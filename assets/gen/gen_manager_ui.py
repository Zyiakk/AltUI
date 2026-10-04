"""Generates assets/50_manager_ui.json: UI bodies of the manager (augment) + event graph. Runs after 40_widgets.json."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
from bpdsl import *
import bodyscale_groups as bg
import weapon_skins as ws
import modui as mu
import face as fc
from gen_manager import S_PRESETCOL
from gen_manager import pop, text_from_str, S_ITEM, T_ITEM, S_COLSLOTS, S_MATS, MGR, S_SNAP, SG, S_LOOK, SG_LOOKS, LOOKS_SLOT, SG_LOG, LOG_SLOT, LOG_MAX
from strings import LANGS, LIST_CAP
from theme import THEME, DERIVED, BG_ALPHA, TILE_ALPHA
from gen_manager import S_THEMEP
from gen_textures import TAB_ICONS, T_ALTUI
from gen_manager import LAYOUTS, LAYOUT_FRACTIONS, BSEARCH_STEPS

W_ROW = M + "/W_MenuRow"; W_MENU = M + "/W_ContextMenu"
P_PAL = "/Game/Project/UserInterface/PaletteUI"; P_PALR = "/Game/Project/UserInterface/Widgets/Paletter"
W_TOP = M + "/W_TopTab"; W_OUTFIT = M + "/W_OutfitButton"; W_LOOK = M + "/W_LookButton"; W_SECTION = M + "/W_ContentSection"; W_VALROW = M + "/W_ValueRow"; W_TXT = M + "/W_TextButton"; T_UNDO = M + "/T_Undo"; T_REDO = M + "/T_Redo"; SC = 1.9; CAMMOD = M + "/CM_AltUICam"; OUTFIT_SLOT = "Outfits"
E_PCM = "/Script/Engine.PlayerCameraManager"; E_CAMA = "/Script/Engine.CameraActor"; E_CAMC = "/Script/Engine.CameraComponent"
W_PANEL = M + "/W_AltUI"; W_HEAD = M + "/W_GroupHeader"; W_TAB = M + "/W_SlotTab"; W_BTN = M + "/W_ClothesButton"; W_SUB = M + "/W_SubTab"; W_SWATCH = M + "/W_ColorSwatch"; W_NAMEROW = M + "/W_NameRow"; W_HSWATCH = M + "/W_HairSwatch"; W_CONFLICT = M + "/W_ConflictRow"


# ALTUI_WEAPONLOG=1 wires "Log Line" calls into the weapon-model path (Saved/SaveGames/AltUI_Log.sav, `strings` reads
# it): per component which original was remembered, which package was tried and whether it loaded. A Shipping build
# writes no log and PrintString is compiled out, so this is the only way to see it. Off in the pak that goes out.
WEAPONLOG = os.environ.get("ALTUI_WEAPONLOG") == "1"

# ALTUI_MAKEUPPROBE=1 builds a throwaway probe into the panel: when the panel opens, eight stripes in two colours are
# drawn into Jodi's make-up render target (Makeup Tex), the same target the game fills in Render Makeup Texture.
# It answers the one question static analysis cannot: does the skin shader read the COLOUR of that target, or only its
# mask? Stripes in two colours on Jodi -> colour arrives; stripes all alike (or none) -> only the mask is read.
# Never in a release build.
MAKEUPPROBE = os.environ.get("ALTUI_MAKEUPPROBE") == "1"

# ALTUI_TABLOG=1 measures every page change: "Select Page" becomes a wrapper that takes the accurate real time, runs the page change
# (then "Select Page Inner") and writes one log line "tab <page> <ms>" afterwards, so the log's own disk write is not measured.
# Used for the hidden-tabs comparison (docs/notes/2026-10-03-optionen-kategorien-reiter.md). Off in the pak that goes out.
TABLOG = os.environ.get("ALTUI_TABLOG") == "1"



def log(g, tag, parts):
    """A "Log Line" call node whose text is the concatenation of parts (literals and "@id.pin" expressions)."""
    expr = parts[0]
    for i, p in enumerate(parts[1:]):
        nid = "lc%s_%d" % (tag, i)
        g.call(nid, K_STR, "Concat_StrStr", inp={"A": expr, "B": p})
        expr = "@%s.ReturnValue" % nid
    return g.n("lg" + tag, "call_self", function="Log Line", inp={"text": expr})


def num(g, tag, int_expr):
    g.call("ns" + tag, K_STR, "Conv_IntToString", inp={"InInt": int_expr}); return "@ns%s.ReturnValue" % tag


def nstr(g, tag, name_expr):
    g.call("nm" + tag, K_STR, "Conv_NameToString", inp={"InName": name_expr}); return "@nm%s.ReturnValue" % tag


def oname(g, tag, obj_expr):
    g.call("ob" + tag, K_SYS, "GetObjectName", inp={"Object": obj_expr}); return "@ob%s.ReturnValue" % tag


def fnum(g, tag, float_expr):
    g.call("fs" + tag, K_STR, "Conv_FloatToString", inp={"InFloat": float_expr}); return "@fs%s.ReturnValue" % tag


def boolstr(g, tag, bool_expr):
    g.call("bs" + tag, K_STR, "Conv_BoolToString", inp={"InBool": bool_expr}); return "@bs%s.ReturnValue" % tag


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
    g.get("gp9", "Panel"); g.get("gco", "CachedOnlyOwned"); g.get("gcf", "CachedOnlyFav"); g.get("gcv", "CachedOnlyVanilla"); g.get("gcw", "CachedOnlyWorn")
    g.call("sft", W_PANEL, "Set Filter Toggles", inp={"self": "@gp9.Panel", "owned": "@gco.CachedOnlyOwned", "fav": "@gcf.CachedOnlyFav", "vanilla": "@gcv.CachedOnlyVanilla", "worn": "@gcw.CachedOnlyWorn"})
    g.get("gp9l", "Panel"); g.get("glof", "LookOnlyFav"); g.call("slof", W_PANEL, "Set Look Only Fav", inp={"self": "@gp9l.Panel", "yes": "@glof.LookOnlyFav"})
    g.get("gp9w", "Panel"); g.get("glow", "LookOnlyWorn"); g.call("slow", W_PANEL, "Set Look Only Worn", inp={"self": "@gp9w.Panel", "yes": "@glow.LookOnlyWorn"})
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
    g.n("sws", "call_self", function="Scan Weapon Skins"); g.n("swm", "call_self", function="Scan Weapon Models"); g.n("aws", "call_self", function="Apply All Weapon Looks")
    g.n("aicO", "call_self", function="Apply All Item Colors")   # own slot colours: the game only restores what its own flag covers
    g.n("aecO", "call_self", function="Apply Eye Colors")
    g.n("amcO", "call_self", function="Apply Makeup Colors")
    probe = ["mprobe"] if MAKEUPPROBE else []
    if MAKEUPPROBE: g.n("mprobe", "call_self", function="Makeup Probe")
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
    g.set("svo", "ViewOutfit", inp={"ViewOutfit": "-1"}); g.set("svl", "ViewLook", inp={"ViewLook": "-1"}); g.set("svp", "ViewPreset", inp={"ViewPreset": "-1"}); g.set("svf", "ViewFace", inp={"ViewFace": "-1"})   # content views end with the panel session
    g.get("gp5", "Panel"); g.call("spg", W_PANEL, "Set Page", inp={"self": "@gp5.Panel", "page": "Clothes"}); g.n("rtt", "call_self", function="Rebuild TopTabs")
    g.get("gp6", "Panel"); g.call("csl", W_PANEL, "Clear Search Links", inp={"self": "@gp6.Panel"})
    xw = create_widget(g, "cx", W_TXT); set_manager(g, "smx", W_TXT, xw)
    g.call("xt", K_TXT, "Conv_StringToText", inp={"InString": "\u00d7"}); g.call("xi", W_TXT, "Init", inp={"self": xw, "action": "ClearSearch", "caption": "@xt.ReturnValue"})
    g.get("gp7", "Panel"); g.call("asl", W_PANEL, "Add Search Link", inp={"self": "@gp7.Panel", "widget": xw})
    g.get("gp6c", "Panel"); g.call("cslc", W_PANEL, "Clear Chip Search Links", inp={"self": "@gp6c.Panel"})
    xc = create_widget(g, "cxc", W_TXT); set_manager(g, "smxc", W_TXT, xc)
    g.call("xtc", K_TXT, "Conv_StringToText", inp={"InString": "\u00d7"}); g.call("xic", W_TXT, "Init", inp={"self": xc, "action": "ClearChipSearch", "caption": "@xtc.ReturnValue"})
    g.get("gp7c", "Panel"); g.call("aslc", W_PANEL, "Add Chip Search Link", inp={"self": "@gp7c.Panel", "widget": xc})
    g.n("aps", "call_self", function="Apply Strings")
    g.get("gp8", "Panel"); g.call("ibt", W_PANEL, "Init Buttons", inp={"self": "@gp8.Panel"})   # +/- round buttons: manager, action, icon
    g.n("ath", "call_self", function="Apply Theme")
    # Jodi drag: remember the mesh rotation (Close Panel restores it), no drag running
    g.get("gplm", "Player"); g.get("gmcm", "Mesh", cls=E_CHARACTER); g.link("gplm.Player", "gmcm.self")
    g.get("grr", "RelativeRotation", cls=E_SCENECOMP); g.link("gmcm.Mesh", "grr.self")
    g.set("smr", "JodiMeshRot", inp={"JodiMeshRot": "@grr.RelativeRotation"}); g.set("sjd", "JodiDrag", inp={"JodiDrag": "false"})
    g.chain("entry", "b", "atv"); g.chain("b:else", "cw_cr", "sp", "sm", "sft", "slof", "slow", "ibt", "aps", "ath", "atv")
    g.chain("atv", "so", "smr", "sjd", "cur", "im", "bl", "epc", "rs"); g.chain("bl:else", "di", "rs")
    g.n("rst", "call_self", function="Rebuild Status")
    g.n("uf", "call_self", function="Update Focus")
    # the tab it was left on (kept in the settings): read before Page goes to Clothes, switched to once the clothes page is built;
    # a kept Mods tab without any registered mod, or a switched-off tab, opens the first tab the bar shows
    g.get("gpk", "Page"); g.set("sopk", "OpenPage", inp={"OpenPage": "@gpk.Page"})
    g.get("gop", "OpenPage")
    g.call("opm", K_MATH, "EqualEqual_NameName", inp={"A": "@gop.OpenPage", "B": "Mods"}); g.get("gmk", "ModEntryKeys")
    g.call("mkl", K_ARR, "Array_Length", inp={"TargetArray": "@gmk.ModEntryKeys"}); g.call("mke", K_MATH, "EqualEqual_IntInt", inp={"A": "@mkl.ReturnValue", "B": "0"})
    g.call("dead", K_MATH, "BooleanAND", inp={"A": "@opm.ReturnValue", "B": "@mke.ReturnValue"}); g.call("alive", K_MATH, "Not_PreBool", inp={"A": "@dead.ReturnValue"})
    # a switched-off tab (or a dead Mods tab) is not opened: the first tab the bar shows instead
    g.get("ghp", "HiddenTabs"); g.call("ohid", K_ARR, "Array_Contains", inp={"TargetArray": "@ghp.HiddenTabs", "ItemToFind": "@gop.OpenPage"}); g.call("onh", K_MATH, "Not_PreBool", inp={"A": "@ohid.ReturnValue"})
    g.call("okp", K_MATH, "BooleanAND", inp={"A": "@onh.ReturnValue", "B": "@alive.ReturnValue"}); g.branch("bokp", "@okp.ReturnValue")
    g.n("fvp", "call_self", function="First Visible Page"); g.set("sopf", "OpenPage", inp={"OpenPage": "@fvp.page"})
    g.get("gop3", "OpenPage"); g.call("opc2", K_MATH, "NotEqual_NameName", inp={"A": "@gop3.OpenPage", "B": "Clothes"}); g.branch("bop", "@opc2.ReturnValue")
    g.get("gop2", "OpenPage"); g.n("sel", "call_self", function="Select Page", inp={"name": "@gop2.OpenPage"})
    g.chain("uf", "bop", "sel"); g.chain("bokp:else", "sopf", "spo")
    # Clothes switched off: its page is not built (Select Page builds the tab that opens)
    g.get("ghc", "HiddenTabs"); g.call("chid", K_ARR, "Array_Contains", inp={"TargetArray": "@ghc.HiddenTabs", "ItemToFind": g.lit_name("lclo", "Clothes")}); g.branch("bclh", "@chid.ReturnValue")
    g.chain("rs", "sws", "swm", "aws", "aicO", "aecO", "amcO", *probe, "lo", "lp", "ao", "sopk", "bokp", "spo", "svo", "svl", "svp", "svf", "spg", "rtt", "rst", "csl", "cx_cr", "smx", "xi", "asl", "cslc", "cxc_cr", "smxc", "xic", "aslc", "bclh"); g.chain("bclh:else", "bs", "bsl", "scs", "rcd", "rl"); g.chain("bclh", "kf"); g.chain("bs:else", "rcd"); g.chain("bsl:else", "rcd"); g.chain("rcd", "rl", "rt", "rli", "kf", "uf")
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
    g.get("gsc9", "Scanning"); g.branch("bsc9", "@gsc9.Scanning"); g.n("sps9", "call_self", function="Stop Pose Scan")
    g.get("gcm", "CamMode"); g.call("is1", K_MATH, "EqualEqual_IntInt", inp={"A": "@gcm.CamMode", "B": "1"}); g.branch("bc1", "@is1.ReturnValue"); g.n("sfc", "call_self", function="Stop Free Cam")
    g.get("gcm2", "CamMode"); g.call("is2", K_MATH, "EqualEqual_IntInt", inp={"A": "@gcm2.CamMode", "B": "2"}); g.branch("bc2", "@is2.ReturnValue")
    g.call("gs", K_GS, "GetGameState"); g.cast("cgs", P_GS2, "@gs.ReturnValue", pure=False, miss="ignore"); g.call("xp", P_GS2, "Try Exit Photo Mode", inp={"self": "@cgs.AsTKA Game State"})
    g.set("so0", "PanelOpen", inp={"PanelOpen": "false"}); g.n("epm", "call_self", function="End Photo Mode")
    # Jodi drag: end it, put the mesh back (only if the panel was open - JodiMeshRot is unset otherwise)
    g.set("sjd", "JodiDrag", inp={"JodiDrag": "false"}); g.get("gpo", "PanelOpen"); g.branch("bpo", "@gpo.PanelOpen")
    g.get("gplm", "Player"); g.get("gmcm", "Mesh", cls=E_CHARACTER); g.link("gplm.Player", "gmcm.self"); g.get("gmr", "JodiMeshRot")
    g.call("srr", E_SCENECOMP, "K2_SetRelativeRotation", inp={"self": "@gmcm.Mesh", "NewRotation": "@gmr.JodiMeshRot", "bSweep": "false", "bTeleport": "true"})
    g.chain("entry", "sjd", "bpo", "srr", "bsc9", "sps9", "bc1", "sfc", "cmn"); g.chain("bsc9:else", "bc1"); g.chain("bpo:else", "bc1"); g.chain("bc1:else", "bc2", "cgs", "xp", "so0", "epm", "cmn"); g.chain("bc2:else", "cmn")
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
    g.get("gpw", "Panel"); g.call("ow", W_PANEL, "Get Only Worn", inp={"self": "@gpw.Panel"})
    g.get("gst", "SearchText"); g.call("sne", K_STR, "IsEmpty", inp={"InString": "@gst.SearchText"}); g.call("sact", K_MATH, "Not_PreBool", inp={"A": "@sne.ReturnValue"})
    g.call("fa1", K_MATH, "BooleanOR", inp={"A": "@oo.yes", "B": "@of.yes"}); g.call("fa2a", K_MATH, "BooleanOR", inp={"A": "@fa1.ReturnValue", "B": "@ov.yes"}); g.call("fa2", K_MATH, "BooleanOR", inp={"A": "@fa2a.ReturnValue", "B": "@ow.yes"})
    g.get("gcg0", "CurrentGroup"); g.call("gact", K_MATH, "NotEqual_NameName", inp={"A": "@gcg0.CurrentGroup", "B": "None"})   # a selected group chip filters too
    g.call("fact0", K_MATH, "BooleanOR", inp={"A": "@fa2.ReturnValue", "B": "@sact.ReturnValue"}); g.call("fact", K_MATH, "BooleanOR", inp={"A": "@fact0.ReturnValue", "B": "@gact.ReturnValue"}); g.set("sfa", "TmpBool", inp={"TmpBool": "@fact.ReturnValue"})
    g.get("gst2", "SearchText"); g.n("fc", "call_self", function="Filtered Counts", inp={"search": "@gst2.SearchText", "onlyOwned": "@oo.yes", "onlyFav": "@of.yes", "onlyVanilla": "@ov.yes", "onlyWorn": "@ow.yes"})
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
    g.get("gpw", "Panel"); g.call("ow", W_PANEL, "Get Only Worn", inp={"self": "@gpw.Panel"})
    g.set("co", "CachedOnlyOwned", inp={"CachedOnlyOwned": "@oo.yes"}); g.set("cf", "CachedOnlyFav", inp={"CachedOnlyFav": "@of.yes"}); g.set("cv", "CachedOnlyVanilla", inp={"CachedOnlyVanilla": "@ov.yes"}); g.set("cw", "CachedOnlyWorn", inp={"CachedOnlyWorn": "@ow.yes"})
    g.set("nf", "TmpIdx", inp={"TmpIdx": "0"})
    g.get("gcs", "CurrentSlot"); g.get("gcg", "CurrentGroup"); g.get("gst", "SearchText")
    g.n("it", "call_self", function="Filtered Items", inp={"slot": "@gcs.CurrentSlot", "group": "@gcg.CurrentGroup", "search": "@gst.SearchText", "onlyOwned": "@oo.yes", "onlyFav": "@of.yes", "onlyVanilla": "@ov.yes", "onlyWorn": "@ow.yes"})
    g.set("sti", "TmpItems2", inp={"TmpItems2": "@it.items"})
    # pass 1: favourites block
    g.get("gti", "TmpItems2"); g.foreach("ff", "@gti.TmpItems2"); g.brk("fb", S_ITEM, "@ff.Array Element")
    g.n("ffv", "call_self", function="Is Favorite", inp={"name": "@fb.Name"}); g.branch("fbr", "@ffv.yes")
    fw = create_widget(g, "cf1", W_BTN); set_manager(g, "smf", W_BTN, fw)
    g.n("fiw", "call_self", function="Is Worn", inp={"name": "@fb.Name"}); g.n("fio", "call_self", function="Shown Owned", inp={"name": "@fb.Name"})
    g.n("fdm", "call_self", function="Is Damaged", inp={"name": "@fb.Name"}); g.n("fti", "call_self", function="Item Tip", inp={"item": "@ff.Array Element", "kind": "item", "category": ""})
    g.call("fin", W_BTN, "Init", inp={"self": fw, "item": "@ff.Array Element", "worn": "@fiw.yes", "owned": "@fio.yes", "fav": "true", "damaged": "@fdm.yes", "tip": "@fti.tip", "dim": "false"})
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
    g.call("bin", W_BTN, "Init", inp={"self": bw, "item": "@fe.Array Element", "worn": "@iw.yes", "owned": "@io.yes", "fav": "@ifv.yes", "damaged": "@dm.yes", "tip": "@bti.tip", "dim": "false"})
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
    g.chain("entry", "cl", "clf", "co", "cf", "cv", "cw", "nf", "ci0", "it", "sti", "ff"); g.chain("ff", "fbr", "cf1_cr", "smf", "fdm", "fti", "fin", "af", "bhlf", "sswf", "sn"); g.chain("bhlf:else", "sn")
    g.chain("ff:Completed", "sfv", "fe"); g.chain("fe", "bcap", "cb_cr", "smb", "dm", "bti", "bin", "ai", "bhl", "ssw", "sci"); g.chain("bhl:else", "sci"); g.chain("fe:Completed", "slh")
    return fn("Rebuild List", graph=g)


def f_on_chip_search_changed():
    """Panel key-up: the chip search box -> ChipSearchText; rebuild only the chips when the text changed."""
    g = G(); g.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@entry.text"})
    g.get("gst", "ChipSearchText"); g.call("neq", K_STR, "NotEqual_StrStr", inp={"A": "@t2s.ReturnValue", "B": "@gst.ChipSearchText"}); g.branch("b", "@neq.ReturnValue")
    g.set("s", "ChipSearchText", inp={"ChipSearchText": "@t2s.ReturnValue"})
    g.n("rt", "call_self", function="Rebuild SubTabs")
    g.chain("entry", "b", "s", "rt")
    return fn("On Chip Search Changed", [param("text", "text")], graph=g)


def f_chip_shown():
    """Does Rebuild SubTabs show this group chip? The chip search has to match (an empty search matches everything) or it is
    the selected one; and the chip row has to be expanded, or there is text in the chip search (the search would otherwise do
    nothing while collapsed), or it is the selected one."""
    g = G()
    g.get("gcst", "ChipSearchText"); g.call("cse", K_STR, "IsEmpty", inp={"InString": "@gcst.ChipSearchText"}); g.call("csa", K_MATH, "Not_PreBool", inp={"A": "@cse.ReturnValue"})
    g.get("gcg", "CurrentGroup"); g.call("selG", K_MATH, "EqualEqual_NameName", inp={"A": "@gcg.CurrentGroup", "B": "@entry.group"})
    g.call("gcap", K_STR, "Conv_NameToString", inp={"InName": "@entry.group"})
    g.get("gcst2", "ChipSearchText"); g.n("cm", "call_self", function="Name Matches", inp={"kind": "group", "row": "@entry.group", "default": "@gcap.ReturnValue", "search": "@gcst2.ChipSearchText"})
    g.call("hit", K_MATH, "BooleanOR", inp={"A": "@cse.ReturnValue", "B": "@cm.yes"})
    g.call("hitS", K_MATH, "BooleanOR", inp={"A": "@hit.ReturnValue", "B": "@selG.ReturnValue"})
    g.get("gcol", "SubTabsCollapsed"); g.call("ncol", K_MATH, "Not_PreBool", inp={"A": "@gcol.SubTabsCollapsed"})
    g.call("open", K_MATH, "BooleanOR", inp={"A": "@ncol.ReturnValue", "B": "@csa.ReturnValue"})
    g.call("show0", K_MATH, "BooleanOR", inp={"A": "@open.ReturnValue", "B": "@selG.ReturnValue"})
    g.call("show", K_MATH, "BooleanAND", inp={"A": "@show0.ReturnValue", "B": "@hitS.ReturnValue"})
    g.link("show.ReturnValue", "return.yes")
    return fn("Chip Shown", [param("group", "name")], [param("yes", "bool")], graph=g, pure=True)


CHIP_LEAD = ("Basis", "Vanilla")   # stay first in a chip row (the game's own pieces), "Hidden" stays last


def f_sort_chips():
    """Chip row order: Basis / Vanilla first, then the groups / mods alphabetically by the name the chip shows (custom names included,
    Chip Caption for clothes groups, Look Chip Caption for mods), Hidden last. Sort keys and sorted insert by binary search as in the
    catalog (Build Catalog): the first 12 characters, then the next 12."""
    g = G()
    for v in ("SortOut", "SortHead", "SortTail", "SortK1", "SortK2"):
        g.get("c_" + v, v); g.call("cl_" + v, K_ARR, "Array_Clear", inp={"TargetArray": "@c_%s.%s" % (v, v)})
    g.foreach("fe", "@entry.groups")
    g.call("l0", K_MATH, "EqualEqual_NameName", inp={"A": "@fe.Array Element", "B": CHIP_LEAD[0]}); g.call("l1", K_MATH, "EqualEqual_NameName", inp={"A": "@fe.Array Element", "B": CHIP_LEAD[1]})
    g.call("lead", K_MATH, "BooleanOR", inp={"A": "@l0.ReturnValue", "B": "@l1.ReturnValue"}); g.branch("blead", "@lead.ReturnValue")
    g.get("gh", "SortHead"); g.call("addh", K_ARR, "Array_Add", inp={"TargetArray": "@gh.SortHead", "NewItem": "@fe.Array Element"})
    g.call("hid", K_MATH, "EqualEqual_NameName", inp={"A": "@fe.Array Element", "B": "Hidden"}); g.branch("bhid", "@hid.ReturnValue")
    g.get("gt", "SortTail"); g.call("addt", K_ARR, "Array_Add", inp={"TargetArray": "@gt.SortTail", "NewItem": "@fe.Array Element"})
    # the shown name, frozen (pure consumers would ask again per use)
    g.branch("blk", "@entry.look")
    g.n("lcc", "call_self", function="Look Chip Caption", inp={"group": "@fe.Array Element", "full": "true"}); g.call("lcs", K_TXT, "Conv_TextToString", inp={"InText": "@lcc.caption"})
    g.set("sl", "SortStr", inp={"SortStr": "@lcs.ReturnValue"})
    g.n("ccc", "call_self", function="Chip Caption", inp={"group": "@fe.Array Element", "full": "true"}); g.call("ccs", K_TXT, "Conv_TextToString", inp={"InText": "@ccc.caption"})
    g.set("sc", "SortStr", inp={"SortStr": "@ccs.ReturnValue"})
    g.get("gss", "SortStr"); g.n("k1", "call_self", function="Sort Key", inp={"s": "@gss.SortStr"}); g.set("sk1", "SortKey1", inp={"SortKey1": "@k1.key"})
    g.get("gss2", "SortStr"); g.call("sub2", K_STR, "GetSubstring", inp={"SourceString": "@gss2.SortStr", "StartIndex": "12", "Length": "12"})
    g.n("k2", "call_self", function="Sort Key", inp={"s": "@sub2.ReturnValue"}); g.set("sk2", "SortKey2", inp={"SortKey2": "@k2.key"})
    g.set("lo0", "SortLo", inp={"SortLo": "0"}); g.get("gk0", "SortK1"); g.call("klen", K_ARR, "Array_Length", inp={"TargetArray": "@gk0.SortK1"}); g.set("hi0", "SortHi", inp={"SortHi": "@klen.ReturnValue"})
    g.n("bs", "macro", name="ForLoop", inp={"First Index": "0", "Last Index": str(BSEARCH_STEPS - 1)})
    g.get("glo", "SortLo"); g.get("ghi", "SortHi"); g.call("open", K_MATH, "Less_IntInt", inp={"A": "@glo.SortLo", "B": "@ghi.SortHi"}); g.branch("bopen", "@open.ReturnValue")
    g.call("sum", K_MATH, "Add_IntInt", inp={"A": "@glo.SortLo", "B": "@ghi.SortHi"}); g.call("mid", K_MATH, "Divide_IntInt", inp={"A": "@sum.ReturnValue", "B": "2"})
    g.get("gk1", "SortK1"); g.call("kmid", K_ARR, "Array_Get", inp={"TargetArray": "@gk1.SortK1", "Index": "@mid.ReturnValue"})
    g.get("gk2", "SortK2"); g.call("k2mid", K_ARR, "Array_Get", inp={"TargetArray": "@gk2.SortK2", "Index": "@mid.ReturnValue"})
    g.get("gky", "SortKey1"); g.get("gky2", "SortKey2")
    g.call("lt", K_MATH, "Less_Int64Int64", inp={"A": "@gky.SortKey1", "B": "@kmid.Item"}); g.call("eq", K_MATH, "EqualEqual_Int64Int64", inp={"A": "@gky.SortKey1", "B": "@kmid.Item"})
    g.call("lt2", K_MATH, "Less_Int64Int64", inp={"A": "@gky2.SortKey2", "B": "@k2mid.Item"}); g.call("and2", K_MATH, "BooleanAND", inp={"A": "@eq.ReturnValue", "B": "@lt2.ReturnValue"})
    g.call("less", K_MATH, "BooleanOR", inp={"A": "@lt.ReturnValue", "B": "@and2.ReturnValue"}); g.branch("bless", "@less.ReturnValue")
    g.set("hi1", "SortHi", inp={"SortHi": "@mid.ReturnValue"}); g.call("mid1", K_MATH, "Add_IntInt", inp={"A": "@mid.ReturnValue", "B": "1"}); g.set("lo1", "SortLo", inp={"SortLo": "@mid1.ReturnValue"})
    g.get("gidx", "SortLo")
    g.get("go", "SortOut"); g.call("ins", K_ARR, "Array_Insert", inp={"TargetArray": "@go.SortOut", "NewItem": "@fe.Array Element", "Index": "@gidx.SortLo"})
    g.get("gi1", "SortK1"); g.get("gky3", "SortKey1"); g.call("ins1", K_ARR, "Array_Insert", inp={"TargetArray": "@gi1.SortK1", "NewItem": "@gky3.SortKey1", "Index": "@gidx.SortLo"})
    g.get("gi2", "SortK2"); g.get("gky4", "SortKey2"); g.call("ins2", K_ARR, "Array_Insert", inp={"TargetArray": "@gi2.SortK2", "NewItem": "@gky4.SortKey2", "Index": "@gidx.SortLo"})
    # head + sorted + tail
    g.get("gh2", "SortHead"); g.get("go2", "SortOut"); g.call("ap1", K_ARR, "Array_Append", inp={"TargetArray": "@gh2.SortHead", "SourceArray": "@go2.SortOut"})
    g.get("gh3", "SortHead"); g.get("gt2", "SortTail"); g.call("ap2", K_ARR, "Array_Append", inp={"TargetArray": "@gh3.SortHead", "SourceArray": "@gt2.SortTail"})
    g.get("gh4", "SortHead"); g.link("gh4.SortHead", "return.sorted")
    g.chain("entry", *["cl_" + v for v in ("SortOut", "SortHead", "SortTail", "SortK1", "SortK2")], "fe")
    g.chain("fe", "blead", "addh"); g.chain("blead:else", "bhid", "addt"); g.chain("bhid:else", "blk", "lcc", "sl", "k1")
    g.chain("blk:else", "ccc", "sc", "k1"); g.chain("k1", "sk1", "k2", "sk2", "lo0", "hi0", "bs")
    g.chain("bs", "bopen", "bless", "hi1"); g.chain("bless:else", "lo1"); g.chain("bs:Completed", "ins", "ins1", "ins2")
    g.chain("fe:Completed", "ap1", "ap2", "return")
    return fn("Sort Chips", [param("groups", "name", "array"), param("look", "bool")], [param("sorted", "name", "array")], graph=g)


def f_rebuild_subtabs():
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear SubTabs", inp={"self": "@gp.Panel"})
    g.get("gcs", "CurrentSlot"); g.n("gr0", "call_self", function="Groups Of Slot", inp={"slot": "@gcs.CurrentSlot"})
    g.n("srt", "call_self", function="Sort Chips", inp={"groups": "@gr0.groups", "look": "false"}); g.set("sco", "ChipOrder", inp={"ChipOrder": "@srt.sorted"})
    g.get("gco", "ChipOrder")
    g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@gco.ChipOrder"})
    g.call("gt1", K_MATH, "Greater_IntInt", inp={"A": "@len.ReturnValue", "B": "1"})
    g.get("gcsh", "ChipSearchShown"); g.call("csv", K_MATH, "BooleanAND", inp={"A": "@gt1.ReturnValue", "B": "@gcsh.ChipSearchShown"})
    g.get("gpcv", "Panel"); g.call("cvs", W_PANEL, "Set Chip Search Visible", inp={"self": "@gpcv.Panel", "visible": "@csv.ReturnValue"})
    g.branch("b", "@gt1.ReturnValue")
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
    g.get("gco2", "ChipOrder"); g.foreach("fe", "@gco2.ChipOrder")
    g.n("cs1", "call_self", function="Chip Shown", inp={"group": "@fe.Array Element"}); g.branch("bs", "@cs1.yes")
    sw = create_widget(g, "cs", W_SUB); set_manager(g, "sms", W_SUB, sw)
    g.get("gcol3", "SubTabsCollapsed"); g.call("fullc", K_MATH, "BooleanAND", inp={"A": "@gcol3.SubTabsCollapsed", "B": "@selG.ReturnValue"})
    g.n("cap", "call_self", function="Chip Caption", inp={"group": "@fe.Array Element", "full": "@fullc.ReturnValue"})
    g.get("gcg2", "CurrentGroup"); g.call("selG", K_MATH, "EqualEqual_NameName", inp={"A": "@gcg2.CurrentGroup", "B": "@fe.Array Element"})
    g.call("is", W_SUB, "Init", inp={"self": sw, "group": "@fe.Array Element", "caption": "@cap.caption", "selected": "@selG.ReturnValue"})
    g.get("gp3", "Panel"); g.call("as", W_PANEL, "Add SubTab", inp={"self": "@gp3.Panel", "widget": sw})
    g.chain("entry", "cl", "gr0", "srt", "sco", "cvs", "b", "ca_cr", "sma", "ia", "aa", "cm_cr", "smm", "im", "am", "fe"); g.chain("fe", "bs", "cs_cr", "sms", "cap", "is", "as")
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
    g.get("gpg3", "Page"); g.call("isw", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg3.Page", "B": "Weapons"}); g.branch("bpw", "@isw.ReturnValue")
    g.n("swp", "call_self", function="Select Weapon", inp={"name": "@entry.name"})
    g.get("gpg4", "Page"); g.call("isps2", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg4.Page", "B": "Poses"}); g.branch("bpps2", "@isps2.ReturnValue")
    g.n("spc", "call_self", function="Select Pose Cat", inp={"name": "@entry.name"})
    g.get("gpg5", "Page"); g.call("ismd", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg5.Page", "B": "Mods"}); g.branch("bpmd", "@ismd.ReturnValue")
    g.n("smd", "call_self", function="Select Mod Entry", inp={"name": "@entry.name"})
    g.get("gpg6", "Page"); g.call("isfg", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg6.Page", "B": "Face"}); g.branch("bpfg", "@isfg.ReturnValue")
    g.n("sfg", "call_self", function="Select Face Group", inp={"name": "@entry.name"})
    g.get("gpg7", "Page"); g.call("isop", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg7.Page", "B": "Options"}); g.branch("bpop", "@isop.ReturnValue")
    g.n("soc", "call_self", function="Select Option Cat", inp={"name": "@entry.name"})
    g.n("uf", "call_self", function="Update Focus")
    g.set("hlc", "HighlightItem", inp={"HighlightItem": "None"})
    g.chain("entry", "bpl", "slc"); g.chain("bpl:else", "bpm", "smc"); g.chain("bpm:else", "bpw", "swp"); g.chain("bpw:else", "bpps2", "spc"); g.chain("bpps2:else", "bpmd", "smd"); g.chain("bpmd:else", "bpfg", "sfg"); g.chain("bpfg:else", "bpop", "soc"); g.chain("bpop:else", "hlc", "s", "gr", "bk", "rl", "rt", "rli", "uf"); g.chain("bk:else", "sg", "rl"); return fn("Select Slot", [param("name", "name")], graph=g)


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
    g.get("gpg0", "Page"); g.n("cop", "call_self", function="Content Open", inp={"page": "@gpg0.Page"}); g.branch("bcv", "@cop.yes")   # content view: Content Item Clicked
    g.get("gpg", "Page"); g.call("isb", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Bag"}); g.branch("bpg", "@isb.ReturnValue")
    g.n("btw", "call_self", function="Bag Toggle Wear", inp={"name": "@entry.name"})
    g.get("gpg2", "Page"); g.call("ish", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg2.Page", "B": "Hair"}); g.branch("bph", "@ish.ReturnValue")
    g.n("hc", "call_self", function="Hair Clicked", inp={"name": "@entry.name"})
    g.get("gpg3", "Page"); g.call("isl", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg3.Page", "B": "Look"}); g.branch("bpl", "@isl.ReturnValue")
    g.n("lc", "call_self", function="Look Clicked", inp={"name": "@entry.name"})
    g.get("gpg4", "Page"); g.call("isps", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg4.Page", "B": "Poses"}); g.branch("bpps", "@isps.ReturnValue"); g.n("pc", "call_self", function="Pose Clicked", inp={"name": "@entry.name"})
    g.get("gpg5", "Page"); g.call("isw", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg5.Page", "B": "Weapons"}); g.branch("bpw", "@isw.ReturnValue"); g.n("wsc", "call_self", function="Weapon Tile Clicked", inp={"name": "@entry.name"})
    g.n("io", "call_self", function="Can Wear", inp={"name": "@entry.name"}); g.branch("bo", "@io.yes")   # owned, in the backpack, or option "not owned items" != locked
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"})
    g.call("msg", K_STR, "Concat_StrStr", inp={"A": ts(g, "mk", "Msg_NotOwned"), "B": "@n2s.ReturnValue"})
    pop(g, "pop", text_from_str(g, "t", "@msg.ReturnValue"))
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@entry.name"}); g.branch("bw", "@iw.yes")
    g.n("to", "call_self", function="Take Off", inp={"name": "@entry.name"}); g.n("we", "call_self", function="Wear", inp={"name": "@entry.name"})
    g.n("rl", "call_self", function="Rebuild Left"); g.n("rli", "call_self", function="Rebuild List")
    g.n("cic", "call_self", function="Content Item Clicked", inp={"name": "@entry.name"})
    g.chain("entry", "cop", "bcv", "cic"); g.chain("bcv:else", "bpg", "btw"); g.chain("bpg:else", "bph", "hc"); g.chain("bph:else", "bpps", "pc"); g.chain("bpps:else", "bpw", "wsc"); g.chain("bpw:else", "bpl", "lc")
    g.n("ph", "call_self", function="Push History")
    g.chain("bpl:else", "io", "bo", "ph", "bw", "to", "rl", "rli"); g.chain("bw:else", "we", "rl", "rli"); g.chain("bo:else", "pop")
    return fn("On Item Clicked", [param("name", "name")], graph=g)


def color_menu_rows(g, p, name_pin):
    """Context-menu rows for the colourable material slots of a piece: one row per slot, action "Color:<index>".
    With a single slot the row reads like before ("Colour..."), with several it names the slot. Returns the exec ids."""
    g.n(p + "_cs", "call_self", function="Item Color Slots", inp={"name": name_pin}); g.brk(p + "_b", S_COLSLOTS, "@%s_cs.slots" % p)
    g.call(p + "_len", K_ARR, "Array_Length", inp={"TargetArray": "@%s_b.Idx" % p})
    g.call(p + "_one", K_MATH, "EqualEqual_IntInt", inp={"A": "@%s_len.ReturnValue" % p, "B": "1"})
    g.foreach(p + "_fe", "@%s_b.Idx" % p)
    g.call(p + "_i2s", K_STR, "Conv_IntToString", inp={"InInt": "@%s_fe.Array Element" % p})
    g.call(p + "_ac1", K_STR, "Concat_StrStr", inp={"A": "Color:", "B": "@%s_i2s.ReturnValue" % p})
    g.call(p + "_acn", K_STR, "Conv_StringToName", inp={"InString": "@%s_ac1.ReturnValue" % p})
    g.call(p + "_cap", K_ARR, "Array_Get", inp={"TargetArray": "@%s_b.Caption" % p, "Index": "@%s_fe.Array Index" % p})
    g.call(p + "_caps", K_STR, "Conv_NameToString", inp={"InName": "@%s_cap.Item" % p})
    g.call(p + "_rep", K_STR, "Replace", inp={"SourceString": ts(g, p + "_slot", "Menu_ColorSlot"), "From": "%s", "To": "@%s_caps.ReturnValue" % p, "SearchCase": "CaseSensitive"})
    g.call(p + "_sel", K_MATH, "SelectString", inp={"A": ts(g, p + "_plain", "Menu_Color"), "B": "@%s_rep.ReturnValue" % p, "bPickA": "@%s_one.ReturnValue" % p})
    g.call(p + "_txt", K_TXT, "Conv_StringToText", inp={"InString": "@%s_sel.ReturnValue" % p})
    rw = create_widget(g, p + "_rw", W_ROW); set_manager(g, p + "_sm", W_ROW, rw)
    g.call(p + "_init", W_ROW, "Init", inp={"self": rw, "action": "@%s_acn.ReturnValue" % p, "caption": "@%s_txt.ReturnValue" % p})
    g.get(p + "_gm", "Menu"); g.call(p + "_add", W_MENU, "Add Row", inp={"self": "@%s_gm.Menu" % p, "widget": rw})
    g.chain(p + "_fe", p + "_rw_cr", p + "_sm", p + "_init", p + "_add")
    return [p + "_cs", p + "_fe"]


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
    g.get("gpg5", "Page"); g.call("isps", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg5.Page", "B": "Poses"}); g.branch("bpps", "@isps.ReturnValue"); g.n("opsc", "call_self", function="On Pose Context", inp={"name": "@entry.name"})
    g.get("gpg6", "Page"); g.call("isw", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg6.Page", "B": "Weapons"}); g.branch("bpw", "@isw.ReturnValue"); g.n("oskc", "call_self", function="On Weapon Context", inp={"name": "@entry.name"})
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
    # rows: colour - one per colourable material slot. Also on a piece that is not worn: the colour is stored for it
    # and the piece wears it the moment it goes on (Apply Item Colors), so the menu does not depend on the order of clicks.
    crows = color_menu_rows(g, "cc", "@entry.name")
    # row: reset colour (only if the piece carries a colour of its own)
    g.n("gcr", "call_self", function="Item Has Own Color", inp={"name": "@entry.name"}); g.branch("brc", "@gcr.found")
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
    g.chain("bpc:else", "bph", "ohc"); g.chain("bph:else", "bpps", "opsc"); g.chain("bpps:else", "bpw", "oskc"); g.chain("bpw:else", "bpp", "pix", "opc"); g.chain("bpp:else", "olc")
    g.chain("clr", "cr1_cr", "sr1", "ri1", "ar1", *hr, *rn, "fi", "bog", *og, *rg, "bmc", *mc, *rm, *crows); g.chain("cc_fe:Completed", "gcr", "brc", *rr, "ib", "bpb", *pb, "cr3_cr")
    g.chain("bog:else", "bmc"); g.chain("bmc:else", crows[0]); g.chain("brc:else", "ib"); g.chain("bpb:else", "cr3_cr")
    g.chain("cr3_cr", "sr3", "ri3", "ar3", "atv", "mp", "spv")
    return fn("On Item Context", [param("name", "name")], graph=g)


def simple_menu(name, rows, pre=None, cond=None):
    """Context menu with fixed rows [(action, caption)]; pre(g) may create nodes and returns exec ids that run before the menu.
    cond = {action: "Item Mod"}: that row appears only when Item Mod(entry.name) is found (the menu function has a `name` parameter).
    A row that is skipped continues at the next row - with several conditional rows in a run, wiring the skip to the next
    *unconditional* row swallowed every row in between (2026-09-25: the eye rows ate the reset row and the lash rows)."""
    g = G(); head = ["entry"] + (pre(g) if pre else [])
    g.get("gm", "Menu"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gm.Menu"}); g.branch("b", "@iv.ReturnValue")
    mw = create_widget(g, "cm", W_MENU); g.set("sm", "Menu", inp={"Menu": mw}); set_manager(g, "smm", W_MENU, mw)
    g.get("gm2", "Menu"); g.call("clr", W_MENU, "Clear Rows", inp={"self": "@gm2.Menu"})
    tail = ["clr"]; joins = []
    for i, (action, cap) in enumerate(rows):
        row = menu_row(g, i, action, cap if cap.startswith("@") else tt(g, "t%d" % i, cap))   # cap = key of the Strings table or a text pin
        if cond and action in cond:
            g.n("cq%d" % i, "call_self", function=cond[action], inp={"row": "@entry.name"}); g.branch("cb%d" % i, "@cq%d.found" % i)
            g.chain(*tail, "cb%d" % i, *row); [g.chain(j, "cb%d" % i) for j in joins]
            joins = ["cb%d:else" % i]; tail = [row[-1]]   # the skip goes to the NEXT row, not to the next unconditional one
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
    eye_rows = [("MakeupColor", "Menu_Tint"), ("MakeupReset", "Menu_TintReset")]   # make-up is tinted, so the row says so
    eye_rows += [("EyeColor:" + key, menu_key) for key, _, _, menu_key, _ in EYE_PARTS]
    eye_rows += [("EyeReset" + cat, "Menu_EyeReset") for cat in dict.fromkeys(c for _, _, _, _, c in EYE_PARTS)]
    eye_cond = {"MakeupColor": "Row Is Makeup", "MakeupReset": "Row Has Makeup Color"}
    eye_cond.update({"EyeColor:" + key: "Row Is " + cat for key, _, _, _, cat in EYE_PARTS})
    eye_cond.update({"EyeReset" + cat: "Row Is " + cat for _, _, _, _, cat in EYE_PARTS})
    g = simple_menu("On Look Item Context", [("LookFav", "@ft.ReturnValue"), ("LookHide", "@ht.ReturnValue"), ("Rename", "Menu_Rename")] + eye_rows
                    + [("RenameMod", "Menu_RenameMod"), ("LookOnlyMod", "Menu_LookOnlyMod"), ("ModContent", "Menu_ModContent"), ("Cancel", "Menu_Cancel")],
                    pre=pre, cond=dict(eye_cond, **{"RenameMod": "Item Mod", "LookOnlyMod": "Item Mod", "ModContent": "Item Mod"}))
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


def f_apply_nude():
    """Set the game rule 'Allow Naked' (TKA_GameState_Base) from AltUI's option; otherwise check clothes covering puts underwear back on."""
    g = G()
    g.call("gs", K_GS, "GetGameState"); g.cast("cs", P_GS2, "@gs.ReturnValue"); g.get("gan", "AllowNude")
    g.call("sn", P_GS2, "Set Nude Allowed", inp={"self": "@cs.AsTKA Game State", "allow": "@gan.AllowNude"})
    g.chain("entry", "sn"); return fn("Apply Nude", graph=g)


def f_fix_loaded_underwear():
    """At the end of BeginPlay (after Apply Saved Body): on load, check clothes covering (Allow Naked still false) re-adds Bra/Briefs.
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
LOOK_TILE_MAX = 2.5               # look tiles up to 250 % (a full-body photo wants the room)
TILE_STEPS = 100                  # tile sizes in 1 % steps (the other sliders: 5 %)
OUTFIT_GRID_DEFAULT = 3            # outfit tiles: pieces per row / rows (Options > Tiles; 0 in the settings = never set)


def scale_getter(name, var):
    """<var> once set (> 0), else the general tile size: outfits and looks follow it until their own slider is moved."""
    g = G(); g.get("gv", var); g.get("gt", "TileScale"); g.call("set", K_MATH, "Greater_FloatFloat", inp={"A": "@gv." + var, "B": "0.0"})
    g.call("sel", K_MATH, "SelectFloat", inp={"A": "@gv." + var, "B": "@gt.TileScale", "bPickA": "@set.ReturnValue"}); g.link("sel.ReturnValue", "return.scale")
    return fn(name, [], [param("scale", "float")], graph=g, pure=True)


def f_quick_alpha():
    """Opacity of the quick menu's fills (sectors, centre): QuickAlpha once set (> 0), else the panel background opacity."""
    g = G(); g.get("gq", "QuickAlpha"); g.get("gb", "BgAlpha"); g.call("set", K_MATH, "Greater_FloatFloat", inp={"A": "@gq.QuickAlpha", "B": "0.0"})
    g.call("sel", K_MATH, "SelectFloat", inp={"A": "@gq.QuickAlpha", "B": "@gb.BgAlpha", "bPickA": "@set.ReturnValue"}); g.link("sel.ReturnValue", "return.alpha")
    return fn("Quick Alpha", [], [param("alpha", "float")], graph=g, pure=True)


def grid_getter(name, var):
    g = G(); g.get("gv", var); g.call("set", K_MATH, "Greater_IntInt", inp={"A": "@gv." + var, "B": "0"})
    g.call("sel", K_MATH, "SelectInt", inp={"A": "@gv." + var, "B": str(OUTFIT_GRID_DEFAULT), "bPickA": "@set.ReturnValue"}); g.link("sel.ReturnValue", "return.n")
    return fn(name, [], [param("n", "int")], graph=g, pure=True)
FOV_MIN, FOV_MAX = 0.3, 1.0      # camera FOV scale 30..100 %
DIST_MIN, DIST_MAX = 0.0, 3.0    # camera distance scale 0..300 %
GROUPLEN_MIN, GROUPLEN_MAX = 3, 20   # chip caption length; slider step 18 (past GROUPLEN_MAX) = unlimited (GroupLen 0)
GROUPLEN_STEPS = GROUPLEN_MAX - GROUPLEN_MIN + 1
from gen_widgets import SUBTABS_MAX_H, SUBTABS_MAX_H_MAX, OPT_CATS
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
    # camera height in centimetres ("0 cm", "35 cm", "-20 cm"): a percentage says nothing here, and the value can be negative
    g.get("ox_hg", "CamHeight"); g.call("ox_hgr", K_MATH, "Round", inp={"A": "@ox_hg.CamHeight"}); g.call("ox_hgi", K_STR, "Conv_IntToString", inp={"InInt": "@ox_hgr.ReturnValue"})
    g.call("ox_hgc", K_STR, "Concat_StrStr", inp={"A": "@ox_hgi.ReturnValue", "B": " cm"}); g.call("ox_hgt", K_TXT, "Conv_StringToText", inp={"InString": "@ox_hgc.ReturnValue"})
    def pct_fn(fname, id):
        g.n(id + "_v", "call_self", function=fname); g.call(id + "_m", K_MATH, "Multiply_FloatFloat", inp={"A": "@%s_v.scale" % id, "B": "100.0"}); g.call(id + "_r", K_MATH, "Round", inp={"A": "@%s_m.ReturnValue" % id})
        g.call(id + "_i", K_STR, "Conv_IntToString", inp={"InInt": "@%s_r.ReturnValue" % id}); g.call(id + "_c", K_STR, "Concat_StrStr", inp={"A": "@%s_i.ReturnValue" % id, "B": " %"}); g.call(id + "_t", K_TXT, "Conv_StringToText", inp={"InString": "@%s_c.ReturnValue" % id})
        return "@%s_t.ReturnValue" % id
    def qa_text():
        g.n("ox_qa_v", "call_self", function="Quick Alpha"); g.call("ox_qa_m", K_MATH, "Multiply_FloatFloat", inp={"A": "@ox_qa_v.alpha", "B": "100.0"}); g.call("ox_qa_r", K_MATH, "Round", inp={"A": "@ox_qa_m.ReturnValue"})
        g.call("ox_qa_i", K_STR, "Conv_IntToString", inp={"InInt": "@ox_qa_r.ReturnValue"}); g.call("ox_qa_c", K_STR, "Concat_StrStr", inp={"A": "@ox_qa_i.ReturnValue", "B": " %"}); g.call("ox_qa_t", K_TXT, "Conv_StringToText", inp={"InString": "@ox_qa_c.ReturnValue"})
        return "@ox_qa_t.ReturnValue"
    def int_fn(fname, id):
        g.n(id + "_v", "call_self", function=fname); g.call(id + "_t", K_TXT, "Conv_IntToText", inp={"Value": "@%s_v.n" % id}); return "@%s_t.ReturnValue" % id
    return ("@ox_t.ReturnValue", "@ox_t2.ReturnValue", pct("CamFov", "ox_f2"), pct("CamDist", "ox_d2"), "@ox_hgt.ReturnValue",
            pct("BgAlpha", "ox_ba"), pct("TileAlpha", "ox_ta"), "@ox_glt.ReturnValue", "@ox_cht.ReturnValue",
            pct_fn("Outfit Scale", "ox_os"), pct_fn("Look Scale", "ox_ls"), int_fn("Outfit Cols", "ox_oc"), int_fn("Outfit Rows", "ox_or"), qa_text())


def f_rebuild_options():
    """Set the sliders from ScrollMult (1..10) / TileScale (TILE_MIN..TILE_MAX) / camera / opacities; layout, language, key chips; theme swatches + reset link."""
    g = G()
    g.get("gsm", "ScrollMult"); g.call("s1", K_MATH, "Subtract_FloatFloat", inp={"A": "@gsm.ScrollMult", "B": "1.0"}); g.call("s2", K_MATH, "Divide_FloatFloat", inp={"A": "@s1.ReturnValue", "B": "9.0"})
    g.get("gts", "TileScale"); g.call("t0", K_MATH, "Subtract_FloatFloat", inp={"A": "@gts.TileScale", "B": str(TILE_MIN)}); g.call("t1", K_MATH, "Divide_FloatFloat", inp={"A": "@t0.ReturnValue", "B": str(TILE_MAX - TILE_MIN)})
    # FOV FOV_MIN..FOV_MAX -> slider (x-min)/(max-min); distance likewise
    g.get("gcf", "CamFov"); g.call("f1", K_MATH, "Subtract_FloatFloat", inp={"A": "@gcf.CamFov", "B": str(FOV_MIN)}); g.call("f2", K_MATH, "Divide_FloatFloat", inp={"A": "@f1.ReturnValue", "B": str(FOV_MAX - FOV_MIN)})
    g.get("gcd", "CamDist"); g.call("d1", K_MATH, "Subtract_FloatFloat", inp={"A": "@gcd.CamDist", "B": str(DIST_MIN)}); g.call("d2", K_MATH, "Divide_FloatFloat", inp={"A": "@d1.ReturnValue", "B": str(DIST_MAX - DIST_MIN)})
    g.get("gchm", "CamHeight"); g.call("hg1", K_MATH, "Subtract_FloatFloat", inp={"A": "@gchm.CamHeight", "B": str(HEIGHT_MIN)}); g.call("hg2", K_MATH, "Divide_FloatFloat", inp={"A": "@hg1.ReturnValue", "B": str(HEIGHT_MAX - HEIGHT_MIN)})
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
    g.set("of", "OptFov", inp={"OptFov": "@f2.ReturnValue"}); g.set("od", "OptDist", inp={"OptDist": "@d2.ReturnValue"}); g.set("ohg", "OptHeight", inp={"OptHeight": "@hg2.ReturnValue"})
    g.set("oba", "OptBgAlpha", inp={"OptBgAlpha": "@gba.BgAlpha"}); g.set("ota", "OptTileAlpha", inp={"OptTileAlpha": "@gta.TileAlpha"})
    # outfit / look tile sizes (TILE_MIN..TILE_MAX like the tile size), outfit grid 1..OUTFIT_MAX
    pos = {}
    for k, fname, top in (("OutfitScale", "Outfit Scale", TILE_MAX), ("LookScale", "Look Scale", LOOK_TILE_MAX)):
        g.n("g" + k, "call_self", function=fname); g.call("p0" + k, K_MATH, "Subtract_FloatFloat", inp={"A": "@g%s.scale" % k, "B": str(TILE_MIN)})
        g.call("p" + k, K_MATH, "Divide_FloatFloat", inp={"A": "@p0%s.ReturnValue" % k, "B": str(top - TILE_MIN)}); pos[k] = "@p%s.ReturnValue" % k
    for k, fname in (("OutfitCols", "Outfit Cols"), ("OutfitRows", "Outfit Rows")):
        g.n("g" + k, "call_self", function=fname); g.call("p0" + k, K_MATH, "Subtract_IntInt", inp={"A": "@g%s.n" % k, "B": "1"}); g.call("p1" + k, K_MATH, "Conv_IntToFloat", inp={"InInt": "@p0%s.ReturnValue" % k})
        g.call("p" + k, K_MATH, "Divide_FloatFloat", inp={"A": "@p1%s.ReturnValue" % k, "B": str(float(OUTFIT_MAX - 1))}); pos[k] = "@p%s.ReturnValue" % k
    g.n("gQuickAlpha", "call_self", function="Quick Alpha"); pos["QuickAlpha"] = "@gQuickAlpha.alpha"   # 0..1 = the slider itself
    for k in pos: g.set("so" + k, "Opt" + k, inp={"Opt" + k: pos[k]})
    t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14 = opt_texts(g)
    g.get("gp", "Panel"); g.call("sv", W_PANEL, "Set Option Values", inp={"self": "@gp.Panel", "scroll": "@s2.ReturnValue", "scale": "@t1.ReturnValue", "fov": "@f2.ReturnValue", "dist": "@d2.ReturnValue", "height": "@hg2.ReturnValue",
                                                                            "bgalpha": "@gba.BgAlpha", "tilealpha": "@gta.TileAlpha", "grouplen": "@gl4.ReturnValue", "chiph": "@ch3.ReturnValue",
                                                                            "outfitscale": pos["OutfitScale"], "lookscale": pos["LookScale"], "outfitcols": pos["OutfitCols"], "outfitrows": pos["OutfitRows"], "quickalpha": pos["QuickAlpha"],
                                                                            "scroll text": t1, "scale text": t2, "fov text": t3, "dist text": t4, "height text": t5, "bgalpha text": t6, "tilealpha text": t7, "grouplen text": t8, "chiph text": t9,
                                                                            "outfitscale text": t10, "lookscale text": t11, "outfitcols text": t12, "outfitrows text": t13, "quickalpha text": t14})
    g.get("gp2", "Panel"); g.get("gun", "Unlimited"); g.get("gpn", "PanToSlot"); g.get("gan", "AllowNude"); g.get("gmg", "MergeGroups"); g.get("gmm", "MergeMods"); g.get("gtp", "TipNoPrefix"); g.get("gtn", "TipNoIds"); g.get("gcrh", "CamRightHeight")
    g.get("gcsh", "ChipSearchShown")
    g.call("su", W_PANEL, "Set Option Checks", inp={"self": "@gp2.Panel", "unlimited": "@gun.Unlimited", "pan": "@gpn.PanToSlot", "nude": "@gan.AllowNude", "merge": "@gmg.MergeGroups", "mergemods": "@gmm.MergeMods", "chipsearch": "@gcsh.ChipSearchShown", "tipnoprefix": "@gtp.TipNoPrefix", "tipnoids": "@gtn.TipNoIds", "camright": "@gcrh.CamRightHeight"})
    # layout chips (W_SubTab: click -> Select SubTab -> Select Layout), display order by size, stable indices
    g.get("gp3", "Panel"); g.call("cl", W_PANEL, "Clear Layout Chips", inp={"self": "@gp3.Panel"}); tail = ["entry", "os", "oc", "of", "od", "ohg", "oba", "ota", "ogl", "och", "soOutfitScale", "soLookScale", "soOutfitCols", "soOutfitRows", "soQuickAlpha", "sv", "su", "cl"]
    for i, (idx, key) in enumerate(LAYOUTS):
        cw = create_widget(g, "cc%d" % i, W_SUB); set_manager(g, "cm%d" % i, W_SUB, cw)
        g.get("glf%d" % i, "LeftFree"); g.call("eq%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": "@glf%d.LeftFree" % i, "B": str(idx)})
        g.call("ci%d" % i, W_SUB, "Init", inp={"self": cw, "group": "Layout%d" % idx, "caption": tt(g, "ct%d" % i, key), "selected": "@eq%d.ReturnValue" % i})
        g.get("gpc%d" % i, "Panel"); g.call("ac%d" % i, W_PANEL, "Add Layout Chip", inp={"self": "@gpc%d.Panel" % i, "widget": cw})
        tail += ["cc%d_cr" % i, "cm%d" % i, "ci%d" % i, "ac%d" % i]
    # not-owned mode chips (group "Unowned<n>"), active = UnownedMode
    g.get("gpu", "Panel"); g.call("clu", W_PANEL, "Clear Unowned Chips", inp={"self": "@gpu.Panel"}); tail.append("clu")
    for i in range(3):
        uw = create_widget(g, "uc%d" % i, W_SUB); set_manager(g, "um%d" % i, W_SUB, uw)
        g.get("gum%d" % i, "UnownedMode"); g.call("ueq%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": "@gum%d.UnownedMode" % i, "B": str(i)})
        g.call("uci%d" % i, W_SUB, "Init", inp={"self": uw, "group": "Unowned%d" % i, "caption": tt(g, "ut%d" % i, "Chip_Unowned%d" % i), "selected": "@ueq%d.ReturnValue" % i})
        g.get("gpv%d" % i, "Panel"); g.call("ua%d" % i, W_PANEL, "Add Unowned Chip", inp={"self": "@gpv%d.Panel" % i, "widget": uw})
        tail += ["uc%d_cr" % i, "um%d" % i, "uci%d" % i, "ua%d" % i]
    # language chips (Auto / English / Deutsch / 中文 / Русский / Español / Polski), active = LangChoice (chip index, Lang = LangChoice - 1)
    g.get("gpl9", "Panel"); g.call("cll", W_PANEL, "Clear Lang Chips", inp={"self": "@gpl9.Panel"}); tail.append("cll")
    for i, key in enumerate(["Chip_LangAuto"] + ["Chip_Lang" + l.capitalize() for l in LANGS]):
        lw = create_widget(g, "lc%d" % i, W_SUB); set_manager(g, "lm%d" % i, W_SUB, lw)
        g.get("glc%d" % i, "LangChoice"); g.call("leq%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": "@glc%d.LangChoice" % i, "B": str(i)})
        g.call("lci%d" % i, W_SUB, "Init", inp={"self": lw, "group": "Lang%d" % i, "caption": tt(g, "lt%d" % i, key), "selected": "@leq%d.ReturnValue" % i})
        g.get("gpq%d" % i, "Panel"); g.call("la%d" % i, W_PANEL, "Add Lang Chip", inp={"self": "@gpq%d.Panel" % i, "widget": lw})
        tail += ["lc%d_cr" % i, "lm%d" % i, "lci%d" % i, "la%d" % i]
    # panel key chips (group "Key<X>"), active = ToggleKey
    g.get("gpk", "Panel"); g.call("clk", W_PANEL, "Clear Key Chips", inp={"self": "@gpk.Panel"}); tail.append("clk")
    for i, k in enumerate(TOGGLE_KEYS):
        kw = create_widget(g, "kc%d" % i, W_SUB); set_manager(g, "km%d" % i, W_SUB, kw)
        g.get("gtk%d" % i, "ToggleKey"); g.call("keq%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@gtk%d.ToggleKey" % i, "B": k})
        g.call("kt%d" % i, K_TXT, "Conv_StringToText", inp={"InString": k})
        g.call("kci%d" % i, W_SUB, "Init", inp={"self": kw, "group": "Key" + k, "caption": "@kt%d.ReturnValue" % i, "selected": "@keq%d.ReturnValue" % i})
        g.get("gpx%d" % i, "Panel"); g.call("ka%d" % i, W_PANEL, "Add Key Chip", inp={"self": "@gpx%d.Panel" % i, "widget": kw})
        tail += ["kc%d_cr" % i, "km%d" % i, "kci%d" % i, "ka%d" % i]
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
    # saved schemes: the "save" link next to the name field, one chip per scheme
    g.get("gpsl", "Panel"); g.call("ctsl", W_PANEL, "Clear Theme Save Links", inp={"self": "@gpsl.Panel"}); tail.append("ctsl")
    tsw = create_widget(g, "tsw", W_TXT); set_manager(g, "tswm", W_TXT, tsw)
    g.call("tswi", W_TXT, "Init", inp={"self": tsw, "action": "ThemeSave", "caption": tt(g, "tswt", "Btn_ThemeSave")})
    g.get("gpsa", "Panel"); g.call("tswa", W_PANEL, "Add Theme Save Link", inp={"self": "@gpsa.Panel", "widget": tsw}); tail += ["tsw_cr", "tswm", "tswi", "tswa"]
    g.n("rtp", "call_self", function="Rebuild Theme Presets"); tail.append("rtp")
    g.n("rcf", "call_self", function="Rebuild Conflicts"); tail.append("rcf")
    g.n("rtc", "call_self", function="Rebuild Tab Chips"); tail.append("rtc")
    g.n("rqo", "call_self", function="Rebuild Quick Options"); tail.append("rqo")
    # values and checks always (cheap); the chip / swatch / conflict blocks only for the category that is shown (OptionsCat)
    cut = {k: tail.index(k) for k in ("cl", "clk", "cts", "rcf", "rtc")}
    segs = [("General", tail[cut["cl"]:cut["clk"]]), ("Controls", tail[cut["clk"]:cut["cts"]]), ("Theme", tail[cut["cts"]:cut["rcf"]]), ("Conflicts", ["rcf"]), ("Tabs", ["rtc"]), ("Quick", ["rqo"])]
    g.chain(*tail[:cut["cl"]]); exits = [tail[cut["cl"] - 1]]
    for cat, seg in segs:
        g.get("goc_" + cat, "OptionsCat"); g.call("eoc_" + cat, K_MATH, "EqualEqual_NameName", inp={"A": "@goc_%s.OptionsCat" % cat, "B": cat}); g.branch("boc_" + cat, "@eoc_%s.ReturnValue" % cat)
        for e in exits: g.chain(e, "boc_" + cat)
        g.chain("boc_" + cat, *seg); exits = [seg[-1], "boc_%s:else" % cat]
    return fn("Rebuild Options", graph=g)


def f_rebuild_option_cats():
    """Options: left list, one W_SlotTab per category (OPT_CATS), selected = OptionsCat, no count."""
    g = G(); g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Option Cats", inp={"self": "@gp.Panel"}); tail = ["entry", "cl"]
    for i, cat in enumerate(OPT_CATS):
        p = "c%d" % i; tw = create_widget(g, p + "w", W_TAB); set_manager(g, p + "sm", W_TAB, tw)
        g.get(p + "gc", "OptionsCat"); g.call(p + "sel", K_MATH, "EqualEqual_NameName", inp={"A": "@%sgc.OptionsCat" % p, "B": cat})
        g.call(p + "ti", W_TAB, "Init", inp={"self": tw, "slot": cat, "caption": tt(g, p + "t", "OptCat_" + cat), "count": "0", "worn icon": "None",
                                             "selected": "@%ssel.ReturnValue" % p, "has items": "true", "filtered": "-1", "indent": "false"})
        g.call(p + "hc", W_TAB, "Hide Count", inp={"self": tw})
        g.get(p + "gp", "Panel"); g.call(p + "ad", W_PANEL, "Add Option Cat", inp={"self": "@%sgp.Panel" % p, "widget": tw})
        tail += [p + "w_cr", p + "sm", p + "ti", p + "hc", p + "ad"]
    g.chain(*tail); return fn("Rebuild Option Cats", graph=g)


def f_select_option_cat():
    """Options category click: show its block, mark it in the list, fill it, keep it in the settings."""
    g = G(); g.set("s", "OptionsCat", inp={"OptionsCat": "@entry.name"})
    g.get("gp", "Panel"); g.call("soc", W_PANEL, "Set Option Cat", inp={"self": "@gp.Panel", "cat": "@entry.name"})
    g.n("roc", "call_self", function="Rebuild Option Cats"); g.n("ro", "call_self", function="Rebuild Options"); g.n("sv", "call_self", function="Save Settings")
    g.chain("entry", "s", "soc", "roc", "ro", "sv"); return fn("Select Option Cat", [param("name", "name")], graph=g)


TAB_STYLES = ["Chip_TabStyle0", "Chip_TabStyle1", "Chip_TabStyle2"]   # TabStyle: text / icons / icons + text
TAB_ICON_POS = ["Chip_TabIconPos0", "Chip_TabIconPos1"]                 # TabIconRight: left / right


def f_rebuild_tab_chips():
    """Options > Tabs: tab bar style chips ("TabStyle<n>", TabStyle), icon position chips ("TabIconPos<n>", TabIconRight), then one chip
    per tab of TOP_TABS but Options (group "Tab:<page>", selected = not switched off)."""
    g = G(); tail = ["entry"]
    for row, keys, var_, cmp in (("TabStyle", TAB_STYLES, "TabStyle", "int"), ("TabIconPos", TAB_ICON_POS, "TabIconRight", "bool")):
        clr = "Clear Tab Style Chips" if row == "TabStyle" else "Clear Tab Icon Pos Chips"; add = "Add Tab Style Chip" if row == "TabStyle" else "Add Tab Icon Pos Chip"
        g.get("gp" + row, "Panel"); g.call("cl" + row, W_PANEL, clr, inp={"self": "@gp%s.Panel" % row}); tail.append("cl" + row)
        for i, key in enumerate(keys):
            p = "%s%d" % (row, i); cw = create_widget(g, p + "w", W_SUB); set_manager(g, p + "sm", W_SUB, cw); g.get(p + "gv", var_)
            if cmp == "int": g.call(p + "eq", K_MATH, "EqualEqual_IntInt", inp={"A": "@%sgv.%s" % (p, var_), "B": str(i)})
            else: g.call(p + "eq", K_MATH, "EqualEqual_BoolBool", inp={"A": "@%sgv.%s" % (p, var_), "B": "true" if i else "false"})
            g.call(p + "ci", W_SUB, "Init", inp={"self": cw, "group": p, "caption": tt(g, p + "t", key), "selected": "@%seq.ReturnValue" % p})
            g.get(p + "gp", "Panel"); g.call(p + "ad", W_PANEL, add, inp={"self": "@%sgp.Panel" % p, "widget": cw})
            tail += [p + "w_cr", p + "sm", p + "ci", p + "ad"]
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Tab Chips", inp={"self": "@gp.Panel"}); tail.append("cl")
    for i, page in enumerate(p for p in TOP_TABS if p != "Options"):
        p = "t%d" % i; cw = create_widget(g, p + "w", W_SUB); set_manager(g, p + "sm", W_SUB, cw)
        g.get(p + "gh", "HiddenTabs"); g.call(p + "h", K_ARR, "Array_Contains", inp={"TargetArray": "@%sgh.HiddenTabs" % p, "ItemToFind": g.lit_name(p + "ln", page)})
        g.call(p + "on", K_MATH, "Not_PreBool", inp={"A": "@%sh.ReturnValue" % p})
        g.call(p + "ci", W_SUB, "Init", inp={"self": cw, "group": "Tab:" + page, "caption": tt(g, p + "t", "Tab_" + page), "selected": "@%son.ReturnValue" % p})
        g.get(p + "gp", "Panel"); g.call(p + "ad", W_PANEL, "Add Tab Chip", inp={"self": "@%sgp.Panel" % p, "widget": cw})
        tail += [p + "w_cr", p + "sm", p + "ci", p + "ad"]
    g.chain(*tail); return fn("Rebuild Tab Chips", graph=g)


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


def f_select_tab_style():
    """Chip "TabStyle<n>" -> TabStyle, "TabIconPos<n>" -> TabIconRight; save, the tab bar and the chips follow."""
    g = G(); tail = ["entry"]; sets = []
    for i in range(len(TAB_STYLES)):
        g.call("e%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "TabStyle%d" % i}); g.branch("b%d" % i, "@e%d.ReturnValue" % i)
        g.set("s%d" % i, "TabStyle", inp={"TabStyle": str(i)}); g.chain(*tail, "b%d" % i, "s%d" % i); tail = ["b%d:else" % i]; sets.append("s%d" % i)
    for i in range(len(TAB_ICON_POS)):
        g.call("pe%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "TabIconPos%d" % i}); g.branch("pb%d" % i, "@pe%d.ReturnValue" % i)
        g.set("ps%d" % i, "TabIconRight", inp={"TabIconRight": "true" if i else "false"}); g.chain(*tail, "pb%d" % i, "ps%d" % i); tail = ["pb%d:else" % i]; sets.append("ps%d" % i)
    g.n("sv", "call_self", function="Save Settings"); g.n("rtt", "call_self", function="Rebuild TopTabs"); g.n("rtc", "call_self", function="Rebuild Tab Chips")
    for s_ in sets: g.chain(s_, "sv")
    g.chain("sv", "rtt", "rtc"); return fn("Select Tab Style", [param("name", "name")], graph=g)


def theme_preset_key(g, id, pin):
    """"ThemeP:<name>" (chip group) -> <name> as a Name pin."""
    g.call(id + "_s", K_STR, "Conv_NameToString", inp={"InName": pin}); g.call(id + "_c", K_STR, "GetSubstring", inp={"SourceString": "@%s_s.ReturnValue" % id, "StartIndex": "7", "Length": "1000"})
    g.call(id, K_STR, "Conv_StringToName", inp={"InString": "@%s_c.ReturnValue" % id}); return "@%s.ReturnValue" % id


def f_theme_save():
    """Options > Colours "save": Save Theme Preset with the typed name, then the field is emptied."""
    g = G(); g.get("gp", "Panel"); g.call("gt", W_PANEL, "Get Theme Name", inp={"self": "@gp.Panel"}); g.call("ts", K_TXT, "Conv_TextToString", inp={"InText": "@gt.text"})
    g.n("stp", "call_self", function="Save Theme Preset", inp={"name": "@ts.ReturnValue"}); g.branch("bok", "@stp.ok")
    g.get("gp2", "Panel"); g.call("cn", W_PANEL, "Clear Theme Name", inp={"self": "@gp2.Panel"})
    g.chain("entry", "stp", "bok", "cn")
    return fn("Theme Save", graph=g)


def f_save_theme_preset():
    """The base colours and both opacities under `name`, trimmed (ThemePresets; the same name - case does not matter - overwrites).
    An empty name stores nothing (ok = false)."""
    g = G()
    g.call("tr", K_STR, "Trim", inp={"SourceString": "@entry.name"}); g.call("tr2", K_STR, "TrimTrailing", inp={"SourceString": "@tr.ReturnValue"})
    g.call("emp", K_STR, "IsEmpty", inp={"InString": "@tr2.ReturnValue"}); g.call("ne", K_MATH, "Not_PreBool", inp={"A": "@emp.ReturnValue"}); g.branch("b", "@ne.ReturnValue")
    for key, _, _ in THEME: g.get("gc" + key, "Theme" + key)
    g.n("arr", "make_array", count=len(THEME), type=S_LINCOLOR, inp={"[%d]" % i: "@gc%s.Theme%s" % (k, k) for i, (k, _, _) in enumerate(THEME)})
    g.get("gba", "BgAlpha"); g.get("gta", "TileAlpha"); g.make("mk", S_THEMEP, Colors="@arr.Array", BgAlpha="@gba.BgAlpha", TileAlpha="@gta.TileAlpha")
    g.call("nm", K_STR, "Conv_StringToName", inp={"InString": "@tr2.ReturnValue"})
    g.get("gtp", "ThemePresets"); g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gtp.ThemePresets", "Key": "@nm.ReturnValue", "Value": "@mk." + S_THEMEP.rsplit("/", 1)[-1]})
    g.n("sv", "call_self", function="Save Settings"); g.n("rtp", "call_self", function="Rebuild Theme Presets")
    g.set("sok", "ThemeSaveOk", inp={"ThemeSaveOk": "@ne.ReturnValue"}); g.get("gok", "ThemeSaveOk"); g.link("gok.ThemeSaveOk", "return.ok")
    g.chain("entry", "sok", "b", "add", "sv", "rtp", "return"); g.chain("b:else", "return")
    return fn("Save Theme Preset", [param("name", "string")], [param("ok", "bool")], graph=g)


def f_apply_theme_preset():
    """Saved scheme chip "ThemeP:<name>": its colours and opacities become the current theme (applied, saved, the page redrawn)."""
    g = G(); k = theme_preset_key(g, "k", "@entry.name")
    g.get("gtp", "ThemePresets"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gtp.ThemePresets", "Key": k}); g.branch("bf", "@f.ReturnValue")
    g.brk("br", S_THEMEP, "@f.Value"); g.set("sct", "ThemeColorsTmp", inp={"ThemeColorsTmp": "@br.Colors"})
    g.get("gct", "ThemeColorsTmp"); g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@gct.ThemeColorsTmp"})
    g.set("sba", "BgAlpha", inp={"BgAlpha": "@br.BgAlpha"}); g.set("sta", "TileAlpha", inp={"TileAlpha": "@br.TileAlpha"})
    g.chain("entry", "bf", "sct", "sba", "sta"); prev = ["sta"]
    for i, (key, _, _) in enumerate(THEME):   # a scheme with fewer colours keeps the current ones for the rest
        g.call("in%d" % i, K_MATH, "Greater_IntInt", inp={"A": "@len.ReturnValue", "B": str(i)}); g.branch("bi%d" % i, "@in%d.ReturnValue" % i)
        g.get("gc%d" % i, "ThemeColorsTmp"); g.call("get%d" % i, K_ARR, "Array_Get", inp={"TargetArray": "@gc%d.ThemeColorsTmp" % i, "Index": str(i)})
        g.set("s%d" % i, "Theme" + key, inp={"Theme" + key: "@get%d.Item" % i})
        for p_ in prev: g.chain(p_, "bi%d" % i)
        g.chain("bi%d" % i, "s%d" % i); prev = ["s%d" % i, "bi%d:else" % i]
    g.n("ap", "call_self", function="Apply Theme"); g.n("sv", "call_self", function="Save Settings"); g.n("ro", "call_self", function="Rebuild Options")
    for p_ in prev: g.chain(p_, "ap")
    g.chain("ap", "sv", "ro")
    return fn("Apply Theme Preset", [param("name", "name")], graph=g)


def f_delete_theme_preset():
    g = G(); k = theme_preset_key(g, "k", "@entry.name")
    g.get("gtp", "ThemePresets"); g.call("rm", K_MAP, "Map_Remove", inp={"TargetMap": "@gtp.ThemePresets", "Key": k})
    g.n("sv", "call_self", function="Save Settings"); g.n("rtp", "call_self", function="Rebuild Theme Presets"); g.chain("entry", "rm", "sv", "rtp")
    return fn("Delete Theme Preset", [param("name", "name")], graph=g)


def f_rebuild_theme_presets():
    """Options > Colours: one chip per saved scheme (group "ThemeP:<name>"), in the order they were saved."""
    g = G(); g.get("gp0", "Panel"); g.call("pv", K_SYS, "IsValid", inp={"Object": "@gp0.Panel"}); g.branch("bpv", "@pv.ReturnValue")
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Theme Presets", inp={"self": "@gp.Panel"})
    g.get("gtp", "ThemePresets"); g.call("keys", K_MAP, "Map_Keys", inp={"TargetMap": "@gtp.ThemePresets"}); g.set("sk", "ThemePresetKeys", inp={"ThemePresetKeys": "@keys.Keys"})
    g.get("gk", "ThemePresetKeys"); g.foreach("fe", "@gk.ThemePresetKeys")
    cw = create_widget(g, "cw", W_SUB); set_manager(g, "sm", W_SUB, cw)
    g.call("ks", K_STR, "Conv_NameToString", inp={"InName": "@fe.Array Element"}); g.call("gs", K_STR, "Concat_StrStr", inp={"A": "ThemeP:", "B": "@ks.ReturnValue"}); g.call("gn", K_STR, "Conv_StringToName", inp={"InString": "@gs.ReturnValue"})
    g.call("kt", K_TXT, "Conv_StringToText", inp={"InString": "@ks.ReturnValue"})
    g.call("ci", W_SUB, "Init", inp={"self": cw, "group": "@gn.ReturnValue", "caption": "@kt.ReturnValue", "selected": "false"})
    g.get("gp2", "Panel"); g.call("ad", W_PANEL, "Add Theme Preset", inp={"self": "@gp2.Panel", "widget": cw})
    g.chain("entry", "bpv", "cl", "keys", "sk", "fe"); g.chain("fe", "cw_cr", "sm", "ci", "ad")
    return fn("Rebuild Theme Presets", graph=g)


def f_subtab_context():
    """Right click on a chip: a saved colour scheme gets its menu (apply / delete); every other chip does what a click does."""
    g = None
    def pre(gg):
        gg.call("ns", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"}); gg.call("isp", K_STR, "StartsWith", inp={"SourceString": "@ns.ReturnValue", "InPrefix": "ThemeP:", "SearchCase": "CaseSensitive"})
        gg.branch("bisp", "@isp.ReturnValue"); gg.set("sci", "ContextItem", inp={"ContextItem": "@entry.name"})
        gg.n("sst", "call_self", function="Select SubTab", inp={"name": "@entry.name"}); gg.chain("bisp:else", "sst"); return ["bisp", "sci"]
    g = simple_menu("SubTab Context", [("ThemePApply", "Menu_Apply"), ("ThemePDelete", "Menu_Delete"), ("Cancel", "Menu_Cancel")], pre)
    return fn("SubTab Context", [param("name", "name")], graph=g)


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


def f_ensure_cam_mod():
    """Attach CM_AltUICam to whatever PlayerCameraManager this level has (vanilla, AltUI's own, another mod's - a modifier needs
    no replaced class). Lazy instead of in BeginPlay: neither the spawn order at level start nor a level change matters."""
    g = G()
    g.get("gcm0", "CamMod"); g.call("cv0", K_SYS, "IsValid", inp={"Object": "@gcm0.CamMod"}); g.call("ncv", K_MATH, "Not_PreBool", inp={"A": "@cv0.ReturnValue"}); g.branch("bv", "@ncv.ReturnValue")
    g.get("gpc", "PC"); g.get("gmgr", "PlayerCameraManager", cls=E_PC); g.link("gpc.PC", "gmgr.self")
    g.call("mv", K_SYS, "IsValid", inp={"Object": "@gmgr.PlayerCameraManager"}); g.branch("bm", "@mv.ReturnValue")   # no controller/camera yet -> the next call tries again
    # a previous manager of this level may have left one behind (its EndPlay removes it, but not if it was destroyed hard)
    g.call("find", E_PCM, "FindCameraModifierByClass", inp={"self": "@gmgr.PlayerCameraManager", "ModifierClass": CAMMOD})
    g.call("fv", K_SYS, "IsValid", inp={"Object": "@find.ReturnValue"}); g.branch("bf", "@fv.ReturnValue")
    g.cast("cf", CAMMOD, "@find.ReturnValue", pure=False, miss="ignore"); g.set("sf", "CamMod", inp={"CamMod": "@cf.AsCM_AltUICam"})
    g.call("add", E_PCM, "AddNewCameraModifier", inp={"self": "@gmgr.PlayerCameraManager", "ModifierClass": CAMMOD})
    g.cast("ca", CAMMOD, "@add.ReturnValue", pure=False, miss="ignore"); g.set("sa", "CamMod", inp={"CamMod": "@ca.AsCM_AltUICam"})
    g.chain("entry", "bv", "bm", "find", "bf", "cf", "sf"); g.chain("bf:else", "add", "ca", "sa")   # Find/Add are impure: chained, or they are pruned
    return fn("Ensure Cam Mod", graph=g)


def f_set_view_shift():
    """Pass ViewShift on to AltUI's camera modifier. It sits on the camera manager the game already has, so this works
    whether or not the hook pak is installed and whichever mod owns TKA_PlayerCameraManager."""
    g = G(); g.n("ens", "call_self", function="Ensure Cam Mod")
    g.get("gcm", "CamMod"); g.call("cv", K_SYS, "IsValid", inp={"Object": "@gcm.CamMod"}); g.branch("bv", "@cv.ReturnValue")   # camera manager not there yet -> nothing to pass on
    g.get("gvs", "ViewShift"); g.get("gcmv", "CamMode"); g.call("cm0", K_MATH, "EqualEqual_IntInt", inp={"A": "@gcmv.CamMode", "B": "0"})
    g.call("vsel", K_MATH, "SelectFloat", inp={"A": "@gvs.ViewShift", "B": "0.0", "bPickA": "@cm0.ReturnValue"})   # free cam / photo mode: the modifier must pass the view through
    g.n("sv", "set", var="ViewShift", cls=CAMMOD, inp={"self": "@gcm.CamMod", "ViewShift": "@vsel.ReturnValue"})
    g.get("gcf", "CamFov"); g.n("sf", "set", var="FovScale", cls=CAMMOD, inp={"self": "@gcm.CamMod", "FovScale": "@gcf.CamFov"})
    g.get("gcd", "CamDist"); g.n("sd", "set", var="DistScale", cls=CAMMOD, inp={"self": "@gcm.CamMod", "DistScale": "@gcd.CamDist"})
    g.get("gfo", "FocusOn"); g.n("sfo", "set", var="FocusOn", cls=CAMMOD, inp={"self": "@gcm.CamMod", "FocusOn": "@gfo.FocusOn"})
    g.n("sfz", "set", var="FocusZ", cls=CAMMOD, inp={"self": "@gcm.CamMod", "FocusZ": "0.0"})   # the height travels as UserZ (FocusHeight), see below
    g.get("gfm", "FocusZoom"); g.n("sfm", "set", var="FocusZoom", cls=CAMMOD, inp={"self": "@gcm.CamMod", "FocusZoom": "@gfm.FocusZoom"})
    # the dragged height belongs to the open panel: closed (and in free cam / photo mode) the game keeps its own camera
    # target height: with a slot focus FocusHeight (starts at the slot, Update Focus), else the saved camera height - both in the same
    # fixed band around Jodi, so the reachable range never moves with the slot
    g.get("gch", "CamHeight"); g.get("gpo", "PanelOpen"); g.call("hon", K_MATH, "BooleanAND", inp={"A": "@gpo.PanelOpen", "B": "@cm0.ReturnValue"})
    g.get("gfo2", "FocusOn"); g.get("gfh", "FocusHeight"); g.call("hrel", K_MATH, "SelectFloat", inp={"A": "@gfh.FocusHeight", "B": "@gch.CamHeight", "bPickA": "@gfo2.FocusOn"})
    g.call("hsel", K_MATH, "SelectFloat", inp={"A": "@hrel.ReturnValue", "B": "0.0", "bPickA": "@hon.ReturnValue"})
    g.n("suz", "set", var="UserZ", cls=CAMMOD, inp={"self": "@gcm.CamMod", "UserZ": "@hsel.ReturnValue"})
    g.chain("entry", "ens", "bv", "sv", "sf", "sd", "sfo", "sfz", "sfm", "suz"); return fn("Set View Shift", graph=g)



# ---------------- Free cam (own CameraActor as view target) + the game's photo mode ----------------
FREE_TRACE_R = 12.0; FREE_TRACE_GAP = 2.0; FREE_PITCH = 85.0; FREE_LOOK = 0.6; FREE_FAST = 3.0; FREE_WHEEL = 1.25; FREE_SPEED_MIN = 50.0; FREE_SPEED_MAX = 1000.0
SETTINGS_SAVE_DELAY = 0.5   # seconds after the last body slider move until Save Settings (Save Settings Soon)
WHEEL_DIST_STEP = 0.04; DIST_SAVE_DELAY = 0.5   # mouse wheel over Jodi: CamDist per notch (up = closer); seconds after the last notch until Save Settings / slider update
POSE_H_LIE = 40.0; POSE_H_SIT = 70.0; POSE_MOVE = 6.0; POSE_T1 = 0.6; POSE_T2 = 1.8; POSE_TIMEOUT = 4.0; SCAN_GAP = 0.2; SCAN_GC = 10   # collect garbage every n poses: a run loads hundreds of montages (17 GB and an OOM kill without it)   # pelvis height over the floor / travel between the two samples
POSE_PROP_RADIUS = 600.0   # cm around Jodi: props a pose mod spawns (chair, table …) are cleaned up within this radius
# The four pieces of equipment a gun can carry. All derive from Gun_Equipment_Base_C, so a cast tells them apart, and
# Weapon_Gun_Base_C holds one variable per piece. Each can be left out of the forcing on its own, per model.
# (part, component class, array, letter for the picture's cache key, menu strings)
WEAPON_PARTS = [("Mag", P_MAGCOMP, "ForceSkipMag", "m", "Menu_MagExclude", "Menu_MagInclude"),
                ("Optics", P_OPTICSCOMP, "ForceSkipOptics", "o", "Menu_OpticsExclude", "Menu_OpticsInclude"),
                ("Barrel", P_BARRELCOMP, "ForceSkipBarrel", "b", "Menu_BarrelExclude", "Menu_BarrelInclude"),
                ("Grip", P_GRIPCOMP, "ForceSkipGrip", "g", "Menu_GripExclude", "Menu_GripInclude")]
# Eye colours: key -> (material instance on Jodi, vector parameter, menu string, category of the tile the row belongs to).
# Everything else follows from this table: menu rows, applying, resetting. The game writes the EyeTable colour onto the
# same parameters in Update Eyes Style, so AltUI's has to be put on after it. Kept per row (<key>#<row>), the way the game
# keeps hair colour per hairstyle - a colour belongs to the lens it was chosen on.
# Not in here, all tested in the game on 2026-09-25: ScleraColor (a TEXTURE parameter of M_EyeRefractive, not a colour),
# ScleraTint (its vector counterpart - no effect either, the white of Jodi's eye is not driven by it) and
# EyeCornerDarknessColor (a vector parameter, nothing of it visible).
EYE_PARTS = [("Iris", "Eye Material", "IrisColor", "Menu_EyeIris", "Eye"),
             ("Lashes", "Eyelashes Material", "MainColor", "Menu_Lashes", "Eyelashes")]
FORCE_SLOTS = 8   # material slots a forced skin covers: the most a weapon mesh in the wild has is six (Clatter Carbine)
ICON_SPAWN_WAIT = 3   # frames between spawning the weapon actor and taking its picture: what the game attaches by itself (the magazine is a component of its own) is not there in the frame of the spawn
ICON_PITCH = 36.0   # tile picture: the weapon's length axis tilted up by this much - muzzle into the upper left corner, grip to the lower right
JODI_DRAG_DEG = 0.5   # click on Jodi + drag: mesh yaw per pixel of mouse travel (negative dx factor: the side facing the viewer follows the cursor)
JODI_HEIGHT_CM = 0.35   # the same drag, vertically: camera height per pixel (positive dy = mouse down = camera up, so she follows the cursor as she does when turning)
HEIGHT_MIN, HEIGHT_MAX = -100.0, 100.0   # cm around the game's camera height: from below the knees to above her head
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


def f_begin_jodi_drag():
    """Click in the free area: cursor trace (Visibility) hits Jodi -> JodiDrag on, yes; otherwise no (the panel then leaves the click to the
    viewport = camera drag as before). GetHitResultUnderCursorByChannel is const -> pure."""
    g = G(); g.get("gpc", "PC"); g.call("hr", E_PC, "GetHitResultUnderCursorByChannel", inp={"self": "@gpc.PC", "TraceChannel": "TraceTypeQuery1", "bTraceComplex": "false"})
    g.call("bh", K_GS, "BreakHitResult", inp={"Hit": "@hr.HitResult"})
    g.get("gpl", "Player"); g.call("eq", K_MATH, "EqualEqual_ObjectObject", inp={"A": "@bh.HitActor", "B": "@gpl.Player"})
    g.call("hit", K_MATH, "BooleanAND", inp={"A": "@hr.ReturnValue", "B": "@eq.ReturnValue"}); g.branch("b", "@hit.ReturnValue")
    g.set("sd", "JodiDrag", inp={"JodiDrag": "true"}); g.set("sr", "JodiDragRight", inp={"JodiDragRight": "@entry.right"})
    g.get("gch", "CamHeight"); g.set("sz0", "JodiDragZ0", inp={"JodiDragZ0": "@gch.CamHeight"})   # End Jodi Drag saves only if the height really moved
    g.link("hit.ReturnValue", "return.yes")
    g.chain("entry", "b", "sd", "sr", "sz0", "return"); g.chain("b:else", "return")
    return fn("Begin Jodi Drag", [param("right", "bool")], [param("yes", "bool")], graph=g)


def f_jodi_drag():
    """Drag on Jodi: x yaws her mesh (relative to the capsule) by -dx * JODI_DRAG_DEG - actor, control rotation and camera stay.
    y moves the camera height by dy * JODI_HEIGHT_CM, clamped to HEIGHT_MIN..HEIGHT_MAX (with a slot in focus its FocusHeight instead). With CamRightHeight the two axes are
    split over the buttons: the left one only turns, the right one only lifts; without it either button does both."""
    g = G(); g.get("gcr", "CamRightHeight"); g.get("gjr", "JodiDragRight"); g.call("nr", K_MATH, "Not_PreBool", inp={"A": "@gjr.JodiDragRight"})
    g.call("norot", K_MATH, "BooleanAND", inp={"A": "@gcr.CamRightHeight", "B": "@gjr.JodiDragRight"})
    g.call("dorot", K_MATH, "Not_PreBool", inp={"A": "@norot.ReturnValue"}); g.branch("brot", "@dorot.ReturnValue")
    g.call("m", K_MATH, "Multiply_FloatFloat", inp={"A": "@entry.dx", "B": str(-JODI_DRAG_DEG)})
    g.call("rot", K_MATH, "MakeRotator", inp={"Roll": "0.0", "Pitch": "0.0", "Yaw": "@m.ReturnValue"})
    g.get("gpl", "Player"); g.get("gmc", "Mesh", cls=E_CHARACTER); g.link("gpl.Player", "gmc.self")
    g.call("ar", E_SCENECOMP, "K2_AddRelativeRotation", inp={"self": "@gmc.Mesh", "DeltaRotation": "@rot.ReturnValue", "bSweep": "false", "bTeleport": "true"})
    g.call("nohgt", K_MATH, "BooleanAND", inp={"A": "@gcr.CamRightHeight", "B": "@nr.ReturnValue"})
    g.call("dohgt", K_MATH, "Not_PreBool", inp={"A": "@nohgt.ReturnValue"}); g.branch("bhgt", "@dohgt.ReturnValue")
    g.call("dh", K_MATH, "Multiply_FloatFloat", inp={"A": "@entry.dy", "B": str(JODI_HEIGHT_CM)})
    g.get("gch", "CamHeight"); g.call("nh", K_MATH, "Add_FloatFloat", inp={"A": "@gch.CamHeight", "B": "@dh.ReturnValue"})
    g.call("nhc", K_MATH, "FClamp", inp={"Value": "@nh.ReturnValue", "Min": str(HEIGHT_MIN), "Max": str(HEIGHT_MAX)})
    g.set("sch", "CamHeight", inp={"CamHeight": "@nhc.ReturnValue"}); g.n("svs", "call_self", function="Set View Shift")
    # a slot in focus: its own height moves (same band), the saved camera height stays
    g.get("gfo", "FocusOn"); g.branch("bfo", "@gfo.FocusOn")
    g.get("gfh", "FocusHeight"); g.call("nf", K_MATH, "Add_FloatFloat", inp={"A": "@gfh.FocusHeight", "B": "@dh.ReturnValue"})
    g.call("nfc", K_MATH, "FClamp", inp={"Value": "@nf.ReturnValue", "Min": str(HEIGHT_MIN), "Max": str(HEIGHT_MAX)}); g.set("sfh", "FocusHeight", inp={"FocusHeight": "@nfc.ReturnValue"})
    g.chain("entry", "brot", "ar", "bhgt", "bfo", "sfh", "svs"); g.chain("bfo:else", "sch", "svs"); g.chain("brot:else", "bhgt")
    return fn("Jodi Drag", [param("dx", "float"), param("dy", "float")], graph=g)


def f_end_jodi_drag():
    """Drag over. A changed camera height is persisted here (the drag has a defined end, so no save timer as for the wheel);
    the Options slider is redrawn only while that page is shown."""
    g = G(); g.set("sd", "JodiDrag", inp={"JodiDrag": "false"})
    g.get("gch", "CamHeight"); g.get("gz0", "JodiDragZ0")
    g.call("same", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gch.CamHeight", "B": "@gz0.JodiDragZ0", "ErrorTolerance": "0.0001"})
    g.call("moved", K_MATH, "Not_PreBool", inp={"A": "@same.ReturnValue"}); g.branch("bm", "@moved.ReturnValue")
    g.n("sv", "call_self", function="Save Settings")
    g.get("gpo", "PanelOpen"); g.get("gpg", "Page"); g.call("isO", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Options"})
    g.call("ao", K_MATH, "BooleanAND", inp={"A": "@gpo.PanelOpen", "B": "@isO.ReturnValue"}); g.branch("bO", "@ao.ReturnValue"); g.n("rbo", "call_self", function="Rebuild Options")
    g.chain("entry", "sd", "bm", "sv", "bO", "rbo"); return fn("End Jodi Drag", graph=g)


def f_wheel_dist():
    """Mouse wheel over the free area beside the panel (over the panel it is skipped - plain background and a scroll box
    at its end let the notch through to the player controller, which moved the Jodi view while one scrolled a list):
    CamDist by WHEEL_DIST_STEP per notch (up = closer). Only Set View Shift runs per notch, not Apply Options: the latter
    re-anchors the panel and re-measures the chip boxes, which made a fast scroll stutter. Save Settings and the Options
    slider follow DIST_SAVE_DELAY after the last notch (DistSaveTimer counts down, also with the panel closed)."""
    g = G()
    g.get("gpo", "PanelOpen"); g.branch("bpo", "@gpo.PanelOpen")
    g.get("gpnl", "Panel"); g.call("opv", K_SYS, "IsValid", inp={"Object": "@gpnl.Panel"})
    g.get("gpnl2", "Panel"); g.call("ovp", W_PANEL, "Over Panel", inp={"self": "@gpnl2.Panel"})
    g.call("ovok", K_MATH, "BooleanAND", inp={"A": "@opv.ReturnValue", "B": "@ovp.yes"})
    g.call("novp", K_MATH, "Not_PreBool", inp={"A": "@ovok.ReturnValue"}); g.branch("bovp", "@novp.ReturnValue")   # cursor over the panel: the notch belongs to the panel, not to the camera
    g.get("gpc3", "PC"); g.call("wa", E_PC, "GetInputAnalogKeyState", inp={"self": "@gpc3.PC", "Key": "MouseWheelAxis"})   # axis value of this frame = sum of the notches (GetInputAxisKeyValue is not exposed to Blueprint in 4.27)
    g.call("nz", K_MATH, "NotEqual_FloatFloat", inp={"A": "@wa.ReturnValue", "B": "0.0"}); g.branch("bnz", "@nz.ReturnValue")
    g.call("st", K_MATH, "Multiply_FloatFloat", inp={"A": "@wa.ReturnValue", "B": str(WHEEL_DIST_STEP)}); g.get("gcd", "CamDist")
    g.call("nd", K_MATH, "Subtract_FloatFloat", inp={"A": "@gcd.CamDist", "B": "@st.ReturnValue"})   # wheel up = positive = closer (distance down)
    g.call("ndc", K_MATH, "FClamp", inp={"Value": "@nd.ReturnValue", "Min": str(DIST_MIN), "Max": str(DIST_MAX)})
    g.set("scd", "CamDist", inp={"CamDist": "@ndc.ReturnValue"}); g.n("apo", "call_self", function="Set View Shift")
    g.set("sdt", "DistSaveTimer", inp={"DistSaveTimer": str(DIST_SAVE_DELAY)})
    # pending save: count down, at <= 0 save + slider (Rebuild Options only while the Options page is shown)
    g.get("gt", "DistSaveTimer"); g.call("tp", K_MATH, "Greater_FloatFloat", inp={"A": "@gt.DistSaveTimer", "B": "0.0"}); g.branch("btp", "@tp.ReturnValue")
    g.get("gt2", "DistSaveTimer"); g.call("tm", K_MATH, "Subtract_FloatFloat", inp={"A": "@gt2.DistSaveTimer", "B": "@entry.dt"}); g.set("stm", "DistSaveTimer", inp={"DistSaveTimer": "@tm.ReturnValue"})
    g.get("gt3", "DistSaveTimer"); g.call("tz", K_MATH, "LessEqual_FloatFloat", inp={"A": "@gt3.DistSaveTimer", "B": "0.0"}); g.branch("btz", "@tz.ReturnValue")
    g.n("svd", "call_self", function="Save Settings")
    g.get("gpo2", "PanelOpen"); g.get("gpg", "Page"); g.call("isO", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Options"})
    g.call("ao", K_MATH, "BooleanAND", inp={"A": "@gpo2.PanelOpen", "B": "@isO.ReturnValue"}); g.branch("bO", "@ao.ReturnValue"); g.n("rbo", "call_self", function="Rebuild Options")
    g.chain("entry", "bpo", "bovp", "bnz", "scd", "apo", "sdt", "btp"); g.chain("bpo:else", "btp"); g.chain("bovp:else", "btp"); g.chain("bnz:else", "btp")
    g.chain("btp", "stm", "btz", "svd", "bO", "rbo")
    return fn("Wheel Dist", [param("dt", "float")], graph=g)


def f_cam_tick():
    """Per frame: free cam step, or photo mode end detection (Is In Photo Mode false -> End Photo Mode), or (no camera mode) Shift + wheel distance."""
    g = G(); g.get("gcm", "CamMode"); g.call("is1", K_MATH, "EqualEqual_IntInt", inp={"A": "@gcm.CamMode", "B": "1"}); g.branch("b1", "@is1.ReturnValue")
    g.n("st", "call_self", function="Free Cam Step", inp={"dt": "@entry.dt"})
    g.get("gcm2", "CamMode"); g.call("is2", K_MATH, "EqualEqual_IntInt", inp={"A": "@gcm2.CamMode", "B": "2"}); g.branch("b2", "@is2.ReturnValue")
    g.call("gs", K_GS, "GetGameState"); g.cast("cgs", P_GS2, "@gs.ReturnValue", pure=False, miss="ignore")
    g.call("ipm", P_GS2, "Is In Photo Mode", inp={"self": "@cgs.AsTKA Game State"}); g.branch("bp", "@ipm.yes")
    g.n("ep", "call_self", function="End Photo Mode")
    g.n("wd", "call_self", function="Wheel Dist", inp={"dt": "@entry.dt"})
    g.n("pw", "call_self", function="Poll Weapons"); g.n("mt", "call_self", function="Measure Tick", inp={"dt": "@entry.dt"}); g.n("sct", "call_self", function="Scan Tick", inp={"dt": "@entry.dt"})
    g.chain("entry", "b1", "st"); g.chain("b1:else", "b2", "cgs", "ipm", "bp"); g.chain("bp:else", "ep"); g.chain("b2:else", "wd", "pw", "mt", "sct")
    return fn("Cam Tick", [param("dt", "float")], graph=g)

def f_poll_options():
    g = G()
    g.get("gp", "Panel"); g.call("gv", W_PANEL, "Get Option Values", inp={"self": "@gp.Panel"})
    g.get("cs", "OptScroll"); g.get("cc", "OptScale"); g.get("cf", "OptFov"); g.get("cd", "OptDist"); g.get("chg", "OptHeight"); g.get("cba", "OptBgAlpha"); g.get("cta", "OptTileAlpha"); g.get("cgl", "OptGroupLen"); g.get("cch", "OptChipH")
    g.call("ngl", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.grouplen", "B": "@cgl.OptGroupLen", "ErrorTolerance": "0.0001"})
    g.call("nch", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.chiph", "B": "@cch.OptChipH", "ErrorTolerance": "0.0001"})
    g.call("ns", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.scroll", "B": "@cs.OptScroll", "ErrorTolerance": "0.0001"})
    g.call("nc", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.scale", "B": "@cc.OptScale", "ErrorTolerance": "0.0001"})
    g.call("nf", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.fov", "B": "@cf.OptFov", "ErrorTolerance": "0.0001"})
    g.call("nd", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.dist", "B": "@cd.OptDist", "ErrorTolerance": "0.0001"})
    g.call("nhg", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.height", "B": "@chg.OptHeight", "ErrorTolerance": "0.0001"})
    g.call("nba", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.bgalpha", "B": "@cba.OptBgAlpha", "ErrorTolerance": "0.0001"})
    g.call("nta", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.tilealpha", "B": "@cta.OptTileAlpha", "ErrorTolerance": "0.0001"})
    g.call("a0", K_MATH, "BooleanAND", inp={"A": "@ns.ReturnValue", "B": "@nc.ReturnValue"}); g.call("a1", K_MATH, "BooleanAND", inp={"A": "@a0.ReturnValue", "B": "@nf.ReturnValue"})
    g.call("a2", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@nd.ReturnValue"}); g.call("a3", K_MATH, "BooleanAND", inp={"A": "@a2.ReturnValue", "B": "@nba.ReturnValue"})
    g.call("a4", K_MATH, "BooleanAND", inp={"A": "@a3.ReturnValue", "B": "@nta.ReturnValue"})
    g.call("a5", K_MATH, "BooleanAND", inp={"A": "@a4.ReturnValue", "B": "@ngl.ReturnValue"})
    g.call("a6", K_MATH, "BooleanAND", inp={"A": "@a5.ReturnValue", "B": "@nch.ReturnValue"})
    g.call("a7", K_MATH, "BooleanAND", inp={"A": "@a6.ReturnValue", "B": "@nhg.ReturnValue"}); prev = "@a7.ReturnValue"
    for k in ("OutfitScale", "LookScale", "OutfitCols", "OutfitRows", "QuickAlpha"):   # outfit / look tiles, quick menu opacity
        g.get("co" + k, "Opt" + k); g.call("n" + k, K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv." + k.lower(), "B": "@co%s.Opt%s" % (k, k), "ErrorTolerance": "0.0001"})
        g.call("an" + k, K_MATH, "BooleanAND", inp={"A": prev, "B": "@n%s.ReturnValue" % k}); prev = "@an%s.ReturnValue" % k
    g.call("a", K_MATH, "BooleanAND", inp={"A": prev, "B": "true"}); g.branch("bsame", "@a.ReturnValue")
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
    g.get("gcsh", "ChipSearchShown"); g.call("csne", K_MATH, "NotEqual_BoolBool", inp={"A": "@gv.chipsearch", "B": "@gcsh.ChipSearchShown"}); g.branch("bcs", "@csne.ReturnValue")
    g.set("scsh", "ChipSearchShown", inp={"ChipSearchShown": "@gv.chipsearch"})
    g.n("rst2", "call_self", function="Rebuild SubTabs"); g.n("rlch2", "call_self", function="Rebuild Look Chips"); g.n("svcs", "call_self", function="Save Settings")
    # tooltip options: pages rebuild their tiles when opened (Select Page), so only store + save
    g.get("gtp", "TipNoPrefix"); g.call("tpne", K_MATH, "NotEqual_BoolBool", inp={"A": "@gv.tipnoprefix", "B": "@gtp.TipNoPrefix"}); g.branch("btp", "@tpne.ReturnValue")
    g.set("stp", "TipNoPrefix", inp={"TipNoPrefix": "@gv.tipnoprefix"}); g.n("svtp", "call_self", function="Save Settings")
    g.get("gtn", "TipNoIds"); g.call("tnne", K_MATH, "NotEqual_BoolBool", inp={"A": "@gv.tipnoids", "B": "@gtn.TipNoIds"}); g.branch("btn", "@tnne.ReturnValue")
    g.set("stn", "TipNoIds", inp={"TipNoIds": "@gv.tipnoids"}); g.n("svtn", "call_self", function="Save Settings")
    # which button drags the camera height: read by Jodi Drag, so storing it is all there is to do
    g.get("gcr", "CamRightHeight"); g.call("crne", K_MATH, "NotEqual_BoolBool", inp={"A": "@gv.camright", "B": "@gcr.CamRightHeight"}); g.branch("bcr", "@crne.ReturnValue")
    g.set("scr", "CamRightHeight", inp={"CamRightHeight": "@gv.camright"}); g.n("svcr", "call_self", function="Save Settings")
    g.set("os", "OptScroll", inp={"OptScroll": "@gv.scroll"}); g.set("oc", "OptScale", inp={"OptScale": "@gv.scale"}); g.set("of", "OptFov", inp={"OptFov": "@gv.fov"}); g.set("od", "OptDist", inp={"OptDist": "@gv.dist"}); g.set("ohg", "OptHeight", inp={"OptHeight": "@gv.height"})
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
    def snap(id, expr, lo, span, steps=20):   # steps per 1.0: 20 = 5 %, TILE_STEPS = 1 %
        g.call(id + "a", K_MATH, "Multiply_FloatFloat", inp={"A": expr, "B": str(span)}); g.call(id + "b", K_MATH, "Add_FloatFloat", inp={"A": "@%sa.ReturnValue" % id, "B": str(lo)})
        g.call(id + "c", K_MATH, "Multiply_FloatFloat", inp={"A": "@%sb.ReturnValue" % id, "B": str(float(steps))}); g.call(id + "d", K_MATH, "Round", inp={"A": "@%sc.ReturnValue" % id})
        g.call(id + "e", K_MATH, "Conv_IntToFloat", inp={"InInt": "@%sd.ReturnValue" % id}); g.call(id + "f", K_MATH, "Divide_FloatFloat", inp={"A": "@%se.ReturnValue" % id, "B": str(float(steps))})
        return "@%sf.ReturnValue" % id
    g.set("scf", "CamFov", inp={"CamFov": snap("f", "@gv.fov", FOV_MIN, FOV_MAX - FOV_MIN)}); g.set("scd", "CamDist", inp={"CamDist": snap("d", "@gv.dist", DIST_MIN, DIST_MAX - DIST_MIN)})
    g.set("sba", "BgAlpha", inp={"BgAlpha": snap("ba", "@gv.bgalpha", 0.0, 1.0)}); g.set("sta", "TileAlpha", inp={"TileAlpha": snap("ta", "@gv.tilealpha", 0.0, 1.0)})
    g.call("m1", K_MATH, "Multiply_FloatFloat", inp={"A": "@gv.scroll", "B": "9.0"}); g.call("m2", K_MATH, "Add_FloatFloat", inp={"A": "@m1.ReturnValue", "B": "1.0"})
    g.call("m3", K_MATH, "Multiply_FloatFloat", inp={"A": "@m2.ReturnValue", "B": "2.0"}); g.call("m4", K_MATH, "Round", inp={"A": "@m3.ReturnValue"}); g.call("m5", K_MATH, "Conv_IntToFloat", inp={"InInt": "@m4.ReturnValue"})
    g.call("m6", K_MATH, "Divide_FloatFloat", inp={"A": "@m5.ReturnValue", "B": "2.0"})     # in steps of 0.5
    g.set("ssm", "ScrollMult", inp={"ScrollMult": "@m6.ReturnValue"})
    g.set("sts", "TileScale", inp={"TileScale": snap("t", "@gv.scale", TILE_MIN, TILE_MAX - TILE_MIN, TILE_STEPS)})   # 1 % steps
    g.set("sos", "OutfitScale", inp={"OutfitScale": snap("tos", "@gv.outfitscale", TILE_MIN, TILE_MAX - TILE_MIN, TILE_STEPS)})
    g.set("sls", "LookScale", inp={"LookScale": snap("tls", "@gv.lookscale", TILE_MIN, LOOK_TILE_MAX - TILE_MIN, TILE_STEPS)})
    for k in ("OutfitCols", "OutfitRows"):   # 1 + Round(slider * (OUTFIT_MAX - 1))
        g.call("gm" + k, K_MATH, "Multiply_FloatFloat", inp={"A": "@gv." + k.lower(), "B": str(float(OUTFIT_MAX - 1))}); g.call("gr" + k, K_MATH, "Round", inp={"A": "@gm%s.ReturnValue" % k})
        g.call("ga" + k, K_MATH, "Add_IntInt", inp={"A": "@gr%s.ReturnValue" % k, "B": "1"}); g.set("s" + k, k, inp={k: "@ga%s.ReturnValue" % k})
    for k in ("OutfitScale", "LookScale", "OutfitCols", "OutfitRows", "QuickAlpha"): g.set("po" + k, "Opt" + k, inp={"Opt" + k: "@gv." + k.lower()})
    # quick menu opacity in 5 % steps, at least 5 % (0 in the settings means "follow the panel background")
    g.call("qamx", K_MATH, "FMax", inp={"A": snap("qa", "@gv.quickalpha", 0.0, 1.0), "B": "0.05"}); g.set("sqa", "QuickAlpha", inp={"QuickAlpha": "@qamx.ReturnValue"})
    # camera height in whole centimetres: the snap helper above rounds to 1/20 of the value, which does nothing on a cm scale
    g.call("hgta", K_MATH, "Multiply_FloatFloat", inp={"A": "@gv.height", "B": str(HEIGHT_MAX - HEIGHT_MIN)}); g.call("hgtb", K_MATH, "Add_FloatFloat", inp={"A": "@hgta.ReturnValue", "B": str(HEIGHT_MIN)})
    g.call("hgtc", K_MATH, "Round", inp={"A": "@hgtb.ReturnValue"}); g.call("hgtd", K_MATH, "Conv_IntToFloat", inp={"InInt": "@hgtc.ReturnValue"})
    g.set("schg", "CamHeight", inp={"CamHeight": "@hgtd.ReturnValue"})
    g.n("ap", "call_self", function="Apply Options"); g.n("ath", "call_self", function="Apply Theme")
    tx1, tx2, tx3, tx4, tx5, tx6, tx7, tx8, tx9, tx10, tx11, tx12, tx13, tx14 = opt_texts(g)
    g.get("gp2", "Panel"); g.call("sv", W_PANEL, "Set Option Values", inp={"self": "@gp2.Panel", "scroll": "@gv.scroll", "scale": "@gv.scale", "fov": "@gv.fov", "dist": "@gv.dist", "height": "@gv.height",
                                                                             "bgalpha": "@gv.bgalpha", "tilealpha": "@gv.tilealpha", "grouplen": "@gv.grouplen", "chiph": "@gv.chiph",
                                                                             "outfitscale": "@gv.outfitscale", "lookscale": "@gv.lookscale", "outfitcols": "@gv.outfitcols", "outfitrows": "@gv.outfitrows", "quickalpha": "@gv.quickalpha",
                                                                             "scroll text": tx1, "scale text": tx2, "fov text": tx3, "dist text": tx4, "height text": tx5, "bgalpha text": tx6, "tilealpha text": tx7, "grouplen text": tx8, "chiph text": tx9,
                                                                             "outfitscale text": tx10, "lookscale text": tx11, "outfitcols text": tx12, "outfitrows text": tx13, "quickalpha text": tx14})
    g.chain("entry", "gv", "sun", "bpn", "spn", "upf", "bnn"); g.chain("bpn:else", "bnn"); g.chain("bnn", "san", "apn", "svn", "bmg"); g.chain("bnn:else", "bmg")
    g.chain("bmg", "smg", "bga", "rst", "rli", "svm", "bmm"); g.chain("bmg:else", "bmm"); g.chain("bmm", "smm", "bgam", "sgm", "rlch", "rlca", "rlk", "svmm", "bcs"); g.chain("bmm:else", "bcs")
    g.chain("bcs", "scsh", "rst2", "rlch2", "svcs", "btp"); g.chain("bcs:else", "btp")
    g.chain("btp", "stp", "svtp", "btn"); g.chain("btp:else", "btn"); g.chain("btn", "stn", "svtn", "bcr"); g.chain("btn:else", "bcr"); g.chain("bcr", "scr", "svcr", "bsame"); g.chain("bcr:else", "bsame")
    g.chain("bsame:else", "os", "oc", "of", "od", "ohg", "oba", "ota", "ogl", "och", "poOutfitScale", "poLookScale", "poOutfitCols", "poOutfitRows", "poQuickAlpha", "sqa", "ssm", "sts", "sos", "sls", "sOutfitCols", "sOutfitRows",
            "scf", "scd", "schg", "sba", "sta", "sgl", "sch", "ap", "ath", "sv")
    return fn("Poll Options", graph=g)


# ---------------- Status bar / history (undo, redo; 5 steps, clothes + appearance) ----------------
HISTORY_MAX = 5


def f_redo_weapon_icons():
    """Mark every tile of the current weapon for a fresh picture and rebuild both rows.

    A rendered tile is kept as a file, and Weapon Icon reads that file whenever it has one - so nothing would ever be
    taken again by itself. The marks go into IconRedo; Weapon Icon answers "no picture" for a marked key, which is what
    makes the rebuild take one, and Finish Photo strikes the key off again. Capture Photo overwrites the file, so no
    file has to be deleted - which a Blueprint could not do anyway.
    """
    g = G()
    g.get("gir", "IconRedo"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gir.IconRedo"})
    g.get("gcw", "CurrentWeapon")
    g.n("cs", "call_self", function="Current Skin"); g.n("cm", "call_self", function="Current Model")
    # one key per model tile (each shows the current skin) ...
    g.n("mods", "call_self", function="Models For Weapon", inp={"weapon": "@gcw.CurrentWeapon"})
    g.foreach("fm", "@mods.rows")
    g.n("mk", "call_self", function="Weapon Icon Key", inp={"weapon": "@gcw.CurrentWeapon", "model": "@fm.Array Element", "skin": "@cs.skin"})
    g.get("gir2", "IconRedo"); g.call("am", K_ARR, "Array_Add", inp={"TargetArray": "@gir2.IconRedo", "NewItem": "@mk.key"})
    # ... and one per skin tile (each shows the current model)
    g.n("skins", "call_self", function="Skins For Weapon", inp={"weapon": "@gcw.CurrentWeapon"})
    g.foreach("fs", "@skins.rows")
    g.n("sk", "call_self", function="Weapon Icon Key", inp={"weapon": "@gcw.CurrentWeapon", "model": "@cm.model", "skin": "@fs.Array Element"})
    g.get("gir3", "IconRedo"); g.call("as", K_ARR, "Array_Add", inp={"TargetArray": "@gir3.IconRedo", "NewItem": "@sk.key"})
    g.get("gwi", "WeaponIcons"); g.call("wc", K_MAP, "Map_Clear", inp={"TargetMap": "@gwi.WeaponIcons"})
    g.n("rws", "call_self", function="Rebuild Weapon Skins"); g.n("rwm", "call_self", function="Rebuild Weapon Models")
    # Current Skin / Current Model are pure: pulled, not chained
    g.chain("entry", "clr", "mods", "fm"); g.chain("fm", "am"); g.chain("fm:Completed", "skins", "fs")
    g.chain("fs", "as"); g.chain("fs:Completed", "wc", "rws", "rwm")
    return fn("Redo Weapon Icons", graph=g)


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
    # the right-hand zone: what the page can do, in the one place that does not scroll away with the content
    g.get("gpr", "Panel"); g.call("clr", W_PANEL, "Clear Status Right", inp={"self": "@gpr.Panel"})
    g.get("gpg", "Page")
    g.call("isps", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Poses"}); g.branch("bps", "@isps.ReturnValue")
    # poses: stop the pose, and measure every one of them - while the run is going the link shows its progress and cancels
    pw = create_widget(g, "pstop", W_TXT); set_manager(g, "smp", W_TXT, pw)
    g.call("pii", W_TXT, "Init", inp={"self": pw, "action": "PoseStop", "caption": tt(g, "plt", "Btn_StopPose")})
    g.get("gpp", "Panel"); g.call("apl", W_PANEL, "Add Status Right", inp={"self": "@gpp.Panel", "widget": pw})
    g.get("gsc", "Scanning"); g.call("cts", K_TXT, "Conv_TextToString", inp={"InText": tt(g, "ct1", "Btn_ScanCancel")})
    g.get("gsi", "ScanIndex"); g.call("i2s", K_STR, "Conv_IntToString", inp={"InInt": "@gsi.ScanIndex"})
    g.get("gsr", "ScanRows"); g.call("slen", K_ARR, "Array_Length", inp={"TargetArray": "@gsr.ScanRows"}); g.call("l2s", K_STR, "Conv_IntToString", inp={"InInt": "@slen.ReturnValue"})
    g.call("p1", K_STR, "Concat_StrStr", inp={"A": "@cts.ReturnValue", "B": " ("}); g.call("p2", K_STR, "Concat_StrStr", inp={"A": "@p1.ReturnValue", "B": "@i2s.ReturnValue"})
    g.call("p3", K_STR, "Concat_StrStr", inp={"A": "@p2.ReturnValue", "B": "/"}); g.call("p4", K_STR, "Concat_StrStr", inp={"A": "@p3.ReturnValue", "B": "@l2s.ReturnValue"})
    g.call("p5", K_STR, "Concat_StrStr", inp={"A": "@p4.ReturnValue", "B": ")"}); g.call("sts", K_TXT, "Conv_TextToString", inp={"InText": tt(g, "ct2", "Btn_ScanPoses")})
    g.call("csel", K_MATH, "SelectString", inp={"A": "@p5.ReturnValue", "B": "@sts.ReturnValue", "bPickA": "@gsc.Scanning"}); g.call("ctxt", K_TXT, "Conv_StringToText", inp={"InString": "@csel.ReturnValue"})
    g.call("asel", K_MATH, "SelectString", inp={"A": "PoseScanStop", "B": "PoseScan", "bPickA": "@gsc.Scanning"}); g.call("an", K_STR, "Conv_StringToName", inp={"InString": "@asel.ReturnValue"})
    sw = create_widget(g, "csw", W_TXT); set_manager(g, "smsw", W_TXT, sw)
    g.call("sli", W_TXT, "Init", inp={"self": sw, "action": "@an.ReturnValue", "caption": "@ctxt.ReturnValue"})
    g.get("gp5", "Panel"); g.call("al2", W_PANEL, "Add Status Right", inp={"self": "@gp5.Panel", "widget": sw})
    # weapons: take the tile pictures of this weapon again - the rendered ones are kept as files and never redone by themselves
    g.get("gpg2", "Page"); g.call("isw", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg2.Page", "B": "Weapons"}); g.branch("bws", "@isw.ReturnValue")
    rw = create_widget(g, "rfw", W_TXT); set_manager(g, "smr", W_TXT, rw)
    g.call("rii", W_TXT, "Init", inp={"self": rw, "action": "WeaponIconsRedo", "caption": tt(g, "rlt", "Btn_RedoIcons")})
    g.get("gpw", "Panel"); g.call("arl", W_PANEL, "Add Status Right", inp={"self": "@gpw.Panel", "widget": rw})
    g.chain(*tail, "clr", "bps")
    g.chain("bps", "pstop_cr", "smp", "pii", "apl", "csw_cr", "smsw", "sli", "al2", "bws")
    g.chain("bps:else", "bws")
    g.chain("bws", "rfw_cr", "smr", "rii", "arl")
    return fn("Rebuild Status", graph=g)


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
    g.get("gsc9", "SlotColors"); g.get("gec9", "EyeColors"); g.get("gmc9", "MakeupColors"); g.get("gfv9", "FaceValues"); g.get("gfa9", "FaceAdd")
    g.make("mk", S_SNAP, Face="@gfv9.FaceValues", FaceAdd="@gfa9.FaceAdd", SlotColors="@gsc9.SlotColors", EyeColors="@gec9.EyeColors", MakeupColors="@gmc9.MakeupColors", Worn="@gw.Worn", Makeup="@gmd.Makeup Data", Skin="@gsn.Skin Name", Hair="@hn.name", Colors="@gtc3.TmpColors", HairColor="@hc.color",
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
    # underwear right away: one Wear Queue Step per piece, counted on an array of its own (the last step can end in Finish Apply
    # Snapshot -> Select Page -> Rebuild Content, which refills TmpNames3)
    g.get("gu3", "TmpNames3"); g.set("sul", "SnapUnder", inp={"SnapUnder": "@gu3.TmpNames3"}); g.get("gu4", "SnapUnder"); g.foreach("f3", "@gu4.SnapUnder")
    g.set("sw0", "WearWait", inp={"WearWait": "0"}); g.n("ws", "call_self", function="Wear Queue Step")
    g.set("sw", "WearWait", inp={"WearWait": str(WEAR_WAIT_FIRST)})   # ticks before the next piece goes on (the pieces just taken off get destroyed first)
    g.chain("entry", "bpend", "sns", "snp"); g.chain("bpend:else", "sps", "spp", "pmc", "rs", "sn", "f1"); g.chain("f1", "b1"); g.chain("b1:else", "to")
    g.chain("f1:Completed", "cu", "co", "f2"); g.chain("f2", "fi", "bu", "au"); g.chain("bu:else", "ao"); g.chain("f2:Completed", "sq", "app", "sul", "f3"); g.chain("f3", "sw0", "ws"); g.chain("f3:Completed", "sw")
    return fn("Apply Snapshot", [param("snap", "struct:" + S_SNAP)], graph=g)


def f_start_next_snapshot():
    """Tick: a snapshot queued while another was being put on (NextPending) starts once that one is done."""
    g = G(); g.get("gnp", "NextPending"); g.get("gsp", "SnapPending"); g.call("nsp", K_MATH, "Not_PreBool", inp={"A": "@gsp.SnapPending"})
    g.call("go", K_MATH, "BooleanAND", inp={"A": "@gnp.NextPending", "B": "@nsp.ReturnValue"}); g.branch("b", "@go.ReturnValue")
    g.set("s0", "NextPending", inp={"NextPending": "false"}); g.get("gns", "NextSnap"); g.n("asn", "call_self", function="Apply Snapshot", inp={"snap": "@gns.NextSnap"})
    g.chain("entry", "b", "s0", "asn"); return fn("Start Next Snapshot", graph=g)


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
    # the game's own answer: Worn (Is Worn) is refreshed only when the queue is done, so a piece put on just now was not
    # in it yet and its outfit colour was skipped - it only took on the second time
    g.get("gpl6", "Player"); g.call("iw3", P_CPB, "is clothes wearing", inp={"self": "@gpl6.Player", "clothes name": "@gn.TmpName2"}); g.branch("b3", "@iw3.yes")
    g.call("cf", K_MAP, "Map_Find", inp={"TargetMap": "@bs.Colors", "Key": "@gn.TmpName2"}); g.branch("bcf", "@cf.ReturnValue")
    g.get("gpl4", "Player"); g.call("fcc", P_CPB, "Find Clothes Component With Name", inp={"self": "@gpl4.Player", "name": "@gn.TmpName2"})
    g.call("cv", K_SYS, "IsValid", inp={"Object": "@fcc.clothes comp"}); g.branch("bcv", "@cv.ReturnValue")
    g.call("chg", P_CC, "Change Color", inp={"self": "@fcc.clothes comp", "Color": "@cf.Value"})
    g.get("gpl5", "Player"); g.call("svc", P_CPB, "Save Clothes Color", inp={"self": "@gpl5.Player", "clothes name": "@gn.TmpName2", "color": "@cf.Value"})
    g.get("gplR", "Player"); g.call("rsc", P_CPB, "Restore Clothes Color", inp={"self": "@gplR.Player", "clothes": "@gn.TmpName2"})
    g.get("gn7", "TmpName2"); g.n("aic", "call_self", function="Apply Item Colors", inp={"name": "@gn7.TmpName2"})   # AltUI's slot colours come after the game's
    # queue empty -> finish the pending snapshot
    g.get("gq3", "WearQueue"); g.call("ln2", K_ARR, "Array_Length", inp={"TargetArray": "@gq3.WearQueue"}); g.call("eq0", K_MATH, "EqualEqual_IntInt", inp={"A": "@ln2.ReturnValue", "B": "0"})
    g.get("gsp", "SnapPending"); g.call("fin", K_MATH, "BooleanAND", inp={"A": "@eq0.ReturnValue", "B": "@gsp.SnapPending"}); g.branch("bfin", "@fin.ReturnValue")
    g.n("fs", "call_self", function="Finish Apply Snapshot")
    g.chain("entry", "bq", "bw", "sww"); g.chain("bw:else", "sn", "rm", "sww2", "fi", "bfi", "has", "bhas", "b2"); g.chain("bfi:else", "sadd"); g.chain("bhas:else", "sadd"); g.chain("sadd", "b3")
    g.chain("b2:else", "bkn", "tc_cs", "tc_fo"); g.chain("tc_fo", "tc_to"); g.chain("tc_fo:Completed", "we2", "bwe2", "b3"); g.chain("bwe2:else", "sadd"); g.chain("bkn:else", "we", "bwe", "b3"); g.chain("bwe:else", "sadd"); g.chain("b2", "b3")
    g.chain("b3", "bcf", "fcc", "bcv", "chg", "svc", "aic", "bfin"); g.chain("bcf:else", "rsc", "aic", "bfin"); g.chain("bcv:else", "aic", "bfin"); g.chain("b3:else", "bfin")
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
    g.n("rdc", "call_self", function="Reset Dropped Colors", inp={"next": "@bs.SlotColors", "colors": "@bs.Colors"})   # pieces the look leaves plain go back to default first
    g.set("ssc9", "SlotColors", inp={"SlotColors": "@bs.SlotColors"}); g.set("sec9", "EyeColors", inp={"EyeColors": "@bs.EyeColors"})   # the look's own colours
    g.set("smc9", "MakeupColors", inp={"MakeupColors": "@bs.MakeupColors"})
    g.set("sfa9", "FaceAdd", inp={"FaceAdd": "@bs.FaceAdd"})
    g.set("sfv9", "FaceValues", inp={"FaceValues": "@bs.Face"}); g.n("afc9", "call_self", function="Apply Face"); g.n("svf9", "call_self", function="Save Settings")   # an empty map (look from before the face tab) = the game's face
    g.get("gplC", "Player"); g.call("ues", P_JODI, "Update Eyes Style", inp={"self": "@gplC.Player"})
    g.n("aecS", "call_self", function="Apply Eye Colors")
    g.n("amcS", "call_self", function="Apply Makeup Colors")
    g.get("gplD", "Player"); g.call("rcp", P_CPB, "Reset Clothes Physics", inp={"self": "@gplD.Player"})
    g.n("aicA", "call_self", function="Apply All Item Colors")
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
    # a snapshot queued while this one was being put on starts on the next tick (Start Next Snapshot): started from here it ran
    # inside the underwear loop of the Apply Snapshot that called Wear Queue Step - a recursion that refilled its loop array
    g.chain("entry", "spp", "md", "smd", "sbo", "swa", "shi", "cb2", "cw2", "sbc", "bsk", "cs", "bh"); g.chain("bsk:else", "bh")
    g.chain("bh", "hrow", "bho", "ch", "chc"); g.chain("bho:else", "hpop", "chc"); g.chain("bh:else", "chc"); g.chain("hrow:Row Not Found", "chc")   # hairstyle gone (mod removed) -> keep going
    g.chain("chc", "svh", "umt", "rdc", "ssc9", "sec9", "smc9", "sfa9", "sfv9", "afc9", "svf9", "ues", "aecS", "amcS", "rcp", "aicA", "sa", "sd", "bb", "ab", "bsc", "ssf", "sbv", "svs", "bms"); g.chain("bsc:else", "sbv"); g.chain("bb:else", "bsc"); g.chain("bms", "mpop", "rs2"); g.chain("bms:else", "rs2"); g.chain("rs2", "sp")
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


def f_preset_name_row():
    """Name row of the preset at `index`: its icon number. A custom name is kept under preset:<icon number>, not under the position -
    deleting another preset moves the positions up, the icon number (file Preset_<n>.jpg) stays with its preset."""
    g = G(); data = presets_data(g, "gd"); g.call("get", K_ARR, "Array_Get", inp={"TargetArray": data, "Index": "@entry.index"}); g.brk("bo", P_PRESET_S, "@get.Item")
    g.call("ns", K_STR, "Conv_IntToString", inp={"InInt": "@bo.IconNumber"}); g.call("nn", K_STR, "Conv_StringToName", inp={"InString": "@ns.ReturnValue"})
    g.link("nn.ReturnValue", "return.row")
    return fn("Preset Name Row", [param("index", "int")], [param("row", "name")], graph=g, pure=True)


def f_preset_shown_name():
    """Shown name of the preset at `index`: the custom name (Manage / Rename), else "Preset <position>" as before."""
    g = G(); g.call("i1", K_MATH, "Add_IntInt", inp={"A": "@entry.index", "B": "1"}); g.call("i1s", K_STR, "Conv_IntToString", inp={"InInt": "@i1.ReturnValue"})
    g.call("df", K_STR, "Concat_StrStr", inp={"A": "Preset ", "B": "@i1s.ReturnValue"}); g.n("nr", "call_self", function="Preset Name Row", inp={"index": "@entry.index"})
    g.n("sn", "call_self", function="Shown Name", inp={"kind": "preset", "row": "@nr.row", "default": "@df.ReturnValue"})
    g.link("sn.name", "return.s"); g.link("df.ReturnValue", "return.default")
    return fn("Preset Shown Name", [param("index", "int")], [param("s", "string"), param("default", "string")], graph=g, pure=True)


def presets_data(g, id):
    g.get(id + "_p", "Presets"); g.get(id, "Data", cls=P_PRESET_SAVE); g.link(id + "_p.Presets", id + ".self"); return "@%s.Data" % id


def f_preset_clicked():
    g = G(); data = presets_data(g, "gd")
    g.call("get", K_ARR, "Array_Get", inp={"TargetArray": data, "Index": "@entry.index"}); g.set("st", "TmpPreset", inp={"TmpPreset": "@get.Item"})
    g.get("gpl", "Player"); g.get("gtp", "TmpPreset"); g.call("ap", P_JODI, "Apply Makeup Preset", inp={"self": "@gpl.Player", "data": "@gtp.TmpPreset"})
    g.n("sa", "call_self", function="Save Worn")
    g.set("sd", "MakeupDirty", inp={"MakeupDirty": "true"}); g.n("rl", "call_self", function="Rebuild Look")
    # AltUI's own eye / make-up colours of this preset (Settings.PresetColors); none stored = the factory colours, as with an old look
    g.get("gtp2", "TmpPreset"); g.brk("btp", P_PRESET_S, "@gtp2.TmpPreset")
    g.get("gpc", "PresetColors"); g.call("fpc", K_MAP, "Map_Find", inp={"TargetMap": "@gpc.PresetColors", "Key": "@btp.IconNumber"}); g.brk("bpc", S_PRESETCOL, "@fpc.Value")
    g.set("sec", "EyeColors", inp={"EyeColors": "@bpc.EyeColors"}); g.set("smc", "MakeupColors", inp={"MakeupColors": "@bpc.MakeupColors"})
    g.get("gplu", "Player"); g.call("ues", P_JODI, "Update Eyes Style", inp={"self": "@gplu.Player"})   # the EyeTable colour back first
    g.n("aec", "call_self", function="Apply Eye Colors"); g.n("amc", "call_self", function="Apply Makeup Colors"); g.n("svs", "call_self", function="Save Settings")
    g.n("ph", "call_self", function="Push History"); g.chain("entry", "ph", "st", "ap", "sec", "smc", "ues", "aec", "amc", "svs", "sa", "sd", "rl"); return fn("Preset Clicked", [param("index", "int")], graph=g)


def f_store_preset_colors():
    """Settings.PresetColors[number] = the current eye and make-up colours (the game's preset keeps everything else)."""
    g = G(); g.get("gec", "EyeColors"); g.get("gmc", "MakeupColors"); g.make("mk", S_PRESETCOL, EyeColors="@gec.EyeColors", MakeupColors="@gmc.MakeupColors")
    g.get("gpc", "PresetColors"); g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gpc.PresetColors", "Key": "@entry.number", "Value": "@mk.S_PresetColors"})
    g.n("sv", "call_self", function="Save Settings"); g.chain("entry", "add", "sv")
    return fn("Store Preset Colors", [param("number", "int")], graph=g)


def f_preset_add():
    g = G(); md = makeup_data(g, "md")
    g.get("gp", "Presets"); g.call("add", P_PRESET_SAVE, "Add New Preset", inp={"self": "@gp.Presets", "makeup": md})
    g.get("gp2", "Presets"); g.call("sv", P_PRESET_SAVE, "Save Makeup Preset", inp={"self": "@gp2.Presets"})
    g.n("spc", "call_self", function="Store Preset Colors", inp={"number": "@add.number"})
    g.n("cap", "call_self", function="Capture Preset Icon", inp={"number": "@add.number"})
    g.n("rc", "call_self", function="Rebuild Look Cats"); g.n("rl", "call_self", function="Rebuild Look")
    g.chain("entry", "md", "add", "sv", "spc", "cap", "rc", "rl"); return fn("Preset Add", graph=g)


E_SKELMAT = "/Script/Engine.SkeletalMaterial"
E_CANVAS = "/Script/Engine.Canvas"
T_ROUNDBOX = M + "/T_RoundBox"   # white, alpha-masked: with RenderColor it paints exactly that colour
E_PRIM = "/Script/Engine.PrimitiveComponent"; E_MID = "/Script/Engine.MaterialInstanceDynamic"; K_MATLIB = "/Script/Engine.KismetMaterialLibrary"
E_SKELC = "/Script/Engine.SkeletalMeshComponent"; E_SMC = "/Script/Engine.StaticMeshComponent"
E_STATICMESH = "/Script/Engine.StaticMesh"
E_SCAP = "/Script/Engine.SceneCapture2D"; E_SCAPC = "/Script/Engine.SceneCaptureComponent2D"; E_SCAPCB = "/Script/Engine.SceneCaptureComponent"; E_SCENEC = "/Script/Engine.SceneComponent"; E_CHAR = "/Script/Engine.Character"; E_CAMC = "/Script/Engine.CameraComponent"


def f_capture_photo():
    """SceneCapture2D `distance` cm in front of `target` (along Jodi's forward vector, turned with her mesh) and `rise` cm above it, looking at `target`; fill light whose
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
    g.get("gpl2", "Player"); g.call("fwd0", E_ACTOR, "GetActorForwardVector", inp={"self": "@gpl2.Player"})
    # Jodi turned by dragging (only the mesh turns, the actor stays): the camera goes round with her by the same yaw, so the
    # photo shows her front. Not for PhotoOnly (weapon icons: an actor of their own) and not with the panel closed (JodiMeshRot unset).
    g.get("gplr", "Player"); g.get("gmr", "Mesh", cls=E_CHARACTER); g.link("gplr.Player", "gmr.self")
    g.get("grr", "RelativeRotation", cls=E_SCENECOMP); g.link("gmr.Mesh", "grr.self"); g.call("brr", K_MATH, "BreakRotator", inp={"InRot": "@grr.RelativeRotation"})
    g.get("gjr", "JodiMeshRot"); g.call("bjr", K_MATH, "BreakRotator", inp={"InRot": "@gjr.JodiMeshRot"})
    g.call("dyaw", K_MATH, "Subtract_FloatFloat", inp={"A": "@brr.Yaw", "B": "@bjr.Yaw"})
    g.get("gpoj", "PhotoOnly"); g.call("pvj", K_SYS, "IsValid", inp={"Object": "@gpoj.PhotoOnly"}); g.call("npj", K_MATH, "Not_PreBool", inp={"A": "@pvj.ReturnValue"})
    g.get("gpnj", "PanelOpen"); g.call("usej", K_MATH, "BooleanAND", inp={"A": "@gpnj.PanelOpen", "B": "@npj.ReturnValue"})
    g.call("yaw", K_MATH, "SelectFloat", inp={"A": "@dyaw.ReturnValue", "B": "0.0", "bPickA": "@usej.ReturnValue"})
    g.call("fwd", K_MATH, "RotateAngleAxis", inp={"InVect": "@fwd0.ReturnValue", "AngleDeg": "@yaw.ReturnValue", "Axis": "(X=0,Y=0,Z=1)"})
    # PhotoFace (close-ups: preset icons, saved faces): "from the front" means the face, not the body - in the appearance poses the head
    # is often turned. Face direction = horizontal perpendicular to the eye line (Eye_L -> Eye_R), on the side the body faces.
    # A body without the eye bones (both sockets fall back to the component) keeps the body direction.
    g.get("gpe", "Player"); g.get("gme", "Mesh", cls=E_CHARACTER); g.link("gpe.Player", "gme.self")
    g.call("eyl", E_SCENEC, "GetSocketLocation", inp={"self": "@gme.Mesh", "InSocketName": "Eye_L"}); g.call("eyr", E_SCENEC, "GetSocketLocation", inp={"self": "@gme.Mesh", "InSocketName": "Eye_R"})
    g.call("eyd", K_MATH, "Subtract_VectorVector", inp={"A": "@eyr.ReturnValue", "B": "@eyl.ReturnValue"}); g.call("eyb", K_MATH, "BreakVector", inp={"InVec": "@eyd.ReturnValue"})
    g.call("eyh", K_MATH, "MakeVector", inp={"X": "@eyb.X", "Y": "@eyb.Y", "Z": "0.0"})
    g.call("eyc", K_MATH, "Cross_VectorVector", inp={"A": "@eyh.ReturnValue", "B": "(X=0,Y=0,Z=1)"}); g.call("eyn", K_MATH, "Normal", inp={"A": "@eyc.ReturnValue", "Tolerance": "0.0001"})
    g.call("eydt", K_MATH, "Dot_VectorVector", inp={"A": "@eyn.ReturnValue", "B": "@fwd.ReturnValue"}); g.call("eypos", K_MATH, "GreaterEqual_FloatFloat", inp={"A": "@eydt.ReturnValue", "B": "0.0"})
    g.call("eyneg", K_MATH, "Multiply_VectorFloat", inp={"A": "@eyn.ReturnValue", "B": "-1.0"})
    g.call("eyf", K_MATH, "SelectVector", inp={"A": "@eyn.ReturnValue", "B": "@eyneg.ReturnValue", "bPickA": "@eypos.ReturnValue"})
    g.call("eylen", K_MATH, "VSize", inp={"A": "@eyh.ReturnValue"}); g.call("eyok", K_MATH, "Greater_FloatFloat", inp={"A": "@eylen.ReturnValue", "B": "0.5"})   # eyes ~6 cm apart
    g.get("gpf", "PhotoFace"); g.call("usef", K_MATH, "BooleanAND", inp={"A": "@gpf.PhotoFace", "B": "@eyok.ReturnValue"})
    g.call("ffw", K_MATH, "SelectVector", inp={"A": "@eyf.ReturnValue", "B": "@fwd.ReturnValue", "bPickA": "@usef.ReturnValue"})
    g.call("fv", K_MATH, "Multiply_VectorFloat", inp={"A": "@ffw.ReturnValue", "B": "@entry.distance"})
    g.call("cl0", K_MATH, "Add_VectorVector", inp={"A": "@entry.target", "B": "@fv.ReturnValue"})
    g.call("up", K_MATH, "MakeVector", inp={"X": "0.0", "Y": "0.0", "Z": "@entry.rise"})
    g.call("cl", K_MATH, "Add_VectorVector", inp={"A": "@cl0.ReturnValue", "B": "@up.ReturnValue"})
    g.call("rot", K_MATH, "FindLookAtRotation", inp={"Start": "@cl.ReturnValue", "Target": "@entry.target"})
    # PhotoView ("as seen", lower half of a "+" tile): the view of the game camera next to the panel - same direction, `distance` cm
    # back from `target` along it (so the frame stays centred like the front photo); `rise` is left to the camera's own pitch
    g.call("pcm", K_GS, "GetPlayerCameraManager", inp={"PlayerIndex": "0"})
    g.call("crot", "/Script/Engine.PlayerCameraManager", "GetCameraRotation", inp={"self": "@pcm.ReturnValue"})
    g.call("cfw", K_MATH, "GetForwardVector", inp={"InRot": "@crot.ReturnValue"}); g.call("cbk", K_MATH, "Multiply_VectorFloat", inp={"A": "@cfw.ReturnValue", "B": "@entry.distance"})
    g.call("vloc", K_MATH, "Subtract_VectorVector", inp={"A": "@entry.target", "B": "@cbk.ReturnValue"})
    g.get("gpvw", "PhotoView"); g.call("usev", K_MATH, "BooleanAND", inp={"A": "@gpvw.PhotoView", "B": "@npj.ReturnValue"})   # never for PhotoOnly (weapon icons)
    g.call("floc", K_MATH, "SelectVector", inp={"A": "@vloc.ReturnValue", "B": "@cl.ReturnValue", "bPickA": "@usev.ReturnValue"})
    g.call("frot", K_MATH, "SelectRotator", inp={"A": "@crot.ReturnValue", "B": "@rot.ReturnValue", "bPickA": "@usev.ReturnValue"})
    # a wall or furniture between Jodi and the front camera point (2 m for a look): the camera moves in front of it, 15 cm
    # short of the hit, and widens its angle so the frame stays the same - otherwise it sat behind the wall and the fill
    # light lit the wall from a few cm: a white photo. Not for "as seen" (the game camera's own point) or weapon icons.
    g.get("gplt", "Player"); g.n("ignp", "make_array", count=1, type="object:" + E_ACTOR, inp={"[0]": "@gplt.Player"})
    g.call("ptr", K_SYS, "LineTraceSingle", inp={"Start": "@entry.target", "End": "@floc.ReturnValue", "TraceChannel": "TraceTypeQuery1", "bTraceComplex": "false",
                                                 "ActorsToIgnore": "@ignp.Array", "DrawDebugType": "None", "bIgnoreSelf": "true",
                                                 "TraceColor": "(R=1,G=0,B=0,A=1)", "TraceHitColor": "(R=0,G=1,B=0,A=1)", "DrawTime": "5.0"})
    g.call("ptb", K_GS, "BreakHitResult", inp={"Hit": "@ptr.OutHit"})
    g.call("nusv", K_MATH, "Not_PreBool", inp={"A": "@usev.ReturnValue"}); g.call("pfr", K_MATH, "BooleanAND", inp={"A": "@nusv.ReturnValue", "B": "@npj.ReturnValue"})
    g.call("pap", K_MATH, "BooleanAND", inp={"A": "@pfr.ReturnValue", "B": "@ptr.ReturnValue"})
    g.call("pvec", K_MATH, "Subtract_VectorVector", inp={"A": "@floc.ReturnValue", "B": "@entry.target"}); g.call("pfull", K_MATH, "VSize", inp={"A": "@pvec.ReturnValue"})
    g.call("pnd0", K_MATH, "Subtract_FloatFloat", inp={"A": "@ptb.Distance", "B": "15.0"}); g.call("pnd", K_MATH, "FMax", inp={"A": "@pnd0.ReturnValue", "B": "20.0"})
    g.call("pdir", K_MATH, "Normal", inp={"A": "@pvec.ReturnValue", "Tolerance": "0.0001"}); g.call("poff", K_MATH, "Multiply_VectorFloat", inp={"A": "@pdir.ReturnValue", "B": "@pnd.ReturnValue"})
    g.call("ploc2", K_MATH, "Add_VectorVector", inp={"A": "@entry.target", "B": "@poff.ReturnValue"})
    g.call("ploc", K_MATH, "SelectVector", inp={"A": "@ploc2.ReturnValue", "B": "@floc.ReturnValue", "bPickA": "@pap.ReturnValue"})
    g.call("pr", K_MATH, "Divide_FloatFloat", inp={"A": "@pfull.ReturnValue", "B": "@pnd.ReturnValue"}); g.call("pt", K_MATH, "Multiply_FloatFloat", inp={"A": "@pr.ReturnValue", "B": "0.24933"})   # tan(14°)
    g.call("pa", K_MATH, "DegAtan", inp={"A": "@pt.ReturnValue"}); g.call("pf2", K_MATH, "Multiply_FloatFloat", inp={"A": "@pa.ReturnValue", "B": "2.0"})
    g.call("pf3", K_MATH, "FMin", inp={"A": "@pf2.ReturnValue", "B": "110.0"})
    g.call("pfov", K_MATH, "SelectFloat", inp={"A": "@pf3.ReturnValue", "B": "28.0", "bPickA": "@pap.ReturnValue"})
    g.call("pdst", K_MATH, "SelectFloat", inp={"A": "@pnd.ReturnValue", "B": "@entry.distance", "bPickA": "@pap.ReturnValue"})   # the fill light's distance
    g.call("tf", K_MATH, "MakeTransform", inp={"Location": "@ploc.ReturnValue", "Rotation": "@frot.ReturnValue", "Scale": "(X=1,Y=1,Z=1)"})
    g.n("sp", "spawn", cls=E_SCAP, inp={"SpawnTransform": "@tf.ReturnValue"})
    g.get("gc", "CaptureComponent2D", cls=E_SCAP); g.link("sp.ReturnValue", "gc.self")
    g.get("grt2", "PhotoRT")
    g.n("st", "set", var="TextureTarget", cls=E_SCAPC, inp={"self": "@gc.CaptureComponent2D", "TextureTarget": "@grt2.PhotoRT"})
    g.n("sf", "set", var="FOVAngle", cls=E_SCAPC, inp={"self": "@gc.CaptureComponent2D", "FOVAngle": "@pfov.ReturnValue"})
    g.n("ss", "set", var="CaptureSource", cls=E_SCAPC, inp={"self": "@gc.CaptureComponent2D", "CaptureSource": "SCS_FinalColorLDR"})
    g.n("se", "set", var="bCaptureEveryFrame", cls=E_SCAPC, inp={"self": "@gc.CaptureComponent2D", "bCaptureEveryFrame": "true"})
    # PhotoOnly (weapon icons): the capture shows that actor alone - no room and no Jodi behind the weapon
    g.get("gpo", "PhotoOnly"); g.call("pov", K_SYS, "IsValid", inp={"Object": "@gpo.PhotoOnly"}); g.branch("bpo", "@pov.ReturnValue")
    g.get("gpo2", "PhotoOnly")
    g.call("so", E_SCAPCB, "ShowOnlyActorComponents", inp={"self": "@gc.CaptureComponent2D", "InActor": "@gpo2.PhotoOnly", "bIncludeFromChildActors": "true"})
    # take over the game camera's post-process (exposure/bias as in the game image), blend 1
    g.get("gpl3", "Player"); g.get("gcam", "Camera", cls=P_JODI); g.link("gpl3.Player", "gcam.self")
    g.get("pps", "PostProcessSettings", cls=E_CAMC); g.link("gcam.Camera", "pps.self")
    g.n("spp", "set", var="PostProcessSettings", cls=E_SCAPC, inp={"self": "@gc.CaptureComponent2D", "PostProcessSettings": "@pps.PostProcessSettings"})
    g.n("spw", "set", var="PostProcessBlendWeight", cls=E_SCAPC, inp={"self": "@gc.CaptureComponent2D", "PostProcessBlendWeight": "1.0"})
    # fill light at the camera point (only during the capture; like the light in the mirror room), radius = 2 x distance,
    # intensity 400 cd x (distance / 55 cm)^2: inverse-square falloff -> Jodi gets the same illuminance at every capture distance
    g.n("spl", "spawn", cls="/Script/Engine.SpotLight", inp={"SpawnTransform": "@tf.ReturnValue"})
    g.get("glc", "SpotLightComponent", cls="/Script/Engine.SpotLight"); g.link("spl.ReturnValue", "glc.self")
    g.call("rad", K_MATH, "Multiply_FloatFloat", inp={"A": "@pdst.ReturnValue", "B": "2.0"})
    g.call("dq", K_MATH, "Divide_FloatFloat", inp={"A": "@pdst.ReturnValue", "B": "55.0"}); g.call("dsq", K_MATH, "Multiply_FloatFloat", inp={"A": "@dq.ReturnValue", "B": "@dq.ReturnValue"})
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
    g.set("rpv", "PhotoView", inp={"PhotoView": "false"})   # one photo only: later ones (lazy tile photos, updates) are front photos again unless asked
    g.set("rpf", "PhotoFace", inp={"PhotoFace": "false"})
    g.chain("entry", "bpv", "bia", "dsa", "dsl", "crt", "srt", "ptr", "sp", "st", "sf", "ss", "se", "bpo", "so", "spp", "spw", "spl", "li", "lr", "lo", "ls", "lrot", "li2", "sil", "sia", "sdir", "sfile", "sif", "rpv", "rpf")
    g.chain("bia:else", "crt"); g.chain("bpo:else", "spp")
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
    g.set("spf", "PhotoFace", inp={"PhotoFace": "true"})
    g.chain("entry", "sk", "sin", "spf", "cap"); return fn("Capture Preset Icon", [param("number", "int")], graph=g)


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
    g.get("gk0", "PhotoKind"); g.call("isw", K_MATH, "EqualEqual_NameName", inp={"A": "@gk0.PhotoKind", "B": "Weapon"}); g.branch("bw", "@isw.ReturnValue")
    g.get("gwa", "IconWeaponActor"); g.call("dsw", E_ACTOR, "K2_DestroyActor", inp={"self": "@gwa.IconWeaponActor"})
    g.get("gpw", "PhotoWeapon"); g.get("gps", "PhotoSkin"); g.get("gpm", "PhotoModel")
    g.n("wk", "call_self", function="Weapon Icon Key", inp={"weapon": "@gpw.PhotoWeapon", "model": "@gpm.PhotoModel", "skin": "@gps.PhotoSkin"})
    g.get("gwi", "WeaponIcons"); g.call("wrm", K_MAP, "Map_Remove", inp={"TargetMap": "@gwi.WeaponIcons", "Key": "@wk.key"})
    g.get("gir", "IconRedo"); g.call("rrm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gir.IconRedo", "Item": "@wk.key"})   # taken - the mark can go
    g.n("rws", "call_self", function="Rebuild Weapon Skins"); g.n("rwm", "call_self", function="Rebuild Weapon Models")
    g.get("gk", "PhotoKind"); g.call("isl", K_MATH, "EqualEqual_NameName", inp={"A": "@gk.PhotoKind", "B": "Look"}); g.branch("bl", "@isl.ReturnValue")
    g.get("gli", "LookIcons"); g.get("gin", "IconNumber"); g.call("lrm", K_MAP, "Map_Remove", inp={"TargetMap": "@gli.LookIcons", "Key": "@gin.IconNumber"}); g.n("rls", "call_self", function="Rebuild Looks")
    g.get("gpi", "PresetIcons"); g.get("gin2", "IconNumber"); g.call("prm", K_MAP, "Map_Remove", inp={"TargetMap": "@gpi.PresetIcons", "Key": "@gin2.IconNumber"}); g.n("rl", "call_self", function="Rebuild Look")
    g.get("gkf", "PhotoKind"); g.call("isf", K_MATH, "EqualEqual_NameName", inp={"A": "@gkf.PhotoKind", "B": "Face"}); g.branch("bf", "@isf.ReturnValue")
    g.get("gfi", "FaceIcons"); g.get("gin3", "IconNumber"); g.call("frm", K_MAP, "Map_Remove", inp={"TargetMap": "@gfi.FaceIcons", "Key": "@gin3.IconNumber"}); g.n("rfp", "call_self", function="Rebuild Face Page")
    g.chain("entry", "ex", "dst", "dsl", "bw", "dsw", "wrm", "rrm", "rws", "rwm"); g.chain("bw:else", "bl")
    g.chain("bl", "lrm", "rls"); g.chain("bl:else", "bf", "frm", "rfp"); g.chain("bf:else", "prm", "rl"); return fn("Finish Photo", graph=g)


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
    g.get("gpc", "PresetColors"); g.call("rpc", K_MAP, "Map_Remove", inp={"TargetMap": "@gpc.PresetColors", "Key": "@rm.number"}); g.n("svs", "call_self", function="Save Settings")
    g.n("rc", "call_self", function="Rebuild Look Cats"); g.n("rl", "call_self", function="Rebuild Look")
    g.chain("entry", "rm", "sv", "rpc", "svs", "rc", "rl"); return fn("Preset Delete", [param("index", "int")], graph=g)


def f_update_preset():
    """Overwrite a make-up preset with the current appearance (like Add New Preset: make-up, skin and body from the makeup save,
    hairstyle and hair colour as Jodi wears them - as Take Snapshot does); place and icon number stay, new photo."""
    g = G(); data = presets_data(g, "gd"); g.call("get", K_ARR, "Array_Get", inp={"TargetArray": data, "Index": "@entry.index"}); g.brk("bo", P_PRESET_S, "@get.Item")
    g.set("sin", "TmpI", inp={"TmpI": "@bo.IconNumber"}); g.get("gin", "TmpI")
    g.get("gpl", "Player"); g.call("md", P_JODI, "Get Makeup Data", inp={"self": "@gpl.Player"})
    g.get("gmd", "Makeup Data", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "gmd.self"); g.get("gsn", "Skin Name", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "gsn.self")
    g.get("gwa", "Waist", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "gwa.self"); g.get("ghp", "Hip", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "ghp.self")
    g.get("gbs", "Boobs Size", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "gbs.self")
    g.get("gpl2", "Player"); g.call("hn", P_JODI, "Get Hairstyle Name", inp={"self": "@gpl2.Player"}); g.get("gpl3", "Player"); g.call("hc", P_JODI, "Get Hairstyle Color", inp={"self": "@gpl3.Player"})
    g.make("mk", P_PRESET_S, HairstyleName="@hn.name", MakeupData="@gmd.Makeup Data", SkinName="@gsn.Skin Name", HairColor="@hc.color",
           Waist="@gwa.Waist", Hip="@ghp.Hip", BoobsSize="@gbs.Boobs Size", IconNumber="@gin.TmpI")
    g.set("stp", "TmpPreset", inp={"TmpPreset": "@mk.MakeupPreset_Struct"})
    data2 = presets_data(g, "gd2"); g.get("gtp", "TmpPreset"); g.call("set", K_ARR, "Array_Set", inp={"TargetArray": data2, "Index": "@entry.index", "Item": "@gtp.TmpPreset", "bSizeToFit": "false"})
    g.get("gp", "Presets"); g.call("sv", P_PRESET_SAVE, "Save Makeup Preset", inp={"self": "@gp.Presets"})
    g.get("gpi", "PresetIcons"); g.call("rmi", K_MAP, "Map_Remove", inp={"TargetMap": "@gpi.PresetIcons", "Key": "@gin.TmpI"})
    g.n("cap", "call_self", function="Capture Preset Icon", inp={"number": "@gin.TmpI"})
    g.n("rc", "call_self", function="Rebuild Look Cats"); g.n("rl", "call_self", function="Rebuild Look")
    g.n("spc", "call_self", function="Store Preset Colors", inp={"number": "@gin.TmpI"})
    g.chain("entry", "sin", "md", "stp", "set", "sv", "spc", "rmi", "cap", "rc", "rl")
    return fn("Update Preset", [param("index", "int")], graph=g)


def f_on_preset_context():
    def pre(g): g.set("sci", "ContextPreset", inp={"ContextPreset": "@entry.index"}); return ["sci"]
    g = simple_menu("On Preset Context", [("PresetApply", "Menu_Apply"), ("PresetView", "Menu_ViewContent"), ("Rename", "Menu_Rename"), ("PresetUpdate", "Menu_UpdateFront"), ("PresetUpdateView", "Menu_UpdateView"),
                                          ("PresetDelete", "Menu_Delete"), ("Cancel", "Menu_Cancel")], pre)
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
    # colour: one row per colourable material slot of a worn piece; reset only if it carries a colour of its own
    g.branch("bc", "@iw.yes")
    crows = color_menu_rows(g, "cc", "@entry.name")
    g.n("gcr", "call_self", function="Item Has Own Color", inp={"name": "@entry.name"}); g.branch("brc", "@gcr.found")
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
    g.chain("clr", *r8, *r0, "bc", *crows); g.chain("cc_fe:Completed", "gcr", "brc", *r6, "dm")
    g.chain("bc:else", "dm"); g.chain("brc:else", "dm")
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
    ("Fav", "Toggle Favorite", "ContextItem"), ("Hide", "Toggle Item Hidden", "ContextItem"),
    ("ClothesResetColor", "Slot Reset Color", "ContextItem"), ("MakeupColor", "Open Makeup Color", "ContextItem"),
    ("MakeupReset", "Makeup Reset Color", "ContextItem"), ("HairResetColor", "Hair Reset Color", "ContextItem"), ("HairColor", "Open Hair Color", None),
    ("PutInBag", "Put In Bag", "ContextItem"), ("BagWear", "Bag Toggle Wear", "ContextItem"), ("BagRepair", "Bag Repair", "ContextItem"),
    ("BagRemove", "Bag Remove", "ContextItem"), ("BagToWardrobe", "Bag To Wardrobe", "ContextItem"), ("BagCleanup", "Bag Cleanup", None), ("BagAllWorn", "Bag All Worn", None),
    ("OutfitWear", "On Outfit Clicked", "ContextOutfit"), ("OutfitRename", "Start Outfit Rename", "ContextOutfit"), ("OutfitDelete", "Delete Outfit", "ContextOutfit"),
    ("LookRename", "Start Look Rename", "ContextLook"), ("LookUpdate", "Update Look Front", "ContextLook"), ("LookUpdateView", "Update Look View", "ContextLook"), ("LookDelete", "Delete Look", "ContextLook"),
    ("PresetApply", "Preset Clicked", "ContextPreset"), ("PresetUpdate", "Update Preset Front", "ContextPreset"), ("PresetUpdateView", "Update Preset View", "ContextPreset"), ("PresetDelete", "Preset Delete", "ContextPreset"),
    ("OutfitView", "Open Outfit Content", "ContextOutfit"), ("LookView", "Open Look Content", "ContextLook"), ("PresetView", "Open Preset Content", "ContextPreset"),
    ("ContentBack", "Close Content", None), ("ThemeSave", "Theme Save", None), ("ClearManageChipSearch", "Clear Manage Chip Search Text", None), ("ThemePApply", "Apply Theme Preset", "ContextItem"), ("ThemePDelete", "Delete Theme Preset", "ContextItem"), ("GoTo", "Go To Item", "ContextItem"), ("ContentUse", "Content Use", "ContextItem"),
    ("OnlyGroup", "Show Only Group", "ContextItem"), ("ModContent", "Open Mod Content Of Item", "ContextItem"),
    ("Rename", "Start Item Rename", "ContextItem"), ("LookFav", "Toggle Look Favorite", "ContextItem"), ("LookHide", "Toggle Look Hidden", "ContextItem"), ("LookOnlyMod", "Look Only Mod", "ContextItem"), ("PoseFav", "Toggle Pose Favorite", "ContextItem"), ("PoseHide", "Toggle Pose Hidden", "ContextItem"), ("PoseOnlyMod", "Pose Only Mod", "ContextItem"), ("PoseReset", "Reset Pose Measurement", "ContextItem"), ("PoseSetStand", "Pose Set Stand", "ContextItem"), ("PoseSetSit", "Pose Set Sit", "ContextItem"), ("PoseSetLie", "Pose Set Lie", "ContextItem"), ("PoseSetMove", "Toggle Pose Moving", "ContextItem"), ("SkinFav", "Toggle Skin Favorite", "ContextItem"), ("SkinHide", "Toggle Skin Hidden", "ContextItem"), ("SkinOnlyMod", "Skin Only Mod", "ContextItem"), ("ModelFav", "Toggle Model Favorite", "ContextItem"), ("ModelHide", "Toggle Model Hidden", "ContextItem"), ("ModelOnlyMod", "Model Only Mod", "ContextItem"), ("ModelOwnIcon", "Toggle Model Own Icon", "ContextItem"), ("ModelForceSkin", "Toggle Model Force Skin", "ContextItem"), ] + [("ModelSkip" + p, "Toggle Model Skip " + p, "ContextItem") for p, _, _, _, _, _ in WEAPON_PARTS] + [
 ("PoseStop", "Stop Pose", None), ("PoseScan", "Start Pose Scan", None), ("PoseScanStop", "Stop Pose Scan", None), ("WeaponIconsRedo", "Redo Weapon Icons", None), ("RenameMod", "Rename Mod Of Item", "ContextItem"), ("RenameGroup", "Rename Group Of Item", "ContextItem"),
    ("HairNatural", "Toggle Hair Swatches", None), ("FaceAllFixed", "Face All Fixed", None), ("FaceAllGame", "Face All Game", None), ("FaceAddToggle", "Toggle Face Add", None),
    ("FaceApply", "Apply Saved Face", "ContextFace"), ("FaceRename", "Start Face Rename", "ContextFace"), ("FaceUpdate", "Update Face Front", "ContextFace"), ("FaceUpdateView", "Update Face View", "ContextFace"), ("FaceDelete", "Delete Face", "ContextFace"), ("FaceView", "Open Face Content", "ContextFace"),
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
    g.set("scd", "CamDist", inp={"CamDist": "@ndc.ReturnValue"}); g.n("apo", "call_self", function="Set View Shift"); g.n("svd", "call_self", function="Save Settings")
    g.get("gpgD", "Page"); g.call("isO", K_MATH, "EqualEqual_NameName", inp={"A": "@gpgD.Page", "B": "Options"}); g.branch("bO", "@isO.ReturnValue"); g.n("rbo", "call_self", function="Rebuild Options")
    # slot conflict links: "CfAll:<slot>" / "CfReset:<slot>" (row), ConflictsFreeAll / ConflictsReset (block)
    g.call("cfs", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"})
    g.call("cfa", K_STR, "StartsWith", inp={"SourceString": "@cfs.ReturnValue", "InPrefix": "CfAll:", "SearchCase": "CaseSensitive"}); g.branch("bcfa", "@cfa.ReturnValue")
    g.call("cfa_s", K_STR, "GetSubstring", inp={"SourceString": "@cfs.ReturnValue", "StartIndex": "6", "Length": "1000"}); g.call("cfa_n", K_STR, "Conv_StringToName", inp={"InString": "@cfa_s.ReturnValue"})
    g.n("cfa_f", "call_self", function="Free Slot", inp={"slot": "@cfa_n.ReturnValue", "freed": "true"})
    g.call("cec", K_STR, "StartsWith", inp={"SourceString": "@cfs.ReturnValue", "InPrefix": "EyeColor:", "SearchCase": "CaseSensitive"}); g.branch("bcec", "@cec.ReturnValue")
    g.call("cec_s", K_STR, "GetSubstring", inp={"SourceString": "@cfs.ReturnValue", "StartIndex": "9", "Length": "1000"}); g.call("cec_n", K_STR, "Conv_StringToName", inp={"InString": "@cec_s.ReturnValue"})
    g.get("cec_c", "ContextItem"); g.n("cec_o", "call_self", function="Open Eye Color", inp={"part": "@cec_n.ReturnValue", "row": "@cec_c.ContextItem"})
    g.call("cer", K_STR, "StartsWith", inp={"SourceString": "@cfs.ReturnValue", "InPrefix": "EyeReset", "SearchCase": "CaseSensitive"}); g.branch("bcer", "@cer.ReturnValue")
    g.get("cer_c", "ContextItem"); g.n("cer_o", "call_self", function="Eye Reset Colors", inp={"row": "@cer_c.ContextItem"})
    g.call("cco", K_STR, "StartsWith", inp={"SourceString": "@cfs.ReturnValue", "InPrefix": "Color:", "SearchCase": "CaseSensitive"}); g.branch("bcco", "@cco.ReturnValue")
    g.call("cco_s", K_STR, "GetSubstring", inp={"SourceString": "@cfs.ReturnValue", "StartIndex": "6", "Length": "1000"}); g.call("cco_i", K_STR, "Conv_StringToInt", inp={"InString": "@cco_s.ReturnValue"})
    g.get("cco_c", "ContextItem"); g.n("cco_o", "call_self", function="Open Slot Color", inp={"name": "@cco_c.ContextItem", "slot": "@cco_i.ReturnValue"})
    g.call("cfr", K_STR, "StartsWith", inp={"SourceString": "@cfs.ReturnValue", "InPrefix": "CfReset:", "SearchCase": "CaseSensitive"}); g.branch("bcfr", "@cfr.ReturnValue")
    g.call("cfr_s", K_STR, "GetSubstring", inp={"SourceString": "@cfs.ReturnValue", "StartIndex": "8", "Length": "1000"}); g.call("cfr_n", K_STR, "Conv_StringToName", inp={"InString": "@cfr_s.ReturnValue"})
    g.n("cfr_f", "call_self", function="Free Slot", inp={"slot": "@cfr_n.ReturnValue", "freed": "false"})
    g.n("cff_a", "call_self", function="Free All", inp={"freed": "true"}); g.n("cff_r", "call_self", function="Free All", inp={"freed": "false"})
    g.call("qpre", K_STR, "StartsWith", inp={"SourceString": "@cfs.ReturnValue", "InPrefix": "QKey", "SearchCase": "CaseSensitive"})
    g.call("qpu", K_STR, "StartsWith", inp={"SourceString": "@cfs.ReturnValue", "InPrefix": "QUp:", "SearchCase": "CaseSensitive"}); g.call("qpd", K_STR, "StartsWith", inp={"SourceString": "@cfs.ReturnValue", "InPrefix": "QDown:", "SearchCase": "CaseSensitive"})
    g.call("qpx", K_STR, "StartsWith", inp={"SourceString": "@cfs.ReturnValue", "InPrefix": "QDel:", "SearchCase": "CaseSensitive"})
    g.call("qo1", K_MATH, "BooleanOR", inp={"A": "@qpre.ReturnValue", "B": "@qpu.ReturnValue"}); g.call("qo2", K_MATH, "BooleanOR", inp={"A": "@qpd.ReturnValue", "B": "@qpx.ReturnValue"})
    g.call("qo", K_MATH, "BooleanOR", inp={"A": "@qo1.ReturnValue", "B": "@qo2.ReturnValue"}); g.branch("bq", "@qo.ReturnValue"); g.n("qa", "call_self", function="Quick Action", inp={"name": "@entry.name"})
    g.chain("entry", "cm", "bq", "qa"); g.chain("bq:else", "bcfa", "cfa_f"); g.chain("bcfa:else", "bcec", "cec_o"); g.chain("bcec:else", "bcer", "cer_o"); g.chain("bcer:else", "bcco", "cco_o"); g.chain("bcco:else", "bcfr", "cfr_f"); g.chain("bcfr:else", "bdist", "scd", "apo", "svd", "bO", "rbo"); prev = "bdist:else"
    # multi-step actions
    g.get("gpcs", "Panel"); g.call("pcs", W_PANEL, "Clear Search", inp={"self": "@gpcs.Panel"})
    g.call("et", K_TXT, "Conv_StringToText", inp={"InString": ""}); g.n("osc", "call_self", function="On Search Changed", inp={"text": "@et.ReturnValue"})
    g.n("ftr", "call_self", function="Reset Theme"); g.n("ftr2", "call_self", function="Apply Theme"); g.n("ftr3", "call_self", function="Save Settings"); g.n("ftr4", "call_self", function="Rebuild Options")
    g.get("gpcs2", "Panel"); g.call("pcsc", W_PANEL, "Clear Chip Search", inp={"self": "@gpcs2.Panel"}); g.set("scst", "ChipSearchText", inp={"ChipSearchText": ""}); g.n("crt", "call_self", function="Rebuild SubTabs")
    g.get("gpms", "Panel"); g.call("pms", W_PANEL, "Clear Manage Search", inp={"self": "@gpms.Panel"}); g.set("smst", "ManageSearchText", inp={"ManageSearchText": ""})
    g.n("mrc", "call_self", function="Rebuild Manage Cats"); g.n("mrr", "call_self", function="Rebuild Manage")
    g.get("gplcs", "Panel"); g.call("plcs", W_PANEL, "Clear Look Chip Search", inp={"self": "@gplcs.Panel"}); g.set("slcst", "LookChipSearchText", inp={"LookChipSearchText": ""}); g.n("lcrc", "call_self", function="Rebuild Look Chips")
    g.get("gpls", "Panel"); g.call("pls", W_PANEL, "Clear Look Search", inp={"self": "@gpls.Panel"}); g.set("slst", "LookSearchText", inp={"LookSearchText": ""})
    g.n("lrc", "call_self", function="Rebuild Look Cats"); g.n("lrk", "call_self", function="Rebuild Look")
    g.get("gpps", "Panel"); g.call("pps", W_PANEL, "Clear Pose Search", inp={"self": "@gpps.Panel"}); g.set("spst", "PoseSearchText", inp={"PoseSearchText": ""}); g.n("prc", "call_self", function="Rebuild Pose Chips"); g.n("prk", "call_self", function="Rebuild Poses"); g.n("prcat", "call_self", function="Rebuild Pose Cats")
    g.get("gpws", "Panel"); g.call("pws", W_PANEL, "Clear Weapon Search", inp={"self": "@gpws.Panel"}); g.set("swst", "WeaponSearchText", inp={"WeaponSearchText": ""}); g.n("wrc", "call_self", function="Rebuild Weapon Chips"); g.n("wrk", "call_self", function="Rebuild Weapon Skins"); g.n("wrm2", "call_self", function="Rebuild Weapon Models")
    special = {"ClearSearch": ["pcs", "osc"], "ClearChipSearch": ["pcsc", "scst", "crt"], "ClearManageSearch": ["pms", "smst", "mrc", "mrr"], "ClearLookSearch": ["pls", "slst", "lrc", "lrk"], "ClearLookChipSearch": ["plcs", "slcst", "lcrc"], "ClearPoseSearch": ["pps", "spst", "prc", "prk", "prcat"], "ClearWeaponSearch": ["pws", "swst", "wrc", "wrk", "wrm2"], "ThemeReset": ["ftr", "ftr2", "ftr3", "ftr4"],
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


TOP_TABS = ["Clothes", "Outfits", "Looks", "Bag", "Hair", "Poses", "Weapons", "Look", "Body", "Face", "Mods", "Options", "Manage"]   # tab bar order; Options can not be hidden


def f_tab_shown():
    """yes = the tab bar shows `page`: not switched off (HiddenTabs), or it is the current page (a jump into a hidden tab shows it until
    the next page change). Options is always shown."""
    g = G()
    g.get("gp", "Page"); g.call("cur", K_MATH, "EqualEqual_NameName", inp={"A": "@gp.Page", "B": "@entry.page"})
    g.call("opt", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.page", "B": "Options"})
    g.get("gh", "HiddenTabs"); g.call("hid", K_ARR, "Array_Contains", inp={"TargetArray": "@gh.HiddenTabs", "ItemToFind": "@entry.page"}); g.call("vis", K_MATH, "Not_PreBool", inp={"A": "@hid.ReturnValue"})
    g.call("o1", K_MATH, "BooleanOR", inp={"A": "@cur.ReturnValue", "B": "@opt.ReturnValue"}); g.call("yes", K_MATH, "BooleanOR", inp={"A": "@o1.ReturnValue", "B": "@vis.ReturnValue"})
    g.link("yes.ReturnValue", "return.yes"); g.chain("entry", "return")
    return fn("Tab Shown", [param("page", "name")], [param("yes", "bool")], graph=g, pure=True)


def f_first_visible_page():
    """The first tab of TOP_TABS that is not switched off (Options at the latest: it can not be switched off). No SelectName in 4.27: select as string."""
    g = G(); pin = "Options"
    for i, page in reversed(list(enumerate(TOP_TABS))):
        if page == "Options": continue
        g.get("gh%d" % i, "HiddenTabs"); g.call("c%d" % i, K_ARR, "Array_Contains", inp={"TargetArray": "@gh%d.HiddenTabs" % i, "ItemToFind": g.lit_name("ln%d" % i, page)})
        g.call("s%d" % i, K_MATH, "SelectString", inp={"A": pin, "B": page, "bPickA": "@c%d.ReturnValue" % i}); pin = "@s%d.ReturnValue" % i
    g.call("tn", K_STR, "Conv_StringToName", inp={"InString": pin}); g.link("tn.ReturnValue", "return.page"); g.chain("entry", "return")
    return fn("First Visible Page", [], [param("page", "name")], graph=g, pure=True)


def f_toggle_tab_hidden():
    """Tab chip "Tab:<page>" clicked: switch the tab off / on (Options never), save; with the panel open the tab bar and the chips follow."""
    g = G()
    g.call("opt", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.page", "B": "Options"}); g.branch("bo", "@opt.ReturnValue")
    g.get("gh", "HiddenTabs"); g.call("hid", K_ARR, "Array_Contains", inp={"TargetArray": "@gh.HiddenTabs", "ItemToFind": "@entry.page"}); g.branch("bh", "@hid.ReturnValue")
    g.get("gh1", "HiddenTabs"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gh1.HiddenTabs", "Item": "@entry.page"})
    g.get("gh2", "HiddenTabs"); g.call("ad", K_ARR, "Array_AddUnique", inp={"TargetArray": "@gh2.HiddenTabs", "NewItem": "@entry.page"})
    g.n("sv", "call_self", function="Save Settings")
    g.get("gpo", "PanelOpen"); g.branch("bp", "@gpo.PanelOpen"); g.n("rtt", "call_self", function="Rebuild TopTabs"); g.n("ro", "call_self", function="Rebuild Options")
    g.chain("entry", "bo"); g.chain("bo:else", "bh", "rm", "sv"); g.chain("bh:else", "ad", "sv"); g.chain("sv", "bp", "rtt", "ro")
    return fn("Toggle Tab Hidden", [param("page", "name")], graph=g)


def f_rebuild_top_tabs():
    """Tab bar: every tab of TOP_TABS the bar shows (Tab Shown: not switched off, or the current page). Mods only when another mod
    registered something - the entry scan runs only when the Mods tab is shown at all."""
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear TopTabs", inp={"self": "@gp.Panel"})
    g.chain("entry", "cl"); exits = ["cl"]   # exec outputs that continue with the next tab
    for i, page in enumerate(TOP_TABS):
        tw = create_widget(g, "ct%d" % i, W_TOP); set_manager(g, "sm%d" % i, W_TOP, tw)
        g.get("gpo%d" % i, "Page"); g.call("eq%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@gpo%d.Page" % i, "B": page}); sel = "@eq%d.ReturnValue" % i
        g.get("gts%d" % i, "TabStyle"); g.get("gtr%d" % i, "TabIconRight")
        g.call("ti%d" % i, W_TOP, "Init", inp={"self": tw, "page": page, "caption": tt(g, "tt%d" % i, "Tab_" + page), "selected": sel, "icon": TAB_ICONS[page],
                                               "style": "@gts%d.TabStyle" % i, "right": "@gtr%d.TabIconRight" % i})
        g.get("gp%d" % i, "Panel"); g.call("at%d" % i, W_PANEL, "Add TopTab", inp={"self": "@gp%d.Panel" % i, "widget": tw})
        make = ["ct%d_cr" % i, "sm%d" % i, "ti%d" % i, "at%d" % i]
        if page == "Options":   # never switched off
            start, nxt = make[0], ["at%d" % i]
        else:
            g.n("sh%d" % i, "call_self", function="Tab Shown", inp={"page": page}); g.branch("bs%d" % i, "@sh%d.yes" % i)
            start, nxt = "bs%d" % i, ["at%d" % i, "bs%d:else" % i]
            if page == "Mods":   # only when another mod registered something
                g.n("msc", "call_self", function="Scan Mod Entries"); g.get("gmk", "ModEntryKeys")
                g.call("mln", K_ARR, "Array_Length", inp={"TargetArray": "@gmk.ModEntryKeys"}); g.call("many", K_MATH, "Greater_IntInt", inp={"A": "@mln.ReturnValue", "B": "0"}); g.branch("bmods", "@many.ReturnValue")
                g.chain("bs%d" % i, "msc", "bmods", *make); nxt.append("bmods:else")
            else:
                g.chain("bs%d" % i, *make)
        if page == "Options": g.chain(*make)
        for e in exits: g.chain(e, start)
        exits = nxt
    return fn("Rebuild TopTabs", graph=g)


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
MANAGE_CATS = [("Vanilla", "Cat_Vanilla"), ("Mods", "Cat_Mods"), ("Poses", "Tab_Poses"), ("Clothes", "Cat_Clothes"), ("Look", "Tab_Look")]   # clickable categories first, then the two sections with indented sub items   # Vanilla / Mods clickable; Clothes / Look are sections (Look = hairstyles + skins + make-up)
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


def add_key(g, id, kind, row_pin, after, grouped=False):
    """TmpStrings += "<kind>:<row>"; returns the exec ids. grouped: only when the row is in the chosen chip (Manage Row In Group)."""
    g.call(id + "_s", K_STR, "Conv_NameToString", inp={"InName": row_pin}); g.call(id + "_c", K_STR, "Concat_StrStr", inp={"A": kind + ":", "B": "@%s_s.ReturnValue" % id})
    g.get(id + "_g", "TmpStrings"); g.call(id + "_a", K_ARR, "Array_Add", inp={"TargetArray": "@%s_g.TmpStrings" % id, "NewItem": "@%s_c.ReturnValue" % id})
    if grouped:
        g.n(id + "_mg", "call_self", function="Manage Row In Group", inp={"kind": kind, "row": row_pin}); g.branch(id + "_gb", "@%s_mg.yes" % id)
        g.chain(after, id + "_mg", id + "_gb", id + "_a"); return id + "_a"
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
    for cat in ("Mods", "Vanilla", "Clothes", "Look", "Poses"):
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
    g.get("gmm", "TmpBool"); g.call("show0", K_MATH, "BooleanOR", inp={"A": "@gmm.TmpBool", "B": "@n3g.ReturnValue"})
    g.n("mig", "call_self", function="Manage Row In Group", inp={"kind": "mod", "row": "@fm.Array Element"})   # the chosen Manage chip: this mod (with its groups) or nothing
    g.call("show", K_MATH, "BooleanAND", inp={"A": "@show0.ReturnValue", "B": "@mig.yes"}); g.branch("bshow", "@show.ReturnValue")
    last = add_key(g, "km", "mod", "@fm.Array Element", "bshow")
    g.get("gn3d", "TmpNames3"); g.foreach("fg", "@gn3d.TmpNames3"); g.chain(last, "fg"); add_key(g, "kg", "group", "@fg.Array Element", "fg")
    g.chain("bMods", "fm"); g.chain("fm", "smm", "n3c", "fp"); g.chain("fp", "bsw", "gcd", "bgm", "n3a"); g.chain("fp:Completed", "mig", "bshow"); g.chain("fm:Completed", "return")
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
    add_key(g, "ki", "item", "@bi.Name", "biok", grouped=True)
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
        add_key(g, id + "_k", kind, "@%s_fe.Array Element" % id, id + "_b", grouped=True)
        g.chain(prev, id + "_rn", id + "_fe"); g.chain(id + "_fe", *([id + "_row"] if typed else []), id + "_b"); return id + "_fe:Completed"
    # Look: hairstyles when the sub item is All / Hair, skins when All / Skin, then makeup + eye rows filtered by their Type
    g.get("gls", "ManageSub"); g.call("lsn", K_MATH, "EqualEqual_NameName", inp={"A": "@gls.ManageSub", "B": "None"})
    g.call("lsh", K_MATH, "EqualEqual_NameName", inp={"A": "@gls.ManageSub", "B": "Hair"}); g.call("lsho", K_MATH, "BooleanOR", inp={"A": "@lsn.ReturnValue", "B": "@lsh.ReturnValue"}); g.branch("bLookHair", "@lsho.ReturnValue"); g.chain("bLook", "bLookHair")
    hair_done = table_rows("h", P_HAIR_T, "hair", "bLookHair")
    g.call("lsk", K_MATH, "EqualEqual_NameName", inp={"A": "@gls.ManageSub", "B": "Skin"}); g.call("lso", K_MATH, "BooleanOR", inp={"A": "@lsn.ReturnValue", "B": "@lsk.ReturnValue"}); g.branch("bLookSkin", "@lso.ReturnValue")
    g.chain(hair_done, "bLookSkin"); g.chain("bLookHair:else", "bLookSkin")
    skin_done = table_rows("s", P_SKIN_T, "skin", "bLookSkin"); g.chain("bLookSkin:else", "m_rn")
    g.chain(table_rows("e", P_EYE_T, "makeup", table_rows("m", P_MAKEUP_T, "makeup", skin_done, typed=P_MAKEUP_S), typed=P_EYE_S), "return")
    g.chain("bLook:else", "bPoses")
    # --- Poses: the AnimationTable rows the poses tab lists, matched against their title
    g.n("pcol", "call_self", function="Collect Pose Rows")
    g.get("gpr", "PoseRows"); g.foreach("fpp", "@gpr.PoseRows")
    g.n("pimd", "call_self", function="Item Mod", inp={"row": "@fpp.Array Element"}); g.get("pgom", "TmpFound"); g.call("pnom", K_MATH, "Not_PreBool", inp={"A": "@pgom.TmpFound"})
    g.call("pkeep", K_MATH, "BooleanOR", inp={"A": "@pnom.ReturnValue", "B": "@pimd.found"})
    g.n("ptl", "call_self", function="Pose Title", inp={"row": "@fpp.Array Element"}); g.get("pgs", "TmpStr3")
    g.n("pm", "call_self", function="Name Matches", inp={"kind": "pose", "row": "@fpp.Array Element", "default": "@ptl.title", "search": "@pgs.TmpStr3"})
    g.call("pok", K_MATH, "BooleanAND", inp={"A": "@pkeep.ReturnValue", "B": "@pm.yes"}); g.branch("pb", "@pok.ReturnValue")
    add_key(g, "pk", "pose", "@fpp.Array Element", "pb", grouped=True)
    g.chain("bPoses", "pcol", "fpp"); g.chain("fpp", "ptl", "pb"); g.chain("fpp:Completed", "return"); g.chain("bPoses:else", "return")
    return fn("Manage Rows", [param("cat", "name"), param("search", "string"), param("onlyMods", "bool")], [param("keys", "string", "array")], graph=g)


def f_manage_count():
    """Rows of a category for a search text, regardless of the sub item (ManageSub parked in TmpSubSave meanwhile); chip = the chosen
    Manage chip applies too (the hits), else not (the total - the number in front of the brackets)."""
    g = G(); g.get("gom", "OnlyModsNames")
    g.get("gsb", "ManageSub"); g.set("sv", "TmpSubSave", inp={"TmpSubSave": "@gsb.ManageSub"}); g.set("sn", "ManageSub", inp={"ManageSub": "None"})
    g.call("nc", K_MATH, "Not_PreBool", inp={"A": "@entry.chip"}); g.set("ng1", "ManageNoGroup", inp={"ManageNoGroup": "@nc.ReturnValue"})
    g.n("mr", "call_self", function="Manage Rows", inp={"cat": "@entry.cat", "search": "@entry.search", "onlyMods": "@gom.OnlyModsNames"})
    g.set("ng0", "ManageNoGroup", inp={"ManageNoGroup": "false"})
    g.get("gsv", "TmpSubSave"); g.set("sr", "ManageSub", inp={"ManageSub": "@gsv.TmpSubSave"})
    g.call("ln", K_ARR, "Array_Length", inp={"TargetArray": "@mr.keys"}); g.set("sn2", "ManageCountTmp", inp={"ManageCountTmp": "@ln.ReturnValue"})
    g.get("gcn", "ManageCountTmp"); g.link("gcn.ManageCountTmp", "return.n"); g.chain("entry", "sv", "sn", "ng1", "mr", "sn2", "ng0", "sr", "return")
    return fn("Manage Count", [param("cat", "name"), param("search", "string"), param("chip", "bool")], [param("n", "int")], graph=g)


def f_manage_sub_counts():
    """Rows of a category per sub item (Clothes: slot via ItemSlot; Look: Skin, else the makeup / eye row's Type) for a search text, ignoring the
    selected sub item -> ManageSubCounts (filtered = false: totals, search "") or ManageSubFiltered (filtered = true: the current search)."""
    g = G(); g.get("gm", "ManageSubCounts"); g.call("mc", K_MAP, "Map_Clear", inp={"TargetMap": "@gm.ManageSubCounts"})
    g.get("gmf", "ManageSubFiltered"); g.call("mcf", K_MAP, "Map_Clear", inp={"TargetMap": "@gmf.ManageSubFiltered"}); g.branch("bwhich", "@entry.filtered")
    g.get("gom", "OnlyModsNames")
    g.get("gsb", "ManageSub"); g.set("sv", "TmpSubSave", inp={"TmpSubSave": "@gsb.ManageSub"}); g.set("sn", "ManageSub", inp={"ManageSub": "None"})
    g.n("mr", "call_self", function="Manage Rows", inp={"cat": "@entry.cat", "search": "@entry.search", "onlyMods": "@gom.OnlyModsNames"})
    g.get("gsv", "TmpSubSave"); g.set("sr", "ManageSub", inp={"ManageSub": "@gsv.TmpSubSave"})
    # totals without the chosen Manage chip, the hits with it (like Manage Count)
    g.call("snc", K_MATH, "Not_PreBool", inp={"A": "@entry.filtered"}); g.set("sng1", "ManageNoGroup", inp={"ManageNoGroup": "@snc.ReturnValue"}); g.set("sng0", "ManageNoGroup", inp={"ManageNoGroup": "false"})
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
    g.chain("entry", "bwhich", "mcf", "sv"); g.chain("bwhich:else", "mc", "sv"); g.chain("sv", "sn", "sng1", "mr", "sng0", "sr", "sk", "fe")
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
    g.get("gst", "ManageSearchText"); g.call("sne", K_STR, "IsEmpty", inp={"InString": "@gst.ManageSearchText"}); g.call("sact0", K_MATH, "Not_PreBool", inp={"A": "@sne.ReturnValue"}); g.get("gmgc", "ManageGroup"); g.call("chipon", K_MATH, "NotEqual_NameName", inp={"A": "@gmgc.ManageGroup", "B": "None"})
    g.call("sact", K_MATH, "BooleanOR", inp={"A": "@sact0.ReturnValue", "B": "@chipon.ReturnValue"}); g.set("ssa", "ManageSearchActive", inp={"ManageSearchActive": "@sact.ReturnValue"})
    g.chain("entry", "cl", "som", "ssa"); sources = ["ssa"]
    for i, (cat, key) in enumerate(MANAGE_CATS):
        c = cat.lower()
        g.n("cnt%d" % i, "call_self", function="Manage Count", inp={"cat": cat, "search": "", "chip": "false"})
        g.get("gst%d" % i, "ManageSearchText"); g.n("cntf%d" % i, "call_self", function="Manage Count", inp={"cat": cat, "search": "@gst%d.ManageSearchText" % i, "chip": "true"})
        g.get("gsa%d" % i, "ManageSearchActive"); g.call("fsel%d" % i, K_MATH, "SelectInt", inp={"A": "@cntf%d.n" % i, "B": "-1", "bPickA": "@gsa%d.ManageSearchActive" % i})   # -1 = no filter -> no parentheses
        g.get("gmc%d" % i, "ManageCat"); g.call("sel%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": cat, "B": "@gmc%d.ManageCat" % i})
        for src in sources: g.chain(src, "cnt%d" % i)
        if cat not in MANAGE_SUBS:
            tw = create_widget(g, "ct%d" % i, W_TAB); set_manager(g, "sm%d" % i, W_TAB, tw)
            g.call("ti%d" % i, W_TAB, "Init", inp={"self": tw, "slot": cat, "caption": tt(g, "pcc%d" % i, key), "count": "@cnt%d.n" % i, "selected": "@sel%d.ReturnValue" % i, "has items": "true", "filtered": "@fsel%d.ReturnValue" % i})
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
        g.call("ai" + c, W_TAB, "Init", inp={"self": aw, "slot": g.lit_name("aln" + c, "Sub:%s:All" % cat), "caption": tt(g, "at" + c, "Chip_All"), "count": "@cnt%d.n" % i, "selected": "@asel%s.ReturnValue" % c, "has items": "true", "filtered": "@fsel%d.ReturnValue" % i, "indent": "false"})
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
        g.call("si" + c, W_TAB, "Init", inp={"self": sw, "slot": "@kn%s.ReturnValue" % c, "caption": cap, "count": "@cf%s.Value" % c, "selected": "@ssel%s.ReturnValue" % c, "has items": "true", "filtered": "@fsub%s.ReturnValue" % c, "indent": "false"})
        g.get("gps" + c, "Panel"); g.call("sa2" + c, W_PANEL, "Add Manage Cat", inp={"self": "@gps%s.Panel" % c, "widget": sw})
        g.chain("cnt%d" % i, "cntf%d" % i, "ch%s_cr" % c, "shm" + c, "hi" + c, "ah" + c, "msc" + c, "mscf" + c, "ca%s_cr" % c, "sa" + c, "ai" + c, "aa" + c, *keys_prep, "fe" + c)
        g.chain("fe" + c, "bn" + c, "cs%s_cr" % c, "ss" + c, *cap_nodes, "si" + c, "sa2" + c)
        sources = ["fe%s:Completed" % c]
    return fn("Rebuild Manage Cats", graph=g)


MANAGE_CHIP_CATS = ("Clothes", "Look", "Poses", "Mods")   # Manage categories with a chip row: clothes groups / appearance, pose mods like their tabs; Mods: the mods


def f_manage_row_group():
    """Chip of a Manage row: a piece -> its group as the clothes tab shows it (Group Alias; no group = Basis); hair / skin / make-up /
    pose -> its mod (Mod Alias), the game's own rows -> Vanilla; a mod header (Mods) -> the mod, its group rows -> None (they go with it)."""
    g = G(); g.set("s0", "ManageGroupTmp", inp={"ManageGroupTmp": "Vanilla"})
    g.call("isi", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "item"}); g.branch("bi", "@isi.ReturnValue")
    # Mods category: a header row is its mod's chip; its group rows go with it (None: never a chip of their own)
    g.call("ism", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "mod"}); g.branch("bmo", "@ism.ReturnValue")
    g.n("mam", "call_self", function="Mod Alias", inp={"mod": "@entry.row"}); g.set("s3", "ManageGroupTmp", inp={"ManageGroupTmp": "@mam.alias"})
    g.call("isg", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "group"}); g.branch("bgr", "@isg.ReturnValue"); g.set("s4", "ManageGroupTmp", inp={"ManageGroupTmp": "None"})
    g.n("fi", "call_self", function="Find Item", inp={"name": "@entry.row"}); g.brk("bfi", S_ITEM, "@fi.item")
    g.call("gn", K_MATH, "EqualEqual_NameName", inp={"A": "@bfi.Group", "B": "None"}); g.call("gs", K_STR, "Conv_NameToString", inp={"InName": "@bfi.Group"})
    g.call("gsel", K_MATH, "SelectString", inp={"A": "Basis", "B": "@gs.ReturnValue", "bPickA": "@gn.ReturnValue"}); g.call("gnm", K_STR, "Conv_StringToName", inp={"InString": "@gsel.ReturnValue"})
    g.n("ga", "call_self", function="Group Alias", inp={"group": "@gnm.ReturnValue"}); g.set("s1", "ManageGroupTmp", inp={"ManageGroupTmp": "@ga.alias"})
    g.n("im", "call_self", function="Item Mod", inp={"row": "@entry.row"}); g.branch("bm", "@im.found")
    g.n("ma", "call_self", function="Mod Alias", inp={"mod": "@im.mod"}); g.set("s2", "ManageGroupTmp", inp={"ManageGroupTmp": "@ma.alias"})
    g.get("gr", "ManageGroupTmp"); g.link("gr.ManageGroupTmp", "return.group")
    g.chain("entry", "s0", "bi", "fi", "s1", "return"); g.chain("bi:else", "bmo", "s3", "return"); g.chain("bmo:else", "bgr", "s4", "return"); g.chain("bgr:else", "bm", "s2", "return"); g.chain("bm:else", "return")   # Group Alias, Item Mod, Mod Alias are pure
    return fn("Manage Row Group", [param("kind", "name"), param("row", "name")], [param("group", "name")], graph=g)


def f_manage_row_in_group():
    """yes = no chip chosen (ManageGroup None), the chips are being collected (ManageNoGroup), or the row's chip is the chosen one."""
    g = G(); g.get("gmg", "ManageGroup"); g.call("none", K_MATH, "EqualEqual_NameName", inp={"A": "@gmg.ManageGroup", "B": "None"})
    g.get("gng", "ManageNoGroup"); g.call("free", K_MATH, "BooleanOR", inp={"A": "@none.ReturnValue", "B": "@gng.ManageNoGroup"}); g.branch("bf", "@free.ReturnValue")
    g.set("sy", "ManageInGroup", inp={"ManageInGroup": "true"})
    g.n("rg", "call_self", function="Manage Row Group", inp={"kind": "@entry.kind", "row": "@entry.row"}); g.get("gmg2", "ManageGroup")
    g.call("eq", K_MATH, "EqualEqual_NameName", inp={"A": "@rg.group", "B": "@gmg2.ManageGroup"}); g.set("se", "ManageInGroup", inp={"ManageInGroup": "@eq.ReturnValue"})
    g.get("gr", "ManageInGroup"); g.link("gr.ManageInGroup", "return.yes")
    g.chain("entry", "bf", "sy", "return"); g.chain("bf:else", "rg", "se", "return")
    return fn("Manage Row In Group", [param("kind", "name"), param("row", "name")], [param("yes", "bool")], graph=g)


def f_manage_groups():
    """The chips of the current Manage category / sub item: the groups (clothes) or mods (appearance, poses) of its rows, search ignored."""
    g = G(); g.set("on", "ManageNoGroup", inp={"ManageNoGroup": "true"})
    g.get("gmc", "ManageCat"); g.get("gom", "OnlyModsNames"); g.n("mr", "call_self", function="Manage Rows", inp={"cat": "@gmc.ManageCat", "search": "", "onlyMods": "@gom.OnlyModsNames"})
    g.set("sk", "ManageGroupKeys", inp={"ManageGroupKeys": "@mr.keys"}); g.set("off", "ManageNoGroup", inp={"ManageNoGroup": "false"})
    g.get("gl", "ManageGroupList"); g.call("cl", K_ARR, "Array_Clear", inp={"TargetArray": "@gl.ManageGroupList"})
    g.get("gk", "ManageGroupKeys"); g.foreach("fe", "@gk.ManageGroupKeys")
    g.call("sp", K_STR, "Split", inp={"SourceString": "@fe.Array Element", "InStr": ":", "SearchCase": "CaseSensitive", "SearchDir": "FromStart"})
    g.call("kn", K_STR, "Conv_StringToName", inp={"InString": "@sp.LeftS"}); g.call("rn", K_STR, "Conv_StringToName", inp={"InString": "@sp.RightS"})
    g.n("rg", "call_self", function="Manage Row Group", inp={"kind": "@kn.ReturnValue", "row": "@rn.ReturnValue"})
    g.call("gnn", K_MATH, "NotEqual_NameName", inp={"A": "@rg.group", "B": "None"}); g.branch("bgn", "@gnn.ReturnValue")   # group rows under a mod header
    g.get("gl2", "ManageGroupList"); g.call("add", K_ARR, "Array_AddUnique", inp={"TargetArray": "@gl2.ManageGroupList", "NewItem": "@rg.group"})
    g.get("gl3", "ManageGroupList"); g.link("gl3.ManageGroupList", "return.groups")
    g.chain("entry", "on", "mr", "sk", "off", "cl", "fe"); g.chain("fe", "rg", "bgn", "add"); g.chain("fe:Completed", "return")
    return fn("Manage Groups", [], [param("groups", "name", "array")], graph=g)


def f_rebuild_manage_chips():
    """Chip row of the Manage page (Clothes / Appearance / Poses): All + one chip per group / mod in alphabetical order (Sort Chips),
    filtered by the chip search; hidden with fewer than two chips and in the other categories. A chosen chip that is gone -> All."""
    g = G(); g.get("gp0", "Panel"); g.call("pv", K_SYS, "IsValid", inp={"Object": "@gp0.Panel"}); g.branch("bpv", "@pv.ReturnValue")
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Manage Chips", inp={"self": "@gp.Panel"})
    g.get("gmc", "ManageCat"); ors = []
    for i, c in enumerate(MANAGE_CHIP_CATS): g.call("ic%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@gmc.ManageCat", "B": c})
    g.call("o1", K_MATH, "BooleanOR", inp={"A": "@ic0.ReturnValue", "B": "@ic1.ReturnValue"}); g.call("o2", K_MATH, "BooleanOR", inp={"A": "@o1.ReturnValue", "B": "@ic2.ReturnValue"})
    g.call("chipcat", K_MATH, "BooleanOR", inp={"A": "@o2.ReturnValue", "B": "@ic3.ReturnValue"})
    g.branch("bcat", "@chipcat.ReturnValue")
    # not a chip category: hide, back to All
    g.set("sn0", "ManageGroup", inp={"ManageGroup": "None"}); g.get("gph", "Panel"); g.call("hide", W_PANEL, "Set Manage Chips Visible", inp={"self": "@gph.Panel", "chips": "false", "search": "false"})
    g.n("mg", "call_self", function="Manage Groups")
    g.call("nl", K_MATH, "Not_PreBool", inp={"A": "@ic0.ReturnValue"})   # appearance / poses: mod chips
    g.n("srt", "call_self", function="Sort Chips", inp={"groups": "@mg.groups", "look": "@nl.ReturnValue"}); g.set("so", "ManageChipOrder", inp={"ManageChipOrder": "@srt.sorted"})
    g.get("gmg", "ManageGroup"); g.get("go0", "ManageChipOrder"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@go0.ManageChipOrder", "ItemToFind": "@gmg.ManageGroup"})
    g.call("hn", K_MATH, "Not_PreBool", inp={"A": "@has.ReturnValue"}); g.branch("bgone", "@hn.ReturnValue"); g.set("sn1", "ManageGroup", inp={"ManageGroup": "None"})
    g.get("go1", "ManageChipOrder"); g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@go1.ManageChipOrder"}); g.call("many", K_MATH, "Greater_IntInt", inp={"A": "@len.ReturnValue", "B": "1"})
    g.get("gcsh", "ChipSearchShown"); g.call("srch", K_MATH, "BooleanAND", inp={"A": "@many.ReturnValue", "B": "@gcsh.ChipSearchShown"})
    g.get("gpv", "Panel"); g.call("vis", W_PANEL, "Set Manage Chips Visible", inp={"self": "@gpv.Panel", "chips": "@many.ReturnValue", "search": "@srch.ReturnValue"}); g.branch("bmany", "@many.ReturnValue")
    # the x of the chip search
    g.get("gpx", "Panel"); g.call("clx", W_PANEL, "Clear Manage Chip Search Links", inp={"self": "@gpx.Panel"})
    xw = create_widget(g, "cx", W_TXT); set_manager(g, "smx", W_TXT, xw)
    g.call("xt", K_TXT, "Conv_StringToText", inp={"InString": "\u00d7"}); g.call("xi", W_TXT, "Init", inp={"self": xw, "action": "ClearManageChipSearch", "caption": "@xt.ReturnValue"})
    g.get("gpx2", "Panel"); g.call("ax", W_PANEL, "Add Manage Chip Search Link", inp={"self": "@gpx2.Panel", "widget": xw})
    # All
    aw = create_widget(g, "ca", W_SUB); set_manager(g, "sma", W_SUB, aw)
    g.get("gmga", "ManageGroup"); g.call("selA", K_MATH, "EqualEqual_NameName", inp={"A": "@gmga.ManageGroup", "B": "None"})
    g.call("ia", W_SUB, "Init", inp={"self": aw, "group": "MG:", "caption": tt(g, "ta", "Chip_All"), "selected": "@selA.ReturnValue"})
    g.get("gpa", "Panel"); g.call("aa", W_PANEL, "Add Manage Chip", inp={"self": "@gpa.Panel", "widget": aw})
    # "..." right of All: collapses / expands the chips (highlighted while collapsed), like the other chip rows
    mw = create_widget(g, "cm", W_SUB); set_manager(g, "smm", W_SUB, mw); g.get("gcol", "ManageChipsCollapsed")
    g.call("im", W_SUB, "Init", inp={"self": mw, "group": "MG:AltUI_More", "caption": tt(g, "tm", "Chip_More"), "selected": "@gcol.ManageChipsCollapsed"})
    g.get("gpm", "Panel"); g.call("am", W_PANEL, "Add Manage Chip", inp={"self": "@gpm.Panel", "widget": mw})
    # one chip per group / mod; the chip search keeps the chosen one and the hits (by the shown name)
    g.get("go2", "ManageChipOrder"); g.foreach("fe", "@go2.ManageChipOrder")
    g.branch("bk", "@ic0.ReturnValue")
    g.n("ccc", "call_self", function="Chip Caption", inp={"group": "@fe.Array Element", "full": "false"}); g.set("scc", "ManageChipCap", inp={"ManageChipCap": "@ccc.caption"})
    g.n("lcc", "call_self", function="Look Chip Caption", inp={"group": "@fe.Array Element", "full": "false"}); g.set("slc", "ManageChipCap", inp={"ManageChipCap": "@lcc.caption"})
    g.get("gcap", "ManageChipCap"); g.call("cs", K_TXT, "Conv_TextToString", inp={"InText": "@gcap.ManageChipCap"})
    g.get("gst", "ManageChipSearchText"); g.call("se", K_STR, "IsEmpty", inp={"InString": "@gst.ManageChipSearchText"})
    g.call("csl", K_STR, "ToLower", inp={"SourceString": "@cs.ReturnValue"}); g.call("stl", K_STR, "ToLower", inp={"SourceString": "@gst.ManageChipSearchText"})
    g.call("hit", K_STR, "Contains", inp={"SearchIn": "@csl.ReturnValue", "Substring": "@stl.ReturnValue", "bUseCase": "false", "bSearchFromEnd": "false"})
    g.get("gmgs", "ManageGroup"); g.call("sel", K_MATH, "EqualEqual_NameName", inp={"A": "@gmgs.ManageGroup", "B": "@fe.Array Element"})
    g.call("sh0", K_MATH, "BooleanOR", inp={"A": "@se.ReturnValue", "B": "@hit.ReturnValue"}); g.call("sh1", K_MATH, "BooleanOR", inp={"A": "@sh0.ReturnValue", "B": "@sel.ReturnValue"})
    g.get("gcol2", "ManageChipsCollapsed")
    g.call("ncl", K_MATH, "Not_PreBool", inp={"A": "@gcol2.ManageChipsCollapsed"}); g.call("open", K_MATH, "BooleanAND", inp={"A": "@sh1.ReturnValue", "B": "@ncl.ReturnValue"})
    g.call("keep", K_MATH, "BooleanAND", inp={"A": "@gcol2.ManageChipsCollapsed", "B": "@sel.ReturnValue"}); g.call("showf", K_MATH, "BooleanOR", inp={"A": "@open.ReturnValue", "B": "@keep.ReturnValue"})
    g.branch("bsh", "@showf.ReturnValue")   # collapsed: only the chosen chip
    cw = create_widget(g, "cc", W_SUB); set_manager(g, "smc", W_SUB, cw)
    g.call("gs", K_STR, "Conv_NameToString", inp={"InName": "@fe.Array Element"}); g.call("gk", K_STR, "Concat_StrStr", inp={"A": "MG:", "B": "@gs.ReturnValue"}); g.call("gkn", K_STR, "Conv_StringToName", inp={"InString": "@gk.ReturnValue"})
    g.get("gcap2", "ManageChipCap"); g.call("ic", W_SUB, "Init", inp={"self": cw, "group": "@gkn.ReturnValue", "caption": "@gcap2.ManageChipCap", "selected": "@sel.ReturnValue"})
    g.get("gpc", "Panel"); g.call("ac", W_PANEL, "Add Manage Chip", inp={"self": "@gpc.Panel", "widget": cw})
    g.chain("entry", "bpv", "cl", "bcat", "mg", "srt", "so", "bgone", "sn1", "vis"); g.chain("bgone:else", "vis"); g.chain("bcat:else", "sn0", "hide")
    g.chain("vis", "bmany", "clx", "cx_cr", "smx", "xi", "ax", "ca_cr", "sma", "ia", "aa", "cm_cr", "smm", "im", "am", "fe")
    g.chain("fe", "bk", "ccc", "scc", "bsh"); g.chain("bk:else", "lcc", "slc", "bsh"); g.chain("bsh", "cc_cr", "smc", "ic", "ac")
    return fn("Rebuild Manage Chips", graph=g)


def f_select_manage_group():
    """Manage chip "MG:<group>" ("MG:" = All): rows and the category counts follow."""
    g = G(); g.call("ns", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"}); g.call("sub", K_STR, "GetSubstring", inp={"SourceString": "@ns.ReturnValue", "StartIndex": "3", "Length": "1000"})
    g.call("emp", K_STR, "IsEmpty", inp={"InString": "@sub.ReturnValue"}); g.call("sel", K_MATH, "SelectString", inp={"A": "None", "B": "@sub.ReturnValue", "bPickA": "@emp.ReturnValue"})
    g.call("nm", K_STR, "Conv_StringToName", inp={"InString": "@sel.ReturnValue"}); g.set("s", "ManageGroup", inp={"ManageGroup": "@nm.ReturnValue"})
    g.n("rch", "call_self", function="Rebuild Manage Chips"); g.n("rc", "call_self", function="Rebuild Manage Cats"); g.n("rm", "call_self", function="Rebuild Manage")
    g.call("ism", K_STR, "EqualEqual_StrStr", inp={"A": "@sub.ReturnValue", "B": "AltUI_More"}); g.branch("bm", "@ism.ReturnValue")
    g.get("gcol", "ManageChipsCollapsed"); g.call("ncol", K_MATH, "Not_PreBool", inp={"A": "@gcol.ManageChipsCollapsed"}); g.set("scol", "ManageChipsCollapsed", inp={"ManageChipsCollapsed": "@ncol.ReturnValue"})
    g.n("svm", "call_self", function="Save Settings"); g.n("rch2", "call_self", function="Rebuild Manage Chips")
    g.chain("entry", "bm", "scol", "svm", "rch2"); g.chain("bm:else", "s", "rch", "rc", "rm"); return fn("Select Manage Group", [param("name", "name")], graph=g)


def f_on_manage_chip_search_changed():
    g = G(); g.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@entry.text"})
    g.get("gst", "ManageChipSearchText"); g.call("neq", K_STR, "NotEqual_StrStr", inp={"A": "@t2s.ReturnValue", "B": "@gst.ManageChipSearchText"}); g.branch("b", "@neq.ReturnValue")
    g.set("s", "ManageChipSearchText", inp={"ManageChipSearchText": "@t2s.ReturnValue"}); g.n("rc", "call_self", function="Rebuild Manage Chips")
    g.chain("entry", "b", "s", "rc"); return fn("On Manage Chip Search Changed", [param("text", "text")], graph=g)


def f_clear_manage_chip_search():
    g = G(); g.get("gp", "Panel"); g.call("c", W_PANEL, "Clear Manage Chip Search", inp={"self": "@gp.Panel"}); g.set("s", "ManageChipSearchText", inp={"ManageChipSearchText": ""})
    g.n("rc", "call_self", function="Rebuild Manage Chips"); g.chain("entry", "c", "s", "rc"); return fn("Clear Manage Chip Search Text", graph=g)


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
    g.n("rch", "call_self", function="Rebuild Manage Chips"); g.set("sg0", "ManageGroup", inp={"ManageGroup": "None"})
    g.chain("entry", "bsub", "sc", "ss", "rch", "rc", "rm"); g.chain("bsub:else", "s", "s0", "sg0", "rch"); return fn("Select Manage Cat", [param("name", "name")], graph=g)


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
    g.call("isp", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "pose"}); g.branch("bp", "@isp.ReturnValue")
    g.n("ptl", "call_self", function="Pose Title", inp={"row": "@entry.row"}); g.set("s3p", "TmpStr3", inp={"TmpStr3": "@ptl.title"})
    g.set("s4", "TmpStr3", inp={"TmpStr3": "@rs.ReturnValue"})
    g.get("gt", "TmpStr3"); g.link("gt.TmpStr3", "return.s")
    g.chain("entry", "bm", "s1", "return"); g.chain("bm:else", "bg", "gcd", "s2", "return"); g.chain("bg:else", "bi", "s3", "return"); g.chain("bi:else", "bp", "ptl", "s3p", "return"); g.chain("bp:else", "s4", "return")
    return fn("Manage Default", [param("kind", "name"), param("row", "name")], [param("s", "string")], graph=g)


def f_manage_origin():
    """Identifier column of a Manage row. origin: mod -> "pak: <mod>"; group -> "g: <group>[\n\nalso affects:\nPAK: <other mod display name>…]";
    item / hair / skin / makeup -> "id: <row>" (vanilla: + "\nVanilla"). mod: the piece's mod (None for mod / group rows and vanilla) - the row shows it
    as the "pak: <mod>" link. rest: item -> "g: <group>" (or empty), makeup -> the type caption, else empty."""
    g = G()
    g.call("rs", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"})
    for k, key in (("ti", "Tip_Id"), ("tp", "Tip_Pak"), ("tg", "Tip_Grp"), ("tv", "Lbl_Vanilla"), ("ta", "Lbl_AlsoAffects")):
        g.n(k, "call_self", function="T", inp={"key": key}); g.call(k + "s", K_TXT, "Conv_TextToString", inp={"InText": "@%s.text" % k})
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@entry.row"}); g.call("ms", K_STR, "Conv_NameToString", inp={"InName": "@imd.mod"})
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
    g.get("gs3a", "TmpStr3"); g.call("h1", K_STR, "Concat_StrStr", inp={"A": "@gs3a.TmpStr3", "B": "\n\n"}); g.call("h2", K_STR, "Concat_StrStr", inp={"A": "@h1.ReturnValue", "B": "@tas.ReturnValue"})   # an empty line between the group and the list of other paks
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
    # only the Mods category has pak headers with group rows below them: indent and the space of "view content" (so the G: rows line up
    # with the PAK: rows) there; elsewhere the identifier column takes that width (Vanilla groups have no header above them)
    g.get("gmcr", "ManageCat"); g.call("icm", K_MATH, "EqualEqual_NameName", inp={"A": "@gmcr.ManageCat", "B": "Mods"})
    g.call("ind", K_MATH, "BooleanAND", inp={"A": "@isg.ReturnValue", "B": "@icm.ReturnValue"})
    g.call("ini", W_NAMEROW, "Init", inp={"self": rw, "kind": "@gkn.TmpName", "row": "@grn.TmpName2", "default": "@gdf.TmpStr2", "custom": "@cn.name", "origin": "@gor.TmpText", "icon": "@gic.TmpTex", "indent": "@ind.ReturnValue", "content": "@ism.ReturnValue", "gap": "@gap.ReturnValue", "mod": "@gmd.TmpMod", "rest": "@grs.TmpRest2",
                                                 "content space": "@icm.ReturnValue"})
    g.get("gp2", "Panel"); g.call("ad", W_PANEL, "Add Manage Row", inp={"self": "@gp2.Panel", "widget": rw})
    g.get("gwl2", "ManageRowWidgets"); g.call("wla", K_ARR, "Array_Add", inp={"TargetArray": "@gwl2.ManageRowWidgets", "NewItem": rw})
    g.get("gmch", "ManageCat"); g.call("icmh", K_MATH, "EqualEqual_NameName", inp={"A": "@gmch.ManageCat", "B": "Mods"})
    g.get("gph", "Panel"); g.call("mcs", W_PANEL, "Set Manage Content Space", inp={"self": "@gph.Panel", "keep": "@icmh.ReturnValue"})   # header like the rows
    g.chain("entry", "bpv", "cl", "mcs", "wlc", "spm0", "mr", "sk", "fe"); g.chain("fe", "skn", "srn", "bmh", "spm", "md"); g.chain("bmh:else", "md"); g.chain("md", "sdf", "mo", "sor", "smd", "srs", "mi", "sic", "cw_cr", "smw", "ini", "ad", "wla")
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
    """Name kind of a tile's row: catalog item -> item; hairstyle / skin table row -> hair / skin; appearance preset tile -> preset;
    else makeup (makeup + eyes share 'makeup')."""
    g = G(); g.get("gib", "ItemByName"); g.call("ci", K_MAP, "Map_Contains", inp={"TargetMap": "@gib.ItemByName", "Key": "@entry.name"})
    g.call("ch", K_DT, "DoesDataTableRowExist", inp={"Table": P_HAIR_T, "RowName": "@entry.name"}); g.call("cs", K_DT, "DoesDataTableRowExist", inp={"Table": P_SKIN_T, "RowName": "@entry.name"})
    g.call("cp", K_DT, "DoesDataTableRowExist", inp={"Table": P_ANIM_T, "RowName": "@entry.name"})   # pose rows are renameable too
    g.call("s0p", K_MATH, "SelectString", inp={"A": "pose", "B": "makeup", "bPickA": "@cp.ReturnValue"})
    g.call("s1", K_MATH, "SelectString", inp={"A": "skin", "B": "@s0p.ReturnValue", "bPickA": "@cs.ReturnValue"}); g.call("s2", K_MATH, "SelectString", inp={"A": "hair", "B": "@s1.ReturnValue", "bPickA": "@ch.ReturnValue"})
    g.call("s3", K_MATH, "SelectString", inp={"A": "item", "B": "@s2.ReturnValue", "bPickA": "@ci.ReturnValue"})
    g.call("pn", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"}); g.call("ispr", K_STR, "StartsWith", inp={"SourceString": "@pn.ReturnValue", "InPrefix": "Preset_", "SearchCase": "CaseSensitive"})
    g.call("s4", K_MATH, "SelectString", inp={"A": "preset", "B": "@s3.ReturnValue", "bPickA": "@ispr.ReturnValue"})   # appearance preset tile (Preset_<position>)
    g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@s4.ReturnValue"}); g.link("s2n.ReturnValue", "return.kind")
    g.chain("entry", "ch", "cs", "cp", "return")   # DoesDataTableRowExist has exec pins -> not pure
    return fn("Rename Kind", [param("name", "name")], [param("kind", "name")], graph=g)


def f_start_item_rename():
    """Context menu 'Rename…': the text field on the last clicked tile with the shown name; the manager polls the tile for focus loss (Tick)."""
    g = G(); g.get("glb", "LastButton"); g.cast("cb", W_BTN, "@glb.LastButton"); g.call("cv", K_SYS, "IsValid", inp={"Object": "@cb.AsW_ClothesButton"}); g.branch("bv", "@cv.ReturnValue")
    g.n("rk", "call_self", function="Rename Kind", inp={"name": "@entry.name"}); g.n("dn", "call_self", function="Display Name", inp={"kind": "@rk.kind", "row": "@entry.name"})
    # poses: the shown name is the table title, not the row name (a mod often names its rows after the pak)
    g.n("pn", "call_self", function="Pose Name", inp={"row": "@entry.name"})
    g.call("isp", K_MATH, "EqualEqual_NameName", inp={"A": "@rk.kind", "B": "pose"}); g.call("cur0", K_MATH, "SelectString", inp={"A": "@pn.s", "B": "@dn.s", "bPickA": "@isp.ReturnValue"})
    # presets: the name shown on the tile (custom or "Preset <n>")
    g.n("pix", "call_self", function="Preset Index", inp={"name": "@entry.name"}); g.n("psn", "call_self", function="Preset Shown Name", inp={"index": "@pix.index"})
    g.call("ispr", K_MATH, "EqualEqual_NameName", inp={"A": "@rk.kind", "B": "preset"}); g.call("cur", K_MATH, "SelectString", inp={"A": "@psn.s", "B": "@cur0.ReturnValue", "bPickA": "@ispr.ReturnValue"})
    g.get("glb2", "LastButton"); g.set("srt", "RenameTile", inp={"RenameTile": "@glb2.LastButton"})
    g.call("br", W_BTN, "Begin Rename", inp={"self": "@cb.AsW_ClothesButton", "current": "@cur.ReturnValue"}); g.chain("entry", "bv", "rk", "pn", "pix", "srt", "br")
    return fn("Start Item Rename", [param("name", "name")], graph=g)


def f_finish_item_rename():
    """Enter in a tile's rename field: trimmed text (equal to the default stores nothing) -> Set Custom Name, then the page shows the name."""
    g = G(); g.n("rk", "call_self", function="Rename Kind", inp={"name": "@entry.name"}); g.set("skn", "TmpName", inp={"TmpName": "@rk.kind"}); g.get("gkn", "TmpName")
    g.call("tr", K_STR, "Trim", inp={"SourceString": "@entry.text"}); g.call("tr2", K_STR, "TrimTrailing", inp={"SourceString": "@tr.ReturnValue"})
    g.n("md", "call_self", function="Manage Default", inp={"kind": "@gkn.TmpName", "row": "@entry.name"})
    # presets: stored under the icon number, the default is "Preset <position>"
    g.call("ispr", K_MATH, "EqualEqual_NameName", inp={"A": "@gkn.TmpName", "B": "preset"}); g.n("pix", "call_self", function="Preset Index", inp={"name": "@entry.name"})
    g.n("psn", "call_self", function="Preset Shown Name", inp={"index": "@pix.index"}); g.n("pnr", "call_self", function="Preset Name Row", inp={"index": "@pix.index"})
    g.call("dflt", K_MATH, "SelectString", inp={"A": "@psn.default", "B": "@md.s", "bPickA": "@ispr.ReturnValue"})
    g.call("rs", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"}); g.call("prs", K_STR, "Conv_NameToString", inp={"InName": "@pnr.row"})
    g.call("rsel", K_MATH, "SelectString", inp={"A": "@prs.ReturnValue", "B": "@rs.ReturnValue", "bPickA": "@ispr.ReturnValue"}); g.call("rn", K_STR, "Conv_StringToName", inp={"InString": "@rsel.ReturnValue"})
    g.call("same", K_STR, "EqualEqual_StrStr", inp={"A": "@tr2.ReturnValue", "B": "@dflt.ReturnValue"}); g.call("val", K_MATH, "SelectString", inp={"A": "", "B": "@tr2.ReturnValue", "bPickA": "@same.ReturnValue"})
    g.get("gkn2", "TmpName"); g.n("sn", "call_self", function="Set Custom Name", inp={"kind": "@gkn2.TmpName", "row": "@rn.ReturnValue", "name": "@val.ReturnValue"})
    g.n("ra", "call_self", function="Refresh After Rename"); g.chain("entry", "rk", "skn", "md", "pix", "sn", "ra")
    return fn("Finish Item Rename", [param("name", "name"), param("text", "string")], graph=g)


def f_refresh_after_rename():
    """Catalog (names + search), then the tiles of the current view: content view / clothes list / bag / hair / look."""
    g = G(); g.n("rc", "call_self", function="Rebuild Catalog If Dirty")
    g.get("gpg0", "Page"); g.n("cop", "call_self", function="Content Open", inp={"page": "@gpg0.Page"}); g.branch("bco", "@cop.yes"); g.n("rct", "call_self", function="Rebuild Content")
    pages = [("Clothes", "Rebuild List"), ("Bag", "Rebuild Bag"), ("Hair", "Rebuild Hair"), ("Look", "Rebuild Look"), ("Poses", "Rebuild Poses")]
    for i, (pg, fnn) in enumerate(pages):
        g.get("gpg%d" % (i + 1), "Page"); g.call("is%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@gpg%d.Page" % (i + 1), "B": pg}); g.branch("b%d" % i, "@is%d.ReturnValue" % i); g.n("r%d" % i, "call_self", function=fnn)
    g.chain("entry", "rc", "cop", "bco", "rct"); g.chain("bco:else", "b0", "r0")   # Content Open has exec pins
    for i in range(len(pages) - 1): g.chain("b%d:else" % i, "b%d" % (i + 1), "r%d" % (i + 1))
    return fn("Refresh After Rename", graph=g)


def f_manage_rename():
    """'Rename mod… / Rename group…': the Manage tab, category cat (Mods / Vanilla), search cleared, the row's text field focused and scrolled
    into view. An open content view is dropped first (it would stay over the page). ManageCat before Select Page
    (Select Page rebuilds the Manage page with the current category)."""
    g = G()
    # an open content view first (it is an overlay of the page it was opened from - without this it stayed up, and
    # closing it by hand then went back to that page instead of leaving one in the Manage tab)
    g.set("cvm", "ViewMod", inp={"ViewMod": "None"}); g.set("cvo", "ViewOutfit", inp={"ViewOutfit": "-1"})
    g.set("cvl", "ViewLook", inp={"ViewLook": "-1"}); g.set("cvp", "ViewPreset", inp={"ViewPreset": "-1"}); g.set("cvf", "ViewFace", inp={"ViewFace": "-1"})
    g.set("smc", "ManageCat", inp={"ManageCat": "@entry.cat"}); g.set("sst", "ManageSearchText", inp={"ManageSearchText": ""}); g.set("spp", "Page", inp={"Page": "Manage"})   # Page also without a panel (editor tests)
    g.get("gp", "Panel"); g.call("pv", K_SYS, "IsValid", inp={"Object": "@gp.Panel"}); g.branch("bpv", "@pv.ReturnValue")
    g.get("gp2", "Panel"); g.call("pcs", W_PANEL, "Clear Manage Search", inp={"self": "@gp2.Panel"})
    g.n("sp", "call_self", function="Select Page", inp={"name": "Manage"})
    g.get("gl", "ManageRowWidgets"); g.foreach("fe", "@gl.ManageRowWidgets"); g.cast("cr", W_NAMEROW, "@fe.Array Element")
    g.get("gk", "Kind", cls=W_NAMEROW); g.link("cr.AsW_NameRow", "gk.self"); g.get("grw", "Row", cls=W_NAMEROW); g.link("cr.AsW_NameRow", "grw.self")
    g.call("ek", K_MATH, "EqualEqual_NameName", inp={"A": "@gk.Kind", "B": "@entry.kind"}); g.call("er", K_MATH, "EqualEqual_NameName", inp={"A": "@grw.Row", "B": "@entry.row"})
    g.call("hit", K_MATH, "BooleanAND", inp={"A": "@ek.ReturnValue", "B": "@er.ReturnValue"}); g.branch("bh", "@hit.ReturnValue")
    g.call("fe2", W_NAMEROW, "Focus Edit", inp={"self": "@cr.AsW_NameRow"}); g.get("gp3", "Panel"); g.call("siv", W_PANEL, "Scroll Into View", inp={"self": "@gp3.Panel", "page": "Manage", "widget": "@fe.Array Element"})
    g.chain("entry", "cvm", "cvo", "cvl", "cvp", "cvf", "smc", "sst", "spp", "bpv", "pcs", "sp", "fe"); g.chain("fe", "bh", "fe2", "siv")
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
    g.n("rch", "call_self", function="Rebuild Manage Chips")   # "only mods" changes which chips there are
    g.chain("entry", "b", "s", "s2", "sv", "rch", "rc", "rm"); return fn("Poll Manage", graph=g)


# ---------------- context menu: "Only this group", "View mod content"; mod content view ----------------
def f_show_only_group():
    """Group chip of the piece + the All slot; search cleared and a filter that would hide the piece switched off (like Go To Item)."""
    g = G()
    g.n("fi", "call_self", function="Find Item", inp={"name": "@entry.name"}); g.brk("bi", S_ITEM, "@fi.item")
    g.get("gp", "Panel"); g.call("pcs", W_PANEL, "Clear Search", inp={"self": "@gp.Panel"}); g.set("sst", "SearchText", inp={"SearchText": ""})
    g.n("io", "call_self", function="Is Owned", inp={"name": "@entry.name"}); g.get("gco", "CachedOnlyOwned"); g.call("no", K_MATH, "BooleanAND", inp={"A": "@gco.CachedOnlyOwned", "B": "@io.yes"})
    g.n("ifv", "call_self", function="Is Favorite", inp={"name": "@entry.name"}); g.get("gcf", "CachedOnlyFav"); g.call("nf", K_MATH, "BooleanAND", inp={"A": "@gcf.CachedOnlyFav", "B": "@ifv.yes"})
    g.get("gcv", "CachedOnlyVanilla"); g.call("nv", K_MATH, "BooleanAND", inp={"A": "@gcv.CachedOnlyVanilla", "B": "@bi.IsVanilla"})
    g.n("iwn", "call_self", function="Is Worn", inp={"name": "@entry.name"}); g.get("gcw", "CachedOnlyWorn"); g.call("nw", K_MATH, "BooleanAND", inp={"A": "@gcw.CachedOnlyWorn", "B": "@iwn.yes"})
    g.set("sco", "CachedOnlyOwned", inp={"CachedOnlyOwned": "@no.ReturnValue"}); g.set("scf", "CachedOnlyFav", inp={"CachedOnlyFav": "@nf.ReturnValue"}); g.set("scv", "CachedOnlyVanilla", inp={"CachedOnlyVanilla": "@nv.ReturnValue"}); g.set("scw", "CachedOnlyWorn", inp={"CachedOnlyWorn": "@nw.ReturnValue"})
    g.get("gp2", "Panel"); g.get("gco2", "CachedOnlyOwned"); g.get("gcf2", "CachedOnlyFav"); g.get("gcv2", "CachedOnlyVanilla"); g.get("gcw2", "CachedOnlyWorn")
    g.call("sft", W_PANEL, "Set Filter Toggles", inp={"self": "@gp2.Panel", "owned": "@gco2.CachedOnlyOwned", "fav": "@gcf2.CachedOnlyFav", "vanilla": "@gcv2.CachedOnlyVanilla", "worn": "@gcw2.CachedOnlyWorn"})
    g.n("alg", "call_self", function="Group Alias", inp={"group": "@bi.Group"})   # MergeGroups: the chip of the merged group
    g.set("scs", "CurrentSlot", inp={"CurrentSlot": "All"}); g.set("sg", "CurrentGroup", inp={"CurrentGroup": "@alg.alias"})
    g.n("rl", "call_self", function="Rebuild Left"); g.n("rt", "call_self", function="Rebuild SubTabs"); g.n("rli", "call_self", function="Rebuild List"); g.n("sv", "call_self", function="Save Settings")
    g.chain("entry", "fi", "pcs", "sst", "sco", "scf", "scv", "scw", "sft", "scs", "sg", "rl", "rt", "rli", "sv")
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
    # only this slot's catalog list (frozen: Items For Slot is pure), not AllItems per slot - one pass over the catalog instead of slots x catalog
    g.n("isl", "call_self", function="Items For Slot", inp={"slot": "@fs.Array Element"}); g.set("smvi", "ModViewItems", inp={"ModViewItems": "@isl.items"})
    g.get("gai", "ModViewItems"); g.foreach("fi", "@gai.ModViewItems"); g.brk("bi", S_ITEM, "@fi.Array Element")
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@bi.Name"}); g.call("mEq", K_MATH, "EqualEqual_NameName", inp={"A": "@imd.mod", "B": "@gvm.ViewMod"}); g.branch("biok", "@mEq.ReturnValue")
    s1 = mod_section_tiles(g, "c", "@tsl.text", "biok")
    g.set("sti", "TmpItem", inp={"TmpItem": "@fi.Array Element"}); g.get("gti", "TmpItem")
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@bi.Name"}); g.n("io", "call_self", function="Shown Owned", inp={"name": "@bi.Name"})
    g.n("ifv", "call_self", function="Is Favorite", inp={"name": "@bi.Name"}); g.n("idm", "call_self", function="Is Damaged", inp={"name": "@bi.Name"}); g.n("tip", "call_self", function="Item Tip", inp={"item": "@gti.TmpItem", "kind": "item", "category": ""})
    t1, w1 = content_tile(g, "t1", "@gti.TmpItem", "@iw.yes", "@io.yes", "@ifv.yes", "@idm.yes", "@tip.tip")
    g.chain("entry", "clc", "cll", "clk_cr", "sml", "li", "al", "sct", "fs"); g.chain("fs", "f0", "smvi", "fi"); g.chain("fi", "biok")
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
    # --- poses of this mod, one section per chapter of the pack (a marker row) plus one for the poses before the first marker
    g.n("pcol", "call_self", function="Collect Pose Rows")
    g.get("gps2", "PoseSections"); g.call("ins", K_ARR, "Array_Insert", inp={"TargetArray": "@gps2.PoseSections", "NewItem": g.lit_name("pnone", "None"), "Index": "0"})   # "None" = before the first marker
    g.get("gps3", "PoseSections"); g.foreach("fsec", "@gps3.PoseSections")
    g.set("f4", "TmpFound", inp={"TmpFound": "false"})
    g.call("secn", K_MATH, "EqualEqual_NameName", inp={"A": "@fsec.Array Element", "B": "None"})
    g.n("scap", "call_self", function="Pose Section Caption", inp={"row": "@fsec.Array Element"})
    g.call("psel0", K_TXT, "Conv_TextToString", inp={"InText": "@scap.caption"}); g.call("pt0", K_TXT, "Conv_TextToString", inp={"InText": tt(g, "s4t", "Tab_Poses")})
    g.call("csel", K_MATH, "SelectString", inp={"A": "@pt0.ReturnValue", "B": "@psel0.ReturnValue", "bPickA": "@secn.ReturnValue"})
    g.call("ctxt", K_TXT, "Conv_StringToText", inp={"InString": "@csel.ReturnValue"})
    # this mod's poses once (ModViewPoses), then per chapter only those - not chapters x all pose rows
    g.get("gmvp0", "ModViewPoses"); g.call("mvpc", K_ARR, "Array_Clear", inp={"TargetArray": "@gmvp0.ModViewPoses"})
    g.get("gpr", "PoseRows"); g.foreach("fpm", "@gpr.PoseRows")
    g.n("pimd", "call_self", function="Item Mod", inp={"row": "@fpm.Array Element"}); g.call("pEq", K_MATH, "EqualEqual_NameName", inp={"A": "@pimd.mod", "B": "@gvm.ViewMod"})
    g.call("pa1", K_MATH, "BooleanAND", inp={"A": "@pimd.found", "B": "@pEq.ReturnValue"}); g.branch("bpm", "@pa1.ReturnValue")
    g.get("gmvp1", "ModViewPoses"); g.call("mvpa", K_ARR, "Array_Add", inp={"TargetArray": "@gmvp1.ModViewPoses", "NewItem": "@fpm.Array Element"})
    g.get("gmvp2", "ModViewPoses"); g.foreach("fp", "@gmvp2.ModViewPoses")
    g.get("gpsec", "PoseSection"); g.call("psf", K_MAP, "Map_Find", inp={"TargetMap": "@gpsec.PoseSection", "Key": "@fp.Array Element"})
    g.call("sEq2", K_MATH, "EqualEqual_NameName", inp={"A": "@psf.Value", "B": "@fsec.Array Element"}); g.branch("bp", "@sEq2.ReturnValue")
    s4 = mod_section_tiles(g, "p", "@ctxt.ReturnValue", "bp")
    g.n("ptt", "call_self", function="Pose Name", inp={"row": "@fp.Array Element"})
    g.make("pmi", S_ITEM, Name="@fp.Array Element", DisplayName="@ptt.s", Icon=T_POSE)
    g.get("gpl4", "Player"); g.get("gnx4", "Action Animation Name Next", cls=P_JODI); g.link("gpl4.Player", "gnx4.self")
    g.call("psel", K_MATH, "EqualEqual_NameName", inp={"A": "@gnx4.Action Animation Name Next", "B": "@fp.Array Element"})
    t4, _ = content_tile(g, "t4", "@pmi.S_ClothesItem", "@psel.ReturnValue", "true", "false", "false", tt(g, "t4t", "Tab_Poses"), kind="pose")
    g.chain("ft:Completed", "pcol", "ins", "mvpc", "fpm"); g.chain("fpm", "bpm", "mvpa"); g.chain("fpm:Completed", "fsec"); g.chain("fsec", "f4", "scap", "fp"); g.chain("fp", "bp")
    for x in s4: g.chain(x, "ptt", *t4)
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
    g.call("isps", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Poses"}); g.branch("bps", "@isps.ReturnValue"); g.n("rpl", "call_self", function="Rebuild Pose Links"); g.n("rpcat", "call_self", function="Rebuild Pose Cats"); g.n("rpc", "call_self", function="Rebuild Pose Chips"); g.n("rps", "call_self", function="Rebuild Poses")
    g.call("isw", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Weapons"}); g.branch("bw", "@isw.ReturnValue"); g.n("rwl", "call_self", function="Rebuild Weapon Links"); g.n("rwp", "call_self", function="Rebuild Weapons"); g.n("rwc", "call_self", function="Rebuild Weapon Chips"); g.n("rws", "call_self", function="Rebuild Weapon Skins"); g.n("rwmo", "call_self", function="Rebuild Weapon Models")
    g.call("isl", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Look"}); g.branch("bl", "@isl.ReturnValue")
    g.n("rlc", "call_self", function="Rebuild Look Cats"); g.n("rlk", "call_self", function="Rebuild Look"); g.n("rll", "call_self", function="Rebuild Look Links"); g.n("rlch", "call_self", function="Rebuild Look Chips")
    g.n("rcdl", "call_self", function="Rebuild Catalog If Dirty")   # a renamed mod changes the mod aliases (MergeMods) - the catalog rebuild refreshes them
    g.call("isy", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Body"}); g.branch("by", "@isy.ReturnValue"); g.n("rby", "call_self", function="Rebuild Body")
    g.call("isfc", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Face"}); g.branch("bfc", "@isfc.ReturnValue"); g.n("rfc", "call_self", function="Rebuild Face Page")
    g.call("iso2", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Options"}); g.branch("bop", "@iso2.ReturnValue"); g.n("rop", "call_self", function="Rebuild Options")
    g.get("gpoc", "Panel"); g.get("goc", "OptionsCat"); g.call("soc", W_PANEL, "Set Option Cat", inp={"self": "@gpoc.Panel", "cat": "@goc.OptionsCat"}); g.n("roc", "call_self", function="Rebuild Option Cats")
    g.call("ismd", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Mods"}); g.branch("bmd", "@ismd.ReturnValue"); g.n("rmd", "call_self", function="Rebuild Mod Page")
    g.call("isM", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "Manage"}); g.branch("bM", "@isM.ReturnValue")
    g.get("gpm", "Panel"); g.get("gom", "OnlyModsNames"); g.call("som", W_PANEL, "Set Only Mods", inp={"self": "@gpm.Panel", "on": "@gom.OnlyModsNames"})
    g.get("gpcs", "Panel"); g.get("gcsn", "CaseSensitiveNames"); g.call("scs", W_PANEL, "Set Case Sens", inp={"self": "@gpcs.Panel", "on": "@gcsn.CaseSensitiveNames"})
    g.n("rmc", "call_self", function="Rebuild Manage Cats"); g.n("rml", "call_self", function="Rebuild Manage Links"); g.n("rmr", "call_self", function="Rebuild Manage"); g.n("rmch", "call_self", function="Rebuild Manage Chips")
    g.n("cmn", "call_self", function="Close Menu")   # a context menu of the previous page would stay open otherwise
    g.chain("entry", "bkh", "skh", "cmn"); g.chain("bkh:else", "shl", "cmn")
    g.get("gpg0", "Page"); g.call("pne", K_MATH, "NotEqual_NameName", inp={"A": "@gpg0.Page", "B": "@entry.name"}); g.branch("bpn", "@pne.ReturnValue")
    g.set("svm0", "ViewMod", inp={"ViewMod": "None"})   # the mod content view is not tied to a tab: another tab closes it (outfit / look / preset views belong to their tab)
    g.n("rstp", "call_self", function="Rebuild Status")   # the right-hand zone belongs to the page: it has to follow the switch
    g.chain("cmn", "bpn", "svm0", "sp"); g.chain("bpn:else", "sp"); g.chain("sp", "rstp", "spg", "rtt", "uf", "co", "bco", "spc", "rcn")
    g.chain("bco:else", "bo", "ro"); g.chain("bo:else", "blk", "rlk2"); g.chain("blk:else", "bb", "rb"); g.chain("bb:else", "bc", "rcd", "rl", "rt", "rli")
    g.chain("bc:else", "bh", "rh"); g.chain("bh:else", "bps", "rpl", "rpcat", "rpc", "rps"); g.chain("bps:else", "bw", "rwl", "rwp", "rwc", "rwmo", "rws"); g.chain("bw:else", "bl", "rcdl", "rll", "rlch", "rlc", "rlk"); g.chain("bl:else", "by", "rby"); g.chain("by:else", "bfc", "rfc"); g.chain("bfc:else", "bmd", "rmd"); g.chain("bmd:else", "bop", "soc", "roc", "rop"); g.chain("bop:else", "bM", "som", "scs", "rmch", "rmc", "rml", "rmr")
    return fn("Select Page Inner" if TABLOG else "Select Page", [param("name", "name")], graph=g)


def f_select_page_timed():
    """ALTUI_TABLOG: Select Page = time + Select Page Inner + one log line with the duration in ms. GetAccurateRealTime is pure and every
    consumer evaluates it anew: one set node takes (Seconds mod 1000) + PartialSeconds (mod keeps float precision ~0.06 ms; a wrap is undone)."""
    g = G()
    def stamp(id):
        g.call(id, K_GS, "GetAccurateRealTime"); g.call(id + "m", K_MATH, "Percent_IntInt", inp={"A": "@%s.Seconds" % id, "B": "1000"})
        g.call(id + "f", K_MATH, "Conv_IntToFloat", inp={"InInt": "@%sm.ReturnValue" % id}); g.call(id + "a", K_MATH, "Add_FloatFloat", inp={"A": "@%sf.ReturnValue" % id, "B": "@%s.PartialSeconds" % id})
        return "@%sa.ReturnValue" % id
    g.set("s0", "TabP0", inp={"TabP0": stamp("t0")})
    g.n("in", "call_self", function="Select Page Inner", inp={"name": "@entry.name"})
    g.get("gp0", "TabP0"); g.call("d", K_MATH, "Subtract_FloatFloat", inp={"A": stamp("t1"), "B": "@gp0.TabP0"})
    g.call("neg", K_MATH, "Less_FloatFloat", inp={"A": "@d.ReturnValue", "B": "0.0"}); g.call("wr", K_MATH, "SelectFloat", inp={"A": "1000.0", "B": "0.0", "bPickA": "@neg.ReturnValue"})
    g.call("sec", K_MATH, "Add_FloatFloat", inp={"A": "@d.ReturnValue", "B": "@wr.ReturnValue"})
    g.call("ms", K_MATH, "Multiply_FloatFloat", inp={"A": "@sec.ReturnValue", "B": "1000.0"}); g.set("s1", "TabP0", inp={"TabP0": "@ms.ReturnValue"})   # freeze: the log line reads it once
    g.get("gms", "TabP0"); g.call("mss", K_STR, "Conv_FloatToString", inp={"InFloat": "@gms.TabP0"})
    g.get("gh", "HiddenTabs"); g.call("hm", K_ARR, "Array_Contains", inp={"TargetArray": "@gh.HiddenTabs", "ItemToFind": g.lit_name("lmods", "Mods")}); g.call("hms", K_STR, "Conv_BoolToString", inp={"InBool": "@hm.ReturnValue"})
    log(g, "tab", ["tab ", nstr(g, "pg", "@entry.name"), " ", "@mss.ReturnValue", " mods_hidden=", "@hms.ReturnValue"])
    g.chain("entry", "s0", "in", "s1", "lgtab"); return fn("Select Page", [param("name", "name")], graph=g)


def f_rebuild_outfits():
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Outfits", inp={"self": "@gp.Panel"})
    # "+" tile
    g.get("gi0", "TmpIcons"); g.call("clr0", K_ARR, "Array_Clear", inp={"TargetArray": "@gi0.TmpIcons"})
    aw = create_widget(g, "ca", W_OUTFIT); set_manager(g, "sma", W_OUTFIT, aw)
    g.n("osc", "call_self", function="Outfit Scale"); g.n("ocl", "call_self", function="Outfit Cols"); g.n("orw", "call_self", function="Outfit Rows")   # Options > Tiles
    g.call("ocap", K_MATH, "Multiply_IntInt", inp={"A": "@ocl.n", "B": "@orw.n"})   # icons per tile
    g.get("gi1", "TmpIcons"); g.call("ia", W_OUTFIT, "Init", inp={"self": aw, "index": "-1", "icons": "@gi1.TmpIcons", "count": "0", "caption": "", "photo": "false", "scale": "@osc.scale", "cols": "@ocl.n", "rows": "@orw.n"})
    g.get("gpa", "Panel"); g.call("aa", W_PANEL, "Add Outfit", inp={"self": "@gpa.Panel", "widget": aw})
    # per outfit: icons of the first pieces from the catalog
    g.get("go", "Outfits"); g.get("goa", "outfits", cls=P_OUTFITS); g.link("go.Outfits", "goa.self")
    g.foreach("fe", "@goa.outfits"); g.brk("bo", P_OUTFIT_S, "@fe.Array Element")
    g.get("gi2", "TmpIcons"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gi2.TmpIcons"})
    g.call("keys", K_MAP, "Map_Keys", inp={"TargetMap": "@bo." + OUTFIT_MEMBER})
    g.call("len", K_MAP, "Map_Length", inp={"TargetMap": "@bo." + OUTFIT_MEMBER})
    g.foreach("fk", "@keys.Keys")
    g.get("gi3", "TmpIcons"); g.call("cnt", K_ARR, "Array_Length", inp={"TargetArray": "@gi3.TmpIcons"})
    g.call("lt6", K_MATH, "Less_IntInt", inp={"A": "@cnt.ReturnValue", "B": "@ocap.ReturnValue"}); g.branch("b6", "@lt6.ReturnValue")
    g.n("fi", "call_self", function="Find Item", inp={"name": "@fk.Array Element"}); g.brk("bi", S_ITEM, "@fi.item")
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@bi.Icon"}); g.branch("biv", "@iv.ReturnValue")
    g.get("gi4", "TmpIcons"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gi4.TmpIcons", "NewItem": "@bi.Icon"})
    ow = create_widget(g, "co", W_OUTFIT); set_manager(g, "smo", W_OUTFIT, ow)
    g.n("on", "call_self", function="Outfit Name", inp={"index": "@fe.Array Index"}); g.call("ont", K_TXT, "Conv_StringToText", inp={"InString": "@on.name"})
    g.get("gi5", "TmpIcons"); g.call("io", W_OUTFIT, "Init", inp={"self": ow, "index": "@fe.Array Index", "icons": "@gi5.TmpIcons", "count": "@len.ReturnValue", "caption": "@ont.ReturnValue", "photo": "false", "scale": "@osc.scale", "cols": "@ocl.n", "rows": "@orw.n"})
    g.get("gpo", "Panel"); g.call("ao", W_PANEL, "Add Outfit", inp={"self": "@gpo.Panel", "widget": ow})
    g.chain("entry", "cl", "clr0", "ca_cr", "sma", "ia", "aa", "fe"); g.chain("fe", "clr", "keys", "fk")
    g.chain("fk", "b6", "fi", "biv", "add"); g.chain("fk:Completed", "on", "co_cr", "smo", "io", "ao")
    return fn("Rebuild Outfits", graph=g)


def f_outfit_slot_key():
    """Key of one remembered slot colour of an outfit in OutfitSlotColors: <Outfit Key>><piece>#<slot index>."""
    g = G()
    g.n("sk", "call_self", function="Slot Color Key", inp={"name": "@entry.name", "slot": "@entry.slot"})
    g.call("k2s", K_STR, "Conv_NameToString", inp={"InName": "@sk.key"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@entry.okey", "B": ">"}); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@k2s.ReturnValue"})
    g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@c2.ReturnValue"}); g.link("s2n.ReturnValue", "return.key")
    return fn("Outfit Slot Key", [param("okey", "string"), param("name", "name"), param("slot", "int")], [param("key", "name")], graph=g, pure=True)


def outfit_slots_loop(g, index_pin):
    """Nested loops over the pieces of outfit `index` and their colourable slots. Returns (head, body pins): head = exec id
    to start with, body = (slot key pin, outfit slot key pin, inner loop id) - the inner loop body is chained by the caller."""
    g.n("ok", "call_self", function="Outfit Key", inp={"index": index_pin}); g.set("sok", "OutfitKeyTmp", inp={"OutfitKeyTmp": "@ok.key"})
    g.get("go", "Outfits"); g.get("goa", "outfits", cls=P_OUTFITS); g.link("go.Outfits", "goa.self")
    g.call("og", K_ARR, "Array_Get", inp={"TargetArray": "@goa.outfits", "Index": index_pin}); g.brk("obr", P_OUTFIT_S, "@og.Item")
    g.call("keys", K_MAP, "Map_Keys", inp={"TargetMap": "@obr." + OUTFIT_MEMBER}); g.set("skn", "OutfitPieces", inp={"OutfitPieces": "@keys.Keys"})
    g.get("gkn", "OutfitPieces"); g.foreach("fp", "@gkn.OutfitPieces")
    g.n("cs", "call_self", function="Item Color Slots", inp={"name": "@fp.Array Element"}); g.brk("bcs", S_COLSLOTS, "@cs.slots")
    g.foreach("fi", "@bcs.Idx")
    g.n("sk", "call_self", function="Slot Color Key", inp={"name": "@fp.Array Element", "slot": "@fi.Array Element"})
    g.get("gok", "OutfitKeyTmp"); g.n("osk", "call_self", function="Outfit Slot Key", inp={"okey": "@gok.OutfitKeyTmp", "name": "@fp.Array Element", "slot": "@fi.Array Element"})
    g.chain("ok", "sok", "keys", "skn", "fp"); g.chain("fp", "cs", "fi")
    return "ok", "@sk.key", "@osk.key", "fi"


def f_remember_outfit_colors():
    """When an outfit is saved: AltUI's slot colours of its pieces, as they are now, go into OutfitSlotColors under the
    outfit's key; a slot without one clears what an earlier outfit with the same pieces left there."""
    g = G()
    head, sk, osk, inner = outfit_slots_loop(g, "@entry.index")
    g.get("gsc", "SlotColors"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gsc.SlotColors", "Key": sk}); g.branch("bf", "@f.ReturnValue")
    g.get("gos", "OutfitSlotColors"); g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gos.OutfitSlotColors", "Key": osk, "Value": "@f.Value"})
    g.get("gos2", "OutfitSlotColors"); g.call("rem", K_MAP, "Map_Remove", inp={"TargetMap": "@gos2.OutfitSlotColors", "Key": osk})
    g.n("ss", "call_self", function="Save Settings")
    g.chain("entry", head); g.chain(inner, "bf", "add"); g.chain("bf:else", "rem"); g.chain("fp:Completed", "ss")
    return fn("Remember Outfit Colors", [param("index", "int")], graph=g)


def f_outfit_slot_colors():
    """The slot colours wearing outfit `index` leaves behind, in OutfitSC: AltUI's current ones, where for every colourable
    slot of the outfit's pieces the remembered colour is put in - or, without one, AltUI's colour taken out, so the
    outfit's own colour of the piece shows (an outfit saved before AltUI remembered colours has none)."""
    g = G()
    g.get("gsc", "SlotColors"); g.set("cp", "OutfitSC", inp={"OutfitSC": "@gsc.SlotColors"})
    head, sk, osk, inner = outfit_slots_loop(g, "@entry.index")
    g.get("gos", "OutfitSlotColors"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gos.OutfitSlotColors", "Key": osk}); g.branch("bf", "@f.ReturnValue")
    g.get("goc", "OutfitSC"); g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@goc.OutfitSC", "Key": sk, "Value": "@f.Value"})
    g.get("goc2", "OutfitSC"); g.call("rem", K_MAP, "Map_Remove", inp={"TargetMap": "@goc2.OutfitSC", "Key": sk})
    g.chain("entry", "cp", head); g.chain(inner, "bf", "add"); g.chain("bf:else", "rem")
    return fn("Outfit Slot Colors", [param("index", "int")], graph=g)


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
    g.n("osc", "call_self", function="Outfit Slot Colors", inp={"index": "@entry.index"})
    g.get("gsc9", "OutfitSC"); g.get("gec9", "EyeColors"); g.get("gmc9", "MakeupColors")
    g.make("mk", S_SNAP, Face="@bs.Face", FaceAdd="@bs.FaceAdd", SlotColors="@gsc9.OutfitSC", EyeColors="@gec9.EyeColors", MakeupColors="@gmc9.MakeupColors", Worn="@keys.Keys", Makeup="@bs.Makeup", Skin="@bs.Skin", Hair="@bs.Hair", Colors="@gtc3.TmpColors", HairColor="@bs.HairColor",
           Boobs="@bs.Boobs", Waist="@bs.Waist", Hip="@bs.Hip", Body="@bs.Body", Scales="@bs.Scales")
    g.n("as", "call_self", function="Apply Snapshot", inp={"snap": "@mk.S_Snapshot"})
    g.n("sv", "call_self", function="Save Outfits"); g.n("ro", "call_self", function="Rebuild Outfits")
    g.get("go3", "Outfits"); g.get("goa3", "outfits", cls=P_OUTFITS); g.link("go3.Outfits", "goa3.self")
    g.call("ol", K_ARR, "Array_Length", inp={"TargetArray": "@goa3.outfits"}); g.call("last", K_MATH, "Subtract_IntInt", inp={"A": "@ol.ReturnValue", "B": "1"})
    g.n("roc", "call_self", function="Remember Outfit Colors", inp={"index": "@last.ReturnValue"})   # Add Preset appends
    g.chain("entry", "bpl", "pa"); g.chain("bpl:else", "b", "ap", "roc", "sv", "ro"); g.chain("b:else", "ph", "ts", "keys", "mclr", "fk"); g.chain("fk", "madd"); g.chain("fk:Completed", "osc", "as", "ro")
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
    g.call("wi", W_BTN, "Init", inp={"self": ww, "item": "@fi.item", "worn": "true", "owned": "@io.yes", "fav": "@ifv.yes", "damaged": "@dm.yes", "tip": "@wti.tip", "dim": "false"})
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
    g.call("bi", W_BTN, "Init", inp={"self": bw, "item": "@fi2.item", "worn": "false", "owned": "@io2.yes", "fav": "@ifv2.yes", "damaged": "@dm2.yes", "tip": "@bti2.tip", "dim": "false"})
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
def make_item(g, id, name_pin, icon_pin, slot=None, kind="item", color=None):
    """S_ClothesItem for non-clothes (hairstyle/skin/makeup): name, display name via Display Name(kind, row) (custom name, else the row name),
    icon; slot = origin for the content view (Hair / Skin / <type> / Body); color = pin for the colour-wheel badge."""
    g.n(id + "_n", "call_self", function="Display Name", inp={"kind": kind, "row": name_pin})
    g.make(id, S_ITEM, Name=name_pin, DisplayName="@%s_n.s" % id, Icon=icon_pin, **({"Slot": slot} if slot else {}),
           **({"ColorAdjustable": color} if color else {})); return "@%s.S_ClothesItem" % id


def tile_tip(g, id, item_pin, kind, category_pin):
    """Item Tip node for a look tile (hair / skin / makeup / body): the category text becomes the "s:" line; returns (node id, tip pin)."""
    g.n(id + "_tp", "call_self", function="Item Tip", inp={"item": item_pin, "kind": kind, "category": category_pin}); return id + "_tp", "@%s_tp.tip" % id


def look_tile(g, id, item_pin, selected_pin, owned_pin, add_fn, tip_pin, kind=None, fav_pin="false", dim_pin="false"):
    """Create W_ClothesButton + init + add to the panel; returns the exec chain. tip_pin = tooltip text; with kind (hair / skin / makeup) it is the
    category text and the tooltip comes from Item Tip (presets: no kind, the text itself)."""
    pre = []
    if kind: n, tip_pin = tile_tip(g, id, item_pin, kind, tip_pin); pre = [n]
    tw = create_widget(g, id, W_BTN); set_manager(g, id + "_sm", W_BTN, tw)
    g.call(id + "_i", W_BTN, "Init", inp={"self": tw, "item": item_pin, "worn": selected_pin, "owned": owned_pin, "fav": fav_pin, "damaged": "false", "tip": tip_pin, "dim": dim_pin})
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
    g.get(id + "_p", "Wearer"); g.call(id, P_JODI_BASE, "Get Makeup Data", inp={"self": "@%s_p.Wearer" % id}); return "@%s.Makeup Data" % id


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


# ---------------- Poses tab: AnimationTable rows (vanilla + merged Mod_AnimationTable rows), chips per mod, search, favourites, hide ----------------
T_POSE = M + "/T_Pose"


def f_collect_pose_rows():
    """PoseRows = AnimationTable rows without the Dressup_* automatic rows and without the chapter markers a pose mod inserts
    (a row without a montage: "- [ LAYING POSES ] -"). Every marker opens a chapter, the rows after it are filed under it
    (PoseSection), so the sidebar can offer the mod's own chapters."""
    g = G()
    for i, v in enumerate(("PoseRows", "PoseSections")):
        g.get("gc%d" % i, v); g.call("clr%d" % i, K_ARR, "Array_Clear", inp={"TargetArray": "@gc%d.%s" % (i, v)})
    g.get("gsec", "PoseSection"); g.call("mclr", K_MAP, "Map_Clear", inp={"TargetMap": "@gsec.PoseSection"}); g.set("cur", "TmpName2", inp={"TmpName2": "None"})
    g.call("rn", K_DT, "GetDataTableRowNames", inp={"Table": P_ANIM_T}); g.set("sn", "TmpNames2", inp={"TmpNames2": "@rn.OutRowNames"}); g.get("gn", "TmpNames2"); g.foreach("fe", "@gn.TmpNames2")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@fe.Array Element"})
    g.call("sw", K_STR, "StartsWith", inp={"SourceString": "@n2s.ReturnValue", "InPrefix": "Dressup_", "SearchCase": "CaseSensitive"}); g.branch("b", "@sw.ReturnValue")
    g.n("row", "get_row", table=P_ANIM_T, inp={"RowName": "@fe.Array Element"}, miss="ignore"); g.brk("br", P_ANIM_S, "@row.OutRow")
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@br.Montage"}); g.branch("bm", "@iv.ReturnValue")
    # marker row: opens a chapter
    g.set("scur", "TmpName2", inp={"TmpName2": "@fe.Array Element"})
    g.get("gs1", "PoseSections"); g.call("adds", K_ARR, "Array_Add", inp={"TargetArray": "@gs1.PoseSections", "NewItem": "@fe.Array Element"})
    # pose row: list it and file it under the open chapter
    g.get("gr1", "PoseRows"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gr1.PoseRows", "NewItem": "@fe.Array Element"})
    g.get("gsec2", "PoseSection"); g.get("gcur", "TmpName2"); g.call("madd", K_MAP, "Map_Add", inp={"TargetMap": "@gsec2.PoseSection", "Key": "@fe.Array Element", "Value": "@gcur.TmpName2"})
    g.chain("entry", "clr0", "clr1", "mclr", "cur", "rn", "sn", "fe"); g.chain("fe", "b"); g.chain("b:else", "row", "bm", "add", "madd")
    g.chain("bm:else", "scur", "adds"); g.chain("row:Row Not Found", "add")
    return fn("Collect Pose Rows", graph=g)


def f_pose_section_caption():
    """Sidebar caption of a chapter: the marker's title without the decoration modders wrap it in ("- [ LAYING POSES ] -")."""
    g = G(); g.n("pt", "call_self", function="Pose Title", inp={"row": "@entry.row"})
    g.call("t1", K_STR, "Replace", inp={"SourceString": "@pt.title", "From": "- [", "To": "", "SearchCase": "IgnoreCase"})
    g.call("t2", K_STR, "Replace", inp={"SourceString": "@t1.ReturnValue", "From": "] -", "To": "", "SearchCase": "IgnoreCase"})
    g.call("t3", K_STR, "Replace", inp={"SourceString": "@t2.ReturnValue", "From": "----", "To": "", "SearchCase": "IgnoreCase"})
    g.call("t4", K_STR, "Trim", inp={"SourceString": "@t3.ReturnValue"}); g.call("t5", K_STR, "TrimTrailing", inp={"SourceString": "@t4.ReturnValue"})
    g.call("em", K_STR, "IsEmpty", inp={"InString": "@t5.ReturnValue"}); g.call("rs", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"})
    g.call("sel", K_MATH, "SelectString", inp={"A": "@rs.ReturnValue", "B": "@t5.ReturnValue", "bPickA": "@em.ReturnValue"})
    g.call("txt", K_TXT, "Conv_StringToText", inp={"InString": "@sel.ReturnValue"}); g.link("txt.ReturnValue", "return.caption")
    g.chain("entry", "pt", "return")
    return fn("Pose Section Caption", [param("row", "name")], [param("caption", "text")], graph=g)


def f_pose_section_count():
    """Count of one chapter - from the same pass; PoseSection keys the chapter by its row name."""
    g = G()
    g.get("gc", "PoseCounts"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gc.PoseCounts", "Key": "@entry.row"})
    g.get("gf", "PoseCountsF"); g.call("ff", K_MAP, "Map_Find", inp={"TargetMap": "@gf.PoseCountsF", "Key": "@entry.row"})
    g.call("sel", K_MATH, "SelectInt", inp={"A": "@ff.Value", "B": "@f.Value", "bPickA": "@entry.filtered"})
    g.link("sel.ReturnValue", "return.n"); g.chain("entry", "return")
    return fn("Pose Section Count", [param("row", "name"), param("filtered", "bool")], [param("n", "int")], graph=g)


def f_pose_title():
    """Title of an AnimationTable row as a string; "None" is the default tile (no pose), empty title or unknown row -> the row name."""
    g = G(); g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"}); g.set("s0", "TmpStr", inp={"TmpStr": "@n2s.ReturnValue"})
    g.call("isn", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.row", "B": "None"}); g.branch("bn", "@isn.ReturnValue")
    g.call("dts", K_TXT, "Conv_TextToString", inp={"InText": tt(g, "dt", "Pose_Default")}); g.set("sd", "TmpStr", inp={"TmpStr": "@dts.ReturnValue"})
    g.n("row", "get_row", table=P_ANIM_T, inp={"RowName": "@entry.row"}); g.brk("br", P_ANIM_S, "@row.OutRow")
    g.call("te", K_TXT, "TextIsEmpty", inp={"InText": "@br.Title"}); g.branch("be", "@te.ReturnValue")
    g.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@br.Title"}); g.set("s1", "TmpStr", inp={"TmpStr": "@t2s.ReturnValue"})
    g.get("gs", "TmpStr"); g.link("gs.TmpStr", "return.title")
    g.chain("entry", "s0", "bn", "sd", "return"); g.chain("bn:else", "row", "be", "return"); g.chain("be:else", "s1", "return"); g.chain("row:Row Not Found", "return")
    return fn("Pose Title", [param("row", "name")], [param("title", "string")], graph=g)


def f_pose_name():
    """Shown name of a pose: custom name (context menu "Rename"), else the title from the table."""
    g = G(); g.n("pt", "call_self", function="Pose Title", inp={"row": "@entry.row"})
    g.n("sh", "call_self", function="Shown Name", inp={"kind": "pose", "row": "@entry.row", "default": "@pt.title"}); g.link("sh.name", "return.s")
    g.chain("entry", "pt", "return")
    return fn("Pose Name", [param("row", "name")], [param("s", "string")], graph=g)


def f_pose_key():
    """Favourites / hidden key of a pose: pose:<row> (apart from skin: / makeup: / clothes rows)."""
    g = G(); g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"}); g.call("cc", K_STR, "Concat_StrStr", inp={"A": "pose:", "B": "@n2s.ReturnValue"})
    g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@cc.ReturnValue"}); g.link("s2n.ReturnValue", "return.key")
    return fn("Pose Key", [param("row", "name")], [param("key", "name")], graph=g, pure=True)


def f_is_pose_favorite():
    g = G(); g.n("k", "call_self", function="Pose Key", inp={"row": "@entry.name"}); g.n("f", "call_self", function="Is Favorite", inp={"name": "@k.key"}); g.link("f.yes", "return.yes")
    return fn("Is Pose Favorite", [param("name", "name")], [param("yes", "bool")], graph=g, pure=True)


def f_is_pose_hidden():
    g = G(); g.n("k", "call_self", function="Pose Key", inp={"row": "@entry.name"}); g.n("h", "call_self", function="Is Item Hidden", inp={"name": "@k.key"}); g.link("h.yes", "return.yes")
    return fn("Is Pose Hidden", [param("name", "name")], [param("yes", "bool")], graph=g, pure=True)


def f_pose_matches():
    """Poses search (PoseSearchText, case-insensitive): empty, or contained in the title (shown), the row name or the mod caption (shown + DLC caption)."""
    g = G(); g.get("gst", "PoseSearchText"); g.call("em", K_STR, "IsEmpty", inp={"InString": "@gst.PoseSearchText"}); g.call("ls", K_STR, "ToLower", inp={"SourceString": "@gst.PoseSearchText"})
    g.call("rs", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"})
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@entry.row"}); g.n("mcp", "call_self", function="Mod Caption", inp={"mod": "@imd.mod"})
    g.get("gmc", "ModCaption"); g.call("mdf", K_MAP, "Map_Find", inp={"TargetMap": "@gmc.ModCaption", "Key": "@imd.mod"}); g.call("mds", K_TXT, "Conv_TextToString", inp={"InText": "@mdf.Value"})
    prev = "@em.ReturnValue"
    for i, src in enumerate(["@entry.shown", "@rs.ReturnValue", "@mcp.s", "@mds.ReturnValue"]):
        g.call("lo%d" % i, K_STR, "ToLower", inp={"SourceString": src})
        g.call("hit%d" % i, K_STR, "Contains", inp={"SearchIn": "@lo%d.ReturnValue" % i, "Substring": "@ls.ReturnValue", "bUseCase": "false", "bSearchFromEnd": "false"})
        g.call("or%d" % i, K_MATH, "BooleanOR", inp={"A": prev, "B": "@hit%d.ReturnValue" % i}); prev = "@or%d.ReturnValue" % i
    g.link(prev[1:], "return.yes")
    return fn("Pose Matches", [param("row", "name"), param("shown", "string")], [param("yes", "bool")], graph=g, pure=True)


def f_pose_row_shown():
    """Filters of the poses page without the sidebar entry: search (Pose Matches on the title) and chip (PoseGroup: None =
    not hidden; Hidden = hidden only; Vanilla = no mod and not hidden; else its mod alias and not hidden). Pose Row Passes
    adds the sidebar entry to it; the counts in the sidebar need the answer without it, or every entry would count its own."""
    g = G(); g.n("pt", "call_self", function="Pose Name", inp={"row": "@entry.row"})
    g.n("pm", "call_self", function="Pose Matches", inp={"row": "@entry.row", "shown": "@pt.s"})
    g.n("k", "call_self", function="Pose Key", inp={"row": "@entry.row"}); g.n("hid", "call_self", function="Is Item Hidden", inp={"name": "@k.key"})
    g.get("gg", "PoseGroup"); g.call("isN", K_MATH, "EqualEqual_NameName", inp={"A": "@gg.PoseGroup", "B": "None"}); g.call("isH", K_MATH, "EqualEqual_NameName", inp={"A": "@gg.PoseGroup", "B": "Hidden"})
    g.call("isV", K_MATH, "EqualEqual_NameName", inp={"A": "@gg.PoseGroup", "B": "Vanilla"}); g.n("imd", "call_self", function="Item Mod", inp={"row": "@entry.row"})
    g.call("nf", K_MATH, "Not_PreBool", inp={"A": "@imd.found"}); g.call("van", K_MATH, "BooleanAND", inp={"A": "@isV.ReturnValue", "B": "@nf.ReturnValue"})
    g.n("mal", "call_self", function="Mod Alias", inp={"mod": "@imd.mod"}); g.call("eqm", K_MATH, "EqualEqual_NameName", inp={"A": "@mal.alias", "B": "@gg.PoseGroup"}); g.call("mod", K_MATH, "BooleanAND", inp={"A": "@eqm.ReturnValue", "B": "@imd.found"})
    g.call("o1", K_MATH, "BooleanOR", inp={"A": "@isN.ReturnValue", "B": "@van.ReturnValue"}); g.call("o2", K_MATH, "BooleanOR", inp={"A": "@o1.ReturnValue", "B": "@mod.ReturnValue"})
    g.call("nh", K_MATH, "Not_PreBool", inp={"A": "@hid.yes"}); g.call("vis", K_MATH, "BooleanAND", inp={"A": "@o2.ReturnValue", "B": "@nh.ReturnValue"})
    g.call("hh", K_MATH, "BooleanAND", inp={"A": "@isH.ReturnValue", "B": "@hid.yes"}); g.call("chip", K_MATH, "BooleanOR", inp={"A": "@vis.ReturnValue", "B": "@hh.ReturnValue"})
    g.call("a0", K_MATH, "BooleanAND", inp={"A": "@pm.yes", "B": "@chip.ReturnValue"})
    g.set("st", "TmpBool", inp={"TmpBool": "@a0.ReturnValue"}); g.get("gt", "TmpBool"); g.link("gt.TmpBool", "return.yes")
    g.chain("entry", "pt", "st", "return")
    return fn("Pose Row Shown", [param("row", "name")], [param("yes", "bool")], graph=g)


def f_pose_row_passes():
    """Filters of the poses page for one row: Pose Row Shown (search + chip) and the selected sidebar entry."""
    g = G(); g.n("sh", "call_self", function="Pose Row Shown", inp={"row": "@entry.row"})
    g.n("pk", "call_self", function="Pose Kind", inp={"row": "@entry.row"}); g.n("mv", "call_self", function="Is Pose Moving", inp={"row": "@entry.row"})
    g.get("gcat", "PoseCat"); g.call("cAll", K_MATH, "EqualEqual_NameName", inp={"A": "@gcat.PoseCat", "B": "None"})
    g.call("cMove", K_MATH, "EqualEqual_NameName", inp={"A": "@gcat.PoseCat", "B": "Move"}); g.call("cmok", K_MATH, "BooleanAND", inp={"A": "@cMove.ReturnValue", "B": "@mv.yes"})
    g.call("cUns", K_MATH, "EqualEqual_NameName", inp={"A": "@gcat.PoseCat", "B": "Unsorted"}); g.call("nfk", K_MATH, "Not_PreBool", inp={"A": "@pk.found"}); g.call("cuok", K_MATH, "BooleanAND", inp={"A": "@cUns.ReturnValue", "B": "@nfk.ReturnValue"})
    g.call("ceq", K_MATH, "EqualEqual_NameName", inp={"A": "@pk.kind", "B": "@gcat.PoseCat"}); g.call("ckok", K_MATH, "BooleanAND", inp={"A": "@ceq.ReturnValue", "B": "@pk.found"})
    g.get("gsec", "PoseSection"); g.call("sf", K_MAP, "Map_Find", inp={"TargetMap": "@gsec.PoseSection", "Key": "@entry.row"})
    g.call("seq", K_MATH, "EqualEqual_NameName", inp={"A": "@sf.Value", "B": "@gcat.PoseCat"}); g.call("csok", K_MATH, "BooleanAND", inp={"A": "@sf.ReturnValue", "B": "@seq.ReturnValue"})
    g.call("co1", K_MATH, "BooleanOR", inp={"A": "@cAll.ReturnValue", "B": "@cmok.ReturnValue"}); g.call("co2", K_MATH, "BooleanOR", inp={"A": "@co1.ReturnValue", "B": "@cuok.ReturnValue"})
    g.call("co3", K_MATH, "BooleanOR", inp={"A": "@co2.ReturnValue", "B": "@ckok.ReturnValue"}); g.call("ccat", K_MATH, "BooleanOR", inp={"A": "@co3.ReturnValue", "B": "@csok.ReturnValue"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@sh.yes", "B": "@ccat.ReturnValue"})
    g.set("st", "TmpBool", inp={"TmpBool": "@a1.ReturnValue"}); g.get("gt", "TmpBool"); g.link("gt.TmpBool", "return.yes")
    g.chain("entry", "sh", "st", "return")
    return fn("Pose Row Passes", [param("row", "name")], [param("yes", "bool")], graph=g)


def f_pose_groups():
    """Chips of the pose rows: Vanilla / mod alias per row (unique, order of first occurrence), "Hidden" last if a row is hidden."""
    g = G(); g.get("gn0", "TmpNames4"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gn0.TmpNames4"}); g.set("hf0", "TmpFound", inp={"TmpFound": "false"})
    g.get("gr", "PoseRows"); g.foreach("fe", "@gr.PoseRows")
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@fe.Array Element"}); g.n("mal", "call_self", function="Mod Alias", inp={"mod": "@imd.mod"})
    g.call("ms", K_STR, "Conv_NameToString", inp={"InName": "@mal.alias"}); g.call("sel", K_MATH, "SelectString", inp={"A": "@ms.ReturnValue", "B": "Vanilla", "bPickA": "@imd.found"}); g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@sel.ReturnValue"})
    g.get("gn1", "TmpNames4"); g.call("add", K_ARR, "Array_AddUnique", inp={"TargetArray": "@gn1.TmpNames4", "NewItem": "@s2n.ReturnValue"})
    g.n("ih", "call_self", function="Is Pose Hidden", inp={"name": "@fe.Array Element"}); g.branch("bih", "@ih.yes"); g.set("hf1", "TmpFound", inp={"TmpFound": "true"})
    g.get("ghf", "TmpFound"); g.branch("bhf", "@ghf.TmpFound"); g.get("gn3", "TmpNames4"); g.call("addh", K_ARR, "Array_Add", inp={"TargetArray": "@gn3.TmpNames4", "NewItem": g.lit_name("lh", "Hidden")})
    g.get("gn2", "TmpNames4"); g.link("gn2.TmpNames4", "return.groups")
    g.chain("entry", "clr", "hf0", "fe"); g.chain("fe", "add", "bih", "hf1"); g.chain("fe:Completed", "bhf", "addh", "return"); g.chain("bhf:else", "return")
    return fn("Pose Groups", outputs=[param("groups", "name", "array")], graph=g)


def f_rebuild_pose_chips():
    """Chip row of the poses page: All, "..." (collapse), one chip per Pose Groups entry (Look Chip Caption); hidden with one group only."""
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Pose SubTabs", inp={"self": "@gp.Panel"})
    g.n("col", "call_self", function="Collect Pose Rows"); g.n("gr", "call_self", function="Pose Groups")
    g.n("srt", "call_self", function="Sort Chips", inp={"groups": "@gr.groups", "look": "true"})   # mods alphabetically, Vanilla first, Hidden last
    g.set("sgr", "TmpNames3", inp={"TmpNames3": "@srt.sorted"}); g.get("ggr", "TmpNames3"); g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@ggr.TmpNames3"})
    g.call("gt1", K_MATH, "Greater_IntInt", inp={"A": "@len.ReturnValue", "B": "1"}); g.get("gpv", "Panel"); g.call("vis", W_PANEL, "Set Pose Chips Visible", inp={"self": "@gpv.Panel", "visible": "@gt1.ReturnValue"}); g.branch("b", "@gt1.ReturnValue")
    aw = create_widget(g, "ca", W_SUB); set_manager(g, "sma", W_SUB, aw)
    g.get("gcg", "PoseGroup"); g.call("selA", K_MATH, "EqualEqual_NameName", inp={"A": "@gcg.PoseGroup", "B": "None"})
    g.call("ia", W_SUB, "Init", inp={"self": aw, "group": "None", "caption": tt(g, "ta", "Chip_All"), "selected": "@selA.ReturnValue"})
    g.get("gp2", "Panel"); g.call("aa", W_PANEL, "Add Pose SubTab", inp={"self": "@gp2.Panel", "widget": aw})
    mw = create_widget(g, "cm", W_SUB); set_manager(g, "smm", W_SUB, mw); g.get("gcol", "PoseChipsCollapsed")
    g.call("im", W_SUB, "Init", inp={"self": mw, "group": "AltUI_More", "caption": tt(g, "tm", "Chip_More"), "selected": "@gcol.PoseChipsCollapsed"})
    g.get("gpm", "Panel"); g.call("am", W_PANEL, "Add Pose SubTab", inp={"self": "@gpm.Panel", "widget": mw})
    g.get("ggr2", "TmpNames3"); g.foreach("fe", "@ggr2.TmpNames3")
    g.get("gcg2", "PoseGroup"); g.call("selG", K_MATH, "EqualEqual_NameName", inp={"A": "@gcg2.PoseGroup", "B": "@fe.Array Element"})
    g.get("gcol2", "PoseChipsCollapsed"); g.call("ncol", K_MATH, "Not_PreBool", inp={"A": "@gcol2.PoseChipsCollapsed"})
    g.call("show", K_MATH, "BooleanOR", inp={"A": "@ncol.ReturnValue", "B": "@selG.ReturnValue"}); g.branch("bs", "@show.ReturnValue")
    sw = create_widget(g, "cs", W_SUB); set_manager(g, "sms", W_SUB, sw)
    g.get("gcol3", "PoseChipsCollapsed"); g.call("fullc", K_MATH, "BooleanAND", inp={"A": "@gcol3.PoseChipsCollapsed", "B": "@selG.ReturnValue"})
    g.n("cap", "call_self", function="Look Chip Caption", inp={"group": "@fe.Array Element", "full": "@fullc.ReturnValue"})
    g.call("is", W_SUB, "Init", inp={"self": sw, "group": "@fe.Array Element", "caption": "@cap.caption", "selected": "@selG.ReturnValue"})
    g.get("gp3", "Panel"); g.call("as", W_PANEL, "Add Pose SubTab", inp={"self": "@gp3.Panel", "widget": sw})
    g.chain("entry", "cl", "col", "gr", "srt", "sgr", "vis", "b", "ca_cr", "sma", "ia", "aa", "cm_cr", "smm", "im", "am", "fe"); g.chain("fe", "bs", "cs_cr", "sms", "cap", "is", "as")
    return fn("Rebuild Pose Chips", graph=g)


POSE_CATS = [("Stand", "Lbl_PoseStand"), ("Sit", "Lbl_PoseSit"), ("Lie", "Lbl_PoseLie"), ("Move", "Lbl_PoseMove"), ("Unsorted", "Lbl_PoseUnsorted")]


def f_start_pose_scan():
    """Measure every pose that has no category yet: the queue is walked in Scan Tick, each row goes through Pose Clicked."""
    g = G(); g.get("gs0", "ScanRows"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gs0.ScanRows"})
    g.n("col", "call_self", function="Collect Pose Rows"); g.get("gr", "PoseRows"); g.foreach("fe", "@gr.PoseRows")
    g.n("pk", "call_self", function="Pose Kind", inp={"row": "@fe.Array Element"}); g.call("nf", K_MATH, "Not_PreBool", inp={"A": "@pk.found"}); g.branch("b", "@nf.ReturnValue")
    g.get("gs1", "ScanRows"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gs1.ScanRows", "NewItem": "@fe.Array Element"})
    g.set("si", "ScanIndex", inp={"ScanIndex": "0"}); g.set("ss", "Scanning", inp={"Scanning": "true"})
    g.n("rl", "call_self", function="Rebuild Pose Links")
    g.chain("entry", "clr", "col", "fe"); g.chain("fe", "b", "add"); g.chain("fe:Completed", "si", "ss", "rl")
    return fn("Start Pose Scan", graph=g)


def f_stop_pose_scan():
    g = G(); g.set("ss", "Scanning", inp={"Scanning": "false"}); g.get("gs", "ScanRows"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gs.ScanRows"})
    g.n("sp", "call_self", function="Stop Pose"); g.n("rl", "call_self", function="Rebuild Pose Links"); g.n("rc", "call_self", function="Rebuild Pose Cats"); g.n("rp", "call_self", function="Rebuild Poses")
    g.chain("entry", "ss", "clr", "sp", "rl", "rc", "rp")
    return fn("Stop Pose Scan", graph=g)


def f_scan_tick():
    """One pose at a time: while a measurement runs (MeasureRow set) nothing happens, and after each pose SCAN_GAP seconds pass before
    the next one starts (a timed-out measurement must not let the run race through the table)."""
    g = G(); g.get("gsc", "Scanning"); g.branch("bs", "@gsc.Scanning")
    g.get("gw", "ScanWait"); g.call("wgt", K_MATH, "Greater_FloatFloat", inp={"A": "@gw.ScanWait", "B": "0.0"}); g.branch("bw", "@wgt.ReturnValue")
    g.get("gw2", "ScanWait"); g.call("wsub", K_MATH, "Subtract_FloatFloat", inp={"A": "@gw2.ScanWait", "B": "@entry.dt"}); g.set("sw", "ScanWait", inp={"ScanWait": "@wsub.ReturnValue"})
    g.get("gmr", "MeasureRow"); g.call("busy", K_MATH, "NotEqual_NameName", inp={"A": "@gmr.MeasureRow", "B": "None"}); g.branch("bb", "@busy.ReturnValue")
    g.get("gi", "ScanIndex"); g.get("gr", "ScanRows"); g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@gr.ScanRows"})
    g.call("done", K_MATH, "GreaterEqual_IntInt", inp={"A": "@gi.ScanIndex", "B": "@len.ReturnValue"}); g.branch("bd", "@done.ReturnValue")
    g.n("sps", "call_self", function="Stop Pose Scan")
    g.get("gr2", "ScanRows"); g.get("gi2", "ScanIndex"); g.call("row", K_ARR, "Array_Get", inp={"TargetArray": "@gr2.ScanRows", "Index": "@gi2.ScanIndex"})
    g.get("gi3", "ScanIndex"); g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gi3.ScanIndex", "B": "1"}); g.set("sinc", "ScanIndex", inp={"ScanIndex": "@inc.ReturnValue"})
    g.n("pc", "call_self", function="Pose Clicked", inp={"name": "@row.Item"}); g.set("sgap", "ScanWait", inp={"ScanWait": str(SCAN_GAP)}); g.n("rl", "call_self", function="Rebuild Pose Links")
    g.get("gi4", "ScanIndex"); g.call("mod", K_MATH, "Percent_IntInt", inp={"A": "@gi4.ScanIndex", "B": str(SCAN_GC)}); g.call("gc0", K_MATH, "EqualEqual_IntInt", inp={"A": "@mod.ReturnValue", "B": "0"}); g.branch("bgc", "@gc0.ReturnValue")
    g.call("cg", K_SYS, "CollectGarbage"); g.n("glog", "call_self", function="Log Line", inp={"text": "gc"})   # every montage the run played stays loaded otherwise
    g.chain("entry", "bs", "bw", "sw"); g.chain("bw:else", "bb"); g.chain("bb:else", "bd", "sps"); g.chain("bd:else", "sinc", "pc", "sgap", "rl", "bgc", "cg", "glog")
    return fn("Scan Tick", [param("dt", "float")], graph=g)


def f_bump_pose_count():
    """One more row for a sidebar entry: always in PoseCounts, and in PoseCountsF when the search and the chip keep it."""
    g = G()
    g.get("gc", "PoseCounts"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gc.PoseCounts", "Key": "@entry.key"})
    g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@f.Value", "B": "1"})
    g.get("gc2", "PoseCounts"); g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gc2.PoseCounts", "Key": "@entry.key", "Value": "@inc.ReturnValue"})
    g.branch("b", "@entry.shown")
    g.get("gf", "PoseCountsF"); g.call("f2", K_MAP, "Map_Find", inp={"TargetMap": "@gf.PoseCountsF", "Key": "@entry.key"})
    g.call("inc2", K_MATH, "Add_IntInt", inp={"A": "@f2.Value", "B": "1"})
    g.get("gf2", "PoseCountsF"); g.call("add2", K_MAP, "Map_Add", inp={"TargetMap": "@gf2.PoseCountsF", "Key": "@entry.key", "Value": "@inc2.ReturnValue"})
    g.chain("entry", "add", "b", "add2")
    return fn("Bump Pose Count", [param("key", "name"), param("shown", "bool")], graph=g)


def f_count_pose_cats():
    """Counts for the whole sidebar in one pass over the rows: totals and, per entry, how many of them the search and
    the chip leave. Asking per entry instead ran the filter once per entry and row - with a few hundred poses and a
    dozen entries that was felt on every keystroke."""
    g = G()
    g.get("gc0", "PoseCounts"); g.call("cc", K_MAP, "Map_Clear", inp={"TargetMap": "@gc0.PoseCounts"})
    g.get("gf0", "PoseCountsF"); g.call("cf", K_MAP, "Map_Clear", inp={"TargetMap": "@gf0.PoseCountsF"})
    g.n("col", "call_self", function="Collect Pose Rows"); g.get("gr", "PoseRows"); g.foreach("fe", "@gr.PoseRows")
    g.n("sh", "call_self", function="Pose Row Shown", inp={"row": "@fe.Array Element"})
    g.n("addAll", "call_self", function="Bump Pose Count", inp={"key": "All", "shown": "@sh.yes"})
    g.n("mv", "call_self", function="Is Pose Moving", inp={"row": "@fe.Array Element"}); g.branch("bm", "@mv.yes")
    g.n("addMove", "call_self", function="Bump Pose Count", inp={"key": "Move", "shown": "@sh.yes"})
    g.n("pk", "call_self", function="Pose Kind", inp={"row": "@fe.Array Element"}); g.branch("bk", "@pk.found")
    g.n("addKind", "call_self", function="Bump Pose Count", inp={"key": "@pk.kind", "shown": "@sh.yes"})
    g.n("addUns", "call_self", function="Bump Pose Count", inp={"key": "Unsorted", "shown": "@sh.yes"})
    g.get("gsec", "PoseSection"); g.call("sf", K_MAP, "Map_Find", inp={"TargetMap": "@gsec.PoseSection", "Key": "@fe.Array Element"}); g.branch("bs", "@sf.ReturnValue")
    g.n("addSec", "call_self", function="Bump Pose Count", inp={"key": "@sf.Value", "shown": "@sh.yes"})
    g.chain("entry", "cc", "cf", "col", "fe")
    g.chain("fe", "sh", "addAll", "bm", "addMove", "bk", "addKind", "bs", "addSec")
    g.chain("bm:else", "bk"); g.chain("bk:else", "addUns", "bs")
    return fn("Count Pose Cats", graph=g)


def f_pose_cat_count():
    """Count of one sidebar entry - read from the pass in Count Pose Cats, not counted again."""
    g = G()
    g.get("gc", "PoseCounts"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gc.PoseCounts", "Key": "@entry.cat"})
    g.get("gf", "PoseCountsF"); g.call("ff", K_MAP, "Map_Find", inp={"TargetMap": "@gf.PoseCountsF", "Key": "@entry.cat"})
    g.call("sel", K_MATH, "SelectInt", inp={"A": "@ff.Value", "B": "@f.Value", "bPickA": "@entry.filtered"})
    g.link("sel.ReturnValue", "return.n"); g.chain("entry", "return")
    return fn("Pose Cat Count", [param("cat", "name"), param("filtered", "bool")], [param("n", "int")], graph=g)


def f_rebuild_pose_cats():
    """Sidebar of the poses page: "All" always, every other entry only when it has rows (a fresh install shows just "All")."""
    g = G(); g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Pose Cats", inp={"self": "@gp.Panel"})
    g.n("cnt", "call_self", function="Count Pose Cats")
    # "total (hits)" like the clothes and appearance pages: -1 hides the parenthesis, so it only shows with a filter on
    g.get("gpst", "PoseSearchText"); g.call("sne", K_STR, "IsEmpty", inp={"InString": "@gpst.PoseSearchText"})
    g.get("gpg", "PoseGroup"); g.call("gno", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.PoseGroup", "B": "None"})
    g.call("noact", K_MATH, "BooleanAND", inp={"A": "@sne.ReturnValue", "B": "@gno.ReturnValue"})
    g.n("cntA", "call_self", function="Pose Cat Count", inp={"cat": "All", "filtered": "false"})
    g.n("cntAf", "call_self", function="Pose Cat Count", inp={"cat": "All", "filtered": "true"})
    g.call("fselA", K_MATH, "SelectInt", inp={"A": "-1", "B": "@cntAf.n", "bPickA": "@noact.ReturnValue"})
    g.get("gpcA", "PoseCat"); g.call("selA", K_MATH, "EqualEqual_NameName", inp={"A": "@gpcA.PoseCat", "B": "None"})
    aw = create_widget(g, "ca", W_TAB); set_manager(g, "sma", W_TAB, aw)
    g.call("ia", W_TAB, "Init", inp={"self": aw, "slot": "None", "caption": tt(g, "capA", "Chip_All"), "count": "@cntA.n", "worn icon": "None",
                                     "selected": "@selA.ReturnValue", "has items": "true", "filtered": "@fselA.ReturnValue", "indent": "false"})
    g.get("gp2", "Panel"); g.call("aa", W_PANEL, "Add Pose Cat", inp={"self": "@gp2.Panel", "widget": aw})
    g.chain("entry", "cl", "cnt", "cntA", "cntAf", "ca_cr", "sma", "ia", "aa"); sources = ["aa"]
    for i, (cat, key) in enumerate(POSE_CATS):
        g.n("cnt%d" % i, "call_self", function="Pose Cat Count", inp={"cat": cat, "filtered": "false"})
        g.n("cntf%d" % i, "call_self", function="Pose Cat Count", inp={"cat": cat, "filtered": "true"})
        g.call("fsel%d" % i, K_MATH, "SelectInt", inp={"A": "-1", "B": "@cntf%d.n" % i, "bPickA": "@noact.ReturnValue"})
        g.call("has%d" % i, K_MATH, "Greater_IntInt", inp={"A": "@cnt%d.n" % i, "B": "0"}); g.branch("b%d" % i, "@has%d.ReturnValue" % i)
        g.get("gpc%d" % i, "PoseCat"); g.call("sel%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@gpc%d.PoseCat" % i, "B": cat})
        tw = create_widget(g, "ct%d" % i, W_TAB); set_manager(g, "sm%d" % i, W_TAB, tw)
        g.call("ti%d" % i, W_TAB, "Init", inp={"self": tw, "slot": cat, "caption": tt(g, "cap%d" % i, key), "count": "@cnt%d.n" % i, "worn icon": "None",
                                               "selected": "@sel%d.ReturnValue" % i, "has items": "true", "filtered": "@fsel%d.ReturnValue" % i, "indent": "false"})
        g.get("gpp%d" % i, "Panel"); g.call("at%d" % i, W_PANEL, "Add Pose Cat", inp={"self": "@gpp%d.Panel" % i, "widget": tw})
        for src in sources: g.chain(src, "cnt%d" % i)
        g.chain("cnt%d" % i, "cntf%d" % i, "b%d" % i, "ct%d_cr" % i, "sm%d" % i, "ti%d" % i, "at%d" % i)
        sources = ["at%d" % i, "b%d:else" % i]
    # chapters of the pose mods (marker rows), under a header like the sections of the Manage page
    g.get("gsl", "PoseSections"); g.call("slen", K_ARR, "Array_Length", inp={"TargetArray": "@gsl.PoseSections"})
    g.call("any", K_MATH, "Greater_IntInt", inp={"A": "@slen.ReturnValue", "B": "0"}); g.branch("bany", "@any.ReturnValue")
    hw = create_widget(g, "chh", W_HEAD); set_manager(g, "shm", W_HEAD, hw)
    g.call("hi", W_HEAD, "Init", inp={"self": hw, "caption": tt(g, "hcap", "Lbl_PoseChapters")})
    g.get("gph", "Panel"); g.call("ah", W_PANEL, "Add Pose Cat", inp={"self": "@gph.Panel", "widget": hw})
    g.get("gsl2", "PoseSections"); g.foreach("fs", "@gsl2.PoseSections")
    g.n("scnt", "call_self", function="Pose Section Count", inp={"row": "@fs.Array Element", "filtered": "false"})
    g.n("scntf", "call_self", function="Pose Section Count", inp={"row": "@fs.Array Element", "filtered": "true"})
    g.call("sfsel", K_MATH, "SelectInt", inp={"A": "-1", "B": "@scntf.n", "bPickA": "@noact.ReturnValue"})
    g.call("shas", K_MATH, "Greater_IntInt", inp={"A": "@scnt.n", "B": "0"}); g.branch("bsh", "@shas.ReturnValue")
    g.n("scap", "call_self", function="Pose Section Caption", inp={"row": "@fs.Array Element"})
    g.get("gpcs", "PoseCat"); g.call("ssel", K_MATH, "EqualEqual_NameName", inp={"A": "@gpcs.PoseCat", "B": "@fs.Array Element"})
    sw = create_widget(g, "cts", W_TAB); set_manager(g, "sms", W_TAB, sw)
    g.call("tis", W_TAB, "Init", inp={"self": sw, "slot": "@fs.Array Element", "caption": "@scap.caption", "count": "@scnt.n", "worn icon": "None",
                                      "selected": "@ssel.ReturnValue", "has items": "true", "filtered": "@sfsel.ReturnValue", "indent": "false"})
    g.get("gpps", "Panel"); g.call("ats", W_PANEL, "Add Pose Cat", inp={"self": "@gpps.Panel", "widget": sw})
    for src in sources: g.chain(src, "bany")
    g.chain("bany", "chh_cr", "shm", "hi", "ah", "fs"); g.chain("fs", "scnt", "scntf", "bsh", "scap", "cts_cr", "sms", "tis", "ats")
    return fn("Rebuild Pose Cats", graph=g)


def f_select_pose_cat():
    g = G(); g.set("s", "PoseCat", inp={"PoseCat": "@entry.name"})
    g.n("rc", "call_self", function="Rebuild Pose Cats"); g.n("rk", "call_self", function="Rebuild Pose Chips"); g.n("rp", "call_self", function="Rebuild Poses")
    g.chain("entry", "s", "rc", "rk", "rp")
    return fn("Select Pose Cat", [param("name", "name")], graph=g)


def f_select_pose_group():
    """Chip click on the poses page: "..." folds the row (only the selected chip stays), else the chip filters the tiles."""
    g = G(); g.call("ism", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "AltUI_More"}); g.branch("bm", "@ism.ReturnValue")
    g.get("gcol", "PoseChipsCollapsed"); g.call("ncol", K_MATH, "Not_PreBool", inp={"A": "@gcol.PoseChipsCollapsed"}); g.set("scol", "PoseChipsCollapsed", inp={"PoseChipsCollapsed": "@ncol.ReturnValue"})
    g.n("svm", "call_self", function="Save Settings"); g.n("rtm", "call_self", function="Rebuild Pose Chips")
    g.set("s", "PoseGroup", inp={"PoseGroup": "@entry.name"}); g.n("rt", "call_self", function="Rebuild Pose Chips"); g.n("rl", "call_self", function="Rebuild Poses")
    g.n("rc2", "call_self", function="Rebuild Pose Cats")   # same as the search: the chip changes what the sidebar counts
    g.chain("entry", "bm", "scol", "svm", "rtm"); g.chain("bm:else", "s", "rc2", "rt", "rl")
    return fn("Select Pose Group", [param("name", "name")], graph=g)


def pose_tile(g, p, row_pin, add_fn, fav_pin):
    """Tile of one pose row: title as display name, T_Pose icon, highlighted when it is the next / running action; returns the exec chain."""
    g.n(p + "pt", "call_self", function="Pose Name", inp={"row": row_pin})
    g.make(p + "mi", S_ITEM, Name=row_pin, DisplayName="@%spt.s" % p, Icon=T_POSE)
    g.get(p + "gpl", "Player"); g.get(p + "gnx", "Action Animation Name Next", cls=P_JODI); g.link(p + "gpl.Player", p + "gnx.self")
    g.call(p + "sel", K_MATH, "EqualEqual_NameName", inp={"A": "@%sgnx.Action Animation Name Next" % p, "B": row_pin})
    return [p + "pt"] + look_tile(g, p + "t", "@%smi.S_ClothesItem" % p, "@%ssel.ReturnValue" % p, "true", add_fn, tt(g, p + "cap", "Tab_Poses"), kind="pose", fav_pin=fav_pin)


def f_rebuild_poses():
    """Pass 1 favourites block (passes the filters and is a favourite), pass 2 every row that passes the filters."""
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Pose", inp={"self": "@gp.Panel"}); g.get("gpf", "Panel"); g.call("clf", W_PANEL, "Clear Pose Fav", inp={"self": "@gpf.Panel"})
    g.n("col", "call_self", function="Collect Pose Rows"); g.set("nf", "TmpIdx", inp={"TmpIdx": "0"})
    g.get("gr1", "PoseRows"); g.foreach("ff", "@gr1.PoseRows")
    g.n("pf", "call_self", function="Pose Row Passes", inp={"row": "@ff.Array Element"}); g.n("ffv", "call_self", function="Is Pose Favorite", inp={"name": "@ff.Array Element"})
    g.call("fok", K_MATH, "BooleanAND", inp={"A": "@pf.yes", "B": "@ffv.yes"}); g.branch("bf", "@fok.ReturnValue")
    t1 = pose_tile(g, "f", "@ff.Array Element", "Add Pose Fav", "true")
    g.get("gn", "TmpIdx"); g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gn.TmpIdx", "B": "1"}); g.set("sn", "TmpIdx", inp={"TmpIdx": "@inc.ReturnValue"})
    g.get("gn2", "TmpIdx"); g.call("gt0", K_MATH, "Greater_IntInt", inp={"A": "@gn2.TmpIdx", "B": "0"}); g.get("gp5", "Panel"); g.call("sfv", W_PANEL, "Set Pose Fav Visible", inp={"self": "@gp5.Panel", "visible": "@gt0.ReturnValue"})
    t0 = pose_tile(g, "d", g.lit_name("dnone", "None"), "Add Pose", "false")   # default tile: leaves the pose without closing the panel
    g.get("gr2", "PoseRows"); g.foreach("fe", "@gr2.PoseRows")
    g.n("pe", "call_self", function="Pose Row Passes", inp={"row": "@fe.Array Element"}); g.branch("be", "@pe.yes")
    g.n("efv", "call_self", function="Is Pose Favorite", inp={"name": "@fe.Array Element"})
    t2 = pose_tile(g, "a", "@fe.Array Element", "Add Pose", "@efv.yes")
    g.chain("entry", "cl", "clf", "col", "nf", "ff"); g.chain("ff", "pf", "bf", "sn", *t1)
    g.chain("ff:Completed", "sfv", *t0, "fe"); g.chain("fe", "pe", "be", *t2)
    return fn("Rebuild Poses", graph=g)


def f_pose_actors():
    """Actors of one pose mod near Jodi: class path starts with /Game/Mod/<mod>/ and the actor is within POSE_PROP_RADIUS.
    An empty mod name yields an empty list (vanilla poses spawn nothing)."""
    g = G(); g.get("ga0", "TmpActors"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@ga0.TmpActors"})
    g.call("isn", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.mod", "B": "None"}); g.call("nn", K_MATH, "Not_PreBool", inp={"A": "@isn.ReturnValue"}); g.branch("bm", "@nn.ReturnValue")
    g.call("m2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.mod"})
    g.call("pre0", K_STR, "Concat_StrStr", inp={"A": "/Game/Mod/", "B": "@m2s.ReturnValue"}); g.call("pre", K_STR, "Concat_StrStr", inp={"A": "@pre0.ReturnValue", "B": "/"})
    g.get("gpl", "Player"); g.call("ploc", E_ACTOR, "K2_GetActorLocation", inp={"self": "@gpl.Player"})
    g.call("all", K_GS, "GetAllActorsOfClass", inp={"ActorClass": E_ACTOR}); g.foreach("fe", "@all.OutActors")
    g.call("aloc", E_ACTOR, "K2_GetActorLocation", inp={"self": "@fe.Array Element"})
    g.call("dst", K_MATH, "Vector_Distance", inp={"V1": "@aloc.ReturnValue", "V2": "@ploc.ReturnValue"})
    g.call("near", K_MATH, "LessEqual_FloatFloat", inp={"A": "@dst.ReturnValue", "B": str(POSE_PROP_RADIUS)}); g.branch("bnear", "@near.ReturnValue")   # distance first: the path string is the expensive part
    g.call("cls", K_GS, "GetObjectClass", inp={"Object": "@fe.Array Element"})   # a class pin cannot feed GetPathName: the soft reference carries the path
    g.call("scr", K_SYS, "Conv_ClassToSoftClassReference", inp={"Class": "@cls.ReturnValue"}); g.call("pth", K_SYS, "Conv_SoftClassReferenceToString", inp={"SoftClassReference": "@scr.ReturnValue"})
    g.call("sw", K_STR, "StartsWith", inp={"SourceString": "@pth.ReturnValue", "InPrefix": "@pre.ReturnValue", "SearchCase": "IgnoreCase"}); g.branch("bok", "@sw.ReturnValue")
    g.get("ga1", "TmpActors"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@ga1.TmpActors", "NewItem": "@fe.Array Element"})
    g.get("ga2", "TmpActors"); g.link("ga2.TmpActors", "return.actors")
    g.chain("entry", "clr", "bm", "all", "fe"); g.chain("fe", "bnear", "bok", "add"); g.chain("fe:Completed", "return"); g.chain("bm:else", "return")   # K2_GetActorLocation is pure
    return fn("Pose Actors", [param("mod", "name")], [param("actors", "object:" + E_ACTOR, "array")], graph=g)


def f_pose_kind():
    g = G(); g.get("gk", "PoseKind"); g.call("mf", K_MAP, "Map_Find", inp={"TargetMap": "@gk.PoseKind", "Key": "@entry.row"})
    g.link("mf.Value", "return.kind"); g.link("mf.ReturnValue", "return.found")
    return fn("Pose Kind", [param("row", "name")], [param("kind", "name"), param("found", "bool")], graph=g, pure=True)


def f_is_pose_moving():
    g = G(); g.get("gm", "PoseMoving"); g.call("mf", K_MAP, "Map_Find", inp={"TargetMap": "@gm.PoseMoving", "Key": "@entry.row"})
    g.call("a", K_MATH, "BooleanAND", inp={"A": "@mf.ReturnValue", "B": "@mf.Value"}); g.link("a.ReturnValue", "return.yes")
    return fn("Is Pose Moving", [param("row", "name")], [param("yes", "bool")], graph=g, pure=True)


def f_set_pose_kind():
    """Store a pose's category and refresh the sidebar. manual = set by hand in the context menu: a later measurement leaves it alone."""
    g = G(); g.get("gk", "PoseKind"); g.call("ak", K_MAP, "Map_Add", inp={"TargetMap": "@gk.PoseKind", "Key": "@entry.row", "Value": "@entry.kind"})
    g.get("gm", "PoseMoving"); g.call("am", K_MAP, "Map_Add", inp={"TargetMap": "@gm.PoseMoving", "Key": "@entry.row", "Value": "@entry.moving"})
    g.branch("bman", "@entry.manual")
    g.get("gmn", "PoseManual"); g.call("amn", K_MAP, "Map_Add", inp={"TargetMap": "@gmn.PoseManual", "Key": "@entry.row", "Value": g.lit_bool("lt", "true")})
    g.n("sv", "call_self", function="Save Settings"); g.n("rc", "call_self", function="Rebuild Pose Cats")
    g.chain("entry", "ak", "am", "bman", "amn", "sv"); g.chain("bman:else", "sv"); g.chain("sv", "rc")
    return fn("Set Pose Kind", [param("row", "name"), param("kind", "name"), param("moving", "bool"), param("manual", "bool")], graph=g)


def f_is_pose_manual():
    g = G(); g.get("gm", "PoseManual"); g.call("mf", K_MAP, "Map_Find", inp={"TargetMap": "@gm.PoseManual", "Key": "@entry.row"})
    g.call("a", K_MATH, "BooleanAND", inp={"A": "@mf.ReturnValue", "B": "@mf.Value"}); g.link("a.ReturnValue", "return.yes")
    return fn("Is Pose Manual", [param("row", "name")], [param("yes", "bool")], graph=g, pure=True)


def f_pelvis_height():
    """Pelvis position and its height over the mesh origin (= the floor Jodi stands on; heels move the origin with her)."""
    g = G(); g.get("gpl", "Player"); g.get("gm", "Mesh", cls=E_CHARACTER); g.link("gpl.Player", "gm.self")
    g.call("pel", E_SCENEC, "GetSocketLocation", inp={"self": "@gm.Mesh", "InSocketName": "pelvis"})
    g.call("org", E_SCENEC, "K2_GetComponentLocation", inp={"self": "@gm.Mesh"})
    g.call("bp", K_MATH, "BreakVector", inp={"InVec": "@pel.ReturnValue"}); g.call("bo", K_MATH, "BreakVector", inp={"InVec": "@org.ReturnValue"})
    g.call("h", K_MATH, "Subtract_FloatFloat", inp={"A": "@bp.Z", "B": "@bo.Z"})
    g.link("pel.ReturnValue", "return.pos"); g.link("h.ReturnValue", "return.height")
    return fn("Pelvis Height", outputs=[param("pos", "struct:/Script/CoreUObject.Vector"), param("height", "float")], graph=g)


def f_measure_tick():
    """Samples the pelvis every frame while the pose plays (MeasureRun counts only the playing time - the game needs a few frames until
    Action Animation Name Current is the clicked row). The height class comes from the average height, "in motion" from the travelled
    box over the whole window: two snapshots missed periodic motion, which is why dancing poses came out as standing."""
    g = G(); g.get("gmr", "MeasureRow"); g.call("isn", K_MATH, "EqualEqual_NameName", inp={"A": "@gmr.MeasureRow", "B": "None"})
    g.call("act", K_MATH, "Not_PreBool", inp={"A": "@isn.ReturnValue"}); g.branch("ba", "@act.ReturnValue")
    g.get("gt", "MeasureTime"); g.call("addt", K_MATH, "Add_FloatFloat", inp={"A": "@gt.MeasureTime", "B": "@entry.dt"}); g.set("st", "MeasureTime", inp={"MeasureTime": "@addt.ReturnValue"})
    g.get("gpl", "Player"); g.get("gcur", "Action Animation Name Current", cls=P_JODI); g.link("gpl.Player", "gcur.self")
    g.get("gmr2", "MeasureRow"); g.call("run", K_MATH, "EqualEqual_NameName", inp={"A": "@gcur.Action Animation Name Current", "B": "@gmr2.MeasureRow"}); g.branch("br", "@run.ReturnValue")
    g.get("gt2", "MeasureTime"); g.call("late", K_MATH, "Greater_FloatFloat", inp={"A": "@gt2.MeasureTime", "B": str(POSE_TIMEOUT)}); g.branch("bl", "@late.ReturnValue")
    g.set("cancel", "MeasureRow", inp={"MeasureRow": "None"})
    g.get("gr0", "MeasureRun"); g.call("addr", K_MATH, "Add_FloatFloat", inp={"A": "@gr0.MeasureRun", "B": "@entry.dt"}); g.set("sr", "MeasureRun", inp={"MeasureRun": "@addr.ReturnValue"})
    g.n("ph", "call_self", function="Pelvis Height")
    g.get("gr1", "MeasureRun"); g.call("t1", K_MATH, "GreaterEqual_FloatFloat", inp={"A": "@gr1.MeasureRun", "B": str(POSE_T1)}); g.branch("b1", "@t1.ReturnValue")   # settle first, then sample every frame
    # running box of the pelvis + height average
    g.get("gmn", "MeasureMin"); g.get("gmx", "MeasureMax"); g.get("gn", "MeasureN"); g.call("first", K_MATH, "EqualEqual_IntInt", inp={"A": "@gn.MeasureN", "B": "0"}); g.branch("bf", "@first.ReturnValue")
    g.set("sn0", "MeasureMin", inp={"MeasureMin": "@ph.pos"}); g.set("sx0", "MeasureMax", inp={"MeasureMax": "@ph.pos"})
    g.call("mn", K_MATH, "Vector_ComponentMin", inp={"A": "@gmn.MeasureMin", "B": "@ph.pos"}); g.set("sn1", "MeasureMin", inp={"MeasureMin": "@mn.ReturnValue"})
    g.call("mx", K_MATH, "Vector_ComponentMax", inp={"A": "@gmx.MeasureMax", "B": "@ph.pos"}); g.set("sx1", "MeasureMax", inp={"MeasureMax": "@mx.ReturnValue"})
    g.get("gs", "MeasureSum"); g.call("adds", K_MATH, "Add_FloatFloat", inp={"A": "@gs.MeasureSum", "B": "@ph.height"}); g.set("ss", "MeasureSum", inp={"MeasureSum": "@adds.ReturnValue"})
    g.get("gn2", "MeasureN"); g.call("incn", K_MATH, "Add_IntInt", inp={"A": "@gn2.MeasureN", "B": "1"}); g.set("sn2", "MeasureN", inp={"MeasureN": "@incn.ReturnValue"})
    g.get("gr2", "MeasureRun"); g.call("t2", K_MATH, "GreaterEqual_FloatFloat", inp={"A": "@gr2.MeasureRun", "B": str(POSE_T2)}); g.branch("b2", "@t2.ReturnValue")
    # done: average height -> class, box diagonal -> motion
    g.get("gs2", "MeasureSum"); g.get("gn3", "MeasureN"); g.call("nf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@gn3.MeasureN"})
    g.call("avg", K_MATH, "Divide_FloatFloat", inp={"A": "@gs2.MeasureSum", "B": "@nf.ReturnValue"})
    g.get("gmn2", "MeasureMin"); g.get("gmx2", "MeasureMax"); g.call("span", K_MATH, "Vector_Distance", inp={"V1": "@gmx2.MeasureMax", "V2": "@gmn2.MeasureMin"})
    g.call("mov", K_MATH, "Greater_FloatFloat", inp={"A": "@span.ReturnValue", "B": str(POSE_MOVE)})
    g.call("lie", K_MATH, "Less_FloatFloat", inp={"A": "@avg.ReturnValue", "B": str(POSE_H_LIE)}); g.call("sit", K_MATH, "Less_FloatFloat", inp={"A": "@avg.ReturnValue", "B": str(POSE_H_SIT)})
    g.call("k1", K_MATH, "SelectString", inp={"A": "Sit", "B": "Stand", "bPickA": "@sit.ReturnValue"}); g.call("k2", K_MATH, "SelectString", inp={"A": "Lie", "B": "@k1.ReturnValue", "bPickA": "@lie.ReturnValue"})
    g.call("k2n", K_STR, "Conv_StringToName", inp={"InString": "@k2.ReturnValue"})
    g.get("gmr3", "MeasureRow"); g.n("spk", "call_self", function="Set Pose Kind", inp={"row": "@gmr3.MeasureRow", "kind": "@k2n.ReturnValue", "moving": "@mov.ReturnValue", "manual": "false"})
    g.get("gmr4", "MeasureRow"); g.call("rs", K_STR, "Conv_NameToString", inp={"InName": "@gmr4.MeasureRow"}); g.call("hs", K_STR, "Conv_FloatToString", inp={"InFloat": "@avg.ReturnValue"})
    g.call("ms", K_STR, "Conv_FloatToString", inp={"InFloat": "@span.ReturnValue"})
    g.call("l1", K_STR, "Concat_StrStr", inp={"A": "pose ", "B": "@rs.ReturnValue"}); g.call("l2", K_STR, "Concat_StrStr", inp={"A": "@l1.ReturnValue", "B": " h="})
    g.call("l3", K_STR, "Concat_StrStr", inp={"A": "@l2.ReturnValue", "B": "@hs.ReturnValue"}); g.call("l4", K_STR, "Concat_StrStr", inp={"A": "@l3.ReturnValue", "B": " span="})
    g.call("l5", K_STR, "Concat_StrStr", inp={"A": "@l4.ReturnValue", "B": "@ms.ReturnValue"}); g.call("l6", K_STR, "Concat_StrStr", inp={"A": "@l5.ReturnValue", "B": " -> "})
    g.call("l7", K_STR, "Concat_StrStr", inp={"A": "@l6.ReturnValue", "B": "@k2.ReturnValue"}); g.n("log", "call_self", function="Log Line", inp={"text": "@l7.ReturnValue"})
    g.set("done", "MeasureRow", inp={"MeasureRow": "None"})
    g.chain("entry", "ba", "st", "br", "sr", "ph", "b1", "bf", "sn0", "sx0", "ss")
    g.chain("bf:else", "sn1", "sx1", "ss"); g.chain("ss", "sn2", "b2", "spk", "log", "done")
    g.chain("br:else", "bl", "cancel")
    return fn("Measure Tick", [param("dt", "float")], graph=g)


def f_pose_clicked():
    """Tile click: Jodi alive -> stop what is running (Update Action Animation only starts the next one once no montage plays any more,
    and with the panel open Jodi cannot walk out of a pose), then play the clicked one; clicking the running one just stops."""
    g = G(); g.get("gpl", "Player"); g.call("al", P_JODI, "Is Alive ?", inp={"self": "@gpl.Player"}); g.branch("b", "@al.yes")
    g.get("gpl2", "Player"); g.get("gnx", "Action Animation Name Next", cls=P_JODI); g.link("gpl2.Player", "gnx.self")
    g.call("eq", K_MATH, "EqualEqual_NameName", inp={"A": "@gnx.Action Animation Name Next", "B": "@entry.name"})
    g.call("isn", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "None"})   # the default tile only stops
    g.call("stp", K_MATH, "BooleanOR", inp={"A": "@eq.ReturnValue", "B": "@isn.ReturnValue"}); g.branch("bs", "@stp.ReturnValue")
    g.n("sp", "call_self", function="Stop Pose")
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@entry.name"})   # pure; a vanilla pose has no mod -> None
    g.set("spm", "PoseMod", inp={"PoseMod": "@imd.mod"})
    g.get("gpm", "PoseMod"); g.n("pa", "call_self", function="Pose Actors", inp={"mod": "@gpm.PoseMod"}); g.set("spk", "PoseKnown", inp={"PoseKnown": "@pa.actors"})
    g.n("pkn", "call_self", function="Pose Kind", inp={"row": "@entry.name"}); g.call("unm", K_MATH, "Not_PreBool", inp={"A": "@pkn.found"}); g.branch("bmeas", "@unm.ReturnValue")   # already categorised (measured or by hand) -> leave it alone
    g.set("smr", "MeasureRow", inp={"MeasureRow": "@entry.name"}); g.set("smt", "MeasureTime", inp={"MeasureTime": "0.0"}); g.set("smr2", "MeasureRun", inp={"MeasureRun": "0.0"}); g.set("smn", "MeasureN", inp={"MeasureN": "0"}); g.set("sms", "MeasureSum", inp={"MeasureSum": "0.0"})
    g.get("gpl4", "Player"); g.call("play", P_JODI, "Change Next Action Animation", inp={"self": "@gpl4.Player", "Next Action Name": "@entry.name"})
    g.n("rp", "call_self", function="Rebuild Poses")
    g.chain("entry", "b", "bs", "sp"); g.chain("bs:else", "sp", "spm", "pa", "spk", "bmeas", "smr", "smt", "smr2", "smn", "sms", "play"); g.chain("bmeas:else", "play"); g.chain("play", "rp")
    return fn("Pose Clicked", [param("name", "name")], graph=g)


def f_stop_pose():
    """End the running pose: clear the next action, stop the montages (the game itself only leaves a pose when Jodi moves) and destroy
    the props the pose spawned - every actor of the pose's mod near Jodi that was not there when the pose started."""
    g = G(); g.get("gpl", "Player"); g.call("stop", P_JODI, "Change Next Action Animation", inp={"self": "@gpl.Player", "Next Action Name": "None"})
    g.get("gpl2", "Player"); g.call("sa", P_JODI, "Stop Action Animation", inp={"self": "@gpl2.Player"})
    g.get("gpm", "PoseMod"); g.n("pa", "call_self", function="Pose Actors", inp={"mod": "@gpm.PoseMod"}); g.set("sta", "TmpActors2", inp={"TmpActors2": "@pa.actors"})
    g.get("gta", "TmpActors2"); g.foreach("fe", "@gta.TmpActors2")
    g.get("gpk", "PoseKnown"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gpk.PoseKnown", "ItemToFind": "@fe.Array Element"})
    g.call("new", K_MATH, "Not_PreBool", inp={"A": "@has.ReturnValue"}); g.branch("bn", "@new.ReturnValue")
    g.call("dst", E_ACTOR, "K2_DestroyActor", inp={"self": "@fe.Array Element"})
    g.set("cmr", "MeasureRow", inp={"MeasureRow": "None"}); g.set("cpm", "PoseMod", inp={"PoseMod": "None"}); g.get("gpk2", "PoseKnown"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gpk2.PoseKnown"})
    g.n("rp", "call_self", function="Rebuild Poses")
    g.chain("entry", "stop", "sa", "pa", "sta", "fe"); g.chain("fe", "bn", "dst"); g.chain("fe:Completed", "cmr", "cpm", "clr", "rp")
    return fn("Stop Pose", graph=g)


def f_rebuild_pose_links():
    """Link row of the poses page ("Stop pose") and the x that clears the search box."""
    g = G(); g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Pose Links", inp={"self": "@gp.Panel"})
    g.n("rst", "call_self", function="Rebuild Status")   # "Stop pose" and "Measure all" live in the status bar now
    g.get("gp3", "Panel"); g.call("cls", W_PANEL, "Clear Pose Search Links", inp={"self": "@gp3.Panel"})
    xw = create_widget(g, "cx", W_TXT); set_manager(g, "smx", W_TXT, xw)
    g.call("xt", K_TXT, "Conv_StringToText", inp={"InString": "×"}); g.call("xi", W_TXT, "Init", inp={"self": xw, "action": "ClearPoseSearch", "caption": "@xt.ReturnValue"})
    g.get("gp4", "Panel"); g.call("ax", W_PANEL, "Add Pose Search Link", inp={"self": "@gp4.Panel", "widget": xw})
    g.chain("entry", "cl", "rst", "cls", "cx_cr", "smx", "xi", "ax")
    return fn("Rebuild Pose Links", graph=g)


def f_toggle_pose_favorite():
    g = G(); g.n("k", "call_self", function="Pose Key", inp={"row": "@entry.name"}); g.set("sk", "TmpName2", inp={"TmpName2": "@k.key"})
    g.get("gk", "TmpName2"); g.n("isf", "call_self", function="Is Favorite", inp={"name": "@gk.TmpName2"}); g.branch("b", "@isf.yes")
    g.get("gf", "Favorites"); g.get("gk1", "TmpName2"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gf.Favorites", "Item": "@gk1.TmpName2"})
    g.get("gf2", "Favorites"); g.get("gk2", "TmpName2"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gf2.Favorites", "NewItem": "@gk2.TmpName2"})
    g.n("sv", "call_self", function="Save Settings"); g.n("rl", "call_self", function="Rebuild Poses")
    g.chain("entry", "sk", "b", "rm", "sv"); g.chain("b:else", "add", "sv"); g.chain("sv", "rl")
    return fn("Toggle Pose Favorite", [param("name", "name")], graph=g)


def f_toggle_pose_hidden():
    """Hide / unhide a pose (HiddenItems, key pose:<row>); chip "Hidden" without a hidden row left -> All; chips + tiles redrawn."""
    g = G(); g.n("k", "call_self", function="Pose Key", inp={"row": "@entry.name"}); g.set("sk", "TmpName2", inp={"TmpName2": "@k.key"})
    g.get("gk", "TmpName2"); g.n("ish", "call_self", function="Is Item Hidden", inp={"name": "@gk.TmpName2"}); g.branch("b", "@ish.yes")
    g.get("gh", "HiddenItems"); g.get("gk1", "TmpName2"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gh.HiddenItems", "Item": "@gk1.TmpName2"})
    g.get("gh2", "HiddenItems"); g.get("gk2", "TmpName2"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gh2.HiddenItems", "NewItem": "@gk2.TmpName2"})
    g.n("sv", "call_self", function="Save Settings")
    g.n("col", "call_self", function="Collect Pose Rows"); g.n("lg", "call_self", function="Pose Groups")
    g.call("hasH", K_ARR, "Array_Contains", inp={"TargetArray": "@lg.groups", "ItemToFind": g.lit_name("hn", "Hidden")})
    g.get("gg", "PoseGroup"); g.call("onH", K_MATH, "EqualEqual_NameName", inp={"A": "@gg.PoseGroup", "B": "Hidden"}); g.call("nh", K_MATH, "Not_PreBool", inp={"A": "@hasH.ReturnValue"})
    g.call("back", K_MATH, "BooleanAND", inp={"A": "@onH.ReturnValue", "B": "@nh.ReturnValue"}); g.branch("bb", "@back.ReturnValue"); g.set("sg", "PoseGroup", inp={"PoseGroup": "None"})
    g.n("rch", "call_self", function="Rebuild Pose Chips"); g.n("rl", "call_self", function="Rebuild Poses")
    g.chain("entry", "sk", "b", "rm", "sv"); g.chain("b:else", "add", "sv"); g.chain("sv", "col", "lg", "bb", "sg", "rch"); g.chain("bb:else", "rch"); g.chain("rch", "rl")
    return fn("Toggle Pose Hidden", [param("name", "name")], graph=g)


def f_reset_pose_measurement():
    """Context menu: forget the measured category of one pose (it can be measured again or set by hand)."""
    g = G(); g.get("gk", "PoseKind"); g.call("rk", K_MAP, "Map_Remove", inp={"TargetMap": "@gk.PoseKind", "Key": "@entry.name"})
    g.get("gm", "PoseMoving"); g.call("rm", K_MAP, "Map_Remove", inp={"TargetMap": "@gm.PoseMoving", "Key": "@entry.name"})
    g.get("gmn", "PoseManual"); g.call("rmn", K_MAP, "Map_Remove", inp={"TargetMap": "@gmn.PoseManual", "Key": "@entry.name"})
    g.n("sv", "call_self", function="Save Settings"); g.n("rc", "call_self", function="Rebuild Pose Cats"); g.n("rp", "call_self", function="Rebuild Poses")
    g.chain("entry", "rk", "rm", "rmn", "sv", "rc", "rp")
    return fn("Reset Pose Measurement", [param("name", "name")], graph=g)


def f_set_pose_measurement():
    """Context menu: file a pose under a category by hand (the movement flag is kept)."""
    g = G(); g.n("mv", "call_self", function="Is Pose Moving", inp={"row": "@entry.name"})
    g.n("spk", "call_self", function="Set Pose Kind", inp={"row": "@entry.name", "kind": "@entry.kind", "moving": "@mv.yes", "manual": "true"})
    g.n("rp", "call_self", function="Rebuild Poses"); g.chain("entry", "spk", "rp")
    return fn("Set Pose Measurement", [param("name", "name"), param("kind", "name")], graph=g)


def f_toggle_pose_moving():
    """Context menu: mark a pose as moving / still by hand."""
    g = G(); g.n("pk", "call_self", function="Pose Kind", inp={"row": "@entry.name"}); g.n("mv", "call_self", function="Is Pose Moving", inp={"row": "@entry.name"})
    g.call("not", K_MATH, "Not_PreBool", inp={"A": "@mv.yes"})
    g.n("spk", "call_self", function="Set Pose Kind", inp={"row": "@entry.name", "kind": "@pk.kind", "moving": "@not.ReturnValue", "manual": "true"})
    g.n("spk2", "call_self", function="Set Pose Kind", inp={"row": "@entry.name", "kind": "Stand", "moving": "@not.ReturnValue", "manual": "true"})   # never measured: file it under standing so it is visible somewhere
    g.branch("bk", "@pk.found"); g.n("rp", "call_self", function="Rebuild Poses")
    g.chain("entry", "bk", "spk", "rp"); g.chain("bk:else", "spk2", "rp")
    return fn("Toggle Pose Moving", [param("name", "name")], graph=g)


def f_pose_set_stand():
    g = G(); g.n("s", "call_self", function="Set Pose Measurement", inp={"name": "@entry.name", "kind": "Stand"}); g.chain("entry", "s")
    return fn("Pose Set Stand", [param("name", "name")], graph=g)


def f_pose_set_sit():
    g = G(); g.n("s", "call_self", function="Set Pose Measurement", inp={"name": "@entry.name", "kind": "Sit"}); g.chain("entry", "s")
    return fn("Pose Set Sit", [param("name", "name")], graph=g)


def f_pose_set_lie():
    g = G(); g.n("s", "call_self", function="Set Pose Measurement", inp={"name": "@entry.name", "kind": "Lie"}); g.chain("entry", "s")
    return fn("Pose Set Lie", [param("name", "name")], graph=g)


def f_pose_only_mod():
    """Context menu 'Only this mod': the row's mod chip."""
    g = G(); g.n("imd", "call_self", function="Item Mod", inp={"row": "@entry.name"}); g.branch("b", "@imd.found"); g.n("mal", "call_self", function="Mod Alias", inp={"mod": "@imd.mod"})
    g.n("sg", "call_self", function="Select Pose Group", inp={"name": "@mal.alias"})
    g.chain("entry", "b", "sg"); return fn("Pose Only Mod", [param("name", "name")], graph=g)


def f_on_pose_context():
    """Pose tile menu: favourite on/off, hide/unhide, [only this mod when the row comes from a mod], cancel."""
    def pre(g):
        g.set("sci", "ContextItem", inp={"ContextItem": "@entry.name"})
        g.n("isf", "call_self", function="Is Pose Favorite", inp={"name": "@entry.name"}); g.call("fs", K_MATH, "SelectString", inp={"A": ts(g, "fr", "Menu_FavRemove"), "B": ts(g, "fa", "Menu_FavAdd"), "bPickA": "@isf.yes"})
        g.call("ft", K_TXT, "Conv_StringToText", inp={"InString": "@fs.ReturnValue"})
        g.n("ihd", "call_self", function="Is Pose Hidden", inp={"name": "@entry.name"}); g.call("hs", K_MATH, "SelectString", inp={"A": ts(g, "hu", "Menu_Unhide"), "B": ts(g, "hh", "Menu_Hide"), "bPickA": "@ihd.yes"})
        g.call("ht", K_TXT, "Conv_StringToText", inp={"InString": "@hs.ReturnValue"})
        g.n("imv", "call_self", function="Is Pose Moving", inp={"row": "@entry.name"})
        g.call("ms", K_MATH, "SelectString", inp={"A": ts(g, "mr", "Menu_PoseSetStill"), "B": ts(g, "ma", "Menu_PoseSetMove"), "bPickA": "@imv.yes"})
        g.call("mt", K_TXT, "Conv_StringToText", inp={"InString": "@ms.ReturnValue"}); return ["sci"]
    g = simple_menu("On Pose Context", [("PoseFav", "@ft.ReturnValue"), ("PoseHide", "@ht.ReturnValue"), ("Rename", "Menu_Rename"),
                                        ("PoseSetStand", "Menu_PoseSetStand"), ("PoseSetSit", "Menu_PoseSetSit"), ("PoseSetLie", "Menu_PoseSetLie"),
                                        ("PoseSetMove", "@mt.ReturnValue"), ("PoseReset", "Menu_PoseReset"),
                                        ("RenameMod", "Menu_RenameMod"), ("PoseOnlyMod", "Menu_LookOnlyMod"), ("ModContent", "Menu_ModContent"), ("Cancel", "Menu_Cancel")],
                    pre=pre, cond={"RenameMod": "Item Mod", "PoseOnlyMod": "Item Mod", "ModContent": "Item Mod"})
    return fn("On Pose Context", [param("name", "name")], graph=g)


def f_on_pose_search_changed():
    """Panel key-up: the poses search box -> PoseSearchText; chips + tiles when it changed (poses page only)."""
    g = G(); g.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@entry.text"})
    g.get("gst", "PoseSearchText"); g.call("neq", K_STR, "NotEqual_StrStr", inp={"A": "@t2s.ReturnValue", "B": "@gst.PoseSearchText"}); g.branch("b", "@neq.ReturnValue")
    g.set("s", "PoseSearchText", inp={"PoseSearchText": "@t2s.ReturnValue"})
    g.get("gpg", "Page"); g.call("isl", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Poses"}); g.branch("bl", "@isl.ReturnValue")
    g.n("rc", "call_self", function="Rebuild Pose Chips"); g.n("rk", "call_self", function="Rebuild Poses")
    g.n("rcat", "call_self", function="Rebuild Pose Cats")   # the sidebar carries the hit counts, so it has to follow the search
    g.chain("entry", "b", "s", "bl", "rcat", "rc", "rk")
    return fn("On Pose Search Changed", [param("text", "text")], graph=g)


# ---------------- Weapons tab: skin mods (WeaponSkin_*), the game's gun paints, the weapon list from ItemTable ----------------
def scan_weapon_mods(table, struct_path, owner, weapon_var, list_var, icon_map=None):
    """Graph of Scan Weapon Skins / Scan Weapon Models: every row of <table> in every installed weapon mod.
    A mod brings a model, skins, or both - one folder, one table per kind, so each scan reads its own."""
    g = G()
    for i, m in enumerate((owner, weapon_var)):
        g.get("gm%d" % i, m); g.call("mc%d" % i, K_MAP, "Map_Clear", inp={"TargetMap": "@gm%d.%s" % (i, m)})
    g.get("gl", list_var); g.call("lc", K_ARR, "Array_Clear", inp={"TargetArray": "@gl.%s" % list_var})
    if icon_map: g.get("gic", icon_map); g.call("icc", K_MAP, "Map_Clear", inp={"TargetMap": "@gic.%s" % icon_map})
    g.call("rn", K_DT, "GetDataTableRowNames", inp={"Table": P_DLC_T}); g.foreach("fe", "@rn.OutRowNames")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@fe.Array Element"})
    # Weapon_ is what the converter writes; WeaponSkin_ is what its first version wrote and stays readable
    cond = None
    for i, pref in enumerate(ws.MOD_PREFIXES):
        g.call("sw%d" % i, K_STR, "StartsWith", inp={"SourceString": "@n2s.ReturnValue", "InPrefix": pref, "SearchCase": "CaseSensitive"})
        if cond is None: cond = "@sw%d.ReturnValue" % i
        else:
            g.call("or%d" % i, K_MATH, "BooleanOR", inp={"A": cond, "B": "@sw%d.ReturnValue" % i}); cond = "@or%d.ReturnValue" % i
    g.branch("bp", cond)
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "/Game/Mod/", "B": "@n2s.ReturnValue"})
    g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "/%s.%s" % (table, table)})
    g.call("sp", K_SYS, "MakeSoftObjectPath", inp={"PathString": "@c2.ReturnValue"}); g.call("sr", K_SYS, "Conv_SoftObjPathToSoftObjRef", inp={"SoftObjectPath": "@sp.ReturnValue"})
    g.call("ld", K_SYS, "LoadAsset_Blocking", inp={"Asset": "@sr.ReturnValue"})
    # a mod without this kind of table -> end of the iteration. NOT a link back to the ForEachLoop: that is its Exec
    # input, which starts the loop over at index 0 - with a model-only mod in the skin scan the game would hang.
    g.cast("ck", E_DATATABLE, "@ld.ReturnValue", pure=False, miss="ignore")
    g.call("rows", K_DT, "GetDataTableRowNames", inp={"Table": "@ck.AsData Table"}); g.foreach("fr", "@rows.OutRowNames")
    g.n("row", "get_row", inp={"DataTable": "@ck.AsData Table", "RowName": "@fr.Array Element"}, miss="ignore"); g.brk("br", struct_path, "@row.OutRow")
    g.get("go1", owner); g.call("ao", K_MAP, "Map_Add", inp={"TargetMap": "@go1.%s" % owner, "Key": "@fr.Array Element", "Value": "@fe.Array Element"})
    g.get("gw1", weapon_var); g.call("aw", K_MAP, "Map_Add", inp={"TargetMap": "@gw1.%s" % weapon_var, "Key": "@fr.Array Element", "Value": "@br.Weapon"})
    g.get("gl2", list_var); g.call("al", K_ARR, "Array_Add", inp={"TargetArray": "@gl2.%s" % list_var, "NewItem": "@fr.Array Element"})
    if icon_map: g.get("gic2", icon_map); g.call("ai", K_MAP, "Map_Add", inp={"TargetMap": "@gic2.%s" % icon_map, "Key": "@fr.Array Element", "Value": "@br.Icon"})
    g.chain("entry", "mc0", "mc1", "lc", *(["icc"] if icon_map else []), "rn", "fe"); g.chain("fe", "bp", "ld", "ck", "rows", "fr")
    g.chain("fr", "row", "ao", "aw", *(["ai"] if icon_map else []), "al")
    return g


# ---------------- Mods tab: entries and fields other mods register (modui.py) ----------------
def mod_table_load(g, p, pak_pin, table):
    """/Game/Mod/<pak>/<table> loaded by path and cast to DataTable (exec ids: load, cast)."""
    g.call(p + "_n2s", K_STR, "Conv_NameToString", inp={"InName": pak_pin})
    g.call(p + "_c1", K_STR, "Concat_StrStr", inp={"A": "/Game/Mod/", "B": "@%s_n2s.ReturnValue" % p})
    g.call(p + "_c2", K_STR, "Concat_StrStr", inp={"A": "@%s_c1.ReturnValue" % p, "B": "/%s.%s" % (table, table)})
    g.call(p + "_sp", K_SYS, "MakeSoftObjectPath", inp={"PathString": "@%s_c2.ReturnValue" % p})
    g.call(p + "_sr", K_SYS, "Conv_SoftObjPathToSoftObjRef", inp={"SoftObjectPath": "@%s_sp.ReturnValue" % p})
    g.call(p + "_ld", K_SYS, "LoadAsset_Blocking", inp={"Asset": "@%s_sr.ReturnValue" % p})
    g.cast(p + "_ck", E_DATATABLE, "@%s_ld.ReturnValue" % p, pure=False, miss="ignore")
    return p + "_ld", p + "_ck", "@%s_ck.AsData Table" % p


def mod_key(g, p, pak_pin, row_pin):
    """<pak>/<row> as a name pin."""
    g.call(p + "_a", K_STR, "Conv_NameToString", inp={"InName": pak_pin}); g.call(p + "_b", K_STR, "Conv_NameToString", inp={"InName": row_pin})
    g.call(p + "_c", K_STR, "Concat_StrStr", inp={"A": "@%s_a.ReturnValue" % p, "B": "/"}); g.call(p + "_d", K_STR, "Concat_StrStr", inp={"A": "@%s_c.ReturnValue" % p, "B": "@%s_b.ReturnValue" % p})
    g.call(p, K_STR, "Conv_StringToName", inp={"InString": "@%s_d.ReturnValue" % p}); return "@%s.ReturnValue" % p


def f_mod_field_valid():
    """yes = AltUI can draw the field: a known type, a choice with options, a slider or number with Min < Max."""
    g = G()
    ors = None
    for i, t in enumerate(mu.TYPES):
        g.call("t%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@bf.Type", "B": t})
        if ors is None: ors = "@t%d.ReturnValue" % i
        else: g.call("o%d" % i, K_MATH, "BooleanOR", inp={"A": ors, "B": "@t%d.ReturnValue" % i}); ors = "@o%d.ReturnValue" % i
    g.brk("bf", mu.FIELD_STRUCT, "@entry.field")
    g.call("ol", K_ARR, "Array_Length", inp={"TargetArray": "@bf.Options"}); g.call("oh", K_MATH, "Greater_IntInt", inp={"A": "@ol.ReturnValue", "B": "0"})
    g.call("ic", K_MATH, "EqualEqual_NameName", inp={"A": "@bf.Type", "B": "Choice"}); g.call("nc", K_MATH, "Not_PreBool", inp={"A": "@ic.ReturnValue"})
    g.call("cok", K_MATH, "BooleanOR", inp={"A": "@nc.ReturnValue", "B": "@oh.ReturnValue"})
    g.call("rg", K_MATH, "Less_FloatFloat", inp={"A": "@bf.Min", "B": "@bf.Max"})
    g.call("isl0", K_MATH, "EqualEqual_NameName", inp={"A": "@bf.Type", "B": "Slider"}); g.call("isn0", K_MATH, "EqualEqual_NameName", inp={"A": "@bf.Type", "B": "Number"})
    g.call("isl", K_MATH, "BooleanOR", inp={"A": "@isl0.ReturnValue", "B": "@isn0.ReturnValue"}); g.call("nsl", K_MATH, "Not_PreBool", inp={"A": "@isl.ReturnValue"})
    g.call("sok", K_MATH, "BooleanOR", inp={"A": "@nsl.ReturnValue", "B": "@rg.ReturnValue"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": ors, "B": "@cok.ReturnValue"}); g.call("a2", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@sok.ReturnValue"})
    g.link("a2.ReturnValue", "return.yes")
    return fn("Mod Field Valid", [param("field", "struct:" + mu.FIELD_STRUCT)], [param("yes", "bool")], graph=g, pure=True)


def f_mod_entry_pos():
    """Where a new entry goes in ModEntryKeys: after every entry with a lower or equal Order (equal: the one found first stays first)."""
    g = G(); g.set("z", "ModPosTmp", inp={"ModPosTmp": "0"})
    g.get("gk", "ModEntryKeys"); g.foreach("fe", "@gk.ModEntryKeys")
    g.get("ge", "ModEntries"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@ge.ModEntries", "Key": "@fe.Array Element"}); g.brk("be", mu.ENTRY_STRUCT, "@f.Value")
    g.call("le", K_MATH, "LessEqual_IntInt", inp={"A": "@be.Order", "B": "@entry.order"}); g.branch("b", "@le.ReturnValue")
    g.get("gp", "ModPosTmp"); g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gp.ModPosTmp", "B": "1"}); g.set("s", "ModPosTmp", inp={"ModPosTmp": "@inc.ReturnValue"})
    g.get("gr", "ModPosTmp"); g.link("gr.ModPosTmp", "return.index")
    g.chain("entry", "z", "fe"); g.chain("fe", "b", "s"); g.chain("fe:Completed", "return")
    return fn("Mod Entry Pos", [param("order", "int")], [param("index", "int")], graph=g)


def f_add_mod_field():
    """Put one field into the list of its entry (ModFields[key]), after every field with a lower or equal Order."""
    g = G()
    g.get("gm", "ModFields"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gm.ModFields", "Key": "@entry.key"}); g.brk("bl", mu.LIST_STRUCT, "@f.Value")
    g.set("sl", "ModFieldsTmp", inp={"ModFieldsTmp": "@bl.Fields"})   # not found: the default struct, an empty list
    g.set("z", "ModPosTmp", inp={"ModPosTmp": "0"}); g.brk("bn", mu.FIELD_STRUCT, "@entry.field")
    g.get("gt", "ModFieldsTmp"); g.foreach("fe", "@gt.ModFieldsTmp"); g.brk("bo", mu.FIELD_STRUCT, "@fe.Array Element")
    g.call("le", K_MATH, "LessEqual_IntInt", inp={"A": "@bo.Order", "B": "@bn.Order"}); g.branch("b", "@le.ReturnValue")
    g.get("gp", "ModPosTmp"); g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gp.ModPosTmp", "B": "1"}); g.set("s", "ModPosTmp", inp={"ModPosTmp": "@inc.ReturnValue"})
    g.get("gt2", "ModFieldsTmp"); g.get("gp2", "ModPosTmp")
    g.call("ins", K_ARR, "Array_Insert", inp={"TargetArray": "@gt2.ModFieldsTmp", "NewItem": "@entry.field", "Index": "@gp2.ModPosTmp"})
    g.get("gt3", "ModFieldsTmp"); g.make("mk", mu.LIST_STRUCT, Fields="@gt3.ModFieldsTmp")
    g.get("gm2", "ModFields"); g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gm2.ModFields", "Key": "@entry.key", "Value": "@mk.S_ModFieldList"})
    g.chain("entry", "sl", "z", "fe"); g.chain("fe", "b", "s"); g.chain("fe:Completed", "ins", "add")
    return fn("Add Mod Field", [param("key", "name"), param("field", "struct:" + mu.FIELD_STRUCT)], graph=g)


def f_scan_mod_entries():
    """Once per level: every installed mod's AltUI_Entries and AltUI_Fields, one load by path per row of DLC_MainTable
    (row name = pak name = mod folder) - no registry scan. ModEntryKeys in Order, ModFields per entry in Order; fields
    that cannot be drawn or name an entry the mod does not have are left out."""
    g = G(); g.get("gs", "ModScanned"); g.branch("bs", "@gs.ModScanned"); g.set("ss", "ModScanned", inp={"ModScanned": "true"})
    g.get("gk", "ModEntryKeys"); g.call("ck", K_ARR, "Array_Clear", inp={"TargetArray": "@gk.ModEntryKeys"})
    g.get("ge", "ModEntries"); g.call("ce", K_MAP, "Map_Clear", inp={"TargetMap": "@ge.ModEntries"})
    g.get("gf", "ModFields"); g.call("cf", K_MAP, "Map_Clear", inp={"TargetMap": "@gf.ModFields"})
    g.call("rn", K_DT, "GetDataTableRowNames", inp={"Table": P_DLC_T}); g.foreach("fm", "@rn.OutRowNames")
    # entries
    ld, ck, tbl = mod_table_load(g, "e", "@fm.Array Element", mu.ENTRIES_TABLE)
    g.call("er", K_DT, "GetDataTableRowNames", inp={"Table": tbl}); g.foreach("fr", "@er.OutRowNames")
    g.n("row", "get_row", inp={"DataTable": tbl, "RowName": "@fr.Array Element"}, miss="ignore"); g.brk("br", mu.ENTRY_STRUCT, "@row.OutRow")
    key = mod_key(g, "ek", "@fm.Array Element", "@fr.Array Element")
    g.n("pos", "call_self", function="Mod Entry Pos", inp={"order": "@br.Order"})
    g.get("gk2", "ModEntryKeys"); g.call("ins", K_ARR, "Array_Insert", inp={"TargetArray": "@gk2.ModEntryKeys", "NewItem": key, "Index": "@pos.index"})
    g.get("ge2", "ModEntries"); g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@ge2.ModEntries", "Key": key, "Value": "@row.OutRow"})
    # fields, once the mod's entries are known
    fld, fck, ftbl = mod_table_load(g, "f", "@fm.Array Element", mu.FIELDS_TABLE)
    g.call("fr2", K_DT, "GetDataTableRowNames", inp={"Table": ftbl}); g.foreach("ff", "@fr2.OutRowNames")
    g.n("frow", "get_row", inp={"DataTable": ftbl, "RowName": "@ff.Array Element"}, miss="ignore"); g.brk("bff", mu.FIELD_STRUCT, "@frow.OutRow")
    fkey = mod_key(g, "fk", "@fm.Array Element", "@bff.Entry")
    g.n("val", "call_self", function="Mod Field Valid", inp={"field": "@frow.OutRow"})
    g.get("ge3", "ModEntries"); g.call("has", K_MAP, "Map_Contains", inp={"TargetMap": "@ge3.ModEntries", "Key": fkey})
    g.call("ok", K_MATH, "BooleanAND", inp={"A": "@val.yes", "B": "@has.ReturnValue"}); g.branch("bok", "@ok.ReturnValue")
    g.n("amf", "call_self", function="Add Mod Field", inp={"key": fkey, "field": "@frow.OutRow"})
    g.chain("entry", "bs"); g.chain("bs:else", "ss", "ck", "ce", "cf", "rn", "fm")
    g.chain("fm", ld, ck, "er", "fr"); g.chain("fr", "row", "pos", "ins", "add")
    g.chain("fr:Completed", fld, fck, "fr2", "ff"); g.chain("ff", "frow", "bok", "amf")
    # quick menu actions (AltUI_Actions) - a loop of their own: a mod may bring actions without any entry
    g.get("gak", "ModActionKeys"); g.call("cak", K_ARR, "Array_Clear", inp={"TargetArray": "@gak.ModActionKeys"})
    g.get("gaa", "ModActions"); g.call("caa", K_MAP, "Map_Clear", inp={"TargetMap": "@gaa.ModActions"})
    g.call("rn2", K_DT, "GetDataTableRowNames", inp={"Table": P_DLC_T}); g.foreach("fm2", "@rn2.OutRowNames")
    ald, ack, atbl = mod_table_load(g, "a", "@fm2.Array Element", mu.ACTIONS_TABLE)
    g.call("ar", K_DT, "GetDataTableRowNames", inp={"Table": atbl}); g.foreach("fa", "@ar.OutRowNames")
    g.n("arow", "get_row", inp={"DataTable": atbl, "RowName": "@fa.Array Element"}, miss="ignore"); g.brk("abr", mu.ACTION_STRUCT, "@arow.OutRow")
    g.call("ak1", K_STR, "Conv_NameToString", inp={"InName": "@fm2.Array Element"}); g.call("ak2", K_STR, "Conv_NameToString", inp={"InName": "@fa.Array Element"})
    g.call("ak3", K_STR, "Concat_StrStr", inp={"A": "@ak1.ReturnValue", "B": "|"}); g.call("ak4", K_STR, "Concat_StrStr", inp={"A": "@ak3.ReturnValue", "B": "@ak2.ReturnValue"})
    g.call("akn", K_STR, "Conv_StringToName", inp={"InString": "@ak4.ReturnValue"})
    g.n("apos", "call_self", function="Mod Action Pos", inp={"order": "@abr.Order"})
    g.get("gak2", "ModActionKeys"); g.call("ains", K_ARR, "Array_Insert", inp={"TargetArray": "@gak2.ModActionKeys", "NewItem": "@akn.ReturnValue", "Index": "@apos.index"})
    g.get("gaa2", "ModActions"); g.call("aadd", K_MAP, "Map_Add", inp={"TargetMap": "@gaa2.ModActions", "Key": "@akn.ReturnValue", "Value": "@arow.OutRow"})
    g.chain("fm:Completed", "cak", "caa", "rn2", "fm2"); g.chain("fm2", ald, ack, "ar", "fa"); g.chain("fa", "arow", "apos", "ains", "aadd")
    return fn("Scan Mod Entries", graph=g)


W_MODFIELD = M + "/W_ModField"
W_FACEROW = M + "/W_FaceRow"; W_FACEBTN = M + "/W_FaceButton"   # face tab: slider row, saved-face tile


def f_mod_field_changed():
    """A field was changed in the panel (W_ModField) -> the mod's actor, through BPI_AltUIMod. No actor: nothing."""
    g = G(); g.get("ga", "ModActor"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@ga.ModActor"}); g.branch("b", "@iv.ReturnValue")
    g.get("ga2", "ModActor"); g.n("m", "message", cls=mu.INTERFACE, function=mu.ON_CHANGED, inp={"self": "@ga2.ModActor", "Key": "@entry.key", "Value": "@entry.value"})
    g.chain("entry", "b", "m")
    return fn("Mod Field Changed", [param("key", "name"), param("value", "float")], graph=g)


def mod_forward(name, msg, pname, ptype):
    """<name>(key, <pname>) from W_ModField -> the mod's actor through BPI_AltUIMod.<msg>. No actor: nothing."""
    g = G(); g.get("ga", "ModActor"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@ga.ModActor"}); g.branch("b", "@iv.ReturnValue")
    g.get("ga2", "ModActor"); g.n("m", "message", cls=mu.INTERFACE, function=msg, inp={"self": "@ga2.ModActor", "Key": "@entry.key", pname.capitalize(): "@entry." + pname})
    g.chain("entry", "b", "m")
    return fn(name, [param("key", "name"), param(pname, ptype)], graph=g)


def f_begin_key_capture():
    """Key field clicked: it waits for the next key (the panel catches it, see W_AltUI). Another field still waiting stops."""
    g = G(); g.cast("cf", W_MODFIELD, "@entry.field")
    g.get("go", "KeyCapture"); g.cast("co", W_MODFIELD, "@go.KeyCapture", pure=False, miss="ignore")
    g.call("so", W_MODFIELD, "Set Capturing", inp={"self": "@co.AsW_ModField", "on": "false"})
    g.set("sk", "KeyCapture", inp={"KeyCapture": "@entry.field"}); g.call("sc", W_MODFIELD, "Set Capturing", inp={"self": "@cf.AsW_ModField", "on": "true"})
    g.chain("entry", "co", "so", "sk", "sc"); g.chain("co:CastFailed", "sk")
    return fn("Begin Key Capture", [param("field", "object:/Script/UMG.UserWidget")], graph=g)


def f_key_captured():
    """The key for the waiting field: shown there and reported to the mod (On AltUI Key Changed); the quick key link of the options
    takes it as the quick key."""
    g = G(); g.get("gqc", "QuickCapture"); g.branch("bqc", "@gqc.QuickCapture"); g.n("qkc", "call_self", function="Quick Key Captured", inp={"pressed": "@entry.pressed"})
    g.chain("entry", "bqc", "qkc"); g.get("go", "KeyCapture"); g.cast("co", W_MODFIELD, "@go.KeyCapture", pure=False, miss="ignore")
    g.set("s0", "KeyCapture", inp={"KeyCapture": "None"})
    g.call("sc", W_MODFIELD, "Set Capturing", inp={"self": "@co.AsW_ModField", "on": "false"})
    g.call("sk", W_MODFIELD, "Set Key", inp={"self": "@co.AsW_ModField", "pressed": "@entry.pressed"})
    g.get("gk", "Key", cls=W_MODFIELD); g.link("co.AsW_ModField", "gk.self")
    g.n("mk", "call_self", function="Mod Key Changed", inp={"key": "@gk.Key", "pressed": "@entry.pressed"})
    g.chain("bqc:else", "co", "s0", "sc", "sk", "mk"); g.chain("co:CastFailed", "s0")
    return fn("Key Captured", [param("pressed", mu.KEY_TYPE)], graph=g)


def f_cancel_key_capture():
    """Esc or a click elsewhere: the waiting field shows its key again, nothing is reported."""
    g = G(); g.get("go", "KeyCapture"); g.cast("co", W_MODFIELD, "@go.KeyCapture", pure=False, miss="ignore")
    g.set("s0", "KeyCapture", inp={"KeyCapture": "None"}); g.call("sc", W_MODFIELD, "Set Capturing", inp={"self": "@co.AsW_ModField", "on": "false"})
    g.get("gqc", "QuickCapture"); g.branch("bqc", "@gqc.QuickCapture"); g.set("sqc", "QuickCapture", inp={"QuickCapture": "false"}); g.n("rqo", "call_self", function="Rebuild Quick Options")
    g.chain("entry", "bqc", "sqc", "rqo"); g.chain("bqc:else", "co", "s0", "sc"); g.chain("co:CastFailed", "s0")
    return fn("Cancel Key Capture", graph=g)


def f_capturing_key():
    """A field waits for a key - only while the panel is open on the Mods page (the field is on screen)."""
    g = G(); g.get("go", "KeyCapture"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@go.KeyCapture"})
    g.get("gpo", "PanelOpen"); g.get("gpg", "Page"); g.call("ism", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Mods"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@iv.ReturnValue", "B": "@gpo.PanelOpen"}); g.call("a2", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@ism.ReturnValue"})
    # the quick key link of the options waits too
    g.get("gqc", "QuickCapture"); g.call("iso", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Options"}); g.call("q1", K_MATH, "BooleanAND", inp={"A": "@gqc.QuickCapture", "B": "@gpo.PanelOpen"})
    g.call("q2", K_MATH, "BooleanAND", inp={"A": "@q1.ReturnValue", "B": "@iso.ReturnValue"}); g.call("a3", K_MATH, "BooleanOR", inp={"A": "@a2.ReturnValue", "B": "@q2.ReturnValue"})
    g.link("a3.ReturnValue", "return.yes")
    return fn("Capturing Key", outputs=[param("yes", "bool")], graph=g, pure=True)


def f_open_mod_color():
    """Palette for a Color field of a mod (ColorMode Mod, ColorItem = the field's key): Apply Preview sends every change
    live, and closing keeps nothing on AltUI's side - the colour is the mod's."""
    g = G(); g.set("sci", "ColorItem", inp={"ColorItem": "@entry.key"}); g.set("scm", "ColorMode", inp={"ColorMode": "Mod"})
    tail = palette_show(g, "@entry.color")
    g.chain("entry", "sci", "scm", *tail)
    return fn("Open Mod Color", [param("key", "name"), param("color", S_LINCOLOR)], graph=g)


def f_rebuild_mod_entries():
    """Sidebar of the Mods page: one entry per registered list item (caption, number of fields); ModEntry is kept valid."""
    g = G(); g.n("scan", "call_self", function="Scan Mod Entries")
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Mod Entries", inp={"self": "@gp.Panel"})
    g.get("gk", "ModEntryKeys"); g.get("ge", "ModEntry"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gk.ModEntryKeys", "ItemToFind": "@ge.ModEntry"})
    g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@gk.ModEntryKeys"}); g.call("any", K_MATH, "Greater_IntInt", inp={"A": "@len.ReturnValue", "B": "0"})
    g.call("nh", K_MATH, "Not_PreBool", inp={"A": "@has.ReturnValue"}); g.call("fix", K_MATH, "BooleanAND", inp={"A": "@nh.ReturnValue", "B": "@any.ReturnValue"}); g.branch("bf", "@fix.ReturnValue")
    g.get("gk0", "ModEntryKeys"); g.call("first", K_ARR, "Array_Get", inp={"TargetArray": "@gk0.ModEntryKeys", "Index": "0"}); g.set("sf", "ModEntry", inp={"ModEntry": "@first.Item"})
    g.get("gk2", "ModEntryKeys"); g.foreach("fe", "@gk2.ModEntryKeys")
    g.get("gme", "ModEntries"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gme.ModEntries", "Key": "@fe.Array Element"}); g.brk("be", mu.ENTRY_STRUCT, "@f.Value")
    g.get("gmf", "ModFields"); g.call("ff", K_MAP, "Map_Find", inp={"TargetMap": "@gmf.ModFields", "Key": "@fe.Array Element"}); g.brk("bl", mu.LIST_STRUCT, "@ff.Value")
    g.call("n", K_ARR, "Array_Length", inp={"TargetArray": "@bl.Fields"})
    g.get("ge2", "ModEntry"); g.call("sel", K_MATH, "EqualEqual_NameName", inp={"A": "@ge2.ModEntry", "B": "@fe.Array Element"})
    tw = create_widget(g, "ct", W_TAB); set_manager(g, "sm", W_TAB, tw)
    g.call("ti", W_TAB, "Init", inp={"self": tw, "slot": "@fe.Array Element", "caption": "@be.Caption", "count": "@n.ReturnValue", "worn icon": "None",
                                     "selected": "@sel.ReturnValue", "has items": "true", "filtered": "-1", "indent": "false"})
    g.get("gp2", "Panel"); g.call("aa", W_PANEL, "Add Mod Entry", inp={"self": "@gp2.Panel", "widget": tw})
    g.chain("entry", "scan", "cl", "bf", "sf", "fe"); g.chain("bf:else", "fe"); g.chain("fe", "ct_cr", "sm", "ti", "aa")
    return fn("Rebuild Mod Entries", graph=g)


def f_rebuild_mod_fields():
    """Right side: the fields of ModEntry as W_ModField rows. The mod's actor is looked up once here (GetActorOfClass on
    the entry's Actor class); without one the rows are greyed out and a note says why."""
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Mod Fields", inp={"self": "@gp.Panel"})
    g.get("gw", "ModFieldWidgets"); g.call("cw", K_ARR, "Array_Clear", inp={"TargetArray": "@gw.ModFieldWidgets"})
    g.set("sa0", "ModActor", inp={"ModActor": "None"}); g.set("skc", "KeyCapture", inp={"KeyCapture": "None"})   # the field widgets are rebuilt: no capture left over
    g.get("gme", "ModEntries"); g.get("ge", "ModEntry"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gme.ModEntries", "Key": "@ge.ModEntry"}); g.branch("bf", "@f.ReturnValue")
    g.brk("be", mu.ENTRY_STRUCT, "@f.Value")
    g.call("ld", K_SYS, "LoadClassAsset_Blocking", inp={"AssetClass": "@be.Actor"})
    g.n("cc", "class_cast", pure=True, cls=E_ACTOR, inp={"Class": "@ld.ReturnValue"})
    g.call("ga", K_GS, "GetActorOfClass", inp={"ActorClass": "@cc.AsActor"}); g.set("sa", "ModActor", inp={"ModActor": "@ga.ReturnValue"})
    g.get("gmf", "ModFields"); g.get("ge2", "ModEntry"); g.call("ff", K_MAP, "Map_Find", inp={"TargetMap": "@gmf.ModFields", "Key": "@ge2.ModEntry"}); g.brk("bl", mu.LIST_STRUCT, "@ff.Value")
    g.set("sl", "ModFieldsTmp", inp={"ModFieldsTmp": "@bl.Fields"})
    g.get("gt", "ModFieldsTmp"); g.foreach("fe", "@gt.ModFieldsTmp")
    fw = create_widget(g, "cf", W_MODFIELD); set_manager(g, "smf", W_MODFIELD, fw)
    g.call("fi", W_MODFIELD, "Init", inp={"self": fw, "field": "@fe.Array Element"})
    g.get("gp2", "Panel"); g.call("af", W_PANEL, "Add Mod Field Widget", inp={"self": "@gp2.Panel", "widget": fw})
    g.get("gav", "ModActor"); g.call("av", K_SYS, "IsValid", inp={"Object": "@gav.ModActor"})
    g.call("fen", W_MODFIELD, "Set Enabled", inp={"self": fw, "yes": "@av.ReturnValue"})
    g.get("gw2", "ModFieldWidgets"); g.call("aw", K_ARR, "Array_Add", inp={"TargetArray": "@gw2.ModFieldWidgets", "NewItem": fw})
    # the note: no fields, or no actor, or none
    g.get("gt2", "ModFieldsTmp"); g.call("nf", K_ARR, "Array_Length", inp={"TargetArray": "@gt2.ModFieldsTmp"}); g.call("none", K_MATH, "EqualEqual_IntInt", inp={"A": "@nf.ReturnValue", "B": "0"}); g.branch("bn", "@none.ReturnValue")
    g.get("gp3", "Panel"); g.call("h1", W_PANEL, "Set Mod Hint", inp={"self": "@gp3.Panel", "text": tt(g, "tnf", "Lbl_ModNoFields")})
    g.get("gav2", "ModActor"); g.call("av2", K_SYS, "IsValid", inp={"Object": "@gav2.ModActor"}); g.branch("ba", "@av2.ReturnValue")
    g.get("gp4", "Panel"); g.call("h2", W_PANEL, "Set Mod Hint", inp={"self": "@gp4.Panel", "text": ""})
    g.get("gp5", "Panel"); g.call("h3", W_PANEL, "Set Mod Hint", inp={"self": "@gp5.Panel", "text": tt(g, "tin", "Lbl_ModInactive")})
    g.n("poll", "call_self", function="Poll Mods")
    g.chain("entry", "cl", "cw", "sa0", "skc", "bf", "ld", "ga", "sa", "sl", "fe"); g.chain("bf:else", "sl")
    g.chain("fe", "cf_cr", "smf", "fi", "af", "fen", "aw"); g.chain("fe:Completed", "bn", "h1", "poll"); g.chain("bn:else", "ba", "h2", "poll"); g.chain("ba:else", "h3", "poll")
    return fn("Rebuild Mod Fields", graph=g)


def f_poll_mods():
    """While the Mods page is shown: every field's value from the mod's actor, by type - Get AltUI Color for colour
    fields, Get AltUI Text for text and info fields, Get AltUI Key for key fields, Get AltUI Value for the rest - so a change the mod makes itself
    shows in the panel too."""
    g = G(); g.get("ga", "ModActor"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@ga.ModActor"}); g.branch("b", "@iv.ReturnValue")
    g.get("gw", "ModFieldWidgets"); g.foreach("fe", "@gw.ModFieldWidgets")
    g.get("gk", "Key", cls=W_MODFIELD); g.link("fe.Array Element", "gk.self"); g.get("gt", "Type", cls=W_MODFIELD); g.link("fe.Array Element", "gt.self")
    g.call("isc", K_MATH, "EqualEqual_NameName", inp={"A": "@gt.Type", "B": "Color"}); g.branch("bc", "@isc.ReturnValue")
    g.call("ist", K_MATH, "EqualEqual_NameName", inp={"A": "@gt.Type", "B": "Text"}); g.call("isi", K_MATH, "EqualEqual_NameName", inp={"A": "@gt.Type", "B": "Info"})
    g.call("istx", K_MATH, "BooleanOR", inp={"A": "@ist.ReturnValue", "B": "@isi.ReturnValue"}); g.branch("bt", "@istx.ReturnValue")
    g.get("ga2", "ModActor"); g.n("m", "message", cls=mu.INTERFACE, function=mu.GET_VALUE, inp={"self": "@ga2.ModActor", "Key": "@gk.Key"})
    g.call("sv", W_MODFIELD, "Set Value", inp={"self": "@fe.Array Element", "value": "@m.Value"})
    g.get("ga3", "ModActor"); g.n("mc", "message", cls=mu.INTERFACE, function=mu.GET_COLOR, inp={"self": "@ga3.ModActor", "Key": "@gk.Key"})
    g.call("sc", W_MODFIELD, "Set Color", inp={"self": "@fe.Array Element", "color": "@mc.Color"})
    g.get("ga4", "ModActor"); g.n("mt", "message", cls=mu.INTERFACE, function=mu.GET_TEXT, inp={"self": "@ga4.ModActor", "Key": "@gk.Key"})
    g.call("st", W_MODFIELD, "Set Text", inp={"self": "@fe.Array Element", "text": "@mt.Text"})
    g.call("isk", K_MATH, "EqualEqual_NameName", inp={"A": "@gt.Type", "B": "Key"}); g.branch("bk", "@isk.ReturnValue")
    g.get("ga5", "ModActor"); g.n("mk", "message", cls=mu.INTERFACE, function=mu.GET_KEY, inp={"self": "@ga5.ModActor", "Key": "@gk.Key"})
    g.call("sk", W_MODFIELD, "Set Key", inp={"self": "@fe.Array Element", "pressed": "@mk.Pressed"})
    g.chain("entry", "b", "fe"); g.chain("fe", "bc", "mc", "sc"); g.chain("bc:else", "bt", "mt", "st"); g.chain("bt:else", "bk", "mk", "sk"); g.chain("bk:else", "m", "sv")
    return fn("Poll Mods", graph=g)


def f_select_mod_entry():
    g = G(); g.set("s", "ModEntry", inp={"ModEntry": "@entry.name"}); g.n("sv", "call_self", function="Save Settings"); g.n("r", "call_self", function="Rebuild Mod Page")
    g.chain("entry", "s", "sv", "r"); return fn("Select Mod Entry", [param("name", "name")], graph=g)


def f_rebuild_mod_page():
    g = G(); g.n("re", "call_self", function="Rebuild Mod Entries"); g.n("rf", "call_self", function="Rebuild Mod Fields"); g.chain("entry", "re", "rf")
    return fn("Rebuild Mod Page", graph=g)


def f_scan_weapon_skins():
    """SkinOwner[row] = mod folder, SkinWeapon[row] = weapon, SkinList = every skin row of every installed weapon mod."""
    return fn("Scan Weapon Skins", graph=scan_weapon_mods(ws.TABLE_NAME, ws.STRUCT_PATH, "SkinOwner", "SkinWeapon", "SkinList"))


def f_scan_weapon_models():
    """The same for the model rows of Mod_WeaponModel."""
    return fn("Scan Weapon Models", graph=scan_weapon_mods(ws.MODEL_TABLE_NAME, ws.MODEL_STRUCT_PATH, "ModelOwner", "ModelWeapon", "ModelList", "ModelIconOf"))


def f_weapon_rows():
    """The game's weapons: ItemTable rows with HyperBoxGroup "Weapon" (table order)."""
    g = G(); g.get("gn0", "TmpNames4"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gn0.TmpNames4"})
    g.call("rn", K_DT, "GetDataTableRowNames", inp={"Table": P_ITEM_T}); g.set("sn", "TmpNames3", inp={"TmpNames3": "@rn.OutRowNames"})
    g.get("gn", "TmpNames3"); g.foreach("fe", "@gn.TmpNames3")
    g.n("row", "get_row", table=P_ITEM_T, inp={"RowName": "@fe.Array Element"}, miss="ignore"); g.brk("br", P_ITEM_S, "@row.OutRow")
    g.call("isw", K_MATH, "EqualEqual_NameName", inp={"A": "@br.HyperBoxGroup", "B": "Weapon"}); g.branch("b", "@isw.ReturnValue")
    g.get("gn1", "TmpNames4"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gn1.TmpNames4", "NewItem": "@fe.Array Element"})
    g.get("gn2", "TmpNames4"); g.link("gn2.TmpNames4", "return.rows")
    g.chain("entry", "clr", "rn", "sn", "fe"); g.chain("fe", "row", "b", "add"); g.chain("fe:Completed", "return")
    return fn("Weapon Rows", outputs=[param("rows", "name", "array")], graph=g)


def f_skins_for_weapon():
    """Rows shown for one weapon: None (= original), every GunPaint row whose Guns map has the weapon, every skin row with that weapon.
    kinds[i] = paint / skin ("none" for the first entry)."""
    g = G()
    g.get("gr0", "SkinRows"); g.call("cr", K_ARR, "Array_Clear", inp={"TargetArray": "@gr0.SkinRows"})
    g.get("gk0", "SkinKinds"); g.call("ck", K_ARR, "Array_Clear", inp={"TargetArray": "@gk0.SkinKinds"})
    def add(p, kind, row_pin):
        g.get(p + "gr", "SkinRows"); g.call(p + "ar", K_ARR, "Array_Add", inp={"TargetArray": "@%sgr.SkinRows" % p, "NewItem": row_pin})
        g.get(p + "gk", "SkinKinds"); g.call(p + "ak", K_ARR, "Array_Add", inp={"TargetArray": "@%sgk.SkinKinds" % p, "NewItem": g.lit_name(p + "kn", kind)}); return [p + "ar", p + "ak"]
    a0 = add("o", "none", g.lit_name("nrow", "None"))
    g.call("rp", K_DT, "GetDataTableRowNames", inp={"Table": P_PAINT_T}); g.foreach("fp", "@rp.OutRowNames")
    g.n("prow", "get_row", table=P_PAINT_T, inp={"RowName": "@fp.Array Element"}, miss="ignore"); g.brk("pbr", P_PAINT_S, "@prow.OutRow")
    g.call("has", K_MAP, "Map_Contains", inp={"TargetMap": "@pbr.Guns", "Key": "@entry.weapon"}); g.branch("bp", "@has.ReturnValue")
    a1 = add("p", "paint", "@fp.Array Element")
    g.get("gsl", "SkinList"); g.foreach("fs", "@gsl.SkinList")
    g.get("gsw", "SkinWeapon"); g.call("fw", K_MAP, "Map_Find", inp={"TargetMap": "@gsw.SkinWeapon", "Key": "@fs.Array Element"})
    g.call("eqw", K_MATH, "EqualEqual_NameName", inp={"A": "@fw.Value", "B": "@entry.weapon"}); g.call("okw", K_MATH, "BooleanAND", inp={"A": "@fw.ReturnValue", "B": "@eqw.ReturnValue"}); g.branch("bs", "@okw.ReturnValue")
    a2 = add("s", "skin", "@fs.Array Element")
    g.get("gr9", "SkinRows"); g.link("gr9.SkinRows", "return.rows"); g.get("gk9", "SkinKinds"); g.link("gk9.SkinKinds", "return.kinds")
    g.chain("entry", "cr", "ck", *a0, "rp", "fp"); g.chain("fp", "prow", "bp", *a1)
    g.chain("fp:Completed", "fs"); g.chain("fs", "bs", *a2); g.chain("fs:Completed", "return")
    return fn("Skins For Weapon", [param("weapon", "name")], [param("rows", "name", "array"), param("kinds", "name", "array")], graph=g)


def f_skin_mod():
    g = G(); g.get("go", "SkinOwner"); g.call("mf", K_MAP, "Map_Find", inp={"TargetMap": "@go.SkinOwner", "Key": "@entry.row"})
    g.link("mf.ReturnValue", "return.found"); g.link("mf.Value", "return.mod")
    return fn("Skin Mod", [param("row", "name")], [param("found", "bool"), param("mod", "name")], graph=g, pure=True)


def f_skin_row():
    """Row of a skin mod's table (icon / caption / textures); invalid row -> empty struct."""
    g = G(); g.n("md", "call_self", function="Skin Mod", inp={"row": "@entry.row"}); g.branch("b", "@md.found")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@md.mod"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "/Game/Mod/", "B": "@n2s.ReturnValue"})
    g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "/%s.%s" % (ws.TABLE_NAME, ws.TABLE_NAME)})
    g.call("sp", K_SYS, "MakeSoftObjectPath", inp={"PathString": "@c2.ReturnValue"}); g.call("sr", K_SYS, "Conv_SoftObjPathToSoftObjRef", inp={"SoftObjectPath": "@sp.ReturnValue"})
    g.call("ld", K_SYS, "LoadAsset_Blocking", inp={"Asset": "@sr.ReturnValue"}); g.cast("ck", E_DATATABLE, "@ld.ReturnValue", pure=False)
    g.n("row", "get_row", inp={"DataTable": "@ck.AsData Table", "RowName": "@entry.row"}, miss="ignore"); g.brk("br", ws.STRUCT_PATH, "@row.OutRow")
    g.set("st", "TmpSkin", inp={"TmpSkin": "@row.OutRow"}); g.get("gt", "TmpSkin"); g.link("gt.TmpSkin", "return.skin")
    g.chain("entry", "b", "ld", "ck", "row", "st", "return"); g.chain("b:else", "return"); g.chain("ck:CastFailed", "return"); g.chain("row:Row Not Found", "return")
    return fn("Skin Row", [param("row", "name")], [param("skin", "struct:" + ws.STRUCT_PATH)], graph=g)


def f_model_mod():
    g = G(); g.get("go", "ModelOwner"); g.call("mf", K_MAP, "Map_Find", inp={"TargetMap": "@go.ModelOwner", "Key": "@entry.row"})
    g.link("mf.ReturnValue", "return.found"); g.link("mf.Value", "return.mod")
    return fn("Model Mod", [param("row", "name")], [param("found", "bool"), param("mod", "name")], graph=g, pure=True)


def f_models_for_weapon():
    """Rows shown in the model section of one weapon: None (= the game's own model) + every model row for it."""
    g = G()
    g.get("gr0", "ModelRows"); g.call("cr", K_ARR, "Array_Clear", inp={"TargetArray": "@gr0.ModelRows"})
    g.get("gr1", "ModelRows"); g.call("a0", K_ARR, "Array_Add", inp={"TargetArray": "@gr1.ModelRows", "NewItem": g.lit_name("nrow", "None")})
    g.get("gml", "ModelList"); g.foreach("fm", "@gml.ModelList")
    g.get("gmw", "ModelWeapon"); g.call("fw", K_MAP, "Map_Find", inp={"TargetMap": "@gmw.ModelWeapon", "Key": "@fm.Array Element"})
    g.call("eqw", K_MATH, "EqualEqual_NameName", inp={"A": "@fw.Value", "B": "@entry.weapon"})
    g.call("okw", K_MATH, "BooleanAND", inp={"A": "@fw.ReturnValue", "B": "@eqw.ReturnValue"}); g.branch("bm", "@okw.ReturnValue")
    g.get("gr2", "ModelRows"); g.call("am", K_ARR, "Array_Add", inp={"TargetArray": "@gr2.ModelRows", "NewItem": "@fm.Array Element"})
    g.get("gr9", "ModelRows"); g.link("gr9.ModelRows", "return.rows")
    g.chain("entry", "cr", "a0", "fm"); g.chain("fm", "bm", "am"); g.chain("fm:Completed", "return")
    return fn("Models For Weapon", [param("weapon", "name")], [param("rows", "name", "array")], graph=g)


def f_model_mesh():
    """The mesh that replaces `orig` for the chosen model: the mod's package of the same name, else `orig` itself.

    Looked up by the name of the ORIGINAL mesh, never of the one currently set - otherwise a second change would find
    nothing. That a replacer names its files like the game's is what makes magazine and optics come along here."""
    g = G()
    g.n("md", "call_self", function="Model Mod", inp={"row": "@entry.model"}); g.branch("b", "@md.found")
    g.call("on", K_SYS, "GetObjectName", inp={"Object": "@entry.orig"})
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@md.mod"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "/Game/Mod/", "B": "@n2s.ReturnValue"})
    g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "/"})
    g.call("c3", K_STR, "Concat_StrStr", inp={"A": "@c2.ReturnValue", "B": "@on.ReturnValue"})
    g.call("c4", K_STR, "Concat_StrStr", inp={"A": "@c3.ReturnValue", "B": "."})
    g.call("c5", K_STR, "Concat_StrStr", inp={"A": "@c4.ReturnValue", "B": "@on.ReturnValue"})
    g.call("sp", K_SYS, "MakeSoftObjectPath", inp={"PathString": "@c5.ReturnValue"}); g.call("sr", K_SYS, "Conv_SoftObjPathToSoftObjRef", inp={"SoftObjectPath": "@sp.ReturnValue"})
    g.call("ld", K_SYS, "LoadAsset_Blocking", inp={"Asset": "@sr.ReturnValue"})
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@ld.ReturnValue"}); g.branch("b2", "@iv.ReturnValue")
    g.set("sm", "TmpMesh", inp={"TmpMesh": "@ld.ReturnValue"}); g.set("so", "TmpMesh", inp={"TmpMesh": "@entry.orig"})
    g.get("gm", "TmpMesh"); g.link("gm.TmpMesh", "return.mesh")
    # no model chosen or the mod has no package of that name (a model may replace only part of a weapon): the original
    if WEAPONLOG:
        log(g, "try", ["  mesh ", "@on.ReturnValue", " -> ", "@c5.ReturnValue"])
        log(g, "hit", ["  loaded ", "@c5.ReturnValue"])
        log(g, "gone", ["  NOT loaded ", "@c5.ReturnValue"])
        log(g, "nomod", ["  no mod owns model row ", nstr(g, "mm", "@entry.model")])
        g.chain("entry", "so", "b", "lgtry", "ld", "b2", "lghit", "sm", "return")
        g.chain("b:else", "lgnomod", "return"); g.chain("b2:else", "lggone", "return")
    else:
        g.chain("entry", "so", "b", "ld", "b2", "sm", "return"); g.chain("b:else", "return"); g.chain("b2:else", "return")
    return fn("Model Mesh", [param("model", "name"), param("orig", "object:/Script/CoreUObject.Object")], [param("mesh", "object:/Script/CoreUObject.Object")], graph=g)


def skin_tex(g, t, mid, after):
    """Write a skin's textures onto a dynamic material instance - but only those the skin actually brings.

    A texture parameter set to nothing wipes what the material had there, which leaves the surface black. The rule the
    guides state is the opposite, and it is the useful one: leave a texture out of your row and the game's stays. That
    also covers "Original", where there is no skin row at all and every value is empty.

    Returns the node the caller chains into; `after` is where the exec goes when the last one is done.
    """
    steps = []
    for j, member in enumerate(ws.TEX_MEMBERS[:3]):   # MainTex, NormalTex, MetallicTex (Icon is not a material parameter)
        g.call("%sv%d" % (t, j), K_SYS, "IsValid", inp={"Object": "@sb.%s" % member})
        g.branch("%sb%d" % (t, j), "@%sv%d.ReturnValue" % (t, j))
        g.call("%sp%d" % (t, j), E_MID, "SetTextureParameterValue", inp={"self": mid, "ParameterName": member, "Value": "@sb.%s" % member})
        steps.append(("%sb%d" % (t, j), "%sp%d" % (t, j)))
    for k, (br, st) in enumerate(steps):
        nxt = [steps[k + 1][0]] if k + 1 < len(steps) else list(after)
        g.chain(br, st, *nxt); g.chain(br + ":else", *nxt)
    return steps[0][0]


def remember_mats(g, t, comp):
    """OrigMats[comp] = the material of every slot, as the component carries it right now.

    Taken at the same moment as OrigMesh and OrigMat: before any model was put on, so these are the game's own. Apply
    Weapon Look clears every slot to get rid of its own doing, and a mod mesh that brings no material of its own for a
    section would leave that section empty - the engine then draws its grey checkerboard. This is what fills it back in.
    A map cannot hold an array, so the list travels in a one-member struct (S_Mats), like ColorSlotsOf does.

    Returns the node ids to splice into the caller's exec chain.
    """
    g.make(t + "mk", S_MATS); g.set(t + "s0", "TmpMats", inp={"TmpMats": "@%smk.S_Mats" % t})
    g.call(t + "nm", E_PRIM, "GetNumMaterials", inp={"self": comp})
    chain = [t + "s0"]   # GetNumMaterials is pure as well: pulled by the slot branches
    for i in range(FORCE_SLOTS):
        g.call("%sgt%d" % (t, i), K_MATH, "Greater_IntInt", inp={"A": "@%snm.ReturnValue" % t, "B": str(i)})
        g.branch("%sb%d" % (t, i), "@%sgt%d.ReturnValue" % (t, i))
        g.call("%sgm%d" % (t, i), E_PRIM, "GetMaterial", inp={"self": comp, "ElementIndex": str(i)})
        g.get("%sgv%d" % (t, i), "TmpMats"); g.brk("%sbr%d" % (t, i), S_MATS, "@%sgv%d.TmpMats" % (t, i))
        g.call("%sad%d" % (t, i), K_ARR, "Array_Add", inp={"TargetArray": "@%sbr%d.Mats" % (t, i), "NewItem": "@%sgm%d.ReturnValue" % (t, i)})
        g.make("%smm%d" % (t, i), S_MATS, Mats="@%sbr%d.Mats" % (t, i))
        g.set("%sss%d" % (t, i), "TmpMats", inp={"TmpMats": "@%smm%d.S_Mats" % (t, i)})
        seq = ["%sad%d" % (t, i), "%sss%d" % (t, i)]   # GetMaterial is pure: its value is pulled, it is not chained
        nxt = ["%sb%d" % (t, i + 1)] if i + 1 < FORCE_SLOTS else [t + "put"]
        g.chain("%sb%d" % (t, i), *seq, *nxt)
        g.chain("%sb%d:else" % (t, i), *nxt)          # fewer slots than FORCE_SLOTS: the list simply ends here
    g.get(t + "gom", "OrigMats"); g.get(t + "gtm", "TmpMats")
    g.call(t + "put", K_MAP, "Map_Add", inp={"TargetMap": "@%sgom.OrigMats" % t, "Key": comp, "Value": "@%sgtm.TmpMats" % t})
    return chain + [t + "b0"]


def f_apply_weapon_model():
    """Set the meshes of one weapon actor to the chosen model (None = the ones the actor started with).

    The original of a component is remembered per COMPONENT, not per weapon: the tile pictures spawn their own weapon
    actor, and with a list per weapon the first actor to come along would decide what "original" means and in which
    order - the icon actor's components are not the hand-held one's. Per component the question does not arise, and a
    freshly spawned actor answers it with what it carries."""
    g = G()
    g.call("sc", E_ACTOR, "K2_GetComponentsByClass", inp={"self": "@entry.actor", "ComponentClass": E_SKELC}); g.set("ss", "TmpSkelComps", inp={"TmpSkelComps": "@sc.ReturnValue"})
    g.get("gsc", "TmpSkelComps"); g.foreach("fs", "@gsc.TmpSkelComps"); g.cast("cks", E_SKINNED, "@fs.Array Element", pure=False, miss="ignore")
    g.get("gos", "OrigMesh"); g.call("hs", K_MAP, "Map_Contains", inp={"TargetMap": "@gos.OrigMesh", "Key": "@cks.AsSkinned Mesh Component"})
    g.call("nhs", K_MATH, "Not_PreBool", inp={"A": "@hs.ReturnValue"}); g.branch("bhs", "@nhs.ReturnValue")
    g.get("ms", "SkeletalMesh", cls=E_SKINNED); g.link("cks.AsSkinned Mesh Component", "ms.self")
    g.get("gos2", "OrigMesh"); g.call("as", K_MAP, "Map_Add", inp={"TargetMap": "@gos2.OrigMesh", "Key": "@cks.AsSkinned Mesh Component", "Value": "@ms.SkeletalMesh"})
    # the same moment for the material: before any model was put on, slot 0 carries the game's own weapon material.
    # That is what "force the game's material" later builds its instances from - a mod's own materials know no skin parameters.
    g.call("gm0s", E_PRIM, "GetMaterial", inp={"self": "@cks.AsSkinned Mesh Component", "ElementIndex": "0"})
    g.get("goms", "OrigMat"); g.call("ams", K_MAP, "Map_Add", inp={"TargetMap": "@goms.OrigMat", "Key": "@cks.AsSkinned Mesh Component", "Value": "@gm0s.ReturnValue"})
    ws_chain = remember_mats(g, "ws", "@cks.AsSkinned Mesh Component")
    g.get("gos3", "OrigMesh"); g.call("fos", K_MAP, "Map_Find", inp={"TargetMap": "@gos3.OrigMesh", "Key": "@cks.AsSkinned Mesh Component"}); g.branch("bfs", "@fos.ReturnValue")
    g.n("mms", "call_self", function="Model Mesh", inp={"model": "@entry.model", "orig": "@fos.Value"})
    g.cast("cms", E_SKELMESH, "@mms.mesh", pure=False, miss="ignore")   # a package of that name that is no skeletal mesh: leave the component alone
    g.call("sets", E_SKINNED, "SetSkeletalMesh", inp={"self": "@cks.AsSkinned Mesh Component", "NewMesh": "@cms.AsSkeletal Mesh", "bReinitPose": "true"})
    g.call("tc", E_ACTOR, "K2_GetComponentsByClass", inp={"self": "@entry.actor", "ComponentClass": E_SMC}); g.set("st", "TmpStatComps", inp={"TmpStatComps": "@tc.ReturnValue"})
    g.get("gtc", "TmpStatComps"); g.foreach("ft", "@gtc.TmpStatComps"); g.cast("ckt", E_SMC, "@ft.Array Element", pure=False, miss="ignore")
    g.get("got", "OrigMesh"); g.call("ht", K_MAP, "Map_Contains", inp={"TargetMap": "@got.OrigMesh", "Key": "@ckt.AsStatic Mesh Component"})
    g.call("nht", K_MATH, "Not_PreBool", inp={"A": "@ht.ReturnValue"}); g.branch("bht", "@nht.ReturnValue")
    g.get("mt", "StaticMesh", cls=E_SMC); g.link("ckt.AsStatic Mesh Component", "mt.self")
    g.get("got2", "OrigMesh"); g.call("at", K_MAP, "Map_Add", inp={"TargetMap": "@got2.OrigMesh", "Key": "@ckt.AsStatic Mesh Component", "Value": "@mt.StaticMesh"})
    g.call("gm0t", E_PRIM, "GetMaterial", inp={"self": "@ckt.AsStatic Mesh Component", "ElementIndex": "0"})
    g.get("gomt", "OrigMat"); g.call("amt", K_MAP, "Map_Add", inp={"TargetMap": "@gomt.OrigMat", "Key": "@ckt.AsStatic Mesh Component", "Value": "@gm0t.ReturnValue"})
    wt_chain = remember_mats(g, "wt", "@ckt.AsStatic Mesh Component")
    g.get("got3", "OrigMesh"); g.call("fot", K_MAP, "Map_Find", inp={"TargetMap": "@got3.OrigMesh", "Key": "@ckt.AsStatic Mesh Component"}); g.branch("bft", "@fot.ReturnValue")
    g.n("mmt", "call_self", function="Model Mesh", inp={"model": "@entry.model", "orig": "@fot.Value"})
    g.cast("cmt", E_STATICMESH, "@mmt.mesh", pure=False, miss="ignore")
    g.call("sett", E_SMC, "SetStaticMesh", inp={"self": "@ckt.AsStatic Mesh Component", "NewMesh": "@cmt.AsStatic Mesh"})
    if WEAPONLOG:
        g.get("qs", "TmpSkelComps"); g.call("qsn", K_ARR, "Array_Length", inp={"TargetArray": "@qs.TmpSkelComps"})
        g.get("qt", "TmpStatComps"); g.call("qtn", K_ARR, "Array_Length", inp={"TargetArray": "@qt.TmpStatComps"})
        log(g, "a", ["apply ", oname(g, "a", "@entry.actor"), " weapon=", nstr(g, "a", "@entry.weapon"),
                     " model=", nstr(g, "am", "@entry.model"), " skel=", num(g, "a", "@qsn.ReturnValue")])
        # "now" is the mesh the component carries on entry: differs from "orig" once somebody else wrote it
        # (the game's own reload/equip code, say). The read-back after the set says whether the assignment stuck and
        # whether the new mesh has sections at all - a mesh with 0 material slots draws nothing.
        log(g, "sc", ["  skel ", oname(g, "sc", "@cks.AsSkinned Mesh Component"), " orig=", oname(g, "so2", "@fos.Value"),
                      " now=", oname(g, "sn", "@ms.SkeletalMesh")])
        g.get("rbs", "SkeletalMesh", cls=E_SKINNED); g.link("cks.AsSkinned Mesh Component", "rbs.self")
        g.call("nms", E_PRIM, "GetNumMaterials", inp={"self": "@cks.AsSkinned Mesh Component"})
        g.call("vis", E_SCENECOMP, "IsVisible", inp={"self": "@cks.AsSkinned Mesh Component"})
        log(g, "sb", ["    set -> ", oname(g, "sb", "@rbs.SkeletalMesh"), " mats=", num(g, "sb", "@nms.ReturnValue"),
                      " visible=", boolstr(g, "sb", "@vis.ReturnValue")])
        log(g, "sx", ["  the loaded package is no skeletal mesh"])
        log(g, "t", ["  static=", num(g, "t", "@qtn.ReturnValue")])
        log(g, "tc", ["  static ", oname(g, "tc", "@ckt.AsStatic Mesh Component"), " orig=", oname(g, "to2", "@fot.Value"),
                      " now=", oname(g, "tn", "@mt.StaticMesh")])
        g.get("rbt", "StaticMesh", cls=E_SMC); g.link("ckt.AsStatic Mesh Component", "rbt.self")   # no BlueprintCallable GetStaticMesh in 4.27 - read the property, as the skeletal side does
        g.call("nmt", E_PRIM, "GetNumMaterials", inp={"self": "@ckt.AsStatic Mesh Component"})
        g.call("vit", E_SCENECOMP, "IsVisible", inp={"self": "@ckt.AsStatic Mesh Component"})
        log(g, "tb", ["    set -> ", oname(g, "tb", "@rbt.StaticMesh"), " mats=", num(g, "tb", "@nmt.ReturnValue"),
                      " visible=", boolstr(g, "tb", "@vit.ReturnValue")])
        log(g, "tx", ["  the loaded package is no static mesh"])
        g.chain("entry", "ss", "lga", "fs"); g.chain("fs", "cks", "bhs", "as", "ams", *ws_chain); g.chain("wsput", "bfs"); g.chain("bhs:else", "bfs")
        g.chain("bfs", "lgsc", "mms", "cms", "sets", "lgsb"); g.chain("cms:CastFailed", "lgsx")
        g.chain("fs:Completed", "st", "lgt", "ft"); g.chain("ft", "ckt", "bht", "at", "amt", *wt_chain); g.chain("wtput", "bft"); g.chain("bht:else", "bft")
        g.chain("bft", "lgtc", "mmt", "cmt", "sett", "lgtb"); g.chain("cmt:CastFailed", "lgtx")
    else:
        g.chain("entry", "ss", "fs"); g.chain("fs", "cks", "bhs", "as", "ams", *ws_chain); g.chain("wsput", "bfs"); g.chain("bhs:else", "bfs")
        g.chain("bfs", "mms", "cms", "sets")
        g.chain("fs:Completed", "st", "ft"); g.chain("ft", "ckt", "bht", "at", "amt", *wt_chain); g.chain("wtput", "bft"); g.chain("bht:else", "bft")
        g.chain("bft", "mmt", "cmt", "sett")
    return fn("Apply Weapon Model", [param("actor", "object:" + E_ACTOR), param("weapon", "name"), param("model", "name")], graph=g)


MISSING_COLOR = "(R=0,G=0,B=0,A=1)"   # what K2_GetVectorParameterValue answers for a parameter the material does not have


def f_material_takes_color():
    """yes = the material knows the vector parameter MainColor. A material cannot list its parameters in Blueprint, and
    the game's own helper for that (McoreFunctionLibrary.HasColorParamInMaterial) sits in a native class the mod kit does
    not have. So: build a throwaway dynamic instance (valid without a world, it lands in the transient package) and read
    MainColor off it. A fresh instance holds no overrides, so the read walks up to the material itself and answers its
    value - and for a parameter that is not there, exactly FLinearColor(0,0,0) with alpha 1 (MaterialInstanceDynamic.cpp:89).
    Writing a probe value first would prove nothing: a dynamic instance stores any name it is given.
    The one blind spot: a material whose MainColor really is opaque black reads as "no" - such a piece renders black anyway.
    K2_GetVectorParameterValue is impure and has to sit in the exec chain, or it is pruned and answers the default."""
    g = G()
    g.set("s0", "ColorProbe", inp={"ColorProbe": "false"})
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@entry.mat"}); g.branch("bv", "@iv.ReturnValue")
    g.get("gcm", "ColorMat"); g.call("fc", K_MAP, "Map_Find", inp={"TargetMap": "@gcm.ColorMat", "Key": "@entry.mat"}); g.branch("bc", "@fc.ReturnValue")
    g.set("shit", "ColorProbe", inp={"ColorProbe": "@fc.Value"})
    g.call("mid", K_MATLIB, "CreateDynamicMaterialInstance", inp={"Parent": "@entry.mat", "OptionalName": "None"})
    g.call("miv", K_SYS, "IsValid", inp={"Object": "@mid.ReturnValue"}); g.branch("bm", "@miv.ReturnValue")
    g.call("rd", E_MID, "K2_GetVectorParameterValue", inp={"self": "@mid.ReturnValue", "ParameterName": "MainColor"})
    g.call("neq", K_MATH, "NotEqual_LinearColorLinearColor", inp={"A": "@rd.ReturnValue", "B": MISSING_COLOR})
    g.set("st", "ColorProbe", inp={"ColorProbe": "@neq.ReturnValue"})
    g.get("gcm2", "ColorMat"); g.get("gcp", "ColorProbe")
    g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gcm2.ColorMat", "Key": "@entry.mat", "Value": "@gcp.ColorProbe"})
    g.get("gout", "ColorProbe"); g.link("gout.ColorProbe", "return.yes")
    g.chain("entry", "s0", "bv", "bc", "shit", "return")
    g.chain("bc:else", "mid", "bm", "rd", "st", "add", "return")
    g.chain("bm:else", "return"); g.chain("bv:else", "return")
    return fn("Material Takes Color", [param("mat", "object:/Script/Engine.MaterialInterface")], [param("yes", "bool")], graph=g)


def f_item_color_slots():
    """The colourable material slots of a piece: mesh of the ClothesTable row (a hard reference, loaded with the table)
    -> Materials -> the probe above. A slot whose name contains FixedColor stays out, the same exception the game makes
    when it wears a piece. The answer per piece is kept in ColorSlotsOf; empty means "not colourable"."""
    g = G()
    g.get("gcs", "ColorSlotsOf"); g.call("fc", K_MAP, "Map_Find", inp={"TargetMap": "@gcs.ColorSlotsOf", "Key": "@entry.name"}); g.branch("bc", "@fc.ReturnValue")
    g.set("sc", "ColorSlotsTmp", inp={"ColorSlotsTmp": "@fc.Value"})
    g.make("mk0", S_COLSLOTS); g.set("sc0", "ColorSlotsTmp", inp={"ColorSlotsTmp": "@mk0.S_ColorSlots"})
    g.n("row", "get_row", table=P_CT, inp={"RowName": "@entry.name"}, miss="ignore"); g.brk("br", P_CS, "@row.OutRow")
    g.call("mv", K_SYS, "IsValid", inp={"Object": "@br.Mesh"}); g.branch("bm", "@mv.ReturnValue")
    g.get("mats", "Materials", cls=E_SKELMESH); g.link("br.Mesh", "mats.self")
    g.foreach("fe", "@mats.Materials"); g.brk("bs", E_SKELMAT, "@fe.Array Element")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@bs.MaterialSlotName"})
    g.call("fix", K_STR, "Contains", inp={"SearchIn": "@n2s.ReturnValue", "Substring": "FixedColor", "bUseCase": "false", "bSearchFromEnd": "false"})
    g.call("nfix", K_MATH, "Not_PreBool", inp={"A": "@fix.ReturnValue"}); g.branch("bfx", "@nfix.ReturnValue")
    g.n("tc", "call_self", function="Material Takes Color", inp={"mat": "@bs.MaterialInterface"}); g.branch("bt", "@tc.yes")
    g.get("gts", "ColorSlotsTmp"); g.brk("bts", S_COLSLOTS, "@gts.ColorSlotsTmp")
    g.call("ai", K_ARR, "Array_Add", inp={"TargetArray": "@bts.Idx", "NewItem": "@fe.Array Index"})
    g.call("ac", K_ARR, "Array_Add", inp={"TargetArray": "@bts.Caption", "NewItem": "@bs.MaterialSlotName"})
    g.make("mk", S_COLSLOTS, Idx="@bts.Idx", Caption="@bts.Caption"); g.set("sts", "ColorSlotsTmp", inp={"ColorSlotsTmp": "@mk.S_ColorSlots"})
    g.get("gcs2", "ColorSlotsOf"); g.get("gts2", "ColorSlotsTmp")
    g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gcs2.ColorSlotsOf", "Key": "@entry.name", "Value": "@gts2.ColorSlotsTmp"})
    g.get("gts3", "ColorSlotsTmp"); g.link("gts3.ColorSlotsTmp", "return.slots")
    g.chain("entry", "bc", "sc", "return")
    g.chain("bc:else", "sc0", "row", "bm", "fe")
    g.chain("fe", "bfx", "tc", "bt", "ai", "ac", "sts")   # tc in the chain: an impure call outside it is pruned; make is pure and hangs on sts as data
    # no chain back to "fe": a branch that does not qualify simply ends its path, the loop carries on by itself
    g.chain("fe:Completed", "add", "return"); g.chain("bm:else", "add", "return")
    return fn("Item Color Slots", [param("name", "name")], [param("slots", "struct:" + S_COLSLOTS)], graph=g)


def f_apply_weapon_look():
    """Apply the stored choices for one weapon to its actor (not picked up yet -> nothing).

    Model first, then skin, and that order is not negotiable: setting a mesh throws away the dynamic material instance
    the skin put on the component. Skin: original = Reset Gun Paint, paint row = Change Gun Paint, skin row = dynamic
    material instance with the mod's textures on the held and the pickable mesh. A texture the mod does not ship is
    None: SetTextureParameterValue then falls back to the parent material's value."""
    g = G()
    g.get("gpl", "Player"); g.get("gws", "Weapons", cls=P_JODI); g.link("gpl.Player", "gws.self")
    g.call("fw", K_MAP, "Map_Find", inp={"TargetMap": "@gws.Weapons", "Key": "@entry.weapon"}); g.branch("bw", "@fw.ReturnValue")
    g.get("gwa", "WeaponActors"); g.call("wsa", K_MAP, "Map_Add", inp={"TargetMap": "@gwa.WeaponActors", "Key": "@entry.weapon", "Value": "@fw.Value"})   # Poll Weapons: this actor is dressed
    g.cast("cg", P_GUN, "@fw.Value", pure=False, miss="ignore")     # melee weapons are no guns: the paint calls are skipped, skins still work
    g.cast("cw", P_WEAPON, "@fw.Value", pure=False, miss="ignore")
    g.get("gmd", "WeaponModels"); g.call("fm", K_MAP, "Map_Find", inp={"TargetMap": "@gmd.WeaponModels", "Key": "@entry.weapon"})
    g.n("am", "call_self", function="Apply Weapon Model", inp={"actor": "@fw.Value", "weapon": "@entry.weapon", "model": "@fm.Value"})   # no entry -> None -> the meshes it started with
    g.get("gsel", "WeaponSkins"); g.call("fs", K_MAP, "Map_Find", inp={"TargetMap": "@gsel.WeaponSkins", "Key": "@entry.weapon"})
    # Undo AltUI's own doing first: a dynamic material instance from an earlier skin survives a skin change. Apply Weapon Model
    # would clear it, but only when it really sets another mesh - both engine setters return at once for an unchanged mesh
    # (SkinnedMeshComponent.cpp:1554, StaticMeshComponent.cpp:1757). Without this, "Original" kept the previous skin on.
    # Slot 0 only: that is the one the skin writes, so nothing else can be lost here.
    g.set("pst0", "SkinTakes", inp={"SkinTakes": "@fcon.ReturnValue"})   # forced = a skin always lands, whatever the mesh's own material knows
    g.call("rcmp", E_ACTOR, "K2_GetComponentsByClass", inp={"self": "@fw.Value", "ComponentClass": E_PRIM}); g.set("rscp", "TmpComps", inp={"TmpComps": "@rcmp.ReturnValue"})
    g.get("rgcp", "TmpComps"); g.foreach("rfc", "@rgcp.TmpComps"); g.cast("rcc", E_PRIM, "@rfc.Array Element", pure=False, miss="ignore")
    # A weapon's equipment - barrel, magazine, optics, grip - are components of their own, and the game mounts them when
    # the weapon is equipped: a component can appear long after Apply Weapon Model last ran, and then nothing was ever
    # remembered for it. So remember here too, for anything not yet known, while its materials are still untouched.
    g.get("rhm", "OrigMats"); g.call("rhas", K_MAP, "Map_Contains", inp={"TargetMap": "@rhm.OrigMats", "Key": "@rcc.AsPrimitive Component"})
    g.call("rnot", K_MATH, "Not_PreBool", inp={"A": "@rhas.ReturnValue"}); g.branch("rhb", "@rnot.ReturnValue")
    rr_chain = remember_mats(g, "rr", "@rcc.AsPrimitive Component")
    rtail = []
    for i in range(FORCE_SLOTS):   # forcing writes up to FORCE_SLOTS slots - clearing only the first left the forced material on the rest
        g.call("rm%d" % i, E_PRIM, "SetMaterial", inp={"self": "@rcc.AsPrimitive Component", "ElementIndex": str(i), "Material": "None"}); rtail.append("rm%d" % i)   # None = back to the material of the mesh itself
    # ... and while it is bare: does this material know the skin parameters at all? A dynamic instance is the only way to ask
    # (UMaterialInterface::GetTextureParameterValue is not exposed), so build one, read MainTex and drop it again. One
    # component that answers is enough - on the mod models it is the magazine, which keeps a material of the game's.
    g.chain("rfc", "rcc", "rhb"); g.chain("rhb", *rr_chain); g.chain("rrput", "rm0"); g.chain("rhb:else", "rm0")
    g.chain(*rtail)   # the probe moved behind the filling: it has to ask the material that will carry the skin
    # Now that the clearing, the probe and the game's own Reset Gun Paint are all done: whatever is still empty gets
    # back what the component carried before AltUI ever touched it. Earlier would be useless - the probe puts slot 0
    # back to None when it is finished, and Reset Gun Paint resets the weapon's materials once more. A slot left empty
    # is what the engine draws as its grey checkerboard, and a mod mesh need not bring a material for every section:
    # those sections had theirs from the component, put there by the game.
    g.get("zgcp", "TmpComps"); g.foreach("zfc", "@zgcp.TmpComps"); g.cast("zcc", E_PRIM, "@zfc.Array Element", pure=False, miss="ignore")
    g.get("zgom", "OrigMats")
    g.call("zfind", K_MAP, "Map_Find", inp={"TargetMap": "@zgom.OrigMats", "Key": "@zcc.AsPrimitive Component"})
    g.brk("zbrk", S_MATS, "@zfind.Value")
    g.call("zlen", K_ARR, "Array_Length", inp={"TargetArray": "@zbrk.Mats"})
    g.call("zlast", K_MATH, "Subtract_IntInt", inp={"A": "@zlen.ReturnValue", "B": "1"})
    g.call("zany", K_MATH, "Greater_IntInt", inp={"A": "@zlen.ReturnValue", "B": "0"})
    for i in range(FORCE_SLOTS):
        g.call("zq%d" % i, E_PRIM, "GetMaterial", inp={"self": "@zcc.AsPrimitive Component", "ElementIndex": str(i)})
        g.call("zv%d" % i, K_SYS, "IsValid", inp={"Object": "@zq%d.ReturnValue" % i})
        g.call("zn%d" % i, K_MATH, "Not_PreBool", inp={"A": "@zv%d.ReturnValue" % i}); g.branch("zb%d" % i, "@zn%d.ReturnValue" % i)
        # the game's weapon can have fewer slots than the mod's mesh - the Glock has one where the USP9 mod has five.
        # Then nothing was ever remembered for the higher slots, and the last one that was is the best answer there is:
        # it is the material the game put on this component, which is what "force the game's material" uses as well.
        g.call("zgt%d" % i, K_MATH, "Greater_IntInt", inp={"A": "@zlen.ReturnValue", "B": str(i)})
        g.call("zidx%d" % i, K_MATH, "SelectInt", inp={"A": str(i), "B": "@zlast.ReturnValue", "bPickA": "@zgt%d.ReturnValue" % i})
        g.call("zan%d" % i, K_MATH, "BooleanAND", inp={"A": "@zany.ReturnValue", "B": "@zfind.ReturnValue"})
        g.branch("zbb%d" % i, "@zan%d.ReturnValue" % i)
        g.call("zget%d" % i, K_ARR, "Array_Get", inp={"TargetArray": "@zbrk.Mats", "Index": "@zidx%d.ReturnValue" % i})
        g.call("zset%d" % i, E_PRIM, "SetMaterial", inp={"self": "@zcc.AsPrimitive Component", "ElementIndex": str(i), "Material": "@zget%d.Item" % i})
        znxt = ["zb%d" % (i + 1)] if i + 1 < FORCE_SLOTS else ["zpdm"]
        g.chain("zb%d" % i, "zbb%d" % i); g.chain("zb%d:else" % i, *znxt)      # not empty: leave the mod's own material alone
        g.chain("zbb%d" % i, "zset%d" % i, *znxt); g.chain("zbb%d:else" % i, *znxt)   # empty, and one was remembered: put it back
    # the probe belongs here, not before the filling: it asks whether the material of slot 0 knows the skin parameters,
    # and the answer decides whether the skin tiles are shown dimmed. Asked too early it looks at the mod's own material
    # while the skin later lands on the one just put back - the tile then said "does nothing" about a skin that works.
    g.call("zprev", E_PRIM, "GetMaterial", inp={"self": "@zcc.AsPrimitive Component", "ElementIndex": "0"})
    g.call("zpdm", E_PRIM, "CreateDynamicMaterialInstance", inp={"self": "@zcc.AsPrimitive Component", "ElementIndex": "0", "SourceMaterial": "None", "OptionalName": "None"})
    g.call("zptx", E_MID, "K2_GetTextureParameterValue", inp={"self": "@zpdm.ReturnValue", "ParameterName": "MainTex"})
    g.call("zpvl", K_SYS, "IsValid", inp={"Object": "@zptx.ReturnValue"}); g.branch("zpbv", "@zpvl.ReturnValue")
    g.set("zpst", "SkinTakes", inp={"SkinTakes": "true"})
    g.call("zpdrop", E_PRIM, "SetMaterial", inp={"self": "@zcc.AsPrimitive Component", "ElementIndex": "0", "Material": "@zprev.ReturnValue"})   # the probe instance goes, the filled material stays
    g.chain("zfc", "zcc", "zb0"); g.chain("zpdm", "zptx", "zpbv", "zpst", "zpdrop"); g.chain("zpbv:else", "zpdrop")
    g.call("cp0", P_GUN, "Change Gun Paint", inp={"self": "@cg.AsWeapon_Gun_Base", "paint name": "None"})   # always start from the original
    g.call("rp0", P_GUN, "Reset Gun Paint", inp={"self": "@cg.AsWeapon_Gun_Base"})
    g.branch("bs", "@fs.ReturnValue")
    g.n("sm", "call_self", function="Skin Mod", inp={"row": "@fs.Value"}); g.branch("bsk", "@sm.found")
    g.call("cp1", P_GUN, "Change Gun Paint", inp={"self": "@cg.AsWeapon_Gun_Base", "paint name": "@fs.Value"})   # paint row
    g.n("sr", "call_self", function="Skin Row", inp={"row": "@fs.Value"}); g.brk("sb", ws.STRUCT_PATH, "@sr.skin")   # skin row
    # every mesh component of the weapon (held skeletal mesh, pickable static mesh): dynamic material instance on slot 0 with the skin's textures
    g.call("cmp", E_ACTOR, "K2_GetComponentsByClass", inp={"self": "@fw.Value", "ComponentClass": E_PRIM}); g.set("scp", "TmpComps", inp={"TmpComps": "@cmp.ReturnValue"})
    g.get("gcp", "TmpComps"); g.foreach("fc", "@gcp.TmpComps"); g.cast("cc", E_PRIM, "@fc.Array Element", pure=False, miss="ignore")
    # "force the game's material" (tile menu, per model): a mod mesh brings its own materials, and those know none of the
    # three parameters - so the skin does nothing on them. Forced, the instance is built from the material the component had
    # before any model was put on it (OrigMat), and on every slot instead of only the first.
    g.get("gfsk", "ForceSkin"); g.call("fcon", K_ARR, "Array_Contains", inp={"TargetArray": "@gfsk.ForceSkin", "ItemToFind": "@fm.Value"})
    g.branch("bforce", "@fcon.ReturnValue")
    g.get("gom", "OrigMat"); g.call("fom", K_MAP, "Map_Find", inp={"TargetMap": "@gom.OrigMat", "Key": "@cc.AsPrimitive Component"})
    g.call("fnm", E_PRIM, "GetNumMaterials", inp={"self": "@cc.AsPrimitive Component"})
    for i in range(FORCE_SLOTS):
        g.call("fgt%d" % i, K_MATH, "Greater_IntInt", inp={"A": "@fnm.ReturnValue", "B": str(i)}); g.branch("fb%d" % i, "@fgt%d.ReturnValue" % i)
        g.call("fdm%d" % i, E_PRIM, "CreateDynamicMaterialInstance", inp={"self": "@cc.AsPrimitive Component", "ElementIndex": str(i), "SourceMaterial": "@fom.Value", "OptionalName": "None"})
        nxt = ["fb%d" % (i + 1)] if i + 1 < FORCE_SLOTS else []
        g.chain("fb%d" % i, "fdm%d" % i, skin_tex(g, "ftx%d_" % i, "@fdm%d.ReturnValue" % i, nxt))
        if nxt: g.chain("fb%d:else" % i, *nxt)
    g.call("dm", E_PRIM, "CreateDynamicMaterialInstance", inp={"self": "@cc.AsPrimitive Component", "ElementIndex": "0", "SourceMaterial": "None", "OptionalName": "None"})
    tail = ["dm", skin_tex(g, "tx", "@dm.ReturnValue", [])]
    # the magazine is a component of its own (Gun_Mag_Comp_C): with "leave the magazine out" it is skipped while forcing,
    # because the game's own paints do not colour it either. Without forcing it takes the skin as before.
    for i, (part, cls, arr, _, _, _) in enumerate(WEAPON_PARTS):
        g.cast("pcc%d" % i, cls, "@cc.AsPrimitive Component", pure=False, miss="ignore")
        g.get("gsk%d" % i, arr); g.call("skc%d" % i, K_ARR, "Array_Contains", inp={"TargetArray": "@gsk%d.%s" % (i, arr), "ItemToFind": "@fm.Value"})
        g.call("ska%d" % i, K_MATH, "BooleanAND", inp={"A": "@skc%d.ReturnValue" % i, "B": "@fcon.ReturnValue"})
        g.call("skn%d" % i, K_MATH, "Not_PreBool", inp={"A": "@ska%d.ReturnValue" % i}); g.branch("bpk%d" % i, "@skn%d.ReturnValue" % i)
        nxt = "pcc%d" % (i + 1) if i + 1 < len(WEAPON_PARTS) else "bforce"
        g.chain("pcc%d" % i, "bpk%d" % i); g.chain("bpk%d" % i, "bforce")   # it is this part and stays in: apply
        g.chain("pcc%d:CastFailed" % i, nxt)                                 # not this part: ask the next one
    g.chain("fc", "cc", "pcc0")
    g.chain("bforce", "fb0"); g.chain("bforce:else", *tail)
    if WEAPONLOG:
        log(g, "w", ["look ", nstr(g, "w", "@entry.weapon"), " stored model=", nstr(g, "wm", "@fm.Value"),
                     " found=", boolstr(g, "w", "@fm.ReturnValue")])
        g.chain("entry", "bw", "wsa", "cg", "cw", "lgw", "am", "pst0", "rscp", "rfc")
    else:
        g.chain("entry", "bw", "wsa", "cg", "cw", "am", "pst0", "rscp", "rfc")   # Skin Mod and K2_GetComponentsByClass are pure: not in the chain
    g.chain("rfc:Completed", "cp0", "rp0", "zfc"); g.chain("zfc:Completed", "bs", "bsk", "sr", "scp", "fc")
    g.n("qrow", "get_row", table=P_PAINT_T, inp={"RowName": "@fs.Value"}, miss="ignore"); g.brk("qbr", P_PAINT_S, "@qrow.OutRow")
    g.call("qfm", K_MAP, "Map_Find", inp={"TargetMap": "@qbr.Guns", "Key": "@entry.weapon"})
    g.call("qon", K_MATH, "BooleanAND", inp={"A": "@fcon.ReturnValue", "B": "@qfm.ReturnValue"}); g.branch("qbf", "@qon.ReturnValue")
    g.get("qgcp", "TmpComps"); g.foreach("qfc", "@qgcp.TmpComps"); g.cast("qcc", E_PRIM, "@qfc.Array Element", pure=False, miss="ignore")
    g.call("qnm", E_PRIM, "GetNumMaterials", inp={"self": "@qcc.AsPrimitive Component"})
    for i in range(FORCE_SLOTS):
        g.call("qgt%d" % i, K_MATH, "Greater_IntInt", inp={"A": "@qnm.ReturnValue", "B": str(i)}); g.branch("qb%d" % i, "@qgt%d.ReturnValue" % i)
        g.call("qsm%d" % i, E_PRIM, "SetMaterial", inp={"self": "@qcc.AsPrimitive Component", "ElementIndex": str(i), "Material": "@qfm.Value"})
        nxt = ["qb%d" % (i + 1)] if i + 1 < FORCE_SLOTS else []
        g.chain("qb%d" % i, "qsm%d" % i, *nxt)
        if nxt: g.chain("qb%d:else" % i, *nxt)
    g.chain("bsk:else", "cp1", "qrow", "qbf", "qfc"); g.chain("qrow:Row Not Found", "qbf")
    for i, (part, cls, arr, _, _, _) in enumerate(WEAPON_PARTS):
        g.cast("qp%d" % i, cls, "@qcc.AsPrimitive Component", pure=False, miss="ignore"); g.branch("qbp%d" % i, "@skn%d.ReturnValue" % i)
        nxt = "qp%d" % (i + 1) if i + 1 < len(WEAPON_PARTS) else "qb0"
        g.chain("qp%d" % i, "qbp%d" % i); g.chain("qbp%d" % i, "qb0"); g.chain("qp%d:CastFailed" % i, nxt)
    g.chain("qfc", "qcc", "qp0")
    return fn("Apply Weapon Look", [param("weapon", "name")], graph=g)


def f_apply_all_weapon_looks():
    g = G(); g.n("wr", "call_self", function="Weapon Rows"); g.set("sw", "TmpNames", inp={"TmpNames": "@wr.rows"})
    g.get("gw", "TmpNames"); g.foreach("fe", "@gw.TmpNames")
    g.n("ap", "call_self", function="Apply Weapon Look", inp={"weapon": "@fe.Array Element"})
    g.chain("entry", "wr", "sw", "fe"); g.chain("fe", "ap")
    return fn("Apply All Weapon Looks", graph=g)


def f_poll_weapons():
    """Weapon actors appear when Jodi picks a weapon up, and a new one replaces the old when a weapon comes back out of the storage
    box (Got A Gun -> Create a Gun builds it from the stored Gun Data: the game's paint is in there, AltUI's skin and model are not).
    Compared per weapon with the actor Apply Weapon Look last dressed (WeaponActors): counting the map missed a weapon put in and
    taken out again while the box was open - same count, new actor."""
    g = G(); g.get("gpl", "Player"); g.get("gws", "Weapons", cls=P_JODI); g.link("gpl.Player", "gws.self")
    g.call("keys", K_MAP, "Map_Keys", inp={"TargetMap": "@gws.Weapons"}); g.set("sk", "WeaponPollKeys", inp={"WeaponPollKeys": "@keys.Keys"})   # own loop array: Apply Weapon Look fills TmpNames-style arrays
    g.get("gk", "WeaponPollKeys"); g.foreach("fe", "@gk.WeaponPollKeys")
    g.get("gpl2", "Player"); g.get("gws2", "Weapons", cls=P_JODI); g.link("gpl2.Player", "gws2.self")
    g.call("fa", K_MAP, "Map_Find", inp={"TargetMap": "@gws2.Weapons", "Key": "@fe.Array Element"})
    g.get("gwa", "WeaponActors"); g.call("fs", K_MAP, "Map_Find", inp={"TargetMap": "@gwa.WeaponActors", "Key": "@fe.Array Element"})
    g.call("eq", K_MATH, "EqualEqual_ObjectObject", inp={"A": "@fa.Value", "B": "@fs.Value"}); g.call("ne", K_MATH, "Not_PreBool", inp={"A": "@eq.ReturnValue"}); g.branch("b", "@ne.ReturnValue")
    g.n("ap", "call_self", function="Apply Weapon Look", inp={"weapon": "@fe.Array Element"})
    g.chain("entry", "keys", "sk", "fe"); g.chain("fe", "b", "ap")
    return fn("Poll Weapons", graph=g)


def f_select_weapon():
    """Left column of the weapons tab: pick a weapon, redraw chips and tiles."""
    g = G(); g.set("s", "CurrentWeapon", inp={"CurrentWeapon": "@entry.name"}); g.set("sg", "SkinGroup", inp={"SkinGroup": "None"})
    g.n("rw", "call_self", function="Rebuild Weapons"); g.n("rm", "call_self", function="Rebuild Weapon Models")
    g.n("rs", "call_self", function="Rebuild Weapon Skins"); g.n("rc", "call_self", function="Rebuild Weapon Chips")
    g.chain("entry", "s", "sg", "rw", "rm", "rs", "rc")   # chips last: Skin Groups reads the row lists the two rebuilds fill
    return fn("Select Weapon", [param("name", "name")], graph=g)


def f_weapon_skin_clicked():
    """Tile click: store the choice for the current weapon (None = original -> remove the entry), save, apply, redraw."""
    g = G(); g.get("gcw", "CurrentWeapon"); g.get("gm", "WeaponSkins")
    g.call("isn", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "None"}); g.branch("b", "@isn.ReturnValue")
    g.call("rm", K_MAP, "Map_Remove", inp={"TargetMap": "@gm.WeaponSkins", "Key": "@gcw.CurrentWeapon"})
    g.get("gm2", "WeaponSkins"); g.get("gcw2", "CurrentWeapon"); g.call("ad", K_MAP, "Map_Add", inp={"TargetMap": "@gm2.WeaponSkins", "Key": "@gcw2.CurrentWeapon", "Value": "@entry.name"})
    g.n("sv", "call_self", function="Save Settings"); g.get("gcw3", "CurrentWeapon"); g.n("ap", "call_self", function="Apply Weapon Look", inp={"weapon": "@gcw3.CurrentWeapon"})
    g.n("rs", "call_self", function="Rebuild Weapon Skins"); g.n("rmo", "call_self", function="Rebuild Weapon Models")
    g.chain("entry", "b", "rm", "sv"); g.chain("b:else", "ad", "sv"); g.chain("sv", "ap", "rs", "rmo")
    return fn("Weapon Skin Clicked", [param("name", "name")], graph=g)


def f_weapon_count_text():
    """Line under a weapon in the left column: "<m> models, <s> skins" (every tile, "Original" included); with a search or a chip
    the hits in brackets after each number, like the other tabs ("4 (1) ..."), from the same filters as the tiles (Model / Skin Row Passes)."""
    g = G()
    g.get("gst", "WeaponSearchText"); g.call("se", K_STR, "IsEmpty", inp={"InString": "@gst.WeaponSearchText"}); g.call("sne", K_MATH, "Not_PreBool", inp={"A": "@se.ReturnValue"})
    g.get("gsg", "SkinGroup"); g.call("cn", K_MATH, "NotEqual_NameName", inp={"A": "@gsg.SkinGroup", "B": "None"}); g.call("fa", K_MATH, "BooleanOR", inp={"A": "@sne.ReturnValue", "B": "@cn.ReturnValue"})
    g.set("fa0", "WCntFilter", inp={"WCntFilter": "@fa.ReturnValue"}); g.chain("entry", "fa0")
    tail = ["fa0"]
    for kind, rows_fn, pass_fn in (("m", "Models For Weapon", "Model Row Passes"), ("s", "Skins For Weapon", "Skin Row Passes")):
        p = "c" + kind
        g.n(p + "r", "call_self", function=rows_fn, inp={"weapon": "@entry.weapon"}); g.set(p + "sr", "WCntRows", inp={"WCntRows": "@%sr.rows" % p})
        g.set(p + "z0", "WCntAll", inp={"WCntAll": "0"}); g.set(p + "z1", "WCntHit", inp={"WCntHit": "0"})
        g.get(p + "gr", "WCntRows"); g.foreach(p + "fe", "@%sgr.WCntRows" % p)
        g.get(p + "ga", "WCntAll"); g.call(p + "ia", K_MATH, "Add_IntInt", inp={"A": "@%sga.WCntAll" % p, "B": "1"}); g.set(p + "sa", "WCntAll", inp={"WCntAll": "@%sia.ReturnValue" % p})
        g.n(p + "ps", "call_self", function=pass_fn, inp={"row": "@%sfe.Array Element" % p}); g.branch(p + "bp", "@%sps.yes" % p)
        g.get(p + "gh", "WCntHit"); g.call(p + "ih", K_MATH, "Add_IntInt", inp={"A": "@%sgh.WCntHit" % p, "B": "1"}); g.set(p + "sh", "WCntHit", inp={"WCntHit": "@%sih.ReturnValue" % p})
        g.chain(p + "fe", p + "sa", p + "ps", p + "bp", p + "sh")   # every tile, "Original" included: the numbers match what the tab shows
        # "<all>" or "<all> (<hits>)"
        g.get(p + "ga2", "WCntAll"); g.call(p + "as", K_STR, "Conv_IntToString", inp={"InInt": "@%sga2.WCntAll" % p})
        g.get(p + "gh2", "WCntHit"); g.call(p + "hs", K_STR, "Conv_IntToString", inp={"InInt": "@%sgh2.WCntHit" % p})
        g.call(p + "c1", K_STR, "Concat_StrStr", inp={"A": "@%sas.ReturnValue" % p, "B": " ("}); g.call(p + "c2", K_STR, "Concat_StrStr", inp={"A": "@%sc1.ReturnValue" % p, "B": "@%shs.ReturnValue" % p})
        g.call(p + "c3", K_STR, "Concat_StrStr", inp={"A": "@%sc2.ReturnValue" % p, "B": ")"}); g.get(p + "gf", "WCntFilter")
        g.call(p + "sel", K_MATH, "SelectString", inp={"A": "@%sc3.ReturnValue" % p, "B": "@%sas.ReturnValue" % p, "bPickA": "@%sgf.WCntFilter" % p})
        g.set(p + "out", "WCnt" + kind.upper(), inp={"WCnt" + kind.upper(): "@%ssel.ReturnValue" % p})
        g.chain(tail[-1], p + "r", p + "sr", p + "z0", p + "z1", p + "fe"); g.chain(p + "fe:Completed", p + "out"); tail = [p + "out"]
    g.call("tpl", K_STR, "Replace", inp={"SourceString": ts(g, "tw", "Lbl_WeaponCount"), "From": "<m>", "To": "@gwm.WCntM", "SearchCase": "CaseSensitive"}); g.get("gwm", "WCntM")
    g.get("gws", "WCntS"); g.call("tpl2", K_STR, "Replace", inp={"SourceString": "@tpl.ReturnValue", "From": "<s>", "To": "@gws.WCntS", "SearchCase": "CaseSensitive"})
    g.call("tt", K_TXT, "Conv_StringToText", inp={"InString": "@tpl2.ReturnValue"}); g.link("tt.ReturnValue", "return.text")
    g.chain(tail[-1], "return")
    return fn("Weapon Count Text", [param("weapon", "name")], [param("text", "text")], graph=g)


def f_rebuild_weapons():
    """Left column: one W_SlotTab per weapon (item icon, caption, number of skins), the current one selected."""
    g = G(); g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Weapon Cats", inp={"self": "@gp.Panel"})
    g.n("wr", "call_self", function="Weapon Rows"); g.set("sw", "TmpNames", inp={"TmpNames": "@wr.rows"})
    g.get("gw", "TmpNames"); g.foreach("fe", "@gw.TmpNames")
    g.n("row", "get_row", table=P_ITEM_T, inp={"RowName": "@fe.Array Element"}, miss="ignore"); g.brk("br", P_ITEM_S, "@row.OutRow")
    g.n("sk", "call_self", function="Skins For Weapon", inp={"weapon": "@fe.Array Element"}); g.call("cnt", K_ARR, "Array_Length", inp={"TargetArray": "@sk.rows"})
    g.get("gcw", "CurrentWeapon"); g.call("sel", K_MATH, "EqualEqual_NameName", inp={"A": "@fe.Array Element", "B": "@gcw.CurrentWeapon"})
    tw = create_widget(g, "ct", W_TAB); set_manager(g, "smt", W_TAB, tw)
    g.call("ti", W_TAB, "Init", inp={"self": tw, "slot": "@fe.Array Element", "caption": "@br.Caption", "count": "@cnt.ReturnValue", "worn icon": "@br.Icon",
                                     "selected": "@sel.ReturnValue", "has items": "true", "filtered": "-1", "indent": "false"})
    g.get("gp3", "Panel"); g.call("at", W_PANEL, "Add Weapon Cat", inp={"self": "@gp3.Panel", "widget": tw})
    g.n("wct", "call_self", function="Weapon Count Text", inp={"weapon": "@fe.Array Element"}); g.call("sct", W_TAB, "Set Count Text", inp={"self": tw, "text": "@wct.text"})
    g.chain("entry", "cl", "wr", "sw", "fe"); g.chain("fe", "row", "sk", "ct_cr", "smt", "ti", "at", "wct", "sct")
    return fn("Rebuild Weapons", graph=g)


def f_rebuild_weapon_skins():
    """Tiles of the selected weapon: original + paints + skin mods; favourites block first, filters like the appearance page."""
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Weapon Skins", inp={"self": "@gp.Panel"})
    g.get("gpf", "Panel"); g.call("clf", W_PANEL, "Clear Weapon Skin Fav", inp={"self": "@gpf.Panel"})
    g.get("gcw", "CurrentWeapon"); g.n("sk", "call_self", function="Skins For Weapon", inp={"weapon": "@gcw.CurrentWeapon"})
    g.set("nf", "TmpIdx", inp={"TmpIdx": "0"}); g.set("nmiss", "TmpName3", inp={"TmpName3": "None"})   # first tile without a rendered picture
    g.get("gr1", "SkinRows"); g.foreach("ff", "@gr1.SkinRows")
    g.n("pf", "call_self", function="Skin Row Passes", inp={"row": "@ff.Array Element"}); g.n("ffv", "call_self", function="Is Skin Favorite", inp={"name": "@ff.Array Element"})
    g.call("fok", K_MATH, "BooleanAND", inp={"A": "@pf.yes", "B": "@ffv.yes"}); g.branch("bf", "@fok.ReturnValue")
    t1 = skin_tile(g, "f", "@ff.Array Element", "Add Weapon Skin Fav", "true")
    g.get("gn", "TmpIdx"); g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gn.TmpIdx", "B": "1"}); g.set("sn", "TmpIdx", inp={"TmpIdx": "@inc.ReturnValue"})
    g.get("gn2", "TmpIdx"); g.call("gt0", K_MATH, "Greater_IntInt", inp={"A": "@gn2.TmpIdx", "B": "0"}); g.get("gp5", "Panel"); g.call("sfv", W_PANEL, "Set Weapon Fav Visible", inp={"self": "@gp5.Panel", "visible": "@gt0.ReturnValue"})
    g.get("gr2", "SkinRows"); g.foreach("fe", "@gr2.SkinRows")
    g.n("pe", "call_self", function="Skin Row Passes", inp={"row": "@fe.Array Element"}); g.branch("be", "@pe.yes")
    g.n("efv", "call_self", function="Is Skin Favorite", inp={"name": "@fe.Array Element"})
    t2 = skin_tile(g, "a", "@fe.Array Element", "Add Weapon Skin", "@efv.yes")
    g.get("gcw3", "CurrentWeapon"); g.n("cm2", "call_self", function="Current Model")
    g.n("wi2", "call_self", function="Weapon Icon", inp={"weapon": "@gcw3.CurrentWeapon", "model": "@cm2.model", "skin": "@fe.Array Element"})
    g.get("gnm", "TmpName3"); g.call("nset", K_MATH, "EqualEqual_NameName", inp={"A": "@gnm.TmpName3", "B": "None"})
    g.call("want", K_MATH, "BooleanAND", inp={"A": "@wi2.missing", "B": "@nset.ReturnValue"}); g.branch("bwant", "@want.ReturnValue")
    g.set("smiss", "TmpName3", inp={"TmpName3": "@fe.Array Element"})
    g.chain("entry", "cl", "clf", "sk", "nf", "nmiss", "ff"); g.chain("ff", "pf", "bf", "sn", *t1)   # Weapon Icon is impure: it sits in the pass-2 chain below
    # one rendering per rebuild (Capture Photo is serial); Finish Photo redraws, so the pictures fill in one after another
    g.get("gnm2", "TmpName3"); g.call("has", K_MATH, "NotEqual_NameName", inp={"A": "@gnm2.TmpName3", "B": "None"})
    g.get("gcm", "CamMode"); g.call("cam0", K_MATH, "EqualEqual_IntInt", inp={"A": "@gcm.CamMode", "B": "0"})
    g.get("gia", "IconWeaponActor"); g.call("busy", K_SYS, "IsValid", inp={"Object": "@gia.IconWeaponActor"}); g.call("free", K_MATH, "Not_PreBool", inp={"A": "@busy.ReturnValue"})
    g.call("c1", K_MATH, "BooleanAND", inp={"A": "@has.ReturnValue", "B": "@cam0.ReturnValue"}); g.call("cok", K_MATH, "BooleanAND", inp={"A": "@c1.ReturnValue", "B": "@free.ReturnValue"})
    g.get("gpgw", "Page"); g.call("ispw", K_MATH, "EqualEqual_NameName", inp={"A": "@gpgw.Page", "B": "Weapons"})   # the chain of renderings stops when the page is left
    g.call("cok2", K_MATH, "BooleanAND", inp={"A": "@cok.ReturnValue", "B": "@ispw.ReturnValue"}); g.branch("bcap", "@cok2.ReturnValue")
    g.get("gcw4", "CurrentWeapon"); g.get("gnm3", "TmpName3"); g.n("cm3", "call_self", function="Current Model")
    g.n("cap", "call_self", function="Capture Weapon Icon", inp={"weapon": "@gcw4.CurrentWeapon", "model": "@cm3.model", "skin": "@gnm3.TmpName3"})
    g.chain("ff:Completed", "sfv", "fe"); g.chain("fe", "pe", "be", *t2, "wi2", "bwant", "smiss")   # Is Skin Favorite is pure
    g.chain("fe:Completed", "bcap", "cap")
    return fn("Rebuild Weapon Skins", graph=g)


def skin_tile(g, p, row_pin, add_fn, fav_pin):
    """Tile of one skin row: caption (original / paint name / skin caption), icon (skin icon, else the weapon's item icon),
    highlighted when it is the stored choice."""
    g.n(p + "cap", "call_self", function="Skin Caption", inp={"row": row_pin}); g.n(p + "ic", "call_self", function="Skin Icon", inp={"row": row_pin})
    g.make(p + "mi", S_ITEM, Name=row_pin, DisplayName="@%scap.s" % p, Icon="@%sic.tex" % p)
    g.get(p + "gm", "WeaponSkins"); g.get(p + "gcw", "CurrentWeapon")
    g.call(p + "fs", K_MAP, "Map_Find", inp={"TargetMap": "@%sgm.WeaponSkins" % p, "Key": "@%sgcw.CurrentWeapon" % p})
    g.call(p + "eq", K_MATH, "EqualEqual_NameName", inp={"A": "@%sfs.Value" % p, "B": row_pin})
    g.call(p + "isn", K_MATH, "EqualEqual_NameName", inp={"A": row_pin, "B": "None"}); g.call(p + "nf", K_MATH, "Not_PreBool", inp={"A": "@%sfs.ReturnValue" % p})
    g.call(p + "orig", K_MATH, "BooleanAND", inp={"A": "@%sisn.ReturnValue" % p, "B": "@%snf.ReturnValue" % p})
    g.call(p + "sel", K_MATH, "BooleanOR", inp={"A": "@%seq.ReturnValue" % p, "B": "@%sorig.ReturnValue" % p})
    g.get(p + "gst", "SkinTakes"); g.call(p + "nst", K_MATH, "Not_PreBool", inp={"A": "@%sgst.SkinTakes" % p})
    g.n(p + "smd", "call_self", function="Skin Mod", inp={"row": row_pin})   # paints are not dimmed: Change Gun Paint is the game's own way and works on every model
    g.call(p + "dim", K_MATH, "BooleanAND", inp={"A": "@%snst.ReturnValue" % p, "B": "@%ssmd.found" % p})
    return [p + "cap", p + "ic"] + look_tile(g, p + "t", "@%smi.S_ClothesItem" % p, "@%ssel.ReturnValue" % p, "true", add_fn, tt(g, p + "tip", "Tab_Weapons"),
                                             kind="skin", fav_pin=fav_pin, dim_pin="@%sdim.ReturnValue" % p)


def f_current_model():
    g = G(); g.get("gm", "WeaponModels"); g.get("gcw", "CurrentWeapon")
    g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gm.WeaponModels", "Key": "@gcw.CurrentWeapon"}); g.link("f.Value", "return.model")
    return fn("Current Model", outputs=[param("model", "name")], graph=g, pure=True)


def f_current_skin():
    g = G(); g.get("gm", "WeaponSkins"); g.get("gcw", "CurrentWeapon")
    g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gm.WeaponSkins", "Key": "@gcw.CurrentWeapon"}); g.link("f.Value", "return.skin")
    return fn("Current Skin", outputs=[param("skin", "name")], graph=g, pure=True)


def f_model_row():
    """Row of a model mod's table (caption / icon); invalid row -> empty struct."""
    g = G(); g.n("md", "call_self", function="Model Mod", inp={"row": "@entry.row"}); g.branch("b", "@md.found")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@md.mod"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "/Game/Mod/", "B": "@n2s.ReturnValue"})
    g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "/%s.%s" % (ws.MODEL_TABLE_NAME, ws.MODEL_TABLE_NAME)})
    g.call("sp", K_SYS, "MakeSoftObjectPath", inp={"PathString": "@c2.ReturnValue"}); g.call("sr", K_SYS, "Conv_SoftObjPathToSoftObjRef", inp={"SoftObjectPath": "@sp.ReturnValue"})
    g.call("ld", K_SYS, "LoadAsset_Blocking", inp={"Asset": "@sr.ReturnValue"}); g.cast("ck", E_DATATABLE, "@ld.ReturnValue", pure=False)
    g.n("row", "get_row", inp={"DataTable": "@ck.AsData Table", "RowName": "@entry.row"}, miss="ignore"); g.brk("br", ws.MODEL_STRUCT_PATH, "@row.OutRow")
    g.set("st", "TmpModel", inp={"TmpModel": "@row.OutRow"}); g.get("gt", "TmpModel"); g.link("gt.TmpModel", "return.model")
    g.chain("entry", "b", "ld", "ck", "row", "st", "return"); g.chain("b:else", "return"); g.chain("ck:CastFailed", "return"); g.chain("row:Row Not Found", "return")
    return fn("Model Row", [param("row", "name")], [param("model", "struct:" + ws.MODEL_STRUCT_PATH)], graph=g)


def f_model_caption():
    """Tile caption: "Original" for None, else the model's Caption, else its row name."""
    g = G(); g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"}); g.set("s0", "TmpStr", inp={"TmpStr": "@n2s.ReturnValue"})
    g.call("isn", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.row", "B": "None"}); g.branch("bn", "@isn.ReturnValue")
    g.call("ots", K_TXT, "Conv_TextToString", inp={"InText": tt(g, "ot", "Skin_Original")}); g.set("s1", "TmpStr", inp={"TmpStr": "@ots.ReturnValue"})
    g.n("mr", "call_self", function="Model Row", inp={"row": "@entry.row"}); g.brk("mb", ws.MODEL_STRUCT_PATH, "@mr.model")
    g.call("te", K_TXT, "TextIsEmpty", inp={"InText": "@mb.Caption"}); g.branch("be", "@te.ReturnValue")
    g.call("cs", K_TXT, "Conv_TextToString", inp={"InText": "@mb.Caption"}); g.set("s2", "TmpStr", inp={"TmpStr": "@cs.ReturnValue"})
    g.get("gs", "TmpStr"); g.link("gs.TmpStr", "return.s")
    g.chain("entry", "s0", "bn", "s1", "return"); g.chain("bn:else", "mr", "be", "return"); g.chain("be:else", "s2", "return")
    return fn("Model Caption", [param("row", "name")], [param("s", "string")], graph=g)


def f_model_icon():
    """Tile icon: the rendered picture of this weapon with this model and the chosen skin, else the mod's own icon,
    else the weapon's item icon."""
    g = G(); g.get("gcw", "CurrentWeapon"); g.n("wrow", "get_row", table=P_ITEM_T, inp={"RowName": "@gcw.CurrentWeapon"}, miss="ignore"); g.brk("wbr", P_ITEM_S, "@wrow.OutRow")
    g.set("s0", "TmpTex", inp={"TmpTex": "@wbr.Icon"})
    # chosen in the tile menu: show the picture the mod brings instead of the rendered one
    g.get("gio", "IconOwn"); g.call("own", K_ARR, "Array_Contains", inp={"TargetArray": "@gio.IconOwn", "ItemToFind": "@entry.row"})
    g.get("gmi", "ModelIconOf"); g.call("fmi", K_MAP, "Map_Find", inp={"TargetMap": "@gmi.ModelIconOf", "Key": "@entry.row"})
    g.call("miv", K_SYS, "IsValid", inp={"Object": "@fmi.Value"}); g.call("useown", K_MATH, "BooleanAND", inp={"A": "@own.ReturnValue", "B": "@miv.ReturnValue"})
    g.branch("bown", "@useown.ReturnValue"); g.set("sown", "TmpTex", inp={"TmpTex": "@fmi.Value"})
    g.get("gcw2", "CurrentWeapon"); g.n("cs", "call_self", function="Current Skin")
    g.n("ric", "call_self", function="Weapon Icon", inp={"weapon": "@gcw2.CurrentWeapon", "model": "@entry.row", "skin": "@cs.skin"})
    g.call("rv", K_SYS, "IsValid", inp={"Object": "@ric.tex"}); g.branch("brd", "@rv.ReturnValue"); g.set("srd", "TmpTex", inp={"TmpTex": "@ric.tex"})
    g.n("mm", "call_self", function="Model Mod", inp={"row": "@entry.row"}); g.branch("bs", "@mm.found")
    g.n("mr", "call_self", function="Model Row", inp={"row": "@entry.row"}); g.brk("mb", ws.MODEL_STRUCT_PATH, "@mr.model")
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@mb.Icon"}); g.branch("bi", "@iv.ReturnValue"); g.set("s1", "TmpTex", inp={"TmpTex": "@mb.Icon"})
    g.get("gt", "TmpTex"); g.link("gt.TmpTex", "return.tex")
    g.chain("entry", "wrow", "s0", "bown", "sown", "return"); g.chain("wrow:Row Not Found", "bown"); g.chain("bown:else", "ric", "brd", "srd", "return")
    g.chain("brd:else", "bs"); g.chain("bs", "mr", "bi", "s1", "return"); g.chain("bi:else", "return"); g.chain("bs:else", "return")
    return fn("Model Icon", [param("row", "name")], [param("tex", "object:" + E_TEX2D)], graph=g)


def f_model_key():
    g = G(); g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"}); g.call("cc", K_STR, "Concat_StrStr", inp={"A": "model:", "B": "@n2s.ReturnValue"})
    g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@cc.ReturnValue"}); g.link("s2n.ReturnValue", "return.key")
    return fn("Model Key", [param("row", "name")], [param("key", "name")], graph=g, pure=True)


def f_is_model_favorite():
    g = G(); g.n("k", "call_self", function="Model Key", inp={"row": "@entry.name"}); g.n("f", "call_self", function="Is Favorite", inp={"name": "@k.key"}); g.link("f.yes", "return.yes")
    return fn("Is Model Favorite", [param("name", "name")], [param("yes", "bool")], graph=g, pure=True)


def f_model_has_icon():
    """True when the model mod ships a picture of its own. Only then does the tile menu offer to show it instead of
    the rendering - read from the map the scan filled, so the menu needs no table load."""
    g = G(); g.get("gm", "ModelIconOf"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gm.ModelIconOf", "Key": "@entry.row"})
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@f.Value"})
    g.call("a", K_MATH, "BooleanAND", inp={"A": "@f.ReturnValue", "B": "@iv.ReturnValue"}); g.link("a.ReturnValue", "return.found")
    return fn("Model Has Icon", [param("row", "name")], [param("found", "bool")], graph=g, pure=True)


def f_toggle_model_own_icon():
    """Tile menu: this model shows the picture its mod brings instead of the rendered one, or back."""
    g = G(); g.get("gi", "IconOwn"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gi.IconOwn", "ItemToFind": "@entry.name"}); g.branch("b", "@has.ReturnValue")
    g.get("gi1", "IconOwn"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gi1.IconOwn", "Item": "@entry.name"})
    g.get("gi2", "IconOwn"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gi2.IconOwn", "NewItem": "@entry.name"})
    g.n("sv", "call_self", function="Save Settings"); g.n("rl", "call_self", function="Rebuild Weapon Models")
    g.chain("entry", "b", "rm", "sv"); g.chain("b:else", "add", "sv"); g.chain("sv", "rl")
    return fn("Toggle Model Own Icon", [param("name", "name")], graph=g)


def f_model_forced():
    """True when this model is set to force the game's material - only then does the magazine option make sense."""
    g = G(); g.get("gf", "ForceSkin"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gf.ForceSkin", "ItemToFind": "@entry.row"})
    g.link("has.ReturnValue", "return.found")
    return fn("Model Forced", [param("row", "name")], [param("found", "bool")], graph=g, pure=True)


def f_toggle_model_skip(part, arr):
    """Tile menu (only while this model is forced): leave one piece of equipment out of it. The game's own paints do not
    colour them either, so forcing a paint onto them looks wrong to some eyes. Both rows are redrawn - the picture of the
    model tile changes as well, and its cache key carries the choice."""
    g = G(); g.get("gs", arr); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gs.%s" % arr, "ItemToFind": "@entry.name"}); g.branch("b", "@has.ReturnValue")
    g.get("gs1", arr); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gs1.%s" % arr, "Item": "@entry.name"})
    g.get("gs2", arr); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gs2.%s" % arr, "NewItem": "@entry.name"})
    g.n("sv", "call_self", function="Save Settings")
    g.get("gcw", "CurrentWeapon"); g.n("al", "call_self", function="Apply Weapon Look", inp={"weapon": "@gcw.CurrentWeapon"})
    g.n("rl", "call_self", function="Rebuild Weapon Skins"); g.n("rlm", "call_self", function="Rebuild Weapon Models")
    g.chain("entry", "b", "rm", "sv"); g.chain("b:else", "add", "sv"); g.chain("sv", "al", "rl", "rlm")
    return fn("Toggle Model Skip " + part, [param("name", "name")], graph=g)


def f_toggle_model_force_skin():
    """Tile menu: put the game's own weapon material on every slot of this model, so a skin shows on it at all - or back
    to the mod's own materials. The look is the mod author's otherwise; forced, the skin's texture follows the mod's UV
    layout, which it was not painted for, so how well it lands differs from mod to mod."""
    g = G(); g.get("gf", "ForceSkin"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gf.ForceSkin", "ItemToFind": "@entry.name"}); g.branch("b", "@has.ReturnValue")
    g.get("gf1", "ForceSkin"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gf1.ForceSkin", "Item": "@entry.name"})
    g.get("gf2", "ForceSkin"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gf2.ForceSkin", "NewItem": "@entry.name"})
    g.n("sv", "call_self", function="Save Settings")
    g.get("gcw", "CurrentWeapon"); g.n("al", "call_self", function="Apply Weapon Look", inp={"weapon": "@gcw.CurrentWeapon"})
    g.n("rl", "call_self", function="Rebuild Weapon Skins"); g.n("rlm", "call_self", function="Rebuild Weapon Models")
    g.chain("entry", "b", "rm", "sv"); g.chain("b:else", "add", "sv"); g.chain("sv", "al", "rl", "rlm")
    return fn("Toggle Model Force Skin", [param("name", "name")], graph=g)


def f_model_row_passes():
    """Filters of the weapons tab for one model row: search (caption, row name, mod caption), chip (SkinGroup), hidden -
    the same chip row serves both sections, a mod that brings a model and skins is one chip."""
    g = G(); g.n("cap", "call_self", function="Model Caption", inp={"row": "@entry.row"})
    g.get("gst", "WeaponSearchText"); g.call("em", K_STR, "IsEmpty", inp={"InString": "@gst.WeaponSearchText"}); g.call("ls", K_STR, "ToLower", inp={"SourceString": "@gst.WeaponSearchText"})
    g.call("rs", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"})
    g.n("sm", "call_self", function="Model Mod", inp={"row": "@entry.row"}); g.n("mcp", "call_self", function="Mod Caption", inp={"mod": "@sm.mod"})
    prev = "@em.ReturnValue"
    for i, src in enumerate(["@cap.s", "@rs.ReturnValue", "@mcp.s"]):
        g.call("lo%d" % i, K_STR, "ToLower", inp={"SourceString": src})
        g.call("hit%d" % i, K_STR, "Contains", inp={"SearchIn": "@lo%d.ReturnValue" % i, "Substring": "@ls.ReturnValue", "bUseCase": "false", "bSearchFromEnd": "false"})
        g.call("or%d" % i, K_MATH, "BooleanOR", inp={"A": prev, "B": "@hit%d.ReturnValue" % i}); prev = "@or%d.ReturnValue" % i
    g.n("k", "call_self", function="Model Key", inp={"row": "@entry.row"}); g.n("hid", "call_self", function="Is Item Hidden", inp={"name": "@k.key"})
    g.get("gg", "SkinGroup"); g.call("isN", K_MATH, "EqualEqual_NameName", inp={"A": "@gg.SkinGroup", "B": "None"}); g.call("isH", K_MATH, "EqualEqual_NameName", inp={"A": "@gg.SkinGroup", "B": "Hidden"})
    g.call("isV", K_MATH, "EqualEqual_NameName", inp={"A": "@gg.SkinGroup", "B": "Vanilla"})
    g.call("nf", K_MATH, "Not_PreBool", inp={"A": "@sm.found"}); g.call("van", K_MATH, "BooleanAND", inp={"A": "@isV.ReturnValue", "B": "@nf.ReturnValue"})
    g.n("mal", "call_self", function="Mod Alias", inp={"mod": "@sm.mod"}); g.call("eqm", K_MATH, "EqualEqual_NameName", inp={"A": "@mal.alias", "B": "@gg.SkinGroup"}); g.call("mod", K_MATH, "BooleanAND", inp={"A": "@eqm.ReturnValue", "B": "@sm.found"})
    g.call("o1", K_MATH, "BooleanOR", inp={"A": "@isN.ReturnValue", "B": "@van.ReturnValue"}); g.call("o2", K_MATH, "BooleanOR", inp={"A": "@o1.ReturnValue", "B": "@mod.ReturnValue"})
    g.call("nh", K_MATH, "Not_PreBool", inp={"A": "@hid.yes"}); g.call("vis", K_MATH, "BooleanAND", inp={"A": "@o2.ReturnValue", "B": "@nh.ReturnValue"})
    g.call("hh", K_MATH, "BooleanAND", inp={"A": "@isH.ReturnValue", "B": "@hid.yes"}); g.call("chip", K_MATH, "BooleanOR", inp={"A": "@vis.ReturnValue", "B": "@hh.ReturnValue"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": prev, "B": "@chip.ReturnValue"})
    g.set("st", "TmpBool", inp={"TmpBool": "@a1.ReturnValue"}); g.get("gt", "TmpBool"); g.link("gt.TmpBool", "return.yes")
    g.chain("entry", "cap", "st", "return")
    return fn("Model Row Passes", [param("row", "name")], [param("yes", "bool")], graph=g)


def model_tile(g, p, row_pin):
    """Tile of one model row; highlighted when it is the stored choice (None = the weapon's own model).

    The tile carries its row as "model:<row>": both sections sit on one page and both have a row called None, so the
    name a click hands back has to say which section it came from."""
    g.n(p + "cap", "call_self", function="Model Caption", inp={"row": row_pin}); g.n(p + "ic", "call_self", function="Model Icon", inp={"row": row_pin})
    g.call(p + "n2s", K_STR, "Conv_NameToString", inp={"InName": row_pin})
    g.call(p + "pre", K_STR, "Concat_StrStr", inp={"A": "model:", "B": "@%sn2s.ReturnValue" % p})
    g.call(p + "nm", K_STR, "Conv_StringToName", inp={"InString": "@%spre.ReturnValue" % p})
    g.make(p + "mi", S_ITEM, Name="@%snm.ReturnValue" % p, DisplayName="@%scap.s" % p, Icon="@%sic.tex" % p)
    g.n(p + "cm", "call_self", function="Current Model")
    g.call(p + "eq", K_MATH, "EqualEqual_NameName", inp={"A": "@%scm.model" % p, "B": row_pin})
    g.n(p + "fv", "call_self", function="Is Model Favorite", inp={"name": row_pin})
    return [p + "cap", p + "ic"] + look_tile(g, p + "t", "@%smi.S_ClothesItem" % p, "@%seq.ReturnValue" % p, "true",
                                             "Add Weapon Model", tt(g, p + "tip", "Tab_Weapons"), kind="skin", fav_pin="@%sfv.yes" % p)


def want_model_icon(g, p, row_pin):
    """Nodes that remember the first model row without a rendered picture (one rendering per rebuild)."""
    g.get(p + "gcw", "CurrentWeapon"); g.n(p + "cs", "call_self", function="Current Skin")
    g.n(p + "wi", "call_self", function="Weapon Icon", inp={"weapon": "@%sgcw.CurrentWeapon" % p, "model": row_pin, "skin": "@%scs.skin" % p})
    g.get(p + "gnm", "TmpModelMiss"); g.call(p + "ns", K_MATH, "EqualEqual_NameName", inp={"A": "@%sgnm.TmpModelMiss" % p, "B": "None"})
    g.call(p + "wt", K_MATH, "BooleanAND", inp={"A": "@%swi.missing" % p, "B": "@%sns.ReturnValue" % p}); g.branch(p + "bw", "@%swt.ReturnValue" % p)
    g.set(p + "sm", "TmpModelMiss", inp={"TmpModelMiss": row_pin})
    g.chain(p + "bw", p + "sm")
    return [p + "wi", p + "bw"]


def f_rebuild_weapon_models():
    """Tiles of the model section: original + the models of this weapon, favourites first, filters like the skin section."""
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Weapon Models", inp={"self": "@gp.Panel"})
    g.get("gcw", "CurrentWeapon"); g.n("mr", "call_self", function="Models For Weapon", inp={"weapon": "@gcw.CurrentWeapon"})
    g.set("nmiss", "TmpModelMiss", inp={"TmpModelMiss": "None"})
    g.get("gr1", "ModelRows"); g.foreach("ff", "@gr1.ModelRows")
    g.n("pf", "call_self", function="Model Row Passes", inp={"row": "@ff.Array Element"}); g.n("favf", "call_self", function="Is Model Favorite", inp={"name": "@ff.Array Element"})
    g.call("fok", K_MATH, "BooleanAND", inp={"A": "@pf.yes", "B": "@favf.yes"}); g.branch("bf", "@fok.ReturnValue")
    t1 = model_tile(g, "f", "@ff.Array Element") + want_model_icon(g, "f", "@ff.Array Element")
    g.get("gr2", "ModelRows"); g.foreach("fe", "@gr2.ModelRows")
    g.n("pe", "call_self", function="Model Row Passes", inp={"row": "@fe.Array Element"}); g.n("fava", "call_self", function="Is Model Favorite", inp={"name": "@fe.Array Element"})
    g.call("nfv", K_MATH, "Not_PreBool", inp={"A": "@fava.yes"}); g.call("eok", K_MATH, "BooleanAND", inp={"A": "@pe.yes", "B": "@nfv.ReturnValue"}); g.branch("be", "@eok.ReturnValue")
    t2 = model_tile(g, "a", "@fe.Array Element") + want_model_icon(g, "a", "@fe.Array Element")
    # the rendering itself: only outside the camera modes, only while the page is open, and only one at a time
    g.get("gnm2", "TmpModelMiss"); g.call("has", K_MATH, "NotEqual_NameName", inp={"A": "@gnm2.TmpModelMiss", "B": "None"})
    g.get("gcm", "CamMode"); g.call("cam0", K_MATH, "EqualEqual_IntInt", inp={"A": "@gcm.CamMode", "B": "0"})
    g.get("gia", "IconWeaponActor"); g.call("busy", K_SYS, "IsValid", inp={"Object": "@gia.IconWeaponActor"}); g.call("free", K_MATH, "Not_PreBool", inp={"A": "@busy.ReturnValue"})
    g.call("c1", K_MATH, "BooleanAND", inp={"A": "@has.ReturnValue", "B": "@cam0.ReturnValue"}); g.call("cok", K_MATH, "BooleanAND", inp={"A": "@c1.ReturnValue", "B": "@free.ReturnValue"})
    g.get("gpgw", "Page"); g.call("ispw", K_MATH, "EqualEqual_NameName", inp={"A": "@gpgw.Page", "B": "Weapons"})
    g.call("cok2", K_MATH, "BooleanAND", inp={"A": "@cok.ReturnValue", "B": "@ispw.ReturnValue"}); g.branch("bcap", "@cok2.ReturnValue")
    g.get("gcw4", "CurrentWeapon"); g.get("gnm3", "TmpModelMiss"); g.n("cs2", "call_self", function="Current Skin")
    g.n("cap", "call_self", function="Capture Weapon Icon", inp={"weapon": "@gcw4.CurrentWeapon", "model": "@gnm3.TmpModelMiss", "skin": "@cs2.skin"})
    g.chain("entry", "cl", "mr", "nmiss", "ff"); g.chain("ff", "pf", "bf", *t1)
    g.chain("ff:Completed", "fe"); g.chain("fe", "pe", "be", *t2)
    g.chain("fe:Completed", "bcap", "cap")
    return fn("Rebuild Weapon Models", graph=g)


def f_weapon_model_clicked():
    """Model tile: store the choice (None = the weapon's own), apply it and redraw both sections - the skin tiles show
    the skin on the new model."""
    g = G(); g.get("gcw", "CurrentWeapon"); g.get("gm", "WeaponModels")
    g.call("isn", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "None"}); g.branch("b", "@isn.ReturnValue")
    g.call("rm", K_MAP, "Map_Remove", inp={"TargetMap": "@gm.WeaponModels", "Key": "@gcw.CurrentWeapon"})
    g.get("gm2", "WeaponModels"); g.get("gcw2", "CurrentWeapon")
    g.call("ad", K_MAP, "Map_Add", inp={"TargetMap": "@gm2.WeaponModels", "Key": "@gcw2.CurrentWeapon", "Value": "@entry.name"})
    g.n("sv", "call_self", function="Save Settings"); g.get("gcw3", "CurrentWeapon")
    g.n("ap", "call_self", function="Apply Weapon Look", inp={"weapon": "@gcw3.CurrentWeapon"})
    g.n("rm2", "call_self", function="Rebuild Weapon Models"); g.n("rs", "call_self", function="Rebuild Weapon Skins")
    g.chain("entry", "b", "rm", "sv"); g.chain("b:else", "ad", "sv"); g.chain("sv", "ap", "rm2", "rs")
    return fn("Weapon Model Clicked", [param("name", "name")], graph=g)


def f_toggle_model_favorite():
    g = G(); g.n("k", "call_self", function="Model Key", inp={"row": "@entry.name"}); g.set("sk", "TmpName2", inp={"TmpName2": "@k.key"})
    g.get("gk", "TmpName2"); g.n("isf", "call_self", function="Is Favorite", inp={"name": "@gk.TmpName2"}); g.branch("b", "@isf.yes")
    g.get("gf", "Favorites"); g.get("gk1", "TmpName2"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gf.Favorites", "Item": "@gk1.TmpName2"})
    g.get("gf2", "Favorites"); g.get("gk2", "TmpName2"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gf2.Favorites", "NewItem": "@gk2.TmpName2"})
    g.n("sv", "call_self", function="Save Settings"); g.n("rl", "call_self", function="Rebuild Weapon Models")
    g.chain("entry", "sk", "b", "rm", "sv"); g.chain("b:else", "add", "sv"); g.chain("sv", "rl")
    return fn("Toggle Model Favorite", [param("name", "name")], graph=g)


def f_toggle_model_hidden():
    g = G(); g.n("k", "call_self", function="Model Key", inp={"row": "@entry.name"}); g.set("sk", "TmpName2", inp={"TmpName2": "@k.key"})
    g.get("gk", "TmpName2"); g.n("ish", "call_self", function="Is Item Hidden", inp={"name": "@gk.TmpName2"}); g.branch("b", "@ish.yes")
    g.get("gh", "HiddenItems"); g.get("gk1", "TmpName2"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gh.HiddenItems", "Item": "@gk1.TmpName2"})
    g.get("gh2", "HiddenItems"); g.get("gk2", "TmpName2"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gh2.HiddenItems", "NewItem": "@gk2.TmpName2"})
    g.n("sv", "call_self", function="Save Settings"); g.n("rc", "call_self", function="Rebuild Weapon Chips"); g.n("rl", "call_self", function="Rebuild Weapon Models")
    g.chain("entry", "sk", "b", "rm", "sv"); g.chain("b:else", "add", "sv"); g.chain("sv", "rc", "rl")
    return fn("Toggle Model Hidden", [param("name", "name")], graph=g)


def f_model_only_mod():
    g = G(); g.n("sm", "call_self", function="Model Mod", inp={"row": "@entry.name"}); g.branch("b", "@sm.found"); g.n("mal", "call_self", function="Mod Alias", inp={"mod": "@sm.mod"})
    g.n("sg", "call_self", function="Select Skin Group", inp={"name": "@mal.alias"})
    g.chain("entry", "b", "sg"); return fn("Model Only Mod", [param("name", "name")], graph=g)


def f_on_model_context():
    """Model tile menu: favourite on/off, hide/unhide, [only this mod], cancel."""
    def pre(g):
        g.set("sci", "ContextItem", inp={"ContextItem": "@entry.name"})
        g.n("isf", "call_self", function="Is Model Favorite", inp={"name": "@entry.name"}); g.call("fs", K_MATH, "SelectString", inp={"A": ts(g, "fr", "Menu_FavRemove"), "B": ts(g, "fa", "Menu_FavAdd"), "bPickA": "@isf.yes"})
        g.call("ft", K_TXT, "Conv_StringToText", inp={"InString": "@fs.ReturnValue"})
        g.n("k", "call_self", function="Model Key", inp={"row": "@entry.name"}); g.n("ihd", "call_self", function="Is Item Hidden", inp={"name": "@k.key"})
        g.call("hs", K_MATH, "SelectString", inp={"A": ts(g, "hu", "Menu_Unhide"), "B": ts(g, "hh", "Menu_Hide"), "bPickA": "@ihd.yes"})
        g.call("ht", K_TXT, "Conv_StringToText", inp={"InString": "@hs.ReturnValue"})
        g.get("gio2", "IconOwn"); g.call("iso", K_ARR, "Array_Contains", inp={"TargetArray": "@gio2.IconOwn", "ItemToFind": "@entry.name"})
        g.call("os", K_MATH, "SelectString", inp={"A": ts(g, "orn", "Menu_RenderedIcon"), "B": ts(g, "oow", "Menu_OwnIcon"), "bPickA": "@iso.ReturnValue"})
        g.call("ot", K_TXT, "Conv_StringToText", inp={"InString": "@os.ReturnValue"})
        g.get("gfs2", "ForceSkin"); g.call("isfs", K_ARR, "Array_Contains", inp={"TargetArray": "@gfs2.ForceSkin", "ItemToFind": "@entry.name"})
        g.call("fss", K_MATH, "SelectString", inp={"A": ts(g, "fsu", "Menu_UnforceSkin"), "B": ts(g, "fsf", "Menu_ForceSkin"), "bPickA": "@isfs.ReturnValue"})
        g.call("fst", K_TXT, "Conv_StringToText", inp={"InString": "@fss.ReturnValue"})
        for i, (part, cls, arr, _, sx, si) in enumerate(WEAPON_PARTS):
            g.get("gsk%d" % i, arr); g.call("isk%d" % i, K_ARR, "Array_Contains", inp={"TargetArray": "@gsk%d.%s" % (i, arr), "ItemToFind": "@entry.name"})
            g.call("sks%d" % i, K_MATH, "SelectString", inp={"A": ts(g, "ski%d" % i, si), "B": ts(g, "ske%d" % i, sx), "bPickA": "@isk%d.ReturnValue" % i})
            g.call("skt%d" % i, K_TXT, "Conv_StringToText", inp={"InString": "@sks%d.ReturnValue" % i})
        return ["sci"]
    g = simple_menu("On Model Context", [("ModelFav", "@ft.ReturnValue"), ("ModelHide", "@ht.ReturnValue"), ("ModelOwnIcon", "@ot.ReturnValue"),
                                         ("ModelForceSkin", "@fst.ReturnValue")]
                                        + [("ModelSkip" + p, "@skt%d.ReturnValue" % i) for i, (p, _, _, _, _, _) in enumerate(WEAPON_PARTS)]
                                        + [("ModelOnlyMod", "Menu_LookOnlyMod"), ("Cancel", "Menu_Cancel")],
                    pre=pre, cond=dict({"ModelOwnIcon": "Model Has Icon", "ModelForceSkin": "Model Mod", "ModelOnlyMod": "Model Mod"},
                                       **{"ModelSkip" + p: "Model Forced" for p, _, _, _, _, _ in WEAPON_PARTS}))
    return fn("On Model Context", [param("name", "name")], graph=g)


def f_weapon_tile_row():
    """Splits a weapon tile's name: "model:<row>" -> row + model true, anything else -> the name + model false."""
    g = G(); g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"})
    g.call("sw", K_STR, "StartsWith", inp={"SourceString": "@n2s.ReturnValue", "InPrefix": "model:", "SearchCase": "CaseSensitive"})
    g.call("rc", K_STR, "RightChop", inp={"SourceString": "@n2s.ReturnValue", "Count": "6"})   # KismetMath has no SelectName: pick as a string
    g.call("sel", K_MATH, "SelectString", inp={"A": "@rc.ReturnValue", "B": "@n2s.ReturnValue", "bPickA": "@sw.ReturnValue"})
    g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@sel.ReturnValue"})
    g.link("s2n.ReturnValue", "return.row"); g.link("sw.ReturnValue", "return.model")
    return fn("Weapon Tile Row", [param("name", "name")], [param("row", "name"), param("model", "bool")], graph=g, pure=True)


def f_weapon_tile_clicked():
    """A click on the weapons page goes to the handler of the section the tile belongs to."""
    g = G(); g.n("tr", "call_self", function="Weapon Tile Row", inp={"name": "@entry.name"}); g.branch("b", "@tr.model")
    g.n("wmc", "call_self", function="Weapon Model Clicked", inp={"name": "@tr.row"})
    g.n("wsc", "call_self", function="Weapon Skin Clicked", inp={"name": "@tr.row"})
    g.chain("entry", "b", "wmc"); g.chain("b:else", "wsc")
    return fn("Weapon Tile Clicked", [param("name", "name")], graph=g)


def f_on_weapon_context():
    """Right-click on the weapons page: a model row gets the model menu, a skin or paint row the skin menu."""
    g = G(); g.n("tr", "call_self", function="Weapon Tile Row", inp={"name": "@entry.name"}); g.branch("b", "@tr.model")
    g.n("omc", "call_self", function="On Model Context", inp={"name": "@tr.row"})
    g.n("osc", "call_self", function="On Skin Context", inp={"name": "@tr.row"})
    g.chain("entry", "b", "omc"); g.chain("b:else", "osc")
    return fn("On Weapon Context", [param("name", "name")], graph=g)


def f_weapon_icon_key():
    """weapon_model_skin[_f[m]]: a tile shows one combination, so the cache and the file on disk are keyed by all of it.
    The forcing belongs in the key as well - the same weapon, model and skin look different forced, and without it the
    picture from before stayed on disk and was shown again after the forcing was switched off."""
    g = G(); g.call("ws", K_STR, "Conv_NameToString", inp={"InName": "@entry.weapon"})
    g.call("ms", K_STR, "Conv_NameToString", inp={"InName": "@entry.model"}); g.call("ss", K_STR, "Conv_NameToString", inp={"InName": "@entry.skin"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@ws.ReturnValue", "B": "_"}); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@ms.ReturnValue"})
    g.call("c3", K_STR, "Concat_StrStr", inp={"A": "@c2.ReturnValue", "B": "_"}); g.call("c4", K_STR, "Concat_StrStr", inp={"A": "@c3.ReturnValue", "B": "@ss.ReturnValue"})
    g.get("gkf", "ForceSkin"); g.call("hkf", K_ARR, "Array_Contains", inp={"TargetArray": "@gkf.ForceSkin", "ItemToFind": "@entry.model"})
    expr = "_f"
    for i, (part, cls, arr, letter, _, _) in enumerate(WEAPON_PARTS):
        g.get("gkp%d" % i, arr); g.call("hkp%d" % i, K_ARR, "Array_Contains", inp={"TargetArray": "@gkp%d.%s" % (i, arr), "ItemToFind": "@entry.model"})
        g.call("lsel%d" % i, K_MATH, "SelectString", inp={"A": letter, "B": "", "bPickA": "@hkp%d.ReturnValue" % i})
        g.call("lcat%d" % i, K_STR, "Concat_StrStr", inp={"A": expr, "B": "@lsel%d.ReturnValue" % i}); expr = "@lcat%d.ReturnValue" % i
    g.call("sfx", K_MATH, "SelectString", inp={"A": expr, "B": "", "bPickA": "@hkf.ReturnValue"})
    g.call("c5", K_STR, "Concat_StrStr", inp={"A": "@c4.ReturnValue", "B": "@sfx.ReturnValue"})
    g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@c5.ReturnValue"}); g.link("s2n.ReturnValue", "return.key"); g.link("c5.ReturnValue", "return.file")
    return fn("Weapon Icon Key", [param("weapon", "name"), param("model", "name"), param("skin", "name")], [param("key", "name"), param("file", "string")], graph=g, pure=True)


def f_weapon_icon():
    """Rendered tile picture of one weapon with one skin: cache, else the file in Saved/SaveGames/WeaponIcons, else missing."""
    g = G(); g.n("k", "call_self", function="Weapon Icon Key", inp={"weapon": "@entry.weapon", "model": "@entry.model", "skin": "@entry.skin"})
    # marked for a fresh picture (the button in the status bar): answer "no picture", whatever cache or file say - that
    # is what makes the rebuild take one. Finish Photo strikes the key off again.
    g.get("gir", "IconRedo"); g.call("redo", K_ARR, "Array_Contains", inp={"TargetArray": "@gir.IconRedo", "ItemToFind": "@k.key"})
    g.branch("bredo", "@redo.ReturnValue")
    g.n("rmiss", "return_new"); g.link("redo.ReturnValue", "rmiss.missing")
    g.get("gi", "WeaponIcons"); g.call("fnd", K_MAP, "Map_Find", inp={"TargetMap": "@gi.WeaponIcons", "Key": "@k.key"}); g.branch("b", "@fnd.ReturnValue")
    g.link("fnd.Value", "return.tex")
    g.call("dir", K_PATHS, "ProjectSavedDir"); g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@dir.ReturnValue", "B": "SaveGames/WeaponIcons/"})
    g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@k.file"}); g.call("c3", K_STR, "Concat_StrStr", inp={"A": "@c2.ReturnValue", "B": ".jpg"})
    g.call("imp", K_REND, "ImportFileAsTexture2D", inp={"Filename": "@c3.ReturnValue"})
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@imp.ReturnValue"}); g.branch("bv", "@iv.ReturnValue")
    g.get("gi2", "WeaponIcons"); g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gi2.WeaponIcons", "Key": "@k.key", "Value": "@imp.ReturnValue"})
    g.n("r2", "return_new"); g.link("imp.ReturnValue", "r2.tex")
    g.n("r3", "return_new"); g.link("iv.ReturnValue", "r3.missingNot") if False else None
    g.call("miss", K_MATH, "Not_PreBool", inp={"A": "@iv.ReturnValue"}); g.link("miss.ReturnValue", "r2.missing")
    g.chain("entry", "bredo", "rmiss"); g.chain("bredo:else", "b", "return")
    g.chain("b:else", "imp", "bv", "add", "r2"); g.chain("bv:else", "r2")
    return fn("Weapon Icon", [param("weapon", "name"), param("model", "name"), param("skin", "name")], [param("tex", "object:" + E_TEX2D), param("missing", "bool")], graph=g)


def f_capture_weapon_icon():
    """Spawn the weapon actor of `ItemTable.InteractiveClass` (not the pickup actor - only it carries the skeletal mesh),
    put the model on it and let it live for ICON_SPAWN_WAIT frames. The picture itself is taken by Capture Weapon Icon Step,
    because parts the game adds by itself - the magazine is a component of its own - are not there in the frame of the spawn."""
    g = G()
    g.get("gpl", "Player"); g.call("pv", K_SYS, "IsValid", inp={"Object": "@gpl.Player"}); g.branch("bpv", "@pv.ReturnValue")
    g.n("irow", "get_row", table=P_ITEM_T, inp={"RowName": "@entry.weapon"}, miss="ignore"); g.brk("ibr", P_ITEM_S, "@irow.OutRow")
    g.call("icv", K_SYS, "IsValidClass", inp={"Class": "@ibr.InteractiveClass"}); g.branch("bic", "@icv.ReturnValue")
    g.get("gpl2", "Player"); g.call("loc", E_ACTOR, "K2_GetActorLocation", inp={"self": "@gpl2.Player"}); g.call("fwd", E_ACTOR, "GetActorForwardVector", inp={"self": "@gpl2.Player"})
    g.call("fv", K_MATH, "Multiply_VectorFloat", inp={"A": "@fwd.ReturnValue", "B": "120.0"}); g.call("p0", K_MATH, "Add_VectorVector", inp={"A": "@loc.ReturnValue", "B": "@fv.ReturnValue"})
    g.call("up", K_MATH, "MakeVector", inp={"X": "0.0", "Y": "0.0", "Z": "60.0"}); g.call("pos", K_MATH, "Add_VectorVector", inp={"A": "@p0.ReturnValue", "B": "@up.ReturnValue"})
    g.call("tr", K_MATH, "MakeTransform", inp={"Location": "@pos.ReturnValue", "Rotation": "(Pitch=0,Yaw=0,Roll=0)", "Scale": "(X=1,Y=1,Z=1)"})
    g.n("sp", "spawn", inp={"SpawnTransform": "@tr.ReturnValue", "Class": "@ibr.InteractiveClass"})
    g.set("sia", "IconWeaponActor", inp={"IconWeaponActor": "@sp.ReturnValue"})
    g.call("col", E_ACTOR, "SetActorEnableCollision", inp={"self": "@sp.ReturnValue", "bNewActorEnableCollision": "false"})
    # The magazine is a component of its own (Gun_Mag_Comp_C, a StaticMeshComponent) that only the game's equip flow hangs on
    # a weapon - a freshly spawned actor has none, which is why every tile picture was missing it. Mount Mag puts one on; the
    # class comes from the weapon Jodi actually carries. Before Apply Weapon Model, so a model mod replaces the mag mesh too.
    g.cast("cgn", P_GUN, "@sp.ReturnValue", pure=False, miss="ignore")
    g.get("gplw", "Player"); g.get("gws", "Weapons", cls=P_JODI); g.link("gplw.Player", "gws.self")
    g.call("fwn", K_MAP, "Map_Find", inp={"TargetMap": "@gws.Weapons", "Key": "@entry.weapon"}); g.branch("bwn", "@fwn.ReturnValue")
    g.cast("cgo", P_GUN, "@fwn.Value", pure=False, miss="ignore")
    g.get("gem", "Equipment Mag", cls=P_GUN); g.link("cgo.AsWeapon_Gun_Base", "gem.self")
    g.call("emv", K_SYS, "IsValid", inp={"Object": "@gem.Equipment Mag"}); g.branch("bem", "@emv.ReturnValue")
    g.call("mcl", K_GS, "GetObjectClass", inp={"Object": "@gem.Equipment Mag"})
    g.call("mmg", P_GUN, "Mount Mag", inp={"self": "@cgn.AsWeapon_Gun_Base", "class": "@mcl.ReturnValue"})
    # the model before anything is measured: GetComponentBounds would otherwise size and turn the picture by the
    # vanilla mesh, and a longer model would sit cropped in the tile
    g.n("apm", "call_self", function="Apply Weapon Model", inp={"actor": "@sp.ReturnValue", "weapon": "@entry.weapon", "model": "@entry.model"})
    g.set("spk", "PhotoKind", inp={"PhotoKind": "Weapon"}); g.set("spw", "PhotoWeapon", inp={"PhotoWeapon": "@entry.weapon"})
    g.set("sps", "PhotoSkin", inp={"PhotoSkin": "@entry.skin"}); g.set("spm", "PhotoModel", inp={"PhotoModel": "@entry.model"})
    g.set("ssw", "IconSpawnWait", inp={"IconSpawnWait": str(ICON_SPAWN_WAIT)})
    g.chain("entry", "bpv", "irow", "bic", "sp", "sia", "col", "cgn", "bwn", "cgo", "bem", "mmg", "apm", "spk", "spw", "sps", "spm", "ssw")
    g.chain("bwn:else", "apm"); g.chain("bem:else", "apm"); g.chain("cgn:CastFailed", "apm"); g.chain("cgo:CastFailed", "apm")   # melee, or a weapon Jodi does not carry: no magazine, picture as before
    return fn("Capture Weapon Icon", [param("weapon", "name"), param("model", "name"), param("skin", "name")], graph=g)


def f_capture_weapon_icon_step():
    """Second half, a few frames after the spawn: measure, turn, hide the pickup mesh, put the skin on and start the photo."""
    g = G()
    g.get("gwa", "IconWeaponActor"); g.call("av", K_SYS, "IsValid", inp={"Object": "@gwa.IconWeaponActor"}); g.branch("bva", "@av.ReturnValue")
    g.get("gpw", "PhotoWeapon"); g.get("gpm", "PhotoModel"); g.get("gps", "PhotoSkin")
    g.get("gplr", "Player"); g.call("prot", E_ACTOR, "K2_GetActorRotation", inp={"self": "@gplr.Player"}); g.call("brot", K_MATH, "BreakRotator", inp={"InRot": "@prot.ReturnValue"})
    # The weapon actor carries the skeletal mesh and, on top of it, the pickup mesh - the whole weapon a second time as a static
    # mesh. Photograph the skeletal one and hide the pickup. What must NOT be hidden is the weapon's equipment (magazine,
    # optics, suppressor, grip): those derive from Gun_Equipment_Base_C, so the cast tells them apart - a size rule did not
    # (2026-09-25: the APC9's pickup mesh slipped under the threshold and stayed visible, so its tile drew the weapon twice).
    # And the pickup is hidden WITHOUT propagating: the magazine hangs off it, and propagating took it along.
    # A melee weapon has only the static mesh, that one stays.
    g.call("skc", E_ACTOR, "K2_GetComponentsByClass", inp={"self": "@gwa.IconWeaponActor", "ComponentClass": E_SKELC})
    g.call("skn", K_ARR, "Array_Length", inp={"TargetArray": "@skc.ReturnValue"}); g.call("hs", K_MATH, "Greater_IntInt", inp={"A": "@skn.ReturnValue", "B": "0"})
    g.branch("bhs", "@hs.ReturnValue")
    g.call("sk0", K_ARR, "Array_Get", inp={"TargetArray": "@skc.ReturnValue", "Index": "0"}); g.cast("csk", E_SCENEC, "@sk0.Item", pure=False, miss="ignore")
    g.set("tc1", "TmpComp", inp={"TmpComp": "@csk.AsScene Component"})
    g.call("stc", E_ACTOR, "K2_GetComponentsByClass", inp={"self": "@gwa.IconWeaponActor", "ComponentClass": E_SMC}); g.set("sc2", "TmpComps2", inp={"TmpComps2": "@stc.ReturnValue"})
    # reference size: the longest half axis of the photographed skeletal mesh
    g.call("sbd", K_SYS, "GetComponentBounds", inp={"Component": "@csk.AsScene Component"}); g.call("sbe", K_MATH, "BreakVector", inp={"InVec": "@sbd.BoxExtent"})
    g.call("sl0", K_MATH, "FMax", inp={"A": "@sbe.X", "B": "@sbe.Y"}); g.call("sl1", K_MATH, "FMax", inp={"A": "@sl0.ReturnValue", "B": "@sbe.Z"})
    g.set("sirc0", "IconReach", inp={"IconReach": "@sl1.ReturnValue"})
    if WEAPONLOG:
        g.call("qsn", K_ARR, "Array_Length", inp={"TargetArray": "@skc.ReturnValue"})
        g.get("qc2", "TmpComps2"); g.call("qtn", K_ARR, "Array_Length", inp={"TargetArray": "@qc2.TmpComps2"})
        log(g, "cap", ["icon ", nstr(g, "cw", "@gpw.PhotoWeapon"), " model=", nstr(g, "cm", "@gpm.PhotoModel"), " skin=", nstr(g, "cs", "@gps.PhotoSkin"),
                       " skel=", num(g, "ck", "@qsn.ReturnValue"), " static=", num(g, "ct", "@qtn.ReturnValue"),
                       " skelmesh=", oname(g, "csk", "@csk.AsScene Component")])
    g.get("gc2", "TmpComps2"); g.foreach("fh", "@gc2.TmpComps2"); g.cast("ch", E_SCENEC, "@fh.Array Element", pure=False, miss="ignore")
    g.call("hbd", K_SYS, "GetComponentBounds", inp={"Component": "@ch.AsScene Component"}); g.call("hbe", K_MATH, "BreakVector", inp={"InVec": "@hbd.BoxExtent"})
    g.call("hl0", K_MATH, "FMax", inp={"A": "@hbe.X", "B": "@hbe.Y"}); g.call("hl1", K_MATH, "FMax", inp={"A": "@hl0.ReturnValue", "B": "@hbe.Z"})
    g.cast("heq", P_EQUIPBASE, "@fh.Array Element", pure=False, miss="ignore")   # equipment stays, everything else is the pickup
    if WEAPONLOG:
        log(g, "st", ["  static ", oname(g, "sc1", "@ch.AsScene Component"), " size=", fnum(g, "sz", "@hl1.ReturnValue"),
                      " dist=", fnum(g, "ds", "@hdl.ReturnValue")])
    g.call("hid", E_SCENEC, "SetVisibility", inp={"self": "@ch.AsScene Component", "bNewVisibility": "false", "bPropagateToChildren": "false"})
    # stays visible: how far does it reach from the centre of the photographed mesh?
    g.call("hdv", K_MATH, "Subtract_VectorVector", inp={"A": "@hbd.Origin", "B": "@sbd.Origin"}); g.call("hdl", K_MATH, "VSize", inp={"A": "@hdv.ReturnValue"})
    g.call("hrc", K_MATH, "Add_FloatFloat", inp={"A": "@hdl.ReturnValue", "B": "@hl1.ReturnValue"})
    g.get("girc", "IconReach"); g.call("hmx", K_MATH, "FMax", inp={"A": "@girc.IconReach", "B": "@hrc.ReturnValue"}); g.set("sirc", "IconReach", inp={"IconReach": "@hmx.ReturnValue"})
    g.call("pr0", K_ARR, "Array_Get", inp={"TargetArray": "@cmp.ReturnValue", "Index": "0"}); g.cast("cpr", E_SCENEC, "@pr0.Item", pure=False, miss="ignore")
    g.set("tc2", "TmpComp", inp={"TmpComp": "@cpr.AsScene Component"})
    # Side view like the game's own item icons, whatever the mesh's axes are: the bounding box of the photographed mesh at rotation 0
    # sorts them - longest half axis = the weapon's length, middle = its height, shortest = its width. The length axis is turned to the
    # upper left of the picture (muzzle = its plus side), the height axis upwards, so the thin side faces the camera.
    g.get("gtc", "TmpComp"); g.call("bd1", K_SYS, "GetComponentBounds", inp={"Component": "@gtc.TmpComp"})
    g.call("bex", K_MATH, "BreakVector", inp={"InVec": "@bd1.BoxExtent"})
    g.call("phi", K_MATH, "Add_FloatFloat", inp={"A": "@brot.Yaw", "B": "90.0"})   # + 90 = to the left in the picture (the camera looks back at Jodi)
    g.call("drot", K_MATH, "MakeRotator", inp={"Roll": "0.0", "Pitch": str(ICON_PITCH), "Yaw": "@phi.ReturnValue"})
    g.call("bdir", K_MATH, "GetForwardVector", inp={"InRot": "@drot.ReturnValue"}); g.call("dn", K_MATH, "MakeVector", inp={"X": "0.0", "Y": "0.0", "Z": "1.0"})
    g.call("xy", K_MATH, "GreaterEqual_FloatFloat", inp={"A": "@bex.X", "B": "@bex.Y"}); g.call("xz", K_MATH, "GreaterEqual_FloatFloat", inp={"A": "@bex.X", "B": "@bex.Z"})
    g.call("yz", K_MATH, "GreaterEqual_FloatFloat", inp={"A": "@bex.Y", "B": "@bex.Z"}); g.call("nxy", K_MATH, "Not_PreBool", inp={"A": "@xy.ReturnValue"})
    g.call("lx", K_MATH, "BooleanAND", inp={"A": "@xy.ReturnValue", "B": "@xz.ReturnValue"}); g.call("ly", K_MATH, "BooleanAND", inp={"A": "@nxy.ReturnValue", "B": "@yz.ReturnValue"})
    g.branch("blx", "@lx.ReturnValue"); g.branch("bhx", "@yz.ReturnValue")
    g.call("mxy", K_MATH, "MakeRotFromXY", inp={"X": "@bdir.ReturnValue", "Y": "@dn.ReturnValue"}); g.set("rxy", "TmpRot", inp={"TmpRot": "@mxy.ReturnValue"})
    g.call("mxz", K_MATH, "MakeRotFromXZ", inp={"X": "@bdir.ReturnValue", "Z": "@dn.ReturnValue"}); g.set("rxz", "TmpRot", inp={"TmpRot": "@mxz.ReturnValue"})
    g.branch("bly", "@ly.ReturnValue"); g.branch("bhy", "@xz.ReturnValue")
    g.call("myx", K_MATH, "MakeRotFromYX", inp={"Y": "@bdir.ReturnValue", "X": "@dn.ReturnValue"}); g.set("ryx", "TmpRot", inp={"TmpRot": "@myx.ReturnValue"})
    g.call("myz", K_MATH, "MakeRotFromYZ", inp={"Y": "@bdir.ReturnValue", "Z": "@dn.ReturnValue"}); g.set("ryz", "TmpRot", inp={"TmpRot": "@myz.ReturnValue"})
    g.branch("bhz", "@xy.ReturnValue")
    g.call("mzx", K_MATH, "MakeRotFromZX", inp={"Z": "@bdir.ReturnValue", "X": "@dn.ReturnValue"}); g.set("rzx", "TmpRot", inp={"TmpRot": "@mzx.ReturnValue"})
    g.call("mzy", K_MATH, "MakeRotFromZY", inp={"Z": "@bdir.ReturnValue", "Y": "@dn.ReturnValue"}); g.set("rzy", "TmpRot", inp={"TmpRot": "@mzy.ReturnValue"})
    g.get("gtr", "TmpRot"); g.call("srot", E_ACTOR, "K2_SetActorRotation", inp={"self": "@gwa.IconWeaponActor", "NewRotation": "@gtr.TmpRot", "bTeleportPhysics": "false"})
    g.chain("blx", "bhx"); g.chain("bhx", "rxy", "srot"); g.chain("bhx:else", "rxz", "srot")
    g.chain("blx:else", "bly"); g.chain("bly", "bhy"); g.chain("bhy", "ryx", "srot"); g.chain("bhy:else", "ryz", "srot")
    g.chain("bly:else", "bhz"); g.chain("bhz", "rzx", "srot"); g.chain("bhz:else", "rzy", "srot")
    # and it fills the tile: camera distance from the size of the weapon (28 degrees field of view -> half width = 0.249 x distance)
    g.get("girc2", "IconReach")   # not the photographed mesh alone: the magazine hangs off it and was cropped away
    g.call("d0", K_MATH, "Multiply_FloatFloat", inp={"A": "@girc2.IconReach", "B": "5.0"}); g.call("dst", K_MATH, "FMax", inp={"A": "@d0.ReturnValue", "B": "40.0"})
    g.call("rse", K_MATH, "Multiply_FloatFloat", inp={"A": "@dst.ReturnValue", "B": "0.1"})   # a touch from above, otherwise a flat side view
    # only the scene capture sees it, and it wears the skin
    g.call("cmp", E_ACTOR, "K2_GetComponentsByClass", inp={"self": "@gwa.IconWeaponActor", "ComponentClass": E_PRIM}); g.set("scp", "TmpComps", inp={"TmpComps": "@cmp.ReturnValue"})
    g.get("gcp", "TmpComps"); g.foreach("fc", "@gcp.TmpComps"); g.cast("cc", E_PRIM, "@fc.Array Element", pure=False, miss="ignore")
    g.call("vis", E_PRIM, "SetVisibleInSceneCaptureOnly", inp={"self": "@cc.AsPrimitive Component", "bValue": "true"})
    if WEAPONLOG:
        g.call("pvi", E_SCENECOMP, "IsVisible", inp={"self": "@cc.AsPrimitive Component"})
        g.call("pnm", E_PRIM, "GetNumMaterials", inp={"self": "@cc.AsPrimitive Component"})
        log(g, "pr", ["  prim ", oname(g, "pc1", "@cc.AsPrimitive Component"), " visible=", boolstr(g, "pv", "@pvi.ReturnValue"),
                      " mats=", num(g, "pm", "@pnm.ReturnValue")])
    g.n("sm", "call_self", function="Skin Mod", inp={"row": "@gps.PhotoSkin"}); g.branch("bsk", "@sm.found")
    # skin mod: dynamic instance with its textures
    g.n("sr", "call_self", function="Skin Row", inp={"row": "@gps.PhotoSkin"}); g.brk("sb", ws.STRUCT_PATH, "@sr.skin")
    g.call("dm", E_PRIM, "CreateDynamicMaterialInstance", inp={"self": "@cc.AsPrimitive Component", "ElementIndex": "0", "SourceMaterial": "None", "OptionalName": "None"})
    g.chain("dm", skin_tex(g, "ytx", "@dm.ReturnValue", []))
    # gun paint: the material of this weapon
    g.n("prow", "get_row", table=P_PAINT_T, inp={"RowName": "@gps.PhotoSkin"}, miss="ignore"); g.brk("pbr", P_PAINT_S, "@prow.OutRow")
    g.call("fm", K_MAP, "Map_Find", inp={"TargetMap": "@pbr.Guns", "Key": "@gpw.PhotoWeapon"}); g.branch("bfm", "@fm.ReturnValue")
    g.call("setm", E_PRIM, "SetMaterial", inp={"self": "@cc.AsPrimitive Component", "ElementIndex": "0", "Material": "@fm.Value"})
    # photo
    g.n("wk", "call_self", function="Weapon Icon Key", inp={"weapon": "@gpw.PhotoWeapon", "model": "@gpm.PhotoModel", "skin": "@gps.PhotoSkin"})
    g.call("dir", K_PATHS, "ProjectSavedDir"); g.call("pd", K_STR, "Concat_StrStr", inp={"A": "@dir.ReturnValue", "B": "SaveGames/WeaponIcons"})
    g.call("fn2", K_STR, "Concat_StrStr", inp={"A": "@wk.file", "B": ".jpg"})
    g.set("spo", "PhotoOnly", inp={"PhotoOnly": "@gwa.IconWeaponActor"})   # nothing but the weapon in the picture
    g.get("gtc2", "TmpComp"); g.call("bd2", K_SYS, "GetComponentBounds", inp={"Component": "@gtc2.TmpComp"})   # centre of the turned mesh
    g.n("cap", "call_self", function="Capture Photo", inp={"target": "@bd2.Origin", "distance": "@dst.ReturnValue", "rise": "@rse.ReturnValue", "width": "128", "height": "128", "dir": "@pd.ReturnValue", "file": "@fn2.ReturnValue"})
    g.call("lw1", K_STR, "Conv_NameToString", inp={"InName": "@gpw.PhotoWeapon"}); g.call("ls1", K_STR, "Conv_NameToString", inp={"InName": "@gps.PhotoSkin"})
    g.call("lc1", K_STR, "Concat_StrStr", inp={"A": "wicon ", "B": "@lw1.ReturnValue"}); g.call("lc2", K_STR, "Concat_StrStr", inp={"A": "@lc1.ReturnValue", "B": " "})
    g.call("lc3", K_STR, "Concat_StrStr", inp={"A": "@lc2.ReturnValue", "B": "@ls1.ReturnValue"}); g.n("log", "call_self", function="Log Line", inp={"text": "@lc3.ReturnValue"})
    g.chain("entry", "bva", "bhs")
    g.chain("bhs", "csk", "tc1", "sc2", "sirc0", *(["lgcap"] if WEAPONLOG else []), "fh")
    g.chain("fh", "ch", *(["lgst"] if WEAPONLOG else []), "heq", "sirc"); g.chain("heq:CastFailed", "hid"); g.chain("fh:Completed", "blx")
    g.call("mbd", K_SYS, "GetComponentBounds", inp={"Component": "@cpr.AsScene Component"}); g.call("mbe", K_MATH, "BreakVector", inp={"InVec": "@mbd.BoxExtent"})
    g.call("ml0", K_MATH, "FMax", inp={"A": "@mbe.X", "B": "@mbe.Y"}); g.call("ml1", K_MATH, "FMax", inp={"A": "@ml0.ReturnValue", "B": "@mbe.Z"})
    g.set("sircm", "IconReach", inp={"IconReach": "@ml1.ReturnValue"})   # melee: only the static mesh, that is the whole weapon
    g.chain("bhs:else", "cpr", "tc2", "sircm", "blx"); g.chain("srot", "scp", "fc")
    # forced, exactly as on the weapon in the hand: the game's own material on every slot, for a skin mod and for a paint.
    # Without this the picture kept showing what a skin does unforced - which on a mod model is next to nothing.
    # the same clearing the weapon in the hand gets: without it a component keeps the material its Blueprint assigned, and
    # that one knows the skin parameters - which made the picture put a skin on the magazine where the hand does not.
    # ... and, as in the hand, put back what the clearing took away where the mesh brings nothing of its own -
    # otherwise the picture shows the engine's grey checkerboard on those sections (OrigMats, one entry per slot).
    g.get("ygom", "OrigMats")
    g.call("yfind", K_MAP, "Map_Find", inp={"TargetMap": "@ygom.OrigMats", "Key": "@cc.AsPrimitive Component"})
    g.brk("ybrk", S_MATS, "@yfind.Value")
    g.call("ylen", K_ARR, "Array_Length", inp={"TargetArray": "@ybrk.Mats"})
    g.call("ylast", K_MATH, "Subtract_IntInt", inp={"A": "@ylen.ReturnValue", "B": "1"})
    g.call("yany", K_MATH, "Greater_IntInt", inp={"A": "@ylen.ReturnValue", "B": "0"})
    g.get("yhm", "OrigMats"); g.call("yhas", K_MAP, "Map_Contains", inp={"TargetMap": "@yhm.OrigMats", "Key": "@cc.AsPrimitive Component"})
    g.call("ynot", K_MATH, "Not_PreBool", inp={"A": "@yhas.ReturnValue"}); g.branch("yhb", "@ynot.ReturnValue")
    yy_chain = remember_mats(g, "yy", "@cc.AsPrimitive Component")
    ytail = ["yhb"]
    for i in range(FORCE_SLOTS):
        g.call("ym%d" % i, E_PRIM, "SetMaterial", inp={"self": "@cc.AsPrimitive Component", "ElementIndex": str(i), "Material": "None"})
        g.call("yq%d" % i, E_PRIM, "GetMaterial", inp={"self": "@cc.AsPrimitive Component", "ElementIndex": str(i)})
        g.call("yv%d" % i, K_SYS, "IsValid", inp={"Object": "@yq%d.ReturnValue" % i})
        g.call("yn%d" % i, K_MATH, "Not_PreBool", inp={"A": "@yv%d.ReturnValue" % i}); g.branch("yb%d" % i, "@yn%d.ReturnValue" % i)
        g.call("ygt%d" % i, K_MATH, "Greater_IntInt", inp={"A": "@ylen.ReturnValue", "B": str(i)})
        g.call("yidx%d" % i, K_MATH, "SelectInt", inp={"A": str(i), "B": "@ylast.ReturnValue", "bPickA": "@ygt%d.ReturnValue" % i})
        g.call("yan%d" % i, K_MATH, "BooleanAND", inp={"A": "@yany.ReturnValue", "B": "@yfind.ReturnValue"})
        g.branch("ybb%d" % i, "@yan%d.ReturnValue" % i)
        g.call("yget%d" % i, K_ARR, "Array_Get", inp={"TargetArray": "@ybrk.Mats", "Index": "@yidx%d.ReturnValue" % i})
        g.call("yset%d" % i, E_PRIM, "SetMaterial", inp={"self": "@cc.AsPrimitive Component", "ElementIndex": str(i), "Material": "@yget%d.Item" % i})
        ynxt = "ym%d" % (i + 1) if i + 1 < FORCE_SLOTS else "xp0"
        g.chain("ym%d" % i, "yb%d" % i)
        g.chain("yb%d" % i, "ybb%d" % i); g.chain("ybb%d" % i, "yset%d" % i, ynxt)
        g.chain("yb%d:else" % i, ynxt); g.chain("ybb%d:else" % i, ynxt)
    g.chain("yhb", *yy_chain); g.chain("yyput", "ym0"); g.chain("yhb:else", "ym0")
    g.get("xgf", "ForceSkin"); g.call("xfc", K_ARR, "Array_Contains", inp={"TargetArray": "@xgf.ForceSkin", "ItemToFind": "@gpm.PhotoModel"})
    for i, (part, cls, arr, _, _, _) in enumerate(WEAPON_PARTS):
        g.cast("xp%d" % i, cls, "@cc.AsPrimitive Component", pure=False, miss="ignore")
        g.get("xgs%d" % i, arr); g.call("xsc%d" % i, K_ARR, "Array_Contains", inp={"TargetArray": "@xgs%d.%s" % (i, arr), "ItemToFind": "@gpm.PhotoModel"})
        g.call("xan%d" % i, K_MATH, "BooleanAND", inp={"A": "@xsc%d.ReturnValue" % i, "B": "@xfc.ReturnValue"})
        g.call("xno%d" % i, K_MATH, "Not_PreBool", inp={"A": "@xan%d.ReturnValue" % i}); g.branch("xbp%d" % i, "@xno%d.ReturnValue" % i)
    g.branch("xbf", "@xfc.ReturnValue"); g.branch("xqbf", "@xfc.ReturnValue")
    g.get("xom", "OrigMat"); g.call("xfom", K_MAP, "Map_Find", inp={"TargetMap": "@xom.OrigMat", "Key": "@cc.AsPrimitive Component"})
    g.call("xnm", E_PRIM, "GetNumMaterials", inp={"self": "@cc.AsPrimitive Component"})
    for i in range(FORCE_SLOTS):
        g.call("xgt%d" % i, K_MATH, "Greater_IntInt", inp={"A": "@xnm.ReturnValue", "B": str(i)}); g.branch("xb%d" % i, "@xgt%d.ReturnValue" % i)
        g.call("xdm%d" % i, E_PRIM, "CreateDynamicMaterialInstance", inp={"self": "@cc.AsPrimitive Component", "ElementIndex": str(i), "SourceMaterial": "@xfom.Value", "OptionalName": "None"})
        nxt = ["xb%d" % (i + 1)] if i + 1 < FORCE_SLOTS else []
        g.chain("xb%d" % i, "xdm%d" % i, skin_tex(g, "xtx%d_" % i, "@xdm%d.ReturnValue" % i, nxt))
        if nxt: g.chain("xb%d:else" % i, *nxt)
        g.call("xqgt%d" % i, K_MATH, "Greater_IntInt", inp={"A": "@xnm.ReturnValue", "B": str(i)}); g.branch("xqb%d" % i, "@xqgt%d.ReturnValue" % i)
        g.call("xqsm%d" % i, E_PRIM, "SetMaterial", inp={"self": "@cc.AsPrimitive Component", "ElementIndex": str(i), "Material": "@fm.Value"})
        qnxt = ["xqb%d" % (i + 1)] if i + 1 < FORCE_SLOTS else []
        g.chain("xqb%d" % i, "xqsm%d" % i, *qnxt)
        if qnxt: g.chain("xqb%d:else" % i, *qnxt)
    g.chain("fc", "cc", "vis", *(["lgpr"] if WEAPONLOG else []), *ytail)
    for i in range(len(WEAPON_PARTS)):
        nxt = "xp%d" % (i + 1) if i + 1 < len(WEAPON_PARTS) else "bsk"
        g.chain("xp%d" % i, "xbp%d" % i); g.chain("xbp%d" % i, "bsk"); g.chain("xp%d:CastFailed" % i, nxt)
    g.chain("bsk", "sr", "xbf"); g.chain("xbf", "xb0"); g.chain("xbf:else", "dm")
    # unforced, a paint goes onto the weapon itself and not onto its equipment - the game's own Change Gun Paint, which the
    # weapon in the hand uses, leaves the magazine alone. Setting the paint material on every component put it on the
    # magazine, and on a mod model that was the only part that reacted: a pink magazine on an otherwise plain weapon.
    g.cast("xeq", P_EQUIPBASE, "@cc.AsPrimitive Component", pure=False, miss="ignore")
    g.chain("bsk:else", "prow", "bfm", "xqbf"); g.chain("xqbf", "xqb0"); g.chain("xqbf:else", "xeq"); g.chain("xeq:CastFailed", "setm")
    g.chain("fc:Completed", "spo", "log", "cap")
    return fn("Capture Weapon Icon Step", graph=g)


def f_skin_caption():
    """Tile caption: "Original" for None, the skin's Caption (else its row name) for a skin, the row name for a paint."""
    g = G(); g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"}); g.set("s0", "TmpStr", inp={"TmpStr": "@n2s.ReturnValue"})
    g.call("isn", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.row", "B": "None"}); g.branch("bn", "@isn.ReturnValue")
    g.call("ots", K_TXT, "Conv_TextToString", inp={"InText": tt(g, "ot", "Skin_Original")}); g.set("s1", "TmpStr", inp={"TmpStr": "@ots.ReturnValue"})
    g.n("sm", "call_self", function="Skin Mod", inp={"row": "@entry.row"}); g.branch("bs", "@sm.found")
    g.n("sr", "call_self", function="Skin Row", inp={"row": "@entry.row"}); g.brk("sb", ws.STRUCT_PATH, "@sr.skin")
    g.call("te", K_TXT, "TextIsEmpty", inp={"InText": "@sb.Caption"}); g.branch("be", "@te.ReturnValue")
    g.call("cs", K_TXT, "Conv_TextToString", inp={"InText": "@sb.Caption"}); g.set("s2", "TmpStr", inp={"TmpStr": "@cs.ReturnValue"})
    g.get("gs", "TmpStr"); g.link("gs.TmpStr", "return.s")
    g.chain("entry", "s0", "bn", "s1", "return"); g.chain("bn:else", "bs", "sr", "be", "return"); g.chain("be:else", "s2", "return"); g.chain("bs:else", "return")
    return fn("Skin Caption", [param("row", "name")], [param("s", "string")], graph=g)


def f_skin_icon():
    """Tile icon: the rendered picture of this weapon with this skin, else a skin mod's own icon, else the weapon's item icon."""
    g = G(); g.get("gcw", "CurrentWeapon"); g.n("wrow", "get_row", table=P_ITEM_T, inp={"RowName": "@gcw.CurrentWeapon"}, miss="ignore"); g.brk("wbr", P_ITEM_S, "@wrow.OutRow")
    g.set("s0", "TmpTex", inp={"TmpTex": "@wbr.Icon"})
    g.get("gcw2", "CurrentWeapon"); g.n("cm", "call_self", function="Current Model")
    g.n("ric", "call_self", function="Weapon Icon", inp={"weapon": "@gcw2.CurrentWeapon", "model": "@cm.model", "skin": "@entry.row"})
    g.call("rv", K_SYS, "IsValid", inp={"Object": "@ric.tex"}); g.branch("brd", "@rv.ReturnValue"); g.set("srd", "TmpTex", inp={"TmpTex": "@ric.tex"})
    g.n("sm", "call_self", function="Skin Mod", inp={"row": "@entry.row"}); g.branch("bs", "@sm.found")
    # --- skin mod: icon, else base colour
    g.n("sr", "call_self", function="Skin Row", inp={"row": "@entry.row"}); g.brk("sb", ws.STRUCT_PATH, "@sr.skin")
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@sb.Icon"}); g.branch("bi", "@iv.ReturnValue"); g.set("s1", "TmpTex", inp={"TmpTex": "@sb.Icon"})
    g.get("gt", "TmpTex"); g.link("gt.TmpTex", "return.tex")
    g.chain("entry", "wrow", "s0", "ric", "brd", "srd", "return"); g.chain("wrow:Row Not Found", "ric")
    g.chain("brd:else", "bs"); g.chain("bs", "sr", "bi", "s1", "return")
    g.chain("bi:else", "return")
    g.chain("bs:else", "return")   # paints have no picture of their own: the rendered one or the weapon's item icon
    return fn("Skin Icon", [param("row", "name")], [param("tex", "object:" + E_TEX2D)], graph=g)


def f_is_skin_favorite():
    g = G(); g.n("k", "call_self", function="Skin Key", inp={"row": "@entry.name"}); g.n("f", "call_self", function="Is Favorite", inp={"name": "@k.key"}); g.link("f.yes", "return.yes")
    return fn("Is Skin Favorite", [param("name", "name")], [param("yes", "bool")], graph=g, pure=True)


def f_skin_key():
    g = G(); g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"}); g.call("cc", K_STR, "Concat_StrStr", inp={"A": "skin:", "B": "@n2s.ReturnValue"})
    g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@cc.ReturnValue"}); g.link("s2n.ReturnValue", "return.key")
    return fn("Skin Key", [param("row", "name")], [param("key", "name")], graph=g, pure=True)


def f_skin_row_passes():
    """Filters of the weapons tab for one skin row: search (caption, row name, mod caption), chip (SkinGroup), hidden."""
    g = G(); g.n("cap", "call_self", function="Skin Caption", inp={"row": "@entry.row"})
    g.get("gst", "WeaponSearchText"); g.call("em", K_STR, "IsEmpty", inp={"InString": "@gst.WeaponSearchText"}); g.call("ls", K_STR, "ToLower", inp={"SourceString": "@gst.WeaponSearchText"})
    g.call("rs", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"})
    g.n("sm", "call_self", function="Skin Mod", inp={"row": "@entry.row"}); g.n("mcp", "call_self", function="Mod Caption", inp={"mod": "@sm.mod"})
    prev = "@em.ReturnValue"
    for i, src in enumerate(["@cap.s", "@rs.ReturnValue", "@mcp.s"]):
        g.call("lo%d" % i, K_STR, "ToLower", inp={"SourceString": src})
        g.call("hit%d" % i, K_STR, "Contains", inp={"SearchIn": "@lo%d.ReturnValue" % i, "Substring": "@ls.ReturnValue", "bUseCase": "false", "bSearchFromEnd": "false"})
        g.call("or%d" % i, K_MATH, "BooleanOR", inp={"A": prev, "B": "@hit%d.ReturnValue" % i}); prev = "@or%d.ReturnValue" % i
    g.n("k", "call_self", function="Skin Key", inp={"row": "@entry.row"}); g.n("hid", "call_self", function="Is Item Hidden", inp={"name": "@k.key"})
    g.get("gg", "SkinGroup"); g.call("isN", K_MATH, "EqualEqual_NameName", inp={"A": "@gg.SkinGroup", "B": "None"}); g.call("isH", K_MATH, "EqualEqual_NameName", inp={"A": "@gg.SkinGroup", "B": "Hidden"})
    g.call("isV", K_MATH, "EqualEqual_NameName", inp={"A": "@gg.SkinGroup", "B": "Vanilla"})
    g.call("nf", K_MATH, "Not_PreBool", inp={"A": "@sm.found"}); g.call("van", K_MATH, "BooleanAND", inp={"A": "@isV.ReturnValue", "B": "@nf.ReturnValue"})
    g.n("mal", "call_self", function="Mod Alias", inp={"mod": "@sm.mod"}); g.call("eqm", K_MATH, "EqualEqual_NameName", inp={"A": "@mal.alias", "B": "@gg.SkinGroup"}); g.call("mod", K_MATH, "BooleanAND", inp={"A": "@eqm.ReturnValue", "B": "@sm.found"})
    g.call("o1", K_MATH, "BooleanOR", inp={"A": "@isN.ReturnValue", "B": "@van.ReturnValue"}); g.call("o2", K_MATH, "BooleanOR", inp={"A": "@o1.ReturnValue", "B": "@mod.ReturnValue"})
    g.call("nh", K_MATH, "Not_PreBool", inp={"A": "@hid.yes"}); g.call("vis", K_MATH, "BooleanAND", inp={"A": "@o2.ReturnValue", "B": "@nh.ReturnValue"})
    g.call("hh", K_MATH, "BooleanAND", inp={"A": "@isH.ReturnValue", "B": "@hid.yes"}); g.call("chip", K_MATH, "BooleanOR", inp={"A": "@vis.ReturnValue", "B": "@hh.ReturnValue"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": prev, "B": "@chip.ReturnValue"})
    g.set("st", "TmpBool", inp={"TmpBool": "@a1.ReturnValue"}); g.get("gt", "TmpBool"); g.link("gt.TmpBool", "return.yes")
    g.chain("entry", "cap", "st", "return")
    return fn("Skin Row Passes", [param("row", "name")], [param("yes", "bool")], graph=g)


def f_skin_groups():
    """Chips of the current weapon's skin rows: Vanilla / mod alias per row, "Hidden" last if a row is hidden."""
    g = G(); g.get("gn0", "TmpNames4"); g.call("clr", K_ARR, "Array_Clear", inp={"TargetArray": "@gn0.TmpNames4"}); g.set("hf0", "TmpFound", inp={"TmpFound": "false"})
    g.get("gr", "SkinRows"); g.foreach("fe", "@gr.SkinRows")
    g.n("sm", "call_self", function="Skin Mod", inp={"row": "@fe.Array Element"}); g.n("mal", "call_self", function="Mod Alias", inp={"mod": "@sm.mod"})
    g.call("ms", K_STR, "Conv_NameToString", inp={"InName": "@mal.alias"}); g.call("sel", K_MATH, "SelectString", inp={"A": "@ms.ReturnValue", "B": "Vanilla", "bPickA": "@sm.found"})
    g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@sel.ReturnValue"})
    g.get("gn1", "TmpNames4"); g.call("add", K_ARR, "Array_AddUnique", inp={"TargetArray": "@gn1.TmpNames4", "NewItem": "@s2n.ReturnValue"})
    g.n("k", "call_self", function="Skin Key", inp={"row": "@fe.Array Element"}); g.n("ih", "call_self", function="Is Item Hidden", inp={"name": "@k.key"})
    g.branch("bih", "@ih.yes"); g.set("hf1", "TmpFound", inp={"TmpFound": "true"})
    g.get("ghf", "TmpFound"); g.branch("bhf", "@ghf.TmpFound"); g.get("gn3", "TmpNames4"); g.call("addh", K_ARR, "Array_Add", inp={"TargetArray": "@gn3.TmpNames4", "NewItem": g.lit_name("hn", "Hidden")})
    # the model rows belong in the same chip row: a mod that brings a model and skins is one chip
    g.get("mr", "ModelRows"); g.foreach("fm", "@mr.ModelRows")
    g.n("mm", "call_self", function="Model Mod", inp={"row": "@fm.Array Element"}); g.n("mml", "call_self", function="Mod Alias", inp={"mod": "@mm.mod"})
    g.call("mms", K_STR, "Conv_NameToString", inp={"InName": "@mml.alias"}); g.call("msel", K_MATH, "SelectString", inp={"A": "@mms.ReturnValue", "B": "Vanilla", "bPickA": "@mm.found"})
    g.call("ms2n", K_STR, "Conv_StringToName", inp={"InString": "@msel.ReturnValue"})
    g.get("gn4", "TmpNames4"); g.call("madd", K_ARR, "Array_AddUnique", inp={"TargetArray": "@gn4.TmpNames4", "NewItem": "@ms2n.ReturnValue"})
    g.n("mk", "call_self", function="Model Key", inp={"row": "@fm.Array Element"}); g.n("mih", "call_self", function="Is Item Hidden", inp={"name": "@mk.key"})
    g.branch("mbih", "@mih.yes"); g.set("mhf", "TmpFound", inp={"TmpFound": "true"})
    g.get("gn2", "TmpNames4"); g.link("gn2.TmpNames4", "return.groups")
    g.chain("entry", "clr", "hf0", "fe"); g.chain("fe", "add", "bih", "hf1")
    g.chain("fe:Completed", "fm"); g.chain("fm", "madd", "mbih", "mhf")
    g.chain("fm:Completed", "bhf", "addh", "return"); g.chain("bhf:else", "return")
    return fn("Skin Groups", outputs=[param("groups", "name", "array")], graph=g)


def f_rebuild_weapon_chips():
    """Chip row of the weapons tab: All, "..." (collapse), one chip per Skin Groups entry; hidden with one group only."""
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Weapon SubTabs", inp={"self": "@gp.Panel"})
    g.get("gcw", "CurrentWeapon"); g.n("sk", "call_self", function="Skins For Weapon", inp={"weapon": "@gcw.CurrentWeapon"}); g.n("gr", "call_self", function="Skin Groups")
    g.n("srt", "call_self", function="Sort Chips", inp={"groups": "@gr.groups", "look": "true"})   # mods alphabetically, Vanilla first, Hidden last
    g.set("sgr", "TmpNames3", inp={"TmpNames3": "@srt.sorted"}); g.get("ggr", "TmpNames3"); g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@ggr.TmpNames3"})
    g.call("gt1", K_MATH, "Greater_IntInt", inp={"A": "@len.ReturnValue", "B": "1"}); g.get("gpv", "Panel"); g.call("vis", W_PANEL, "Set Weapon Chips Visible", inp={"self": "@gpv.Panel", "visible": "@gt1.ReturnValue"}); g.branch("b", "@gt1.ReturnValue")
    aw = create_widget(g, "ca", W_SUB); set_manager(g, "sma", W_SUB, aw)
    g.get("gcg", "SkinGroup"); g.call("selA", K_MATH, "EqualEqual_NameName", inp={"A": "@gcg.SkinGroup", "B": "None"})
    g.call("ia", W_SUB, "Init", inp={"self": aw, "group": "None", "caption": tt(g, "ta", "Chip_All"), "selected": "@selA.ReturnValue"})
    g.get("gp2", "Panel"); g.call("aa", W_PANEL, "Add Weapon SubTab", inp={"self": "@gp2.Panel", "widget": aw})
    mw = create_widget(g, "cm", W_SUB); set_manager(g, "smm", W_SUB, mw); g.get("gcol", "SkinChipsCollapsed")
    g.call("im", W_SUB, "Init", inp={"self": mw, "group": "AltUI_More", "caption": tt(g, "tm", "Chip_More"), "selected": "@gcol.SkinChipsCollapsed"})
    g.get("gpm", "Panel"); g.call("am", W_PANEL, "Add Weapon SubTab", inp={"self": "@gpm.Panel", "widget": mw})
    g.get("ggr2", "TmpNames3"); g.foreach("fe", "@ggr2.TmpNames3")
    g.get("gcg2", "SkinGroup"); g.call("selG", K_MATH, "EqualEqual_NameName", inp={"A": "@gcg2.SkinGroup", "B": "@fe.Array Element"})
    g.get("gcol2", "SkinChipsCollapsed"); g.call("ncol", K_MATH, "Not_PreBool", inp={"A": "@gcol2.SkinChipsCollapsed"})
    g.call("show", K_MATH, "BooleanOR", inp={"A": "@ncol.ReturnValue", "B": "@selG.ReturnValue"}); g.branch("bs", "@show.ReturnValue")
    sw = create_widget(g, "cs", W_SUB); set_manager(g, "sms", W_SUB, sw)
    g.get("gcol3", "SkinChipsCollapsed"); g.call("fullc", K_MATH, "BooleanAND", inp={"A": "@gcol3.SkinChipsCollapsed", "B": "@selG.ReturnValue"})
    g.n("cap", "call_self", function="Look Chip Caption", inp={"group": "@fe.Array Element", "full": "@fullc.ReturnValue"})
    g.call("is", W_SUB, "Init", inp={"self": sw, "group": "@fe.Array Element", "caption": "@cap.caption", "selected": "@selG.ReturnValue"})
    g.get("gp3", "Panel"); g.call("as", W_PANEL, "Add Weapon SubTab", inp={"self": "@gp3.Panel", "widget": sw})
    g.chain("entry", "cl", "sk", "gr", "srt", "sgr", "vis", "b", "ca_cr", "sma", "ia", "aa", "cm_cr", "smm", "im", "am", "fe"); g.chain("fe", "bs", "cs_cr", "sms", "cap", "is", "as")
    return fn("Rebuild Weapon Chips", graph=g)


def f_select_skin_group():
    g = G(); g.call("ism", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "AltUI_More"}); g.branch("bm", "@ism.ReturnValue")
    g.get("gcol", "SkinChipsCollapsed"); g.call("ncol", K_MATH, "Not_PreBool", inp={"A": "@gcol.SkinChipsCollapsed"}); g.set("scol", "SkinChipsCollapsed", inp={"SkinChipsCollapsed": "@ncol.ReturnValue"})
    g.n("svm", "call_self", function="Save Settings"); g.n("rtm", "call_self", function="Rebuild Weapon Chips")
    g.set("s", "SkinGroup", inp={"SkinGroup": "@entry.name"}); g.n("rt", "call_self", function="Rebuild Weapon Chips"); g.n("rl", "call_self", function="Rebuild Weapon Skins")
    g.n("rmg", "call_self", function="Rebuild Weapon Models"); g.n("rw", "call_self", function="Rebuild Weapons")   # hits per weapon (left column), before the row lists are refilled
    g.chain("entry", "bm", "scol", "svm", "rtm"); g.chain("bm:else", "s", "rw", "rt", "rl", "rmg")
    return fn("Select Skin Group", [param("name", "name")], graph=g)


def f_rebuild_weapon_links():
    """The x that clears the weapons search box."""
    g = G(); g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Weapon Search Links", inp={"self": "@gp.Panel"})
    xw = create_widget(g, "cx", W_TXT); set_manager(g, "smx", W_TXT, xw)
    g.call("xt", K_TXT, "Conv_StringToText", inp={"InString": "\u00d7"}); g.call("xi", W_TXT, "Init", inp={"self": xw, "action": "ClearWeaponSearch", "caption": "@xt.ReturnValue"})
    g.get("gp2", "Panel"); g.call("al", W_PANEL, "Add Weapon Search Link", inp={"self": "@gp2.Panel", "widget": xw})
    g.chain("entry", "cl", "cx_cr", "smx", "xi", "al")
    return fn("Rebuild Weapon Links", graph=g)


def f_on_weapon_search_changed():
    g = G(); g.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@entry.text"})
    g.get("gst", "WeaponSearchText"); g.call("neq", K_STR, "NotEqual_StrStr", inp={"A": "@t2s.ReturnValue", "B": "@gst.WeaponSearchText"}); g.branch("b", "@neq.ReturnValue")
    g.set("s", "WeaponSearchText", inp={"WeaponSearchText": "@t2s.ReturnValue"})
    g.get("gpg", "Page"); g.call("isw", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Weapons"}); g.branch("bw", "@isw.ReturnValue")
    g.n("rc", "call_self", function="Rebuild Weapon Chips"); g.n("rk", "call_self", function="Rebuild Weapon Skins"); g.n("rkm", "call_self", function="Rebuild Weapon Models")
    g.n("rw", "call_self", function="Rebuild Weapons")   # the hits per weapon in the left column; first: it borrows the row lists the others fill again
    g.chain("entry", "b", "s", "bw", "rw", "rc", "rk", "rkm")
    return fn("On Weapon Search Changed", [param("text", "text")], graph=g)


def f_toggle_skin_favorite():
    g = G(); g.n("k", "call_self", function="Skin Key", inp={"row": "@entry.name"}); g.set("sk", "TmpName2", inp={"TmpName2": "@k.key"})
    g.get("gk", "TmpName2"); g.n("isf", "call_self", function="Is Favorite", inp={"name": "@gk.TmpName2"}); g.branch("b", "@isf.yes")
    g.get("gf", "Favorites"); g.get("gk1", "TmpName2"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gf.Favorites", "Item": "@gk1.TmpName2"})
    g.get("gf2", "Favorites"); g.get("gk2", "TmpName2"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gf2.Favorites", "NewItem": "@gk2.TmpName2"})
    g.n("sv", "call_self", function="Save Settings"); g.n("rl", "call_self", function="Rebuild Weapon Skins")
    g.chain("entry", "sk", "b", "rm", "sv"); g.chain("b:else", "add", "sv"); g.chain("sv", "rl")
    return fn("Toggle Skin Favorite", [param("name", "name")], graph=g)


def f_toggle_skin_hidden():
    g = G(); g.n("k", "call_self", function="Skin Key", inp={"row": "@entry.name"}); g.set("sk", "TmpName2", inp={"TmpName2": "@k.key"})
    g.get("gk", "TmpName2"); g.n("ish", "call_self", function="Is Item Hidden", inp={"name": "@gk.TmpName2"}); g.branch("b", "@ish.yes")
    g.get("gh", "HiddenItems"); g.get("gk1", "TmpName2"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gh.HiddenItems", "Item": "@gk1.TmpName2"})
    g.get("gh2", "HiddenItems"); g.get("gk2", "TmpName2"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gh2.HiddenItems", "NewItem": "@gk2.TmpName2"})
    g.n("sv", "call_self", function="Save Settings"); g.n("gr", "call_self", function="Skin Groups")
    g.call("hasH", K_ARR, "Array_Contains", inp={"TargetArray": "@gr.groups", "ItemToFind": g.lit_name("hn", "Hidden")})
    g.get("gg", "SkinGroup"); g.call("onH", K_MATH, "EqualEqual_NameName", inp={"A": "@gg.SkinGroup", "B": "Hidden"}); g.call("nh", K_MATH, "Not_PreBool", inp={"A": "@hasH.ReturnValue"})
    g.call("back", K_MATH, "BooleanAND", inp={"A": "@onH.ReturnValue", "B": "@nh.ReturnValue"}); g.branch("bb", "@back.ReturnValue"); g.set("sg", "SkinGroup", inp={"SkinGroup": "None"})
    g.n("rch", "call_self", function="Rebuild Weapon Chips"); g.n("rl", "call_self", function="Rebuild Weapon Skins"); g.n("rlm", "call_self", function="Rebuild Weapon Models")
    g.chain("entry", "sk", "b", "rm", "sv"); g.chain("b:else", "add", "sv"); g.chain("sv", "gr", "bb", "sg", "rch"); g.chain("bb:else", "rch"); g.chain("rch", "rl", "rlm")
    return fn("Toggle Skin Hidden", [param("name", "name")], graph=g)


def f_skin_only_mod():
    g = G(); g.n("sm", "call_self", function="Skin Mod", inp={"row": "@entry.name"}); g.branch("b", "@sm.found"); g.n("mal", "call_self", function="Mod Alias", inp={"mod": "@sm.mod"})
    g.n("sg", "call_self", function="Select Skin Group", inp={"name": "@mal.alias"})
    g.chain("entry", "b", "sg"); return fn("Skin Only Mod", [param("name", "name")], graph=g)


def f_on_skin_context():
    """Skin tile menu: favourite on/off, hide/unhide, [only this mod for a skin mod row], cancel."""
    def pre(g):
        g.set("sci", "ContextItem", inp={"ContextItem": "@entry.name"})
        g.n("isf", "call_self", function="Is Skin Favorite", inp={"name": "@entry.name"}); g.call("fs", K_MATH, "SelectString", inp={"A": ts(g, "fr", "Menu_FavRemove"), "B": ts(g, "fa", "Menu_FavAdd"), "bPickA": "@isf.yes"})
        g.call("ft", K_TXT, "Conv_StringToText", inp={"InString": "@fs.ReturnValue"})
        g.n("k", "call_self", function="Skin Key", inp={"row": "@entry.name"}); g.n("ihd", "call_self", function="Is Item Hidden", inp={"name": "@k.key"})
        g.call("hs", K_MATH, "SelectString", inp={"A": ts(g, "hu", "Menu_Unhide"), "B": ts(g, "hh", "Menu_Hide"), "bPickA": "@ihd.yes"})
        g.call("ht", K_TXT, "Conv_StringToText", inp={"InString": "@hs.ReturnValue"}); return ["sci"]
    g = simple_menu("On Skin Context", [("SkinFav", "@ft.ReturnValue"), ("SkinHide", "@ht.ReturnValue"), ("SkinOnlyMod", "Menu_LookOnlyMod"), ("Cancel", "Menu_Cancel")], pre=pre, cond={"SkinOnlyMod": "Skin Mod"})
    return fn("On Skin Context", [param("name", "name")], graph=g)


def f_rebuild_look_links():
    """The x that clears the appearance search box (like the clothes search)."""
    g = G(); g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Look Search Links", inp={"self": "@gp.Panel"})
    xw = create_widget(g, "cx", W_TXT); set_manager(g, "smx", W_TXT, xw)
    g.call("xt", K_TXT, "Conv_StringToText", inp={"InString": "\u00d7"}); g.call("xi", W_TXT, "Init", inp={"self": xw, "action": "ClearLookSearch", "caption": "@xt.ReturnValue"})
    g.get("gp2", "Panel"); g.call("al", W_PANEL, "Add Look Search Link", inp={"self": "@gp2.Panel", "widget": xw})
    g.get("gp3", "Panel"); g.call("cl2", W_PANEL, "Clear Look Chip Search Links", inp={"self": "@gp3.Panel"})
    xc = create_widget(g, "cxc", W_TXT); set_manager(g, "smxc", W_TXT, xc)
    g.call("xtc", K_TXT, "Conv_StringToText", inp={"InString": "\u00d7"}); g.call("xic", W_TXT, "Init", inp={"self": xc, "action": "ClearLookChipSearch", "caption": "@xtc.ReturnValue"})
    g.get("gp4", "Panel"); g.call("al2", W_PANEL, "Add Look Chip Search Link", inp={"self": "@gp4.Panel", "widget": xc})
    g.chain("entry", "cl", "cx_cr", "smx", "xi", "al", "cl2", "cxc_cr", "smxc", "xic", "al2")
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
    # "only worn" = what the tile already draws as selected: Is Look Selected. Behind a branch, so that with the filter
    # off the path through Player.Get Makeup Data is not taken at all (editor tests have no player).
    g.set("w0", "TmpWorn", inp={"TmpWorn": "true"})
    g.get("gow", "LookOnlyWorn"); g.branch("bow", "@gow.LookOnlyWorn")
    g.n("lto", "call_self", function="Look Type Of", inp={"name": "@entry.row"})
    g.n("sel", "call_self", function="Is Look Selected", inp={"type": "@lto.type", "style": "@entry.row"})
    g.set("w1", "TmpWorn", inp={"TmpWorn": "@sel.yes"})
    g.get("gtw", "TmpWorn")
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@lm.yes", "B": "@chip.ReturnValue"}); g.call("a2a", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@fok.ReturnValue"})
    g.call("a2", K_MATH, "BooleanAND", inp={"A": "@a2a.ReturnValue", "B": "@gtw.TmpWorn"})
    g.set("st", "TmpBool", inp={"TmpBool": "@a2.ReturnValue"}); g.get("gt", "TmpBool"); g.link("gt.TmpBool", "return.yes")
    g.chain("entry", "k", "w0", "bow", "lto", "sel", "w1", "st", "return"); g.chain("bow:else", "st")
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


def f_on_look_chip_search_changed():
    """Panel key-up: the appearance page's chip search box -> LookChipSearchText; rebuild only the chips."""
    g = G(); g.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@entry.text"})
    g.get("gst", "LookChipSearchText"); g.call("neq", K_STR, "NotEqual_StrStr", inp={"A": "@t2s.ReturnValue", "B": "@gst.LookChipSearchText"}); g.branch("b", "@neq.ReturnValue")
    g.set("s", "LookChipSearchText", inp={"LookChipSearchText": "@t2s.ReturnValue"})
    g.n("rc", "call_self", function="Rebuild Look Chips")
    g.chain("entry", "b", "s", "rc")
    return fn("On Look Chip Search Changed", [param("text", "text")], graph=g)


def f_look_chip_shown():
    """Does Rebuild Look Chips show this mod chip? Like Chip Shown, only with LookGroup / LookChipsCollapsed and the mod's
    caption as the display name."""
    g = G()
    g.get("gcst", "LookChipSearchText"); g.call("cse", K_STR, "IsEmpty", inp={"InString": "@gcst.LookChipSearchText"}); g.call("csa", K_MATH, "Not_PreBool", inp={"A": "@cse.ReturnValue"})
    g.get("gcg", "LookGroup"); g.call("selG", K_MATH, "EqualEqual_NameName", inp={"A": "@gcg.LookGroup", "B": "@entry.group"})
    g.n("mcp", "call_self", function="Mod Caption", inp={"mod": "@entry.group"})
    g.get("gcst2", "LookChipSearchText"); g.n("cm", "call_self", function="Name Matches", inp={"kind": "mod", "row": "@entry.group", "default": "@mcp.s", "search": "@gcst2.LookChipSearchText"})
    g.call("hit", K_MATH, "BooleanOR", inp={"A": "@cse.ReturnValue", "B": "@cm.yes"})
    g.call("hitS", K_MATH, "BooleanOR", inp={"A": "@hit.ReturnValue", "B": "@selG.ReturnValue"})
    g.get("gcol", "LookChipsCollapsed"); g.call("ncol", K_MATH, "Not_PreBool", inp={"A": "@gcol.LookChipsCollapsed"})
    g.call("open", K_MATH, "BooleanOR", inp={"A": "@ncol.ReturnValue", "B": "@csa.ReturnValue"})
    g.call("show0", K_MATH, "BooleanOR", inp={"A": "@open.ReturnValue", "B": "@selG.ReturnValue"})
    g.call("show", K_MATH, "BooleanAND", inp={"A": "@show0.ReturnValue", "B": "@hitS.ReturnValue"})
    g.link("show.ReturnValue", "return.yes")
    return fn("Look Chip Shown", [param("group", "name")], [param("yes", "bool")], graph=g, pure=True)


def f_rebuild_look_chips():
    """Chip row of the appearance page (Rebuild SubTabs for mods): All, "..." (collapse), one chip per Look Groups entry; hidden for presets
    and when there is nothing to choose (one group)."""
    g = G()
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Look SubTabs", inp={"self": "@gp.Panel"})
    g.get("glc", "LookCat"); g.call("isp", K_MATH, "EqualEqual_NameName", inp={"A": "@glc.LookCat", "B": "Presets"}); g.branch("bp", "@isp.ReturnValue")
    g.get("gpv0", "Panel"); g.call("hide", W_PANEL, "Set Look Chips Visible", inp={"self": "@gpv0.Panel", "visible": "false"})
    g.get("gpv0b", "Panel"); g.call("hide2", W_PANEL, "Set Look Chip Search Visible", inp={"self": "@gpv0b.Panel", "visible": "false"})
    g.get("glc2", "LookCat"); g.n("col", "call_self", function="Collect Look Rows", inp={"type": "@glc2.LookCat"}); g.n("gr", "call_self", function="Look Groups")
    g.n("srt", "call_self", function="Sort Chips", inp={"groups": "@gr.groups", "look": "true"})   # mods alphabetically, Vanilla first, Hidden last
    g.set("sgr", "TmpNames3", inp={"TmpNames3": "@srt.sorted"}); g.get("ggr", "TmpNames3"); g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@ggr.TmpNames3"})
    g.call("gt1", K_MATH, "Greater_IntInt", inp={"A": "@len.ReturnValue", "B": "1"}); g.get("gpv", "Panel"); g.call("vis", W_PANEL, "Set Look Chips Visible", inp={"self": "@gpv.Panel", "visible": "@gt1.ReturnValue"})
    g.get("gcsh", "ChipSearchShown"); g.call("lcsv", K_MATH, "BooleanAND", inp={"A": "@gt1.ReturnValue", "B": "@gcsh.ChipSearchShown"})
    g.get("gpvb", "Panel"); g.call("vis2", W_PANEL, "Set Look Chip Search Visible", inp={"self": "@gpvb.Panel", "visible": "@lcsv.ReturnValue"})
    g.branch("b", "@gt1.ReturnValue")
    aw = create_widget(g, "ca", W_SUB); set_manager(g, "sma", W_SUB, aw)
    g.get("gcg", "LookGroup"); g.call("selA", K_MATH, "EqualEqual_NameName", inp={"A": "@gcg.LookGroup", "B": "None"})
    g.call("ia", W_SUB, "Init", inp={"self": aw, "group": "None", "caption": tt(g, "ta", "Chip_All"), "selected": "@selA.ReturnValue"})
    g.get("gp2", "Panel"); g.call("aa", W_PANEL, "Add Look SubTab", inp={"self": "@gp2.Panel", "widget": aw})
    mw = create_widget(g, "cm", W_SUB); set_manager(g, "smm", W_SUB, mw); g.get("gcol", "LookChipsCollapsed")
    g.call("im", W_SUB, "Init", inp={"self": mw, "group": "AltUI_More", "caption": tt(g, "tm", "Chip_More"), "selected": "@gcol.LookChipsCollapsed"})
    g.get("gpm", "Panel"); g.call("am", W_PANEL, "Add Look SubTab", inp={"self": "@gpm.Panel", "widget": mw})
    g.get("ggr2", "TmpNames3"); g.foreach("fe", "@ggr2.TmpNames3")
    g.get("gcg2", "LookGroup"); g.call("selG", K_MATH, "EqualEqual_NameName", inp={"A": "@gcg2.LookGroup", "B": "@fe.Array Element"})
    g.n("lcs", "call_self", function="Look Chip Shown", inp={"group": "@fe.Array Element"}); g.branch("bs", "@lcs.yes")
    sw = create_widget(g, "cs", W_SUB); set_manager(g, "sms", W_SUB, sw)
    g.get("gcol3", "LookChipsCollapsed"); g.call("fullc", K_MATH, "BooleanAND", inp={"A": "@gcol3.LookChipsCollapsed", "B": "@selG.ReturnValue"})
    g.n("cap", "call_self", function="Look Chip Caption", inp={"group": "@fe.Array Element", "full": "@fullc.ReturnValue"})
    g.call("is", W_SUB, "Init", inp={"self": sw, "group": "@fe.Array Element", "caption": "@cap.caption", "selected": "@selG.ReturnValue"})
    g.get("gp3", "Panel"); g.call("as", W_PANEL, "Add Look SubTab", inp={"self": "@gp3.Panel", "widget": sw})
    g.chain("entry", "cl", "bp", "hide", "hide2"); g.chain("bp:else", "col", "gr", "srt", "sgr", "vis", "vis2", "b", "ca_cr", "sma", "ia", "aa", "cm_cr", "smm", "im", "am", "fe"); g.chain("fe", "bs", "cs_cr", "sms", "cap", "is", "as")
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
    g.n("pdn", "call_self", function="Preset Shown Name", inp={"index": "@fp.Array Index"})
    g.call("pis", K_STR, "Conv_IntToString", inp={"InInt": "@fp.Array Index"}); g.call("pn1", K_STR, "Concat_StrStr", inp={"A": "Preset_", "B": "@pis.ReturnValue"}); g.call("pnn", K_STR, "Conv_StringToName", inp={"InString": "@pn1.ReturnValue"})
    g.n("pm", "call_self", function="Look Matches", inp={"kind": "preset", "row": "@pnn.ReturnValue", "shown": "@pdn.s"}); g.call("pok", K_MATH, "BooleanOR", inp={"A": "@nfl.ReturnValue", "B": "@pm.yes"}); g.branch("bpk", "@pok.ReturnValue")
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
    g.call("noact0", K_MATH, "BooleanAND", inp={"A": "@sne0.ReturnValue", "B": "@gno.ReturnValue"})
    g.get("gowc", "LookOnlyWorn"); g.call("nowc", K_MATH, "Not_PreBool", inp={"A": "@gowc.LookOnlyWorn"})   # "only worn" narrows the category just as the other filters do
    g.call("noact1", K_MATH, "BooleanAND", inp={"A": "@noact0.ReturnValue", "B": "@nof.ReturnValue"})
    g.call("noact", K_MATH, "BooleanAND", inp={"A": "@noact1.ReturnValue", "B": "@nowc.ReturnValue"})
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
        # eye / eyelash rows carry their colour on a material parameter, make-up rows are painted over by AltUI:
        # both kinds get the colour-wheel badge, only the skin rows do not
        item = make_item(g, q + "mi", row_pin, "@%sb.%s" % (q, icon), kind=tk, color=("true" if t in ("e", "m") else None))
        chain = look_tile(g, q + "t", item, "@%ssel.yes" % q, "true", add_fn, "@%scap.caption" % q, kind=tk, fav_pin=fav_pin)
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
    pw = create_widget(g, "cpa", W_OUTFIT); set_manager(g, "smpa", W_OUTFIT, pw); g.get("pts", "TileScale")   # among the preset tiles: their size
    g.get("gi1", "TmpIcons"); g.call("pai", W_OUTFIT, "Init", inp={"self": pw, "index": "-1", "icons": "@gi1.TmpIcons", "count": "0", "caption": tt(g, "pct", "Btn_SavePreset"), "photo": "true", "scale": "@pts.TileScale", "cols": "3", "rows": "3"})
    g.get("gpa", "Panel"); g.call("paa", W_PANEL, "Add Look", inp={"self": "@gpa.Panel", "widget": pw})
    pd = presets_data(g, "pd"); g.foreach("fp", pd); g.brk("bpr", P_PRESET_S, "@fp.Array Element")
    g.n("pic", "call_self", function="Preset Icon", inp={"number": "@bpr.IconNumber"})
    g.call("pis", K_STR, "Conv_IntToString", inp={"InInt": "@fp.Array Index"}); g.call("pn1", K_STR, "Concat_StrStr", inp={"A": "Preset_", "B": "@pis.ReturnValue"}); g.call("pnn", K_STR, "Conv_StringToName", inp={"InString": "@pn1.ReturnValue"})
    g.n("pdn", "call_self", function="Preset Shown Name", inp={"index": "@fp.Array Index"})
    g.make("mip", S_ITEM, Name="@pnn.ReturnValue", DisplayName="@pdn.s", Icon="@pic.tex")
    g.n("pmt", "call_self", function="Look Matches", inp={"kind": "preset", "row": "@pnn.ReturnValue", "shown": "@pdn.s"}); g.branch("bpm", "@pmt.yes")   # appearance search
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
    g.n("aec", "call_self", function="Apply Eye Colors")   # the game writes the EyeTable colour there - AltUI's comes after
    g.n("amc", "call_self", function="Apply Makeup Colors")
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
    g.n("amc2", "call_self", function="Apply Makeup Colors")
    # finish
    g.set("sd", "MakeupDirty", inp={"MakeupDirty": "true"}); g.n("rl", "call_self", function="Rebuild Look")
    g.n("ph", "call_self", function="Push History")
    g.chain("entry", "svc", "ba", "lto", "bln"); g.chain("bln:else", "slc", "bp"); g.chain("ba:else", "bp"); g.chain("bp", "pix", "pcl"); g.chain("bp:else", "md", "bs", "ph", "cs", "sd"); g.chain("bs:else", "trow", "ph2", "sel", "be", "bes", "erm", "ues"); g.chain("bes:else", "eclr", "eadd", "eset", "ues"); g.chain("ues", "aec", "amc", "sd")
    g.chain("be:else", "sl", "bms", "beb", "sd"); g.chain("beb:else", "mrm", "bgt"); g.chain("bms:else", "bsg", "mclr", "madd", "bgt"); g.chain("bsg:else", "madd")
    g.chain("bgt", "mset", "srow"); g.chain("bgt:else", "mrem", "srow"); g.chain("srow", "ban", "pm", "umt"); g.chain("ban:else", "umt"); g.chain("srow:Row Not Found", "umt"); g.chain("umt", "amc2", "sd"); g.chain("sd", "rlc", "rl")
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
    # bone-scale sliders: reset chip, slider positions from the body's factors ((f - FACTOR_MIN) / (FACTOR_MAX - FACTOR_MIN)), enabled only with AltUI's ABP, notice otherwise
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
    g.get("gfd", "FaceDirty"); g.branch("bfd", "@gfd.FaceDirty"); g.n("svs", "call_self", function="Save Settings"); g.set("sfd", "FaceDirty", inp={"FaceDirty": "false"})   # face slider moves: saved once here
    g.chain("entry", "bd", "sv", "sd", "bb", "rp", "sb", "bfd", "svs", "sfd"); g.chain("bd:else", "bb"); g.chain("bb:else", "bfd")
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
    g.call("istp", K_STR, "StartsWith", inp={"SourceString": "@n2s.ReturnValue", "InPrefix": "ThemeP:", "SearchCase": "CaseSensitive"}); g.branch("btp", "@istp.ReturnValue")
    g.n("atp", "call_self", function="Apply Theme Preset", inp={"name": "@entry.name"})   # saved colour scheme chip (options)
    g.call("istb", K_STR, "StartsWith", inp={"SourceString": "@n2s.ReturnValue", "InPrefix": "Tab:", "SearchCase": "CaseSensitive"}); g.branch("btb", "@istb.ReturnValue")
    g.call("tbs", K_STR, "GetSubstring", inp={"SourceString": "@n2s.ReturnValue", "StartIndex": "4", "Length": "64"}); g.call("tbn", K_STR, "Conv_StringToName", inp={"InString": "@tbs.ReturnValue"})
    g.n("ttb", "call_self", function="Toggle Tab Hidden", inp={"page": "@tbn.ReturnValue"})   # tab visibility chip (options)
    g.call("istsa", K_STR, "StartsWith", inp={"SourceString": "@n2s.ReturnValue", "InPrefix": "TabStyle", "SearchCase": "CaseSensitive"})
    g.call("istsb", K_STR, "StartsWith", inp={"SourceString": "@n2s.ReturnValue", "InPrefix": "TabIconPos", "SearchCase": "CaseSensitive"})
    g.call("ists", K_MATH, "BooleanOR", inp={"A": "@istsa.ReturnValue", "B": "@istsb.ReturnValue"}); g.branch("bts", "@ists.ReturnValue")
    g.n("sts", "call_self", function="Select Tab Style", inp={"name": "@entry.name"})   # tab bar style / icon position chip (options)
    g.n("sl", "call_self", function="Select Layout", inp={"name": "@entry.name"})
    g.get("gpg2", "Page"); g.call("isb", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg2.Page", "B": "Body"}); g.branch("bb", "@isb.ReturnValue")
    g.get("gpgm", "Page"); g.call("ismg", K_MATH, "EqualEqual_NameName", inp={"A": "@gpgm.Page", "B": "Manage"}); g.branch("bmgp", "@ismg.ReturnValue")
    g.n("smg", "call_self", function="Select Manage Group", inp={"name": "@entry.name"})   # Manage chip
    g.n("sb", "call_self", function="Select Body", inp={"name": "@entry.name"})
    g.set("hlc", "HighlightItem", inp={"HighlightItem": "None"})
    g.call("ism", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "AltUI_More"})
    g.get("gpg3", "Page"); g.call("isc", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg3.Page", "B": "Clothes"})
    g.call("mok", K_MATH, "BooleanAND", inp={"A": "@ism.ReturnValue", "B": "@isc.ReturnValue"}); g.branch("bm", "@mok.ReturnValue")
    g.get("gcol", "SubTabsCollapsed"); g.call("ncol", K_MATH, "Not_PreBool", inp={"A": "@gcol.SubTabsCollapsed"}); g.set("scol", "SubTabsCollapsed", inp={"SubTabsCollapsed": "@ncol.ReturnValue"})
    g.n("svm", "call_self", function="Save Settings"); g.n("rtm", "call_self", function="Rebuild SubTabs")
    g.n("rl", "call_self", function="Rebuild Left")   # the group chip filters the slot counts ("total (in group)")
    g.get("gpg5", "Page"); g.call("isps", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg5.Page", "B": "Poses"}); g.branch("bps", "@isps.ReturnValue"); g.n("spg", "call_self", function="Select Pose Group", inp={"name": "@entry.name"})
    g.get("gpg6", "Page"); g.call("isws", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg6.Page", "B": "Weapons"}); g.branch("bws", "@isws.ReturnValue"); g.n("ssg", "call_self", function="Select Skin Group", inp={"name": "@entry.name"})
    g.get("gpg4", "Page"); g.call("islk", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg4.Page", "B": "Look"}); g.branch("blk", "@islk.ReturnValue"); g.n("slgp", "call_self", function="Select Look Group", inp={"name": "@entry.name"})
    g.chain("entry", "bo", "bl", "slg"); g.chain("bl:else", "bk", "sk"); g.chain("bk:else", "bcf", "tcf"); g.chain("bcf:else", "btp", "atp"); g.chain("btp:else", "bun", "sun"); g.chain("bun:else", "bts", "sts"); g.chain("bts:else", "btb", "ttb"); g.chain("btb:else", "sl"); g.chain("bo:else", "bmgp", "smg"); g.chain("bmgp:else", "bb", "sb"); g.chain("bb:else", "bps", "spg"); g.chain("bps:else", "bws", "ssg"); g.chain("bws:else", "blk", "slgp"); g.chain("blk:else", "bm", "scol", "svm", "rtm"); g.chain("bm:else", "hlc", "s", "rl", "rt", "rli")
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


def palette_show(g, color_pin, flag="0"):
    """Vanilla palette (PaletteUI.Show Palette): create it once, into the viewport, show it with the starting colour.
    The colour is read back from Paletter.Image_Color on Tick (Apply Preview). Returns the exec ids to hang in."""
    g.set("so", "ColorOrig", inp={"ColorOrig": color_pin}); g.set("sc", "ColorCur", inp={"ColorCur": color_pin})
    g.get("gp", "Palette"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gp.Palette"}); g.branch("b", "@iv.ReturnValue")
    pw = create_widget(g, "cp", P_PAL); g.set("sp", "Palette", inp={"Palette": pw})
    g.get("gp2", "Palette"); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@gp2.Palette", "ZOrder": "115"})
    g.get("gp3", "Palette"); g.get("gpn", "Panel"); g.get("glb", "LastButton")
    g.call("show", P_PAL, "Show Palette", inp={"self": "@gp3.Palette", "panel": "@gpn.Panel", "button": "@glb.LastButton", "flag": flag, "initial color": color_pin})
    g.set("sop", "ColorOpen", inp={"ColorOpen": "true"})
    g.chain("b:else", "cp_cr", "sp", "atv"); g.chain("atv", "show", "sop")
    return ["so", "sc", "b", "atv"]


def f_slot_color_key():
    """Key of one material slot in SlotColors: <piece>#<slot index>."""
    g = G()
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"})
    g.call("i2s", K_STR, "Conv_IntToString", inp={"InInt": "@entry.slot"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@n2s.ReturnValue", "B": "#"})
    g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@i2s.ReturnValue"})
    g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@c2.ReturnValue"}); g.link("s2n.ReturnValue", "return.key")
    return fn("Slot Color Key", [param("name", "name"), param("slot", "int")], [param("key", "name")], graph=g, pure=True)


def f_open_slot_color():
    """Palette for one material slot of a worn piece. The starting colour is the stored one, otherwise the colour the
    game keeps for the whole piece, otherwise white."""
    g = G()
    g.set("sci", "ColorItem", inp={"ColorItem": "@entry.name"}); g.set("scs", "ColorSlot", inp={"ColorSlot": "@entry.slot"})
    g.set("scm", "ColorMode", inp={"ColorMode": "Slot"})
    g.n("key", "call_self", function="Slot Color Key", inp={"name": "@entry.name", "slot": "@entry.slot"})
    g.get("gsc", "SlotColors"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gsc.SlotColors", "Key": "@key.key"})
    g.get("gpl", "Player"); g.call("gc", P_CPB, "Get Clothes Color", inp={"self": "@gpl.Player", "clothes name": "@entry.name"})
    g.call("game", K_MATH, "SelectColor", inp={"A": "@gc.color", "B": "(R=1,G=1,B=1,A=1)", "bPickA": "@gc.found"})
    g.call("col", K_MATH, "SelectColor", inp={"A": "@f.Value", "B": "@game.ReturnValue", "bPickA": "@f.ReturnValue"})
    tail = palette_show(g, "@col.ReturnValue")
    g.chain("entry", "sci", "scs", "scm", "gc", *tail)
    return fn("Open Slot Color", [param("name", "name"), param("slot", "int")], graph=g)


def f_item_has_own_color():
    """found = this piece carries a colour of its own - one of AltUI's in SlotColors, or the game's entry for the whole piece."""
    g = G()
    g.set("sf", "ColorProbe", inp={"ColorProbe": "false"})
    g.n("cs", "call_self", function="Item Color Slots", inp={"name": "@entry.name"}); g.brk("bcs", S_COLSLOTS, "@cs.slots")
    g.foreach("fe", "@bcs.Idx")
    g.n("key", "call_self", function="Slot Color Key", inp={"name": "@entry.name", "slot": "@fe.Array Element"})
    g.get("gsc", "SlotColors"); g.call("f", K_MAP, "Map_Contains", inp={"TargetMap": "@gsc.SlotColors", "Key": "@key.key"}); g.branch("bf", "@f.ReturnValue")
    g.set("st", "ColorProbe", inp={"ColorProbe": "true"})
    g.get("gpl", "Player"); g.call("gc", P_CPB, "Get Clothes Color", inp={"self": "@gpl.Player", "clothes name": "@entry.name"}); g.branch("bg", "@gc.found")
    g.set("st2", "ColorProbe", inp={"ColorProbe": "true"})
    g.get("gcp", "ColorProbe"); g.link("gcp.ColorProbe", "return.found")
    # Item Color Slots first, then the flag: its probe (Material Takes Color) writes ColorProbe itself, so setting the
    # flag before the call left the probe's answer in it - a piece without a stored colour then counted as coloured.
    g.chain("entry", "cs", "sf", "fe"); g.chain("fe", "bf", "st")   # "key" is pure: it hangs on bf as data
    g.chain("fe:Completed", "gc", "bg", "st2", "return"); g.chain("bg:else", "return")   # Get Clothes Color is impure: in the chain, or it is pruned
    return fn("Item Has Own Color", [param("name", "name")], [param("found", "bool")], graph=g)


def f_set_slot_color():
    """Put one colour on one material slot of a worn piece. An instance that is already dynamic is used again: a new one
    would leave the game's own instance (the one in Materials for Color) hanging, and its slider dead for that piece."""
    g = G()
    g.get("gpl", "Wearer"); g.call("fc", P_CPB, "Find Clothes Component With Name", inp={"self": "@gpl.Wearer", "name": "@entry.name"})
    g.call("cv", K_SYS, "IsValid", inp={"Object": "@fc.clothes comp"}); g.branch("bv", "@cv.ReturnValue")
    g.cast("cp", E_PRIM, "@fc.clothes comp", pure=False, miss="ignore")
    g.call("gm", E_PRIM, "GetMaterial", inp={"self": "@cp.AsPrimitive Component", "ElementIndex": "@entry.slot"})
    g.cast("cmid", E_MID, "@gm.ReturnValue", pure=False, miss="ignore")
    g.set("s1", "TmpMat", inp={"TmpMat": "@cmid.AsMaterial Instance Dynamic"})
    g.call("mk", E_PRIM, "CreateDynamicMaterialInstance", inp={"self": "@cp.AsPrimitive Component", "ElementIndex": "@entry.slot", "SourceMaterial": "None", "OptionalName": "None"})
    g.set("s2", "TmpMat", inp={"TmpMat": "@mk.ReturnValue"})
    g.get("gtm", "TmpMat"); g.call("sv", E_MID, "SetVectorParameterValue", inp={"self": "@gtm.TmpMat", "ParameterName": "MainColor", "Value": "@entry.color"})
    g.chain("entry", "fc", "bv", "cp", "cmid", "s1", "sv"); g.chain("cmid:CastFailed", "mk", "s2", "sv")   # GetMaterial is pure and hangs on the cast as data; Find Clothes Component is not and has to run
    return fn("Set Slot Color", [param("name", "name"), param("slot", "int"), param("color", S_LINCOLOR)], graph=g)


def f_save_slot_color():
    """Keep the colour of one slot: in AltUI's map always. A piece the game itself would colour (table flag) and that has a
    single colourable slot additionally goes into the game's map - then mirror and outfits see it as before."""
    g = G()
    g.n("key", "call_self", function="Slot Color Key", inp={"name": "@entry.name", "slot": "@entry.slot"})
    g.get("gsc", "SlotColors"); g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gsc.SlotColors", "Key": "@key.key", "Value": "@entry.color"})
    g.n("cs", "call_self", function="Item Color Slots", inp={"name": "@entry.name"}); g.brk("bcs", S_COLSLOTS, "@cs.slots")
    g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@bcs.Idx"}); g.call("one", K_MATH, "EqualEqual_IntInt", inp={"A": "@len.ReturnValue", "B": "1"})
    g.n("row", "get_row", table=P_CT, inp={"RowName": "@entry.name"}, miss="ignore"); g.brk("br", P_CS, "@row.OutRow")
    g.call("both", K_MATH, "BooleanAND", inp={"A": "@one.ReturnValue", "B": "@br.ColorAdjustable"}); g.branch("bb", "@both.ReturnValue")
    g.get("gpl", "Player"); g.call("sv", P_CPB, "Save Clothes Color", inp={"self": "@gpl.Player", "clothes name": "@entry.name", "color": "@entry.color"})
    g.n("ss", "call_self", function="Save Settings")
    g.chain("entry", "add", "cs", "row", "bb", "sv", "ss"); g.chain("bb:else", "ss")
    return fn("Save Slot Color", [param("name", "name"), param("slot", "int"), param("color", S_LINCOLOR)], graph=g)


def f_apply_item_colors():
    """Put the stored slot colours of a worn piece on it. Slots without an entry of their own are not touched."""
    g = G()
    g.n("cs", "call_self", function="Item Color Slots", inp={"name": "@entry.name"}); g.brk("bcs", S_COLSLOTS, "@cs.slots")
    g.foreach("fe", "@bcs.Idx")
    g.n("key", "call_self", function="Slot Color Key", inp={"name": "@entry.name", "slot": "@fe.Array Element"})
    g.get("gsc", "SlotColors"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gsc.SlotColors", "Key": "@key.key"}); g.branch("bf", "@f.ReturnValue")
    g.n("set", "call_self", function="Set Slot Color", inp={"name": "@entry.name", "slot": "@fe.Array Element", "color": "@f.Value"})
    g.chain("entry", "cs", "fe"); g.chain("fe", "bf", "set")
    return fn("Apply Item Colors", [param("name", "name")], graph=g)


def f_apply_all_item_colors():
    """Every worn piece: after a level load (Apply Saved Colors), when the panel opens and after a look has been put on."""
    g = G()
    g.get("gpl", "Wearer"); g.call("wc", P_CPB, "Get Wearing Clothes Names", inp={"self": "@gpl.Wearer"})
    g.set("sn", "TmpNames4", inp={"TmpNames4": "@wc.clothes list"}); g.get("gn", "TmpNames4"); g.foreach("fe", "@gn.TmpNames4")
    g.n("ap", "call_self", function="Apply Item Colors", inp={"name": "@fe.Array Element"})
    g.chain("entry", "wc", "sn", "fe"); g.chain("fe", "ap")
    return fn("Apply All Item Colors", graph=g)


def f_apply_saved_colors():
    """At the end of BeginPlay (main menu / loading scene: in Find Menu Wearer): AltUI's own colours (material slots, eyes, make-up) back on after a level load - the game
    restores only what its own colour map covers, so without this they came back only when the panel was opened.
    Runs after Apply Saved Body and Fix Loaded Underwear, which can still change what is worn."""
    g = G()
    g.n("aic", "call_self", function="Apply All Item Colors"); g.n("aec", "call_self", function="Apply Eye Colors"); g.n("amc", "call_self", function="Apply Makeup Colors")
    g.chain("entry", "aic", "aec", "amc")
    return fn("Apply Saved Colors", graph=g)


def f_reset_dropped_colors():
    """Before the colours of a look go on: every piece that carries one of AltUI's colours now and has none in the look
    goes back to what the game gives it (Restore Clothes Color), or to the snapshot's own colour for it when it has one. Without this a look saved with a plain piece left the
    colour set in the meantime on it - the look's map simply had nothing to say about that piece. A piece AltUI never
    painted is not touched, so a colour from the game's own wardrobe survives."""
    g = G()
    g.get("gsc", "SlotColors"); g.call("keys", K_MAP, "Map_Keys", inp={"TargetMap": "@gsc.SlotColors"})
    g.foreach("fk", "@keys.Keys")
    g.call("k2s", K_STR, "Conv_NameToString", inp={"InName": "@fk.Array Element"})
    g.call("sp", K_STR, "Split", inp={"SourceString": "@k2s.ReturnValue", "InStr": "#", "SearchCase": "CaseSensitive", "SearchDir": "FromStart"})
    g.call("n2n", K_STR, "Conv_StringToName", inp={"InString": "@sp.LeftS"})
    g.call("has", K_MAP, "Map_Contains", inp={"TargetMap": "@entry.next", "Key": "@fk.Array Element"})
    g.call("keep", K_MATH, "Not_PreBool", inp={"A": "@has.ReturnValue"}); g.branch("bk", "@keep.ReturnValue")
    g.get("gpl", "Player"); g.call("rc", P_CPB, "Restore Clothes Color", inp={"self": "@gpl.Player", "clothes": "@n2n.ReturnValue"})
    g.n("ric", "call_self", function="Reset Item Colors", inp={"name": "@n2n.ReturnValue"})   # and repaint it, the same as a reset from the menu
    # a piece the snapshot gives a colour of the game's own (an outfit's colour, set by Wear Queue Step just before) gets it back
    g.call("cf", K_MAP, "Map_Find", inp={"TargetMap": "@entry.colors", "Key": "@n2n.ReturnValue"}); g.branch("bcf", "@cf.ReturnValue")
    g.get("gpl2", "Player"); g.call("fcc", P_CPB, "Find Clothes Component With Name", inp={"self": "@gpl2.Player", "name": "@n2n.ReturnValue"})
    g.call("cv", K_SYS, "IsValid", inp={"Object": "@fcc.clothes comp"}); g.branch("bcv", "@cv.ReturnValue")
    g.call("chg", P_CC, "Change Color", inp={"self": "@fcc.clothes comp", "Color": "@cf.Value"})
    g.get("gpl3", "Player"); g.call("svc", P_CPB, "Save Clothes Color", inp={"self": "@gpl3.Player", "clothes name": "@n2n.ReturnValue", "color": "@cf.Value"})
    g.chain("entry", "keys", "fk"); g.chain("fk", "bk", "rc", "ric", "bcf", "fcc", "bcv", "chg", "svc")
    return fn("Reset Dropped Colors", [param("next", "name", "map", value_type=S_LINCOLOR), param("colors", "name", "map", value_type=S_LINCOLOR)], graph=g)


def f_reset_item_colors():
    """Paint the worn piece back to the colours its own materials carry. Restore Clothes Color only puts the game's
    Default Color on the instances it knows; a piece the game does not colour (no table flag) and every slot beyond the
    first keep the colour until the piece is taken off and put on again. The default of a slot is read from a throwaway
    instance of its material, the same way the probe reads it, and written into the instance that sits on the piece."""
    g = G()
    g.get("gpl", "Player"); g.call("fc", P_CPB, "Find Clothes Component With Name", inp={"self": "@gpl.Player", "name": "@entry.name"})
    g.call("cv", K_SYS, "IsValid", inp={"Object": "@fc.clothes comp"}); g.branch("bv", "@cv.ReturnValue")
    g.cast("cp", E_PRIM, "@fc.clothes comp", pure=False, miss="ignore")
    g.n("row", "get_row", table=P_CT, inp={"RowName": "@entry.name"}, miss="ignore"); g.brk("br", P_CS, "@row.OutRow")
    g.call("mv", K_SYS, "IsValid", inp={"Object": "@br.Mesh"}); g.branch("bm", "@mv.ReturnValue")
    g.get("mats", "Materials", cls=E_SKELMESH); g.link("br.Mesh", "mats.self")
    g.foreach("fe", "@mats.Materials"); g.brk("bs", E_SKELMAT, "@fe.Array Element")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@bs.MaterialSlotName"})
    g.call("fix", K_STR, "Contains", inp={"SearchIn": "@n2s.ReturnValue", "Substring": "FixedColor", "bUseCase": "false", "bSearchFromEnd": "false"})
    g.call("nfix", K_MATH, "Not_PreBool", inp={"A": "@fix.ReturnValue"}); g.branch("bfx", "@nfix.ReturnValue")
    g.n("tc", "call_self", function="Material Takes Color", inp={"mat": "@bs.MaterialInterface"}); g.branch("bt", "@tc.yes")
    g.call("dmi", K_MATLIB, "CreateDynamicMaterialInstance", inp={"Parent": "@bs.MaterialInterface", "OptionalName": "None"})
    g.call("rd", E_MID, "K2_GetVectorParameterValue", inp={"self": "@dmi.ReturnValue", "ParameterName": "MainColor"})
    g.call("gm", E_PRIM, "GetMaterial", inp={"self": "@cp.AsPrimitive Component", "ElementIndex": "@fe.Array Index"})
    g.cast("cmid", E_MID, "@gm.ReturnValue", pure=False, miss="ignore")
    g.call("sv", E_MID, "SetVectorParameterValue", inp={"self": "@cmid.AsMaterial Instance Dynamic", "ParameterName": "MainColor", "Value": "@rd.ReturnValue"})
    g.chain("entry", "fc", "bv", "cp", "row", "bm", "fe")
    g.chain("fe", "bfx", "tc", "bt", "dmi", "rd", "cmid", "sv")
    return fn("Reset Item Colors", [param("name", "name")], graph=g)


def f_slot_reset_color():
    """Every colour of one's own off this piece: AltUI's entries go, then the game's Restore Clothes Color drops its entry
    and puts Default Color back on the instances."""
    g = G()
    g.n("cs", "call_self", function="Item Color Slots", inp={"name": "@entry.name"}); g.brk("bcs", S_COLSLOTS, "@cs.slots")
    g.foreach("fe", "@bcs.Idx")
    g.n("key", "call_self", function="Slot Color Key", inp={"name": "@entry.name", "slot": "@fe.Array Element"})
    g.get("gsc", "SlotColors"); g.call("rm", K_MAP, "Map_Remove", inp={"TargetMap": "@gsc.SlotColors", "Key": "@key.key"})
    g.get("gpl", "Player"); g.call("rc", P_CPB, "Restore Clothes Color", inp={"self": "@gpl.Player", "clothes": "@entry.name"})
    g.n("sv", "call_self", function="Save Settings")
    g.n("ric", "call_self", function="Reset Item Colors", inp={"name": "@entry.name"})   # the values alone are not enough: the worn piece keeps its colour otherwise
    g.chain("entry", "cs", "fe"); g.chain("fe", "rm"); g.chain("fe:Completed", "rc", "ric", "sv")
    return fn("Slot Reset Color", [param("name", "name")], graph=g)


def f_row_is(cat):
    """cond for the appearance tile menu: does the row belong to this category (Eye / Eyelashes)?"""
    def make():
        g = G(); g.n("t", "call_self", function="Look Type Of", inp={"name": "@entry.row"})
        g.call("eq", K_MATH, "EqualEqual_NameName", inp={"A": "@t.type", "B": cat}); g.link("eq.ReturnValue", "return.found")
        g.chain("entry", "t", "return")
        return fn("Row Is " + cat, [param("row", "name")], [param("found", "bool")], graph=g, pure=True)   # cond of simple_menu: pure, like Item Mod
    return make()


def f_eye_color_key():
    """Key of one eye colour: <part>#<row> - the colour belongs to the lens (or the lashes) it was chosen on."""
    g = G()
    g.call("p2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.part"})
    g.call("r2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.row"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@p2s.ReturnValue", "B": "#"})
    g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@r2s.ReturnValue"})
    g.call("s2n", K_STR, "Conv_StringToName", inp={"InString": "@c2.ReturnValue"}); g.link("s2n.ReturnValue", "return.key")
    return fn("Eye Color Key", [param("part", "name"), param("row", "name")], [param("key", "name")], graph=g, pure=True)


def f_current_look_row():
    """The row worn in an appearance category (Makeup Data[type].List, first entry); None when nothing is on."""
    g = G(); md = makeup_data(g, "md")
    g.set("z", "TmpName3", inp={"TmpName3": "None"})
    g.get("gmd", "Makeup Data", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "gmd.self")
    g.call("fnd", K_MAP, "Map_Find", inp={"TargetMap": "@gmd.Makeup Data", "Key": "@entry.type"}); g.brk("bl", P_MDATA_S, "@fnd.Value")
    g.branch("bf", "@fnd.ReturnValue")
    g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@bl.List"}); g.call("gt0", K_MATH, "Greater_IntInt", inp={"A": "@len.ReturnValue", "B": "0"}); g.branch("bn", "@gt0.ReturnValue")
    g.call("get", K_ARR, "Array_Get", inp={"TargetArray": "@bl.List", "Index": "0"}); g.set("sn", "TmpName3", inp={"TmpName3": "@get.Item"})
    g.get("gr", "TmpName3"); g.link("gr.TmpName3", "return.row")
    g.chain("entry", "z", "md", "bf", "bn", "sn", "return"); g.chain("bf:else", "return"); g.chain("bn:else", "return")
    return fn("Current Look Row", [param("type", "name")], [param("row", "name")], graph=g)


# A material cooked in this repo is useless here: this toolchain can only cook LinuxNoEditor (the engine build has no
# Windows target platform), and a material's shader map is platform-specific - in the Windows game it falls back to the
# default material, which paints an opaque black box. So AltUI borrows a material the GAME ships, whose shaders are right:
# ShaderClothes takes MainTex and MainColor, and the mod kit has it too, so bpgen can resolve the reference.
M_TINT = "/Game/Project/Material/ShaderClothes"
M_TINT2 = "/Game/Project/Material/ShaderPrincipled"   # the other candidate, only used by the probe
TINT_PARAM = "MainColor"
MAKEUP_SCALE = 0.5            # the game draws make-up at half the table's coordinates (Render Makeup Texture)


def f_apply_makeup_colors():
    """Let the game draw everything but the coloured entries, and draw those here - each exactly once.

    Two earlier ways were wrong. Painting AltUI's colour over the game's layer put the same drawing on twice, and in its
    soft edge the coverage adds up (a rim around the lips, reaching onto the skin). Clearing the target and drawing
    every entry here was worse: the game draws an entry through its skin material, AltUI draws the plain texture, and
    for its own textures that is not the same picture - eye shadow and liner came out as a pale film.

    So: take the coloured entries out of Makeup Data, let Update Makeup Texture render the rest exactly as always, put
    the map back, and draw only AltUI's entries on top. Nothing else is touched."""
    g = G()
    g.get("gpl", "Wearer"); g.get("gmt", "Makeup Tex", cls=P_JODI_BASE); g.link("gpl.Wearer", "gmt.self")
    g.call("tv", K_SYS, "IsValid", inp={"Object": "@gmt.Makeup Tex"}); g.branch("btv", "@tv.ReturnValue")
    g.get("gmc0", "MakeupColors"); g.call("cnt", K_MAP, "Map_Length", inp={"TargetMap": "@gmc0.MakeupColors"})
    g.call("any", K_MATH, "Greater_IntInt", inp={"A": "@cnt.ReturnValue", "B": "0"}); g.branch("bany", "@any.ReturnValue")
    md = makeup_data(g, "md")
    g.get("gmd", "Makeup Data", cls=P_MAKEUP_SAVE); g.link("md.Makeup Data", "gmd.self")
    g.set("bak", "MakeupBak", inp={"MakeupBak": "@gmd.Makeup Data"})   # the lists come back untouched afterwards
    g.get("gmc", "MakeupColors"); g.call("keys", K_MAP, "Map_Keys", inp={"TargetMap": "@gmc.MakeupColors"})
    g.set("sk", "TmpNames4", inp={"TmpNames4": "@keys.Keys"})
    # pass 1: take every coloured entry that is worn out of its type's list
    g.get("gk", "TmpNames4"); g.foreach("fe", "@gk.TmpNames4")
    g.n("lto", "call_self", function="Look Type Of", inp={"name": "@fe.Array Element"})
    g.call("kn", K_MATH, "NotEqual_NameName", inp={"A": "@lto.type", "B": "None"}); g.branch("bkn", "@kn.ReturnValue")
    g.call("mf", K_MAP, "Map_Find", inp={"TargetMap": "@gmd.Makeup Data", "Key": "@lto.type"}); g.brk("bl", P_MDATA_S, "@mf.Value")
    g.branch("bmf", "@mf.ReturnValue")
    g.call("rmv", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@bl.List", "Item": "@fe.Array Element"})
    g.make("mks", P_MDATA_S, List="@bl.List")
    g.call("put", K_MAP, "Map_Add", inp={"TargetMap": "@gmd.Makeup Data", "Key": "@lto.type", "Value": "@mks.MakeupDataStruct"})
    # the game renders what is left, exactly as it always does
    g.get("gpl2", "Wearer"); g.call("umt", P_JODI_BASE, "Update Makeup Texture", inp={"self": "@gpl2.Wearer"})
    g.get("gbak", "MakeupBak"); g.n("smd", "set", var="Makeup Data", cls=P_MAKEUP_SAVE, inp={"self": md, "Makeup Data": "@gbak.MakeupBak"})
    # pass 2: AltUI's entries, once each, on top
    g.call("beg", K_REND, "BeginDrawCanvasToRenderTarget", inp={"TextureRenderTarget": "@gmt.Makeup Tex"})
    g.get("gk2", "TmpNames4"); g.foreach("fe2", "@gk2.TmpNames4")
    g.n("lto2", "call_self", function="Look Type Of", inp={"name": "@fe2.Array Element"})
    g.call("kn2", K_MATH, "NotEqual_NameName", inp={"A": "@lto2.type", "B": "None"}); g.branch("bkn2", "@kn2.ReturnValue")
    g.n("sel", "call_self", function="Is Look Selected", inp={"type": "@lto2.type", "style": "@fe2.Array Element"}); g.branch("bsel", "@sel.yes")
    g.n("row", "get_row", table=P_MAKEUP_T, inp={"RowName": "@fe2.Array Element"}, miss="ignore"); g.brk("br", P_MAKEUP_S, "@row.OutRow")
    g.get("gmc2", "MakeupColors"); g.call("fc", K_MAP, "Map_Find", inp={"TargetMap": "@gmc2.MakeupColors", "Key": "@fe2.Array Element"})
    g.foreach("frc", "@br.ScreenRect")
    g.call("bs", K_MATH, "BreakVector4", inp={"InVec": "@frc.Array Element"})   # FVector4 has no break node of its own
    g.call("uvok", K_ARR, "Array_IsValidIndex", inp={"TargetArray": "@br.UVRect", "IndexToTest": "@frc.Array Index"})
    g.call("uvg", K_ARR, "Array_Get", inp={"TargetArray": "@br.UVRect", "Index": "@frc.Array Index"})
    g.call("bu", K_MATH, "BreakVector4", inp={"InVec": "@uvg.Item"})
    g.call("ux", K_MATH, "SelectFloat", inp={"A": "@bu.X", "B": "0.0", "bPickA": "@uvok.ReturnValue"})
    g.call("uy", K_MATH, "SelectFloat", inp={"A": "@bu.Y", "B": "0.0", "bPickA": "@uvok.ReturnValue"})
    g.call("uz", K_MATH, "SelectFloat", inp={"A": "@bu.Z", "B": "1.0", "bPickA": "@uvok.ReturnValue"})
    g.call("uw", K_MATH, "SelectFloat", inp={"A": "@bu.W", "B": "1.0", "bPickA": "@uvok.ReturnValue"})
    g.call("uvp", K_MATH, "MakeVector2D", inp={"X": "@ux.ReturnValue", "Y": "@uy.ReturnValue"})
    g.call("uvs", K_MATH, "MakeVector2D", inp={"X": "@uz.ReturnValue", "Y": "@uw.ReturnValue"})
    g.call("pv", K_MATH, "MakeVector2D", inp={"X": "@bs.X", "Y": "@bs.Y"}); g.call("sv", K_MATH, "MakeVector2D", inp={"X": "@bs.Z", "Y": "@bs.W"})
    g.call("pos", K_MATH, "Multiply_Vector2DFloat", inp={"A": "@pv.ReturnValue", "B": str(MAKEUP_SCALE)})
    g.call("siz", K_MATH, "Multiply_Vector2DFloat", inp={"A": "@sv.ReturnValue", "B": str(MAKEUP_SCALE)})
    g.call("zero", K_MATH, "MakeVector2D", inp={"X": "0.0", "Y": "0.0"})
    g.call("draw", E_CANVAS, "K2_DrawTexture", inp={"self": "@beg.Canvas", "RenderTexture": "@br.Texture_d",
                                                    "ScreenPosition": "@pos.ReturnValue", "ScreenSize": "@siz.ReturnValue",
                                                    "CoordinatePosition": "@uvp.ReturnValue", "CoordinateSize": "@uvs.ReturnValue",
                                                    "RenderColor": "@fc.Value", "BlendMode": "BLEND_Translucent",
                                                    "Rotation": "0.0", "PivotPoint": "@zero.ReturnValue"})
    g.call("end", K_REND, "EndDrawCanvasToRenderTarget", inp={"Context": "@beg.Context"})
    g.chain("entry", "btv", "bany", "md", "bak", "keys", "sk", "fe")
    g.chain("fe", "lto", "bkn", "bmf", "rmv", "put")
    g.chain("fe:Completed", "umt", "smd", "beg", "fe2")
    g.chain("fe2", "lto2", "bkn2", "sel", "bsel", "row", "frc"); g.chain("frc", "draw")
    g.chain("fe2:Completed", "end")
    return fn("Apply Makeup Colors", graph=g)


def f_open_makeup_color():
    """Palette for one make-up row (ColorMode Makeup). A row that is not on is put on first."""
    g = G()
    g.n("lto", "call_self", function="Look Type Of", inp={"name": "@entry.name"})
    g.n("sel", "call_self", function="Is Look Selected", inp={"type": "@lto.type", "style": "@entry.name"}); g.branch("bs", "@sel.yes")
    g.n("lc", "call_self", function="Look Clicked", inp={"name": "@entry.name"})
    g.set("sci", "ColorItem", inp={"ColorItem": "@entry.name"}); g.set("scm", "ColorMode", inp={"ColorMode": "Makeup"})
    g.get("gmc", "MakeupColors"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gmc.MakeupColors", "Key": "@entry.name"})
    g.call("col", K_MATH, "SelectColor", inp={"A": "@f.Value", "B": "(R=1,G=1,B=1,A=1)", "bPickA": "@f.ReturnValue"})
    tail = palette_show(g, "@col.ReturnValue")
    g.chain("entry", "lto", "sel", "bs", "sci", "scm", *tail); g.chain("bs:else", "lc", "sci")
    return fn("Open Makeup Color", [param("name", "name")], graph=g)


def f_set_makeup_color():
    """Store the colour of one row and show it at once (AltUI's layer is drawn over the game's, so no full rebuild)."""
    g = G()
    g.get("gmc", "MakeupColors"); g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gmc.MakeupColors", "Key": "@entry.row", "Value": "@entry.color"})
    g.n("ap", "call_self", function="Apply Makeup Colors")
    g.chain("entry", "add", "ap")
    return fn("Set Makeup Color", [param("row", "name"), param("color", S_LINCOLOR)], graph=g)


def f_makeup_reset_color():
    """Back to the make-up as the game draws it: drop the entry, let the game rebuild the layer, put the colours of the
    other rows back on."""
    g = G()
    g.get("gmc", "MakeupColors"); g.call("rm", K_MAP, "Map_Remove", inp={"TargetMap": "@gmc.MakeupColors", "Key": "@entry.name"})
    g.get("gpl", "Player"); g.call("umt", P_JODI, "Update Makeup Texture", inp={"self": "@gpl.Player"})
    g.n("ap", "call_self", function="Apply Makeup Colors"); g.n("sv", "call_self", function="Save Settings")
    g.chain("entry", "rm", "umt", "ap", "sv")
    return fn("Makeup Reset Color", [param("name", "name")], graph=g)


def f_row_has_makeup_color():
    """cond of the tile menu: is a colour of one's own stored for this row?"""
    g = G(); g.get("gmc", "MakeupColors"); g.call("c", K_MAP, "Map_Contains", inp={"TargetMap": "@gmc.MakeupColors", "Key": "@entry.row"})
    g.link("c.ReturnValue", "return.found")
    return fn("Row Has Makeup Color", [param("row", "name")], [param("found", "bool")], graph=g, pure=True)


def f_row_is_makeup():
    """cond of the tile menu: a row of the make-up table (eyes and lashes come from the eye table and have their own)."""
    g = G(); g.call("ex", K_DT, "DoesDataTableRowExist", inp={"Table": P_MAKEUP_T, "RowName": "@entry.row"})
    g.link("ex.ReturnValue", "return.found"); g.chain("entry", "ex", "return")   # impure
    return fn("Row Is Makeup", [param("row", "name")], [param("found", "bool")], graph=g, pure=True)


def f_makeup_probe():
    """Debug only (ALTUI_MAKEUPPROBE): two bands over Jodi's make-up target, each drawn with a dynamic instance of a
    material the game ships - the upper one ShaderClothes, the lower one ShaderPrincipled, both with MainTex = AltUI's white
    rounded mask and MainColor = blue. A band that shows up blue and rounded is a material make-up can be painted with;
    a band that is a black rectangle is the engine's default material, i.e. that one is no good either."""
    g = G()
    g.get("gpl", "Player"); g.get("gmt", "Makeup Tex", cls=P_JODI); g.link("gpl.Player", "gmt.self")
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@gmt.Makeup Tex"}); g.branch("bv", "@iv.ReturnValue")
    g.call("beg", K_REND, "BeginDrawCanvasToRenderTarget", inp={"TextureRenderTarget": "@gmt.Makeup Tex"})
    g.call("bs", K_MATH, "BreakVector2D", inp={"InVec": "@beg.Size"})
    g.call("half", K_MATH, "Divide_FloatFloat", inp={"A": "@bs.Y", "B": "2.0"})
    tail = ["beg"]
    for i, mat in enumerate((M_TINT, M_TINT2)):
        q = "p%d" % i
        g.call(q + "mid", K_MATLIB, "CreateDynamicMaterialInstance", inp={"Parent": mat, "OptionalName": "None"})
        g.call(q + "tx", E_MID, "SetTextureParameterValue", inp={"self": "@%smid.ReturnValue" % q, "ParameterName": "MainTex", "Value": T_ROUNDBOX})
        g.call(q + "cl", E_MID, "SetVectorParameterValue", inp={"self": "@%smid.ReturnValue" % q, "ParameterName": TINT_PARAM, "Value": "(R=0,G=0,B=1,A=1)"})
        g.call(q + "y", K_MATH, "Multiply_FloatFloat", inp={"A": "@half.ReturnValue", "B": str(float(i))})
        g.call(q + "pos", K_MATH, "MakeVector2D", inp={"X": "0.0", "Y": "@%sy.ReturnValue" % q})
        g.call(q + "siz", K_MATH, "MakeVector2D", inp={"X": "@bs.X", "Y": "@half.ReturnValue"})
        g.call(q + "uv0", K_MATH, "MakeVector2D", inp={"X": "0.0", "Y": "0.0"})
        g.call(q + "uv1", K_MATH, "MakeVector2D", inp={"X": "1.0", "Y": "1.0"})
        g.call(q + "dr", E_CANVAS, "K2_DrawMaterial", inp={"self": "@beg.Canvas", "RenderMaterial": "@%smid.ReturnValue" % q,
                                                            "ScreenPosition": "@%spos.ReturnValue" % q, "ScreenSize": "@%ssiz.ReturnValue" % q,
                                                            "CoordinatePosition": "@%suv0.ReturnValue" % q, "CoordinateSize": "@%suv1.ReturnValue" % q,
                                                            "Rotation": "0.0", "PivotPoint": "@%suv0.ReturnValue" % q})
        tail += [q + "mid", q + "tx", q + "cl", q + "dr"]
    g.call("end", K_REND, "EndDrawCanvasToRenderTarget", inp={"Context": "@beg.Context"})
    g.chain("entry", "bv", *tail, "end")
    return fn("Makeup Probe", graph=g)


def f_open_makeup_color():
    """Palette for one make-up row (ColorMode Makeup). A row that is not on is put on first."""
    g = G()
    g.n("lto", "call_self", function="Look Type Of", inp={"name": "@entry.name"})
    g.n("sel", "call_self", function="Is Look Selected", inp={"type": "@lto.type", "style": "@entry.name"}); g.branch("bs", "@sel.yes")
    g.n("lc", "call_self", function="Look Clicked", inp={"name": "@entry.name"})
    g.set("sci", "ColorItem", inp={"ColorItem": "@entry.name"}); g.set("scm", "ColorMode", inp={"ColorMode": "Makeup"})
    g.get("gmc", "MakeupColors"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gmc.MakeupColors", "Key": "@entry.name"})
    g.call("col", K_MATH, "SelectColor", inp={"A": "@f.Value", "B": "(R=1,G=1,B=1,A=1)", "bPickA": "@f.ReturnValue"})
    tail = palette_show(g, "@col.ReturnValue")
    g.chain("entry", "lto", "sel", "bs", "sci", "scm", *tail); g.chain("bs:else", "lc", "sci")
    return fn("Open Makeup Color", [param("name", "name")], graph=g)


def f_set_makeup_color():
    """Store the colour of one row and show it at once (AltUI's layer is drawn over the game's, so no full rebuild)."""
    g = G()
    g.get("gmc", "MakeupColors"); g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gmc.MakeupColors", "Key": "@entry.row", "Value": "@entry.color"})
    g.n("ap", "call_self", function="Apply Makeup Colors")
    g.chain("entry", "add", "ap")
    return fn("Set Makeup Color", [param("row", "name"), param("color", S_LINCOLOR)], graph=g)


def f_makeup_reset_color():
    """Back to the make-up as the game draws it: drop the entry, let the game rebuild the layer, put the colours of the
    other rows back on."""
    g = G()
    g.get("gmc", "MakeupColors"); g.call("rm", K_MAP, "Map_Remove", inp={"TargetMap": "@gmc.MakeupColors", "Key": "@entry.name"})
    g.get("gpl", "Player"); g.call("umt", P_JODI, "Update Makeup Texture", inp={"self": "@gpl.Player"})
    g.n("ap", "call_self", function="Apply Makeup Colors"); g.n("sv", "call_self", function="Save Settings")
    g.chain("entry", "rm", "umt", "ap", "sv")
    return fn("Makeup Reset Color", [param("name", "name")], graph=g)


def f_row_has_makeup_color():
    """cond of the tile menu: is a colour of one's own stored for this row?"""
    g = G(); g.get("gmc", "MakeupColors"); g.call("c", K_MAP, "Map_Contains", inp={"TargetMap": "@gmc.MakeupColors", "Key": "@entry.row"})
    g.link("c.ReturnValue", "return.found")
    return fn("Row Has Makeup Color", [param("row", "name")], [param("found", "bool")], graph=g, pure=True)


def f_row_is_makeup():
    """cond of the tile menu: a row of the make-up table (eyes and lashes come from the eye table and have their own)."""
    g = G(); g.call("ex", K_DT, "DoesDataTableRowExist", inp={"Table": P_MAKEUP_T, "RowName": "@entry.row"})
    g.link("ex.ReturnValue", "return.found"); g.chain("entry", "ex", "return")   # impure
    return fn("Row Is Makeup", [param("row", "name")], [param("found", "bool")], graph=g, pure=True)


def f_makeup_probe():
    """Debug only (ALTUI_MAKEUPPROBE): paint eight stripes, alternating magenta and green, over Jodi's make-up render
    target. Both colours carry the same alpha, so what differs on her skin is the colour alone."""
    g = G()
    g.get("gpl", "Player"); g.get("gmt", "Makeup Tex", cls=P_JODI); g.link("gpl.Player", "gmt.self")
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@gmt.Makeup Tex"}); g.branch("bv", "@iv.ReturnValue")
    g.call("beg", K_REND, "BeginDrawCanvasToRenderTarget", inp={"TextureRenderTarget": "@gmt.Makeup Tex"})
    g.call("bs", K_MATH, "BreakVector2D", inp={"InVec": "@beg.Size"})
    g.call("sw", K_MATH, "Divide_FloatFloat", inp={"A": "@bs.X", "B": "8.0"})   # eight stripes across the whole target
    tail = ["beg"]   # BreakVector2D is pure
    for i in range(8):
        col = "(R=1,G=0,B=1,A=1)" if i % 2 == 0 else "(R=0,G=1,B=0,A=1)"
        g.call("x%d" % i, K_MATH, "Multiply_FloatFloat", inp={"A": "@sw.ReturnValue", "B": str(float(i))})
        g.call("p%d" % i, K_MATH, "MakeVector2D", inp={"X": "@x%d.ReturnValue" % i, "Y": "0.0"})
        g.call("s%d" % i, K_MATH, "MakeVector2D", inp={"X": "@sw.ReturnValue", "Y": "@bs.Y"})
        g.call("c%d" % i, K_MATH, "MakeVector2D", inp={"X": "0.0", "Y": "0.0"})
        g.call("u%d" % i, K_MATH, "MakeVector2D", inp={"X": "1.0", "Y": "1.0"})
        g.call("d%d" % i, E_CANVAS, "K2_DrawTexture", inp={"self": "@beg.Canvas", "RenderTexture": T_ROUNDBOX,
                                                           "ScreenPosition": "@p%d.ReturnValue" % i, "ScreenSize": "@s%d.ReturnValue" % i,
                                                           "CoordinatePosition": "@c%d.ReturnValue" % i, "CoordinateSize": "@u%d.ReturnValue" % i,
                                                           "RenderColor": col, "BlendMode": "BLEND_Opaque", "Rotation": "0.0",
                                                           "PivotPoint": "@c%d.ReturnValue" % i})
        tail.append("d%d" % i)
    g.call("end", K_REND, "EndDrawCanvasToRenderTarget", inp={"Context": "@beg.Context"})
    g.chain("entry", "bv", *tail, "end")
    return fn("Makeup Probe", graph=g)


# ---------------- Face tab: FaceValues (morph -> weight, face.py) on Jodi's mesh ----------------
def f_apply_face():
    """Every face morph off the component's override list first (SetMorphTarget with bRemoveZeroWeight: gone = the
    animation decides again), then each morph that FaceValues holds back on with bRemoveZeroWeight = false - a 0 stays on
    the list and holds the morph at 0 against the animation. The engine applies the list after the animation curves.
    Morph targets add up, and every expression is a whole face that opens the mouth a bit: unless FaceAdd is on, the
    expressions are scaled down together when their sum exceeds 1 (blended). Mouth_Close is no morph: it is taken off
    Mouth_AH (face.VIRTUAL), which is set as soon as one of the two is fixed."""
    g = G()
    g.get("gpl", "Wearer"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gpl.Wearer"}); g.branch("bv", "@iv.ReturnValue")
    g.get("gmc", "Mesh", cls=E_CHARACTER); g.link("gpl.Wearer", "gmc.self")
    tail = ["bv"]
    for i, m in enumerate(fc.MORPHS):
        g.call("rm%d" % i, E_SKELMESHCOMP, "SetMorphTarget", inp={"self": "@gmc.Mesh", "MorphTargetName": m, "Value": "0.0", "bRemoveZeroWeight": "true"}); tail.append("rm%d" % i)
    find = lambda id, key: (g.get(id + "g", "FaceValues"), g.call(id, K_MAP, "Map_Find", inp={"TargetMap": "@%sg.FaceValues" % id, "Key": g.lit_name(id + "k", key)}))
    # blend factor: 1 / sum of the expressions when that exceeds 1 and FaceAdd is off, else 1
    total = "0.0"
    for j, e in enumerate(fc.EXPRESSIONS):
        find("x%d" % j, e); g.call("xs%d" % j, K_MATH, "Add_FloatFloat", inp={"A": total, "B": "@x%d.Value" % j}); total = "@xs%d.ReturnValue" % j
    g.call("over", K_MATH, "Greater_FloatFloat", inp={"A": total, "B": "1.0"}); g.get("gadd", "FaceAdd"); g.call("nadd", K_MATH, "Not_PreBool", inp={"A": "@gadd.FaceAdd"})
    g.call("scl", K_MATH, "BooleanAND", inp={"A": "@over.ReturnValue", "B": "@nadd.ReturnValue"}); g.call("safe", K_MATH, "FMax", inp={"A": total, "B": "1.0"})
    g.call("inv", K_MATH, "Divide_FloatFloat", inp={"A": "1.0", "B": "@safe.ReturnValue"}); g.call("fac", K_MATH, "SelectFloat", inp={"A": "@inv.ReturnValue", "B": "1.0", "bPickA": "@scl.ReturnValue"})
    g.set("sfac", "TmpFloat", inp={"TmpFloat": "@fac.ReturnValue"}); tail.append("sfac")
    folded = {v[0]: (k, v[1]) for k, v in fc.VIRTUAL.items()}   # morph -> (virtual key, factor)
    for i, m in enumerate(fc.MORPHS):
        p = "m%d" % i; find(p + "f", m); fixed, val = "@%sf.ReturnValue" % p, "@%sf.Value" % p
        if m in folded:
            vk, k = folded[m]; find(p + "v", vk)
            g.call(p + "or", K_MATH, "BooleanOR", inp={"A": fixed, "B": "@%sv.ReturnValue" % p}); fixed = "@%sor.ReturnValue" % p
            g.call(p + "vm", K_MATH, "Multiply_FloatFloat", inp={"A": "@%sv.Value" % p, "B": str(-k)})
            g.call(p + "sub", K_MATH, "Subtract_FloatFloat", inp={"A": val, "B": "@%svm.ReturnValue" % p}); val = "@%ssub.ReturnValue" % p
        elif m in fc.EXPRESSIONS:
            g.get(p + "gf", "TmpFloat"); g.call(p + "mul", K_MATH, "Multiply_FloatFloat", inp={"A": val, "B": "@%sgf.TmpFloat" % p}); val = "@%smul.ReturnValue" % p
        g.branch(p + "b", fixed)
        g.call(p + "set", E_SKELMESHCOMP, "SetMorphTarget", inp={"self": "@gmc.Mesh", "MorphTargetName": m, "Value": val, "bRemoveZeroWeight": "false"})
        g.chain(p + "b", p + "set")
    # exec: entry -> removals -> factor -> per morph: branch (set on true), both ends join the next morph
    g.chain("entry", *tail)
    prev = ["sfac"]
    for i, _ in enumerate(fc.MORPHS):
        p = "m%d" % i
        for t in prev: g.chain(t, p + "b")
        prev = [p + "set", p + "b:else"]
    return fn("Apply Face", graph=g)


def f_face_row_changed():
    """A row of the face tab changed (W_FaceRow): fixed -> the entry's morph(s) into FaceValues (gaze: the side of the
    value gets |value|, the other side 0), not fixed -> out of FaceValues. Apply at once; saved when the panel closes.
    The group counts are redrawn only when the fixed state flipped (not on every slider step)."""
    g = G(); prev = "entry"
    for i, e in enumerate(fc.ENTRIES):
        key, _, neg, pos = e; p = "e%d" % i
        g.call(p + "eq", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.key", "B": key}); g.branch(p + "b", "@%seq.ReturnValue" % p)
        g.chain(prev, p + "b"); prev = p + "b:else"
        g.get(p + "gw", "FaceValues"); g.call(p + "was", K_MAP, "Map_Contains", inp={"TargetMap": "@%sgw.FaceValues" % p, "Key": g.lit_name(p + "kw", pos)})
        g.call(p + "flip", K_MATH, "NotEqual_BoolBool", inp={"A": "@%swas.ReturnValue" % p, "B": "@entry.fixed"}); g.set(p + "sf", "TmpBool", inp={"TmpBool": "@%sflip.ReturnValue" % p})
        g.branch(p + "bf", "@entry.fixed")
        on, off = [], []
        if neg:
            g.call(p + "abs", K_MATH, "Abs", inp={"A": "@entry.value"})
            g.call(p + "lt", K_MATH, "Less_FloatFloat", inp={"A": "@entry.value", "B": "0.0"}); g.call(p + "gt", K_MATH, "Greater_FloatFloat", inp={"A": "@entry.value", "B": "0.0"})
            g.call(p + "vn", K_MATH, "SelectFloat", inp={"A": "@%sabs.ReturnValue" % p, "B": "0.0", "bPickA": "@%slt.ReturnValue" % p})
            g.call(p + "vp", K_MATH, "SelectFloat", inp={"A": "@%sabs.ReturnValue" % p, "B": "0.0", "bPickA": "@%sgt.ReturnValue" % p})
            vals = [(neg, "@%svn.ReturnValue" % p), (pos, "@%svp.ReturnValue" % p)]
        else:
            vals = [(pos, "@entry.value")]
        for j, (m, v) in enumerate(vals):
            g.get(p + "ga%d" % j, "FaceValues"); g.call(p + "add%d" % j, K_MAP, "Map_Add", inp={"TargetMap": "@%sga%d.FaceValues" % (p, j), "Key": g.lit_name(p + "ka%d" % j, m), "Value": v}); on.append(p + "add%d" % j)
            g.get(p + "gr%d" % j, "FaceValues"); g.call(p + "rem%d" % j, K_MAP, "Map_Remove", inp={"TargetMap": "@%sgr%d.FaceValues" % (p, j), "Key": g.lit_name(p + "kr%d" % j, m)}); off.append(p + "rem%d" % j)
        g.chain(p + "b", p + "sf", p + "bf", *on, "af"); g.chain(p + "bf:else", *off, "af")
    g.n("af", "call_self", function="Apply Face"); g.set("sd", "FaceDirty", inp={"FaceDirty": "true"})
    g.get("gtb", "TmpBool"); g.branch("bfl", "@gtb.TmpBool"); g.n("rg", "call_self", function="Rebuild Face Groups")
    g.chain("af", "sd", "bfl", "rg")
    return fn("Face Row Changed", [param("key", "name"), param("fixed", "bool"), param("value", "float")], graph=g)


def f_face_all_fixed():
    """'Fix all': every key not in FaceValues goes in at 0 (gaze: centre) - the face then no longer follows any animation."""
    g = G(); prev = ["entry"]
    for i, m in enumerate(fc.KEYS):
        g.get("gc%d" % i, "FaceValues"); g.call("c%d" % i, K_MAP, "Map_Contains", inp={"TargetMap": "@gc%d.FaceValues" % i, "Key": g.lit_name("kc%d" % i, m)}); g.branch("b%d" % i, "@c%d.ReturnValue" % i)
        g.get("ga%d" % i, "FaceValues"); g.call("a%d" % i, K_MAP, "Map_Add", inp={"TargetMap": "@ga%d.FaceValues" % i, "Key": g.lit_name("ka%d" % i, m), "Value": g.lit_float("va%d" % i, "0.0")})
        for t in prev: g.chain(t, "b%d" % i)
        g.chain("b%d:else" % i, "a%d" % i); prev = ["b%d" % i, "a%d" % i]
    g.n("af", "call_self", function="Apply Face"); g.n("sv", "call_self", function="Save Settings"); g.n("rp", "call_self", function="Rebuild Face Page")
    for t in prev: g.chain(t, "af")
    g.chain("af", "sv", "rp")
    return fn("Face All Fixed", graph=g)


def f_toggle_face_add():
    """Expressions added up (FaceAdd) or blended to a sum of at most 100 % (default)."""
    g = G(); g.get("ga", "FaceAdd"); g.call("nt", K_MATH, "Not_PreBool", inp={"A": "@ga.FaceAdd"}); g.set("s", "FaceAdd", inp={"FaceAdd": "@nt.ReturnValue"})
    g.n("af", "call_self", function="Apply Face"); g.n("sv", "call_self", function="Save Settings"); g.n("rp", "call_self", function="Rebuild Face Right")
    g.chain("entry", "s", "af", "sv", "rp")
    return fn("Toggle Face Add", graph=g)


def f_face_all_game():
    """'All to the game': FaceValues empty - the game's own face."""
    g = G(); g.get("gf", "FaceValues"); g.call("clr", K_MAP, "Map_Clear", inp={"TargetMap": "@gf.FaceValues"})
    g.n("af", "call_self", function="Apply Face"); g.n("sv", "call_self", function="Save Settings"); g.n("rp", "call_self", function="Rebuild Face Page")
    g.chain("entry", "clr", "af", "sv", "rp")
    return fn("Face All Game", graph=g)


def faces_array(g, id):
    """FacesSave.Faces as a pin (get via class SG_Faces)."""
    g.get(id + "_s", "FacesSave"); g.get(id, "Faces", cls=fc.SG_FACES); g.link(id + "_s.FacesSave", id + ".self"); return "@%s.Faces" % id


def ensure_faces(g):
    """Exec ids that load the saved faces if the manager has none yet: returns (chain head, tails that continue)."""
    g.get("ef_g", "FacesSave"); g.call("ef_v", K_SYS, "IsValid", inp={"Object": "@ef_g.FacesSave"}); g.branch("ef_b", "@ef_v.ReturnValue")
    g.n("ef_l", "call_self", function="Load Faces"); g.chain("ef_b:else", "ef_l"); return ["ef_b"], ["ef_l", "ef_b"]


def f_select_face_group(): 
    g = G(); g.set("s", "FaceGroup", inp={"FaceGroup": "@entry.name"}); g.n("sv", "call_self", function="Save Settings"); g.n("r", "call_self", function="Rebuild Face Page")
    g.chain("entry", "s", "sv", "r"); return fn("Select Face Group", [param("name", "name")], graph=g)


def f_rebuild_face_page():
    g = G(); g.n("rg", "call_self", function="Rebuild Face Groups"); g.n("rr", "call_self", function="Rebuild Face Right"); g.chain("entry", "rg", "rr")
    return fn("Rebuild Face Page", graph=g)


def f_rebuild_face_groups():
    """Left column: expression / gaze / mouth with the number of entries that have a value of their own, then the saved faces with their number."""
    g = G(); head, tails = ensure_faces(g)
    g.get("gp", "Panel"); g.call("cl", W_PANEL, "Clear Face Groups", inp={"self": "@gp.Panel"})
    g.chain("entry", *head)
    for t in tails: g.chain(t, "cl")
    prev = "cl"
    for i, grp in enumerate(fc.GROUPS + [fc.SAVED]):
        p = "g%d" % i
        if grp == fc.SAVED:
            arr = faces_array(g, p + "fa"); g.call(p + "n", K_ARR, "Array_Length", inp={"TargetArray": arr}); cnt = "@%sn.ReturnValue" % p
        else:
            cnt = "0"
            for j, e in enumerate(x for x in fc.ENTRIES if x[1] == grp):
                q = "%se%d" % (p, j)
                g.get(q + "gv", "FaceValues"); g.call(q + "c", K_MAP, "Map_Contains", inp={"TargetMap": "@%sgv.FaceValues" % q, "Key": g.lit_name(q + "k", e[3])})
                g.call(q + "i", K_MATH, "SelectInt", inp={"A": "1", "B": "0", "bPickA": "@%sc.ReturnValue" % q})
                g.call(q + "s", K_MATH, "Add_IntInt", inp={"A": cnt, "B": "@%si.ReturnValue" % q}); cnt = "@%ss.ReturnValue" % q
        tw = create_widget(g, p + "w", W_TAB); set_manager(g, p + "sm", W_TAB, tw)
        g.get(p + "gg", "FaceGroup"); g.call(p + "sel", K_MATH, "EqualEqual_NameName", inp={"A": "@%sgg.FaceGroup" % p, "B": grp})
        g.call(p + "ti", W_TAB, "Init", inp={"self": tw, "slot": grp, "caption": tt(g, p + "t", "Cat_" + grp), "count": cnt, "worn icon": "None",
                                             "selected": "@%ssel.ReturnValue" % p, "has items": "true", "filtered": "-1", "indent": "false"})
        g.get(p + "gp", "Panel"); g.call(p + "ad", W_PANEL, "Add Face Group", inp={"self": "@%sgp.Panel" % p, "widget": tw})
        g.chain(prev, p + "w_cr", p + "sm", p + "ti", p + "ad"); prev = p + "ad"
    return fn("Rebuild Face Groups", graph=g)


def face_link(g, id, action, key):
    """A W_TextButton in the face page's link row -> On Menu Action(action); returns the exec ids."""
    lw = create_widget(g, id, W_TXT); set_manager(g, id + "sm", W_TXT, lw)
    g.call(id + "i", W_TXT, "Init", inp={"self": lw, "action": action, "caption": tt(g, id + "t", key)})
    g.get(id + "gp", "Panel"); g.call(id + "a", W_PANEL, "Add Face Link", inp={"self": "@%sgp.Panel" % id, "widget": lw})
    return [id + "_cr", id + "sm", id + "i", id + "a", hslot_pad(g, id + "p", lw, 16)]


def f_rebuild_face_right():
    """Right side of the face page: the saved faces (tiles), or for a slider group the links (fix all / all to the game), the note
    (what a tick means - or that the current body has no face morphs) and one W_FaceRow per entry with its state from FaceValues."""
    g = G()
    g.get("gp", "Panel"); g.call("clk", W_PANEL, "Clear Face Links", inp={"self": "@gp.Panel"})
    g.get("gp1", "Panel"); g.call("clr", W_PANEL, "Clear Face Rows", inp={"self": "@gp1.Panel"})
    g.get("gp2", "Panel"); g.call("clt", W_PANEL, "Clear Face Tiles", inp={"self": "@gp2.Panel"})
    g.get("gfr", "FaceRows"); g.call("cfr", K_ARR, "Array_Clear", inp={"TargetArray": "@gfr.FaceRows"})
    g.get("gg", "FaceGroup"); g.call("iss", K_MATH, "EqualEqual_NameName", inp={"A": "@gg.FaceGroup", "B": fc.SAVED}); g.branch("bs", "@iss.ReturnValue")
    g.get("gp3", "Panel"); g.call("h0", W_PANEL, "Set Face Hint", inp={"self": "@gp3.Panel", "text": ""}); g.n("rf", "call_self", function="Rebuild Faces")
    links = face_link(g, "l1", "FaceAllFixed", "Btn_FaceAllFixed") + face_link(g, "l2", "FaceAllGame", "Btn_FaceAllGame")
    # expression group: blended / added up (one link, its caption says the current mode)
    g.get("gg2", "FaceGroup"); g.call("isx", K_MATH, "EqualEqual_NameName", inp={"A": "@gg2.FaceGroup", "B": fc.GROUPS[0]}); g.branch("bx", "@isx.ReturnValue")
    lw = create_widget(g, "l3", W_TXT); set_manager(g, "l3sm", W_TXT, lw); g.get("gad", "FaceAdd")
    g.call("l3c", K_MATH, "SelectString", inp={"A": ts(g, "l3ta", "Btn_FaceAdded"), "B": ts(g, "l3tb", "Btn_FaceBlended"), "bPickA": "@gad.FaceAdd"})
    g.call("l3t", K_TXT, "Conv_StringToText", inp={"InString": "@l3c.ReturnValue"})
    g.call("l3i", W_TXT, "Init", inp={"self": lw, "action": "FaceAddToggle", "caption": "@l3t.ReturnValue"})
    g.get("l3gp", "Panel"); g.call("l3a", W_PANEL, "Add Face Link", inp={"self": "@l3gp.Panel", "widget": lw})
    links += ["bx", "l3_cr", "l3sm", "l3i", "l3a", hslot_pad(g, "l3p", lw, 16)]; g.chain("bx:else", "bh")   # not the expression group: straight on to the note
    # note: the body's mesh has the face morphs (Face_Smile stands for all) or not
    g.get("gpl", "Player"); g.get("gmc", "Mesh", cls=E_CHARACTER); g.link("gpl.Player", "gmc.self")
    g.get("gsk", "SkeletalMesh", cls=E_SKINNED); g.link("gmc.Mesh", "gsk.self")
    g.call("mn", E_SKELMESH, "K2_GetAllMorphTargetNames", inp={"self": "@gsk.SkeletalMesh"})
    g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@mn.ReturnValue", "ItemToFind": g.lit_str("hsl", "Face_Smile")}); g.branch("bh", "@has.ReturnValue")
    g.get("gp4", "Panel"); g.call("h1", W_PANEL, "Set Face Hint", inp={"self": "@gp4.Panel", "text": tt(g, "th1", "Lbl_FaceHint")})
    g.get("gp5", "Panel"); g.call("h2", W_PANEL, "Set Face Hint", inp={"self": "@gp5.Panel", "text": tt(g, "th2", "Lbl_FaceNoMorphs")})
    g.chain("entry", "clk", "clr", "clt", "cfr", "bs", "h0", "rf"); g.chain("bs:else", *links, "bh", "h1", "r0"); g.chain("bh:else", "h2", "r0")
    # rows of the chosen group
    prev = "r0"
    for i, grp in enumerate(fc.GROUPS):
        g.get("rg%d" % i, "FaceGroup"); g.call("req%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@rg%d.FaceGroup" % i, "B": grp}); g.branch("r%d" % i, "@req%d.ReturnValue" % i)
        if i: g.chain(prev, "r%d" % i)
        prev = "r%d:else" % i; tail = ["r%d" % i]
        for j, (key, _, neg, pos) in enumerate(x for x in fc.ENTRIES if x[1] == grp):
            q = "g%de%d" % (i, j)
            rw = create_widget(g, q + "w", W_FACEROW); set_manager(g, q + "sm", W_FACEROW, rw)
            g.call(q + "in", W_FACEROW, "Init", inp={"self": rw, "key": key, "caption": tt(g, q + "t", "Face_" + key), "bipolar": "true" if neg else "false"})
            g.get(q + "gv", "FaceValues"); g.call(q + "fp", K_MAP, "Map_Find", inp={"TargetMap": "@%sgv.FaceValues" % q, "Key": g.lit_name(q + "kp", pos)})
            if neg:
                g.get(q + "gv2", "FaceValues"); g.call(q + "fn", K_MAP, "Map_Find", inp={"TargetMap": "@%sgv2.FaceValues" % q, "Key": g.lit_name(q + "kn", neg)})
                g.call(q + "fx", K_MATH, "BooleanOR", inp={"A": "@%sfp.ReturnValue" % q, "B": "@%sfn.ReturnValue" % q}); fixed = "@%sfx.ReturnValue" % q
                g.call(q + "vl", K_MATH, "Subtract_FloatFloat", inp={"A": "@%sfp.Value" % q, "B": "@%sfn.Value" % q}); val = "@%svl.ReturnValue" % q
            else:
                fixed, val = "@%sfp.ReturnValue" % q, "@%sfp.Value" % q
            g.call(q + "ss", W_FACEROW, "Set State", inp={"self": rw, "fixed": fixed, "value": val})
            g.get(q + "gp", "Panel"); g.call(q + "ad", W_PANEL, "Add Face Row", inp={"self": "@%sgp.Panel" % q, "widget": rw})
            g.get(q + "ga", "FaceRows"); g.call(q + "aa", K_ARR, "Array_Add", inp={"TargetArray": "@%sga.FaceRows" % q, "NewItem": rw})
            tail += [q + "w_cr", q + "sm", q + "in", q + "ss", q + "ad", q + "aa"]
        g.chain(*tail)
    return fn("Rebuild Face Right", graph=g)


# ---------------- Saved faces (SG_Faces, slot AltUI_Faces; photos SaveGames/AltUI/Face_<id>.png) ----------------
def f_load_faces():
    g = G()
    g.call("ex", K_GS, "DoesSaveGameExist", inp={"SlotName": fc.FACES_SLOT, "UserIndex": "0"}); g.branch("b", "@ex.ReturnValue")
    g.call("ld", K_GS, "LoadGameFromSlot", inp={"SlotName": fc.FACES_SLOT, "UserIndex": "0"}); g.cast("cl", fc.SG_FACES, "@ld.ReturnValue")
    g.set("s1", "FacesSave", inp={"FacesSave": "@cl.AsSG_Faces"})
    g.call("cr", K_GS, "CreateSaveGameObject", inp={"SaveGameClass": fc.SG_FACES}); g.cast("cc", fc.SG_FACES, "@cr.ReturnValue")
    g.set("s2", "FacesSave", inp={"FacesSave": "@cc.AsSG_Faces"})
    g.get("gs", "FacesSave"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gs.FacesSave"}); g.branch("bv", "@iv.ReturnValue")
    g.chain("entry", "ex", "b", "ld", "s1", "bv"); g.chain("bv:else", "cr", "s2"); g.chain("b:else", "cr")
    return fn("Load Faces", graph=g)


def f_save_faces():
    g = G(); g.get("gs", "FacesSave"); g.call("sv", K_GS, "SaveGameToSlot", inp={"SaveGameObject": "@gs.FacesSave", "SlotName": fc.FACES_SLOT, "UserIndex": "0"})
    g.chain("entry", "sv"); return fn("Save Faces", graph=g)


def default_face_name(g, id, index_pin):
    """T(Lbl_Face) + " " + (index+1) as string pin."""
    g.call(id + "_i", K_MATH, "Add_IntInt", inp={"A": index_pin, "B": "1"}); g.call(id + "_s", K_STR, "Conv_IntToString", inp={"InInt": "@%s_i.ReturnValue" % id})
    g.call(id + "_a", K_STR, "Concat_StrStr", inp={"A": ts(g, id + "_t", "Lbl_Face"), "B": " "}); g.call(id, K_STR, "Concat_StrStr", inp={"A": "@%s_a.ReturnValue" % id, "B": "@%s_s.ReturnValue" % id})
    return "@%s.ReturnValue" % id


def f_add_face():
    """'+' tile: the current face (FaceValues) as a new saved face "Face N", photo of the face, redraw."""
    g = G(); head, tails = ensure_faces(g)
    g.get("gs", "FacesSave"); g.get("gni", "NextId", cls=fc.SG_FACES); g.link("gs.FacesSave", "gni.self")
    g.set("sid", "TmpI", inp={"TmpI": "@gni.NextId"}); g.get("gid", "TmpI")   # freeze the id before NextId is incremented
    arr = faces_array(g, "fa"); g.call("len", K_ARR, "Array_Length", inp={"TargetArray": arr})
    g.get("gfv", "FaceValues"); g.get("gfa", "FaceAdd"); g.make("mk", fc.S_FACE, Name=default_face_name(g, "dn", "@len.ReturnValue"), Id="@gid.TmpI", Values="@gfv.FaceValues", FaceAdd="@gfa.FaceAdd"); g.set("stf", "TmpFace", inp={"TmpFace": "@mk.S_Face"})
    arr2 = faces_array(g, "fb"); g.get("gtf", "TmpFace"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": arr2, "NewItem": "@gtf.TmpFace"})
    g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gid.TmpI", "B": "1"}); g.get("gs2", "FacesSave"); g.n("sni", "set", var="NextId", cls=fc.SG_FACES, inp={"self": "@gs2.FacesSave", "NextId": "@inc.ReturnValue"})
    g.n("sv", "call_self", function="Save Faces"); g.n("cap", "call_self", function="Capture Face Photo", inp={"id": "@gid.TmpI"}); g.n("rp", "call_self", function="Rebuild Face Page")
    g.chain("entry", *head)
    for t in tails: g.chain(t, "sid")
    g.chain("sid", "stf", "add", "sni", "sv", "cap", "rp")
    return fn("Add Face", graph=g)


def f_update_face():
    """Overwrite a saved face with the current one (name and id stay), new photo."""
    g = G(); arr = faces_array(g, "fa"); g.call("get", K_ARR, "Array_Get", inp={"TargetArray": arr, "Index": "@entry.index"}); g.brk("bf", fc.S_FACE, "@get.Item")
    g.set("sid", "TmpI", inp={"TmpI": "@bf.Id"}); g.get("gid", "TmpI"); g.get("gfv", "FaceValues"); g.get("gfa", "FaceAdd")
    g.make("mk", fc.S_FACE, Name="@bf.Name", Id="@gid.TmpI", Values="@gfv.FaceValues", FaceAdd="@gfa.FaceAdd"); g.set("stf", "TmpFace", inp={"TmpFace": "@mk.S_Face"})
    arr2 = faces_array(g, "fb"); g.get("gtf", "TmpFace"); g.call("set", K_ARR, "Array_Set", inp={"TargetArray": arr2, "Index": "@entry.index", "Item": "@gtf.TmpFace", "bSizeToFit": "false"})
    g.get("gfi", "FaceIcons"); g.call("rmi", K_MAP, "Map_Remove", inp={"TargetMap": "@gfi.FaceIcons", "Key": "@gid.TmpI"})
    g.n("sv", "call_self", function="Save Faces"); g.n("cap", "call_self", function="Capture Face Photo", inp={"id": "@gid.TmpI"}); g.n("rp", "call_self", function="Rebuild Face Page")
    g.chain("entry", "sid", "stf", "set", "rmi", "sv", "cap", "rp")
    return fn("Update Face", [param("index", "int")], graph=g)


def f_delete_face():
    g = G(); arr = faces_array(g, "fa"); g.call("get", K_ARR, "Array_Get", inp={"TargetArray": arr, "Index": "@entry.index"}); g.brk("bf", fc.S_FACE, "@get.Item")
    g.get("gfi", "FaceIcons"); g.call("rmi", K_MAP, "Map_Remove", inp={"TargetMap": "@gfi.FaceIcons", "Key": "@bf.Id"})
    arr2 = faces_array(g, "fb"); g.call("rm", K_ARR, "Array_Remove", inp={"TargetArray": arr2, "IndexToRemove": "@entry.index"})
    g.n("sv", "call_self", function="Save Faces"); g.n("rp", "call_self", function="Rebuild Face Page")
    g.chain("entry", "rmi", "rm", "sv", "rp")
    return fn("Delete Face", [param("index", "int")], graph=g)


def f_face_name():
    g = G(); arr = faces_array(g, "fa"); g.call("get", K_ARR, "Array_Get", inp={"TargetArray": arr, "Index": "@entry.index"}); g.brk("bf", fc.S_FACE, "@get.Item")
    g.link("bf.Name", "return.name"); g.chain("entry", "return")
    return fn("Face Name", [param("index", "int")], [param("name", "string")], graph=g)


def f_set_face_name():
    """Trim, cut to 40 chars; empty -> default "Face N"; save; redraw."""
    g = G()
    g.call("t1", K_STR, "Trim", inp={"SourceString": "@entry.name"}); g.call("t2", K_STR, "TrimTrailing", inp={"SourceString": "@t1.ReturnValue"})
    g.call("cut", K_STR, "Left", inp={"SourceString": "@t2.ReturnValue", "Count": "40"}); g.call("len", K_STR, "Len", inp={"S": "@cut.ReturnValue"})
    g.call("emp", K_MATH, "EqualEqual_IntInt", inp={"A": "@len.ReturnValue", "B": "0"})
    g.call("sel", K_MATH, "SelectString", inp={"A": default_face_name(g, "dn", "@entry.index"), "B": "@cut.ReturnValue", "bPickA": "@emp.ReturnValue"})
    arr = faces_array(g, "fa"); g.call("get", K_ARR, "Array_Get", inp={"TargetArray": arr, "Index": "@entry.index"}); g.brk("bf", fc.S_FACE, "@get.Item")
    g.make("mk", fc.S_FACE, Name="@sel.ReturnValue", Id="@bf.Id", Values="@bf.Values", FaceAdd="@bf.FaceAdd"); g.set("stf", "TmpFace", inp={"TmpFace": "@mk.S_Face"})
    arr2 = faces_array(g, "fb"); g.get("gtf", "TmpFace"); g.call("set", K_ARR, "Array_Set", inp={"TargetArray": arr2, "Index": "@entry.index", "Item": "@gtf.TmpFace", "bSizeToFit": "false"})
    g.n("sv", "call_self", function="Save Faces"); g.n("rp", "call_self", function="Rebuild Face Page")
    g.chain("entry", "stf", "set", "sv", "rp")
    return fn("Set Face Name", [param("index", "int"), param("name", "string")], graph=g)


def f_apply_saved_face():
    """A saved face replaces the current one completely - also which entries are left to the game."""
    g = G(); arr = faces_array(g, "fa"); g.call("get", K_ARR, "Array_Get", inp={"TargetArray": arr, "Index": "@entry.index"}); g.brk("bf", fc.S_FACE, "@get.Item")
    g.set("sfa", "FaceAdd", inp={"FaceAdd": "@bf.FaceAdd"})
    g.set("sfv", "FaceValues", inp={"FaceValues": "@bf.Values"}); g.n("af", "call_self", function="Apply Face"); g.n("sv", "call_self", function="Save Settings"); g.n("rp", "call_self", function="Rebuild Face Page")
    g.chain("entry", "sfa", "sfv", "af", "sv", "rp")
    return fn("Apply Saved Face", [param("index", "int")], graph=g)


def f_rebuild_faces():
    """Tiles of the saved faces: '+' (save the current face) first, then one per face with its photo."""
    g = G(); head, tails = ensure_faces(g)
    aw = create_widget(g, "ca", W_FACEBTN); set_manager(g, "sma", W_FACEBTN, aw)
    g.call("et", K_TXT, "Conv_StringToText", inp={"InString": ""}); g.call("ia", W_FACEBTN, "Init", inp={"self": aw, "index": "-1", "icon": "None", "caption": "@et.ReturnValue"})
    g.get("gpa", "Panel"); g.call("aa", W_PANEL, "Add Face Tile", inp={"self": "@gpa.Panel", "widget": aw})
    arr = faces_array(g, "fa"); g.foreach("fe", arr); g.brk("bf", fc.S_FACE, "@fe.Array Element")
    g.n("ic", "call_self", function="Face Icon", inp={"id": "@bf.Id"}); g.call("ct", K_TXT, "Conv_StringToText", inp={"InString": "@bf.Name"})
    fw = create_widget(g, "cw", W_FACEBTN); set_manager(g, "smw", W_FACEBTN, fw)
    g.call("il", W_FACEBTN, "Init", inp={"self": fw, "index": "@fe.Array Index", "icon": "@ic.tex", "caption": "@ct.ReturnValue"})
    g.get("gpo", "Panel"); g.call("al", W_PANEL, "Add Face Tile", inp={"self": "@gpo.Panel", "widget": fw})
    g.chain("entry", *head)
    for t in tails: g.chain(t, "ca_cr")
    g.chain("ca_cr", "sma", "ia", "aa", "fe"); g.chain("fe", "ic", "cw_cr", "smw", "il", "al")
    return fn("Rebuild Faces", graph=g)


def f_on_face_clicked():
    g = G(); g.call("neg", K_MATH, "Less_IntInt", inp={"A": "@entry.index", "B": "0"}); g.branch("b", "@neg.ReturnValue")
    g.n("add", "call_self", function="Add Face"); g.n("ap", "call_self", function="Apply Saved Face", inp={"index": "@entry.index"})
    g.chain("entry", "b", "add"); g.chain("b:else", "ap"); return fn("On Face Clicked", [param("index", "int")], graph=g)


def f_on_face_context():
    def pre(g):
        g.set("scf", "ContextFace", inp={"ContextFace": "@entry.index"}); return ["scf"]
    g = simple_menu("On Face Context", [("FaceApply", "Menu_Apply"), ("FaceView", "Menu_ViewContent"), ("FaceRename", "Menu_Rename"), ("FaceUpdate", "Menu_UpdateFront"), ("FaceUpdateView", "Menu_UpdateView"), ("FaceDelete", "Menu_Delete"), ("Cancel", "Menu_Cancel")], pre)
    return fn("On Face Context", [param("index", "int")], graph=g)


def f_start_face_rename():
    g = G(); g.n("fn", "call_self", function="Face Name", inp={"index": "@entry.index"})
    g.get("glb", "LastButton"); g.cast("cb", W_FACEBTN, "@glb.LastButton"); g.call("cv", K_SYS, "IsValid", inp={"Object": "@cb.AsW_FaceButton"}); g.branch("bv", "@cv.ReturnValue")
    g.call("br", W_FACEBTN, "Begin Rename", inp={"self": "@cb.AsW_FaceButton", "current": "@fn.name"})
    g.chain("entry", "bv", "fn", "br"); return fn("Start Face Rename", [param("index", "int")], graph=g)


def f_capture_face_photo():
    """Face photo: 55 cm in front of the head socket (like the make-up preset icon), 256x256, SaveGames/AltUI/Face_<id>.png."""
    g = G()
    g.get("gpl", "Player"); g.get("gm", "Mesh", cls=E_CHAR); g.link("gpl.Player", "gm.self")
    g.call("head", E_SCENEC, "GetSocketLocation", inp={"self": "@gm.Mesh", "InSocketName": "head"})
    g.call("tgt", K_MATH, "Add_VectorVector", inp={"A": "@head.ReturnValue", "B": "(X=0,Y=0,Z=2)"})
    g.call("dir", K_PATHS, "ProjectSavedDir"); g.call("pdir", K_STR, "Concat_StrStr", inp={"A": "@dir.ReturnValue", "B": "SaveGames/AltUI"})
    g.call("ns", K_STR, "Conv_IntToString", inp={"InInt": "@entry.id"}); g.call("fn1", K_STR, "Concat_StrStr", inp={"A": "Face_", "B": "@ns.ReturnValue"}); g.call("fn2", K_STR, "Concat_StrStr", inp={"A": "@fn1.ReturnValue", "B": ".png"})
    g.set("sk", "PhotoKind", inp={"PhotoKind": "Face"}); g.set("sin", "IconNumber", inp={"IconNumber": "@entry.id"})
    g.n("cap", "call_self", function="Capture Photo", inp={"target": "@tgt.ReturnValue", "distance": "55.0", "rise": "0.0", "width": "256", "height": "256", "dir": "@pdir.ReturnValue", "file": "@fn2.ReturnValue"})
    g.set("spf", "PhotoFace", inp={"PhotoFace": "true"})
    g.chain("entry", "sk", "sin", "spf", "cap"); return fn("Capture Face Photo", [param("id", "int")], graph=g)


def f_face_icon():
    """Load and cache Saved/SaveGames/AltUI/Face_<id>.png; missing -> None (not cached: the file may still be written)."""
    g = G()
    g.get("gi", "FaceIcons"); g.call("fnd", K_MAP, "Map_Find", inp={"TargetMap": "@gi.FaceIcons", "Key": "@entry.id"}); g.branch("b", "@fnd.ReturnValue")
    g.link("fnd.Value", "return.tex")
    g.call("dir", K_PATHS, "ProjectSavedDir"); g.call("ns", K_STR, "Conv_IntToString", inp={"InInt": "@entry.id"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@dir.ReturnValue", "B": "SaveGames/AltUI/Face_"}); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@ns.ReturnValue"})
    g.call("c3", K_STR, "Concat_StrStr", inp={"A": "@c2.ReturnValue", "B": ".png"})
    g.call("imp", K_REND, "ImportFileAsTexture2D", inp={"Filename": "@c3.ReturnValue"})
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@imp.ReturnValue"}); g.branch("bv", "@iv.ReturnValue")
    g.get("gi2", "FaceIcons"); g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gi2.FaceIcons", "Key": "@entry.id", "Value": "@imp.ReturnValue"})
    g.n("r2", "return_new"); g.link("imp.ReturnValue", "r2.tex")
    g.chain("entry", "b", "return"); g.chain("b:else", "imp", "bv", "add", "r2"); g.chain("bv:else", "r2")
    return fn("Face Icon", [param("id", "int")], [param("tex", "object:" + E_TEX2D)], graph=g)


def f_apply_eye_colors():
    """Put the stored eye colours of the lens and the lashes that are currently on onto Jodi's two material instances.
    Has to run after every Update Eyes Style: that call builds the instance anew when it is missing and writes the
    EyeTable colour while doing so."""
    g = G(); tail = ["entry"]; ends = []
    for key, var_name, par, _, cat in EYE_PARTS:
        q = "e" + key
        g.n(q + "cur", "call_self", function="Current Look Row", inp={"type": cat})
        g.call(q + "has", K_MATH, "NotEqual_NameName", inp={"A": "@%scur.row" % q, "B": "None"}); g.branch(q + "bc", "@%shas.ReturnValue" % q)
        g.get(q + "pl", "Wearer"); g.get(q + "m", var_name, cls=P_JODI_BASE); g.link(q + "pl.Wearer", q + "m.self")
        g.call(q + "v", K_SYS, "IsValid", inp={"Object": "@%sm.%s" % (q, var_name)}); g.branch(q + "b", "@%sv.ReturnValue" % q)
        g.n(q + "k", "call_self", function="Eye Color Key", inp={"part": key, "row": "@%scur.row" % q})
        g.get(q + "ec", "EyeColors"); g.call(q + "f", K_MAP, "Map_Find", inp={"TargetMap": "@%sec.EyeColors" % q, "Key": "@%sk.key" % q})
        g.branch(q + "bf", "@%sf.ReturnValue" % q)
        g.call(q + "s", E_MID, "SetVectorParameterValue", inp={"self": "@%sm.%s" % (q, var_name), "ParameterName": par, "Value": "@%sf.Value" % q})
        g.chain(*tail, q + "cur", q + "bc", q + "b", q + "bf", q + "s")
        for e in ends: g.chain(e, q + "cur")
        ends = [q + "bc:else", q + "b:else", q + "bf:else"]; tail = [q + "s"]
    return fn("Apply Eye Colors", graph=g)


def f_set_eye_color():
    """One eye colour onto its parameter right now (live preview while the palette is open)."""
    g = G(); tail = ["entry"]; ends = []
    for key, var_name, par, _, _ in EYE_PARTS:
        q = "e" + key
        g.call(q + "is", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.part", "B": key}); g.branch(q + "b", "@%sis.ReturnValue" % q)
        g.get(q + "pl", "Player"); g.get(q + "m", var_name, cls=P_JODI); g.link(q + "pl.Player", q + "m.self")
        g.call(q + "v", K_SYS, "IsValid", inp={"Object": "@%sm.%s" % (q, var_name)}); g.branch(q + "bv", "@%sv.ReturnValue" % q)
        g.call(q + "s", E_MID, "SetVectorParameterValue", inp={"self": "@%sm.%s" % (q, var_name), "ParameterName": par, "Value": "@entry.color"})
        g.chain(*tail, q + "b", q + "bv", q + "s")
        for e in ends: g.chain(e, q + "b")
        ends = [q + "b:else", q + "bv:else"]; tail = [q + "s"]
    return fn("Set Eye Color", [param("part", "name"), param("color", S_LINCOLOR)], graph=g)


def f_open_eye_color():
    """Palette for one eye colour of one row. A row that is not on is put on first - otherwise one would drag a colour
    with nothing to see."""
    g = G()
    g.n("lto", "call_self", function="Look Type Of", inp={"name": "@entry.row"})
    g.n("sel", "call_self", function="Is Look Selected", inp={"type": "@lto.type", "style": "@entry.row"}); g.branch("bs", "@sel.yes")
    g.n("lc", "call_self", function="Look Clicked", inp={"name": "@entry.row"})
    g.set("sci", "ColorItem", inp={"ColorItem": "@entry.part"}); g.set("scr", "ColorRow", inp={"ColorRow": "@entry.row"})
    g.set("scm", "ColorMode", inp={"ColorMode": "Eye"})
    g.n("key", "call_self", function="Eye Color Key", inp={"part": "@entry.part", "row": "@entry.row"})
    g.get("gec", "EyeColors"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@gec.EyeColors", "Key": "@key.key"})
    g.call("col", K_MATH, "SelectColor", inp={"A": "@f.Value", "B": "(R=1,G=1,B=1,A=1)", "bPickA": "@f.ReturnValue"})
    tail = palette_show(g, "@col.ReturnValue")
    g.chain("entry", "lto", "sel", "bs", "sci", "scr", "scm", *tail); g.chain("bs:else", "lc", "sci")   # Is Look Selected is impure
    return fn("Open Eye Color", [param("part", "name"), param("row", "name")], graph=g)


def f_eye_reset_colors():
    """Drop the stored colours of one row (a lens: iris and sclera; lashes: their colour) and let the game put the
    EyeTable colour back on."""
    g = G(); ends = []
    g.n("lto", "call_self", function="Look Type Of", inp={"name": "@entry.row"})
    tail = ["entry", "lto"]   # impure and read by every branch below: it has to run first
    for key, _, _, _, cat in EYE_PARTS:
        q = "r" + key
        g.call(q + "is", K_MATH, "EqualEqual_NameName", inp={"A": "@lto.type", "B": cat}); g.branch(q + "b", "@%sis.ReturnValue" % q)
        g.n(q + "k", "call_self", function="Eye Color Key", inp={"part": key, "row": "@entry.row"})
        g.get(q + "ec", "EyeColors"); g.call(q + "rm", K_MAP, "Map_Remove", inp={"TargetMap": "@%sec.EyeColors" % q, "Key": "@%sk.key" % q})
        g.chain(*tail, q + "b", q + "rm")
        for e in ends: g.chain(e, q + "b")
        ends = [q + "b:else"]; tail = [q + "rm"]
    g.get("gpl", "Player"); g.call("ues", P_JODI, "Update Eyes Style", inp={"self": "@gpl.Player"})
    g.n("ae", "call_self", function="Apply Eye Colors"); g.n("sv", "call_self", function="Save Settings")
    g.chain(*tail, "ues", "ae", "sv")
    for e in ends: g.chain(e, "ues")
    return fn("Eye Reset Colors", [param("row", "name")], graph=g)


def f_open_hair_color():
    """Vanilla palette (flag 1) for the hair colour; preview/save via Apply Preview with ColorMode=Hair."""
    g = G()
    g.set("scm", "ColorMode", inp={"ColorMode": "Hair"})
    g.get("gpl", "Player"); g.call("gc", P_JODI, "Get Hairstyle Color", inp={"self": "@gpl.Player"})
    tail = palette_show(g, "@gc.color", flag="1")
    g.chain("entry", "scm", *tail)   # Get Hairstyle Color is pure
    return fn("Open Hair Color", graph=g)


def f_open_theme_color():
    """Vanilla palette (flag 2) for a theme base colour; Apply Preview (ColorMode=Theme) writes Set Theme Color + Apply Theme live."""
    g = G()
    g.set("sci", "ColorItem", inp={"ColorItem": "@entry.key"}); g.set("scm", "ColorMode", inp={"ColorMode": "Theme"})
    g.n("gc", "call_self", function="Theme Color", inp={"key": "@entry.key"})
    tail = palette_show(g, "@gc.color", flag="2")
    g.chain("entry", "sci", "scm", "gc", *tail)
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
    # the Options category list stays visible while the theme is edited; W_SlotTab has no Refresh Theme: rebuild it (8 rows)
    g.get("gpg", "Page"); g.call("iso", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Options"}); g.branch("bo", "@iso.ReturnValue"); g.n("roc", "call_self", function="Rebuild Option Cats")
    g.chain(*tail, "pat", "bo", "roc"); return fn("Apply Theme", graph=g)


def f_commit_color():
    """Keep what the palette chose, per mode (clothes: Save Slot Color; hair: GameInstance.Save Hair Color Data; eyes: into
    EyeColors; theme and make-up: the colour is already in place, only AltUI's settings file is missing)."""
    g = G()
    g.get("gcmt", "ColorMode"); g.call("ist", K_MATH, "EqualEqual_NameName", inp={"A": "@gcmt.ColorMode", "B": "Theme"}); g.branch("bt", "@ist.ReturnValue")
    g.n("svt", "call_self", function="Save Settings")
    g.get("gcm", "ColorMode"); g.call("ish", K_MATH, "EqualEqual_NameName", inp={"A": "@gcm.ColorMode", "B": "Hair"}); g.branch("bh", "@ish.ReturnValue")
    g.get("gcmm", "ColorMode"); g.call("ism", K_MATH, "EqualEqual_NameName", inp={"A": "@gcmm.ColorMode", "B": "Makeup"}); g.branch("bm", "@ism.ReturnValue")
    g.n("msv", "call_self", function="Save Settings")
    g.get("gcme", "ColorMode"); g.call("ise", K_MATH, "EqualEqual_NameName", inp={"A": "@gcme.ColorMode", "B": "Eye"}); g.branch("be", "@ise.ReturnValue")
    g.get("gcl4", "ColorItem"); g.get("gcr4", "ColorRow"); g.get("gcc5", "ColorCur"); g.get("gec2", "EyeColors")
    g.n("ekey", "call_self", function="Eye Color Key", inp={"part": "@gcl4.ColorItem", "row": "@gcr4.ColorRow"})
    g.call("eadd", K_MAP, "Map_Add", inp={"TargetMap": "@gec2.EyeColors", "Key": "@ekey.key", "Value": "@gcc5.ColorCur"})
    g.n("esv", "call_self", function="Save Settings")
    g.get("gcl", "ColorItem"); g.get("gcc", "ColorCur"); g.get("gcs", "ColorSlot")
    g.n("sv", "call_self", function="Save Slot Color", inp={"name": "@gcl.ColorItem", "slot": "@gcs.ColorSlot", "color": "@gcc.ColorCur"})
    g.call("gi", K_GS, "GetGameInstance"); g.cast("cgi", P_GI, "@gi.ReturnValue"); g.get("gplh", "Player")
    g.call("svh", P_GI, "Save Hair Color Data", inp={"self": "@cgi.AsTKA Game Instance", "player": "@gplh.Player"})
    g.chain("entry", "bt", "svt"); g.chain("bt:else", "bh", "svh"); g.chain("bh:else", "bm", "msv")
    g.get("gcmo", "ColorMode"); g.call("imo", K_MATH, "EqualEqual_NameName", inp={"A": "@gcmo.ColorMode", "B": "Mod"}); g.branch("bmo", "@imo.ReturnValue")   # the mod's colour: nothing here
    g.chain("bm:else", "be", "eadd", "esv"); g.chain("be:else", "bmo"); g.chain("bmo:else", "sv")
    return fn("Commit Color", graph=g)


def f_close_color():
    """Every way the palette closes ends here - its own close button (seen by Apply Preview), closing the panel, free cam,
    photo mode. The tick stops with ColorOpen, so what was chosen is kept here, not there."""
    g = G(); g.get("gco", "ColorOpen"); g.branch("bo", "@gco.ColorOpen"); g.n("cm", "call_self", function="Commit Color")
    g.set("s", "ColorOpen", inp={"ColorOpen": "false"})
    g.get("gp", "Palette"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gp.Palette"}); g.branch("b", "@iv.ReturnValue")
    g.get("gp2", "Palette"); g.call("cf", P_PAL, "Close Frame", inp={"self": "@gp2.Palette"})
    g.get("gp3", "Palette"); g.call("rm", E_WIDGET, "RemoveFromParent", inp={"self": "@gp3.Palette"})
    g.chain("entry", "bo", "cm", "s", "b", "cf", "rm"); g.chain("bo:else", "s"); return fn("Close Color", graph=g)


def f_apply_preview():
    """Tick while the palette is open: read the colour from Paletter.Image_Color, apply live; palette closed -> Close Color
    (which keeps the colour). Modes: Theme (panel colours), Hair, Eye, Makeup, otherwise Slot - one material slot of one worn
    piece (ColorItem + ColorSlot)."""
    g = G()
    g.get("gp", "Palette"); g.call("inv", E_USERWIDGET, "IsInViewport", inp={"self": "@gp.Palette"})
    g.get("gp1", "Palette"); g.call("vis", E_WIDGET, "IsVisible", inp={"self": "@gp1.Palette"})
    g.call("open", K_MATH, "BooleanAND", inp={"A": "@inv.ReturnValue", "B": "@vis.ReturnValue"}); g.branch("bo", "@open.ReturnValue")
    g.n("cc", "call_self", function="Close Color")
    # open, theme -> Set Theme Color + Apply Theme (widgets refresh on their Tick); hair -> Change Hairstyle Color
    g.get("gcmt2", "ColorMode"); g.call("ist2", K_MATH, "EqualEqual_NameName", inp={"A": "@gcmt2.ColorMode", "B": "Theme"}); g.branch("bt2", "@ist2.ReturnValue")
    g.get("gcl3", "ColorItem"); g.get("gcc4", "ColorCur"); g.n("stc", "call_self", function="Set Theme Color", inp={"key": "@gcl3.ColorItem", "color": "@gcc4.ColorCur"}); g.n("ath", "call_self", function="Apply Theme")
    g.get("gcm2", "ColorMode"); g.call("ish2", K_MATH, "EqualEqual_NameName", inp={"A": "@gcm2.ColorMode", "B": "Hair"}); g.branch("bh2", "@ish2.ReturnValue")
    g.get("gplh2", "Player"); g.get("gcc3", "ColorCur"); g.call("chh", P_JODI, "Change Hairstyle Color", inp={"self": "@gplh2.Player", "color": "@gcc3.ColorCur"})
    g.get("gcm3", "ColorMode"); g.call("ise2", K_MATH, "EqualEqual_NameName", inp={"A": "@gcm3.ColorMode", "B": "Eye"}); g.branch("be2", "@ise2.ReturnValue")
    g.get("gcle", "ColorItem"); g.get("gcce", "ColorCur"); g.n("sec", "call_self", function="Set Eye Color", inp={"part": "@gcle.ColorItem", "color": "@gcce.ColorCur"})
    g.get("gcm4", "ColorMode"); g.call("ism2", K_MATH, "EqualEqual_NameName", inp={"A": "@gcm4.ColorMode", "B": "Makeup"}); g.branch("bm2", "@ism2.ReturnValue")
    g.get("gclm", "ColorItem"); g.get("gccm", "ColorCur"); g.n("smc", "call_self", function="Set Makeup Color", inp={"row": "@gclm.ColorItem", "color": "@gccm.ColorCur"})
    # open -> read the colour
    g.get("gp2", "Palette"); g.get("pal", "Paletter", cls=P_PAL); g.link("gp2.Palette", "pal.self")
    g.get("img", "Image_Color", cls=P_PALR); g.link("pal.Paletter", "img.self")
    g.get("colr", "ColorAndOpacity", cls=E_IMAGE); g.link("img.Image_Color", "colr.self")
    g.get("gcc2", "ColorCur"); g.call("neq", K_MATH, "NotEqual_LinearColorLinearColor", inp={"A": "@colr.ColorAndOpacity", "B": "@gcc2.ColorCur"}); g.branch("bn", "@neq.ReturnValue")
    g.set("scc", "ColorCur", inp={"ColorCur": "@colr.ColorAndOpacity"})
    g.get("gcl2", "ColorItem"); g.get("gcs2", "ColorSlot")
    g.n("chg", "call_self", function="Set Slot Color", inp={"name": "@gcl2.ColorItem", "slot": "@gcs2.ColorSlot", "color": "@colr.ColorAndOpacity"})
    g.chain("entry", "bo", "bn", "scc", "bt2", "stc", "ath"); g.chain("bt2:else", "bh2", "chh"); g.chain("bh2:else", "be2", "sec")
    g.get("gcm5", "ColorMode"); g.call("imo2", K_MATH, "EqualEqual_NameName", inp={"A": "@gcm5.ColorMode", "B": "Mod"}); g.branch("bmo2", "@imo2.ReturnValue")
    g.get("gclo", "ColorItem"); g.n("mcc", "call_self", function="Mod Color Changed", inp={"key": "@gclo.ColorItem", "color": "@colr.ColorAndOpacity"})
    g.chain("be2:else", "bm2", "smc"); g.chain("bm2:else", "bmo2", "mcc"); g.chain("bmo2:else", "chg")
    g.chain("bo:else", "cc")
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


def photo_mode_wrapper(name, target, view):
    """Context menu "Update (photo from the front / as seen)": PhotoView for the one photo, then `target`(index)."""
    g = G(); g.set("spv", "PhotoView", inp={"PhotoView": "true" if view else "false"}); g.n("u", "call_self", function=target, inp={"index": "@entry.index"})
    g.chain("entry", "spv", "u"); return fn(name, [param("index", "int")], graph=g)


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
    for i, (action, key) in enumerate([("LookView", "Menu_ViewContent"), ("LookRename", "Menu_Rename"), ("LookUpdate", "Menu_UpdateFront"), ("LookUpdateView", "Menu_UpdateView"), ("LookDelete", "Menu_Delete"), ("Cancel", "Menu_Cancel")]):
        tail += menu_row(g, i, action, tt(g, "t%d" % i, key))
    g.get("gm6", "Menu"); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@gm6.Menu", "ZOrder": "110"})
    g.call("mp", "/Script/UMG.WidgetLayoutLibrary", "GetMousePositionOnViewport")
    g.get("gm7", "Menu"); g.call("spv", E_USERWIDGET, "SetPositionInViewport", inp={"self": "@gm7.Menu", "Position": "@mp.ReturnValue", "bRemoveDPIScale": "false"})
    g.chain("entry", "bn", "oc"); g.chain("bn:else", "scl", "b", "clr"); g.chain("b:else", "cm_cr", "sm", "smm", "clr"); g.chain(*tail, "atv", "mp", "spv")
    return fn("On Look Context", [param("index", "int")], graph=g)


# ---------------- Content view (View content / Show in tab) ----------------
def f_content_open():
    """yes = the tab `page` has a content view open (ViewOutfit / ViewLook / ViewPreset / ViewFace >= 0)."""
    g = G()
    g.call("isO", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.page", "B": "Outfits"}); g.call("isL", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.page", "B": "Looks"})
    g.call("isA", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.page", "B": "Look"})
    g.get("gvo", "ViewOutfit"); g.get("gvl", "ViewLook"); g.get("gvp", "ViewPreset")
    g.call("v1", K_MATH, "SelectInt", inp={"A": "@gvp.ViewPreset", "B": "-1", "bPickA": "@isA.ReturnValue"}); g.call("v2", K_MATH, "SelectInt", inp={"A": "@gvl.ViewLook", "B": "@v1.ReturnValue", "bPickA": "@isL.ReturnValue"})
    g.call("isF", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.page", "B": "Face"}); g.get("gvf", "ViewFace")
    g.call("v3", K_MATH, "SelectInt", inp={"A": "@gvo.ViewOutfit", "B": "@v2.ReturnValue", "bPickA": "@isO.ReturnValue"})
    g.call("v4", K_MATH, "SelectInt", inp={"A": "@gvf.ViewFace", "B": "@v3.ReturnValue", "bPickA": "@isF.ReturnValue"}); g.call("ge", K_MATH, "GreaterEqual_IntInt", inp={"A": "@v4.ReturnValue", "B": "0"})
    g.get("gvm", "ViewMod"); g.call("vm", K_MATH, "NotEqual_NameName", inp={"A": "@gvm.ViewMod", "B": "None"}); g.call("yes", K_MATH, "BooleanOR", inp={"A": "@ge.ReturnValue", "B": "@vm.ReturnValue"})
    g.link("yes.ReturnValue", "return.yes"); g.chain("entry", "return")
    return fn("Content Open", [param("page", "name")], [param("yes", "bool")], graph=g)


def f_open_content():
    """Open the content view of outfit / look / preset / saved face `index` (kind = Outfit / Look / Preset / Face) on the current page."""
    g = G()
    g.call("isO", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "Outfit"}); g.branch("bO", "@isO.ReturnValue"); g.set("so", "ViewOutfit", inp={"ViewOutfit": "@entry.index"})
    g.call("isL", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "Look"}); g.branch("bL", "@isL.ReturnValue"); g.set("sl", "ViewLook", inp={"ViewLook": "@entry.index"})
    g.call("isP", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "Preset"}); g.branch("bP", "@isP.ReturnValue"); g.set("sp", "ViewPreset", inp={"ViewPreset": "@entry.index"})
    g.call("isF", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "Face"}); g.branch("bF", "@isF.ReturnValue"); g.set("sf", "ViewFace", inp={"ViewFace": "@entry.index"})
    g.get("gpg", "Page"); g.n("spg", "call_self", function="Select Page", inp={"name": "@gpg.Page"})
    g.chain("entry", "bO", "so", "spg"); g.chain("bO:else", "bL", "sl", "spg"); g.chain("bL:else", "bP", "sp", "spg"); g.chain("bP:else", "bF", "sf", "spg")
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
    g.call("isF", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Face"}); g.branch("bF", "@isF.ReturnValue"); g.set("sf", "ViewFace", inp={"ViewFace": "-1"})
    g.get("gpg2", "Page"); g.n("spg", "call_self", function="Select Page", inp={"name": "@gpg2.Page"})
    g.chain("entry", "bM", "svm", "spf"); g.chain("bM:else", "bO", "so", "spg"); g.chain("bO:else", "bL", "sl", "spg"); g.chain("bL:else", "bA", "sp", "spg"); g.chain("bA:else", "bF", "sf", "spg"); g.chain("bF:else", "spg")
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
    g.get("gpcv", "PresetColors"); g.call("fpcv", K_MAP, "Map_Find", inp={"TargetMap": "@gpcv.PresetColors", "Key": "@pbr.IconNumber"}); g.brk("bpcv", S_PRESETCOL, "@fpcv.Value")
    g.make("pmk", S_SNAP, EyeColors="@bpcv.EyeColors", MakeupColors="@bpcv.MakeupColors", Makeup="@pbr.MakeupData", Skin="@pbr.SkinName", Hair="@pbr.HairstyleName", HairColor="@pbr.HairColor", Boobs="@pbr.BoobsSize", Waist="@pbr.Waist", Hip="@pbr.Hip")
    g.set("psn", "ViewSnap", inp={"ViewSnap": "@pmk.S_Snapshot"})
    g.n("pt", "call_self", function="Preset Shown Name", inp={"index": "@entry.index"})   # its own name, else "Preset <n>"
    g.set("pst", "ViewTitle", inp={"ViewTitle": "@pt.s"}); g.set("pok", "TmpBool", inp={"TmpBool": "true"})
    # --- look
    g.call("isL", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "Look"}); g.branch("bL", "@isL.ReturnValue")
    head, tails = ensure_looks(g)
    arr = looks_array(g, "la"); g.call("ll", K_ARR, "Array_Length", inp={"TargetArray": arr}); g.call("lin", K_MATH, "Less_IntInt", inp={"A": "@entry.index", "B": "@ll.ReturnValue"})
    g.call("ge2", K_MATH, "GreaterEqual_IntInt", inp={"A": "@entry.index", "B": "0"}); g.call("lin2", K_MATH, "BooleanAND", inp={"A": "@lin.ReturnValue", "B": "@ge2.ReturnValue"}); g.branch("bLi", "@lin2.ReturnValue")
    g.call("lget", K_ARR, "Array_Get", inp={"TargetArray": arr, "Index": "@entry.index"}); g.brk("lbr", S_LOOK, "@lget.Item")
    g.set("lsn", "ViewSnap", inp={"ViewSnap": "@lbr.Snap"}); g.set("lst", "ViewTitle", inp={"ViewTitle": "@lbr.Name"}); g.set("lok", "TmpBool", inp={"TmpBool": "true"})
    # --- saved face: only its values and how they mix; the view then shows the face section alone
    g.call("isF", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "Face"}); g.branch("bF", "@isF.ReturnValue")
    fhead, ftails = ensure_faces(g)
    farr = faces_array(g, "fa"); g.call("fl", K_ARR, "Array_Length", inp={"TargetArray": farr}); g.call("fin", K_MATH, "Less_IntInt", inp={"A": "@entry.index", "B": "@fl.ReturnValue"})
    g.call("ge3", K_MATH, "GreaterEqual_IntInt", inp={"A": "@entry.index", "B": "0"}); g.call("fin2", K_MATH, "BooleanAND", inp={"A": "@fin.ReturnValue", "B": "@ge3.ReturnValue"}); g.branch("bFi", "@fin2.ReturnValue")
    g.call("fget", K_ARR, "Array_Get", inp={"TargetArray": farr, "Index": "@entry.index"}); g.brk("fbr", fc.S_FACE, "@fget.Item")
    g.make("fmk", S_SNAP, Face="@fbr.Values", FaceAdd="@fbr.FaceAdd"); g.set("fsn", "ViewSnap", inp={"ViewSnap": "@fmk.S_Snapshot"})
    g.set("fst", "ViewTitle", inp={"ViewTitle": "@fbr.Name"}); g.set("fok", "TmpBool", inp={"TmpBool": "true"})
    g.get("gok", "TmpBool"); g.link("gok.TmpBool", "return.ok")
    g.chain("entry", "ok0", "bO", "bOi", "okeys", "sokeys", "cclr", "fo"); g.chain("fo", "oadd"); g.chain("fo:Completed", "osn", "oname", "ost", "ook", "return"); g.chain("bOi:else", "return")
    g.chain("bO:else", "bP", "bPi", "psn", "pst", "pok", "return"); g.chain("bPi:else", "return")
    g.chain("bP:else", "bL", *head)
    for t in tails: g.chain(t, "bLi")
    g.chain("bLi", "lsn", "lst", "lok", "return"); g.chain("bLi:else", "return"); g.chain("bL:else", "bF", *fhead)
    for t in ftails: g.chain(t, "bFi")
    g.chain("bFi", "fsn", "fst", "fok", "return"); g.chain("bFi:else", "return"); g.chain("bF:else", "return")
    return fn("Content Snapshot", [param("kind", "name"), param("index", "int")], [param("ok", "bool")], graph=g)


def content_section(g, id, caption_pin):
    """New W_ContentSection (caption) -> TmpSection, added to the panel's content list; returns the exec chain."""
    sw = create_widget(g, id, W_SECTION); set_manager(g, id + "_sm", W_SECTION, sw)
    g.call(id + "_i", W_SECTION, "Init", inp={"self": sw, "caption": caption_pin}); g.set(id + "_ss", "TmpSection", inp={"TmpSection": sw})
    g.get(id + "_gp", "Panel"); g.get(id + "_gs", "TmpSection")
    g.call(id + "_a", W_PANEL, "Add Content Section", inp={"self": "@%s_gp.Panel" % id, "widget": "@%s_gs.TmpSection" % id})
    return [id + "_cr", id + "_sm", id + "_i", id + "_ss", id + "_a"]


def value_row(g, id, label_pin, value_pin="", header=False):
    """W_ValueRow (label | value, or a header line) into the current section's table (TmpSection); returns the exec chain."""
    rw = create_widget(g, id, W_VALROW); set_manager(g, id + "_sm", W_VALROW, rw)
    g.call(id + "_i", W_VALROW, "Init", inp={"self": rw, "label": label_pin, "value": value_pin, "header": "true" if header else "false"})
    g.get(id + "_gs", "TmpSection"); g.call(id + "_a", W_SECTION, "Add Row", inp={"self": "@%s_gs.TmpSection" % id, "row": rw})
    return [id + "_cr", id + "_sm", id + "_i", id + "_a"]


def pct_text(g, id, pin, signed=False):
    """float 0..1 -> text "37 %" (signed: "+37 %" / "-37 %")."""
    g.call(id + "_m", K_MATH, "Multiply_FloatFloat", inp={"A": pin, "B": "100.0"}); g.call(id + "_r", K_MATH, "Round", inp={"A": "@%s_m.ReturnValue" % id})
    g.call(id + "_s", K_STR, "Conv_IntToString", inp={"InInt": "@%s_r.ReturnValue" % id}); s = "@%s_s.ReturnValue" % id
    if signed:
        g.call(id + "_p", K_MATH, "Greater_IntInt", inp={"A": "@%s_r.ReturnValue" % id, "B": "0"})
        g.call(id + "_ps", K_STR, "Concat_StrStr", inp={"A": "+", "B": s}); g.call(id + "_sel", K_MATH, "SelectString", inp={"A": "@%s_ps.ReturnValue" % id, "B": s, "bPickA": "@%s_p.ReturnValue" % id})
        s = "@%s_sel.ReturnValue" % id
    g.call(id + "_c", K_STR, "Concat_StrStr", inp={"A": s, "B": " %"}); g.call(id, K_TXT, "Conv_StringToText", inp={"InString": "@%s_c.ReturnValue" % id}); return "@%s.ReturnValue" % id


def content_tile(g, id, item_pin, worn_pin, owned_pin, fav_pin, damaged_pin, tip_pin, kind=None):
    """W_ClothesButton in the current section (TmpSection); returns (exec chain, widget pin). With kind (hair / skin / makeup / body) tip_pin is the
    category text and the tooltip comes from Item Tip; else tip_pin is the tooltip (clothes: the caller's Item Tip)."""
    pre = []
    if kind: n, tip_pin = tile_tip(g, id, item_pin, kind, tip_pin); pre = [n]
    tw = create_widget(g, id, W_BTN); set_manager(g, id + "_sm", W_BTN, tw)
    g.call(id + "_i", W_BTN, "Init", inp={"self": tw, "item": item_pin, "worn": worn_pin, "owned": owned_pin, "fav": fav_pin, "damaged": damaged_pin, "tip": tip_pin, "dim": "false"})
    g.get(id + "_gs", "TmpSection"); g.call(id + "_a", W_SECTION, "Add Tile", inp={"self": "@%s_gs.TmpSection" % id, "widget": tw})
    return pre + [id + "_cr", id + "_sm", id + "_i", id + "_a"], tw


def f_rebuild_content():
    """Content view of the open outfit / look / preset (Page decides the kind): back link + title, then one section per non-empty part of the
    snapshot - clothes (+ stored colour), hairstyle (+ colour), skin, one per makeup type, body (mod tile + slider line). An index that became
    invalid (deleted in the mirror meanwhile) closes the view."""
    g = G()
    g.get("gpg", "Page"); g.call("isO", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Outfits"})
    g.get("gpg2", "Page"); g.call("isL", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg2.Page", "B": "Looks"})
    g.get("gpg3", "Page"); g.call("isF", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg3.Page", "B": "Face"})
    g.call("k0", K_MATH, "SelectString", inp={"A": "Face", "B": "Preset", "bPickA": "@isF.ReturnValue"})
    g.call("k1", K_MATH, "SelectString", inp={"A": "Look", "B": "@k0.ReturnValue", "bPickA": "@isL.ReturnValue"}); g.call("k2s", K_MATH, "SelectString", inp={"A": "Outfit", "B": "@k1.ReturnValue", "bPickA": "@isO.ReturnValue"})
    g.call("k2", K_STR, "Conv_StringToName", inp={"InString": "@k2s.ReturnValue"})   # no SelectName in 4.27
    g.get("gvo", "ViewOutfit"); g.get("gvl", "ViewLook"); g.get("gvp", "ViewPreset")
    g.get("gvf", "ViewFace"); g.call("i0", K_MATH, "SelectInt", inp={"A": "@gvf.ViewFace", "B": "@gvp.ViewPreset", "bPickA": "@isF.ReturnValue"})
    g.call("i1", K_MATH, "SelectInt", inp={"A": "@gvl.ViewLook", "B": "@i0.ReturnValue", "bPickA": "@isL.ReturnValue"}); g.call("i2", K_MATH, "SelectInt", inp={"A": "@gvo.ViewOutfit", "B": "@i1.ReturnValue", "bPickA": "@isO.ReturnValue"})
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
    # AltUI's own colour of this entry as the tile's swatch: make-up by row, the lens / lashes by <part>#<row>
    g.call("mcf", K_MAP, "Map_Find", inp={"TargetMap": "@bv.MakeupColors", "Key": "@fs.Array Element"})
    g.call("ity", K_MATH, "EqualEqual_NameName", inp={"A": "@fm.Array Element", "B": "Eye"}); g.call("ily", K_MATH, "EqualEqual_NameName", inp={"A": "@fm.Array Element", "B": "Eyelashes"})
    g.call("iey", K_MATH, "BooleanOR", inp={"A": "@ity.ReturnValue", "B": "@ily.ReturnValue"})
    g.call("epf", K_MATH, "SelectString", inp={"A": "Lashes#", "B": "Iris#", "bPickA": "@ily.ReturnValue"}); g.call("ers", K_STR, "Conv_NameToString", inp={"InName": "@fs.Array Element"})
    g.call("eks", K_STR, "Concat_StrStr", inp={"A": "@epf.ReturnValue", "B": "@ers.ReturnValue"}); g.call("ekn", K_STR, "Conv_StringToName", inp={"InString": "@eks.ReturnValue"})
    g.call("ecf", K_MAP, "Map_Find", inp={"TargetMap": "@bv.EyeColors", "Key": "@ekn.ReturnValue"})
    g.call("eok", K_MATH, "BooleanAND", inp={"A": "@iey.ReturnValue", "B": "@ecf.ReturnValue"}); g.call("cok", K_MATH, "BooleanOR", inp={"A": "@mcf.ReturnValue", "B": "@eok.ReturnValue"}); g.branch("bmc", "@cok.ReturnValue")
    g.call("ccol", K_MATH, "SelectColor", inp={"A": "@mcf.Value", "B": "@ecf.Value", "bPickA": "@mcf.ReturnValue"})
    g.call("scs4", W_BTN, "Set Color Swatch", inp={"self": w4, "color": "@ccol.ReturnValue"})
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
    # body values as a table: breast / waist, then the bone-scale factors when the snapshot carries all of them
    g.branch("bsl", "@bo2.ReturnValue")
    body_rows = value_row(g, "vb0", tt(g, "vb0t", "Lbl_Breast"), pct_text(g, "vb0p", "@bv.Boobs")) + value_row(g, "vb1", tt(g, "vb1t", "Lbl_Waist"), pct_text(g, "vb1p", "@bv.Waist"))
    g.call("bscl", K_ARR, "Array_Length", inp={"TargetArray": "@bv.Scales"}); g.call("bsc6", K_MATH, "EqualEqual_IntInt", inp={"A": "@bscl.ReturnValue", "B": str(bg.N_SLIDERS)}); g.branch("bsc", "@bsc6.ReturnValue")
    scale_rows = []
    for i, (key, _) in enumerate(bg.SLIDERS):
        g.call("sf%d_g" % i, K_ARR, "Array_Get", inp={"TargetArray": "@bv.Scales", "Index": str(i)})
        g.call("sf%d_t" % i, K_TXT, "Conv_FloatToText", inp={"Value": "@sf%d_g.Item" % i, "MinimumFractionalDigits": "2", "MaximumFractionalDigits": "2"})
        g.call("sf%d_s" % i, K_TXT, "Conv_TextToString", inp={"InText": "@sf%d_t.ReturnValue" % i}); g.call("sf%d_x" % i, K_STR, "Concat_StrStr", inp={"A": "\u00d7", "B": "@sf%d_s.ReturnValue" % i})
        g.call("sf%d" % i, K_TXT, "Conv_StringToText", inp={"InString": "@sf%d_x.ReturnValue" % i})
        scale_rows += value_row(g, "vs%d" % i, tt(g, "vs%dt" % i, "Lbl_Sc" + key), "@sf%d.ReturnValue" % i)
    # --- face: only the entries the look fixes (an empty map = the game's own face, no section); per group a header line,
    # the expressions with how they mix (blended / added up)
    g.call("fln", K_MAP, "Map_Length", inp={"TargetMap": "@bv.Face"}); g.call("fgt", K_MATH, "Greater_IntInt", inp={"A": "@fln.ReturnValue", "B": "0"}); g.branch("bfc", "@fgt.ReturnValue")
    sec6 = content_section(g, "s6", tt(g, "s6t", "Tab_Face"))
    face_steps = []   # (branch id or None, [exec chain]) in order; a branch skips its chain when false
    for gi, grp in enumerate(fc.GROUPS):
        entries = [e for e in fc.ENTRIES if e[1] == grp]; found = []
        for ei, (key, _, neg, pos) in enumerate(entries):
            q = "fe%d_%d" % (gi, ei)
            g.call(q + "fp", K_MAP, "Map_Find", inp={"TargetMap": "@bv.Face", "Key": g.lit_name(q + "kp", pos)})
            if neg:
                g.call(q + "fn", K_MAP, "Map_Find", inp={"TargetMap": "@bv.Face", "Key": g.lit_name(q + "kn", neg)})
                g.call(q + "fx", K_MATH, "BooleanOR", inp={"A": "@%sfp.ReturnValue" % q, "B": "@%sfn.ReturnValue" % q}); fx = "@%sfx.ReturnValue" % q
                g.call(q + "vl", K_MATH, "Subtract_FloatFloat", inp={"A": "@%sfp.Value" % q, "B": "@%sfn.Value" % q}); val = pct_text(g, q + "pt", "@%svl.ReturnValue" % q, signed=True)
            else:
                fx = "@%sfp.ReturnValue" % q; val = pct_text(g, q + "pt", "@%sfp.Value" % q)
            found.append(fx); g.branch(q + "b", fx)
            face_steps.append((q + "b", value_row(g, q + "r", tt(g, q + "t", "Face_" + key), val)))
        # any entry of the group fixed -> header line first
        acc = found[0]
        for k, f in enumerate(found[1:]):
            g.call("fa%d_%d" % (gi, k), K_MATH, "BooleanOR", inp={"A": acc, "B": f}); acc = "@fa%d_%d.ReturnValue" % (gi, k)
        g.branch("fg%d" % gi, acc)
        face_steps.insert(len(face_steps) - len(entries), ("fg%d" % gi, value_row(g, "fh%d" % gi, tt(g, "fh%dt" % gi, "Cat_" + grp), header=True)))
        if grp == fc.GROUPS[0]:
            g.branch("fm%d" % gi, acc)
            g.call("fmv", K_MATH, "SelectString", inp={"A": ts(g, "fma", "Lbl_FaceAddedShort"), "B": ts(g, "fmb", "Lbl_FaceBlendedShort"), "bPickA": "@bv.FaceAdd"})
            g.call("fmt", K_TXT, "Conv_StringToText", inp={"InString": "@fmv.ReturnValue"})
            face_steps.append(("fm%d" % gi, value_row(g, "fmr", tt(g, "fmrt", "Lbl_FaceMix"), "@fmt.ReturnValue")))
    # exec chains
    g.get("gvm", "ViewMod"); g.call("vm", K_MATH, "NotEqual_NameName", inp={"A": "@gvm.ViewMod", "B": "None"}); g.branch("bvm", "@vm.ReturnValue"); g.n("rmc", "call_self", function="Rebuild Mod Content")
    g.chain("entry", "bvm", "rmc"); g.chain("bvm:else", "cs", "bok", "clc", "cll", "clk_cr", "sml", "li", "al", "sct", "bw"); g.chain("bok:else", "cc")
    g.chain("bw", *sec1, "fw"); g.chain("fw", "fi", "bfi", "sti", "idm", "tip", *t1, "bcf", "scs"); g.chain("bfi:else", "stp", "idm"); g.chain("fw:Completed", "bh"); g.chain("bw:else", "bh")
    g.chain("bh", *sec2, "hrow", "shi", *t2, "shc", "bsk"); g.chain("hrow:Row Not Found", "shp", t2[0]); g.chain("bh:else", "bsk")
    g.chain("bsk", *sec3, "srow", "ssi", "ssel", *t3, "mk"); g.chain("srow:Row Not Found", "ssp", "ssel"); g.chain("bsk:else", "mk")
    g.chain("mk", "fm"); g.chain("fm", "bml", "mcap", *sec4, "trow", "sey", "smln"); g.chain("trow:Row Not Found", "sey0", "smln"); g.chain("smln", "fs")
    g.chain("fs", "bey", "erow", "sei", "msel"); g.chain("erow:Row Not Found", "spi", "msel"); g.chain("bey:else", "mrow", "smi", "msel"); g.chain("mrow:Row Not Found", "spi"); g.chain("msel", *t4, "bmc"); g.chain("bmc", "scs4")
    g.chain("fm:Completed", "bb"); g.chain("bb", *sec5, "bbn", "scan", *t5, "bsl"); g.chain("bbn:else", "bsl"); g.chain("bb:else", "bfc")
    g.chain("bsl", *body_rows, "bsc"); g.chain("bsl:else", "bfc"); g.chain("bsc", *scale_rows, "bfc"); g.chain("bsc:else", "bfc")
    # face steps: each branch runs its rows or skips them; both ways go on to the next step
    g.chain("bfc", *sec6); prev = [sec6[-1]]
    for br, rows in face_steps:
        for p in prev: g.chain(p, br)
        g.chain(br, *rows); prev = [rows[-1], br + ":else"]
    return fn("Rebuild Content", graph=g)


def f_on_content_item_context():
    """Right click on a tile of the content view: Wear / Take off / Apply (Content Use), Rename, "Show in tab" (only if the tile knows its origin slot), "Rename mod…" (mod piece) + Cancel."""
    g = G()
    g.get("glb", "LastButton"); g.cast("cb", W_BTN, "@glb.LastButton"); g.get("gsl", "ItemSlot", cls=W_BTN); g.link("cb.AsW_ClothesButton", "gsl.self")
    g.set("scs", "ContextSlot", inp={"ContextSlot": "@gsl.ItemSlot"})
    g.get("gm", "Menu"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gm.Menu"}); g.branch("b", "@iv.ReturnValue")
    mw = create_widget(g, "cm", W_MENU); g.set("sm", "Menu", inp={"Menu": mw}); set_manager(g, "smm", W_MENU, mw)
    g.get("gm2", "Menu"); g.call("clr", W_MENU, "Clear Rows", inp={"self": "@gm2.Menu"})
    g.get("gcs", "ContextSlot"); g.call("has", K_MATH, "NotEqual_NameName", inp={"A": "@gcs.ContextSlot", "B": "None"}); g.branch("bh", "@has.ReturnValue")
    r0 = menu_row(g, 0, "GoTo", tt(g, "t0", "Menu_ShowIn")); r1 = menu_row(g, 1, "Cancel", tt(g, "t1", "Menu_Cancel")); r2 = menu_row(g, 2, "Rename", tt(g, "t2", "Menu_Rename"))
    # first row: use the tile - clothes "Wear" / "Take off", the rest "Apply"; none for a piece that is gone
    g.get("gcs1", "ContextSlot"); g.n("ck", "call_self", function="Content Kind", inp={"slot": "@gcs1.ContextSlot"})
    g.call("kn", K_MATH, "NotEqual_NameName", inp={"A": "@ck.kind", "B": "None"}); g.branch("bk", "@kn.ReturnValue")
    g.call("kc", K_MATH, "EqualEqual_NameName", inp={"A": "@ck.kind", "B": "Clothes"}); g.n("iw", "call_self", function="Is Worn", inp={"name": "@entry.name"})
    g.call("wo", K_MATH, "SelectString", inp={"A": ts(g, "wto", "Menu_TakeOff"), "B": ts(g, "wwe", "Menu_Wear"), "bPickA": "@iw.yes"})
    g.call("us", K_MATH, "SelectString", inp={"A": "@wo.ReturnValue", "B": ts(g, "wap", "Menu_Apply"), "bPickA": "@kc.ReturnValue"}); g.call("ut", K_TXT, "Conv_StringToText", inp={"InString": "@us.ReturnValue"})
    r4 = menu_row(g, 4, "ContentUse", "@ut.ReturnValue")
    g.n("imd", "call_self", function="Item Mod", inp={"row": "@entry.name"}); g.branch("bmd", "@imd.found")   # mod piece (any kind): rename the mod
    r3 = menu_row(g, 3, "RenameMod", tt(g, "t3", "Menu_RenameMod"))
    g.get("gm6", "Menu"); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@gm6.Menu", "ZOrder": "110"})
    g.call("mp", "/Script/UMG.WidgetLayoutLibrary", "GetMousePositionOnViewport")
    g.get("gm7", "Menu"); g.call("spv", E_USERWIDGET, "SetPositionInViewport", inp={"self": "@gm7.Menu", "Position": "@mp.ReturnValue", "bRemoveDPIScale": "false"})
    g.chain("entry", "scs", "b", "clr"); g.chain("b:else", "cm_cr", "sm", "smm", "clr")
    g.chain("clr", "ck", "bk", *r4, r2[0]); g.chain("bk:else", r2[0]); g.chain(*r2, "bh", *r0, "bmd"); g.chain("bh:else", "bmd"); g.chain("bmd", *r3, r1[0]); g.chain("bmd:else", r1[0]); g.chain(*r1, "atv", "mp", "spv")
    return fn("On Content Item Context", [param("name", "name")], graph=g)

def f_content_kind():
    """What a tile of a content view is, from its origin slot (ContextSlot of the tile): Hair, Body, Look (skin or a make-up
    type), Pose (no slot, mod content only), None (no slot elsewhere: a piece of an outfit that is gone), else Clothes."""
    g = G()
    g.set("sc", "ClickKind", inp={"ClickKind": "Clothes"})
    g.call("isH", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.slot", "B": "Hair"}); g.branch("bH", "@isH.ReturnValue"); g.set("sH", "ClickKind", inp={"ClickKind": "Hair"})
    g.call("isB", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.slot", "B": "Body"}); g.branch("bB", "@isB.ReturnValue"); g.set("sB", "ClickKind", inp={"ClickKind": "Body"})
    g.call("isS", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.slot", "B": "Skin"}); g.branch("bS", "@isS.ReturnValue"); g.set("sS", "ClickKind", inp={"ClickKind": "Look"})
    g.call("isN", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.slot", "B": "None"}); g.branch("bN", "@isN.ReturnValue")
    g.get("gvm", "ViewMod"); g.call("vm", K_MATH, "NotEqual_NameName", inp={"A": "@gvm.ViewMod", "B": "None"})
    g.call("pk", K_MATH, "SelectString", inp={"A": "Pose", "B": "None", "bPickA": "@vm.ReturnValue"}); g.call("pkn", K_STR, "Conv_StringToName", inp={"InString": "@pk.ReturnValue"})
    g.set("sN", "ClickKind", inp={"ClickKind": "@pkn.ReturnValue"})
    g.call("mt", K_DT, "DoesDataTableRowExist", inp={"Table": P_MTYPE_T, "RowName": "@entry.slot"}); g.branch("bM", "@mt.ReturnValue"); g.set("sM", "ClickKind", inp={"ClickKind": "Look"})
    g.get("gk", "ClickKind"); g.link("gk.ClickKind", "return.kind")
    g.chain("entry", "sc", "bH", "sH", "return"); g.chain("bH:else", "bB", "sB", "return"); g.chain("bB:else", "bS", "sS", "return")
    g.chain("bS:else", "bN", "sN", "return"); g.chain("bN:else", "mt", "bM", "sM", "return"); g.chain("bM:else", "return")
    return fn("Content Kind", [param("slot", "name")], [param("kind", "name")], graph=g)


def f_content_item_clicked():
    """Left click on a tile of a content view: its origin slot comes from the tile (LastButton), then Content Use."""
    g = G()
    g.get("glb", "LastButton"); g.cast("cb", W_BTN, "@glb.LastButton"); g.get("gsl", "ItemSlot", cls=W_BTN); g.link("cb.AsW_ClothesButton", "gsl.self")
    g.set("scs", "ContextSlot", inp={"ContextSlot": "@gsl.ItemSlot"})
    g.n("cu", "call_self", function="Content Use", inp={"name": "@entry.name"})
    g.chain("entry", "scs", "cu"); return fn("Content Item Clicked", [param("name", "name")], graph=g)


def f_content_use():
    """A tile of a content view does what it does on its own page (ContextSlot = its origin): clothes are put on or taken off,
    a hairstyle / skin / make-up row / body / pose is applied the same way as a click there; then the view is redrawn.
    Make-up and skin go through Look Clicked with LookCat set to the tile's type for the call - the category of the Look page
    must not decide it (under Presets it would apply a preset)."""
    g = G()
    g.get("gcs", "ContextSlot"); g.n("ck", "call_self", function="Content Kind", inp={"slot": "@gcs.ContextSlot"})
    g.n("rct", "call_self", function="Rebuild Content")
    # clothes: like a click on the clothes page
    g.call("isC", K_MATH, "EqualEqual_NameName", inp={"A": "@ck.kind", "B": "Clothes"}); g.branch("bC", "@isC.ReturnValue")
    g.n("io", "call_self", function="Can Wear", inp={"name": "@entry.name"}); g.branch("bo", "@io.yes")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"})
    g.call("msg", K_STR, "Concat_StrStr", inp={"A": ts(g, "mk", "Msg_NotOwned"), "B": "@n2s.ReturnValue"})
    pop(g, "pop", text_from_str(g, "t", "@msg.ReturnValue"))
    g.n("ph", "call_self", function="Push History")
    g.n("iw", "call_self", function="Is Worn", inp={"name": "@entry.name"}); g.branch("bw", "@iw.yes")
    g.n("to", "call_self", function="Take Off", inp={"name": "@entry.name"}); g.n("we", "call_self", function="Wear", inp={"name": "@entry.name"})
    g.n("rl", "call_self", function="Rebuild Left")
    # hairstyle
    g.call("isH", K_MATH, "EqualEqual_NameName", inp={"A": "@ck.kind", "B": "Hair"}); g.branch("bH", "@isH.ReturnValue")
    g.n("hc", "call_self", function="Hair Clicked", inp={"name": "@entry.name"})
    # skin / make-up
    g.call("isL", K_MATH, "EqualEqual_NameName", inp={"A": "@ck.kind", "B": "Look"}); g.branch("bL", "@isL.ReturnValue")
    g.get("glc", "LookCat"); g.set("slk", "LookCatKeep", inp={"LookCatKeep": "@glc.LookCat"})
    g.get("gcs2", "ContextSlot"); g.set("slc", "LookCat", inp={"LookCat": "@gcs2.ContextSlot"})
    g.n("lc", "call_self", function="Look Clicked", inp={"name": "@entry.name"})
    g.get("glk", "LookCatKeep"); g.set("rlc", "LookCat", inp={"LookCat": "@glk.LookCatKeep"})
    # body
    g.call("isB", K_MATH, "EqualEqual_NameName", inp={"A": "@ck.kind", "B": "Body"}); g.branch("bB", "@isB.ReturnValue")
    g.n("sb", "call_self", function="Select Body", inp={"name": "@entry.name"})
    # pose
    g.call("isP", K_MATH, "EqualEqual_NameName", inp={"A": "@ck.kind", "B": "Pose"}); g.branch("bP", "@isP.ReturnValue")
    g.n("pc", "call_self", function="Pose Clicked", inp={"name": "@entry.name"})
    g.chain("entry", "ck", "bC", "io", "bo", "ph", "bw", "to", "rl", "rct"); g.chain("bw:else", "we", "rl"); g.chain("bo:else", "pop")
    g.chain("bC:else", "bH", "hc", "rct"); g.chain("bH:else", "bL", "slk", "slc", "lc", "rlc", "rct")
    g.chain("bL:else", "bB", "sb", "rct"); g.chain("bB:else", "bP", "pc", "rct")
    return fn("Content Use", [param("name", "name")], graph=g)


def f_go_to_item():
    """"Show in tab": jump from the content view to the piece's own page - ContextSlot = origin (Hair / Skin / <makeup type> / Body / clothes slot).
    Clothes: search cleared, a filter toggle that would hide the piece is switched off (like a click), slot + group chip (Hidden for hidden pieces,
    the piece's group when the slot has more than one, else All); the tile is highlighted and scrolled into view."""
    g = G(); g.get("gcs", "ContextSlot")
    # the jump target must be visible: close every content view (mod / outfit / look / preset) before switching the page
    g.set("cvm", "ViewMod", inp={"ViewMod": "None"}); g.set("cvo", "ViewOutfit", inp={"ViewOutfit": "-1"}); g.set("cvl", "ViewLook", inp={"ViewLook": "-1"}); g.set("cvp", "ViewPreset", inp={"ViewPreset": "-1"}); g.set("cvf", "ViewFace", inp={"ViewFace": "-1"})
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
    g.chain("entry", "cvm", "cvo", "cvl", "cvp", "cvf", "bH", "hh", "hk", "hsp", "hsc"); g.chain("bH:else", "bB", "bsp"); g.chain("bB:else", "bS", "lc"); g.chain("bS:else", "trow", "lc"); g.chain("lc", "lh", "lk", "lih", "lg", "lif", "slof", "plof", "lcs", "pls", "lsp", "lsc")
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
    g.get("gpg3", "Page"); g.call("ish0", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg3.Page", "B": "Hair"}); g.call("isfc", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg3.Page", "B": "Face"})
    g.call("ish", K_MATH, "BooleanOR", inp={"A": "@ish0.ReturnValue", "B": "@isfc.ReturnValue"}); g.branch("bh", "@ish.ReturnValue"); g.set("sh", "TmpI", inp={"TmpI": "983"})   # face page: the same close-up
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
    # every focus (start or another slot): the camera arrives at the slot's height - FocusHeight, the target height while a slot is
    # focused, inside the same band as the camera height (HEIGHT_MIN..MAX around Jodi). Dragging moves FocusHeight until the next
    # focus; the saved camera height (CamHeight, no focus) is left alone. Dragging does not come here.
    g.call("fzc", K_MATH, "FClamp", inp={"Value": "@z.ReturnValue", "Min": str(HEIGHT_MIN), "Max": str(HEIGHT_MAX)})
    g.branch("bfb", "@a2.ReturnValue"); g.set("sfb", "FocusHeight", inp={"FocusHeight": "@fzc.ReturnValue"})
    g.set("son", "FocusOn", inp={"FocusOn": "@a2.ReturnValue"}); g.n("svs", "call_self", function="Set View Shift")
    g.chain("entry", "fc", "fach", "sz", "szm", "stf", "sti", "bfb", "sfb", "son", "svs"); g.chain("bfb:else", "son"); return fn("Update Focus", graph=g)


# ---------------- Language: static panel texts, language choice ----------------
PANEL_STRINGS = [("search", "Lbl_Search"), ("chipsearch", "Lbl_Search"), ("onlyowned", "Lbl_OnlyOwned"), ("onlyfav", "Lbl_OnlyFav"), ("onlyvanilla", "Lbl_OnlyVanilla"), ("onlyworn", "Lbl_OnlyWorn"), ("favorites", "Lbl_Favorites"), ("all", "Lbl_All"), ("listhint", "Lbl_ListHint"),
                 ("lookonlyfav", "Lbl_OnlyFav"), ("lookonlyworn", "Lbl_OnlyWorn"), ("lookfavorites", "Lbl_Favorites"), ("lookall", "Lbl_All"),
                 ("worn", "Lbl_Worn"), ("inbag", "Lbl_InBag"), ("bagempty", "Lbl_BagEmpty"), ("breast", "Lbl_Breast"), ("waist", "Lbl_Waist"),
                 ("scbreast", "Lbl_ScBreast"), ("scwaist", "Lbl_ScWaist"), ("scglutes", "Lbl_ScGlutes"), ("scthighs", "Lbl_ScThighs"), ("sccalves", "Lbl_ScCalves"), ("scarms", "Lbl_ScArms"), ("schands", "Lbl_ScHands"), ("scfeet", "Lbl_ScFeet"), ("scheight", "Lbl_ScHeight"),
                 ("scroll", "Lbl_Scroll"), ("scale", "Lbl_Scale"), ("quickalpha", "Lbl_QuickAlpha"), ("outfitscale", "Lbl_OutfitScale"), ("lookscale", "Lbl_LookScale"), ("outfitcols", "Lbl_OutfitCols"), ("outfitrows", "Lbl_OutfitRows"), ("fov", "Lbl_Fov"), ("dist", "Lbl_Dist"), ("height", "Lbl_Height"), ("grouplen", "Lbl_GroupLen"), ("chiph", "Lbl_ChipH"), ("unlimited", "Lbl_Unlimited"), ("layout", "Lbl_Layout"),
                 ("language", "Lbl_Language"), ("placeholder", "Lbl_Placeholder"), ("pan", "Lbl_Pan"), ("camright", "Lbl_CamRight"), ("nude", "Lbl_Nude"), ("merge", "Lbl_Merge"), ("mergemods", "Lbl_MergeMods"), ("chipsearchopt", "Lbl_ChipSearch"), ("tipnoprefix", "Lbl_TipNoPrefix"), ("tipnoids", "Lbl_TipNoIds"), ("conflicts", "Lbl_Conflicts"), ("conflictshint", "Lbl_ConflictsHint"), ("unowned", "Lbl_Unowned"), ("scalehint", "Lbl_ScaleHint"),
                 ("theme", "Lbl_Theme"), ("bgalpha", "Lbl_BgAlpha"), ("tilealpha", "Lbl_TileAlpha"), ("key", "Lbl_ToggleKey"), ("onlymods", "Lbl_OnlyMods"), ("casesens", "Lbl_CaseSens"), ("managesearch", "Lbl_Search"), ("looksearch", "Lbl_Search"), ("lookchipsearch", "Lbl_Search"), ("hdrname", "Lbl_HdrName"), ("hdrdisplay", "Lbl_HdrDisplay"), ("hdrorigin", "Lbl_HdrIds"), ("hdrcontent", "Btn_ModContent"), ("posesearch", "Lbl_Search"), ("posefavorites", "Lbl_Favorites"), ("poseall", "Lbl_All"), ("weaponsearch", "Lbl_Search"), ("weaponfavorites", "Lbl_Favorites"), ("weaponall", "Hdr_WeaponSkins"), ("weaponmodels", "Hdr_WeaponModels"), ("tabshint", "Lbl_TabsHint"), ("quickkey", "Lbl_QuickKey"), ("quickinwheel", "Lbl_QuickInWheel"), ("quickavailable", "Lbl_QuickAvailable"), ("tabstyle", "Lbl_TabStyle"), ("tabiconpos", "Lbl_TabIconPos"), ("themesave", "Lbl_ThemeSave"), ("themename", "Hint_ThemeName"), ("themepresets", "Lbl_ThemePresets"), ("themepresetshint", "Lbl_ThemePresetsHint"), ("managechipsearch", "Lbl_Search"), ("quickcontrol", "Lbl_QuickControl"), ("quickkeywidth", "Lbl_KeyPress")]
from gen_widgets import PANEL_TEXTS, THEME_COLS, OUTFIT_MAX
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
    g.n("roc", "call_self", function="Rebuild Option Cats")
    g.chain("entry", "s", "sv", "dl", "ist", "aps", "rtt", "roc", "ro"); return fn("Select Language", [param("choice", "int")], graph=g)


# ---------------- Body switcher (body mods = paks Body_<Name> with /Game/Mod/Body_<Name>/Female; list from the game loader's DLC_MainTable) ----------------
def f_scan_body_mods():
    """Every installed body mod, newest naming first.

    A body converted again carries MOD_PREFIX (BodyAltUI_); the same body from an earlier release carries the legacy
    prefix (Body_). Both are read, but the new name wins: the legacy pass skips a row whose name, with the prefix
    swapped, is already in the list. Two chips for one body would be the worse answer - the player cannot tell them
    apart, and only one of the two paks is the one that got fixed."""
    g = G()
    g.get("gm", "BodyMods"); g.call("cl", K_ARR, "Array_Clear", inp={"TargetArray": "@gm.BodyMods"})
    g.get("gc", "BodyCaptions"); g.call("mc", K_MAP, "Map_Clear", inp={"TargetMap": "@gc.BodyCaptions"})
    g.call("rn", K_DT, "GetDataTableRowNames", inp={"Table": P_DLC_T})
    g.foreach("fe", "@rn.OutRowNames")
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@fe.Array Element"})
    g.call("sw", K_STR, "StartsWith", inp={"SourceString": "@n2s.ReturnValue", "InPrefix": bg.MOD_PREFIX, "SearchCase": "CaseSensitive"}); g.branch("b", "@sw.ReturnValue")
    g.n("row", "get_row", table=P_DLC_T, inp={"RowName": "@fe.Array Element"}, miss="ignore"); g.brk("br", P_DLC_S, "@row.OutRow")   # row names of the same table
    g.get("gm2", "BodyMods"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gm2.BodyMods", "NewItem": "@fe.Array Element"})
    g.get("gc2", "BodyCaptions"); g.call("ma", K_MAP, "Map_Add", inp={"TargetMap": "@gc2.BodyCaptions", "Key": "@fe.Array Element", "Value": "@br.Caption"})
    g.chain("entry", "cl", "mc", "rn", "fe"); g.chain("fe", "b", "row", "add", "ma")
    # one further pass per legacy prefix, each skipping what the newer naming already brought in
    prev = "fe"
    for i, old in enumerate(bg.MOD_PREFIXES[1:]):
        q = "o%d" % i
        g.foreach(q, "@rn.OutRowNames")
        g.call(q + "n2s", K_STR, "Conv_NameToString", inp={"InName": "@%s.Array Element" % q})
        g.call(q + "sw", K_STR, "StartsWith", inp={"SourceString": "@%sn2s.ReturnValue" % q, "InPrefix": old, "SearchCase": "CaseSensitive"}); g.branch(q + "b", "@%ssw.ReturnValue" % q)
        g.call(q + "chop", K_STR, "RightChop", inp={"SourceString": "@%sn2s.ReturnValue" % q, "Count": len(old)})
        g.call(q + "cat", K_STR, "Concat_StrStr", inp={"A": bg.MOD_PREFIX, "B": "@%schop.ReturnValue" % q})
        g.call(q + "nn", K_STR, "Conv_StringToName", inp={"InString": "@%scat.ReturnValue" % q})
        g.get(q + "gm", "BodyMods"); g.call(q + "has", K_ARR, "Array_Contains", inp={"TargetArray": "@%sgm.BodyMods" % q, "ItemToFind": "@%snn.ReturnValue" % q})
        g.call(q + "not", K_MATH, "Not_PreBool", inp={"A": "@%shas.ReturnValue" % q}); g.branch(q + "b2", "@%snot.ReturnValue" % q)
        g.n(q + "row", "get_row", table=P_DLC_T, inp={"RowName": "@%s.Array Element" % q}, miss="ignore"); g.brk(q + "br", P_DLC_S, "@%srow.OutRow" % q)
        g.get(q + "gm2", "BodyMods"); g.call(q + "add", K_ARR, "Array_Add", inp={"TargetArray": "@%sgm2.BodyMods" % q, "NewItem": "@%s.Array Element" % q})
        g.get(q + "gc2", "BodyCaptions"); g.call(q + "ma", K_MAP, "Map_Add", inp={"TargetMap": "@%sgc2.BodyCaptions" % q, "Key": "@%s.Array Element" % q, "Value": "@%sbr.Caption" % q})
        g.chain(prev + ":Completed", q)
        g.chain(q, q + "b", q + "b2", q + "row", q + "add", q + "ma")
        prev = q
    return fn("Scan Body Mods", graph=g)


def f_apply_body():
    """None = default mesh (remembered from Jodi on the first call: vanilla or ~mods override), otherwise load /Game/Mod/<name>/Female.Female.
    Then vanilla `Load Player Makeup` (skin/eyes/lashes reliably re-applied), `Reset Clothes Physics`, `update body mask` and
    `Enable Boobs Physics`: SetSkeletalMesh clears every morph curve the component carries (ClearMorphTargets), so the game's
    "Nipple" morph - the one that presses that part flat under clothing - is gone, and a different physics asset costs the jiggle bodies
    as well. Both are the game's own doing, it just has to be asked. Not loadable -> default + notice."""
    g = G()
    g.get("gpl", "Wearer"); g.get("gmc", "Mesh", cls=E_CHARACTER); g.link("gpl.Wearer", "gmc.self")
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
    g.get("gpl2", "Wearer"); g.call("lpm", P_JODI_BASE, "Load Player Makeup", inp={"self": "@gpl2.Wearer"})
    g.get("gpl3", "Wearer"); g.call("rcp", P_CPB, "Reset Clothes Physics", inp={"self": "@gpl3.Wearer"})
    g.get("gpl4", "Wearer"); g.call("ubm", P_CPB, "update body mask", inp={"self": "@gpl4.Wearer"})
    g.get("gpl5", "Wearer"); g.call("ebp", P_CB, "Enable Boobs Physics", inp={"self": "@gpl5.Wearer", "hip": "true"})
    g.n("afc", "call_self", function="Apply Face")   # SetSkeletalMesh emptied the component's morph list
    g.chain("entry", "bv", "bn", "sm1", "sc1", "ssm", "sd1", "ld2", "ct", "row", "sdf", "abs", "lpm", "rcp", "ubm", "ebp", "afc"); g.chain("bv:else", "sst", "bn")
    g.chain("bn:else", "ld", "ck", "sm2", "sc2", "ssm"); g.chain("ck:CastFailed", "pop", "sm3", "sc3", "ssm")
    g.chain("ct:CastFailed", "abs"); g.chain("row:Row Not Found", "abs")
    return fn("Apply Body", [param("name", "name")], graph=g)


def f_find_menu_wearer():
    """Main menu and loading scene: the figure there is a Jodi_Intro placed in the level (a Jodi_Base, not the pawn) and
    dresses itself from the game's save. Look for it every MENU_WEARER_WAIT s, at most MENU_WEARER_TRIES times; once it is
    there, body, colours and face go on (not underwear/nude: that figure's clothes are the game's business)."""
    g = G()
    g.call("ga", K_GS, "GetActorOfClass", inp={"ActorClass": P_JODI_BASE}); g.cast("cw", P_JODI_BASE, "@ga.ReturnValue", pure=False, miss="ignore")
    g.set("sw", "Wearer", inp={"Wearer": "@cw.AsJodi Base"})
    # at once, not on the level-load timers: the loading scene may be over after two seconds, and the figure is dressed
    # already (in its own BeginPlay; the manager comes at the earliest 0.5 s later). Body first: Apply Body re-applies
    # the game's make-up and eyes, the colours go on top.
    g.n("asb", "call_self", function="Apply Saved Body"); g.n("asc", "call_self", function="Apply Saved Colors"); g.n("afc", "call_self", function="Apply Face")
    # not there yet (the scene is streamed in): again later, but not forever
    g.get("gt", "MenuTries"); g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gt.MenuTries", "B": "1"}); g.set("st", "MenuTries", inp={"MenuTries": "@inc.ReturnValue"})
    g.get("gt2", "MenuTries"); g.call("lt", K_MATH, "Less_IntInt", inp={"A": "@gt2.MenuTries", "B": str(MENU_WEARER_TRIES)}); g.branch("bl", "@lt.ReturnValue")
    g.self_("me4"); g.call("again", K_SYS, "K2_SetTimer", inp={"Object": "@me4.self", "FunctionName": "Find Menu Wearer", "Time": str(MENU_WEARER_WAIT), "bLooping": "false"})
    g.chain("entry", "ga", "cw", "sw", "asb", "asc", "afc"); g.chain("cw:CastFailed", "st", "bl", "again")
    return fn("Find Menu Wearer", graph=g)


def f_apply_saved_body():
    """At the end of BeginPlay (main menu / loading scene: in Find Menu Wearer): apply the saved body to Wearer, if there is one."""
    g = G()
    g.get("gpl", "Wearer"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gpl.Wearer"}); g.branch("bp", "@iv.ReturnValue")
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


MENU_WEARER_WAIT, MENU_WEARER_TRIES = 0.5, 60   # main menu: look for the figure every 0.5 s, give up after 30 s
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
    """BodyScales[name] = factors (persisted via SETTINGS), then apply + save. defer: save only once the sliders rest (a drag
    changes the value every frame - Save Settings Soon instead of writing AltUI.sav each time)."""
    g = G()
    g.make("mk", S_FLOATS, Values="@entry.factors")
    g.get("gm", "BodyScales"); g.call("ma", K_MAP, "Map_Add", inp={"TargetMap": "@gm.BodyScales", "Key": "@entry.name", "Value": "@mk.S_Floats"})
    g.n("ap", "call_self", function="Apply Body Scales"); g.branch("bd", "@entry.defer")
    g.n("sv", "call_self", function="Save Settings"); g.n("svl", "call_self", function="Save Settings Soon"); g.n("uf", "call_self", function="Update Focus")
    g.chain("entry", "ma", "ap", "bd", "svl", "uf"); g.chain("bd:else", "sv", "uf")
    return fn("Set Body Scale Factors", [param("name", "name"), param("factors", "float", "array"), param("defer", "bool")], graph=g)


def f_save_settings_soon():
    """Save Settings once nothing changed for SETTINGS_SAVE_DELAY seconds (Settings Save Step counts down every frame;
    Close Panel and EndPlay save anyway)."""
    g = G(); g.set("st", "SettingsSaveTimer", inp={"SettingsSaveTimer": str(SETTINGS_SAVE_DELAY)}); g.chain("entry", "st")
    return fn("Save Settings Soon", graph=g)


def f_settings_save_step():
    """Per frame: a pending Save Settings Soon counts down and saves at <= 0 (Save Settings sets the timer back to 0)."""
    g = G(); g.get("gt", "SettingsSaveTimer"); g.call("tp", K_MATH, "Greater_FloatFloat", inp={"A": "@gt.SettingsSaveTimer", "B": "0.0"}); g.branch("btp", "@tp.ReturnValue")
    g.get("gt2", "SettingsSaveTimer"); g.call("tm", K_MATH, "Subtract_FloatFloat", inp={"A": "@gt2.SettingsSaveTimer", "B": "@entry.dt"}); g.set("stm", "SettingsSaveTimer", inp={"SettingsSaveTimer": "@tm.ReturnValue"})
    g.get("gt3", "SettingsSaveTimer"); g.call("tz", K_MATH, "LessEqual_FloatFloat", inp={"A": "@gt3.SettingsSaveTimer", "B": "0.0"}); g.branch("btz", "@tz.ReturnValue")
    g.n("sv", "call_self", function="Save Settings")
    g.chain("entry", "btp", "stm", "btz", "sv")
    return fn("Settings Save Step", [param("dt", "float")], graph=g)


def f_apply_body_scales():
    """GetPostProcessInstance -> ABP_BodyScale_C. Net scale per group = Default * per-axis (1 + w * (f - 1)) with f = its slider's factor and
    w = bodyscale_groups.AXES (1 = full factor, 0 = untouched, else a Lerp); Default via Vector Or One (older Body_Scale rows); a modified bone's
    children inherit the change, so each node gets net(group) / net(parent group) (bodyscale_groups.PARENT_GROUP) - "Calves x1.00" then
    really leaves the calves alone whatever the thighs do. Cast failed -> ScaleActive false (no sliders)."""
    g = G()
    g.get("gpl", "Wearer"); g.get("gmc", "Mesh", cls=E_CHARACTER); g.link("gpl.Wearer", "gmc.self")
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
    g.get("gplb", "Wearer"); g.call("ebp", P_CB, "Enable Boobs Physics", inp={"self": "@gplb.Wearer", "hip": "true"})
    g.get("gplc", "Wearer"); g.get("gbm", "Breast Morph Weight", cls=P_CPB); g.link("gplc.Wearer", "gbm.self")
    g.get("gpld", "Wearer"); g.call("cbc", P_CPB, "Change Breast Constraint Profile", inp={"self": "@gpld.Wearer", "morph": "@gbm.Breast Morph Weight"})
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
    g.get("gcb", "CurrentBody"); g.get("gtf", "TmpFloats"); g.n("sf", "call_self", function="Set Body Scale Factors", inp={"name": "@gcb.CurrentBody", "factors": "@gtf.TmpFloats", "defer": "true"})
    g.get("gp2", "Panel"); g.call("sv", W_PANEL, "Set Body Scales", inp=dict({"self": "@gp2.Panel"}, **{k: "@gv." + k for k in SCALE_KEYS}))
    g.chain("entry", "ba", "gv", "bs"); g.chain("bs:else", *ids, "sf", "sv")
    return fn("Poll Body Scales", graph=g)


def f_log_line():
    """Debug log to Saved/SaveGames/AltUI_Log.sav (a SaveGame with one FString per line; `strings AltUI_Log.sav` reads it) -
    Blueprints cannot write text files in a Shipping build and PrintString is compiled out. A new object per game session (first
    call), "<tick> <text>", at most LOG_MAX lines, written to disk on every call so the last line survives a crash. No caller in
    the release build; ALTUI_WEAPONLOG=1 wires the weapon-model path up to it, otherwise wire "Log Line" calls in temporarily when
    a problem needs tracing (see docs/specs 2026-09-19 Nachtrag)."""
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
    # no Jodi (main menu / loading scene): only the settings, then Find Menu Wearer looks for the figure there and puts body, face and
    # colours on it - no catalog/strings/panel; the next level spawns a new manager
    g.call("gp", E_CTRL, "K2_GetPawn", inp={"self": "@spc.Output_Get"}); g.cast("cj", P_JODI, "@gp.ReturnValue", pure=False, miss="ignore")
    g.set("spl", "Player", inp={"Player": "@cj.AsJodi"})
    # Wearer = the same pawn: in the game Jodi_C is a Jodi_Base_C, the kit's stubs do not know that - hence a cast of its own (from the pawn: from Jodi the editor calls it "always fails")
    g.cast("cjb", P_JODI_BASE, "@gp.ReturnValue", pure=False); g.set("swr", "Wearer", inp={"Wearer": "@cjb.AsJodi Base"})
    g.chain("cjb:CastFailed", "isg")   # never in the game - and if it did, the panel still comes up (only the look is not applied)
    g.n("mlds", "call_self", function="Load Settings"); g.n("mfind", "call_self", function="Find Menu Wearer")
    g.chain("cj:CastFailed", "mlds", "mfind")
    g.n("isg", "call_self", function="Init Slot Groups"); g.n("bc", "call_self", function="Build Catalog"); g.n("rs", "call_self", function="Refresh State")
    g.n("lds", "call_self", function="Load Settings")
    g.n("lnm", "call_self", function="Load Names")   # before Build Catalog: display names carry the custom names
    # the saved look at once, at the end of BeginPlay: the game dresses Jodi in her own BeginPlay (Load Player Save Data,
    # covering check) and on possession (Jodi_StoryMode after a shower) - both before a spawner sees a Jodi pawn, and no
    # Delay in Jodi / GameState dresses her later. Order: body (the mesh swap re-applies the game's make-up and clears the
    # morphs), underwear (can change what is worn), colours (on what is worn now), face (morphs on the final mesh).
    g.n("asb", "call_self", function="Apply Saved Body"); g.n("flu", "call_self", function="Fix Loaded Underwear")
    g.n("asc", "call_self", function="Apply Saved Colors"); g.n("afc", "call_self", function="Apply Face")
    g.n("dl", "call_self", function="Detect Language"); g.n("ist", "call_self", function="Init Strings"); g.n("apn", "call_self", function="Apply Nude")
    g.n("bga", "call_self", function="Build Group Aliases")   # Build Catalog ran before Load Settings: apply the loaded MergeGroups option
    g.n("bcf", "call_self", function="Build Conflicts")   # slot conflict pairs from ClothesTypeTable
    g.chain("bp", "cpc", "spc", "ei", "cj", "spl", "cjb", "swr", "isg", "bcf", "lnm", "bc", "lds", "bga", "apn", "dl", "ist", "rs", "asb", "flu", "asc", "afc")
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
    # quick key (Pressed, held): the wheel, only with the panel closed and Jodi taking input; its release goes to the wheel widget
    g.get("gqk", "QuickKey"); g.call("qks", K_STR, "Conv_NameToString", inp={"InName": "@gqk.QuickKey"})
    g.call("qeq", K_STR, "EqualEqual_StriStri", inp={"A": "@kds.ReturnValue", "B": "@qks.ReturnValue"})
    g.get("gpo", "PanelOpen"); g.get("gqo", "QuickOpen"); g.call("qbusy", K_MATH, "BooleanOR", inp={"A": "@gpo.PanelOpen", "B": "@gqo.QuickOpen"}); g.call("qfree", K_MATH, "Not_PreBool", inp={"A": "@qbusy.ReturnValue"})
    g.call("qa", K_MATH, "BooleanAND", inp={"A": "@qeq.ReturnValue", "B": "@qfree.ReturnValue"}); g.call("qb", K_MATH, "BooleanAND", inp={"A": "@qa.ReturnValue", "B": "@ie.yes"}); g.branch("bq", "@qb.ReturnValue")
    g.n("oqw", "call_self", function="Open Quick Wheel"); g.chain("kAny:Pressed", "bq", "oqw")
    # Tick: poll the checkboxes (no delegates)
    g.event("tick", E_ACTOR, "ReceiveTick")
    g.n("tct", "call_self", function="Cam Tick", inp={"dt": "@tick.DeltaSeconds"})   # free cam step / photo mode end detection
    g.n("tssv", "call_self", function="Settings Save Step", inp={"dt": "@tick.DeltaSeconds"})   # deferred Save Settings (body sliders)
    g.get("tpo", "PanelOpen"); g.branch("tb0", "@tpo.PanelOpen")
    g.get("tp1", "Panel"); g.call("too", W_PANEL, "Get Only Owned", inp={"self": "@tp1.Panel"})
    g.get("tp2", "Panel"); g.call("tof", W_PANEL, "Get Only Fav", inp={"self": "@tp2.Panel"})
    g.get("tp3", "Panel"); g.call("tov", W_PANEL, "Get Only Vanilla", inp={"self": "@tp3.Panel"})
    g.get("tp4", "Panel"); g.call("tow", W_PANEL, "Get Only Worn", inp={"self": "@tp4.Panel"})
    g.get("tco", "CachedOnlyOwned"); g.get("tcf", "CachedOnlyFav"); g.get("tcv", "CachedOnlyVanilla"); g.get("tcwo", "CachedOnlyWorn")
    g.call("tn1", K_MATH, "NotEqual_BoolBool", inp={"A": "@too.yes", "B": "@tco.CachedOnlyOwned"})
    g.call("tn2", K_MATH, "NotEqual_BoolBool", inp={"A": "@tof.yes", "B": "@tcf.CachedOnlyFav"})
    g.call("tn3", K_MATH, "NotEqual_BoolBool", inp={"A": "@tov.yes", "B": "@tcv.CachedOnlyVanilla"})
    g.call("tor0", K_MATH, "BooleanOR", inp={"A": "@tn1.ReturnValue", "B": "@tn2.ReturnValue"})
    g.call("tn4", K_MATH, "NotEqual_BoolBool", inp={"A": "@tow.yes", "B": "@tcwo.CachedOnlyWorn"})   # "only worn" belongs here too: without it the box only took effect at the next rebuild
    g.call("tor", K_MATH, "BooleanOR", inp={"A": "@tor0.ReturnValue", "B": "@tn3.ReturnValue"})
    g.call("tor1", K_MATH, "BooleanOR", inp={"A": "@tor.ReturnValue", "B": "@tn4.ReturnValue"}); g.branch("tb1", "@tor1.ReturnValue")
    g.n("trlf", "call_self", function="Rebuild Left"); g.n("trl", "call_self", function="Rebuild List"); g.n("tsv", "call_self", function="Save Settings")   # Rebuild List refreshes the caches -> persist
    g.get("tpl", "Panel"); g.call("tglf", W_PANEL, "Get Look Only Fav", inp={"self": "@tpl.Panel"}); g.get("tlof", "LookOnlyFav"); g.call("tlqn", K_MATH, "NotEqual_BoolBool", inp={"A": "@tglf.yes", "B": "@tlof.LookOnlyFav"}); g.branch("tlqb", "@tlqn.ReturnValue")
    g.set("tlqs", "LookOnlyFav", inp={"LookOnlyFav": "@tglf.yes"}); g.n("tlqv", "call_self", function="Save Settings"); g.n("tlqc", "call_self", function="Rebuild Look Cats"); g.n("tlqk", "call_self", function="Rebuild Look")
    g.get("tpw", "Panel"); g.call("tglw", W_PANEL, "Get Look Only Worn", inp={"self": "@tpw.Panel"}); g.get("tlow", "LookOnlyWorn"); g.call("tlwn", K_MATH, "NotEqual_BoolBool", inp={"A": "@tglw.yes", "B": "@tlow.LookOnlyWorn"}); g.branch("tlwb", "@tlwn.ReturnValue")
    g.set("tlws", "LookOnlyWorn", inp={"LookOnlyWorn": "@tglw.yes"}); g.n("tlwv", "call_self", function="Save Settings"); g.n("tlwc", "call_self", function="Rebuild Look Cats"); g.n("tlwk", "call_self", function="Rebuild Look")
    g.get("tco2", "ColorOpen"); g.branch("tbc", "@tco2.ColorOpen"); g.n("tap", "call_self", function="Apply Preview")
    g.get("tpg", "Page"); g.call("tib", K_MATH, "EqualEqual_NameName", inp={"A": "@tpg.Page", "B": "Body"}); g.branch("tbb", "@tib.ReturnValue"); g.n("tpb", "call_self", function="Poll Body"); g.n("tpbs", "call_self", function="Poll Body Scales")
    g.get("tpg2", "Page"); g.call("tio", K_MATH, "EqualEqual_NameName", inp={"A": "@tpg2.Page", "B": "Options"}); g.branch("tbo", "@tio.ReturnValue"); g.n("tpo2", "call_self", function="Poll Options")
    g.get("tpg3", "Page"); g.call("tim", K_MATH, "EqualEqual_NameName", inp={"A": "@tpg3.Page", "B": "Manage"}); g.branch("tbmg", "@tim.ReturnValue"); g.n("tpm", "call_self", function="Poll Manage")
    g.get("tpg4", "Page"); g.call("timd", K_MATH, "EqualEqual_NameName", inp={"A": "@tpg4.Page", "B": "Mods"}); g.branch("tbmd", "@timd.ReturnValue"); g.n("tpmd", "call_self", function="Poll Mods")
    g.get("tsw", "IconSpawnWait"); g.call("tswg", K_MATH, "Greater_IntInt", inp={"A": "@tsw.IconSpawnWait", "B": "0"}); g.branch("tbsw", "@tswg.ReturnValue")
    g.get("tsw2", "IconSpawnWait"); g.call("tswd", K_MATH, "Subtract_IntInt", inp={"A": "@tsw2.IconSpawnWait", "B": "1"}); g.set("tsws", "IconSpawnWait", inp={"IconSpawnWait": "@tswd.ReturnValue"})
    g.get("tsw3", "IconSpawnWait"); g.call("tswz", K_MATH, "EqualEqual_IntInt", inp={"A": "@tsw3.IconSpawnWait", "B": "0"}); g.branch("tbswz", "@tswz.ReturnValue"); g.n("tcws", "call_self", function="Capture Weapon Icon Step")
    g.get("tif", "IconFrames"); g.call("tig", K_MATH, "Greater_IntInt", inp={"A": "@tif.IconFrames", "B": "0"}); g.branch("tbi", "@tig.ReturnValue")
    g.get("tif2", "IconFrames"); g.call("tid", K_MATH, "Subtract_IntInt", inp={"A": "@tif2.IconFrames", "B": "1"}); g.set("tis", "IconFrames", inp={"IconFrames": "@tid.ReturnValue"})
    g.get("tif3", "IconFrames"); g.call("tiz", K_MATH, "EqualEqual_IntInt", inp={"A": "@tif3.IconFrames", "B": "0"}); g.branch("tbz", "@tiz.ReturnValue"); g.n("tfi", "call_self", function="Finish Photo")
    g.n("twq", "call_self", function="Wear Queue Step"); g.n("tns", "call_self", function="Start Next Snapshot")
    g.get("tkc", "TickCount"); g.call("tkc1", K_MATH, "Add_IntInt", inp={"A": "@tkc.TickCount", "B": "1"}); g.set("tkcs", "TickCount", inp={"TickCount": "@tkc1.ReturnValue"})   # frame counter (Log Line prefix)
    # tile rename field: poll the tile for focus loss (cancel); forget it once the field is closed
    g.get("trnt", "RenameTile"); g.cast("trc", W_BTN, "@trnt.RenameTile"); g.call("trv", K_SYS, "IsValid", inp={"Object": "@trc.AsW_ClothesButton"}); g.branch("tbr", "@trv.ReturnValue")
    g.call("tpr", W_BTN, "Poll Rename", inp={"self": "@trc.AsW_ClothesButton"}); g.branch("tba", "@tpr.active"); g.set("trs", "RenameTile", inp={"RenameTile": "None"})
    g.chain("tick", "tct", "tssv", "tkcs", "twq", "tns", "tbr", "tpr", "tba", "tbsw"); g.chain("tba:else", "trs", "tbsw"); g.chain("tbr:else", "tbsw")
    g.chain("tbsw", "tsws", "tbswz", "tcws", "tbi"); g.chain("tbswz:else", "tbi"); g.chain("tbsw:else", "tbi")
    g.chain("tbi", "tis", "tbz", "tfi", "tb0"); g.chain("tbz:else", "tb0"); g.chain("tbi:else", "tb0")
    g.get("tpx", "Panel"); g.call("tsc", W_PANEL, "Sync Check Size", inp={"self": "@tpx.Panel"})
    g.chain("tb0", "tsc", "tbb"); g.chain("tbb", "tpb", "tpbs", "tb1"); g.chain("tbb:else", "tbo", "tpo2", "tb1"); g.chain("tbo:else", "tbmg", "tpm", "tb1"); g.chain("tbmg:else", "tbmd", "tpmd", "tb1"); g.chain("tbmd:else", "tb1"); g.chain("tb1", "trlf", "trl", "tsv"); g.chain("tb0:else", "tbc", "tap"); g.chain("tb1:else", "tlqb", "tlqs", "tlqv", "tlqc", "tlqk", "tlwb"); g.chain("tlqb:else", "tlwb")
    g.chain("tlwb", "tlws", "tlwv", "tlwc", "tlwk", "tbc"); g.chain("tlwb:else", "tbc")
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
    g.custom("tf", "Test Filter", [param("slot", "name"), param("group", "name"), param("search", "string"), param("onlyOwned", "bool"), param("onlyFav", "bool"), param("onlyVanilla", "bool"), param("onlyWorn", "bool")])
    g.n("tf_it", "call_self", function="Filtered Items", inp={"slot": "@tf.slot", "group": "@tf.group", "search": "@tf.search", "onlyOwned": "@tf.onlyOwned", "onlyFav": "@tf.onlyFav", "onlyVanilla": "@tf.onlyVanilla", "onlyWorn": "@tf.onlyWorn"})
    g.get("tf_gn", "TmpNames"); g.call("tf_clr", K_ARR, "Array_Clear", inp={"TargetArray": "@tf_gn.TmpNames"})
    g.foreach("tf_fe", "@tf_it.items"); g.brk("tf_b", S_ITEM, "@tf_fe.Array Element")
    g.get("tf_gn2", "TmpNames"); g.call("tf_add", K_ARR, "Array_Add", inp={"TargetArray": "@tf_gn2.TmpNames", "NewItem": "@tf_b.Name"})
    g.chain("tf", "tf_it", "tf_clr", "tf_fe"); g.chain("tf_fe", "tf_add")
    g.custom("tfn", "Test Filtered Counts", [param("search", "string"), param("onlyOwned", "bool"), param("onlyFav", "bool"), param("onlyVanilla", "bool"), param("onlyWorn", "bool")])
    g.n("tfn_c", "call_self", function="Filtered Counts", inp={"search": "@tfn.search", "onlyOwned": "@tfn.onlyOwned", "onlyFav": "@tfn.onlyFav", "onlyVanilla": "@tfn.onlyVanilla", "onlyWorn": "@tfn.onlyWorn"}); g.chain("tfn", "tfn_c")
    g.custom("tchc", "Test Chip Caption", [param("group", "name"), param("full", "bool")]); g.n("tchc_c", "call_self", function="Chip Caption", inp={"group": "@tchc.group", "full": "@tchc.full"})
    g.set("tchc_s", "TmpText", inp={"TmpText": "@tchc_c.caption"}); g.chain("tchc", "tchc_c", "tchc_s")
    g.custom("tssl", "Test Select Slot", [param("name", "name")]); g.n("tssl_s", "call_self", function="Select Slot", inp={"name": "@tssl.name"}); g.chain("tssl", "tssl_s")
    g.custom("tcsh", "Test Chip Shown", [param("group", "name")]); g.n("tcsh_c", "call_self", function="Chip Shown", inp={"group": "@tcsh.group"})
    g.set("tcsh_s", "TmpBool", inp={"TmpBool": "@tcsh_c.yes"}); g.chain("tcsh", "tcsh_s")
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
    # colour: the probe (real materials from the kit), the slots of a row and what the tile badge ends up with
    g.custom("tmtc", "Test Material Takes Color", [param("mat", "object:/Script/Engine.MaterialInterface")])
    g.n("tmtc_c", "call_self", function="Material Takes Color", inp={"mat": "@tmtc.mat"}); g.set("tmtc_s", "TmpBool", inp={"TmpBool": "@tmtc_c.yes"}); g.chain("tmtc", "tmtc_c", "tmtc_s")
    g.custom("tcsl", "Test Color Slots", [param("name", "name")]); g.n("tcsl_c", "call_self", function="Item Color Slots", inp={"name": "@tcsl.name"})
    g.brk("tcsl_b", S_COLSLOTS, "@tcsl_c.slots"); g.call("tcsl_n", K_ARR, "Array_Length", inp={"TargetArray": "@tcsl_b.Idx"})
    g.set("tcsl_s", "TmpI", inp={"TmpI": "@tcsl_n.ReturnValue"}); g.set("tcsl_s2", "TmpNames", inp={"TmpNames": "@tcsl_b.Caption"}); g.chain("tcsl", "tcsl_c", "tcsl_s", "tcsl_s2")
    g.custom("tsnc", "Test Snapshot Colors"); g.n("tsnc_t", "call_self", function="Take Snapshot"); g.brk("tsnc_b", S_SNAP, "@tsnc_t.snap")
    g.set("tsnc_s", "TmpColors", inp={"TmpColors": "@tsnc_b.SlotColors"}); g.set("tsnc_s2", "TmpColors2", inp={"TmpColors2": "@tsnc_b.EyeColors"}); g.set("tsnc_s3", "TmpFColors2", inp={"TmpFColors2": "@tsnc_b.MakeupColors"})
    g.chain("tsnc", "tsnc_t", "tsnc_s", "tsnc_s2", "tsnc_s3")
    g.custom("ter", "Test Eye Reset", [param("row", "name")]); g.n("ter_c", "call_self", function="Eye Reset Colors", inp={"row": "@ter.row"}); g.chain("ter", "ter_c")
    g.custom("tmkc", "Test Set Makeup Color", [param("row", "name"), param("color", S_LINCOLOR)])
    g.n("tmkc_c", "call_self", function="Set Makeup Color", inp={"row": "@tmkc.row", "color": "@tmkc.color"}); g.chain("tmkc", "tmkc_c")
    g.custom("tmkr", "Test Makeup Reset", [param("name", "name")]); g.n("tmkr_c", "call_self", function="Makeup Reset Color", inp={"name": "@tmkr.name"}); g.chain("tmkr", "tmkr_c")
    g.custom("trim", "Test Row Is Makeup", [param("row", "name")]); g.n("trim_c", "call_self", function="Row Is Makeup", inp={"row": "@trim.row"})
    g.set("trim_s", "TmpBool", inp={"TmpBool": "@trim_c.found"}); g.chain("trim", "trim_s")
    g.custom("trhm", "Test Row Has Makeup Color", [param("row", "name")]); g.n("trhm_c", "call_self", function="Row Has Makeup Color", inp={"row": "@trhm.row"})
    g.set("trhm_s", "TmpBool", inp={"TmpBool": "@trhm_c.found"}); g.chain("trhm", "trhm_s")
    g.custom("tms", "Test Mod Scan"); g.n("tms_c", "call_self", function="Scan Mod Entries"); g.chain("tms", "tms_c")
    g.custom("tmf", "Test Mod Fields", [param("key", "name")])
    g.get("tmf_g", "TmpNames"); g.call("tmf_clr", K_ARR, "Array_Clear", inp={"TargetArray": "@tmf_g.TmpNames"})
    g.get("tmf_m", "ModFields"); g.call("tmf_f", K_MAP, "Map_Find", inp={"TargetMap": "@tmf_m.ModFields", "Key": "@tmf.key"}); g.brk("tmf_b", mu.LIST_STRUCT, "@tmf_f.Value")
    g.foreach("tmf_fe", "@tmf_b.Fields"); g.brk("tmf_bf", mu.FIELD_STRUCT, "@tmf_fe.Array Element")
    g.get("tmf_g2", "TmpNames"); g.call("tmf_add", K_ARR, "Array_Add", inp={"TargetArray": "@tmf_g2.TmpNames", "NewItem": "@tmf_bf.Key"})
    g.chain("tmf", "tmf_clr", "tmf_fe"); g.chain("tmf_fe", "tmf_add")
    g.custom("tek", "Test Eye Key", [param("part", "name"), param("row", "name")]); g.n("tek_k", "call_self", function="Eye Color Key", inp={"part": "@tek.part", "row": "@tek.row"})
    g.set("tek_s", "TmpName", inp={"TmpName": "@tek_k.key"}); g.chain("tek", "tek_s")
    g.custom("tlcs", "Test Look Chip Shown", [param("group", "name")]); g.n("tlcs_c", "call_self", function="Look Chip Shown", inp={"group": "@tlcs.group"})
    g.set("tlcs_s", "TmpBool", inp={"TmpBool": "@tlcs_c.yes"}); g.chain("tlcs", "tlcs_s")
    g.custom("tlrp", "Test Look Row Passes", [param("kind", "name"), param("row", "name")]); g.n("tlrp_c", "call_self", function="Look Row Passes", inp={"kind": "@tlrp.kind", "row": "@tlrp.row"})
    g.set("tlrp_s", "TmpBool", inp={"TmpBool": "@tlrp_c.yes"}); g.chain("tlrp", "tlrp_c", "tlrp_s")
    g.custom("tclr", "Test Current Look Row", [param("type", "name")]); g.n("tclr_c", "call_self", function="Current Look Row", inp={"type": "@tclr.type"})
    g.set("tclr_s", "TmpName", inp={"TmpName": "@tclr_c.row"}); g.chain("tclr", "tclr_c", "tclr_s")
    for _cat in dict.fromkeys(c for _, _, _, _, c in EYE_PARTS):
        q = "tri" + _cat
        g.custom(q, "Test Row Is " + _cat, [param("row", "name")]); g.n(q + "_c", "call_self", function="Row Is " + _cat, inp={"row": "@%s.row" % q})
        g.set(q + "_s", "TmpBool", inp={"TmpBool": "@%s_c.found" % q}); g.chain(q, q + "_s")
    g.custom("tsk", "Test Slot Key", [param("name", "name"), param("slot", "int")]); g.n("tsk_k", "call_self", function="Slot Color Key", inp={"name": "@tsk.name", "slot": "@tsk.slot"})
    g.set("tsk_s", "TmpName", inp={"TmpName": "@tsk_k.key"}); g.chain("tsk", "tsk_s")
    g.custom("tssc", "Test Save Slot Color", [param("name", "name"), param("slot", "int"), param("color", S_LINCOLOR)])
    g.n("tssc_c", "call_self", function="Save Slot Color", inp={"name": "@tssc.name", "slot": "@tssc.slot", "color": "@tssc.color"}); g.chain("tssc", "tssc_c")
    g.custom("thoc", "Test Has Own Color", [param("name", "name")]); g.n("thoc_c", "call_self", function="Item Has Own Color", inp={"name": "@thoc.name"})
    g.set("thoc_s", "TmpBool", inp={"TmpBool": "@thoc_c.found"}); g.chain("thoc", "thoc_c", "thoc_s")
    g.custom("tsrc", "Test Slot Reset Color", [param("name", "name")]); g.n("tsrc_c", "call_self", function="Slot Reset Color", inp={"name": "@tsrc.name"}); g.chain("tsrc", "tsrc_c")
    g.custom("tcsi", "Test Color Slot Idx", [param("name", "name"), param("pos", "int")]); g.n("tcsi_c", "call_self", function="Item Color Slots", inp={"name": "@tcsi.name"})
    g.brk("tcsi_b", S_COLSLOTS, "@tcsi_c.slots"); g.call("tcsi_g", K_ARR, "Array_Get", inp={"TargetArray": "@tcsi_b.Idx", "Index": "@tcsi.pos"})
    g.set("tcsi_s", "TmpI", inp={"TmpI": "@tcsi_g.Item"}); g.chain("tcsi", "tcsi_c", "tcsi_s")
    g.custom("tcol", "Test Item Colorable", [param("name", "name")]); g.n("tcol_f", "call_self", function="Find Item", inp={"name": "@tcol.name"})
    g.brk("tcol_b", S_ITEM, "@tcol_f.item"); g.set("tcol_s", "TmpBool", inp={"TmpBool": "@tcol_b.ColorAdjustable"}); g.chain("tcol", "tcol_f", "tcol_s")
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
    g.custom("tqs", "Test Quick Sector At", [param("dx", "float"), param("dy", "float"), param("radius", "float"), param("count", "int")]); g.n("tqs_c", "call_self", function="Quick Sector At", inp={"dx": "@tqs.dx", "dy": "@tqs.dy", "radius": "@tqs.radius", "count": "@tqs.count"}); g.set("tqs_s", "TmpI", inp={"TmpI": "@tqs_c.index"}); g.chain("tqs", "tqs_s")
    g.custom("tqa", "Test Quick Add", [param("item", "string")]); g.n("tqa_c", "call_self", function="Quick Add", inp={"item": "@tqa.item"}); g.chain("tqa", "tqa_c")
    g.custom("tqr", "Test Quick Remove", [param("item", "string")]); g.n("tqr_c", "call_self", function="Quick Remove", inp={"item": "@tqr.item"}); g.chain("tqr", "tqr_c")
    g.custom("tqm", "Test Quick Move", [param("item", "string"), param("delta", "int")]); g.n("tqm_c", "call_self", function="Quick Move", inp={"item": "@tqm.item", "delta": "@tqm.delta"}); g.chain("tqm", "tqm_c")
    g.custom("tqf", "Test Quick Find", [param("item", "string")]); g.n("tqf_c", "call_self", function="Quick Find", inp={"item": "@tqf.item"}); g.set("tqf_s", "TmpBool", inp={"TmpBool": "@tqf_c.ok"}); g.chain("tqf", "tqf_c", "tqf_s")
    g.custom("ttsh", "Test Tab Shown", [param("page", "name")]); g.n("ttsh_c", "call_self", function="Tab Shown", inp={"page": "@ttsh.page"}); g.set("ttsh_s", "TmpBool", inp={"TmpBool": "@ttsh_c.yes"}); g.chain("ttsh", "ttsh_s")
    g.custom("tfvp", "Test First Visible Page"); g.n("tfvp_c", "call_self", function="First Visible Page"); g.set("tfvp_s", "TmpName", inp={"TmpName": "@tfvp_c.page"}); g.chain("tfvp", "tfvp_s")
    g.custom("tttg", "Test Toggle Tab Hidden", [param("page", "name")]); g.n("tttg_c", "call_self", function="Toggle Tab Hidden", inp={"page": "@tttg.page"}); g.chain("tttg", "tttg_c")
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
    g.custom("tmcn", "Test Manage Count", [param("cat", "name")]); g.n("tmcn_c", "call_self", function="Manage Count", inp={"cat": "@tmcn.cat", "search": "", "chip": "false"}); g.call("tmcn_k", K_MATH, "Conv_IntToInt64", inp={"InInt": "@tmcn_c.n"}); g.set("tmcn_s", "TmpKey", inp={"TmpKey": "@tmcn_k.ReturnValue"}); g.chain("tmcn", "tmcn_c", "tmcn_s")
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
    # Test Legacy Layout: a save from before SAVE_VERSION 2 with the old layout default ("no space for Jodi", 0)
    g.custom("tlyl", "Test Legacy Layout"); tail = ["tlyl"]
    for name, val in (("SaveVersion", "1"), ("LeftFree", "0")):
        g.get("tlyl_g" + name, "Settings"); g.n("tlyl_s" + name, "set", var=name, cls=SG, inp={"self": "@tlyl_g%s.Settings" % name, name: val}); tail.append("tlyl_s" + name)
    g.get("tlyl_gs", "Settings"); g.call("tlyl_sv", K_GS, "SaveGameToSlot", inp={"SaveGameObject": "@tlyl_gs.Settings", "SlotName": "AltUI", "UserIndex": "0"}); g.chain(*tail, "tlyl_sv")
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
    # poses (editor test): rows without Dressup_*, title fallback, key, mod origin
    g.custom("tps_r", "Test Pose Rows"); g.n("tps_r_c", "call_self", function="Collect Pose Rows"); g.get("tps_r_g", "PoseRows"); g.call("tps_r_l", K_ARR, "Array_Length", inp={"TargetArray": "@tps_r_g.PoseRows"})
    g.set("tps_r_s", "TmpI", inp={"TmpI": "@tps_r_l.ReturnValue"}); g.chain("tps_r", "tps_r_c", "tps_r_s")
    g.custom("tps_t", "Test Pose Title", [param("row", "name")]); g.n("tps_t_c", "call_self", function="Pose Title", inp={"row": "@tps_t.row"}); g.set("tps_t_s", "TmpStr", inp={"TmpStr": "@tps_t_c.title"}); g.chain("tps_t", "tps_t_c", "tps_t_s")
    g.custom("tps_k", "Test Pose Key", [param("row", "name")]); g.n("tps_k_c", "call_self", function="Pose Key", inp={"row": "@tps_k.row"}); g.set("tps_k_s", "TmpName", inp={"TmpName": "@tps_k_c.key"}); g.chain("tps_k", "tps_k_s")
    g.custom("tps_a", "Test Pose Actors", [param("mod", "name")]); g.n("tps_a_c", "call_self", function="Pose Actors", inp={"mod": "@tps_a.mod"})
    g.call("tps_a_l", K_ARR, "Array_Length", inp={"TargetArray": "@tps_a_c.actors"}); g.set("tps_a_s", "TmpI", inp={"TmpI": "@tps_a_l.ReturnValue"}); g.chain("tps_a", "tps_a_c", "tps_a_s")
    g.custom("tpc_s", "Test Set Pose Kind", [param("row", "name"), param("kind", "name"), param("moving", "bool")])
    g.n("tpc_s_c", "call_self", function="Set Pose Kind", inp={"row": "@tpc_s.row", "kind": "@tpc_s.kind", "moving": "@tpc_s.moving"}); g.chain("tpc_s", "tpc_s_c")
    g.custom("tpc_k", "Test Pose Kind", [param("row", "name")]); g.n("tpc_k_c", "call_self", function="Pose Kind", inp={"row": "@tpc_k.row"})
    g.set("tpc_k_s", "TmpName", inp={"TmpName": "@tpc_k_c.kind"}); g.n("tpc_k_m", "call_self", function="Is Pose Moving", inp={"row": "@tpc_k.row"}); g.set("tpc_k_b", "TmpBool", inp={"TmpBool": "@tpc_k_m.yes"}); g.chain("tpc_k", "tpc_k_s", "tpc_k_b")
    g.custom("tps_m", "Test Pose Mod", [param("row", "name")]); g.n("tps_m_c", "call_self", function="Scan Mod Items"); g.n("tps_m_m", "call_self", function="Item Mod", inp={"row": "@tps_m.row"}); g.set("tps_m_s", "TmpName", inp={"TmpName": "@tps_m_m.mod"}); g.chain("tps_m", "tps_m_c", "tps_m_s")
    # weapons (editor test)
    g.custom("twp_r", "Test Weapon Rows"); g.n("twp_r_c", "call_self", function="Weapon Rows"); g.call("twp_r_l", K_ARR, "Array_Length", inp={"TargetArray": "@twp_r_c.rows"})
    g.set("twp_r_s", "TmpI", inp={"TmpI": "@twp_r_l.ReturnValue"}); g.chain("twp_r", "twp_r_c", "twp_r_s")
    g.custom("twp_s", "Test Skins For Weapon", [param("weapon", "name")]); g.n("twp_s_sc", "call_self", function="Scan Weapon Skins")
    g.n("twp_s_c", "call_self", function="Skins For Weapon", inp={"weapon": "@twp_s.weapon"}); g.call("twp_s_l", K_ARR, "Array_Length", inp={"TargetArray": "@twp_s_c.rows"})
    g.set("twp_s_s", "TmpI", inp={"TmpI": "@twp_s_l.ReturnValue"}); g.chain("twp_s", "twp_s_sc", "twp_s_c", "twp_s_s")
    g.custom("twp_md", "Test Models For Weapon", [param("weapon", "name")]); g.n("twp_md_sc", "call_self", function="Scan Weapon Models")
    g.n("twp_md_c", "call_self", function="Models For Weapon", inp={"weapon": "@twp_md.weapon"}); g.call("twp_md_l", K_ARR, "Array_Length", inp={"TargetArray": "@twp_md_c.rows"})
    g.set("twp_md_s", "TmpI", inp={"TmpI": "@twp_md_l.ReturnValue"}); g.chain("twp_md", "twp_md_sc", "twp_md_c", "twp_md_s")
    g.custom("twp_mm", "Test Model Mod", [param("row", "name")]); g.n("twp_mm_sc", "call_self", function="Scan Weapon Models"); g.n("twp_mm_c", "call_self", function="Model Mod", inp={"row": "@twp_mm.row"})
    g.set("twp_mm_s", "TmpName", inp={"TmpName": "@twp_mm_c.mod"}); g.chain("twp_mm", "twp_mm_sc", "twp_mm_s")
    g.custom("twp_i", "Test Weapon Icon", [param("weapon", "name"), param("model", "name"), param("skin", "name")])
    g.n("twp_i_c", "call_self", function="Weapon Icon", inp={"weapon": "@twp_i.weapon", "model": "@twp_i.model", "skin": "@twp_i.skin"})
    g.set("twp_i_s", "TmpBool", inp={"TmpBool": "@twp_i_c.missing"}); g.chain("twp_i", "twp_i_c", "twp_i_s")
    g.custom("twp_m", "Test Skin Mod", [param("row", "name")]); g.n("twp_m_sc", "call_self", function="Scan Weapon Skins"); g.n("twp_m_c", "call_self", function="Skin Mod", inp={"row": "@twp_m.row"})
    g.set("twp_m_s", "TmpName", inp={"TmpName": "@twp_m_c.mod"}); g.chain("twp_m", "twp_m_sc", "twp_m_s")
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
    g.custom("tadi", "Test Add Preset Icon", [param("icon", "int")]); g.make("tadi_mk", P_PRESET_S, SkinName="Skin_Default", IconNumber="@tadi.icon")
    tadi_pd = presets_data(g, "tadi_pd"); g.call("tadi_aa", K_ARR, "Array_Add", inp={"TargetArray": tadi_pd, "NewItem": "@tadi_mk.MakeupPreset_Struct"}); g.chain("tadi", "tadi_aa")
    g.custom("tsch", "Test Sort Chips", [param("groups", "name", "array"), param("look", "bool")]); g.n("tsch_c", "call_self", function="Sort Chips", inp={"groups": "@tsch.groups", "look": "@tsch.look"})
    g.set("tsch_s", "ChipOrder", inp={"ChipOrder": "@tsch_c.sorted"}); g.chain("tsch", "tsch_c", "tsch_s")
    g.custom("tafc", "Test Add Face", [param("name", "string"), param("add", "bool")]); tafc_h, tafc_t = ensure_faces(g)
    g.get("tafc_fv", "FaceValues"); g.make("tafc_mk", fc.S_FACE, Name="@tafc.name", Values="@tafc_fv.FaceValues", FaceAdd="@tafc.add")
    tafc_a = faces_array(g, "tafc_fa"); g.call("tafc_aa", K_ARR, "Array_Add", inp={"TargetArray": tafc_a, "NewItem": "@tafc_mk.S_Face"})
    g.chain("tafc", *tafc_h); [g.chain(t, "tafc_aa") for t in tafc_t]
    g.custom("tsfc", "Test Snap Face", [param("key", "name")]); g.get("tsfc_v", "ViewSnap"); g.brk("tsfc_b", S_SNAP, "@tsfc_v.ViewSnap")
    g.call("tsfc_l", K_MAP, "Map_Length", inp={"TargetMap": "@tsfc_b.Face"}); g.call("tsfc_f", K_MAP, "Map_Find", inp={"TargetMap": "@tsfc_b.Face", "Key": "@tsfc.key"})
    g.set("tsfc_s1", "TmpI", inp={"TmpI": "@tsfc_l.ReturnValue"}); g.set("tsfc_s2", "TmpFloat", inp={"TmpFloat": "@tsfc_f.Value"}); g.set("tsfc_s3", "TmpBool", inp={"TmpBool": "@tsfc_b.FaceAdd"})
    g.chain("tsfc", "tsfc_s1", "tsfc_s2", "tsfc_s3")
    g.custom("tstp", "Test Save Theme Preset", [param("name", "string")]); g.n("tstp_c", "call_self", function="Save Theme Preset", inp={"name": "@tstp.name"})
    g.set("tstp_s", "TmpBool", inp={"TmpBool": "@tstp_c.ok"}); g.chain("tstp", "tstp_c", "tstp_s")
    g.custom("tatp", "Test Apply Theme Preset", [param("name", "name")]); g.n("tatp_c", "call_self", function="Apply Theme Preset", inp={"name": "@tatp.name"}); g.chain("tatp", "tatp_c")
    g.custom("tdtp", "Test Delete Theme Preset", [param("name", "name")]); g.n("tdtp_c", "call_self", function="Delete Theme Preset", inp={"name": "@tdtp.name"}); g.chain("tdtp", "tdtp_c")
    for tid, fname in (("tosc", "Outfit Scale"), ("tlsc", "Look Scale")):
        g.custom(tid, "Test " + fname); g.n(tid + "_c", "call_self", function=fname); g.set(tid + "_s", "TmpFloat", inp={"TmpFloat": "@%s_c.scale" % tid}); g.chain(tid, tid + "_s")
    g.custom("tqal", "Test Quick Alpha"); g.n("tqal_c", "call_self", function="Quick Alpha"); g.set("tqal_s", "TmpFloat", inp={"TmpFloat": "@tqal_c.alpha"}); g.chain("tqal", "tqal_s")
    g.custom("togr", "Test Outfit Grid"); g.n("togr_c", "call_self", function="Outfit Cols"); g.n("togr_r", "call_self", function="Outfit Rows")
    g.set("togr_s1", "TmpI", inp={"TmpI": "@togr_c.n"}); g.set("togr_s2", "TmpIdx", inp={"TmpIdx": "@togr_r.n"}); g.chain("togr", "togr_s1", "togr_s2")
    g.custom("tmrg", "Test Manage Row Group", [param("kind", "name"), param("row", "name")]); g.n("tmrg_c", "call_self", function="Manage Row Group", inp={"kind": "@tmrg.kind", "row": "@tmrg.row"})
    g.set("tmrg_s", "TmpName", inp={"TmpName": "@tmrg_c.group"}); g.chain("tmrg", "tmrg_c", "tmrg_s")
    g.custom("tmgs", "Test Manage Groups"); g.n("tmgs_c", "call_self", function="Manage Groups"); g.set("tmgs_s", "TmpNames", inp={"TmpNames": "@tmgs_c.groups"}); g.chain("tmgs", "tmgs_c", "tmgs_s")
    g.custom("tclp", "Test Clear Presets"); tclp_pd = presets_data(g, "tclp_pd"); g.call("tclp_c", K_ARR, "Array_Clear", inp={"TargetArray": tclp_pd}); g.chain("tclp", "tclp_c")
    g.custom("trmp", "Test Remove Preset", [param("index", "int")]); trmp_pd = presets_data(g, "trmp_pd"); g.call("trmp_c", K_ARR, "Array_Remove", inp={"TargetArray": trmp_pd, "IndexToRemove": "@trmp.index"}); g.chain("trmp", "trmp_c")
    g.custom("tpsn", "Test Preset Shown Name", [param("index", "int")]); g.n("tpsn_c", "call_self", function="Preset Shown Name", inp={"index": "@tpsn.index"})
    g.set("tpsn_s", "TmpStr3", inp={"TmpStr3": "@tpsn_c.s"}); g.chain("tpsn", "tpsn_s")
    g.custom("tldp", "Test Load Presets"); g.n("tldp_l", "call_self", function="Load Presets"); g.chain("tldp", "tldp_l")
    g.custom("tbs", "Test Body Scales", [param("name", "name")]); g.n("tbs_f", "call_self", function="Body Scale Factors", inp={"name": "@tbs.name"})
    g.set("tbs_s", "TmpFloats", inp={"TmpFloats": "@tbs_f.factors"}); g.chain("tbs", "tbs_f", "tbs_s")
    g.custom("tvo", "Test Vector Or One", [param("v", "struct:/Script/CoreUObject.Vector")]); g.n("tvo_c", "call_self", function="Vector Or One", inp={"v": "@tvo.v"}); g.set("tvo_s", "TmpVector", inp={"TmpVector": "@tvo_c.out"}); g.chain("tvo", "tvo_s")
    g.custom("tbss", "Test Set Body Scales", [param("name", "name"), param("factors", "float", "array")]); g.make("tbss_mk", S_FLOATS, Values="@tbss.factors")
    g.get("tbss_g", "BodyScales"); g.call("tbss_a", K_MAP, "Map_Add", inp={"TargetMap": "@tbss_g.BodyScales", "Key": "@tbss.name", "Value": "@tbss_mk.S_Floats"}); g.chain("tbss", "tbss_a")
    g.custom("tgt", "Test Go To", [param("name", "name"), param("slot", "name")]); g.set("tgt_s", "ContextSlot", inp={"ContextSlot": "@tgt.slot"})
    g.n("tgt_g", "call_self", function="Go To Item", inp={"name": "@tgt.name"}); g.chain("tgt", "tgt_s", "tgt_g")
    # EndPlay: take AltUI's modifier off the camera manager again. Both usually die together with the level; this covers the
    # case where only the manager goes (a second one would otherwise find a leftover modifier it no longer feeds).
    g.event("ep", E_ACTOR, "ReceiveEndPlay")
    g.get("epm", "CamMod"); g.call("epv", K_SYS, "IsValid", inp={"Object": "@epm.CamMod"})
    g.get("eppc", "PC"); g.get("epmgr", "PlayerCameraManager", cls=E_PC); g.link("eppc.PC", "epmgr.self")
    g.call("epv2", K_SYS, "IsValid", inp={"Object": "@epmgr.PlayerCameraManager"})
    g.call("epand", K_MATH, "BooleanAND", inp={"A": "@epv.ReturnValue", "B": "@epv2.ReturnValue"}); g.branch("epb", "@epand.ReturnValue")
    g.call("epr", E_PCM, "RemoveCameraModifier", inp={"self": "@epmgr.PlayerCameraManager", "ModifierToRemove": "@epm.CamMod"})
    g.chain("ep", "epb", "epr")
    # a deferred Save Settings still pending (slider let go less than SETTINGS_SAVE_DELAY before the level ends): save now
    g.get("epst", "SettingsSaveTimer"); g.call("epsg", K_MATH, "Greater_FloatFloat", inp={"A": "@epst.SettingsSaveTimer", "B": "0.0"}); g.branch("epsb", "@epsg.ReturnValue")
    g.n("epsv", "call_self", function="Save Settings"); g.chain("epb:else", "epsb"); g.chain("epr", "epsb"); g.chain("epsb", "epsv")
    return g


# ---------------- Quick menu (docs/specs/2026-10-03-quick-menu-design.md) ----------------
# Items are strings "<kind>:<id>" (fixed ones without id); QuickItems = the wheel in order, QuickKey = the key held to open it.
QUICK_MAX = 32          # sectors at most
QUICK_INNER = 0.36      # dead zone / dark centre, share of the wheel radius (= Inner of M_QuickSector)
QUICK_FIXED = ["freecam", "photo", "panel", "posestop"]
QUICK_FIXED_TEXT = {"freecam": "Quick_FreeCam", "photo": "Quick_Photo", "panel": "Quick_Panel", "posestop": "Quick_PoseStop"}
QUICK_MOD_KINDS = ["modfield", "modaction"]   # a mod's Button / Toggle field, a row of its AltUI_Actions


def quick_run_mod(g, br, id_pin):
    """Run branches of the mod kinds: On AltUI Changed(Key, 1) on the mod's actor; a toggle flips (1 - Get AltUI Value). No actor: nothing."""
    g.n("qma", "call_self", function="Quick Mod Actor", inp={"item": "@entry.item"}); g.call("qmv", K_SYS, "IsValid", inp={"Object": "@qma.actor"}); g.branch("qmb", "@qmv.ReturnValue")
    g.get("qgt", "QModToggle"); g.branch("qbt", "@qgt.QModToggle")
    g.get("qgk", "QModKey"); g.n("qgv", "message", cls=mu.INTERFACE, function=mu.GET_VALUE, inp={"self": "@qma.actor", "Key": "@qgk.QModKey"})
    g.call("qfl", K_MATH, "Subtract_FloatFloat", inp={"A": "1.0", "B": "@qgv.Value"}); g.call("qnv", K_MATH, "SelectFloat", inp={"A": "@qfl.ReturnValue", "B": "1.0", "bPickA": "@qgt.QModToggle"})
    g.get("qgk2", "QModKey"); g.n("qoc", "message", cls=mu.INTERFACE, function=mu.ON_CHANGED, inp={"self": "@qma.actor", "Key": "@qgk2.QModKey", "Value": "@qnv.ReturnValue"})
    for k in QUICK_MOD_KINDS: g.chain(br[k], "qma", "qmb")
    g.chain("qmb", "qbt", "qgv", "qoc"); g.chain("qbt:else", "qoc")


QUICK_FIXED_ICON = {"freecam": M + "/T_Cam", "photo": M + "/T_Photo", "panel": T_ALTUI, "posestop": M + "/T_Pose"}


def f_quick_sector_at():
    """Sector under the offset (dx, dy) from the wheel centre (y down): -1 inside the dead zone or without sectors; sector 0 is centred at
    the top, clockwise - the same formula as M_QuickSector."""
    g = G()
    g.call("xx", K_MATH, "Multiply_FloatFloat", inp={"A": "@entry.dx", "B": "@entry.dx"}); g.call("yy", K_MATH, "Multiply_FloatFloat", inp={"A": "@entry.dy", "B": "@entry.dy"})
    g.call("d2", K_MATH, "Add_FloatFloat", inp={"A": "@xx.ReturnValue", "B": "@yy.ReturnValue"}); g.call("d", K_MATH, "Sqrt", inp={"A": "@d2.ReturnValue"})
    g.call("ir", K_MATH, "Multiply_FloatFloat", inp={"A": "@entry.radius", "B": str(QUICK_INNER)}); g.call("in", K_MATH, "Less_FloatFloat", inp={"A": "@d.ReturnValue", "B": "@ir.ReturnValue"})
    g.call("z", K_MATH, "LessEqual_IntInt", inp={"A": "@entry.count", "B": "0"}); g.call("no", K_MATH, "BooleanOR", inp={"A": "@in.ReturnValue", "B": "@z.ReturnValue"})
    g.call("c1", K_MATH, "Max", inp={"A": "@entry.count", "B": "1"}); g.call("cf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@c1.ReturnValue"})
    g.call("ny", K_MATH, "Multiply_FloatFloat", inp={"A": "@entry.dy", "B": "-1.0"}); g.call("deg", K_MATH, "DegAtan2", inp={"Y": "@entry.dx", "X": "@ny.ReturnValue"})
    g.call("a", K_MATH, "Divide_FloatFloat", inp={"A": "@deg.ReturnValue", "B": "360.0"}); g.call("h", K_MATH, "Divide_FloatFloat", inp={"A": "0.5", "B": "@cf.ReturnValue"})
    g.call("a1", K_MATH, "Add_FloatFloat", inp={"A": "@a.ReturnValue", "B": "1.0"}); g.call("a2", K_MATH, "Add_FloatFloat", inp={"A": "@a1.ReturnValue", "B": "@h.ReturnValue"})
    g.call("fr", K_MATH, "Fraction", inp={"A": "@a2.ReturnValue"}); g.call("s", K_MATH, "Multiply_FloatFloat", inp={"A": "@fr.ReturnValue", "B": "@cf.ReturnValue"})
    g.call("fl", K_MATH, "FFloor", inp={"A": "@s.ReturnValue"})
    g.call("cm", K_MATH, "Subtract_IntInt", inp={"A": "@c1.ReturnValue", "B": "1"}); g.call("cl2", K_MATH, "Min", inp={"A": "@fl.ReturnValue", "B": "@cm.ReturnValue"})   # float rounding at the last edge
    g.call("r", K_MATH, "SelectInt", inp={"A": "-1", "B": "@cl2.ReturnValue", "bPickA": "@no.ReturnValue"}); g.link("r.ReturnValue", "return.index"); g.chain("entry", "return")
    return fn("Quick Sector At", [param("dx", "float"), param("dy", "float"), param("radius", "float"), param("count", "int")], [param("index", "int")], graph=g, pure=True)


def f_quick_item_kind():
    """"look:12" -> kind "look", id "12"; "freecam" -> kind "freecam", id ""."""
    g = G(); g.call("sp", K_STR, "Split", inp={"SourceString": "@entry.item", "InStr": ":", "SearchCase": "CaseSensitive", "SearchDir": "FromStart"})
    g.call("k", K_MATH, "SelectString", inp={"A": "@sp.LeftS", "B": "@entry.item", "bPickA": "@sp.ReturnValue"})
    g.call("i", K_MATH, "SelectString", inp={"A": "@sp.RightS", "B": "", "bPickA": "@sp.ReturnValue"})
    g.link("k.ReturnValue", "return.kind"); g.link("i.ReturnValue", "return.id"); g.chain("entry", "return")
    return fn("Quick Item Kind", [param("item", "string")], [param("kind", "string"), param("id", "string")], graph=g, pure=True)


def quick_kind_branches(g, p, kinds, kind_pin):
    """Branch chain over kinds: returns {kind: branch id} (true = this kind) and the id of the last else-exit."""
    out = {}; prev = None
    for k in kinds:
        g.call(p + "e_" + k, K_STR, "EqualEqual_StrStr", inp={"A": kind_pin, "B": k}); g.branch(p + "b_" + k, "@%se_%s.ReturnValue" % (p, k))
        if prev: g.chain(prev, p + "b_" + k)
        out[k] = p + "b_" + k; prev = p + "b_" + k + ":else"
    return out, prev


def f_quick_find():
    """Does the item's target exist, and at which index (outfit / look / face / preset; -1 otherwise)? Fixed items always exist."""
    g = G(); g.n("k", "call_self", function="Quick Item Kind", inp={"item": "@entry.item"})
    g.set("s0", "QOk", inp={"QOk": "false"}); g.set("s1", "QIdx", inp={"QIdx": "-1"}); g.chain("entry", "s0", "s1")
    br, last = quick_kind_branches(g, "q", QUICK_FIXED + ["tab", "pose", "modentry", "outfit", "look", "face", "preset"] + QUICK_MOD_KINDS, "@k.kind")
    g.chain("s1", br[QUICK_FIXED[0]])
    g.n("mi", "call_self", function="Quick Mod Info", inp={"item": "@entry.item"}); g.set("smo", "QOk", inp={"QOk": "@mi.ok"})
    for k in QUICK_MOD_KINDS: g.chain(br[k], "mi", "smo", "return")
    g.set("ok", "QOk", inp={"QOk": "true"}); g.chain("ok", "return")
    for k in QUICK_FIXED: g.chain(br[k], "ok")
    # tab: one of TOP_TABS
    expr = None
    for i, page in enumerate(TOP_TABS):
        g.call("te%d" % i, K_STR, "EqualEqual_StrStr", inp={"A": "@k.id", "B": page}); e = "@te%d.ReturnValue" % i
        if expr: g.call("to%d" % i, K_MATH, "BooleanOR", inp={"A": expr, "B": e}); expr = "@to%d.ReturnValue" % i
        else: expr = e
    g.set("tok", "QOk", inp={"QOk": expr}); g.chain(br["tab"], "tok", "return")
    g.call("pn", K_STR, "Conv_StringToName", inp={"InString": "@k.id"})
    g.call("pe", K_DT, "DoesDataTableRowExist", inp={"Table": P_ANIM_T, "RowName": "@pn.ReturnValue"}); g.set("pok", "QOk", inp={"QOk": "@pe.ReturnValue"}); g.chain(br["pose"], "pe", "pok", "return")
    g.get("gme", "ModEntries"); g.call("mc", K_MAP, "Map_Contains", inp={"TargetMap": "@gme.ModEntries", "Key": "@pn.ReturnValue"}); g.set("mok", "QOk", inp={"QOk": "@mc.ReturnValue"}); g.chain(br["modentry"], "mok", "return")
    # outfit: the index whose content key is the id
    g.get("go", "Outfits"); g.call("ov", K_SYS, "IsValid", inp={"Object": "@go.Outfits"}); g.branch("bov", "@ov.ReturnValue"); g.chain(br["outfit"], "bov"); g.chain("bov:else", "return")
    g.get("go2", "Outfits"); g.get("goa", "outfits", cls=P_OUTFITS); g.link("go2.Outfits", "goa.self"); g.foreach("fo", "@goa.outfits")
    g.n("okey", "call_self", function="Outfit Key", inp={"index": "@fo.Array Index"}); g.call("oeq", K_STR, "EqualEqual_StrStr", inp={"A": "@okey.key", "B": "@k.id"}); g.branch("boe", "@oeq.ReturnValue")
    g.set("oo", "QOk", inp={"QOk": "true"}); g.set("oi", "QIdx", inp={"QIdx": "@fo.Array Index"})
    g.chain("bov", "fo"); g.chain("fo", "okey", "boe", "oo", "oi"); g.chain("fo:Completed", "return")
    # look / face / preset: the index whose Id (IconNumber) is the id
    g.call("idn", K_STR, "Conv_StringToInt", inp={"InString": "@k.id"})
    for kind, arr_fn, struct, field, ensure in (("look", looks_array, S_LOOK, "Id", ensure_looks), ("face", faces_array, fc.S_FACE, "Id", ensure_faces),
                                                ("preset", presets_data, P_PRESET_S, "IconNumber", None)):
        p = kind + "_fx"
        if ensure:
            head, tails = ensure(g)
            g.chain(br[kind], *head)
            for t in tails: g.chain(t, p + "fe")
        else:
            g.get(p + "gp", "Presets"); g.call(p + "pv", K_SYS, "IsValid", inp={"Object": "@%sgp.Presets" % p}); g.branch(p + "bp", "@%spv.ReturnValue" % p)
            g.chain(br[kind], p + "bp", p + "fe"); g.chain(p + "bp:else", "return")
        g.foreach(p + "fe", arr_fn(g, p + "arr")); g.brk(p + "br", struct, "@%sfe.Array Element" % p)
        g.call(p + "eq", K_MATH, "EqualEqual_IntInt", inp={"A": "@%sbr.%s" % (p, field), "B": "@idn.ReturnValue"}); g.branch(p + "b", "@%seq.ReturnValue" % p)
        g.set(p + "o", "QOk", inp={"QOk": "true"}); g.set(p + "i", "QIdx", inp={"QIdx": "@%sfe.Array Index" % p})
        g.chain(p + "fe", p + "b", p + "o", p + "i"); g.chain(p + "fe:Completed", "return")
    g.chain(last, "return")
    g.get("rok", "QOk"); g.get("rix", "QIdx"); g.link("rok.QOk", "return.ok"); g.link("rix.QIdx", "return.index")
    return fn("Quick Find", [param("item", "string")], [param("ok", "bool"), param("index", "int")], graph=g)


def f_quick_item_caption():
    """Display name of an item (the full name: the wheel centre shows it, the options list too)."""
    g = G(); g.n("k", "call_self", function="Quick Item Kind", inp={"item": "@entry.item"}); g.n("f", "call_self", function="Quick Find", inp={"item": "@entry.item"})
    g.set("s0", "QStr", inp={"QStr": "@entry.item"}); g.chain("entry", "f", "s0")
    br, last = quick_kind_branches(g, "q", QUICK_FIXED + ["tab", "pose", "modentry", "outfit", "look", "face", "preset"] + QUICK_MOD_KINDS, "@k.kind"); g.chain("s0", br[QUICK_FIXED[0]])
    g.n("mi", "call_self", function="Quick Mod Info", inp={"item": "@entry.item"}); g.set("smc", "QStr", inp={"QStr": "@mi.caption"})
    for k in QUICK_MOD_KINDS: g.chain(br[k], "mi", "smc", "return")
    for k in QUICK_FIXED:
        g.set("sf_" + k, "QStr", inp={"QStr": ts(g, "tf_" + k, QUICK_FIXED_TEXT[k])}); g.chain(br[k], "sf_" + k, "return")
    g.call("pn", K_STR, "Conv_StringToName", inp={"InString": "@k.id"})
    g.call("tk", K_TXT, "Conv_TextToString", inp={"InText": key_text(g, "tkt", "Tab_", "@pn.ReturnValue")}); g.set("st", "QStr", inp={"QStr": "@tk.ReturnValue"}); g.chain(br["tab"], "st", "return")
    g.n("pt", "call_self", function="Pose Title", inp={"row": "@pn.ReturnValue"}); g.set("sp", "QStr", inp={"QStr": "@pt.title"}); g.chain(br["pose"], "pt", "sp", "return")
    g.get("gme", "ModEntries"); g.call("mf", K_MAP, "Map_Find", inp={"TargetMap": "@gme.ModEntries", "Key": "@pn.ReturnValue"}); g.brk("mb", mu.ENTRY_STRUCT, "@mf.Value")
    g.call("mt", K_TXT, "Conv_TextToString", inp={"InText": "@mb.Caption"}); g.set("sm", "QStr", inp={"QStr": "@mt.ReturnValue"}); g.chain(br["modentry"], "sm", "return")
    # outfit: its own name, else "Outfit <n>"
    g.branch("bfo", "@f.ok"); g.chain(br["outfit"], "bfo"); g.chain("bfo:else", "return")
    g.n("on", "call_self", function="Outfit Name", inp={"index": "@f.index"}); g.call("oe", K_STR, "IsEmpty", inp={"InString": "@on.name"})
    g.call("o1", K_MATH, "Add_IntInt", inp={"A": "@f.index", "B": "1"}); g.call("o1s", K_STR, "Conv_IntToString", inp={"InInt": "@o1.ReturnValue"})
    g.call("oc", K_STR, "Concat_StrStr", inp={"A": ts(g, "tou", "Quick_Outfit"), "B": " "}); g.call("oc2", K_STR, "Concat_StrStr", inp={"A": "@oc.ReturnValue", "B": "@o1s.ReturnValue"})
    g.set("so", "QStr", inp={"QStr": "@on.name"}); g.branch("boe", "@oe.ReturnValue"); g.set("so2", "QStr", inp={"QStr": "@oc2.ReturnValue"})
    g.chain("bfo", "on", "so", "boe", "so2", "return"); g.chain("boe:else", "return")
    for kind, arr_fn, struct in (("look", looks_array, S_LOOK), ("face", faces_array, fc.S_FACE)):
        p = kind + "_cp"; g.branch(p + "b", "@f.ok"); g.chain(br[kind], p + "b"); g.chain(p + "b:else", "return")
        g.call(p + "g", K_ARR, "Array_Get", inp={"TargetArray": arr_fn(g, p + "arr"), "Index": "@f.index"}); g.brk(p + "br", struct, "@%sg.Item" % p)
        g.set(p + "s", "QStr", inp={"QStr": "@%sbr.Name" % p}); g.chain(p + "b", p + "s", "return")
    g.call("pc", K_STR, "Concat_StrStr", inp={"A": ts(g, "tpr", "Quick_Preset"), "B": " "}); g.call("pc2", K_STR, "Concat_StrStr", inp={"A": "@pc.ReturnValue", "B": "@k.id"})
    g.call("pid", K_STR, "Conv_StringToName", inp={"InString": "@k.id"}); g.n("psn", "call_self", function="Shown Name", inp={"kind": "preset", "row": "@pid.ReturnValue", "default": "@pc2.ReturnValue"})   # its custom name (stored under the icon number, = the item's id)
    g.set("spr", "QStr", inp={"QStr": "@psn.name"}); g.chain(br["preset"], "spr", "return")
    g.chain(last, "return")
    g.get("gs", "QStr"); g.call("t", K_TXT, "Conv_StringToText", inp={"InString": "@gs.QStr"}); g.link("t.ReturnValue", "return.caption")
    return fn("Quick Item Caption", [param("item", "string")], [param("caption", "text")], graph=g)


def f_quick_item_icon():
    """Icon of an item: photos of outfits (first piece) / looks / faces / presets, the camera / photo / panel / pose symbols, a tab's icon;
    None = text only."""
    g = G(); g.n("k", "call_self", function="Quick Item Kind", inp={"item": "@entry.item"}); g.n("f", "call_self", function="Quick Find", inp={"item": "@entry.item"})
    g.set("s0", "QTex", inp={"QTex": "None"}); g.chain("entry", "f", "s0")
    kinds = list(QUICK_FIXED_ICON) + ["tab", "pose", "outfit", "look", "face", "preset"] + QUICK_MOD_KINDS
    br, last = quick_kind_branches(g, "q", kinds, "@k.kind"); g.chain("s0", br[kinds[0]])
    for k, tex in list(QUICK_FIXED_ICON.items()) + [("pose", M + "/T_Pose")]:
        g.set("si_" + k, "QTex", inp={"QTex": tex}); g.chain(br[k], "si_" + k, "return")
    tb, tlast = quick_kind_branches(g, "tp", TOP_TABS, "@k.id"); g.chain(br["tab"], tb[TOP_TABS[0]]); g.chain(tlast, "return")
    for page in TOP_TABS: g.set("st_" + page, "QTex", inp={"QTex": TAB_ICONS[page]}); g.chain(tb[page], "st_" + page, "return")
    g.n("mi", "call_self", function="Quick Mod Info", inp={"item": "@entry.item"}); g.get("gmi", "QModIcon")
    g.call("mld", K_SYS, "LoadAsset_Blocking", inp={"Asset": "@gmi.QModIcon"}); g.cast("mct", E_TEX2D, "@mld.ReturnValue", pure=False, miss="ignore")
    g.set("smi", "QTex", inp={"QTex": "@mct.AsTexture2D"})
    for k in QUICK_MOD_KINDS: g.chain(br[k], "mi", "mld", "mct", "smi", "return")
    g.chain("mct:CastFailed", "return")
    g.call("idn", K_STR, "Conv_StringToInt", inp={"InString": "@k.id"})
    for kind, fn_name in (("look", "Look Icon"), ("face", "Face Icon"), ("preset", "Preset Icon")):
        p = kind + "_ic"; g.n(p, "call_self", function=fn_name, inp={("number" if kind == "preset" else "id"): "@idn.ReturnValue"})
        g.set(p + "s", "QTex", inp={"QTex": "@%s.tex" % p}); g.branch(p + "b", "@f.ok"); g.chain(br[kind], p + "b", p, p + "s", "return"); g.chain(p + "b:else", "return")
    # outfit: the icon of its first piece that has one (like the outfit tiles) - the very first piece may have none or be gone from
    # the catalog, and then outfits with only a few pieces showed no picture at all (game test 2026-10-04)
    g.branch("bfo", "@f.ok"); g.chain(br["outfit"], "bfo"); g.chain("bfo:else", "return")
    g.get("go", "Outfits"); g.get("goa", "outfits", cls=P_OUTFITS); g.link("go.Outfits", "goa.self")
    g.call("og", K_ARR, "Array_Get", inp={"TargetArray": "@goa.outfits", "Index": "@f.index"}); g.brk("ob", P_OUTFIT_S, "@og.Item")
    g.call("keys", K_MAP, "Map_Keys", inp={"TargetMap": "@ob." + OUTFIT_MEMBER}); g.set("sk", "QNames", inp={"QNames": "@keys.Keys"})   # typed first: Array_* on Map_Keys' wildcard output does not resolve
    g.get("gk", "QNames"); g.foreach("fk", "@gk.QNames")
    g.get("gqt", "QTex"); g.call("hv", K_SYS, "IsValid", inp={"Object": "@gqt.QTex"}); g.call("nhv", K_MATH, "Not_PreBool", inp={"A": "@hv.ReturnValue"}); g.branch("bk", "@nhv.ReturnValue")
    g.n("fi", "call_self", function="Find Item", inp={"name": "@fk.Array Element"}); g.brk("bi", S_ITEM, "@fi.item")
    g.set("so", "QTex", inp={"QTex": "@bi.Icon"}); g.chain("bfo", "keys", "sk", "fk"); g.chain("fk", "bk", "fi", "so"); g.chain("fk:Completed", "return")
    g.chain(last, "return")
    g.get("gt", "QTex"); g.link("gt.QTex", "return.tex")
    return fn("Quick Item Icon", [param("item", "string")], [param("tex", "object:" + E_TEX2D)], graph=g)


def f_run_quick_item():
    """Run a wheel item (the wheel is closed already): like the click on its tile / button. A missing target does nothing."""
    g = G(); g.n("k", "call_self", function="Quick Item Kind", inp={"item": "@entry.item"}); g.n("f", "call_self", function="Quick Find", inp={"item": "@entry.item"})
    g.branch("bok", "@f.ok"); g.chain("entry", "f", "bok")
    kinds = QUICK_FIXED + ["tab", "pose", "modentry", "outfit", "look", "face", "preset"] + QUICK_MOD_KINDS
    br, last = quick_kind_branches(g, "q", kinds, "@k.kind"); g.chain("bok", br[kinds[0]])
    def op(id): g.n(id, "call_self", function="Open Panel"); return id
    g.n("sfc", "call_self", function="Start Free Cam"); g.chain(br["freecam"], op("op1"), "sfc")
    g.n("spm", "call_self", function="Start Photo Mode"); g.chain(br["photo"], op("op2"), "spm")
    g.chain(br["panel"], op("op3"))
    g.n("stp", "call_self", function="Stop Pose"); g.chain(br["posestop"], "stp")
    g.call("pn", K_STR, "Conv_StringToName", inp={"InString": "@k.id"})
    g.n("spg", "call_self", function="Select Page", inp={"name": "@pn.ReturnValue"}); g.chain(br["tab"], op("op4"), "spg")   # a jump: a switched-off tab shows while it is open
    g.n("pcl", "call_self", function="Pose Clicked", inp={"name": "@pn.ReturnValue"}); g.chain(br["pose"], "pcl")
    g.n("spm2", "call_self", function="Select Page", inp={"name": "Mods"}); g.n("sme", "call_self", function="Select Mod Entry", inp={"name": "@pn.ReturnValue"})
    g.chain(br["modentry"], op("op5"), "spm2", "sme")
    g.n("ooc", "call_self", function="On Outfit Clicked", inp={"index": "@f.index"}); g.chain(br["outfit"], "ooc")
    g.n("alk", "call_self", function="Apply Look", inp={"index": "@f.index"}); g.chain(br["look"], "alk")
    g.n("ofc", "call_self", function="On Face Clicked", inp={"index": "@f.index"}); g.chain(br["face"], "ofc")
    g.n("prc", "call_self", function="Preset Clicked", inp={"index": "@f.index"}); g.chain(br["preset"], "prc")
    quick_run_mod(g, br, "@k.id")
    return fn("Run Quick Item", [param("item", "string")], graph=g)


W_QUICK = M + "/W_QuickWheel"; W_QSECTOR = M + "/W_QuickSector"


def f_open_quick_wheel():
    """Quick key pressed (panel closed, Jodi takes input): the wheel with every item of QuickItems whose target exists (at most
    QUICK_MAX), mouse cursor in its centre, input to the wheel, Jodi locked like with the panel."""
    g = G(); tail = ["entry"]
    g.n("lo", "call_self", function="Load Outfits"); g.n("lp", "call_self", function="Load Presets"); tail += ["lo", "lp"]   # the panel reloads them on open, too
    g.get("gsh", "QuickShown"); g.call("csh", K_ARR, "Array_Clear", inp={"TargetArray": "@gsh.QuickShown"}); tail.append("csh")
    g.get("gqi", "QuickItems"); g.set("sq", "QItemsLoop", inp={"QItemsLoop": "@gqi.QuickItems"}); tail.append("sq")   # frozen copy of its own: Quick Find -> Outfit Key -> Join Names refills TmpStrings
    g.get("gts", "QItemsLoop"); g.foreach("fe", "@gts.QItemsLoop"); tail.append("fe")
    g.n("f", "call_self", function="Quick Find", inp={"item": "@fe.Array Element"})
    g.get("gsh2", "QuickShown"); g.call("sl", K_ARR, "Array_Length", inp={"TargetArray": "@gsh2.QuickShown"}); g.call("room", K_MATH, "Less_IntInt", inp={"A": "@sl.ReturnValue", "B": str(QUICK_MAX)})
    g.call("ok", K_MATH, "BooleanAND", inp={"A": "@f.ok", "B": "@room.ReturnValue"}); g.branch("bok", "@ok.ReturnValue")
    g.get("gsh3", "QuickShown"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gsh3.QuickShown", "NewItem": "@fe.Array Element"})
    g.chain("fe", "f", "bok", "add")
    ww = create_widget(g, "cw", W_QUICK); g.set("sw", "QuickWheel", inp={"QuickWheel": ww}); set_manager(g, "smw", W_QUICK, "@sw.Output_Get")
    g.get("gw0", "QuickWheel"); g.call("icn", W_QUICK, "Init Center", inp={"self": "@gw0.QuickWheel"})
    g.get("gsc", "QuickSectors"); g.call("csc", K_ARR, "Array_Clear", inp={"TargetArray": "@gsc.QuickSectors"})
    g.chain("fe:Completed", "cw_cr", "sw", "smw", "icn", "csc", "fs")
    g.get("gsh4", "QuickShown"); g.foreach("fs", "@gsh4.QuickShown")
    sw_ = create_widget(g, "cs", W_QSECTOR); set_manager(g, "sms", W_QSECTOR, sw_)
    g.n("cap", "call_self", function="Quick Item Caption", inp={"item": "@fs.Array Element"}); g.n("ico", "call_self", function="Quick Item Icon", inp={"item": "@fs.Array Element"})
    g.n("live", "call_self", function="Quick Item Live", inp={"item": "@fs.Array Element"})
    g.get("gsh5", "QuickShown"); g.call("cnt", K_ARR, "Array_Length", inp={"TargetArray": "@gsh5.QuickShown"})
    g.call("si", W_QSECTOR, "Init", inp={"self": sw_, "index": "@fs.Array Index", "count": "@cnt.ReturnValue", "caption": "@cap.caption", "icon": "@ico.tex", "valid": "@live.yes"})
    g.get("gw1", "QuickWheel"); g.call("as", W_QUICK, "Add Sector", inp={"self": "@gw1.QuickWheel", "widget": sw_})
    g.get("gsc2", "QuickSectors"); g.call("asc", K_ARR, "Array_Add", inp={"TargetArray": "@gsc2.QuickSectors", "NewItem": sw_})
    g.chain("fs", "cs_cr", "sms", "cap", "ico", "live", "si", "as", "asc")
    # empty wheel: the hint in the centre; else nothing until the mouse points at a sector
    g.get("gsh6", "QuickShown"); g.call("n0", K_ARR, "Array_Length", inp={"TargetArray": "@gsh6.QuickShown"}); g.call("emp", K_MATH, "EqualEqual_IntInt", inp={"A": "@n0.ReturnValue", "B": "0"})
    g.call("ct", K_MATH, "SelectString", inp={"A": ts(g, "tem", "Lbl_QuickEmpty"), "B": "", "bPickA": "@emp.ReturnValue"})
    g.call("ctt", K_TXT, "Conv_StringToText", inp={"InString": "@ct.ReturnValue"})
    g.get("gw2", "QuickWheel"); g.call("scn", W_QUICK, "Set Center", inp={"self": "@gw2.QuickWheel", "text": "@ctt.ReturnValue"})
    g.set("smk", "QuickMarked", inp={"QuickMarked": "-1"}); g.set("sop", "QuickOpen", inp={"QuickOpen": "true"})
    g.get("gw3", "QuickWheel"); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@gw3.QuickWheel", "ZOrder": "110"})
    g.get("gpc", "PC"); g.call("cur", P_PC, "ShowMouseCursor", inp={"self": "@gpc.PC", "show": "true"})
    g.get("gpc2", "PC"); g.get("gw4", "QuickWheel"); g.call("im", K_WBL, "SetInputMode_UIOnlyEx", inp={"PlayerController": "@gpc2.PC", "InWidgetToFocus": "@gw4.QuickWheel", "InMouseLockMode": "DoNotLock"})
    g.call("vp", "/Script/UMG.WidgetLayoutLibrary", "GetViewportSize"); g.call("bvp", K_MATH, "BreakVector2D", inp={"InVec": "@vp.ReturnValue"})
    g.call("mx", K_MATH, "Multiply_FloatFloat", inp={"A": "@bvp.X", "B": "0.5"}); g.call("my", K_MATH, "Multiply_FloatFloat", inp={"A": "@bvp.Y", "B": "0.5"})
    g.call("mxi", K_MATH, "FTrunc", inp={"A": "@mx.ReturnValue"}); g.call("myi", K_MATH, "FTrunc", inp={"A": "@my.ReturnValue"})
    g.get("gpc3", "PC"); g.call("sml", E_PC, "SetMouseLocation", inp={"self": "@gpc3.PC", "X": "@mxi.ReturnValue", "Y": "@myi.ReturnValue"})
    g.n("lk", "call_self", function="Quick Lock", inp={"on": "true"})
    g.chain("fs:Completed", "scn", "smk", "sop", "atv", "cur", "im", "sml", "lk")
    g.chain(*tail); return fn("Open Quick Wheel", graph=g)


def f_quick_lock():
    """Jodi's input while the wheel is open: off / back on (LockStrategy 0, the same as the panel)."""
    g = G(); g.get("gls", "LockStrategy"); g.call("eq0", K_MATH, "EqualEqual_IntInt", inp={"A": "@gls.LockStrategy", "B": "0"}); g.branch("bl", "@eq0.ReturnValue")
    g.branch("bon", "@entry.on")
    g.get("gpc", "PC"); g.call("d1", P_PC, "Enable Player Control", inp={"self": "@gpc.PC", "Base": "false", "Playing": "false"})
    g.get("gpl", "Player"); g.get("gpc2", "PC"); g.call("d2", E_ACTOR, "DisableInput", inp={"self": "@gpl.Player", "PlayerController": "@gpc2.PC"})
    g.get("gpc3", "PC"); g.call("e1", P_PC, "Enable Player Control", inp={"self": "@gpc3.PC", "Base": "true", "Playing": "true"})
    g.get("gpl2", "Player"); g.get("gpc4", "PC"); g.call("e2", E_ACTOR, "EnableInput", inp={"self": "@gpl2.Player", "PlayerController": "@gpc4.PC"})
    g.chain("entry", "bl", "bon", "d1", "d2"); g.chain("bon:else", "e1", "e2")
    return fn("Quick Lock", [param("on", "bool")], graph=g)


def f_quick_hover():
    """Mouse moved over the wheel: mark the sector under it (only when it changes), its full name in the centre."""
    g = G(); g.get("gsh", "QuickShown"); g.call("n", K_ARR, "Array_Length", inp={"TargetArray": "@gsh.QuickShown"})
    g.n("at", "call_self", function="Quick Sector At", inp={"dx": "@entry.dx", "dy": "@entry.dy", "radius": "@entry.radius", "count": "@n.ReturnValue"})
    g.get("gm", "QuickMarked"); g.call("ne", K_MATH, "NotEqual_IntInt", inp={"A": "@at.index", "B": "@gm.QuickMarked"}); g.branch("b", "@ne.ReturnValue")
    g.set("si", "QIdx", inp={"QIdx": "@at.index"})   # frozen: the pure call would be read again after QuickMarked changed
    g.get("gsc", "QuickSectors"); g.get("gm2", "QuickMarked"); g.call("old", K_ARR, "Array_Get", inp={"TargetArray": "@gsc.QuickSectors", "Index": "@gm2.QuickMarked"})
    g.get("gsc0", "QuickSectors"); g.get("gm0", "QuickMarked"); g.call("ovl", K_ARR, "Array_IsValidIndex", inp={"TargetArray": "@gsc0.QuickSectors", "IndexToTest": "@gm0.QuickMarked"}); g.branch("bo", "@ovl.ReturnValue")
    g.call("um", W_QSECTOR, "Set Marked", inp={"self": "@old.Item", "on": "false"})
    g.get("gqi", "QIdx"); g.set("sm", "QuickMarked", inp={"QuickMarked": "@gqi.QIdx"})
    g.get("gsc2", "QuickSectors"); g.get("gm3", "QuickMarked"); g.call("nvl", K_ARR, "Array_IsValidIndex", inp={"TargetArray": "@gsc2.QuickSectors", "IndexToTest": "@gm3.QuickMarked"}); g.branch("bn", "@nvl.ReturnValue")
    g.get("gsc3", "QuickSectors"); g.get("gm4", "QuickMarked"); g.call("new", K_ARR, "Array_Get", inp={"TargetArray": "@gsc3.QuickSectors", "Index": "@gm4.QuickMarked"})
    g.call("mk", W_QSECTOR, "Set Marked", inp={"self": "@new.Item", "on": "true"})
    g.get("gsh2", "QuickShown"); g.get("gm5", "QuickMarked"); g.call("it", K_ARR, "Array_Get", inp={"TargetArray": "@gsh2.QuickShown", "Index": "@gm5.QuickMarked"})
    g.n("cap", "call_self", function="Quick Item Caption", inp={"item": "@it.Item"})
    g.get("gw", "QuickWheel"); g.call("sc", W_QUICK, "Set Center", inp={"self": "@gw.QuickWheel", "text": "@cap.caption"})
    g.call("et", K_TXT, "Conv_StringToText", inp={"InString": ""}); g.get("gw2", "QuickWheel"); g.call("sc0", W_QUICK, "Set Center", inp={"self": "@gw2.QuickWheel", "text": "@et.ReturnValue"})
    g.chain("entry", "b", "si", "bo", "um", "sm"); g.chain("bo:else", "sm"); g.chain("sm", "bn", "mk", "cap", "sc"); g.chain("bn:else", "sc0")
    return fn("Quick Hover", [param("dx", "float"), param("dy", "float"), param("radius", "float")], graph=g)


def f_close_quick_wheel():
    """Wheel away, mouse and input back to the game, Jodi unlocked."""
    g = G(); g.get("gop", "QuickOpen"); g.branch("b", "@gop.QuickOpen"); g.set("so", "QuickOpen", inp={"QuickOpen": "false"})
    g.get("gw", "QuickWheel"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gw.QuickWheel"}); g.branch("bv", "@iv.ReturnValue")
    g.get("gw2", "QuickWheel"); g.call("rm", E_WIDGET, "RemoveFromParent", inp={"self": "@gw2.QuickWheel"})
    g.get("gsc", "QuickSectors"); g.call("csc", K_ARR, "Array_Clear", inp={"TargetArray": "@gsc.QuickSectors"})
    g.get("gpc", "PC"); g.call("cur", P_PC, "ShowMouseCursor", inp={"self": "@gpc.PC", "show": "false"})
    g.get("gpc2", "PC"); g.call("im", K_WBL, "SetInputMode_GameOnly", inp={"PlayerController": "@gpc2.PC"})
    g.n("lk", "call_self", function="Quick Lock", inp={"on": "false"})
    g.chain("entry", "b", "so", "bv", "rm", "csc"); g.chain("bv:else", "csc"); g.chain("csc", "cur", "im", "lk")
    return fn("Close Quick Wheel", graph=g)


def f_quick_release():
    """Quick key released / left click: close the wheel, then run the marked item (if any)."""
    g = G(); g.get("gsh", "QuickShown"); g.get("gm", "QuickMarked"); g.call("vi", K_ARR, "Array_IsValidIndex", inp={"TargetArray": "@gsh.QuickShown", "IndexToTest": "@gm.QuickMarked"})
    g.call("it", K_ARR, "Array_Get", inp={"TargetArray": "@gsh.QuickShown", "Index": "@gm.QuickMarked"})
    g.call("sel", K_MATH, "SelectString", inp={"A": "@it.Item", "B": "", "bPickA": "@vi.ReturnValue"}); g.set("sr", "QRun", inp={"QRun": "@sel.ReturnValue"})
    g.n("cl", "call_self", function="Close Quick Wheel")
    g.get("gr", "QRun"); g.call("em", K_STR, "IsEmpty", inp={"InString": "@gr.QRun"}); g.branch("b", "@em.ReturnValue")
    g.get("gr2", "QRun"); g.n("run", "call_self", function="Run Quick Item", inp={"item": "@gr2.QRun"})
    g.chain("entry", "sr", "cl", "b"); g.chain("b:else", "run")
    return fn("Quick Release", graph=g)


def f_quick_cancel():
    g = G(); g.n("cl", "call_self", function="Close Quick Wheel"); g.chain("entry", "cl"); return fn("Quick Cancel", graph=g)


def f_quick_item_live():
    """Can the item run right now? Mod items need their actor in the level; everything else yes."""
    g = G(); g.n("k", "call_self", function="Quick Item Kind", inp={"item": "@entry.item"})
    g.call("e1", K_STR, "EqualEqual_StrStr", inp={"A": "@k.kind", "B": QUICK_MOD_KINDS[0]}); g.call("e2", K_STR, "EqualEqual_StrStr", inp={"A": "@k.kind", "B": QUICK_MOD_KINDS[1]})
    g.call("om", K_MATH, "BooleanOR", inp={"A": "@e1.ReturnValue", "B": "@e2.ReturnValue"}); g.branch("b", "@om.ReturnValue")
    g.n("a", "call_self", function="Quick Mod Actor", inp={"item": "@entry.item"}); g.call("v", K_SYS, "IsValid", inp={"Object": "@a.actor"}); g.link("v.ReturnValue", "return.yes")
    g.n("r2", "return_new"); g.call("t", K_MATH, "Not_PreBool", inp={"A": "false"}); g.link("t.ReturnValue", "r2.yes")
    g.chain("entry", "b", "a", "return"); g.chain("b:else", "r2")
    return fn("Quick Item Live", [param("item", "string")], [param("yes", "bool")], graph=g)


W_QROW = M + "/W_QuickRow"


def quick_row(g, p, item_pin, mode, add_fn, tail_from, links=False):
    """Nodes for one W_QuickRow (caption, icon, checked = in QuickItems, valid = target exists) added by add_fn; returns the last exec id."""
    rw = create_widget(g, p + "w", W_QROW); set_manager(g, p + "sm", W_QROW, rw)
    g.n(p + "f", "call_self", function="Quick Find", inp={"item": item_pin}); g.n(p + "c", "call_self", function="Quick Item Caption", inp={"item": item_pin})
    g.n(p + "i", "call_self", function="Quick Item Icon", inp={"item": item_pin})
    if not item_pin.startswith("@"): item_pin = g.lit_str(p + "lit", item_pin)   # a literal on a wildcard pin is dropped when the wildcard resolves
    g.get(p + "gq", "QuickItems"); g.call(p + "in", K_ARR, "Array_Contains", inp={"TargetArray": "@%sgq.QuickItems" % p, "ItemToFind": item_pin})
    # zebra stripes like the slot conflicts: QStripe counts the rows of a block (Rebuild Quick Options / quick_head reset it), even rows tinted
    g.get(p + "gsc", "QStripe"); g.call(p + "srm", K_MATH, "Percent_IntInt", inp={"A": "@%sgsc.QStripe" % p, "B": "2"}); g.call(p + "sev", K_MATH, "EqualEqual_IntInt", inp={"A": "@%ssrm.ReturnValue" % p, "B": "0"})
    g.call(p + "sin", K_MATH, "Add_IntInt", inp={"A": "@%sgsc.QStripe" % p, "B": "1"}); g.set(p + "sst", "QStripe", inp={"QStripe": "@%ssin.ReturnValue" % p})
    g.call(p + "init", W_QROW, "Init", inp={"self": rw, "item": item_pin, "caption": "@%sc.caption" % p, "icon": "@%si.tex" % p, "mode": str(mode), "checked": "@%sin.ReturnValue" % p, "valid": "@%sf.ok" % p,
                                         "tinted": "@%ssev.ReturnValue" % p})
    g.get(p + "gp", "Panel"); g.call(p + "ad", W_PANEL, add_fn, inp={"self": "@%sgp.Panel" % p, "widget": rw})
    ids = [p + "w_cr", p + "sm", p + "f", p + "c", p + "i", p + "init", p + "sst"]
    if links:
        for j, (prefix, cap) in enumerate((("QUp:", "↑"), ("QDown:", "↓"), ("QDel:", "✕"))):
            q = "%sl%d" % (p, j); lw = create_widget(g, q + "w", W_TXT); set_manager(g, q + "sm", W_TXT, lw)
            g.call(q + "s", K_STR, "Concat_StrStr", inp={"A": prefix, "B": item_pin}); g.call(q + "n", K_STR, "Conv_StringToName", inp={"InString": "@%ss.ReturnValue" % q})
            g.call(q + "t", K_TXT, "Conv_StringToText", inp={"InString": cap})
            g.call(q + "in", W_TXT, "Init", inp={"self": lw, "action": "@%sn.ReturnValue" % q, "caption": "@%st.ReturnValue" % q})
            g.call(q + "ad", W_QROW, "Add Link", inp={"self": rw, "widget": lw}); ids += [q + "w_cr", q + "sm", q + "in", q + "ad"]
    ids.append(p + "ad"); g.chain(tail_from, *ids); return ids[-1]


def quick_head(g, p, key, tail_from):
    """Group heading row (mode 2) in the available list."""
    rw = create_widget(g, p + "w", W_QROW); set_manager(g, p + "sm", W_QROW, rw)
    g.call(p + "init", W_QROW, "Init", inp={"self": rw, "item": "", "caption": tt(g, p + "t", key), "icon": "None", "mode": "2", "checked": "false", "valid": "true", "tinted": "false"})
    g.get(p + "gp", "Panel"); g.call(p + "ad", W_PANEL, "Add Quick Available", inp={"self": "@%sgp.Panel" % p, "widget": rw})
    g.set(p + "rs", "QStripe", inp={"QStripe": "0"})   # a heading starts the stripes again
    g.chain(tail_from, p + "w_cr", p + "sm", p + "init", p + "ad", p + "rs"); return p + "rs"


def concat_item(g, id, prefix, str_pin):
    g.call(id, K_STR, "Concat_StrStr", inp={"A": prefix, "B": str_pin}); return "@%s.ReturnValue" % id


def f_rebuild_quick_options():
    """Options › Quick menu: the key link (waiting: "Press a key …"), the wheel's items with ↑ ↓ ✕, then every available item by group
    (camera and panel, outfits, looks, faces, presets, favourite poses, tabs, mod entries, mods' actions) with a check box."""
    g = G()
    g.get("gp", "Panel"); g.call("ck", W_PANEL, "Clear Quick Key Links", inp={"self": "@gp.Panel"})
    kw = create_widget(g, "kw", W_TXT); set_manager(g, "ksm", W_TXT, kw)
    g.get("gqk", "QuickKey"); g.call("kqs", K_STR, "Conv_NameToString", inp={"InName": "@gqk.QuickKey"})
    g.get("gqc", "QuickCapture"); g.call("kcap", K_MATH, "SelectString", inp={"A": ts(g, "tkp", "Lbl_KeyPress"), "B": "@kqs.ReturnValue", "bPickA": "@gqc.QuickCapture"})
    g.call("kct", K_TXT, "Conv_StringToText", inp={"InString": "@kcap.ReturnValue"})
    g.call("ki", W_TXT, "Init", inp={"self": kw, "action": "QKey", "caption": "@kct.ReturnValue"})   # it fills the width of "Press a key …"; W_TextButton centres its text
    g.get("gp1", "Panel"); g.call("ka", W_PANEL, "Add Quick Key Link", inp={"self": "@gp1.Panel", "widget": kw})
    g.get("gqh", "QuickKeyHint"); g.get("gp2", "Panel"); g.call("kh", W_PANEL, "Set Quick Key Hint", inp={"self": "@gp2.Panel", "text": "@gqh.QuickKeyHint"})
    g.chain("entry", "ck", "kw_cr", "ksm", "ki", "ka", "kh")
    # in the wheel
    g.get("gp3", "Panel"); g.call("cw", W_PANEL, "Clear Quick In Wheel", inp={"self": "@gp3.Panel"})
    g.get("gqi", "QuickItems"); g.set("sts", "QItemsLoop", inp={"QItemsLoop": "@gqi.QuickItems"}); g.get("gts", "QItemsLoop"); g.foreach("fw", "@gts.QItemsLoop")   # not TmpStrings: Outfit Key refills it
    g.set("rs0", "QStripe", inp={"QStripe": "0"})
    g.chain("kh", "cw", "rs0", "sts", "fw"); quick_row(g, "rw", "@fw.Array Element", 0, "Add Quick In Wheel", "fw", links=True)
    # available
    g.get("gp4", "Panel"); g.call("ca", W_PANEL, "Clear Quick Available", inp={"self": "@gp4.Panel"}); g.chain("fw:Completed", "ca")
    prev = quick_head(g, "hc", "QuickGrp_Camera", "ca")
    for i, k in enumerate(QUICK_FIXED): prev = quick_row(g, "fx%d" % i, k, 1, "Add Quick Available", prev)
    # outfits (content key), looks / faces (Id), presets (IconNumber)
    prev = quick_head(g, "ho", "QuickGrp_Outfits", prev)
    g.get("go", "Outfits"); g.call("ov", K_SYS, "IsValid", inp={"Object": "@go.Outfits"}); g.branch("bov", "@ov.ReturnValue"); g.chain(prev, "bov")
    g.get("go2", "Outfits"); g.get("goa", "outfits", cls=P_OUTFITS); g.link("go2.Outfits", "goa.self"); g.foreach("fo", "@goa.outfits"); g.chain("bov", "fo")
    g.n("ok", "call_self", function="Outfit Key", inp={"index": "@fo.Array Index"}); g.set("so", "QStr2", inp={"QStr2": concat_item(g, "oci", "outfit:", "@ok.key")}); g.chain("fo", "ok", "so")
    g.get("gs2", "QStr2"); quick_row(g, "ro", "@gs2.QStr2", 1, "Add Quick Available", "so")
    g.n("jo", "call_self", function="Quick Noop"); g.chain("fo:Completed", "jo"); g.chain("bov:else", "jo"); prev = "jo"
    for kind, arr_fn, struct, field, ensure, head in (("look", looks_array, S_LOOK, "Id", ensure_looks, "QuickGrp_Looks"), ("face", faces_array, fc.S_FACE, "Id", ensure_faces, "QuickGrp_Faces"),
                                                      ("preset", presets_data, P_PRESET_S, "IconNumber", None, "QuickGrp_Presets")):
        p = kind + "_av"; prev = quick_head(g, p + "h", head, prev)
        if ensure:
            hd, tails = ensure(g); g.chain(prev, *hd)
            for t in tails: g.chain(t, p + "fe")
        else:
            g.get(p + "gp", "Presets"); g.call(p + "pv", K_SYS, "IsValid", inp={"Object": "@%sgp.Presets" % p}); g.branch(p + "bp", "@%spv.ReturnValue" % p)
            g.chain(prev, p + "bp", p + "fe"); g.chain(p + "bp:else", p + "j")
        g.foreach(p + "fe", arr_fn(g, p + "arr")); g.brk(p + "br", struct, "@%sfe.Array Element" % p)
        g.call(p + "is", K_STR, "Conv_IntToString", inp={"InInt": "@%sbr.%s" % (p, field)})
        g.set(p + "s", "QStr2", inp={"QStr2": concat_item(g, p + "ci", kind + ":", "@%sis.ReturnValue" % p)}); g.chain(p + "fe", p + "s")
        g.get(p + "gs", "QStr2"); quick_row(g, p + "r", "@%sgs.QStr2" % p, 1, "Add Quick Available", p + "s")
        g.n(p + "j", "call_self", function="Quick Noop"); g.chain(p + "fe:Completed", p + "j"); prev = p + "j"
    # favourite poses: Favorites holds them as pose:<row> - the same string as the item
    prev = quick_head(g, "hp", "QuickGrp_Poses", prev)
    g.get("gfv", "Favorites"); g.set("sfv", "QLoop", inp={"QLoop": "@gfv.Favorites"}); g.get("gqn", "QLoop"); g.foreach("fp", "@gqn.QLoop"); g.chain(prev, "sfv", "fp")
    # an FName keeps the case of its first use: Favorites holds "Pose:Dance_1" - match without case, the item is pose:<row>
    g.call("pfs", K_STR, "Conv_NameToString", inp={"InName": "@fp.Array Element"}); g.call("pfp", K_STR, "StartsWith", inp={"SourceString": "@pfs.ReturnValue", "InPrefix": "pose:", "SearchCase": "IgnoreCase"})
    g.call("pfr", K_STR, "GetSubstring", inp={"SourceString": "@pfs.ReturnValue", "StartIndex": "5", "Length": "1000"})
    g.branch("bpf", "@pfp.ReturnValue"); g.set("spf", "QStr2", inp={"QStr2": concat_item(g, "pfc", "pose:", "@pfr.ReturnValue")}); g.chain("fp", "bpf", "spf")
    g.get("gs3", "QStr2"); quick_row(g, "rp", "@gs3.QStr2", 1, "Add Quick Available", "spf")
    prev = quick_head(g, "ht", "QuickGrp_Tabs", "fp:Completed")
    for i, page in enumerate(TOP_TABS): prev = quick_row(g, "tb%d" % i, "tab:" + page, 1, "Add Quick Available", prev)
    # mod entries (and, Task 6, the mods' actions)
    g.n("sme", "call_self", function="Scan Mod Entries"); g.get("gmk", "ModEntryKeys"); g.call("mkl", K_ARR, "Array_Length", inp={"TargetArray": "@gmk.ModEntryKeys"})
    g.call("mkg", K_MATH, "Greater_IntInt", inp={"A": "@mkl.ReturnValue", "B": "0"}); g.branch("bmk", "@mkg.ReturnValue"); g.chain(prev, "sme", "bmk")
    prev = quick_head(g, "hm", "QuickGrp_ModEntries", "bmk")
    g.get("gmk2", "ModEntryKeys"); g.set("smk", "QLoop", inp={"QLoop": "@gmk2.ModEntryKeys"}); g.get("gqn2", "QLoop"); g.foreach("fm", "@gqn2.QLoop"); g.chain(prev, "smk", "fm")
    g.call("mks", K_STR, "Conv_NameToString", inp={"InName": "@fm.Array Element"}); g.set("smi", "QStr2", inp={"QStr2": concat_item(g, "mci", "modentry:", "@mks.ReturnValue")}); g.chain("fm", "smi")
    g.get("gs4", "QStr2"); quick_row(g, "rm", "@gs4.QStr2", 1, "Add Quick Available", "smi")
    quick_mod_rows(g, ["fm:Completed", "bmk:else"])
    return fn("Rebuild Quick Options", graph=g)


def quick_mod_rows(g, froms):
    """Available rows of the mods: per entry its Button / Toggle fields, then every row of the mods' AltUI_Actions."""
    g.n("mrh", "call_self", function="Quick Noop")
    for f in froms: g.chain(f, "mrh")
    prev = quick_head(g, "hma", "QuickGrp_ModActions", "mrh")
    g.get("gek", "ModEntryKeys"); g.set("sek", "QLoop", inp={"QLoop": "@gek.ModEntryKeys"}); g.get("gql", "QLoop"); g.foreach("me", "@gql.QLoop"); g.chain(prev, "sek", "me")
    g.get("gmf", "ModFields"); g.call("mff", K_MAP, "Map_Find", inp={"TargetMap": "@gmf.ModFields", "Key": "@me.Array Element"}); g.brk("mfl", mu.LIST_STRUCT, "@mff.Value")
    g.set("smf", "QRowFields", inp={"QRowFields": "@mfl.Fields"}); g.get("gqf", "QRowFields"); g.foreach("mf", "@gqf.QRowFields"); g.brk("mfb", mu.FIELD_STRUCT, "@mf.Array Element")
    g.chain("me", "smf", "mf")
    g.call("mib", K_MATH, "EqualEqual_NameName", inp={"A": "@mfb.Type", "B": "Button"}); g.call("mit", K_MATH, "EqualEqual_NameName", inp={"A": "@mfb.Type", "B": "Toggle"})
    g.call("mio", K_MATH, "BooleanOR", inp={"A": "@mib.ReturnValue", "B": "@mit.ReturnValue"}); g.branch("mbq", "@mio.ReturnValue")
    g.call("mes", K_STR, "Conv_NameToString", inp={"InName": "@me.Array Element"}); g.call("mfks", K_STR, "Conv_NameToString", inp={"InName": "@mfb.Key"})
    g.call("mc1", K_STR, "Concat_StrStr", inp={"A": "modfield:", "B": "@mes.ReturnValue"}); g.call("mc2", K_STR, "Concat_StrStr", inp={"A": "@mc1.ReturnValue", "B": "|"})
    g.call("mc3", K_STR, "Concat_StrStr", inp={"A": "@mc2.ReturnValue", "B": "@mfks.ReturnValue"}); g.set("msi", "QStr2", inp={"QStr2": "@mc3.ReturnValue"})
    g.chain("mf", "mbq", "msi"); g.get("gs5", "QStr2"); quick_row(g, "rmf", "@gs5.QStr2", 1, "Add Quick Available", "msi")
    g.get("gak", "ModActionKeys"); g.set("sak", "QLoop", inp={"QLoop": "@gak.ModActionKeys"}); g.get("gql2", "QLoop"); g.foreach("ma", "@gql2.QLoop"); g.chain("me:Completed", "sak", "ma")
    g.call("mas", K_STR, "Conv_NameToString", inp={"InName": "@ma.Array Element"}); g.set("mai", "QStr2", inp={"QStr2": concat_item(g, "mac", "modaction:", "@mas.ReturnValue")}); g.chain("ma", "mai")
    g.get("gs6", "QStr2"); quick_row(g, "rma", "@gs6.QStr2", 1, "Add Quick Available", "mai")


def f_quick_noop():
    g = G(); g.chain("entry"); return fn("Quick Noop", graph=g)


def f_quick_toggle():
    """Check box of an available row: into the wheel (at the end) / out of it; the lists follow."""
    g = G(); g.get("gq", "QuickItems"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gq.QuickItems", "ItemToFind": "@entry.item"}); g.branch("b", "@has.ReturnValue")
    g.n("rm", "call_self", function="Quick Remove", inp={"item": "@entry.item"}); g.n("ad", "call_self", function="Quick Add", inp={"item": "@entry.item"})
    g.n("rb", "call_self", function="Rebuild Quick Options"); g.chain("entry", "b", "rm", "rb"); g.chain("b:else", "ad", "rb")
    return fn("Quick Toggle", [param("item", "string")], graph=g)


def f_quick_action():
    """Links of the quick menu options: QKey (wait for the next key), QUp:/QDown:/QDel:<item>."""
    g = G(); g.call("s", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"})
    g.call("isk", K_STR, "EqualEqual_StrStr", inp={"A": "@s.ReturnValue", "B": "QKey"}); g.branch("bk", "@isk.ReturnValue")
    g.set("sc", "QuickCapture", inp={"QuickCapture": "true"}); g.call("et", K_TXT, "Conv_StringToText", inp={"InString": ""}); g.set("sh", "QuickKeyHint", inp={"QuickKeyHint": "@et.ReturnValue"})
    g.call("sp", K_STR, "Split", inp={"SourceString": "@s.ReturnValue", "InStr": ":", "SearchCase": "CaseSensitive", "SearchDir": "FromStart"})
    g.call("iu", K_STR, "EqualEqual_StrStr", inp={"A": "@sp.LeftS", "B": "QUp"}); g.branch("bu", "@iu.ReturnValue")
    g.call("idn", K_STR, "EqualEqual_StrStr", inp={"A": "@sp.LeftS", "B": "QDown"}); g.branch("bd", "@idn.ReturnValue")
    g.n("mu", "call_self", function="Quick Move", inp={"item": "@sp.RightS", "delta": "-1"}); g.n("md", "call_self", function="Quick Move", inp={"item": "@sp.RightS", "delta": "1"})
    g.n("rmv", "call_self", function="Quick Remove", inp={"item": "@sp.RightS"}); g.n("rb", "call_self", function="Rebuild Quick Options")
    g.chain("entry", "bk", "sc", "sh", "rb"); g.chain("bk:else", "bu", "mu", "rb"); g.chain("bu:else", "bd", "md", "rb"); g.chain("bd:else", "rmv", "rb")
    return fn("Quick Action", [param("name", "name")], graph=g)


def f_quick_key_captured():
    """The next key for the quick key: its display name (the key events compare names); the panel key is refused with a note."""
    g = G(); g.set("sc", "QuickCapture", inp={"QuickCapture": "false"})
    g.call("kdn", K_IN, "Key_GetDisplayName", inp={"Key": "@entry.pressed"}); g.call("kds", K_TXT, "Conv_TextToString", inp={"InText": "@kdn.ReturnValue"})
    g.get("gtk", "ToggleKey"); g.call("tks", K_STR, "Conv_NameToString", inp={"InName": "@gtk.ToggleKey"}); g.call("same", K_STR, "EqualEqual_StriStri", inp={"A": "@kds.ReturnValue", "B": "@tks.ReturnValue"})
    g.branch("bs", "@same.ReturnValue"); g.set("sht", "QuickKeyHint", inp={"QuickKeyHint": tt(g, "tkt", "Lbl_QuickKeyTaken")})
    g.call("kn", K_STR, "Conv_StringToName", inp={"InString": "@kds.ReturnValue"}); g.set("sk", "QuickKey", inp={"QuickKey": "@kn.ReturnValue"})
    g.call("et", K_TXT, "Conv_StringToText", inp={"InString": ""}); g.set("she", "QuickKeyHint", inp={"QuickKeyHint": "@et.ReturnValue"})
    g.n("sv", "call_self", function="Save Settings"); g.n("rb", "call_self", function="Rebuild Quick Options")
    g.chain("entry", "sc", "bs", "sht", "rb"); g.chain("bs:else", "sk", "she", "sv", "rb")
    return fn("Quick Key Captured", [param("pressed", mu.KEY_TYPE)], graph=g)


def f_mod_action_pos():
    """Where a new action goes in ModActionKeys: after every action with a lower or equal Order (like Mod Entry Pos)."""
    g = G(); g.set("z", "ModPosTmp", inp={"ModPosTmp": "0"})
    g.get("gk", "ModActionKeys"); g.foreach("fe", "@gk.ModActionKeys")
    g.get("ge", "ModActions"); g.call("f", K_MAP, "Map_Find", inp={"TargetMap": "@ge.ModActions", "Key": "@fe.Array Element"}); g.brk("be", mu.ACTION_STRUCT, "@f.Value")
    g.call("le", K_MATH, "LessEqual_IntInt", inp={"A": "@be.Order", "B": "@entry.order"}); g.branch("b", "@le.ReturnValue")
    g.get("gp", "ModPosTmp"); g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gp.ModPosTmp", "B": "1"}); g.set("s", "ModPosTmp", inp={"ModPosTmp": "@inc.ReturnValue"})
    g.get("gr", "ModPosTmp"); g.link("gr.ModPosTmp", "return.index")
    g.chain("entry", "z", "fe"); g.chain("fe", "b", "s"); g.chain("fe:Completed", "return")
    return fn("Mod Action Pos", [param("order", "int")], [param("index", "int")], graph=g)


def f_quick_mod_info():
    """A mod item of the quick menu -> QModCls (the actor's class), QModKey, QModToggle (flip instead of 1), QStr (caption), QModIcon.
    modfield:<pak>/<entry>|<Key> = a Button or Toggle field of AltUI_Fields; modaction:<pak>|<row> = a row of AltUI_Actions."""
    g = G(); g.n("k", "call_self", function="Quick Item Kind", inp={"item": "@entry.item"})
    g.set("s0", "QModOk", inp={"QModOk": "false"}); g.set("s1", "QModToggle", inp={"QModToggle": "false"}); g.set("s2", "QModIcon", inp={"QModIcon": "None"})
    g.n("scn", "call_self", function="Scan Mod Entries"); g.chain("entry", "scn", "s0", "s1", "s2")
    br, last = quick_kind_branches(g, "q", ["modfield", "modaction"], "@k.kind"); g.chain("s2", br["modfield"]); g.chain(last, "return")
    # action
    g.call("an", K_STR, "Conv_StringToName", inp={"InString": "@k.id"}); g.get("gma", "ModActions")
    g.call("af", K_MAP, "Map_Find", inp={"TargetMap": "@gma.ModActions", "Key": "@an.ReturnValue"}); g.brk("ab", mu.ACTION_STRUCT, "@af.Value")
    g.branch("baf", "@af.ReturnValue"); g.set("ao", "QModOk", inp={"QModOk": "true"}); g.set("ac", "QModCls", inp={"QModCls": "@ab.Actor"}); g.set("ak", "QModKey", inp={"QModKey": "@ab.Key"})
    g.call("acs", K_TXT, "Conv_TextToString", inp={"InText": "@ab.Caption"}); g.set("as", "QModCaption", inp={"QModCaption": "@acs.ReturnValue"}); g.set("ai", "QModIcon", inp={"QModIcon": "@ab.Icon"})
    g.chain(br["modaction"], "baf", "ao", "ac", "ak", "as", "ai", "return"); g.chain("baf:else", "return")
    # field: entry key | field key
    g.call("sp", K_STR, "Split", inp={"SourceString": "@k.id", "InStr": "|", "SearchCase": "CaseSensitive", "SearchDir": "FromEnd"})
    g.call("en", K_STR, "Conv_StringToName", inp={"InString": "@sp.LeftS"}); g.call("fk", K_STR, "Conv_StringToName", inp={"InString": "@sp.RightS"})
    g.get("gme", "ModEntries"); g.call("ef", K_MAP, "Map_Find", inp={"TargetMap": "@gme.ModEntries", "Key": "@en.ReturnValue"}); g.brk("eb", mu.ENTRY_STRUCT, "@ef.Value")
    g.get("gmf", "ModFields"); g.call("ff", K_MAP, "Map_Find", inp={"TargetMap": "@gmf.ModFields", "Key": "@en.ReturnValue"}); g.brk("fl", mu.LIST_STRUCT, "@ff.Value")
    g.call("ok2", K_MATH, "BooleanAND", inp={"A": "@ef.ReturnValue", "B": "@ff.ReturnValue"}); g.branch("bef", "@ok2.ReturnValue")
    g.set("sfl", "QFields", inp={"QFields": "@fl.Fields"}); g.get("gqf", "QFields"); g.foreach("fe", "@gqf.QFields"); g.brk("fb", mu.FIELD_STRUCT, "@fe.Array Element")
    g.call("keq", K_MATH, "EqualEqual_NameName", inp={"A": "@fb.Key", "B": "@fk.ReturnValue"})
    g.call("ib", K_MATH, "EqualEqual_NameName", inp={"A": "@fb.Type", "B": "Button"}); g.call("it", K_MATH, "EqualEqual_NameName", inp={"A": "@fb.Type", "B": "Toggle"})
    g.call("tp", K_MATH, "BooleanOR", inp={"A": "@ib.ReturnValue", "B": "@it.ReturnValue"}); g.call("hit", K_MATH, "BooleanAND", inp={"A": "@keq.ReturnValue", "B": "@tp.ReturnValue"}); g.branch("bh", "@hit.ReturnValue")
    g.set("fo", "QModOk", inp={"QModOk": "true"}); g.set("fc", "QModCls", inp={"QModCls": "@eb.Actor"}); g.set("fkk", "QModKey", inp={"QModKey": "@fb.Key"}); g.set("ft", "QModToggle", inp={"QModToggle": "@it.ReturnValue"})
    g.call("ecs", K_TXT, "Conv_TextToString", inp={"InText": "@eb.Caption"}); g.call("lcs", K_TXT, "Conv_TextToString", inp={"InText": "@fb.Label"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@ecs.ReturnValue", "B": " › "}); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@lcs.ReturnValue"}); g.set("fs", "QModCaption", inp={"QModCaption": "@c2.ReturnValue"})
    g.chain(br["modfield"], "bef", "sfl", "fe"); g.chain("bef:else", "return"); g.chain("fe", "bh", "fo", "fc", "fkk", "ft", "fs"); g.chain("fe:Completed", "return")
    g.get("rok", "QModOk"); g.link("rok.QModOk", "return.ok"); g.get("rcp", "QModCaption"); g.link("rcp.QModCaption", "return.caption")
    return fn("Quick Mod Info", [param("item", "string")], [param("ok", "bool"), param("caption", "string")], graph=g)


def f_quick_mod_actor():
    """The running actor of a mod item (None: not in this level / no such item)."""
    g = G(); g.n("i", "call_self", function="Quick Mod Info", inp={"item": "@entry.item"}); g.branch("b", "@i.ok"); g.chain("entry", "i", "b")
    g.get("gc", "QModCls"); g.call("ld", K_SYS, "LoadClassAsset_Blocking", inp={"AssetClass": "@gc.QModCls"}); g.n("cc", "class_cast", pure=True, cls=E_ACTOR, inp={"Class": "@ld.ReturnValue"})
    g.call("ga", K_GS, "GetActorOfClass", inp={"ActorClass": "@cc.AsActor"}); g.link("ga.ReturnValue", "return.actor")
    g.n("r2", "return_new")
    g.chain("b", "ld", "ga", "return"); g.chain("b:else", "r2")
    return fn("Quick Mod Actor", [param("item", "string")], [param("actor", "object:/Script/Engine.Actor")], graph=g)


def f_quick_add():
    """Append an item to the wheel (once, at most QUICK_MAX), save."""
    g = G(); g.get("gq", "QuickItems"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gq.QuickItems", "ItemToFind": "@entry.item"})
    g.call("ln", K_ARR, "Array_Length", inp={"TargetArray": "@gq.QuickItems"}); g.call("full", K_MATH, "GreaterEqual_IntInt", inp={"A": "@ln.ReturnValue", "B": str(QUICK_MAX)})
    g.call("no", K_MATH, "BooleanOR", inp={"A": "@has.ReturnValue", "B": "@full.ReturnValue"}); g.branch("b", "@no.ReturnValue")
    g.get("gq2", "QuickItems"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gq2.QuickItems", "NewItem": "@entry.item"}); g.n("sv", "call_self", function="Save Settings")
    g.chain("entry", "b"); g.chain("b:else", "add", "sv"); return fn("Quick Add", [param("item", "string")], graph=g)


def f_quick_remove():
    g = G(); g.get("gq", "QuickItems"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gq.QuickItems", "Item": "@entry.item"}); g.n("sv", "call_self", function="Save Settings")
    g.chain("entry", "rm", "sv"); return fn("Quick Remove", [param("item", "string")], graph=g)


def f_quick_move():
    """Move an item by delta places (-1 = towards the top / earlier); at the ends nothing happens."""
    g = G(); g.get("gq", "QuickItems"); g.call("i", K_ARR, "Array_Find", inp={"TargetArray": "@gq.QuickItems", "ItemToFind": "@entry.item"})
    g.call("j", K_MATH, "Add_IntInt", inp={"A": "@i.ReturnValue", "B": "@entry.delta"})
    g.call("v1", K_ARR, "Array_IsValidIndex", inp={"TargetArray": "@gq.QuickItems", "IndexToTest": "@i.ReturnValue"}); g.call("v2", K_ARR, "Array_IsValidIndex", inp={"TargetArray": "@gq.QuickItems", "IndexToTest": "@j.ReturnValue"})
    g.call("ok", K_MATH, "BooleanAND", inp={"A": "@v1.ReturnValue", "B": "@v2.ReturnValue"}); g.branch("b", "@ok.ReturnValue")
    g.get("gq2", "QuickItems"); g.call("sw", K_ARR, "Array_Swap", inp={"TargetArray": "@gq2.QuickItems", "FirstIndex": "@i.ReturnValue", "SecondIndex": "@j.ReturnValue"}); g.n("sv", "call_self", function="Save Settings")
    g.chain("entry", "b", "sw", "sv"); return fn("Quick Move", [param("item", "string"), param("delta", "int")], graph=g)


assets = [bp_cam_input(), blueprint(MGR, mode="augment", variables=[var("QuickWheel", "object:" + W_QUICK), var("QuickSectors", "object:" + W_QSECTOR, "array"), var("Panel", "object:" + W_PANEL), var("Menu", "object:" + W_MENU), var("TmpItems2", T_ITEM, "array"),
                               var("Palette", "object:" + P_PAL), var("ModFieldWidgets", "object:" + W_MODFIELD, "array"), var("FaceRows", "object:" + W_FACEROW, "array"), var("ColorItem", "name"), var("ColorOrig", S_LINCOLOR), var("ColorCur", S_LINCOLOR), var("ColorOpen", "bool"),
                               var("OptBgAlpha", "float"), var("OptTileAlpha", "float"), var("TmpSection", "object:" + W_SECTION)],
                    functions=[f_slot_color_key(), f_open_slot_color(), f_item_has_own_color(), f_row_is("Eye"), f_row_is("Eyelashes"), f_row_is_makeup(), f_row_has_makeup_color(), f_eye_color_key(),
                               f_apply_makeup_colors(), f_open_makeup_color(), f_set_makeup_color(), f_makeup_reset_color(),
                               *([f_makeup_probe()] if MAKEUPPROBE else []), f_apply_face(), f_face_row_changed(), f_face_all_fixed(), f_face_all_game(), f_toggle_face_add(), f_select_face_group(), f_rebuild_face_page(), f_rebuild_face_groups(), f_rebuild_face_right(), f_load_faces(), f_save_faces(), f_add_face(), f_update_face(), f_delete_face(), f_face_name(), f_set_face_name(), f_apply_saved_face(), f_rebuild_faces(), f_on_face_clicked(), f_on_face_context(), f_start_face_rename(), f_capture_face_photo(), f_face_icon(), f_current_look_row(), f_apply_eye_colors(), f_open_eye_color(), f_set_eye_color(), f_eye_reset_colors(), f_set_slot_color(), f_save_slot_color(), f_apply_item_colors(), f_apply_all_item_colors(), f_apply_saved_colors(), f_slot_reset_color(), f_reset_item_colors(), f_reset_dropped_colors(), f_commit_color(), f_close_color(), f_apply_preview(), f_toggle(), f_open(), f_close(), f_rebuild_left(), f_rebuild_list(), f_chip_shown(), f_rebuild_subtabs(), f_select_slot(),
                               f_take_off_slot(), f_on_item_clicked(), f_on_item_context(), f_close_menu(), f_on_menu_action(), f_select_subtab(), f_on_search_changed(), f_on_chip_search_changed(),
                               f_load_outfits(), f_save_outfits(), f_rebuild_top_tabs(), f_select_page(), f_rebuild_catalog_if_dirty(), f_on_manage_search_changed(), f_name_matches(), f_manage_rows(), f_manage_count(), f_manage_sub_counts(), f_rebuild_manage_cats(), f_select_manage_cat(), f_manage_default(), f_manage_origin(), f_manage_icon(), f_rebuild_manage(), f_focus_name_row(), f_refresh_manage_rows(), f_manage_search_for(), f_rename_kind(), f_start_item_rename(), f_finish_item_rename(), f_refresh_after_rename(), f_manage_rename(), f_manage_go_to(), f_rename_mod_of_item(), f_rename_group_of_item(), f_rebuild_manage_links(), f_poll_manage(), f_show_only_group(), f_open_mod_content_of_item(), f_open_mod_content(), f_rebuild_mod_content(), f_on_look_item_context(), f_swatch_color(), f_rebuild_hair_swatches(), f_hair_swatch_clicked(), f_toggle_hair_swatches(), f_rebuild_outfits(), f_outfit_slot_key(), f_remember_outfit_colors(), f_outfit_slot_colors(), f_on_outfit_clicked(), f_on_outfit_context(), f_delete_outfit(),
                               f_in_bag(), f_can_wear(), f_is_damaged(), f_rebuild_bag(), f_bag_toggle_wear(), f_bag_remove(), f_bag_cleanup(), f_bag_all_worn(), f_bag_repair(), f_bag_to_wardrobe(), f_put_in_bag(), f_on_bag_item_context(),
                               f_rebuild_hair(), f_hair_clicked(), f_open_hair_color(), f_look_caption(), f_is_look_selected(), f_look_type_of(), f_look_key(), f_is_look_favorite(), f_is_look_hidden(), f_toggle_look_favorite(), f_toggle_look_hidden(), f_collect_look_rows(), f_look_row_passes(), f_look_groups(), f_look_chip_caption(), f_look_chip_shown(), f_rebuild_look_chips(), f_select_look_group(), f_look_only_mod(), f_look_matches(), f_on_look_search_changed(), f_on_look_chip_search_changed(), f_rebuild_look_links(), f_look_count(), f_rebuild_look_cats(), f_select_look_cat(), f_tab_shown(), f_first_visible_page(), f_toggle_tab_hidden(), f_quick_sector_at(), f_quick_item_kind(), f_quick_find(), f_quick_item_caption(), f_quick_item_icon(), f_start_next_snapshot(), f_quick_add(), f_quick_remove(), f_quick_move(), f_run_quick_item(), f_open_quick_wheel(), f_quick_lock(), f_quick_hover(), f_close_quick_wheel(), f_quick_release(), f_quick_cancel(), f_quick_item_live(), f_rebuild_quick_options(), f_quick_noop(), f_quick_toggle(), f_quick_action(), f_quick_key_captured(), f_mod_action_pos(), f_quick_mod_info(), f_quick_mod_actor(), *([f_select_page_timed()] if TABLOG else []), f_rebuild_option_cats(), f_select_option_cat(), f_rebuild_tab_chips(), f_select_tab_style(), f_preset_name_row(), f_preset_shown_name(), f_sort_chips(), f_weapon_count_text(), f_manage_row_group(), f_manage_row_in_group(), f_manage_groups(), f_rebuild_manage_chips(), f_select_manage_group(), f_on_manage_chip_search_changed(), f_clear_manage_chip_search(), scale_getter("Outfit Scale", "OutfitScale"), scale_getter("Look Scale", "LookScale"), f_quick_alpha(), grid_getter("Outfit Cols", "OutfitCols"), grid_getter("Outfit Rows", "OutfitRows"), f_theme_save(), f_save_theme_preset(), f_apply_theme_preset(), f_delete_theme_preset(), f_rebuild_theme_presets(), f_subtab_context(),
                               f_rebuild_look(), f_look_clicked(), f_rebuild_body(), f_poll_body(), f_save_appearance_data(), f_scan_body_mods(), f_apply_body(), f_apply_saved_body(), f_find_menu_wearer(), f_select_body(),
                               f_apply_body_scales(), f_body_scale_factors(), f_vector_or_one(), f_set_body_scale_factors(), f_save_settings_soon(), f_settings_save_step(), f_reset_body_scales(), f_poll_body_scales(), f_log_line(), f_apply_strings(), f_select_language(), f_focus_code(), f_update_focus(),
                               f_on_hair_context(), f_hair_reset_color(), f_open_theme_color(), f_apply_theme(), f_select_key(), f_apply_nude(), f_fix_loaded_underwear(), f_start_outfit_rename(), f_join_names(), f_outfit_key(), f_outfit_name_by_key(), f_outfit_name(), f_set_outfit_name_by_key(), f_set_outfit_name(), f_rebuild_options(), f_apply_options(), f_poll_options(),
                               f_load_presets(), f_preset_icon(), f_preset_index(), f_preset_clicked(), f_preset_add(), f_preset_delete(), f_on_preset_context(), f_capture_photo(), f_capture_preset_photo(), f_capture_look_photo(), f_finish_photo(), f_look_icon(),
                               f_load_looks(), f_save_looks(), f_looks_count(), f_add_look(), f_update_look(), photo_mode_wrapper("Update Look Front", "Update Look", False), photo_mode_wrapper("Update Look View", "Update Look", True),
                               photo_mode_wrapper("Update Face Front", "Update Face", False), photo_mode_wrapper("Update Face View", "Update Face", True),
                               f_update_preset(), f_store_preset_colors(), photo_mode_wrapper("Update Preset Front", "Update Preset", False), photo_mode_wrapper("Update Preset View", "Update Preset", True), f_delete_look(), f_look_name(), f_set_look_name(), f_apply_look(), f_rebuild_looks(), f_on_look_clicked(), f_on_look_context(), f_start_look_rename(),
                               f_select_layout(), f_rebuild_conflicts(), f_toggle_conflict(), f_free_slot(), f_free_all(), f_ensure_cam_mod(), f_set_view_shift(), f_start_free_cam(), f_stop_free_cam(), f_free_cam_look(), f_free_cam_wheel(), f_free_cam_step(), f_start_photo_mode(), f_end_photo_mode(), f_cam_tick(), f_wheel_dist(), f_begin_jodi_drag(), f_jodi_drag(), f_end_jodi_drag(), f_collect_pose_rows(), f_pose_section_caption(), f_pose_section_count(), f_pose_title(), f_pose_name(), f_pose_actors(), f_pose_kind(), f_is_pose_moving(), f_is_pose_manual(), f_set_pose_kind(), f_pelvis_height(), f_measure_tick(), f_start_pose_scan(), f_stop_pose_scan(), f_scan_tick(), f_pose_set_stand(), f_pose_set_sit(), f_pose_set_lie(), f_reset_pose_measurement(), f_set_pose_measurement(), f_toggle_pose_moving(), f_pose_cat_count(), f_rebuild_pose_cats(), f_select_pose_cat(), f_pose_key(), f_is_pose_favorite(), f_is_pose_hidden(), f_pose_matches(), f_pose_row_shown(), f_pose_row_passes(), f_bump_pose_count(), f_count_pose_cats(), f_pose_groups(), f_rebuild_pose_chips(), f_select_pose_group(), f_rebuild_poses(), f_pose_clicked(), f_stop_pose(), f_rebuild_pose_links(), f_toggle_pose_favorite(), f_toggle_pose_hidden(), f_pose_only_mod(), f_on_pose_context(), f_on_pose_search_changed(), f_mod_field_valid(), f_mod_entry_pos(), f_add_mod_field(), f_scan_mod_entries(), f_mod_field_changed(), mod_forward("Mod Color Changed", mu.ON_COLOR, "color", S_LINCOLOR),
                               mod_forward("Mod Key Changed", mu.ON_KEY, "pressed", mu.KEY_TYPE), f_begin_key_capture(), f_key_captured(), f_cancel_key_capture(), f_capturing_key(), mod_forward("Mod Text Changed", mu.ON_TEXT, "text", "string"), f_open_mod_color(), f_rebuild_mod_entries(), f_rebuild_mod_fields(), f_poll_mods(), f_select_mod_entry(), f_rebuild_mod_page(), f_scan_weapon_skins(), f_scan_weapon_models(), f_weapon_rows(), f_skins_for_weapon(), f_skin_mod(), f_skin_row(), f_model_mod(), f_models_for_weapon(), f_model_mesh(), f_material_takes_color(), f_item_color_slots(), f_apply_weapon_model(), f_apply_weapon_look(), f_apply_all_weapon_looks(), f_poll_weapons(), f_select_weapon(), f_weapon_skin_clicked(), f_rebuild_weapons(), f_rebuild_weapon_skins(), f_skin_caption(), f_skin_icon(), f_is_skin_favorite(), f_skin_key(), f_skin_row_passes(), f_current_model(), f_current_skin(), f_model_row(), f_model_caption(), f_model_icon(), f_model_key(), f_is_model_favorite(), f_model_row_passes(), f_rebuild_weapon_models(), f_weapon_model_clicked(), f_toggle_model_favorite(), f_toggle_model_hidden(), f_model_has_icon(), f_toggle_model_own_icon(), f_model_forced(), *[f_toggle_model_skip(p, a) for p, _, a, _, _, _ in WEAPON_PARTS], f_toggle_model_force_skin(), f_model_only_mod(), f_on_model_context(), f_weapon_tile_row(), f_weapon_tile_clicked(), f_on_weapon_context(), f_weapon_icon_key(), f_weapon_icon(), f_capture_weapon_icon(), f_capture_weapon_icon_step(), f_skin_groups(), f_rebuild_weapon_chips(), f_select_skin_group(), f_rebuild_weapon_links(), f_on_weapon_search_changed(), f_toggle_skin_favorite(), f_toggle_skin_hidden(), f_skin_only_mod(), f_on_skin_context(), f_select_unowned(), f_redo_weapon_icons(), f_rebuild_status(), f_take_snapshot(), f_push_history(), f_apply_snapshot(), f_wear_queue_step(), f_finish_apply_snapshot(), history_step("Undo", "UndoStack", "RedoStack"), history_step("Redo", "RedoStack", "UndoStack"),
                               f_content_open(), f_open_content(), f_content_snapshot(), open_content_wrapper("Open Outfit Content", "Outfit"), open_content_wrapper("Open Look Content", "Look"), open_content_wrapper("Open Preset Content", "Preset"), open_content_wrapper("Open Face Content", "Face"), f_close_content(),
                               f_rebuild_content(), f_on_content_item_context(), f_content_kind(), f_content_item_clicked(), f_content_use(), f_go_to_item(), f_scroll_to_highlight()],
                    event_graph=event_graph())]
write(os.path.join(os.path.dirname(__file__), "..", "50_manager_ui.json"), assets)
