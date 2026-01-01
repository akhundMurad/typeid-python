import re

from typeid import base32
from typeid.constants import SUFFIX_LEN
from typeid.errors import PrefixValidationException, SuffixValidationException

_PREFIX_RE = re.compile(r"^([a-z]([a-z0-9_]{0,61}[a-z0-9])?)?$")  # allow digits too (spec-like)


def validate_prefix(prefix: str) -> None:
    # Use fullmatch (anchored) and precompiled regex
    if not _PREFIX_RE.fullmatch(prefix or ""):
        raise PrefixValidationException(f"Invalid prefix: {prefix}.")


def validate_suffix_and_decode(suffix: str) -> bytes:
    """
    Validate a TypeID suffix and return decoded UUID bytes (16 bytes).
    This guarantees: one decode per suffix on the fast path.
    """
    if (
        len(suffix) != SUFFIX_LEN
        or suffix == ""
        or " " in suffix
        or (not suffix.isdigit() and not suffix.islower())
        or any([symbol not in base32.ALPHABET for symbol in suffix])
        or suffix[0] > "7"
    ):
        raise SuffixValidationException(f"Invalid suffix: {suffix}.")

    try:
        uuid_bytes = base32.decode(suffix)  # rust-backed or py fallback
    except Exception as exc:
        raise SuffixValidationException(f"Invalid suffix: {suffix}.") from exc

    if len(uuid_bytes) != 16:
        raise SuffixValidationException(f"Invalid suffix: {suffix}.")
    return uuid_bytes
