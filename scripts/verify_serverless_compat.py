#!/usr/bin/env python3
"""Evidence check: Serverless-Compatible Notebooks (README, Serverless Compatibility Notes).

Fails unless no notebook imports pyspark.ml and the ML-style step in
notebooks/04_mlflow_experiments.py loads data via .toPandas() with MLflow tracking.
Stdlib-only, no network.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = REPO_ROOT / "notebooks"
MLFLOW_NB = "04_mlflow_experiments.py"


def main() -> int:
    failures = []
    notebooks = sorted(NOTEBOOKS.glob("*.py"))
    if not notebooks:
        return fail("no notebooks found under notebooks/")

    for nb in notebooks:
        text = nb.read_text(encoding="utf-8")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith(("import pyspark.ml", "from pyspark.ml")):
                failures.append(f"{nb.name}: pyspark.ml import: {stripped!r}")

    mlflow_text = (NOTEBOOKS / MLFLOW_NB).read_text(encoding="utf-8")
    if ".toPandas()" not in mlflow_text:
        failures.append(f"{MLFLOW_NB}: no .toPandas() usage (claimed ML-style path)")
    if "import mlflow" not in mlflow_text:
        failures.append(f"{MLFLOW_NB}: no MLflow tracking import")

    if failures:
        for f in failures:
            print(f"FAIL {f}")
        return 1
    print(f"OK: {len(notebooks)} notebooks, no pyspark.ml imports; {MLFLOW_NB} uses .toPandas() + MLflow")
    return 0


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
