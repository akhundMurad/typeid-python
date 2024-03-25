import warnings
from typing import Optional
from uuid import UUID

from uuid6 import uuid7

from typeid import base32
from typeid.errors import InvalidTypeIDStringException
from typeid.validation import validate_prefix, validate_suffix


class TypeID:
    def __init__(self, prefix: Optional[str] = None, suffix: Optional[str] = None) -> None:
        suffix = _convert_uuid_to_b32(uuid7()) if not suffix else suffix
        validate_suffix(suffix=suffix)
        if prefix:
            validate_prefix(prefix=prefix)

        self._prefix = prefix or ""
        self._suffix = suffix

    @classmethod
    def from_string(cls, string: str):
        prefix, suffix = get_prefix_and_suffix(string=string)
        return cls(suffix=suffix, prefix=prefix)

    @classmethod
    def from_uuid(cls, suffix: UUID, prefix: Optional[str] = None):
        suffix_str = _convert_uuid_to_b32(suffix)
        return TypeID(suffix=suffix_str, prefix=prefix)

    @property
    def suffix(self) -> str:
        return self._suffix

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def uuid(self) -> UUID:
        return _convert_b32_to_uuid(self.suffix)

    def __str__(self) -> str:
        value = ""
        if self.prefix:
            value += f"{self.prefix}_"
        value += self.suffix
        return value

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, str(self))

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, TypeID):
            return False
        return value.prefix == self.prefix and value.suffix == self.suffix

    def __gt__(self, other):
        if isinstance(other, TypeID):
            return str(self) > str(other)
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, TypeID):
            return str(self) >= str(other)
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.prefix, self.suffix))


def from_string(string: str) -> TypeID:
    warnings.warn("Consider TypeID.from_string instead.", DeprecationWarning)
    return TypeID.from_string(string=string)


def from_uuid(suffix: UUID, prefix: Optional[str] = None) -> TypeID:
    warnings.warn("Consider TypeID.from_uuid instead.", DeprecationWarning)
    return TypeID.from_uuid(suffix=suffix, prefix=prefix)


def get_prefix_and_suffix(string: str) -> tuple:
    parts = string.split("_")
    suffix = None
    prefix = None
    if len(parts) == 1:
        suffix = parts[0]
    elif len(parts) == 2 and parts[0] != "":
        suffix = parts[1]
        prefix = parts[0]
    else:
        raise InvalidTypeIDStringException(f"Invalid TypeID: {string}")

    return prefix, suffix


def _convert_uuid_to_b32(uuid_instance: UUID) -> str:
    return base32.encode(list(uuid_instance.bytes))


def _convert_b32_to_uuid(b32: str) -> UUID:
    return UUID(bytes=bytes(base32.decode(b32)))
