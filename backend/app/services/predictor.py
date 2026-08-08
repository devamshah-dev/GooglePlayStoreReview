"""ML prediction service – loads models once and reuses them."""

from __future__ import annotations

import logging
from typing import Optional

import joblib
import numpy as np

from app.config import (
    SENTIMENT_MODEL_PATH,
    SENTIMENT_VECTORIZER_PATH,
    THEME_MODEL_PATH,
    THEME_VECTORIZER_PATH,
)
from app.preprocessing.text_cleaner import clean_text, clean_texts

logger = logging.getLogger(__name__)


class ModelNotLoadedError(RuntimeError):
    """Raised when prediction is attempted before models are loaded."""


class PredictorService:
    """Singleton-style predictor that loads artifacts at application startup."""

    def __init__(self) -> None:
        self.sentiment_vectorizer = None
        self.sentiment_model = None
        self.theme_vectorizer = None
        self.theme_model = None
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load_models(self) -> None:
        """Load all model artifacts from disk. Called once at startup."""
        missing = []
        for path in (
            SENTIMENT_VECTORIZER_PATH,
            SENTIMENT_MODEL_PATH,
            THEME_VECTORIZER_PATH,
            THEME_MODEL_PATH,
        ):
            if not path.exists():
                missing.append(str(path))

        if missing:
            raise FileNotFoundError(
                "Required model files are missing. Run the training pipeline first.\n"
                + "\n".join(f"  - {m}" for m in missing)
            )

        logger.info("Loading sentiment vectorizer from %s", SENTIMENT_VECTORIZER_PATH)
        self.sentiment_vectorizer = joblib.load(SENTIMENT_VECTORIZER_PATH)
        logger.info("Loading sentiment model from %s", SENTIMENT_MODEL_PATH)
        self.sentiment_model = joblib.load(SENTIMENT_MODEL_PATH)
        logger.info("Loading theme vectorizer from %s", THEME_VECTORIZER_PATH)
        self.theme_vectorizer = joblib.load(THEME_VECTORIZER_PATH)
        logger.info("Loading theme model from %s", THEME_MODEL_PATH)
        self.theme_model = joblib.load(THEME_MODEL_PATH)
        self._loaded = True
        logger.info("All models loaded successfully.")

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            raise ModelNotLoadedError(
                "Models are not loaded. Ensure the training pipeline has been run "
                "and the application started correctly."
            )

    def predict_one(self, review: str) -> dict[str, str]:
        """Predict sentiment and theme for a single review text."""
        self._ensure_loaded()
        cleaned = clean_text(review)
        if not cleaned:
            raise ValueError("Review text is empty after preprocessing.")

        sent_vec = self.sentiment_vectorizer.transform([cleaned])
        theme_vec = self.theme_vectorizer.transform([cleaned])

        sentiment = str(self.sentiment_model.predict(sent_vec)[0])
        theme = str(self.theme_model.predict(theme_vec)[0])
        return {"sentiment": sentiment, "theme": theme, "cleaned": cleaned}

    def predict_batch(self, reviews: list[str]) -> tuple[list[str], list[str]]:
        """Predict sentiment and theme for a batch of review texts."""
        self._ensure_loaded()
        cleaned = clean_texts(reviews)

        # Empty strings get a placeholder so vectorizer doesn't break; mark as Other/Neutral
        safe = [c if c else " " for c in cleaned]

        sent_vec = self.sentiment_vectorizer.transform(safe)
        theme_vec = self.theme_vectorizer.transform(safe)

        sentiments = [str(s) for s in self.sentiment_model.predict(sent_vec)]
        themes = [str(t) for t in self.theme_model.predict(theme_vec)]

        # Override empty originals
        for i, c in enumerate(cleaned):
            if not c:
                sentiments[i] = "Neutral"
                themes[i] = "Other"

        return sentiments, themes


# Module-level singleton used by the FastAPI app
predictor = PredictorService()
