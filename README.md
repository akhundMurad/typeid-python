# TypeID Python

## A Python implementation of [TypeIDs](https://github.com/jetpack-io/typeid) using Python

TypeIDs are a modern, **type-safe**, globally unique identifier based on the upcoming
UUIDv7 standard. They provide a ton of nice properties that make them a great choice
as the primary identifiers for your data in a database, APIs, and distributed systems.
Read more about TypeIDs in their [spec](https://github.com/jetpack-io/typeid).

This particular implementation provides an pip package that can be used by any Python project.

## Installation

- PyPI:

    ```bash
    pip install typeid-python
    ```

- Poetry:

    ```bash
    poetry add typeid-python
    ```

## Usage

- Create TypeID Instance:

    ```python
    from typeid import TypeID

    typeid = TypeID()

    print(typeid.prefix)  # ""
    print(typeid.suffix)  # "01h45ytscbebyvny4gc8cr8ma2" (encoded uuid7 instance)

    typeid = TypeID(prefix="user")

    print(typeid.prefix)  # "user"
    print(str(typeid))  # "user_01h45ytscbebyvny4gc8cr8ma2"
    ```

- Create TypeID from string:

    ```python
    from typeid import from_string

    typeid = from_string("user_01h45ytscbebyvny4gc8cr8ma2")

    print(str(typeid))  # "user_01h45ytscbebyvny4gc8cr8ma2"
    ```

- Create TypeID from uuid7:

    ```python
    from typeid import from_uuid
    from uuid6 import uuid7

    uuid = uuid7()  # UUID('01890bf0-846f-7762-8605-5a3abb40e0e5')
    prefix = "user"

    typeid = from_uuid(prefix=prefix, suffix=uuid)

    print(str(typeid))  # "user_01h45z113fexh8c1at7axm1r75"
    ```
