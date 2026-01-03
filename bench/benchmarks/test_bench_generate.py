from typeid import TypeID
import uuid
import uuid_utils


def test_typeid_generate(benchmark):
    benchmark(TypeID, "user")


def test_uuid4_generate(benchmark):
    benchmark(uuid.uuid4)


def test_uuid_utils_generate(benchmark):
    benchmark(uuid_utils.uuid7)
