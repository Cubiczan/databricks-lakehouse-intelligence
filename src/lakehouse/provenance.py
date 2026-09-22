"""Deterministic source manifests and quality findings for lakehouse runs."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class QualityFinding:
    code: str
    severity: str
    message: str
    record_count: int = 0

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SourceManifest:
    dataset: str
    source_system: str
    run_id: str
    row_count: int
    schema_hash: str
    input_hash: str
    quality_findings: tuple[dict[str, Any], ...]
    created_at: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def canonical_hash(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return sha256(blob.encode("utf-8")).hexdigest()


def build_manifest(
    dataset: str,
    source_system: str,
    run_id: str,
    records: Sequence[Mapping[str, Any]],
    required_columns: Sequence[str] = (),
    key_columns: Sequence[str] = (),
) -> SourceManifest:
    rows = [dict(row) for row in records]
    columns = sorted({key for row in rows for key in row})
    findings: list[QualityFinding] = []
    missing = [column for column in required_columns if column not in columns]
    if missing:
        findings.append(QualityFinding("MISSING_COLUMNS", "BLOCKING", f"Missing columns: {missing}", len(missing)))
    if key_columns:
        keys = [tuple(row.get(column) for column in key_columns) for row in rows]
        duplicate_count = len(keys) - len(set(keys))
        if duplicate_count:
            findings.append(QualityFinding("DUPLICATE_KEYS", "BLOCKING", "Duplicate natural keys detected.", duplicate_count))
    return SourceManifest(
        dataset=dataset,
        source_system=source_system,
        run_id=run_id,
        row_count=len(rows),
        schema_hash=canonical_hash(columns),
        input_hash=canonical_hash(rows),
        quality_findings=tuple(finding.as_dict() for finding in findings),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def manifest_status(manifest: SourceManifest) -> str:
    return "HALT" if any(finding["severity"] == "BLOCKING" for finding in manifest.quality_findings) else "PASS"
