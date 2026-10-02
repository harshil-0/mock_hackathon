#!/usr/bin/env bash
# Phase 1 git bootstrap (GIT_WORKFLOW.md section 4). Run ONCE, by one person (A / the repo owner).
#
#   bash scripts/bootstrap_git.sh                       # local repo only
#   bash scripts/bootstrap_git.sh <git-remote-url>      # also push to GitHub
#
# Creates: main (initial skeleton commit), dev, and the four member branches (all from dev).
set -euo pipefail
cd "$(dirname "$0")/.."

REMOTE="${1:-}"
MEMBER_BRANCHES=(a/ingestion b/retrieval-answering c/ui-demo d/corpus-eval-docs)

if [ -d .git ]; then echo "Already a git repo. Aborting."; exit 1; fi

git init -q -b main
git add -A
git commit -q -m "chore: initial skeleton (Phase 1): config, interface stubs, sample corpus, plan"
git branch dev
for b in "${MEMBER_BRANCHES[@]}"; do git branch "$b" dev; done

echo "Created branches:"; git branch --format='  %(refname:short)'

if [ -n "$REMOTE" ]; then
  git remote add origin "$REMOTE"
  git push -u origin main dev "${MEMBER_BRANCHES[@]}"
  git tag v0.0-phase1 && git push -q origin v0.0-phase1
  echo "Pushed. Now set branch protection on GitHub (Settings > Branches): main and dev require a PR."
else
  echo
  echo "No remote given. To publish later:"
  echo "  git remote add origin <url> && git push -u origin main dev ${MEMBER_BRANCHES[*]}"
fi

echo
echo "Each member now runs:  git clone <url> && cd policy-assistant && git checkout <their-branch>"
echo "  A: a/ingestion   B: b/retrieval-answering   C: c/ui-demo   D: d/corpus-eval-docs"
