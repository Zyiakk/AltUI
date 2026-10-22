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
    "Project/Classes/Character_Player_Base": ("Character_Player_Base", ["Wear The Clothes", "Take off this clothes", "Get Wearing Clothes Names", "is clothes wearing", "Find Clothes Component With Name", "Get Clothes Color", "Save Clothes Color", "Restore Clothes Color", "Is Wanna Run ?", "Change Wanna Run",
                                                                     "Put Item to Bag", "Consume Item", "Got A Gun", "Drop Item", "Equip This Weapon", "Has This Item",   # inventory tab
                                                                     "Get Weapon In Hand",   # body switch: the weapon in hand back on its socket
                                                                     "Get Clothes Damage", "Store Clothes Damage",   # damage slider in the clothes menu
                                                                     "Change Hairstyle Ex", "check clothes covering",   # followers: the game's hair, the underwear rule
                                                                     "Count Weapon Ammo",   # followers: infinite ammo
                                                                     "Character Die", "Play Montage", "Attach Weapon to Right Hand"]),   # Jason: his death; any weapon with his montages   # Jason: his death past Character_NPC's
    "Project/Classes/Character_Base": ("Character_Base", ["Is Crouching"]),   # walk / run speed (BP_AltUIMove)
    "Project/Character/Jodi/Jodi": ("Jodi", ["Save Appearance", "Is Input Enabled ?", "Wanna Running", "Wanna Use This Item", "Add Item to Shortcut"]),
    "Project/Character/Jodi/Jodi_Base": ("Jodi_Base", ["Get Makeup Data", "Update Makeup Texture", "Load Player Makeup"]),
    "Project/Classes/GameMode/TKA_GameState_Base": ("TKA_GameState_Base", ["Get Wardrobe Data", "Pop Attention", "Get Attention UI"]),
    "Project/Classes/TKA_Controller": ("TKA_Controller", ["ShowMouseCursor", "Set Widget Focus", "Enable Player Control"]),
    "Project/Classes/Misc/WardrobeData": ("WardrobeData", ["Has This Clothes"]),
    "Project/Classes/Misc/Clothes_Comp": ("Clothes_Comp", ["Change Color", "Change Damage", "Is Damaged"]),
    "Project/Classes/Misc/Hair_Comp": ("Hair_Comp", ["Change Color"]),
    "Project/Classes/Misc/InvisibleHand_Comp": ("InvisibleHand_Comp", ["Update Power"]),
    "Project/Classes/GameMode/TKA_GameState": ("TKA_GameState", ["Get Note Save", "Get Hyper Box Data", "Is Game Over ?"]),   # Kodex: the encyclopedia's unlock list
    "Project/Classes/Items/ItemComponent": ("ItemComponent", ["Is Locked"]),
    "Project/Maps/JodisOffice/TV/TV_Actor": ("TV_Actor", ["On Use This", "Play Video", "Start Animation"]),   # TV tab   # Kodex: lock state of a code lock
    # inventory tab: backpack, storage box, weapon, item detail
    "Project/Classes/Misc/Bag_Comp": ("Bag_Comp", ["Count Items", "Can I Pickup This Item ?", "Add Clothes To Bag", "Remove Clothes", "Append Clothes"]),
    "Project/Classes/Misc/HyperBoxData": ("HyperBoxData", ["Add Item", "Consume Item Count", "Save", "Count Items", "Add a Gun", "Remove a Gun"]),
    "Project/Actors/Weapons/Weapon_Base": ("Weapon_Base", ["Unload Ammo", "Attach to Hand", "Set Visible", "Get Ammo Name", "Get Player Montage"]),   # body switch: Attach to Hand, Set Visible
    "Project/Actors/Weapons/Weapon_Gun_Base": ("Weapon_Gun_Base", ["Mount Equipment", "Apply Extra Attributes", "Change Gun Paint", "Mark to Need Update Anim"]),   # weapons tab: attachments; body switch
    "Project/UserInterface/PlayingHud": ("PlayingHud", ["Show Item Detail with Name"]),
    "Project/Character/Jason/Jason": ("Jason", ["Got Glock"]),   # Jason: a given Glock becomes his own
    "Project/Character/Npc/Character_NPC": ("Character_NPC", ["Need to Save", "Mutate", "on Spawn in Runtime", "Ani Notify Grab Weapon"]),   # followers: the child says no / never mutates
    "Project/Character/Npc/NPC_Female": ("NPC_Female", ["delay to mutant", "Apply Npc Appearance"]),
    "Project/Classes/Controller/Npc_Controller": ("Npc_Controller", ["Change Order", "Receive Order", "Decide Next State"]),   # followers: NpcFollow / NpcStay
}


def strip_mod(p):
    return re.sub(r"^(out |ref |const& )", "", p)


VARS = {  # cooked stub -> (API dump, checked variables: name and type must match the game)
    "Project/Character/Jodi/Jodi": ("Jodi", ["previous weapon", "wanna toggle weapon", "Settings", "InvisibleHand_Comp"]),   # inventory tab: auto-equip option (Inv Got Gun)
    "Project/Classes/Controller/Npc_Controller": ("Npc_Controller", ["master"]),   # followers
    "Project/Character/Npc/NPC_Female": ("NPC_Female", ["save order", "Order Location"]),
    "Project/Character/Jason/Jason": ("Jason", ["State"]),   # Jason prototype
    "Project/Classes/Misc/InvisibleHand_Comp": ("InvisibleHand_Comp", ["Number"]),   # catalog: the invisible hand (Hand Watch)
    "Project/Classes/Character_Base": ("Character_Base", ["Health", "Anim Blueprint"]),
    "Project/Classes/TKA_Controller": ("TKA_Controller", ["Input Move Values"]),   # idle pose: raw move input
    "Project/UserInterface/PlayingHud": ("PlayingHud", ["InventoryNpc"]),   # followers: Fol Watch (the game's swap dialog)
    "Project/Classes/Character_Player_Base": ("Character_Player_Base", ["Bag", "Weapons", "Save Player Clothes", "Save Clothes Damaged", "Hair Comps", "clothes component list", "in hand weapon"]),   # followers: fallen when Health <= 0; anim instance after the body swap
}


def api_vars(name):
    out = {}
    for line in open(os.path.join(API_DIR, name + ".txt")):
        m = re.match(r"  var (.+?)\s{2,}(\S+)", line.rstrip("\n"))
        if m: out[m.group(1)] = m.group(2)
    return out


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
for rel, (api, names) in VARS.items():
    path = os.path.join(COOKED, rel + ".uasset")
    if not os.path.exists(path):
        print("MISSING cooked stub", path); errors += 1; continue
    mine = {v["name"]: v["type"] for v in (uasset_funcs.dump(path).get("class") or {}).get("vars", [])}; real = api_vars(api)
    for n in names:
        if n not in mine: print("STUB LACKS var", api, n); errors += 1
        elif n not in real: print("API LACKS var", api, n); errors += 1
        elif mine[n] != real[n]: print("MISMATCH var", api, n, "stub:", mine[n], "game:", real[n]); errors += 1
        else: print("ok var", api, n, mine[n])
print("VERIFY STUBS", "FAILED" if errors else "OK")
sys.exit(1 if errors else 0)
