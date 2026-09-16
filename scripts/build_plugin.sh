#!/bin/bash
# Builds only the TKA_BPGen module and writes the module manifest itself (the full target build fails on
# a never-built engine plugin (MeshModelingToolset), so UBT does not write the manifest).
set -e; source "$(dirname "$0")/../config.sh"; mkdir -p "$BUILD"
"$ENGINE/Engine/Build/BatchFiles/Linux/Build.sh" UE4Editor Linux Development -Project="$UPROJECT" -TargetType=Editor -Module=TKA_BPGen -Progress > "$BUILD/plugin_build.log" 2>&1 || { grep -E "error:" "$BUILD/plugin_build.log" | head; echo "PLUGIN BUILD FAILED"; exit 1; }
grep -E "error:" "$BUILD/plugin_build.log" | grep -v MeshSpaceDeformer && { echo "PLUGIN BUILD FAILED"; exit 1; }
BIN="$KIT/Plugins/TKA_BPGen/Binaries/Linux"
test -f "$BIN/libUE4Editor-TKA_BPGen.so"
BUILDID=$(python3 -c "import json;print(json.load(open(\"$ENGINE/Engine/Binaries/Linux/UE4Editor.modules\"))[\"BuildId\"])")
printf "{\n\t\"BuildId\": \"%s\",\n\t\"Modules\": \n\t{\n\t\t\"TKA_BPGen\": \"libUE4Editor-TKA_BPGen.so\"\n\t}\n}\n" "$BUILDID" > "$BIN/UE4Editor.modules"
cat "$BIN/UE4Editor.modules"; echo "PLUGIN BUILD OK"
