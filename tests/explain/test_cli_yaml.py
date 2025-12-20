import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from typeid import TypeID
from typeid.cli import cli


yaml = pytest.importorskip("yaml")  # skip if PyYAML not installed


def test_cli_explain_with_yaml_schema(tmp_path: Path):
    runner = CliRunner()
    tid = str(TypeID(prefix="usr"))

    p = tmp_path / "typeid.schema.yaml"
    p.write_text(
        """
schema_version: 1
types:
  usr:
    name: User
    owner_team: identity-platform
    links:
      logs: "https://logs?q={id}"
""",
        encoding="utf-8",
    )

    result = runner.invoke(cli, ["explain", tid, "--schema", str(p)])
    assert result.exit_code == 0
    out = result.output

    assert "schema:" in out
    assert "found: true" in out
    assert "name: User" in out
    assert "owner_team: identity-platform" in out
    assert "logs:" in out


def test_cli_explain_with_yaml_schema_json_output(tmp_path: Path):
    runner = CliRunner()
    tid = str(TypeID(prefix="usr"))

    p = tmp_path / "typeid.schema.yaml"
    p.write_text(
        """
schema_version: 1
types:
  usr:
    name: User
""",
        encoding="utf-8",
    )

    result = runner.invoke(cli, ["explain", tid, "--schema", str(p), "--json"])
    assert result.exit_code == 0

    payload = json.loads(result.output)
    assert payload["valid"] is True
    assert payload["schema"] is not None
    assert payload["schema"]["name"] == "User"
