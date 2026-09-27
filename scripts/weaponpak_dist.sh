#!/bin/bash
# Builds build/weaponpak.pyz: single-file weapon mod converter for other users, skins and models
# (python3 weaponpak.pyz <Replacer.pak> [--name X] [--title "..."]).
# Standard library only – the Oodle decoder is pure Python (oodle_kraken.py, GPL-3, hence LICENSE-GPL-3.0.txt in the zip).
set -e; cd "$(dirname "$0")/.."; rm -rf build/weaponpak_app; mkdir -p build/weaponpak_app
cp scripts/weaponpak.py scripts/weapon_skins.py scripts/bodypak.py scripts/bodypak_abp.py scripts/bodyscale_groups.py scripts/pak11_extract.py scripts/pakio.py scripts/oodle_kraken.py scripts/uasset_props.py scripts/uasset_pkg.py scripts/uasset_datatable.py build/weaponpak_app/
cp LICENSE-GPL-3.0.txt build/weaponpak_app/
printf 'import weaponpak\nweaponpak.main()\n' > build/weaponpak_app/__main__.py
python3 -m zipapp build/weaponpak_app -o build/weaponpak.pyz -p "/usr/bin/env python3"
rm -rf build/weaponpak_app; ls -la build/weaponpak.pyz
