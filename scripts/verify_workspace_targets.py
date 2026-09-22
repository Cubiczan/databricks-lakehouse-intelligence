#!/usr/bin/env python3
"""Evidence check: Unity Catalog workspace targets (README, Architecture / Deployment).

Fails unless every notebook pins the `workspace` catalog, 00_setup.py
enumerates the five lakehouse_* schemas, and 01_bronze_ingest.py creates the
three bronze tables. Stdlib-only, no network.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = REPO_ROOT / "notebooks"

SCHEMAS = (
    "lakehouse_bronze",
    "lakehouse_silver",
    "lakehouse_gold",
    "lakehouse_ml",
    "lakehouse_reporting",
)
BRONZE_TABLES = (
    "lakehouse_bronze.mining_companies",
    "lakehouse_bronze.production_records",
    "lakehouse_bronze.financial_metrics",
)


def main() -> int:
    failures = []
    notebooks = sorted(NOTEBOOKS.glob("*.py"))
    for nb in notebooks:
        text = nb.read_text(encoding="utf-8")
        if 'CATALOG = "workspace"' not in text:
            failures.append(f"{nb.name}: CATALOG not pinned to 'workspace'")

    setup_text = (NOTEBOOKS / "00_setup.py").read_text(encoding="utf-8")
    for schema in SCHEMAS:
        if f'"{schema}"' not in setup_text:
            failures.append(f"00_setup.py: schema not enumerated: {schema}")

    bronze_text = (NOTEBOOKS / "01_bronze_ingest.py").read_text(encoding="utf-8")
    for table in BRONZE_TABLES:
        if table not in bronze_text:
            failures.append(f"01_bronze_ingest.py: bronze table target missing: {table}")

    if failures:
        for f in failures:
            print(f"FAIL {f}")
        return 1
    print(f"OK: {len(notebooks)} notebooks pin the workspace catalog; 5 schemas enumerated; 3 bronze tables created")
    return 0


if __name__ == "__main__":
    sys.exit(main())
