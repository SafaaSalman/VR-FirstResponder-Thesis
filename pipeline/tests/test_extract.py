"""Tests for PDF extraction helpers: heading detection, section splitting, title detection."""

from __future__ import annotations

import pytest

from pipeline.extract import (
    Section,
    _match_heading,
    _split_into_sections,
    _detect_title,
    _normalize_text,
    _merge_thin_sections,
    _split_into_sections_paged,
    _PageData,
)


# ═══════════════════════════════════════════════════════════════════════════
# _match_heading
# ═══════════════════════════════════════════════════════════════════════════


class TestMatchHeading:
    """Heading regex detection with 15+ cases."""

    # ── Numbered headings ──────────────────────────────────────────

    def test_simple_numbered(self):
        result = _match_heading("1. Introduction")
        assert result is not None
        assert "Introduction" in result["heading"]
        assert result["level"] == 1

    def test_dotted_numbered(self):
        result = _match_heading("2.3 Evacuation Procedures")
        assert result is not None
        assert "Evacuation Procedures" in result["heading"]
        assert result["level"] == 2

    def test_deeply_nested_numbered(self):
        result = _match_heading("4.2.1 Sub-procedure Details")
        assert result is not None
        assert result["level"] == 3

    def test_step_prefix(self):
        result = _match_heading("Step 3: Verify equipment")
        assert result is not None
        assert "Verify equipment" in result["heading"]

    def test_section_prefix(self):
        result = _match_heading("Section 5. Emergency Contacts")
        assert result is not None
        assert "Emergency Contacts" in result["heading"]

    def test_chapter_prefix(self):
        result = _match_heading("Chapter 1 — Overview")
        assert result is not None

    # ── Letter headings ────────────────────────────────────────────

    def test_letter_heading_uppercase(self):
        result = _match_heading("A. Pre-departure checklist")
        assert result is not None
        assert result["level"] == 2
        assert "Pre-departure checklist" in result["heading"]

    def test_letter_heading_with_paren(self):
        result = _match_heading("B) Secondary evacuation route")
        assert result is not None
        assert result["level"] == 2

    # ── ALL-CAPS headings ──────────────────────────────────────────

    def test_allcaps_short_heading(self):
        result = _match_heading("EMERGENCY PROCEDURES", preceded_by_break=True)
        assert result is not None
        assert result["heading"] == "EMERGENCY PROCEDURES"
        assert result["level"] == 1

    def test_allcaps_without_break_rejected(self):
        """ALL-CAPS mid-paragraph should NOT be detected as heading."""
        result = _match_heading("DO NOT USE ELEVATORS", preceded_by_break=False)
        assert result is None

    def test_allcaps_too_long_rejected(self):
        """ALL-CAPS lines > 80 chars should be rejected."""
        long_line = "A" * 82
        result = _match_heading(long_line, preceded_by_break=True)
        assert result is None

    def test_allcaps_with_break_accepted(self):
        result = _match_heading("FIRE SAFETY PROTOCOL", preceded_by_break=True)
        assert result is not None

    # ── Font-size override ─────────────────────────────────────────

    def test_large_font_overrides_case(self):
        """A lowercase line with large font should be detected as heading."""
        result = _match_heading(
            "evacuation route details",
            preceded_by_break=False,
            is_large_font=True,
        )
        assert result is not None
        assert result["level"] == 1

    # ── Non-headings (should return None) ──────────────────────────

    def test_short_line_rejected(self):
        """Lines < 4 chars should be rejected."""
        assert _match_heading("Hi") is None

    def test_very_long_line_rejected(self):
        """Lines > 150 chars should be rejected."""
        assert _match_heading("x" * 151) is None

    def test_plain_body_text_rejected(self):
        assert _match_heading("This is a normal sentence about fire safety.") is None

    def test_lowercase_sentence_rejected(self):
        assert _match_heading("ensure all exits are clearly marked") is None

    def test_mixed_case_body_rejected(self):
        """Normal mixed-case body text should not match any heading pattern."""
        assert _match_heading("The firefighter must wear PPE at all times.") is None


# ═══════════════════════════════════════════════════════════════════════════
# _split_into_sections
# ═══════════════════════════════════════════════════════════════════════════


class TestSplitIntoSections:
    """Section splitting from raw text."""

    SAMPLE_TEXT = (
        "Some introductory text about the protocol.\n"
        "This paragraph describes the overall purpose.\n"
        "\n"
        "1. Initial Assessment\n"
        "Check the area for hazards. Ensure all personnel are accounted for.\n"
        "Document the situation carefully. Report findings to command.\n"
        "This is additional information about the initial assessment phase.\n"
        "\n"
        "2. Evacuation Procedures\n"
        "Begin evacuation of the building following designated routes.\n"
        "Assist those who need help. Check all rooms before leaving.\n"
        "Verify everyone has reached the assembly point safely.\n"
        "\n"
        "3. Post-Evacuation\n"
        "Conduct a headcount at the assembly point for all personnel.\n"
        "Report the results to the incident commander immediately.\n"
        "Await further instructions from the fire department team.\n"
    )

    def test_splits_numbered_sections(self):
        sections = _split_into_sections(self.SAMPLE_TEXT)
        # Should have intro + 3 numbered sections
        assert len(sections) >= 3

    def test_headings_preserved(self):
        sections = _split_into_sections(self.SAMPLE_TEXT)
        headings = [s.heading for s in sections]
        assert any("Initial Assessment" in h for h in headings)
        assert any("Evacuation" in h for h in headings)
        assert any("Post-Evacuation" in h for h in headings)

    def test_no_empty_bodies(self):
        sections = _split_into_sections(self.SAMPLE_TEXT)
        for s in sections:
            assert len(s.text.strip()) > 0, f"Section '{s.heading}' has empty body"

    def test_all_text_accounted_for(self):
        """Every non-blank line should appear in exactly one section."""
        sections = _split_into_sections(self.SAMPLE_TEXT)
        all_section_text = " ".join(s.text for s in sections)
        for line in self.SAMPLE_TEXT.strip().split("\n"):
            line = line.strip()
            if line and not _match_heading(line, preceded_by_break=True):
                # Body lines should appear somewhere in section text
                assert line in all_section_text, f"Line missing: {line!r}"

    def test_single_section_no_headings(self):
        """Text without headings should produce a single section."""
        text = (
            "This is some body text without any headings present.\n"
            "It just has regular paragraphs of content throughout.\n"
            "More text to ensure it passes the minimum body length threshold.\n"
        )
        sections = _split_into_sections(text)
        assert len(sections) == 1

    def test_allcaps_in_body_not_heading(self):
        """ALL-CAPS lines in the middle of a paragraph are not headings."""
        text = (
            "1. Safety Rules for Evacuation During Emergency Events\n"
            "Several important points to remember during any evacuation:\n"
            "DO NOT USE ELEVATORS during a fire emergency event.\n"
            "ALWAYS CHECK FOR SMOKE before opening any closed door.\n"
            "Wait for the all-clear signal from the incident commander.\n"
        )
        sections = _split_into_sections(text)
        # The ALL-CAPS lines should NOT create separate sections
        # because they are not preceded by a blank line
        assert len(sections) == 1


# ═══════════════════════════════════════════════════════════════════════════
# _detect_title
# ═══════════════════════════════════════════════════════════════════════════


class TestDetectTitle:
    """Title detection from the first page."""

    def test_normal_title(self):
        text = "Emergency Evacuation Protocol\nVersion 2.0\nPublished 2024"
        assert _detect_title(text) == "Emergency Evacuation Protocol"

    def test_skips_short_lines(self):
        text = "v2\nEmergency Evacuation Protocol\nDetails follow"
        assert _detect_title(text) == "Emergency Evacuation Protocol"

    def test_empty_first_page(self):
        assert _detect_title("") == "Untitled Protocol"

    def test_whitespace_only(self):
        assert _detect_title("   \n  \n") == "Untitled Protocol"

    def test_title_with_special_chars(self):
        text = "SOP #42 — Fire Response (Rev. 3)\nSome other text"
        assert "SOP #42" in _detect_title(text)


# ═══════════════════════════════════════════════════════════════════════════
# _normalize_text
# ═══════════════════════════════════════════════════════════════════════════


class TestNormalizeText:
    """Unicode normalisation and PDF artifact cleanup."""

    def test_soft_hyphen_removed(self):
        assert _normalize_text("proto\u00adcol") == "protocol"

    def test_zero_width_space_removed(self):
        assert _normalize_text("fire\u200bsafety") == "firesafety"

    def test_nbsp_replaced(self):
        assert _normalize_text("hello\u00a0world") == "hello world"

    def test_bom_removed(self):
        assert _normalize_text("\ufeffHello") == "Hello"

    def test_nfkc_ligature(self):
        # fi ligature (U+FB01) should normalise to 'fi'
        assert _normalize_text("\ufb01re") == "fire"


# ═══════════════════════════════════════════════════════════════════════════
# _merge_thin_sections
# ═══════════════════════════════════════════════════════════════════════════


class TestMergeThinSections:
    """Thin section merging."""

    def test_thin_section_merged(self):
        sections = [
            Section(heading="Intro", text="Long enough body text with lots of details here for testing.", page_numbers=[1]),
            Section(heading="Tiny", text="Short", page_numbers=[2]),
        ]
        merged = _merge_thin_sections(sections, min_body_chars=50)
        assert len(merged) == 1
        assert "Short" in merged[0].text

    def test_thick_sections_kept(self):
        sections = [
            Section(heading="A", text="x" * 100, page_numbers=[1]),
            Section(heading="B", text="y" * 100, page_numbers=[2]),
        ]
        merged = _merge_thin_sections(sections, min_body_chars=50)
        assert len(merged) == 2

    def test_empty_list(self):
        assert _merge_thin_sections([], min_body_chars=50) == []

    def test_page_numbers_merged(self):
        sections = [
            Section(heading="Intro", text="x" * 100, page_numbers=[1, 2]),
            Section(heading="Tiny", text="Short", page_numbers=[3]),
        ]
        merged = _merge_thin_sections(sections, min_body_chars=50)
        assert 3 in merged[0].page_numbers
