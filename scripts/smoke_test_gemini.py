"""
Smoke-test the configured Gemini models with a minimal prompt.

Usage:
    .venv/bin/python scripts/smoke_test_gemini.py
"""

from pathlib import Path
import sys

import google.generativeai as genai

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config


def main() -> int:
    if not config.GEMINI_API_KEY:
        print("GEMINI_API_KEY is not set.")
        return 1

    genai.configure(api_key=config.GEMINI_API_KEY)
    models = [config.GEMINI_MODEL, *config.GEMINI_FALLBACK_MODELS]
    prompt = "Reply with exactly: GEMINI_OK"

    ok = False
    for model_name in dict.fromkeys(model for model in models if model):
        print(f"Testing {model_name}...")
        try:
            model = genai.GenerativeModel(model_name=model_name)
            response = model.generate_content(prompt)
            text = (getattr(response, "text", "") or "").strip()
            print(f"  OK: {text[:120]}")
            ok = True
        except Exception as exc:
            print(f"  ERROR: {exc}")

    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
