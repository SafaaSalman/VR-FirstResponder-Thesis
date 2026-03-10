"""
Rule engine – deterministic protocol compliance checker.

Responsibilities:
 - Decide what actions are valid given the current state
 - Detect forbidden / skipped / out-of-order actions
 - Apply state effects when a valid step is completed
 - Never uses the LLM – pure logic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .state import ScenarioState


# ── Data structures ────────────────────────────────────────────────────────


@dataclass
class ActionResult:
    """Structured output of evaluating a single trainee action."""

    action_id: str
    matched_step: Optional[str] = None
    validity: str = "invalid"  # valid | invalid | meta
    violations: List[str] = field(default_factory=list)
    skipped_steps: List[str] = field(default_factory=list)
    critical_error: bool = False
    next_expected_step: Optional[str] = None
    reason: str = ""
    state_updates: Dict[str, Any] = field(default_factory=dict)
    branch_result: Optional[str] = None
    constraint_violated: Optional[str] = None
    step_description: str = ""
    phase: str = ""

    def to_dict(self) -> dict:
        return {
            "action_id": self.action_id,
            "matched_step": self.matched_step,
            "validity": self.validity,
            "violations": self.violations,
            "skipped_steps": self.skipped_steps,
            "critical_error": self.critical_error,
            "next_expected_step": self.next_expected_step,
            "reason": self.reason,
            "state_updates": self.state_updates,
            "branch_result": self.branch_result,
            "constraint_violated": self.constraint_violated,
            "step_description": self.step_description,
            "phase": self.phase,
        }


# ── Rule Engine ────────────────────────────────────────────────────────────


class RuleEngine:
    """Protocol compliance checker operating on a ScenarioState."""

    def __init__(self, protocol: dict, state: ScenarioState) -> None:
        self.protocol = protocol
        self.state = state
        self._step_index: Dict[str, dict] = {
            s["id"]: s for s in protocol["steps"]
        }
        self._step_order: List[str] = []
        self._build_step_order()

    # ── Graph helpers ──────────────────────────────────────────────────────

    def _build_step_order(self) -> None:
        """Topological traversal from the initial step."""
        visited: set[str] = set()

        def _dfs(step_id: str) -> None:
            if step_id in visited or step_id not in self._step_index:
                return
            visited.add(step_id)
            self._step_order.append(step_id)
            step = self._step_index[step_id]
            # Decision branches
            for cond in step.get("conditions", []):
                _dfs(cond["next"])
            # Sequential next
            for nxt in step.get("allowed_next", []):
                _dfs(nxt)

        initial = self.protocol.get("initial_step")
        if initial:
            _dfs(initial)

    def get_all_steps_ordered(self) -> List[str]:
        return list(self._step_order)

    def get_critical_steps(self) -> List[str]:
        return [
            sid
            for sid, s in self._step_index.items()
            if s.get("critical", False)
        ]

    # ── Condition / effect evaluation ──────────────────────────────────────

    def evaluate_condition(self, condition_str: str) -> bool:
        """Evaluate ``'variable == value'`` against the live state."""
        state = self.state.get_state()
        parts = condition_str.strip().split()
        if len(parts) != 3:
            return False
        var, op, expected = parts

        actual = state.get(var)

        # Coerce the expected-value string
        if expected.lower() == "true":
            expected = True
        elif expected.lower() == "false":
            expected = False
        else:
            try:
                expected = int(expected)
            except ValueError:
                pass  # keep as str

        if op == "==":
            return actual == expected
        if op == "!=":
            return actual != expected
        if op == ">" and actual is not None:
            return actual > expected
        if op == "<" and actual is not None:
            return actual < expected
        return False

    # ── Constraint checks ──────────────────────────────────────────────────

    def check_global_constraints(self, action_id: str) -> List[dict]:
        violations = []
        for c in self.protocol.get("global_constraints", []):
            if action_id in c.get("forbidden_actions", []):
                violations.append(
                    {
                        "constraint_id": c["id"],
                        "description": c["description"],
                        "critical": c.get("critical", False),
                    }
                )
        return violations

    # ── Step lookup / graph search ─────────────────────────────────────────

    def find_step(self, step_id: str) -> Optional[dict]:
        return self._step_index.get(step_id)

    def get_expected_next_steps(self) -> List[str]:
        """Return the step(s) the trainee should perform right now."""
        current = self.state.progress.current_step
        if current is None:
            return []
        return [current]

    def _find_skipped_between(
        self, from_step: str, to_step: str
    ) -> List[str]:
        """BFS from *from_step* to *to_step*; return intermediate nodes."""
        if from_step == to_step:
            return []
        visited: set[str] = set()
        queue: list[tuple[str, list[str]]] = [(from_step, [])]

        while queue:
            node, path = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            step = self._step_index.get(node)
            if step is None:
                continue

            successors: list[str] = []
            for cond in step.get("conditions", []):
                successors.append(cond["next"])
            successors.extend(step.get("allowed_next", []))

            for s in successors:
                new_path = path + [node]
                if s == to_step:
                    # Don't include from_step itself
                    return [
                        n
                        for n in new_path
                        if n != from_step
                        and n not in self.state.progress.completed_steps
                    ]
                if s not in visited:
                    queue.append((s, new_path))
        return []

    def evaluate_decision(self, step: dict) -> Optional[str]:
        """Pick the branch of a decision step using the live state."""
        for cond in step.get("conditions", []):
            if self.evaluate_condition(cond["if"]):
                return cond["next"]
        # Fallback: first branch
        if step.get("conditions"):
            return step["conditions"][0]["next"]
        return None

    # ── Main evaluation ────────────────────────────────────────────────────

    def evaluate_action(self, action_id: str) -> ActionResult:
        """
        Evaluate a trainee action against the protocol.

        Returns an ``ActionResult`` with validity, violations, skipped
        steps, and the next expected step.
        """
        result = ActionResult(action_id=action_id)

        # ── Meta actions (not protocol steps) ──────────────────────────────
        if action_id in ("ask_question", "request_hint"):
            result.validity = "meta"
            result.reason = "Meta action"
            result.next_expected_step = self.state.progress.current_step
            return result

        # ── 1. Global constraints ──────────────────────────────────────────
        constraint_hits = self.check_global_constraints(action_id)
        if constraint_hits:
            hit = constraint_hits[0]
            result.validity = "invalid"
            result.violations = [
                f"forbidden_action_{action_id}"
            ]
            result.critical_error = hit["critical"]
            result.constraint_violated = hit["constraint_id"]
            result.reason = hit["description"]
            result.next_expected_step = self.state.progress.current_step
            self.state.record_violation(
                {
                    "type": "global_constraint",
                    "action": action_id,
                    "constraint": hit["constraint_id"],
                    "critical": hit["critical"],
                }
            )
            return result

        # ── 2. Locate protocol step ────────────────────────────────────────
        step = self.find_step(action_id)
        if step is None:
            result.validity = "invalid"
            result.reason = (
                f"'{action_id}' is not a recognized protocol action."
            )
            result.next_expected_step = self.state.progress.current_step
            return result

        result.matched_step = step["id"]
        result.step_description = step.get("description", "")
        result.phase = step.get("phase", "")

        # ── 3. Already completed? ──────────────────────────────────────────
        if action_id in self.state.progress.completed_steps:
            result.validity = "invalid"
            result.reason = f"Step '{action_id}' has already been completed."
            result.next_expected_step = self.state.progress.current_step
            return result

        # ── 4. Preconditions ───────────────────────────────────────────────
        preconditions_met = all(
            self.evaluate_condition(pc)
            for pc in step.get("preconditions", [])
        )

        current_step = self.state.progress.current_step
        is_expected = action_id == current_step

        # ── 5. Skipped-step detection ──────────────────────────────────────
        skipped: List[str] = []
        if not is_expected and current_step:
            skipped = self._find_skipped_between(current_step, action_id)

        # ── 6. Validity decision ───────────────────────────────────────────
        if is_expected and preconditions_met:
            result.validity = "valid"
            result.reason = "Correct action."
        elif is_expected and not preconditions_met:
            result.validity = "invalid"
            failed = [
                pc
                for pc in step.get("preconditions", [])
                if not self.evaluate_condition(pc)
            ]
            result.violations = [
                f"precondition_not_met: {pc}" for pc in failed
            ]
            result.reason = (
                "Conditions for this step are not yet met."
            )
        elif skipped:
            result.validity = "invalid"
            result.skipped_steps = skipped
            result.reason = f"Steps skipped: {', '.join(skipped)}"
            crit_skipped = [
                s
                for s in skipped
                if self._step_index.get(s, {}).get("critical", False)
            ]
            if crit_skipped:
                result.critical_error = True
                result.violations.append(
                    f"critical_steps_skipped: {', '.join(crit_skipped)}"
                )
            self.state.record_violation(
                {
                    "type": "step_skip",
                    "action": action_id,
                    "skipped": skipped,
                    "critical": result.critical_error,
                }
            )
        else:
            result.validity = "invalid"
            result.reason = "This action is not permitted right now."

        result.next_expected_step = self.state.progress.current_step

        # ── 7. Apply on valid ──────────────────────────────────────────────
        if result.validity == "valid":
            # Effects
            for effect in step.get("effects", []):
                self.state.apply_effect(effect)
                parts = effect.split(" = ", 1)
                if len(parts) == 2:
                    result.state_updates[parts[0].strip()] = parts[1].strip()

            self.state.mark_step_complete(action_id)

            # Advance pointer
            if step.get("type") == "decision":
                branch = self.evaluate_decision(step)
                result.branch_result = branch
                self.state.advance_step(branch)
                result.next_expected_step = branch
            elif step.get("terminal"):
                self.state.advance_step(None)
                result.next_expected_step = None
            elif step.get("allowed_next"):
                nxt = step["allowed_next"][0]
                self.state.advance_step(nxt)
                result.next_expected_step = nxt
            else:
                self.state.advance_step(None)
                result.next_expected_step = None

        return result
