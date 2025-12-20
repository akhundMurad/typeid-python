"""
Complex example: schema discovery + taxonomy prefixes + robust handling.

Run:
  # (recommended) set schema location so discovery works
  export TYPEID_SCHEMA=examples/schemas/typeid.schema.json

  python examples/explain_complex.py

Optional:
  pip install typeid-python[yaml]
  export TYPEID_SCHEMA=examples/schemas/typeid.schema.yaml
"""

import os
from typing import Iterable

from typeid import TypeID
from typeid.explain.discovery import discover_schema_path
from typeid.explain.registry import load_registry, make_lookup
from typeid.explain.engine import explain as explain_engine
from typeid.explain.formatters import format_explanation_pretty


def _load_schema_lookup():
    discovery = discover_schema_path()
    if discovery.path is None:
        print("No schema discovered. Proceeding without schema.")
        return None

    result = load_registry(discovery.path)
    if result.registry is None:
        print(f"Schema load failed: {result.error.message if result.error else 'unknown error'}")
        return None

    print(f"Schema loaded from: {discovery.path} ({discovery.source})")
    return make_lookup(result.registry)


def _banner(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def _explain_many(ids: Iterable[str], lookup) -> None:
    for tid in ids:
        exp = explain_engine(tid, schema_lookup=lookup, enable_schema=True, enable_links=True)
        print(format_explanation_pretty(exp))


def main() -> None:
    _banner("TypeID explain — complex demo")

    # Use schema discovery (env/cwd/user-config)
    lookup = _load_schema_lookup()

    # Create a bunch of IDs:
    # - standard prefixes
    # - taxonomy prefix (env/region in prefix)
    # - unknown prefix
    # - invalid string
    user_id = str(TypeID(prefix="user"))
    order_id = str(TypeID(prefix="order"))
    evt_id = str(TypeID(prefix="evt_payment"))
    user_live_eu_id = str(TypeID(prefix="user_live_eu"))
    unknown_id = str(TypeID(prefix="something_new"))
    invalid_id = "user_NOT_A_SUFFIX"

    _banner("Explaining generated IDs")
    ids = [user_id, order_id, evt_id, user_live_eu_id, unknown_id, invalid_id]
    _explain_many(ids, lookup)

    _banner("Notes")
    print("- IDs still explain offline (derived facts always present).")
    print("- Schema adds meaning, ownership, policies, and links.")
    print("- Prefix taxonomy works because TypeID prefixes allow underscores.")
    print("- Invalid IDs never crash; they return valid=false and errors.")
    print("- Unknown prefixes still show derived facts, schema found=false.")


if __name__ == "__main__":
    # Helpful hint for users
    if "TYPEID_SCHEMA" not in os.environ:
        print("Tip: set TYPEID_SCHEMA to enable schema discovery, e.g.:")
        print("  export TYPEID_SCHEMA=examples/schemas/typeid.schema.json\n")
    main()
