#!/bin/bash
# Cooks for WindowsNoEditor with the Windows UE 4.27 under Wine (custom materials need D3D SM5 shaders; the Linux kit
# cannot produce them). Usage: scripts/wincook.sh <cook args...>   e.g. -cookdir=Mod/X -map=/Game/Mod/X/Map
# -cookdir=Mod/X is relative to Content. Needs: Wine prefix $WINE_UE_PREFIX, the real d3dcompiler_47 (Wine's own
# vkd3d one fails on UE's shaders: E5001 "Unexpected modifier used on a function").
set -e; source "$(dirname "$0")/../config.sh"
if pgrep -x TheKillingAntid >/dev/null; then echo "game is running - close it first" >&2; exit 1; fi
C="$WINCOOK_PROJECT"; mkdir -p "$C"
python3 -c "
import json; d=json.load(open('$UPROJECT')); d['Plugins']=[p for p in d['Plugins'] if p['Name']!='TKA_BPGen']
json.dump(d, open('$C/TheKillingAntidote.uproject','w'), indent=1)"
rm -rf "$C/Config"; cp -r "$KIT/Config" "$C/Config"; ln -sfn "$KIT/Content" "$C/Content"
ARGS=(); for a in "$@"; do case "$a" in -cookdir=*) ARGS+=("-cookdir=Z:$C/Content/${a#-cookdir=}");; *) ARGS+=("$a");; esac; done
# mshtml off: no Wine-Gecko install dialog. mscoree must stay: UE4Editor-SwarmInterface.dll imports it (without it the
# editor quits silently); the Wine-Mono dialog came from creating the prefix, not from cooking
export WINEPREFIX="$WINE_UE_PREFIX" WINEDEBUG=-all WINEDLLOVERRIDES="d3dcompiler_47=n,b;mshtml="
cd "$UE_WIN/Engine/Binaries/Win64"
timeout 3600 systemd-run --user --scope -q -E WINEPREFIX -E WINEDEBUG -E WINEDLLOVERRIDES wine UE4Editor-Cmd.exe "Z:$C/TheKillingAntidote.uproject" -run=cook -targetplatform=WindowsNoEditor \
  "${ARGS[@]}" -unattended -nullrhi -nosplash -stdout -NoLogTimes > "$BUILD/wincook.log" 2>&1 || true
if grep -qE "E50[0-9][0-9]:|Failed to compile Material" "$BUILD/wincook.log"; then
  grep -E "Failed to compile Material" "$BUILD/wincook.log" | sort -u | head; echo "WINCOOK: shader errors" >&2; exit 1; fi
grep -E "Success - |Failure - " "$BUILD/wincook.log" | tail -1
grep -q "Success - 0 error" "$BUILD/wincook.log"
