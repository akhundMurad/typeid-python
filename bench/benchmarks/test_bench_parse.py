from typeid import TypeID
import uuid6
import uuid_utils


TYPEID_STR = str(TypeID("user"))
UUID_STR = str(uuid6.uuid7())


def test_typeid_parse(benchmark):
    benchmark(TypeID.from_string, TYPEID_STR)


def test_uuid6_parse(benchmark):
    benchmark(uuid6.UUID, UUID_STR)


def test_uuid_utils_parse(benchmark):
    benchmark(uuid_utils.UUID, UUID_STR)
