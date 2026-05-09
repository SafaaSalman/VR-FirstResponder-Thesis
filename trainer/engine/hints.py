"""
Multi-level hint engine.

Hint levels:
 1 – Gentle nudge (vague direction)
 2 – Direct guidance (names the step category)
 3 – Explicit instruction (states the exact next step)

Level auto-escalates on repeated requests.
"""

from __future__ import annotations

from typing import Optional

from .. import config
from .state import ScenarioState


class HintEngine:
    """Generates hints from the rule engine state (no LLM needed)."""

    def __init__(self, protocol: dict, state: ScenarioState) -> None:
        self.protocol = protocol
        self.state = state
        self._step_index = {s["id"]: s for s in protocol["steps"]}

    def get_hint(self, level: Optional[int] = None) -> dict:
        """
        Return a hint dict with ``level``, ``text``, and ``related_steps``.
        If *level* is ``None``, use the trainee's auto-escalating level.
        """
        if level is None:
            level = self.state.progress.current_hint_level

        # Clamp
        level = max(1, min(level, config.MAX_HINT_LEVEL))

        current = self.state.progress.current_step
        step = self._step_index.get(current) if current else None

        if step is None:
            return {
                "level": level,
                "text": "There are no more steps to complete.",
                "related_steps": [],
            }

        phase = step.get("phase", "")
        desc = step.get("description", "")

        if level == 1:
            text = self._gentle_hint(phase, step)
        elif level == 2:
            text = self._direct_hint(step)
        else:
            text = self._explicit_hint(step, desc)

        # Auto-escalate for next request
        self.state.progress.hint_requests += 1
        if self.state.progress.current_hint_level < config.MAX_HINT_LEVEL:
            self.state.progress.current_hint_level += 1

        return {
            "level": level,
            "text": text,
            "related_steps": [current],
        }

    # ── Hint generators ────────────────────────────────────────────────────

    @staticmethod
    def _gentle_hint(phase: str, step: dict) -> str:
        hints = {
            "immediate_response": (
                "Think about what you should do to protect yourself "
                "right now."
            ),
            "assessment": (
                "Before moving, you may want to check whether it is "
                "actually safe around you."
            ),
            "route_planning": (
                "Consider whether your planned evacuation path is "
                "safe to use."
            ),
            "assistance": (
                "Is there anyone nearby who might need your help?"
            ),
            "evacuation": (
                "It may be time to start moving towards an exit."
            ),
            "assembly": (
                "Think about where you should go once you are outside."
            ),
            "accountability": (
                "After gathering, there is an important step to make "
                "sure everyone is safe."
            ),
            "reporting": (
                "Emergency responders will need information from you."
            ),
            "post_evacuation": (
                "You are outside now. What should you be alert for?"
            ),
        }
        return hints.get(
            phase,
            "Think carefully about the correct next action.",
        )

    @staticmethod
    def _direct_hint(step: dict) -> str:
        phase_labels = {
            "immediate_response": "immediate safety action",
            "assessment": "hazard assessment",
            "route_planning": "evacuation route verification",
            "assistance": "checking for people who need help",
            "evacuation": "evacuation procedure",
            "assembly": "moving to the assembly point",
            "accountability": "personnel accountability",
            "reporting": "status reporting",
            "post_evacuation": "post-evacuation monitoring",
        }
        phase = step.get("phase", "")
        label = phase_labels.get(phase, "the next procedure step")
        return (
            f"The procedure requires {label} at this point."
        )

    @staticmethod
    def _explicit_hint(step: dict, description: str) -> str:
        return (
            f"The next correct step is: {description}"
        )
