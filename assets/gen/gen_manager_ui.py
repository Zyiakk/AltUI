"""Generates assets/50_manager_ui.json: UI bodies of the manager (augment) + event graph. Runs after 40_widgets.json."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
from bpdsl import *
import bodyscale_groups as bg
from gen_manager import pop, text_from_str, S_ITEM, T_ITEM, MGR, S_SNAP, SG, S_LOOK, SG_LOOKS, LOOKS_SLOT, SG_LOG, LOG_SLOT, LOG_MAX
from strings import LANGS, LIST_CAP
from theme import THEME, DERIVED, BG_ALPHA, TILE_ALPHA
from gen_manager import LAYOUTS, LAYOUT_FRACTIONS

W_ROW = M + "/W_MenuRow"; W_MENU = M + "/W_ContextMenu"
P_PAL = "/Game/Project/UserInterface/PaletteUI"; P_PALR = "/Game/Project/UserInterface/Widgets/Paletter"
W_TOP = M + "/W_TopTab"; W_OUTFIT = M + "/W_OutfitButton"; W_LOOK = M + "/W_LookButton"; W_SECTION = M + "/W_ContentSection"; W_TXT = M + "/W_TextButton"; T_UNDO = M + "/T_Undo"; T_REDO = M + "/T_Redo"; SC = 1.9; P_HOOK = "/Game/Project/Classes/TKA_PlayerCameraManager"; OUTFIT_SLOT = "Outfits"
E_PCM = "/Script/Engine.PlayerCameraManager"; E_CAMA = "/Script/Engine.CameraActor"; E_CAMC = "/Script/Engine.CameraComponent"
W_PANEL = M + "/W_AltUI"; W_HEAD = M + "/W_GroupHeader"; W_TAB = M + "/W_SlotTab"; W_BTN = M + "/W_ClothesButton"; W_SUB = M + "/W_SubTab"; W_SWATCH = M + "/W_ColorSwatch"; W_NAMEROW = M + "/W_NameRow"; W_HSWATCH = M + "/W_HairSwatch"; W_CONFLICT = M + "/W_ConflictRow"


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
    g.get("gp9l", "Panel"); g.get("glof", "LookOnlyFav"); g.call("slof", W_PANEL, "Set Look Only Fav", inp={"self": "@gp9l.Panel", "yes": "@glof.LookOnlyFav"})
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
    g.n("rcd", "call_self", function="Rebuild Catalog If Dirty")
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
    g.chain("entry", "b", "atv"); g.chain("b:else", "cw_cr", "sp", "sm", "sft", "slof", "ibt", "aps", "ath", "atv")
    g.chain("atv", "so", "cur", "im", "bl", "epc", "rs"); g.chain("bl:else", "di", "rs")
    g.n("rst", "call_self", function="Rebuild Status")
    g.n("uf", "call_self", function="Update Focus")
    g.chain("rs", "lo", "lp", "ao", "spo", "svo", "svl", "svp", "spg", "rtt", "rst", "csl", "cx_cr", "smx", "xi", "asl", "bs", "bsl", "scs", "rcd", "rl"); g.chain("bs:else", "rcd"); g.chain("bsl:else", "rcd"); g.chain("rcd", "rl", "rt", "rli", "kf", "uf")
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
    # camera modes end with the panel: free cam -> Stop Free Cam; photo mode -> Try Exit Photo Mode + End Photo Mode (PanelOpen false first: no panel part)
    g.get("gcm", "CamMode"); g.call("is1", K_MATH, "EqualEqual_IntInt", inp={"A": "@gcm.CamMode", "B": "1"}); g.branch("bc1", "@is1.ReturnValue"); g.n("sfc", "call_self", function="Stop Free Cam")
    g.get("gcm2", "CamMode"); g.call("is2", K_MATH, "EqualEqual_IntInt", inp={"A": "@gcm2.CamMode", "B": "2"}); g.branch("bc2", "@is2.ReturnValue")
    g.call("gs", K_GS, "GetGameState"); g.cast("cgs", P_GS2, "@gs.ReturnValue", pure=False, miss="ignore"); g.call("xp", P_GS2, "Try Exit Photo Mode", inp={"self": "@cgs.AsTKA Game State"})
    g.set("so0", "PanelOpen", inp={"PanelOpen": "false"}); g.n("epm", "call_self", function="End Photo Mode")
    g.chain("entry", "bc1", "sfc", "cmn"); g.chain("bc1:else", "bc2", "cgs", "xp", "so0", "epm", "cmn"); g.chain("bc2:else", "cmn")
    g.chain("cmn", "ccl", "b", "rm", "so"); g.chain("b:else", "so"); g.chain("so", "cur", "im", "bl", "epc", "svs"); g.chain("bl:else", "ei", "svs"); g.chain("svs", "sad", "svs0", "svc0")
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
    g.get("gcg0", "CurrentGroup"); g.call("gact", K_MATH, "NotEqual_NameName", inp={"A": "@gcg0.CurrentGroup", "B": "None"})   # a selected group chip filters too
    g.call("fact0", K_MATH, "BooleanOR", inp={"A": "@fa2.ReturnValue", "B": "@sact.ReturnValue"}); g.call("fact", K_MATH, "BooleanOR", inp={"A": "@fact0.ReturnValue", "B": "@gact.ReturnValue"}); g.set("sfa", "TmpBool", inp={"TmpBool": "@fact.ReturnValue"})
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
    g.n("fiw", "call_self", function="Is Worn", inp={"name": "@fb.Name"}); g.n("fio", "call_self", function="Shown Owned", inp={"name": "@fb.Name"})
    g.n("fdm", "call_self", function="Is Damaged", inp={"name": "@fb.Name"}); g.n("fti", "call_self", function="Item Tip", inp={"item": "@ff.Array Element", "kind": "item", "category": ""})
    g.call("fin", W_BTN, "Init", inp={"self": fw, "item": "@ff.Array Element", "worn": "@fiw.yes", "owned": "@fio.yes", "fav": "true", "damaged": "@fdm.yes", "tip": "@fti.tip"})
    g.get("gp4", "Panel"); g.call("af", W_PANEL, "Add Fav", inp={"self": "@gp4.Panel", "widget": fw})
    g.get("gn", "TmpIdx"); g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gn.TmpIdx", "B": "1"}); g.set("sn", "TmpIdx", inp={"TmpIdx": "@inc.ReturnValue"})
    g.get("gn2", "TmpIdx"); g.call("gt0", K_MATH, "Greater_IntInt", inp={"A": "@gn2.TmpIdx", "B": "0"})
    g.get("gp5", "Panel"); g.call("sfv", W_PANEL, "Set Fav Visible", inp={"self": "@gp5.Panel", "visible": "@gt0.ReturnValue"})
    # pass 2: all (alphabetical)
    g.get("gti2", "TmpItems2"); g.foreach("fe", "@gti2.TmpItems2"); g.brk("bi", S_ITEM, "@fe.Array Element")
    bw = create_widget(g, "cb", W_BTN)
    set_manager(g, "smb", W_BTN, bw)
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@bi.Name"}); g.n("io", "call_self", function="Shown Owned", inp={"name": "@bi.Name"})
    g.n("ifv", "call_self", function="Is Favorite", inp={"name": "@bi.Name"})
    g.n("dm", "call_self", function="Is Damaged", inp={"name": "@bi.Name"}); g.n("bti", "call_self", function="Item Tip", inp={"item": "@fe.Array Element", "kind": "item", "category": ""})
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
    g.get("gpg2", "Page"); g.call("ism", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg2.Page", "B": "Manage"}); g.branch("bpm", "@ism.ReturnValue")
    g.n("smc", "call_self", function="Select Manage Cat", inp={"name": "@entry.name"})
    g.n("uf", "call_self", function="Update Focus")
    g.set("hlc", "HighlightItem", inp={"HighlightItem": "None"})
    g.chain("entry", "bpl", "slc"); g.chain("bpl:else", "bpm", "smc"); g.chain("bpm:else", "hlc", "s", "gr", "bk", "rl", "rt", "rli", "uf"); g.chain("bk:else", "sg", "rl"); return fn("Select Slot", [param("name", "name")], graph=g)


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
    g.n("io", "call_self", function="Can Wear", inp={"name": "@entry.name"}); g.branch("bo", "@io.yes")   # owned, in the backpack, or option "not owned items" != locked
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"})
    g.call("msg", K_STR, "Concat_StrStr", inp={"A": ts(g, "mk", "Msg_NotOwned"), "B": "@n2s.ReturnValue"})
    pop(g, "pop", text_from_str(g, "t", "@msg.ReturnValue"))
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@entry.name"}); g.branch("bw", "@iw.yes")
    g.n("to", "call_self", function="Take Off", inp={"name": "@entry.name"}); g.n("we", "call_self", function="Wear", inp={"name": "@entry.name"})
    g.n("rl", "call_self", function="Rebuild Left"); g.n("rli", "call_self", function="Rebuild List")
    g.chain("entry", "cop", "bcv"); g.chain("bcv:else", "bpg", "btw"); g.chain("bpg:else", "bph", "hc"); g.chain("bph:else", "bpl", "lc")
    g.n("ph", "call_self", function="Push History")
    g.chain("bpl:else", "io", "bo", "ph", "bw", "to", "rl", "rli"); g.chain("bw:else", "we", "rl"); g.chain("bo:else", "pop")
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
    g.n("olc", "call_self", function="On Look Item Context", inp={"name": "@entry.name"})   # skin / makeup tiles: mod content (mod rows only) + cancel
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
    rn = menu_row(g, 9, "Rename", tt(g, "rnt", "Menu_Rename"))   # inline display name on the tile
    g.n("fi", "call_self", function="Find Item", inp={"name": "@entry.name"}); g.brk("bi", S_ITEM, "@fi.item")
    # row: only this group + rename group (piece has a group); row: mod content + rename mod (piece comes from a mod) - the rename rows jump to the Manage row
    g.call("gne", K_MATH, "NotEqual_NameName", inp={"A": "@bi.Group", "B": "None"}); g.branch("bog", "@gne.ReturnValue")
    og = menu_row(g, 7, "OnlyGroup", tt(g, "ogt", "Menu_OnlyGroup")); rg = menu_row(g, 10, "RenameGroup", tt(g, "rgt", "Menu_RenameGroup"))
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@entry.name"}); g.branch("bmc", "@imd.found")
    mc = menu_row(g, 8, "ModContent", tt(g, "mct", "Menu_ModContent")); rm = menu_row(g, 11, "RenameMod", tt(g, "rmt", "Menu_RenameMod"))
    # row: colour (only if colour-adjustable and worn)
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
    g.chain("bpc:else", "bph", "ohc"); g.chain("bph:else", "bpp", "pix", "opc"); g.chain("bpp:else", "olc")
    g.chain("clr", "cr1_cr", "sr1", "ri1", "ar1", *hr, *rn, "fi", "bog", *og, *rg, "bmc", *mc, *rm, "bc", "cr2_cr", "sr2", "ri2", "ar2", "gcr", "brc", *rr, "ib", "bpb", *pb, "cr3_cr"); g.chain("bog:else", "bmc"); g.chain("bmc:else", "bc"); g.chain("bc:else", "ib"); g.chain("brc:else", "ib"); g.chain("bpb:else", "cr3_cr")
    g.chain("cr3_cr", "sr3", "ri3", "ar3", "atv", "mp", "spv")
    return fn("On Item Context", [param("name", "name")], graph=g)


def simple_menu(name, rows, pre=None, cond=None):
    """Context menu with fixed rows [(action, caption)]; pre(g) may create nodes and returns exec ids that run before the menu.
    cond = {action: "Item Mod"}: that row appears only when Item Mod(entry.name) is found (the menu function has a `name` parameter)."""
    g = G(); head = ["entry"] + (pre(g) if pre else [])
    g.get("gm", "Menu"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gm.Menu"}); g.branch("b", "@iv.ReturnValue")
    mw = create_widget(g, "cm", W_MENU); g.set("sm", "Menu", inp={"Menu": mw}); set_manager(g, "smm", W_MENU, mw)
    g.get("gm2", "Menu"); g.call("clr", W_MENU, "Clear Rows", inp={"self": "@gm2.Menu"})
    tail = ["clr"]; joins = []
    for i, (action, cap) in enumerate(rows):
        row = menu_row(g, i, action, cap if cap.startswith("@") else tt(g, "t%d" % i, cap))   # cap = key of the Strings table or a text pin
        if cond and action in cond:
            g.n("cq%d" % i, "call_self", function=cond[action], inp={"row": "@entry.name"}); g.branch("cb%d" % i, "@cq%d.found" % i)
            g.chain(*tail, "cb%d" % i, *row); joins.append("cb%d:else" % i); tail = [row[-1]]
        else:
            g.chain(*tail, row[0]); [g.chain(j, row[0]) for j in joins]; joins = []; tail = row
    g.get("gm6", "Menu"); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@gm6.Menu", "ZOrder": "110"})
    g.call("mp", "/Script/UMG.WidgetLayoutLibrary", "GetMousePositionOnViewport")
    g.get("gm7", "Menu"); g.call("spv", E_USERWIDGET, "SetPositionInViewport", inp={"self": "@gm7.Menu", "Position": "@mp.ReturnValue", "bRemoveDPIScale": "false"})
    g.chain(*head, "b", "clr"); g.chain("b:else", "cm_cr", "sm", "smm", "clr"); g.chain(*tail, "atv", "mp", "spv"); [g.chain(j, "atv") for j in joins]
    return g


def f_on_look_item_context():
    """Skin / make-up tile menu: favourite on/off, hide/unhide, rename, [rename mod, only this mod, mod content when the row comes from a mod], cancel."""
    def pre(g):
        g.set("sci", "ContextItem", inp={"ContextItem": "@entry.name"})
        g.n("isf", "call_self", function="Is Look Favorite", inp={"name": "@entry.name"}); g.call("fs", K_MATH, "SelectString", inp={"A": ts(g, "fr", "Menu_FavRemove"), "B": ts(g, "fa", "Menu_FavAdd"), "bPickA": "@isf.yes"})
        g.call("ft", K_TXT, "Conv_StringToText", inp={"InString": "@fs.ReturnValue"})
        g.n("ihd", "call_self", function="Is Look Hidden", inp={"name": "@entry.name"}); g.call("hs", K_MATH, "SelectString", inp={"A": ts(g, "hu", "Menu_Unhide"), "B": ts(g, "hh", "Menu_Hide"), "bPickA": "@ihd.yes"})
        g.call("ht", K_TXT, "Conv_StringToText", inp={"InString": "@hs.ReturnValue"}); return ["sci", "isf", "ihd"]
    g = simple_menu("On Look Item Context", [("LookFav", "@ft.ReturnValue"), ("LookHide", "@ht.ReturnValue"), ("Rename", "Menu_Rename"), ("RenameMod", "Menu_RenameMod"), ("LookOnlyMod", "Menu_LookOnlyMod"), ("ModContent", "Menu_ModContent"), ("Cancel", "Menu_Cancel")],
                    pre=pre, cond={"RenameMod": "Item Mod", "LookOnlyMod": "Item Mod", "ModContent": "Item Mod"})
    return fn("On Look Item Context", [param("name", "name")], graph=g)


def f_on_hair_context():
    """Hair tile menu: reset colour, [mod content when the hairstyle comes from a mod], cancel."""
    def pre(g):
        g.set("sci", "ContextItem", inp={"ContextItem": "@entry.name"}); return ["sci"]
    g = simple_menu("On Hair Context", [("Rename", "Menu_Rename"), ("HairResetColor", "Menu_HairReset"), ("ModContent", "Menu_ModContent"), ("Cancel", "Menu_Cancel")], pre=pre, cond={"ModContent": "Item Mod"})
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
import hair_colors as hc
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
    g.get("gp2", "Panel"); g.get("gun", "Unlimited"); g.get("gpn", "PanToSlot"); g.get("gan", "AllowNude"); g.get("gmg", "MergeGroups"); g.get("gmm", "MergeMods"); g.get("gtp", "TipNoPrefix"); g.get("gtn", "TipNoIds")
    g.call("su", W_PANEL, "Set Option Checks", inp={"self": "@gp2.Panel", "unlimited": "@gun.Unlimited", "pan": "@gpn.PanToSlot", "nude": "@gan.AllowNude", "merge": "@gmg.MergeGroups", "mergemods": "@gmm.MergeMods", "tipnoprefix": "@gtp.TipNoPrefix", "tipnoids": "@gtn.TipNoIds"})
    # layout chips (W_SubTab: click -> Select SubTab -> Select Layout), display order by size, stable indices
    g.get("gp3", "Panel"); g.call("cl", W_PANEL, "Clear Layout Chips", inp={"self": "@gp3.Panel"}); tail = ["entry", "os", "oc", "of", "od", "oba", "ota", "ogl", "och", "sv", "su", "cl"]
    for i, (idx, key) in enumerate(LAYOUTS):
        cw = create_widget(g, "cc%d" % i, W_SUB); set_manager(g, "cm%d" % i, W_SUB, cw)
        g.get("glf%d" % i, "LeftFree"); g.call("eq%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": "@glf%d.LeftFree" % i, "B": str(idx)})
        g.call("ci%d" % i, W_SUB, "Init", inp={"self": cw, "group": "Layout%d" % idx, "caption": tt(g, "ct%d" % i, key), "selected": "@eq%d.ReturnValue" % i})
        g.get("gpc%d" % i, "Panel"); g.call("ac%d" % i, W_PANEL, "Add Layout Chip", inp={"self": "@gpc%d.Panel" % i, "widget": cw})
        tail += ["cc%d_cr" % i, "cm%d" % i, "ci%d" % i, "ac%d" % i, hslot_pad(g, "pd%d" % i, cw, 8)]
    # not-owned mode chips (group "Unowned<n>"), active = UnownedMode
    g.get("gpu", "Panel"); g.call("clu", W_PANEL, "Clear Unowned Chips", inp={"self": "@gpu.Panel"}); tail.append("clu")
    for i in range(3):
        uw = create_widget(g, "uc%d" % i, W_SUB); set_manager(g, "um%d" % i, W_SUB, uw)
        g.get("gum%d" % i, "UnownedMode"); g.call("ueq%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": "@gum%d.UnownedMode" % i, "B": str(i)})
        g.call("uci%d" % i, W_SUB, "Init", inp={"self": uw, "group": "Unowned%d" % i, "caption": tt(g, "ut%d" % i, "Chip_Unowned%d" % i), "selected": "@ueq%d.ReturnValue" % i})
        g.get("gpv%d" % i, "Panel"); g.call("ua%d" % i, W_PANEL, "Add Unowned Chip", inp={"self": "@gpv%d.Panel" % i, "widget": uw})
        tail += ["uc%d_cr" % i, "um%d" % i, "uci%d" % i, "ua%d" % i, hslot_pad(g, "up%d" % i, uw, 8)]
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
    g.n("rcf", "call_self", function="Rebuild Conflicts"); tail.append("rcf")
    g.chain(*tail); return fn("Rebuild Options", graph=g)


def f_rebuild_conflicts():
    """Options block "Slot conflicts": global links (all free / Vanilla), then per slot (Slots order) with at least one conflict pair a
    W_ConflictRow - caption, one W_SubTab chip per partner (group "Cf:<slot>|<partner>", selected = freed), links "all free" / "Vanilla"."""
    g = G(); g.get("gp", "Panel"); g.call("pv", K_SYS, "IsValid", inp={"Object": "@gp.Panel"}); g.branch("bpv", "@pv.ReturnValue")
    g.get("gp0", "Panel"); g.call("cl", W_PANEL, "Clear Conflict Rows", inp={"self": "@gp0.Panel"}); g.get("gp1", "Panel"); g.call("cll", W_PANEL, "Clear Conflict Links", inp={"self": "@gp1.Panel"})
    tail = ["entry", "bpv", "cl", "cll"]
    for i, (action, key) in enumerate((("ConflictsFreeAll", "Btn_FreeAll"), ("ConflictsReset", "Btn_Vanilla"))):
        lw = create_widget(g, "gl%d" % i, W_TXT); set_manager(g, "glm%d" % i, W_TXT, lw)
        g.call("gli%d" % i, W_TXT, "Init", inp={"self": lw, "action": action, "caption": tt(g, "glt%d" % i, key)})
        g.get("gpl%d" % i, "Panel"); g.call("gla%d" % i, W_PANEL, "Add Conflict Link", inp={"self": "@gpl%d.Panel" % i, "widget": lw}); tail += ["gl%d_cr" % i, "glm%d" % i, "gli%d" % i, "gla%d" % i, hslot_pad(g, "glp%d" % i, lw, 16)]
    g.set("si0", "TmpI", inp={"TmpI": "0"}); tail.append("si0")   # row counter for the zebra stripes
    g.get("gsl", "Slots"); g.foreach("fs", "@gsl.Slots"); g.call("ss", K_STR, "Conv_NameToString", inp={"InName": "@fs.Array Element"})
    # partners of this slot: every pair "A|B" with A == slot or B == slot
    g.get("gn0", "TmpNames3"); g.call("n3c", K_ARR, "Array_Clear", inp={"TargetArray": "@gn0.TmpNames3"})
    g.get("gcp", "ConflictPairs"); g.foreach("fp", "@gcp.ConflictPairs"); g.call("ps", K_STR, "Conv_NameToString", inp={"InName": "@fp.Array Element"})
    g.call("sp", K_STR, "Split", inp={"SourceString": "@ps.ReturnValue", "InStr": "|", "SearchCase": "CaseSensitive", "SearchDir": "FromStart"})
    g.call("eqa", K_STR, "EqualEqual_StrStr", inp={"A": "@sp.LeftS", "B": "@ss.ReturnValue"}); g.call("eqb", K_STR, "EqualEqual_StrStr", inp={"A": "@sp.RightS", "B": "@ss.ReturnValue"})
    g.call("psel", K_MATH, "SelectString", inp={"A": "@sp.RightS", "B": "@sp.LeftS", "bPickA": "@eqa.ReturnValue"}); g.call("pn", K_STR, "Conv_StringToName", inp={"InString": "@psel.ReturnValue"})
    g.call("hit", K_MATH, "BooleanOR", inp={"A": "@eqa.ReturnValue", "B": "@eqb.ReturnValue"}); g.branch("bh", "@hit.ReturnValue")
    g.get("gn1", "TmpNames3"); g.call("n3a", K_ARR, "Array_AddUnique", inp={"TargetArray": "@gn1.TmpNames3", "NewItem": "@pn.ReturnValue"})
    g.get("gn2", "TmpNames3"); g.call("n3l", K_ARR, "Array_Length", inp={"TargetArray": "@gn2.TmpNames3"}); g.call("n3g", K_MATH, "Greater_IntInt", inp={"A": "@n3l.ReturnValue", "B": "0"}); g.branch("bany", "@n3g.ReturnValue")
    rw = create_widget(g, "cr", W_CONFLICT); set_manager(g, "crm", W_CONFLICT, rw)
    g.get("gti", "TmpI"); g.call("rem", K_MATH, "Percent_IntInt", inp={"A": "@gti.TmpI", "B": "2"}); g.call("even", K_MATH, "EqualEqual_IntInt", inp={"A": "@rem.ReturnValue", "B": "0"})
    g.call("cri", W_CONFLICT, "Init", inp={"self": rw, "caption": key_text(g, "cap", "Slot_", "@fs.Array Element"), "tinted": "@even.ReturnValue"})
    g.get("gti2", "TmpI"); g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gti2.TmpI", "B": "1"}); g.set("si1", "TmpI", inp={"TmpI": "@inc.ReturnValue"})
    # chips (partner order = Slots order: iterate Slots again, keep the ones in TmpNames3)
    g.get("gsl2", "Slots"); g.foreach("fq", "@gsl2.Slots"); g.get("gn3", "TmpNames3"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gn3.TmpNames3", "ItemToFind": "@fq.Array Element"}); g.branch("bq", "@has.ReturnValue")
    cw = create_widget(g, "cc", W_SUB); set_manager(g, "ccm", W_SUB, cw)
    g.call("qs", K_STR, "Conv_NameToString", inp={"InName": "@fq.Array Element"}); g.call("k1", K_STR, "Concat_StrStr", inp={"A": "Cf:", "B": "@ss.ReturnValue"}); g.call("k2", K_STR, "Concat_StrStr", inp={"A": "@k1.ReturnValue", "B": "|"})
    g.call("k3", K_STR, "Concat_StrStr", inp={"A": "@k2.ReturnValue", "B": "@qs.ReturnValue"}); g.call("kn", K_STR, "Conv_StringToName", inp={"InString": "@k3.ReturnValue"})
    g.n("fr", "call_self", function="Is Freed", inp={"a": "@fs.Array Element", "b": "@fq.Array Element"})
    g.call("cci", W_SUB, "Init", inp={"self": cw, "group": "@kn.ReturnValue", "caption": key_text(g, "qcap", "Slot_", "@fq.Array Element"), "selected": "@fr.yes"})
    g.call("cca", W_CONFLICT, "Add Chip", inp={"self": rw, "widget": cw})
    # row links
    for i, (prefix, key) in enumerate((("CfAll:", "Btn_FreeAll"), ("CfReset:", "Btn_Vanilla"))):
        lw = create_widget(g, "rl%d" % i, W_TXT); set_manager(g, "rlm%d" % i, W_TXT, lw)
        g.call("ra%d" % i, K_STR, "Concat_StrStr", inp={"A": prefix, "B": "@ss.ReturnValue"}); g.call("ran%d" % i, K_STR, "Conv_StringToName", inp={"InString": "@ra%d.ReturnValue" % i})
        g.call("rli%d" % i, W_TXT, "Init", inp={"self": lw, "action": "@ran%d.ReturnValue" % i, "caption": tt(g, "rlt%d" % i, key)})
        g.call("rla%d" % i, W_CONFLICT, "Add Link", inp={"self": rw, "widget": lw})
    g.get("gpa", "Panel"); g.call("ar", W_PANEL, "Add Conflict Row", inp={"self": "@gpa.Panel", "widget": rw})
    g.chain(*tail, "fs"); g.chain("fs", "n3c", "fp"); g.chain("fp", "bh", "n3a"); g.chain("fp:Completed", "bany", "cr_cr", "crm", "cri", "fq"); g.chain("fq", "bq", "cc_cr", "ccm", "cci", "cca")
    g.chain("fq:Completed", "rl0_cr", "rlm0", "rli0", "rla0", "rl1_cr", "rlm1", "rli1", "rla1", "ar", "si1")
    return fn("Rebuild Conflicts", graph=g)


def f_toggle_conflict():
    """Chip "Cf:<a>|<b>" clicked: flip the freed state of the pair, redraw the block."""
    g = G(); g.call("ns", K_STR, "Conv_NameToString", inp={"InName": "@entry.key"}); g.call("rest", K_STR, "GetSubstring", inp={"SourceString": "@ns.ReturnValue", "StartIndex": "3", "Length": "1000"})
    g.call("sp", K_STR, "Split", inp={"SourceString": "@rest.ReturnValue", "InStr": "|", "SearchCase": "CaseSensitive", "SearchDir": "FromStart"})
    g.call("an", K_STR, "Conv_StringToName", inp={"InString": "@sp.LeftS"}); g.call("bn", K_STR, "Conv_StringToName", inp={"InString": "@sp.RightS"})
    g.n("fr", "call_self", function="Is Freed", inp={"a": "@an.ReturnValue", "b": "@bn.ReturnValue"}); g.call("nf", K_MATH, "Not_PreBool", inp={"A": "@fr.yes"})
    g.n("sf", "call_self", function="Set Freed", inp={"a": "@an.ReturnValue", "b": "@bn.ReturnValue", "freed": "@nf.ReturnValue"}); g.n("rc", "call_self", function="Rebuild Conflicts")
    g.chain("entry", "sf", "rc")
    return fn("Toggle Conflict", [param("key", "name")], graph=g)


def f_free_slot():
    """All pairs of one slot freed (true) or back to Vanilla (false)."""
    g = G(); g.call("ss", K_STR, "Conv_NameToString", inp={"InName": "@entry.slot"})
    g.get("gcp", "ConflictPairs"); g.set("scp", "TmpNames3", inp={"TmpNames3": "@gcp.ConflictPairs"}); g.get("gn", "TmpNames3"); g.foreach("fp", "@gn.TmpNames3")
    g.call("ps", K_STR, "Conv_NameToString", inp={"InName": "@fp.Array Element"}); g.call("sp", K_STR, "Split", inp={"SourceString": "@ps.ReturnValue", "InStr": "|", "SearchCase": "CaseSensitive", "SearchDir": "FromStart"})
    g.call("eqa", K_STR, "EqualEqual_StrStr", inp={"A": "@sp.LeftS", "B": "@ss.ReturnValue"}); g.call("eqb", K_STR, "EqualEqual_StrStr", inp={"A": "@sp.RightS", "B": "@ss.ReturnValue"})
    g.call("hit", K_MATH, "BooleanOR", inp={"A": "@eqa.ReturnValue", "B": "@eqb.ReturnValue"}); g.branch("bh", "@hit.ReturnValue")
    g.call("an", K_STR, "Conv_StringToName", inp={"InString": "@sp.LeftS"}); g.call("bn", K_STR, "Conv_StringToName", inp={"InString": "@sp.RightS"})
    g.n("sf", "call_self", function="Set Freed", inp={"a": "@an.ReturnValue", "b": "@bn.ReturnValue", "freed": "@entry.freed"}); g.n("rc", "call_self", function="Rebuild Conflicts")
    g.chain("entry", "scp", "fp"); g.chain("fp", "bh", "sf"); g.chain("fp:Completed", "rc")
    return fn("Free Slot", [param("slot", "name"), param("freed", "bool")], graph=g)


def f_free_all():
    """Every pair freed (true: FreedConflicts = ConflictPairs) or Vanilla (false: empty); saved, block redrawn."""
    g = G(); g.branch("b", "@entry.freed"); g.get("gcp", "ConflictPairs"); g.set("s1", "FreedConflicts", inp={"FreedConflicts": "@gcp.ConflictPairs"})
    g.get("gf", "FreedConflicts"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gf.FreedConflicts"})
    g.n("sv", "call_self", function="Save Settings"); g.n("rc", "call_self", function="Rebuild Conflicts")
    g.chain("entry", "b", "s1", "sv", "rc"); g.chain("b:else", "clr", "sv")
    return fn("Free All", [param("freed", "bool")], graph=g)


def f_select_layout():
    g = G(); tail = ["entry"]
    for i in range(5):
        g.call("e%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Layout%d" % i}); g.branch("b%d" % i, "@e%d.ReturnValue" % i)
        g.set("s%d" % i, "LeftFree", inp={"LeftFree": str(i)}); g.chain(*tail, "b%d" % i, "s%d" % i); tail = ["b%d:else" % i]
    g.n("ap", "call_self", function="Apply Options"); g.n("ro", "call_self", function="Rebuild Options")
    for i in range(5): g.chain("s%d" % i, "ap")
    g.chain("ap", "ro"); return fn("Select Layout", [param("name", "name")], graph=g)


def f_select_unowned():
    """Chip "Unowned<n>" -> UnownedMode; tiles and looks rebuild (tile state / wearability changed)."""
    g = G(); tail = ["entry"]
    for i in range(3):
        g.call("e%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Unowned%d" % i}); g.branch("b%d" % i, "@e%d.ReturnValue" % i)
        g.set("s%d" % i, "UnownedMode", inp={"UnownedMode": str(i)}); g.chain(*tail, "b%d" % i, "s%d" % i); tail = ["b%d:else" % i]
    g.n("sv", "call_self", function="Save Settings"); g.n("ro", "call_self", function="Rebuild Options"); g.n("rli", "call_self", function="Rebuild List"); g.n("rlk", "call_self", function="Rebuild Looks")
    for i in range(3): g.chain("s%d" % i, "sv")
    g.chain("sv", "ro", "rli", "rlk"); return fn("Select Unowned", [param("name", "name")], graph=g)


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
    g.get("gvs", "ViewShift"); g.get("gcmv", "CamMode"); g.call("cm0", K_MATH, "EqualEqual_IntInt", inp={"A": "@gcmv.CamMode", "B": "0"})
    g.call("vsel", K_MATH, "SelectFloat", inp={"A": "@gvs.ViewShift", "B": "0.0", "bPickA": "@cm0.ReturnValue"})   # free cam / photo mode: the hook must pass the view target through
    g.n("sv", "set", var="ViewShift", cls=P_HOOK, inp={"self": "@ch.AsTKA Player Camera Manager", "ViewShift": "@vsel.ReturnValue"})
    g.get("gcf", "CamFov"); g.n("sf", "set", var="FovScale", cls=P_HOOK, inp={"self": "@ch.AsTKA Player Camera Manager", "FovScale": "@gcf.CamFov"})
    g.get("gcd", "CamDist"); g.n("sd", "set", var="DistScale", cls=P_HOOK, inp={"self": "@ch.AsTKA Player Camera Manager", "DistScale": "@gcd.CamDist"})
    g.get("gfo", "FocusOn"); g.n("sfo", "set", var="FocusOn", cls=P_HOOK, inp={"self": "@ch.AsTKA Player Camera Manager", "FocusOn": "@gfo.FocusOn"})
    g.get("gfz", "FocusZ"); g.n("sfz", "set", var="FocusZ", cls=P_HOOK, inp={"self": "@ch.AsTKA Player Camera Manager", "FocusZ": "@gfz.FocusZ"})
    g.get("gfm", "FocusZoom"); g.n("sfm", "set", var="FocusZoom", cls=P_HOOK, inp={"self": "@ch.AsTKA Player Camera Manager", "FocusZoom": "@gfm.FocusZoom"})
    g.chain("entry", "ch", "sv", "sf", "sd", "sfo", "sfz", "sfm"); return fn("Set View Shift", graph=g)



# ---------------- Free cam (own CameraActor as view target) + the game's photo mode ----------------
FREE_TRACE_R = 12.0; FREE_TRACE_GAP = 2.0; FREE_PITCH = 85.0; FREE_LOOK = 0.6; FREE_FAST = 3.0; FREE_WHEEL = 1.25; FREE_SPEED_MIN = 50.0; FREE_SPEED_MAX = 1000.0
S_VEC2 = "struct:/Script/CoreUObject.Vector2D"; P_CAMIN = M + "/BP_CamInput"


def bp_cam_input():
    """Helper actor for the free cam: one consuming AnyKey event on top of the controller's input stack, so the game's own
    Esc / Tab / Backspace / F9 bindings do not fire while the viewport has the input (GameOnly mode = raw mouse, no cursor warps).
    Released: panel key -> Close Panel, Escape -> Stop Free Cam; everything else is swallowed. Movement keys are polled (IsInputKeyDown)."""
    g = G(); g.key("k", "AnyKey")
    g.branch("bp0", "false")   # pressed: bound (so it is consumed), nothing to do
    g.call("kdn", K_IN, "Key_GetDisplayName", inp={"Key": "@k.Key"}); g.call("kds", K_TXT, "Conv_TextToString", inp={"InText": "@kdn.ReturnValue"})
    g.get("gm", "Manager"); g.get("gtk", "ToggleKey", cls=MGR); g.link("gm.Manager", "gtk.self"); g.call("tks", K_STR, "Conv_NameToString", inp={"InName": "@gtk.ToggleKey"})
    g.call("keq", K_STR, "EqualEqual_StriStri", inp={"A": "@kds.ReturnValue", "B": "@tks.ReturnValue"}); g.branch("btk", "@keq.ReturnValue")
    g.get("gm2", "Manager"); g.call("cp", MGR, "Close Panel", inp={"self": "@gm2.Manager"})
    g.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@k.Key", "B": "Escape"}); g.branch("besc", "@esc.ReturnValue")
    g.get("gm3", "Manager"); g.call("sfc", MGR, "Stop Free Cam", inp={"self": "@gm3.Manager"})
    g.chain("k:Pressed", "bp0"); g.chain("k:Released", "btk", "cp"); g.chain("btk:else", "besc", "sfc")
    return blueprint(P_CAMIN, E_ACTOR, variables=[var("Manager", "object:" + MGR)], event_graph=g)


def f_start_free_cam():
    """CameraActor at the current camera pose (seamless cut), view target, ViewShift 0 to the hook, panel hidden, cursor off,
    input to the game viewport (GameOnly: high-precision mouse capture -> GetInputMouseDelta, keys via IsInputKeyDown), BP_CamInput on top."""
    g = G(); g.get("gcm", "CamMode"); g.call("is0", K_MATH, "EqualEqual_IntInt", inp={"A": "@gcm.CamMode", "B": "0"}); g.branch("b0", "@is0.ReturnValue")
    g.n("cmn", "call_self", function="Close Menu"); g.n("ccl", "call_self", function="Close Color")
    g.set("scm", "CamMode", inp={"CamMode": "1"})
    g.get("gpc", "PC"); g.get("gpcm", "PlayerCameraManager", cls=E_PC); g.link("gpc.PC", "gpcm.self")
    g.call("loc", E_PCM, "GetCameraLocation", inp={"self": "@gpcm.PlayerCameraManager"}); g.call("rot", E_PCM, "GetCameraRotation", inp={"self": "@gpcm.PlayerCameraManager"})
    g.call("fov", E_PCM, "GetFOVAngle", inp={"self": "@gpcm.PlayerCameraManager"}); g.call("br", K_MATH, "BreakRotator", inp={"InRot": "@rot.ReturnValue"})
    g.set("sy", "FreeYaw", inp={"FreeYaw": "@br.Yaw"}); g.set("sp", "FreePitch", inp={"FreePitch": "@br.Pitch"})
    g.call("rot2", K_MATH, "MakeRotator", inp={"Roll": "0.0", "Pitch": "@br.Pitch", "Yaw": "@br.Yaw"})
    g.call("tf", K_MATH, "MakeTransform", inp={"Location": "@loc.ReturnValue", "Rotation": "@rot2.ReturnValue", "Scale": "(X=1,Y=1,Z=1)"})
    g.n("spawn", "spawn", cls=E_CAMA, inp={"SpawnTransform": "@tf.ReturnValue"}); g.set("sfc", "FreeCam", inp={"FreeCam": "@spawn.ReturnValue"})
    g.get("gcc", "CameraComponent", cls=E_CAMA); g.link("spawn.ReturnValue", "gcc.self")
    g.call("sfov", E_CAMC, "SetFieldOfView", inp={"self": "@gcc.CameraComponent", "InFieldOfView": "@fov.ReturnValue"})
    g.call("sar", E_CAMC, "SetConstraintAspectRatio", inp={"self": "@gcc.CameraComponent", "bInConstrainAspectRatio": "false"})
    g.get("gpc2", "PC"); g.call("svt", E_PC, "SetViewTargetWithBlend", inp={"self": "@gpc2.PC", "NewViewTarget": "@spawn.ReturnValue", "BlendTime": "0.0", "BlendFunc": "VTBlend_Linear", "BlendExp": "0.0", "bLockOutgoing": "false"})
    g.n("svs", "call_self", function="Set View Shift")
    g.get("gp", "Panel"); g.call("pcm", W_PANEL, "Set Cam Mode", inp={"self": "@gp.Panel", "on": "true"})
    # input helper on top of the input stack (spawned after the manager -> higher priority), control rotation saved (the game turns Jodi's camera with the mouse too)
    g.n("spi", "spawn", cls=P_CAMIN, inp={"SpawnTransform": "@tf.ReturnValue"}); g.set("sci", "CamInput", inp={"CamInput": "@spi.ReturnValue"})
    g.self_("me"); g.n("smi", "set", var="Manager", cls=P_CAMIN, inp={"self": "@spi.ReturnValue", "Manager": "@me.self"})
    g.get("gpc5", "PC"); g.call("eni", E_ACTOR, "EnableInput", inp={"self": "@spi.ReturnValue", "PlayerController": "@gpc5.PC"})
    g.get("gpc6", "PC"); g.call("gcr", E_CTRL, "GetControlRotation", inp={"self": "@gpc6.PC"}); g.set("scr", "FreeCtrlRot", inp={"FreeCtrlRot": "@gcr.ReturnValue"})
    g.get("gpc3", "PC"); g.call("cur", P_PC, "ShowMouseCursor", inp={"self": "@gpc3.PC", "show": "false"})
    g.get("gpc4", "PC"); g.call("im", K_WBL, "SetInputMode_GameOnly", inp={"PlayerController": "@gpc4.PC"})
    g.chain("entry", "b0", "cmn", "ccl", "scm", "sy", "sp", "spawn", "sfc", "sfov", "sar", "svt", "svs", "pcm", "spi", "sci", "smi", "eni", "scr", "cur", "im")
    return fn("Start Free Cam", graph=g)


def f_stop_free_cam():
    """Back to Jodi's camera (blend 0), actor gone, hook re-initialises with the option values, panel visible and focused."""
    g = G(); g.get("gcm", "CamMode"); g.call("is1", K_MATH, "EqualEqual_IntInt", inp={"A": "@gcm.CamMode", "B": "1"}); g.branch("b1", "@is1.ReturnValue")
    g.get("gpc", "PC"); g.get("gpl", "Player"); g.call("svt", E_PC, "SetViewTargetWithBlend", inp={"self": "@gpc.PC", "NewViewTarget": "@gpl.Player", "BlendTime": "0.0", "BlendFunc": "VTBlend_Linear", "BlendExp": "0.0", "bLockOutgoing": "false"})
    g.get("gfc", "FreeCam"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gfc.FreeCam"}); g.branch("bv", "@iv.ReturnValue")
    g.get("gfc2", "FreeCam"); g.call("ds", E_ACTOR, "K2_DestroyActor", inp={"self": "@gfc2.FreeCam"})
    g.set("sfc", "FreeCam", inp={"FreeCam": "None"}); g.set("scm", "CamMode", inp={"CamMode": "0"})
    g.get("gci", "CamInput"); g.call("ivi", K_SYS, "IsValid", inp={"Object": "@gci.CamInput"}); g.branch("bvi", "@ivi.ReturnValue")
    g.get("gci2", "CamInput"); g.call("dsi", E_ACTOR, "K2_DestroyActor", inp={"self": "@gci2.CamInput"}); g.set("sci", "CamInput", inp={"CamInput": "None"})
    g.get("gpc9", "PC"); g.get("gcr", "FreeCtrlRot"); g.call("scr", E_CTRL, "SetControlRotation", inp={"self": "@gpc9.PC", "NewRotation": "@gcr.FreeCtrlRot"})
    g.get("go", "PanelOpen"); g.branch("bo", "@go.PanelOpen")
    g.get("gp", "Panel"); g.call("pcm", W_PANEL, "Set Cam Mode", inp={"self": "@gp.Panel", "on": "false"})
    g.n("apo", "call_self", function="Apply Options")   # Set Left Free (buttons back) + Set View Shift (option value)
    g.get("gpc2", "PC"); g.call("cur", P_PC, "ShowMouseCursor", inp={"self": "@gpc2.PC", "show": "true"})
    g.get("gpc3", "PC"); g.get("gp2", "Panel"); g.call("im", K_WBL, "SetInputMode_GameAndUIEx", inp={"PlayerController": "@gpc3.PC", "InWidgetToFocus": "@gp2.Panel", "InMouseLockMode": "DoNotLock", "bHideCursorDuringCapture": "false"})
    g.get("gp3", "Panel"); g.call("kf", E_WIDGET, "SetKeyboardFocus", inp={"self": "@gp3.Panel"})
    g.n("svs", "call_self", function="Set View Shift")   # panel closed (B): CamMode 0 -> the hook gets ViewShift (0 after Close Panel)
    g.chain("entry", "b1", "svt", "bv", "ds", "sfc"); g.chain("bv:else", "sfc"); g.chain("sfc", "scm", "bvi", "dsi", "sci"); g.chain("bvi:else", "sci")
    g.chain("sci", "scr", "bo", "pcm", "apo", "cur", "im", "kf"); g.chain("bo:else", "svs")
    return fn("Stop Free Cam", graph=g)


def f_free_cam_look():
    """Mouse delta -> yaw / pitch (pitch clamped, mouse up = look up), rotation onto the camera actor."""
    g = G(); g.call("bd", K_MATH, "BreakVector2D", inp={"InVec": "@entry.delta"})
    g.get("gy", "FreeYaw"); g.call("dy", K_MATH, "Multiply_FloatFloat", inp={"A": "@bd.X", "B": str(FREE_LOOK)}); g.call("ny", K_MATH, "Add_FloatFloat", inp={"A": "@gy.FreeYaw", "B": "@dy.ReturnValue"}); g.set("sy", "FreeYaw", inp={"FreeYaw": "@ny.ReturnValue"})
    g.get("gp", "FreePitch"); g.call("dp", K_MATH, "Multiply_FloatFloat", inp={"A": "@bd.Y", "B": str(FREE_LOOK)}); g.call("np", K_MATH, "Subtract_FloatFloat", inp={"A": "@gp.FreePitch", "B": "@dp.ReturnValue"})
    g.call("cp", K_MATH, "FClamp", inp={"Value": "@np.ReturnValue", "Min": str(-FREE_PITCH), "Max": str(FREE_PITCH)}); g.set("sp", "FreePitch", inp={"FreePitch": "@cp.ReturnValue"})
    g.get("gy2", "FreeYaw"); g.get("gp2", "FreePitch"); g.call("rot", K_MATH, "MakeRotator", inp={"Roll": "0.0", "Pitch": "@gp2.FreePitch", "Yaw": "@gy2.FreeYaw"})
    g.get("gfc", "FreeCam"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gfc.FreeCam"}); g.branch("bv", "@iv.ReturnValue")
    g.get("gfc2", "FreeCam"); g.call("sr", E_ACTOR, "K2_SetActorRotation", inp={"self": "@gfc2.FreeCam", "NewRotation": "@rot.ReturnValue", "bTeleportPhysics": "false"})
    g.chain("entry", "sy", "sp", "bv", "sr"); return fn("Free Cam Look", [param("delta", S_VEC2)], graph=g)


def f_free_cam_wheel():
    g = G(); g.call("gt", K_MATH, "Greater_FloatFloat", inp={"A": "@entry.delta", "B": "0.0"})
    g.call("f", K_MATH, "SelectFloat", inp={"A": str(FREE_WHEEL), "B": str(1.0 / FREE_WHEEL), "bPickA": "@gt.ReturnValue"})
    g.get("gs", "FreeSpeed"); g.call("m", K_MATH, "Multiply_FloatFloat", inp={"A": "@gs.FreeSpeed", "B": "@f.ReturnValue"})
    g.call("c", K_MATH, "FClamp", inp={"Value": "@m.ReturnValue", "Min": str(FREE_SPEED_MIN), "Max": str(FREE_SPEED_MAX)}); g.set("ss", "FreeSpeed", inp={"FreeSpeed": "@c.ReturnValue"})
    g.chain("entry", "ss"); return fn("Free Cam Wheel", [param("delta", "float")], graph=g)


def f_free_cam_step():
    """target = loc + dir * v * dt, clamped to the sphere around Jodi; sphere trace loc -> target (Visibility; Jodi's mesh blocks, only the
    camera actor is ignored). Hit: stop FREE_TRACE_GAP before the contact point (the sphere never rests in contact - a trace that starts
    overlapping reports a hit at distance 0 in every direction = stuck), then slide the remainder along the surface with a second trace.
    Initial overlap (already touching): only movement away from the surface (dir . normal > 0) is allowed."""
    g = G(); g.get("gfc", "FreeCam"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gfc.FreeCam"}); g.branch("bv", "@iv.ReturnValue")
    # mouse: raw deltas of the frame (GetInputMouseDelta is pure; MouseY positive = up -> negate for the pitch convention of Free Cam Look)
    g.get("gpcm", "PC"); g.call("md", E_PC, "GetInputMouseDelta", inp={"self": "@gpcm.PC"}); g.call("ndy", K_MATH, "Multiply_FloatFloat", inp={"A": "@md.DeltaY", "B": "-1.0"})
    g.call("mv2", K_MATH, "MakeVector2D", inp={"X": "@md.DeltaX", "Y": "@ndy.ReturnValue"}); g.n("lk", "call_self", function="Free Cam Look", inp={"delta": "@mv2.ReturnValue"})
    # wheel: speed
    g.get("gpcw", "PC"); g.call("wu", E_PC, "WasInputKeyJustPressed", inp={"self": "@gpcw.PC", "Key": "MouseScrollUp"}); g.branch("bwu", "@wu.ReturnValue"); g.n("fw1", "call_self", function="Free Cam Wheel", inp={"delta": "1.0"})
    g.get("gpcw2", "PC"); g.call("wd", E_PC, "WasInputKeyJustPressed", inp={"self": "@gpcw2.PC", "Key": "MouseScrollDown"}); g.branch("bwd", "@wd.ReturnValue"); g.n("fw2", "call_self", function="Free Cam Wheel", inp={"delta": "-1.0"})
    # keys -> direction
    g.n("keys", "call_self", function="Free Cam Keys"); g.get("gy", "FreeYaw"); g.get("gpt", "FreePitch"); g.n("dir", "call_self", function="Free Cam Dir", inp={"keys": "@keys.keys", "yaw": "@gy.FreeYaw", "pitch": "@gpt.FreePitch"})
    g.call("dl", K_MATH, "VSize", inp={"A": "@dir.dir"}); g.call("mv", K_MATH, "Greater_FloatFloat", inp={"A": "@dl.ReturnValue", "B": "0.5"}); g.branch("bm", "@mv.ReturnValue")
    g.call("sha", K_MATH, "And_IntInt", inp={"A": "@keys.keys", "B": "64"}); g.call("shb", K_MATH, "NotEqual_IntInt", inp={"A": "@sha.ReturnValue", "B": "0"})
    g.call("fast", K_MATH, "SelectFloat", inp={"A": str(FREE_FAST), "B": "1.0", "bPickA": "@shb.ReturnValue"})
    g.get("gs", "FreeSpeed"); g.call("v", K_MATH, "Multiply_FloatFloat", inp={"A": "@gs.FreeSpeed", "B": "@fast.ReturnValue"}); g.call("vd", K_MATH, "Multiply_FloatFloat", inp={"A": "@v.ReturnValue", "B": "@entry.dt"})
    g.call("off", K_MATH, "Multiply_VectorFloat", inp={"A": "@dir.dir", "B": "@vd.ReturnValue"})
    g.get("gfc2", "FreeCam"); g.call("loc", E_ACTOR, "K2_GetActorLocation", inp={"self": "@gfc2.FreeCam"}); g.call("tgt0", K_MATH, "Add_VectorVector", inp={"A": "@loc.ReturnValue", "B": "@off.ReturnValue"})
    g.get("gpl", "Player"); g.call("ploc", E_ACTOR, "K2_GetActorLocation", inp={"self": "@gpl.Player"})
    g.n("cl", "call_self", function="Free Cam Clamp", inp={"center": "@ploc.ReturnValue", "target": "@tgt0.ReturnValue"})
    g.get("gfc3", "FreeCam"); g.n("ign", "make_array", count=1, type="object:" + E_ACTOR, inp={"[0]": "@gfc3.FreeCam"})
    trace = lambda id, start, end: g.call(id, K_SYS, "SphereTraceSingle", inp={"Start": start, "End": end, "Radius": str(FREE_TRACE_R), "TraceChannel": "TraceTypeQuery1", "bTraceComplex": "false", "ActorsToIgnore": "@ign.Array", "DrawDebugType": "None", "bIgnoreSelf": "true", "TraceColor": "(R=1,G=0,B=0,A=1)", "TraceHitColor": "(R=0,G=1,B=0,A=1)", "DrawTime": "5.0"})
    trace("tr", "@loc.ReturnValue", "@cl.v"); g.branch("bh", "@tr.ReturnValue")
    g.call("bh1", K_GS, "BreakHitResult", inp={"Hit": "@tr.OutHit"})
    # free path: move to the clamped target
    g.get("gfc4", "FreeCam"); g.call("sl", E_ACTOR, "K2_SetActorLocation", inp={"self": "@gfc4.FreeCam", "NewLocation": "@cl.v", "bSweep": "false", "bTeleport": "true"})
    # hit: initial overlap -> allowed only away from the surface (dir . normal > 0), then the full move
    g.call("dn", K_MATH, "Dot_VectorVector", inp={"A": "@dir.dir", "B": "@bh1.ImpactNormal"}); g.call("away", K_MATH, "Greater_FloatFloat", inp={"A": "@dn.ReturnValue", "B": "0.0"})
    g.branch("bio", "@bh1.bInitialOverlap"); g.branch("baw", "@away.ReturnValue")
    g.get("gfc5", "FreeCam"); g.call("sl2", E_ACTOR, "K2_SetActorLocation", inp={"self": "@gfc5.FreeCam", "NewLocation": "@cl.v", "bSweep": "false", "bTeleport": "true"})
    # hit on the way: contact point minus a gap along the move, then slide the remainder along the surface (second trace)
    g.call("gap", K_MATH, "Multiply_VectorFloat", inp={"A": "@dir.dir", "B": str(FREE_TRACE_GAP)}); g.call("stop", K_MATH, "Subtract_VectorVector", inp={"A": "@bh1.Location", "B": "@gap.ReturnValue"})
    g.call("rem", K_MATH, "Subtract_VectorVector", inp={"A": "@cl.v", "B": "@stop.ReturnValue"})
    g.call("rn", K_MATH, "Dot_VectorVector", inp={"A": "@rem.ReturnValue", "B": "@bh1.ImpactNormal"}); g.call("rnv", K_MATH, "Multiply_VectorFloat", inp={"A": "@bh1.ImpactNormal", "B": "@rn.ReturnValue"})
    g.call("slide", K_MATH, "Subtract_VectorVector", inp={"A": "@rem.ReturnValue", "B": "@rnv.ReturnValue"}); g.call("tgt2", K_MATH, "Add_VectorVector", inp={"A": "@stop.ReturnValue", "B": "@slide.ReturnValue"})
    trace("tr2", "@stop.ReturnValue", "@tgt2.ReturnValue")
    g.call("sel2", K_MATH, "SelectVector", inp={"A": "@stop.ReturnValue", "B": "@tgt2.ReturnValue", "bPickA": "@tr2.ReturnValue"})
    g.get("gfc6", "FreeCam"); g.call("sl3", E_ACTOR, "K2_SetActorLocation", inp={"self": "@gfc6.FreeCam", "NewLocation": "@sel2.ReturnValue", "bSweep": "false", "bTeleport": "true"})
    g.chain("entry", "bv", "lk", "bwu", "fw1", "bwd", "fw2", "bm", "tr", "bh", "bio", "baw", "sl2"); g.chain("bwu:else", "bwd"); g.chain("bwd:else", "bm")
    g.chain("bh:else", "sl"); g.chain("bio:else", "tr2", "sl3")
    return fn("Free Cam Step", [param("dt", "float")], graph=g)


def f_start_photo_mode():
    """Game photo mode (TKA_GameState.Enter Photo Mode): panel collapsed + unfocused so Esc reaches the controller; ViewShift 0."""
    g = G(); g.get("gcm", "CamMode"); g.call("is0", K_MATH, "EqualEqual_IntInt", inp={"A": "@gcm.CamMode", "B": "0"}); g.branch("b0", "@is0.ReturnValue")
    g.call("gs", K_GS, "GetGameState"); g.cast("cgs", P_GS2, "@gs.ReturnValue", pure=False, miss="ignore")
    g.n("cmn", "call_self", function="Close Menu"); g.n("ccl", "call_self", function="Close Color")
    g.set("scm", "CamMode", inp={"CamMode": "2"}); g.n("svs", "call_self", function="Set View Shift")
    g.get("gp", "Panel"); g.call("pv", E_WIDGET, "SetVisibility", inp={"self": "@gp.Panel", "InVisibility": "Collapsed"})
    g.get("gpc", "PC"); g.call("im", K_WBL, "SetInputMode_GameAndUIEx", inp={"PlayerController": "@gpc.PC", "InWidgetToFocus": "None", "InMouseLockMode": "DoNotLock", "bHideCursorDuringCapture": "false"})
    g.call("ep", P_GS2, "Enter Photo Mode", inp={"self": "@cgs.AsTKA Game State"})
    g.chain("entry", "b0", "cgs", "cmn", "ccl", "scm", "svs", "pv", "im", "ep")
    return fn("Start Photo Mode", graph=g)


def f_end_photo_mode():
    """Photo mode is over (Esc in the game, or Close Panel): panel back if still open, Jodi locked again, hook gets the option values."""
    g = G(); g.set("scm", "CamMode", inp={"CamMode": "0"})
    # visibility back first, even when the panel was closed meanwhile (B during the photo mode): Open Panel reuses the same widget
    g.get("gp", "Panel"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gp.Panel"}); g.branch("bv", "@iv.ReturnValue")
    g.get("gp0", "Panel"); g.call("pv", E_WIDGET, "SetVisibility", inp={"self": "@gp0.Panel", "InVisibility": "Visible"})
    g.get("go", "PanelOpen"); g.branch("bo", "@go.PanelOpen")
    g.get("gpc", "PC"); g.call("cur", P_PC, "ShowMouseCursor", inp={"self": "@gpc.PC", "show": "true"})
    g.get("gpc2", "PC"); g.get("gp2", "Panel"); g.call("im", K_WBL, "SetInputMode_GameAndUIEx", inp={"PlayerController": "@gpc2.PC", "InWidgetToFocus": "@gp2.Panel", "InMouseLockMode": "DoNotLock", "bHideCursorDuringCapture": "false"})
    # movement lock as in Open Panel (Exit Photo Mode re-enabled Jodi's input)
    g.get("gls", "LockStrategy"); g.call("eq0", K_MATH, "EqualEqual_IntInt", inp={"A": "@gls.LockStrategy", "B": "0"}); g.branch("bl", "@eq0.ReturnValue")
    g.get("gpc3", "PC"); g.call("epc", P_PC, "Enable Player Control", inp={"self": "@gpc3.PC", "Base": "false", "Playing": "false"})
    g.get("gpl", "Player"); g.get("gpc4", "PC"); g.call("di", E_ACTOR, "DisableInput", inp={"self": "@gpl.Player", "PlayerController": "@gpc4.PC"})
    g.get("gp3", "Panel"); g.call("kf", E_WIDGET, "SetKeyboardFocus", inp={"self": "@gp3.Panel"})
    g.n("apo", "call_self", function="Apply Options"); g.n("uf", "call_self", function="Update Focus")   # Apply Options: Set View Shift with the option value
    g.n("svs", "call_self", function="Set View Shift")
    g.chain("entry", "scm", "bv", "pv", "bo", "cur", "im", "bl", "epc", "kf"); g.chain("bv:else", "bo"); g.chain("bl:else", "di", "kf"); g.chain("kf", "apo", "uf"); g.chain("bo:else", "svs")
    return fn("End Photo Mode", graph=g)


def f_cam_tick():
    """Per frame: free cam step, or photo mode end detection (Is In Photo Mode false -> End Photo Mode)."""
    g = G(); g.get("gcm", "CamMode"); g.call("is1", K_MATH, "EqualEqual_IntInt", inp={"A": "@gcm.CamMode", "B": "1"}); g.branch("b1", "@is1.ReturnValue")
    g.n("st", "call_self", function="Free Cam Step", inp={"dt": "@entry.dt"})
    g.get("gcm2", "CamMode"); g.call("is2", K_MATH, "EqualEqual_IntInt", inp={"A": "@gcm2.CamMode", "B": "2"}); g.branch("b2", "@is2.ReturnValue")
    g.call("gs", K_GS, "GetGameState"); g.cast("cgs", P_GS2, "@gs.ReturnValue", pure=False, miss="ignore")
    g.call("ipm", P_GS2, "Is In Photo Mode", inp={"self": "@cgs.AsTKA Game State"}); g.branch("bp", "@ipm.yes")
    g.n("ep", "call_self", function="End Photo Mode")
    g.chain("entry", "b1", "st"); g.chain("b1:else", "b2", "cgs", "ipm", "bp"); g.chain("bp:else", "ep")
    return fn("Cam Tick", [param("dt", "float")], graph=g)

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
    g.get("gmg", "MergeGroups"); g.call("mne", K_MATH, "NotEqual_BoolBool", inp={"A": "@gv.merge", "B": "@gmg.MergeGroups"}); g.branch("bmg", "@mne.ReturnValue")
    g.set("smg", "MergeGroups", inp={"MergeGroups": "@gv.merge"}); g.n("bga", "call_self", function="Build Group Aliases"); g.n("rst", "call_self", function="Rebuild SubTabs"); g.n("rli", "call_self", function="Rebuild List"); g.n("svm", "call_self", function="Save Settings")
    g.get("gmm", "MergeMods"); g.call("mmne", K_MATH, "NotEqual_BoolBool", inp={"A": "@gv.mergemods", "B": "@gmm.MergeMods"}); g.branch("bmm", "@mmne.ReturnValue")
    g.set("smm", "MergeMods", inp={"MergeMods": "@gv.mergemods"}); g.n("bgam", "call_self", function="Build Group Aliases"); g.set("sgm", "LookGroup", inp={"LookGroup": "None"})
    g.n("rlch", "call_self", function="Rebuild Look Chips"); g.n("rlca", "call_self", function="Rebuild Look Cats"); g.n("rlk", "call_self", function="Rebuild Look"); g.n("svmm", "call_self", function="Save Settings")
    # tooltip options: pages rebuild their tiles when opened (Select Page), so only store + save
    g.get("gtp", "TipNoPrefix"); g.call("tpne", K_MATH, "NotEqual_BoolBool", inp={"A": "@gv.tipnoprefix", "B": "@gtp.TipNoPrefix"}); g.branch("btp", "@tpne.ReturnValue")
    g.set("stp", "TipNoPrefix", inp={"TipNoPrefix": "@gv.tipnoprefix"}); g.n("svtp", "call_self", function="Save Settings")
    g.get("gtn", "TipNoIds"); g.call("tnne", K_MATH, "NotEqual_BoolBool", inp={"A": "@gv.tipnoids", "B": "@gtn.TipNoIds"}); g.branch("btn", "@tnne.ReturnValue")
    g.set("stn", "TipNoIds", inp={"TipNoIds": "@gv.tipnoids"}); g.n("svtn", "call_self", function="Save Settings")
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
    g.chain("entry", "gv", "sun", "bpn", "spn", "upf", "bnn"); g.chain("bpn:else", "bnn"); g.chain("bnn", "san", "apn", "svn", "bmg"); g.chain("bnn:else", "bmg")
    g.chain("bmg", "smg", "bga", "rst", "rli", "svm", "bmm"); g.chain("bmg:else", "bmm"); g.chain("bmm", "smm", "bgam", "sgm", "rlch", "rlca", "rlk", "svmm", "btp"); g.chain("bmm:else", "btp")
    g.chain("btp", "stp", "svtp", "btn"); g.chain("btp:else", "btn"); g.chain("btn", "stn", "svtn", "bsame"); g.chain("btn:else", "bsame")
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
    g.get("gcb0", "CurrentBody"); g.n("fac", "call_self", function="Body Scale Factors", inp={"name": "@gcb0.CurrentBody"})
    g.make("mk", S_SNAP, Worn="@gw.Worn", Makeup="@gmd.Makeup Data", Skin="@gsn.Skin Name", Hair="@hn.name", Colors="@gtc3.TmpColors", HairColor="@hc.color",
           Boobs="@gbs.Boobs Size", Waist="@gwa.Waist", Hip="@ghp.Hip", Body="@gcb.CurrentBody", Scales="@fac.factors")
    g.set("st", "TmpSnap2", inp={"TmpSnap2": "@mk.S_Snapshot"}); g.get("gt", "TmpSnap2"); g.link("gt.TmpSnap2", "return.snap")
    g.chain("entry", "rs", "md", "mclr", "fc"); g.chain("fc", "gc", "bf", "madd"); g.chain("fc:Completed", "fac", "st", "return")
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
    """Apply a snapshot, staggered: the clothes diff is taken off now, every piece to wear goes into WearQueue (one piece per tick -
    creating several cloth-simulated garments in one frame crashes NvCloth in the game, with or without AltUI) and Finish Apply
    Snapshot (colours, hairstyle, makeup, sliders, body, popup) runs when the queue is empty. A new call replaces a running queue."""
    g = G(); g.brk("bs", S_SNAP, "@entry.snap")
    # a snapshot still being put on: queue this one behind it (Finish Apply Snapshot picks it up)
    g.get("gsp0", "SnapPending"); g.branch("bpend", "@gsp0.SnapPending")
    g.set("sns", "NextSnap", inp={"NextSnap": "@entry.snap"}); g.set("snp", "NextPending", inp={"NextPending": "true"})
    g.set("sps", "PendingSnap", inp={"PendingSnap": "@entry.snap"}); g.set("spp", "SnapPending", inp={"SnapPending": "true"})
    g.get("gpm", "PendingMissing"); g.call("pmc", K_ARR, "Array_Clear", inp={"TargetArray": "@gpm.PendingMissing"})
    # clothes: difference to the current state
    g.n("rs", "call_self", function="Refresh State"); g.get("gw", "Worn"); g.set("sn", "TmpNames", inp={"TmpNames": "@gw.Worn"}); g.get("gn", "TmpNames"); g.foreach("f1", "@gn.TmpNames")
    g.call("c1", K_ARR, "Array_Contains", inp={"TargetArray": "@bs.Worn", "ItemToFind": "@f1.Array Element"}); g.branch("b1", "@c1.ReturnValue")
    g.get("gpl", "Player"); g.call("to", P_CPB, "Take off this clothes", inp={"self": "@gpl.Player", "clothes name": "@f1.Array Element"})
    # queue: underwear (slots Bra / Briefs) first and right away, everything else after the wait
    g.get("gu0", "TmpNames3"); g.call("cu", K_ARR, "Array_Clear", inp={"TargetArray": "@gu0.TmpNames3"}); g.get("go0", "TmpNames4"); g.call("co", K_ARR, "Array_Clear", inp={"TargetArray": "@go0.TmpNames4"})
    g.foreach("f2", "@bs.Worn"); g.n("fi", "call_self", function="Find Item", inp={"name": "@f2.Array Element"}); g.brk("ib", S_ITEM, "@fi.item")
    g.call("isb", K_MATH, "EqualEqual_NameName", inp={"A": "@ib.Slot", "B": "Bra"}); g.call("isp", K_MATH, "EqualEqual_NameName", inp={"A": "@ib.Slot", "B": "Briefs"})
    g.call("isu", K_MATH, "BooleanOR", inp={"A": "@isb.ReturnValue", "B": "@isp.ReturnValue"}); g.branch("bu", "@isu.ReturnValue")
    g.get("gu1", "TmpNames3"); g.call("au", K_ARR, "Array_Add", inp={"TargetArray": "@gu1.TmpNames3", "NewItem": "@f2.Array Element"})
    g.get("go1", "TmpNames4"); g.call("ao", K_ARR, "Array_Add", inp={"TargetArray": "@go1.TmpNames4", "NewItem": "@f2.Array Element"})
    g.get("gu2", "TmpNames3"); g.set("sq", "WearQueue", inp={"WearQueue": "@gu2.TmpNames3"})
    g.get("gq", "WearQueue"); g.get("go2", "TmpNames4"); g.call("app", K_ARR, "Array_Append", inp={"TargetArray": "@gq.WearQueue", "SourceArray": "@go2.TmpNames4"})
    g.get("gu3", "TmpNames3"); g.foreach("f3", "@gu3.TmpNames3"); g.set("sw0", "WearWait", inp={"WearWait": "0"}); g.n("ws", "call_self", function="Wear Queue Step")
    g.set("sw", "WearWait", inp={"WearWait": str(WEAR_WAIT_FIRST)})   # ticks before the next piece goes on (the pieces just taken off get destroyed first)
    g.chain("entry", "bpend", "sns", "snp"); g.chain("bpend:else", "sps", "spp", "pmc", "rs", "sn", "f1"); g.chain("f1", "b1"); g.chain("b1:else", "to")
    g.chain("f1:Completed", "cu", "co", "f2"); g.chain("f2", "fi", "bu", "au"); g.chain("bu:else", "ao"); g.chain("f2:Completed", "sq", "app", "f3"); g.chain("f3", "sw0", "ws"); g.chain("f3:Completed", "sw")
    return fn("Apply Snapshot", [param("snap", "struct:" + S_SNAP)], graph=g)


def f_wear_queue_step():
    """One piece of WearQueue: wear it (only if the player has it - wardrobe or backpack - and it is not worn), apply the snapshot's
    colour or restore the factory colour; unknown / missing pieces are collected for the popup. Empty queue + pending snapshot -> finish."""
    g = G(); g.brk("bs", S_SNAP, "@gps.PendingSnap"); g.get("gps", "PendingSnap")
    g.get("gq", "WearQueue"); g.call("ln", K_ARR, "Array_Length", inp={"TargetArray": "@gq.WearQueue"}); g.call("gt", K_MATH, "Greater_IntInt", inp={"A": "@ln.ReturnValue", "B": "0"}); g.branch("bq", "@gt.ReturnValue")
    # waiting ticks between pieces
    g.get("gww", "WearWait"); g.call("wgt", K_MATH, "Greater_IntInt", inp={"A": "@gww.WearWait", "B": "0"}); g.branch("bw", "@wgt.ReturnValue")
    g.get("gww2", "WearWait"); g.call("wdec", K_MATH, "Subtract_IntInt", inp={"A": "@gww2.WearWait", "B": "1"}); g.set("sww", "WearWait", inp={"WearWait": "@wdec.ReturnValue"})
    g.set("sww2", "WearWait", inp={"WearWait": str(WEAR_WAIT_NEXT)})
    g.get("gq1", "WearQueue"); g.call("get", K_ARR, "Array_Get", inp={"TargetArray": "@gq1.WearQueue", "Index": "0"}); g.set("sn", "TmpName2", inp={"TmpName2": "@get.Item"})
    g.get("gq2", "WearQueue"); g.call("rm", K_ARR, "Array_Remove", inp={"TargetArray": "@gq2.WearQueue", "IndexToRemove": "0"})
    g.get("gn", "TmpName2"); g.n("fi", "call_self", function="Find Item", inp={"name": "@gn.TmpName2"}); g.branch("bfi", "@fi.found")
    g.n("has", "call_self", function="Can Wear", inp={"name": "@gn.TmpName2"}); g.branch("bhas", "@has.yes")   # owned / backpack / option "not owned items" != locked
    g.get("gpl2", "Player"); g.call("iw", P_CPB, "is clothes wearing", inp={"self": "@gpl2.Player", "clothes name": "@gn.TmpName2"}); g.branch("b2", "@iw.yes")
    g.get("gpl3", "Player"); g.call("we", P_CPB, "Wear The Clothes", inp={"self": "@gpl3.Player", "name": "@gn.TmpName2", "check covering": "true", "update mask": "true", "ignore compatible": "false"}); g.branch("bwe", "@we.successed")
    # catalog piece: AltUI's conflict check (freed pairs stay on), then ignore compatible = true (see Wear in gen_manager.py)
    g.get("gn5", "TmpName2"); g.n("isl", "call_self", function="Item Slot", inp={"name": "@gn5.TmpName2"}); g.call("known", K_MATH, "NotEqual_NameName", inp={"A": "@isl.slot", "B": "None"}); g.branch("bkn", "@known.ReturnValue")
    g.n("tc_cs", "call_self", function="Conflicting Worn Slots", inp={"slot": "@isl.slot"}); g.foreach("tc_fo", "@tc_cs.slots")
    g.get("tc_gp", "Player"); g.call("tc_to", P_CPB, "take off clothes", inp={"self": "@tc_gp.Player", "type": "@tc_fo.Array Element", "update mask": "false"})
    g.get("gplw2", "Player"); g.get("gn6", "TmpName2"); g.call("we2", P_CPB, "Wear The Clothes", inp={"self": "@gplw2.Player", "name": "@gn6.TmpName2", "check covering": "true", "update mask": "true", "ignore compatible": "true"}); g.branch("bwe2", "@we2.successed")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@gn.TmpName2"}); g.get("gpm", "PendingMissing"); g.call("sadd", K_ARR, "Array_Add", inp={"TargetArray": "@gpm.PendingMissing", "NewItem": "@n2s.ReturnValue"})
    # colour: the snapshot's, otherwise the factory colour (undo of a recolour, redo of a reset)
    g.n("iw3", "call_self", function="Is Worn", inp={"name": "@gn.TmpName2"}); g.branch("b3", "@iw3.yes")
    g.call("cf", K_MAP, "Map_Find", inp={"TargetMap": "@bs.Colors", "Key": "@gn.TmpName2"}); g.branch("bcf", "@cf.ReturnValue")
    g.get("gpl4", "Player"); g.call("fcc", P_CPB, "Find Clothes Component With Name", inp={"self": "@gpl4.Player", "name": "@gn.TmpName2"})
    g.call("cv", K_SYS, "IsValid", inp={"Object": "@fcc.clothes comp"}); g.branch("bcv", "@cv.ReturnValue")
    g.call("chg", P_CC, "Change Color", inp={"self": "@fcc.clothes comp", "Color": "@cf.Value"})
    g.get("gpl5", "Player"); g.call("svc", P_CPB, "Save Clothes Color", inp={"self": "@gpl5.Player", "clothes name": "@gn.TmpName2", "color": "@cf.Value"})
    g.get("gplR", "Player"); g.call("rsc", P_CPB, "Restore Clothes Color", inp={"self": "@gplR.Player", "clothes": "@gn.TmpName2"})
    # queue empty -> finish the pending snapshot
    g.get("gq3", "WearQueue"); g.call("ln2", K_ARR, "Array_Length", inp={"TargetArray": "@gq3.WearQueue"}); g.call("eq0", K_MATH, "EqualEqual_IntInt", inp={"A": "@ln2.ReturnValue", "B": "0"})
    g.get("gsp", "SnapPending"); g.call("fin", K_MATH, "BooleanAND", inp={"A": "@eq0.ReturnValue", "B": "@gsp.SnapPending"}); g.branch("bfin", "@fin.ReturnValue")
    g.n("fs", "call_self", function="Finish Apply Snapshot")
    g.chain("entry", "bq", "bw", "sww"); g.chain("bw:else", "sn", "rm", "sww2", "fi", "bfi", "has", "bhas", "b2"); g.chain("bfi:else", "sadd"); g.chain("bhas:else", "sadd"); g.chain("sadd", "b3")
    g.chain("b2:else", "bkn", "tc_cs", "tc_fo"); g.chain("tc_fo", "tc_to"); g.chain("tc_fo:Completed", "we2", "bwe2", "b3"); g.chain("bwe2:else", "sadd"); g.chain("bkn:else", "we", "bwe", "b3"); g.chain("bwe:else", "sadd"); g.chain("b2", "b3")
    g.chain("b3", "bcf", "fcc", "bcv", "chg", "svc", "bfin"); g.chain("bcf:else", "rsc", "bfin"); g.chain("bcv:else", "bfin"); g.chain("b3:else", "bfin")
    g.chain("bq:else", "bfin"); g.chain("bfin", "fs")
    return fn("Wear Queue Step", graph=g)


def f_finish_apply_snapshot():
    """Second half of Apply Snapshot once every piece is on: makeup map, skin, sliders, hairstyle (if unlocked) + colour, body variant and its
    bone-scale factors, popup for missing pieces, refresh."""
    g = G(); g.set("spp", "SnapPending", inp={"SnapPending": "false"}); g.get("gps", "PendingSnap"); g.brk("bs", S_SNAP, "@gps.PendingSnap")
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
    owned = hair_owned(g, "hown", "@bs.Hair", "@hbr.MirrorID", mode_min=1); g.branch("bho", owned)
    pop(g, "hpop", tt(g, "hlt", "Msg_HairLocked"))
    g.get("gpl8", "Player"); g.call("ch", P_JODI, "Change Hairstyle", inp={"self": "@gpl8.Player", "Hairstyle": "@bs.Hair"})
    g.get("gpl9", "Player"); g.call("chc", P_JODI, "Change Hairstyle Color", inp={"self": "@gpl9.Player", "color": "@bs.HairColor"})
    gi = game_instance(g, "gi"); g.get("gplA", "Player"); g.call("svh", P_GI, "Save Hair Color Data", inp={"self": gi, "player": "@gplA.Player"})
    g.get("gplB", "Player"); g.call("umt", P_JODI, "Update Makeup Texture", inp={"self": "@gplB.Player"})
    g.get("gplC", "Player"); g.call("ues", P_JODI, "Update Eyes Style", inp={"self": "@gplC.Player"})
    g.get("gplD", "Player"); g.call("rcp", P_CPB, "Reset Clothes Physics", inp={"self": "@gplD.Player"})
    g.n("sa", "call_self", function="Save Worn")
    g.set("sd", "MakeupDirty", inp={"MakeupDirty": "true"})
    # body variant
    g.get("gcb", "CurrentBody"); g.call("eqb", K_MATH, "NotEqual_NameName", inp={"A": "@gcb.CurrentBody", "B": "@bs.Body"}); g.branch("bb", "@eqb.ReturnValue")
    g.n("ab", "call_self", function="Apply Body", inp={"name": "@bs.Body"}); g.get("gcb2", "CurrentBody"); g.set("sbv", "BodyVariant", inp={"BodyVariant": "@gcb2.CurrentBody"}); g.n("svs", "call_self", function="Save Settings")
    # bone-scale factors of the snapshot (N entries, body set) -> saved for that body and applied
    g.call("sl", K_ARR, "Array_Length", inp={"TargetArray": "@bs.Scales"}); g.call("s6", K_MATH, "EqualEqual_IntInt", inp={"A": "@sl.ReturnValue", "B": str(bg.N_SLIDERS)})
    g.call("bn2", K_MATH, "NotEqual_NameName", inp={"A": "@bs.Body", "B": "None"}); g.call("sok", K_MATH, "BooleanAND", inp={"A": "@s6.ReturnValue", "B": "@bn2.ReturnValue"}); g.branch("bsc", "@sok.ReturnValue")
    g.n("ssf", "call_self", function="Set Body Scale Factors", inp={"name": "@bs.Body", "factors": "@bs.Scales"})
    # missing pieces -> popup
    g.get("gts2", "PendingMissing"); g.call("slen", K_ARR, "Array_Length", inp={"TargetArray": "@gts2.PendingMissing"}); g.call("sgt", K_MATH, "Greater_IntInt", inp={"A": "@slen.ReturnValue", "B": "0"}); g.branch("bms", "@sgt.ReturnValue")
    g.get("gts3", "PendingMissing"); g.call("join", K_STR, "JoinStringArray", inp={"SourceArray": "@gts3.PendingMissing", "Separator": ", "})
    g.call("mc", K_STR, "Concat_StrStr", inp={"A": ts(g, "mlm", "Msg_LookMissing"), "B": "@join.ReturnValue"}); pop(g, "mpop", text_from_str(g, "mpt", "@mc.ReturnValue"))
    g.n("rs2", "call_self", function="Refresh State"); g.get("gpg", "Page"); g.n("sp", "call_self", function="Select Page", inp={"name": "@gpg.Page"})
    # a snapshot queued while this one was being put on -> next
    g.get("gnp", "NextPending"); g.branch("bnp", "@gnp.NextPending"); g.set("snp0", "NextPending", inp={"NextPending": "false"})
    g.get("gns", "NextSnap"); g.n("asn", "call_self", function="Apply Snapshot", inp={"snap": "@gns.NextSnap"})
    g.chain("sp", "bnp", "snp0", "asn")
    g.chain("entry", "spp", "md", "smd", "sbo", "swa", "shi", "cb2", "cw2", "sbc", "bsk", "cs", "bh"); g.chain("bsk:else", "bh")
    g.chain("bh", "hrow", "bho", "ch", "chc"); g.chain("bho:else", "hpop", "chc"); g.chain("bh:else", "chc"); g.chain("hrow:Row Not Found", "chc")   # hairstyle gone (mod removed) -> keep going
    g.chain("chc", "svh", "umt", "ues", "rcp", "sa", "sd", "bb", "ab", "bsc", "ssf", "sbv", "svs", "bms"); g.chain("bsc:else", "sbv"); g.chain("bb:else", "bsc"); g.chain("bms", "mpop", "rs2"); g.chain("bms:else", "rs2"); g.chain("rs2", "sp")
    return fn("Finish Apply Snapshot", graph=g)


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
    g.n("sa", "call_self", function="Save Worn")
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
    repair (if damaged), put in backpack (owned, not in the bag) or remove (in the bag), to wardrobe (if new), show in tab, rename mod (mod piece)."""
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
    r8 = menu_row(g, 8, "Rename", tt(g, "rnt", "Menu_Rename"))
    # "Show in tab" (clothes page, slot + group of the piece; Go To Item reads ContextSlot) and "Rename mod…" for a mod piece
    g.n("isl", "call_self", function="Item Slot", inp={"name": "@entry.name"}); g.set("scs", "ContextSlot", inp={"ContextSlot": "@isl.slot"})
    g.call("hsl", K_MATH, "NotEqual_NameName", inp={"A": "@isl.slot", "B": "None"}); g.branch("bsl", "@hsl.ReturnValue")
    r9 = menu_row(g, 9, "GoTo", tt(g, "gtt", "Menu_ShowIn"))
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@entry.name"}); g.branch("bmd", "@imd.found")
    r10 = menu_row(g, 10, "RenameMod", tt(g, "rmt", "Menu_RenameMod"))
    g.chain("clr", *r8, *r0, "fi", "bc", *r5, "gcr", "brc", *r6, "dm"); g.chain("bc:else", "dm"); g.chain("brc:else", "dm")
    g.chain("dm", "bd", *r1, "ib"); g.chain("bd:else", "ib")
    g.chain("ib", "bib", *r2, "bw"); g.chain("bib:else", "bpb", *r7, "bw"); g.chain("bpb:else", "bw")
    g.chain("bw", *r3, "scs"); g.chain("bw:else", "scs")
    g.chain("scs", "bsl", *r9, "bmd"); g.chain("bsl:else", "bmd"); g.chain("bmd", *r10, r4[0]); g.chain("bmd:else", r4[0])
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
    ("BagRemove", "Bag Remove", "ContextItem"), ("BagToWardrobe", "Bag To Wardrobe", "ContextItem"), ("BagCleanup", "Bag Cleanup", None), ("BagAllWorn", "Bag All Worn", None),
    ("OutfitWear", "On Outfit Clicked", "ContextOutfit"), ("OutfitRename", "Start Outfit Rename", "ContextOutfit"), ("OutfitDelete", "Delete Outfit", "ContextOutfit"),
    ("LookRename", "Start Look Rename", "ContextLook"), ("LookUpdate", "Update Look", "ContextLook"), ("LookDelete", "Delete Look", "ContextLook"),
    ("PresetApply", "Preset Clicked", "ContextPreset"), ("PresetDelete", "Preset Delete", "ContextPreset"),
    ("OutfitView", "Open Outfit Content", "ContextOutfit"), ("LookView", "Open Look Content", "ContextLook"), ("PresetView", "Open Preset Content", "ContextPreset"),
    ("ContentBack", "Close Content", None), ("GoTo", "Go To Item", "ContextItem"),
    ("OnlyGroup", "Show Only Group", "ContextItem"), ("ModContent", "Open Mod Content Of Item", "ContextItem"),
    ("Rename", "Start Item Rename", "ContextItem"), ("LookFav", "Toggle Look Favorite", "ContextItem"), ("LookHide", "Toggle Look Hidden", "ContextItem"), ("LookOnlyMod", "Look Only Mod", "ContextItem"), ("RenameMod", "Rename Mod Of Item", "ContextItem"), ("RenameGroup", "Rename Group Of Item", "ContextItem"),
    ("HairNatural", "Toggle Hair Swatches", None),
    ("FreeCam", "Start Free Cam", None), ("PhotoMode", "Start Photo Mode", None),
    ("Undo", "Undo", None), ("Redo", "Redo", None)]


def f_on_menu_action():
    g = G()
    g.n("cm", "call_self", function="Close Menu")
    # +/- in the Jodi view: camera distance by one slider step (5 %; + = closer), DIST_MIN..DIST_MAX, save, update the slider
    g.call("isP", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "DistPlus"}); g.call("isM", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "DistMinus"})
    g.call("orD", K_MATH, "BooleanOR", inp={"A": "@isP.ReturnValue", "B": "@isM.ReturnValue"}); g.branch("bdist", "@orD.ReturnValue")
    g.call("step", K_MATH, "SelectFloat", inp={"A": "-0.05", "B": "0.05", "bPickA": "@isP.ReturnValue"}); g.get("gcd", "CamDist")   # + = closer (distance -5 %), - = farther
    g.call("nd", K_MATH, "Add_FloatFloat", inp={"A": "@gcd.CamDist", "B": "@step.ReturnValue"}); g.call("ndc", K_MATH, "FClamp", inp={"Value": "@nd.ReturnValue", "Min": str(DIST_MIN), "Max": str(DIST_MAX)})
    g.set("scd", "CamDist", inp={"CamDist": "@ndc.ReturnValue"}); g.n("apo", "call_self", function="Apply Options"); g.n("svd", "call_self", function="Save Settings")
    g.get("gpgD", "Page"); g.call("isO", K_MATH, "EqualEqual_NameName", inp={"A": "@gpgD.Page", "B": "Options"}); g.branch("bO", "@isO.ReturnValue"); g.n("rbo", "call_self", function="Rebuild Options")
    # slot conflict links: "CfAll:<slot>" / "CfReset:<slot>" (row), ConflictsFreeAll / ConflictsReset (block)
    g.call("cfs", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"})
    g.call("cfa", K_STR, "StartsWith", inp={"SourceString": "@cfs.ReturnValue", "InPrefix": "CfAll:", "SearchCase": "CaseSensitive"}); g.branch("bcfa", "@cfa.ReturnValue")
    g.call("cfa_s", K_STR, "GetSubstring", inp={"SourceString": "@cfs.ReturnValue", "StartIndex": "6", "Length": "1000"}); g.call("cfa_n", K_STR, "Conv_StringToName", inp={"InString": "@cfa_s.ReturnValue"})
    g.n("cfa_f", "call_self", function="Free Slot", inp={"slot": "@cfa_n.ReturnValue", "freed": "true"})
    g.call("cfr", K_STR, "StartsWith", inp={"SourceString": "@cfs.ReturnValue", "InPrefix": "CfReset:", "SearchCase": "CaseSensitive"}); g.branch("bcfr", "@cfr.ReturnValue")
    g.call("cfr_s", K_STR, "GetSubstring", inp={"SourceString": "@cfs.ReturnValue", "StartIndex": "8", "Length": "1000"}); g.call("cfr_n", K_STR, "Conv_StringToName", inp={"InString": "@cfr_s.ReturnValue"})
    g.n("cfr_f", "call_self", function="Free Slot", inp={"slot": "@cfr_n.ReturnValue", "freed": "false"})
    g.n("cff_a", "call_self", function="Free All", inp={"freed": "true"}); g.n("cff_r", "call_self", function="Free All", inp={"freed": "false"})
    g.chain("entry", "cm", "bcfa", "cfa_f"); g.chain("bcfa:else", "bcfr", "cfr_f"); g.chain("bcfr:else", "bdist", "scd", "apo", "svd", "bO", "rbo"); prev = "bdist:else"
    # multi-step actions
    g.get("gpcs", "Panel"); g.call("pcs", W_PANEL, "Clear Search", inp={"self": "@gpcs.Panel"})
    g.call("et", K_TXT, "Conv_StringToText", inp={"InString": ""}); g.n("osc", "call_self", function="On Search Changed", inp={"text": "@et.ReturnValue"})
    g.n("ftr", "call_self", function="Reset Theme"); g.n("ftr2", "call_self", function="Apply Theme"); g.n("ftr3", "call_self", function="Save Settings"); g.n("ftr4", "call_self", function="Rebuild Options")
    g.get("gpms", "Panel"); g.call("pms", W_PANEL, "Clear Manage Search", inp={"self": "@gpms.Panel"}); g.set("smst", "ManageSearchText", inp={"ManageSearchText": ""})
    g.n("mrc", "call_self", function="Rebuild Manage Cats"); g.n("mrr", "call_self", function="Rebuild Manage")
    g.get("gpls", "Panel"); g.call("pls", W_PANEL, "Clear Look Search", inp={"self": "@gpls.Panel"}); g.set("slst", "LookSearchText", inp={"LookSearchText": ""})
    g.n("lrc", "call_self", function="Rebuild Look Cats"); g.n("lrk", "call_self", function="Rebuild Look")
    special = {"ClearSearch": ["pcs", "osc"], "ClearManageSearch": ["pms", "smst", "mrc", "mrr"], "ClearLookSearch": ["pls", "slst", "lrc", "lrk"], "ThemeReset": ["ftr", "ftr2", "ftr3", "ftr4"],
               "ConflictsFreeAll": ["cff_a"], "ConflictsReset": ["cff_r"]}
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
    for i, page in enumerate(["Clothes", "Outfits", "Looks", "Bag", "Hair", "Look", "Body", "Options", "Manage"]):
        tw = create_widget(g, "ct%d" % i, W_TOP); set_manager(g, "sm%d" % i, W_TOP, tw)
        g.get("gpo%d" % i, "Page"); g.call("eq%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@gpo%d.Page" % i, "B": page}); sel = "@eq%d.ReturnValue" % i
        g.call("ti%d" % i, W_TOP, "Init", inp={"self": tw, "page": page, "caption": tt(g, "tt%d" % i, "Tab_" + page), "selected": sel})
        g.get("gp%d" % i, "Panel"); g.call("at%d" % i, W_PANEL, "Add TopTab", inp={"self": "@gp%d.Panel" % i, "widget": tw})
        tail += ["ct%d_cr" % i, "sm%d" % i, "ti%d" % i, "at%d" % i]
    g.chain(*tail); return fn("Rebuild TopTabs", graph=g)


def f_rebuild_catalog_if_dirty():
    """A custom name changed (Manage tab) -> the catalog's display names are stale; rebuild once before the clothes page shows them."""
    g = G(); g.get("gcd", "CatalogDirty"); g.branch("b", "@gcd.CatalogDirty")
    g.n("bc", "call_self", function="Build Catalog"); g.set("s", "CatalogDirty", inp={"CatalogDirty": "false"})
    g.chain("entry", "b", "bc", "s")
    return fn("Rebuild Catalog If Dirty", graph=g)


# ---------------- Manage tab / mod content / hair swatches: entry points the widgets call (filled in below) ----------------
def f_on_manage_search_changed():
    """Panel key-up: the Manage search box text -> ManageSearchText; rebuild the rows when it changed (Manage page only)."""
    g = G(); g.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@entry.text"})
    g.get("gst", "ManageSearchText"); g.call("neq", K_STR, "NotEqual_StrStr", inp={"A": "@t2s.ReturnValue", "B": "@gst.ManageSearchText"}); g.branch("b", "@neq.ReturnValue")
    g.set("s", "ManageSearchText", inp={"ManageSearchText": "@t2s.ReturnValue"})
    g.get("gpg", "Page"); g.call("ism", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Manage"}); g.branch("bm", "@ism.ReturnValue")
    g.n("rc", "call_self", function="Rebuild Manage Cats"); g.n("rm", "call_self", function="Rebuild Manage")
    g.chain("entry", "b", "s", "bm", "rc", "rm")
    return fn("On Manage Search Changed", [param("text", "text")], graph=g)


# ---------------- Manage tab: categories, rows (keys "<kind>:<row>"), row data, rebuild ----------------
MANAGE_CATS = [("Vanilla", "Cat_Vanilla"), ("Mods", "Cat_Mods"), ("Clothes", "Cat_Clothes"), ("Look", "Tab_Look")]   # Vanilla / Mods clickable; Clothes / Look are sections (Look = hairstyles + skins + make-up)
MANAGE_NO_ONLY_MODS = ("Mods", "Vanilla")   # categories without the "only mods" checkbox
MANAGE_SUBS = ("Clothes", "Look")   # categories with sub items (ManageSub: None = All; Clothes: slot; Look: Skin / makeup type)


def f_name_matches():
    """yes = search empty or contained in the row name, the default name or the custom name (case per CaseSensitiveNames)."""
    g = G()
    g.call("em", K_STR, "IsEmpty", inp={"InString": "@entry.search"}); g.get("gcs", "CaseSensitiveNames")
    g.call("rs", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"}); g.n("cn", "call_self", function="Custom Name", inp={"kind": "@entry.kind", "row": "@entry.row"})
    prev = "@em.ReturnValue"
    for i, src in enumerate(["@rs.ReturnValue", "@entry.default", "@cn.name"]):
        g.call("hit%d" % i, K_STR, "Contains", inp={"SearchIn": src, "Substring": "@entry.search", "bUseCase": "@gcs.CaseSensitiveNames", "bSearchFromEnd": "false"})
        g.call("or%d" % i, K_MATH, "BooleanOR", inp={"A": prev, "B": "@hit%d.ReturnValue" % i}); prev = "@or%d.ReturnValue" % i
    g.link(prev[1:], "return.yes")
    return fn("Name Matches", [param("kind", "name"), param("row", "name"), param("default", "string"), param("search", "string")], [param("yes", "bool")], graph=g, pure=True)


def add_key(g, id, kind, row_pin, after):
    """TmpStrings += "<kind>:<row>"; returns the exec ids."""
    g.call(id + "_s", K_STR, "Conv_NameToString", inp={"InName": row_pin}); g.call(id + "_c", K_STR, "Concat_StrStr", inp={"A": kind + ":", "B": "@%s_s.ReturnValue" % id})
    g.get(id + "_g", "TmpStrings"); g.call(id + "_a", K_ARR, "Array_Add", inp={"TargetArray": "@%s_g.TmpStrings" % id, "NewItem": "@%s_c.ReturnValue" % id})
    g.chain(after, id + "_a"); return id + "_a"


def f_manage_rows():
    """Row keys of a Manage category in display order: Mods = mod header + its groups (a header stays when one of its groups matches);
    Vanilla = the groups with a vanilla piece (VanillaGroups, no header; onlyMods has no effect); Clothes = catalog order (ManageSub = slot); Look = hairstyle table (ManageSub None / Hair) + skin table (None / Skin) + makeup + eye tables
    (None / the row's Type). onlyMods drops rows without a mod origin; search via Name Matches."""
    g = G()
    g.get("gts", "TmpStrings"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gts.TmpStrings"})
    g.set("ss", "TmpStr3", inp={"TmpStr3": "@entry.search"})   # case handled in Name Matches (CaseSensitiveNames)
    g.set("som", "TmpFound", inp={"TmpFound": "@entry.onlyMods"})
    cats = []
    for cat in ("Mods", "Vanilla", "Clothes", "Look"):
        g.call("is" + cat, K_MATH, "EqualEqual_NameName", inp={"A": "@entry.cat", "B": cat}); g.branch("b" + cat, "@is%s.ReturnValue" % cat); cats.append("b" + cat)
    g.chain("entry", "clr", "ss", "som", cats[0])
    for a, b in zip(cats, cats[1:]): g.chain(a + ":else", b)
    g.get("gr", "TmpStrings"); g.link("gr.TmpStrings", "return.keys")
    # --- Mods: header + groups
    g.get("gml", "ModList"); g.foreach("fm", "@gml.ModList")
    g.call("ms", K_STR, "Conv_NameToString", inp={"InName": "@fm.Array Element"}); g.call("mp", K_STR, "Concat_StrStr", inp={"A": "@ms.ReturnValue", "B": "|"})
    g.get("gmc", "ModCaption"); g.call("mcf", K_MAP, "Map_Find", inp={"TargetMap": "@gmc.ModCaption", "Key": "@fm.Array Element"}); g.call("mcs", K_TXT, "Conv_TextToString", inp={"InText": "@mcf.Value"})
    g.get("gs1", "TmpStr3"); g.n("mm", "call_self", function="Name Matches", inp={"kind": "mod", "row": "@fm.Array Element", "default": "@mcs.ReturnValue", "search": "@gs1.TmpStr3"})
    g.set("smm", "TmpBool", inp={"TmpBool": "@mm.yes"})
    g.get("gn3", "TmpNames3"); g.call("n3c", K_ARR, "Array_Clear", inp={"TargetArray": "@gn3.TmpNames3"})
    g.get("gpp", "ModGroupPairs"); g.foreach("fp", "@gpp.ModGroupPairs")
    g.call("ps", K_STR, "Conv_NameToString", inp={"InName": "@fp.Array Element"}); g.call("sw", K_STR, "StartsWith", inp={"SourceString": "@ps.ReturnValue", "InPrefix": "@mp.ReturnValue", "SearchCase": "CaseSensitive"}); g.branch("bsw", "@sw.ReturnValue")
    g.call("pl", K_STR, "Len", inp={"S": "@mp.ReturnValue"}); g.call("gsub", K_STR, "GetSubstring", inp={"SourceString": "@ps.ReturnValue", "StartIndex": "@pl.ReturnValue", "Length": "1000"}); g.call("gname", K_STR, "Conv_StringToName", inp={"InString": "@gsub.ReturnValue"})
    g.n("gcd", "call_self", function="Group Caption Default", inp={"group": "@gname.ReturnValue"}); g.call("gcs", K_TXT, "Conv_TextToString", inp={"InText": "@gcd.caption"})
    g.get("gs2", "TmpStr3"); g.n("gm", "call_self", function="Name Matches", inp={"kind": "group", "row": "@gname.ReturnValue", "default": "@gcs.ReturnValue", "search": "@gs2.TmpStr3"}); g.branch("bgm", "@gm.yes")
    g.get("gn3b", "TmpNames3"); g.call("n3a", K_ARR, "Array_Add", inp={"TargetArray": "@gn3b.TmpNames3", "NewItem": "@gname.ReturnValue"})
    g.get("gn3c", "TmpNames3"); g.call("n3l", K_ARR, "Array_Length", inp={"TargetArray": "@gn3c.TmpNames3"}); g.call("n3g", K_MATH, "Greater_IntInt", inp={"A": "@n3l.ReturnValue", "B": "0"})
    g.get("gmm", "TmpBool"); g.call("show", K_MATH, "BooleanOR", inp={"A": "@gmm.TmpBool", "B": "@n3g.ReturnValue"}); g.branch("bshow", "@show.ReturnValue")
    last = add_key(g, "km", "mod", "@fm.Array Element", "bshow")
    g.get("gn3d", "TmpNames3"); g.foreach("fg", "@gn3d.TmpNames3"); g.chain(last, "fg"); add_key(g, "kg", "group", "@fg.Array Element", "fg")
    g.chain("bMods", "fm"); g.chain("fm", "smm", "n3c", "fp"); g.chain("fp", "bsw", "gcd", "bgm", "n3a"); g.chain("fp:Completed", "bshow"); g.chain("fm:Completed", "return")
    # --- Vanilla: the groups of vanilla pieces, as group rows
    g.get("gvg", "VanillaGroups"); g.foreach("fv", "@gvg.VanillaGroups")
    g.n("vcd", "call_self", function="Group Caption Default", inp={"group": "@fv.Array Element"}); g.call("vcs", K_TXT, "Conv_TextToString", inp={"InText": "@vcd.caption"})
    g.get("gs4", "TmpStr3"); g.n("vm", "call_self", function="Name Matches", inp={"kind": "group", "row": "@fv.Array Element", "default": "@vcs.ReturnValue", "search": "@gs4.TmpStr3"}); g.branch("bvm", "@vm.yes")
    add_key(g, "kv", "group", "@fv.Array Element", "bvm")
    g.chain("bVanilla", "fv"); g.chain("fv", "vcd", "bvm"); g.chain("fv:Completed", "return")
    # --- Clothes: catalog order
    g.get("gai", "AllItems"); g.foreach("fi", "@gai.AllItems"); g.brk("bi", S_ITEM, "@fi.Array Element")
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@bi.Name"}); g.get("gom", "TmpFound"); g.call("nom", K_MATH, "Not_PreBool", inp={"A": "@gom.TmpFound"})
    g.call("keep", K_MATH, "BooleanOR", inp={"A": "@nom.ReturnValue", "B": "@imd.found"})
    g.n("dfn", "call_self", function="Default Name", inp={"row": "@bi.Name"}); g.get("gs3", "TmpStr3")
    g.n("im", "call_self", function="Name Matches", inp={"kind": "item", "row": "@bi.Name", "default": "@dfn.s", "search": "@gs3.TmpStr3"})
    g.get("gsb", "ManageSub"); g.call("sbn", K_MATH, "EqualEqual_NameName", inp={"A": "@gsb.ManageSub", "B": "None"}); g.call("sbe", K_MATH, "EqualEqual_NameName", inp={"A": "@gsb.ManageSub", "B": "@bi.Slot"})
    g.call("sbok", K_MATH, "BooleanOR", inp={"A": "@sbn.ReturnValue", "B": "@sbe.ReturnValue"})   # sub item = slot
    g.call("iok0", K_MATH, "BooleanAND", inp={"A": "@keep.ReturnValue", "B": "@im.yes"}); g.call("iok", K_MATH, "BooleanAND", inp={"A": "@iok0.ReturnValue", "B": "@sbok.ReturnValue"}); g.branch("biok", "@iok.ReturnValue")
    add_key(g, "ki", "item", "@bi.Name", "biok")
    g.chain("bClothes", "fi"); g.chain("fi", "biok"); g.chain("fi:Completed", "return")
    # --- Hair / Skin / Makeup: table rows
    def table_rows(id, table, kind, prev, typed=None):
        """typed = row struct with a Type field: the row passes only when ManageSub is None or equals its Type."""
        g.call(id + "_rn", K_DT, "GetDataTableRowNames", inp={"Table": table}); g.foreach(id + "_fe", "@%s_rn.OutRowNames" % id)
        g.n(id + "_imd", "call_self", function="Item Mod", inp={"row": "@%s_fe.Array Element" % id}); g.get(id + "_gom", "TmpFound"); g.call(id + "_nom", K_MATH, "Not_PreBool", inp={"A": "@%s_gom.TmpFound" % id})
        g.call(id + "_keep", K_MATH, "BooleanOR", inp={"A": "@%s_nom.ReturnValue" % id, "B": "@%s_imd.found" % id})
        g.call(id + "_ds", K_STR, "Conv_NameToString", inp={"InName": "@%s_fe.Array Element" % id}); g.get(id + "_gs", "TmpStr3")
        g.n(id + "_m", "call_self", function="Name Matches", inp={"kind": kind, "row": "@%s_fe.Array Element" % id, "default": "@%s_ds.ReturnValue" % id, "search": "@%s_gs.TmpStr3" % id})
        g.call(id + "_ok0", K_MATH, "BooleanAND", inp={"A": "@%s_keep.ReturnValue" % id, "B": "@%s_m.yes" % id})
        if typed:
            g.n(id + "_row", "get_row", table=table, inp={"RowName": "@%s_fe.Array Element" % id}, miss="ignore"); g.brk(id + "_br", typed, "@%s_row.OutRow" % id)
            g.get(id + "_gsb", "ManageSub"); g.call(id + "_sn", K_MATH, "EqualEqual_NameName", inp={"A": "@%s_gsb.ManageSub" % id, "B": "None"})
            g.call(id + "_st", K_MATH, "EqualEqual_NameName", inp={"A": "@%s_gsb.ManageSub" % id, "B": "@%s_br.Type" % id}); g.call(id + "_sok", K_MATH, "BooleanOR", inp={"A": "@%s_sn.ReturnValue" % id, "B": "@%s_st.ReturnValue" % id})
            g.call(id + "_ok", K_MATH, "BooleanAND", inp={"A": "@%s_ok0.ReturnValue" % id, "B": "@%s_sok.ReturnValue" % id})
        else:
            g.call(id + "_ok", K_MATH, "BooleanAND", inp={"A": "@%s_ok0.ReturnValue" % id, "B": "true"})
        g.branch(id + "_b", "@%s_ok.ReturnValue" % id)
        add_key(g, id + "_k", kind, "@%s_fe.Array Element" % id, id + "_b")
        g.chain(prev, id + "_rn", id + "_fe"); g.chain(id + "_fe", *([id + "_row"] if typed else []), id + "_b"); return id + "_fe:Completed"
    # Look: hairstyles when the sub item is All / Hair, skins when All / Skin, then makeup + eye rows filtered by their Type
    g.get("gls", "ManageSub"); g.call("lsn", K_MATH, "EqualEqual_NameName", inp={"A": "@gls.ManageSub", "B": "None"})
    g.call("lsh", K_MATH, "EqualEqual_NameName", inp={"A": "@gls.ManageSub", "B": "Hair"}); g.call("lsho", K_MATH, "BooleanOR", inp={"A": "@lsn.ReturnValue", "B": "@lsh.ReturnValue"}); g.branch("bLookHair", "@lsho.ReturnValue"); g.chain("bLook", "bLookHair")
    hair_done = table_rows("h", P_HAIR_T, "hair", "bLookHair")
    g.call("lsk", K_MATH, "EqualEqual_NameName", inp={"A": "@gls.ManageSub", "B": "Skin"}); g.call("lso", K_MATH, "BooleanOR", inp={"A": "@lsn.ReturnValue", "B": "@lsk.ReturnValue"}); g.branch("bLookSkin", "@lso.ReturnValue")
    g.chain(hair_done, "bLookSkin"); g.chain("bLookHair:else", "bLookSkin")
    skin_done = table_rows("s", P_SKIN_T, "skin", "bLookSkin"); g.chain("bLookSkin:else", "m_rn")
    g.chain(table_rows("e", P_EYE_T, "makeup", table_rows("m", P_MAKEUP_T, "makeup", skin_done, typed=P_MAKEUP_S), typed=P_EYE_S), "return")
    g.chain("bLook:else", "return")
    return fn("Manage Rows", [param("cat", "name"), param("search", "string"), param("onlyMods", "bool")], [param("keys", "string", "array")], graph=g)


def f_manage_count():
    """Rows of a category for a search text, regardless of the sub item (ManageSub parked in TmpSubSave meanwhile)."""
    g = G(); g.get("gom", "OnlyModsNames")
    g.get("gsb", "ManageSub"); g.set("sv", "TmpSubSave", inp={"TmpSubSave": "@gsb.ManageSub"}); g.set("sn", "ManageSub", inp={"ManageSub": "None"})
    g.n("mr", "call_self", function="Manage Rows", inp={"cat": "@entry.cat", "search": "@entry.search", "onlyMods": "@gom.OnlyModsNames"})
    g.get("gsv", "TmpSubSave"); g.set("sr", "ManageSub", inp={"ManageSub": "@gsv.TmpSubSave"})
    g.call("ln", K_ARR, "Array_Length", inp={"TargetArray": "@mr.keys"}); g.link("ln.ReturnValue", "return.n"); g.chain("entry", "sv", "sn", "mr", "sr", "return")
    return fn("Manage Count", [param("cat", "name"), param("search", "string")], [param("n", "int")], graph=g)


def f_manage_sub_counts():
    """Rows of a category per sub item (Clothes: slot via ItemSlot; Look: Skin, else the makeup / eye row's Type) for a search text, ignoring the
    selected sub item -> ManageSubCounts (filtered = false: totals, search "") or ManageSubFiltered (filtered = true: the current search)."""
    g = G(); g.get("gm", "ManageSubCounts"); g.call("mc", K_MAP, "Map_Clear", inp={"TargetMap": "@gm.ManageSubCounts"})
    g.get("gmf", "ManageSubFiltered"); g.call("mcf", K_MAP, "Map_Clear", inp={"TargetMap": "@gmf.ManageSubFiltered"}); g.branch("bwhich", "@entry.filtered")
    g.get("gom", "OnlyModsNames")
    g.get("gsb", "ManageSub"); g.set("sv", "TmpSubSave", inp={"TmpSubSave": "@gsb.ManageSub"}); g.set("sn", "ManageSub", inp={"ManageSub": "None"})
    g.n("mr", "call_self", function="Manage Rows", inp={"cat": "@entry.cat", "search": "@entry.search", "onlyMods": "@gom.OnlyModsNames"})
    g.get("gsv", "TmpSubSave"); g.set("sr", "ManageSub", inp={"ManageSub": "@gsv.TmpSubSave"})
    g.set("sk", "TmpStrings2", inp={"TmpStrings2": "@mr.keys"}); g.get("gk", "TmpStrings2"); g.foreach("fe", "@gk.TmpStrings2")
    g.call("sp", K_STR, "Split", inp={"SourceString": "@fe.Array Element", "InStr": ":", "SearchCase": "CaseSensitive", "SearchDir": "FromStart"})
    g.call("rn", K_STR, "Conv_StringToName", inp={"InString": "@sp.RightS"}); g.set("srn", "TmpName2", inp={"TmpName2": "@rn.ReturnValue"}); g.get("grn", "TmpName2")
    g.call("isc", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.cat", "B": "Clothes"}); g.branch("bc", "@isc.ReturnValue")
    g.get("gis", "ItemSlot"); g.call("sf", K_MAP, "Map_Find", inp={"TargetMap": "@gis.ItemSlot", "Key": "@grn.TmpName2"}); g.set("s1", "TmpName", inp={"TmpName": "@sf.Value"})
    g.call("ish", K_STR, "EqualEqual_StrStr", inp={"A": "@sp.LeftS", "B": "hair"}); g.branch("bh", "@ish.ReturnValue"); g.set("s0", "TmpName", inp={"TmpName": "Hair"})
    g.call("isk", K_STR, "EqualEqual_StrStr", inp={"A": "@sp.LeftS", "B": "skin"}); g.branch("bk", "@isk.ReturnValue"); g.set("s2", "TmpName", inp={"TmpName": "Skin"})
    g.n("mrow", "get_row", table=P_MAKEUP_T, inp={"RowName": "@grn.TmpName2"}); g.brk("mbr", P_MAKEUP_S, "@mrow.OutRow"); g.set("s3", "TmpName", inp={"TmpName": "@mbr.Type"})
    g.n("erow", "get_row", table=P_EYE_T, inp={"RowName": "@grn.TmpName2"}); g.brk("ebr", P_EYE_S, "@erow.OutRow"); g.set("s4", "TmpName", inp={"TmpName": "@ebr.Type"}); g.set("s5", "TmpName", inp={"TmpName": "None"})
    # +1 in the chosen map
    g.get("gtn", "TmpName"); g.get("gm2", "ManageSubCounts"); g.call("cf", K_MAP, "Map_Find", inp={"TargetMap": "@gm2.ManageSubCounts", "Key": "@gtn.TmpName"})
    g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@cf.Value", "B": "1"}); g.get("gm3", "ManageSubCounts"); g.call("ca", K_MAP, "Map_Add", inp={"TargetMap": "@gm3.ManageSubCounts", "Key": "@gtn.TmpName", "Value": "@inc.ReturnValue"})
    g.get("gtn2", "TmpName"); g.get("gf2", "ManageSubFiltered"); g.call("cff", K_MAP, "Map_Find", inp={"TargetMap": "@gf2.ManageSubFiltered", "Key": "@gtn2.TmpName"})
    g.call("incf", K_MATH, "Add_IntInt", inp={"A": "@cff.Value", "B": "1"}); g.get("gf3", "ManageSubFiltered"); g.call("caf", K_MAP, "Map_Add", inp={"TargetMap": "@gf3.ManageSubFiltered", "Key": "@gtn2.TmpName", "Value": "@incf.ReturnValue"})
    g.branch("bw2", "@entry.filtered")
    g.chain("entry", "bwhich", "mcf", "sv"); g.chain("bwhich:else", "mc", "sv"); g.chain("sv", "sn", "mr", "sr", "sk", "fe")
    g.chain("fe", "srn", "bc", "s1", "bw2"); g.chain("bc:else", "bh", "s0", "bw2"); g.chain("bh:else", "bk", "s2", "bw2"); g.chain("bk:else", "mrow", "s3", "bw2")
    g.chain("mrow:Row Not Found", "erow", "s4", "bw2"); g.chain("erow:Row Not Found", "s5", "bw2"); g.chain("bw2", "caf"); g.chain("bw2:else", "ca")
    return fn("Manage Sub Counts", [param("cat", "name"), param("search", "string"), param("filtered", "bool")], graph=g)


def f_rebuild_manage_cats():
    """Left column of the Manage page. Mods / Vanilla: clickable category tabs. Clothes / Look: a section header (not clickable) with the sub items
    always shown and indented - All, then the slots / Skins + makeup types (tab slot "Sub:<cat>:<key>"). Counts follow the clothes page:
    total, plus "(hits)" while a search is active (Manage Count / Manage Sub Counts twice: search "" and the current search); sub items
    without rows (without hits while searching) are left out."""
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Manage Cats", inp={"self": "@gp.Panel"})
    # "only mods" checkbox only for the categories where vanilla rows can be dropped (Clothes / Look)
    prev = "false"
    for i, cat in enumerate(MANAGE_NO_ONLY_MODS):
        g.get("gnc%d" % i, "ManageCat"); g.call("ncat%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@gnc%d.ManageCat" % i, "B": cat}); g.call("nor%d" % i, K_MATH, "BooleanOR", inp={"A": prev, "B": "@ncat%d.ReturnValue" % i}); prev = "@nor%d.ReturnValue" % i
    g.call("omv", K_MATH, "Not_PreBool", inp={"A": prev}); g.get("gpo", "Panel"); g.call("som", W_PANEL, "Set Only Mods Visible", inp={"self": "@gpo.Panel", "visible": "@omv.ReturnValue"})
    g.get("gst", "ManageSearchText"); g.call("sne", K_STR, "IsEmpty", inp={"InString": "@gst.ManageSearchText"}); g.call("sact", K_MATH, "Not_PreBool", inp={"A": "@sne.ReturnValue"}); g.set("ssa", "ManageSearchActive", inp={"ManageSearchActive": "@sact.ReturnValue"})
    g.chain("entry", "cl", "som", "ssa"); sources = ["ssa"]
    for i, (cat, key) in enumerate(MANAGE_CATS):
        c = cat.lower()
        g.n("cnt%d" % i, "call_self", function="Manage Count", inp={"cat": cat, "search": ""})
        g.get("gst%d" % i, "ManageSearchText"); g.n("cntf%d" % i, "call_self", function="Manage Count", inp={"cat": cat, "search": "@gst%d.ManageSearchText" % i})
        g.get("gsa%d" % i, "ManageSearchActive"); g.call("fsel%d" % i, K_MATH, "SelectInt", inp={"A": "@cntf%d.n" % i, "B": "-1", "bPickA": "@gsa%d.ManageSearchActive" % i})   # -1 = no filter -> no parentheses
        g.get("gmc%d" % i, "ManageCat"); g.call("sel%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": cat, "B": "@gmc%d.ManageCat" % i})
        for src in sources: g.chain(src, "cnt%d" % i)
        if cat not in MANAGE_SUBS:
            tw = create_widget(g, "ct%d" % i, W_TAB); set_manager(g, "sm%d" % i, W_TAB, tw)
            g.call("ti%d" % i, W_TAB, "Init", inp={"self": tw, "slot": cat, "caption": tt(g, "cp%d" % i, key), "count": "@cnt%d.n" % i, "selected": "@sel%d.ReturnValue" % i, "has items": "true", "filtered": "@fsel%d.ReturnValue" % i})
            g.get("gp%d" % i, "Panel"); g.call("at%d" % i, W_PANEL, "Add Manage Cat", inp={"self": "@gp%d.Panel" % i, "widget": tw})
            g.chain("cnt%d" % i, "cntf%d" % i, "ct%d_cr" % i, "sm%d" % i, "ti%d" % i, "at%d" % i); sources = ["at%d" % i]; continue
        # section header
        hw = create_widget(g, "ch" + c, W_HEAD); set_manager(g, "shm" + c, W_HEAD, hw)
        g.call("hi" + c, W_HEAD, "Init", inp={"self": hw, "caption": tt(g, "hc" + c, key)}); g.get("gph" + c, "Panel"); g.call("ah" + c, W_PANEL, "Add Manage Cat", inp={"self": "@gph%s.Panel" % c, "widget": hw})
        # counts per sub item: totals, and the hits of the current search
        g.n("msc" + c, "call_self", function="Manage Sub Counts", inp={"cat": cat, "search": "", "filtered": "false"})
        g.get("gstf" + c, "ManageSearchText"); g.n("mscf" + c, "call_self", function="Manage Sub Counts", inp={"cat": cat, "search": "@gstf%s.ManageSearchText" % c, "filtered": "true"})
        # "All"
        aw = create_widget(g, "ca" + c, W_TAB); set_manager(g, "sa" + c, W_TAB, aw)
        g.get("gsa" + c, "ManageSub"); g.call("asn" + c, K_MATH, "EqualEqual_NameName", inp={"A": "@gsa%s.ManageSub" % c, "B": "None"}); g.call("asel" + c, K_MATH, "BooleanAND", inp={"A": "@asn%s.ReturnValue" % c, "B": "@sel%d.ReturnValue" % i})
        g.call("ai" + c, W_TAB, "Init", inp={"self": aw, "slot": g.lit_name("aln" + c, "Sub:%s:All" % cat), "caption": tt(g, "at" + c, "Chip_All"), "count": "@cnt%d.n" % i, "selected": "@asel%s.ReturnValue" % c, "has items": "true", "filtered": "@fsel%d.ReturnValue" % i, "indent": "true"})
        g.get("gpa" + c, "Panel"); g.call("aa" + c, W_PANEL, "Add Manage Cat", inp={"self": "@gpa%s.Panel" % c, "widget": aw})
        # sub keys: slots (Clothes) / Skin + makeup types (Look)
        if cat == "Clothes":
            g.get("gsl" + c, "Slots"); g.set("sks" + c, "TmpNames", inp={"TmpNames": "@gsl%s.Slots" % c}); keys_prep = ["sks" + c]
        else:
            g.call("mtr" + c, K_DT, "GetDataTableRowNames", inp={"Table": P_MTYPE_T}); g.set("sks" + c, "TmpNames", inp={"TmpNames": "@mtr%s.OutRowNames" % c})
            g.get("gn0" + c, "TmpNames"); g.call("ins" + c, K_ARR, "Array_Insert", inp={"TargetArray": "@gn0%s.TmpNames" % c, "NewItem": g.lit_name("lsk" + c, "Skin"), "Index": "0"})
            g.get("gn00" + c, "TmpNames"); g.call("insh" + c, K_ARR, "Array_Insert", inp={"TargetArray": "@gn00%s.TmpNames" % c, "NewItem": g.lit_name("lsh" + c, "Hair"), "Index": "0"}); keys_prep = ["mtr" + c, "sks" + c, "ins" + c, "insh" + c]
        g.get("gn" + c, "TmpNames"); g.foreach("fe" + c, "@gn%s.TmpNames" % c)
        g.get("gcm" + c, "ManageSubCounts"); g.call("cf" + c, K_MAP, "Map_Find", inp={"TargetMap": "@gcm%s.ManageSubCounts" % c, "Key": "@fe%s.Array Element" % c})
        g.get("gcf" + c, "ManageSubFiltered"); g.call("cff" + c, K_MAP, "Map_Find", inp={"TargetMap": "@gcf%s.ManageSubFiltered" % c, "Key": "@fe%s.Array Element" % c})
        g.get("gsb" + c, "ManageSearchActive"); g.call("shown" + c, K_MATH, "SelectInt", inp={"A": "@cff%s.Value" % c, "B": "@cf%s.Value" % c, "bPickA": "@gsb%s.ManageSearchActive" % c})   # searching: hits decide
        g.call("gt0" + c, K_MATH, "Greater_IntInt", inp={"A": "@shown%s.ReturnValue" % c, "B": "0"}); g.branch("bn" + c, "@gt0%s.ReturnValue" % c)
        g.call("fsub" + c, K_MATH, "SelectInt", inp={"A": "@cff%s.Value" % c, "B": "-1", "bPickA": "@gsb%s.ManageSearchActive" % c})
        sw = create_widget(g, "cs" + c, W_TAB); set_manager(g, "ss" + c, W_TAB, sw)
        g.call("ks" + c, K_STR, "Conv_NameToString", inp={"InName": "@fe%s.Array Element" % c}); g.call("kp" + c, K_STR, "Concat_StrStr", inp={"A": "Sub:%s:" % cat, "B": "@ks%s.ReturnValue" % c}); g.call("kn" + c, K_STR, "Conv_StringToName", inp={"InString": "@kp%s.ReturnValue" % c})
        if cat == "Clothes":
            cap = key_text(g, "sc" + c, "Slot_", "@fe%s.Array Element" % c); cap_nodes = []
        else:
            g.call("isk" + c, K_MATH, "EqualEqual_NameName", inp={"A": "@fe%s.Array Element" % c, "B": "Skin"}); g.call("ish" + c, K_MATH, "EqualEqual_NameName", inp={"A": "@fe%s.Array Element" % c, "B": "Hair"})
            g.n("lc" + c, "call_self", function="Look Caption", inp={"type": "@fe%s.Array Element" % c})
            g.call("lcs" + c, K_TXT, "Conv_TextToString", inp={"InText": "@lc%s.caption" % c}); g.call("sks2" + c, K_TXT, "Conv_TextToString", inp={"InText": tt(g, "skt" + c, "Cat_Skin")}); g.call("shs2" + c, K_TXT, "Conv_TextToString", inp={"InText": tt(g, "sht" + c, "Cat_Hair")})
            g.call("csel0" + c, K_MATH, "SelectString", inp={"A": "@sks2%s.ReturnValue" % c, "B": "@lcs%s.ReturnValue" % c, "bPickA": "@isk%s.ReturnValue" % c})
            g.call("csel" + c, K_MATH, "SelectString", inp={"A": "@shs2%s.ReturnValue" % c, "B": "@csel0%s.ReturnValue" % c, "bPickA": "@ish%s.ReturnValue" % c}); g.call("ct" + c, K_TXT, "Conv_StringToText", inp={"InString": "@csel%s.ReturnValue" % c})
            cap = "@ct%s.ReturnValue" % c; cap_nodes = ["lc" + c]
        g.get("gss" + c, "ManageSub"); g.call("ssk" + c, K_MATH, "EqualEqual_NameName", inp={"A": "@gss%s.ManageSub" % c, "B": "@fe%s.Array Element" % c}); g.call("ssel" + c, K_MATH, "BooleanAND", inp={"A": "@ssk%s.ReturnValue" % c, "B": "@sel%d.ReturnValue" % i})
        g.call("si" + c, W_TAB, "Init", inp={"self": sw, "slot": "@kn%s.ReturnValue" % c, "caption": cap, "count": "@cf%s.Value" % c, "selected": "@ssel%s.ReturnValue" % c, "has items": "true", "filtered": "@fsub%s.ReturnValue" % c, "indent": "true"})
        g.get("gps" + c, "Panel"); g.call("sa2" + c, W_PANEL, "Add Manage Cat", inp={"self": "@gps%s.Panel" % c, "widget": sw})
        g.chain("cnt%d" % i, "cntf%d" % i, "ch%s_cr" % c, "shm" + c, "hi" + c, "ah" + c, "msc" + c, "mscf" + c, "ca%s_cr" % c, "sa" + c, "ai" + c, "aa" + c, *keys_prep, "fe" + c)
        g.chain("fe" + c, "bn" + c, "cs%s_cr" % c, "ss" + c, *cap_nodes, "si" + c, "sa2" + c)
        sources = ["fe%s:Completed" % c]
    return fn("Rebuild Manage Cats", graph=g)


def f_select_manage_cat():
    """Category tab -> ManageCat (sub item back to All); sub tab "Sub:<cat>:<key>" -> ManageCat + ManageSub ("All" = None)."""
    g = G(); g.call("ns", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"}); g.call("sw", K_STR, "StartsWith", inp={"SourceString": "@ns.ReturnValue", "InPrefix": "Sub:", "SearchCase": "CaseSensitive"}); g.branch("bsub", "@sw.ReturnValue")
    g.call("rest", K_STR, "GetSubstring", inp={"SourceString": "@ns.ReturnValue", "StartIndex": "4", "Length": "1000"})
    g.call("sp", K_STR, "Split", inp={"SourceString": "@rest.ReturnValue", "InStr": ":", "SearchCase": "CaseSensitive", "SearchDir": "FromStart"})
    g.call("catn", K_STR, "Conv_StringToName", inp={"InString": "@sp.LeftS"}); g.set("sc", "ManageCat", inp={"ManageCat": "@catn.ReturnValue"})
    g.call("isall", K_STR, "EqualEqual_StrStr", inp={"A": "@sp.RightS", "B": "All"})
    g.call("subsel", K_MATH, "SelectString", inp={"A": "None", "B": "@sp.RightS", "bPickA": "@isall.ReturnValue"}); g.call("subn", K_STR, "Conv_StringToName", inp={"InString": "@subsel.ReturnValue"})
    g.set("ss", "ManageSub", inp={"ManageSub": "@subn.ReturnValue"})
    g.set("s", "ManageCat", inp={"ManageCat": "@entry.name"}); g.set("s0", "ManageSub", inp={"ManageSub": "None"})
    g.n("rc", "call_self", function="Rebuild Manage Cats"); g.n("rm", "call_self", function="Rebuild Manage")
    g.chain("entry", "bsub", "sc", "ss", "rc", "rm"); g.chain("bsub:else", "s", "s0", "rc"); return fn("Select Manage Cat", [param("name", "name")], graph=g)


def f_manage_default():
    """Default (non-custom) display text of a Manage row: mod caption / group caption / item default name / row name."""
    g = G()
    g.call("ism", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "mod"}); g.branch("bm", "@ism.ReturnValue")
    g.get("gmc", "ModCaption"); g.call("mcf", K_MAP, "Map_Find", inp={"TargetMap": "@gmc.ModCaption", "Key": "@entry.row"}); g.call("mcs", K_TXT, "Conv_TextToString", inp={"InText": "@mcf.Value"})
    g.call("rs", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"}); g.call("msel", K_MATH, "SelectString", inp={"A": "@mcs.ReturnValue", "B": "@rs.ReturnValue", "bPickA": "@mcf.ReturnValue"})
    g.set("s1", "TmpStr3", inp={"TmpStr3": "@msel.ReturnValue"})
    g.call("isg", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "group"}); g.branch("bg", "@isg.ReturnValue")
    g.n("gcd", "call_self", function="Group Caption Default", inp={"group": "@entry.row"}); g.call("gcs", K_TXT, "Conv_TextToString", inp={"InText": "@gcd.caption"}); g.set("s2", "TmpStr3", inp={"TmpStr3": "@gcs.ReturnValue"})
    g.call("isi", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "item"}); g.branch("bi", "@isi.ReturnValue")
    g.n("dfn", "call_self", function="Default Name", inp={"row": "@entry.row"}); g.set("s3", "TmpStr3", inp={"TmpStr3": "@dfn.s"})
    g.set("s4", "TmpStr3", inp={"TmpStr3": "@rs.ReturnValue"})
    g.get("gt", "TmpStr3"); g.link("gt.TmpStr3", "return.s")
    g.chain("entry", "bm", "s1", "return"); g.chain("bm:else", "bg", "gcd", "s2", "return"); g.chain("bg:else", "bi", "s3", "return"); g.chain("bi:else", "s4", "return")
    return fn("Manage Default", [param("kind", "name"), param("row", "name")], [param("s", "string")], graph=g)


def f_manage_origin():
    """Identifier column of a Manage row. origin: mod -> "pak: <mod>"; group -> "g: <group>[\nalso affects:\nPAK: <other mod display name>…]";
    item / hair / skin / makeup -> "id: <row>" (vanilla: + "\nVanilla"). mod: the piece's mod (None for mod / group rows and vanilla) - the row shows it
    as the "pak: <mod>" link. rest: item -> "g: <group>" (or empty), makeup -> the type caption, else empty."""
    g = G()
    g.call("rs", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"})
    for k, key in (("ti", "Tip_Id"), ("tp", "Tip_Pak"), ("tg", "Tip_Grp"), ("tv", "Lbl_Vanilla"), ("ta", "Lbl_AlsoAffects")):
        g.n(k, "call_self", function="T", inp={"key": key}); g.call(k + "s", K_TXT, "Conv_TextToString", inp={"InText": "@%s.text" % k})
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@entry.row"}); g.call("ms", K_STR, "Conv_NameToString", inp={"InName": "@imd.mod"})
    g.call("pk1", K_STR, "Concat_StrStr", inp={"A": "@tps.ReturnValue", "B": "@ms.ReturnValue"})
    g.call("orig", K_MATH, "SelectString", inp={"A": "@pk1.ReturnValue", "B": "@tvs.ReturnValue", "bPickA": "@imd.found"})   # "pak: X" or "Vanilla"
    g.call("id1", K_STR, "Concat_StrStr", inp={"A": "@tis.ReturnValue", "B": "@rs.ReturnValue"}); g.call("id2", K_STR, "Concat_StrStr", inp={"A": "@id1.ReturnValue", "B": "\n"})
    g.call("idv", K_STR, "Concat_StrStr", inp={"A": "@id2.ReturnValue", "B": "@tvs.ReturnValue"})
    g.call("idp", K_MATH, "SelectString", inp={"A": "@id1.ReturnValue", "B": "@idv.ReturnValue", "bPickA": "@imd.found"})   # "id: X" (the pak goes to the link line) / "id: X\nVanilla"
    g.set("sr0", "TmpRest", inp={"TmpRest": ""}); g.set("sm0", "TmpMod", inp={"TmpMod": "None"})
    g.call("mdn", K_MATH, "SelectString", inp={"A": "@ms.ReturnValue", "B": "None", "bPickA": "@imd.found"}); g.call("mdnn", K_STR, "Conv_StringToName", inp={"InString": "@mdn.ReturnValue"}); g.set("sm1", "TmpMod", inp={"TmpMod": "@mdnn.ReturnValue"})
    # mod
    g.call("ism", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "mod"}); g.branch("bm", "@ism.ReturnValue")
    g.call("mi", K_STR, "Concat_StrStr", inp={"A": "@tps.ReturnValue", "B": "@rs.ReturnValue"}); g.set("s1", "TmpStr3", inp={"TmpStr3": "@mi.ReturnValue"})
    # group: "g: <id>", and for a group shared by several paks "also affects:" + the other paks (ModGroupPairs, TmpParentMod = the header above)
    g.call("isg", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "group"}); g.branch("bg", "@isg.ReturnValue")
    g.call("gi", K_STR, "Concat_StrStr", inp={"A": "@tgs.ReturnValue", "B": "@rs.ReturnValue"}); g.set("s2", "TmpStr3", inp={"TmpStr3": "@gi.ReturnValue"}); g.set("sf0", "TmpFound", inp={"TmpFound": "false"})
    g.get("gpp", "ModGroupPairs"); g.foreach("fp", "@gpp.ModGroupPairs"); g.call("ps", K_STR, "Conv_NameToString", inp={"InName": "@fp.Array Element"})
    g.call("sp", K_STR, "Split", inp={"SourceString": "@ps.ReturnValue", "InStr": "|", "SearchCase": "CaseSensitive", "SearchDir": "FromStart"})
    g.call("gEq", K_STR, "EqualEqual_StrStr", inp={"A": "@sp.RightS", "B": "@rs.ReturnValue"}); g.call("pmn", K_STR, "Conv_StringToName", inp={"InString": "@sp.LeftS"})
    g.get("gpm", "TmpParentMod"); g.call("mNe", K_MATH, "NotEqual_NameName", inp={"A": "@pmn.ReturnValue", "B": "@gpm.TmpParentMod"})
    g.call("oth", K_MATH, "BooleanAND", inp={"A": "@gEq.ReturnValue", "B": "@mNe.ReturnValue"}); g.branch("bo", "@oth.ReturnValue")
    g.get("gf", "TmpFound"); g.branch("bf", "@gf.TmpFound")   # first other pak: the "also affects:" line
    g.get("gs3a", "TmpStr3"); g.call("h1", K_STR, "Concat_StrStr", inp={"A": "@gs3a.TmpStr3", "B": "\n"}); g.call("h2", K_STR, "Concat_StrStr", inp={"A": "@h1.ReturnValue", "B": "@tas.ReturnValue"})
    g.set("sh", "TmpStr3", inp={"TmpStr3": "@h2.ReturnValue"}); g.set("sf1", "TmpFound", inp={"TmpFound": "true"})
    g.n("mcp", "call_self", function="Mod Caption", inp={"mod": "@pmn.ReturnValue"})
    g.n("tk", "call_self", function="T", inp={"key": "Lbl_KindMod"}); g.call("tks", K_TXT, "Conv_TextToString", inp={"InText": "@tk.text"}); g.call("tkp", K_STR, "Concat_StrStr", inp={"A": "@tks.ReturnValue", "B": ": "})
    g.get("gs3b", "TmpStr3"); g.call("m1", K_STR, "Concat_StrStr", inp={"A": "@gs3b.TmpStr3", "B": "\n"}); g.call("m1p", K_STR, "Concat_StrStr", inp={"A": "@m1.ReturnValue", "B": "@tkp.ReturnValue"})
    g.call("m2", K_STR, "Concat_StrStr", inp={"A": "@m1p.ReturnValue", "B": "@mcp.s"}); g.set("sm", "TmpStr3", inp={"TmpStr3": "@m2.ReturnValue"})   # "PAK: <display name>" per other pak (upper case = display name)
    # item: + group
    g.call("isi", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "item"}); g.branch("bi", "@isi.ReturnValue")
    g.n("fi", "call_self", function="Find Item", inp={"name": "@entry.row"}); g.brk("bfi", S_ITEM, "@fi.item")
    g.call("gne", K_MATH, "NotEqual_NameName", inp={"A": "@bfi.Group", "B": "None"}); g.branch("bgr", "@gne.ReturnValue")
    g.call("gs", K_STR, "Conv_NameToString", inp={"InName": "@bfi.Group"}); g.call("o2", K_STR, "Concat_StrStr", inp={"A": "@tgs.ReturnValue", "B": "@gs.ReturnValue"})
    g.set("s3r", "TmpRest", inp={"TmpRest": "@o2.ReturnValue"}); g.set("s3", "TmpStr3", inp={"TmpStr3": "@idp.ReturnValue"}); g.set("s3p", "TmpStr3", inp={"TmpStr3": "@idp.ReturnValue"})
    # makeup: + type caption
    g.call("isk", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "makeup"}); g.branch("bk", "@isk.ReturnValue")
    g.n("mrow", "get_row", table=P_MAKEUP_T, inp={"RowName": "@entry.row"}); g.brk("mbr", P_MAKEUP_S, "@mrow.OutRow"); g.set("st1", "TmpGroup", inp={"TmpGroup": "@mbr.Type"})
    g.n("erow", "get_row", table=P_EYE_T, inp={"RowName": "@entry.row"}); g.brk("ebr", P_EYE_S, "@erow.OutRow"); g.set("st2", "TmpGroup", inp={"TmpGroup": "@ebr.Type"}); g.set("st3", "TmpGroup", inp={"TmpGroup": "None"})
    g.get("gtn", "TmpGroup"); g.n("lc", "call_self", function="Look Caption", inp={"type": "@gtn.TmpGroup"}); g.call("lcs", K_TXT, "Conv_TextToString", inp={"InText": "@lc.caption"})
    g.set("s4r", "TmpRest", inp={"TmpRest": "@lcs.ReturnValue"}); g.set("s4", "TmpStr3", inp={"TmpStr3": "@idp.ReturnValue"})
    # hair / skin
    g.set("s5", "TmpStr3", inp={"TmpStr3": "@idp.ReturnValue"})
    g.get("gt", "TmpStr3"); g.call("tt", K_TXT, "Conv_StringToText", inp={"InString": "@gt.TmpStr3"}); g.link("tt.ReturnValue", "return.origin")
    g.get("gtr", "TmpRest"); g.call("ttr", K_TXT, "Conv_StringToText", inp={"InString": "@gtr.TmpRest"}); g.link("ttr.ReturnValue", "return.rest"); g.get("gtm", "TmpMod"); g.link("gtm.TmpMod", "return.mod")
    g.chain("entry", "sr0", "sm0", "bm", "s1", "return"); g.chain("bm:else", "bg", "s2", "sf0", "fp"); g.chain("fp", "bo", "bf", "sm"); g.chain("bf:else", "sh", "sf1", "sm"); g.chain("fp:Completed", "return")
    g.chain("bg:else", "sm1", "bi", "fi", "bgr", "s3r", "s3", "return"); g.chain("bgr:else", "s3p", "return")
    g.chain("bi:else", "bk", "mrow", "st1", "lc", "s4r", "s4", "return"); g.chain("mrow:Row Not Found", "erow", "st2", "lc"); g.chain("erow:Row Not Found", "st3", "lc")
    g.chain("bk:else", "s5", "return")
    return fn("Manage Origin", [param("kind", "name"), param("row", "name")], [param("origin", "text"), param("mod", "name"), param("rest", "text")], graph=g)


def f_manage_icon():
    """Tile icon of a Manage row (item / hair / skin / makeup), None for mods and groups."""
    g = G(); g.set("s0", "TmpTex", inp={"TmpTex": "None"})
    g.call("isi", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "item"}); g.branch("bi", "@isi.ReturnValue")
    g.n("fi", "call_self", function="Find Item", inp={"name": "@entry.row"}); g.brk("bfi", S_ITEM, "@fi.item"); g.set("s1", "TmpTex", inp={"TmpTex": "@bfi.Icon"})
    g.call("ish", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "hair"}); g.branch("bh", "@ish.ReturnValue")
    g.n("hrow", "get_row", table=P_HAIR_T, inp={"RowName": "@entry.row"}, miss="ignore"); g.brk("hbr", P_HAIR_S, "@hrow.OutRow"); g.set("s2", "TmpTex", inp={"TmpTex": "@hbr.icon"})
    g.call("iss", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "skin"}); g.branch("bs", "@iss.ReturnValue")
    g.n("srow", "get_row", table=P_SKIN_T, inp={"RowName": "@entry.row"}, miss="ignore"); g.brk("sbr", P_SKIN_S, "@srow.OutRow"); g.set("s3", "TmpTex", inp={"TmpTex": "@sbr.icon"})
    g.call("isk", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "makeup"}); g.branch("bk", "@isk.ReturnValue")
    g.n("mrow", "get_row", table=P_MAKEUP_T, inp={"RowName": "@entry.row"}); g.brk("mbr", P_MAKEUP_S, "@mrow.OutRow"); g.set("s4", "TmpTex", inp={"TmpTex": "@mbr.Icon"})
    g.n("erow", "get_row", table=P_EYE_T, inp={"RowName": "@entry.row"}, miss="ignore"); g.brk("ebr", P_EYE_S, "@erow.OutRow"); g.set("s5", "TmpTex", inp={"TmpTex": "@ebr.Icon"})
    g.get("gt", "TmpTex"); g.link("gt.TmpTex", "return.tex")
    g.chain("entry", "s0", "bi", "fi", "s1", "return"); g.chain("bi:else", "bh", "hrow", "s2", "return"); g.chain("bh:else", "bs", "srow", "s3", "return")
    g.chain("bs:else", "bk", "mrow", "s4", "return"); g.chain("mrow:Row Not Found", "erow", "s5", "return"); g.chain("bk:else", "return")
    return fn("Manage Icon", [param("kind", "name"), param("row", "name")], [param("tex", "object:" + E_TEX2D)], graph=g)


def f_rebuild_manage():
    """Manage page rows: one W_NameRow per key of Manage Rows(ManageCat, ManageSearchText, OnlyModsNames)."""
    g = G()
    g.get("gp0", "Panel"); g.call("pv", K_SYS, "IsValid", inp={"Object": "@gp0.Panel"}); g.branch("bpv", "@pv.ReturnValue")
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Manage Rows", inp={"self": "@gp.Panel"})
    g.get("gwl", "ManageRowWidgets"); g.call("wlc", K_ARR, "Array_Clear", inp={"TargetArray": "@gwl.ManageRowWidgets"})
    g.set("spm0", "TmpParentMod", inp={"TmpParentMod": "None"})   # group rows without a mod header above (Vanilla) list every pak sharing the group
    g.get("gmc", "ManageCat"); g.get("gst", "ManageSearchText"); g.get("gom", "OnlyModsNames")
    g.n("mr", "call_self", function="Manage Rows", inp={"cat": "@gmc.ManageCat", "search": "@gst.ManageSearchText", "onlyMods": "@gom.OnlyModsNames"})
    g.set("sk", "TmpStrings2", inp={"TmpStrings2": "@mr.keys"}); g.get("gk", "TmpStrings2"); g.foreach("fe", "@gk.TmpStrings2")
    g.call("sp", K_STR, "Split", inp={"SourceString": "@fe.Array Element", "InStr": ":", "SearchCase": "CaseSensitive", "SearchDir": "FromStart"})
    g.call("kn", K_STR, "Conv_StringToName", inp={"InString": "@sp.LeftS"}); g.call("rn", K_STR, "Conv_StringToName", inp={"InString": "@sp.RightS"})
    g.set("skn", "TmpName", inp={"TmpName": "@kn.ReturnValue"}); g.set("srn", "TmpName2", inp={"TmpName2": "@rn.ReturnValue"}); g.get("gkn", "TmpName"); g.get("grn", "TmpName2")
    g.call("ismh", K_MATH, "EqualEqual_NameName", inp={"A": "@kn.ReturnValue", "B": "mod"}); g.branch("bmh", "@ismh.ReturnValue"); g.set("spm", "TmpParentMod", inp={"TmpParentMod": "@rn.ReturnValue"})
    g.n("md", "call_self", function="Manage Default", inp={"kind": "@gkn.TmpName", "row": "@grn.TmpName2"}); g.set("sdf", "TmpStr2", inp={"TmpStr2": "@md.s"}); g.get("gdf", "TmpStr2")
    g.n("mo", "call_self", function="Manage Origin", inp={"kind": "@gkn.TmpName", "row": "@grn.TmpName2"}); g.set("sor", "TmpText", inp={"TmpText": "@mo.origin"}); g.get("gor", "TmpText")
    g.set("smd", "TmpMod", inp={"TmpMod": "@mo.mod"}); g.get("gmd", "TmpMod"); g.set("srs", "TmpRest2", inp={"TmpRest2": "@mo.rest"}); g.get("grs", "TmpRest2")
    g.n("mi", "call_self", function="Manage Icon", inp={"kind": "@gkn.TmpName", "row": "@grn.TmpName2"}); g.set("sic", "TmpTex", inp={"TmpTex": "@mi.tex"}); g.get("gic", "TmpTex")
    g.n("cn", "call_self", function="Custom Name", inp={"kind": "@gkn.TmpName", "row": "@grn.TmpName2"})
    g.call("isg", K_MATH, "EqualEqual_NameName", inp={"A": "@gkn.TmpName", "B": "group"}); g.call("ism", K_MATH, "EqualEqual_NameName", inp={"A": "@gkn.TmpName", "B": "mod"})
    g.call("nf", K_MATH, "Greater_IntInt", inp={"A": "@fe.Array Index", "B": "0"}); g.call("gap", K_MATH, "BooleanAND", inp={"A": "@ism.ReturnValue", "B": "@nf.ReturnValue"})   # air above a mod header that follows other rows
    rw = create_widget(g, "cw", W_NAMEROW); set_manager(g, "smw", W_NAMEROW, rw)
    g.call("ini", W_NAMEROW, "Init", inp={"self": rw, "kind": "@gkn.TmpName", "row": "@grn.TmpName2", "default": "@gdf.TmpStr2", "custom": "@cn.name", "origin": "@gor.TmpText", "icon": "@gic.TmpTex", "indent": "@isg.ReturnValue", "content": "@ism.ReturnValue", "gap": "@gap.ReturnValue", "mod": "@gmd.TmpMod", "rest": "@grs.TmpRest2"})
    g.get("gp2", "Panel"); g.call("ad", W_PANEL, "Add Manage Row", inp={"self": "@gp2.Panel", "widget": rw})
    g.get("gwl2", "ManageRowWidgets"); g.call("wla", K_ARR, "Array_Add", inp={"TargetArray": "@gwl2.ManageRowWidgets", "NewItem": rw})
    g.chain("entry", "bpv", "cl", "wlc", "spm0", "mr", "sk", "fe"); g.chain("fe", "skn", "srn", "bmh", "spm", "md"); g.chain("bmh:else", "md"); g.chain("md", "sdf", "mo", "sor", "smd", "srs", "mi", "sic", "cw_cr", "smw", "ini", "ad", "wla")
    return fn("Rebuild Manage", graph=g)


def f_focus_name_row():
    """Tab / Shift+Tab in a name row: keyboard focus to the next / previous row's text field (wraps), scrolled into view."""
    g = G(); g.get("gl", "ManageRowWidgets"); g.call("fi", K_ARR, "Array_Find", inp={"TargetArray": "@gl.ManageRowWidgets", "ItemToFind": "@entry.row"})
    g.get("gl2", "ManageRowWidgets"); g.call("ln", K_ARR, "Array_Length", inp={"TargetArray": "@gl2.ManageRowWidgets"})
    g.call("step", K_MATH, "SelectInt", inp={"A": "-1", "B": "1", "bPickA": "@entry.backwards"}); g.call("nx", K_MATH, "Add_IntInt", inp={"A": "@fi.ReturnValue", "B": "@step.ReturnValue"})
    g.call("nx2", K_MATH, "Add_IntInt", inp={"A": "@nx.ReturnValue", "B": "@ln.ReturnValue"}); g.call("idx", K_MATH, "Percent_IntInt", inp={"A": "@nx2.ReturnValue", "B": "@ln.ReturnValue"})   # wrap both ways
    g.call("ok", K_MATH, "Greater_IntInt", inp={"A": "@ln.ReturnValue", "B": "0"}); g.branch("b", "@ok.ReturnValue")
    g.get("gl3", "ManageRowWidgets"); g.call("gt", K_ARR, "Array_Get", inp={"TargetArray": "@gl3.ManageRowWidgets", "Index": "@idx.ReturnValue"})
    g.cast("cr", W_NAMEROW, "@gt.Item"); g.call("fe", W_NAMEROW, "Focus Edit", inp={"self": "@cr.AsW_NameRow"})
    g.get("gp", "Panel"); g.call("siv", W_PANEL, "Scroll Into View", inp={"self": "@gp.Panel", "page": "Manage", "widget": "@gt.Item"})
    g.chain("entry", "b", "fe", "siv")
    return fn("Focus Name Row", [param("row", "object:" + E_USERWIDGET), param("backwards", "bool")], graph=g)


def f_refresh_manage_rows():
    """After a name change: mod / group rows of the Manage page re-read their stored name and identifiers (a mod's display name sits in
    'also affects' lines, a shared group's name in the G: rows under other mods). No widget rebuild: scroll position and focus stay.
    TmpParentMod follows the mod headers like in Rebuild Manage; item / hair / skin / makeup rows show nothing foreign and are skipped."""
    g = G(); g.set("spm0", "TmpParentMod", inp={"TmpParentMod": "None"}); g.get("gl", "ManageRowWidgets"); g.foreach("fe", "@gl.ManageRowWidgets"); g.cast("cr", W_NAMEROW, "@fe.Array Element")
    g.get("gk", "Kind", cls=W_NAMEROW); g.link("cr.AsW_NameRow", "gk.self"); g.get("grw", "Row", cls=W_NAMEROW); g.link("cr.AsW_NameRow", "grw.self")
    g.set("skn", "TmpName", inp={"TmpName": "@gk.Kind"}); g.set("srn", "TmpName2", inp={"TmpName2": "@grw.Row"}); g.get("gkn", "TmpName"); g.get("grn", "TmpName2")
    g.call("ism", K_MATH, "EqualEqual_NameName", inp={"A": "@gkn.TmpName", "B": "mod"}); g.branch("bm", "@ism.ReturnValue"); g.set("spm", "TmpParentMod", inp={"TmpParentMod": "@grn.TmpName2"})
    g.call("isg", K_MATH, "EqualEqual_NameName", inp={"A": "@gkn.TmpName", "B": "group"}); g.call("mg", K_MATH, "BooleanOR", inp={"A": "@ism.ReturnValue", "B": "@isg.ReturnValue"}); g.branch("bmg", "@mg.ReturnValue")
    g.n("cn", "call_self", function="Custom Name", inp={"kind": "@gkn.TmpName", "row": "@grn.TmpName2"})
    g.n("mo", "call_self", function="Manage Origin", inp={"kind": "@gkn.TmpName", "row": "@grn.TmpName2"})
    g.call("rf", W_NAMEROW, "Refresh", inp={"self": "@cr.AsW_NameRow", "custom": "@cn.name", "origin": "@mo.origin"})
    g.chain("entry", "spm0", "fe"); g.chain("fe", "skn", "srn", "bm", "spm", "bmg"); g.chain("bm:else", "bmg"); g.chain("bmg", "mo", "rf")
    return fn("Refresh Manage Rows", graph=g)


def f_rename_kind():
    """Name kind of a tile's row: catalog item -> item; hairstyle / skin table row -> hair / skin; else makeup (makeup + eyes share 'makeup')."""
    g = G(); g.get("gib", "ItemByName"); g.call("ci", K_MAP, "Map_Contains", inp={"TargetMap": "@gib.ItemByName", "Key": "@entry.name"})
    g.call("ch", K_DT, "DoesDataTableRowExist", inp={"Table": P_HAIR_T, "RowName": "@entry.name"}); g.call("cs", K_DT, "DoesDataTableRowExist", inp={"Table": P_SKIN_T, "RowName": "@entry.name"})
    g.call("s1", K_MATH, "SelectString", inp={"A": "skin", "B": "makeup", "bPickA": "@cs.ReturnValue"}); g.call("s2", K_MATH, "SelectString", inp={"A": "hair", "B": "@s1.ReturnValue", "bPickA": "@ch.ReturnValue"})
    g.call("s3", K_MATH, "SelectString", inp={"A": "item", "B": "@s2.ReturnValue", "bPickA": "@ci.ReturnValue"}); g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@s3.ReturnValue"}); g.link("s2n.ReturnValue", "return.kind")
    g.chain("entry", "ch", "cs", "return")   # DoesDataTableRowExist has exec pins -> not pure
    return fn("Rename Kind", [param("name", "name")], [param("kind", "name")], graph=g)


def f_start_item_rename():
    """Context menu 'Rename…': the text field on the last clicked tile with the shown name; the manager polls the tile for focus loss (Tick)."""
    g = G(); g.get("glb", "LastButton"); g.cast("cb", W_BTN, "@glb.LastButton"); g.call("cv", K_SYS, "IsValid", inp={"Object": "@cb.AsW_ClothesButton"}); g.branch("bv", "@cv.ReturnValue")
    g.n("rk", "call_self", function="Rename Kind", inp={"name": "@entry.name"}); g.n("dn", "call_self", function="Display Name", inp={"kind": "@rk.kind", "row": "@entry.name"})
    g.get("glb2", "LastButton"); g.set("srt", "RenameTile", inp={"RenameTile": "@glb2.LastButton"})
    g.call("br", W_BTN, "Begin Rename", inp={"self": "@cb.AsW_ClothesButton", "current": "@dn.s"}); g.chain("entry", "bv", "rk", "srt", "br")
    return fn("Start Item Rename", [param("name", "name")], graph=g)


def f_finish_item_rename():
    """Enter in a tile's rename field: trimmed text (equal to the default stores nothing) -> Set Custom Name, then the page shows the name."""
    g = G(); g.n("rk", "call_self", function="Rename Kind", inp={"name": "@entry.name"}); g.set("skn", "TmpName", inp={"TmpName": "@rk.kind"}); g.get("gkn", "TmpName")
    g.call("tr", K_STR, "Trim", inp={"SourceString": "@entry.text"}); g.call("tr2", K_STR, "TrimTrailing", inp={"SourceString": "@tr.ReturnValue"})
    g.n("md", "call_self", function="Manage Default", inp={"kind": "@gkn.TmpName", "row": "@entry.name"})
    g.call("same", K_STR, "EqualEqual_StrStr", inp={"A": "@tr2.ReturnValue", "B": "@md.s"}); g.call("val", K_MATH, "SelectString", inp={"A": "", "B": "@tr2.ReturnValue", "bPickA": "@same.ReturnValue"})
    g.get("gkn2", "TmpName"); g.n("sn", "call_self", function="Set Custom Name", inp={"kind": "@gkn2.TmpName", "row": "@entry.name", "name": "@val.ReturnValue"})
    g.n("ra", "call_self", function="Refresh After Rename"); g.chain("entry", "rk", "skn", "md", "sn", "ra")
    return fn("Finish Item Rename", [param("name", "name"), param("text", "string")], graph=g)


def f_refresh_after_rename():
    """Catalog (names + search), then the tiles of the current view: content view / clothes list / bag / hair / look."""
    g = G(); g.n("rc", "call_self", function="Rebuild Catalog If Dirty")
    g.get("gpg0", "Page"); g.n("cop", "call_self", function="Content Open", inp={"page": "@gpg0.Page"}); g.branch("bco", "@cop.yes"); g.n("rct", "call_self", function="Rebuild Content")
    pages = [("Clothes", "Rebuild List"), ("Bag", "Rebuild Bag"), ("Hair", "Rebuild Hair"), ("Look", "Rebuild Look")]
    for i, (pg, fnn) in enumerate(pages):
        g.get("gpg%d" % (i + 1), "Page"); g.call("is%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@gpg%d.Page" % (i + 1), "B": pg}); g.branch("b%d" % i, "@is%d.ReturnValue" % i); g.n("r%d" % i, "call_self", function=fnn)
    g.chain("entry", "rc", "cop", "bco", "rct"); g.chain("bco:else", "b0", "r0")   # Content Open has exec pins
    for i in range(len(pages) - 1): g.chain("b%d:else" % i, "b%d" % (i + 1), "r%d" % (i + 1))
    return fn("Refresh After Rename", graph=g)


def f_manage_rename():
    """'Rename mod… / Rename group…': the Manage tab, category cat (Mods / Vanilla), search cleared, the row's text field focused and scrolled
    into view. ManageCat before Select Page (Select Page rebuilds the Manage page with the current category)."""
    g = G(); g.set("smc", "ManageCat", inp={"ManageCat": "@entry.cat"}); g.set("sst", "ManageSearchText", inp={"ManageSearchText": ""}); g.set("spp", "Page", inp={"Page": "Manage"})   # Page also without a panel (editor tests)
    g.get("gp", "Panel"); g.call("pv", K_SYS, "IsValid", inp={"Object": "@gp.Panel"}); g.branch("bpv", "@pv.ReturnValue")
    g.get("gp2", "Panel"); g.call("pcs", W_PANEL, "Clear Manage Search", inp={"self": "@gp2.Panel"})
    g.n("sp", "call_self", function="Select Page", inp={"name": "Manage"})
    g.get("gl", "ManageRowWidgets"); g.foreach("fe", "@gl.ManageRowWidgets"); g.cast("cr", W_NAMEROW, "@fe.Array Element")
    g.get("gk", "Kind", cls=W_NAMEROW); g.link("cr.AsW_NameRow", "gk.self"); g.get("grw", "Row", cls=W_NAMEROW); g.link("cr.AsW_NameRow", "grw.self")
    g.call("ek", K_MATH, "EqualEqual_NameName", inp={"A": "@gk.Kind", "B": "@entry.kind"}); g.call("er", K_MATH, "EqualEqual_NameName", inp={"A": "@grw.Row", "B": "@entry.row"})
    g.call("hit", K_MATH, "BooleanAND", inp={"A": "@ek.ReturnValue", "B": "@er.ReturnValue"}); g.branch("bh", "@hit.ReturnValue")
    g.call("fe2", W_NAMEROW, "Focus Edit", inp={"self": "@cr.AsW_NameRow"}); g.get("gp3", "Panel"); g.call("siv", W_PANEL, "Scroll Into View", inp={"self": "@gp3.Panel", "page": "Manage", "widget": "@fe.Array Element"})
    g.chain("entry", "smc", "sst", "spp", "bpv", "pcs", "sp", "fe"); g.chain("fe", "bh", "fe2", "siv")
    return fn("Manage Rename", [param("kind", "name"), param("row", "name"), param("cat", "name")], graph=g)


def f_manage_go_to():
    """Click on a Manage row's icon: jump to the piece on its own page (Go To Item with ContextSlot = clothes slot / Hair / Skin / makeup type)."""
    g = G(); g.call("isi", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "item"}); g.branch("bi", "@isi.ReturnValue")
    g.get("gis", "ItemSlot"); g.call("sf", K_MAP, "Map_Find", inp={"TargetMap": "@gis.ItemSlot", "Key": "@entry.row"}); g.set("s1", "ContextSlot", inp={"ContextSlot": "@sf.Value"})
    g.call("ish", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "hair"}); g.branch("bh", "@ish.ReturnValue"); g.set("s2", "ContextSlot", inp={"ContextSlot": "Hair"})
    g.call("iss", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "skin"}); g.branch("bs", "@iss.ReturnValue"); g.set("s3", "ContextSlot", inp={"ContextSlot": "Skin"})
    g.n("mrow", "get_row", table=P_MAKEUP_T, inp={"RowName": "@entry.row"}); g.brk("mbr", P_MAKEUP_S, "@mrow.OutRow"); g.set("s4", "ContextSlot", inp={"ContextSlot": "@mbr.Type"})
    g.n("erow", "get_row", table=P_EYE_T, inp={"RowName": "@entry.row"}); g.brk("ebr", P_EYE_S, "@erow.OutRow"); g.set("s5", "ContextSlot", inp={"ContextSlot": "@ebr.Type"})
    g.n("gt", "call_self", function="Go To Item", inp={"name": "@entry.row"})
    g.chain("entry", "bi", "s1", "gt"); g.chain("bi:else", "bh", "s2", "gt"); g.chain("bh:else", "bs", "s3", "gt"); g.chain("bs:else", "mrow", "s4", "gt")
    g.chain("mrow:Row Not Found", "erow", "s5", "gt"); g.chain("erow:Row Not Found", "gt")
    return fn("Manage Go To", [param("kind", "name"), param("row", "name")], graph=g)


def f_rename_mod_of_item():
    g = G(); g.n("imd", "call_self", function="Item Mod", inp={"row": "@entry.name"}); g.branch("b", "@imd.found")
    g.n("mr", "call_self", function="Manage Rename", inp={"kind": "mod", "row": "@imd.mod", "cat": "Mods"}); g.chain("entry", "b", "mr")
    return fn("Rename Mod Of Item", [param("name", "name")], graph=g)


def f_rename_group_of_item():
    """The group row sits under Mods for a mod piece, under Vanilla for a vanilla one."""
    g = G(); g.n("fi", "call_self", function="Find Item", inp={"name": "@entry.name"}); g.brk("bi", S_ITEM, "@fi.item")
    g.call("gne", K_MATH, "NotEqual_NameName", inp={"A": "@bi.Group", "B": "None"}); g.branch("b", "@gne.ReturnValue")
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@entry.name"}); g.call("cs", K_MATH, "SelectString", inp={"A": "Mods", "B": "Vanilla", "bPickA": "@imd.found"}); g.call("cn", K_STR, "Conv_StringToName", inp={"InString": "@cs.ReturnValue"})
    g.n("mr", "call_self", function="Manage Rename", inp={"kind": "group", "row": "@bi.Group", "cat": "@cn.ReturnValue"}); g.chain("entry", "fi", "b", "mr")
    return fn("Rename Group Of Item", [param("name", "name")], graph=g)


def f_manage_search_for():
    """'search' link of a Manage row: the display name into the search box + ManageSearchText, then the counts and rows."""
    g = G(); g.set("s", "ManageSearchText", inp={"ManageSearchText": "@entry.s"})
    g.call("t", K_TXT, "Conv_StringToText", inp={"InString": "@entry.s"}); g.get("gp", "Panel"); g.call("ps", W_PANEL, "Set Manage Search", inp={"self": "@gp.Panel", "text": "@t.ReturnValue"})
    g.n("rc", "call_self", function="Rebuild Manage Cats"); g.n("rm", "call_self", function="Rebuild Manage")
    g.chain("entry", "s", "ps", "rc", "rm")
    return fn("Manage Search For", [param("s", "string")], graph=g)


def f_rebuild_manage_links():
    """The x that clears the Manage search box (like the clothes search)."""
    g = G(); g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Manage Search Links", inp={"self": "@gp.Panel"})
    xw = create_widget(g, "cx", W_TXT); set_manager(g, "smx", W_TXT, xw)
    g.call("xt", K_TXT, "Conv_StringToText", inp={"InString": "\u00d7"}); g.call("xi", W_TXT, "Init", inp={"self": xw, "action": "ClearManageSearch", "caption": "@xt.ReturnValue"})
    g.get("gp2", "Panel"); g.call("al", W_PANEL, "Add Manage Search Link", inp={"self": "@gp2.Panel", "widget": xw})
    g.chain("entry", "cl", "cx_cr", "smx", "xi", "al")
    return fn("Rebuild Manage Links", graph=g)


def f_poll_manage():
    """Tick on the Manage page: "only mods" / "case-sensitive" checkboxes -> settings + rebuild."""
    g = G(); g.get("gp", "Panel"); g.call("om", W_PANEL, "Get Only Mods", inp={"self": "@gp.Panel"}); g.get("gc", "OnlyModsNames")
    g.call("ne", K_MATH, "NotEqual_BoolBool", inp={"A": "@om.yes", "B": "@gc.OnlyModsNames"})
    g.get("gp2", "Panel"); g.call("cs", W_PANEL, "Get Case Sens", inp={"self": "@gp2.Panel"}); g.get("gcs", "CaseSensitiveNames")
    g.call("ne2", K_MATH, "NotEqual_BoolBool", inp={"A": "@cs.yes", "B": "@gcs.CaseSensitiveNames"})
    g.call("any", K_MATH, "BooleanOR", inp={"A": "@ne.ReturnValue", "B": "@ne2.ReturnValue"}); g.branch("b", "@any.ReturnValue")
    g.set("s", "OnlyModsNames", inp={"OnlyModsNames": "@om.yes"}); g.set("s2", "CaseSensitiveNames", inp={"CaseSensitiveNames": "@cs.yes"})
    g.n("sv", "call_self", function="Save Settings"); g.n("rc", "call_self", function="Rebuild Manage Cats"); g.n("rm", "call_self", function="Rebuild Manage")
    g.chain("entry", "b", "s", "s2", "sv", "rc", "rm"); return fn("Poll Manage", graph=g)


# ---------------- context menu: "Only this group", "View mod content"; mod content view ----------------
def f_show_only_group():
    """Group chip of the piece + the All slot; search cleared and a filter that would hide the piece switched off (like Go To Item)."""
    g = G()
    g.n("fi", "call_self", function="Find Item", inp={"name": "@entry.name"}); g.brk("bi", S_ITEM, "@fi.item")
    g.get("gp", "Panel"); g.call("pcs", W_PANEL, "Clear Search", inp={"self": "@gp.Panel"}); g.set("sst", "SearchText", inp={"SearchText": ""})
    g.n("io", "call_self", function="Is Owned", inp={"name": "@entry.name"}); g.get("gco", "CachedOnlyOwned"); g.call("no", K_MATH, "BooleanAND", inp={"A": "@gco.CachedOnlyOwned", "B": "@io.yes"})
    g.n("ifv", "call_self", function="Is Favorite", inp={"name": "@entry.name"}); g.get("gcf", "CachedOnlyFav"); g.call("nf", K_MATH, "BooleanAND", inp={"A": "@gcf.CachedOnlyFav", "B": "@ifv.yes"})
    g.get("gcv", "CachedOnlyVanilla"); g.call("nv", K_MATH, "BooleanAND", inp={"A": "@gcv.CachedOnlyVanilla", "B": "@bi.IsVanilla"})
    g.set("sco", "CachedOnlyOwned", inp={"CachedOnlyOwned": "@no.ReturnValue"}); g.set("scf", "CachedOnlyFav", inp={"CachedOnlyFav": "@nf.ReturnValue"}); g.set("scv", "CachedOnlyVanilla", inp={"CachedOnlyVanilla": "@nv.ReturnValue"})
    g.get("gp2", "Panel"); g.get("gco2", "CachedOnlyOwned"); g.get("gcf2", "CachedOnlyFav"); g.get("gcv2", "CachedOnlyVanilla")
    g.call("sft", W_PANEL, "Set Filter Toggles", inp={"self": "@gp2.Panel", "owned": "@gco2.CachedOnlyOwned", "fav": "@gcf2.CachedOnlyFav", "vanilla": "@gcv2.CachedOnlyVanilla"})
    g.n("alg", "call_self", function="Group Alias", inp={"group": "@bi.Group"})   # MergeGroups: the chip of the merged group
    g.set("scs", "CurrentSlot", inp={"CurrentSlot": "All"}); g.set("sg", "CurrentGroup", inp={"CurrentGroup": "@alg.alias"})
    g.n("rl", "call_self", function="Rebuild Left"); g.n("rt", "call_self", function="Rebuild SubTabs"); g.n("rli", "call_self", function="Rebuild List"); g.n("sv", "call_self", function="Save Settings")
    g.chain("entry", "fi", "pcs", "sst", "sco", "scf", "scv", "sft", "scs", "sg", "rl", "rt", "rli", "sv")
    return fn("Show Only Group", [param("name", "name")], graph=g)


def f_open_mod_content_of_item():
    g = G(); g.n("imd", "call_self", function="Item Mod", inp={"row": "@entry.name"}); g.branch("b", "@imd.found")
    g.n("op", "call_self", function="Open Mod Content", inp={"mod": "@imd.mod"}); g.chain("entry", "b", "op")
    return fn("Open Mod Content Of Item", [param("name", "name")], graph=g)


def f_open_mod_content():
    """Content view of a mod: everything it adds (clothes per slot, hairstyles, skins, make-up). ContentFrom remembers the page to return to."""
    g = G()
    g.get("gpg", "Page"); g.set("sf", "ContentFrom", inp={"ContentFrom": "@gpg.Page"}); g.set("sv", "ViewMod", inp={"ViewMod": "@entry.mod"})
    g.n("mcp", "call_self", function="Mod Caption", inp={"mod": "@entry.mod"}); g.n("ti", "call_self", function="T", inp={"key": "Tip_Pak"}); g.call("si", K_TXT, "Conv_TextToString", inp={"InText": "@ti.text"})
    g.call("ms", K_STR, "Conv_NameToString", inp={"InName": "@entry.mod"})
    g.call("t1", K_STR, "Concat_StrStr", inp={"A": "@mcp.s", "B": "\n"}); g.call("t2", K_STR, "Concat_StrStr", inp={"A": "@t1.ReturnValue", "B": "@si.ReturnValue"}); g.call("t3", K_STR, "Concat_StrStr", inp={"A": "@t2.ReturnValue", "B": "@ms.ReturnValue"})
    g.set("st", "ViewTitle", inp={"ViewTitle": "@t3.ReturnValue"})
    g.get("gpg2", "Page"); g.n("sp", "call_self", function="Select Page", inp={"name": "@gpg2.Page"})
    g.chain("entry", "sf", "sv", "st", "sp")
    return fn("Open Mod Content", [param("mod", "name")], graph=g)


def mod_section_tiles(g, id, caption_pin, prev):
    """Section that is created on the first tile (TmpFound): returns the exec id after which the tile chain continues."""
    g.get(id + "_gf", "TmpFound"); g.branch(id + "_bf", "@%s_gf.TmpFound" % id)
    sec = content_section(g, id + "_s", caption_pin); g.set(id + "_sf", "TmpFound", inp={"TmpFound": "true"})
    g.chain(prev, id + "_bf"); g.chain(id + "_bf:else", *sec, id + "_sf")
    return [id + "_bf", id + "_sf"]   # both continue with the tile


def f_rebuild_mod_content():
    """Mod content view: back link + title, then Clothes per slot (catalog items whose Item Mod is ViewMod), Hairstyles, Skins, one section per make-up type."""
    g = G()
    g.get("gp0", "Panel"); g.call("clc", W_PANEL, "Clear Content", inp={"self": "@gp0.Panel"}); g.get("gp1", "Panel"); g.call("cll", W_PANEL, "Clear Content Links", inp={"self": "@gp1.Panel"})
    lw = create_widget(g, "clk", W_TXT); set_manager(g, "sml", W_TXT, lw)
    g.call("li", W_TXT, "Init", inp={"self": lw, "action": "ContentBack", "caption": tt(g, "lt", "Btn_Back")})
    g.get("gp2", "Panel"); g.call("al", W_PANEL, "Add Content Link", inp={"self": "@gp2.Panel", "widget": lw})
    g.get("gvt", "ViewTitle"); g.call("tt1", K_TXT, "Conv_StringToText", inp={"InString": "@gvt.ViewTitle"}); g.get("gp3", "Panel"); g.call("sct", W_PANEL, "Set Content Title", inp={"self": "@gp3.Panel", "text": "@tt1.ReturnValue"})
    g.get("gvm", "ViewMod")
    # --- clothes: one section per slot with pieces of this mod
    g.get("gsl", "Slots"); g.foreach("fs", "@gsl.Slots"); g.set("f0", "TmpFound", inp={"TmpFound": "false"})
    g.call("sn", K_STR, "Conv_NameToString", inp={"InName": "@fs.Array Element"}); g.call("sk", K_STR, "Concat_StrStr", inp={"A": "Slot_", "B": "@sn.ReturnValue"}); g.call("skn", K_STR, "Conv_StringToName", inp={"InString": "@sk.ReturnValue"})
    g.n("tsl", "call_self", function="T", inp={"key": "@skn.ReturnValue"})
    g.get("gai", "AllItems"); g.foreach("fi", "@gai.AllItems"); g.brk("bi", S_ITEM, "@fi.Array Element")
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@bi.Name"}); g.call("mEq", K_MATH, "EqualEqual_NameName", inp={"A": "@imd.mod", "B": "@gvm.ViewMod"})
    g.call("sEq", K_MATH, "EqualEqual_NameName", inp={"A": "@bi.Slot", "B": "@fs.Array Element"}); g.call("iok", K_MATH, "BooleanAND", inp={"A": "@mEq.ReturnValue", "B": "@sEq.ReturnValue"}); g.branch("biok", "@iok.ReturnValue")
    s1 = mod_section_tiles(g, "c", "@tsl.text", "biok")
    g.set("sti", "TmpItem", inp={"TmpItem": "@fi.Array Element"}); g.get("gti", "TmpItem")
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@bi.Name"}); g.n("io", "call_self", function="Shown Owned", inp={"name": "@bi.Name"})
    g.n("ifv", "call_self", function="Is Favorite", inp={"name": "@bi.Name"}); g.n("idm", "call_self", function="Is Damaged", inp={"name": "@bi.Name"}); g.n("tip", "call_self", function="Item Tip", inp={"item": "@gti.TmpItem", "kind": "item", "category": ""})
    t1, w1 = content_tile(g, "t1", "@gti.TmpItem", "@iw.yes", "@io.yes", "@ifv.yes", "@idm.yes", "@tip.tip")
    g.chain("entry", "clc", "cll", "clk_cr", "sml", "li", "al", "sct", "fs"); g.chain("fs", "f0", "fi"); g.chain("fi", "biok")
    for x in s1: g.chain(x, "sti", "idm", "tip", *t1)
    # --- hairstyles
    g.set("f1", "TmpFound", inp={"TmpFound": "false"}); g.call("hrn", K_DT, "GetDataTableRowNames", inp={"Table": P_HAIR_T}); g.foreach("fh", "@hrn.OutRowNames")
    g.n("himd", "call_self", function="Item Mod", inp={"row": "@fh.Array Element"}); g.call("hEq", K_MATH, "EqualEqual_NameName", inp={"A": "@himd.mod", "B": "@gvm.ViewMod"}); g.call("hok", K_MATH, "BooleanAND", inp={"A": "@himd.found", "B": "@hEq.ReturnValue"}); g.branch("bh", "@hok.ReturnValue")
    s2 = mod_section_tiles(g, "h", tt(g, "s2t", "Tab_Hair"), "bh")
    g.n("hrow", "get_row", table=P_HAIR_T, inp={"RowName": "@fh.Array Element"}, miss="ignore"); g.brk("hbr", P_HAIR_S, "@hrow.OutRow")
    g.set("shi", "TmpItem", inp={"TmpItem": make_item(g, "mhi", "@fh.Array Element", "@hbr.icon", slot="Hair", kind="hair")})
    g.get("gpl", "Player"); g.call("cur", P_JODI, "Get Hairstyle Name", inp={"self": "@gpl.Player"}); g.call("hsel", K_MATH, "EqualEqual_NameName", inp={"A": "@cur.name", "B": "@fh.Array Element"})
    howned = hair_owned(g, "hown", "@fh.Array Element", "@hbr.MirrorID")
    g.get("gti2", "TmpItem"); t2, w2 = content_tile(g, "t2", "@gti2.TmpItem", "@hsel.ReturnValue", howned, "false", "false", tt(g, "t2t", "Tab_Hair"), kind="hair")
    g.chain("fs:Completed", "f1", "hrn", "fh"); g.chain("fh", "bh")
    for x in s2: g.chain(x, "hrow", "shi", *t2)
    # --- skins
    g.set("f2", "TmpFound", inp={"TmpFound": "false"}); g.call("srn", K_DT, "GetDataTableRowNames", inp={"Table": P_SKIN_T}); g.foreach("fk", "@srn.OutRowNames")
    g.n("kimd", "call_self", function="Item Mod", inp={"row": "@fk.Array Element"}); g.call("kEq", K_MATH, "EqualEqual_NameName", inp={"A": "@kimd.mod", "B": "@gvm.ViewMod"}); g.call("kok", K_MATH, "BooleanAND", inp={"A": "@kimd.found", "B": "@kEq.ReturnValue"}); g.branch("bk", "@kok.ReturnValue")
    s3 = mod_section_tiles(g, "k", tt(g, "s3t", "Look_Skin"), "bk")
    g.n("srow", "get_row", table=P_SKIN_T, inp={"RowName": "@fk.Array Element"}, miss="ignore"); g.brk("sbr", P_SKIN_S, "@srow.OutRow")
    g.set("ssi", "TmpItem", inp={"TmpItem": make_item(g, "msi", "@fk.Array Element", "@sbr.icon", slot="Skin", kind="skin")})
    g.n("ssel", "call_self", function="Is Look Selected", inp={"type": "Skin", "style": "@fk.Array Element"})
    g.get("gti3", "TmpItem"); t3, w3 = content_tile(g, "t3", "@gti3.TmpItem", "@ssel.yes", "true", "false", "false", tt(g, "t3t", "Look_Skin"), kind="skin")
    g.chain("fh:Completed", "f2", "srn", "fk"); g.chain("fk", "bk")
    for x in s3: g.chain(x, "srow", "ssi", "ssel", *t3)
    # --- make-up: per type (MakeupTypeTable rows) the rows of MakeupTable / EyeTable with that type
    g.call("trn", K_DT, "GetDataTableRowNames", inp={"Table": P_MTYPE_T}); g.foreach("ft", "@trn.OutRowNames"); g.set("f3", "TmpFound", inp={"TmpFound": "false"})
    g.n("mcap", "call_self", function="Look Caption", inp={"type": "@ft.Array Element"})   # caption pin stays valid for the rows (TmpText would be clobbered by Item Tip -> Group Caption)
    def makeup_rows(id, table, struct, prev):
        g.call(id + "_rn", K_DT, "GetDataTableRowNames", inp={"Table": table}); g.foreach(id + "_fe", "@%s_rn.OutRowNames" % id)
        g.n(id + "_row", "get_row", table=table, inp={"RowName": "@%s_fe.Array Element" % id}, miss="ignore"); g.brk(id + "_br", struct, "@%s_row.OutRow" % id)
        g.n(id + "_imd", "call_self", function="Item Mod", inp={"row": "@%s_fe.Array Element" % id})
        g.call(id + "_mEq", K_MATH, "EqualEqual_NameName", inp={"A": "@%s_imd.mod" % id, "B": "@gvm.ViewMod"}); g.call(id + "_tEq", K_MATH, "EqualEqual_NameName", inp={"A": "@%s_br.Type" % id, "B": "@ft.Array Element"})
        g.call(id + "_a1", K_MATH, "BooleanAND", inp={"A": "@%s_imd.found" % id, "B": "@%s_mEq.ReturnValue" % id}); g.call(id + "_ok", K_MATH, "BooleanAND", inp={"A": "@%s_a1.ReturnValue" % id, "B": "@%s_tEq.ReturnValue" % id}); g.branch(id + "_b", "@%s_ok.ReturnValue" % id)
        sec = mod_section_tiles(g, id + "_x", "@mcap.caption", id + "_b")
        g.set(id + "_si", "TmpItem", inp={"TmpItem": make_item(g, id + "_mi", "@%s_fe.Array Element" % id, "@%s_br.Icon" % id, slot="@ft.Array Element", kind="makeup")})
        g.n(id + "_sel", "call_self", function="Is Look Selected", inp={"type": "@ft.Array Element", "style": "@%s_fe.Array Element" % id})
        g.get(id + "_gti", "TmpItem"); tl, _ = content_tile(g, id + "_t", "@%s_gti.TmpItem" % id, "@%s_sel.yes" % id, "true", "false", "false", "@mcap.caption", kind="makeup")
        g.chain(prev, id + "_rn", id + "_fe"); g.chain(id + "_fe", id + "_row", id + "_b")
        for x in sec: g.chain(x, id + "_si", id + "_sel", *tl)
        return id + "_fe:Completed"
    g.chain("fk:Completed", "trn", "ft"); g.chain("ft", "f3", "mcap")
    makeup_rows("e", P_EYE_T, P_EYE_S, makeup_rows("m", P_MAKEUP_T, P_MAKEUP_S, "mcap"))
    return fn("Rebuild Mod Content", graph=g)


# ---------------- natural hair colours: swatch row under the Coiffure links ----------------
def lin_color(rgb):
    return "(R=%s,G=%s,B=%s,A=1)" % rgb


def f_swatch_color():
    """found/color of a hair colour preset key (assets/gen/hair_colors.py)."""
    g = G(); g.set("f0", "TmpFound", inp={"TmpFound": "false"}); tail = ["entry", "f0"]
    for i, (key, rgb, _) in enumerate(hc.COLORS):
        g.call("is%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@entry.key", "B": key}); g.branch("b%d" % i, "@is%d.ReturnValue" % i)
        g.set("sc%d" % i, "TmpColor", inp={"TmpColor": lin_color(rgb)}); g.set("sf%d" % i, "TmpFound", inp={"TmpFound": "true"})
        g.chain(*tail, "b%d" % i, "sc%d" % i, "sf%d" % i, "return"); tail = ["b%d:else" % i]
    g.chain(*tail, "return")
    g.get("gc", "TmpColor"); g.get("gf", "TmpFound"); g.link("gc.TmpColor", "return.color"); g.link("gf.TmpFound", "return.found")
    return fn("Swatch Color", [param("key", "name")], [param("found", "bool"), param("color", S_LINCOLOR)], graph=g)


def f_rebuild_hair_swatches():
    """One W_HairSwatch per preset; the one equal to the current hair colour is framed; the row is visible iff HairSwatchesOpen."""
    g = G()
    g.get("gp0", "Panel"); g.call("pv", K_SYS, "IsValid", inp={"Object": "@gp0.Panel"}); g.branch("bpv", "@pv.ReturnValue")
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Hair Swatches", inp={"self": "@gp.Panel"})
    g.get("gpl", "Player"); g.call("gc", P_JODI, "Get Hairstyle Color", inp={"self": "@gpl.Player"}); g.set("scc", "TmpColor", inp={"TmpColor": "@gc.color"})
    tail = ["entry", "bpv", "cl", "scc"]
    for i, (key, rgb, _) in enumerate(hc.COLORS):
        sw = create_widget(g, "sw%d" % i, W_HSWATCH); set_manager(g, "sm%d" % i, W_HSWATCH, sw)
        g.get("gcc%d" % i, "TmpColor"); g.call("eq%d" % i, K_MATH, "EqualEqual_LinearColorLinearColor", inp={"A": "@gcc%d.TmpColor" % i, "B": lin_color(rgb)})
        g.call("si%d" % i, W_HSWATCH, "Init", inp={"self": sw, "key": key, "color": lin_color(rgb), "tip": tt(g, "st%d" % i, "Hair_" + key), "selected": "@eq%d.ReturnValue" % i})
        g.get("gpa%d" % i, "Panel"); g.call("ad%d" % i, W_PANEL, "Add Hair Swatch", inp={"self": "@gpa%d.Panel" % i, "widget": sw})
        tail += ["sw%d_cr" % i, "sm%d" % i, "si%d" % i, "ad%d" % i]
    g.get("go", "HairSwatchesOpen"); g.get("gpv", "Panel"); g.call("vis", W_PANEL, "Set Hair Swatches Visible", inp={"self": "@gpv.Panel", "visible": "@go.HairSwatchesOpen"}); tail.append("vis")
    g.chain(*tail)
    return fn("Rebuild Hair Swatches", graph=g)


def f_hair_swatch_clicked():
    """Apply a preset like the palette's "apply": Change Hairstyle Color + GameInstance.Save Hair Color Data; then re-frame the swatches."""
    g = G(); g.n("sc", "call_self", function="Swatch Color", inp={"key": "@entry.key"}); g.branch("b", "@sc.found")
    g.get("gpl", "Player"); g.call("chc", P_JODI, "Change Hairstyle Color", inp={"self": "@gpl.Player", "color": "@sc.color"})
    gi = game_instance(g, "gi"); g.get("gpl2", "Player"); g.call("svh", P_GI, "Save Hair Color Data", inp={"self": gi, "player": "@gpl2.Player"})
    g.n("rb", "call_self", function="Rebuild Hair Swatches")
    g.chain("entry", "sc", "b", "chc", "svh", "rb")
    return fn("Hair Swatch Clicked", [param("key", "name")], graph=g)


def f_toggle_hair_swatches():
    g = G(); g.get("go", "HairSwatchesOpen"); g.call("nt", K_MATH, "Not_PreBool", inp={"A": "@go.HairSwatchesOpen"}); g.set("so", "HairSwatchesOpen", inp={"HairSwatchesOpen": "@nt.ReturnValue"})
    g.n("sv", "call_self", function="Save Settings"); g.n("rb", "call_self", function="Rebuild Hair Swatches"); g.chain("entry", "so", "sv", "rb")
    return fn("Toggle Hair Swatches", graph=g)


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
    g.call("isc", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Clothes"}); g.branch("bc", "@isc.ReturnValue"); g.n("rcd", "call_self", function="Rebuild Catalog If Dirty")
    g.call("ish", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Hair"}); g.branch("bh", "@ish.ReturnValue"); g.n("rh", "call_self", function="Rebuild Hair")
    g.call("isl", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Look"}); g.branch("bl", "@isl.ReturnValue")
    g.n("rlc", "call_self", function="Rebuild Look Cats"); g.n("rlk", "call_self", function="Rebuild Look"); g.n("rll", "call_self", function="Rebuild Look Links"); g.n("rlch", "call_self", function="Rebuild Look Chips")
    g.n("rcdl", "call_self", function="Rebuild Catalog If Dirty")   # a renamed mod changes the mod aliases (MergeMods) - the catalog rebuild refreshes them
    g.call("isy", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Body"}); g.branch("by", "@isy.ReturnValue"); g.n("rby", "call_self", function="Rebuild Body")
    g.call("iso2", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Options"}); g.branch("bop", "@iso2.ReturnValue"); g.n("rop", "call_self", function="Rebuild Options")
    g.call("isM", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Manage"}); g.branch("bM", "@isM.ReturnValue")
    g.get("gpm", "Panel"); g.get("gom", "OnlyModsNames"); g.call("som", W_PANEL, "Set Only Mods", inp={"self": "@gpm.Panel", "on": "@gom.OnlyModsNames"})
    g.get("gpcs", "Panel"); g.get("gcsn", "CaseSensitiveNames"); g.call("scs", W_PANEL, "Set Case Sens", inp={"self": "@gpcs.Panel", "on": "@gcsn.CaseSensitiveNames"})
    g.n("rmc", "call_self", function="Rebuild Manage Cats"); g.n("rml", "call_self", function="Rebuild Manage Links"); g.n("rmr", "call_self", function="Rebuild Manage")
    g.n("cmn", "call_self", function="Close Menu")   # a context menu of the previous page would stay open otherwise
    g.chain("entry", "bkh", "skh", "cmn"); g.chain("bkh:else", "shl", "cmn")
    g.get("gpg0", "Page"); g.call("pne", K_MATH, "NotEqual_NameName", inp={"A": "@gpg0.Page", "B": "@entry.name"}); g.branch("bpn", "@pne.ReturnValue")
    g.set("svm0", "ViewMod", inp={"ViewMod": "None"})   # the mod content view is not tied to a tab: another tab closes it (outfit / look / preset views belong to their tab)
    g.chain("cmn", "bpn", "svm0", "sp"); g.chain("bpn:else", "sp"); g.chain("sp", "spg", "rtt", "uf", "co", "bco", "spc", "rcn")
    g.chain("bco:else", "bo", "ro"); g.chain("bo:else", "blk", "rlk2"); g.chain("blk:else", "bb", "rb"); g.chain("bb:else", "bc", "rcd", "rl", "rt", "rli")
    g.chain("bc:else", "bh", "rh"); g.chain("bh:else", "bl", "rcdl", "rll", "rlch", "rlc", "rlk"); g.chain("bl:else", "by", "rby"); g.chain("by:else", "bop", "rop"); g.chain("bop:else", "bM", "som", "scs", "rmc", "rml", "rmr")
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
    """Wear a vanilla outfit (preset): current state as snapshot, its clothes and colours replaced by the outfit's -> Apply Snapshot
    (one piece per tick, see there). The Looks page reuses the click for 'Save current appearance' (index < 0 = the + tile)."""
    g = G()
    g.get("gpg", "Page"); g.call("isl", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Look"}); g.branch("bpl", "@isl.ReturnValue"); g.n("pa", "call_self", function="Preset Add")
    g.call("neg", K_MATH, "Less_IntInt", inp={"A": "@entry.index", "B": "0"}); g.branch("b", "@neg.ReturnValue")
    g.get("go", "Outfits"); g.get("gpl", "Player"); g.call("ap", P_OUTFITS, "Add Preset", inp={"self": "@go.Outfits", "player": "@gpl.Player"})
    g.n("ph", "call_self", function="Push History"); g.n("ts", "call_self", function="Take Snapshot"); g.brk("bs", S_SNAP, "@ts.snap")
    g.get("go2", "Outfits"); g.get("goa", "outfits", cls=P_OUTFITS); g.link("go2.Outfits", "goa.self")
    g.call("og", K_ARR, "Array_Get", inp={"TargetArray": "@goa.outfits", "Index": "@entry.index"}); g.brk("obr", P_OUTFIT_S, "@og.Item")
    g.call("keys", K_MAP, "Map_Keys", inp={"TargetMap": "@obr." + OUTFIT_MEMBER})
    g.get("gtc", "TmpColors"); g.call("mclr", K_MAP, "Map_Clear", inp={"TargetMap": "@gtc.TmpColors"})
    g.foreach("fk", "@keys.Keys"); g.call("cf", K_MAP, "Map_Find", inp={"TargetMap": "@obr." + OUTFIT_MEMBER, "Key": "@fk.Array Element"})
    g.call("c2l", K_MATH, "Conv_ColorToLinearColor", inp={"InColor": "@cf.Value"})
    g.get("gtc2", "TmpColors"); g.call("madd", K_MAP, "Map_Add", inp={"TargetMap": "@gtc2.TmpColors", "Key": "@fk.Array Element", "Value": "@c2l.ReturnValue"})
    g.get("gtc3", "TmpColors")
    g.make("mk", S_SNAP, Worn="@keys.Keys", Makeup="@bs.Makeup", Skin="@bs.Skin", Hair="@bs.Hair", Colors="@gtc3.TmpColors", HairColor="@bs.HairColor",
           Boobs="@bs.Boobs", Waist="@bs.Waist", Hip="@bs.Hip", Body="@bs.Body", Scales="@bs.Scales")
    g.n("as", "call_self", function="Apply Snapshot", inp={"snap": "@mk.S_Snapshot"})
    g.n("sv", "call_self", function="Save Outfits"); g.n("ro", "call_self", function="Rebuild Outfits")
    g.chain("entry", "bpl", "pa"); g.chain("bpl:else", "b", "ap", "sv", "ro"); g.chain("b:else", "ph", "ts", "keys", "mclr", "fk"); g.chain("fk", "madd"); g.chain("fk:Completed", "as", "ro")
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


def f_can_wear():
    """A piece may be put on: owned, in the backpack, or option "not owned items" = greyed / like owned (UnownedMode > 0)."""
    g = G()
    g.n("io", "call_self", function="Is Owned", inp={"name": "@entry.name"}); g.n("ib", "call_self", function="In Bag", inp={"name": "@entry.name"})
    g.get("gm", "UnownedMode"); g.call("m0", K_MATH, "Greater_IntInt", inp={"A": "@gm.UnownedMode", "B": "0"})
    g.call("o1", K_MATH, "BooleanOR", inp={"A": "@io.yes", "B": "@ib.yes"}); g.call("o2", K_MATH, "BooleanOR", inp={"A": "@o1.ReturnValue", "B": "@m0.ReturnValue"}); g.link("o2.ReturnValue", "return.yes")
    g.chain("entry", "ib", "return"); return fn("Can Wear", [param("name", "name")], [param("yes", "bool")], graph=g)


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
    g.get("gpw0", "Panel"); g.call("cwl", W_PANEL, "Clear Bag Worn Links", inp={"self": "@gpw0.Panel"})
    aw_ = create_widget(g, "cla", W_TXT); set_manager(g, "smla", W_TXT, aw_)
    g.call("lia", W_TXT, "Init", inp={"self": aw_, "action": "BagAllWorn", "caption": tt(g, "lta", "Btn_BagAll")})
    g.get("gpw1", "Panel"); g.call("awl", W_PANEL, "Add Bag Worn Link", inp={"self": "@gpw1.Panel", "widget": aw_})
    g.set("nf", "TmpIdx", inp={"TmpIdx": "0"})
    # worn
    g.get("gw", "Worn"); g.foreach("fw", "@gw.Worn")
    g.n("fi", "call_self", function="Find Item", inp={"name": "@fw.Array Element"}); g.branch("bf", "@fi.found")
    ww = create_widget(g, "cw1", W_BTN); set_manager(g, "smw", W_BTN, ww)
    g.n("io", "call_self", function="Shown Owned", inp={"name": "@fw.Array Element"}); g.n("ifv", "call_self", function="Is Favorite", inp={"name": "@fw.Array Element"})
    g.n("dm", "call_self", function="Is Damaged", inp={"name": "@fw.Array Element"})
    g.n("wti", "call_self", function="Item Tip", inp={"item": "@fi.item", "kind": "item", "category": ""})
    g.call("wi", W_BTN, "Init", inp={"self": ww, "item": "@fi.item", "worn": "true", "owned": "@io.yes", "fav": "@ifv.yes", "damaged": "@dm.yes", "tip": "@wti.tip"})
    g.get("gp3", "Panel"); g.call("aw", W_PANEL, "Add Bag Worn", inp={"self": "@gp3.Panel", "widget": ww})
    # in the backpack (not worn)
    bag = player_bag(g, "gb"); g.get("gcb", "Clothes in bag", cls=P_BAG); g.link("gb.Bag", "gcb.self")
    g.set("sbl", "TmpNames", inp={"TmpNames": "@gcb.Clothes in bag"}); g.get("gtn", "TmpNames"); g.foreach("fb", "@gtn.TmpNames")
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@fb.Array Element"}); g.call("niw", K_MATH, "Not_PreBool", inp={"A": "@iw.yes"}); g.branch("bnw", "@niw.ReturnValue")
    g.n("fi2", "call_self", function="Find Item", inp={"name": "@fb.Array Element"}); g.branch("bf2", "@fi2.found")
    bw = create_widget(g, "cb1", W_BTN); set_manager(g, "smb", W_BTN, bw)
    g.n("io2", "call_self", function="Shown Owned", inp={"name": "@fb.Array Element"}); g.n("ifv2", "call_self", function="Is Favorite", inp={"name": "@fb.Array Element"})
    g.n("dm2", "call_self", function="Is Damaged", inp={"name": "@fb.Array Element"})
    g.n("bti2", "call_self", function="Item Tip", inp={"item": "@fi2.item", "kind": "item", "category": ""})
    g.call("bi", W_BTN, "Init", inp={"self": bw, "item": "@fi2.item", "worn": "false", "owned": "@io2.yes", "fav": "@ifv2.yes", "damaged": "@dm2.yes", "tip": "@bti2.tip"})
    g.get("gp4", "Panel"); g.call("ab", W_PANEL, "Add Bag Item", inp={"self": "@gp4.Panel", "widget": bw})
    g.get("gn", "TmpIdx"); g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gn.TmpIdx", "B": "1"}); g.set("sn", "TmpIdx", inp={"TmpIdx": "@inc.ReturnValue"})
    g.get("gn2", "TmpIdx"); g.call("eq0", K_MATH, "EqualEqual_IntInt", inp={"A": "@gn2.TmpIdx", "B": "0"})
    g.get("gp5", "Panel"); g.call("sbe", W_PANEL, "Set Bag Empty", inp={"self": "@gp5.Panel", "visible": "@eq0.ReturnValue"})
    g.chain("entry", "cw", "cl", "cll", "clk_cr", "sml", "li", "al", "cwl", "cla_cr", "smla", "lia", "awl", "nf", "fw"); g.chain("fw", "fi", "bf", "cw1_cr", "smw", "dm", "wti", "wi", "aw")
    g.chain("fw:Completed", "sbl", "fb"); g.chain("fb", "bnw", "fi2", "bf2", "cb1_cr", "smb", "dm2", "bti2", "bi", "ab", "sn")
    g.chain("fb:Completed", "sbe")
    return fn("Rebuild Bag", graph=g)


def after_bag_change(g, first):
    """Save Appearance, Refresh State, Rebuild Bag (chain starting at `first`)."""
    g.n("sa9", "call_self", function="Save Worn")
    g.n("rs9", "call_self", function="Refresh State"); g.n("rb9", "call_self", function="Rebuild Bag")
    g.chain(first, "sa9", "rs9", "rb9")


def f_bag_toggle_wear():
    """Wear: AltUI's Wear first (own conflict check - freed pairs stay on), then the vanilla Use Clothes from Bag: the piece is already
    worn, so its Wear The Clothes only redoes covering/mask (no conflict check) and the vanilla follow-ups (backpack capacity,
    statistics, on clothes wear) still run. Take off: vanilla only."""
    g = G()
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@entry.name"}); g.branch("bw", "@iw.yes")
    g.n("w", "call_self", function="Wear", inp={"name": "@entry.name"})
    g.get("gpl", "Player"); g.call("u", P_JODI, "Use Clothes from Bag", inp={"self": "@gpl.Player", "clothes name": "@entry.name", "is wear": "true"})
    g.get("gpl2", "Player"); g.call("off", P_JODI, "Use Clothes from Bag", inp={"self": "@gpl2.Player", "clothes name": "@entry.name", "is wear": "false"})
    g.n("ph", "call_self", function="Push History"); g.chain("entry", "ph", "bw", "off", "sa9"); g.chain("bw:else", "w", "u"); after_bag_change(g, "u")
    return fn("Bag Toggle Wear", [param("name", "name")], graph=g)


def f_bag_remove():
    g = G()
    # deliberately without the vanilla lock for default underwear (z-fighting under tight outfits)
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@entry.name"}); g.branch("bw", "@iw.yes")
    g.get("gpl", "Player"); g.call("to", P_CPB, "Take off this clothes", inp={"self": "@gpl.Player", "clothes name": "@entry.name"})
    g.get("gpl2", "Player"); g.call("rm", P_CPB, "Remove Clothing From Bag", inp={"self": "@gpl2.Player", "clothing name": "@entry.name"})
    g.n("ph", "call_self", function="Push History"); g.chain("entry", "ph", "bw", "to", "rm"); g.chain("bw:else", "rm"); after_bag_change(g, "rm")
    return fn("Bag Remove", [param("name", "name")], graph=g)


def f_bag_all_worn():
    """Link next to 'Worn': every worn piece is taken off and lands in the backpack - a piece not in the backpack yet is put there first
    (the vanilla notice when the bag is full, that piece stays on), then taken off like 'Take off' in the bag menu (stays in the bag)."""
    g = G(); g.n("ph", "call_self", function="Push History")
    g.get("gw", "Worn"); g.set("sn", "TmpNames", inp={"TmpNames": "@gw.Worn"}); g.get("gn", "TmpNames"); g.foreach("fw", "@gn.TmpNames")
    g.n("ib", "call_self", function="In Bag", inp={"name": "@fw.Array Element"}); g.branch("bib", "@ib.yes")
    bag = player_bag(g, "gb"); g.call("full", P_BAG, "Is Bag Full ?", inp={"self": bag}); g.branch("bfull", "@full.yes")
    pop(g, "pop", tt(g, "t", "Msg_BagFull"))
    g.get("gpl", "Player"); g.call("gc", P_JODI, "Got Clothes", inp={"self": "@gpl.Player", "clothes name": "@fw.Array Element", "wear": "false"})
    g.get("gpl2", "Player"); g.call("off", P_JODI, "Use Clothes from Bag", inp={"self": "@gpl2.Player", "clothes name": "@fw.Array Element", "is wear": "false"})
    g.chain("entry", "ph", "sn", "fw"); g.chain("fw", "ib", "bib", "off"); g.chain("bib:else", "bfull", "pop"); g.chain("bfull:else", "gc", "off")
    after_bag_change(g, "fw:Completed")
    return fn("Bag All Worn", graph=g)


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
def make_item(g, id, name_pin, icon_pin, slot=None, kind="item"):
    """S_ClothesItem for non-clothes (hairstyle/skin/makeup): name, display name via Display Name(kind, row) (custom name, else the row name),
    icon; slot = origin for the content view (Hair / Skin / <type> / Body)."""
    g.n(id + "_n", "call_self", function="Display Name", inp={"kind": kind, "row": name_pin})
    g.make(id, S_ITEM, Name=name_pin, DisplayName="@%s_n.s" % id, Icon=icon_pin, **({"Slot": slot} if slot else {})); return "@%s.S_ClothesItem" % id


def tile_tip(g, id, item_pin, kind, category_pin):
    """Item Tip node for a look tile (hair / skin / makeup / body): the category text becomes the "s:" line; returns (node id, tip pin)."""
    g.n(id + "_tp", "call_self", function="Item Tip", inp={"item": item_pin, "kind": kind, "category": category_pin}); return id + "_tp", "@%s_tp.tip" % id


def look_tile(g, id, item_pin, selected_pin, owned_pin, add_fn, tip_pin, kind=None, fav_pin="false"):
    """Create W_ClothesButton + init + add to the panel; returns the exec chain. tip_pin = tooltip text; with kind (hair / skin / makeup) it is the
    category text and the tooltip comes from Item Tip (presets: no kind, the text itself)."""
    pre = []
    if kind: n, tip_pin = tile_tip(g, id, item_pin, kind, tip_pin); pre = [n]
    tw = create_widget(g, id, W_BTN); set_manager(g, id + "_sm", W_BTN, tw)
    g.call(id + "_i", W_BTN, "Init", inp={"self": tw, "item": item_pin, "worn": selected_pin, "owned": owned_pin, "fav": fav_pin, "damaged": "false", "tip": tip_pin})
    g.get(id + "_gp", "Panel"); g.call(id + "_a", W_PANEL, add_fn, inp={"self": "@%s_gp.Panel" % id, "widget": tw})
    return pre + [id + "_cr", id + "_sm", id + "_i", id + "_a"]


def game_instance(g, id):
    g.call(id + "_gi", K_GS, "GetGameInstance"); g.cast(id, P_GI, "@%s_gi.ReturnValue" % id); return "@%s.AsTKA Game Instance" % id


def hair_owned(g, id, name_pin, mirror_pin, mode_min=2):
    """owned = in the GameInstance's Hairstyles set or MirrorID == -1, or the option "not owned items" reaches mode_min
    (tiles: 2 = like owned; wearing: 1 = greyed but wearable) - the same modes as for clothes."""
    gi = game_instance(g, id + "_g"); g.get(id + "_hs", "Hairstyles Save", cls=P_GI); g.link(id + "_g.AsTKA Game Instance", id + "_hs.self")
    g.get(id + "_set", "Hairstyles", cls=P_HAIR_SAVE); g.link(id + "_hs.Hairstyles Save", id + "_set.self")
    g.call(id + "_c", K_SET, "Set_Contains", inp={"TargetSet": "@%s_set.Hairstyles" % id, "ItemToFind": name_pin})
    g.call(id + "_m", K_MATH, "EqualEqual_IntInt", inp={"A": mirror_pin, "B": "-1"})
    g.call(id + "_o", K_MATH, "BooleanOR", inp={"A": "@%s_c.ReturnValue" % id, "B": "@%s_m.ReturnValue" % id})
    g.get(id + "_um", "UnownedMode"); g.call(id + "_ge", K_MATH, "GreaterEqual_IntInt", inp={"A": "@%s_um.UnownedMode" % id, "B": str(mode_min)})
    g.call(id, K_MATH, "BooleanOR", inp={"A": "@%s_o.ReturnValue" % id, "B": "@%s_ge.ReturnValue" % id}); return "@%s.ReturnValue" % id


def f_rebuild_hair():
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Hair", inp={"self": "@gp.Panel"})
    g.get("gp1", "Panel"); g.call("cll", W_PANEL, "Clear Hair Links", inp={"self": "@gp1.Panel"})
    lw = create_widget(g, "clk", W_TXT); set_manager(g, "sml", W_TXT, lw)
    g.call("li", W_TXT, "Init", inp={"self": lw, "action": "HairColor", "caption": tt(g, "lt", "Btn_HairColor")})
    g.get("gp2", "Panel"); g.call("al", W_PANEL, "Add Hair Link", inp={"self": "@gp2.Panel", "widget": lw})
    lw2 = create_widget(g, "cln", W_TXT); set_manager(g, "smn", W_TXT, lw2)
    g.call("li2", W_TXT, "Init", inp={"self": lw2, "action": "HairNatural", "caption": tt(g, "ltn", "Btn_HairNatural")})
    g.get("gp2n", "Panel"); g.call("aln", W_PANEL, "Add Hair Link", inp={"self": "@gp2n.Panel", "widget": lw2}); g.n("rhs", "call_self", function="Rebuild Hair Swatches")
    g.call("rn", K_DT, "GetDataTableRowNames", inp={"Table": P_HAIR_T}); g.set("sn", "TmpNames2", inp={"TmpNames2": "@rn.OutRowNames"})
    g.get("gpl", "Player"); g.call("cur", P_JODI, "Get Hairstyle Name", inp={"self": "@gpl.Player"}); g.set("scn", "TmpName2", inp={"TmpName2": "@cur.name"})
    g.get("gn", "TmpNames2"); g.foreach("fe", "@gn.TmpNames2")
    g.n("row", "get_row", table=P_HAIR_T, inp={"RowName": "@fe.Array Element"}, miss="ignore"); g.brk("br", P_HAIR_S, "@row.OutRow")   # row names of the same table
    owned = hair_owned(g, "own", "@fe.Array Element", "@br.MirrorID")
    item = make_item(g, "mi", "@fe.Array Element", "@br.icon", kind="hair")
    g.get("gcn", "TmpName2"); g.call("sel", K_MATH, "EqualEqual_NameName", inp={"A": "@fe.Array Element", "B": "@gcn.TmpName2"})
    tile = look_tile(g, "th", item, "@sel.ReturnValue", owned, "Add Hair", tt(g, "thtp", "Tab_Hair"), kind="hair")
    g.get("ghl", "HighlightItem"); g.call("ish", K_MATH, "EqualEqual_NameName", inp={"A": "@fe.Array Element", "B": "@ghl.HighlightItem"}); g.branch("bhl", "@ish.ReturnValue")   # scroll target of a "Show in tab" jump
    g.set("ssw", "ScrollWidget", inp={"ScrollWidget": "@th.AsW_ClothesButton"})
    g.chain("entry", "cl", "cll", "clk_cr", "sml", "li", "al", "cln_cr", "smn", "li2", "aln", "rhs", "rn", "sn", "scn", "fe"); g.chain("fe", "row", *tile, "bhl", "ssw")
    return fn("Rebuild Hair", graph=g)


def f_hair_clicked():
    g = G()
    g.n("row", "get_row", table=P_HAIR_T, inp={"RowName": "@entry.name"}, miss="ignore"); g.brk("br", P_HAIR_S, "@row.OutRow")   # unknown hairstyle -> nothing (no history entry yet)
    owned = hair_owned(g, "own", "@entry.name", "@br.MirrorID", mode_min=1); g.branch("bo", owned)
    pop(g, "pop", tt(g, "t", "Msg_HairLocked"))
    g.get("gpl", "Player"); g.call("ch", P_JODI, "Change Hairstyle", inp={"self": "@gpl.Player", "Hairstyle": "@entry.name"})
    g.n("sa", "call_self", function="Save Worn")
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


def f_look_matches():
    """Appearance page search (LookSearchText, case-insensitive like the clothes search): empty, or contained in the shown name, the row name
    or the piece's mod caption (shown + default). shown = the tile's display name (custom name, else row name / "Preset N")."""
    g = G(); g.get("gst", "LookSearchText"); g.call("em", K_STR, "IsEmpty", inp={"InString": "@gst.LookSearchText"}); g.call("ls", K_STR, "ToLower", inp={"SourceString": "@gst.LookSearchText"})
    g.call("rs", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"})
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@entry.row"}); g.n("mcp", "call_self", function="Mod Caption", inp={"mod": "@imd.mod"})
    g.get("gmc", "ModCaption"); g.call("mdf", K_MAP, "Map_Find", inp={"TargetMap": "@gmc.ModCaption", "Key": "@imd.mod"}); g.call("mds", K_TXT, "Conv_TextToString", inp={"InText": "@mdf.Value"})
    prev = "@em.ReturnValue"
    for i, src in enumerate(["@entry.shown", "@rs.ReturnValue", "@mcp.s", "@mds.ReturnValue"]):
        g.call("lo%d" % i, K_STR, "ToLower", inp={"SourceString": src})
        g.call("hit%d" % i, K_STR, "Contains", inp={"SearchIn": "@lo%d.ReturnValue" % i, "Substring": "@ls.ReturnValue", "bUseCase": "false", "bSearchFromEnd": "false"})
        g.call("or%d" % i, K_MATH, "BooleanOR", inp={"A": prev, "B": "@hit%d.ReturnValue" % i}); prev = "@or%d.ReturnValue" % i
    g.link(prev[1:], "return.yes")
    return fn("Look Matches", [param("kind", "name"), param("row", "name"), param("shown", "string")], [param("yes", "bool")], graph=g, pure=True)


def f_on_look_search_changed():
    """Panel key-up: the appearance search box -> LookSearchText; categories + tiles when it changed (appearance page only)."""
    g = G(); g.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@entry.text"})
    g.get("gst", "LookSearchText"); g.call("neq", K_STR, "NotEqual_StrStr", inp={"A": "@t2s.ReturnValue", "B": "@gst.LookSearchText"}); g.branch("b", "@neq.ReturnValue")
    g.set("s", "LookSearchText", inp={"LookSearchText": "@t2s.ReturnValue"}); g.set("hlc", "HighlightItem", inp={"HighlightItem": "None"})
    g.get("gpg", "Page"); g.call("isl", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Look"}); g.branch("bl", "@isl.ReturnValue")
    g.n("rc", "call_self", function="Rebuild Look Cats"); g.n("rk", "call_self", function="Rebuild Look")
    g.chain("entry", "b", "hlc", "s", "bl", "rc", "rk")
    return fn("On Look Search Changed", [param("text", "text")], graph=g)


def f_rebuild_look_links():
    """The x that clears the appearance search box (like the clothes search)."""
    g = G(); g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Look Search Links", inp={"self": "@gp.Panel"})
    xw = create_widget(g, "cx", W_TXT); set_manager(g, "smx", W_TXT, xw)
    g.call("xt", K_TXT, "Conv_StringToText", inp={"InString": "\u00d7"}); g.call("xi", W_TXT, "Init", inp={"self": xw, "action": "ClearLookSearch", "caption": "@xt.ReturnValue"})
    g.get("gp2", "Panel"); g.call("al", W_PANEL, "Add Look Search Link", inp={"self": "@gp2.Panel", "widget": xw})
    g.chain("entry", "cl", "cx_cr", "smx", "xi", "al")
    return fn("Rebuild Look Links", graph=g)


def f_look_type_of():
    """Category of an appearance row: SkinTable row -> Skin; EyeTable row -> its Type; MakeupTable row -> its Type; else None ("All" tiles)."""
    g = G(); g.set("z", "TmpName", inp={"TmpName": "None"})
    g.n("srow", "get_row", table=P_SKIN_T, inp={"RowName": "@entry.name"}, miss="ignore"); g.set("ss", "TmpName", inp={"TmpName": "Skin"})
    g.n("erow", "get_row", table=P_EYE_T, inp={"RowName": "@entry.name"}, miss="ignore"); g.brk("ber", P_EYE_S, "@erow.OutRow"); g.set("se", "TmpName", inp={"TmpName": "@ber.Type"})
    g.n("mrow", "get_row", table=P_MAKEUP_T, inp={"RowName": "@entry.name"}, miss="ignore"); g.brk("bmr", P_MAKEUP_S, "@mrow.OutRow"); g.set("sm", "TmpName", inp={"TmpName": "@bmr.Type"})
    g.get("gt", "TmpName"); g.link("gt.TmpName", "return.type")
    g.chain("entry", "z", "srow", "ss", "return"); g.chain("srow:Row Not Found", "erow", "se", "return"); g.chain("erow:Row Not Found", "mrow", "sm", "return"); g.chain("mrow:Row Not Found", "return")
    return fn("Look Type Of", [param("name", "name")], [param("type", "name")], graph=g)


def f_look_key():
    """Favourites / hidden key of an appearance row: skin:<row> (SkinTable row) else makeup:<row> (make-up and eyes, like Rename Kind)."""
    g = G(); g.call("cs", K_DT, "DoesDataTableRowExist", inp={"Table": P_SKIN_T, "RowName": "@entry.name"})
    g.call("pf", K_MATH, "SelectString", inp={"A": "skin:", "B": "makeup:", "bPickA": "@cs.ReturnValue"})
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"}); g.call("cc", K_STR, "Concat_StrStr", inp={"A": "@pf.ReturnValue", "B": "@n2s.ReturnValue"})
    g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@cc.ReturnValue"}); g.link("s2n.ReturnValue", "return.key")
    g.chain("entry", "cs", "return")
    return fn("Look Key", [param("name", "name")], [param("key", "name")], graph=g)


def f_is_look_favorite():
    g = G(); g.n("k", "call_self", function="Look Key", inp={"name": "@entry.name"}); g.n("f", "call_self", function="Is Favorite", inp={"name": "@k.key"}); g.link("f.yes", "return.yes")
    g.chain("entry", "k", "return"); return fn("Is Look Favorite", [param("name", "name")], [param("yes", "bool")], graph=g)


def f_is_look_hidden():
    g = G(); g.n("k", "call_self", function="Look Key", inp={"name": "@entry.name"}); g.n("h", "call_self", function="Is Item Hidden", inp={"name": "@k.key"}); g.link("h.yes", "return.yes")
    g.chain("entry", "k", "return"); return fn("Is Look Hidden", [param("name", "name")], [param("yes", "bool")], graph=g)


def f_toggle_look_favorite():
    """Context menu of an appearance tile: favourite on/off (Favorites list, key from Look Key), save, redraw the page."""
    g = G(); g.n("k", "call_self", function="Look Key", inp={"name": "@entry.name"}); g.set("sk", "TmpName2", inp={"TmpName2": "@k.key"})
    g.get("gk", "TmpName2"); g.n("isf", "call_self", function="Is Favorite", inp={"name": "@gk.TmpName2"}); g.branch("b", "@isf.yes")
    g.get("gf", "Favorites"); g.get("gk1", "TmpName2"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gf.Favorites", "Item": "@gk1.TmpName2"})
    g.get("gf2", "Favorites"); g.get("gk2", "TmpName2"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gf2.Favorites", "NewItem": "@gk2.TmpName2"})
    g.n("sv", "call_self", function="Save Settings"); g.n("rc", "call_self", function="Rebuild Look Cats"); g.n("rl", "call_self", function="Rebuild Look")
    g.chain("entry", "k", "sk", "b", "rm", "sv"); g.chain("b:else", "add", "sv"); g.chain("sv", "rc", "rl")
    return fn("Toggle Look Favorite", [param("name", "name")], graph=g)


def f_toggle_look_hidden():
    """Context menu of an appearance tile: hide/unhide (HiddenItems, key from Look Key), save; chip "Hidden" without a hidden row left -> All."""
    g = G(); g.n("k", "call_self", function="Look Key", inp={"name": "@entry.name"}); g.set("sk", "TmpName2", inp={"TmpName2": "@k.key"})
    g.get("gk", "TmpName2"); g.n("ish", "call_self", function="Is Item Hidden", inp={"name": "@gk.TmpName2"}); g.branch("b", "@ish.yes")
    g.get("gh", "HiddenItems"); g.get("gk1", "TmpName2"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gh.HiddenItems", "Item": "@gk1.TmpName2"})
    g.get("gh2", "HiddenItems"); g.get("gk2", "TmpName2"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gh2.HiddenItems", "NewItem": "@gk2.TmpName2"})
    g.n("sv", "call_self", function="Save Settings")
    g.get("glc", "LookCat"); g.n("col", "call_self", function="Collect Look Rows", inp={"type": "@glc.LookCat"}); g.n("lg", "call_self", function="Look Groups")
    g.call("hasH", K_ARR, "Array_Contains", inp={"TargetArray": "@lg.groups", "ItemToFind": g.lit_name("hn", "Hidden")})
    g.get("gg", "LookGroup"); g.call("onH", K_MATH, "EqualEqual_NameName", inp={"A": "@gg.LookGroup", "B": "Hidden"}); g.call("nh", K_MATH, "Not_PreBool", inp={"A": "@hasH.ReturnValue"})
    g.call("back", K_MATH, "BooleanAND", inp={"A": "@onH.ReturnValue", "B": "@nh.ReturnValue"}); g.branch("bb", "@back.ReturnValue"); g.set("sg", "LookGroup", inp={"LookGroup": "None"})
    g.n("rch", "call_self", function="Rebuild Look Chips"); g.n("rc", "call_self", function="Rebuild Look Cats"); g.n("rl", "call_self", function="Rebuild Look")
    g.chain("entry", "k", "sk", "b", "rm", "sv"); g.chain("b:else", "add", "sv"); g.chain("sv", "col", "lg", "bb", "sg", "rch"); g.chain("bb:else", "rch"); g.chain("rch", "rc", "rl")
    return fn("Toggle Look Hidden", [param("name", "name")], graph=g)


def f_collect_look_rows():
    """LookRowKinds / LookRows = the rows of an appearance category in page order: skins (kind skin), MakeupTable rows, EyeTable rows (kind makeup);
    All = every row of every table; presets: empty (own path)."""
    g = G()
    g.get("gk0", "LookRowKinds"); g.call("ck", K_ARR, "Array_Clear", inp={"TargetArray": "@gk0.LookRowKinds"}); g.get("gr0", "LookRows"); g.call("cr", K_ARR, "Array_Clear", inp={"TargetArray": "@gr0.LookRows"})
    g.call("isa", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.type", "B": "All"}); g.call("iss", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.type", "B": "Skin"})
    g.call("sk", K_MATH, "BooleanOR", inp={"A": "@iss.ReturnValue", "B": "@isa.ReturnValue"}); g.branch("bs", "@sk.ReturnValue"); g.branch("ba", "@isa.ReturnValue"); g.branch("ba3", "@isa.ReturnValue")
    def adder(p, kind, row_pin):
        g.get(p + "gk", "LookRowKinds"); g.call(p + "ak", K_ARR, "Array_Add", inp={"TargetArray": "@%sgk.LookRowKinds" % p, "NewItem": g.lit_name(p + "kn", kind)})
        g.get(p + "gr", "LookRows"); g.call(p + "ar", K_ARR, "Array_Add", inp={"TargetArray": "@%sgr.LookRows" % p, "NewItem": row_pin}); return [p + "ak", p + "ar"]
    g.call("rs", K_DT, "GetDataTableRowNames", inp={"Table": P_SKIN_T}); g.set("sns", "TmpNames2", inp={"TmpNames2": "@rs.OutRowNames"}); g.get("gns", "TmpNames2"); g.foreach("fs", "@gns.TmpNames2")
    a1 = adder("s", "skin", "@fs.Array Element")
    g.n("trow", "get_row", table=P_MTYPE_T, inp={"RowName": "@entry.type"}, miss="ignore"); g.brk("bt", P_MTYPE_S, "@trow.OutRow"); g.branch("be", "@bt.EyeTable")
    g.call("rm", K_DT, "GetDataTableRowNames", inp={"Table": P_MAKEUP_T}); g.set("snm", "TmpNames2", inp={"TmpNames2": "@rm.OutRowNames"}); g.get("gnm", "TmpNames2"); g.foreach("fm", "@gnm.TmpNames2")
    g.n("mrow", "get_row", table=P_MAKEUP_T, inp={"RowName": "@fm.Array Element"}, miss="ignore"); g.brk("bmr", P_MAKEUP_S, "@mrow.OutRow")
    g.call("eqm", K_MATH, "EqualEqual_NameName", inp={"A": "@bmr.Type", "B": "@entry.type"}); g.call("okm", K_MATH, "BooleanOR", inp={"A": "@eqm.ReturnValue", "B": "@isa.ReturnValue"}); g.branch("bqm", "@okm.ReturnValue")
    a2 = adder("m", "makeup", "@fm.Array Element")
    g.call("re", K_DT, "GetDataTableRowNames", inp={"Table": P_EYE_T}); g.set("sne", "TmpNames2", inp={"TmpNames2": "@re.OutRowNames"}); g.get("gne", "TmpNames2"); g.foreach("fe", "@gne.TmpNames2")
    g.n("erow", "get_row", table=P_EYE_T, inp={"RowName": "@fe.Array Element"}, miss="ignore"); g.brk("ber", P_EYE_S, "@erow.OutRow")
    g.call("eqe", K_MATH, "EqualEqual_NameName", inp={"A": "@ber.Type", "B": "@entry.type"}); g.call("oke", K_MATH, "BooleanOR", inp={"A": "@eqe.ReturnValue", "B": "@isa.ReturnValue"}); g.branch("bqe", "@oke.ReturnValue")
    a3 = adder("e", "makeup", "@fe.Array Element")
    g.chain("entry", "ck", "cr", "bs", "rs", "sns", "fs"); g.chain("fs", *a1); g.chain("fs:Completed", "ba"); g.chain("bs:else", "ba")
    g.chain("ba", "rm", "snm", "fm"); g.chain("fm", "mrow", "bqm", *a2); g.chain("fm:Completed", "ba3", "re", "sne", "fe"); g.chain("fe", "erow", "bqe", *a3)   # All: skins -> make-up -> eyes
    g.chain("ba:else", "trow", "be", "re"); g.chain("be:else", "rm")
    return fn("Collect Look Rows", [param("type", "name")], graph=g)


def f_look_row_passes():
    """Filters of the appearance page for one row: search (Look Matches), chip (LookGroup: None = not hidden; Hidden = hidden only; Vanilla = no mod
    and not hidden; else its mod and not hidden), "only favourites"."""
    g = G(); g.n("dn", "call_self", function="Display Name", inp={"kind": "@entry.kind", "row": "@entry.row"})
    g.n("lm", "call_self", function="Look Matches", inp={"kind": "@entry.kind", "row": "@entry.row", "shown": "@dn.s"})
    g.n("k", "call_self", function="Look Key", inp={"name": "@entry.row"}); g.n("hid", "call_self", function="Is Item Hidden", inp={"name": "@k.key"}); g.n("fav", "call_self", function="Is Favorite", inp={"name": "@k.key"})
    g.get("gg", "LookGroup"); g.call("isN", K_MATH, "EqualEqual_NameName", inp={"A": "@gg.LookGroup", "B": "None"}); g.call("isH", K_MATH, "EqualEqual_NameName", inp={"A": "@gg.LookGroup", "B": "Hidden"})
    g.call("isV", K_MATH, "EqualEqual_NameName", inp={"A": "@gg.LookGroup", "B": "Vanilla"}); g.n("imd", "call_self", function="Item Mod", inp={"row": "@entry.row"})
    g.call("nf", K_MATH, "Not_PreBool", inp={"A": "@imd.found"}); g.call("van", K_MATH, "BooleanAND", inp={"A": "@isV.ReturnValue", "B": "@nf.ReturnValue"})
    g.n("mal", "call_self", function="Mod Alias", inp={"mod": "@imd.mod"}); g.call("eqm", K_MATH, "EqualEqual_NameName", inp={"A": "@mal.alias", "B": "@gg.LookGroup"}); g.call("mod", K_MATH, "BooleanAND", inp={"A": "@eqm.ReturnValue", "B": "@imd.found"})
    g.call("o1", K_MATH, "BooleanOR", inp={"A": "@isN.ReturnValue", "B": "@van.ReturnValue"}); g.call("o2", K_MATH, "BooleanOR", inp={"A": "@o1.ReturnValue", "B": "@mod.ReturnValue"})
    g.call("nh", K_MATH, "Not_PreBool", inp={"A": "@hid.yes"}); g.call("vis", K_MATH, "BooleanAND", inp={"A": "@o2.ReturnValue", "B": "@nh.ReturnValue"})
    g.call("hh", K_MATH, "BooleanAND", inp={"A": "@isH.ReturnValue", "B": "@hid.yes"}); g.call("chip", K_MATH, "BooleanOR", inp={"A": "@vis.ReturnValue", "B": "@hh.ReturnValue"})
    g.get("gof", "LookOnlyFav"); g.call("nof", K_MATH, "Not_PreBool", inp={"A": "@gof.LookOnlyFav"}); g.call("fok", K_MATH, "BooleanOR", inp={"A": "@nof.ReturnValue", "B": "@fav.yes"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@lm.yes", "B": "@chip.ReturnValue"}); g.call("a2", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@fok.ReturnValue"})
    g.set("st", "TmpBool", inp={"TmpBool": "@a2.ReturnValue"}); g.get("gt", "TmpBool"); g.link("gt.TmpBool", "return.yes")
    g.chain("entry", "k", "st", "return")
    return fn("Look Row Passes", [param("kind", "name"), param("row", "name")], [param("yes", "bool")], graph=g)


def f_look_groups():
    """Chips of the collected rows: Vanilla / mod folder per row (unique, order of first occurrence), "Hidden" last if a row is hidden."""
    g = G(); g.get("gn0", "TmpNames4"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gn0.TmpNames4"}); g.set("hf0", "TmpFound", inp={"TmpFound": "false"})
    g.get("gr", "LookRows"); g.foreach("fe", "@gr.LookRows")
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@fe.Array Element"}); g.n("mal", "call_self", function="Mod Alias", inp={"mod": "@imd.mod"})   # MergeMods: one chip per shown name
    g.call("ms", K_STR, "Conv_NameToString", inp={"InName": "@mal.alias"}); g.call("sel", K_MATH, "SelectString", inp={"A": "@ms.ReturnValue", "B": "Vanilla", "bPickA": "@imd.found"}); g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@sel.ReturnValue"})
    g.get("gn1", "TmpNames4"); g.call("add", K_ARR, "Array_AddUnique", inp={"TargetArray": "@gn1.TmpNames4", "NewItem": "@s2n.ReturnValue"})
    g.n("ih", "call_self", function="Is Look Hidden", inp={"name": "@fe.Array Element"}); g.branch("bih", "@ih.yes"); g.set("hf1", "TmpFound", inp={"TmpFound": "true"})
    g.get("ghf", "TmpFound"); g.branch("bhf", "@ghf.TmpFound"); g.get("gn3", "TmpNames4"); g.call("addh", K_ARR, "Array_Add", inp={"TargetArray": "@gn3.TmpNames4", "NewItem": g.lit_name("lh", "Hidden")})
    g.get("gn2", "TmpNames4"); g.link("gn2.TmpNames4", "return.groups")
    g.chain("entry", "clr", "hf0", "fe"); g.chain("fe", "add", "ih", "bih", "hf1"); g.chain("fe:Completed", "bhf", "addh", "return"); g.chain("bhf:else", "return")
    return fn("Look Groups", outputs=[param("groups", "name", "array")], graph=g)


def f_look_chip_caption():
    """Caption of an appearance chip: Vanilla / Hidden from the strings, a mod by Mod Caption; cut like the group chips (Cut Caption)."""
    g = G()
    g.call("isV", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.group", "B": "Vanilla"}); g.branch("bv", "@isV.ReturnValue")
    g.n("tv", "call_self", function="T", inp={"key": "Lbl_Vanilla"}); g.call("tvs", K_TXT, "Conv_TextToString", inp={"InText": "@tv.text"}); g.set("s1", "TmpStr", inp={"TmpStr": "@tvs.ReturnValue"})
    g.call("isH", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.group", "B": "Hidden"}); g.branch("bh", "@isH.ReturnValue")
    g.n("th", "call_self", function="T", inp={"key": "Group_Hidden"}); g.call("ths", K_TXT, "Conv_TextToString", inp={"InText": "@th.text"}); g.set("s2", "TmpStr", inp={"TmpStr": "@ths.ReturnValue"})
    g.n("mc", "call_self", function="Mod Caption", inp={"mod": "@entry.group"}); g.set("s3", "TmpStr", inp={"TmpStr": "@mc.s"})
    g.get("gs", "TmpStr"); g.n("cut", "call_self", function="Cut Caption", inp={"text": "@gs.TmpStr", "full": "@entry.full"}); g.link("cut.caption", "return.caption")
    g.chain("entry", "bv", "s1", "return"); g.chain("bv:else", "bh", "s2", "return"); g.chain("bh:else", "s3", "return")   # Cut Caption is pure
    return fn("Look Chip Caption", [param("group", "name"), param("full", "bool")], [param("caption", "text")], graph=g)


def f_rebuild_look_chips():
    """Chip row of the appearance page (Rebuild SubTabs for mods): All, "..." (collapse), one chip per Look Groups entry; hidden for presets
    and when there is nothing to choose (one group)."""
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Look SubTabs", inp={"self": "@gp.Panel"})
    g.get("glc", "LookCat"); g.call("isp", K_MATH, "EqualEqual_NameName", inp={"A": "@glc.LookCat", "B": "Presets"}); g.branch("bp", "@isp.ReturnValue")
    g.get("gpv0", "Panel"); g.call("hide", W_PANEL, "Set Look Chips Visible", inp={"self": "@gpv0.Panel", "visible": "false"})
    g.get("glc2", "LookCat"); g.n("col", "call_self", function="Collect Look Rows", inp={"type": "@glc2.LookCat"}); g.n("gr", "call_self", function="Look Groups")
    g.set("sgr", "TmpNames3", inp={"TmpNames3": "@gr.groups"}); g.get("ggr", "TmpNames3"); g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@ggr.TmpNames3"})
    g.call("gt1", K_MATH, "Greater_IntInt", inp={"A": "@len.ReturnValue", "B": "1"}); g.get("gpv", "Panel"); g.call("vis", W_PANEL, "Set Look Chips Visible", inp={"self": "@gpv.Panel", "visible": "@gt1.ReturnValue"}); g.branch("b", "@gt1.ReturnValue")
    aw = create_widget(g, "ca", W_SUB); set_manager(g, "sma", W_SUB, aw)
    g.get("gcg", "LookGroup"); g.call("selA", K_MATH, "EqualEqual_NameName", inp={"A": "@gcg.LookGroup", "B": "None"})
    g.call("ia", W_SUB, "Init", inp={"self": aw, "group": "None", "caption": tt(g, "ta", "Chip_All"), "selected": "@selA.ReturnValue"})
    g.get("gp2", "Panel"); g.call("aa", W_PANEL, "Add Look SubTab", inp={"self": "@gp2.Panel", "widget": aw})
    mw = create_widget(g, "cm", W_SUB); set_manager(g, "smm", W_SUB, mw); g.get("gcol", "LookChipsCollapsed")
    g.call("im", W_SUB, "Init", inp={"self": mw, "group": "AltUI_More", "caption": tt(g, "tm", "Chip_More"), "selected": "@gcol.LookChipsCollapsed"})
    g.get("gpm", "Panel"); g.call("am", W_PANEL, "Add Look SubTab", inp={"self": "@gpm.Panel", "widget": mw})
    g.get("ggr2", "TmpNames3"); g.foreach("fe", "@ggr2.TmpNames3")
    g.get("gcg2", "LookGroup"); g.call("selG", K_MATH, "EqualEqual_NameName", inp={"A": "@gcg2.LookGroup", "B": "@fe.Array Element"})
    g.get("gcol2", "LookChipsCollapsed"); g.call("ncol", K_MATH, "Not_PreBool", inp={"A": "@gcol2.LookChipsCollapsed"})
    g.call("show", K_MATH, "BooleanOR", inp={"A": "@ncol.ReturnValue", "B": "@selG.ReturnValue"}); g.branch("bs", "@show.ReturnValue")
    sw = create_widget(g, "cs", W_SUB); set_manager(g, "sms", W_SUB, sw)
    g.get("gcol3", "LookChipsCollapsed"); g.call("fullc", K_MATH, "BooleanAND", inp={"A": "@gcol3.LookChipsCollapsed", "B": "@selG.ReturnValue"})
    g.n("cap", "call_self", function="Look Chip Caption", inp={"group": "@fe.Array Element", "full": "@fullc.ReturnValue"})
    g.call("is", W_SUB, "Init", inp={"self": sw, "group": "@fe.Array Element", "caption": "@cap.caption", "selected": "@selG.ReturnValue"})
    g.get("gp3", "Panel"); g.call("as", W_PANEL, "Add Look SubTab", inp={"self": "@gp3.Panel", "widget": sw})
    g.chain("entry", "cl", "bp", "hide"); g.chain("bp:else", "col", "gr", "sgr", "vis", "b", "ca_cr", "sma", "ia", "aa", "cm_cr", "smm", "im", "am", "fe"); g.chain("fe", "bs", "cs_cr", "sms", "cap", "is", "as")
    return fn("Rebuild Look Chips", graph=g)


def f_look_only_mod():
    """Context menu 'Only this mod': the row's mod chip."""
    g = G(); g.n("imd", "call_self", function="Item Mod", inp={"row": "@entry.name"}); g.branch("b", "@imd.found"); g.n("mal", "call_self", function="Mod Alias", inp={"mod": "@imd.mod"}); g.n("sg", "call_self", function="Select Look Group", inp={"name": "@mal.alias"})
    g.chain("entry", "b", "sg"); return fn("Look Only Mod", [param("name", "name")], graph=g)


def f_select_look_group():
    """Chip click on the appearance page: "..." folds the row (only the selected chip stays), else the chip filters the tiles."""
    g = G(); g.call("ism", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "AltUI_More"}); g.branch("bm", "@ism.ReturnValue")
    g.get("gcol", "LookChipsCollapsed"); g.call("ncol", K_MATH, "Not_PreBool", inp={"A": "@gcol.LookChipsCollapsed"}); g.set("scol", "LookChipsCollapsed", inp={"LookChipsCollapsed": "@ncol.ReturnValue"})
    g.n("svm", "call_self", function="Save Settings"); g.n("rtm", "call_self", function="Rebuild Look Chips")
    g.set("hlc", "HighlightItem", inp={"HighlightItem": "None"}); g.set("s", "LookGroup", inp={"LookGroup": "@entry.name"})
    g.n("rt", "call_self", function="Rebuild Look Chips"); g.n("rc", "call_self", function="Rebuild Look Cats"); g.n("rl", "call_self", function="Rebuild Look")
    g.chain("entry", "bm", "scol", "svm", "rtm"); g.chain("bm:else", "hlc", "s", "rt", "rc", "rl")
    return fn("Select Look Group", [param("name", "name")], graph=g)


def f_look_count():
    """Number of entries of a category (presets; All = skin + every make-up type; otherwise the collected rows of the category);
    filtered = only the entries that pass the page filters (Look Row Passes: search, chip, only favourites)."""
    g = G(); g.set("z", "TmpIdx", inp={"TmpIdx": "0"}); g.call("nfl", K_MATH, "Not_PreBool", inp={"A": "@entry.filtered"})
    # All: Skin + every MakeupTypeTable type (recursive; TmpIdx is clobbered by the inner calls -> TmpI accumulates)
    g.call("isa", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.type", "B": "All"}); g.branch("ba", "@isa.ReturnValue")
    g.n("acs", "call_self", function="Look Count", inp={"type": g.lit_name("askn", "Skin"), "filtered": "@entry.filtered"}); g.set("asi", "TmpI", inp={"TmpI": "@acs.n"})
    g.call("arn", K_DT, "GetDataTableRowNames", inp={"Table": P_MTYPE_T}); g.set("asn", "LookTypes", inp={"LookTypes": "@arn.OutRowNames"}); g.get("agn", "LookTypes"); g.foreach("fa", "@agn.LookTypes")
    g.n("act", "call_self", function="Look Count", inp={"type": "@fa.Array Element", "filtered": "@entry.filtered"})
    g.get("agi", "TmpI"); g.call("aadd", K_MATH, "Add_IntInt", inp={"A": "@agi.TmpI", "B": "@act.n"}); g.set("asi2", "TmpI", inp={"TmpI": "@aadd.ReturnValue"})
    g.get("agr", "TmpI"); g.set("asr", "TmpIdx", inp={"TmpIdx": "@agr.TmpI"})
    # presets
    g.call("isp", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.type", "B": "Presets"}); g.branch("bp", "@isp.ReturnValue")
    pd = presets_data(g, "pd"); g.foreach("fp", pd)
    g.call("pi1", K_MATH, "Add_IntInt", inp={"A": "@fp.Array Index", "B": "1"}); g.call("pi1s", K_STR, "Conv_IntToString", inp={"InInt": "@pi1.ReturnValue"}); g.call("pdn", K_STR, "Concat_StrStr", inp={"A": "Preset ", "B": "@pi1s.ReturnValue"})
    g.call("pis", K_STR, "Conv_IntToString", inp={"InInt": "@fp.Array Index"}); g.call("pn1", K_STR, "Concat_StrStr", inp={"A": "Preset_", "B": "@pis.ReturnValue"}); g.call("pnn", K_STR, "Conv_StringToName", inp={"InString": "@pn1.ReturnValue"})
    g.n("pm", "call_self", function="Look Matches", inp={"kind": "preset", "row": "@pnn.ReturnValue", "shown": "@pdn.ReturnValue"}); g.call("pok", K_MATH, "BooleanOR", inp={"A": "@nfl.ReturnValue", "B": "@pm.yes"}); g.branch("bpk", "@pok.ReturnValue")
    g.get("gi0", "TmpIdx"); g.call("inc0", K_MATH, "Add_IntInt", inp={"A": "@gi0.TmpIdx", "B": "1"}); g.set("si0", "TmpIdx", inp={"TmpIdx": "@inc0.ReturnValue"})
    # rows of the category
    g.n("col", "call_self", function="Collect Look Rows", inp={"type": "@entry.type"})
    g.get("gr", "LookRows"); g.foreach("fr", "@gr.LookRows"); g.branch("bnf", "@nfl.ReturnValue")
    g.get("gk", "LookRowKinds"); g.call("kg", K_ARR, "Array_Get", inp={"TargetArray": "@gk.LookRowKinds", "Index": "@fr.Array Index"})
    g.n("ps", "call_self", function="Look Row Passes", inp={"kind": "@kg.Item", "row": "@fr.Array Element"}); g.branch("bok", "@ps.yes")
    g.get("gi1", "TmpIdx"); g.call("inc1", K_MATH, "Add_IntInt", inp={"A": "@gi1.TmpIdx", "B": "1"}); g.set("si1", "TmpIdx", inp={"TmpIdx": "@inc1.ReturnValue"})
    g.get("grt", "TmpIdx"); g.link("grt.TmpIdx", "return.n")
    g.chain("entry", "z", "ba", "acs", "asi", "arn", "asn", "fa"); g.chain("fa", "act", "asi2"); g.chain("fa:Completed", "asr", "return")
    g.chain("ba:else", "bp", "fp"); g.chain("fp", "bpk", "si0"); g.chain("fp:Completed", "return")
    g.chain("bp:else", "col", "fr"); g.chain("fr", "bnf", "si1"); g.chain("bnf:else", "ps", "bok", "si1"); g.chain("fr:Completed", "return")
    return fn("Look Count", [param("type", "name"), param("filtered", "bool")], [param("n", "int")], graph=g)


def f_rebuild_look_cats():
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Look Cats", inp={"self": "@gp.Panel"})
    g.call("rn", K_DT, "GetDataTableRowNames", inp={"Table": P_MTYPE_T}); g.set("sn", "TmpNames", inp={"TmpNames": "@rn.OutRowNames"})
    g.get("gn0", "TmpNames"); g.call("ins", K_ARR, "Array_Insert", inp={"TargetArray": "@gn0.TmpNames", "NewItem": g.lit_name("skin", "Skin"), "Index": "0"})
    g.get("gna", "TmpNames"); g.call("insa", K_ARR, "Array_Insert", inp={"TargetArray": "@gna.TmpNames", "NewItem": g.lit_name("all", "All"), "Index": "0"})
    g.get("gn9", "TmpNames"); g.call("adp", K_ARR, "Array_Add", inp={"TargetArray": "@gn9.TmpNames", "NewItem": g.lit_name("prs", "Presets")})
    g.get("gn", "TmpNames"); g.foreach("fe", "@gn.TmpNames")
    tw = create_widget(g, "ct", W_TAB); set_manager(g, "smt", W_TAB, tw)
    g.n("cap", "call_self", function="Look Caption", inp={"type": "@fe.Array Element"}); g.n("cnt", "call_self", function="Look Count", inp={"type": "@fe.Array Element", "filtered": "false"})
    g.n("cntf", "call_self", function="Look Count", inp={"type": "@fe.Array Element", "filtered": "true"})   # search hits: "total (hits)" like the clothes page, -1 = no search
    g.get("gst", "LookSearchText"); g.call("sne0", K_STR, "IsEmpty", inp={"InString": "@gst.LookSearchText"})
    g.get("glg", "LookGroup"); g.call("gno", K_MATH, "EqualEqual_NameName", inp={"A": "@glg.LookGroup", "B": "None"}); g.get("gof", "LookOnlyFav"); g.call("nof", K_MATH, "Not_PreBool", inp={"A": "@gof.LookOnlyFav"})
    g.call("noact0", K_MATH, "BooleanAND", inp={"A": "@sne0.ReturnValue", "B": "@gno.ReturnValue"}); g.call("noact", K_MATH, "BooleanAND", inp={"A": "@noact0.ReturnValue", "B": "@nof.ReturnValue"})   # no filter active -> total only
    g.call("fsel", K_MATH, "SelectInt", inp={"A": "-1", "B": "@cntf.n", "bPickA": "@noact.ReturnValue"})
    g.call("has", K_MATH, "Greater_IntInt", inp={"A": "@cnt.n", "B": "0"})
    g.get("glc", "LookCat"); g.call("sel", K_MATH, "EqualEqual_NameName", inp={"A": "@fe.Array Element", "B": "@glc.LookCat"})
    g.call("ti", W_TAB, "Init", inp={"self": tw, "slot": "@fe.Array Element", "caption": "@cap.caption", "count": "@cnt.n", "selected": "@sel.ReturnValue", "has items": "@has.ReturnValue", "filtered": "@fsel.ReturnValue"})
    g.get("gp3", "Panel"); g.call("at", W_PANEL, "Add Look Cat", inp={"self": "@gp3.Panel", "widget": tw})
    g.chain("entry", "cl", "rn", "sn", "ins", "insa", "adp", "fe"); g.chain("fe", "ct_cr", "smt", "cap", "cnt", "cntf", "ti", "at")
    return fn("Rebuild Look Cats", graph=g)


def f_select_look_cat():
    """Category click: the chip stays selected when the new category has that group too (Look Groups), otherwise back to All - like Select Slot."""
    g = G(); g.set("s", "LookCat", inp={"LookCat": "@entry.name"})
    g.n("col", "call_self", function="Collect Look Rows", inp={"type": "@entry.name"}); g.n("lg", "call_self", function="Look Groups")
    g.get("gg", "LookGroup"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@lg.groups", "ItemToFind": "@gg.LookGroup"}); g.branch("bk", "@has.ReturnValue")
    g.set("sg", "LookGroup", inp={"LookGroup": "None"}); g.n("rch", "call_self", function="Rebuild Look Chips")
    g.n("rc", "call_self", function="Rebuild Look Cats"); g.n("rl", "call_self", function="Rebuild Look")
    g.n("uf", "call_self", function="Update Focus"); g.set("hlc", "HighlightItem", inp={"HighlightItem": "None"})
    g.chain("entry", "hlc", "s", "col", "lg", "bk", "rch"); g.chain("bk:else", "sg", "rch"); g.chain("rch", "rc", "rl", "uf"); return fn("Select Look Cat", [param("name", "name")], graph=g)


def look_row_tiles(g, p, idx_pin, row_pin, add_fn, fav_pin):
    """Tile for one collected row (kind from LookRowKinds[idx]): skin -> SkinTable icon, selection/tooltip category Skin; makeup -> MakeupTable row,
    else EyeTable row (icon + Type). Returns the id of the first node; the chains end in the loop body."""
    g.get(p + "gk", "LookRowKinds"); g.call(p + "k", K_ARR, "Array_Get", inp={"TargetArray": "@%sgk.LookRowKinds" % p, "Index": idx_pin}); kind = "@%sk.Item" % p
    g.call(p + "isk", K_MATH, "EqualEqual_NameName", inp={"A": kind, "B": "skin"}); g.branch(p + "bk", "@%sisk.ReturnValue" % p)
    g.get(p + "hl", "HighlightItem"); g.call(p + "eq", K_MATH, "EqualEqual_NameName", inp={"A": row_pin, "B": "@%shl.HighlightItem" % p})   # scroll target of a "Show in tab" jump
    tiles = []
    for t, table, struct, icon, typ in (("s", P_SKIN_T, P_SKIN_S, "icon", None), ("m", P_MAKEUP_T, P_MAKEUP_S, "Icon", "Type"), ("e", P_EYE_T, P_EYE_S, "Icon", "Type")):
        q = p + t; g.n(q + "r", "get_row", table=table, inp={"RowName": row_pin}, miss="ignore"); g.brk(q + "b", struct, "@%sr.OutRow" % q)
        type_pin = g.lit_name(q + "tn", "Skin") if typ is None else "@%sb.%s" % (q, typ)
        g.n(q + "sel", "call_self", function="Is Look Selected", inp={"type": type_pin, "style": row_pin}); g.n(q + "cap", "call_self", function="Look Caption", inp={"type": type_pin})
        tk = "skin" if typ is None else "makeup"
        chain = look_tile(g, q + "t", make_item(g, q + "mi", row_pin, "@%sb.%s" % (q, icon), kind=tk), "@%ssel.yes" % q, "true", add_fn, "@%scap.caption" % q, kind=tk, fav_pin=fav_pin)
        g.branch(q + "bh", "@%seq.ReturnValue" % p); g.set(q + "sw", "ScrollWidget", inp={"ScrollWidget": "@%st.AsW_ClothesButton" % q})
        g.chain(q + "r", q + "sel", q + "cap", *chain, q + "bh", q + "sw"); tiles.append(q + "r")
    g.chain(p + "bk", tiles[0]); g.chain(p + "bk:else", tiles[1]); g.chain(p + "mr:Row Not Found", tiles[2])
    return p + "bk"


def f_rebuild_look():
    g = G()
    g.get("glc7", "LookCat"); g.n("lcp", "call_self", function="Look Caption", inp={"type": "@glc7.LookCat"})   # presets: tooltip of every tile
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Look", inp={"self": "@gp.Panel"}); g.get("gpf", "Panel"); g.call("clf", W_PANEL, "Clear Look Fav", inp={"self": "@gpf.Panel"})
    # presets: "+" tile (outfit widget) + one tile per preset with its icon file; no favourites block
    g.get("glc0", "LookCat"); g.call("isp", K_MATH, "EqualEqual_NameName", inp={"A": "@glc0.LookCat", "B": "Presets"}); g.branch("bp", "@isp.ReturnValue")
    g.get("gpf0", "Panel"); g.call("sfv0", W_PANEL, "Set Look Fav Visible", inp={"self": "@gpf0.Panel", "visible": "false"})
    g.get("gi0", "TmpIcons"); g.call("clr0", K_ARR, "Array_Clear", inp={"TargetArray": "@gi0.TmpIcons"})
    pw = create_widget(g, "cpa", W_OUTFIT); set_manager(g, "smpa", W_OUTFIT, pw)
    g.get("gi1", "TmpIcons"); g.call("pai", W_OUTFIT, "Init", inp={"self": pw, "index": "-1", "icons": "@gi1.TmpIcons", "count": "0", "caption": tt(g, "pct", "Btn_SavePreset")})
    g.get("gpa", "Panel"); g.call("paa", W_PANEL, "Add Look", inp={"self": "@gpa.Panel", "widget": pw})
    pd = presets_data(g, "pd"); g.foreach("fp", pd); g.brk("bpr", P_PRESET_S, "@fp.Array Element")
    g.n("pic", "call_self", function="Preset Icon", inp={"number": "@bpr.IconNumber"})
    g.call("pis", K_STR, "Conv_IntToString", inp={"InInt": "@fp.Array Index"}); g.call("pn1", K_STR, "Concat_StrStr", inp={"A": "Preset_", "B": "@pis.ReturnValue"}); g.call("pnn", K_STR, "Conv_StringToName", inp={"InString": "@pn1.ReturnValue"})
    g.call("pi1", K_MATH, "Add_IntInt", inp={"A": "@fp.Array Index", "B": "1"}); g.call("pi1s", K_STR, "Conv_IntToString", inp={"InInt": "@pi1.ReturnValue"}); g.call("pdn", K_STR, "Concat_StrStr", inp={"A": "Preset ", "B": "@pi1s.ReturnValue"})
    g.make("mip", S_ITEM, Name="@pnn.ReturnValue", DisplayName="@pdn.ReturnValue", Icon="@pic.tex")
    g.n("pmt", "call_self", function="Look Matches", inp={"kind": "preset", "row": "@pnn.ReturnValue", "shown": "@pdn.ReturnValue"}); g.branch("bpm", "@pmt.yes")   # appearance search
    tp = look_tile(g, "tp", "@mip.S_ClothesItem", "false", "true", "Add Look", "@lcp.caption")
    # skins / make-up / eyes: the collected rows of the category; pass 1 favourites block, pass 2 every row that passes the filters
    g.get("glc1", "LookCat"); g.n("col", "call_self", function="Collect Look Rows", inp={"type": "@glc1.LookCat"}); g.set("nf", "TmpIdx", inp={"TmpIdx": "0"})
    g.get("gr1", "LookRows"); g.foreach("ff", "@gr1.LookRows")
    g.get("gk1", "LookRowKinds"); g.call("kf", K_ARR, "Array_Get", inp={"TargetArray": "@gk1.LookRowKinds", "Index": "@ff.Array Index"})
    g.n("pf", "call_self", function="Look Row Passes", inp={"kind": "@kf.Item", "row": "@ff.Array Element"}); g.n("ffv", "call_self", function="Is Look Favorite", inp={"name": "@ff.Array Element"})
    g.call("fok", K_MATH, "BooleanAND", inp={"A": "@pf.yes", "B": "@ffv.yes"}); g.branch("bf", "@fok.ReturnValue")
    t1 = look_row_tiles(g, "f", "@ff.Array Index", "@ff.Array Element", "Add Look Fav", "true")
    g.get("gn", "TmpIdx"); g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gn.TmpIdx", "B": "1"}); g.set("sn", "TmpIdx", inp={"TmpIdx": "@inc.ReturnValue"})
    g.get("gn2", "TmpIdx"); g.call("gt0", K_MATH, "Greater_IntInt", inp={"A": "@gn2.TmpIdx", "B": "0"}); g.get("gp5", "Panel"); g.call("sfv", W_PANEL, "Set Look Fav Visible", inp={"self": "@gp5.Panel", "visible": "@gt0.ReturnValue"})
    g.get("gr2", "LookRows"); g.foreach("fe", "@gr2.LookRows")
    g.get("gk2", "LookRowKinds"); g.call("ke", K_ARR, "Array_Get", inp={"TargetArray": "@gk2.LookRowKinds", "Index": "@fe.Array Index"})
    g.n("pe", "call_self", function="Look Row Passes", inp={"kind": "@ke.Item", "row": "@fe.Array Element"}); g.branch("be", "@pe.yes")
    g.n("efv", "call_self", function="Is Look Favorite", inp={"name": "@fe.Array Element"})
    t2 = look_row_tiles(g, "a", "@fe.Array Index", "@fe.Array Element", "Add Look", "@efv.yes")
    g.chain("entry", "cl", "clf", "lcp", "bp", "sfv0", "clr0", "cpa_cr", "smpa", "pai", "paa", "fp"); g.chain("fp", "pic", "bpm", *tp)
    g.chain("bp:else", "col", "nf", "ff"); g.chain("ff", "pf", "ffv", "bf", "sn", t1)
    g.chain("ff:Completed", "sfv", "fe"); g.chain("fe", "pe", "be", "efv", t2)
    return fn("Rebuild Look", graph=g)


def f_look_clicked():
    """Vanilla logic (AppearancePanel.On Makeup/Eye/Skin Button Clicked) without camera moves."""
    g = G(); md = makeup_data(g, "md")
    # "All": the row's own type stands in for LookCat while the body runs (None = unknown row -> nothing), restored before Rebuild Look
    g.get("glcs", "LookCat"); g.set("svc", "LookCatSave", inp={"LookCatSave": "@glcs.LookCat"})
    g.get("glca", "LookCat"); g.call("isa", K_MATH, "EqualEqual_NameName", inp={"A": "@glca.LookCat", "B": "All"}); g.branch("ba", "@isa.ReturnValue")
    g.n("lto", "call_self", function="Look Type Of", inp={"name": "@entry.name"}); g.call("ltn", K_MATH, "EqualEqual_NameName", inp={"A": "@lto.type", "B": "None"}); g.branch("bln", "@ltn.ReturnValue")
    g.set("slc", "LookCat", inp={"LookCat": "@lto.type"})
    g.get("glcr", "LookCatSave"); g.set("rlc", "LookCat", inp={"LookCat": "@glcr.LookCatSave"})
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
    g.chain("entry", "svc", "ba", "lto", "bln"); g.chain("bln:else", "slc", "bp"); g.chain("ba:else", "bp"); g.chain("bp", "pix", "pcl"); g.chain("bp:else", "md", "bs", "ph", "cs", "sd"); g.chain("bs:else", "trow", "ph2", "sel", "be", "bes", "erm", "ues"); g.chain("bes:else", "eclr", "eadd", "eset", "ues"); g.chain("ues", "sd")
    g.chain("be:else", "sl", "bms", "beb", "sd"); g.chain("beb:else", "mrm", "bgt"); g.chain("bms:else", "bsg", "mclr", "madd", "bgt"); g.chain("bsg:else", "madd")
    g.chain("bgt", "mset", "srow"); g.chain("bgt:else", "mrem", "srow"); g.chain("srow", "ban", "pm", "umt"); g.chain("ban:else", "umt"); g.chain("srow:Row Not Found", "umt"); g.chain("umt", "sd"); g.chain("sd", "rlc", "rl")
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
    # bone-scale sliders: reset chip, slider positions from the body's factors ((f - FACTOR_MIN) / (FACTOR_MAX - FACTOR_MIN)), enabled only with our ABP, notice otherwise
    rw = create_widget(g, "cr", W_SUB); set_manager(g, "smr", W_SUB, rw)
    g.call("ir", W_SUB, "Init", inp={"self": rw, "group": "BodyScReset", "caption": tt(g, "tr", "Btn_ScReset"), "selected": "false"})
    g.get("gp5", "Panel"); g.call("ar", W_PANEL, "Add Body Chip", inp={"self": "@gp5.Panel", "widget": rw})
    g.get("gcb3", "CurrentBody"); g.n("fac", "call_self", function="Body Scale Factors", inp={"name": "@gcb3.CurrentBody"})
    vals = {}
    for i, key in enumerate(SCALE_KEYS):
        lo, hi = bg.factor_range(bg.SLIDERS[i][0])
        g.call("fg%d" % i, K_ARR, "Array_Get", inp={"TargetArray": "@fac.factors", "Index": str(i)})
        g.call("sub%d" % i, K_MATH, "Subtract_FloatFloat", inp={"A": "@fg%d.Item" % i, "B": str(lo)}); g.call("dv%d" % i, K_MATH, "Divide_FloatFloat", inp={"A": "@sub%d.ReturnValue" % i, "B": str(hi - lo)})
        vals[key] = "@dv%d.ReturnValue" % i
    ids = add_floats(g, "v", "BodyScaleVals", [vals[k] for k in SCALE_KEYS])
    g.get("gp6", "Panel"); g.call("ssc", W_PANEL, "Set Body Scales", inp=dict({"self": "@gp6.Panel"}, **vals))
    g.get("gsa", "ScaleActive"); g.get("gp7", "Panel"); g.call("sen", W_PANEL, "Set Body Scales Enabled", inp={"self": "@gp7.Panel", "enabled": "@gsa.ScaleActive"})
    g.get("gcb4", "CurrentBody"); g.call("isn", K_MATH, "NotEqual_NameName", inp={"A": "@gcb4.CurrentBody", "B": "None"}); g.get("gsa2", "ScaleActive"); g.call("nsa", K_MATH, "Not_PreBool", inp={"A": "@gsa2.ScaleActive"})
    g.call("warn", K_MATH, "BooleanAND", inp={"A": "@isn.ReturnValue", "B": "@nsa.ReturnValue"}); g.branch("bw", "@warn.ReturnValue"); pop(g, "npop", tt(g, "nst", "Msg_NoScale"))
    g.chain("entry", "md", "cb", "cw", "sv", "scan", "cl", "cs_cr", "sms", "i0", "a0", "fe"); g.chain("fe", "cm_cr", "smm", "i1", "a1")
    g.chain("fe:Completed", "cr_cr", "smr", "ir", "ar", "fac", *ids, "ssc", "sen", "bw", "npop")
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
    g.call("iscf", K_STR, "StartsWith", inp={"SourceString": "@n2s.ReturnValue", "InPrefix": "Cf:", "SearchCase": "CaseSensitive"}); g.branch("bcf", "@iscf.ReturnValue")
    g.n("tcf", "call_self", function="Toggle Conflict", inp={"key": "@entry.name"})   # slot conflict chip (options)
    g.call("isun", K_STR, "StartsWith", inp={"SourceString": "@n2s.ReturnValue", "InPrefix": "Unowned", "SearchCase": "CaseSensitive"}); g.branch("bun", "@isun.ReturnValue")
    g.n("sun", "call_self", function="Select Unowned", inp={"name": "@entry.name"})   # not-owned mode chip (options)
    g.n("sl", "call_self", function="Select Layout", inp={"name": "@entry.name"})
    g.get("gpg2", "Page"); g.call("isb", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg2.Page", "B": "Body"}); g.branch("bb", "@isb.ReturnValue")
    g.n("sb", "call_self", function="Select Body", inp={"name": "@entry.name"})
    g.set("hlc", "HighlightItem", inp={"HighlightItem": "None"})
    g.call("ism", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "AltUI_More"})
    g.get("gpg3", "Page"); g.call("isc", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg3.Page", "B": "Clothes"})
    g.call("mok", K_MATH, "BooleanAND", inp={"A": "@ism.ReturnValue", "B": "@isc.ReturnValue"}); g.branch("bm", "@mok.ReturnValue")
    g.get("gcol", "SubTabsCollapsed"); g.call("ncol", K_MATH, "Not_PreBool", inp={"A": "@gcol.SubTabsCollapsed"}); g.set("scol", "SubTabsCollapsed", inp={"SubTabsCollapsed": "@ncol.ReturnValue"})
    g.n("svm", "call_self", function="Save Settings"); g.n("rtm", "call_self", function="Rebuild SubTabs")
    g.n("rl", "call_self", function="Rebuild Left")   # the group chip filters the slot counts ("total (in group)")
    g.get("gpg4", "Page"); g.call("islk", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg4.Page", "B": "Look"}); g.branch("blk", "@islk.ReturnValue"); g.n("slgp", "call_self", function="Select Look Group", inp={"name": "@entry.name"})
    g.chain("entry", "bo", "bl", "slg"); g.chain("bl:else", "bk", "sk"); g.chain("bk:else", "bcf", "tcf"); g.chain("bcf:else", "bun", "sun"); g.chain("bun:else", "sl"); g.chain("bo:else", "bb", "sb"); g.chain("bb:else", "blk", "slgp"); g.chain("blk:else", "bm", "scol", "svm", "rtm"); g.chain("bm:else", "hlc", "s", "rl", "rt", "rli")
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
    g.get("gvm", "ViewMod"); g.call("vm", K_MATH, "NotEqual_NameName", inp={"A": "@gvm.ViewMod", "B": "None"}); g.call("yes", K_MATH, "BooleanOR", inp={"A": "@ge.ReturnValue", "B": "@vm.ReturnValue"})
    g.link("yes.ReturnValue", "return.yes"); g.chain("entry", "return")
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
    g.get("gvm", "ViewMod"); g.call("vm", K_MATH, "NotEqual_NameName", inp={"A": "@gvm.ViewMod", "B": "None"}); g.branch("bM", "@vm.ReturnValue")
    g.set("svm", "ViewMod", inp={"ViewMod": "None"}); g.get("gcf", "ContentFrom"); g.n("spf", "call_self", function="Select Page", inp={"name": "@gcf.ContentFrom"})
    g.call("isO", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Outfits"}); g.branch("bO", "@isO.ReturnValue"); g.set("so", "ViewOutfit", inp={"ViewOutfit": "-1"})
    g.call("isL", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Looks"}); g.branch("bL", "@isL.ReturnValue"); g.set("sl", "ViewLook", inp={"ViewLook": "-1"})
    g.call("isA", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Look"}); g.branch("bA", "@isA.ReturnValue"); g.set("sp", "ViewPreset", inp={"ViewPreset": "-1"})
    g.get("gpg2", "Page"); g.n("spg", "call_self", function="Select Page", inp={"name": "@gpg2.Page"})
    g.chain("entry", "bM", "svm", "spf"); g.chain("bM:else", "bO", "so", "spg"); g.chain("bO:else", "bL", "sl", "spg"); g.chain("bL:else", "bA", "sp", "spg"); g.chain("bA:else", "spg")
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


def content_tile(g, id, item_pin, worn_pin, owned_pin, fav_pin, damaged_pin, tip_pin, kind=None):
    """W_ClothesButton in the current section (TmpSection); returns (exec chain, widget pin). With kind (hair / skin / makeup / body) tip_pin is the
    category text and the tooltip comes from Item Tip; else tip_pin is the tooltip (clothes: the caller's Item Tip)."""
    pre = []
    if kind: n, tip_pin = tile_tip(g, id, item_pin, kind, tip_pin); pre = [n]
    tw = create_widget(g, id, W_BTN); set_manager(g, id + "_sm", W_BTN, tw)
    g.call(id + "_i", W_BTN, "Init", inp={"self": tw, "item": item_pin, "worn": worn_pin, "owned": owned_pin, "fav": fav_pin, "damaged": damaged_pin, "tip": tip_pin})
    g.get(id + "_gs", "TmpSection"); g.call(id + "_a", W_SECTION, "Add Tile", inp={"self": "@%s_gs.TmpSection" % id, "widget": tw})
    return pre + [id + "_cr", id + "_sm", id + "_i", id + "_a"], tw


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
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@fw.Array Element"}); g.n("io", "call_self", function="Shown Owned", inp={"name": "@fw.Array Element"})
    g.n("ifv", "call_self", function="Is Favorite", inp={"name": "@fw.Array Element"}); g.n("idm", "call_self", function="Is Damaged", inp={"name": "@fw.Array Element"})
    g.call("own1", K_MATH, "BooleanAND", inp={"A": "@io.yes", "B": "@fi.found"}); g.n("tip", "call_self", function="Item Tip", inp={"item": "@gti.TmpItem", "kind": "item", "category": ""})
    t1, w1 = content_tile(g, "t1", "@gti.TmpItem", "@iw.yes", "@own1.ReturnValue", "@ifv.yes", "@idm.yes", "@tip.tip")
    g.call("cf", K_MAP, "Map_Find", inp={"TargetMap": "@bv.Colors", "Key": "@fw.Array Element"}); g.branch("bcf", "@cf.ReturnValue")
    g.call("scs", W_BTN, "Set Color Swatch", inp={"self": w1, "color": "@cf.Value"})
    # --- hairstyle (+ hair colour)
    g.call("hn", K_MATH, "NotEqual_NameName", inp={"A": "@bv.Hair", "B": "None"}); g.branch("bh", "@hn.ReturnValue")
    sec2 = content_section(g, "s2", tt(g, "s2t", "Tab_Hair"))
    g.n("hrow", "get_row", table=P_HAIR_T, inp={"RowName": "@bv.Hair"}); g.brk("hbr", P_HAIR_S, "@hrow.OutRow")
    g.set("shi", "TmpItem", inp={"TmpItem": make_item(g, "mhi", "@bv.Hair", "@hbr.icon", slot="Hair", kind="hair")}); g.set("shp", "TmpItem", inp={"TmpItem": make_item(g, "mhp", "@bv.Hair", "None", slot="Hair", kind="hair")})
    g.get("gpl", "Player"); g.call("cur", P_JODI, "Get Hairstyle Name", inp={"self": "@gpl.Player"}); g.call("hsel", K_MATH, "EqualEqual_NameName", inp={"A": "@cur.name", "B": "@bv.Hair"})
    howned = hair_owned(g, "hown", "@bv.Hair", "@hbr.MirrorID")
    g.get("gti2", "TmpItem"); t2, w2 = content_tile(g, "t2", "@gti2.TmpItem", "@hsel.ReturnValue", howned, "false", "false", tt(g, "t2t", "Tab_Hair"), kind="hair")
    g.call("shc", W_BTN, "Set Color Swatch", inp={"self": w2, "color": "@bv.HairColor"})
    # --- skin
    g.call("skn", K_MATH, "NotEqual_NameName", inp={"A": "@bv.Skin", "B": "None"}); g.branch("bsk", "@skn.ReturnValue")
    sec3 = content_section(g, "s3", tt(g, "s3t", "Look_Skin"))
    g.n("srow", "get_row", table=P_SKIN_T, inp={"RowName": "@bv.Skin"}); g.brk("sbr", P_SKIN_S, "@srow.OutRow")
    g.set("ssi", "TmpItem", inp={"TmpItem": make_item(g, "msi", "@bv.Skin", "@sbr.icon", slot="Skin", kind="skin")}); g.set("ssp", "TmpItem", inp={"TmpItem": make_item(g, "msp", "@bv.Skin", "None", slot="Skin", kind="skin")})
    g.n("ssel", "call_self", function="Is Look Selected", inp={"type": "Skin", "style": "@bv.Skin"})
    g.get("gti3", "TmpItem"); t3, w3 = content_tile(g, "t3", "@gti3.TmpItem", "@ssel.yes", "true", "false", "false", tt(g, "t3t", "Look_Skin"), kind="skin")
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
    g.set("sei", "TmpItem", inp={"TmpItem": make_item(g, "mei", "@fs.Array Element", "@ebr.Icon", slot="@fm.Array Element", kind="makeup")})
    g.set("smi", "TmpItem", inp={"TmpItem": make_item(g, "mmi", "@fs.Array Element", "@mbr.Icon", slot="@fm.Array Element", kind="makeup")})
    g.set("spi", "TmpItem", inp={"TmpItem": make_item(g, "mpi", "@fs.Array Element", "None", slot="@fm.Array Element", kind="makeup")})
    g.n("msel", "call_self", function="Is Look Selected", inp={"type": "@fm.Array Element", "style": "@fs.Array Element"})
    g.get("gti4", "TmpItem"); t4, w4 = content_tile(g, "t4", "@gti4.TmpItem", "@msel.yes", "true", "false", "false", "@mcap.caption", kind="makeup")
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
    t5, w5 = content_tile(g, "t5", "@mbi.S_ClothesItem", "@bcur.ReturnValue", "true", "false", "false", tt(g, "t5t", "Tab_Body"), kind="body")
    g.branch("bsl", "@bo2.ReturnValue")
    def pct(id, pin):
        g.call(id + "_m", K_MATH, "Multiply_FloatFloat", inp={"A": pin, "B": "100.0"}); g.call(id + "_r", K_MATH, "Round", inp={"A": "@%s_m.ReturnValue" % id})
        g.call(id, K_STR, "Conv_IntToString", inp={"InInt": "@%s_r.ReturnValue" % id}); return "@%s.ReturnValue" % id
    parts = [ts(g, "lb", "Lbl_Breast"), " ", pct("pb", "@bv.Boobs"), " % \u00b7 ", ts(g, "lw", "Lbl_Waist"), " ", pct("pw", "@bv.Waist"), " %"]
    acc = parts[0]
    for i, p in enumerate(parts[1:]):
        g.call("nc%d" % i, K_STR, "Concat_StrStr", inp={"A": acc, "B": p}); acc = "@nc%d.ReturnValue" % i
    # second line: bone-scale factors ("Bust x1.20 · Hips / glutes x1.00 · ...") when the snapshot carries all six
    def fac(id, i):
        g.call(id + "_g", K_ARR, "Array_Get", inp={"TargetArray": "@bv.Scales", "Index": str(i)})
        g.call(id + "_t", K_TXT, "Conv_FloatToText", inp={"Value": "@%s_g.Item" % id, "MinimumFractionalDigits": "2", "MaximumFractionalDigits": "2"})
        g.call(id, K_TXT, "Conv_TextToString", inp={"InText": "@%s_t.ReturnValue" % id}); return "@%s.ReturnValue" % id
    sparts = []
    for i, (key, _) in enumerate(bg.SLIDERS):
        sparts += ([" \u00b7 "] if i else []) + [ts(g, "sl%d" % i, "Lbl_Sc" + key), " \u00d7", fac("sf%d" % i, i)]
    sacc = "\n"
    for i, p in enumerate(sparts):
        g.call("scc%d" % i, K_STR, "Concat_StrStr", inp={"A": sacc, "B": p}); sacc = "@scc%d.ReturnValue" % i
    g.call("bscl", K_ARR, "Array_Length", inp={"TargetArray": "@bv.Scales"}); g.call("bsc6", K_MATH, "EqualEqual_IntInt", inp={"A": "@bscl.ReturnValue", "B": str(bg.N_SLIDERS)})
    g.call("bscsel", K_MATH, "SelectString", inp={"A": sacc, "B": "", "bPickA": "@bsc6.ReturnValue"}); g.call("ncs", K_STR, "Concat_StrStr", inp={"A": acc, "B": "@bscsel.ReturnValue"}); acc = "@ncs.ReturnValue"
    g.call("nt", K_TXT, "Conv_StringToText", inp={"InString": acc}); g.get("gs5", "TmpSection"); g.call("sn5", W_SECTION, "Set Note", inp={"self": "@gs5.TmpSection", "text": "@nt.ReturnValue"})
    # exec chains
    g.get("gvm", "ViewMod"); g.call("vm", K_MATH, "NotEqual_NameName", inp={"A": "@gvm.ViewMod", "B": "None"}); g.branch("bvm", "@vm.ReturnValue"); g.n("rmc", "call_self", function="Rebuild Mod Content")
    g.chain("entry", "bvm", "rmc"); g.chain("bvm:else", "cs", "bok", "clc", "cll", "clk_cr", "sml", "li", "al", "sct", "bw"); g.chain("bok:else", "cc")
    g.chain("bw", *sec1, "fw"); g.chain("fw", "fi", "bfi", "sti", "idm", "tip", *t1, "bcf", "scs"); g.chain("bfi:else", "stp", "idm"); g.chain("fw:Completed", "bh"); g.chain("bw:else", "bh")
    g.chain("bh", *sec2, "hrow", "shi", *t2, "shc", "bsk"); g.chain("hrow:Row Not Found", "shp", t2[0]); g.chain("bh:else", "bsk")
    g.chain("bsk", *sec3, "srow", "ssi", "ssel", *t3, "mk"); g.chain("srow:Row Not Found", "ssp", "ssel"); g.chain("bsk:else", "mk")
    g.chain("mk", "fm"); g.chain("fm", "bml", "mcap", *sec4, "trow", "sey", "smln"); g.chain("trow:Row Not Found", "sey0", "smln"); g.chain("smln", "fs")
    g.chain("fs", "bey", "erow", "sei", "msel"); g.chain("erow:Row Not Found", "spi", "msel"); g.chain("bey:else", "mrow", "smi", "msel"); g.chain("mrow:Row Not Found", "spi"); g.chain("msel", *t4)
    g.chain("fm:Completed", "bb"); g.chain("bb", *sec5, "bbn", "scan", *t5, "bsl", "sn5"); g.chain("bbn:else", "bsl")
    return fn("Rebuild Content", graph=g)


def f_on_content_item_context():
    """Right click on a tile of the content view: Rename, "Show in tab" (only if the tile knows its origin slot), "Rename mod…" (mod piece) + Cancel."""
    g = G()
    g.get("glb", "LastButton"); g.cast("cb", W_BTN, "@glb.LastButton"); g.get("gsl", "ItemSlot", cls=W_BTN); g.link("cb.AsW_ClothesButton", "gsl.self")
    g.set("scs", "ContextSlot", inp={"ContextSlot": "@gsl.ItemSlot"})
    g.get("gm", "Menu"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gm.Menu"}); g.branch("b", "@iv.ReturnValue")
    mw = create_widget(g, "cm", W_MENU); g.set("sm", "Menu", inp={"Menu": mw}); set_manager(g, "smm", W_MENU, mw)
    g.get("gm2", "Menu"); g.call("clr", W_MENU, "Clear Rows", inp={"self": "@gm2.Menu"})
    g.get("gcs", "ContextSlot"); g.call("has", K_MATH, "NotEqual_NameName", inp={"A": "@gcs.ContextSlot", "B": "None"}); g.branch("bh", "@has.ReturnValue")
    r0 = menu_row(g, 0, "GoTo", tt(g, "t0", "Menu_ShowIn")); r1 = menu_row(g, 1, "Cancel", tt(g, "t1", "Menu_Cancel")); r2 = menu_row(g, 2, "Rename", tt(g, "t2", "Menu_Rename"))
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@entry.name"}); g.branch("bmd", "@imd.found")   # mod piece (any kind): rename the mod
    r3 = menu_row(g, 3, "RenameMod", tt(g, "t3", "Menu_RenameMod"))
    g.get("gm6", "Menu"); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@gm6.Menu", "ZOrder": "110"})
    g.call("mp", "/Script/UMG.WidgetLayoutLibrary", "GetMousePositionOnViewport")
    g.get("gm7", "Menu"); g.call("spv", E_USERWIDGET, "SetPositionInViewport", inp={"self": "@gm7.Menu", "Position": "@mp.ReturnValue", "bRemoveDPIScale": "false"})
    g.chain("entry", "scs", "b", "clr"); g.chain("b:else", "cm_cr", "sm", "smm", "clr")
    g.chain("clr", *r2, "bh", *r0, "bmd"); g.chain("bh:else", "bmd"); g.chain("bmd", *r3, r1[0]); g.chain("bmd:else", r1[0]); g.chain(*r1, "atv", "mp", "spv")
    return fn("On Content Item Context", [param("name", "name")], graph=g)


def f_go_to_item():
    """"Show in tab": jump from the content view to the piece's own page - ContextSlot = origin (Hair / Skin / <makeup type> / Body / clothes slot).
    Clothes: search cleared, a filter toggle that would hide the piece is switched off (like a click), slot + group chip (Hidden for hidden pieces,
    the piece's group when the slot has more than one, else All); the tile is highlighted and scrolled into view."""
    g = G(); g.get("gcs", "ContextSlot")
    # the jump target must be visible: close every content view (mod / outfit / look / preset) before switching the page
    g.set("cvm", "ViewMod", inp={"ViewMod": "None"}); g.set("cvo", "ViewOutfit", inp={"ViewOutfit": "-1"}); g.set("cvl", "ViewLook", inp={"ViewLook": "-1"}); g.set("cvp", "ViewPreset", inp={"ViewPreset": "-1"})
    g.call("isH", K_MATH, "EqualEqual_NameName", inp={"A": "@gcs.ContextSlot", "B": "Hair"}); g.branch("bH", "@isH.ReturnValue")
    g.set("hh", "HighlightItem", inp={"HighlightItem": "@entry.name"}); g.set("hk", "KeepHighlight", inp={"KeepHighlight": "true"})
    g.n("hsp", "call_self", function="Select Page", inp={"name": "Hair"}); g.n("hsc", "call_self", function="Scroll To Highlight")
    g.call("isB", K_MATH, "EqualEqual_NameName", inp={"A": "@gcs.ContextSlot", "B": "Body"}); g.branch("bB", "@isB.ReturnValue")
    g.n("bsp", "call_self", function="Select Page", inp={"name": "Body"})
    # appearance: Skin or a row of the makeup type table
    g.call("isS", K_MATH, "EqualEqual_NameName", inp={"A": "@gcs.ContextSlot", "B": "Skin"}); g.branch("bS", "@isS.ReturnValue")
    g.n("trow", "get_row", table=P_MTYPE_T, inp={"RowName": "@gcs.ContextSlot"})
    g.set("lc", "LookCat", inp={"LookCat": "@gcs.ContextSlot"}); g.set("lh", "HighlightItem", inp={"HighlightItem": "@entry.name"}); g.set("lk", "KeepHighlight", inp={"KeepHighlight": "true"})
    g.n("lih", "call_self", function="Is Look Hidden", inp={"name": "@entry.name"}); g.call("lgs", K_MATH, "SelectString", inp={"A": "Hidden", "B": "None", "bPickA": "@lih.yes"}); g.call("lgn", K_STR, "Conv_StringToName", inp={"InString": "@lgs.ReturnValue"})
    g.set("lg", "LookGroup", inp={"LookGroup": "@lgn.ReturnValue"})
    g.n("lif", "call_self", function="Is Look Favorite", inp={"name": "@entry.name"}); g.get("glof", "LookOnlyFav"); g.call("lnf", K_MATH, "BooleanAND", inp={"A": "@glof.LookOnlyFav", "B": "@lif.yes"}); g.set("slof", "LookOnlyFav", inp={"LookOnlyFav": "@lnf.ReturnValue"})
    g.get("gplf", "Panel"); g.get("glof2", "LookOnlyFav"); g.call("plof", W_PANEL, "Set Look Only Fav", inp={"self": "@gplf.Panel", "yes": "@glof2.LookOnlyFav"})
    g.set("lcs", "LookSearchText", inp={"LookSearchText": ""}); g.get("gpl", "Panel"); g.call("pls", W_PANEL, "Clear Look Search", inp={"self": "@gpl.Panel"})   # search cleared like on the clothes page
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
    g.chain("entry", "cvm", "cvo", "cvl", "cvp", "bH", "hh", "hk", "hsp", "hsc"); g.chain("bH:else", "bB", "bsp"); g.chain("bB:else", "bS", "lc"); g.chain("bS:else", "trow", "lc"); g.chain("lc", "lh", "lk", "lih", "lg", "lif", "slof", "plof", "lcs", "pls", "lsp", "lsc")
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
    # the height slider scales the mesh component: the slot's height above the feet scales with it, the zoom the other way (same framing)
    g.get("gcbh", "CurrentBody"); g.n("fach", "call_self", function="Body Scale Factors", inp={"name": "@gcbh.CurrentBody"})
    g.call("hfac", K_ARR, "Array_Get", inp={"TargetArray": "@fach.factors", "Index": str(bg.HEIGHT_INDEX)})
    g.call("h30s", K_MATH, "Multiply_FloatFloat", inp={"A": "@h30.ReturnValue", "B": "@hfac.Item"}); g.call("zooms", K_MATH, "Divide_FloatFloat", inp={"A": "@zoom.ReturnValue", "B": "@hfac.Item"})
    g.call("dz", K_MATH, "Subtract_FloatFloat", inp={"A": "@bml.Z", "B": "@bal.Z"}); g.call("z", K_MATH, "Add_FloatFloat", inp={"A": "@dz.ReturnValue", "B": "@h30s.ReturnValue"})
    g.set("sz", "FocusZ", inp={"FocusZ": "@z.ReturnValue"}); g.set("szm", "FocusZoom", inp={"FocusZoom": "@zooms.ReturnValue"}); g.set("stf", "TmpFloat", inp={"TmpFloat": "@zoom.ReturnValue"}); g.set("sti", "TmpI", inp={"TmpI": "@h.ReturnValue"})
    g.get("gpn", "PanToSlot"); g.get("gpo", "PanelOpen"); g.call("gt0", K_MATH, "Greater_IntInt", inp={"A": "@fc.code", "B": "0"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@gpn.PanToSlot", "B": "@gpo.PanelOpen"}); g.call("a2", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@gt0.ReturnValue"})
    g.set("son", "FocusOn", inp={"FocusOn": "@a2.ReturnValue"}); g.n("svs", "call_self", function="Set View Shift")
    g.chain("entry", "fc", "fach", "sz", "szm", "stf", "sti", "son", "svs"); return fn("Update Focus", graph=g)


# ---------------- Language: static panel texts, language choice ----------------
PANEL_STRINGS = [("search", "Lbl_Search"), ("onlyowned", "Lbl_OnlyOwned"), ("onlyfav", "Lbl_OnlyFav"), ("onlyvanilla", "Lbl_OnlyVanilla"), ("favorites", "Lbl_Favorites"), ("all", "Lbl_All"), ("listhint", "Lbl_ListHint"),
                 ("lookonlyfav", "Lbl_OnlyFav"), ("lookfavorites", "Lbl_Favorites"), ("lookall", "Lbl_All"),
                 ("worn", "Lbl_Worn"), ("inbag", "Lbl_InBag"), ("bagempty", "Lbl_BagEmpty"), ("breast", "Lbl_Breast"), ("waist", "Lbl_Waist"),
                 ("scbreast", "Lbl_ScBreast"), ("scwaist", "Lbl_ScWaist"), ("scglutes", "Lbl_ScGlutes"), ("scthighs", "Lbl_ScThighs"), ("sccalves", "Lbl_ScCalves"), ("scarms", "Lbl_ScArms"), ("schands", "Lbl_ScHands"), ("scfeet", "Lbl_ScFeet"), ("scheight", "Lbl_ScHeight"),
                 ("scroll", "Lbl_Scroll"), ("scale", "Lbl_Scale"), ("fov", "Lbl_Fov"), ("dist", "Lbl_Dist"), ("grouplen", "Lbl_GroupLen"), ("chiph", "Lbl_ChipH"), ("unlimited", "Lbl_Unlimited"), ("layout", "Lbl_Layout"),
                 ("language", "Lbl_Language"), ("placeholder", "Lbl_Placeholder"), ("pan", "Lbl_Pan"), ("nude", "Lbl_Nude"), ("merge", "Lbl_Merge"), ("mergemods", "Lbl_MergeMods"), ("tipnoprefix", "Lbl_TipNoPrefix"), ("tipnoids", "Lbl_TipNoIds"), ("conflicts", "Lbl_Conflicts"), ("conflictshint", "Lbl_ConflictsHint"), ("unowned", "Lbl_Unowned"), ("scalehint", "Lbl_ScaleHint"),
                 ("theme", "Lbl_Theme"), ("bgalpha", "Lbl_BgAlpha"), ("tilealpha", "Lbl_TileAlpha"), ("key", "Lbl_ToggleKey"), ("onlymods", "Lbl_OnlyMods"), ("casesens", "Lbl_CaseSens"), ("managesearch", "Lbl_Search"), ("looksearch", "Lbl_Search"), ("hdrname", "Lbl_HdrName"), ("hdrdisplay", "Lbl_HdrDisplay"), ("hdrorigin", "Lbl_HdrIds"), ("hdrcontent", "Btn_ModContent")]
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
    # bone-scale defaults of the body (/Game/Mod/<name>/Body_Scale, row Default); standard body / missing table -> all 1 (Apply Body Scales then finds no ABP or scales by 1)
    ones = {v: "(X=1,Y=1,Z=1)" for v, _, _ in bg.GROUPS}
    g.make("m1", S_BODYSCALE, **ones); g.set("sd1", "BodyDefaults", inp={"BodyDefaults": "@m1.S_BodyScale"})
    g.call("c3", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "/Body_Scale.Body_Scale"})
    g.call("sp2", K_SYS, "MakeSoftObjectPath", inp={"PathString": "@c3.ReturnValue"}); g.call("sr2", K_SYS, "Conv_SoftObjPathToSoftObjRef", inp={"SoftObjectPath": "@sp2.ReturnValue"})
    g.call("ld2", K_SYS, "LoadAsset_Blocking", inp={"Asset": "@sr2.ReturnValue"}); g.cast("ct", E_DATATABLE, "@ld2.ReturnValue", pure=False, miss="ignore")
    g.n("row", "get_row", inp={"DataTable": "@ct.AsData Table", "RowName": "Default"}, miss="ignore"); g.set("sdf", "BodyDefaults", inp={"BodyDefaults": "@row.ReturnValue"})
    g.n("abs", "call_self", function="Apply Body Scales")
    g.get("gpl2", "Player"); g.call("lpm", P_JODI, "Load Player Makeup", inp={"self": "@gpl2.Player"})
    g.get("gpl3", "Player"); g.call("rcp", P_CPB, "Reset Clothes Physics", inp={"self": "@gpl3.Player"})
    g.chain("entry", "bv", "bn", "sm1", "sc1", "ssm", "sd1", "ld2", "ct", "row", "sdf", "abs", "lpm", "rcp"); g.chain("bv:else", "sst", "bn")
    g.chain("bn:else", "ld", "ck", "sm2", "sc2", "ssm"); g.chain("ck:CastFailed", "pop", "sm3", "sc3", "ssm")
    g.chain("ct:CastFailed", "abs"); g.chain("row:Row Not Found", "abs")
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
    g.call("isr", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "BodyScReset"}); g.branch("br", "@isr.ReturnValue"); g.n("rsc", "call_self", function="Reset Body Scales")
    g.call("iss", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "BodyStd"}); g.branch("b", "@iss.ReturnValue")
    g.n("a0", "call_self", function="Apply Body", inp={"name": "None"}); g.n("a1", "call_self", function="Apply Body", inp={"name": "@entry.name"})
    g.get("gc", "CurrentBody"); g.set("sv", "BodyVariant", inp={"BodyVariant": "@gc.CurrentBody"})
    g.n("ss", "call_self", function="Save Settings"); g.n("rb", "call_self", function="Rebuild Body")
    g.chain("entry", "br", "rsc"); g.chain("br:else", "b", "a0", "sv", "ss", "rb"); g.chain("b:else", "a1", "sv")
    return fn("Select Body", [param("name", "name")], graph=g)


WEAR_WAIT_FIRST, WEAR_WAIT_NEXT = 9, 2   # ticks: ~0.15 s after the take-offs, then one piece every third frame


# ---------------- Bone-scale sliders (ABP_BodyScale post-process ABP attached by bodypak; defaults per body in Body_Scale) ----------------
SCALE_KEYS = [k.lower() for k, _ in bg.SLIDERS]


def add_floats(g, prefix, var, values):
    """Array_Clear + Array_Add of literal/pin values into a float array variable; returns the exec ids."""
    g.get(prefix + "g", var); g.call(prefix + "cl", K_ARR, "Array_Clear", inp={"TargetArray": "@%sg.%s" % (prefix, var)}); ids = [prefix + "cl"]
    for i, v in enumerate(values):
        if not v.startswith("@"):
            v = g.lit_float("%sl%d" % (prefix, i), v)
        g.get("%sg%d" % (prefix, i), var); g.call("%sa%d" % (prefix, i), K_ARR, "Array_Add", inp={"TargetArray": "@%sg%d.%s" % (prefix, i, var), "NewItem": v}); ids.append("%sa%d" % (prefix, i))
    return ids


def f_body_scale_factors():
    """Factors (N_SLIDERS) saved for a body; an array from before the waist slider (one entry short) gets a 1.0 appended, anything else
    missing / older -> all 1.0. Writes TmpFloats."""
    g = G()
    g.get("gm", "BodyScales"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gm.BodyScales", "Key": "@entry.name"})
    g.brk("bf", S_FLOATS, "@f.Value"); g.call("ln", K_ARR, "Array_Length", inp={"TargetArray": "@bf.Values"})
    g.call("eqn", K_MATH, "EqualEqual_IntInt", inp={"A": "@ln.ReturnValue", "B": str(bg.N_SLIDERS)}); g.call("ok", K_MATH, "BooleanAND", inp={"A": "@f.ReturnValue", "B": "@eqn.ReturnValue"}); g.branch("b", "@ok.ReturnValue")
    g.set("s1", "TmpFloats", inp={"TmpFloats": "@bf.Values"})
    g.call("eqp", K_MATH, "EqualEqual_IntInt", inp={"A": "@ln.ReturnValue", "B": str(bg.N_SLIDERS - 1)}); g.call("okp", K_MATH, "BooleanAND", inp={"A": "@f.ReturnValue", "B": "@eqp.ReturnValue"}); g.branch("bp", "@okp.ReturnValue")
    g.set("s2", "TmpFloats", inp={"TmpFloats": "@bf.Values"}); g.get("gp1", "TmpFloats"); g.call("pad", K_ARR, "Array_Add", inp={"TargetArray": "@gp1.TmpFloats", "NewItem": g.lit_float("padl", "1.0")})
    ids = add_floats(g, "d", "TmpFloats", ["1.0"] * bg.N_SLIDERS)   # missing or from an older layout -> all 1.0
    g.get("gr", "TmpFloats"); g.link("gr.TmpFloats", "return.factors")
    g.chain("entry", "b", "s1", "return"); g.chain("b:else", "bp", "s2", "pad", "return"); g.chain("bp:else", *ids, "return")
    return fn("Body Scale Factors", [param("name", "name")], outputs=[param("factors", "float", "array")], graph=g)


def f_vector_or_one():
    """A body's Body_Scale row from before a group was added leaves that member at (0,0,0) - treated as (1,1,1) (a scale of 0 is never meant)."""
    g = G(); g.call("sz", K_MATH, "VSize", inp={"A": "@entry.v"}); g.call("lt", K_MATH, "Less_FloatFloat", inp={"A": "@sz.ReturnValue", "B": "0.001"})
    g.call("one", K_MATH, "MakeVector", inp={"X": "1.0", "Y": "1.0", "Z": "1.0"}); g.call("sel", K_MATH, "SelectVector", inp={"A": "@one.ReturnValue", "B": "@entry.v", "bPickA": "@lt.ReturnValue"})
    g.link("sel.ReturnValue", "return.out")   # output must not share the input's name: cooked bytecode resolves properties by name (crash 2026-09-21)
    return fn("Vector Or One", [param("v", "struct:/Script/CoreUObject.Vector")], outputs=[param("out", "struct:/Script/CoreUObject.Vector")], graph=g, pure=True)


def f_set_body_scale_factors():
    """BodyScales[name] = factors (persisted via SETTINGS), then apply + save."""
    g = G()
    g.make("mk", S_FLOATS, Values="@entry.factors")
    g.get("gm", "BodyScales"); g.call("ma", K_MAP, "Map_Add", inp={"TargetMap": "@gm.BodyScales", "Key": "@entry.name", "Value": "@mk.S_Floats"})
    g.n("ap", "call_self", function="Apply Body Scales"); g.n("sv", "call_self", function="Save Settings"); g.n("uf", "call_self", function="Update Focus")
    g.chain("entry", "ma", "ap", "sv", "uf")
    return fn("Set Body Scale Factors", [param("name", "name"), param("factors", "float", "array")], graph=g)


def f_apply_body_scales():
    """GetPostProcessInstance -> ABP_BodyScale_C. Net scale per group = Default * per-axis (1 + w * (f - 1)) with f = its slider's factor and
    w = bodyscale_groups.AXES (1 = full factor, 0 = untouched, else a Lerp); Default via Vector Or One (older Body_Scale rows); a modified bone's
    children inherit the change, so each node gets net(group) / net(parent group) (bodyscale_groups.PARENT_GROUP) - "Calves x1.00" then
    really leaves the calves alone whatever the thighs do. Cast failed -> ScaleActive false (no sliders)."""
    g = G()
    g.get("gpl", "Player"); g.get("gmc", "Mesh", cls=E_CHARACTER); g.link("gpl.Player", "gmc.self")
    g.get("gcb", "CurrentBody"); g.n("fac", "call_self", function="Body Scale Factors", inp={"name": "@gcb.CurrentBody"})
    slider_of = {v: si for si, (_, vars_) in enumerate(bg.SLIDERS) for v in vars_}
    for si in range(len(bg.SLIDERS)):
        g.call("fg%d" % si, K_ARR, "Array_Get", inp={"TargetArray": "@fac.factors", "Index": str(si)})
    # height: the whole mesh component (origin at the feet) - also for the standard body, no ABP involved
    hi = bg.HEIGHT_INDEX
    g.call("hv", K_MATH, "MakeVector", inp={"X": "@fg%d.Item" % hi, "Y": "@fg%d.Item" % hi, "Z": "@fg%d.Item" % hi})
    g.call("srs", E_SCENECOMP, "SetRelativeScale3D", inp={"self": "@gmc.Mesh", "NewScale3D": "@hv.ReturnValue"})
    # a changed scale: physics bodies and constraints (breast / hip jiggle, anchored in cm on spine_02) are only rebuilt with the new scale by a
    # re-init of the physics state -> Set Physics Asset(force), then switch the jiggle back on the way the game does it
    g.get("glh", "LastHeight"); g.call("hne", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@glh.LastHeight", "B": "@fg%d.Item" % hi, "ErrorTolerance": "0.0001"}); g.branch("bh", "@hne.ReturnValue")
    g.set("slh", "LastHeight", inp={"LastHeight": "@fg%d.Item" % hi})
    g.get("gskm", "SkeletalMesh", cls=E_SKINNED); g.link("gmc.Mesh", "gskm.self"); g.get("gpa", "PhysicsAsset", cls=E_SKELMESH); g.link("gskm.SkeletalMesh", "gpa.self")
    g.call("spa", E_SKINNED, "SetPhysicsAsset", inp={"self": "@gmc.Mesh", "NewPhysicsAsset": "@gpa.PhysicsAsset", "bForceReInit": "true"})
    g.get("gplb", "Player"); g.call("ebp", P_CB, "Enable Boobs Physics", inp={"self": "@gplb.Player", "hip": "true"})
    g.get("gplc", "Player"); g.get("gbm", "Breast Morph Weight", cls=P_CPB); g.link("gplc.Player", "gbm.self")
    g.get("gpld", "Player"); g.call("cbc", P_CPB, "Change Breast Constraint Profile", inp={"self": "@gpld.Player", "morph": "@gbm.Breast Morph Weight"})
    g.call("ppi", E_SKELMESHCOMP, "GetPostProcessInstance", inp={"self": "@gmc.Mesh"}); g.cast("ck", P_ABP, "@ppi.ReturnValue", pure=False)
    g.set("sa0", "ScaleActive", inp={"ScaleActive": "false"}); g.set("sa1", "ScaleActive", inp={"ScaleActive": "true"})
    g.get("gd", "BodyDefaults"); g.brk("bd", S_BODYSCALE, "@gd.BodyDefaults")
    net = {}
    for v, _, _ in bg.GROUPS:
        si = slider_of[v]
        f = "@fg%d.Item" % si; comps = []
        for ai, w in enumerate(bg.AXES[v]):
            if w == 1: comps.append(f)
            elif w == 0: comps.append("1.0")
            else:
                g.call("lp_%s_%d" % (v, ai), K_MATH, "Lerp", inp={"A": "1.0", "B": f, "Alpha": str(float(w))}); comps.append("@lp_%s_%d.ReturnValue" % (v, ai))
        g.call("mv_" + v, K_MATH, "MakeVector", inp={"X": comps[0], "Y": comps[1], "Z": comps[2]})
        g.n("vo_" + v, "call_self", function="Vector Or One", inp={"v": "@bd." + v})
        g.call("net_" + v, K_MATH, "Multiply_VectorVector", inp={"A": "@vo_%s.out" % v, "B": "@mv_%s.ReturnValue" % v}); net[v] = "@net_%s.ReturnValue" % v
    chain = ["fac", "srs", "bh", "ck", "sa1"]; g.chain("bh:else", "slh", "spa", "ebp", "cbc", "ck")
    for v, _, _ in bg.GROUPS:
        pin = net[v]
        if v in bg.PARENT_GROUP:
            g.call("rel_" + v, K_MATH, "Divide_VectorVector", inp={"A": net[v], "B": net[bg.PARENT_GROUP[v]]}); pin = "@rel_%s.ReturnValue" % v
        g.n("set_" + v, "set", var=v, cls=P_ABP, inp={"self": "@ck.AsABP Body Scale", v: pin}); chain.append("set_" + v)
    # floor compensation (bodyscale_groups: root_shift / feet_shift): RootShift.Z = S (1 - 1/h), FeetShift.Z = A (f - 1) - component space
    fi = [k for k, _ in bg.SLIDERS].index("Feet")
    g.call("rs1", K_MATH, "Divide_FloatFloat", inp={"A": "1.0", "B": "@fg%d.Item" % hi}); g.call("rs2", K_MATH, "Subtract_FloatFloat", inp={"A": "1.0", "B": "@rs1.ReturnValue"})
    g.call("rs3", K_MATH, "Multiply_FloatFloat", inp={"A": str(bg.SOLE_BELOW_ORIGIN), "B": "@rs2.ReturnValue"}); g.call("rsv", K_MATH, "MakeVector", inp={"X": "0.0", "Y": "0.0", "Z": "@rs3.ReturnValue"})
    g.n("set_RootShift", "set", var="RootShift", cls=P_ABP, inp={"self": "@ck.AsABP Body Scale", "RootShift": "@rsv.ReturnValue"}); chain.append("set_RootShift")
    g.call("fs1", K_MATH, "Subtract_FloatFloat", inp={"A": "@fg%d.Item" % fi, "B": "1.0"}); g.call("fs2", K_MATH, "Multiply_FloatFloat", inp={"A": str(bg.ANKLE_TO_SOLE), "B": "@fs1.ReturnValue"})
    g.call("fsv", K_MATH, "MakeVector", inp={"X": "0.0", "Y": "0.0", "Z": "@fs2.ReturnValue"})
    g.n("set_FeetShift", "set", var="FeetShift", cls=P_ABP, inp={"self": "@ck.AsABP Body Scale", "FeetShift": "@fsv.ReturnValue"}); chain.append("set_FeetShift")
    g.chain("entry", *chain); g.chain("ck:CastFailed", "sa0")
    return fn("Apply Body Scales", graph=g)


def f_reset_body_scales():
    g = G(); ids = add_floats(g, "r", "TmpFloats", ["1.0"] * bg.N_SLIDERS)
    g.get("gcb", "CurrentBody"); g.get("gtf", "TmpFloats"); g.n("sf", "call_self", function="Set Body Scale Factors", inp={"name": "@gcb.CurrentBody", "factors": "@gtf.TmpFloats"})
    g.n("rb", "call_self", function="Rebuild Body"); g.chain("entry", *ids, "sf", "rb")
    return fn("Reset Body Scales", graph=g)


def f_poll_body_scales():
    """Tick on the body page (after Poll Body): slider moved -> factors for CurrentBody, apply, save, refresh the value texts."""
    g = G(); g.get("gsa", "ScaleActive"); g.branch("ba", "@gsa.ScaleActive")
    g.get("gp", "Panel"); g.call("gv", W_PANEL, "Get Body Scales", inp={"self": "@gp.Panel"})
    same = None
    for i, k in enumerate(SCALE_KEYS):
        g.get("gc%d" % i, "BodyScaleVals"); g.call("ag%d" % i, K_ARR, "Array_Get", inp={"TargetArray": "@gc%d.BodyScaleVals" % i, "Index": str(i)})
        g.call("ne%d" % i, K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv." + k, "B": "@ag%d.Item" % i, "ErrorTolerance": "0.0001"})
        if same is None: same = "@ne0.ReturnValue"
        else: g.call("an%d" % i, K_MATH, "BooleanAND", inp={"A": same, "B": "@ne%d.ReturnValue" % i}); same = "@an%d.ReturnValue" % i
    g.branch("bs", same)
    ids = add_floats(g, "v", "BodyScaleVals", ["@gv." + k for k in SCALE_KEYS])
    for i, k in enumerate(SCALE_KEYS):
        lo, hi = bg.factor_range(bg.SLIDERS[i][0])
        g.call("m%d" % i, K_MATH, "Multiply_FloatFloat", inp={"A": "@gv." + k, "B": str(hi - lo)}); g.call("f%d" % i, K_MATH, "Add_FloatFloat", inp={"A": "@m%d.ReturnValue" % i, "B": str(lo)})
    ids += add_floats(g, "t", "TmpFloats", ["@f%d.ReturnValue" % i for i in range(bg.N_SLIDERS)])
    g.get("gcb", "CurrentBody"); g.get("gtf", "TmpFloats"); g.n("sf", "call_self", function="Set Body Scale Factors", inp={"name": "@gcb.CurrentBody", "factors": "@gtf.TmpFloats"})
    g.get("gp2", "Panel"); g.call("sv", W_PANEL, "Set Body Scales", inp=dict({"self": "@gp2.Panel"}, **{k: "@gv." + k for k in SCALE_KEYS}))
    g.chain("entry", "ba", "gv", "bs"); g.chain("bs:else", *ids, "sf", "sv")
    return fn("Poll Body Scales", graph=g)


def f_log_line():
    """Debug log to Saved/SaveGames/AltUI_Log.sav (a SaveGame with one FString per line; `strings AltUI_Log.sav` reads it) -
    Blueprints cannot write text files in a Shipping build and PrintString is compiled out. A new object per game session (first
    call), "<tick> <text>", at most LOG_MAX lines, written to disk on every call so the last line survives a crash. No caller in
    the release build; wire "Log Line" calls in temporarily when a problem needs tracing (see docs/specs 2026-09-19 Nachtrag)."""
    g = G()
    g.get("gl", "LogSave"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gl.LogSave"}); g.branch("b", "@iv.ReturnValue")
    g.call("cr", K_GS, "CreateSaveGameObject", inp={"SaveGameClass": SG_LOG}); g.cast("cc", SG_LOG, "@cr.ReturnValue"); g.set("sl", "LogSave", inp={"LogSave": "@cc.AsSG_Log"})
    g.get("gt", "TickCount"); g.call("ts", K_STR, "Conv_IntToString", inp={"InInt": "@gt.TickCount"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@ts.ReturnValue", "B": " "}); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@entry.text"})
    g.get("gl2", "LogSave"); g.get("ln", "Lines", cls=SG_LOG); g.link("gl2.LogSave", "ln.self")
    g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@ln.Lines", "NewItem": "@c2.ReturnValue"})
    g.get("gl3", "LogSave"); g.get("ln2", "Lines", cls=SG_LOG); g.link("gl3.LogSave", "ln2.self")
    g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@ln2.Lines"}); g.call("gtm", K_MATH, "Greater_IntInt", inp={"A": "@len.ReturnValue", "B": str(LOG_MAX)}); g.branch("bm", "@gtm.ReturnValue")
    g.call("rm", K_ARR, "Array_Remove", inp={"TargetArray": "@ln2.Lines", "IndexToRemove": "0"})
    g.get("gl4", "LogSave"); g.call("sv", K_GS, "SaveGameToSlot", inp={"SaveGameObject": "@gl4.LogSave", "SlotName": LOG_SLOT, "UserIndex": "0"})
    g.chain("entry", "b", "add", "bm", "rm", "sv"); g.chain("b:else", "cr", "sl", "add"); g.chain("bm:else", "sv")
    return fn("Log Line", [param("text", "string")], graph=g)


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
    g.n("lnm", "call_self", function="Load Names")   # before Build Catalog: display names carry the custom names
    # apply the saved body 1 s after BeginPlay (Jodi + mod paks are certainly there by then; the default mesh is remembered)
    g.self_("me"); g.call("tm", K_SYS, "K2_SetTimer", inp={"Object": "@me.self", "FunctionName": "Apply Saved Body", "Time": "1.0", "bLooping": "false"})
    g.self_("me3"); g.call("tmu", K_SYS, "K2_SetTimer", inp={"Object": "@me3.self", "FunctionName": "Fix Loaded Underwear", "Time": "1.5", "bLooping": "false"})
    g.n("dl", "call_self", function="Detect Language"); g.n("ist", "call_self", function="Init Strings"); g.n("apn", "call_self", function="Apply Nude")
    g.n("bga", "call_self", function="Build Group Aliases")   # Build Catalog ran before Load Settings: apply the loaded MergeGroups option
    g.n("bcf", "call_self", function="Build Conflicts")   # slot conflict pairs from ClothesTypeTable
    g.chain("bp", "cpc", "spc", "ei", "cj", "spl", "isg", "bcf", "lnm", "bc", "lds", "bga", "apn", "dl", "ist", "rs", "tm", "tmu")
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
    g.n("tct", "call_self", function="Cam Tick", inp={"dt": "@tick.DeltaSeconds"})   # free cam step / photo mode end detection
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
    g.get("tpl", "Panel"); g.call("tglf", W_PANEL, "Get Look Only Fav", inp={"self": "@tpl.Panel"}); g.get("tlof", "LookOnlyFav"); g.call("tlqn", K_MATH, "NotEqual_BoolBool", inp={"A": "@tglf.yes", "B": "@tlof.LookOnlyFav"}); g.branch("tlqb", "@tlqn.ReturnValue")
    g.set("tlqs", "LookOnlyFav", inp={"LookOnlyFav": "@tglf.yes"}); g.n("tlqv", "call_self", function="Save Settings"); g.n("tlqc", "call_self", function="Rebuild Look Cats"); g.n("tlqk", "call_self", function="Rebuild Look")
    g.get("tco2", "ColorOpen"); g.branch("tbc", "@tco2.ColorOpen"); g.n("tap", "call_self", function="Apply Preview")
    g.get("tpg", "Page"); g.call("tib", K_MATH, "EqualEqual_NameName", inp={"A": "@tpg.Page", "B": "Body"}); g.branch("tbb", "@tib.ReturnValue"); g.n("tpb", "call_self", function="Poll Body"); g.n("tpbs", "call_self", function="Poll Body Scales")
    g.get("tpg2", "Page"); g.call("tio", K_MATH, "EqualEqual_NameName", inp={"A": "@tpg2.Page", "B": "Options"}); g.branch("tbo", "@tio.ReturnValue"); g.n("tpo2", "call_self", function="Poll Options")
    g.get("tpg3", "Page"); g.call("tim", K_MATH, "EqualEqual_NameName", inp={"A": "@tpg3.Page", "B": "Manage"}); g.branch("tbmg", "@tim.ReturnValue"); g.n("tpm", "call_self", function="Poll Manage")
    g.get("tif", "IconFrames"); g.call("tig", K_MATH, "Greater_IntInt", inp={"A": "@tif.IconFrames", "B": "0"}); g.branch("tbi", "@tig.ReturnValue")
    g.get("tif2", "IconFrames"); g.call("tid", K_MATH, "Subtract_IntInt", inp={"A": "@tif2.IconFrames", "B": "1"}); g.set("tis", "IconFrames", inp={"IconFrames": "@tid.ReturnValue"})
    g.get("tif3", "IconFrames"); g.call("tiz", K_MATH, "EqualEqual_IntInt", inp={"A": "@tif3.IconFrames", "B": "0"}); g.branch("tbz", "@tiz.ReturnValue"); g.n("tfi", "call_self", function="Finish Photo")
    g.n("twq", "call_self", function="Wear Queue Step")
    g.get("tkc", "TickCount"); g.call("tkc1", K_MATH, "Add_IntInt", inp={"A": "@tkc.TickCount", "B": "1"}); g.set("tkcs", "TickCount", inp={"TickCount": "@tkc1.ReturnValue"})   # frame counter (Log Line prefix)
    # tile rename field: poll the tile for focus loss (cancel); forget it once the field is closed
    g.get("trnt", "RenameTile"); g.cast("trc", W_BTN, "@trnt.RenameTile"); g.call("trv", K_SYS, "IsValid", inp={"Object": "@trc.AsW_ClothesButton"}); g.branch("tbr", "@trv.ReturnValue")
    g.call("tpr", W_BTN, "Poll Rename", inp={"self": "@trc.AsW_ClothesButton"}); g.branch("tba", "@tpr.active"); g.set("trs", "RenameTile", inp={"RenameTile": "None"})
    g.chain("tick", "tct", "tkcs", "twq", "tbr", "tpr", "tba", "tbi"); g.chain("tba:else", "trs", "tbi"); g.chain("tbr:else", "tbi"); g.chain("tbi", "tis", "tbz", "tfi", "tb0"); g.chain("tbz:else", "tb0"); g.chain("tbi:else", "tb0")
    g.get("tpx", "Panel"); g.call("tsc", W_PANEL, "Sync Check Size", inp={"self": "@tpx.Panel"})
    g.chain("tb0", "tsc", "tbb"); g.chain("tbb", "tpb", "tpbs", "tb1"); g.chain("tbb:else", "tbo", "tpo2", "tb1"); g.chain("tbo:else", "tbmg", "tpm", "tb1"); g.chain("tbmg:else", "tb1"); g.chain("tb1", "trlf", "trl", "tsv"); g.chain("tb0:else", "tbc", "tap"); g.chain("tb1:else", "tlqb", "tlqs", "tlqv", "tlqc", "tlqk", "tbc"); g.chain("tlqb:else", "tbc")
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
    g.custom("tga", "Test Group Alias", [param("group", "name")]); g.n("tga_a", "call_self", function="Group Alias", inp={"group": "@tga.group"}); g.set("tga_s", "TmpName", inp={"TmpName": "@tga_a.alias"}); g.chain("tga", "tga_s")
    g.custom("tc", "Test Group Caption", [param("group", "name")]); g.n("tc_c", "call_self", function="Group Caption", inp={"group": "@tc.group"})
    g.set("tc_s", "TmpText", inp={"TmpText": "@tc_c.caption"}); g.chain("tc", "tc_c", "tc_s")
    g.custom("ttf", "Test Toggle Fav", [param("name", "name")]); g.n("ttf_t", "call_self", function="Toggle Favorite", inp={"name": "@ttf.name"}); g.chain("ttf", "ttf_t")
    g.custom("tth", "Test Toggle Hidden", [param("name", "name")]); g.n("tth_t", "call_self", function="Toggle Item Hidden", inp={"name": "@tth.name"}); g.chain("tth", "tth_t")
    # ownership options (tests/editor/test_ownership.py): OwnedSet entry on/off, Can Wear / Shown Owned -> TmpBool
    g.custom("tso", "Test Set Owned", [param("name", "name"), param("yes", "bool")]); g.branch("tso_b", "@tso.yes")
    g.get("tso_g1", "OwnedSet"); g.call("tso_a", K_SET, "Set_Add", inp={"TargetSet": "@tso_g1.OwnedSet", "NewItem": "@tso.name"})
    g.get("tso_g2", "OwnedSet"); g.call("tso_r", K_SET, "Set_Remove", inp={"TargetSet": "@tso_g2.OwnedSet", "Item": "@tso.name"})
    g.chain("tso", "tso_b", "tso_a"); g.chain("tso_b:else", "tso_r")
    g.custom("tcw", "Test Can Wear", [param("name", "name")]); g.n("tcw_c", "call_self", function="Can Wear", inp={"name": "@tcw.name"}); g.set("tcw_s", "TmpBool", inp={"TmpBool": "@tcw_c.yes"}); g.chain("tcw", "tcw_c", "tcw_s")
    g.custom("tsho", "Test Shown Owned", [param("name", "name")]); g.n("tsho_c", "call_self", function="Shown Owned", inp={"name": "@tsho.name"}); g.set("tsho_s", "TmpBool", inp={"TmpBool": "@tsho_c.yes"}); g.chain("tsho", "tsho_s")
    g.custom("tst2", "Test Set Toggles", [param("owned", "bool"), param("fav", "bool")])
    g.set("tst2_o", "CachedOnlyOwned", inp={"CachedOnlyOwned": "@tst2.owned"}); g.set("tst2_f", "CachedOnlyFav", inp={"CachedOnlyFav": "@tst2.fav"}); g.chain("tst2", "tst2_o", "tst2_f")
    g.custom("tss", "Test Save Settings"); g.n("tss_s", "call_self", function="Save Settings"); g.chain("tss", "tss_s")
    g.custom("tit", "Test Item Tip", [param("name", "name"), param("kind", "name"), param("category", "text")]); g.n("tit_f", "call_self", function="Find Item", inp={"name": "@tit.name"})
    g.call("tit_k", K_MATH, "EqualEqual_NameName", inp={"A": "@tit.kind", "B": "item"}); g.branch("tit_b", "@tit_k.ReturnValue")   # item: catalog entry; else a look item (name + display name)
    g.n("tit_t", "call_self", function="Item Tip", inp={"item": "@tit_f.item", "kind": "@tit.kind", "category": "@tit.category"}); g.set("tit_s", "TmpText", inp={"TmpText": "@tit_t.tip"})
    g.n("tit_dn", "call_self", function="Display Name", inp={"kind": "@tit.kind", "row": "@tit.name"}); g.make("tit_m", S_ITEM, Name="@tit.name", DisplayName="@tit_dn.s")
    g.n("tit_t2", "call_self", function="Item Tip", inp={"item": "@tit_m.S_ClothesItem", "kind": "@tit.kind", "category": "@tit.category"}); g.set("tit_s2", "TmpText", inp={"TmpText": "@tit_t2.tip"})
    g.chain("tit", "tit_f", "tit_b", "tit_t", "tit_s"); g.chain("tit_b:else", "tit_t2", "tit_s2")
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
    g.custom("tmr", "Test Manage Rows", [param("cat", "name"), param("search", "string"), param("onlyMods", "bool")])
    g.n("tmr_r", "call_self", function="Manage Rows", inp={"cat": "@tmr.cat", "search": "@tmr.search", "onlyMods": "@tmr.onlyMods"}); g.set("tmr_s", "TmpStrings2", inp={"TmpStrings2": "@tmr_r.keys"}); g.chain("tmr", "tmr_r", "tmr_s")
    g.custom("tspg", "Test Select Page", [param("name", "name")]); g.n("tspg_s", "call_self", function="Select Page", inp={"name": "@tspg.name"}); g.chain("tspg", "tspg_s")
    g.custom("tomc", "Test Open Mod Content", [param("name", "name")]); g.n("tomc_c", "call_self", function="Open Mod Content Of Item", inp={"name": "@tomc.name"}); g.chain("tomc", "tomc_c")
    g.custom("tsog", "Test Show Only Group", [param("name", "name")]); g.n("tsog_c", "call_self", function="Show Only Group", inp={"name": "@tsog.name"}); g.chain("tsog", "tsog_c")
    g.custom("tths", "Test Toggle Hair Swatches"); g.n("tths_c", "call_self", function="Toggle Hair Swatches"); g.chain("tths", "tths_c")
    g.custom("tswc", "Test Swatch Color", [param("key", "name")]); g.n("tswc_c", "call_self", function="Swatch Color", inp={"key": "@tswc.key"})
    g.set("tswc_b", "TmpBool", inp={"TmpBool": "@tswc_c.found"}); g.set("tswc_s", "ColorCur", inp={"ColorCur": "@tswc_c.color"}); g.chain("tswc", "tswc_c", "tswc_b", "tswc_s")
    g.custom("tldn", "Test Load Names"); g.n("tldn_l", "call_self", function="Load Names"); g.chain("tldn", "tldn_l")
    g.custom("tscn", "Test Set Custom Name", [param("kind", "name"), param("row", "name"), param("name", "string")]); g.n("tscn_c", "call_self", function="Set Custom Name", inp={"kind": "@tscn.kind", "row": "@tscn.row", "name": "@tscn.name"}); g.chain("tscn", "tscn_c")
    g.custom("tcn", "Test Custom Name", [param("kind", "name"), param("row", "name")]); g.n("tcn_c", "call_self", function="Custom Name", inp={"kind": "@tcn.kind", "row": "@tcn.row"})
    g.set("tcn_b", "TmpBool", inp={"TmpBool": "@tcn_c.found"}); g.set("tcn_s", "TmpStr2", inp={"TmpStr2": "@tcn_c.name"}); g.chain("tcn", "tcn_b", "tcn_s")
    g.custom("tmcn", "Test Manage Count", [param("cat", "name")]); g.n("tmcn_c", "call_self", function="Manage Count", inp={"cat": "@tmcn.cat", "search": ""}); g.call("tmcn_k", K_MATH, "Conv_IntToInt64", inp={"InInt": "@tmcn_c.n"}); g.set("tmcn_s", "TmpKey", inp={"TmpKey": "@tmcn_k.ReturnValue"}); g.chain("tmcn", "tmcn_c", "tmcn_s")
    g.custom("tmsc", "Test Manage Sub Counts", [param("cat", "name"), param("search", "string"), param("filtered", "bool")]); g.n("tmsc_c", "call_self", function="Manage Sub Counts", inp={"cat": "@tmsc.cat", "search": "@tmsc.search", "filtered": "@tmsc.filtered"}); g.chain("tmsc", "tmsc_c")
    g.custom("tsmc", "Test Select Manage Cat", [param("name", "name")]); g.n("tsmc_c", "call_self", function="Select Manage Cat", inp={"name": "@tsmc.name"}); g.chain("tsmc", "tsmc_c")
    g.custom("tbcf", "Test Build Conflicts"); g.n("tbcf_c", "call_self", function="Build Conflicts"); g.chain("tbcf", "tbcf_c")
    g.custom("tcfw", "Test Conflicts With", [param("a", "name"), param("b", "name")]); g.n("tcfw_c", "call_self", function="Conflicts With", inp={"a": "@tcfw.a", "b": "@tcfw.b"}); g.set("tcfw_s", "TmpBool", inp={"TmpBool": "@tcfw_c.yes"}); g.chain("tcfw", "tcfw_s")
    g.custom("tcff", "Test Is Freed", [param("a", "name"), param("b", "name")]); g.n("tcff_c", "call_self", function="Is Freed", inp={"a": "@tcff.a", "b": "@tcff.b"}); g.set("tcff_s", "TmpBool", inp={"TmpBool": "@tcff_c.yes"}); g.chain("tcff", "tcff_s")
    g.custom("tcfs", "Test Set Freed", [param("a", "name"), param("b", "name"), param("freed", "bool")]); g.n("tcfs_c", "call_self", function="Set Freed", inp={"a": "@tcfs.a", "b": "@tcfs.b", "freed": "@tcfs.freed"}); g.chain("tcfs", "tcfs_c")
    g.custom("tcfc", "Test Conflicting Slots", [param("slot", "name"), param("worn", "name", "array")]); g.n("tcfc_c", "call_self", function="Conflicting Slots", inp={"slot": "@tcfc.slot", "worn": "@tcfc.worn"}); g.set("tcfc_s", "TmpNames", inp={"TmpNames": "@tcfc_c.slots"}); g.chain("tcfc", "tcfc_c", "tcfc_s")
    g.custom("trk", "Test Rename Kind", [param("name", "name")]); g.n("trk_k", "call_self", function="Rename Kind", inp={"name": "@trk.name"}); g.set("trk_s", "TmpName", inp={"TmpName": "@trk_k.kind"}); g.chain("trk", "trk_k", "trk_s")
    g.custom("tfr", "Test Finish Item Rename", [param("name", "name"), param("text", "string")]); g.n("tfr_f", "call_self", function="Finish Item Rename", inp={"name": "@tfr.name", "text": "@tfr.text"}); g.chain("tfr", "tfr_f")
    g.custom("tmrn", "Test Manage Rename", [param("kind", "name"), param("row", "name"), param("cat", "name")]); g.n("tmrn_m", "call_self", function="Manage Rename", inp={"kind": "@tmrn.kind", "row": "@tmrn.row", "cat": "@tmrn.cat"}); g.chain("tmrn", "tmrn_m")
    g.custom("trg", "Test Rename Group Of Item", [param("name", "name")]); g.n("trg_r", "call_self", function="Rename Group Of Item", inp={"name": "@trg.name"}); g.chain("trg", "trg_r")
    g.custom("tmo", "Test Manage Origin", [param("kind", "name"), param("row", "name")]); g.n("tmo_o", "call_self", function="Manage Origin", inp={"kind": "@tmo.kind", "row": "@tmo.row"})
    g.set("tmo_s", "TmpText", inp={"TmpText": "@tmo_o.origin"}); g.set("tmo_m", "TmpMod", inp={"TmpMod": "@tmo_o.mod"}); g.call("tmo_r2s", K_TXT, "Conv_TextToString", inp={"InText": "@tmo_o.rest"}); g.set("tmo_r", "TmpRest", inp={"TmpRest": "@tmo_r2s.ReturnValue"}); g.chain("tmo", "tmo_o", "tmo_s", "tmo_m", "tmo_r")
    # Test Legacy Save: write a save like before the versioning (SaveVersion 0, floats 0 = never set, key unset) - SG properties are not editable from Python
    g.custom("tlg", "Test Legacy Save"); tail = ["tlg"]
    for name, val in (("SaveVersion", "0"), ("CamDist", "0.0"), ("ScrollMult", "0.0"), ("ToggleKey", "None")):
        g.get("tlg_g" + name, "Settings"); g.n("tlg_s" + name, "set", var=name, cls=SG, inp={"self": "@tlg_g%s.Settings" % name, name: val}); tail.append("tlg_s" + name)
    g.get("tlg_gs", "Settings"); g.call("tlg_sv", K_GS, "SaveGameToSlot", inp={"SaveGameObject": "@tlg_gs.Settings", "SlotName": "AltUI", "UserIndex": "0"}); g.chain(*tail, "tlg_sv")
    g.custom("tlo", "Test Load Outfits"); g.n("tlo_l", "call_self", function="Load Outfits"); g.chain("tlo", "tlo_l")
    g.custom("tlky", "Test Look Key", [param("name", "name")]); g.n("tlky_c", "call_self", function="Look Key", inp={"name": "@tlky.name"}); g.set("tlky_s", "TmpName", inp={"TmpName": "@tlky_c.key"}); g.chain("tlky", "tlky_c", "tlky_s")
    g.custom("tlfv", "Test Toggle Look Favorite", [param("name", "name")]); g.n("tlfv_c", "call_self", function="Toggle Look Favorite", inp={"name": "@tlfv.name"}); g.chain("tlfv", "tlfv_c")
    g.custom("tlh", "Test Toggle Look Hidden", [param("name", "name")]); g.n("tlh_c", "call_self", function="Toggle Look Hidden", inp={"name": "@tlh.name"}); g.chain("tlh", "tlh_c")
    g.custom("tbga", "Test Build Group Aliases"); g.n("tbga_c", "call_self", function="Build Group Aliases"); g.chain("tbga", "tbga_c")
    g.custom("tmal", "Test Mod Alias", [param("mod", "name")]); g.n("tmal_c", "call_self", function="Mod Alias", inp={"mod": "@tmal.mod"}); g.set("tmal_s", "TmpName", inp={"TmpName": "@tmal_c.alias"}); g.chain("tmal", "tmal_s")
    g.custom("tslc", "Test Select Look Cat", [param("name", "name")]); g.n("tslc_c", "call_self", function="Select Look Cat", inp={"name": "@tslc.name"}); g.chain("tslc", "tslc_c")
    g.custom("tcr", "Test Collect Look Rows", [param("type", "name")]); g.n("tcr_c", "call_self", function="Collect Look Rows", inp={"type": "@tcr.type"}); g.chain("tcr", "tcr_c")
    g.custom("tlgr", "Test Look Groups"); g.n("tlgr_c", "call_self", function="Look Groups"); g.set("tlgr_s", "TmpNames", inp={"TmpNames": "@tlgr_c.groups"}); g.chain("tlgr", "tlgr_c", "tlgr_s")
    g.custom("tlt", "Test Look Type Of", [param("name", "name")]); g.n("tlt_c", "call_self", function="Look Type Of", inp={"name": "@tlt.name"}); g.set("tlt_s", "TmpName", inp={"TmpName": "@tlt_c.type"}); g.chain("tlt", "tlt_c", "tlt_s")
    g.custom("tlc", "Test Look Count", [param("type", "name"), param("filtered", "bool")]); g.n("tlc_c", "call_self", function="Look Count", inp={"type": "@tlc.type", "filtered": "@tlc.filtered"})
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
    # Test Free Cam Dir(keys, yaw) / Test Free Cam Clamp(c, t) -> TmpVector (free cam maths, tests/editor/test_freecam.py)
    g.custom("tfd", "Test Free Cam Dir", [param("keys", "int"), param("yaw", "float"), param("pitch", "float")])
    g.n("tfd_d", "call_self", function="Free Cam Dir", inp={"keys": "@tfd.keys", "yaw": "@tfd.yaw", "pitch": "@tfd.pitch"}); g.set("tfd_s", "TmpVector", inp={"TmpVector": "@tfd_d.dir"}); g.chain("tfd", "tfd_s")
    g.custom("tfm", "Test Free Cam Clamp", [param("cx", "float"), param("cy", "float"), param("cz", "float"), param("tx", "float"), param("ty", "float"), param("tz", "float")])
    g.call("tfm_c", K_MATH, "MakeVector", inp={"X": "@tfm.cx", "Y": "@tfm.cy", "Z": "@tfm.cz"}); g.call("tfm_t", K_MATH, "MakeVector", inp={"X": "@tfm.tx", "Y": "@tfm.ty", "Z": "@tfm.tz"})
    g.n("tfm_f", "call_self", function="Free Cam Clamp", inp={"center": "@tfm_c.ReturnValue", "target": "@tfm_t.ReturnValue"}); g.set("tfm_s", "TmpVector", inp={"TmpVector": "@tfm_f.v"}); g.chain("tfm", "tfm_s")
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
    g.custom("tbs", "Test Body Scales", [param("name", "name")]); g.n("tbs_f", "call_self", function="Body Scale Factors", inp={"name": "@tbs.name"})
    g.set("tbs_s", "TmpFloats", inp={"TmpFloats": "@tbs_f.factors"}); g.chain("tbs", "tbs_f", "tbs_s")
    g.custom("tvo", "Test Vector Or One", [param("v", "struct:/Script/CoreUObject.Vector")]); g.n("tvo_c", "call_self", function="Vector Or One", inp={"v": "@tvo.v"}); g.set("tvo_s", "TmpVector", inp={"TmpVector": "@tvo_c.out"}); g.chain("tvo", "tvo_s")
    g.custom("tbss", "Test Set Body Scales", [param("name", "name"), param("factors", "float", "array")]); g.make("tbss_mk", S_FLOATS, Values="@tbss.factors")
    g.get("tbss_g", "BodyScales"); g.call("tbss_a", K_MAP, "Map_Add", inp={"TargetMap": "@tbss_g.BodyScales", "Key": "@tbss.name", "Value": "@tbss_mk.S_Floats"}); g.chain("tbss", "tbss_a")
    g.custom("tgt", "Test Go To", [param("name", "name"), param("slot", "name")]); g.set("tgt_s", "ContextSlot", inp={"ContextSlot": "@tgt.slot"})
    g.n("tgt_g", "call_self", function="Go To Item", inp={"name": "@tgt.name"}); g.chain("tgt", "tgt_s", "tgt_g")
    return g


assets = [bp_cam_input(), blueprint(MGR, mode="augment", variables=[var("Panel", "object:" + W_PANEL), var("Menu", "object:" + W_MENU), var("TmpItems2", T_ITEM, "array"),
                               var("Palette", "object:" + P_PAL), var("ColorItem", "name"), var("ColorOrig", S_LINCOLOR), var("ColorCur", S_LINCOLOR), var("ColorOpen", "bool"),
                               var("OptBgAlpha", "float"), var("OptTileAlpha", "float"), var("TmpSection", "object:" + W_SECTION)],
                    functions=[f_open_color(), f_close_color(), f_apply_preview(), f_toggle(), f_open(), f_close(), f_rebuild_left(), f_rebuild_list(), f_rebuild_subtabs(), f_select_slot(),
                               f_take_off_slot(), f_on_item_clicked(), f_on_item_context(), f_close_menu(), f_on_menu_action(), f_select_subtab(), f_on_search_changed(),
                               f_load_outfits(), f_save_outfits(), f_rebuild_top_tabs(), f_select_page(), f_rebuild_catalog_if_dirty(), f_on_manage_search_changed(), f_name_matches(), f_manage_rows(), f_manage_count(), f_manage_sub_counts(), f_rebuild_manage_cats(), f_select_manage_cat(), f_manage_default(), f_manage_origin(), f_manage_icon(), f_rebuild_manage(), f_focus_name_row(), f_refresh_manage_rows(), f_manage_search_for(), f_rename_kind(), f_start_item_rename(), f_finish_item_rename(), f_refresh_after_rename(), f_manage_rename(), f_manage_go_to(), f_rename_mod_of_item(), f_rename_group_of_item(), f_rebuild_manage_links(), f_poll_manage(), f_show_only_group(), f_open_mod_content_of_item(), f_open_mod_content(), f_rebuild_mod_content(), f_on_look_item_context(), f_swatch_color(), f_rebuild_hair_swatches(), f_hair_swatch_clicked(), f_toggle_hair_swatches(), f_rebuild_outfits(), f_on_outfit_clicked(), f_on_outfit_context(), f_delete_outfit(),
                               f_in_bag(), f_can_wear(), f_is_damaged(), f_rebuild_bag(), f_bag_toggle_wear(), f_bag_remove(), f_bag_cleanup(), f_bag_all_worn(), f_bag_repair(), f_bag_to_wardrobe(), f_put_in_bag(), f_on_bag_item_context(),
                               f_rebuild_hair(), f_hair_clicked(), f_open_hair_color(), f_look_caption(), f_is_look_selected(), f_look_type_of(), f_look_key(), f_is_look_favorite(), f_is_look_hidden(), f_toggle_look_favorite(), f_toggle_look_hidden(), f_collect_look_rows(), f_look_row_passes(), f_look_groups(), f_look_chip_caption(), f_rebuild_look_chips(), f_select_look_group(), f_look_only_mod(), f_look_matches(), f_on_look_search_changed(), f_rebuild_look_links(), f_look_count(), f_rebuild_look_cats(), f_select_look_cat(),
                               f_rebuild_look(), f_look_clicked(), f_rebuild_body(), f_poll_body(), f_save_appearance_data(), f_scan_body_mods(), f_apply_body(), f_apply_saved_body(), f_select_body(),
                               f_apply_body_scales(), f_body_scale_factors(), f_vector_or_one(), f_set_body_scale_factors(), f_reset_body_scales(), f_poll_body_scales(), f_log_line(), f_apply_strings(), f_select_language(), f_focus_code(), f_update_focus(),
                               f_on_hair_context(), f_hair_reset_color(), f_clothes_reset_color(), f_open_theme_color(), f_apply_theme(), f_select_key(), f_apply_nude(), f_fix_loaded_underwear(), f_start_outfit_rename(), f_join_names(), f_outfit_key(), f_outfit_name_by_key(), f_outfit_name(), f_set_outfit_name_by_key(), f_set_outfit_name(), f_rebuild_options(), f_apply_options(), f_poll_options(),
                               f_load_presets(), f_preset_icon(), f_preset_index(), f_preset_clicked(), f_preset_add(), f_preset_delete(), f_on_preset_context(), f_capture_photo(), f_capture_preset_photo(), f_capture_look_photo(), f_finish_photo(), f_look_icon(),
                               f_load_looks(), f_save_looks(), f_looks_count(), f_add_look(), f_update_look(), f_delete_look(), f_look_name(), f_set_look_name(), f_apply_look(), f_rebuild_looks(), f_on_look_clicked(), f_on_look_context(), f_start_look_rename(),
                               f_select_layout(), f_rebuild_conflicts(), f_toggle_conflict(), f_free_slot(), f_free_all(), f_set_view_shift(), f_start_free_cam(), f_stop_free_cam(), f_free_cam_look(), f_free_cam_wheel(), f_free_cam_step(), f_start_photo_mode(), f_end_photo_mode(), f_cam_tick(), f_select_unowned(), f_rebuild_status(), f_take_snapshot(), f_push_history(), f_apply_snapshot(), f_wear_queue_step(), f_finish_apply_snapshot(), history_step("Undo", "UndoStack", "RedoStack"), history_step("Redo", "RedoStack", "UndoStack"),
                               f_content_open(), f_open_content(), f_content_snapshot(), open_content_wrapper("Open Outfit Content", "Outfit"), open_content_wrapper("Open Look Content", "Look"), open_content_wrapper("Open Preset Content", "Preset"), f_close_content(),
                               f_rebuild_content(), f_on_content_item_context(), f_go_to_item(), f_scroll_to_highlight()],
                    event_graph=event_graph())]
write(os.path.join(os.path.dirname(__file__), "..", "50_manager_ui.json"), assets)
