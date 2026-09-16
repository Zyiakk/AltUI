#!/bin/bash
set -e; source "$(dirname "$0")/../config.sh"; mkdir -p "$BUILD"
R1="$BUILD/mod.rsp"; : > "$R1"
find "$COOKED/Mod/AltUI" -type f \( -name "*.uasset" -o -name "*.uexp" -o -name "*.ubulk" \) | sort | while read -r f; do
  rel="${f#$COOKED/}"; echo "\"$f\" \"../../../TheKillingAntidote/Content/$rel\"" >> "$R1"; done
R2="$BUILD/hook.rsp"; : > "$R2"
for f in "$COOKED/Project/Classes/TKA_PlayerCameraManager.uasset" "$COOKED/Project/Classes/TKA_PlayerCameraManager.uexp"; do
  rel="${f#$COOKED/}"; echo "\"$f\" \"../../../TheKillingAntidote/Content/$rel\"" >> "$R2"; done
rm -f "$BUILD/AltUI.pak" "$BUILD/AltUI_Hook_P.pak"
"$UNREALPAK" "$BUILD/AltUI.pak" -create="$R1" 2>&1 | grep -E "Added|Error|error" | tail -3
"$UNREALPAK" "$BUILD/AltUI_Hook_P.pak" -create="$R2" 2>&1 | grep -E "Added|Error|error" | tail -3
ls -la "$BUILD"/*.pak && echo "PAK OK"
