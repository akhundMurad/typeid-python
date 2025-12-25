# Quickstart

This page walks through the core workflow of TypeID: generating identifiers, inspecting them, and understanding how they fit into a real system.

It is intentionally short. The goal is to get you productive quickly, not to explain every detail.

---

## Installation

Install the package using your preferred tool.

With pip:

```bash
pip install typeid-python
```

With uv:

```bash
uv add typeid-python
```

If you plan to use YAML schemas later, install the optional extra:

```bash
pip install "typeid-python[yaml]"
```

JSON schemas work without any extras.

## Creating a TypeID

A TypeID is created by providing a prefix that describes what the identifier represents.

```python
from typeid import TypeID

tid = TypeID("user")

value = str(tid)

assert value.startswith("user_")
assert len(value.split("_", 1)[1]) > 0
```

This produces a string similar to:

```text
user_01h45ytscbebyvny4gc8cr8ma2
```

The prefix is meaningful to humans.
The suffix is globally unique and time-sortable.

Prefixes are optional. If you omit it, you get a prefix-less identifier:

```python
from typeid import TypeID

tid = TypeID(None)

assert not tid.prefix
```

This can be useful when the type is implied by context or stored elsewhere.

## Pre-defined prefixes

Sometimes it's useful to have pre-defined prefix.

```python
from dataclasses import dataclass, field
from typing import Literal
from typeid import TypeID, typeid_factory

UserID = TypeID[Literal["user"]]
gen_user_id = typeid_factory("user")


@dataclass()
class UserDTO:
    user_id: UserID = field(default_factory=gen_user_id)
    full_name: str = "A J"
    age: int = 18


user = UserDTO()
assert str(user.user_id).startswith("user_")
```

## Parsing and validation

TypeIDs can be parsed back from strings.

```python
from typeid import TypeID

prefix = "user"
suffix = "01h45ytscbebyvny4gc8cr8ma2"
tid = TypeID.from_string(f"{prefix}_{suffix}")

assert tid.prefix == "user" and tid.suffix == suffix
```

If the string is invalid, parsing fails explicitly. Invalid identifiers are never silently accepted.

When dealing with untrusted input, you will usually want to rely on the `explain` functionality instead of raising exceptions. This is covered later.

## UUID compatibility

Every TypeID is backed by a UUID.

You can always extract the UUID:

```text
tid.uuid
```

And you can always reconstruct a TypeID from a UUID:

```python
from uuid6 import uuid7
from typeid import TypeID

u = uuid7()
tid = TypeID.from_uuid(suffix=u, prefix="user")
assert str(tid).startswith("user_")
```

This is the intended storage model:

> **Store UUIDs in the database.
> Expose TypeIDs at the application boundary.**

You get the benefits of UUIDs at rest and the benefits of TypeIDs everywhere else.

## Using the CLI

TypeID also ships with a command-line interface.

If you installed the CLI extra:

```bash
pip install "typeid-python[cli]"
```

You can generate identifiers directly:

```bash
typeid new -p user
```

You can inspect existing identifiers:

```bash
typeid decode user_01h45ytscbebyvny4gc8cr8ma2
```

And you can convert between UUIDs and TypeIDs:

```bash
typeid encode <uuid> --prefix user
```

## Explaining an identifier

The most distinctive feature of this implementation is the ability to explain identifiers.

```bash
typeid explain user_01h45ytscbebyvny4gc8cr8ma2
```

This command inspects the identifier and reports:

* whether it is valid
* what prefix it uses
* which UUID it represents
* when it was created

This works even without any configuration and never crashes on invalid input.

## What to read next

If you want to understand *why* TypeID works the way it does, read **Concepts**.

If you want to understand *what explain can do*, read **Explain**.

If you want integration details or API reference material, those sections are available as well.

At this point, you already know enough to start using TypeID in a real project.
