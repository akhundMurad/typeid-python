# Pydantic v2 integration

TypeID ships with an **optional Pydantic v2 adapter**.
It lets you use `TypeID` in Pydantic models without pulling Pydantic into the TypeID core.

The adapter:

* validates values using the TypeID core,
* optionally enforces a fixed prefix,
* serializes TypeIDs as strings,
* exposes sensible JSON Schema metadata.

---

## Installation

```bash
pip install typeid-python[pydantic]
```

This installs the latest version of Pydantic v2.

## Basic usage

Use `TypeIDField` with a fixed prefix.

```python
from typing import Literal
from pydantic import BaseModel
from typeid.integrations.pydantic import TypeIDField

class User(BaseModel):
    id: TypeIDField[Literal["user"]]

u = User(id="user_01ke82dtesfn9bjcrzyzz54ya9")
assert str(u.id) == "user_01ke82dtesfn9bjcrzyzz54ya9"
```

## Accepted inputs

You can pass either a string or a `TypeID` instance.

```python
from typing import Literal
from pydantic import BaseModel
from typeid.integrations.pydantic import TypeIDField

class User(BaseModel):
    id: TypeIDField[Literal["user"]]

u = User(id="user_01ke82dtesfn9bjcrzyzz54ya9")
assert u.id is not None
```

```python
from typing import Literal
from pydantic import BaseModel
from typeid import TypeID
from typeid.integrations.pydantic import TypeIDField

class User(BaseModel):
    id: TypeIDField[Literal["user"]]

tid = TypeID.from_str("user_01ke82dtesfn9bjcrzyzz54ya9")
u = User(id=tid)

assert u.id == tid
```

In both cases, `id` is stored as a `TypeID` object inside the model.

## Prefix validation

The prefix in `TypeIDField[...]` is enforced.

```python
import pytest
from typing import Literal
from pydantic import BaseModel, ValidationError
from typeid.integrations.pydantic import TypeIDField

class Order(BaseModel):
    id: TypeIDField[Literal["order"]]

with pytest.raises(ValidationError):
    Order(id="user_01ke82dtesfn9bjcrzyzz54ya9")
```

This fails with a validation error because the prefix does not match.

This is useful when you want the model itself to encode domain meaning
(e.g. *this field must be a user ID, not just any ID*).

## Serialization

When exporting a model, TypeIDs are always serialized as strings.

```python
from typing import Literal
from pydantic import BaseModel
from typeid.integrations.pydantic import TypeIDField

class User(BaseModel):
    id: TypeIDField[Literal["user"]]

u = User(id="user_01ke82dtesfn9bjcrzyzz54ya9")
data = u.model_dump()

assert data == {"id": "user_01ke82dtesfn9bjcrzyzz54ya9"}
```

```python
from typing import Literal
from pydantic import BaseModel
from typeid.integrations.pydantic import TypeIDField

class User(BaseModel):
    id: TypeIDField[Literal["user"]]

u = User(id="user_01ke82dtesfn9bjcrzyzz54ya9")
json_data = u.model_dump_json()

assert json_data == '{"id":"user_01ke82dtesfn9bjcrzyzz54ya9"}'
```

This keeps JSON output simple and predictable.

## JSON Schema / OpenAPI

The generated schema looks roughly like this:

```yaml
id:
  type: string
  format: typeid
  description: TypeID with prefix 'user'
  examples:
    - user_01ke82dtesfn9bjcrzyzz54ya9
```

Notes:

* The schema does not hard-code internal regex details.
* Actual validation is handled by the TypeID core.
* The schema is meant to document intent, not re-implement parsing rules.

## Why `Literal["user"]`?

The recommended form is:

```text
TypeIDField[Literal["user"]]
```

This works cleanly with:

* Ruff
* Pyright / MyPy
* IDE type checkers

Using `Literal` makes the prefix a real compile-time constant and avoids
annotation edge cases.

## FastAPI

FastAPI uses Pydantic v2, so no extra integration is needed.

TypeID fields work automatically in request and response models,
including OpenAPI output, as soon as you use them in a Pydantic model.

## Design notes

* The TypeID core does not import Pydantic.
* All framework-specific code lives in `typeid.integrations.pydantic`.
* Parsing and validation rules live in the core, not in the adapter.

This keeps the integration small and easy to maintain.

*That’s it — no magic, no hidden behavior.*
