from datetime import datetime, timezone
from typing import Callable
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
    print(type(typeid.uuid))
    assert typeid.uuid.version == uuid.version == 7
    assert typeid.uuid.bytes == uuid.bytes
    assert typeid.uuid.time == uuid.time


def _extract_ts_ms_from_uuid_bytes(uuid_bytes: bytes) -> int:
    """UUIDv7: first 48 bits (6 bytes) are Unix timestamp in milliseconds."""
    assert len(uuid_bytes) == 16
    return int.from_bytes(uuid_bytes[0:6], byteorder="big")


def _assert_utc_datetime(dt: datetime) -> None:
    assert isinstance(dt, datetime)
    assert dt.tzinfo is not None
    assert dt.tzinfo.utcoffset(dt) == timezone.utc.utcoffset(dt)


@pytest.mark.parametrize(
    "uuid7_factory",
    [
        pytest.param(
            lambda: __import__("uuid_utils").uuid7(),
            id="uuid-utils",
            marks=pytest.mark.skipif(
                pytest.importorskip("uuid_utils", reason="uuid-utils not installed") is None,
                reason="uuid-utils not installed",
            ),
        ),
        pytest.param(
            lambda: __import__("uuid6").uuid7(),
            id="uuid6",
            marks=pytest.mark.skipif(
                pytest.importorskip("uuid6", reason="uuid6 not installed") is None,
                reason="uuid6 not installed",
            ),
        ),
    ],
)
def test_timestamp_ms_matches_uuid_bytes_from_uuid(uuid7_factory: Callable[[], object]) -> None:
    u = uuid7_factory()
    tid = TypeID.from_uuid(prefix="user", suffix=u)

    expected = _extract_ts_ms_from_uuid_bytes(u.bytes)
    assert tid.timestamp_ms == expected


@pytest.mark.parametrize(
    "uuid7_factory",
    [
        pytest.param(
            lambda: __import__("uuid_utils").uuid7(),
            id="uuid-utils",
            marks=pytest.mark.skipif(
                pytest.importorskip("uuid_utils", reason="uuid-utils not installed") is None,
                reason="uuid-utils not installed",
            ),
        ),
        pytest.param(
            lambda: __import__("uuid6").uuid7(),
            id="uuid6",
            marks=pytest.mark.skipif(
                pytest.importorskip("uuid6", reason="uuid6 not installed") is None,
                reason="uuid6 not installed",
            ),
        ),
    ],
)
def test_creation_time_matches_timestamp_ms_from_uuid(uuid7_factory: Callable[[], object]) -> None:
    u = uuid7_factory()
    tid = TypeID.from_uuid(prefix="user", suffix=u)

    _assert_utc_datetime(tid.creation_time)

    expected_dt = datetime.fromtimestamp(tid.timestamp_ms / 1000, tz=timezone.utc)
    assert tid.creation_time == expected_dt


def test_timestamp_ms_roundtrip_from_string() -> None:
    # Generate a TypeID (whatever backend is configured) and roundtrip via string parsing.
    tid1 = TypeID(prefix="user")
    s = str(tid1)

    tid2 = TypeID.from_string(s)
    assert tid2.timestamp_ms == tid1.timestamp_ms
    assert tid2.creation_time == tid1.creation_time


def test_creation_time_is_monotonic_non_decreasing_for_multiple_new() -> None:
    # UUIDv7 timestamps are millisecond resolution; two IDs in the same ms may be equal.
    t1 = TypeID(prefix="user")
    t2 = TypeID(prefix="user")

    assert t2.timestamp_ms >= t1.timestamp_ms


def test_creation_time_timezone_is_utc() -> None:
    tid = TypeID(prefix="user")
    _assert_utc_datetime(tid.creation_time)
