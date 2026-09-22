# Databricks notebook source
# Evidence and quality manifest hook for every pipeline run.

from datetime import datetime, timezone
import json

CATALOG = "workspace"
RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def manifest_from_table(table_name: str, required_columns: list[str], key_columns: list[str]) -> dict:
    """Collect a bounded manifest from a Delta table without collecting all rows."""
    df = spark.read.table(table_name)
    columns = df.columns
    row_count = df.count()
    findings = []
    missing = [column for column in required_columns if column not in columns]
    if missing:
        findings.append({"code": "MISSING_COLUMNS", "severity": "BLOCKING", "message": str(missing), "record_count": len(missing)})
    duplicate_count = df.groupBy(key_columns).count().filter("count > 1").count() if key_columns else 0
    if duplicate_count:
        findings.append({"code": "DUPLICATE_KEYS", "severity": "BLOCKING", "message": "Duplicate natural keys", "record_count": duplicate_count})
    schema_hash = str(hash(tuple((field.name, field.dataType.simpleString()) for field in df.schema.fields)))
    return {
        "dataset": table_name,
        "source_system": "databricks-delta",
        "run_id": RUN_ID,
        "row_count": row_count,
        "schema_hash": schema_hash,
        "quality_findings": findings,
        "status": "HALT" if any(item["severity"] == "BLOCKING" for item in findings) else "PASS",
    }


manifests = [
    manifest_from_table(f"{CATALOG}.lakehouse_bronze.mining_companies", ["company_id", "company_name", "ticker"], ["company_id"]),
    manifest_from_table(f"{CATALOG}.lakehouse_bronze.production_records", ["company_id", "year", "quarter", "commodity"], ["company_id", "year", "quarter", "commodity"]),
]

dbutils.jobs.taskValues.set(key="run_id", value=RUN_ID)
dbutils.jobs.taskValues.set(key="manifests", value=json.dumps(manifests))
print(json.dumps(manifests, indent=2))
