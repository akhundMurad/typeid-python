from typeid._base32 import encode as _encode_rust, decode as _decode_rust


def encode(src: bytes) -> str:
    return _encode_rust(src)


def decode(s: str) -> bytes:
    return _decode_rust(s)
