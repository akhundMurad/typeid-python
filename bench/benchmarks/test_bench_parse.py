from .data import TypeID, uuid

TYPEID_STR = str(TypeID("user"))
UUID_STR = str(uuid.uuid4())


def test_typeid_parse(benchmark):
    benchmark(TypeID.from_string, TYPEID_STR)


def test_uuid_parse(benchmark):
    benchmark(uuid.UUID, UUID_STR)
