#!/usr/bin/env bash
set -e

uv run pytest bench/ \
  --benchmark-only \
  --benchmark-columns=min,mean,stddev,ops \
  --benchmark-sort=mean \
  --benchmark-save=my_benchmark_run
