from dataclasses import dataclass
from functools import lru_cache
from typing import Callable

from .typeid import TypeID


@dataclass(frozen=True, slots=True)
class TypeIDFactory:
    """
    Callable object that generates TypeIDs with a fixed prefix.

    Example:
        user_id = TypeIDFactory("user")()
    """

    prefix: str

    def __call__(self) -> TypeID:
        return TypeID(self.prefix)


def typeid_factory(prefix: str) -> Callable[[], TypeID]:
    """
    Return a zero-argument callable that generates TypeIDs with a fixed prefix.

    Example:
        user_id = typeid_factory("user")()
    """
    return TypeIDFactory(prefix)


@lru_cache(maxsize=256)
def cached_typeid_factory(prefix: str) -> Callable[[], TypeID]:
    """
    Same as typeid_factory, but caches factories by prefix.

    Use this if you create factories repeatedly at runtime.
    """
    return TypeIDFactory(prefix)
