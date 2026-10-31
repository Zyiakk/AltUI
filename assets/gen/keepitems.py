"""Keep pieces through look / outfit changes (spec docs/superpowers/specs/2026-10-24-keep-items-design.md).

KeepItems: the pieces marked "keep" in the clothes context menu (saved; only the menu changes it). SnapWorn: worn pieces a
look or an outfit put on (saved). Apply Snapshot with keep = true (looks, outfits) leaves every worn piece that is marked and
not in SnapWorn - one the player put on - and skips the snapshot's pieces that would push it off. Undo / redo and ragdolls
pass keep = false and restore exactly."""
from bpdsl import *


def f_is_kept_item():
    g = G()
    g.get("g", "KeepItems"); g.call("c", K_ARR, "Array_Contains", inp={"TargetArray": "@g.KeepItems", "ItemToFind": "@entry.name"})
    g.link("c.ReturnValue", "return.yes")
    return fn("Is Kept Item", [param("name", "name")], [param("yes", "bool")], graph=g, pure=True)


def f_toggle_keep_item():
    g = G()
    g.n("isk", "call_self", function="Is Kept Item", inp={"name": "@entry.name"}); g.branch("b", "@isk.yes")
    g.get("gk", "KeepItems"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gk.KeepItems", "Item": "@entry.name"})
    g.get("gk2", "KeepItems"); g.call("add", K_ARR, "Array_AddUnique", inp={"TargetArray": "@gk2.KeepItems", "NewItem": "@entry.name"})
    g.n("sv", "call_self", function="Save Settings")
    g.get("go", "PanelOpen"); g.branch("bo", "@go.PanelOpen"); g.n("rl", "call_self", function="Rebuild List")
    g.chain("entry", "b", "rm", "sv"); g.chain("b:else", "add", "sv"); g.chain("sv", "bo", "rl")
    return fn("Toggle Keep Item", [param("name", "name")], graph=g)


def f_note_self_worn():
    """The player put the piece on or took it off by hand: it is no look's any more (saved soon, so a restart keeps that)."""
    g = G(); g.get("gs", "SnapWorn"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gs.SnapWorn", "Item": "@entry.name"})
    g.branch("b", "@rm.ReturnValue")   # true = it was there
    g.n("sv", "call_self", function="Save Settings Soon")
    g.chain("entry", "rm", "b", "sv"); return fn("Note Self Worn", [param("name", "name")], graph=g)


def f_collect_kept():
    """Start of Apply Snapshot (after Refresh State): SnapWorn loses what is not worn any more (taken off on any way - here Jodi
    is surely dressed, unlike a check while a level loads). KeptOn = worn, marked, not put on by a look; empty without keep."""
    g = G(); g.get("gk0", "KeptOn"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gk0.KeptOn"})
    g.get("gt0", "KeepTmp"); g.call("tclr", K_ARR, "Array_Clear", inp={"TargetArray": "@gt0.KeepTmp"})
    g.get("gs0", "SnapWorn"); g.foreach("fs", "@gs0.SnapWorn")
    g.get("gw0", "Worn"); g.call("ws", K_ARR, "Array_Contains", inp={"TargetArray": "@gw0.Worn", "ItemToFind": "@fs.Array Element"}); g.branch("bws", "@ws.ReturnValue")
    g.get("gt1", "KeepTmp"); g.call("tadd", K_ARR, "Array_Add", inp={"TargetArray": "@gt1.KeepTmp", "NewItem": "@fs.Array Element"})
    g.get("gt2", "KeepTmp"); g.set("ssw", "SnapWorn", inp={"SnapWorn": "@gt2.KeepTmp"})
    g.branch("bk", "@entry.keep")
    g.get("gw1", "Worn"); g.foreach("fw", "@gw1.Worn")
    g.n("ik", "call_self", function="Is Kept Item", inp={"name": "@fw.Array Element"})
    g.get("gs1", "SnapWorn"); g.call("sn", K_ARR, "Array_Contains", inp={"TargetArray": "@gs1.SnapWorn", "ItemToFind": "@fw.Array Element"})
    g.call("nsn", K_MATH, "Not_PreBool", inp={"A": "@sn.ReturnValue"}); g.call("own", K_MATH, "BooleanAND", inp={"A": "@ik.yes", "B": "@nsn.ReturnValue"}); g.branch("bo", "@own.ReturnValue")
    g.get("gk1", "KeptOn"); g.call("kadd", K_ARR, "Array_Add", inp={"TargetArray": "@gk1.KeptOn", "NewItem": "@fw.Array Element"})
    g.chain("entry", "clr", "tclr", "fs"); g.chain("fs", "bws", "tadd"); g.chain("fs:Completed", "ssw", "bk", "fw"); g.chain("fw", "bo", "kadd")
    return fn("Collect Kept", [param("keep", "bool")], graph=g)


def f_blocked_by_kept():
    """A snapshot piece that a piece in KeptOn keeps out: the same slot (unless it holds several, MultiSlots) or a slot pair the
    game does not allow together (Conflicts With, not freed). A kept piece itself and a piece without a catalog slot never are."""
    g = G(); g.set("s0", "KeepHit", inp={"KeepHit": "false"})
    g.n("isl", "call_self", function="Item Slot", inp={"name": "@entry.name"}); g.call("known", K_MATH, "NotEqual_NameName", inp={"A": "@isl.slot", "B": "None"})
    g.n("kis", "call_self", function="Keep In Slot", inp={"name": "@entry.name"}); g.call("nkis", K_MATH, "Not_PreBool", inp={"A": "@kis.keep"})
    g.get("gk", "KeptOn"); g.foreach("fk", "@gk.KeptOn")
    g.n("ksl", "call_self", function="Item Slot", inp={"name": "@fk.Array Element"})
    g.call("other", K_MATH, "NotEqual_NameName", inp={"A": "@fk.Array Element", "B": "@entry.name"})
    g.call("same", K_MATH, "EqualEqual_NameName", inp={"A": "@isl.slot", "B": "@ksl.slot"}); g.call("sb", K_MATH, "BooleanAND", inp={"A": "@same.ReturnValue", "B": "@nkis.ReturnValue"})
    g.n("cw", "call_self", function="Conflicts With", inp={"a": "@isl.slot", "b": "@ksl.slot"}); g.n("fr", "call_self", function="Is Freed", inp={"a": "@isl.slot", "b": "@ksl.slot"})
    g.call("nfr", K_MATH, "Not_PreBool", inp={"A": "@fr.yes"}); g.call("cb", K_MATH, "BooleanAND", inp={"A": "@cw.yes", "B": "@nfr.ReturnValue"})
    g.call("any", K_MATH, "BooleanOR", inp={"A": "@sb.ReturnValue", "B": "@cb.ReturnValue"}); g.call("h1", K_MATH, "BooleanAND", inp={"A": "@any.ReturnValue", "B": "@other.ReturnValue"})
    g.call("hit", K_MATH, "BooleanAND", inp={"A": "@h1.ReturnValue", "B": "@known.ReturnValue"}); g.branch("bh", "@hit.ReturnValue")
    g.set("s1", "KeepHit", inp={"KeepHit": "true"})
    g.get("gh", "KeepHit"); g.link("gh.KeepHit", "return.yes")
    g.chain("entry", "s0", "fk"); g.chain("fk", "bh", "s1"); g.chain("fk:Completed", "return")
    return fn("Blocked By Kept", [param("name", "name")], [param("yes", "bool")], graph=g)


def f_with_kept_colors():
    """The look's slot colours plus those of the kept pieces from SlotColors now ("name#slot" keys): Finish Apply Snapshot
    replaces the whole map, Reset Dropped Colors resets what the new map lacks."""
    g = G(); g.set("s0", "KeepColors", inp={"KeepColors": "@entry.next"})
    g.get("gsc", "SlotColors"); g.call("keys", K_MAP, "Map_Keys", inp={"TargetMap": "@gsc.SlotColors"}); g.foreach("fk", "@keys.Keys")
    g.call("k2s", K_STR, "Conv_NameToString", inp={"InName": "@fk.Array Element"})
    g.call("sp", K_STR, "Split", inp={"SourceString": "@k2s.ReturnValue", "InStr": "#", "SearchCase": "CaseSensitive", "SearchDir": "FromStart"})
    g.call("n2n", K_STR, "Conv_StringToName", inp={"InString": "@sp.LeftS"})
    g.get("gk", "KeptOn"); g.call("in", K_ARR, "Array_Contains", inp={"TargetArray": "@gk.KeptOn", "ItemToFind": "@n2n.ReturnValue"}); g.branch("bin", "@in.ReturnValue")
    g.get("gsc2", "SlotColors"); g.call("cf", K_MAP, "Map_Find", inp={"TargetMap": "@gsc2.SlotColors", "Key": "@fk.Array Element"})
    g.get("gkc", "KeepColors"); g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gkc.KeepColors", "Key": "@fk.Array Element", "Value": "@cf.Value"})
    g.get("gkc2", "KeepColors"); g.link("gkc2.KeepColors", "return.colors")
    g.chain("entry", "s0", "keys", "fk"); g.chain("fk", "bin", "add"); g.chain("fk:Completed", "return")
    return fn("With Kept Colors", [param("next", "name", "map", value_type=S_LINCOLOR)], [param("colors", "name", "map", value_type=S_LINCOLOR)], graph=g)


def variables():
    return [var("KeepItems", "name", "array"), var("SnapWorn", "name", "array"), var("KeptOn", "name", "array"), var("KeepTmp", "name", "array"),
            var("KeepHit", "bool"), var("KeepColors", "name", "map", value_type=S_LINCOLOR), var("PendingKept", "string", "array"),
            var("PendingKeep", "bool"), var("NextKeep", "bool"),
            var("SnapMkOwn", "bool"), var("PendingMkOwn", "bool"), var("NextMkOwn", "bool")]   # the snapshot's make-up is Jodi's own (an outfit): no "not available" for it


def saved_variables():
    """SG_AltUI: the two lists that survive a restart (SETTINGS copies them)."""
    return [var("KeepItems", "name", "array"), var("SnapWorn", "name", "array")]


def functions():
    return [f_is_kept_item(), f_toggle_keep_item(), f_note_self_worn(), f_collect_kept(), f_blocked_by_kept(), f_with_kept_colors()]
