"""
Centralised pipeline configuration.

``PipelineConfig`` is a frozen dataclass whose values are resolved in this
priority order (highest wins):

1. Explicit keyword arguments at construction time
2. Environment variables (``PIPELINE_<UPPER_FIELD>``)
3. YAML configuration file (``--config`` or ``pipeline/config.yaml``)
4. Dataclass defaults

Usage::

    from pipeline.config import get_config

    cfg = get_config()                      # defaults + env overrides
    cfg = get_config("custom.yaml")         # from YAML file + env
    cfg = get_config(model="gpt-4o-mini")   # explicit override
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

logger = logging.getLogger("pipeline.config")

# ---------------------------------------------------------------------------
# Config dataclass
# ---------------------------------------------------------------------------

@dataclass
class PipelineConfig:
    """All tuneable pipeline settings in one place."""

    # ── LLM settings ──────────────────────────────────────────────
    model: str = "gpt-4o"
    temperature_extract: float = 0.1
    temperature_summarize: float = 0.05
    temperature_kb: float = 0.15

    # ── Batch sizes (token budgets) ────────────────────────────────
    # Defaults are conservative to work with OpenAI Tier-1 (30K TPM).
    # Users on higher tiers can raise these via env vars or YAML.
    # The actual per-request budget is further capped at runtime to
    # ``tpm_limit * 0.65`` so that prompt overhead + output reservation
    # (which OpenAI counts against TPM) don't push the request over.
    max_single_pass_tokens: int = 25_000
    summary_batch_tokens: int = 20_000
    kb_batch_tokens: int = 12_000

    # ── TPM pacing ────────────────────────────────────────────────
    # Tokens-per-minute limit for your OpenAI org/tier.  Used to
    # calculate inter-batch sleep so sequential calls don't exceed
    # the quota.  Set to 0 to disable pacing.
    tpm_limit: int = 30_000

    # ── Overlap ───────────────────────────────────────────────────
    overlap_sections: int = 2

    # ── Retry settings (tenacity) ─────────────────────────────────
    max_retries: int = 8
    retry_min_wait: float = 15.0
    retry_max_wait: float = 120.0

    # ── Server settings ───────────────────────────────────────────
    max_upload_size_mb: int = 50
    max_concurrent_jobs: int = 3
    job_ttl_hours: int = 2

    # ── Derived (computed once) ───────────────────────────────────
    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def job_ttl_seconds(self) -> int:
        return self.job_ttl_hours * 3600


# ---------------------------------------------------------------------------
# Loading helpers
# ---------------------------------------------------------------------------

_ENV_PREFIX = "PIPELINE_"

# Map Python types to casting functions for env-var parsing
_CASTERS: dict[type, Any] = {
    str: str,
    int: int,
    float: float,
    bool: lambda v: v.lower() in ("1", "true", "yes"),
}


def _apply_env_overrides(values: dict[str, Any]) -> dict[str, Any]:
    """Override *values* with matching ``PIPELINE_*`` environment variables."""
    for f in fields(PipelineConfig):
        env_key = _ENV_PREFIX + f.name.upper()
        env_val = os.environ.get(env_key)
        if env_val is not None:
            caster = _CASTERS.get(f.type, str)  # type: ignore[arg-type]
            try:
                values[f.name] = caster(env_val)
                logger.debug("Config override from env: %s=%s", env_key, env_val)
            except (ValueError, TypeError):
                logger.warning(
                    "Ignoring invalid env var %s=%r (expected %s)",
                    env_key, env_val, f.type,
                )
    return values


def _load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML config file.  Returns empty dict if file not found."""
    p = Path(path)
    if not p.exists():
        return {}
    try:
        import yaml  # optional dependency

        with open(p, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        logger.info("Loaded config from %s", p)
        return data
    except ImportError:
        logger.warning(
            "PyYAML not installed — cannot load %s.  Install with: "
            "pip install pyyaml",
            p,
        )
        return {}
    except Exception as exc:
        logger.warning("Failed to load config YAML %s: %s", p, exc)
        return {}


# ---------------------------------------------------------------------------
# Public factory
# ---------------------------------------------------------------------------

# Singleton so repeated calls without arguments return the same object
_cached_config: PipelineConfig | None = None


def get_config(
    yaml_path: str | Path | None = None,
    **overrides: Any,
) -> PipelineConfig:
    """Build a ``PipelineConfig`` with layered resolution.

    Resolution order (highest priority wins):
    1. *overrides* keyword arguments
    2. Environment variables (``PIPELINE_<FIELD>``)
    3. YAML file (explicit *yaml_path* or ``pipeline/config.yaml``)
    4. Dataclass defaults
    """
    global _cached_config

    # Fast path: return cached if no customisation requested
    if yaml_path is None and not overrides and _cached_config is not None:
        return _cached_config

    # Start with dataclass defaults
    values: dict[str, Any] = {f.name: f.default for f in fields(PipelineConfig)}

    # Layer 1: YAML file (lowest priority override)
    if yaml_path:
        values.update(_load_yaml(yaml_path))
    else:
        # Try default location: pipeline/config.yaml next to this file
        default_yaml = Path(__file__).parent / "config.yaml"
        values.update(_load_yaml(default_yaml))

    # Layer 2: Environment variables
    values = _apply_env_overrides(values)

    # Layer 3: Explicit overrides (highest priority)
    for k, v in overrides.items():
        if k in values:
            values[k] = v

    cfg = PipelineConfig(**values)

    # Cache only if using defaults (no explicit yaml / overrides)
    if yaml_path is None and not overrides:
        _cached_config = cfg

    return cfg
