"""
Explain subsystem for TypeID.

This package provides a high-level, non-breaking API and CLI support
for answering the question:

    "What is this TypeID?"

It is intentionally:
- additive (no changes to existing TypeID semantics),
- schema-optional (works fully offline),
- safe by default (read-only, no side effects).

Public API:
    explain(id_str, schema_path=None, **options) -> Explanation
"""

from pathlib import Path
from typing import Optional

from .discovery import discover_schema_path
from .engine import explain as _explain_engine
from .model import Explanation
from .registry import load_registry, make_lookup

__all__ = [
    "explain",
    "Explanation",
]


def explain(
    id_str: str,
    *,
    schema_path: Optional[str | Path] = None,
    enable_schema: bool = True,
    enable_links: bool = True,
) -> Explanation:
    """
    High-level convenience API for explaining a TypeID.

    This function:
    - parses and validates the TypeID,
    - discovers and loads schema if enabled,
    - executes the explain engine,
    - never raises on normal user errors.

    Args:
        id_str: TypeID string to explain.
        schema_path: Optional explicit path to schema file.
                     If None, discovery rules are applied.
        enable_schema: Disable schema usage entirely if False.
        enable_links: Disable link rendering if False.

    Returns:
        Explanation object.
    """
    lookup = None

    if enable_schema:
        path = None

        if schema_path is not None:
            path = Path(schema_path).expanduser()
        else:
            discovery = discover_schema_path()
            path = discovery.path

        if path is not None:
            result = load_registry(path)
            if result.registry is not None:
                lookup = make_lookup(result.registry)
            # Note: load errors are intentionally not raised here.
            # They will be surfaced as warnings by the CLI layer if desired.

    return _explain_engine(
        id_str,
        schema_lookup=lookup,
        enable_schema=enable_schema,
        enable_links=enable_links,
    )
