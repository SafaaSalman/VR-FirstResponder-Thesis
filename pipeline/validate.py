"""
Output validation module.

Validates the generated protocol tree and knowledge base against
expected schemas and cross-reference integrity.
"""

from __future__ import annotations

import json
import logging
import re
from collections import deque
from dataclasses import dataclass, field
from typing import List

logger = logging.getLogger("pipeline.validate")


@dataclass
class ValidationResult:
    """Collection of validation findings."""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        lines = []
        if self.errors:
            lines.append(f"ERRORS ({len(self.errors)}):")
            for e in self.errors:
                lines.append(f"  ✗ {e}")
        if self.warnings:
            lines.append(f"WARNINGS ({len(self.warnings)}):")
            for w in self.warnings:
                lines.append(f"  ⚠ {w}")
        if self.ok and not self.warnings:
            lines.append("✓ All validations passed.")
        return "\n".join(lines)


# ── Protocol validation ───────────────────────────────────────────────────

def validate_protocol(protocol: dict) -> ValidationResult:
    """Validate a protocol tree JSON for structural correctness."""
    r = ValidationResult()

    # ── Required top-level keys ────────────────────────────────────
    required = ["protocol_id", "title", "initial_step", "steps", "possible_actions"]
    for key in required:
        if key not in protocol:
            r.errors.append(f"Missing required key: '{key}'")

    if r.errors:
        return r  # Can't continue without basics

    steps = protocol.get("steps", [])
    step_ids = {s["id"] for s in steps}
    action_ids = {a["id"] for a in protocol.get("possible_actions", [])}
    constraints = protocol.get("global_constraints", [])

    # ── initial_step ───────────────────────────────────────────────
    if protocol["initial_step"] not in step_ids:
        r.errors.append(f"initial_step '{protocol['initial_step']}' not in steps")

    # ── Step validation ────────────────────────────────────────────
    seen_ids = set()
    terminal_count = 0
    terminal_ids: set[str] = set()

    for s in steps:
        sid = s.get("id", "<missing>")

        # Duplicate check
        if sid in seen_ids:
            r.errors.append(f"Duplicate step id: '{sid}'")
        seen_ids.add(sid)

        # Required fields
        if "description" not in s:
            r.errors.append(f"Step '{sid}' missing description")
        if "type" not in s:
            r.warnings.append(f"Step '{sid}' missing type, defaulting to 'action'")

        # Type-specific checks
        step_type = s.get("type", "action")
        if step_type == "action":
            if not s.get("allowed_next") and not s.get("terminal"):
                r.warnings.append(f"Action step '{sid}' has no allowed_next and is not terminal")
            for nxt in s.get("allowed_next", []):
                if nxt not in step_ids:
                    r.errors.append(f"Step '{sid}' allowed_next references non-existent '{nxt}'")

        elif step_type == "decision":
            conditions = s.get("conditions", [])
            if not conditions:
                r.errors.append(f"Decision step '{sid}' has no conditions")
            for cond in conditions:
                if "if" not in cond or "next" not in cond:
                    r.errors.append(f"Decision '{sid}' has malformed condition: {cond}")
                elif cond["next"] not in step_ids:
                    r.errors.append(f"Decision '{sid}' condition points to non-existent '{cond['next']}'")

        # Terminal
        if s.get("terminal"):
            terminal_count += 1
            terminal_ids.add(sid)

        # Step in possible_actions
        if sid not in action_ids:
            r.warnings.append(f"Step '{sid}' not in possible_actions")

    if terminal_count == 0:
        r.errors.append("No terminal step found — protocol has no endpoint")
    elif terminal_count > 1:
        r.warnings.append(f"Multiple terminal steps ({terminal_count}) — unusual but allowed")

    # ── Constraint validation ──────────────────────────────────────
    for c in constraints:
        if "id" not in c:
            r.errors.append("Constraint missing 'id'")
            continue
        if "forbidden_actions" not in c:
            r.warnings.append(f"Constraint '{c['id']}' has no forbidden_actions")
        for fa in c.get("forbidden_actions", []):
            if fa not in action_ids:
                r.warnings.append(f"Constraint '{c['id']}' forbidden action '{fa}' not in possible_actions")

    # ── Meta-actions ───────────────────────────────────────────────
    for meta in ["ask_question", "request_hint"]:
        if meta not in action_ids:
            r.warnings.append(f"Meta-action '{meta}' missing from possible_actions")

    # ── Reachability (BFS from initial_step) ───────────────────────
    reachable = set()
    _bfs_reachable(protocol["initial_step"], steps, reachable)
    unreachable = step_ids - reachable
    for uid in sorted(unreachable):
        r.warnings.append(f"Step '{uid}' is not reachable from initial_step")

    # ── Cycle detection (DFS) ──────────────────────────────────────
    cycles = _detect_cycles(steps)
    for cycle_path in cycles:
        r.errors.append(
            f"Cycle detected: {' → '.join(cycle_path)}"
        )

    # ── Duplicate-description detection ────────────────────────────
    _check_duplicate_descriptions(steps, r)

    # ── Dead-end reachability: non-terminal steps must eventually
    #    reach a terminal step ──────────────────────────────────────
    if terminal_ids:
        _check_dead_ends(steps, terminal_ids, r)

    return r


# ── Knowledge base validation ─────────────────────────────────────────────

def validate_knowledge_base(kb: dict, protocol: dict) -> ValidationResult:
    """Validate a knowledge base JSON against the protocol tree."""
    r = ValidationResult()

    if "chunks" not in kb:
        r.errors.append("Missing 'chunks' array")
        return r

    step_ids = {s["id"] for s in protocol.get("steps", [])}
    constraint_ids = {c["id"] for c in protocol.get("global_constraints", [])}
    chunks = kb["chunks"]

    if not chunks:
        r.errors.append("Knowledge base has zero chunks")
        return r

    # ── Chunk validation ───────────────────────────────────────────
    seen_chunk_ids = set()
    for chunk in chunks:
        cid = chunk.get("chunk_id", "<missing>")
        if cid in seen_chunk_ids:
            r.errors.append(f"Duplicate chunk_id: '{cid}'")
        seen_chunk_ids.add(cid)

        if not chunk.get("title"):
            r.warnings.append(f"Chunk '{cid}' missing title")
        if not chunk.get("text"):
            r.errors.append(f"Chunk '{cid}' has no text")
        else:
            text = chunk["text"]
            text_len = len(text)

            # Length checks
            if text_len < 100:
                r.warnings.append(
                    f"Chunk '{cid}' text too short ({text_len} chars) — "
                    f"may be too thin for useful retrieval"
                )
            elif text_len > 2000:
                r.warnings.append(
                    f"Chunk '{cid}' text too long ({text_len} chars) — "
                    f"consider splitting for better embedding retrieval"
                )

            # Sentence count check
            sentences = _count_sentences(text)
            if sentences < 2:
                r.warnings.append(
                    f"Chunk '{cid}' has only {sentences} sentence(s) — "
                    f"may lack sufficient context"
                )
            elif sentences > 10:
                r.warnings.append(
                    f"Chunk '{cid}' has {sentences} sentences — "
                    f"consider splitting for focused retrieval"
                )

        # Validate step references
        for sid in chunk.get("related_steps", []):
            if sid not in step_ids:
                r.warnings.append(f"Chunk '{cid}' references non-existent step '{sid}'")

        # Validate constraint references
        for cid_ref in chunk.get("related_constraints", []):
            if cid_ref not in constraint_ids:
                r.warnings.append(f"Chunk '{cid}' references non-existent constraint '{cid_ref}'")

    # ── Near-duplicate chunk detection (word overlap) ──────────────
    _check_chunk_near_duplicates(chunks, r)

    # ── Coverage check ─────────────────────────────────────────────
    covered_steps = set()
    for chunk in chunks:
        covered_steps.update(chunk.get("related_steps", []))

    uncovered = step_ids - covered_steps
    for uid in sorted(uncovered):
        r.warnings.append(f"Step '{uid}' has no KB chunk covering it")

    covered_constraints = set()
    for chunk in chunks:
        covered_constraints.update(chunk.get("related_constraints", []))
    uncovered_constraints = constraint_ids - covered_constraints
    for uid in sorted(uncovered_constraints):
        r.warnings.append(f"Constraint '{uid}' has no dedicated KB chunk")

    # ── protocol_id match ──────────────────────────────────────────
    if kb.get("protocol_id") != protocol.get("protocol_id"):
        r.warnings.append(
            f"KB protocol_id '{kb.get('protocol_id')}' != "
            f"protocol '{protocol.get('protocol_id')}'"
        )

    return r


# ── Helpers ────────────────────────────────────────────────────────────────

def _bfs_reachable(start: str, steps: list[dict], visited: set):
    """BFS to find all reachable step IDs from *start*."""
    step_map = {s["id"]: s for s in steps}
    queue: deque[str] = deque([start])
    while queue:
        current = queue.popleft()
        if current in visited or current not in step_map:
            continue
        visited.add(current)
        s = step_map[current]
        for nxt in s.get("allowed_next", []):
            queue.append(nxt)
        for cond in s.get("conditions", []):
            if "next" in cond:
                queue.append(cond["next"])


def _detect_cycles(steps: list[dict]) -> list[list[str]]:
    """DFS-based cycle detection.  Returns list of cycle paths found."""
    step_map = {s["id"]: s for s in steps}
    all_ids = set(step_map.keys())

    WHITE, GRAY, BLACK = 0, 1, 2
    colour: dict[str, int] = {sid: WHITE for sid in all_ids}
    parent: dict[str, str | None] = {sid: None for sid in all_ids}
    cycles: list[list[str]] = []

    def _successors(sid: str) -> list[str]:
        s = step_map[sid]
        nexts = list(s.get("allowed_next", []))
        for cond in s.get("conditions", []):
            if "next" in cond:
                nexts.append(cond["next"])
        return [n for n in nexts if n in all_ids]

    def _dfs(node: str):
        colour[node] = GRAY
        for nxt in _successors(node):
            if colour[nxt] == GRAY:
                # Back-edge → cycle.  Reconstruct the path.
                path = [nxt]
                cur = node
                while cur != nxt:
                    path.append(cur)
                    cur = parent[cur]  # type: ignore[arg-type]
                    if cur is None:
                        break
                path.append(nxt)
                path.reverse()
                cycles.append(path)
            elif colour[nxt] == WHITE:
                parent[nxt] = node
                _dfs(nxt)
        colour[node] = BLACK

    for sid in all_ids:
        if colour[sid] == WHITE:
            _dfs(sid)

    return cycles


def _check_duplicate_descriptions(steps: list[dict], r: ValidationResult):
    """Flag steps that share identical descriptions (common LLM artifact)."""
    desc_map: dict[str, list[str]] = {}
    for s in steps:
        desc = s.get("description", "")
        key = desc.strip().lower()
        if not key:
            continue
        desc_map.setdefault(key, []).append(s.get("id", "<missing>"))

    for _desc, sids in desc_map.items():
        if len(sids) > 1:
            pairs = ", ".join(f"'{s}'" for s in sids)
            r.warnings.append(
                f"Steps {pairs} have identical descriptions — "
                f"possible LLM duplication artifact"
            )


def _check_dead_ends(
    steps: list[dict],
    terminal_ids: set[str],
    r: ValidationResult,
):
    """Verify every non-terminal step can eventually reach a terminal step.

    A non-terminal step with empty ``allowed_next`` and no conditions is a
    dead-end.  Even if it has successors, it must be possible to reach at
    least one terminal step from it.
    """
    step_map = {s["id"]: s for s in steps}

    def _successors(sid: str) -> list[str]:
        s = step_map[sid]
        nexts = list(s.get("allowed_next", []))
        for cond in s.get("conditions", []):
            if "next" in cond:
                nexts.append(cond["next"])
        return [n for n in nexts if n in step_map]

    for sid, s in step_map.items():
        if sid in terminal_ids:
            continue

        # BFS from this step looking for any terminal
        visited: set[str] = set()
        queue: deque[str] = deque([sid])
        found_terminal = False
        while queue:
            cur = queue.popleft()
            if cur in visited:
                continue
            visited.add(cur)
            if cur in terminal_ids:
                found_terminal = True
                break
            for nxt in _successors(cur):
                if nxt not in visited:
                    queue.append(nxt)

        if not found_terminal:
            r.errors.append(
                f"Step '{sid}' cannot reach any terminal step — dead-end path"
            )


def _count_sentences(text: str) -> int:
    """Rough sentence count using period/question/exclamation terminators."""
    # Split on sentence-ending punctuation followed by whitespace or end-of-string
    parts = re.split(r'[.!?]+(?:\s|$)', text.strip())
    # Filter out empty fragments
    return len([p for p in parts if p.strip()])


def _word_set(text: str) -> set[str]:
    """Lower-cased word set for overlap comparison."""
    return set(re.findall(r'[a-z0-9]+', text.lower()))


def _check_chunk_near_duplicates(chunks: list[dict], r: ValidationResult):
    """Warn if any two chunks have >90% word overlap (near-duplicates)."""
    cached: list[tuple[str, set[str]]] = []
    for chunk in chunks:
        cid = chunk.get("chunk_id", "<missing>")
        text = chunk.get("text", "")
        cached.append((cid, _word_set(text)))

    for i in range(len(cached)):
        cid_a, words_a = cached[i]
        if not words_a:
            continue
        for j in range(i + 1, len(cached)):
            cid_b, words_b = cached[j]
            if not words_b:
                continue
            intersection = len(words_a & words_b)
            smaller = min(len(words_a), len(words_b))
            if smaller == 0:
                continue
            overlap_ratio = intersection / smaller
            if overlap_ratio > 0.90:
                r.warnings.append(
                    f"Chunks '{cid_a}' and '{cid_b}' have {overlap_ratio:.0%} "
                    f"word overlap — possible near-duplicate"
                )
