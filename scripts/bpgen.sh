#!/bin/bash
set -e; source "$(dirname "$0")/../config.sh"; mkdir -p "$BUILD"
# incremental: bpgen skips assets whose entries (and the signature files) did not change - see -hashes in BPGenCommandlet.
# FULL=1 (./build.sh --full) starts from scratch as before.
HASHES="$BUILD/bpgen_hashes.json"
[ "${FULL:-0}" = 1 ] && { rm -f "$KIT/Content/Mod/AltUI/"*.uasset "$KIT/Content/Project/Classes/TKA_PlayerCameraManager.uasset" "$HASHES"; }
# one editor run: manifest, then the dumps of the classes the checks below need, then a hard exit (-fastexit: the engine
# teardown alone took ~50 s; everything is saved synchronously before). Raw log kept for timing (BPGEN timing lines).
DUMPS=/Game/Project/Classes/Character_Player_Base,/Game/Project/Classes/TKA_PlayerCameraManager,/Game/Mod/AltUI/BP_AltUIManager,/Game/Mod/AltUI/ABP_BodyScale,/Game/Mod/AltUI/CM_AltUICam,/Game/Mod/AltUI/BP_AltUILoaderEntry
"$(dirname "$0")/ue.sh" "$UPROJECT" -run=TKA_BPGen.BPGen -manifest="$W/assets/manifest.txt" -hashes="$HASHES" -sigfiles=30_manager.json -freshprefix=/Game/Mod/AltUI/,/Game/Project/Classes/TKA_PlayerCameraManager -dump=$DUMPS -fastexit -unattended -nullrhi -nosplash -stdout > "$BUILD/bpgen_raw.log" 2>&1 || true
grep -E "BPGEN|DUMP|Error:|error" "$BUILD/bpgen_raw.log" | grep -v "LogDerivedDataCache\|DoesPackageExist FAILED" | sed "s/^.*LogBPGen: //" | sort -u > "$BUILD/bpgen.log"
grep "BPGEN timing\|BPGEN OK\|BPGEN FAILED\|Error: BPGEN" "$BUILD/bpgen.log" || true
grep -q "BPGEN manifest ok .*20_hook.json" "$BUILD/bpgen.log"
! grep -E "warnings=[1-9]|errors=[1-9]" "$BUILD/bpgen.log" || { echo "BPGEN: compile warnings/errors present"; exit 1; }
# also errors of a blueprint compiled only on load (e.g. a skipped one against a class rebuilt in this run) - a clean run has none
! grep -q "LogBlueprint: Error" "$BUILD/bpgen_raw.log" || { echo "BPGEN: blueprint errors on load"; grep "LogBlueprint: Error" "$BUILD/bpgen_raw.log" | sort -u | head -5; exit 1; }
grep -q "DUMP FUNC Build Catalog() script=" "$BUILD/bpgen.log"
grep -q "DUMP FUNC Wear The Clothes(name:FName,check covering:bool,update mask:bool,ignore compatible:bool) -> successed:bool" "$BUILD/bpgen.log"
grep -q "DUMP DEFAULT ViewPitchMin -80" "$BUILD/bpgen.log"
grep -E "DUMP FUNC BlueprintModifyCamera.*script=[1-9]" "$BUILD/bpgen.log" >/dev/null          # the framing lives in CM_AltUICam
! grep -q "DUMP FUNC BlueprintUpdateCamera" "$BUILD/bpgen.log" || { echo "BPGEN: hook still carries the camera override"; exit 1; }
grep -E "DUMP FUNC ExecuteUbergraph_BP_AltUIManager.*script=[1-9]" "$BUILD/bpgen.log" >/dev/null
test "$(grep -c 'DUMP VAR AnimGraphNode_ModifyBone.* FAnimNode_ModifyBone' "$BUILD/bpgen.log")" = 24   # 21 scale + 3 translate nodes (root, foot_l, foot_r)
grep -q "DUMP VAR Breasts FVector" "$BUILD/bpgen.log"; grep -q "DUMP VAR Feet FVector" "$BUILD/bpgen.log"; grep -q "DUMP VAR Waist FVector" "$BUILD/bpgen.log"
echo "BPGEN OK"
