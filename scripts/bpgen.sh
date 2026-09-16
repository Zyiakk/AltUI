#!/bin/bash
set -e; source "$(dirname "$0")/../config.sh"; mkdir -p "$BUILD"
# Mod assets are fully generated -> delete before the run (prevents stale graphs/references); stubs stay (augment)
rm -f "$KIT/Content/Mod/AltUI/"*.uasset
"$UE_CMD" "$UPROJECT" -run=TKA_BPGen.BPGen -manifest="$W/assets/manifest.txt" -unattended -nullrhi -nosplash -stdout 2>&1 | grep -E "BPGEN|Error:|error" | grep -v "LogDerivedDataCache\|DoesPackageExist FAILED" | sed "s/^.*LogBPGen: //" | sort -u | tee "$BUILD/bpgen.log"
grep -q "BPGEN manifest ok .*20_hook.json" "$BUILD/bpgen.log"
! grep -E "warnings=[1-9]|errors=[1-9]" "$BUILD/bpgen.log" || { echo "BPGEN: compile warnings/errors present"; exit 1; }
for p in /Game/Project/Classes/Character_Player_Base /Game/Project/Classes/TKA_PlayerCameraManager /Game/Mod/AltUI/BP_AltUIManager; do
  "$UE_CMD" "$UPROJECT" -run=TKA_BPGen.BPGen -dump=$p -unattended -nullrhi -nosplash -stdout 2>&1 | grep "DUMP" | sed "s/^.*LogBPGen: //" | sort -u >> "$BUILD/bpgen.log"
done
grep -q "DUMP FUNC Build Catalog() script=" "$BUILD/bpgen.log"
grep -q "DUMP FUNC Wear The Clothes(name:FName,check covering:bool,update mask:bool,ignore compatible:bool) -> successed:bool" "$BUILD/bpgen.log"
grep -q "DUMP DEFAULT ViewPitchMin -80" "$BUILD/bpgen.log"
grep -E "DUMP FUNC ExecuteUbergraph_BP_AltUIManager.*script=[1-9]" "$BUILD/bpgen.log" >/dev/null
echo "BPGEN OK"
