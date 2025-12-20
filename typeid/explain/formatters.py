"""
Formatting helpers for `typeid explain`.

This module is intentionally small and dependency-free.
It supports:
- YAML-ish pretty output (human-friendly)
- JSON output via Explanation.to_dict() (machine-friendly)

It also provides a minimal "safe formatter" for link templates
(kept here so CLI and engine can share behavior if needed).

Note: This file does NOT require PyYAML. We output YAML-like text
without claiming it's strict YAML.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional

from .model import Explanation, Provenance


def format_explanation_pretty(exp: Explanation) -> str:
    """
    Render an Explanation as readable YAML-ish text.

    We intentionally keep it stable-ish and human-friendly:
    - predictable section ordering
    - indentation
    - lists rendered as "- item"

    This is NOT guaranteed to be strict YAML; it is "YAML-like".
    For strict machine consumption, use JSON output.
    """
    lines: List[str] = []

    def add(line: str = "") -> None:
        lines.append(line)

    add(f"id: {exp.id}")
    add(f"valid: {str(exp.valid).lower()}")

    if exp.errors:
        add("errors:")
        for e in exp.errors:
            add(f"  - code: {e.code}")
            add(f"    message: {_quote_if_needed(e.message)}")

    add()
    add("parsed:")
    _emit_kv(lines, "  ", "prefix", exp.parsed.prefix)
    _emit_kv(lines, "  ", "suffix", exp.parsed.suffix)
    _emit_kv(lines, "  ", "uuid", exp.parsed.uuid)
    _emit_kv(lines, "  ", "created_at", _iso(exp.parsed.created_at))
    _emit_kv(lines, "  ", "sortable", exp.parsed.sortable)

    # Schema section
    add()
    add("schema:")
    if exp.schema is None:
        add("  found: false")
    else:
        add("  found: true")
        _emit_kv(lines, "  ", "prefix", exp.schema.prefix)
        _emit_kv(lines, "  ", "name", exp.schema.name)
        _emit_kv(lines, "  ", "description", exp.schema.description)
        _emit_kv(lines, "  ", "owner_team", exp.schema.owner_team)
        _emit_kv(lines, "  ", "pii", exp.schema.pii)
        _emit_kv(lines, "  ", "retention", exp.schema.retention)

        # Show extra raw keys (optional, but helpful)
        extra = _schema_extras(exp.schema.raw)
        if extra:
            add("  extra:")
            for k in sorted(extra.keys()):
                _emit_any(lines, "    ", k, extra[k])

    # Derived
    if exp.derived:
        add()
        add("derived:")
        for k in sorted(exp.derived.keys()):
            _emit_any(lines, "  ", k, exp.derived[k])

    # Links
    add()
    add("links:")
    if not exp.links:
        add("  {}")
    else:
        for k in sorted(exp.links.keys()):
            _emit_kv(lines, "  ", k, exp.links[k])

    # Provenance
    if exp.provenance:
        add()
        add("provenance:")
        for k in sorted(exp.provenance.keys()):
            prov = exp.provenance[k]
            add(f"  {k}: {prov.value if isinstance(prov, Provenance) else str(prov)}")

    # Warnings
    if exp.warnings:
        add()
        add("warnings:")
        for w in exp.warnings:
            add(f"  - {_quote_if_needed(w)}")

    return "\n".join(lines).rstrip() + "\n"


def format_explanation_json(exp: Explanation, *, indent: int = 2) -> str:
    """
    Render Explanation as JSON string.
    """
    return json.dumps(exp.to_dict(), indent=indent, ensure_ascii=False) + "\n"


class SafeFormatDict(dict):
    """dict that leaves unknown placeholders intact rather than raising KeyError."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def render_template(template: str, mapping: Mapping[str, Any]) -> str:
    """
    Render a template using str.format_map with SafeFormatDict.

    Unknown placeholders remain unchanged.
    """
    safe = SafeFormatDict({k: _stringify(v) for k, v in mapping.items()})
    return template.format_map(safe)


def _iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None


def _emit_kv(lines: List[str], indent: str, key: str, value: Any) -> None:
    if value is None:
        lines.append(f"{indent}{key}: null")
        return
    if isinstance(value, bool):
        lines.append(f"{indent}{key}: {str(value).lower()}")
        return
    if isinstance(value, (int, float)):
        lines.append(f"{indent}{key}: {value}")
        return
    lines.append(f"{indent}{key}: {_quote_if_needed(str(value))}")


def _emit_any(lines: List[str], indent: str, key: str, value: Any) -> None:
    """
    Emit arbitrary JSON-y values in YAML-ish style.
    """
    if value is None or isinstance(value, (str, bool, int, float)):
        _emit_kv(lines, indent, key, value)
        return

    if isinstance(value, list):
        lines.append(f"{indent}{key}:")
        if not value:
            lines.append(f"{indent}  []")
            return
        for item in value:
            if isinstance(item, (str, int, float, bool)) or item is None:
                lines.append(f"{indent}  - {_quote_if_needed(_stringify(item))}")
            else:
                # nested complex item: render as JSON inline
                lines.append(f"{indent}  - {_quote_if_needed(json.dumps(item, ensure_ascii=False))}")
        return

    if isinstance(value, dict):
        lines.append(f"{indent}{key}:")
        if not value:
            lines.append(f"{indent}  {{}}")
            return
        for k in sorted(value.keys(), key=lambda x: str(x)):
            _emit_any(lines, indent + "  ", str(k), value[k])
        return

    # Fallback: stringify
    _emit_kv(lines, indent, key, _stringify(value))


def _stringify(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return str(v).lower()
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, datetime):
        return v.isoformat()
    return str(v)


def _quote_if_needed(s: str) -> str:
    """
    Add quotes if the string contains characters that could confuse YAML-ish output.
    """
    if s == "":
        return '""'
    # Minimal quoting rules for readability; not strict YAML.
    needs = any(ch in s for ch in [":", "#", "{", "}", "[", "]", ",", "\n", "\r", "\t"])
    if s.strip() != s:
        needs = True
    if s.lower() in {"true", "false", "null", "none"}:
        needs = True
    if needs:
        escaped = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return s


def _schema_extras(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return schema keys excluding the ones we already print as normalized fields.
    """
    exclude = {
        "name",
        "description",
        "owner_team",
        "pii",
        "retention",
        "links",
    }
    return {k: v for k, v in raw.items() if k not in exclude}
