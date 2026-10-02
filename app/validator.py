"""Citation validation and not-found enforcement (PLAN.md section 5). Owner: B."""
from __future__ import annotations


def validate(result: dict, chunks: list[dict]) -> dict:
    """Drop citations whose chunk_id is not in `chunks` or whose quote is not a substring of
    that chunk's text; if nothing valid remains, force status "not_found"."""
    raise NotImplementedError("Phase 3 (B)")
