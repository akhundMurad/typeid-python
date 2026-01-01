from typeid import TypeID
import uuid6
import uuid_utils


def test_typeid_generate(benchmark):
    benchmark(TypeID, "user")


def test_uuid6_generate(benchmark):
    benchmark(uuid6.uuid7)


def test_uuid_utils_generate(benchmark):
    benchmark(uuid_utils.uuid7)
