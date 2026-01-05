from dataclasses import dataclass
from typing import Any, ClassVar, Generic, Literal, Optional, TypeVar, get_args, get_origin

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
    """
    if isinstance(value, TypeID):
        return value

    if isinstance(value, str):
        return TypeID.from_string(value)

    raise TypeError(f"TypeID must be str or TypeID, got {type(value).__name__}")


@dataclass(frozen=True)
class _TypeIDMeta:
    expected_prefix: Optional[str] = None
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
            if tid.prefix != exp:
                raise ValueError(f"TypeID prefix mismatch: expected '{exp}', got '{tid.prefix}'")

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
                lambda v: str(v),
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

    def __class_getitem__(cls, item: str | tuple[str]) -> type[TypeID]:
        """
        Support:
            - TypeIDField["user"]
            - TypeIDField[Literal["user"]]
            - TypeIDField[("user",)]
        """
        if isinstance(item, tuple):
            if len(item) != 1:
                raise TypeError("TypeIDField[...] expects a single prefix")
            item = item[0]

        # Literal["user"]
        if get_origin(item) is Literal:
            args = get_args(item)
            if len(args) != 1 or not isinstance(args[0], str):
                raise TypeError("TypeIDField[Literal['prefix']] expects a single string literal")
            prefix = args[0]

        # Plain "user"
        elif isinstance(item, str):
            prefix = item

        else:
            raise TypeError("TypeIDField[...] expects a string prefix or Literal['prefix']")

        name = f"TypeIDField_{prefix}"

        # Optionally add a simple example that looks like TypeID format
        # You can improve this to a real example generator if your core has one.
        example = f"{prefix}_01hxxxxxxxxxxxxxxxxxxxxxxx"

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
