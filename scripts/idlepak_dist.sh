#!/bin/bash
# Builds build/idlepak.pyz: single-file converter for other users (python3 idlepak.pyz <Replacer.pak> [--name X] [--title "..."] [--altui AltUI.pak]).
# Standard library only – the Oodle decoder is pure Python (oodle_kraken.py, GPL-3, hence LICENSE-GPL-3.0.txt in the zip).
set -e; cd "$(dirname "$0")/.."; rm -rf build/idlepak_app; mkdir -p build/idlepak_app
cp scripts/idlepak.py scripts/idle_mods.py scripts/anim_templates.py scripts/weaponpak.py scripts/weapon_skins.py scripts/bodypak.py scripts/bodybones.py scripts/bodypak_abp.py scripts/bodyscale_groups.py scripts/pak11_extract.py scripts/pakio.py scripts/oodle_kraken.py scripts/uasset_props.py scripts/uasset_pkg.py scripts/uasset_datatable.py build/idlepak_app/
cp LICENSE-GPL-3.0.txt build/idlepak_app/
printf 'import idlepak\nidlepak.main()\n' > build/idlepak_app/__main__.py
python3 -m zipapp build/idlepak_app -o build/idlepak.pyz -p "/usr/bin/env python3"
rm -rf build/idlepak_app; ls -la build/idlepak.pyz
