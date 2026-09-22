#!/usr/bin/env python3
"""Evidence check: Signal Score Methodology (README, Signal Score Methodology).

Fails unless notebooks/03_gold_aggregate.py computes the deployed composite
(Grade 0.20, Cost 0.25, Production 0.20, Growth 0.20, ESG 0.15) with the
documented signal bands, the values match evidence/methodology.json, and the
README formula states the same weights. Stdlib-only, no network.
"""
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NB = REPO_ROOT / "notebooks" / "03_gold_aggregate.py"
README = REPO_ROOT / "README.md"
MANIFEST = REPO_ROOT / "evidence" / "methodology.json"

DEPLOYED_WEIGHTS = {
    "grade": "0.20",
    "cost": "0.25",
    "production": "0.20",
    "growth": "0.20",
    "esg": "0.15",
}
BANDS = (
    (">= 80", "Strong Buy"),
    (">= 65", "Buy"),
    (">= 50", "Hold"),
    (">= 35", "Sell"),
    (None, "Strong Sell"),
)
GOLD_TABLES = ("lakehouse_gold.mining_signal_scores", "lakehouse_gold.cross_domain_intelligence")


def main() -> int:
    failures = []
    text = NB.read_text(encoding="utf-8")

    for dimension, weight in DEPLOYED_WEIGHTS.items():
        pattern = re.compile(rf'col\("{dimension}_score"\)\s*\*\s*{re.escape(weight)}\b')
        if not pattern.search(text):
            failures.append(f'03_gold_aggregate.py: composite weight not found: {dimension} * {weight}')

    for threshold, band in BANDS:
        if threshold:
            pattern = re.compile(rf'{re.escape(threshold)},\s*"{re.escape(band)}"')
            if not pattern.search(text):
                failures.append(f'03_gold_aggregate.py: signal band not found: {threshold} "{band}"')
        elif f'"{band}"' not in text:
            failures.append(f'03_gold_aggregate.py: signal band not found: "{band}"')

    for table in GOLD_TABLES:
        if table not in text:
            failures.append(f"03_gold_aggregate.py: gold table target missing: {table}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    deployed = manifest["deployed"]["composite_weights"]
    expected = {k: float(v) for k, v in DEPLOYED_WEIGHTS.items()}
    if deployed != expected:
        failures.append(f"evidence/methodology.json: composite_weights {deployed!r} != {expected!r}")
    thresholds = manifest["deployed"]["signal_band_thresholds"]
    expected_thresholds = {"strong_buy": 80, "buy": 65, "hold": 50, "sell": 35}
    if thresholds != expected_thresholds:
        failures.append(f"evidence/methodology.json: signal_band_thresholds {thresholds!r} != {expected_thresholds!r}")

    readme = README.read_text(encoding="utf-8")
    formula = "Composite = Grade x 0.20 + Cost x 0.25 + Production x 0.20 + Growth x 0.20 + ESG x 0.15"
    if formula not in readme:
        failures.append("README.md: methodology formula line does not state the deployed weights")

    if failures:
        for f in failures:
            print(f"FAIL {f}")
        return 1
    print("OK: deployed composite weights and signal bands match notebook, methodology.json, and README")
    return 0


if __name__ == "__main__":
    sys.exit(main())
