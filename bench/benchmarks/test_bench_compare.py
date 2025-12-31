from .data import TypeID


def _typeid_workflow():
    tid = TypeID("order")
    s = str(tid)
    parsed = TypeID.from_string(s)
    return parsed


def test_typeid_workflow(benchmark):
    benchmark(_typeid_workflow)
