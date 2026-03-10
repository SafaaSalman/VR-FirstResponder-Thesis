"""
Action parser – maps free-text trainee input to protocol action IDs.

Uses the LLM with structured JSON output to perform the mapping.
"""

from __future__ import annotations

import json
from typing import List

from openai import OpenAI

from trainer import config


_SYSTEM_PROMPT = """\
You are an action parser for an emergency-response training simulation.

TASK
Given the trainee's message, identify which action(s) they are
attempting or describing.  Return ONLY a JSON object:

  {{"actions": ["action_id_1", "action_id_2"]}}

RULES
- Match the trainee's described actions to the closest action IDs from
  the list below.
- A single message may contain multiple actions.
- If the trainee is asking a question about the situation or the
  scenario, return ["ask_question"].
- If the trainee asks for a hint or for help, return ["request_hint"].
- If no action from the list matches at all, pick the closest
  reasonable match.  Only return IDs from the provided list.

AVAILABLE ACTIONS
{actions_json}
"""


class ActionParser:
    """Parse trainee natural-language input into protocol action IDs."""

    def __init__(
        self,
        possible_actions: List[dict],
        client: OpenAI | None = None,
    ) -> None:
        self.client = client or OpenAI(api_key=config.OPENAI_API_KEY)
        self.possible_actions = possible_actions
        self._system = _SYSTEM_PROMPT.format(
            actions_json=json.dumps(possible_actions, indent=2)
        )

    def parse(self, user_input: str) -> List[str]:
        """
        Return a list of action IDs extracted from *user_input*.
        Falls back to ``["ask_question"]`` on parse failure.
        """
        resp = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self._system},
                {"role": "user", "content": user_input},
            ],
        )
        text = resp.choices[0].message.content or "{}"
        try:
            data = json.loads(text)
            actions = data.get("actions", [])
            if isinstance(actions, list) and actions:
                return actions
        except json.JSONDecodeError:
            pass
        return ["ask_question"]
