# Explain

The `explain` feature exists because identifiers rarely live in isolation.

They appear in logs, stack traces, database rows, monitoring dashboards, tickets, and CI output. When something goes wrong, engineers are often faced with a string that looks like an identifier and the implicit question:

> “What is this ID?”

In most systems, that question cannot be answered without code, database access, or tribal knowledge. `typeid explain` is an attempt to make identifiers themselves carry enough structure to answer that question directly.

---

## What “explain” means

To explain a TypeID means to inspect it and produce **structured information** about it.

This includes:
- whether the identifier is structurally valid
- what prefix it uses
- which UUID it represents
- when it was created
- whether it is sortable

These facts are derived purely from the identifier itself. They require no configuration, no network access, and no external state.

This is the baseline: explanation always works, even offline.

## Derived facts

Every explanation starts with derived facts.

Given a string, the system attempts to parse it as a TypeID. If parsing succeeds, the result includes:
- the parsed prefix (or absence of one)
- the underlying UUID
- the approximate creation time
- sortability guarantees

If parsing fails, the explanation still succeeds — it simply reports that the identifier is invalid and why.

This distinction is important. `explain` is not a validator that throws errors; it is an inspection tool that always returns an answer.

## Invalid vs unknown

An invalid identifier is one that cannot be parsed at all. Its structure is wrong, its encoding is broken, or it does not conform to the TypeID format.

An unknown identifier, on the other hand, may be perfectly valid but use a prefix that the system does not recognize.

`explain` treats these cases very differently.

Invalid identifiers are reported as invalid.  
Unknown identifiers are reported as valid, but unrecognized.

This distinction allows systems to evolve independently. Producers of IDs can introduce new prefixes without breaking consumers, and tooling can remain forward-compatible.

## Schemas as optional meaning

Derived facts answer questions about structure and origin, but they do not answer questions about *semantics*.

What does a `user` ID represent?  
Does it contain PII?  
Which team owns it?  
Where should an engineer look next?

Schemas exist to answer these questions.

```yaml
schema_version: 1
types:
  user:
    name: User
    description: End-user account
    owner_team: identity-platform
    pii: true
    retention: 7y
    services: [user-service, auth-service]
    storage:
      primary:
        kind: postgres
        table: users
        shard_by: tenant_id
    events: [user.created, user.updated, user.deleted]
    policies:
      delete:
        allowed: false
        reason: GDPR retention policy
    links:
      docs: "https://docs.company/entities/user"
      logs: "https://logs.company/search?q={id}"
      trace: "https://traces.company/?q={id}"
      admin: "https://admin.company/users/{id}"
```

A schema is a declarative description of what a prefix means. It can attach human-readable descriptions, ownership information, retention rules, links to logs or dashboards, and other metadata that helps people reason about identifiers in context.

Schemas are explicitly optional. They are not required for explanation, and they never affect structural validity.

If a schema is present and valid, `explain` enriches the output.  
If a schema is missing, outdated, or invalid, explanation still works using derived facts only.

## Schema discovery

To make schemas practical, `explain` supports discovery.

Rather than requiring every invocation to specify a schema path explicitly, the system looks for schemas in well-defined locations, such as environment variables, the current working directory, or a user-level configuration directory.

This allows schemas to be shared across tools, CI jobs, and developer machines without tight coupling.

Discovery failure is not an error. It is simply reported as “schema not found”.

## Links and affordances

One of the most practical uses of schemas is attaching links.

A schema can define URL templates for logs, traces, admin tools, dashboards, or documentation. During explanation, these templates are expanded using the identifier being explained.

This turns an identifier into a navigational object: from an ID, you can jump directly to relevant systems without knowing how URLs are constructed.

This is especially useful during incident response and debugging, where speed and clarity matter.

## Batch explanation

Explanation is designed to scale beyond single identifiers.

Batch explanation allows many IDs to be processed independently. One invalid identifier does not affect others. Partial results are always produced.

This makes `explain` suitable for:
- CI checks
- offline analysis
- reporting
- log and data pipeline inspection

Machine-readable output formats make it easy to integrate with other tooling.

## Safety and non-goals

The `explain` feature is intentionally conservative.

It does not:
- mutate data
- enforce policy
- make authorization decisions
- infer meaning beyond what is explicitly declared

Schemas describe intent; they do not impose it.

Identifiers remain identifiers. `explain` helps humans and tools understand them, nothing more.

## Mental model

A useful way to think about `typeid explain` is:

> **OpenAPI, but for identifiers instead of HTTP endpoints**

It provides a shared, inspectable contract for something that is otherwise opaque and informal.

## Closing

Identifiers are part of a system’s interface, whether we acknowledge it or not.

By making identifiers inspectable and explainable, TypeID aims to reduce friction in debugging, improve communication across teams, and make systems slightly easier to reason about — without sacrificing compatibility or safety.
