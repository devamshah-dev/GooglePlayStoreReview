"""CSV column detection and normalization for Google Play review datasets."""

from __future__ import annotations

from typing import Optional

import pandas as pd

# Accepted source column names (case-sensitive match first, then case-insensitive).
RATING_CANDIDATES = ["Rating", "rating", "score", "Score"]
REVIEW_CANDIDATES = [
    "Review",
    "review",
    "Review Text",
    "review_text",
    "reviewText",
    "Content",
    "content",
]


class ColumnMappingError(ValueError):
    """Raised when required CSV columns cannot be detected."""


def _find_column(columns: list[str], candidates: list[str]) -> Optional[str]:
    """Return the first matching column name from candidates."""
    col_set = set(columns)
    for name in candidates:
        if name in col_set:
            return name

    # Case-insensitive fallback
    lower_map = {c.lower(): c for c in columns}
    for name in candidates:
        if name.lower() in lower_map:
            return lower_map[name.lower()]
    return None


def detect_columns(df: pd.DataFrame) -> dict[str, str]:
    """Detect rating and review columns in a DataFrame.

    Returns:
        {"rating": <source_col>, "review": <source_col>}

    Raises:
        ColumnMappingError if review cannot be found.
        Rating is optional for prediction-only flows but required for training.
    """
    columns = list(df.columns)
    review_col = _find_column(columns, REVIEW_CANDIDATES)
    rating_col = _find_column(columns, RATING_CANDIDATES)

    if review_col is None:
        raise ColumnMappingError(
            "Could not find a review text column. "
            f"Expected one of: {', '.join(REVIEW_CANDIDATES)}. "
            f"Found columns: {', '.join(columns)}"
        )

    mapping: dict[str, str] = {"review": review_col}
    if rating_col is not None:
        mapping["rating"] = rating_col
    return mapping


def normalize_dataframe(
    df: pd.DataFrame,
    *,
    require_rating: bool = False,
) -> pd.DataFrame:
    """Map detected columns to canonical names: review, rating.

    Preserves all original columns and adds/overwrites canonical names.
    """
    mapping = detect_columns(df)

    if require_rating and "rating" not in mapping:
        raise ColumnMappingError(
            "Could not find a rating column. "
            f"Expected one of: {', '.join(RATING_CANDIDATES)}. "
            f"Found columns: {', '.join(df.columns)}"
        )

    result = df.copy()
    review_src = mapping["review"]
    result["review"] = result[review_src]
    # Drop differently named source column to avoid duplicate review/Review pairs
    if review_src != "review" and review_src in result.columns:
        result = result.drop(columns=[review_src])

    if "rating" in mapping:
        rating_src = mapping["rating"]
        result["rating"] = result[rating_src]
        if rating_src != "rating" and rating_src in result.columns:
            result = result.drop(columns=[rating_src])
    elif require_rating:
        raise ColumnMappingError("Rating column is required but was not found.")

    return result
