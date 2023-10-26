#!/bin/sh

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

# Build
python3 -m build

# Install
VERSION=$(cat VERSION)
pip install --upgrade "dist/bq-meta-$VERSION.tar.gz"