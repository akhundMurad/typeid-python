import os
import uuid as std_uuid
from dataclasses import dataclass
from typing import Callable, Literal, Type


BackendName = Literal["uuid-utils", "uuid6"]


@dataclass(frozen=True)
class UUIDBackend:
    name: BackendName
    uuid7: Callable[[], std_uuid.UUID]
    UUID: Type[std_uuid.UUID]


def _load_uuid_utils() -> UUIDBackend:
    import uuid_utils as uuid  # type: ignore

    return UUIDBackend(name="uuid-utils", uuid7=uuid.uuid7, UUID=uuid.UUID)  # type: ignore


def _load_uuid6() -> UUIDBackend:
    import uuid6  # type: ignore

    return UUIDBackend(name="uuid6", uuid7=uuid6.uuid7, UUID=uuid6.UUID)  # type: ignore


def get_uuid_backend() -> UUIDBackend:
    """
    Select UUIDv7 backend.

    Selection order:
      1) If TYPEID_UUID_BACKEND is set, force that backend (or fail with a clear error).
      2) Otherwise prefer uuid-utils if installed, else fallback to uuid6.

    Allowed values:
      TYPEID_UUID_BACKEND=uuid-utils|uuid6
    """
    forced = os.getenv("TYPEID_UUID_BACKEND")
    if forced:
        forced = forced.strip()
        if forced not in ("uuid-utils", "uuid6"):
            raise RuntimeError(f"Invalid TYPEID_UUID_BACKEND={forced!r}. " "Allowed values: 'uuid-utils' or 'uuid6'.")
        try:
            return _load_uuid_utils() if forced == "uuid-utils" else _load_uuid6()
        except Exception as e:
            raise RuntimeError(
                f"TYPEID_UUID_BACKEND is set to {forced!r}, but that backend "
                "is not available. Install the required dependency."
            ) from e

    # Auto mode
    try:
        return _load_uuid_utils()
    except Exception:
        pass

    try:
        return _load_uuid6()
    except Exception as e:
        raise RuntimeError("No UUIDv7 backend available. Install one of: uuid-utils (recommended) or uuid6.") from e
