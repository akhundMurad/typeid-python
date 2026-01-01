# Contributing

This document describes how to contribute to **typeid-python**.

Thank you for taking the time to contribute ❤️

## Requirements

### Core requirements (all contributors)

- Linux or macOS (development is primarily tested on Unix-like systems)
- A supported Python version (Python **3.10+**; latest tested: **Python 3.14**)
- [`uv`](https://astral.sh/uv/) – fast Python package manager and environment tool

### Optional (for Rust acceleration work)

- Rust toolchain (`rustc`, `cargo`)
- [`maturin`](https://www.maturin.rs/) (installed automatically via `uv` if needed)

> Rust is **optional**.  
> The project must always work in pure Python mode.

## Installation

### 1. Fork & clone

1. Fork the repository on GitHub.
2. Clone your fork locally:

```bash
git clone https://github.com/akhundMurad/typeid-python.git
cd typeid-python

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

Run the full test suite:

```bash
make test
```

or directly:

```bash
uv run pytest -v
```

Tests are expected to pass in **both**:

- pure Python mode
- Rust-accelerated mode (if available)

## Rust acceleration (optional)

TypeID includes an **optional Rust extension** used for performance-critical paths
(e.g. base32 encode/decode).

### Building the Rust extension locally

If you have Rust installed:

```bash
cd rust-base32
maturin develop
```

This installs the native extension into the active virtual environment.

You can verify which backend is active via tests.

### Testing Python fallback explicitly

Contributors **must not break** the pure Python fallback.

To test fallback behavior:

```bash
pytest tests/test_base32.py
```

This suite verifies that:

- Rust is used when available
- Python fallback is used when Rust is unavailable

## Benchmarks (performance-sensitive changes)

If your change affects performance-sensitive code paths (generation, parsing, base32):

Run benchmarks locally:

```bash
./bench/run.sh
```

Benchmark results are:

- reproducible
- stored as raw JSON
- compared across versions

When making performance claims, include:

- before/after numbers
- raw benchmark JSON (if applicable)

## Formatters & linters

We use:

- **ruff** – linting & import sorting
- **black** – code formatting
- **mypy** – static type checking

Run all linters:

```bash
make check-linting
```

Auto-fix formatting where possible:

```bash
make fix-linting
```

## Building the package

Build wheel and source distribution:

```bash
make build
```

This uses `uv build` under the hood.

Rust wheels are built automatically in CI when applicable.

## Testing extras (CLI)

To test the CLI extra locally:

```bash
uv sync --all-groups --extra cli
uv run typeid new -p test
```

## Lockfile discipline

- `uv.lock` **must be committed**
- Always change dependencies via `uv add` / `uv remove`
- CI uses `uv sync --locked`
- Lockfile drift will fail builds

## Branch naming

Branch names are flexible, as long as they are respectful and descriptive.

Recommended patterns:

- `fix/core/32`
- `feature/rust-base32`
- `perf/lazy-uuid`
- `docs/readme-update`
- `chore/ci-cleanup`

Referencing an issue number is encouraged but not required.

## Submitting a Pull Request

1. Create a feature branch
2. Ensure tests and linters pass
3. Ensure Python fallback still works
4. Commit with a clear message
5. Open a pull request against `main`
6. Describe **what** changed and **why**

Performance-related PRs should explain:

- which path was optimized
- what benchmark changed
- why the change is safe

---

Happy hacking 🚀
If anything is unclear, feel free to open an issue or discussion.
