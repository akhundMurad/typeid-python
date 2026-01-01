try:
    from typeid_base32 import encode as _encode_rust, decode as _decode_rust  # type: ignore

    _HAS_RUST = True
except Exception:
    _HAS_RUST = False
    _encode_rust = None
    _decode_rust = None

from typing import Union
from typeid.constants import SUFFIX_LEN

ALPHABET = "0123456789abcdefghjkmnpqrstvwxyz"

# TABLE maps ASCII byte -> 0..31 or 0xFF if invalid
TABLE = [
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0x00,
    0x01,
    0x02,
    0x03,
    0x04,
    0x05,
    0x06,
    0x07,
    0x08,
    0x09,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0x0A,
    0x0B,
    0x0C,
    0x0D,
    0x0E,
    0x0F,
    0x10,
    0x11,
    0xFF,
    0x12,
    0x13,
    0xFF,
    0x14,
    0x15,
    0xFF,
    0x16,
    0x17,
    0x18,
    0x19,
    0x1A,
    0xFF,
    0x1B,
    0x1C,
    0x1D,
    0x1E,
    0x1F,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0x0A,
    0x0B,
    0x0C,
    0x0D,
    0x0E,
    0x0F,
    0x10,
    0x11,
    0xFF,
    0x12,
    0x13,
    0xFF,
    0x14,
    0x15,
    0xFF,
    0x16,
    0x17,
    0x18,
    0x19,
    0x1A,
    0xFF,
    0x1B,
    0x1C,
    0x1D,
    0x1E,
    0x1F,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
] + [0xFF] * (256 - 128)


BytesLike = Union[bytes, bytearray, memoryview]


def _encode_py(src: BytesLike) -> str:
    mv = memoryview(src)
    if mv.nbytes != 16:
        raise RuntimeError("Invalid length.")

    # Pre-allocate output chars
    dst = [""] * SUFFIX_LEN

    # Timestamp (6 bytes => 10 chars)
    dst[0] = ALPHABET[(mv[0] & 0b11100000) >> 5]
    dst[1] = ALPHABET[mv[0] & 0b00011111]
    dst[2] = ALPHABET[(mv[1] & 0b11111000) >> 3]
    dst[3] = ALPHABET[((mv[1] & 0b00000111) << 2) | ((mv[2] & 0b11000000) >> 6)]
    dst[4] = ALPHABET[(mv[2] & 0b00111110) >> 1]
    dst[5] = ALPHABET[((mv[2] & 0b00000001) << 4) | ((mv[3] & 0b11110000) >> 4)]
    dst[6] = ALPHABET[((mv[3] & 0b00001111) << 1) | ((mv[4] & 0b10000000) >> 7)]
    dst[7] = ALPHABET[(mv[4] & 0b01111100) >> 2]
    dst[8] = ALPHABET[((mv[4] & 0b00000011) << 3) | ((mv[5] & 0b11100000) >> 5)]
    dst[9] = ALPHABET[mv[5] & 0b00011111]

    # Entropy (10 bytes => 16 chars)
    dst[10] = ALPHABET[(mv[6] & 0b11111000) >> 3]
    dst[11] = ALPHABET[((mv[6] & 0b00000111) << 2) | ((mv[7] & 0b11000000) >> 6)]
    dst[12] = ALPHABET[(mv[7] & 0b00111110) >> 1]
    dst[13] = ALPHABET[((mv[7] & 0b00000001) << 4) | ((mv[8] & 0b11110000) >> 4)]
    dst[14] = ALPHABET[((mv[8] & 0b00001111) << 1) | ((mv[9] & 0b10000000) >> 7)]
    dst[15] = ALPHABET[(mv[9] & 0b01111100) >> 2]
    dst[16] = ALPHABET[((mv[9] & 0b00000011) << 3) | ((mv[10] & 0b11100000) >> 5)]
    dst[17] = ALPHABET[mv[10] & 0b00011111]
    dst[18] = ALPHABET[(mv[11] & 0b11111000) >> 3]
    dst[19] = ALPHABET[((mv[11] & 0b00000111) << 2) | ((mv[12] & 0b11000000) >> 6)]
    dst[20] = ALPHABET[(mv[12] & 0b00111110) >> 1]
    dst[21] = ALPHABET[((mv[12] & 0b00000001) << 4) | ((mv[13] & 0b11110000) >> 4)]
    dst[22] = ALPHABET[((mv[13] & 0b00001111) << 1) | ((mv[14] & 0b10000000) >> 7)]
    dst[23] = ALPHABET[(mv[14] & 0b01111100) >> 2]
    dst[24] = ALPHABET[((mv[14] & 0b00000011) << 3) | ((mv[15] & 0b11100000) >> 5)]
    dst[25] = ALPHABET[mv[15] & 0b00011111]

    return "".join(dst)


def _decode_py(s: str) -> bytes:
    if len(s) != SUFFIX_LEN:
        raise RuntimeError("Invalid length.")

    v = s.encode("utf-8")
    tbl = TABLE

    # ✅ FIX: fail if ANY character is invalid (not only if ALL are invalid)
    for b in v:
        if tbl[b] == 0xFF:
            raise RuntimeError("Invalid base32 character")

    out = bytearray(16)

    # 6 bytes timestamp (48 bits)
    out[0] = (tbl[v[0]] << 5) | tbl[v[1]]
    out[1] = (tbl[v[2]] << 3) | (tbl[v[3]] >> 2)
    out[2] = ((tbl[v[3]] & 3) << 6) | (tbl[v[4]] << 1) | (tbl[v[5]] >> 4)
    out[3] = ((tbl[v[5]] & 15) << 4) | (tbl[v[6]] >> 1)
    out[4] = ((tbl[v[6]] & 1) << 7) | (tbl[v[7]] << 2) | (tbl[v[8]] >> 3)
    out[5] = ((tbl[v[8]] & 7) << 5) | tbl[v[9]]

    # 10 bytes entropy (80 bits)
    out[6] = (tbl[v[10]] << 3) | (tbl[v[11]] >> 2)
    out[7] = ((tbl[v[11]] & 3) << 6) | (tbl[v[12]] << 1) | (tbl[v[13]] >> 4)
    out[8] = ((tbl[v[13]] & 15) << 4) | (tbl[v[14]] >> 1)
    out[9] = ((tbl[v[14]] & 1) << 7) | (tbl[v[15]] << 2) | (tbl[v[16]] >> 3)
    out[10] = ((tbl[v[16]] & 7) << 5) | tbl[v[17]]
    out[11] = (tbl[v[18]] << 3) | (tbl[v[19]] >> 2)
    out[12] = ((tbl[v[19]] & 3) << 6) | (tbl[v[20]] << 1) | (tbl[v[21]] >> 4)
    out[13] = ((tbl[v[21]] & 15) << 4) | (tbl[v[22]] >> 1)
    out[14] = ((tbl[v[22]] & 1) << 7) | (tbl[v[23]] << 2) | (tbl[v[24]] >> 3)
    out[15] = ((tbl[v[24]] & 7) << 5) | tbl[v[25]]

    return bytes(out)


def encode(src: bytes) -> str:
    if _HAS_RUST:
        return _encode_rust(src)
    return _encode_py(src)


def decode(s: str) -> bytes:
    if _HAS_RUST:
        return _decode_rust(s)
    return _decode_py(s)
