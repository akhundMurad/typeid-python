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

- PyPI:

    ```console
    pip install typeid-python
    ```

- Poetry:

    ```console
    poetry add typeid-python
    ```

## Usage

### Basic

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
    from typeid import TypeID

    typeid = TypeID.from_string("user_01h45ytscbebyvny4gc8cr8ma2")

    print(str(typeid))  # "user_01h45ytscbebyvny4gc8cr8ma2"
    ```

- Create TypeID from uuid7:

    ```python
    from typeid import TypeID
    from uuid6 import uuid7

    uuid = uuid7()  # UUID('01890bf0-846f-7762-8605-5a3abb40e0e5')
    prefix = "user"

    typeid = TypeID.from_uuid(prefix=prefix, suffix=uuid)

    print(str(typeid))  # "user_01h45z113fexh8c1at7axm1r75"
    ```

### CLI-tool

- Install dependencies:

    ```console
    pip install typeid-python[cli]
    ```

- To generate a new TypeID, run:

    ```console
    $ python3 -m typeid.cli new -p prefix
    prefix_01h2xcejqtf2nbrexx3vqjhp41
    ```

- To decode an existing TypeID into a UUID run:

    ```console
    $ python3 -m typeid.cli decode prefix_01h2xcejqtf2nbrexx3vqjhp41
    type: prefix
    uuid: 0188bac7-4afa-78aa-bc3b-bd1eef28d881
    ```

- And to encode an existing UUID into a TypeID run:

    ```console
    $ python3 -m typeid.cli encode 0188bac7-4afa-78aa-bc3b-bd1eef28d881 --prefix prefix
    prefix_01h2xcejqtf2nbrexx3vqjhp41
    ```
