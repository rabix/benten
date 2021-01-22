#!/bin/bash
if [[ $1 != "--inside" ]]; then
    exec docker run --rm -v$PWD:/benten -w/benten quay.io/tetron/manylinux2010_x86_64:fc5d4309b9cff6e58a2d0e5d9d4eba0c797c655b /benten/package/build-manylinux.sh --inside
fi

set -xe

export LD_LIBRARY_PATH=/usr/local/lib:/opt/python/cp38-cp38/lib

rm -rf bvenv
/opt/python/cp38-cp38/bin/python -m venv bvenv
. bvenv/bin/activate

pip install .
pip install pyinstaller==4.0

cd package
rm -rf dist
pyinstaller benten-ls.spec
python tgz.py
