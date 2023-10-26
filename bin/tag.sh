#!/bin/sh

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

VERSION=$(cat VERSION)
git tag $VERSION -a -m "Version: $VERSION"
git push origin --tags