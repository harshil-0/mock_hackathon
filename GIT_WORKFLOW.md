# Git Workflow for the Hackathon

> Goal: 4 people, under 8 hours, no merge disasters, and a `main` branch that always runs.
> Companion to [`PLAN.md`](./PLAN.md). Members A, B, C, D are the same as in the plan.
> **One branch per person.** You keep it all day and send your work to `dev` through small, frequent PRs.

---

## 1. The model in one picture

```
main     ●────────────────────────●────────────────────────────●     always demo-ready
                                  ▲ v0.1-e2e (4:00)             ▲ demo-v1 (7:30)
                                  │                             │
dev      ●──●──●──●──●──●──●──●──●──●──●──●──●──●──●──●──●──●──●
            ▲  ▲     ▲  ▲  ▲     ▲  ▲  ▲  ▲                   └─▶ release/demo-freeze
a/ingestion ┘  │     │  │  │     │  │  │  │                       (cut at 7:30)
b/retrieval-answering ┘  │  │     │  │  │  │
c/ui-demo ───────────────┘  │     │  │  │  │          each branch merges into dev several times
d/corpus-eval-docs ─────────┘     │  │  │  │          via PRs; the branch itself lives all day
```

**Three rules to remember**
1. Nobody commits directly to `main` or `dev`. Everything goes through a pull request (PR). The only exception is A's initial skeleton commit at the start.
2. One owner per file (see the file map in `PLAN.md`). Only the owner edits it, so conflicts are rare.
3. Your branch is long-lived, so **sync it from `dev` often** and **open a PR whenever a piece works** (every 30 to 60 minutes). Small PRs are easy to review and rarely conflict.

---

## 2. The branches

| Branch | Owner | Holds | Created from | Merges into |
|---|---|---|---|---|
| `main` | team | Always runnable. Tagged at milestones | initial commit | n/a |
| `dev` | team | Integration of everyone's work | `main` | `main` (4:00 and 7:30) |
| `a/ingestion` | A | `extract.py`, `chunking.py`, `embeddings.py`, `ingest.py`, `inspect_chunks.py`, `config.py`, chunking tests | `dev` | `dev` |
| `b/retrieval-answering` | B | `retriever.py`, `prompts.py`, `llm.py`, `answerer.py`, `validator.py`, `service.py`, tests | `dev` | `dev` |
| `c/ui-demo` | C | `schemas.py`, `streamlit_app.py`, `run_demo.sh`, optional `api.py` | `dev` | `dev` |
| `d/corpus-eval-docs` | D | `data/pdfs/`, `eval/*`, `README.md` | `dev` | `dev` |
| `release/demo-freeze` | A | Final demo code, plus the built index | `dev` (7:30) | `main` |

Protection settings (A sets these in GitHub, Settings, Branches):
- `main`: require a PR and 1 approval.
- `dev`: require a PR (approval encouraged, not enforced, so nobody blocks).
- `release/demo-freeze`: require a PR and 1 approval.

---

## 3. What each member sends to `dev` and when

These are **PRs from your single branch**, not separate branches.

### A: `a/ingestion`

| PR | Contents | Target time |
|---|---|---|
| A1 | Extraction, embeddings wrapper, `ingest.py`, **fixed** chunker, `data/index_fixed` build. This unblocks CP1 | **2:00** |
| A2 | Dynamic chunker (headings, sections, tables, lists, fallback) + `test_chunking.py` | **3:30** |
| A3 | `inspect_chunks.py`, `documents.json` stats, chunk-quality fixes found by the eval | **5:30** |

A's skeleton (folders, `requirements.txt`, `.env.example`, `.gitignore`, `config.py`, PR template) is the initial commit, see section 4.

### B: `b/retrieval-answering`

| PR | Contents | Target time |
|---|---|---|
| B1 | `prompts.py`, `llm.py` (cache, retry), `answerer.py`, `validator.py`, `test_validator.py` (using fixture chunks) | **2:00** |
| B2 | `retriever.py`: dense, BM25, RRF, neighbor expansion, soft gate, `test_retriever.py` | **3:00** |
| B3 | `service.py` with `answer_question()` wired to A's real index | **3:15** (CP1) |
| B4+ | Prompt, gate, and `TOP_K` tuning from dev-set failures. Several small PRs are fine | **6:30** |

### C: `c/ui-demo`

| PR | Contents | Target time |
|---|---|---|
| C1 | `schemas.py`, `streamlit_app.py` against a stub `answer_question` | **2:30** |
| C2 | Real service wired in, Sources expander, not-found state, debug panel, error handling | **3:30** |
| C3 | `run_demo.sh` with pre-flight checks (index present, key present, model downloaded) | **6:00** |
| C4 | **Optional:** `api.py` (FastAPI), only if everything else is green | **6:45** or dropped |

In hour 0 to 1, C helps D write PDFs. C sends the finished files to D (chat or shared drive) and **D commits them** on `d/corpus-eval-docs`, so each file still has one committer.

### D: `d/corpus-eval-docs`

| PR | Contents | Target time |
|---|---|---|
| D1 | `data/pdfs/*` (6 to 8 PDFs following the corpus checklist) | **1:30** |
| D2 | `run_eval.py` with the four metrics and CLI flags (`--index`, `--retrieval`) | **3:00** |
| D3 | `questions_dev.json`, `questions_heldout.json`, `results.md` with the ablation table | **5:30** (final numbers by **6:30**) |
| D4 | `README.md`, demo script, known limits | **7:15** |

---

## 4. Schedule

| Time | Event |
|---|---|
| 0:00 | A creates the GitHub repo and adds the other 3 as collaborators. A makes the **initial skeleton commit** on `main` (folders, `requirements.txt`, `.env.example`, `.gitignore`, `config.py`, `.github/pull_request_template.md`), then creates `dev` from it and sets branch protection |
| 0:00-0:30 | Everyone else reads `PLAN.md` and ticks the assumptions together |
| 0:30 | Everyone clones and creates their own branch from `dev` (section 5). Nobody creates another branch after this |
| 1:30 | D1 merged. A can test on real PDFs |
| 3:00 | **CP1 (walking skeleton):** A1, B2, B3, C1 merged. `dev` must run end to end, even with `CHUNK_MODE=fixed`. Anyone who sees it broken tells the owner and stops merging until it is fixed |
| 4:00 | `dev` merged into `main` via PR. A tags `v0.1-e2e` |
| 4:00-6:30 | Tuning PRs only, kept small. No new features after 5:00 |
| 6:45 | Last non-fix PR merged. Run the tests and the eval one more time on `dev` |
| 7:30 | **Freeze.** A cuts `release/demo-freeze` from `dev`, force-adds the built index (section 8), and opens a PR into `main`. After the merge, A tags `demo-v1` |
| 7:30-8:00 | Fixes only. Commit on **your own branch**, open a PR into `release/demo-freeze`, and once merged, also merge the same fix into `dev`/`main`. Rehearse from a clean clone of the tag |

---

## 5. Everyday commands

### Setup (each member, once, at 0:30)

```bash
git clone <repo-url>
cd policy-assistant
git checkout dev
git pull
git checkout -b a/ingestion          # your own branch: a/ingestion | b/retrieval-answering | c/ui-demo | d/corpus-eval-docs
git push -u origin a/ingestion
```

### Commit and push (every 20 to 30 minutes)

```bash
git add app/chunking.py tests/test_chunking.py     # add specific files, not "git add ."
git commit -m "feat(chunking): merge small sibling sections under MIN tokens"
git push
```

### Open a PR when a piece works (every 30 to 60 minutes)

1. Sync first (below), then push.
2. On GitHub, open a PR from your branch **into `dev`** and fill in the PR template.
3. Ask a teammate in chat for a 5-minute review. If nobody responds within 10 minutes, a teammate other than the author may merge after reading the diff.
4. Choose **Create a merge commit**, not squash. Squashing a long-lived branch rewrites its history and causes false conflicts on your next PR.
5. **Do not delete your branch** after merging. You keep using it.

### Sync your branch from `dev` (before every PR, and whenever someone merges something you need)

```bash
git fetch origin
git merge origin/dev                 # use merge, not rebase, on a long-lived shared branch
git push
```

If you get conflicts, see section 7.

---

## 6. Conventions

### Commit messages

Format: `type(scope): short description`

| type | Use for |
|---|---|
| `feat` | New behavior |
| `fix` | Bug fix |
| `test` | Tests or eval questions |
| `docs` | README, PLAN, comments |
| `chore` | Dependencies, config, scripts |

Examples: `feat(retriever): add RRF fusion`, `fix(validator): normalize whitespace before quote match`, `test(eval): add 3 not-found questions`.

### PR template

Saved by A as `.github/pull_request_template.md` in the initial commit:

```markdown
## What this changes
<!-- one or two sentences -->

## Files touched
<!-- list; they should all be yours per the file map in PLAN.md -->

## How I tested it
<!-- command + result, e.g. `pytest tests/test_chunking.py` passes -->

## Checklist
- [ ] Merged latest `dev` into my branch before opening this PR
- [ ] No `.env`, API keys, `data/cache/`, or `data/index_*/` committed
- [ ] Interfaces in PLAN.md section 7 not changed (or the team agreed)
- [ ] `streamlit run ui/streamlit_app.py` still starts (if you touched app code)
```

### Review checklist (5 minutes, reviewer)

- Does it only touch the author's files?
- Any secrets or large generated files?
- Does it match the interface in `PLAN.md` section 7?
- Does it run?

---

## 7. Shared files and conflict rules

| File | Rule |
|---|---|
| `requirements.txt` | A owns it. Need a library? Message A with the exact line. A adds it on `a/ingestion` and merges it quickly. Never reorder or reformat |
| `.env.example`, `config.py` | Same as above. Ask A; do not edit them yourself |
| `PLAN.md` | Anyone can propose a change in chat; the team must agree on interface changes. Never edit it silently |
| `README.md` | D only |
| Interfaces (`PLAN.md` section 7) | Changing a signature or a JSON field needs a message to all 4 **before** the PR |

Because every file has one owner and each person has one branch, real conflicts should be rare. If you hit one:

1. Stop. Do not force-push.
2. `git status` to see the conflicted files.
3. If a conflicted file is **not yours**, the other owner's version wins. Take it from `dev` with `git checkout origin/dev -- <file>`, then commit. Then message the owner to ask why you had touched it.
4. If it is yours, edit the markers (`<<<<<<<`, `=======`, `>>>>>>>`), run `git add <file>`, then `git commit`.
5. Still stuck after 10 minutes? Ask the other owner in chat. Do not guess.

---

## 8. Generated files and the demo index

| Path | In Git? | Why |
|---|---|---|
| `.env` | **Never** | Contains the API key |
| `data/cache/` | No (gitignored) | Local cache, large and machine-specific |
| `data/index_dynamic/`, `data/index_fixed/` | No during development (gitignored) | Binary files change on every ingest and conflict |
| `data/index_dynamic/` at **freeze** | **Yes, force-added on `release/demo-freeze` only** | The demo machine should not need to re-embed or download anything |
| `data/pdfs/` | Yes | Small and needed by everyone |

Force-add at the freeze (A does this):

```bash
git checkout dev && git pull
git checkout -b release/demo-freeze
python -m app.ingest --mode dynamic
git add -f data/index_dynamic/ data/documents.json
git commit -m "chore(release): include built index for demo"
git push -u origin release/demo-freeze
```

Also pre-download the embedding model on the demo laptop while you still have network access.

---

## 9. When something goes wrong

| Problem | Fix |
|---|---|
| Committed `.env` or an API key | **Rotate the key immediately** (it is compromised the moment it is pushed). Then remove the file from the repo: `git rm --cached .env`, commit, push. History cleanup is not worth the time; the new key is what matters |
| Committed `data/cache/` or an index | `git rm -r --cached data/cache`, commit, push. Make sure `.gitignore` lists it |
| Pushed to the wrong branch | Tell the team. Do not force-push. Revert with `git revert <sha>` on that branch |
| `dev` is broken | Whoever sees it first posts in chat. The author of the last merged PR fixes it on their own branch or reverts the merge within 10 minutes: `git revert -m 1 <merge-sha>` on a branch, then PR |
| Need to switch work temporarily | `git stash`, switch, later `git stash pop` |
| Need a teammate's unmerged work | `git fetch origin && git checkout -b try-b origin/b/retrieval-answering`. Do not commit on it; switch back to your own branch afterward |
| Never do | `git push --force` to `main`, `dev`, or `release/demo-freeze`, and never force-push your own branch once someone else has pulled it |

---

## 10. Quick reference: all branches

| Branch | Owner | Created from | Merges into | Due |
|---|---|---|---|---|
| `main` | team | initial commit | n/a | tags: `v0.1-e2e` at 4:00, `demo-v1` at 7:30 |
| `dev` | team | `main` | `main` | at 4:00 and 7:30 |
| `a/ingestion` | A | `dev` | `dev` | PRs at 2:00, 3:30, 5:30 |
| `b/retrieval-answering` | B | `dev` | `dev` | PRs at 2:00, 3:00, 3:15, then tuning until 6:30 |
| `c/ui-demo` | C | `dev` | `dev` | PRs at 2:30, 3:30, 6:00, optional 6:45 |
| `d/corpus-eval-docs` | D | `dev` | `dev` | PRs at 1:30, 3:00, 5:30, 7:15 |
| `release/demo-freeze` | A | `dev` | `main` | 7:30 |
