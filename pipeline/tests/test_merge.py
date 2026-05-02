"""Tests for _merge_and_renumber() in kb_generator.py."""

from __future__ import annotations

import pytest

from pipeline.kb_generator import _merge_and_renumber


# ── Helpers ────────────────────────────────────────────────────────────────

def _chunk(chunk_id: str, title: str, text: str,
           related_steps: list[str] | None = None) -> dict:
    """Create a minimal chunk dict."""
    return {
        "chunk_id": chunk_id,
        "title": title,
        "text": text,
        "related_steps": related_steps or [],
        "tags": [],
    }


# ═══════════════════════════════════════════════════════════════════════════
# Merge & renumber
# ═══════════════════════════════════════════════════════════════════════════


class TestMergeAndRenumber:
    """Merge, deduplicate, and renumber KB chunks."""

    def test_basic_merge_preserves_all(self):
        """Non-overlapping chunks from different batches are all kept."""
        chunks = [
            _chunk("kb_001", "First chunk", "Details about assessment.", ["step_a"]),
            _chunk("kb_002", "Second chunk", "Details about evacuation.", ["step_b"]),
            _chunk("kb_001", "Third chunk", "Details about cleanup.", ["step_c"]),
        ]
        result = _merge_and_renumber(chunks)
        assert len(result) == 3

    def test_renumbering_sequential(self):
        """After merge, chunk_ids should be kb_001, kb_002, kb_003, ..."""
        chunks = [
            _chunk("batch1_001", "A", "Text A about procedures.", ["step_a"]),
            _chunk("batch1_002", "B", "Text B about procedures.", ["step_b"]),
            _chunk("batch2_001", "C", "Text C about procedures.", ["step_c"]),
        ]
        result = _merge_and_renumber(chunks)
        for i, c in enumerate(result, 1):
            assert c["chunk_id"] == f"kb_{i:03d}"

    def test_deduplication_same_steps_same_title(self):
        """Chunks with same related_steps and same title prefix are deduped."""
        shorter = _chunk("kb_001", "Evacuation procedure",
                         "Short text.", ["step_b"])
        longer = _chunk("kb_002", "Evacuation procedure",
                        "This is a much more detailed text about evacuation procedures and safety.",
                        ["step_b"])
        result = _merge_and_renumber([shorter, longer])
        # Should keep only 1 (the longer one)
        assert len(result) == 1
        assert "much more detailed" in result[0]["text"]

    def test_dedup_keeps_longer(self):
        """When deduplicating, the longer chunk text wins."""
        c1 = _chunk("kb_001", "Fire safety overview",
                     "Brief note.", ["step_fire"])
        c2 = _chunk("kb_002", "Fire safety overview",
                     "Extended description of fire safety with many details and procedures.",
                     ["step_fire"])
        result = _merge_and_renumber([c1, c2])
        assert len(result) == 1
        assert result[0]["text"] == c2["text"]
        assert result[0]["chunk_id"] == "kb_001"

    def test_different_steps_no_dedup(self):
        """Chunks with different related_steps are NOT deduped even if titles match."""
        c1 = _chunk("kb_001", "Safety procedures", "Text one.", ["step_a"])
        c2 = _chunk("kb_002", "Safety procedures", "Text two.", ["step_b"])
        result = _merge_and_renumber([c1, c2])
        assert len(result) == 2

    def test_different_titles_no_dedup(self):
        """Chunks with same steps but different titles are NOT deduped."""
        c1 = _chunk("kb_001", "Assessment protocol",
                     "Text one about assessment.", ["step_a"])
        c2 = _chunk("kb_002", "Evacuation protocol",
                     "Text two about evacuation.", ["step_a"])
        result = _merge_and_renumber([c1, c2])
        assert len(result) == 2

    def test_empty_input(self):
        assert _merge_and_renumber([]) == []

    def test_single_chunk(self):
        chunks = [_chunk("kb_999", "Only chunk", "Some text here.", ["step_x"])]
        result = _merge_and_renumber(chunks)
        assert len(result) == 1
        assert result[0]["chunk_id"] == "kb_001"

    def test_renumber_after_dedup(self):
        """After dedup removes chunks, renumbering should still be sequential."""
        chunks = [
            _chunk("kb_001", "Alpha", "First chunk text content.", ["step_a"]),
            _chunk("kb_002", "Beta", "Short.", ["step_b"]),
            _chunk("kb_003", "Beta", "Much longer beta content with extra detail.", ["step_b"]),
            _chunk("kb_004", "Gamma", "Gamma chunk text content.", ["step_c"]),
        ]
        result = _merge_and_renumber(chunks)
        # Beta short + Beta long → deduplicated to 1
        assert len(result) == 3
        assert [c["chunk_id"] for c in result] == ["kb_001", "kb_002", "kb_003"]

    def test_preserves_extra_fields(self):
        """Fields like tags and related_constraints should survive merge."""
        chunk = {
            "chunk_id": "kb_001",
            "title": "Tagged chunk",
            "text": "Some chunk text with details.",
            "related_steps": ["step_a"],
            "tags": ["fire", "safety"],
            "related_constraints": ["no_running"],
            "source_grounded": True,
        }
        result = _merge_and_renumber([chunk])
        assert result[0]["tags"] == ["fire", "safety"]
        assert result[0]["related_constraints"] == ["no_running"]
        assert result[0]["source_grounded"] is True
