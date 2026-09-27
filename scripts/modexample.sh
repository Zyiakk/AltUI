#!/bin/bash
# Builds the Mods tab example: AltUIMod_Example, a lamp in front of Jodi set up from AltUI's Mods tab.
#   build/AltUIMod_Example.pak   -> TheKillingAntidote/Mods/   (checked in as examples/AltUIMod_Example/AltUIMod_Example.pak)
# Separate from build.sh, like the weapon example: own manifest, own cook directory, own pak. Needs the AltUI structs
# and BPI_AltUIMod in the kit (build.sh writes them), and the Blueprint Loader's row structure.
set -e; source "$(dirname "$0")/../config.sh"; mkdir -p "$BUILD"
test -f "$KIT/Content/Mod/AltUI/BPI_AltUIMod.uasset" || { echo "BPI_AltUIMod missing in the kit - run ./build.sh first"; exit 1; }
python3 "$W/assets/gen/gen_modexample.py"

LIST="$W/assets/modexample_manifest.txt"; printf '87_modexample.json\n' > "$LIST"   # the commandlet resolves the entries next to the manifest
rm -f "$KIT/Content/Mod/AltUIMod_Example/"*.uasset
"$(dirname "$0")/ue.sh" "$UPROJECT" -run=TKA_BPGen.BPGen -manifest="$LIST" \
  -fastexit -unattended -nullrhi -nosplash -stdout > "$BUILD/modexample_raw.log" 2>&1 || true
grep -E "BPGEN|Error:|error" "$BUILD/modexample_raw.log" | grep -v "LogDerivedDataCache\|DoesPackageExist FAILED" \
  | sed "s/^.*LogBPGen: //" | sort -u > "$BUILD/modexample.log"
grep -q "BPGEN manifest ok .*87_modexample.json" "$BUILD/modexample.log"
! grep -E "warnings=[1-9]|errors=[1-9]|rows import problems" "$BUILD/modexample.log" \
  || { echo "BPGEN: problems present"; exit 1; }

"$(dirname "$0")/ue.sh" "$UPROJECT" -run=cook -targetplatform=LinuxNoEditor -iterate -unattended -nullrhi -nosplash -stdout \
  -cookdir="$KIT/Content/Mod/AltUIMod_Example" 2>&1 \
  | grep -E "LogCook: (Error|Warning)|Error:|Success|Failure" | tail -10 | tee "$BUILD/modexample_cook.log"
for f in Mod/AltUIMod_Example/SG_ExampleLamp Mod/AltUIMod_Example/BP_AltUIModExample Mod/AltUIMod_Example/AltUI_Entries Mod/AltUIMod_Example/AltUI_Fields Mod/AltUIMod_Example/TKA_BlueprintLoader Mod/AltUIMod_Example/TKA_Mod_Table; do
  test -f "$COOKED/$f.uasset" || { echo "cook: missing $f"; exit 1; }; done

RSP="$BUILD/modexample.rsp"; : > "$RSP"
for f in Mod/AltUIMod_Example/SG_ExampleLamp Mod/AltUIMod_Example/BP_AltUIModExample Mod/AltUIMod_Example/AltUI_Entries Mod/AltUIMod_Example/AltUI_Fields Mod/AltUIMod_Example/TKA_BlueprintLoader Mod/AltUIMod_Example/TKA_Mod_Table; do
  for ext in .uasset .uexp .ubulk; do
    [ -f "$COOKED/$f$ext" ] && echo "\"$COOKED/$f$ext\" \"../../../TheKillingAntidote/Content/$f$ext\"" >> "$RSP"
  done
done
rm -f "$BUILD/AltUIMod_Example.pak"
"$UNREALPAK" "$BUILD/AltUIMod_Example.pak" -create="$RSP" 2>&1 | grep -E "Added [0-9]+ files|Error|error" | tail -2
# the structs belong to AltUI.pak: a pak that ships its own would replace AltUI's for everyone who installs it
python3 "$W/scripts/pak11_extract.py" "$BUILD/AltUIMod_Example.pak" list > "$BUILD/modexample_files.txt"
grep -q "AltUI_Fields.uasset" "$BUILD/modexample_files.txt"; grep -q "BP_AltUIModExample.uasset" "$BUILD/modexample_files.txt"
! grep -q "Mod/AltUI/\|Mod/TKA_BlueprintLoader/" "$BUILD/modexample_files.txt" || { echo "pak ships AltUI or loader assets"; exit 1; }
ls -la "$BUILD/AltUIMod_Example.pak" && echo "MOD EXAMPLE OK"
