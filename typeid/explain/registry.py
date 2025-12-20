"""
Schema registry loader for `typeid explain`.

This module loads a schema file (JSON by default, YAML optionally) and exposes
a lookup function: prefix -> TypeSchema.

Goals:
- Non-breaking: schema is optional; failures are handled gracefully.
- Minimal dependencies: JSON uses stdlib; YAML support is optional.
- Future-proof: schema versioning with a light validation layer.

Schema shape (v1) - JSON/YAML:
{
  "schema_version": 1,
  "types": {
    "usr": {
      "name": "User",
      "description": "...",
      "owner_team": "...",
      "pii": true,
      "retention": "7y",
      "links": {
        "logs": "https://...q={id}",
        "trace": "https://...?id={id}"
      }
    }
  }
}
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .model import TypeSchema


@dataclass(frozen=True, slots=True)
class RegistryLoadError:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class RegistryLoadResult:
    registry: Optional["SchemaRegistry"]
    error: Optional[RegistryLoadError] = None


class SchemaRegistry:
    """
    In-memory registry of TypeSchema objects loaded from a schema file.

    Lookup is by full TypeID prefix (which may contain underscores).
    """

    def __init__(self, *, schema_version: int, types: Dict[str, TypeSchema], source_path: Path):
        self.schema_version = schema_version
        self._types = types
        self.source_path = source_path

    def get(self, prefix: str) -> Optional[TypeSchema]:
        return self._types.get(prefix)

    def __contains__(self, prefix: str) -> bool:
        return prefix in self._types

    def __len__(self) -> int:
        return len(self._types)


def load_registry(path: Path) -> RegistryLoadResult:
    """
    Load a schema registry from the given path.

    Returns RegistryLoadResult:
      - registry != None on success
      - error != None on failure (never raises for normal user mistakes)
    """
    try:
        data, fmt = _read_schema_file(path)
    except Exception as e:
        return RegistryLoadResult(
            registry=None,
            error=RegistryLoadError(code="read_failed", message=f"Failed to read schema: {e!s}"),
        )

    if not isinstance(data, dict):
        return RegistryLoadResult(
            registry=None,
            error=RegistryLoadError(code="invalid_schema", message="Schema root must be an object/map."),
        )

    schema_version = data.get("schema_version")
    if schema_version is None:
        return RegistryLoadResult(
            registry=None,
            error=RegistryLoadError(code="missing_schema_version", message="Schema missing 'schema_version'."),
        )
    if not isinstance(schema_version, int):
        return RegistryLoadResult(
            registry=None,
            error=RegistryLoadError(code="invalid_schema_version", message="'schema_version' must be an integer."),
        )
    if schema_version != 1:
        return RegistryLoadResult(
            registry=None,
            error=RegistryLoadError(
                code="unsupported_schema_version",
                message=f"Unsupported schema_version={schema_version}. Supported: 1.",
            ),
        )

    types_raw = data.get("types")
    if types_raw is None:
        return RegistryLoadResult(
            registry=None,
            error=RegistryLoadError(code="missing_types", message="Schema missing 'types' map."),
        )
    if not isinstance(types_raw, dict):
        return RegistryLoadResult(
            registry=None,
            error=RegistryLoadError(code="invalid_types", message="'types' must be an object/map."),
        )

    types: Dict[str, TypeSchema] = {}
    for prefix, spec in types_raw.items():
        if not isinstance(prefix, str) or not prefix:
            # skip invalid keys but don't fail entire load
            continue
        if not isinstance(spec, dict):
            # skip invalid type spec entries
            continue
        types[prefix] = _to_type_schema(prefix, spec)

    return RegistryLoadResult(registry=SchemaRegistry(schema_version=schema_version, types=types, source_path=path))


def make_lookup(registry: Optional[SchemaRegistry]):
    """
    Convenience helper to make a schema_lookup callable for engine.explain().

    Example:
        reg = load_registry(path).registry
        lookup = make_lookup(reg)
        explanation = explain(id, schema_lookup=lookup)
    """

    def _lookup(prefix: str) -> Optional[TypeSchema]:
        if registry is None:
            return None
        return registry.get(prefix)

    return _lookup


def _read_schema_file(path: Path) -> Tuple[Dict[str, Any], str]:
    """
    Read schema file and parse it into a dict.

    Returns:
        (data, format) where format is 'json' or 'yaml'

    JSON is always supported.
    YAML is supported only if PyYAML is installed.
    """
    suffix = path.suffix.lower()
    raw = path.read_text(encoding="utf-8")

    if suffix == ".json":
        return json.loads(raw), "json"

    if suffix in (".yaml", ".yml"):
        # Optional dependency
        try:
            import yaml  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "YAML schema requires optional dependency. "
                "Install PyYAML (or `typeid[yaml]` if you provide extras)."
            ) from e
        data = yaml.safe_load(raw)
        return data, "yaml"

    # If extension unknown, try JSON first for convenience.
    try:
        return json.loads(raw), "json"
    except Exception as e:
        raise RuntimeError(
            f"Unsupported schema file extension: {path.suffix!s} (supported: .json, .yaml, .yml)"
        ) from e


def _to_type_schema(prefix: str, spec: Dict[str, Any]) -> TypeSchema:
    """
    Normalize a raw type spec into TypeSchema.

    We keep `raw` for forward-compatibility but also extract a few common fields
    for nicer UX.
    """
    links = spec.get("links") or {}
    if not isinstance(links, dict):
        links = {}

    # Extract common fields safely
    name = spec.get("name")
    description = spec.get("description")
    owner_team = spec.get("owner_team")
    pii = spec.get("pii")
    retention = spec.get("retention")

    return TypeSchema(
        prefix=prefix,
        raw=dict(spec),
        name=name if isinstance(name, str) else None,
        description=description if isinstance(description, str) else None,
        owner_team=owner_team if isinstance(owner_team, str) else None,
        pii=pii if isinstance(pii, bool) else None,
        retention=retention if isinstance(retention, str) else None,
        links={str(k): str(v) for k, v in links.items() if isinstance(k, str) and isinstance(v, str)},
    )
