"""Single-review prediction endpoint."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.prediction import PredictRequest, PredictResponse
from app.services.predictor import ModelNotLoadedError, predictor

logger = logging.getLogger(__name__)
router = APIRouter(tags=["predict"])


@router.post("/predict", response_model=PredictResponse)
def predict_review(payload: PredictRequest) -> PredictResponse:
    """Analyze a single Google Play review for sentiment and theme."""
    review = (payload.review or "").strip()
    if not review:
        raise HTTPException(status_code=400, detail="Review text cannot be empty.")

    try:
        result = predictor.predict_one(review)
    except ModelNotLoadedError as exc:
        logger.error("Models not loaded: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Models are not loaded. Please train models and restart the server.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=500,
            detail="Prediction failed due to an internal error.",
        ) from exc

    return PredictResponse(
        success=True,
        review=review,
        sentiment=result["sentiment"],
        theme=result["theme"],
    )
