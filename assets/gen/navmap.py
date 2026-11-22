"""Navigation tab: a map of the level (internal design notes).

The game has no map pictures, so AltUI draws its own: the world is cut into square tiles (TILE_CM), and while Jodi plays a
SceneCapture2D looks straight down onto the tile she is in and its neighbours, orthographic, from CUT_IN above her feet (UE 4.27:
an orthographic capture's near plane is the camera itself, so ceilings and upper floors are cut off - a floor plan). Outside (no
roof within SKY_CM above her head) the camera hangs CUT_OUT above her feet: terrain and trees from above. Each tile is exported as
a PNG per level, floor band and tile, so the map grows as she explores; the Navigation tab shows the tiles of one band in a
W_NavMap (gen_widgets.py: pools of images on a canvas, the mouse goes to the manager), with markers (Jodi, beds, followers,
zombies) and a click target to teleport to.

Coordinates: the camera looks down with yaw 0, so on the map up = +X and right = +Y. Tile (x, y) covers X in [x, x+1) * TILE_CM and
Y in [y, y+1) * TILE_CM; on screen its top-left corner is world point ((x+1) * TILE_CM, y * TILE_CM).
Floor bands: band = floor(feet z / BAND_CM), kept while the feet stay within BAND_HYST of the band (stairs do not flicker);
OUT_BAND (1000, file key "O") is "outside"."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *

TILE_CM = 4000.0; TILE_PX = 512          # 40 m per tile, ~8 cm per pixel
BAND_CM = 350.0; BAND_HYST = 100.0       # a floor band, and how far the feet may leave it before the band changes
Z_TOL = 100.0                            # an inside tile counts as taken while Jodi's feet are within this of the height it was taken from
CUT_IN = 200.0; CUT_OUT = 5000.0         # camera height above the feet: inside (the cut), outside (above the trees)
SKY_CM = 3000.0                          # nothing above her head within this -> outside
OUT_BAND = 1000                          # "outside" as a band number
CAPTURE_EVERY = 1.0; REDRAW_EVERY = 0.25 # seconds: one tile per capture step; markers while the tab is open
MAP_DIR = "SaveGames/AltUI/Map/"         # under ProjectSavedDir: <level>/<style>/<band>_<x>_<y>.png
MAP_EXT = ".png"
SC = 1.9                                 # gen_widgets.SC
def sz(v): return int(round(v * SC))
MAP_W, MAP_H = sz(560), sz(360)          # the map area until W_NavMap has a size (it fills the panel width and half its height: MapW / MapH)
TILE_POOL = 200; MARK_POOL = 120          # images on the map: tiles (PX_MIN keeps the visible ones below the pool), markers
CROSS = TILE_POOL + MARK_POOL; ARROW = CROSS + 1; POOL = ARROW + 1
PX_MIN, PX_MAX, PX_DEFAULT, ZOOM_STEP = float(sz(64)), float(sz(1024)), float(sz(256)), 1.25   # widget units per tile; a wheel notch zooms by ZOOM_STEP
CLICK_PX = float(sz(4))                  # mouse travel up to this is a click, more is a drag
BED_HIT = sz(14)                         # a click this near a bed marker picks the bed
MARK = {"bed": sz(16), "dot": sz(9), "ring": sz(12), "dead": sz(9), "vend": sz(14), "arrow": sz(20), "cross": sz(24)}
NEIGHBOURS = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]   # capture order: her tile first
STYLES = ("SCS_BaseColor", "SCS_SceneColorHDR", "SCS_Normal")   # MapStyle 0 base colour (default), 1 lit, 2 surfaces (shaded in M_MapTile)
STYLE_DIRS = ("base", "lit", "surfaces")   # every tile is taken in all three styles, each into its own folder (play test 2026-11-19: a
                                           # style switch showed the other styles' pictures, "surfaces" shading a colour picture)
LIT_BOOST = 1.8                            # "lit" a bit brighter than the base colour on average (it looked best so in the office)
M_MAPMEAN = "/Game/Mod/AltUI/Mat/M_MapMean"
STYLE_KEYS = ("Map_StyleBase", "Map_StyleLit", "Map_StyleFlat")
# minimap (Options > Map): corner 0 top left, 1 top right, 2 bottom left, 3 bottom right; size and margin in % of the screen height;
# zoom = metres across the minimap. Placed every frame it is shown, drawn every MINI_EVERY seconds, turned with the camera.
MINI_CORNER, MINI_SIZE, MINI_MARGIN, MINI_ZOOM = 1, 25.0, 2.0, 60.0
MINI_SIZE_RANGE, MINI_MARGIN_RANGE, MINI_ZOOM_RANGE = (10.0, 60.0), (0.0, 15.0), (20.0, 200.0)
MINI_EVERY = 0.05; MINI_PAD = sz(3); MINI_DIAG = 1.4143; MINI_Z = 40   # under the panel (100)
FULL_RIM = 0.03                          # fullscreen map: rim around it, share of the screen height
NAV_EXTENT_IN, NAV_EXTENT_OUT = "(X=100,Y=100,Z=400)", "(X=100,Y=100,Z=3000)"   # teleport target -> navmesh

W_NAVMAP = M + "/W_NavMap"; W_MAPSLOT = M + "/W_MapSlot"; W_MINIMAP = M + "/W_MiniMap"; W_MAPLEG = M + "/W_MapLegItem"; W_SUB = M + "/W_SubTab"; W_PANEL = M + "/W_AltUI"; W_TXT = M + "/W_TextButton"; MGR = M + "/BP_AltUIManager"
M_MAPTILE = "/Game/Mod/AltUI/Mat/M_MapTile"; M_MAPCOMBINE = "/Game/Mod/AltUI/Mat/M_MapCombine"; M_MAPCIRCLE = "/Game/Mod/AltUI/Mat/M_MapCircle"; MID = "/Script/Engine.MaterialInstanceDynamic"
T_ARROW, T_DOT, T_BED, T_CROSS = M + "/T_MapArrow", M + "/T_MapDot", M + "/T_MapBed", M + "/T_MapCross"
E_SCAP = "/Script/Engine.SceneCapture2D"; E_SCAPC = "/Script/Engine.SceneCaptureComponent2D"; E_SCAPCB = "/Script/Engine.SceneCaptureComponent"
E_WIDGET = "/Script/UMG.Widget"; K_SLATE = "/Script/UMG.SlateBlueprintLibrary"; K_MATLIB = "/Script/Engine.KismetMaterialLibrary"
E_PC = "/Script/Engine.PlayerController"; E_TEXT = "/Script/UMG.TextBlock"; K_WBL = "/Script/UMG.WidgetBlueprintLibrary"; E_USERWIDGET = "/Script/UMG.UserWidget"
E_CHAR = "/Script/Engine.Character"; E_CAMC = "/Script/Engine.CameraComponent"; E_CAPS = "/Script/Engine.CapsuleComponent"
K_NAVSYS = "/Script/NavigationSystem.NavigationSystemV1"
S_VEC = "struct:/Script/CoreUObject.Vector"; S_V2 = "struct:/Script/CoreUObject.Vector2D"
COL_BED, COL_FOL, COL_ENEMY, COL_JODI = "(R=1,G=1,B=1,A=1)", "(R=0.25,G=0.95,B=0.35,A=1)", "(R=1,G=0.18,B=0.12,A=1)", "(R=1,G=0.85,B=0.2,A=1)"
COL_JODI_DIM = "(R=1,G=0.85,B=0.2,A=0.4)"
COL_NPC, COL_HOSTILE, COL_DEAD, COL_VEND = "(R=0.35,G=0.75,B=1,A=1)", "(R=1,G=0.55,B=0.1,A=1)", "(R=0.55,G=0.55,B=0.55,A=0.85)", "(R=0.2,G=0.9,B=0.85,A=1)"
T_RING, T_DEAD, T_VEND, T_LOWER, T_HATCH, T_RINGFRAME = M + "/T_MapRing", M + "/T_MapDead", M + "/T_MapVend", M + "/T_MapLower", M + "/T_MapHatch", M + "/T_MapRingFrame"
# marker kinds (spec 2026-11-19): code = index; the name is the key in MapHidden (saved) and of the legend entry; bit 1 << code in MapSeen
KIND_KEYS = ("", "fol", "npc", "zombie", "hostile", "dead", "bed", "vend")
K_FOL, K_NPC, K_ZOMBIE, K_HOSTILE, K_DEAD, K_BED, K_VEND = 1, 2, 3, 4, 5, 6, 7
KIND_COL = {K_FOL: COL_FOL, K_NPC: COL_NPC, K_ZOMBIE: COL_ENEMY, K_HOSTILE: COL_HOSTILE, K_DEAD: COL_DEAD, K_BED: COL_BED, K_VEND: COL_VEND}
KIND_TEX = {K_FOL: T_DOT, K_NPC: T_DOT, K_ZOMBIE: T_DOT, K_HOSTILE: T_RING, K_DEAD: T_DEAD, K_BED: T_BED, K_VEND: T_VEND}

# menu actions (name, manager function): the links above the map
ACTIONS = [("MapUp", "Map Up"), ("MapDown", "Map Down"), ("MapOutside", "Map Outside"), ("MapCenter", "Map Center"), ("MapFull", "Map Full Toggle"),
           ("MapRecord", "Map Record Toggle"), ("MapStyle", "Map Style Next"), ("MapGo", "Map Teleport"), ("MapRetake", "Map Retake")]

# persisted (gen_manager SETTINGS / SG_AltUI): MapNoRecord (default false = recording on), MapStyle
# MapOff: the whole map off (no recording, nothing drawn, no minimap) - default on; the minimap's settings (defaults in the class: an
# older AltUI_Settings.sav lacks them and keeps these)
_PERSIST = [("MapNoRecord", "bool", None), ("MapStyle", "int", None), ("MapOff", "bool", None), ("MiniOn", "bool", None), ("MiniCorner", "int", str(MINI_CORNER)),
            ("MiniSize", "float", str(MINI_SIZE)), ("MiniMargin", "float", str(MINI_MARGIN)), ("MiniZoom", "float", str(MINI_ZOOM))]
_PERSIST += [("MapNoLegend", "bool", None), ("MiniRound", "bool", None)]
_PERSIST += [("MapOneStyle", "bool", None)]   # Options > Map "Only take pictures for the active map style" (play test 2026-11-21)   # Options > Map "Show legend" (stored inverted), minimap shape (spec 2026-11-19)
# MapHidden: kinds hidden by a click on the legend; MapLitGain: "lit" brightness per level and inside / outside (Map Capture Tile)
SETTINGS = [(k, k, "copy", None) for k, _, _ in _PERSIST] + [(v, v, "copy", None) for v in ("MapHidden", "MapLitGain")]
SG_VARS = [var(k, t, **({"default": d} if d else {})) for k, t, d in _PERSIST] + [var("MapHidden", "name", "array"), var("MapLitGain", "string", "map", value_type="float")]
MGR_VARS = [var(k, t, **({"default": d} if d else {})) for k, t, d in _PERSIST] + [var("MapHidden", "name", "array"), var("MapLitGain", "string", "map", value_type="float")]
VARS = [var("MapBand", "int"), var("MapBandSet", "bool"), var("MapOut", "bool"), var("MapFeetZ", "float"), var("MapNext", "float"), var("MapNextDraw", "float"),
        var("MapDone", "string", "map", value_type="bool"), var("MapDoneZ", "string", "map", value_type="float"), var("MapTileTmp", "object:" + E_TEX2D), var("MapSpot", S_VEC), var("MapTex", "string", "map", value_type="object:" + E_TEX2D), var("MapMiss", "string", "map", value_type="bool"),
        var("MapRT", "object:/Script/Engine.TextureRenderTarget2D"), var("MapLevel", "string"), var("MapView", "object:" + W_NAVMAP),
        var("MapShowBand", "int"), var("MapCX", "float"), var("MapCY", "float"), var("MapPx", "float"), var("MapPi", "int"), var("MapMi", "int"),
        var("MapPressed", "bool"), var("MapMoved", "bool"), var("MapDownX", "float"), var("MapDownY", "float"), var("MapLastX", "float"), var("MapLastY", "float"),
        var("MapTgtOn", "bool"), var("MapTgt", S_VEC), var("MapTgtBed", "int"), var("MapHitD", "float"),
        var("MapW", "float", default=str(float(MAP_W))), var("MapH", "float", default=str(float(MAP_H))), var("MapColRT", "object:/Script/Engine.TextureRenderTarget2D"),
        var("MapDepRT", "object:/Script/Engine.TextureRenderTarget2D"), var("MapMID", "object:/Script/Engine.MaterialInstanceDynamic"),
        var("MapHdrRT", "object:/Script/Engine.TextureRenderTarget2D"), var("MapMeanRT", "object:/Script/Engine.TextureRenderTarget2D"), var("MapMeanMID", "object:/Script/Engine.MaterialInstanceDynamic"),
        var("MapBeds", "object:" + P_BED, "array"), var("MapMini", "bool"), var("MiniView", "object:" + W_MINIMAP), var("MiniShown", "bool"), var("MiniNext", "float"),
        var("OptMiniSize", "float"), var("OptMiniMargin", "float"), var("OptMiniZoom", "float"),
        var("MapVends", "object:" + E_ACTOR, "array"), var("MapChars", "object:" + E_ACTOR, "array"), var("MapCharKinds", "int", "array"), var("MapSeen", "int"), var("MapLegMask", "int", default="-1"),
        var("MapFullOn", "bool"), var("MapFullFromPanel", "bool"), var("MapFullPrevPage", "name"), var("MapFullArm", "bool"), var("QFromKey", "bool")] + \
       [var("MapSv" + k, t) for k, t in (("View", "object:" + W_NAVMAP), ("W", "float"), ("H", "float"), ("CX", "float"), ("CY", "float"), ("Px", "float"), ("Band", "int"))]

# called by W_NavMap (compiled before 50_manager_ui): signatures in gen_manager's UI_SIGNATURES
SIGNATURES = [fn("Map Legend Toggle", [param("key", "name")]), fn("Map Full Key", [param("key", "string")], [param("yes", "bool")]), fn("Map Wheel", [param("notches", "float"), param("x", "float"), param("y", "float")]), fn("Map Press", [param("x", "float"), param("y", "float")]),
              fn("Map Move", [param("x", "float"), param("y", "float")]), fn("Map Release", [param("x", "float"), param("y", "float")])]


def _half(g, p, var):
    """Half the map area along MapW / MapH (its laid-out size, Map Redraw) as a pin."""
    g.get(p + "g", var); g.call(p, K_MATH, "Multiply_FloatFloat", inp={"A": "@%sg.%s" % (p, var), "B": "0.5"}); return "@%s.ReturnValue" % p


# ---------------- pure arithmetic (tests/unit/test_navmap.py runs these with bp_eval) ----------------
def f_band_next():
    """The floor band for feet height z: the current one while z stays within BAND_HYST of it (and one is set), else floor(z / BAND_CM)."""
    g = G()
    g.call("cf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@entry.cur"}); g.call("lo0", K_MATH, "Multiply_FloatFloat", inp={"A": "@cf.ReturnValue", "B": str(BAND_CM)})
    g.call("lo", K_MATH, "Subtract_FloatFloat", inp={"A": "@lo0.ReturnValue", "B": str(BAND_HYST)}); g.call("hi", K_MATH, "Add_FloatFloat", inp={"A": "@lo0.ReturnValue", "B": str(BAND_CM + BAND_HYST)})
    g.call("ge", K_MATH, "GreaterEqual_FloatFloat", inp={"A": "@entry.z", "B": "@lo.ReturnValue"}); g.call("lt", K_MATH, "Less_FloatFloat", inp={"A": "@entry.z", "B": "@hi.ReturnValue"})
    g.call("in", K_MATH, "BooleanAND", inp={"A": "@ge.ReturnValue", "B": "@lt.ReturnValue"}); g.call("keep", K_MATH, "BooleanAND", inp={"A": "@in.ReturnValue", "B": "@entry.has"})
    g.call("dz", K_MATH, "Divide_FloatFloat", inp={"A": "@entry.z", "B": str(BAND_CM)}); g.call("nb", K_MATH, "FFloor", inp={"A": "@dz.ReturnValue"})
    g.call("sel", K_MATH, "SelectInt", inp={"A": "@entry.cur", "B": "@nb.ReturnValue", "bPickA": "@keep.ReturnValue"}); g.link("sel.ReturnValue", "return.band")
    return fn("Map Band Next", [param("cur", "int"), param("has", "bool"), param("z", "float")], [param("band", "int")], graph=g, pure=True)


def f_band_of():
    """The band a point at height z (feet / floor) lies in."""
    g = G(); g.call("dz", K_MATH, "Divide_FloatFloat", inp={"A": "@entry.z", "B": str(BAND_CM)}); g.call("fl", K_MATH, "FFloor", inp={"A": "@dz.ReturnValue"}); g.link("fl.ReturnValue", "return.band")
    return fn("Map Band Of", [param("z", "float")], [param("band", "int")], graph=g, pure=True)


def f_key():
    """File key of a tile: "<band>_<x>_<y>", band OUT_BAND as "O"."""
    g = G()
    g.call("bs", K_STR, "Conv_IntToString", inp={"InInt": "@entry.band"}); g.call("isO", K_MATH, "EqualEqual_IntInt", inp={"A": "@entry.band", "B": str(OUT_BAND)})
    g.call("b", K_MATH, "SelectString", inp={"A": "O", "B": "@bs.ReturnValue", "bPickA": "@isO.ReturnValue"})
    g.call("xs", K_STR, "Conv_IntToString", inp={"InInt": "@entry.x"}); g.call("ys", K_STR, "Conv_IntToString", inp={"InInt": "@entry.y"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@b.ReturnValue", "B": "_"}); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@xs.ReturnValue"})
    g.call("c3", K_STR, "Concat_StrStr", inp={"A": "@c2.ReturnValue", "B": "_"}); g.call("c4", K_STR, "Concat_StrStr", inp={"A": "@c3.ReturnValue", "B": "@ys.ReturnValue"})
    g.link("c4.ReturnValue", "return.key")
    return fn("Map Key", [param("band", "int"), param("x", "int"), param("y", "int")], [param("key", "string")], graph=g, pure=True)


def f_tile_of():
    """The tile a world point lies in."""
    g = G(); g.call("bv", K_MATH, "BreakVector", inp={"InVec": "@entry.v"})
    for a in ("X", "Y"):
        g.call("d" + a, K_MATH, "Divide_FloatFloat", inp={"A": "@bv.%s" % a, "B": str(TILE_CM)}); g.call("f" + a, K_MATH, "FFloor", inp={"A": "@d%s.ReturnValue" % a})
        g.link("f%s.ReturnValue" % a, "return.%s" % a.lower())
    return fn("Map Tile Of", [param("v", S_VEC)], [param("x", "int"), param("y", "int")], graph=g, pure=True)


def f_to_screen():
    """World (wx, wy) -> map pixel (sx, sy) for the view MapCX / MapCY / MapPx (pixels per tile): up = +X, right = +Y."""
    g = G(); g.get("gp", "MapPx"); g.call("p", K_MATH, "Divide_FloatFloat", inp={"A": "@gp.MapPx", "B": str(TILE_CM)})
    g.get("gcy", "MapCY"); g.call("dy", K_MATH, "Subtract_FloatFloat", inp={"A": "@entry.wy", "B": "@gcy.MapCY"}); g.call("my", K_MATH, "Multiply_FloatFloat", inp={"A": "@dy.ReturnValue", "B": "@p.ReturnValue"})
    g.call("sx", K_MATH, "Add_FloatFloat", inp={"A": "@my.ReturnValue", "B": _half(g, "hw", "MapW")})
    g.get("gcx", "MapCX"); g.call("dx", K_MATH, "Subtract_FloatFloat", inp={"A": "@entry.wx", "B": "@gcx.MapCX"}); g.call("mx", K_MATH, "Multiply_FloatFloat", inp={"A": "@dx.ReturnValue", "B": "@p.ReturnValue"})
    g.call("sy", K_MATH, "Subtract_FloatFloat", inp={"A": _half(g, "hh", "MapH"), "B": "@mx.ReturnValue"})
    g.link("sx.ReturnValue", "return.sx"); g.link("sy.ReturnValue", "return.sy")
    return fn("Map To Screen", [param("wx", "float"), param("wy", "float")], [param("sx", "float"), param("sy", "float")], graph=g, pure=True)


def f_to_world():
    """Map pixel (sx, sy) -> world (wx, wy), the inverse of Map To Screen."""
    g = G(); g.get("gp", "MapPx"); g.call("p", K_MATH, "Divide_FloatFloat", inp={"A": "@gp.MapPx", "B": str(TILE_CM)})
    g.call("oy", K_MATH, "Subtract_FloatFloat", inp={"A": "@entry.sy", "B": _half(g, "hh", "MapH")}); g.call("cy", K_MATH, "Divide_FloatFloat", inp={"A": "@oy.ReturnValue", "B": "@p.ReturnValue"})
    g.get("gcx", "MapCX"); g.call("wx", K_MATH, "Subtract_FloatFloat", inp={"A": "@gcx.MapCX", "B": "@cy.ReturnValue"})
    g.call("ox", K_MATH, "Subtract_FloatFloat", inp={"A": "@entry.sx", "B": _half(g, "hw", "MapW")}); g.call("cx", K_MATH, "Divide_FloatFloat", inp={"A": "@ox.ReturnValue", "B": "@p.ReturnValue"})
    g.get("gcy", "MapCY"); g.call("wy", K_MATH, "Add_FloatFloat", inp={"A": "@gcy.MapCY", "B": "@cx.ReturnValue"})
    g.link("wx.ReturnValue", "return.wx"); g.link("wy.ReturnValue", "return.wy")
    return fn("Map To World", [param("sx", "float"), param("sy", "float")], [param("wx", "float"), param("wy", "float")], graph=g, pure=True)


def f_mark_spot():
    """A marker at world point v (z = its feet / floor): shown on the map? (outside view: every band; else its band is the shown one,
    and the point lies on the map area) and where (sx, sy)."""
    g = G(); g.call("bv", K_MATH, "BreakVector", inp={"InVec": "@entry.v"})
    g.n("sc", "call_self", function="Map To Screen", inp={"wx": "@bv.X", "wy": "@bv.Y"})
    # its height within the shown band, with the margin Jodi's own band has (Map Band Next): her band keeps while her feet are up to
    # BAND_HYST outside it, so a figure on her floor could fall into the next band by plain floor(z / BAND_CM) and had no marker
    # (play test 2026-11-21: spawned enemies without dots)
    g.get("gsb", "MapShowBand"); g.call("bf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@gsb.MapShowBand"}); g.call("lo0", K_MATH, "Multiply_FloatFloat", inp={"A": "@bf.ReturnValue", "B": str(BAND_CM)})
    g.call("lo", K_MATH, "Subtract_FloatFloat", inp={"A": "@lo0.ReturnValue", "B": str(BAND_HYST)}); g.call("hi", K_MATH, "Add_FloatFloat", inp={"A": "@lo0.ReturnValue", "B": str(BAND_CM + BAND_HYST)})
    g.call("zge", K_MATH, "GreaterEqual_FloatFloat", inp={"A": "@bv.Z", "B": "@lo.ReturnValue"}); g.call("zlt", K_MATH, "Less_FloatFloat", inp={"A": "@bv.Z", "B": "@hi.ReturnValue"})
    g.call("eqb", K_MATH, "BooleanAND", inp={"A": "@zge.ReturnValue", "B": "@zlt.ReturnValue"}); g.call("out", K_MATH, "EqualEqual_IntInt", inp={"A": "@gsb.MapShowBand", "B": str(OUT_BAND)})
    g.call("bnd", K_MATH, "BooleanOR", inp={"A": "@eqb.ReturnValue", "B": "@out.ReturnValue"})
    g.get("gmw", "MapW"); g.get("gmh", "MapH")
    g.call("ix", K_MATH, "InRange_FloatFloat", inp={"Value": "@sc.sx", "Min": "0.0", "Max": "@gmw.MapW", "InclusiveMin": "true", "InclusiveMax": "true"})
    g.call("iy", K_MATH, "InRange_FloatFloat", inp={"Value": "@sc.sy", "Min": "0.0", "Max": "@gmh.MapH", "InclusiveMin": "true", "InclusiveMax": "true"})
    g.call("in", K_MATH, "BooleanAND", inp={"A": "@ix.ReturnValue", "B": "@iy.ReturnValue"}); g.call("ok", K_MATH, "BooleanAND", inp={"A": "@in.ReturnValue", "B": "@bnd.ReturnValue"})
    g.link("ok.ReturnValue", "return.ok"); g.link("sc.sx", "return.sx"); g.link("sc.sy", "return.sy")
    return fn("Map Mark Spot", [param("v", S_VEC)], [param("ok", "bool"), param("sx", "float"), param("sy", "float")], graph=g, pure=True)


def f_feet():
    """Jodi's feet: her location minus the capsule half height."""
    g = G(); g.get("gpl", "Player"); g.call("loc", E_ACTOR, "K2_GetActorLocation", inp={"self": "@gpl.Player"})
    g.get("gpl2", "Player"); g.get("gcap", "CapsuleComponent", cls=E_CHAR); g.link("gpl2.Player", "gcap.self")
    g.call("hh", E_CAPS, "GetScaledCapsuleHalfHeight", inp={"self": "@gcap.CapsuleComponent"}); g.call("hv", K_MATH, "MakeVector", inp={"X": "0.0", "Y": "0.0", "Z": "@hh.ReturnValue"})
    g.call("ft", K_MATH, "Subtract_VectorVector", inp={"A": "@loc.ReturnValue", "B": "@hv.ReturnValue"}); g.link("ft.ReturnValue", "return.feet"); g.link("hh.ReturnValue", "return.half")
    return fn("Map Jodi Feet", outputs=[param("feet", S_VEC), param("half", "float")], graph=g, pure=True)


def f_jodi_band():
    """The band of Jodi's place: OUT_BAND outside, else MapBand."""
    g = G(); g.get("go", "MapOut"); g.get("gb", "MapBand")
    g.call("s", K_MATH, "SelectInt", inp={"A": str(OUT_BAND), "B": "@gb.MapBand", "bPickA": "@go.MapOut"}); g.link("s.ReturnValue", "return.band")
    return fn("Map Jodi Band", outputs=[param("band", "int")], graph=g, pure=True)


# ---------------- recording ----------------
def f_update_band():
    """Jodi's band (MapBand, hysteresis), her feet height (MapFeetZ) and whether she is outside (MapOut: a line up from her head hits
    nothing within SKY_CM). Needs a valid Player."""
    g = G(); g.n("ft", "call_self", function="Map Jodi Feet"); g.call("fb", K_MATH, "BreakVector", inp={"InVec": "@ft.feet"})
    g.set("sz", "MapFeetZ", inp={"MapFeetZ": "@fb.Z"})
    g.get("gb", "MapBand"); g.get("gh", "MapBandSet"); g.n("bn", "call_self", function="Map Band Next", inp={"cur": "@gb.MapBand", "has": "@gh.MapBandSet", "z": "@fb.Z"})
    g.set("sb", "MapBand", inp={"MapBand": "@bn.band"}); g.set("sh", "MapBandSet", inp={"MapBandSet": "true"})
    g.get("gpl", "Player"); g.call("loc", E_ACTOR, "K2_GetActorLocation", inp={"self": "@gpl.Player"})
    g.call("hv", K_MATH, "MakeVector", inp={"X": "0.0", "Y": "0.0", "Z": "@ft.half"}); g.call("head", K_MATH, "Add_VectorVector", inp={"A": "@loc.ReturnValue", "B": "@hv.ReturnValue"})
    g.call("end", K_MATH, "Add_VectorVector", inp={"A": "@head.ReturnValue", "B": "(X=0,Y=0,Z=%d)" % SKY_CM})
    g.get("gpl2", "Player"); g.n("ign", "make_array", count=1, type="object:" + E_ACTOR, inp={"[0]": "@gpl2.Player"})
    g.call("tr", K_SYS, "LineTraceSingle", inp={"Start": "@head.ReturnValue", "End": "@end.ReturnValue", "TraceChannel": "TraceTypeQuery1", "bTraceComplex": "false",
                                                "ActorsToIgnore": "@ign.Array", "DrawDebugType": "None", "bIgnoreSelf": "true",
                                                "TraceColor": "(R=1,G=0,B=0,A=1)", "TraceHitColor": "(R=0,G=1,B=0,A=1)", "DrawTime": "5.0"})
    g.call("no", K_MATH, "Not_PreBool", inp={"A": "@tr.ReturnValue"}); g.set("so", "MapOut", inp={"MapOut": "@no.ReturnValue"})
    g.chain("entry", "sz", "sb", "sh", "tr", "so")
    return fn("Map Update Band", graph=g)


def f_level():
    """MapLevel = the level's name (GetCurrentLevelName is not pure in 4.27: here on the exec chain)."""
    g = G(); g.call("lvl", K_GS, "GetCurrentLevelName", inp={"bRemovePrefixString": "true"}); g.set("s", "MapLevel", inp={"MapLevel": "@lvl.ReturnValue"})
    g.chain("entry", "lvl", "s")
    return fn("Map Read Level", graph=g)


def f_dir():
    """Folder of this level's tiles in one style: <Saved>/SaveGames/AltUI/Map/<level>/<base|lit|surfaces>/."""
    g = G(); g.call("sd", K_PATHS, "ProjectSavedDir"); g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@sd.ReturnValue", "B": MAP_DIR})
    g.get("gl", "MapLevel"); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@gl.MapLevel"}); g.call("c3", K_STR, "Concat_StrStr", inp={"A": "@c2.ReturnValue", "B": "/"})
    pin = STYLE_DIRS[0] + "/"
    for i in range(1, len(STYLE_DIRS)):
        g.call("se%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": "@entry.style", "B": str(i)})
        g.call("ss%d" % i, K_MATH, "SelectString", inp={"A": STYLE_DIRS[i] + "/", "B": pin, "bPickA": "@se%d.ReturnValue" % i}); pin = "@ss%d.ReturnValue" % i
    g.call("c4", K_STR, "Concat_StrStr", inp={"A": "@c3.ReturnValue", "B": pin})
    g.link("c4.ReturnValue", "return.dir")
    return fn("Map Dir", [param("style", "int")], outputs=[param("dir", "string")], graph=g, pure=True)


def f_capture_tile():
    """Tile (x, y) of `band`: an orthographic SceneCapture2D over its middle, looking straight down from CUT_IN (inside) / CUT_OUT
    (outside) above Jodi's feet, every Character hidden (no figures burnt into the map). One depth capture, then the tile in all three
    styles (STYLES), each made one picture with the depth by M_MapCombine into MapRT and exported as <Map Dir(style)><key>.png - a
    style switch shows the whole recorded map at once. The actor goes again. The tile counts as done for this session; its cached
    texture is dropped (reloaded).
    "lit" is the scene's HDR colour: a scene capture has no eye adaptation (its fixed exposure is 0.18 / the middle of the level's
    auto-exposure range - a dark level came out black, play test 2026-11-19), so it is brought to the level's brightness by a gain:
    LIT_BOOST x mean base colour / mean lit (M_MapMean over the tile, read back from a 1 x 1 RGBA16f target: ReadRenderTargetRawPixel
    reads only 8 bit and 16f - RGBA32f returned red, the gain fell back to LIT_BOOST, play test round 2), taken from the first
    tile with light and kept per level and inside / outside (MapLitGain, saved) - the tiles fit together."""
    g = G()
    g.get("grt", "MapRT"); g.call("rv", K_SYS, "IsValid", inp={"Object": "@grt.MapRT"}); g.branch("brv", "@rv.ReturnValue")
    # RTF_RGBA8_SRGB: the PNG export is as bright as the picture (Capture Photo)
    def rt(i, var_, fmt, size=TILE_PX, clear="(R=0,G=0,B=0,A=1)"):
        g.call("c" + i, K_REND, "CreateRenderTarget2D", inp={"Width": str(size), "Height": str(size), "Format": fmt, "ClearColor": clear, "bAutoGenerateMipMaps": "false"})
        g.set("s" + i, var_, inp={var_: "@c%s.ReturnValue" % i}); return ["c" + i, "s" + i]
    mk = rt("rt", "MapRT", "RTF_RGBA8_SRGB") + rt("cr", "MapColRT", "RTF_RGBA8_SRGB") + rt("hd", "MapHdrRT", "RTF_RGBA16f") + \
         rt("dr", "MapDepRT", "RTF_R32f", clear="(R=100000,G=0,B=0,A=1)") + rt("mr", "MapMeanRT", "RTF_RGBA16f", size=1)
    # M_MapCombine makes one picture of colour and depth (rooms readable: what lies below Jodi's floor dark, edges where the height
    # jumps drawn as lines); M_MapMean the brightness for "lit"
    g.call("mid", K_MATLIB, "CreateDynamicMaterialInstance", inp={"Parent": M_MAPCOMBINE, "OptionalName": "None"}); g.set("smid", "MapMID", inp={"MapMID": "@mid.ReturnValue"})
    g.call("mmi", K_MATLIB, "CreateDynamicMaterialInstance", inp={"Parent": M_MAPMEAN, "OptionalName": "None"}); g.set("smmi", "MapMeanMID", inp={"MapMeanMID": "@mmi.ReturnValue"})
    mk += ["mid", "smid", "mmi", "smmi"]
    g.call("isO", K_MATH, "EqualEqual_IntInt", inp={"A": "@entry.band", "B": str(OUT_BAND)}); g.call("cut", K_MATH, "SelectFloat", inp={"A": str(CUT_OUT), "B": str(CUT_IN), "bPickA": "@isO.ReturnValue"})
    g.get("gfz", "MapFeetZ"); g.call("cz", K_MATH, "Add_FloatFloat", inp={"A": "@gfz.MapFeetZ", "B": "@cut.ReturnValue"})
    for a in ("x", "y"):
        g.call("f" + a, K_MATH, "Conv_IntToFloat", inp={"InInt": "@entry.%s" % a}); g.call("m" + a, K_MATH, "Multiply_FloatFloat", inp={"A": "@f%s.ReturnValue" % a, "B": str(TILE_CM)})
        g.call("c" + a, K_MATH, "Add_FloatFloat", inp={"A": "@m%s.ReturnValue" % a, "B": str(TILE_CM / 2)})
    g.call("loc", K_MATH, "MakeVector", inp={"X": "@cx.ReturnValue", "Y": "@cy.ReturnValue", "Z": "@cz.ReturnValue"})
    # straight down - a MakeRotator node: a rotator pin default only takes "P=.. Y=.. R=.." (FRotator::InitFromString), "(Pitch=-90,..)"
    # was dropped without a word and the camera looked level (play test 2026-11-17: mountain silhouettes, the tower's facade)
    g.call("down", K_MATH, "MakeRotator", inp={"Roll": "0.0", "Pitch": "-90.0", "Yaw": "0.0"})
    g.call("tf", K_MATH, "MakeTransform", inp={"Location": "@loc.ReturnValue", "Rotation": "@down.ReturnValue", "Scale": "(X=1,Y=1,Z=1)"})
    g.n("sp", "spawn", cls=E_SCAP, inp={"SpawnTransform": "@tf.ReturnValue"})
    g.get("gc", "CaptureComponent2D", cls=E_SCAP); g.link("sp.ReturnValue", "gc.self"); c = "@gc.CaptureComponent2D"
    g.n("se", "set", var="bCaptureEveryFrame", cls=E_SCAPC, inp={"self": c, "bCaptureEveryFrame": "false"})
    g.n("sm", "set", var="bCaptureOnMovement", cls=E_SCAPC, inp={"self": c, "bCaptureOnMovement": "false"})
    g.n("spj", "set", var="ProjectionType", cls=E_SCAPC, inp={"self": c, "ProjectionType": "Orthographic"})
    g.n("sow", "set", var="OrthoWidth", cls=E_SCAPC, inp={"self": c, "OrthoWidth": str(TILE_CM)})
    g.get("gpl", "Player"); g.get("gcam", "Camera", cls="/Game/Project/Character/Jodi/Jodi"); g.link("gpl.Player", "gcam.self")
    g.get("pps", "PostProcessSettings", cls=E_CAMC); g.link("gcam.Camera", "pps.self")
    g.n("spp", "set", var="PostProcessSettings", cls=E_SCAPC, inp={"self": c, "PostProcessSettings": "@pps.PostProcessSettings"})
    g.n("spw", "set", var="PostProcessBlendWeight", cls=E_SCAPC, inp={"self": c, "PostProcessBlendWeight": "1.0"})
    g.call("all", K_GS, "GetAllActorsOfClass", inp={"ActorClass": E_CHAR}); g.foreach("fe", "@all.OutActors")
    g.call("hide", E_SCAPCB, "HideActorComponents", inp={"self": c, "InActor": "@fe.Array Element", "bIncludeFromChildActors": "true"})
    tail = ["fe:Completed"]
    def capture(p, src, target):
        g.n(p + "src", "set", var="CaptureSource", cls=E_SCAPC, inp={"self": c, "CaptureSource": src})
        g.get(p + "tg", target); g.n(p + "st", "set", var="TextureTarget", cls=E_SCAPC, inp={"self": c, "TextureTarget": "@%stg.%s" % (p, target)})
        g.call(p + "cap", E_SCAPC, "CaptureScene", inp={"self": c}); tail.extend([p + "src", p + "st", p + "cap"])
    capture("d", "SCS_SceneDepth", "MapDepRT")
    def picture(i, col, gain, lit):
        p = "s%d" % i
        g.get(p + "mi", "MapMID"); g.get(p + "cr", col); g.get(p + "dr", "MapDepRT"); mi = "@%smi.MapMID" % p
        g.call(p + "pc", MID, "SetTextureParameterValue", inp={"self": mi, "ParameterName": "Col", "Value": "@%scr.%s" % (p, col)})
        g.call(p + "pd", MID, "SetTextureParameterValue", inp={"self": mi, "ParameterName": "Depth", "Value": "@%sdr.MapDepRT" % p})
        g.call(p + "pcut", MID, "SetScalarParameterValue", inp={"self": mi, "ParameterName": "Cut", "Value": "@cut.ReturnValue"})
        g.call(p + "pis", MID, "SetScalarParameterValue", inp={"self": mi, "ParameterName": "Inside", "Value": "@pin.ReturnValue"})
        g.call(p + "pg", MID, "SetScalarParameterValue", inp={"self": mi, "ParameterName": "Gain", "Value": gain})
        g.call(p + "pl", MID, "SetScalarParameterValue", inp={"self": mi, "ParameterName": "Lit", "Value": lit})
        g.call(p + "pn", MID, "SetScalarParameterValue", inp={"self": mi, "ParameterName": "Nrm", "Value": "1.0" if i == 2 else "0.0"})   # "surfaces": lower floors dimmed as normals, not as a colour (M_MapCombine)
        # the PNG opaque: M_MapCombine is AlphaComposite with opacity 0 - it adds its colour and leaves the target's alpha alone, so the
        # target is cleared to black, alpha 1 first. (An opaque material wrote alpha 0: the tiles looked empty in every image viewer.)
        g.get(p + "rt0", "MapRT"); g.call(p + "clr", K_REND, "ClearRenderTarget2D", inp={"TextureRenderTarget": "@%srt0.MapRT" % p, "ClearColor": "(R=0,G=0,B=0,A=1)"})
        g.get(p + "rt", "MapRT"); g.call(p + "drw", K_REND, "DrawMaterialToRenderTarget", inp={"TextureRenderTarget": "@%srt.MapRT" % p, "Material": mi})
        g.n(p + "dir", "call_self", function="Map Dir", inp={"style": str(i)})
        g.get(p + "rt2", "MapRT"); g.call(p + "ex", K_REND, "ExportRenderTarget", inp={"TextureRenderTarget": "@%srt2.MapRT" % p, "FilePath": "@%sdir.dir" % p, "FileName": "@fn.ReturnValue"})
        tail.extend([p + "pc", p + "pd", p + "pcut", p + "pis", p + "pg", p + "pl", p + "pn", p + "clr", p + "drw", p + "ex"])
    g.call("pin", K_MATH, "SelectFloat", inp={"A": "0.0", "B": "1.0", "bPickA": "@isO.ReturnValue"})
    g.n("key", "call_self", function="Map Key", inp={"band": "@entry.band", "x": "@entry.x", "y": "@entry.y"})
    g.call("fn", K_STR, "Concat_StrStr", inp={"A": "@key.key", "B": MAP_EXT})
    # Options > Map "Only take pictures for the active map style" (MapOneStyle): a style is taken when the option is off or it is the
    # shown one (bw<i>); the base colour is captured for "lit" too (its gain), only its picture is left out
    g.get("gos", "MapOneStyle"); g.call("all3", K_MATH, "Not_PreBool", inp={"A": "@gos.MapOneStyle"}); g.get("gcs", "MapStyle")
    for i in range(len(STYLES)):
        g.call("is%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": "@gcs.MapStyle", "B": str(i)}); g.call("w%d" % i, K_MATH, "BooleanOR", inp={"A": "@all3.ReturnValue", "B": "@is%d.ReturnValue" % i})
        g.branch("bw%d" % i, "@w%d.ReturnValue" % i)
    # 0 base colour
    capture("b", STYLES[0], "MapColRT"); tail.append("bw0"); picture(0, "MapColRT", "1.0", "0.0"); tail.append("bw1"); g.chain(*tail); g.chain("bw0:else", "bw1"); tail[:] = ["bw1"]
    # 1 lit: HDR capture, its gain (MapColRT still holds the base colour)
    capture("l", STYLES[1], "MapHdrRT")
    g.get("mn", "MapMeanMID"); g.get("mnh", "MapHdrRT"); g.get("mnc", "MapColRT")
    g.call("mna", MID, "SetTextureParameterValue", inp={"self": "@mn.MapMeanMID", "ParameterName": "A", "Value": "@mnh.MapHdrRT"})
    g.call("mnb", MID, "SetTextureParameterValue", inp={"self": "@mn.MapMeanMID", "ParameterName": "B", "Value": "@mnc.MapColRT"})
    g.get("mnr", "MapMeanRT"); g.call("mnd", K_REND, "DrawMaterialToRenderTarget", inp={"TextureRenderTarget": "@mnr.MapMeanRT", "Material": "@mn.MapMeanMID"})
    g.get("mnr2", "MapMeanRT"); g.call("mrp", K_REND, "ReadRenderTargetRawPixel", inp={"TextureRenderTarget": "@mnr2.MapMeanRT", "X": "0", "Y": "0"})
    g.call("mbk", K_MATH, "BreakColor", inp={"InColor": "@mrp.ReturnValue"})
    g.call("rmx", K_MATH, "FMax", inp={"A": "@mbk.R", "B": "0.000001"}); g.call("rat", K_MATH, "Divide_FloatFloat", inp={"A": "@mbk.G", "B": "@rmx.ReturnValue"})
    g.call("rbo", K_MATH, "Multiply_FloatFloat", inp={"A": "@rat.ReturnValue", "B": str(LIT_BOOST)})
    g.call("rcl", K_MATH, "FClamp", inp={"Value": "@rbo.ReturnValue", "Min": "0.05", "Max": "5000.0"})
    g.call("vr", K_MATH, "Greater_FloatFloat", inp={"A": "@mbk.R", "B": "0.000001"}); g.call("vg", K_MATH, "Greater_FloatFloat", inp={"A": "@mbk.G", "B": "0.005"})
    g.call("vok", K_MATH, "BooleanAND", inp={"A": "@vr.ReturnValue", "B": "@vg.ReturnValue"})
    g.call("ksu", K_MATH, "SelectString", inp={"A": "/O", "B": "/I", "bPickA": "@isO.ReturnValue"})
    g.get("glv", "MapLevel"); g.call("gky", K_STR, "Concat_StrStr", inp={"A": "@glv.MapLevel", "B": "@ksu.ReturnValue"})
    g.get("glg", "MapLitGain"); g.call("lgf", K_MAP, "Map_Find", inp={"TargetMap": "@glg.MapLitGain", "Key": "@gky.ReturnValue"})
    g.call("gtl", K_MATH, "SelectFloat", inp={"A": "@rcl.ReturnValue", "B": str(LIT_BOOST), "bPickA": "@vok.ReturnValue"})
    g.call("gai", K_MATH, "SelectFloat", inp={"A": "@lgf.Value", "B": "@gtl.ReturnValue", "bPickA": "@lgf.ReturnValue"})
    g.branch("blg", "@lgf.ReturnValue"); g.branch("bvk", "@vok.ReturnValue")
    g.get("glg2", "MapLitGain"); g.call("lga", K_MAP, "Map_Add", inp={"TargetMap": "@glg2.MapLitGain", "Key": "@gky.ReturnValue", "Value": "@rcl.ReturnValue"})
    g.n("lsv", "call_self", function="Save Settings")
    tail.extend(["mna", "mnb", "mnd", "mrp", "blg"]); g.chain(*tail); g.chain("blg:else", "bvk", "lga", "lsv")
    tail[:] = ["blg"]; picture(1, "MapHdrRT", "@gai.ReturnValue", "1.0")
    g.chain("bvk:else", "s1pc"); g.chain("lsv", "s1pc")
    tail.append("bw2"); g.chain(*tail); g.chain("bw1:else", "bw2"); tail[:] = ["bw2"]
    # 2 surfaces (normals; shaded grey in M_MapTile)
    capture("n", STYLES[2], "MapColRT"); picture(2, "MapColRT", "1.0", "0.0"); g.chain("bw2:else", "ds")
    g.call("ds", E_ACTOR, "K2_DestroyActor", inp={"self": "@sp.ReturnValue"})
    g.get("gd", "MapDone"); g.call("ad", K_MAP, "Map_Add", inp={"TargetMap": "@gd.MapDone", "Key": "@key.key", "Value": g.lit_bool("lt", "true")})
    g.get("gdz", "MapDoneZ"); g.get("gfz2", "MapFeetZ"); g.call("adz", K_MAP, "Map_Add", inp={"TargetMap": "@gdz.MapDoneZ", "Key": "@key.key", "Value": "@gfz2.MapFeetZ"})
    g.get("gt", "MapTex"); g.call("rt", K_MAP, "Map_Remove", inp={"TargetMap": "@gt.MapTex", "Key": "@key.key"})
    g.get("gm", "MapMiss"); g.call("rm", K_MAP, "Map_Remove", inp={"TargetMap": "@gm.MapMiss", "Key": "@key.key"})
    tail.extend(["ds", "ad", "adz", "rt", "rm"]); g.chain(*tail)
    g.chain("entry", "brv", "sp"); g.chain("brv:else", *mk, "sp")
    g.chain("sp", "se", "sm", "spj", "sow", "spp", "spw", "all", "fe", "hide")
    return fn("Map Capture Tile", [param("x", "int"), param("y", "int"), param("band", "int")], graph=g)


def f_capture_next():
    """One tile per call: Jodi's own, then her eight neighbours - the first not captured in this session (MapDone) for her band. Once
    per session (taking them again in turn made the game stutter, play test 2026-11-19); new light: Map Retake."""
    g = G(); g.n("ft", "call_self", function="Map Jodi Feet"); g.n("to", "call_self", function="Map Tile Of", inp={"v": "@ft.feet"}); g.n("jb", "call_self", function="Map Jodi Band")
    g.get("gfz", "MapFeetZ"); g.call("isout", K_MATH, "EqualEqual_IntInt", inp={"A": "@jb.band", "B": str(OUT_BAND)})
    prev = "entry"
    for i, (dx, dy) in enumerate(NEIGHBOURS):
        g.call("x%d" % i, K_MATH, "Add_IntInt", inp={"A": "@to.x", "B": str(dx)}); g.call("y%d" % i, K_MATH, "Add_IntInt", inp={"A": "@to.y", "B": str(dy)})
        g.n("k%d" % i, "call_self", function="Map Key", inp={"band": "@jb.band", "x": "@x%d.ReturnValue" % i, "y": "@y%d.ReturnValue" % i})
        g.get("gd%d" % i, "MapDone"); g.call("h%d" % i, K_MAP, "Map_Contains", inp={"TargetMap": "@gd%d.MapDone" % i, "Key": "@k%d.key" % i})
        # inside, a tile is a cut CUT_IN above the feet it was taken from: taken on the stairs (the band changes there) it shows the
        # floor below, and stayed so for the session - until the panel opened (it takes her tile). Taken again once her feet are
        # more than Z_TOL from that height (play test 2026-11-21: the minimap kept the old floor)
        g.get("gz%d" % i, "MapDoneZ"); g.call("fz%d" % i, K_MAP, "Map_Find", inp={"TargetMap": "@gz%d.MapDoneZ" % i, "Key": "@k%d.key" % i})
        g.call("dz%d" % i, K_MATH, "Subtract_FloatFloat", inp={"A": "@fz%d.Value" % i, "B": "@gfz.MapFeetZ"}); g.call("az%d" % i, K_MATH, "Abs", inp={"A": "@dz%d.ReturnValue" % i})
        g.call("nz%d" % i, K_MATH, "LessEqual_FloatFloat", inp={"A": "@az%d.ReturnValue" % i, "B": str(Z_TOL)}); g.call("oz%d" % i, K_MATH, "BooleanOR", inp={"A": "@nz%d.ReturnValue" % i, "B": "@isout.ReturnValue"})
        g.call("t%d" % i, K_MATH, "BooleanAND", inp={"A": "@h%d.ReturnValue" % i, "B": "@oz%d.ReturnValue" % i}); g.branch("b%d" % i, "@t%d.ReturnValue" % i)
        g.n("c%d" % i, "call_self", function="Map Capture Tile", inp={"x": "@x%d.ReturnValue" % i, "y": "@y%d.ReturnValue" % i, "band": "@jb.band"})
        g.chain(prev, "b%d" % i); g.chain("b%d:else" % i, "c%d" % i); prev = "b%d" % i   # taken: done for this call
    return fn("Map Capture Next", graph=g)


def f_tick():
    """Every frame (manager tick, not while paused): every CAPTURE_EVERY seconds, with recording on and Jodi alive, her band and one
    tile (Map Capture Next)."""
    g = G(); g.get("gpl", "Player"); g.call("pv", K_SYS, "IsValid", inp={"Object": "@gpl.Player"}); g.branch("bpv", "@pv.ReturnValue")
    g.get("gnr", "MapNoRecord"); g.branch("bnr", "@gnr.MapNoRecord")
    g.call("now", K_GS, "GetRealTimeSeconds"); g.get("gnx", "MapNext"); g.call("due", K_MATH, "GreaterEqual_FloatFloat", inp={"A": "@now.ReturnValue", "B": "@gnx.MapNext"}); g.branch("bdu", "@due.ReturnValue")
    g.call("nx", K_MATH, "Add_FloatFloat", inp={"A": "@now.ReturnValue", "B": str(CAPTURE_EVERY)}); g.set("snx", "MapNext", inp={"MapNext": "@nx.ReturnValue"})
    g.get("gpl2", "Player"); g.call("al", "/Game/Project/Character/Jodi/Jodi", "Is Alive ?", inp={"self": "@gpl2.Player"}); g.branch("bal", "@al.yes")
    g.get("glv", "MapLevel"); g.call("lvl", K_STR, "Len", inp={"S": "@glv.MapLevel"}); g.call("nol", K_MATH, "EqualEqual_IntInt", inp={"A": "@lvl.ReturnValue", "B": "0"}); g.branch("bnl", "@nol.ReturnValue")
    g.n("rl", "call_self", function="Map Read Level")
    g.n("ub", "call_self", function="Map Update Band"); g.n("cn", "call_self", function="Map Capture Next")
    g.get("gof", "MapOff"); g.branch("bof", "@gof.MapOff")   # the map off: nothing at all
    g.chain("entry", "bof"); g.chain("bof:else", "bpv", "bnr"); g.chain("bnr:else", "bdu", "snx", "bal", "bnl", "rl", "ub", "cn"); g.chain("bnl:else", "ub")
    return fn("Map Tick", graph=g)


# ---------------- view ----------------
def f_tile_tex():
    """Texture of tile `key` of this level: cached (MapTex), known missing (MapMiss: None), else its PNG imported (FileExists first)."""
    g = G(); g.get("gt", "MapTex"); g.call("fd", K_MAP, "Map_Find", inp={"TargetMap": "@gt.MapTex", "Key": "@entry.key"}); g.branch("bfd", "@fd.ReturnValue")
    g.link("fd.Value", "return.tex")
    g.get("gm", "MapMiss"); g.call("ms", K_MAP, "Map_Contains", inp={"TargetMap": "@gm.MapMiss", "Key": "@entry.key"}); g.branch("bms", "@ms.ReturnValue")
    g.n("r1", "return_new", inp={"tex": "None"})
    g.get("gst", "MapStyle"); g.n("dir", "call_self", function="Map Dir", inp={"style": "@gst.MapStyle"}); g.call("p1", K_STR, "Concat_StrStr", inp={"A": "@dir.dir", "B": "@entry.key"}); g.call("p2", K_STR, "Concat_StrStr", inp={"A": "@p1.ReturnValue", "B": MAP_EXT})
    g.call("ex", K_PATHS, "FileExists", inp={"InPath": "@p2.ReturnValue"}); g.branch("bex", "@ex.ReturnValue")
    g.call("imp", K_REND, "ImportFileAsTexture2D", inp={"Filename": "@p2.ReturnValue"}); g.call("iv", K_SYS, "IsValid", inp={"Object": "@imp.ReturnValue"}); g.branch("biv", "@iv.ReturnValue")
    g.get("gt2", "MapTex"); g.call("ad", K_MAP, "Map_Add", inp={"TargetMap": "@gt2.MapTex", "Key": "@entry.key", "Value": "@imp.ReturnValue"})
    g.n("r2", "return_new"); g.link("imp.ReturnValue", "r2.tex")
    g.get("gm2", "MapMiss"); g.call("am", K_MAP, "Map_Add", inp={"TargetMap": "@gm2.MapMiss", "Key": "@entry.key", "Value": g.lit_bool("lt", "true")})
    g.n("r3", "return_new", inp={"tex": "None"})
    g.chain("entry", "bfd", "return"); g.chain("bfd:else", "bms", "r1"); g.chain("bms:else", "bex", "imp", "biv", "ad", "r2"); g.chain("bex:else", "am", "r3"); g.chain("biv:else", "am")
    return fn("Map Tile Tex", [param("key", "string")], [param("tex", "object:" + E_TEX2D)], graph=g)


def _place(g, p, idx, x, y, size, angle="0.0", shown="true", center=True):
    """W_NavMap.Place of pool image `idx` at (x, y) (its middle when center) with `size`; returns the exec id."""
    if center:
        g.call(p + "hx", K_MATH, "Subtract_FloatFloat", inp={"A": x, "B": str(size / 2.0)}); g.call(p + "hy", K_MATH, "Subtract_FloatFloat", inp={"A": y, "B": str(size / 2.0)})
        x, y = "@%shx.ReturnValue" % p, "@%shy.ReturnValue" % p
    g.get(p + "v", "MapView")
    g.call(p, W_NAVMAP, "Place", inp={"self": "@%sv.MapView" % p, "index": idx, "x": x, "y": y, "w": str(float(size)), "h": str(float(size)), "angle": angle, "shown": shown})
    return p


def _marks(g, p, arr, tex, col, size, zoff, head_after):
    """Markers for the actors of array pin `arr` (z of their feet = location z - zoff): foreach -> Map Mark Spot -> pool room left ->
    Place + Set Mark, MapMi + 1. Chains from `head_after`; returns the loop id (its Completed exit goes on)."""
    g.foreach(p + "fe", arr); g.call(p + "l", E_ACTOR, "K2_GetActorLocation", inp={"self": "@%sfe.Array Element" % p})
    g.call(p + "z", K_MATH, "Subtract_VectorVector", inp={"A": "@%sl.ReturnValue" % p, "B": "(X=0,Y=0,Z=%s)" % zoff})
    g.n(p + "ms", "call_self", function="Map Mark Spot", inp={"v": "@%sz.ReturnValue" % p})
    g.get(p + "gi", "MapMi"); g.call(p + "room", K_MATH, "Less_IntInt", inp={"A": "@%sgi.MapMi" % p, "B": str(CROSS)})
    g.call(p + "ok", K_MATH, "BooleanAND", inp={"A": "@%sms.ok" % p, "B": "@%sroom.ReturnValue" % p}); g.branch(p + "b", "@%sok.ReturnValue" % p)
    angle = "0.0"
    if tex == T_BED:   # a bed lies the way it stands
        g.call(p + "rot", E_ACTOR, "K2_GetActorRotation", inp={"self": "@%sfe.Array Element" % p}); g.call(p + "br", K_MATH, "BreakRotator", inp={"InRot": "@%srot.ReturnValue" % p}); angle = "@%sbr.Yaw" % p
    _place(g, p + "pl", "@%sgi.MapMi" % p, "@%sms.sx" % p, "@%sms.sy" % p, size, angle=angle)
    g.get(p + "v2", "MapView"); g.call(p + "sm", W_NAVMAP, "Set Mark", inp={"self": "@%sv2.MapView" % p, "index": "@%sgi.MapMi" % p, "tex": tex, "color": col})
    g.call(p + "inc", K_MATH, "Add_IntInt", inp={"A": "@%sgi.MapMi" % p, "B": "1"}); g.set(p + "si", "MapMi", inp={"MapMi": "@%sinc.ReturnValue" % p})
    if head_after: g.chain(head_after, p + "fe")
    g.chain(p + "fe", p + "b", p + "pl", p + "sm", p + "si")
    return p + "fe"


def _mark_one(g, p, actor, tex, col, size, after):
    """One figure's marker (z of its feet = location z - 90): Map Mark Spot -> pool room left -> Place + Set Mark, MapMi + 1;
    the exec comes from `after` (a branch: its then exit)."""
    g.call(p + "l", E_ACTOR, "K2_GetActorLocation", inp={"self": actor}); g.call(p + "z", K_MATH, "Subtract_VectorVector", inp={"A": "@%sl.ReturnValue" % p, "B": "(X=0,Y=0,Z=90)"})
    g.n(p + "ms", "call_self", function="Map Mark Spot", inp={"v": "@%sz.ReturnValue" % p})
    g.get(p + "gi", "MapMi"); g.call(p + "room", K_MATH, "Less_IntInt", inp={"A": "@%sgi.MapMi" % p, "B": str(CROSS)})
    g.call(p + "ok", K_MATH, "BooleanAND", inp={"A": "@%sms.ok" % p, "B": "@%sroom.ReturnValue" % p}); g.branch(p + "b", "@%sok.ReturnValue" % p)
    _place(g, p + "pl", "@%sgi.MapMi" % p, "@%sms.sx" % p, "@%sms.sy" % p, size)
    g.get(p + "v2", "MapView"); g.call(p + "sm", W_NAVMAP, "Set Mark", inp={"self": "@%sv2.MapView" % p, "index": "@%sgi.MapMi" % p, "tex": tex, "color": col})
    g.call(p + "inc", K_MATH, "Add_IntInt", inp={"A": "@%sgi.MapMi" % p, "B": "1"}); g.set(p + "si", "MapMi", inp={"MapMi": "@%sinc.ReturnValue" % p})
    g.chain(after, p + "b", p + "pl", p + "sm", p + "si")


def f_kind_of():
    """The marker kind of a figure (KIND_KEYS): Jodi and anything else 0; a zombie alive (Is Alive ?) K_ZOMBIE, else K_DEAD; a
    Character_NPC with health left: Jason K_HOSTILE, a follower (FolActors) K_FOL, else K_NPC - without health K_DEAD.
    A figure hidden in the game (bHidden) is 0 too: levels place zombies hidden until a trigger shows them (Character_Base.Change
    Character Visible: hidden, no tick, no collision) - they were red dots where nothing was (play test 2026-11-20)."""
    g = G(); g.get("gpl", "Player"); g.call("isp", K_MATH, "EqualEqual_ObjectObject", inp={"A": "@entry.actor", "B": "@gpl.Player"})
    g.get("ghd", "bHidden", cls=E_ACTOR); g.link("entry.actor", "ghd.self"); g.call("skip", K_MATH, "BooleanOR", inp={"A": "@isp.ReturnValue", "B": "@ghd.bHidden"})
    g.branch("bisp", "@skip.ReturnValue")
    g.n("r0", "return_new", inp={"kind": "0"})
    g.cast("cz", P_ZOMBIE, "@entry.actor"); g.call("vz", K_SYS, "IsValid", inp={"Object": "@cz.AsZombie Base"}); g.branch("bz", "@vz.ReturnValue")
    g.call("al", P_ZOMBIE, "Is Alive ?", inp={"self": "@cz.AsZombie Base"}); g.call("zk", K_MATH, "SelectInt", inp={"A": str(K_ZOMBIE), "B": str(K_DEAD), "bPickA": "@al.yes"})
    g.n("rz", "return_new"); g.link("zk.ReturnValue", "rz.kind")
    g.cast("cn", P_CNPC, "@entry.actor"); g.call("vn", K_SYS, "IsValid", inp={"Object": "@cn.AsCharacter NPC"}); g.branch("bn", "@vn.ReturnValue")
    g.n("r1", "return_new", inp={"kind": "0"})
    g.get("ghp", "Health", cls=P_CB); g.link("cn.AsCharacter NPC", "ghp.self"); g.call("hp", K_MATH, "Greater_FloatFloat", inp={"A": "@ghp.Health", "B": "0.0"}); g.branch("bhp", "@hp.ReturnValue")
    g.n("r5", "return_new", inp={"kind": str(K_DEAD)})
    g.cast("cj", P_JASON, "@entry.actor"); g.call("vj", K_SYS, "IsValid", inp={"Object": "@cj.AsJason"}); g.branch("bj", "@vj.ReturnValue")
    g.n("r4", "return_new", inp={"kind": str(K_HOSTILE)})
    g.get("gfa", "FolActors"); g.call("fav", K_MAP, "Map_Values", inp={"TargetMap": "@gfa.FolActors"}); g.call("isf", K_ARR, "Array_Contains", inp={"TargetArray": "@fav.Values", "ItemToFind": "@cn.AsCharacter NPC"})
    g.call("fk", K_MATH, "SelectInt", inp={"A": str(K_FOL), "B": str(K_NPC), "bPickA": "@isf.ReturnValue"}); g.link("fk.ReturnValue", "return.kind")
    g.chain("entry", "bisp", "r0"); g.chain("bisp:else", "bz", "rz"); g.chain("bz:else", "bn", "bhp", "bj", "r4"); g.chain("bn:else", "r1"); g.chain("bhp:else", "r5"); g.chain("bj:else", "fav", "return")
    return fn("Map Kind Of", [param("actor", "object:" + E_ACTOR)], [param("kind", "int")], graph=g)


def f_kind_hidden():
    """A kind (code) hidden by a click on the legend: its key in MapHidden."""
    g = G(); g.n("keys", "make_array", count=len(KIND_KEYS), type="name", inp={"[%d]" % i: g.lit_name("k%d" % i, k or "None") for i, k in enumerate(KIND_KEYS)})
    g.call("cl", K_MATH, "Clamp", inp={"Value": "@entry.kind", "Min": "0", "Max": str(len(KIND_KEYS) - 1)})
    g.call("k", K_ARR, "Array_Get", inp={"TargetArray": "@keys.Array", "Index": "@cl.ReturnValue"}); g.get("gh", "MapHidden")
    g.call("h", K_ARR, "Array_Contains", inp={"TargetArray": "@gh.MapHidden", "ItemToFind": "@k.Item"}); g.link("h.ReturnValue", "return.yes")
    return fn("Map Kind Hidden", [param("kind", "int")], [param("yes", "bool")], graph=g, pure=True)


def f_scan_vends():
    """MapVends = the level's vending machines (TradingMachine and its kinds: they stand still, scanned when the map opens)."""
    g = G(); g.call("all", K_GS, "GetAllActorsOfClass", inp={"ActorClass": P_TRADING}); g.set("s", "MapVends", inp={"MapVends": "@all.OutActors"}); g.chain("entry", "all", "s")
    return fn("Map Scan Vends", graph=g)


def f_read_size():
    """MapW / MapH = the laid-out size of the map area (it fills the panel width and half its height); before its first layout
    (size 0) the defaults stay."""
    g = G(); g.get("gv", "MapView"); g.call("geo", E_WIDGET, "GetCachedGeometry", inp={"self": "@gv.MapView"})
    g.call("ls", K_SLATE, "GetLocalSize", inp={"Geometry": "@geo.ReturnValue"}); g.call("b", K_MATH, "BreakVector2D", inp={"InVec": "@ls.ReturnValue"})
    g.call("okx", K_MATH, "Greater_FloatFloat", inp={"A": "@b.X", "B": "8.0"}); g.call("oky", K_MATH, "Greater_FloatFloat", inp={"A": "@b.Y", "B": "8.0"})
    g.call("ok", K_MATH, "BooleanAND", inp={"A": "@okx.ReturnValue", "B": "@oky.ReturnValue"}); g.branch("bok", "@ok.ReturnValue")
    g.set("sw", "MapW", inp={"MapW": "@b.X"}); g.set("sh", "MapH", inp={"MapH": "@b.Y"}); g.chain("entry", "bok", "sw", "sh")   # GetCachedGeometry is pure (const)
    return fn("Map Read Size", graph=g)


def f_redraw():
    """Draws the map: the tiles of MapShowBand in view (Map Tile Tex; missing ones leave the dark ground), the markers (beds of the
    Navigation list, followers, zombies of the level), the click target and Jodi's arrow (dim when she is on another band), the
    floor label; unused pool images hidden."""
    g = G(); g.get("gv", "MapView"); g.call("vv", K_SYS, "IsValid", inp={"Object": "@gv.MapView"}); g.branch("bvv", "@vv.ReturnValue")
    g.get("gp", "MapPx"); g.call("p", K_MATH, "Divide_FloatFloat", inp={"A": "@gp.MapPx", "B": str(TILE_CM)})
    g.call("hw", K_MATH, "Divide_FloatFloat", inp={"A": _half(g, "mhw", "MapW"), "B": "@p.ReturnValue"}); g.call("hh", K_MATH, "Divide_FloatFloat", inp={"A": _half(g, "mhh", "MapH"), "B": "@p.ReturnValue"})
    g.get("gcx", "MapCX"); g.get("gcy", "MapCY")
    for nm, c, op, h in (("y0", "@gcy.MapCY", "Subtract_FloatFloat", "@hw.ReturnValue"), ("y1", "@gcy.MapCY", "Add_FloatFloat", "@hw.ReturnValue"),
                         ("x0", "@gcx.MapCX", "Subtract_FloatFloat", "@hh.ReturnValue"), ("x1", "@gcx.MapCX", "Add_FloatFloat", "@hh.ReturnValue")):
        g.call(nm + "a", K_MATH, op, inp={"A": c, "B": h}); g.call(nm + "d", K_MATH, "Divide_FloatFloat", inp={"A": "@%sa.ReturnValue" % nm, "B": str(TILE_CM)})
        g.call(nm, K_MATH, "FFloor", inp={"A": "@%sd.ReturnValue" % nm})
    g.n("msz", "call_self", function="Map Read Size")
    g.set("pi0", "MapPi", inp={"MapPi": "0"})
    g.get("gst", "MapStyle"); g.call("flat", K_MATH, "EqualEqual_IntInt", inp={"A": "@gst.MapStyle", "B": "2"}); g.call("shade", K_MATH, "SelectFloat", inp={"A": "1.0", "B": "0.0", "bPickA": "@flat.ReturnValue"})
    g.n("lx", "macro", name="ForLoop", inp={"First Index": "@x0.ReturnValue", "Last Index": "@x1.ReturnValue"})
    g.n("ly", "macro", name="ForLoop", inp={"First Index": "@y0.ReturnValue", "Last Index": "@y1.ReturnValue"})
    g.get("gpi", "MapPi"); g.call("room", K_MATH, "Less_IntInt", inp={"A": "@gpi.MapPi", "B": str(TILE_POOL)}); g.branch("brm", "@room.ReturnValue")
    g.get("gsb", "MapShowBand"); g.n("key", "call_self", function="Map Key", inp={"band": "@gsb.MapShowBand", "x": "@lx.Index", "y": "@ly.Index"})
    g.n("tex", "call_self", function="Map Tile Tex", inp={"key": "@key.key"}); g.set("stt", "MapTileTmp", inp={"MapTileTmp": "@tex.tex"})
    g.get("gtt", "MapTileTmp"); g.call("tv", K_SYS, "IsValid", inp={"Object": "@gtt.MapTileTmp"}); g.branch("btv", "@tv.ReturnValue")
    # a floor's tile that is missing: the outside tile of the place instead of a hole (play test 2026-11-21: under an open roof the
    # map changed to "her floor", which had only the few tiles taken under the roof - the rest of the map was gone)
    g.get("gsbo", "MapShowBand"); g.call("nout", K_MATH, "NotEqual_IntInt", inp={"A": "@gsbo.MapShowBand", "B": str(OUT_BAND)}); g.branch("bno", "@nout.ReturnValue")
    g.n("keyo", "call_self", function="Map Key", inp={"band": str(OUT_BAND), "x": "@lx.Index", "y": "@ly.Index"}); g.n("texo", "call_self", function="Map Tile Tex", inp={"key": "@keyo.key"})
    g.set("stto", "MapTileTmp", inp={"MapTileTmp": "@texo.tex"}); g.get("gtto", "MapTileTmp"); g.call("tvo", K_SYS, "IsValid", inp={"Object": "@gtto.MapTileTmp"}); g.branch("btvo", "@tvo.ReturnValue")
    # top-left corner = world ((x+1) * TILE, y * TILE)
    g.call("x1i", K_MATH, "Add_IntInt", inp={"A": "@lx.Index", "B": "1"}); g.call("xf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@x1i.ReturnValue"}); g.call("wx", K_MATH, "Multiply_FloatFloat", inp={"A": "@xf.ReturnValue", "B": str(TILE_CM)})
    g.call("yf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@ly.Index"}); g.call("wy", K_MATH, "Multiply_FloatFloat", inp={"A": "@yf.ReturnValue", "B": str(TILE_CM)})
    g.n("scr", "call_self", function="Map To Screen", inp={"wx": "@wx.ReturnValue", "wy": "@wy.ReturnValue"})
    g.get("gp2", "MapPx"); g.call("tsz", K_MATH, "Add_FloatFloat", inp={"A": "@gp2.MapPx", "B": "1.0"})   # 1 px overlap: no seams
    g.get("tv1", "MapView"); g.call("tpl", W_NAVMAP, "Place", inp={"self": "@tv1.MapView", "index": "@gpi.MapPi", "x": "@scr.sx", "y": "@scr.sy", "w": "@tsz.ReturnValue", "h": "@tsz.ReturnValue", "angle": "0.0", "shown": "true"})
    g.get("tv2", "MapView"); g.call("tst", W_NAVMAP, "Set Tile", inp={"self": "@tv2.MapView", "index": "@gpi.MapPi", "tex": "@gtt.MapTileTmp", "shade": "@shade.ReturnValue"})
    g.call("pin", K_MATH, "Add_IntInt", inp={"A": "@gpi.MapPi", "B": "1"}); g.set("spi", "MapPi", inp={"MapPi": "@pin.ReturnValue"})
    g.get("gpi2", "MapPi"); g.get("hv1", "MapView"); g.call("htl", W_NAVMAP, "Hide Range", inp={"self": "@hv1.MapView", "first": "@gpi2.MapPi", "last": str(TILE_POOL - 1)})
    g.get("gmm", "MapMini"); g.branch("bmm", "@gmm.MapMini")   # the minimap gives its size (Map Draw Mini)
    # the ground in the panel's colour (opaque) with the hatching in the text colour (play test 2026-11-19: no bright white around)
    g.get("gcb", "ColBg"); g.call("cbk", K_MATH, "BreakColor", inp={"InColor": "@gcb.ColBg"})
    g.call("cbo", K_MATH, "MakeColor", inp={"R": "@cbk.R", "G": "@cbk.G", "B": "@cbk.B", "A": "1.0"})
    g.get("gct", "ColText"); g.call("ctk", K_MATH, "BreakColor", inp={"InColor": "@gct.ColText"})
    g.call("cto", K_MATH, "MakeColor", inp={"R": "@ctk.R", "G": "@ctk.G", "B": "@ctk.B", "A": "0.1"})
    g.get("gv0", "MapView"); g.call("sgr", W_NAVMAP, "Set Ground", inp={"self": "@gv0.MapView", "ground": "@cbo.ReturnValue", "lines": "@cto.ReturnValue"})
    g.chain("entry", "bvv", "sgr", "bmm", "pi0", "lx"); g.chain("bmm:else", "msz", "pi0"); g.chain("lx", "ly"); g.chain("ly", "brm", "tex", "stt", "btv", "tpl", "tst", "spi"); g.chain("btv:else", "bno", "texo", "stto", "btvo", "tpl")
    g.chain("lx:Completed", "htl", "mi0")
    # markers (spec 2026-11-19): beds, vending machines, then every Character_Base in three passes - dead under the living,
    # dots (followers, NPCs, zombies), the hostile human's ring on top; a kind hidden on the legend (MapHidden) is skipped.
    # MapSeen = the kinds the level has (all of them, whatever the band or view): the legend shows those
    g.set("mi0", "MapMi", inp={"MapMi": str(TILE_POOL)}); g.set("ms0", "MapSeen", inp={"MapSeen": "0"}); g.chain("mi0", "ms0")
    g.get("gnb", "MapBeds"); g.n("hbd", "call_self", function="Map Kind Hidden", inp={"kind": str(K_BED)}); g.branch("bhbd", "@hbd.yes")
    bed = _marks(g, "mb", "@gnb.MapBeds", T_BED, COL_BED, MARK["bed"], "0", None)
    g.get("gvd", "MapVends"); g.n("hvd", "call_self", function="Map Kind Hidden", inp={"kind": str(K_VEND)}); g.branch("bhvd", "@hvd.yes")
    vend = _marks(g, "mv", "@gvd.MapVends", T_VEND, COL_VEND, MARK["vend"], "0", None)
    g.chain("ms0", "bhbd"); g.chain("bhbd:else", bed); g.chain("bhbd", "bhvd"); g.chain(bed + ":Completed", "bhvd"); g.chain("bhvd:else", vend)
    g.call("chall", K_GS, "GetAllActorsOfClass", inp={"ActorClass": P_CB}); g.set("schr", "MapChars", inp={"MapChars": "@chall.OutActors"})
    g.get("gck", "MapCharKinds"); g.call("cck", K_ARR, "Array_Clear", inp={"TargetArray": "@gck.MapCharKinds"})
    g.chain("bhvd", "chall"); g.chain(vend + ":Completed", "chall"); g.chain("chall", "schr", "cck", "kd")
    # pass 1: every figure's kind (MapCharKinds, MapSeen), the dead drawn
    g.get("gch1", "MapChars"); g.foreach("kd", "@gch1.MapChars"); g.n("kof", "call_self", function="Map Kind Of", inp={"actor": "@kd.Array Element"})
    g.get("gck2", "MapCharKinds"); g.call("kad", K_ARR, "Array_Add", inp={"TargetArray": "@gck2.MapCharKinds", "NewItem": "@kof.kind"})
    g.n("bits", "make_array", count=len(KIND_KEYS), type="int", inp={"[%d]" % i: str(0 if i == 0 else 1 << i) for i in range(len(KIND_KEYS))})
    g.call("bit", K_ARR, "Array_Get", inp={"TargetArray": "@bits.Array", "Index": "@kof.kind"}); g.get("gsn", "MapSeen")
    g.call("sor", K_MATH, "Or_IntInt", inp={"A": "@gsn.MapSeen", "B": "@bit.Item"}); g.set("ssn", "MapSeen", inp={"MapSeen": "@sor.ReturnValue"})
    g.chain("kd", "kof", "kad", "ssn", "kdb")
    g.call("isd", K_MATH, "EqualEqual_IntInt", inp={"A": "@kof.kind", "B": str(K_DEAD)}); g.n("hdd", "call_self", function="Map Kind Hidden", inp={"kind": str(K_DEAD)})
    g.call("nhd", K_MATH, "Not_PreBool", inp={"A": "@hdd.yes"}); g.call("dok", K_MATH, "BooleanAND", inp={"A": "@isd.ReturnValue", "B": "@nhd.ReturnValue"}); g.branch("kdb", "@dok.ReturnValue")
    _mark_one(g, "kdm", "@kd.Array Element", T_DEAD, COL_DEAD, MARK["dead"], "kdb")
    # pass 2: dots of the living (followers green, NPCs blue, zombies red); pass 3: the hostile human's ring
    def kind_pass(p, want, tex, size, after):
        g.get(p + "gc", "MapChars"); g.foreach(p, "@%sgc.MapChars" % p)
        g.get(p + "gk", "MapCharKinds"); g.call(p + "k", K_ARR, "Array_Get", inp={"TargetArray": "@%sgk.MapCharKinds" % p, "Index": "@%s.Array Index" % p})
        k = "@%sk.Item" % p
        if want == "dots":
            g.call(p + "lo", K_MATH, "GreaterEqual_IntInt", inp={"A": k, "B": str(K_FOL)}); g.call(p + "hi", K_MATH, "LessEqual_IntInt", inp={"A": k, "B": str(K_ZOMBIE)})
            g.call(p + "in", K_MATH, "BooleanAND", inp={"A": "@%slo.ReturnValue" % p, "B": "@%shi.ReturnValue" % p}); ok = "@%sin.ReturnValue" % p
            g.call(p + "c1", K_MATH, "EqualEqual_IntInt", inp={"A": k, "B": str(K_FOL)}); g.call(p + "c2", K_MATH, "EqualEqual_IntInt", inp={"A": k, "B": str(K_NPC)})
            g.call(p + "s2", K_MATH, "SelectColor", inp={"A": COL_NPC, "B": COL_ENEMY, "bPickA": "@%sc2.ReturnValue" % p})
            g.call(p + "s1", K_MATH, "SelectColor", inp={"A": COL_FOL, "B": "@%ss2.ReturnValue" % p, "bPickA": "@%sc1.ReturnValue" % p}); col = "@%ss1.ReturnValue" % p
        else:
            g.call(p + "in", K_MATH, "EqualEqual_IntInt", inp={"A": k, "B": str(want)}); ok = "@%sin.ReturnValue" % p; col = KIND_COL[want]
        g.n(p + "hd", "call_self", function="Map Kind Hidden", inp={"kind": k}); g.call(p + "nh", K_MATH, "Not_PreBool", inp={"A": "@%shd.yes" % p})
        g.call(p + "ok", K_MATH, "BooleanAND", inp={"A": ok, "B": "@%snh.ReturnValue" % p}); g.branch(p + "b", "@%sok.ReturnValue" % p)
        g.chain(after, p); g.chain(p, p + "b"); _mark_one(g, p + "m", "@%s.Array Element" % p, tex, col, size, p + "b")
        return p
    dots = kind_pass("kp2", "dots", T_DOT, MARK["dot"], "kd:Completed")
    ring = kind_pass("kp3", K_HOSTILE, T_RING, MARK["ring"], dots + ":Completed")
    # the level's beds / vending machines count as seen
    for nm_, var_, bit_ in (("sb", "MapBeds", K_BED), ("sv", "MapVends", K_VEND)):
        g.get(nm_ + "g", var_); g.call(nm_ + "l", K_ARR, "Array_Length", inp={"TargetArray": "@%sg.%s" % (nm_, var_)}); g.call(nm_ + "h", K_MATH, "Greater_IntInt", inp={"A": "@%sl.ReturnValue" % nm_, "B": "0"})
        g.call(nm_ + "b", K_MATH, "SelectInt", inp={"A": str(1 << bit_), "B": "0", "bPickA": "@%sh.ReturnValue" % nm_}); g.get(nm_ + "s", "MapSeen")
        g.call(nm_ + "o", K_MATH, "Or_IntInt", inp={"A": "@%ss.MapSeen" % nm_, "B": "@%sb.ReturnValue" % nm_}); g.set(nm_ + "w", "MapSeen", inp={"MapSeen": "@%so.ReturnValue" % nm_})
    g.chain(ring + ":Completed", "sbw", "svw", "blg")
    # the legend follows what the level has (not for the minimap: it has none)
    g.get("gsn2", "MapSeen"); g.get("glm", "MapLegMask"); g.call("lne", K_MATH, "NotEqual_IntInt", inp={"A": "@gsn2.MapSeen", "B": "@glm.MapLegMask"})
    g.get("gmm4", "MapMini"); g.call("nmm4", K_MATH, "Not_PreBool", inp={"A": "@gmm4.MapMini"}); g.call("lgo", K_MATH, "BooleanAND", inp={"A": "@lne.ReturnValue", "B": "@nmm4.ReturnValue"})
    g.branch("blg", "@lgo.ReturnValue"); g.n("rlg", "call_self", function="Map Rebuild Legend"); g.chain("blg", "rlg", "hmk"); g.chain("blg:else", "hmk")
    g.get("gmi", "MapMi"); g.get("hv2", "MapView"); g.call("hmk", W_NAVMAP, "Hide Range", inp={"self": "@hv2.MapView", "first": "@gmi.MapMi", "last": str(CROSS - 1)})
    g.chain("hmk", "ct")
    # click target: on the shown band (or outside) only
    g.get("gto", "MapTgtOn"); g.get("gtg", "MapTgt"); g.n("cms", "call_self", function="Map Mark Spot", inp={"v": "@gtg.MapTgt"})
    g.call("cok0", K_MATH, "BooleanAND", inp={"A": "@gto.MapTgtOn", "B": "@cms.ok"}); g.get("gmm2", "MapMini"); g.call("nmm", K_MATH, "Not_PreBool", inp={"A": "@gmm2.MapMini"})
    g.call("cok", K_MATH, "BooleanAND", inp={"A": "@cok0.ReturnValue", "B": "@nmm.ReturnValue"}); g.branch("ct", "@cok.ReturnValue")
    _place(g, "cpl", str(CROSS), "@cms.sx", "@cms.sy", MARK["cross"])
    g.get("cv2", "MapView"); g.call("csm", W_NAVMAP, "Set Mark", inp={"self": "@cv2.MapView", "index": str(CROSS), "tex": T_CROSS, "color": COL_BED})
    g.get("cv3", "MapView"); g.call("chd", W_NAVMAP, "Hide Range", inp={"self": "@cv3.MapView", "first": str(CROSS), "last": str(CROSS)})
    g.chain("ct", "cpl", "csm", "bjv"); g.chain("ct:else", "chd", "bjv")
    # Jodi: her arrow, turned by her yaw (0 = +X = up), dim on another band
    g.get("gpl", "Player"); g.call("jv", K_SYS, "IsValid", inp={"Object": "@gpl.Player"}); g.branch("bjv", "@jv.ReturnValue")
    g.get("gpl2", "Player"); g.call("jl", E_ACTOR, "K2_GetActorLocation", inp={"self": "@gpl2.Player"}); g.call("jb", K_MATH, "BreakVector", inp={"InVec": "@jl.ReturnValue"})
    g.n("jsc", "call_self", function="Map To Screen", inp={"wx": "@jb.X", "wy": "@jb.Y"})
    g.get("gpl3", "Player"); g.call("jr", E_ACTOR, "K2_GetActorRotation", inp={"self": "@gpl3.Player"}); g.call("jrb", K_MATH, "BreakRotator", inp={"InRot": "@jr.ReturnValue"})
    _place(g, "jpl", str(ARROW), "@jsc.sx", "@jsc.sy", MARK["arrow"], angle="@jrb.Yaw")
    g.n("jbd", "call_self", function="Map Jodi Band"); g.get("gsb2", "MapShowBand"); g.call("jsame", K_MATH, "EqualEqual_IntInt", inp={"A": "@jbd.band", "B": "@gsb2.MapShowBand"})
    g.call("jout", K_MATH, "EqualEqual_IntInt", inp={"A": "@gsb2.MapShowBand", "B": str(OUT_BAND)}); g.call("jon", K_MATH, "BooleanOR", inp={"A": "@jsame.ReturnValue", "B": "@jout.ReturnValue"})
    g.call("jcol", K_MATH, "SelectColor", inp={"A": COL_JODI, "B": COL_JODI_DIM, "bPickA": "@jon.ReturnValue"})
    g.get("jv2", "MapView"); g.call("jsm", W_NAVMAP, "Set Mark", inp={"self": "@jv2.MapView", "index": str(ARROW), "tex": T_ARROW, "color": "@jcol.ReturnValue"})
    g.n("lbl", "call_self", function="Map Show Label"); g.get("gmm3", "MapMini"); g.branch("bml", "@gmm3.MapMini")
    g.chain("bjv", "jpl", "jsm", "bml"); g.chain("bjv:else", "bml"); g.chain("bml:else", "lbl")
    return fn("Map Redraw", graph=g)


def f_scan_beds():
    """MapBeds = the level's save beds (the markers; the Navigation tab copies its sorted list in, the minimap scans once)."""
    g = G(); g.call("all", K_GS, "GetAllActorsOfClass", inp={"ActorClass": P_BED}); g.get("gb", "MapBeds"); g.call("cl", K_ARR, "Array_Clear", inp={"TargetArray": "@gb.MapBeds"})
    g.foreach("fe", "@all.OutActors"); g.cast("cb", P_BED, "@fe.Array Element"); g.get("gb2", "MapBeds")
    g.call("ad", K_ARR, "Array_Add", inp={"TargetArray": "@gb2.MapBeds", "NewItem": "@cb.AsBed"}); g.chain("entry", "all", "cl", "fe", "ad")
    g.n("sv", "call_self", function="Map Scan Vends"); g.chain("fe:Completed", "sv")
    return fn("Map Scan Beds", graph=g)


SV = ("View", "W", "H", "CX", "CY", "Px", "Band")
SV_VAR = {"View": "MapView", "W": "MapW", "H": "MapH", "CX": "MapCX", "CY": "MapCY", "Px": "MapPx", "Band": "MapShowBand"}


def f_draw_mini():
    """Draws the minimap's inner map: the big map's view kept aside (MapSv*), the view set to the minimap (Jodi in the middle, her
    band, MiniZoom metres across its frame), Map Redraw with MapMini (no label, no target, the size given), the view back."""
    g = G(); g.get("gmv", "MiniView"); g.call("vv", K_SYS, "IsValid", inp={"Object": "@gmv.MiniView"}); g.branch("bvv", "@vv.ReturnValue"); tail = ["entry", "bvv"]
    for k in SV:
        g.get("sg" + k, SV_VAR[k]); g.set("ss" + k, "MapSv" + k, inp={"MapSv" + k: "@sg%s.%s" % (k, SV_VAR[k])}); tail.append("ss" + k)
    g.call("inn", W_MINIMAP, "Inner Map", inp={"self": "@gmv.MiniView"})
    g.n("ft", "call_self", function="Map Jodi Feet"); g.call("fb", K_MATH, "BreakVector", inp={"InVec": "@ft.feet"}); g.n("jb", "call_self", function="Map Jodi Band")
    g.n("ms", "call_self", function="Mini Size"); g.call("s", K_MATH, "Subtract_FloatFloat", inp={"A": "@ms.size", "B": str(2.0 * MINI_PAD)})
    g.call("d", K_MATH, "Multiply_FloatFloat", inp={"A": "@s.ReturnValue", "B": str(MINI_DIAG)})
    g.get("gz", "MiniZoom"); g.call("zcm", K_MATH, "Multiply_FloatFloat", inp={"A": "@gz.MiniZoom", "B": "100.0"}); g.call("pcm", K_MATH, "Divide_FloatFloat", inp={"A": "@s.ReturnValue", "B": "@zcm.ReturnValue"})
    g.call("px", K_MATH, "Multiply_FloatFloat", inp={"A": "@pcm.ReturnValue", "B": str(TILE_CM)})
    for k, pin in (("View", "@inn.map"), ("W", "@d.ReturnValue"), ("H", "@d.ReturnValue"), ("CX", "@fb.X"), ("CY", "@fb.Y"), ("Px", "@px.ReturnValue"), ("Band", "@jb.band")):
        g.set("sm" + k, SV_VAR[k], inp={SV_VAR[k]: pin}); tail.append("sm" + k)
    g.set("mm1", "MapMini", inp={"MapMini": "true"}); g.n("rd", "call_self", function="Map Redraw"); g.set("mm0", "MapMini", inp={"MapMini": "false"}); tail += ["mm1", "rd", "mm0"]
    for k in SV:
        g.get("rg" + k, "MapSv" + k); g.set("rs" + k, SV_VAR[k], inp={SV_VAR[k]: "@rg%s.MapSv%s" % (k, k)}); tail.append("rs" + k)
    g.chain(*tail)
    return fn("Map Draw Mini", graph=g)


def f_mini_size():
    """The minimap's frame size in widget units: MiniSize % of the screen height (pixels / viewport scale)."""
    g = G(); g.get("gpc", "PC"); g.call("vs", E_PC, "GetViewportSize", inp={"self": "@gpc.PC"}); g.call("vh", K_MATH, "Conv_IntToFloat", inp={"InInt": "@vs.SizeY"})
    g.get("gs", "MiniSize"); g.call("pc", K_MATH, "Multiply_FloatFloat", inp={"A": "@vh.ReturnValue", "B": "@gs.MiniSize"}); g.call("px", K_MATH, "Divide_FloatFloat", inp={"A": "@pc.ReturnValue", "B": "100.0"})
    g.call("sc", "/Script/UMG.WidgetLayoutLibrary", "GetViewportScale"); g.call("mx", K_MATH, "FMax", inp={"A": "@sc.ReturnValue", "B": "0.01"})
    g.call("u", K_MATH, "Divide_FloatFloat", inp={"A": "@px.ReturnValue", "B": "@mx.ReturnValue"}); g.link("u.ReturnValue", "return.size"); g.link("px.ReturnValue", "return.pixels")
    return fn("Mini Size", outputs=[param("size", "float"), param("pixels", "float")], graph=g, pure=True)


def f_mini_tick():
    """Every frame (not paused): the minimap shown while the map is on, the minimap is switched on, Jodi is there and the panel is
    closed (the panel has the big map) or shows Options > Map (its settings are made with it in sight; behind the panel); else hidden. Shown: in its corner, turned so the camera's view points up; drawn every
    MINI_EVERY seconds. Created on first use (and the level's beds scanned for it)."""
    g = G(); g.get("gof", "MapOff"); g.call("on1", K_MATH, "Not_PreBool", inp={"A": "@gof.MapOff"}); g.get("gmo", "MiniOn"); g.get("gpo", "PanelOpen")
    # panel open: only on Options > Map (play test 2026-11-17: the settings were made blind) - behind the panel (MINI_Z < 100)
    g.get("gpg", "Page"); g.call("iop", K_MATH, "EqualEqual_NameName", inp={"A": "@gpg.Page", "B": "Options"})
    g.get("goc", "OptionsCat"); g.call("imc", K_MATH, "EqualEqual_NameName", inp={"A": "@goc.OptionsCat", "B": "Map"})
    g.call("onmap", K_MATH, "BooleanAND", inp={"A": "@iop.ReturnValue", "B": "@imc.ReturnValue"})
    g.call("npo0", K_MATH, "Not_PreBool", inp={"A": "@gpo.PanelOpen"}); g.call("npo", K_MATH, "BooleanOR", inp={"A": "@npo0.ReturnValue", "B": "@onmap.ReturnValue"})
    g.get("gpl", "Player"); g.call("pv", K_SYS, "IsValid", inp={"Object": "@gpl.Player"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@on1.ReturnValue", "B": "@gmo.MiniOn"}); g.call("a2", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@npo.ReturnValue"})
    g.call("show", K_MATH, "BooleanAND", inp={"A": "@a2.ReturnValue", "B": "@pv.ReturnValue"}); g.branch("bsh", "@show.ReturnValue")
    # hide (once)
    g.get("gsn", "MiniShown"); g.branch("bsn", "@gsn.MiniShown"); g.get("gmv0", "MiniView")
    g.call("hid", E_WIDGET, "SetVisibility", inp={"self": "@gmv0.MiniView", "InVisibility": "Collapsed"}); g.set("sn0", "MiniShown", inp={"MiniShown": "false"})
    g.chain("entry", "bsh"); g.chain("bsh:else", "bsn", "hid", "sn0")
    # create once
    g.get("gmv", "MiniView"); g.call("vv", K_SYS, "IsValid", inp={"Object": "@gmv.MiniView"}); g.branch("bvv", "@vv.ReturnValue")
    g.get("gpc", "PC"); g.call("cr", K_WBL, "Create", inp={"WidgetType": W_MINIMAP, "OwningPlayer": "@gpc.PC"}); g.cast("cm", W_MINIMAP, "@cr.ReturnValue")
    g.set("smv", "MiniView", inp={"MiniView": "@cm.AsW_MiniMap"}); g.call("atv", E_USERWIDGET, "AddToViewport", inp={"self": "@cm.AsW_MiniMap", "ZOrder": str(MINI_Z)})
    g.n("sbd", "call_self", function="Map Scan Beds")
    g.chain("bsh", "bvv"); g.chain("bvv:else", "cr", "smv", "atv", "sbd", "bvv2")
    # shown: visible, placed, turned; drawn now and then
    g.get("gmv2", "MiniView"); g.call("vv2", K_SYS, "IsValid", inp={"Object": "@gmv2.MiniView"}); g.branch("bvv2", "@vv2.ReturnValue")
    g.chain("bvv", "bvv2")
    g.get("gmv3", "MiniView"); g.call("vis", E_WIDGET, "SetVisibility", inp={"self": "@gmv3.MiniView", "InVisibility": "HitTestInvisible"}); g.set("sn1", "MiniShown", inp={"MiniShown": "true"})
    g.n("ms", "call_self", function="Mini Size"); g.get("gpc2", "PC"); g.call("vs", E_PC, "GetViewportSize", inp={"self": "@gpc2.PC"})
    g.call("vw", K_MATH, "Conv_IntToFloat", inp={"InInt": "@vs.SizeX"}); g.call("vh", K_MATH, "Conv_IntToFloat", inp={"InInt": "@vs.SizeY"})
    g.get("gmg", "MiniMargin"); g.call("mg0", K_MATH, "Multiply_FloatFloat", inp={"A": "@vh.ReturnValue", "B": "@gmg.MiniMargin"}); g.call("mg", K_MATH, "Divide_FloatFloat", inp={"A": "@mg0.ReturnValue", "B": "100.0"})
    g.get("gco", "MiniCorner"); g.call("cmod", K_MATH, "Percent_IntInt", inp={"A": "@gco.MiniCorner", "B": "2"}); g.call("right", K_MATH, "EqualEqual_IntInt", inp={"A": "@cmod.ReturnValue", "B": "1"})
    g.call("bot", K_MATH, "GreaterEqual_IntInt", inp={"A": "@gco.MiniCorner", "B": "2"})
    g.call("rx0", K_MATH, "Subtract_FloatFloat", inp={"A": "@vw.ReturnValue", "B": "@ms.pixels"}); g.call("rx", K_MATH, "Subtract_FloatFloat", inp={"A": "@rx0.ReturnValue", "B": "@mg.ReturnValue"})
    g.call("by0", K_MATH, "Subtract_FloatFloat", inp={"A": "@vh.ReturnValue", "B": "@ms.pixels"}); g.call("by", K_MATH, "Subtract_FloatFloat", inp={"A": "@by0.ReturnValue", "B": "@mg.ReturnValue"})
    g.call("x", K_MATH, "SelectFloat", inp={"A": "@rx.ReturnValue", "B": "@mg.ReturnValue", "bPickA": "@right.ReturnValue"}); g.call("y", K_MATH, "SelectFloat", inp={"A": "@by.ReturnValue", "B": "@mg.ReturnValue", "bPickA": "@bot.ReturnValue"})
    g.call("pos", K_MATH, "MakeVector2D", inp={"X": "@x.ReturnValue", "Y": "@y.ReturnValue"}); g.call("siz", K_MATH, "MakeVector2D", inp={"X": "@ms.size", "Y": "@ms.size"})
    g.get("gmv4", "MiniView"); g.call("spv", E_USERWIDGET, "SetPositionInViewport", inp={"self": "@gmv4.MiniView", "Position": "@pos.ReturnValue", "bRemoveDPIScale": "true"})
    g.call("ssv", E_USERWIDGET, "SetDesiredSizeInViewport", inp={"self": "@gmv4.MiniView", "Size": "@siz.ReturnValue"})
    g.call("lay", W_MINIMAP, "Layout", inp={"self": "@gmv4.MiniView", "size": "@ms.size"})
    # camera forward up: the map turned by minus the camera's yaw (yaw 0 = +X = up on the map)
    g.call("pcm", K_GS, "GetPlayerCameraManager", inp={"PlayerIndex": "0"}); g.call("crot", "/Script/Engine.PlayerCameraManager", "GetCameraRotation", inp={"self": "@pcm.ReturnValue"})
    g.call("cb", K_MATH, "BreakRotator", inp={"InRot": "@crot.ReturnValue"}); g.call("ang", K_MATH, "Multiply_FloatFloat", inp={"A": "@cb.Yaw", "B": "-1.0"})
    g.call("trn", W_MINIMAP, "Turn", inp={"self": "@gmv4.MiniView", "angle": "@ang.ReturnValue"})
    g.get("gmr", "MiniRound"); g.call("srd", W_MINIMAP, "Set Round", inp={"self": "@gmv4.MiniView", "round": "@gmr.MiniRound"})   # square / round (Options > Map)
    g.call("now", K_GS, "GetRealTimeSeconds"); g.get("gnx", "MiniNext"); g.call("due", K_MATH, "GreaterEqual_FloatFloat", inp={"A": "@now.ReturnValue", "B": "@gnx.MiniNext"}); g.branch("bdu", "@due.ReturnValue")
    g.call("nx", K_MATH, "Add_FloatFloat", inp={"A": "@now.ReturnValue", "B": str(MINI_EVERY)}); g.set("snx", "MiniNext", inp={"MiniNext": "@nx.ReturnValue"})
    g.n("dm", "call_self", function="Map Draw Mini")
    g.chain("bvv2", "vis", "sn1", "spv", "ssv", "lay", "trn", "srd", "bdu", "snx", "dm")
    return fn("Mini Tick", graph=g)


def functions(ts, tt, create_widget, set_manager):
    """Manager functions that need gen_manager_ui's helpers (strings, widget creation)."""

    def f_label():
        """The floor label above the map: "Outside", "Floor: Jodi's" or "Floor: +1" / "Floor: -2" (relative to Jodi's band)."""
        g = G(); g.get("gsb", "MapShowBand"); g.call("out", K_MATH, "EqualEqual_IntInt", inp={"A": "@gsb.MapShowBand", "B": str(OUT_BAND)})
        g.get("gb", "MapBand"); g.call("rel", K_MATH, "Subtract_IntInt", inp={"A": "@gsb.MapShowBand", "B": "@gb.MapBand"})
        g.call("rs", K_STR, "Conv_IntToString", inp={"InInt": "@rel.ReturnValue"}); g.call("pos", K_MATH, "Greater_IntInt", inp={"A": "@rel.ReturnValue", "B": "0"})
        g.call("rp", K_STR, "Concat_StrStr", inp={"A": "+", "B": "@rs.ReturnValue"}); g.call("rv", K_MATH, "SelectString", inp={"A": "@rp.ReturnValue", "B": "@rs.ReturnValue", "bPickA": "@pos.ReturnValue"})
        g.call("zero", K_MATH, "EqualEqual_IntInt", inp={"A": "@rel.ReturnValue", "B": "0"})
        g.call("v", K_MATH, "SelectString", inp={"A": ts(g, "tj", "Map_FloorJodi"), "B": "@rv.ReturnValue", "bPickA": "@zero.ReturnValue"})
        g.call("fl", K_STR, "Replace", inp={"SourceString": ts(g, "tf", "Map_Floor"), "From": "%s", "To": "@v.ReturnValue", "SearchCase": "CaseSensitive"})
        g.call("s", K_MATH, "SelectString", inp={"A": ts(g, "to", "Map_Outside"), "B": "@fl.ReturnValue", "bPickA": "@out.ReturnValue"})
        g.call("t", K_TXT, "Conv_StringToText", inp={"InString": "@s.ReturnValue"})
        g.get("gp", "Panel"); g.call("sl", W_PANEL, "Set Map Label", inp={"self": "@gp.Panel", "label": "@t.ReturnValue"}); g.chain("entry", "sl")
        return fn("Map Show Label", graph=g)

    LEG_ORDER = (K_BED, K_VEND, K_FOL, K_NPC, K_ZOMBIE, K_HOSTILE, K_DEAD)
    LEG_TEXT = {K_BED: "Map_Leg_Bed", K_VEND: "Map_Leg_Vend", K_FOL: "Map_Leg_Fol", K_NPC: "Map_Leg_Npc", K_ZOMBIE: "Map_Leg_Zombie", K_HOSTILE: "Map_Leg_Hostile", K_DEAD: "Map_Leg_Dead"}

    def f_legend():
        """The legend (spec 2026-11-19): Jodi, each kind the level has (MapSeen; hidden ones dimmed, a click hides / shows), then the
        two grounds (unexplored, lower). Off in Options > Map (MapNoLegend): none. MapLegMask remembers what it was built for."""
        g = G(); g.get("gp", "Panel"); g.call("clr", W_PANEL, "Clear Map Legend", inp={"self": "@gp.Panel"})
        g.get("gsn", "MapSeen"); g.set("slm", "MapLegMask", inp={"MapLegMask": "@gsn.MapSeen"})
        g.get("gnl", "MapNoLegend"); g.call("on", K_MATH, "Not_PreBool", inp={"A": "@gnl.MapNoLegend"}); g.get("gp1", "Panel")
        g.call("shw", W_PANEL, "Set Map Legend Shown", inp={"self": "@gp1.Panel", "shown": "@on.ReturnValue"}); g.branch("bon", "@on.ReturnValue")
        g.chain("entry", "clr", "slm", "shw", "bon"); prev = "bon"
        def item(p, key, tex, col, caption_pin, hidden, clickable, prev):
            lw = create_widget(g, p, W_MAPLEG); set_manager(g, p + "sm", W_MAPLEG, lw)
            g.call(p + "in", W_MAPLEG, "Init", inp={"self": lw, "key": g.lit_name(p + "k", key), "tex": tex, "color": col, "caption": caption_pin, "hidden": hidden,
                                                     "clickable": clickable, "tip": tt(g, p + "tt", "Map_LegTip")})
            g.get(p + "gp", "Panel"); g.call(p + "ad", W_PANEL, "Add Map Legend", inp={"self": "@%sgp.Panel" % p, "widget": lw})
            g.chain(prev, p + "_cr", p + "sm", p + "in", p + "ad"); return p + "ad"
        prev = item("lj", "jodi", T_ARROW, COL_JODI, tt(g, "tj", "Map_Leg_Jodi"), "false", "false", prev)
        for k in LEG_ORDER:
            p = "lk%d" % k; g.get(p + "s", "MapSeen"); g.call(p + "a", K_MATH, "And_IntInt", inp={"A": "@%ss.MapSeen" % p, "B": str(1 << k)})
            g.call(p + "nz", K_MATH, "NotEqual_IntInt", inp={"A": "@%sa.ReturnValue" % p, "B": "0"}); g.branch(p + "b", "@%snz.ReturnValue" % p); g.chain(prev, p + "b")
            g.n(p + "h", "call_self", function="Map Kind Hidden", inp={"kind": str(k)})
            done = item(p + "i", KIND_KEYS[k], KIND_TEX[k], KIND_COL[k], tt(g, p + "t", LEG_TEXT[k]), "@%sh.yes" % p, "true", p + "b")
            g.n(p + "j", "sequence", count=1); g.chain(done, p + "j"); g.chain(p + "b:else", p + "j"); prev = p + "j:then_0"
        prev = item("lu", "unexplored", T_HATCH, "(R=1,G=1,B=1,A=0.6)", tt(g, "tu", "Map_Leg_Unexplored"), "false", "false", prev)
        item("ll", "lower", T_LOWER, "(R=1,G=1,B=1,A=1)", tt(g, "tl", "Map_Leg_Lower"), "false", "false", prev)
        return fn("Map Rebuild Legend", graph=g)

    def f_legend_toggle():
        """A legend entry clicked: its kind hidden <-> shown (MapHidden, saved), legend and picture anew."""
        g = G(); g.get("gh", "MapHidden"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gh.MapHidden", "ItemToFind": "@entry.key"}); g.branch("bh", "@has.ReturnValue")
        g.get("gh2", "MapHidden"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gh2.MapHidden", "Item": "@entry.key"})
        g.get("gh3", "MapHidden"); g.call("ad", K_ARR, "Array_AddUnique", inp={"TargetArray": "@gh3.MapHidden", "NewItem": "@entry.key"})
        g.n("sv", "call_self", function="Save Settings"); g.set("slm", "MapLegMask", inp={"MapLegMask": "-1"}); g.n("rd", "call_self", function="Map Redraw")
        g.chain("entry", "bh", "rm", "sv"); g.chain("bh:else", "ad", "sv"); g.chain("sv", "slm", "rd")
        return fn("Map Legend Toggle", [param("key", "name")], graph=g)

    def link(g, p, action, caption_pin, tail, widest=None, add="Add Map Link"):
        """A link above the map. widest: up to three text pins, every caption it can show - the link then sits in a W_MapSlot as wide
        as the widest of them, so the links behind it do not move when its caption changes."""
        lw = create_widget(g, p, W_TXT); set_manager(g, p + "sm", W_TXT, lw)
        g.call(p + "in", W_TXT, "Init", inp={"self": lw, "action": action, "caption": caption_pin})
        tail += [p + "_cr", p + "sm", p + "in"]   # the cast (p) is pure
        if widest:
            sw = create_widget(g, p + "sl", W_MAPSLOT); pins = list(widest) + [widest[-1]] * (3 - len(widest))
            g.call(p + "si", W_MAPSLOT, "Init", inp={"self": sw, "widget": lw, "a": pins[0], "b": pins[1], "c": pins[2]}); tail += [p + "sl_cr", p + "si"]; lw = sw
        g.get(p + "gp", "Panel"); g.call(p + "ad", W_PANEL, add, inp={"self": "@%sgp.Panel" % p, "widget": lw}); tail.append(p + "ad")

    def f_links():
        """The links above the map: Up, Down, Outside / Inside, Center on Jodi, Recording: on / off, Style: ..., and Teleport while a
        target is set and Jodi can go (NavOk, as the bed rows)."""
        g = G(); g.get("gp", "Panel"); g.call("clr", W_PANEL, "Clear Map Links", inp={"self": "@gp.Panel"}); tail = ["entry", "clr"]
        link(g, "lu", "MapUp", tt(g, "tu", "Map_Up"), tail); link(g, "ld", "MapDown", tt(g, "td", "Map_Down"), tail)
        g.get("gsb", "MapShowBand"); g.call("out", K_MATH, "EqualEqual_IntInt", inp={"A": "@gsb.MapShowBand", "B": str(OUT_BAND)})
        g.call("oc", K_MATH, "SelectString", inp={"A": ts(g, "tin", "Map_Inside"), "B": ts(g, "tout", "Map_Outside"), "bPickA": "@out.ReturnValue"})
        g.call("oct", K_TXT, "Conv_StringToText", inp={"InString": "@oc.ReturnValue"}); link(g, "lo", "MapOutside", "@oct.ReturnValue", tail, widest=[tt(g, "wo1", "Map_Inside"), tt(g, "wo2", "Map_Outside")])
        link(g, "lc", "MapCenter", tt(g, "tc", "Map_Center"), tail)
        g.get("gnr", "MapNoRecord"); g.call("rc", K_MATH, "SelectString", inp={"A": ts(g, "troff", "Map_RecOff"), "B": ts(g, "tron", "Map_RecOn"), "bPickA": "@gnr.MapNoRecord"})
        g.call("rct", K_TXT, "Conv_StringToText", inp={"InString": "@rc.ReturnValue"}); link(g, "lr", "MapRecord", "@rct.ReturnValue", tail, widest=[tt(g, "wr1", "Map_RecOff"), tt(g, "wr2", "Map_RecOn")])
        g.get("gst", "MapStyle"); pin = ts(g, "ts0", STYLE_KEYS[0])
        for i, k in enumerate(STYLE_KEYS[1:], 1):
            g.call("se%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": "@gst.MapStyle", "B": str(i)})
            g.call("ss%d" % i, K_MATH, "SelectString", inp={"A": ts(g, "ts%d" % i, k), "B": pin, "bPickA": "@se%d.ReturnValue" % i}); pin = "@ss%d.ReturnValue" % i
        g.call("sty", K_STR, "Replace", inp={"SourceString": ts(g, "tsf", "Map_Style"), "From": "%s", "To": pin, "SearchCase": "CaseSensitive"})
        wst = []
        for i, k in enumerate(STYLE_KEYS):
            g.call("wsr%d" % i, K_STR, "Replace", inp={"SourceString": ts(g, "wsf%d" % i, "Map_Style"), "From": "%s", "To": ts(g, "wsk%d" % i, k), "SearchCase": "CaseSensitive"})
            g.call("wst%d" % i, K_TXT, "Conv_StringToText", inp={"InString": "@wsr%d.ReturnValue" % i}); wst.append("@wst%d.ReturnValue" % i)
        g.call("styt", K_TXT, "Conv_StringToText", inp={"InString": "@sty.ReturnValue"}); link(g, "ls", "MapStyle", "@styt.ReturnValue", tail, widest=wst)
        link(g, "lrt", "MapRetake", tt(g, "trt", "Map_Retake"), tail)
        # "Fullscreen" as the last fixed link in the panel; in fullscreen "Close" at the far right of the head (Add Map Close)
        g.get("gfo", "MapFullOn"); g.branch("bfo", "@gfo.MapFullOn"); tail.append("bfo"); g.n("jfo", "sequence", count=1)
        lcl = []; link(g, "lx", "MapFull", tt(g, "tfc", "Map_Close"), lcl, add="Add Map Close"); lfu = []; link(g, "lf", "MapFull", tt(g, "tff", "Map_Full"), lfu)
        g.chain(*tail, *lcl, "jfo"); g.chain("bfo:else", *lfu, "jfo"); tail[:] = ["jfo:then_0"]
        g.get("gto", "MapTgtOn"); g.get("gok", "NavOk"); g.call("go", K_MATH, "BooleanAND", inp={"A": "@gto.MapTgtOn", "B": "@gok.NavOk"}); g.branch("bgo", "@go.ReturnValue"); tail.append("bgo")
        tg = []; link(g, "lg", "MapGo", tt(g, "tg", "Nav_Go"), tg)
        g.chain(*tail); g.chain("bgo", *tg)
        return fn("Map Rebuild Links", graph=g)

    def f_retake():
        """"Retake" (play test 2026-11-19: new light without taking tiles again all the time): the session forgets which tiles it took
        (MapDone, MapMiss), so they are taken again as Jodi walks and their PNGs overwritten; her tile and the eight around it at once in
        turn (recording on). Nothing is deleted - a tile she does not pass keeps its old picture."""
        g = G(); tail = ["entry"]
        for v in ("MapDone", "MapMiss"):
            g.get("g" + v, v); g.call("c" + v, K_MAP, "Map_Clear", inp={"TargetMap": "@g%s.%s" % (v, v)}); tail.append("c" + v)
        g.get("gpl", "Player"); g.call("pv", K_SYS, "IsValid", inp={"Object": "@gpl.Player"}); g.get("gnr", "MapNoRecord"); g.call("rec", K_MATH, "Not_PreBool", inp={"A": "@gnr.MapNoRecord"})
        g.call("go", K_MATH, "BooleanAND", inp={"A": "@pv.ReturnValue", "B": "@rec.ReturnValue"}); g.branch("bgo", "@go.ReturnValue"); tail.append("bgo")
        g.n("ub", "call_self", function="Map Update Band"); g.n("cn", "call_self", function="Map Capture Next"); g.n("rd", "call_self", function="Map Redraw")
        g.chain(*tail, "ub", "cn", "rd"); g.chain("bgo:else", "rd")
        return fn("Map Retake", graph=g)

    def f_open():
        """The Navigation tab opened (Select Page, after Rebuild Nav): the view on Jodi and her band, her tile captured afresh (recording
        on), links and picture."""
        g = G(); g.get("gp", "Panel"); g.call("gm", W_PANEL, "Get Nav Map", inp={"self": "@gp.Panel"}); g.set("sv", "MapView", inp={"MapView": "@gm.map"}); set_manager(g, "svm", W_NAVMAP, "@gm.map")
        g.set("tg", "MapTgtOn", inp={"MapTgtOn": "false"}); g.set("tb", "MapTgtBed", inp={"MapTgtBed": "-1"})
        g.get("gpx", "MapPx"); g.call("pz", K_MATH, "Less_FloatFloat", inp={"A": "@gpx.MapPx", "B": str(PX_MIN)}); g.branch("bpz", "@pz.ReturnValue")
        g.set("spx", "MapPx", inp={"MapPx": str(PX_DEFAULT)})
        g.get("gpl", "Player"); g.call("pv", K_SYS, "IsValid", inp={"Object": "@gpl.Player"}); g.branch("bpv", "@pv.ReturnValue")
        g.n("rl", "call_self", function="Map Read Level"); g.n("ub", "call_self", function="Map Update Band"); g.n("ce", "call_self", function="Map Center")
        g.get("gnr", "MapNoRecord"); g.branch("bnr", "@gnr.MapNoRecord")
        g.n("ft", "call_self", function="Map Jodi Feet"); g.n("to", "call_self", function="Map Tile Of", inp={"v": "@ft.feet"}); g.n("jb", "call_self", function="Map Jodi Band")
        g.n("cap", "call_self", function="Map Capture Tile", inp={"x": "@to.x", "y": "@to.y", "band": "@jb.band"})
        g.n("lk", "call_self", function="Map Rebuild Links"); g.n("rd", "call_self", function="Map Redraw")
        # the map off (Options > Map): map and its links hidden, nothing else
        g.get("gof", "MapOff"); g.call("on", K_MATH, "Not_PreBool", inp={"A": "@gof.MapOff"}); g.get("gp2", "Panel")
        g.call("shw", W_PANEL, "Set Map Shown", inp={"self": "@gp2.Panel", "shown": "@on.ReturnValue"}); g.branch("bof", "@gof.MapOff")
        g.get("gnb", "NavBeds"); g.set("smb", "MapBeds", inp={"MapBeds": "@gnb.NavBeds"})   # Rebuild Nav just scanned them
        g.n("svd", "call_self", function="Map Scan Vends"); g.set("slm", "MapLegMask", inp={"MapLegMask": "-1"})   # the legend built anew with the first picture
        g.chain("entry", "shw", "bof"); g.chain("bof:else", "sv", "svm", "smb", "svd", "slm", "tg", "tb", "bpz", "spx", "bpv", "rl", "ub", "ce", "bnr", "lk", "rd"); g.chain("bpz:else", "bpv"); g.chain("bpv:else", "lk")
        g.chain("bnr:else", "cap", "lk")
        return fn("Map Open", graph=g)


    def f_full_open():
        """Fullscreen map (spec 2026-11-19): from the Navigation tab (MapFullFromPanel) or from the game (quick action: the panel opens
        on Navigation first, the page it had is kept to go back to). The panel's MapFull layer shows (rim FULL_RIM of the screen
        height), MapView becomes its own W_NavMap; links, label and legend go there (the panel's FullOn)."""
        g = G(); g.get("gof", "MapOff"); g.branch("bof", "@gof.MapOff"); g.get("gpo", "PanelOpen"); g.branch("bpo", "@gpo.PanelOpen")
        g.set("fp1", "MapFullFromPanel", inp={"MapFullFromPanel": "true"})
        g.get("gpg", "Page"); g.set("spp", "MapFullPrevPage", inp={"MapFullPrevPage": "@gpg.Page"}); g.set("fp0", "MapFullFromPanel", inp={"MapFullFromPanel": "false"})
        g.n("op", "call_self", function="Open Panel"); g.n("sp", "call_self", function="Select Page", inp={"name": "Navigation"})
        g.n("j", "sequence", count=1)
        # a key that opened it is still down: its release must not close it again (Map Full Key)
        g.get("gqk", "QFromKey"); g.call("arm", K_MATH, "Not_PreBool", inp={"A": "@gqk.QFromKey"}); g.get("gfp", "MapFullFromPanel")
        g.call("arm2", K_MATH, "BooleanOR", inp={"A": "@arm.ReturnValue", "B": "@gfp.MapFullFromPanel"}); g.set("sar", "MapFullArm", inp={"MapFullArm": "@arm2.ReturnValue"})
        g.set("son", "MapFullOn", inp={"MapFullOn": "true"})
        g.get("gpc", "PC"); g.call("vs", E_PC, "GetViewportSize", inp={"self": "@gpc.PC"}); g.call("vh", K_MATH, "Conv_IntToFloat", inp={"InInt": "@vs.SizeY"})
        g.call("sc", "/Script/UMG.WidgetLayoutLibrary", "GetViewportScale"); g.call("mx", K_MATH, "FMax", inp={"A": "@sc.ReturnValue", "B": "0.01"})
        g.call("px", K_MATH, "Multiply_FloatFloat", inp={"A": "@vh.ReturnValue", "B": str(FULL_RIM)}); g.call("pad", K_MATH, "Divide_FloatFloat", inp={"A": "@px.ReturnValue", "B": "@mx.ReturnValue"})
        g.get("gp", "Panel"); g.call("smf", W_PANEL, "Set Map Full", inp={"self": "@gp.Panel", "on": "true", "pad": "@pad.ReturnValue"})
        g.get("gp2", "Panel"); g.call("gfm", W_PANEL, "Get Full Map", inp={"self": "@gp2.Panel"}); g.set("smv", "MapView", inp={"MapView": "@gfm.map"}); set_manager(g, "svm", W_NAVMAP, "@gfm.map")
        g.set("slm", "MapLegMask", inp={"MapLegMask": "-1"}); g.n("lb", "call_self", function="Map Show Label"); g.n("lk", "call_self", function="Map Rebuild Links"); g.n("rd", "call_self", function="Map Redraw")
        g.chain("entry", "bof"); g.chain("bof:else", "bpo", "fp1", "j"); g.chain("bpo:else", "spp", "fp0", "op", "sp", "j")
        g.chain("j:then_0", "sar", "son", "smf", "smv", "svm", "slm", "lb", "lk", "rd")
        return fn("Map Full Open", graph=g)

    def f_full_reset():
        """The fullscreen layer off, the map back in the Navigation tab (MapView) - Close Panel calls it too (a teleport closes all)."""
        g = G(); g.get("gfo", "MapFullOn"); g.branch("b", "@gfo.MapFullOn"); g.set("sof", "MapFullOn", inp={"MapFullOn": "false"})
        g.get("gp", "Panel"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gp.Panel"}); g.branch("biv", "@iv.ReturnValue")
        g.get("gp1", "Panel"); g.call("smf", W_PANEL, "Set Map Full", inp={"self": "@gp1.Panel", "on": "false", "pad": "0.0"})
        g.get("gp2", "Panel"); g.call("gnm", W_PANEL, "Get Nav Map", inp={"self": "@gp2.Panel"}); g.set("smv", "MapView", inp={"MapView": "@gnm.map"})
        g.set("slm", "MapLegMask", inp={"MapLegMask": "-1"})
        g.chain("entry", "b", "sof", "biv", "smf", "smv", "slm")
        return fn("Map Full Reset", graph=g)

    def f_full_close():
        """Esc, the panel key, "Close" or the quick action's key: back where it came from - the Navigation tab (links, legend and
        picture there again), or the game (the panel's page as it was, the panel closed)."""
        g = G(); g.n("rs", "call_self", function="Map Full Reset"); g.get("gfp", "MapFullFromPanel"); g.branch("bfp", "@gfp.MapFullFromPanel")
        g.n("lb", "call_self", function="Map Show Label"); g.n("lk", "call_self", function="Map Rebuild Links"); g.n("rd", "call_self", function="Map Redraw")
        g.get("gpp", "MapFullPrevPage"); g.set("spg", "Page", inp={"Page": "@gpp.MapFullPrevPage"}); g.n("cp", "call_self", function="Close Panel")
        g.chain("entry", "rs", "bfp", "lb", "lk", "rd"); g.chain("bfp:else", "spg", "cp")
        return fn("Map Full Close", graph=g)

    def f_full_toggle():
        """The "Fullscreen" / "Close" link and the quick action mapfull."""
        g = G(); g.get("gfo", "MapFullOn"); g.branch("b", "@gfo.MapFullOn"); g.n("cl", "call_self", function="Map Full Close"); g.n("op", "call_self", function="Map Full Open")
        g.chain("entry", "b", "cl"); g.chain("b:else", "op")
        return fn("Map Full Toggle", graph=g)

    def f_full_key():
        """The panel's key-up (display name `key`) while the fullscreen map is open: the quick action mapfull's own key closes it
        (yes) - except the release of the key press that opened it (MapFullArm false: armed now)."""
        g = G(); g.get("gfo", "MapFullOn"); g.branch("bon", "@gfo.MapFullOn"); g.n("rn", "return_new", inp={"yes": "false"})
        g.call("kn", K_STR, "Conv_StringToName", inp={"InString": "@entry.key"}); g.get("gkk", "KeyBindKeys"); g.call("fk", K_ARR, "Array_Find", inp={"TargetArray": "@gkk.KeyBindKeys", "ItemToFind": "@kn.ReturnValue"})
        g.call("has", K_MATH, "GreaterEqual_IntInt", inp={"A": "@fk.ReturnValue", "B": "0"}); g.branch("bhas", "@has.ReturnValue"); g.n("rn2", "return_new", inp={"yes": "false"})
        g.get("gki", "KeyBindItems"); g.call("it", K_ARR, "Array_Get", inp={"TargetArray": "@gki.KeyBindItems", "Index": "@fk.ReturnValue"})
        g.call("ism", K_STR, "EqualEqual_StrStr", inp={"A": "@it.Item", "B": "mapfull"}); g.branch("bism", "@ism.ReturnValue"); g.n("rn3", "return_new", inp={"yes": "false"})
        g.get("gar", "MapFullArm"); g.branch("bar", "@gar.MapFullArm"); g.set("sar", "MapFullArm", inp={"MapFullArm": "true"}); g.n("rn4", "return_new", inp={"yes": "false"})
        g.lit_bool("lty", "true"); g.link("lty.ReturnValue", "return.yes")
        g.chain("entry", "bon", "bhas", "bism", "bar", "return"); g.chain("bon:else", "rn"); g.chain("bhas:else", "rn2"); g.chain("bism:else", "rn3"); g.chain("bar:else", "sar", "rn4")
        return fn("Map Full Key", [param("key", "string")], [param("yes", "bool")], graph=g)

    def f_center():
        """View on Jodi: her place in the middle, her band shown."""
        g = G(); g.get("gpl", "Player"); g.call("pv", K_SYS, "IsValid", inp={"Object": "@gpl.Player"}); g.branch("bpv", "@pv.ReturnValue")
        g.get("gpl2", "Player"); g.call("l", E_ACTOR, "K2_GetActorLocation", inp={"self": "@gpl2.Player"}); g.call("b", K_MATH, "BreakVector", inp={"InVec": "@l.ReturnValue"})
        g.set("sx", "MapCX", inp={"MapCX": "@b.X"}); g.set("sy", "MapCY", inp={"MapCY": "@b.Y"})
        g.n("jb", "call_self", function="Map Jodi Band"); g.set("sb", "MapShowBand", inp={"MapShowBand": "@jb.band"})
        g.n("lk", "call_self", function="Map Rebuild Links"); g.n("rd", "call_self", function="Map Redraw")
        g.chain("entry", "bpv", "sx", "sy", "sb", "lk", "rd")
        return fn("Map Center", graph=g)

    def f_step(name, delta):
        """Band up / down by one, relative to the shown band (from outside: from Jodi's inside band)."""
        g = G(); g.get("gsb", "MapShowBand"); g.call("out", K_MATH, "EqualEqual_IntInt", inp={"A": "@gsb.MapShowBand", "B": str(OUT_BAND)})
        g.get("gb", "MapBand"); g.call("base", K_MATH, "SelectInt", inp={"A": "@gb.MapBand", "B": "@gsb.MapShowBand", "bPickA": "@out.ReturnValue"})
        g.call("nb", K_MATH, "Add_IntInt", inp={"A": "@base.ReturnValue", "B": str(delta)}); g.set("sb", "MapShowBand", inp={"MapShowBand": "@nb.ReturnValue"})
        g.n("lk", "call_self", function="Map Rebuild Links"); g.n("rd", "call_self", function="Map Redraw"); g.chain("entry", "sb", "lk", "rd")
        return fn(name, graph=g)

    def f_outside():
        """Outside <-> inside (Jodi's band)."""
        g = G(); g.get("gsb", "MapShowBand"); g.call("out", K_MATH, "EqualEqual_IntInt", inp={"A": "@gsb.MapShowBand", "B": str(OUT_BAND)})
        g.get("gb", "MapBand"); g.call("nb", K_MATH, "SelectInt", inp={"A": "@gb.MapBand", "B": str(OUT_BAND), "bPickA": "@out.ReturnValue"})
        g.set("sb", "MapShowBand", inp={"MapShowBand": "@nb.ReturnValue"})
        g.n("lk", "call_self", function="Map Rebuild Links"); g.n("rd", "call_self", function="Map Redraw"); g.chain("entry", "sb", "lk", "rd")
        return fn("Map Outside", graph=g)

    def f_record():
        """Recording on / off (saved)."""
        g = G(); g.get("g", "MapNoRecord"); g.call("n", K_MATH, "Not_PreBool", inp={"A": "@g.MapNoRecord"}); g.set("s", "MapNoRecord", inp={"MapNoRecord": "@n.ReturnValue"})
        g.n("sv", "call_self", function="Save Settings"); g.n("lk", "call_self", function="Map Rebuild Links"); g.chain("entry", "s", "sv", "lk")
        return fn("Map Record Toggle", graph=g)

    def f_style():
        """Next style (saved): every tile is taken in all styles (Map Capture Tile), so only the cached textures go (MapTex, MapMiss)
        and the map is drawn again from the new style's folder."""
        g = G(); g.get("g", "MapStyle"); g.call("a", K_MATH, "Add_IntInt", inp={"A": "@g.MapStyle", "B": "1"}); g.call("m", K_MATH, "Percent_IntInt", inp={"A": "@a.ReturnValue", "B": str(len(STYLES))})
        g.set("s", "MapStyle", inp={"MapStyle": "@m.ReturnValue"}); g.n("sv", "call_self", function="Save Settings")
        tail = ["entry", "s", "sv"]
        for v in ("MapTex", "MapMiss"):
            g.get("g" + v, v); g.call("c" + v, K_MAP, "Map_Clear", inp={"TargetMap": "@g%s.%s" % (v, v)}); tail.append("c" + v)
        g.n("lk", "call_self", function="Map Rebuild Links"); g.n("rd", "call_self", function="Map Redraw")
        # only the active style is taken (MapOneStyle): what this session took is not there in the new style - forgotten, so the
        # tiles around Jodi are taken in it as she walks
        g.get("gos", "MapOneStyle"); g.branch("bos", "@gos.MapOneStyle"); g.get("gdn", "MapDone"); g.call("cdn", K_MAP, "Map_Clear", inp={"TargetMap": "@gdn.MapDone"})
        g.chain(*tail, "bos", "cdn", "lk", "rd"); g.chain("bos:else", "lk")
        return fn("Map Style Next", graph=g)

    def f_poll():
        """Navigation tab open: the map is redrawn every REDRAW_EVERY seconds (markers move, new tiles come)."""
        g = G(); g.call("now", K_GS, "GetRealTimeSeconds"); g.get("gn", "MapNextDraw")
        g.call("due", K_MATH, "GreaterEqual_FloatFloat", inp={"A": "@now.ReturnValue", "B": "@gn.MapNextDraw"}); g.branch("bd", "@due.ReturnValue")
        g.call("nx", K_MATH, "Add_FloatFloat", inp={"A": "@now.ReturnValue", "B": str(REDRAW_EVERY)}); g.set("sn", "MapNextDraw", inp={"MapNextDraw": "@nx.ReturnValue"})
        g.n("rd", "call_self", function="Map Redraw"); g.get("gof", "MapOff"); g.branch("bof", "@gof.MapOff")
        g.chain("entry", "bof"); g.chain("bof:else", "bd", "sn", "rd")
        return fn("Map Poll", graph=g)

    def f_wheel():
        """Zoom by `notches` around the mouse point (x, y): the world point under it stays there; PX_MIN..PX_MAX pixels per tile."""
        g = G(); g.n("w", "call_self", function="Map To World", inp={"sx": "@entry.x", "sy": "@entry.y"})
        g.set("swx", "MapDownX", inp={"MapDownX": "@w.wx"}); g.set("swy", "MapDownY", inp={"MapDownY": "@w.wy"})   # held over the change of MapPx
        g.call("pw", K_MATH, "MultiplyMultiply_FloatFloat", inp={"Base": str(ZOOM_STEP), "Exp": "@entry.notches"})
        g.get("gp", "MapPx"); g.call("np", K_MATH, "Multiply_FloatFloat", inp={"A": "@gp.MapPx", "B": "@pw.ReturnValue"})
        g.call("cl", K_MATH, "FClamp", inp={"Value": "@np.ReturnValue", "Min": str(PX_MIN), "Max": str(PX_MAX)}); g.set("sp", "MapPx", inp={"MapPx": "@cl.ReturnValue"})
        g.get("gp2", "MapPx"); g.call("p", K_MATH, "Divide_FloatFloat", inp={"A": "@gp2.MapPx", "B": str(TILE_CM)})
        g.call("oy", K_MATH, "Subtract_FloatFloat", inp={"A": "@entry.y", "B": _half(g, "hh", "MapH")}); g.call("cy", K_MATH, "Divide_FloatFloat", inp={"A": "@oy.ReturnValue", "B": "@p.ReturnValue"})
        g.get("gwx", "MapDownX"); g.call("ncx", K_MATH, "Add_FloatFloat", inp={"A": "@gwx.MapDownX", "B": "@cy.ReturnValue"}); g.set("scx", "MapCX", inp={"MapCX": "@ncx.ReturnValue"})
        g.call("ox", K_MATH, "Subtract_FloatFloat", inp={"A": "@entry.x", "B": _half(g, "hw", "MapW")}); g.call("cx", K_MATH, "Divide_FloatFloat", inp={"A": "@ox.ReturnValue", "B": "@p.ReturnValue"})
        g.get("gwy", "MapDownY"); g.call("ncy", K_MATH, "Subtract_FloatFloat", inp={"A": "@gwy.MapDownY", "B": "@cx.ReturnValue"}); g.set("scy", "MapCY", inp={"MapCY": "@ncy.ReturnValue"})
        g.n("rd", "call_self", function="Map Redraw"); g.chain("entry", "swx", "swy", "sp", "scx", "scy", "rd")
        return fn("Map Wheel", [param("notches", "float"), param("x", "float"), param("y", "float")], graph=g)

    def f_press():
        g = G(); g.set("sp", "MapPressed", inp={"MapPressed": "true"}); g.set("sm", "MapMoved", inp={"MapMoved": "false"})
        tail = ["entry", "sp", "sm"]
        for v, a in (("MapDownX", "x"), ("MapDownY", "y"), ("MapLastX", "x"), ("MapLastY", "y")):
            g.set("s" + v, v, inp={v: "@entry.%s" % a}); tail.append("s" + v)
        g.chain(*tail)
        return fn("Map Press", [param("x", "float"), param("y", "float")], graph=g)

    def f_move():
        """Mouse moved over the map: while pressed, a drag beyond CLICK_PX pans the view with the mouse."""
        g = G(); g.get("gpr", "MapPressed"); g.branch("bpr", "@gpr.MapPressed")
        g.get("glx", "MapLastX"); g.get("gly", "MapLastY")
        g.call("dx", K_MATH, "Subtract_FloatFloat", inp={"A": "@entry.x", "B": "@glx.MapLastX"}); g.call("dy", K_MATH, "Subtract_FloatFloat", inp={"A": "@entry.y", "B": "@gly.MapLastY"})
        g.set("slx", "MapLastX", inp={"MapLastX": "@entry.x"}); g.set("sly", "MapLastY", inp={"MapLastY": "@entry.y"})
        g.get("gdx", "MapDownX"); g.get("gdy", "MapDownY")
        g.call("tx", K_MATH, "Subtract_FloatFloat", inp={"A": "@entry.x", "B": "@gdx.MapDownX"}); g.call("ty", K_MATH, "Subtract_FloatFloat", inp={"A": "@entry.y", "B": "@gdy.MapDownY"})
        g.call("tv", K_MATH, "MakeVector2D", inp={"X": "@tx.ReturnValue", "Y": "@ty.ReturnValue"}); g.call("tl", K_MATH, "VSize2D", inp={"A": "@tv.ReturnValue"})
        g.call("far", K_MATH, "Greater_FloatFloat", inp={"A": "@tl.ReturnValue", "B": str(CLICK_PX)}); g.get("gmv", "MapMoved")
        g.call("mv", K_MATH, "BooleanOR", inp={"A": "@far.ReturnValue", "B": "@gmv.MapMoved"}); g.set("smv", "MapMoved", inp={"MapMoved": "@mv.ReturnValue"}); g.branch("bmv", "@mv.ReturnValue")
        g.get("gp", "MapPx"); g.call("p", K_MATH, "Divide_FloatFloat", inp={"A": "@gp.MapPx", "B": str(TILE_CM)})
        # the picture follows the mouse: down = -X on screen -> the view's X grows; right = +Y -> the view's Y shrinks
        g.call("ddx", K_MATH, "Divide_FloatFloat", inp={"A": "@dy.ReturnValue", "B": "@p.ReturnValue"}); g.get("gcx", "MapCX")
        g.call("ncx", K_MATH, "Add_FloatFloat", inp={"A": "@gcx.MapCX", "B": "@ddx.ReturnValue"}); g.set("scx", "MapCX", inp={"MapCX": "@ncx.ReturnValue"})
        g.call("ddy", K_MATH, "Divide_FloatFloat", inp={"A": "@dx.ReturnValue", "B": "@p.ReturnValue"}); g.get("gcy", "MapCY")
        g.call("ncy", K_MATH, "Subtract_FloatFloat", inp={"A": "@gcy.MapCY", "B": "@ddy.ReturnValue"}); g.set("scy", "MapCY", inp={"MapCY": "@ncy.ReturnValue"})
        g.n("rd", "call_self", function="Map Redraw")
        # MapLast* only after the pan: dx / dy are pure and read MapLast* when the pan uses them (set first, the step was 0 - play test 2026-11-17)
        g.chain("entry", "bpr", "smv", "bmv", "scx", "scy", "slx", "sly", "rd"); g.chain("bmv:else", "slx", "sly")
        return fn("Map Move", [param("x", "float"), param("y", "float")], graph=g)

    def f_release():
        """Mouse released: no drag -> a click: the target at that point (a bed marker within BED_HIT picks the bed), links + picture."""
        g = G(); g.set("sp", "MapPressed", inp={"MapPressed": "false"}); g.get("gmv", "MapMoved"); g.branch("bmv", "@gmv.MapMoved")
        g.n("w", "call_self", function="Map To World", inp={"sx": "@entry.x", "sy": "@entry.y"})
        g.get("gsb", "MapShowBand"); g.call("out", K_MATH, "EqualEqual_IntInt", inp={"A": "@gsb.MapShowBand", "B": str(OUT_BAND)})
        g.call("bf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@gsb.MapShowBand"}); g.call("bz", K_MATH, "Multiply_FloatFloat", inp={"A": "@bf.ReturnValue", "B": str(BAND_CM)})
        g.call("bz2", K_MATH, "Add_FloatFloat", inp={"A": "@bz.ReturnValue", "B": "1.0"})   # on the band's floor (Map Mark Spot: same band)
        g.get("gfz", "MapFeetZ"); g.call("z", K_MATH, "SelectFloat", inp={"A": "@gfz.MapFeetZ", "B": "@bz2.ReturnValue", "bPickA": "@out.ReturnValue"})
        g.call("v", K_MATH, "MakeVector", inp={"X": "@w.wx", "Y": "@w.wy", "Z": "@z.ReturnValue"}); g.set("st", "MapTgt", inp={"MapTgt": "@v.ReturnValue"})
        g.set("so", "MapTgtOn", inp={"MapTgtOn": "true"}); g.set("sb0", "MapTgtBed", inp={"MapTgtBed": "-1"}); g.set("sd0", "MapHitD", inp={"MapHitD": str(float(BED_HIT))})
        g.get("gnb", "NavBeds"); g.foreach("fe", "@gnb.NavBeds"); g.call("bl", E_ACTOR, "K2_GetActorLocation", inp={"self": "@fe.Array Element"})
        g.n("ms", "call_self", function="Map Mark Spot", inp={"v": "@bl.ReturnValue"})
        g.call("ddx", K_MATH, "Subtract_FloatFloat", inp={"A": "@ms.sx", "B": "@entry.x"}); g.call("ddy", K_MATH, "Subtract_FloatFloat", inp={"A": "@ms.sy", "B": "@entry.y"})
        g.call("dv", K_MATH, "MakeVector2D", inp={"X": "@ddx.ReturnValue", "Y": "@ddy.ReturnValue"}); g.call("dl", K_MATH, "VSize2D", inp={"A": "@dv.ReturnValue"})
        g.get("ghd", "MapHitD"); g.call("near", K_MATH, "Less_FloatFloat", inp={"A": "@dl.ReturnValue", "B": "@ghd.MapHitD"})
        g.n("hbd", "call_self", function="Map Kind Hidden", inp={"kind": str(K_BED)}); g.call("nhb", K_MATH, "Not_PreBool", inp={"A": "@hbd.yes"})   # hidden beds take no click
        g.call("hit0", K_MATH, "BooleanAND", inp={"A": "@near.ReturnValue", "B": "@ms.ok"}); g.call("hit", K_MATH, "BooleanAND", inp={"A": "@hit0.ReturnValue", "B": "@nhb.ReturnValue"}); g.branch("bh", "@hit.ReturnValue")
        g.set("sb", "MapTgtBed", inp={"MapTgtBed": "@fe.Array Index"}); g.set("sd", "MapHitD", inp={"MapHitD": "@dl.ReturnValue"}); g.set("st2", "MapTgt", inp={"MapTgt": "@bl.ReturnValue"})
        g.n("lk", "call_self", function="Map Rebuild Links"); g.n("rd", "call_self", function="Map Redraw")
        g.chain("entry", "sp", "bmv"); g.chain("bmv:else", "st", "so", "sb0", "sd0", "fe"); g.chain("fe", "bh", "sb", "sd", "st2"); g.chain("fe:Completed", "lk", "rd")
        return fn("Map Release", [param("x", "float"), param("y", "float")], graph=g)

    def f_teleport():
        """Link "Teleport" under a target: a bed picked -> Nav Teleport of it; else the target's point projected onto the navmesh (inside:
        within the shown band, outside: tall extent) - none: hint, Jodi stays; found: as Nav Teleport (end free camera, flight and poses,
        stand there, speed 0, her facing kept, followers along, panel closed)."""
        g = G(); g.get("gto", "MapTgtOn"); g.get("gok", "NavOk"); g.call("can", K_MATH, "BooleanAND", inp={"A": "@gto.MapTgtOn", "B": "@gok.NavOk"}); g.branch("bcan", "@can.ReturnValue")
        g.get("gtb", "MapTgtBed"); g.call("isb", K_MATH, "GreaterEqual_IntInt", inp={"A": "@gtb.MapTgtBed", "B": "0"}); g.branch("bisb", "@isb.ReturnValue")
        g.n("nt", "call_self", function="Nav Teleport", inp={"index": "@gtb.MapTgtBed"})
        g.get("gsb", "MapShowBand"); g.call("out", K_MATH, "EqualEqual_IntInt", inp={"A": "@gsb.MapShowBand", "B": str(OUT_BAND)})
        g.call("ext", K_MATH, "SelectVector", inp={"A": NAV_EXTENT_OUT, "B": NAV_EXTENT_IN, "bPickA": "@out.ReturnValue"})
        g.get("gtg", "MapTgt"); g.call("up", K_MATH, "Add_VectorVector", inp={"A": "@gtg.MapTgt", "B": "(X=0,Y=0,Z=%s)" % (BAND_CM / 2)})   # the middle of the band
        g.call("pj", K_NAVSYS, "K2_ProjectPointToNavigation", inp={"Point": "@up.ReturnValue", "NavData": "None", "FilterClass": "None", "QueryExtent": "@ext.ReturnValue"})
        g.branch("bpj", "@pj.ReturnValue"); g.set("sps1", "MapSpot", inp={"MapSpot": "@pj.ProjectedLocation"})
        # a level without a navmesh (Jodi's office has none - "No walkable spot" on every click, play test 2026-11-21): Jodi's own
        # place is not on one either (bjn:else), so the floor under the click is found with a line straight down - from just below
        # the map's cut to below the floor (her floor: around her feet; another floor: around its band; outside: from above the
        # trees) - and taken when it is flat enough to stand on. With a navmesh a click off it stays "No walkable spot" (walls).
        g.n("jf0", "call_self", function="Map Jodi Feet")
        g.call("pjj", K_NAVSYS, "K2_ProjectPointToNavigation", inp={"Point": "@jf0.feet", "NavData": "None", "FilterClass": "None", "QueryExtent": "(X=200,Y=200,Z=300)"}); g.branch("bjn", "@pjj.ReturnValue")
        g.get("gfz", "MapFeetZ"); g.get("gmb", "MapBand"); g.call("same", K_MATH, "EqualEqual_IntInt", inp={"A": "@gsb.MapShowBand", "B": "@gmb.MapBand"})
        g.call("bf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@gsb.MapShowBand"}); g.call("bz", K_MATH, "Multiply_FloatFloat", inp={"A": "@bf.ReturnValue", "B": str(BAND_CM)})
        g.call("t_same", K_MATH, "Add_FloatFloat", inp={"A": "@gfz.MapFeetZ", "B": str(CUT_IN - 10.0)}); g.call("b_same", K_MATH, "Subtract_FloatFloat", inp={"A": "@gfz.MapFeetZ", "B": "300.0"})
        g.call("t_band", K_MATH, "Add_FloatFloat", inp={"A": "@bz.ReturnValue", "B": str(BAND_CM + BAND_HYST)}); g.call("b_band", K_MATH, "Subtract_FloatFloat", inp={"A": "@bz.ReturnValue", "B": str(BAND_HYST)})
        g.call("t_out", K_MATH, "Add_FloatFloat", inp={"A": "@gfz.MapFeetZ", "B": str(CUT_OUT)}); g.call("b_out", K_MATH, "Subtract_FloatFloat", inp={"A": "@gfz.MapFeetZ", "B": "5000.0"})
        g.call("t_in", K_MATH, "SelectFloat", inp={"A": "@t_same.ReturnValue", "B": "@t_band.ReturnValue", "bPickA": "@same.ReturnValue"}); g.call("b_in", K_MATH, "SelectFloat", inp={"A": "@b_same.ReturnValue", "B": "@b_band.ReturnValue", "bPickA": "@same.ReturnValue"})
        g.call("ttop", K_MATH, "SelectFloat", inp={"A": "@t_out.ReturnValue", "B": "@t_in.ReturnValue", "bPickA": "@out.ReturnValue"}); g.call("tbot", K_MATH, "SelectFloat", inp={"A": "@b_out.ReturnValue", "B": "@b_in.ReturnValue", "bPickA": "@out.ReturnValue"})
        g.call("tgb", K_MATH, "BreakVector", inp={"InVec": "@gtg.MapTgt"})
        g.call("ts0", K_MATH, "MakeVector", inp={"X": "@tgb.X", "Y": "@tgb.Y", "Z": "@ttop.ReturnValue"}); g.call("te0", K_MATH, "MakeVector", inp={"X": "@tgb.X", "Y": "@tgb.Y", "Z": "@tbot.ReturnValue"})
        g.get("gplt", "Player"); g.n("ign", "make_array", count=1, type="object:" + E_ACTOR, inp={"[0]": "@gplt.Player"})
        g.call("ftr", K_SYS, "LineTraceSingle", inp={"Start": "@ts0.ReturnValue", "End": "@te0.ReturnValue", "TraceChannel": "TraceTypeQuery1", "bTraceComplex": "false",
                                                     "ActorsToIgnore": "@ign.Array", "DrawDebugType": "None", "bIgnoreSelf": "true",
                                                     "TraceColor": "(R=1,G=0,B=0,A=1)", "TraceHitColor": "(R=0,G=1,B=0,A=1)", "DrawTime": "5.0"})
        g.call("fbh", K_GS, "BreakHitResult", inp={"Hit": "@ftr.OutHit"}); g.call("fnb", K_MATH, "BreakVector", inp={"InVec": "@fbh.ImpactNormal"})
        g.call("flat", K_MATH, "Greater_FloatFloat", inp={"A": "@fnb.Z", "B": "0.7"}); g.call("npen", K_MATH, "Not_PreBool", inp={"A": "@fbh.bInitialOverlap"})
        g.call("fok0", K_MATH, "BooleanAND", inp={"A": "@ftr.ReturnValue", "B": "@flat.ReturnValue"}); g.call("fok", K_MATH, "BooleanAND", inp={"A": "@fok0.ReturnValue", "B": "@npen.ReturnValue"}); g.branch("bfl", "@fok.ReturnValue")
        g.set("sps2", "MapSpot", inp={"MapSpot": "@fbh.ImpactPoint"})
        g.call("nh", K_TXT, "Conv_StringToText", inp={"InString": ts(g, "tns", "Map_NoSpot")}); g.get("gph", "Panel"); g.call("sh", W_PANEL, "Set Nav Hint", inp={"self": "@gph.Panel", "hint": "@nh.ReturnValue"})
        g.n("sfc", "call_self", function="Stop Free Cam"); g.n("fst", "call_self", function="Fly Stop", inp={"mode": "1"})
        g.n("eip", "call_self", function="End Idle Pose"); g.n("sps", "call_self", function="Stop Pose")
        g.n("jf", "call_self", function="Map Jodi Feet"); g.call("hv", K_MATH, "MakeVector", inp={"X": "0.0", "Y": "0.0", "Z": "@jf.half"})
        g.get("gsp", "MapSpot"); g.call("dst", K_MATH, "Add_VectorVector", inp={"A": "@gsp.MapSpot", "B": "@hv.ReturnValue"})
        g.get("gpl", "Player"); g.call("rot", E_ACTOR, "K2_GetActorRotation", inp={"self": "@gpl.Player"}); g.call("rb", K_MATH, "BreakRotator", inp={"InRot": "@rot.ReturnValue"})
        g.call("yaw", K_MATH, "MakeRotator", inp={"Roll": "0.0", "Pitch": "0.0", "Yaw": "@rb.Yaw"})
        g.get("gpl2", "Player"); g.call("tp", E_ACTOR, "K2_TeleportTo", inp={"self": "@gpl2.Player", "DestLocation": "@dst.ReturnValue", "DestRotation": "@yaw.ReturnValue"}); g.branch("btp", "@tp.ReturnValue")
        g.get("gpl3", "Player"); g.call("sal", E_ACTOR, "K2_SetActorLocation", inp={"self": "@gpl3.Player", "NewLocation": "@dst.ReturnValue", "bSweep": "false", "bTeleport": "true"})
        g.get("gpl4", "Player"); g.get("gcm", "CharacterMovement", cls=E_CHAR); g.link("gpl4.Player", "gcm.self")
        g.call("stp", "/Script/Engine.MovementComponent", "StopMovementImmediately", inp={"self": "@gcm.CharacterMovement"})
        g.get("gpl5", "Player"); g.call("fw", E_ACTOR, "GetActorForwardVector", inp={"self": "@gpl5.Player"}); g.call("fw2", K_MATH, "Multiply_VectorFloat", inp={"A": "@fw.ReturnValue", "B": "200.0"})
        g.get("gsp2", "MapSpot"); g.call("face", K_MATH, "Add_VectorVector", inp={"A": "@gsp2.MapSpot", "B": "@fw2.ReturnValue"})
        g.get("gsp3", "MapSpot"); g.n("fol", "call_self", function="Nav Follow", inp={"spot": "@gsp3.MapSpot", "face": "@face.ReturnValue"})
        g.set("toff", "MapTgtOn", inp={"MapTgtOn": "false"}); g.n("cp", "call_self", function="Close Panel")
        g.chain("entry", "bcan", "bisb", "nt"); g.chain("bisb:else", "bpj", "sps1", "sfc", "fst", "eip", "sps", "tp", "btp", "stp"); g.chain("bpj:else", "bjn", "sh")
        g.chain("bjn:else", "ftr", "bfl", "sps2", "sfc"); g.chain("bfl:else", "sh")
        g.chain("btp:else", "sal", "stp"); g.chain("stp", "fol", "toff", "cp")
        return fn("Map Teleport", graph=g)

    MINI_SLIDERS = (("MiniSize", MINI_SIZE_RANGE, 1.0, " %"), ("MiniMargin", MINI_MARGIN_RANGE, 0.5, " %"), ("MiniZoom", MINI_ZOOM_RANGE, 5.0, " m"))
    CORNER_KEYS = ("Mini_TopLeft", "Mini_TopRight", "Mini_BottomLeft", "Mini_BottomRight"); SHAPE_KEYS = ("Mini_Square", "Mini_Round")

    def value_text(g, p, pin, unit):
        g.call(p + "s", K_STR, "Conv_FloatToString", inp={"InFloat": pin}); g.call(p + "c", K_STR, "Concat_StrStr", inp={"A": "@%ss.ReturnValue" % p, "B": unit})
        g.call(p + "t", K_TXT, "Conv_StringToText", inp={"InString": "@%sc.ReturnValue" % p}); return "@%st.ReturnValue" % p

    def f_rebuild_options():
        """Options > Map: the two checks (the map on = MapOff false), the sliders from their values (Range Slider), the corner chips
        (W_SubTab "MiniCorner<i>", the chosen one selected). The slider positions are kept (OptMini*) to see a move in Poll Map Options."""
        g = G(); tail = ["entry"]; inp = {}
        g.get("gof", "MapOff"); g.call("on", K_MATH, "Not_PreBool", inp={"A": "@gof.MapOff"}); g.get("gmo", "MiniOn")
        g.get("gnl", "MapNoLegend"); g.call("leg", K_MATH, "Not_PreBool", inp={"A": "@gnl.MapNoLegend"}); g.get("gos", "MapOneStyle")
        for k, (lo, hi), _, unit in MINI_SLIDERS:
            g.get("g" + k, k); g.n("r" + k, "call_self", function="Range Slider", inp={"value": "@g%s.%s" % (k, k), "lo": str(lo), "hi": str(hi)})
            g.set("o" + k, "Opt" + k, inp={"Opt" + k: "@r%s.v" % k}); tail.append("o" + k)
            inp[k.lower()] = "@r%s.v" % k; inp[k.lower() + " text"] = value_text(g, "vt" + k, "@g%s.%s" % (k, k), unit)
        g.get("gp", "Panel"); g.call("smo", W_PANEL, "Set Map Options", inp=dict(self="@gp.Panel", mapon="@on.ReturnValue", legend="@leg.ReturnValue", onestyle="@gos.MapOneStyle", minion="@gmo.MiniOn", **inp)); tail.append("smo")
        g.get("gp2", "Panel"); g.call("clr", W_PANEL, "Clear MiniCorner Chips", inp={"self": "@gp2.Panel"}); tail.append("clr")
        for i, key in enumerate(CORNER_KEYS):
            cw = create_widget(g, "cc%d" % i, W_SUB); set_manager(g, "cm%d" % i, W_SUB, cw)
            g.get("gco%d" % i, "MiniCorner"); g.call("eq%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": "@gco%d.MiniCorner" % i, "B": str(i)})
            g.call("ci%d" % i, W_SUB, "Init", inp={"self": cw, "group": "MiniCorner%d" % i, "caption": tt(g, "ct%d" % i, key), "selected": "@eq%d.ReturnValue" % i})
            g.get("gpc%d" % i, "Panel"); g.call("ac%d" % i, W_PANEL, "Add MiniCorner Chip", inp={"self": "@gpc%d.Panel" % i, "widget": cw})
            tail += ["cc%d_cr" % i, "cm%d" % i, "ci%d" % i, "ac%d" % i]
        g.get("gp3", "Panel"); g.call("csh", W_PANEL, "Clear MiniShape Chips", inp={"self": "@gp3.Panel"}); tail.append("csh")
        for i, key in enumerate(SHAPE_KEYS):   # square (0) / round (1)
            cw = create_widget(g, "sc%d" % i, W_SUB); set_manager(g, "sm%d" % i, W_SUB, cw); g.get("gsr%d" % i, "MiniRound")
            sel = "@gsr%d.MiniRound" % i
            if i == 0: g.call("nr%d" % i, K_MATH, "Not_PreBool", inp={"A": sel}); sel = "@nr%d.ReturnValue" % i
            g.call("si%d" % i, W_SUB, "Init", inp={"self": cw, "group": "MiniShape%d" % i, "caption": tt(g, "st%d" % i, key), "selected": sel})
            g.get("gps%d" % i, "Panel"); g.call("as%d" % i, W_PANEL, "Add MiniShape Chip", inp={"self": "@gps%d.Panel" % i, "widget": cw})
            tail += ["sc%d_cr" % i, "sm%d" % i, "si%d" % i, "as%d" % i]
        g.chain(*tail)
        return fn("Rebuild Map Options", graph=g)

    def f_poll_options():
        """Every frame on Options > Map: a check that changed -> its setting, saved; a slider that moved -> its value (Range Value,
        stepped), the value texts, saved soon (the drag goes on)."""
        g = G(); g.get("gc", "OptionsCat"); g.call("isc", K_MATH, "EqualEqual_NameName", inp={"A": "@gc.OptionsCat", "B": "Map"}); g.branch("bc", "@isc.ReturnValue")
        g.get("gp", "Panel"); g.call("gv", W_PANEL, "Get Map Options", inp={"self": "@gp.Panel"})
        # map on / off (stored inverted: MapOff)
        g.call("noff", K_MATH, "Not_PreBool", inp={"A": "@gv.mapon"}); g.get("gof", "MapOff"); g.call("dof", K_MATH, "NotEqual_BoolBool", inp={"A": "@noff.ReturnValue", "B": "@gof.MapOff"}); g.branch("bof", "@dof.ReturnValue")
        g.set("sof", "MapOff", inp={"MapOff": "@noff.ReturnValue"}); g.n("vof", "call_self", function="Save Settings")
        g.get("gmo", "MiniOn"); g.call("dmo", K_MATH, "NotEqual_BoolBool", inp={"A": "@gv.minion", "B": "@gmo.MiniOn"}); g.branch("bmo", "@dmo.ReturnValue")
        g.set("smo", "MiniOn", inp={"MiniOn": "@gv.minion"}); g.n("vmo", "call_self", function="Save Settings")
        # legend shown / not (stored inverted: MapNoLegend); the legend built anew next time the map draws
        g.call("nleg", K_MATH, "Not_PreBool", inp={"A": "@gv.legend"}); g.get("gnl", "MapNoLegend"); g.call("dnl", K_MATH, "NotEqual_BoolBool", inp={"A": "@nleg.ReturnValue", "B": "@gnl.MapNoLegend"}); g.branch("bnl", "@dnl.ReturnValue")
        g.set("snl", "MapNoLegend", inp={"MapNoLegend": "@nleg.ReturnValue"}); g.set("slm", "MapLegMask", inp={"MapLegMask": "-1"}); g.n("vnl", "call_self", function="Save Settings")
        # one style only: saved; the session forgets what it took (MapDone) - switched off, the other styles are taken as Jodi walks
        g.get("gos", "MapOneStyle"); g.call("dos", K_MATH, "NotEqual_BoolBool", inp={"A": "@gv.onestyle", "B": "@gos.MapOneStyle"}); g.branch("bos", "@dos.ReturnValue")
        g.set("sos", "MapOneStyle", inp={"MapOneStyle": "@gv.onestyle"}); g.get("gdn", "MapDone"); g.call("cdn", K_MAP, "Map_Clear", inp={"TargetMap": "@gdn.MapDone"}); g.n("vos", "call_self", function="Save Settings")
        g.chain("entry", "bc", "bof", "sof", "vof", "bnl"); g.chain("bof:else", "bnl"); g.chain("bnl", "snl", "slm", "vnl", "bos"); g.chain("bnl:else", "bos"); g.chain("bos", "sos", "cdn", "vos", "bmo"); g.chain("bos:else", "bmo")
        g.chain("bmo", "smo", "vmo", "s0"); g.chain("bmo:else", "s0")
        # sliders: any moved?
        same = "true"; i = 0
        for k, _, _, _ in MINI_SLIDERS:
            g.get("go" + k, "Opt" + k); g.call("ne" + k, K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.%s" % k.lower(), "B": "@go%s.Opt%s" % (k, k), "ErrorTolerance": "0.001"})
            g.call("a" + k, K_MATH, "BooleanAND", inp={"A": same, "B": "@ne%s.ReturnValue" % k}); same = "@a%s.ReturnValue" % k
        g.n("s0", "sequence", count=1); g.branch("bs", same); tl = []
        inp = {}
        for k, (lo, hi), step, unit in MINI_SLIDERS:
            g.n("rv" + k, "call_self", function="Range Value", inp={"v": "@gv.%s" % k.lower(), "lo": str(lo), "hi": str(hi), "step": str(step)})
            g.set("sv" + k, k, inp={k: "@rv%s.value" % k}); g.set("so" + k, "Opt" + k, inp={"Opt" + k: "@gv.%s" % k.lower()}); tl += ["sv" + k, "so" + k]
            g.get("gk" + k, k); inp[k.lower()] = "@gv.%s" % k.lower(); inp[k.lower() + " text"] = value_text(g, "vt" + k, "@gk%s.%s" % (k, k), unit)
        g.get("gp2", "Panel"); g.call("smv", W_PANEL, "Set Map Options", inp=dict(self="@gp2.Panel", mapon="@gv.mapon", legend="@gv.legend", minion="@gv.minion", **inp))
        g.n("svs", "call_self", function="Save Settings Soon")
        g.chain("s0:then_0", "bs"); g.chain("bs:else", *tl, "smv", "svs")
        return fn("Poll Map Options", graph=g)

    def f_select_corner():
        """Chip "MiniCorner<i>" -> MiniCorner, saved, the chips again."""
        g = G(); g.call("ns", K_STR, "Conv_NameToString", inp={"InName": "@entry.name"}); g.call("rc", K_STR, "RightChop", inp={"SourceString": "@ns.ReturnValue", "Count": "10"})
        g.call("ix", K_STR, "Conv_StringToInt", inp={"InString": "@rc.ReturnValue"}); g.call("cl", K_MATH, "Clamp", inp={"Value": "@ix.ReturnValue", "Min": "0", "Max": "3"})
        g.set("s", "MiniCorner", inp={"MiniCorner": "@cl.ReturnValue"}); g.n("sv", "call_self", function="Save Settings"); g.n("rb", "call_self", function="Rebuild Map Options")
        g.chain("entry", "s", "sv", "rb")
        return fn("Select Mini Corner", [param("name", "name")], graph=g)

    def f_select_shape():
        """Chip "MiniShape<i>" -> MiniRound (1 = round), saved, the chips again."""
        g = G(); g.call("eq", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.name", "B": "MiniShape1"})
        g.set("s", "MiniRound", inp={"MiniRound": "@eq.ReturnValue"}); g.n("sv", "call_self", function="Save Settings"); g.n("rb", "call_self", function="Rebuild Map Options")
        g.chain("entry", "s", "sv", "rb")
        return fn("Select Mini Shape", [param("name", "name")], graph=g)

    return [f_legend(), f_legend_toggle(), f_rebuild_options(), f_poll_options(), f_select_corner(), f_select_shape(), f_band_next(), f_band_of(), f_key(), f_tile_of(), f_to_screen(), f_to_world(), f_mark_spot(), f_feet(), f_jodi_band(),
            f_update_band(), f_level(), f_dir(), f_capture_tile(), f_capture_next(), f_tick(), f_tile_tex(), f_read_size(), f_redraw(), f_scan_beds(), f_kind_of(), f_kind_hidden(), f_scan_vends(), f_draw_mini(), f_mini_size(), f_mini_tick(),
            f_label(), f_links(), f_open(), f_full_open(), f_full_reset(), f_full_close(), f_full_toggle(), f_full_key(), f_center(), f_step("Map Up", 1), f_step("Map Down", -1), f_outside(), f_record(), f_style(), f_retake(),
            f_poll(), f_wheel(), f_press(), f_move(), f_release(), f_teleport()]
