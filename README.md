# TypeID Python

[![PyPI - Version](https://img.shields.io/pypi/v/typeid-python?color=green)](https://pypi.org/project/typeid-python/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/typeid-python?color=green)](https://pypi.org/project/typeid-python/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/typeid-python?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/typeid-python)
![GitHub License](https://img.shields.io/github/license/akhundMurad/typeid-python)

> [!WARNING]
> `main` may contain unreleased changes. For stable usage, use the latest release tag.

A **high-performance Python implementation of [TypeIDs](https://github.com/jetpack-io/typeid)** — type-safe,
sortable identifiers based on **UUIDv7**.

TypeIDs are designed for modern systems where identifiers should be:

- globally unique
- sortable by creation time
- safe to expose externally
- easy to reason about in logs, APIs, and databases

This library provides a Python package with Rust acceleration.

## Key features

- ✅ UUIDv7-based, time-sortable identifiers
- ✅ Schema-based ID explanations (JSON / YAML)
- ✅ Fast generation & parsing (Rust-accelerated)
- ✅ Multiple integrations (Pydantic, FastAPI, ...)
- ✅ Type-safe prefixes (`user_`, `order_`, ...)
- ✅ Human-readable and URL-safe
- ✅ CLI tools (`new`, `encode`, `decode`, `explain`)
- ✅ Fully offline, no external services

## Performance

TypeID is optimized for **real-world performance**, not just correctness.

### Benchmark summary (mean time)

| Operation | Before Rust | Rust + optimizations |
| --------- | ----------- | -------------------- |
| Generate  | 3.47 µs     | **0.70 µs**          |
| Parse     | 2.08 µs     | **1.30 µs**          |
| Workflow  | 5.52 µs     | **2.25 µs**          |

### Highlights

* 🚀 **~5× faster generation**
* ⚡ **~1.6× faster parsing**
* 🔁 **~2.5× faster end-to-end workflows**

Benchmarks are:

* reproducible
* committed as raw JSON
* runnable locally via `bench/`

See [`Docs: Performance`](https://akhundmurad.github.io/typeid-python/performance/) for details.

## Installation

### Core

```console
$ pip install typeid-python
```

Included:

* Rust base32 encode/decode
* `uuid-utils` for fast UUIDv7 generation

### Other optional extras

```console
$ pip install typeid-python[yaml]     # YAML schema support
$ pip install typeid-python[cli]      # CLI tools
$ pip install typeid-python[pydantic] # Pydantic integration
```

Extras are **strictly optional**.

## Usage

### Basic

```python
from typeid import TypeID

tid = TypeID(prefix="user")

assert tid.prefix == "user"
assert isinstance(tid.suffix, str)
assert str(tid).startswith("user_")
```

### From string

```python
from typeid import TypeID

tid = TypeID.from_string("user_01h45ytscbebyvny4gc8cr8ma2")
assert tid.prefix == "user"
```

### From UUIDv7

```python
from typeid import TypeID
from uuid_utils import uuid7

u = uuid7()
tid = TypeID.from_uuid(prefix="user", suffix=u)

assert tid.uuid.version == 7
```

### Typed prefixes

```python
from typing import Literal
from typeid import TypeID, typeid_factory

UserID = TypeID[Literal["user"]]
gen_user_id = typeid_factory("user")

user_id = gen_user_id()
```

## CLI

```console
$ pip install typeid-python[cli]
```

Generate:

```console
$ typeid new -p user
user_01h2xcejqtf2nbrexx3vqjhp41
```

Decode:

```console
$ typeid decode user_01h2xcejqtf2nbrexx3vqjhp41
uuid: 0188bac7-4afa-78aa-bc3b-bd1eef28d881
```

Encode:

```console
$ typeid encode 0188bac7-4afa-78aa-bc3b-bd1eef28d881 --prefix user
```

## Framework integrations

TypeID is **framework-agnostic by design**.
Integrations are provided as optional adapters, installed explicitly and kept separate from the core.

### Available integrations

* **Pydantic (v2)**
  Native field type with validation and JSON Schema support.

  ```bash
  pip install typeid-python[pydantic]
  ```

  ```python
  from typing import Literal
  from pydantic import BaseModel
  from typeid.integrations.pydantic import TypeIDField

  class User(BaseModel):
      id: TypeIDField[Literal["user"]]
  ```

* **FastAPI**
  Works automatically via Pydantic (request/response models, OpenAPI).

  ```bash
  pip install typeid-python[fastapi]
  ```

* **SQLAlchemy**
  Column types for storing TypeIDs (typically as strings).

  ```bash
  pip install typeid-python[sqlalchemy]
  ```

All integrations are **opt-in via extras** and never affect the core package.

## ✨ `typeid explain` — understand any ID

```console
$ typeid explain user_01h45ytscbebyvny4gc8cr8ma2
```

Outputs:

```yaml
parsed:
  prefix: user
  uuid: 01890bf0-846f-7762-8605-5a3abb40e0e5
  created_at: 2025-03-12T10:41:23Z
  sortable: true
```

Works **without schema**, fully offline.

## Schema-based explanations

Define meaning for prefixes using JSON or YAML.

Example (`typeid.schema.json`):

```json
{
  "schema_version": 1,
  "types": {
    "user": {
      "name": "User",
      "owner_team": "identity-platform",
      "pii": true
    }
  }
}
```

Then:

```console
$ typeid explain user_01h45ytscbebyvny4gc8cr8ma2
```

Read more here: ["Docs: Explain"](https://akhundmurad.github.io/typeid-python/performance/).

## Design principles

* **Non-breaking**: stable APIs
* **Lazy evaluation**: work is done only when needed
* **Explainability**: identifiers carry meaning
* **Transparency**: performance claims are backed by data

> Think of TypeID as
> **UUIDs + semantics + observability — without sacrificing speed**

## License

MIT
