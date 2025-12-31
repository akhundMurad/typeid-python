from .data import TypeID, uuid, ulid


def test_typeid_generate(benchmark):
    benchmark(TypeID, "user")


def test_uuid4_generate(benchmark):
    benchmark(uuid.uuid4)


def test_ulid_generate(benchmark):
    if ulid is None:
        import pytest
        pytest.skip("ulid not installed")
    benchmark(ulid.new)
