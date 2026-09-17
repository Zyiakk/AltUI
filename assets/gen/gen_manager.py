"""Generates assets/30_manager.json: BP_AltUIManager (data layer, state, actions, debug)."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *
from slots import SLOTS, SLOT_GROUP, GROUPS

MGR = M + "/BP_AltUIManager"
S_ITEM = M + "/S_ClothesItem"
S_LIST = M + "/S_ItemList"
S_NAMES = M + "/S_NameList"
S_SNAP = M + "/S_Snapshot"
S_LOOK = M + "/S_Look"; SG_LOOKS = M + "/SG_Looks"; LOOKS_SLOT = "AltUI_Looks"
T_ITEM = "struct:" + S_ITEM
T_LIST = "struct:" + S_LIST
STRINGTABLE = "/Game/Project/Tables/StringTable.StringTable"
from strings import rows as string_rows, LANGS
from theme import THEME, DERIVED, DERIVED_NAMES, BG_ALPHA, TILE_ALPHA, rgb_lit
S_STR = M + "/S_Strings"; T_STRINGS = M + "/Strings"


def pop(g, id, text_pin, exec_prev=None):
    """Pop Attention(content=<text pin>) via the GameState."""
    g.call(id + "_gs", K_GS, "GetGameState")
    g.cast(id + "_c", P_GS, "@" + id + "_gs.ReturnValue")
    g.call(id, P_GS, "Pop Attention", inp={"self": "@" + id + "_c.AsTKA Game State Base", "content": text_pin, "type": "0"})
    return id


def text_from_str(g, id, str_pin):
    g.call(id, K_TXT, "Conv_StringToText", inp={"InString": str_pin}); return "@" + id + ".ReturnValue"


# ---------------- Init Slot Groups ----------------
def f_init_slot_groups():
    g = G()
    g.get("gm", "SlotGroup")
    g.call("clr", K_MAP, "Map_Clear", inp={"TargetMap": "@gm.SlotGroup"})
    chain = ["entry", "clr"]
    for i, s in enumerate(SLOTS):
        g.get("gm%d" % i, "SlotGroup")
        k = g.lit_name("k%d" % i, s); v = g.lit_name("v%d" % i, SLOT_GROUP[s])
        g.call("add%d" % i, K_MAP, "Map_Add", inp={"TargetMap": "@gm%d.SlotGroup" % i, "Key": k, "Value": v})
        chain.append("add%d" % i)
    g.chain(*chain)
    return fn("Init Slot Groups", graph=g)


# ---------------- Order Slots(rows) ----------------
def f_order_slots():
    g = G()
    g.get("gs0", "Slots"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gs0.Slots"})
    for i, grp in enumerate(GROUPS):
        p = "g%d" % i
        g.foreach(p, "@entry.rows")
        g.get(p + "_m", "SlotGroup")
        g.call(p + "_f", K_MAP, "Map_Find", inp={"TargetMap": "@%s_m.SlotGroup" % p, "Key": "@%s.Array Element" % p})
        g.call(p + "_eq", K_MATH, "EqualEqual_NameName", inp={"A": "@%s_f.Value" % p, "B": grp})
        g.branch(p + "_b", "@%s_eq.ReturnValue" % p)
        g.get(p + "_s", "Slots")
        g.call(p + "_add", K_ARR, "Array_Add", inp={"TargetArray": "@%s_s.Slots" % p, "NewItem": "@%s.Array Element" % p})
        g.chain(p, p + "_b", p + "_add")
    g.chain("entry", "clr", "g0")
    for i in range(1, len(GROUPS)):
        g.chain("g%d:Completed" % (i - 1), "g%d" % i)
    # append unknown slots (not in the group map) at the end
    g.foreach("gu", "@entry.rows")
    g.get("gu_s", "Slots"); g.call("gu_c", K_ARR, "Array_Contains", inp={"TargetArray": "@gu_s.Slots", "ItemToFind": "@gu.Array Element"})
    g.call("gu_n", K_MATH, "Not_PreBool", inp={"A": "@gu_c.ReturnValue"})
    g.branch("gu_b", "@gu_n.ReturnValue")
    g.get("gu_s2", "Slots"); g.call("gu_add", K_ARR, "Array_Add", inp={"TargetArray": "@gu_s2.Slots", "NewItem": "@gu.Array Element"})
    g.get("gu_m", "SlotGroup"); g.call("gu_madd", K_MAP, "Map_Add", inp={"TargetMap": "@gu_m.SlotGroup", "Key": "@gu.Array Element", "Value": g.lit_name("gu_acc", "Accessories")})
    g.chain("g%d:Completed" % (len(GROUPS) - 1), "gu")
    g.chain("gu", "gu_b", "gu_add", "gu_madd")
    return fn("Order Slots", [param("rows", "name", "array")], graph=g)


# ---------------- Sort Key(s) -> key ----------------
def f_sort_key():
    g = G()
    g.call("low", K_STR, "ToLower", inp={"SourceString": "@entry.s"})
    g.set("st", "TmpStr", inp={"TmpStr": "@low.ReturnValue"})
    g.set("k0", "TmpKey", inp={"TmpKey": "0"})
    g.n("fl", "macro", name="ForLoop", inp={"First Index": "0", "Last Index": "11"})
    # ord = (Index < Len) ? FindSubstring(Alphabet, ch)+1 : 0
    g.get("gts", "TmpStr"); g.call("len", K_STR, "Len", inp={"S": "@gts.TmpStr"})
    g.call("lt", K_MATH, "Less_IntInt", inp={"A": "@fl.Index", "B": "@len.ReturnValue"})
    g.get("gts2", "TmpStr"); g.call("ch", K_STR, "GetSubstring", inp={"SourceString": "@gts2.TmpStr", "StartIndex": "@fl.Index", "Length": "1"})
    g.get("ga", "Alphabet"); g.call("fs", K_STR, "FindSubstring", inp={"SearchIn": "@ga.Alphabet", "Substring": "@ch.ReturnValue", "bUseCase": "false", "bSearchFromEnd": "false", "StartPosition": "-1"})
    g.call("ord1", K_MATH, "Add_IntInt", inp={"A": "@fs.ReturnValue", "B": "1"})
    g.call("ord", K_MATH, "SelectInt", inp={"A": "@ord1.ReturnValue", "B": "0", "bPickA": "@lt.ReturnValue"})
    g.get("gk", "TmpKey"); g.call("mul", K_MATH, "Multiply_Int64Int64", inp={"A": "@gk.TmpKey", "B": "37"})
    g.call("c64", K_MATH, "Conv_IntToInt64", inp={"InInt": "@ord.ReturnValue"})
    g.call("add", K_MATH, "Add_Int64Int64", inp={"A": "@mul.ReturnValue", "B": "@c64.ReturnValue"})
    g.set("sk", "TmpKey", inp={"TmpKey": "@add.ReturnValue"})
    g.get("gk2", "TmpKey")
    g.link("gk2.TmpKey", "return.key")
    g.chain("entry", "st", "k0", "fl")
    g.chain("fl", "sk")                 # LoopBody
    g.chain("fl:Completed", "return")
    return fn("Sort Key", [param("s", "string")], [param("key", "int64")], graph=g)


# ---------------- Display Name(row) -> s  (pure) ----------------
def f_display_name():
    g = G()
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"})
    g.call("reg", K_STT, "IsRegisteredTableEntry", inp={"TableId": STRINGTABLE, "Key": "@n2s.ReturnValue"})
    g.call("src", K_STT, "GetTableEntrySourceString", inp={"TableId": STRINGTABLE, "Key": "@n2s.ReturnValue"})
    g.call("sel", K_MATH, "SelectString", inp={"A": "@src.ReturnValue", "B": "@n2s.ReturnValue", "bPickA": "@reg.ReturnValue"})
    g.link("sel.ReturnValue", "return.s")
    return fn("Display Name", [param("row", "name")], [param("s", "string")], graph=g, pure=True)


# ---------------- Scan Mod Items(): ItemOrigin[row] = caption of the mod whose Mod_ClothesTable holds the row ----------------
# The loader appends mod rows to the base ClothesTable, and vanilla themes (Demon, Combat, ...) live in their own tables, so
# DoesDataTableRowExist(ClothesTable) says nothing about the origin. DLC_MainTable has one row per mounted mod pak (= mod folder).
def f_scan_mod_items():
    g = G()
    g.get("go", "ItemOrigin"); g.call("mc", K_MAP, "Map_Clear", inp={"TargetMap": "@go.ItemOrigin"})
    g.call("rn", K_DT, "GetDataTableRowNames", inp={"Table": P_DLC_T}); g.foreach("fe", "@rn.OutRowNames")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@fe.Array Element"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "/Game/Mod/", "B": "@n2s.ReturnValue"}); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "/Mod_ClothesTable.Mod_ClothesTable"})
    g.call("sp", K_SYS, "MakeSoftObjectPath", inp={"PathString": "@c2.ReturnValue"}); g.call("sr", K_SYS, "Conv_SoftObjPathToSoftObjRef", inp={"SoftObjectPath": "@sp.ReturnValue"})
    g.call("ld", K_SYS, "LoadAsset_Blocking", inp={"Asset": "@sr.ReturnValue"}); g.cast("ck", E_DATATABLE, "@ld.ReturnValue", pure=False, miss="ignore")   # mod without a clothes table -> next mod
    # caption of the mod (DLC row), row name as fallback
    g.n("row", "get_row", table=P_DLC_T, inp={"RowName": "@fe.Array Element"}); g.brk("br", P_DLC_S, "@row.OutRow")
    g.call("ce", K_TXT, "TextIsEmpty", inp={"InText": "@br.Caption"}); g.call("cs", K_TXT, "Conv_TextToString", inp={"InText": "@br.Caption"})
    g.call("sel", K_MATH, "SelectString", inp={"A": "@n2s.ReturnValue", "B": "@cs.ReturnValue", "bPickA": "@ce.ReturnValue"}); g.call("ct", K_TXT, "Conv_StringToText", inp={"InString": "@sel.ReturnValue"})
    g.set("stt", "TmpText", inp={"TmpText": "@ct.ReturnValue"})
    g.call("rows", K_DT, "GetDataTableRowNames", inp={"Table": "@ck.AsData Table"}); g.foreach("fr", "@rows.OutRowNames")
    g.get("go2", "ItemOrigin"); g.get("gtt", "TmpText"); g.call("ma", K_MAP, "Map_Add", inp={"TargetMap": "@go2.ItemOrigin", "Key": "@fr.Array Element", "Value": "@gtt.TmpText"})
    g.chain("entry", "mc", "rn", "fe"); g.chain("fe", "ld", "ck", "row", "stt", "rows", "fr"); g.chain("row:Row Not Found", "stt"); g.chain("fr", "ma")
    return fn("Scan Mod Items", graph=g)


# ---------------- Build Catalog() ----------------
# Pass 1 (per table row): item struct -> ItemByName/ItemSlot, row name appended to SlotNames[slot] (name arrays: cheap copies).
# Pass 2 (per slot, in slot order): items inserted into TmpItems by binary search over the parallel key arrays TmpKeys/TmpKeys2
# (int64, no struct copies), then one Map_Add into Catalog; SlotCounts and AllItems ("All") on the way.
# Equal keys keep table order (insert after equals, like the former linear Insert Sorted).
BSEARCH_STEPS = 13   # ForLoop with a fixed bound instead of WhileLoop: 2^13 > any slot; a shipping build has no runaway-loop guard


def f_build_catalog():
    g = G()
    for i, m in enumerate(("Catalog", "ItemSlot", "ItemByName", "SlotCounts", "SlotNames")):
        g.get("gm%d" % i, m); g.call("clr%d" % i, K_MAP, "Map_Clear", inp={"TargetMap": "@gm%d.%s" % (i, m)})
    g.call("rt", K_DT, "GetDataTableRowNames", inp={"Table": P_CTT})
    g.n("os", "call_self", function="Order Slots", inp={"rows": "@rt.OutRowNames"})
    g.call("ra", K_DT, "GetDataTableRowNames", inp={"Table": P_CT})
    g.call("lena", K_ARR, "Array_Length", inp={"TargetArray": "@ra.OutRowNames"})
    g.set("scr", "CatalogRows", inp={"CatalogRows": "@lena.ReturnValue"})
    # ---- pass 1: rows -> items
    g.foreach("fe", "@ra.OutRowNames")
    g.call("rn2s", K_STR, "Conv_NameToString", inp={"InName": "@fe.Array Element"})
    g.call("ign", K_STR, "StartsWith", inp={"SourceString": "@rn2s.ReturnValue", "InPrefix": "TKAIgnore", "SearchCase": "IgnoreCase"})
    g.call("nign", K_MATH, "Not_PreBool", inp={"A": "@ign.ReturnValue"}); g.branch("bign", "@nign.ReturnValue")
    g.n("row", "get_row", table=P_CT, inp={"RowName": "@fe.Array Element"}, miss="ignore")   # row names of the same table
    g.brk("bc", P_CS, "@row.OutRow")
    # display name / slot frozen in TmpStr2 / TmpName: pure nodes are evaluated once per consumer (Display Name = 2 string-table lookups)
    g.n("dn", "call_self", function="Display Name", inp={"row": "@fe.Array Element"}); g.set("sdn", "TmpStr2", inp={"TmpStr2": "@dn.s"}); g.get("gdn", "TmpStr2")
    g.n("sk", "call_self", function="Sort Key", inp={"s": "@gdn.TmpStr2"})
    g.call("sub2", K_STR, "GetSubstring", inp={"SourceString": "@gdn.TmpStr2", "StartIndex": "12", "Length": "12"})
    g.n("sk2", "call_self", function="Sort Key", inp={"s": "@sub2.ReturnValue"})
    g.get("gio", "ItemOrigin"); g.call("inmod", K_MAP, "Map_Contains", inp={"TargetMap": "@gio.ItemOrigin", "Key": "@fe.Array Element"}); g.call("van", K_MATH, "Not_PreBool", inp={"A": "@inmod.ReturnValue"})
    g.get("gsg", "SlotGroup"); g.call("known", K_MAP, "Map_Contains", inp={"TargetMap": "@gsg.SlotGroup", "Key": "@bc.TypeName"})
    g.call("tns", K_STR, "Conv_NameToString", inp={"InName": "@bc.TypeName"})
    g.call("ssel", K_MATH, "SelectString", inp={"A": "@tns.ReturnValue", "B": "Unknown", "bPickA": "@known.ReturnValue"})
    g.call("slot", K_STR, "Conv_StringToName", inp={"InString": "@ssel.ReturnValue"}); g.set("sslot", "TmpName", inp={"TmpName": "@slot.ReturnValue"}); g.get("gslot", "TmpName")
    g.make("mi", S_ITEM, Name="@fe.Array Element", Slot="@gslot.TmpName", DisplayName="@gdn.TmpStr2", SortKey="@sk.key", SortKey2="@sk2.key",
           Icon="@bc.Icon", ColorAdjustable="@bc.ColorAdjustable", Group="@bc.Group", IsVanilla="@van.ReturnValue")
    g.get("gis2", "ItemSlot"); g.call("madd", K_MAP, "Map_Add", inp={"TargetMap": "@gis2.ItemSlot", "Key": "@fe.Array Element", "Value": "@gslot.TmpName"})
    g.get("gib2", "ItemByName"); g.call("madd2", K_MAP, "Map_Add", inp={"TargetMap": "@gib2.ItemByName", "Key": "@fe.Array Element", "Value": "@mi.S_ClothesItem"})
    g.get("gsn", "SlotNames"); g.call("snf", K_MAP, "Map_Find", inp={"TargetMap": "@gsn.SlotNames", "Key": "@gslot.TmpName"}); g.brk("snb", S_NAMES, "@snf.Value")
    g.set("sn1", "TmpNames", inp={"TmpNames": "@snb.Names"}); g.get("gtn", "TmpNames"); g.call("sna", K_ARR, "Array_Add", inp={"TargetArray": "@gtn.TmpNames", "NewItem": "@fe.Array Element"})
    g.get("gtn2", "TmpNames"); g.make("snm", S_NAMES, Names="@gtn2.TmpNames"); g.get("gsn2", "SlotNames"); g.call("snadd", K_MAP, "Map_Add", inp={"TargetMap": "@gsn2.SlotNames", "Key": "@gslot.TmpName", "Value": "@snm.S_NameList"})
    # after pass 1: append the Unknown slot if populated
    unk = g.lit_name("unk", "Unknown"); acc = g.lit_name("acc", "Accessories")
    g.get("gsn3", "SlotNames"); g.call("hasu", K_MAP, "Map_Contains", inp={"TargetMap": "@gsn3.SlotNames", "Key": unk}); g.branch("bu", "@hasu.ReturnValue")
    g.get("gsl", "Slots"); g.call("addu", K_ARR, "Array_Add", inp={"TargetArray": "@gsl.Slots", "NewItem": unk})
    g.get("gsg2", "SlotGroup"); g.call("maddu", K_MAP, "Map_Add", inp={"TargetMap": "@gsg2.SlotGroup", "Key": unk, "Value": acc})
    # ---- pass 2: per slot, sorted insert by binary search
    g.get("ga0", "AllItems"); g.call("aclr", K_ARR, "Array_Clear", inp={"TargetArray": "@ga0.AllItems"})
    g.get("gsl2", "Slots"); g.foreach("fa", "@gsl2.Slots")
    for i, arr in enumerate(("TmpItems", "TmpKeys", "TmpKeys2")):
        g.get("gt%d" % i, arr); g.call("tclr%d" % i, K_ARR, "Array_Clear", inp={"TargetArray": "@gt%d.%s" % (i, arr)})
    g.get("gsn4", "SlotNames"); g.call("snf2", K_MAP, "Map_Find", inp={"TargetMap": "@gsn4.SlotNames", "Key": "@fa.Array Element"}); g.brk("snb2", S_NAMES, "@snf2.Value")
    g.set("sn2", "TmpNames", inp={"TmpNames": "@snb2.Names"}); g.get("gtn3", "TmpNames"); g.foreach("fn", "@gtn3.TmpNames")
    g.get("gib3", "ItemByName"); g.call("ibf", K_MAP, "Map_Find", inp={"TargetMap": "@gib3.ItemByName", "Key": "@fn.Array Element"}); g.set("sti", "TmpItem", inp={"TmpItem": "@ibf.Value"})
    g.get("gti", "TmpItem"); g.brk("bti", S_ITEM, "@gti.TmpItem")
    g.set("sk1", "TmpKey1", inp={"TmpKey1": "@bti.SortKey"}); g.set("sk2s", "TmpKey2", inp={"TmpKey2": "@bti.SortKey2"})   # keys frozen: no struct break per search step (TmpKey belongs to Sort Key)
    g.set("lo0", "TmpIdx", inp={"TmpIdx": "0"}); g.get("gk0", "TmpKeys"); g.call("klen", K_ARR, "Array_Length", inp={"TargetArray": "@gk0.TmpKeys"}); g.set("hi0", "TmpI", inp={"TmpI": "@klen.ReturnValue"})
    g.n("bs", "macro", name="ForLoop", inp={"First Index": "0", "Last Index": str(BSEARCH_STEPS - 1)})
    g.get("glo", "TmpIdx"); g.get("ghi", "TmpI"); g.call("open", K_MATH, "Less_IntInt", inp={"A": "@glo.TmpIdx", "B": "@ghi.TmpI"}); g.branch("bopen", "@open.ReturnValue")
    g.call("sum", K_MATH, "Add_IntInt", inp={"A": "@glo.TmpIdx", "B": "@ghi.TmpI"}); g.call("mid", K_MATH, "Divide_IntInt", inp={"A": "@sum.ReturnValue", "B": "2"})
    g.get("gk1", "TmpKeys"); g.call("kmid", K_ARR, "Array_Get", inp={"TargetArray": "@gk1.TmpKeys", "Index": "@mid.ReturnValue"})
    g.get("gk2", "TmpKeys2"); g.call("k2mid", K_ARR, "Array_Get", inp={"TargetArray": "@gk2.TmpKeys2", "Index": "@mid.ReturnValue"})
    g.get("gky", "TmpKey1"); g.get("gky2", "TmpKey2")
    g.call("lt", K_MATH, "Less_Int64Int64", inp={"A": "@gky.TmpKey1", "B": "@kmid.Item"}); g.call("eq", K_MATH, "EqualEqual_Int64Int64", inp={"A": "@gky.TmpKey1", "B": "@kmid.Item"})
    g.call("lt2", K_MATH, "Less_Int64Int64", inp={"A": "@gky2.TmpKey2", "B": "@k2mid.Item"}); g.call("and2", K_MATH, "BooleanAND", inp={"A": "@eq.ReturnValue", "B": "@lt2.ReturnValue"})
    g.call("less", K_MATH, "BooleanOR", inp={"A": "@lt.ReturnValue", "B": "@and2.ReturnValue"}); g.branch("bless", "@less.ReturnValue")
    g.set("hi1", "TmpI", inp={"TmpI": "@mid.ReturnValue"}); g.call("mid1", K_MATH, "Add_IntInt", inp={"A": "@mid.ReturnValue", "B": "1"}); g.set("lo1", "TmpIdx", inp={"TmpIdx": "@mid1.ReturnValue"})
    g.get("gidx", "TmpIdx"); g.get("gti2", "TmpItem"); g.get("gt3", "TmpItems"); g.call("ins", K_ARR, "Array_Insert", inp={"TargetArray": "@gt3.TmpItems", "NewItem": "@gti2.TmpItem", "Index": "@gidx.TmpIdx"})
    g.get("gk3", "TmpKeys"); g.get("gky3", "TmpKey1"); g.call("insk", K_ARR, "Array_Insert", inp={"TargetArray": "@gk3.TmpKeys", "NewItem": "@gky3.TmpKey1", "Index": "@gidx.TmpIdx"})
    g.get("gk4", "TmpKeys2"); g.get("gky4", "TmpKey2"); g.call("insk2", K_ARR, "Array_Insert", inp={"TargetArray": "@gk4.TmpKeys2", "NewItem": "@gky4.TmpKey2", "Index": "@gidx.TmpIdx"})
    # slot done: Catalog, SlotCounts, AllItems
    g.get("gt4", "TmpItems"); g.make("ml", S_LIST, Items="@gt4.TmpItems"); g.get("gc2", "Catalog"); g.call("cadd", K_MAP, "Map_Add", inp={"TargetMap": "@gc2.Catalog", "Key": "@fa.Array Element", "Value": "@ml.S_ItemList"})
    g.get("gt5", "TmpItems"); g.call("slen", K_ARR, "Array_Length", inp={"TargetArray": "@gt5.TmpItems"})
    g.get("gsc", "SlotCounts"); g.call("scadd", K_MAP, "Map_Add", inp={"TargetMap": "@gsc.SlotCounts", "Key": "@fa.Array Element", "Value": "@slen.ReturnValue"})
    g.get("ga1", "AllItems"); g.get("gt6", "TmpItems"); g.call("app", K_ARR, "Array_Append", inp={"TargetArray": "@ga1.AllItems", "SourceArray": "@gt6.TmpItems"})
    # pseudo slot "All": all slot lists in slot order (for "All" / search across everything)
    g.get("ga2", "AllItems"); g.make("mall", S_LIST, Items="@ga2.AllItems")
    alln = g.lit_name("alln", "All"); g.get("gc4", "Catalog"); g.call("madda", K_MAP, "Map_Add", inp={"TargetMap": "@gc4.Catalog", "Key": alln, "Value": "@mall.S_ItemList"})
    g.get("ga3", "AllItems"); g.call("alen", K_ARR, "Array_Length", inp={"TargetArray": "@ga3.AllItems"})
    g.get("gsc2", "SlotCounts"); g.call("scadda", K_MAP, "Map_Add", inp={"TargetMap": "@gsc2.SlotCounts", "Key": alln, "Value": "@alen.ReturnValue"})
    g.n("smi", "call_self", function="Scan Mod Items")
    g.chain("entry", "smi", "clr0", "clr1", "clr2", "clr3", "clr4", "rt", "os", "ra", "scr", "fe")
    g.chain("fe", "bign", "row", "sdn", "sslot", "sk", "sk2", "madd", "madd2", "sn1", "sna", "snadd")      # row: "Row Found" is the first exec output
    g.chain("fe:Completed", "bu", "addu", "maddu", "aclr", "fa"); g.chain("bu:else", "aclr")
    g.chain("fa", "tclr0", "tclr1", "tclr2", "sn2", "fn"); g.chain("fn", "sti", "sk1", "sk2s", "lo0", "hi0", "bs")
    g.chain("bs", "bopen", "bless", "hi1"); g.chain("bless:else", "lo1"); g.chain("bs:Completed", "ins", "insk", "insk2")
    g.chain("fn:Completed", "cadd", "scadd", "app"); g.chain("fa:Completed", "madda", "scadda")
    return fn("Build Catalog", graph=g)


# ---------------- Queries ----------------
def f_items_for_slot():
    g = G()
    g.get("gc", "Catalog"); g.call("find", K_MAP, "Map_Find", inp={"TargetMap": "@gc.Catalog", "Key": "@entry.slot"})
    g.brk("bl", S_LIST, "@find.Value")
    g.link("bl.Items", "return.items")
    return fn("Items For Slot", [param("slot", "name")], [param("items", T_ITEM, "array")], graph=g, pure=True)


def f_slot_count():
    """Items per slot from SlotCounts (filled by Build Catalog; unknown slot -> 0) - no copy of the slot list."""
    g = G()
    g.get("g", "SlotCounts"); g.call("find", K_MAP, "Map_Find", inp={"TargetMap": "@g.SlotCounts", "Key": "@entry.slot"})
    g.link("find.Value", "return.n")
    return fn("Slot Count", [param("slot", "name")], [param("n", "int")], graph=g, pure=True)


def f_item_slot():
    g = G()
    g.get("g", "ItemSlot"); g.call("find", K_MAP, "Map_Find", inp={"TargetMap": "@g.ItemSlot", "Key": "@entry.name"})
    g.link("find.Value", "return.slot")
    return fn("Item Slot", [param("name", "name")], [param("slot", "name")], graph=g, pure=True)


def f_is_worn():
    g = G()
    g.get("g", "Worn"); g.call("c", K_ARR, "Array_Contains", inp={"TargetArray": "@g.Worn", "ItemToFind": "@entry.name"})
    g.link("c.ReturnValue", "return.yes")
    return fn("Is Worn", [param("name", "name")], [param("yes", "bool")], graph=g, pure=True)


def f_is_owned():
    g = G()
    g.get("g", "OwnedSet"); g.call("c", K_SET, "Set_Contains", inp={"TargetSet": "@g.OwnedSet", "ItemToFind": "@entry.name"})
    g.link("c.ReturnValue", "return.yes")
    return fn("Is Owned", [param("name", "name")], [param("yes", "bool")], graph=g, pure=True)


def f_worn_in_slot():
    g = G()
    g.set("s0", "TmpName", inp={"TmpName": "None"})
    g.get("gw", "Worn"); g.foreach("fe", "@gw.Worn")
    g.n("isl", "call_self", function="Item Slot", inp={"name": "@fe.Array Element"})
    g.call("eq", K_MATH, "EqualEqual_NameName", inp={"A": "@isl.slot", "B": "@entry.slot"})
    g.get("gt", "TmpName"); g.call("eqn", K_MATH, "EqualEqual_NameName", inp={"A": "@gt.TmpName", "B": "None"})
    g.call("and", K_MATH, "BooleanAND", inp={"A": "@eq.ReturnValue", "B": "@eqn.ReturnValue"})
    g.branch("b", "@and.ReturnValue")
    g.set("s1", "TmpName", inp={"TmpName": "@fe.Array Element"})
    g.get("gt2", "TmpName"); g.link("gt2.TmpName", "return.name")
    g.chain("entry", "s0", "fe"); g.chain("fe", "b", "s1"); g.chain("fe:Completed", "return")
    return fn("Worn In Slot", [param("slot", "name")], [param("name", "name")], graph=g)


# ---------------- State + Actions ----------------
def f_refresh_state():
    g = G()
    g.get("gp", "Player"); g.call("w", P_CPB, "Get Wearing Clothes Names", inp={"self": "@gp.Player"})
    g.set("sw", "Worn", inp={"Worn": "@w.clothes list"})
    g.call("gs", K_GS, "GetGameState"); g.cast("cgs", P_GS, "@gs.ReturnValue")
    g.call("wd", P_GS, "Get Wardrobe Data", inp={"self": "@cgs.AsTKA Game State Base"})
    g.get("gcl", "Clothes", cls=P_WD); g.link("wd.wardrobe data", "gcl.self")
    g.set("so", "Owned", inp={"Owned": "@gcl.Clothes"})
    g.get("gos", "OwnedSet"); g.call("sclr", K_SET, "Set_Clear", inp={"TargetSet": "@gos.OwnedSet"})
    g.get("gos2", "OwnedSet"); g.get("go2", "Owned"); g.call("sadd", K_SET, "Set_AddItems", inp={"TargetSet": "@gos2.OwnedSet", "NewItems": "@go2.Owned"})
    g.chain("entry", "w", "sw", "wd", "so", "sclr", "sadd")
    return fn("Refresh State", graph=g)


def f_wear():
    g = G()
    g.get("gp", "Player"); g.call("w", P_CPB, "Wear The Clothes", inp={"self": "@gp.Player", "name": "@entry.name", "check covering": "true", "update mask": "true", "ignore compatible": "false"})
    g.branch("b", "@w.successed")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"})
    g.n("mk", "call_self", function="T", inp={"key": "Msg_WearFailed"}); g.call("mks", K_TXT, "Conv_TextToString", inp={"InText": "@mk.text"})
    g.call("msg", K_STR, "Concat_StrStr", inp={"A": "@mks.ReturnValue", "B": "@n2s.ReturnValue"})
    pop(g, "pop", text_from_str(g, "t", "@msg.ReturnValue"))
    g.get("gp2", "Player"); g.call("sa", P_JODI, "Save Appearance", inp={"self": "@gp2.Player"})
    g.n("rs", "call_self", function="Refresh State")
    g.chain("entry", "w", "b", "sa", "rs"); g.chain("b:else", "pop", "sa")
    return fn("Wear", [param("name", "name")], graph=g)


def f_take_off():
    g = G()
    g.get("gp", "Player"); g.call("t", P_CPB, "Take off this clothes", inp={"self": "@gp.Player", "clothes name": "@entry.name"})
    g.get("gp2", "Player"); g.call("sa", P_JODI, "Save Appearance", inp={"self": "@gp2.Player"})
    g.n("rs", "call_self", function="Refresh State")
    g.chain("entry", "t", "sa", "rs")
    return fn("Take Off", [param("name", "name")], graph=g)


def f_debug_status():
    g = G()
    g.get("gr", "CatalogRows"); g.get("gs", "Slots"); g.call("ls", K_ARR, "Array_Length", inp={"TargetArray": "@gs.Slots"})
    g.get("gw", "Worn"); g.call("lw", K_ARR, "Array_Length", inp={"TargetArray": "@gw.Worn"})
    g.get("go", "Owned"); g.call("lo", K_ARR, "Array_Length", inp={"TargetArray": "@go.Owned"})
    g.call("b1", K_STR, "BuildString_Int", inp={"AppendTo": "", "Prefix": "AltUI OK: ", "InInt": "@gr.CatalogRows", "Suffix": " items, "})
    g.call("b2", K_STR, "BuildString_Int", inp={"AppendTo": "@b1.ReturnValue", "Prefix": "", "InInt": "@ls.ReturnValue", "Suffix": " Slots, "})
    g.call("b3", K_STR, "BuildString_Int", inp={"AppendTo": "@b2.ReturnValue", "Prefix": "", "InInt": "@lw.ReturnValue", "Suffix": " worn, "})
    g.call("b4", K_STR, "BuildString_Int", inp={"AppendTo": "@b3.ReturnValue", "Prefix": "", "InInt": "@lo.ReturnValue", "Suffix": " owned"})
    g.n("rs", "call_self", function="Refresh State")
    pop(g, "pop", text_from_str(g, "t", "@b4.ReturnValue"))
    g.chain("entry", "rs", "pop")
    return fn("Debug Status", graph=g)


# ---------------- Find Item(name) -> item, found ----------------
def f_find_item():
    g = G()
    g.get("g", "ItemByName"); g.call("find", K_MAP, "Map_Find", inp={"TargetMap": "@g.ItemByName", "Key": "@entry.name"})
    g.link("find.Value", "return.item"); g.link("find.ReturnValue", "return.found")
    g.chain("entry", "return")
    return fn("Find Item", [param("name", "name")], [param("item", T_ITEM), param("found", "bool")], graph=g)


def f_is_favorite():
    g = G()
    g.get("g", "Favorites"); g.call("c", K_ARR, "Array_Contains", inp={"TargetArray": "@g.Favorites", "ItemToFind": "@entry.name"})
    g.link("c.ReturnValue", "return.yes")
    return fn("Is Favorite", [param("name", "name")], [param("yes", "bool")], graph=g, pure=True)


# ---------------- Filtered Items(slot, group, search, onlyOwned, onlyFav) -> items ----------------
# group: None = all groups; "Basis" = pieces without a group (Group == None)
def f_filtered_items():
    g = G()
    g.n("it", "call_self", function="Items For Slot", inp={"slot": "@entry.slot"})
    g.set("sti", "TmpSlotItems", inp={"TmpSlotItems": "@it.items"}); g.get("gsi", "TmpSlotItems")
    g.get("gt0", "TmpItems"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gt0.TmpItems"})
    g.call("ls", K_STR, "ToLower", inp={"SourceString": "@entry.search"}); g.set("ss", "TmpStr", inp={"TmpStr": "@ls.ReturnValue"})
    g.foreach("fe", "@gsi.TmpSlotItems"); g.brk("b", S_ITEM, "@fe.Array Element")
    # hidden: group "Hidden" -> only hidden pieces (group check skipped); otherwise hidden pieces are dropped
    g.call("gHid", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.group", "B": "Hidden"})
    g.n("ih", "call_self", function="Is Item Hidden", inp={"name": "@b.Name"})
    g.call("hEq", K_MATH, "EqualEqual_BoolBool", inp={"A": "@ih.yes", "B": "@gHid.ReturnValue"})   # hidden == (group is Hidden)
    # group
    g.call("gAll", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.group", "B": "None"})
    g.call("gBasis", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.group", "B": "Basis"})
    g.call("iNone", K_MATH, "EqualEqual_NameName", inp={"A": "@b.Group", "B": "None"})
    g.call("gEq", K_MATH, "EqualEqual_NameName", inp={"A": "@b.Group", "B": "@entry.group"})
    g.call("gB", K_MATH, "BooleanAND", inp={"A": "@gBasis.ReturnValue", "B": "@iNone.ReturnValue"})
    g.call("gOk1", K_MATH, "BooleanOR", inp={"A": "@gAll.ReturnValue", "B": "@gB.ReturnValue"})
    g.call("gOk", K_MATH, "BooleanOR", inp={"A": "@gOk1.ReturnValue", "B": "@gEq.ReturnValue"})
    g.call("gOkH", K_MATH, "BooleanOR", inp={"A": "@gOk.ReturnValue", "B": "@gHid.ReturnValue"})
    # search
    g.get("gts", "TmpStr"); g.call("sEmpty", K_STR, "IsEmpty", inp={"InString": "@gts.TmpStr"})
    g.call("dl", K_STR, "ToLower", inp={"SourceString": "@b.DisplayName"})
    g.get("gts2", "TmpStr"); g.call("sHit", K_STR, "Contains", inp={"SearchIn": "@dl.ReturnValue", "Substring": "@gts2.TmpStr", "bUseCase": "false", "bSearchFromEnd": "false"})
    g.call("sOk", K_MATH, "BooleanOR", inp={"A": "@sEmpty.ReturnValue", "B": "@sHit.ReturnValue"})
    # owned / favourite
    g.n("io", "call_self", function="Is Owned", inp={"name": "@b.Name"}); g.n("ifv", "call_self", function="Is Favorite", inp={"name": "@b.Name"})
    g.call("nO", K_MATH, "Not_PreBool", inp={"A": "@entry.onlyOwned"}); g.call("oOk", K_MATH, "BooleanOR", inp={"A": "@nO.ReturnValue", "B": "@io.yes"})
    g.call("nF", K_MATH, "Not_PreBool", inp={"A": "@entry.onlyFav"}); g.call("fOk", K_MATH, "BooleanOR", inp={"A": "@nF.ReturnValue", "B": "@ifv.yes"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@gOkH.ReturnValue", "B": "@sOk.ReturnValue"})
    g.call("a2", K_MATH, "BooleanAND", inp={"A": "@oOk.ReturnValue", "B": "@fOk.ReturnValue"})
    g.call("a3", K_MATH, "BooleanAND", inp={"A": "@a2.ReturnValue", "B": "@hEq.ReturnValue"})
    g.call("all", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@a3.ReturnValue"})
    g.branch("br", "@all.ReturnValue")
    g.get("gt1", "TmpItems"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gt1.TmpItems", "NewItem": "@fe.Array Element"})
    g.get("gt2", "TmpItems"); g.link("gt2.TmpItems", "return.items")
    g.chain("entry", "sti", "clr", "ss", "fe"); g.chain("fe", "br", "add"); g.chain("fe:Completed", "return")
    return fn("Filtered Items", [param("slot", "name"), param("group", "name"), param("search", "string"), param("onlyOwned", "bool"), param("onlyFav", "bool")],
              [param("items", T_ITEM, "array")], graph=g)


# ---------------- Groups Of Slot(slot) -> groups (None -> "Basis"; unique, order of first occurrence) ----------------
def f_groups_of_slot():
    g = G()
    g.n("it", "call_self", function="Items For Slot", inp={"slot": "@entry.slot"})
    g.set("sti", "TmpSlotItems", inp={"TmpSlotItems": "@it.items"}); g.get("gsi", "TmpSlotItems")
    g.get("gn0", "TmpNames"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gn0.TmpNames"})
    g.foreach("fe", "@gsi.TmpSlotItems"); g.brk("b", S_ITEM, "@fe.Array Element")
    g.call("isN", K_MATH, "EqualEqual_NameName", inp={"A": "@b.Group", "B": "None"})
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@b.Group"})
    g.call("sel", K_MATH, "SelectString", inp={"A": "Basis", "B": "@n2s.ReturnValue", "bPickA": "@isN.ReturnValue"})
    g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@sel.ReturnValue"})
    g.get("gn1", "TmpNames"); g.call("add", K_ARR, "Array_AddUnique", inp={"TargetArray": "@gn1.TmpNames", "NewItem": "@s2n.ReturnValue"})
    # "Hidden" as the last sub tab if at least one piece of the slot is hidden
    g.set("hf0", "TmpFound", inp={"TmpFound": "false"})
    g.get("gsi2", "TmpSlotItems"); g.foreach("fh", "@gsi2.TmpSlotItems"); g.brk("bh", S_ITEM, "@fh.Array Element")
    g.n("ih", "call_self", function="Is Item Hidden", inp={"name": "@bh.Name"}); g.branch("bih", "@ih.yes"); g.set("hf1", "TmpFound", inp={"TmpFound": "true"})
    g.get("ghf", "TmpFound"); g.branch("bhf", "@ghf.TmpFound")
    hid = g.lit_name("lh", "Hidden"); g.get("gn3", "TmpNames"); g.call("addh", K_ARR, "Array_Add", inp={"TargetArray": "@gn3.TmpNames", "NewItem": hid})
    g.get("gn2", "TmpNames"); g.link("gn2.TmpNames", "return.groups")
    g.chain("entry", "sti", "clr", "fe"); g.chain("fe", "add"); g.chain("fe:Completed", "hf0", "fh"); g.chain("fh", "bih", "hf1"); g.chain("fh:Completed", "bhf", "addh", "return"); g.chain("bhf:else", "return")
    return fn("Groups Of Slot", [param("slot", "name")], [param("groups", "name", "array")], graph=g)


# ---------------- Group Caption(group) -> caption (text from com_ClothesGroup, else the group name) ----------------
def f_group_caption():
    g = G()
    g.call("isB", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.group", "B": "Basis"}); g.branch("bb", "@isB.ReturnValue")
    g.n("tb", "call_self", function="T", inp={"key": "Group_Basis"}); g.set("s1", "TmpText", inp={"TmpText": "@tb.text"})
    g.call("isH", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.group", "B": "Hidden"}); g.branch("bh", "@isH.ReturnValue")
    g.n("th", "call_self", function="T", inp={"key": "Group_Hidden"}); g.set("s4", "TmpText", inp={"TmpText": "@th.text"})
    g.n("row", "get_row", table=P_CG, inp={"RowName": "@entry.group"})
    g.brk("br", P_CGS, "@row.OutRow"); g.set("s2", "TmpText", inp={"TmpText": "@br.GroupName"})
    g.call("tn", K_TXT, "Conv_NameToText", inp={"InName": "@entry.group"}); g.set("s3", "TmpText", inp={"TmpText": "@tn.ReturnValue"})
    g.get("gt", "TmpText"); g.link("gt.TmpText", "return.caption")
    g.chain("entry", "bb", "s1", "return"); g.chain("bb:else", "bh", "s4", "return"); g.chain("bh:else", "row", "s2", "return"); g.chain("row:Row Not Found", "s3", "return")
    return fn("Group Caption", [param("group", "name")], [param("caption", "text")], graph=g)


# ---------------- Item Tip(item) -> tip: display name, slot label, origin (Vanilla / Mod [· group]), row name ----------------
def f_item_tip():
    g = G(); g.brk("b", S_ITEM, "@entry.item")
    g.n("isl", "call_self", function="Item Slot", inp={"name": "@b.Name"})
    g.call("sn", K_STR, "Conv_NameToString", inp={"InName": "@isl.slot"}); g.call("sk", K_STR, "Concat_StrStr", inp={"A": "Slot_", "B": "@sn.ReturnValue"})
    g.call("skn", K_STR, "Conv_StringToName", inp={"InString": "@sk.ReturnValue"}); g.n("ts", "call_self", function="T", inp={"key": "@skn.ReturnValue"})
    g.call("ss", K_TXT, "Conv_TextToString", inp={"InText": "@ts.text"})
    # origin: "Vanilla" or "Mod", plus " · <group caption>" when the piece has a group
    g.n("tv", "call_self", function="T", inp={"key": "Tip_Vanilla"}); g.call("sv", K_TXT, "Conv_TextToString", inp={"InText": "@tv.text"})
    g.n("tm", "call_self", function="T", inp={"key": "Tip_Mod"}); g.call("sm", K_TXT, "Conv_TextToString", inp={"InText": "@tm.text"})
    g.get("gio", "ItemOrigin"); g.call("of", K_MAP, "Map_Find", inp={"TargetMap": "@gio.ItemOrigin", "Key": "@b.Name"}); g.call("ofs", K_TXT, "Conv_TextToString", inp={"InText": "@of.Value"})
    g.call("modn", K_MATH, "SelectString", inp={"A": "@ofs.ReturnValue", "B": "@sm.ReturnValue", "bPickA": "@of.ReturnValue"})
    g.call("org", K_MATH, "SelectString", inp={"A": "@sv.ReturnValue", "B": "@modn.ReturnValue", "bPickA": "@b.IsVanilla"})
    g.call("gn", K_MATH, "EqualEqual_NameName", inp={"A": "@b.Group", "B": "None"}); g.branch("bg", "@gn.ReturnValue")
    g.n("gc", "call_self", function="Group Caption", inp={"group": "@b.Group"}); g.call("gcs", K_TXT, "Conv_TextToString", inp={"InText": "@gc.caption"})
    g.call("og1", K_STR, "Concat_StrStr", inp={"A": "@org.ReturnValue", "B": " \u00b7 "}); g.call("og2", K_STR, "Concat_StrStr", inp={"A": "@og1.ReturnValue", "B": "@gcs.ReturnValue"})
    g.set("so1", "TmpStr", inp={"TmpStr": "@og2.ReturnValue"}); g.set("so2", "TmpStr", inp={"TmpStr": "@org.ReturnValue"})
    # assemble: name \n slot \n origin [\n row]
    g.get("go", "TmpStr")
    g.call("l1", K_STR, "Concat_StrStr", inp={"A": "@b.DisplayName", "B": "\n"}); g.call("l2", K_STR, "Concat_StrStr", inp={"A": "@l1.ReturnValue", "B": "@ss.ReturnValue"})
    g.call("l3", K_STR, "Concat_StrStr", inp={"A": "@l2.ReturnValue", "B": "\n"}); g.call("l4", K_STR, "Concat_StrStr", inp={"A": "@l3.ReturnValue", "B": "@go.TmpStr"})
    g.call("rn", K_STR, "Conv_NameToString", inp={"InName": "@b.Name"}); g.call("same", K_STR, "EqualEqual_StrStr", inp={"A": "@rn.ReturnValue", "B": "@b.DisplayName"})
    g.call("l5", K_STR, "Concat_StrStr", inp={"A": "@l4.ReturnValue", "B": "\n"}); g.call("l6", K_STR, "Concat_StrStr", inp={"A": "@l5.ReturnValue", "B": "@rn.ReturnValue"})
    g.call("sel", K_MATH, "SelectString", inp={"A": "@l4.ReturnValue", "B": "@l6.ReturnValue", "bPickA": "@same.ReturnValue"})
    g.call("tt", K_TXT, "Conv_StringToText", inp={"InString": "@sel.ReturnValue"}); g.link("tt.ReturnValue", "return.tip")
    g.chain("entry", "bg", "so2", "return"); g.chain("bg:else", "gc", "so1", "return")
    return fn("Item Tip", [param("item", T_ITEM)], [param("tip", "text")], graph=g)


SG = M + "/SG_AltUI"
SLOT_NAME = "AltUI"


# ---------------- Language: T(key) pure, Detect Language, Init Strings ----------------
def f_t():
    g = G()
    g.get("gs", "Strings"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gs.Strings", "Key": "@entry.key"})
    g.call("vs", K_TXT, "Conv_TextToString", inp={"InText": "@f.Value"}); g.call("ks", K_STR, "Conv_NameToString", inp={"InName": "@entry.key"})
    g.call("sel", K_MATH, "SelectString", inp={"A": "@vs.ReturnValue", "B": "@ks.ReturnValue", "bPickA": "@f.ReturnValue"})   # no SelectText in 4.27
    g.call("st", K_TXT, "Conv_StringToText", inp={"InString": "@sel.ReturnValue"}); g.link("st.ReturnValue", "return.text")
    return fn("T", [param("key", "name")], [param("text", "text")], graph=g, pure=True)


def f_detect_language():
    """LangChoice > 0 -> Lang = LangChoice - 1; otherwise the game language: prefix from LANGS[1:] (de* -> 1, zh* -> 2, ru* -> 3, es* -> 4), else 0 (en)."""
    g = G()
    g.get("gc", "LangChoice"); g.call("gt", K_MATH, "Greater_IntInt", inp={"A": "@gc.LangChoice", "B": "0"}); g.branch("b", "@gt.ReturnValue")
    g.call("m1", K_MATH, "Subtract_IntInt", inp={"A": "@gc.LangChoice", "B": "1"}); g.set("s1", "Lang", inp={"Lang": "@m1.ReturnValue"})
    g.call("cl", "/Script/Engine.KismetInternationalizationLibrary", "GetCurrentLanguage")
    prev = "0"
    for i, lang in enumerate(LANGS[1:], 1):
        g.call("p%d" % i, K_STR, "StartsWith", inp={"SourceString": "@cl.ReturnValue", "InPrefix": lang, "SearchCase": "IgnoreCase"})
        g.call("i%d" % i, K_MATH, "SelectInt", inp={"A": str(i), "B": prev, "bPickA": "@p%d.ReturnValue" % i}); prev = "@i%d.ReturnValue" % i
    g.set("s2", "Lang", inp={"Lang": prev})
    g.chain("entry", "b", "s1"); g.chain("b:else", "s2")
    return fn("Detect Language", graph=g)


def f_init_strings():
    """Fill the Strings map for Lang: column LANGS[Lang], empty cell -> en."""
    g = G()
    g.get("gs", "Strings"); g.call("mc", K_MAP, "Map_Clear", inp={"TargetMap": "@gs.Strings"})
    g.call("rn", K_DT, "GetDataTableRowNames", inp={"Table": T_STRINGS}); g.foreach("fe", "@rn.OutRowNames")
    g.n("row", "get_row", table=T_STRINGS, inp={"RowName": "@fe.Array Element"}, miss="ignore"); g.brk("br", S_STR, "@row.OutRow")   # row names of the same table
    g.get("gl", "Lang"); g.call("sen", K_TXT, "Conv_TextToString", inp={"InText": "@br.en"}); prev = "@sen.ReturnValue"
    for i, lang in enumerate(LANGS[1:], 1):
        g.call("is%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": "@gl.Lang", "B": str(i)}); g.call("s%s" % lang, K_TXT, "Conv_TextToString", inp={"InText": "@br." + lang})
        g.call("t%d" % i, K_MATH, "SelectString", inp={"A": "@s%s.ReturnValue" % lang, "B": prev, "bPickA": "@is%d.ReturnValue" % i}); prev = "@t%d.ReturnValue" % i
    g.call("emp", K_STR, "IsEmpty", inp={"InString": prev}); g.call("tf", K_MATH, "SelectString", inp={"A": "@sen.ReturnValue", "B": prev, "bPickA": "@emp.ReturnValue"})
    g.call("tft", K_TXT, "Conv_StringToText", inp={"InString": "@tf.ReturnValue"})
    g.get("gs2", "Strings"); g.call("ma", K_MAP, "Map_Add", inp={"TargetMap": "@gs2.Strings", "Key": "@fe.Array Element", "Value": "@tft.ReturnValue"})
    g.chain("entry", "mc", "rn", "fe"); g.chain("fe", "row", "ma")
    return fn("Init Strings", graph=g)


# ---------------- Load Settings / Save Settings / Toggle Favorite ----------------
# Persisted settings (manager variable, SG_AltUI variable, kind, default). kind: "copy" = as is; "name" = None means unset;
# "float0" = saves before SAVE_VERSION 1 had no version and used 0 as "never set" -> default (with SaveVersion >= 1 a 0 is a real value:
# camera distance 0 %, opacity 0 %). Both Load Settings and Save Settings are generated from this table.
SAVE_VERSION = 1
SETTINGS = [("Favorites", "Favorites", "copy", None), ("HiddenItems", "HiddenItems", "copy", None),
            ("CachedOnlyOwned", "OnlyOwned", "copy", None), ("CachedOnlyFav", "OnlyFav", "copy", None),
            ("ScrollMult", "ScrollMult", "float0", 4.0), ("TileScale", "TileScale", "float0", 1.0),
            ("Unlimited", "Unlimited", "copy", None), ("LeftFree", "LeftFree", "copy", None),
            ("CamFov", "CamFov", "float0", 0.8), ("CamDist", "CamDist", "float0", 1.0),
            ("BodyVariant", "BodyVariant", "copy", None), ("LangChoice", "LangChoice", "copy", None),
            ("PanToSlot", "PanToSlot", "copy", None), ("AllowNude", "AllowNude", "copy", None), ("ToggleKey", "ToggleKey", "name", None)]
THEME_SETTINGS = [("Theme" + k, "Theme" + k, "copy", None) for k, _, _ in THEME] + [("BgAlpha", "BgAlpha", "float0", BG_ALPHA), ("TileAlpha", "TileAlpha", "float0", TILE_ALPHA)]


def sg_get(g, id, sg_var):
    """Settings.<sg_var> -> pin (get via class SG_AltUI)."""
    g.get(id + "_s", "Settings"); g.get(id, sg_var, cls=SG); g.link(id + "_s.Settings", id + ".self"); return "@%s.%s" % (id, sg_var)


def load_setting(g, i, mgr_var, sg_var, kind, default, versioned_pin):
    """Nodes that take Settings.<sg_var> into <mgr_var>; returns the exec ids (a "name" entry ends in a branch whose else-path is the skip)."""
    src = sg_get(g, "lg%d" % i, sg_var)
    if kind == "float0":
        g.call("lz%d" % i, K_MATH, "Greater_FloatFloat", inp={"A": src, "B": "0.0"}); g.call("lv%d" % i, K_MATH, "BooleanOR", inp={"A": versioned_pin, "B": "@lz%d.ReturnValue" % i})
        g.call("ld%d" % i, K_MATH, "SelectFloat", inp={"A": src, "B": str(default), "bPickA": "@lv%d.ReturnValue" % i}); src = "@ld%d.ReturnValue" % i
    g.set("ls%d" % i, mgr_var, inp={mgr_var: src})
    if kind == "name":
        g.call("ln%d" % i, K_MATH, "NotEqual_NameName", inp={"A": src, "B": "None"}); g.branch("lb%d" % i, "@ln%d.ReturnValue" % i)
        return ["lb%d" % i, "ls%d" % i]
    return ["ls%d" % i]


def f_load_settings():
    g = G()
    g.call("ex", K_GS, "DoesSaveGameExist", inp={"SlotName": SLOT_NAME, "UserIndex": "0"}); g.branch("b", "@ex.ReturnValue")
    g.call("ld", K_GS, "LoadGameFromSlot", inp={"SlotName": SLOT_NAME, "UserIndex": "0"}); g.cast("cl", SG, "@ld.ReturnValue")
    g.set("s1", "Settings", inp={"Settings": "@cl.AsSG_AltUI"})
    g.call("cr", K_GS, "CreateSaveGameObject", inp={"SaveGameClass": SG}); g.cast("cc", SG, "@cr.ReturnValue")
    g.set("s2", "Settings", inp={"Settings": "@cc.AsSG_AltUI"})
    # Settings None after a failed load/cast (corrupt file, class change) -> fresh object like Load Presets/Outfits/Looks
    g.get("gs", "Settings"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gs.Settings"}); g.branch("bv", "@iv.ReturnValue")
    g.call("ver", K_MATH, "GreaterEqual_IntInt", inp={"A": sg_get(g, "gver", "SaveVersion"), "B": "1"}); versioned = "@ver.ReturnValue"
    tail = ["bv"]; first = None
    for i, (mgr_var, sg_var, kind, default) in enumerate(SETTINGS):
        ids = load_setting(g, i, mgr_var, sg_var, kind, default, versioned); first = first or ids[0]
        if kind == "name": g.chain(*tail, *ids); tail = [ids[-1], ids[0] + ":else"]   # unset -> keep the manager default
        else: tail.append(ids[0])
    # theme: stored (ThemeSet) -> take over, otherwise defaults; derived colours in both cases
    g.branch("bth", sg_get(g, "gth", "ThemeSet")); ttail = ["bth"]
    for i, (mgr_var, sg_var, kind, default) in enumerate(THEME_SETTINGS, len(SETTINGS)):
        ttail += load_setting(g, i, mgr_var, sg_var, kind, default, versioned)
    g.n("rth", "call_self", function="Reset Theme"); g.n("ath", "call_self", function="Apply Theme")
    # last slot only if set (else the first slot, see Open Panel)
    g.get("gl", "LastSlot", cls=SG); g.get("gls", "Settings"); g.link("gls.Settings", "gl.self")
    g.call("eqn", K_MATH, "EqualEqual_NameName", inp={"A": "@gl.LastSlot", "B": "None"}); g.branch("bn", "@eqn.ReturnValue")
    g.set("sc", "CurrentSlot", inp={"CurrentSlot": "@gl.LastSlot"})
    g.chain("entry", "ex", "b", "ld", "s1", "bv"); g.chain("b:else", "cr", "s2", first); g.chain("bv:else", "cr")
    for t in tail: g.chain(t, "bth")
    g.chain(*ttail, "ath"); g.chain("bth:else", "rth", "ath"); g.chain("ath", "bn"); g.chain("bn:else", "sc")
    return fn("Load Settings", graph=g)


def f_save_settings():
    g = G()
    g.get("gs", "Settings"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gs.Settings"}); g.branch("bv", "@iv.ReturnValue")
    g.call("cr", K_GS, "CreateSaveGameObject", inp={"SaveGameClass": SG}); g.cast("cc", SG, "@cr.ReturnValue")
    g.set("s2", "Settings", inp={"Settings": "@cc.AsSG_AltUI"})
    tail = ["bv"]
    for i, (mgr_var, sg_var, kind, default) in enumerate(SETTINGS + THEME_SETTINGS):
        g.get("gs%d" % i, "Settings"); g.get("g%d" % i, mgr_var)
        g.n("w%d" % i, "set", var=sg_var, cls=SG, inp={"self": "@gs%d.Settings" % i, sg_var: "@g%d.%s" % (i, mgr_var)}); tail.append("w%d" % i)
    for name, val in (("LastSlot", "@gcs.CurrentSlot"), ("ThemeSet", "true"), ("SaveVersion", str(SAVE_VERSION))):
        g.get("gs_" + name, "Settings"); g.n("s_" + name, "set", var=name, cls=SG, inp={"self": "@gs_%s.Settings" % name, name: val}); tail.append("s_" + name)
    g.get("gcs", "CurrentSlot")
    g.get("gsv", "Settings"); g.call("sv", K_GS, "SaveGameToSlot", inp={"SaveGameObject": "@gsv.Settings", "SlotName": SLOT_NAME, "UserIndex": "0"})
    g.chain("entry", *tail, "sv"); g.chain("bv:else", "cr", "s2", tail[1])
    return fn("Save Settings", graph=g)


# ---------------- Theme (base colours -> derived colours; widgets refresh via ThemeVersion) ----------------
def f_reset_theme():
    g = G(); tail = ["entry"]
    for key, rgb, _ in THEME:
        g.set("s" + key, "Theme" + key, inp={"Theme" + key: rgb_lit(rgb)}); tail.append("s" + key)
    g.set("sba", "BgAlpha", inp={"BgAlpha": str(BG_ALPHA)}); g.set("sta", "TileAlpha", inp={"TileAlpha": str(TILE_ALPHA)}); tail += ["sba", "sta"]
    g.chain(*tail); return fn("Reset Theme", graph=g)


def f_theme_color():
    """Base colour by key (Bg, Accent, ...); unknown key -> black."""
    g = G(); prev = "entry"
    for i, (key, _, _) in enumerate(THEME):
        g.call("eq%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@entry.key", "B": key}); g.branch("b%d" % i, "@eq%d.ReturnValue" % i)
        g.get("g%d" % i, "Theme" + key); rid = "return" if i == 0 else "r%d" % i
        if i: g.n(rid, "return_new")
        g.link("g%d.Theme%s" % (i, key), rid + ".color"); g.chain(prev, "b%d" % i, rid); prev = "b%d:else" % i
    g.n("rx", "return_new"); g.chain(prev, "rx")
    return fn("Theme Color", [param("key", "name")], [param("color", S_LINCOLOR)], graph=g)


def f_set_theme_color():
    g = G(); prev = "entry"
    for i, (key, _, _) in enumerate(THEME):
        g.call("eq%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@entry.key", "B": key}); g.branch("b%d" % i, "@eq%d.ReturnValue" % i)
        g.set("s%d" % i, "Theme" + key, inp={"Theme" + key: "@entry.color"}); g.chain(prev, "b%d" % i, "s%d" % i); prev = "b%d:else" % i
    return fn("Set Theme Color", [param("key", "name"), param("color", S_LINCOLOR)], graph=g)


def f_layout_fraction():
    """LeftFree index -> free fraction of the screen (0 none, 1 third, 2 half, 3 quarter, 4 fifth)."""
    g = G(); src = "0.0"
    for i, (idx, frac) in enumerate(LAYOUT_FRACTIONS):
        g.call("e%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": "@entry.index", "B": str(idx)})
        g.call("s%d" % i, K_MATH, "SelectFloat", inp={"A": str(frac), "B": src, "bPickA": "@e%d.ReturnValue" % i}); src = "@s%d.ReturnValue" % i
    g.link("s%d.ReturnValue" % (len(LAYOUT_FRACTIONS) - 1), "return.fraction"); g.chain("entry", "return")
    return fn("Layout Fraction", [param("index", "int")], [param("fraction", "float")], graph=g)


LAYOUT_FRACTIONS = [(1, 0.3333), (2, 0.5), (3, 0.25), (4, 0.2)]   # LeftFree index -> fraction (0 = none)
LAYOUTS = [(0, "Lbl_LayoutNone"), (4, "Lbl_LayoutFifth"), (3, "Lbl_LayoutQuarter"), (1, "Lbl_LayoutThird"), (2, "Lbl_LayoutHalf")]   # display order (by size)


def f_toggle_favorite():
    g = G()
    g.n("isf", "call_self", function="Is Favorite", inp={"name": "@entry.name"}); g.branch("b", "@isf.yes")
    g.get("gf", "Favorites"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gf.Favorites", "Item": "@entry.name"})
    g.get("gf2", "Favorites"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gf2.Favorites", "NewItem": "@entry.name"})
    g.n("sv", "call_self", function="Save Settings")
    g.get("go", "PanelOpen"); g.branch("bo", "@go.PanelOpen"); g.n("rl", "call_self", function="Rebuild List")
    g.chain("entry", "b", "rm", "sv"); g.chain("b:else", "add", "sv"); g.chain("sv", "bo", "rl")
    return fn("Toggle Favorite", [param("name", "name")], graph=g)


# ---------------- Is Item Hidden / Toggle Item Hidden (names avoid AActor.bHidden / IsHidden) ----------------
def f_is_item_hidden():
    g = G()
    g.get("g", "HiddenItems"); g.call("c", K_ARR, "Array_Contains", inp={"TargetArray": "@g.HiddenItems", "ItemToFind": "@entry.name"})
    g.link("c.ReturnValue", "return.yes")
    return fn("Is Item Hidden", [param("name", "name")], [param("yes", "bool")], graph=g, pure=True)


def f_toggle_item_hidden():
    """Hide/unhide a piece; if the last hidden piece of the current slot was unhidden, leave the "Hidden" sub tab."""
    g = G()
    g.n("ish", "call_self", function="Is Item Hidden", inp={"name": "@entry.name"}); g.branch("b", "@ish.yes")
    g.get("gh", "HiddenItems"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gh.HiddenItems", "Item": "@entry.name"})
    g.get("gh2", "HiddenItems"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gh2.HiddenItems", "NewItem": "@entry.name"})
    g.n("sv", "call_self", function="Save Settings")
    # current group "Hidden" but no hidden piece left in the slot -> back to "All"
    g.get("gcg", "CurrentGroup"); g.call("eqh", K_MATH, "EqualEqual_NameName", inp={"A": "@gcg.CurrentGroup", "B": "Hidden"}); g.branch("bg", "@eqh.ReturnValue")
    g.get("gcs", "CurrentSlot"); g.n("gr", "call_self", function="Groups Of Slot", inp={"slot": "@gcs.CurrentSlot"})
    hid = g.lit_name("lh", "Hidden"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gr.groups", "ItemToFind": hid}); g.branch("bh", "@has.ReturnValue")
    g.set("scg", "CurrentGroup", inp={"CurrentGroup": "None"})
    g.get("go", "PanelOpen"); g.branch("bo", "@go.PanelOpen"); g.n("rt", "call_self", function="Rebuild SubTabs"); g.n("rl", "call_self", function="Rebuild List")
    g.chain("entry", "b", "rm", "sv"); g.chain("b:else", "add", "sv"); g.chain("sv", "bg", "gr", "bh", "bo"); g.chain("bh:else", "scg", "bo"); g.chain("bg:else", "bo"); g.chain("bo", "rt", "rl")
    return fn("Toggle Item Hidden", [param("name", "name")], graph=g)


# UI functions: signatures here (so widgets can reference them), bodies in gen_manager_ui.py
UI_SIGNATURES = [
    fn("Toggle Panel"), fn("Open Panel"), fn("Close Panel"), fn("Rebuild Left"), fn("Rebuild List"), fn("Rebuild SubTabs"),
    fn("Select Slot", [param("name", "name")]), fn("Take Off Slot", [param("name", "name")]),
    fn("On Item Clicked", [param("name", "name")]), fn("On Item Context", [param("name", "name")]),
    fn("Select SubTab", [param("name", "name")]), fn("On Search Changed", [param("text", "text")]),
    fn("On Menu Action", [param("name", "name")]), fn("Close Menu"),
    # Outfits (vanilla data: Outfits_Save in slot "Outfits")
    fn("Load Outfits"), fn("Save Outfits"), fn("Rebuild TopTabs"), fn("Rebuild Outfits"), fn("Select Page", [param("name", "name")]),
    fn("On Outfit Clicked", [param("index", "int")]), fn("On Outfit Context", [param("index", "int")]), fn("Delete Outfit", [param("index", "int")]),
    # Attire & Backpack (vanilla: Jodi.Use Clothes from Bag / Got Clothes, Bag_Comp, InventoryPanel.Repair Clothes)
    fn("Rebuild Bag"), fn("Bag Toggle Wear", [param("name", "name")]), fn("Bag Remove", [param("name", "name")]),
    fn("Bag Repair", [param("name", "name")]), fn("Bag To Wardrobe", [param("name", "name")]), fn("Put In Bag", [param("name", "name")]),
    fn("Is Damaged", [param("name", "name")], [param("yes", "bool")]), fn("In Bag", [param("name", "name")], [param("yes", "bool")]),
    fn("On Bag Item Context", [param("name", "name")]), fn("Bag Cleanup"),
    # Coiffure / Appearance / Body Shape
    fn("Join Names", [param("names", "name", "array")], [param("key", "string")]),
    fn("Outfit Key", [param("index", "int")], [param("key", "string")]),
    fn("Outfit Name By Key", [param("key", "string")], [param("name", "string")]),
    fn("Outfit Name", [param("index", "int")], [param("name", "string")]),
    fn("Set Outfit Name By Key", [param("key", "string"), param("name", "string")]),
    fn("Set Outfit Name", [param("index", "int"), param("name", "string")]),
    fn("Start Outfit Rename", [param("index", "int")]),
    fn("Rebuild Hair"), fn("Hair Clicked", [param("name", "name")]), fn("Open Hair Color"),
    fn("Rebuild Look Cats"), fn("Rebuild Look"), fn("Select Look Cat", [param("name", "name")]), fn("Look Clicked", [param("name", "name")]),
    fn("Look Caption", [param("type", "name")], [param("caption", "text")]), fn("Look Count", [param("type", "name")], [param("n", "int")]),
    fn("Is Look Selected", [param("type", "name"), param("style", "name")], [param("yes", "bool")]),
    fn("Rebuild Body"), fn("Poll Body"), fn("Save Appearance Data"),
    fn("Scan Body Mods"), fn("Apply Body", [param("name", "name")]), fn("Apply Saved Body"), fn("Select Body", [param("name", "name")]),
    fn("Select Language", [param("choice", "int")]), fn("Apply Strings"),
    fn("Focus Code", outputs=[param("code", "int")]), fn("Update Focus"),
    fn("Hair Reset Color", [param("name", "name")]), fn("Clothes Reset Color", [param("name", "name")]), fn("On Hair Context", [param("name", "name")]), fn("Apply Nude"), fn("Fix Loaded Underwear"),
    fn("Rebuild Options"), fn("Poll Options"), fn("Apply Options"), fn("Apply Theme"), fn("Open Theme Color", [param("key", "name")]), fn("Select Key", [param("name", "name")]),
    fn("Load Presets"), fn("Preset Icon", [param("number", "int")], [param("tex", "object:" + E_TEX2D)]), fn("Preset Clicked", [param("index", "int")]),
    fn("Preset Delete", [param("index", "int")]), fn("Preset Add"), fn("On Preset Context", [param("index", "int")]), fn("Preset Index", [param("name", "name")], [param("index", "int")]),
    fn("Capture Preset Icon", [param("number", "int")]),
    fn("Select Layout", [param("name", "name")]), fn("Rebuild Status"), fn("Set View Shift"),
    fn("Take Snapshot", outputs=[param("snap", "struct:" + S_SNAP)]), fn("Push History"), fn("Apply Snapshot", [param("snap", "struct:" + S_SNAP)]), fn("Undo"), fn("Redo"),
    fn("Load Looks"), fn("Save Looks"), fn("Looks Count", outputs=[param("n", "int")]), fn("Add Look"), fn("Update Look", [param("index", "int")]), fn("Delete Look", [param("index", "int")]),
    fn("Look Name", [param("index", "int")], [param("name", "string")]), fn("Set Look Name", [param("index", "int"), param("name", "string")]), fn("Apply Look", [param("index", "int")]),
    fn("Rebuild Looks"), fn("On Look Clicked", [param("index", "int")]), fn("On Look Context", [param("index", "int")]), fn("Start Look Rename", [param("index", "int")]),
    fn("Look Icon", [param("id", "int")], [param("tex", "object:" + E_TEX2D)]), fn("Capture Look Photo", [param("id", "int")]),
    fn("Capture Photo", [param("target", "struct:/Script/CoreUObject.Vector"), param("distance", "float"), param("rise", "float"), param("width", "int"), param("height", "int"), param("dir", "string"), param("file", "string")]), fn("Finish Photo"),
    # content view
    fn("Content Open", [param("page", "name")], [param("yes", "bool")]), fn("Open Content", [param("kind", "name"), param("index", "int")]),
    fn("Open Outfit Content", [param("index", "int")]), fn("Open Look Content", [param("index", "int")]), fn("Open Preset Content", [param("index", "int")]), fn("Close Content"),
    fn("Content Snapshot", [param("kind", "name"), param("index", "int")], [param("ok", "bool")]), fn("Rebuild Content"),
    fn("On Content Item Context", [param("name", "name")]), fn("Go To Item", [param("name", "name")]), fn("Scroll To Highlight"),
]


# ---------------- Event Graph (base; rebuilt completely in 50_manager_ui.json) ----------------
def event_graph():
    g = G()
    g.event("bp", E_ACTOR, "ReceiveBeginPlay")
    g.call("own", E_ACTOR, "GetOwner"); g.cast("cpc", P_PC, "@own.ReturnValue", pure=False, miss="ignore")   # spawned by the camera hook with the controller as owner
    g.set("spc", "PC", inp={"PC": "@cpc.AsTKA Controller"})
    g.call("ei", E_ACTOR, "EnableInput", inp={"PlayerController": "@spc.Output_Get"})
    g.call("gp", E_CTRL, "K2_GetPawn", inp={"self": "@spc.Output_Get"}); g.cast("cj", P_JODI, "@gp.ReturnValue", pure=False, miss="ignore")   # no Jodi (main menu): stay idle
    g.set("spl", "Player", inp={"Player": "@cj.AsJodi"})
    g.n("isg", "call_self", function="Init Slot Groups"); g.n("bc", "call_self", function="Build Catalog"); g.n("rs", "call_self", function="Refresh State")
    g.chain("bp", "cpc", "spc", "ei", "cj", "spl", "isg", "bc", "rs")
    # test entry points for editor Python (events have no locals -> call_method works)
    g.custom("tb", "Test Build"); g.n("tb_i", "call_self", function="Init Slot Groups"); g.n("tb_b", "call_self", function="Build Catalog")
    g.chain("tb", "tb_i", "tb_b")
    g.custom("tk", "Test Sort Key", [param("s", "string")]); g.n("tk_k", "call_self", function="Sort Key", inp={"s": "@tk.s"})
    g.set("tk_s", "TmpKey", inp={"TmpKey": "@tk_k.key"}); g.chain("tk", "tk_k", "tk_s")
    # Test Items(slot): TmpNames = names in order, TmpIdx = count, TmpName/TmpFound = Group/IsVanilla of the first
    g.custom("ti", "Test Items", [param("slot", "name")])
    g.n("ti_it", "call_self", function="Items For Slot", inp={"slot": "@ti.slot"})
    g.get("ti_gn", "TmpNames"); g.call("ti_clr", K_ARR, "Array_Clear", inp={"TargetArray": "@ti_gn.TmpNames"})
    g.call("ti_len", K_ARR, "Array_Length", inp={"TargetArray": "@ti_it.items"}); g.set("ti_cnt", "TmpIdx", inp={"TmpIdx": "@ti_len.ReturnValue"})
    g.set("ti_n0", "TmpName", inp={"TmpName": "None"}); g.set("ti_f0", "TmpFound", inp={"TmpFound": "false"})
    g.foreach("ti_fe", "@ti_it.items"); g.brk("ti_b", S_ITEM, "@ti_fe.Array Element")
    g.get("ti_gn2", "TmpNames"); g.call("ti_add", K_ARR, "Array_Add", inp={"TargetArray": "@ti_gn2.TmpNames", "NewItem": "@ti_b.Name"})
    g.call("ti_eq0", K_MATH, "EqualEqual_IntInt", inp={"A": "@ti_fe.Array Index", "B": "0"}); g.branch("ti_bb", "@ti_eq0.ReturnValue")
    g.set("ti_sg", "TmpName", inp={"TmpName": "@ti_b.Group"}); g.set("ti_sv", "TmpFound", inp={"TmpFound": "@ti_b.IsVanilla"})
    g.chain("ti", "ti_clr", "ti_cnt", "ti_n0", "ti_f0", "ti_fe"); g.chain("ti_fe", "ti_add", "ti_bb", "ti_sg", "ti_sv")
    g.custom("tw", "Test Worn In Slot", [param("slot", "name")]); g.n("tw_w", "call_self", function="Worn In Slot", inp={"slot": "@tw.slot"})
    g.set("tw_s", "TmpName", inp={"TmpName": "@tw_w.name"}); g.chain("tw", "tw_w", "tw_s")
    return g


assets = [
    struct(S_ITEM, [param("Name", "name"), param("Slot", "name"), param("DisplayName", "string"), param("SortKey", "int64"), param("SortKey2", "int64"),
                    param("Icon", "object:" + E_TEX2D), param("ColorAdjustable", "bool"), param("Group", "name"), param("IsVanilla", "bool")]),
    struct(S_LIST, [param("Items", T_ITEM, "array")]),
    struct(S_NAMES, [param("Names", "name", "array")]),
    struct(S_SNAP, [param("Worn", "name", "array"), param("Makeup", "name", "map", value_type="struct:" + P_MDATA_S), param("Skin", "name"), param("Hair", "name"),
                    param("Colors", "name", "map", value_type=S_LINCOLOR), param("HairColor", S_LINCOLOR), param("Boobs", "float"), param("Waist", "float"), param("Hip", "float"), param("Body", "name")]),
    struct(S_LOOK, [param("Name", "string"), param("Id", "int"), param("Snap", "struct:" + S_SNAP)]),
    blueprint(SG_LOOKS, "/Script/Engine.SaveGame", variables=[var("Looks", "struct:" + S_LOOK, "array"), var("NextId", "int", default="1")]),
    struct(S_STR, [param(l, "text") for l in LANGS]),
    datatable(T_STRINGS, S_STR, rows=string_rows()),
    datatable(M + "/TKA_Mod_Table", "/Game/Project/Tables/DLC_Struct"),
    blueprint(M + "/SG_AltUI", "/Script/Engine.SaveGame",
              variables=[var("Favorites", "name", "array"), var("HiddenItems", "name", "array"), var("OnlyOwned", "bool"), var("OnlyFav", "bool"), var("LastSlot", "name"),
                         var("ScrollMult", "float", default="0"), var("TileScale", "float", default="0"),   # 0 = never set -> default
                         var("Unlimited", "bool"), var("LeftFree", "int"), var("CamFov", "float", default="0"), var("CamDist", "float", default="0"), var("BodyVariant", "name"), var("LangChoice", "int"), var("PanToSlot", "bool"), var("AllowNude", "bool"), var("OutfitNames", "string", "map", value_type="string"),
                         var("ThemeSet", "bool"), var("BgAlpha", "float", default="0"), var("TileAlpha", "float", default="0"), var("ToggleKey", "name"),
                         var("SaveVersion", "int")] + [var("Theme" + k, S_LINCOLOR) for k, _, _ in THEME]),   # SaveVersion 0 = save from before the versioning (0 = "never set" for floats)
    blueprint(MGR, E_ACTOR,
              variables=[var("Player", "object:" + P_JODI), var("PC", "object:" + P_PC), var("ControlDisabled", "bool"),
                         var("Slots", "name", "array"), var("SlotGroup", "name", "map", value_type="name"),
                         var("Catalog", "name", "map", value_type=T_LIST), var("ItemSlot", "name", "map", value_type="name"),
                         var("CatalogRows", "int"), var("Worn", "name", "array"), var("Owned", "name", "array"), var("OwnedSet", "name", "set"), var("SlotCounts", "name", "map", value_type="int"), var("SlotNames", "name", "map", value_type="struct:" + S_NAMES),
                         var("Alphabet", "string", default="0123456789abcdefghijklmnopqrstuvwxyz"),
                         var("TmpI", "int"), var("TmpKey", "int64"), var("TmpKey1", "int64"), var("TmpKey2", "int64"), var("TmpKeys", "int64", "array"), var("TmpKeys2", "int64", "array"), var("TmpStr", "string"), var("TmpItems", T_ITEM, "array"),
                         var("TmpIdx", "int"), var("TmpFound", "bool"), var("TmpName", "name"), var("TmpNames", "name", "array"), var("TmpItem", T_ITEM),
                         var("TmpGroup", "name"), var("PanelOpen", "bool"),
                         var("CurrentSlot", "name"), var("CurrentGroup", "name"), var("SearchText", "string"), var("LockStrategy", "int", default="0"),
                         var("Favorites", "name", "array"), var("HiddenItems", "name", "array"), var("TmpText", "text"), var("TmpStrings", "string", "array"), var("TmpStr2", "string"), var("Settings", "object:" + M + "/SG_AltUI"), var("ContextItem", "name"), var("LastButton", "object:" + E_WIDGET), var("CachedOnlyOwned", "bool"), var("CachedOnlyFav", "bool"),
                         var("ItemByName", "name", "map", value_type=T_ITEM), var("TmpSlotItems", T_ITEM, "array"), var("AllItems", T_ITEM, "array"), var("Outfits", "object:" + P_OUTFITS), var("Page", "name", default="Clothes"), var("ContextOutfit", "int"),
                         var("LookCat", "name", default="Skin"), var("MakeupDirty", "bool"), var("BoobsChanged", "bool"), var("ColorMode", "name", default="Clothes"),
                         var("BodyBreast", "float"), var("BodyWaist", "float"), var("TmpNames2", "name", "array"), var("TmpNames3", "name", "array"), var("TmpNames4", "name", "array"), var("TmpName2", "name"), var("TmpBool", "bool"),
                         var("TmpColor", S_LINCOLOR), var("TmpColors", "name", "map", value_type=S_LINCOLOR), var("ItemOrigin", "name", "map", value_type="text"),
                         var("LooksSave", "object:" + SG_LOOKS), var("TmpLook", "struct:" + S_LOOK), var("ContextLook", "int"), var("LookIcons", "int", "map", value_type="object:" + E_TEX2D),
                         var("PhotoRT", "object:/Script/Engine.TextureRenderTarget2D"), var("PhotoKind", "name"), var("PhotoDir", "string"), var("PhotoFile", "string"), var("ScrollMult", "float", default="4.0"), var("TileScale", "float", default="1.0"), var("OptScroll", "float"), var("OptScale", "float"),
                         var("Presets", "object:" + P_PRESET_SAVE), 
                         var("IconFrames", "int"), var("IconActor", "object:/Script/Engine.SceneCapture2D"), var("IconNumber", "int"),
                         var("Unlimited", "bool"), var("LeftFree", "int"), var("ViewShift", "float"), var("CamFov", "float", default="0.8"), var("CamDist", "float", default="1.0"), var("OptFov", "float"), var("OptDist", "float"), var("IconLight", "object:/Script/Engine.SpotLight"), var("UndoStack", "struct:" + S_SNAP, "array"), var("RedoStack", "struct:" + S_SNAP, "array"), var("TmpSnap", "struct:" + S_SNAP), var("TmpSnap2", "struct:" + S_SNAP), var("PresetIcons", "int", "map", value_type="object:" + E_TEX2D), var("TmpPreset", "struct:" + P_PRESET_S), var("ContextPreset", "int"), var("TmpIcons", "object:" + E_TEX2D, "array"),
                         # content view (View content): open index per tab (-1 = closed), the rendered snapshot + title, tile origin for "Show in tab", highlight/scroll target
                         var("ViewOutfit", "int", default="-1"), var("ViewLook", "int", default="-1"), var("ViewPreset", "int", default="-1"), var("ViewSnap", "struct:" + S_SNAP), var("ViewTitle", "string"),
                         var("ContextSlot", "name"), var("HighlightItem", "name"), var("KeepHighlight", "bool"), var("ScrollWidget", "object:" + E_WIDGET),   # TmpSection (W_ContentSection) lives in the augment: the widget class exists only after 40_widgets
                         var("TmpFColors", "name", "map", value_type=S_COLOR),
                         var("BodyMods", "name", "array"), var("BodyCaptions", "name", "map", value_type="text"), var("StandardMesh", "object:" + E_SKELMESH),
                         var("BodyMesh", "object:" + E_SKELMESH), var("CurrentBody", "name"), var("BodyVariant", "name"),
                         var("Lang", "int"), var("LangChoice", "int"), var("Strings", "name", "map", value_type="text"),
                         var("PanToSlot", "bool"), var("AllowNude", "bool"), var("FocusOn", "bool"), var("FocusZ", "float"), var("FocusZoom", "float", default="1.0"), var("TmpFloat", "float"),
                         var("ThemeVersion", "int"), var("ToggleKey", "name", default="B"), var("BgAlpha", "float", default=str(BG_ALPHA)), var("TileAlpha", "float", default=str(TILE_ALPHA)), var("ThemeKey", "name")]
                        + [var("Theme" + k, S_LINCOLOR) for k, _, _ in THEME] + [var(n, S_LINCOLOR) for n in DERIVED_NAMES],
              functions=[f_init_slot_groups(), f_order_slots(), f_sort_key(), f_display_name(), f_scan_mod_items(), f_build_catalog(),
                         f_items_for_slot(), f_slot_count(), f_item_slot(), f_is_worn(), f_is_owned(), f_worn_in_slot(),
                         f_refresh_state(), f_wear(), f_take_off(), f_debug_status(), f_find_item(), f_is_favorite(), f_filtered_items(),
                         f_groups_of_slot(), f_group_caption(), f_item_tip(), f_load_settings(), f_save_settings(), f_toggle_favorite(), f_is_item_hidden(), f_toggle_item_hidden(), f_t(), f_detect_language(), f_init_strings(),
                         f_reset_theme(), f_theme_color(), f_set_theme_color(), f_layout_fraction()] + UI_SIGNATURES),
]
write(os.path.join(os.path.dirname(__file__), "..", "30_manager.json"), assets)
