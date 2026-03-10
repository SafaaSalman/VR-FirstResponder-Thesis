"""
Deterministic scoring engine.

Computes five dimensions:
 1. Sequence adherence   – correct step ordering
 2. Critical compliance  – mandatory safety steps completed
 3. Branch correctness   – right path given the scenario state
 4. Hazard awareness     – acknowledged route safety, aftershocks, etc.
 5. Completion quality   – finished all required end-steps

Each dimension is 0-100.  Overall is the weighted average (weights in config).
"""

from __future__ import annotations

from typing import Dict, List

from trainer import config
from .state import ScenarioState


class ScoringEngine:
    """Deterministic, rule-based scoring."""

    def __init__(self, protocol: dict, state: ScenarioState) -> None:
        self.protocol = protocol
        self.state = state
        self._step_index = {s["id"]: s for s in protocol["steps"]}

        # Pre-compute reference lists
        self._critical_steps = [
            s["id"] for s in protocol["steps"] if s.get("critical")
        ]
        self._all_steps = [s["id"] for s in protocol["steps"]]
        self._terminal_steps = [
            s["id"] for s in protocol["steps"] if s.get("terminal")
        ]
        # Steps related to hazard awareness
        self._hazard_steps = [
            s["id"]
            for s in protocol["steps"]
            if s.get("phase") in (
                "assessment", "route_planning", "post_evacuation"
            )
        ]
        # End-phase steps (assembly onward)
        self._completion_steps = [
            s["id"]
            for s in protocol["steps"]
            if s.get("phase") in (
                "assembly", "accountability", "reporting", "post_evacuation"
            )
        ]

    # ── Penalty catalogue ──────────────────────────────────────────────────

    PENALTIES: Dict[str, Dict[str, int]] = {
        "forbidden_action_use_elevator": {
            "critical_compliance": -30,
            "hazard_awareness": -20,
        },
        "forbidden_action_re_enter_building": {
            "critical_compliance": -30,
            "hazard_awareness": -20,
        },
        "forbidden_action_run_outside_during_shaking": {
            "critical_compliance": -20,
            "sequence_adherence": -15,
        },
    }

    # ── Scoring ────────────────────────────────────────────────────────────

    def compute(self) -> Dict[str, object]:
        """Return the full score dict including per-dimension and overall."""
        completed = set(self.state.progress.completed_steps)
        violations = self.state.progress.violations

        # 1. Sequence adherence
        seq = self._score_sequence_adherence(completed)

        # 2. Critical compliance
        crit = self._score_critical_compliance(completed, violations)

        # 3. Branch correctness
        branch = self._score_branch_correctness(completed)

        # 4. Hazard awareness
        hazard = self._score_hazard_awareness(completed, violations)

        # 5. Completion quality
        comp = self._score_completion_quality(completed)

        # Apply violation penalties
        penalties = self._compute_penalties(violations)
        seq = max(0, seq + penalties.get("sequence_adherence", 0))
        crit = max(0, crit + penalties.get("critical_compliance", 0))
        hazard = max(0, hazard + penalties.get("hazard_awareness", 0))

        scores = {
            "sequence_adherence": round(seq),
            "critical_compliance": round(crit),
            "branch_correctness": round(branch),
            "hazard_awareness": round(hazard),
            "completion_quality": round(comp),
        }

        w = config.SCORE_WEIGHTS
        overall = sum(scores[k] * w[k] for k in w)
        scores["overall"] = round(overall)

        # Penalty details for debrief
        penalty_details = self._get_penalty_details(violations)

        return {"scores": scores, "penalties": penalty_details}

    # ── Dimension implementations ──────────────────────────────────────────

    def _score_sequence_adherence(self, completed: set) -> float:
        """How well did the trainee follow the correct step order?"""
        if not self.state.progress.actions_taken:
            return 0

        ordered_completed = [
            a["action"]
            for a in self.state.progress.actions_taken
            if a["result"].get("validity") == "valid"
        ]
        if not ordered_completed:
            return 0

        # Check if completed steps appear in protocol order
        expected_order = [
            s for s in self._all_steps if s in completed
        ]
        matches = 0
        for i, step_id in enumerate(ordered_completed):
            if i < len(expected_order) and step_id == expected_order[i]:
                matches += 1

        return (matches / max(len(expected_order), 1)) * 100

    def _score_critical_compliance(
        self, completed: set, violations: list
    ) -> float:
        """Were all critical / mandatory steps done?"""
        if not self._critical_steps:
            return 100
        done = sum(1 for s in self._critical_steps if s in completed)
        base = (done / len(self._critical_steps)) * 100
        # Extra penalty for constraint violations
        constraint_viols = [
            v for v in violations if v.get("type") == "global_constraint"
        ]
        base -= len(constraint_viols) * 15
        return max(0, base)

    def _score_branch_correctness(self, completed: set) -> float:
        """Did the trainee take the correct branch for the scenario?"""
        decision_steps = [
            s for s in self.protocol["steps"] if s["type"] == "decision"
        ]
        if not decision_steps:
            return 100
        correct = 0
        total = 0
        state = self.state.get_state()
        for ds in decision_steps:
            if ds["id"] not in completed:
                continue
            total += 1
            # Find which branch they should have taken
            for cond in ds.get("conditions", []):
                cond_str = cond["if"]
                parts = cond_str.strip().split()
                if len(parts) == 3:
                    var, op, val = parts
                    if val.lower() == "true":
                        val = True
                    elif val.lower() == "false":
                        val = False
                    actual = state.get(var)
                    if (op == "==" and actual == val) or (
                        op == "!=" and actual != val
                    ):
                        # This was the correct branch
                        if cond["next"] in completed:
                            correct += 1
                        break
        return (correct / max(total, 1)) * 100

    def _score_hazard_awareness(
        self, completed: set, violations: list
    ) -> float:
        """Did the trainee attend to hazard-related steps?"""
        if not self._hazard_steps:
            return 100
        done = sum(1 for s in self._hazard_steps if s in completed)
        return (done / len(self._hazard_steps)) * 100

    def _score_completion_quality(self, completed: set) -> float:
        """Did the trainee finish all end-phase steps?"""
        if not self._completion_steps:
            return 100
        done = sum(1 for s in self._completion_steps if s in completed)
        return (done / len(self._completion_steps)) * 100

    # ── Penalty helpers ────────────────────────────────────────────────────

    def _compute_penalties(self, violations: list) -> Dict[str, int]:
        totals: Dict[str, int] = {}
        for v in violations:
            key = f"forbidden_action_{v.get('action', '')}"
            if key in self.PENALTIES:
                for dim, penalty in self.PENALTIES[key].items():
                    totals[dim] = totals.get(dim, 0) + penalty
        return totals

    def _get_penalty_details(self, violations: list) -> List[dict]:
        details = []
        for v in violations:
            if v.get("type") == "global_constraint":
                details.append(
                    {
                        "type": "major",
                        "description": f"Forbidden action: {v.get('action')}",
                        "constraint": v.get("constraint"),
                    }
                )
            elif v.get("type") == "step_skip":
                severity = "major" if v.get("critical") else "medium"
                details.append(
                    {
                        "type": severity,
                        "description": (
                            f"Skipped steps: {', '.join(v.get('skipped', []))}"
                        ),
                    }
                )
        return details
