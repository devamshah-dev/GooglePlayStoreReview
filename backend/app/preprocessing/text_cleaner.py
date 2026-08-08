"""Lightweight text preprocessing for TF-IDF classification."""

from __future__ import annotations

import re
from typing import Any

# Keep negation tokens and emphasis punctuation that carry sentiment signal.
_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_HTML_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")
# Remove punctuation except ! ? ' which help sentiment / contractions
_PUNCT_RE = re.compile(r"[^\w\s!?\']+")


def clean_text(text: Any) -> str:
    """Clean a single review string for TF-IDF vectorization.

    Steps:
    - coerce to string
    - lowercase
    - strip URLs and HTML
    - remove unnecessary punctuation (keep ! ? ')
    - normalize whitespace
    """
    if text is None:
        return ""

    text = str(text)
    text = text.lower()
    text = _URL_RE.sub(" ", text)
    text = _HTML_RE.sub(" ", text)
    text = _PUNCT_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def clean_texts(texts: list[Any]) -> list[str]:
    """Clean a list of review texts."""
    return [clean_text(t) for t in texts]
