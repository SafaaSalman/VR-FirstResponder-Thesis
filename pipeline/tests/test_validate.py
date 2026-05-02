"""Tests for protocol and knowledge base validation logic."""

from __future__ import annotations

import pytest

from pipeline.validate import (
    validate_protocol,
    validate_knowledge_base,
    _bfs_reachable,
    _detect_cycles,
    _count_sentences,
    _word_set,
)


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures: minimal valid protocol and KB
# ═══════════════════════════════════════════════════════════════════════════


def _valid_protocol() -> dict:
    """Minimal valid protocol with 3 steps and 1 constraint."""
    return {
        "protocol_id": "test_protocol_v1",
        "title": "Test Protocol",
        "description": "Testing protocol.",
        "initial_step": "step_assess",
        "roles": ["responder"],
        "steps": [
            {
                "id": "step_assess",
                "description": "Assess the situation.",
                "type": "action",
                "allowed_next": ["step_decide"],
            },
            {
                "id": "step_decide",
                "description": "Decide on next action.",
                "type": "decision",
                "conditions": [
                    {"if": "safe", "next": "step_complete"},
                    {"if": "unsafe", "next": "step_complete"},
                ],
            },
            {
                "id": "step_complete",
                "description": "Mark protocol complete.",
                "type": "action",
                "terminal": True,
                "allowed_next": [],
            },
        ],
        "possible_actions": [
            {"id": "step_assess", "description": "Assess"},
            {"id": "step_decide", "description": "Decide"},
            {"id": "step_complete", "description": "Complete"},
            {"id": "ask_question", "description": "Ask question"},
            {"id": "request_hint", "description": "Request hint"},
        ],
        "global_constraints": [
            {
                "id": "no_running",
                "description": "Do not run.",
                "forbidden_actions": ["step_assess"],
            }
        ],
    }


def _valid_kb(protocol: dict | None = None) -> dict:
    """Minimal valid KB matching the test protocol."""
    proto = protocol or _valid_protocol()
    pid = proto["protocol_id"]
    step_ids = [s["id"] for s in proto["steps"]]
    constraint_ids = [c["id"] for c in proto.get("global_constraints", [])]

    chunks = []
    for i, sid in enumerate(step_ids, 1):
        chunks.append({
            "chunk_id": f"kb_{i:03d}",
            "title": f"Chunk for {sid}",
            "text": (
                f"This chunk describes the procedure for {sid}. "
                "It includes detailed instructions that must be followed carefully. "
                "The responder should verify conditions before proceeding."
            ),
            "related_steps": [sid],
            "related_constraints": constraint_ids[:1] if i == 1 else [],
            "tags": ["procedure"],
        })
    return {
        "protocol_id": pid,
        "description": "Test knowledge base.",
        "chunks": chunks,
    }


# ═══════════════════════════════════════════════════════════════════════════
# validate_protocol — valid input
# ═══════════════════════════════════════════════════════════════════════════


class TestValidateProtocolValid:
    """A well-formed protocol should pass with no errors."""

    def test_no_errors(self):
        r = validate_protocol(_valid_protocol())
        assert r.ok, f"Unexpected errors: {r.errors}"

    def test_has_no_critical_warnings(self):
        r = validate_protocol(_valid_protocol())
        # May have some informational warnings, but no "not reachable" type
        for w in r.warnings:
            assert "not reachable" not in w.lower()


# ═══════════════════════════════════════════════════════════════════════════
# validate_protocol — missing keys
# ═══════════════════════════════════════════════════════════════════════════


class TestValidateProtocolMissingKeys:
    """Missing top-level keys must produce errors."""

    @pytest.mark.parametrize("key", [
        "protocol_id", "title", "initial_step", "steps", "possible_actions",
    ])
    def test_missing_required_key(self, key):
        proto = _valid_protocol()
        del proto[key]
        r = validate_protocol(proto)
        assert not r.ok
        assert any(key in e for e in r.errors)


# ═══════════════════════════════════════════════════════════════════════════
# validate_protocol — broken references
# ═══════════════════════════════════════════════════════════════════════════


class TestValidateProtocolBrokenRefs:
    """Step references pointing to non-existent IDs must be flagged."""

    def test_bad_allowed_next(self):
        proto = _valid_protocol()
        proto["steps"][0]["allowed_next"] = ["nonexistent_step"]
        r = validate_protocol(proto)
        assert not r.ok
        assert any("nonexistent_step" in e for e in r.errors)

    def test_bad_decision_condition_next(self):
        proto = _valid_protocol()
        proto["steps"][1]["conditions"][0]["next"] = "ghost_step"
        r = validate_protocol(proto)
        assert not r.ok
        assert any("ghost_step" in e for e in r.errors)

    def test_bad_initial_step(self):
        proto = _valid_protocol()
        proto["initial_step"] = "does_not_exist"
        r = validate_protocol(proto)
        assert not r.ok
        assert any("does_not_exist" in e for e in r.errors)


# ═══════════════════════════════════════════════════════════════════════════
# validate_protocol — cycle detection
# ═══════════════════════════════════════════════════════════════════════════


class TestCycleDetection:
    """Cycle detection via DFS."""

    def test_no_cycle_in_valid_protocol(self):
        cycles = _detect_cycles(_valid_protocol()["steps"])
        assert cycles == []

    def test_simple_cycle(self):
        """A → B → A should be detected."""
        steps = [
            {"id": "a", "allowed_next": ["b"]},
            {"id": "b", "allowed_next": ["a"]},
        ]
        cycles = _detect_cycles(steps)
        assert len(cycles) >= 1
        # The cycle path should contain both a and b
        flat = [sid for c in cycles for sid in c]
        assert "a" in flat
        assert "b" in flat

    def test_longer_cycle(self):
        """A → B → C → A should be detected."""
        steps = [
            {"id": "a", "allowed_next": ["b"]},
            {"id": "b", "allowed_next": ["c"]},
            {"id": "c", "allowed_next": ["a"]},
        ]
        cycles = _detect_cycles(steps)
        assert len(cycles) >= 1

    def test_cycle_via_decision_conditions(self):
        """Cycles through decision conditions should also be detected."""
        steps = [
            {"id": "a", "allowed_next": [], "conditions": [{"if": "x", "next": "b"}]},
            {"id": "b", "allowed_next": [], "conditions": [{"if": "y", "next": "a"}]},
        ]
        cycles = _detect_cycles(steps)
        assert len(cycles) >= 1

    def test_cycle_reported_in_validate_protocol(self):
        """Full validation should report cycle as an ERROR."""
        proto = _valid_protocol()
        # Create A→B→A cycle
        proto["steps"][0]["allowed_next"] = ["step_decide"]
        proto["steps"][1]["conditions"] = [
            {"if": "loop", "next": "step_assess"},
        ]
        # Remove terminal to ensure dead-end error doesn't mask cycle
        # (step_complete has no path from the loop)
        r = validate_protocol(proto)
        # Should have cycle-related error
        assert any("Cycle detected" in e for e in r.errors)


# ═══════════════════════════════════════════════════════════════════════════
# validate_protocol — duplicate descriptions
# ═══════════════════════════════════════════════════════════════════════════


class TestDuplicateDescriptions:
    """Steps with identical descriptions should trigger a warning."""

    def test_duplicate_flagged(self):
        proto = _valid_protocol()
        proto["steps"][0]["description"] = "Do the thing."
        proto["steps"][2]["description"] = "Do the thing."
        r = validate_protocol(proto)
        assert any("identical descriptions" in w for w in r.warnings)

    def test_no_false_positive(self):
        r = validate_protocol(_valid_protocol())
        assert not any("identical descriptions" in w for w in r.warnings)


# ═══════════════════════════════════════════════════════════════════════════
# validate_protocol — dead-end / reachability
# ═══════════════════════════════════════════════════════════════════════════


class TestDeadEnds:
    """Non-terminal steps must reach a terminal step."""

    def test_dead_end_flagged(self):
        """A non-terminal step with no successors is a dead end."""
        proto = _valid_protocol()
        # Add a disconnected non-terminal step
        proto["steps"].append({
            "id": "step_orphan",
            "description": "Orphan step with no way forward.",
            "type": "action",
            "allowed_next": [],
        })
        proto["possible_actions"].append(
            {"id": "step_orphan", "description": "Orphan"}
        )
        r = validate_protocol(proto)
        assert any("step_orphan" in e and "dead-end" in e for e in r.errors)

    def test_no_dead_end_in_valid(self):
        r = validate_protocol(_valid_protocol())
        assert not any("dead-end" in e for e in r.errors)


# ═══════════════════════════════════════════════════════════════════════════
# BFS reachability
# ═══════════════════════════════════════════════════════════════════════════


class TestBFSReachable:
    """BFS reachability helper."""

    def test_reaches_all_connected(self):
        steps = _valid_protocol()["steps"]
        visited: set[str] = set()
        _bfs_reachable("step_assess", steps, visited)
        assert "step_assess" in visited
        assert "step_decide" in visited
        assert "step_complete" in visited

    def test_unreachable_node(self):
        """Steps not connected to start are not in the visited set."""
        steps = _valid_protocol()["steps"]
        steps.append({
            "id": "step_isolated",
            "description": "Not connected.",
            "type": "action",
            "allowed_next": [],
        })
        visited: set[str] = set()
        _bfs_reachable("step_assess", steps, visited)
        assert "step_isolated" not in visited

    def test_empty_graph(self):
        visited: set[str] = set()
        _bfs_reachable("start", [], visited)
        assert len(visited) == 0


# ═══════════════════════════════════════════════════════════════════════════
# validate_knowledge_base — valid input
# ═══════════════════════════════════════════════════════════════════════════


class TestValidateKBValid:
    """A well-formed KB should pass with no errors."""

    def test_no_errors(self):
        proto = _valid_protocol()
        kb = _valid_kb(proto)
        r = validate_knowledge_base(kb, proto)
        assert r.ok, f"Unexpected errors: {r.errors}"


# ═══════════════════════════════════════════════════════════════════════════
# validate_knowledge_base — missing coverage
# ═══════════════════════════════════════════════════════════════════════════


class TestValidateKBCoverage:
    """Steps without KB chunks should produce warnings."""

    def test_missing_step_coverage(self):
        proto = _valid_protocol()
        kb = _valid_kb(proto)
        # Remove the chunk covering step_complete
        kb["chunks"] = [c for c in kb["chunks"] if "step_complete" not in c.get("related_steps", [])]
        r = validate_knowledge_base(kb, proto)
        assert any("step_complete" in w for w in r.warnings)

    def test_missing_constraint_coverage(self):
        proto = _valid_protocol()
        kb = _valid_kb(proto)
        # Remove constraint refs from all chunks
        for c in kb["chunks"]:
            c["related_constraints"] = []
        r = validate_knowledge_base(kb, proto)
        assert any("no_running" in w for w in r.warnings)


# ═══════════════════════════════════════════════════════════════════════════
# validate_knowledge_base — chunk quality
# ═══════════════════════════════════════════════════════════════════════════


class TestValidateKBChunkQuality:
    """Chunk quality checks: length, sentences, duplicates."""

    def test_short_chunk_warning(self):
        proto = _valid_protocol()
        kb = _valid_kb(proto)
        kb["chunks"][0]["text"] = "Too short."  # < 100 chars
        r = validate_knowledge_base(kb, proto)
        assert any("too short" in w for w in r.warnings)

    def test_long_chunk_warning(self):
        proto = _valid_protocol()
        kb = _valid_kb(proto)
        kb["chunks"][0]["text"] = "Long content. " * 200  # > 2000 chars
        r = validate_knowledge_base(kb, proto)
        assert any("too long" in w for w in r.warnings)

    def test_near_duplicate_warning(self):
        proto = _valid_protocol()
        kb = _valid_kb(proto)
        # Make two chunks nearly identical
        shared_text = (
            "This is identical text about evacuation procedures. "
            "Follow the route to the assembly point. "
            "Check all rooms before leaving the building."
        )
        kb["chunks"][0]["text"] = shared_text
        kb["chunks"][1]["text"] = shared_text
        r = validate_knowledge_base(kb, proto)
        assert any("near-duplicate" in w for w in r.warnings)

    def test_single_sentence_warning(self):
        proto = _valid_protocol()
        kb = _valid_kb(proto)
        kb["chunks"][0]["text"] = "Only one sentence without enough information for retrieval" + " padding" * 20
        r = validate_knowledge_base(kb, proto)
        assert any("1 sentence" in w for w in r.warnings)

    def test_protocol_id_mismatch(self):
        proto = _valid_protocol()
        kb = _valid_kb(proto)
        kb["protocol_id"] = "wrong_id"
        r = validate_knowledge_base(kb, proto)
        assert any("protocol_id" in w for w in r.warnings)

    def test_empty_chunks_error(self):
        proto = _valid_protocol()
        r = validate_knowledge_base({"chunks": []}, proto)
        assert not r.ok
        assert any("zero chunks" in e for e in r.errors)

    def test_missing_chunks_key_error(self):
        proto = _valid_protocol()
        r = validate_knowledge_base({}, proto)
        assert not r.ok
        assert any("chunks" in e for e in r.errors)


# ═══════════════════════════════════════════════════════════════════════════
# Helper function tests
# ═══════════════════════════════════════════════════════════════════════════


class TestHelpers:
    """Unit tests for small helpers."""

    def test_count_sentences_normal(self):
        assert _count_sentences("Hello world. This is a test. Done!") == 3

    def test_count_sentences_single(self):
        assert _count_sentences("Just one sentence.") == 1

    def test_count_sentences_questions(self):
        assert _count_sentences("Is this safe? Yes it is. Proceed.") == 3

    def test_word_set(self):
        words = _word_set("Hello, World! Hello again.")
        assert "hello" in words
        assert "world" in words
        assert "again" in words

    def test_word_set_empty(self):
        assert _word_set("") == set()
