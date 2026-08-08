"""Rule-based theme labeling to bootstrap the theme classifier.

IMPORTANT: These labels are AUTOMATICALLY GENERATED using keyword/rule-based
logic. They are NOT human-annotated ground truth. They exist solely to
bootstrap a prototype theme classifier when the raw dataset has no theme labels.
"""

from __future__ import annotations

import re
from typing import Callable

# Each rule: (theme_name, list of keyword/phrase patterns)
# Patterns are matched as whole-word or phrase substrings (case-insensitive).
# Order matters: first match wins. Put more specific themes before "General Praise"
# and "Other".

ThemeRule = tuple[str, list[str]]

THEME_RULES: list[ThemeRule] = [
    (
        "Crash",
        [
            "crash",
            "crashes",
            "crashing",
            "crashed",
            "force close",
            "force-close",
            "force closed",
            "keeps closing",
            "stopped working",
            "app stopped",
        ],
    ),
    (
        "Login Problem",
        [
            "login",
            "log in",
            "log-in",
            "sign in",
            "sign-in",
            "can't sign in",
            "cannot sign in",
            "cant sign in",
            "can't log in",
            "cannot log in",
            "password",
            "authentication",
            "otp",
            "unable to login",
            "unable to log in",
        ],
    ),
    (
        "Performance Issue",
        [
            "slow",
            "sluggish",
            "lag",
            "laggy",
            "lagging",
            "freeze",
            "freezing",
            "frozen",
            "hang",
            "hanging",
            "takes forever",
            "loading forever",
            "not responding",
            "stutter",
            "battery drain",
        ],
    ),
    (
        "UI Problem",
        [
            "interface",
            "button",
            "layout",
            " ui ",
            "design",
            "screen looks",
            "hard to navigate",
            "confusing ui",
            "ugly",
            "cluttered",
            "font size",
            "dark mode broken",
        ],
    ),
    (
        "Feature Request",
        [
            "please add",
            "would like",
            "feature request",
            "wish there was",
            "wish you had",
            "should add",
            "need a feature",
            "missing feature",
            "hope you add",
            "can you add",
            "it would be nice",
        ],
    ),
    (
        "Ads Complaint",
        [
            "ads",
            "advertisement",
            "advertisements",
            "too many ads",
            "ad pop",
            "pop-up ads",
            "popup ads",
            "full of ads",
            "annoying ads",
            "forced ads",
        ],
    ),
    (
        "Security Concern",
        [
            "hack",
            "hacked",
            "hacker",
            "security",
            "privacy",
            "unsafe",
            "data breach",
            "steal",
            "stolen",
            "malware",
            "spyware",
            "permission",
            "personal data",
        ],
    ),
    (
        "Payment Problem",
        [
            "payment",
            "transaction",
            "refund",
            "upi",
            "money",
            "charged",
            "billing",
            "purchase failed",
            "payment failed",
            "double charged",
            "subscription",
            "in-app purchase",
            "iap",
        ],
    ),
    (
        "General Praise",
        [
            "great",
            "amazing",
            "love this",
            "love it",
            "excellent",
            "best app",
            "awesome",
            "fantastic",
            "perfect",
            "wonderful",
            "highly recommend",
            "very good",
            "so good",
        ],
    ),
]


def _compile_patterns(phrases: list[str]) -> list[re.Pattern[str]]:
    """Compile phrase list into regex patterns with word-boundary awareness."""
    compiled: list[re.Pattern[str]] = []
    for phrase in phrases:
        escaped = re.escape(phrase.strip().lower())
        # Allow flexible whitespace inside multi-word phrases
        escaped = escaped.replace(r"\ ", r"\s+")
        compiled.append(re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE))
    return compiled


# Pre-compile for speed
_COMPILED_RULES: list[tuple[str, list[re.Pattern[str]]]] = [
    (theme, _compile_patterns(phrases)) for theme, phrases in THEME_RULES
]


def assign_theme(text: str) -> str:
    """Assign a theme label using keyword/rule-based logic.

    Returns one of the theme category names, or "Other" if no rule matches.
    """
    if not text or not str(text).strip():
        return "Other"

    # Pad with spaces so patterns like " ui " can match at edges
    haystack = f" {str(text).lower()} "

    for theme, patterns in _COMPILED_RULES:
        for pattern in patterns:
            if pattern.search(haystack):
                return theme
    return "Other"


def assign_themes(texts: list[str]) -> list[str]:
    """Assign theme labels to a list of review texts."""
    return [assign_theme(t) for t in texts]


def get_theme_rules_summary() -> dict[str, list[str]]:
    """Return a readable summary of theme rules (for documentation/debugging)."""
    return {theme: phrases for theme, phrases in THEME_RULES}
