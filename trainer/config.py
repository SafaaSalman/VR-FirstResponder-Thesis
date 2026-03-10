"""Configuration for the procedural training engine."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
PROTOCOLS_DIR = BASE_DIR / "protocols"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
SCENARIOS_DIR = BASE_DIR / "scenarios"

# ── OpenAI ─────────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# ── Engine defaults ────────────────────────────────────────────────────────
MAX_HINT_LEVEL = 3
DEFAULT_PROTOCOL = "earthquake_building_evacuation_v1"
DEFAULT_SCENARIO = "eq_moderate_injury"
RAG_TOP_K = 3

# ── Scoring weights (must sum to 1.0) ─────────────────────────────────────
SCORE_WEIGHTS = {
    "sequence_adherence": 0.25,
    "critical_compliance": 0.30,
    "branch_correctness": 0.15,
    "hazard_awareness": 0.15,
    "completion_quality": 0.15,
}
