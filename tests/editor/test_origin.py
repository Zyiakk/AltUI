import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

# ItemOriginMod has one key per table ("<kind>:<row>"): equal row names in different tables belong to different mods
# (2026-10-10: Iris eyes 1..20 showed as brefg's poses, whose AnimationTable has rows 1, 2, ... too).
def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Build"); mgr.call_method("Test Strings", args=(1,)); mgr.call_method("Test Load Names")
    def om(kind, row):
        mgr.call_method("Test Origin Mod", args=(kind, row)); return (mgr.get_editor_property("TmpBool"), str(mgr.get_editor_property("TmpName")))
    def ctx(kind, row):
        mgr.call_method("Test Context Mod", args=(kind, row)); return str(mgr.get_editor_property("TmpName"))
    def manage_mod(kind, row):
        mgr.call_method("Test Manage Origin", args=(kind, row)); return str(mgr.get_editor_property("TmpMod"))
    # scan of the stub mod SomeMod: clothes ModThing, pose ModPose, eye ModThing, make-up Skin_Default (a vanilla skin's name)
    expect("clothes row", om("item", "ModThing"), (True, "SomeMod"))
    expect("pose row", om("pose", "ModPose"), (True, "SomeMod"))
    expect("pose row is no clothes piece", om("item", "ModPose")[0], False)
    expect("eye row with a clothes name", om("eye", "ModThing"), (True, "SomeMod"))
    expect("eye row on the appearance page", om("look", "ModThing"), (True, "SomeMod"))
    expect("make-up row", om("makeup", "Skin_Default"), (True, "SomeMod"))
    expect("appearance page: the vanilla skin wins over the make-up row", om("look", "Skin_Default")[0], False)
    expect("vanilla skin", om("skin", "Skin_Default")[0], False)
    # the same row in two tables of two mods (the reported case)
    origin = mgr.get_editor_property("ItemOriginMod")
    origin["eye:Twin"] = "ModEyes"; origin["look:Twin"] = "ModEyes"; origin["pose:Twin"] = "ModPoses"; origin["item:Twin"] = "ModClothes"; origin["hair:Twin"] = "ModHair"
    mgr.set_editor_property("ItemOriginMod", origin)
    expect("per table", (om("eye", "Twin")[1], om("pose", "Twin")[1], om("item", "Twin")[1], om("hair", "Twin")[1]), ("ModEyes", "ModPoses", "ModClothes", "ModHair"))
    expect("context menu follows its kind", (ctx("look", "Twin"), ctx("pose", "Twin"), ctx("item", "Twin"), ctx("hair", "Twin")), ("ModEyes", "ModPoses", "ModClothes", "ModHair"))
    expect("manage rows follow their kind", (manage_mod("makeup", "Twin"), manage_mod("pose", "Twin"), manage_mod("item", "Twin"), manage_mod("hair", "Twin")), ("ModEyes", "ModPoses", "ModClothes", "ModHair"))
    expect("skin tiles read the appearance key", manage_mod("skin", "Twin"), "ModEyes")   # skin and make-up rows share the appearance page's name space (look:)
    for k in ("eye:Twin", "look:Twin", "pose:Twin", "item:Twin", "hair:Twin"): del origin[k]
    mgr.set_editor_property("ItemOriginMod", origin)
    mgr.call_method("Test Context Mod", args=("item", "None"))   # ContextOriginKind back to its default
    # AltUI_ModScan.sav (Test Build scanned and saved it): the same mods -> the saved origins, without a scan
    origin = mgr.get_editor_property("ItemOriginMod"); n0 = len(origin)
    mgr.set_editor_property("ItemOriginMod", {})
    mgr.call_method("Test Mod Origins")
    expect("saved scan used", mgr.get_editor_property("TmpBool"), True)
    expect("saved origins", (len(mgr.get_editor_property("ItemOriginMod")), om("item", "ModThing")), (n0, (True, "SomeMod")))
    # a changed mod line (e.g. a mod's caption, version or Tables) -> scan again, then the new result is saved
    sv = unreal.GameplayStatics.load_game_from_slot("AltUI_ModScan", 0)
    sig = list(sv.get_editor_property("Sig")); sig[0] = sig[0] + "x"; sv.set_editor_property("Sig", sig)
    unreal.GameplayStatics.save_game_to_slot(sv, "AltUI_ModScan", 0)
    mgr.call_method("Test Mod Origins")
    expect("changed mod line: scanned", (mgr.get_editor_property("TmpBool"), om("item", "ModThing")), (False, (True, "SomeMod")))
    mgr.call_method("Test Mod Origins")
    expect("rescan saved", mgr.get_editor_property("TmpBool"), True)
    # a changed row list of a game table -> scan again
    sv = unreal.GameplayStatics.load_game_from_slot("AltUI_ModScan", 0)
    rows = sv.get_editor_property("Rows"); rows[unreal.Name("pose")] = rows[unreal.Name("eye")]; sv.set_editor_property("Rows", rows)   # other row names
    unreal.GameplayStatics.save_game_to_slot(sv, "AltUI_ModScan", 0)
    mgr.call_method("Test Mod Origins")
    expect("changed rows: scanned", mgr.get_editor_property("TmpBool"), False)
    # a changed number of clothes rows with a mod mesh -> scan again
    sv = unreal.GameplayStatics.load_game_from_slot("AltUI_ModScan", 0); sv.set_editor_property("MeshN", sv.get_editor_property("MeshN") + 1)
    unreal.GameplayStatics.save_game_to_slot(sv, "AltUI_ModScan", 0)
    mgr.call_method("Test Mod Origins")
    expect("changed mod meshes: scanned", mgr.get_editor_property("TmpBool"), False)
    # the mods' file index (Mod File Index, 2026-11-15): kept while the mod list is the same, the origins' saves leave it in the file
    mgr.call_method("Test Mod File Index")
    expect("file index from the save", mgr.get_editor_property("TmpBool"), True)
    sv = unreal.GameplayStatics.load_game_from_slot("AltUI_ModScan", 0)
    fs = list(sv.get_editor_property("FileSig")); fs[0] = fs[0] + "x"; sv.set_editor_property("FileSig", fs)
    unreal.GameplayStatics.save_game_to_slot(sv, "AltUI_ModScan", 0)
    mgr.call_method("Test Mod File Index")
    expect("changed mod list: files looked up again", mgr.get_editor_property("TmpBool"), False)
    mgr.call_method("Test Mod File Index")
    expect("new file index saved", mgr.get_editor_property("TmpBool"), True)
    mgr.call_method("Test Mod Origins")
    expect("origins kept beside it", mgr.get_editor_property("TmpBool"), True)
run(main)
