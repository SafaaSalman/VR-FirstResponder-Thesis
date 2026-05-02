"""
LLM interface – all LLM calls go through this module.

The LLM is used for:
 - Scenario introduction narration
 - Response generation (valid / invalid actions)
 - Hint elaboration (wraps the rule-engine hint in natural language)
 - Debrief generation (from structured debrief input + RAG chunks)
 - Free-form Q&A (trainee asks a question about the situation)

The LLM NEVER decides protocol correctness.  That is the rule engine's
job.  The LLM only communicates the result in natural language.
"""

from __future__ import annotations

import json
from typing import List, Optional

from openai import OpenAI

from trainer import config


class LLMInterface:
    """Thin wrapper around OpenAI chat completions."""

    def __init__(self, client: OpenAI | None = None) -> None:
        self.client = client or OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.LLM_MODEL

    # ── Scenario introduction ──────────────────────────────────────────────

    def generate_scenario_intro(
        self,
        scenario: dict,
        protocol_title: str,
    ) -> str:
        """Generate an immersive opening narration for the trainee."""
        narrative = scenario.get("narrative_details", {})
        system = (
            "You are the narrator for an emergency-response training "
            "simulation.  Set the scene vividly in 3-5 sentences.  "
            "Describe what the trainee sees, hears, and feels.  "
            "End by asking the trainee what they do first.  Do NOT "
            "reveal or hint at any correct protocol steps."
        )
        user = json.dumps(
            {
                "protocol": protocol_title,
                "scenario_name": scenario.get("name"),
                "description": scenario.get("description"),
                "location": narrative.get("location"),
                "time": narrative.get("time"),
                "people": narrative.get("people_nearby"),
                "environment": narrative.get("environment"),
            },
            indent=2,
        )
        return self._chat(system, user)

    # ── Action response ────────────────────────────────────────────────────

    def generate_response(
        self,
        action_results: List[dict],
        rag_text: str,
        state_summary: dict,
        scenario_narrative: dict,
    ) -> str:
        """
        Generate trainer response given rule-engine results + RAG text.
        """
        system = (
            "You are the NARRATOR of an immersive emergency-response "
            "training simulation.  Your tone shifts depending on "
            "whether the trainee's action was valid or invalid.\n\n"

            "DATA YOU RECEIVE:\n"
            "- action_results: the rule engine's verdict (valid/invalid, "
            "skipped steps, constraint violations).\n"
            "- scenario_state.state: the CURRENT world variables "
            "(e.g., stairs_accessible, smoke_present, inside_building). "
            "USE THESE to describe what the trainee observes.\n"
            "- narrative: DYNAMIC scene description built from the "
            "current world state — includes location, environment, "
            "people_nearby, phase_context, and current_step.  The "
            "narrative already reflects whether the trainee is inside "
            "the building, outside, at the assembly point, etc.  "
            "BASE YOUR SCENE DESCRIPTION ON THIS NARRATIVE, not on "
            "any initial earthquake imagery.\n"
            "- supporting_protocol_text: actual SOP / protocol text "
            "retrieved from the knowledge base.\n\n"

            "═══ WHEN THE ACTION IS VALID ═══\n"
            "Narrate the OUTCOME as an immersive scene.  Describe "
            "what the trainee SEES, HEARS, FEELS based on the world-"
            "state variables.  Examples:\n"
            "  • assess_surroundings + smoke_present=false, "
            "building_damage='light' → 'You scan the room. A few "
            "ceiling tiles have cracked and books litter the floor, "
            "but there is no smoke or fire.'\n"
            "  • verify_route + stairs_accessible=false → 'You "
            "approach the main stairwell — a section of the ceiling "
            "has collapsed, blocking the passage.  This route is "
            "impassable.'\n"
            "Keep it 2-3 vivid sentences.  Do NOT reference protocol "
            "text for valid actions.\n\n"

            "═══ WHEN THE ACTION IS INVALID / SKIPPED STEPS / "
            "CONSTRAINT VIOLATION ═══\n"
            "Switch to an INSTRUCTOR tone.  Your response MUST:\n"
            "1. Open with ONE short scene sentence showing the "
            "consequence (e.g., 'The building is still shaking; "
            "debris crashes around you as you try to move.').\n"
            "2. Then QUOTE or closely PARAPHRASE the relevant "
            "supporting_protocol_text to explain what the protocol "
            "says and WHY it matters.  Use phrases like 'According "
            "to protocol…', 'The SOP states…', 'The protocol "
            "requires…'.  This is the MAIN body of your response.\n"
            "3. If steps were skipped, list them and briefly note "
            "from the protocol text why each matters.\n"
            "4. Keep total response 3-5 sentences.\n\n"

            "═══ ENDING ═══\n"
            "Always end with 'What do you do?' or similar — "
            "NOTHING else after the question.\n\n"

            "═══ ABSOLUTE PROHIBITIONS ═══\n"
            "- NEVER mention, hint at, or describe ANY future "
            "protocol step or what the trainee should do next.\n"
            "- NEVER list what the trainee has already done.\n"
            "- NEVER say 'you are now ready to …', 'next you "
            "should …', 'consider …', 'focus on …'."
        )
        user = json.dumps(
            {
                "action_results": action_results,
                "supporting_protocol_text": rag_text,
                "scenario_state": state_summary,
                "narrative": scenario_narrative,
            },
            indent=2,
        )
        return self._chat(system, user)

    # ── Hint ───────────────────────────────────────────────────────────────

    def generate_hint_response(
        self,
        hint: dict,
        rag_text: str,
    ) -> str:
        """Wrap a rule-engine hint in natural language."""
        system = (
            "You are an emergency-response training instructor "
            "giving a hint.  Rephrase the hint below naturally in "
            "1-2 sentences.  Do NOT reveal the full correct answer "
            "unless the hint level is 3 (explicit)."
        )
        user = json.dumps(
            {"hint": hint, "supporting_text": rag_text}, indent=2
        )
        return self._chat(system, user)

    # ── Free-form Q&A ─────────────────────────────────────────────────────

    def answer_question(
        self,
        question: str,
        rag_text: str,
        state_summary: dict,
    ) -> str:
        """Answer a trainee's question using RAG context."""
        system = (
            "You are an emergency-response training instructor.  "
            "Answer the trainee's question using ONLY the protocol "
            "text provided below.  If the answer is not in the text, "
            "say you can only advise on what the protocol covers.  "
            "Do NOT reveal upcoming steps.  Keep it to 2-3 sentences."
        )
        user = json.dumps(
            {
                "question": question,
                "protocol_text": rag_text,
                "current_state": state_summary,
            },
            indent=2,
        )
        return self._chat(system, user)

    # ── Debrief ────────────────────────────────────────────────────────────

    def generate_debrief(
        self,
        debrief_input: dict,
        rag_text: str,
    ) -> str:
        """Generate the after-action debrief from structured data."""
        system = (
            "You are generating an after-action debrief for an "
            "emergency-response training session.\n\n"
            "Structure your debrief as follows:\n"
            "1. SUMMARY – one sentence overview\n"
            "2. WHAT WAS DONE CORRECTLY – list completed steps\n"
            "3. WHAT WAS MISSED – list missed steps with why they "
            "matter (reference protocol text)\n"
            "4. CRITICAL ERRORS – detail any, explain safety impact\n"
            "5. SCORES – present each dimension and the overall score\n"
            "6. RECOMMENDATIONS – 2-3 specific improvement actions\n"
            "7. ADAPTABILITY NOTE – mention that future sessions "
            "can target the trainee's weak areas\n\n"
            "Use the structured data and protocol text below.  "
            "Do NOT invent facts outside the provided data."
        )
        user = json.dumps(
            {
                "debrief_data": debrief_input,
                "supporting_protocol_text": rag_text,
            },
            indent=2,
        )
        return self._chat(system, user)

    # ── Private ────────────────────────────────────────────────────────────

    def _chat(self, system: str, user: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=0.4,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content or ""
