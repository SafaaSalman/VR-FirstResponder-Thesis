"""
Knowledge base chunk generator.

Takes the extracted document sections + the generated protocol tree
and produces RAG knowledge base chunks in the format the trainer expects.

For small documents: single LLM call.
For large documents: processes sections in batches, each batch generating
chunks, then merges and deduplicates.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List

from openai import OpenAI

from .extract import ExtractedDocument, Section
from .llm_utils import call_llm_json, count_tokens, tpm_pace
from .config import PipelineConfig, get_config

logger = logging.getLogger("pipeline.kb")

# ── Legacy constants (resolved from PipelineConfig at import time) ───────
_cfg = get_config()
MAX_SINGLE_PASS_TOKENS = _cfg.max_single_pass_tokens
KB_BATCH_TOKENS = _cfg.kb_batch_tokens
OVERLAP_SECTIONS = _cfg.overlap_sections


KB_SCHEMA_DESCRIPTION = """
You are a knowledge-base engineer for an emergency-response training
system.  Given the source protocol text and a structured protocol tree,
produce a JSON knowledge base of RAG-retrieval chunks.

The JSON must conform to this structure:

{
  "protocol_id": "<must match the protocol tree's protocol_id>",
  "description": "<One sentence describing this KB>",
  "chunks": [
    {
      "chunk_id": "kb_001",
      "title": "<Short descriptive title for this chunk>",
      "text": "<Self-contained paragraph (3-8 sentences) of protocol
               knowledge.  Must be factually grounded in the source
               text — do NOT invent details.  Written in instructive
               tone, suitable for quoting to a trainee.>",
      "related_steps": ["<step_id>", ...],
      "tags": ["<tag1>", "<tag2>", ...],
      "related_constraints": ["<constraint_id>"],    // optional
      "related_actions": ["<forbidden_action_id>"]   // optional
    }
  ]
}

CHUNK CREATION RULES:
1.  Every protocol step must be covered by AT LEAST one chunk.
2.  Every global constraint must have its own dedicated chunk explaining
    WHY it is forbidden and what the safety consequences are.
3.  Chunks should be 3-8 sentences — long enough to be useful as
    evidence, short enough for embedding retrieval.
4.  Each chunk must be SELF-CONTAINED: a reader should understand it
    without seeing other chunks.
5.  Use the original protocol text as the primary source.  You may
    lightly rephrase for clarity but do NOT invent new requirements.
6.  Tags should include the phase, relevant hazards, and whether the
    chunk is "critical" or "safety"-related.
7.  related_steps must reference valid step IDs from the protocol tree.
8.  Chunk IDs must be sequential: kb_001, kb_002, kb_003, ...
9.  Aim for roughly 1-2 chunks per step + 1 per constraint.
    More complex steps may warrant 2 chunks (procedure + rationale).
10. Include cross-references where chunks relate to multiple steps.
"""


def generate_knowledge_base(
    doc: ExtractedDocument,
    protocol: dict,
    client: OpenAI,
    model: str = "gpt-4o",
    progress: Callable[[str], None] | None = None,
    checkpoint_dir: Path | None = None,
) -> dict:
    """Generate RAG knowledge base chunks from document + protocol tree.

    For small documents: single LLM call.
    For large documents: batched processing with merge.
    """
    _log = progress or (lambda msg: logger.info(msg))

    protocol_summary = _format_protocol_summary(protocol)
    protocol_id = protocol.get("protocol_id", "unknown")

    # Determine if we need batching
    sections = doc.sections if doc.sections else _fake_sections(doc.raw_text)
    total_text = _format_source_text_from_sections(sections)
    total_tokens = count_tokens(total_text)

    # Account for protocol summary + system prompt overhead in the
    # single-pass check — the actual LLM prompt includes these on top
    # of the source text.  Also respect the TPM limit.
    cfg = get_config()
    proto_overhead = count_tokens(protocol_summary) + 1_000  # ~1K for system + wrappers
    effective_single_pass = MAX_SINGLE_PASS_TOKENS
    if cfg.tpm_limit > 0:
        # The prompt must fit entirely under the TPM limit
        effective_single_pass = min(
            effective_single_pass,
            int(cfg.tpm_limit * 0.75) - proto_overhead,
        )

    if total_tokens <= effective_single_pass:
        # ── Small document: single pass ────────────────────────────
        _log(f"Document is {total_tokens:,} tokens — fits in single pass")
        return _generate_kb_single(total_text, protocol_summary, protocol, client, model, _log)
    else:
        # ── Large document: batched processing ─────────────────────
        _log(f"Document is {total_tokens:,} tokens — using batched KB generation...")

        # Cap the budget so the full request (sections + protocol
        # summary + system prompt + output) stays under the TPM limit.
        cfg = get_config()
        effective_budget = KB_BATCH_TOKENS
        if cfg.tpm_limit > 0:
            proto_overhead = count_tokens(protocol_summary)
            # Reserve ~35 % of remaining TPM for other prompt overhead
            tpm_budget = int((cfg.tpm_limit - proto_overhead) * 0.65)
            effective_budget = min(effective_budget, max(tpm_budget, 2_000))
            if effective_budget < KB_BATCH_TOKENS:
                _log(f"TPM limit {cfg.tpm_limit:,} → capping KB batch "
                     f"budget to {effective_budget:,} tokens")

        batches = _split_into_batches(sections, effective_budget)
        _log(f"Split into {len(batches)} batches")

        # Checkpoint support
        ckpt_subdir = (checkpoint_dir / "checkpoints") if checkpoint_dir else None
        if ckpt_subdir:
            ckpt_subdir.mkdir(parents=True, exist_ok=True)

        all_chunks = []
        for i, batch in enumerate(batches):
            ckpt_file = ckpt_subdir / f"kb_batch_{i+1:03d}.json" if ckpt_subdir else None

            # Resume: load from checkpoint if it exists
            if ckpt_file and ckpt_file.exists():
                import json as _json
                batch_chunks = _json.loads(ckpt_file.read_text(encoding="utf-8"))
                _log(f"KB batch {i+1}/{len(batches)} loaded from checkpoint "
                     f"({len(batch_chunks)} chunks)")
            else:
                batch_text = _format_source_text_from_sections(batch)
                batch_tokens = count_tokens(batch_text)
                _log(f"Processing KB batch {i+1}/{len(batches)} "
                     f"({batch_tokens:,} tokens, {len(batch)} sections)...")

                batch_kb = _generate_kb_single(
                    batch_text, protocol_summary, protocol, client, model, _log,
                    batch_hint=f"This is batch {i+1} of {len(batches)} from a large document. "
                               f"Generate chunks ONLY for the content in THIS batch. "
                               f"Other batches will cover other sections."
                )

                batch_chunks = batch_kb.get("chunks", [])
                _log(f"  → batch {i+1}: {len(batch_chunks)} chunks")

                # Save checkpoint
                if ckpt_file:
                    import json as _json
                    ckpt_file.write_text(
                        _json.dumps(batch_chunks, indent=2, ensure_ascii=False),
                        encoding="utf-8",
                    )
                    logger.debug("Saved KB checkpoint: %s", ckpt_file)

                # Pace sequential calls so we don't exceed the TPM quota
                tpm_pace(batch_tokens)

            all_chunks.extend(batch_chunks)

        # ── Merge & deduplicate ────────────────────────────────────
        _log(f"Merging {len(all_chunks)} chunks from {len(batches)} batches...")
        merged_chunks = _merge_and_renumber(all_chunks)
        _log(f"After merge: {len(merged_chunks)} chunks")

        # ── Coverage check: ensure all steps/constraints covered ───
        covered_steps = set()
        covered_constraints = set()
        for c in merged_chunks:
            covered_steps.update(c.get("related_steps", []))
            covered_constraints.update(c.get("related_constraints", []))

        all_steps = {s["id"] for s in protocol.get("steps", [])}
        all_constraints = {c["id"] for c in protocol.get("global_constraints", [])}
        missing_steps = all_steps - covered_steps
        missing_constraints = all_constraints - covered_constraints

        if missing_steps or missing_constraints:
            _log(f"Coverage gaps: {len(missing_steps)} steps, "
                 f"{len(missing_constraints)} constraints uncovered — "
                 f"generating source-grounded fill-in chunks...")
            fill_chunks = _generate_coverage_fill(
                missing_steps, missing_constraints, protocol,
                sections, client, model, len(merged_chunks),
                progress=_log,
            )
            merged_chunks.extend(fill_chunks)
            n_grounded = sum(1 for c in fill_chunks if c.get("source_grounded", True))
            n_ungrounded = len(fill_chunks) - n_grounded
            _log(f"Added {len(fill_chunks)} fill-in chunks "
                 f"({n_grounded} grounded, {n_ungrounded} no-source) → "
                 f"total: {len(merged_chunks)}")

        kb = {
            "protocol_id": protocol_id,
            "description": f"Knowledge base for {protocol.get('title', protocol_id)}",
            "chunks": merged_chunks,
        }

        kb = _validate_references(kb, protocol, _log)
        return kb


def generate_kb_from_multiple(
    docs: list[ExtractedDocument],
    protocol: dict,
    client: OpenAI,
    model: str = "gpt-4o",
    progress: Callable[[str], None] | None = None,
    checkpoint_dir: Path | None = None,
) -> dict:
    """Generate KB from multiple source documents + one protocol tree."""
    # Collect all sections with source attribution
    all_sections = []
    for doc in docs:
        for s in doc.sections:
            tagged = Section(
                heading=f"[{doc.title}] {s.heading}",
                text=s.text,
                page_numbers=s.page_numbers,
                level=s.level,
            )
            all_sections.append(tagged)

    merged_doc = ExtractedDocument(
        source_path=", ".join(d.source_path for d in docs),
        title=docs[0].title,
        raw_text="",
        sections=all_sections,
        page_count=sum(d.page_count for d in docs),
    )

    return generate_knowledge_base(merged_doc, protocol, client, model, progress,
                                    checkpoint_dir=checkpoint_dir)


# ── Private helpers ────────────────────────────────────────────────────────

def _generate_kb_single(
    source_text: str,
    protocol_summary: str,
    protocol: dict,
    client: OpenAI,
    model: str,
    _log: Callable[[str], None],
    batch_hint: str = "",
) -> dict:
    """Single-pass KB generation from source text."""
    system_msg = KB_SCHEMA_DESCRIPTION
    if batch_hint:
        system_msg += f"\n\nIMPORTANT: {batch_hint}"

    # Overlap-awareness instruction
    if "[OVERLAP" in source_text:
        system_msg += (
            "\n\nIMPORTANT: Sections marked [OVERLAP \u2014 context from previous "
            "batch] are for context continuity.  Only generate chunks for "
            "content NOT marked as overlap."
        )

    user_msg = (
        f"PROTOCOL TREE (for reference — use step IDs and constraint IDs from here):\n"
        f"{protocol_summary}\n\n"
        f"SOURCE DOCUMENT TEXT:\n{source_text}\n\n"
        "Now produce the knowledge base JSON.  Return ONLY valid JSON, "
        "no markdown fences, no commentary."
    )

    return call_llm_json(
        client, model, system_msg, user_msg,
        temperature=get_config().temperature_kb, progress=_log,
    )


def _split_into_batches(
    sections: list[Section],
    max_tokens: int,
    overlap: int = OVERLAP_SECTIONS,
) -> list[list[Section]]:
    """Split sections into batches by **token** budget.

    Successive batches include the last *overlap* sections of the previous
    batch (with headings prefixed ``[OVERLAP — context from previous batch]``)
    so that procedures spanning a boundary are not cut in half.
    """
    # --- first pass: pack sections into raw batches (no overlap) ---
    raw_batches: list[list[Section]] = []
    current: list[Section] = []
    current_tokens = 0
    for s in sections:
        sec_tokens = count_tokens(s.heading + "\n" + s.text)
        if current_tokens + sec_tokens > max_tokens and current:
            raw_batches.append(current)
            current = []
            current_tokens = 0
        current.append(s)
        current_tokens += sec_tokens
    if current:
        raw_batches.append(current)

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
    """Split raw text into synthetic sections."""
    sections = []
    for i in range(0, len(raw_text), chunk_size):
        sections.append(Section(
            heading=f"Block {i // chunk_size + 1}",
            text=raw_text[i:i + chunk_size],
            page_numbers=[],
            level=1,
        ))
    return sections


def _format_source_text_from_sections(sections: list[Section]) -> str:
    """Format sections for LLM consumption."""
    return "\n\n".join(f"### {s.heading}\n{s.text}" for s in sections)


def _merge_and_renumber(chunks: list[dict]) -> list[dict]:
    """Merge chunks from multiple batches, deduplicate, and renumber."""
    # Simple deduplication: if two chunks have the same related_steps
    # and very similar titles, keep only the longer one
    seen = {}
    unique = []

    for chunk in chunks:
        key = (
            tuple(sorted(chunk.get("related_steps", []))),
            chunk.get("title", "").lower().strip()[:50],
        )
        if key in seen:
            # Keep the longer text
            existing = seen[key]
            if len(chunk.get("text", "")) > len(existing.get("text", "")):
                unique[unique.index(existing)] = chunk
                seen[key] = chunk
        else:
            seen[key] = chunk
            unique.append(chunk)

    # Renumber sequentially
    for i, chunk in enumerate(unique, 1):
        chunk["chunk_id"] = f"kb_{i:03d}"

    return unique


def _generate_coverage_fill(
    missing_steps: set,
    missing_constraints: set,
    protocol: dict,
    source_sections: list[Section],
    client: OpenAI,
    model: str,
    existing_count: int,
    progress: Callable[[str], None] | None = None,
) -> list[dict]:
    """Generate source-grounded chunks for steps/constraints not covered.

    For each uncovered item, searches the source sections by keyword
    relevance and includes the best-matching excerpts in the prompt so
    the LLM can ground its output in real document text.

    Each returned chunk includes a ``source_grounded`` boolean:
    - ``True``  → chunk text is grounded in source excerpts
    - ``False`` → no relevant source text was found; chunk is flagged
    """
    _log = progress or (lambda msg: None)
    step_map = {s["id"]: s for s in protocol.get("steps", [])}
    constraint_map = {c["id"]: c for c in protocol.get("global_constraints", [])}

    # ── Build items list with matched source text ──────────────────
    items_with_sources: list[dict] = []

    for sid in missing_steps:
        step = step_map.get(sid, {})
        description = step.get("description", "")
        relevant = _find_relevant_sections(description, source_sections, top_k=5)
        items_with_sources.append({
            "type": "step",
            "id": sid,
            "description": description,
            "phase": step.get("phase", "unknown"),
            "source_excerpts": relevant,
        })

    for cid in missing_constraints:
        constraint = constraint_map.get(cid, {})
        description = constraint.get("description", "")
        relevant = _find_relevant_sections(description, source_sections, top_k=5)
        items_with_sources.append({
            "type": "constraint",
            "id": cid,
            "description": description,
            "source_excerpts": relevant,
        })

    if not items_with_sources:
        return []

    # ── Format items + source excerpts for the prompt ──────────────
    items_text_parts = []
    for item in items_with_sources:
        label = f"{item['type'].title()} '{item['id']}'"
        if item["type"] == "step":
            label += f" (phase: {item.get('phase', 'unknown')})"
        header = f"- {label}: {item['description']}"

        if item["source_excerpts"]:
            excerpts = "\n".join(
                f"    [{s['heading']}] {s['text'][:600]}"
                for s in item["source_excerpts"]
            )
            header += f"\n  SOURCE EXCERPTS:\n{excerpts}"
        else:
            header += "\n  SOURCE EXCERPTS: NONE FOUND"

        items_text_parts.append(header)

    items_text = "\n\n".join(items_text_parts)
    n_with_source = sum(1 for i in items_with_sources if i["source_excerpts"])
    _log(f"  Found source text for {n_with_source}/{len(items_with_sources)} uncovered items")

    system_msg = KB_SCHEMA_DESCRIPTION + (
        "\n\nYou are generating FILL-IN chunks for protocol items that "
        "weren't covered by previous batched passes.\n\n"
        "CRITICAL GROUNDING RULES:\n"
        "- Ground ALL chunk text in the provided SOURCE EXCERPTS.\n"
        "- Do NOT invent, assume, or fabricate any protocol details.\n"
        "- If source excerpts are provided, base the chunk text on them.\n"
        "- If SOURCE EXCERPTS say 'NONE FOUND', create a chunk with this "
        "exact text: 'No specific guidance found in source documents for "
        "this step \u2014 refer to general protocol procedures.' and include "
        "'no_source' in the tags array.\n"
        "- Add a \"source_grounded\" field (boolean) to EVERY chunk:\n"
        "  \u2022 true  \u2192 chunk is based on source excerpts\n"
        "  \u2022 false \u2192 no source text was found (no_source tag)"
    )

    user_msg = (
        f"PROTOCOL ID: {protocol.get('protocol_id')}\n\n"
        f"ITEMS NEEDING COVERAGE (with source excerpts):\n\n"
        f"{items_text}\n\n"
        f"Generate a KB JSON with chunks covering these items. "
        f"Start chunk IDs from kb_{existing_count + 1:03d}. "
        f"Return ONLY valid JSON."
    )

    raw = call_llm_json(
        client, model, system_msg, user_msg,
        temperature=get_config().temperature_kb, progress=_log,
    )

    # Pace after the coverage-fill LLM call to respect TPM limits
    fill_tokens = count_tokens(system_msg + user_msg)
    tpm_pace(fill_tokens)

    chunks = raw.get("chunks", [])

    # ── Ensure source_grounded field is present on every chunk ─────
    for chunk in chunks:
        if "source_grounded" not in chunk:
            # Infer from tags: if 'no_source' tag present → not grounded
            tags = [t.lower() for t in chunk.get("tags", [])]
            chunk["source_grounded"] = "no_source" not in tags

    return chunks


def _find_relevant_sections(
    description: str,
    sections: list[Section],
    top_k: int = 5,
) -> list[dict]:
    """Find the most relevant source sections for a step/constraint description.

    Uses keyword matching: extracts significant words from the description,
    scores each section by how many keywords appear in its heading + text,
    and returns the top-k highest-scoring sections.
    """
    if not description or not sections:
        return []

    # Extract keywords: words ≥ 3 chars, lowered, excluding stop words
    stop_words = {
        "the", "and", "for", "are", "but", "not", "you", "all", "can",
        "has", "her", "was", "one", "our", "out", "day", "had", "his",
        "how", "its", "may", "new", "now", "old", "see", "way", "who",
        "did", "get", "let", "say", "she", "too", "use", "that", "this",
        "with", "have", "from", "they", "been", "said", "each", "make",
        "like", "than", "them", "then", "when", "will", "about", "which",
        "their", "there", "these", "other", "into", "could", "after",
        "should", "would", "must", "step", "action", "perform", "ensure",
        "check", "verify", "complete", "begin", "start", "proceed",
    }

    words = re.findall(r"[a-z]{3,}", description.lower())
    keywords = [w for w in words if w not in stop_words]

    if not keywords:
        # Fallback: use all words ≥ 4 chars
        keywords = [w for w in words if len(w) >= 4]

    if not keywords:
        return []

    # Score each section
    scored: list[tuple[int, int, dict]] = []
    for idx, section in enumerate(sections):
        searchable = (section.heading + " " + section.text).lower()
        score = sum(1 for kw in keywords if kw in searchable)
        if score > 0:
            scored.append((score, idx, {
                "heading": section.heading,
                "text": section.text,
            }))

    # Sort by score descending, then by document order
    scored.sort(key=lambda x: (-x[0], x[1]))

    return [item[2] for item in scored[:top_k]]


def _format_protocol_summary(protocol: dict) -> str:
    """Create a compact protocol summary for the LLM."""
    summary = {
        "protocol_id": protocol.get("protocol_id"),
        "title": protocol.get("title"),
        "steps": [
            {"id": s["id"], "description": s["description"], "phase": s.get("phase")}
            for s in protocol.get("steps", [])
        ],
        "global_constraints": [
            {"id": c["id"], "description": c["description"]}
            for c in protocol.get("global_constraints", [])
        ],
    }
    return json.dumps(summary, indent=2)


def _validate_references(
    kb: dict,
    protocol: dict,
    progress: Callable[[str], None] | None = None,
) -> dict:
    """Ensure all step/constraint references in KB chunks are valid."""
    _log = progress or (lambda msg: None)
    valid_steps = {s["id"] for s in protocol.get("steps", [])}
    valid_constraints = {c["id"] for c in protocol.get("global_constraints", [])}

    issues = []
    for chunk in kb.get("chunks", []):
        # Fix related_steps
        bad_steps = [s for s in chunk.get("related_steps", []) if s not in valid_steps]
        if bad_steps:
            issues.append(f"Chunk {chunk['chunk_id']}: invalid steps {bad_steps}")
            chunk["related_steps"] = [s for s in chunk["related_steps"] if s in valid_steps]

        # Fix related_constraints
        bad_constraints = [c for c in chunk.get("related_constraints", []) if c not in valid_constraints]
        if bad_constraints:
            issues.append(f"Chunk {chunk['chunk_id']}: invalid constraints {bad_constraints}")
            chunk["related_constraints"] = [c for c in chunk["related_constraints"] if c in valid_constraints]

    if issues:
        _log(f"Fixed {len(issues)} invalid references in KB chunks")
        logger.warning("Fixed %d invalid references in KB chunks", len(issues))
        for issue in issues[:5]:
            logger.debug("  %s", issue)
    else:
        _log("✓ All KB references valid")
        logger.info("All KB references valid")

    # Ensure protocol_id matches
    kb["protocol_id"] = protocol.get("protocol_id", kb.get("protocol_id"))

    return kb
