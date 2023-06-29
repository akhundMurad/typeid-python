import base64
from typing import Optional
from uuid import UUID

from uuid6 import uuid7

from typeid.errors import InvalidTypeIDStringException
from typeid.validation import validate_prefix, validate_suffix

B32_LEN = 26


class TypeID:
    def __init__(self, prefix: Optional[str] = None, suffix: Optional[str] = None) -> None:
        suffix = _convert_uuid_to_b32(uuid7()) if not suffix else suffix
        validate_suffix(suffix=suffix)
        if prefix:
            validate_prefix(prefix=prefix)

        self._prefix = prefix
        self._suffix = suffix[:26].lower()

    @property
    def suffix(self) -> str:
        return self._suffix

    @property
    def prefix(self) -> Optional[str]:
        return self._prefix

    def __str__(self) -> str:
        value = ""
        if self.prefix:
            value += f"{self.prefix}_"
        value += self.suffix
        return value


def from_string(string: str) -> TypeID:
    parts = string.split("_")

    if len(parts) == 1:
        return TypeID(suffix=parts[1])
    elif len(parts) == 2:
        return TypeID(suffix=parts[1], prefix=parts[0])
    else:
        raise InvalidTypeIDStringException(f"Invalid TypeID: {string}")


def from_uuid(prefix: str, suffix: UUID) -> TypeID:
    suffix_str = _convert_uuid_to_b32(suffix)
    return TypeID(suffix=suffix_str, prefix=prefix)


def _convert_uuid_to_b32(uuid_instance: UUID) -> str:
    return base64.b32encode(uuid_instance.bytes).decode("ascii")
