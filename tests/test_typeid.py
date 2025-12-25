from datetime import datetime, timezone
from uuid import UUID
import pytest
import uuid6

from typeid import TypeID
from typeid.errors import SuffixValidationException


def test_default_suffix() -> None:
    prefix = "qutab"
    typeid = TypeID(suffix=None, prefix=prefix)

    assert typeid.prefix == prefix
    assert typeid.suffix


def test_construct_typeid() -> None:
    prefix = "plov"
    suffix = "00041061050r3gg28a1c60t3gf"

    typeid = TypeID(prefix=prefix, suffix=suffix)

    assert typeid.prefix == prefix
    assert typeid.suffix == suffix


def test_compare_typeid() -> None:
    prefix_1 = "plov"
    suffix_1 = "00041061050r3gg28a1c60t3gf"
    prefix_2 = "abcd"
    suffix_2 = "00000000000000000000000000"

    typeid_1 = TypeID(prefix=prefix_1, suffix=suffix_1)
    typeid_2 = TypeID(prefix=prefix_1, suffix=suffix_1)
    typeid_3 = TypeID(suffix=suffix_1)
    typeid_4 = TypeID(prefix=prefix_2, suffix=suffix_1)
    typeid_5 = TypeID(prefix=prefix_1, suffix=suffix_2)

    assert typeid_1 == typeid_2
    assert typeid_1 <= typeid_2
    assert typeid_1 >= typeid_2
    assert typeid_3 != typeid_1
    assert typeid_3 < typeid_1
    assert typeid_4 <= typeid_1
    assert typeid_1 > typeid_5


def test_construct_type_from_string() -> None:
    string = "00041061050r3gg28a1c60t3gf"

    typeid = TypeID.from_string(string)

    assert isinstance(typeid, TypeID)
    assert typeid.prefix == ""
    assert isinstance(typeid.suffix, str)


def test_construct_type_from_string_standalone() -> None:
    string = "00041061050r3gg28a1c60t3gf"

    typeid = TypeID.from_string(string)

    assert isinstance(typeid, TypeID)
    assert typeid.prefix == ""
    assert isinstance(typeid.suffix, str)


def test_construct_type_from_string_with_prefix() -> None:
    string = "prefix_00041061050r3gg28a1c60t3gf"

    typeid = TypeID.from_string(string)

    assert isinstance(typeid, TypeID)
    assert typeid.prefix == "prefix"
    assert isinstance(typeid.suffix, str)


def test_construct_type_from_string_with_prefix_standalone() -> None:
    string = "prefix_00041061050r3gg28a1c60t3gf"

    typeid = TypeID.from_string(string)

    assert isinstance(typeid, TypeID)
    assert typeid.prefix == "prefix"
    assert isinstance(typeid.suffix, str)


def test_construct_type_from_string_with_multi_underscore_prefix() -> None:
    string = "double_prefix_00041061050r3gg28a1c60t3gf"

    typeid = TypeID.from_string(string)

    assert isinstance(typeid, TypeID)
    assert typeid.prefix == "double_prefix"
    assert isinstance(typeid.suffix, str)


def test_construct_type_from_invalid_string() -> None:
    string = "invalid_string_to_typeid"

    with pytest.raises(SuffixValidationException):
        TypeID.from_string(string)


def test_construct_type_from_uuid() -> None:
    uuid = uuid6.uuid7()

    typeid = TypeID.from_uuid(suffix=uuid, prefix="")

    assert isinstance(typeid, TypeID)
    assert typeid.prefix == ""
    assert isinstance(typeid.suffix, str)


def test_construct_type_from_uuid_with_prefix() -> None:
    uuid = uuid6.uuid7()
    prefix = "prefix"

    typeid = TypeID.from_uuid(prefix=prefix, suffix=uuid)

    assert isinstance(typeid, TypeID)
    assert typeid.prefix == "prefix"
    assert isinstance(typeid.suffix, str)


def test_hash_type_id() -> None:
    prefix = "plov"
    suffix = "00041061050r3gg28a1c60t3gf"

    typeid_1 = TypeID(prefix=prefix, suffix=suffix)
    typeid_2 = TypeID(prefix=prefix, suffix=suffix)
    typeid_3 = TypeID(suffix=suffix)

    assert hash(typeid_1) == hash(typeid_2)
    assert hash(typeid_3) != hash(typeid_1)


def test_uuid_property() -> None:
    uuid = uuid6.uuid7()

    typeid = TypeID.from_uuid(suffix=uuid)

    assert isinstance(typeid.uuid, uuid6.UUID)
    assert typeid.uuid.version == uuid.version == 7
    assert typeid.uuid.time == uuid.time


def test_created_at_none_for_nil_uuid_suffix():
    tid = TypeID(prefix="x", suffix="00000000000000000000000000")
    assert tid.created_at is None


def test_created_at_none_for_non_v7_uuid_v4():
    # UUIDv4 (random) must not claim created_at
    u = UUID("550e8400-e29b-41d4-a716-446655440000")  # version 4
    tid = TypeID.from_uuid(u, prefix="x")
    assert tid.created_at is None


def test_created_at_is_utc_for_uuid7_generated_typeid():
    # Default TypeID generation should be UUIDv7; then created_at must be present and UTC
    tid = TypeID(prefix="x")
    dt = tid.created_at
    assert dt is not None
    _assert_utc_datetime(dt)


def test_created_at_monotonic_increasing_for_multiple_new_ids():
    # UUIDv7 embeds time; created_at should be non-decreasing across consecutive generations.
    # Note: UUIDv7 can generate multiple IDs within the same millisecond, so equality is allowed.
    t1 = TypeID(prefix="x").created_at
    t2 = TypeID(prefix="x").created_at
    t3 = TypeID(prefix="x").created_at

    assert t1 is not None and t2 is not None and t3 is not None
    assert t1 <= t2 <= t3


def test_created_at_does_not_crash_if_uuid_object_is_unexpected(monkeypatch):
    # If TypeID.uuid returns something odd that breaks version/int access,
    # created_at should return None (safe behavior).
    class WeirdUUID:
        @property
        def version(self):
            raise RuntimeError("nope")

        @property
        def int(self):
            raise RuntimeError("nope")

    tid = TypeID(prefix="x", suffix="00000000000000000000000000")

    # monkeypatch instance attribute/property access
    monkeypatch.setattr(type(tid), "uuid", property(lambda self: WeirdUUID()))

    assert tid.created_at is None


def _assert_utc_datetime(dt: datetime) -> None:
    assert isinstance(dt, datetime)
    assert dt.tzinfo is timezone.utc
    # must be timezone-aware and normalized to UTC
    assert dt.utcoffset() == timezone.utc.utcoffset(dt)
