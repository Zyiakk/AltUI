#!/bin/bash
# Quick menu sector material: create it in the kit (editor Python) and cook it for Windows under Wine (D3D SM5 shaders - a
# Linux cook has none and the DX11 game would draw the default material). The cooked files live in the repo
# (assets/cooked_win/Mod/AltUI/Mat, stamp = sha256 of material.py) and replace the Linux-cooked copy in AltUI.pak (pak.sh),
# so a build needs Wine only after material.py changed. A kit without the asset (fresh checkout) gets it without Wine.
set -eo pipefail; source "$(dirname "$0")/../../config.sh"
S="$W/scripts/quickmenu/material.py"; D="$W/assets/cooked_win/Mod/AltUI/Mat"; mkdir -p "$D"
HASH=$(sha256sum "$S" | cut -d' ' -f1)
if [ "$(cat "$D/stamp.sha256" 2>/dev/null)" = "$HASH" ] && [ -f "$D/M_QuickSector.uasset" ]; then
  [ -f "$KIT/Content/Mod/AltUI/Mat/M_QuickSector.uasset" ] || "$W/scripts/edtest.sh" "$S"
  echo "QUICK MATERIAL up to date"; exit 0; fi
"$W/scripts/edtest.sh" "$S"
rm -rf "$COOKED_WIN/Mod/AltUI/Mat"
"$W/scripts/wincook.sh" -cookdir=Mod/AltUI/Mat
cp -v "$COOKED_WIN/Mod/AltUI/Mat/M_QuickSector.uasset" "$COOKED_WIN/Mod/AltUI/Mat/M_QuickSector.uexp" "$D/"
echo "$HASH" > "$D/stamp.sha256"; echo "QUICK MATERIAL cooked"
