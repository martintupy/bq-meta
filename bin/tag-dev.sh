#!/bin/sh

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

VERSION=$(cat setup.cfg | grep "version =" | cut -d = -f 2 | xargs)
TIMESTAMP=$(python -c 'from datetime import datetime; print(datetime.utcnow().strftime("%Y%m%d%H%M%S"))')
git tag $VERSION+$TIMESTAMP -a -m "Version: $VERSION"
git push origin --tags