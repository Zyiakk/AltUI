"""What the game dressed Jodi from when the level started (Restore Multi Worn, Fix Loaded Underwear).

* Story save loaded (Character_Base.Loading State > 0): Plots_GameState.Load Game Ex put the save's Player Save Data on Jodi
  (LoadActorData) and Jodi's On Begun Play skipped Load Player Save Data - TKAPlayer is not read. Her `Save Player Clothes` (worn
  at save time) went on through Wear These Clothes and was cleared. The list is still in the loaded save object
  (Plots_GameState.Story Mode Save Game Data): Player Save Data.ByteData = Jodi's SaveGame properties, tagged-property serialised.
* Chapter start (Jodi_StoryMode, Plots_GameState.Prev Level End Save valid): that end state's Wear Clothes instead of TKAPlayer.
* Otherwise TKAPlayer (Player_Save, Functions.Get Player Save Slot Name).
Notes: docs/notes/2026-10-24-laden-story-stand.md."""
from bpdsl import *

SAVE_PROP = "Save Player Clothes"
CHARS = "".join(chr(c) for c in range(32, 127))   # SaveChars: byte c (32..126) -> the character at c - 32
MAX_STR = 256      # longer FStrings: not what is looked for
MAX_NAMES = 512    # a sane count of worn pieces


def variables():
    return [var("SaveBytes", "byte", "array"), var("SaveStr", "string"), var("SaveOk", "bool"), var("SavePos", "int"), var("SaveFound", "int"),
            var("SaveChars", "string", default=CHARS)]


def f_save_byte():
    g = G(); g.get("gb", "SaveBytes"); g.call("ag", K_ARR, "Array_Get", inp={"TargetArray": "@gb.SaveBytes", "Index": "@entry.pos"})
    g.call("bi", K_MATH, "Conv_ByteToInt", inp={"InByte": "@ag.Item"}); g.link("bi.ReturnValue", "return.v")
    return fn("Save Byte", [param("pos", "int")], [param("v", "int")], graph=g, pure=True)


def f_save_int():
    """int32 little endian at pos (signed: a negative FString length = UTF-16)."""
    g = G(); b = []
    for i in range(4):
        g.call("p%d" % i, K_MATH, "Add_IntInt", inp={"A": "@entry.pos", "B": str(i)}); g.n("b%d" % i, "call_self", function="Save Byte", inp={"pos": "@p%d.ReturnValue" % i}); b.append("@b%d.v" % i)
    g.call("neg", K_MATH, "GreaterEqual_IntInt", inp={"A": b[3], "B": "128"}); g.call("b3n", K_MATH, "Subtract_IntInt", inp={"A": b[3], "B": "256"})
    g.call("hi", K_MATH, "SelectInt", inp={"A": "@b3n.ReturnValue", "B": b[3], "bPickA": "@neg.ReturnValue"})
    g.call("m1", K_MATH, "Multiply_IntInt", inp={"A": b[1], "B": "256"}); g.call("m2", K_MATH, "Multiply_IntInt", inp={"A": b[2], "B": "65536"})
    g.call("m3", K_MATH, "Multiply_IntInt", inp={"A": "@hi.ReturnValue", "B": "16777216"})
    g.call("s1", K_MATH, "Add_IntInt", inp={"A": b[0], "B": "@m1.ReturnValue"}); g.call("s2", K_MATH, "Add_IntInt", inp={"A": "@s1.ReturnValue", "B": "@m2.ReturnValue"})
    g.call("s3", K_MATH, "Add_IntInt", inp={"A": "@s2.ReturnValue", "B": "@m3.ReturnValue"}); g.link("s3.ReturnValue", "return.v")
    return fn("Save Int", [param("pos", "int")], [param("v", "int")], graph=g, pure=True)


def f_save_str():
    """The FString at pos: s, the position after it, ok = an ASCII string of 1..MAX_STR bytes inside SaveBytes (a UTF-16 one is
    skipped: next is right, ok false)."""
    g = G(); g.n("n", "call_self", function="Save Int", inp={"pos": "@entry.pos"})
    g.set("s0", "SaveStr", inp={"SaveStr": ""})
    g.call("ge1", K_MATH, "Greater_IntInt", inp={"A": "@n.v", "B": "0"}); g.call("le", K_MATH, "LessEqual_IntInt", inp={"A": "@n.v", "B": str(MAX_STR)})
    g.call("e4", K_MATH, "Add_IntInt", inp={"A": "@entry.pos", "B": "4"}); g.call("end", K_MATH, "Add_IntInt", inp={"A": "@e4.ReturnValue", "B": "@n.v"})
    g.get("gb", "SaveBytes"); g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@gb.SaveBytes"}); g.call("inb", K_MATH, "LessEqual_IntInt", inp={"A": "@end.ReturnValue", "B": "@len.ReturnValue"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@ge1.ReturnValue", "B": "@le.ReturnValue"}); g.call("a2", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@inb.ReturnValue"})
    g.set("sok", "SaveOk", inp={"SaveOk": "@a2.ReturnValue"}); g.get("gok", "SaveOk"); g.branch("bok", "@gok.SaveOk")
    g.call("last", K_MATH, "Subtract_IntInt", inp={"A": "@n.v", "B": "2"})   # the terminating NUL is not read
    g.n("fl", "macro", name="ForLoop", inp={"First Index": "0", "Last Index": "@last.ReturnValue"})
    g.call("ci", K_MATH, "Add_IntInt", inp={"A": "@e4.ReturnValue", "B": "@fl.Index"}); g.n("c", "call_self", function="Save Byte", inp={"pos": "@ci.ReturnValue"})
    g.call("lo", K_MATH, "GreaterEqual_IntInt", inp={"A": "@c.v", "B": "32"}); g.call("hi", K_MATH, "LessEqual_IntInt", inp={"A": "@c.v", "B": "126"})
    g.call("pr", K_MATH, "BooleanAND", inp={"A": "@lo.ReturnValue", "B": "@hi.ReturnValue"}); g.branch("bpr", "@pr.ReturnValue")
    g.call("ix", K_MATH, "Subtract_IntInt", inp={"A": "@c.v", "B": "32"}); g.get("gch", "SaveChars")
    g.call("ch", K_STR, "GetSubstring", inp={"SourceString": "@gch.SaveChars", "StartIndex": "@ix.ReturnValue", "Length": "1"})
    g.get("gs", "SaveStr"); g.call("cat", K_STR, "Concat_StrStr", inp={"A": "@gs.SaveStr", "B": "@ch.ReturnValue"}); g.set("sc", "SaveStr", inp={"SaveStr": "@cat.ReturnValue"})
    g.set("bad", "SaveOk", inp={"SaveOk": "false"})
    # next: ASCII n bytes, UTF-16 -n * 2
    g.call("neg", K_MATH, "Less_IntInt", inp={"A": "@n.v", "B": "0"}); g.call("w", K_MATH, "Multiply_IntInt", inp={"A": "@n.v", "B": "-2"})
    g.call("sz", K_MATH, "SelectInt", inp={"A": "@w.ReturnValue", "B": "@n.v", "bPickA": "@neg.ReturnValue"}); g.call("nx", K_MATH, "Add_IntInt", inp={"A": "@e4.ReturnValue", "B": "@sz.ReturnValue"})
    g.get("gs2", "SaveStr"); g.get("gok2", "SaveOk"); g.link("gs2.SaveStr", "return.s"); g.link("nx.ReturnValue", "return.next"); g.link("gok2.SaveOk", "return.ok")
    g.chain("entry", "s0", "sok", "bok", "fl"); g.chain("fl", "bpr", "sc"); g.chain("bpr:else", "bad"); g.chain("fl:Completed", "return"); g.chain("bok:else", "return")
    return fn("Save Str", [param("pos", "int")], [param("s", "string"), param("next", "int"), param("ok", "bool")], graph=g)


def f_find_save_prop():
    """Position after the property name `name` (an FString: int32 length incl. NUL, then the bytes) in SaveBytes, -1 = not there."""
    g = G(); g.set("s0", "SaveFound", inp={"SaveFound": "-1"})
    g.call("ln", K_STR, "Len", inp={"S": "@entry.name"}); g.call("l1", K_MATH, "Add_IntInt", inp={"A": "@ln.ReturnValue", "B": "1"})
    g.call("c0", K_STR, "GetCharacterAsNumber", inp={"SourceString": "@entry.name", "Index": "0"})
    g.get("gb", "SaveBytes"); g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@gb.SaveBytes"})
    g.call("l5", K_MATH, "Add_IntInt", inp={"A": "@l1.ReturnValue", "B": "5"}); g.call("last", K_MATH, "Subtract_IntInt", inp={"A": "@len.ReturnValue", "B": "@l5.ReturnValue"})
    g.n("fl", "macro", name="ForLoop", inp={"First Index": "0", "Last Index": "@last.ReturnValue"})
    g.get("gf", "SaveFound"); g.call("nf", K_MATH, "Less_IntInt", inp={"A": "@gf.SaveFound", "B": "0"})
    # cheap test first: length byte, the next one 0, first character
    g.n("b0", "call_self", function="Save Byte", inp={"pos": "@fl.Index"}); g.call("e0", K_MATH, "EqualEqual_IntInt", inp={"A": "@b0.v", "B": "@l1.ReturnValue"})
    g.call("p1", K_MATH, "Add_IntInt", inp={"A": "@fl.Index", "B": "1"}); g.n("b1", "call_self", function="Save Byte", inp={"pos": "@p1.ReturnValue"}); g.call("e1", K_MATH, "EqualEqual_IntInt", inp={"A": "@b1.v", "B": "0"})
    g.call("p4", K_MATH, "Add_IntInt", inp={"A": "@fl.Index", "B": "4"}); g.n("b4", "call_self", function="Save Byte", inp={"pos": "@p4.ReturnValue"}); g.call("e4", K_MATH, "EqualEqual_IntInt", inp={"A": "@b4.v", "B": "@c0.ReturnValue"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@nf.ReturnValue", "B": "@e0.ReturnValue"}); g.call("a2", K_MATH, "BooleanAND", inp={"A": "@e1.ReturnValue", "B": "@e4.ReturnValue"})
    g.call("a3", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@a2.ReturnValue"}); g.branch("bc", "@a3.ReturnValue")
    g.n("rs", "call_self", function="Save Str", inp={"pos": "@fl.Index"})
    g.call("eq", K_STR, "EqualEqual_StrStr", inp={"A": "@rs.s", "B": "@entry.name"}); g.call("hit", K_MATH, "BooleanAND", inp={"A": "@rs.ok", "B": "@eq.ReturnValue"}); g.branch("bh", "@hit.ReturnValue")
    g.set("sf", "SaveFound", inp={"SaveFound": "@rs.next"})
    g.get("gf2", "SaveFound"); g.link("gf2.SaveFound", "return.pos")
    g.chain("entry", "s0", "fl"); g.chain("fl", "bc", "rs", "bh", "sf"); g.chain("fl:Completed", "return")
    return fn("Find Save Prop", [param("name", "string")], [param("pos", "int")], graph=g)


def f_parse_save_worn():
    """TmpNames3 = Save Player Clothes in SaveBytes (Jodi's SaveGame properties). ok false: the property is missing (nothing worn: an
    empty array is not written) or not laid out as expected (ArrayProperty of NameProperty). SaveBytes is emptied afterwards."""
    g = G(); g.get("gn0", "TmpNames3"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gn0.TmpNames3"})
    g.n("fp", "call_self", function="Find Save Prop", inp={"name": SAVE_PROP}); g.call("fok", K_MATH, "GreaterEqual_IntInt", inp={"A": "@fp.pos", "B": "0"}); g.branch("bf", "@fok.ReturnValue")
    # ArrayProperty, int64 size, NameProperty, guid flag, count, then the names
    g.n("t1", "call_self", function="Save Str", inp={"pos": "@fp.pos"}); g.call("sz", K_MATH, "Add_IntInt", inp={"A": "@t1.next", "B": "8"})
    g.n("t2", "call_self", function="Save Str", inp={"pos": "@sz.ReturnValue"}); g.call("cnp", K_MATH, "Add_IntInt", inp={"A": "@t2.next", "B": "1"})
    g.n("cnt", "call_self", function="Save Int", inp={"pos": "@cnp.ReturnValue"})
    g.call("q1", K_STR, "EqualEqual_StrStr", inp={"A": "@t1.s", "B": "ArrayProperty"}); g.call("q2", K_STR, "EqualEqual_StrStr", inp={"A": "@t2.s", "B": "NameProperty"})
    g.call("q3", K_MATH, "InRange_IntInt", inp={"Value": "@cnt.v", "Min": "0", "Max": str(MAX_NAMES), "InclusiveMin": "true", "InclusiveMax": "true"})
    g.call("qa", K_MATH, "BooleanAND", inp={"A": "@q1.ReturnValue", "B": "@q2.ReturnValue"}); g.call("qb", K_MATH, "BooleanAND", inp={"A": "@qa.ReturnValue", "B": "@q3.ReturnValue"}); g.branch("bq", "@qb.ReturnValue")
    g.call("p0", K_MATH, "Add_IntInt", inp={"A": "@cnp.ReturnValue", "B": "4"}); g.set("sp0", "SavePos", inp={"SavePos": "@p0.ReturnValue"})
    g.call("lst", K_MATH, "Subtract_IntInt", inp={"A": "@cnt.v", "B": "1"}); g.n("fl", "macro", name="ForLoop", inp={"First Index": "0", "Last Index": "@lst.ReturnValue"})
    g.get("gp", "SavePos"); g.n("rn", "call_self", function="Save Str", inp={"pos": "@gp.SavePos"}); g.branch("brn", "@rn.ok")   # a UTF-16 name is skipped
    g.call("sn", K_STR, "Conv_StringToName", inp={"InString": "@rn.s"}); g.get("gn1", "TmpNames3"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gn1.TmpNames3", "NewItem": "@sn.ReturnValue"})
    g.set("snx", "SavePos", inp={"SavePos": "@rn.next"})
    g.get("gb2", "SaveBytes"); g.call("fr", K_ARR, "Array_Clear", inp={"TargetArray": "@gb2.SaveBytes"})
    g.get("gb3", "SaveBytes"); g.call("fr2", K_ARR, "Array_Clear", inp={"TargetArray": "@gb3.SaveBytes"})
    g.n("ok", "return_new", inp={"ok": "true"})
    g.chain("entry", "clr", "fp", "bf", "t1", "t2", "bq", "sp0", "fl"); g.chain("fl", "rn", "brn", "add", "snx"); g.chain("brn:else", "snx")
    g.chain("fl:Completed", "fr", "ok"); g.chain("bf:else", "fr2", "return"); g.chain("bq:else", "fr2")
    return fn("Parse Save Worn", outputs=[param("ok", "bool")], graph=g)


def f_story_worn():
    """TmpNames3 = Save Player Clothes of the loaded story save (Plots_GameState.Story Mode Save Game Data); ok false: no story save
    or Parse Save Worn found none."""
    g = G(); g.get("gn0", "TmpNames3"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gn0.TmpNames3"})
    g.call("gs", K_GS, "GetGameState"); g.cast("cp", P_PLOTS, "@gs.ReturnValue"); g.get("gsd", "Story Mode Save Game Data", cls=P_PLOTS); g.link("cp.AsPlots_GameState", "gsd.self")
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@gsd.Story Mode Save Game Data"}); g.branch("biv", "@iv.ReturnValue")
    g.get("gpd", "Player Save Data", cls=P_TKASAVE); g.link("gsd.Story Mode Save Game Data", "gpd.self")
    g.brk("br", S_ACTORSAVE.split(":", 1)[1], "@gpd.Player Save Data"); g.set("sb", "SaveBytes", inp={"SaveBytes": "@br.ByteData"})
    g.n("ps", "call_self", function="Parse Save Worn"); g.n("rok", "return_new", inp={"ok": "@ps.ok"})
    g.chain("entry", "clr", "biv", "sb", "ps", "rok"); g.chain("biv:else", "return")
    return fn("Story Worn", outputs=[param("ok", "bool")], graph=g)


def f_loaded_worn():
    """TmpNames3 = the clothes the game dressed `char` from at the level start (see the module text); ok false = unknown (the callers
    then leave what is worn alone)."""
    g = G(); g.call("ivc", K_SYS, "IsValid", inp={"Object": "@entry.char"})
    g.get("gls", "Loading State", cls=P_CB); g.link("entry.char", "gls.self"); g.call("ld", K_MATH, "Greater_IntInt", inp={"A": "@gls.Loading State", "B": "0"})
    g.call("al", K_MATH, "BooleanAND", inp={"A": "@ivc.ReturnValue", "B": "@ld.ReturnValue"}); g.branch("bld", "@al.ReturnValue")
    g.n("sw", "call_self", function="Story Worn"); g.n("rsw", "return_new", inp={"ok": "@sw.ok"})
    # chapter start: Jodi_StoryMode dresses from the previous chapter's end state
    g.call("gs", K_GS, "GetGameState"); g.cast("cp", P_PLOTS, "@gs.ReturnValue"); g.get("gle", "Prev Level End Save", cls=P_PLOTS); g.link("cp.AsPlots_GameState", "gle.self")
    g.call("ivl", K_SYS, "IsValid", inp={"Object": "@gle.Prev Level End Save"}); g.cast("csm", P_JODI_SM, "@entry.char"); g.call("ivs", K_SYS, "IsValid", inp={"Object": "@csm.AsJodi_StoryMode"})
    g.call("ale", K_MATH, "BooleanAND", inp={"A": "@ivl.ReturnValue", "B": "@ivs.ReturnValue"}); g.branch("ble", "@ale.ReturnValue")
    g.get("gwl", "Wear Clothes", cls=P_PSAVE); g.link("gle.Prev Level End Save", "gwl.self"); g.set("sle", "TmpNames3", inp={"TmpNames3": "@gwl.Wear Clothes"})
    g.n("rle", "return_new", inp={"ok": "true"})
    # otherwise TKAPlayer
    g.call("ex", K_GS, "DoesSaveGameExist", inp={"SlotName": "TKAPlayer", "UserIndex": "0"}); g.branch("be", "@ex.ReturnValue")
    g.call("ldg", K_GS, "LoadGameFromSlot", inp={"SlotName": "TKAPlayer", "UserIndex": "0"}); g.cast("cs", P_PSAVE, "@ldg.ReturnValue")
    g.call("csv", K_SYS, "IsValid", inp={"Object": "@cs.AsPlayer_Save"}); g.branch("bcs", "@csv.ReturnValue")   # foreign/corrupt slot content -> unknown
    g.get("gwc", "Wear Clothes", cls=P_PSAVE); g.link("cs.AsPlayer_Save", "gwc.self"); g.set("sn", "TmpNames3", inp={"TmpNames3": "@gwc.Wear Clothes"})
    g.n("rtp", "return_new", inp={"ok": "true"})
    g.chain("entry", "bld", "sw", "rsw"); g.chain("bld:else", "ble", "sle", "rle"); g.chain("ble:else", "ex", "be", "ldg", "bcs", "sn", "rtp")
    g.chain("be:else", "return"); g.chain("bcs:else", "return")
    return fn("Loaded Worn", [param("char", "object:" + P_CB)], [param("ok", "bool")], graph=g)


def functions():
    return [f_save_byte(), f_save_int(), f_save_str(), f_find_save_prop(), f_parse_save_worn(), f_story_worn(), f_loaded_worn()]
