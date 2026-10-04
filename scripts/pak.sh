#!/bin/bash
set -e; source "$(dirname "$0")/../config.sh"; mkdir -p "$BUILD"
R1="$BUILD/mod.rsp"; : > "$R1"
find "$COOKED/Mod/AltUI" -type f \( -name "*.uasset" -o -name "*.uexp" -o -name "*.ubulk" \) | sort | while read -r f; do
  rel="${f#$COOKED/}"; echo "\"$f\" \"../../../TheKillingAntidote/Content/$rel\"" >> "$R1"; done
# Windows-cooked assets kept in the repo (scripts/quickmenu/material.sh: D3D shaders) replace their Linux-cooked copies
if [ -d "$W/assets/cooked_win" ]; then
  find "$W/assets/cooked_win" -type f \( -name "*.uasset" -o -name "*.uexp" \) | sort | while read -r f; do
    rel="${f#$W/assets/cooked_win/}"; dst="../../../TheKillingAntidote/Content/$rel"
    grep -vF "\"$dst\"" "$R1" > "$R1.tmp" || true; mv "$R1.tmp" "$R1"; echo "\"$f\" \"$dst\"" >> "$R1"; done; fi
R2="$BUILD/hook.rsp"; : > "$R2"
for f in "$COOKED/Project/Classes/TKA_PlayerCameraManager.uasset" "$COOKED/Project/Classes/TKA_PlayerCameraManager.uexp"; do
  rel="${f#$COOKED/}"; echo "\"$f\" \"../../../TheKillingAntidote/Content/$rel\"" >> "$R2"; done
rm -f "$BUILD/AltUI.pak" "$BUILD/AltUI_Hook_P.pak"
"$UNREALPAK" "$BUILD/AltUI.pak" -create="$R1" 2>&1 | grep -E "Added|Error|error" | tail -3
"$UNREALPAK" "$BUILD/AltUI_Hook_P.pak" -create="$R2" 2>&1 | grep -E "Added|Error|error" | tail -3
ls -la "$BUILD"/*.pak && echo "PAK OK"
