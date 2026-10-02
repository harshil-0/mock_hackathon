"""The single entry point used by the UI and the eval. Owner: B.

PHASE 1 STUB: returns a canned response that matches the real contract so that C can build
the UI and D can build the eval harness before the pipeline exists. B replaces the body in
Phase 3 and removes the stub flag.
"""
from __future__ import annotations

from app import config


def answer_question(question: str) -> dict:
    """Return a dict matching schemas.AskResponse (PLAN.md section 7)."""
    if not question or not question.strip():
        raise ValueError("question must not be empty")

    # Anything mentioning "unicorn" exercises the not-found path of the UI; everything else
    # returns a sample answered response.
    if "unicorn" in question.lower():
        return {
            "status": "not_found",
            "answer": config.NOT_FOUND_ANSWER,
            "citations": [],
            "debug": {"gate": "blocked", "top_dense_score": 0.05, "retrieved_ids": [],
                      "llm_retries": 0, "latency_ms": 1, "stub": True},
        }

    quote = "entitled to 12 paid sick days per calendar year"
    return {
        "status": "answered",
        "answer": "Employees get 12 paid sick days per calendar year. (STUB ANSWER)",
        "citations": [{
            "chunk_id": "01_leave_policy::p1::c4",
            "doc_name": "01_leave_policy.pdf",
            "doc_title": "Leave Policy",
            "section": "2. Leave Entitlements > 2.3 Sick Leave",
            "page_start": 1,
            "page_end": 1,
            "quote": quote,
            "snippet": "Employees are " + quote + ". If you are absent for more than 2 ...",
        }],
        "debug": {"gate": "passed", "top_dense_score": 0.71,
                  "retrieved_ids": ["01_leave_policy::p1::c4"],
                  "llm_retries": 0, "latency_ms": 1, "stub": True},
    }
