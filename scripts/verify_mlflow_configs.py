#!/usr/bin/env python3
"""Evidence check: MLflow Experiment Tracking (README, MLflow Experiment Results).

Fails unless notebooks/04_mlflow_experiments.py defines the four documented
weight-configuration runs, sets the Databricks tracking/registry URIs, and
carries the disclosure that logged metrics are fixed demonstration values
(labeled illustrative, not computed aggregates). Stdlib-only, no network.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NB = REPO_ROOT / "notebooks" / "04_mlflow_experiments.py"
README = REPO_ROOT / "README.md"

RUN_NAMES = ("baseline", "cost_focused", "growth_focused", "esg_focused")
DISCLOSURE = "fixed demonstration values"


def main() -> int:
    failures = []
    # Whitespace-normalized: comment line wraps must not hide the phrase.
    text = re.sub(r"\s+", " ", NB.read_text(encoding="utf-8"))

    for name in RUN_NAMES:
        if f'run_name="{name}"' not in text:
            failures.append(f'04_mlflow_experiments.py: weight-configuration run not found: "{name}"')
    if 'mlflow.set_tracking_uri("databricks")' not in text:
        failures.append('04_mlflow_experiments.py: mlflow.set_tracking_uri("databricks") not set')
    if 'mlflow.set_registry_uri("databricks-uc")' not in text:
        failures.append('04_mlflow_experiments.py: mlflow.set_registry_uri("databricks-uc") not set')
    if DISCLOSURE not in text:
        failures.append(f"04_mlflow_experiments.py: missing disclosure that logged metrics are {DISCLOSURE!r} (labeled illustrative)")

    readme = re.sub(r"\s+", " ", README.read_text(encoding="utf-8"))
    if DISCLOSURE not in readme:
        failures.append(f"README.md: MLflow results table missing the {DISCLOSURE!r} disclosure")

    if failures:
        for f in failures:
            print(f"FAIL {f}")
        return 1
    print("OK: 4 weight-configuration runs, Databricks tracking/registry URIs set, illustrative-metrics disclosure present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
