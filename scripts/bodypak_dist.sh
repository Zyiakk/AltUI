#!/bin/bash
# Builds build/bodypak.pyz: single-file converter for other users (python3 bodypak.pyz <Original.pak> [--name Body_X] [--title "..."]).
# Standard library only – the Oodle decoder is pure Python (oodle_kraken.py, GPL-3, hence LICENSE-GPL-3.0.txt in the zip).
set -e; cd "$(dirname "$0")/.."; rm -rf build/bodypak_app; mkdir -p build/bodypak_app
cp scripts/bodypak.py scripts/bodypak_abp.py scripts/bodyscale_groups.py scripts/pak11_extract.py scripts/pakio.py scripts/oodle_kraken.py scripts/uasset_props.py scripts/uasset_pkg.py scripts/uasset_datatable.py build/bodypak_app/
cp LICENSE-GPL-3.0.txt build/bodypak_app/
printf 'import bodypak\nbodypak.main()\n' > build/bodypak_app/__main__.py
python3 -m zipapp build/bodypak_app -o build/bodypak.pyz -p "/usr/bin/env python3"
rm -rf build/bodypak_app; ls -la build/bodypak.pyz
