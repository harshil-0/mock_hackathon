"""Central configuration. Owner: A.

All switches come from environment variables (see .env.example) so that the
ablation in PLAN.md section 12 can be run without editing code.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _env(name: str, default: str = "") -> str:
    value = os.getenv(name)
    return default if value is None or value.strip() == "" else value.strip()


# --- Paths -----------------------------------------------------------------
DATA_DIR = ROOT / "data"
PDF_DIR = DATA_DIR / "pdfs"
CACHE_DIR = DATA_DIR / "cache"
DOCUMENTS_JSON = DATA_DIR / "documents.json"

# --- Switches --------------------------------------------------------------
CHUNK_MODE = _env("CHUNK_MODE", "dynamic")          # dynamic | fixed
RETRIEVAL = _env("RETRIEVAL", "hybrid")             # hybrid | dense
INDEX_DIR = Path(_env("INDEX_DIR", str(DATA_DIR / f"index_{CHUNK_MODE}")))
if not INDEX_DIR.is_absolute():
    INDEX_DIR = ROOT / INDEX_DIR

# --- Chunking (PLAN.md section 3) -------------------------------------------
TARGET_TOKENS = 350
MIN_TOKENS = 120
MAX_TOKENS = 600
FIXED_CHUNK_TOKENS = 350
FIXED_OVERLAP_TOKENS = 50
FALLBACK_OVERLAP_RATIO = 0.15
MIN_HEADINGS_FOR_STRUCTURE = 3
HEADING_SIZE_RATIO = 1.15
TOKENS_PER_WORD = 1.3                                # token estimate = words * 1.3

# --- Retrieval (PLAN.md section 4) ------------------------------------------
EMBED_MODEL = _env("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
DENSE_TOP_N = 20
BM25_TOP_N = 20
RRF_K = 60
TOP_K = int(_env("TOP_K", "5"))
GATE_LOW = float(_env("GATE_LOW", "0.20"))
NEIGHBOR_EXPAND_TOP = 2
MAX_CONTEXT_TOKENS = 2500

# --- Answering and validation (PLAN.md section 5) ---------------------------
LLM_PROVIDER = _env("LLM_PROVIDER", "anthropic")     # anthropic | openai
_DEFAULT_MODELS = {"anthropic": "claude-sonnet-5-5", "openai": "gpt-4o-mini"}
LLM_MODEL = _env("LLM_MODEL", _DEFAULT_MODELS.get(LLM_PROVIDER, ""))
LLM_TEMPERATURE = 0.0
QUOTE_MAX_WORDS = 25
NOT_FOUND_ANSWER = "Not found in the provided policy documents."
