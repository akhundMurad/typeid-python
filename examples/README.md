# TypeID Examples

This directory contains **independent, self-contained examples** demonstrating
different ways to use **TypeID in real projects**.

Each example focuses on a specific integration or use case and can be studied
and used on its own.

## `examples/explain/` — `typeid explain` feature

This directory contains **advanced examples** for the `typeid explain` feature.

These examples demonstrate how to:

* inspect TypeIDs (“what is this ID?”)
* enrich IDs using schemas (JSON / YAML)
* batch-process IDs for automation
* safely handle invalid or unknown IDs
* generate machine-readable reports

## `examples/sqlalchemy.py` — SQLAlchemy integration

This example demonstrates how to use **TypeID with SQLAlchemy** in a clean and
database-friendly way.

### Purpose

* Store **native UUIDs** in the database
* Expose **TypeID objects** at the application level
* Enforce prefix correctness automatically
* Keep database schema simple and efficient

This example is **independent** of the `typeid explain` feature.

### What this example shows

* How to implement a custom `TypeDecorator` for TypeID
* How to:

  * bind a `TypeID` to a UUID column
  * reconstruct a `TypeID` on read
* How to ensure:

  * prefixes are validated
  * Alembic autogeneration preserves constructor arguments

### Usage snippet

```python
id = mapped_column(
    TypeIDType("user"),
    primary_key=True,
    default=lambda: TypeID("user")
)
```

Resulting identifiers look like:

```text
user_01h45ytscbebyvny4gc8cr8ma2
```

while the database stores only the UUID value.

## Choosing the right example

| Use case                     | Example                              |
| ---------------------------- | ------------------------------------ |
| Understand `typeid explain`  | `examples/explain/`                  |
| Batch / CI / reporting       | `examples/explain/explain_report.py` |
| SQLAlchemy ORM integration   | `examples/sqlalchemy.py`             |
| UUID-native database storage | `examples/sqlalchemy.py`             |

## Design Principles

All examples in this directory follow these principles:

* ✅ non-breaking
* ✅ production-oriented
* ✅ minimal dependencies
* ✅ explicit and readable
* ✅ safe handling of invalid input

Examples are meant to be **copied, adapted, and extended**.
