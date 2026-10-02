"""Hybrid retrieval: dense + BM25, RRF fusion, neighbour expansion, soft gate. Owner: B."""
from __future__ import annotations


def retrieve(question: str, k: int = 5) -> list[dict]:
    """Return chunk records (PLAN.md section 3.2) plus:
    score (fused), dense_score, bm25_score, source ('retrieved' | 'neighbor'). Best first."""
    raise NotImplementedError("Phase 3 (B)")
