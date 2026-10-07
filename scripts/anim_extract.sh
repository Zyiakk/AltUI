#!/bin/bash
# Animation pipeline step 1 (docs/specs/2026-10-06-anim-pipeline-design.md): the game's source animations + skeleton from the main pak
# (our extractor - umodel cannot read Oodle) into build/anim/src, bones as .psa (+ props.txt with sync markers / notifies) into
# build/anim/psa. Curves: scripts/animcurves.py on the extracted .uasset.
set -e; source "$(dirname "$0")/../config.sh"
OUT="$BUILD/anim"; mkdir -p "$OUT/src" "$OUT/psa"
ANIMS="${ANIMS:-Female_Walk Female_Run Female_WalkHurt_F Female_Run_Hurt}"
RX="Character/Jodi/(Body/Female_Skeleton|Animations/($(echo $ANIMS | tr ' ' '|')))\\."
python3 "$(dirname "$0")/pak11_extract.py" "$GAME/Content/Paks/pakchunk0-WindowsNoEditor.pak" "$OUT/src" "$RX" >/dev/null
UMODEL="${UMODEL:-$W/build/tools/UEViewer/umodel}"   # UE Viewer (github.com/gildor2/UEViewer), built from source
test -x "$UMODEL" || { echo "umodel missing: build UE Viewer and put umodel at $UMODEL (or set UMODEL)"; exit 1; }
# Jodi's body from the kit as FBX (once; delete build/kit/female.fbx to redo) - Blender puts the animations on it
mkdir -p "$BUILD/kit"
if [ ! -f "$BUILD/kit/female.fbx" ]; then
  "$(dirname "$0")/ue.sh" "$UPROJECT" -run=TKA_BPGen.BPGen -exportfbx=/Game/Project/Character/Jodi/Body/Female.Female="$BUILD/kit/female.fbx" \
    -fastexit -unattended -nullrhi -nosplash -stdout > "$BUILD/kit/export_raw.log" 2>&1 || true
  grep -q "BPGEN exportfbx .* ok" "$BUILD/kit/export_raw.log" || { echo "body export failed (see $BUILD/kit/export_raw.log)"; exit 1; }
fi
for a in $ANIMS; do
  (cd "$OUT/src/TheKillingAntidote/Content" && "$UMODEL" -game=ue4.27 -path="$OUT/src/TheKillingAntidote/Content" -export -out="$OUT/psa" "Project/Character/Jodi/Animations/$a.uasset" >/dev/null)
done
find "$OUT/psa" -name "*.psa" | sort
