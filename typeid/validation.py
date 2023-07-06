from typeid import base32
from typeid.constants import PREFIX_MAX_LEN, SUFFIX_LEN
from typeid.errors import PrefixValidationException, SuffixValidationException


def validate_prefix(prefix: str) -> None:
    if not prefix.islower() or not prefix.isascii() or len(prefix) > PREFIX_MAX_LEN or not prefix.isalpha():
        raise PrefixValidationException(f"Invalid prefix: {prefix}.")


def validate_suffix(suffix: str) -> None:
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
        base32.decode(suffix)
    except Exception as exc:
        raise SuffixValidationException(f"Invalid suffix: {suffix}.") from exc
