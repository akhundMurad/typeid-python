from datetime import datetime, timezone
import warnings
import uuid_utils
from typing import Generic, Optional, TypeVar

from typeid.codecs import base32
from typeid.core.parsing import get_prefix_and_suffix
from typeid.core.validation import validate_prefix, validate_suffix_and_decode

PrefixT = TypeVar("PrefixT", bound=str)


def _uuid_from_bytes_v7(uuid_bytes: bytes) -> uuid_utils.UUID:
    """
    Construct a UUID object from bytes.
    """
    uuid_int = int.from_bytes(uuid_bytes, "big")
    return uuid_utils.UUID(int=uuid_int)


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

    __slots__ = ("_prefix", "_suffix", "_uuid_bytes", "_uuid", "_str")

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
        # Validate prefix early (cheap) so failures don't do extra work
        if prefix:
            validate_prefix(prefix=prefix)
        self._prefix: Optional[PrefixT] = prefix

        self._str: Optional[str] = None
        self._uuid: Optional[uuid_utils.UUID] = None
        self._uuid_bytes: Optional[bytes] = None

        if not suffix:
            # generate uuid (fast path)
            u = uuid_utils.uuid7()
            uuid_bytes = u.bytes
            suffix = base32.encode(uuid_bytes)
            # Cache UUID object (keep original type for user expectations)
            self._uuid = u
            self._uuid_bytes = uuid_bytes
        else:
            # validate+decode once; don't create UUID object yet
            uuid_bytes = validate_suffix_and_decode(suffix)
            self._uuid_bytes = uuid_bytes

        self._suffix = suffix

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
    def from_uuid(cls, suffix: uuid_utils.UUID, prefix: Optional[PrefixT] = None) -> "TypeID":
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
        # Validate prefix (if provided)
        if prefix:
            validate_prefix(prefix=prefix)

        uuid_bytes = suffix.bytes
        suffix_str = base32.encode(uuid_bytes)

        obj = cls.__new__(cls)  # bypass __init__ to avoid decode+validate cycle
        obj._prefix = prefix
        obj._suffix = suffix_str
        obj._uuid_bytes = uuid_bytes
        obj._uuid = suffix  # keep original object type
        obj._str = None
        return obj

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
    def uuid(self) -> uuid_utils.UUID:
        """
        The UUID represented by this TypeID.

        Returns:
            The decoded UUID value.
        """
        # Lazy materialization
        if self._uuid is None:
            assert self._uuid_bytes is not None
            self._uuid = _uuid_from_bytes_v7(self._uuid_bytes)
        return self._uuid

    @property
    def uuid_bytes(self) -> bytes:
        """
        Raw bytes of the underlying UUID.

        This returns the canonical 16-byte representation of the UUID encoded
        in this TypeID. The value is derived lazily from the suffix and cached
        on first access.

        Returns:
            A 16-byte ``bytes`` object representing the UUID.
        """
        if self._uuid_bytes is None:
            self._uuid_bytes = base32.decode(self._suffix)
        return self._uuid_bytes

    @property
    def created_at(self) -> Optional[datetime]:
        """
        Creation time embedded in the underlying UUID, if available.

        TypeID typically uses UUIDv7 for generated IDs. UUIDv7 encodes the Unix
        timestamp (milliseconds) in the most significant 48 bits of the 128-bit UUID.

        Returns:
            A timezone-aware UTC datetime if the underlying UUID is version 7,
            otherwise None.
        """
        u = self.uuid

        # Only UUIDv7 has a defined "created_at" in this sense.
        try:
            if getattr(u, "version", None) != 7:
                return None
        except Exception:
            return None

        try:
            # UUID is 128 bits; top 48 bits are unix epoch time in milliseconds.
            # So: unix_ms = uuid_int >> (128 - 48) = uuid_int >> 80
            unix_ms = int(u.int) >> 80
            return datetime.fromtimestamp(unix_ms / 1000.0, tz=timezone.utc)
        except Exception:
            return None

    def __str__(self) -> str:
        """
        Render the TypeID into its canonical string representation.

        Returns:
            "<prefix>_<suffix>" if prefix is present, otherwise "<suffix>".
        """
        # cache string representation; helps workflow + comparisons
        s = self._str
        if s is not None:
            return s
        if self.prefix:
            s = f"{self.prefix}_{self.suffix}"
        else:
            s = self.suffix
        self._str = s
        return s

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


def from_uuid(suffix: uuid_utils.UUID, prefix: Optional[str] = None) -> TypeID:
    warnings.warn("Consider TypeID.from_uuid instead.", DeprecationWarning)
    return TypeID.from_uuid(suffix=suffix, prefix=prefix)
