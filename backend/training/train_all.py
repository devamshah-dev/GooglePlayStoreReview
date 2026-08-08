"""Run the full training pipeline: prepare → sentiment → theme."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent


def run(module: str) -> None:
    print(f"\n{'=' * 60}\nRunning: {module}\n{'=' * 60}")
    result = subprocess.run(
        [sys.executable, "-m", module],
        cwd=str(BACKEND_DIR),
    )
    if result.returncode != 0:
        sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="Full ML training pipeline.")
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Optional raw CSV path (passed to prepare_data)",
    )
    args = parser.parse_args()

    if args.input:
        result = subprocess.run(
            [sys.executable, "-m", "training.prepare_data", "--input", args.input],
            cwd=str(BACKEND_DIR),
        )
        if result.returncode != 0:
            sys.exit(result.returncode)
    else:
        run("training.prepare_data")

    run("training.train_sentiment")
    run("training.train_theme")
    print("\nTraining pipeline completed successfully.")
    print(f"Models saved under: {BACKEND_DIR / 'models'}")
    print(f"Metrics saved under: {BACKEND_DIR / 'artifacts' / 'metrics'}")


if __name__ == "__main__":
    main()
