from typeid import base32
from typeid.constants import PREFIX_MAX_LEN
from typeid.errors import PrefixValidationException, SuffixValidationException


def validate_prefix(prefix: str) -> None:
    if not prefix.islower() or not prefix.isascii() or len(prefix) > PREFIX_MAX_LEN:
        raise PrefixValidationException(f"Invalid prefix: {prefix}. Prefix can only have lowercase ASCII characters.")


def validate_suffix(suffix: str) -> None:
    if suffix == "":
        raise SuffixValidationException("Suffix cannot be empty.")
    try:
        base32.decode(suffix)
    except Exception as exc:
        raise SuffixValidationException(f"Invalid suffix: {suffix}.") from exc
