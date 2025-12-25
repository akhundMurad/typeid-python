# Contributing

This document describes how to contribute to **typeid-python**.

Thank you for taking the time to contribute ❤️

## Requirements

- Linux or macOS (the development workflow is primarily tested on Unix-like systems)
- A supported Python version (e.g. Python 3.10+; latest tested: Python 3.14)
- [`uv`](https://astral.sh/uv/) – fast Python package manager and environment tool

## Installation

### 1. Fork & clone

1. Fork the repository on GitHub.
2. Clone your fork locally:

```bash
git clone https://github.com/akhundMurad/typeid-python.git
cd typeid-python
```

### 2. Install `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:

```bash
uv --version
```

### 3. Set up the development environment

Create and sync the virtual environment (including dev dependencies):

```bash
uv sync --all-groups
```

This will:

- create a local `.venv/`
- install dependencies according to `uv.lock`
- keep the environment reproducible

## Running tests

```bash
make test
```

or directly:

```bash
uv run pytest -v
```

## Formatters & linters

We use the following tools:

- **ruff** – linting & import sorting
- **black** – code formatting
- **mypy** – static type checking

Run all linters:

```bash
make check-linting
```

Auto-fix formatting issues where possible:

```bash
make fix-linting
```

## Building the package

Build wheel and source distribution:

```bash
make build
```

This uses `uv build` under the hood.

## Testing extras (CLI)

To test the CLI extra locally:

```bash
uv sync --all-groups --extra cli
uv run typeid new -p test
```

## Lockfile discipline

- `uv.lock` **must be committed**
- Always run dependency changes via `uv add` / `uv remove`
- CI uses `uv sync --locked`, so lockfile drift will fail builds

## How to name branches

Branch names are flexible, as long as they are respectful and descriptive.

Recommended patterns:

- `fix/core/32`
- `feature/cli-support`
- `docs/readme-update`
- `chore/ci-cleanup`

Referencing an issue number in the branch name is encouraged but not required.

## Submitting a Pull Request

1. Create a feature branch
2. Make sure tests and linters pass
3. Commit with a clear message
4. Open a pull request against `main`
5. Describe **what** changed and **why**

Happy hacking 🚀
If something is unclear, feel free to open an issue or discussion.
