#!/usr/bin/env python3
"""Evidence check: Silver quality scores are computed, not decorative literals.

Fails unless notebooks/02_silver_transform.py assigns `quality_score` from the
computed dedup-retention helper (no hardcoded lit(<number>) quality scores),
upserts the three Silver tables, and the README states the computed measure.
Stdlib-only, no network.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NB = REPO_ROOT / "notebooks" / "02_silver_transform.py"
README = REPO_ROOT / "README.md"

# quality_score assigned straight from a numeric literal — the decorative pattern.
HARDCODED = re.compile(r"quality_score[\"']?,\s*lit\(\s*[0-9.]+\s*\)")
HELPER = re.compile(r"dedup_retention\(")
COMPUTED = re.compile(r"lit\(\s*quality_")
SILVER_TABLES = (
    "lakehouse_silver.mining_companies",
    "lakehouse_silver.production_records",
    "lakehouse_silver.financial_metrics",
)


def main() -> int:
    failures = []
    text = NB.read_text(encoding="utf-8")

    for match in HARDCODED.finditer(text):
        failures.append(f"02_silver_transform.py: hardcoded quality_score literal at char {match.start()}: {match.group(0)!r}")
    if "def dedup_retention(" not in text:
        failures.append("02_silver_transform.py: dedup_retention helper not defined (quality_score must be computed)")
    helper_uses = len(HELPER.findall(text))
    if helper_uses < 4:  # 1 definition + 3 call sites
        failures.append(f"02_silver_transform.py: expected 3 dedup_retention call sites, found {helper_uses - 1}")
    computed_uses = len(COMPUTED.findall(text))
    if computed_uses < 3:
        failures.append(f"02_silver_transform.py: expected 3 computed quality_score assignments, found {computed_uses}")
    for table in SILVER_TABLES:
        if f"upsert_delta(" not in text or table not in text:
            failures.append(f"02_silver_transform.py: silver table target missing: {table}")

    readme = README.read_text(encoding="utf-8")
    if "computed dedup-retention" not in readme:
        failures.append("README.md: does not describe the silver quality_score as a computed dedup-retention measure")

    if failures:
        for f in failures:
            print(f"FAIL {f}")
        return 1
    print("OK: silver quality_score computed via dedup_retention for all 3 silver tables; no hardcoded literals")
    return 0


if __name__ == "__main__":
    sys.exit(main())
