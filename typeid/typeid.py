from typing import Optional


class TypeID:
    def __init__(self, suffix: str, prefix: Optional[str] = None) -> None:
        self._suffix = suffix
        self._prefix = prefix
