#!/bin/bash
# Deploys AltUI.pak to Mods/. The hook pak is rebuilt on every build but its bytes differ per rebuild (package GUID,
# compiler order) even with unchanged source, so it is only deployed when its source (assets/20_hook.json) changed since
# the last hook deploy (stamp $BUILD/hook_deployed.sha256) - a released hook stays byte-identical in the game.
# --hook forces the hook deploy.
set -e; source "$(dirname "$0")/../config.sh"
mkdir -p "$GAME/Content/Paks/~mods" "$GAME/Mods"
STAMP="$BUILD/hook_deployed.sha256"; SRC=$(sha256sum "$W/assets/20_hook.json" | cut -d' ' -f1)
if [[ " $* " == *" --hook "* || ! -f "$GAME/Content/Paks/~mods/AltUI_Hook_P.pak" || "$(cat "$STAMP" 2>/dev/null)" != "$SRC" ]]; then
    cp -v "$BUILD/AltUI_Hook_P.pak" "$GAME/Content/Paks/~mods/"; echo "$SRC" > "$STAMP"
else
    echo "hook unchanged (assets/20_hook.json) - game keeps its AltUI_Hook_P.pak"
fi
cp -v "$BUILD/AltUI.pak" "$GAME/Mods/"
echo "DEPLOY OK"
