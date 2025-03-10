import warnings
from typing import Optional

import uuid6

from typeid import base32
from typeid.errors import InvalidTypeIDStringException
from typeid.validation import validate_prefix, validate_suffix


class TypeID:
    def __init__(self, prefix: Optional[str] = None, suffix: Optional[str] = None) -> None:
        suffix = _convert_uuid_to_b32(uuid6.uuid7()) if not suffix else suffix
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
    def from_uuid(cls, suffix: uuid6.UUID, prefix: Optional[str] = None):
        suffix_str = _convert_uuid_to_b32(suffix)
        return cls(suffix=suffix_str, prefix=prefix)

    @property
    def suffix(self) -> str:
        return self._suffix

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def uuid(self) -> uuid6.UUID:
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


def from_uuid(suffix: uuid6.UUID, prefix: Optional[str] = None) -> TypeID:
    warnings.warn("Consider TypeID.from_uuid instead.", DeprecationWarning)
    return TypeID.from_uuid(suffix=suffix, prefix=prefix)


def get_prefix_and_suffix(string: str) -> tuple:
    parts = string.rsplit("_", 1)

    # When there's no underscore in the string.
    if len(parts) == 1:
        if parts[0].strip() == "":
            raise InvalidTypeIDStringException(f"Invalid TypeID: {string}")
        return None, parts[0]

    # When there is an underscore, unpack prefix and suffix.
    prefix, suffix = parts
    if prefix.strip() == "" or suffix.strip() == "":
        raise InvalidTypeIDStringException(f"Invalid TypeID: {string}")

    return prefix, suffix


def _convert_uuid_to_b32(uuid_instance: uuid6.UUID) -> str:
    return base32.encode(list(uuid_instance.bytes))


def _convert_b32_to_uuid(b32: str) -> uuid6.UUID:
    uuid_bytes = bytes(base32.decode(b32))
    uuid_int = int.from_bytes(uuid_bytes, byteorder="big")
    return uuid6.UUID(int=uuid_int, version=7)
