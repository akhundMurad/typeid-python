import builtins
import importlib
import sys

import pytest
from typeid.base32 import decode, encode


def test_encode_decode_logic() -> None:
    original_data = bytes(range(0, 16))

    encoded_data = encode(original_data)

    assert isinstance(encoded_data, str)

    assert encoded_data == "00041061050r3gg28a1c60t3gf"

    decoded_data = decode(encoded_data)

    assert decoded_data == original_data


def _reload_base32():
    sys.modules.pop("typeid.base32", None)
    return importlib.import_module("typeid.base32")


def test_uses_rust_if_available():
    """
    If the native module is importable, typeid.base32 should pick Rust backend.
    If native module is not installed in this environment, skip (can't force it).
    """
    try:
        import typeid_base32  # noqa: F401
    except Exception:
        pytest.skip("Rust extension typeid_base32 not installed in this environment")

    base32 = _reload_base32()
    assert base32._HAS_RUST


def test_falls_back_to_python_when_rust_missing(monkeypatch):
    """
    Force ImportError for typeid_base32 and re-import typeid.base32.
    This must select Python backend.
    """
    real_import = builtins.__import__

    def blocked_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "typeid_base32":
            raise ImportError("blocked by test")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", blocked_import)

    base32 = _reload_base32()
    assert not base32._HAS_RUST
