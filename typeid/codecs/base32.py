from typeid._base32 import encode as _encode_rust, decode as _decode_rust  # type: ignore


def encode(src: bytes) -> str:
    """
    Encode 16 raw bytes into a 26-character TypeID suffix (Rust-accelerated).

    This function is the low-level codec used by TypeID to transform the 16-byte
    UUID payload into the 26-character suffix string.

    It is **not** a general-purpose Base32 encoder:
    - Input length is strictly **16 bytes**.
    - Output length is strictly **26 characters**.
    - The alphabet is fixed to:
      ``0123456789abcdefghjkmnpqrstvwxyz`` (lowercase only).

    The mapping is a fixed bit-packing scheme:
    - The first 6 input bytes (48 bits) become the first 10 characters
      (often corresponding to the UUIDv7 timestamp portion in TypeID usage).
    - The remaining 10 bytes (80 bits) become the last 16 characters.

    Parameters
    ----------
    src : bytes
        Exactly 16 bytes to encode (the raw UUID bytes).

    Returns
    -------
    str
        A 26-character ASCII string using only the TypeID Base32 alphabet.

    Raises
    ------
    RuntimeError
        If ``src`` is not exactly 16 bytes long:
        ``"Invalid length (expected 16 bytes)."``

    Notes
    -----
    - This function is implemented in Rust and exposed via a CPython extension;
      there is no Python fallback.
    - The returned string is always lowercase.
    """

    return _encode_rust(src)


def decode(s: str) -> bytes:
    """
    Decode a 26-character TypeID suffix into 16 raw bytes (Rust-accelerated).

    This function is the inverse of :func:`encode`. It takes a TypeID suffix
    (26 characters) and reconstructs the original 16 bytes by reversing the
    same fixed bit-packing scheme.

    Decoding is strict:
    - Input length must be exactly **26 characters**.
    - Only characters from the alphabet
      ``0123456789abcdefghjkmnpqrstvwxyz`` are accepted.
    - Uppercase letters, whitespace, separators, and Crockford aliases
      (e.g. 'O'→'0', 'I'/'L'→'1') are **not** accepted.

    Parameters
    ----------
    s : str
        The 26-character suffix string to decode.

    Returns
    -------
    bytes
        Exactly 16 bytes (the raw UUID bytes).

    Raises
    ------
    RuntimeError
        If ``s`` is not exactly 26 characters long:
        ``"Invalid length (expected 26 chars)."``

        If ``s`` contains any character outside the allowed alphabet:
        ``"Invalid base32 character."``

    Notes
    -----
    - This function is implemented in Rust and exposed via a CPython extension;
      there is no Python fallback.
    - This performs only decoding/validation of the suffix encoding. It does not
      validate UUID version/variant semantics.
    """

    return _decode_rust(s)
