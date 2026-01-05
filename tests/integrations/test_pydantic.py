import pytest
from pydantic import BaseModel, ValidationError

from typeid.integrations.pydantic import TypeIDField
from typeid import TypeID


USER_TYPEID_STR = str(TypeID("user"))
ORDER_TYPEID_STR = str(TypeID("order"))


class M(BaseModel):
    id: TypeIDField["user"]


def test_accepts_str():
    m = M(id=USER_TYPEID_STR)
    assert isinstance(m.id, TypeID)


def test_accepts_typeid_instance():
    tid = TypeID.from_string(USER_TYPEID_STR)
    m = M(id=tid)
    assert m.id == tid


def test_prefix_mismatch():
    with pytest.raises(ValidationError):
        M(id=ORDER_TYPEID_STR)


def test_json_serializes_as_string():
    m = M(id=USER_TYPEID_STR)
    data = m.model_dump_json()
    assert '"id":"' in data
