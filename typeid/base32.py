from typing import List

from typeid.constants import SUFFIX_LEN

ALPHABET = "0123456789abcdefghjkmnpqrstvwxyz"


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
]


def encode(src: List[int]) -> str:
    dst = [""] * SUFFIX_LEN

    if len(src) != 16:
        raise RuntimeError("Invalid length.")

    # 10 byte timestamp
    dst[0] = ALPHABET[(src[0] & 224) >> 5]
    dst[1] = ALPHABET[src[0] & 31]
    dst[2] = ALPHABET[(src[1] & 248) >> 3]
    dst[3] = ALPHABET[((src[1] & 7) << 2) | ((src[2] & 192) >> 6)]
    dst[4] = ALPHABET[(src[2] & 62) >> 1]
    dst[5] = ALPHABET[((src[2] & 1) << 4) | ((src[3] & 240) >> 4)]
    dst[6] = ALPHABET[((src[3] & 15) << 1) | ((src[4] & 128) >> 7)]
    dst[7] = ALPHABET[(src[4] & 124) >> 2]
    dst[8] = ALPHABET[((src[4] & 3) << 3) | ((src[5] & 224) >> 5)]
    dst[9] = ALPHABET[src[5] & 31]

    # 16 bytes of randomness
    dst[10] = ALPHABET[(src[6] & 248) >> 3]
    dst[11] = ALPHABET[((src[6] & 7) << 2) | ((src[7] & 192) >> 6)]
    dst[12] = ALPHABET[(src[7] & 62) >> 1]
    dst[13] = ALPHABET[((src[7] & 1) << 4) | ((src[8] & 240) >> 4)]
    dst[14] = ALPHABET[((src[8] & 15) << 1) | ((src[9] & 128) >> 7)]
    dst[15] = ALPHABET[(src[9] & 124) >> 2]
    dst[16] = ALPHABET[((src[9] & 3) << 3) | ((src[10] & 224) >> 5)]
    dst[17] = ALPHABET[src[10] & 31]
    dst[18] = ALPHABET[(src[11] & 248) >> 3]
    dst[19] = ALPHABET[((src[11] & 7) << 2) | ((src[12] & 192) >> 6)]
    dst[20] = ALPHABET[(src[12] & 62) >> 1]
    dst[21] = ALPHABET[((src[12] & 1) << 4) | ((src[13] & 240) >> 4)]
    dst[22] = ALPHABET[((src[13] & 15) << 1) | ((src[14] & 128) >> 7)]
    dst[23] = ALPHABET[(src[14] & 124) >> 2]
    dst[24] = ALPHABET[((src[14] & 3) << 3) | ((src[15] & 224) >> 5)]
    dst[25] = ALPHABET[src[15] & 31]

    return "".join(dst)


def decode(s: str) -> List[int]:
    v = bytes(s, encoding="utf-8")

    if (
        TABLE[v[0]] == 0xFF
        and TABLE[v[1]] == 0xFF
        and TABLE[v[2]] == 0xFF
        and TABLE[v[3]] == 0xFF
        and TABLE[v[4]] == 0xFF
        and TABLE[v[5]] == 0xFF
        and TABLE[v[6]] == 0xFF
        and TABLE[v[7]] == 0xFF
        and TABLE[v[8]] == 0xFF
        and TABLE[v[9]] == 0xFF
        and TABLE[v[10]] == 0xFF
        and TABLE[v[11]] == 0xFF
        and TABLE[v[12]] == 0xFF
        and TABLE[v[13]] == 0xFF
        and TABLE[v[14]] == 0xFF
        and TABLE[v[15]] == 0xFF
        and TABLE[v[16]] == 0xFF
        and TABLE[v[17]] == 0xFF
        and TABLE[v[18]] == 0xFF
        and TABLE[v[19]] == 0xFF
        and TABLE[v[20]] == 0xFF
        and TABLE[v[21]] == 0xFF
        and TABLE[v[22]] == 0xFF
        and TABLE[v[23]] == 0xFF
        and TABLE[v[24]] == 0xFF
        and TABLE[v[25]] == 0xFF
    ):
        raise RuntimeError("Invalid base32 character")

    typeid = [0] * 16

    # 6 bytes timestamp (48 bits)
    typeid[0] = (TABLE[v[0]] << 5) | TABLE[v[1]]
    typeid[1] = (TABLE[v[2]] << 3) | (TABLE[v[3]] >> 2)
    typeid[2] = ((TABLE[v[3]] & 3) << 6) | (TABLE[v[4]] << 1) | (TABLE[v[5]] >> 4)
    typeid[3] = ((TABLE[v[5]] & 15) << 4) | (TABLE[v[6]] >> 1)
    typeid[4] = ((TABLE[v[6]] & 1) << 7) | (TABLE[v[7]] << 2) | (TABLE[v[8]] >> 3)
    typeid[5] = ((TABLE[v[8]] & 7) << 5) | TABLE[v[9]]

    # 10 bytes of entropy (80 bits)
    typeid[6] = (TABLE[v[10]] << 3) | (TABLE[v[11]] >> 2)
    typeid[7] = ((TABLE[v[11]] & 3) << 6) | (TABLE[v[12]] << 1) | (TABLE[v[13]] >> 4)
    typeid[8] = ((TABLE[v[13]] & 15) << 4) | (TABLE[v[14]] >> 1)
    typeid[9] = ((TABLE[v[14]] & 1) << 7) | (TABLE[v[15]] << 2) | (TABLE[v[16]] >> 3)
    typeid[10] = ((TABLE[v[16]] & 7) << 5) | TABLE[v[17]]
    typeid[11] = (TABLE[v[18]] << 3) | (TABLE[v[19]] >> 2)
    typeid[12] = ((TABLE[v[19]] & 3) << 6) | (TABLE[v[20]] << 1) | (TABLE[v[21]] >> 4)
    typeid[13] = ((TABLE[v[21]] & 15) << 4) | (TABLE[v[22]] >> 1)
    typeid[14] = ((TABLE[v[22]] & 1) << 7) | (TABLE[v[23]] << 2) | (TABLE[v[24]] >> 3)
    typeid[15] = ((TABLE[v[24]] & 7) << 5) | TABLE[v[25]]

    return typeid
