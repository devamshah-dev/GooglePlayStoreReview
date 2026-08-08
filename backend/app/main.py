"""FastAPI application entry point."""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api import predict, upload
from app.config import (
    CORS_ORIGINS,
    SENTIMENT_METRICS_PATH,
    THEME_METRICS_PATH,
)
from app.services.predictor import predictor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Load ML models once at startup."""
    try:
        predictor.load_models()
    except FileNotFoundError as exc:
        logger.error("Model load failed:\n%s", exc)
        logger.error(
            "Start the API after running: python -m training.train_all"
        )
        # Allow app to start so /health can report the issue
    except Exception:  # noqa: BLE001
        logger.exception("Unexpected error while loading models")
    yield


app = FastAPI(
    title="Google Play Review Classification Platform",
    description=(
        "CPU-based classical ML API for Google Play review sentiment "
        "and theme classification (TF-IDF + Logistic Regression / NB / Linear SVM)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)
app.include_router(upload.router)


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "Google Play Review Classification Platform",
        "models_loaded": predictor.is_loaded,
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "healthy" if predictor.is_loaded else "degraded",
        "models_loaded": predictor.is_loaded,
    }


@app.get("/metrics")
def metrics() -> dict[str, Any]:
    """Return saved evaluation metrics for sentiment and theme models."""
    result: dict[str, Any] = {"success": True, "sentiment": None, "theme": None}

    if SENTIMENT_METRICS_PATH.exists():
        with SENTIMENT_METRICS_PATH.open(encoding="utf-8") as fh:
            result["sentiment"] = json.load(fh)
    if THEME_METRICS_PATH.exists():
        with THEME_METRICS_PATH.open(encoding="utf-8") as fh:
            result["theme"] = json.load(fh)

    if result["sentiment"] is None and result["theme"] is None:
        raise HTTPException(
            status_code=404,
            detail="No metrics found. Run the training pipeline first.",
        )
    return result
