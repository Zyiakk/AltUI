"""Generates assets/30_manager.json: BP_AltUIManager (data layer, state, actions, debug)."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
from bpdsl import *
import bodyscale_groups as bg
from slots import SLOTS, SLOT_GROUP, GROUPS

MGR = M + "/BP_AltUIManager"
S_ITEM = M + "/S_ClothesItem"
S_LIST = M + "/S_ItemList"
S_NAMES = M + "/S_NameList"
S_SNAP = M + "/S_Snapshot"
S_LOOK = M + "/S_Look"; SG_LOOKS = M + "/SG_Looks"; LOOKS_SLOT = "AltUI_Looks"
SG_NAMES = M + "/SG_Names"; NAMES_SLOT = "AltUI_Names"; NAMES_VERSION = 1   # custom display names: Saved/SaveGames/AltUI_Names.sav (scripts/altui_names.py exports/imports it)
NAME_KINDS = ["mod", "group", "item", "hair", "skin", "makeup"]
SG_LOG = M + "/SG_Log"; LOG_SLOT = "AltUI_Log"; LOG_MAX = 4000   # debug log: Saved/SaveGames/AltUI_Log.sav, one FString per line
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


# ---------------- Default Name(row) / Display Name(kind, row) -> s  (pure) ----------------
def f_default_name():
    """String-table entry for the row, else the row name (the game's own display names)."""
    g = G()
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"})
    g.call("reg", K_STT, "IsRegisteredTableEntry", inp={"TableId": STRINGTABLE, "Key": "@n2s.ReturnValue"})
    g.call("src", K_STT, "GetTableEntrySourceString", inp={"TableId": STRINGTABLE, "Key": "@n2s.ReturnValue"})
    g.call("sel", K_MATH, "SelectString", inp={"A": "@src.ReturnValue", "B": "@n2s.ReturnValue", "bPickA": "@reg.ReturnValue"}); g.link("sel.ReturnValue", "return.s")
    return fn("Default Name", [param("row", "name")], [param("s", "string")], graph=g, pure=True)


def f_display_name():
    """Custom name (SG_Names) -> else Default Name (string table for items; row name for hair/skin/makeup, whose tables carry no text)."""
    g = G()
    g.call("isi", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "item"})
    g.n("dn", "call_self", function="Default Name", inp={"row": "@entry.row"}); g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"})
    g.call("dsel", K_MATH, "SelectString", inp={"A": "@dn.s", "B": "@n2s.ReturnValue", "bPickA": "@isi.ReturnValue"})
    g.n("sn", "call_self", function="Shown Name", inp={"kind": "@entry.kind", "row": "@entry.row", "default": "@dsel.ReturnValue"}); g.link("sn.name", "return.s")
    return fn("Display Name", [param("kind", "name"), param("row", "name")], [param("s", "string")], graph=g, pure=True)


# ---------------- Scan Mod Items(): ItemOriginMod[row] = mod folder of every row of every mod table (clothes, hairstyles, skins, makeup, eyes) ----------------
# The loader appends mod rows to the game's tables, so DoesDataTableRowExist says nothing about the origin. DLC_MainTable has one row per mounted mod pak (= mod folder).
MOD_TABLES = [("Mod_ClothesTable", "item"), ("Mod_HairstyleTable", "hair"), ("Mod_SkinTable", "skin"), ("Mod_MakeupTable", "makeup"), ("Mod_EyesTable", "makeup")]


def f_scan_mod_items():
    """ItemOriginMod[row] = mod folder for every row of every mod table; ModCaption[mod] = DLC caption (row name if empty); ModList = mods with a table."""
    g = G()
    g.get("go", "ItemOriginMod"); g.call("mc", K_MAP, "Map_Clear", inp={"TargetMap": "@go.ItemOriginMod"})
    g.get("gc", "ModCaption"); g.call("cc", K_MAP, "Map_Clear", inp={"TargetMap": "@gc.ModCaption"})
    g.get("gl", "ModList"); g.call("lc", K_ARR, "Array_Clear", inp={"TargetArray": "@gl.ModList"})
    g.call("rn", K_DT, "GetDataTableRowNames", inp={"Table": P_DLC_T}); g.foreach("fe", "@rn.OutRowNames")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@fe.Array Element"})
    # caption of the mod (DLC row), row name as fallback
    g.n("row", "get_row", table=P_DLC_T, inp={"RowName": "@fe.Array Element"}); g.brk("br", P_DLC_S, "@row.OutRow")
    g.call("ce", K_TXT, "TextIsEmpty", inp={"InText": "@br.Caption"}); g.call("cs", K_TXT, "Conv_TextToString", inp={"InText": "@br.Caption"})
    g.call("sel", K_MATH, "SelectString", inp={"A": "@n2s.ReturnValue", "B": "@cs.ReturnValue", "bPickA": "@ce.ReturnValue"}); g.call("ct", K_TXT, "Conv_StringToText", inp={"InString": "@sel.ReturnValue"})
    g.set("stt", "TmpText", inp={"TmpText": "@ct.ReturnValue"}); g.set("sf", "TmpFound", inp={"TmpFound": "false"})
    g.chain("fe", "row", "stt", "sf"); g.chain("row:Row Not Found", "stt"); prev = "sf"
    for i, (tbl, kind) in enumerate(MOD_TABLES):
        g.call("c1%d" % i, K_STR, "Concat_StrStr", inp={"A": "/Game/Mod/", "B": "@n2s.ReturnValue"}); g.call("c2%d" % i, K_STR, "Concat_StrStr", inp={"A": "@c1%d.ReturnValue" % i, "B": "/%s.%s" % (tbl, tbl)})
        g.call("sp%d" % i, K_SYS, "MakeSoftObjectPath", inp={"PathString": "@c2%d.ReturnValue" % i}); g.call("sr%d" % i, K_SYS, "Conv_SoftObjPathToSoftObjRef", inp={"SoftObjectPath": "@sp%d.ReturnValue" % i})
        g.call("ld%d" % i, K_SYS, "LoadAsset_Blocking", inp={"Asset": "@sr%d.ReturnValue" % i}); g.cast("ck%d" % i, E_DATATABLE, "@ld%d.ReturnValue" % i, pure=False)
        g.call("rows%d" % i, K_DT, "GetDataTableRowNames", inp={"Table": "@ck%d.AsData Table" % i}); g.foreach("fr%d" % i, "@rows%d.OutRowNames" % i)
        g.get("go%d" % i, "ItemOriginMod"); g.call("ma%d" % i, K_MAP, "Map_Add", inp={"TargetMap": "@go%d.ItemOriginMod" % i, "Key": "@fr%d.Array Element" % i, "Value": "@fe.Array Element"})
        g.set("sf%d" % i, "TmpFound", inp={"TmpFound": "true"})
        g.chain(prev, "ld%d" % i, "ck%d" % i, "sf%d" % i, "rows%d" % i, "fr%d" % i); g.chain("fr%d" % i, "ma%d" % i)
        nxt = "ld%d" % (i + 1) if i + 1 < len(MOD_TABLES) else "bf"
        g.chain("ck%d:CastFailed" % i, nxt)   # mod without this table -> next table kind
        prev = "fr%d:Completed" % i
    # mod had at least one table -> ModList + ModCaption
    g.get("gf", "TmpFound"); g.branch("bf", "@gf.TmpFound")
    g.get("gl2", "ModList"); g.call("la", K_ARR, "Array_Add", inp={"TargetArray": "@gl2.ModList", "NewItem": "@fe.Array Element"})
    g.get("gc2", "ModCaption"); g.get("gtt", "TmpText"); g.call("ca", K_MAP, "Map_Add", inp={"TargetMap": "@gc2.ModCaption", "Key": "@fe.Array Element", "Value": "@gtt.TmpText"})
    g.chain("entry", "mc", "cc", "lc", "rn", "fe"); g.chain(prev, "bf", "la", "ca")
    return fn("Scan Mod Items", graph=g)


def f_item_mod():
    g = G(); g.get("go", "ItemOriginMod"); g.call("mf", K_MAP, "Map_Find", inp={"TargetMap": "@go.ItemOriginMod", "Key": "@entry.row"})
    g.link("mf.ReturnValue", "return.found"); g.link("mf.Value", "return.mod")
    return fn("Item Mod", [param("row", "name")], [param("found", "bool"), param("mod", "name")], graph=g, pure=True)


def f_mod_caption():
    """Shown name of a mod: custom name, else the DLC caption, else the mod folder name."""
    g = G(); g.get("gc", "ModCaption"); g.call("mf", K_MAP, "Map_Find", inp={"TargetMap": "@gc.ModCaption", "Key": "@entry.mod"})
    g.call("cs", K_TXT, "Conv_TextToString", inp={"InText": "@mf.Value"}); g.call("ms", K_STR, "Conv_NameToString", inp={"InName": "@entry.mod"})
    g.call("dsel", K_MATH, "SelectString", inp={"A": "@cs.ReturnValue", "B": "@ms.ReturnValue", "bPickA": "@mf.ReturnValue"})
    g.n("sn", "call_self", function="Shown Name", inp={"kind": "mod", "row": "@entry.mod", "default": "@dsel.ReturnValue"}); g.link("sn.name", "return.s")
    return fn("Mod Caption", [param("mod", "name")], [param("s", "string")], graph=g, pure=True)


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
    g.n("dn", "call_self", function="Display Name", inp={"kind": "item", "row": "@fe.Array Element"}); g.set("sdn", "TmpStr2", inp={"TmpStr2": "@dn.s"}); g.get("gdn", "TmpStr2")
    g.n("sk", "call_self", function="Sort Key", inp={"s": "@gdn.TmpStr2"})
    g.call("sub2", K_STR, "GetSubstring", inp={"SourceString": "@gdn.TmpStr2", "StartIndex": "12", "Length": "12"})
    g.n("sk2", "call_self", function="Sort Key", inp={"s": "@sub2.ReturnValue"})
    g.get("gio", "ItemOriginMod"); g.call("inmod", K_MAP, "Map_Contains", inp={"TargetMap": "@gio.ItemOriginMod", "Key": "@fe.Array Element"}); g.call("van", K_MATH, "Not_PreBool", inp={"A": "@inmod.ReturnValue"})
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
    g.n("smg", "call_self", function="Scan Mod Groups"); g.n("bga", "call_self", function="Build Group Aliases")
    g.chain("fn:Completed", "cadd", "scadd", "app"); g.chain("fa:Completed", "madda", "scadda", "smg", "bga")
    return fn("Build Catalog", graph=g)


# ---------------- Scan Mod Groups(): ModGroupPairs = unique "<mod>|<group>" in catalog order, GroupModCount[group] = mods using it, VanillaGroups = groups with a vanilla piece ----------------
def f_scan_mod_groups():
    g = G()
    g.get("gp", "ModGroupPairs"); g.call("pc", K_ARR, "Array_Clear", inp={"TargetArray": "@gp.ModGroupPairs"})
    g.get("gm", "GroupModCount"); g.call("mc", K_MAP, "Map_Clear", inp={"TargetMap": "@gm.GroupModCount"})
    g.get("gv", "VanillaGroups"); g.call("vc", K_ARR, "Array_Clear", inp={"TargetArray": "@gv.VanillaGroups"})
    g.get("ga", "AllItems"); g.foreach("fe", "@ga.AllItems"); g.brk("b", S_ITEM, "@fe.Array Element")
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@b.Name"})
    g.call("gne", K_MATH, "NotEqual_NameName", inp={"A": "@b.Group", "B": "None"}); g.call("ok", K_MATH, "BooleanAND", inp={"A": "@imd.found", "B": "@gne.ReturnValue"}); g.branch("bok", "@ok.ReturnValue")
    # vanilla piece with a group -> VanillaGroups (unique, catalog order)
    g.call("nmd", K_MATH, "Not_PreBool", inp={"A": "@imd.found"}); g.call("vok", K_MATH, "BooleanAND", inp={"A": "@nmd.ReturnValue", "B": "@gne.ReturnValue"}); g.branch("bv", "@vok.ReturnValue")
    g.get("gv2", "VanillaGroups"); g.call("vhas", K_ARR, "Array_Contains", inp={"TargetArray": "@gv2.VanillaGroups", "ItemToFind": "@b.Group"}); g.call("vnh", K_MATH, "Not_PreBool", inp={"A": "@vhas.ReturnValue"}); g.branch("bvn", "@vnh.ReturnValue")
    g.get("gv3", "VanillaGroups"); g.call("va", K_ARR, "Array_Add", inp={"TargetArray": "@gv3.VanillaGroups", "NewItem": "@b.Group"})
    g.call("ms", K_STR, "Conv_NameToString", inp={"InName": "@imd.mod"}); g.call("gs", K_STR, "Conv_NameToString", inp={"InName": "@b.Group"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@ms.ReturnValue", "B": "|"}); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@gs.ReturnValue"})
    g.call("pn", K_STR, "Conv_StringToName", inp={"InString": "@c2.ReturnValue"})
    g.get("gp2", "ModGroupPairs"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gp2.ModGroupPairs", "ItemToFind": "@pn.ReturnValue"}); g.call("nh", K_MATH, "Not_PreBool", inp={"A": "@has.ReturnValue"}); g.branch("bn", "@nh.ReturnValue")
    g.get("gp3", "ModGroupPairs"); g.call("pa", K_ARR, "Array_Add", inp={"TargetArray": "@gp3.ModGroupPairs", "NewItem": "@pn.ReturnValue"})
    g.get("gm2", "GroupModCount"); g.call("mf", K_MAP, "Map_Find", inp={"TargetMap": "@gm2.GroupModCount", "Key": "@b.Group"})
    g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@mf.Value", "B": "1"})
    g.get("gm3", "GroupModCount"); g.call("ma", K_MAP, "Map_Add", inp={"TargetMap": "@gm3.GroupModCount", "Key": "@b.Group", "Value": "@inc.ReturnValue"})
    g.chain("entry", "pc", "mc", "vc", "fe"); g.chain("fe", "bok", "bn", "pa", "ma"); g.chain("bok:else", "bv", "bvn", "va")
    return fn("Scan Mod Groups", graph=g)


def f_build_group_aliases():
    """GroupAlias[id] = first group id with the same shown caption (custom, else default) - only with the MergeGroups option; else empty.
    Runs at the end of Build Catalog (so after every rename) and when the option toggles."""
    g = G()
    g.get("ga", "GroupAlias"); g.call("ca", K_MAP, "Map_Clear", inp={"TargetMap": "@ga.GroupAlias"})
    g.get("go", "TmpCaptionOwner"); g.call("co", K_MAP, "Map_Clear", inp={"TargetMap": "@go.TmpCaptionOwner"})
    g.get("gm", "MergeGroups"); g.branch("bm", "@gm.MergeGroups")
    g.get("gai", "AllItems"); g.foreach("fe", "@gai.AllItems"); g.brk("b", S_ITEM, "@fe.Array Element")
    g.call("gne", K_MATH, "NotEqual_NameName", inp={"A": "@b.Group", "B": "None"}); g.branch("bg", "@gne.ReturnValue")
    g.n("gc", "call_self", function="Group Caption", inp={"group": "@b.Group"}); g.call("cs", K_TXT, "Conv_TextToString", inp={"InText": "@gc.caption"})
    g.call("tr", K_STR, "Trim", inp={"SourceString": "@cs.ReturnValue"}); g.call("tr2", K_STR, "TrimTrailing", inp={"SourceString": "@tr.ReturnValue"})
    g.get("go2", "TmpCaptionOwner"); g.call("mf", K_MAP, "Map_Find", inp={"TargetMap": "@go2.TmpCaptionOwner", "Key": "@tr2.ReturnValue"}); g.branch("bf", "@mf.ReturnValue")
    g.get("ga2", "GroupAlias"); g.call("aa", K_MAP, "Map_Add", inp={"TargetMap": "@ga2.GroupAlias", "Key": "@b.Group", "Value": "@mf.Value"})
    g.get("go3", "TmpCaptionOwner"); g.call("oa", K_MAP, "Map_Add", inp={"TargetMap": "@go3.TmpCaptionOwner", "Key": "@tr2.ReturnValue", "Value": "@b.Group"})
    # ModAlias[mod] = first mod with the same shown caption (appearance chips) - only with the MergeMods option
    g.get("gma", "ModAlias"); g.call("cma", K_MAP, "Map_Clear", inp={"TargetMap": "@gma.ModAlias"}); g.get("gmo", "TmpCaptionOwner"); g.call("cmo", K_MAP, "Map_Clear", inp={"TargetMap": "@gmo.TmpCaptionOwner"})
    g.get("gmm", "MergeMods"); g.branch("bmm", "@gmm.MergeMods"); g.get("gml", "ModList"); g.foreach("fm", "@gml.ModList")
    g.n("mc", "call_self", function="Mod Caption", inp={"mod": "@fm.Array Element"}); g.call("mtr", K_STR, "Trim", inp={"SourceString": "@mc.s"}); g.call("mtr2", K_STR, "TrimTrailing", inp={"SourceString": "@mtr.ReturnValue"})
    g.get("gmo2", "TmpCaptionOwner"); g.call("mmf", K_MAP, "Map_Find", inp={"TargetMap": "@gmo2.TmpCaptionOwner", "Key": "@mtr2.ReturnValue"}); g.branch("bmf", "@mmf.ReturnValue")
    g.get("gma2", "ModAlias"); g.call("maa", K_MAP, "Map_Add", inp={"TargetMap": "@gma2.ModAlias", "Key": "@fm.Array Element", "Value": "@mmf.Value"})
    g.get("gmo3", "TmpCaptionOwner"); g.call("moa", K_MAP, "Map_Add", inp={"TargetMap": "@gmo3.TmpCaptionOwner", "Key": "@mtr2.ReturnValue", "Value": "@fm.Array Element"})
    g.chain("entry", "ca", "co", "bm", "fe"); g.chain("fe", "bg", "gc", "bf", "aa"); g.chain("bf:else", "oa"); g.chain("fe:Completed", "cma"); g.chain("bm:else", "cma")
    g.chain("cma", "cmo", "bmm", "fm"); g.chain("fm", "bmf", "maa"); g.chain("bmf:else", "moa")
    return fn("Build Group Aliases", graph=g)


def f_mod_alias():
    """Representative mod (MergeMods: first mod with the same shown caption), else the mod itself."""
    g = G(); g.get("ga", "ModAlias"); g.call("mf", K_MAP, "Map_Find", inp={"TargetMap": "@ga.ModAlias", "Key": "@entry.mod"})
    g.call("vs", K_STR, "Conv_NameToString", inp={"InName": "@mf.Value"}); g.call("gs", K_STR, "Conv_NameToString", inp={"InName": "@entry.mod"})
    g.call("sel", K_MATH, "SelectString", inp={"A": "@vs.ReturnValue", "B": "@gs.ReturnValue", "bPickA": "@mf.ReturnValue"}); g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@sel.ReturnValue"}); g.link("s2n.ReturnValue", "return.alias")
    return fn("Mod Alias", [param("mod", "name")], [param("alias", "name")], graph=g, pure=True)


def f_group_alias():
    """Representative group id (MergeGroups), else the id itself."""
    g = G(); g.get("ga", "GroupAlias"); g.call("mf", K_MAP, "Map_Find", inp={"TargetMap": "@ga.GroupAlias", "Key": "@entry.group"})
    g.call("vs", K_STR, "Conv_NameToString", inp={"InName": "@mf.Value"}); g.call("gs", K_STR, "Conv_NameToString", inp={"InName": "@entry.group"})   # no SelectName in 4.27: select as string
    g.call("sel", K_MATH, "SelectString", inp={"A": "@vs.ReturnValue", "B": "@gs.ReturnValue", "bPickA": "@mf.ReturnValue"}); g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@sel.ReturnValue"}); g.link("s2n.ReturnValue", "return.alias")
    return fn("Group Alias", [param("group", "name")], [param("alias", "name")], graph=g, pure=True)


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


# ---------------- Filtered Counts(search, onlyOwned, onlyFav, onlyVanilla) ----------------
# FilteredCounts: slot -> number of pieces that pass the filters (left list "total (filtered)"); one pass over
# Filtered Items("All"), slots without a match stay absent (Map_Find -> 0). "All" = length of the result.
def f_filtered_counts():
    g = G()
    g.get("gfc0", "FilteredCounts"); g.call("mc", K_MAP, "Map_Clear", inp={"TargetMap": "@gfc0.FilteredCounts"})
    g.get("gcg", "CurrentGroup"); g.n("it", "call_self", function="Filtered Items", inp={"slot": "All", "group": "@gcg.CurrentGroup", "search": "@entry.search", "onlyOwned": "@entry.onlyOwned", "onlyFav": "@entry.onlyFav", "onlyVanilla": "@entry.onlyVanilla"})
    g.set("sti", "TmpItems3", inp={"TmpItems3": "@it.items"}); g.get("gti", "TmpItems3")
    g.foreach("fe", "@gti.TmpItems3"); g.brk("b", S_ITEM, "@fe.Array Element")
    g.get("gis", "ItemSlot"); g.call("sf", K_MAP, "Map_Find", inp={"TargetMap": "@gis.ItemSlot", "Key": "@b.Name"})
    g.get("gfc1", "FilteredCounts"); g.call("cf", K_MAP, "Map_Find", inp={"TargetMap": "@gfc1.FilteredCounts", "Key": "@sf.Value"})
    g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@cf.Value", "B": "1"})
    g.get("gfc2", "FilteredCounts"); g.call("ma", K_MAP, "Map_Add", inp={"TargetMap": "@gfc2.FilteredCounts", "Key": "@sf.Value", "Value": "@inc.ReturnValue"})
    g.get("gti2", "TmpItems3"); g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@gti2.TmpItems3"})
    alln = g.lit_name("la", "All")
    g.get("gfc3", "FilteredCounts"); g.call("maa", K_MAP, "Map_Add", inp={"TargetMap": "@gfc3.FilteredCounts", "Key": alln, "Value": "@len.ReturnValue"})
    g.chain("entry", "mc", "it", "sti", "fe"); g.chain("fe", "ma"); g.chain("fe:Completed", "maa")
    return fn("Filtered Counts", [param("search", "string"), param("onlyOwned", "bool"), param("onlyFav", "bool"), param("onlyVanilla", "bool")], graph=g)


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


def f_shown_owned():
    """Tile state: owned, or option "not owned items = like owned" (UnownedMode 2)."""
    g = G()
    g.n("io", "call_self", function="Is Owned", inp={"name": "@entry.name"})
    g.get("gm", "UnownedMode"); g.call("m2", K_MATH, "EqualEqual_IntInt", inp={"A": "@gm.UnownedMode", "B": "2"})
    g.call("or", K_MATH, "BooleanOR", inp={"A": "@io.yes", "B": "@m2.ReturnValue"}); g.link("or.ReturnValue", "return.yes")
    return fn("Shown Owned", [param("name", "name")], [param("yes", "bool")], graph=g, pure=True)


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


# ---------------- Slot conflicts (ClothesTypeTable.IncompatibleTypes, symmetric at runtime) with per-pair exceptions ----------------
# The game takes worn pieces off by slot when Wear The Clothes runs with ignore compatible = false (both directions of the table).
# AltUI reads the table once (ConflictPairs "A|B"), lets the player free pairs (FreedConflicts, saved) and does the check itself,
# then wears with ignore compatible = true. Slot exclusivity and the underwear covering rule stay with the game.
def f_build_conflicts():
    g = G(); g.get("gcp", "ConflictPairs"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gcp.ConflictPairs"})
    g.call("rn", K_DT, "GetDataTableRowNames", inp={"Table": P_CTT}); g.foreach("fe", "@rn.OutRowNames")
    g.n("row", "get_row", table=P_CTT, inp={"RowName": "@fe.Array Element"}, miss="ignore"); g.brk("br", P_CTS, "@row.OutRow"); g.foreach("ft", "@br.IncompatibleTypes")
    g.call("as", K_STR, "Conv_NameToString", inp={"InName": "@fe.Array Element"}); g.call("bs", K_STR, "Conv_NameToString", inp={"InName": "@ft.Array Element"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@as.ReturnValue", "B": "|"}); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@bs.ReturnValue"}); g.call("kn", K_STR, "Conv_StringToName", inp={"InString": "@c2.ReturnValue"})
    g.get("gcp2", "ConflictPairs"); g.call("add", K_ARR, "Array_AddUnique", inp={"TargetArray": "@gcp2.ConflictPairs", "NewItem": "@kn.ReturnValue"})
    g.chain("entry", "clr", "rn", "fe"); g.chain("fe", "row", "ft"); g.chain("ft", "add")
    return fn("Build Conflicts", graph=g)


def pair_keys(g, id, a_pin, b_pin):
    """Name pins "a|b" and "b|a" (a pair is stored in one of the two spellings)."""
    g.call(id + "_as", K_STR, "Conv_NameToString", inp={"InName": a_pin}); g.call(id + "_bs", K_STR, "Conv_NameToString", inp={"InName": b_pin})
    g.call(id + "_a1", K_STR, "Concat_StrStr", inp={"A": "@%s_as.ReturnValue" % id, "B": "|"}); g.call(id + "_ab", K_STR, "Concat_StrStr", inp={"A": "@%s_a1.ReturnValue" % id, "B": "@%s_bs.ReturnValue" % id})
    g.call(id + "_b1", K_STR, "Concat_StrStr", inp={"A": "@%s_bs.ReturnValue" % id, "B": "|"}); g.call(id + "_ba", K_STR, "Concat_StrStr", inp={"A": "@%s_b1.ReturnValue" % id, "B": "@%s_as.ReturnValue" % id})
    g.call(id + "_kab", K_STR, "Conv_StringToName", inp={"InString": "@%s_ab.ReturnValue" % id}); g.call(id + "_kba", K_STR, "Conv_StringToName", inp={"InString": "@%s_ba.ReturnValue" % id})
    return "@%s_kab.ReturnValue" % id, "@%s_kba.ReturnValue" % id


def f_pair_in():
    g = G(); kab, kba = pair_keys(g, "k", "@entry.a", "@entry.b")
    g.call("c1", K_ARR, "Array_Contains", inp={"TargetArray": "@entry.list", "ItemToFind": kab}); g.call("c2", K_ARR, "Array_Contains", inp={"TargetArray": "@entry.list", "ItemToFind": kba})
    g.call("or", K_MATH, "BooleanOR", inp={"A": "@c1.ReturnValue", "B": "@c2.ReturnValue"}); g.link("or.ReturnValue", "return.yes")
    return fn("Pair In", [param("list", "name", "array"), param("a", "name"), param("b", "name")], [param("yes", "bool")], graph=g, pure=True)


def f_conflicts_with():
    g = G(); g.get("gcp", "ConflictPairs"); g.n("pi", "call_self", function="Pair In", inp={"list": "@gcp.ConflictPairs", "a": "@entry.a", "b": "@entry.b"}); g.link("pi.yes", "return.yes")
    return fn("Conflicts With", [param("a", "name"), param("b", "name")], [param("yes", "bool")], graph=g, pure=True)


def f_is_freed():
    g = G(); g.get("gfc", "FreedConflicts"); g.n("pi", "call_self", function="Pair In", inp={"list": "@gfc.FreedConflicts", "a": "@entry.a", "b": "@entry.b"}); g.link("pi.yes", "return.yes")
    return fn("Is Freed", [param("a", "name"), param("b", "name")], [param("yes", "bool")], graph=g, pure=True)


def f_set_freed():
    """freed = the pair may be worn together (both spellings removed, "a|b" added when freed); saved."""
    g = G(); kab, kba = pair_keys(g, "k", "@entry.a", "@entry.b")
    g.get("gf1", "FreedConflicts"); g.call("r1", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gf1.FreedConflicts", "Item": kab})
    g.get("gf2", "FreedConflicts"); g.call("r2", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gf2.FreedConflicts", "Item": kba}); g.branch("b", "@entry.freed")
    g.get("gf3", "FreedConflicts"); g.call("ad", K_ARR, "Array_Add", inp={"TargetArray": "@gf3.FreedConflicts", "NewItem": kab}); g.n("sv", "call_self", function="Save Settings")
    g.chain("entry", "r1", "r2", "b", "ad", "sv"); g.chain("b:else", "sv")
    return fn("Set Freed", [param("a", "name"), param("b", "name"), param("freed", "bool")], graph=g)


def f_conflicting_slots():
    """Slots of the worn pieces that the game would take off for a piece of `slot` and that are not freed (TmpConflicts, unique)."""
    g = G(); g.get("gt0", "TmpConflicts"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gt0.TmpConflicts"}); g.foreach("fe", "@entry.worn")
    g.n("isl", "call_self", function="Item Slot", inp={"name": "@fe.Array Element"})
    g.call("ne", K_MATH, "NotEqual_NameName", inp={"A": "@isl.slot", "B": "@entry.slot"})
    g.n("cw", "call_self", function="Conflicts With", inp={"a": "@entry.slot", "b": "@isl.slot"}); g.n("fr", "call_self", function="Is Freed", inp={"a": "@entry.slot", "b": "@isl.slot"}); g.call("nfr", K_MATH, "Not_PreBool", inp={"A": "@fr.yes"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@ne.ReturnValue", "B": "@cw.yes"}); g.call("a2", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@nfr.ReturnValue"}); g.branch("b", "@a2.ReturnValue")
    g.get("gt1", "TmpConflicts"); g.call("add", K_ARR, "Array_AddUnique", inp={"TargetArray": "@gt1.TmpConflicts", "NewItem": "@isl.slot"})
    g.get("gt2", "TmpConflicts"); g.link("gt2.TmpConflicts", "return.slots")
    g.chain("entry", "clr", "fe"); g.chain("fe", "b", "add"); g.chain("fe:Completed", "return")
    return fn("Conflicting Slots", [param("slot", "name"), param("worn", "name", "array")], [param("slots", "name", "array")], graph=g)


def f_conflicting_worn_slots():
    g = G(); g.get("gp", "Player"); g.call("w", P_CPB, "Get Wearing Clothes Names", inp={"self": "@gp.Player"})
    g.n("cs", "call_self", function="Conflicting Slots", inp={"slot": "@entry.slot", "worn": "@w.clothes list"}); g.link("cs.slots", "return.slots"); g.chain("entry", "w", "cs", "return")
    return fn("Conflicting Worn Slots", [param("slot", "name")], [param("slots", "name", "array")], graph=g)


def take_off_conflicts(g, id, slot_pin, prev):
    """Exec chain: take off (by slot, no covering check) every worn slot that conflicts with slot_pin; returns the exec id to continue from."""
    g.n(id + "_cs", "call_self", function="Conflicting Worn Slots", inp={"slot": slot_pin}); g.foreach(id + "_fo", "@%s_cs.slots" % id)
    g.get(id + "_gp", "Player"); g.call(id + "_to", P_CPB, "take off clothes", inp={"self": "@%s_gp.Player" % id, "type": "@%s_fo.Array Element" % id, "update mask": "false"})
    g.chain(prev, id + "_cs", id + "_fo"); g.chain(id + "_fo", id + "_to"); return id + "_fo:Completed"


def f_save_worn():
    """Persist the worn pieces like Jodi.Save Appearance, but without its ownership check: the game's version skips the whole save while
    any worn piece is not in the wardrobe, so with "not owned items" = greyed / like owned nothing would survive a level load."""
    g = G(); g.call("cr", K_GS, "CreateSaveGameObject", inp={"SaveGameClass": P_PSAVE}); g.cast("cs", P_PSAVE, "@cr.ReturnValue")
    g.get("gpl", "Player"); g.call("col", P_PSAVE, "Collect Player Data", inp={"self": "@cs.AsPlayer Save", "player": "@gpl.Player"})
    g.call("sv", K_GS, "SaveGameToSlot", inp={"SaveGameObject": "@cs.AsPlayer Save", "SlotName": "TKAPlayer", "UserIndex": "0"})   # Functions.Get Player Save Slot Name = "TKAPlayer"
    g.chain("entry", "cr", "col", "sv"); return fn("Save Worn", graph=g)


def f_wear():
    """Wear a piece. Catalog piece: AltUI's own conflict check (Conflicting Worn Slots, freed pairs stay on) + Wear The Clothes with
    ignore compatible = true; unknown piece: the game's own check (ignore compatible = false)."""
    g = G(); g.n("isl", "call_self", function="Item Slot", inp={"name": "@entry.name"}); g.call("known", K_MATH, "NotEqual_NameName", inp={"A": "@isl.slot", "B": "None"}); g.branch("bk", "@known.ReturnValue")
    done = take_off_conflicts(g, "tc", "@isl.slot", "bk")
    g.get("gp3", "Player"); g.call("w2", P_CPB, "Wear The Clothes", inp={"self": "@gp3.Player", "name": "@entry.name", "check covering": "true", "update mask": "true", "ignore compatible": "true"}); g.branch("b2", "@w2.successed")
    g.get("gp", "Player"); g.call("w", P_CPB, "Wear The Clothes", inp={"self": "@gp.Player", "name": "@entry.name", "check covering": "true", "update mask": "true", "ignore compatible": "false"})
    g.branch("b", "@w.successed")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"})
    g.n("mk", "call_self", function="T", inp={"key": "Msg_WearFailed"}); g.call("mks", K_TXT, "Conv_TextToString", inp={"InText": "@mk.text"})
    g.call("msg", K_STR, "Concat_StrStr", inp={"A": "@mks.ReturnValue", "B": "@n2s.ReturnValue"})
    pop(g, "pop", text_from_str(g, "t", "@msg.ReturnValue"))
    g.n("sa", "call_self", function="Save Worn")
    g.n("rs", "call_self", function="Refresh State")
    g.chain("entry", "bk"); g.chain(done, "w2", "b2", "sa", "rs"); g.chain("b2:else", "pop"); g.chain("bk:else", "w", "b", "sa"); g.chain("b:else", "pop", "sa")
    return fn("Wear", [param("name", "name")], graph=g)


def f_take_off():
    g = G()
    g.get("gp", "Player"); g.call("t", P_CPB, "Take off this clothes", inp={"self": "@gp.Player", "clothes name": "@entry.name"})
    g.n("sa", "call_self", function="Save Worn")
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


# ---------------- Filtered Items(slot, group, search, onlyOwned, onlyFav, onlyVanilla) -> items ----------------
# group: None = all groups; "Basis" = pieces without a group (Group == None); onlyVanilla drops pieces from mod tables (IsVanilla)
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
    g.n("alI", "call_self", function="Group Alias", inp={"group": "@b.Group"}); g.n("alG", "call_self", function="Group Alias", inp={"group": "@entry.group"})   # MergeGroups
    g.call("gEq", K_MATH, "EqualEqual_NameName", inp={"A": "@alI.alias", "B": "@alG.alias"})
    g.call("gB", K_MATH, "BooleanAND", inp={"A": "@gBasis.ReturnValue", "B": "@iNone.ReturnValue"})
    g.call("gOk1", K_MATH, "BooleanOR", inp={"A": "@gAll.ReturnValue", "B": "@gB.ReturnValue"})
    g.call("gOk", K_MATH, "BooleanOR", inp={"A": "@gOk1.ReturnValue", "B": "@gEq.ReturnValue"})
    g.call("gOkH", K_MATH, "BooleanOR", inp={"A": "@gOk.ReturnValue", "B": "@gHid.ReturnValue"})
    # search
    # search: shown name (custom or default), row name, default name, mod caption (shown + default), custom group name + group name
    g.get("gts", "TmpStr"); g.call("sEmpty", K_STR, "IsEmpty", inp={"InString": "@gts.TmpStr"})
    g.call("rn", K_STR, "Conv_NameToString", inp={"InName": "@b.Name"}); g.n("dfn", "call_self", function="Default Name", inp={"row": "@b.Name"})
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@b.Name"}); g.n("mcp", "call_self", function="Mod Caption", inp={"mod": "@imd.mod"})
    g.get("gmc", "ModCaption"); g.call("mdf", K_MAP, "Map_Find", inp={"TargetMap": "@gmc.ModCaption", "Key": "@imd.mod"}); g.call("mds", K_TXT, "Conv_TextToString", inp={"InText": "@mdf.Value"})
    g.n("gcn", "call_self", function="Custom Name", inp={"kind": "group", "row": "@b.Group"})   # Group Caption has exec pins (table row) - custom group name + group id suffice here
    g.call("gn", K_STR, "Conv_NameToString", inp={"InName": "@b.Group"})
    hits = []
    for i, src in enumerate(["@b.DisplayName", "@rn.ReturnValue", "@dfn.s", "@mcp.s", "@mds.ReturnValue", "@gcn.name", "@gn.ReturnValue"]):
        g.call("lo%d" % i, K_STR, "ToLower", inp={"SourceString": src}); g.get("gts%d" % i, "TmpStr")
        g.call("hit%d" % i, K_STR, "Contains", inp={"SearchIn": "@lo%d.ReturnValue" % i, "Substring": "@gts%d.TmpStr" % i, "bUseCase": "false", "bSearchFromEnd": "false"}); hits.append("@hit%d.ReturnValue" % i)
    prev = hits[0]
    for i, h in enumerate(hits[1:]):
        g.call("or%d" % i, K_MATH, "BooleanOR", inp={"A": prev, "B": h}); prev = "@or%d.ReturnValue" % i
    g.call("sOk", K_MATH, "BooleanOR", inp={"A": "@sEmpty.ReturnValue", "B": prev})
    # owned / favourite
    g.n("io", "call_self", function="Is Owned", inp={"name": "@b.Name"}); g.n("ifv", "call_self", function="Is Favorite", inp={"name": "@b.Name"})
    g.call("nO", K_MATH, "Not_PreBool", inp={"A": "@entry.onlyOwned"}); g.call("oOk", K_MATH, "BooleanOR", inp={"A": "@nO.ReturnValue", "B": "@io.yes"})
    g.call("nF", K_MATH, "Not_PreBool", inp={"A": "@entry.onlyFav"}); g.call("fOk", K_MATH, "BooleanOR", inp={"A": "@nF.ReturnValue", "B": "@ifv.yes"})
    g.call("nV", K_MATH, "Not_PreBool", inp={"A": "@entry.onlyVanilla"}); g.call("vOk", K_MATH, "BooleanOR", inp={"A": "@nV.ReturnValue", "B": "@b.IsVanilla"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@gOkH.ReturnValue", "B": "@sOk.ReturnValue"})
    g.call("a2", K_MATH, "BooleanAND", inp={"A": "@oOk.ReturnValue", "B": "@fOk.ReturnValue"})
    g.call("a3a", K_MATH, "BooleanAND", inp={"A": "@a2.ReturnValue", "B": "@hEq.ReturnValue"})
    g.call("a3", K_MATH, "BooleanAND", inp={"A": "@a3a.ReturnValue", "B": "@vOk.ReturnValue"})
    g.call("all", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@a3.ReturnValue"})
    g.branch("br", "@all.ReturnValue")
    g.get("gt1", "TmpItems"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gt1.TmpItems", "NewItem": "@fe.Array Element"})
    g.get("gt2", "TmpItems"); g.link("gt2.TmpItems", "return.items")
    g.chain("entry", "sti", "clr", "ss", "fe"); g.chain("fe", "br", "add"); g.chain("fe:Completed", "return")
    return fn("Filtered Items", [param("slot", "name"), param("group", "name"), param("search", "string"), param("onlyOwned", "bool"), param("onlyFav", "bool"), param("onlyVanilla", "bool")],
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
    g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@sel.ReturnValue"}); g.n("al", "call_self", function="Group Alias", inp={"group": "@s2n.ReturnValue"})   # MergeGroups: one chip per shown name
    g.get("gn1", "TmpNames"); g.call("add", K_ARR, "Array_AddUnique", inp={"TargetArray": "@gn1.TmpNames", "NewItem": "@al.alias"})
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
def f_group_caption_default():
    g = G()
    g.call("isB", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.group", "B": "Basis"}); g.branch("bb", "@isB.ReturnValue")
    g.n("tb", "call_self", function="T", inp={"key": "Group_Basis"}); g.set("s1", "TmpText", inp={"TmpText": "@tb.text"})
    g.call("isH", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.group", "B": "Hidden"}); g.branch("bh", "@isH.ReturnValue")
    g.n("th", "call_self", function="T", inp={"key": "Group_Hidden"}); g.set("s4", "TmpText", inp={"TmpText": "@th.text"})
    g.call("isM", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.group", "B": "AltUI_More"}); g.branch("bm", "@isM.ReturnValue")
    g.n("tm", "call_self", function="T", inp={"key": "Chip_More"}); g.set("s5", "TmpText", inp={"TmpText": "@tm.text"})
    g.n("row", "get_row", table=P_CG, inp={"RowName": "@entry.group"})
    g.brk("br", P_CGS, "@row.OutRow"); g.set("s2", "TmpText", inp={"TmpText": "@br.GroupName"})
    g.call("tn", K_TXT, "Conv_NameToText", inp={"InName": "@entry.group"}); g.set("s3", "TmpText", inp={"TmpText": "@tn.ReturnValue"})
    g.get("gt", "TmpText"); g.link("gt.TmpText", "return.caption")
    g.chain("entry", "bb", "s1", "return"); g.chain("bb:else", "bh", "s4", "return"); g.chain("bh:else", "bm", "s5", "return"); g.chain("bm:else", "row", "s2", "return"); g.chain("row:Row Not Found", "s3", "return")
    return fn("Group Caption Default", [param("group", "name")], [param("caption", "text")], graph=g)


def f_group_caption():
    """Shown caption of a group: the custom name (Manage tab), else Group Caption Default."""
    g = G()
    g.n("cn", "call_self", function="Custom Name", inp={"kind": "group", "row": "@entry.group"}); g.branch("bcn", "@cn.found")
    g.call("cnt", K_TXT, "Conv_StringToText", inp={"InString": "@cn.name"}); g.set("s0", "TmpText", inp={"TmpText": "@cnt.ReturnValue"})
    g.n("gd", "call_self", function="Group Caption Default", inp={"group": "@entry.group"}); g.set("s1", "TmpText", inp={"TmpText": "@gd.caption"})
    g.get("gt", "TmpText"); g.link("gt.TmpText", "return.caption")
    g.chain("entry", "bcn", "s0", "return"); g.chain("bcn:else", "gd", "s1", "return")
    return fn("Group Caption", [param("group", "name")], [param("caption", "text")], graph=g)


# ---------------- Chip Caption(group) -> caption: Group Caption shortened to GroupLen characters (0 = unlimited) ----------------
# Cut in the middle: head (the longer half) + ".." + tail, the dots do not count - groups that share a prefix stay apart.
# full: never cut (the selected chip while the row is collapsed - it is the only group chip, so there is room).
def f_cut_caption():
    g = G()
    g.call("len", K_STR, "Len", inp={"S": "@entry.text"})
    g.get("gl", "GroupLen"); g.call("lim", K_MATH, "Greater_IntInt", inp={"A": "@gl.GroupLen", "B": "0"})
    g.get("gl2", "GroupLen"); g.call("over", K_MATH, "Greater_IntInt", inp={"A": "@len.ReturnValue", "B": "@gl2.GroupLen"})
    g.call("cut0", K_MATH, "BooleanAND", inp={"A": "@lim.ReturnValue", "B": "@over.ReturnValue"})
    g.call("nfull", K_MATH, "Not_PreBool", inp={"A": "@entry.full"}); g.call("cut", K_MATH, "BooleanAND", inp={"A": "@cut0.ReturnValue", "B": "@nfull.ReturnValue"})
    g.get("gl3", "GroupLen"); g.call("h1", K_MATH, "Add_IntInt", inp={"A": "@gl3.GroupLen", "B": "1"}); g.call("head", K_MATH, "Divide_IntInt", inp={"A": "@h1.ReturnValue", "B": "2"})
    g.get("gl4", "GroupLen"); g.call("tailn", K_MATH, "Subtract_IntInt", inp={"A": "@gl4.GroupLen", "B": "@head.ReturnValue"})
    g.call("left", K_STR, "Left", inp={"SourceString": "@entry.text", "Count": "@head.ReturnValue"}); g.call("right", K_STR, "Right", inp={"SourceString": "@entry.text", "Count": "@tailn.ReturnValue"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@left.ReturnValue", "B": ".."}); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@right.ReturnValue"})
    g.call("sel", K_MATH, "SelectString", inp={"A": "@c2.ReturnValue", "B": "@entry.text", "bPickA": "@cut.ReturnValue"})
    g.call("s2t", K_TXT, "Conv_StringToText", inp={"InString": "@sel.ReturnValue"}); g.link("s2t.ReturnValue", "return.caption")
    return fn("Cut Caption", [param("text", "string"), param("full", "bool")], [param("caption", "text")], graph=g, pure=True)


def f_chip_caption():
    g = G()
    g.n("gc", "call_self", function="Group Caption", inp={"group": "@entry.group"})
    g.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@gc.caption"}); g.n("cut", "call_self", function="Cut Caption", inp={"text": "@t2s.ReturnValue", "full": "@entry.full"})
    g.set("st", "TmpText", inp={"TmpText": "@cut.caption"}); g.get("gt", "TmpText"); g.link("gt.TmpText", "return.caption")
    g.chain("entry", "gc", "st", "return")
    return fn("Chip Caption", [param("group", "name"), param("full", "bool")], [param("caption", "text")], graph=g)


# ---------------- Item Tip(item, kind, category) -> tip ----------------
def f_item_tip():
    """Lines: shown name · [Standard: default, when a custom name is set] · "s: " slot label (item) / category text (hair, skin, makeup, body)
    · "Vanilla" or "PAK: " mod caption [+ "pak: " pak name] · [item with group: "G: " group caption [+ "g: " id]] (id lines unless TipNoIds)
    · "id: " row. Options: TipNoPrefix drops every prefix (s:, PAK:, pak:, G:, g:, id:), TipNoIds drops the pak: / g: / id: lines."""
    g = G(); g.brk("b", S_ITEM, "@entry.item")
    g.call("rn", K_STR, "Conv_NameToString", inp={"InName": "@b.Name"})
    g.call("isi", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "item"})
    g.get("gnp", "TipNoPrefix"); g.get("gni", "TipNoIds"); g.call("nni", K_MATH, "Not_PreBool", inp={"A": "@gni.TipNoIds"})

    def pfx(id, key, colon=False):   # prefix string, empty with TipNoPrefix
        g.n(id + "t", "call_self", function="T", inp={"key": key}); g.call(id + "s", K_TXT, "Conv_TextToString", inp={"InText": "@%st.text" % id}); src = "@%ss.ReturnValue" % id
        if colon:
            g.call(id + "c", K_STR, "Concat_StrStr", inp={"A": src, "B": ": "}); src = "@%sc.ReturnValue" % id
        g.call(id, K_MATH, "SelectString", inp={"A": "", "B": src, "bPickA": "@gnp.TipNoPrefix"}); return "@%s.ReturnValue" % id
    ps = pfx("ps", "Tip_Slot"); pP = pfx("pkm", "Lbl_KindMod", True); pp = pfx("pp", "Tip_Pak"); pG = pfx("pkg", "Lbl_KindGroup", True); pg = pfx("pg", "Tip_Grp"); pi = pfx("pi", "Tip_Id")
    # "Standard: <default>" only when a custom name is in effect; default = Default Name (item) or the row name
    g.n("dn", "call_self", function="Default Name", inp={"row": "@b.Name"}); g.call("dfs", K_MATH, "SelectString", inp={"A": "@dn.s", "B": "@rn.ReturnValue", "bPickA": "@isi.ReturnValue"})
    g.n("cn", "call_self", function="Custom Name", inp={"kind": "@entry.kind", "row": "@b.Name"})
    g.n("td", "call_self", function="T", inp={"key": "Tip_Default"}); g.call("sd", K_TXT, "Conv_TextToString", inp={"InText": "@td.text"})
    g.call("d1", K_STR, "Concat_StrStr", inp={"A": "\n", "B": "@sd.ReturnValue"}); g.call("d2", K_STR, "Concat_StrStr", inp={"A": "@d1.ReturnValue", "B": "@dfs.ReturnValue"})
    g.call("dsel", K_MATH, "SelectString", inp={"A": "@d2.ReturnValue", "B": "", "bPickA": "@cn.found"})
    # "s: " slot label (item) or the category text
    g.n("isl", "call_self", function="Item Slot", inp={"name": "@b.Name"})
    g.call("sn", K_STR, "Conv_NameToString", inp={"InName": "@isl.slot"}); g.call("sk", K_STR, "Concat_StrStr", inp={"A": "Slot_", "B": "@sn.ReturnValue"})
    g.call("skn", K_STR, "Conv_StringToName", inp={"InString": "@sk.ReturnValue"}); g.n("ts", "call_self", function="T", inp={"key": "@skn.ReturnValue"})
    g.call("ss", K_TXT, "Conv_TextToString", inp={"InText": "@ts.text"}); g.call("cs", K_TXT, "Conv_TextToString", inp={"InText": "@entry.category"})
    g.call("s3", K_MATH, "SelectString", inp={"A": "@ss.ReturnValue", "B": "@cs.ReturnValue", "bPickA": "@isi.ReturnValue"}); g.call("l3", K_STR, "Concat_StrStr", inp={"A": ps, "B": "@s3.ReturnValue"})
    # origin: "Vanilla" or "PAK: <caption>" [+ "\npak: <pak>" when ids are shown]
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@b.Name"}); g.n("mcp", "call_self", function="Mod Caption", inp={"mod": "@imd.mod"})
    g.call("ms", K_STR, "Conv_NameToString", inp={"InName": "@imd.mod"}); g.call("o1", K_STR, "Concat_StrStr", inp={"A": pP, "B": "@mcp.s"})
    g.call("showp", K_MATH, "BooleanAND", inp={"A": "true", "B": "@nni.ReturnValue"})   # pak line always (unless TipNoIds); "only when it differs" dropped 2026-09-21
    g.call("o2", K_STR, "Concat_StrStr", inp={"A": "\n", "B": pp}); g.call("o3", K_STR, "Concat_StrStr", inp={"A": "@o2.ReturnValue", "B": "@ms.ReturnValue"})
    g.call("o4", K_MATH, "SelectString", inp={"A": "@o3.ReturnValue", "B": "", "bPickA": "@showp.ReturnValue"}); g.call("o5", K_STR, "Concat_StrStr", inp={"A": "@o1.ReturnValue", "B": "@o4.ReturnValue"})
    g.n("tv", "call_self", function="T", inp={"key": "Tip_Vanilla"}); g.call("sv", K_TXT, "Conv_TextToString", inp={"InText": "@tv.text"})
    g.call("org", K_MATH, "SelectString", inp={"A": "@o5.ReturnValue", "B": "@sv.ReturnValue", "bPickA": "@imd.found"})
    # group (item only): "\nG: <caption>" [+ "\ng: <id>" when ids are shown] -> TmpStr
    g.call("gn", K_MATH, "EqualEqual_NameName", inp={"A": "@b.Group", "B": "None"}); g.call("ngn", K_MATH, "Not_PreBool", inp={"A": "@gn.ReturnValue"})
    g.call("hasg", K_MATH, "BooleanAND", inp={"A": "@ngn.ReturnValue", "B": "@isi.ReturnValue"}); g.branch("bg", "@hasg.ReturnValue")
    g.n("gc", "call_self", function="Group Caption", inp={"group": "@b.Group"}); g.call("gcs", K_TXT, "Conv_TextToString", inp={"InText": "@gc.caption"})
    g.call("gs", K_STR, "Conv_NameToString", inp={"InName": "@b.Group"})
    g.call("g1", K_STR, "Concat_StrStr", inp={"A": "\n", "B": pG}); g.call("g2", K_STR, "Concat_StrStr", inp={"A": "@g1.ReturnValue", "B": "@gcs.ReturnValue"})
    g.call("showg", K_MATH, "BooleanAND", inp={"A": "true", "B": "@nni.ReturnValue"})   # g line always (unless TipNoIds)
    g.call("g3", K_STR, "Concat_StrStr", inp={"A": "\n", "B": pg}); g.call("g4", K_STR, "Concat_StrStr", inp={"A": "@g3.ReturnValue", "B": "@gs.ReturnValue"})
    g.call("g5", K_MATH, "SelectString", inp={"A": "@g4.ReturnValue", "B": "", "bPickA": "@showg.ReturnValue"}); g.call("g6", K_STR, "Concat_StrStr", inp={"A": "@g2.ReturnValue", "B": "@g5.ReturnValue"})
    g.set("sg1", "TmpStr", inp={"TmpStr": "@g6.ReturnValue"}); g.set("sg0", "TmpStr", inp={"TmpStr": ""})
    # "\nid: <row>" unless TipNoIds
    g.call("i1", K_STR, "Concat_StrStr", inp={"A": "\n", "B": pi}); g.call("i2", K_STR, "Concat_StrStr", inp={"A": "@i1.ReturnValue", "B": "@rn.ReturnValue"})
    g.call("i3", K_MATH, "SelectString", inp={"A": "@i2.ReturnValue", "B": "", "bPickA": "@nni.ReturnValue"})
    # assemble: name [\n Standard: default] \n s: slot \n origin [\n G: group] [\n id: row]
    g.get("go", "TmpStr")
    g.call("l1", K_STR, "Concat_StrStr", inp={"A": "@b.DisplayName", "B": "@dsel.ReturnValue"}); g.call("l2", K_STR, "Concat_StrStr", inp={"A": "@l1.ReturnValue", "B": "\n"})
    g.call("l4", K_STR, "Concat_StrStr", inp={"A": "@l2.ReturnValue", "B": "@l3.ReturnValue"}); g.call("l5", K_STR, "Concat_StrStr", inp={"A": "@l4.ReturnValue", "B": "\n"})
    g.call("l6", K_STR, "Concat_StrStr", inp={"A": "@l5.ReturnValue", "B": "@org.ReturnValue"}); g.call("l7", K_STR, "Concat_StrStr", inp={"A": "@l6.ReturnValue", "B": "@go.TmpStr"})
    g.call("l8", K_STR, "Concat_StrStr", inp={"A": "@l7.ReturnValue", "B": "@i3.ReturnValue"})
    g.call("tt", K_TXT, "Conv_StringToText", inp={"InString": "@l8.ReturnValue"}); g.link("tt.ReturnValue", "return.tip")
    g.chain("entry", "bg", "gc", "sg1", "return"); g.chain("bg:else", "sg0", "return")
    return fn("Item Tip", [param("item", T_ITEM), param("kind", "name"), param("category", "text")], [param("tip", "text")], graph=g)


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
            ("CachedOnlyOwned", "OnlyOwned", "copy", None), ("CachedOnlyFav", "OnlyFav", "copy", None), ("CachedOnlyVanilla", "OnlyVanilla", "copy", None),
            ("ScrollMult", "ScrollMult", "float0", 4.0), ("TileScale", "TileScale", "float0", 1.0),
            ("Unlimited", "Unlimited", "copy", None), ("LeftFree", "LeftFree", "copy", None), ("SubTabsCollapsed", "SubTabsCollapsed", "copy", None), ("LookOnlyFav", "LookOnlyFav", "copy", None), ("LookChipsCollapsed", "LookChipsCollapsed", "copy", None), ("GroupLen", "GroupLen", "copy", None), ("ChipH", "ChipH", "copy", None),
            ("CamFov", "CamFov", "float0", 0.8), ("CamDist", "CamDist", "float0", 1.0),
            ("BodyVariant", "BodyVariant", "copy", None), ("BodyScales", "BodyScales", "copy", None), ("LangChoice", "LangChoice", "copy", None),
            ("PanToSlot", "PanToSlot", "copy", None), ("AllowNude", "AllowNude", "copy", None), ("OnlyModsNames", "OnlyModsNames", "copy", None), ("CaseSensitiveNames", "CaseSensitiveNames", "copy", None), ("MergeGroups", "MergeGroups", "copy", None), ("MergeMods", "MergeMods", "copy", None), ("TipNoPrefix", "TipNoPrefix", "copy", None), ("TipNoIds", "TipNoIds", "copy", None), ("FreedConflicts", "FreedConflicts", "copy", None), ("HairSwatchesOpen", "HairSwatchesOpen", "copy", None),
            ("UnownedMode", "UnownedMode", "copy", None), ("ToggleKey", "ToggleKey", "name", None)]
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


# ---------------- custom display names: SG_Names (AltUI_Names.sav), key "<kind>:<row>" ----------------
def f_name_key():
    g = G()
    g.call("ks", K_STR, "Conv_NameToString", inp={"InName": "@entry.kind"}); g.call("rs", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@ks.ReturnValue", "B": ":"}); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@rs.ReturnValue"})
    g.call("kn", K_STR, "Conv_StringToName", inp={"InString": "@c2.ReturnValue"}); g.link("kn.ReturnValue", "return.key")
    return fn("Name Key", [param("kind", "name"), param("row", "name")], [param("key", "name")], graph=g, pure=True)


def f_custom_name():
    """found/name from Names.Names[<kind>:<row>]; Names invalid -> not found."""
    g = G()
    g.get("gn", "Names"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gn.Names"})
    g.get("gm", "Names", cls=SG_NAMES); g.get("gn2", "Names"); g.link("gn2.Names", "gm.self")
    g.n("k", "call_self", function="Name Key", inp={"kind": "@entry.kind", "row": "@entry.row"})
    g.call("mf", K_MAP, "Map_Find", inp={"TargetMap": "@gm.Names", "Key": "@k.key"})
    g.call("ne", K_STR, "IsEmpty", inp={"InString": "@mf.Value"}); g.call("nn", K_MATH, "Not_PreBool", inp={"A": "@ne.ReturnValue"})
    g.call("f1", K_MATH, "BooleanAND", inp={"A": "@iv.ReturnValue", "B": "@mf.ReturnValue"}); g.call("f2", K_MATH, "BooleanAND", inp={"A": "@f1.ReturnValue", "B": "@nn.ReturnValue"})
    g.call("sel", K_MATH, "SelectString", inp={"A": "@mf.Value", "B": "", "bPickA": "@f2.ReturnValue"})
    g.link("f2.ReturnValue", "return.found"); g.link("sel.ReturnValue", "return.name")
    return fn("Custom Name", [param("kind", "name"), param("row", "name")], [param("found", "bool"), param("name", "string")], graph=g, pure=True)


def f_shown_name():
    g = G()
    g.n("cn", "call_self", function="Custom Name", inp={"kind": "@entry.kind", "row": "@entry.row"})
    g.call("sel", K_MATH, "SelectString", inp={"A": "@cn.name", "B": "@entry.default", "bPickA": "@cn.found"}); g.link("sel.ReturnValue", "return.name")
    return fn("Shown Name", [param("kind", "name"), param("row", "name"), param("default", "string")], [param("name", "string")], graph=g, pure=True)


def f_set_custom_name():
    """Trimmed name -> Names map (empty = remove), save, mark the catalog dirty."""
    g = G()
    g.call("tr", K_STR, "Trim", inp={"SourceString": "@entry.name"}); g.call("tr2", K_STR, "TrimTrailing", inp={"SourceString": "@tr.ReturnValue"})
    g.get("gn", "Names"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gn.Names"}); g.branch("bv", "@iv.ReturnValue")
    g.call("cr", K_GS, "CreateSaveGameObject", inp={"SaveGameClass": SG_NAMES}); g.cast("cc", SG_NAMES, "@cr.ReturnValue"); g.set("sn", "Names", inp={"Names": "@cc.AsSG_Names"})
    g.n("k", "call_self", function="Name Key", inp={"kind": "@entry.kind", "row": "@entry.row"})
    g.get("gm", "Names", cls=SG_NAMES); g.get("gn2", "Names"); g.link("gn2.Names", "gm.self")
    g.call("em", K_STR, "IsEmpty", inp={"InString": "@tr2.ReturnValue"}); g.branch("be", "@em.ReturnValue")
    g.call("rm", K_MAP, "Map_Remove", inp={"TargetMap": "@gm.Names", "Key": "@k.key"})
    g.call("ad", K_MAP, "Map_Add", inp={"TargetMap": "@gm.Names", "Key": "@k.key", "Value": "@tr2.ReturnValue"})
    g.set("sd", "CatalogDirty", inp={"CatalogDirty": "true"}); g.n("sv", "call_self", function="Save Names")
    g.chain("entry", "bv", "be", "rm", "sd", "sv"); g.chain("bv:else", "cr", "sn", "be"); g.chain("be:else", "ad", "sd")
    return fn("Set Custom Name", [param("kind", "name"), param("row", "name"), param("name", "string")], graph=g)


def f_load_names():
    g = G()
    g.call("ex", K_GS, "DoesSaveGameExist", inp={"SlotName": NAMES_SLOT, "UserIndex": "0"}); g.branch("b", "@ex.ReturnValue")
    g.call("ld", K_GS, "LoadGameFromSlot", inp={"SlotName": NAMES_SLOT, "UserIndex": "0"}); g.cast("cl", SG_NAMES, "@ld.ReturnValue"); g.set("s1", "Names", inp={"Names": "@cl.AsSG_Names"})
    g.get("gs", "Names"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gs.Names"}); g.branch("bv", "@iv.ReturnValue")
    g.call("cr", K_GS, "CreateSaveGameObject", inp={"SaveGameClass": SG_NAMES}); g.cast("cc", SG_NAMES, "@cr.ReturnValue"); g.set("s2", "Names", inp={"Names": "@cc.AsSG_Names"})
    g.chain("entry", "ex", "b", "ld", "s1", "bv"); g.chain("b:else", "cr", "s2"); g.chain("bv:else", "cr")
    return fn("Load Names", graph=g)


def f_save_names():
    g = G()
    g.get("gn", "Names"); g.get("gv", "Names"); g.n("sv", "set", var="SaveVersion", cls=SG_NAMES, inp={"self": "@gv.Names", "SaveVersion": str(NAMES_VERSION)})
    g.call("sg", K_GS, "SaveGameToSlot", inp={"SaveGameObject": "@gn.Names", "SlotName": NAMES_SLOT, "UserIndex": "0"})
    g.chain("entry", "sv", "sg")
    return fn("Save Names", graph=g)


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


# ---------------- Free cam (pure maths; the actor handling lives in gen_manager_ui.py) ----------------
FREE_RADIUS = 600.0   # cm, sphere around Jodi's actor location (4 m felt too tight in the game)
S_VEC = "struct:/Script/CoreUObject.Vector"


def _bit(g, id, keys, bit):
    """keys & bit != 0 -> bool pin."""
    g.call(id + "_a", K_MATH, "And_IntInt", inp={"A": keys, "B": str(bit)}); g.call(id, K_MATH, "NotEqual_IntInt", inp={"A": "@%s_a.ReturnValue" % id, "B": "0"}); return "@%s.ReturnValue" % id


def f_free_cam_dir():
    """Movement direction from the key bits (1 W, 2 S, 4 A, 8 D, 16 Q, 32 E), yaw and pitch: forward along the view (with pitch: looking down + W flies down),
    right horizontal, up = world Z; normalised (0 stays 0)."""
    g = G()
    g.call("rot", K_MATH, "MakeRotator", inp={"Roll": "0.0", "Pitch": "0.0", "Yaw": "@entry.yaw"}); g.call("rotv", K_MATH, "MakeRotator", inp={"Roll": "0.0", "Pitch": "@entry.pitch", "Yaw": "@entry.yaw"})
    g.call("fwd", K_MATH, "GetForwardVector", inp={"InRot": "@rotv.ReturnValue"}); g.call("rgt", K_MATH, "GetRightVector", inp={"InRot": "@rot.ReturnValue"})
    g.call("up", K_MATH, "MakeVector", inp={"X": "0.0", "Y": "0.0", "Z": "1.0"})
    def axis(id, vec, plus, minus):
        g.call(id + "_p", K_MATH, "SelectFloat", inp={"A": "1.0", "B": "0.0", "bPickA": _bit(g, id + "_bp", "@entry.keys", plus)})
        g.call(id + "_m", K_MATH, "SelectFloat", inp={"A": "-1.0", "B": "0.0", "bPickA": _bit(g, id + "_bm", "@entry.keys", minus)})
        g.call(id + "_s", K_MATH, "Add_FloatFloat", inp={"A": "@%s_p.ReturnValue" % id, "B": "@%s_m.ReturnValue" % id})
        g.call(id, K_MATH, "Multiply_VectorFloat", inp={"A": vec, "B": "@%s_s.ReturnValue" % id}); return "@%s.ReturnValue" % id
    f = axis("af", "@fwd.ReturnValue", 1, 2); r = axis("ar", "@rgt.ReturnValue", 8, 4); u = axis("au", "@up.ReturnValue", 32, 16)
    g.call("s1", K_MATH, "Add_VectorVector", inp={"A": f, "B": r}); g.call("s2", K_MATH, "Add_VectorVector", inp={"A": "@s1.ReturnValue", "B": u})
    g.call("n", K_MATH, "Normal", inp={"A": "@s2.ReturnValue", "Tolerance": "0.0001"})
    g.link("n.ReturnValue", "return.dir")
    return fn("Free Cam Dir", [param("keys", "int"), param("yaw", "float"), param("pitch", "float")], [param("dir", S_VEC)], graph=g, pure=True)


FREE_KEYS = ((("W", "Up"), 1), (("S", "Down"), 2), (("A", "Left"), 4), (("D", "Right"), 8), (("Q",), 16), (("E",), 32), (("LeftShift", "RightShift"), 64))


def f_free_cam_keys():
    """Key bits (1 W, 2 S, 4 A, 8 D, 16 Q, 32 E, 64 Shift) from the controller's key state (IsInputKeyDown is pure: const + output)."""
    g = G(); g.get("gpc", "PC"); total = None
    for i, (keys, bit) in enumerate(FREE_KEYS):
        cond = None
        for j, k in enumerate(keys):
            g.call("k%d_%d" % (i, j), E_PC, "IsInputKeyDown", inp={"self": "@gpc.PC", "Key": k}); pin = "@k%d_%d.ReturnValue" % (i, j)
            if cond is None: cond = pin
            else: g.call("o%d_%d" % (i, j), K_MATH, "BooleanOR", inp={"A": cond, "B": pin}); cond = "@o%d_%d.ReturnValue" % (i, j)
        g.call("b%d" % i, K_MATH, "SelectInt", inp={"A": str(bit), "B": "0", "bPickA": cond}); pin = "@b%d.ReturnValue" % i
        if total is None: total = pin
        else: g.call("s%d" % i, K_MATH, "Add_IntInt", inp={"A": total, "B": pin}); total = "@s%d.ReturnValue" % i
    g.link(total[1:], "return.keys")
    return fn("Free Cam Keys", outputs=[param("keys", "int")], graph=g, pure=True)


def f_free_cam_clamp():
    """Pull target back onto the sphere of radius FREE_RADIUS around center (inside: unchanged)."""
    g = G()
    g.call("d", K_MATH, "Subtract_VectorVector", inp={"A": "@entry.target", "B": "@entry.center"})
    g.call("len", K_MATH, "VSize", inp={"A": "@d.ReturnValue"}); g.call("gt", K_MATH, "Greater_FloatFloat", inp={"A": "@len.ReturnValue", "B": str(FREE_RADIUS)})
    g.call("n", K_MATH, "Normal", inp={"A": "@d.ReturnValue", "Tolerance": "0.0001"}); g.call("m", K_MATH, "Multiply_VectorFloat", inp={"A": "@n.ReturnValue", "B": str(FREE_RADIUS)})
    g.call("on", K_MATH, "Add_VectorVector", inp={"A": "@entry.center", "B": "@m.ReturnValue"})
    g.call("sel", K_MATH, "SelectVector", inp={"A": "@on.ReturnValue", "B": "@entry.target", "bPickA": "@gt.ReturnValue"})
    g.link("sel.ReturnValue", "return.v")
    return fn("Free Cam Clamp", [param("center", S_VEC), param("target", S_VEC)], [param("v", S_VEC)], graph=g, pure=True)


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
    # Manage tab / mod content / hair swatches (bodies in gen_manager_ui.py; widgets call these)
    fn("Open Mod Content", [param("mod", "name")]), fn("Hair Swatch Clicked", [param("key", "name")]), fn("On Manage Search Changed", [param("text", "text")]), fn("On Look Search Changed", [param("text", "text")]),
    fn("Focus Name Row", [param("row", "object:" + E_USERWIDGET), param("backwards", "bool")]),   # W_NameRow (40_widgets) is not known here
    fn("Refresh Manage Rows"), fn("Manage Search For", [param("s", "string")]),   # W_NameRow links / commit
    fn("Finish Item Rename", [param("name", "name"), param("text", "string")]),   # W_ClothesButton rename field (Enter)
    fn("Manage Go To", [param("kind", "name"), param("row", "name")]),   # W_NameRow icon click
    fn("Rebuild Look Cats"), fn("Rebuild Look"), fn("Select Look Cat", [param("name", "name")]), fn("Look Clicked", [param("name", "name")]),
    fn("Look Caption", [param("type", "name")], [param("caption", "text")]), fn("Look Count", [param("type", "name"), param("filtered", "bool")], [param("n", "int")]),
    fn("Is Look Selected", [param("type", "name"), param("style", "name")], [param("yes", "bool")]),
    fn("Rebuild Body"), fn("Poll Body"), fn("Save Appearance Data"),
    fn("Scan Body Mods"), fn("Apply Body", [param("name", "name")]), fn("Apply Saved Body"), fn("Select Body", [param("name", "name")]),
    fn("Bag All Worn"), fn("Wear Queue Step"), fn("Finish Apply Snapshot"), fn("Apply Body Scales"), fn("Body Scale Factors", [param("name", "name")], outputs=[param("factors", "float", "array")]),
    fn("Set Body Scale Factors", [param("name", "name"), param("factors", "float", "array")]), fn("Reset Body Scales"), fn("Poll Body Scales"),
    fn("Select Language", [param("choice", "int")]), fn("Apply Strings"),
    fn("Focus Code", outputs=[param("code", "int")]), fn("Update Focus"),
    fn("Hair Reset Color", [param("name", "name")]), fn("Clothes Reset Color", [param("name", "name")]), fn("On Hair Context", [param("name", "name")]), fn("Apply Nude"), fn("Fix Loaded Underwear"),
    fn("Rebuild Options"), fn("Poll Options"), fn("Apply Options"), fn("Apply Theme"), fn("Open Theme Color", [param("key", "name")]), fn("Select Key", [param("name", "name")]),
    fn("Load Presets"), fn("Preset Icon", [param("number", "int")], [param("tex", "object:" + E_TEX2D)]), fn("Preset Clicked", [param("index", "int")]),
    fn("Preset Delete", [param("index", "int")]), fn("Preset Add"), fn("On Preset Context", [param("index", "int")]), fn("Preset Index", [param("name", "name")], [param("index", "int")]),
    fn("Capture Preset Icon", [param("number", "int")]),
    fn("Select Layout", [param("name", "name")]), fn("Rebuild Status"), fn("Set View Shift"),
    fn("Start Free Cam"), fn("Stop Free Cam"),
    fn("Free Cam Look", [param("delta", "struct:/Script/CoreUObject.Vector2D")]), fn("Free Cam Wheel", [param("delta", "float")]), fn("Free Cam Step", [param("dt", "float")]),
    fn("Cam Tick", [param("dt", "float")]), fn("Start Photo Mode"), fn("End Photo Mode"),
    fn("Can Wear", [param("name", "name")], [param("yes", "bool")]), fn("Select Unowned", [param("name", "name")]),
    fn("Take Snapshot", outputs=[param("snap", "struct:" + S_SNAP)]), fn("Push History"), fn("Apply Snapshot", [param("snap", "struct:" + S_SNAP)]), fn("Undo"), fn("Redo"),
    fn("Load Looks"), fn("Save Looks"), fn("Log Line", [param("text", "string")]), fn("Looks Count", outputs=[param("n", "int")]), fn("Add Look"), fn("Update Look", [param("index", "int")]), fn("Delete Look", [param("index", "int")]),
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
    # bone-scale sliders: S_BodyScale = ABP_BodyScale's variables (row struct of a body pak's Body_Scale table), S_Floats = map value (BP maps take no arrays)
    struct(S_BODYSCALE, [param(v, "struct:/Script/CoreUObject.Vector") for v, _, _ in bg.GROUPS]),
    struct(S_FLOATS, [param("Values", "float", "array")]),
    struct(S_SNAP, [param("Worn", "name", "array"), param("Makeup", "name", "map", value_type="struct:" + P_MDATA_S), param("Skin", "name"), param("Hair", "name"),
                    param("Colors", "name", "map", value_type=S_LINCOLOR), param("HairColor", S_LINCOLOR), param("Boobs", "float"), param("Waist", "float"), param("Hip", "float"), param("Body", "name"),
                    param("Scales", "float", "array")]),
    struct(S_LOOK, [param("Name", "string"), param("Id", "int"), param("Snap", "struct:" + S_SNAP)]),
    blueprint(SG_LOOKS, "/Script/Engine.SaveGame", variables=[var("Looks", "struct:" + S_LOOK, "array"), var("NextId", "int", default="1")]),
    blueprint(SG_LOG, "/Script/Engine.SaveGame", variables=[var("Lines", "string", "array")]),
    blueprint(SG_NAMES, "/Script/Engine.SaveGame", variables=[var("SaveVersion", "int"), var("Names", "name", "map", value_type="string")]),
    struct(S_STR, [param(l, "text") for l in LANGS]),
    datatable(T_STRINGS, S_STR, rows=string_rows()),
    datatable(M + "/TKA_Mod_Table", "/Game/Project/Tables/DLC_Struct"),
    blueprint(M + "/SG_AltUI", "/Script/Engine.SaveGame",
              variables=[var("Favorites", "name", "array"), var("HiddenItems", "name", "array"), var("OnlyOwned", "bool"), var("OnlyFav", "bool"), var("OnlyVanilla", "bool"), var("SubTabsCollapsed", "bool"), var("LookOnlyFav", "bool"), var("LookChipsCollapsed", "bool"), var("GroupLen", "int"), var("ChipH", "int"), var("LastSlot", "name"),
                         var("ScrollMult", "float", default="0"), var("TileScale", "float", default="0"),   # 0 = never set -> default
                         var("Unlimited", "bool"), var("LeftFree", "int"), var("CamFov", "float", default="0"), var("CamDist", "float", default="0"), var("OnlyModsNames", "bool", default="true"), var("CaseSensitiveNames", "bool"), var("MergeGroups", "bool"), var("MergeMods", "bool"), var("TipNoPrefix", "bool"), var("TipNoIds", "bool"), var("FreedConflicts", "name", "array"), var("HairSwatchesOpen", "bool"), var("BodyVariant", "name"), var("LangChoice", "int"), var("PanToSlot", "bool"), var("AllowNude", "bool"), var("OutfitNames", "string", "map", value_type="string"),
                         var("UnownedMode", "int"),
                         var("BodyScales", "name", "map", value_type="struct:" + S_FLOATS),
                         var("ThemeSet", "bool"), var("BgAlpha", "float", default="0"), var("TileAlpha", "float", default="0"), var("ToggleKey", "name"),
                         var("SaveVersion", "int")] + [var("Theme" + k, S_LINCOLOR) for k, _, _ in THEME]),   # SaveVersion 0 = save from before the versioning (0 = "never set" for floats)
    blueprint(MGR, E_ACTOR,
              variables=[var("Player", "object:" + P_JODI), var("PC", "object:" + P_PC), var("ControlDisabled", "bool"),
                         var("Names", "object:" + SG_NAMES), var("CatalogDirty", "bool"),
                         var("ItemOriginMod", "name", "map", value_type="name"), var("ModCaption", "name", "map", value_type="text"), var("ModList", "name", "array"),
                         var("ViewMod", "name"), var("ContentFrom", "name"), var("ManageCat", "name", default="Mods"), var("ManageSub", "name"), var("ManageSubCounts", "name", "map", value_type="int"), var("ManageSubFiltered", "name", "map", value_type="int"), var("ManageSearchActive", "bool"), var("LookSearchText", "string"), var("TmpRest", "string"), var("TmpRest2", "text"), var("TmpMod", "name"), var("ConflictPairs", "name", "array"), var("TmpConflicts", "name", "array"), var("TmpSubSave", "name"), var("OnlyModsNames", "bool", default="true"), var("CaseSensitiveNames", "bool"), var("MergeGroups", "bool"), var("MergeMods", "bool"), var("ModAlias", "name", "map", value_type="name"), var("TipNoPrefix", "bool"), var("TipNoIds", "bool"), var("FreedConflicts", "name", "array"), var("HairSwatchesOpen", "bool"),
                         var("UnownedMode", "int"),
                         var("ManageSearchText", "string"), var("ContextKind", "name"), var("TmpNames3", "name", "array"), var("TmpStr3", "string"),
                         var("ModGroupPairs", "name", "array"), var("VanillaGroups", "name", "array"), var("GroupModCount", "name", "map", value_type="int"), var("GroupAlias", "name", "map", value_type="name"), var("TmpCaptionOwner", "string", "map", value_type="name"), var("ManageRowWidgets", "object:" + E_USERWIDGET, "array"), var("RenameTile", "object:" + E_WIDGET), var("TmpParentMod", "name"), var("TmpTex", "object:" + E_TEX2D), var("TmpStrings2", "string", "array"), var("TmpVector", "struct:/Script/CoreUObject.Vector"),
                         var("Slots", "name", "array"), var("SlotGroup", "name", "map", value_type="name"),
                         var("Catalog", "name", "map", value_type=T_LIST), var("ItemSlot", "name", "map", value_type="name"),
                         var("CatalogRows", "int"), var("Worn", "name", "array"), var("Owned", "name", "array"), var("OwnedSet", "name", "set"), var("SlotCounts", "name", "map", value_type="int"), var("SlotNames", "name", "map", value_type="struct:" + S_NAMES),
                         var("Alphabet", "string", default="0123456789abcdefghijklmnopqrstuvwxyz"),
                         var("TmpI", "int"), var("TmpKey", "int64"), var("TmpKey1", "int64"), var("TmpKey2", "int64"), var("TmpKeys", "int64", "array"), var("TmpKeys2", "int64", "array"), var("TmpStr", "string"), var("TmpItems", T_ITEM, "array"), var("TmpItems3", T_ITEM, "array"), var("FilteredCounts", "name", "map", value_type="int"),
                         var("TmpIdx", "int"), var("TmpFound", "bool"), var("TmpName", "name"), var("TmpNames", "name", "array"), var("TmpItem", T_ITEM),
                         var("TmpGroup", "name"), var("PanelOpen", "bool"),
                         var("CurrentSlot", "name"), var("CurrentGroup", "name"), var("SearchText", "string"), var("LockStrategy", "int", default="0"),
                         var("Favorites", "name", "array"), var("HiddenItems", "name", "array"), var("TmpText", "text"), var("TmpStrings", "string", "array"), var("TmpStr2", "string"), var("Settings", "object:" + M + "/SG_AltUI"), var("ContextItem", "name"), var("LastButton", "object:" + E_WIDGET), var("CachedOnlyOwned", "bool"), var("CachedOnlyFav", "bool"), var("CachedOnlyVanilla", "bool"), var("SubTabsCollapsed", "bool"), var("GroupLen", "int"), var("OptGroupLen", "float"), var("ChipH", "int"), var("OptChipH", "float"),
                         var("ItemByName", "name", "map", value_type=T_ITEM), var("TmpSlotItems", T_ITEM, "array"), var("AllItems", T_ITEM, "array"), var("Outfits", "object:" + P_OUTFITS), var("Page", "name", default="Clothes"), var("ContextOutfit", "int"),
                         var("LookCat", "name", default="Skin"), var("LookCatSave", "name"), var("LookGroup", "name"), var("LookOnlyFav", "bool"), var("LookChipsCollapsed", "bool"), var("LookRowKinds", "name", "array"), var("LookRows", "name", "array"), var("LookTypes", "name", "array"), var("MakeupDirty", "bool"), var("BoobsChanged", "bool"), var("ColorMode", "name", default="Clothes"),
                         var("BodyBreast", "float"), var("BodyWaist", "float"), var("TmpNames2", "name", "array"), var("TmpNames3", "name", "array"), var("TmpNames4", "name", "array"), var("TmpName2", "name"), var("TmpBool", "bool"),
                         var("TmpColor", S_LINCOLOR), var("TmpColors", "name", "map", value_type=S_LINCOLOR),
                         var("LooksSave", "object:" + SG_LOOKS), var("TmpLook", "struct:" + S_LOOK), var("ContextLook", "int"), var("LookIcons", "int", "map", value_type="object:" + E_TEX2D),
                         var("PhotoRT", "object:/Script/Engine.TextureRenderTarget2D"), var("PhotoKind", "name"), var("PhotoDir", "string"), var("PhotoFile", "string"), var("ScrollMult", "float", default="4.0"), var("TileScale", "float", default="1.0"), var("OptScroll", "float"), var("OptScale", "float"),
                         var("Presets", "object:" + P_PRESET_SAVE), 
                         var("TickCount", "int"), var("LogSave", "object:" + SG_LOG), var("IconFrames", "int"), var("IconActor", "object:/Script/Engine.SceneCapture2D"), var("IconNumber", "int"),
                         var("Unlimited", "bool"), var("LeftFree", "int"), var("ViewShift", "float"), var("CamFov", "float", default="0.8"), var("CamDist", "float", default="1.0"), var("OptFov", "float"), var("OptDist", "float"), var("IconLight", "object:/Script/Engine.SpotLight"), var("UndoStack", "struct:" + S_SNAP, "array"), var("RedoStack", "struct:" + S_SNAP, "array"), var("TmpSnap", "struct:" + S_SNAP), var("TmpSnap2", "struct:" + S_SNAP), var("PresetIcons", "int", "map", value_type="object:" + E_TEX2D), var("TmpPreset", "struct:" + P_PRESET_S), var("ContextPreset", "int"), var("TmpIcons", "object:" + E_TEX2D, "array"),
                         # content view (View content): open index per tab (-1 = closed), the rendered snapshot + title, tile origin for "Show in tab", highlight/scroll target
                         var("ViewOutfit", "int", default="-1"), var("ViewLook", "int", default="-1"), var("ViewPreset", "int", default="-1"), var("ViewSnap", "struct:" + S_SNAP), var("ViewTitle", "string"),
                         var("ContextSlot", "name"), var("HighlightItem", "name"), var("KeepHighlight", "bool"), var("ScrollWidget", "object:" + E_WIDGET),   # TmpSection (W_ContentSection) lives in the augment: the widget class exists only after 40_widgets
                         var("TmpFColors", "name", "map", value_type=S_COLOR),
                         var("BodyMods", "name", "array"), var("BodyCaptions", "name", "map", value_type="text"), var("StandardMesh", "object:" + E_SKELMESH),
                         var("BodyMesh", "object:" + E_SKELMESH), var("CurrentBody", "name"), var("BodyVariant", "name"),
                         var("WearQueue", "name", "array"), var("WearWait", "int"), var("PendingSnap", "struct:" + S_SNAP), var("SnapPending", "bool"), var("PendingMissing", "string", "array"),
                         var("NextSnap", "struct:" + S_SNAP), var("NextPending", "bool"),
                         var("BodyScales", "name", "map", value_type="struct:" + S_FLOATS), var("BodyDefaults", "struct:" + S_BODYSCALE), var("ScaleActive", "bool"),
                         var("BodyScaleVals", "float", "array"), var("TmpFloats", "float", "array"), var("LastHeight", "float", default="1.0"),
                         var("Lang", "int"), var("LangChoice", "int"), var("Strings", "name", "map", value_type="text"),
                         var("PanToSlot", "bool"), var("AllowNude", "bool"), var("FocusOn", "bool"), var("FocusZ", "float"), var("FocusZoom", "float", default="1.0"), var("TmpFloat", "float"),
                         var("CamMode", "int"), var("FreeCam", "object:/Script/Engine.CameraActor"), var("CamInput", "object:" + E_ACTOR), var("FreeCtrlRot", "struct:/Script/CoreUObject.Rotator"), var("FreeYaw", "float"), var("FreePitch", "float"), var("FreeSpeed", "float", default="200.0"),
                         var("ThemeVersion", "int"), var("ToggleKey", "name", default="B"), var("BgAlpha", "float", default=str(BG_ALPHA)), var("TileAlpha", "float", default=str(TILE_ALPHA)), var("ThemeKey", "name")]
                        + [var("Theme" + k, S_LINCOLOR) for k, _, _ in THEME] + [var(n, S_LINCOLOR) for n in DERIVED_NAMES],
              functions=[f_init_slot_groups(), f_order_slots(), f_sort_key(), f_display_name(), f_scan_mod_items(), f_build_catalog(),
                         f_items_for_slot(), f_slot_count(), f_filtered_counts(), f_cut_caption(), f_chip_caption(), f_item_slot(), f_is_worn(), f_is_owned(), f_worn_in_slot(),
                         f_shown_owned(), f_refresh_state(), f_build_conflicts(), f_pair_in(), f_conflicts_with(), f_is_freed(), f_set_freed(), f_conflicting_slots(), f_conflicting_worn_slots(), f_save_worn(), f_wear(), f_take_off(), f_debug_status(), f_find_item(), f_is_favorite(), f_filtered_items(),
                         f_groups_of_slot(), f_group_caption_default(), f_group_caption(), f_scan_mod_groups(), f_build_group_aliases(), f_group_alias(), f_mod_alias(), f_item_tip(), f_load_settings(), f_save_settings(), f_default_name(), f_item_mod(), f_mod_caption(), f_name_key(), f_custom_name(), f_shown_name(), f_set_custom_name(), f_load_names(), f_save_names(), f_toggle_favorite(), f_is_item_hidden(), f_toggle_item_hidden(), f_t(), f_detect_language(), f_init_strings(),
                         f_reset_theme(), f_theme_color(), f_set_theme_color(), f_layout_fraction(), f_free_cam_dir(), f_free_cam_keys(), f_free_cam_clamp()] + UI_SIGNATURES),
]
write(os.path.join(os.path.dirname(__file__), "..", "30_manager.json"), assets)
