from lakehouse.provenance import build_manifest, canonical_hash, manifest_status


def test_manifest_hash_is_deterministic():
    rows = [{"id": "a", "value": 1}, {"id": "b", "value": 2}]
    first = build_manifest("demo", "csv", "run-1", rows, ["id"], ["id"])
    second = build_manifest("demo", "csv", "run-1", rows, ["id"], ["id"])
    assert first.input_hash == second.input_hash
    assert first.schema_hash == second.schema_hash
    assert manifest_status(first) == "PASS"


def test_manifest_blocks_missing_columns_and_duplicates():
    rows = [{"id": "a"}, {"id": "a"}]
    manifest = build_manifest("demo", "csv", "run-1", rows, ["id", "required"], ["id"])
    assert manifest_status(manifest) == "HALT"
    assert {item["code"] for item in manifest.quality_findings} == {"MISSING_COLUMNS", "DUPLICATE_KEYS"}


def test_canonical_hash_changes_with_payload():
    assert canonical_hash({"a": 1}) != canonical_hash({"a": 2})
