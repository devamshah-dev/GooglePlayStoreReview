"""Shared evaluation helpers for classification models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


def evaluate_classifier(
    y_true: np.ndarray | list,
    y_pred: np.ndarray | list,
    labels: list[str] | None = None,
) -> dict[str, Any]:
    """Compute standard classification metrics.

    Prefer weighted F1 as the primary selection metric because review
    sentiment/theme classes are often imbalanced; weighted F1 accounts for
    support per class while still penalizing poor minority-class performance.
    Macro F1 is also reported for reference.
    """
    metrics: dict[str, Any] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_weighted": float(
            precision_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "recall_weighted": float(
            recall_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "f1_weighted": float(
            f1_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "classification_report": classification_report(
            y_true, y_pred, zero_division=0, output_dict=True
        ),
    }

    cm_labels = labels if labels is not None else sorted(set(list(y_true) + list(y_pred)))
    cm = confusion_matrix(y_true, y_pred, labels=cm_labels)
    metrics["confusion_matrix"] = {
        "labels": [str(l) for l in cm_labels],
        "matrix": cm.tolist(),
    }
    return metrics


def save_metrics(metrics: dict[str, Any], path: Path) -> None:
    """Write metrics JSON to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"Saved metrics: {path}")
