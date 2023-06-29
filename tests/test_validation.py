import base64

import pytest

from typeid.errors import PrefixValidationException, SuffixValidationException
from typeid.validation import validate_prefix, validate_suffix


def test_validate_correct_prefix() -> None:
    prefix = "plov"

    try:
        validate_prefix(prefix)
    except PrefixValidationException as exc:
        pytest.fail(str(exc))


def test_validate_uppercase_prefix() -> None:
    prefix = "Plov"

    with pytest.raises(PrefixValidationException):
        validate_prefix(prefix)


def test_validate_not_ascii_prefix() -> None:
    prefix = "∞¥₤€"

    with pytest.raises(PrefixValidationException):
        validate_prefix(prefix)


def test_validate_correct_suffix() -> None:
    suffix = base64.b32encode("asd".encode("ascii")).decode("utf-8")

    try:
        validate_suffix(suffix)
    except SuffixValidationException as exc:
        pytest.fail(str(exc))


def test_validate_wrong_suffix() -> None:
    suffix = "asd"

    with pytest.raises(SuffixValidationException):
        validate_suffix(suffix)
