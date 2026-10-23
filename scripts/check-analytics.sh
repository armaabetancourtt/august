#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest -q tests
if command -v dbt >/dev/null 2>&1; then dbt parse; fi
