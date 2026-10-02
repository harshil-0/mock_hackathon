"""CLI: extract -> chunk -> embed -> write index. Owner: A.

    python -m app.ingest --mode dynamic     # writes data/index_dynamic/
    python -m app.ingest --mode fixed       # writes data/index_fixed/
"""
from __future__ import annotations

import argparse


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build the policy index.")
    parser.add_argument("--mode", choices=["dynamic", "fixed"], default="dynamic")
    parser.parse_args(argv)
    raise NotImplementedError("Phase 2 (A)")


if __name__ == "__main__":
    main()
