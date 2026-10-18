"""Several pieces in one slot (Options > Slot conflicts > "several pieces", MultiSlots). Shared by the manager and BP_AltUIFollower.

The game wears a piece in Character_Player_Base.Wear The Clothes: new Clothes_Comp, Wear(row, ...), then - unless the slot's Flag & 1
(only Acc) - Get Clothes Component(slot) and off with it. That lookup goes by Clothes_Comp.Type; the new comp is appended last, so it
finds the old one. Wear Kept hides the slot's worn comps under HELD_TYPE for that one call and gives them their slot back after:
everything else of the game's wearing (colour, damage, heels, body mask, Wear Clothes Last) stays. The game's own loads (Wear These
Clothes) keep only one piece per slot - the callers put the others on again (Restore Multi Worn, the follower's Check Appearence).
Notes: docs/notes/2026-10-18-mehrere-teile-pro-slot.md."""
from bpdsl import *

HELD_TYPE = "AltUIHeld"   # no slot of the game's ClothesTypeTable


def f_hold_slot():
    """The comps worn in the slot of `name` (com_ClothesTable.TypeName) under HELD_TYPE, remembered in HeldComps (Release Held)."""
    g = G(); g.get("gh0", "HeldComps"); g.call("hc0", K_ARR, "Array_Clear", inp={"TargetArray": "@gh0.HeldComps"}); g.set("sht", "HeldType", inp={"HeldType": "None"})
    g.n("row", "get_row", table=P_CT, inp={"RowName": "@entry.name"}, miss="ignore"); g.brk("br", P_CS, "@row.OutRow"); g.set("sty", "HeldType", inp={"HeldType": "@br.TypeName"})
    g.get("gcl", "clothes component list", cls=P_CPB); g.link("entry.char", "gcl.self"); g.foreach("fc", "@gcl.clothes component list")
    g.get("gty", "Type", cls=P_CC); g.link("fc.Array Element", "gty.self"); g.get("ght", "HeldType")
    g.call("eq", K_MATH, "EqualEqual_NameName", inp={"A": "@gty.Type", "B": "@ght.HeldType"}); g.branch("beq", "@eq.ReturnValue")
    g.get("gh1", "HeldComps"); g.call("ha", K_ARR, "Array_Add", inp={"TargetArray": "@gh1.HeldComps", "NewItem": "@fc.Array Element"})
    g.n("sh", "set", var="Type", cls=P_CC, inp={"self": "@fc.Array Element", "Type": HELD_TYPE})
    g.chain("entry", "hc0", "sht", "row", "sty", "fc"); g.chain("fc", "beq", "ha", "sh")
    return fn("Hold Slot", [param("char", "object:" + P_CPB), param("name", "name")], graph=g)


def f_release_held():
    """The held comps get their slot back."""
    g = G(); g.get("gh", "HeldComps"); g.foreach("fb", "@gh.HeldComps"); g.get("ght", "HeldType")
    g.n("sb", "set", var="Type", cls=P_CC, inp={"self": "@fb.Array Element", "Type": "@ght.HeldType"})
    g.get("gh2", "HeldComps"); g.call("hc", K_ARR, "Array_Clear", inp={"TargetArray": "@gh2.HeldComps"})
    g.chain("entry", "fb"); g.chain("fb", "sb"); g.chain("fb:Completed", "hc")
    return fn("Release Held", graph=g)


def f_clear_slot_for():
    """Before `name` goes on without keep: every piece worn in its slot off (the game's slot rule takes off only the first - two pieces
    left from keep would stay two). Not in a slot the game lets hold several itself (ClothesTypeTable Flag & 1: Acc), not for a
    piece worn already (Wear The Clothes only redoes its mask), not for a piece outside com_ClothesTable."""
    g = G(); g.n("row", "get_row", table=P_CT, inp={"RowName": "@entry.name"}, miss="ignore"); g.brk("br", P_CS, "@row.OutRow")
    g.n("trow", "get_row", table=P_CTT, inp={"RowName": "@br.TypeName"}, miss="ignore"); g.brk("tbr", P_CTS, "@trow.OutRow")
    g.call("fa", K_MATH, "And_IntInt", inp={"A": "@tbr.Flag", "B": "1"}); g.call("f0", K_MATH, "EqualEqual_IntInt", inp={"A": "@fa.ReturnValue", "B": "0"})
    g.call("iw", P_CPB, "is clothes wearing", inp={"self": "@entry.char", "clothes name": "@entry.name"}); g.call("nw", K_MATH, "Not_PreBool", inp={"A": "@iw.yes"})
    g.call("one", K_MATH, "BooleanAND", inp={"A": "@f0.ReturnValue", "B": "@nw.ReturnValue"}); g.branch("bone", "@one.ReturnValue")
    g.n("tsa", "call_self", function="Take Off Slot All", inp={"char": "@entry.char", "slot": "@br.TypeName"})
    g.chain("entry", "row", "trow", "bone", "tsa")
    return fn("Clear Slot For", [param("char", "object:" + P_CPB), param("name", "name")], graph=g)


def f_wear_kept():
    """Wear The Clothes on `char`. keep = the pieces already worn in the piece's slot stay on; otherwise Clear Slot For first."""
    g = G(); g.branch("bk", "@entry.keep"); g.n("hs", "call_self", function="Hold Slot", inp={"char": "@entry.char", "name": "@entry.name"})
    g.n("csf", "call_self", function="Clear Slot For", inp={"char": "@entry.char", "name": "@entry.name"})
    g.call("w", P_CPB, "Wear The Clothes", inp={"self": "@entry.char", "name": "@entry.name", "check covering": "@entry.check covering", "update mask": "@entry.update mask",
                                                 "ignore compatible": "@entry.ignore compatible"})
    g.n("rh", "call_self", function="Release Held"); g.branch("bk2", "@entry.keep")
    g.link("w.successed", "return.successed")
    g.chain("entry", "bk", "hs", "w", "bk2", "rh", "return"); g.chain("bk2:else", "return"); g.chain("bk:else", "csf", "w")
    return fn("Wear Kept", [param("char", "object:" + P_CPB), param("name", "name"), param("check covering", "bool"), param("update mask", "bool"),
                            param("ignore compatible", "bool"), param("keep", "bool")], [param("successed", "bool")], graph=g)


def f_take_off_slot_all():
    """Every worn piece of `slot` off `char` (the game's take off clothes finds only the first), no covering check / body mask."""
    g = G(); g.get("gcl", "clothes component list", cls=P_CPB); g.link("entry.char", "gcl.self")
    g.set("cp", "HeldComps", inp={"HeldComps": "@gcl.clothes component list"}); g.get("gh", "HeldComps"); g.foreach("fc", "@gh.HeldComps")   # a copy: the list shrinks
    g.get("gty", "Type", cls=P_CC); g.link("fc.Array Element", "gty.self"); g.call("eq", K_MATH, "EqualEqual_NameName", inp={"A": "@gty.Type", "B": "@entry.slot"}); g.branch("beq", "@eq.ReturnValue")
    g.call("to", P_CPB, "Take Off Clothes And Remove Component", inp={"self": "@entry.char", "comp": "@fc.Array Element"})
    g.get("gh2", "HeldComps"); g.call("hc", K_ARR, "Array_Clear", inp={"TargetArray": "@gh2.HeldComps"})
    g.chain("entry", "cp", "fc"); g.chain("fc", "beq", "to"); g.chain("fc:Completed", "hc")
    return fn("Take Off Slot All", [param("char", "object:" + P_CPB), param("slot", "name")], graph=g)


def held_vars():
    return [var("HeldComps", "object:" + P_CC, "array"), var("HeldType", "name")]


def functions():
    return [f_hold_slot(), f_release_held(), f_clear_slot_for(), f_wear_kept(), f_take_off_slot_all()]
