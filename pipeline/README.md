# Protocol Ingestion Pipeline

Automatically converts emergency protocol PDFs into the structured JSON formats used by the VR training engine:

1. **Protocol Tree** (`protocol_id.json`) — step graph with decisions, constraints, and effects
2. **RAG Knowledge Base** (`protocol_id_kb.json`) — searchable chunks for evidence-grounded LLM responses

## Architecture

```
PDF(s)
  │
  ▼
┌──────────────┐
│  extract.py  │  pdfplumber → raw text + sections
└──────┬───────┘
       │
       ▼
┌────────────────┐
│  structure.py  │  GPT-4o → protocol tree JSON (two-pass: generate + validate)
└──────┬─────────┘
       │
       ▼
┌──────────────────┐
│  kb_generator.py │  GPT-4o → knowledge base chunks
└──────┬───────────┘
       │
       ▼
┌────────────────┐
│  validate.py   │  Schema + cross-reference validation
└──────┬─────────┘
       │
       ▼
  Output JSON files
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r pipeline/requirements.txt
```

### 2. Set your OpenAI API key

```bash
# .env in project root
OPENAI_API_KEY=sk-...
```

### 3a. Run via Web UI (recommended)

```bash
python -m uvicorn pipeline.web.server:app --reload --port 8001
```

Open http://localhost:8001 — two panels:

- **PDF → JSON**: Upload PDFs, pick a model, hit "Run Pipeline". Progress streams in real time via SSE. Download the generated protocol + KB JSONs when done.
- **Tree Visualizer**: Upload/paste any protocol JSON to inspect the step graph, constraints, actions, and validation results. Click a node for details.

### 3b. Run via CLI

```bash
# Single PDF
python -m pipeline path/to/evacuation_sop.pdf

# Multiple PDFs (merged into one protocol)
python -m pipeline chapter1.pdf chapter2.pdf appendix.pdf

# Specify output directory
python -m pipeline protocol.pdf --output ./my_output

# Use a cheaper model
python -m pipeline protocol.pdf --model gpt-4o-mini

# Extract only (no LLM calls) — for inspecting parsed sections
python -m pipeline protocol.pdf --extract-only
```

### 4. Copy results to the trainer

```bash
copy pipeline_output\<protocol_id>.json trainer\protocols\
copy pipeline_output\<protocol_id>_kb.json trainer\knowledge_base\
```

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `pdfs` (positional) | required | One or more PDF file paths |
| `--output`, `-o` | `./pipeline_output` | Output directory |
| `--model`, `-m` | `gpt-4o` | OpenAI model for extraction |
| `--extract-only` | off | Skip LLM calls, only extract/save text |
| `--name` | auto-detected | Protocol name (useful for multi-PDF merge) |

## Output Files

The pipeline creates these files in the output directory:

| File | Description |
|------|-------------|
| `extracted_N.txt` | Raw extracted text per PDF (for debugging) |
| `<protocol_id>.json` | Structured protocol tree |
| `<protocol_id>_kb.json` | RAG knowledge base |

## Pipeline Stages

### 1. PDF Extraction (`extract.py`)

Uses **pdfplumber** to extract:
- Raw text preserving reading order
- Sections detected via heading patterns (numbered, ALL-CAPS, etc.)
- Tables converted to text

### 2. Protocol Tree Generation (`structure.py`)

**Two-pass LLM approach** using GPT-4o:

- **Pass 1**: Extracts the full protocol structure — steps (sequential + decision), global constraints, possible actions, and metadata
- **Pass 2**: Validates the structure—checks BFS reachability from the start step, verifies references, and asks the LLM to fix any issues

The LLM is given a detailed schema description with 13 extraction rules covering step types, branching logic, effects, and constraint relationships.

### 3. Knowledge Base Generation (`kb_generator.py`)

Creates searchable chunks for RAG retrieval:
- Each chunk tagged with `step_ref` and `constraint_ref` IDs
- Chunks cover: step procedures, decision rationale, constraint details, safety warnings, general background
- Cross-references validated against the protocol tree

### 4. Validation (`validate.py`)

Two-stage validation:

**Protocol validation:**
- Required top-level keys
- Step schema completeness (id, type, description, effects, transitions)
- Start step existence
- BFS reachability (all steps reachable from start)
- Terminal steps have no `next`/`branches`
- All `possible_actions` reference existing steps

**KB validation:**
- Chunk schema completeness (id, type, content, tags)
- All `step_ref` / `constraint_ref` values match protocol IDs
- Coverage check — warns about steps/constraints without KB entries

## How It Handles Complex Documents

- **Long PDFs**: Sections are processed in batches to stay within token limits
- **Multiple PDFs**: Each PDF is extracted independently, then the LLM merges all sections into one unified protocol tree
- **Tables**: Converted to text format automatically
- **Decision points**: The LLM identifies conditional branches (e.g., "if route blocked → seek alternate exit") and creates decision-type steps with branches

## Customization

The extraction rules are defined as constants in `structure.py` (`PROTOCOL_SCHEMA_DESCRIPTION`) and `kb_generator.py` (`KB_SCHEMA_DESCRIPTION`). Edit these to adjust:
- How steps are categorized
- What metadata is extracted per step
- How KB chunks are typed and tagged
- Minimum/maximum granularity

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `pdfplumber` can't read PDF | Try converting to PDF/A first, or check if the PDF has selectable text (not scanned images) |
| LLM returns invalid JSON | Pipeline will retry with validation pass; if it persists, try `gpt-4o` instead of cheaper models |
| Validation errors after generation | Review `extracted_N.txt` to check if sections were parsed correctly |
| Missing sections | Check if the PDF uses image-based headers — pdfplumber only extracts text |
