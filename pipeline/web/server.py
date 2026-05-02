"""
Pipeline Web UI — FastAPI backend.

Upload PDFs → run pipeline → download JSONs
Upload protocol JSON → visualize tree

Start with:
    python -m uvicorn pipeline.web.server:app --reload --port 8001
"""

from __future__ import annotations

import asyncio
import json
import logging
import shutil
import tempfile
import threading
import time
import traceback
import uuid
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Server uses SSE for progress — keep console logging quiet
logging.getLogger("pipeline").setLevel(logging.WARNING)
logger = logging.getLogger("pipeline.server")

from ..config import get_config as _get_config
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import StreamingResponse

load_dotenv()

# ── App ────────────────────────────────────────────────────────────────────

app = FastAPI(title="Protocol Pipeline UI", version="1.0.0")

STATIC_DIR = Path(__file__).parent / "static"
UPLOAD_DIR = Path(tempfile.gettempdir()) / "pipeline_uploads"
OUTPUT_DIR = Path(tempfile.gettempdir()) / "pipeline_outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Job storage  {job_id: {status, progress, messages[], result, created_at}}
jobs: dict[str, dict[str, Any]] = {}

# ── Limits & tunables (driven by PipelineConfig) ─────────────────────────

_server_cfg = _get_config()
MAX_UPLOAD_SIZE = _server_cfg.max_upload_size_bytes
MAX_CONCURRENT_JOBS = _server_cfg.max_concurrent_jobs
JOB_TTL_SECONDS = _server_cfg.job_ttl_seconds
CLEANUP_INTERVAL = 30 * 60           # 30 minutes

_jobs_lock = threading.Lock()
_server_start_time = time.time()
_total_jobs_processed = 0


# ── Helpers ────────────────────────────────────────────────────────────────

def _update_job(job_id: str, **kwargs):
    """Update a job's state and append to its message log."""
    with _jobs_lock:
        job = jobs.setdefault(
            job_id,
            {"status": "pending", "progress": 0, "messages": [],
             "result": None, "created_at": time.time()},
        )
        job.update(kwargs)
        if "message" in kwargs:
            job["messages"].append(kwargs["message"])


def _run_pipeline_sync(job_id: str, pdf_paths: list[str], model: str, name: str | None):
    """Run the full pipeline (blocking).  Updates job state as it goes.

    Automatically resumes if a previous run left a protocol JSON or
    KB-batch checkpoints in the output directory.
    """
    try:
        from ..extract import extract_multiple_pdfs
        from ..structure import generate_protocol_tree, generate_protocol_from_multiple
        from ..kb_generator import generate_knowledge_base, generate_kb_from_multiple
        from ..validate import validate_protocol, validate_knowledge_base
        from openai import OpenAI

        output_path = OUTPUT_DIR / job_id
        output_path.mkdir(parents=True, exist_ok=True)
        # Step 1: Extract
        _update_job(job_id, status="running", progress=10,
                    message="📄 Extracting text from PDFs...")
        docs = extract_multiple_pdfs([Path(p) for p in pdf_paths])
        sections_total = sum(len(d.sections) for d in docs)
        pages_total = sum(d.page_count for d in docs)
        _update_job(job_id, progress=20,
                    message=f"✓ Extracted {len(docs)} PDF(s): {pages_total} pages, {sections_total} sections")

        # Save extracted text for debug
        for i, doc in enumerate(docs):
            txt_path = output_path / f"extracted_{i+1}.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"Source: {doc.source_path}\nTitle: {doc.title}\nPages: {doc.page_count}\n\n")
                for s in doc.sections:
                    f.write(f"{'#' * s.level} {s.heading}\n{s.text}\n\n")

        # Step 2: Protocol tree — resume if a previous run already saved one
        existing_protos = [p for p in sorted(output_path.glob("*.json"))
                          if "_kb" not in p.name and p.name != "checkpoints"]
        if existing_protos:
            proto_path = existing_protos[0]
            _update_job(job_id, progress=25,
                        message=f"🌲 Found existing protocol — resuming from {proto_path.name}")
            with open(proto_path, "r", encoding="utf-8") as f:
                protocol = json.load(f)
        else:
            _update_job(job_id, progress=25,
                        message="🌲 Generating protocol tree via LLM (this may take a while for large documents)...")
            client = OpenAI()

            # Progress callback: forward batched-processing messages to SSE stream
            def _proto_progress(msg: str):
                _update_job(job_id, message=f"  🌲 {msg}")

            if len(docs) == 1:
                protocol = generate_protocol_tree(docs[0], client, model, progress=_proto_progress,
                                                  checkpoint_dir=output_path)
            else:
                protocol = generate_protocol_from_multiple(docs, client, model, name, progress=_proto_progress,
                                                           checkpoint_dir=output_path)

            protocol_id = protocol.get("protocol_id", "unknown_protocol")
            proto_path = output_path / f"{protocol_id}.json"
            with open(proto_path, "w", encoding="utf-8") as f:
                json.dump(protocol, f, indent=2, ensure_ascii=False)

        # Ensure client is available for KB step (may not have been created above)
        try:
            client
        except NameError:
            client = OpenAI()

        n_steps = len(protocol.get("steps", []))
        n_constraints = len(protocol.get("global_constraints", []))
        _update_job(job_id, progress=50,
                    message=f"✓ Protocol tree generated: {n_steps} steps, {n_constraints} constraints")

        # Step 3: Validate protocol
        _update_job(job_id, progress=55,
                    message="🔍 Validating protocol structure...")
        proto_val = validate_protocol(protocol)
        if proto_val.errors:
            _update_job(job_id, message=f"⚠ Protocol validation: {len(proto_val.errors)} error(s)")
            for e in proto_val.errors:
                _update_job(job_id, message=f"  ✗ {e}")
        else:
            _update_job(job_id, message="✓ Protocol validation passed")
        if proto_val.warnings:
            for w in proto_val.warnings:
                _update_job(job_id, message=f"  ⚡ {w}")

        # Step 4: Knowledge base — resume if already completed
        protocol_id = protocol.get("protocol_id", "unknown_protocol")
        kb_path = output_path / f"{protocol_id}_kb.json"
        if kb_path.exists():
            _update_job(job_id, progress=60,
                        message=f"📚 Found existing KB — resuming from {kb_path.name}")
            with open(kb_path, "r", encoding="utf-8") as f:
                kb = json.load(f)
        else:
            _update_job(job_id, progress=60,
                        message="📚 Generating knowledge base chunks via LLM...")

            def _kb_progress(msg: str):
                _update_job(job_id, message=f"  📚 {msg}")

            if len(docs) == 1:
                kb = generate_knowledge_base(docs[0], protocol, client, model, progress=_kb_progress,
                                             checkpoint_dir=output_path)
            else:
                kb = generate_kb_from_multiple(docs, protocol, client, model, progress=_kb_progress,
                                               checkpoint_dir=output_path)

            with open(kb_path, "w", encoding="utf-8") as f:
                json.dump(kb, f, indent=2, ensure_ascii=False)

        n_chunks = len(kb.get("chunks", []))
        _update_job(job_id, progress=85,
                    message=f"✓ Knowledge base generated: {n_chunks} chunks")

        # Step 5: Validate KB
        _update_job(job_id, progress=90,
                    message="🔍 Validating knowledge base...")
        kb_val = validate_knowledge_base(kb, protocol)
        if kb_val.errors:
            _update_job(job_id, message=f"⚠ KB validation: {len(kb_val.errors)} error(s)")
            for e in kb_val.errors:
                _update_job(job_id, message=f"  ✗ {e}")
        else:
            _update_job(job_id, message="✓ KB validation passed")
        if kb_val.warnings:
            for w in kb_val.warnings:
                _update_job(job_id, message=f"  ⚡ {w}")

        # Cleanup checkpoints after successful completion
        ckpt_dir = output_path / "checkpoints"
        if ckpt_dir.exists():
            shutil.rmtree(ckpt_dir, ignore_errors=True)

        # Done
        _update_job(job_id, status="complete", progress=100,
                    message="🎉 Pipeline complete!",
                    result={
                        "protocol_id": protocol_id,
                        "protocol_path": str(proto_path),
                        "kb_path": str(kb_path),
                        "protocol": protocol,
                        "knowledge_base": kb,
                        "validation": {
                            "protocol": {"ok": proto_val.ok, "errors": proto_val.errors, "warnings": proto_val.warnings},
                            "kb": {"ok": kb_val.ok, "errors": kb_val.errors, "warnings": kb_val.warnings},
                        },
                    })

    except Exception as exc:
        _update_job(job_id, status="error", progress=100,
                    message=f"❌ Error: {exc}\n{traceback.format_exc()}")


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.post("/api/upload")
async def upload_pdfs(
    files: list[UploadFile] = File(...),
    model: str = Form("gpt-4o"),
    name: str = Form(None),
):
    """Upload one or more PDFs and start the pipeline."""
    global _total_jobs_processed

    # ── Concurrent job limit ───────────────────────────────────────────
    with _jobs_lock:
        running = sum(1 for j in jobs.values() if j["status"] in ("running", "queued"))
    if running >= MAX_CONCURRENT_JOBS:
        raise HTTPException(429, detail="Too many concurrent jobs")

    job_id = uuid.uuid4().hex[:12]
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    pdf_paths = []
    for f in files:
        # ── File size limit ────────────────────────────────────────────
        content = await f.read()
        if len(content) > MAX_UPLOAD_SIZE:
            shutil.rmtree(job_dir, ignore_errors=True)
            raise HTTPException(
                413,
                detail=(
                    f"File '{f.filename}' exceeds "
                    f"{MAX_UPLOAD_SIZE // (1024 * 1024)} MB limit"
                ),
            )
        dest = job_dir / f.filename
        dest.write_bytes(content)
        pdf_paths.append(str(dest))

    _update_job(job_id, status="queued", progress=0,
                message=f"Queued {len(files)} PDF(s) for processing")
    _total_jobs_processed += 1

    # Run pipeline in background thread so we don't block the event loop
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, _run_pipeline_sync, job_id, pdf_paths, model, name)

    return {"job_id": job_id, "file_count": len(files)}


@app.post("/api/jobs/{job_id}/retry")
async def retry_job(job_id: str, model: str = Form("gpt-4o"), name: str = Form(None)):
    """Retry a failed / errored job, reusing its existing output directory and checkpoints.

    Works even after a server restart — if the job isn't in memory but
    the upload directory still exists on disk, a fresh job entry is created.
    """
    job = jobs.get(job_id)

    # ── Recover from disk after a server restart ──────────────────
    if not job:
        job_dir = UPLOAD_DIR / job_id
        if not job_dir.exists():
            raise HTTPException(404, "Job not found and no upload directory on disk — please re-upload")
        pdf_paths = sorted(str(p) for p in job_dir.glob("*.pdf"))
        if not pdf_paths:
            raise HTTPException(410, "Upload directory exists but contains no PDFs — please re-upload")
        # Bootstrap a minimal job entry so the rest of the flow works
        _update_job(job_id, status="error", progress=0,
                    message="(recovered from disk after server restart)")
        job = jobs[job_id]

    if job["status"] not in ("error", "complete"):
        raise HTTPException(409, f"Job is {job['status']}, cannot retry")

    # Locate uploaded PDFs from the original run
    job_dir = UPLOAD_DIR / job_id
    if not job_dir.exists():
        raise HTTPException(410, "Upload directory was cleaned up — please re-upload")

    pdf_paths = sorted(str(p) for p in job_dir.glob("*.pdf"))
    if not pdf_paths:
        raise HTTPException(410, "No PDFs found in upload directory — please re-upload")

    # Reset job state but preserve existing output directory (protocol JSON, checkpoints)
    _update_job(job_id, status="queued", progress=0,
                message=f"♻️ Retrying job — {len(pdf_paths)} PDF(s), will resume from checkpoints")

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, _run_pipeline_sync, job_id, pdf_paths, model, name)

    return {"job_id": job_id, "file_count": len(pdf_paths), "resumed": True}


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Poll job status."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return {
        "status": job["status"],
        "progress": job["progress"],
        "messages": job["messages"],
        "result": {
            "protocol_id": job["result"]["protocol_id"],
            "validation": job["result"]["validation"],
        } if job.get("result") else None,
    }


@app.get("/api/jobs/{job_id}/stream")
async def stream_job(job_id: str):
    """SSE stream of job progress."""
    with _jobs_lock:
        if job_id not in jobs:
            raise HTTPException(404, "Job not found")

    async def event_generator():
        last_idx = 0
        stale_ticks = 0          # detect stuck jobs
        MAX_STALE_TICKS = 600    # 5 minutes at 0.5s interval
        while True:
            # Snapshot job state under lock
            with _jobs_lock:
                job = jobs.get(job_id, {})
                messages = list(job.get("messages", []))
                status = job.get("status")
                progress = job.get("progress", 0)
                result = job.get("result")

            # Send any new messages
            new_messages = False
            while last_idx < len(messages):
                new_messages = True
                data = json.dumps({
                    "status": status,
                    "progress": progress,
                    "message": messages[last_idx],
                })
                yield f"data: {data}\n\n"
                last_idx += 1

            if new_messages:
                stale_ticks = 0
            else:
                stale_ticks += 1

            if status in ("complete", "error"):
                # Send final event
                final = {
                    "status": status,
                    "progress": 100,
                    "message": "__DONE__",
                    "result": {
                        "protocol_id": result["protocol_id"],
                        "validation": result["validation"],
                    } if result else None,
                }
                yield f"data: {json.dumps(final)}\n\n"
                break

            # Timeout: if no updates for 5 minutes, assume crash
            if stale_ticks >= MAX_STALE_TICKS:
                timeout_msg = {
                    "status": "error",
                    "progress": 100,
                    "message": "__DONE__",
                    "result": None,
                }
                _update_job(job_id, status="error",
                            message="❌ Pipeline timed out — no progress for 5 minutes.")
                yield f"data: {json.dumps(timeout_msg)}\n\n"
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/jobs/{job_id}/download/{file_type}")
async def download_result(job_id: str, file_type: str):
    """Download protocol or KB JSON file."""
    job = jobs.get(job_id)
    if not job or not job.get("result"):
        raise HTTPException(404, "Job not found or not complete")

    if file_type == "protocol":
        path = job["result"]["protocol_path"]
    elif file_type == "kb":
        path = job["result"]["kb_path"]
    else:
        raise HTTPException(400, "file_type must be 'protocol' or 'kb'")

    return FileResponse(path, filename=Path(path).name, media_type="application/json")


@app.get("/api/jobs/{job_id}/protocol")
async def get_protocol_json(job_id: str):
    """Get the generated protocol tree JSON (for visualization)."""
    job = jobs.get(job_id)
    if not job or not job.get("result"):
        raise HTTPException(404, "Job not found or not complete")
    return job["result"]["protocol"]


@app.get("/api/jobs/{job_id}/kb")
async def get_kb_json(job_id: str):
    """Get the generated KB JSON."""
    job = jobs.get(job_id)
    if not job or not job.get("result"):
        raise HTTPException(404, "Job not found or not complete")
    return job["result"]["knowledge_base"]


@app.post("/api/visualize")
async def visualize_protocol(protocol: dict):
    """Accept a raw protocol JSON and return tree visualization data."""
    from ..validate import validate_protocol

    validation = validate_protocol(protocol)

    # Build tree nodes for the frontend
    steps = protocol.get("steps", [])
    step_map = {s["id"]: s for s in steps}
    initial = protocol.get("initial_step")

    # BFS to determine order
    ordered = []
    visited = set()
    queue = [initial] if initial else []
    while queue:
        sid = queue.pop(0)
        if sid in visited:
            continue
        visited.add(sid)
        step = step_map.get(sid)
        if step:
            ordered.append(step)
            if step.get("type") == "decision":
                for br in step.get("branches", []):
                    if br.get("next") and br["next"] not in visited:
                        queue.append(br["next"])
            elif step.get("next"):
                if step["next"] not in visited:
                    queue.append(step["next"])

    # Add any steps not reachable from initial (orphans)
    for s in steps:
        if s["id"] not in visited:
            ordered.append(s)

    tree_nodes = []
    for step in ordered:
        node = {
            "id": step["id"],
            "description": step.get("description", ""),
            "type": step.get("type", "sequential"),
            "phase": step.get("phase", ""),
            "critical": step.get("critical", False),
            "terminal": step.get("terminal", False),
            "effects": step.get("effects", {}),
            "preconditions": step.get("preconditions", {}),
        }
        if step.get("type") == "decision":
            node["branches"] = [
                {"condition": br.get("condition", ""), "next": br.get("next", "")}
                for br in step.get("branches", [])
            ]
        elif step.get("next"):
            node["next_step"] = step["next"]
        tree_nodes.append(node)

    constraints = [
        {
            "id": c.get("id", ""),
            "description": c.get("description", ""),
            "critical": c.get("critical", False),
            "forbidden_actions": c.get("forbidden_actions", []),
        }
        for c in protocol.get("global_constraints", [])
    ]

    return {
        "tree": tree_nodes,
        "constraints": constraints,
        "possible_actions": protocol.get("possible_actions", []),
        "metadata": {
            "protocol_id": protocol.get("protocol_id", ""),
            "title": protocol.get("title", ""),
            "description": protocol.get("description", ""),
            "roles": protocol.get("roles", []),
            "initial_step": protocol.get("initial_step", ""),
        },
        "validation": {
            "ok": validation.ok,
            "errors": validation.errors,
            "warnings": validation.warnings,
        },
    }


# ── Background cleanup ─────────────────────────────────────────────────────

async def _cleanup_stale_jobs():
    """Periodically remove jobs older than JOB_TTL_SECONDS."""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        now = time.time()
        stale_ids: list[str] = []
        with _jobs_lock:
            for jid, job in list(jobs.items()):
                if now - job.get("created_at", now) > JOB_TTL_SECONDS:
                    stale_ids.append(jid)
            for jid in stale_ids:
                del jobs[jid]
        # Clean up disk
        for jid in stale_ids:
            for d in (UPLOAD_DIR / jid, OUTPUT_DIR / jid):
                if d.exists():
                    shutil.rmtree(d, ignore_errors=True)
        if stale_ids:
            logger.info("Cleaned up %d stale jobs", len(stale_ids))


@app.on_event("startup")
async def _start_cleanup_task():
    asyncio.create_task(_cleanup_stale_jobs())


@app.get("/api/health")
async def health():
    """Server health check: uptime, active jobs, total processed."""
    with _jobs_lock:
        active = sum(1 for j in jobs.values() if j["status"] in ("running", "queued"))
    return {
        "uptime_seconds": round(time.time() - _server_start_time, 1),
        "active_jobs": active,
        "total_jobs_processed": _total_jobs_processed,
    }


# ── Serve static files last (catchall) ────────────────────────────────────

app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
