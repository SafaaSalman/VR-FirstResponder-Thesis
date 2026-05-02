"""Tests for batch splitting with overlap in structure.py and kb_generator.py."""

from __future__ import annotations

import pytest

from pipeline.extract import Section
from pipeline.structure import (
    _split_sections_into_batches,
    OVERLAP_SECTIONS as STRUCT_OVERLAP,
)
from pipeline.kb_generator import (
    _split_into_batches,
    OVERLAP_SECTIONS as KB_OVERLAP,
)


# ── Helpers ────────────────────────────────────────────────────────────────

OVERLAP_TAG = "[OVERLAP \u2014 context from previous batch] "


def _make_sections(n: int, text_len: int = 200) -> list[Section]:
    """Create *n* deterministic sections with known text length."""
    return [
        Section(
            heading=f"Section {i+1}",
            text=f"Body of section {i+1}. " + ("x" * text_len),
            page_numbers=[i + 1],
            level=1,
        )
        for i in range(n)
    ]


def _tiny_token_budget() -> int:
    """Return a token budget that forces roughly 5 sections per batch.

    Each test section is ~60 tokens (heading + 200-char body).
    5 sections × 60 ≈ 300 tokens.
    """
    return 300


# ── Tests: structure.py _split_sections_into_batches ───────────────────────

class TestStructureBatching:
    """Batch splitting with overlap for structure.py."""

    def test_single_batch_no_overlap(self):
        """When everything fits in one batch, no overlap is added."""
        sections = _make_sections(3)
        batches = _split_sections_into_batches(sections, max_tokens=999_999)
        assert len(batches) == 1
        assert batches[0] == sections
        # No heading should start with the overlap tag
        for s in batches[0]:
            assert not s.heading.startswith(OVERLAP_TAG)

    def test_multiple_batches_have_overlap(self):
        """Second+ batches start with overlap sections from the previous batch."""
        sections = _make_sections(10)
        budget = _tiny_token_budget()
        batches = _split_sections_into_batches(sections, max_tokens=budget)

        assert len(batches) >= 2, "Should create at least 2 batches"

        # First batch has no overlap tags
        for s in batches[0]:
            assert not s.heading.startswith(OVERLAP_TAG)

        # Every subsequent batch starts with tagged overlap sections
        for batch_idx in range(1, len(batches)):
            batch = batches[batch_idx]
            # Check the first OVERLAP_SECTIONS entries are tagged
            overlap_count = sum(
                1 for s in batch if s.heading.startswith(OVERLAP_TAG)
            )
            assert overlap_count >= 1, (
                f"Batch {batch_idx + 1} should have overlap sections"
            )
            # Overlap sections should be at the START
            for s in batch[:overlap_count]:
                assert s.heading.startswith(OVERLAP_TAG)

    def test_overlap_sections_match_previous_tail(self):
        """Overlap sections contain the same text as the tail of the previous batch."""
        sections = _make_sections(10)
        budget = _tiny_token_budget()
        batches = _split_sections_into_batches(sections, max_tokens=budget)

        assert len(batches) >= 2

        for batch_idx in range(1, len(batches)):
            batch = batches[batch_idx]
            prev_batch = batches[batch_idx - 1]

            # Collect overlap sections from current batch
            overlap_secs = [s for s in batch if s.heading.startswith(OVERLAP_TAG)]
            # Tail of previous batch (non-overlap only)
            prev_originals = [
                s for s in prev_batch if not s.heading.startswith(OVERLAP_TAG)
            ]
            tail = prev_originals[-len(overlap_secs):]

            for ov, orig in zip(overlap_secs, tail):
                assert ov.text == orig.text, "Overlap text must match original"
                expected_heading = f"{OVERLAP_TAG}{orig.heading}"
                assert ov.heading == expected_heading

    def test_overlap_zero_disables(self):
        """overlap=0 produces batches with no overlap at all."""
        sections = _make_sections(10)
        budget = _tiny_token_budget()
        batches = _split_sections_into_batches(
            sections, max_tokens=budget, overlap=0
        )
        for batch in batches:
            for s in batch:
                assert not s.heading.startswith(OVERLAP_TAG)

    def test_no_sections_lost(self):
        """Every original section appears at least once (ignoring overlap copies)."""
        sections = _make_sections(10)
        budget = _tiny_token_budget()
        batches = _split_sections_into_batches(sections, max_tokens=budget)

        original_headings = {s.heading for s in sections}
        found = set()
        for batch in batches:
            for s in batch:
                heading = s.heading
                if heading.startswith(OVERLAP_TAG):
                    heading = heading[len(OVERLAP_TAG):]
                found.add(heading)

        assert found == original_headings, "All sections must appear in batches"


# ── Tests: kb_generator.py _split_into_batches ────────────────────────────

class TestKBBatching:
    """Batch splitting with overlap for kb_generator.py."""

    def test_single_batch_no_overlap(self):
        sections = _make_sections(3)
        batches = _split_into_batches(sections, max_tokens=999_999)
        assert len(batches) == 1
        for s in batches[0]:
            assert not s.heading.startswith(OVERLAP_TAG)

    def test_multiple_batches_have_overlap(self):
        sections = _make_sections(10)
        budget = _tiny_token_budget()
        batches = _split_into_batches(sections, max_tokens=budget)

        assert len(batches) >= 2
        for batch_idx in range(1, len(batches)):
            overlap_count = sum(
                1 for s in batches[batch_idx]
                if s.heading.startswith(OVERLAP_TAG)
            )
            assert overlap_count >= 1

    def test_overlap_sections_properly_tagged(self):
        sections = _make_sections(10)
        budget = _tiny_token_budget()
        batches = _split_into_batches(sections, max_tokens=budget)

        for batch_idx in range(1, len(batches)):
            batch = batches[batch_idx]
            overlap_secs = [s for s in batch if s.heading.startswith(OVERLAP_TAG)]
            # Each overlap heading should contain the original heading
            for s in overlap_secs:
                original_heading = s.heading[len(OVERLAP_TAG):]
                assert original_heading.startswith("Section ")

    def test_no_sections_lost(self):
        sections = _make_sections(10)
        budget = _tiny_token_budget()
        batches = _split_into_batches(sections, max_tokens=budget)

        original_headings = {s.heading for s in sections}
        found = set()
        for batch in batches:
            for s in batch:
                heading = s.heading
                if heading.startswith(OVERLAP_TAG):
                    heading = heading[len(OVERLAP_TAG):]
                found.add(heading)

        assert found == original_headings

    def test_overlap_zero_disables(self):
        sections = _make_sections(10)
        budget = _tiny_token_budget()
        batches = _split_into_batches(sections, max_tokens=budget, overlap=0)
        for batch in batches:
            for s in batch:
                assert not s.heading.startswith(OVERLAP_TAG)


# ── Constant sanity checks ────────────────────────────────────────────────

class TestOverlapConstants:
    """Both modules should use the same default overlap."""

    def test_default_overlap_is_2(self):
        assert STRUCT_OVERLAP == 2
        assert KB_OVERLAP == 2


# ── Edge-case tests ───────────────────────────────────────────────────────

class TestStructureBatchingEdgeCases:
    """Edge cases for structure.py batch splitting."""

    def test_single_section(self):
        """One section always yields one batch."""
        sections = _make_sections(1)
        batches = _split_sections_into_batches(sections, max_tokens=999_999)
        assert len(batches) == 1
        assert len(batches[0]) == 1

    def test_empty_sections(self):
        """Empty input produces no batches."""
        batches = _split_sections_into_batches([], max_tokens=999_999)
        assert batches == [] or batches == [[]]

    def test_huge_single_section(self):
        """A section larger than the budget still gets its own batch."""
        big = Section(
            heading="Giant Section",
            text="word " * 50_000,  # very large
            page_numbers=[1],
            level=1,
        )
        batches = _split_sections_into_batches([big], max_tokens=100)
        assert len(batches) == 1
        assert batches[0][0].heading == "Giant Section"

    def test_two_sections_second_overflows(self):
        """If only two sections exist and they don't fit in one batch,
        the second batch gets overlap from the first."""
        sections = _make_sections(2, text_len=500)
        budget = _tiny_token_budget()
        batches = _split_sections_into_batches(sections, max_tokens=budget)
        if len(batches) == 2:
            overlap_in_second = [
                s for s in batches[1] if s.heading.startswith(OVERLAP_TAG)
            ]
            assert len(overlap_in_second) >= 1


class TestKBBatchingEdgeCases:
    """Edge cases for kb_generator.py batch splitting."""

    def test_single_section(self):
        sections = _make_sections(1)
        batches = _split_into_batches(sections, max_tokens=999_999)
        assert len(batches) == 1
        assert len(batches[0]) == 1

    def test_empty_sections(self):
        batches = _split_into_batches([], max_tokens=999_999)
        assert batches == [] or batches == [[]]

    def test_huge_single_section(self):
        big = Section(
            heading="Massive Section",
            text="word " * 50_000,
            page_numbers=[1],
            level=1,
        )
        batches = _split_into_batches([big], max_tokens=100)
        assert len(batches) == 1
        assert batches[0][0].heading == "Massive Section"
