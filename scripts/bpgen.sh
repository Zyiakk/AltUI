#!/bin/bash
set -e; source "$(dirname "$0")/../config.sh"; mkdir -p "$BUILD"
# Mod assets are fully generated -> delete before the run (prevents stale graphs/references); stubs stay (augment)
rm -f "$KIT/Content/Mod/AltUI/"*.uasset
# one editor run: manifest, then the dumps of the classes the checks below need, then a hard exit (-fastexit: the engine
# teardown alone took ~50 s; everything is saved synchronously before). Raw log kept for timing (BPGEN timing lines).
DUMPS=/Game/Project/Classes/Character_Player_Base,/Game/Project/Classes/TKA_PlayerCameraManager,/Game/Mod/AltUI/BP_AltUIManager,/Game/Mod/AltUI/ABP_BodyScale
"$(dirname "$0")/ue.sh" "$UPROJECT" -run=TKA_BPGen.BPGen -manifest="$W/assets/manifest.txt" -dump=$DUMPS -fastexit -unattended -nullrhi -nosplash -stdout > "$BUILD/bpgen_raw.log" 2>&1 || true
grep -E "BPGEN|DUMP|Error:|error" "$BUILD/bpgen_raw.log" | grep -v "LogDerivedDataCache\|DoesPackageExist FAILED" | sed "s/^.*LogBPGen: //" | sort -u > "$BUILD/bpgen.log"
grep "BPGEN timing\|BPGEN OK\|BPGEN FAILED\|Error: BPGEN" "$BUILD/bpgen.log" || true
grep -q "BPGEN manifest ok .*20_hook.json" "$BUILD/bpgen.log"
! grep -E "warnings=[1-9]|errors=[1-9]" "$BUILD/bpgen.log" || { echo "BPGEN: compile warnings/errors present"; exit 1; }
grep -q "DUMP FUNC Build Catalog() script=" "$BUILD/bpgen.log"
grep -q "DUMP FUNC Wear The Clothes(name:FName,check covering:bool,update mask:bool,ignore compatible:bool) -> successed:bool" "$BUILD/bpgen.log"
grep -q "DUMP DEFAULT ViewPitchMin -80" "$BUILD/bpgen.log"
grep -E "DUMP FUNC ExecuteUbergraph_BP_AltUIManager.*script=[1-9]" "$BUILD/bpgen.log" >/dev/null
test "$(grep -c 'DUMP VAR AnimGraphNode_ModifyBone.* FAnimNode_ModifyBone' "$BUILD/bpgen.log")" = 24   # 21 scale + 3 translate nodes (root, foot_l, foot_r)
grep -q "DUMP VAR Breasts FVector" "$BUILD/bpgen.log"; grep -q "DUMP VAR Feet FVector" "$BUILD/bpgen.log"; grep -q "DUMP VAR Waist FVector" "$BUILD/bpgen.log"
echo "BPGEN OK"
