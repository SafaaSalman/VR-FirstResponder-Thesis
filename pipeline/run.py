"""
Pipeline orchestrator and CLI.

Usage:
    # Single PDF
    python -m pipeline path/to/protocol.pdf

    # Multiple PDFs (merged into one protocol)
    python -m pipeline doc1.pdf doc2.pdf doc3.pdf

    # Specify output directory
    python -m pipeline protocol.pdf --output ./output

    # Use a specific model
    python -m pipeline protocol.pdf --model gpt-4o-mini

    # Dry run (extract only, no LLM calls)
    python -m pipeline protocol.pdf --extract-only
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from .extract import extract_pdf, extract_multiple_pdfs, ExtractedDocument
from .structure import generate_protocol_tree, generate_protocol_from_multiple
from .kb_generator import generate_knowledge_base, generate_kb_from_multiple
from .validate import validate_protocol, validate_knowledge_base
from .config import PipelineConfig, get_config

logger = logging.getLogger("pipeline.run")


def _cleanup_checkpoints(output_path: Path) -> None:
    """Remove the checkpoints sub-directory after a successful run."""
    ckpt_dir = output_path / "checkpoints"
    if ckpt_dir.exists():
        shutil.rmtree(ckpt_dir, ignore_errors=True)
        logger.info("Cleaned up checkpoint directory: %s", ckpt_dir)


def run_pipeline(
    pdf_paths: list[str],
    output_dir: str = "./output",
    model: str | None = None,
    extract_only: bool = False,
    protocol_name: str | None = None,
    resume: bool = False,
    config: PipelineConfig | None = None,
) -> dict:
    """Run the full ingestion pipeline.

    If *resume* is ``True``, previously completed stages (extraction,
    protocol generation, KB batch results) are loaded from disk instead
    of being regenerated.

    Returns a dict with 'protocol', 'knowledge_base', and 'validation'.
    """
    cfg = config or get_config()
    model = model or cfg.model
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Extract PDFs ───────────────────────────────────────
    logger.info("═══ STEP 1: PDF EXTRACTION ═══")

    existing_txts = sorted(output_path.glob("extracted_*.txt"))
    if resume and existing_txts:
        logger.info("Resume: found %d extracted text file(s) — skipping extraction",
                     len(existing_txts))
        # Re-extract anyway (cheap, local) so we have ExtractedDocument objects
        docs = extract_multiple_pdfs([Path(p) for p in pdf_paths])
    else:
        docs = extract_multiple_pdfs([Path(p) for p in pdf_paths])

    for doc in docs:
        logger.info("✓ %s — %d pages, %d sections", doc.title, doc.page_count, len(doc.sections))

    # Save extracted text
    for i, doc in enumerate(docs):
        txt_path = output_path / f"extracted_{i+1}.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"Source: {doc.source_path}\n")
            f.write(f"Title: {doc.title}\n")
            f.write(f"Pages: {doc.page_count}\n")
            f.write(f"Sections: {len(doc.sections)}\n\n")
            for s in doc.sections:
                f.write(f"{'#' * s.level} {s.heading}\n{s.text}\n\n")
        logger.info("Saved: %s", txt_path)

    if extract_only:
        logger.info("--extract-only: stopping after extraction.")
        return {"docs": [{"title": d.title, "sections": len(d.sections)} for d in docs]}

    # ── Step 2: Generate protocol tree ─────────────────────────────
    logger.info("═══ STEP 2: PROTOCOL TREE GENERATION ═══")
    load_dotenv()
    client = OpenAI()

    def _proto_log(msg: str):
        logger.info(msg)

    # Check for an existing protocol JSON when resuming
    existing_protocols = sorted(output_path.glob("*_v*.json"))
    # Filter out KB JSONs
    existing_protocols = [p for p in existing_protocols if "_kb" not in p.name]

    if resume and existing_protocols:
        protocol_path = existing_protocols[0]
        logger.info("Resume: loading existing protocol from %s", protocol_path)
        with open(protocol_path, "r", encoding="utf-8") as f:
            protocol = json.load(f)
    else:
        if len(docs) == 1:
            protocol = generate_protocol_tree(
                docs[0], client, model, progress=_proto_log,
                checkpoint_dir=output_path,
            )
        else:
            protocol = generate_protocol_from_multiple(
                docs, client, model, protocol_name, progress=_proto_log,
                checkpoint_dir=output_path,
            )

        # Save protocol
        protocol_id = protocol.get("protocol_id", "unknown_protocol")
        protocol_path = output_path / f"{protocol_id}.json"
        with open(protocol_path, "w", encoding="utf-8") as f:
            json.dump(protocol, f, indent=2, ensure_ascii=False)

    protocol_id = protocol.get("protocol_id", "unknown_protocol")
    protocol_path = output_path / f"{protocol_id}.json"
    # Ensure protocol is saved (idempotent)
    if not protocol_path.exists():
        with open(protocol_path, "w", encoding="utf-8") as f:
            json.dump(protocol, f, indent=2, ensure_ascii=False)

    logger.info("✓ Protocol saved: %s", protocol_path)
    logger.info("  Steps: %d", len(protocol.get('steps', [])))
    logger.info("  Constraints: %d", len(protocol.get('global_constraints', [])))
    logger.info("  Actions: %d", len(protocol.get('possible_actions', [])))

    # ── Step 3: Validate protocol ──────────────────────────────────
    logger.info("═══ STEP 3: PROTOCOL VALIDATION ═══")
    proto_validation = validate_protocol(protocol)
    logger.info(proto_validation.summary())

    # ── Step 4: Generate knowledge base ────────────────────────────
    logger.info("═══ STEP 4: KNOWLEDGE BASE GENERATION ═══")

    def _kb_log(msg: str):
        logger.info(msg)

    if len(docs) == 1:
        kb = generate_knowledge_base(docs[0], protocol, client, model, progress=_kb_log,
                                     checkpoint_dir=output_path)
    else:
        kb = generate_kb_from_multiple(docs, protocol, client, model, progress=_kb_log,
                                       checkpoint_dir=output_path)

    # Save KB
    kb_path = output_path / f"{protocol_id}_kb.json"
    with open(kb_path, "w", encoding="utf-8") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)
    logger.info("✓ KB saved: %s", kb_path)
    logger.info("  Chunks: %d", len(kb.get('chunks', [])))

    # ── Step 5: Validate knowledge base ────────────────────────────
    logger.info("═══ STEP 5: KNOWLEDGE BASE VALIDATION ═══")
    kb_validation = validate_knowledge_base(kb, protocol)
    logger.info(kb_validation.summary())

    # ── Summary ────────────────────────────────────────────────────
    logger.info("═══ PIPELINE COMPLETE ═══")
    logger.info("Protocol: %s", protocol_path)
    logger.info("KB:       %s", kb_path)
    if proto_validation.errors or kb_validation.errors:
        logger.warning("There were validation errors — review output before using.")
    else:
        logger.info("✓ All validations passed.")

    logger.info("To use with the trainer, copy files to:")
    logger.info("  %s  →  trainer/protocols/", protocol_path)
    logger.info("  %s  →  trainer/knowledge_base/", kb_path)

    # ── Cleanup checkpoints after successful completion ───────────
    _cleanup_checkpoints(output_path)

    return {
        "protocol": protocol,
        "knowledge_base": kb,
        "protocol_path": str(protocol_path),
        "kb_path": str(kb_path),
        "validation": {
            "protocol": {
                "ok": proto_validation.ok,
                "errors": proto_validation.errors,
                "warnings": proto_validation.warnings,
            },
            "kb": {
                "ok": kb_validation.ok,
                "errors": kb_validation.errors,
                "warnings": kb_validation.warnings,
            },
        },
    }


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        description="Protocol Ingestion Pipeline — PDF → Protocol Tree + RAG KB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m pipeline evacuation_sop.pdf\n"
            "  python -m pipeline doc1.pdf doc2.pdf --output ./my_protocol\n"
            "  python -m pipeline protocol.pdf --extract-only\n"
            "  python -m pipeline protocol.pdf --model gpt-4o-mini\n"
        ),
    )
    parser.add_argument(
        "pdfs",
        nargs="+",
        help="One or more PDF file paths to process",
    )
    parser.add_argument(
        "--output", "-o",
        default="./pipeline_output",
        help="Output directory (default: ./pipeline_output)",
    )
    parser.add_argument(
        "--model", "-m",
        default=None,
        help="OpenAI model to use (default: from config, typically gpt-4o)",
    )
    parser.add_argument(
        "--extract-only",
        action="store_true",
        help="Only extract PDF text, skip LLM calls",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Protocol name (for multi-PDF merge)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume a previous run — skip completed stages and reuse checkpoints",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to a YAML configuration file (overrides defaults)",
    )

    args = parser.parse_args()

    # Build configuration (YAML → env → CLI overrides)
    cfg = get_config(yaml_path=args.config)
    # CLI --model takes precedence over config file
    model = args.model or cfg.model

    # Validate inputs
    for pdf in args.pdfs:
        if not Path(pdf).exists():
            logger.error("File not found: %s", pdf)
            sys.exit(1)

    result = run_pipeline(
        pdf_paths=args.pdfs,
        output_dir=args.output,
        model=model,
        extract_only=args.extract_only,
        protocol_name=args.name,
        resume=args.resume,
        config=cfg,
    )

    if not args.extract_only:
        validation = result.get("validation", {})
        if validation.get("protocol", {}).get("errors") or validation.get("kb", {}).get("errors"):
            sys.exit(1)


if __name__ == "__main__":
    main()
