"""
FastAPI backend for the admin / debug web interface.

Exposes REST endpoints that wrap the existing CLI training engine,
returning rich JSON payloads (including debug data) for the frontend.

Usage:
    uvicorn trainer.web.server:app --reload
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI

from trainer import config
from trainer.engine.state import ScenarioState
from trainer.engine.rule_engine import RuleEngine
from trainer.engine.scoring import ScoringEngine
from trainer.engine.hints import HintEngine
from trainer.engine.debrief import DebriefGenerator
from trainer.rag.retriever import RAGRetriever
from trainer.llm.action_parser import ActionParser
from trainer.llm.interface import LLMInterface
from trainer.chat import load_protocol, load_scenarios, pick_scenario


# ── FastAPI app ────────────────────────────────────────────────────────────

app = FastAPI(title="Procedural Trainer – Admin Debug UI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"

# ── Session state (single user, in-memory) ─────────────────────────────────

_session: Dict[str, Any] = {}


def _get(key: str):
    if key not in _session:
        raise HTTPException(status_code=400, detail="No active session. Start one first.")
    return _session[key]


# ── Pydantic models ────────────────────────────────────────────────────────

class StartRequest(BaseModel):
    scenario_id: Optional[str] = None


class ActionRequest(BaseModel):
    text: str


# ── Helpers ─────────────────────────────────────────────────────────────────

def _protocol_tree(protocol: dict, state: ScenarioState, rule_engine: RuleEngine) -> List[dict]:
    """Build a flat list of step objects with status annotations for the frontend."""
    completed = set(state.progress.completed_steps)
    current = state.progress.current_step
    violations_by_step: Dict[str, list] = {}
    for v in state.progress.violations:
        action = v.get("action", "")
        violations_by_step.setdefault(action, []).append(v)

    # Determine skipped steps (steps that were before current but not completed)
    step_order = rule_engine.get_all_steps_ordered()

    tree = []
    for step_def in protocol["steps"]:
        sid = step_def["id"]
        status = "pending"
        if sid in completed:
            status = "completed"
        elif sid == current:
            status = "current"

        # Check if this step was involved in a violation
        has_violation = sid in violations_by_step

        # Decision branches
        branches = []
        if step_def.get("type") == "decision":
            for cond in step_def.get("conditions", []):
                branches.append({
                    "condition": cond["if"],
                    "next": cond["next"],
                    "active": rule_engine.evaluate_condition(cond["if"]),
                })

        tree.append({
            "id": sid,
            "description": step_def.get("description", ""),
            "type": step_def.get("type", "action"),
            "phase": step_def.get("phase", ""),
            "critical": step_def.get("critical", False),
            "terminal": step_def.get("terminal", False),
            "status": status,
            "has_violation": has_violation,
            "violations": violations_by_step.get(sid, []),
            "branches": branches,
            "allowed_next": step_def.get("allowed_next", []),
        })
    return tree


def _constraints_status(protocol: dict, state: ScenarioState) -> List[dict]:
    """Return global constraints with violation status."""
    violated_constraints = set()
    for v in state.progress.violations:
        if v.get("type") == "global_constraint":
            violated_constraints.add(v.get("constraint", ""))
    result = []
    for c in protocol.get("global_constraints", []):
        result.append({
            "id": c["id"],
            "description": c["description"],
            "critical": c.get("critical", False),
            "violated": c["id"] in violated_constraints,
        })
    return result


# ── Routes ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main admin UI."""
    html_path = STATIC_DIR / "index.html"
    return FileResponse(html_path)


@app.get("/api/scenarios")
async def list_scenarios():
    """List available scenarios."""
    scenarios = load_scenarios()
    return [
        {
            "scenario_id": s["scenario_id"],
            "name": s["name"],
            "difficulty": s["difficulty"],
            "description": s.get("description", ""),
        }
        for s in scenarios
    ]


@app.post("/api/start")
async def start_session(req: StartRequest):
    """Initialize a new training session."""
    if not config.OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set.")

    client = OpenAI(api_key=config.OPENAI_API_KEY)
    protocol = load_protocol()
    scenarios = load_scenarios()
    scenario_id = req.scenario_id or config.DEFAULT_SCENARIO

    try:
        scenario = pick_scenario(scenarios, scenario_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    state = ScenarioState(scenario, protocol)
    rule_engine = RuleEngine(protocol, state)
    scoring = ScoringEngine(protocol, state)
    hints = HintEngine(protocol, state)
    debrief_gen = DebriefGenerator(protocol, state, scoring)
    rag = RAGRetriever(client=client)
    action_parser = ActionParser(protocol["possible_actions"], client=client)
    llm = LLMInterface(client=client)

    _session.update({
        "client": client,
        "protocol": protocol,
        "scenario": scenario,
        "state": state,
        "rule_engine": rule_engine,
        "scoring": scoring,
        "hints": hints,
        "debrief_gen": debrief_gen,
        "rag": rag,
        "action_parser": action_parser,
        "llm": llm,
        "messages": [],       # chat history for debug
        "turn_debug": [],     # debug info per turn
    })

    # Generate intro
    intro = llm.generate_scenario_intro(scenario, protocol["title"])
    _session["messages"].append({"role": "trainer", "text": intro})

    return {
        "intro": intro,
        "scenario": {
            "id": scenario["scenario_id"],
            "name": scenario["name"],
            "difficulty": scenario["difficulty"],
        },
        "protocol_tree": _protocol_tree(protocol, state, rule_engine),
        "constraints": _constraints_status(protocol, state),
        "state_summary": state.get_summary(),
    }


@app.post("/api/action")
async def perform_action(req: ActionRequest):
    """Process a trainee action (free text)."""
    state: ScenarioState = _get("state")
    rule_engine: RuleEngine = _get("rule_engine")
    scoring: ScoringEngine = _get("scoring")
    rag: RAGRetriever = _get("rag")
    action_parser: ActionParser = _get("action_parser")
    llm: LLMInterface = _get("llm")
    protocol: dict = _get("protocol")

    user_text = req.text.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Empty input.")

    _session["messages"].append({"role": "trainee", "text": user_text})

    # ── Parse actions  ──────────────────────────────────────────────────
    parsed_actions = action_parser.parse(user_text)

    # ── Handle meta-actions ─────────────────────────────────────────────
    if parsed_actions == ["request_hint"]:
        return await get_hint()

    if parsed_actions == ["ask_question"]:
        chunks = rag.retrieve_by_query(user_text, top_k=config.RAG_TOP_K)
        rag_text = rag.format_chunks_for_prompt(chunks)
        answer = llm.answer_question(user_text, rag_text, state.get_summary())
        _session["messages"].append({"role": "trainer", "text": answer})

        debug = {
            "turn_type": "question",
            "parsed_actions": parsed_actions,
            "rag_chunks": [c["chunk_id"] for c in chunks],
            "rag_text": rag_text,
        }
        _session["turn_debug"].append(debug)

        return {
            "response": answer,
            "turn_type": "question",
            "protocol_tree": _protocol_tree(protocol, state, rule_engine),
            "constraints": _constraints_status(protocol, state),
            "state_summary": state.get_summary(),
            "scores": scoring.compute(),
            "debug": debug,
        }

    # ── Evaluate actions ────────────────────────────────────────────────
    all_results: list[dict] = []
    rag_step_ids: list[str] = []

    for action_id in parsed_actions:
        if action_id in ("request_hint", "ask_question"):
            continue
        result = rule_engine.evaluate_action(action_id)
        result_dict = result.to_dict()
        state.record_action(action_id, result_dict)
        all_results.append(result_dict)

        if result.matched_step:
            rag_step_ids.append(result.matched_step)
        rag_step_ids.extend(result.skipped_steps)

    # ── RAG retrieval ───────────────────────────────────────────────────
    constraint_id = None
    for r in all_results:
        if r.get("constraint_violated"):
            constraint_id = r["constraint_violated"]
            break

    chunks = rag.retrieve_for_result(
        step_ids=rag_step_ids,
        constraint_id=constraint_id,
        top_k=config.RAG_TOP_K,
    )
    rag_text = rag.format_chunks_for_prompt(chunks)

    # ── LLM response ───────────────────────────────────────────────────
    response = llm.generate_response(
        action_results=all_results,
        rag_text=rag_text,
        state_summary=state.get_summary(),
        scenario_narrative=state.get_dynamic_narrative(),
    )
    _session["messages"].append({"role": "trainer", "text": response})

    # ── Debug payload ──────────────────────────────────────────────────
    debug = {
        "turn_type": "action",
        "user_text": user_text,
        "parsed_actions": parsed_actions,
        "action_results": all_results,
        "rag_step_ids": rag_step_ids,
        "rag_chunks": [c["chunk_id"] for c in chunks],
        "rag_text": rag_text,
        "constraint_id": constraint_id,
    }
    _session["turn_debug"].append(debug)

    # ── Check completion ───────────────────────────────────────────────
    is_complete = state.progress.is_complete
    debrief_data = None
    if is_complete:
        debrief_gen: DebriefGenerator = _get("debrief_gen")
        debrief_data = debrief_gen.generate_input()
        debrief_chunks = rag.retrieve_for_result(step_ids=debrief_data["rag_step_ids"])
        debrief_rag_text = rag.format_chunks_for_prompt(debrief_chunks)
        debrief_text = llm.generate_debrief(debrief_data, debrief_rag_text)
        _session["messages"].append({"role": "trainer", "text": f"[DEBRIEF]\n{debrief_text}"})
        debrief_data["debrief_text"] = debrief_text

    return {
        "response": response,
        "turn_type": "action",
        "is_complete": is_complete,
        "debrief": debrief_data,
        "protocol_tree": _protocol_tree(protocol, state, rule_engine),
        "constraints": _constraints_status(protocol, state),
        "state_summary": state.get_summary(),
        "scores": scoring.compute(),
        "debug": debug,
    }


@app.get("/api/hint")
async def get_hint():
    """Get a progressive hint."""
    state: ScenarioState = _get("state")
    hints: HintEngine = _get("hints")
    rag: RAGRetriever = _get("rag")
    llm: LLMInterface = _get("llm")
    rule_engine: RuleEngine = _get("rule_engine")
    scoring: ScoringEngine = _get("scoring")
    protocol: dict = _get("protocol")

    hint = hints.get_hint()
    chunks = rag.retrieve_for_result(step_ids=hint["related_steps"])
    rag_text = rag.format_chunks_for_prompt(chunks)
    response = llm.generate_hint_response(hint, rag_text)

    _session["messages"].append({"role": "trainer", "text": f"[Hint L{hint['level']}] {response}"})

    debug = {
        "turn_type": "hint",
        "hint_level": hint["level"],
        "hint_text_raw": hint["text"],
        "rag_chunks": [c["chunk_id"] for c in chunks],
    }
    _session["turn_debug"].append(debug)

    return {
        "response": response,
        "turn_type": "hint",
        "hint_level": hint["level"],
        "protocol_tree": _protocol_tree(protocol, state, rule_engine),
        "constraints": _constraints_status(protocol, state),
        "state_summary": state.get_summary(),
        "scores": scoring.compute(),
        "debug": debug,
    }


@app.get("/api/status")
async def get_status():
    """Return current session status, scores, tree, debug."""
    state: ScenarioState = _get("state")
    rule_engine: RuleEngine = _get("rule_engine")
    scoring: ScoringEngine = _get("scoring")
    protocol: dict = _get("protocol")

    return {
        "protocol_tree": _protocol_tree(protocol, state, rule_engine),
        "constraints": _constraints_status(protocol, state),
        "state_summary": state.get_summary(),
        "scores": scoring.compute(),
        "messages": _session.get("messages", []),
        "turn_debug": _session.get("turn_debug", []),
    }


@app.post("/api/debrief")
async def get_debrief():
    """Manually trigger debrief generation."""
    state: ScenarioState = _get("state")
    rule_engine: RuleEngine = _get("rule_engine")
    scoring: ScoringEngine = _get("scoring")
    debrief_gen: DebriefGenerator = _get("debrief_gen")
    rag: RAGRetriever = _get("rag")
    llm: LLMInterface = _get("llm")
    protocol: dict = _get("protocol")

    data = debrief_gen.generate_input()
    chunks = rag.retrieve_for_result(step_ids=data["rag_step_ids"])
    rag_text = rag.format_chunks_for_prompt(chunks)
    debrief_text = llm.generate_debrief(data, rag_text)

    _session["messages"].append({"role": "trainer", "text": f"[DEBRIEF]\n{debrief_text}"})
    data["debrief_text"] = debrief_text

    return {
        "debrief": data,
        "protocol_tree": _protocol_tree(protocol, state, rule_engine),
        "constraints": _constraints_status(protocol, state),
        "state_summary": state.get_summary(),
        "scores": scoring.compute(),
    }


# Mount static files last (so API routes take priority)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
