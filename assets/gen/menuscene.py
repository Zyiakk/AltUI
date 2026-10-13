"""Main menu scene picker (docs/notes/2026-10-11-reply-discord-menu-animation.md): in the main menu's scenes and in the loading
scene opened from there, the panel key opens a small menu instead of the panel (there is no Jodi pawn): the three menu scenes and
the loading scene to choose from, the next camera, and hiding the game's menu (Esc brings it back).

What the game does (bytecode 2026-10-11):
* Maps/Menu only throws the dice (RandomMenuScene_Pawn: OpenLevel of Menu_Standing / Menu_Sitting / Menu_Level2). Each scene is a map of
  its own with a Jodi_Intro, Menu_Gamemode (creates MainMenuUI, cursor on, music) and Menu_Pawn (a random Menu_Camera as view target;
  another one only in builds not packaged for distribution).
* Maps/Loading: LoadingPawn (native parent LoadingMapPawn) loads TKA_GameInstance.Level Name and opens it on a key press once the load is
  done. With Level Name = None it only shows the scene: LoadingUI, camera shake, Init(random 0..2) = camera height -10 / -55 / -110 and
  the walk (1: the figure's own Female_Walk, else Female_Walk_F). The game sets Level Name in "load level" before every load, so AltUI
  clears it only for its own visit. The key press after a finished load still runs into OpenLevel(None): the press is only taken while
  TextBlock_AnyKey is visible, so AltUI keeps that text collapsed in its own loading scene (Scene Tick)."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *

P_MAINMENU_UI = "/Game/Project/UserInterface/MainMenuUI"; P_LOADING_UI = "/Game/Project/UserInterface/LoadingUI"
P_MENU_CAM = "/Game/Project/Maps/Menu/Menu_Camera"; P_LOADING_PAWN = "/Game/Project/Maps/Loading/LoadingPawn"
P_JODI_INTRO = "/Game/Project/Character/Jodi/Jodi_Intro"; P_INTRO_ANIM = "/Game/Project/Character/Jodi/Jodi_Intro_Anim"
E_SEQ = "/Script/Engine.AnimSequence"; E_SEQBASE = "/Script/Engine.AnimSequenceBase"; E_ANIMINST = "/Script/Engine.AnimInstance"
K_GSL = "/Script/Engine.GameplayStatics"

# (action, caption key, level): the menu's scenes in the order of Menu.umap's Scene Names, then the loading scene
SCENES = [("Scene:Menu_Standing", "Scene_Standing", "Menu_Standing"), ("Scene:Menu_Sitting", "Scene_Sitting", "Menu_Sitting"),
          ("Scene:Menu_Level2", "Scene_Level2", "Menu_Level2"), ("Scene:Loading", "Scene_Loading", "Loading")]
LOADING_VIEWS = 3   # LoadingPawn.Init(0..2)
LOAD_HEIGHTS = (-10.0, -55.0, -110.0)   # its "offset z" per index: read back to know which view is on

# ALTUI_SCENELOG=1: the picker's steps and a heartbeat (every SCENELOG_BEAT frames) into AltUI_Log.sav ("Log Line"; `strings`
# reads it) - a Shipping build writes no log, and the file survives a crash. Off in the pak that goes out.
SCENELOG = os.environ.get("ALTUI_SCENELOG") == "1"; SCENELOG_BEAT = 30


def log(g, id, text):
    """Log Line(text) when SCENELOG (text: literal or pin), as an exec id list to splice into a chain ([] when off)."""
    if not SCENELOG: return []
    g.n(id, "call_self", function="Log Line", inp={"text": text}); return [id]


VARS = [var("SceneOn", "bool"), var("SceneLoad", "bool"), var("SceneHidden", "bool"), var("SceneView", "int"), var("SceneWidgets", "object:" + E_USERWIDGET, "array")]

SIGNATURES = [fn("Scene Init"), fn("Scene Key", [param("key", "struct:/Script/InputCore.Key")]), fn("Toggle Scene Menu"), fn("Open Scene Menu"),
              fn("Scene Action", [param("name", "name")]), fn("Scene Open", [param("level", "string")]), fn("Scene Next Camera"),
              fn("Scene Toggle Hidden"), fn("Scene Cursor", [param("show", "bool")]), fn("Scene Tick")]


def stubs():
    """Game classes the picker touches, as far as it needs them (kit stand-ins, never packed)."""
    return [blueprint(P_MAINMENU_UI, E_USERWIDGET),
            blueprint(P_LOADING_UI, E_USERWIDGET, variables=[var("TextBlock_AnyKey", "object:" + E_TEXT)]),
            blueprint(P_MENU_CAM, E_ACTOR),
            blueprint(P_JODI_INTRO, P_JODI_BASE, variables=[var("Idle Animation", "object:" + E_SEQ)]),
            blueprint(P_INTRO_ANIM, E_ANIMINST, variables=[var("Sequence", "object:" + E_SEQBASE)]),
            blueprint(P_LOADING_PAWN, E_PAWN, variables=[var("ui", "object:" + P_LOADING_UI), var("jodi", "object:" + P_JODI_INTRO), var("offset z", "float")],
                      functions=[fn("Init", [param("index", "int")])])]


def f_scene_init():
    """Menu branch of BeginPlay, after Find Menu Wearer: SceneOn in a menu scene (Menu_*) and in the loading scene without a level to
    load (AltUI's own visit), SceneLoad in the latter. Only then strings and theme for the small menu."""
    g = G()
    g.call("lvl", K_GSL, "GetCurrentLevelName", inp={"bRemovePrefixString": "true"})   # not pure in 4.27: on the exec chain
    g.call("menu", K_STR, "StartsWith", inp={"SourceString": "@lvl.ReturnValue", "InPrefix": "Menu_", "SearchCase": "CaseSensitive"})
    g.call("load", K_STR, "EqualEqual_StrStr", inp={"A": "@lvl.ReturnValue", "B": "Loading"})
    g.call("gi", K_GSL, "GetGameInstance"); g.cast("cgi", P_GI, "@gi.ReturnValue")
    g.get("gln", "Level Name", cls=P_GI); g.link("cgi.AsTKA Game Instance", "gln.self")
    g.call("none", K_MATH, "EqualEqual_NameName", inp={"A": "@gln.Level Name", "B": "None"})
    g.call("own", K_MATH, "BooleanAND", inp={"A": "@load.ReturnValue", "B": "@none.ReturnValue"})
    g.call("on", K_MATH, "BooleanOR", inp={"A": "@menu.ReturnValue", "B": "@own.ReturnValue"})
    g.set("sl", "SceneLoad", inp={"SceneLoad": "@own.ReturnValue"}); g.set("so", "SceneOn", inp={"SceneOn": "@on.ReturnValue"}); g.set("sh", "SceneHidden", inp={"SceneHidden": "false"})
    g.get("gon", "SceneOn"); g.branch("b", "@gon.SceneOn")
    g.n("dl", "call_self", function="Detect Language"); g.n("ist", "call_self", function="Init Strings"); g.n("ath", "call_self", function="Apply Theme")
    lg = []
    if SCENELOG:
        g.call("lgs", K_STR, "Conv_BoolToString", inp={"InBool": "@on.ReturnValue"}); g.call("lgc", K_STR, "Concat_StrStr", inp={"A": "scene init on=", "B": "@lgs.ReturnValue"})
        g.call("lgc2", K_STR, "Concat_StrStr", inp={"A": "@lgc.ReturnValue", "B": " level="}); g.call("lgc3", K_STR, "Concat_StrStr", inp={"A": "@lgc2.ReturnValue", "B": "@lvl.ReturnValue"})
        lg = log(g, "lg", "@lgc3.ReturnValue")
    g.chain("entry", "lvl", "sl", "so", "sh", *lg, "b", "dl", "ist", "ath", *log(g, "lg2", "scene init done"))
    return fn("Scene Init", graph=g)


def f_scene_key():
    """A key released in a picker scene: the panel key opens / closes the menu; Esc closes it, else shows a hidden game menu again."""
    g = G()
    g.call("kdn", K_IN, "Key_GetDisplayName", inp={"Key": "@entry.key"}); g.call("kds", K_TXT, "Conv_TextToString", inp={"InText": "@kdn.ReturnValue"})
    g.get("gtk", "ToggleKey"); g.call("tks", K_STR, "Conv_NameToString", inp={"InName": "@gtk.ToggleKey"})
    g.call("keq", K_STR, "EqualEqual_StriStri", inp={"A": "@kds.ReturnValue", "B": "@tks.ReturnValue"}); g.branch("bk", "@keq.ReturnValue")
    g.n("tsm", "call_self", function="Toggle Scene Menu")
    g.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@entry.key", "B": "Escape"}); g.branch("be", "@esc.ReturnValue")
    g.get("gm", "Menu"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gm.Menu"}); g.call("vp", E_USERWIDGET, "IsInViewport", inp={"self": "@gm.Menu"})
    g.call("open", K_MATH, "BooleanAND", inp={"A": "@iv.ReturnValue", "B": "@vp.ReturnValue"}); g.branch("bo", "@open.ReturnValue")
    g.n("cm", "call_self", function="Close Menu")
    g.get("gh", "SceneHidden"); g.branch("bh", "@gh.SceneHidden"); g.n("th", "call_self", function="Scene Toggle Hidden")
    if SCENELOG: g.call("lkc", K_STR, "Concat_StrStr", inp={"A": "scene key ", "B": "@kds.ReturnValue"})
    g.chain("entry", *log(g, "lk", "@lkc.ReturnValue"), "bk", "tsm", *log(g, "lk2", "scene key toggled")); g.chain("bk:else", "be", "bo", "cm"); g.chain("bo:else", "bh", "th")
    return fn("Scene Key", [param("key", "struct:/Script/InputCore.Key")], graph=g)


def f_toggle_scene_menu():
    g = G()
    g.get("gm", "Menu"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gm.Menu"}); g.call("vp", E_USERWIDGET, "IsInViewport", inp={"self": "@gm.Menu"})
    g.call("open", K_MATH, "BooleanAND", inp={"A": "@iv.ReturnValue", "B": "@vp.ReturnValue"}); g.branch("b", "@open.ReturnValue")
    g.n("cm", "call_self", function="Close Menu"); g.n("om", "call_self", function="Open Scene Menu")
    g.chain("entry", "b", *log(g, "lc", "toggle: close"), "cm", *log(g, "lc2", "toggle: closed")); g.chain("b:else", *log(g, "lo", "toggle: open"), "om", *log(g, "lo2", "toggle: opened"))
    return fn("Toggle Scene Menu", graph=g)


def f_open_scene_menu(simple_menu, ts):
    """The picker: the four scenes, next camera, hide / show the game's menu (the loading scene: its texts), cancel. In the loading
    scene the game hides the cursor: on while the menu is open (Close Menu takes it away again; Scene Cursor does nothing elsewhere)."""
    def pre(g):
        g.n("cur", "call_self", function="Scene Cursor", inp={"show": "true"})   # acts only where the game shows no cursor
        # caption of the hide row: menu / texts, hide / show
        g.get("gl", "SceneLoad")
        g.call("hm", K_MATH, "SelectString", inp={"A": ts(g, "sht", "Scene_HideText"), "B": ts(g, "shm", "Scene_Hide"), "bPickA": "@gl.SceneLoad"})
        g.call("wm", K_MATH, "SelectString", inp={"A": ts(g, "swt", "Scene_ShowText"), "B": ts(g, "swm", "Scene_Show"), "bPickA": "@gl.SceneLoad"})
        g.get("gh", "SceneHidden"); g.call("hs", K_MATH, "SelectString", inp={"A": "@wm.ReturnValue", "B": "@hm.ReturnValue", "bPickA": "@gh.SceneHidden"})
        g.call("ht", K_TXT, "Conv_StringToText", inp={"InString": "@hs.ReturnValue"})
        return ["cur"]
    rows = [(a, k) for a, k, _ in SCENES] + [("SceneCam", "Scene_Camera"), ("SceneHide", "@ht.ReturnValue"), ("Cancel", "Menu_Cancel")]
    g = simple_menu("Open Scene Menu", rows, pre)
    return fn("Open Scene Menu", graph=g)


def f_scene_action():
    """Menu rows of the picker: "Scene:<level>" opens that scene, SceneCam the next camera, SceneHide hides / shows the game's menu."""
    g = G()
    g.call("s", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"})
    g.call("pre", K_STR, "StartsWith", inp={"SourceString": "@s.ReturnValue", "InPrefix": "Scene:", "SearchCase": "CaseSensitive"}); g.branch("bp", "@pre.ReturnValue")
    g.call("lv", K_STR, "RightChop", inp={"SourceString": "@s.ReturnValue", "Count": "6"}); g.n("op", "call_self", function="Scene Open", inp={"level": "@lv.ReturnValue"})
    g.call("ic", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "SceneCam"}); g.branch("bc", "@ic.ReturnValue"); g.n("nc", "call_self", function="Scene Next Camera")
    g.call("ih", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "SceneHide"}); g.branch("bh", "@ih.ReturnValue"); g.n("th", "call_self", function="Scene Toggle Hidden")
    if SCENELOG: g.call("lac", K_STR, "Concat_StrStr", inp={"A": "scene action ", "B": "@s.ReturnValue"})
    g.chain("entry", *log(g, "la", "@lac.ReturnValue"), "bp", "op"); g.chain("bp:else", "bc", "nc"); g.chain("bc:else", "bh", "th")
    return fn("Scene Action", [param("name", "name")], graph=g)


def f_scene_open():
    """Open a scene. The loading scene only shows itself when the game instance has no level to load: Level Name = None (the game sets
    it again in "load level" before each of its own loads)."""
    g = G()
    g.call("il", K_STR, "EqualEqual_StrStr", inp={"A": "@entry.level", "B": "Loading"}); g.branch("bl", "@il.ReturnValue")
    g.call("gi", K_GSL, "GetGameInstance"); g.cast("cgi", P_GI, "@gi.ReturnValue")
    g.n("sln", "set", var="Level Name", cls=P_GI, inp={"self": "@cgi.AsTKA Game Instance", "Level Name": "None"})
    g.call("ln", K_STR, "Conv_StringToName", inp={"InString": "@entry.level"})
    g.call("ol", K_GSL, "OpenLevel", inp={"LevelName": "@ln.ReturnValue", "bAbsolute": "true", "Options": ""})
    g.chain("entry", "bl", "sln", "ol"); g.chain("bl:else", "ol")
    return fn("Scene Open", [param("level", "string")], graph=g)


def f_scene_next_camera():
    """Menu scene: the next Menu_Camera after the current view target (the game picks one at random; -1 -> the first).
    Loading scene: the next of LoadingPawn's three views (Init(index)); its current one from the camera height it keeps (offset z).
    Init sets Female_Walk_F for 0 and 2 but leaves 1 alone - for 1 the figure's own walk (Idle Animation) goes back on."""
    g = G()
    g.get("gl", "SceneLoad"); g.branch("bl", "@gl.SceneLoad")
    # menu scene
    g.call("all", K_GSL, "GetAllActorsOfClass", inp={"ActorClass": P_MENU_CAM}); g.set("sa", "TmpActors", inp={"TmpActors": "@all.OutActors"})
    g.get("ga", "TmpActors"); g.call("n", K_ARR, "Array_Length", inp={"TargetArray": "@ga.TmpActors"})
    g.call("has", K_MATH, "Greater_IntInt", inp={"A": "@n.ReturnValue", "B": "0"}); g.branch("bh", "@has.ReturnValue")
    g.get("gpc", "PC"); g.call("vt", E_CTRL, "GetViewTarget", inp={"self": "@gpc.PC"})
    g.call("fi", K_ARR, "Array_Find", inp={"TargetArray": "@ga.TmpActors", "ItemToFind": "@vt.ReturnValue"})
    g.call("nx", K_MATH, "Add_IntInt", inp={"A": "@fi.ReturnValue", "B": "1"}); g.call("md", K_MATH, "Percent_IntInt", inp={"A": "@nx.ReturnValue", "B": "@n.ReturnValue"})
    g.call("cam", K_ARR, "Array_Get", inp={"TargetArray": "@ga.TmpActors", "Index": "@md.ReturnValue"})
    g.get("gpc2", "PC"); g.call("svt", E_PC, "SetViewTargetWithBlend", inp={"self": "@gpc2.PC", "NewViewTarget": "@cam.Item", "BlendTime": "0.0", "BlendFunc": "VTBlend_Linear", "BlendExp": "0.0", "bLockOutgoing": "false"})
    # loading scene
    g.call("gp", K_GSL, "GetActorOfClass", inp={"ActorClass": P_LOADING_PAWN}); g.cast("cp", P_LOADING_PAWN, "@gp.ReturnValue", pure=False, miss="ignore")
    g.get("goz", "offset z", cls=P_LOADING_PAWN); g.link("cp.AsLoading Pawn", "goz.self")
    mid = (LOAD_HEIGHTS[0] + LOAD_HEIGHTS[1]) / 2; low = (LOAD_HEIGHTS[1] + LOAD_HEIGHTS[2]) / 2
    g.call("l1", K_MATH, "Less_FloatFloat", inp={"A": "@goz.offset z", "B": str(mid)}); g.call("l2", K_MATH, "Less_FloatFloat", inp={"A": "@goz.offset z", "B": str(low)})
    g.call("c1", K_MATH, "SelectInt", inp={"A": "1", "B": "0", "bPickA": "@l1.ReturnValue"}); g.call("c2", K_MATH, "SelectInt", inp={"A": "2", "B": "@c1.ReturnValue", "bPickA": "@l2.ReturnValue"})
    g.call("ln", K_MATH, "Add_IntInt", inp={"A": "@c2.ReturnValue", "B": "1"}); g.call("lm", K_MATH, "Percent_IntInt", inp={"A": "@ln.ReturnValue", "B": str(LOADING_VIEWS)})
    # kept in a variable: Init changes offset z, and the pure nodes above would be read again after it
    g.set("sv", "SceneView", inp={"SceneView": "@lm.ReturnValue"}); g.get("gv", "SceneView")
    g.call("ini", P_LOADING_PAWN, "Init", inp={"self": "@cp.AsLoading Pawn", "index": "@gv.SceneView"})
    g.call("is1", K_MATH, "EqualEqual_IntInt", inp={"A": "@gv.SceneView", "B": "1"}); g.branch("b1", "@is1.ReturnValue")
    g.get("gj", "jodi", cls=P_LOADING_PAWN); g.link("cp.AsLoading Pawn", "gj.self")
    g.get("gme", "Mesh", cls=E_CHARACTER); g.link("gj.jodi", "gme.self"); g.call("ai", E_SKELMESHCOMP, "GetAnimInstance", inp={"self": "@gme.Mesh"})
    g.cast("ca", P_INTRO_ANIM, "@ai.ReturnValue", pure=False, miss="ignore")
    g.get("gia", "Idle Animation", cls=P_JODI_INTRO); g.link("gj.jodi", "gia.self")
    g.n("ssq", "set", var="Sequence", cls=P_INTRO_ANIM, inp={"self": "@ca.AsJodi Intro Anim", "Sequence": "@gia.Idle Animation"})
    g.chain("entry", "bl", "gp", "cp", "sv", "ini", "b1", "ca", "ssq"); g.chain("bl:else", "all", "sa", "bh", "svt")
    return fn("Scene Next Camera", graph=g)


def f_scene_toggle_hidden():
    """Hide / show the game's menu (MainMenuUI; in the loading scene LoadingUI). Hidden in the main menu also hides the cursor and
    gives the keys to the game viewport (Esc must reach AltUI, not a hidden button). Shown again: SelfHitTestInvisible, a user
    widget's default."""
    g = G()
    g.get("gh", "SceneHidden"); g.call("nh", K_MATH, "Not_PreBool", inp={"A": "@gh.SceneHidden"}); g.set("sh", "SceneHidden", inp={"SceneHidden": "@nh.ReturnValue"})
    g.get("gl", "SceneLoad"); g.branch("bl", "@gl.SceneLoad")
    g.call("wl", K_WBL, "GetAllWidgetsOfClass", inp={"WidgetClass": P_LOADING_UI, "TopLevelOnly": "false"}); g.set("swl", "SceneWidgets", inp={"SceneWidgets": "@wl.FoundWidgets"})
    g.call("wm", K_WBL, "GetAllWidgetsOfClass", inp={"WidgetClass": P_MAINMENU_UI, "TopLevelOnly": "false"}); g.set("swm", "SceneWidgets", inp={"SceneWidgets": "@wm.FoundWidgets"})
    g.get("gw", "SceneWidgets"); g.foreach("fe", "@gw.SceneWidgets")
    g.get("gh2", "SceneHidden"); g.branch("bv", "@gh2.SceneHidden")
    g.call("hid", E_WIDGET, "SetVisibility", inp={"self": "@fe.Array Element", "InVisibility": "Hidden"})
    g.call("vis", E_WIDGET, "SetVisibility", inp={"self": "@fe.Array Element", "InVisibility": "SelfHitTestInvisible"})
    # main menu only: the cursor goes with the menu (the loading scene has none unless the picker is open)
    g.get("gl2", "SceneLoad"); g.branch("bc", "@gl2.SceneLoad")
    g.get("gh3", "SceneHidden"); g.call("sc", K_MATH, "Not_PreBool", inp={"A": "@gh3.SceneHidden"})
    g.get("gpc", "PC"); g.n("smc", "set", var="bShowMouseCursor", cls=E_PC, inp={"self": "@gpc.PC", "bShowMouseCursor": "@sc.ReturnValue"})
    g.get("gh4", "SceneHidden"); g.branch("bf", "@gh4.SceneHidden"); g.call("fv", K_WBL, "SetFocusToGameViewport")
    g.chain("entry", "sh", "bl", "wl", "swl", "fe"); g.chain("bl:else", "wm", "swm", "fe"); g.chain("fe", "bv", "hid"); g.chain("bv:else", "vis")
    g.chain("fe:Completed", "bc"); g.chain("bc:else", "smc", "bf", "fv")
    return fn("Scene Toggle Hidden", graph=g)


def f_scene_cursor():
    """Cursor for the picker where the game shows none: the loading scene (LoadingPawn sets game-only input) and the main menu
    while its menu is hidden (Scene Toggle Hidden took the cursor away). show: cursor on, UI input with the picker focused.
    Off again: cursor off; loading scene back to game only (as LoadingPawn set it), hidden main menu keys to the game viewport
    (Esc must reach AltUI). Main menu with its menu shown: nothing - the game's cursor stays as it is."""
    g = G()
    g.get("gl", "SceneLoad"); g.get("gh", "SceneHidden"); g.call("need", K_MATH, "BooleanOR", inp={"A": "@gl.SceneLoad", "B": "@gh.SceneHidden"}); g.branch("bl", "@need.ReturnValue")
    g.get("gpc", "PC"); g.n("smc", "set", var="bShowMouseCursor", cls=E_PC, inp={"self": "@gpc.PC", "bShowMouseCursor": "@entry.show"})
    g.branch("b", "@entry.show")
    g.get("gpc2", "PC"); g.get("gm", "Menu")
    g.call("ui", K_WBL, "SetInputMode_GameAndUIEx", inp={"PlayerController": "@gpc2.PC", "InWidgetToFocus": "@gm.Menu", "InMouseLockMode": "DoNotLock", "bHideCursorDuringCapture": "false"})
    g.get("gl2", "SceneLoad"); g.branch("bld", "@gl2.SceneLoad")
    g.get("gpc3", "PC"); g.call("go", K_WBL, "SetInputMode_GameOnly", inp={"PlayerController": "@gpc3.PC"})
    g.call("fv", K_WBL, "SetFocusToGameViewport")
    g.chain("entry", "bl", "smc", "b", "ui"); g.chain("b:else", "bld", "go"); g.chain("bld:else", "fv")
    return fn("Scene Cursor", [param("show", "bool")], graph=g)


def f_scene_tick():
    """Every frame in AltUI's own loading scene: "press any key" stays collapsed - LoadingPawn only acts on a key while it is
    visible, and with no level to load it would open level None."""
    g = G()
    g.get("gl", "SceneLoad"); g.branch("b", "@gl.SceneLoad")
    g.call("gp", K_GSL, "GetActorOfClass", inp={"ActorClass": P_LOADING_PAWN}); g.cast("cp", P_LOADING_PAWN, "@gp.ReturnValue", pure=False, miss="ignore")
    g.get("gui", "ui", cls=P_LOADING_PAWN); g.link("cp.AsLoading Pawn", "gui.self")
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@gui.ui"}); g.branch("bv", "@iv.ReturnValue")
    g.get("gak", "TextBlock_AnyKey", cls=P_LOADING_UI); g.link("gui.ui", "gak.self")
    g.call("hd", E_WIDGET, "SetVisibility", inp={"self": "@gak.TextBlock_AnyKey", "InVisibility": "Collapsed"})
    head = ["entry"]
    if SCENELOG:
        g.get("gtc", "TickCount"); g.call("tm", K_MATH, "Percent_IntInt", inp={"A": "@gtc.TickCount", "B": str(SCENELOG_BEAT)})
        g.call("t0", K_MATH, "EqualEqual_IntInt", inp={"A": "@tm.ReturnValue", "B": "0"}); g.branch("bt", "@t0.ReturnValue")
        g.get("gso", "SceneOn"); g.branch("bso", "@gso.SceneOn")
        g.get("gmn", "Menu"); g.call("mv", E_USERWIDGET, "IsInViewport", inp={"self": "@gmn.Menu"}); g.call("mvs", K_STR, "Conv_BoolToString", inp={"InBool": "@mv.ReturnValue"})
        g.call("hbc", K_STR, "Concat_StrStr", inp={"A": "beat menu=", "B": "@mvs.ReturnValue"}); log(g, "hb", "@hbc.ReturnValue")
        g.chain("entry", "bso", "bt", "hb", "b"); g.chain("bt:else", "b"); g.chain("bso:else", "b"); head = []
    g.chain(*head, "b", "gp", "cp", "bv", "hd") if head else g.chain("b", "gp", "cp", "bv", "hd")
    return fn("Scene Tick", graph=g)


def functions(simple_menu, ts):
    return [f_scene_init(), f_scene_key(), f_toggle_scene_menu(), f_open_scene_menu(simple_menu, ts), f_scene_action(), f_scene_open(),
            f_scene_next_camera(), f_scene_toggle_hidden(), f_scene_cursor(), f_scene_tick()]
