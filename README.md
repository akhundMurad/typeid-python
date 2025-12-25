# TypeID Python

<a href="https://github.com/akhundMurad/typeid-python/actions?query=setup%3ACI%2FCD+event%3Apush+branch%3Amain" target="_blank">
    <img src="https://github.com/akhundMurad/typeid-python/actions/workflows/setup.yml/badge.svg?event=push&branch=main" alt="Test">
</a>
<a href="https://pepy.tech/project/typeid-python" target="_blank">
    <img src="https://static.pepy.tech/personalized-badge/typeid-python?period=total&units=international_system&left_color=black&right_color=red&left_text=downloads" alt="Downloads">
</a>
<a href="https://pypi.org/project/typeid-python" target="_blank">
    <img src="https://img.shields.io/pypi/v/typeid-python?color=red&labelColor=black" alt="Package version">
</a>
<a href="https://pypi.org/project/typeid-python" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/typeid-python.svg?color=red&labelColor=black" alt="Supported Python versions">
</a>

## A Python implementation of [TypeIDs](https://github.com/jetpack-io/typeid) using Python

TypeIDs are a modern, **type-safe**, globally unique identifier based on the upcoming
UUIDv7 standard. They provide a ton of nice properties that make them a great choice
as the primary identifiers for your data in a database, APIs, and distributed systems.
Read more about TypeIDs in their [spec](https://github.com/jetpack-io/typeid).

This particular implementation provides an pip package that can be used by any Python project.

## Installation

- Pip:

    ```console
    pip install typeid-python
    ```

- Uv:

    ```console
    uv add typeid-python
    ```

- Poetry:

    ```console
    poetry add typeid-python
    ```

### Optional dependencies

TypeID supports schema-based ID explanations using JSON (always available) and
YAML (optional).

To enable YAML support:

```console
pip install typeid-python[yaml]
```

If the extra is not installed, JSON schemas will still work.

## Usage

### Basic

- Create TypeID Instance:

    ```python
    from typeid import TypeID

    # Default TypeID (no prefix)
    typeid = TypeID()

    assert typeid.prefix == ""
    assert isinstance(typeid.suffix, str)
    assert len(typeid.suffix) > 0  # encoded UUIDv7

    # TypeID with prefix
    typeid = TypeID(prefix="user")

    assert typeid.prefix == "user"
    assert str(typeid).startswith("user_")
    ```

- Create TypeID from string:

    ```python
    from typeid import TypeID

    value = "user_01h45ytscbebyvny4gc8cr8ma2"
    typeid = TypeID.from_string(value)

    assert str(typeid) == value
    assert typeid.prefix == "user"
    ```

- Create TypeID from uuid7:

    ```python
    from typeid import TypeID
    from uuid6 import uuid7

    uuid = uuid7()
    prefix = "user"

    typeid = TypeID.from_uuid(prefix=prefix, suffix=uuid)

    assert typeid.prefix == prefix
    assert str(typeid).startswith(f"{prefix}_")

    ```

- Use pre-defined prefix:

    ```python
    from dataclasses import dataclass, field
    from typing import Literal
    from typeid import TypeID, typeid_factory

    UserID = TypeID[Literal["user"]]
    gen_user_id = typeid_factory("user")


    @dataclass
    class UserDTO:
        user_id: UserID = field(default_factory=gen_user_id)
        full_name: str = "A J"
        age: int = 18


    user = UserDTO()

    assert str(user.user_id).startswith("user_")
    ```

### CLI-tool

- Install dependencies:

    ```console
    pip install typeid-python[cli]
    ```

- To generate a new TypeID, run:

    ```console
    $ typeid new -p prefix
    prefix_01h2xcejqtf2nbrexx3vqjhp41
    ```

- To decode an existing TypeID into a UUID run:

    ```console
    $ typeid decode prefix_01h2xcejqtf2nbrexx3vqjhp41
    type: prefix
    uuid: 0188bac7-4afa-78aa-bc3b-bd1eef28d881
    ```

- And to encode an existing UUID into a TypeID run:

    ```console
    $ typeid encode 0188bac7-4afa-78aa-bc3b-bd1eef28d881 --prefix prefix
    prefix_01h2xcejqtf2nbrexx3vqjhp41
    ```

## ✨ NEW: `typeid explain` — “What is this ID?”

TypeID can now **explain a TypeID** in a human-readable way.

This is useful when:

* debugging logs
* inspecting database records
* reviewing production incidents
* understanding IDs shared via Slack, tickets, or dashboards

### Basic usage (no schema required)

```console
$ typeid explain user_01h45ytscbebyvny4gc8cr8ma2
```

Example output:

```yaml
id: user_01h45ytscbebyvny4gc8cr8ma2
valid: true

parsed:
  prefix: user
  suffix: 01h45ytscbebyvny4gc8cr8ma2
  uuid: 01890bf0-846f-7762-8605-5a3abb40e0e5
  created_at: 2025-03-12T10:41:23Z
  sortable: true

schema:
  found: false
```

Even without configuration, `typeid explain` can:

* validate the ID
* extract the UUID
* derive creation time (UUIDv7)
* determine sortability

## Schema-based explanations

To make explanations richer, you can define a **TypeID schema** describing what each
prefix represents.

### Example schema (`typeid.schema.json`)

```json
{
  "schema_version": 1,
  "types": {
    "user": {
      "name": "User",
      "description": "End-user account",
      "owner_team": "identity-platform",
      "pii": true,
      "retention": "7y",
      "links": {
        "logs": "https://logs.company/search?q={id}",
        "trace": "https://traces.company/?id={id}"
      }
    }
  }
}
```

### Explain using schema

```console
$ typeid explain user_01h45ytscbebyvny4gc8cr8ma2
```

Output (excerpt):

```yaml
schema:
  found: true
  name: User
  owner_team: identity-platform
  pii: true
  retention: 7y

links:
  logs: https://logs.company/search?q=user_01h45ytscbebyvny4gc8cr8ma2
```

## Schema discovery rules

If `--schema` is not provided, TypeID looks for a schema in the following order:

1. Environment variable:

   ```console
   TYPEID_SCHEMA=/path/to/schema.json
   ```
2. Current directory:

   * `typeid.schema.json`
   * `typeid.schema.yaml`
3. User config directory:

   * `~/.config/typeid/schema.json`
   * `~/.config/typeid/schema.yaml`

If no schema is found, the command still works with derived information only.

## YAML schemas (optional)

YAML schemas are supported if the optional dependency is installed:

```console
pip install typeid-python[yaml]
```

Example (`typeid.schema.yaml`):

```yaml
schema_version: 1
types:
  user:
    name: User
    owner_team: identity-platform
    links:
      logs: "https://logs.company/search?q={id}"
```

## JSON output (machine-readable)

```console
$ typeid explain user_01h45ytscbebyvny4gc8cr8ma2 --json
```

Useful for:

* scripts
* CI pipelines
* IDE integrations

## Design principles

* **Non-breaking**: existing APIs and CLI commands remain unchanged
* **Schema-optional**: works fully offline
* **Read-only**: no side effects or external mutations
* **Declarative**: meaning is defined by users, not inferred by the tool

You can think of `typeid explain` as:

> **OpenAPI — but for identifiers instead of HTTP endpoints**

## License

MIT

