import importlib
import sys
import uuid

import pytest

django = pytest.importorskip("django")
pytest.importorskip("rest_framework")

from django.conf import settings  # noqa: E402

if not settings.configured:
    settings.configure(INSTALLED_APPS=["rest_framework"], USE_I18N=False)
    django.setup()

from rest_framework import serializers  # noqa: E402
from uuid_utils import uuid7  # noqa: E402

from typeid import TypeID  # noqa: E402
from typeid.core.errors import PrefixValidationException  # noqa: E402
from typeid.integrations.drf import TypeIDField  # noqa: E402

USER_ID = str(TypeID("user"))
ORDER_ID = str(TypeID("order"))


class UserSerializer(serializers.Serializer):
    id = TypeIDField(prefix="user")
    ref = TypeIDField(required=False)


def test_accepts_string_and_returns_typeid():
    s = UserSerializer(data={"id": USER_ID})
    assert s.is_valid(), s.errors
    assert isinstance(s.validated_data["id"], TypeID)
    assert str(s.validated_data["id"]) == USER_ID


def test_accepts_typeid_instance():
    tid = TypeID.from_string(USER_ID)
    s = UserSerializer(data={"id": tid})
    assert s.is_valid(), s.errors
    assert s.validated_data["id"] == tid


def test_rejects_prefix_mismatch():
    s = UserSerializer(data={"id": ORDER_ID})
    assert not s.is_valid()
    assert "prefix 'user'" in str(s.errors["id"][0])


@pytest.mark.parametrize("value", ["not-a-typeid", "user_", 123, None])
def test_rejects_invalid_values(value):
    s = UserSerializer(data={"id": value})
    assert not s.is_valid()
    assert "id" in s.errors


def test_any_prefix_when_unset():
    s = UserSerializer(data={"id": USER_ID, "ref": ORDER_ID})
    assert s.is_valid(), s.errors
    assert s.validated_data["ref"].prefix == "order"


def test_serializes_typeid_as_string():
    tid = TypeID.from_string(USER_ID)
    assert UserSerializer({"id": tid}).data["id"] == USER_ID


def test_serializes_uuid_with_prefix():
    u = uuid7()
    data = UserSerializer({"id": u}).data
    assert data["id"] == str(TypeID.from_uuid(u, prefix="user"))
    assert TypeID.from_string(data["id"]).uuid == u


def test_serializes_stdlib_uuid_with_prefix():
    # e.g. the value of a Django UUIDField primary key
    u = uuid.uuid4()
    data = UserSerializer({"id": u}).data
    assert TypeID.from_string(data["id"]).prefix == "user"
    assert str(TypeID.from_string(data["id"]).uuid) == str(u)


def test_invalid_prefix_argument():
    with pytest.raises(PrefixValidationException):
        TypeIDField(prefix="Not Valid")


def test_missing_drf_raises_helpful_import_error(monkeypatch):
    monkeypatch.setitem(sys.modules, "rest_framework", None)
    monkeypatch.delitem(sys.modules, "typeid.integrations.drf")
    monkeypatch.delitem(sys.modules, "typeid.integrations.drf.fields")
    with pytest.raises(ImportError, match="pip install djangorestframework"):
        importlib.import_module("typeid.integrations.drf")
