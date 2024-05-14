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
