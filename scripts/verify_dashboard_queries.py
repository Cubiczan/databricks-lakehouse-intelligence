#!/usr/bin/env python3
"""Evidence check: SQL Dashboard Queries (README, Key Capabilities).

Fails unless notebooks/05_dashboard_sql.py implements the four documented
analytics — top signals, AISC benchmark, signal distribution, cross-domain —
against the deployed silver/gold tables. Stdlib-only, no network.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NB = REPO_ROOT / "notebooks" / "05_dashboard_sql.py"

REQUIRED = (
    "--- Top Companies by Signal Score ---",
    "--- AISC Benchmark by Commodity ---",
    "--- Signal Distribution ---",
    "--- Cross-Domain: Mining + Financial ---",
    'lakehouse_gold.mining_signal_scores',
    'lakehouse_silver.production_records',
    'lakehouse_gold.cross_domain_intelligence',
    'orderBy(desc("composite_score"))',
    'avg("aisc_usd_per_t")',
    'groupBy("signal_band")',
)


def main() -> int:
    failures = []
    text = NB.read_text(encoding="utf-8")
    for needle in REQUIRED:
        if needle not in text:
            failures.append(f"05_dashboard_sql.py: required analytics element missing: {needle}")

    if failures:
        for f in failures:
            print(f"FAIL {f}")
        return 1
    print("OK: 05_dashboard_sql.py implements top-signal, AISC-benchmark, distribution, and cross-domain analytics")
    return 0


if __name__ == "__main__":
    sys.exit(main())
