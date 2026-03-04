"""Utility helpers shared across analyst modules."""

import os


def ensure_api_key():
    """Copy GEMINI_API_KEY to OPENAI_API_KEY if the latter is missing.

    This allows the codebase to accept either environment variable but
    ensures that the libraries we call (which expect OPENAI_API_KEY) always
    see a value.  It's idempotent and safe to call multiple times.
    """
    if not os.getenv("OPENAI_API_KEY") and os.getenv("GEMINI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.getenv("GEMINI_API_KEY")
