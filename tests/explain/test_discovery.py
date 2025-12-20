from pathlib import Path

import pytest

from typeid.explain.discovery import discover_schema_path


def test_discovery_env_var_wins(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    schema = tmp_path / "schema.json"
    schema.write_text('{"schema_version": 1, "types": {}}', encoding="utf-8")

    monkeypatch.setenv("TYPEID_SCHEMA", str(schema))

    # even if cwd has other candidates, env must win
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    (cwd / "typeid.schema.json").write_text('{"schema_version": 1, "types": {}}', encoding="utf-8")

    res = discover_schema_path(cwd=cwd)
    assert res.path == schema
    assert res.source.startswith("env:")


def test_discovery_cwd_candidate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("TYPEID_SCHEMA", raising=False)

    cwd = tmp_path / "cwd"
    cwd.mkdir()
    schema = cwd / "typeid.schema.json"
    schema.write_text('{"schema_version": 1, "types": {}}', encoding="utf-8")

    res = discover_schema_path(cwd=cwd)
    assert res.path == schema
    assert res.source == "cwd"


def test_discovery_user_config_when_no_env_and_no_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("TYPEID_SCHEMA", raising=False)

    # Force XDG_CONFIG_HOME to a temp dir
    xdg = tmp_path / "xdg"
    xdg.mkdir()
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg))
    monkeypatch.delenv("APPDATA", raising=False)

    # Put schema in user config location: <xdg>/typeid/schema.json
    base = xdg / "typeid"
    base.mkdir()
    schema = base / "schema.json"
    schema.write_text('{"schema_version": 1, "types": {}}', encoding="utf-8")

    cwd = tmp_path / "cwd"
    cwd.mkdir()

    res = discover_schema_path(cwd=cwd)
    assert res.path == schema
    assert res.source == "user_config"


def test_discovery_none_when_missing_everywhere(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("TYPEID_SCHEMA", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg_missing"))
    monkeypatch.delenv("APPDATA", raising=False)

    cwd = tmp_path / "cwd"
    cwd.mkdir()

    res = discover_schema_path(cwd=cwd)
    assert res.path is None
    assert res.source in {"none", "env:TYPEID_SCHEMA (not found)"}
