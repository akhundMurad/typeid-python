from typeid.errors import SuffixValidationException

try:
    from typeid_base32 import encode as _encode_rust, decode as _decode_rust
    _HAS_RUST = True
except Exception:
    _HAS_RUST = False
    _encode_rust = None
    _decode_rust = None

# Keep your existing pure-Python encode/decode as _encode_py / _decode_py

def encode(src: bytes) -> str:
    if _HAS_RUST:
        try:
            return _encode_rust(src)
        except ValueError as e:
            raise SuffixValidationException(str(e))
    return _encode_py(src)

def decode(s: str) -> bytes:
    if _HAS_RUST:
        try:
            return _decode_rust(s)
        except ValueError as e:
            raise SuffixValidationException(str(e))
    return _decode_py(s)
