"""
Protocol tree generator.

Takes extracted PDF sections and uses GPT-4o (structured output) to
produce the protocol JSON that the trainer engine expects.

For small documents (≤ 80K chars), uses a simple two-pass approach.
For large documents, uses a multi-pass approach:
  1. Batch-summarize sections into procedural summaries
  2. Feed all summaries into the extraction pass
  3. Validate and fix step connections
"""

from __future__ import annotations

import json
import logging
import math
import re
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from openai import OpenAI

from .extract import ExtractedDocument, Section
from .llm_utils import call_llm_json, call_llm_text, count_tokens, tpm_pace
from .config import PipelineConfig, get_config

logger = logging.getLogger("pipeline.structure")

# ── Legacy constants (kept as module-level defaults read from config) ─────
# These are now resolved from PipelineConfig at call time.
# The module-level names are retained only so that test_batching.py (which
# imports OVERLAP_SECTIONS directly) keeps working.
_cfg = get_config()
MAX_SINGLE_PASS_TOKENS = _cfg.max_single_pass_tokens
SUMMARY_BATCH_TOKENS = _cfg.summary_batch_tokens
OVERLAP_SECTIONS = _cfg.overlap_sections


# ── JSON schema that the LLM must produce ──────────────────────────────────

PROTOCOL_SCHEMA_DESCRIPTION = """
You are a protocol-engineering expert.  Given the text of an emergency
SOP / protocol document, produce a STRUCTURED JSON protocol object.

The JSON must conform to this exact structure:

{
  "protocol_id": "<snake_case_id>_v1",
  "title": "<Human-readable title>",
  "description": "<One-sentence description of the protocol>",
  "source": "<Source attribution>",
  "roles": ["<role1>", "<role2>"],
  "initial_step": "<id of the very first step>",

  "global_constraints": [
    {
      "id": "<snake_case_id>",
      "description": "<What is forbidden and why>",
      "forbidden_actions": ["<action_id_that_violates_this>"],
      "critical": true/false
    }
  ],

  "steps": [
    {
      "id": "<snake_case_id>",
      "type": "action" | "decision",
      "description": "<What the trainee must do — one sentence>",
      "preconditions": ["<variable> == <value>"],
      "effects": ["<variable> = <value>"],
      "allowed_next": ["<step_id>"],          // for action steps
      "conditions": [                          // for decision steps only
        { "if": "<variable> == <value>", "next": "<step_id>" }
      ],
      "critical": true/false,
      "phase": "<phase_name>"
    }
  ],

  "possible_actions": [
    { "id": "<action_id>", "label": "<short human label>" }
  ]
}

RULES FOR EXTRACTION:
1. Each step must have a unique snake_case id.
2. Steps must be ordered in the correct procedural sequence.
3. Use "decision" type when the next step depends on a condition
   (e.g., route blocked? injured person present?).
4. Preconditions are state variables that must be true BEFORE the step.
   Effects are state changes AFTER the step completes.
5. State variables must be boolean or simple types (string, int).
6. The first step should have `allowed_next` pointing to the second step.
7. The last step should have `"terminal": true` and empty `allowed_next`.
8. `critical: true` for steps that are mandatory for safety.
9. Phases group steps (e.g., "immediate_response", "assessment",
   "evacuation", "post_evacuation").
10. Global constraints define FORBIDDEN actions (things you must NEVER
    do). Each needs a corresponding entry in possible_actions.
11. possible_actions must include ALL step ids + constraint forbidden
    actions + "ask_question" + "request_hint".
12. Keep descriptions concise but specific.
13. Identify state variables that the scenario needs to track
    (e.g., shaking_active, stairs_accessible, inside_building).
    Document them through preconditions/effects so the engine
    knows when they change.
"""


def generate_protocol_tree(
    doc: ExtractedDocument,
    client: OpenAI,
    model: str = "gpt-4o",
    extra_context: str = "",
    progress: Callable[[str], None] | None = None,
    checkpoint_dir: Path | None = None,
) -> dict:
    """Generate the protocol tree JSON from extracted document text.

    For small documents: simple two-pass (extract → validate).
    For large documents: multi-pass (batch-summarize → extract → validate).

    If *checkpoint_dir* is given, batch summaries are persisted to
    ``<checkpoint_dir>/summary_batch_NNN.txt`` so that interrupted runs
    can be resumed without re-calling the LLM.
    """
    _log = progress or (lambda msg: logger.info(msg))

    sections_text = _format_sections(doc.sections) if doc.sections else doc.raw_text
    total_tokens = count_tokens(sections_text)

    if total_tokens <= MAX_SINGLE_PASS_TOKENS:
        # ── Small document: direct extraction ──────────────────────
        _log(f"Document is {total_tokens:,} tokens — fits in single pass")
        return _extract_and_validate(sections_text, doc, client, model, extra_context, _log)
    else:
        # ── Large document: batch-summarize → extract ──────────────
        _log(f"Document is {total_tokens:,} tokens — "
             f"using multi-pass batch summarization...")

        # Step 1: Split sections into batches by token budget.
        # Cap the budget so the full request (sections + system prompt +
        # user wrapper + output reservation) stays under the TPM limit.
        cfg = get_config()
        effective_budget = SUMMARY_BATCH_TOKENS
        if cfg.tpm_limit > 0:
            # Reserve ~35 % of TPM for prompt overhead & output tokens
            tpm_budget = int(cfg.tpm_limit * 0.65)
            effective_budget = min(effective_budget, tpm_budget)
            if effective_budget < SUMMARY_BATCH_TOKENS:
                _log(f"TPM limit {cfg.tpm_limit:,} → capping batch budget "
                     f"to {effective_budget:,} tokens")

        batches = _split_sections_into_batches(
            doc.sections if doc.sections else _fake_sections(doc.raw_text),
            effective_budget
        )
        _log(f"Split into {len(batches)} batches for summarization")

        # Step 2: Summarize each batch (with checkpoint support)
        ckpt_subdir = (checkpoint_dir / "checkpoints") if checkpoint_dir else None
        if ckpt_subdir:
            ckpt_subdir.mkdir(parents=True, exist_ok=True)

        all_summaries = []
        for i, batch in enumerate(batches):
            ckpt_file = ckpt_subdir / f"summary_batch_{i+1:03d}.txt" if ckpt_subdir else None

            # Resume: load from checkpoint if it exists
            if ckpt_file and ckpt_file.exists():
                summary = ckpt_file.read_text(encoding="utf-8")
                _log(f"Batch {i+1}/{len(batches)} loaded from checkpoint")
            else:
                batch_tokens = sum(count_tokens(s.heading + "\n" + s.text) for s in batch)
                _log(f"Summarizing batch {i+1}/{len(batches)} "
                     f"({batch_tokens:,} tokens, {len(batch)} sections)...")
                summary = _summarize_batch(batch, doc.title, client, model)
                _log(f"  → batch {i+1}: {count_tokens(summary):,} tokens of procedural content")

                # Save checkpoint
                if ckpt_file:
                    ckpt_file.write_text(summary, encoding="utf-8")
                    logger.debug("Saved checkpoint: %s", ckpt_file)

                # Pace sequential calls so we don't exceed the TPM quota
                tpm_pace(batch_tokens)

            all_summaries.append(summary)

        # Step 3: Combine summaries — recursively re-summarize if too long
        combined_summary = _recursive_summarize(
            all_summaries, doc.title, client, model, _log,
            level=1,
        )
        combined_tokens = count_tokens(combined_summary)
        _log(f"Final combined summary: {combined_tokens:,} tokens — "
             f"extracting protocol tree...")

        merged_extra = (
            f"{extra_context}\n\n" if extra_context else ""
        ) + (
            f"IMPORTANT: This text consists of {len(batches)} summarized batches "
            f"from a {doc.page_count}-page document.  The summaries focus on "
            f"procedural steps, decisions, constraints, and safety rules.  "
            f"Build the COMPLETE protocol covering ALL batches."
        )

        return _extract_and_validate(combined_summary, doc, client, model, merged_extra, _log)


def _extract_and_validate(
    text: str,
    doc: ExtractedDocument,
    client: OpenAI,
    model: str,
    extra_context: str,
    _log: Callable[[str], None],
) -> dict:
    """Pass 1: extract protocol structure, Pass 2: validate & fix."""
    _log("Pass 1: Extracting protocol structure via LLM...")
    system_msg = PROTOCOL_SCHEMA_DESCRIPTION
    if extra_context:
        system_msg += f"\n\nADDITIONAL CONTEXT:\n{extra_context}"

    user_msg = (
        f"DOCUMENT TITLE: {doc.title}\n"
        f"SOURCE: {doc.source_path}\n"
        f"PAGES: {doc.page_count}\n\n"
        f"DOCUMENT SECTIONS:\n{text}\n\n"
        "Now produce the protocol JSON.  Return ONLY valid JSON, "
        "no markdown fences, no commentary."
    )

    protocol = call_llm_json(
        client, model, system_msg, user_msg,
        temperature=get_config().temperature_extract, progress=_log,
    )

    n_steps = len(protocol.get("steps", []))
    n_constraints = len(protocol.get("global_constraints", []))
    _log(f"Pass 1 result: {n_steps} steps, {n_constraints} constraints")

    # Pace between extraction and validation to respect TPM limits
    extraction_tokens = count_tokens(text)
    tpm_pace(extraction_tokens)

    # ── Pass 2: Validate & fix connections ─────────────────────────
    _log("Pass 2: Validating step connections...")
    protocol = _validate_and_fix(protocol, client, model)

    # Pace after validation so the next pipeline stage (KB) starts fresh
    tpm_pace(extraction_tokens // 2)

    return protocol


def generate_protocol_from_multiple(
    docs: list[ExtractedDocument],
    client: OpenAI,
    model: str = "gpt-4o",
    protocol_name: str | None = None,
    progress: Callable[[str], None] | None = None,
    checkpoint_dir: Path | None = None,
) -> dict:
    """Merge multiple PDFs into a single protocol.

    Useful when a protocol spans multiple documents
    (e.g., general SOP + specific annex).
    """
    # Collect ALL sections from every document
    all_sections: list[Section] = []
    for doc in docs:
        for s in doc.sections:
            # Tag with source doc for attribution
            tagged = Section(
                heading=f"[{doc.title}] {s.heading}",
                text=s.text,
                page_numbers=s.page_numbers,
                level=s.level,
            )
            all_sections.append(tagged)

    # Create a synthetic ExtractedDocument with all sections
    combined_doc = ExtractedDocument(
        source_path=", ".join(d.source_path for d in docs),
        title=protocol_name or docs[0].title,
        raw_text="",  # not used — sections are used instead
        sections=all_sections,
        page_count=sum(d.page_count for d in docs),
    )

    extra_context = (
        "This protocol is assembled from MULTIPLE source documents.  "
        "Merge them into a single coherent protocol.  Resolve any "
        "conflicts by preferring the more specific / detailed version."
    )

    return generate_protocol_tree(combined_doc, client, model, extra_context, progress,
                                   checkpoint_dir=checkpoint_dir)


# ── Private helpers ────────────────────────────────────────────────────────

# Max recursion depth for summarization (prevents infinite loops)
_MAX_SUMMARY_RECURSION = 3

CONSOLIDATION_SYSTEM_PROMPT = """\
You are an expert at consolidating procedural summaries.

These are SUMMARIES of procedural content from a large emergency-protocol
document.  Consolidate them into a single comprehensive summary preserving
ALL procedural steps, decisions, and constraints.  Do not drop any procedures.

Preserve:
- The exact sequence of procedural steps
- All decision logic and branching
- All safety rules and constraints
- Key terminology exactly as written in the source

Output a CONCISE consolidated summary (aim for 30-50% of total input length).
Write in plain text, not JSON.  Use numbered lists for sequential steps and
bullet points for constraints/notes.
"""

SUMMARY_SYSTEM_PROMPT = """\
You are an expert at analyzing emergency protocol documents.

Given a batch of document sections, extract and summarize ALL procedural content:
- Sequential steps (what to do, in what order)
- Decision points (conditions that change the next action)
- Safety constraints and prohibitions (what is NEVER allowed)
- Roles and responsibilities
- State variables (conditions that change: e.g., "building evacuated", "route blocked")
- Timing requirements ("within 5 minutes", "immediately")
- Equipment or resource requirements

IGNORE non-procedural content like:
- Administrative metadata, revision history, table of contents
- General background/theory that doesn't contain actionable steps
- Appendices with reference tables (unless they define procedures)

Output a CONCISE summary (aim for 30-50% of input length) preserving:
- The exact sequence of procedural steps
- All decision logic and branching
- All safety rules and constraints
- Key terminology exactly as written in the source

Write in plain text, not JSON. Use numbered lists for sequential steps and
bullet points for constraints/notes.
"""


def _summarize_batch(
    sections: list[Section],
    doc_title: str,
    client: OpenAI,
    model: str,
) -> str:
    """Summarize a batch of sections, focusing on procedural content."""
    batch_text = "\n\n".join(
        f"### {s.heading}\n{s.text}" for s in sections
    )

    overlap_note = ""
    if any(s.heading.startswith("[OVERLAP") for s in sections):
        overlap_note = (
            "\n\nIMPORTANT: Sections marked [OVERLAP — context from previous "
            "batch] are provided for context only — do NOT re-summarize them, "
            "but use them to understand procedures that span batch boundaries."
        )

    user_msg = (
        f"Document: {doc_title}\n\n"
        f"Sections ({len(sections)} sections):\n\n"
        f"{batch_text}\n\n"
        "Summarize the procedural content from these sections."
        f"{overlap_note}"
    )

    return call_llm_text(
        client, model, SUMMARY_SYSTEM_PROMPT, user_msg,
        temperature=get_config().temperature_summarize,
    )


def _recursive_summarize(
    summaries: list[str],
    doc_title: str,
    client: OpenAI,
    model: str,
    _log: Callable[[str], None],
    level: int = 1,
) -> str:
    """Combine *summaries* into one text that fits MAX_SINGLE_PASS_TOKENS.

    If the concatenation exceeds the budget, re-batch and re-summarize
    using a consolidation prompt.  Recurses up to ``_MAX_SUMMARY_RECURSION``
    levels.
    """
    combined = "\n\n".join(
        f"═══ SUMMARY {i+1}/{len(summaries)} ═══\n{s}"
        for i, s in enumerate(summaries)
    )
    combined_tokens = count_tokens(combined)

    _log(f"Level {level}: {len(summaries)} summaries → "
         f"{combined_tokens:,} tokens")

    if combined_tokens <= MAX_SINGLE_PASS_TOKENS:
        _log(f"Level {level}: {combined_tokens:,} tokens — fits in single pass")
        return combined

    # ── Safety valve: give up after max recursion depth ────────────
    if level >= _MAX_SUMMARY_RECURSION:
        _log(f"⚠ Level {level}: still {combined_tokens:,} tokens after "
             f"{_MAX_SUMMARY_RECURSION} recursion levels — truncating as "
             f"last resort")
        keep_ratio = MAX_SINGLE_PASS_TOKENS / combined_tokens
        keep_chars = int(len(combined) * keep_ratio * 0.95)
        return (combined[:keep_chars]
                + "\n\n[... additional summaries truncated ...]")

    # ── Re-batch and re-summarize ──────────────────────────────────
    # Convert each summary text into a Section so we can reuse the
    # token-aware batch splitter.
    pseudo_sections = [
        Section(heading=f"Summary {i+1}", text=s, page_numbers=[], level=1)
        for i, s in enumerate(summaries)
    ]
    batches = _split_sections_into_batches(pseudo_sections,
                                           SUMMARY_BATCH_TOKENS,
                                           overlap=0)  # no overlap for consolidation
    _log(f"Level {level+1}: re-summarizing {len(summaries)} summaries "
         f"in {len(batches)} batches...")

    next_summaries: list[str] = []
    for i, batch in enumerate(batches):
        batch_tokens = sum(count_tokens(s.text) for s in batch)
        _log(f"  Consolidation batch {i+1}/{len(batches)} "
             f"({batch_tokens:,} tokens, {len(batch)} summaries)...")

        batch_text = "\n\n".join(s.text for s in batch)
        user_msg = (
            f"Document: {doc_title}\n\n"
            f"Summaries to consolidate ({len(batch)} summaries):\n\n"
            f"{batch_text}\n\n"
            "Consolidate these summaries into one comprehensive summary."
        )

        consolidated = call_llm_text(
            client, model, CONSOLIDATION_SYSTEM_PROMPT, user_msg,
            temperature=get_config().temperature_summarize,
        )
        next_summaries.append(consolidated)
        _log(f"  → consolidation batch {i+1}: "
             f"{count_tokens(consolidated):,} tokens")

        # Pace between consolidation calls
        tpm_pace(batch_tokens)

    return _recursive_summarize(
        next_summaries, doc_title, client, model, _log,
        level=level + 1,
    )


def _split_sections_into_batches(
    sections: list[Section],
    max_tokens: int,
    overlap: int = OVERLAP_SECTIONS,
) -> list[list[Section]]:
    """Split sections into batches that fit within a **token** budget.

    Successive batches include the last *overlap* sections of the previous
    batch (with headings prefixed ``[OVERLAP — context from previous batch]``)
    so that procedures spanning a boundary are not cut in half.
    """
    # --- first pass: pack sections into raw batches (no overlap yet) ---
    raw_batches: list[list[Section]] = []
    current_batch: list[Section] = []
    current_tokens = 0

    for s in sections:
        section_tokens = count_tokens(s.heading + "\n" + s.text)
        if current_tokens + section_tokens > max_tokens and current_batch:
            raw_batches.append(current_batch)
            current_batch = []
            current_tokens = 0
        current_batch.append(s)
        current_tokens += section_tokens

    if current_batch:
        raw_batches.append(current_batch)

    # Only one batch — no overlap needed
    if len(raw_batches) <= 1:
        return raw_batches

    # --- second pass: prepend overlap sections from previous batch ---
    OVERLAP_TAG = "[OVERLAP \u2014 context from previous batch] "

    final_batches: list[list[Section]] = [raw_batches[0]]
    for i in range(1, len(raw_batches)):
        prev = raw_batches[i - 1]
        tail = prev[-overlap:] if overlap else []
        tagged = [
            Section(
                heading=f"{OVERLAP_TAG}{s.heading}",
                text=s.text,
                page_numbers=s.page_numbers,
                level=s.level,
            )
            for s in tail
        ]
        final_batches.append(tagged + raw_batches[i])

    return final_batches


def _fake_sections(raw_text: str, chunk_size: int = 4000) -> list[Section]:
    """Split raw text into fake sections when no real sections exist."""
    sections = []
    for i in range(0, len(raw_text), chunk_size):
        chunk = raw_text[i:i + chunk_size]
        sections.append(Section(
            heading=f"Text block {i // chunk_size + 1}",
            text=chunk,
            page_numbers=[],
            level=1,
        ))
    return sections


def _format_sections(sections: list[Section]) -> str:
    """Format sections into a readable text block for the LLM."""
    parts = []
    for s in sections:
        indent = "  " * (s.level - 1)
        parts.append(f"{indent}## {s.heading}\n{s.text}")
    return "\n\n".join(parts)


def _truncate_sections(sections: list[Section], max_chars: int) -> str:
    """Truncate sections to fit within a character budget."""
    parts = []
    total = 0
    for s in sections:
        text = f"## {s.heading}\n{s.text}"
        if total + len(text) > max_chars:
            remaining = max_chars - total
            if remaining > 200:
                parts.append(text[:remaining] + "\n[... section truncated ...]")
            break
        parts.append(text)
        total += len(text)
    return "\n\n".join(parts)


def _validate_and_fix(protocol: dict, client: OpenAI, model: str) -> dict:
    """Second LLM pass to validate and fix connection issues."""
    steps = protocol.get("steps", [])
    if not steps:
        return protocol

    # Build a quick summary for the validator
    step_ids = [s["id"] for s in steps]
    step_summary = json.dumps(
        [
            {
                "id": s["id"],
                "type": s.get("type", "action"),
                "allowed_next": s.get("allowed_next", []),
                "conditions": s.get("conditions", []),
                "preconditions": s.get("preconditions", []),
                "effects": s.get("effects", []),
                "terminal": s.get("terminal", False),
            }
            for s in steps
        ],
        indent=2,
    )

    possible_ids = {a["id"] for a in protocol.get("possible_actions", [])}
    forbidden_ids = set()
    for c in protocol.get("global_constraints", []):
        forbidden_ids.update(c.get("forbidden_actions", []))

    errors = []

    # Check: every allowed_next / condition next must reference a real step
    for s in steps:
        for nxt in s.get("allowed_next", []):
            if nxt not in step_ids:
                errors.append(f"Step '{s['id']}' references non-existent next '{nxt}'")
        for cond in s.get("conditions", []):
            if cond["next"] not in step_ids:
                errors.append(f"Decision '{s['id']}' condition references non-existent '{cond['next']}'")
        # Check that step id is in possible_actions
        if s["id"] not in possible_ids:
            errors.append(f"Step '{s['id']}' missing from possible_actions")

    # Check: forbidden actions in possible_actions
    for fid in forbidden_ids:
        if fid not in possible_ids:
            errors.append(f"Forbidden action '{fid}' missing from possible_actions")

    # Check: exactly one terminal step
    terminals = [s for s in steps if s.get("terminal")]
    if not terminals:
        errors.append("No terminal step found")

    # Check: initial_step exists
    if protocol.get("initial_step") not in step_ids:
        errors.append(f"initial_step '{protocol.get('initial_step')}' not in steps")

    if not errors:
        logger.info("No connection errors found.")
        return protocol

    logger.warning("Found %d connection issues, asking LLM to fix...", len(errors))

    fix_prompt = (
        "The following protocol JSON has connection errors.  "
        "Fix ONLY the issues listed below.  Return the complete "
        "corrected JSON.\n\n"
        f"ERRORS:\n" + "\n".join(f"- {e}" for e in errors) + "\n\n"
        f"CURRENT PROTOCOL:\n{json.dumps(protocol, indent=2)}\n\n"
        "Return ONLY the corrected JSON."
    )

    fixed = call_llm_json(
        client, model,
        "You fix JSON structure errors in protocol definitions. Return only valid JSON.",
        fix_prompt,
        temperature=0.0,
    )
    return fixed if fixed.get("steps") else protocol
