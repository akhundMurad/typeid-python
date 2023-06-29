import base64

from typeid.errors import PrefixValidationException, SuffixValidationException


def validate_prefix(prefix: str) -> None:
    if not prefix.islower() or not prefix.isascii():
        raise PrefixValidationException(f"Invalid prefix: {prefix}. Prefix can only have lowercase ASCII characters.")


def validate_suffix(suffix: str) -> None:
    if suffix == "":
        raise SuffixValidationException("Suffix cannot be empty.")
    try:
        base64.b32decode(suffix)
    except Exception as exc:
        raise SuffixValidationException(f"Invalid suffix: {suffix}.") from exc
