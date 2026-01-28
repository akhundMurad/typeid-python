from typing import Literal

import pytest
from pydantic import BaseModel, ValidationError

from typeid import TypeID
from typeid.integrations.pydantic import TypeIDField

USER_TYPEID_STR = str(TypeID("user"))
ORDER_TYPEID_STR = str(TypeID("order"))


class M(BaseModel):
    id: TypeIDField[Literal["user"]]


def test_accepts_str():
    m = M(id=USER_TYPEID_STR)
    assert isinstance(m.id, TypeID)


def test_accepts_typeid_instance():
    tid = TypeID.from_string(USER_TYPEID_STR)
    m = M(id=tid)
    assert m.id == tid


def test_prefix_mismatch():
    with pytest.raises(ValidationError):
        M(id=ORDER_TYPEID_STR)


def test_json_serializes_as_string():
    m = M(id=USER_TYPEID_STR)
    data = m.model_dump_json()
    assert '"id":"' in data


def test_json_schema_generation():
    """Test that model_json_schema() works and produces correct schema."""
    schema = M.model_json_schema()

    # Verify the schema structure exists
    assert "properties" in schema
    assert "id" in schema["properties"]

    id_schema = schema["properties"]["id"]

    # Verify it matches the documented expectations
    assert id_schema["type"] == "string"
    assert id_schema["format"] == "typeid"
    assert "user" in id_schema.get("description", "")
    assert "examples" in id_schema


def test_json_schema_with_generate_definitions():
    """
    Test that TypeIDField works with Pydantic's generate_definitions().

    This mimics how FastAPI generates OpenAPI schemas and would catch
    the bug where __get_pydantic_json_schema__ was passing the wrong
    schema to the handler, causing FastAPI's OpenAPI generation to fail.
    """
    from pydantic.json_schema import GenerateJsonSchema

    # Use the same method FastAPI uses internally
    generator = GenerateJsonSchema()
    _, definitions = generator.generate_definitions(
        inputs=[(M, "validation", M.__pydantic_core_schema__)],
    )

    # Verify M is in definitions
    assert "M" in definitions

    # Check the id field schema
    m_schema = definitions["M"]
    assert "properties" in m_schema
    assert "id" in m_schema["properties"]

    id_schema = m_schema["properties"]["id"]

    # Verify TypeID-specific schema properties (same as test_json_schema_generation)
    assert id_schema["type"] == "string"
    assert id_schema["format"] == "typeid"
    assert "user" in id_schema.get("description", "")
    assert "examples" in id_schema
