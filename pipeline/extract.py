"""
PDF text extraction module.

Uses pdfplumber to extract text from one or more PDFs while
preserving structural cues (headings, lists, tables).

Improvements (Prompt 3):
- Page numbers populated for every section
- ALL-CAPS heading detection tightened (≤80 chars, requires blank-line break)
- Font-size heading detection via pdfplumber character data
- Scanned/image-based PDF detection with warnings
- Table deduplication (only append genuinely new table content)
- Unicode NFKC normalisation + PDF artifact cleanup
- Thin sections (< 50 chars body) merged into predecessor
"""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from statistics import median
from typing import List

import pdfplumber

logger = logging.getLogger("pipeline.extract")


# ── Data structures ────────────────────────────────────────────────────────

@dataclass
class Section:
    """A logical section extracted from a PDF."""
    heading: str
    text: str
    page_numbers: List[int] = field(default_factory=list)
    level: int = 1  # heading depth (1 = top, 2 = sub, etc.)


@dataclass
class ExtractedDocument:
    """Full extraction result from one PDF."""
    source_path: str
    title: str
    raw_text: str
    sections: List[Section]
    page_count: int
    warnings: List[str] = field(default_factory=list)


@dataclass
class _PageData:
    """Per-page extraction data used during section splitting."""
    page_num: int                                            # 1-based
    text: str                                                # normalised, table-deduplicated
    large_font_lines: set = field(default_factory=set)       # lines with oversized font


# ── Unicode normalisation ──────────────────────────────────────────────────

def _normalize_text(text: str) -> str:
    """NFKC normalisation + common PDF artifact cleanup."""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00ad", "")     # soft hyphen
    text = text.replace("\u200b", "")     # zero-width space
    text = text.replace("\u200c", "")     # zero-width non-joiner
    text = text.replace("\u200d", "")     # zero-width joiner
    text = text.replace("\ufeff", "")     # BOM / zero-width no-break space
    text = text.replace("\u00a0", " ")    # non-breaking space → regular space
    return text


# ── Table deduplication ────────────────────────────────────────────────────

def _build_table_block(table: list[list], page_text: str) -> str | None:
    """Build a [TABLE] block only if it contains content NOT already in *page_text*.

    Returns the formatted table string or ``None`` if all cell content is
    already present in the page's extracted text.
    """
    rows: list[str] = []
    has_new_content = False
    for row in table:
        cells = [str(c).strip() if c else "" for c in row]
        for cell in cells:
            if cell and len(cell) > 3 and cell not in page_text:
                has_new_content = True
        rows.append(" | ".join(cells))

    if not has_new_content:
        return None
    return "\n\n[TABLE]\n" + "\n".join(rows) + "\n[/TABLE]\n"


# ── Font-size heading detection ────────────────────────────────────────────

def _compute_body_font_size(page) -> float | None:
    """Median font size on a page (proxy for body-text size)."""
    try:
        chars = page.chars
        if not chars:
            return None
        sizes = [c.get("size", 0) for c in chars if c.get("size")]
        return median(sizes) if sizes else None
    except Exception:
        return None


def _find_large_font_lines(page, body_font_size: float | None) -> set[str]:
    """Return line texts whose average font size is >20 % larger than body."""
    if not body_font_size or body_font_size <= 0:
        return set()
    try:
        chars = page.chars
        if not chars:
            return set()

        threshold = body_font_size * 1.2
        y_tolerance = 3.0

        # Group characters by approximate y-position (visual row)
        y_groups: dict[float, list] = {}
        for c in chars:
            y_key = round(c.get("top", 0) / y_tolerance) * y_tolerance
            y_groups.setdefault(y_key, [])
            y_groups[y_key].append(c)

        large_lines: set[str] = set()
        for row_chars in y_groups.values():
            sizes = [c.get("size", 0) for c in row_chars if c.get("size")]
            if not sizes:
                continue
            if sum(sizes) / len(sizes) > threshold:
                row_text = "".join(
                    c.get("text", "") for c in
                    sorted(row_chars, key=lambda ch: ch.get("x0", 0))
                ).strip()
                if row_text:
                    large_lines.add(row_text)

        return large_lines
    except Exception:
        return set()


# ── Extraction entry points ────────────────────────────────────────────────

def extract_pdf(pdf_path: str | Path) -> ExtractedDocument:
    """Extract structured text from a single PDF.

    Returns an ``ExtractedDocument`` with per-section page tracking,
    deduplicated tables, normalised Unicode, and scanned-PDF warnings.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages_data: list[_PageData] = []
    warnings: list[str] = []
    empty_page_count = 0

    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            page_num: int = page.page_number  # 1-based

            raw_page_text = page.extract_text() or ""

            # Scanned-PDF bookkeeping
            if not raw_page_text.strip():
                empty_page_count += 1

            # Unicode normalisation
            text = _normalize_text(raw_page_text)

            # Table deduplication — only append tables with genuinely new content
            for table in page.extract_tables():
                block = _build_table_block(table, text)
                if block:
                    text += block

            # Font-size heading detection
            body_fs = _compute_body_font_size(page)
            large_font_lines = _find_large_font_lines(page, body_fs)

            pages_data.append(_PageData(
                page_num=page_num,
                text=text,
                large_font_lines=large_font_lines,
            ))

    # ── Scanned-PDF detection ──────────────────────────────────────
    if page_count > 0 and empty_page_count / page_count > 0.5:
        warn_msg = (
            f"PDF appears to be scanned/image-based "
            f"({empty_page_count}/{page_count} pages empty). "
            f"Consider running OCR first (e.g., ocrmypdf)."
        )
        warnings.append(warn_msg)
        logger.warning(warn_msg)

    raw_text = "\n\n".join(pd.text for pd in pages_data)
    title = _detect_title(pages_data[0].text) if pages_data else pdf_path.stem
    sections = _split_into_sections_paged(pages_data)
    sections = _merge_thin_sections(sections, min_body_chars=50)

    return ExtractedDocument(
        source_path=str(pdf_path),
        title=title,
        raw_text=raw_text,
        sections=sections,
        page_count=page_count,
        warnings=warnings,
    )


def extract_multiple_pdfs(pdf_paths: list[str | Path]) -> list[ExtractedDocument]:
    """Extract from multiple PDFs and return a list of documents."""
    docs = []
    for path in pdf_paths:
        logger.info("Extracting: %s", path)
        docs.append(extract_pdf(path))
    return docs


# ── Heading / section detection ────────────────────────────────────────────

# Numbered: "1.", "1.1", "Step 1:", "Section 1:", "Chapter 2:"
_HEADING_NUMBERED = re.compile(
    r"^(?:(?:step|section|chapter|part|phase|appendix)\s+)?"
    r"(\d+(?:\.\d+)*)\s*[.:)\-]?\s+(.+)",
    re.IGNORECASE,
)

# Letter-numbered: "A.", "B)", "a."
_HEADING_LETTER = re.compile(r"^([A-Z])\s*[.)]\s+(.+)")

# ALL-CAPS lines — tightened to 4–80 chars (was 4–120)
_HEADING_ALLCAPS = re.compile(r"^([A-Z][A-Z\s\-/&:]{2,76}[A-Z])$")


def _detect_title(first_page_text: str) -> str:
    """Heuristic: the first non-empty line of page 1 is the title."""
    for line in first_page_text.split("\n"):
        line = line.strip()
        if len(line) > 3:
            return line
    return "Untitled Protocol"


def _match_heading(line: str, *, preceded_by_break: bool = True,
                   is_large_font: bool = False) -> dict | None:
    """Check if *line* looks like a section heading.

    Args:
        line: stripped line text.
        preceded_by_break: True when the line is preceded by a blank line
            or is at page start (required for ALL-CAPS filtering).
        is_large_font: True when the line's average font size is >20 %
            larger than the page body font — treated as heading regardless
            of case.
    """
    if len(line) < 4 or len(line) > 150:
        return None

    # ── Font-size heading (overrides case rules) ───────────────────
    if is_large_font:
        return {"heading": line, "level": 1}

    # ── Numbered heading ───────────────────────────────────────────
    m = _HEADING_NUMBERED.match(line)
    if m:
        num = m.group(1)
        heading_text = m.group(2).strip()
        level = num.count(".") + 1
        return {"heading": f"{num} {heading_text}", "level": level}

    # ── Letter heading ─────────────────────────────────────────────
    m = _HEADING_LETTER.match(line)
    if m:
        heading_text = m.group(2).strip()
        return {"heading": f"{m.group(1)}. {heading_text}", "level": 2}

    # ── ALL-CAPS (strict: ≤ 80 chars + preceded by break) ─────────
    if len(line) <= 80:
        m = _HEADING_ALLCAPS.match(line)
        if m and preceded_by_break:
            return {"heading": line, "level": 1}

    return None


# ── Section splitting (page-aware) ────────────────────────────────────────

def _split_into_sections_paged(pages_data: list[_PageData]) -> list[Section]:
    """Split page-level text into sections, populating ``page_numbers``."""
    sections: list[Section] = []
    current_heading = "Introduction"
    current_lines: list[str] = []
    current_pages: set[int] = set()
    current_level = 1

    for page_data in pages_data:
        lines = page_data.text.split("\n")
        # Page start counts as a break (blank-line equivalent)
        prev_line_blank = True

        for line in lines:
            stripped = line.strip()
            if not stripped:
                current_lines.append("")
                prev_line_blank = True
                continue

            heading_match = _match_heading(
                stripped,
                preceded_by_break=prev_line_blank,
                is_large_font=(stripped in page_data.large_font_lines),
            )

            if heading_match:
                # Flush the accumulated section
                body = "\n".join(current_lines).strip()
                if body:
                    sections.append(Section(
                        heading=current_heading,
                        text=body,
                        page_numbers=sorted(current_pages),
                        level=current_level,
                    ))
                elif current_pages and sections:
                    # No body text — absorb page range into previous section
                    sections[-1].page_numbers = sorted(
                        set(sections[-1].page_numbers) | current_pages
                    )

                current_heading = heading_match["heading"]
                current_level = heading_match["level"]
                current_lines = []
                current_pages = {page_data.page_num}
            else:
                current_lines.append(line)
                current_pages.add(page_data.page_num)

            prev_line_blank = False

    # Flush the last section
    body = "\n".join(current_lines).strip()
    if body:
        sections.append(Section(
            heading=current_heading,
            text=body,
            page_numbers=sorted(current_pages),
            level=current_level,
        ))

    return sections


def _merge_thin_sections(sections: list[Section],
                         min_body_chars: int = 50) -> list[Section]:
    """Merge sections whose body text is shorter than *min_body_chars*
    back into the preceding section."""
    if not sections:
        return sections

    merged: list[Section] = [sections[0]]
    for section in sections[1:]:
        if len(section.text.strip()) < min_body_chars and merged:
            prev = merged[-1]
            prev.text += f"\n\n{section.heading}\n{section.text}"
            prev.page_numbers = sorted(
                set(prev.page_numbers) | set(section.page_numbers)
            )
        else:
            merged.append(section)

    return merged


# Backward-compatible wrapper (used by legacy callers / tests)
def _split_into_sections(text: str) -> list[Section]:
    """Split raw text into sections without page tracking."""
    page_data = _PageData(page_num=1, text=text, large_font_lines=set())
    return _merge_thin_sections(
        _split_into_sections_paged([page_data]),
        min_body_chars=50,
    )
