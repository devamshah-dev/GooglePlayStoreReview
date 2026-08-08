"""Prepare raw CSV data for training: detect columns, clean, label, dedupe."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

# Allow running as script from backend/ directory
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import (  # noqa: E402
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    SENTIMENT_FROM_RATING,
)
from app.preprocessing.text_cleaner import clean_text  # noqa: E402
from app.utils.columns import ColumnMappingError, normalize_dataframe  # noqa: E402
from training.create_theme_labels import assign_theme  # noqa: E402


def rating_to_sentiment(rating: float) -> str | None:
    """Map star rating (1–5) to sentiment label. Returns None if invalid."""
    try:
        r = int(round(float(rating)))
    except (TypeError, ValueError):
        return None
    return SENTIMENT_FROM_RATING.get(r)


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Full preparation pipeline on an in-memory DataFrame."""
    df = normalize_dataframe(df, require_rating=True)

    # Drop missing reviews
    df = df.dropna(subset=["review"])
    df["review"] = df["review"].astype(str)
    df = df[df["review"].str.strip().astype(bool)]

    # Coerce rating
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df = df.dropna(subset=["rating"])
    df["rating"] = df["rating"].round().astype(int)
    df = df[df["rating"].between(1, 5)]

    # Clean text
    df["review_clean"] = df["review"].map(clean_text)
    df = df[df["review_clean"].str.len() > 0]

    # Deduplicate on cleaned review text
    before = len(df)
    df = df.drop_duplicates(subset=["review_clean"])
    print(f"Removed {before - len(df)} duplicate reviews.")

    # Sentiment from rating (intentional bootstrap labeling)
    df["sentiment"] = df["rating"].map(rating_to_sentiment)
    df = df.dropna(subset=["sentiment"])

    # Theme from keyword rules (automatically generated – NOT human ground truth)
    df["theme"] = df["review_clean"].map(assign_theme)

    return df.reset_index(drop=True)


def find_raw_csv(explicit: str | None = None) -> Path:
    """Locate a raw CSV for training."""
    if explicit:
        path = Path(explicit)
        if not path.exists():
            raise FileNotFoundError(f"CSV not found: {path}")
        return path

    preferred = RAW_DATA_DIR / "sample_reviews.csv"
    if preferred.exists():
        return preferred

    csvs = sorted(RAW_DATA_DIR.glob("*.csv"))
    if not csvs:
        raise FileNotFoundError(
            f"No CSV files found in {RAW_DATA_DIR}. "
            "Place a dataset there or pass --input."
        )
    return csvs[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare review data for training.")
    parser.add_argument("--input", type=str, default=None, help="Path to raw CSV")
    parser.add_argument(
        "--output",
        type=str,
        default=str(PROCESSED_DATA_DIR / "prepared_reviews.csv"),
        help="Output path for prepared CSV",
    )
    args = parser.parse_args()

    raw_path = find_raw_csv(args.input)
    print(f"Reading: {raw_path}")
    df = pd.read_csv(raw_path)
    print(f"Raw rows: {len(df)}")

    try:
        prepared = prepare_dataframe(df)
    except ColumnMappingError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    prepared.to_csv(out, index=False)

    print(f"Prepared rows: {len(prepared)}")
    print(f"Sentiment distribution:\n{prepared['sentiment'].value_counts().to_string()}")
    print(f"Theme distribution:\n{prepared['theme'].value_counts().to_string()}")
    print(f"Saved: {out}")
    print(
        "\nNOTE: Theme labels are automatically generated via keyword rules "
        "and are NOT human-annotated ground truth."
    )


if __name__ == "__main__":
    main()
