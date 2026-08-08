"""Pydantic request/response schemas."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    review: str = Field(..., min_length=1, description="Google Play review text")


class PredictResponse(BaseModel):
    success: bool = True
    review: str
    sentiment: str
    theme: str


class SentimentStats(BaseModel):
    Positive: int = 0
    Neutral: int = 0
    Negative: int = 0


class DashboardStats(BaseModel):
    total_reviews: int
    positive_reviews: int
    neutral_reviews: int
    negative_reviews: int
    average_rating: Optional[float] = None
    sentiment_distribution: dict[str, int]
    theme_distribution: dict[str, int]
    rating_distribution: dict[str, int]


class UploadResponse(BaseModel):
    success: bool = True
    message: str
    stats: DashboardStats
    results: list[dict[str, Any]]
    csv_data: str
    total_rows: int
