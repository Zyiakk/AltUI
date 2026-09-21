#!/bin/bash
# Builds build/altui_names.pyz: export / import of AltUI's custom display names (Saved/SaveGames/AltUI_Names.sav <-> JSON). Standard library only.
set -e; cd "$(dirname "$0")/.."; rm -rf build/altui_names_app; mkdir -p build/altui_names_app
cp scripts/altui_names.py scripts/savegame_gvas.py build/altui_names_app/
printf 'import altui_names\naltui_names.main()\n' > build/altui_names_app/__main__.py
python3 -m zipapp build/altui_names_app -o build/altui_names.pyz -p "/usr/bin/env python3"
rm -rf build/altui_names_app; ls -la build/altui_names.pyz
