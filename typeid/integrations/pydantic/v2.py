from dataclasses import dataclass
from typing import Any, ClassVar, Generic, Optional, TypeVar, overload

from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue

from typeid import TypeID


T = TypeVar("T")


def _parse_typeid(value: Any) -> TypeID:
    """
    Convert input into a TypeID instance.

    Supports:
    - TypeID -> TypeID
    - str   -> parse into TypeID

    Tries common parsing APIs to avoid coupling to one exact core method.
    If none match, update this function to call your canonical parser.
    """
    if isinstance(value, TypeID):
        return value

    if isinstance(value, str):
        # Try the common names
        for name in ("from_str", "from_string", "parse"):
            fn = getattr(TypeID, name, None)
            if callable(fn):
                return fn(value)  # type: ignore[misc]
        # Fallback: constructor accepts string
        try:
            return TypeID(value)  # type: ignore[call-arg]
        except Exception as e:
            raise TypeError(
                "TypeID Pydantic integration couldn't parse a string. "
                "Please implement TypeID.from_str(s: str) (or .parse/.from_string), "
                "or make TypeID(s: str) work. Original error: "
                f"{e!r}"
            ) from e

    raise TypeError(f"TypeID must be str or TypeID, got {type(value).__name__}")


def _get_prefix(tid: TypeID) -> Optional[str]:
    """
    Extract prefix from TypeID. Adjust this if your core uses a different attribute.
    """
    # Common: tid.prefix
    pref = getattr(tid, "prefix", None)
    if isinstance(pref, str):
        return pref
    return None


def _to_str(tid: TypeID) -> str:
    """
    Convert TypeID to its canonical string representation.
    """
    # Prefer a dedicated method if you have one
    for name in ("to_string", "__str__"):
        fn = getattr(tid, name, None)
        if callable(fn):
            try:
                return fn() if name == "to_string" else str(tid)
            except Exception:
                pass
    return str(tid)


@dataclass(frozen=True)
class _TypeIDMeta:
    expected_prefix: Optional[str] = None
    # Optional: if you have a known regex for full string form, set it for JSON schema
    # pattern: Optional[str] = None
    pattern: Optional[str] = None
    example: Optional[str] = None


class _TypeIDFieldBase:
    """
    Base class implementing Pydantic v2 hooks.
    Subclasses specify _typeid_meta.
    """

    _typeid_meta: ClassVar[_TypeIDMeta] = _TypeIDMeta()

    @classmethod
    def _validate(cls, v: Any) -> TypeID:
        tid = _parse_typeid(v)

        exp = cls._typeid_meta.expected_prefix
        if exp is not None:
            got = _get_prefix(tid)
            if got != exp:
                raise ValueError(f"TypeID prefix mismatch: expected '{exp}', got '{got}'")

        return tid

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:
        """
        Build a schema that:
        - accepts TypeID instances
        - accepts strings and validates/parses them
        - serializes to string in JSON
        """
        # Accept either already-parsed TypeID, or a string (or any -> we validate)
        # Using a plain validator keeps it simple and fast.
        return core_schema.no_info_plain_validator_function(
            cls._validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda v: _to_str(v),
                when_used="json",
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema_: core_schema.CoreSchema, handler: Any) -> JsonSchemaValue:
        schema = handler(core_schema_)

        # Ensure JSON schema is "string"
        schema.update(
            {
                "type": "string",
                "format": "typeid",
            }
        )

        # Add prefix hint in schema
        exp = cls._typeid_meta.expected_prefix
        if exp is not None:
            schema.setdefault("description", f"TypeID with prefix '{exp}'")

        # Optional pattern / example
        if cls._typeid_meta.pattern:
            schema["pattern"] = cls._typeid_meta.pattern
        if cls._typeid_meta.example:
            schema.setdefault("examples", [cls._typeid_meta.example])

        return schema


class TypeIDField(Generic[T]):
    """
    Usage:

        from typeid.integrations.pydantic import TypeIDField

        class User(BaseModel):
            id: TypeIDField["user"]

    This returns a specialized *type* that Pydantic will validate into your core TypeID.
    """

    @overload
    def __class_getitem__(cls, prefix: str) -> type[TypeID]: ...
    @overload
    def __class_getitem__(cls, prefix: tuple[str]) -> type[TypeID]: ...

    def __class_getitem__(cls, item: Any) -> type[TypeID]:
        # Support TypeIDField["user"] or TypeIDField[("user",)]
        if isinstance(item, tuple):
            if len(item) != 1 or not isinstance(item[0], str):
                raise TypeError("TypeIDField[...] expects a single string prefix, e.g. TypeIDField['user']")
            prefix = item[0]
        else:
            if not isinstance(item, str):
                raise TypeError("TypeIDField[...] expects a string prefix, e.g. TypeIDField['user']")
            prefix = item

        name = f"TypeIDField_{prefix}"

        # Optionally add a simple example that looks like TypeID format
        # You can improve this to a real example generator if your core has one.
        example = f"{prefix}_01hxxxxxxxxxxxxxxxxxxxxxxxxx"

        # Create a new subclass of _TypeIDFieldBase with fixed meta
        field_cls = type(
            name,
            (_TypeIDFieldBase,),
            {
                "_typeid_meta": _TypeIDMeta(
                    expected_prefix=prefix,
                    # If you know your precise regex, put it here:
                    # pattern=rf"^{prefix}_[0-9a-z]{{26}}$",
                    pattern=None,
                    example=example,
                )
            },
        )

        # IMPORTANT:
        # We return `field_cls` as the annotation type, but the runtime validated value is your core TypeID.
        return field_cls  # type: ignore[return-value]
