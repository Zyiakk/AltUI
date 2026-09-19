#!/bin/bash
# Builds build/bodypak.pyz: single-file converter for other users (python3 bodypak.pyz <Original.pak> [--name Body_X] [--title "..."]). Standard library + bundled ooz.
set -e; cd "$(dirname "$0")/.."; rm -rf build/bodypak_app; mkdir -p build/bodypak_app
cp scripts/bodypak.py scripts/pak11_extract.py scripts/pakio.py scripts/uasset_props.py scripts/uasset_pkg.py scripts/uasset_datatable.py build/bodypak_app/
# ooz decoder (GPL-3, tools/fetch_ooz.sh) for Windows and Linux: needed to read the mesh's import table (companion assets) of Oodle-compressed paks
for lib in tools/ooz/ooz.dll tools/ooz/libooz.so; do [ -f "$lib" ] || { echo "missing $lib – run tools/fetch_ooz.sh"; exit 1; }; cp "$lib" build/bodypak_app/; done
printf 'import bodypak\nbodypak.main()\n' > build/bodypak_app/__main__.py
python3 -m zipapp build/bodypak_app -o build/bodypak.pyz -p "/usr/bin/env python3"
rm -rf build/bodypak_app; echo "build/bodypak.pyz"
