"""Layout-aware PDF extraction (PLAN.md section 3.1, steps 1-2). Owner: A.

Contract: turn one PDF into an ExtractedDoc that `chunking.py` can consume.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Line:
    text: str
    size: float
    bold: bool
    page: int          # 1-based
    y0: float
    y1: float


@dataclass
class Table:
    page: int
    y0: float
    markdown: str      # table rendered as Markdown rows


@dataclass
class ExtractedDoc:
    doc_name: str      # e.g. "leave_policy.pdf"
    doc_title: str     # e.g. "Leave Policy"
    pages: int
    lines: list[Line] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)


def extract_pdf(path: Path) -> ExtractedDoc:
    """Extract lines (with font size/bold/page/position) and tables; drop running
    headers, footers and bare page numbers."""
    raise NotImplementedError("Phase 2 (A)")
