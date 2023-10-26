#!/bin/sh

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

python3 -m build

VERSION=$(cat VERSION)

docker build . \
  --build-arg version=$VERSION \
  --tag bq-meta:latest \
  --tag bq-meta:$VERSION