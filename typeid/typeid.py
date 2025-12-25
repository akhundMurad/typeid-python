import uuid
import warnings
from typing import Generic, Optional, TypeVar

import uuid6

from typeid import base32
from typeid.errors import InvalidTypeIDStringException
from typeid.validation import validate_prefix, validate_suffix

PrefixT = TypeVar("PrefixT", bound=str)


class TypeID(Generic[PrefixT]):
    """
    A TypeID is a human-meaningful, UUID-backed identifier.

    A TypeID is rendered as:

        <prefix>_<suffix>   or just   <suffix>  (when prefix is None/empty)

    - **prefix**: optional semantic label (e.g. "user", "order"). It is *not* part of the UUID.
      Prefixes are validated for allowed characters/shape (see `validate_prefix`).
    - **suffix**: a compact, URL-safe Base32 encoding of a UUID (UUIDv7 by default).
      Suffixes are validated structurally (see `validate_suffix`).

    Design notes:
    - A TypeID is intended to be safe to store as a string (e.g. in logs / URLs).
    - The underlying UUID can always be recovered via `.uuid`.
    - Ordering (`>`, `>=`) is based on lexicographic order of the string representation,
      which corresponds to time-ordering if the UUID version is time-sortable (UUIDv7).

    Type parameters:
        PrefixT: a type-level constraint for the prefix (often `str` or a Literal).
    """

    def __init__(self, prefix: Optional[PrefixT] = None, suffix: Optional[str] = None) -> None:
        """
        Create a new TypeID.

        If `suffix` is not provided, a new UUIDv7 is generated and encoded as Base32.
        If `prefix` is provided, it is validated.

        Args:
            prefix: Optional prefix. If None, the TypeID has no prefix and its string
                form will be just the suffix. If provided, it must pass `validate_prefix`.
            suffix: Optional Base32-encoded UUID string. If None, a new UUIDv7 is generated.

        Raises:
            InvalidTypeIDStringException (or another project-specific exception):
                If `suffix` is invalid, or if `prefix` is invalid.
        """
        # If no suffix is provided, generate a new UUIDv7 and encode it as Base32.
        suffix = _convert_uuid_to_b32(uuid6.uuid7()) if not suffix else suffix

        # Ensure the suffix is a valid encoded UUID representation.
        validate_suffix(suffix=suffix)

        # Prefix is optional; when present it must satisfy the project's prefix rules.
        if prefix is not None:
            validate_prefix(prefix=prefix)

        # Keep prefix as Optional internally. String rendering decides whether to show it.
        self._prefix: Optional[PrefixT] = prefix
        self._suffix: str = suffix

    @classmethod
    def from_string(cls, string: str) -> "TypeID":
        """
        Parse a TypeID from its string form.

        The input can be either:
        - "<prefix>_<suffix>"
        - "<suffix>" (prefix-less)

        Args:
            string: String representation of a TypeID.

        Returns:
            A `TypeID` instance.

        Raises:
            InvalidTypeIDStringException (or another project-specific exception):
                If the string cannot be split/parsed or if the extracted parts are invalid.
        """
        # Split into (prefix, suffix) according to project rules.
        prefix, suffix = get_prefix_and_suffix(string=string)
        return cls(suffix=suffix, prefix=prefix)

    @classmethod
    def from_uuid(cls, suffix: uuid.UUID, prefix: Optional[PrefixT] = None) -> "TypeID":
        """
        Construct a TypeID from an existing UUID.

        This is useful when you store UUIDs in a database but want to expose
        TypeIDs at the application boundary.

        Args:
            suffix: UUID value to encode into the TypeID suffix.
            prefix: Optional prefix to attach (validated if provided).

        Returns:
            A `TypeID` whose `.uuid` equals the provided UUID.
        """
        # Encode the UUID into the canonical Base32 suffix representation.
        suffix_str = _convert_uuid_to_b32(suffix)
        return cls(suffix=suffix_str, prefix=prefix)

    @property
    def suffix(self) -> str:
        """
        The Base32-encoded UUID portion of the TypeID (always present).

        Notes:
            - This is the identity-carrying part.
            - It is validated at construction time.
        """
        return self._suffix

    @property
    def prefix(self) -> str:
        """
        The prefix portion of the TypeID, as a string.

        Returns:
            The configured prefix, or "" if the TypeID is prefix-less.

        Notes:
            - Empty string is the *presentation* of "no prefix". Internally, `_prefix`
              remains Optional to preserve the distinction between None and a real value.
        """
        return self._prefix or ""

    @property
    def uuid(self) -> uuid6.UUID:
        """
        The UUID represented by this TypeID.

        Returns:
            The decoded UUID value.

        Notes:
            - This decodes `self.suffix` each time it is accessed.
            - The UUID type here follows `uuid6.UUID` used by the project.
        """
        return _convert_b32_to_uuid(self.suffix)

    def __str__(self) -> str:
        """
        Render the TypeID into its canonical string representation.

        Returns:
            "<prefix>_<suffix>" if prefix is present, otherwise "<suffix>".
        """
        value = ""
        if self.prefix:
            value += f"{self.prefix}_"
        value += self.suffix
        return value

    def __repr__(self):
        """
        Developer-friendly representation.

        Uses a constructor-like form to make debugging and copy/paste easier.
        """
        return "%s.from_string(%r)" % (self.__class__.__name__, str(self))

    def __eq__(self, value: object) -> bool:
        """
        Equality based on prefix and suffix.

        Notes:
            - Two TypeIDs are considered equal if both their string components match.
            - This is stricter than "same UUID" because prefix is part of the public ID.
        """
        if not isinstance(value, TypeID):
            return False
        return value.prefix == self.prefix and value.suffix == self.suffix

    def __gt__(self, other) -> bool:
        """
        Compare TypeIDs by lexicographic order of their string form.

        This is useful because TypeID suffixes based on UUIDv7 are time-sortable,
        so string order typically corresponds to creation time order (within a prefix).

        Returns:
            True/False if `other` is a TypeID, otherwise NotImplemented.
        """
        if isinstance(other, TypeID):
            return str(self) > str(other)
        return NotImplemented

    def __ge__(self, other) -> bool:
        """
        Compare TypeIDs by lexicographic order of their string form (>=).

        See `__gt__` for rationale and notes.
        """
        if isinstance(other, TypeID):
            return str(self) >= str(other)
        return NotImplemented

    def __hash__(self) -> int:
        """
        Hash based on (prefix, suffix), allowing TypeIDs to be used as dict keys / set members.
        """
        return hash((self.prefix, self.suffix))


def from_string(string: str) -> TypeID:
    warnings.warn("Consider TypeID.from_string instead.", DeprecationWarning)
    return TypeID.from_string(string=string)


def from_uuid(suffix: uuid.UUID, prefix: Optional[str] = None) -> TypeID:
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


def _convert_uuid_to_b32(uuid_instance: uuid.UUID) -> str:
    return base32.encode(list(uuid_instance.bytes))


def _convert_b32_to_uuid(b32: str) -> uuid6.UUID:
    uuid_bytes = bytes(base32.decode(b32))
    uuid_int = int.from_bytes(uuid_bytes, byteorder="big")
    return uuid6.UUID(int=uuid_int, version=7)
