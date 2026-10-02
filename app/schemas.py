"""Pydantic models that pin down the contract in PLAN.md sections 3.2 and 7. Owner: C."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChunkRecord(BaseModel):
    """One line of chunks.jsonl (PLAN.md section 3.2)."""

    chunk_id: str
    doc_name: str
    doc_title: str
    section_path: list[str] = Field(default_factory=list)
    page_start: int
    page_end: int
    text: str
    embed_text: str
    token_count: int
    chunk_index: int
    prev_id: Optional[str] = None
    next_id: Optional[str] = None
    chunk_mode: Literal["dynamic", "fixed", "fallback"] = "dynamic"


class Citation(BaseModel):
    chunk_id: str
    doc_name: str
    doc_title: str
    section: str
    page_start: int
    page_end: int
    quote: str
    snippet: str


class DebugInfo(BaseModel):
    gate: Literal["passed", "blocked"] = "passed"
    top_dense_score: float = 0.0
    retrieved_ids: list[str] = Field(default_factory=list)
    llm_retries: int = 0
    latency_ms: int = 0
    stub: bool = False


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class AskResponse(BaseModel):
    status: Literal["answered", "not_found"]
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    debug: DebugInfo = Field(default_factory=DebugInfo)
