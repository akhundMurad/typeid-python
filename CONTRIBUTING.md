# Contributing

This page discribes how to contribute to typeid-python.

## Requirements

- Linux, since all development proccess adapted for Linux machines.
- supported Python version (e.g. Python 3.14).

## Installation

1. Fork the [repository](https://github.com/akhundMurad/typeid-python).
2. Clone the forked repository.
3. Install [Poetry Packaging Manager](https://python-poetry.org/):

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

4. Configure virtual environment:

```bash
poetry config virtualenvs.in-project true

poetry install --with dev
```

## Formatters

We are using the following linters:

- black
- mypy
- isort
- ruff

`Makefile` supports a task to run linters:

```bash
make check-linting
```

## How to name branches

It doesn't matter, as long as branch names don't contain anything that violates the Code of Conduct included in the project's repository. As a general rule of thumb, branch names should have a descriptive name, or refer the number of an issue in their name.
