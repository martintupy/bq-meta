#!/bin/sh

cd "$(dirname "${BASH_SOURCE[0]}")/.."

source venv/bin/activate

python3 -m build

VERSION=$(cat setup.cfg | grep "version =" | cut -d = -f 2 | xargs)

pip install "dist/bq-meta-$VERSION.tar.gz"