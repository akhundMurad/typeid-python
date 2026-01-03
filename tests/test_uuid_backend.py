import pytest

from typeid._uuid_backend import get_uuid_backend


@pytest.mark.parametrize(
    "value,expected",
    [
        ("uuid6", "uuid6"),
        ("uuid-utils", "uuid-utils"),
    ],
)
def test_backend_forced(monkeypatch, value, expected):
    try:
        import uuid_utils  # noqa: F401
    except Exception:
        pytest.skip("Rust extension uuid_utils not installed in this environment")
    
    monkeypatch.setenv("TYPEID_UUID_BACKEND", value)
    backend = get_uuid_backend()
    assert backend.name == expected


def test_backend_invalid_value(monkeypatch):
    monkeypatch.setenv("TYPEID_UUID_BACKEND", "nope")
    with pytest.raises(RuntimeError):
        get_uuid_backend()
