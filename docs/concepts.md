# Concepts

TypeID exists because identifiers are used for much more than uniqueness.

They appear in logs, URLs, dashboards, tickets, alerts, database rows, and Slack messages.  
Yet most identifiers—especially UUIDs—are opaque. They carry no meaning, no context, and no affordances for inspection.

TypeID is an attempt to fix that, without breaking the properties that make UUIDs useful.

---

## TypeID as an identifier

A TypeID is a string identifier composed of two independent parts:

```text
<prefix>_<suffix>
```

For example:

```text
user_01h45ytscbebyvny4gc8cr8ma2
```

The **suffix** is the identity. It is globally unique and backed by a UUID.
The **prefix** is context. It tells a human (and tooling) what kind of thing the identifier refers to.

Crucially, the prefix does *not* participate in uniqueness. Two TypeIDs with different prefixes but the same suffix represent the same underlying UUID. The prefix is a semantic layer, not a storage primitive.

This separation is intentional. It allows TypeID to add meaning without interfering with existing UUID-based systems.

## UUID compatibility by design

TypeID is not a replacement for UUIDs. It is a layer on top of them.

Every TypeID corresponds to exactly one UUID, and that UUID can always be extracted or reconstructed. This makes it possible to:

* store native UUIDs in databases
* use existing UUID indexes and constraints
* introduce TypeID without schema migrations
* roll back or interoperate with systems that know nothing about TypeID

The recommended pattern is simple: **store UUIDs, expose TypeIDs**.

TypeID lives at the boundaries of your system—APIs, logs, tooling—not at the lowest storage level.

## Sortability and time

The suffix used by TypeID is time-sortable. When two TypeIDs are compared lexicographically, the one created earlier sorts before the one created later.

This property is not about business semantics; it is about ergonomics.

Sortable identifiers make logs readable, pagination predictable, and debugging less frustrating. When you scan a list of IDs, you can usually infer their relative age without additional metadata.

There are important limits to this property. Ordering reflects **generation time**, not transaction time or business events. Clock skew and distributed systems still exist. TypeID does not attempt to impose global ordering or causality.

Sortability is a convenience, not a guarantee.

## Explainability

Once an identifier carries structure, it becomes possible to inspect it.

TypeID can be *explained*: given a string, the system can determine whether it is a valid TypeID, extract its UUID, derive its creation time, and report these facts in a structured way.

This is useful in places where identifiers normally appear as dead text:

* logs
* error messages
* database dumps
* incident reports
* CI output

Explainability is designed to be safe. Invalid identifiers do not crash the system. Unknown prefixes are accepted. Each identifier is handled independently, which makes batch processing robust.

## Schemas as optional meaning

Derived facts are always available, but they are not always enough. In real systems, prefixes often correspond to domain concepts: users, orders, events, aggregates.

Schemas allow you to describe that meaning explicitly.

A schema can say that a `user` ID represents an end-user account, that it contains PII, that it is owned by a particular team, or that related logs and dashboards can be found at specific URLs.

Schemas are optional and additive. If a schema is missing, outdated, or invalid, TypeID still works. The identifier does not become invalid because metadata could not be loaded.

This separation keeps the core identifier system stable while allowing richer interpretation where it is useful.

## Unknown and invalid identifiers

TypeID makes a clear distinction between identifiers that are **invalid** and those that are merely **unknown**.

An invalid identifier is structurally wrong: it cannot be parsed or decoded.
An unknown identifier is structurally valid, but its prefix is not recognized by any schema.

Unknown identifiers are first-class citizens. They allow systems to evolve independently and avoid tight coupling between producers and consumers of IDs.

This distinction is essential for forward compatibility and safe tooling.

## A note on safety

TypeID is deliberately conservative.

It does not infer meaning.
It does not mutate state.
It does not enforce authorization.
It does not treat identifiers as secrets.

Its goal is to make identifiers **more understandable**.

## Closing thoughts

TypeID treats identifiers as part of the system’s interface, not as incidental implementation details.

By combining UUID compatibility, time-based sortability, and structured explainability, it aims to make everyday engineering tasks—debugging, inspection, reasoning—slightly less painful.

Identifiers should not be mysterious. They should be inspectable, understandable, and boring in the best possible way.
