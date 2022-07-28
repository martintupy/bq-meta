#!/bin/sh

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

# Install
VERSION=$(cat setup.cfg | grep "version =" | cut -d = -f 2 | xargs)
git tag $VERSION -a -m "Version: $VERSION"
git push origin --tags