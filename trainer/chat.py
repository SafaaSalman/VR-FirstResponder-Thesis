"""
Chat-based procedural training engine – main entry point.

Usage:
    python -m trainer.chat
    python -m trainer.chat --scenario eq_blocked_route
    python -m trainer.chat --list-scenarios

The full pipeline per turn:
    trainee text → ActionParser (LLM) → RuleEngine → RAG → LLM response
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

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


# ── Helpers ────────────────────────────────────────────────────────────────


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_protocol() -> dict:
    return load_json(
        config.PROTOCOLS_DIR / f"{config.DEFAULT_PROTOCOL}.json"
    )


def load_scenarios() -> list[dict]:
    path = config.SCENARIOS_DIR / "earthquake_scenarios.json"
    data = load_json(path)
    return data["scenarios"]


def pick_scenario(scenarios: list[dict], scenario_id: str) -> dict:
    for s in scenarios:
        if s["scenario_id"] == scenario_id:
            return s
    raise ValueError(
        f"Scenario '{scenario_id}' not found.  "
        f"Available: {[s['scenario_id'] for s in scenarios]}"
    )


# ── Terminal formatting ────────────────────────────────────────────────────

BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def banner() -> None:
    print(f"\n{BOLD}{CYAN}{'═' * 60}")
    print("   PROCEDURAL TRAINING ENGINE  –  Chat Prototype")
    print(f"{'═' * 60}{RESET}\n")


def trainer_says(text: str) -> None:
    print(f"\n{GREEN}{BOLD}[Trainer]{RESET} {text}\n")


def system_says(text: str) -> None:
    print(f"{YELLOW}[System] {text}{RESET}")


def error_says(text: str) -> None:
    print(f"{RED}[Error] {text}{RESET}")


# ── Main loop ──────────────────────────────────────────────────────────────


def run(scenario_id: str | None = None) -> None:
    # ── Validate API key ───────────────────────────────────────────────
    if not config.OPENAI_API_KEY:
        error_says(
            "OPENAI_API_KEY not set.  "
            "Create a .env file in the project root or export the variable."
        )
        sys.exit(1)

    client = OpenAI(api_key=config.OPENAI_API_KEY)

    # ── Load data ──────────────────────────────────────────────────────
    protocol = load_protocol()
    scenarios = load_scenarios()
    scenario_id = scenario_id or config.DEFAULT_SCENARIO
    scenario = pick_scenario(scenarios, scenario_id)

    # ── Initialize components ──────────────────────────────────────────
    state = ScenarioState(scenario, protocol)
    rule_engine = RuleEngine(protocol, state)
    scoring = ScoringEngine(protocol, state)
    hints = HintEngine(protocol, state)
    debrief_gen = DebriefGenerator(protocol, state, scoring)
    rag = RAGRetriever(client=client)
    action_parser = ActionParser(protocol["possible_actions"], client=client)
    llm = LLMInterface(client=client)

    # ── Banner + scenario intro ────────────────────────────────────────
    banner()
    system_says(f"Protocol: {protocol['title']}")
    system_says(f"Scenario: {scenario['name']}  ({scenario['difficulty']})")
    system_says("Type 'hint' for a hint, 'status' for progress, 'quit' to end.\n")

    intro = llm.generate_scenario_intro(scenario, protocol["title"])
    trainer_says(intro)

    # ── Chat loop ──────────────────────────────────────────────────────
    while True:
        try:
            user_input = input(f"{BLUE}{BOLD}You > {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        lower = user_input.lower()

        # ── Meta commands ──────────────────────────────────────────────
        if lower in ("quit", "exit", "q"):
            system_says("Ending session.  Generating debrief...\n")
            _do_debrief(debrief_gen, rag, llm, state)
            break

        if lower in ("status", "progress"):
            _show_status(state, rule_engine)
            continue

        if lower in ("hint", "help"):
            _do_hint(hints, rag, llm, state)
            continue

        if lower == "debrief":
            _do_debrief(debrief_gen, rag, llm, state)
            continue

        if lower == "score":
            _show_score(scoring)
            continue

        # ── Parse actions ──────────────────────────────────────────────
        actions = action_parser.parse(user_input)
        all_results: list[dict] = []
        rag_step_ids: list[str] = []

        for action_id in actions:
            # Handle meta actions
            if action_id == "request_hint":
                _do_hint(hints, rag, llm, state)
                continue
            if action_id == "ask_question":
                _do_question(user_input, rag, llm, state)
                continue

            # Evaluate via rule engine
            result = rule_engine.evaluate_action(action_id)
            result_dict = result.to_dict()
            state.record_action(action_id, result_dict)
            all_results.append(result_dict)

            # Collect step IDs for RAG
            if result.matched_step:
                rag_step_ids.append(result.matched_step)
            rag_step_ids.extend(result.skipped_steps)

        if not all_results:
            continue

        # ── RAG retrieval ──────────────────────────────────────────────
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

        # ── LLM response ──────────────────────────────────────────────
        response = llm.generate_response(
            action_results=all_results,
            rag_text=rag_text,
            state_summary=state.get_summary(),
            scenario_narrative=state.narrative,
        )
        trainer_says(response)

        # ── Check completion ───────────────────────────────────────────
        if state.progress.is_complete:
            system_says(
                "Protocol complete!  Generating debrief...\n"
            )
            _do_debrief(debrief_gen, rag, llm, state)
            break


# ── Sub-routines ───────────────────────────────────────────────────────────


def _do_hint(
    hints: HintEngine,
    rag: RAGRetriever,
    llm: LLMInterface,
    state: ScenarioState,
) -> None:
    hint = hints.get_hint()
    chunks = rag.retrieve_for_result(step_ids=hint["related_steps"])
    rag_text = rag.format_chunks_for_prompt(chunks)
    response = llm.generate_hint_response(hint, rag_text)
    print(f"\n{CYAN}[Hint – Level {hint['level']}]{RESET} {response}\n")


def _do_question(
    question: str,
    rag: RAGRetriever,
    llm: LLMInterface,
    state: ScenarioState,
) -> None:
    chunks = rag.retrieve_by_query(question, top_k=config.RAG_TOP_K)
    rag_text = rag.format_chunks_for_prompt(chunks)
    response = llm.answer_question(question, rag_text, state.get_summary())
    trainer_says(response)


def _do_debrief(
    debrief_gen: DebriefGenerator,
    rag: RAGRetriever,
    llm: LLMInterface,
    state: ScenarioState,
) -> None:
    data = debrief_gen.generate_input()
    chunks = rag.retrieve_for_result(step_ids=data["rag_step_ids"])
    rag_text = rag.format_chunks_for_prompt(chunks)
    debrief = llm.generate_debrief(data, rag_text)
    print(f"\n{BOLD}{CYAN}{'─' * 60}")
    print("                    AFTER-ACTION DEBRIEF")
    print(f"{'─' * 60}{RESET}\n")
    print(debrief)
    print(f"\n{CYAN}{'─' * 60}{RESET}")
    _show_score_raw(data["scores"])


def _show_status(state: ScenarioState, rule_engine: RuleEngine) -> None:
    s = state.get_summary()
    print(f"\n{CYAN}── Progress ──{RESET}")
    print(f"  Current step : {s['current_step'] or 'N/A'}")
    print(f"  Completed    : {', '.join(s['completed_steps']) or 'none'}")
    print(f"  Violations   : {s['violations_count']}")
    print(f"  Actions taken: {s['actions_count']}")
    print(f"  Complete     : {s['is_complete']}\n")


def _show_score(scoring: ScoringEngine) -> None:
    data = scoring.compute()
    _show_score_raw(data["scores"])


def _show_score_raw(scores: dict) -> None:
    print(f"\n{CYAN}── Scores ──{RESET}")
    for k, v in scores.items():
        label = k.replace("_", " ").title()
        bar = "█" * (v // 5) + "░" * (20 - v // 5)
        print(f"  {label:25s} {bar} {v}/100")
    print()


# ── CLI ────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Procedural Training Engine – chat prototype"
    )
    parser.add_argument(
        "--scenario",
        default=None,
        help="Scenario ID to load (e.g. eq_blocked_route)",
    )
    parser.add_argument(
        "--list-scenarios",
        action="store_true",
        help="List available scenarios and exit",
    )
    args = parser.parse_args()

    if args.list_scenarios:
        scenarios = load_scenarios()
        for s in scenarios:
            print(
                f"  {s['scenario_id']:25s} "
                f"{s['name']} ({s['difficulty']})"
            )
        return

    run(scenario_id=args.scenario)


if __name__ == "__main__":
    main()
