import pytest

from typeid import TypeID, cached_typeid_factory, typeid_factory
from typeid.errors import PrefixValidationException


def test_typeid_factory_generates_typeid_with_prefix():
    gen = typeid_factory("user")
    tid = gen()

    assert isinstance(tid, TypeID)
    assert tid.prefix == "user"


def test_typeid_factory_returns_new_ids_each_time():
    gen = typeid_factory("user")
    a = gen()
    b = gen()

    assert a != b


def test_cached_typeid_factory_is_cached():
    a = cached_typeid_factory("user")
    b = cached_typeid_factory("user")
    c = cached_typeid_factory("order")

    assert a is b
    assert a is not c


def test_factory_invalid_prefix_propagates():
    gen = typeid_factory("BAD PREFIX")
    with pytest.raises(PrefixValidationException):
        gen()
