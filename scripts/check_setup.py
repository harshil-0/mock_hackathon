"""Pre-flight check. Run this on EVERY teammate's machine before Phase 2.

    python scripts/check_setup.py            # environment, packages, keys, corpus
    python scripts/check_setup.py --embed    # also loads the embedding model (downloads it once)
    python scripts/check_setup.py --ping     # also makes one tiny LLM call to prove the key works
"""
from __future__ import annotations

import argparse
import importlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

OK, BAD = "[ ok ]", "[FAIL]"
failures = 0


def report(ok: bool, msg: str) -> None:
    global failures
    print(f"{OK if ok else BAD} {msg}")
    if not ok:
        failures += 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--embed", action="store_true", help="load the embedding model and embed one sentence")
    parser.add_argument("--ping", action="store_true", help="make one tiny LLM call")
    args = parser.parse_args()

    report(sys.version_info >= (3, 10), f"Python {sys.version.split()[0]} (need 3.10+)")

    for module, pip_name in [("fitz", "pymupdf"), ("numpy", "numpy"), ("sentence_transformers", "sentence-transformers"),
                             ("rank_bm25", "rank-bm25"), ("pydantic", "pydantic"), ("dotenv", "python-dotenv"),
                             ("streamlit", "streamlit"), ("pytest", "pytest")]:
        try:
            importlib.import_module(module)
            report(True, f"package {pip_name}")
        except Exception as exc:  # noqa: BLE001
            report(False, f"package {pip_name} not importable ({type(exc).__name__}): pip install -r requirements.txt")

    from app import config

    report((config.ROOT / ".env").exists(), ".env exists (copy .env.example to .env)")
    key_name = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}.get(config.LLM_PROVIDER)
    report(bool(key_name and os.getenv(key_name)),
           f"{key_name or 'LLM_PROVIDER'} is set for provider '{config.LLM_PROVIDER}' (model: {config.LLM_MODEL})")

    pdfs = sorted(config.PDF_DIR.glob("*.pdf"))
    report(5 <= len(pdfs) <= 10, f"{len(pdfs)} PDFs in data/pdfs (need 5 to 10)")

    if args.embed:
        try:
            from sentence_transformers import SentenceTransformer
            vec = SentenceTransformer(config.EMBED_MODEL).encode(["hello policy"], normalize_embeddings=True)
            report(vec.shape[0] == 1, f"embedding model {config.EMBED_MODEL} loads (dim {vec.shape[1]})")
        except Exception as exc:  # noqa: BLE001
            report(False, f"embedding model failed: {type(exc).__name__}: {exc}")

    if args.ping:
        try:
            if config.LLM_PROVIDER == "anthropic":
                import anthropic
                r = anthropic.Anthropic().messages.create(
                    model=config.LLM_MODEL, max_tokens=10,
                    messages=[{"role": "user", "content": "Reply with the single word: OK"}])
                text = r.content[0].text
            elif config.LLM_PROVIDER == "openai":
                import openai
                r = openai.OpenAI().chat.completions.create(
                    model=config.LLM_MODEL, max_tokens=10,
                    messages=[{"role": "user", "content": "Reply with the single word: OK"}])
                text = r.choices[0].message.content
            else:
                raise ValueError(f"unknown LLM_PROVIDER {config.LLM_PROVIDER!r}")
            report(True, f"LLM call works, model said: {text.strip()[:30]!r}")
        except Exception as exc:  # noqa: BLE001
            report(False, f"LLM call failed: {type(exc).__name__}: {exc}")

    print()
    print("All checks passed." if failures == 0 else f"{failures} check(s) failed. Fix them before Phase 2.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
