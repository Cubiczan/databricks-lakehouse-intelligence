#!/usr/bin/env python3
"""Evidence check: Run-evidence manifest notebook (README, Run Evidence).

Fails unless notebooks/06_quality_manifest.py publishes run_id and manifests
as job task values, marks each manifest PASS or HALT on BLOCKING findings, and
covers the two bronze manifests. Stdlib-only, no network.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NB = REPO_ROOT / "notebooks" / "06_quality_manifest.py"

BRONZE_TABLES = (
    "lakehouse_bronze.mining_companies",
    "lakehouse_bronze.production_records",
)


def main() -> int:
    failures = []
    text = NB.read_text(encoding="utf-8")

    for key in ("run_id", "manifests"):
        if f'dbutils.jobs.taskValues.set(key="{key}"' not in text:
            failures.append(f"06_quality_manifest.py: task value not published: {key}")
    if '"severity": "BLOCKING"' not in text:
        failures.append('06_quality_manifest.py: no BLOCKING severity finding construction')
    if '"HALT" if any(' not in text:
        failures.append("06_quality_manifest.py: PASS/HALT status mapping not found")
    for table in BRONZE_TABLES:
        if table not in text:
            failures.append(f"06_quality_manifest.py: manifest target missing: {table}")

    if failures:
        for f in failures:
            print(f"FAIL {f}")
        return 1
    print("OK: 06_quality_manifest.py publishes run_id + manifests task values with PASS/HALT blocking mapping")
    return 0


if __name__ == "__main__":
    sys.exit(main())
