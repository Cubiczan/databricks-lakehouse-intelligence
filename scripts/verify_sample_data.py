#!/usr/bin/env python3
"""Evidence check: Sample data (README, Sample Data).

Fails unless the three committed CSVs match the src/lakehouse/models.py
schemas, carry the documented row counts (10 companies, 15 production
records, 10 financial rows), and have unique primary identifiers.
Stdlib-only, no network.
"""
import ast
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS = REPO_ROOT / "src" / "lakehouse" / "models.py"
# model class -> (csv path, key column, documented row count, generated timestamp fields)
EXPECTED = {
    "MiningCompany": ("data/sample_mining_companies.csv", "company_id", 10, {"ingested_at"}),
    "ProductionRecord": ("data/sample_production.csv", "record_id", 15, {"ingested_at"}),
    "FinancialMetric": ("data/sample_financials.csv", "metric_id", 10, {"reported_at"}),
}


def model_field_names(class_name: str) -> list[str]:
    tree = ast.parse(MODELS.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return [
                stmt.target.id
                for stmt in node.body
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name)
            ]
    raise KeyError(f"model class not found in models.py: {class_name}")


def main() -> int:
    failures = []
    for class_name, (csv_rel, key_column, row_count, generated_fields) in EXPECTED.items():
        path = REPO_ROOT / csv_rel
        if not path.is_file():
            failures.append(f"{csv_rel}: file missing")
            continue
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            header = reader.fieldnames or []
            rows = list(reader)

        expected_fields = [f for f in model_field_names(class_name) if f not in generated_fields]
        if header != expected_fields:
            failures.append(f"{csv_rel}: header {header} does not match {class_name} fields {expected_fields}")
        if len(rows) != row_count:
            failures.append(f"{csv_rel}: expected {row_count} data rows, found {len(rows)}")
        keys = [row.get(key_column) for row in rows]
        if len(set(keys)) != len(keys):
            failures.append(f"{csv_rel}: duplicate {key_column} values")

    if failures:
        for f in failures:
            print(f"FAIL {f}")
        return 1
    print("OK: 3 sample CSVs match the models.py schemas with documented row counts and unique keys")
    return 0


if __name__ == "__main__":
    sys.exit(main())
