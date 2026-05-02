"""
Scenario state management for the training engine.

Tracks:
 - scenario world-state (shaking, damage, exits, etc.)
 - trainee progress (completed steps, violations, actions)
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TraineeProgress:
    """Book-keeping for the trainee's journey through the protocol."""

    completed_steps: List[str] = field(default_factory=list)
    current_step: Optional[str] = None
    violations: List[Dict[str, Any]] = field(default_factory=list)
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    hint_requests: int = 0
    current_hint_level: int = 1
    is_complete: bool = False


class ScenarioState:
    """Manages the mutable scenario state and trainee progress."""

    def __init__(self, scenario: dict, protocol: dict) -> None:
        self.scenario_id: str = scenario["scenario_id"]
        self.scenario_name: str = scenario["name"]
        self.scenario_description: str = scenario["description"]
        self.narrative: dict = scenario.get("narrative_details", {})
        self.difficulty: str = scenario.get("difficulty", "intermediate")

        # Deep-copy so the original JSON stays untouched
        self.state: Dict[str, Any] = copy.deepcopy(scenario["initial_state"])
        self.protocol: dict = protocol

        self.progress = TraineeProgress(
            current_step=protocol.get("initial_step")
        )

    # ── State access ───────────────────────────────────────────────────────

    def get_state(self) -> Dict[str, Any]:
        """Return a snapshot of the current world-state."""
        return copy.deepcopy(self.state)

    def update_state(self, key: str, value: Any) -> None:
        self.state[key] = value

    def apply_effect(self, effect_str: str) -> None:
        """Parse and apply ``'variable = value'`` effect strings."""
        if " = " not in effect_str:
            return
        var, val = effect_str.split(" = ", 1)
        var = var.strip()
        val = val.strip()

        # Type coercion
        if val.lower() == "true":
            val = True
        elif val.lower() == "false":
            val = False
        else:
            try:
                val = int(val)
            except ValueError:
                try:
                    val = float(val)
                except ValueError:
                    pass  # keep as string

        self.state[var] = val

    # ── Progress tracking ──────────────────────────────────────────────────

    def mark_step_complete(self, step_id: str) -> None:
        if step_id not in self.progress.completed_steps:
            self.progress.completed_steps.append(step_id)

    def record_action(self, action_id: str, result: dict) -> None:
        self.progress.actions_taken.append(
            {
                "action": action_id,
                "result": result,
                "step_number": len(self.progress.actions_taken) + 1,
            }
        )

    def record_violation(self, violation: dict) -> None:
        self.progress.violations.append(violation)

    def advance_step(self, next_step: Optional[str]) -> None:
        self.progress.current_step = next_step
        if next_step is None:
            self.progress.is_complete = True

    # ── Summaries ──────────────────────────────────────────────────────────

    def get_summary(self) -> dict:
        """Compact summary useful for LLM context and logging."""
        return {
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "difficulty": self.difficulty,
            "current_step": self.progress.current_step,
            "completed_steps": list(self.progress.completed_steps),
            "violations_count": len(self.progress.violations),
            "actions_count": len(self.progress.actions_taken),
            "is_complete": self.progress.is_complete,
            "state": self.get_state(),
        }

    def get_state_description(self) -> str:
        """Human-readable state summary for the LLM prompt."""
        lines = []
        for key, val in self.state.items():
            label = key.replace("_", " ").title()
            lines.append(f"  - {label}: {val}")
        return "\n".join(lines)

    def get_dynamic_narrative(self) -> dict:
        """Build a phase-aware narrative that evolves with the world state.

        Returns a dict with 'location', 'environment', 'people',
        and 'phase_context' — replacing the static initial narrative
        for LLM context.
        """
        s = self.state
        base = dict(self.narrative)  # start from static narrative
        phase = self._current_phase()

        # ── Location shifts based on progress ──────────────────────
        if s.get("assembly_point_reached"):
            base["location"] = (
                f"Assembly point outside {self.narrative.get('location', 'the building')}. "
                f"You are outdoors, at a safe distance from the structure."
            )
        elif not s.get("inside_building", True):
            base["location"] = (
                f"Just outside {self.narrative.get('location', 'the building')}. "
                f"You are in the process of moving to the assembly point."
            )

        # ── Environment evolves ────────────────────────────────────
        env_parts = []
        if s.get("shaking_active"):
            env_parts.append(
                "The ground is shaking violently. Objects are falling, "
                "lights swaying, and people are screaming."
            )
        else:
            env_parts.append("The shaking has stopped.")
            damage = s.get("building_damage", "light")
            if damage == "light":
                env_parts.append(
                    "Minor cracks in the ceiling, some items on the floor, "
                    "but the structure appears stable."
                )
            elif damage == "moderate":
                env_parts.append(
                    "Visible cracks in walls, debris on the floor, "
                    "some ceiling tiles fallen.  The structure may be "
                    "compromised."
                )
            else:
                env_parts.append(
                    "Severe structural damage — cracked walls, collapsed "
                    "ceiling sections, heavy debris.  The building is "
                    "clearly unsafe."
                )

        if s.get("smoke_present"):
            env_parts.append("There is a smell of smoke in the air.")
        if s.get("assembly_point_reached"):
            env_parts.append(
                "You are at the outdoor assembly area.  The building "
                "stands behind you; fresh air, open sky above."
            )
        if s.get("aftershock_risk"):
            env_parts.append(
                "Occasional rumbles hint at possible aftershocks."
            )

        base["environment"] = " ".join(env_parts)

        # ── People description evolves ─────────────────────────────
        if s.get("assembly_point_reached"):
            count = s.get("occupant_count", "many")
            headcount = "accounted for" if s.get("headcount_completed") else "gathering"
            base["people_nearby"] = (
                f"Approximately {count} evacuees are {headcount} "
                f"at the assembly point, some anxious, some helping "
                f"each other."
            )

        # ── Phase context (tells the LLM where we are) ────────────
        base["phase_context"] = phase
        base["current_step"] = self.progress.current_step

        return base

    def _current_phase(self) -> str:
        """Return a human-readable phase description."""
        step = self.progress.current_step
        if not step:
            return "post_completion"
        for s in self.protocol.get("steps", []):
            if s["id"] == step:
                return s.get("phase", "unknown")
        return "unknown"
