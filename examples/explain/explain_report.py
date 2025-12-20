"""
Batch report example:
- Reads TypeIDs from a file (sample_ids.txt)
- Explains each one
- Prints summary stats
- Optionally writes JSON report

Run:
  export TYPEID_SCHEMA=examples/schemas/typeid.schema.json
  python examples/explain_report.py examples/sample_ids.txt --json-out /tmp/report.json
"""

import argparse
import json
from pathlib import Path

from typeid.explain.discovery import discover_schema_path
from typeid.explain.engine import explain as explain_engine
from typeid.explain.registry import load_registry, make_lookup


def _read_ids(path: Path) -> list[str]:
    ids: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        ids.append(line)
    return ids


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="Path to file with TypeIDs (one per line).")
    parser.add_argument("--json-out", type=str, default=None, help="Optional path to write JSON report.")
    args = parser.parse_args()

    ids = _read_ids(Path(args.file))

    # Discover schema (optional)
    discovery = discover_schema_path()
    lookup = None
    schema_info = {"found": False}

    if discovery.path is not None:
        r = load_registry(discovery.path)
        if r.registry is not None:
            lookup = make_lookup(r.registry)
            schema_info = {"found": True, "path": str(discovery.path), "source": discovery.source}
        else:
            schema_info = {"found": False, "error": r.error.message if r.error else "unknown"}

    explanations = []
    valid_count = 0
    schema_hit = 0

    for tid in ids:
        exp = explain_engine(tid, schema_lookup=lookup, enable_schema=True, enable_links=True)
        explanations.append(exp)
        if exp.valid:
            valid_count += 1
        if exp.schema is not None:
            schema_hit += 1

    # Summary
    print("TypeID explain report")
    print("--------------------")
    print(f"IDs processed: {len(ids)}")
    print(f"Valid IDs:     {valid_count}")
    print(f"Schema hits:   {schema_hit}")
    print(f"Schema:        {schema_info}")
    print()

    # Print concise table
    for exp in explanations:
        prefix = exp.parsed.prefix or "-"
        ok = "OK" if exp.valid else "ERR"
        name = exp.schema.name if exp.schema and exp.schema.name else "-"
        print(f"{ok:>3}  {prefix:<16}  {name:<22}  {exp.id}")

    # Optional JSON output
    if args.json_out:
        payload = {
            "summary": {
                "count": len(ids),
                "valid": valid_count,
                "schema_hits": schema_hit,
                "schema": schema_info,
            },
            "items": [e.to_dict() for e in explanations],
        }
        out_path = Path(args.json_out)
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nWrote JSON report to: {out_path}")


if __name__ == "__main__":
    main()
