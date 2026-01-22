# Framework Integrations

TypeID is designed to be framework-agnostic.
The core package does not depend on any web framework, ORM, or serialization library.

Integrations are provided as **optional** adapters that translate between TypeID and specific ecosystems.
They are installed explicitly and never affect the core unless imported.

---

## Available integrations

### Pydantic (v2)

Native support for using TypeID in Pydantic v2 models.

* Prefix-aware validation
* Accepts `str` and `TypeID`
* Serializes as string
* Clean JSON Schema / OpenAPI output

```bash
pip install typeid-python pydantic
```

See: [Pydantic v2](https://akhundmurad.github.io/typeid-python/integrations/pydantic/) documentation page for details and examples.

### FastAPI (Coming Soon 🚧)

FastAPI builds on Pydantic v2, so TypeID works automatically in:

* request models
* response models
* OpenAPI schemas

No separate FastAPI-specific adapter is required.

### SQLAlchemy (Coming Soon 🚧)

Column types for storing TypeIDs in relational databases.

## Design notes

* The TypeID core never imports framework code
* Validation rules live in the core, not in adapters
* Integrations are thin and easy to replace or extend

This keeps the library stable even as frameworks evolve.

## Adding new integrations

If you want to integrate TypeID with another framework:

* keep the adapter small,
* avoid duplicating validation logic,
* depend on the TypeID core as the single source of truth.

Community integrations are welcome.
