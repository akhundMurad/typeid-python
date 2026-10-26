# Django REST Framework integration

TypeID ships with an **optional Django REST Framework serializer field**.
It validates incoming TypeID strings with the TypeID core and serializes TypeIDs back to strings.

The field:

* accepts a TypeID string or a `TypeID` instance and returns a `TypeID`,
* optionally enforces a fixed prefix,
* serializes `TypeID` values as strings,
* renders UUIDs (for example a `UUIDField` primary key) as `<prefix>_<suffix>` when a prefix is set.

```bash
pip install typeid-python djangorestframework
```

---

## Basic usage

```python notest
from rest_framework import serializers
from typeid.integrations.drf import TypeIDField

class UserSerializer(serializers.Serializer):
    id = TypeIDField(prefix="user")

s = UserSerializer(data={"id": "user_01ke82dtesfn9bjcrzyzz54ya9"})
assert s.is_valid()
s.validated_data["id"]  # TypeID('user_01ke82dtesfn9bjcrzyzz54ya9')
```

A value with a different prefix fails validation:

```python notest
s = UserSerializer(data={"id": "order_01ke82dtesfn9bjcrzyzz54ya9"})
assert not s.is_valid()
# {'id': ["Expected a TypeID with prefix 'user', got 'order'."]}
```

Omit `prefix` to accept TypeIDs with any prefix.

## UUID primary keys

If your model stores a plain UUID, the field exposes it as a TypeID in API responses:

```python notest
class UserSerializer(serializers.ModelSerializer):
    id = TypeIDField(prefix="user", read_only=True)

    class Meta:
        model = User  # id = models.UUIDField(primary_key=True, default=uuid.uuid4)
        fields = ["id", "name"]
```
