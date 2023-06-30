import pytest
from uuid6 import UUID

from typeid import from_string, from_uuid


def test_invalid_spec(invalid_spec: list) -> None:
    for spec in invalid_spec:
        with pytest.raises(Exception):
            from_string(spec["typeid"])


def test_valid_spec(valid_spec: list) -> None:
    for spec in valid_spec:
        prefix = spec["prefix"]
        uuid = UUID(spec["uuid"])

        typeid = from_uuid(prefix=prefix, suffix=uuid)
        assert str(typeid) == spec["typeid"]
