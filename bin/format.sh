#!/bin/sh

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

autoflake --in-place --remove-all-unused-imports bq_meta/**/*.py
