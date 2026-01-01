# Performance Benchmarks

This directory contains reproducible performance benchmarks for `typeid-python`.

The goal is to transparently demonstrate:
- the impact of the Rust base32 implementation,
- the effect of additional architectural optimizations,
- and the remaining overhead compared to raw UUIDs.

All benchmark results are produced using `pytest-benchmark` and committed as raw JSON.

## Benchmark environments

Benchmarks were run with:

- Python: **3.13**
- OS: macOS / Linux
- CPU: Apple Silicon / x86_64
- Tooling: `pytest-benchmark`
- UUID backends:
  - `uuid-utils` (Rust, optional)
  - `uuid6` (Python, legacy comparison)

Exact environment details are embedded in each JSON result file.

## How to run benchmarks locally

### Install dependencies

```bash
uv sync --extra rust
uv sync --dev
```

### Run all benchmarks

```bash
./bench/run.sh
```

### Export results to JSON

```bash
uv run pytest bench/ --benchmark-only --benchmark-json=bench.json
```

## Benchmark result sets

We maintain multiple benchmark snapshots to show progress over time:

| ID       | Description                                                          |
| -------- | -------------------------------------------------------------------- |
| **0001** | Pure Python implementation (before Rust)                             |
| **0004** | Rust base32 + `uuid-utils` + lazy UUID + single decode optimizations |

Raw benchmark data:

- `bench/results/0001_before_rust.json`
- `bench/results/0002_rust_optimized.json`

These files are the **source of truth**.

---

## Comparison summary (mean time, µs)

| Benchmark           | 0001 – Before Rust | 0002 – Rust + optimizations | Speedup (0004 vs 0001) |
| ------------------- | -----------------: | --------------------------: | ---------------------: |
| **TypeID generate** |           3.467 µs |                **0.701 µs** |       **4.94× faster** |
| **TypeID parse**    |           2.076 µs |                **1.296 µs** |       **1.60× faster** |
| **TypeID workflow** |           5.516 µs |                **2.247 µs** |       **2.46× faster** |

## What changed between versions

### Rust integration

* Rust base32 encode/decode
* `uuid-utils` for UUIDv7 generation
* Major improvement in **generation speed**
* Temporary regression in parse due to eager UUID construction

### Architectural optimizations

* Lazy UUID materialization (`.uuid` created only when accessed)
* Single-pass suffix validation (no double decode)
* Optimized `from_uuid()` path
* Cached string rendering

Result: parse and workflow became faster than the original Python baseline.

## UUID backend comparison (context)

These numbers represent the approximate lower bound:

| Operation | uuid-utils |    uuid6 |
| --------- | ---------: | -------: |
| Generate  |   ~0.08 µs | ~1.51 µs |
| Parse     |   ~0.12 µs | ~0.53 µs |

TypeID adds overhead for:

* base32 encoding
* prefix handling
* validation
* safety guarantees

This overhead is now reduced to approximately **1–2 µs**, depending on the operation.

## Cold path vs warm path

All benchmarks measure cold-path performance: each iteration operates on a new identifier.

In real applications (logs, databases, queues), identifiers are often:

- parsed multiple times,
- stringified repeatedly,
- compared frequently.

In those scenarios, caching and lazy evaluation reduce effective cost further.

## Benchmark philosophy

TypeID does **not** aim to outperform raw UUIDs in every metric.

Instead, it provides:

- sortable identifiers,
- human-readable representation,
- type safety,
- explainability,

at a cost of roughly **~1 µs** over raw UUID operations.

This tradeoff is intentional and documented.

## Performance regression policy

Performance regressions are tracked via benchmark comparison.

Future CI plans:

- compare PR benchmarks against `0002`
- fail CI on statistically significant regressions

## Reproducibility

If you doubt any number:

1. Clone the repository
2. Run the benchmarks
3. Compare the JSON output

No screenshots, no hidden scripts — only raw data.

## Summary

* TypeID generation is now **~5× faster** than the original implementation
* Parsing is **faster than the original Python baseline**
* End-to-end workflows are **~2.5× faster**
* Improvements are measurable, documented, and reproducible
