use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyModule;

const SUFFIX_LEN: usize = 26;
const UUID_LEN: usize = 16;

const ALPHABET: &[u8; 32] = b"0123456789abcdefghjkmnpqrstvwxyz";

#[inline]
fn build_table() -> [u8; 256] {
    let mut t = [0xFFu8; 256];
    for (i, &ch) in ALPHABET.iter().enumerate() {
        t[ch as usize] = i as u8;
    }

    t
}

#[pyfunction]
fn encode(src: &[u8]) -> PyResult<String> {
    if src.len() != UUID_LEN {
        return Err(PyRuntimeError::new_err("Invalid length (expected 16 bytes)."));
    }
    let b = src;

    let mut out = [0u8; SUFFIX_LEN];

    // Timestamp (6 bytes => 10 chars)
    out[0] = ALPHABET[((b[0] & 0b1110_0000) >> 5) as usize];
    out[1] = ALPHABET[(b[0] & 0b0001_1111) as usize];
    out[2] = ALPHABET[((b[1] & 0b1111_1000) >> 3) as usize];
    out[3] = ALPHABET[(((b[1] & 0b0000_0111) << 2) | ((b[2] & 0b1100_0000) >> 6)) as usize];
    out[4] = ALPHABET[((b[2] & 0b0011_1110) >> 1) as usize];
    out[5] = ALPHABET[(((b[2] & 0b0000_0001) << 4) | ((b[3] & 0b1111_0000) >> 4)) as usize];
    out[6] = ALPHABET[(((b[3] & 0b0000_1111) << 1) | ((b[4] & 0b1000_0000) >> 7)) as usize];
    out[7] = ALPHABET[((b[4] & 0b0111_1100) >> 2) as usize];
    out[8] = ALPHABET[(((b[4] & 0b0000_0011) << 3) | ((b[5] & 0b1110_0000) >> 5)) as usize];
    out[9] = ALPHABET[(b[5] & 0b0001_1111) as usize];

    // Entropy (10 bytes => 16 chars)
    out[10] = ALPHABET[((b[6] & 0b1111_1000) >> 3) as usize];
    out[11] = ALPHABET[(((b[6] & 0b0000_0111) << 2) | ((b[7] & 0b1100_0000) >> 6)) as usize];
    out[12] = ALPHABET[((b[7] & 0b0011_1110) >> 1) as usize];
    out[13] = ALPHABET[(((b[7] & 0b0000_0001) << 4) | ((b[8] & 0b1111_0000) >> 4)) as usize];
    out[14] = ALPHABET[(((b[8] & 0b0000_1111) << 1) | ((b[9] & 0b1000_0000) >> 7)) as usize];
    out[15] = ALPHABET[((b[9] & 0b0111_1100) >> 2) as usize];
    out[16] = ALPHABET[(((b[9] & 0b0000_0011) << 3) | ((b[10] & 0b1110_0000) >> 5)) as usize];
    out[17] = ALPHABET[(b[10] & 0b0001_1111) as usize];
    out[18] = ALPHABET[((b[11] & 0b1111_1000) >> 3) as usize];
    out[19] = ALPHABET[(((b[11] & 0b0000_0111) << 2) | ((b[12] & 0b1100_0000) >> 6)) as usize];
    out[20] = ALPHABET[((b[12] & 0b0011_1110) >> 1) as usize];
    out[21] = ALPHABET[(((b[12] & 0b0000_0001) << 4) | ((b[13] & 0b1111_0000) >> 4)) as usize];
    out[22] = ALPHABET[(((b[13] & 0b0000_1111) << 1) | ((b[14] & 0b1000_0000) >> 7)) as usize];
    out[23] = ALPHABET[((b[14] & 0b0111_1100) >> 2) as usize];
    out[24] = ALPHABET[(((b[14] & 0b0000_0011) << 3) | ((b[15] & 0b1110_0000) >> 5)) as usize];
    out[25] = ALPHABET[(b[15] & 0b0001_1111) as usize];

    // Safe because alphabet is ASCII
    Ok(String::from_utf8(out.to_vec()).unwrap())
}

#[pyfunction]
fn decode(s: &str) -> PyResult<Vec<u8>> {
    if s.len() != SUFFIX_LEN {
        return Err(PyRuntimeError::new_err("Invalid length (expected 26 chars)."));
    }

    let t = build_table();
    let bytes = s.as_bytes();

    // Validate
    for &ch in bytes {
        if t[ch as usize] == 0xFF {
            return Err(PyRuntimeError::new_err("Invalid base32 character."));
        }
    }

    #[inline]
    fn v(t: &[u8; 256], bytes: &[u8], i: usize) -> u8 {
        t[bytes[i] as usize]
    }

    let mut out = [0u8; UUID_LEN];

    // Timestamp (48 bits)
    out[0] = (v(&t, bytes, 0) << 5) | v(&t, bytes, 1);
    out[1] = (v(&t, bytes, 2) << 3) | (v(&t, bytes, 3) >> 2);
    out[2] = ((v(&t, bytes, 3) & 3) << 6) | (v(&t, bytes, 4) << 1) | (v(&t, bytes, 5) >> 4);
    out[3] = ((v(&t, bytes, 5) & 15) << 4) | (v(&t, bytes, 6) >> 1);
    out[4] = ((v(&t, bytes, 6) & 1) << 7) | (v(&t, bytes, 7) << 2) | (v(&t, bytes, 8) >> 3);
    out[5] = ((v(&t, bytes, 8) & 7) << 5) | v(&t, bytes, 9);

    // Entropy (80 bits)
    out[6]  = (v(&t, bytes, 10) << 3) | (v(&t, bytes, 11) >> 2);
    out[7]  = ((v(&t, bytes, 11) & 3) << 6) | (v(&t, bytes, 12) << 1) | (v(&t, bytes, 13) >> 4);
    out[8]  = ((v(&t, bytes, 13) & 15) << 4) | (v(&t, bytes, 14) >> 1);
    out[9]  = ((v(&t, bytes, 14) & 1) << 7) | (v(&t, bytes, 15) << 2) | (v(&t, bytes, 16) >> 3);
    out[10] = ((v(&t, bytes, 16) & 7) << 5) | v(&t, bytes, 17);
    out[11] = (v(&t, bytes, 18) << 3) | (v(&t, bytes, 19) >> 2);
    out[12] = ((v(&t, bytes, 19) & 3) << 6) | (v(&t, bytes, 20) << 1) | (v(&t, bytes, 21) >> 4);
    out[13] = ((v(&t, bytes, 21) & 15) << 4) | (v(&t, bytes, 22) >> 1);
    out[14] = ((v(&t, bytes, 22) & 1) << 7) | (v(&t, bytes, 23) << 2) | (v(&t, bytes, 24) >> 3);
    out[15] = ((v(&t, bytes, 24) & 7) << 5) | v(&t, bytes, 25);

    Ok(out.to_vec())
}

#[pymodule]
fn _base32(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(encode, m)?)?;
    m.add_function(wrap_pyfunction!(decode, m)?)?;
    Ok(())
}
