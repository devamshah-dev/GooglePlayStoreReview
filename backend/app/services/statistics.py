"""Dashboard statistics from predicted review data."""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd


def compute_statistics(df: pd.DataFrame) -> dict[str, Any]:
    """Compute dashboard statistics from a DataFrame with predictions.

    Expected columns (when available):
    - predicted_sentiment
    - predicted_theme
    - rating
    """
    total = len(df)

    sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
    if "predicted_sentiment" in df.columns:
        vc = df["predicted_sentiment"].value_counts()
        for key in sentiment_counts:
            sentiment_counts[key] = int(vc.get(key, 0))

    theme_counts: dict[str, int] = {}
    if "predicted_theme" in df.columns:
        vc = df["predicted_theme"].value_counts()
        theme_counts = {str(k): int(v) for k, v in vc.items()}

    rating_counts: dict[str, int] = {}
    average_rating: Optional[float] = None
    if "rating" in df.columns:
        ratings = pd.to_numeric(df["rating"], errors="coerce")
        valid = ratings.dropna()
        if len(valid) > 0:
            average_rating = round(float(valid.mean()), 2)
            for star in range(1, 6):
                rating_counts[str(star)] = int((valid == star).sum())
            # Include any other numeric ratings
            other = valid[~valid.isin([1, 2, 3, 4, 5])]
            for val, count in other.value_counts().items():
                rating_counts[str(int(val) if float(val).is_integer() else val)] = int(count)

    return {
        "total_reviews": total,
        "positive_reviews": sentiment_counts["Positive"],
        "neutral_reviews": sentiment_counts["Neutral"],
        "negative_reviews": sentiment_counts["Negative"],
        "average_rating": average_rating,
        "sentiment_distribution": sentiment_counts,
        "theme_distribution": theme_counts,
        "rating_distribution": rating_counts,
    }
