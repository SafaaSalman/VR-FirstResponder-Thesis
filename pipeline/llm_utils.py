"""
Shared LLM call helpers with retry logic and robust JSON recovery.

Every LLM interaction in the pipeline should use these helpers instead
of calling client.chat.completions.create() directly.  This ensures:
  - Automatic retry with exponential backoff on transient API errors
  - Multi-strategy JSON recovery when the LLM returns malformed output
  - Consistent token-usage logging across all modules
"""

from __future__ import annotations

import json
import re
import logging
import time
from typing import Any, Callable

import tiktoken
from openai import OpenAI
import openai
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from .config import PipelineConfig, get_config

logger = logging.getLogger("pipeline.llm")

# ── Token counting ─────────────────────────────────────────────────────────

# Cache the encoder to avoid re-loading on every call
_encoder_cache: dict[str, tiktoken.Encoding] = {}


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count the number of tokens in *text* for the given *model*.

    Uses tiktoken with a cached encoder.  Falls back to the cl100k_base
    encoding if the model isn't directly supported.
    """
    if model not in _encoder_cache:
        try:
            _encoder_cache[model] = tiktoken.encoding_for_model(model)
        except KeyError:
            _encoder_cache[model] = tiktoken.get_encoding("cl100k_base")
    return len(_encoder_cache[model].encode(text))

# ── Retry configuration ───────────────────────────────────────────────────

RETRYABLE_EXCEPTIONS = (
    openai.RateLimitError,
    openai.APITimeoutError,
    openai.APIConnectionError,
    openai.InternalServerError,
)


# ── Public API ─────────────────────────────────────────────────────────────

def call_llm_json(
    client: OpenAI,
    model: str,
    system: str,
    user: str,
    temperature: float = 0.1,
    progress: Callable[[str], None] | None = None,
) -> dict:
    """Call the LLM expecting a JSON response, with retry + recovery.

    1.  Calls the API with ``response_format=json_object``.
    2.  On transient errors (429, 500, timeout, connection) retries up
        to ``MAX_RETRIES`` times with exponential backoff.
    3.  Attempts multi-strategy JSON parsing on the raw response.
    4.  If all parsing strategies fail, makes one "fix this JSON" call.
    5.  Logs token usage via *progress* callback.

    Returns the parsed dict.
    Raises ``LLMJsonError`` if all recovery strategies are exhausted.
    """
    _log = progress or _noop

    raw_text = _call_api_with_retry(
        client, model, system, user, temperature,
        response_format={"type": "json_object"},
        progress=_log,
    )

    # ── Try to parse ───────────────────────────────────────────────
    result = _try_parse_json(raw_text)
    if result is not None:
        return result

    # ── Recovery: ask the LLM to fix its own JSON ──────────────────
    _log("⚠ JSON parse failed — attempting LLM self-repair...")
    logger.warning("JSON parse failed on raw output (%d chars), attempting repair", len(raw_text))

    repair_system = (
        "The following text was supposed to be valid JSON but has syntax errors. "
        "Fix it and return ONLY the corrected valid JSON.  Do not add commentary."
    )
    repair_user = f"Broken JSON:\n{raw_text[:12_000]}"

    fixed_text = _call_api_with_retry(
        client, model, repair_system, repair_user, 0.0,
        response_format={"type": "json_object"},
        progress=_log,
    )

    result = _try_parse_json(fixed_text)
    if result is not None:
        _log("✓ JSON repaired successfully")
        return result

    raise LLMJsonError(
        f"All JSON recovery strategies failed. "
        f"Raw output starts with: {raw_text[:200]!r}"
    )


def call_llm_text(
    client: OpenAI,
    model: str,
    system: str,
    user: str,
    temperature: float = 0.1,
    progress: Callable[[str], None] | None = None,
) -> str:
    """Call the LLM expecting a plain-text response, with retry.

    Same retry logic as ``call_llm_json`` but skips JSON parsing.
    Returns the raw text string.
    """
    _log = progress or _noop

    return _call_api_with_retry(
        client, model, system, user, temperature,
        response_format=None,
        progress=_log,
    )


# ── Error classes ──────────────────────────────────────────────────────────

class LLMJsonError(Exception):
    """Raised when we cannot recover valid JSON from the LLM output."""


class TokenBudgetExceeded(Exception):
    """Raised when a single request exceeds the org's TPM quota.

    This is NOT retryable — the batch must be split into smaller pieces.
    """


# ── TPM pacing ─────────────────────────────────────────────────────────────

def tpm_pace(tokens_used: int) -> None:
    """Sleep long enough to avoid exceeding the TPM quota.

    Call this **after** each successful LLM call in a sequential-batch
    loop.  If ``tpm_limit`` is 0 in the config, pacing is disabled.

    The function inflates *tokens_used* by 30 % to account for prompt
    overhead (system prompt, user wrapper, chat framing) and the output
    tokens that OpenAI also counts against TPM.
    """
    cfg = get_config()
    if cfg.tpm_limit <= 0:
        return
    # Scale up to account for system prompt, user wrapper, formatting,
    # and output tokens that OpenAI counts against the TPM quota.
    estimated_total = int(tokens_used * 1.3)
    # How many seconds of the 60-s TPM window did this call consume?
    wait = estimated_total / cfg.tpm_limit * 60
    # Only sleep if the delay is meaningful (> 1 s)
    if wait > 1:
        logger.info(
            "TPM pacing: sleeping %.1fs after ~%d tokens (est. total)",
            wait, estimated_total,
        )
        time.sleep(wait)


# ── Internal helpers ───────────────────────────────────────────────────────

def _noop(msg: str) -> None:
    """Default no-op progress callback."""


def _call_api_with_retry(
    client: OpenAI,
    model: str,
    system: str,
    user: str,
    temperature: float,
    response_format: dict | None,
    progress: Callable[[str], None],
) -> str:
    """Make the actual API call with tenacity retry wrapping."""

    cfg = get_config()
    attempt_num = 0

    @retry(
        retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
        stop=stop_after_attempt(cfg.max_retries),
        wait=wait_exponential(multiplier=1, min=cfg.retry_min_wait, max=cfg.retry_max_wait),
        reraise=True,
    )
    def _do_call() -> str:
        nonlocal attempt_num
        attempt_num += 1
        if attempt_num > 1:
            progress(f"⟳ Retry attempt {attempt_num}/{cfg.max_retries}...")
            logger.info("Retry attempt %d/%d", attempt_num, cfg.max_retries)

        kwargs: dict[str, Any] = dict(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        if response_format is not None:
            kwargs["response_format"] = response_format

        try:
            response = client.chat.completions.create(**kwargs)
        except openai.RateLimitError as exc:
            msg = str(exc)

            # ── Quota / billing exhausted ──────────────────────────
            # 429 with 'insufficient_quota' = billing issue, NOT a
            # transient rate-limit.  Retrying just wastes minutes.
            if "insufficient_quota" in msg:
                logger.error(
                    "OpenAI quota exhausted: %s\n"
                    "Check project spending limits at "
                    "https://platform.openai.com/settings/organization/limits",
                    msg,
                )
                raise TokenBudgetExceeded(
                    "OpenAI quota exhausted — check billing / project spending "
                    "limits at https://platform.openai.com/settings/organization/limits"
                ) from exc

            # ── Single request exceeds TPM ─────────────────────────
            # "Request too large for <model> … Limit N, Requested M"
            # means the single request exceeds the org's TPM quota.
            # Retrying won't help — the batch must be made smaller.
            if "Request too large" in msg:
                logger.error(
                    "Request exceeds TPM quota: %s.  "
                    "Reduce batch sizes via PIPELINE_SUMMARY_BATCH_TOKENS / "
                    "PIPELINE_KB_BATCH_TOKENS env vars or a config YAML.",
                    msg,
                )
                raise TokenBudgetExceeded(msg) from exc

            raise  # normal rate-limit — let tenacity retry

        # ── Log token usage ────────────────────────────────────────
        usage = response.usage
        if usage:
            progress(
                f"Tokens: {usage.prompt_tokens:,} in / "
                f"{usage.completion_tokens:,} out"
            )
            logger.debug(
                "Token usage: %d prompt + %d completion = %d total",
                usage.prompt_tokens,
                usage.completion_tokens,
                usage.total_tokens,
            )

        return response.choices[0].message.content or ""

    return _do_call()


def _try_parse_json(text: str) -> dict | None:
    """Try multiple strategies to extract valid JSON from *text*.

    Strategy order:
    1. Direct ``json.loads``
    2. Strip markdown fences (```json ... ```)
    3. Regex-extract first ``{ ... }`` block
    """
    # Strategy 1: direct parse
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass

    # Strategy 2: strip markdown code fences
    stripped = _strip_markdown_fences(text)
    if stripped != text:
        try:
            return json.loads(stripped)
        except (json.JSONDecodeError, TypeError):
            pass

    # Strategy 3: regex extract first { ... } block
    extracted = _extract_json_block(text)
    if extracted:
        try:
            return json.loads(extracted)
        except (json.JSONDecodeError, TypeError):
            pass

    return None


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` fences."""
    # Match ```json\n...\n``` or ```\n...\n```
    m = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text


def _extract_json_block(text: str) -> str | None:
    """Extract the first balanced { ... } JSON object from text."""
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False

    for i in range(start, len(text)):
        c = text[i]

        if escape:
            escape = False
            continue

        if c == "\\":
            escape = True
            continue

        if c == '"' and not escape:
            in_string = not in_string
            continue

        if in_string:
            continue

        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

    return None
