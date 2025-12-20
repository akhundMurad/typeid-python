import json
from pathlib import Path

from click.testing import CliRunner

from typeid import TypeID
from typeid.cli import cli


def _make_valid_id(prefix: str = "usr") -> str:
    return str(TypeID(prefix=prefix))


def test_cli_explain_pretty_offline_no_schema():
    runner = CliRunner()
    tid = _make_valid_id("usr")

    result = runner.invoke(cli, ["explain", tid, "--no-schema"])
    assert result.exit_code == 0
    out = result.output

    assert f"id: {tid}" in out
    assert "valid: true" in out
    assert "schema:" in out
    assert "found: false" in out or "found: false" in out.lower()


def test_cli_explain_json_offline():
    runner = CliRunner()
    tid = _make_valid_id("usr")

    result = runner.invoke(cli, ["explain", tid, "--no-schema", "--json"])
    assert result.exit_code == 0

    payload = json.loads(result.output)
    assert payload["id"] == tid
    assert payload["valid"] is True
    assert payload["schema"] is None
    assert payload["parsed"]["prefix"] == "usr"
    assert payload["parsed"]["uuid"] is not None


def test_cli_explain_with_schema_file(tmp_path: Path):
    runner = CliRunner()
    tid = _make_valid_id("usr")

    schema = {
        "schema_version": 1,
        "types": {
            "usr": {"name": "User", "owner_team": "identity-platform", "links": {"logs": "https://logs?q={id}"}}
        },
    }
    p = tmp_path / "typeid.schema.json"
    p.write_text(json.dumps(schema), encoding="utf-8")

    result = runner.invoke(cli, ["explain", tid, "--schema", str(p)])
    assert result.exit_code == 0
    out = result.output

    assert "schema:" in out
    assert "found: true" in out
    assert "name: User" in out
    assert "owner_team: identity-platform" in out
    assert "links:" in out
    assert "logs:" in out


def test_cli_explain_schema_load_failure_still_works(tmp_path: Path):
    runner = CliRunner()
    tid = _make_valid_id("usr")

    p = tmp_path / "typeid.schema.json"
    p.write_text("{not json", encoding="utf-8")

    result = runner.invoke(cli, ["explain", tid, "--schema", str(p)])
    assert result.exit_code == 0
    out = result.output

    # Should still explain derived facts and surface warning
    assert f"id: {tid}" in out
    assert "valid: true" in out
    assert "warnings:" in out.lower()


def test_cli_explain_invalid_id_exit_code_zero_but_valid_false():
    # We keep exit_code 0 for "explain" so it can be used in scripts without
    # failing pipelines; the content will indicate validity.
    runner = CliRunner()

    result = runner.invoke(cli, ["explain", "not_a_typeid", "--no-schema"])
    assert result.exit_code == 0
    assert "valid: false" in result.output.lower()
    assert "errors:" in result.output.lower()
