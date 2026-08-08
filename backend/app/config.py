"""Application configuration using project-relative paths."""

from pathlib import Path

# backend/ directory (parent of app/)
BACKEND_DIR = Path(__file__).resolve().parent.parent

# Project root (GooglePlayReviewPlatform/)
PROJECT_ROOT = BACKEND_DIR.parent

MODELS_DIR = BACKEND_DIR / "models"
ARTIFACTS_DIR = BACKEND_DIR / "artifacts"
METRICS_DIR = ARTIFACTS_DIR / "metrics"
DATASETS_DIR = BACKEND_DIR / "datasets"
RAW_DATA_DIR = DATASETS_DIR / "raw"
PROCESSED_DATA_DIR = DATASETS_DIR / "processed"

# Model artifact filenames
SENTIMENT_VECTORIZER_PATH = MODELS_DIR / "sentiment_vectorizer.pkl"
SENTIMENT_MODEL_PATH = MODELS_DIR / "sentiment_model.pkl"
THEME_VECTORIZER_PATH = MODELS_DIR / "theme_vectorizer.pkl"
THEME_MODEL_PATH = MODELS_DIR / "theme_model.pkl"

SENTIMENT_METRICS_PATH = METRICS_DIR / "sentiment_metrics.json"
THEME_METRICS_PATH = METRICS_DIR / "theme_metrics.json"

# CORS – local Vite / React development servers
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# ML settings
RANDOM_STATE = 42
TEST_SIZE = 0.2
MAX_FEATURES = 5000
NGRAM_RANGE = (1, 2)

# Sentiment label mapping from star ratings
SENTIMENT_FROM_RATING = {
    1: "Negative",
    2: "Negative",
    3: "Neutral",
    4: "Positive",
    5: "Positive",
}

THEME_LABELS = [
    "Crash",
    "Login Problem",
    "Performance Issue",
    "UI Problem",
    "Feature Request",
    "Ads Complaint",
    "Security Concern",
    "Payment Problem",
    "General Praise",
    "Other",
]
