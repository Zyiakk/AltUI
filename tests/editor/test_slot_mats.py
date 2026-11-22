"""Material swap, core (spec 2026-11-17-material-tausch-design): resolving a source, the SlotMats store and what the swap does to
the colourable slots. Putting a material on the worn component needs Jodi - that is the game test."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"
FEMALE = "/Game/Project/Character/Jodi/Body/Female"   # the mesh the stub row Briefs03 points at

DEFAULT = "/Engine/EngineMaterials/DefaultMaterial"
SHADER = "/Game/Project/Material/ShaderClothes"
OVERRIDE, OVERRIDE_MAT = "AltUITestOverride", "/Game/Project/Editor/axis_red.axis_red"   # gen_stubs.py: Briefs03's row override


def slots(mgr, name):
    mgr.call_method("Test Color Slots", args=(name,))
    return mgr.get_editor_property("TmpI"), [str(n) for n in mgr.get_editor_property("TmpNames")]


def set_materials(mesh, pairs):
    """Give the kit mesh material slots in memory (nothing is saved)."""
    mesh.set_editor_property("materials", [unreal.SkeletalMaterial(material_interface=m, material_slot_name=n) for n, m in pairs])


def resolve(mgr, source):
    mgr.call_method("Test Mat Of Slot", args=(source,))
    mat = mgr.get_editor_property("MatTmp")
    return mgr.get_editor_property("TmpBool"), (mat.get_path_name() if mat else None)


def has_own_mat(mgr, name):
    mgr.call_method("Test Has Own Mat", args=(name,))
    return mgr.get_editor_property("TmpBool")


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    plain, shader = unreal.load_asset(DEFAULT), unreal.load_asset(SHADER)
    # a copy: get_editor_property hands out the live array, which the set_materials below would overwrite (and the restore at the end
    # would then leave the test slots on the mesh for the next test file - test_colors reads the mesh's slots)
    mesh = unreal.load_asset(FEMALE); before = [unreal.SkeletalMaterial(material_interface=m.get_editor_property("material_interface"),
        material_slot_name=m.get_editor_property("material_slot_name")) for m in mesh.get_editor_property("materials")]
    set_materials(mesh, [("Metal", plain), ("Body", shader)])
    mgr.call_method("Test Build"); mgr.set_editor_property("SlotMats", {})
    # resolution
    expect("slot 1 resolves to its material", resolve(mgr, "Briefs03#1"), (True, shader.get_path_name()))
    expect("slot 0 resolves to its material", resolve(mgr, "Briefs03#0"), (True, plain.get_path_name()))
    expect("a missing piece does not resolve", resolve(mgr, "Nope#0")[0], False)
    expect("a slot beyond the mesh does not", resolve(mgr, "Briefs03#7")[0], False)
    expect("no '#' does not", resolve(mgr, "Briefs03")[0], False)
    # all slots, whatever the material takes
    mgr.call_method("Test Mat Slots", args=("Briefs03",))
    expect("every slot is listed", [str(n) for n in mgr.get_editor_property("TmpNames")], ["Metal", "Body"])
    # colourable slots before / after a swap
    mgr.call_method("Test Build")
    expect("only the shader slot takes a colour", slots(mgr, "Briefs03")[1], ["Body"])
    expect("nothing swapped yet", has_own_mat(mgr, "Briefs03"), False)
    mgr.call_method("Test Slot Set Mat", args=("Briefs03", 0, "Briefs03#1"))
    expect("the swap is stored", {str(k): v for k, v in mgr.get_editor_property("SlotMats").items()}, {"Briefs03#0": "Briefs03#1"})
    expect("the piece has a swap", has_own_mat(mgr, "Briefs03"), True)
    expect("the swapped slot is probed with its new material", slots(mgr, "Briefs03")[1], ["Metal", "Body"])
    # a source that does not resolve: the entry stays, the slot is left as it is
    mgr.call_method("Test Slot Set Mat", args=("Briefs03", 0, "Nope#0"))
    expect("a missing source keeps its entry", {str(k): v for k, v in mgr.get_editor_property("SlotMats").items()}, {"Briefs03#0": "Nope#0"})
    expect("and the slot keeps its own material", slots(mgr, "Briefs03")[1], ["Body"])
    # reset
    mgr.call_method("Test Slot Reset Mat", args=("Briefs03", 0))
    expect("the reset drops the entry", len(mgr.get_editor_property("SlotMats")), 0)
    expect("no swap left", has_own_mat(mgr, "Briefs03"), False)
    expect("colourable slots as before", slots(mgr, "Briefs03")[1], ["Body"])
    # the picker on the clothes page (Open Mat Picker / a tile's material menu / a row of it / target chip / ✕ / Close Mat Picker): the
    # list is never rebuilt for any of them - CloKind / CloItems stay exactly as they were
    mgr.call_method("Test Build"); mgr.set_editor_property("SlotMats", {}); mgr.set_editor_property("UndoStack", [])
    mgr.set_editor_property("Page", "Clothes"); mgr.set_editor_property("CurrentSlot", "All"); mgr.set_editor_property("CurrentGroup", "None")
    mgr.set_editor_property("SearchText", ""); mgr.set_editor_property("Worn", ["Briefs03"])
    mgr.call_method("Test Open Mat Picker", args=("Briefs03",))
    expect("picking Briefs03", str(mgr.get_editor_property("MatPickTarget")), "Briefs03")
    expect("first slot active", mgr.get_editor_property("MatPickSlot"), 0)
    expect("came from the clothes page", str(mgr.get_editor_property("MatPickBack")), "Clothes")
    def listed():   # entries, and the flag every Rebuild List sets (the list's rows are measured anew)
        return (list(mgr.get_editor_property("CloKind")), list(mgr.get_editor_property("CloRef")), len(mgr.get_editor_property("CloItems")),
                mgr.get_editor_property("CloRowsDirty"))
    def menu(name):   # the rows of the tile's material menu (Mat Pick Row per material slot, as Open Mat Pick Menu builds them; the
        # menu widget needs a world the commandlet has not): (action, caption)
        mgr.call_method("Test Mat Pick Rows", args=(name,))
        return list(zip([str(a) for a in mgr.get_editor_property("TmpStrings")], [str(c) for c in mgr.get_editor_property("TmpStrings2")]))
    mgr.set_editor_property("CloRowsDirty", False); before_list = listed()
    expect("the list has entries", len(before_list[0]) > 0, True)
    same = lambda: listed() == before_list
    mgr.call_method("Test Item Clicked", args=("Briefs03",))
    expect("still worn (no wear / take off)", [str(n) for n in mgr.get_editor_property("Worn")], ["Briefs03"])
    expect("no undo step for opening the menu", len(mgr.get_editor_property("UndoStack")), 0)
    expect("the list is unchanged after a tile click", same(), True)
    mgr.call_method("Test Mat Slots", args=("Briefs03",)); caps = [str(c) for c in mgr.get_editor_property("TmpNames")]
    expect("the menu: one row per material slot of the tile, the own slot on the active slot marked", menu("Briefs03"),
           [("MatPick:Briefs03#0", "> " + caps[0]), ("MatPick:Briefs03#1", "   " + caps[1])])
    expect("a piece without material slots: no rows", menu("Nope"), [])
    mgr.call_method("Test Menu Action", args=("MatPick:Briefs03#1",))
    expect("the row swaps the active slot", {str(k): v for k, v in mgr.get_editor_property("SlotMats").items()}, {"Briefs03#0": "Briefs03#1"})
    expect("one undo step", len(mgr.get_editor_property("UndoStack")), 1)
    expect("the list is unchanged after a row", same(), True)
    expect("the picker stays open", str(mgr.get_editor_property("MatPickTarget")), "Briefs03")
    expect("the mark moves to the chosen row", menu("Briefs03"), [("MatPick:Briefs03#0", "   " + caps[0]), ("MatPick:Briefs03#1", "> " + caps[1])])
    mgr.call_method("Test Menu Action", args=("MatSlot:1",))
    expect("a target chip sets the active slot", mgr.get_editor_property("MatPickSlot"), 1)
    expect("active slot 1 has no swap: its own material marked", menu("Briefs03"),
           [("MatPick:Briefs03#0", "   " + caps[0]), ("MatPick:Briefs03#1", "> " + caps[1])])
    mgr.call_method("Test Menu Action", args=("MatSlot:0",)); mgr.call_method("Test Menu Action", args=("MatPick:Briefs03#0",))
    expect("the own material on its own slot resets the slot", {str(k): v for k, v in mgr.get_editor_property("SlotMats").items()}, {})
    expect("and marked", menu("Briefs03")[0], ("MatPick:Briefs03#0", "> " + caps[0]))
    mgr.call_method("Test Menu Action", args=("MatX:0",))
    expect("the ✕ leaves the slot reset", len(mgr.get_editor_property("SlotMats")), 0)
    expect("one undo step per row and ✕", len(mgr.get_editor_property("UndoStack")), 3)
    expect("the list is unchanged after target chip and ✕", same(), True)
    mgr.call_method("Test Close Mat Picker")
    expect("closed", str(mgr.get_editor_property("MatPickTarget")), "None")
    # the target taken off: the next rebuild ends the picker
    mgr.call_method("Test Open Mat Picker", args=("Briefs03",)); mgr.set_editor_property("Worn", [])
    mgr.set_editor_property("SearchText", "x"); mgr.call_method("Test Menu Action", args=("ClearSearch",))   # any Rebuild List (in the game: the one of Take Off)
    expect("taken off closes the picker", str(mgr.get_editor_property("MatPickTarget")), "None")
    expect("(a rebuild does set the flag the checks above watch)", mgr.get_editor_property("CloRowsDirty"), True)
    # the row's material override (colour variants, play test 2026-11-18): the stub row Briefs03 overrides slot OVERRIDE with axis_red,
    # an instance that takes MainColor - the slot's own material is that one, not the mesh's plain material
    set_materials(mesh, [("Metal", plain), ("Body", shader), (OVERRIDE, plain)])
    mgr.call_method("Test Build"); mgr.set_editor_property("SlotMats", {})
    expect("an overridden slot resolves to the row's material", resolve(mgr, "Briefs03#2"), (True, OVERRIDE_MAT))
    expect("the other slots keep the mesh's", (resolve(mgr, "Briefs03#0")[1], resolve(mgr, "Briefs03#1")[1]), (plain.get_path_name(), shader.get_path_name()))
    expect("the colour probe uses the override too", slots(mgr, "Briefs03")[1], ["Body", OVERRIDE])
    mgr.call_method("Test Mat Slots", args=("Briefs03",))
    expect("every slot is still listed", [str(n) for n in mgr.get_editor_property("TmpNames")], ["Metal", "Body", OVERRIDE])
    mesh.set_editor_property("materials", before)
    mgr.set_editor_property("SlotMats", {}); mgr.set_editor_property("UndoStack", [])


run(main)
