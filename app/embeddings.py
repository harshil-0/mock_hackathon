"""Embedding wrapper with disk cache. Owner: A."""
from __future__ import annotations

import numpy as np


def embed(texts: list[str], is_query: bool = False) -> np.ndarray:
    """Return an (n, d) float32 matrix of L2-normalised embeddings, so cosine = dot product."""
    raise NotImplementedError("Phase 2 (A)")
