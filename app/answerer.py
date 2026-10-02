"""Builds the prompt, calls the LLM, parses its JSON. Owner: B."""
from __future__ import annotations


def generate_answer(question: str, chunks: list[dict]) -> dict:
    """Return {"status", "answer", "citations": [{"chunk_id", "quote"}]} parsed from the LLM."""
    raise NotImplementedError("Phase 3 (B)")
