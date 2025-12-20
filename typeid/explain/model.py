"""
Data models for the `typeid explain` feature.

Design goals:
- Additive, non-breaking: does not modify existing TypeID behavior.
- Stable-ish: callers can rely on these dataclasses, but we keep flexibility
  by storing schema/derived sections as dicts (schema evolves without breaking).
- Provenance: every top-level field can be tagged by where it came from.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class Provenance(str, Enum):
    """Where a piece of information came from."""

    DERIVED_FROM_ID = "derived_from_id"
    SCHEMA = "schema"
    EXTERNAL = "external"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ParseError:
    """Represents a recoverable parse/validation error."""

    code: str
    message: str


@dataclass(frozen=True, slots=True)
class ParsedTypeID:
    """
    Facts extracted from the TypeID string without any schema lookup.

    Notes:
    - `prefix` is the full prefix as per TypeID spec (may contain underscores).
    - `suffix` is the encoded UUIDv7 portion (base32 string).
    - `uuid` and `created_at` are *derived* from suffix if possible.
    """

    raw: str
    prefix: Optional[str]
    suffix: Optional[str]

    valid: bool
    errors: List[ParseError] = field(default_factory=list)

    # Derived (best-effort)
    uuid: Optional[str] = None  # keep as string to avoid uuid/uuid6 typing bleed
    created_at: Optional[datetime] = None
    sortable: Optional[bool] = None  # TypeIDs w/ UUIDv7 are typically sortable


@dataclass(frozen=True, slots=True)
class TypeSchema:
    """
    Schema info for a given prefix, loaded from a registry file.

    This is intentionally flexible to keep the schema format evolving without
    breaking the Python API: we store raw dict and also normalize a few
    commonly-used fields for nicer UX.
    """

    prefix: str
    raw: Dict[str, Any] = field(default_factory=dict)

    # Common optional fields (convenience)
    name: Optional[str] = None
    description: Optional[str] = None
    owner_team: Optional[str] = None
    pii: Optional[bool] = None
    retention: Optional[str] = None

    # Link templates (e.g. {"logs": "https://...q={id}"})
    links: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Explanation:
    """
    Final explanation object produced by the explain engine.

    Sections:
    - parsed: always present (even if invalid; fields may be None)
    - schema: may be None if no schema found or schema loading disabled
    - derived: small dict for extra derived facts (extensible)
    - links: rendered links (from schema templates), safe for display
    - provenance: per-field provenance labels for transparency
    """

    id: str
    valid: bool

    parsed: ParsedTypeID
    schema: Optional[TypeSchema] = None

    # Additional derived facts that aren't worth dedicated fields yet
    derived: Dict[str, Any] = field(default_factory=dict)

    # Rendered (not templates) links
    links: Dict[str, str] = field(default_factory=dict)

    # Field -> provenance label; keep keys simple (e.g. "created_at", "retention")
    provenance: Dict[str, Provenance] = field(default_factory=dict)

    # Non-fatal warnings (e.g. schema loaded but link template failed)
    warnings: List[str] = field(default_factory=list)

    # Errors copied from parsed.errors for convenience (and future external errors)
    errors: List[ParseError] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a JSON-serializable dict.

        We avoid serializing complex objects directly (datetime, Enums) without
        conversion to keep `--json` output stable and easy to consume.
        """
        parsed = {
            "raw": self.parsed.raw,
            "prefix": self.parsed.prefix,
            "suffix": self.parsed.suffix,
            "valid": self.parsed.valid,
            "errors": [e.__dict__ for e in self.parsed.errors],
            "uuid": self.parsed.uuid,
            "created_at": self.parsed.created_at.isoformat() if self.parsed.created_at else None,
            "sortable": self.parsed.sortable,
        }

        schema = None
        if self.schema is not None:
            schema = {
                "prefix": self.schema.prefix,
                "name": self.schema.name,
                "description": self.schema.description,
                "owner_team": self.schema.owner_team,
                "pii": self.schema.pii,
                "retention": self.schema.retention,
                "links": dict(self.schema.links),
                "raw": dict(self.schema.raw),
            }

        return {
            "id": self.id,
            "valid": self.valid,
            "parsed": parsed,
            "derived": dict(self.derived),
            "schema": schema,
            "links": dict(self.links),
            "provenance": {k: str(v.value) for k, v in self.provenance.items()},
            "warnings": list(self.warnings),
            "errors": [e.__dict__ for e in self.errors],
        }
