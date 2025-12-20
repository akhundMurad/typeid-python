import json
from pathlib import Path

from typeid.explain.registry import load_registry


def test_load_registry_json_happy_path(tmp_path: Path):
    schema = {
        "schema_version": 1,
        "types": {
            "usr": {
                "name": "User",
                "description": "End-user account",
                "owner_team": "identity-platform",
                "pii": True,
                "retention": "7y",
                "links": {
                    "logs": "https://logs?q={id}",
                },
            }
        },
    }
    p = tmp_path / "typeid.schema.json"
    p.write_text(json.dumps(schema), encoding="utf-8")

    result = load_registry(p)
    assert result.registry is not None
    assert result.error is None

    s = result.registry.get("usr")
    assert s is not None
    assert s.name == "User"
    assert s.pii is True
    assert s.links["logs"].startswith("https://")


def test_load_registry_missing_schema_version(tmp_path: Path):
    schema = {"types": {"usr": {"name": "User"}}}
    p = tmp_path / "typeid.schema.json"
    p.write_text(json.dumps(schema), encoding="utf-8")

    result = load_registry(p)
    assert result.registry is None
    assert result.error is not None
    assert result.error.code == "missing_schema_version"


def test_load_registry_unsupported_schema_version(tmp_path: Path):
    schema = {"schema_version": 999, "types": {}}
    p = tmp_path / "typeid.schema.json"
    p.write_text(json.dumps(schema), encoding="utf-8")

    result = load_registry(p)
    assert result.registry is None
    assert result.error is not None
    assert result.error.code == "unsupported_schema_version"


def test_load_registry_types_not_a_map(tmp_path: Path):
    schema = {"schema_version": 1, "types": ["usr"]}
    p = tmp_path / "typeid.schema.json"
    p.write_text(json.dumps(schema), encoding="utf-8")

    result = load_registry(p)
    assert result.registry is None
    assert result.error is not None
    assert result.error.code == "invalid_types"


def test_load_registry_skips_invalid_type_entries(tmp_path: Path):
    schema = {
        "schema_version": 1,
        "types": {
            "usr": {"name": "User"},
            "": {"name": "EmptyPrefixShouldSkip"},
            "bad": "not a map",
        },
    }
    p = tmp_path / "typeid.schema.json"
    p.write_text(json.dumps(schema), encoding="utf-8")

    result = load_registry(p)
    assert result.registry is not None

    assert result.registry.get("usr") is not None
    assert result.registry.get("") is None
    assert result.registry.get("bad") is None


def test_load_registry_unknown_extension_tries_json_then_fails(tmp_path: Path):
    p = tmp_path / "schema.weird"
    p.write_text('{"schema_version": 1, "types": {"usr": {"name": "User"}}}', encoding="utf-8")

    result = load_registry(p)
    assert result.registry is not None
    assert result.error is None


def test_load_registry_invalid_json_returns_error(tmp_path: Path):
    p = tmp_path / "typeid.schema.json"
    p.write_text("{not json", encoding="utf-8")

    result = load_registry(p)
    assert result.registry is None
    assert result.error is not None
    assert result.error.code == "read_failed"
