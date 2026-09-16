#!/bin/bash
# Note: the engine build has no Windows target platform; a LinuxNoEditor cook is byte-identical for BP/DataTable assets (confirmed by smoke test).
set -e; source "$(dirname "$0")/../config.sh"; mkdir -p "$BUILD"
"$UE_CMD" "$UPROJECT" -run=cook -targetplatform=LinuxNoEditor -iterate -unattended -nullrhi -nosplash -stdout \
  -cookdir="$KIT/Content/Mod/AltUI" -map=/Game/Project/Classes/TKA_PlayerCameraManager 2>&1 | grep -E "LogCook|Error|Success|Failure|AltUI|TKA_PlayerCameraManager" | grep -vE "LogCook: Display: (Cooking|Updating|Warning)|LogDerivedDataCache" | tail -40 | tee "$BUILD/cook.log"
if [ ! -f "$COOKED/Project/Classes/TKA_PlayerCameraManager.uasset" ]; then echo "COOK: hook missing - fallback -cookdir Project/Classes";
  "$UE_CMD" "$UPROJECT" -run=cook -targetplatform=LinuxNoEditor -iterate -unattended -nullrhi -nosplash -stdout -cookdir="$KIT/Content/Project/Classes" 2>&1 | grep -E "LogCook|Error" | tail -20; fi
test -f "$COOKED/Project/Classes/TKA_PlayerCameraManager.uasset"
test -f "$COOKED/Mod/AltUI/BP_AltUIManager.uasset"
echo "COOK OK"
