#!/bin/bash
# Builds the weapon example: WeaponAltUI_Example, a skin mod for the UMP45 with a generated checker texture.
#   build/WeaponAltUI_Example.pak   -> TheKillingAntidote/Mods/   (checked in as examples/WeaponAltUI_Example/WeaponAltUI_Example.pak)
# Separate from build.sh, like the loader example: own manifest, own cook directory, own pak. Needs the AltUI structs
# in the kit (build.sh writes them) - the skin table refers to /Game/Mod/AltUI/S_WeaponSkin as its row structure.
set -e; source "$(dirname "$0")/../config.sh"; mkdir -p "$BUILD"
test -f "$KIT/Content/Mod/AltUI/S_WeaponSkin.uasset" || { echo "S_WeaponSkin missing in the kit - run ./build.sh first"; exit 1; }
python3 "$W/assets/gen/gen_weaponexample.py"

LIST="$W/assets/weaponexample_manifest.txt"; printf '85_weaponexample.json\n' > "$LIST"   # the commandlet resolves the entries next to the manifest
rm -f "$KIT/Content/Mod/WeaponAltUI_Example/"*.uasset
"$(dirname "$0")/ue.sh" "$UPROJECT" -run=TKA_BPGen.BPGen -manifest="$LIST" \
  -fastexit -unattended -nullrhi -nosplash -stdout > "$BUILD/weaponexample_raw.log" 2>&1 || true
grep -E "BPGEN|Error:|error" "$BUILD/weaponexample_raw.log" | grep -v "LogDerivedDataCache\|DoesPackageExist FAILED" \
  | sed "s/^.*LogBPGen: //" | sort -u > "$BUILD/weaponexample.log"
grep -q "BPGEN manifest ok .*85_weaponexample.json" "$BUILD/weaponexample.log"
! grep -E "warnings=[1-9]|errors=[1-9]|rows import problems" "$BUILD/weaponexample.log" \
  || { echo "BPGEN: problems present"; exit 1; }

"$(dirname "$0")/ue.sh" "$UPROJECT" -run=cook -targetplatform=LinuxNoEditor -iterate -unattended -nullrhi -nosplash -stdout \
  -cookdir="$KIT/Content/Mod/WeaponAltUI_Example" 2>&1 \
  | grep -E "LogCook: (Error|Warning)|Error:|Success|Failure" | tail -10 | tee "$BUILD/weaponexample_cook.log"
for f in Mod/WeaponAltUI_Example/T_ExampleSkin Mod/WeaponAltUI_Example/Mod_WeaponSkin Mod/WeaponAltUI_Example/TKA_Mod_Table; do
  test -f "$COOKED/$f.uasset" || { echo "cook: missing $f"; exit 1; }; done

RSP="$BUILD/weaponexample.rsp"; : > "$RSP"
for f in Mod/WeaponAltUI_Example/T_ExampleSkin Mod/WeaponAltUI_Example/Mod_WeaponSkin Mod/WeaponAltUI_Example/TKA_Mod_Table; do
  for ext in .uasset .uexp .ubulk; do
    [ -f "$COOKED/$f$ext" ] && echo "\"$COOKED/$f$ext\" \"../../../TheKillingAntidote/Content/$f$ext\"" >> "$RSP"
  done
done
rm -f "$BUILD/WeaponAltUI_Example.pak"
"$UNREALPAK" "$BUILD/WeaponAltUI_Example.pak" -create="$RSP" 2>&1 | grep -E "Added [0-9]+ files|Error|error" | tail -2
# the structs belong to AltUI.pak: a pak that ships its own would replace AltUI's for everyone who installs it
python3 "$W/scripts/pak11_extract.py" "$BUILD/WeaponAltUI_Example.pak" list > "$BUILD/weaponexample_files.txt"
grep -q "Mod_WeaponSkin.uasset" "$BUILD/weaponexample_files.txt"
! grep -q "Mod/AltUI/" "$BUILD/weaponexample_files.txt" || { echo "pak ships AltUI assets"; exit 1; }
ls -la "$BUILD/WeaponAltUI_Example.pak" && echo "WEAPON EXAMPLE OK"
