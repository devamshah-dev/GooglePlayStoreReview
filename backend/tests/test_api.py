"""Basic backend tests for preprocessing, columns, and API endpoints."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.preprocessing.text_cleaner import clean_text  # noqa: E402
from app.utils.columns import ColumnMappingError, detect_columns, normalize_dataframe  # noqa: E402
import pandas as pd  # noqa: E402


def test_clean_text_preserves_negation():
    cleaned = clean_text("App is NOT working!!!")
    assert "not" in cleaned
    assert "working" in cleaned


def test_clean_text_removes_urls_and_html():
    cleaned = clean_text('Check <b>this</b> https://example.com now')
    assert "http" not in cleaned
    assert "<b>" not in cleaned
    assert "check" in cleaned
    assert "this" in cleaned
    assert "now" in cleaned


def test_detect_columns_common_names():
    df = pd.DataFrame({"score": [5], "reviewText": ["great app"]})
    mapping = detect_columns(df)
    assert mapping["rating"] == "score"
    assert mapping["review"] == "reviewText"


def test_detect_columns_missing_review():
    df = pd.DataFrame({"Rating": [5], "Title": ["x"]})
    with pytest.raises(ColumnMappingError):
        detect_columns(df)


def test_normalize_dataframe():
    df = pd.DataFrame({"Score": [4], "Content": ["Nice app"]})
    out = normalize_dataframe(df, require_rating=True)
    assert out.loc[0, "rating"] == 4
    assert out.loc[0, "review"] == "Nice app"


@pytest.fixture(scope="module")
def client():
    from app.main import app
    from app.services.predictor import predictor

    if not predictor.is_loaded:
        try:
            predictor.load_models()
        except FileNotFoundError:
            pytest.skip("Models not trained yet")
    return TestClient(app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["models_loaded"] is True


def test_predict_crash(client):
    r = client.post(
        "/predict",
        json={"review": "The app crashes every time I open it."},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["theme"] == "Crash"
    assert data["sentiment"] in {"Negative", "Neutral", "Positive"}


def test_predict_login(client):
    r = client.post(
        "/predict",
        json={"review": "I cannot login to my account."},
    )
    assert r.status_code == 200
    assert r.json()["theme"] == "Login Problem"


def test_predict_positive(client):
    r = client.post(
        "/predict",
        json={"review": "Excellent application. I love it."},
    )
    assert r.status_code == 200
    assert r.json()["sentiment"] == "Positive"


def test_predict_empty(client):
    r = client.post("/predict", json={"review": "   "})
    assert r.status_code == 422 or r.status_code == 400


def test_upload_csv(client):
    csv_content = (
        "Rating,Review\n"
        "1,The app crashes every time I open it.\n"
        "5,Excellent application. I love it.\n"
        "2,I cannot login to my account.\n"
    )
    files = {"file": ("sample.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    r = client.post("/upload", files=files)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["total_rows"] == 3
    assert "predicted_sentiment" in data["csv_data"]
    assert data["stats"]["total_reviews"] == 3
