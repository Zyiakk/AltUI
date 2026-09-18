"""Generates assets/50_manager_ui.json: UI bodies of the manager (augment) + event graph. Runs after 40_widgets.json."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *
from gen_manager import pop, text_from_str, S_ITEM, T_ITEM, MGR, S_SNAP, SG, S_LOOK, SG_LOOKS, LOOKS_SLOT
from strings import LANGS, LIST_CAP
from theme import THEME, DERIVED, BG_ALPHA, TILE_ALPHA
from gen_manager import LAYOUTS, LAYOUT_FRACTIONS

W_ROW = M + "/W_MenuRow"; W_MENU = M + "/W_ContextMenu"
P_PAL = "/Game/Project/UserInterface/PaletteUI"; P_PALR = "/Game/Project/UserInterface/Widgets/Paletter"
W_TOP = M + "/W_TopTab"; W_OUTFIT = M + "/W_OutfitButton"; W_LOOK = M + "/W_LookButton"; W_SECTION = M + "/W_ContentSection"; W_TXT = M + "/W_TextButton"; T_UNDO = M + "/T_Undo"; T_REDO = M + "/T_Redo"; SC = 1.9; P_HOOK = "/Game/Project/Classes/TKA_PlayerCameraManager"; OUTFIT_SLOT = "Outfits"
W_PANEL = M + "/W_AltUI"; W_HEAD = M + "/W_GroupHeader"; W_TAB = M + "/W_SlotTab"; W_BTN = M + "/W_ClothesButton"; W_SUB = M + "/W_SubTab"; W_SWATCH = M + "/W_ColorSwatch"


def create_widget(g, id, cls):
    """WBL.Create(self, cls, PC) -> cast -> pin of the typed widget."""
    g.get(id + "_pc", "PC")
    g.call(id + "_cr", K_WBL, "Create", inp={"WidgetType": cls, "OwningPlayer": "@" + id + "_pc.PC"})
    g.cast(id, cls, "@" + id + "_cr.ReturnValue")
    return "@%s.As%s" % (id, cls.rsplit("/", 1)[-1])


def hslot_pad(g, id, widget_pin, right, left=0):
    """Padding of a child in a HorizontalBox (call after adding); returns the exec id."""
    g.call(id + "_s", "/Script/UMG.WidgetLayoutLibrary", "SlotAsHorizontalBoxSlot", inp={"Widget": widget_pin})
    g.call(id, "/Script/UMG.HorizontalBoxSlot", "SetPadding", inp={"self": "@%s_s.ReturnValue" % id, "InPadding": "(Left=%d,Top=0,Right=%d,Bottom=0)" % (int(round(left * SC)), int(round(right * SC)))})
    return id


def set_manager(g, id, cls, widget_pin):
    g.self_(id + "_me")
    g.n(id, "set", var="Manager", cls=cls, inp={"self": widget_pin, "Manager": "@" + id + "_me.self"})
    return id


def name_text(g, id, name_pin):
    g.call(id, K_TXT, "Conv_NameToText", inp={"InName": name_pin}); return "@" + id + ".ReturnValue"


def tt(g, id, key):
    """T(key) (pure manager function, Strings table) -> text pin."""
    g.n(id, "call_self", function="T", inp={"key": key}); return "@%s.text" % id


def ts(g, id, key):
    """T(key) as a string pin (for Concat/SelectString)."""
    g.call(id + "_2s", K_TXT, "Conv_TextToString", inp={"InText": tt(g, id, key)}); return "@%s_2s.ReturnValue" % id


def key_text(g, id, prefix, name_pin):
    """T(prefix + name) -> text pin (Slot_/Group_ keys at runtime; unknown key -> the key itself)."""
    g.call(id + "_s", K_STR, "Conv_NameToString", inp={"InName": name_pin}); g.call(id + "_c", K_STR, "Concat_StrStr", inp={"A": prefix, "B": "@%s_s.ReturnValue" % id})
    g.call(id + "_n", K_STR, "Conv_StringToName", inp={"InString": "@%s_c.ReturnValue" % id}); return tt(g, id, "@%s_n.ReturnValue" % id)


# ---------------- Toggle / Open / Close ----------------
def f_toggle():
    g = G(); g.get("go", "PanelOpen"); g.branch("b", "@go.PanelOpen")
    g.n("cl", "call_self", function="Close Panel"); g.n("op", "call_self", function="Open Panel")
    g.chain("entry", "b", "cl"); g.chain("b:else", "op"); return fn("Toggle Panel", graph=g)


def f_open():
    g = G()
    g.get("gp", "Panel"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gp.Panel"}); g.branch("b", "@iv.ReturnValue")
    pw = create_widget(g, "cw", W_PANEL)
    g.set("sp", "Panel", inp={"Panel": pw})
    set_manager(g, "sm", W_PANEL, "@sp.Output_Get")
    g.get("gp9", "Panel"); g.get("gco", "CachedOnlyOwned"); g.get("gcf", "CachedOnlyFav"); g.get("gcv", "CachedOnlyVanilla")
    g.call("sft", W_PANEL, "Set Filter Toggles", inp={"self": "@gp9.Panel", "owned": "@gco.CachedOnlyOwned", "fav": "@gcf.CachedOnlyFav", "vanilla": "@gcv.CachedOnlyVanilla"})
    g.get("gp2", "Panel"); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@gp2.Panel", "ZOrder": "100"})
    g.set("so", "PanelOpen", inp={"PanelOpen": "true"})
    g.get("gpc", "PC"); g.call("cur", P_PC, "ShowMouseCursor", inp={"self": "@gpc.PC", "show": "true"})
    g.get("gpc2", "PC"); g.get("gp3", "Panel")
    g.call("im", K_WBL, "SetInputMode_GameAndUIEx", inp={"PlayerController": "@gpc2.PC", "InWidgetToFocus": "@gp3.Panel", "InMouseLockMode": "DoNotLock", "bHideCursorDuringCapture": "false"})
    # movement lock according to strategy
    g.get("gls", "LockStrategy"); g.call("eq0", K_MATH, "EqualEqual_IntInt", inp={"A": "@gls.LockStrategy", "B": "0"}); g.branch("bl", "@eq0.ReturnValue")
    g.get("gpc3", "PC"); g.call("epc", P_PC, "Enable Player Control", inp={"self": "@gpc3.PC", "Base": "false", "Playing": "false"})
    g.get("gpl", "Player"); g.get("gpc4", "PC"); g.call("di", E_ACTOR, "DisableInput", inp={"self": "@gpl.Player", "PlayerController": "@gpc4.PC"})
    g.n("rs", "call_self", function="Refresh State")
    # initialise CurrentSlot
    g.get("gcs", "CurrentSlot"); g.call("eqn", K_MATH, "EqualEqual_NameName", inp={"A": "@gcs.CurrentSlot", "B": "None"}); g.branch("bs", "@eqn.ReturnValue")
    g.get("gsl0", "Slots"); g.call("sll", K_ARR, "Array_Length", inp={"TargetArray": "@gsl0.Slots"}); g.call("slgt", K_MATH, "Greater_IntInt", inp={"A": "@sll.ReturnValue", "B": "0"}); g.branch("bsl", "@slgt.ReturnValue")
    g.get("gsl", "Slots"); g.call("first", K_ARR, "Array_Get", inp={"TargetArray": "@gsl.Slots", "Index": "0"})
    g.set("scs", "CurrentSlot", inp={"CurrentSlot": "@first.Item"})
    g.n("rl", "call_self", function="Rebuild Left"); g.n("rt", "call_self", function="Rebuild SubTabs"); g.n("rli", "call_self", function="Rebuild List")
    g.get("gp4", "Panel"); g.call("kf", E_WIDGET, "SetKeyboardFocus", inp={"self": "@gp4.Panel"})
    # reload outfits (the mirror may have changed them), always start on the "Clothes" page
    g.n("lo", "call_self", function="Load Outfits"); g.n("lp", "call_self", function="Load Presets"); g.n("ao", "call_self", function="Apply Options"); g.set("spo", "Page", inp={"Page": "Clothes"})
    g.set("svo", "ViewOutfit", inp={"ViewOutfit": "-1"}); g.set("svl", "ViewLook", inp={"ViewLook": "-1"}); g.set("svp", "ViewPreset", inp={"ViewPreset": "-1"})   # content views end with the panel session
    g.get("gp5", "Panel"); g.call("spg", W_PANEL, "Set Page", inp={"self": "@gp5.Panel", "page": "Clothes"}); g.n("rtt", "call_self", function="Rebuild TopTabs")
    g.get("gp6", "Panel"); g.call("csl", W_PANEL, "Clear Search Links", inp={"self": "@gp6.Panel"})
    xw = create_widget(g, "cx", W_TXT); set_manager(g, "smx", W_TXT, xw)
    g.call("xt", K_TXT, "Conv_StringToText", inp={"InString": "\u00d7"}); g.call("xi", W_TXT, "Init", inp={"self": xw, "action": "ClearSearch", "caption": "@xt.ReturnValue"})
    g.get("gp7", "Panel"); g.call("asl", W_PANEL, "Add Search Link", inp={"self": "@gp7.Panel", "widget": xw})
    g.n("aps", "call_self", function="Apply Strings")
    g.get("gp8", "Panel"); g.call("ibt", W_PANEL, "Init Buttons", inp={"self": "@gp8.Panel"})   # +/- round buttons: manager, action, icon
    g.n("ath", "call_self", function="Apply Theme")
    g.chain("entry", "b", "atv"); g.chain("b:else", "cw_cr", "sp", "sm", "sft", "ibt", "aps", "ath", "atv")
    g.chain("atv", "so", "cur", "im", "bl", "epc", "rs"); g.chain("bl:else", "di", "rs")
    g.n("rst", "call_self", function="Rebuild Status")
    g.n("uf", "call_self", function="Update Focus")
    g.chain("rs", "lo", "lp", "ao", "spo", "svo", "svl", "svp", "spg", "rtt", "rst", "csl", "cx_cr", "smx", "xi", "asl", "bs", "bsl", "scs", "rl"); g.chain("bs:else", "rl"); g.chain("bsl:else", "rl"); g.chain("rl", "rt", "rli", "kf", "uf")
    return fn("Open Panel", graph=g)


def f_close():
    g = G()
    g.get("gp", "Panel"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gp.Panel"}); g.branch("b", "@iv.ReturnValue")
    g.get("gp2", "Panel"); g.call("rm", E_WIDGET, "RemoveFromParent", inp={"self": "@gp2.Panel"})
    g.set("so", "PanelOpen", inp={"PanelOpen": "false"})
    g.get("gpc", "PC"); g.call("cur", P_PC, "ShowMouseCursor", inp={"self": "@gpc.PC", "show": "false"})
    g.get("gpc2", "PC"); g.call("im", K_WBL, "SetInputMode_GameOnly", inp={"PlayerController": "@gpc2.PC"})
    g.get("gls", "LockStrategy"); g.call("eq0", K_MATH, "EqualEqual_IntInt", inp={"A": "@gls.LockStrategy", "B": "0"}); g.branch("bl", "@eq0.ReturnValue")
    g.get("gpc3", "PC"); g.call("epc", P_PC, "Enable Player Control", inp={"self": "@gpc3.PC", "Base": "true", "Playing": "true"})
    g.get("gpl", "Player"); g.get("gpc4", "PC"); g.call("ei", E_ACTOR, "EnableInput", inp={"self": "@gpl.Player", "PlayerController": "@gpc4.PC"})
    g.n("cmn", "call_self", function="Close Menu"); g.n("svs", "call_self", function="Save Settings"); g.n("ccl", "call_self", function="Close Color")
    g.n("sad", "call_self", function="Save Appearance Data"); g.set("svs0", "ViewShift", inp={"ViewShift": "0.0"}); g.n("svc0", "call_self", function="Set View Shift")
    g.chain("entry", "cmn", "ccl", "b", "rm", "so"); g.chain("b:else", "so"); g.chain("so", "cur", "im", "bl", "epc", "svs"); g.chain("bl:else", "ei", "svs"); g.chain("svs", "sad", "svs0", "svc0")
    return fn("Close Panel", graph=g)


# ---------------- Rebuild Left ----------------
def f_rebuild_left():
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Left", inp={"self": "@gp.Panel"})
    # filters as the panel shows them (the caches are refreshed by Rebuild List, which runs after this)
    g.get("gpo", "Panel"); g.call("oo", W_PANEL, "Get Only Owned", inp={"self": "@gpo.Panel"})
    g.get("gpf", "Panel"); g.call("of", W_PANEL, "Get Only Fav", inp={"self": "@gpf.Panel"})
    g.get("gpv", "Panel"); g.call("ov", W_PANEL, "Get Only Vanilla", inp={"self": "@gpv.Panel"})
    g.get("gst", "SearchText"); g.call("sne", K_STR, "IsEmpty", inp={"InString": "@gst.SearchText"}); g.call("sact", K_MATH, "Not_PreBool", inp={"A": "@sne.ReturnValue"})
    g.call("fa1", K_MATH, "BooleanOR", inp={"A": "@oo.yes", "B": "@of.yes"}); g.call("fa2", K_MATH, "BooleanOR", inp={"A": "@fa1.ReturnValue", "B": "@ov.yes"})
    g.call("fact", K_MATH, "BooleanOR", inp={"A": "@fa2.ReturnValue", "B": "@sact.ReturnValue"}); g.set("sfa", "TmpBool", inp={"TmpBool": "@fact.ReturnValue"})
    g.get("gst2", "SearchText"); g.n("fc", "call_self", function="Filtered Counts", inp={"search": "@gst2.SearchText", "onlyOwned": "@oo.yes", "onlyFav": "@of.yes", "onlyVanilla": "@ov.yes"})
    g.set("sg0", "TmpGroup", inp={"TmpGroup": "None"})
    g.get("gsl", "Slots"); g.foreach("fe", "@gsl.Slots")
    g.get("gsg", "SlotGroup"); g.call("grp", K_MAP, "Map_Find", inp={"TargetMap": "@gsg.SlotGroup", "Key": "@fe.Array Element"})
    g.get("gtg", "TmpGroup"); g.call("neq", K_MATH, "NotEqual_NameName", inp={"A": "@grp.Value", "B": "@gtg.TmpGroup"}); g.branch("bh", "@neq.ReturnValue")
    hw = create_widget(g, "ch", W_HEAD); set_manager(g, "chm", W_HEAD, hw)
    g.call("hi", W_HEAD, "Init", inp={"self": hw, "caption": key_text(g, "ht", "Group_", "@grp.Value")})
    g.get("gp2", "Panel"); g.call("ah", W_PANEL, "Add Left", inp={"self": "@gp2.Panel", "widget": hw})
    g.set("sg", "TmpGroup", inp={"TmpGroup": "@grp.Value"})
    tw = create_widget(g, "ct", W_TAB)
    set_manager(g, "smt", W_TAB, tw)
    g.n("win", "call_self", function="Worn In Slot", inp={"slot": "@fe.Array Element"})
    g.n("fi", "call_self", function="Find Item", inp={"name": "@win.name"})
    g.brk("bi", S_ITEM, "@fi.item")
    g.n("cnt", "call_self", function="Slot Count", inp={"slot": "@fe.Array Element"})
    g.call("has", K_MATH, "Greater_IntInt", inp={"A": "@cnt.n", "B": "0"})
    g.get("gcs", "CurrentSlot"); g.call("sel", K_MATH, "EqualEqual_NameName", inp={"A": "@fe.Array Element", "B": "@gcs.CurrentSlot"})
    g.get("gfc", "FilteredCounts"); g.call("fcf", K_MAP, "Map_Find", inp={"TargetMap": "@gfc.FilteredCounts", "Key": "@fe.Array Element"})
    g.get("gfa", "TmpBool"); g.call("fsel", K_MATH, "SelectInt", inp={"A": "@fcf.Value", "B": "-1", "bPickA": "@gfa.TmpBool"})
    g.call("ti", W_TAB, "Init", inp={"self": tw, "slot": "@fe.Array Element", "caption": key_text(g, "tt", "Slot_", "@fe.Array Element"), "count": "@cnt.n",
                                     "worn icon": "@bi.Icon", "selected": "@sel.ReturnValue", "has items": "@has.ReturnValue", "filtered": "@fsel.ReturnValue"})
    g.get("gp3", "Panel"); g.call("at", W_PANEL, "Add Left", inp={"self": "@gp3.Panel", "widget": tw})
    # "All" at the very top (pseudo slot All, no thumbnail)
    aw = create_widget(g, "ca", W_TAB); set_manager(g, "sma", W_TAB, aw)
    g.n("acnt", "call_self", function="Slot Count", inp={"slot": "All"})
    g.get("gcsa", "CurrentSlot"); g.call("asel", K_MATH, "EqualEqual_NameName", inp={"A": "All", "B": "@gcsa.CurrentSlot"})
    g.get("gfca", "FilteredCounts"); g.call("fcfa", K_MAP, "Map_Find", inp={"TargetMap": "@gfca.FilteredCounts", "Key": g.lit_name("lfa", "All")})   # wildcard pin: typed literal, a plain default arrives as None
    g.get("gfaa", "TmpBool"); g.call("fsela", K_MATH, "SelectInt", inp={"A": "@fcfa.Value", "B": "-1", "bPickA": "@gfaa.TmpBool"})
    g.call("ai", W_TAB, "Init", inp={"self": aw, "slot": "All", "caption": tt(g, "at0", "Slot_All"), "count": "@acnt.n", "selected": "@asel.ReturnValue", "has items": "true", "filtered": "@fsela.ReturnValue"})
    g.get("gpa", "Panel"); g.call("aa", W_PANEL, "Add Left", inp={"self": "@gpa.Panel", "widget": aw})
    g.chain("entry", "cl", "sfa", "fc", "sg0", "ca_cr", "sma", "ai", "aa", "fe"); g.chain("fe", "bh", "ch_cr", "chm", "hi", "ah", "sg", "ct_cr"); g.chain("bh:else", "ct_cr")
    g.chain("ct_cr", "smt", "win", "fi", "ti", "at")
    return fn("Rebuild Left", graph=g)


# ---------------- Rebuild List / SubTabs (filters follow in M2) ----------------
def f_rebuild_list():
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear List", inp={"self": "@gp.Panel"})
    g.get("gpf", "Panel"); g.call("clf", W_PANEL, "Clear Fav", inp={"self": "@gpf.Panel"})
    g.get("gp1", "Panel"); g.call("oo", W_PANEL, "Get Only Owned", inp={"self": "@gp1.Panel"})
    g.get("gp2", "Panel"); g.call("of", W_PANEL, "Get Only Fav", inp={"self": "@gp2.Panel"})
    g.get("gpv", "Panel"); g.call("ov", W_PANEL, "Get Only Vanilla", inp={"self": "@gpv.Panel"})
    g.set("co", "CachedOnlyOwned", inp={"CachedOnlyOwned": "@oo.yes"}); g.set("cf", "CachedOnlyFav", inp={"CachedOnlyFav": "@of.yes"}); g.set("cv", "CachedOnlyVanilla", inp={"CachedOnlyVanilla": "@ov.yes"})
    g.set("nf", "TmpIdx", inp={"TmpIdx": "0"})
    g.get("gcs", "CurrentSlot"); g.get("gcg", "CurrentGroup"); g.get("gst", "SearchText")
    g.n("it", "call_self", function="Filtered Items", inp={"slot": "@gcs.CurrentSlot", "group": "@gcg.CurrentGroup", "search": "@gst.SearchText", "onlyOwned": "@oo.yes", "onlyFav": "@of.yes", "onlyVanilla": "@ov.yes"})
    g.set("sti", "TmpItems2", inp={"TmpItems2": "@it.items"})
    # pass 1: favourites block
    g.get("gti", "TmpItems2"); g.foreach("ff", "@gti.TmpItems2"); g.brk("fb", S_ITEM, "@ff.Array Element")
    g.n("ffv", "call_self", function="Is Favorite", inp={"name": "@fb.Name"}); g.branch("fbr", "@ffv.yes")
    fw = create_widget(g, "cf1", W_BTN); set_manager(g, "smf", W_BTN, fw)
    g.n("fiw", "call_self", function="Is Worn", inp={"name": "@fb.Name"}); g.n("fio", "call_self", function="Is Owned", inp={"name": "@fb.Name"})
    g.n("fdm", "call_self", function="Is Damaged", inp={"name": "@fb.Name"}); g.n("fti", "call_self", function="Item Tip", inp={"item": "@ff.Array Element"})
    g.call("fin", W_BTN, "Init", inp={"self": fw, "item": "@ff.Array Element", "worn": "@fiw.yes", "owned": "@fio.yes", "fav": "true", "damaged": "@fdm.yes", "tip": "@fti.tip"})
    g.get("gp4", "Panel"); g.call("af", W_PANEL, "Add Fav", inp={"self": "@gp4.Panel", "widget": fw})
    g.get("gn", "TmpIdx"); g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gn.TmpIdx", "B": "1"}); g.set("sn", "TmpIdx", inp={"TmpIdx": "@inc.ReturnValue"})
    g.get("gn2", "TmpIdx"); g.call("gt0", K_MATH, "Greater_IntInt", inp={"A": "@gn2.TmpIdx", "B": "0"})
    g.get("gp5", "Panel"); g.call("sfv", W_PANEL, "Set Fav Visible", inp={"self": "@gp5.Panel", "visible": "@gt0.ReturnValue"})
    # pass 2: all (alphabetical)
    g.get("gti2", "TmpItems2"); g.foreach("fe", "@gti2.TmpItems2"); g.brk("bi", S_ITEM, "@fe.Array Element")
    bw = create_widget(g, "cb", W_BTN)
    set_manager(g, "smb", W_BTN, bw)
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@bi.Name"}); g.n("io", "call_self", function="Is Owned", inp={"name": "@bi.Name"})
    g.n("ifv", "call_self", function="Is Favorite", inp={"name": "@bi.Name"})
    g.n("dm", "call_self", function="Is Damaged", inp={"name": "@bi.Name"}); g.n("bti", "call_self", function="Item Tip", inp={"item": "@fe.Array Element"})
    g.call("bin", W_BTN, "Init", inp={"self": bw, "item": "@fe.Array Element", "worn": "@iw.yes", "owned": "@io.yes", "fav": "@ifv.yes", "damaged": "@dm.yes", "tip": "@bti.tip"})
    g.get("gp3", "Panel"); g.call("ai", W_PANEL, "Add Item", inp={"self": "@gp3.Panel", "widget": bw})
    # cap: at most LIST_CAP tiles (pseudo slot "All" has ~3000 pieces)
    g.set("ci0", "TmpI", inp={"TmpI": "0"})
    g.get("gci", "TmpI"); g.call("lt", K_MATH, "Less_IntInt", inp={"A": "@gci.TmpI", "B": str(LIST_CAP)})
    g.get("gun", "Unlimited"); g.call("orc", K_MATH, "BooleanOR", inp={"A": "@lt.ReturnValue", "B": "@gun.Unlimited"})
    g.get("ghl0", "HighlightItem"); g.call("ishc", K_MATH, "EqualEqual_NameName", inp={"A": "@bi.Name", "B": "@ghl0.HighlightItem"})   # the jump target is built even beyond the cap
    g.call("orc2", K_MATH, "BooleanOR", inp={"A": "@orc.ReturnValue", "B": "@ishc.ReturnValue"}); g.branch("bcap", "@orc2.ReturnValue")
    # scroll target of a "Show in tab" jump (favourites block + list)
    g.get("ghlf", "HighlightItem"); g.call("ishf", K_MATH, "EqualEqual_NameName", inp={"A": "@fb.Name", "B": "@ghlf.HighlightItem"}); g.branch("bhlf", "@ishf.ReturnValue"); g.set("sswf", "ScrollWidget", inp={"ScrollWidget": fw})
    g.get("ghl", "HighlightItem"); g.call("ish", K_MATH, "EqualEqual_NameName", inp={"A": "@bi.Name", "B": "@ghl.HighlightItem"}); g.branch("bhl", "@ish.ReturnValue"); g.set("ssw", "ScrollWidget", inp={"ScrollWidget": bw})
    g.get("gci2", "TmpI"); g.call("cinc", K_MATH, "Add_IntInt", inp={"A": "@gci2.TmpI", "B": "1"}); g.set("sci", "TmpI", inp={"TmpI": "@cinc.ReturnValue"})
    g.get("gti3", "TmpItems2"); g.call("tlen", K_ARR, "Array_Length", inp={"TargetArray": "@gti3.TmpItems2"})
    g.call("over0", K_MATH, "Greater_IntInt", inp={"A": "@tlen.ReturnValue", "B": str(LIST_CAP)})
    g.get("gun2", "Unlimited"); g.call("nun", K_MATH, "Not_PreBool", inp={"A": "@gun2.Unlimited"}); g.call("over", K_MATH, "BooleanAND", inp={"A": "@over0.ReturnValue", "B": "@nun.ReturnValue"})
    g.get("gp6", "Panel"); g.call("slh", W_PANEL, "Set List Hint", inp={"self": "@gp6.Panel", "visible": "@over.ReturnValue"})
    g.chain("entry", "cl", "clf", "co", "cf", "cv", "nf", "ci0", "it", "sti", "ff"); g.chain("ff", "fbr", "cf1_cr", "smf", "fdm", "fti", "fin", "af", "bhlf", "sswf", "sn"); g.chain("bhlf:else", "sn")
    g.chain("ff:Completed", "sfv", "fe"); g.chain("fe", "bcap", "cb_cr", "smb", "dm", "bti", "bin", "ai", "bhl", "ssw", "sci"); g.chain("bhl:else", "sci"); g.chain("fe:Completed", "slh")
    return fn("Rebuild List", graph=g)


def f_rebuild_subtabs():
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear SubTabs", inp={"self": "@gp.Panel"})
    g.get("gcs", "CurrentSlot"); g.n("gr", "call_self", function="Groups Of Slot", inp={"slot": "@gcs.CurrentSlot"})
    g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@gr.groups"})
    g.call("gt1", K_MATH, "Greater_IntInt", inp={"A": "@len.ReturnValue", "B": "1"}); g.branch("b", "@gt1.ReturnValue")
    # "All"
    aw = create_widget(g, "ca", W_SUB); set_manager(g, "sma", W_SUB, aw)
    g.get("gcg", "CurrentGroup"); g.call("selA", K_MATH, "EqualEqual_NameName", inp={"A": "@gcg.CurrentGroup", "B": "None"})
    g.call("ia", W_SUB, "Init", inp={"self": aw, "group": "None", "caption": tt(g, "ta", "Chip_All"), "selected": "@selA.ReturnValue"})
    g.get("gp2", "Panel"); g.call("aa", W_PANEL, "Add SubTab", inp={"self": "@gp2.Panel", "widget": aw})
    # "..." right of All: collapses / expands the group chips (highlighted while collapsed)
    mw = create_widget(g, "cm", W_SUB); set_manager(g, "smm", W_SUB, mw)
    g.get("gcol", "SubTabsCollapsed")
    g.call("im", W_SUB, "Init", inp={"self": mw, "group": "AltUI_More", "caption": tt(g, "tm", "Chip_More"), "selected": "@gcol.SubTabsCollapsed"})
    g.get("gpm", "Panel"); g.call("am", W_PANEL, "Add SubTab", inp={"self": "@gpm.Panel", "widget": mw})
    # per group; collapsed: only the selected group stays visible
    g.foreach("fe", "@gr.groups")
    g.get("gcol2", "SubTabsCollapsed"); g.call("ncol", K_MATH, "Not_PreBool", inp={"A": "@gcol2.SubTabsCollapsed"})
    g.call("show", K_MATH, "BooleanOR", inp={"A": "@ncol.ReturnValue", "B": "@selG.ReturnValue"}); g.branch("bs", "@show.ReturnValue")
    sw = create_widget(g, "cs", W_SUB); set_manager(g, "sms", W_SUB, sw)
    g.get("gcol3", "SubTabsCollapsed"); g.call("fullc", K_MATH, "BooleanAND", inp={"A": "@gcol3.SubTabsCollapsed", "B": "@selG.ReturnValue"})
    g.n("cap", "call_self", function="Chip Caption", inp={"group": "@fe.Array Element", "full": "@fullc.ReturnValue"})
    g.get("gcg2", "CurrentGroup"); g.call("selG", K_MATH, "EqualEqual_NameName", inp={"A": "@gcg2.CurrentGroup", "B": "@fe.Array Element"})
    g.call("is", W_SUB, "Init", inp={"self": sw, "group": "@fe.Array Element", "caption": "@cap.caption", "selected": "@selG.ReturnValue"})
    g.get("gp3", "Panel"); g.call("as", W_PANEL, "Add SubTab", inp={"self": "@gp3.Panel", "widget": sw})
    g.chain("entry", "cl", "gr", "b", "ca_cr", "sma", "ia", "aa", "cm_cr", "smm", "im", "am", "fe"); g.chain("fe", "bs", "cs_cr", "sms", "cap", "is", "as")
    return fn("Rebuild SubTabs", graph=g)


# ---------------- Interaction ----------------
def f_select_slot():
    """Slot click: the group chip stays selected when the new slot has that group too, otherwise back to All."""
    g = G(); g.set("s", "CurrentSlot", inp={"CurrentSlot": "@entry.name"}); g.set("sg", "CurrentGroup", inp={"CurrentGroup": "None"})
    g.n("gr", "call_self", function="Groups Of Slot", inp={"slot": "@entry.name"})
    g.get("gcg", "CurrentGroup"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gr.groups", "ItemToFind": "@gcg.CurrentGroup"}); g.branch("bk", "@has.ReturnValue")
    g.n("rl", "call_self", function="Rebuild Left"); g.n("rt", "call_self", function="Rebuild SubTabs"); g.n("rli", "call_self", function="Rebuild List")
    g.get("gpg", "Page"); g.call("isl", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Look"}); g.branch("bpl", "@isl.ReturnValue")
    g.n("slc", "call_self", function="Select Look Cat", inp={"name": "@entry.name"})
    g.n("uf", "call_self", function="Update Focus")
    g.set("hlc", "HighlightItem", inp={"HighlightItem": "None"})
    g.chain("entry", "bpl", "slc"); g.chain("bpl:else", "hlc", "s", "gr", "bk", "rl", "rt", "rli", "uf"); g.chain("bk:else", "sg", "rl"); return fn("Select Slot", [param("name", "name")], graph=g)


def f_take_off_slot():
    g = G(); g.n("win", "call_self", function="Worn In Slot", inp={"slot": "@entry.name"})
    g.call("neq", K_MATH, "NotEqual_NameName", inp={"A": "@win.name", "B": "None"})
    g.call("nall", K_MATH, "NotEqual_NameName", inp={"A": "@entry.name", "B": "All"})
    g.call("ok", K_MATH, "BooleanAND", inp={"A": "@neq.ReturnValue", "B": "@nall.ReturnValue"}); g.branch("b", "@ok.ReturnValue")
    g.n("to", "call_self", function="Take Off", inp={"name": "@win.name"})
    g.n("rl", "call_self", function="Rebuild Left"); g.n("rli", "call_self", function="Rebuild List")
    g.chain("entry", "win", "b", "to", "rl", "rli"); return fn("Take Off Slot", [param("name", "name")], graph=g)


def f_on_item_clicked():
    g = G()
    g.get("gpg0", "Page"); g.n("cop", "call_self", function="Content Open", inp={"page": "@gpg0.Page"}); g.branch("bcv", "@cop.yes")   # content view: tiles are display only
    g.get("gpg", "Page"); g.call("isb", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Bag"}); g.branch("bpg", "@isb.ReturnValue")
    g.n("btw", "call_self", function="Bag Toggle Wear", inp={"name": "@entry.name"})
    g.get("gpg2", "Page"); g.call("ish", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg2.Page", "B": "Hair"}); g.branch("bph", "@ish.ReturnValue")
    g.n("hc", "call_self", function="Hair Clicked", inp={"name": "@entry.name"})
    g.get("gpg3", "Page"); g.call("isl", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg3.Page", "B": "Look"}); g.branch("bpl", "@isl.ReturnValue")
    g.n("lc", "call_self", function="Look Clicked", inp={"name": "@entry.name"})
    g.n("io", "call_self", function="Is Owned", inp={"name": "@entry.name"}); g.branch("bo", "@io.yes")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"})
    g.call("msg", K_STR, "Concat_StrStr", inp={"A": ts(g, "mk", "Msg_NotOwned"), "B": "@n2s.ReturnValue"})
    pop(g, "pop", text_from_str(g, "t", "@msg.ReturnValue"))
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@entry.name"}); g.branch("bw", "@iw.yes")
    g.n("to", "call_self", function="Take Off", inp={"name": "@entry.name"}); g.n("we", "call_self", function="Wear", inp={"name": "@entry.name"})
    g.n("rl", "call_self", function="Rebuild Left"); g.n("rli", "call_self", function="Rebuild List")
    g.chain("entry", "cop", "bcv"); g.chain("bcv:else", "bpg", "btw"); g.chain("bpg:else", "bph", "hc"); g.chain("bph:else", "bpl", "lc")
    g.n("ph", "call_self", function="Push History")
    g.chain("bpl:else", "bo", "ph", "bw", "to", "rl", "rli"); g.chain("bw:else", "we", "rl"); g.chain("bo:else", "pop")
    return fn("On Item Clicked", [param("name", "name")], graph=g)


def menu_row(g, i, action, caption_pin):
    """Create context menu row i; returns the exec chain [create, set manager, init, add]."""
    rw = create_widget(g, "mr%d" % i, W_ROW); set_manager(g, "ms%d" % i, W_ROW, rw)
    g.call("mi%d" % i, W_ROW, "Init", inp={"self": rw, "action": action, "caption": caption_pin})
    g.get("mg%d" % i, "Menu"); g.call("ma%d" % i, W_MENU, "Add Row", inp={"self": "@mg%d.Menu" % i, "widget": rw})
    return ["mr%d_cr" % i, "ms%d" % i, "mi%d" % i, "ma%d" % i]


def f_on_item_context():
    g = G()
    g.set("sci", "ContextItem", inp={"ContextItem": "@entry.name"})
    g.get("gpg0", "Page"); g.n("cop", "call_self", function="Content Open", inp={"page": "@gpg0.Page"}); g.branch("bcv", "@cop.yes")   # content view: own menu
    g.n("occ", "call_self", function="On Content Item Context", inp={"name": "@entry.name"})
    g.get("gpg", "Page"); g.call("isbag", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Bag"}); g.branch("bpg", "@isbag.ReturnValue")
    g.n("obc", "call_self", function="On Bag Item Context", inp={"name": "@entry.name"})
    g.get("gpg2", "Page"); g.call("iscl", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg2.Page", "B": "Clothes"}); g.branch("bpc", "@iscl.ReturnValue")
    g.get("gpg3", "Page"); g.call("ish", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg3.Page", "B": "Hair"}); g.branch("bph", "@ish.ReturnValue")
    g.n("ohc", "call_self", function="On Hair Context", inp={"name": "@entry.name"})
    g.get("glc", "LookCat"); g.call("isp", K_MATH, "EqualEqual_NameName", inp={"A": "@glc.LookCat", "B": "Presets"})
    g.get("gpg4", "Page"); g.call("isl", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg4.Page", "B": "Look"}); g.call("andp", K_MATH, "BooleanAND", inp={"A": "@isl.ReturnValue", "B": "@isp.ReturnValue"}); g.branch("bpp", "@andp.ReturnValue")
    g.n("pix", "call_self", function="Preset Index", inp={"name": "@entry.name"}); g.n("opc", "call_self", function="On Preset Context", inp={"index": "@pix.index"})
    g.get("gm", "Menu"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gm.Menu"}); g.branch("b", "@iv.ReturnValue")
    mw = create_widget(g, "cm", W_MENU); g.set("sm", "Menu", inp={"Menu": mw}); set_manager(g, "smm", W_MENU, mw)
    g.get("gm2", "Menu"); g.call("clr", W_MENU, "Clear Rows", inp={"self": "@gm2.Menu"})
    # row: favourite
    g.n("isf", "call_self", function="Is Favorite", inp={"name": "@entry.name"})
    g.call("fs", K_MATH, "SelectString", inp={"A": ts(g, "fr", "Menu_FavRemove"), "B": ts(g, "fa", "Menu_FavAdd"), "bPickA": "@isf.yes"})
    g.call("ft", K_TXT, "Conv_StringToText", inp={"InString": "@fs.ReturnValue"})
    rw = create_widget(g, "cr1", W_ROW); set_manager(g, "sr1", W_ROW, rw)
    g.call("ri1", W_ROW, "Init", inp={"self": rw, "action": "Fav", "caption": "@ft.ReturnValue"})
    g.get("gm3", "Menu"); g.call("ar1", W_MENU, "Add Row", inp={"self": "@gm3.Menu", "widget": rw})
    # row: hide / unhide
    g.n("ihd", "call_self", function="Is Item Hidden", inp={"name": "@entry.name"})
    g.call("hs", K_MATH, "SelectString", inp={"A": ts(g, "hu", "Menu_Unhide"), "B": ts(g, "hh", "Menu_Hide"), "bPickA": "@ihd.yes"})
    g.call("ht", K_TXT, "Conv_StringToText", inp={"InString": "@hs.ReturnValue"})
    hr = menu_row(g, 5, "Hide", "@ht.ReturnValue")
    # row: colour (only if colour-adjustable and worn)
    g.n("fi", "call_self", function="Find Item", inp={"name": "@entry.name"}); g.brk("bi", S_ITEM, "@fi.item")
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@entry.name"})
    g.call("cok", K_MATH, "BooleanAND", inp={"A": "@bi.ColorAdjustable", "B": "@iw.yes"}); g.branch("bc", "@cok.ReturnValue")
    rw2 = create_widget(g, "cr2", W_ROW); set_manager(g, "sr2", W_ROW, rw2)
    g.call("ri2", W_ROW, "Init", inp={"self": rw2, "action": "Color", "caption": tt(g, "ct", "Menu_Color")})
    g.get("gm4", "Menu"); g.call("ar2", W_MENU, "Add Row", inp={"self": "@gm4.Menu", "widget": rw2})
    # row: reset colour (only if a custom colour is stored)
    g.get("gplr", "Player"); g.call("gcr", P_CPB, "Get Clothes Color", inp={"self": "@gplr.Player", "clothes name": "@entry.name"}); g.branch("brc", "@gcr.found")
    rr = menu_row(g, 6, "ClothesResetColor", tt(g, "rct", "Menu_ClothesReset"))
    # row: "Put in backpack" (owned, not yet in the backpack)
    g.n("io", "call_self", function="Is Owned", inp={"name": "@entry.name"}); g.n("ib", "call_self", function="In Bag", inp={"name": "@entry.name"})
    g.call("nib", K_MATH, "Not_PreBool", inp={"A": "@ib.yes"}); g.call("cpb", K_MATH, "BooleanAND", inp={"A": "@io.yes", "B": "@nib.ReturnValue"}); g.branch("bpb", "@cpb.ReturnValue")
    pb = menu_row(g, 4, "PutInBag", tt(g, "pbt", "Menu_PutInBag"))
    # row: cancel
    rw3 = create_widget(g, "cr3", W_ROW); set_manager(g, "sr3", W_ROW, rw3)
    g.call("ri3", W_ROW, "Init", inp={"self": rw3, "action": "Cancel", "caption": tt(g, "xt", "Menu_Cancel")})
    g.get("gm5", "Menu"); g.call("ar3", W_MENU, "Add Row", inp={"self": "@gm5.Menu", "widget": rw3})
    # show at the mouse position
    g.get("gm6", "Menu"); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@gm6.Menu", "ZOrder": "110"})
    g.call("mp", "/Script/UMG.WidgetLayoutLibrary", "GetMousePositionOnViewport")
    g.get("gm7", "Menu"); g.call("spv", E_USERWIDGET, "SetPositionInViewport", inp={"self": "@gm7.Menu", "Position": "@mp.ReturnValue", "bRemoveDPIScale": "false"})
    g.chain("entry", "sci", "cop", "bcv", "occ"); g.chain("bcv:else", "bpg", "obc"); g.chain("bpg:else", "bpc", "b", "clr"); g.chain("b:else", "cm_cr", "sm", "smm", "clr")
    g.chain("bpc:else", "bph", "ohc"); g.chain("bph:else", "bpp", "pix", "opc")
    g.chain("clr", "cr1_cr", "sr1", "ri1", "ar1", *hr, "fi", "bc", "cr2_cr", "sr2", "ri2", "ar2", "gcr", "brc", *rr, "ib", "bpb", *pb, "cr3_cr"); g.chain("bc:else", "ib"); g.chain("brc:else", "ib"); g.chain("bpb:else", "cr3_cr")
    g.chain("cr3_cr", "sr3", "ri3", "ar3", "atv", "mp", "spv")
    return fn("On Item Context", [param("name", "name")], graph=g)


def simple_menu(name, rows, pre=None):
    """Context menu with fixed rows [(action, caption)]; pre(g) may create nodes and returns exec ids that run before the menu."""
    g = G(); head = ["entry"] + (pre(g) if pre else [])
    g.get("gm", "Menu"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gm.Menu"}); g.branch("b", "@iv.ReturnValue")
    mw = create_widget(g, "cm", W_MENU); g.set("sm", "Menu", inp={"Menu": mw}); set_manager(g, "smm", W_MENU, mw)
    g.get("gm2", "Menu"); g.call("clr", W_MENU, "Clear Rows", inp={"self": "@gm2.Menu"})
    tail = ["clr"]
    for i, (action, cap) in enumerate(rows):
        tail += menu_row(g, i, action, tt(g, "t%d" % i, cap))   # cap = key of the Strings table
    g.get("gm6", "Menu"); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@gm6.Menu", "ZOrder": "110"})
    g.call("mp", "/Script/UMG.WidgetLayoutLibrary", "GetMousePositionOnViewport")
    g.get("gm7", "Menu"); g.call("spv", E_USERWIDGET, "SetPositionInViewport", inp={"self": "@gm7.Menu", "Position": "@mp.ReturnValue", "bRemoveDPIScale": "false"})
    g.chain(*head, "b", "clr"); g.chain("b:else", "cm_cr", "sm", "smm", "clr"); g.chain(*tail, "atv", "mp", "spv")
    return g


def f_on_hair_context():
    g = simple_menu("On Hair Context", [("HairResetColor", "Menu_HairReset"), ("Cancel", "Menu_Cancel")])
    return fn("On Hair Context", [param("name", "name")], graph=g)


def f_hair_reset_color():
    """Set and save the factory colour of the hairstyle (HairstyleStruct.Color)."""
    g = G()
    g.n("row", "get_row", table=P_HAIR_T, inp={"RowName": "@entry.name"}, miss="ignore"); g.brk("br", P_HAIR_S, "@row.OutRow")   # unknown hairstyle -> nothing to reset
    g.call("c2l", K_MATH, "Conv_ColorToLinearColor", inp={"InColor": "@br.Color"}); g.set("sc", "TmpColor", inp={"TmpColor": "@c2l.ReturnValue"})
    g.get("gpl", "Player"); g.get("gtc", "TmpColor"); g.call("ch", P_JODI, "Change Hairstyle Color", inp={"self": "@gpl.Player", "color": "@gtc.TmpColor"})
    gi = game_instance(g, "gi"); g.get("gpl2", "Player"); g.call("sv", P_GI, "Save Hair Color Data", inp={"self": gi, "player": "@gpl2.Player"})
    g.chain("entry", "row", "sc", "ch", "sv")
    return fn("Hair Reset Color", [param("name", "name")], graph=g)


def f_clothes_reset_color():
    """Back to the factory colour of the piece: the game's Restore Clothes Color drops the map entry and calls Clothes_Comp.Restore Color."""
    g = G()
    g.get("gpl", "Player"); g.call("rc", P_CPB, "Restore Clothes Color", inp={"self": "@gpl.Player", "clothes": "@entry.name"})
    g.chain("entry", "rc")
    return fn("Clothes Reset Color", [param("name", "name")], graph=g)


def f_apply_nude():
    """Set the game rule 'Allow Naked' (TKA_GameState_Base) from our option; otherwise check clothes covering puts underwear back on."""
    g = G()
    g.call("gs", K_GS, "GetGameState"); g.cast("cs", P_GS2, "@gs.ReturnValue"); g.get("gan", "AllowNude")
    g.call("sn", P_GS2, "Set Nude Allowed", inp={"self": "@cs.AsTKA Game State", "allow": "@gan.AllowNude"})
    g.chain("entry", "sn"); return fn("Apply Nude", graph=g)


def f_fix_loaded_underwear():
    """Via timer after BeginPlay: on load, check clothes covering (Allow Naked still false) re-adds Bra/Briefs.
    With the option active: take off pieces of type Bra/Briefs that are worn but not listed in Player_Save.Wear Clothes (slot TKAPlayer)."""
    g = G()
    g.get("gan", "AllowNude"); g.get("gpl", "Player"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gpl.Player"})
    g.call("and", K_MATH, "BooleanAND", inp={"A": "@gan.AllowNude", "B": "@iv.ReturnValue"}); g.branch("b", "@and.ReturnValue")
    g.call("ex", K_GS, "DoesSaveGameExist", inp={"SlotName": "TKAPlayer", "UserIndex": "0"}); g.branch("be", "@ex.ReturnValue")
    g.call("ld", K_GS, "LoadGameFromSlot", inp={"SlotName": "TKAPlayer", "UserIndex": "0"}); g.cast("cs", P_PSAVE, "@ld.ReturnValue")
    g.call("csv", K_SYS, "IsValid", inp={"Object": "@cs.AsPlayer_Save"}); g.branch("bcs", "@csv.ReturnValue")   # foreign/corrupt slot content -> leave the underwear alone
    g.get("gwc", "Wear Clothes", cls=P_PSAVE); g.link("cs.AsPlayer_Save", "gwc.self"); g.set("sn", "TmpNames3", inp={"TmpNames3": "@gwc.Wear Clothes"})
    g.n("rs", "call_self", function="Refresh State")
    g.chain("entry", "b", "ex", "be", "ld", "bcs", "sn", "rs"); tail = ["rs"]   # DoesSaveGameExist/LoadGameFromSlot are exec nodes
    for t in ("Bra", "Briefs"):
        g.n("w" + t, "call_self", function="Worn In Slot", inp={"slot": t})
        g.call("ne" + t, K_MATH, "NotEqual_NameName", inp={"A": "@w%s.name" % t, "B": "None"})
        g.get("gn" + t, "TmpNames3"); g.call("ct" + t, K_ARR, "Array_Contains", inp={"TargetArray": "@gn%s.TmpNames3" % t, "ItemToFind": "@w%s.name" % t})
        g.call("nc" + t, K_MATH, "Not_PreBool", inp={"A": "@ct%s.ReturnValue" % t}); g.call("a" + t, K_MATH, "BooleanAND", inp={"A": "@ne%s.ReturnValue" % t, "B": "@nc%s.ReturnValue" % t}); g.branch("b" + t, "@a%s.ReturnValue" % t)
        g.get("gp" + t, "Player"); g.call("to" + t, P_CPB, "Take off this clothes", inp={"self": "@gp%s.Player" % t, "clothes name": "@w%s.name" % t})
        for src in tail: g.chain(src, "w" + t)
        g.chain("w" + t, "b" + t, "to" + t); tail = ["to" + t, "b%s:else" % t]   # both branches merge in the next node
    g.n("rs2", "call_self", function="Refresh State")
    for src in tail: g.chain(src, "rs2")
    return fn("Fix Loaded Underwear", graph=g)


# ---------------- Options ----------------
TOGGLE_KEYS = ["B", "G", "H", "I", "J", "K", "N", "O", "P", "U", "Y", "Z"]   # panel key candidates (default B): letters the vanilla DefaultInput.ini does not bind (L = debug); matched by an AnyKey event, nothing is consumed
TILE_MIN, TILE_MAX = 0.6, 2.0    # tile size 60..200 %
FOV_MIN, FOV_MAX = 0.3, 1.0      # camera FOV scale 30..100 %
DIST_MIN, DIST_MAX = 0.0, 3.0    # camera distance scale 0..300 %
GROUPLEN_MIN, GROUPLEN_MAX = 3, 20   # chip caption length; slider step 18 (past GROUPLEN_MAX) = unlimited (GroupLen 0)
GROUPLEN_STEPS = GROUPLEN_MAX - GROUPLEN_MIN + 1
from gen_widgets import SUBTABS_MAX_H, SUBTABS_MAX_H_MAX
CHIPH_STEP = 4   # chip area height snaps to 4 units; ChipH 0 = default SUBTABS_MAX_H


def chip_h(g, id):
    """ChipH (0 = default) -> effective height as int pin."""
    g.get(id + "_v", "ChipH"); g.call(id + "_z", K_MATH, "EqualEqual_IntInt", inp={"A": "@%s_v.ChipH" % id, "B": "0"})
    g.call(id + "_s", K_MATH, "SelectInt", inp={"A": str(SUBTABS_MAX_H), "B": "@%s_v.ChipH" % id, "bPickA": "@%s_z.ReturnValue" % id}); return "@%s_s.ReturnValue" % id


def opt_texts(g):
    """Display texts for ScrollMult ("4.0x") and TileScale ("100 %")"""
    g.get("ox_sm", "ScrollMult"); g.call("ox_f", K_STR, "Conv_FloatToString", inp={"InFloat": "@ox_sm.ScrollMult"}); g.call("ox_c", K_STR, "Concat_StrStr", inp={"A": "@ox_f.ReturnValue", "B": "x"}); g.call("ox_t", K_TXT, "Conv_StringToText", inp={"InString": "@ox_c.ReturnValue"})
    g.get("ox_ts", "TileScale"); g.call("ox_m", K_MATH, "Multiply_FloatFloat", inp={"A": "@ox_ts.TileScale", "B": "100.0"}); g.call("ox_r", K_MATH, "Round", inp={"A": "@ox_m.ReturnValue"})
    g.call("ox_i", K_STR, "Conv_IntToString", inp={"InInt": "@ox_r.ReturnValue"}); g.call("ox_c2", K_STR, "Concat_StrStr", inp={"A": "@ox_i.ReturnValue", "B": " %"}); g.call("ox_t2", K_TXT, "Conv_StringToText", inp={"InString": "@ox_c2.ReturnValue"})
    def pct(var, id):
        g.get(id + "_v", var); g.call(id + "_m", K_MATH, "Multiply_FloatFloat", inp={"A": "@%s_v.%s" % (id, var), "B": "100.0"}); g.call(id + "_r", K_MATH, "Round", inp={"A": "@%s_m.ReturnValue" % id})
        g.call(id + "_i", K_STR, "Conv_IntToString", inp={"InInt": "@%s_r.ReturnValue" % id}); g.call(id + "_c", K_STR, "Concat_StrStr", inp={"A": "@%s_i.ReturnValue" % id, "B": " %"}); g.call(id + "_t", K_TXT, "Conv_StringToText", inp={"InString": "@%s_c.ReturnValue" % id})
        return "@%s_t.ReturnValue" % id
    # group name length: "12" or "unlimited"
    g.get("ox_gl", "GroupLen"); g.call("ox_gli", K_STR, "Conv_IntToString", inp={"InInt": "@ox_gl.GroupLen"})
    g.get("ox_gl2", "GroupLen"); g.call("ox_glz", K_MATH, "EqualEqual_IntInt", inp={"A": "@ox_gl2.GroupLen", "B": "0"})
    g.call("ox_gls", K_MATH, "SelectString", inp={"A": ts(g, "ox_glu", "Opt_Unlimited"), "B": "@ox_gli.ReturnValue", "bPickA": "@ox_glz.ReturnValue"})
    g.call("ox_glt", K_TXT, "Conv_StringToText", inp={"InString": "@ox_gls.ReturnValue"})
    g.call("ox_cht", K_TXT, "Conv_IntToText", inp={"Value": chip_h(g, "ox_ch")})
    return "@ox_t.ReturnValue", "@ox_t2.ReturnValue", pct("CamFov", "ox_f2"), pct("CamDist", "ox_d2"), pct("BgAlpha", "ox_ba"), pct("TileAlpha", "ox_ta"), "@ox_glt.ReturnValue", "@ox_cht.ReturnValue"


def f_rebuild_options():
    """Set the sliders from ScrollMult (1..10) / TileScale (TILE_MIN..TILE_MAX) / camera / opacities; layout, language, key chips; theme swatches + reset link."""
    g = G()
    g.get("gsm", "ScrollMult"); g.call("s1", K_MATH, "Subtract_FloatFloat", inp={"A": "@gsm.ScrollMult", "B": "1.0"}); g.call("s2", K_MATH, "Divide_FloatFloat", inp={"A": "@s1.ReturnValue", "B": "9.0"})
    g.get("gts", "TileScale"); g.call("t0", K_MATH, "Subtract_FloatFloat", inp={"A": "@gts.TileScale", "B": str(TILE_MIN)}); g.call("t1", K_MATH, "Divide_FloatFloat", inp={"A": "@t0.ReturnValue", "B": str(TILE_MAX - TILE_MIN)})
    # FOV FOV_MIN..FOV_MAX -> slider (x-min)/(max-min); distance likewise
    g.get("gcf", "CamFov"); g.call("f1", K_MATH, "Subtract_FloatFloat", inp={"A": "@gcf.CamFov", "B": str(FOV_MIN)}); g.call("f2", K_MATH, "Divide_FloatFloat", inp={"A": "@f1.ReturnValue", "B": str(FOV_MAX - FOV_MIN)})
    g.get("gcd", "CamDist"); g.call("d1", K_MATH, "Subtract_FloatFloat", inp={"A": "@gcd.CamDist", "B": str(DIST_MIN)}); g.call("d2", K_MATH, "Divide_FloatFloat", inp={"A": "@d1.ReturnValue", "B": str(DIST_MAX - DIST_MIN)})
    g.get("gba", "BgAlpha"); g.get("gta", "TileAlpha")
    # group name length: 0 (unlimited) -> slider 1.0, else (len - min) / steps
    g.get("ggl", "GroupLen"); g.call("gl0", K_MATH, "EqualEqual_IntInt", inp={"A": "@ggl.GroupLen", "B": "0"})
    g.call("gl1", K_MATH, "Subtract_IntInt", inp={"A": "@ggl.GroupLen", "B": str(GROUPLEN_MIN)}); g.call("gl2", K_MATH, "Conv_IntToFloat", inp={"InInt": "@gl1.ReturnValue"})
    g.call("gl3", K_MATH, "Divide_FloatFloat", inp={"A": "@gl2.ReturnValue", "B": str(float(GROUPLEN_STEPS))})
    g.call("gl4", K_MATH, "SelectFloat", inp={"A": "1.0", "B": "@gl3.ReturnValue", "bPickA": "@gl0.ReturnValue"})
    # chip area height SUBTABS_MAX_H..SUBTABS_MAX_H_MAX -> slider
    g.call("ch1", K_MATH, "Subtract_IntInt", inp={"A": chip_h(g, "rch"), "B": str(SUBTABS_MAX_H)}); g.call("ch2", K_MATH, "Conv_IntToFloat", inp={"InInt": "@ch1.ReturnValue"})
    g.call("ch3", K_MATH, "Divide_FloatFloat", inp={"A": "@ch2.ReturnValue", "B": str(float(SUBTABS_MAX_H_MAX - SUBTABS_MAX_H))})
    g.set("os", "OptScroll", inp={"OptScroll": "@s2.ReturnValue"}); g.set("oc", "OptScale", inp={"OptScale": "@t1.ReturnValue"}); g.set("ogl", "OptGroupLen", inp={"OptGroupLen": "@gl4.ReturnValue"}); g.set("och", "OptChipH", inp={"OptChipH": "@ch3.ReturnValue"})
    g.set("of", "OptFov", inp={"OptFov": "@f2.ReturnValue"}); g.set("od", "OptDist", inp={"OptDist": "@d2.ReturnValue"})
    g.set("oba", "OptBgAlpha", inp={"OptBgAlpha": "@gba.BgAlpha"}); g.set("ota", "OptTileAlpha", inp={"OptTileAlpha": "@gta.TileAlpha"})
    t1, t2, t3, t4, t5, t6, t7, t8 = opt_texts(g)
    g.get("gp", "Panel"); g.call("sv", W_PANEL, "Set Option Values", inp={"self": "@gp.Panel", "scroll": "@s2.ReturnValue", "scale": "@t1.ReturnValue", "fov": "@f2.ReturnValue", "dist": "@d2.ReturnValue",
                                                                            "bgalpha": "@gba.BgAlpha", "tilealpha": "@gta.TileAlpha", "grouplen": "@gl4.ReturnValue", "chiph": "@ch3.ReturnValue",
                                                                            "scroll text": t1, "scale text": t2, "fov text": t3, "dist text": t4, "bgalpha text": t5, "tilealpha text": t6, "grouplen text": t7, "chiph text": t8})
    g.get("gp2", "Panel"); g.get("gun", "Unlimited"); g.get("gpn", "PanToSlot"); g.get("gan", "AllowNude"); g.call("su", W_PANEL, "Set Option Checks", inp={"self": "@gp2.Panel", "unlimited": "@gun.Unlimited", "pan": "@gpn.PanToSlot", "nude": "@gan.AllowNude"})
    # layout chips (W_SubTab: click -> Select SubTab -> Select Layout), display order by size, stable indices
    g.get("gp3", "Panel"); g.call("cl", W_PANEL, "Clear Layout Chips", inp={"self": "@gp3.Panel"}); tail = ["entry", "os", "oc", "of", "od", "oba", "ota", "ogl", "och", "sv", "su", "cl"]
    for i, (idx, key) in enumerate(LAYOUTS):
        cw = create_widget(g, "cc%d" % i, W_SUB); set_manager(g, "cm%d" % i, W_SUB, cw)
        g.get("glf%d" % i, "LeftFree"); g.call("eq%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": "@glf%d.LeftFree" % i, "B": str(idx)})
        g.call("ci%d" % i, W_SUB, "Init", inp={"self": cw, "group": "Layout%d" % idx, "caption": tt(g, "ct%d" % i, key), "selected": "@eq%d.ReturnValue" % i})
        g.get("gpc%d" % i, "Panel"); g.call("ac%d" % i, W_PANEL, "Add Layout Chip", inp={"self": "@gpc%d.Panel" % i, "widget": cw})
        tail += ["cc%d_cr" % i, "cm%d" % i, "ci%d" % i, "ac%d" % i, hslot_pad(g, "pd%d" % i, cw, 8)]
    # language chips (Auto / English / Deutsch / 中文 / Русский / Español), active = LangChoice (chip index, Lang = LangChoice - 1)
    g.get("gpl9", "Panel"); g.call("cll", W_PANEL, "Clear Lang Chips", inp={"self": "@gpl9.Panel"}); tail.append("cll")
    for i, key in enumerate(["Chip_LangAuto"] + ["Chip_Lang" + l.capitalize() for l in LANGS]):
        lw = create_widget(g, "lc%d" % i, W_SUB); set_manager(g, "lm%d" % i, W_SUB, lw)
        g.get("glc%d" % i, "LangChoice"); g.call("leq%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": "@glc%d.LangChoice" % i, "B": str(i)})
        g.call("lci%d" % i, W_SUB, "Init", inp={"self": lw, "group": "Lang%d" % i, "caption": tt(g, "lt%d" % i, key), "selected": "@leq%d.ReturnValue" % i})
        g.get("gpq%d" % i, "Panel"); g.call("la%d" % i, W_PANEL, "Add Lang Chip", inp={"self": "@gpq%d.Panel" % i, "widget": lw})
        tail += ["lc%d_cr" % i, "lm%d" % i, "lci%d" % i, "la%d" % i, hslot_pad(g, "lp%d" % i, lw, 8)]
    # panel key chips (group "Key<X>"), active = ToggleKey
    g.get("gpk", "Panel"); g.call("clk", W_PANEL, "Clear Key Chips", inp={"self": "@gpk.Panel"}); tail.append("clk")
    for i, k in enumerate(TOGGLE_KEYS):
        kw = create_widget(g, "kc%d" % i, W_SUB); set_manager(g, "km%d" % i, W_SUB, kw)
        g.get("gtk%d" % i, "ToggleKey"); g.call("keq%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@gtk%d.ToggleKey" % i, "B": k})
        g.call("kt%d" % i, K_TXT, "Conv_StringToText", inp={"InString": k})
        g.call("kci%d" % i, W_SUB, "Init", inp={"self": kw, "group": "Key" + k, "caption": "@kt%d.ReturnValue" % i, "selected": "@keq%d.ReturnValue" % i})
        g.get("gpx%d" % i, "Panel"); g.call("ka%d" % i, W_PANEL, "Add Key Chip", inp={"self": "@gpx%d.Panel" % i, "widget": kw})
        tail += ["kc%d_cr" % i, "km%d" % i, "kci%d" % i, "ka%d" % i, hslot_pad(g, "kp%d" % i, kw, 8)]
    # theme swatches (W_ColorSwatch per base colour, column-wise in THEME_COLS columns) + reset link
    ROWS_PER_COL = -(-len(THEME) // THEME_COLS)
    g.get("gpt", "Panel"); g.call("cts", W_PANEL, "Clear Theme Swatches", inp={"self": "@gpt.Panel"}); tail.append("cts")
    for i, (key, _, cap) in enumerate(THEME):
        sw = create_widget(g, "sw%d" % i, W_SWATCH); set_manager(g, "swm%d" % i, W_SWATCH, sw)
        g.call("swi%d" % i, W_SWATCH, "Init", inp={"self": sw, "key": key, "caption": tt(g, "swt%d" % i, cap)})
        g.get("gps%d" % i, "Panel"); g.call("swa%d" % i, W_PANEL, "Add Theme Swatch", inp={"self": "@gps%d.Panel" % i, "widget": sw, "column": str(i // ROWS_PER_COL)})
        tail += ["sw%d_cr" % i, "swm%d" % i, "swi%d" % i, "swa%d" % i]
    g.get("gptl", "Panel"); g.call("ctl", W_PANEL, "Clear Theme Links", inp={"self": "@gptl.Panel"}); tail.append("ctl")
    rw = create_widget(g, "rw", W_TXT); set_manager(g, "rwm", W_TXT, rw)
    g.call("rwi", W_TXT, "Init", inp={"self": rw, "action": "ThemeReset", "caption": tt(g, "rwt", "Btn_ThemeReset")})
    g.get("gpr", "Panel"); g.call("rwa", W_PANEL, "Add Theme Link", inp={"self": "@gpr.Panel", "widget": rw}); tail += ["rw_cr", "rwm", "rwi", "rwa"]
    g.chain(*tail); return fn("Rebuild Options", graph=g)


def f_select_layout():
    g = G(); tail = ["entry"]
    for i in range(5):
        g.call("e%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Layout%d" % i}); g.branch("b%d" % i, "@e%d.ReturnValue" % i)
        g.set("s%d" % i, "LeftFree", inp={"LeftFree": str(i)}); g.chain(*tail, "b%d" % i, "s%d" % i); tail = ["b%d:else" % i]
    g.n("ap", "call_self", function="Apply Options"); g.n("ro", "call_self", function="Rebuild Options")
    for i in range(5): g.chain("s%d" % i, "ap")
    g.chain("ap", "ro"); return fn("Select Layout", [param("name", "name")], graph=g)


def f_apply_options():
    g = G(); g.get("gp", "Panel"); g.get("gsm", "ScrollMult"); g.call("ssm", W_PANEL, "Set Scroll Mult", inp={"self": "@gp.Panel", "mult": "@gsm.ScrollMult"})
    g.call("chf", K_MATH, "Conv_IntToFloat", inp={"InInt": chip_h(g, "ach")}); g.get("gp4", "Panel"); g.call("sth", W_PANEL, "Set SubTabs Height", inp={"self": "@gp4.Panel", "height": "@chf.ReturnValue"})
    g.get("glf", "LeftFree"); g.n("lf", "call_self", function="Layout Fraction", inp={"index": "@glf.LeftFree"})
    g.get("gp2", "Panel"); g.call("slf", W_PANEL, "Set Left Free", inp={"self": "@gp2.Panel", "fraction": "@lf.fraction"})
    # camera: Jodi in the centre of the free area (NDC x = -(1 - fraction): third -> 2/3, half -> 1/2, quarter -> 3/4, fifth -> 4/5); none -> 0
    g.call("k1", K_MATH, "Subtract_FloatFloat", inp={"A": "1.0", "B": "@lf.fraction"}); g.call("gt0", K_MATH, "Greater_FloatFloat", inp={"A": "@lf.fraction", "B": "0.0"})
    g.call("k2", K_MATH, "SelectFloat", inp={"A": "@k1.ReturnValue", "B": "0.0", "bPickA": "@gt0.ReturnValue"})
    g.set("svs", "ViewShift", inp={"ViewShift": "@k2.ReturnValue"}); g.n("svc", "call_self", function="Set View Shift")
    g.chain("entry", "ssm", "sth", "lf", "slf", "svs", "svc"); return fn("Apply Options", graph=g)


def f_set_view_shift():
    """Pass ViewShift on to the (replaced) PlayerCameraManager; without the hook pak nothing happens."""
    g = G(); g.get("gpc", "PC"); g.get("gcm", "PlayerCameraManager", cls=E_PC); g.link("gpc.PC", "gcm.self")
    g.cast("ch", P_HOOK, "@gcm.PlayerCameraManager", pure=False, miss="ignore")   # vanilla camera manager (hook pak missing) -> nothing to pass on
    g.get("gvs", "ViewShift"); g.n("sv", "set", var="ViewShift", cls=P_HOOK, inp={"self": "@ch.AsTKA Player Camera Manager", "ViewShift": "@gvs.ViewShift"})
    g.get("gcf", "CamFov"); g.n("sf", "set", var="FovScale", cls=P_HOOK, inp={"self": "@ch.AsTKA Player Camera Manager", "FovScale": "@gcf.CamFov"})
    g.get("gcd", "CamDist"); g.n("sd", "set", var="DistScale", cls=P_HOOK, inp={"self": "@ch.AsTKA Player Camera Manager", "DistScale": "@gcd.CamDist"})
    g.get("gfo", "FocusOn"); g.n("sfo", "set", var="FocusOn", cls=P_HOOK, inp={"self": "@ch.AsTKA Player Camera Manager", "FocusOn": "@gfo.FocusOn"})
    g.get("gfz", "FocusZ"); g.n("sfz", "set", var="FocusZ", cls=P_HOOK, inp={"self": "@ch.AsTKA Player Camera Manager", "FocusZ": "@gfz.FocusZ"})
    g.get("gfm", "FocusZoom"); g.n("sfm", "set", var="FocusZoom", cls=P_HOOK, inp={"self": "@ch.AsTKA Player Camera Manager", "FocusZoom": "@gfm.FocusZoom"})
    g.chain("entry", "ch", "sv", "sf", "sd", "sfo", "sfz", "sfm"); return fn("Set View Shift", graph=g)


def f_poll_options():
    g = G()
    g.get("gp", "Panel"); g.call("gv", W_PANEL, "Get Option Values", inp={"self": "@gp.Panel"})
    g.get("cs", "OptScroll"); g.get("cc", "OptScale"); g.get("cf", "OptFov"); g.get("cd", "OptDist"); g.get("cba", "OptBgAlpha"); g.get("cta", "OptTileAlpha"); g.get("cgl", "OptGroupLen"); g.get("cch", "OptChipH")
    g.call("ngl", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.grouplen", "B": "@cgl.OptGroupLen", "ErrorTolerance": "0.0001"})
    g.call("nch", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.chiph", "B": "@cch.OptChipH", "ErrorTolerance": "0.0001"})
    g.call("ns", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.scroll", "B": "@cs.OptScroll", "ErrorTolerance": "0.0001"})
    g.call("nc", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.scale", "B": "@cc.OptScale", "ErrorTolerance": "0.0001"})
    g.call("nf", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.fov", "B": "@cf.OptFov", "ErrorTolerance": "0.0001"})
    g.call("nd", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.dist", "B": "@cd.OptDist", "ErrorTolerance": "0.0001"})
    g.call("nba", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.bgalpha", "B": "@cba.OptBgAlpha", "ErrorTolerance": "0.0001"})
    g.call("nta", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.tilealpha", "B": "@cta.OptTileAlpha", "ErrorTolerance": "0.0001"})
    g.call("a0", K_MATH, "BooleanAND", inp={"A": "@ns.ReturnValue", "B": "@nc.ReturnValue"}); g.call("a1", K_MATH, "BooleanAND", inp={"A": "@a0.ReturnValue", "B": "@nf.ReturnValue"})
    g.call("a2", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@nd.ReturnValue"}); g.call("a3", K_MATH, "BooleanAND", inp={"A": "@a2.ReturnValue", "B": "@nba.ReturnValue"})
    g.call("a4", K_MATH, "BooleanAND", inp={"A": "@a3.ReturnValue", "B": "@nta.ReturnValue"})
    g.call("a5", K_MATH, "BooleanAND", inp={"A": "@a4.ReturnValue", "B": "@ngl.ReturnValue"})
    g.call("a", K_MATH, "BooleanAND", inp={"A": "@a5.ReturnValue", "B": "@nch.ReturnValue"}); g.branch("bsame", "@a.ReturnValue")
    g.set("sun", "Unlimited", inp={"Unlimited": "@gv.unlimited"})
    g.get("gpn", "PanToSlot"); g.call("pne", K_MATH, "NotEqual_BoolBool", inp={"A": "@gv.pan", "B": "@gpn.PanToSlot"}); g.branch("bpn", "@pne.ReturnValue")
    g.set("spn", "PanToSlot", inp={"PanToSlot": "@gv.pan"}); g.n("upf", "call_self", function="Update Focus")
    g.get("gan", "AllowNude"); g.call("nne", K_MATH, "NotEqual_BoolBool", inp={"A": "@gv.nude", "B": "@gan.AllowNude"}); g.branch("bnn", "@nne.ReturnValue")
    g.set("san", "AllowNude", inp={"AllowNude": "@gv.nude"}); g.n("apn", "call_self", function="Apply Nude"); g.n("svn", "call_self", function="Save Settings")
    g.set("os", "OptScroll", inp={"OptScroll": "@gv.scroll"}); g.set("oc", "OptScale", inp={"OptScale": "@gv.scale"}); g.set("of", "OptFov", inp={"OptFov": "@gv.fov"}); g.set("od", "OptDist", inp={"OptDist": "@gv.dist"})
    g.set("oba", "OptBgAlpha", inp={"OptBgAlpha": "@gv.bgalpha"}); g.set("ota", "OptTileAlpha", inp={"OptTileAlpha": "@gv.tilealpha"}); g.set("ogl", "OptGroupLen", inp={"OptGroupLen": "@gv.grouplen"}); g.set("och", "OptChipH", inp={"OptChipH": "@gv.chiph"})
    # chip area height: min + Round(slider * span / step) * step
    g.call("cha", K_MATH, "Multiply_FloatFloat", inp={"A": "@gv.chiph", "B": str(float(SUBTABS_MAX_H_MAX - SUBTABS_MAX_H) / CHIPH_STEP)}); g.call("chb", K_MATH, "Round", inp={"A": "@cha.ReturnValue"})
    g.call("chc", K_MATH, "Multiply_IntInt", inp={"A": "@chb.ReturnValue", "B": str(CHIPH_STEP)}); g.call("chd", K_MATH, "Add_IntInt", inp={"A": "@chc.ReturnValue", "B": str(SUBTABS_MAX_H)})
    g.set("sch", "ChipH", inp={"ChipH": "@chd.ReturnValue"})
    # group name length: step = Round(slider * steps); step >= steps -> unlimited (0), else min + step
    g.call("gla", K_MATH, "Multiply_FloatFloat", inp={"A": "@gv.grouplen", "B": str(float(GROUPLEN_STEPS))}); g.call("glb", K_MATH, "Round", inp={"A": "@gla.ReturnValue"})
    g.call("glc", K_MATH, "GreaterEqual_IntInt", inp={"A": "@glb.ReturnValue", "B": str(GROUPLEN_STEPS)}); g.call("gld", K_MATH, "Add_IntInt", inp={"A": "@glb.ReturnValue", "B": str(GROUPLEN_MIN)})
    g.call("gle", K_MATH, "SelectInt", inp={"A": "0", "B": "@gld.ReturnValue", "bPickA": "@glc.ReturnValue"}); g.set("sgl", "GroupLen", inp={"GroupLen": "@gle.ReturnValue"})
    # FOV FOV_MIN..FOV_MAX and distance DIST_MIN..DIST_MAX in steps of 5 %; opacities 0..100 % in steps of 5 %
    def snap(id, expr, lo, span):
        g.call(id + "a", K_MATH, "Multiply_FloatFloat", inp={"A": expr, "B": str(span)}); g.call(id + "b", K_MATH, "Add_FloatFloat", inp={"A": "@%sa.ReturnValue" % id, "B": str(lo)})
        g.call(id + "c", K_MATH, "Multiply_FloatFloat", inp={"A": "@%sb.ReturnValue" % id, "B": "20.0"}); g.call(id + "d", K_MATH, "Round", inp={"A": "@%sc.ReturnValue" % id})
        g.call(id + "e", K_MATH, "Conv_IntToFloat", inp={"InInt": "@%sd.ReturnValue" % id}); g.call(id + "f", K_MATH, "Divide_FloatFloat", inp={"A": "@%se.ReturnValue" % id, "B": "20.0"})
        return "@%sf.ReturnValue" % id
    g.set("scf", "CamFov", inp={"CamFov": snap("f", "@gv.fov", FOV_MIN, FOV_MAX - FOV_MIN)}); g.set("scd", "CamDist", inp={"CamDist": snap("d", "@gv.dist", DIST_MIN, DIST_MAX - DIST_MIN)})
    g.set("sba", "BgAlpha", inp={"BgAlpha": snap("ba", "@gv.bgalpha", 0.0, 1.0)}); g.set("sta", "TileAlpha", inp={"TileAlpha": snap("ta", "@gv.tilealpha", 0.0, 1.0)})
    g.call("m1", K_MATH, "Multiply_FloatFloat", inp={"A": "@gv.scroll", "B": "9.0"}); g.call("m2", K_MATH, "Add_FloatFloat", inp={"A": "@m1.ReturnValue", "B": "1.0"})
    g.call("m3", K_MATH, "Multiply_FloatFloat", inp={"A": "@m2.ReturnValue", "B": "2.0"}); g.call("m4", K_MATH, "Round", inp={"A": "@m3.ReturnValue"}); g.call("m5", K_MATH, "Conv_IntToFloat", inp={"InInt": "@m4.ReturnValue"})
    g.call("m6", K_MATH, "Divide_FloatFloat", inp={"A": "@m5.ReturnValue", "B": "2.0"})     # in steps of 0.5
    g.set("ssm", "ScrollMult", inp={"ScrollMult": "@m6.ReturnValue"})
    g.set("sts", "TileScale", inp={"TileScale": snap("t", "@gv.scale", TILE_MIN, TILE_MAX - TILE_MIN)})   # 5 % steps
    g.n("ap", "call_self", function="Apply Options"); g.n("ath", "call_self", function="Apply Theme")
    tx1, tx2, tx3, tx4, tx5, tx6, tx7, tx8 = opt_texts(g)
    g.get("gp2", "Panel"); g.call("sv", W_PANEL, "Set Option Values", inp={"self": "@gp2.Panel", "scroll": "@gv.scroll", "scale": "@gv.scale", "fov": "@gv.fov", "dist": "@gv.dist",
                                                                             "bgalpha": "@gv.bgalpha", "tilealpha": "@gv.tilealpha", "grouplen": "@gv.grouplen", "chiph": "@gv.chiph",
                                                                             "scroll text": tx1, "scale text": tx2, "fov text": tx3, "dist text": tx4, "bgalpha text": tx5, "tilealpha text": tx6, "grouplen text": tx7, "chiph text": tx8})
    g.chain("entry", "gv", "sun", "bpn", "spn", "upf", "bnn"); g.chain("bpn:else", "bnn"); g.chain("bnn", "san", "apn", "svn", "bsame"); g.chain("bnn:else", "bsame")
    g.chain("bsame:else", "os", "oc", "of", "od", "oba", "ota", "ogl", "och", "ssm", "sts", "scf", "scd", "sba", "sta", "sgl", "sch", "ap", "ath", "sv")
    return fn("Poll Options", graph=g)


# ---------------- Status bar / history (undo, redo; 5 steps, clothes + appearance) ----------------
HISTORY_MAX = 5


def f_rebuild_status():
    g = G(); g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Status", inp={"self": "@gp.Panel"}); tail = ["entry", "cl"]
    for i, (action, cap, stack) in enumerate([("Undo", "Rueckgaengig", "UndoStack"), ("Redo", "Wiederherstellen", "RedoStack")]):
        lw = create_widget(g, "l%d" % i, W_TXT); set_manager(g, "m%d" % i, W_TXT, lw)
        g.get("gs%d" % i, stack); g.call("ln%d" % i, K_ARR, "Array_Length", inp={"TargetArray": "@gs%d.%s" % (i, stack)}); g.call("ns%d" % i, K_STR, "Conv_IntToString", inp={"InInt": "@ln%d.ReturnValue" % i})
        g.call("c1%d" % i, K_STR, "Concat_StrStr", inp={"A": "", "B": "@ns%d.ReturnValue" % i}); g.call("c2%d" % i, K_STR, "Concat_StrStr", inp={"A": "@c1%d.ReturnValue" % i, "B": ""})
        g.call("t%d" % i, K_TXT, "Conv_StringToText", inp={"InString": "@c2%d.ReturnValue" % i})
        g.call("i%d" % i, W_TXT, "Init", inp={"self": lw, "action": action, "caption": "@t%d.ReturnValue" % i, "icon": T_UNDO if action == "Undo" else T_REDO})
        g.get("gp%d" % i, "Panel"); g.call("a%d" % i, W_PANEL, "Add Status", inp={"self": "@gp%d.Panel" % i, "widget": lw})
        tail += ["l%d_cr" % i, "m%d" % i, "i%d" % i, "a%d" % i, hslot_pad(g, "sp%d" % i, lw, 14, 14)]
    g.chain(*tail); return fn("Rebuild Status", graph=g)


def f_take_snapshot():
    """Current state: worn clothes (+ colours), makeup map, skin, hairstyle (+ colour), body sliders, body variant."""
    g = G(); g.n("rs", "call_self", function="Refresh State"); md = makeup_data(g, "md")
    g.get("gmd", "Makeup Data", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "gmd.self")
    g.get("gsn", "Skin Name", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "gsn.self")
    g.get("gbs", "Boobs Size", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "gbs.self")
    g.get("gwa", "Waist", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "gwa.self")
    g.get("ghp", "Hip", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "ghp.self")
    g.get("gpl", "Player"); g.call("hn", P_JODI, "Get Hairstyle Name", inp={"self": "@gpl.Player"})
    g.get("gplc", "Player"); g.call("hc", P_JODI, "Get Hairstyle Color", inp={"self": "@gplc.Player"})
    # colours of the worn pieces (only those with a saved colour)
    g.get("gtc", "TmpColors"); g.call("mclr", K_MAP, "Map_Clear", inp={"TargetMap": "@gtc.TmpColors"})
    g.get("gw0", "Worn"); g.foreach("fc", "@gw0.Worn")
    g.get("gpl2", "Player"); g.call("gc", P_CPB, "Get Clothes Color", inp={"self": "@gpl2.Player", "clothes name": "@fc.Array Element"}); g.branch("bf", "@gc.found")
    g.get("gtc2", "TmpColors"); g.call("madd", K_MAP, "Map_Add", inp={"TargetMap": "@gtc2.TmpColors", "Key": "@fc.Array Element", "Value": "@gc.color"})
    g.get("gw", "Worn"); g.get("gtc3", "TmpColors"); g.get("gcb", "CurrentBody")
    g.make("mk", S_SNAP, Worn="@gw.Worn", Makeup="@gmd.Makeup Data", Skin="@gsn.Skin Name", Hair="@hn.name", Colors="@gtc3.TmpColors", HairColor="@hc.color",
           Boobs="@gbs.Boobs Size", Waist="@gwa.Waist", Hip="@ghp.Hip", Body="@gcb.CurrentBody")
    g.set("st", "TmpSnap2", inp={"TmpSnap2": "@mk.S_Snapshot"}); g.get("gt", "TmpSnap2"); g.link("gt.TmpSnap2", "return.snap")
    g.chain("entry", "rs", "md", "mclr", "fc"); g.chain("fc", "gc", "bf", "madd"); g.chain("fc:Completed", "st", "return")
    return fn("Take Snapshot", outputs=[param("snap", "struct:" + S_SNAP)], graph=g)


def f_push_history():
    """Call before a change: push the state onto the undo stack (max. 5), discard redo."""
    g = G(); g.n("ts", "call_self", function="Take Snapshot")
    g.get("gu", "UndoStack"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gu.UndoStack", "NewItem": "@ts.snap"})
    g.get("gu2", "UndoStack"); g.call("ln", K_ARR, "Array_Length", inp={"TargetArray": "@gu2.UndoStack"}); g.call("gt", K_MATH, "Greater_IntInt", inp={"A": "@ln.ReturnValue", "B": str(HISTORY_MAX)}); g.branch("b", "@gt.ReturnValue")
    g.get("gu3", "UndoStack"); g.call("rm", K_ARR, "Array_Remove", inp={"TargetArray": "@gu3.UndoStack", "IndexToRemove": "0"})
    g.get("gr", "RedoStack"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gr.RedoStack"}); g.n("rs", "call_self", function="Rebuild Status")
    g.chain("entry", "ts", "add", "b", "rm", "clr"); g.chain("b:else", "clr"); g.chain("clr", "rs"); return fn("Push History", graph=g)


def f_apply_snapshot():
    """Apply a snapshot: clothes diff (+ colours), hairstyle (if unlocked) + colour, makeup/skin, sliders, body. Missing pieces -> one popup."""
    g = G(); g.brk("bs", S_SNAP, "@entry.snap")
    # clothes: difference to the current state
    g.n("rs", "call_self", function="Refresh State"); g.get("gw", "Worn"); g.set("sn", "TmpNames", inp={"TmpNames": "@gw.Worn"}); g.get("gn", "TmpNames"); g.foreach("f1", "@gn.TmpNames")
    g.call("c1", K_ARR, "Array_Contains", inp={"TargetArray": "@bs.Worn", "ItemToFind": "@f1.Array Element"}); g.branch("b1", "@c1.ReturnValue")
    g.get("gpl", "Player"); g.call("to", P_CPB, "Take off this clothes", inp={"self": "@gpl.Player", "clothes name": "@f1.Array Element"})
    g.get("gts0", "TmpStrings"); g.call("sclr", K_ARR, "Array_Clear", inp={"TargetArray": "@gts0.TmpStrings"})
    g.set("sn2", "TmpNames2", inp={"TmpNames2": "@bs.Worn"}); g.get("gn2", "TmpNames2"); g.foreach("f2", "@gn2.TmpNames2")
    g.n("fi", "call_self", function="Find Item", inp={"name": "@f2.Array Element"}); g.branch("bfi", "@fi.found")
    # only pieces the player still has (wardrobe or backpack): a snapshot may predate losing a backpack piece, and the game's own
    # save keeps whatever is worn - undo/looks must not hand out pieces
    g.n("io2", "call_self", function="Is Owned", inp={"name": "@f2.Array Element"}); g.n("ib2", "call_self", function="In Bag", inp={"name": "@f2.Array Element"})
    g.call("has", K_MATH, "BooleanOR", inp={"A": "@io2.yes", "B": "@ib2.yes"}); g.branch("bhas", "@has.ReturnValue")
    g.get("gpl2", "Player"); g.call("iw", P_CPB, "is clothes wearing", inp={"self": "@gpl2.Player", "clothes name": "@f2.Array Element"}); g.branch("b2", "@iw.yes")
    g.get("gpl3", "Player"); g.call("we", P_CPB, "Wear The Clothes", inp={"self": "@gpl3.Player", "name": "@f2.Array Element", "check covering": "true", "update mask": "true", "ignore compatible": "false"}); g.branch("bwe", "@we.successed")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@f2.Array Element"}); g.get("gts1", "TmpStrings"); g.call("sadd", K_ARR, "Array_Add", inp={"TargetArray": "@gts1.TmpStrings", "NewItem": "@n2s.ReturnValue"})
    # colours
    g.call("ck", K_MAP, "Map_Keys", inp={"TargetMap": "@bs.Colors"}); g.set("sn3", "TmpNames3", inp={"TmpNames3": "@ck.Keys"}); g.get("gn3", "TmpNames3"); g.foreach("f3", "@gn3.TmpNames3")
    g.n("iw3", "call_self", function="Is Worn", inp={"name": "@f3.Array Element"}); g.branch("b3", "@iw3.yes")
    g.call("cf", K_MAP, "Map_Find", inp={"TargetMap": "@bs.Colors", "Key": "@f3.Array Element"})
    g.get("gpl4", "Player"); g.call("fcc", P_CPB, "Find Clothes Component With Name", inp={"self": "@gpl4.Player", "name": "@f3.Array Element"})
    g.call("cv", K_SYS, "IsValid", inp={"Object": "@fcc.clothes comp"}); g.branch("bcv", "@cv.ReturnValue")
    g.call("chg", P_CC, "Change Color", inp={"self": "@fcc.clothes comp", "Color": "@cf.Value"})
    g.get("gpl5", "Player"); g.call("svc", P_CPB, "Save Clothes Color", inp={"self": "@gpl5.Player", "clothes name": "@f3.Array Element", "color": "@cf.Value"})
    # pieces without a snapshot colour -> factory colour (undo of a recolour, redo of a reset)
    g.set("sn4", "TmpNames4", inp={"TmpNames4": "@bs.Worn"}); g.get("gn4", "TmpNames4"); g.foreach("f4", "@gn4.TmpNames4")
    g.call("hcl", K_MAP, "Map_Contains", inp={"TargetMap": "@bs.Colors", "Key": "@f4.Array Element"}); g.branch("b4", "@hcl.ReturnValue")
    g.get("gplR", "Player"); g.call("rsc", P_CPB, "Restore Clothes Color", inp={"self": "@gplR.Player", "clothes": "@f4.Array Element"})
    # appearance: makeup map, skin, sliders
    md = makeup_data(g, "md")
    g.n("smd", "set", var="Makeup Data", cls=P_MAKEUP_SAVE, inp={"self": md, "Makeup Data": "@bs.Makeup"})
    g.n("sbo", "set", var="Boobs Size", cls=P_MAKEUP_SAVE, inp={"self": md, "Boobs Size": "@bs.Boobs"})
    g.n("swa", "set", var="Waist", cls=P_MAKEUP_SAVE, inp={"self": md, "Waist": "@bs.Waist"})
    g.n("shi", "set", var="Hip", cls=P_MAKEUP_SAVE, inp={"self": md, "Hip": "@bs.Hip"})
    g.set("cb2", "BodyBreast", inp={"BodyBreast": "@bs.Boobs"}); g.set("cw2", "BodyWaist", inp={"BodyWaist": "@bs.Waist"}); g.set("sbc", "BoobsChanged", inp={"BoobsChanged": "true"})
    g.get("gsn", "Skin Name", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "gsn.self")
    g.call("eqs", K_MATH, "NotEqual_NameName", inp={"A": "@gsn.Skin Name", "B": "@bs.Skin"}); g.branch("bsk", "@eqs.ReturnValue")
    g.get("gpl6", "Player"); g.call("cs", P_JODI, "Change Skin", inp={"self": "@gpl6.Player", "SkinName": "@bs.Skin"})
    # hairstyle (only if unlocked) + colour
    g.get("gpl7", "Player"); g.call("hn", P_JODI, "Get Hairstyle Name", inp={"self": "@gpl7.Player"})
    g.call("eqh", K_MATH, "NotEqual_NameName", inp={"A": "@hn.name", "B": "@bs.Hair"}); g.branch("bh", "@eqh.ReturnValue")
    g.n("hrow", "get_row", table=P_HAIR_T, inp={"RowName": "@bs.Hair"}); g.brk("hbr", P_HAIR_S, "@hrow.OutRow")
    owned = hair_owned(g, "hown", "@bs.Hair", "@hbr.MirrorID"); g.branch("bho", owned)
    pop(g, "hpop", tt(g, "hlt", "Msg_HairLocked"))
    g.get("gpl8", "Player"); g.call("ch", P_JODI, "Change Hairstyle", inp={"self": "@gpl8.Player", "Hairstyle": "@bs.Hair"})
    g.get("gpl9", "Player"); g.call("chc", P_JODI, "Change Hairstyle Color", inp={"self": "@gpl9.Player", "color": "@bs.HairColor"})
    gi = game_instance(g, "gi"); g.get("gplA", "Player"); g.call("svh", P_GI, "Save Hair Color Data", inp={"self": gi, "player": "@gplA.Player"})
    g.get("gplB", "Player"); g.call("umt", P_JODI, "Update Makeup Texture", inp={"self": "@gplB.Player"})
    g.get("gplC", "Player"); g.call("ues", P_JODI, "Update Eyes Style", inp={"self": "@gplC.Player"})
    g.get("gplD", "Player"); g.call("rcp", P_CPB, "Reset Clothes Physics", inp={"self": "@gplD.Player"})
    g.get("gplE", "Player"); g.call("sa", P_JODI, "Save Appearance", inp={"self": "@gplE.Player"})
    g.set("sd", "MakeupDirty", inp={"MakeupDirty": "true"})
    # body variant
    g.get("gcb", "CurrentBody"); g.call("eqb", K_MATH, "NotEqual_NameName", inp={"A": "@gcb.CurrentBody", "B": "@bs.Body"}); g.branch("bb", "@eqb.ReturnValue")
    g.n("ab", "call_self", function="Apply Body", inp={"name": "@bs.Body"}); g.get("gcb2", "CurrentBody"); g.set("sbv", "BodyVariant", inp={"BodyVariant": "@gcb2.CurrentBody"}); g.n("svs", "call_self", function="Save Settings")
    # missing pieces -> popup
    g.get("gts2", "TmpStrings"); g.call("slen", K_ARR, "Array_Length", inp={"TargetArray": "@gts2.TmpStrings"}); g.call("sgt", K_MATH, "Greater_IntInt", inp={"A": "@slen.ReturnValue", "B": "0"}); g.branch("bms", "@sgt.ReturnValue")
    g.get("gts3", "TmpStrings"); g.call("join", K_STR, "JoinStringArray", inp={"SourceArray": "@gts3.TmpStrings", "Separator": ", "})
    g.call("mc", K_STR, "Concat_StrStr", inp={"A": ts(g, "mlm", "Msg_LookMissing"), "B": "@join.ReturnValue"}); pop(g, "mpop", text_from_str(g, "mpt", "@mc.ReturnValue"))
    g.n("rs2", "call_self", function="Refresh State"); g.get("gpg", "Page"); g.n("sp", "call_self", function="Select Page", inp={"name": "@gpg.Page"})
    g.chain("entry", "rs", "sn", "f1"); g.chain("f1", "b1"); g.chain("b1:else", "to"); g.chain("f1:Completed", "sclr", "sn2", "f2")
    g.chain("f2", "fi", "bfi", "ib2", "bhas", "b2"); g.chain("bfi:else", "sadd"); g.chain("bhas:else", "sadd"); g.chain("b2:else", "we", "bwe"); g.chain("bwe:else", "sadd")
    g.chain("f2:Completed", "ck", "sn3", "f3"); g.chain("f3", "b3", "fcc", "bcv", "chg", "svc")
    g.chain("f3:Completed", "sn4", "f4"); g.chain("f4", "b4"); g.chain("b4:else", "rsc")
    g.chain("f4:Completed", "md", "smd", "sbo", "swa", "shi", "cb2", "cw2", "sbc", "bsk", "cs", "bh"); g.chain("bsk:else", "bh")
    g.chain("bh", "hrow", "bho", "ch", "chc"); g.chain("bho:else", "hpop", "chc"); g.chain("bh:else", "chc"); g.chain("hrow:Row Not Found", "chc")   # hairstyle gone (mod removed) -> keep going
    g.chain("chc", "svh", "umt", "ues", "rcp", "sa", "sd", "bb", "ab", "sbv", "svs", "bms"); g.chain("bb:else", "bms"); g.chain("bms", "mpop", "rs2"); g.chain("bms:else", "rs2"); g.chain("rs2", "sp")
    return fn("Apply Snapshot", [param("snap", "struct:" + S_SNAP)], graph=g)


def history_step(name, src, dst):
    g = G()
    g.get("gs", src); g.call("ln", K_ARR, "Array_Length", inp={"TargetArray": "@gs.%s" % src}); g.call("gt", K_MATH, "Greater_IntInt", inp={"A": "@ln.ReturnValue", "B": "0"}); g.branch("b", "@gt.ReturnValue")
    g.get("gs2", src); g.call("li", K_ARR, "Array_LastIndex", inp={"TargetArray": "@gs2.%s" % src}); g.call("get", K_ARR, "Array_Get", inp={"TargetArray": "@gs2.%s" % src, "Index": "@li.ReturnValue"})
    g.set("st", "TmpSnap", inp={"TmpSnap": "@get.Item"})
    g.n("ts", "call_self", function="Take Snapshot"); g.get("gd", dst); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gd.%s" % dst, "NewItem": "@ts.snap"})
    g.get("gs3", src); g.call("li2", K_ARR, "Array_LastIndex", inp={"TargetArray": "@gs3.%s" % src}); g.call("rm", K_ARR, "Array_Remove", inp={"TargetArray": "@gs3.%s" % src, "IndexToRemove": "@li2.ReturnValue"})
    g.get("gt2", "TmpSnap"); g.n("ap", "call_self", function="Apply Snapshot", inp={"snap": "@gt2.TmpSnap"}); g.n("rst", "call_self", function="Rebuild Status")
    g.chain("entry", "b", "st", "ts", "add", "rm", "ap", "rst"); return fn(name, graph=g)


# ---------------- Makeup presets (vanilla MakeupPreset_Save, slot "MakeupPreset") ----------------
PRESET_SLOT = "MakeupPreset"


def f_load_presets():
    g = G()
    g.call("ex", K_GS, "DoesSaveGameExist", inp={"SlotName": PRESET_SLOT, "UserIndex": "0"}); g.branch("b", "@ex.ReturnValue")
    g.call("ld", K_GS, "LoadGameFromSlot", inp={"SlotName": PRESET_SLOT, "UserIndex": "0"}); g.cast("cl", P_PRESET_SAVE, "@ld.ReturnValue")
    g.set("s1", "Presets", inp={"Presets": "@cl.AsMakeup Preset Save"})
    g.call("cr", K_GS, "CreateSaveGameObject", inp={"SaveGameClass": P_PRESET_SAVE}); g.cast("cc", P_PRESET_SAVE, "@cr.ReturnValue")
    g.set("s2", "Presets", inp={"Presets": "@cc.AsMakeup Preset Save"})
    g.get("gs", "Presets"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gs.Presets"}); g.branch("bv", "@iv.ReturnValue")
    g.chain("entry", "ex", "b", "ld", "s1", "bv"); g.chain("bv:else", "cr", "s2"); g.chain("b:else", "cr")
    return fn("Load Presets", graph=g)


def f_preset_icon():
    """Load and cache the game's icon file (Saved/SaveGames/Makeup/Preset_<n>.jpg); missing -> None."""
    g = G()
    g.get("gi", "PresetIcons"); g.call("fnd", K_MAP, "Map_Find", inp={"TargetMap": "@gi.PresetIcons", "Key": "@entry.number"}); g.branch("b", "@fnd.ReturnValue")
    g.link("fnd.Value", "return.tex")
    g.call("dir", K_PATHS, "ProjectSavedDir"); g.call("ns", K_STR, "Conv_IntToString", inp={"InInt": "@entry.number"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@dir.ReturnValue", "B": "SaveGames/Makeup/Preset_"}); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@ns.ReturnValue"})
    g.call("c3", K_STR, "Concat_StrStr", inp={"A": "@c2.ReturnValue", "B": ".jpg"})
    g.call("imp", K_REND, "ImportFileAsTexture2D", inp={"Filename": "@c3.ReturnValue"})
    g.get("gi2", "PresetIcons"); g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gi2.PresetIcons", "Key": "@entry.number", "Value": "@imp.ReturnValue"})
    g.n("r2", "return_new"); g.link("imp.ReturnValue", "r2.tex")
    g.chain("entry", "b", "return"); g.chain("b:else", "imp", "add", "r2")
    return fn("Preset Icon", [param("number", "int")], [param("tex", "object:" + E_TEX2D)], graph=g)


def f_preset_index():
    """"Preset_<i>" -> i"""
    g = G(); g.call("ns", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"}); g.call("sub", K_STR, "GetSubstring", inp={"SourceString": "@ns.ReturnValue", "StartIndex": "7", "Length": "10"})
    g.call("i", K_STR, "Conv_StringToInt", inp={"InString": "@sub.ReturnValue"}); g.link("i.ReturnValue", "return.index"); g.chain("entry", "return")
    return fn("Preset Index", [param("name", "name")], [param("index", "int")], graph=g)


def presets_data(g, id):
    g.get(id + "_p", "Presets"); g.get(id, "Data", cls=P_PRESET_SAVE); g.link(id + "_p.Presets", id + ".self"); return "@%s.Data" % id


def f_preset_clicked():
    g = G(); data = presets_data(g, "gd")
    g.call("get", K_ARR, "Array_Get", inp={"TargetArray": data, "Index": "@entry.index"}); g.set("st", "TmpPreset", inp={"TmpPreset": "@get.Item"})
    g.get("gpl", "Player"); g.get("gtp", "TmpPreset"); g.call("ap", P_JODI, "Apply Makeup Preset", inp={"self": "@gpl.Player", "data": "@gtp.TmpPreset"})
    g.get("gpl2", "Player"); g.call("sa", P_JODI, "Save Appearance", inp={"self": "@gpl2.Player"})
    g.set("sd", "MakeupDirty", inp={"MakeupDirty": "true"}); g.n("rl", "call_self", function="Rebuild Look")
    g.n("ph", "call_self", function="Push History"); g.chain("entry", "ph", "st", "ap", "sa", "sd", "rl"); return fn("Preset Clicked", [param("index", "int")], graph=g)


def f_preset_add():
    g = G(); md = makeup_data(g, "md")
    g.get("gp", "Presets"); g.call("add", P_PRESET_SAVE, "Add New Preset", inp={"self": "@gp.Presets", "makeup": md})
    g.get("gp2", "Presets"); g.call("sv", P_PRESET_SAVE, "Save Makeup Preset", inp={"self": "@gp2.Presets"})
    g.n("cap", "call_self", function="Capture Preset Icon", inp={"number": "@add.number"})
    g.n("rc", "call_self", function="Rebuild Look Cats"); g.n("rl", "call_self", function="Rebuild Look")
    g.chain("entry", "md", "add", "sv", "cap", "rc", "rl"); return fn("Preset Add", graph=g)


E_SCAP = "/Script/Engine.SceneCapture2D"; E_SCAPC = "/Script/Engine.SceneCaptureComponent2D"; E_SCENEC = "/Script/Engine.SceneComponent"; E_CHAR = "/Script/Engine.Character"; E_CAMC = "/Script/Engine.CameraComponent"


def f_capture_photo():
    """SceneCapture2D `distance` cm in front of `target` (along Jodi's forward vector) and `rise` cm above it, looking at `target`; fill light whose
    intensity grows with distance^2 (same illuminance on Jodi as the 55 cm preset icons); RT width x height -> after IconFrames frames Finish Photo exports dir/file."""
    g = G()
    g.get("gpl0", "Player"); g.call("pv", K_SYS, "IsValid", inp={"Object": "@gpl0.Player"}); g.branch("bpv", "@pv.ReturnValue")
    # a capture still in flight (second photo within IconFrames frames) -> drop its actors first; otherwise the old SceneCapture2D
    # (bCaptureEveryFrame) would be orphaned and render every frame until the level changes
    g.get("gia0", "IconActor"); g.call("iva", K_SYS, "IsValid", inp={"Object": "@gia0.IconActor"}); g.branch("bia", "@iva.ReturnValue")
    g.get("gia1", "IconActor"); g.call("dsa", E_ACTOR, "K2_DestroyActor", inp={"self": "@gia1.IconActor"})
    g.get("gil1", "IconLight"); g.call("dsl", E_ACTOR, "K2_DestroyActor", inp={"self": "@gil1.IconLight"})
    # RTF_RGBA8_SRGB: RGBA8 without sRGB has bForceLinearGamma=true -> tonemapper writes linear -> PNG export too dark
    g.call("crt", K_REND, "CreateRenderTarget2D", inp={"Width": "@entry.width", "Height": "@entry.height", "Format": "RTF_RGBA8_SRGB", "ClearColor": "(R=0,G=0,B=0,A=1)", "bAutoGenerateMipMaps": "false"})
    g.set("srt", "PhotoRT", inp={"PhotoRT": "@crt.ReturnValue"})
    g.get("gpl2", "Player"); g.call("fwd", E_ACTOR, "GetActorForwardVector", inp={"self": "@gpl2.Player"})
    g.call("fv", K_MATH, "Multiply_VectorFloat", inp={"A": "@fwd.ReturnValue", "B": "@entry.distance"})
    g.call("cl0", K_MATH, "Add_VectorVector", inp={"A": "@entry.target", "B": "@fv.ReturnValue"})
    g.call("up", K_MATH, "MakeVector", inp={"X": "0.0", "Y": "0.0", "Z": "@entry.rise"})
    g.call("cl", K_MATH, "Add_VectorVector", inp={"A": "@cl0.ReturnValue", "B": "@up.ReturnValue"})
    g.call("rot", K_MATH, "FindLookAtRotation", inp={"Start": "@cl.ReturnValue", "Target": "@entry.target"})
    g.call("tf", K_MATH, "MakeTransform", inp={"Location": "@cl.ReturnValue", "Rotation": "@rot.ReturnValue", "Scale": "(X=1,Y=1,Z=1)"})
    g.n("sp", "spawn", cls=E_SCAP, inp={"SpawnTransform": "@tf.ReturnValue"})
    g.get("gc", "CaptureComponent2D", cls=E_SCAP); g.link("sp.ReturnValue", "gc.self")
    g.get("grt2", "PhotoRT")
    g.n("st", "set", var="TextureTarget", cls=E_SCAPC, inp={"self": "@gc.CaptureComponent2D", "TextureTarget": "@grt2.PhotoRT"})
    g.n("sf", "set", var="FOVAngle", cls=E_SCAPC, inp={"self": "@gc.CaptureComponent2D", "FOVAngle": "28.0"})
    g.n("ss", "set", var="CaptureSource", cls=E_SCAPC, inp={"self": "@gc.CaptureComponent2D", "CaptureSource": "SCS_FinalColorLDR"})
    g.n("se", "set", var="bCaptureEveryFrame", cls=E_SCAPC, inp={"self": "@gc.CaptureComponent2D", "bCaptureEveryFrame": "true"})
    # take over the game camera's post-process (exposure/bias as in the game image), blend 1
    g.get("gpl3", "Player"); g.get("gcam", "Camera", cls=P_JODI); g.link("gpl3.Player", "gcam.self")
    g.get("pps", "PostProcessSettings", cls=E_CAMC); g.link("gcam.Camera", "pps.self")
    g.n("spp", "set", var="PostProcessSettings", cls=E_SCAPC, inp={"self": "@gc.CaptureComponent2D", "PostProcessSettings": "@pps.PostProcessSettings"})
    g.n("spw", "set", var="PostProcessBlendWeight", cls=E_SCAPC, inp={"self": "@gc.CaptureComponent2D", "PostProcessBlendWeight": "1.0"})
    # fill light at the camera point (only during the capture; like the light in the mirror room), radius = 2 x distance,
    # intensity 400 cd x (distance / 55 cm)^2: inverse-square falloff -> Jodi gets the same illuminance at every capture distance
    g.n("spl", "spawn", cls="/Script/Engine.SpotLight", inp={"SpawnTransform": "@tf.ReturnValue"})
    g.get("glc", "SpotLightComponent", cls="/Script/Engine.SpotLight"); g.link("spl.ReturnValue", "glc.self")
    g.call("rad", K_MATH, "Multiply_FloatFloat", inp={"A": "@entry.distance", "B": "2.0"})
    g.call("dq", K_MATH, "Divide_FloatFloat", inp={"A": "@entry.distance", "B": "55.0"}); g.call("dsq", K_MATH, "Multiply_FloatFloat", inp={"A": "@dq.ReturnValue", "B": "@dq.ReturnValue"})
    g.call("lint", K_MATH, "Multiply_FloatFloat", inp={"A": "@dsq.ReturnValue", "B": "400.0"})
    g.call("li", "/Script/Engine.LightComponent", "SetIntensity", inp={"self": "@glc.SpotLightComponent", "NewIntensity": "@lint.ReturnValue"})
    g.call("lr", "/Script/Engine.LocalLightComponent", "SetAttenuationRadius", inp={"self": "@glc.SpotLightComponent", "NewRadius": "@rad.ReturnValue"})
    g.call("lo", "/Script/Engine.SpotLightComponent", "SetOuterConeAngle", inp={"self": "@glc.SpotLightComponent", "NewOuterConeAngle": "35.0"})
    g.call("ls", "/Script/Engine.LightComponentBase", "SetCastShadows", inp={"self": "@glc.SpotLightComponent", "bNewValue": "false"})
    # attach the light exactly to the capture component (snap): same position and view direction as the capture camera
    g.call("lrot", E_ACTOR, "K2_AttachToComponent", inp={"self": "@spl.ReturnValue", "Parent": "@gc.CaptureComponent2D", "SocketName": "None", "LocationRule": "SnapToTarget", "RotationRule": "SnapToTarget", "ScaleRule": "KeepWorld", "bWeldSimulatedBodies": "false"})
    g.call("li2", "/Script/Engine.LightComponent", "SetIntensity", inp={"self": "@glc.SpotLightComponent", "NewIntensity": "@lint.ReturnValue"})
    g.set("sil", "IconLight", inp={"IconLight": "@spl.ReturnValue"}); g.set("sia", "IconActor", inp={"IconActor": "@sp.ReturnValue"})
    g.set("sdir", "PhotoDir", inp={"PhotoDir": "@entry.dir"}); g.set("sfile", "PhotoFile", inp={"PhotoFile": "@entry.file"}); g.set("sif", "IconFrames", inp={"IconFrames": "30"})
    g.chain("entry", "bpv", "bia", "dsa", "dsl", "crt", "srt", "sp", "st", "sf", "ss", "se", "spp", "spw", "spl", "li", "lr", "lo", "ls", "lrot", "li2", "sil", "sia", "sdir", "sfile", "sif")
    g.chain("bia:else", "crt")
    return fn("Capture Photo", [param("target", "struct:/Script/CoreUObject.Vector"), param("distance", "float"), param("rise", "float"), param("width", "int"), param("height", "int"), param("dir", "string"), param("file", "string")], graph=g)


def f_capture_preset_photo():
    """Preset icon: 55 cm in front of the head socket, 256x256, SaveGames/Makeup/Preset_<n>.jpg (PNG data, file name like vanilla)."""
    g = G()
    g.get("gpl", "Player"); g.get("gm", "Mesh", cls=E_CHAR); g.link("gpl.Player", "gm.self")
    g.call("head", E_SCENEC, "GetSocketLocation", inp={"self": "@gm.Mesh", "InSocketName": "head"})
    g.call("tgt", K_MATH, "Add_VectorVector", inp={"A": "@head.ReturnValue", "B": "(X=0,Y=0,Z=2)"})
    g.call("dir", K_PATHS, "ProjectSavedDir"); g.call("pdir", K_STR, "Concat_StrStr", inp={"A": "@dir.ReturnValue", "B": "SaveGames/Makeup"})
    g.call("ns", K_STR, "Conv_IntToString", inp={"InInt": "@entry.number"}); g.call("fn1", K_STR, "Concat_StrStr", inp={"A": "Preset_", "B": "@ns.ReturnValue"}); g.call("fn2", K_STR, "Concat_StrStr", inp={"A": "@fn1.ReturnValue", "B": ".jpg"})
    g.set("sk", "PhotoKind", inp={"PhotoKind": "Preset"}); g.set("sin", "IconNumber", inp={"IconNumber": "@entry.number"})
    g.n("cap", "call_self", function="Capture Photo", inp={"target": "@tgt.ReturnValue", "distance": "55.0", "rise": "0.0", "width": "256", "height": "256", "dir": "@pdir.ReturnValue", "file": "@fn2.ReturnValue"})
    g.chain("entry", "sk", "sin", "cap"); return fn("Capture Preset Icon", [param("number", "int")], graph=g)


def f_capture_look_photo():
    """Look photo: aim 15 cm above the actor location (capsule centre; Jodi with heels sits higher than the capsule, so the frame
    is centred on her), camera 200 cm in front and 40 cm above that point - chest height, slight downward tilt - 256x512 portrait, SaveGames/AltUI/Look_<id>.png."""
    g = G()
    g.get("gpl", "Player"); g.call("loc0", E_ACTOR, "K2_GetActorLocation", inp={"self": "@gpl.Player"})
    g.call("loc", K_MATH, "Add_VectorVector", inp={"A": "@loc0.ReturnValue", "B": "(X=0,Y=0,Z=15)"})
    g.call("dir", K_PATHS, "ProjectSavedDir"); g.call("pdir", K_STR, "Concat_StrStr", inp={"A": "@dir.ReturnValue", "B": "SaveGames/AltUI"})
    g.call("ns", K_STR, "Conv_IntToString", inp={"InInt": "@entry.id"}); g.call("fn1", K_STR, "Concat_StrStr", inp={"A": "Look_", "B": "@ns.ReturnValue"}); g.call("fn2", K_STR, "Concat_StrStr", inp={"A": "@fn1.ReturnValue", "B": ".png"})
    g.set("sk", "PhotoKind", inp={"PhotoKind": "Look"}); g.set("sin", "IconNumber", inp={"IconNumber": "@entry.id"})
    g.n("cap", "call_self", function="Capture Photo", inp={"target": "@loc.ReturnValue", "distance": "200.0", "rise": "40.0", "width": "256", "height": "512", "dir": "@pdir.ReturnValue", "file": "@fn2.ReturnValue"})
    g.chain("entry", "sk", "sin", "cap"); return fn("Capture Look Photo", [param("id", "int")], graph=g)


def f_finish_photo():
    """After a few rendered frames: export the render target, remove capture actor + light, drop the cached icon, redraw the page."""
    g = G()
    g.get("grt", "PhotoRT"); g.get("gd", "PhotoDir"); g.get("gf", "PhotoFile"); g.call("ex", K_REND, "ExportRenderTarget", inp={"TextureRenderTarget": "@grt.PhotoRT", "FilePath": "@gd.PhotoDir", "FileName": "@gf.PhotoFile"})
    g.get("gia", "IconActor"); g.call("dst", E_ACTOR, "K2_DestroyActor", inp={"self": "@gia.IconActor"})
    g.get("gil", "IconLight"); g.call("dsl", E_ACTOR, "K2_DestroyActor", inp={"self": "@gil.IconLight"})
    g.get("gk", "PhotoKind"); g.call("isl", K_MATH, "EqualEqual_NameName", inp={"A": "@gk.PhotoKind", "B": "Look"}); g.branch("bl", "@isl.ReturnValue")
    g.get("gli", "LookIcons"); g.get("gin", "IconNumber"); g.call("lrm", K_MAP, "Map_Remove", inp={"TargetMap": "@gli.LookIcons", "Key": "@gin.IconNumber"}); g.n("rls", "call_self", function="Rebuild Looks")
    g.get("gpi", "PresetIcons"); g.get("gin2", "IconNumber"); g.call("prm", K_MAP, "Map_Remove", inp={"TargetMap": "@gpi.PresetIcons", "Key": "@gin2.IconNumber"}); g.n("rl", "call_self", function="Rebuild Look")
    g.chain("entry", "ex", "dst", "dsl", "bl", "lrm", "rls"); g.chain("bl:else", "prm", "rl"); return fn("Finish Photo", graph=g)


def f_look_icon():
    """Load and cache Saved/SaveGames/AltUI/Look_<id>.png; missing -> None (not cached: the file may still be written)."""
    g = G()
    g.get("gi", "LookIcons"); g.call("fnd", K_MAP, "Map_Find", inp={"TargetMap": "@gi.LookIcons", "Key": "@entry.id"}); g.branch("b", "@fnd.ReturnValue")
    g.link("fnd.Value", "return.tex")
    g.call("dir", K_PATHS, "ProjectSavedDir"); g.call("ns", K_STR, "Conv_IntToString", inp={"InInt": "@entry.id"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@dir.ReturnValue", "B": "SaveGames/AltUI/Look_"}); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@ns.ReturnValue"})
    g.call("c3", K_STR, "Concat_StrStr", inp={"A": "@c2.ReturnValue", "B": ".png"})
    g.call("imp", K_REND, "ImportFileAsTexture2D", inp={"Filename": "@c3.ReturnValue"})
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@imp.ReturnValue"}); g.branch("bv", "@iv.ReturnValue")
    g.get("gi2", "LookIcons"); g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gi2.LookIcons", "Key": "@entry.id", "Value": "@imp.ReturnValue"})
    g.n("r2", "return_new"); g.link("imp.ReturnValue", "r2.tex")
    g.chain("entry", "b", "return"); g.chain("b:else", "imp", "bv", "add", "r2"); g.chain("bv:else", "r2")
    return fn("Look Icon", [param("id", "int")], [param("tex", "object:" + E_TEX2D)], graph=g)


def f_preset_delete():
    g = G()
    g.get("gp", "Presets"); g.call("rm", P_PRESET_SAVE, "Remove A Preset", inp={"self": "@gp.Presets", "index": "@entry.index"})
    g.get("gp2", "Presets"); g.call("sv", P_PRESET_SAVE, "Save Makeup Preset", inp={"self": "@gp2.Presets"})
    g.n("rc", "call_self", function="Rebuild Look Cats"); g.n("rl", "call_self", function="Rebuild Look")
    g.chain("entry", "rm", "sv", "rc", "rl"); return fn("Preset Delete", [param("index", "int")], graph=g)


def f_on_preset_context():
    def pre(g): g.set("sci", "ContextPreset", inp={"ContextPreset": "@entry.index"}); return ["sci"]
    g = simple_menu("On Preset Context", [("PresetApply", "Menu_Apply"), ("PresetView", "Menu_ViewContent"), ("PresetDelete", "Menu_Delete"), ("Cancel", "Menu_Cancel")], pre)
    return fn("On Preset Context", [param("index", "int")], graph=g)


def f_on_bag_item_context():
    """Right click on the Attire & Backpack page: wear/take off, colour (worn + adjustable), reset colour (custom colour stored),
    repair (if damaged), put in backpack (owned, not in the bag) or remove (in the bag), to wardrobe (if new)."""
    g = G()
    g.get("gm", "Menu"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gm.Menu"}); g.branch("b", "@iv.ReturnValue")
    mw = create_widget(g, "cm", W_MENU); g.set("sm", "Menu", inp={"Menu": mw}); set_manager(g, "smm", W_MENU, mw)
    g.get("gm2", "Menu"); g.call("clr", W_MENU, "Clear Rows", inp={"self": "@gm2.Menu"})
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@entry.name"})
    g.call("ws", K_MATH, "SelectString", inp={"A": ts(g, "wo", "Menu_TakeOff"), "B": ts(g, "wn", "Menu_Wear"), "bPickA": "@iw.yes"}); g.call("wt", K_TXT, "Conv_StringToText", inp={"InString": "@ws.ReturnValue"})
    r0 = menu_row(g, 0, "BagWear", "@wt.ReturnValue")
    # colour: only worn and colour-adjustable pieces; reset only if a custom colour is stored
    g.n("fi", "call_self", function="Find Item", inp={"name": "@entry.name"}); g.brk("bi", S_ITEM, "@fi.item")
    g.call("cok", K_MATH, "BooleanAND", inp={"A": "@bi.ColorAdjustable", "B": "@iw.yes"}); g.branch("bc", "@cok.ReturnValue")
    r5 = menu_row(g, 5, "Color", tt(g, "ct5", "Menu_Color"))
    g.get("gplr", "Player"); g.call("gcr", P_CPB, "Get Clothes Color", inp={"self": "@gplr.Player", "clothes name": "@entry.name"}); g.branch("brc", "@gcr.found")
    r6 = menu_row(g, 6, "ClothesResetColor", tt(g, "rct", "Menu_ClothesReset"))
    g.n("dm", "call_self", function="Is Damaged", inp={"name": "@entry.name"}); g.branch("bd", "@dm.yes")
    r1 = menu_row(g, 1, "BagRepair", tt(g, "rt", "Menu_Repair"))
    # in the bag -> remove; owned but not in the bag (worn section) -> put in
    g.n("ib", "call_self", function="In Bag", inp={"name": "@entry.name"}); g.branch("bib", "@ib.yes")
    r2 = menu_row(g, 2, "BagRemove", tt(g, "xt", "Menu_BagRemove"))
    g.n("io", "call_self", function="Is Owned", inp={"name": "@entry.name"}); g.branch("bpb", "@io.yes")
    r7 = menu_row(g, 7, "PutInBag", tt(g, "pbt", "Menu_PutInBag"))
    g.call("nio", K_MATH, "Not_PreBool", inp={"A": "@io.yes"}); g.branch("bw", "@nio.ReturnValue")
    r3 = menu_row(g, 3, "BagToWardrobe", tt(g, "ct", "Menu_ToWardrobe"))
    r4 = menu_row(g, 4, "Cancel", tt(g, "at", "Menu_Cancel"))
    g.get("gm6", "Menu"); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@gm6.Menu", "ZOrder": "110"})
    g.call("mp", "/Script/UMG.WidgetLayoutLibrary", "GetMousePositionOnViewport")
    g.get("gm7", "Menu"); g.call("spv", E_USERWIDGET, "SetPositionInViewport", inp={"self": "@gm7.Menu", "Position": "@mp.ReturnValue", "bRemoveDPIScale": "false"})
    g.chain("entry", "b", "clr"); g.chain("b:else", "cm_cr", "sm", "smm", "clr")
    g.chain("clr", *r0, "fi", "bc", *r5, "gcr", "brc", *r6, "dm"); g.chain("bc:else", "dm"); g.chain("brc:else", "dm")
    g.chain("dm", "bd", *r1, "ib"); g.chain("bd:else", "ib")
    g.chain("ib", "bib", *r2, "bw"); g.chain("bib:else", "bpb", *r7, "bw"); g.chain("bpb:else", "bw")
    g.chain("bw", *r3, r4[0]); g.chain("bw:else", r4[0])
    g.chain(*r4, "atv", "mp", "spv")
    return fn("On Bag Item Context", [param("name", "name")], graph=g)


def f_close_menu():
    g = G(); g.get("gm", "Menu"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gm.Menu"}); g.branch("b", "@iv.ReturnValue")
    g.get("gm2", "Menu"); g.call("rm", E_WIDGET, "RemoveFromParent", inp={"self": "@gm2.Menu"}); g.chain("entry", "b", "rm")
    return fn("Close Menu", graph=g)


# context-menu / link actions: (action, manager function, argument variable or None). The argument pin is "name" for ContextItem,
# "index" for the other context variables. Actions with more than one call (DistPlus/DistMinus, ClearSearch, ThemeReset) are built in
# f_on_menu_action itself; "Cancel" just closes the menu.
MENU_ACTIONS = [
    ("Fav", "Toggle Favorite", "ContextItem"), ("Hide", "Toggle Item Hidden", "ContextItem"), ("Color", "Open Color", "ContextItem"),
    ("ClothesResetColor", "Clothes Reset Color", "ContextItem"), ("HairResetColor", "Hair Reset Color", "ContextItem"), ("HairColor", "Open Hair Color", None),
    ("PutInBag", "Put In Bag", "ContextItem"), ("BagWear", "Bag Toggle Wear", "ContextItem"), ("BagRepair", "Bag Repair", "ContextItem"),
    ("BagRemove", "Bag Remove", "ContextItem"), ("BagToWardrobe", "Bag To Wardrobe", "ContextItem"), ("BagCleanup", "Bag Cleanup", None),
    ("OutfitWear", "On Outfit Clicked", "ContextOutfit"), ("OutfitRename", "Start Outfit Rename", "ContextOutfit"), ("OutfitDelete", "Delete Outfit", "ContextOutfit"),
    ("LookRename", "Start Look Rename", "ContextLook"), ("LookUpdate", "Update Look", "ContextLook"), ("LookDelete", "Delete Look", "ContextLook"),
    ("PresetApply", "Preset Clicked", "ContextPreset"), ("PresetDelete", "Preset Delete", "ContextPreset"),
    ("OutfitView", "Open Outfit Content", "ContextOutfit"), ("LookView", "Open Look Content", "ContextLook"), ("PresetView", "Open Preset Content", "ContextPreset"),
    ("ContentBack", "Close Content", None), ("GoTo", "Go To Item", "ContextItem"),
    ("Undo", "Undo", None), ("Redo", "Redo", None)]


def f_on_menu_action():
    g = G()
    g.n("cm", "call_self", function="Close Menu")
    # +/- in the Jodi view: camera distance by one slider step (5 %), DIST_MIN..DIST_MAX, save, update the slider
    g.call("isP", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "DistPlus"}); g.call("isM", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "DistMinus"})
    g.call("orD", K_MATH, "BooleanOR", inp={"A": "@isP.ReturnValue", "B": "@isM.ReturnValue"}); g.branch("bdist", "@orD.ReturnValue")
    g.call("step", K_MATH, "SelectFloat", inp={"A": "0.05", "B": "-0.05", "bPickA": "@isP.ReturnValue"}); g.get("gcd", "CamDist")
    g.call("nd", K_MATH, "Add_FloatFloat", inp={"A": "@gcd.CamDist", "B": "@step.ReturnValue"}); g.call("ndc", K_MATH, "FClamp", inp={"Value": "@nd.ReturnValue", "Min": str(DIST_MIN), "Max": str(DIST_MAX)})
    g.set("scd", "CamDist", inp={"CamDist": "@ndc.ReturnValue"}); g.n("apo", "call_self", function="Apply Options"); g.n("svd", "call_self", function="Save Settings")
    g.get("gpgD", "Page"); g.call("isO", K_MATH, "EqualEqual_NameName", inp={"A": "@gpgD.Page", "B": "Options"}); g.branch("bO", "@isO.ReturnValue"); g.n("rbo", "call_self", function="Rebuild Options")
    g.chain("entry", "cm", "bdist", "scd", "apo", "svd", "bO", "rbo"); prev = "bdist:else"
    # multi-step actions
    g.get("gpcs", "Panel"); g.call("pcs", W_PANEL, "Clear Search", inp={"self": "@gpcs.Panel"})
    g.call("et", K_TXT, "Conv_StringToText", inp={"InString": ""}); g.n("osc", "call_self", function="On Search Changed", inp={"text": "@et.ReturnValue"})
    g.n("ftr", "call_self", function="Reset Theme"); g.n("ftr2", "call_self", function="Apply Theme"); g.n("ftr3", "call_self", function="Save Settings"); g.n("ftr4", "call_self", function="Rebuild Options")
    special = {"ClearSearch": ["pcs", "osc"], "ThemeReset": ["ftr", "ftr2", "ftr3", "ftr4"]}
    # one-call actions from the table; the branches form an else-chain (a name-comparison chain, ~25 compares per click)
    for i, (action, func, ctx) in enumerate([(a, None, None) for a in special] + MENU_ACTIONS):
        g.call("ia%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": action}); g.branch("ba%d" % i, "@ia%d.ReturnValue" % i)
        if action in special: body = special[action]
        elif ctx: g.get("gc%d" % i, ctx); g.n("fa%d" % i, "call_self", function=func, inp={("name" if ctx == "ContextItem" else "index"): "@gc%d.%s" % (i, ctx)}); body = ["fa%d" % i]
        else: g.n("fa%d" % i, "call_self", function=func); body = ["fa%d" % i]
        g.chain(prev, "ba%d" % i, *body); prev = "ba%d:else" % i
    return fn("On Menu Action", [param("name", "name")], graph=g)


# ---------------- Outfits (vanilla system: Outfits_Save in SaveGame slot "Outfits") ----------------
def f_load_outfits():
    g = G()
    g.call("ex", K_GS, "DoesSaveGameExist", inp={"SlotName": OUTFIT_SLOT, "UserIndex": "0"}); g.branch("b", "@ex.ReturnValue")
    g.call("ld", K_GS, "LoadGameFromSlot", inp={"SlotName": OUTFIT_SLOT, "UserIndex": "0"}); g.cast("cl", P_OUTFITS, "@ld.ReturnValue")
    g.set("s1", "Outfits", inp={"Outfits": "@cl.AsOutfits Save"})
    g.call("cr", K_GS, "CreateSaveGameObject", inp={"SaveGameClass": P_OUTFITS}); g.cast("cc", P_OUTFITS, "@cr.ReturnValue")
    g.set("s2", "Outfits", inp={"Outfits": "@cc.AsOutfits Save"})
    # cast failed (foreign slot content) -> empty object
    g.get("gs", "Outfits"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gs.Outfits"}); g.branch("bv", "@iv.ReturnValue")
    g.chain("entry", "ex", "b", "ld", "s1", "bv"); g.chain("bv:else", "cr", "s2"); g.chain("b:else", "cr")
    return fn("Load Outfits", graph=g)


def f_save_outfits():
    g = G(); g.get("go", "Outfits"); g.call("sv", K_GS, "SaveGameToSlot", inp={"SaveGameObject": "@go.Outfits", "SlotName": OUTFIT_SLOT, "UserIndex": "0"})
    g.chain("entry", "sv"); return fn("Save Outfits", graph=g)


def f_rebuild_top_tabs():
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear TopTabs", inp={"self": "@gp.Panel"})
    tail = ["entry", "cl"]
    for i, page in enumerate(["Clothes", "Outfits", "Looks", "Bag", "Hair", "Look", "Body", "Options"]):
        tw = create_widget(g, "ct%d" % i, W_TOP); set_manager(g, "sm%d" % i, W_TOP, tw)
        g.get("gpo%d" % i, "Page"); g.call("eq%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@gpo%d.Page" % i, "B": page}); sel = "@eq%d.ReturnValue" % i
        g.call("ti%d" % i, W_TOP, "Init", inp={"self": tw, "page": page, "caption": tt(g, "tt%d" % i, "Tab_" + page), "selected": sel})
        g.get("gp%d" % i, "Panel"); g.call("at%d" % i, W_PANEL, "Add TopTab", inp={"self": "@gp%d.Panel" % i, "widget": tw})
        tail += ["ct%d_cr" % i, "sm%d" % i, "ti%d" % i, "at%d" % i]
    g.chain(*tail); return fn("Rebuild TopTabs", graph=g)


def f_select_page():
    g = G()
    # the highlight of a "Show in tab" jump survives only the Select Page that jump issues (KeepHighlight); any other page change clears it
    g.get("gkh", "KeepHighlight"); g.branch("bkh", "@gkh.KeepHighlight"); g.set("skh", "KeepHighlight", inp={"KeepHighlight": "false"}); g.set("shl", "HighlightItem", inp={"HighlightItem": "None"})
    g.set("sp", "Page", inp={"Page": "@entry.name"})
    g.get("gp", "Panel"); g.call("spg", W_PANEL, "Set Page", inp={"self": "@gp.Panel", "page": "@entry.name"})
    g.n("rtt", "call_self", function="Rebuild TopTabs"); g.n("uf", "call_self", function="Update Focus")
    # content view open for this tab -> the Content page replaces the tab's own page
    g.n("co", "call_self", function="Content Open", inp={"page": "@entry.name"}); g.branch("bco", "@co.yes")
    g.get("gpc", "Panel"); g.call("spc", W_PANEL, "Set Page", inp={"self": "@gpc.Panel", "page": "Content"}); g.n("rcn", "call_self", function="Rebuild Content")
    g.call("iso", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Outfits"}); g.branch("bo", "@iso.ReturnValue")
    g.call("isb", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Bag"}); g.branch("bb", "@isb.ReturnValue")
    g.n("ro", "call_self", function="Rebuild Outfits"); g.n("rb", "call_self", function="Rebuild Bag")
    g.call("islk", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Looks"}); g.branch("blk", "@islk.ReturnValue"); g.n("rlk2", "call_self", function="Rebuild Looks")
    # rebuild the clothes page (outfit/backpack actions change what is worn)
    g.n("rl", "call_self", function="Rebuild Left"); g.n("rt", "call_self", function="Rebuild SubTabs"); g.n("rli", "call_self", function="Rebuild List")
    g.call("isc", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Clothes"}); g.branch("bc", "@isc.ReturnValue")
    g.call("ish", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Hair"}); g.branch("bh", "@ish.ReturnValue"); g.n("rh", "call_self", function="Rebuild Hair")
    g.call("isl", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Look"}); g.branch("bl", "@isl.ReturnValue")
    g.n("rlc", "call_self", function="Rebuild Look Cats"); g.n("rlk", "call_self", function="Rebuild Look")
    g.call("isy", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Body"}); g.branch("by", "@isy.ReturnValue"); g.n("rby", "call_self", function="Rebuild Body")
    g.call("iso2", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Options"}); g.branch("bop", "@iso2.ReturnValue"); g.n("rop", "call_self", function="Rebuild Options")
    g.n("cmn", "call_self", function="Close Menu")   # a context menu of the previous page would stay open otherwise
    g.chain("entry", "bkh", "skh", "cmn"); g.chain("bkh:else", "shl", "cmn")
    g.chain("cmn", "sp", "spg", "rtt", "uf", "co", "bco", "spc", "rcn")
    g.chain("bco:else", "bo", "ro"); g.chain("bo:else", "blk", "rlk2"); g.chain("blk:else", "bb", "rb"); g.chain("bb:else", "bc", "rl", "rt", "rli")
    g.chain("bc:else", "bh", "rh"); g.chain("bh:else", "bl", "rlc", "rlk"); g.chain("bl:else", "by", "rby"); g.chain("by:else", "bop", "rop")
    return fn("Select Page", [param("name", "name")], graph=g)


def f_rebuild_outfits():
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Outfits", inp={"self": "@gp.Panel"})
    # "+" tile
    g.get("gi0", "TmpIcons"); g.call("clr0", K_ARR, "Array_Clear", inp={"TargetArray": "@gi0.TmpIcons"})
    aw = create_widget(g, "ca", W_OUTFIT); set_manager(g, "sma", W_OUTFIT, aw)
    g.get("gi1", "TmpIcons"); g.call("ia", W_OUTFIT, "Init", inp={"self": aw, "index": "-1", "icons": "@gi1.TmpIcons", "count": "0", "caption": ""})
    g.get("gpa", "Panel"); g.call("aa", W_PANEL, "Add Outfit", inp={"self": "@gpa.Panel", "widget": aw})
    # per outfit: icons of the first pieces from the catalog
    g.get("go", "Outfits"); g.get("goa", "outfits", cls=P_OUTFITS); g.link("go.Outfits", "goa.self")
    g.foreach("fe", "@goa.outfits"); g.brk("bo", P_OUTFIT_S, "@fe.Array Element")
    g.get("gi2", "TmpIcons"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gi2.TmpIcons"})
    g.call("keys", K_MAP, "Map_Keys", inp={"TargetMap": "@bo." + OUTFIT_MEMBER})
    g.call("len", K_MAP, "Map_Length", inp={"TargetMap": "@bo." + OUTFIT_MEMBER})
    g.foreach("fk", "@keys.Keys")
    g.get("gi3", "TmpIcons"); g.call("cnt", K_ARR, "Array_Length", inp={"TargetArray": "@gi3.TmpIcons"})
    g.call("lt6", K_MATH, "Less_IntInt", inp={"A": "@cnt.ReturnValue", "B": "9"}); g.branch("b6", "@lt6.ReturnValue")
    g.n("fi", "call_self", function="Find Item", inp={"name": "@fk.Array Element"}); g.brk("bi", S_ITEM, "@fi.item")
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@bi.Icon"}); g.branch("biv", "@iv.ReturnValue")
    g.get("gi4", "TmpIcons"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gi4.TmpIcons", "NewItem": "@bi.Icon"})
    ow = create_widget(g, "co", W_OUTFIT); set_manager(g, "smo", W_OUTFIT, ow)
    g.n("on", "call_self", function="Outfit Name", inp={"index": "@fe.Array Index"}); g.call("ont", K_TXT, "Conv_StringToText", inp={"InString": "@on.name"})
    g.get("gi5", "TmpIcons"); g.call("io", W_OUTFIT, "Init", inp={"self": ow, "index": "@fe.Array Index", "icons": "@gi5.TmpIcons", "count": "@len.ReturnValue", "caption": "@ont.ReturnValue"})
    g.get("gpo", "Panel"); g.call("ao", W_PANEL, "Add Outfit", inp={"self": "@gpo.Panel", "widget": ow})
    g.chain("entry", "cl", "clr0", "ca_cr", "sma", "ia", "aa", "fe"); g.chain("fe", "clr", "keys", "fk")
    g.chain("fk", "b6", "fi", "biv", "add"); g.chain("fk:Completed", "on", "co_cr", "smo", "io", "ao")
    return fn("Rebuild Outfits", graph=g)


def f_on_outfit_clicked():
    g = G()
    g.get("gpg", "Page"); g.call("isl", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Look"}); g.branch("bpl", "@isl.ReturnValue"); g.n("pa", "call_self", function="Preset Add")
    g.call("neg", K_MATH, "Less_IntInt", inp={"A": "@entry.index", "B": "0"}); g.branch("b", "@neg.ReturnValue")
    g.get("go", "Outfits"); g.get("gpl", "Player"); g.call("ap", P_OUTFITS, "Add Preset", inp={"self": "@go.Outfits", "player": "@gpl.Player"})
    g.get("go2", "Outfits"); g.get("gpl2", "Player"); g.call("wear", P_OUTFITS, "Apply Preset to Player", inp={"self": "@go2.Outfits", "player": "@gpl2.Player", "index": "@entry.index"})
    g.get("gpl3", "Player"); g.call("sa", P_JODI, "Save Appearance", inp={"self": "@gpl3.Player"})
    g.n("rs", "call_self", function="Refresh State")
    g.n("sv", "call_self", function="Save Outfits"); g.n("ro", "call_self", function="Rebuild Outfits")
    g.n("ph", "call_self", function="Push History")
    g.chain("entry", "bpl", "pa"); g.chain("bpl:else", "b", "ap", "sv", "ro"); g.chain("b:else", "ph", "wear", "sa", "rs", "ro")
    return fn("On Outfit Clicked", [param("index", "int")], graph=g)


def f_on_outfit_context():
    g = G()
    g.call("neg", K_MATH, "Less_IntInt", inp={"A": "@entry.index", "B": "0"}); g.branch("bn", "@neg.ReturnValue")
    g.n("oc", "call_self", function="On Outfit Clicked", inp={"index": "@entry.index"})
    g.set("sco", "ContextOutfit", inp={"ContextOutfit": "@entry.index"})
    g.get("gm", "Menu"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gm.Menu"}); g.branch("b", "@iv.ReturnValue")
    mw = create_widget(g, "cm", W_MENU); g.set("sm", "Menu", inp={"Menu": mw}); set_manager(g, "smm", W_MENU, mw)
    g.get("gm2", "Menu"); g.call("clr", W_MENU, "Clear Rows", inp={"self": "@gm2.Menu"})
    tail = ["clr"]
    for i, (action, key) in enumerate([("OutfitWear", "Menu_Wear"), ("OutfitView", "Menu_ViewContent"), ("OutfitRename", "Menu_Rename"), ("OutfitDelete", "Menu_Delete"), ("Cancel", "Menu_Cancel")]):
        rw = create_widget(g, "cr%d" % i, W_ROW); set_manager(g, "sr%d" % i, W_ROW, rw)
        g.call("ri%d" % i, W_ROW, "Init", inp={"self": rw, "action": action, "caption": tt(g, "t%d" % i, key)})
        g.get("gm%d" % (i + 10), "Menu"); g.call("ar%d" % i, W_MENU, "Add Row", inp={"self": "@gm%d.Menu" % (i + 10), "widget": rw})
        tail += ["cr%d_cr" % i, "sr%d" % i, "ri%d" % i, "ar%d" % i]
    g.get("gm6", "Menu"); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@gm6.Menu", "ZOrder": "110"})
    g.call("mp", "/Script/UMG.WidgetLayoutLibrary", "GetMousePositionOnViewport")
    g.get("gm7", "Menu"); g.call("spv", E_USERWIDGET, "SetPositionInViewport", inp={"self": "@gm7.Menu", "Position": "@mp.ReturnValue", "bRemoveDPIScale": "false"})
    g.chain("entry", "bn", "oc"); g.chain("bn:else", "sco", "b", "clr"); g.chain("b:else", "cm_cr", "sm", "smm", "clr")
    g.chain(*tail, "atv", "mp", "spv")
    return fn("On Outfit Context", [param("index", "int")], graph=g)


# ---------------- Attire & Backpack ----------------
def player_bag(g, id):
    """Player.Bag (Bag_Comp) as a pin."""
    g.get(id + "_p", "Player"); g.get(id, "Bag", cls=P_CPB); g.link(id + "_p.Player", id + ".self"); return "@%s.Bag" % id


def f_in_bag():
    g = G(); bag = player_bag(g, "gb")
    g.call("has", P_BAG, "Has this Clothes ?", inp={"self": bag, "clothes name": "@entry.name"}); g.link("has.yes", "return.yes")
    g.chain("entry", "return"); return fn("In Bag", [param("name", "name")], [param("yes", "bool")], graph=g)


def f_is_damaged():
    g = G(); g.get("gp", "Player"); g.call("d", P_CPB, "Is Clothes Damaged", inp={"self": "@gp.Player", "clothes": "@entry.name"}); g.link("d.yes", "return.yes")
    g.chain("entry", "return"); return fn("Is Damaged", [param("name", "name")], [param("yes", "bool")], graph=g)


def f_rebuild_bag():
    g = G()
    g.get("gp", "Panel"); g.call("cw", W_PANEL, "Clear Bag Worn", inp={"self": "@gp.Panel"})
    g.get("gp2", "Panel"); g.call("cl", W_PANEL, "Clear Bag List", inp={"self": "@gp2.Panel"})
    g.get("gpl0", "Panel"); g.call("cll", W_PANEL, "Clear Bag Links", inp={"self": "@gpl0.Panel"})
    lw = create_widget(g, "clk", W_TXT); set_manager(g, "sml", W_TXT, lw)
    g.call("li", W_TXT, "Init", inp={"self": lw, "action": "BagCleanup", "caption": tt(g, "lt", "Btn_BagCleanup")})
    g.get("gpl1", "Panel"); g.call("al", W_PANEL, "Add Bag Link", inp={"self": "@gpl1.Panel", "widget": lw})
    g.set("nf", "TmpIdx", inp={"TmpIdx": "0"})
    # worn
    g.get("gw", "Worn"); g.foreach("fw", "@gw.Worn")
    g.n("fi", "call_self", function="Find Item", inp={"name": "@fw.Array Element"}); g.branch("bf", "@fi.found")
    ww = create_widget(g, "cw1", W_BTN); set_manager(g, "smw", W_BTN, ww)
    g.n("io", "call_self", function="Is Owned", inp={"name": "@fw.Array Element"}); g.n("ifv", "call_self", function="Is Favorite", inp={"name": "@fw.Array Element"})
    g.n("dm", "call_self", function="Is Damaged", inp={"name": "@fw.Array Element"})
    g.n("wti", "call_self", function="Item Tip", inp={"item": "@fi.item"})
    g.call("wi", W_BTN, "Init", inp={"self": ww, "item": "@fi.item", "worn": "true", "owned": "@io.yes", "fav": "@ifv.yes", "damaged": "@dm.yes", "tip": "@wti.tip"})
    g.get("gp3", "Panel"); g.call("aw", W_PANEL, "Add Bag Worn", inp={"self": "@gp3.Panel", "widget": ww})
    # in the backpack (not worn)
    bag = player_bag(g, "gb"); g.get("gcb", "Clothes in bag", cls=P_BAG); g.link("gb.Bag", "gcb.self")
    g.set("sbl", "TmpNames", inp={"TmpNames": "@gcb.Clothes in bag"}); g.get("gtn", "TmpNames"); g.foreach("fb", "@gtn.TmpNames")
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@fb.Array Element"}); g.call("niw", K_MATH, "Not_PreBool", inp={"A": "@iw.yes"}); g.branch("bnw", "@niw.ReturnValue")
    g.n("fi2", "call_self", function="Find Item", inp={"name": "@fb.Array Element"}); g.branch("bf2", "@fi2.found")
    bw = create_widget(g, "cb1", W_BTN); set_manager(g, "smb", W_BTN, bw)
    g.n("io2", "call_self", function="Is Owned", inp={"name": "@fb.Array Element"}); g.n("ifv2", "call_self", function="Is Favorite", inp={"name": "@fb.Array Element"})
    g.n("dm2", "call_self", function="Is Damaged", inp={"name": "@fb.Array Element"})
    g.n("bti2", "call_self", function="Item Tip", inp={"item": "@fi2.item"})
    g.call("bi", W_BTN, "Init", inp={"self": bw, "item": "@fi2.item", "worn": "false", "owned": "@io2.yes", "fav": "@ifv2.yes", "damaged": "@dm2.yes", "tip": "@bti2.tip"})
    g.get("gp4", "Panel"); g.call("ab", W_PANEL, "Add Bag Item", inp={"self": "@gp4.Panel", "widget": bw})
    g.get("gn", "TmpIdx"); g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gn.TmpIdx", "B": "1"}); g.set("sn", "TmpIdx", inp={"TmpIdx": "@inc.ReturnValue"})
    g.get("gn2", "TmpIdx"); g.call("eq0", K_MATH, "EqualEqual_IntInt", inp={"A": "@gn2.TmpIdx", "B": "0"})
    g.get("gp5", "Panel"); g.call("sbe", W_PANEL, "Set Bag Empty", inp={"self": "@gp5.Panel", "visible": "@eq0.ReturnValue"})
    g.chain("entry", "cw", "cl", "cll", "clk_cr", "sml", "li", "al", "nf", "fw"); g.chain("fw", "fi", "bf", "cw1_cr", "smw", "dm", "wti", "wi", "aw")
    g.chain("fw:Completed", "sbl", "fb"); g.chain("fb", "bnw", "fi2", "bf2", "cb1_cr", "smb", "dm2", "bti2", "bi", "ab", "sn")
    g.chain("fb:Completed", "sbe")
    return fn("Rebuild Bag", graph=g)


def after_bag_change(g, first):
    """Save Appearance, Refresh State, Rebuild Bag (chain starting at `first`)."""
    g.get("gpl9", "Player"); g.call("sa9", P_JODI, "Save Appearance", inp={"self": "@gpl9.Player"})
    g.n("rs9", "call_self", function="Refresh State"); g.n("rb9", "call_self", function="Rebuild Bag")
    g.chain(first, "sa9", "rs9", "rb9")


def f_bag_toggle_wear():
    g = G()
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@entry.name"}); g.call("nw", K_MATH, "Not_PreBool", inp={"A": "@iw.yes"})
    g.get("gpl", "Player"); g.call("u", P_JODI, "Use Clothes from Bag", inp={"self": "@gpl.Player", "clothes name": "@entry.name", "is wear": "@nw.ReturnValue"})
    g.n("ph", "call_self", function="Push History"); g.chain("entry", "ph", "u"); after_bag_change(g, "u")
    return fn("Bag Toggle Wear", [param("name", "name")], graph=g)


def f_bag_remove():
    g = G()
    # deliberately without the vanilla lock for default underwear (z-fighting under tight outfits)
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@entry.name"}); g.branch("bw", "@iw.yes")
    g.get("gpl", "Player"); g.call("to", P_CPB, "Take off this clothes", inp={"self": "@gpl.Player", "clothes name": "@entry.name"})
    g.get("gpl2", "Player"); g.call("rm", P_CPB, "Remove Clothing From Bag", inp={"self": "@gpl2.Player", "clothing name": "@entry.name"})
    g.n("ph", "call_self", function="Push History"); g.chain("entry", "ph", "bw", "to", "rm"); g.chain("bw:else", "rm"); after_bag_change(g, "rm")
    return fn("Bag Remove", [param("name", "name")], graph=g)


def f_bag_cleanup():
    """Vanilla 'Remove all undressed clothes' (InventoryPanel): removes unworn clothes that are in the wardrobe from the backpack."""
    g = G()
    g.call("gs", K_GS, "GetGameState"); g.cast("cgs", P_GS2, "@gs.ReturnValue")
    g.get("gui", "UserInterface", cls=P_GS2); g.link("cgs.AsTKA Game State", "gui.self")
    g.get("gip", "InventoryPanel", cls=P_HUD); g.link("gui.UserInterface", "gip.self")
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@gip.InventoryPanel"}); g.branch("b", "@iv.ReturnValue")
    g.call("ru", P_INV, "Remove all undressed clothes", inp={"self": "@gip.InventoryPanel"})
    g.chain("entry", "b", "ru"); after_bag_change(g, "ru")
    return fn("Bag Cleanup", graph=g)


def f_bag_repair():
    g = G()
    g.call("gs", K_GS, "GetGameState"); g.cast("cgs", P_GS2, "@gs.ReturnValue")
    g.get("gui", "UserInterface", cls=P_GS2); g.link("cgs.AsTKA Game State", "gui.self")
    g.get("gip", "InventoryPanel", cls=P_HUD); g.link("gui.UserInterface", "gip.self")
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@gip.InventoryPanel"}); g.branch("b", "@iv.ReturnValue")
    g.call("rp", P_INV, "Repair Clothes", inp={"self": "@gip.InventoryPanel", "clothes": "@entry.name", "all": "false"})
    g.chain("entry", "b", "rp"); after_bag_change(g, "rp")
    return fn("Bag Repair", [param("name", "name")], graph=g)


def f_bag_to_wardrobe():
    g = G()
    g.call("gs", K_GS, "GetGameState"); g.cast("cgs", P_GS, "@gs.ReturnValue")
    g.call("wd", P_GS, "Get Wardrobe Data", inp={"self": "@cgs.AsTKA Game State Base"})
    g.call("add", P_WD, "Add Item And Save", inp={"self": "@wd.wardrobe data", "name": "@entry.name"})
    g.chain("entry", "wd", "add"); after_bag_change(g, "add")
    return fn("Bag To Wardrobe", [param("name", "name")], graph=g)


def f_put_in_bag():
    g = G()
    bag = player_bag(g, "gb"); g.call("full", P_BAG, "Is Bag Full ?", inp={"self": bag}); g.branch("bfull", "@full.yes")
    pop(g, "pop", tt(g, "t", "Msg_BagFull"))
    g.get("gpl", "Player"); g.call("gc", P_JODI, "Got Clothes", inp={"self": "@gpl.Player", "clothes name": "@entry.name", "wear": "false"})
    g.get("gpg", "Page"); g.call("isb", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Bag"}); g.branch("bb", "@isb.ReturnValue")
    g.chain("entry", "bfull", "pop"); g.chain("bfull:else", "gc", "bb"); after_bag_change(g, "bb")
    return fn("Put In Bag", [param("name", "name")], graph=g)


# ---------------- Coiffure / Appearance / Body Shape ----------------
def make_item(g, id, name_pin, icon_pin, slot=None):
    """S_ClothesItem for non-clothes (hairstyle/skin/makeup): name, display name = name, icon; slot = origin for the content view (Hair / Skin / <type> / Body)."""
    g.call(id + "_n", K_STR, "Conv_NameToString", inp={"InName": name_pin})
    g.make(id, S_ITEM, Name=name_pin, DisplayName="@%s_n.ReturnValue" % id, Icon=icon_pin, **({"Slot": slot} if slot else {})); return "@%s.S_ClothesItem" % id


def look_tile(g, id, item_pin, selected_pin, owned_pin, add_fn, tip_pin):
    """Create W_ClothesButton + init + add to the panel; returns the exec chain. tip_pin = tooltip text (category caption)."""
    tw = create_widget(g, id, W_BTN); set_manager(g, id + "_sm", W_BTN, tw)
    g.call(id + "_i", W_BTN, "Init", inp={"self": tw, "item": item_pin, "worn": selected_pin, "owned": owned_pin, "fav": "false", "damaged": "false", "tip": tip_pin})
    g.get(id + "_gp", "Panel"); g.call(id + "_a", W_PANEL, add_fn, inp={"self": "@%s_gp.Panel" % id, "widget": tw})
    return [id + "_cr", id + "_sm", id + "_i", id + "_a"]


def game_instance(g, id):
    g.call(id + "_gi", K_GS, "GetGameInstance"); g.cast(id, P_GI, "@%s_gi.ReturnValue" % id); return "@%s.AsTKA Game Instance" % id


def hair_owned(g, id, name_pin, mirror_pin):
    """owned = in the GameInstance's Hairstyles set or MirrorID == -1"""
    gi = game_instance(g, id + "_g"); g.get(id + "_hs", "Hairstyles Save", cls=P_GI); g.link(id + "_g.AsTKA Game Instance", id + "_hs.self")
    g.get(id + "_set", "Hairstyles", cls=P_HAIR_SAVE); g.link(id + "_hs.Hairstyles Save", id + "_set.self")
    g.call(id + "_c", K_SET, "Set_Contains", inp={"TargetSet": "@%s_set.Hairstyles" % id, "ItemToFind": name_pin})
    g.call(id + "_m", K_MATH, "EqualEqual_IntInt", inp={"A": mirror_pin, "B": "-1"})
    g.call(id, K_MATH, "BooleanOR", inp={"A": "@%s_c.ReturnValue" % id, "B": "@%s_m.ReturnValue" % id}); return "@%s.ReturnValue" % id


def f_rebuild_hair():
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Hair", inp={"self": "@gp.Panel"})
    g.get("gp1", "Panel"); g.call("cll", W_PANEL, "Clear Hair Links", inp={"self": "@gp1.Panel"})
    lw = create_widget(g, "clk", W_TXT); set_manager(g, "sml", W_TXT, lw)
    g.call("li", W_TXT, "Init", inp={"self": lw, "action": "HairColor", "caption": tt(g, "lt", "Btn_HairColor")})
    g.get("gp2", "Panel"); g.call("al", W_PANEL, "Add Hair Link", inp={"self": "@gp2.Panel", "widget": lw})
    g.call("rn", K_DT, "GetDataTableRowNames", inp={"Table": P_HAIR_T}); g.set("sn", "TmpNames2", inp={"TmpNames2": "@rn.OutRowNames"})
    g.get("gpl", "Player"); g.call("cur", P_JODI, "Get Hairstyle Name", inp={"self": "@gpl.Player"}); g.set("scn", "TmpName2", inp={"TmpName2": "@cur.name"})
    g.get("gn", "TmpNames2"); g.foreach("fe", "@gn.TmpNames2")
    g.n("row", "get_row", table=P_HAIR_T, inp={"RowName": "@fe.Array Element"}, miss="ignore"); g.brk("br", P_HAIR_S, "@row.OutRow")   # row names of the same table
    owned = hair_owned(g, "own", "@fe.Array Element", "@br.MirrorID")
    item = make_item(g, "mi", "@fe.Array Element", "@br.icon")
    g.get("gcn", "TmpName2"); g.call("sel", K_MATH, "EqualEqual_NameName", inp={"A": "@fe.Array Element", "B": "@gcn.TmpName2"})
    tile = look_tile(g, "th", item, "@sel.ReturnValue", owned, "Add Hair", tt(g, "thtp", "Tab_Hair"))
    g.get("ghl", "HighlightItem"); g.call("ish", K_MATH, "EqualEqual_NameName", inp={"A": "@fe.Array Element", "B": "@ghl.HighlightItem"}); g.branch("bhl", "@ish.ReturnValue")   # scroll target of a "Show in tab" jump
    g.set("ssw", "ScrollWidget", inp={"ScrollWidget": "@th.AsW_ClothesButton"})
    g.chain("entry", "cl", "cll", "clk_cr", "sml", "li", "al", "rn", "sn", "scn", "fe"); g.chain("fe", "row", *tile, "bhl", "ssw")
    return fn("Rebuild Hair", graph=g)


def f_hair_clicked():
    g = G()
    g.n("row", "get_row", table=P_HAIR_T, inp={"RowName": "@entry.name"}, miss="ignore"); g.brk("br", P_HAIR_S, "@row.OutRow")   # unknown hairstyle -> nothing (no history entry yet)
    owned = hair_owned(g, "own", "@entry.name", "@br.MirrorID"); g.branch("bo", owned)
    pop(g, "pop", tt(g, "t", "Msg_HairLocked"))
    g.get("gpl", "Player"); g.call("ch", P_JODI, "Change Hairstyle", inp={"self": "@gpl.Player", "Hairstyle": "@entry.name"})
    g.get("gpl2", "Player"); g.call("sa", P_JODI, "Save Appearance", inp={"self": "@gpl2.Player"})
    g.set("sd", "MakeupDirty", inp={"MakeupDirty": "true"}); g.n("rh", "call_self", function="Rebuild Hair")
    g.n("ph", "call_self", function="Push History")
    g.chain("entry", "row", "bo", "ph", "ch", "sa", "sd", "rh"); g.chain("bo:else", "pop")
    return fn("Hair Clicked", [param("name", "name")], graph=g)


def f_look_caption():
    """Category caption: own key Look_<type> (presets, skin, all makeup types of the game), else MakeupTypeTable.Caption, else the type name."""
    g = G()
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.type"}); g.call("kc", K_STR, "Concat_StrStr", inp={"A": "Look_", "B": "@n2s.ReturnValue"}); g.call("kn", K_STR, "Conv_StringToName", inp={"InString": "@kc.ReturnValue"})
    g.get("gs", "Strings"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gs.Strings", "Key": "@kn.ReturnValue"}); g.branch("bf", "@f.ReturnValue")
    g.set("so", "TmpText", inp={"TmpText": "@f.Value"})
    g.n("row", "get_row", table=P_MTYPE_T, inp={"RowName": "@entry.type"}); g.brk("br", P_MTYPE_S, "@row.OutRow")
    g.call("emp", K_TXT, "TextIsEmpty", inp={"InText": "@br.Caption"}); g.branch("be", "@emp.ReturnValue")
    g.set("sc", "TmpText", inp={"TmpText": "@br.Caption"})
    g.call("nt", K_TXT, "Conv_NameToText", inp={"InName": "@entry.type"}); g.set("sn", "TmpText", inp={"TmpText": "@nt.ReturnValue"})
    g.get("gt", "TmpText"); g.link("gt.TmpText", "return.caption")
    g.chain("entry", "bf", "so", "return"); g.chain("bf:else", "row", "be", "sn", "return"); g.chain("be:else", "sc", "return"); g.chain("row:Row Not Found", "sn")
    return fn("Look Caption", [param("type", "name")], [param("caption", "text")], graph=g)


def makeup_data(g, id):
    g.get(id + "_p", "Player"); g.call(id, P_JODI, "Get Makeup Data", inp={"self": "@%s_p.Player" % id}); return "@%s.Makeup Data" % id


def f_is_look_selected():
    """Skin: Skin Name == style; otherwise: Makeup Data[type].List contains style"""
    g = G(); md = makeup_data(g, "md")
    g.call("iss", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.type", "B": "Skin"}); g.branch("bs", "@iss.ReturnValue")
    g.get("gsn", "Skin Name", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "gsn.self")
    g.call("eqs", K_MATH, "EqualEqual_NameName", inp={"A": "@gsn.Skin Name", "B": "@entry.style"}); g.set("r1", "TmpBool", inp={"TmpBool": "@eqs.ReturnValue"})
    g.get("gmd", "Makeup Data", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "gmd.self")
    g.call("fnd", K_MAP, "Map_Find", inp={"TargetMap": "@gmd.Makeup Data", "Key": "@entry.type"}); g.brk("bl", P_MDATA_S, "@fnd.Value")
    g.call("con", K_ARR, "Array_Contains", inp={"TargetArray": "@bl.List", "ItemToFind": "@entry.style"})
    g.call("and", K_MATH, "BooleanAND", inp={"A": "@fnd.ReturnValue", "B": "@con.ReturnValue"}); g.set("r2", "TmpBool", inp={"TmpBool": "@and.ReturnValue"})
    g.get("gr", "TmpBool"); g.link("gr.TmpBool", "return.yes")
    g.chain("entry", "md", "bs", "r1", "return"); g.chain("bs:else", "r2", "return")
    return fn("Is Look Selected", [param("type", "name"), param("style", "name")], [param("yes", "bool")], graph=g)


def f_look_count():
    """Number of entries of a category (skin: SkinTable; eye types: EyeTable; otherwise MakeupTable with Type == type)"""
    g = G(); g.set("z", "TmpIdx", inp={"TmpIdx": "0"})
    g.call("isp", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.type", "B": "Presets"}); g.branch("bp", "@isp.ReturnValue")
    pd = presets_data(g, "pd"); g.call("lp", K_ARR, "Array_Length", inp={"TargetArray": pd}); g.set("sp", "TmpIdx", inp={"TmpIdx": "@lp.ReturnValue"})
    g.call("iss", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.type", "B": "Skin"}); g.branch("bs", "@iss.ReturnValue")
    g.call("rs", K_DT, "GetDataTableRowNames", inp={"Table": P_SKIN_T}); g.call("ls", K_ARR, "Array_Length", inp={"TargetArray": "@rs.OutRowNames"}); g.set("ss", "TmpIdx", inp={"TmpIdx": "@ls.ReturnValue"})
    g.n("trow", "get_row", table=P_MTYPE_T, inp={"RowName": "@entry.type"}); g.brk("bt", P_MTYPE_S, "@trow.OutRow"); g.branch("be", "@bt.EyeTable")
    g.call("re", K_DT, "GetDataTableRowNames", inp={"Table": P_EYE_T}); g.set("sne", "TmpNames2", inp={"TmpNames2": "@re.OutRowNames"}); g.get("gne", "TmpNames2"); g.foreach("fe", "@gne.TmpNames2")
    g.n("erow", "get_row", table=P_EYE_T, inp={"RowName": "@fe.Array Element"}, miss="ignore"); g.brk("ber", P_EYE_S, "@erow.OutRow")
    g.call("eqe", K_MATH, "EqualEqual_NameName", inp={"A": "@ber.Type", "B": "@entry.type"}); g.branch("bqe", "@eqe.ReturnValue")
    g.get("gi1", "TmpIdx"); g.call("inc1", K_MATH, "Add_IntInt", inp={"A": "@gi1.TmpIdx", "B": "1"}); g.set("si1", "TmpIdx", inp={"TmpIdx": "@inc1.ReturnValue"})
    g.call("rm", K_DT, "GetDataTableRowNames", inp={"Table": P_MAKEUP_T}); g.set("snm", "TmpNames2", inp={"TmpNames2": "@rm.OutRowNames"}); g.get("gnm", "TmpNames2"); g.foreach("fm", "@gnm.TmpNames2")
    g.n("mrow", "get_row", table=P_MAKEUP_T, inp={"RowName": "@fm.Array Element"}, miss="ignore"); g.brk("bmr", P_MAKEUP_S, "@mrow.OutRow")
    g.call("eqm", K_MATH, "EqualEqual_NameName", inp={"A": "@bmr.Type", "B": "@entry.type"}); g.branch("bqm", "@eqm.ReturnValue")
    g.get("gi2", "TmpIdx"); g.call("inc2", K_MATH, "Add_IntInt", inp={"A": "@gi2.TmpIdx", "B": "1"}); g.set("si2", "TmpIdx", inp={"TmpIdx": "@inc2.ReturnValue"})
    g.get("gr", "TmpIdx"); g.link("gr.TmpIdx", "return.n")
    g.chain("entry", "z", "bp", "sp", "return"); g.chain("bp:else", "bs", "rs", "ss", "return"); g.chain("bs:else", "trow", "be", "re", "sne", "fe"); g.chain("fe", "erow", "bqe", "si1"); g.chain("fe:Completed", "return")
    g.chain("be:else", "rm", "snm", "fm"); g.chain("fm", "mrow", "bqm", "si2"); g.chain("fm:Completed", "return"); g.chain("trow:Row Not Found", "return")
    return fn("Look Count", [param("type", "name")], [param("n", "int")], graph=g)


def f_rebuild_look_cats():
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Look Cats", inp={"self": "@gp.Panel"})
    g.call("rn", K_DT, "GetDataTableRowNames", inp={"Table": P_MTYPE_T}); g.set("sn", "TmpNames", inp={"TmpNames": "@rn.OutRowNames"})
    g.get("gn0", "TmpNames"); g.call("ins", K_ARR, "Array_Insert", inp={"TargetArray": "@gn0.TmpNames", "NewItem": g.lit_name("skin", "Skin"), "Index": "0"})
    g.get("gn9", "TmpNames"); g.call("adp", K_ARR, "Array_Add", inp={"TargetArray": "@gn9.TmpNames", "NewItem": g.lit_name("prs", "Presets")})
    g.get("gn", "TmpNames"); g.foreach("fe", "@gn.TmpNames")
    tw = create_widget(g, "ct", W_TAB); set_manager(g, "smt", W_TAB, tw)
    g.n("cap", "call_self", function="Look Caption", inp={"type": "@fe.Array Element"}); g.n("cnt", "call_self", function="Look Count", inp={"type": "@fe.Array Element"})
    g.call("has", K_MATH, "Greater_IntInt", inp={"A": "@cnt.n", "B": "0"})
    g.get("glc", "LookCat"); g.call("sel", K_MATH, "EqualEqual_NameName", inp={"A": "@fe.Array Element", "B": "@glc.LookCat"})
    g.call("ti", W_TAB, "Init", inp={"self": tw, "slot": "@fe.Array Element", "caption": "@cap.caption", "count": "@cnt.n", "selected": "@sel.ReturnValue", "has items": "@has.ReturnValue"})
    g.get("gp3", "Panel"); g.call("at", W_PANEL, "Add Look Cat", inp={"self": "@gp3.Panel", "widget": tw})
    g.chain("entry", "cl", "rn", "sn", "ins", "adp", "fe"); g.chain("fe", "ct_cr", "smt", "cap", "cnt", "ti", "at")
    return fn("Rebuild Look Cats", graph=g)


def f_select_look_cat():
    g = G(); g.set("s", "LookCat", inp={"LookCat": "@entry.name"}); g.n("rc", "call_self", function="Rebuild Look Cats"); g.n("rl", "call_self", function="Rebuild Look")
    g.n("uf", "call_self", function="Update Focus"); g.set("hlc", "HighlightItem", inp={"HighlightItem": "None"})
    g.chain("entry", "hlc", "s", "rc", "rl", "uf"); return fn("Select Look Cat", [param("name", "name")], graph=g)


def f_rebuild_look():
    g = G()
    g.get("glc7", "LookCat"); g.n("lcp", "call_self", function="Look Caption", inp={"type": "@glc7.LookCat"})   # tooltip of every tile on this page
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Look", inp={"self": "@gp.Panel"})
    # presets: "+" tile (outfit widget) + one tile per preset with its icon file
    g.get("glc0", "LookCat"); g.call("isp", K_MATH, "EqualEqual_NameName", inp={"A": "@glc0.LookCat", "B": "Presets"}); g.branch("bp", "@isp.ReturnValue")
    g.get("gi0", "TmpIcons"); g.call("clr0", K_ARR, "Array_Clear", inp={"TargetArray": "@gi0.TmpIcons"})
    pw = create_widget(g, "cpa", W_OUTFIT); set_manager(g, "smpa", W_OUTFIT, pw)
    g.get("gi1", "TmpIcons"); g.call("pai", W_OUTFIT, "Init", inp={"self": pw, "index": "-1", "icons": "@gi1.TmpIcons", "count": "0", "caption": tt(g, "pct", "Btn_SavePreset")})
    g.get("gpa", "Panel"); g.call("paa", W_PANEL, "Add Look", inp={"self": "@gpa.Panel", "widget": pw})
    pd = presets_data(g, "pd"); g.foreach("fp", pd); g.brk("bpr", P_PRESET_S, "@fp.Array Element")
    g.n("pic", "call_self", function="Preset Icon", inp={"number": "@bpr.IconNumber"})
    g.call("pis", K_STR, "Conv_IntToString", inp={"InInt": "@fp.Array Index"}); g.call("pn1", K_STR, "Concat_StrStr", inp={"A": "Preset_", "B": "@pis.ReturnValue"}); g.call("pnn", K_STR, "Conv_StringToName", inp={"InString": "@pn1.ReturnValue"})
    g.call("pi1", K_MATH, "Add_IntInt", inp={"A": "@fp.Array Index", "B": "1"}); g.call("pi1s", K_STR, "Conv_IntToString", inp={"InInt": "@pi1.ReturnValue"}); g.call("pdn", K_STR, "Concat_StrStr", inp={"A": "Preset ", "B": "@pi1s.ReturnValue"})
    g.make("mip", S_ITEM, Name="@pnn.ReturnValue", DisplayName="@pdn.ReturnValue", Icon="@pic.tex")
    tp = look_tile(g, "tp", "@mip.S_ClothesItem", "false", "true", "Add Look", "@lcp.caption")
    g.get("glc", "LookCat"); g.call("iss", K_MATH, "EqualEqual_NameName", inp={"A": "@glc.LookCat", "B": "Skin"}); g.branch("bs", "@iss.ReturnValue")
    # skin
    g.call("rs", K_DT, "GetDataTableRowNames", inp={"Table": P_SKIN_T}); g.set("sns", "TmpNames2", inp={"TmpNames2": "@rs.OutRowNames"}); g.get("gns", "TmpNames2"); g.foreach("fs", "@gns.TmpNames2")
    g.n("srow", "get_row", table=P_SKIN_T, inp={"RowName": "@fs.Array Element"}, miss="ignore"); g.brk("bsr", P_SKIN_S, "@srow.OutRow")
    g.get("glc1", "LookCat"); g.n("sel1", "call_self", function="Is Look Selected", inp={"type": "@glc1.LookCat", "style": "@fs.Array Element"})
    t1 = look_tile(g, "ts", make_item(g, "mis", "@fs.Array Element", "@bsr.icon"), "@sel1.yes", "true", "Add Look", "@lcp.caption")
    # type: eye table or makeup table
    g.get("glc2", "LookCat"); g.n("trow", "get_row", table=P_MTYPE_T, inp={"RowName": "@glc2.LookCat"}, miss="ignore"); g.brk("bt", P_MTYPE_S, "@trow.OutRow"); g.branch("be", "@bt.EyeTable")   # unknown category -> empty page
    g.call("re", K_DT, "GetDataTableRowNames", inp={"Table": P_EYE_T}); g.set("sne", "TmpNames2", inp={"TmpNames2": "@re.OutRowNames"}); g.get("gne", "TmpNames2"); g.foreach("fe", "@gne.TmpNames2")
    g.n("erow", "get_row", table=P_EYE_T, inp={"RowName": "@fe.Array Element"}, miss="ignore"); g.brk("ber", P_EYE_S, "@erow.OutRow")
    g.get("glc3", "LookCat"); g.call("eqe", K_MATH, "EqualEqual_NameName", inp={"A": "@ber.Type", "B": "@glc3.LookCat"}); g.branch("bqe", "@eqe.ReturnValue")
    g.get("glc4", "LookCat"); g.n("sel2", "call_self", function="Is Look Selected", inp={"type": "@glc4.LookCat", "style": "@fe.Array Element"})
    t2 = look_tile(g, "te", make_item(g, "mie", "@fe.Array Element", "@ber.Icon"), "@sel2.yes", "true", "Add Look", "@lcp.caption")
    g.call("rm", K_DT, "GetDataTableRowNames", inp={"Table": P_MAKEUP_T}); g.set("snm", "TmpNames2", inp={"TmpNames2": "@rm.OutRowNames"}); g.get("gnm", "TmpNames2"); g.foreach("fm", "@gnm.TmpNames2")
    g.n("mrow", "get_row", table=P_MAKEUP_T, inp={"RowName": "@fm.Array Element"}, miss="ignore"); g.brk("bmr", P_MAKEUP_S, "@mrow.OutRow")
    g.get("glc5", "LookCat"); g.call("eqm", K_MATH, "EqualEqual_NameName", inp={"A": "@bmr.Type", "B": "@glc5.LookCat"}); g.branch("bqm", "@eqm.ReturnValue")
    g.get("glc6", "LookCat"); g.n("sel3", "call_self", function="Is Look Selected", inp={"type": "@glc6.LookCat", "style": "@fm.Array Element"})
    t3 = look_tile(g, "tm", make_item(g, "mim", "@fm.Array Element", "@bmr.Icon"), "@sel3.yes", "true", "Add Look", "@lcp.caption")
    for tid, elem in (("ts", "@fs.Array Element"), ("te", "@fe.Array Element"), ("tm", "@fm.Array Element")):   # scroll target of a "Show in tab" jump
        g.get("hl_" + tid, "HighlightItem"); g.call("eq_" + tid, K_MATH, "EqualEqual_NameName", inp={"A": elem, "B": "@hl_%s.HighlightItem" % tid}); g.branch("b_" + tid, "@eq_%s.ReturnValue" % tid)
        g.set("sw_" + tid, "ScrollWidget", inp={"ScrollWidget": "@%s.AsW_ClothesButton" % tid})
    g.chain("entry", "cl", "lcp", "bp", "clr0", "cpa_cr", "smpa", "pai", "paa", "fp"); g.chain("fp", "pic", *tp); g.chain("bp:else", "bs", "rs", "sns", "fs"); g.chain("fs", "srow", "sel1", *t1, "b_ts", "sw_ts")
    g.chain("bs:else", "trow", "be", "re", "sne", "fe"); g.chain("fe", "erow", "bqe", "sel2", *t2, "b_te", "sw_te")
    g.chain("be:else", "rm", "snm", "fm"); g.chain("fm", "mrow", "bqm", "sel3", *t3, "b_tm", "sw_tm")
    return fn("Rebuild Look", graph=g)


def f_look_clicked():
    """Vanilla logic (AppearancePanel.On Makeup/Eye/Skin Button Clicked) without camera moves."""
    g = G(); md = makeup_data(g, "md")
    g.get("glc0", "LookCat"); g.call("isp", K_MATH, "EqualEqual_NameName", inp={"A": "@glc0.LookCat", "B": "Presets"}); g.branch("bp", "@isp.ReturnValue")
    g.n("pix", "call_self", function="Preset Index", inp={"name": "@entry.name"}); g.n("pcl", "call_self", function="Preset Clicked", inp={"index": "@pix.index"})
    g.get("glc", "LookCat"); g.call("iss", K_MATH, "EqualEqual_NameName", inp={"A": "@glc.LookCat", "B": "Skin"}); g.branch("bs", "@iss.ReturnValue")
    g.get("gpl", "Player"); g.call("cs", P_JODI, "Change Skin", inp={"self": "@gpl.Player", "SkinName": "@entry.name"})
    # type info
    g.get("glc2", "LookCat"); g.n("trow", "get_row", table=P_MTYPE_T, inp={"RowName": "@glc2.LookCat"}, miss="ignore"); g.brk("bt", P_MTYPE_S, "@trow.OutRow")   # unknown category -> nothing (no history entry)
    g.n("ph2", "call_self", function="Push History")
    g.get("glc3", "LookCat"); g.n("sel", "call_self", function="Is Look Selected", inp={"type": "@glc3.LookCat", "style": "@entry.name"})
    g.get("gmd", "Makeup Data", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "gmd.self")
    g.branch("be", "@bt.EyeTable")
    # --- eyes: selected -> remove the entry, else set it; Update Eyes Style
    g.branch("bes", "@sel.yes")
    g.get("glc4", "LookCat"); g.call("erm", K_MAP, "Map_Remove", inp={"TargetMap": "@gmd.Makeup Data", "Key": "@glc4.LookCat"})
    g.get("gn0", "TmpNames2"); g.call("eclr", K_ARR, "Array_Clear", inp={"TargetArray": "@gn0.TmpNames2"})
    g.get("gn1", "TmpNames2"); g.call("eadd", K_ARR, "Array_Add", inp={"TargetArray": "@gn1.TmpNames2", "NewItem": "@entry.name"})
    g.get("gn2", "TmpNames2"); g.make("ems", P_MDATA_S, List="@gn2.TmpNames2")
    g.get("glc5", "LookCat"); g.call("eset", K_MAP, "Map_Add", inp={"TargetMap": "@gmd.Makeup Data", "Key": "@glc5.LookCat", "Value": "@ems.MakeupDataStruct"})
    g.get("gpl2", "Player"); g.call("ues", P_JODI, "Update Eyes Style", inp={"self": "@gpl2.Player"})
    # --- makeup: fetch the type's list (empty if no entry)
    g.get("glc6", "LookCat"); g.call("fnd", K_MAP, "Map_Find", inp={"TargetMap": "@gmd.Makeup Data", "Key": "@glc6.LookCat"}); g.brk("bl", P_MDATA_S, "@fnd.Value")
    g.set("sl", "TmpNames2", inp={"TmpNames2": "@bl.List"})
    g.branch("bms", "@sel.yes")
    #    selected: remove (Eyebrow can never be deselected)
    g.get("glc7", "LookCat"); g.call("iseb", K_MATH, "EqualEqual_NameName", inp={"A": "@glc7.LookCat", "B": "Eyebrow"}); g.branch("beb", "@iseb.ReturnValue")
    g.get("gn3", "TmpNames2"); g.call("mrm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gn3.TmpNames2", "Item": "@entry.name"})
    #    not selected: Single -> replace, else append
    g.branch("bsg", "@bt.Single")
    g.get("gn4", "TmpNames2"); g.call("mclr", K_ARR, "Array_Clear", inp={"TargetArray": "@gn4.TmpNames2"})
    g.get("gn5", "TmpNames2"); g.call("madd", K_ARR, "Array_Add", inp={"TargetArray": "@gn5.TmpNames2", "NewItem": "@entry.name"})
    #    write back
    g.get("gn6", "TmpNames2"); g.call("mlen", K_ARR, "Array_Length", inp={"TargetArray": "@gn6.TmpNames2"}); g.call("gt0", K_MATH, "Greater_IntInt", inp={"A": "@mlen.ReturnValue", "B": "0"}); g.branch("bgt", "@gt0.ReturnValue")
    g.get("gn7", "TmpNames2"); g.make("mms", P_MDATA_S, List="@gn7.TmpNames2")
    g.get("glc8", "LookCat"); g.call("mset", K_MAP, "Map_Add", inp={"TargetMap": "@gmd.Makeup Data", "Key": "@glc8.LookCat", "Value": "@mms.MakeupDataStruct"})
    g.get("glc9", "LookCat"); g.call("mrem", K_MAP, "Map_Remove", inp={"TargetMap": "@gmd.Makeup Data", "Key": "@glc9.LookCat"})
    #    animation (style, else type) + texture
    g.n("srow", "get_row", table=P_MAKEUP_T, inp={"RowName": "@entry.name"}); g.brk("bsr", P_MAKEUP_S, "@srow.OutRow")
    g.call("anN", K_MATH, "EqualEqual_NameName", inp={"A": "@bsr.Animation", "B": "None"})
    g.call("anT", K_STR, "Conv_NameToString", inp={"InName": "@bt.Animation"}); g.call("anS", K_STR, "Conv_NameToString", inp={"InName": "@bsr.Animation"})
    g.call("ani", K_MATH, "SelectString", inp={"A": "@anT.ReturnValue", "B": "@anS.ReturnValue", "bPickA": "@anN.ReturnValue"}); g.call("anin", K_STR, "Conv_StringToName", inp={"InString": "@ani.ReturnValue"})
    g.call("anN2", K_MATH, "NotEqual_NameName", inp={"A": "@anin.ReturnValue", "B": "None"}); g.branch("ban", "@anN2.ReturnValue")
    g.get("gpl3", "Player"); g.call("pm", P_JODI, "Play Montage With Name", inp={"self": "@gpl3.Player", "montage name": "@anin.ReturnValue", "ignore when the montage playing": "true"})
    g.get("gpl4", "Player"); g.call("umt", P_JODI, "Update Makeup Texture", inp={"self": "@gpl4.Player"})
    # finish
    g.set("sd", "MakeupDirty", inp={"MakeupDirty": "true"}); g.n("rl", "call_self", function="Rebuild Look")
    g.n("ph", "call_self", function="Push History")
    g.chain("entry", "bp", "pix", "pcl"); g.chain("bp:else", "md", "bs", "ph", "cs", "sd"); g.chain("bs:else", "trow", "ph2", "sel", "be", "bes", "erm", "ues"); g.chain("bes:else", "eclr", "eadd", "eset", "ues"); g.chain("ues", "sd")
    g.chain("be:else", "sl", "bms", "beb", "sd"); g.chain("beb:else", "mrm", "bgt"); g.chain("bms:else", "bsg", "mclr", "madd", "bgt"); g.chain("bsg:else", "madd")
    g.chain("bgt", "mset", "srow"); g.chain("bgt:else", "mrem", "srow"); g.chain("srow", "ban", "pm", "umt"); g.chain("ban:else", "umt"); g.chain("srow:Row Not Found", "umt"); g.chain("umt", "sd"); g.chain("sd", "rl")
    return fn("Look Clicked", [param("name", "name")], graph=g)


def f_rebuild_body():
    g = G(); md = makeup_data(g, "md")
    g.get("gb", "Boobs Size", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "gb.self")
    g.get("gw", "Waist", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "gw.self")
    g.set("cb", "BodyBreast", inp={"BodyBreast": "@gb.Boobs Size"}); g.set("cw", "BodyWaist", inp={"BodyWaist": "@gw.Waist"})
    g.get("gp", "Panel"); g.call("sv", W_PANEL, "Set Body Values", inp={"self": "@gp.Panel", "breast": "@gb.Boobs Size", "waist": "@gw.Waist"})
    # body chips: "Standard" + one per body mod (caption from the mod table), active = CurrentBody (None = Standard)
    g.n("scan", "call_self", function="Scan Body Mods")
    g.get("gp2", "Panel"); g.call("cl", W_PANEL, "Clear Body Chips", inp={"self": "@gp2.Panel"})
    sw = create_widget(g, "cs", W_SUB); set_manager(g, "sms", W_SUB, sw)
    g.get("gcb", "CurrentBody"); g.call("sel0", K_MATH, "EqualEqual_NameName", inp={"A": "@gcb.CurrentBody", "B": "None"})
    g.call("i0", W_SUB, "Init", inp={"self": sw, "group": "BodyStd", "caption": tt(g, "t0", "Chip_Standard"), "selected": "@sel0.ReturnValue"})
    g.get("gp3", "Panel"); g.call("a0", W_PANEL, "Add Body Chip", inp={"self": "@gp3.Panel", "widget": sw})
    g.get("gbm", "BodyMods"); g.foreach("fe", "@gbm.BodyMods")
    mw = create_widget(g, "cm", W_SUB); set_manager(g, "smm", W_SUB, mw)
    g.get("gcp", "BodyCaptions"); g.call("cap", K_MAP, "Map_Find", inp={"TargetMap": "@gcp.BodyCaptions", "Key": "@fe.Array Element"})
    g.get("gcb2", "CurrentBody"); g.call("sel1", K_MATH, "EqualEqual_NameName", inp={"A": "@gcb2.CurrentBody", "B": "@fe.Array Element"})
    g.call("i1", W_SUB, "Init", inp={"self": mw, "group": "@fe.Array Element", "caption": "@cap.Value", "selected": "@sel1.ReturnValue"})
    g.get("gp4", "Panel"); g.call("a1", W_PANEL, "Add Body Chip", inp={"self": "@gp4.Panel", "widget": mw})
    g.chain("entry", "md", "cb", "cw", "sv", "scan", "cl", "cs_cr", "sms", "i0", "a0", "fe"); g.chain("fe", "cm_cr", "smm", "i1", "a1")
    return fn("Rebuild Body", graph=g)


def f_poll_body():
    """Tick on the body page: read the sliders, write to Makeup Data on change (vanilla: slider -> Boobs Size / Waist)."""
    g = G()
    g.get("gp", "Panel"); g.call("gv", W_PANEL, "Get Body Values", inp={"self": "@gp.Panel"})
    g.get("cb", "BodyBreast"); g.get("cw", "BodyWaist")
    g.call("nb", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.breast", "B": "@cb.BodyBreast", "ErrorTolerance": "0.0001"})
    g.call("nw", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.waist", "B": "@cw.BodyWaist", "ErrorTolerance": "0.0001"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@nb.ReturnValue", "B": "@nw.ReturnValue"})
    g.branch("bsame", "@a1.ReturnValue")
    md = makeup_data(g, "md")
    g.n("sb", "set", var="Boobs Size", cls=P_MAKEUP_SAVE, inp={"self": md, "Boobs Size": "@gv.breast"})
    g.n("sw", "set", var="Waist", cls=P_MAKEUP_SAVE, inp={"self": md, "Waist": "@gv.waist"})
    g.call("nbn", K_MATH, "Not_PreBool", inp={"A": "@nb.ReturnValue"}); g.get("gbc", "BoobsChanged"); g.call("or", K_MATH, "BooleanOR", inp={"A": "@gbc.BoobsChanged", "B": "@nbn.ReturnValue"})
    g.set("sbc", "BoobsChanged", inp={"BoobsChanged": "@or.ReturnValue"}); g.set("sd", "MakeupDirty", inp={"MakeupDirty": "true"})
    g.set("cb2", "BodyBreast", inp={"BodyBreast": "@gv.breast"}); g.set("cw2", "BodyWaist", inp={"BodyWaist": "@gv.waist"})
    g.get("gp2", "Panel"); g.call("sv", W_PANEL, "Set Body Values", inp={"self": "@gp2.Panel", "breast": "@gv.breast", "waist": "@gv.waist"})
    g.chain("entry", "gv", "bsame"); g.chain("bsame:else", "md", "sb", "sw", "sbc", "sd", "cb2", "cw2", "sv")
    return fn("Poll Body", graph=g)


def f_save_appearance_data():
    """On close: save makeup/hairstyle/body (vanilla: Save Makeup Data to File), breast changed -> Reset Clothes Physics."""
    g = G()
    g.get("gd", "MakeupDirty"); g.branch("bd", "@gd.MakeupDirty")
    g.get("gpl", "Player"); g.call("sv", P_JODI, "Save Makeup Data to File", inp={"self": "@gpl.Player"}); g.set("sd", "MakeupDirty", inp={"MakeupDirty": "false"})
    g.get("gb", "BoobsChanged"); g.branch("bb", "@gb.BoobsChanged")
    g.get("gpl2", "Player"); g.call("rp", P_CPB, "Reset Clothes Physics", inp={"self": "@gpl2.Player"}); g.set("sb", "BoobsChanged", inp={"BoobsChanged": "false"})
    g.chain("entry", "bd", "sv", "sd", "bb", "rp", "sb"); g.chain("bd:else", "bb")
    return fn("Save Appearance Data", graph=g)


def f_delete_outfit():
    """Remove the outfit and its assigned name (Set Outfit Name By Key with "" drops the entry; the key must be read before the removal)."""
    g = G()
    g.n("ok", "call_self", function="Outfit Key", inp={"index": "@entry.index"}); g.n("sn", "call_self", function="Set Outfit Name By Key", inp={"key": "@ok.key", "name": ""})
    g.get("go", "Outfits"); g.get("goa", "outfits", cls=P_OUTFITS); g.link("go.Outfits", "goa.self")
    g.call("rm", K_ARR, "Array_Remove", inp={"TargetArray": "@goa.outfits", "IndexToRemove": "@entry.index"})
    g.n("sv", "call_self", function="Save Outfits"); g.n("ro", "call_self", function="Rebuild Outfits")
    g.chain("entry", "ok", "sn", "rm", "sv", "ro")
    return fn("Delete Outfit", [param("index", "int")], graph=g)


def f_start_outfit_rename():
    """Context menu 'Rename': open the text field on the last clicked tile (LastButton)."""
    g = G()
    g.n("on", "call_self", function="Outfit Name", inp={"index": "@entry.index"})
    g.get("glb", "LastButton"); g.cast("cb", W_OUTFIT, "@glb.LastButton"); g.call("cv", K_SYS, "IsValid", inp={"Object": "@cb.AsW_OutfitButton"}); g.branch("bv", "@cv.ReturnValue")
    g.call("br", W_OUTFIT, "Begin Rename", inp={"self": "@cb.AsW_OutfitButton", "current": "@on.name"})
    g.chain("entry", "bv", "on", "br")
    return fn("Start Outfit Rename", [param("index", "int")], graph=g)


def f_join_names():
    """Join the clothes names in map order with '|' (key for OutfitNames)."""
    g = G()
    g.get("gs0", "TmpStrings"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gs0.TmpStrings"})
    g.foreach("fe", "@entry.names"); g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@fe.Array Element"})
    g.get("gs1", "TmpStrings"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gs1.TmpStrings", "NewItem": "@n2s.ReturnValue"})
    g.get("gs2", "TmpStrings"); g.call("join", K_STR, "JoinStringArray", inp={"SourceArray": "@gs2.TmpStrings", "Separator": "|"}); g.link("join.ReturnValue", "return.key")
    g.chain("entry", "clr", "fe"); g.chain("fe", "add"); g.chain("fe:Completed", "return")
    return fn("Join Names", [param("names", "name", "array")], [param("key", "string")], graph=g)


def f_outfit_key():
    g = G()
    g.get("go", "Outfits"); g.get("goa", "outfits", cls=P_OUTFITS); g.link("go.Outfits", "goa.self")
    g.call("get", K_ARR, "Array_Get", inp={"TargetArray": "@goa.outfits", "Index": "@entry.index"}); g.brk("bo", P_OUTFIT_S, "@get.Item")
    g.call("keys", K_MAP, "Map_Keys", inp={"TargetMap": "@bo." + OUTFIT_MEMBER})
    g.n("jn", "call_self", function="Join Names", inp={"names": "@keys.Keys"}); g.link("jn.key", "return.key")
    g.chain("entry", "keys", "jn", "return")
    return fn("Outfit Key", [param("index", "int")], [param("key", "string")], graph=g)


def f_outfit_name_by_key():
    g = G()
    g.get("gs", "Settings"); g.get("gm", "OutfitNames", cls=SG); g.link("gs.Settings", "gm.self")
    g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gm.OutfitNames", "Key": "@entry.key"}); g.branch("b", "@f.ReturnValue")
    g.set("s1", "TmpStr2", inp={"TmpStr2": "@f.Value"}); g.set("s2", "TmpStr2", inp={"TmpStr2": ""})
    g.get("gt", "TmpStr2"); g.link("gt.TmpStr2", "return.name")
    g.chain("entry", "b", "s1", "return"); g.chain("b:else", "s2", "return")
    return fn("Outfit Name By Key", [param("key", "string")], [param("name", "string")], graph=g)


def f_outfit_name():
    g = G()
    g.n("ok", "call_self", function="Outfit Key", inp={"index": "@entry.index"})
    g.n("nm", "call_self", function="Outfit Name By Key", inp={"key": "@ok.key"}); g.link("nm.name", "return.name")
    g.chain("entry", "ok", "nm", "return")
    return fn("Outfit Name", [param("index", "int")], [param("name", "string")], graph=g)


def f_set_outfit_name_by_key():
    """Trim the name, cut to 40 characters; empty -> remove the entry; save."""
    g = G()
    g.call("t1", K_STR, "Trim", inp={"SourceString": "@entry.name"}); g.call("t2", K_STR, "TrimTrailing", inp={"SourceString": "@t1.ReturnValue"})
    g.call("cut", K_STR, "Left", inp={"SourceString": "@t2.ReturnValue", "Count": "40"}); g.set("st", "TmpStr2", inp={"TmpStr2": "@cut.ReturnValue"})
    g.get("gt", "TmpStr2"); g.call("len", K_STR, "Len", inp={"S": "@gt.TmpStr2"}); g.call("emp", K_MATH, "EqualEqual_IntInt", inp={"A": "@len.ReturnValue", "B": "0"}); g.branch("b", "@emp.ReturnValue")
    g.get("gs", "Settings"); g.get("gm", "OutfitNames", cls=SG); g.link("gs.Settings", "gm.self")
    g.call("rm", K_MAP, "Map_Remove", inp={"TargetMap": "@gm.OutfitNames", "Key": "@entry.key"})
    g.get("gs2", "Settings"); g.get("gm2", "OutfitNames", cls=SG); g.link("gs2.Settings", "gm2.self"); g.get("gt2", "TmpStr2")
    g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gm2.OutfitNames", "Key": "@entry.key", "Value": "@gt2.TmpStr2"})
    g.n("sv", "call_self", function="Save Settings")
    g.chain("entry", "st", "b", "rm", "sv"); g.chain("b:else", "add", "sv")
    return fn("Set Outfit Name By Key", [param("key", "string"), param("name", "string")], graph=g)


def f_set_outfit_name():
    g = G()
    g.n("ok", "call_self", function="Outfit Key", inp={"index": "@entry.index"})
    g.n("sn", "call_self", function="Set Outfit Name By Key", inp={"key": "@ok.key", "name": "@entry.name"})
    g.n("ro", "call_self", function="Rebuild Outfits")
    g.chain("entry", "ok", "sn", "ro")
    return fn("Set Outfit Name", [param("index", "int"), param("name", "string")], graph=g)


def f_select_subtab():
    g = G(); g.set("s", "CurrentGroup", inp={"CurrentGroup": "@entry.name"}); g.n("rt", "call_self", function="Rebuild SubTabs"); g.n("rli", "call_self", function="Rebuild List")
    g.get("gpg", "Page"); g.call("iso", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Options"}); g.branch("bo", "@iso.ReturnValue")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"}); g.call("isl", K_STR, "StartsWith", inp={"SourceString": "@n2s.ReturnValue", "InPrefix": "Lang", "SearchCase": "CaseSensitive"}); g.branch("bl", "@isl.ReturnValue")
    g.call("sub", K_STR, "GetSubstring", inp={"SourceString": "@n2s.ReturnValue", "StartIndex": "4", "Length": "1"}); g.call("s2i", K_STR, "Conv_StringToInt", inp={"InString": "@sub.ReturnValue"})
    g.n("slg", "call_self", function="Select Language", inp={"choice": "@s2i.ReturnValue"})
    g.call("isk", K_STR, "StartsWith", inp={"SourceString": "@n2s.ReturnValue", "InPrefix": "Key", "SearchCase": "CaseSensitive"}); g.branch("bk", "@isk.ReturnValue")
    g.n("sk", "call_self", function="Select Key", inp={"name": "@entry.name"})
    g.n("sl", "call_self", function="Select Layout", inp={"name": "@entry.name"})
    g.get("gpg2", "Page"); g.call("isb", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg2.Page", "B": "Body"}); g.branch("bb", "@isb.ReturnValue")
    g.n("sb", "call_self", function="Select Body", inp={"name": "@entry.name"})
    g.set("hlc", "HighlightItem", inp={"HighlightItem": "None"})
    g.call("ism", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "AltUI_More"})
    g.get("gpg3", "Page"); g.call("isc", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg3.Page", "B": "Clothes"})
    g.call("mok", K_MATH, "BooleanAND", inp={"A": "@ism.ReturnValue", "B": "@isc.ReturnValue"}); g.branch("bm", "@mok.ReturnValue")
    g.get("gcol", "SubTabsCollapsed"); g.call("ncol", K_MATH, "Not_PreBool", inp={"A": "@gcol.SubTabsCollapsed"}); g.set("scol", "SubTabsCollapsed", inp={"SubTabsCollapsed": "@ncol.ReturnValue"})
    g.n("svm", "call_self", function="Save Settings"); g.n("rtm", "call_self", function="Rebuild SubTabs")
    g.chain("entry", "bo", "bl", "slg"); g.chain("bl:else", "bk", "sk"); g.chain("bk:else", "sl"); g.chain("bo:else", "bb", "sb"); g.chain("bb:else", "bm", "scol", "svm", "rtm"); g.chain("bm:else", "hlc", "s", "rt", "rli")
    return fn("Select SubTab", [param("name", "name")], graph=g)


def f_select_key():
    """Options chip "Key<X>": ToggleKey = X, save, redraw the chips."""
    g = G(); g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"})
    g.call("sub", K_STR, "GetSubstring", inp={"SourceString": "@n2s.ReturnValue", "StartIndex": "3", "Length": "8"}); g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@sub.ReturnValue"})
    g.set("s", "ToggleKey", inp={"ToggleKey": "@s2n.ReturnValue"}); g.n("sv", "call_self", function="Save Settings"); g.n("ro", "call_self", function="Rebuild Options")
    g.chain("entry", "s", "sv", "ro"); return fn("Select Key", [param("name", "name")], graph=g)


def f_on_search_changed():
    g = G(); g.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@entry.text"})
    g.get("gst", "SearchText"); g.call("neq", K_STR, "NotEqual_StrStr", inp={"A": "@t2s.ReturnValue", "B": "@gst.SearchText"}); g.branch("b", "@neq.ReturnValue")
    g.set("s", "SearchText", inp={"SearchText": "@t2s.ReturnValue"}); g.n("rl", "call_self", function="Rebuild Left"); g.n("rli", "call_self", function="Rebuild List"); g.set("hlc", "HighlightItem", inp={"HighlightItem": "None"})
    g.chain("entry", "b", "hlc", "s", "rl", "rli"); return fn("On Search Changed", [param("text", "text")], graph=g)


def f_open_color():
    """Open the vanilla palette (PaletteUI.Show Palette) for the piece; the colour is read from Paletter.Image_Color on Tick."""
    g = G()
    g.set("sci", "ColorItem", inp={"ColorItem": "@entry.name"}); g.set("scm", "ColorMode", inp={"ColorMode": "Clothes"})
    g.get("gpl", "Player"); g.call("gc", P_CPB, "Get Clothes Color", inp={"self": "@gpl.Player", "clothes name": "@entry.name"})
    g.call("col", K_MATH, "SelectColor", inp={"A": "@gc.color", "B": "(R=1,G=1,B=1,A=1)", "bPickA": "@gc.found"})
    g.set("so", "ColorOrig", inp={"ColorOrig": "@col.ReturnValue"}); g.set("sc", "ColorCur", inp={"ColorCur": "@col.ReturnValue"})
    g.get("gp", "Palette"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gp.Palette"}); g.branch("b", "@iv.ReturnValue")
    pw = create_widget(g, "cp", P_PAL); g.set("sp", "Palette", inp={"Palette": pw})
    g.get("gp2", "Palette"); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@gp2.Palette", "ZOrder": "115"})
    g.get("gp3", "Palette"); g.get("gpn", "Panel"); g.get("glb", "LastButton")
    g.call("show", P_PAL, "Show Palette", inp={"self": "@gp3.Palette", "panel": "@gpn.Panel", "button": "@glb.LastButton", "flag": "0", "initial color": "@col.ReturnValue"})
    g.set("sop", "ColorOpen", inp={"ColorOpen": "true"})
    g.chain("entry", "sci", "scm", "gc", "so", "sc", "b", "atv"); g.chain("b:else", "cp_cr", "sp", "atv"); g.chain("atv", "show", "sop")
    return fn("Open Color", [param("name", "name")], graph=g)


def f_open_hair_color():
    """Vanilla palette (flag 1) for the hair colour; preview/save via Apply Preview with ColorMode=Hair."""
    g = G()
    g.set("scm", "ColorMode", inp={"ColorMode": "Hair"})
    g.get("gpl", "Player"); g.call("gc", P_JODI, "Get Hairstyle Color", inp={"self": "@gpl.Player"})
    g.set("so", "ColorOrig", inp={"ColorOrig": "@gc.color"}); g.set("sc", "ColorCur", inp={"ColorCur": "@gc.color"})
    g.get("gp", "Palette"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gp.Palette"}); g.branch("b", "@iv.ReturnValue")
    pw = create_widget(g, "cp", P_PAL); g.set("sp", "Palette", inp={"Palette": pw})
    g.get("gp2", "Palette"); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@gp2.Palette", "ZOrder": "115"})
    g.get("gp3", "Palette"); g.get("gpn", "Panel"); g.get("glb", "LastButton")
    g.call("show", P_PAL, "Show Palette", inp={"self": "@gp3.Palette", "panel": "@gpn.Panel", "button": "@glb.LastButton", "flag": "1", "initial color": "@gc.color"})
    g.set("sop", "ColorOpen", inp={"ColorOpen": "true"})
    g.chain("entry", "scm", "so", "sc", "b", "atv"); g.chain("b:else", "cp_cr", "sp", "atv"); g.chain("atv", "show", "sop")
    return fn("Open Hair Color", graph=g)


def f_open_theme_color():
    """Vanilla palette (flag 2) for a theme base colour; Apply Preview (ColorMode=Theme) writes Set Theme Color + Apply Theme live."""
    g = G()
    g.set("sci", "ColorItem", inp={"ColorItem": "@entry.key"}); g.set("scm", "ColorMode", inp={"ColorMode": "Theme"})
    g.n("gc", "call_self", function="Theme Color", inp={"key": "@entry.key"})
    g.set("so", "ColorOrig", inp={"ColorOrig": "@gc.color"}); g.set("sc", "ColorCur", inp={"ColorCur": "@gc.color"})
    g.get("gp", "Palette"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gp.Palette"}); g.branch("b", "@iv.ReturnValue")
    pw = create_widget(g, "cp", P_PAL); g.set("sp", "Palette", inp={"Palette": pw})
    g.get("gp2", "Palette"); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@gp2.Palette", "ZOrder": "115"})
    g.get("gp3", "Palette"); g.get("gpn", "Panel"); g.get("glb", "LastButton")
    g.call("show", P_PAL, "Show Palette", inp={"self": "@gp3.Palette", "panel": "@gpn.Panel", "button": "@glb.LastButton", "flag": "2", "initial color": "@gc.color"})
    g.set("sop", "ColorOpen", inp={"ColorOpen": "true"})
    g.chain("entry", "sci", "scm", "gc", "so", "sc", "b", "atv"); g.chain("b:else", "cp_cr", "sp", "atv"); g.chain("atv", "show", "sop")
    return fn("Open Theme Color", [param("key", "name")], graph=g)


def f_apply_theme():
    """Derived colours from the base colours (lighten towards white, darken, fixed alphas x TileAlpha), ThemeVersion + 1, panel-owned parts."""
    g = G(); tail = ["entry"]
    g.get("gta", "TileAlpha"); g.get("gba", "BgAlpha")
    for name, key, t, f, a, scaled in DERIVED:
        g.get("g_" + name, "Theme" + key); src = "@g_%s.Theme%s" % (name, key)
        if t:
            g.call("l_" + name, K_MATH, "LinearColorLerp", inp={"A": src, "B": "(R=1,G=1,B=1,A=1)", "Alpha": str(t)}); src = "@l_%s.ReturnValue" % name
        if f != 1:
            g.call("d_" + name, K_MATH, "Multiply_LinearColorFloat", inp={"A": src, "B": str(f)}); src = "@d_%s.ReturnValue" % name
        g.call("b_" + name, K_MATH, "BreakColor", inp={"InColor": src})
        if a is None: alpha = "@gba.BgAlpha"
        elif scaled:
            g.call("a_" + name, K_MATH, "Multiply_FloatFloat", inp={"A": str(a), "B": "@gta.TileAlpha"}); alpha = "@a_%s.ReturnValue" % name
        else: alpha = str(a)
        g.call("m_" + name, K_MATH, "MakeColor", inp={"R": "@b_%s.R" % name, "G": "@b_%s.G" % name, "B": "@b_%s.B" % name, "A": alpha})
        g.set("s_" + name, name, inp={name: "@m_%s.ReturnValue" % name}); tail.append("s_" + name)
    g.get("gv", "ThemeVersion"); g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gv.ThemeVersion", "B": "1"}); g.set("sv", "ThemeVersion", inp={"ThemeVersion": "@inc.ReturnValue"}); tail.append("sv")
    g.get("gp", "Panel"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gp.Panel"}); g.branch("bp", "@iv.ReturnValue"); tail.append("bp")
    g.get("gp2", "Panel"); g.call("pat", M + "/W_AltUI", "Apply Theme", inp={"self": "@gp2.Panel"})
    g.chain(*tail, "pat"); return fn("Apply Theme", graph=g)


def f_close_color():
    g = G(); g.set("s", "ColorOpen", inp={"ColorOpen": "false"})
    g.get("gp", "Palette"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gp.Palette"}); g.branch("b", "@iv.ReturnValue")
    g.get("gp2", "Palette"); g.call("cf", P_PAL, "Close Frame", inp={"self": "@gp2.Palette"})
    g.get("gp3", "Palette"); g.call("rm", E_WIDGET, "RemoveFromParent", inp={"self": "@gp3.Palette"})
    g.chain("entry", "s", "b", "cf", "rm"); return fn("Close Color", graph=g)


def f_apply_preview():
    """Tick while the palette is open: read the colour from Paletter.Image_Color, apply live; palette closed -> save."""
    g = G()
    g.get("gp", "Palette"); g.call("inv", E_USERWIDGET, "IsInViewport", inp={"self": "@gp.Palette"})
    g.get("gp1", "Palette"); g.call("vis", E_WIDGET, "IsVisible", inp={"self": "@gp1.Palette"})
    g.call("open", K_MATH, "BooleanAND", inp={"A": "@inv.ReturnValue", "B": "@vis.ReturnValue"}); g.branch("bo", "@open.ReturnValue")
    # closed -> save (clothes: Save Clothes Color; hair: GameInstance.Save Hair Color Data; theme: our settings)
    g.get("gcmt", "ColorMode"); g.call("ist", K_MATH, "EqualEqual_NameName", inp={"A": "@gcmt.ColorMode", "B": "Theme"}); g.branch("bt", "@ist.ReturnValue")
    g.n("svt", "call_self", function="Save Settings")
    g.get("gcm", "ColorMode"); g.call("ish", K_MATH, "EqualEqual_NameName", inp={"A": "@gcm.ColorMode", "B": "Hair"}); g.branch("bh", "@ish.ReturnValue")
    g.get("gpl", "Player"); g.get("gcl", "ColorItem"); g.get("gcc", "ColorCur")
    g.call("sv", P_CPB, "Save Clothes Color", inp={"self": "@gpl.Player", "clothes name": "@gcl.ColorItem", "color": "@gcc.ColorCur"})
    g.call("gi", K_GS, "GetGameInstance"); g.cast("cgi", P_GI, "@gi.ReturnValue"); g.get("gplh", "Player")
    g.call("svh", P_GI, "Save Hair Color Data", inp={"self": "@cgi.AsTKA Game Instance", "player": "@gplh.Player"})
    g.n("cc", "call_self", function="Close Color")
    # open, theme -> Set Theme Color + Apply Theme (widgets refresh on their Tick); hair -> Change Hairstyle Color
    g.get("gcmt2", "ColorMode"); g.call("ist2", K_MATH, "EqualEqual_NameName", inp={"A": "@gcmt2.ColorMode", "B": "Theme"}); g.branch("bt2", "@ist2.ReturnValue")
    g.get("gcl3", "ColorItem"); g.get("gcc4", "ColorCur"); g.n("stc", "call_self", function="Set Theme Color", inp={"key": "@gcl3.ColorItem", "color": "@gcc4.ColorCur"}); g.n("ath", "call_self", function="Apply Theme")
    g.get("gcm2", "ColorMode"); g.call("ish2", K_MATH, "EqualEqual_NameName", inp={"A": "@gcm2.ColorMode", "B": "Hair"}); g.branch("bh2", "@ish2.ReturnValue")
    g.get("gplh2", "Player"); g.get("gcc3", "ColorCur"); g.call("chh", P_JODI, "Change Hairstyle Color", inp={"self": "@gplh2.Player", "color": "@gcc3.ColorCur"})
    # open -> read the colour
    g.get("gp2", "Palette"); g.get("pal", "Paletter", cls=P_PAL); g.link("gp2.Palette", "pal.self")
    g.get("img", "Image_Color", cls=P_PALR); g.link("pal.Paletter", "img.self")
    g.get("colr", "ColorAndOpacity", cls=E_IMAGE); g.link("img.Image_Color", "colr.self")
    g.get("gcc2", "ColorCur"); g.call("neq", K_MATH, "NotEqual_LinearColorLinearColor", inp={"A": "@colr.ColorAndOpacity", "B": "@gcc2.ColorCur"}); g.branch("bn", "@neq.ReturnValue")
    g.set("scc", "ColorCur", inp={"ColorCur": "@colr.ColorAndOpacity"})
    g.get("gpl2", "Player"); g.get("gcl2", "ColorItem"); g.call("fc", P_CPB, "Find Clothes Component With Name", inp={"self": "@gpl2.Player", "name": "@gcl2.ColorItem"})
    g.call("cv", K_SYS, "IsValid", inp={"Object": "@fc.clothes comp"}); g.branch("bc", "@cv.ReturnValue")
    g.call("chg", P_CC, "Change Color", inp={"self": "@fc.clothes comp", "Color": "@colr.ColorAndOpacity"})
    g.chain("entry", "bo", "bn", "scc", "bt2", "stc", "ath"); g.chain("bt2:else", "bh2", "chh"); g.chain("bh2:else", "fc", "bc", "chg")
    g.chain("bo:else", "bt", "svt", "cc"); g.chain("bt:else", "bh", "svh", "cc"); g.chain("bh:else", "sv", "cc")
    return fn("Apply Preview", graph=g)


# ---------------- Looks (own SaveGame SG_Looks, slot AltUI_Looks; a look = name + id + snapshot) ----------------
def looks_array(g, id):
    """LooksSave.Looks as a pin (get via class SG_Looks)."""
    g.get(id + "_s", "LooksSave"); g.get(id, "Looks", cls=SG_LOOKS); g.link(id + "_s.LooksSave", id + ".self"); return "@%s.Looks" % id


def f_load_looks():
    g = G()
    g.call("ex", K_GS, "DoesSaveGameExist", inp={"SlotName": LOOKS_SLOT, "UserIndex": "0"}); g.branch("b", "@ex.ReturnValue")
    g.call("ld", K_GS, "LoadGameFromSlot", inp={"SlotName": LOOKS_SLOT, "UserIndex": "0"}); g.cast("cl", SG_LOOKS, "@ld.ReturnValue")
    g.set("s1", "LooksSave", inp={"LooksSave": "@cl.AsSG_Looks"})
    g.call("cr", K_GS, "CreateSaveGameObject", inp={"SaveGameClass": SG_LOOKS}); g.cast("cc", SG_LOOKS, "@cr.ReturnValue")
    g.set("s2", "LooksSave", inp={"LooksSave": "@cc.AsSG_Looks"})
    g.get("gs", "LooksSave"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gs.LooksSave"}); g.branch("bv", "@iv.ReturnValue")
    g.chain("entry", "ex", "b", "ld", "s1", "bv"); g.chain("bv:else", "cr", "s2"); g.chain("b:else", "cr")
    return fn("Load Looks", graph=g)


def f_save_looks():
    g = G(); g.get("gs", "LooksSave"); g.call("sv", K_GS, "SaveGameToSlot", inp={"SaveGameObject": "@gs.LooksSave", "SlotName": LOOKS_SLOT, "UserIndex": "0"})
    g.chain("entry", "sv"); return fn("Save Looks", graph=g)


def ensure_looks(g):
    """Exec ids that load the looks save if the manager has none yet: returns (chain head, tails that continue)."""
    g.get("el_g", "LooksSave"); g.call("el_v", K_SYS, "IsValid", inp={"Object": "@el_g.LooksSave"}); g.branch("el_b", "@el_v.ReturnValue")
    g.n("el_l", "call_self", function="Load Looks"); g.chain("el_b:else", "el_l"); return ["el_b"], ["el_l", "el_b"]


def f_looks_count():
    g = G(); arr = looks_array(g, "la"); g.call("len", K_ARR, "Array_Length", inp={"TargetArray": arr}); g.link("len.ReturnValue", "return.n")
    g.chain("entry", "return"); return fn("Looks Count", outputs=[param("n", "int")], graph=g)


def default_look_name(g, id, index_pin):
    """T(Lbl_Look) + " " + (index+1) as string pin."""
    g.call(id + "_i", K_MATH, "Add_IntInt", inp={"A": index_pin, "B": "1"}); g.call(id + "_s", K_STR, "Conv_IntToString", inp={"InInt": "@%s_i.ReturnValue" % id})
    g.call(id + "_a", K_STR, "Concat_StrStr", inp={"A": ts(g, id + "_t", "Lbl_Look"), "B": " "}); g.call(id, K_STR, "Concat_StrStr", inp={"A": "@%s_a.ReturnValue" % id, "B": "@%s_s.ReturnValue" % id})
    return "@%s.ReturnValue" % id


def f_add_look():
    g = G()
    g.n("ts", "call_self", function="Take Snapshot")
    g.get("gs", "LooksSave"); g.get("gni", "NextId", cls=SG_LOOKS); g.link("gs.LooksSave", "gni.self")
    g.set("sid", "TmpI", inp={"TmpI": "@gni.NextId"}); g.get("gid", "TmpI")   # pure getters re-evaluate per consumer -> freeze the id before NextId is incremented
    arr = looks_array(g, "la"); g.call("len", K_ARR, "Array_Length", inp={"TargetArray": arr})
    name = default_look_name(g, "dn", "@len.ReturnValue")
    g.make("mk", S_LOOK, Name=name, Id="@gid.TmpI", Snap="@ts.snap"); g.set("stl", "TmpLook", inp={"TmpLook": "@mk.S_Look"})
    arr2 = looks_array(g, "lb"); g.get("gtl", "TmpLook"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": arr2, "NewItem": "@gtl.TmpLook"})
    g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gid.TmpI", "B": "1"}); g.get("gs2", "LooksSave"); g.n("sni", "set", var="NextId", cls=SG_LOOKS, inp={"self": "@gs2.LooksSave", "NextId": "@inc.ReturnValue"})
    g.n("sv", "call_self", function="Save Looks"); g.n("cap", "call_self", function="Capture Look Photo", inp={"id": "@gid.TmpI"}); g.n("rl", "call_self", function="Rebuild Looks")
    g.chain("entry", "ts", "sid", "stl", "add", "sni", "sv", "cap", "rl")
    return fn("Add Look", graph=g)


def f_update_look():
    g = G(); arr = looks_array(g, "la"); g.call("get", K_ARR, "Array_Get", inp={"TargetArray": arr, "Index": "@entry.index"}); g.brk("bl", S_LOOK, "@get.Item")
    g.set("sid", "TmpI", inp={"TmpI": "@bl.Id"}); g.get("gid", "TmpI")
    g.n("ts", "call_self", function="Take Snapshot"); g.make("mk", S_LOOK, Name="@bl.Name", Id="@gid.TmpI", Snap="@ts.snap"); g.set("stl", "TmpLook", inp={"TmpLook": "@mk.S_Look"})
    arr2 = looks_array(g, "lb"); g.get("gtl", "TmpLook"); g.call("set", K_ARR, "Array_Set", inp={"TargetArray": arr2, "Index": "@entry.index", "Item": "@gtl.TmpLook", "bSizeToFit": "false"})
    g.get("gli", "LookIcons"); g.call("rmi", K_MAP, "Map_Remove", inp={"TargetMap": "@gli.LookIcons", "Key": "@gid.TmpI"})
    g.n("sv", "call_self", function="Save Looks"); g.n("cap", "call_self", function="Capture Look Photo", inp={"id": "@gid.TmpI"}); g.n("rl", "call_self", function="Rebuild Looks")
    g.chain("entry", "sid", "ts", "stl", "set", "rmi", "sv", "cap", "rl")
    return fn("Update Look", [param("index", "int")], graph=g)


def f_delete_look():
    g = G(); arr = looks_array(g, "la"); g.call("get", K_ARR, "Array_Get", inp={"TargetArray": arr, "Index": "@entry.index"}); g.brk("bl", S_LOOK, "@get.Item")
    g.get("gli", "LookIcons"); g.call("rmi", K_MAP, "Map_Remove", inp={"TargetMap": "@gli.LookIcons", "Key": "@bl.Id"})
    arr2 = looks_array(g, "lb"); g.call("rm", K_ARR, "Array_Remove", inp={"TargetArray": arr2, "IndexToRemove": "@entry.index"})
    g.n("sv", "call_self", function="Save Looks"); g.get("go", "PanelOpen"); g.branch("bo", "@go.PanelOpen"); g.n("rl", "call_self", function="Rebuild Looks")
    g.chain("entry", "rmi", "rm", "sv", "bo", "rl")
    return fn("Delete Look", [param("index", "int")], graph=g)


def f_look_name():
    g = G(); arr = looks_array(g, "la"); g.call("get", K_ARR, "Array_Get", inp={"TargetArray": arr, "Index": "@entry.index"}); g.brk("bl", S_LOOK, "@get.Item")
    g.link("bl.Name", "return.name"); g.chain("entry", "return")
    return fn("Look Name", [param("index", "int")], [param("name", "string")], graph=g)


def f_set_look_name():
    """Trim, cut to 40 chars; empty -> default "Look N"; save; redraw."""
    g = G()
    g.call("t1", K_STR, "Trim", inp={"SourceString": "@entry.name"}); g.call("t2", K_STR, "TrimTrailing", inp={"SourceString": "@t1.ReturnValue"})
    g.call("cut", K_STR, "Left", inp={"SourceString": "@t2.ReturnValue", "Count": "40"}); g.call("len", K_STR, "Len", inp={"S": "@cut.ReturnValue"})
    g.call("emp", K_MATH, "EqualEqual_IntInt", inp={"A": "@len.ReturnValue", "B": "0"})
    name = default_look_name(g, "dn", "@entry.index"); g.call("sel", K_MATH, "SelectString", inp={"A": name, "B": "@cut.ReturnValue", "bPickA": "@emp.ReturnValue"})
    arr = looks_array(g, "la"); g.call("get", K_ARR, "Array_Get", inp={"TargetArray": arr, "Index": "@entry.index"}); g.brk("bl", S_LOOK, "@get.Item")
    g.make("mk", S_LOOK, Name="@sel.ReturnValue", Id="@bl.Id", Snap="@bl.Snap"); g.set("stl", "TmpLook", inp={"TmpLook": "@mk.S_Look"})
    arr2 = looks_array(g, "lb"); g.get("gtl", "TmpLook"); g.call("set", K_ARR, "Array_Set", inp={"TargetArray": arr2, "Index": "@entry.index", "Item": "@gtl.TmpLook", "bSizeToFit": "false"})
    g.n("sv", "call_self", function="Save Looks"); g.get("go", "PanelOpen"); g.branch("bo", "@go.PanelOpen"); g.n("rl", "call_self", function="Rebuild Looks")
    g.chain("entry", "stl", "set", "sv", "bo", "rl")
    return fn("Set Look Name", [param("index", "int"), param("name", "string")], graph=g)


def f_apply_look():
    g = G(); arr = looks_array(g, "la"); g.call("get", K_ARR, "Array_Get", inp={"TargetArray": arr, "Index": "@entry.index"}); g.brk("bl", S_LOOK, "@get.Item")
    g.n("ph", "call_self", function="Push History"); g.n("ap", "call_self", function="Apply Snapshot", inp={"snap": "@bl.Snap"})
    g.chain("entry", "ph", "ap"); return fn("Apply Look", [param("index", "int")], graph=g)


def f_rebuild_looks():
    g = G(); head, tails = ensure_looks(g)
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Look Tiles", inp={"self": "@gp.Panel"})
    aw = create_widget(g, "ca", W_LOOK); set_manager(g, "sma", W_LOOK, aw)
    g.call("et", K_TXT, "Conv_StringToText", inp={"InString": ""}); g.call("ia", W_LOOK, "Init", inp={"self": aw, "index": "-1", "icon": "None", "caption": "@et.ReturnValue"})
    g.get("gpa", "Panel"); g.call("aa", W_PANEL, "Add Look Tile", inp={"self": "@gpa.Panel", "widget": aw})
    arr = looks_array(g, "la"); g.foreach("fe", arr); g.brk("bl", S_LOOK, "@fe.Array Element")
    g.n("ic", "call_self", function="Look Icon", inp={"id": "@bl.Id"}); g.call("ct", K_TXT, "Conv_StringToText", inp={"InString": "@bl.Name"})
    lw = create_widget(g, "cw", W_LOOK); set_manager(g, "smw", W_LOOK, lw)
    g.call("il", W_LOOK, "Init", inp={"self": lw, "index": "@fe.Array Index", "icon": "@ic.tex", "caption": "@ct.ReturnValue"})
    g.get("gpo", "Panel"); g.call("al", W_PANEL, "Add Look Tile", inp={"self": "@gpo.Panel", "widget": lw})
    g.chain("entry", *head)
    for t in tails: g.chain(t, "cl")
    g.chain("cl", "ca_cr", "sma", "ia", "aa", "fe"); g.chain("fe", "ic", "cw_cr", "smw", "il", "al")
    return fn("Rebuild Looks", graph=g)


def f_on_look_clicked():
    g = G(); g.call("neg", K_MATH, "Less_IntInt", inp={"A": "@entry.index", "B": "0"}); g.branch("b", "@neg.ReturnValue")
    g.n("add", "call_self", function="Add Look"); g.n("ap", "call_self", function="Apply Look", inp={"index": "@entry.index"})
    g.chain("entry", "b", "add"); g.chain("b:else", "ap"); return fn("On Look Clicked", [param("index", "int")], graph=g)


def f_on_look_context():
    g = G()
    g.call("neg", K_MATH, "Less_IntInt", inp={"A": "@entry.index", "B": "0"}); g.branch("bn", "@neg.ReturnValue")
    g.n("oc", "call_self", function="On Look Clicked", inp={"index": "@entry.index"})
    g.set("scl", "ContextLook", inp={"ContextLook": "@entry.index"})
    g.get("gm", "Menu"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gm.Menu"}); g.branch("b", "@iv.ReturnValue")
    mw = create_widget(g, "cm", W_MENU); g.set("sm", "Menu", inp={"Menu": mw}); set_manager(g, "smm", W_MENU, mw)
    g.get("gm2", "Menu"); g.call("clr", W_MENU, "Clear Rows", inp={"self": "@gm2.Menu"})
    tail = ["clr"]
    for i, (action, key) in enumerate([("LookView", "Menu_ViewContent"), ("LookRename", "Menu_Rename"), ("LookUpdate", "Menu_UpdateLook"), ("LookDelete", "Menu_Delete"), ("Cancel", "Menu_Cancel")]):
        tail += menu_row(g, i, action, tt(g, "t%d" % i, key))
    g.get("gm6", "Menu"); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@gm6.Menu", "ZOrder": "110"})
    g.call("mp", "/Script/UMG.WidgetLayoutLibrary", "GetMousePositionOnViewport")
    g.get("gm7", "Menu"); g.call("spv", E_USERWIDGET, "SetPositionInViewport", inp={"self": "@gm7.Menu", "Position": "@mp.ReturnValue", "bRemoveDPIScale": "false"})
    g.chain("entry", "bn", "oc"); g.chain("bn:else", "scl", "b", "clr"); g.chain("b:else", "cm_cr", "sm", "smm", "clr"); g.chain(*tail, "atv", "mp", "spv")
    return fn("On Look Context", [param("index", "int")], graph=g)


# ---------------- Content view (View content / Show in tab) ----------------
def f_content_open():
    """yes = the tab `page` has a content view open (ViewOutfit / ViewLook / ViewPreset >= 0)."""
    g = G()
    g.call("isO", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.page", "B": "Outfits"}); g.call("isL", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.page", "B": "Looks"})
    g.call("isA", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.page", "B": "Look"})
    g.get("gvo", "ViewOutfit"); g.get("gvl", "ViewLook"); g.get("gvp", "ViewPreset")
    g.call("v1", K_MATH, "SelectInt", inp={"A": "@gvp.ViewPreset", "B": "-1", "bPickA": "@isA.ReturnValue"}); g.call("v2", K_MATH, "SelectInt", inp={"A": "@gvl.ViewLook", "B": "@v1.ReturnValue", "bPickA": "@isL.ReturnValue"})
    g.call("v3", K_MATH, "SelectInt", inp={"A": "@gvo.ViewOutfit", "B": "@v2.ReturnValue", "bPickA": "@isO.ReturnValue"}); g.call("ge", K_MATH, "GreaterEqual_IntInt", inp={"A": "@v3.ReturnValue", "B": "0"})
    g.link("ge.ReturnValue", "return.yes"); g.chain("entry", "return")
    return fn("Content Open", [param("page", "name")], [param("yes", "bool")], graph=g)


def f_open_content():
    """Open the content view of outfit / look / preset `index` (kind = Outfit / Look / Preset) on the current page."""
    g = G()
    g.call("isO", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "Outfit"}); g.branch("bO", "@isO.ReturnValue"); g.set("so", "ViewOutfit", inp={"ViewOutfit": "@entry.index"})
    g.call("isL", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "Look"}); g.branch("bL", "@isL.ReturnValue"); g.set("sl", "ViewLook", inp={"ViewLook": "@entry.index"})
    g.call("isP", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "Preset"}); g.branch("bP", "@isP.ReturnValue"); g.set("sp", "ViewPreset", inp={"ViewPreset": "@entry.index"})
    g.get("gpg", "Page"); g.n("spg", "call_self", function="Select Page", inp={"name": "@gpg.Page"})
    g.chain("entry", "bO", "so", "spg"); g.chain("bO:else", "bL", "sl", "spg"); g.chain("bL:else", "bP", "sp", "spg")
    return fn("Open Content", [param("kind", "name"), param("index", "int")], graph=g)


def open_content_wrapper(name, kind):
    """One-argument wrappers for the menu action table."""
    g = G(); g.n("oc", "call_self", function="Open Content", inp={"kind": kind, "index": "@entry.index"}); g.chain("entry", "oc")
    return fn(name, [param("index", "int")], graph=g)


def f_close_content():
    """Back link: close the content view of the current page and show the page itself again."""
    g = G(); g.get("gpg", "Page")
    g.call("isO", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Outfits"}); g.branch("bO", "@isO.ReturnValue"); g.set("so", "ViewOutfit", inp={"ViewOutfit": "-1"})
    g.call("isL", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Looks"}); g.branch("bL", "@isL.ReturnValue"); g.set("sl", "ViewLook", inp={"ViewLook": "-1"})
    g.call("isA", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Look"}); g.branch("bA", "@isA.ReturnValue"); g.set("sp", "ViewPreset", inp={"ViewPreset": "-1"})
    g.get("gpg2", "Page"); g.n("spg", "call_self", function="Select Page", inp={"name": "@gpg2.Page"})
    g.chain("entry", "bO", "so", "spg"); g.chain("bO:else", "bL", "sl", "spg"); g.chain("bL:else", "bA", "sp", "spg"); g.chain("bA:else", "spg")
    return fn("Close Content", graph=g)


def f_content_snapshot():
    """ViewSnap / ViewTitle from outfit / preset / look `index`; ok = false for an unknown kind or an index out of range.
    Outfit: Worn = keys of the clothes map, Colors = its values (FColor -> LinearColor); Preset: makeup/skin/hair/hair colour/sliders; Look: its snapshot."""
    g = G(); g.set("ok0", "TmpBool", inp={"TmpBool": "false"})
    # --- outfit
    g.call("isO", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "Outfit"}); g.branch("bO", "@isO.ReturnValue")
    g.get("go", "Outfits"); g.get("goa", "outfits", cls=P_OUTFITS); g.link("go.Outfits", "goa.self")
    g.call("ol", K_ARR, "Array_Length", inp={"TargetArray": "@goa.outfits"}); g.call("oin", K_MATH, "Less_IntInt", inp={"A": "@entry.index", "B": "@ol.ReturnValue"})
    g.call("ge0", K_MATH, "GreaterEqual_IntInt", inp={"A": "@entry.index", "B": "0"}); g.call("oin2", K_MATH, "BooleanAND", inp={"A": "@oin.ReturnValue", "B": "@ge0.ReturnValue"}); g.branch("bOi", "@oin2.ReturnValue")
    g.call("oget", K_ARR, "Array_Get", inp={"TargetArray": "@goa.outfits", "Index": "@entry.index"}); g.brk("obr", P_OUTFIT_S, "@oget.Item")
    g.call("okeys", K_MAP, "Map_Keys", inp={"TargetMap": "@obr." + OUTFIT_MEMBER}); g.set("sokeys", "TmpNames", inp={"TmpNames": "@okeys.Keys"})
    g.get("gtc0", "TmpColors"); g.call("cclr", K_MAP, "Map_Clear", inp={"TargetMap": "@gtc0.TmpColors"})
    g.get("gtn", "TmpNames"); g.foreach("fo", "@gtn.TmpNames")
    g.call("ofind", K_MAP, "Map_Find", inp={"TargetMap": "@obr." + OUTFIT_MEMBER, "Key": "@fo.Array Element"}); g.call("olin", K_MATH, "Conv_ColorToLinearColor", inp={"InColor": "@ofind.Value"})
    g.get("gtc1", "TmpColors"); g.call("oadd", K_MAP, "Map_Add", inp={"TargetMap": "@gtc1.TmpColors", "Key": "@fo.Array Element", "Value": "@olin.ReturnValue"})
    g.get("gtn2", "TmpNames"); g.get("gtc2", "TmpColors"); g.make("omk", S_SNAP, Worn="@gtn2.TmpNames", Colors="@gtc2.TmpColors"); g.set("osn", "ViewSnap", inp={"ViewSnap": "@omk.S_Snapshot"})
    g.n("oname", "call_self", function="Outfit Name", inp={"index": "@entry.index"})   # writes TmpStrings/TmpStr2 -> after the snapshot is stored
    g.call("olen", K_STR, "Len", inp={"S": "@oname.name"}); g.call("oemp", K_MATH, "EqualEqual_IntInt", inp={"A": "@olen.ReturnValue", "B": "0"})
    g.call("oi1", K_MATH, "Add_IntInt", inp={"A": "@entry.index", "B": "1"}); g.call("ois", K_STR, "Conv_IntToString", inp={"InInt": "@oi1.ReturnValue"})
    g.call("od1", K_STR, "Concat_StrStr", inp={"A": ts(g, "odt", "Lbl_Outfit"), "B": " "}); g.call("od2", K_STR, "Concat_StrStr", inp={"A": "@od1.ReturnValue", "B": "@ois.ReturnValue"})
    g.call("osel", K_MATH, "SelectString", inp={"A": "@od2.ReturnValue", "B": "@oname.name", "bPickA": "@oemp.ReturnValue"}); g.set("ost", "ViewTitle", inp={"ViewTitle": "@osel.ReturnValue"})
    g.set("ook", "TmpBool", inp={"TmpBool": "true"})
    # --- preset
    g.call("isP", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "Preset"}); g.branch("bP", "@isP.ReturnValue")
    pd = presets_data(g, "pd"); g.call("pl", K_ARR, "Array_Length", inp={"TargetArray": pd}); g.call("pin", K_MATH, "Less_IntInt", inp={"A": "@entry.index", "B": "@pl.ReturnValue"})
    g.call("ge1", K_MATH, "GreaterEqual_IntInt", inp={"A": "@entry.index", "B": "0"}); g.call("pin2", K_MATH, "BooleanAND", inp={"A": "@pin.ReturnValue", "B": "@ge1.ReturnValue"}); g.branch("bPi", "@pin2.ReturnValue")
    g.call("pget", K_ARR, "Array_Get", inp={"TargetArray": pd, "Index": "@entry.index"}); g.brk("pbr", P_PRESET_S, "@pget.Item")
    g.make("pmk", S_SNAP, Makeup="@pbr.MakeupData", Skin="@pbr.SkinName", Hair="@pbr.HairstyleName", HairColor="@pbr.HairColor", Boobs="@pbr.BoobsSize", Waist="@pbr.Waist", Hip="@pbr.Hip")
    g.set("psn", "ViewSnap", inp={"ViewSnap": "@pmk.S_Snapshot"})
    g.call("pi1", K_MATH, "Add_IntInt", inp={"A": "@entry.index", "B": "1"}); g.call("pis", K_STR, "Conv_IntToString", inp={"InInt": "@pi1.ReturnValue"}); g.call("pt", K_STR, "Concat_StrStr", inp={"A": "Preset ", "B": "@pis.ReturnValue"})
    g.set("pst", "ViewTitle", inp={"ViewTitle": "@pt.ReturnValue"}); g.set("pok", "TmpBool", inp={"TmpBool": "true"})
    # --- look
    g.call("isL", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "Look"}); g.branch("bL", "@isL.ReturnValue")
    head, tails = ensure_looks(g)
    arr = looks_array(g, "la"); g.call("ll", K_ARR, "Array_Length", inp={"TargetArray": arr}); g.call("lin", K_MATH, "Less_IntInt", inp={"A": "@entry.index", "B": "@ll.ReturnValue"})
    g.call("ge2", K_MATH, "GreaterEqual_IntInt", inp={"A": "@entry.index", "B": "0"}); g.call("lin2", K_MATH, "BooleanAND", inp={"A": "@lin.ReturnValue", "B": "@ge2.ReturnValue"}); g.branch("bLi", "@lin2.ReturnValue")
    g.call("lget", K_ARR, "Array_Get", inp={"TargetArray": arr, "Index": "@entry.index"}); g.brk("lbr", S_LOOK, "@lget.Item")
    g.set("lsn", "ViewSnap", inp={"ViewSnap": "@lbr.Snap"}); g.set("lst", "ViewTitle", inp={"ViewTitle": "@lbr.Name"}); g.set("lok", "TmpBool", inp={"TmpBool": "true"})
    g.get("gok", "TmpBool"); g.link("gok.TmpBool", "return.ok")
    g.chain("entry", "ok0", "bO", "bOi", "okeys", "sokeys", "cclr", "fo"); g.chain("fo", "oadd"); g.chain("fo:Completed", "osn", "oname", "ost", "ook", "return"); g.chain("bOi:else", "return")
    g.chain("bO:else", "bP", "bPi", "psn", "pst", "pok", "return"); g.chain("bPi:else", "return")
    g.chain("bP:else", "bL", *head)
    for t in tails: g.chain(t, "bLi")
    g.chain("bLi", "lsn", "lst", "lok", "return"); g.chain("bLi:else", "return"); g.chain("bL:else", "return")
    return fn("Content Snapshot", [param("kind", "name"), param("index", "int")], [param("ok", "bool")], graph=g)


def content_section(g, id, caption_pin):
    """New W_ContentSection (caption) -> TmpSection, added to the panel's content list; returns the exec chain."""
    sw = create_widget(g, id, W_SECTION); set_manager(g, id + "_sm", W_SECTION, sw)
    g.call(id + "_i", W_SECTION, "Init", inp={"self": sw, "caption": caption_pin}); g.set(id + "_ss", "TmpSection", inp={"TmpSection": sw})
    g.get(id + "_gp", "Panel"); g.get(id + "_gs", "TmpSection")
    g.call(id + "_a", W_PANEL, "Add Content Section", inp={"self": "@%s_gp.Panel" % id, "widget": "@%s_gs.TmpSection" % id})
    return [id + "_cr", id + "_sm", id + "_i", id + "_ss", id + "_a"]


def content_tile(g, id, item_pin, worn_pin, owned_pin, fav_pin, damaged_pin, tip_pin):
    """W_ClothesButton in the current section (TmpSection); returns (exec chain, widget pin)."""
    tw = create_widget(g, id, W_BTN); set_manager(g, id + "_sm", W_BTN, tw)
    g.call(id + "_i", W_BTN, "Init", inp={"self": tw, "item": item_pin, "worn": worn_pin, "owned": owned_pin, "fav": fav_pin, "damaged": damaged_pin, "tip": tip_pin})
    g.get(id + "_gs", "TmpSection"); g.call(id + "_a", W_SECTION, "Add Tile", inp={"self": "@%s_gs.TmpSection" % id, "widget": tw})
    return [id + "_cr", id + "_sm", id + "_i", id + "_a"], tw


def f_rebuild_content():
    """Content view of the open outfit / look / preset (Page decides the kind): back link + title, then one section per non-empty part of the
    snapshot - clothes (+ stored colour), hairstyle (+ colour), skin, one per makeup type, body (mod tile + slider line). An index that became
    invalid (deleted in the mirror meanwhile) closes the view."""
    g = G()
    g.get("gpg", "Page"); g.call("isO", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Outfits"})
    g.get("gpg2", "Page"); g.call("isL", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg2.Page", "B": "Looks"})
    g.call("k1", K_MATH, "SelectString", inp={"A": "Look", "B": "Preset", "bPickA": "@isL.ReturnValue"}); g.call("k2s", K_MATH, "SelectString", inp={"A": "Outfit", "B": "@k1.ReturnValue", "bPickA": "@isO.ReturnValue"})
    g.call("k2", K_STR, "Conv_StringToName", inp={"InString": "@k2s.ReturnValue"})   # no SelectName in 4.27
    g.get("gvo", "ViewOutfit"); g.get("gvl", "ViewLook"); g.get("gvp", "ViewPreset")
    g.call("i1", K_MATH, "SelectInt", inp={"A": "@gvl.ViewLook", "B": "@gvp.ViewPreset", "bPickA": "@isL.ReturnValue"}); g.call("i2", K_MATH, "SelectInt", inp={"A": "@gvo.ViewOutfit", "B": "@i1.ReturnValue", "bPickA": "@isO.ReturnValue"})
    g.n("cs", "call_self", function="Content Snapshot", inp={"kind": "@k2.ReturnValue", "index": "@i2.ReturnValue"}); g.branch("bok", "@cs.ok")
    g.n("cc", "call_self", function="Close Content")
    # back link + title
    g.get("gp0", "Panel"); g.call("clc", W_PANEL, "Clear Content", inp={"self": "@gp0.Panel"})
    g.get("gp1", "Panel"); g.call("cll", W_PANEL, "Clear Content Links", inp={"self": "@gp1.Panel"})
    lw = create_widget(g, "clk", W_TXT); set_manager(g, "sml", W_TXT, lw)
    g.call("li", W_TXT, "Init", inp={"self": lw, "action": "ContentBack", "caption": tt(g, "lt", "Btn_Back")})
    g.get("gp2", "Panel"); g.call("al", W_PANEL, "Add Content Link", inp={"self": "@gp2.Panel", "widget": lw})
    g.get("gvt", "ViewTitle"); g.call("tt1", K_TXT, "Conv_StringToText", inp={"InString": "@gvt.ViewTitle"})
    g.get("gp3", "Panel"); g.call("sct", W_PANEL, "Set Content Title", inp={"self": "@gp3.Panel", "text": "@tt1.ReturnValue"})
    g.get("gvs", "ViewSnap"); g.brk("bv", S_SNAP, "@gvs.ViewSnap")
    # --- clothes: catalog item (placeholder without icon/slot if the piece is gone), stored colour as swatch
    g.call("wl", K_ARR, "Array_Length", inp={"TargetArray": "@bv.Worn"}); g.call("wgt", K_MATH, "Greater_IntInt", inp={"A": "@wl.ReturnValue", "B": "0"}); g.branch("bw", "@wgt.ReturnValue")
    sec1 = content_section(g, "s1", tt(g, "s1t", "Tab_Clothes"))
    g.foreach("fw", "@bv.Worn")
    g.n("fi", "call_self", function="Find Item", inp={"name": "@fw.Array Element"}); g.branch("bfi", "@fi.found")
    g.set("sti", "TmpItem", inp={"TmpItem": "@fi.item"}); g.set("stp", "TmpItem", inp={"TmpItem": make_item(g, "mph", "@fw.Array Element", "None")})
    g.get("gti", "TmpItem")
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@fw.Array Element"}); g.n("io", "call_self", function="Is Owned", inp={"name": "@fw.Array Element"})
    g.n("ifv", "call_self", function="Is Favorite", inp={"name": "@fw.Array Element"}); g.n("idm", "call_self", function="Is Damaged", inp={"name": "@fw.Array Element"})
    g.call("own1", K_MATH, "BooleanAND", inp={"A": "@io.yes", "B": "@fi.found"}); g.n("tip", "call_self", function="Item Tip", inp={"item": "@gti.TmpItem"})
    t1, w1 = content_tile(g, "t1", "@gti.TmpItem", "@iw.yes", "@own1.ReturnValue", "@ifv.yes", "@idm.yes", "@tip.tip")
    g.call("cf", K_MAP, "Map_Find", inp={"TargetMap": "@bv.Colors", "Key": "@fw.Array Element"}); g.branch("bcf", "@cf.ReturnValue")
    g.call("scs", W_BTN, "Set Color Swatch", inp={"self": w1, "color": "@cf.Value"})
    # --- hairstyle (+ hair colour)
    g.call("hn", K_MATH, "NotEqual_NameName", inp={"A": "@bv.Hair", "B": "None"}); g.branch("bh", "@hn.ReturnValue")
    sec2 = content_section(g, "s2", tt(g, "s2t", "Tab_Hair"))
    g.n("hrow", "get_row", table=P_HAIR_T, inp={"RowName": "@bv.Hair"}); g.brk("hbr", P_HAIR_S, "@hrow.OutRow")
    g.set("shi", "TmpItem", inp={"TmpItem": make_item(g, "mhi", "@bv.Hair", "@hbr.icon", slot="Hair")}); g.set("shp", "TmpItem", inp={"TmpItem": make_item(g, "mhp", "@bv.Hair", "None", slot="Hair")})
    g.get("gpl", "Player"); g.call("cur", P_JODI, "Get Hairstyle Name", inp={"self": "@gpl.Player"}); g.call("hsel", K_MATH, "EqualEqual_NameName", inp={"A": "@cur.name", "B": "@bv.Hair"})
    howned = hair_owned(g, "hown", "@bv.Hair", "@hbr.MirrorID")
    g.get("gti2", "TmpItem"); t2, w2 = content_tile(g, "t2", "@gti2.TmpItem", "@hsel.ReturnValue", howned, "false", "false", tt(g, "t2t", "Tab_Hair"))
    g.call("shc", W_BTN, "Set Color Swatch", inp={"self": w2, "color": "@bv.HairColor"})
    # --- skin
    g.call("skn", K_MATH, "NotEqual_NameName", inp={"A": "@bv.Skin", "B": "None"}); g.branch("bsk", "@skn.ReturnValue")
    sec3 = content_section(g, "s3", tt(g, "s3t", "Look_Skin"))
    g.n("srow", "get_row", table=P_SKIN_T, inp={"RowName": "@bv.Skin"}); g.brk("sbr", P_SKIN_S, "@srow.OutRow")
    g.set("ssi", "TmpItem", inp={"TmpItem": make_item(g, "msi", "@bv.Skin", "@sbr.icon", slot="Skin")}); g.set("ssp", "TmpItem", inp={"TmpItem": make_item(g, "msp", "@bv.Skin", "None", slot="Skin")})
    g.n("ssel", "call_self", function="Is Look Selected", inp={"type": "Skin", "style": "@bv.Skin"})
    g.get("gti3", "TmpItem"); t3, w3 = content_tile(g, "t3", "@gti3.TmpItem", "@ssel.yes", "true", "false", "false", tt(g, "t3t", "Look_Skin"))
    # --- one section per makeup type with a non-empty list (icon from EyeTable or MakeupTable; unknown type row -> makeup table)
    g.call("mk", K_MAP, "Map_Keys", inp={"TargetMap": "@bv.Makeup"}); g.foreach("fm", "@mk.Keys")
    g.call("mf", K_MAP, "Map_Find", inp={"TargetMap": "@bv.Makeup", "Key": "@fm.Array Element"}); g.brk("mbl", P_MDATA_S, "@mf.Value")
    g.call("mll", K_ARR, "Array_Length", inp={"TargetArray": "@mbl.List"}); g.call("mgt", K_MATH, "Greater_IntInt", inp={"A": "@mll.ReturnValue", "B": "0"}); g.branch("bml", "@mgt.ReturnValue")
    g.n("mcap", "call_self", function="Look Caption", inp={"type": "@fm.Array Element"})
    sec4 = content_section(g, "s4", "@mcap.caption")
    g.n("trow", "get_row", table=P_MTYPE_T, inp={"RowName": "@fm.Array Element"}); g.brk("tbr", P_MTYPE_S, "@trow.OutRow")
    g.set("sey", "TmpFound", inp={"TmpFound": "@tbr.EyeTable"}); g.set("sey0", "TmpFound", inp={"TmpFound": "false"})
    g.set("smln", "TmpNames3", inp={"TmpNames3": "@mbl.List"}); g.get("gml", "TmpNames3"); g.foreach("fs", "@gml.TmpNames3")
    g.get("gey", "TmpFound"); g.branch("bey", "@gey.TmpFound")
    g.n("erow", "get_row", table=P_EYE_T, inp={"RowName": "@fs.Array Element"}); g.brk("ebr", P_EYE_S, "@erow.OutRow")
    g.n("mrow", "get_row", table=P_MAKEUP_T, inp={"RowName": "@fs.Array Element"}); g.brk("mbr", P_MAKEUP_S, "@mrow.OutRow")
    g.set("sei", "TmpItem", inp={"TmpItem": make_item(g, "mei", "@fs.Array Element", "@ebr.Icon", slot="@fm.Array Element")})
    g.set("smi", "TmpItem", inp={"TmpItem": make_item(g, "mmi", "@fs.Array Element", "@mbr.Icon", slot="@fm.Array Element")})
    g.set("spi", "TmpItem", inp={"TmpItem": make_item(g, "mpi", "@fs.Array Element", "None", slot="@fm.Array Element")})
    g.n("msel", "call_self", function="Is Look Selected", inp={"type": "@fm.Array Element", "style": "@fs.Array Element"})
    g.get("gti4", "TmpItem"); t4, w4 = content_tile(g, "t4", "@gti4.TmpItem", "@msel.yes", "true", "false", "false", "@mcap.caption")
    # --- body: mod tile (caption from the mod table) + slider line; skipped when neither is set
    g.call("bn", K_MATH, "NotEqual_NameName", inp={"A": "@bv.Body", "B": "None"})
    g.call("b1", K_MATH, "Greater_FloatFloat", inp={"A": "@bv.Boobs", "B": "0.0"}); g.call("b2", K_MATH, "Greater_FloatFloat", inp={"A": "@bv.Waist", "B": "0.0"})
    g.call("bo2", K_MATH, "BooleanOR", inp={"A": "@b1.ReturnValue", "B": "@b2.ReturnValue"})
    g.call("bany", K_MATH, "BooleanOR", inp={"A": "@bn.ReturnValue", "B": "@bo2.ReturnValue"}); g.branch("bb", "@bany.ReturnValue")
    sec5 = content_section(g, "s5", tt(g, "s5t", "Tab_Body"))
    g.branch("bbn", "@bn.ReturnValue"); g.n("scan", "call_self", function="Scan Body Mods")
    g.get("gcp", "BodyCaptions"); g.call("cap", K_MAP, "Map_Find", inp={"TargetMap": "@gcp.BodyCaptions", "Key": "@bv.Body"})
    g.call("caps", K_TXT, "Conv_TextToString", inp={"InText": "@cap.Value"}); g.call("bns", K_STR, "Conv_NameToString", inp={"InName": "@bv.Body"})
    g.call("bsel", K_MATH, "SelectString", inp={"A": "@caps.ReturnValue", "B": "@bns.ReturnValue", "bPickA": "@cap.ReturnValue"})
    g.make("mbi", S_ITEM, Name="@bv.Body", Slot="Body", DisplayName="@bsel.ReturnValue")
    g.get("gcb", "CurrentBody"); g.call("bcur", K_MATH, "EqualEqual_NameName", inp={"A": "@gcb.CurrentBody", "B": "@bv.Body"})
    t5, w5 = content_tile(g, "t5", "@mbi.S_ClothesItem", "@bcur.ReturnValue", "true", "false", "false", tt(g, "t5t", "Tab_Body"))
    g.branch("bsl", "@bo2.ReturnValue")
    def pct(id, pin):
        g.call(id + "_m", K_MATH, "Multiply_FloatFloat", inp={"A": pin, "B": "100.0"}); g.call(id + "_r", K_MATH, "Round", inp={"A": "@%s_m.ReturnValue" % id})
        g.call(id, K_STR, "Conv_IntToString", inp={"InInt": "@%s_r.ReturnValue" % id}); return "@%s.ReturnValue" % id
    parts = [ts(g, "lb", "Lbl_Breast"), " ", pct("pb", "@bv.Boobs"), " % \u00b7 ", ts(g, "lw", "Lbl_Waist"), " ", pct("pw", "@bv.Waist"), " %"]
    acc = parts[0]
    for i, p in enumerate(parts[1:]):
        g.call("nc%d" % i, K_STR, "Concat_StrStr", inp={"A": acc, "B": p}); acc = "@nc%d.ReturnValue" % i
    g.call("nt", K_TXT, "Conv_StringToText", inp={"InString": acc}); g.get("gs5", "TmpSection"); g.call("sn5", W_SECTION, "Set Note", inp={"self": "@gs5.TmpSection", "text": "@nt.ReturnValue"})
    # exec chains
    g.chain("entry", "cs", "bok", "clc", "cll", "clk_cr", "sml", "li", "al", "sct", "bw"); g.chain("bok:else", "cc")
    g.chain("bw", *sec1, "fw"); g.chain("fw", "fi", "bfi", "sti", "idm", "tip", *t1, "bcf", "scs"); g.chain("bfi:else", "stp", "idm"); g.chain("fw:Completed", "bh"); g.chain("bw:else", "bh")
    g.chain("bh", *sec2, "hrow", "shi", *t2, "shc", "bsk"); g.chain("hrow:Row Not Found", "shp", t2[0]); g.chain("bh:else", "bsk")
    g.chain("bsk", *sec3, "srow", "ssi", "ssel", *t3, "mk"); g.chain("srow:Row Not Found", "ssp", "ssel"); g.chain("bsk:else", "mk")
    g.chain("mk", "fm"); g.chain("fm", "bml", "mcap", *sec4, "trow", "sey", "smln"); g.chain("trow:Row Not Found", "sey0", "smln"); g.chain("smln", "fs")
    g.chain("fs", "bey", "erow", "sei", "msel"); g.chain("erow:Row Not Found", "spi", "msel"); g.chain("bey:else", "mrow", "smi", "msel"); g.chain("mrow:Row Not Found", "spi"); g.chain("msel", *t4)
    g.chain("fm:Completed", "bb"); g.chain("bb", *sec5, "bbn", "scan", *t5, "bsl", "sn5"); g.chain("bbn:else", "bsl")
    return fn("Rebuild Content", graph=g)


def f_on_content_item_context():
    """Right click on a tile of the content view: "Show in tab" (only if the tile knows its origin slot) + Cancel."""
    g = G()
    g.get("glb", "LastButton"); g.cast("cb", W_BTN, "@glb.LastButton"); g.get("gsl", "ItemSlot", cls=W_BTN); g.link("cb.AsW_ClothesButton", "gsl.self")
    g.set("scs", "ContextSlot", inp={"ContextSlot": "@gsl.ItemSlot"})
    g.get("gm", "Menu"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gm.Menu"}); g.branch("b", "@iv.ReturnValue")
    mw = create_widget(g, "cm", W_MENU); g.set("sm", "Menu", inp={"Menu": mw}); set_manager(g, "smm", W_MENU, mw)
    g.get("gm2", "Menu"); g.call("clr", W_MENU, "Clear Rows", inp={"self": "@gm2.Menu"})
    g.get("gcs", "ContextSlot"); g.call("has", K_MATH, "NotEqual_NameName", inp={"A": "@gcs.ContextSlot", "B": "None"}); g.branch("bh", "@has.ReturnValue")
    r0 = menu_row(g, 0, "GoTo", tt(g, "t0", "Menu_ShowIn")); r1 = menu_row(g, 1, "Cancel", tt(g, "t1", "Menu_Cancel"))
    g.get("gm6", "Menu"); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@gm6.Menu", "ZOrder": "110"})
    g.call("mp", "/Script/UMG.WidgetLayoutLibrary", "GetMousePositionOnViewport")
    g.get("gm7", "Menu"); g.call("spv", E_USERWIDGET, "SetPositionInViewport", inp={"self": "@gm7.Menu", "Position": "@mp.ReturnValue", "bRemoveDPIScale": "false"})
    g.chain("entry", "scs", "b", "clr"); g.chain("b:else", "cm_cr", "sm", "smm", "clr")
    g.chain("clr", "bh", *r0, r1[0]); g.chain("bh:else", r1[0]); g.chain(*r1, "atv", "mp", "spv")
    return fn("On Content Item Context", [param("name", "name")], graph=g)


def f_go_to_item():
    """"Show in tab": jump from the content view to the piece's own page - ContextSlot = origin (Hair / Skin / <makeup type> / Body / clothes slot).
    Clothes: search cleared, a filter toggle that would hide the piece is switched off (like a click), slot + group chip (Hidden for hidden pieces,
    the piece's group when the slot has more than one, else All); the tile is highlighted and scrolled into view."""
    g = G(); g.get("gcs", "ContextSlot")
    g.call("isH", K_MATH, "EqualEqual_NameName", inp={"A": "@gcs.ContextSlot", "B": "Hair"}); g.branch("bH", "@isH.ReturnValue")
    g.set("hh", "HighlightItem", inp={"HighlightItem": "@entry.name"}); g.set("hk", "KeepHighlight", inp={"KeepHighlight": "true"})
    g.n("hsp", "call_self", function="Select Page", inp={"name": "Hair"}); g.n("hsc", "call_self", function="Scroll To Highlight")
    g.call("isB", K_MATH, "EqualEqual_NameName", inp={"A": "@gcs.ContextSlot", "B": "Body"}); g.branch("bB", "@isB.ReturnValue")
    g.n("bsp", "call_self", function="Select Page", inp={"name": "Body"})
    # appearance: Skin or a row of the makeup type table
    g.call("isS", K_MATH, "EqualEqual_NameName", inp={"A": "@gcs.ContextSlot", "B": "Skin"}); g.branch("bS", "@isS.ReturnValue")
    g.n("trow", "get_row", table=P_MTYPE_T, inp={"RowName": "@gcs.ContextSlot"})
    g.set("lc", "LookCat", inp={"LookCat": "@gcs.ContextSlot"}); g.set("lh", "HighlightItem", inp={"HighlightItem": "@entry.name"}); g.set("lk", "KeepHighlight", inp={"KeepHighlight": "true"})
    g.set("lcv", "ViewPreset", inp={"ViewPreset": "-1"})   # coming from a preset's content view: close it, the appearance page must be visible
    g.n("lsp", "call_self", function="Select Page", inp={"name": "Look"}); g.n("lsc", "call_self", function="Scroll To Highlight")
    # clothes
    g.get("gp", "Panel"); g.call("pcs", W_PANEL, "Clear Search", inp={"self": "@gp.Panel"}); g.set("sst", "SearchText", inp={"SearchText": ""})
    g.n("io", "call_self", function="Is Owned", inp={"name": "@entry.name"}); g.get("gco", "CachedOnlyOwned"); g.call("no", K_MATH, "BooleanAND", inp={"A": "@gco.CachedOnlyOwned", "B": "@io.yes"})
    g.n("ifv", "call_self", function="Is Favorite", inp={"name": "@entry.name"}); g.get("gcf", "CachedOnlyFav"); g.call("nf", K_MATH, "BooleanAND", inp={"A": "@gcf.CachedOnlyFav", "B": "@ifv.yes"})
    g.n("gfi", "call_self", function="Find Item", inp={"name": "@entry.name"}); g.brk("gfb", S_ITEM, "@gfi.item")
    g.get("gcv", "CachedOnlyVanilla"); g.call("nv", K_MATH, "BooleanAND", inp={"A": "@gcv.CachedOnlyVanilla", "B": "@gfb.IsVanilla"})
    g.set("sco", "CachedOnlyOwned", inp={"CachedOnlyOwned": "@no.ReturnValue"}); g.set("scf", "CachedOnlyFav", inp={"CachedOnlyFav": "@nf.ReturnValue"}); g.set("scv", "CachedOnlyVanilla", inp={"CachedOnlyVanilla": "@nv.ReturnValue"})
    g.get("gp2", "Panel"); g.get("gco2", "CachedOnlyOwned"); g.get("gcf2", "CachedOnlyFav"); g.get("gcv2", "CachedOnlyVanilla")
    g.call("sft", W_PANEL, "Set Filter Toggles", inp={"self": "@gp2.Panel", "owned": "@gco2.CachedOnlyOwned", "fav": "@gcf2.CachedOnlyFav", "vanilla": "@gcv2.CachedOnlyVanilla"}); g.n("svs", "call_self", function="Save Settings")
    g.set("scs", "CurrentSlot", inp={"CurrentSlot": "@gcs.ContextSlot"})
    g.n("ih", "call_self", function="Is Item Hidden", inp={"name": "@entry.name"}); g.branch("bih", "@ih.yes"); g.set("sgh", "CurrentGroup", inp={"CurrentGroup": "Hidden"})
    g.n("grp", "call_self", function="Groups Of Slot", inp={"slot": "@gcs.ContextSlot"}); g.call("gl", K_ARR, "Array_Length", inp={"TargetArray": "@grp.groups"})
    g.call("gt1", K_MATH, "Greater_IntInt", inp={"A": "@gl.ReturnValue", "B": "1"}); g.branch("bg1", "@gt1.ReturnValue")
    g.n("fi", "call_self", function="Find Item", inp={"name": "@entry.name"}); g.brk("bi", S_ITEM, "@fi.item")
    g.call("gn", K_MATH, "EqualEqual_NameName", inp={"A": "@bi.Group", "B": "None"}); g.call("gns", K_STR, "Conv_NameToString", inp={"InName": "@bi.Group"})
    g.call("gsel", K_MATH, "SelectString", inp={"A": "Basis", "B": "@gns.ReturnValue", "bPickA": "@gn.ReturnValue"}); g.call("gseln", K_STR, "Conv_StringToName", inp={"InString": "@gsel.ReturnValue"})
    g.set("sgg", "CurrentGroup", inp={"CurrentGroup": "@gseln.ReturnValue"}); g.set("sgn", "CurrentGroup", inp={"CurrentGroup": "None"})
    g.set("ch", "HighlightItem", inp={"HighlightItem": "@entry.name"}); g.set("ck", "KeepHighlight", inp={"KeepHighlight": "true"})
    g.n("csp", "call_self", function="Select Page", inp={"name": "Clothes"}); g.n("csc", "call_self", function="Scroll To Highlight")
    g.chain("entry", "bH", "hh", "hk", "hsp", "hsc"); g.chain("bH:else", "bB", "bsp"); g.chain("bB:else", "bS", "lc"); g.chain("bS:else", "trow", "lc"); g.chain("lc", "lh", "lk", "lcv", "lsp", "lsc")
    g.chain("trow:Row Not Found", "pcs"); g.chain("pcs", "sst", "gfi", "sco", "scf", "scv", "sft", "svs", "scs", "bih", "sgh", "ch"); g.chain("bih:else", "grp", "bg1", "fi", "sgg", "ch"); g.chain("bg1:else", "sgn", "ch")
    g.chain("ch", "ck", "csp", "csc")
    return fn("Go To Item", [param("name", "name")], graph=g)


def f_scroll_to_highlight():
    """Scroll the tile remembered by the last rebuild (ScrollWidget = tile of HighlightItem) into view on the current page."""
    g = G(); g.get("gw", "ScrollWidget"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gw.ScrollWidget"}); g.branch("b", "@iv.ReturnValue")
    g.get("gp", "Panel"); g.get("gpg", "Page"); g.get("gw2", "ScrollWidget")
    g.call("siv", W_PANEL, "Scroll Into View", inp={"self": "@gp.Panel", "page": "@gpg.Page", "widget": "@gw2.ScrollWidget"})
    g.chain("entry", "b", "siv")
    return fn("Scroll To Highlight", graph=g)


def f_start_look_rename():
    g = G(); g.n("ln", "call_self", function="Look Name", inp={"index": "@entry.index"})
    g.get("glb", "LastButton"); g.cast("cb", W_LOOK, "@glb.LastButton"); g.call("cv", K_SYS, "IsValid", inp={"Object": "@cb.AsW_LookButton"}); g.branch("bv", "@cv.ReturnValue")
    g.call("br", W_LOOK, "Begin Rename", inp={"self": "@cb.AsW_LookButton", "current": "@ln.name"})
    g.chain("entry", "bv", "ln", "br"); return fn("Start Look Rename", [param("index", "int")], graph=g)


# ---------------- Camera follows slot/face (mirror codes: ClothesTypeTable.CameraFocus, MakeupTypeTable.CameraPosition) ----------------
def f_focus_code():
    """Clothes page: CameraFocus of the slot; Appearance: CameraPosition of the makeup type (skin/presets 0); Coiffure: 983; else 0."""
    g = G(); g.set("z", "TmpI", inp={"TmpI": "0"})
    g.get("gpg", "Page"); g.call("isc", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Clothes"}); g.branch("bc", "@isc.ReturnValue")
    g.get("gcs", "CurrentSlot"); g.n("crow", "get_row", table=P_CTT, inp={"RowName": "@gcs.CurrentSlot"}); g.brk("cbr", P_CTS, "@crow.OutRow"); g.set("sc", "TmpI", inp={"TmpI": "@cbr.CameraFocus"})
    g.get("gpg2", "Page"); g.call("isl", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg2.Page", "B": "Look"}); g.branch("bl", "@isl.ReturnValue")
    g.get("glc", "LookCat"); g.call("isp", K_MATH, "EqualEqual_NameName", inp={"A": "@glc.LookCat", "B": "Presets"}); g.call("iss", K_MATH, "EqualEqual_NameName", inp={"A": "@glc.LookCat", "B": "Skin"})
    g.call("orp", K_MATH, "BooleanOR", inp={"A": "@isp.ReturnValue", "B": "@iss.ReturnValue"}); g.branch("bps", "@orp.ReturnValue")
    g.n("mrow", "get_row", table=P_MTYPE_T, inp={"RowName": "@glc.LookCat"}); g.brk("mbr", P_MTYPE_S, "@mrow.OutRow"); g.set("sm", "TmpI", inp={"TmpI": "@mbr.CameraPosition"})
    g.get("gpg3", "Page"); g.call("ish", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg3.Page", "B": "Hair"}); g.branch("bh", "@ish.ReturnValue"); g.set("sh", "TmpI", inp={"TmpI": "983"})
    g.get("gt", "TmpI"); g.link("gt.TmpI", "return.code")
    g.chain("entry", "z", "bc", "crow", "sc", "return"); g.chain("crow:Row Not Found", "return")
    g.chain("bc:else", "bl", "bps", "return"); g.chain("bps:else", "mrow", "sm", "return"); g.chain("mrow:Row Not Found", "return")
    g.chain("bl:else", "bh", "sh", "return"); g.chain("bh:else", "return")
    return fn("Focus Code", outputs=[param("code", "int")], graph=g)


def f_update_focus():
    """Decode the code (h = code % 100 -> height 30 + 1.4h cm above the feet; f = (code % 1000) / 100 -> focal length 15 + 7f mm -> zoom 22/mm) and pass it to the hook."""
    g = G(); g.n("fc", "call_self", function="Focus Code")
    g.call("h", K_MATH, "Percent_IntInt", inp={"A": "@fc.code", "B": "100"}); g.call("v", K_MATH, "Percent_IntInt", inp={"A": "@fc.code", "B": "1000"})
    g.call("f0", K_MATH, "Divide_IntInt", inp={"A": "@v.ReturnValue", "B": "100"}); g.call("f", K_MATH, "Max", inp={"A": "@f0.ReturnValue", "B": "1"})
    g.call("f7", K_MATH, "Multiply_IntInt", inp={"A": "@f.ReturnValue", "B": "7"}); g.call("mm", K_MATH, "Add_IntInt", inp={"A": "@f7.ReturnValue", "B": "15"})
    g.call("mmf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@mm.ReturnValue"}); g.call("zoom", K_MATH, "Divide_FloatFloat", inp={"A": "22.0", "B": "@mmf.ReturnValue"})
    g.call("hf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@h.ReturnValue"}); g.call("h14", K_MATH, "Multiply_FloatFloat", inp={"A": "@hf.ReturnValue", "B": "1.4"}); g.call("h30", K_MATH, "Add_FloatFloat", inp={"A": "@h14.ReturnValue", "B": "30.0"})
    g.get("gpl", "Player"); g.get("gmc", "Mesh", cls=E_CHARACTER); g.link("gpl.Player", "gmc.self")
    g.call("ml", "/Script/Engine.SceneComponent", "K2_GetComponentLocation", inp={"self": "@gmc.Mesh"}); g.call("bml", K_MATH, "BreakVector", inp={"InVec": "@ml.ReturnValue"})
    g.get("gpl2", "Player"); g.call("al", E_ACTOR, "K2_GetActorLocation", inp={"self": "@gpl2.Player"}); g.call("bal", K_MATH, "BreakVector", inp={"InVec": "@al.ReturnValue"})
    g.call("dz", K_MATH, "Subtract_FloatFloat", inp={"A": "@bml.Z", "B": "@bal.Z"}); g.call("z", K_MATH, "Add_FloatFloat", inp={"A": "@dz.ReturnValue", "B": "@h30.ReturnValue"})
    g.set("sz", "FocusZ", inp={"FocusZ": "@z.ReturnValue"}); g.set("szm", "FocusZoom", inp={"FocusZoom": "@zoom.ReturnValue"}); g.set("stf", "TmpFloat", inp={"TmpFloat": "@zoom.ReturnValue"}); g.set("sti", "TmpI", inp={"TmpI": "@h.ReturnValue"})
    g.get("gpn", "PanToSlot"); g.get("gpo", "PanelOpen"); g.call("gt0", K_MATH, "Greater_IntInt", inp={"A": "@fc.code", "B": "0"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@gpn.PanToSlot", "B": "@gpo.PanelOpen"}); g.call("a2", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@gt0.ReturnValue"})
    g.set("son", "FocusOn", inp={"FocusOn": "@a2.ReturnValue"}); g.n("svs", "call_self", function="Set View Shift")
    g.chain("entry", "fc", "sz", "szm", "stf", "sti", "son", "svs"); return fn("Update Focus", graph=g)


# ---------------- Language: static panel texts, language choice ----------------
PANEL_STRINGS = [("search", "Lbl_Search"), ("onlyowned", "Lbl_OnlyOwned"), ("onlyfav", "Lbl_OnlyFav"), ("onlyvanilla", "Lbl_OnlyVanilla"), ("favorites", "Lbl_Favorites"), ("all", "Lbl_All"), ("listhint", "Lbl_ListHint"),
                 ("worn", "Lbl_Worn"), ("inbag", "Lbl_InBag"), ("bagempty", "Lbl_BagEmpty"), ("breast", "Lbl_Breast"), ("waist", "Lbl_Waist"),
                 ("scroll", "Lbl_Scroll"), ("scale", "Lbl_Scale"), ("fov", "Lbl_Fov"), ("dist", "Lbl_Dist"), ("grouplen", "Lbl_GroupLen"), ("chiph", "Lbl_ChipH"), ("unlimited", "Lbl_Unlimited"), ("layout", "Lbl_Layout"),
                 ("language", "Lbl_Language"), ("placeholder", "Lbl_Placeholder"), ("pan", "Lbl_Pan"), ("nude", "Lbl_Nude"),
                 ("theme", "Lbl_Theme"), ("bgalpha", "Lbl_BgAlpha"), ("tilealpha", "Lbl_TileAlpha"), ("key", "Lbl_ToggleKey")]
from gen_widgets import PANEL_TEXTS, THEME_COLS
assert [p for p, _ in PANEL_STRINGS] == [p for p, _ in PANEL_TEXTS], "PANEL_STRINGS must cover the parameters of W_AltUI.Set Strings (PANEL_TEXTS) exactly"


def f_apply_strings():
    g = G(); g.get("gp", "Panel")
    g.call("ss", W_PANEL, "Set Strings", inp={"self": "@gp.Panel", **{p: tt(g, "t_" + p, key) for p, key in PANEL_STRINGS}})
    g.chain("entry", "ss"); return fn("Apply Strings", graph=g)


def f_select_language():
    """Options chip: save LangChoice, reload the texts, relabel the visible parts."""
    g = G(); g.set("s", "LangChoice", inp={"LangChoice": "@entry.choice"})
    g.n("sv", "call_self", function="Save Settings"); g.n("dl", "call_self", function="Detect Language"); g.n("ist", "call_self", function="Init Strings")
    g.n("aps", "call_self", function="Apply Strings"); g.n("rtt", "call_self", function="Rebuild TopTabs"); g.n("ro", "call_self", function="Rebuild Options")
    g.chain("entry", "s", "sv", "dl", "ist", "aps", "rtt", "ro"); return fn("Select Language", [param("choice", "int")], graph=g)


# ---------------- Body switcher (body mods = paks Body_<Name> with /Game/Mod/Body_<Name>/Female; list from the game loader's DLC_MainTable) ----------------
def f_scan_body_mods():
    g = G()
    g.get("gm", "BodyMods"); g.call("cl", K_ARR, "Array_Clear", inp={"TargetArray": "@gm.BodyMods"})
    g.get("gc", "BodyCaptions"); g.call("mc", K_MAP, "Map_Clear", inp={"TargetMap": "@gc.BodyCaptions"})
    g.call("rn", K_DT, "GetDataTableRowNames", inp={"Table": P_DLC_T})
    g.foreach("fe", "@rn.OutRowNames")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@fe.Array Element"})
    g.call("sw", K_STR, "StartsWith", inp={"SourceString": "@n2s.ReturnValue", "InPrefix": "Body_", "SearchCase": "CaseSensitive"}); g.branch("b", "@sw.ReturnValue")
    g.n("row", "get_row", table=P_DLC_T, inp={"RowName": "@fe.Array Element"}, miss="ignore"); g.brk("br", P_DLC_S, "@row.OutRow")   # row names of the same table
    g.get("gm2", "BodyMods"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gm2.BodyMods", "NewItem": "@fe.Array Element"})
    g.get("gc2", "BodyCaptions"); g.call("ma", K_MAP, "Map_Add", inp={"TargetMap": "@gc2.BodyCaptions", "Key": "@fe.Array Element", "Value": "@br.Caption"})
    g.chain("entry", "cl", "mc", "rn", "fe"); g.chain("fe", "b", "row", "add", "ma")
    return fn("Scan Body Mods", graph=g)


def f_apply_body():
    """None = default mesh (remembered from Jodi on the first call: vanilla or ~mods override), otherwise load /Game/Mod/<name>/Female.Female.
    Then vanilla `Load Player Makeup` (skin/eyes/lashes reliably re-applied) + `Reset Clothes Physics`. Not loadable -> default + notice."""
    g = G()
    g.get("gpl", "Player"); g.get("gmc", "Mesh", cls=E_CHARACTER); g.link("gpl.Player", "gmc.self")
    g.get("gsk", "SkeletalMesh", cls=E_SKINNED); g.link("gmc.Mesh", "gsk.self")
    g.get("gst", "StandardMesh"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gst.StandardMesh"}); g.branch("bv", "@iv.ReturnValue")
    g.set("sst", "StandardMesh", inp={"StandardMesh": "@gsk.SkeletalMesh"})
    g.call("isn", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "None"}); g.branch("bn", "@isn.ReturnValue")
    g.get("gst2", "StandardMesh"); g.set("sm1", "BodyMesh", inp={"BodyMesh": "@gst2.StandardMesh"}); g.set("sc1", "CurrentBody", inp={"CurrentBody": "None"})
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "/Game/Mod/", "B": "@n2s.ReturnValue"}); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "/Female.Female"})
    g.call("sp", K_SYS, "MakeSoftObjectPath", inp={"PathString": "@c2.ReturnValue"}); g.call("sr", K_SYS, "Conv_SoftObjPathToSoftObjRef", inp={"SoftObjectPath": "@sp.ReturnValue"})
    g.call("ld", K_SYS, "LoadAsset_Blocking", inp={"Asset": "@sr.ReturnValue"}); g.cast("ck", E_SKELMESH, "@ld.ReturnValue", pure=False)
    g.set("sm2", "BodyMesh", inp={"BodyMesh": "@ck.AsSkeletalMesh"}); g.set("sc2", "CurrentBody", inp={"CurrentBody": "@entry.name"})
    g.call("e1", K_STR, "Concat_StrStr", inp={"A": ts(g, "mk", "Msg_BodyMissing"), "B": "@n2s.ReturnValue"}); pop(g, "pop", text_from_str(g, "pt", "@e1.ReturnValue"))
    g.get("gst3", "StandardMesh"); g.set("sm3", "BodyMesh", inp={"BodyMesh": "@gst3.StandardMesh"}); g.set("sc3", "CurrentBody", inp={"CurrentBody": "None"})
    g.get("gbm", "BodyMesh"); g.call("ssm", E_SKINNED, "SetSkeletalMesh", inp={"self": "@gmc.Mesh", "NewMesh": "@gbm.BodyMesh", "bReinitPose": "true"})
    g.get("gpl2", "Player"); g.call("lpm", P_JODI, "Load Player Makeup", inp={"self": "@gpl2.Player"})
    g.get("gpl3", "Player"); g.call("rcp", P_CPB, "Reset Clothes Physics", inp={"self": "@gpl3.Player"})
    g.chain("entry", "bv", "bn", "sm1", "sc1", "ssm", "lpm", "rcp"); g.chain("bv:else", "sst", "bn")
    g.chain("bn:else", "ld", "ck", "sm2", "sc2", "ssm"); g.chain("ck:CastFailed", "pop", "sm3", "sc3", "ssm")
    return fn("Apply Body", [param("name", "name")], graph=g)


def f_apply_saved_body():
    """Via timer after BeginPlay: apply the saved body (only with a valid player, e.g. not in the main menu)."""
    g = G()
    g.get("gpl", "Player"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gpl.Player"}); g.branch("bp", "@iv.ReturnValue")
    g.get("gv", "BodyVariant"); g.call("isn", K_MATH, "EqualEqual_NameName", inp={"A": "@gv.BodyVariant", "B": "None"}); g.branch("b", "@isn.ReturnValue")
    g.n("ap", "call_self", function="Apply Body", inp={"name": "@gv.BodyVariant"})
    g.chain("entry", "bp", "b"); g.chain("b:else", "ap")
    return fn("Apply Saved Body", graph=g)


def f_select_body():
    """Chip click on the body page: 'BodyStd' = default, otherwise the mod row name; save the choice, redraw the page."""
    g = G()
    g.call("iss", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "BodyStd"}); g.branch("b", "@iss.ReturnValue")
    g.n("a0", "call_self", function="Apply Body", inp={"name": "None"}); g.n("a1", "call_self", function="Apply Body", inp={"name": "@entry.name"})
    g.get("gc", "CurrentBody"); g.set("sv", "BodyVariant", inp={"BodyVariant": "@gc.CurrentBody"})
    g.n("ss", "call_self", function="Save Settings"); g.n("rb", "call_self", function="Rebuild Body")
    g.chain("entry", "b", "a0", "sv", "ss", "rb"); g.chain("b:else", "a1", "sv")
    return fn("Select Body", [param("name", "name")], graph=g)


# ---------------- Event Graph ----------------
def event_graph():
    g = G()
    g.event("bp", E_ACTOR, "ReceiveBeginPlay")
    g.call("own", E_ACTOR, "GetOwner"); g.cast("cpc", P_PC, "@own.ReturnValue", pure=False, miss="ignore")   # spawned by the camera hook with the controller as owner
    g.set("spc", "PC", inp={"PC": "@cpc.AsTKA Controller"})
    g.call("ei", E_ACTOR, "EnableInput", inp={"PlayerController": "@spc.Output_Get"})
    # no Jodi (main menu level): the chain ends here on purpose - no catalog/settings/strings; the next level spawns a new manager
    g.call("gp", E_CTRL, "K2_GetPawn", inp={"self": "@spc.Output_Get"}); g.cast("cj", P_JODI, "@gp.ReturnValue", pure=False, miss="ignore")
    g.set("spl", "Player", inp={"Player": "@cj.AsJodi"})
    g.n("isg", "call_self", function="Init Slot Groups"); g.n("bc", "call_self", function="Build Catalog"); g.n("rs", "call_self", function="Refresh State")
    g.n("lds", "call_self", function="Load Settings")
    # apply the saved body 1 s after BeginPlay (Jodi + mod paks are certainly there by then; the default mesh is remembered)
    g.self_("me"); g.call("tm", K_SYS, "K2_SetTimer", inp={"Object": "@me.self", "FunctionName": "Apply Saved Body", "Time": "1.0", "bLooping": "false"})
    g.self_("me3"); g.call("tmu", K_SYS, "K2_SetTimer", inp={"Object": "@me3.self", "FunctionName": "Fix Loaded Underwear", "Time": "1.5", "bLooping": "false"})
    g.n("dl", "call_self", function="Detect Language"); g.n("ist", "call_self", function="Init Strings"); g.n("apn", "call_self", function="Apply Nude")
    g.chain("bp", "cpc", "spc", "ei", "cj", "spl", "isg", "bc", "lds", "apn", "dl", "ist", "rs", "tm", "tmu")
    # panel key (configurable): ONE "AnyKey" event without consume (no key is taken away from the game or other mods),
    # acts only if the key's display name equals ToggleKey and input is allowed
    g.key("kAny", "AnyKey", consume=False)
    g.call("kdn", K_IN, "Key_GetDisplayName", inp={"Key": "@kAny.Key"}); g.call("kds", K_TXT, "Conv_TextToString", inp={"InText": "@kdn.ReturnValue"})
    g.get("gtk", "ToggleKey"); g.call("tks", K_STR, "Conv_NameToString", inp={"InName": "@gtk.ToggleKey"})
    g.call("keq", K_STR, "EqualEqual_StriStri", inp={"A": "@kds.ReturnValue", "B": "@tks.ReturnValue"}); g.branch("bkey", "@keq.ReturnValue")
    g.get("gpl", "Player"); g.call("ie", P_JODI, "Is Input Enabled ?", inp={"self": "@gpl.Player"})
    g.get("go", "PanelOpen"); g.call("or", K_MATH, "BooleanOR", inp={"A": "@ie.yes", "B": "@go.PanelOpen"}); g.branch("bk", "@or.ReturnValue")
    # Released instead of Pressed: the panel also closes on key-up (no release leak into the game, no double toggle)
    g.n("tp", "call_self", function="Toggle Panel"); g.chain("kAny:Released", "bkey", "bk", "tp")
    # Tick: poll the checkboxes (no delegates)
    g.event("tick", E_ACTOR, "ReceiveTick")
    g.get("tpo", "PanelOpen"); g.branch("tb0", "@tpo.PanelOpen")
    g.get("tp1", "Panel"); g.call("too", W_PANEL, "Get Only Owned", inp={"self": "@tp1.Panel"})
    g.get("tp2", "Panel"); g.call("tof", W_PANEL, "Get Only Fav", inp={"self": "@tp2.Panel"})
    g.get("tp3", "Panel"); g.call("tov", W_PANEL, "Get Only Vanilla", inp={"self": "@tp3.Panel"})
    g.get("tco", "CachedOnlyOwned"); g.get("tcf", "CachedOnlyFav"); g.get("tcv", "CachedOnlyVanilla")
    g.call("tn1", K_MATH, "NotEqual_BoolBool", inp={"A": "@too.yes", "B": "@tco.CachedOnlyOwned"})
    g.call("tn2", K_MATH, "NotEqual_BoolBool", inp={"A": "@tof.yes", "B": "@tcf.CachedOnlyFav"})
    g.call("tn3", K_MATH, "NotEqual_BoolBool", inp={"A": "@tov.yes", "B": "@tcv.CachedOnlyVanilla"})
    g.call("tor0", K_MATH, "BooleanOR", inp={"A": "@tn1.ReturnValue", "B": "@tn2.ReturnValue"})
    g.call("tor", K_MATH, "BooleanOR", inp={"A": "@tor0.ReturnValue", "B": "@tn3.ReturnValue"}); g.branch("tb1", "@tor.ReturnValue")
    g.n("trlf", "call_self", function="Rebuild Left"); g.n("trl", "call_self", function="Rebuild List"); g.n("tsv", "call_self", function="Save Settings")   # Rebuild List refreshes the caches -> persist
    g.get("tco2", "ColorOpen"); g.branch("tbc", "@tco2.ColorOpen"); g.n("tap", "call_self", function="Apply Preview")
    g.get("tpg", "Page"); g.call("tib", K_MATH, "EqualEqual_NameName", inp={"A": "@tpg.Page", "B": "Body"}); g.branch("tbb", "@tib.ReturnValue"); g.n("tpb", "call_self", function="Poll Body")
    g.get("tpg2", "Page"); g.call("tio", K_MATH, "EqualEqual_NameName", inp={"A": "@tpg2.Page", "B": "Options"}); g.branch("tbo", "@tio.ReturnValue"); g.n("tpo2", "call_self", function="Poll Options")
    g.get("tif", "IconFrames"); g.call("tig", K_MATH, "Greater_IntInt", inp={"A": "@tif.IconFrames", "B": "0"}); g.branch("tbi", "@tig.ReturnValue")
    g.get("tif2", "IconFrames"); g.call("tid", K_MATH, "Subtract_IntInt", inp={"A": "@tif2.IconFrames", "B": "1"}); g.set("tis", "IconFrames", inp={"IconFrames": "@tid.ReturnValue"})
    g.get("tif3", "IconFrames"); g.call("tiz", K_MATH, "EqualEqual_IntInt", inp={"A": "@tif3.IconFrames", "B": "0"}); g.branch("tbz", "@tiz.ReturnValue"); g.n("tfi", "call_self", function="Finish Photo")
    g.chain("tick", "tbi", "tis", "tbz", "tfi", "tb0"); g.chain("tbz:else", "tb0"); g.chain("tbi:else", "tb0")
    g.get("tpx", "Panel"); g.call("tsc", W_PANEL, "Sync Check Size", inp={"self": "@tpx.Panel"})
    g.chain("tb0", "tsc", "tbb"); g.chain("tbb", "tpb", "tb1"); g.chain("tbb:else", "tbo", "tpo2", "tb1"); g.chain("tbo:else", "tb1"); g.chain("tb1", "trlf", "trl", "tsv"); g.chain("tb0:else", "tbc", "tap"); g.chain("tb1:else", "tbc")
    # test entry points (editor Python)
    g.custom("tb", "Test Build"); g.n("tb_i", "call_self", function="Init Slot Groups"); g.n("tb_b", "call_self", function="Build Catalog"); g.chain("tb", "tb_i", "tb_b")
    g.custom("tk", "Test Sort Key", [param("s", "string")]); g.n("tk_k", "call_self", function="Sort Key", inp={"s": "@tk.s"})
    g.set("tk_s", "TmpKey", inp={"TmpKey": "@tk_k.key"}); g.chain("tk", "tk_k", "tk_s")
    g.custom("ti", "Test Items", [param("slot", "name")])
    g.n("ti_it", "call_self", function="Items For Slot", inp={"slot": "@ti.slot"}); g.set("ti_si", "TmpSlotItems", inp={"TmpSlotItems": "@ti_it.items"})   # pure -> freeze before the loop
    g.get("ti_gn", "TmpNames"); g.call("ti_clr", K_ARR, "Array_Clear", inp={"TargetArray": "@ti_gn.TmpNames"})
    g.get("ti_gi", "TmpSlotItems"); g.call("ti_len", K_ARR, "Array_Length", inp={"TargetArray": "@ti_gi.TmpSlotItems"}); g.set("ti_cnt", "TmpIdx", inp={"TmpIdx": "@ti_len.ReturnValue"})
    g.set("ti_n0", "TmpName", inp={"TmpName": "None"}); g.set("ti_f0", "TmpFound", inp={"TmpFound": "false"})
    g.get("ti_gi2", "TmpSlotItems"); g.foreach("ti_fe", "@ti_gi2.TmpSlotItems"); g.brk("ti_b", S_ITEM, "@ti_fe.Array Element")
    g.get("ti_gn2", "TmpNames"); g.call("ti_add", K_ARR, "Array_Add", inp={"TargetArray": "@ti_gn2.TmpNames", "NewItem": "@ti_b.Name"})
    g.call("ti_eq0", K_MATH, "EqualEqual_IntInt", inp={"A": "@ti_fe.Array Index", "B": "0"}); g.branch("ti_bb", "@ti_eq0.ReturnValue")
    g.set("ti_sg", "TmpName", inp={"TmpName": "@ti_b.Group"}); g.set("ti_sv", "TmpFound", inp={"TmpFound": "@ti_b.IsVanilla"})
    g.chain("ti", "ti_si", "ti_clr", "ti_cnt", "ti_n0", "ti_f0", "ti_fe"); g.chain("ti_fe", "ti_add", "ti_bb", "ti_sg", "ti_sv")
    g.custom("tf", "Test Filter", [param("slot", "name"), param("group", "name"), param("search", "string"), param("onlyOwned", "bool"), param("onlyFav", "bool"), param("onlyVanilla", "bool")])
    g.n("tf_it", "call_self", function="Filtered Items", inp={"slot": "@tf.slot", "group": "@tf.group", "search": "@tf.search", "onlyOwned": "@tf.onlyOwned", "onlyFav": "@tf.onlyFav", "onlyVanilla": "@tf.onlyVanilla"})
    g.get("tf_gn", "TmpNames"); g.call("tf_clr", K_ARR, "Array_Clear", inp={"TargetArray": "@tf_gn.TmpNames"})
    g.foreach("tf_fe", "@tf_it.items"); g.brk("tf_b", S_ITEM, "@tf_fe.Array Element")
    g.get("tf_gn2", "TmpNames"); g.call("tf_add", K_ARR, "Array_Add", inp={"TargetArray": "@tf_gn2.TmpNames", "NewItem": "@tf_b.Name"})
    g.chain("tf", "tf_it", "tf_clr", "tf_fe"); g.chain("tf_fe", "tf_add")
    g.custom("tfn", "Test Filtered Counts", [param("search", "string"), param("onlyOwned", "bool"), param("onlyFav", "bool"), param("onlyVanilla", "bool")])
    g.n("tfn_c", "call_self", function="Filtered Counts", inp={"search": "@tfn.search", "onlyOwned": "@tfn.onlyOwned", "onlyFav": "@tfn.onlyFav", "onlyVanilla": "@tfn.onlyVanilla"}); g.chain("tfn", "tfn_c")
    g.custom("tchc", "Test Chip Caption", [param("group", "name"), param("full", "bool")]); g.n("tchc_c", "call_self", function="Chip Caption", inp={"group": "@tchc.group", "full": "@tchc.full"})
    g.set("tchc_s", "TmpText", inp={"TmpText": "@tchc_c.caption"}); g.chain("tchc", "tchc_c", "tchc_s")
    g.custom("tssl", "Test Select Slot", [param("name", "name")]); g.n("tssl_s", "call_self", function="Select Slot", inp={"name": "@tssl.name"}); g.chain("tssl", "tssl_s")
    g.custom("tsst", "Test Select SubTab", [param("name", "name")]); g.n("tsst_s", "call_self", function="Select SubTab", inp={"name": "@tsst.name"}); g.chain("tsst", "tsst_s")
    g.custom("tg", "Test Groups", [param("slot", "name")]); g.n("tg_g", "call_self", function="Groups Of Slot", inp={"slot": "@tg.slot"})
    g.get("tg_gn", "TmpNames"); g.call("tg_clr", K_ARR, "Array_Clear", inp={"TargetArray": "@tg_gn.TmpNames"})
    g.foreach("tg_fe", "@tg_g.groups"); g.get("tg_gn2", "TmpNames"); g.call("tg_add", K_ARR, "Array_Add", inp={"TargetArray": "@tg_gn2.TmpNames", "NewItem": "@tg_fe.Array Element"})
    g.chain("tg", "tg_g", "tg_clr", "tg_fe"); g.chain("tg_fe", "tg_add")
    g.custom("tc", "Test Group Caption", [param("group", "name")]); g.n("tc_c", "call_self", function="Group Caption", inp={"group": "@tc.group"})
    g.set("tc_s", "TmpText", inp={"TmpText": "@tc_c.caption"}); g.chain("tc", "tc_c", "tc_s")
    g.custom("ttf", "Test Toggle Fav", [param("name", "name")]); g.n("ttf_t", "call_self", function="Toggle Favorite", inp={"name": "@ttf.name"}); g.chain("ttf", "ttf_t")
    g.custom("tth", "Test Toggle Hidden", [param("name", "name")]); g.n("tth_t", "call_self", function="Toggle Item Hidden", inp={"name": "@tth.name"}); g.chain("tth", "tth_t")
    g.custom("tst2", "Test Set Toggles", [param("owned", "bool"), param("fav", "bool")])
    g.set("tst2_o", "CachedOnlyOwned", inp={"CachedOnlyOwned": "@tst2.owned"}); g.set("tst2_f", "CachedOnlyFav", inp={"CachedOnlyFav": "@tst2.fav"}); g.chain("tst2", "tst2_o", "tst2_f")
    g.custom("tss", "Test Save Settings"); g.n("tss_s", "call_self", function="Save Settings"); g.chain("tss", "tss_s")
    g.custom("tit", "Test Item Tip", [param("name", "name")]); g.n("tit_f", "call_self", function="Find Item", inp={"name": "@tit.name"}); g.n("tit_t", "call_self", function="Item Tip", inp={"item": "@tit_f.item"})
    g.set("tit_s", "TmpText", inp={"TmpText": "@tit_t.tip"}); g.chain("tit", "tit_f", "tit_t", "tit_s")
    g.custom("tsb", "Test Snapshot Body"); g.n("tsb_t", "call_self", function="Take Snapshot"); g.brk("tsb_b", S_SNAP, "@tsb_t.snap")
    g.set("tsb_n", "TmpName", inp={"TmpName": "@tsb_b.Body"}); g.set("tsb_f", "TmpFloat", inp={"TmpFloat": "@tsb_b.Boobs"}); g.chain("tsb", "tsb_t", "tsb_n", "tsb_f")
    g.custom("trt", "Test Reset Theme"); g.n("trt_r", "call_self", function="Reset Theme"); g.n("trt_a", "call_self", function="Apply Theme"); g.chain("trt", "trt_r", "trt_a")
    g.custom("ttc", "Test Theme Color", [param("key", "name")]); g.n("ttc_c", "call_self", function="Theme Color", inp={"key": "@ttc.key"}); g.set("ttc_s", "TmpColor", inp={"TmpColor": "@ttc_c.color"}); g.chain("ttc", "ttc_c", "ttc_s")
    g.custom("tstc", "Test Set Theme Color", [param("key", "name"), param("color", S_LINCOLOR)]); g.n("tstc_s", "call_self", function="Set Theme Color", inp={"key": "@tstc.key", "color": "@tstc.color"}); g.n("tstc_a", "call_self", function="Apply Theme"); g.chain("tstc", "tstc_s", "tstc_a")
    g.custom("tsa", "Test Set Alphas", [param("bg", "float"), param("tile", "float")]); g.set("tsa_b", "BgAlpha", inp={"BgAlpha": "@tsa.bg"}); g.set("tsa_t", "TileAlpha", inp={"TileAlpha": "@tsa.tile"}); g.n("tsa_a", "call_self", function="Apply Theme"); g.chain("tsa", "tsa_b", "tsa_t", "tsa_a")
    g.custom("tlf", "Test Layout Fraction", [param("index", "int")]); g.n("tlf_f", "call_self", function="Layout Fraction", inp={"index": "@tlf.index"}); g.set("tlf_s", "TmpFloat", inp={"TmpFloat": "@tlf_f.fraction"}); g.chain("tlf", "tlf_f", "tlf_s")
    g.custom("tll", "Test Load Looks"); g.n("tll_l", "call_self", function="Load Looks"); g.chain("tll", "tll_l")
    g.custom("tal", "Test Add Look"); g.n("tal_a", "call_self", function="Add Look"); g.chain("tal", "tal_a")
    g.custom("tlk", "Test Looks Count"); g.n("tlk_c", "call_self", function="Looks Count"); g.set("tlk_s", "TmpI", inp={"TmpI": "@tlk_c.n"}); g.chain("tlk", "tlk_c", "tlk_s")
    g.custom("tln", "Test Look Name", [param("index", "int")]); g.n("tln_n", "call_self", function="Look Name", inp={"index": "@tln.index"}); g.set("tln_s", "TmpStr2", inp={"TmpStr2": "@tln_n.name"}); g.chain("tln", "tln_n", "tln_s")
    g.custom("tli", "Test Look Id", [param("index", "int")]); tli_arr = looks_array(g, "tli_a"); g.call("tli_g", K_ARR, "Array_Get", inp={"TargetArray": tli_arr, "Index": "@tli.index"}); g.brk("tli_b", S_LOOK, "@tli_g.Item")
    g.set("tli_s", "TmpI", inp={"TmpI": "@tli_b.Id"}); g.chain("tli", "tli_s")
    g.custom("tsl", "Test Set Look Name", [param("index", "int"), param("name", "string")]); g.n("tsl_s", "call_self", function="Set Look Name", inp={"index": "@tsl.index", "name": "@tsl.name"}); g.chain("tsl", "tsl_s")
    g.custom("tdl", "Test Delete Look", [param("index", "int")]); g.n("tdl_d", "call_self", function="Delete Look", inp={"index": "@tdl.index"}); g.chain("tdl", "tdl_d")
    g.custom("tls", "Test Load Settings"); g.n("tls_l", "call_self", function="Load Settings"); g.chain("tls", "tls_l")
    # Test Legacy Save: write a save like before the versioning (SaveVersion 0, floats 0 = never set, key unset) - SG properties are not editable from Python
    g.custom("tlg", "Test Legacy Save"); tail = ["tlg"]
    for name, val in (("SaveVersion", "0"), ("CamDist", "0.0"), ("ScrollMult", "0.0"), ("ToggleKey", "None")):
        g.get("tlg_g" + name, "Settings"); g.n("tlg_s" + name, "set", var=name, cls=SG, inp={"self": "@tlg_g%s.Settings" % name, name: val}); tail.append("tlg_s" + name)
    g.get("tlg_gs", "Settings"); g.call("tlg_sv", K_GS, "SaveGameToSlot", inp={"SaveGameObject": "@tlg_gs.Settings", "SlotName": "AltUI", "UserIndex": "0"}); g.chain(*tail, "tlg_sv")
    g.custom("tlo", "Test Load Outfits"); g.n("tlo_l", "call_self", function="Load Outfits"); g.chain("tlo", "tlo_l")
    g.custom("tlc", "Test Look Count", [param("type", "name")]); g.n("tlc_c", "call_self", function="Look Count", inp={"type": "@tlc.type"})
    g.set("tlc_s", "TmpI", inp={"TmpI": "@tlc_c.n"}); g.chain("tlc", "tlc_c", "tlc_s")
    g.custom("tlp", "Test Look Caption", [param("type", "name")]); g.n("tlp_c", "call_self", function="Look Caption", inp={"type": "@tlp.type"})
    g.set("tlp_s", "TmpText", inp={"TmpText": "@tlp_c.caption"}); g.chain("tlp", "tlp_c", "tlp_s")
    g.custom("tw", "Test Worn In Slot", [param("slot", "name")]); g.n("tw_w", "call_self", function="Worn In Slot", inp={"slot": "@tw.slot"})
    g.set("tw_s", "TmpName", inp={"TmpName": "@tw_w.name"}); g.chain("tw", "tw_w", "tw_s")
    g.custom("tst", "Test Strings", [param("choice", "int")]); g.set("tst_s", "LangChoice", inp={"LangChoice": "@tst.choice"})
    g.n("tst_d", "call_self", function="Detect Language"); g.n("tst_i", "call_self", function="Init Strings"); g.chain("tst", "tst_s", "tst_d", "tst_i")
    g.custom("ttt", "Test T", [param("key", "name")]); g.n("ttt_t", "call_self", function="T", inp={"key": "@ttt.key"}); g.set("ttt_s", "TmpText", inp={"TmpText": "@ttt_t.text"}); g.chain("ttt", "ttt_s")
    g.custom("tjn", "Test Join Names", [param("names", "name", "array")]); g.n("tjn_c", "call_self", function="Join Names", inp={"names": "@tjn.names"})
    g.set("tjn_s", "TmpStr2", inp={"TmpStr2": "@tjn_c.key"}); g.chain("tjn", "tjn_c", "tjn_s")
    g.custom("ton", "Test Outfit Name", [param("key", "string")]); g.n("ton_c", "call_self", function="Outfit Name By Key", inp={"key": "@ton.key"})
    g.set("ton_s", "TmpStr2", inp={"TmpStr2": "@ton_c.name"}); g.chain("ton", "ton_c", "ton_s")
    g.custom("tsn", "Test Set Outfit Name", [param("key", "string"), param("name", "string")]); g.n("tsn_c", "call_self", function="Set Outfit Name By Key", inp={"key": "@tsn.key", "name": "@tsn.name"}); g.chain("tsn", "tsn_c")
    g.custom("tfc", "Test Focus Code"); g.n("tfc_c", "call_self", function="Focus Code"); g.set("tfc_s", "TmpI", inp={"TmpI": "@tfc_c.code"}); g.chain("tfc", "tfc_c", "tfc_s")
    # Test Decode(code): the arithmetic of Update Focus without a player (h -> TmpI, zoom -> TmpFloat)
    g.custom("tdc", "Test Decode", [param("code", "int")])
    g.call("tdc_h", K_MATH, "Percent_IntInt", inp={"A": "@tdc.code", "B": "100"}); g.call("tdc_v", K_MATH, "Percent_IntInt", inp={"A": "@tdc.code", "B": "1000"})
    g.call("tdc_f0", K_MATH, "Divide_IntInt", inp={"A": "@tdc_v.ReturnValue", "B": "100"}); g.call("tdc_f", K_MATH, "Max", inp={"A": "@tdc_f0.ReturnValue", "B": "1"})
    g.call("tdc_f7", K_MATH, "Multiply_IntInt", inp={"A": "@tdc_f.ReturnValue", "B": "7"}); g.call("tdc_mm", K_MATH, "Add_IntInt", inp={"A": "@tdc_f7.ReturnValue", "B": "15"})
    g.call("tdc_mf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@tdc_mm.ReturnValue"}); g.call("tdc_z", K_MATH, "Divide_FloatFloat", inp={"A": "22.0", "B": "@tdc_mf.ReturnValue"})
    g.set("tdc_si", "TmpI", inp={"TmpI": "@tdc_h.ReturnValue"}); g.set("tdc_sf", "TmpFloat", inp={"TmpFloat": "@tdc_z.ReturnValue"}); g.chain("tdc", "tdc_si", "tdc_sf")
    g.custom("tbm", "Test Body Mods"); g.n("tbm_s", "call_self", function="Scan Body Mods"); g.chain("tbm", "tbm_s")
    g.custom("tcap", "Test Body Caption", [param("name", "name")]); g.get("tcap_g", "BodyCaptions")
    g.call("tcap_f", K_MAP, "Map_Find", inp={"TargetMap": "@tcap_g.BodyCaptions", "Key": "@tcap.name"}); g.set("tcap_s", "TmpText", inp={"TmpText": "@tcap_f.Value"}); g.chain("tcap", "tcap_s")
    # content view
    g.custom("tcop", "Test Content Open", [param("page", "name")]); g.n("tcop_c", "call_self", function="Content Open", inp={"page": "@tcop.page"}); g.set("tcop_s", "TmpBool", inp={"TmpBool": "@tcop_c.yes"}); g.chain("tcop", "tcop_c", "tcop_s")
    g.custom("toc", "Test Open Content", [param("kind", "name"), param("index", "int")]); g.n("toc_o", "call_self", function="Open Content", inp={"kind": "@toc.kind", "index": "@toc.index"}); g.chain("toc", "toc_o")
    g.custom("tcc", "Test Close Content"); g.n("tcc_c", "call_self", function="Close Content"); g.chain("tcc", "tcc_c")
    g.custom("tcs", "Test Content Snapshot", [param("kind", "name"), param("index", "int")]); g.n("tcs_c", "call_self", function="Content Snapshot", inp={"kind": "@tcs.kind", "index": "@tcs.index"})
    g.set("tcs_ok", "TmpBool", inp={"TmpBool": "@tcs_c.ok"}); g.get("tcs_gt", "ViewTitle"); g.set("tcs_st", "TmpStr2", inp={"TmpStr2": "@tcs_gt.ViewTitle"})
    g.get("tcs_gs", "ViewSnap"); g.brk("tcs_b", S_SNAP, "@tcs_gs.ViewSnap")
    g.call("tcs_wl", K_ARR, "Array_Length", inp={"TargetArray": "@tcs_b.Worn"}); g.set("tcs_si", "TmpI", inp={"TmpI": "@tcs_wl.ReturnValue"})
    g.call("tcs_ml", K_MAP, "Map_Length", inp={"TargetMap": "@tcs_b.Makeup"}); g.set("tcs_sx", "TmpIdx", inp={"TmpIdx": "@tcs_ml.ReturnValue"})
    g.set("tcs_sn", "TmpName", inp={"TmpName": "@tcs_b.Skin"}); g.set("tcs_sn2", "TmpName2", inp={"TmpName2": "@tcs_b.Body"})
    g.chain("tcs", "tcs_c", "tcs_ok", "tcs_st", "tcs_si", "tcs_sx", "tcs_sn", "tcs_sn2")
    # Test Add Outfit(names): vanilla outfit struct (Map<Name, Color>, all white) appended to Outfits.outfits
    g.custom("tao", "Test Add Outfit", [param("names", "name", "array")])
    g.get("tao_g0", "TmpFColors"); g.call("tao_clr", K_MAP, "Map_Clear", inp={"TargetMap": "@tao_g0.TmpFColors"})
    g.foreach("tao_fe", "@tao.names"); g.call("tao_lc", K_MATH, "Conv_LinearColorToColor", inp={"InLinearColor": "(R=1,G=1,B=1,A=1)"})
    g.get("tao_g1", "TmpFColors"); g.call("tao_add", K_MAP, "Map_Add", inp={"TargetMap": "@tao_g1.TmpFColors", "Key": "@tao_fe.Array Element", "Value": "@tao_lc.ReturnValue"})
    g.get("tao_g2", "TmpFColors"); g.make("tao_mk", P_OUTFIT_S, **{OUTFIT_MEMBER: "@tao_g2.TmpFColors"})
    g.get("tao_go", "Outfits"); g.get("tao_goa", "outfits", cls=P_OUTFITS); g.link("tao_go.Outfits", "tao_goa.self")
    g.call("tao_aa", K_ARR, "Array_Add", inp={"TargetArray": "@tao_goa.outfits", "NewItem": "@tao_mk.Outfit_Struct"})
    g.chain("tao", "tao_clr", "tao_fe"); g.chain("tao_fe", "tao_add"); g.chain("tao_fe:Completed", "tao_aa")
    # Test Add Preset(skin, hair): preset struct appended to Presets.Data (the vanilla Add New Preset is a stub in the editor)
    g.custom("tadp", "Test Add Preset", [param("skin", "name"), param("hair", "name")])
    g.make("tadp_mk", P_PRESET_S, SkinName="@tadp.skin", HairstyleName="@tadp.hair", Waist="0.4")
    tadp_pd = presets_data(g, "tadp_pd"); g.call("tadp_aa", K_ARR, "Array_Add", inp={"TargetArray": tadp_pd, "NewItem": "@tadp_mk.MakeupPreset_Struct"}); g.chain("tadp", "tadp_aa")
    g.custom("tldp", "Test Load Presets"); g.n("tldp_l", "call_self", function="Load Presets"); g.chain("tldp", "tldp_l")
    g.custom("tgt", "Test Go To", [param("name", "name"), param("slot", "name")]); g.set("tgt_s", "ContextSlot", inp={"ContextSlot": "@tgt.slot"})
    g.n("tgt_g", "call_self", function="Go To Item", inp={"name": "@tgt.name"}); g.chain("tgt", "tgt_s", "tgt_g")
    return g


assets = [blueprint(MGR, mode="augment", variables=[var("Panel", "object:" + W_PANEL), var("Menu", "object:" + W_MENU), var("TmpItems2", T_ITEM, "array"),
                               var("Palette", "object:" + P_PAL), var("ColorItem", "name"), var("ColorOrig", S_LINCOLOR), var("ColorCur", S_LINCOLOR), var("ColorOpen", "bool"),
                               var("OptBgAlpha", "float"), var("OptTileAlpha", "float"), var("TmpSection", "object:" + W_SECTION)],
                    functions=[f_open_color(), f_close_color(), f_apply_preview(), f_toggle(), f_open(), f_close(), f_rebuild_left(), f_rebuild_list(), f_rebuild_subtabs(), f_select_slot(),
                               f_take_off_slot(), f_on_item_clicked(), f_on_item_context(), f_close_menu(), f_on_menu_action(), f_select_subtab(), f_on_search_changed(),
                               f_load_outfits(), f_save_outfits(), f_rebuild_top_tabs(), f_select_page(), f_rebuild_outfits(), f_on_outfit_clicked(), f_on_outfit_context(), f_delete_outfit(),
                               f_in_bag(), f_is_damaged(), f_rebuild_bag(), f_bag_toggle_wear(), f_bag_remove(), f_bag_cleanup(), f_bag_repair(), f_bag_to_wardrobe(), f_put_in_bag(), f_on_bag_item_context(),
                               f_rebuild_hair(), f_hair_clicked(), f_open_hair_color(), f_look_caption(), f_is_look_selected(), f_look_count(), f_rebuild_look_cats(), f_select_look_cat(),
                               f_rebuild_look(), f_look_clicked(), f_rebuild_body(), f_poll_body(), f_save_appearance_data(), f_scan_body_mods(), f_apply_body(), f_apply_saved_body(), f_select_body(), f_apply_strings(), f_select_language(), f_focus_code(), f_update_focus(),
                               f_on_hair_context(), f_hair_reset_color(), f_clothes_reset_color(), f_open_theme_color(), f_apply_theme(), f_select_key(), f_apply_nude(), f_fix_loaded_underwear(), f_start_outfit_rename(), f_join_names(), f_outfit_key(), f_outfit_name_by_key(), f_outfit_name(), f_set_outfit_name_by_key(), f_set_outfit_name(), f_rebuild_options(), f_apply_options(), f_poll_options(),
                               f_load_presets(), f_preset_icon(), f_preset_index(), f_preset_clicked(), f_preset_add(), f_preset_delete(), f_on_preset_context(), f_capture_photo(), f_capture_preset_photo(), f_capture_look_photo(), f_finish_photo(), f_look_icon(),
                               f_load_looks(), f_save_looks(), f_looks_count(), f_add_look(), f_update_look(), f_delete_look(), f_look_name(), f_set_look_name(), f_apply_look(), f_rebuild_looks(), f_on_look_clicked(), f_on_look_context(), f_start_look_rename(),
                               f_select_layout(), f_set_view_shift(), f_rebuild_status(), f_take_snapshot(), f_push_history(), f_apply_snapshot(), history_step("Undo", "UndoStack", "RedoStack"), history_step("Redo", "RedoStack", "UndoStack"),
                               f_content_open(), f_open_content(), f_content_snapshot(), open_content_wrapper("Open Outfit Content", "Outfit"), open_content_wrapper("Open Look Content", "Look"), open_content_wrapper("Open Preset Content", "Preset"), f_close_content(),
                               f_rebuild_content(), f_on_content_item_context(), f_go_to_item(), f_scroll_to_highlight()],
                    event_graph=event_graph())]
write(os.path.join(os.path.dirname(__file__), "..", "50_manager_ui.json"), assets)
