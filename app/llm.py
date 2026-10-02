"""LLM client: JSON output, retry, disk cache. Owner: B."""
from __future__ import annotations


def call_llm(system: str, user: str) -> str:
    """Return the raw model text. Provider and model come from app.config."""
    raise NotImplementedError("Phase 3 (B)")
