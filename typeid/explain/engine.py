"""
Explain engine for the `typeid explain` feature.

This module is intentionally:
- Additive (doesn't change existing TypeID behavior)
- Defensive (never crashes on normal user input)
- Dependency-light (stdlib only)

It builds an Explanation by combining:
1) parsed + derived facts from the ID (always available if parsable)
2) optional schema (registry) data looked up by prefix
3) optional rendered links (from schema templates)
"""

from dataclasses import replace
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from typeid import TypeID
from typeid.errors import TypeIDException

from .model import Explanation, ParsedTypeID, ParseError, Provenance, TypeSchema

SchemaLookup = Callable[[str], Optional[TypeSchema]]


def explain(
    id_str: str,
    *,
    schema_lookup: Optional[SchemaLookup] = None,
    enable_schema: bool = True,
    enable_links: bool = True,
) -> Explanation:
    """
    Produce an Explanation for a TypeID string.

    Args:
        id_str: The TypeID string to explain.
        schema_lookup: Optional callable to fetch TypeSchema by prefix.
                      If provided and enable_schema=True, we will look up schema.
        enable_schema: If False, do not attempt schema lookup (offline mode).
        enable_links: If True, render link templates from schema (if any).

    Returns:
        Explanation (always returned; valid=False if parse/validation fails).
    """
    parsed = _parse_typeid(id_str)

    # Start building explanation; keep it useful even if invalid.
    exp = Explanation(
        id=id_str,
        valid=parsed.valid,
        parsed=parsed,
        schema=None,
        derived={},
        links={},
        provenance={},
        warnings=[],
        errors=list(parsed.errors),
    )

    # If parse failed, nothing more we can deterministically derive.
    if not parsed.valid or parsed.prefix is None or parsed.suffix is None:
        return exp

    # Schema lookup (optional)
    schema: Optional[TypeSchema] = None
    if enable_schema and schema_lookup is not None and parsed.prefix:
        try:
            schema = schema_lookup(parsed.prefix)
        except Exception as e:  # never let schema backend break explain
            exp.warnings.append(f"Schema lookup failed: {e!s}")
            schema = None

    if schema is not None:
        exp = replace(exp, schema=schema)
        _apply_schema_provenance(exp)

    # Render links (optional)
    if enable_links and schema is not None and schema.links:
        rendered, warnings = _render_links(schema.links, exp)
        exp.links.update(rendered)
        exp.warnings.extend(warnings)
        for k in rendered.keys():
            exp.provenance.setdefault(f"links.{k}", Provenance.SCHEMA)

    # Derived facts provenance
    _apply_derived_provenance(exp)

    return exp


def _parse_typeid(id_str: str) -> ParsedTypeID:
    """
    Parse and validate a TypeID using the library's existing logic.

    Implementation detail:
    - We rely on TypeID.from_string() to ensure behavior matches existing users.
    - On error, we still attempt to extract prefix/suffix best-effort to show
      something helpful (without promising correctness).
    """
    try:
        tid = TypeID.from_string(id_str)
    except TypeIDException as e:
        # Best-effort split so users can see what's wrong.
        prefix, suffix = _best_effort_split(id_str)
        return ParsedTypeID(
            raw=id_str,
            prefix=prefix,
            suffix=suffix,
            valid=False,
            errors=[ParseError(code="invalid_typeid", message=str(e))],
            uuid=None,
            created_at=None,
            sortable=None,
        )
    except Exception as e:
        prefix, suffix = _best_effort_split(id_str)
        return ParsedTypeID(
            raw=id_str,
            prefix=prefix,
            suffix=suffix,
            valid=False,
            errors=[ParseError(code="parse_error", message=f"Unexpected error: {e!s}")],
            uuid=None,
            created_at=None,
            sortable=None,
        )

    # Derived facts from the validated TypeID
    uuid_obj = tid.uuid  # library returns a UUID object (uuid6.UUID)
    uuid_str = str(uuid_obj)

    created_at = _uuid7_created_at(uuid_obj)
    sortable = True  # UUIDv7 is time-ordered by design

    return ParsedTypeID(
        raw=id_str,
        prefix=tid.prefix,
        suffix=tid.suffix,
        valid=True,
        errors=[],
        uuid=uuid_str,
        created_at=created_at,
        sortable=sortable,
    )


def _best_effort_split(id_str: str) -> tuple[Optional[str], Optional[str]]:
    """
    Split by the last underscore (TypeID allows underscores in prefix).
    Returns (prefix, suffix) or (None, None) if not splittable.
    """
    if "_" not in id_str:
        return None, None
    prefix, suffix = id_str.rsplit("_", 1)
    if not prefix or not suffix:
        return None, None
    return prefix, suffix


def _uuid7_created_at(uuid_obj: Any) -> Optional[datetime]:
    """
    Extract created_at from a UUIDv7.

    UUIDv7 layout: the top 48 bits are unix epoch time in milliseconds.
    Python's uuid.UUID.int is a 128-bit integer with the most significant bits first,
    so unix_ms = int >> 80 (128-48).

    Returns:
        UTC datetime or None if extraction fails.
    """
    try:
        # uuid_obj is likely uuid6.UUID, but supports .int like uuid.UUID
        u_int = int(uuid_obj.int)
        unix_ms = u_int >> 80
        unix_s = unix_ms / 1000.0
        return datetime.fromtimestamp(unix_s, tz=timezone.utc)
    except Exception:
        return None


class _SafeFormatDict(dict):
    """dict that leaves unknown placeholders intact instead of raising KeyError."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def _render_links(templates: Dict[str, str], exp: Explanation) -> tuple[Dict[str, str], list[str]]:
    """
    Render schema link templates using known values.

    Supported placeholders:
      {id}, {prefix}, {suffix}, {uuid}
      {created_at} (ISO8601 if available)

    Unknown placeholders remain unchanged.
    """
    mapping = _SafeFormatDict(
        id=exp.id,
        prefix=exp.parsed.prefix or "",
        suffix=exp.parsed.suffix or "",
        uuid=exp.parsed.uuid or "",
        created_at=exp.parsed.created_at.isoformat() if exp.parsed.created_at else "",
    )

    rendered: Dict[str, str] = {}
    warnings: list[str] = []

    for name, tmpl in templates.items():
        if not isinstance(tmpl, str):
            warnings.append(f"Link template '{name}' is not a string; skipping.")
            continue
        try:
            rendered[name] = tmpl.format_map(mapping)
        except Exception as e:
            warnings.append(f"Failed to render link '{name}': {e!s}")

    return rendered, warnings


def _apply_schema_provenance(exp: Explanation) -> None:
    """
    Mark common schema fields as coming from schema.
    (We keep this small; schema.raw stays schema by definition.)
    """
    if exp.schema is None:
        return

    for key in ("name", "description", "owner_team", "pii", "retention"):
        if getattr(exp.schema, key, None) is not None:
            exp.provenance.setdefault(key, Provenance.SCHEMA)


def _apply_derived_provenance(exp: Explanation) -> None:
    """Mark parsed-derived fields as coming from the ID itself."""
    if exp.parsed.prefix is not None:
        exp.provenance.setdefault("prefix", Provenance.DERIVED_FROM_ID)
    if exp.parsed.suffix is not None:
        exp.provenance.setdefault("suffix", Provenance.DERIVED_FROM_ID)
    if exp.parsed.uuid is not None:
        exp.provenance.setdefault("uuid", Provenance.DERIVED_FROM_ID)
    if exp.parsed.created_at is not None:
        exp.provenance.setdefault("created_at", Provenance.DERIVED_FROM_ID)
    if exp.parsed.sortable is not None:
        exp.provenance.setdefault("sortable", Provenance.DERIVED_FROM_ID)
