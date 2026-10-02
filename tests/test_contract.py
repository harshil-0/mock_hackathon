"""Phase 1 checks: config loads, corpus is present, the stub service matches the contract."""
from pathlib import Path

import pytest

from app import config
from app.schemas import AskResponse, ChunkRecord
from app.service import answer_question


def test_config_defaults_are_sane():
    assert config.CHUNK_MODE in {"dynamic", "fixed"}
    assert config.RETRIEVAL in {"hybrid", "dense"}
    assert config.MIN_TOKENS < config.TARGET_TOKENS < config.MAX_TOKENS
    assert config.TOP_K >= 1
    assert 0.0 <= config.GATE_LOW <= 1.0
    assert config.LLM_MODEL, "LLM_MODEL should have a default for the chosen provider"


def test_corpus_has_5_to_10_pdfs():
    pdfs = sorted(Path(config.PDF_DIR).glob("*.pdf"))
    assert 5 <= len(pdfs) <= 10, f"found {len(pdfs)} PDFs in {config.PDF_DIR}"


def test_every_pdf_has_extractable_text():
    fitz = pytest.importorskip("fitz")
    for pdf in Path(config.PDF_DIR).glob("*.pdf"):
        with fitz.open(pdf) as doc:
            text = " ".join(page.get_text() for page in doc).strip()
        assert len(text) > 500, f"{pdf.name} looks empty or scanned"


def test_stub_answered_matches_schema():
    resp = AskResponse(**answer_question("How many sick days do I get?"))
    assert resp.status == "answered"
    assert resp.citations and resp.citations[0].quote in resp.citations[0].snippet


def test_stub_not_found_matches_schema():
    resp = AskResponse(**answer_question("Do we have a unicorn policy?"))
    assert resp.status == "not_found"
    assert resp.citations == []
    assert resp.answer == config.NOT_FOUND_ANSWER


def test_empty_question_rejected():
    with pytest.raises(ValueError):
        answer_question("   ")


def test_chunk_record_example_validates():
    ChunkRecord(
        chunk_id="01_leave_policy::p1::c4", doc_name="01_leave_policy.pdf", doc_title="Leave Policy",
        section_path=["2. Leave Entitlements", "2.3 Sick Leave"], page_start=1, page_end=1,
        text="Employees are entitled to 12 paid sick days per calendar year.",
        embed_text="Leave Policy > 2. Leave Entitlements > 2.3 Sick Leave\nEmployees are entitled to 12 paid sick days.",
        token_count=14, chunk_index=4, prev_id="01_leave_policy::p2::c3", next_id=None,
    )
