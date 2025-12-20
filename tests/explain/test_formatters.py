import json

from typeid import TypeID
from typeid.explain.engine import explain
from typeid.explain.formatters import format_explanation_json, format_explanation_pretty


def test_pretty_formatter_contains_sections():
    tid = str(TypeID(prefix="usr"))
    exp = explain(tid)

    out = format_explanation_pretty(exp)
    assert "parsed:" in out
    assert "schema:" in out
    assert "links:" in out


def test_json_formatter_is_valid_json():
    tid = str(TypeID(prefix="usr"))
    exp = explain(tid)

    out = format_explanation_json(exp)
    json.loads(out)  # should not raise
