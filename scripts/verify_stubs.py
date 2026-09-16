#!/usr/bin/env python3
"""verify_stubs.py – compares parameter order/types of the cooked kit stubs with API dumps of the real game.
Requires COOKED in the environment (config.sh); GAME_API_DIR (directory with one <Class>.txt dump per game class) enables the check, unset = skipped."""
import sys, os, re
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import uasset_funcs
W = os.path.dirname(H)
COOKED = os.environ["COOKED"]
API_DIR = os.environ.get("GAME_API_DIR")
if not API_DIR or not os.path.isdir(API_DIR):
    print("VERIFY STUBS SKIPPED (GAME_API_DIR not set)"); sys.exit(0)
STUBS = {  # cooked stub -> (API dump, checked functions)
    "Project/Classes/Character_Player_Base": ("Character_Player_Base", ["Wear The Clothes", "Take off this clothes", "Get Wearing Clothes Names", "is clothes wearing", "Find Clothes Component With Name", "Get Clothes Color", "Save Clothes Color", "Restore Clothes Color"]),
    "Project/Character/Jodi/Jodi": ("Jodi", ["Save Appearance", "Is Input Enabled ?"]),
    "Project/Classes/GameMode/TKA_GameState_Base": ("TKA_GameState_Base", ["Get Wardrobe Data", "Pop Attention"]),
    "Project/Classes/TKA_Controller": ("TKA_Controller", ["ShowMouseCursor", "Set Widget Focus", "Enable Player Control"]),
    "Project/Classes/Misc/WardrobeData": ("WardrobeData", ["Has This Clothes"]),
    "Project/Classes/Misc/Clothes_Comp": ("Clothes_Comp", ["Change Color"]),
}


def strip_mod(p):
    return re.sub(r"^(out |ref |const& )", "", p)


def api_sigs(name):
    sigs = {}
    for line in open(os.path.join(API_DIR, name + ".txt")):
        m = re.match(r"  (.+?)\s{2,}\((.*)\)(?: -> (.*?))?\s+\[", line.rstrip("\n"))
        if not m: continue
        params = [p.strip() for p in m.group(2).split(", ") if p.strip()]
        types = [strip_mod(p).split(": ", 1)[1] for p in params]
        sigs[m.group(1)] = types + ([m.group(3)] if m.group(3) else [])
    return sigs


errors = 0
for rel, (api, funcs) in STUBS.items():
    path = os.path.join(COOKED, rel + ".uasset")
    if not os.path.exists(path):
        print("MISSING cooked stub", path); errors += 1; continue
    res = uasset_funcs.dump(path); real = api_sigs(api)
    for fn in funcs:
        if fn not in res["functions"]:
            print("STUB LACKS", api, fn); errors += 1; continue
        f = res["functions"][fn]
        mine = [strip_mod(p).split(": ", 1)[1] for p in f["params"]] + ([f["ret"]] if f["ret"] else [])
        if fn not in real:
            print("API LACKS", api, fn); errors += 1; continue
        if mine != real[fn]:
            print("MISMATCH", api, fn, "\n   stub:", mine, "\n   game:", real[fn]); errors += 1
        else:
            print("ok", api, fn, mine)
print("VERIFY STUBS", "FAILED" if errors else "OK")
sys.exit(1 if errors else 0)
