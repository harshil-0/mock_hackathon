# Policy Assistant

Question answering over 5 to 10 company policy PDFs. Every answer cites its source (document, section, page, verbatim quote). If the documents do not cover the question, it says "not found".

**Status:** Phase 1 complete (skeleton, contracts, sample corpus). Pipeline code arrives in Phases 2 to 4.

- Plan, architecture, work split: [PLAN.md](./PLAN.md)
- Branches, PRs, merge schedule: [GIT_WORKFLOW.md](./GIT_WORKFLOW.md)
- Sample corpus answer key: [eval/corpus_facts.md](./eval/corpus_facts.md)

## Setup

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt                          # sentence-transformers pulls in torch: install early
cp .env.example .env                                     # add your API key
python scripts/check_setup.py --embed --ping             # every teammate must pass this
pytest -q                                                # Phase 1 contract tests
```

## Repo layout

See PLAN.md section 9 (file map). One owner per file.

## Assumptions and known limits

To be completed by D in Phase 6 (see PLAN.md section 1).
