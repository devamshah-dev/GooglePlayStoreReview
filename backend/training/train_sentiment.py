"""Train and select the best sentiment classifier (TF-IDF + classical ML)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import (  # noqa: E402
    MAX_FEATURES,
    MODELS_DIR,
    NGRAM_RANGE,
    PROCESSED_DATA_DIR,
    RANDOM_STATE,
    SENTIMENT_METRICS_PATH,
    SENTIMENT_MODEL_PATH,
    SENTIMENT_VECTORIZER_PATH,
    TEST_SIZE,
)
from training.evaluate_models import evaluate_classifier, save_metrics  # noqa: E402


def build_candidates() -> dict:
    return {
        "LogisticRegression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            solver="lbfgs",
        ),
        "MultinomialNB": MultinomialNB(alpha=0.5),
        "LinearSVM": LinearSVC(
            class_weight="balanced",
            random_state=RANDOM_STATE,
            max_iter=5000,
            dual="auto",
        ),
    }


def train_sentiment(df: pd.DataFrame) -> dict:
    X = df["review_clean"].astype(str).values
    y = df["sentiment"].astype(str).values

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    # Fit TF-IDF ONLY on training data to prevent leakage
    vectorizer = TfidfVectorizer(
        max_features=MAX_FEATURES,
        ngram_range=NGRAM_RANGE,
        min_df=1,
        sublinear_tf=True,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    results = {}
    best_name = None
    best_f1 = -1.0
    best_model = None

    for name, model in build_candidates().items():
        print(f"Training sentiment model: {name} ...")
        model.fit(X_train_vec, y_train)
        y_pred = model.predict(X_test_vec)
        metrics = evaluate_classifier(y_test, y_pred, labels=sorted(set(y)))
        results[name] = metrics
        f1 = metrics["f1_weighted"]
        print(
            f"  {name}: accuracy={metrics['accuracy']:.4f} "
            f"f1_weighted={f1:.4f} f1_macro={metrics['f1_macro']:.4f}"
        )
        if f1 > best_f1:
            best_f1 = f1
            best_name = name
            best_model = model

    print(f"\nBest sentiment model: {best_name} (weighted F1={best_f1:.4f})")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, SENTIMENT_VECTORIZER_PATH)
    joblib.dump(best_model, SENTIMENT_MODEL_PATH)
    print(f"Saved: {SENTIMENT_VECTORIZER_PATH}")
    print(f"Saved: {SENTIMENT_MODEL_PATH}")

    summary = {
        "task": "sentiment",
        "best_model": best_name,
        "selection_metric": "f1_weighted",
        "selection_reason": (
            "Weighted F1 is preferred because sentiment classes can be imbalanced; "
            "it balances precision/recall while accounting for class support."
        ),
        "test_size": TEST_SIZE,
        "random_state": RANDOM_STATE,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "models": results,
        "best_metrics": results[best_name],
    }
    save_metrics(summary, SENTIMENT_METRICS_PATH)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Train sentiment classifiers.")
    parser.add_argument(
        "--input",
        type=str,
        default=str(PROCESSED_DATA_DIR / "prepared_reviews.csv"),
    )
    args = parser.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"Prepared data not found: {path}")
        print("Run: python -m training.prepare_data")
        sys.exit(1)

    df = pd.read_csv(path)
    if "review_clean" not in df.columns or "sentiment" not in df.columns:
        print("Prepared CSV must contain review_clean and sentiment columns.")
        sys.exit(1)

    # Need at least 2 samples per class for stratification
    counts = df["sentiment"].value_counts()
    print(f"Sentiment class counts:\n{counts.to_string()}")
    train_sentiment(df)


if __name__ == "__main__":
    main()
