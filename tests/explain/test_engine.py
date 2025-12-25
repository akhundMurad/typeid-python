import json
from datetime import datetime

from typeid import TypeID
from typeid.explain.engine import explain
from typeid.explain.model import Provenance, TypeSchema


def _make_valid_id(prefix: str = "usr") -> str:
    return str(TypeID(prefix=prefix))


def test_explain_valid_id_without_schema_has_derived_fields():
    tid = _make_valid_id("usr")

    exp = explain(tid, schema_lookup=None, enable_schema=True, enable_links=True)

    assert exp.id == tid
    assert exp.valid is True
    assert exp.parsed.valid is True
    assert exp.parsed.prefix == "usr"
    assert exp.parsed.suffix is not None
    assert exp.parsed.uuid is not None

    # UUIDv7 timestamp should be derivable
    assert exp.parsed.created_at is not None
    assert isinstance(exp.parsed.created_at, datetime)
    assert exp.parsed.created_at.tzinfo is not None

    # Provenance should mark derived fields
    assert exp.provenance["prefix"] == Provenance.DERIVED_FROM_ID
    assert exp.provenance["suffix"] == Provenance.DERIVED_FROM_ID
    assert exp.provenance["uuid"] == Provenance.DERIVED_FROM_ID
    assert exp.provenance["created_at"] == Provenance.DERIVED_FROM_ID


def test_explain_invalid_id_returns_valid_false_and_errors():
    exp = explain("not_a_typeid", schema_lookup=None)

    assert exp.valid is False
    assert exp.parsed.valid is False
    assert exp.errors, "Should include parse/validation errors"
    assert any(e.code in {"invalid_typeid", "parse_error"} for e in exp.errors)


def test_explain_best_effort_split_on_invalid_but_contains_underscore():
    # invalid suffix, but prefix/suffix should still be split best-effort
    exp = explain("usr_badSuffix", schema_lookup=None)

    assert exp.valid is False
    assert exp.parsed.prefix == "usr"
    assert exp.parsed.suffix == "badSuffix"


def test_explain_schema_lookup_applies_schema_fields_and_provenance():
    tid = _make_valid_id("ord")

    schema = TypeSchema(
        prefix="ord",
        raw={
            "name": "Order",
            "owner_team": "commerce-platform",
            "pii": False,
            "retention": "7y",
        },
        name="Order",
        owner_team="commerce-platform",
        pii=False,
        retention="7y",
        links={},
    )

    def lookup(prefix: str):
        assert prefix == "ord"
        return schema

    exp = explain(tid, schema_lookup=lookup, enable_schema=True, enable_links=False)

    assert exp.valid is True
    assert exp.schema is not None
    assert exp.schema.name == "Order"
    assert exp.schema.owner_team == "commerce-platform"
    assert exp.provenance["name"] == Provenance.SCHEMA
    assert exp.provenance["owner_team"] == Provenance.SCHEMA
    assert exp.provenance["pii"] == Provenance.SCHEMA
    assert exp.provenance["retention"] == Provenance.SCHEMA


def test_explain_schema_lookup_exception_does_not_crash_and_adds_warning():
    tid = _make_valid_id("usr")

    def lookup(_prefix: str):
        raise RuntimeError("boom")

    exp = explain(tid, schema_lookup=lookup, enable_schema=True)

    assert exp.valid is True
    assert exp.schema is None
    assert any("Schema lookup failed" in w for w in exp.warnings)


def test_explain_disable_schema_skips_lookup():
    tid = _make_valid_id("usr")

    called = {"n": 0}

    def lookup(_prefix: str):
        called["n"] += 1
        return None

    exp = explain(tid, schema_lookup=lookup, enable_schema=False)

    assert exp.valid is True
    assert exp.schema is None
    assert called["n"] == 0


def test_explain_link_rendering_basic_placeholders():
    tid = _make_valid_id("usr")

    schema = TypeSchema(
        prefix="usr",
        raw={},
        name="User",
        links={
            "logs": "https://logs.local/search?q={id}",
            "trace": "https://trace.local/?id={id}&uuid={uuid}",
        },
    )

    exp = explain(tid, schema_lookup=lambda p: schema if p == "usr" else None, enable_schema=True, enable_links=True)

    assert "logs" in exp.links
    assert tid in exp.links["logs"]
    assert "trace" in exp.links
    assert tid in exp.links["trace"]
    assert (exp.parsed.uuid or "") in exp.links["trace"]

    assert exp.provenance["links.logs"] == Provenance.SCHEMA
    assert exp.provenance["links.trace"] == Provenance.SCHEMA


def test_explain_link_rendering_unknown_placeholder_is_left_intact():
    tid = _make_valid_id("usr")

    schema = TypeSchema(
        prefix="usr",
        raw={},
        links={"x": "http://x/{does_not_exist}/{id}"},
    )

    exp = explain(tid, schema_lookup=lambda p: schema if p == "usr" else None)

    assert exp.links["x"].startswith("http://x/")
    assert "{does_not_exist}" in exp.links["x"]
    assert tid in exp.links["x"]


def test_explain_link_rendering_non_string_template_is_skipped_with_warning():
    tid = _make_valid_id("usr")

    schema = TypeSchema(
        prefix="usr",
        raw={},
        links={"bad": 123},  # type: ignore
    )

    exp = explain(tid, schema_lookup=lambda p: schema if p == "usr" else None)

    assert "bad" not in exp.links
    assert any("not a string" in w.lower() for w in exp.warnings)


def test_to_dict_is_json_serializable():
    tid = _make_valid_id("usr")
    exp = explain(tid)

    payload = exp.to_dict()
    json.dumps(payload)  # should not raise


def test_explain_nil_uuid_not_sortable_no_created_at():
    exp = explain("x_00000000000000000000000000", enable_schema=False)
    assert exp.valid is True
    assert exp.parsed.uuid == "00000000-0000-0000-0000-000000000000"
    assert exp.parsed.created_at is None
    assert exp.parsed.sortable is False
