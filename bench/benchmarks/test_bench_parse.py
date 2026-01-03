from typeid import TypeID
import uuid
import uuid_utils


TYPEID_STR = str(TypeID("user"))
UUID_STR = str(uuid_utils.uuid7())


def test_typeid_parse(benchmark):
    benchmark(TypeID.from_string, TYPEID_STR)


def test_typeid_parse_reuse(benchmark):
    s = str(TypeID("user"))
    benchmark(lambda: TypeID.from_string(s))


def test_uuid_utils_parse(benchmark):
    benchmark(uuid_utils.UUID, UUID_STR)
