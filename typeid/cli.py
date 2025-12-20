from typing import Optional

import click
from uuid6 import UUID

from typeid import TypeID, base32, from_uuid, get_prefix_and_suffix

from typeid.explain.engine import explain as explain_engine
from typeid.explain.discovery import discover_schema_path
from typeid.explain.formatters import format_explanation_json, format_explanation_pretty
from typeid.explain.registry import load_registry, make_lookup


@click.group()
def cli():
    pass


@cli.command()
@click.option("-p", "--prefix")
def new(prefix: Optional[str] = None) -> None:
    typeid = TypeID(prefix=prefix)
    click.echo(str(typeid))


@cli.command()
@click.argument("uuid")
@click.option("-p", "--prefix")
def encode(uuid: str, prefix: Optional[str] = None) -> None:
    typeid = from_uuid(suffix=UUID(uuid), prefix=prefix)
    click.echo(str(typeid))


@cli.command()
@click.argument("encoded")
def decode(encoded: str) -> None:
    prefix, suffix = get_prefix_and_suffix(encoded)
    decoded_bytes = bytes(base32.decode(suffix))
    uuid = UUID(bytes=decoded_bytes)
    click.echo(f"type: {prefix}")
    click.echo(f"uuid: {uuid}")


@cli.command()
@click.argument("encoded")
@click.option(
    "--schema",
    "schema_path",
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    required=False,
    help="Path to TypeID schema file (JSON, or YAML if PyYAML is installed). "
         "If omitted, TypeID will try to discover a schema automatically.",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output machine-readable JSON.",
)
@click.option(
    "--no-schema",
    is_flag=True,
    help="Disable schema lookup (derived facts only).",
)
@click.option(
    "--no-links",
    is_flag=True,
    help="Disable link template rendering.",
)
def explain(
    encoded: str,
    schema_path: Optional[str],
    as_json: bool,
    no_schema: bool,
    no_links: bool,
) -> None:
    """
    Explain a TypeID: parse/validate it, derive facts (uuid, created_at),
    and optionally enrich explanation from a user-provided schema.
    """
    enable_schema = not no_schema
    enable_links = not no_links

    schema_lookup = None
    warnings: list[str] = []

    # Load schema (optional)
    if enable_schema:
        resolved_path = None

        if schema_path:
            resolved_path = schema_path
        else:
            discovery = discover_schema_path()
            if discovery.path is not None:
                resolved_path = str(discovery.path)
            # If env var was set but invalid, discovery returns source info;
            # we keep CLI robust and simply proceed without schema.

        if resolved_path:
            result = load_registry(click.Path(resolved_path))
            # NOTE: click.Path is not a real filesystem path. Convert to pathlib Path.
            # We'll do it safely:
            from pathlib import Path
            result = load_registry(Path(resolved_path))

            if result.registry is not None:
                schema_lookup = make_lookup(result.registry)
            else:
                if result.error is not None:
                    warnings.append(f"Schema load failed: {result.error.message}")

    # Build explanation (never raises on normal errors)
    exp = explain_engine(
        encoded,
        schema_lookup=schema_lookup,
        enable_schema=enable_schema,
        enable_links=enable_links,
    )

    # Surface schema-load warnings (if any)
    if warnings:
        exp.warnings.extend(warnings)

    # Print
    if as_json:
        click.echo(format_explanation_json(exp))
    else:
        click.echo(format_explanation_pretty(exp))


if __name__ == "__main__":
    cli()
