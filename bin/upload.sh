#!/bin/sh

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

source venv/bin/activate

twine check dist/*
twine upload dist/*