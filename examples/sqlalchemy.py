from typing import Optional

from sqlalchemy import types
from sqlalchemy.util import generic_repr
from typeid import TypeID


class TypeIDType(types.TypeDecorator):
    """
    A SQLAlchemy TypeDecorator that allows storing TypeIDs in the database.
    The prefix will not be persisted, instead the database-native UUID field will be used.
    At retrieval time a TypeID will be constructed based on the configured prefix and the
    UUID value from the database.

    Usage:
        # will result in TypeIDs such as "user_01h45ytscbebyvny4gc8cr8ma2"
        id = mapped_column(
            TypeIDType("user"),
            primary_key=True,
            default=lambda: TypeID("user")
        )
    """
    impl = types.Uuid

    cache_ok = True

    prefix: Optional[str] = None

    def __init__(self, prefix: Optional[str], *args, **kwargs):
        self.prefix = prefix
        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        # Customize __repr__ to ensure that auto-generated code e.g. from alembic includes
        # the right __init__ params (otherwise by default prefix will be omitted because
        # uuid.__init__ does not have such an argument).
        return generic_repr(
            self,
            to_inspect=TypeID(self.prefix),
        )

    def process_bind_param(self, value: TypeID, dialect):
        if self.prefix is None:
            assert value.prefix is None
        else:
            assert value.prefix == self.prefix

        return value.uuid

    def process_result_value(self, value, dialect):
        return TypeID.from_uuid(value, self.prefix)
