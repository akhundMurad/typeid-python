from typing import Optional

import click
from uuid6 import UUID

from typeid import TypeID, base32, from_uuid, get_prefix_and_suffix


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


if __name__ == "__main__":
    cli()
