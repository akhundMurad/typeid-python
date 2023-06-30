from typeid.base32 import decode, encode


def test_encode_decode_logic() -> None:
    original_data = list(range(0, 16))

    encoded_data = encode(original_data)

    assert isinstance(encoded_data, str)

    assert encoded_data == "00041061050r3gg28a1c60t3gf"

    decoded_data = decode(encoded_data)

    assert decoded_data == original_data
