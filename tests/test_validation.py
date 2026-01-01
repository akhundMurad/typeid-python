import pytest
from uuid6 import uuid7

from typeid import base32
from typeid.errors import PrefixValidationException, SuffixValidationException
from typeid.validation import validate_prefix, validate_suffix_and_decode


def test_validate_correct_prefix() -> None:
    prefix = "plov"

    try:
        validate_prefix(prefix)
    except PrefixValidationException as exc:
        pytest.fail(str(exc))


def test_validate_correct_prefix_with_underscores() -> None:
    prefix = "plov_good"

    try:
        validate_prefix(prefix)
    except PrefixValidationException as exc:
        pytest.fail(str(exc))


def test_validate_invalid_prefix_with_trailing_underscore() -> None:
    prefix = "plov_bad_"

    with pytest.raises(PrefixValidationException):
        validate_prefix(prefix)


def test_validate_uppercase_prefix() -> None:
    prefix = "Plov"

    with pytest.raises(PrefixValidationException):
        validate_prefix(prefix)


def test_validate_not_ascii_prefix() -> None:
    prefix = "∞¥₤€"

    with pytest.raises(PrefixValidationException):
        validate_prefix(prefix)


def test_validate_correct_suffix() -> None:
    suffix = base32.encode(uuid7().bytes)

    try:
        validate_suffix_and_decode(suffix)
    except SuffixValidationException as exc:
        pytest.fail(str(exc))


def test_validate_wrong_suffix() -> None:
    suffix = "asd"

    with pytest.raises(SuffixValidationException):
        validate_suffix_and_decode(suffix)
