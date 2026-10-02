"""Dynamic structure-aware chunker plus fixed-size baseline (PLAN.md section 3). Owner: A."""
from __future__ import annotations

from app.extract import ExtractedDoc


def chunk_document(doc: ExtractedDoc, mode: str = "dynamic") -> list[dict]:
    """Return chunk records exactly as in PLAN.md section 3.2 (see schemas.ChunkRecord).

    mode="dynamic": sections kept whole, split/merged to TARGET/MIN/MAX tokens.
    mode="fixed":   plain ~350-token chunks with 50-token overlap (baseline / CP1 fallback).
    """
    raise NotImplementedError("Phase 2 (A)")
