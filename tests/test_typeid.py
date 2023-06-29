from typeid import TypeID


def test_default_suffix() -> None:
    prefix = "qutab"
    typeid = TypeID(suffix=None, prefix=prefix)

    assert typeid.prefix == prefix
    assert typeid.suffix
