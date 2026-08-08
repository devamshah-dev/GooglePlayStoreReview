"""CSV upload and batch analysis endpoint."""

from __future__ import annotations

import io
import logging
from typing import Any

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.preprocessing.text_cleaner import clean_text
from app.schemas.prediction import DashboardStats, UploadResponse
from app.services.predictor import ModelNotLoadedError, predictor
from app.services.statistics import compute_statistics
from app.utils.columns import ColumnMappingError, normalize_dataframe

logger = logging.getLogger(__name__)
router = APIRouter(tags=["upload"])

# Cap returned preview rows to keep JSON responses manageable
MAX_PREVIEW_ROWS = 500


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)) -> UploadResponse:
    """Upload a CSV of Google Play reviews, predict, and return results + stats."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a .csv file.",
        )

    try:
        raw_bytes = await file.read()
        if not raw_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        try:
            df = pd.read_csv(io.BytesIO(raw_bytes))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to parse CSV: %s", exc)
            raise HTTPException(
                status_code=400,
                detail=f"Could not parse CSV file: {exc}",
            ) from exc

        if df.empty:
            raise HTTPException(status_code=400, detail="CSV contains no rows.")

        try:
            # Rating is optional for prediction; review is required
            df = normalize_dataframe(df, require_rating=False)
        except ColumnMappingError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        if "review" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="Review column could not be normalized.",
            )

        # Clean reviews
        df["review"] = df["review"].fillna("").astype(str)
        cleaned = df["review"].map(clean_text)

        if cleaned.str.len().sum() == 0:
            raise HTTPException(
                status_code=400,
                detail="All review texts are empty after preprocessing.",
            )

        try:
            sentiments, themes = predictor.predict_batch(df["review"].tolist())
        except ModelNotLoadedError as exc:
            raise HTTPException(
                status_code=503,
                detail="Models are not loaded. Please train models and restart the server.",
            ) from exc

        df["predicted_sentiment"] = sentiments
        df["predicted_theme"] = themes

        # Ensure rating column exists for stats (may be missing)
        if "rating" in df.columns:
            df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

        stats_dict = compute_statistics(df)
        stats = DashboardStats(**stats_dict)

        # Build downloadable CSV (preserve original cols + predictions)
        output_cols = list(df.columns)
        # Prefer a stable leading order for key columns
        preferred = ["review", "rating", "predicted_sentiment", "predicted_theme"]
        ordered = [c for c in preferred if c in output_cols] + [
            c for c in output_cols if c not in preferred
        ]
        csv_buf = io.StringIO()
        df[ordered].to_csv(csv_buf, index=False)
        csv_data = csv_buf.getvalue()

        # Preview rows for the results table
        preview_df = df[ordered].head(MAX_PREVIEW_ROWS)
        # Convert NaN to None for JSON
        results: list[dict[str, Any]] = preview_df.where(
            pd.notnull(preview_df), None
        ).to_dict(orient="records")

        return UploadResponse(
            success=True,
            message=f"Successfully analyzed {len(df)} reviews.",
            stats=stats,
            results=results,
            csv_data=csv_data,
            total_rows=len(df),
        )

    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("CSV upload processing failed")
        raise HTTPException(
            status_code=500,
            detail="Failed to process the uploaded CSV due to an internal error.",
        ) from exc
