from pathlib import Path

import pytest

from typeid.explain.registry import load_registry

yaml = pytest.importorskip("yaml")  # skip entire file if PyYAML is not installed


def test_load_registry_yaml_happy_path(tmp_path: Path):
    p = tmp_path / "typeid.schema.yaml"
    p.write_text(
        """
schema_version: 1
types:
  usr:
    name: User
    description: End-user account
    owner_team: identity-platform
    pii: true
    retention: 7y
    links:
      logs: "https://logs?q={id}"
      trace: "https://trace?id={id}&uuid={uuid}"
""",
        encoding="utf-8",
    )

    result = load_registry(p)
    assert result.registry is not None
    assert result.error is None

    s = result.registry.get("usr")
    assert s is not None
    assert s.name == "User"
    assert s.description == "End-user account"
    assert s.owner_team == "identity-platform"
    assert s.pii is True
    assert s.retention == "7y"
    assert "logs" in s.links
    assert "{id}" in s.links["logs"]


def test_load_registry_yaml_missing_schema_version(tmp_path: Path):
    p = tmp_path / "typeid.schema.yaml"
    p.write_text(
        """
types:
  usr:
    name: User
""",
        encoding="utf-8",
    )

    result = load_registry(p)
    assert result.registry is None
    assert result.error is not None
    assert result.error.code == "missing_schema_version"


def test_load_registry_yaml_unsupported_schema_version(tmp_path: Path):
    p = tmp_path / "typeid.schema.yaml"
    p.write_text(
        """
schema_version: 2
types: {}
""",
        encoding="utf-8",
    )

    result = load_registry(p)
    assert result.registry is None
    assert result.error is not None
    assert result.error.code == "unsupported_schema_version"


def test_load_registry_yaml_types_not_a_map(tmp_path: Path):
    p = tmp_path / "typeid.schema.yaml"
    p.write_text(
        """
schema_version: 1
types:
  - usr
  - ord
""",
        encoding="utf-8",
    )

    result = load_registry(p)
    assert result.registry is None
    assert result.error is not None
    assert result.error.code == "invalid_types"


def test_load_registry_yaml_root_not_a_map(tmp_path: Path):
    p = tmp_path / "typeid.schema.yaml"
    p.write_text(
        """
- not
- a
- map
""",
        encoding="utf-8",
    )

    result = load_registry(p)
    assert result.registry is None
    assert result.error is not None
    assert result.error.code == "invalid_schema"


def test_load_registry_yaml_skips_invalid_type_entries(tmp_path: Path):
    p = tmp_path / "typeid.schema.yaml"
    p.write_text(
        """
schema_version: 1
types:
  usr:
    name: User
  "":  # invalid prefix key -> should be skipped
    name: EmptyPrefix
  bad: "not a map"  # invalid value -> should be skipped
""",
        encoding="utf-8",
    )

    result = load_registry(p)
    assert result.registry is not None
    assert result.error is None

    assert result.registry.get("usr") is not None
    assert result.registry.get("") is None
    assert result.registry.get("bad") is None


def test_load_registry_yaml_links_not_a_map_becomes_empty(tmp_path: Path):
    p = tmp_path / "typeid.schema.yaml"
    p.write_text(
        """
schema_version: 1
types:
  usr:
    name: User
    links: "not a map"
""",
        encoding="utf-8",
    )

    result = load_registry(p)
    assert result.registry is not None
    s = result.registry.get("usr")
    assert s is not None
    assert s.links == {}


def test_load_registry_yaml_malformed_yaml_returns_read_failed(tmp_path: Path):
    p = tmp_path / "typeid.schema.yaml"
    p.write_text(
        """
schema_version: 1
types:
  usr:
    name: User
    links:
      logs: "https://logs?q={id}"
    bad: [unclosed
""",
        encoding="utf-8",
    )

    result = load_registry(p)
    assert result.registry is None
    assert result.error is not None
    assert result.error.code == "read_failed"
