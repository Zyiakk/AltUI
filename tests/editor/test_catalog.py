import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def items(mgr, slot):
    mgr.call_method("Test Items", args=(slot,))
    return [str(n) for n in mgr.get_editor_property("TmpNames")]

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Build")
    slots = [str(s) for s in mgr.get_editor_property("Slots")]
    expect("slots first", slots[:3], ["Bra", "Shirt", "Top"])
    expect("slots count", len(slots), 34)
    expect("slots last", slots[-1], "Unknown")
    expect("count Briefs", len(items(mgr, "Briefs")), 1)
    expect("count Neck", len(items(mgr, "Neck")), 3)
    expect("count Unknown", len(items(mgr, "Unknown")), 1)
    expect("count empty slot", len(items(mgr, "Bra")), 0)
    expect("neck order", items(mgr, "Neck"), ["Alpha_Neck", "Casual_Mina_Neck", "Zeta_Neck"])
    expect("item group", str(mgr.get_editor_property("TmpName")), "Kpop")
    expect("item vanilla", mgr.get_editor_property("TmpFound"), True)
    expect("socks order (binary insert, equal keys in table order)", items(mgr, "Socks"),
           ["Sock_a", "Sock_b", "Sock_c", "Sock_d", "Sock_e", "Sock_f", "Sock_g", "Sock_Same_Prefix_Twenty4_B", "Sock_Same_Prefix_Twenty4_A"])
    expect("all = slots in order", len(items(mgr, "All")), 18)
    counts = {str(k): v for k, v in mgr.get_editor_property("SlotCounts").items()}
    expect("slot counts", (counts.get("Socks"), counts.get("Neck"), counts.get("All"), counts.get("Bra")), (9, 3, 18, 0))
    mgr.call_method("Test Sort Key", args=("a",)); ka = mgr.get_editor_property("TmpKey")
    mgr.call_method("Test Sort Key", args=("b",)); kb = mgr.get_editor_property("TmpKey")
    report("sortkey a<b", ka < kb, (ka, kb))
    mgr.call_method("Test Sort Key", args=("Casual_Mina_Neck",)); k1 = mgr.get_editor_property("TmpKey")
    mgr.call_method("Test Sort Key", args=("Casual_Mina_Necklace",)); k2 = mgr.get_editor_property("TmpKey")
    report("sortkey prefix equal (12 chars)", k1 == k2, (k1, k2))
    mgr.call_method("Test Sort Key", args=("Neck",)); k3 = mgr.get_editor_property("TmpKey")
    mgr.call_method("Test Sort Key", args=("Necklace",)); k4 = mgr.get_editor_property("TmpKey")
    report("sortkey2 tail", k3 < k4, (k3, k4))
    islot = {str(k): str(v) for k, v in mgr.get_editor_property("ItemSlot").items()}
    expect("item slot map", islot.get("SpikeBoots"), "Boots")
    expect("catalog rows", mgr.get_editor_property("CatalogRows"), 18)   # 17 vanilla stub rows + ModThing from the SomeMod stub table
    mgr.set_editor_property("Worn", ["SpikeBoots", "Zeta_Neck"])
    mgr.call_method("Test Worn In Slot", args=("Neck",)); expect("worn in slot", str(mgr.get_editor_property("TmpName")), "Zeta_Neck")
    mgr.call_method("Test Worn In Slot", args=("Bra",)); expect("worn in empty slot", str(mgr.get_editor_property("TmpName")), "None")
run(main)
