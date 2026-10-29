from typing import Any, Optional
import uuid

import uuid_utils

try:
    from rest_framework import serializers  # type: ignore[import-untyped]
except ImportError as exc:
    raise ImportError(
        "typeid.integrations.drf requires Django REST Framework. Install it with `pip install djangorestframework`."
    ) from exc

from typeid import TypeID
from typeid.core.errors import TypeIDException
from typeid.core.validation import validate_prefix


class TypeIDField(serializers.Field):
    """
    Django REST Framework serializer field for TypeIDs.

    - Accepts a TypeID string (or a `TypeID` instance) and returns a `TypeID`.
    - Optionally enforces a fixed prefix.
    - Serializes to the TypeID string. With a prefix set, plain UUIDs (for
      example a UUID primary key) are rendered as `<prefix>_<suffix>`.

    Example:
        class UserSerializer(serializers.Serializer):
            id = TypeIDField(prefix="user")
    """

    default_error_messages = {
        "invalid": "Must be a valid TypeID string.",
        "prefix": "Expected a TypeID with prefix '{expected}', got '{actual}'.",
    }

    def __init__(self, prefix: Optional[str] = None, **kwargs: Any) -> None:
        if prefix:
            validate_prefix(prefix)
        self.prefix = prefix
        super().__init__(**kwargs)

    def to_internal_value(self, data: Any) -> TypeID:
        if isinstance(data, TypeID):
            tid = data
        elif isinstance(data, str):
            try:
                tid = TypeID.from_string(data)
            except TypeIDException:
                self.fail("invalid")
        else:
            self.fail("invalid")

        if self.prefix is not None and tid.prefix != self.prefix:
            self.fail("prefix", expected=self.prefix, actual=tid.prefix)
        return tid

    def to_representation(self, value: Any) -> str:
        if isinstance(value, uuid.UUID):
            value = uuid_utils.UUID(int=value.int)
        if isinstance(value, uuid_utils.UUID):
            value = TypeID.from_uuid(value, prefix=self.prefix)
        return str(value)
