#!/bin/bash
set -e; source "$(dirname "$0")/../config.sh"
mkdir -p "$GAME/Content/Paks/~mods" "$GAME/Mods"
cp -v "$BUILD/AltUI_Hook_P.pak" "$GAME/Content/Paks/~mods/"
cp -v "$BUILD/AltUI.pak" "$GAME/Mods/"
echo "DEPLOY OK"
