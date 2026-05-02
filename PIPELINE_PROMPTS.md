# Pipeline Hardening Prompts — Copy & Paste One at a Time

These prompts fix the reliability, correctness, and quality issues identified
in the data-pipeline code review.  Work through them **in order** — each builds
on the previous.

> **Goal:** The pipeline processes real emergency-protocol PDFs (100+ pages each)
> and produces a protocol tree + RAG knowledge base.  These are safety protocols —
> **nothing may be invented or hallucinated**.  Every output must be traceable to
> the source PDF text.

---

## PROMPT 1 — API Retry + JSON Recovery (Critical Reliability)

```
You are a Senior Data Engineer hardening pipeline/structure.py and 
pipeline/kb_generator.py for production reliability.

PROBLEM:
Every OpenAI API call in the pipeline is a single unprotected
client.chat.completions.create() → json.loads() sequence.  If the API returns a
429 (rate-limit), 500 (server error), timeout, or malformed JSON (truncated
braces, trailing commas), the entire pipeline crashes and all previous work is
lost.  With batched processing making 10–20+ sequential calls per run, this
happens frequently.

REQUIREMENTS — implement ALL of these:

1. Add the `tenacity` library for retry:
   - Retry on openai.RateLimitError, openai.APITimeoutError,
     openai.APIConnectionError, openai.InternalServerError
   - Exponential backoff: wait 2^n seconds, min 1s, max 60s
   - Max 5 attempts per call
   - Log every retry via the progress callback (so the web UI shows it)

2. Add robust JSON parsing after every LLM response:
   - First try json.loads() as-is
   - If it fails, try stripping markdown fences (```json ... ```)
   - If it still fails, try a regex to extract the first { ... } block
   - If it STILL fails, make one "fix this JSON" retry call to the LLM
     with the broken output and ask it to return valid JSON
   - Only raise after all recovery attempts fail

3. Create a shared helper module pipeline/llm_utils.py containing:
   - call_llm_json(client, model, system, user, temperature, progress) → dict
     Wraps the retry + JSON recovery logic so every call site uses the
     same resilient pattern.
   - call_llm_text(client, model, system, user, temperature, progress) → str
     Same retry, no JSON parsing (for summarization calls).

4. Refactor ALL LLM calls in structure.py and kb_generator.py to use
   these helpers instead of raw client.chat.completions.create().

5. Add tenacity to pipeline/requirements.txt

6. After each LLM call, log token usage via the progress callback:
   progress(f"Tokens used: {response.usage.prompt_tokens} in / "
            f"{response.usage.completion_tokens} out")

Test: Verify all modules still import cleanly with:
  python -c "from pipeline.structure import generate_protocol_tree; 
             from pipeline.kb_generator import generate_knowledge_base; print('OK')"

Files to modify: pipeline/llm_utils.py (new), pipeline/structure.py,
pipeline/kb_generator.py, pipeline/requirements.txt
```

---

## PROMPT 2 — Fix Coverage-Fill Hallucination (Critical Correctness)

```
You are a Senior Data Engineer fixing a critical correctness bug in
pipeline/kb_generator.py.

PROBLEM:
The _generate_coverage_fill() function generates KB chunks for protocol steps
that weren't covered by the batched processing.  BUT it uses ONLY the step
descriptions from the protocol tree — it has NO access to the original source
document text.  This means these chunks are pure LLM hallucination.

This violates our core requirement: these are emergency protocols and we
CANNOT invent any information.  Every KB chunk MUST be traceable to source text.

Our own KB Schema Rule #5 says:
  "Use the original protocol text as the primary source.  Do NOT invent new
   requirements."

REQUIREMENTS — implement ALL of these:

1. Change _generate_coverage_fill() to accept the source document sections as
   a parameter (list[Section]).

2. For each uncovered step/constraint, search the source sections for relevant
   text:
   - Use keyword matching: extract key terms from the step description, search
     section headings and text for matches
   - Score each section by relevance (number of matching keywords)
   - Include the top 3-5 most relevant source sections in the prompt

3. Rewrite the fill prompt to:
   - Include the matched source text
   - Explicitly instruct: "Ground ALL chunk text in the provided source
     excerpts.  If no relevant source text exists for an item, create a
     chunk that says 'No specific guidance found in source documents for
     this step — refer to general protocol procedures.' and tag it with
     a 'no_source' tag."

4. Update the callers in generate_knowledge_base() to pass the source
   sections through to _generate_coverage_fill().

5. Add a "source_grounded": true/false field to each chunk in the coverage
   fill output so downstream systems know which chunks are fully grounded
   vs. flagged as missing-source.

Test: Verify imports work and the function signature is correct.

Files to modify: pipeline/kb_generator.py
```

---

## PROMPT 3 — Fix PDF Extraction Quality (High — Data Quality)

```
You are a Senior Data Engineer improving pipeline/extract.py to produce
higher-quality input for the LLM stages.

PROBLEMS IDENTIFIED:
A) page_numbers field in Section is never populated — we can't trace content
   back to source pages
B) ALL-CAPS heading regex is too aggressive — lines like "DO NOT USE ELEVATORS"
   trigger false heading breaks, creating hundreds of micro-sections from a
   632-page document
C) No detection of scanned/image-based PDFs — pdfplumber returns "" for
   image-only pages, and the pipeline silently produces zero content
D) Table text is often duplicated (extract_text includes it, then we append
   [TABLE] blocks on top)
E) No Unicode normalization — ligatures (fi → fi), soft hyphens, zero-width
   spaces cause downstream issues

REQUIREMENTS — fix ALL five issues:

1. PAGE NUMBERS — Track which pages each section spans:
   - Process text page-by-page instead of concatenating first
   - When splitting into sections, associate each section with its page range
   - Populate the page_numbers field in each Section

2. HEADING DETECTION — Reduce false positives for ALL-CAPS pattern:
   - Only match ALL-CAPS lines that are SHORT (≤ 80 chars)
   - Require ALL-CAPS lines to be preceded by a blank line or be at
     page start (not mid-paragraph)
   - Add a minimum body-text requirement: only create a new section if
     there's at least 50 chars of body text following the heading
     (otherwise merge with the previous section)
   - Use pdfplumber's character-level data to check font size when available:
     if a line's average font size is >20% larger than the body font, it's
     likely a heading regardless of case

3. SCANNED PDF DETECTION — After extraction:
   - Count pages where extract_text() returned "" or only whitespace
   - If >50% of pages are empty, log a WARNING: "PDF appears to be
     scanned/image-based ({n}/{total} pages empty). Consider running
     OCR first (e.g., ocrmypdf)."
   - Include the warning in the ExtractedDocument (add a `warnings` field)

4. TABLE DEDUPLICATION:
   - Check if table cell text already appears in the page's extract_text()
   - Only append [TABLE] block if it contains content NOT already in the
     extracted text (use a simple substring check on cell values)

5. UNICODE NORMALIZATION:
   - Apply unicodedata.normalize('NFKC', text) to all extracted text
   - Replace common PDF artifacts: soft hyphens → '', zero-width spaces → '',
     non-breaking spaces → regular spaces

Test: Run extraction on a real PDF to verify sections are reasonable:
  python -c "from pipeline.extract import extract_pdf; 
             doc = extract_pdf('path/to/test.pdf');
             print(f'{len(doc.sections)} sections, {doc.page_count} pages');
             for s in doc.sections[:10]: print(f'  p{s.page_numbers}: {s.heading}')"

Files to modify: pipeline/extract.py
```

---

## PROMPT 4 — Token-Aware Batching with tiktoken (High — Efficiency + Correctness)

```
You are a Senior Data Engineer replacing the character-based batch budgets in
pipeline/structure.py and pipeline/kb_generator.py with accurate token-based
budgets using tiktoken.

PROBLEM:
The pipeline uses character counts to estimate LLM capacity:
  - MAX_SINGLE_PASS_CHARS = 80,000 (~20K tokens)
  - SUMMARY_BATCH_CHARS = 50,000 (~12K tokens)
  - KB_BATCH_CHARS = 40,000 (~10K tokens)

But GPT-4o supports 128K tokens input (~500K chars).  The current budgets use
only ~15% of available context, creating 5-10x more batches than needed.
More batches = more API calls = slower, more expensive, more failure points,
more information lost at batch boundaries.

REQUIREMENTS:

1. Add tiktoken to pipeline/requirements.txt

2. Create token counting helpers in pipeline/llm_utils.py (or create it if
   Prompt 1 hasn't been done yet):
   - count_tokens(text: str, model: str = "gpt-4o") -> int
   - Split budgets should account for system prompt + user prompt overhead

3. Replace character-based constants with token-based ones:
   - MAX_SINGLE_PASS_TOKENS = 100_000  (leaves 28K for output + system prompt)
   - SUMMARY_BATCH_TOKENS = 90_000  (summaries are text-out, need less output room)
   - KB_BATCH_TOKENS = 80_000  (KB JSON output is larger)

4. Update _split_sections_into_batches() in structure.py and
   _split_into_batches() in kb_generator.py to use token counting
   instead of len().

5. Update the single-pass-vs-batch decision threshold in both
   generate_protocol_tree() and generate_knowledge_base() to use
   token counts.

6. Log the actual token counts in progress messages:
   "Document is 45,230 tokens — fits in single pass"
   "Batch 3/5: 18,400 tokens, 42 sections"

This should reduce a 12-batch run to 2-3 batches for typical documents,
cutting cost and time by 3-5x while improving quality (less context lost
at batch boundaries).

Test: Verify token counting works:
  python -c "from pipeline.llm_utils import count_tokens; 
             print(count_tokens('Hello world'))"

Files to modify: pipeline/llm_utils.py, pipeline/structure.py,
pipeline/kb_generator.py, pipeline/requirements.txt
```

---

## PROMPT 5 — Recursive Summarization (No More Truncation)

```
You are a Senior Data Engineer fixing a remaining truncation bug in
pipeline/structure.py.

PROBLEM:
In generate_protocol_tree(), after batch-summarizing all sections, the combined
summaries are concatenated.  If the total exceeds MAX_SINGLE_PASS_CHARS (or
MAX_SINGLE_PASS_TOKENS if Prompt 4 is done), the code TRUNCATES:

    if len(combined_summary) > MAX_SINGLE_PASS_CHARS:
        combined_summary = combined_summary[:MAX_SINGLE_PASS_CHARS] + \
            "\n\n[... additional summaries truncated ...]"

This re-introduces the original data-loss bug for very large documents
(e.g., 3 PDFs × 200 pages = 600+ pages where summaries alone exceed the limit).

REQUIREMENTS:

1. Replace truncation with RECURSIVE summarization:
   - If combined summaries exceed the single-pass budget, treat them as
     a new "document" and re-batch + re-summarize
   - Use a slightly different prompt for the second level:
     "These are SUMMARIES of procedural content from a large document.
      Consolidate them into a single comprehensive summary preserving
      ALL procedural steps, decisions, and constraints.  Do not drop
      any procedures."
   - Repeat recursion until the result fits (max 3 levels to prevent
     infinite loops)

2. Log each recursion level via the progress callback:
   "Level 1: 12 batches → 12 summaries (total: 150K chars)"
   "Level 2: re-summarizing 12 summaries in 2 batches..."
   "Level 2: combined: 70K chars — fits in single pass"

3. Add a safety check: if after 3 levels of recursion the text still
   doesn't fit, log a WARNING and proceed with truncation as last resort
   (but this should be nearly impossible in practice).

Files to modify: pipeline/structure.py
```

---

## PROMPT 6 — Replace print() with Python Logging (Medium — Observability)

```
You are a Senior Data Engineer adding proper logging to the pipeline.

PROBLEM:
Every module uses print() for output.  This means:
- Can't control verbosity (debug vs info vs warning)
- Can't route output to files for audit
- Can't suppress noise during testing
- Server.py progress callbacks and direct print() are mixed together
- _validate_references() in kb_generator.py prints directly, bypassing
  the progress callback system (messages lost in web UI)

REQUIREMENTS:

1. Add Python logging to every pipeline module:
   - pipeline/extract.py: logger = logging.getLogger("pipeline.extract")
   - pipeline/structure.py: logger = logging.getLogger("pipeline.structure")
   - pipeline/kb_generator.py: logger = logging.getLogger("pipeline.kb")
   - pipeline/validate.py: logger = logging.getLogger("pipeline.validate")
   - pipeline/run.py: logger = logging.getLogger("pipeline.run")
   - pipeline/web/server.py: logger = logging.getLogger("pipeline.server")

2. Replace ALL print() calls with appropriate log levels:
   - print("  ✓ ...") → logger.info(...)
   - print("  ⚠ ...") → logger.warning(...)
   - Error messages → logger.error(...)
   - Verbose/debug info → logger.debug(...)

3. Fix _validate_references() in kb_generator.py to use the progress
   callback instead of print().  Pass _log through from the caller.

4. In pipeline/run.py, configure the root logger at startup:
   logging.basicConfig(
       level=logging.INFO,
       format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
       datefmt="%H:%M:%S",
   )

5. In pipeline/web/server.py, set logging level to WARNING for console
   (since progress messages go through SSE, not logs).

6. Keep progress callback messages (the user-facing ones) distinct from
   logging — progress callbacks are for UI display, logging is for
   developer debugging.

Files to modify: pipeline/extract.py, pipeline/structure.py,
pipeline/kb_generator.py, pipeline/validate.py, pipeline/run.py,
pipeline/web/server.py
```

---

## PROMPT 7 — Batch Overlap + Boundary Awareness (Medium — Quality)

```
You are a Senior Data Engineer improving batch quality in pipeline/structure.py
and pipeline/kb_generator.py.

PROBLEM:
When sections are split into batches, a multi-paragraph procedure that spans
the batch boundary gets cut in half.  Neither batch has full context, so:
- Summarization misses half the procedure
- KB generation creates incomplete chunks

REQUIREMENTS:

1. Add OVERLAP to batch splitting in both _split_sections_into_batches()
   (structure.py) and _split_into_batches() (kb_generator.py):
   - Include the last 2 sections of the previous batch at the START of
     the next batch
   - Mark them clearly: prefix the heading with "[OVERLAP — context from
     previous batch]"
   - This costs ~5-10% extra tokens but prevents boundary data loss

2. In the summarization prompt (_summarize_batch in structure.py):
   - Add instruction: "Sections marked [OVERLAP] are provided for context
     only — do not re-summarize them, but use them to understand procedures
     that span batch boundaries."

3. In KB generation (_generate_kb_single in kb_generator.py):
   - Add instruction: "Sections marked [OVERLAP] are for context continuity.
     Only generate chunks for content NOT marked as overlap."

4. Add a unit test function (pipeline/tests/test_batching.py) that verifies:
   - 10 sections split into batches of 5 → batch 2 starts with sections 4,5
     from batch 1
   - Overlap sections are properly tagged
   - Single-batch case has no overlap

Files to modify: pipeline/structure.py, pipeline/kb_generator.py,
pipeline/tests/test_batching.py (new)
```

---

## PROMPT 8 — Validation Improvements (Medium — Correctness)

```
You are a Senior Data Engineer improving pipeline/validate.py.

PROBLEMS:
A) BFS uses list.pop(0) — O(n), should use collections.deque
B) No cycle detection — A→B→C→A loops aren't flagged
C) No duplicate-description detection (common LLM artifact)
D) KB chunk quality not assessed (no text length, no diversity check)

REQUIREMENTS:

1. Fix BFS to use collections.deque for O(1) popleft()

2. Add cycle detection:
   - During BFS, if we encounter a node already in the current path
     (not just visited), flag it as a cycle
   - Report: "Cycle detected: step_a → step_b → step_c → step_a"
   - This is an ERROR, not a warning (protocol is unresolvable)

3. Add duplicate-description detection:
   - If two or more steps have identical descriptions (after lowering
     and stripping whitespace), flag as WARNING
   - "Steps 'step_a' and 'step_b' have identical descriptions — possible
     LLM duplication artifact"

4. Add KB chunk quality checks in validate_knowledge_base():
   - Warn if chunk text < 100 chars (too thin to be useful)
   - Warn if chunk text > 2000 chars (too long for embedding retrieval)
   - Warn if two chunks have >90% word overlap (near-duplicates)
   - Count sentence count per chunk, warn if < 2 or > 10

5. Add a reachability check: verify that every non-terminal step has at
   least one path that eventually reaches a terminal step.  If a step
   leads to a dead-end (non-terminal step with empty allowed_next),
   flag as ERROR.

Files to modify: pipeline/validate.py
```

---

## PROMPT 9 — Intermediate Checkpointing (Medium — Cost Savings)

```
You are a Senior Data Engineer adding checkpointing to the pipeline so that
partial progress is saved and re-runnable.

PROBLEM:
If the pipeline fails at batch 8 of 12 during KB generation, all 7 successful
batches are lost.  The protocol tree (which took 10 minutes and $2 of API calls)
must be regenerated from scratch.

REQUIREMENTS:

1. In pipeline/run.py, add a --resume flag:
   - python -m pipeline docs/*.pdf --resume
   - If output directory already contains extracted_*.txt, skip extraction
   - If output directory contains a protocol JSON, skip protocol generation
   - If output directory contains a partial KB, resume from last batch

2. In pipeline/structure.py:
   - After each batch summary completes, save it to the output directory:
     output/checkpoints/summary_batch_001.txt, etc.
   - Before starting summarization, check if checkpoints exist and skip
     already-completed batches

3. In pipeline/kb_generator.py:
   - After each KB batch completes, save it to:
     output/checkpoints/kb_batch_001.json, etc.
   - On resume, load existing batch results and continue from next batch

4. Add a checkpoint_dir parameter to generate_protocol_tree() and
   generate_knowledge_base() (optional, defaults to None = no checkpointing)

5. In the web server, pass the job output directory as checkpoint_dir
   so web UI runs also benefit from checkpointing.

6. Add a cleanup step: after successful completion, delete checkpoint files
   (keep only final outputs).

Files to modify: pipeline/structure.py, pipeline/kb_generator.py,
pipeline/run.py, pipeline/web/server.py
```

---

## PROMPT 10 — Server Hardening (Medium — Production Safety)

```
You are a Senior Data Engineer hardening pipeline/web/server.py.

PROBLEMS:
A) No upload file size limit — users can upload multi-GB files
B) No job cleanup — jobs dict and temp files grow forever
C) Thread safety — _update_job() modifies shared dict from background thread
D) asyncio.get_event_loop() is deprecated
E) No concurrent job limit

REQUIREMENTS:

1. FILE SIZE LIMIT:
   - Add MAX_UPLOAD_SIZE = 50 * 1024 * 1024  (50MB per file)
   - Check each uploaded file's size in the /api/upload endpoint
   - Return 413 if exceeded

2. JOB CLEANUP:
   - Add a background task that runs every 30 minutes
   - Delete jobs older than 2 hours (both from jobs dict and disk)
   - Log cleanup: "Cleaned up {n} stale jobs"

3. THREAD SAFETY:
   - Add a threading.Lock for the jobs dict
   - Wrap _update_job() reads and writes in the lock
   - Ensure SSE streaming reads also acquire the lock

4. FIX DEPRECATION:
   - Replace asyncio.get_event_loop() with asyncio.get_running_loop()

5. CONCURRENT JOB LIMIT:
   - Max 3 simultaneous running jobs
   - If limit reached, return 429 with "Too many concurrent jobs"

6. Add a /api/health endpoint that returns:
   - Server uptime
   - Active job count
   - Total jobs processed

Files to modify: pipeline/web/server.py
```

---

## PROMPT 11 — Configuration System (Low — Maintainability)

```
You are a Senior Data Engineer creating a centralized configuration system
for the pipeline.

PROBLEM:
Batch sizes, model names, temperatures, timeouts, and thresholds are hardcoded
constants scattered across 4 different files.  Changing the model requires
editing multiple files.

REQUIREMENTS:

1. Create pipeline/config.py with a PipelineConfig dataclass:

   @dataclass
   class PipelineConfig:
       # LLM settings
       model: str = "gpt-4o"
       temperature_extract: float = 0.1
       temperature_summarize: float = 0.05
       temperature_kb: float = 0.15
       
       # Batch sizes (tokens if tiktoken available, else chars)
       max_single_pass_tokens: int = 100_000
       summary_batch_tokens: int = 90_000
       kb_batch_tokens: int = 80_000
       
       # Retry settings
       max_retries: int = 5
       retry_min_wait: float = 1.0
       retry_max_wait: float = 60.0
       
       # Server settings  
       max_upload_size_mb: int = 50
       max_concurrent_jobs: int = 3
       job_ttl_hours: int = 2

2. Support loading from environment variables:
   PIPELINE_MODEL=gpt-4o-mini overrides config.model

3. Support loading from a YAML file (optional):
   pipeline/config.yaml if it exists

4. Update ALL modules to import and use PipelineConfig instead of
   local constants.

5. Add a --config flag to the CLI:
   python -m pipeline docs/*.pdf --config custom_config.yaml

Files to create: pipeline/config.py
Files to modify: pipeline/structure.py, pipeline/kb_generator.py,
pipeline/run.py, pipeline/web/server.py
```

---

## PROMPT 12 — Unit Tests for Core Logic (Low — Quality Assurance)

```
You are a Senior Data Engineer adding unit tests for the pipeline's pure
functions that DON'T require LLM calls.

PROBLEM:
Zero test coverage.  Heading detection, section splitting, batch splitting,
JSON parsing, validation logic, merge/dedup are all highly testable pure
functions that have never been tested.

REQUIREMENTS:

Create pipeline/tests/__init__.py and the following test files:

1. pipeline/tests/test_extract.py:
   - Test _match_heading() with 10+ cases: numbered headings, ALL-CAPS,
     letter-numbered, non-headings, edge cases
   - Test _split_into_sections() with a sample multi-section text
   - Test _detect_title() with various first-page formats
   - Test that false-positive ALL-CAPS lines in body text aren't treated
     as headings

2. pipeline/tests/test_validate.py:
   - Test validate_protocol() with a valid protocol → no errors
   - Test with missing required keys → correct errors
   - Test with broken step references → correct errors
   - Test cycle detection (if Prompt 8 is done)
   - Test validate_knowledge_base() with valid KB
   - Test with missing coverage → correct warnings
   - Test BFS reachability with unreachable steps

3. pipeline/tests/test_batching.py:
   - Test _split_sections_into_batches() with various sizes
   - Test _split_into_batches() (kb version)
   - Test that no section is lost during splitting
   - Test edge cases: 1 section, empty sections, huge single section

4. pipeline/tests/test_merge.py:
   - Test _merge_and_renumber() with overlapping chunks
   - Test deduplication logic
   - Test renumbering is sequential

Run with: python -m pytest pipeline/tests/ -v

Add pytest to pipeline/requirements.txt

Files to create: pipeline/tests/__init__.py, pipeline/tests/test_extract.py,
pipeline/tests/test_validate.py, pipeline/tests/test_batching.py,
pipeline/tests/test_merge.py
Files to modify: pipeline/requirements.txt
```

---

## Execution Order Summary

| # | Prompt | Impact | Effort | Why this order |
|---|--------|--------|--------|----------------|
| 1 | API Retry + JSON Recovery | Critical | 1-2 hr | #1 runtime failure cause |
| 2 | Fix Coverage-Fill Hallucination | Critical | 30 min | Correctness — no invented content |
| 3 | Fix PDF Extraction Quality | High | 1-2 hr | Bad input → bad output |
| 4 | Token-Aware Batching | High | 1 hr | 3-5x fewer API calls |
| 5 | Recursive Summarization | High | 30 min | Eliminates last truncation path |
| 6 | Python Logging | Medium | 1 hr | Observability for all other fixes |
| 7 | Batch Overlap | Medium | 45 min | Quality at batch boundaries |
| 8 | Validation Improvements | Medium | 1 hr | Catch LLM output issues |
| 9 | Checkpointing | Medium | 1-2 hr | Save $ on long runs |
| 10 | Server Hardening | Medium | 1 hr | Production safety |
| 11 | Configuration System | Low | 1 hr | Maintainability |
| 12 | Unit Tests | Low | 1-2 hr | Regression prevention |
