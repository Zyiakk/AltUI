"""Generates assets/40_widgets.json: panel and element widgets (thin; the logic lives in the manager)."""
import os, re, sys; sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
from bpdsl import *
import bodyscale_groups as bg
from bodyscale_ui import factor_text
import gen_move

MGR = M + "/BP_AltUIManager"
S_ITEM = M + "/S_ClothesItem"
T_ITEM = "struct:" + S_ITEM
W_PANEL = M + "/W_AltUI"
W_HEAD = M + "/W_GroupHeader"
W_TAB = M + "/W_SlotTab"
W_BTN = M + "/W_ClothesButton"
W_SUB = M + "/W_SubTab"
W_ROUND = M + "/W_RoundButton"; T_PLUS = M + "/T_Plus"; T_MINUS = M + "/T_Minus"; T_CAM = M + "/T_Cam"; T_PHOTO = M + "/T_Photo"; T_COLORIZE = M + "/T_Colorize"
W_TOP = M + "/W_TopTab"
W_OUTFIT = M + "/W_OutfitButton"; W_LOOK = M + "/W_LookButton"; W_FACEBTN = M + "/W_FaceButton"; W_KODEXTILE = M + "/W_KodexTile"; W_RAGTILE = M + "/W_RagTile"; W_LINKROW = M + "/W_LinkRow"; W_RAGPOSES = M + "/W_RagPoses"; W_TOOLTIP = M + "/W_Tooltip"; W_SECTION = M + "/W_ContentSection"; W_VALROW = M + "/W_ValueRow"
U_OVERLAY = "/Script/UMG.Overlay"; K_SLATE = "/Script/UMG.SlateBlueprintLibrary"
U_VBOX = "/Script/UMG.VerticalBox"; U_HBOX = "/Script/UMG.HorizontalBox"; U_SCROLL = "/Script/UMG.ScrollBox"
U_PROGRESS = "/Script/UMG.ProgressBar"; U_WRAP = "/Script/UMG.WrapBox"; U_SCALE = "/Script/UMG.ScaleBox"; U_SIZE = "/Script/UMG.SizeBox"; U_CANVAS = "/Script/UMG.CanvasPanel"; U_PANELW = "/Script/UMG.PanelWidget"

SC = 1.9   # global size factor (2560x1440)
def sz(v): return int(round(v * SC))
LIST_ROOM = sz(60)   # room below the last row of a virtual list: it can be scrolled up into the view
OUTFIT_GAP = sz(6) + 1   # space between outfit tiles (wrap box padding; the manager's row height adds it)
FULL = {"LayoutData": "(Anchors=(Minimum=(X=0,Y=0),Maximum=(X=1,Y=1)),Offsets=(Left=0,Top=0,Right=0,Bottom=0))"}
FILL = {"Size": "(SizeRule=Fill,Value=1)"}
COL_BG = "(R=0.02,G=0.02,B=0.03,A=0.88)"
# COL_* below are the widget-tree initial values only: at runtime every colour comes from the manager theme (Manager.Col*, theme.py)
# via Compute Colors / W_AltUI.Apply Theme; the defaults of theme.py mirror these values.
# tiles / chips: round box texture (white, tinted via BrushColor), 9-slice with 16px corners
T_ROUNDBOX = M + "/T_RoundBox"
T_CHECK_ON = M + "/T_CheckOn"; T_CHECK_OFF = M + "/T_CheckOff"
W_TXT = M + "/W_TextButton"
W_NAMEROW = M + "/W_NameRow"; W_HSWATCH = M + "/W_HairSwatch"; W_CONFLICT = M + "/W_ConflictRow"; W_KODEXLOCK = M + "/W_KodexLockRow"
SEARCH_FONT = 16; SEARCH_PAD = 7
CHECK_SIZE = int(round(sz(SEARCH_FONT) * 1.2 + 2 * sz(SEARCH_PAD) + 2 * sz(1)))   # = height of the search bar
COL_LINK = "(SpecifiedColor=(R=0.62,G=0.76,B=1.0,A=1))"
ROUNDBOX = "(ResourceObject=Texture2D'%s.T_RoundBox',ImageSize=(X=48,Y=48),DrawAs=Box,Margin=(Left=0.33,Top=0.33,Right=0.33,Bottom=0.33))" % T_ROUNDBOX
T_ROUNDFRAME = M + "/T_RoundFrame"
ROUNDFRAME = "(ResourceObject=Texture2D'%s.T_RoundFrame',ImageSize=(X=48,Y=48),DrawAs=Box,Margin=(Left=0.33,Top=0.33,Right=0.33,Bottom=0.33))" % T_ROUNDFRAME
COL_NONE = "(R=0,G=0,B=0,A=0)"
COL_ACCENT = "(R=0.75,G=0.10,B=0.10,A=1)"          # vanilla red (selection)
COL_FILL = "(R=0.02,G=0.02,B=0.03,A=0.80)"         # tile fill like vanilla
COL_FILL_HOVER = "(R=0.12,G=0.12,B=0.14,A=0.85)"
COL_FILL_WORN = "(R=0.04,G=0.14,B=0.06,A=0.85)"
COL_FILL_WORN_HOVER = "(R=0.10,G=0.24,B=0.12,A=0.90)"
COL_FRAME = "(R=1,G=1,B=1,A=0.35)"                 # thin light border
COL_FRAME_HOVER = "(R=1,G=1,B=1,A=0.90)"
COL_FRAME_WORN = "(R=0.20,G=0.80,B=0.30,A=0.90)"
COL_FRAME_LOCKED = "(R=1,G=1,B=1,A=0.12)"
COL_ROW = "(R=0,G=0,B=0,A=0.35)"                   # slot row
COL_ROW_HOVER = "(R=1,G=1,B=1,A=0.08)"
COL_ROW_SEL = "(R=1,G=1,B=1,A=0.10)"
COL_ROW_SEL_HOVER = "(R=1,G=1,B=1,A=0.16)"
COL_LINE = "(R=1,G=1,B=1,A=0.12)"                  # separator line
COL_CHIP = "(R=0,G=0,B=0,A=0.55)"                  # sub tab
COL_CHIP_HOVER = "(R=1,G=1,B=1,A=0.08)"
COL_CHIP_SEL = "(R=1,G=1,B=1,A=0.12)"
COL_CHIP_SEL_HOVER = "(R=1,G=1,B=1,A=0.18)"
COL_CHIP_FRAME = "(R=1,G=1,B=1,A=0.25)"
COL_CHIP_FRAME_HOVER = "(R=1,G=1,B=1,A=0.70)"
COL_MENU_HOVER = "(R=1,G=1,B=1,A=0.15)"
WHITE = "(SpecifiedColor=(R=1,G=1,B=1,A=1))"
GREY = "(SpecifiedColor=(R=0.6,G=0.6,B=0.6,A=1))"
HAND = {"bOverride_Cursor": "true", "Cursor": "Hand"}   # click cursor (CDO defaults of the element widgets)


def text(name, txt="", size=12, color=WHITE, wrap=False, slot=None, center=False, break_all=False, props_extra=None):
    p = {"Text": txt, "Font": "(Size=%d)" % sz(size), "ColorAndOpacity": color}
    if props_extra: p.update(props_extra)
    if wrap: p["AutoWrapText"] = True
    if break_all: p["WrappingPolicy"] = "AllowPerCharacterWrapping"   # like CSS word-break: break-all
    if center: p["Justification"] = "Center"
    return w(E_TEXT, name, props=p, slot=slot)


def fit_image(name, wd, ht, slot=None, hidden=False):
    """SizeBox -> ScaleBox(ScaleToFit) -> Image: the icon keeps its aspect ratio (SetBrushFromTexture with bMatchSize=true)."""
    p = {"Visibility": "Hidden"} if hidden else None
    return sizebox(name + "Box", wd, ht, [w(U_SCALE, name + "Scale", props={"Stretch": "ScaleToFit"}, children=[w(E_IMAGE, name, props=p)])], slot=slot)


def check_style(size):
    def br(tex, tint="(R=1,G=1,B=1,A=1)"):
        return "(ResourceObject=Texture2D'%s.%s',ImageSize=(X=%d,Y=%d),DrawAs=Image,TintColor=(SpecifiedColor=%s))" % (tex, tex.rsplit("/", 1)[-1], size, size, tint)
    hov = "(R=1.25,G=1.25,B=1.25,A=1)"
    return "(UncheckedImage=%s,UncheckedHoveredImage=%s,UncheckedPressedImage=%s,CheckedImage=%s,CheckedHoveredImage=%s,CheckedPressedImage=%s,Padding=(Left=0,Top=0,Right=0,Bottom=0))" % (
        br(T_CHECK_OFF), br(T_CHECK_OFF, hov), br(T_CHECK_OFF, hov), br(T_CHECK_ON), br(T_CHECK_ON, hov), br(T_CHECK_ON, hov))


def tile_scale(g, tail, boxes, scale_pin=None):
    """Multiply SizeBox sizes by Manager.TileScale, or by scale_pin (outfit / look tiles have sizes of their own) (init chain);
    ht None = width only (the height follows the content)."""
    if scale_pin is None:
        g.get("tsm", "Manager"); g.get("tsv", "TileScale", cls=MGR); g.link("tsm.Manager", "tsv.self"); scale_pin = "@tsv.TileScale"
    for name, wd, ht in boxes:
        g.call("tw_" + name, K_MATH, "Multiply_FloatFloat", inp={"A": str(float(sz(wd))), "B": scale_pin})
        g.get("tg_" + name, name); g.call("tsw_" + name, U_SIZE, "SetWidthOverride", inp={"self": "@tg_%s.%s" % (name, name), "InWidthOverride": "@tw_%s.ReturnValue" % name})
        tail.append("tsw_" + name)
        if ht is None: continue
        g.call("th_" + name, K_MATH, "Multiply_FloatFloat", inp={"A": str(float(sz(ht))), "B": scale_pin})
        g.get("tg2_" + name, name); g.call("tsh_" + name, U_SIZE, "SetHeightOverride", inp={"self": "@tg2_%s.%s" % (name, name), "InHeightOverride": "@th_%s.ReturnValue" % name})
        tail.append("tsh_" + name)


INV_AREA_TINT = "(R=1,G=1,B=1,A=0.05)"   # = the tinted rows of the slot conflicts
AREA_FRAME = "(R=1,G=1,B=1,A=0.16)"      # a slightly brighter white rim around those surfaces


def framed(name, content, pad):
    """Overlay: content (inner padding `pad` = (l, t, r, b) before sz) and on top the round outline (no hits) - the child of a
    see-through round surface whose own padding is 0, so the rim sits on its edge."""
    return w(U_OVERLAY, name, children=[
        dict(content, slot=dict(content.get("slot") or {}, HorizontalAlignment="HAlign_Fill", VerticalAlignment="VAlign_Fill",
                                Padding="(Left=%d,Top=%d,Right=%d,Bottom=%d)" % tuple(sz(v) for v in pad))),
        w(E_IMAGE, name + "Rim", props={"Brush": ROUNDFRAME, "ColorAndOpacity": AREA_FRAME, "Visibility": "HitTestInvisible"},
          slot={"HorizontalAlignment": "HAlign_Fill", "VerticalAlignment": "VAlign_Fill"})])


def inv_area(area, scroll, lst, hidden=False):
    """Inventory list on a rounded light surface: inner padding left / bottom (the section headings bring their own top gap),
    little on the right so the scroll bar stays at the edge. hidden: collapsed until switched on (the catalogue)."""
    return roundbox(area, INV_AREA_TINT, 0, slot=FILL, props=dict({"Padding": "(Left=0,Top=0,Right=0,Bottom=0)"}, **({"Visibility": "Collapsed"} if hidden else {})),
                    children=[framed(area + "Ov", w(U_SCROLL, scroll, props={"WheelScrollMultiplier": 2.0}, children=[w(U_VBOX, lst, slot={"Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)})]),
                                     (10, 0, 3, 10))])


def inv_head_btns(name):
    """Inventory list head: box for the fold ("...") and full-height chips the manager puts in (Inv Head Chips)."""
    return w(U_HBOX, name, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(10)})


def roundbox(name, color, pad, children, props=None, slot=None):
    """Border with the round box texture (frame or fill)."""
    p = {"Background": ROUNDBOX, "BrushColor": color, "Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % ((sz(pad),) * 4)}
    if props: p.update(props)
    return w(E_BORDER, name, props=p, slot=slot, children=children)


IMAGE_TINT = 0.4   # button image: tinted this far towards the state colour (hover, selection show through)


def hover_parts(cls, frame, fill, image=False):
    """Hover mechanics: variables Base*/Hover*, function `Apply Colors(hover)` and event graph OnMouseEnter/Leave.
    frame/fill = name of the border widget (frame optional). image: with a button image (Options > Theme, Manager.ButtonOn) the fill
    draws Manager.ButtonBrush (M_ImageBox: the picture cut to the round box) tinted towards the state colour, at the tile opacity.
    Returns (variables, functions, event_graph)."""
    names = [n for n in (("Frame", frame), ("Fill", fill)) if n[1]]
    vars_ = [var(pre + part, S_LINCOLOR) for part, _ in names for pre in ("Base", "Hover")]
    g = G(); chain = ["entry"]
    for part, wn in names:
        g.get("gb" + part, "Base" + part); g.get("gh" + part, "Hover" + part)
        g.call("c" + part, K_MATH, "SelectColor", inp={"A": "@gh%s.Hover%s" % (part, part), "B": "@gb%s.Base%s" % (part, part), "bPickA": "@entry.hover"})
        g.get("gw" + part, wn); g.call("s" + part, E_BORDER, "SetBrushColor", inp={"self": "@gw%s.%s" % (part, wn), "InBrushColor": "@c%s.ReturnValue" % part})
        chain.append("s" + part)
    if image and fill:
        g.get("img_m", "Manager"); g.call("img_v", K_SYS, "IsValid", inp={"Object": "@img_m.Manager"})
        g.get("img_on", "ButtonOn", cls=MGR); g.link("img_m.Manager", "img_on.self"); g.call("img_a", K_MATH, "BooleanAND", inp={"A": "@img_v.ReturnValue", "B": "@img_on.ButtonOn"})
        g.branch("img_b", "@img_a.ReturnValue"); g.get("img_br", "ButtonBrush", cls=MGR); g.link("img_m.Manager", "img_br.self")
        g.get("img_w", fill); g.call("img_sb", E_BORDER, "SetBrush", inp={"self": "@img_w." + fill, "InBrush": "@img_br.ButtonBrush"})
        g.call("img_l", K_MATH, "LinearColorLerp", inp={"A": "(R=1,G=1,B=1,A=1)", "B": "@cFill.ReturnValue", "Alpha": str(IMAGE_TINT)}); g.call("img_k", K_MATH, "BreakColor", inp={"InColor": "@img_l.ReturnValue"})
        g.get("img_ta", "TileAlpha", cls=MGR); g.link("img_m.Manager", "img_ta.self")
        g.call("img_c", K_MATH, "MakeColor", inp={"R": "@img_k.R", "G": "@img_k.G", "B": "@img_k.B", "A": "@img_ta.TileAlpha"})
        g.get("img_w2", fill); g.call("img_sc", E_BORDER, "SetBrushColor", inp={"self": "@img_w2." + fill, "InBrushColor": "@img_c.ReturnValue"})
        chain += ["img_b", "img_sb", "img_sc"]
    g.chain(*chain)
    eg = G()
    eg.event("en", E_USERWIDGET, "OnMouseEnter"); eg.n("ae", "call_self", function="Apply Colors", inp={"hover": "true"}); eg.chain("en", "ae")
    eg.event("lv", E_USERWIDGET, "OnMouseLeave"); eg.n("al", "call_self", function="Apply Colors", inp={"hover": "false"}); eg.chain("lv", "al")
    return vars_, [fn("Apply Colors", [param("hover", "bool")], graph=g)], eg


def set_colors(g, part, base, hover, tail):
    """Init helper: set Base<part>/Hover<part> (values = colour literals or pin refs); appends the node ids to tail."""
    g.set("sb" + part, "Base" + part, inp={"Base" + part: base}); g.set("sh" + part, "Hover" + part, inp={"Hover" + part: hover})
    tail += ["sb" + part, "sh" + part]


def sizebox(name, wd, ht, children, slot=None):
    """ht None: width only - the height follows the content."""
    p = {"bOverride_WidthOverride": True, "WidthOverride": sz(wd)}
    if ht is not None: p.update({"bOverride_HeightOverride": True, "HeightOverride": sz(ht)})
    return w(U_SIZE, name, props=p, slot=slot, children=children)


# Tiles are a little wider than their centred content (icon / photo): TILE_SIDE is that slack per side, so the fill's padding
# above and below adds it too - the content sits at the same distance from all four edges. The height follows the content;
# a wrap box row stretches its tiles to the tallest one (tile lists add with VAlign_Fill).
TILE_PAD = 4; TILE_SIDE = 3
TILE_LISTS = {"OutfitList", "LooksList", "BagWorn", "BagList", "HairList", "HairFavList", "LookList", "LookFavList", "FaceTiles", "PoseList", "PoseFavList",
              "WeaponModelList", "WeaponList", "WeaponFavList"}
TILE_FILL_PAD = "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(TILE_PAD), sz(TILE_PAD + TILE_SIDE), sz(TILE_PAD), sz(TILE_PAD + TILE_SIDE))


def mt(g, id, key):
    """Manager.T(key) (pure) -> text pin; widgets know the manager through the variable Manager."""
    g.get(id + "_m", "Manager"); g.call(id, MGR, "T", inp={"self": "@%s_m.Manager" % id, "key": key}); return "@%s.text" % id


def mts(g, id, key):
    """Manager.T(key) as a string pin."""
    g.call(id + "_2s", K_TXT, "Conv_TextToString", inp={"InText": mt(g, id, key)}); return "@%s_2s.ReturnValue" % id


def mouse_down_override(left_fn, right_fn, arg_var, pin="name", split=False):
    """OnMouseButtonDown: right mouse button -> right_fn, else left_fn (manager function with one argument `pin`). Remembers the widget as Manager.LastButton.
    split: a "+" tile split in two photo modes (SplitTile) - a left click in the lower half of the Split box sets Manager.PhotoView
    (photo along the current camera instead of from the front), everything else clears it."""
    g = G()
    g.call("btn", K_IN, "PointerEvent_GetEffectingButton", inp={"Input": "@entry.MouseEvent"})
    g.call("isr", K_IN, "EqualEqual_KeyKey", inp={"A": "@btn.ReturnValue", "B": "RightMouseButton"})
    g.branch("b", "@isr.ReturnValue")
    g.get("gm0", "Manager"); g.self_("me0"); g.n("slb", "set", var="LastButton", cls=MGR, inp={"self": "@gm0.Manager", "LastButton": "@me0.self"})
    g.get("gm", "Manager"); g.get("ga", arg_var)
    g.call("r", MGR, right_fn, inp={"self": "@gm.Manager", pin: "@ga." + arg_var})
    g.get("gm2", "Manager"); g.get("ga2", arg_var)
    g.call("l", MGR, left_fn, inp={"self": "@gm2.Manager", pin: "@ga2." + arg_var})
    g.call("h", K_WBL, "Handled"); g.link("h.ReturnValue", "return.ReturnValue")
    if split:
        g.call("ssp", K_IN, "PointerEvent_GetScreenSpacePosition", inp={"Input": "@entry.MouseEvent"})
        g.get("gst", "SplitTile"); g.call("pv", K_MATH, "BooleanAND", inp={"A": "@gst.SplitTile", "B": split_lower(g, "sl", "@ssp.ReturnValue")})
        g.get("gm3", "Manager"); g.n("spv", "set", var="PhotoView", cls=MGR, inp={"self": "@gm3.Manager", "PhotoView": "@pv.ReturnValue"})
        g.chain("entry", "slb", "b", "r", "return"); g.chain("b:else", "spv", "l", "return")
    else:
        g.chain("entry", "slb", "b", "r", "return"); g.chain("b:else", "l", "return")
    return fn("OnMouseButtonDown", override=True, graph=g)


def photo_split():
    """The "+" tile of a photo: upper half "from the front", lower half "as seen" (the click side is decided in OnMouseButtonDown).
    It lies over the tile's whole content (overlay TileOv): the content stays in the layout but hidden, so the halves fill the tile
    also when its row is taller."""
    def half(name, label):   # a background of its own: Tick lights up the half under the mouse (split_tick)
        return w(E_BORDER, name, props={"Background": ROUNDBOX, "BrushColor": "(R=0,G=0,B=0,A=0)", "HorizontalAlignment": "HAlign_Center", "VerticalAlignment": "VAlign_Center",
                                        "Padding": "(Left=%d,Top=0,Right=%d,Bottom=0)" % (sz(TILE_PAD + TILE_SIDE), sz(TILE_PAD + TILE_SIDE))},   # text as far from the sides as the tile's content
                 slot={"Size": "(SizeRule=Fill,Value=1)", "HorizontalAlignment": "HAlign_Fill", "VerticalAlignment": "VAlign_Fill"},
                 children=[text(label, "+", 10, WHITE, wrap=True, center=True)])
    # the fill pads the sides by TILE_PAD only (the content's own slack makes the rest): TILE_SIDE more, so the halves sit
    # as far from all four edges as the other tiles' content
    return w(U_VBOX, "Split", props={"Visibility": "Collapsed"}, slot={"HorizontalAlignment": "HAlign_Fill", "VerticalAlignment": "VAlign_Fill",
                                                                     "Padding": "(Left=%d,Top=0,Right=%d,Bottom=0)" % (sz(TILE_SIDE), sz(TILE_SIDE))}, children=[
        half("SplitFrontBg", "SplitFront"),
        w(U_SIZE, "SplitLineBox", props={"bOverride_HeightOverride": True, "HeightOverride": max(1, sz(1))}, slot={"HorizontalAlignment": "HAlign_Fill"},
          children=[w(E_BORDER, "SplitLine", props={"BrushColor": COL_FRAME})]),
        half("SplitViewBg", "SplitView")])


def with_split(tree):
    """Put photo_split() over the tile's content: Fill -> TileOv [VB, Split]."""
    def walk(n):
        if n.get("name") == "Fill":
            n["children"] = [w(U_OVERLAY, "TileOv", children=[dict(n["children"][0], slot={"HorizontalAlignment": "HAlign_Fill", "VerticalAlignment": "VAlign_Fill"}), photo_split()])]
            return True
        return any(walk(c) for c in n.get("children", []))
    assert walk(tree); return tree


def split_lower(g, id, abs_pin):
    """Pure: is the absolute point `abs_pin` in the lower half of the Split box? -> bool pin."""
    g.get(id + "g", "Split"); g.call(id + "geo", E_WIDGET, "GetCachedGeometry", inp={"self": "@%sg.Split" % id})
    g.call(id + "loc", K_SLATE, "AbsoluteToLocal", inp={"Geometry": "@%sgeo.ReturnValue" % id, "AbsoluteCoordinate": abs_pin})
    g.call(id + "siz", K_SLATE, "GetLocalSize", inp={"Geometry": "@%sgeo.ReturnValue" % id})
    g.call(id + "bl", K_MATH, "BreakVector2D", inp={"InVec": "@%sloc.ReturnValue" % id}); g.call(id + "bs", K_MATH, "BreakVector2D", inp={"InVec": "@%ssiz.ReturnValue" % id})
    g.call(id + "h", K_MATH, "Multiply_FloatFloat", inp={"A": "@%sbs.Y" % id, "B": "0.5"})
    g.call(id + "lo", K_MATH, "GreaterEqual_FloatFloat", inp={"A": "@%sbl.Y" % id, "B": "@%sh.ReturnValue" % id}); return "@%slo.ReturnValue" % id


def split_tick(tk, start, cont):
    """Tick part of a split "+" tile: the half under the mouse gets the hover fill, the tile's own fill stays at its base colour
    (otherwise both halves would light up together). Runs from `start`, continues with `cont`; does nothing unless SplitTile."""
    tk.get("gst", "SplitTile"); tk.branch("bst", "@gst.SplitTile")
    tk.call("hov", E_WIDGET, "IsHovered"); tk.call("mp", "/Script/UMG.WidgetLayoutLibrary", "GetMousePositionOnPlatform")
    low = split_lower(tk, "sl", "@mp.ReturnValue"); tk.call("nlo", K_MATH, "Not_PreBool", inp={"A": low})
    tk.call("fon", K_MATH, "BooleanAND", inp={"A": "@hov.ReturnValue", "B": "@nlo.ReturnValue"}); tk.call("von", K_MATH, "BooleanAND", inp={"A": "@hov.ReturnValue", "B": low})
    hc = mcol(tk, "chv", "ColFillHover")
    tk.call("cf", K_MATH, "SelectColor", inp={"A": hc, "B": "(R=0,G=0,B=0,A=0)", "bPickA": "@fon.ReturnValue"})
    tk.call("cv", K_MATH, "SelectColor", inp={"A": hc, "B": "(R=0,G=0,B=0,A=0)", "bPickA": "@von.ReturnValue"})
    tk.get("gfb", "SplitFrontBg"); tk.call("sf", E_BORDER, "SetBrushColor", inp={"self": "@gfb.SplitFrontBg", "InBrushColor": "@cf.ReturnValue"})
    tk.get("gvb", "SplitViewBg"); tk.call("sv", E_BORDER, "SetBrushColor", inp={"self": "@gvb.SplitViewBg", "InBrushColor": "@cv.ReturnValue"})
    tk.get("gbf", "BaseFill"); tk.get("gfl", "Fill"); tk.call("sfl", E_BORDER, "SetBrushColor", inp={"self": "@gfl.Fill", "InBrushColor": "@gbf.BaseFill"})
    tk.chain(start, "bst", "mp", "sf", "sv", "sfl", cont); tk.chain("bst:else", cont)   # mp: impure, needs the exec


def split_init(g, id, on_pin, front_key=None, view_key=None):
    """Init part: SplitTile = on_pin; the split visible, each half with its full caption (string keys front_key / view_key), the plain
    plus and the bottom Label collapsed - or the other way round.
    Returns (first exec id, [the two exec ids to continue from]). While split, the content VB is hidden (keeps its size)."""
    g.set(id + "st", "SplitTile", inp={"SplitTile": on_pin}); g.branch(id + "b", on_pin)
    g.get(id + "g1", "Split"); g.call(id + "v1", E_WIDGET, "SetVisibility", inp={"self": "@%sg1.Split" % id, "InVisibility": "Visible"})
    g.get(id + "g2", "Plus"); g.call(id + "c2", E_WIDGET, "SetVisibility", inp={"self": "@%sg2.Plus" % id, "InVisibility": "Collapsed"})
    g.get(id + "g3", "SplitFront"); g.call(id + "t3", E_TEXT, "SetText", inp={"self": "@%sg3.SplitFront" % id, "InText": mt(g, id + "m3", front_key) if front_key else ""})
    g.get(id + "g4", "SplitView"); g.call(id + "t4", E_TEXT, "SetText", inp={"self": "@%sg4.SplitView" % id, "InText": mt(g, id + "m4", view_key) if view_key else ""})
    g.get(id + "g8", "VB"); g.call(id + "c8", E_WIDGET, "SetVisibility", inp={"self": "@%sg8.VB" % id, "InVisibility": "Hidden"})
    g.get(id + "g5", "Split"); g.call(id + "c5", E_WIDGET, "SetVisibility", inp={"self": "@%sg5.Split" % id, "InVisibility": "Collapsed"})
    g.get(id + "ga", "VB"); g.call(id + "va", E_WIDGET, "SetVisibility", inp={"self": "@%sga.VB" % id, "InVisibility": "Visible"})
    g.chain(id + "st", id + "b", id + "v1", id + "c2", id + "t3", id + "t4", id + "c8"); g.chain(id + "b:else", id + "c5", id + "va")
    return id + "st", [id + "c8", id + "va"]


# ---------------- Theme helpers ----------------
def mcol(g, id, name):
    """Manager.<name> (derived theme colour ColX, or any manager variable) -> pin."""
    g.get(id + "_m", "Manager"); g.get(id, name, cls=MGR); g.link(id + "_m.Manager", id + ".self"); return "@%s.%s" % (id, name)


def text_color(g, id, widget, color_pin, tail):
    """TextBlock.SetColorAndOpacity(SlateColor(colour))."""
    g.make(id + "_sc", "/Script/SlateCore.SlateColor", SpecifiedColor=color_pin)
    g.get(id + "_w", widget); g.call(id, E_TEXT, "SetColorAndOpacity", inp={"self": "@%s_w.%s" % (id, widget), "InColorAndOpacity": "@%s_sc.SlateColor" % id}); tail.append(id)


def brush(g, id, widget, color_pin, tail):
    g.get(id + "_w", widget); g.call(id, E_BORDER, "SetBrushColor", inp={"self": "@%s_w.%s" % (id, widget), "InBrushColor": color_pin}); tail.append(id)


def refresh_fn():
    """Refresh Theme: recompute the colours from Manager.Col* and apply them for the current hover state.
    Called by W_AltUI.Apply Theme for the elements that stay visible while the theme is edited (Options page); every other page is
    rebuilt when it is selected. Replaces the former per-widget Tick that compared ThemeSeen with Manager.ThemeVersion every frame."""
    g = G(); g.n("cc", "call_self", function="Compute Colors"); g.call("hov", E_WIDGET, "IsHovered")
    g.n("ap", "call_self", function="Apply Colors", inp={"hover": "@hov.ReturnValue"}); g.chain("entry", "cc", "ap")
    return fn("Refresh Theme", graph=g)


def compute_fn(g):
    return fn("Compute Colors", graph=g)


def reset_rename(g, tail, label):
    """Init of a renameable tile: a rename still open on it ends without a word (tiles of the virtual lists are reused for other
    entries); the keyboard focus stays where it is."""
    g.set("rr_se", "Editing", inp={"Editing": "false"}); g.get("rr_ge", "NameEdit"); g.call("rr_hv", E_WIDGET, "SetVisibility", inp={"self": "@rr_ge.NameEdit", "InVisibility": "Collapsed"})
    g.get("rr_gl", label); g.call("rr_sl", E_WIDGET, "SetVisibility", inp={"self": "@rr_gl.%s" % label, "InVisibility": "Visible"}); tail += ["rr_se", "rr_hv", "rr_sl"]


def rename_tick(split=False, pre=None):
    """Tick of the renameable tiles: Editing and the text field lost the keyboard focus -> End Rename. split: then the split_tick part.
    pre: a function of the tile called first."""
    tk = G(); start = "entry"
    if pre: tk.n("pre", "call_self", function=pre); tk.chain("entry", "pre"); start = "pre"
    tk.get("ged", "Editing"); tk.get("ge", "NameEdit"); tk.call("hf", E_WIDGET, "HasKeyboardFocus", inp={"self": "@ge.NameEdit"})
    tk.call("nf", K_MATH, "Not_PreBool", inp={"A": "@hf.ReturnValue"}); tk.call("and", K_MATH, "BooleanAND", inp={"A": "@ged.Editing", "B": "@nf.ReturnValue"}); tk.branch("b", "@and.ReturnValue")
    tk.n("er", "call_self", function="End Rename")
    if split: split_tick(tk, start, "b"); tk.chain("b", "er")
    else: tk.chain(start, "b", "er")
    return tk


# ---------------- W_Tooltip (dark round box + text; the engine default tooltip is unreadably small at the panel scale) ----------------
def w_tooltip():
    tree = roundbox("Frame", COL_FRAME, 1, [roundbox("Fill", "(R=0.05,G=0.05,B=0.06,A=0.96)", 6, [text("Tip", "", 12, WHITE)])])
    g = G(); g.get("gt", "Tip"); g.call("st", E_TEXT, "SetText", inp={"self": "@gt.Tip", "InText": "@entry.text"}); g.n("cc", "call_self", function="Compute Colors"); g.chain("entry", "st", "cc")
    c = G(); tail = ["entry"]
    brush(c, "sf", "Frame", mcol(c, "cf", "ColFrame"), tail); brush(c, "sb", "Fill", mcol(c, "cb", "ColMenuBg"), tail); text_color(c, "tc", "Tip", mcol(c, "ct", "ColText"), tail); c.chain(*tail)
    return blueprint(W_TOOLTIP, E_USERWIDGET, variables=[var("Manager", "object:" + MGR)],
                     functions=[fn("Init", [param("text", "text")], graph=g), compute_fn(c)], widget_tree=tree)


# ---------------- W_GroupHeader ----------------
def w_group_header():
    tree = w(E_BORDER, "Bg", props={"BrushColor": "(R=0.0,G=0.0,B=0.0,A=0.0)", "Padding": "(Left=15,Top=19,Right=15,Bottom=8)"},
             children=[text("Label", "Gruppe", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))")])
    g = G(); g.get("gl", "Label"); g.call("st", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@entry.caption"}); g.n("cc", "call_self", function="Compute Colors"); g.chain("entry", "st", "cc")
    c = G(); tail = ["entry"]; text_color(c, "tc", "Label", mcol(c, "ch", "ColHead"), tail); c.chain(*tail)
    return blueprint(W_HEAD, E_USERWIDGET, variables=[var("Manager", "object:" + MGR)],
                     functions=[fn("Init", [param("caption", "text")], graph=g), compute_fn(c)], widget_tree=tree)


# ---------------- W_ContentSection (content view: heading + tiles + optional note line) ----------------
def w_content_section():
    tree = w(U_VBOX, "VB", children=[
        text("Header", "Section", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(12), sz(6))}),
        text("SmallHeader", "", 12, WHITE, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(5))}, props_extra={"Visibility": "Collapsed"}),
        w(U_WRAP, "Tiles", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)}),
        w(U_VBOX, "Table", props={"Visibility": "Collapsed"}, slot={"HorizontalAlignment": "HAlign_Left", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(6)}),
        w(E_TEXT, "Note", props={"Text": "", "Font": "(Size=%d)" % sz(12), "ColorAndOpacity": GREY, "Visibility": "Collapsed"}, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(6)})])
    g = G(); g.get("gh", "Header"); g.call("st", E_TEXT, "SetText", inp={"self": "@gh.Header", "InText": "@entry.caption"}); g.n("cc", "call_self", function="Compute Colors"); g.chain("entry", "st", "cc")
    a = G(); a.get("gt", "Tiles"); a.call("ad", U_WRAP, "AddChildToWrapBox", inp={"self": "@gt.Tiles", "Content": "@entry.widget"})
    a.call("va", "/Script/UMG.WrapBoxSlot", "SetVerticalAlignment", inp={"self": "@ad.ReturnValue", "InVerticalAlignment": "VAlign_Fill"}); a.chain("entry", "ad", "va")
    n = G(); n.get("gn", "Note"); n.call("sn", E_TEXT, "SetText", inp={"self": "@gn.Note", "InText": "@entry.text"})
    n.get("gn2", "Note"); n.call("vn", E_WIDGET, "SetVisibility", inp={"self": "@gn2.Note", "InVisibility": "Visible"}); n.chain("entry", "sn", "vn")
    # table of text values (W_ValueRow): value rows striped alternately, a header row starts the count again
    r = G(); r.get("gt", "Table"); r.call("ad", U_VBOX, "AddChildToVerticalBox", inp={"self": "@gt.Table", "Content": "@entry.row"})
    r.get("gt2", "Table"); r.call("vt", E_WIDGET, "SetVisibility", inp={"self": "@gt2.Table", "InVisibility": "Visible"})
    r.get("gh", "Header", cls=W_VALROW); r.link("entry.row", "gh.self"); r.branch("bh", "@gh.Header")
    r.set("rc0", "RowCount", inp={"RowCount": "0"})
    r.get("grc", "RowCount"); r.call("odd", K_MATH, "Percent_IntInt", inp={"A": "@grc.RowCount", "B": "2"}); r.call("is1", K_MATH, "EqualEqual_IntInt", inp={"A": "@odd.ReturnValue", "B": "1"})
    r.call("ss", W_VALROW, "Set Stripe", inp={"self": "@entry.row", "on": "@is1.ReturnValue"})
    r.get("grc2", "RowCount"); r.call("inc", K_MATH, "Add_IntInt", inp={"A": "@grc2.RowCount", "B": "1"}); r.set("rc1", "RowCount", inp={"RowCount": "@inc.ReturnValue"})
    r.chain("entry", "ad", "vt", "bh", "rc0"); r.chain("bh:else", "ss", "rc1")
    c = G(); tail = ["entry"]; text_color(c, "th", "Header", mcol(c, "ch", "ColHead"), tail); text_color(c, "tn", "Note", mcol(c, "cn", "ColTextDim"), tail)
    text_color(c, "tsh", "SmallHeader", mcol(c, "csh", "ColText"), tail); c.chain(*tail)
    # Set Head Mode: 0 = heading as made, 1 = small heading, 2 = none (tiles / note take the top gap instead)
    hm = G(); hm.call("is1", K_MATH, "EqualEqual_IntInt", inp={"A": "@entry.mode", "B": "1"}); hm.branch("b1", "@is1.ReturnValue")
    hm.get("gh", "Header"); hm.call("gt", E_TEXT, "GetText", inp={"self": "@gh.Header"}); hm.get("gs", "SmallHeader"); hm.call("st", E_TEXT, "SetText", inp={"self": "@gs.SmallHeader", "InText": "@gt.ReturnValue"})
    hm.get("gs2", "SmallHeader"); hm.call("vs", E_WIDGET, "SetVisibility", inp={"self": "@gs2.SmallHeader", "InVisibility": "HitTestInvisible"})
    hm.get("gh2", "Header"); hm.call("hh", E_WIDGET, "SetVisibility", inp={"self": "@gh2.Header", "InVisibility": "Collapsed"})
    hm.call("is2", K_MATH, "EqualEqual_IntInt", inp={"A": "@entry.mode", "B": "2"}); hm.branch("b2", "@is2.ReturnValue")
    hm.get("gh3", "Header"); hm.call("hh2", E_WIDGET, "SetVisibility", inp={"self": "@gh3.Header", "InVisibility": "Collapsed"})
    for wn in ("Tiles", "Note"):
        hm.get("g" + wn, wn); hm.call("s" + wn, "/Script/UMG.WidgetLayoutLibrary", "SlotAsVerticalBoxSlot", inp={"Widget": "@g%s.%s" % (wn, wn)})
        hm.call("p" + wn, "/Script/UMG.VerticalBoxSlot", "SetPadding", inp={"self": "@s%s.ReturnValue" % wn, "InPadding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(10)})
    hm.chain("entry", "b1", "st", "vs", "hh"); hm.chain("b1:else", "b2", "hh2", "pTiles", "pNote")
    return blueprint(W_SECTION, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("RowCount", "int")],
                     functions=[fn("Init", [param("caption", "text")], graph=g), fn("Add Tile", [param("widget", "object:" + E_WIDGET)], graph=a),
                                fn("Add Row", [param("row", "object:" + W_VALROW)], graph=r),
                                fn("Set Note", [param("text", "text")], graph=n), fn("Set Head Mode", [param("mode", "int")], graph=hm), compute_fn(c)], widget_tree=tree)


# ---------------- W_ValueRow (one line of a content section's table: label | value, or a header line) ----------------
def w_value_row():
    tree = w(E_BORDER, "Fill", props={"BrushColor": COL_NONE, "Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(6), sz(2), sz(6), sz(2))}, children=[
        w(U_HBOX, "HB", children=[
            w(U_SIZE, "LabelBox", props={"bOverride_WidthOverride": True, "WidthOverride": sz(190)}, children=[text("Label", "", 12, WHITE)]),
            w(U_SIZE, "ValueBox", props={"bOverride_WidthOverride": True, "WidthOverride": sz(110)}, children=[text("Value", "", 12, WHITE, props_extra={"Justification": "Right"})])])])
    g = G(); g.set("sh", "Header", inp={"Header": "@entry.header"})
    g.get("gl", "Label"); g.call("sl", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@entry.label"})
    g.get("gv", "Value"); g.call("sv", E_TEXT, "SetText", inp={"self": "@gv.Value", "InText": "@entry.value"})
    g.branch("bh", "@entry.header")   # a header gets some air above it (not the first line of the table - it has the section's padding)
    g.get("gf", "Fill"); g.call("pd", E_BORDER, "SetPadding", inp={"self": "@gf.Fill", "InPadding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(6), sz(8), sz(6), sz(2))})
    g.n("cc", "call_self", function="Compute Colors"); g.chain("entry", "sh", "sl", "sv", "bh", "pd", "cc"); g.chain("bh:else", "cc")
    s = G(); s.set("ss", "Stripe", inp={"Stripe": "@entry.on"}); s.n("cc", "call_self", function="Compute Colors"); s.chain("entry", "ss", "cc")
    c = G(); tail = ["entry"]; c.get("ghd", "Header"); c.get("gst", "Stripe")
    c.call("lc", K_MATH, "SelectColor", inp={"A": mcol(c, "chd", "ColHead"), "B": mcol(c, "ctx", "ColText"), "bPickA": "@ghd.Header"}); text_color(c, "tl", "Label", "@lc.ReturnValue", tail)
    text_color(c, "tv", "Value", mcol(c, "ctv", "ColText"), tail)
    c.call("fc", K_MATH, "SelectColor", inp={"A": mcol(c, "crw", "ColRow"), "B": COL_NONE, "bPickA": "@gst.Stripe"})
    c.get("gf", "Fill"); c.call("sf", E_BORDER, "SetBrushColor", inp={"self": "@gf.Fill", "InBrushColor": "@fc.ReturnValue"}); tail.append("sf"); c.chain(*tail)
    return blueprint(W_VALROW, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Header", "bool"), var("Stripe", "bool")],
                     functions=[fn("Init", [param("label", "text"), param("value", "text"), param("header", "bool")], graph=g), fn("Set Stripe", [param("on", "bool")], graph=s),
                                compute_fn(c)], widget_tree=tree)


# ---------------- W_LinkRow (Ragdolls tab: a caption, indented on demand, and a row of W_TextButton links) ----------------
def w_link_row():
    tree = w(E_BORDER, "Fill", props={"BrushColor": COL_NONE, "Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(6), sz(3), sz(6), sz(3))}, children=[
        w(U_HBOX, "HB", children=[
            w(U_SIZE, "Indent", props={"bOverride_WidthOverride": True, "WidthOverride": 0}),
            w(U_SIZE, "LabelBox", props={"bOverride_MinDesiredWidth": True, "MinDesiredWidth": sz(220)}, slot={"VerticalAlignment": "VAlign_Center"}, children=[text("Label", "", 13, WHITE)]),
            w(U_HBOX, "Links", slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(12)})])])
    g = G(); g.set("sh", "Header", inp={"Header": "@entry.header"})
    g.get("gl", "Label"); g.call("sl", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@entry.caption"})
    g.call("iw", K_MATH, "Conv_IntToFloat", inp={"InInt": "@entry.indent"}); g.call("iws", K_MATH, "Multiply_FloatFloat", inp={"A": "@iw.ReturnValue", "B": str(float(sz(1)))})
    g.get("gi", "Indent"); g.call("si", U_SIZE, "SetWidthOverride", inp={"self": "@gi.Indent", "InWidthOverride": "@iws.ReturnValue"})
    g.get("gk", "Links"); g.call("ck", U_PANELW, "ClearChildren", inp={"self": "@gk.Links"})
    g.n("cc", "call_self", function="Compute Colors"); g.chain("entry", "sh", "sl", "si", "ck", "cc")
    al = G(); al.get("gk", "Links"); al.call("a", U_HBOX, "AddChildToHorizontalBox", inp={"self": "@gk.Links", "Content": "@entry.widget"})
    al.call("pd", "/Script/UMG.HorizontalBoxSlot", "SetPadding", inp={"self": "@a.ReturnValue", "InPadding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(10)}); al.chain("entry", "a", "pd")
    s = G(); s.set("ss", "Stripe", inp={"Stripe": "@entry.on"}); s.n("cc", "call_self", function="Compute Colors"); s.chain("entry", "ss", "cc")
    c = G(); tail = ["entry"]; c.get("ghd", "Header"); c.get("gst", "Stripe")
    c.call("lc", K_MATH, "SelectColor", inp={"A": mcol(c, "chd", "ColHead"), "B": mcol(c, "ctx", "ColText"), "bPickA": "@ghd.Header"}); text_color(c, "tl", "Label", "@lc.ReturnValue", tail)
    c.call("fc", K_MATH, "SelectColor", inp={"A": mcol(c, "crw", "ColRow"), "B": COL_NONE, "bPickA": "@gst.Stripe"})
    c.get("gf", "Fill"); c.call("sf", E_BORDER, "SetBrushColor", inp={"self": "@gf.Fill", "InBrushColor": "@fc.ReturnValue"}); tail.append("sf"); c.chain(*tail)
    return blueprint(W_LINKROW, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Header", "bool"), var("Stripe", "bool")],
                     functions=[fn("Init", [param("caption", "text"), param("indent", "int"), param("header", "bool")], graph=g), fn("Add Link", [param("widget", "object:" + E_WIDGET)], graph=al),
                                fn("Set Stripe", [param("on", "bool")], graph=s), compute_fn(c)], widget_tree=tree)



def keep_typing_fn(edit):
    """OnKeyUp of a widget with a text field of its own: while <edit> has keyboard focus every key but Esc is handled here,
    so the panel's key-up never sees the panel key (B) typed into the field and does not close."""
    g = G(); g.get("ge", edit); g.call("hf", E_WIDGET, "HasKeyboardFocus", inp={"self": "@ge." + edit})
    g.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"}); g.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Escape"})
    g.call("ne", K_MATH, "Not_PreBool", inp={"A": "@esc.ReturnValue"}); g.call("ok", K_MATH, "BooleanAND", inp={"A": "@hf.ReturnValue", "B": "@ne.ReturnValue"}); g.branch("b", "@ok.ReturnValue")
    g.call("h", K_WBL, "Handled"); g.link("h.ReturnValue", "return.ReturnValue"); g.n("r2", "return_new"); g.call("u", K_WBL, "Unhandled"); g.link("u.ReturnValue", "r2.ReturnValue")
    g.chain("entry", "b", "return"); g.chain("b:else", "r2")
    return fn("OnKeyUp", override=True, graph=g)


# ---------------- W_FolRow (Followers tab: one figure - name, status, chips; its bag tiles below; rename in place) ----------------
# A table row: name and status in fixed widths, then one fixed-width column per chip (followers.FOL_COLS) - a chip the figure's
# state does not have leaves its column empty, so the chips of all rows line up.
from followers import W_FOLROW, FOL_COLS, FOL_NAME_W, FOL_ROW_GAP, col_width, state_width


def w_fol_row():
    # outer border: transparent, only the gap below the row (between rows; the gap between the top columns and the first row is
    # the scroll box's own padding, outside the scrolled area - 2026-10-10: inside, the scroll bar began above the first row)
    gap = "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(FOL_ROW_GAP)
    tree = w(E_BORDER, "Outer", props={"BrushColor": COL_NONE, "Padding": gap}, children=[
      w(E_BORDER, "Bg", props={"Background": ROUNDBOX, "BrushColor": INV_AREA_TINT, "Padding": "(Left=0,Top=0,Right=0,Bottom=0)"}, children=[framed("BgOv",
        w(U_VBOX, "VB", children=[
            w(U_HBOX, "Head", children=[
                # name over its status, one fixed-width cell
                w(U_SIZE, "NameBox", props={"bOverride_WidthOverride": True, "WidthOverride": sz(max(FOL_NAME_W, state_width())), "Clipping": "ClipToBounds"},
                  slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(10)}, children=[
                    w(U_VBOX, "NameVB", children=[
                        w(U_HBOX, "NameHB", children=[
                            text("Name", "Name", 14, WHITE, slot={"VerticalAlignment": "VAlign_Center"}),
                            w(E_EDIT, "NameEdit", props={"HintText": "", "WidgetStyle": EDIT_STYLE, "SelectAllTextWhenFocused": True, "ClearKeyboardFocusOnCommit": False, "Visibility": "Collapsed"},
                              slot={"VerticalAlignment": "VAlign_Center", "Size": "(SizeRule=Fill,Value=1)"})]),
                        text("State", "", 11, GREY)])]),
                # chip columns: fixed widths in a wrap box - a narrow tab breaks them into the next line the same way in every row
                w(U_WRAP, "Cols", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(4) + 1, sz(4) + 1)}, slot={"Size": "(SizeRule=Fill,Value=1)", "VerticalAlignment": "VAlign_Center"},
                  children=[sizebox("Col" + k, col_width(keys), None, []) for k, keys in FOL_COLS])]),
            # a note under the head (an old follower: its clothes are part of its look), collapsed unless Set Note gives it a text
            text("Note", "", 11, GREY, wrap=True, props_extra={"Visibility": "Collapsed"}, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(6)}),
            w(U_WRAP, "Tiles", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)}, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(6)})]),
        (10, 6, 10, 8))])])
    g = G(); g.set("si", "Id", inp={"Id": "@entry.id"}); g.set("ss", "Selected", inp={"Selected": "@entry.selected"}); g.set("st", "Tinted", inp={"Tinted": "@entry.tinted"})
    g.get("gn", "Name"); g.call("sn", E_TEXT, "SetText", inp={"self": "@gn.Name", "InText": "@entry.caption"})
    g.get("gs", "State"); g.call("sst", E_TEXT, "SetText", inp={"self": "@gs.State", "InText": "@entry.state"})
    g.n("cc", "call_self", function="Compute Colors"); g.chain("entry", "si", "ss", "st", "sn", "sst", "cc")
    init = fn("Init", [param("id", "name"), param("caption", "text"), param("state", "text"), param("tinted", "bool"), param("selected", "bool")], graph=g)
    def set_chip(k):
        sc = G(); sc.get("g", "Col" + k); sc.call("a", "/Script/UMG.ContentWidget", "SetContent", inp={"self": "@g.Col" + k, "Content": "@entry.widget"})
        # the chip keeps its own width, at the column's left edge (filling the column left empty space right of the caption)
        sc.cast("cs", "/Script/UMG.SizeBoxSlot", "@a.ReturnValue"); sc.call("ha", "/Script/UMG.SizeBoxSlot", "SetHorizontalAlignment", inp={"self": "@cs.AsSizeBoxSlot", "InHorizontalAlignment": "HAlign_Left"})
        sc.chain("entry", "a", "ha")
        return fn("Set Chip " + k, [param("widget", "object:" + E_WIDGET)], graph=sc)
    at = G(); at.get("g", "Tiles"); at.call("a", U_WRAP, "AddChildToWrapBox", inp={"self": "@g.Tiles", "Content": "@entry.widget"})
    at.call("va", "/Script/UMG.WrapBoxSlot", "SetVerticalAlignment", inp={"self": "@a.ReturnValue", "InVerticalAlignment": "VAlign_Fill"}); at.chain("entry", "a", "va")
    # background: every row a tile of its own like the backpack / box surfaces (no zebra since 2026-10-10); selected = the theme's selected row colour
    c = G(); tail = ["entry"]; c.get("gse", "Selected")
    c.call("t2", K_MATH, "SelectColor", inp={"A": mcol(c, "csel", "ColRowSel"), "B": INV_AREA_TINT, "bPickA": "@gse.Selected"})
    c.get("gbg", "Bg"); c.call("sbg", E_BORDER, "SetBrushColor", inp={"self": "@gbg.Bg", "InBrushColor": "@t2.ReturnValue"}); tail.append("sbg")
    text_color(c, "tn", "Name", mcol(c, "ch", "ColHead"), tail); text_color(c, "ts", "State", mcol(c, "cd", "ColTextDim"), tail)
    text_color(c, "tno", "Note", mcol(c, "cdn", "ColTextDim"), tail); c.chain(*tail)
    sn = G(); sn.get("g", "Note"); sn.call("st", E_TEXT, "SetText", inp={"self": "@g.Note", "InText": "@entry.text"})
    sn.get("g2", "Note"); sn.call("sv", E_WIDGET, "SetVisibility", inp={"self": "@g2.Note", "InVisibility": "HitTestInvisible"}); sn.chain("entry", "st", "sv")
    # rename: label -> field (Begin Rename), Enter -> Manager.Fol Finish Rename, Esc -> back; other keys stay in the field (panel key)
    br = G(); br.call("txt", K_TXT, "Conv_StringToText", inp={"InString": "@entry.current"}); br.get("ge", "NameEdit"); br.call("stx", E_EDIT, "SetText", inp={"self": "@ge.NameEdit", "InText": "@txt.ReturnValue"})
    br.get("gl", "Name"); br.call("hl", E_WIDGET, "SetVisibility", inp={"self": "@gl.Name", "InVisibility": "Collapsed"})
    br.get("ge2", "NameEdit"); br.call("sv", E_WIDGET, "SetVisibility", inp={"self": "@ge2.NameEdit", "InVisibility": "Visible"})
    br.get("ge3", "NameEdit"); br.call("kf", E_WIDGET, "SetKeyboardFocus", inp={"self": "@ge3.NameEdit"}); br.chain("entry", "stx", "hl", "sv", "kf")
    er = G(); er.get("ge", "NameEdit"); er.call("hv", E_WIDGET, "SetVisibility", inp={"self": "@ge.NameEdit", "InVisibility": "Collapsed"})
    er.get("gl", "Name"); er.call("sl", E_WIDGET, "SetVisibility", inp={"self": "@gl.Name", "InVisibility": "HitTestInvisible"}); er.chain("entry", "hv", "sl")
    ku = G(); ku.get("ge", "NameEdit"); ku.call("hf", E_WIDGET, "HasKeyboardFocus", inp={"self": "@ge.NameEdit"}); ku.branch("bf", "@hf.ReturnValue")
    ku.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"})
    ku.call("ent", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Enter"}); ku.branch("ben", "@ent.ReturnValue")
    ku.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Escape"}); ku.branch("bes", "@esc.ReturnValue")
    ku.get("ge2", "NameEdit"); ku.call("gt", E_EDIT, "GetText", inp={"self": "@ge2.NameEdit"}); ku.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@gt.ReturnValue"})
    ku.get("gm", "Manager"); ku.get("gi", "Id"); ku.n("er", "call_self", function="End Rename"); ku.n("er2", "call_self", function="End Rename")
    ku.call("fr", MGR, "Fol Finish Rename", inp={"self": "@gm.Manager", "id": "@gi.Id", "name": "@t2s.ReturnValue"})   # End Rename first: the manager rebuilds the rows
    ku.call("h", K_WBL, "Handled"); ku.link("h.ReturnValue", "return.ReturnValue"); ku.n("r2", "return_new"); ku.call("u", K_WBL, "Unhandled"); ku.link("u.ReturnValue", "r2.ReturnValue")
    ku.chain("entry", "bf", "ben", "er", "fr", "return"); ku.chain("ben:else", "bes", "er2", "return"); ku.chain("bes:else", "return"); ku.chain("bf:else", "r2")   # Esc ends the rename only (as on the tiles)
    return blueprint(W_FOLROW, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Id", "name"), var("Selected", "bool"), var("Tinted", "bool")],
                     functions=[init] + [set_chip(k) for k, _ in FOL_COLS] + [fn("Add Tile", [param("widget", "object:" + E_WIDGET)], graph=at), fn("Set Note", [param("text", "text")], graph=sn),
                                compute_fn(c), fn("Begin Rename", [param("current", "string")], graph=br), fn("End Rename", graph=er), fn("OnKeyUp", override=True, graph=ku),
                                mouse_down_override("Fol Row Clicked", "Fol Row Context", "Id", pin="id")],
                     widget_tree=tree, defaults=HAND)


# ---------------- W_RagPoses (Ragdolls tab, an opened figure: its poses - a name + "save pose", one chip per pose of its type, a hint) ----------------
def w_rag_poses():
    pad = "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(24)
    tree = w(E_BORDER, "Fill", props={"BrushColor": COL_NONE, "Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(6), sz(6), sz(6), sz(6))}, children=[
        w(U_VBOX, "VB", children=[
            w(U_HBOX, "Row", slot={"Padding": pad}, children=[
                w(U_SIZE, "LabelBox", props={"bOverride_MinDesiredWidth": True, "MinDesiredWidth": sz(196)}, slot={"VerticalAlignment": "VAlign_Center"}, children=[text("Label", "", 13, WHITE)]),
                sizebox("NameBox", 220, None, [w(E_EDIT, "NameEdit", props={"HintText": "", "WidgetStyle": EDIT_STYLE, "SelectAllTextWhenFocused": True})], slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(12)}),
                w(U_HBOX, "Links", slot={"VerticalAlignment": "VAlign_Center"})]),
            w(U_WRAP, "Chips", props=OPT_CHIP_WRAP, slot={"Padding": "(Left=%d,Top=%d,Right=0,Bottom=0)" % (sz(24), sz(6))}),
            text("Hint", "", 11, GREY, wrap=True, slot={"Padding": "(Left=%d,Top=%d,Right=%d,Bottom=0)" % (sz(24), sz(4), sz(12))})])])
    g = G(); g.get("gl", "Label"); g.call("sl", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@entry.caption"})
    g.get("gk", "Links"); g.call("ck", U_PANELW, "ClearChildren", inp={"self": "@gk.Links"}); g.get("gc", "Chips"); g.call("cc", U_PANELW, "ClearChildren", inp={"self": "@gc.Chips"})
    g.n("col", "call_self", function="Compute Colors"); g.chain("entry", "sl", "ck", "cc", "col")
    h = G(); h.get("g", "Hint"); h.call("t", E_TEXT, "SetText", inp={"self": "@g.Hint", "InText": "@entry.text"}); h.call("e", K_TXT, "TextIsEmpty", inp={"InText": "@entry.text"})
    h.branch("b", "@e.ReturnValue")
    h.get("g2", "Hint"); h.call("hc", E_WIDGET, "SetVisibility", inp={"self": "@g2.Hint", "InVisibility": "Collapsed"}); h.get("g3", "Hint"); h.call("hv", E_WIDGET, "SetVisibility", inp={"self": "@g3.Hint", "InVisibility": "Visible"})
    h.chain("entry", "t", "b", "hc"); h.chain("b:else", "hv")
    al = G(); al.get("gk", "Links"); al.call("a", U_HBOX, "AddChildToHorizontalBox", inp={"self": "@gk.Links", "Content": "@entry.widget"})
    al.call("pd", "/Script/UMG.HorizontalBoxSlot", "SetPadding", inp={"self": "@a.ReturnValue", "InPadding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(10)}); al.chain("entry", "a", "pd")
    ac = G(); ac.get("gc", "Chips"); ac.call("a", U_WRAP, "AddChildToWrapBox", inp={"self": "@gc.Chips", "Content": "@entry.widget"}); ac.chain("entry", "a")
    gn = G(); gn.get("g", "NameEdit"); gn.call("t", E_EDIT, "GetText", inp={"self": "@g.NameEdit"}); gn.link("t.ReturnValue", "return.text")
    c = G(); tail = ["entry"]; text_color(c, "tl", "Label", mcol(c, "ctx", "ColText"), tail); text_color(c, "th", "Hint", mcol(c, "cdm", "ColTextDim"), tail); c.chain(*tail)
    return blueprint(W_RAGPOSES, E_USERWIDGET, variables=[var("Manager", "object:" + MGR)],
                     functions=[fn("Init", [param("caption", "text")], graph=g), fn("Set Hint", [param("text", "text")], graph=h),
                                fn("Add Link", [param("widget", "object:" + E_WIDGET)], graph=al), fn("Add Chip", [param("widget", "object:" + E_WIDGET)], graph=ac),
                                fn("Get Name", outputs=[param("text", "text")], graph=gn, pure=True), compute_fn(c), keep_typing_fn("NameEdit")], widget_tree=tree)

# ---------------- W_SlotTab ----------------
def w_slot_tab():
    tree = w(E_BORDER, "Fill", props={"BrushColor": COL_ROW, "Padding": "(Left=0,Top=0,Right=0,Bottom=0)"}, children=[
        w(U_VBOX, "Col", children=[
            w(U_HBOX, "HB", children=[
                w(U_SIZE, "Indent", props={"bOverride_WidthOverride": True, "WidthOverride": 0}),   # Manage sub items (Init indent)
                w(U_SIZE, "AccentBox", props={"bOverride_WidthOverride": True, "WidthOverride": sz(2)}, slot={"VerticalAlignment": "VAlign_Fill"},
                  children=[w(E_BORDER, "Accent", props={"BrushColor": COL_NONE, "Padding": "(Left=0,Top=0,Right=0,Bottom=0)"})]),
                fit_image("Thumb", 44, 44, hidden=True, slot={"Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(9), sz(4), sz(8), sz(4)), "VerticalAlignment": "VAlign_Center"}),
                w(U_VBOX, "VB", slot={**FILL, "VerticalAlignment": "VAlign_Center"}, children=[text("Name", "Slot", 13), text("Count", "0", 10, GREY)]),
            ]),
            # 2 units, not 1: at 1440p one unit is ~0.65 px, and a line below a pixel is drawn only where it happens to cover one -
            # in the left lists every second or third line was missing (game test 2026-10-03)
            w(U_SIZE, "LineBox", props={"bOverride_HeightOverride": True, "HeightOverride": max(2, sz(1))},
              children=[w(E_BORDER, "Line", props={"BrushColor": COL_LINE, "Padding": "(Left=0,Top=0,Right=0,Bottom=0)"})]),
        ])])
    hv, hf, eg = hover_parts(W_TAB, None, "Fill", image=True)
    g = G(); tail = ["entry"]
    g.set("ss", "SlotName", inp={"SlotName": "@entry.slot"}); tail.append("ss")
    g.set("ssl", "Selected", inp={"Selected": "@entry.selected"}); tail.append("ssl")
    g.get("gn", "Name"); g.call("stn", E_TEXT, "SetText", inp={"self": "@gn.Name", "InText": "@entry.caption"}); tail.append("stn")
    # count: "N", or "N (M)" with M = pieces passing the current filters (filtered < 0: no filter active)
    g.call("cs", K_STR, "Conv_IntToString", inp={"InInt": "@entry.count"}); g.call("fs", K_STR, "Conv_IntToString", inp={"InInt": "@entry.filtered"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@cs.ReturnValue", "B": " ("}); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@fs.ReturnValue"})
    g.call("c3", K_STR, "Concat_StrStr", inp={"A": "@c2.ReturnValue", "B": ")"})
    g.call("hasf", K_MATH, "GreaterEqual_IntInt", inp={"A": "@entry.filtered", "B": "0"})
    g.call("csel", K_MATH, "SelectString", inp={"A": "@c3.ReturnValue", "B": "@cs.ReturnValue", "bPickA": "@hasf.ReturnValue"})
    g.call("cnt", K_TXT, "Conv_StringToText", inp={"InString": "@csel.ReturnValue"})
    g.get("gc", "Count"); g.call("stc", E_TEXT, "SetText", inp={"self": "@gc.Count", "InText": "@cnt.ReturnValue"}); tail.append("stc")
    # empty slots: dimmed text instead of a grey area
    g.call("op", K_MATH, "SelectFloat", inp={"A": "1.0", "B": "0.45", "bPickA": "@entry.has items"})
    g.get("gn2", "Name"); g.call("so", E_TEXT, "SetOpacity", inp={"self": "@gn2.Name", "InOpacity": "@op.ReturnValue"}); tail.append("so")
    g.call("iw", K_MATH, "SelectFloat", inp={"A": str(float(sz(18))), "B": "0.0", "bPickA": "@entry.indent"})
    g.get("gin", "Indent"); g.call("siw", U_SIZE, "SetWidthOverride", inp={"self": "@gin.Indent", "InWidthOverride": "@iw.ReturnValue"}); tail.append("siw")
    g.n("cc", "call_self", function="Compute Colors"); tail.append("cc")
    g.n("ap", "call_self", function="Apply Colors", inp={"hover": "false"}); tail.append("ap")
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@entry.worn icon"})
    g.branch("b", "@iv.ReturnValue"); tail.append("b")
    g.get("gt", "Thumb"); g.call("sb", E_IMAGE, "SetBrushFromTexture", inp={"self": "@gt.Thumb", "Texture": "@entry.worn icon", "bMatchSize": "true"})
    g.get("gt2", "Thumb"); g.call("sv", E_WIDGET, "SetVisibility", inp={"self": "@gt2.Thumb", "InVisibility": "Visible"})
    g.get("gt3", "Thumb"); g.call("sh", E_WIDGET, "SetVisibility", inp={"self": "@gt3.Thumb", "InVisibility": "Hidden"})
    g.chain(*tail, "sb", "sv"); g.chain("b:else", "sh")
    init = fn("Init", [param("slot", "name"), param("caption", "text"), param("count", "int"), param("worn icon", "object:" + E_TEX2D),
                       param("selected", "bool"), param("has items", "bool"), param("filtered", "int"), param("indent", "bool")], graph=g)
    # colours from the manager theme: red accent bar + lighter row when selected; line, text
    c = G(); tail = ["entry"]; c.get("gsl", "Selected")
    c.call("ac", K_MATH, "SelectColor", inp={"A": mcol(c, "ca", "ColAccent"), "B": COL_NONE, "bPickA": "@gsl.Selected"}); brush(c, "sac", "Accent", "@ac.ReturnValue", tail)
    brush(c, "sln", "Line", mcol(c, "cl", "ColLine"), tail)
    c.call("c1", K_MATH, "SelectColor", inp={"A": mcol(c, "crs", "ColRowSel"), "B": mcol(c, "cr", "ColRow"), "bPickA": "@gsl.Selected"})
    c.call("c2", K_MATH, "SelectColor", inp={"A": mcol(c, "crsh", "ColRowSelHover"), "B": mcol(c, "crh", "ColRowHover"), "bPickA": "@gsl.Selected"})
    set_colors(c, "Fill", "@c1.ReturnValue", "@c2.ReturnValue", tail)
    text_color(c, "tn", "Name", mcol(c, "ct", "ColText"), tail); text_color(c, "tcn", "Count", mcol(c, "ctd", "ColTextDim"), tail); c.chain(*tail)
    return blueprint(W_TAB, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("SlotName", "name"), var("Selected", "bool")] + hv,
                     functions=[init, compute_fn(c), mouse_down_override("Select Slot", "Take Off Slot", "SlotName"), hide_count_fn(), count_text_fn()] + hf, event_graph=eg, widget_tree=tree, defaults=HAND)


def hide_count_fn():
    """Hide Count: rows without a number (Options categories)."""
    g = G(); g.get("gc", "Count"); g.call("hc", E_WIDGET, "SetVisibility", inp={"self": "@gc.Count", "InVisibility": "Collapsed"}); g.chain("entry", "hc")
    return fn("Hide Count", graph=g)


def count_text_fn():
    """Set Count Text: a line of its own instead of the number (weapons: "4 models, 6 skins")."""
    g = G(); g.get("gc", "Count"); g.call("st", E_TEXT, "SetText", inp={"self": "@gc.Count", "InText": "@entry.text"}); g.chain("entry", "st")
    return fn("Set Count Text", [param("text", "text")], graph=g)


def sound_mark_graph():
    """W_ClothesButton.Set Sound Mark(on): the speaker in the lower right corner (pose tiles with a sound)."""
    g = G(); g.get("gs", "SoundMark"); g.branch("b", "@entry.on")
    g.call("sv", E_WIDGET, "SetVisibility", inp={"self": "@gs.SoundMark", "InVisibility": "HitTestInvisible"})
    g.get("gs2", "SoundMark"); g.call("sc", E_WIDGET, "SetVisibility", inp={"self": "@gs2.SoundMark", "InVisibility": "Collapsed"})
    g.chain("entry", "b", "sv"); g.chain("b:else", "sc"); return g


# ---------------- W_VersionWarning (game fingerprint differs: before AltUI calls anything of the game) ----------------
W_VERWARN = M + "/W_VersionWarning"


def w_version_warning():
    """Dimmed screen, a box in the middle: title, text, the two choices (W_TextButton links -> Manager.On Menu Action)."""
    box = roundbox("Frame", COL_CHIP_FRAME, 1, slot={"HorizontalAlignment": "HAlign_Center", "VerticalAlignment": "VAlign_Center"}, children=[
        roundbox("Bg", "(R=0.05,G=0.05,B=0.06,A=0.98)", sz(18), children=[sizebox("TextBox", 560, None, [w(U_VBOX, "VB", children=[
            text("Title", "AltUI", 16, "(SpecifiedColor=(R=1,G=0.6,B=0.3,A=1))", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(10)}),
            text("Body", "", 12, WHITE, wrap=True, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(16)}),
            w(U_HBOX, "Links")])])])])
    tree = w(E_BORDER, "Dim", props={"BrushColor": "(R=0,G=0,B=0,A=0.6)", "HorizontalAlignment": "HAlign_Center", "VerticalAlignment": "VAlign_Center"}, children=[box])
    g = G(); g.get("gt", "Title"); g.call("st", E_TEXT, "SetText", inp={"self": "@gt.Title", "InText": "@entry.title"})
    g.get("gb", "Body"); g.call("sb", E_TEXT, "SetText", inp={"self": "@gb.Body", "InText": "@entry.body"}); g.chain("entry", "st", "sb")
    a = G(); a.get("gl", "Links"); a.call("ad", U_HBOX, "AddChildToHorizontalBox", inp={"self": "@gl.Links", "Content": "@entry.widget"})
    a.call("pad", "/Script/UMG.HorizontalBoxSlot", "SetPadding", inp={"self": "@ad.ReturnValue", "InPadding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(24)}); a.chain("entry", "ad", "pad")
    md = G(); md.call("h", K_WBL, "Handled"); md.link("h.ReturnValue", "return.ReturnValue"); md.chain("entry", "return")   # nothing reaches the menu below
    return blueprint(W_VERWARN, E_USERWIDGET, variables=[var("Manager", "object:" + MGR)],
                     functions=[fn("Init", [param("title", "text"), param("body", "text")], graph=g), fn("Add Link", [param("widget", "object:" + E_WIDGET)], graph=a),
                                fn("OnMouseButtonDown", override=True, graph=md)], widget_tree=tree)


# ---------------- W_ClothesButton ----------------
def w_clothes_button():
    tree = sizebox("Box", 104, None, [   # 88 icon + 2 x (frame 1 + fill 4 + TILE_SIDE 3)
        roundbox("Frame", COL_FRAME, 1, props={"Clipping": "ClipToBounds"}, children=[
            roundbox("Fill", COL_FILL, TILE_PAD, props={"Padding": TILE_FILL_PAD}, children=[
                w(U_VBOX, "VB", children=[
                    # icon + "colour adjustable" subscript (vanilla ItemButton.Image_subscript) in the lower right corner
                    w(U_OVERLAY, "IconOv", slot={"HorizontalAlignment": "HAlign_Center"}, children=[
                        fit_image("Icon", 88, 88),
                        sizebox("ColorizeBox", 20, 20, [w(E_IMAGE, "Colorize", props={"Brush": "(ResourceObject=Texture2D'%s.T_Colorize',ImageSize=(X=48,Y=48),DrawAs=Image)" % T_COLORIZE, "Visibility": "Collapsed"})],
                                slot={"HorizontalAlignment": "HAlign_Right", "VerticalAlignment": "VAlign_Bottom"}),
                        # pose rows with a sound (AnimationTable.Sound): speaker in the same corner (poses never show the colour symbol)
                        sizebox("SoundBox", 20, 20, [w(E_IMAGE, "SoundMark", props={"Brush": "(ResourceObject=Texture2D'%s/T_Sound.T_Sound',ImageSize=(X=48,Y=48),DrawAs=Image)" % M, "Visibility": "Collapsed"})],
                                slot={"HorizontalAlignment": "HAlign_Right", "VerticalAlignment": "VAlign_Bottom"}),
                        # stored colour of a piece in the content view (replaces the "colour adjustable" symbol there)
                        w(U_SIZE, "SwatchBox", props={"bOverride_WidthOverride": True, "WidthOverride": sz(20), "bOverride_HeightOverride": True, "HeightOverride": sz(20), "Visibility": "Collapsed"},
                          slot={"HorizontalAlignment": "HAlign_Right", "VerticalAlignment": "VAlign_Bottom"},
                          children=[roundbox("SwatchFrame", COL_FRAME, 1, [roundbox("Swatch", "(R=1,G=1,B=1,A=1)", 0, [])])])]),
                    text("Name", "Name", 11, WHITE, wrap=True, center=True, break_all=True, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(E_EDIT, "NameEdit", props={"HintText": "display name", "ClearKeyboardFocusOnCommit": False, "WidgetStyle": EDIT_STYLE, "Visibility": "Collapsed"},   # context menu "Rename…"
                      slot={"Padding": "(Left=%d,Top=%d,Right=%d,Bottom=0)" % (sz(4), sz(3), sz(4))}),
                    text("Badge", "", 9, "(SpecifiedColor=(R=1,G=0.6,B=0.3,A=1))", center=True, props_extra={"Visibility": "Collapsed"}),
                ])])])])
    hv, hf, eg = hover_parts(W_BTN, "Frame", "Fill", image=True)
    g = G(); tail = ["entry"]; reset_rename(g, tail, "Name")
    tile_scale(g, tail, [("Box", 104, None), ("IconBox", 88, 88), ("ColorizeBox", 20, 20), ("SwatchBox", 20, 20), ("SoundBox", 20, 20)])
    g.brk("bi", S_ITEM, "@entry.item")
    g.set("sn", "ItemName", inp={"ItemName": "@bi.Name"}); tail.append("sn")
    g.get("gsm0", "SoundMark"); g.call("csm0", E_WIDGET, "SetVisibility", inp={"self": "@gsm0.SoundMark", "InVisibility": "Collapsed"}); tail.append("csm0")   # a reused tile: only Set Sound Mark shows it
    g.branch("bca", "@bi.ColorAdjustable"); tail.append("bca")
    g.get("gcz", "Colorize"); g.call("vcz", E_WIDGET, "SetVisibility", inp={"self": "@gcz.Colorize", "InVisibility": "Visible"})
    g.get("gcz2", "Colorize"); g.call("ccz", E_WIDGET, "SetVisibility", inp={"self": "@gcz2.Colorize", "InVisibility": "Collapsed"})
    g.set("sw", "Worn", inp={"Worn": "@entry.worn"}); g.set("sow", "Owned", inp={"Owned": "@entry.owned"}); tail += ["sw", "sow"]
    # origin slot (content view: Hair / Skin / <makeup type> / Body / clothes slot) + highlight of a "Show in tab" jump
    g.set("sis", "ItemSlot", inp={"ItemSlot": "@bi.Slot"}); tail.append("sis")
    g.call("hle", K_MATH, "EqualEqual_NameName", inp={"A": "@bi.Name", "B": mcol(g, "hl", "HighlightItem")})
    g.call("hln", K_MATH, "NotEqual_NameName", inp={"A": "@bi.Name", "B": "None"}); g.call("hla", K_MATH, "BooleanAND", inp={"A": "@hle.ReturnValue", "B": "@hln.ReturnValue"})
    g.set("shl", "Highlight", inp={"Highlight": "@hla.ReturnValue"}); tail.append("shl")
    g.call("t", K_TXT, "Conv_StringToText", inp={"InString": "@bi.DisplayName"})
    g.get("gn", "Name"); g.call("stn", E_TEXT, "SetText", inp={"self": "@gn.Name", "InText": "@t.ReturnValue"}); tail.append("stn")
    g.call("gop", E_USERWIDGET, "GetOwningPlayer"); g.call("ctt", K_WBL, "Create", inp={"WidgetType": W_TOOLTIP, "OwningPlayer": "@gop.ReturnValue"}); g.cast("ctc", W_TOOLTIP, "@ctt.ReturnValue")
    g.get("gmt", "Manager"); g.n("stm", "set", var="Manager", cls=W_TOOLTIP, inp={"self": "@ctc.AsW_Tooltip", "Manager": "@gmt.Manager"})
    g.call("tti", W_TOOLTIP, "Init", inp={"self": "@ctc.AsW_Tooltip", "text": "@entry.tip"}); g.get("gbx", "Box"); g.call("stt", E_WIDGET, "SetToolTip", inp={"self": "@gbx.Box", "Widget": "@ctc.AsW_Tooltip"})
    tail += ["ctt", "stm", "tti", "stt"]
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@bi.Icon"}); g.branch("b", "@iv.ReturnValue"); tail.append("b")
    g.get("gi", "Icon"); g.call("sb", E_IMAGE, "SetBrushFromTexture", inp={"self": "@gi.Icon", "Texture": "@bi.Icon", "bMatchSize": "true"})
    tail2 = []
    g.n("cc", "call_self", function="Compute Colors"); tail2.append("cc")
    g.n("ap", "call_self", function="Apply Colors", inp={"hover": "false"}); tail2.append("ap")
    # dim: like "not owned", but without its badge - used where an entry exists yet cannot do anything (a skin on a model
    # whose materials know no skin parameters). Ownership keeps its own badge below, so the two never get mixed up.
    g.call("ndim", K_MATH, "Not_PreBool", inp={"A": "@entry.dim"}); g.call("brite", K_MATH, "BooleanAND", inp={"A": "@entry.owned", "B": "@ndim.ReturnValue"})
    g.call("ic", K_MATH, "SelectColor", inp={"A": "(R=1,G=1,B=1,A=1)", "B": "(R=0.5,G=0.5,B=0.5,A=0.6)", "bPickA": "@brite.ReturnValue"})
    g.get("gi2", "Icon"); g.call("sic", E_IMAGE, "SetColorAndOpacity", inp={"self": "@gi2.Icon", "InColorAndOpacity": "@ic.ReturnValue"}); tail2.append("sic")
    g.call("bs", K_MATH, "SelectString", inp={"A": "", "B": mts(g, "sno", "State_NotOwned"), "bPickA": "@entry.owned"})
    g.call("fs", K_MATH, "SelectString", inp={"A": mts(g, "sfv", "State_Fav"), "B": "@bs.ReturnValue", "bPickA": "@entry.fav"})
    g.call("ds", K_MATH, "SelectString", inp={"A": mts(g, "sdm", "State_Damaged"), "B": "@fs.ReturnValue", "bPickA": "@entry.damaged"})
    g.call("bt", K_TXT, "Conv_StringToText", inp={"InString": "@ds.ReturnValue"})
    g.get("gbd", "Badge"); g.call("stb", E_TEXT, "SetText", inp={"self": "@gbd.Badge", "InText": "@bt.ReturnValue"}); tail2.append("stb")
    # an empty badge takes no line (the tile height follows the content)
    g.call("bde", K_TXT, "TextIsEmpty", inp={"InText": "@bt.ReturnValue"}); g.branch("bbe", "@bde.ReturnValue"); tail2.append("bbe")
    g.get("gbd2", "Badge"); g.call("cbd", E_WIDGET, "SetVisibility", inp={"self": "@gbd2.Badge", "InVisibility": "Collapsed"})
    g.get("gbd3", "Badge"); g.call("vbd", E_WIDGET, "SetVisibility", inp={"self": "@gbd3.Badge", "InVisibility": "Visible"}); g.chain("bbe", "cbd"); g.chain("bbe:else", "vbd")
    # tail: ... "sn", "bca" | "vcz"/"ccz" -> rest
    i = tail.index("bca"); rest = tail[i + 1:]; tail = tail[:i + 1]
    g.chain(*tail, "vcz", *rest, "sb", *tail2); g.chain("bca:else", "ccz", rest[0]); g.chain("b:else", tail2[0])
    init = fn("Init", [param("item", T_ITEM), param("worn", "bool"), param("owned", "bool"), param("fav", "bool"), param("damaged", "bool"), param("tip", "text"), param("dim", "bool")], graph=g)
    # border: normally light, "worn" colour when worn, dimmed when not owned; fill: dark, tinted when worn
    c = G(); tail = ["entry"]; c.get("gw", "Worn"); c.get("go", "Owned")
    c.call("f1", K_MATH, "SelectColor", inp={"A": mcol(c, "cf", "ColFrame"), "B": mcol(c, "cfl", "ColFrameLocked"), "bPickA": "@go.Owned"})
    c.call("f2", K_MATH, "SelectColor", inp={"A": mcol(c, "cfw", "ColFrameWorn"), "B": "@f1.ReturnValue", "bPickA": "@gw.Worn"})
    c.call("c1", K_MATH, "SelectColor", inp={"A": mcol(c, "cw", "ColFillWorn"), "B": mcol(c, "cfi", "ColFill"), "bPickA": "@gw.Worn"})
    c.call("c2", K_MATH, "SelectColor", inp={"A": mcol(c, "cwh", "ColFillWornHover"), "B": mcol(c, "cfh", "ColFillHover"), "bPickA": "@gw.Worn"})
    c.get("ghl", "Highlight")   # "Show in tab" target: accent frame
    c.call("f3", K_MATH, "SelectColor", inp={"A": mcol(c, "cac", "ColAccent"), "B": "@f2.ReturnValue", "bPickA": "@ghl.Highlight"})
    c.call("f4", K_MATH, "SelectColor", inp={"A": mcol(c, "cac2", "ColAccent"), "B": mcol(c, "cfrh", "ColFrameHover"), "bPickA": "@ghl.Highlight"})
    set_colors(c, "Frame", "@f3.ReturnValue", "@f4.ReturnValue", tail)
    set_colors(c, "Fill", "@c1.ReturnValue", "@c2.ReturnValue", tail)
    text_color(c, "tn", "Name", mcol(c, "ct", "ColText"), tail); c.chain(*tail)
    # Set Color Swatch(color): show the stored colour bottom right instead of the "colour adjustable" symbol (content view only)
    sc = G(); sc.get("gsw", "Swatch"); sc.call("sb", E_BORDER, "SetBrushColor", inp={"self": "@gsw.Swatch", "InBrushColor": "@entry.color"})
    sc.get("gsb", "SwatchBox"); sc.call("sv", E_WIDGET, "SetVisibility", inp={"self": "@gsb.SwatchBox", "InVisibility": "Visible"})
    sc.get("gcb", "ColorizeBox"); sc.call("cv", E_WIDGET, "SetVisibility", inp={"self": "@gcb.ColorizeBox", "InVisibility": "Collapsed"}); sc.chain("entry", "sb", "sv", "cv")
    # rename (context menu): label -> text field (Begin Rename), back (End Rename); Enter -> Manager.Finish Item Rename, Esc -> cancel;
    # focus loss is polled by the manager (Poll Rename) - no per-tile Tick (up to 2600 tiles with "unlimited")
    br = G(); br.set("se", "Editing", inp={"Editing": "true"}); br.call("txt", K_TXT, "Conv_StringToText", inp={"InString": "@entry.current"})
    br.get("ge", "NameEdit"); br.call("stx", E_EDIT, "SetText", inp={"self": "@ge.NameEdit", "InText": "@txt.ReturnValue"})
    br.get("gl", "Name"); br.call("hl", E_WIDGET, "SetVisibility", inp={"self": "@gl.Name", "InVisibility": "Collapsed"})
    br.get("ge2", "NameEdit"); br.call("sv", E_WIDGET, "SetVisibility", inp={"self": "@ge2.NameEdit", "InVisibility": "Visible"})
    br.get("ge3", "NameEdit"); br.call("kf", E_WIDGET, "SetKeyboardFocus", inp={"self": "@ge3.NameEdit"}); br.chain("entry", "se", "stx", "hl", "sv", "kf")
    er = G(); er.set("se", "Editing", inp={"Editing": "false"})
    er.get("ge", "NameEdit"); er.call("hv", E_WIDGET, "SetVisibility", inp={"self": "@ge.NameEdit", "InVisibility": "Collapsed"})
    er.get("gl", "Name"); er.call("sl", E_WIDGET, "SetVisibility", inp={"self": "@gl.Name", "InVisibility": "Visible"}); er.chain("entry", "se", "hv", "sl")
    ku = G(); ku.get("ged", "Editing"); ku.branch("be", "@ged.Editing"); ku.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"})
    ku.call("ent", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Enter"}); ku.branch("ben", "@ent.ReturnValue")
    ku.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Escape"}); ku.branch("bes", "@esc.ReturnValue")
    ku.get("ge", "NameEdit"); ku.call("gt", E_EDIT, "GetText", inp={"self": "@ge.NameEdit"}); ku.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@gt.ReturnValue"})
    ku.get("gm", "Manager"); ku.get("gi", "ItemName"); ku.call("fr", MGR, "Finish Item Rename", inp={"self": "@gm.Manager", "name": "@gi.ItemName", "text": "@t2s.ReturnValue"})
    ku.n("er", "call_self", function="End Rename"); ku.n("er2", "call_self", function="End Rename")   # End Rename first: Finish rebuilds the list and drops this tile
    ku.call("h", K_WBL, "Handled"); ku.link("h.ReturnValue", "return.ReturnValue"); ku.n("r2", "return_new"); ku.call("u", K_WBL, "Unhandled"); ku.link("u.ReturnValue", "r2.ReturnValue")
    ku.chain("entry", "be", "ben", "er", "fr", "return"); ku.chain("ben:else", "bes", "er2", "return"); ku.chain("bes:else", "return"); ku.chain("be:else", "r2")
    pr = G(); pr.get("ged", "Editing"); pr.get("ge", "NameEdit"); pr.call("hf", E_WIDGET, "HasKeyboardFocus", inp={"self": "@ge.NameEdit"})
    pr.call("nf", K_MATH, "Not_PreBool", inp={"A": "@hf.ReturnValue"}); pr.call("lost", K_MATH, "BooleanAND", inp={"A": "@ged.Editing", "B": "@nf.ReturnValue"}); pr.branch("b", "@lost.ReturnValue")
    pr.n("er", "call_self", function="End Rename"); pr.get("ged2", "Editing"); pr.link("ged2.Editing", "return.active"); pr.chain("entry", "b", "er", "return"); pr.chain("b:else", "return")
    # Set Scale(scale): the sizes of Init with a factor of the caller's (inventory tiles have a size of their own, Options > Tiles)
    ssc = G(); tail = ["entry"]; tile_scale(ssc, tail, [("Box", 104, None), ("IconBox", 88, 88), ("ColorizeBox", 20, 20), ("SwatchBox", 20, 20)], scale_pin="@entry.scale"); ssc.chain(*tail)
    return blueprint(W_BTN, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("ItemName", "name"), var("ItemSlot", "name"), var("Worn", "bool"), var("Owned", "bool"), var("Highlight", "bool"), var("Editing", "bool")] + hv,
                     functions=[fn("Set Tile Size", [param("width", "float"), param("height", "float")], graph=tile_size_graph()), init, fn("Set Scale", [param("scale", "float")], graph=ssc), compute_fn(c), mouse_down_override("On Item Clicked", "On Item Context", "ItemName"), fn("Set Color Swatch", [param("color", S_LINCOLOR)], graph=sc),
                                fn("Set Sound Mark", [param("on", "bool")], graph=sound_mark_graph()), fn("Begin Rename", [param("current", "string")], graph=br), fn("End Rename", graph=er), fn("OnKeyUp", override=True, graph=ku), fn("Poll Rename", outputs=[param("active", "bool")], graph=pr)] + hf,
                     event_graph=eg, widget_tree=tree, defaults=HAND)


# ---------------- W_SubTab ----------------
def w_sub_tab():
    tree = roundbox("Frame", COL_CHIP_FRAME, 1, children=[
        roundbox("Fill", COL_CHIP, 0, props={"Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(10), sz(4), sz(10), sz(4))}, children=[
            w(U_SIZE, "MinBox", children=[w(U_HBOX, "Row", slot={"HorizontalAlignment": "HAlign_Center", "VerticalAlignment": "VAlign_Center"}, children=[
                w(U_SIZE, "ThumbBox", props={"Visibility": "Collapsed"}, children=[w(E_IMAGE, "Thumb")]), text("Label", "Alle", 12, slot={"VerticalAlignment": "VAlign_Center"})])])])])
    hv, hf, eg = hover_parts(W_SUB, "Frame", "Fill")
    g = G(); tail = ["entry"]
    g.set("sg", "Group", inp={"Group": "@entry.group"}); tail.append("sg")
    g.set("ssl", "Selected", inp={"Selected": "@entry.selected"}); tail.append("ssl")
    g.get("gl", "Label"); g.call("st", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@entry.caption"}); tail.append("st")
    g.n("cc", "call_self", function="Compute Colors"); tail.append("cc")
    g.n("ap", "call_self", function="Apply Colors", inp={"hover": "false"}); tail.append("ap")
    g.chain(*tail)
    init = fn("Init", [param("group", "name"), param("caption", "text"), param("selected", "bool")], graph=g)
    c = G(); tail = ["entry"]; c.get("gsl", "Selected")
    c.call("f1", K_MATH, "SelectColor", inp={"A": mcol(c, "ca", "ColAccent"), "B": mcol(c, "ccf", "ColChipFrame"), "bPickA": "@gsl.Selected"})
    c.call("f2", K_MATH, "SelectColor", inp={"A": mcol(c, "ca2", "ColAccent"), "B": mcol(c, "ccfh", "ColChipFrameHover"), "bPickA": "@gsl.Selected"})
    c.call("c1", K_MATH, "SelectColor", inp={"A": mcol(c, "ccs", "ColChipSel"), "B": mcol(c, "cch", "ColChip"), "bPickA": "@gsl.Selected"})
    c.call("c2", K_MATH, "SelectColor", inp={"A": mcol(c, "ccsh", "ColChipSelHover"), "B": mcol(c, "cchh", "ColChipHover"), "bPickA": "@gsl.Selected"})
    set_colors(c, "Frame", "@f1.ReturnValue", "@f2.ReturnValue", tail)
    set_colors(c, "Fill", "@c1.ReturnValue", "@c2.ReturnValue", tail)
    text_color(c, "tl", "Label", mcol(c, "ct", "ColText"), tail); c.chain(*tail)
    tp = G(); tp.call("gop", E_USERWIDGET, "GetOwningPlayer"); tp.call("ctt", K_WBL, "Create", inp={"WidgetType": W_TOOLTIP, "OwningPlayer": "@gop.ReturnValue"}); tp.cast("ctc", W_TOOLTIP, "@ctt.ReturnValue")
    tp.get("gmt", "Manager"); tp.n("stm", "set", var="Manager", cls=W_TOOLTIP, inp={"self": "@ctc.AsW_Tooltip", "Manager": "@gmt.Manager"})
    tp.call("tti", W_TOOLTIP, "Init", inp={"self": "@ctc.AsW_Tooltip", "text": "@entry.tip"}); tp.get("gfr", "Frame"); tp.call("stt", E_WIDGET, "SetToolTip", inp={"self": "@gfr.Frame", "Widget": "@ctc.AsW_Tooltip"})
    tp.chain("entry", "ctt", "stm", "tti", "stt")
    # Set Thumb (Options > Theme, "Show previews"): the picture instead of the caption, through its own M_ImageBox instance (rounded
    # corners, the filters of the picture); width / height in pixels of the layout (sz), radius in screen pixels
    th = G(); th.call("cr", "/Script/Engine.KismetMaterialLibrary", "CreateDynamicMaterialInstance", inp={"Parent": M + "/Mat/M_ImageBox"}); th.set("sm", "ThumbMID", inp={"ThumbMID": "@cr.ReturnValue"})
    tail = ["entry", "cr", "sm"]
    th.get("gm0", "ThumbMID"); th.call("stx", "/Script/Engine.MaterialInstanceDynamic", "SetTextureParameterValue", inp={"self": "@gm0.ThumbMID", "ParameterName": "Tex", "Value": "@entry.tex"}); tail.append("stx")
    th.get("gm1", "ThumbMID"); th.call("srd", "/Script/Engine.MaterialInstanceDynamic", "SetScalarParameterValue", inp={"self": "@gm1.ThumbMID", "ParameterName": "Radius", "Value": "@entry.radius"}); tail.append("srd")
    th.n("flt", "call_self", function="Set Thumb Filters", inp={"hue": "@entry.hue", "sepia": "@entry.sepia", "invert": "@entry.invert"}); tail.append("flt")
    th.get("gi", "Thumb"); th.get("gm2", "ThumbMID"); th.call("sbm", E_IMAGE, "SetBrushFromMaterial", inp={"self": "@gi.Thumb", "Material": "@gm2.ThumbMID"}); tail.append("sbm")
    th.get("gb1", "ThumbBox"); th.call("sw", U_SIZE, "SetWidthOverride", inp={"self": "@gb1.ThumbBox", "InWidthOverride": "@entry.width"}); tail.append("sw")
    th.get("gb2", "ThumbBox"); th.call("sh", U_SIZE, "SetHeightOverride", inp={"self": "@gb2.ThumbBox", "InHeightOverride": "@entry.height"}); tail.append("sh")
    th.get("gb3", "ThumbBox"); th.call("sv", E_WIDGET, "SetVisibility", inp={"self": "@gb3.ThumbBox", "InVisibility": "Visible"}); tail.append("sv")
    th.get("gl", "Label"); th.call("lc", E_WIDGET, "SetVisibility", inp={"self": "@gl.Label", "InVisibility": "Collapsed"}); tail.append("lc")
    th.get("gf", "Fill"); th.call("pd", E_BORDER, "SetPadding", inp={"self": "@gf.Fill", "InPadding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % ((sz(THUMB_PAD),) * 4)}); tail.append("pd")
    th.chain(*tail)
    tf = G(); tf.get("gm", "ThumbMID"); tf.call("vm", K_SYS, "IsValid", inp={"Object": "@gm.ThumbMID"}); tf.branch("bm", "@vm.ReturnValue"); tail = ["entry", "bm"]
    for par, pin in (("Hue", "hue"), ("Sepia", "sepia"), ("Invert", "invert")):
        tf.get("g" + par, "ThumbMID"); tf.call("s" + par, "/Script/Engine.MaterialInstanceDynamic", "SetScalarParameterValue", inp={"self": "@g%s.ThumbMID" % par, "ParameterName": par, "Value": "@entry." + pin}); tail.append("s" + par)
    tf.chain(*tail)
    # Set Thumb Size: a chip without a picture in a row of previews ("none", a picture that cannot be read) - as large as the previews
    # (MinBox around the row: at least width x height), the caption in the middle
    tg = G(); tail = ["entry"]
    tg.get("gb1", "MinBox"); tg.call("sw", U_SIZE, "SetMinDesiredWidth", inp={"self": "@gb1.MinBox", "InMinDesiredWidth": "@entry.width"}); tail.append("sw")
    tg.get("gb2", "MinBox"); tg.call("sh", U_SIZE, "SetMinDesiredHeight", inp={"self": "@gb2.MinBox", "InMinDesiredHeight": "@entry.height"}); tail.append("sh")
    tg.get("gf", "Fill"); tg.call("pd", E_BORDER, "SetPadding", inp={"self": "@gf.Fill", "InPadding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % ((sz(THUMB_PAD),) * 4)}); tail.append("pd")
    tg.chain(*tail)
    thumb_fns = [fn("Set Thumb Size", [param("width", "float"), param("height", "float")], graph=tg), fn("Set Thumb", [param("tex", "object:/Script/Engine.Texture"), param("width", "float"), param("height", "float"), param("radius", "float"),
                                  param("hue", "float"), param("sepia", "float"), param("invert", "float")], graph=th),
                 fn("Set Thumb Filters", [param("hue", "float"), param("sepia", "float"), param("invert", "float")], graph=tf)]
    return blueprint(W_SUB, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Group", "name"), var("Selected", "bool"), var("ThumbMID", "object:/Script/Engine.MaterialInstanceDynamic")] + hv,
                     functions=[init, fn("Set Tip", [param("tip", "text")], graph=tp), compute_fn(c), refresh_fn(), mouse_down_override("Select SubTab", "SubTab Context", "Group")] + thumb_fns + hf, event_graph=eg, widget_tree=tree, defaults=HAND)


THUMB_PAD = 3   # chip with a preview: the picture this far inside the chip's frame


# ---------------- W_TopTab (tab bar at the top: text and / or icon (left or right of the text) + red underline) ----------------
TOP_ICON = 18   # icon edge in the tab bar (text 14)
# one-row tab bar: font sizes 14 down to 10, then at 10 the captions cut to 16 .. 4 characters - encoded size * 100 + characters (0 = all)
TOP_FIT_STEPS = sorted({sz(v) * 100 for v in range(14, 9, -1)}, reverse=True) + [sz(10) * 100 + n for n in (16, 14, 12, 10, 8, 6, 4)]


def w_top_tab():
    # 10 to the sides (was 14): with the Face tab the thirteen tabs no longer fitted one row at the "one third" layout
    def icon(n): return sizebox(n + "Box", TOP_ICON, TOP_ICON, [w(E_IMAGE, n)], slot={"VerticalAlignment": "VAlign_Center"})
    def gap(n): return sizebox(n, 5, 1, [])
    tree = w(E_BORDER, "Fill", props={"BrushColor": COL_NONE, "Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(10), sz(4), sz(10), sz(0))}, children=[
        w(U_VBOX, "VB", children=[
            w(U_HBOX, "Row", slot={"HorizontalAlignment": "HAlign_Center", "Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(5)}, children=[
                icon("IconL"), gap("GapL"), text("Label", "Reiter", 14, slot={"VerticalAlignment": "VAlign_Center"}), gap("GapR"), icon("IconR")]),
            w(U_SIZE, "LineBox", props={"bOverride_HeightOverride": True, "HeightOverride": sz(1.5)},
              children=[w(E_BORDER, "Accent", props={"BrushColor": COL_NONE, "Padding": "(Left=0,Top=0,Right=0,Bottom=0)"})]),
        ])])
    hv, hf, eg = hover_parts(W_TOP, None, "Fill", image=True)
    g = G(); tail = ["entry"]
    g.set("sp", "Page", inp={"Page": "@entry.page"}); tail.append("sp")
    g.set("ssl", "Selected", inp={"Selected": "@entry.selected"}); tail.append("ssl")
    g.get("gl", "Label"); g.call("st", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@entry.caption"}); tail.append("st")
    g.call("cts", K_TXT, "Conv_TextToString", inp={"InText": "@entry.caption"}); g.set("scp", "Caption", inp={"Caption": "@cts.ReturnValue"}); tail.append("scp")   # Set Fit cuts from the full one
    # style 0 = text, 1 = icon, 2 = icon + text; the icon left or right of the text (right); no icon texture -> text
    g.call("hasi", K_SYS, "IsValid", inp={"Object": "@entry.icon"}); g.call("s0", K_MATH, "Greater_IntInt", inp={"A": "@entry.style", "B": "0"})
    g.call("ico", K_MATH, "BooleanAND", inp={"A": "@s0.ReturnValue", "B": "@hasi.ReturnValue"})
    g.call("s1", K_MATH, "EqualEqual_IntInt", inp={"A": "@entry.style", "B": "1"}); g.call("only", K_MATH, "BooleanAND", inp={"A": "@s1.ReturnValue", "B": "@hasi.ReturnValue"})
    g.call("txt", K_MATH, "Not_PreBool", inp={"A": "@only.ReturnValue"}); g.call("both", K_MATH, "BooleanAND", inp={"A": "@ico.ReturnValue", "B": "@txt.ReturnValue"})
    g.call("nr", K_MATH, "Not_PreBool", inp={"A": "@entry.right"})
    g.call("il", K_MATH, "BooleanAND", inp={"A": "@ico.ReturnValue", "B": "@nr.ReturnValue"}); g.call("ir", K_MATH, "BooleanAND", inp={"A": "@ico.ReturnValue", "B": "@entry.right"})
    g.call("gl_", K_MATH, "BooleanAND", inp={"A": "@both.ReturnValue", "B": "@nr.ReturnValue"}); g.call("gr_", K_MATH, "BooleanAND", inp={"A": "@both.ReturnValue", "B": "@entry.right"})
    # next to text the icon moves up onto the caps' centre (the text box keeps room for descenders below them; game test: 2.5 px low at
    # 1440p) - a render translation, so the row keeps the height of the text-only bar; icons only: no shift
    g.call("ty", K_MATH, "SelectFloat", inp={"A": str(float(-sz(2))), "B": "0.0", "bPickA": "@both.ReturnValue"}); g.call("tv", K_MATH, "MakeVector2D", inp={"X": "0.0", "Y": "@ty.ReturnValue"})
    for wn in ("IconLBox", "IconRBox"):
        g.get("gt" + wn, wn); g.call("t" + wn, E_WIDGET, "SetRenderTranslation", inp={"self": "@gt%s.%s" % (wn, wn), "Translation": "@tv.ReturnValue"}); tail.append("t" + wn)
    for wn in ("IconL", "IconR"):
        g.get("g" + wn, wn); g.call("b" + wn, E_IMAGE, "SetBrushFromTexture", inp={"self": "@g%s.%s" % (wn, wn), "Texture": "@entry.icon", "bMatchSize": "false"}); tail.append("b" + wn)
    g.call("op", K_MATH, "SelectFloat", inp={"A": "1.0", "B": "0.7", "bPickA": "@entry.selected"})
    g.get("gr2", "Row"); g.call("so", E_WIDGET, "SetRenderOpacity", inp={"self": "@gr2.Row", "InOpacity": "@op.ReturnValue"}); tail.append("so")
    g.chain(*tail); exits = [tail[-1]]
    # SetVisibility expects ESlateVisibility: two branch paths per widget (Visible / Collapsed)
    for wn, cond in (("IconLBox", "@il.ReturnValue"), ("IconRBox", "@ir.ReturnValue"), ("GapL", "@gl_.ReturnValue"), ("GapR", "@gr_.ReturnValue"), ("Label", "@txt.ReturnValue")):
        g.branch("bv" + wn, cond)
        g.get("gv" + wn, wn); g.call("sv" + wn, E_WIDGET, "SetVisibility", inp={"self": "@gv%s.%s" % (wn, wn), "InVisibility": "Visible"})
        g.get("gc" + wn, wn); g.call("sc" + wn, E_WIDGET, "SetVisibility", inp={"self": "@gc%s.%s" % (wn, wn), "InVisibility": "Collapsed"})
        for e in exits: g.chain(e, "bv" + wn)
        g.chain("bv" + wn, "sv" + wn); g.chain("bv%s:else" % wn, "sc" + wn); exits = ["sv" + wn, "sc" + wn]
    g.n("cc", "call_self", function="Compute Colors"); g.n("ap", "call_self", function="Apply Colors", inp={"hover": "false"})
    for e in exits: g.chain(e, "cc")
    g.chain("cc", "ap")
    init = fn("Init", [param("page", "name"), param("caption", "text"), param("selected", "bool"), param("icon", "object:" + E_TEX2D), param("style", "int"), param("right", "bool")], graph=g)
    # Set Fit (one-row tab bar, W_Panel.Fit Top Tabs): font size of the caption, and at most maxc characters ("…" at the end; 0 = all)
    sf = G(); sf.get("gl", "Label"); sf.get("gf", "Font", cls=E_TEXT); sf.link("gl.Label", "gf.self"); SFI = "/Script/SlateCore.SlateFontInfo"; sf.brk("bf", SFI, "@gf.Font")
    sf.make("mf", SFI, FontObject="@bf.FontObject", FontMaterial="@bf.FontMaterial", OutlineSettings="@bf.OutlineSettings", TypefaceFontName="@bf.TypefaceFontName",
            Size="@entry.size", LetterSpacing="@bf.LetterSpacing")
    sf.get("gl2", "Label"); sf.call("sfn", E_TEXT, "SetFont", inp={"self": "@gl2.Label", "InFontInfo": "@mf.SlateFontInfo"})
    sf.get("gc", "Caption"); sf.call("ln", K_STR, "Len", inp={"S": "@gc.Caption"}); sf.call("pos", K_MATH, "Greater_IntInt", inp={"A": "@entry.maxc", "B": "0"})
    sf.call("lng", K_MATH, "Greater_IntInt", inp={"A": "@ln.ReturnValue", "B": "@entry.maxc"}); sf.call("cut", K_MATH, "BooleanAND", inp={"A": "@pos.ReturnValue", "B": "@lng.ReturnValue"})
    sf.call("m1", K_MATH, "Subtract_IntInt", inp={"A": "@entry.maxc", "B": "1"}); sf.call("lf", K_STR, "Left", inp={"SourceString": "@gc.Caption", "Count": "@m1.ReturnValue"})
    sf.call("tr", K_STR, "TrimTrailing", inp={"SourceString": "@lf.ReturnValue"}); sf.call("el", K_STR, "Concat_StrStr", inp={"A": "@tr.ReturnValue", "B": "\u2026"})
    sf.call("sel", K_MATH, "SelectString", inp={"A": "@el.ReturnValue", "B": "@gc.Caption", "bPickA": "@cut.ReturnValue"}); sf.call("tx", K_TXT, "Conv_StringToText", inp={"InString": "@sel.ReturnValue"})
    sf.get("gl3", "Label"); sf.call("stx", E_TEXT, "SetText", inp={"self": "@gl3.Label", "InText": "@tx.ReturnValue"}); sf.chain("entry", "sfn", "stx")
    set_fit = fn("Set Fit", [param("size", "int"), param("maxc", "int")], graph=sf)
    c = G(); tail = ["entry"]; c.get("gsl", "Selected")
    c.call("ac", K_MATH, "SelectColor", inp={"A": mcol(c, "ca", "ColAccent"), "B": COL_NONE, "bPickA": "@gsl.Selected"}); brush(c, "sac", "Accent", "@ac.ReturnValue", tail)
    set_colors(c, "Fill", COL_NONE, mcol(c, "cth", "ColTopHover"), tail)
    text_color(c, "tl", "Label", mcol(c, "ct", "ColText"), tail)
    for wn in ("IconL", "IconR"):
        c.get("g" + wn, wn); c.call("c" + wn, E_IMAGE, "SetColorAndOpacity", inp={"self": "@g%s.%s" % (wn, wn), "InColorAndOpacity": mcol(c, "ci" + wn, "ColText")}); tail.append("c" + wn)
    c.chain(*tail)
    return blueprint(W_TOP, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Page", "name"), var("Selected", "bool"), var("Caption", "string")] + hv,
                     functions=[init, set_fit, compute_fn(c), refresh_fn(), mouse_down_override("Select Page", "Tab Context", "Page")] + hf, event_graph=eg, widget_tree=tree, defaults=HAND)


def tile_colors(*texts):
    """Compute Colors of a plain tile (frame/fill without state) + text colours [(widget, ColX), ...]."""
    c = G(); tail = ["entry"]
    set_colors(c, "Frame", mcol(c, "cf", "ColFrame"), mcol(c, "cfh", "ColFrameHover"), tail); set_colors(c, "Fill", mcol(c, "cfi", "ColFill"), mcol(c, "cfih", "ColFillHover"), tail)
    for i, (wn, col) in enumerate(texts): text_color(c, "tc%d" % i, wn, mcol(c, "cc%d" % i, col), tail)
    c.chain(*tail); return compute_fn(c)


# ---------------- W_OutfitButton (cols x rows piece icons + label; index -1 = "+ save") ----------------
OUTFIT_MAX = 6            # the grid holds up to OUTFIT_MAX x OUTFIT_MAX icons; Init shows cols x rows of them (Options > Tiles, default 3 x 3)
OUTFIT_ICONS = OUTFIT_MAX * OUTFIT_MAX


W_VROW = M + "/W_VRow"


def w_vrow():
    """One row of tiles of a virtual list (vlist.py): exactly the tiles the list gives it, left to right, as high as Set Tile Size says."""
    tree = w(U_SIZE, "Box", children=[w(E_BORDER, "Pad", props={"BrushColor": "(R=0,G=0,B=0,A=0)", "Padding": "(Left=0,Top=0,Right=0,Bottom=0)"}, children=[w(U_HBOX, "Row")])])
    # Set Fit (lists whose rows grow with their content): no fixed height, at least min, the gap below as padding
    f = G(); f.get("g", "Box"); f.call("ch", U_SIZE, "ClearHeightOverride", inp={"self": "@g.Box"}); f.get("g2", "Box"); f.call("mh", U_SIZE, "SetMinDesiredHeight", inp={"self": "@g2.Box", "InMinDesiredHeight": "@entry.min"})
    f.make("m", "/Script/SlateCore.Margin", Left="0.0", Top="0.0", Right="0.0", Bottom="@entry.gap"); f.get("gp", "Pad"); f.call("pp", E_BORDER, "SetPadding", inp={"self": "@gp.Pad", "InPadding": "@m.Margin"})
    f.chain("entry", "ch", "mh", "pp")
    # Set Gap (growing rows, fixed height RowH + gap): the gap as padding below, so tiles that fill the row end above it
    gp = G(); gp.make("m", "/Script/SlateCore.Margin", Left="0.0", Top="0.0", Right="0.0", Bottom="@entry.gap"); gp.get("g", "Pad")
    gp.call("pp", E_BORDER, "SetPadding", inp={"self": "@g.Pad", "InPadding": "@m.Margin"}); gp.chain("entry", "pp")
    # Content Height: the highest tile wants (desired sizes are bottom-up: the row's own fixed height does not change them)
    ch = G(); ch.get("g", "Row"); ch.call("ac", U_PANELW, "GetAllChildren", inp={"self": "@g.Row"}); ch.set("s0", "MaxH", inp={"MaxH": "0.0"}); ch.foreach("fc", "@ac.ReturnValue")
    ch.call("ds", E_WIDGET, "GetDesiredSize", inp={"self": "@fc.Array Element"}); ch.call("bd", K_MATH, "BreakVector2D", inp={"InVec": "@ds.ReturnValue"}); ch.get("gm", "MaxH")
    ch.call("mx", K_MATH, "FMax", inp={"A": "@gm.MaxH", "B": "@bd.Y"}); ch.set("sm", "MaxH", inp={"MaxH": "@mx.ReturnValue"}); ch.get("gm2", "MaxH"); ch.link("gm2.MaxH", "return.h")
    ch.chain("entry", "s0", "fc"); ch.chain("fc", "sm"); ch.chain("fc:Completed", "return")
    c = G(); c.get("g", "Row"); c.call("c", U_PANELW, "ClearChildren", inp={"self": "@g.Row"}); c.chain("entry", "c")
    a = G(); a.get("g", "Row"); a.call("a", U_HBOX, "AddChildToHorizontalBox", inp={"self": "@g.Row", "Content": "@entry.widget"})
    a.make("m", "/Script/SlateCore.Margin", Left="@entry.left", Top="0.0", Right="0.0", Bottom="0.0")
    a.call("p", "/Script/UMG.HorizontalBoxSlot", "SetPadding", inp={"self": "@a.ReturnValue", "InPadding": "@m.Margin"})
    a.branch("bf", "@entry.fill")   # fill: the tiles of a growing row all as high as its highest
    a.call("v", "/Script/UMG.HorizontalBoxSlot", "SetVerticalAlignment", inp={"self": "@a.ReturnValue", "InVerticalAlignment": "VAlign_Top"})
    a.call("vf", "/Script/UMG.HorizontalBoxSlot", "SetVerticalAlignment", inp={"self": "@a.ReturnValue", "InVerticalAlignment": "VAlign_Fill"})
    a.chain("entry", "a", "p", "bf", "vf"); a.chain("bf:else", "v")
    return blueprint(W_VROW, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("MaxH", "float")],
                     functions=[fn("Clear", graph=c), fn("Add", [param("widget", "object:" + E_WIDGET), param("left", "float"), param("fill", "bool")], graph=a),
                                fn("Set Tile Size", [param("width", "float"), param("height", "float")], graph=tile_size_graph()),
                                fn("Set Fit", [param("min", "float"), param("gap", "float")], graph=f), fn("Set Gap", [param("gap", "float")], graph=gp), fn("Content Height", outputs=[param("h", "float")], graph=ch)], widget_tree=tree)


def vlist_panel_fns(L, scroll, vb, top, wrap, bottom):
    """Panel side of the virtual list L (vlist.py): "<L> View" = the part of the list box (vb) inside the scroll box's viewport, in the
    list's own coordinates (top / bottom) and its width - wherever the list sits in the scrolled content; "<L> Spacers" (heights of the
    rows above / below the window), "<L> Clear" / "<L> Add" (the wrap box with the window's widgets)."""
    v = G(); v.get("gs", scroll); v.call("geos", E_WIDGET, "GetCachedGeometry", inp={"self": "@gs." + scroll}); v.call("szs", K_SLATE, "GetLocalSize", inp={"Geometry": "@geos.ReturnValue"})
    v.get("gv", vb); v.call("geov", E_WIDGET, "GetCachedGeometry", inp={"self": "@gv." + vb}); v.call("szv", K_SLATE, "GetLocalSize", inp={"Geometry": "@geov.ReturnValue"})
    v.call("abs", K_SLATE, "LocalToAbsolute", inp={"Geometry": "@geov.ReturnValue", "LocalCoordinate": "(X=0,Y=0)"})
    v.call("loc", K_SLATE, "AbsoluteToLocal", inp={"Geometry": "@geos.ReturnValue", "AbsoluteCoordinate": "@abs.ReturnValue"})
    v.call("bl", K_MATH, "BreakVector2D", inp={"InVec": "@loc.ReturnValue"}); v.call("bs", K_MATH, "BreakVector2D", inp={"InVec": "@szs.ReturnValue"}); v.call("bv", K_MATH, "BreakVector2D", inp={"InVec": "@szv.ReturnValue"})
    v.call("t", K_MATH, "Multiply_FloatFloat", inp={"A": "@bl.Y", "B": "-1.0"}); v.call("b", K_MATH, "Subtract_FloatFloat", inp={"A": "@bs.Y", "B": "@bl.Y"})
    v.link("t.ReturnValue", "return.top"); v.link("b.ReturnValue", "return.bottom"); v.link("bv.X", "return.width"); v.chain("entry", "return")
    s = G(); s.get("g", top); s.call("t", U_SIZE, "SetHeightOverride", inp={"self": "@g." + top, "InHeightOverride": "@entry.top"})
    s.get("g2", bottom); s.call("b", U_SIZE, "SetHeightOverride", inp={"self": "@g2." + bottom, "InHeightOverride": "@entry.bottom"}); s.chain("entry", "t", "b")
    a = G(); a.get("g", wrap); a.call("a", U_VBOX, "AddChildToVerticalBox", inp={"self": "@g." + wrap, "Content": "@entry.widget"}); a.chain("entry", "a")
    c = G(); c.get("g", wrap); c.call("c", U_PANELW, "ClearChildren", inp={"self": "@g." + wrap}); c.chain("entry", "c")
    y = G(); y.get("g", scroll); y.call("o", U_SCROLL, "GetScrollOffset", inp={"self": "@g." + scroll}); y.call("n", K_MATH, "Add_FloatFloat", inp={"A": "@o.ReturnValue", "B": "@entry.delta"})
    y.call("n0", K_MATH, "FMax", inp={"A": "@n.ReturnValue", "B": "0.0"}); y.get("g2", scroll); y.call("s", U_SCROLL, "SetScrollOffset", inp={"self": "@g2." + scroll, "NewScrollOffset": "@n0.ReturnValue"}); y.chain("entry", "s")
    return [fn(L + " Scroll By", [param("delta", "float")], graph=y), fn(L + " View", outputs=[param("top", "float"), param("bottom", "float"), param("width", "float")], graph=v),
            fn(L + " Spacers", [param("top", "float"), param("bottom", "float")], graph=s),
            fn(L + " Add", [param("widget", "object:" + E_WIDGET)], graph=a), fn(L + " Clear", graph=c)]


def tile_size_graph(box="Box"):
    """Set Tile Size(width, height) of a virtual-list widget: the SizeBox overrides; 0 or less keeps that side as it is."""
    g = G(); g.call("pw", K_MATH, "Greater_FloatFloat", inp={"A": "@entry.width", "B": "0.0"}); g.branch("bw", "@pw.ReturnValue")
    g.get("g1", box); g.call("sw", U_SIZE, "SetWidthOverride", inp={"self": "@g1." + box, "InWidthOverride": "@entry.width"})
    g.call("ph", K_MATH, "Greater_FloatFloat", inp={"A": "@entry.height", "B": "0.0"}); g.branch("bh", "@ph.ReturnValue")
    g.get("g2", box); g.call("sh", U_SIZE, "SetHeightOverride", inp={"self": "@g2." + box, "InHeightOverride": "@entry.height"})
    g.chain("entry", "bw", "sw", "bh", "sh"); g.chain("bw:else", "bh"); return g


W_LISTHEAD = M + "/W_ListHead"


def w_list_head():
    """Heading row of a virtual list (vlist.py): full width (Set Tile Size), the text in the heading or the dim text colour."""
    tree = w(U_SIZE, "Box", props={"bOverride_HeightOverride": True, "HeightOverride": sz(30)}, children=[
        text("Label", "", 13, slot={"VerticalAlignment": "VAlign_Bottom", "Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(4)})])
    g = G(); g.get("gl", "Label"); g.call("st", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@entry.text"})
    g.call("col", K_MATH, "SelectColor", inp={"A": mcol(g, "cd", "ColTextDim"), "B": mcol(g, "ch", "ColHead"), "bPickA": "@entry.dim"})
    tail = ["entry", "st"]; text_color(g, "tc", "Label", "@col.ReturnValue", tail); g.chain(*tail)
    return blueprint(W_LISTHEAD, E_USERWIDGET, variables=[var("Manager", "object:" + MGR)],
                     functions=[fn("Init", [param("text", "text"), param("dim", "bool")], graph=g),
                                fn("Set Tile Size", [param("width", "float"), param("height", "float")], graph=tile_size_graph())], widget_tree=tree)


def w_outfit_button():
    def icon(i): return fit_image("Icon%d" % i, 46, 46, hidden=True, slot={"Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(1), sz(1), sz(1), sz(1))})
    tree = sizebox("Box", 160, None, [   # cols x 48 icons + 2 x (frame 1 + fill 4 + TILE_SIDE 3); set in Init
        roundbox("Frame", COL_FRAME, 1, props={"Clipping": "ClipToBounds"}, children=[
            roundbox("Fill", COL_FILL, TILE_PAD, props={"Padding": TILE_FILL_PAD}, children=[
                w(U_VBOX, "VB", children=[
                    *[w(U_HBOX, "Row%d" % r, slot={"HorizontalAlignment": "HAlign_Center"}, children=[icon(r * OUTFIT_MAX + c) for c in range(OUTFIT_MAX)]) for r in range(OUTFIT_MAX)],
                    sizebox("PlusBox", 144, 144, [
                        text("Plus", "+", 44, WHITE, center=True, slot={"VerticalAlignment": "VAlign_Center", "HorizontalAlignment": "HAlign_Fill"})],
                            slot={"HorizontalAlignment": "HAlign_Center"}),
                    text("Label", "Outfit", 11, WHITE, wrap=True, center=True, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(E_EDIT, "NameEdit", props={"Visibility": "Collapsed", "SelectAllTextWhenFocused": True, "ClearKeyboardFocusOnCommit": False,   # otherwise focus is lost on the Enter key-down -> Tick ends editing before the Enter key-up
                                                "WidgetStyle": "(Font=(Size=%d),Padding=(Left=%d,Top=%d,Right=%d,Bottom=%d),BackgroundColor=(SpecifiedColor=(R=0.1,G=0.1,B=0.12,A=1)),ForegroundColor=(SpecifiedColor=(R=1,G=1,B=1,A=1)))" % (sz(11), sz(4), sz(2), sz(4), sz(2))},
                      slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                ])])])])
    tree = with_split(tree)
    hv, hf, eg = hover_parts(W_OUTFIT, "Frame", "Fill", image=True)
    g = G(); tail = ["entry"]; reset_rename(g, tail, "Label")
    # sizes: icons by the caller's scale; the tile as wide as cols icons, the "+" box cols x rows icons
    tile_scale(g, tail, [("Icon%dBox" % i, 46, 46) for i in range(OUTFIT_ICONS)], "@entry.scale")
    g.call("colf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@entry.cols"}); g.call("rowf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@entry.rows"})
    g.call("bw0", K_MATH, "Multiply_FloatFloat", inp={"A": "@colf.ReturnValue", "B": str(float(sz(48)))}); g.call("bw1", K_MATH, "Add_FloatFloat", inp={"A": "@bw0.ReturnValue", "B": str(float(sz(16)))})
    g.call("bw", K_MATH, "Multiply_FloatFloat", inp={"A": "@bw1.ReturnValue", "B": "@entry.scale"}); g.get("gbx", "Box"); g.call("sbw", U_SIZE, "SetWidthOverride", inp={"self": "@gbx.Box", "InWidthOverride": "@bw.ReturnValue"})
    g.call("pw0", K_MATH, "Multiply_FloatFloat", inp={"A": "@bw0.ReturnValue", "B": "@entry.scale"}); g.get("gpbx", "PlusBox"); g.call("spw", U_SIZE, "SetWidthOverride", inp={"self": "@gpbx.PlusBox", "InWidthOverride": "@pw0.ReturnValue"})
    g.call("ph0", K_MATH, "Multiply_FloatFloat", inp={"A": "@rowf.ReturnValue", "B": str(float(sz(48)))}); g.call("ph", K_MATH, "Multiply_FloatFloat", inp={"A": "@ph0.ReturnValue", "B": "@entry.scale"})
    g.get("gpbx2", "PlusBox"); g.call("sph", U_SIZE, "SetHeightOverride", inp={"self": "@gpbx2.PlusBox", "InHeightOverride": "@ph.ReturnValue"})
    tail += ["sbw", "spw", "sph"]
    g.set("si", "Index", inp={"Index": "@entry.index"}); tail.append("si")
    g.call("neg", K_MATH, "Less_IntInt", inp={"A": "@entry.index", "B": "0"})
    # visibility: the "+" tile shows only the plus (rows hidden below, in the icon pass), otherwise no plus
    for wn, when_add in (("PlusBox", "Visible"),):
        other = "Visible" if when_add == "Collapsed" else "Collapsed"
        g.get("g" + wn, wn); g.call("v" + wn, E_WIDGET, "SetVisibility", inp={"self": "@g%s.%s" % (wn, wn), "InVisibility": when_add})
        g.get("h" + wn, wn); g.call("c" + wn, E_WIDGET, "SetVisibility", inp={"self": "@h%s.%s" % (wn, wn), "InVisibility": other})
    g.branch("badd", "@neg.ReturnValue"); tail.append("badd")
    # label
    g.call("i1", K_MATH, "Add_IntInt", inp={"A": "@entry.index", "B": "1"}); g.call("is", K_STR, "Conv_IntToString", inp={"InInt": "@i1.ReturnValue"})
    g.call("cs", K_STR, "Conv_IntToString", inp={"InInt": "@entry.count"})
    g.call("l0", K_STR, "Concat_StrStr", inp={"A": mts(g, "lo", "Lbl_Outfit"), "B": " "})
    g.call("l1", K_STR, "Concat_StrStr", inp={"A": "@l0.ReturnValue", "B": "@is.ReturnValue"})
    g.call("ct", K_TXT, "Conv_TextToString", inp={"InText": "@entry.caption"}); g.call("ce", K_TXT, "TextIsEmpty", inp={"InText": "@entry.caption"})
    g.call("head", K_MATH, "SelectString", inp={"A": "@l1.ReturnValue", "B": "@ct.ReturnValue", "bPickA": "@ce.ReturnValue"})   # "Outfit N" or the assigned name
    g.call("l2", K_STR, "Concat_StrStr", inp={"A": "@head.ReturnValue", "B": " \u00b7 "})
    g.call("l3", K_STR, "Concat_StrStr", inp={"A": "@l2.ReturnValue", "B": "@cs.ReturnValue"}); g.call("l3b", K_STR, "Concat_StrStr", inp={"A": "@l3.ReturnValue", "B": " "})
    g.call("l4", K_STR, "Concat_StrStr", inp={"A": "@l3b.ReturnValue", "B": mts(g, "lpc", "Lbl_Pieces")})
    # "+" tile: the caller's caption (presets page: "Save current appearance"), default "Save current outfit"
    g.call("sadd", K_MATH, "SelectString", inp={"A": mts(g, "sso", "Btn_SaveOutfit"), "B": "@ct.ReturnValue", "bPickA": "@ce.ReturnValue"})
    g.call("ls", K_MATH, "SelectString", inp={"A": "@sadd.ReturnValue", "B": "@l4.ReturnValue", "bPickA": "@neg.ReturnValue"})
    g.call("lt", K_TXT, "Conv_StringToText", inp={"InString": "@ls.ReturnValue"})
    g.get("gl", "Label"); g.call("stl", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@lt.ReturnValue"})
    # rows: the first `rows` shown (none on the "+" tile); icon (r, c): its box only for c < cols, picture r * cols + c of the icons
    # when there is one (hidden otherwise, the grid keeps its shape)
    g.call("nadd", K_MATH, "Not_PreBool", inp={"A": "@neg.ReturnValue"})
    for r in range(OUTFIT_MAX):
        g.call("rin%d" % r, K_MATH, "Greater_IntInt", inp={"A": "@entry.rows", "B": str(r)}); g.call("ron%d" % r, K_MATH, "BooleanAND", inp={"A": "@rin%d.ReturnValue" % r, "B": "@nadd.ReturnValue"})
        g.branch("br%d" % r, "@ron%d.ReturnValue" % r)
        g.get("grv%d" % r, "Row%d" % r); g.call("rv%d" % r, E_WIDGET, "SetVisibility", inp={"self": "@grv%d.Row%d" % (r, r), "InVisibility": "Visible"})
        g.get("grc%d" % r, "Row%d" % r); g.call("rc%d" % r, E_WIDGET, "SetVisibility", inp={"self": "@grc%d.Row%d" % (r, r), "InVisibility": "Collapsed"})
    for c in range(OUTFIT_MAX):
        g.call("cin%d" % c, K_MATH, "Greater_IntInt", inp={"A": "@entry.cols", "B": str(c)})
    for i in range(OUTFIT_ICONS):
        r, c = divmod(i, OUTFIT_MAX)
        g.branch("bc%d" % i, "@cin%d.ReturnValue" % c)
        g.get("gbv%d" % i, "Icon%dBox" % i); g.call("bv%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@gbv%d.Icon%dBox" % (i, i), "InVisibility": "Visible"})
        g.get("gbc%d" % i, "Icon%dBox" % i); g.call("bcl%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@gbc%d.Icon%dBox" % (i, i), "InVisibility": "Collapsed"})
        g.call("ix%d" % i, K_MATH, "Multiply_IntInt", inp={"A": str(r), "B": "@entry.cols"}); g.call("ixc%d" % i, K_MATH, "Add_IntInt", inp={"A": "@ix%d.ReturnValue" % i, "B": str(c)})
        g.call("vi%d" % i, K_ARR, "Array_IsValidIndex", inp={"TargetArray": "@entry.icons", "IndexToTest": "@ixc%d.ReturnValue" % i}); g.branch("bi%d" % i, "@vi%d.ReturnValue" % i)
        g.call("gt%d" % i, K_ARR, "Array_Get", inp={"TargetArray": "@entry.icons", "Index": "@ixc%d.ReturnValue" % i})
        g.get("gi%d" % i, "Icon%d" % i); g.call("sb%d" % i, E_IMAGE, "SetBrushFromTexture", inp={"self": "@gi%d.Icon%d" % (i, i), "Texture": "@gt%d.Item" % i, "bMatchSize": "true"})
        g.get("gv%d" % i, "Icon%d" % i); g.call("sv%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@gv%d.Icon%d" % (i, i), "InVisibility": "Visible"})
        g.get("gh%d" % i, "Icon%d" % i); g.call("sh%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@gh%d.Icon%d" % (i, i), "InVisibility": "Hidden"})
    g.n("cc", "call_self", function="Compute Colors"); g.n("ap", "call_self", function="Apply Colors", inp={"hover": "false"})
    # the presets' "+" tile (photo) is split in two photo modes; the outfits' one (no photo) keeps the plain plus
    g.get("gpv", "Plus"); g.call("vpls", E_WIDGET, "SetVisibility", inp={"self": "@gpv.Plus", "InVisibility": "Visible"})
    s_on, s_on_ends = split_init(g, "spn", "@entry.photo", "Btn_SavePresetFront", "Btn_SavePresetView")   # only the presets' "+" is a photo tile
    s_off, s_off_ends = split_init(g, "spf", "false")
    # the presets' "+" stands among preset tiles (W_ClothesButton, 104 wide, 88 picture): as wide as they are, and the hidden
    # plus box no taller than their picture, so the row keeps its height
    g.call("pbw", K_MATH, "Multiply_FloatFloat", inp={"A": str(float(sz(104))), "B": "@entry.scale"}); g.call("ppw", K_MATH, "Multiply_FloatFloat", inp={"A": str(float(sz(88))), "B": "@entry.scale"})
    g.get("pgb", "Box"); g.call("pbx", U_SIZE, "SetWidthOverride", inp={"self": "@pgb.Box", "InWidthOverride": "@pbw.ReturnValue"})
    g.get("pgp", "PlusBox"); g.call("ppx", U_SIZE, "SetWidthOverride", inp={"self": "@pgp.PlusBox", "InWidthOverride": "@ppw.ReturnValue"})
    g.get("pgp2", "PlusBox"); g.call("ppy", U_SIZE, "SetHeightOverride", inp={"self": "@pgp2.PlusBox", "InHeightOverride": "@ppw.ReturnValue"})
    g.branch("bph", "@entry.photo")
    g.chain(*tail); g.chain("badd", "vPlusBox", "vpls", "bph", "pbx", "ppx", "ppy", s_on); g.chain("bph:else", s_on); g.chain("badd:else", "cPlusBox", s_off)
    for e in s_on_ends + s_off_ends: g.chain(e, "stl")
    prev = ["stl"]
    for r in range(OUTFIT_MAX):
        for p_ in prev: g.chain(p_, "br%d" % r)
        g.chain("br%d" % r, "rv%d" % r); g.chain("br%d:else" % r, "rc%d" % r); prev = ["rv%d" % r, "rc%d" % r]
    for i in range(OUTFIT_ICONS):
        for p_ in prev: g.chain(p_, "bc%d" % i)
        g.chain("bc%d" % i, "bv%d" % i, "bi%d" % i); g.chain("bc%d:else" % i, "bcl%d" % i)
        g.chain("bi%d" % i, "sb%d" % i, "sv%d" % i); g.chain("bi%d:else" % i, "sh%d" % i)
        prev = ["sv%d" % i, "sh%d" % i, "bcl%d" % i]
    for p_ in prev: g.chain(p_, "cc")
    g.chain("cc", "ap")
    init = fn("Init", [param("index", "int"), param("icons", "object:" + E_TEX2D, "array"), param("count", "int"), param("caption", "text"), param("photo", "bool"),
                       param("scale", "float"), param("cols", "int"), param("rows", "int")], graph=g)
    # rename: label -> text field (Begin Rename), and back (End Rename)
    br = G(); br.set("se", "Editing", inp={"Editing": "true"})
    br.call("txt", K_TXT, "Conv_StringToText", inp={"InString": "@entry.current"})
    br.get("ge", "NameEdit"); br.call("stx", E_EDIT, "SetText", inp={"self": "@ge.NameEdit", "InText": "@txt.ReturnValue"})
    br.get("gl", "Label"); br.call("hl", E_WIDGET, "SetVisibility", inp={"self": "@gl.Label", "InVisibility": "Collapsed"})
    br.get("ge2", "NameEdit"); br.call("sv", E_WIDGET, "SetVisibility", inp={"self": "@ge2.NameEdit", "InVisibility": "Visible"})
    br.get("ge3", "NameEdit"); br.call("kf", E_WIDGET, "SetKeyboardFocus", inp={"self": "@ge3.NameEdit"})
    br.chain("entry", "se", "stx", "hl", "sv", "kf")
    er = G(); er.set("se", "Editing", inp={"Editing": "false"})
    er.get("ge", "NameEdit"); er.call("hv", E_WIDGET, "SetVisibility", inp={"self": "@ge.NameEdit", "InVisibility": "Collapsed"})
    er.get("gl", "Label"); er.call("sl", E_WIDGET, "SetVisibility", inp={"self": "@gl.Label", "InVisibility": "Visible"})
    er.get("gm", "Manager"); er.call("kf", MGR, "Focus Panel", inp={"self": "@gm.Manager"})   # typing goes nowhere else
    er.chain("entry", "se", "hv", "sl", "kf")
    # OnKeyUp: only responsible while editing (key-ups bubble up from the text field; BPGen cannot bind OnTextCommitted).
    # Enter -> Manager.Set Outfit Name, Esc -> cancel; always Handled while editing (the panel never sees Esc or the panel key), otherwise Unhandled
    ku = G(); ku.get("ged", "Editing"); ku.branch("be", "@ged.Editing")
    ku.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"})
    ku.call("ent", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Enter"}); ku.branch("ben", "@ent.ReturnValue")
    ku.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Escape"}); ku.branch("bes", "@esc.ReturnValue")
    ku.get("ge", "NameEdit"); ku.call("gt", E_EDIT, "GetText", inp={"self": "@ge.NameEdit"}); ku.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@gt.ReturnValue"})
    ku.get("gm", "Manager"); ku.get("gi", "Index"); ku.call("sn", MGR, "Set Outfit Name", inp={"self": "@gm.Manager", "index": "@gi.Index", "name": "@t2s.ReturnValue"})
    ku.n("er", "call_self", function="End Rename"); ku.n("er_e", "call_self", function="End Rename")   # Enter: close the field first (a tile of a virtual list stays)
    ku.call("h", K_WBL, "Handled"); ku.link("h.ReturnValue", "return.ReturnValue")
    ku.n("r2", "return_new"); ku.call("u", K_WBL, "Unhandled"); ku.link("u.ReturnValue", "r2.ReturnValue")
    ku.chain("entry", "be", "ben", "er_e", "sn", "return"); ku.chain("ben:else", "bes", "er", "return"); ku.chain("bes:else", "return"); ku.chain("be:else", "r2")
    # Tick: focus lost while renaming (click elsewhere) -> cancel (BPGen cannot bind OnTextCommitted)
    tk = rename_tick(split=True)
    return blueprint(W_OUTFIT, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Index", "int"), var("Editing", "bool"), var("SplitTile", "bool")] + hv,
                     functions=[init, tile_colors(("Label", "ColText"), ("Plus", "ColText"), ("SplitFront", "ColText"), ("SplitView", "ColText")),
                                mouse_down_override("On Outfit Clicked", "On Outfit Context", "Index", pin="index", split=True),
                                fn("Set Tile Size", [param("width", "float"), param("height", "float")], graph=tile_size_graph()),   # virtual outfit list: every tile as high as a row
                                fn("Begin Rename", [param("current", "string")], graph=br), fn("End Rename", graph=er),
                                fn("OnKeyUp", override=True, graph=ku), fn("Tick", override=True, graph=tk)] + hf, event_graph=eg, widget_tree=tree, defaults=HAND)


# ---------------- W_LookButton (portrait photo + name; index -1 = "+ save"; inline rename like W_OutfitButton) ----------------
RAG_LABEL_H, RAG_LINKS_H = 30, 44   # Ragdolls tiles: caption 2 lines, variant links 2 lines (Squirter: blue red yellow did not fit one) - fixed, so every tile of a row is equally high


def w_look_button(path=W_LOOK, clicked="On Look Clicked", context="On Look Context", rename="Set Look Name", add_key="Btn_SaveLook", box=(104, 236), photo=(88, 176), scale_fn=None, links=False):
    """Tile with a photo and a renameable caption; the "+" tile (index < 0) saves. Looks (portrait photo) and saved faces
    (W_FaceButton: square photo, face functions) share it."""
    tree = sizebox("Box", box[0], None, [   # photo + 2 x (frame 1 + fill 4 + TILE_SIDE 3); height from the content
        roundbox("Frame", COL_FRAME, 1, props={"Clipping": "ClipToBounds"}, children=[
            roundbox("Fill", COL_FILL, TILE_PAD, props={"Padding": TILE_FILL_PAD}, children=[
                w(U_VBOX, "VB", children=[
                    sizebox("PhotoBox", photo[0], photo[1], [w(U_OVERLAY, "PhotoOv", children=[
                        w(E_IMAGE, "Photo", props={"Visibility": "Collapsed"}, slot={"HorizontalAlignment": "HAlign_Fill", "VerticalAlignment": "VAlign_Fill"}),
                        text("NoPhoto", "", 10, GREY, center=True, slot={"HorizontalAlignment": "HAlign_Center", "VerticalAlignment": "VAlign_Center"}),
                        text("Plus", "+", 44, WHITE, center=True, slot={"HorizontalAlignment": "HAlign_Center", "VerticalAlignment": "VAlign_Center"})])],
                            slot={"HorizontalAlignment": "HAlign_Center"}),
                    *([w(U_SIZE, "LabelBox", props={"bOverride_HeightOverride": True, "HeightOverride": sz(RAG_LABEL_H)}, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)},
                         children=[text("Label", "Look", 11, WHITE, wrap=True, center=True, slot={"VerticalAlignment": "VAlign_Center"})]),
                       w(U_SIZE, "VarsBox", props={"bOverride_HeightOverride": True, "HeightOverride": sz(RAG_LINKS_H)},
                         children=[w(U_VBOX, "VarsV", slot={"HorizontalAlignment": "HAlign_Fill", "VerticalAlignment": "VAlign_Center"}, children=[
                             w(U_HBOX, "Vars", slot={"HorizontalAlignment": "HAlign_Center"}), w(U_HBOX, "Vars2", slot={"HorizontalAlignment": "HAlign_Center"})])])] if links else
                      [text("Label", "Look", 11, WHITE, wrap=True, center=True, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)})]),
                    w(E_EDIT, "NameEdit", props={"Visibility": "Collapsed", "SelectAllTextWhenFocused": True, "ClearKeyboardFocusOnCommit": False,
                                                "WidgetStyle": "(Font=(Size=%d),Padding=(Left=%d,Top=%d,Right=%d,Bottom=%d),BackgroundColor=(SpecifiedColor=(R=0.1,G=0.1,B=0.12,A=1)),ForegroundColor=(SpecifiedColor=(R=1,G=1,B=1,A=1)))" % (sz(11), sz(4), sz(2), sz(4), sz(2))},
                      slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                ])])])])
    tree = with_split(tree)
    hv, hf, eg = hover_parts(path, "Frame", "Fill", image=True)
    g = G(); tail = ["entry"]
    scale_pin = None
    if scale_fn:   # Looks: a size of their own (Options > Tiles)
        g.get("lsm", "Manager"); g.call("lsv", MGR, scale_fn, inp={"self": "@lsm.Manager"}); scale_pin = "@lsv.scale"
    tile_scale(g, tail, [("Box", box[0], None), ("PhotoBox", photo[0], photo[1])], scale_pin)
    g.set("si", "Index", inp={"Index": "@entry.index"}); tail.append("si")
    g.call("neg", K_MATH, "Less_IntInt", inp={"A": "@entry.index", "B": "0"}); g.branch("badd", "@neg.ReturnValue"); tail.append("badd")
    # "+" tile: plus only; look tile: photo (or "no photo" text) + name
    g.get("gpl", "Plus"); g.call("vpl", E_WIDGET, "SetVisibility", inp={"self": "@gpl.Plus", "InVisibility": "Visible"})
    g.get("gph", "Photo"); g.call("cph", E_WIDGET, "SetVisibility", inp={"self": "@gph.Photo", "InVisibility": "Collapsed"})
    g.get("gnp", "NoPhoto"); g.call("cnp", E_WIDGET, "SetVisibility", inp={"self": "@gnp.NoPhoto", "InVisibility": "Collapsed"})
    g.get("gl1", "Label"); g.call("sl1", E_TEXT, "SetText", inp={"self": "@gl1.Label", "InText": mt(g, "mtsv", add_key)})
    g.get("gpl2", "Plus"); g.call("cpl", E_WIDGET, "SetVisibility", inp={"self": "@gpl2.Plus", "InVisibility": "Collapsed"})
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@entry.icon"}); g.branch("biv", "@iv.ReturnValue")
    g.get("gph2", "Photo"); g.call("sb", E_IMAGE, "SetBrushFromTexture", inp={"self": "@gph2.Photo", "Texture": "@entry.icon", "bMatchSize": "false"})
    g.get("gph3", "Photo"); g.call("vph", E_WIDGET, "SetVisibility", inp={"self": "@gph3.Photo", "InVisibility": "Visible"})
    g.get("gnp2", "NoPhoto"); g.call("cnp2", E_WIDGET, "SetVisibility", inp={"self": "@gnp2.NoPhoto", "InVisibility": "Collapsed"})
    g.get("gnp3", "NoPhoto"); g.call("snp", E_TEXT, "SetText", inp={"self": "@gnp3.NoPhoto", "InText": mt(g, "mtnp", "Lbl_NoPhoto")})
    g.get("gnp4", "NoPhoto"); g.call("vnp", E_WIDGET, "SetVisibility", inp={"self": "@gnp4.NoPhoto", "InVisibility": "Visible"})
    g.get("gph4", "Photo"); g.call("cph2", E_WIDGET, "SetVisibility", inp={"self": "@gph4.Photo", "InVisibility": "Collapsed"})
    g.get("gl2", "Label"); g.call("sl2", E_TEXT, "SetText", inp={"self": "@gl2.Label", "InText": "@entry.caption"})
    g.n("cc", "call_self", function="Compute Colors"); g.n("ap", "call_self", function="Apply Colors", inp={"hover": "false"})
    s_on, s_on_ends = split_init(g, "spn", "true", add_key + "Front", add_key + "View"); s_off, s_off_ends = split_init(g, "spf", "false")
    g.chain(*tail); g.chain("badd", "vpl", "cph", "cnp", "sl1", s_on); g.chain("badd:else", "cpl", "biv", "sb", "vph", "cnp2", "sl2"); g.chain("biv:else", "snp", "vnp", "cph2", "sl2")
    g.chain("sl2", s_off)
    for e in s_on_ends + s_off_ends: g.chain(e, "cc")
    g.chain("cc", "ap")
    init = fn("Init", [param("index", "int"), param("icon", "object:" + E_TEX2D), param("caption", "text")], graph=g)
    # rename: label -> text field (Begin Rename), and back (End Rename); keys via OnKeyUp, focus loss via Tick (see W_OutfitButton)
    br = G(); br.set("se", "Editing", inp={"Editing": "true"})
    br.call("txt", K_TXT, "Conv_StringToText", inp={"InString": "@entry.current"})
    br.get("ge", "NameEdit"); br.call("stx", E_EDIT, "SetText", inp={"self": "@ge.NameEdit", "InText": "@txt.ReturnValue"})
    br.get("gl", "Label"); br.call("hl", E_WIDGET, "SetVisibility", inp={"self": "@gl.Label", "InVisibility": "Collapsed"})
    br.get("ge2", "NameEdit"); br.call("sv", E_WIDGET, "SetVisibility", inp={"self": "@ge2.NameEdit", "InVisibility": "Visible"})
    br.get("ge3", "NameEdit"); br.call("kf", E_WIDGET, "SetKeyboardFocus", inp={"self": "@ge3.NameEdit"})
    br.chain("entry", "se", "stx", "hl", "sv", "kf")
    er = G(); er.set("se", "Editing", inp={"Editing": "false"})
    er.get("ge", "NameEdit"); er.call("hv", E_WIDGET, "SetVisibility", inp={"self": "@ge.NameEdit", "InVisibility": "Collapsed"})
    er.get("gl", "Label"); er.call("sl", E_WIDGET, "SetVisibility", inp={"self": "@gl.Label", "InVisibility": "Visible"})
    er.get("gm", "Manager"); er.call("kf", MGR, "Focus Panel", inp={"self": "@gm.Manager"})   # typing goes nowhere else
    er.chain("entry", "se", "hv", "sl", "kf")
    ku = G(); ku.get("ged", "Editing"); ku.branch("be", "@ged.Editing")
    ku.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"})
    ku.call("ent", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Enter"}); ku.branch("ben", "@ent.ReturnValue")
    ku.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Escape"}); ku.branch("bes", "@esc.ReturnValue")
    ku.get("ge", "NameEdit"); ku.call("gt", E_EDIT, "GetText", inp={"self": "@ge.NameEdit"}); ku.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@gt.ReturnValue"})
    ku.get("gm", "Manager"); ku.get("gi", "Index"); ku.call("sn", MGR, rename, inp={"self": "@gm.Manager", "index": "@gi.Index", "name": "@t2s.ReturnValue"})
    ku.n("er", "call_self", function="End Rename"); ku.n("er_e", "call_self", function="End Rename")   # Enter: close the field first (a tile of a virtual list stays)
    ku.call("h", K_WBL, "Handled"); ku.link("h.ReturnValue", "return.ReturnValue")
    ku.n("r2", "return_new"); ku.call("u", K_WBL, "Unhandled"); ku.link("u.ReturnValue", "r2.ReturnValue")
    ku.chain("entry", "be", "ben", "er_e", "sn", "return"); ku.chain("ben:else", "bes", "er", "return"); ku.chain("bes:else", "return"); ku.chain("be:else", "r2")
    tk = rename_tick(split=True, pre="Fit Vars" if links else None)
    return blueprint(path, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Index", "int"), var("Editing", "bool"), var("SplitTile", "bool")] + hv
                     + ([var("VarsAll", "object:" + E_WIDGET, "array"), var("VarsMoved", "int"), var("VarsPending", "bool")] if links else []),
                     functions=[init, tile_colors(("Label", "ColText"), ("Plus", "ColText"), ("NoPhoto", "ColTextDim"), ("SplitFront", "ColText"), ("SplitView", "ColText")),
                                mouse_down_override(clicked, context, "Index", pin="index", split=True),
                                fn("Begin Rename", [param("current", "string")], graph=br), fn("End Rename", graph=er),
                                fn("OnKeyUp", override=True, graph=ku), fn("Tick", override=True, graph=tk)] + hf + (add_var_fn() if links else []), event_graph=eg, widget_tree=tree, defaults=HAND)


def add_var_fn():
    """Ragdolls tile: a variant link under the caption (its own click handling keeps the tile's click away). The links stand
    centred in one line; Fit Vars (Tick) moves the last ones into a second centred line while the first is wider than the
    tile (Squirter: blue red yellow; German, Polish: two already). 4.27's WrapBox wraps, but cannot centre its lines."""
    av = G(); av.get("ga", "VarsAll"); av.call("aa", K_ARR, "Array_Add", inp={"TargetArray": "@ga.VarsAll", "NewItem": "@entry.widget"})
    av.set("sp", "VarsPending", inp={"VarsPending": "true"}); av.n("rd", "call_self", function="Lay Out Vars"); av.chain("entry", "aa", "sp", "rd")
    lo = G()
    for i, box in enumerate(("Vars", "Vars2")): lo.get("gb%d" % i, box); lo.call("cl%d" % i, U_PANELW, "ClearChildren", inp={"self": "@gb%d.%s" % (i, box)})
    lo.get("ga", "VarsAll"); lo.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@ga.VarsAll"}); lo.get("gm", "VarsMoved")
    lo.call("cut", K_MATH, "Subtract_IntInt", inp={"A": "@len.ReturnValue", "B": "@gm.VarsMoved"})
    lo.get("ga2", "VarsAll"); lo.foreach("fe", "@ga2.VarsAll")
    lo.call("one", K_MATH, "Less_IntInt", inp={"A": "@fe.Array Index", "B": "@cut.ReturnValue"}); lo.branch("b", "@one.ReturnValue")
    pad = "(Left=%d,Top=0,Right=%d,Bottom=0)" % (sz(3), sz(3))
    for i, box in enumerate(("Vars", "Vars2")):
        lo.get("gv%d" % i, box); lo.call("a%d" % i, U_HBOX, "AddChildToHorizontalBox", inp={"self": "@gv%d.%s" % (i, box), "Content": "@fe.Array Element"})
        lo.call("pd%d" % i, "/Script/UMG.HorizontalBoxSlot", "SetPadding", inp={"self": "@a%d.ReturnValue" % i, "InPadding": pad})
    lo.chain("entry", "cl0", "cl1", "fe"); lo.chain("fe", "b", "a0", "pd0"); lo.chain("b:else", "a1", "pd1")
    fv = G(); fv.get("gp", "VarsPending"); fv.branch("bp", "@gp.VarsPending")
    fv.get("gbx", "VarsBox"); fv.call("geo", E_WIDGET, "GetCachedGeometry", inp={"self": "@gbx.VarsBox"}); fv.call("ls", K_SLATE, "GetLocalSize", inp={"Geometry": "@geo.ReturnValue"})
    fv.call("bl", K_MATH, "BreakVector2D", inp={"InVec": "@ls.ReturnValue"}); fv.call("laid", K_MATH, "Greater_FloatFloat", inp={"A": "@bl.X", "B": "1.0"}); fv.branch("bl2", "@laid.ReturnValue")
    fv.get("gv", "Vars"); fv.call("fl", E_WIDGET, "ForceLayoutPrepass", inp={"self": "@gv.Vars"}); fv.call("ds", E_WIDGET, "GetDesiredSize", inp={"self": "@gv.Vars"})
    fv.call("bd", K_MATH, "BreakVector2D", inp={"InVec": "@ds.ReturnValue"}); fv.call("wide", K_MATH, "Greater_FloatFloat", inp={"A": "@bd.X", "B": "@bl.X"})
    fv.get("ga", "VarsAll"); fv.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@ga.VarsAll"}); fv.get("gm", "VarsMoved")
    fv.call("left", K_MATH, "Subtract_IntInt", inp={"A": "@len.ReturnValue", "B": "@gm.VarsMoved"}); fv.call("more", K_MATH, "Greater_IntInt", inp={"A": "@left.ReturnValue", "B": "1"})
    fv.call("go", K_MATH, "BooleanAND", inp={"A": "@wide.ReturnValue", "B": "@more.ReturnValue"}); fv.branch("bgo", "@go.ReturnValue")
    fv.get("gm2", "VarsMoved"); fv.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gm2.VarsMoved", "B": "1"}); fv.set("sm", "VarsMoved", inp={"VarsMoved": "@inc.ReturnValue"})
    fv.n("rd", "call_self", function="Lay Out Vars"); fv.set("done", "VarsPending", inp={"VarsPending": "false"})
    fv.chain("entry", "bp", "bl2", "fl", "bgo", "sm", "rd"); fv.chain("bgo:else", "done")
    return [fn("Add Var", [param("widget", "object:" + E_WIDGET)], graph=av), fn("Lay Out Vars", graph=lo), fn("Fit Vars", graph=fv)]


# ---------------- W_TextButton (text link: click -> Manager.On Menu Action(action)) ----------------
def w_text_button():
    tree = w(E_BORDER, "Fill", props={"BrushColor": COL_NONE, "Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(6), sz(2), sz(6), sz(2))},
             children=[w(U_HBOX, "HB", children=[
                 w(U_SIZE, "IconBox", props={"bOverride_WidthOverride": True, "WidthOverride": sz(20), "bOverride_HeightOverride": True, "HeightOverride": sz(20), "Visibility": "Collapsed"},
                   slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(5)}, children=[w(E_IMAGE, "Icon", props={"ColorAndOpacity": "(R=0.62,G=0.76,B=1.0,A=1)"})]),
                 # the text takes the rest of the link and is centred in it: an ordinary link is as wide as its text (no change), a link
                 # stretched wider (the quick key) shows its text in the middle - set at design time, like the lamp's key field: in
                 # 4.27 a border's content alignment set at runtime before the widget is built is lost (BorderSlot.cpp)
                 text("Label", "Link", 12, COL_LINK, center=True, slot={"VerticalAlignment": "VAlign_Center", "Size": "(SizeRule=Fill,Value=1)"})])])
    hv, hf, eg = hover_parts(W_TXT, None, "Fill")
    g = G(); tail = ["entry"]
    g.set("sa", "Action", inp={"Action": "@entry.action"}); tail.append("sa")
    g.get("gl", "Label"); g.call("st", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@entry.caption"}); tail.append("st")
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@entry.icon"}); g.branch("bi", "@iv.ReturnValue"); tail.append("bi")
    g.get("gi", "Icon"); g.call("sb", E_IMAGE, "SetBrushFromTexture", inp={"self": "@gi.Icon", "Texture": "@entry.icon", "bMatchSize": "false"})
    g.get("gi2", "Icon"); g.call("sv", E_WIDGET, "SetVisibility", inp={"self": "@gi2.Icon", "InVisibility": "Visible"})
    g.get("gib", "IconBox"); g.call("sbx", E_WIDGET, "SetVisibility", inp={"self": "@gib.IconBox", "InVisibility": "Visible"})
    g.get("gib2", "IconBox"); g.call("cbx", E_WIDGET, "SetVisibility", inp={"self": "@gib2.IconBox", "InVisibility": "Collapsed"})
    g.n("cc", "call_self", function="Compute Colors"); g.n("ap", "call_self", function="Apply Colors", inp={"hover": "false"})
    g.chain(*tail, "sb", "sv", "sbx", "cc"); g.chain("bi:else", "cbx", "cc"); g.chain("cc", "ap")
    c = G(); ctail = ["entry"]; set_colors(c, "Fill", COL_NONE, mcol(c, "clh", "ColLinkHover"), ctail)
    text_color(c, "tl", "Label", mcol(c, "cl", "ColLink"), ctail)
    c.get("gic", "Icon"); c.call("sic", E_IMAGE, "SetColorAndOpacity", inp={"self": "@gic.Icon", "InColorAndOpacity": mcol(c, "cl2", "ColLink")}); ctail.append("sic"); c.chain(*ctail)
    md = G(); md.get("gm0", "Manager"); md.self_("me0"); md.n("slb", "set", var="LastButton", cls=MGR, inp={"self": "@gm0.Manager", "LastButton": "@me0.self"})
    md.get("gm", "Manager"); md.get("ga", "Action")
    md.call("c", MGR, "On Menu Action", inp={"self": "@gm.Manager", "name": "@ga.Action"})
    md.call("h", K_WBL, "Handled"); md.link("h.ReturnValue", "return.ReturnValue"); md.chain("entry", "slb", "c", "return")
    return blueprint(W_TXT, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Action", "name")] + hv,
                     functions=[fn("Init", [param("action", "name"), param("caption", "text"), param("icon", "object:" + E_TEX2D)], graph=g), compute_fn(c), refresh_fn(), fn("OnMouseButtonDown", override=True, graph=md)] + hf,
                     event_graph=eg, widget_tree=tree, defaults=HAND)


# ---------------- W_RoundButton (round button with icon in the Jodi view: click -> Manager.On Menu Action(action)) ----------------
BTN_R = sz(42)   # ~80 px


def w_round_button():
    tree = w(U_SIZE, "Box", props={"bOverride_WidthOverride": True, "WidthOverride": BTN_R, "bOverride_HeightOverride": True, "HeightOverride": BTN_R},
             children=[w(E_IMAGE, "Icon", props={"ColorAndOpacity": "(R=1,G=1,B=1,A=0.75)"})])
    g = G(); g.set("sa", "Action", inp={"Action": "@entry.action"})
    g.get("gi", "Icon"); g.call("sb", E_IMAGE, "SetBrushFromTexture", inp={"self": "@gi.Icon", "Texture": "@entry.icon", "bMatchSize": "false"})
    # tooltip (W_Tooltip like the tiles; empty text -> none)
    g.call("te", K_TXT, "TextIsEmpty", inp={"InText": "@entry.tip"}); g.branch("bt", "@te.ReturnValue")
    g.call("gop", E_USERWIDGET, "GetOwningPlayer"); g.call("ctt", K_WBL, "Create", inp={"WidgetType": W_TOOLTIP, "OwningPlayer": "@gop.ReturnValue"}); g.cast("ctc", W_TOOLTIP, "@ctt.ReturnValue")
    g.get("gmt", "Manager"); g.n("stm", "set", var="Manager", cls=W_TOOLTIP, inp={"self": "@ctc.AsW_Tooltip", "Manager": "@gmt.Manager"})
    g.call("tti", W_TOOLTIP, "Init", inp={"self": "@ctc.AsW_Tooltip", "text": "@entry.tip"}); g.get("gbx", "Box"); g.call("stt", E_WIDGET, "SetToolTip", inp={"self": "@gbx.Box", "Widget": "@ctc.AsW_Tooltip"})
    g.chain("entry", "sa", "sb", "bt"); g.chain("bt:else", "ctt", "stm", "tti", "stt")
    eg = G()
    eg.event("en", E_USERWIDGET, "OnMouseEnter"); eg.get("gi1", "Icon"); eg.call("c1", E_IMAGE, "SetColorAndOpacity", inp={"self": "@gi1.Icon", "InColorAndOpacity": "(R=1,G=1,B=1,A=1)"}); eg.chain("en", "c1")
    eg.event("lv", E_USERWIDGET, "OnMouseLeave"); eg.get("gi2", "Icon"); eg.call("c2", E_IMAGE, "SetColorAndOpacity", inp={"self": "@gi2.Icon", "InColorAndOpacity": "(R=1,G=1,B=1,A=0.75)"}); eg.chain("lv", "c2")
    md = G(); md.get("gm", "Manager"); md.get("ga", "Action")
    md.call("c", MGR, "On Menu Action", inp={"self": "@gm.Manager", "name": "@ga.Action"})
    md.call("h", K_WBL, "Handled"); md.link("h.ReturnValue", "return.ReturnValue"); md.chain("entry", "c", "return")
    return blueprint(W_ROUND, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Action", "name")],
                     functions=[fn("Init", [param("action", "name"), param("icon", "object:" + E_TEX2D), param("tip", "text")], graph=g), fn("OnMouseButtonDown", override=True, graph=md)],
                     event_graph=eg, widget_tree=tree, defaults=HAND)


# ---------------- W_MenuRow / W_ContextMenu ----------------
W_ROW = M + "/W_MenuRow"; W_MENU = M + "/W_ContextMenu"


def w_menu_row():
    tree = w(E_BORDER, "Fill", props={"BrushColor": COL_NONE, "Padding": "(Left=23,Top=11,Right=23,Bottom=11)"}, children=[text("Label", "Aktion", 12)])
    hv, hf, eg = hover_parts(W_ROW, None, "Fill")
    g = G(); tail = ["entry"]
    g.set("sa", "Action", inp={"Action": "@entry.action"}); tail.append("sa")
    g.get("gl", "Label"); g.call("st", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@entry.caption"}); tail.append("st")
    g.n("cc", "call_self", function="Compute Colors"); tail.append("cc")
    g.n("ap", "call_self", function="Apply Colors", inp={"hover": "false"}); tail.append("ap")
    g.chain(*tail)
    c = G(); ctail = ["entry"]; set_colors(c, "Fill", COL_NONE, mcol(c, "cmh", "ColMenuHover"), ctail); text_color(c, "tl", "Label", mcol(c, "ct", "ColText"), ctail); c.chain(*ctail)
    md = G(); md.get("gm", "Manager"); md.get("ga", "Action")
    md.call("c", MGR, "On Menu Action", inp={"self": "@gm.Manager", "name": "@ga.Action"})
    md.call("h", K_WBL, "Handled"); md.link("h.ReturnValue", "return.ReturnValue"); md.chain("entry", "c", "return")
    return blueprint(W_ROW, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Action", "name")] + hv,
                     functions=[fn("Init", [param("action", "name"), param("caption", "text")], graph=g), compute_fn(c), fn("OnMouseButtonDown", override=True, graph=md)] + hf,
                     event_graph=eg, widget_tree=tree, defaults=HAND)



# ---------------- W_MenuSlider (context menu row with a slider: clothes damage 0..100 %; Tick -> Manager.Set Item Damage) ----------------
W_MSLIDER = M + "/W_MenuSlider"


def w_menu_slider():
    tree = w(E_BORDER, "Fill", props={"BrushColor": COL_NONE, "Padding": "(Left=23,Top=11,Right=23,Bottom=11)"}, children=[w(U_HBOX, "HB", children=[
        text("Label", "Damage", 12, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(10)}),
        sizebox("SldBox", 130, 24, [w(E_SLIDER, "Sld", props={"Value": 0.0, "StepSize": 0.01, "SliderBarColor": "(R=0.35,G=0.42,B=0.55,A=1)", "SliderHandleColor": "(R=1,G=1,B=1,A=1)",
                                                                "WidgetStyle": "(BarThickness=5.0)"})], slot={"VerticalAlignment": "VAlign_Center"}),
        sizebox("ValBox", 52, 24, [text("Val", "0 %", 12, GREY, slot={"VerticalAlignment": "VAlign_Center", "HorizontalAlignment": "HAlign_Right"})],
                slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(8)})])])
    ut = G(); ut.get("gl", "Last"); ut.call("x", K_MATH, "Multiply_FloatFloat", inp={"A": "@gl.Last", "B": "100"}); ut.call("r", K_MATH, "Round", inp={"A": "@x.ReturnValue"})
    ut.call("is", K_STR, "Conv_IntToString", inp={"InInt": "@r.ReturnValue"}); ut.call("c", K_STR, "Concat_StrStr", inp={"A": "@is.ReturnValue", "B": " %"})
    ut.call("t", K_TXT, "Conv_StringToText", inp={"InString": "@c.ReturnValue"}); ut.get("gv", "Val"); ut.call("st", E_TEXT, "SetText", inp={"self": "@gv.Val", "InText": "@t.ReturnValue"}); ut.chain("entry", "st")
    g = G(); g.set("si", "Item", inp={"Item": "@entry.item"}); g.set("sl", "Last", inp={"Last": "@entry.value"})
    g.get("gl", "Label"); g.call("stl", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@entry.caption"})
    g.get("gs", "Sld"); g.call("ssv", E_SLIDER, "SetValue", inp={"self": "@gs.Sld", "InValue": "@entry.value"}); g.n("ut", "call_self", function="Update Text")
    g.n("cc", "call_self", function="Compute Colors"); g.chain("entry", "si", "sl", "stl", "ssv", "ut", "cc")
    # Tick: the slider as the player drags it -> the piece (live), the number beside it
    tk = G(); tk.get("gs", "Sld"); tk.call("gv", E_SLIDER, "GetValue", inp={"self": "@gs.Sld"}); tk.get("gl", "Last")
    tk.call("ne", K_MATH, "NotEqual_FloatFloat", inp={"A": "@gv.ReturnValue", "B": "@gl.Last"}); tk.branch("b", "@ne.ReturnValue")
    tk.set("sl", "Last", inp={"Last": "@gv.ReturnValue"}); tk.n("ut", "call_self", function="Update Text")
    tk.get("gm", "Manager"); tk.get("gi", "Item"); tk.get("gl2", "Last"); tk.call("sd", MGR, "Set Item Damage", inp={"self": "@gm.Manager", "name": "@gi.Item", "v": "@gl2.Last"})
    tk.chain("entry", "b", "sl", "ut", "sd")
    c = G(); ctail = ["entry"]; text_color(c, "tl", "Label", mcol(c, "ct", "ColText"), ctail); text_color(c, "tv", "Val", mcol(c, "ctd", "ColTextDim"), ctail)
    c.get("gsl", "Sld"); c.call("sbc", E_SLIDER, "SetSliderBarColor", inp={"self": "@gsl.Sld", "InValue": mcol(c, "csl", "ColSlider")}); ctail.append("sbc"); c.chain(*ctail)
    md = G(); md.call("h", K_WBL, "Handled"); md.link("h.ReturnValue", "return.ReturnValue"); md.chain("entry", "return")   # a click beside the slider stays in the menu
    return blueprint(W_MSLIDER, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Item", "name"), var("Last", "float")],
                     functions=[fn("Init", [param("item", "name"), param("caption", "text"), param("value", "float")], graph=g), fn("Update Text", graph=ut), compute_fn(c),
                                fn("Tick", override=True, graph=tk), fn("OnMouseButtonDown", override=True, graph=md)],
                     widget_tree=tree)

# ---------------- W_MenuAmount (context menu row: slider + number field for a chosen amount of a stack; Manager.Menu Amount Set) ----------------
# docs/specs/2026-10-14-stack-amount-design.md. The slider covers Lo..Hi, the field Lo..FMax (the catalogue's field goes beyond
# the slider). Dragging writes the field, typing moves the slider; every change goes to the manager, which renames the action
# rows ("<action> n"). Enter runs the first action row (First), Esc closes the menu; both and all typing stay here.
W_MAMOUNT = M + "/W_MenuAmount"
AMOUNT_EDIT_W = 64   # x SC


def w_menu_amount():
    tree = w(E_BORDER, "Fill", props={"BrushColor": COL_NONE, "Padding": "(Left=23,Top=11,Right=23,Bottom=11)"}, children=[w(U_HBOX, "HB", children=[
        text("Label", "Amount", 12, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(10)}),
        sizebox("SldBox", 130, 24, [w(E_SLIDER, "Sld", props={"Value": 0.0, "StepSize": 0.001, "SliderBarColor": "(R=0.35,G=0.42,B=0.55,A=1)", "SliderHandleColor": "(R=1,G=1,B=1,A=1)",
                                                                "WidgetStyle": "(BarThickness=5.0)"})], slot={"VerticalAlignment": "VAlign_Center"}),
        w(U_SIZE, "EditBox", props={"bOverride_WidthOverride": True, "WidthOverride": sz(AMOUNT_EDIT_W)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(8)},
          children=[w(E_EDIT, "Edit", props={"SelectAllTextWhenFocused": True, "ClearKeyboardFocusOnCommit": False, "Justification": "Right", "WidgetStyle": EDIT_STYLE})])])])

    def slider_of(g, p, n_pin):
        """n -> slider value (n - Lo) / max(Hi - Lo, 1), 0..1."""
        g.get(p + "lo", "Lo"); g.get(p + "hi", "Hi"); g.call(p + "d", K_MATH, "Subtract_IntInt", inp={"A": n_pin, "B": "@%slo.Lo" % p})
        g.call(p + "r", K_MATH, "Subtract_IntInt", inp={"A": "@%shi.Hi" % p, "B": "@%slo.Lo" % p}); g.call(p + "rm", K_MATH, "Max", inp={"A": "@%sr.ReturnValue" % p, "B": "1"})
        g.call(p + "df", K_MATH, "Conv_IntToFloat", inp={"InInt": "@%sd.ReturnValue" % p}); g.call(p + "rf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@%srm.ReturnValue" % p})
        g.call(p + "q", K_MATH, "Divide_FloatFloat", inp={"A": "@%sdf.ReturnValue" % p, "B": "@%srf.ReturnValue" % p})
        g.call(p + "c", K_MATH, "FClamp", inp={"Value": "@%sq.ReturnValue" % p, "Min": "0", "Max": "1"}); return "@%sc.ReturnValue" % p

    def int_text(g, p, n_pin):
        g.call(p + "s", K_STR, "Conv_IntToString", inp={"InInt": n_pin}); g.call(p + "t", K_TXT, "Conv_StringToText", inp={"InString": "@%ss.ReturnValue" % p}); return "@%st.ReturnValue" % p

    g = G(); g.set("slo", "Lo", inp={"Lo": "@entry.lo"}); g.set("shi", "Hi", inp={"Hi": "@entry.hi"}); g.set("sfm", "FMax", inp={"FMax": "@entry.fmax"}); g.set("sfi", "First", inp={"First": "@entry.first"})
    g.set("sla", "Last", inp={"Last": "@entry.start"})
    g.get("gl", "Label"); g.call("stl", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@entry.caption"})
    v0 = slider_of(g, "v0", "@entry.start"); g.set("slv", "LastV", inp={"LastV": v0}); g.get("gs", "Sld"); g.call("ssv", E_SLIDER, "SetValue", inp={"self": "@gs.Sld", "InValue": v0})
    g.get("ge", "Edit"); g.call("set", E_EDIT, "SetText", inp={"self": "@ge.Edit", "InText": int_text(g, "t0", "@entry.start")})
    g.get("gm", "Manager"); g.call("mas", MGR, "Menu Amount Set", inp={"self": "@gm.Manager", "n": "@entry.start"})
    g.n("cc", "call_self", function="Compute Colors"); g.chain("entry", "slo", "shi", "sfm", "sfi", "sla", "stl", "slv", "ssv", "set", "mas", "cc")
    # Tick: typing (field focused) -> number clamped to Lo..FMax -> slider + manager; else a dragged slider (its value moved away
    # from the one set last) -> number -> field + manager; an unfocused field always shows the number
    tk = G(); tk.get("ge", "Edit"); tk.call("hf", E_WIDGET, "HasKeyboardFocus", inp={"self": "@ge.Edit"}); tk.branch("bf", "@hf.ReturnValue")
    tk.get("ge2", "Edit"); tk.call("gt", E_EDIT, "GetText", inp={"self": "@ge2.Edit"}); tk.call("ts", K_TXT, "Conv_TextToString", inp={"InText": "@gt.ReturnValue"})
    tk.call("ti", K_STR, "Conv_StringToInt", inp={"InString": "@ts.ReturnValue"}); tk.get("glo", "Lo"); tk.get("gfm", "FMax")
    tk.call("tc", K_MATH, "Clamp", inp={"Value": "@ti.ReturnValue", "Min": "@glo.Lo", "Max": "@gfm.FMax"}); tk.get("gla", "Last")
    tk.call("tne", K_MATH, "NotEqual_IntInt", inp={"A": "@tc.ReturnValue", "B": "@gla.Last"}); tk.branch("btn", "@tne.ReturnValue")
    tk.set("tsl", "Last", inp={"Last": "@tc.ReturnValue"}); tv = slider_of(tk, "tv", "@tc.ReturnValue"); tk.set("tlv", "LastV", inp={"LastV": tv})
    tk.get("gs", "Sld"); tk.call("tss", E_SLIDER, "SetValue", inp={"self": "@gs.Sld", "InValue": tv})
    tk.get("gm", "Manager"); tk.call("tms", MGR, "Menu Amount Set", inp={"self": "@gm.Manager", "n": "@tc.ReturnValue"})
    tk.get("gs2", "Sld"); tk.call("sv", E_SLIDER, "GetValue", inp={"self": "@gs2.Sld"}); tk.get("glv", "LastV")
    tk.call("sne", K_MATH, "NotEqual_FloatFloat", inp={"A": "@sv.ReturnValue", "B": "@glv.LastV"}); tk.branch("bsn", "@sne.ReturnValue")
    tk.get("glo2", "Lo"); tk.get("ghi2", "Hi"); tk.call("sr", K_MATH, "Subtract_IntInt", inp={"A": "@ghi2.Hi", "B": "@glo2.Lo"}); tk.call("srf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@sr.ReturnValue"})
    tk.call("sm", K_MATH, "Multiply_FloatFloat", inp={"A": "@sv.ReturnValue", "B": "@srf.ReturnValue"}); tk.call("srd", K_MATH, "Round", inp={"A": "@sm.ReturnValue"})
    tk.call("sn", K_MATH, "Add_IntInt", inp={"A": "@srd.ReturnValue", "B": "@glo2.Lo"})
    tk.set("ssl", "Last", inp={"Last": "@sn.ReturnValue"}); tk.set("ssv", "LastV", inp={"LastV": "@sv.ReturnValue"})
    tk.get("gm2", "Manager"); tk.call("sms", MGR, "Menu Amount Set", inp={"self": "@gm2.Manager", "n": "@sn.ReturnValue"})
    tk.get("ge3", "Edit"); tk.call("cur", E_EDIT, "GetText", inp={"self": "@ge3.Edit"}); tk.call("cs", K_TXT, "Conv_TextToString", inp={"InText": "@cur.ReturnValue"})
    tk.get("gla2", "Last"); tk.call("ls", K_STR, "Conv_IntToString", inp={"InInt": "@gla2.Last"}); tk.call("fne", K_STR, "NotEqual_StrStr", inp={"A": "@cs.ReturnValue", "B": "@ls.ReturnValue"}); tk.branch("bfn", "@fne.ReturnValue")
    tk.call("lt", K_TXT, "Conv_StringToText", inp={"InString": "@ls.ReturnValue"}); tk.get("ge4", "Edit"); tk.call("fst", E_EDIT, "SetText", inp={"self": "@ge4.Edit", "InText": "@lt.ReturnValue"})
    tk.chain("entry", "bf", "btn", "tsl", "tlv", "tss", "tms"); tk.chain("bf:else", "bsn", "ssl", "ssv", "sms", "bfn"); tk.chain("bsn:else", "bfn"); tk.chain("bfn", "fst")
    # keys: Esc and Enter always stay here (an Esc that reached the game would open its pause menu); typed keys while the field has focus
    def keys(up):
        k = G(); k.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"})
        k.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Escape"}); k.call("ent", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Enter"})
        k.get("ge", "Edit"); k.call("hf", E_WIDGET, "HasKeyboardFocus", inp={"self": "@ge.Edit"})
        k.call("o1", K_MATH, "BooleanOR", inp={"A": "@esc.ReturnValue", "B": "@ent.ReturnValue"}); k.call("o2", K_MATH, "BooleanOR", inp={"A": "@o1.ReturnValue", "B": "@hf.ReturnValue"}); k.branch("b", "@o2.ReturnValue")
        k.call("h", K_WBL, "Handled"); k.link("h.ReturnValue", "return.ReturnValue")
        k.n("r2", "return_new"); k.call("u", K_WBL, "Unhandled"); k.link("u.ReturnValue", "r2.ReturnValue")
        if not up:
            k.chain("entry", "b", "return"); k.chain("b:else", "r2"); return k
        k.branch("be", "@ent.ReturnValue"); k.get("gm", "Manager"); k.get("gf", "First"); k.call("ma", MGR, "On Menu Action", inp={"self": "@gm.Manager", "name": "@gf.First"})
        k.branch("bx", "@esc.ReturnValue"); k.get("gm2", "Manager"); k.call("cm", MGR, "Close Menu", inp={"self": "@gm2.Manager"})
        k.chain("entry", "b", "be", "ma", "return"); k.chain("be:else", "bx", "cm", "return"); k.chain("bx:else", "return"); k.chain("b:else", "r2"); return k
    c = G(); ctail = ["entry"]; text_color(c, "tl", "Label", mcol(c, "ct", "ColText"), ctail)
    c.get("gsl", "Sld"); c.call("sbc", E_SLIDER, "SetSliderBarColor", inp={"self": "@gsl.Sld", "InValue": mcol(c, "csl", "ColSlider")}); ctail.append("sbc"); c.chain(*ctail)
    md = G(); md.call("h", K_WBL, "Handled"); md.link("h.ReturnValue", "return.ReturnValue"); md.chain("entry", "return")   # a click beside slider / field stays in the menu
    return blueprint(W_MAMOUNT, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Lo", "int"), var("Hi", "int"), var("FMax", "int"), var("Last", "int"), var("LastV", "float"), var("First", "name")],
                     functions=[fn("Init", [param("caption", "text"), param("lo", "int"), param("hi", "int"), param("start", "int"), param("fmax", "int"), param("first", "name")], graph=g), compute_fn(c),
                                fn("Tick", override=True, graph=tk), fn("OnKeyDown", override=True, graph=keys(False)), fn("OnKeyUp", override=True, graph=keys(True)),
                                fn("OnMouseButtonDown", override=True, graph=md)],
                     widget_tree=tree)


def w_context_menu():
    tree = roundbox("Frame", COL_CHIP_FRAME, 1, children=[roundbox("Bg", "(R=0.05,G=0.05,B=0.06,A=0.98)", 3, children=[w(U_VBOX, "Rows")])])
    c = G(); c.get("g", "Rows"); c.call("cl", U_PANELW, "ClearChildren", inp={"self": "@g.Rows"}); c.chain("entry", "cl")
    a = G(); a.get("g", "Rows"); a.call("ad", U_VBOX, "AddChildToVerticalBox", inp={"self": "@g.Rows", "Content": "@entry.widget"}); a.chain("entry", "ad")
    cc = G(); tail = ["entry"]; brush(cc, "sf", "Frame", mcol(cc, "cf", "ColChipFrame"), tail); brush(cc, "sb", "Bg", mcol(cc, "cb", "ColMenuBg"), tail); cc.chain(*tail)
    # Place At: at `pos` (viewport-local, as GetMousePositionOnViewport gives it), pushed back inside the viewport when the menu would
    # stick out right / below (desired size after a layout prepass; viewport size in the same local units, not pixels)
    pl = G(); pl.self_("me"); pl.call("fl", E_WIDGET, "ForceLayoutPrepass", inp={"self": "@me.self"}); pl.call("ds", E_WIDGET, "GetDesiredSize", inp={"self": "@me.self"})
    pl.call("bd", K_MATH, "BreakVector2D", inp={"InVec": "@ds.ReturnValue"}); pl.call("vg", "/Script/UMG.WidgetLayoutLibrary", "GetViewportWidgetGeometry")
    pl.call("vs", "/Script/UMG.SlateBlueprintLibrary", "GetLocalSize", inp={"Geometry": "@vg.ReturnValue"}); pl.call("bv", K_MATH, "BreakVector2D", inp={"InVec": "@vs.ReturnValue"})
    pl.call("bp", K_MATH, "BreakVector2D", inp={"InVec": "@entry.pos"})
    for ax in ("X", "Y"):
        pl.call("rm" + ax, K_MATH, "Subtract_FloatFloat", inp={"A": "@bv.%s" % ax, "B": "@bd.%s" % ax}); pl.call("mx" + ax, K_MATH, "FMax", inp={"A": "@rm%s.ReturnValue" % ax, "B": "0"})
        pl.call("c" + ax, K_MATH, "FClamp", inp={"Value": "@bp.%s" % ax, "Min": "0", "Max": "@mx%s.ReturnValue" % ax})
    pl.call("np", K_MATH, "MakeVector2D", inp={"X": "@cX.ReturnValue", "Y": "@cY.ReturnValue"})
    pl.call("sp", E_USERWIDGET, "SetPositionInViewport", inp={"self": "@me.self", "Position": "@np.ReturnValue", "bRemoveDPIScale": "false"})
    pl.chain("entry", "fl", "vg", "sp")
    return blueprint(W_MENU, E_USERWIDGET, variables=[var("Manager", "object:" + MGR)],
                     functions=[fn("Clear Rows", graph=c), fn("Add Row", [param("widget", "object:" + E_WIDGET)], graph=a), compute_fn(cc),
                                fn("Place At", [param("pos", "struct:/Script/CoreUObject.Vector2D")], graph=pl)], widget_tree=tree)


# ---------------- W_ColorSwatch (options: caption + colour box; click -> Manager.Open Theme Color(key)) ----------------
W_SWATCH = M + "/W_ColorSwatch"


def w_color_swatch():
    tree = roundbox("Bg", COL_CHIP, 0, props={"Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(8), sz(8), sz(8), sz(8))}, children=[w(U_HBOX, "HB", children=[
        sizebox("LblBox", 170, 24, [text("Label", "Colour", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Center"}),
        sizebox("SwBox", 60, 24, [roundbox("Frame", COL_FRAME, 1, children=[roundbox("Fill", "(R=1,G=1,B=1,A=1)", 0, None)])], slot={"VerticalAlignment": "VAlign_Center"})])])
    hv, hf, eg = hover_parts(W_SWATCH, "Frame", "Bg")
    g = G(); g.set("sk", "Key", inp={"Key": "@entry.key"}); g.get("gl", "Label"); g.call("st", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@entry.caption"})
    g.n("cc", "call_self", function="Compute Colors"); g.n("ap", "call_self", function="Apply Colors", inp={"hover": "false"}); g.chain("entry", "sk", "st", "cc", "ap")
    c = G(); tail = ["entry"]; set_colors(c, "Frame", mcol(c, "cf", "ColFrame"), mcol(c, "cfh", "ColFrameHover"), tail)
    set_colors(c, "Fill", mcol(c, "cch", "ColChip"), mcol(c, "cchh", "ColChipHover"), tail)   # "Fill" of the hover mechanics = the entry background (Bg)
    c.get("gm", "Manager"); c.get("gk", "Key"); c.call("tc", MGR, "Theme Color", inp={"self": "@gm.Manager", "key": "@gk.Key"}); tail.append("tc")
    brush(c, "sfl", "Fill", "@tc.color", tail); text_color(c, "tl", "Label", mcol(c, "ct", "ColText"), tail); c.chain(*tail)
    md = G(); md.get("gm0", "Manager"); md.self_("me0"); md.n("slb", "set", var="LastButton", cls=MGR, inp={"self": "@gm0.Manager", "LastButton": "@me0.self"})
    md.get("gm", "Manager"); md.get("gk", "Key"); md.call("oc", MGR, "Open Theme Color", inp={"self": "@gm.Manager", "key": "@gk.Key"})
    md.call("h", K_WBL, "Handled"); md.link("h.ReturnValue", "return.ReturnValue"); md.chain("entry", "slb", "oc", "return")
    return blueprint(W_SWATCH, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Key", "name")] + hv,
                     functions=[fn("Init", [param("key", "name"), param("caption", "text")], graph=g), compute_fn(c), refresh_fn(), fn("OnMouseButtonDown", override=True, graph=md)] + hf,
                     event_graph=eg, widget_tree=tree, defaults=HAND)


# ---------------- W_HexBar (beside the game's palette: the colour as #RRGGBB, copy / paste between pieces) ----------------
# The palette (PaletteUI) is the game's, a window in the middle of the screen; the bar is a viewport widget of its own above
# it, right-aligned under the window (Manager.Place Hex Bar on every tick). While the field has no focus it follows the palette live; Enter or
# leaving the field puts a valid code into the palette (Manager.Hex Commit), anything else falls back to the current colour.
# Ctrl+C / Ctrl+V work in the field itself; "Remember" / "Use" keep a colour inside AltUI across palettes (named so because
# they do not touch the clipboard - "Copy" would promise that).
W_HEX = M + "/W_HexBar"
HEX_EDIT_W = 110   # x SC


def w_hex_bar():
    tree = roundbox("Frame", COL_CHIP_FRAME, 1, children=[roundbox("Bg", "(R=0.05,G=0.05,B=0.06,A=0.98)", sz(6), children=[w(U_VBOX, "VB", children=[
        w(U_SIZE, "EditBox", props={"bOverride_WidthOverride": True, "WidthOverride": sz(HEX_EDIT_W)}, children=[
            w(E_EDIT, "Edit", props={"HintText": "#RRGGBB", "SelectAllTextWhenFocused": True, "ClearKeyboardFocusOnCommit": False, "WidgetStyle": EDIT_STYLE})]),
        w(U_HBOX, "Links", slot={"Padding": "(Left=%d,Top=%d,Right=0,Bottom=0)" % (sz(2), sz(5))}, children=[
            text("LinkCopy", "Remember", 12, COL_LINK, slot={"Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(14)}),
            text("LinkPaste", "Use", 12, COL_LINK)])])])])
    g = G(); g.set("se", "Editing", inp={"Editing": "false"})
    g.get("gc", "LinkCopy"); g.call("stc", E_TEXT, "SetText", inp={"self": "@gc.LinkCopy", "InText": mt(g, "tc", "Hex_Copy")})
    g.get("gp", "LinkPaste"); g.call("stp", E_TEXT, "SetText", inp={"self": "@gp.LinkPaste", "InText": mt(g, "tp", "Hex_Paste")})
    tail = ["entry", "se", "stc", "stp"]; brush(g, "sf", "Frame", mcol(g, "cf", "ColChipFrame"), tail); brush(g, "sb", "Bg", mcol(g, "cb", "ColMenuBg"), tail); g.chain(*tail)
    # Commit: the field -> Manager.Hex Commit (an invalid code changes nothing; the next Tick shows the current colour again)
    cm = G(); cm.set("se", "Editing", inp={"Editing": "false"}); cm.get("ge", "Edit"); cm.call("gt", E_EDIT, "GetText", inp={"self": "@ge.Edit"})
    cm.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@gt.ReturnValue"}); cm.get("gm", "Manager"); cm.call("hc", MGR, "Hex Commit", inp={"self": "@gm.Manager", "s": "@t2s.ReturnValue"})
    cm.chain("entry", "se", "hc")
    # Tick: focus gained -> Editing; focus lost while editing -> Commit; without focus the field shows the palette's colour;
    # link colours (hover; "Paste" dim while AltUI holds no colour)
    tk = G(); tk.get("ged", "Editing"); tk.get("ge", "Edit"); tk.call("hf", E_WIDGET, "HasKeyboardFocus", inp={"self": "@ge.Edit"})
    tk.call("nf", K_MATH, "Not_PreBool", inp={"A": "@hf.ReturnValue"}); tk.call("ne", K_MATH, "Not_PreBool", inp={"A": "@ged.Editing"})
    tk.call("lost", K_MATH, "BooleanAND", inp={"A": "@ged.Editing", "B": "@nf.ReturnValue"}); tk.call("got", K_MATH, "BooleanAND", inp={"A": "@ne.ReturnValue", "B": "@hf.ReturnValue"})
    tk.branch("bl", "@lost.ReturnValue"); tk.branch("bg", "@got.ReturnValue"); tk.n("cm", "call_self", function="Commit"); tk.set("sed", "Editing", inp={"Editing": "true"})
    tk.get("ge2", "Edit"); tk.call("hf2", E_WIDGET, "HasKeyboardFocus", inp={"self": "@ge2.Edit"}); tk.branch("bf", "@hf2.ReturnValue")
    tk.get("gm", "Manager"); tk.call("ch", MGR, "Color Hex", inp={"self": "@gm.Manager"})
    tk.get("ge3", "Edit"); tk.call("cur", E_EDIT, "GetText", inp={"self": "@ge3.Edit"}); tk.call("cs", K_TXT, "Conv_TextToString", inp={"InText": "@cur.ReturnValue"})
    tk.call("neq", K_STR, "NotEqual_StrStr", inp={"A": "@cs.ReturnValue", "B": "@ch.s"}); tk.branch("bn", "@neq.ReturnValue")
    tk.call("ht", K_TXT, "Conv_StringToText", inp={"InString": "@ch.s"}); tk.get("ge4", "Edit"); tk.call("st", E_EDIT, "SetText", inp={"self": "@ge4.Edit", "InText": "@ht.ReturnValue"})
    ttail = []
    tk.get("ghc", "LinkCopy"); tk.call("ihc", E_WIDGET, "IsHovered", inp={"self": "@ghc.LinkCopy"})
    tk.call("lcc", K_MATH, "SelectColor", inp={"A": mcol(tk, "cthc", "ColText"), "B": mcol(tk, "clc", "ColLink"), "bPickA": "@ihc.ReturnValue"}); text_color(tk, "scc", "LinkCopy", "@lcc.ReturnValue", ttail)
    tk.get("ghp", "LinkPaste"); tk.call("ihp", E_WIDGET, "IsHovered", inp={"self": "@ghp.LinkPaste"}); tk.get("gm2", "Manager"); tk.call("hcl", MGR, "Has Color Clip", inp={"self": "@gm2.Manager"})
    tk.call("lcp", K_MATH, "SelectColor", inp={"A": mcol(tk, "cthp", "ColText"), "B": mcol(tk, "clp", "ColLink"), "bPickA": "@ihp.ReturnValue"})
    tk.call("lcp2", K_MATH, "SelectColor", inp={"A": "@lcp.ReturnValue", "B": mcol(tk, "ctd", "ColTextDim"), "bPickA": "@hcl.yes"}); text_color(tk, "scp", "LinkPaste", "@lcp2.ReturnValue", ttail)
    tk.get("gmp", "Manager"); tk.call("plc", MGR, "Place Hex Bar", inp={"self": "@gmp.Manager"})   # the palette window moves with nothing we know of: follow it
    tk.chain("entry", "plc", "bl", "cm", "bf"); tk.chain("bl:else", "bg", "sed", "bf"); tk.chain("bg:else", "bf")
    tk.chain("bf:else", "bn", "st", ttail[0]); tk.chain("bf", ttail[0]); tk.chain("bn:else", ttail[0]); tk.chain(*ttail)
    # keys while the field has focus: all handled here (the game must not see typing); Enter -> Commit, Esc -> back to the
    # palette's colour; both return the focus to the panel, whose Esc closes the palette (Focus Color Keys)
    ku = G(); ku.get("ge", "Edit"); ku.call("hf", E_WIDGET, "HasKeyboardFocus", inp={"self": "@ge.Edit"}); ku.branch("b", "@hf.ReturnValue")
    ku.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"})
    ku.call("ent", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Enter"}); ku.branch("ben", "@ent.ReturnValue")
    ku.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Escape"}); ku.branch("bes", "@esc.ReturnValue")
    ku.n("cm", "call_self", function="Commit"); ku.set("sne", "Editing", inp={"Editing": "false"})
    ku.get("gm", "Manager"); ku.call("fp", MGR, "Focus Color Keys", inp={"self": "@gm.Manager"})
    ku.call("h", K_WBL, "Handled"); ku.link("h.ReturnValue", "return.ReturnValue")
    ku.n("r2", "return_new"); ku.call("u", K_WBL, "Unhandled"); ku.link("u.ReturnValue", "r2.ReturnValue")
    ku.chain("entry", "b", "ben", "cm", "fp", "return"); ku.chain("ben:else", "bes", "sne", "fp"); ku.chain("bes:else", "return"); ku.chain("b:else", "r2")
    kd = G(); kd.get("ge", "Edit"); kd.call("hf", E_WIDGET, "HasKeyboardFocus", inp={"self": "@ge.Edit"}); kd.branch("b", "@hf.ReturnValue")
    kd.call("h", K_WBL, "Handled"); kd.link("h.ReturnValue", "return.ReturnValue")
    kd.n("r2", "return_new"); kd.call("u", K_WBL, "Unhandled"); kd.link("u.ReturnValue", "r2.ReturnValue"); kd.chain("entry", "b", "return"); kd.chain("b:else", "r2")
    # click: Copy -> Manager.Color Clip Copy, Paste -> Color Clip Paste; anywhere else on the bar: into the field. Always handled,
    # so nothing reaches the palette below
    md = G(); md.get("glc", "LinkCopy"); md.call("hc", E_WIDGET, "IsHovered", inp={"self": "@glc.LinkCopy"}); md.branch("bc", "@hc.ReturnValue")
    md.get("gm", "Manager"); md.call("cc", MGR, "Color Clip Copy", inp={"self": "@gm.Manager"})
    md.get("glp", "LinkPaste"); md.call("hp", E_WIDGET, "IsHovered", inp={"self": "@glp.LinkPaste"}); md.branch("bp", "@hp.ReturnValue")
    md.get("gm2", "Manager"); md.call("cp", MGR, "Color Clip Paste", inp={"self": "@gm2.Manager"})
    md.get("ge", "Edit"); md.call("kf", E_WIDGET, "SetKeyboardFocus", inp={"self": "@ge.Edit"})
    md.call("h", K_WBL, "Handled"); md.link("h.ReturnValue", "return.ReturnValue")
    md.get("gec", "Edit"); md.call("kfc", E_WIDGET, "SetKeyboardFocus", inp={"self": "@gec.Edit"})   # Copy also selects the code: Ctrl+C puts it on the clipboard (Blueprint has no clipboard node)
    md.chain("entry", "bc", "cc", "kfc", "return"); md.chain("bc:else", "bp", "cp", "return"); md.chain("bp:else", "kf", "return")
    return blueprint(W_HEX, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Editing", "bool")],
                     functions=[fn("Init", graph=g), fn("Commit", graph=cm), fn("Tick", override=True, graph=tk), fn("OnKeyUp", override=True, graph=ku), fn("OnKeyDown", override=True, graph=kd),
                                fn("OnMouseButtonDown", override=True, graph=md)],
                     widget_tree=tree, defaults=HAND)


# ---------------- W_NameRow (Manage tab: fixed columns - name (icon, indent) · editable display name (+ search / like pak / like g links in the Mods category) · identifiers · content link) ----------------
EDIT_STYLE = "(Font=(Size=%d),Padding=(Left=%d,Top=%d,Right=%d,Bottom=%d),BackgroundColor=(SpecifiedColor=(R=0.1,G=0.1,B=0.12,A=1)),ForegroundColor=(SpecifiedColor=(R=1,G=1,B=1,A=1)))" % (sz(11), sz(6), sz(3), sz(6), sz(3))
ROW_PAD = 10                  # inner left/right padding of the row
FILL1 = {"Size": "(SizeRule=Fill,Value=1)", "VerticalAlignment": "VAlign_Center"}   # the three text columns share the width equally (the panel can be half the screen)


def w_name_row():
    tree = w(U_VBOX, "Outer", children=[
        w(U_SIZE, "Gap", props={"bOverride_HeightOverride": True, "HeightOverride": 0}),
        roundbox("Frame", COL_FRAME, 1, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(4)}, children=[roundbox("Fill", COL_FILL, 4, [
            w(U_HBOX, "Line", children=[
                w(U_HBOX, "NameHB", slot=FILL1, children=[
                    w(U_SIZE, "Indent", props={"bOverride_WidthOverride": True, "WidthOverride": sz(ROW_PAD)}, slot={"VerticalAlignment": "VAlign_Center"}),
                    fit_image("Icon", 78, 78, hidden=True, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("Label", "", 12, WHITE, wrap=True, break_all=True, slot=dict(FILL1, Padding="(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)))]),
                w(U_VBOX, "EditCol", slot=dict(FILL1, Padding="(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)), children=[
                    w(E_EDIT, "Edit", props={"HintText": "display name", "ClearKeyboardFocusOnCommit": False, "WidgetStyle": EDIT_STYLE}),
                    w(U_HBOX, "Links", props={"Visibility": "Collapsed"}, slot={"Padding": "(Left=%d,Top=%d,Right=0,Bottom=0)" % (sz(6), sz(3))}, children=[   # Mods category only: search · like pak
                        text("LinkSearch", "search", 11, COL_LINK, slot={"Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(14)}),
                        text("LinkLike", "like pak", 11, COL_LINK)])]),   # "like pak" (mod) / "like g" (group): the identifier as display name
                text("Revert", "\u21ba", 14, COL_LINK, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(12)}),
                w(U_VBOX, "OriginCol", slot=dict(FILL1, Padding="(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)), children=[
                    text("Origin", "", 10, GREY, wrap=True, break_all=True),
                    text("PakLink", "", 10, COL_LINK, wrap=True, break_all=True, props_extra={"Visibility": "Collapsed"}),   # "pak: <mod>" -> Manager.Open Mod Content
                    text("Rest", "", 10, GREY, wrap=True, break_all=True, props_extra={"Visibility": "Collapsed"})]),
                text("Content", "View content", 11, COL_LINK, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(ROW_PAD)}),
            ])])])])
    hv, hf, eg = hover_parts(W_NAMEROW, "Frame", "Fill")
    g = G(); tail = ["entry"]
    for v, pin in (("Kind", "kind"), ("Row", "row"), ("Default", "default")):
        g.set("s" + v, v, inp={v: "@entry." + pin}); tail.append("s" + v)
    g.set("sed", "Editing", inp={"Editing": "false"}); tail.append("sed")
    # label: "Mod: <default>" / "Group: <default>" in the Mods category, the default name elsewhere
    g.call("ism", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "mod"}); g.call("isg", K_MATH, "EqualEqual_NameName", inp={"A": "@entry.kind", "B": "group"})
    g.call("pm", K_STR, "Concat_StrStr", inp={"A": mts(g, "km", "Lbl_KindMod"), "B": ": "}); g.call("pg", K_STR, "Concat_StrStr", inp={"A": mts(g, "kg", "Lbl_KindGroup"), "B": ": "})
    g.call("p1", K_MATH, "SelectString", inp={"A": "@pg.ReturnValue", "B": "", "bPickA": "@isg.ReturnValue"}); g.call("p2", K_MATH, "SelectString", inp={"A": "@pm.ReturnValue", "B": "@p1.ReturnValue", "bPickA": "@ism.ReturnValue"})
    g.call("lab", K_STR, "Concat_StrStr", inp={"A": "@p2.ReturnValue", "B": "@entry.default"})
    g.call("dt", K_TXT, "Conv_StringToText", inp={"InString": "@lab.ReturnValue"}); g.get("gl", "Label"); g.call("stl", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@dt.ReturnValue"}); tail.append("stl")
    g.get("ge", "Edit"); g.call("sh", E_EDIT, "SetHintText", inp={"self": "@ge.Edit", "InText": mt(g, "hn", "Hint_Name")}); tail.append("sh")
    g.get("go", "Origin"); g.call("sto", E_TEXT, "SetText", inp={"self": "@go.Origin", "InText": "@entry.origin"}); tail.append("sto")
    g.set("smod", "Mod", inp={"Mod": "@entry.mod"}); tail.append("smod")
    # pak link line (pieces from a mod): "pak: <mod>"; rest line (group / makeup type) when not empty
    g.call("hasm", K_MATH, "NotEqual_NameName", inp={"A": "@entry.mod", "B": "None"}); g.branch("bpm", "@hasm.ReturnValue")
    g.call("mds", K_STR, "Conv_NameToString", inp={"InName": "@entry.mod"}); g.call("pkt", K_STR, "Concat_StrStr", inp={"A": mts(g, "tpk", "Tip_Pak"), "B": "@mds.ReturnValue"}); g.call("pktt", K_TXT, "Conv_StringToText", inp={"InString": "@pkt.ReturnValue"})
    g.get("gpl", "PakLink"); g.call("stpl", E_TEXT, "SetText", inp={"self": "@gpl.PakLink", "InText": "@pktt.ReturnValue"})
    g.get("gpl2", "PakLink"); g.call("splv", E_WIDGET, "SetVisibility", inp={"self": "@gpl2.PakLink", "InVisibility": "Visible"})
    g.get("gpl3", "PakLink"); g.call("splc", E_WIDGET, "SetVisibility", inp={"self": "@gpl3.PakLink", "InVisibility": "Collapsed"})
    g.call("rem", K_TXT, "TextIsEmpty", inp={"InText": "@entry.rest"}); g.branch("bre", "@rem.ReturnValue")
    g.get("grs", "Rest"); g.call("srsc", E_WIDGET, "SetVisibility", inp={"self": "@grs.Rest", "InVisibility": "Collapsed"})
    g.get("grs2", "Rest"); g.call("strs", E_TEXT, "SetText", inp={"self": "@grs2.Rest", "InText": "@entry.rest"}); g.get("grs3", "Rest"); g.call("srsv", E_WIDGET, "SetVisibility", inp={"self": "@grs3.Rest", "InVisibility": "Visible"})
    g.chain("bpm", "stpl", "splv", "bre"); g.chain("bpm:else", "splc", "bre"); g.chain("bre", "srsc"); g.chain("bre:else", "strs", "srsv")
    tail += ["bpm"]; tail_join = ["srsc", "srsv"]
    g.get("gc", "Content"); g.call("stc", E_TEXT, "SetText", inp={"self": "@gc.Content", "InText": mt(g, "ct", "Btn_ModContent")})
    g.chain(*tail); [g.chain(j, "stc") for j in tail_join]; tail = ["stc"]
    g.get("gls", "LinkSearch"); g.call("stls", E_TEXT, "SetText", inp={"self": "@gls.LinkSearch", "InText": mt(g, "tsn", "Btn_SearchName")}); tail.append("stls")
    g.call("lks", K_MATH, "SelectString", inp={"A": mts(g, "tlp", "Btn_LikePak"), "B": mts(g, "tlg", "Btn_LikeGroup"), "bPickA": "@ism.ReturnValue"}); g.call("lkt", K_TXT, "Conv_StringToText", inp={"InString": "@lks.ReturnValue"})
    g.get("glp", "LinkLike"); g.call("stlp", E_TEXT, "SetText", inp={"self": "@glp.LinkLike", "InText": "@lkt.ReturnValue"}); tail.append("stlp")
    # links only in the Mods category (mod + group rows): 'search' and 'like pak' / 'like g'
    g.call("mg", K_MATH, "BooleanOR", inp={"A": "@ism.ReturnValue", "B": "@isg.ReturnValue"}); g.branch("bl", "@mg.ReturnValue")
    g.get("glk", "Links"); g.call("slv", E_WIDGET, "SetVisibility", inp={"self": "@glk.Links", "InVisibility": "Visible"})
    g.get("glk2", "Links"); g.call("slc", E_WIDGET, "SetVisibility", inp={"self": "@glk2.Links", "InVisibility": "Collapsed"})
    g.call("gop", E_USERWIDGET, "GetOwningPlayer"); g.call("ctt", K_WBL, "Create", inp={"WidgetType": W_TOOLTIP, "OwningPlayer": "@gop.ReturnValue"}); g.cast("ctc", W_TOOLTIP, "@ctt.ReturnValue")
    g.get("gmt", "Manager"); g.n("stm", "set", var="Manager", cls=W_TOOLTIP, inp={"self": "@ctc.AsW_Tooltip", "Manager": "@gmt.Manager"})
    g.call("tti", W_TOOLTIP, "Init", inp={"self": "@ctc.AsW_Tooltip", "text": mt(g, "rt", "Tip_Revert")}); g.get("gr", "Revert"); g.call("str", E_WIDGET, "SetToolTip", inp={"self": "@gr.Revert", "Widget": "@ctc.AsW_Tooltip"})
    tail += ["ctt", "stm", "tti", "str"]
    # indent (group rows) inside the name column; gap above a mod header that follows other rows
    g.call("sel", K_MATH, "SelectInt", inp={"A": str(sz(ROW_PAD + 24)), "B": str(sz(ROW_PAD)), "bPickA": "@entry.indent"}); g.call("self", K_MATH, "Conv_IntToFloat", inp={"InInt": "@sel.ReturnValue"})
    g.get("gi", "Indent"); g.call("swo", U_SIZE, "SetWidthOverride", inp={"self": "@gi.Indent", "InWidthOverride": "@self.ReturnValue"}); tail.append("swo")
    g.call("gsel", K_MATH, "SelectInt", inp={"A": str(sz(12)), "B": "0", "bPickA": "@entry.gap"}); g.call("gself", K_MATH, "Conv_IntToFloat", inp={"InInt": "@gsel.ReturnValue"})
    g.get("gg", "Gap"); g.call("sho", U_SIZE, "SetHeightOverride", inp={"self": "@gg.Gap", "InHeightOverride": "@gself.ReturnValue"}); tail.append("sho")
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@entry.icon"}); g.branch("bi", "@iv.ReturnValue"); tail.append("bi")
    g.get("gic", "Icon"); g.call("sb", E_IMAGE, "SetBrushFromTexture", inp={"self": "@gic.Icon", "Texture": "@entry.icon", "bMatchSize": "true"})
    g.get("gic2", "Icon"); g.call("siv0", E_WIDGET, "SetVisibility", inp={"self": "@gic2.Icon", "InVisibility": "Visible"})   # fit_image(hidden=True) starts the image itself hidden
    g.get("gib", "IconBox"); g.call("siv", E_WIDGET, "SetVisibility", inp={"self": "@gib.IconBox", "InVisibility": "Visible"})
    g.get("gib2", "IconBox"); g.call("sic", E_WIDGET, "SetVisibility", inp={"self": "@gib2.IconBox", "InVisibility": "Collapsed"})
    g.branch("bc", "@entry.content")
    g.get("gc2", "Content"); g.call("scv", E_WIDGET, "SetVisibility", inp={"self": "@gc2.Content", "InVisibility": "Visible"})
    g.get("gc3", "Content"); g.call("scc", E_WIDGET, "SetVisibility", inp={"self": "@gc3.Content", "InVisibility": "Hidden"})   # keeps its width: G: rows line up with PAK: rows
    g.get("gc4", "Content"); g.call("sccc", E_WIDGET, "SetVisibility", inp={"self": "@gc4.Content", "InVisibility": "Collapsed"})   # no link in the whole category: the identifiers take the width
    g.branch("bcs", "@entry.content space")
    g.n("sc", "call_self", function="Show Custom", inp={"custom": "@entry.custom"})
    g.n("cc", "call_self", function="Compute Colors"); g.n("ap", "call_self", function="Apply Colors", inp={"hover": "false"})
    g.chain(*tail, "sb", "siv0", "siv", "bl"); g.chain("bi:else", "sic", "bl"); g.chain("bl", "slv", "bc"); g.chain("bl:else", "slc", "bc")
    g.chain("bc", "scv", "sc"); g.chain("bc:else", "bcs", "scc", "sc"); g.chain("bcs:else", "sccc", "sc"); g.chain("sc", "cc", "ap")
    init = fn("Init", [param("kind", "name"), param("row", "name"), param("default", "string"), param("custom", "string"), param("origin", "text"), param("icon", "object:" + E_TEX2D),
                       param("indent", "bool"), param("content", "bool"), param("gap", "bool"), param("mod", "name"), param("rest", "text"), param("content space", "bool")], graph=g)
    # Show Custom(custom): the field shows the name in effect (custom, else the default); the revert link only when a custom name is stored
    sc = G(); sc.call("em", K_STR, "IsEmpty", inp={"InString": "@entry.custom"}); sc.get("gd", "Default")
    sc.call("shown", K_MATH, "SelectString", inp={"A": "@gd.Default", "B": "@entry.custom", "bPickA": "@em.ReturnValue"}); sc.call("ct", K_TXT, "Conv_StringToText", inp={"InString": "@shown.ReturnValue"})
    sc.get("ge", "Edit"); sc.call("st", E_EDIT, "SetText", inp={"self": "@ge.Edit", "InText": "@ct.ReturnValue"}); sc.branch("b", "@em.ReturnValue")
    sc.get("gr", "Revert"); sc.call("hr", E_WIDGET, "SetVisibility", inp={"self": "@gr.Revert", "InVisibility": "Hidden"})
    sc.get("gr2", "Revert"); sc.call("vr", E_WIDGET, "SetVisibility", inp={"self": "@gr2.Revert", "InVisibility": "Visible"})
    sc.chain("entry", "st", "b", "hr"); sc.chain("b:else", "vr")
    # Commit: text field -> Manager.Set Custom Name (a text equal to the default stores nothing), then show what is stored
    cm = G(); cm.set("se", "Editing", inp={"Editing": "false"})
    cm.get("ge", "Edit"); cm.call("gt", E_EDIT, "GetText", inp={"self": "@ge.Edit"}); cm.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@gt.ReturnValue"})
    cm.call("tr", K_STR, "Trim", inp={"SourceString": "@t2s.ReturnValue"}); cm.call("tr2", K_STR, "TrimTrailing", inp={"SourceString": "@tr.ReturnValue"})
    cm.get("gd", "Default"); cm.call("same", K_STR, "EqualEqual_StrStr", inp={"A": "@tr2.ReturnValue", "B": "@gd.Default"})
    cm.call("val", K_MATH, "SelectString", inp={"A": "", "B": "@tr2.ReturnValue", "bPickA": "@same.ReturnValue"})
    cm.get("gm", "Manager"); cm.get("gk", "Kind"); cm.get("gr", "Row"); cm.call("sn", MGR, "Set Custom Name", inp={"self": "@gm.Manager", "kind": "@gk.Kind", "row": "@gr.Row", "name": "@val.ReturnValue"})
    cm.get("gm2", "Manager"); cm.get("gk2", "Kind"); cm.get("gr2", "Row"); cm.call("cn", MGR, "Custom Name", inp={"self": "@gm2.Manager", "kind": "@gk2.Kind", "row": "@gr2.Row"})
    cm.n("sc", "call_self", function="Show Custom", inp={"custom": "@cn.name"})
    cm.get("gm3", "Manager"); cm.call("rr", MGR, "Refresh Manage Rows", inp={"self": "@gm3.Manager"}); cm.chain("entry", "se", "sn", "sc", "rr")   # other rows showing this name
    # Cancel: back to the stored name
    ca = G(); ca.set("se", "Editing", inp={"Editing": "false"})
    ca.get("gm", "Manager"); ca.get("gk", "Kind"); ca.get("gr", "Row"); ca.call("cn", MGR, "Custom Name", inp={"self": "@gm.Manager", "kind": "@gk.Kind", "row": "@gr.Row"})
    ca.n("sc", "call_self", function="Show Custom", inp={"custom": "@cn.name"}); ca.chain("entry", "se", "sc")
    # Refresh (Manager.Refresh Manage Rows after a name change elsewhere): new identifiers + stored name, never while this row is being edited
    rf = G(); rf.get("ged", "Editing"); rf.branch("be", "@ged.Editing")
    rf.get("go", "Origin"); rf.call("sto", E_TEXT, "SetText", inp={"self": "@go.Origin", "InText": "@entry.origin"})
    rf.n("sc", "call_self", function="Show Custom", inp={"custom": "@entry.custom"}); rf.chain("entry", "be"); rf.chain("be:else", "sto", "sc")
    # Focus Edit: keyboard focus into the text field (Tab navigation, see OnKeyDown)
    fe = G(); fe.get("ge", "Edit"); fe.call("kf", E_WIDGET, "SetKeyboardFocus", inp={"self": "@ge.Edit"}); fe.chain("entry", "kf")
    # OnKeyDown: Tab / Shift+Tab while editing -> Manager.Focus Name Row(self, backwards) (the panel swallows every other key-down anyway)
    kd = G(); kd.get("ged", "Editing"); kd.branch("be", "@ged.Editing")
    kd.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"}); kd.call("tab", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Tab"}); kd.branch("bt", "@tab.ReturnValue")
    kd.call("sh", K_IN, "InputEvent_IsShiftDown", inp={"Input": "@entry.InKeyEvent"})
    kd.get("gm", "Manager"); kd.self_("me"); kd.call("fn", MGR, "Focus Name Row", inp={"self": "@gm.Manager", "row": "@me.self", "backwards": "@sh.ReturnValue"})
    kd.call("h", K_WBL, "Handled"); kd.link("h.ReturnValue", "return.ReturnValue")
    kd.n("r2", "return_new"); kd.call("u", K_WBL, "Unhandled"); kd.link("u.ReturnValue", "r2.ReturnValue")
    kd.chain("entry", "be", "bt", "fn", "return"); kd.chain("bt:else", "r2"); kd.chain("be:else", "r2")
    # OnKeyUp while editing: Enter -> Commit, Escape -> Cancel (Handled); otherwise Unhandled
    ku = G(); ku.get("ged", "Editing"); ku.branch("be", "@ged.Editing")
    ku.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"})
    ku.call("ent", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Enter"}); ku.branch("ben", "@ent.ReturnValue")
    ku.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Escape"}); ku.branch("bes", "@esc.ReturnValue")
    ku.call("tab", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Tab"}); ku.branch("btb", "@tab.ReturnValue")   # Tab moved the focus on key-down: swallow the key-up
    ku.n("cm", "call_self", function="Commit"); ku.n("ca", "call_self", function="Cancel")
    ku.call("h", K_WBL, "Handled"); ku.link("h.ReturnValue", "return.ReturnValue")
    ku.n("r2", "return_new"); ku.call("u", K_WBL, "Unhandled"); ku.link("u.ReturnValue", "r2.ReturnValue")
    ku.chain("entry", "be", "ben", "cm", "return"); ku.chain("ben:else", "bes", "ca", "return"); ku.chain("bes:else", "btb", "return"); ku.chain("btb:else", "return"); ku.chain("be:else", "r2")
    # Tick: focus gained -> Editing; focus lost while editing -> Commit; hover colours of the two links
    tk = G(); tk.get("ged", "Editing"); tk.get("ge", "Edit"); tk.call("hf", E_WIDGET, "HasKeyboardFocus", inp={"self": "@ge.Edit"})
    tk.call("nf", K_MATH, "Not_PreBool", inp={"A": "@hf.ReturnValue"}); tk.call("ne", K_MATH, "Not_PreBool", inp={"A": "@ged.Editing"})
    tk.call("lost", K_MATH, "BooleanAND", inp={"A": "@ged.Editing", "B": "@nf.ReturnValue"}); tk.call("got", K_MATH, "BooleanAND", inp={"A": "@ne.ReturnValue", "B": "@hf.ReturnValue"})
    tk.branch("bl", "@lost.ReturnValue"); tk.branch("bg", "@got.ReturnValue"); tk.n("cm", "call_self", function="Commit"); tk.set("se", "Editing", inp={"Editing": "true"})
    ttail = []
    for wn in ("Content", "Revert", "LinkSearch", "LinkLike", "PakLink"):
        tk.get("gh" + wn, wn); tk.call("ih" + wn, E_WIDGET, "IsHovered", inp={"self": "@gh%s.%s" % (wn, wn)})
        tk.call("lc" + wn, K_MATH, "SelectColor", inp={"A": mcol(tk, "clh" + wn, "ColText"), "B": mcol(tk, "cl" + wn, "ColLink"), "bPickA": "@ih%s.ReturnValue" % wn})   # ColLinkHover is a fill colour (alpha 0.1)
        text_color(tk, "sc" + wn, wn, "@lc%s.ReturnValue" % wn, ttail)
    tk.chain("entry", "bl", "cm", ttail[0]); tk.chain("bl:else", "bg", "se", ttail[0]); tk.chain("bg:else", ttail[0]); tk.chain(*ttail)
    # click: revert -> Manager.Set Custom Name(kind, row, "") + Show Custom("") + Refresh Manage Rows; content -> Manager.Open Mod Content(row);
    # search -> Manager.Manage Search For(field text); like pak / like g -> field = identifier (Row) + Commit; pak link -> Open Mod Content(Mod);
    # icon -> Manage Go To(kind, row) (the piece on its own page); elsewhere: focus the text field
    md = G(); md.get("gr", "Revert"); md.call("hr", E_WIDGET, "IsHovered", inp={"self": "@gr.Revert"}); md.branch("br", "@hr.ReturnValue")
    md.get("gm", "Manager"); md.get("gk", "Kind"); md.get("grw", "Row"); md.call("sn", MGR, "Set Custom Name", inp={"self": "@gm.Manager", "kind": "@gk.Kind", "row": "@grw.Row", "name": ""})
    md.n("sc", "call_self", function="Show Custom", inp={"custom": ""}); md.get("gm4", "Manager"); md.call("rr", MGR, "Refresh Manage Rows", inp={"self": "@gm4.Manager"})
    md.get("gc", "Content"); md.call("hc", E_WIDGET, "IsHovered", inp={"self": "@gc.Content"}); md.branch("bc", "@hc.ReturnValue")
    md.get("gm2", "Manager"); md.get("grw2", "Row"); md.call("oc", MGR, "Open Mod Content", inp={"self": "@gm2.Manager", "mod": "@grw2.Row"})
    md.get("gls", "LinkSearch"); md.call("hs", E_WIDGET, "IsHovered", inp={"self": "@gls.LinkSearch"}); md.branch("bs", "@hs.ReturnValue")
    md.get("ge2", "Edit"); md.call("gt", E_EDIT, "GetText", inp={"self": "@ge2.Edit"}); md.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@gt.ReturnValue"})
    md.get("gm3", "Manager"); md.call("sf", MGR, "Manage Search For", inp={"self": "@gm3.Manager", "s": "@t2s.ReturnValue"})
    md.get("gpk", "PakLink"); md.call("hpk", E_WIDGET, "IsHovered", inp={"self": "@gpk.PakLink"}); md.branch("bpk", "@hpk.ReturnValue")
    md.get("gm5", "Manager"); md.get("gmod", "Mod"); md.call("omc", MGR, "Open Mod Content", inp={"self": "@gm5.Manager", "mod": "@gmod.Mod"})
    md.get("gib", "IconBox"); md.call("hib", E_WIDGET, "IsHovered", inp={"self": "@gib.IconBox"}); md.branch("bib", "@hib.ReturnValue")
    md.get("gm6", "Manager"); md.get("gk6", "Kind"); md.get("grw6", "Row"); md.call("mgt", MGR, "Manage Go To", inp={"self": "@gm6.Manager", "kind": "@gk6.Kind", "row": "@grw6.Row"})
    md.get("glp", "LinkLike"); md.call("hp", E_WIDGET, "IsHovered", inp={"self": "@glp.LinkLike"}); md.branch("bp", "@hp.ReturnValue")
    md.get("grw3", "Row"); md.call("r2s", K_STR, "Conv_NameToString", inp={"InName": "@grw3.Row"}); md.call("r2t", K_TXT, "Conv_StringToText", inp={"InString": "@r2s.ReturnValue"})
    md.get("ge3", "Edit"); md.call("stp", E_EDIT, "SetText", inp={"self": "@ge3.Edit", "InText": "@r2t.ReturnValue"}); md.n("cmp", "call_self", function="Commit")
    md.get("ge", "Edit"); md.call("kf", E_WIDGET, "SetKeyboardFocus", inp={"self": "@ge.Edit"})
    md.call("h", K_WBL, "Handled"); md.link("h.ReturnValue", "return.ReturnValue")
    md.chain("entry", "br", "sn", "sc", "rr", "return"); md.chain("br:else", "bc", "oc", "return"); md.chain("bc:else", "bs", "sf", "return")
    md.chain("bs:else", "bp", "stp", "cmp", "return"); md.chain("bp:else", "bpk", "omc", "return"); md.chain("bpk:else", "bib", "mgt", "return"); md.chain("bib:else", "kf", "return")
    c = G(); ctail = ["entry"]
    set_colors(c, "Frame", mcol(c, "cf", "ColFrame"), mcol(c, "cfh", "ColFrameHover"), ctail); set_colors(c, "Fill", mcol(c, "cfi", "ColFill"), mcol(c, "cfih", "ColFillHover"), ctail)
    text_color(c, "tl", "Label", mcol(c, "ct", "ColText"), ctail); text_color(c, "to", "Origin", mcol(c, "ctd", "ColTextDim"), ctail); c.chain(*ctail)
    return blueprint(W_NAMEROW, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Kind", "name"), var("Row", "name"), var("Default", "string"), var("Editing", "bool"), var("Mod", "name")] + hv,
                     functions=[init, fn("Show Custom", [param("custom", "string")], graph=sc), fn("Commit", graph=cm), fn("Cancel", graph=ca), fn("Refresh", [param("custom", "string"), param("origin", "text")], graph=rf), fn("Focus Edit", graph=fe), compute_fn(c),
                                fn("OnKeyDown", override=True, graph=kd), fn("OnKeyUp", override=True, graph=ku), fn("Tick", override=True, graph=tk), fn("OnMouseButtonDown", override=True, graph=md)] + hf,
                     event_graph=eg, widget_tree=tree)


# ---------------- W_KodexLockRow (Codex > Passwords: one code lock as a table row - lock · place · state · code link) ----------------
def w_kodex_lock_row():
    # zebra stripe as W_ConflictRow; fixed columns so the rows line up, the place takes the rest; the code link (W_TextButton, "show code" /
    # "code: 1234") is added into CodeBox by the manager
    cell = {"VerticalAlignment": "VAlign_Center"}
    tree = w(E_BORDER, "Bg", props={"BrushColor": "(R=1,G=1,B=1,A=0)", "Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(8), sz(4), sz(8), sz(4))}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % CONFLICT_GAP}, children=[
        w(U_HBOX, "Row", children=[
            sizebox("LockBox", 90, None, [text("Lock", "Lock 1", 13, slot=cell)], slot=cell),
            w(U_HBOX, "PlaceBox", slot={"Size": "(SizeRule=Fill,Value=1)", "VerticalAlignment": "VAlign_Center"}, children=[text("Place", "3 m", 13, slot=cell)]),
            sizebox("StateBox", 110, None, [text("State", "open", 13, slot=cell)], slot=cell),
            sizebox("CodeSize", 150, None, [w(U_HBOX, "CodeBox")], slot=cell)])])
    g = G()
    for n in ("Lock", "Place", "State"):
        g.get("g" + n, n); g.call("s" + n, E_TEXT, "SetText", inp={"self": "@g%s.%s" % (n, n), "InText": "@entry.%s" % n.lower()})
    g.call("bc", K_MATH, "SelectColor", inp={"A": "(R=1,G=1,B=1,A=0.05)", "B": "(R=1,G=1,B=1,A=0)", "bPickA": "@entry.tinted"})
    g.get("gb", "Bg"); g.call("sb", E_BORDER, "SetBrushColor", inp={"self": "@gb.Bg", "InBrushColor": "@bc.ReturnValue"})
    g.n("cc", "call_self", function="Compute Colors"); g.chain("entry", "sLock", "sPlace", "sState", "sb", "cc")
    l = G(); l.get("g", "CodeBox"); l.call("a", U_HBOX, "AddChildToHorizontalBox", inp={"self": "@g.CodeBox", "Content": "@entry.widget"}); l.chain("entry", "a")
    c = G(); tail = ["entry"]
    for n in ("Lock", "Place", "State"): text_color(c, "t" + n, n, mcol(c, "c" + n, "ColText"), tail)
    c.chain(*tail)
    return blueprint(W_KODEXLOCK, E_USERWIDGET, variables=[var("Manager", "object:" + MGR)],
                     functions=[fn("Init", [param("lock", "text"), param("place", "text"), param("state", "text"), param("tinted", "bool")], graph=g),
                                fn("Add Link", [param("widget", "object:" + E_WIDGET)], graph=l), compute_fn(c)],
                     widget_tree=tree)


# ---------------- W_ConflictRow (options: slot caption · one W_SubTab chip per conflicting slot · links "all free" / "Vanilla") ----------------
CONFLICT_GAP = sz(4) + 1   # chip gap = gap below a row


def w_conflict_row():
    # Bg: zebra stripe (tinted rows a light rgba tint, first row tinted), padded; the gap below a row equals the gap between chips
    tree = w(E_BORDER, "Bg", props={"BrushColor": "(R=1,G=1,B=1,A=0)", "Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(6), sz(4), sz(6), sz(4))}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % CONFLICT_GAP}, children=[
        w(U_HBOX, "Row", children=[
            sizebox("LabelBox", 180, 24, [text("Label", "Slot", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(4)}),
            w(U_WRAP, "Chips", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (CONFLICT_GAP, CONFLICT_GAP)}, slot={"Size": "(SizeRule=Fill,Value=1)", "VerticalAlignment": "VAlign_Top"}),
            w(U_HBOX, "Links", slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=%d,Top=%d,Right=0,Bottom=0)" % (sz(12), sz(4))})])])
    g = G(); g.get("gl", "Label"); g.call("st", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@entry.caption"})
    g.call("bc", K_MATH, "SelectColor", inp={"A": "(R=1,G=1,B=1,A=0.05)", "B": "(R=1,G=1,B=1,A=0)", "bPickA": "@entry.tinted"})
    g.get("gb", "Bg"); g.call("sb", E_BORDER, "SetBrushColor", inp={"self": "@gb.Bg", "InBrushColor": "@bc.ReturnValue"})
    g.n("cc", "call_self", function="Compute Colors"); g.chain("entry", "st", "sb", "cc")
    a = G(); a.get("g", "Chips"); a.call("a", U_WRAP, "AddChildToWrapBox", inp={"self": "@g.Chips", "Content": "@entry.widget"}); a.chain("entry", "a")
    l = G(); l.get("g", "Links"); l.call("a", U_HBOX, "AddChildToHorizontalBox", inp={"self": "@g.Links", "Content": "@entry.widget"}); l.chain("entry", "a")
    c = G(); tail = ["entry"]; text_color(c, "tl", "Label", mcol(c, "ct", "ColText"), tail); c.chain(*tail)
    return blueprint(W_CONFLICT, E_USERWIDGET, variables=[var("Manager", "object:" + MGR)],
                     functions=[fn("Init", [param("caption", "text"), param("tinted", "bool")], graph=g), fn("Add Chip", [param("widget", "object:" + E_WIDGET)], graph=a), fn("Add Link", [param("widget", "object:" + E_WIDGET)], graph=l), compute_fn(c)],
                     widget_tree=tree)


# ---------------- W_ModField (one field of the Mods tab: label + toggle / slider / choice / button; reports to Manager.Mod Field Changed) ----------------
W_MODFIELD = M + "/W_ModField"
import modui as mu


# clickable parts of a mod field: (border, colour, colour under the mouse); dark while pressed (COL_PRESS), acting on release
MODFIELD_PRESS = [("Act", "(R=1,G=1,B=1,A=0.08)", "(R=1,G=1,B=1,A=0.18)"), ("KeyBg", "(R=1,G=1,B=1,A=0.08)", "(R=1,G=1,B=1,A=0.18)"),
                  ("Prev", COL_NONE, "(R=1,G=1,B=1,A=0.12)"), ("Next", COL_NONE, "(R=1,G=1,B=1,A=0.12)"),
                  ("Minus", COL_NONE, "(R=1,G=1,B=1,A=0.12)"), ("Plus", COL_NONE, "(R=1,G=1,B=1,A=0.12)")]
COL_PRESS = "(R=0,G=0,B=0,A=0.35)"
PRESS_TYPES = [("Button", "Act"), ("Key", "KeyBg"), ("Choice", "Prev"), ("Choice", "Next"), ("Number", "Minus"), ("Number", "Plus")]


def w_mod_field():
    """Checkbox and slider are polled in Tick like the options page does; choice arrows and the button are plain borders,
    OnMouseButtonDown asks which one is under the mouse. Value is what the manager set last or what was reported last,
    so neither side echoes the other. The slider runs 0..1 internally and maps to Min..Max (Slider Value / Slider Pos)."""
    hidden = {"Visibility": "Collapsed"}; vc = {"VerticalAlignment": "VAlign_Center"}
    def pad_l(px): return {"VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(px)}
    tree = w(E_BORDER, "Bg", props={"BrushColor": COL_NONE, "Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(6), sz(6))}, children=[
        w(U_HBOX, "Row", children=[
            sizebox("LabelBox", 260, 24, [text("Label", "Field", 13, slot=vc)], slot=vc),
            sizebox("CheckWrap", 34, 34, [w(U_SCALE, "CheckScale", props={"Stretch": "ScaleToFit"}, children=[w(E_CHECK, "Check", props={"WidgetStyle": check_style(CHECK_SIZE)})])], slot=vc),
            # the slider takes the width that is there (at least 120, at most 360) and the value always keeps its room - with fixed widths
            # the row ran past the right edge on a narrower panel and the value was cut off (game test 2026-10-03)
            w(U_HBOX, "SldHB", props=hidden, slot=dict(vc, Size="(SizeRule=Fill,Value=1)"), children=[
                w(U_SIZE, "SldBox", props={"bOverride_MinDesiredWidth": True, "MinDesiredWidth": sz(120), "bOverride_MaxDesiredWidth": True, "MaxDesiredWidth": sz(360),
                                           "bOverride_HeightOverride": True, "HeightOverride": sz(24)}, slot=dict(vc, Size="(SizeRule=Fill,Value=1)"),
                  children=[w(E_SLIDER, "Sld", props={"Value": 0.0, "StepSize": 0.001, "SliderBarColor": "(R=0.35,G=0.42,B=0.55,A=1)", "SliderHandleColor": "(R=1,G=1,B=1,A=1)",
                                                      "WidgetStyle": "(BarThickness=5.0)"})]),
                sizebox("ValBox", 110, 24, [text("ValText", "0", 12, GREY, slot=vc)], slot=pad_l(10))]),
            w(U_HBOX, "ChoiceHB", props=hidden, slot=vc, children=[
                w(E_BORDER, "Prev", props={"BrushColor": COL_NONE, "Padding": "(Left=%d,Top=0,Right=%d,Bottom=0)" % (sz(6), sz(6))}, slot=vc, children=[text("PrevText", "‹", 16, COL_LINK)]),
                sizebox("ChoiceBox", 220, 24, [text("ChoiceText", "", 13, slot=vc, center=True)], slot=vc),
                w(E_BORDER, "Next", props={"BrushColor": COL_NONE, "Padding": "(Left=%d,Top=0,Right=%d,Bottom=0)" % (sz(6), sz(6))}, slot=vc, children=[text("NextText", "›", 16, COL_LINK)])]),
            w(E_BORDER, "Act", props={"BrushColor": "(R=1,G=1,B=1,A=0.08)", "Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(10), sz(3), sz(10), sz(3)), "Visibility": "Collapsed"},
              slot=vc, children=[text("ActText", "", 13, COL_LINK)]),
            w(U_HBOX, "NumHB", props=hidden, slot=vc, children=[
                w(E_BORDER, "Minus", props={"BrushColor": COL_NONE, "Padding": "(Left=%d,Top=0,Right=%d,Bottom=0)" % (sz(6), sz(6))}, slot=vc, children=[text("MinusText", "\u2212", 16, COL_LINK)]),
                sizebox("NumBox", 120, 24, [text("NumText", "0", 13, slot=vc, center=True)], slot=vc),
                w(E_BORDER, "Plus", props={"BrushColor": COL_NONE, "Padding": "(Left=%d,Top=0,Right=%d,Bottom=0)" % (sz(6), sz(6))}, slot=vc, children=[text("PlusText", "+", 16, COL_LINK)])]),
            sizebox("SwatchBox", 60, 24, [w(E_BORDER, "Swatch", props={"BrushColor": "(R=1,G=1,B=1,A=1)"})], slot=vc),
            sizebox("EditBox", 360, 34, [w(E_BORDER, "EditBg", props={"BrushColor": "(R=1,G=1,B=1,A=0.08)", "Padding": "(Left=0,Top=0,Right=0,Bottom=0)"},
                                          children=[w(E_EDIT, "Edit", props={"WidgetStyle": SEARCH_STYLE})])], slot=vc),
            sizebox("InfoBox", 460, 24, [text("InfoText", "", 13, wrap=True, slot=vc)], slot=vc),
            # Key: the bound key as a button - left click waits for the next key (the panel catches it), right click clears
            sizebox("KeyBox", 260, 30, [w(E_BORDER, "KeyBg", props={"BrushColor": "(R=1,G=1,B=1,A=0.08)", "HorizontalAlignment": "HAlign_Center", "VerticalAlignment": "VAlign_Center",
                                                                   "Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(10), sz(3), sz(10), sz(3))},
                                          children=[text("KeyText", "", 13, COL_LINK)])], slot=vc)])])
    # Init(field): keep what the tick and the clicks need, show the control of this type
    g = G(); g.brk("bf", mu.FIELD_STRUCT, "@entry.field")
    tail = ["entry"]
    for v in ("Key", "Type", "Min", "Max", "Step", "Options"):
        g.set("s" + v, v, inp={v: "@bf." + v}); tail.append("s" + v)
    g.get("gl", "Label"); g.call("stl", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@bf.Label"}); tail.append("stl")
    g.get("ga", "ActText"); g.call("sta", E_TEXT, "SetText", inp={"self": "@ga.ActText", "InText": "@bf.Label"}); tail.append("sta")
    for i, part in enumerate(("CheckWrap", "SwatchBox", "EditBox", "InfoBox", "KeyBox")):   # size boxes carry no Visibility in the tree
        g.get("gh%d" % i, part); g.call("hh%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@gh%d.%s" % (i, part), "InVisibility": "Collapsed"}); tail.append("hh%d" % i)
    shows = [("Toggle", "CheckWrap"), ("Slider", "SldHB"), ("Choice", "ChoiceHB"), ("Button", "Act"), ("Number", "NumHB"), ("Color", "SwatchBox"), ("Text", "EditBox"), ("Info", "InfoBox"), ("Key", "KeyBox")]
    for i, (t, part) in enumerate(shows):
        g.call("is%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@bf.Type", "B": t}); g.branch("b%d" % i, "@is%d.ReturnValue" % i)
        g.get("gp%d" % i, part); g.call("sv%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@gp%d.%s" % (i, part), "InVisibility": "Visible"})
    g.call("isb", K_MATH, "EqualEqual_NameName", inp={"A": "@bf.Type", "B": "Button"}); g.branch("bbtn", "@isb.ReturnValue")
    g.get("gl2", "Label"); g.call("stl2", E_TEXT, "SetText", inp={"self": "@gl2.Label", "InText": ""})   # a button carries its label itself
    g.set("sv0v", "Value", inp={"Value": "-1.0"}); g.n("setv", "call_self", function="Set Value", inp={"value": "@bf.Min"})   # -1: the first Set Value always applies
    g.n("cc", "call_self", function="Compute Colors")
    g.chain(*tail, "b0")
    for i in range(len(shows)):
        nxt = "b%d" % (i + 1) if i + 1 < len(shows) else "bbtn"
        g.chain("b%d" % i, "sv%d" % i, nxt); g.chain("b%d:else" % i, nxt)
    g.chain("bbtn", "stl2", "sv0v", "setv", "cc"); g.chain("bbtn:else", "sv0v")
    # Slider Value(pos) / Slider Pos(value)
    sv = G(); sv.get("gmn", "Min"); sv.get("gmx", "Max"); sv.get("gst", "Step")
    sv.call("rng", K_MATH, "Subtract_FloatFloat", inp={"A": "@gmx.Max", "B": "@gmn.Min"}); sv.call("mul", K_MATH, "Multiply_FloatFloat", inp={"A": "@entry.pos", "B": "@rng.ReturnValue"})
    sv.call("raw", K_MATH, "Add_FloatFloat", inp={"A": "@gmn.Min", "B": "@mul.ReturnValue"})
    sv.call("rel", K_MATH, "Subtract_FloatFloat", inp={"A": "@raw.ReturnValue", "B": "@gmn.Min"}); sv.call("st1", K_MATH, "FMax", inp={"A": "@gst.Step", "B": "0.000001"})
    sv.call("div", K_MATH, "Divide_FloatFloat", inp={"A": "@rel.ReturnValue", "B": "@st1.ReturnValue"}); sv.call("rnd", K_MATH, "Round", inp={"A": "@div.ReturnValue"})
    sv.call("rf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@rnd.ReturnValue"}); sv.call("snp", K_MATH, "Multiply_FloatFloat", inp={"A": "@rf.ReturnValue", "B": "@st1.ReturnValue"})
    sv.call("stp", K_MATH, "Add_FloatFloat", inp={"A": "@gmn.Min", "B": "@snp.ReturnValue"})
    sv.call("hs", K_MATH, "Greater_FloatFloat", inp={"A": "@gst.Step", "B": "0.0"}); sv.call("pick", K_MATH, "SelectFloat", inp={"A": "@stp.ReturnValue", "B": "@raw.ReturnValue", "bPickA": "@hs.ReturnValue"})
    sv.call("cl", K_MATH, "FClamp", inp={"Value": "@pick.ReturnValue", "Min": "@gmn.Min", "Max": "@gmx.Max"}); sv.link("cl.ReturnValue", "return.value")
    sp = G(); sp.get("gmn", "Min"); sp.get("gmx", "Max")
    sp.call("rng", K_MATH, "Subtract_FloatFloat", inp={"A": "@gmx.Max", "B": "@gmn.Min"}); sp.call("rel", K_MATH, "Subtract_FloatFloat", inp={"A": "@entry.value", "B": "@gmn.Min"})
    sp.call("r1", K_MATH, "FMax", inp={"A": "@rng.ReturnValue", "B": "0.000001"}); sp.call("div", K_MATH, "Divide_FloatFloat", inp={"A": "@rel.ReturnValue", "B": "@r1.ReturnValue"})
    sp.call("cl", K_MATH, "FClamp", inp={"Value": "@div.ReturnValue", "Min": "0.0", "Max": "1.0"}); sp.link("cl.ReturnValue", "return.pos")
    # Update Text: the slider's number (no decimals from Step 1 up), the chosen option
    ut = G(); ut.get("gv", "Value"); ut.get("gst", "Step"); ut.call("ge1", K_MATH, "GreaterEqual_FloatFloat", inp={"A": "@gst.Step", "B": "1.0"})
    ut.call("dig", K_MATH, "SelectInt", inp={"A": "0", "B": "2", "bPickA": "@ge1.ReturnValue"})
    ut.call("ft", K_TXT, "Conv_FloatToText", inp={"Value": "@gv.Value", "MinimumFractionalDigits": "@dig.ReturnValue", "MaximumFractionalDigits": "@dig.ReturnValue"})
    ut.get("gvt", "ValText"); ut.call("svt", E_TEXT, "SetText", inp={"self": "@gvt.ValText", "InText": "@ft.ReturnValue"})
    ut.get("gnt", "NumText"); ut.call("snt", E_TEXT, "SetText", inp={"self": "@gnt.NumText", "InText": "@ft.ReturnValue"})
    ut.get("go", "Options"); ut.call("ol", K_ARR, "Array_Length", inp={"TargetArray": "@go.Options"}); ut.call("hasopt", K_MATH, "Greater_IntInt", inp={"A": "@ol.ReturnValue", "B": "0"}); ut.branch("bo", "@hasopt.ReturnValue")
    ut.get("gv2", "Value"); ut.call("ri", K_MATH, "Round", inp={"A": "@gv2.Value"}); ut.call("mx", K_MATH, "Subtract_IntInt", inp={"A": "@ol.ReturnValue", "B": "1"})
    ut.call("ci", K_MATH, "Clamp", inp={"Value": "@ri.ReturnValue", "Min": "0", "Max": "@mx.ReturnValue"})
    ut.get("go2", "Options"); ut.call("oget", K_ARR, "Array_Get", inp={"TargetArray": "@go2.Options", "Index": "@ci.ReturnValue"})
    ut.get("gct", "ChoiceText"); ut.call("sct", E_TEXT, "SetText", inp={"self": "@gct.ChoiceText", "InText": "@oget.Item"})
    ut.chain("entry", "svt", "snt", "bo", "sct")
    # Set Value(value): from the manager (poll) - stored first, so the tick sees no change of its own
    sv2 = G(); sv2.get("gv", "Value"); sv2.call("same", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gv.Value", "B": "@entry.value", "ErrorTolerance": "0.0001"}); sv2.branch("bs", "@same.ReturnValue")
    sv2.set("s", "Value", inp={"Value": "@entry.value"})
    sv2.call("gt", K_MATH, "Greater_FloatFloat", inp={"A": "@entry.value", "B": "0.5"}); sv2.get("gc", "Check"); sv2.call("sc", E_CHECK, "SetIsChecked", inp={"self": "@gc.Check", "InIsChecked": "@gt.ReturnValue"})
    sv2.n("pos", "call_self", function="Slider Pos", inp={"value": "@entry.value"}); sv2.get("gsl", "Sld"); sv2.call("ss", E_SLIDER, "SetValue", inp={"self": "@gsl.Sld", "InValue": "@pos.pos"})
    sv2.n("ut", "call_self", function="Update Text")
    sv2.chain("entry", "bs"); sv2.chain("bs:else", "s", "sc", "ss", "ut")
    # Set Color(color) / Set Text(text): from the manager (poll); a text field the player is typing in is left alone
    sc = G(); sc.set("s", "ColorValue", inp={"ColorValue": "@entry.color"}); sc.get("gs", "Swatch"); sc.call("b", E_BORDER, "SetBrushColor", inp={"self": "@gs.Swatch", "InBrushColor": "@entry.color"})
    sc.chain("entry", "s", "b")
    st = G(); st.get("gt", "Type"); st.call("ii", K_MATH, "EqualEqual_NameName", inp={"A": "@gt.Type", "B": "Info"}); st.branch("bi", "@ii.ReturnValue")
    st.call("s2t", K_TXT, "Conv_StringToText", inp={"InString": "@entry.text"}); st.get("gi", "InfoText"); st.call("si", E_TEXT, "SetText", inp={"self": "@gi.InfoText", "InText": "@s2t.ReturnValue"})
    st.get("ge", "Edit"); st.call("hf", E_WIDGET, "HasKeyboardFocus", inp={"self": "@ge.Edit"}); st.branch("bf", "@hf.ReturnValue")
    st.get("gtv", "TextValue"); st.call("same", K_STR, "EqualEqual_StrStr", inp={"A": "@gtv.TextValue", "B": "@entry.text"}); st.branch("bs", "@same.ReturnValue")
    st.set("stv", "TextValue", inp={"TextValue": "@entry.text"}); st.call("s2t2", K_TXT, "Conv_StringToText", inp={"InString": "@entry.text"})
    st.get("ge2", "Edit"); st.call("se", E_EDIT, "SetText", inp={"self": "@ge2.Edit", "InText": "@s2t2.ReturnValue"})
    st.chain("entry", "bi", "si"); st.chain("bi:else", "bf"); st.chain("bf:else", "bs"); st.chain("bs:else", "stv", "se")
    # Key fields: Set Key(pressed) from the poll or the capture, Set Capturing(on) while the panel waits; the caption is
    # "press a key…" while waiting, else the key's name or "none" (an empty key)
    sk = G(); sk.set("s", "KeyValue", inp={"KeyValue": "@entry.pressed"}); sk.n("u", "call_self", function="Update Key Text"); sk.chain("entry", "s", "u")
    scp = G(); scp.set("s", "Capturing", inp={"Capturing": "@entry.on"}); scp.n("u", "call_self", function="Update Key Text"); scp.chain("entry", "s", "u")
    uk = G(); uk.get("gkv", "KeyValue"); uk.call("kv", K_IN, "Key_IsValid", inp={"Key": "@gkv.KeyValue"}); uk.call("dn", K_IN, "Key_GetDisplayName", inp={"Key": "@gkv.KeyValue"})
    uk.call("dns", K_TXT, "Conv_TextToString", inp={"InText": "@dn.ReturnValue"}); uk.call("nn", K_TXT, "Conv_TextToString", inp={"InText": mt(uk, "mnk", "Lbl_KeyNone")})
    uk.call("s1", K_MATH, "SelectString", inp={"A": "@dns.ReturnValue", "B": "@nn.ReturnValue", "bPickA": "@kv.ReturnValue"})
    uk.call("pk", K_TXT, "Conv_TextToString", inp={"InText": mt(uk, "mpk", "Lbl_KeyPress")}); uk.get("gcp", "Capturing")
    uk.call("s2", K_MATH, "SelectString", inp={"A": "@pk.ReturnValue", "B": "@s1.ReturnValue", "bPickA": "@gcp.Capturing"})
    uk.call("t", K_TXT, "Conv_StringToText", inp={"InString": "@s2.ReturnValue"}); uk.get("gkt", "KeyText"); uk.call("st", E_TEXT, "SetText", inp={"self": "@gkt.KeyText", "InText": "@t.ReturnValue"})
    uk.chain("entry", "st")
    mp = G(); mp.set("sp", "PressPart", inp={"PressPart": "@entry.part"}); mp.chain("entry", "sp")
    # Set Enabled(yes): greyed out and not clickable while the mod's actor is missing
    se = G(); se.self_("me"); se.call("en", E_WIDGET, "SetIsEnabled", inp={"self": "@me.self", "bInIsEnabled": "@entry.yes"})
    se.call("op", K_MATH, "SelectFloat", inp={"A": "1.0", "B": "0.4", "bPickA": "@entry.yes"}); se.self_("me2"); se.call("ro", E_WIDGET, "SetRenderOpacity", inp={"self": "@me2.self", "InOpacity": "@op.ReturnValue"})
    se.chain("entry", "en", "ro")
    # Report(value): store, redraw the texts, tell the manager
    rp = G(); rp.set("s", "Value", inp={"Value": "@entry.value"}); rp.n("ut", "call_self", function="Update Text")
    rp.get("gm", "Manager"); rp.get("gk", "Key"); rp.call("mc", MGR, "Mod Field Changed", inp={"self": "@gm.Manager", "key": "@gk.Key", "value": "@entry.value"})
    rp.chain("entry", "s", "ut", "mc")
    # Tick: checkbox and slider as the player moves them
    tk = G(); tk.get("gt", "Type"); tk.call("ist", K_MATH, "EqualEqual_NameName", inp={"A": "@gt.Type", "B": "Toggle"}); tk.branch("bt", "@ist.ReturnValue")
    tk.get("gc", "Check"); tk.call("ic", E_CHECK, "IsChecked", inp={"self": "@gc.Check"}); tk.call("cv", K_MATH, "SelectFloat", inp={"A": "1.0", "B": "0.0", "bPickA": "@ic.ReturnValue"})
    tk.get("gv", "Value"); tk.call("chg", K_MATH, "NotEqual_FloatFloat", inp={"A": "@cv.ReturnValue", "B": "@gv.Value"}); tk.branch("bc", "@chg.ReturnValue")
    tk.get("gm", "Manager"); tk.get("gk", "Key"); tk.set("scv", "Value", inp={"Value": "@cv.ReturnValue"})
    tk.call("mc", MGR, "Mod Field Changed", inp={"self": "@gm.Manager", "key": "@gk.Key", "value": "@cv.ReturnValue"})
    tk.get("gt2", "Type"); tk.call("iss", K_MATH, "EqualEqual_NameName", inp={"A": "@gt2.Type", "B": "Slider"}); tk.branch("bs", "@iss.ReturnValue")
    tk.get("gsl", "Sld"); tk.call("gsv", E_SLIDER, "GetValue", inp={"self": "@gsl.Sld"}); tk.n("sval", "call_self", function="Slider Value", inp={"pos": "@gsv.ReturnValue"})
    tk.get("gv2", "Value"); tk.call("same", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@sval.value", "B": "@gv2.Value", "ErrorTolerance": "0.0001"}); tk.branch("bsm", "@same.ReturnValue")
    tk.n("rep", "call_self", function="Report", inp={"value": "@sval.value"})
    tk.get("gt3", "Type"); tk.call("isx", K_MATH, "EqualEqual_NameName", inp={"A": "@gt3.Type", "B": "Text"}); tk.branch("bx", "@isx.ReturnValue")
    tk.get("ge", "Edit"); tk.call("hf", E_WIDGET, "HasKeyboardFocus", inp={"self": "@ge.Edit"}); tk.call("gtx", E_EDIT, "GetText", inp={"self": "@ge.Edit"})
    tk.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@gtx.ReturnValue"}); tk.get("gtv", "TextValue")
    tk.call("dif", K_STR, "NotEqual_StrStr", inp={"A": "@t2s.ReturnValue", "B": "@gtv.TextValue"}); tk.call("nf", K_MATH, "Not_PreBool", inp={"A": "@hf.ReturnValue"})
    tk.call("com", K_MATH, "BooleanAND", inp={"A": "@dif.ReturnValue", "B": "@nf.ReturnValue"}); tk.branch("bxc", "@com.ReturnValue")
    tk.set("stv", "TextValue", inp={"TextValue": "@t2s.ReturnValue"})
    tk.get("gm3", "Manager"); tk.get("gk3", "Key"); tk.call("mtc", MGR, "Mod Text Changed", inp={"self": "@gm3.Manager", "key": "@gk3.Key", "text": "@t2s.ReturnValue"})
    # button feedback: a clickable part lights up under the mouse and stays dark while it is pressed and the mouse is over it
    # (the press holds the mouse, so hover comes from the geometry then)
    tk.call("mp", "/Script/UMG.WidgetLayoutLibrary", "GetMousePositionOnPlatform"); fb = []
    for i, (part, base, hover) in enumerate(MODFIELD_PRESS):
        tk.get("fp%d" % i, part); tk.call("fh%d" % i, E_WIDGET, "IsHovered", inp={"self": "@fp%d.%s" % (i, part)})
        tk.get("fg%d" % i, part); tk.call("fgg%d" % i, E_WIDGET, "GetCachedGeometry", inp={"self": "@fg%d.%s" % (i, part)})
        tk.call("fu%d" % i, K_SLATE, "IsUnderLocation", inp={"Geometry": "@fgg%d.ReturnValue" % i, "AbsoluteCoordinate": "@mp.ReturnValue"})
        tk.get("fpp%d" % i, "PressPart"); tk.call("fe%d" % i, K_STR, "EqualEqual_StrStr", inp={"A": "@fpp%d.PressPart" % i, "B": part})
        tk.call("fa%d" % i, K_MATH, "BooleanAND", inp={"A": "@fe%d.ReturnValue" % i, "B": "@fu%d.ReturnValue" % i})
        tk.call("fc%d" % i, K_MATH, "SelectColor", inp={"A": hover, "B": base, "bPickA": "@fh%d.ReturnValue" % i})
        tk.call("fd%d" % i, K_MATH, "SelectColor", inp={"A": COL_PRESS, "B": "@fc%d.ReturnValue" % i, "bPickA": "@fa%d.ReturnValue" % i})
        tk.get("fq%d" % i, part); tk.call("fs%d" % i, E_BORDER, "SetBrushColor", inp={"self": "@fq%d.%s" % (i, part), "InBrushColor": "@fd%d.ReturnValue" % i}); fb.append("fs%d" % i)
    tk.chain("entry", "mp", *fb, "bt", "bc", "scv", "mc"); tk.chain("bt:else", "bs", "bsm"); tk.chain("bsm:else", "rep"); tk.chain("bs:else", "bx", "bxc", "stv", "mtc")
    # Clicks: the clickable parts (MODFIELD_PRESS) act on release, like buttons - the press darkens the part and holds the mouse
    # (CaptureMouse), the release over the same part does what it stands for (OnMouseButtonUp), a release elsewhere nothing.
    # A right click on a Key field clears it at once; the colour swatch opens the palette on the press.
    md = G(); md.call("btn", K_IN, "PointerEvent_GetEffectingButton", inp={"Input": "@entry.MouseEvent"})
    md.call("isl", K_IN, "EqualEqual_KeyKey", inp={"A": "@btn.ReturnValue", "B": "LeftMouseButton"}); md.call("isr", K_IN, "EqualEqual_KeyKey", inp={"A": "@btn.ReturnValue", "B": "RightMouseButton"})
    part = ""
    for i, (t, p) in enumerate(PRESS_TYPES):
        md.get("pg%d" % i, p); md.call("ph%d" % i, E_WIDGET, "IsHovered", inp={"self": "@pg%d.%s" % (i, p)}); md.get("pt%d" % i, "Type")
        md.call("pe%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@pt%d.Type" % i, "B": t}); md.call("pa%d" % i, K_MATH, "BooleanAND", inp={"A": "@pe%d.ReturnValue" % i, "B": "@ph%d.ReturnValue" % i})
        md.call("ps%d" % i, K_MATH, "SelectString", inp={"A": p, "B": part, "bPickA": "@pa%d.ReturnValue" % i}); part = "@ps%d.ReturnValue" % i
    md.call("pne", K_STR, "NotEqual_StrStr", inp={"A": part, "B": ""}); md.call("plp", K_MATH, "BooleanAND", inp={"A": "@isl.ReturnValue", "B": "@pne.ReturnValue"}); md.branch("bp", "@plp.ReturnValue")
    md.n("mk", "call_self", function="Mark Press", inp={"part": part})
    md.call("h", K_WBL, "Handled"); md.self_("me"); md.call("cap", K_WBL, "CaptureMouse", inp={"Reply": "@h.ReturnValue", "CapturingWidget": "@me.self"}); md.link("cap.ReturnValue", "return.ReturnValue")
    md.n("r2", "return_new"); md.call("u", K_WBL, "Unhandled"); md.link("u.ReturnValue", "r2.ReturnValue")
    md.n("r3", "return_new"); md.call("h3", K_WBL, "Handled"); md.link("h3.ReturnValue", "r3.ReturnValue")
    # Key field, right click: none
    md.get("gkb", "KeyBg"); md.call("hk", E_WIDGET, "IsHovered", inp={"self": "@gkb.KeyBg"}); md.get("gt5", "Type")
    md.call("isk", K_MATH, "EqualEqual_NameName", inp={"A": "@gt5.Type", "B": "Key"}); md.call("ak0", K_MATH, "BooleanAND", inp={"A": "@isk.ReturnValue", "B": "@hk.ReturnValue"})
    md.call("akr", K_MATH, "BooleanAND", inp={"A": "@ak0.ReturnValue", "B": "@isr.ReturnValue"}); md.branch("bkr", "@akr.ReturnValue")
    md.get("gnk", "NoKey"); md.n("skn", "call_self", function="Set Key", inp={"pressed": "@gnk.NoKey"})
    md.get("gm6", "Manager"); md.get("gk6", "Key"); md.get("gnk2", "NoKey"); md.call("mkc", MGR, "Mod Key Changed", inp={"self": "@gm6.Manager", "key": "@gk6.Key", "pressed": "@gnk2.NoKey"})
    # colour: the swatch opens AltUI's palette for this field
    md.get("gsw", "Swatch"); md.call("hsw", E_WIDGET, "IsHovered", inp={"self": "@gsw.Swatch"}); md.get("gt4", "Type")
    md.call("isco", K_MATH, "EqualEqual_NameName", inp={"A": "@gt4.Type", "B": "Color"}); md.call("aco0", K_MATH, "BooleanAND", inp={"A": "@isco.ReturnValue", "B": "@hsw.ReturnValue"})
    md.call("aco", K_MATH, "BooleanAND", inp={"A": "@aco0.ReturnValue", "B": "@isl.ReturnValue"}); md.branch("bco", "@aco.ReturnValue")
    md.get("gm4", "Manager"); md.get("gk4", "Key"); md.get("gcv", "ColorValue")
    md.call("omc", MGR, "Open Mod Color", inp={"self": "@gm4.Manager", "key": "@gk4.Key", "color": "@gcv.ColorValue"})
    # Button / Toggle, right click: the quick menu row (Mod Field Context)
    md.get("gt7", "Type"); md.call("ibt", K_MATH, "EqualEqual_NameName", inp={"A": "@gt7.Type", "B": "Button"}); md.call("itg", K_MATH, "EqualEqual_NameName", inp={"A": "@gt7.Type", "B": "Toggle"})
    md.call("obt", K_MATH, "BooleanOR", inp={"A": "@ibt.ReturnValue", "B": "@itg.ReturnValue"}); md.call("abt", K_MATH, "BooleanAND", inp={"A": "@obt.ReturnValue", "B": "@isr.ReturnValue"}); md.branch("bmf", "@abt.ReturnValue")
    md.get("gm7", "Manager"); md.get("gk7", "Key"); md.call("mfc", MGR, "Mod Field Context", inp={"self": "@gm7.Manager", "key": "@gk7.Key"})
    md.chain("entry", "bp", "mk", "return"); md.chain("bp:else", "bkr", "skn", "mkc", "r3"); md.chain("bkr:else", "bco", "omc", "r3"); md.chain("bco:else", "bmf", "mfc", "r3"); md.chain("bmf:else", "r2")
    # OnMouseButtonUp: the pressed part, released over it -> its action; the press ends either way
    mu_ = G(); mu_.get("gpp", "PressPart"); mu_.call("pne", K_STR, "NotEqual_StrStr", inp={"A": "@gpp.PressPart", "B": ""}); mu_.branch("bp", "@pne.ReturnValue")
    mu_.call("ssp", K_IN, "PointerEvent_GetScreenSpacePosition", inp={"Input": "@entry.MouseEvent"})
    over = "false"
    for i, (part_, _, _) in enumerate(MODFIELD_PRESS):
        mu_.get("og%d" % i, part_); mu_.call("oge%d" % i, E_WIDGET, "GetCachedGeometry", inp={"self": "@og%d.%s" % (i, part_)})
        mu_.call("ou%d" % i, K_SLATE, "IsUnderLocation", inp={"Geometry": "@oge%d.ReturnValue" % i, "AbsoluteCoordinate": "@ssp.ReturnValue"})
        mu_.get("opp%d" % i, "PressPart"); mu_.call("oe%d" % i, K_STR, "EqualEqual_StrStr", inp={"A": "@opp%d.PressPart" % i, "B": part_})
        mu_.call("oa%d" % i, K_MATH, "BooleanAND", inp={"A": "@oe%d.ReturnValue" % i, "B": "@ou%d.ReturnValue" % i})
        mu_.call("oo%d" % i, K_MATH, "BooleanOR", inp={"A": over, "B": "@oa%d.ReturnValue" % i}); over = "@oo%d.ReturnValue" % i
    mu_.branch("bo", over)
    mu_.get("gm", "Manager"); mu_.get("gk", "Key"); mu_.call("x0", MGR, "Mod Field Changed", inp={"self": "@gm.Manager", "key": "@gk.Key", "value": "1.0"})
    mu_.self_("me1"); mu_.get("gm1", "Manager"); mu_.call("x1", MGR, "Begin Key Capture", inp={"self": "@gm1.Manager", "field": "@me1.self"})
    mu_.n("x2", "call_self", function="Step Choice", inp={"dir": "-1"}); mu_.n("x3", "call_self", function="Step Choice", inp={"dir": "1"})
    mu_.n("x4", "call_self", function="Step Number", inp={"sign": "-1.0"}); mu_.n("x5", "call_self", function="Step Number", inp={"sign": "1.0"})
    acts = [("Act", "x0"), ("KeyBg", "x1"), ("Prev", "x2"), ("Next", "x3"), ("Minus", "x4"), ("Plus", "x5")]
    mu_.set("clr", "PressPart", inp={"PressPart": ""})
    prev = "bo"
    for i, (p, act) in enumerate(acts):
        mu_.get("dp%d" % i, "PressPart"); mu_.call("de%d" % i, K_STR, "EqualEqual_StrStr", inp={"A": "@dp%d.PressPart" % i, "B": p}); mu_.branch("db%d" % i, "@de%d.ReturnValue" % i)
        mu_.chain(prev, "db%d" % i); mu_.chain("db%d" % i, act, "clr"); prev = "db%d:else" % i
    mu_.chain(prev, "clr"); mu_.chain("bo:else", "clr")
    mu_.call("h", K_WBL, "Handled"); mu_.call("rel", K_WBL, "ReleaseMouseCapture", inp={"Reply": "@h.ReturnValue"}); mu_.link("rel.ReturnValue", "return.ReturnValue")
    mu_.n("r2", "return_new"); mu_.call("u", K_WBL, "Unhandled"); mu_.link("u.ReturnValue", "r2.ReturnValue")
    mu_.chain("entry", "bp", "bo"); mu_.chain("clr", "return"); mu_.chain("bp:else", "r2")
    # capture lost (window change, another capture): no press left hanging
    cl = G(); cl.set("clr", "PressPart", inp={"PressPart": ""}); cl.chain("entry", "clr")
    # Step Choice(dir): the next / previous option, round; Step Number(sign): - / + by Step (0 -> 1), clamped
    sch = G(); sch.get("go", "Options"); sch.call("n", K_ARR, "Array_Length", inp={"TargetArray": "@go.Options"})
    sch.get("gv", "Value"); sch.call("ri", K_MATH, "Round", inp={"A": "@gv.Value"})
    sch.call("a1", K_MATH, "Add_IntInt", inp={"A": "@ri.ReturnValue", "B": "@entry.dir"}); sch.call("a2", K_MATH, "Add_IntInt", inp={"A": "@a1.ReturnValue", "B": "@n.ReturnValue"})
    sch.call("n1", K_MATH, "Max", inp={"A": "@n.ReturnValue", "B": "1"}); sch.call("mod", K_MATH, "Percent_IntInt", inp={"A": "@a2.ReturnValue", "B": "@n1.ReturnValue"})
    sch.call("mf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@mod.ReturnValue"}); sch.n("rep", "call_self", function="Report", inp={"value": "@mf.ReturnValue"}); sch.chain("entry", "rep")
    snm = G(); snm.get("gst", "Step"); snm.call("sp0", K_MATH, "Greater_FloatFloat", inp={"A": "@gst.Step", "B": "0.0"}); snm.call("stp", K_MATH, "SelectFloat", inp={"A": "@gst.Step", "B": "1.0", "bPickA": "@sp0.ReturnValue"})
    snm.call("dlt", K_MATH, "Multiply_FloatFloat", inp={"A": "@stp.ReturnValue", "B": "@entry.sign"})
    snm.get("gv3", "Value"); snm.call("nv", K_MATH, "Add_FloatFloat", inp={"A": "@gv3.Value", "B": "@dlt.ReturnValue"})
    snm.get("gmn", "Min"); snm.get("gmx", "Max"); snm.call("ncl", K_MATH, "FClamp", inp={"Value": "@nv.ReturnValue", "Min": "@gmn.Min", "Max": "@gmx.Max"})
    snm.n("repn", "call_self", function="Report", inp={"value": "@ncl.ReturnValue"}); snm.chain("entry", "repn")
    # colours
    c = G(); ct = ["entry"]
    c.get("gt", "Type"); c.call("ih", K_MATH, "EqualEqual_NameName", inp={"A": "@gt.Type", "B": "Header"})
    c.call("lc", K_MATH, "SelectColor", inp={"A": mcol(c, "chd", "ColHead"), "B": mcol(c, "ctx", "ColText"), "bPickA": "@ih.ReturnValue"})
    text_color(c, "tl", "Label", "@lc.ReturnValue", ct); text_color(c, "tv", "ValText", mcol(c, "cdim", "ColTextDim"), ct); text_color(c, "tc", "ChoiceText", mcol(c, "ctx2", "ColText"), ct)
    for i, wn in enumerate(("PrevText", "NextText", "ActText")): text_color(c, "tk%d" % i, wn, mcol(c, "clk%d" % i, "ColLink"), ct)
    text_color(c, "tnm", "NumText", mcol(c, "ctx3", "ColText"), ct); text_color(c, "tif", "InfoText", mcol(c, "ctx4", "ColText"), ct)
    for i, wn in enumerate(("MinusText", "PlusText")): text_color(c, "tp%d" % i, wn, mcol(c, "clp%d" % i, "ColLink"), ct)
    brush(c, "beb", "EditBg", mcol(c, "cch", "ColChip"), ct); text_color(c, "tky", "KeyText", mcol(c, "clky", "ColLink"), ct)
    c.get("gsl", "Sld"); c.call("sbc", E_SLIDER, "SetSliderBarColor", inp={"self": "@gsl.Sld", "InValue": mcol(c, "csl", "ColSlider")}); ct.append("sbc")   # like the panel's sliders (Apply Theme)
    c.chain(*ct)
    return blueprint(W_MODFIELD, E_USERWIDGET,
                     variables=[var("Manager", "object:" + MGR), var("Key", "name"), var("Type", "name"), var("Min", "float"), var("Max", "float"), var("Step", "float"),
                                var("Options", "text", "array"), var("Value", "float"), var("ColorValue", S_LINCOLOR), var("TextValue", "string"),
                                var("KeyValue", mu.KEY_TYPE), var("NoKey", mu.KEY_TYPE), var("Capturing", "bool"),   # NoKey: never set - the empty key
                                var("PressPart", "string")],   # the part pressed and not yet released
                     functions=[fn("Init", [param("field", "struct:" + mu.FIELD_STRUCT)], graph=g),
                                fn("Slider Value", [param("pos", "float")], [param("value", "float")], graph=sv, pure=True),
                                fn("Slider Pos", [param("value", "float")], [param("pos", "float")], graph=sp, pure=True),
                                fn("Update Text", graph=ut), fn("Set Value", [param("value", "float")], graph=sv2), fn("Set Enabled", [param("yes", "bool")], graph=se),
                                fn("Set Color", [param("color", S_LINCOLOR)], graph=sc), fn("Set Text", [param("text", "string")], graph=st),
                                fn("Report", [param("value", "float")], graph=rp), compute_fn(c),
                                fn("Set Key", [param("pressed", mu.KEY_TYPE)], graph=sk), fn("Mark Press", [param("part", "string")], graph=mp), fn("Set Capturing", [param("on", "bool")], graph=scp), fn("Update Key Text", graph=uk),
                                fn("Tick", override=True, graph=tk), fn("OnMouseButtonDown", override=True, graph=md), fn("OnMouseButtonUp", override=True, graph=mu_),
                                fn("OnMouseCaptureLost", override=True, graph=cl), fn("Step Choice", [param("dir", "int")], graph=sch), fn("Step Number", [param("sign", "float")], graph=snm), keep_typing_fn("Edit")],
                     widget_tree=tree, defaults=HAND)


# ---------------- W_FaceRow (one entry of the face tab: tick = own value / off = the game's animation, slider, value) ----------------
W_FACEROW = M + "/W_FaceRow"


def w_face_row():
    """Checkbox and slider polled in Tick like W_ModField. Moving the slider ticks the box; every change goes to
    Manager.Face Row Changed(key, fixed, value). Fixed/Value are what the manager set last or what was reported last,
    so neither side echoes the other. Value 0..1, a bipolar row (gaze) -1..1 with the slider centre at 0."""
    vc = {"VerticalAlignment": "VAlign_Center"}
    tree = w(E_BORDER, "Bg", props={"BrushColor": COL_NONE, "Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(6), sz(6))}, children=[
        w(U_HBOX, "Row", children=[
            sizebox("CheckWrap", 34, 34, [w(U_SCALE, "CheckScale", props={"Stretch": "ScaleToFit"}, children=[w(E_CHECK, "Check", props={"WidgetStyle": check_style(CHECK_SIZE)})])], slot=vc),
            sizebox("LabelBox", 240, 24, [text("Label", "Face", 13, slot=vc)], slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(8)}),
            # slider fills (120..360), the value keeps its room: fixed widths pushed the value past the right edge (game test 2026-10-03)
            w(U_SIZE, "SldBox", props={"bOverride_MinDesiredWidth": True, "MinDesiredWidth": sz(120), "bOverride_MaxDesiredWidth": True, "MaxDesiredWidth": sz(360),
                                       "bOverride_HeightOverride": True, "HeightOverride": sz(24)}, slot=dict(vc, Size="(SizeRule=Fill,Value=1)"),
              children=[w(E_SLIDER, "Sld", props={"Value": 0.0, "StepSize": 0.01, "SliderBarColor": "(R=0.35,G=0.42,B=0.55,A=1)", "SliderHandleColor": "(R=1,G=1,B=1,A=1)",
                                                  "WidgetStyle": "(BarThickness=5.0)"})]),
            sizebox("ValBox", 90, 24, [text("ValText", "", 12, GREY, slot=vc)], slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(10)})])])
    # Init(key, caption, bipolar)
    g = G(); g.set("sk", "Key", inp={"Key": "@entry.key"}); g.set("sb", "Bipolar", inp={"Bipolar": "@entry.bipolar"})
    g.get("gl", "Label"); g.call("stl", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@entry.caption"})
    g.n("cc", "call_self", function="Compute Colors"); g.chain("entry", "sk", "sb", "stl", "cc")
    # Slider Pos(value) / Slider Value(pos): bipolar maps -1..1 onto the whole bar; values to 0.01
    sp = G(); sp.get("gb", "Bipolar"); sp.call("a1", K_MATH, "Add_FloatFloat", inp={"A": "@entry.value", "B": "1.0"}); sp.call("h", K_MATH, "Multiply_FloatFloat", inp={"A": "@a1.ReturnValue", "B": "0.5"})
    sp.call("sel", K_MATH, "SelectFloat", inp={"A": "@h.ReturnValue", "B": "@entry.value", "bPickA": "@gb.Bipolar"}); sp.link("sel.ReturnValue", "return.pos")
    sv = G(); sv.get("gb", "Bipolar"); sv.call("m2", K_MATH, "Multiply_FloatFloat", inp={"A": "@entry.pos", "B": "2.0"}); sv.call("s1", K_MATH, "Subtract_FloatFloat", inp={"A": "@m2.ReturnValue", "B": "1.0"})
    sv.call("sel", K_MATH, "SelectFloat", inp={"A": "@s1.ReturnValue", "B": "@entry.pos", "bPickA": "@gb.Bipolar"})
    sv.call("x100", K_MATH, "Multiply_FloatFloat", inp={"A": "@sel.ReturnValue", "B": "100.0"}); sv.call("rnd", K_MATH, "Round", inp={"A": "@x100.ReturnValue"})
    sv.call("rf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@rnd.ReturnValue"}); sv.call("d", K_MATH, "Divide_FloatFloat", inp={"A": "@rf.ReturnValue", "B": "100.0"}); sv.link("d.ReturnValue", "return.value")
    # Update Look: "N %" (bipolar with sign) or "game"; slider dimmed while the game decides
    ul = G(); ul.get("gv", "Value"); ul.call("x", K_MATH, "Multiply_FloatFloat", inp={"A": "@gv.Value", "B": "100.0"}); ul.call("r", K_MATH, "Round", inp={"A": "@x.ReturnValue"})
    ul.call("i2s", K_STR, "Conv_IntToString", inp={"InInt": "@r.ReturnValue"}); ul.call("pc", K_STR, "Concat_StrStr", inp={"A": "@i2s.ReturnValue", "B": " %"})
    ul.get("gb", "Bipolar"); ul.call("pos", K_MATH, "Greater_IntInt", inp={"A": "@r.ReturnValue", "B": "0"}); ul.call("sg", K_MATH, "BooleanAND", inp={"A": "@gb.Bipolar", "B": "@pos.ReturnValue"})
    ul.call("pl", K_STR, "Concat_StrStr", inp={"A": "+", "B": "@pc.ReturnValue"}); ul.call("ps", K_MATH, "SelectString", inp={"A": "@pl.ReturnValue", "B": "@pc.ReturnValue", "bPickA": "@sg.ReturnValue"})
    ul.get("gf", "Fixed"); ul.call("txt", K_MATH, "SelectString", inp={"A": "@ps.ReturnValue", "B": mts(ul, "tg", "Lbl_FaceGame"), "bPickA": "@gf.Fixed"})
    ul.call("t", K_TXT, "Conv_StringToText", inp={"InString": "@txt.ReturnValue"}); ul.get("gvt", "ValText"); ul.call("st", E_TEXT, "SetText", inp={"self": "@gvt.ValText", "InText": "@t.ReturnValue"})
    ul.call("op", K_MATH, "SelectFloat", inp={"A": "1.0", "B": "0.35", "bPickA": "@gf.Fixed"}); ul.get("gsb", "SldBox"); ul.call("ro", E_WIDGET, "SetRenderOpacity", inp={"self": "@gsb.SldBox", "InOpacity": "@op.ReturnValue"})
    ul.chain("entry", "st", "ro")
    # Set State(fixed, value): from the manager, or after a change of the player's
    ss = G(); ss.set("sf", "Fixed", inp={"Fixed": "@entry.fixed"}); ss.set("sv", "Value", inp={"Value": "@entry.value"})
    ss.get("gc", "Check"); ss.call("sc", E_CHECK, "SetIsChecked", inp={"self": "@gc.Check", "InIsChecked": "@entry.fixed"})
    ss.n("pos", "call_self", function="Slider Pos", inp={"value": "@entry.value"}); ss.get("gsl", "Sld"); ss.call("ssl", E_SLIDER, "SetValue", inp={"self": "@gsl.Sld", "InValue": "@pos.pos"})
    ss.n("ul", "call_self", function="Update Look"); ss.chain("entry", "sf", "sv", "sc", "ssl", "ul")
    # Tick: slider moved -> fixed with that value; else the box flipped -> fixed/free with the value as it is
    tk = G(); tk.get("gsl", "Sld"); tk.call("gsv", E_SLIDER, "GetValue", inp={"self": "@gsl.Sld"}); tk.n("sval", "call_self", function="Slider Value", inp={"pos": "@gsv.ReturnValue"})
    tk.get("gv", "Value"); tk.call("same", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@sval.value", "B": "@gv.Value", "ErrorTolerance": "0.006"})
    tk.get("gsw", "Switch"); tk.call("nomv", K_MATH, "BooleanOR", inp={"A": "@same.ReturnValue", "B": "@gsw.Switch"}); tk.branch("bm", "@nomv.ReturnValue")   # a switch row: only the box
    tk.n("s1", "call_self", function="Set State", inp={"fixed": "true", "value": "@sval.value"})
    tk.get("gc", "Check"); tk.call("ic", E_CHECK, "IsChecked", inp={"self": "@gc.Check"}); tk.get("gf", "Fixed")
    tk.call("flip", K_MATH, "NotEqual_BoolBool", inp={"A": "@ic.ReturnValue", "B": "@gf.Fixed"}); tk.branch("bc", "@flip.ReturnValue")
    tk.get("gv2", "Value"); tk.n("s2", "call_self", function="Set State", inp={"fixed": "@ic.ReturnValue", "value": "@gv2.Value"})
    tk.get("gm", "Manager"); tk.get("gk", "Key"); tk.get("gf2", "Fixed"); tk.get("gv3", "Value")
    tk.call("rep", MGR, "Face Row Changed", inp={"self": "@gm.Manager", "key": "@gk.Key", "fixed": "@gf2.Fixed", "value": "@gv3.Value"})
    tk.chain("entry", "bm", "bc", "s2", "rep"); tk.chain("bm:else", "s1", "rep")
    # Set Switch: a plain on/off row (mutation veins / eyes) - slider and value hidden (Hidden keeps the rows aligned), the box alone reports
    sw = G(); sw.set("ss", "Switch", inp={"Switch": "true"})
    sw.get("gsb", "SldBox"); sw.call("h1", E_WIDGET, "SetVisibility", inp={"self": "@gsb.SldBox", "InVisibility": "Hidden"})
    sw.get("gvt", "ValText"); sw.call("h2", E_WIDGET, "SetVisibility", inp={"self": "@gvt.ValText", "InVisibility": "Hidden"})
    sw.chain("entry", "ss", "h1", "h2")
    # colours
    c = G(); ct = ["entry"]
    text_color(c, "tl", "Label", mcol(c, "ctx", "ColText"), ct); text_color(c, "tv", "ValText", mcol(c, "cdim", "ColTextDim"), ct)
    c.get("gsl", "Sld"); c.call("sbc", E_SLIDER, "SetSliderBarColor", inp={"self": "@gsl.Sld", "InValue": mcol(c, "csl", "ColSlider")}); ct.append("sbc")
    c.chain(*ct)
    return blueprint(W_FACEROW, E_USERWIDGET,
                     variables=[var("Manager", "object:" + MGR), var("Key", "name"), var("Bipolar", "bool"), var("Fixed", "bool"), var("Value", "float"), var("Switch", "bool")],
                     functions=[fn("Init", [param("key", "name"), param("caption", "text"), param("bipolar", "bool")], graph=g),
                                fn("Slider Pos", [param("value", "float")], [param("pos", "float")], graph=sp, pure=True),
                                fn("Slider Value", [param("pos", "float")], [param("value", "float")], graph=sv, pure=True),
                                fn("Update Look", graph=ul), fn("Set State", [param("fixed", "bool"), param("value", "float")], graph=ss),
                                fn("Set Switch", graph=sw), compute_fn(c), fn("Tick", override=True, graph=tk)],
                     widget_tree=tree)


# ---------------- W_HairSwatch (natural hair colour: colour square, frame when it is the current colour, tooltip) ----------------
def w_hair_swatch():
    tree = sizebox("Box", 30, 30, [roundbox("Frame", COL_FRAME, 2, [roundbox("Fill", "(R=0.5,G=0.5,B=0.5,A=1)", 0, None)])])
    g = G(); g.set("sk", "Key", inp={"Key": "@entry.key"})
    g.get("gf", "Fill"); g.call("sb", E_BORDER, "SetBrushColor", inp={"self": "@gf.Fill", "InBrushColor": "@entry.color"})
    g.call("sel", K_MATH, "SelectColor", inp={"A": "(R=1,G=1,B=1,A=1)", "B": COL_FRAME, "bPickA": "@entry.selected"})
    g.get("gfr", "Frame"); g.call("sf", E_BORDER, "SetBrushColor", inp={"self": "@gfr.Frame", "InBrushColor": "@sel.ReturnValue"})
    g.call("gop", E_USERWIDGET, "GetOwningPlayer"); g.call("ctt", K_WBL, "Create", inp={"WidgetType": W_TOOLTIP, "OwningPlayer": "@gop.ReturnValue"}); g.cast("ctc", W_TOOLTIP, "@ctt.ReturnValue")
    g.get("gmt", "Manager"); g.n("stm", "set", var="Manager", cls=W_TOOLTIP, inp={"self": "@ctc.AsW_Tooltip", "Manager": "@gmt.Manager"})
    g.call("tti", W_TOOLTIP, "Init", inp={"self": "@ctc.AsW_Tooltip", "text": "@entry.tip"}); g.get("gb", "Box"); g.call("tt", E_WIDGET, "SetToolTip", inp={"self": "@gb.Box", "Widget": "@ctc.AsW_Tooltip"})
    g.chain("entry", "sk", "sb", "sf", "ctt", "stm", "tti", "tt")
    return blueprint(W_HSWATCH, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Key", "name")],
                     functions=[fn("Init", [param("key", "name"), param("color", S_LINCOLOR), param("tip", "text"), param("selected", "bool")], graph=g),
                                mouse_down_override("Hair Swatch Clicked", "Hair Swatch Clicked", "Key", pin="key")], widget_tree=tree, defaults=HAND)


# ---------------- W_AltUI (Panel) ----------------
BODY_ROWS = [("Breast", "Breast"), ("Waist", "Waist")]   # the game has no hip morph (Makeup_Save.Hip is an unused remnant)
SCALE_ROWS = [("Sc" + k, k) for k in bg.SLIDER_ORDER]   # bone-scale sliders (ABP_BodyScale), captions via Lbl_Sc<Key>; row order = SLIDER_ORDER
OPTION_ROWS = [("Scroll", "Scroll speed"), ("Scale", "Tile size"), ("OutfitScale", "Outfit tile size"), ("LookScale", "Look tile size"), ("RagScale", "Ragdoll tile size"), ("InvScale", "Inventory tile size"), ("OutfitCols", "Outfit pieces per row"), ("OutfitRows", "Outfit rows of pieces"), ("Fov", "Camera FOV (Jodi view)"), ("Dist", "Camera distance (Jodi view)"), ("Height", "Camera height (Jodi view)"), ("GroupLen", "Group names: max. characters"), ("ChipH", "Group chip area: max. height"),
               ("BgAlpha", "Background opacity"), ("TileAlpha", "Tile opacity"), ("QuickAlpha", "Quick menu opacity"), ("WalkSpeed", "Walk speed"), ("RunSpeed", "Run speed"), ("RagWheel", "Ragdoll lift per wheel notch"), ("SlowMo", "Slow motion speed"), ("BgImgAlpha", "Pattern opacity"), ("BgHue", "Hue"), ("BgSepia", "Sepia"), ("BtnHue", "Hue"), ("BtnSepia", "Sepia")]   # sliders of Get/Set Option Values (the last two sit in the theme block)
OPT_CATS = ["General", "Tiles", "Groups", "Camera", "Controls", "Move", "Quick", "Theme", "Conflicts", "Tabs"]   # Options page: left list (key = widget OptCat_<key>, text OptCat_<key>)
OPTION_ROWS_MAIN = 12   # the first rows sit in the options block, the rest below the theme grid
IMG_ROWS = ["BgImgAlpha", "BgHue", "BgSepia", "BtnHue", "BtnSepia"]   # ... except these: they sit with their picture (image block)
PANEL_TEXTS = [("search", "Search"), ("chipsearch", "ChipSearch"), ("onlyowned", "LblOwned"), ("onlyfav", "LblFav"), ("onlyvanilla", "LblVanilla"), ("onlyworn", "LblOnlyWorn"), ("favorites", "FavHeader"), ("all", "AllHeader"), ("listhint", "ListHint"),
               ("lookonlyfav", "LblLookFav"), ("lookonlyworn", "LblLookWorn"), ("lookfavorites", "LookFavHeader"), ("lookall", "LookAllHeader"),
               ("worn", "BagWornHeader"), ("inbag", "BagListHeader"), ("bagempty", "BagEmpty"), ("breast", "LblBreast"), ("waist", "LblWaist"),
               ("scbreast", "LblScBreast"), ("scwaist", "LblScWaist"), ("scglutes", "LblScGlutes"), ("scthighs", "LblScThighs"), ("sccalves", "LblScCalves"), ("scarms", "LblScArms"), ("schands", "LblScHands"), ("scfeet", "LblScFeet"), ("scheight", "LblScHeight"),
               ("scroll", "LblScroll"), ("scale", "LblScale"), ("quickalpha", "LblQuickAlpha"), ("outfitscale", "LblOutfitScale"), ("lookscale", "LblLookScale"), ("ragscale", "LblRagScale"), ("invscale", "LblInvScale"), ("outfitcols", "LblOutfitCols"), ("outfitrows", "LblOutfitRows"), ("fov", "LblFov"), ("dist", "LblDist"), ("height", "LblHeight"), ("grouplen", "LblGroupLen"), ("chiph", "LblChipH"), ("unlimited", "LblUnlimited"), ("layout", "LblLayout"),
               ("language", "LblLanguage"), ("placeholder", "PlaceholderText"), ("pan", "LblPan"), ("camright", "LblCamRight"), ("nude", "LblNude"), ("merge", "LblMerge"), ("mergemods", "LblMergeMods"), ("chipsearchopt", "LblChipSearch"), ("tipnoprefix", "LblTipNoPrefix"), ("tipnoids", "LblTipNoIds"), ("kodexall", "LblKodexAll"), ("moveon", "LblMoveOn"), ("walkspeed", "LblWalkSpeed"), ("runspeed", "LblRunSpeed"), ("walkstyle", "LblWalkStyle"), ("runstyle", "LblRunStyle"), ("idlestyle", "LblIdleStyle"), ("conflicts", "LblConflicts"), ("conflictshint", "LblConflictsHint"), ("multislots", "LblMultiSlots"), ("multislotshint", "LblMultiSlotsHint"), ("unowned", "LblUnowned"), ("scalehint", "LblScaleHint"),
               ("theme", "LblTheme"), ("bgalpha", "LblBgAlpha"), ("bgimgalpha", "LblBgImgAlpha"), ("tilealpha", "LblTileAlpha"), ("key", "LblKey"), ("onlymods", "LblOnlyMods"), ("casesens", "LblCaseSens"), ("managesearch", "ManageSearch"), ("looksearch", "LookSearch"), ("lookchipsearch", "LookChipSearch"), ("hdrname", "HdrName"), ("hdrdisplay", "HdrDisplay"), ("hdrorigin", "HdrOrigin"), ("hdrcontent", "HdrContent"), ("posesearch", "PoseSearch"), ("invsearch", "InvSearch"), ("posefavorites", "PoseFavHeader"), ("poseall", "PoseAllHeader"), ("weaponsearch", "WeaponSearch"), ("weaponfavorites", "WeaponFavHeader"), ("weaponall", "WeaponAllHeader"), ("weaponmodels", "WeaponModelHeader"), ("weaponsounds", "WeaponSoundHeader"), ("tabshint", "LblTabsHint"), ("quickkey", "LblQuickKey"), ("quickinwheel", "LblQuickInWheel"), ("quickavailable", "LblQuickAvailable"), ("tabstyle", "LblTabStyle"), ("tabiconpos", "LblTabIconPos"), ("tabrow", "LblTabRow"), ("bgimage", "LblBgImage"), ("bgfit", "LblBgFit"), ("bghalign", "LblBgHAlign"), ("bgvalign", "LblBgVAlign"), ("btnimage", "LblBtnImage"), ("bghue", "LblBgHue"), ("bgsepia", "LblBgSepia"), ("bginv", "LblBgInv"), ("imgthumbs", "LblImgThumbs"), ("btnhue", "LblBtnHue"), ("btnsepia", "LblBtnSepia"), ("btninv", "LblBtnInv"), ("themesave", "LblThemeSave"), ("themename", "ThemeNameEdit"), ("themepresets", "LblThemePresets"), ("themepresetshint", "ThemePresetsHint"), ("managechipsearch", "ManageChipSearch"), ("quickcontrol", "LblQuickControl"), ("quickkeywidth", "QuickKeyWidth"), ("invbag", "InvBagTitle"), ("folbag", "FolBagTitle"), ("folbox", "FolBoxTitle"), ("invbox", "InvBoxTitle"), ("invcat", "InvCatTitle"), ("invcatalog", "LblInvCatalog"), ("invautoequip", "LblInvAutoEquip"), ("weaponattach", "WeaponAttachHeader")]   # parameter of Set Strings -> widget name (order = gen_manager_ui.PANEL_STRINGS)
PANEL_TEXTS += [("sc" + k.lower(), "LblSc" + k) for k in bg.SLIDER_ORDER[9:]] + [("scgrp" + h[len("Lbl_ScGrp"):].lower(), "LblScGrp" + h[len("Lbl_ScGrp"):]) for h in bg.GROUP_HEADS.values()]   # 2026-10-09 body-physics rows + group headings
PANEL_TEXTS += [("ragwheel", "LblRagWheel"), ("slowmo", "LblSlowMo")]   # 2026-10-11 sliders
PANEL_TEXTS += [("hdr" + k.lower(), "Hdr" + k) for k in ("ThemeColors", "BgPic", "BtnPic", "ThemeSchemes")]   # 2026-10-16 Options > Theme sections
PANEL_TEXTS += [("slowmoon", "LblSlowMoOn")]
PANEL_TEXTS += [("freenocollide", "LblFreeNoCollide"), ("freenolimit", "LblFreeNoLimit")]   # 2026-10-16 free camera options
PANEL_TEXTS += [("nonotices", "LblNoNotices")]   # 2026-10-16 no notices at all   # 2026-10-16 free camera options   # 2026-10-12 slow motion on / off next to its slider
PANEL_TEXTS += [("hairfavorites", "HairFavHeader"), ("hairall", "HairAllHeader")]   # 2026-10-15 favourites block of the Coiffure tab
PANEL_TEXTS += [("keybinds", "LblKeyBinds")]   # 2026-10-15 own keys (Options › Quick menu)
THEME_COLS = 5   # theme grid: fixed columns (entries fill column-wise), the wrap box wraps whole columns on narrow panels
THEME_REFRESH = [("TopTabs", W_TOP), ("TabChips", W_SUB), ("QuickKeyLinks", W_TXT), ("LayoutChips", W_SUB), ("UnownedChips", W_SUB), ("ThemePresetChips", W_SUB), ("ManageChips", W_SUB), ("ManageChipSearchLinks", W_TXT), ("ThemeSaveLinks", W_TXT), ("TabStyleChips", W_SUB), ("TabIconPosChips", W_SUB), ("TabRowChips", W_SUB), ("BgImageChips", W_SUB), ("BgFitChips", W_SUB), ("BgHAlignChips", W_SUB), ("BgVAlignChips", W_SUB), ("BtnImageChips", W_SUB), ("BgInvChips", W_SUB), ("ImgThumbsChips", W_SUB), ("BtnInvChips", W_SUB), ("LangChips", W_SUB), ("KeyChips", W_SUB), ("MultiSlotChips", W_SUB), ("StatusLinks", W_TXT), ("StatusRight", W_TXT)] + [("ThemeCol%d" % i, W_SWATCH) for i in range(THEME_COLS)]
SUBTABS_MAX_H, SUBTABS_MAX_H_MAX = 112, 500   # default ~3.5 chip rows (80 showed 2.5); option range (unscaled units, x SC at runtime)
SCROLL_PAGES = ["LeftScroll", "SubTabsScroll", "BodyChipsScroll", "LookSubTabsScroll", "ManageSubTabsScroll", "ListScroll", "OutfitScroll", "LooksScroll", "ContentScroll", "BagScroll", "HairScroll", "LookCatScroll", "LookScroll", "OptionsScroll", "ManageCatScroll", "ManageScroll", "PoseCatScroll", "PoseSubTabsScroll", "PoseScroll", "WeaponCatScroll", "WeaponSubTabsScroll", "WeaponScroll", "FaceGroupScroll", "FaceScroll", "KodexCatScroll", "KodexScroll", "RagScroll", "InvBagScroll", "InvBoxScroll", "InvCatScroll", "FolBagScroll", "FolBoxScroll", "FolScroll"]
# panel-owned texts coloured by Apply Theme: widget -> derived colour
PANEL_TEXT_COLORS = {"ColHead": ["HdrThemeColors", "HdrBgPic", "HdrBtnPic", "HdrThemeSchemes", "FolBagTitle", "FolBoxTitle", "InvBagTitle", "InvBoxTitle", "InvCatTitle", "KodexTitle", "LblQuickControl", "LblQuickInWheel", "LblKeyBinds", "LblQuickAvailable", "BagWornHeader", "BagListHeader", "FavHeader", "LookFavHeader", "HairFavHeader", "PoseFavHeader", "WeaponFavHeader", "LblTheme", "ContentTitle", "LblConflicts", "LblMultiSlots"],
                     "ColTextDim": ["FolHint", "FolBagNote", "InvBagNote", "InvWeightText", "RagHint", "RagPresetsHint", "ModHint", "FaceHint", "LblTabsHint", "ThemePresetsHint", "LblQuickKeyHint", "KeyBindHint", "AllHeader", "LookAllHeader", "HairAllHeader", "PoseAllHeader", "WeaponAllHeader", "WeaponModelHeader", "ListHint", "BagEmpty", "PlaceholderText", "HdrName", "HdrDisplay", "HdrOrigin", "LblConflictsHint", "LblMultiSlotsHint", "LblScaleHint"] + ["Val" + k for k, _ in OPTION_ROWS] + ["Val" + k for k, _ in BODY_ROWS] + ["Val" + k for k, _ in SCALE_ROWS],
                     "ColText": ["KodexBody", "LblRagKinds", "LblRagSave", "LblRagPresets", "LblQuickKey", "LblOwned", "LblFav", "LblVanilla", "LblOnlyWorn", "LblLookFav", "LblLookWorn", "LblOnlyMods", "LblCaseSens", "LblUnlimited", "LblPan", "LblCamRight", "LblNude", "LblMerge", "LblMergeMods", "LblChipSearch", "LblTipNoPrefix", "LblTipNoIds", "LblKodexAll", "LblMoveOn", "LblWalkStyle", "LblRunStyle", "LblIdleStyle", "LblUnowned", "LblTabStyle", "LblTabIconPos", "LblThemeSave", "LblThemePresets", "LblLayout", "LblLanguage", "LblKey"] + ["Lbl" + k for k, _ in OPTION_ROWS] + ["Lbl" + k for k, _ in BODY_ROWS] + ["Lbl" + k for k, _ in SCALE_ROWS] + ["LblScGrp" + h[len("Lbl_ScGrp"):] for h in bg.GROUP_HEADS.values()]}


# Options page: which category block (OptCat_<key>) every row of the former single options list belongs to
OPT_CAT_ROWS = {"General": ["RowLanguage", "RowLayout", "RowNude", "RowUnowned", "RowKodexAll", "RowInvCatalog", "RowInvAutoEquip", "RowNoNotices"],
                "Tiles": ["RowScale", "RowOutfitScale", "RowLookScale", "RowRagScale", "RowInvScale", "RowOutfitCols", "RowOutfitRows", "RowUnlimited", "RowTipNoPrefix", "RowTipNoIds"],
                "Groups": ["RowMerge", "RowMergeMods", "RowGroupLen", "RowChipH", "RowChipSearch"],
                "Camera": ["RowFov", "RowDist", "RowHeight", "RowPan", "RowFreeNoCollide", "RowFreeNoLimit"],
                "Controls": ["RowKey", "RowScroll", "RowCamRight", "RowRagWheel"],
                "Move": ["RowMoveOn", "RowWalkSpeed", "RowRunSpeed", "RowWalkStyle", "RowRunStyle", "RowIdleStyle", "RowSlowMoOn", "RowSlowMo", "MoveLinks"],   # reset below everything it resets
                "Quick": ["LblQuickControl", "RowQuickKey", "RowQuickAlpha", "LblQuickInWheel", "QuickInWheel", "LblKeyBinds", "KeyBindHint", "KeyBinds", "LblQuickAvailable", "QuickAvailable"],
                "Theme": ["LblTheme", "SecThemeColors", "ThemeGrid", "RowBgAlpha", "RowTileAlpha",
                          "SecImgNote", "LblImgHint", "RowImgThumbs", "SecBgPic", "RowBgImage", "RowBgImgAlpha", "RowBgFit", "RowBgHAlign", "RowBgVAlign", "RowBgHue", "RowBgSepia", "RowBgInv",
                          "SecBtnPic", "RowBtnImage", "RowBtnHue", "RowBtnSepia", "RowBtnInv",
                          "SecThemeSchemes", "RowThemeSave", "RowThemePresets"],
                "Conflicts": ["LblConflicts", "LblConflictsHint", "ConflictLinks", "ConflictRows", "LblMultiSlots", "LblMultiSlotsHint", "MultiSlotChips"],
                "Tabs": ["RowTabStyle", "RowTabIconPos", "RowTabRow", "LblTabsHint", "TabChips"]}
OPT_CAT_TITLES = {"LblTheme", "LblConflicts"}   # former block headings: the left list names the category now


def theme_section(key, line=True, heading=True):
    """Options > Theme: a section heading (Hdr<key>, ColHead like the other headings) with a thin line above it (not on the first)."""
    # 2 units: 1 fell under a pixel at the panel scale and came and went with the scroll position (ui-test-105)
    kids = ([sizebox("SecLine%sBox" % key, 10, 2, [w(E_BORDER, "SecLine" + key, props={"BrushColor": "(R=1,G=1,B=1,A=0.14)"})],
                     slot={"HorizontalAlignment": "HAlign_Fill", "Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(12)})] if line else []) + \
           ([text("Hdr" + key, key, 15, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))")] if heading else [])
    return w(U_VBOX, "Sec" + key, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(28), sz(10))}, children=kids)


def scroll_keep_fns():
    """Remember Scrolls / Restore Scrolls: the offsets of every page scroll box (SCROLL_PAGES) - a rebuild of a page clears its list and
    fills it anew, the scroll box would end at the top (Manager: KEEP_SCROLL wrappers). Restore only after a Remember (as many values)."""
    r = G(); r.get("gm", "ScrollMem"); r.call("cl", K_ARR, "Array_Clear", inp={"TargetArray": "@gm.ScrollMem"}); tail = ["entry", "cl"]
    for i, wn in enumerate(SCROLL_PAGES):
        r.get("g%d" % i, wn); r.call("o%d" % i, U_SCROLL, "GetScrollOffset", inp={"self": "@g%d.%s" % (i, wn)})
        r.get("m%d" % i, "ScrollMem"); r.call("a%d" % i, K_ARR, "Array_Add", inp={"TargetArray": "@m%d.ScrollMem" % i, "NewItem": "@o%d.ReturnValue" % i}); tail.append("a%d" % i)
    r.chain(*tail)
    s = G(); s.get("gm", "ScrollMem"); s.call("ln", K_ARR, "Array_Length", inp={"TargetArray": "@gm.ScrollMem"})
    s.call("ok", K_MATH, "EqualEqual_IntInt", inp={"A": "@ln.ReturnValue", "B": str(len(SCROLL_PAGES))}); s.branch("b", "@ok.ReturnValue"); tail = ["entry", "b"]
    for i, wn in enumerate(SCROLL_PAGES):
        s.get("m%d" % i, "ScrollMem"); s.call("v%d" % i, K_ARR, "Array_Get", inp={"TargetArray": "@m%d.ScrollMem" % i, "Index": str(i)})
        s.get("g%d" % i, wn); s.call("s%d" % i, U_SCROLL, "SetScrollOffset", inp={"self": "@g%d.%s" % (i, wn), "NewScrollOffset": "@v%d.Item" % i}); tail.append("s%d" % i)
    s.chain(*tail)
    return [fn("Remember Scrolls", graph=r), fn("Restore Scrolls", graph=s)]


def thumb_filters_fn(name, box):
    """Hue / sepia / invert onto the previews of one picture row (the slider moves, the chips follow without being rebuilt)."""
    g = G(); g.get("gb", box); g.call("ch", U_PANELW, "GetAllChildren", inp={"self": "@gb.%s" % box}); g.foreach("fe", "@ch.ReturnValue")
    g.cast("cs", W_SUB, "@fe.Array Element"); g.call("vs", K_SYS, "IsValid", inp={"Object": "@cs.AsW_SubTab"}); g.branch("bv", "@vs.ReturnValue")
    g.call("st", W_SUB, "Set Thumb Filters", inp={"self": "@cs.AsW_SubTab", "hue": "@entry.hue", "sepia": "@entry.sepia", "invert": "@entry.invert"})
    g.chain("entry", "fe"); g.chain("fe", "bv", "st")
    return fn(name, [param("hue", "float"), param("sepia", "float"), param("invert", "float")], graph=g)


def options_page(rows):
    """Options: category list on the left (OptionCats, W_SlotTab rows), on the right one VBox OptCat_<key> per category holding its rows
    (OPT_CAT_ROWS order); only General is visible at first (Set Option Cat switches). The first row of a block loses its top padding."""
    by_name = {r["name"]: r for r in rows}
    assert sorted(by_name) == sorted(n for v in OPT_CAT_ROWS.values() for n in v), "options row without a category"
    blocks = []
    for cat in OPT_CATS:
        kids = [by_name[n] for n in OPT_CAT_ROWS[cat]]
        for k in kids:
            if k["name"] in OPT_CAT_TITLES: k.setdefault("props", {})["Visibility"] = "Collapsed"
        first = next(k for k in kids if k["name"] not in OPT_CAT_TITLES)
        if "Padding" in first.get("slot", {}): first["slot"] = dict(first["slot"], Padding=re.sub(r"Top=[0-9.]+", "Top=0", first["slot"]["Padding"]))
        blocks.append(w(U_VBOX, "OptCat_" + cat, props={} if cat == OPT_CATS[0] else {"Visibility": "Collapsed"}, children=kids))
    return w(U_HBOX, "OptionsHB", props={"Visibility": "Collapsed"}, slot=FILL, children=[
        sizebox("OptLeftSize", 300, 100, [w(U_SCROLL, "OptionsCatScroll", props={"WheelScrollMultiplier": 2.0}, children=[w(U_VBOX, "OptionCats")])],
                slot={"Size": "(SizeRule=Automatic)", "VerticalAlignment": "VAlign_Fill", "Padding": "(Left=0,Top=0,Right=30,Bottom=0)"}),
        w(U_SCROLL, "OptionsScroll", props={"WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "OptionsBox", children=blocks)])])


OPT_LBL_W = 300   # Options: label column of slider and chip rows
BODY_LBL_W = 265   # Body Shape: label column, the longest caption is ~258 (ru "Угол (при меньшем колыхании)", Roboto 13, measured 2026-10-10)
OPT_CHIP_WRAP = {"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(8), sz(6))}   # Options chip rows wrap onto more lines when the page is narrow
OPT_CHIP_SLOT = {"Size": "(SizeRule=Fill,Value=1)", "VerticalAlignment": "VAlign_Top"}


def slider_box(key, fill):
    """Slider box: fixed 420 wide (Body page), or with fill the rest of the row, at least 120 (Options: the width follows the page)."""
    if not fill: return lambda children, slot: sizebox("Sld%sBox" % key, 420, 24, children, slot=slot)
    return lambda children, slot: w(U_SIZE, "Sld%sBox" % key, props={"bOverride_MinDesiredWidth": True, "MinDesiredWidth": sz(120), "bOverride_HeightOverride": True, "HeightOverride": sz(24)},
                                    slot=dict(slot, Size="(SizeRule=Fill,Value=1)"), children=children)


def body_row(key, caption, lbl_w=120, fill=False):
    return w(U_HBOX, "Row" + key, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(6), sz(6))}, children=[
        sizebox("Lbl%sBox" % key, lbl_w, 24, [text("Lbl" + key, caption, 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Center"}),
        slider_box(key, fill)([w(E_SLIDER, "Sld" + key, props={"Value": 0.5, "StepSize": 0.01, "SliderBarColor": "(R=0.35,G=0.42,B=0.55,A=1)", "SliderHandleColor": "(R=1,G=1,B=1,A=1)",
                                              "WidgetStyle": "(BarThickness=5.0)"})],   # the engine default of 2 px drops below 1 px at panel scale ~0.4 and is not rasterised on some rows
                slot={"VerticalAlignment": "VAlign_Center"}),
        sizebox("Val%sBox" % key, 70, 24, [text("Val" + key, "50 %", 12, GREY, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(10)}),
    ])


def round_btn(name, top):
    return w(W_ROUND, name, props={"Visibility": "Collapsed"},
             slot={"LayoutData": "(Anchors=(Minimum=(X=0,Y=1),Maximum=(X=0,Y=1)),Offsets=(Left=%d,Top=%d,Right=%d,Bottom=%d),Alignment=(X=1,Y=1))" % (-sz(10.5), -top, BTN_R, BTN_R), "ZOrder": 5})


SEARCH_STYLE = "(Font=(Size=%d),Padding=(Left=%d,Top=%d,Right=%d,Bottom=%d),BackgroundColor=(SpecifiedColor=(R=0,G=0,B=0,A=0)),ForegroundColor=(SpecifiedColor=(R=1,G=1,B=1,A=1)))" % (sz(SEARCH_FONT), sz(10), sz(SEARCH_PAD), sz(10), sz(SEARCH_PAD))


def set_hint_fn(name, widget):
    """<name>(text): a note text block; empty text hides it."""
    g = G(); g.get("gh", widget); g.call("st", E_TEXT, "SetText", inp={"self": "@gh." + widget, "InText": "@entry.text"})
    g.call("em", K_TXT, "TextIsEmpty", inp={"InText": "@entry.text"}); g.branch("b", "@em.ReturnValue")
    g.get("gh2", widget); g.call("hd", E_WIDGET, "SetVisibility", inp={"self": "@gh2." + widget, "InVisibility": "Collapsed"})
    g.get("gh3", widget); g.call("sh", E_WIDGET, "SetVisibility", inp={"self": "@gh3." + widget, "InVisibility": "Visible"})
    g.chain("entry", "st", "b", "hd"); g.chain("b:else", "sh")
    return fn(name, [param("text", "text")], graph=g)


def set_mod_hint():
    """Set Mod Hint(text): the note above the fields of the Mods page (actor missing, no fields); empty text hides it."""
    g = G(); g.get("gh", "ModHint"); g.call("st", E_TEXT, "SetText", inp={"self": "@gh.ModHint", "InText": "@entry.text"})
    g.call("em", K_TXT, "TextIsEmpty", inp={"InText": "@entry.text"}); g.branch("b", "@em.ReturnValue")
    g.get("gh2", "ModHint"); g.call("hd", E_WIDGET, "SetVisibility", inp={"self": "@gh2.ModHint", "InVisibility": "Collapsed"})
    g.get("gh3", "ModHint"); g.call("sh", E_WIDGET, "SetVisibility", inp={"self": "@gh3.ModHint", "InVisibility": "Visible"})
    g.chain("entry", "st", "b", "hd"); g.chain("b:else", "sh")
    return fn("Set Mod Hint", [param("text", "text")], graph=g)


def w_panel():
    tree = w(U_CANVAS, "Root", children=[
        # Jodi drag: transparent catcher over the free area (Set Left Free anchors it 0..fraction); clicks on Jodi start the drag, everything else bubbles to the viewport
        w(E_BORDER, "JodiCatcher", props={"BrushColor": "(R=0,G=0,B=0,A=0)", "Visibility": "Collapsed"},
          slot={"LayoutData": "(Anchors=(Minimum=(X=0,Y=0),Maximum=(X=0,Y=1)),Offsets=(Left=0,Top=0,Right=0,Bottom=0))", "ZOrder": 0}),
        round_btn("BtnPhoto", sz(10.5) + 4 * (BTN_R + sz(5))), round_btn("BtnCam", sz(10.5) + 3 * (BTN_R + sz(5))), round_btn("BtnRag", sz(10.5) + 2 * (BTN_R + sz(5))),   # Ragdolls mode right under the free camera
        round_btn("BtnPlus", sz(10.5) + BTN_R + sz(5)), round_btn("BtnMinus", sz(10.5)),
        # background image (Options > Theme): under Bg, which goes transparent while it shows; same anchors as Bg (Set Left Free)
        w(U_OVERLAY, "BgImgLayer", props={"Clipping": "ClipToBounds", "Visibility": "Collapsed"}, slot=FULL, children=[
            w(U_SCALE, "BgScale", props={"Stretch": "ScaleToFill"}, slot={"HorizontalAlignment": "HAlign_Fill", "VerticalAlignment": "VAlign_Fill"},
              children=[w(E_IMAGE, "BgImage")]),
            w(E_IMAGE, "BgTile", props={"Visibility": "Collapsed"}, slot={"HorizontalAlignment": "HAlign_Fill", "VerticalAlignment": "VAlign_Fill"})]),
        w(E_BORDER, "Bg", props={"BrushColor": COL_BG, "Padding": "(Left=46,Top=30,Right=46,Bottom=46)"}, slot=FULL, children=[
          w(U_VBOX, "Main", children=[
            # tabs wrap into a second row when the panel is narrow (half-width layouts do not fit ten tabs)
            w(U_WRAP, "TopTabs", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(4) + 1, sz(4) + 1)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(10)}),
            # virtual: only the rows in view hold tiles; OutfitTop / OutfitBottom stand in for the rows above and below (Outfit Window Update)
            w(U_SCROLL, "OutfitScroll", props={"Visibility": "Collapsed", "WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "OutfitVB", children=[
                w(U_SIZE, "OutfitTop", props={"bOverride_HeightOverride": True, "HeightOverride": 0}),
                w(U_VBOX, "OutfitList"),
                w(U_SIZE, "OutfitBottom", props={"bOverride_HeightOverride": True, "HeightOverride": 0}), w(U_SIZE, "OutfitBottomRoom", props={"bOverride_HeightOverride": True, "HeightOverride": LIST_ROOM})])]),
            w(U_SCROLL, "LooksScroll", props={"Visibility": "Collapsed", "WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_WRAP, "LooksList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)})]),
            # content view (outfit / preset / look): back link + title, sections below
            w(U_VBOX, "ContentBox", props={"Visibility": "Collapsed"}, slot=FILL, children=[
                w(U_HBOX, "ContentHead", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(8)}, children=[
                    w(U_HBOX, "ContentLinks", slot={"VerticalAlignment": "VAlign_Center"}),
                    text("ContentTitle", "", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(12)})]),
                w(U_SCROLL, "ContentScroll", props={"WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "ContentList")])]),
            w(U_SCROLL, "PlaceholderScroll", props={"Visibility": "Collapsed"}, slot=FILL, children=[text("PlaceholderText", "This tab is not finished yet.", 13, GREY)]),
            # Coiffure: link row (hair colour) + tiles
            w(U_SCROLL, "HairScroll", props={"Visibility": "Collapsed", "WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "HairVB", children=[
                w(U_HBOX, "HairLinks", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(8)}),
                w(U_WRAP, "HairSwatches", props={"Visibility": "Collapsed", "InnerSlotPadding": "(X=%d,Y=%d)" % (sz(4) + 1, sz(4) + 1)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(8)}),
                text("HairFavHeader", "Favourites", 13, "(SpecifiedColor=(R=0.95,G=0.8,B=0.3,A=1))", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=8)"}),
                w(U_WRAP, "HairFavList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=23)"}),
                text("HairAllHeader", "All", 13, "(SpecifiedColor=(R=0.7,G=0.7,B=0.7,A=1))", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=8)"}),
                w(U_WRAP, "HairList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)})])]),
            # Poses: mod chips + search + link row ("stop") + tiles (favourites block, all) - the right half of the appearance page without the favourites checkbox
            # Poses: categories on the left (measured height class / motion), chips + search + tiles on the right
            w(U_HBOX, "PoseHB", props={"Visibility": "Collapsed"}, slot=FILL, children=[
                sizebox("PoseLeftSize", 300, 100, [w(U_SCROLL, "PoseCatScroll", props={"WheelScrollMultiplier": 2.0}, children=[w(U_VBOX, "PoseCats")])],
                        slot={"Size": "(SizeRule=Automatic)", "VerticalAlignment": "VAlign_Fill", "Padding": "(Left=0,Top=0,Right=30,Bottom=0)"}),
                w(U_VBOX, "PoseRight", slot=FILL, children=[
                    w(U_SIZE, "PoseSubTabsBox", props={"bOverride_MaxDesiredHeight": True, "MaxDesiredHeight": sz(SUBTABS_MAX_H)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=15)"}, children=[
                        w(U_SCROLL, "PoseSubTabsScroll", props={"WheelScrollMultiplier": 2.0}, children=[
                            w(U_WRAP, "PoseSubTabs", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(4) + 1, sz(4) + 1)})])]),
                    w(U_HBOX, "PoseFilters", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=15)"}, children=[
                        roundbox("PSearchFrame", COL_CHIP_FRAME, 1, slot=FILL, children=[roundbox("PSearchFill", COL_CHIP, 0, children=[w(U_HBOX, "PSearchHB", children=[
                            w(E_EDIT, "PoseSearch", props={"HintText": "Search...", "WidgetStyle": SEARCH_STYLE}, slot=FILL),
                            w(U_HBOX, "PoseSearchLinks", slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(4)})])])])]),
                    w(U_HBOX, "PoseLinks", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(8)}),
                    w(U_SCROLL, "PoseScroll", props={"WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "PoseVB", children=[
                        text("PoseFavHeader", "Favourites", 13, "(SpecifiedColor=(R=0.95,G=0.8,B=0.3,A=1))", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=8)"}),
                        w(U_WRAP, "PoseFavList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=23)"}),
                        text("PoseAllHeader", "All", 13, "(SpecifiedColor=(R=0.7,G=0.7,B=0.7,A=1))", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=8)"}),
                        w(U_WRAP, "PoseList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)})])])])]),
            # Appearance: categories on the left, tiles on the right
            w(U_HBOX, "LookHB", props={"Visibility": "Collapsed"}, slot=FILL, children=[
                sizebox("LookLeftSize", 300, 100, [w(U_SCROLL, "LookCatScroll", props={"WheelScrollMultiplier": 2.0}, children=[w(U_VBOX, "LookCats")])],
                        slot={"Size": "(SizeRule=Automatic)", "VerticalAlignment": "VAlign_Fill", "Padding": "(Left=0,Top=0,Right=30,Bottom=0)"}),
                w(U_VBOX, "LookRight", slot=FILL, children=[
                    # a search of its own, only for the mod chips, above the chip row
                    w(U_HBOX, "LookChipSearchRow", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(8)}, children=[
                        roundbox("LCSearchFrame", COL_CHIP_FRAME, 1, slot=FILL, children=[roundbox("LCSearchFill", COL_CHIP, 0, children=[w(U_HBOX, "LCSearchHB", children=[
                            w(E_EDIT, "LookChipSearch", props={"HintText": "Search...", "WidgetStyle": SEARCH_STYLE}, slot=FILL),
                            w(U_HBOX, "LookChipSearchLinks", slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(4)})])])])]),
                    # mod chips (Vanilla, one per mod, Hidden) like the group chips of the clothes page; hidden for presets
                    w(U_SIZE, "LookSubTabsBox", props={"bOverride_MaxDesiredHeight": True, "MaxDesiredHeight": sz(SUBTABS_MAX_H)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=15)"}, children=[
                        w(U_SCROLL, "LookSubTabsScroll", props={"WheelScrollMultiplier": 2.0}, children=[
                            w(U_WRAP, "LookSubTabs", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(4) + 1, sz(4) + 1)})])]),
                    # search above the tiles (same box as the clothes page: frame, field, x link) + "only favourites"
                    w(U_HBOX, "LookFilters", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=15)"}, children=[
                        roundbox("LSearchFrame", COL_CHIP_FRAME, 1, slot=FILL, children=[roundbox("LSearchFill", COL_CHIP, 0, children=[w(U_HBOX, "LSearchHB", children=[
                            w(E_EDIT, "LookSearch", props={"HintText": "Search...", "WidgetStyle": SEARCH_STYLE}, slot=FILL),
                            w(U_HBOX, "LookSearchLinks", slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(4)})])])]),
                        sizebox("LookFavBox", 34, 34, [w(U_SCALE, "LookFavScale", props={"Stretch": "ScaleToFit"}, children=[w(E_CHECK, "LookOnlyFav", props={"WidgetStyle": check_style(CHECK_SIZE)})])],
                                slot={"Padding": "(Left=30,Top=0,Right=10,Bottom=0)", "VerticalAlignment": "VAlign_Center"}),
                        text("LblLookFav", "only\nfavourites", 11, slot={"VerticalAlignment": "VAlign_Center"}),
                        sizebox("LookWornBox", 34, 34, [w(U_SCALE, "LookWornScale", props={"Stretch": "ScaleToFit"}, children=[w(E_CHECK, "LookOnlyWorn", props={"WidgetStyle": check_style(CHECK_SIZE)})])],
                                slot={"Padding": "(Left=30,Top=0,Right=10,Bottom=0)", "VerticalAlignment": "VAlign_Center"}),
                        text("LblLookWorn", "only\nworn", 11, slot={"VerticalAlignment": "VAlign_Center"})]),
                    w(U_SCROLL, "LookScroll", props={"WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "LookVB", children=[
                        w(U_VBOX, "LookRowList"),   # the mutation entry's rows (W_FaceRow) and its reset link
                        text("LookFavHeader", "Favourites", 13, "(SpecifiedColor=(R=0.95,G=0.8,B=0.3,A=1))", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=8)"}),
                        w(U_WRAP, "LookFavList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=23)"}),
                        text("LookAllHeader", "All", 13, "(SpecifiedColor=(R=0.7,G=0.7,B=0.7,A=1))", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=8)"}),
                        w(U_WRAP, "LookList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)})])])])]),
            # Mods: the entries other mods registered on the left, the fields of the chosen one on the right (W_ModField rows)
            w(U_HBOX, "ModsHB", props={"Visibility": "Collapsed"}, slot=FILL, children=[
                sizebox("ModsLeftSize", 300, 100, [w(U_SCROLL, "ModEntryScroll", props={"WheelScrollMultiplier": 2.0}, children=[w(U_VBOX, "ModEntries")])],
                        slot={"Size": "(SizeRule=Automatic)", "VerticalAlignment": "VAlign_Fill", "Padding": "(Left=0,Top=0,Right=30,Bottom=0)"}),
                w(U_VBOX, "ModsRight", slot=FILL, children=[
                    text("ModHint", "", 13, GREY, wrap=True, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(10)}),
                    w(U_SCROLL, "ModFieldScroll", props={"WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "ModFieldList")])])]),
            # Face: groups on the left (expression / gaze / mouth / saved faces), on the right the links, a note and the rows or the saved-face tiles
            w(U_HBOX, "FaceHB", props={"Visibility": "Collapsed"}, slot=FILL, children=[
                sizebox("FaceLeftSize", 300, 100, [w(U_SCROLL, "FaceGroupScroll", props={"WheelScrollMultiplier": 2.0}, children=[w(U_VBOX, "FaceGroups")])],
                        slot={"Size": "(SizeRule=Automatic)", "VerticalAlignment": "VAlign_Fill", "Padding": "(Left=0,Top=0,Right=30,Bottom=0)"}),
                w(U_VBOX, "FaceRight", slot=FILL, children=[
                    w(U_HBOX, "FaceLinks", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(8)}),
                    text("FaceHint", "", 13, GREY, wrap=True, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(10)}),
                    w(U_SCROLL, "FaceScroll", props={"WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "FaceVB", children=[
                        w(U_VBOX, "FaceRowList"),
                        w(U_WRAP, "FaceTiles", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)})])])])]),
            # Weapons: the weapons on the left, the skins of the selected one on the right (chips per mod, search, favourites)
            w(U_HBOX, "WeaponHB", props={"Visibility": "Collapsed"}, slot=FILL, children=[
                sizebox("WeaponLeftSize", 300, 100, [w(U_SCROLL, "WeaponCatScroll", props={"WheelScrollMultiplier": 2.0}, children=[w(U_VBOX, "WeaponCats")])],
                        slot={"Size": "(SizeRule=Automatic)", "VerticalAlignment": "VAlign_Fill", "Padding": "(Left=0,Top=0,Right=30,Bottom=0)"}),
                w(U_VBOX, "WeaponRight", slot=FILL, children=[
                    w(U_SIZE, "WeaponSubTabsBox", props={"bOverride_MaxDesiredHeight": True, "MaxDesiredHeight": sz(SUBTABS_MAX_H)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=15)"}, children=[
                        w(U_SCROLL, "WeaponSubTabsScroll", props={"WheelScrollMultiplier": 2.0}, children=[
                            w(U_WRAP, "WeaponSubTabs", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(4) + 1, sz(4) + 1)})])]),
                    w(U_HBOX, "WeaponFilters", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=15)"}, children=[
                        roundbox("WSearchFrame", COL_CHIP_FRAME, 1, slot=FILL, children=[roundbox("WSearchFill", COL_CHIP, 0, children=[w(U_HBOX, "WSearchHB", children=[
                            w(E_EDIT, "WeaponSearch", props={"HintText": "Search...", "WidgetStyle": SEARCH_STYLE}, slot=FILL),
                            w(U_HBOX, "WeaponSearchLinks", slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(4)})])])])]),
                    w(U_SCROLL, "WeaponScroll", props={"WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "WeaponVB", children=[
                        # one scroll area: the attachments (one section per slot, chips), the shot sounds as text buttons (they wrap), then the model tiles, then the skin tiles
                        text("WeaponAttachHeader", "Attachments", 13, "(SpecifiedColor=(R=0.7,G=0.7,B=0.7,A=1))", props_extra={"Visibility": "Collapsed"}),
                        w(U_VBOX, "WeaponAttachList", props={"Visibility": "Collapsed"}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=19)"}),
                        text("WeaponSoundHeader", "Sound", 13, "(SpecifiedColor=(R=0.7,G=0.7,B=0.7,A=1))", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=8)"}),
                        w(U_WRAP, "WeaponSoundList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(4) + 1, sz(4) + 1)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=19)"}),
                        text("WeaponModelHeader", "Model", 13, "(SpecifiedColor=(R=0.7,G=0.7,B=0.7,A=1))", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=8)"}),
                        w(U_WRAP, "WeaponModelList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=23)"}),
                        text("WeaponFavHeader", "Favourites", 13, "(SpecifiedColor=(R=0.95,G=0.8,B=0.3,A=1))", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=8)"}),
                        w(U_WRAP, "WeaponFavList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=23)"}),
                        text("WeaponAllHeader", "All", 13, "(SpecifiedColor=(R=0.7,G=0.7,B=0.7,A=1))", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=8)"}),
                        w(U_WRAP, "WeaponList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)})])])])]),
            # Manage (custom names): categories on the left, name rows on the right, search + "only mods" above the rows
            w(U_HBOX, "ManageHB", props={"Visibility": "Collapsed"}, slot=FILL, children=[
                sizebox("ManageLeftSize", 300, 100, [w(U_SCROLL, "ManageCatScroll", props={"WheelScrollMultiplier": 2.0}, children=[w(U_VBOX, "ManageCats")])],
                        slot={"Size": "(SizeRule=Automatic)", "VerticalAlignment": "VAlign_Fill", "Padding": "(Left=0,Top=0,Right=30,Bottom=0)"}),
                w(U_VBOX, "ManageRight", slot=FILL, children=[
                    # Clothes / Appearance / Poses: chip search + group / mod chips like on their own tabs (Rebuild Manage Chips; collapsed elsewhere)
                    w(U_HBOX, "ManageChipSearchRow", props={"Visibility": "Collapsed"}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(8)}, children=[
                        roundbox("MCSearchFrame", COL_CHIP_FRAME, 1, slot=FILL, children=[roundbox("MCSearchFill", COL_CHIP, 0, children=[w(U_HBOX, "MCSearchHB", children=[
                            w(E_EDIT, "ManageChipSearch", props={"HintText": "Search...", "WidgetStyle": SEARCH_STYLE}, slot=FILL),
                            w(U_HBOX, "ManageChipSearchLinks", slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(4)})])])])]),
                    w(U_SIZE, "ManageSubTabsBox", props={"Visibility": "Collapsed", "bOverride_MaxDesiredHeight": True, "MaxDesiredHeight": sz(SUBTABS_MAX_H)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=15)"}, children=[
                        w(U_SCROLL, "ManageSubTabsScroll", props={"WheelScrollMultiplier": 2.0}, children=[
                            w(U_WRAP, "ManageChips", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(4) + 1, sz(4) + 1)})])]),
                    w(U_HBOX, "ManageFilters", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=15)"}, children=[
                        roundbox("MSearchFrame", COL_CHIP_FRAME, 1, slot=FILL, children=[roundbox("MSearchFill", COL_CHIP, 0, children=[w(U_HBOX, "MSearchHB", children=[
                            w(E_EDIT, "ManageSearch", props={"HintText": "Search...", "WidgetStyle": SEARCH_STYLE}, slot=FILL),
                            w(U_HBOX, "ManageSearchLinks", slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(4)})])])]),
                        sizebox("OnlyModsBox", 34, 34, [w(U_SCALE, "OnlyModsScale", props={"Stretch": "ScaleToFit"}, children=[w(E_CHECK, "OnlyMods", props={"WidgetStyle": check_style(CHECK_SIZE)})])],
                                slot={"Padding": "(Left=30,Top=0,Right=10,Bottom=0)", "VerticalAlignment": "VAlign_Center"}),
                        text("LblOnlyMods", "only\nmods", 11, slot={"VerticalAlignment": "VAlign_Center"}),
                        sizebox("CaseSensBox", 34, 34, [w(U_SCALE, "CaseSensScale", props={"Stretch": "ScaleToFit"}, children=[w(E_CHECK, "CaseSens", props={"WidgetStyle": check_style(CHECK_SIZE)})])],
                                slot={"Padding": "(Left=30,Top=0,Right=10,Bottom=0)", "VerticalAlignment": "VAlign_Center"}),
                        text("LblCaseSens", "case-\nsensitive", 11, slot={"VerticalAlignment": "VAlign_Center"})]),
                    # column headers (fixed above the scrolling rows): same fill weights as W_NameRow, hidden placeholders keep the widths of its links
                    w(U_HBOX, "ManageHead", slot={"Padding": "(Left=%d,Top=0,Right=%d,Bottom=%d)" % (sz(5), sz(5), sz(4))}, children=[
                        text("HdrName", "Default name", 11, GREY, slot=dict(FILL1, Padding="(Left=%d,Top=0,Right=%d,Bottom=0)" % (sz(ROW_PAD), sz(8)))),
                        text("HdrDisplay", "Display name", 11, GREY, slot=dict(FILL1, Padding="(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8))),
                        w(E_TEXT, "HdrRevert", props={"Text": "\u21ba", "Font": "(Size=%d)" % sz(14), "Visibility": "Hidden"}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(12)}),
                        text("HdrOrigin", "Identifiers", 11, GREY, slot=dict(FILL1, Padding="(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8))),
                        w(E_TEXT, "HdrContent", props={"Text": "View content", "Font": "(Size=%d)" % sz(11), "Visibility": "Hidden"}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(ROW_PAD)})]),
                    w(U_SCROLL, "ManageScroll", props={"WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "ManageRows")])])]),
            # Ragdolls: spawn / remove links, a hint while there are no figures, one W_LinkRow per figure (and per joint when opened)
            w(U_SCROLL, "RagScroll", props={"Visibility": "Collapsed", "WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "RagBox", children=[
                w(U_HBOX, "RagTop", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(12)}),
                # zombies / NPCs: one W_RagTile per base kind (picture from the encyclopedia, variant links in the tile)
                text("LblRagKinds", "", 13, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(6)}),
                w(U_WRAP, "RagKinds", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(10))}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(16)}),
                text("RagHint", "", 13, GREY, wrap=True, props_extra={"LineHeightPercentage": 1.5}, slot={"Padding": "(Left=0,Top=0,Right=%d,Bottom=%d)" % (sz(12), sz(12))}),
                w(U_VBOX, "RagRows"),
                # saved scenes of this level: a name + "save" (the same name overwrites), one chip per scene (click loads, right click: load / delete)
                w(U_HBOX, "RagSaveRow", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(24), sz(6))}, children=[
                    text("LblRagSave", "", 13, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(12)}),
                    sizebox("RagNameBox", 260, None, [w(E_EDIT, "RagNameEdit", props={"HintText": "", "WidgetStyle": EDIT_STYLE, "SelectAllTextWhenFocused": True})], slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(12)}),
                    w(U_HBOX, "RagSaveLinks", slot={"VerticalAlignment": "VAlign_Center"})]),
                text("LblRagPresets", "", 13, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(6), sz(6))}),
                w(U_WRAP, "RagPresetChips", props=OPT_CHIP_WRAP),
                text("RagPresetsHint", "", 11, GREY, wrap=True, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(4)})])]),
            # Kodex: sections on the left (manual chapters, encyclopedia, passwords), on the right one area the manager fills:
            # back link, title, picture, text, tiles, link rows (Rebuild Kodex shows what the section needs)
            w(U_HBOX, "KodexHB", props={"Visibility": "Collapsed"}, slot=FILL, children=[
                sizebox("KodexLeftSize", 300, 100, [w(U_SCROLL, "KodexCatScroll", props={"WheelScrollMultiplier": 2.0}, children=[w(U_VBOX, "KodexCats")])],
                        slot={"Size": "(SizeRule=Automatic)", "VerticalAlignment": "VAlign_Fill", "Padding": "(Left=0,Top=0,Right=30,Bottom=0)"}),
                w(U_SCROLL, "KodexScroll", props={"WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "KodexBox", children=[
                    w(U_HBOX, "KodexBack", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(8)}),
                    text("KodexTitle", "", 18, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(10)}),
                    sizebox("KodexImageBox", 320, 480, [w(E_IMAGE, "KodexImage")], slot={"HorizontalAlignment": "HAlign_Left", "Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(12)}),
                    text("KodexBody", "", 13, wrap=True, props_extra={"LineHeightPercentage": 1.5}, slot={"Padding": "(Left=0,Top=0,Right=%d,Bottom=%d)" % (sz(12), sz(12))}),
                    w(U_WRAP, "KodexTiles", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)}),
                    w(U_VBOX, "KodexLinks")])])]),
            # Body Shape: body chips (Standard + body mods) above the sliders
            w(U_VBOX, "BodyBox", props={"Visibility": "Collapsed"}, slot=FILL, children=[
                # body chips: at most the chip area height (Options › Groups, like the clothes groups), then the box scrolls (many body mods)
                w(U_SIZE, "BodyChipsBox", props={"bOverride_MaxDesiredHeight": True, "MaxDesiredHeight": sz(SUBTABS_MAX_H)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(14)}, children=[
                    w(U_SCROLL, "BodyChipsScroll", props={"WheelScrollMultiplier": 2.0}, children=[
                        w(U_WRAP, "BodyChips", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(4) + 1, sz(4) + 1)})])])] +
              [body_row(k, cap, BODY_LBL_W, fill=True) for k, cap in BODY_ROWS] + [body_row(k, cap, BODY_LBL_W, fill=True) for k, cap in SCALE_ROWS[:1]] +   # "Height" scales the component: every body
              [text("LblScaleHint", "", 11, GREY, wrap=True, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(4))})] +   # greyed-out rows need ABP_BodyScale (converted bodies)
              [x for k, cap in SCALE_ROWS[1:] for x in (
                  ([text("LblScGrp" + bg.GROUP_HEADS[cap][len("Lbl_ScGrp"):], "", 14, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(14), sz(2))})] if cap in bg.GROUP_HEADS else [])
                  + [body_row(k, cap, BODY_LBL_W, fill=True)])]),   # "Reset shape": status bar
            # Options: sliders (scroll speed, tile size, camera), checks, chips, theme block (scrollable: the theme block makes the page tall)
            options_page([body_row(k, cap, OPT_LBL_W, fill=True) for k, cap in OPTION_ROWS[:OPTION_ROWS_MAIN]] + [
                w(U_HBOX, "RowUnlimited", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    w(E_CHECK, "OptUnlimited", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblUnlimited", "show unlimited items at once", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowFreeNoCollide", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(14), sz(6))}, children=[
                    w(E_CHECK, "OptFreeNoCollide", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblFreeNoCollide", "Free camera: no collision", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowFreeNoLimit", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(0), sz(6))}, children=[
                    w(E_CHECK, "OptFreeNoLimit", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblFreeNoLimit", "Free camera: any distance from Jodi", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowPan", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    w(E_CHECK, "OptPan", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblPan", "Camera follows slot / face", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowCamRight", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(6)}, children=[
                    w(E_CHECK, "OptCamRight", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblCamRight", "Camera height with the right mouse button", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowMoveOn", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    w(E_CHECK, "OptMoveOn", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblMoveOn", "Own walk / run speed", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowSlowMoOn", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(14), sz(6))}, children=[
                    w(E_CHECK, "OptSlowMoOn", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblSlowMoOn", "Slow motion on", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "MoveLinks", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(10)}),
                *[w(U_HBOX, "Row%sStyle" % k, props={} if len(styles) > 1 else {"Visibility": "Collapsed"}, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(14), sz(6))}, children=[
                    sizebox("Lbl%sStyleBox" % k, OPT_LBL_W, 24, [text("Lbl%sStyle" % k, cap, 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_WRAP, "%sStyleChips" % k, props=OPT_CHIP_WRAP, slot=OPT_CHIP_SLOT)]) for k, cap, styles in (("Walk", "Walk style", gen_move.WALK_STYLES), ("Run", "Run style", gen_move.RUN_STYLES), ("Idle", "Standing", gen_move.IDLE_STYLES))],   # a row only with a choice
                w(U_HBOX, "RowNude", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    w(E_CHECK, "OptNude", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblNude", "Underwear may be taken off", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowMerge", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    w(E_CHECK, "OptMerge", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblMerge", "Merge groups with the same name", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowMergeMods", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(6)}, children=[
                    w(E_CHECK, "OptMergeMods", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblMergeMods", "Merge mods with the same name", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowChipSearch", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(6)}, children=[
                    w(E_CHECK, "OptChipSearch", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblChipSearch", "Show chip search", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowTipNoPrefix", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    w(E_CHECK, "OptTipNoPrefix", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblTipNoPrefix", "Tooltips without prefixes", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowNoNotices", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    w(E_CHECK, "OptNoNotices", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblNoNotices", "No notices", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowKodexAll", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    w(E_CHECK, "OptKodexAll", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblKodexAll", "Codex: show all encyclopedia entries", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowInvCatalog", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    w(E_CHECK, "OptInvCatalog", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblInvCatalog", "All-items catalogue in the Inventory tab", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowInvAutoEquip", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    w(E_CHECK, "OptInvAutoEquip", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblInvAutoEquip", "Auto-equip weapons", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowTipNoIds", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    w(E_CHECK, "OptTipNoIds", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblTipNoIds", "Tooltips: display names only", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                # ownership: not-owned mode chips (locked / greyed / like owned)
                w(U_HBOX, "RowUnowned", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    sizebox("LblUnownedBox", OPT_LBL_W, 24, [text("LblUnowned", "Not owned items", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_WRAP, "UnownedChips", props=OPT_CHIP_WRAP, slot=OPT_CHIP_SLOT)]),
                w(U_HBOX, "RowLayout", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    sizebox("LblLayoutBox", OPT_LBL_W, 24, [text("LblLayout", "Space for Jodi", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_WRAP, "LayoutChips", props=OPT_CHIP_WRAP, slot=OPT_CHIP_SLOT)]),
                w(U_HBOX, "RowLanguage", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    sizebox("LblLanguageBox", OPT_LBL_W, 24, [text("LblLanguage", "Language", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_WRAP, "LangChips", props=OPT_CHIP_WRAP, slot=OPT_CHIP_SLOT)]),
                w(U_HBOX, "RowKey", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    sizebox("LblKeyBox", OPT_LBL_W, 24, [text("LblKey", "Panel key", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_WRAP, "KeyChips", props=OPT_CHIP_WRAP, slot=OPT_CHIP_SLOT)]),
                # theme: heading, swatch grid (W_ColorSwatch per base colour), opacity sliders, reset link
                text("LblTheme", "Colours", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(16), sz(6))}),
                w(U_WRAP, "ThemeGrid", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(10) + 1, sz(6) + 1)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(18)},
                  children=[w(U_VBOX, "ThemeCol%d" % i) for i in range(THEME_COLS)])] +
                [body_row(k, cap, OPT_LBL_W, fill=True) for k, cap in OPTION_ROWS[OPTION_ROWS_MAIN:] if k not in IMG_ROWS] + [
                # background / button images (Rebuild Image Chips): built in + the user's own files, how the background fills and aligns
                w(U_HBOX, "RowImgThumbs", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(6), sz(6))}, children=[
                    sizebox("LblImgThumbsBox", OPT_LBL_W, 24, [text("LblImgThumbs", "Show previews", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_WRAP, "ImgThumbsChips", props=OPT_CHIP_WRAP, slot=OPT_CHIP_SLOT)]),
                w(U_HBOX, "RowBgImage", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(2), sz(6))}, children=[
                    sizebox("LblBgImageBox", OPT_LBL_W, 24, [text("LblBgImage", "Background image", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_WRAP, "BgImageChips", props=OPT_CHIP_WRAP, slot=OPT_CHIP_SLOT)]),
                body_row("BgImgAlpha", "Pattern opacity", OPT_LBL_W, fill=True),
                w(U_HBOX, "RowBgFit", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(6), sz(6))}, children=[
                    sizebox("LblBgFitBox", OPT_LBL_W, 24, [text("LblBgFit", "Image fill", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_WRAP, "BgFitChips", props=OPT_CHIP_WRAP, slot=OPT_CHIP_SLOT)]),
                w(U_HBOX, "RowBgHAlign", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(6), sz(6))}, children=[
                    sizebox("LblBgHAlignBox", OPT_LBL_W, 24, [text("LblBgHAlign", "Horizontal", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_WRAP, "BgHAlignChips", props=OPT_CHIP_WRAP, slot=OPT_CHIP_SLOT)]),
                w(U_HBOX, "RowBgVAlign", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(6), sz(6))}, children=[
                    sizebox("LblBgVAlignBox", OPT_LBL_W, 24, [text("LblBgVAlign", "Vertical", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_WRAP, "BgVAlignChips", props=OPT_CHIP_WRAP, slot=OPT_CHIP_SLOT)]),
                body_row("BgHue", "Hue", OPT_LBL_W, fill=True),
                body_row("BgSepia", "Sepia", OPT_LBL_W, fill=True),
                w(U_HBOX, "RowBgInv", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(6), sz(6))}, children=[
                    sizebox("LblBgInvBox", OPT_LBL_W, 24, [text("LblBgInv", "Invert", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_WRAP, "BgInvChips", props=OPT_CHIP_WRAP, slot=OPT_CHIP_SLOT)]),
                w(U_HBOX, "RowBtnImage", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(2), sz(6))}, children=[
                    sizebox("LblBtnImageBox", OPT_LBL_W, 24, [text("LblBtnImage", "Button image", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_WRAP, "BtnImageChips", props=OPT_CHIP_WRAP, slot=OPT_CHIP_SLOT)]),
                body_row("BtnHue", "Hue", OPT_LBL_W, fill=True),
                body_row("BtnSepia", "Sepia", OPT_LBL_W, fill=True),
                w(U_HBOX, "RowBtnInv", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(6), sz(6))}, children=[
                    sizebox("LblBtnInvBox", OPT_LBL_W, 24, [text("LblBtnInv", "Invert", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_WRAP, "BtnInvChips", props=OPT_CHIP_WRAP, slot=OPT_CHIP_SLOT)]),
                text("LblImgHint", "", 12, GREY, wrap=True, props_extra={"LineHeightPercentage": 1.35}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(4)}),
                theme_section("ThemeColors", False),
                theme_section("ImgNote", True, heading=False), theme_section("BgPic", False),
                theme_section("BtnPic", True),
                theme_section("ThemeSchemes", True),
                # saved colour schemes: a name + "save" (same name overwrites), then one chip per scheme (click applies, right click: apply / delete)
                w(U_HBOX, "RowThemeSave", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(18), sz(6))}, children=[
                    sizebox("LblThemeSaveBox", OPT_LBL_W, 24, [text("LblThemeSave", "Save scheme as", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Center"}),
                    sizebox("ThemeNameBox", 260, None, [w(E_EDIT, "ThemeNameEdit", props={"HintText": "", "WidgetStyle": EDIT_STYLE, "SelectAllTextWhenFocused": True})], slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(12)}),
                    w(U_HBOX, "ThemeSaveLinks", slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowThemePresets", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(6), sz(6))}, children=[
                    sizebox("LblThemePresetsBox", OPT_LBL_W, 24, [text("LblThemePresets", "Saved schemes", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_VBOX, "ThemePresetsCol", slot=OPT_CHIP_SLOT, children=[
                        w(U_WRAP, "ThemePresetChips", props=OPT_CHIP_WRAP),
                        text("ThemePresetsHint", "", 11, GREY, wrap=True, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(4)})])]),
                # slot conflicts: heading, hint, global links, one W_ConflictRow per slot with conflicts (Rebuild Conflicts)
                text("LblConflicts", "Slot conflicts", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(24), sz(4))}),
                text("LblConflictsHint", "", 11, GREY, wrap=True, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(6)}),
                w(U_HBOX, "ConflictLinks", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(8)}),
                w(U_VBOX, "ConflictRows"),
                # several pieces in one slot: one W_SubTab chip per slot (Rebuild Multi Slots; not Acc - the game allows it there already)
                text("LblMultiSlots", "Several pieces in one slot", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(24), sz(4))}),
                text("LblMultiSlotsHint", "", 11, GREY, wrap=True, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(6)}),
                w(U_WRAP, "MultiSlotChips", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(4) + 1, sz(4) + 1)}),
                # tabs: tab bar style (text / icons / both), icon position (left / right), hint, one chip per tab (W_SubTab "Tab:<page>", selected = shown), Options has none
                w(U_HBOX, "RowTabStyle", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    sizebox("LblTabStyleBox", OPT_LBL_W, 24, [text("LblTabStyle", "Tab bar", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_WRAP, "TabStyleChips", props=OPT_CHIP_WRAP, slot=OPT_CHIP_SLOT)]),
                w(U_HBOX, "RowTabIconPos", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    sizebox("LblTabIconPosBox", OPT_LBL_W, 24, [text("LblTabIconPos", "Icon position", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_WRAP, "TabIconPosChips", props=OPT_CHIP_WRAP, slot=OPT_CHIP_SLOT)]),
                w(U_HBOX, "RowTabRow", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(12))}, children=[
                    sizebox("LblTabRowBox", OPT_LBL_W, 24, [text("LblTabRow", "Tab rows", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Top", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(U_WRAP, "TabRowChips", props=OPT_CHIP_WRAP, slot=OPT_CHIP_SLOT)]),
                text("LblTabsHint", "", 11, GREY, wrap=True, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(8)}),
                w(U_WRAP, "TabChips", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(4) + 1, sz(4) + 1)}),
                # quick menu: key (a link that waits for the next key), the wheel's items in order, every available item with a check box
                text("LblQuickControl", "Control", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(4)}),
                w(U_HBOX, "RowQuickKey", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    sizebox("LblQuickKeyBox", OPT_LBL_W, 24, [text("LblQuickKey", "Key (hold)", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Center"}),
                    # the key link as wide as its widest text ("Press a key …" while it waits): a hidden copy of that text sets the width,
                    # the link fills it (Add Quick Key Link) - the click area no longer shrinks to a single letter
                    w(U_OVERLAY, "QuickKeyOv", slot={"VerticalAlignment": "VAlign_Center"}, children=[
                        text("QuickKeyWidth", "", 12, props_extra={"Visibility": "Hidden"}, slot={"Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(6), sz(2), sz(6), sz(2))}),
                        w(U_HBOX, "QuickKeyLinks", slot={"HorizontalAlignment": "HAlign_Fill", "VerticalAlignment": "VAlign_Center"})]),
                    text("LblQuickKeyHint", "", 11, GREY, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(12)})]),
                text("LblQuickInWheel", "In the wheel", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(14), sz(4))}),
                w(U_VBOX, "QuickInWheel"),
                # own keys: key -> any item of the quick menu (right click on an available item binds it), rows with key link and ✕
                text("LblKeyBinds", "Own keys", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(18), sz(4))}),
                text("KeyBindHint", "", 11, GREY, wrap=True, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(6)}),
                w(U_VBOX, "KeyBinds"),
                text("LblQuickAvailable", "Available", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(18), sz(4))}),
                w(U_VBOX, "QuickAvailable", children=[   # virtual list "Qa" (vlist.py), three to a row
                    w(U_SIZE, "QaTop", props={"bOverride_HeightOverride": True, "HeightOverride": 0}),
                    w(U_VBOX, "QaWrap"),
                    w(U_SIZE, "QaBottom", props={"bOverride_HeightOverride": True, "HeightOverride": 0}), w(U_SIZE, "QaBottomRoom", props={"bOverride_HeightOverride": True, "HeightOverride": LIST_ROOM})])]),
            w(U_SCROLL, "BagScroll", props={"Visibility": "Collapsed", "WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "BagVB", children=[
                w(U_HBOX, "BagWornHead", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(6)}, children=[
                    text("BagWornHeader", "Worn", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"VerticalAlignment": "VAlign_Center"}),
                    w(U_HBOX, "BagWornLinks", slot={"Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(12), "VerticalAlignment": "VAlign_Center"})]),
                w(U_WRAP, "BagWorn", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(14)}),
                w(U_HBOX, "BagListHead", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(6)}, children=[
                    text("BagListHeader", "In backpack", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"VerticalAlignment": "VAlign_Center"}),
                    w(U_HBOX, "BagLinks", slot={"Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(12), "VerticalAlignment": "VAlign_Center"})]),
                w(U_WRAP, "BagList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)}),
                text("BagEmpty", "Backpack is empty", 11, GREY)])]),
            # Inventory: chips over both boxes, backpack items (weight head) and the storage box; the two boxes share the height,
            # each scrolls on its own (narrow panels: rows, not columns). The manager fills InvBagList / InvBoxList with W_ContentSection.
            # Every list sits on a surface of its own (inv_area: the light tint of the slot conflict stripes), so the boxes do not run into each other.
            w(U_VBOX, "InventoryVB", props={"Visibility": "Collapsed"}, slot=FILL, children=[
                w(U_WRAP, "InvChips", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(4) + 1, sz(4) + 1)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(8)}),
                w(U_HBOX, "InvBagHead", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(4)}, children=[
                    text("InvBagTitle", "Backpack · Items", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"VerticalAlignment": "VAlign_Center"}),
                    inv_head_btns("InvBagBtns"),
                    sizebox("InvWeightSize", 160, 10, [w(U_PROGRESS, "InvWeightBar", props={"Percent": 0.0})],
                            slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=%d,Bottom=0)" % (sz(14), sz(8))}),
                    text("InvWeightText", "", 11, GREY, slot={"VerticalAlignment": "VAlign_Center"}),
                    # "not saved on this map - keep what you want in the box" (Manager.Fol Bag Saved): Set Inv Bag Note
                    text("InvBagNote", "", 11, GREY, wrap=True, props_extra={"Visibility": "Collapsed"}, slot={"Size": "(SizeRule=Fill,Value=1)", "VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(14)})]),
                inv_area("InvBagArea", "InvBagScroll", "InvBagList"),
                w(U_HBOX, "InvBoxHead", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(4))}, children=[
                    text("InvBoxTitle", "Storage box", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"VerticalAlignment": "VAlign_Center"}),
                    inv_head_btns("InvBoxBtns")]),
                inv_area("InvBoxArea", "InvBoxScroll", "InvBoxList"),
                # all-items catalogue (Options > General): hidden unless switched on
                w(U_HBOX, "InvCatHead", props={"Visibility": "Collapsed"}, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(4))}, children=[
                    text("InvCatTitle", "All items", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"VerticalAlignment": "VAlign_Center"}),
                    inv_head_btns("InvCatBtns"),
                    # search over the catalogue (name as shown or row name): the panel's key-up -> Manager.On Inv Search Changed
                    roundbox("ISearchFrame", COL_CHIP_FRAME, 1, slot={"Size": "(SizeRule=Fill,Value=1)", "VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(14)},
                             children=[roundbox("ISearchFill", COL_CHIP, 0, children=[w(U_HBOX, "ISearchHB", children=[
                                 w(E_EDIT, "InvSearch", props={"HintText": "Search...", "WidgetStyle": SEARCH_STYLE}, slot=FILL),
                                 w(U_HBOX, "InvSearchLinks", slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(4)})])])])]),
                inv_area("InvCatArea", "InvCatScroll", "InvCatList", hidden=True)]),
            # Followers: backpack (left) and storage box (right) side by side in the top third, each with its head (title outside,
            # "..." inside: folds it - the folded column keeps only its head, the other takes the width); the figures below (two
            # thirds), one W_FolRow each. The manager fills FolBagList / FolBoxList with W_ContentSection, FolRows with W_FolRow.
            w(U_VBOX, "FollowersVB", props={"Visibility": "Collapsed"}, slot=FILL, children=[
                w(U_HBOX, "FolTop", slot={"Size": "(SizeRule=Fill,Value=1)"}, children=[
                    w(U_VBOX, "FolBagCol", slot={"Size": "(SizeRule=Fill,Value=1)", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(6)}, children=[
                        w(U_HBOX, "FolBagHead", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(4)}, children=[
                            text("FolBagTitle", "Backpack", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(10)}),   # gap to "..." also when folded (no spacer width left)
                            # "not saved on this map" (the shooting range never saves Jodi's backpack): Set Fol Bag Note
                            text("FolBagNote", "", 11, GREY, props_extra={"Visibility": "Collapsed"}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(10)}),
                            w("/Script/UMG.Spacer", "FolBagGap", slot=FILL),
                            w(U_HBOX, "FolBagBtns", slot={"VerticalAlignment": "VAlign_Center"})]),
                        inv_area("FolBagArea", "FolBagScroll", "FolBagList")]),
                    w(U_VBOX, "FolBoxCol", slot={"Size": "(SizeRule=Fill,Value=1)", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(6)}, children=[
                        w(U_HBOX, "FolBoxHead", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(4)}, children=[
                            w(U_HBOX, "FolBoxBtns", slot={"VerticalAlignment": "VAlign_Center"}),
                            w("/Script/UMG.Spacer", "FolBoxGap", slot=FILL),
                            text("FolBoxTitle", "Storage box", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(10)})]),
                        inv_area("FolBoxArea", "FolBoxScroll", "FolBoxList")])]),
                text("FolHint", "", 11, GREY, wrap=True, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(4))}),
                w(U_SCROLL, "FolScroll", props={"WheelScrollMultiplier": 2.0}, slot={"Size": "(SizeRule=Fill,Value=2)", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(FOL_ROW_GAP)}, children=[w(U_VBOX, "FolRows")])]),
            w(U_HBOX, "HB", slot=FILL, children=[
                sizebox("LeftSize", 340, 100, [w(U_SCROLL, "LeftScroll", props={"WheelScrollMultiplier": 2.0}, children=[w(U_VBOX, "LeftBox")])],
                        slot={"Size": "(SizeRule=Automatic)", "VerticalAlignment": "VAlign_Fill", "Padding": "(Left=0,Top=0,Right=30,Bottom=0)"}),
                w(U_VBOX, "RightBox", slot=FILL, children=[
                    # a search of its own, only for the chips, above the chip row
                    w(U_HBOX, "ChipSearchRow", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(8)}, children=[
                        roundbox("CSearchFrame", COL_CHIP_FRAME, 1, slot=FILL, children=[roundbox("CSearchFill", COL_CHIP, 0, children=[w(U_HBOX, "CSearchHB", children=[
                            w(E_EDIT, "ChipSearch", props={"HintText": "Search...", "WidgetStyle": SEARCH_STYLE}, slot=FILL),
                            w(U_HBOX, "ChipSearchLinks", slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(4)})])])])]),
                    # group chips: at most ~3 rows, then the box scrolls (one tab per mod gets long)
                    w(U_SIZE, "SubTabsBox", props={"bOverride_MaxDesiredHeight": True, "MaxDesiredHeight": sz(SUBTABS_MAX_H)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=15)"}, children=[
                        w(U_SCROLL, "SubTabsScroll", props={"WheelScrollMultiplier": 2.0}, children=[
                            w(U_WRAP, "SubTabs", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(4) + 1, sz(4) + 1)})])]),
                    w(U_HBOX, "Filters", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=15)"}, children=[
                        roundbox("SearchFrame", COL_CHIP_FRAME, 1, slot=FILL, children=[roundbox("SearchFill", COL_CHIP, 0, children=[w(U_HBOX, "SearchHB", children=[
                            w(E_EDIT, "Search", props={"HintText": "Search...", "WidgetStyle": SEARCH_STYLE}, slot=FILL),
                            w(U_HBOX, "SearchLinks", slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(4)})])])]),
                        sizebox("OwnedBox", 34, 34, [w(U_SCALE, "OwnedScale", props={"Stretch": "ScaleToFit"}, children=[w(E_CHECK, "OnlyOwned", props={"WidgetStyle": check_style(CHECK_SIZE)})])],
                                slot={"Padding": "(Left=30,Top=0,Right=10,Bottom=0)", "VerticalAlignment": "VAlign_Center"}),
                        text("LblOwned", "only\nowned", 11, slot={"VerticalAlignment": "VAlign_Center"}),
                        sizebox("FavBox", 34, 34, [w(U_SCALE, "FavScale", props={"Stretch": "ScaleToFit"}, children=[w(E_CHECK, "OnlyFav", props={"WidgetStyle": check_style(CHECK_SIZE)})])],
                                slot={"Padding": "(Left=30,Top=0,Right=10,Bottom=0)", "VerticalAlignment": "VAlign_Center"}),
                        text("LblFav", "only\nfavourites", 11, slot={"VerticalAlignment": "VAlign_Center"}),
                        sizebox("VanillaBox", 34, 34, [w(U_SCALE, "VanillaScale", props={"Stretch": "ScaleToFit"}, children=[w(E_CHECK, "OnlyVanilla", props={"WidgetStyle": check_style(CHECK_SIZE)})])],
                                slot={"Padding": "(Left=30,Top=0,Right=10,Bottom=0)", "VerticalAlignment": "VAlign_Center"}),
                        text("LblVanilla", "only\nvanilla", 11, slot={"VerticalAlignment": "VAlign_Center"}),
                        sizebox("WornBox", 34, 34, [w(U_SCALE, "WornScale", props={"Stretch": "ScaleToFit"}, children=[w(E_CHECK, "OnlyWorn", props={"WidgetStyle": check_style(CHECK_SIZE)})])],
                                slot={"Padding": "(Left=30,Top=0,Right=10,Bottom=0)", "VerticalAlignment": "VAlign_Center"}),
                        text("LblOnlyWorn", "only\nworn", 11, slot={"VerticalAlignment": "VAlign_Center"}),
                    ]),
                    w(U_SCROLL, "ListScroll", props={"WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "ListVB", children=[
                        # virtual list "Clo" (vlist.py): the favourites / all headings are entries of it; FavHeader / AllHeader only keep
                        # Set Strings' parameters and stay collapsed
                        text("FavHeader", "Favourites", 13, props_extra={"Visibility": "Collapsed"}), text("AllHeader", "All", 13, props_extra={"Visibility": "Collapsed"}),
                        w(U_SIZE, "CloTop", props={"bOverride_HeightOverride": True, "HeightOverride": 0}),
                        w(U_VBOX, "List"),
                        w(U_SIZE, "CloBottom", props={"bOverride_HeightOverride": True, "HeightOverride": 0}), w(U_SIZE, "CloBottomRoom", props={"bOverride_HeightOverride": True, "HeightOverride": LIST_ROOM}),
                        text("ListHint", "Only the first 400 matches are shown - please narrow the search.", 11, GREY, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(8)})])]),
                ]),
            ]),
            w(U_VBOX, "StatusBar", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(8)}, children=[
                w(U_SIZE, "StatusLineBox", props={"bOverride_HeightOverride": True, "HeightOverride": 1}, children=[w(E_BORDER, "StatusLine", props={"BrushColor": "(R=1,G=1,B=1,A=0.35)", "Padding": "(Left=0,Top=0,Right=0,Bottom=0)"})]),
                # the links sit in the middle, a second box hangs on the right: page actions belong there, not in the
                # page itself, where they wander with the content (poses: "Stop pose" and "Measure all"; weapons: the
                # button that takes the tile pictures again)
                w(U_OVERLAY, "StatusRow", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(6)}, children=[
                    w(U_HBOX, "StatusLinks", slot={"HorizontalAlignment": "HAlign_Center"}),
                    w(U_HBOX, "StatusRight", slot={"HorizontalAlignment": "HAlign_Right"})])]),
            ])])])
    # small helper functions for the manager
    def clear(name, box):
        g = G(); g.get("g", box); g.call("c", U_PANELW, "ClearChildren", inp={"self": "@g." + box}); g.chain("entry", "c"); return fn(name, graph=g)
    # the key link fills the overlay that the hidden "Press a key …" sizes
    qg = G(); qg.get("g", "QuickKeyLinks"); qg.call("a", U_HBOX, "AddChildToHorizontalBox", inp={"self": "@g.QuickKeyLinks", "Content": "@entry.widget"})
    qg.call("sz", "/Script/UMG.HorizontalBoxSlot", "SetSize", inp={"self": "@a.ReturnValue", "InSize": "(SizeRule=Fill,Value=1.0)"}); qg.chain("entry", "a", "sz")
    qkl = fn("Add Quick Key Link", [param("widget", "object:" + E_WIDGET)], graph=qg)
    def padded_add(name, box):   # inventory head chips: a small gap between them
        g = G(); g.get("g", box); g.call("a", U_HBOX, "AddChildToHorizontalBox", inp={"self": "@g." + box, "Content": "@entry.widget"})
        g.call("p", "/Script/UMG.HorizontalBoxSlot", "SetPadding", inp={"self": "@a.ReturnValue", "InPadding": "(Left=0,Top=0,Right=%d,Bottom=0)" % (sz(4) + 1)})
        g.call("v", "/Script/UMG.HorizontalBoxSlot", "SetVerticalAlignment", inp={"self": "@a.ReturnValue", "InVerticalAlignment": "VAlign_Center"})
        g.chain("entry", "a", "p", "v"); return fn(name, [param("widget", "object:" + E_WIDGET)], graph=g)
    # Followers page: head chips, the two columns (a folded one keeps only its head and gives the width away), the hint line
    cfh = G(); tail = ["entry"]
    for b in ("FolBagBtns", "FolBoxBtns"): cfh.get("g" + b, b); cfh.call("c" + b, U_PANELW, "ClearChildren", inp={"self": "@g%s.%s" % (b, b)}); tail.append("c" + b)
    cfh.chain(*tail)
    flo = G(); ends = ["entry"]
    for k, pin in (("Bag", "bagshown"), ("Box", "boxshown")):
        a = "Fol%sArea" % k; col = "Fol%sCol" % k
        flo.branch("bs" + k, "@entry." + pin); flo.get("gv" + k, a); flo.call("vv" + k, E_WIDGET, "SetVisibility", inp={"self": "@gv%s.%s" % (k, a), "InVisibility": "SelfHitTestInvisible"})
        flo.get("gh" + k, a); flo.call("vh" + k, E_WIDGET, "SetVisibility", inp={"self": "@gh%s.%s" % (k, a), "InVisibility": "Collapsed"})
        flo.get("gc" + k, col); flo.call("sl" + k, "/Script/UMG.WidgetLayoutLibrary", "SlotAsHorizontalBoxSlot", inp={"Widget": "@gc%s.%s" % (k, col)})
        flo.call("sf" + k, "/Script/UMG.HorizontalBoxSlot", "SetSize", inp={"self": "@sl%s.ReturnValue" % k, "InSize": "(SizeRule=Fill,Value=1.0)"})
        flo.call("sa" + k, "/Script/UMG.HorizontalBoxSlot", "SetSize", inp={"self": "@sl%s.ReturnValue" % k, "InSize": "(SizeRule=Automatic,Value=1.0)"})
        for e in ends: flo.chain(e, "bs" + k)
        flo.chain("bs" + k, "vv" + k, "sf" + k); flo.chain("bs%s:else" % k, "vh" + k, "sa" + k); ends = ["sf" + k, "sa" + k]
    def text_or_hide(name):
        """SetText on widget `name`; an empty text collapses it."""
        t = G(); t.get("gt", name); t.call("st", E_TEXT, "SetText", inp={"self": "@gt." + name, "InText": "@entry.text"}); t.call("e", K_TXT, "TextIsEmpty", inp={"InText": "@entry.text"})
        t.branch("b", "@e.ReturnValue"); t.get("gt2", name); t.call("h", E_WIDGET, "SetVisibility", inp={"self": "@gt2." + name, "InVisibility": "Collapsed"})
        t.get("gt3", name); t.call("v", E_WIDGET, "SetVisibility", inp={"self": "@gt3." + name, "InVisibility": "HitTestInvisible"}); t.chain("entry", "st", "b", "h"); t.chain("b:else", "v")
        return t
    fhi = text_or_hide("FolHint"); fbn = text_or_hide("FolBagNote"); ibn = text_or_hide("InvBagNote")
    cih = G(); tail = ["entry"]
    for b in ("InvBagBtns", "InvBoxBtns", "InvCatBtns"): cih.get("g" + b, b); cih.call("c" + b, U_PANELW, "ClearChildren", inp={"self": "@g%s.%s" % (b, b)}); tail.append("c" + b)
    cih.chain(*tail)

    def add(name, box, cls, func):
        g = G(); g.get("g", box); g.call("a", cls, func, inp={"self": "@g." + box, "Content": "@entry.widget"}); g.chain("entry", "a")
        if box in TILE_LISTS:   # a row of tiles is as tall as its tallest tile
            g.call("va", "/Script/UMG.WrapBoxSlot", "SetVerticalAlignment", inp={"self": "@a.ReturnValue", "InVerticalAlignment": "VAlign_Fill"}); g.chain("a", "va")
        return fn(name, [param("widget", "object:" + E_WIDGET)], graph=g)
    gs = G(); gs.get("g", "Search"); gs.call("t", E_EDIT, "GetText", inp={"self": "@g.Search"}); gs.link("t.ReturnValue", "return.text")
    go = G(); go.get("g", "OnlyOwned"); go.call("c", E_CHECK, "IsChecked", inp={"self": "@g.OnlyOwned"}); go.link("c.ReturnValue", "return.yes")
    gf = G(); gf.get("g", "OnlyFav"); gf.call("c", E_CHECK, "IsChecked", inp={"self": "@g.OnlyFav"}); gf.link("c.ReturnValue", "return.yes")
    gv = G(); gv.get("g", "OnlyVanilla"); gv.call("c", E_CHECK, "IsChecked", inp={"self": "@g.OnlyVanilla"}); gv.link("c.ReturnValue", "return.yes")
    gw = G(); gw.get("g", "OnlyWorn"); gw.call("c", E_CHECK, "IsChecked", inp={"self": "@g.OnlyWorn"}); gw.link("c.ReturnValue", "return.yes")
    # Manage page: search box, "only mods" checkbox; Coiffure: swatch row visibility
    gtn = G(); gtn.get("g", "ThemeNameEdit"); gtn.call("t", E_EDIT, "GetText", inp={"self": "@g.ThemeNameEdit"}); gtn.link("t.ReturnValue", "return.text")
    ctn = G(); ctn.get("g", "ThemeNameEdit"); ctn.call("st", E_EDIT, "SetText", inp={"self": "@g.ThemeNameEdit", "InText": ""}); ctn.chain("entry", "st")
    gms = G(); gms.get("g", "ManageSearch"); gms.call("t", E_EDIT, "GetText", inp={"self": "@g.ManageSearch"}); gms.link("t.ReturnValue", "return.text")
    gom = G(); gom.get("g", "OnlyMods"); gom.call("c", E_CHECK, "IsChecked", inp={"self": "@g.OnlyMods"}); gom.link("c.ReturnValue", "return.yes")
    cms = G(); cms.get("g", "ManageSearch"); cms.call("st", E_EDIT, "SetText", inp={"self": "@g.ManageSearch", "InText": ""}); cms.chain("entry", "st")
    sms = G(); sms.get("g", "ManageSearch"); sms.call("st", E_EDIT, "SetText", inp={"self": "@g.ManageSearch", "InText": "@entry.text"}); sms.chain("entry", "st")
    gls = G(); gls.get("g", "LookSearch"); gls.call("t", E_EDIT, "GetText", inp={"self": "@g.LookSearch"}); gls.link("t.ReturnValue", "return.text")
    cls_ = G(); cls_.get("g", "LookSearch"); cls_.call("st", E_EDIT, "SetText", inp={"self": "@g.LookSearch", "InText": ""}); cls_.chain("entry", "st")
    gcse = G(); gcse.get("g", "ChipSearch"); gcse.call("t", E_EDIT, "GetText", inp={"self": "@g.ChipSearch"}); gcse.link("t.ReturnValue", "return.text")
    ccse = G(); ccse.get("g", "ChipSearch"); ccse.call("st", E_EDIT, "SetText", inp={"self": "@g.ChipSearch", "InText": ""}); ccse.chain("entry", "st")
    # SetVisibility expects ESlateVisibility: two branch paths (like Set Look Chips Visible)
    csv_ = G(); csv_.branch("b", "@entry.visible")
    csv_.get("g0", "ChipSearchRow"); csv_.call("v0", E_WIDGET, "SetVisibility", inp={"self": "@g0.ChipSearchRow", "InVisibility": "Visible"})
    csv_.get("h0", "ChipSearchRow"); csv_.call("c0", E_WIDGET, "SetVisibility", inp={"self": "@h0.ChipSearchRow", "InVisibility": "Collapsed"})
    csv_.chain("entry", "b", "v0"); csv_.chain("b:else", "c0")
    glcs = G(); glcs.get("g", "LookChipSearch"); glcs.call("t", E_EDIT, "GetText", inp={"self": "@g.LookChipSearch"}); glcs.link("t.ReturnValue", "return.text")
    clcs = G(); clcs.get("g", "LookChipSearch"); clcs.call("st", E_EDIT, "SetText", inp={"self": "@g.LookChipSearch", "InText": ""}); clcs.chain("entry", "st")
    # own function, not part of Set Look Chips Visible: the option may hide the search row without taking the chips with it
    # Manage chips: the chip box, and the chip search row only when the chip search is wanted (option) - both decided by the caller
    mcv = G(); mcv.branch("b", "@entry.chips"); mcv.branch("b2", "@entry.search")
    for i, wn in enumerate(["ManageSubTabsBox", "ManageChipSearchRow"]):
        mcv.get("gv%d" % i, wn); mcv.call("v%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@gv%d.%s" % (i, wn), "InVisibility": "Visible"})
        mcv.get("gc%d" % i, wn); mcv.call("c%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@gc%d.%s" % (i, wn), "InVisibility": "Collapsed"})
    mcv.chain("entry", "b", "v0", "b2", "v1"); mcv.chain("b:else", "c0", "b2"); mcv.chain("b2:else", "c1")
    cmcs = G(); cmcs.get("g", "ManageChipSearch"); cmcs.call("st", E_EDIT, "SetText", inp={"self": "@g.ManageChipSearch", "InText": ""}); cmcs.chain("entry", "st")
    lcsv = G(); lcsv.branch("b", "@entry.visible")
    lcsv.get("g0", "LookChipSearchRow"); lcsv.call("v0", E_WIDGET, "SetVisibility", inp={"self": "@g0.LookChipSearchRow", "InVisibility": "Visible"})
    lcsv.get("h0", "LookChipSearchRow"); lcsv.call("c0", E_WIDGET, "SetVisibility", inp={"self": "@h0.LookChipSearchRow", "InVisibility": "Collapsed"})
    lcsv.chain("entry", "b", "v0"); lcsv.chain("b:else", "c0")
    som = G(); som.get("g", "OnlyMods"); som.call("s", E_CHECK, "SetIsChecked", inp={"self": "@g.OnlyMods", "InIsChecked": "@entry.on"}); som.chain("entry", "s")
    gcs = G(); gcs.get("g", "CaseSens"); gcs.call("c", E_CHECK, "IsChecked", inp={"self": "@g.CaseSens"}); gcs.link("c.ReturnValue", "return.yes")
    scs = G(); scs.get("g", "CaseSens"); scs.call("s", E_CHECK, "SetIsChecked", inp={"self": "@g.CaseSens", "InIsChecked": "@entry.on"}); scs.chain("entry", "s")
    shs = G(); shs.branch("b", "@entry.visible")
    shs.get("g0", "HairSwatches"); shs.call("v0", E_WIDGET, "SetVisibility", inp={"self": "@g0.HairSwatches", "InVisibility": "Visible"})
    shs.get("h0", "HairSwatches"); shs.call("c0", E_WIDGET, "SetVisibility", inp={"self": "@h0.HairSwatches", "InVisibility": "Collapsed"})
    shs.chain("entry", "b", "v0"); shs.chain("b:else", "c0")
    # Manage page: "only mods" checkbox + label shown only for Clothes / Look (Mods / Vanilla list mod or vanilla rows anyway)
    somv = G(); somv.branch("b", "@entry.visible"); somv.chain("entry", "b"); prev = {"v": "b", "c": "b:else"}
    for i, wn in enumerate(("OnlyModsBox", "LblOnlyMods")):
        somv.get("gv%d" % i, wn); somv.call("v%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@gv%d.%s" % (i, wn), "InVisibility": "Visible"}); somv.chain(prev["v"], "v%d" % i); prev["v"] = "v%d" % i
        somv.get("gc%d" % i, wn); somv.call("c%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@gc%d.%s" % (i, wn), "InVisibility": "Collapsed"}); somv.chain(prev["c"], "c%d" % i); prev["c"] = "c%d" % i
    # keyboard: game actions (Esc, HideUI=Backspace, Inventory=Tab, Screenshot=F9) are bound to IE_Released in the controller.
    # Hence: swallow all key-downs AND key-ups while the panel is open; close only on key-up (Esc / the panel key, B by default),
    # so no release slips through to the game. K does not close while the search field has focus (typing).
    # Exception: LeftShift / RightShift pass through (Unhandled -> SViewport -> PlayerInput) so PlayerInput keeps seeing the
    # modifier while the panel has the focus; the game binds Shift only to Run (pawn action, locked while the panel is open).
    def is_shift(g, id, key):
        g.call(id + "l", K_IN, "EqualEqual_KeyKey", inp={"A": key, "B": "LeftShift"}); g.call(id + "r", K_IN, "EqualEqual_KeyKey", inp={"A": key, "B": "RightShift"})
        g.call(id + "o", K_MATH, "BooleanOR", inp={"A": "@%sl.ReturnValue" % id, "B": "@%sr.ReturnValue" % id}); return "@%so.ReturnValue" % id
    kd = G(); kd.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"}); kd.branch("bs", is_shift(kd, "s", "@key.ReturnValue"))
    kd.call("u", K_WBL, "Unhandled"); kd.link("u.ReturnValue", "return.ReturnValue")
    kd.n("r2", "return_new"); kd.call("h", K_WBL, "Handled"); kd.link("h.ReturnValue", "r2.ReturnValue")
    if os.environ.get("ALTUI_FOCUSLOG") == "1":   # which key events reach the panel at all (Esc and the pause menu)
        kd.call("kn", K_IN, "Key_GetDisplayName", inp={"Key": "@key.ReturnValue"}); kd.call("ks", K_TXT, "Conv_TextToString", inp={"InText": "@kn.ReturnValue"})
        kd.call("kc", K_STR, "Concat_StrStr", inp={"A": "down ", "B": "@ks.ReturnValue"}); kd.get("gmf", "Manager"); kd.call("flk", MGR, "Focus Log Key", inp={"self": "@gmf.Manager", "what": "@kc.ReturnValue"})
        kd.chain("entry", "flk", "bs", "return")
    else:
        kd.chain("entry", "bs", "return")
    kd.chain("bs:else", "r2")
    # OnPreviewKeyDown (tunnel, before the text field): a Key field of the Mods tab waiting (Manager.Capturing Key) takes the key -
    # Escape cancels instead - and the key's key-up is swallowed (SwallowUp), so Esc or the panel key do not close the panel.
    # Otherwise: swallow Escape (the text field must not react)
    pk = G()
    pk.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"})
    pk.get("gmc", "Manager"); pk.call("cap", MGR, "Capturing Key", inp={"self": "@gmc.Manager"}); pk.branch("bc", "@cap.yes")
    pk.call("esc0", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Escape"}); pk.branch("be", "@esc0.ReturnValue")
    pk.get("gm1", "Manager"); pk.call("cn", MGR, "Cancel Key Capture", inp={"self": "@gm1.Manager"})
    pk.get("gm2", "Manager"); pk.call("kc", MGR, "Key Captured", inp={"self": "@gm2.Manager", "pressed": "@key.ReturnValue"})
    pk.get("gm3", "Manager"); pk.n("ssu", "set", var="SwallowUp", cls=MGR, inp={"self": "@gm3.Manager", "SwallowUp": "true"})
    pk.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Escape"}); pk.branch("b", "@esc.ReturnValue")
    pk.call("h", K_WBL, "Handled"); pk.link("h.ReturnValue", "return.ReturnValue")
    pk.n("r2", "return_new"); pk.call("u", K_WBL, "Unhandled"); pk.link("u.ReturnValue", "r2.ReturnValue")
    pk.chain("entry", "bc", "be", "cn", "ssu", "return"); pk.chain("be:else", "kc", "ssu"); pk.chain("bc:else", "b", "return"); pk.chain("b:else", "r2")
    # OnPreviewMouseButtonDown: a click anywhere while a Key field waits cancels it and goes on as the click it is (on the
    # same field it starts the wait again). Mouse buttons are no keys for a Key field. (pvm: pm is the panel's own
    # OnMouseButtonDown further down - the same name once made both events run that one.)
    # It also closes an open context menu first: a tile handles its own click, so the panel's OnMouseButtonDown (closes the
    # menu) never saw a click on another tile and the menu stayed open (2026-10-16). The menu is a viewport widget of its
    # own, not in the panel: clicks on its rows do not pass here. A right click on a tile opens its menu after this.
    pvm = G()
    pvm.get("gmm", "Manager"); pvm.call("cm", MGR, "Close Menu", inp={"self": "@gmm.Manager"})
    pvm.get("gmc", "Manager"); pvm.call("cap", MGR, "Capturing Key", inp={"self": "@gmc.Manager"}); pvm.branch("bc", "@cap.yes")
    pvm.get("gm1", "Manager"); pvm.call("cn", MGR, "Cancel Key Capture", inp={"self": "@gm1.Manager"})
    pvm.call("u", K_WBL, "Unhandled"); pvm.link("u.ReturnValue", "return.ReturnValue")
    pvm.chain("entry", "cm", "bc", "cn", "return"); pvm.chain("bc:else", "return")
    # OnKeyUp: search -> Manager.On Search Changed(text); Esc or the panel key (without focus in a search box) -> Panel Key Close (Esc with the palette open: the palette, else the panel); Handled except Shift (see OnKeyDown)
    ku = G()
    ku.get("gs", "Search"); ku.call("t", E_EDIT, "GetText", inp={"self": "@gs.Search"})
    ku.get("gm", "Manager"); ku.call("sc", MGR, "On Search Changed", inp={"self": "@gm.Manager", "text": "@t.ReturnValue"})
    ku.get("gsm", "ManageSearch"); ku.call("tm", E_EDIT, "GetText", inp={"self": "@gsm.ManageSearch"})
    ku.get("gm9", "Manager"); ku.call("scm", MGR, "On Manage Search Changed", inp={"self": "@gm9.Manager", "text": "@tm.ReturnValue"})
    ku.get("gsl", "LookSearch"); ku.call("tl", E_EDIT, "GetText", inp={"self": "@gsl.LookSearch"})
    ku.get("gm8", "Manager"); ku.call("scl", MGR, "On Look Search Changed", inp={"self": "@gm8.Manager", "text": "@tl.ReturnValue"})
    ku.get("gsp", "PoseSearch"); ku.call("tp", E_EDIT, "GetText", inp={"self": "@gsp.PoseSearch"})
    ku.get("gm7", "Manager"); ku.call("scp", MGR, "On Pose Search Changed", inp={"self": "@gm7.Manager", "text": "@tp.ReturnValue"})
    ku.get("gsw", "WeaponSearch"); ku.call("tw", E_EDIT, "GetText", inp={"self": "@gsw.WeaponSearch"})
    ku.get("gm6", "Manager"); ku.call("scw", MGR, "On Weapon Search Changed", inp={"self": "@gm6.Manager", "text": "@tw.ReturnValue"})
    ku.get("gsc", "ChipSearch"); ku.call("tc", E_EDIT, "GetText", inp={"self": "@gsc.ChipSearch"})
    ku.get("gm5", "Manager"); ku.call("scc", MGR, "On Chip Search Changed", inp={"self": "@gm5.Manager", "text": "@tc.ReturnValue"})
    ku.get("gsmc", "ManageChipSearch"); ku.call("tmc", E_EDIT, "GetText", inp={"self": "@gsmc.ManageChipSearch"})
    ku.get("gm3", "Manager"); ku.call("scmc", MGR, "On Manage Chip Search Changed", inp={"self": "@gm3.Manager", "text": "@tmc.ReturnValue"})
    ku.get("gslc", "LookChipSearch"); ku.call("tlc", E_EDIT, "GetText", inp={"self": "@gslc.LookChipSearch"})
    ku.get("gm4", "Manager"); ku.call("sclc", MGR, "On Look Chip Search Changed", inp={"self": "@gm4.Manager", "text": "@tlc.ReturnValue"})
    ku.get("gsi", "InvSearch"); ku.call("tiv", E_EDIT, "GetText", inp={"self": "@gsi.InvSearch"})
    ku.get("gm10", "Manager"); ku.call("sciv", MGR, "On Inv Search Changed", inp={"self": "@gm10.Manager", "text": "@tiv.ReturnValue"})
    ku.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"})
    ku.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Escape"})
    ku.call("kdn", K_IN, "Key_GetDisplayName", inp={"Key": "@key.ReturnValue"}); ku.call("kds", K_TXT, "Conv_TextToString", inp={"InText": "@kdn.ReturnValue"})
    ku.get("gmk", "Manager"); ku.get("gtk", "ToggleKey", cls=MGR); ku.link("gmk.Manager", "gtk.self"); ku.call("tks", K_STR, "Conv_NameToString", inp={"InName": "@gtk.ToggleKey"})
    ku.call("kk", K_STR, "EqualEqual_StriStri", inp={"A": "@kds.ReturnValue", "B": "@tks.ReturnValue"})
    ku.get("gs2", "Search"); ku.call("hf", E_WIDGET, "HasKeyboardFocus", inp={"self": "@gs2.Search"})
    ku.get("gs3", "ManageSearch"); ku.call("hfm", E_WIDGET, "HasKeyboardFocus", inp={"self": "@gs3.ManageSearch"})   # typing the panel key into any search box
    ku.get("gs4", "LookSearch"); ku.call("hfl", E_WIDGET, "HasKeyboardFocus", inp={"self": "@gs4.LookSearch"})
    ku.get("gs5", "PoseSearch"); ku.call("hfp", E_WIDGET, "HasKeyboardFocus", inp={"self": "@gs5.PoseSearch"})
    ku.get("gs6", "WeaponSearch"); ku.call("hfw", E_WIDGET, "HasKeyboardFocus", inp={"self": "@gs6.WeaponSearch"})
    ku.call("hfa0", K_MATH, "BooleanOR", inp={"A": "@hf.ReturnValue", "B": "@hfm.ReturnValue"}); ku.call("hfa1", K_MATH, "BooleanOR", inp={"A": "@hfa0.ReturnValue", "B": "@hfl.ReturnValue"}); ku.call("hfa2", K_MATH, "BooleanOR", inp={"A": "@hfa1.ReturnValue", "B": "@hfp.ReturnValue"}); ku.call("hfa", K_MATH, "BooleanOR", inp={"A": "@hfa2.ReturnValue", "B": "@hfw.ReturnValue"})
    ku.get("gs7", "ChipSearch"); ku.call("hfc", E_WIDGET, "HasKeyboardFocus", inp={"self": "@gs7.ChipSearch"})
    ku.call("hfb", K_MATH, "BooleanOR", inp={"A": "@hfa.ReturnValue", "B": "@hfc.ReturnValue"})
    ku.get("gs8", "LookChipSearch"); ku.call("hfd", E_WIDGET, "HasKeyboardFocus", inp={"self": "@gs8.LookChipSearch"})
    ku.get("gs9", "ManageChipSearch"); ku.call("hfg", E_WIDGET, "HasKeyboardFocus", inp={"self": "@gs9.ManageChipSearch"})
    ku.call("hfe0", K_MATH, "BooleanOR", inp={"A": "@hfb.ReturnValue", "B": "@hfd.ReturnValue"}); ku.call("hfe1", K_MATH, "BooleanOR", inp={"A": "@hfe0.ReturnValue", "B": "@hfg.ReturnValue"})
    ku.get("gs10", "InvSearch"); ku.call("hfi", E_WIDGET, "HasKeyboardFocus", inp={"self": "@gs10.InvSearch"}); ku.call("hfe2", K_MATH, "BooleanOR", inp={"A": "@hfe1.ReturnValue", "B": "@hfi.ReturnValue"})
    ku.get("gs11", "RagNameEdit"); ku.call("hfr", E_WIDGET, "HasKeyboardFocus", inp={"self": "@gs11.RagNameEdit"}); ku.call("hfe3", K_MATH, "BooleanOR", inp={"A": "@hfe2.ReturnValue", "B": "@hfr.ReturnValue"})
    ku.get("gs12", "ThemeNameEdit"); ku.call("hft", E_WIDGET, "HasKeyboardFocus", inp={"self": "@gs12.ThemeNameEdit"}); ku.call("hfe", K_MATH, "BooleanOR", inp={"A": "@hfe3.ReturnValue", "B": "@hft.ReturnValue"})
    ku.call("nf", K_MATH, "Not_PreBool", inp={"A": "@hfe.ReturnValue"})
    ku.call("kx", K_MATH, "BooleanAND", inp={"A": "@kk.ReturnValue", "B": "@nf.ReturnValue"})
    ku.call("or", K_MATH, "BooleanOR", inp={"A": "@esc.ReturnValue", "B": "@kx.ReturnValue"}); ku.branch("b", "@or.ReturnValue")
    ku.get("gm2", "Manager"); ku.call("cl", MGR, "Panel Key Close", inp={"self": "@gm2.Manager", "esc": "@esc.ReturnValue"})   # Esc with the palette open: only the palette
    ku.call("h", K_WBL, "Handled"); ku.link("h.ReturnValue", "return.ReturnValue")
    ku.branch("bs", is_shift(ku, "s", "@key.ReturnValue"))
    ku.n("r2", "return_new"); ku.call("u", K_WBL, "Unhandled"); ku.link("u.ReturnValue", "r2.ReturnValue")
    ku.get("gsu", "Manager"); ku.get("gsu2", "SwallowUp", cls=MGR); ku.link("gsu.Manager", "gsu2.self"); ku.branch("bsu", "@gsu2.SwallowUp")   # the key-up of a key a Key field took
    ku.get("gsu3", "Manager"); ku.n("csu", "set", var="SwallowUp", cls=MGR, inp={"self": "@gsu3.Manager", "SwallowUp": "false"})
    if os.environ.get("ALTUI_FOCUSLOG") == "1":
        ku.call("fkc", K_STR, "Concat_StrStr", inp={"A": "up ", "B": "@kds.ReturnValue"}); ku.get("gmf", "Manager"); ku.call("flk", MGR, "Focus Log Key", inp={"self": "@gmf.Manager", "what": "@fkc.ReturnValue"})
        ku.chain("entry", "flk", "bsu", "csu", "return")
    else:
        ku.chain("entry", "bsu", "csu", "return")
    ku.chain("bsu:else", "sc")
    ku.chain("sc", "scm", "scl", "scp", "scw", "scc", "sclc", "scmc", "sciv", "b", "cl", "return"); ku.chain("b:else", "bs", "r2"); ku.chain("bs:else", "return")
    # SetVisibility expects ESlateVisibility: via two branch paths (Visible / Collapsed)
    fv2 = G(); fv2.branch("b", "@entry.visible")
    fv2.chain("entry", "b")   # clothes favourites: the headings are entries of the virtual list now (kept for its callers)
    # Manage header: the hidden "View content" placeholder keeps its width only where rows have that link (Mods category)
    mcs = G(); mcs.branch("b", "@entry.keep"); mcs.get("g0", "HdrContent"); mcs.call("v0", E_WIDGET, "SetVisibility", inp={"self": "@g0.HdrContent", "InVisibility": "Hidden"})
    mcs.get("g1", "HdrContent"); mcs.call("c0", E_WIDGET, "SetVisibility", inp={"self": "@g1.HdrContent", "InVisibility": "Collapsed"}); mcs.chain("entry", "b", "v0"); mcs.chain("b:else", "c0")
    lfv = G(); lfv.branch("b", "@entry.visible")
    for i, wn in enumerate(["LookFavHeader", "LookFavList", "LookAllHeader"]):
        lfv.get("g%d" % i, wn); lfv.call("v%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@g%d.%s" % (i, wn), "InVisibility": "Visible"})
        lfv.get("h%d" % i, wn); lfv.call("c%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@h%d.%s" % (i, wn), "InVisibility": "Collapsed"})
    lfv.chain("entry", "b", "v0", "v1", "v2"); lfv.chain("b:else", "c0", "c1", "c2")
    lcv = G(); lcv.branch("b", "@entry.visible")
    lcv.get("g0", "LookSubTabsBox"); lcv.call("v0", E_WIDGET, "SetVisibility", inp={"self": "@g0.LookSubTabsBox", "InVisibility": "Visible"})
    lcv.get("h0", "LookSubTabsBox"); lcv.call("c0", E_WIDGET, "SetVisibility", inp={"self": "@h0.LookSubTabsBox", "InVisibility": "Collapsed"})
    lcv.chain("entry", "b", "v0"); lcv.chain("b:else", "c0")
    glf = G(); glf.get("g", "LookOnlyFav"); glf.call("c", E_CHECK, "IsChecked", inp={"self": "@g.LookOnlyFav"}); glf.link("c.ReturnValue", "return.yes")
    slf = G(); slf.get("g", "LookOnlyFav"); slf.call("c", E_CHECK, "SetIsChecked", inp={"self": "@g.LookOnlyFav", "InIsChecked": "@entry.yes"}); slf.chain("entry", "c")
    glw = G(); glw.get("g", "LookOnlyWorn"); glw.call("c", E_CHECK, "IsChecked", inp={"self": "@g.LookOnlyWorn"}); glw.link("c.ReturnValue", "return.yes")
    slw = G(); slw.get("g", "LookOnlyWorn"); slw.call("s", E_CHECK, "SetIsChecked", inp={"self": "@g.LookOnlyWorn", "InIsChecked": "@entry.yes"}); slw.chain("entry", "s")
    # panel click (no child handled the click): close the context menu. Click on Jodi in the free area (catcher hovered + Manager.Begin Jodi Drag:
    # cursor trace hits her) -> capture the mouse for the drag (the viewport never sees it -> the camera stays); otherwise Unhandled -> viewport (camera drag)
    pm = G(); pm.get("gm", "Manager"); pm.call("cm", MGR, "Close Menu", inp={"self": "@gm.Manager"})
    pm.get("gjc", "JodiCatcher"); pm.call("hov", E_WIDGET, "IsHovered", inp={"self": "@gjc.JodiCatcher"}); pm.branch("bh", "@hov.ReturnValue")
    pm.call("btn", K_IN, "PointerEvent_GetEffectingButton", inp={"Input": "@entry.MouseEvent"})
    pm.call("isr", K_IN, "EqualEqual_KeyKey", inp={"A": "@btn.ReturnValue", "B": "RightMouseButton"})   # the manager needs the button: with the option on, right drags the height and left only turns
    pm.get("gm2", "Manager"); pm.call("psh", K_IN, "InputEvent_IsShiftDown", inp={"Input": "@entry.MouseEvent"})   # Ragdolls: Shift + click locks / frees a joint
    pm.call("bd", MGR, "Begin Jodi Drag", inp={"self": "@gm2.Manager", "right": "@isr.ReturnValue", "shift": "@psh.ReturnValue"}); pm.branch("bj", "@bd.yes")
    # right click while a ragdoll part is held: it stays there (Manager.Rag Pin Grab, GMod) - the left drag goes on, the capture stays
    pm.get("gm4", "Manager"); pm.get("grgp", "RagGrab", cls=MGR); pm.link("gm4.Manager", "grgp.self")
    pm.call("pgr", K_MATH, "BooleanAND", inp={"A": "@isr.ReturnValue", "B": "@grgp.RagGrab"}); pm.branch("bpg", "@pgr.ReturnValue")
    pm.get("gm5", "Manager"); pm.call("rpg", MGR, "Rag Pin Grab", inp={"self": "@gm5.Manager"}); pm.call("h2", K_WBL, "Handled"); pm.n("r3", "return_new"); pm.link("h2.ReturnValue", "r3.ReturnValue")
    pm.call("h", K_WBL, "Handled"); pm.self_("me"); pm.call("cap", K_WBL, "CaptureMouse", inp={"Reply": "@h.ReturnValue", "CapturingWidget": "@me.self"}); pm.link("cap.ReturnValue", "return.ReturnValue")
    pm.n("r2", "return_new"); pm.call("u", K_WBL, "Unhandled"); pm.link("u.ReturnValue", "r2.ReturnValue")
    lgpm = []
    if os.environ.get("ALTUI_RAGLOG") == "1":   # ui-test-116: does a right click during a ragdoll drag reach the panel, is the catcher hovered then
        pm.call("lpr", K_STR, "Conv_BoolToString", inp={"InBool": "@isr.ReturnValue"}); pm.call("lph", K_STR, "Conv_BoolToString", inp={"InBool": "@hov.ReturnValue"})
        pm.get("gm6", "Manager"); pm.get("lpg", "RagGrab", cls=MGR); pm.link("gm6.Manager", "lpg.self"); pm.call("lpgs", K_STR, "Conv_BoolToString", inp={"InBool": "@lpg.RagGrab"})
        pm.call("lc1", K_STR, "Concat_StrStr", inp={"A": "panel down right=", "B": "@lpr.ReturnValue"}); pm.call("lc2", K_STR, "Concat_StrStr", inp={"A": "@lc1.ReturnValue", "B": " hov="})
        pm.call("lc3", K_STR, "Concat_StrStr", inp={"A": "@lc2.ReturnValue", "B": "@lph.ReturnValue"}); pm.call("lc4", K_STR, "Concat_StrStr", inp={"A": "@lc3.ReturnValue", "B": " grab="})
        pm.call("lc5", K_STR, "Concat_StrStr", inp={"A": "@lc4.ReturnValue", "B": "@lpgs.ReturnValue"}); pm.get("gm7", "Manager"); pm.call("lgp", MGR, "Log Line", inp={"self": "@gm7.Manager", "text": "@lc5.ReturnValue"}); lgpm = ["lgp"]
    # the grab check comes before the hover check: while the panel holds the mouse for the drag the catcher is not hovered (RAGLOG, ui-test-116)
    pm.chain("entry", "cm", *lgpm, "bpg", "rpg", "r3"); pm.chain("bpg:else", "bh", "bd", "bj", "return"); pm.chain("bh:else", "r2"); pm.chain("bj:else", "r2")
    # OnMouseWheel: a frozen ragdoll being dragged -> Manager.Rag Lift(notches), Handled (the panel holds the mouse during the drag, so the
    # player controller's wheel axis does not see it); else Unhandled as before
    mw = G(); mw.get("gm", "Manager"); mw.get("grm", "RagMove", cls=MGR); mw.link("gm.Manager", "grm.self"); mw.branch("b", "@grm.RagMove")
    mw.call("wd", K_IN, "PointerEvent_GetWheelDelta", inp={"Input": "@entry.MouseEvent"}); mw.get("gm2", "Manager"); mw.call("rl", MGR, "Rag Lift", inp={"self": "@gm2.Manager", "notches": "@wd.ReturnValue"})
    mw.call("h", K_WBL, "Handled"); mw.link("h.ReturnValue", "return.ReturnValue")
    mw.n("r2", "return_new"); mw.call("u", K_WBL, "Unhandled"); mw.link("u.ReturnValue", "r2.ReturnValue")
    mw.chain("entry", "b", "rl", "return"); mw.chain("b:else", "r2")
    # OnMouseMove: drag running -> Manager.Jodi Drag(cursor delta), Handled; else Unhandled
    mm = G(); mm.get("gm", "Manager"); mm.get("gjd", "JodiDrag", cls=MGR); mm.link("gm.Manager", "gjd.self"); mm.branch("b", "@gjd.JodiDrag")
    mm.call("cd", K_IN, "PointerEvent_GetCursorDelta", inp={"Input": "@entry.MouseEvent"}); mm.call("bv", K_MATH, "BreakVector2D", inp={"InVec": "@cd.ReturnValue"})
    mm.get("gm2", "Manager"); mm.call("jd", MGR, "Jodi Drag", inp={"self": "@gm2.Manager", "dx": "@bv.X", "dy": "@bv.Y", "shift": "false"})
    mm.call("h", K_WBL, "Handled"); mm.link("h.ReturnValue", "return.ReturnValue")
    mm.n("r2", "return_new"); mm.call("u", K_WBL, "Unhandled"); mm.link("u.ReturnValue", "r2.ReturnValue")
    mm.chain("entry", "b", "jd", "return"); mm.chain("b:else", "r2")
    # OnMouseButtonUp: drag running -> End Jodi Drag + release the capture, Handled; else Unhandled
    mu = G(); mu.get("gm", "Manager"); mu.get("gjd", "JodiDrag", cls=MGR); mu.link("gm.Manager", "gjd.self"); mu.branch("b", "@gjd.JodiDrag")
    mu.get("gm2", "Manager"); mu.call("ed", MGR, "End Jodi Drag", inp={"self": "@gm2.Manager"})
    mu.get("gm3", "Manager"); mu.call("fp", MGR, "Focus Color Keys", inp={"self": "@gm3.Manager"})   # a drag beside an open palette: Esc closes it (through the panel)
    mu.call("h", K_WBL, "Handled"); mu.call("rel", K_WBL, "ReleaseMouseCapture", inp={"Reply": "@h.ReturnValue"}); mu.link("rel.ReturnValue", "return.ReturnValue")
    mu.n("r2", "return_new"); mu.call("u", K_WBL, "Unhandled"); mu.link("u.ReturnValue", "r2.ReturnValue")
    mu.chain("entry", "b", "ed", "fp", "return"); mu.chain("b:else", "r2")
    # Set Page(page): exactly one page visible (Clothes = HB, Outfits = OutfitScroll, Bag = BagScroll)
    sp = G(); pages = [("HB", "Clothes"), ("OutfitScroll", "Outfits"), ("LooksScroll", "Looks"), ("BagScroll", "Bag"), ("InventoryVB", "Inventory"), ("FollowersVB", "Followers"), ("HairScroll", "Hair"), ("PoseHB", "Poses"), ("WeaponHB", "Weapons"), ("ModsHB", "Mods"), ("FaceHB", "Face"), ("LookHB", "Look"), ("BodyBox", "Body"), ("OptionsHB", "Options"), ("ContentBox", "Content"), ("ManageHB", "Manage"), ("RagScroll", "Ragdolls"), ("KodexHB", "Kodex")]
    sp.set("sk", "TmpKnown", inp={"TmpKnown": "false"})
    for i, (wn, page) in enumerate(pages):
        sp.call("eq%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@entry.page", "B": page}); sp.branch("b%d" % i, "@eq%d.ReturnValue" % i)
        sp.get("g%d" % i, wn); sp.call("v%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@g%d.%s" % (i, wn), "InVisibility": "Visible"})
        sp.set("k%d" % i, "TmpKnown", inp={"TmpKnown": "true"})
        sp.get("h%d" % i, wn); sp.call("c%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@h%d.%s" % (i, wn), "InVisibility": "Collapsed"})
        sp.chain("b%d" % i, "v%d" % i, "k%d" % i); sp.chain("b%d:else" % i, "c%d" % i)
        nxt = "b%d" % (i + 1) if i + 1 < len(pages) else "bk"
        sp.chain("k%d" % i, nxt); sp.chain("c%d" % i, nxt)
    # unknown page (Coiffure/Appearance/Body Shape): placeholder
    sp.get("gk", "TmpKnown"); sp.branch("bk", "@gk.TmpKnown")
    sp.get("gp0", "PlaceholderScroll"); sp.call("pc", E_WIDGET, "SetVisibility", inp={"self": "@gp0.PlaceholderScroll", "InVisibility": "Collapsed"})
    sp.get("gp1", "PlaceholderScroll"); sp.call("pv", E_WIDGET, "SetVisibility", inp={"self": "@gp1.PlaceholderScroll", "InVisibility": "Visible"})
    sp.chain("entry", "sk", "b0"); sp.chain("bk", "pc"); sp.chain("bk:else", "pv")
    qkh = G(); qkh.get("g", "LblQuickKeyHint"); qkh.call("s", E_TEXT, "SetText", inp={"self": "@g.LblQuickKeyHint", "InText": "@entry.text"}); qkh.chain("entry", "s")
    kbh = G(); kbh.get("g", "KeyBindHint"); kbh.call("s", E_TEXT, "SetText", inp={"self": "@g.KeyBindHint", "InText": "@entry.text"}); kbh.chain("entry", "s")
    # Set Option Cat(cat): exactly one category block of the Options page visible, scrolled to the top
    soc = G(); tail = ["entry"]
    for i, cat in enumerate(OPT_CATS):
        wn = "OptCat_" + cat
        soc.call("eq%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@entry.cat", "B": cat})
        soc.branch("b%d" % i, "@eq%d.ReturnValue" % i)
        soc.get("g%d" % i, wn); soc.call("v%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@g%d.%s" % (i, wn), "InVisibility": "Visible"})
        soc.get("h%d" % i, wn); soc.call("c%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@h%d.%s" % (i, wn), "InVisibility": "Collapsed"})
        for t in tail: soc.chain(t, "b%d" % i)
        soc.chain("b%d" % i, "v%d" % i); soc.chain("b%d:else" % i, "c%d" % i); tail = ["v%d" % i, "c%d" % i]
    # to the top only when the category changes (2026-10-17: rebuilding the page for a picture / theme chip jumped to the top); a jump
    # to the top drops the remembered offsets, so the delayed Restore Scrolls of a rebuild does not undo it
    soc.get("gsc", "ShownOptCat"); soc.call("chg", K_MATH, "NotEqual_NameName", inp={"A": "@gsc.ShownOptCat", "B": "@entry.cat"}); soc.branch("bchg", "@chg.ReturnValue")
    soc.set("ssc", "ShownOptCat", inp={"ShownOptCat": "@entry.cat"}); soc.get("gsm", "ScrollMem"); soc.call("csm", K_ARR, "Array_Clear", inp={"TargetArray": "@gsm.ScrollMem"})
    soc.get("gos", "OptionsScroll"); soc.call("sts", U_SCROLL, "ScrollToStart", inp={"self": "@gos.OptionsScroll"})
    for t in tail: soc.chain(t, "bchg")
    soc.chain("bchg", "ssc", "csm", "sts")
    # read / set the body sliders (values 0..1, displayed as percent)
    # vanilla breast / waist: slider 0..1 <-> value VANILLA_RANGE (the game's own UI covers 0..1 = 0..100 %)
    vlo, vhi = bg.VANILLA_RANGE
    gb = G()
    for k, _ in BODY_ROWS:
        gb.get("g" + k, "Sld" + k); gb.call("v" + k, E_SLIDER, "GetValue", inp={"self": "@g%s.Sld%s" % (k, k)})
        gb.call("vm" + k, K_MATH, "Multiply_FloatFloat", inp={"A": "@v%s.ReturnValue" % k, "B": str(vhi - vlo)}); gb.call("va" + k, K_MATH, "Add_FloatFloat", inp={"A": "@vm%s.ReturnValue" % k, "B": str(vlo)})
        gb.link("va%s.ReturnValue" % k, "return." + k.lower())
    gb.chain("entry", "return")
    sb = G(); tail = ["entry"]
    for k, _ in BODY_ROWS:
        sb.call("vs" + k, K_MATH, "Subtract_FloatFloat", inp={"A": "@entry." + k.lower(), "B": str(vlo)}); sb.call("vd" + k, K_MATH, "Divide_FloatFloat", inp={"A": "@vs%s.ReturnValue" % k, "B": str(vhi - vlo)})
        sb.get("g" + k, "Sld" + k); sb.call("s" + k, E_SLIDER, "SetValue", inp={"self": "@g%s.Sld%s" % (k, k), "InValue": "@vd%s.ReturnValue" % k}); tail.append("s" + k)
        sb.call("m" + k, K_MATH, "Multiply_FloatFloat", inp={"A": "@entry." + k.lower(), "B": "100.0"}); sb.call("r" + k, K_MATH, "Round", inp={"A": "@m%s.ReturnValue" % k})
        sb.call("i" + k, K_STR, "Conv_IntToString", inp={"InInt": "@r%s.ReturnValue" % k}); sb.call("c" + k, K_STR, "Concat_StrStr", inp={"A": "@i%s.ReturnValue" % k, "B": " %"})
        sb.call("t" + k, K_TXT, "Conv_StringToText", inp={"InString": "@c%s.ReturnValue" % k})
        sb.get("gv" + k, "Val" + k); sb.call("st" + k, E_TEXT, "SetText", inp={"self": "@gv%s.Val%s" % (k, k), "InText": "@t%s.ReturnValue" % k}); tail.append("st" + k)
    sb.chain(*tail)
    # bone-scale sliders: raw 0..1 values; the display shows the factor FACTOR_MIN + (FACTOR_MAX - FACTOR_MIN) * value as "x1.00"
    gsc = G()
    for k, key in SCALE_ROWS:
        gsc.get("g" + k, "Sld" + k); gsc.call("v" + k, E_SLIDER, "GetValue", inp={"self": "@g%s.Sld%s" % (k, k)}); gsc.link("v%s.ReturnValue" % k, "return." + key.lower())
    gsc.chain("entry", "return")
    ssc = G(); tail = ["entry"]
    for k, key in SCALE_ROWS:
        ssc.get("g" + k, "Sld" + k); ssc.call("s" + k, E_SLIDER, "SetValue", inp={"self": "@g%s.Sld%s" % (k, k), "InValue": "@entry." + key.lower()}); tail.append("s" + k)
        lo, hi = bg.factor_range(key)
        ssc.call("m" + k, K_MATH, "Multiply_FloatFloat", inp={"A": "@entry." + key.lower(), "B": str(hi - lo)}); ssc.call("a" + k, K_MATH, "Add_FloatFloat", inp={"A": "@m%s.ReturnValue" % k, "B": str(lo)})
        tpin = factor_text(ssc, "t" + k, key, "@a%s.ReturnValue" % k)   # x1.00 / 75 % / 5° / 0.40 (bodyscale_groups.DISPLAY)
        ssc.get("gv" + k, "Val" + k); ssc.call("st" + k, E_TEXT, "SetText", inp={"self": "@gv%s.Val%s" % (k, k), "InText": tpin}); tail.append("st" + k)
    ssc.chain(*tail)
    esc = G(); tail = ["entry"]
    for k, key in SCALE_ROWS:
        if key in bg.ALL_BODIES: continue   # component scale / the game's physics / a morph: every body
        esc.get("g" + k, "Sld" + k); esc.call("e" + k, E_WIDGET, "SetIsEnabled", inp={"self": "@g%s.Sld%s" % (k, k), "bInIsEnabled": "@entry.enabled"}); tail.append("e" + k)
    esc.chain(*tail)
    # read / set the option sliders (0..1; display computed by the manager)
    gov = G()
    for k, _ in OPTION_ROWS:
        gov.get("g" + k, "Sld" + k); gov.call("v" + k, E_SLIDER, "GetValue", inp={"self": "@g%s.Sld%s" % (k, k)}); gov.link("v%s.ReturnValue" % k, "return." + k.lower())
    gov.get("gu", "OptUnlimited"); gov.call("vu", E_CHECK, "IsChecked", inp={"self": "@gu.OptUnlimited"}); gov.link("vu.ReturnValue", "return.unlimited")
    gov.get("gpn", "OptPan"); gov.call("vp", E_CHECK, "IsChecked", inp={"self": "@gpn.OptPan"}); gov.link("vp.ReturnValue", "return.pan")
    gov.get("gcr", "OptCamRight"); gov.call("vcr", E_CHECK, "IsChecked", inp={"self": "@gcr.OptCamRight"}); gov.link("vcr.ReturnValue", "return.camright")
    gov.get("gnd", "OptNude"); gov.call("vn", E_CHECK, "IsChecked", inp={"self": "@gnd.OptNude"}); gov.link("vn.ReturnValue", "return.nude")
    gov.get("gmg", "OptMerge"); gov.call("vm", E_CHECK, "IsChecked", inp={"self": "@gmg.OptMerge"}); gov.link("vm.ReturnValue", "return.merge")
    gov.get("gmm", "OptMergeMods"); gov.call("vmm", E_CHECK, "IsChecked", inp={"self": "@gmm.OptMergeMods"}); gov.link("vmm.ReturnValue", "return.mergemods")
    gov.get("gcsh", "OptChipSearch"); gov.call("vcsh", E_CHECK, "IsChecked", inp={"self": "@gcsh.OptChipSearch"}); gov.link("vcsh.ReturnValue", "return.chipsearch")
    gov.get("gtp", "OptTipNoPrefix"); gov.call("vtp", E_CHECK, "IsChecked", inp={"self": "@gtp.OptTipNoPrefix"}); gov.link("vtp.ReturnValue", "return.tipnoprefix")
    gov.get("gti", "OptTipNoIds"); gov.call("vti", E_CHECK, "IsChecked", inp={"self": "@gti.OptTipNoIds"}); gov.link("vti.ReturnValue", "return.tipnoids")
    gov.get("gkx", "OptKodexAll"); gov.call("vkx", E_CHECK, "IsChecked", inp={"self": "@gkx.OptKodexAll"}); gov.link("vkx.ReturnValue", "return.kodexall")
    gov.get("gic", "OptInvCatalog"); gov.call("vic", E_CHECK, "IsChecked", inp={"self": "@gic.OptInvCatalog"}); gov.link("vic.ReturnValue", "return.invcatalog")
    gov.get("gia", "OptInvAutoEquip"); gov.call("via", E_CHECK, "IsChecked", inp={"self": "@gia.OptInvAutoEquip"}); gov.link("via.ReturnValue", "return.invautoequip")
    gov.get("gmo", "OptMoveOn"); gov.call("vmo", E_CHECK, "IsChecked", inp={"self": "@gmo.OptMoveOn"}); gov.link("vmo.ReturnValue", "return.moveon")
    gov.get("gsmo", "OptSlowMoOn"); gov.call("vsmo", E_CHECK, "IsChecked", inp={"self": "@gsmo.OptSlowMoOn"}); gov.link("vsmo.ReturnValue", "return.slowmoon")
    for k in ("FreeNoCollide", "FreeNoLimit", "NoNotices"):
        gov.get("g" + k, "Opt" + k); gov.call("v" + k, E_CHECK, "IsChecked", inp={"self": "@g%s.Opt%s" % (k, k)}); gov.link("v%s.ReturnValue" % k, "return." + k.lower())
    gov.chain("entry", "return")
    # static texts (language): search field hint + labels
    sst = G(); tail = ["entry"]
    for p, widget in PANEL_TEXTS:
        sst.get("g" + p, widget)
        if widget in ("Search", "ManageSearch", "LookSearch", "PoseSearch", "WeaponSearch", "ChipSearch", "LookChipSearch", "ThemeNameEdit", "ManageChipSearch", "InvSearch"):
            sst.call("s" + p, E_EDIT, "SetHintText", inp={"self": "@g%s.%s" % (p, widget), "InText": "@entry." + p})
        else:
            sst.call("s" + p, E_TEXT, "SetText", inp={"self": "@g%s.%s" % (p, widget), "InText": "@entry." + p})
        tail.append("s" + p)
    sst.chain(*tail)
    su = G(); su.get("g", "OptUnlimited"); su.call("s", E_CHECK, "SetIsChecked", inp={"self": "@g.OptUnlimited", "InIsChecked": "@entry.unlimited"})
    su.get("g2", "OptPan"); su.call("s2", E_CHECK, "SetIsChecked", inp={"self": "@g2.OptPan", "InIsChecked": "@entry.pan"})
    su.get("g3", "OptNude"); su.call("s3", E_CHECK, "SetIsChecked", inp={"self": "@g3.OptNude", "InIsChecked": "@entry.nude"})
    su.get("g4", "OptMerge"); su.call("s4", E_CHECK, "SetIsChecked", inp={"self": "@g4.OptMerge", "InIsChecked": "@entry.merge"})
    su.get("g5", "OptTipNoPrefix"); su.call("s5", E_CHECK, "SetIsChecked", inp={"self": "@g5.OptTipNoPrefix", "InIsChecked": "@entry.tipnoprefix"})
    su.get("g6", "OptTipNoIds"); su.call("s6", E_CHECK, "SetIsChecked", inp={"self": "@g6.OptTipNoIds", "InIsChecked": "@entry.tipnoids"})
    su.get("g7", "OptMergeMods"); su.call("s7", E_CHECK, "SetIsChecked", inp={"self": "@g7.OptMergeMods", "InIsChecked": "@entry.mergemods"})
    su.get("g9", "OptChipSearch"); su.call("s9", E_CHECK, "SetIsChecked", inp={"self": "@g9.OptChipSearch", "InIsChecked": "@entry.chipsearch"})
    su.get("g8", "OptCamRight"); su.call("s8", E_CHECK, "SetIsChecked", inp={"self": "@g8.OptCamRight", "InIsChecked": "@entry.camright"}); su.get("g10", "OptKodexAll"); su.call("s10", E_CHECK, "SetIsChecked", inp={"self": "@g10.OptKodexAll", "InIsChecked": "@entry.kodexall"})
    su.get("g11", "OptMoveOn"); su.call("s11", E_CHECK, "SetIsChecked", inp={"self": "@g11.OptMoveOn", "InIsChecked": "@entry.moveon"})
    su.get("g12", "OptInvCatalog"); su.call("s12", E_CHECK, "SetIsChecked", inp={"self": "@g12.OptInvCatalog", "InIsChecked": "@entry.invcatalog"})
    su.get("g13", "OptInvAutoEquip"); su.call("s13", E_CHECK, "SetIsChecked", inp={"self": "@g13.OptInvAutoEquip", "InIsChecked": "@entry.invautoequip"})
    su.get("g14", "OptSlowMoOn"); su.call("s14", E_CHECK, "SetIsChecked", inp={"self": "@g14.OptSlowMoOn", "InIsChecked": "@entry.slowmoon"})
    for k in ("FreeNoCollide", "FreeNoLimit", "NoNotices"):
        su.get("g" + k, "Opt" + k); su.call("s" + k, E_CHECK, "SetIsChecked", inp={"self": "@g%s.Opt%s" % (k, k), "InIsChecked": "@entry." + k.lower()})
    su.chain("entry", "s", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11", "s12", "s13", "s14", "sFreeNoCollide", "sFreeNoLimit", "sNoNotices")
    # keep the left side of the panel free: anchor of the background border (Minimum.X = fraction)
    la = G(); la.get("g", "Bg"); la.call("sl", "/Script/UMG.WidgetLayoutLibrary", "SlotAsCanvasSlot", inp={"Widget": "@g.Bg"})
    la.call("mk", K_MATH, "MakeVector2D", inp={"X": "@entry.fraction", "Y": "0.0"})
    la.make("an", "/Script/Slate.Anchors", Minimum="@mk.ReturnValue", Maximum="(X=1,Y=1)")
    la.call("sa", "/Script/UMG.CanvasPanelSlot", "SetAnchors", inp={"self": "@sl.ReturnValue", "InAnchors": "@an.Anchors"})
    la.get("gil", "BgImgLayer"); la.call("sli", "/Script/UMG.WidgetLayoutLibrary", "SlotAsCanvasSlot", inp={"Widget": "@gil.BgImgLayer"})
    la.call("sai", "/Script/UMG.CanvasPanelSlot", "SetAnchors", inp={"self": "@sli.ReturnValue", "InAnchors": "@an.Anchors"})
    # +/- buttons: anchored at the edge of the free area, visible only when a free area exists
    la.call("mk2", K_MATH, "MakeVector2D", inp={"X": "@entry.fraction", "Y": "1.0"}); la.make("an2", "/Script/Slate.Anchors", Minimum="@mk2.ReturnValue", Maximum="@mk2.ReturnValue")
    la.call("gt0", K_MATH, "Greater_FloatFloat", inp={"A": "@entry.fraction", "B": "0.0"}); la.branch("bv", "@gt0.ReturnValue")
    tail = ["sa", "sai"]; on = ["bv"]; off = ["bv:else"]
    for b in ("BtnPlus", "BtnMinus", "BtnCam", "BtnPhoto", "BtnRag"):
        la.get("g" + b, b); la.call("sl" + b, "/Script/UMG.WidgetLayoutLibrary", "SlotAsCanvasSlot", inp={"Widget": "@g%s.%s" % (b, b)})
        la.call("sa" + b, "/Script/UMG.CanvasPanelSlot", "SetAnchors", inp={"self": "@sl%s.ReturnValue" % b, "InAnchors": "@an2.Anchors"}); tail.append("sa" + b)
        la.get("h" + b, b); la.call("sv" + b, E_WIDGET, "SetVisibility", inp={"self": "@h%s.%s" % (b, b), "InVisibility": "Visible"}); on.append("sv" + b)
        la.get("k" + b, b); la.call("sc" + b, E_WIDGET, "SetVisibility", inp={"self": "@k%s.%s" % (b, b), "InVisibility": "Collapsed"}); off.append("sc" + b)
    # Jodi catcher: 0..fraction over the full height, visible only with a free area
    la.make("an3", "/Script/Slate.Anchors", Minimum="(X=0,Y=0)", Maximum="@mk2.ReturnValue")
    la.get("gjc", "JodiCatcher"); la.call("sljc", "/Script/UMG.WidgetLayoutLibrary", "SlotAsCanvasSlot", inp={"Widget": "@gjc.JodiCatcher"})
    la.call("sajc", "/Script/UMG.CanvasPanelSlot", "SetAnchors", inp={"self": "@sljc.ReturnValue", "InAnchors": "@an3.Anchors"}); tail.append("sajc")
    la.get("hjc", "JodiCatcher"); la.call("svjc", E_WIDGET, "SetVisibility", inp={"self": "@hjc.JodiCatcher", "InVisibility": "Visible"}); on.append("svjc")
    la.get("kjc", "JodiCatcher"); la.call("scjc", E_WIDGET, "SetVisibility", inp={"self": "@kjc.JodiCatcher", "InVisibility": "Collapsed"}); off.append("scjc")
    la.chain("entry", *tail, "bv"); la.chain(*on); la.chain(*off)
    # +/- round buttons: pass the manager through, set action + icon (tree instances otherwise never get an init)
    ib = G(); tail = ["entry"]
    for b, action, tex, tipkey in (("BtnPlus", "DistPlus", T_PLUS, "Tip_DistPlus"), ("BtnMinus", "DistMinus", T_MINUS, "Tip_DistMinus"),
                                   ("BtnCam", "FreeCam", T_CAM, "Tip_FreeCam"), ("BtnPhoto", "PhotoMode", T_PHOTO, "Tip_PhotoMode"), ("BtnRag", "ModeRagdoll", M + "/T_RagMode", "Tip_RagdollMode")):
        ib.get("g" + b, b); ib.get("m" + b, "Manager"); ib.n("s" + b, "set", var="Manager", cls=W_ROUND, inp={"self": "@g%s.%s" % (b, b), "Manager": "@m%s.Manager" % b})
        ib.get("h" + b, b); ib.call("i" + b, W_ROUND, "Init", inp={"self": "@h%s.%s" % (b, b), "action": action, "icon": tex, "tip": mt(ib, "t" + b, tipkey)}); tail += ["s" + b, "i" + b]
    ib.chain(*tail)
    # Set Cam Mode(on): free cam hides Bg + the round buttons (input goes to the game viewport meanwhile); off restores Bg (buttons come back via Set Left Free)
    scm = G(); scm.branch("b", "@entry.on"); on = ["b"]
    for i, wn in enumerate(("Bg", "BtnPlus", "BtnMinus", "BtnCam", "BtnPhoto", "BtnRag", "JodiCatcher")):
        scm.get("g%d" % i, wn); scm.call("c%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@g%d.%s" % (i, wn), "InVisibility": "Collapsed"}); on.append("c%d" % i)
    scm.get("gbg", "Bg"); scm.call("vbg", E_WIDGET, "SetVisibility", inp={"self": "@gbg.Bg", "InVisibility": "Visible"})
    scm.get("gil", "BgImgLayer"); scm.call("cil", E_WIDGET, "SetVisibility", inp={"self": "@gil.BgImgLayer", "InVisibility": "Collapsed"}); on.append("cil")
    scm.get("gio", "BgImgOn"); scm.branch("bio", "@gio.BgImgOn")
    scm.get("gil2", "BgImgLayer"); scm.call("vil", E_WIDGET, "SetVisibility", inp={"self": "@gil2.BgImgLayer", "InVisibility": "HitTestInvisible"})
    scm.chain("entry", *on); scm.chain("b:else", "vbg", "bio", "vil")
    # Set Palette Lock(on): the game's Show Palette makes the whole panel HitTestInvisible + disabled, which also takes the Jodi catcher
    # away (a click on her went to the viewport = camera). on: panel back to Visible + enabled, only Bg and the round buttons disabled
    # (dimmed, no clicks); off (Close Color, every way the palette closes): Bg and the buttons enabled again
    spl = G(); spl.call("nt", K_MATH, "Not_PreBool", inp={"A": "@entry.on"}); tail = ["entry"]
    for i, wn in enumerate(("Bg", "BtnPlus", "BtnMinus", "BtnCam", "BtnPhoto", "BtnRag")):
        spl.get("g%d" % i, wn); spl.call("e%d" % i, E_WIDGET, "SetIsEnabled", inp={"self": "@g%d.%s" % (i, wn), "bInIsEnabled": "@nt.ReturnValue"}); tail.append("e%d" % i)
    spl.branch("b", "@entry.on"); spl.self_("me"); spl.call("sv", E_WIDGET, "SetVisibility", inp={"self": "@me.self", "InVisibility": "Visible"})
    spl.self_("me2"); spl.call("en", E_WIDGET, "SetIsEnabled", inp={"self": "@me2.self", "bInIsEnabled": "true"})
    spl.chain(*tail, "b", "sv", "en")
    sov = G(); tail = ["entry"]
    for k, _ in OPTION_ROWS:
        sov.get("g" + k, "Sld" + k); sov.call("s" + k, E_SLIDER, "SetValue", inp={"self": "@g%s.Sld%s" % (k, k), "InValue": "@entry." + k.lower()}); tail.append("s" + k)
        sov.get("gv" + k, "Val" + k); sov.call("st" + k, E_TEXT, "SetText", inp={"self": "@gv%s.Val%s" % (k, k), "InText": "@entry." + k.lower() + " text"}); tail.append("st" + k)
    sov.chain(*tail)
    # max height of the group chip area (option; unscaled units -> x SC)
    sth = G(); sth.call("m", K_MATH, "Multiply_FloatFloat", inp={"A": "@entry.height", "B": str(SC)})
    sth.get("gb", "SubTabsBox"); sth.call("s", U_SIZE, "SetMaxDesiredHeight", inp={"self": "@gb.SubTabsBox", "InMaxDesiredHeight": "@m.ReturnValue"})
    sth.get("gbl", "LookSubTabsBox"); sth.call("sl", U_SIZE, "SetMaxDesiredHeight", inp={"self": "@gbl.LookSubTabsBox", "InMaxDesiredHeight": "@m.ReturnValue"})
    sth.get("gbp", "PoseSubTabsBox"); sth.call("sp", U_SIZE, "SetMaxDesiredHeight", inp={"self": "@gbp.PoseSubTabsBox", "InMaxDesiredHeight": "@m.ReturnValue"})
    sth.get("gbw", "WeaponSubTabsBox"); sth.call("sw", U_SIZE, "SetMaxDesiredHeight", inp={"self": "@gbw.WeaponSubTabsBox", "InMaxDesiredHeight": "@m.ReturnValue"})
    sth.get("gbm", "ManageSubTabsBox"); sth.call("sm", U_SIZE, "SetMaxDesiredHeight", inp={"self": "@gbm.ManageSubTabsBox", "InMaxDesiredHeight": "@m.ReturnValue"})
    sth.get("gbb", "BodyChipsBox"); sth.call("sb", U_SIZE, "SetMaxDesiredHeight", inp={"self": "@gbb.BodyChipsBox", "InMaxDesiredHeight": "@m.ReturnValue"}); sth.chain("entry", "s", "sl", "sp", "sw", "sm", "sb")
    # scroll multiplier for all scroll areas
    sm = G(); tail = ["entry"]
    for i, wn in enumerate(SCROLL_PAGES):
        sm.get("g%d" % i, wn); sm.call("s%d" % i, U_SCROLL, "SetWheelScrollMultiplier", inp={"self": "@g%d.%s" % (i, wn), "NewWheelScrollMultiplier": "@entry.mult"}); tail.append("s%d" % i)
    sm.chain(*tail)
    # bring the checkbox boxes to the actual height of the search field (Tick; only sets on change)
    # check boxes next to a search box follow the search box height (clothes page: SearchFrame, Manage page: MSearchFrame - the collapsed one reports 0)
    cs2 = G(); cs2.get("gsf", "SearchFrame"); cs2.call("ds", E_WIDGET, "GetDesiredSize", inp={"self": "@gsf.SearchFrame"}); cs2.call("bv0", K_MATH, "BreakVector2D", inp={"InVec": "@ds.ReturnValue"})
    cs2.get("gmf", "MSearchFrame"); cs2.call("dsm", E_WIDGET, "GetDesiredSize", inp={"self": "@gmf.MSearchFrame"}); cs2.call("bvm", K_MATH, "BreakVector2D", inp={"InVec": "@dsm.ReturnValue"})
    cs2.call("bv", K_MATH, "FMax", inp={"A": "@bv0.Y", "B": "@bvm.Y"})
    cs2.get("gcs", "CheckSize"); cs2.call("ne0", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@bv.ReturnValue", "B": "@gcs.CheckSize", "ErrorTolerance": "0.5"}); cs2.call("ne", K_MATH, "Not_PreBool", inp={"A": "@ne0.ReturnValue"})
    cs2.call("gt", K_MATH, "Greater_FloatFloat", inp={"A": "@bv.ReturnValue", "B": "1.0"}); cs2.call("and", K_MATH, "BooleanAND", inp={"A": "@ne.ReturnValue", "B": "@gt.ReturnValue"}); cs2.branch("b", "@and.ReturnValue")
    cs2.set("scs", "CheckSize", inp={"CheckSize": "@bv.ReturnValue"}); tail = ["entry", "b", "scs"]
    for i, wn in enumerate(["OwnedBox", "FavBox", "VanillaBox", "OnlyModsBox", "CaseSensBox"]):
        cs2.get("g%d" % i, wn); cs2.call("w%d" % i, U_SIZE, "SetWidthOverride", inp={"self": "@g%d.%s" % (i, wn), "InWidthOverride": "@bv.ReturnValue"})
        cs2.get("h%d" % i, wn); cs2.call("hh%d" % i, U_SIZE, "SetHeightOverride", inp={"self": "@h%d.%s" % (i, wn), "InHeightOverride": "@bv.ReturnValue"}); tail += ["w%d" % i, "hh%d" % i]
    cs2.chain(*tail)
    # clear search / list hint
    cs = G(); cs.get("g", "Search"); cs.call("st", E_EDIT, "SetText", inp={"self": "@g.Search", "InText": ""}); cs.chain("entry", "st")
    lh = G(); lh.branch("b", "@entry.visible")
    lh.get("g0", "ListHint"); lh.call("v0", E_WIDGET, "SetVisibility", inp={"self": "@g0.ListHint", "InVisibility": "Visible"})
    lh.get("h0", "ListHint"); lh.call("c0", E_WIDGET, "SetVisibility", inp={"self": "@h0.ListHint", "InVisibility": "Collapsed"})
    lh.chain("entry", "b", "v0"); lh.chain("b:else", "c0")
    # BagEmpty hint
    be = G(); be.branch("b", "@entry.visible")
    be.get("g0", "BagEmpty"); be.call("v0", E_WIDGET, "SetVisibility", inp={"self": "@g0.BagEmpty", "InVisibility": "Visible"})
    be.get("h0", "BagEmpty"); be.call("c0", E_WIDGET, "SetVisibility", inp={"self": "@h0.BagEmpty", "InVisibility": "Collapsed"})
    be.chain("entry", "b", "v0"); be.chain("b:else", "c0")
    ft = G(); ft.get("g1", "OnlyOwned"); ft.call("c1", E_CHECK, "SetIsChecked", inp={"self": "@g1.OnlyOwned", "InIsChecked": "@entry.owned"})
    ft.get("g2", "OnlyFav"); ft.call("c2", E_CHECK, "SetIsChecked", inp={"self": "@g2.OnlyFav", "InIsChecked": "@entry.fav"})
    ft.get("g3", "OnlyVanilla"); ft.call("c3", E_CHECK, "SetIsChecked", inp={"self": "@g3.OnlyVanilla", "InIsChecked": "@entry.vanilla"})
    ft.get("g4", "OnlyWorn"); ft.call("c4", E_CHECK, "SetIsChecked", inp={"self": "@g4.OnlyWorn", "InIsChecked": "@entry.worn"}); ft.chain("entry", "c1", "c2", "c3", "c4")
    # Apply Theme: panel-owned parts from Manager.Col* (background, status line, search box, headings, labels, slider bars)
    at = G(); tail = ["entry"]
    brush(at, "sbg", "Bg", mcol(at, "cbg", "ColBg"), tail); brush(at, "ssl", "StatusLine", mcol(at, "csl", "ColStatusLine"), tail)
    brush(at, "ssf", "SearchFrame", mcol(at, "csf", "ColChipFrame"), tail); brush(at, "ssi", "SearchFill", mcol(at, "csi", "ColChip"), tail)
    # these frames kept their static colours: after a theme change every search box but the clothes page's sat visibly
    # beside it - and the new chip search sits directly above one of them.
    for _i, (_fr, _fi) in enumerate([("CSearchFrame", "CSearchFill"), ("LCSearchFrame", "LCSearchFill"), ("LSearchFrame", "LSearchFill"), ("PSearchFrame", "PSearchFill"),
                                     ("WSearchFrame", "WSearchFill"), ("MSearchFrame", "MSearchFill"), ("ISearchFrame", "ISearchFill")]):
        brush(at, "sf%d" % _i, _fr, mcol(at, "cf%d" % _i, "ColChipFrame"), tail)
        brush(at, "si%d" % _i, _fi, mcol(at, "ci%d" % _i, "ColChip"), tail)
    for col, names in PANEL_TEXT_COLORS.items():
        pin = mcol(at, "c_" + col, col)
        for wn in names: text_color(at, "t_" + wn, wn, pin, tail)
    sld = mcol(at, "c_slider", "ColSlider")
    for k, _ in OPTION_ROWS + BODY_ROWS + SCALE_ROWS:
        at.get("gs_" + k, "Sld" + k); at.call("ss_" + k, E_SLIDER, "SetSliderBarColor", inp={"self": "@gs_%s.Sld%s" % (k, k), "InValue": sld}); tail.append("ss_" + k)
    at.chain(*tail); prev = tail[-1]
    # element widgets visible while the theme is edited (Options page + top tabs + status bar): Refresh Theme; every other page is rebuilt on select
    for i, (box, cls) in enumerate(THEME_REFRESH):
        at.get("rg%d" % i, box); at.call("rc%d" % i, U_PANELW, "GetAllChildren", inp={"self": "@rg%d.%s" % (i, box)})
        at.foreach("rf%d" % i, "@rc%d.ReturnValue" % i); wp = "@rx%d.As%s" % (i, cls.rsplit("/", 1)[-1]); at.cast("rx%d" % i, cls, "@rf%d.Array Element" % i)
        at.call("rv%d" % i, K_SYS, "IsValid", inp={"Object": wp}); at.branch("rb%d" % i, "@rv%d.ReturnValue" % i); at.call("rr%d" % i, cls, "Refresh Theme", inp={"self": wp})
        at.chain(prev, "rf%d" % i); at.chain("rf%d" % i, "rb%d" % i, "rr%d" % i); prev = "rf%d:Completed" % i   # GetAllChildren is const -> pure
    # theme grid: clear all columns / add to column i (entries fill column-wise); slot padding between rows
    cts = G(); tail = ["entry"]
    for i in range(THEME_COLS):
        cts.get("g%d" % i, "ThemeCol%d" % i); cts.call("c%d" % i, U_PANELW, "ClearChildren", inp={"self": "@g%d.ThemeCol%d" % (i, i)}); tail.append("c%d" % i)
    cts.chain(*tail)
    ats = G(); prev = "entry"
    for i in range(THEME_COLS):
        ats.call("e%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": "@entry.column", "B": str(i)}); ats.branch("b%d" % i, "@e%d.ReturnValue" % i)
        ats.get("g%d" % i, "ThemeCol%d" % i); ats.call("a%d" % i, U_VBOX, "AddChildToVerticalBox", inp={"self": "@g%d.ThemeCol%d" % (i, i), "Content": "@entry.widget"})
        ats.call("p%d" % i, "/Script/UMG.VerticalBoxSlot", "SetPadding", inp={"self": "@a%d.ReturnValue" % i, "InPadding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(6)})
        ats.chain(prev, "b%d" % i, "a%d" % i, "p%d" % i); prev = "b%d:else" % i
    # content view: title + scroll a tile into view on the page's scroll box (Show in tab)
    # Kodex: text (an empty body is hidden), picture (None hides it), scroll to the top
    kt = G(); kt.get("gt", "KodexTitle"); kt.call("st", E_TEXT, "SetText", inp={"self": "@gt.KodexTitle", "InText": "@entry.title"})
    kt.get("gb", "KodexBody"); kt.call("sb", E_TEXT, "SetText", inp={"self": "@gb.KodexBody", "InText": "@entry.body"})
    kt.call("emp", K_TXT, "TextIsEmpty", inp={"InText": "@entry.body"})
    kt.branch("be", "@emp.ReturnValue"); kt.get("gb2", "KodexBody"); kt.call("hb", E_WIDGET, "SetVisibility", inp={"self": "@gb2.KodexBody", "InVisibility": "Collapsed"})
    kt.get("gb3", "KodexBody"); kt.call("vb", E_WIDGET, "SetVisibility", inp={"self": "@gb3.KodexBody", "InVisibility": "Visible"})
    kt.chain("entry", "st", "sb", "be", "hb"); kt.chain("be:else", "vb")
    ki = G(); ki.call("iv", K_SYS, "IsValid", inp={"Object": "@entry.tex"}); ki.branch("b", "@iv.ReturnValue")
    ki.get("gi", "KodexImage"); ki.call("sb", E_IMAGE, "SetBrushFromTexture", inp={"self": "@gi.KodexImage", "Texture": "@entry.tex", "bMatchSize": "false"})
    ki.get("gx", "KodexImageBox"); ki.call("vx", E_WIDGET, "SetVisibility", inp={"self": "@gx.KodexImageBox", "InVisibility": "Visible"})
    ki.get("gx2", "KodexImageBox"); ki.call("hx", E_WIDGET, "SetVisibility", inp={"self": "@gx2.KodexImageBox", "InVisibility": "Collapsed"})
    ki.chain("entry", "b", "sb", "vx"); ki.chain("b:else", "hx")
    rh = G(); rh.get("g", "RagHint"); rh.call("t", E_TEXT, "SetText", inp={"self": "@g.RagHint", "InText": "@entry.text"}); rh.call("e", K_TXT, "TextIsEmpty", inp={"InText": "@entry.text"})
    rh.branch("b", "@e.ReturnValue"); rh.get("g2", "RagHint"); rh.call("h", E_WIDGET, "SetVisibility", inp={"self": "@g2.RagHint", "InVisibility": "Collapsed"})
    rh.get("g3", "RagHint"); rh.call("s", E_WIDGET, "SetVisibility", inp={"self": "@g3.RagHint", "InVisibility": "Visible"}); rh.chain("entry", "t", "b", "h"); rh.chain("b:else", "s")
    rt = G(); tail = ["entry"]
    for w_, pn in (("LblRagSave", "save"), ("LblRagPresets", "presets"), ("RagPresetsHint", "hint")):
        rt.get("g" + pn, w_); rt.call("s" + pn, E_TEXT, "SetText", inp={"self": "@g%s.%s" % (pn, w_), "InText": "@entry." + pn}); tail.append("s" + pn)
    rt.chain(*tail)
    grn = G(); grn.get("g", "RagNameEdit"); grn.call("t", E_EDIT, "GetText", inp={"self": "@g.RagNameEdit"}); grn.link("t.ReturnValue", "return.text")
    crn = G(); crn.get("g", "RagNameEdit"); crn.call("st", E_EDIT, "SetText", inp={"self": "@g.RagNameEdit", "InText": ""}); crn.chain("entry", "st")
    # Weapons tab: the attachments header and list only for a weapon that takes attachments
    wav = G(); wav.branch("b", "@entry.visible"); wav.get("gh", "WeaponAttachHeader"); wav.get("gl", "WeaponAttachList")
    wav.call("v1", E_WIDGET, "SetVisibility", inp={"self": "@gh.WeaponAttachHeader", "InVisibility": "Visible"}); wav.call("v2", E_WIDGET, "SetVisibility", inp={"self": "@gl.WeaponAttachList", "InVisibility": "Visible"})
    wav.get("gh2", "WeaponAttachHeader"); wav.get("gl2", "WeaponAttachList")
    wav.call("h1", E_WIDGET, "SetVisibility", inp={"self": "@gh2.WeaponAttachHeader", "InVisibility": "Collapsed"}); wav.call("h2", E_WIDGET, "SetVisibility", inp={"self": "@gl2.WeaponAttachList", "InVisibility": "Collapsed"})
    wav.chain("entry", "b", "v1", "v2"); wav.chain("b:else", "h1", "h2")
    # Inventory: the catalogue's title and list shown only with the option on
    icv = G()
    icv.get("gt", "InvCatHead"); icv.branch("b", "@entry.on")
    icv.call("v1", E_WIDGET, "SetVisibility", inp={"self": "@gt.InvCatHead", "InVisibility": "SelfHitTestInvisible"})
    icv.get("gt2", "InvCatHead"); icv.call("h1", E_WIDGET, "SetVisibility", inp={"self": "@gt2.InvCatHead", "InVisibility": "Collapsed"})
    icv.chain("entry", "b", "v1"); icv.chain("b:else", "h1")
    # Set Inv Layout, per list: shown (else collapsed - folded, another list has the full height, catalogue off) and fill
    # (share the height; else only as high as the content: an empty list shrinks to its note)
    ilo = G(); ends = ["entry"]
    for k in ("Bag", "Box", "Cat"):
        a = "Inv%sArea" % k; lk = k.lower()
        ilo.branch("bs" + k, "@entry.%sshown" % lk); ilo.get("gv" + k, a); ilo.call("vv" + k, E_WIDGET, "SetVisibility", inp={"self": "@gv%s.%s" % (k, a), "InVisibility": "SelfHitTestInvisible"})
        ilo.get("gh" + k, a); ilo.call("vh" + k, E_WIDGET, "SetVisibility", inp={"self": "@gh%s.%s" % (k, a), "InVisibility": "Collapsed"})
        ilo.get("gs" + k, a); ilo.call("sl" + k, "/Script/UMG.WidgetLayoutLibrary", "SlotAsVerticalBoxSlot", inp={"Widget": "@gs%s.%s" % (k, a)}); ilo.branch("bf" + k, "@entry.%sfill" % lk)
        ilo.call("sf" + k, "/Script/UMG.VerticalBoxSlot", "SetSize", inp={"self": "@sl%s.ReturnValue" % k, "InSize": "(SizeRule=Fill,Value=1.0)"})
        ilo.call("sa" + k, "/Script/UMG.VerticalBoxSlot", "SetSize", inp={"self": "@sl%s.ReturnValue" % k, "InSize": "(SizeRule=Automatic,Value=1.0)"})
        for e in ends: ilo.chain(e, "bs" + k)
        ilo.chain("bs" + k, "vv" + k, "bf" + k); ilo.chain("bs%s:else" % k, "vh" + k, "bf" + k); ilo.chain("bf" + k, "sf" + k); ilo.chain("bf%s:else" % k, "sa" + k)
        ends = ["sf" + k, "sa" + k]
    # Inventory: weight bar (0..1), its text, warning colour when overloaded
    iw = G(); iw.call("cl", K_MATH, "FClamp", inp={"Value": "@entry.percent", "Min": "0.0", "Max": "1.0"})
    iw.get("gb", "InvWeightBar"); iw.call("sp", U_PROGRESS, "SetPercent", inp={"self": "@gb.InvWeightBar", "InPercent": "@cl.ReturnValue"})
    iw.call("col", K_MATH, "SelectColor", inp={"A": "(R=1.0,G=0.45,B=0.2,A=1.0)", "B": "(R=0.85,G=0.75,B=0.4,A=1.0)", "bPickA": "@entry.over"})
    iw.get("gb2", "InvWeightBar"); iw.call("sf", U_PROGRESS, "SetFillColorAndOpacity", inp={"self": "@gb2.InvWeightBar", "InColor": "@col.ReturnValue"})
    iw.get("gt", "InvWeightText"); iw.call("st", E_TEXT, "SetText", inp={"self": "@gt.InvWeightText", "InText": "@entry.text"})
    iw.chain("entry", "sp", "sf", "st")
    ks = G(); ks.get("g", "KodexScroll"); ks.call("s", U_SCROLL, "ScrollToStart", inp={"self": "@g.KodexScroll"})
    ks.get("gsm", "ScrollMem"); ks.call("csm", K_ARR, "Array_Clear", inp={"TargetArray": "@gsm.ScrollMem"}); ks.chain("entry", "csm", "s")   # see Set Option Cat
    ct = G(); ct.get("g", "ContentTitle"); ct.call("s", E_TEXT, "SetText", inp={"self": "@g.ContentTitle", "InText": "@entry.text"}); ct.chain("entry", "s")
    si = G(); prev = "entry"
    for i, (page, box) in enumerate([("Clothes", "ListScroll"), ("Hair", "HairScroll"), ("Look", "LookScroll"), ("Manage", "ManageScroll")]):
        si.call("e%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@entry.page", "B": page}); si.branch("b%d" % i, "@e%d.ReturnValue" % i)
        si.get("g%d" % i, box); si.call("s%d" % i, U_SCROLL, "ScrollWidgetIntoView", inp={"self": "@g%d.%s" % (i, box), "WidgetToFind": "@entry.widget", "AnimateScroll": "false", "ScrollDestination": "Center"})
        si.chain(prev, "b%d" % i, "s%d" % i); prev = "b%d:else" % i
    def fav_visible(names):
        g = G(); g.branch("b", "@entry.visible")
        for i, wn in enumerate(names):
            g.get("g%d" % i, wn); g.call("v%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@g%d.%s" % (i, wn), "InVisibility": "Visible"})
            g.get("h%d" % i, wn); g.call("c%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@h%d.%s" % (i, wn), "InVisibility": "Collapsed"})
        g.chain("entry", "b", "v0", "v1", "v2"); g.chain("b:else", "c0", "c1", "c2"); return g
    pfv = fav_visible(["PoseFavHeader", "PoseFavList", "PoseAllHeader"]); hfv = fav_visible(["HairFavHeader", "HairFavList", "HairAllHeader"])
    pcv = G(); pcv.branch("b", "@entry.visible")
    pcv.get("g0", "PoseSubTabsBox"); pcv.call("v0", E_WIDGET, "SetVisibility", inp={"self": "@g0.PoseSubTabsBox", "InVisibility": "Visible"})
    pcv.get("h0", "PoseSubTabsBox"); pcv.call("c0", E_WIDGET, "SetVisibility", inp={"self": "@h0.PoseSubTabsBox", "InVisibility": "Collapsed"})
    pcv.chain("entry", "b", "v0"); pcv.chain("b:else", "c0")
    gps = G(); gps.get("g", "PoseSearch"); gps.call("t", E_EDIT, "GetText", inp={"self": "@g.PoseSearch"}); gps.link("t.ReturnValue", "return.text")
    cps = G(); cps.get("g", "PoseSearch"); cps.call("st", E_EDIT, "SetText", inp={"self": "@g.PoseSearch", "InText": ""}); cps.chain("entry", "st")
    wfv = G(); wfv.branch("b", "@entry.visible")
    # only the favourites block: "WeaponAllHeader" is the caption of the skin section and stays, with or without favourites
    for i, wn in enumerate(["WeaponFavHeader", "WeaponFavList"]):
        wfv.get("g%d" % i, wn); wfv.call("v%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@g%d.%s" % (i, wn), "InVisibility": "Visible"})
        wfv.get("h%d" % i, wn); wfv.call("c%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@h%d.%s" % (i, wn), "InVisibility": "Collapsed"})
    wfv.chain("entry", "b", "v0", "v1"); wfv.chain("b:else", "c0", "c1")
    wsv = G(); wsv.branch("b", "@entry.visible")
    for i, wn in enumerate(["WeaponSoundHeader", "WeaponSoundList"]):
        wsv.get("g%d" % i, wn); wsv.call("v%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@g%d.%s" % (i, wn), "InVisibility": "Visible"})
        wsv.get("h%d" % i, wn); wsv.call("c%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@h%d.%s" % (i, wn), "InVisibility": "Collapsed"})
    wsv.chain("entry", "b", "v0", "v1"); wsv.chain("b:else", "c0", "c1")
    wcv = G(); wcv.branch("b", "@entry.visible")
    wcv.get("g0", "WeaponSubTabsBox"); wcv.call("v0", E_WIDGET, "SetVisibility", inp={"self": "@g0.WeaponSubTabsBox", "InVisibility": "Visible"})
    wcv.get("h0", "WeaponSubTabsBox"); wcv.call("c0", E_WIDGET, "SetVisibility", inp={"self": "@h0.WeaponSubTabsBox", "InVisibility": "Collapsed"})
    wcv.chain("entry", "b", "v0"); wcv.chain("b:else", "c0")
    gwse = G(); gwse.get("g", "WeaponSearch"); gwse.call("t", E_EDIT, "GetText", inp={"self": "@g.WeaponSearch"}); gwse.link("t.ReturnValue", "return.text")
    cise = G(); cise.get("g", "InvSearch"); cise.call("st", E_EDIT, "SetText", inp={"self": "@g.InvSearch", "InText": ""}); cise.chain("entry", "st")
    cwse = G(); cwse.get("g", "WeaponSearch"); cwse.call("st", E_EDIT, "SetText", inp={"self": "@g.WeaponSearch", "InText": ""}); cwse.chain("entry", "st")
    # the mouse wheel over the panel must not reach the camera: over plain background, and in a scroll box that has
    # reached its end, nothing consumes the wheel, so the notch arrived at the player controller and moved the Jodi view
    ov = G(); ov.get("obg", "Bg"); ov.call("ohov", E_WIDGET, "IsHovered", inp={"self": "@obg.Bg"})
    ov.link("ohov.ReturnValue", "return.yes")   # Bg is hovered anywhere over the panel: Slate marks the whole hover chain
    # Set Bg Image (Options > Theme): the picture under Bg (whose colour, at its own opacity, lies over it), filled as fit says - 0 fill (crop), 1 fit, 2 stretch
    # (ScaleBox; h / v: 0 left / top, 1 centre, 2 right / bottom - for fill that is where it is cut), 3 tile (an Image brush with Tiling at
    # the picture's own size); alpha = the pattern opacity (BgImgAlpha). on false: the layer goes.
    sbi = G(); sbi.set("so", "BgImgOn", inp={"BgImgOn": "@entry.on"}); sbi.branch("bon", "@entry.on")
    sbi.get("goff", "BgImgLayer"); sbi.call("loff", E_WIDGET, "SetVisibility", inp={"self": "@goff.BgImgLayer", "InVisibility": "Collapsed"})
    sbi.get("gon", "BgImgLayer"); sbi.call("lon", E_WIDGET, "SetVisibility", inp={"self": "@gon.BgImgLayer", "InVisibility": "HitTestInvisible"})
    sbi.call("tint", K_MATH, "MakeColor", inp={"R": "1.0", "G": "1.0", "B": "1.0", "A": "@entry.alpha"})
    sbi.call("ist", K_MATH, "EqualEqual_IntInt", inp={"A": "@entry.fit", "B": "3"}); sbi.branch("bt", "@ist.ReturnValue")
    # tile
    sbi.get("gs0", "BgScale"); sbi.call("hs0", E_WIDGET, "SetVisibility", inp={"self": "@gs0.BgScale", "InVisibility": "Collapsed"})
    sbi.get("gt0", "BgTile"); sbi.call("vt0", E_WIDGET, "SetVisibility", inp={"self": "@gt0.BgTile", "InVisibility": "Visible"})
    sbi.call("sx", E_TEX2D, "Blueprint_GetSizeX", inp={"self": "@entry.tex"}); sbi.call("sy", E_TEX2D, "Blueprint_GetSizeY", inp={"self": "@entry.tex"})
    sbi.call("fx", K_MATH, "Conv_IntToFloat", inp={"InInt": "@sx.ReturnValue"}); sbi.call("fy", K_MATH, "Conv_IntToFloat", inp={"InInt": "@sy.ReturnValue"})
    sbi.call("isz", K_MATH, "MakeVector2D", inp={"X": "@fx.ReturnValue", "Y": "@fy.ReturnValue"})
    sbi.make("mb", "/Script/SlateCore.SlateBrush", ImageSize="@isz.ReturnValue", DrawAs="Image", Tiling="Both"); sbi.set("stb", "TileBrush", inp={"TileBrush": "@mb.SlateBrush"})
    sbi.get("gtb", "TileBrush"); sbi.call("srt", "/Script/UMG.WidgetBlueprintLibrary", "SetBrushResourceToMaterial", inp={"Brush": "@gtb.TileBrush", "Material": "@entry.mat"})
    sbi.get("gtb2", "TileBrush"); sbi.get("gt1", "BgTile"); sbi.call("stl", E_IMAGE, "SetBrush", inp={"self": "@gt1.BgTile", "InBrush": "@gtb2.TileBrush"})
    sbi.get("gt2", "BgTile"); sbi.call("ctl", E_IMAGE, "SetColorAndOpacity", inp={"self": "@gt2.BgTile", "InColorAndOpacity": "@tint.ReturnValue"})
    # fill / fit / stretch
    sbi.get("gt3", "BgTile"); sbi.call("ht3", E_WIDGET, "SetVisibility", inp={"self": "@gt3.BgTile", "InVisibility": "Collapsed"})
    sbi.get("gs1", "BgScale"); sbi.call("vs1", E_WIDGET, "SetVisibility", inp={"self": "@gs1.BgScale", "InVisibility": "HitTestInvisible"})
    sbi.make("mb2", "/Script/SlateCore.SlateBrush", ImageSize="@isz.ReturnValue", DrawAs="Image"); sbi.set("stbi", "TileBrush", inp={"TileBrush": "@mb2.SlateBrush"})
    sbi.get("gtb3", "TileBrush"); sbi.call("srm2", "/Script/UMG.WidgetBlueprintLibrary", "SetBrushResourceToMaterial", inp={"Brush": "@gtb3.TileBrush", "Material": "@entry.mat"})
    sbi.get("gtb4", "TileBrush"); sbi.get("gi0", "BgImage"); sbi.call("sbt", E_IMAGE, "SetBrush", inp={"self": "@gi0.BgImage", "InBrush": "@gtb4.TileBrush"})   # the picture's size: the ScaleBox scales from it
    sbi.get("gi1", "BgImage"); sbi.call("cim", E_IMAGE, "SetColorAndOpacity", inp={"self": "@gi1.BgImage", "InColorAndOpacity": "@tint.ReturnValue"})
    tail = ["entry", "so", "bon", "lon", "bt"]; sbi.chain(*tail); sbi.chain("bon:else", "loff")
    sbi.chain("bt", "hs0", "vt0", "stb", "srt", "stl", "ctl"); sbi.chain("bt:else", "ht3", "vs1", "stbi", "srm2", "sbt", "cim")
    prev = ["cim"]
    def switch(p, pin, cases):
        """Branch chain on an int 0..n-1: case i runs the node made by cases[i](id); returns the exits."""
        nonlocal prev
        exits = []; at = prev
        for i, mk in enumerate(cases):
            sbi.call(p + "e%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": pin, "B": str(i)}); sbi.branch(p + "b%d" % i, "@%se%d.ReturnValue" % (p, i))
            for a in at: sbi.chain(a, p + "b%d" % i)
            node = mk(p + "n%d" % i); sbi.chain(p + "b%d" % i, node); exits.append(node); at = [p + "b%d:else" % i]
        prev = exits + at
    def stretch(st):
        def mk(id): sbi.get(id + "g", "BgScale"); sbi.call(id, U_SCALE, "SetStretch", inp={"self": "@%sg.BgScale" % id, "InStretch": st}); return id
        return mk
    switch("st", "@entry.fit", [stretch("ScaleToFill"), stretch("ScaleToFit"), stretch("Fill")])
    sbi.get("gi2", "BgImage"); sbi.call("slot", "/Script/UMG.WidgetLayoutLibrary", "SlotAsScaleBoxSlot", inp={"Widget": "@gi2.BgImage"})
    def halign(v):
        def mk(id): sbi.call(id, "/Script/UMG.ScaleBoxSlot", "SetHorizontalAlignment", inp={"self": "@slot.ReturnValue", "InHorizontalAlignment": v}); return id
        return mk
    def valign(v):
        def mk(id): sbi.call(id, "/Script/UMG.ScaleBoxSlot", "SetVerticalAlignment", inp={"self": "@slot.ReturnValue", "InVerticalAlignment": v}); return id
        return mk
    switch("ha", "@entry.h", [halign("HAlign_Left"), halign("HAlign_Center"), halign("HAlign_Right")])
    switch("va", "@entry.v", [valign("VAlign_Top"), valign("VAlign_Center"), valign("VAlign_Bottom")])
    # one-row tab bar (Options > Tabs, TabOneRow): the bar's width, and shrinking the captions until the tabs fit beside each other
    ttw = G(); ttw.get("g", "TopTabs"); ttw.call("geo", E_WIDGET, "GetCachedGeometry", inp={"self": "@g.TopTabs"}); ttw.call("ls", K_SLATE, "GetLocalSize", inp={"Geometry": "@geo.ReturnValue"})
    ttw.call("bv", K_MATH, "BreakVector2D", inp={"InVec": "@ls.ReturnValue"}); ttw.link("bv.X", "return.width"); ttw.chain("entry", "return")
    ftt = G(); ftt.set("s0", "FitDone", inp={"FitDone": "false"}); ftt.get("gt", "TopTabs"); ftt.call("ch", E_PANEL, "GetAllChildren", inp={"self": "@gt.TopTabs"}); ftt.set("sk", "FitKids", inp={"FitKids": "@ch.ReturnValue"})
    ftt.n("steps", "make_array", count=len(TOP_FIT_STEPS), type="int", inp={"[%d]" % i: str(v) for i, v in enumerate(TOP_FIT_STEPS)}); ftt.foreach("fs", "@steps.Array")
    ftt.get("gd", "FitDone"); ftt.call("nd", K_MATH, "Not_PreBool", inp={"A": "@gd.FitDone"}); ftt.branch("bnd", "@nd.ReturnValue")
    ftt.call("size", K_MATH, "Divide_IntInt", inp={"A": "@fs.Array Element", "B": "100"}); ftt.call("maxc", K_MATH, "Percent_IntInt", inp={"A": "@fs.Array Element", "B": "100"})
    ftt.get("gk1", "FitKids"); ftt.foreach("f1", "@gk1.FitKids"); ftt.cast("c1", W_TOP, "@f1.Array Element", pure=False, miss="ignore")
    ftt.call("sf", W_TOP, "Set Fit", inp={"self": "@c1.AsW_TopTab", "size": "@size.ReturnValue", "maxc": "@maxc.ReturnValue"})
    ftt.set("ss0", "FitSum", inp={"FitSum": "0.0"}); ftt.get("gk2", "FitKids"); ftt.foreach("f2", "@gk2.FitKids")
    ftt.call("pp", E_WIDGET, "ForceLayoutPrepass", inp={"self": "@f2.Array Element"}); ftt.call("ds", E_WIDGET, "GetDesiredSize", inp={"self": "@f2.Array Element"})
    ftt.call("bd", K_MATH, "BreakVector2D", inp={"InVec": "@ds.ReturnValue"}); ftt.get("gs", "FitSum"); ftt.call("a1", K_MATH, "Add_FloatFloat", inp={"A": "@gs.FitSum", "B": "@bd.X"})
    ftt.call("a2", K_MATH, "Add_FloatFloat", inp={"A": "@a1.ReturnValue", "B": str(float(sz(4) + 1))}); ftt.set("ss1", "FitSum", inp={"FitSum": "@a2.ReturnValue"})
    ftt.get("gs2", "FitSum"); ftt.call("fits", K_MATH, "LessEqual_FloatFloat", inp={"A": "@gs2.FitSum", "B": "@entry.avail"}); ftt.branch("bfit", "@fits.ReturnValue")
    ftt.set("sd", "FitDone", inp={"FitDone": "true"})
    ftt.chain("entry", "s0", "sk", "fs"); ftt.chain("fs", "bnd", "f1"); ftt.chain("f1", "c1", "sf"); ftt.chain("f1:Completed", "ss0", "f2"); ftt.chain("f2", "pp", "ss1")
    ftt.chain("f2:Completed", "bfit", "sd")
    funcs = [fn("Over Panel", outputs=[param("yes", "bool")], graph=ov, pure=True),
             clear("Clear Left", "LeftBox"), add("Add Left", "LeftBox", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Content", "ContentList"), add("Add Content Section", "ContentList", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Content Links", "ContentLinks"), add("Add Content Link", "ContentLinks", U_HBOX, "AddChildToHorizontalBox"),
             fn("Set Content Title", [param("text", "text")], graph=ct), fn("Scroll Into View", [param("page", "name"), param("widget", "object:" + E_WIDGET)], graph=si),
             fn("Apply Theme", graph=at), fn("Clear Theme Swatches", graph=cts), fn("Add Theme Swatch", [param("widget", "object:" + E_WIDGET), param("column", "int")], graph=ats),
             clear("Clear TopTabs", "TopTabs"), add("Add TopTab", "TopTabs", U_WRAP, "AddChildToWrapBox"),
             *vlist_panel_fns("Ofl", "OutfitScroll", "OutfitVB", "OutfitTop", "OutfitList", "OutfitBottom"),
             clear("Clear Look Tiles", "LooksList"), add("Add Look Tile", "LooksList", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Bag Worn", "BagWorn"), add("Add Bag Worn", "BagWorn", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Bag List", "BagList"), add("Add Bag Item", "BagList", U_WRAP, "AddChildToWrapBox"),
             fn("Set Page", [param("page", "name")], graph=sp), fn("Set Bag Empty", [param("visible", "bool")], graph=be),
             fn("Clear Search", graph=cs), fn("Set List Hint", [param("visible", "bool")], graph=lh), fn("Sync Check Size", graph=cs2),
             clear("Clear Bag Links", "BagLinks"), add("Add Bag Link", "BagLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Bag Worn Links", "BagWornLinks"), add("Add Bag Worn Link", "BagWornLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Search Links", "SearchLinks"), add("Add Search Link", "SearchLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Hair Links", "HairLinks"), add("Add Hair Link", "HairLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Hair", "HairList"), add("Add Hair", "HairList", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Hair Fav", "HairFavList"), add("Add Hair Fav", "HairFavList", U_WRAP, "AddChildToWrapBox"), fn("Set Hair Fav Visible", [param("visible", "bool")], graph=hfv),
             clear("Clear Look Cats", "LookCats"), add("Add Look Cat", "LookCats", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Rag Kinds", "RagKinds"), add("Add Rag Kind", "RagKinds", U_WRAP, "AddChildToWrapBox"), set_hint_fn("Set Rag Kinds Title", "LblRagKinds"), clear("Clear Rag Top", "RagTop"), add("Add Rag Top", "RagTop", U_HBOX, "AddChildToHorizontalBox"), clear("Clear Rag Rows", "RagRows"), add("Add Rag Row", "RagRows", U_VBOX, "AddChildToVerticalBox"),
             fn("Set Rag Hint", [param("text", "text")], graph=rh), fn("Set Rag Texts", [param("save", "text"), param("presets", "text"), param("hint", "text")], graph=rt),
             fn("Get Rag Name", outputs=[param("text", "text")], graph=grn, pure=True), fn("Clear Rag Name", graph=crn),
             clear("Clear Rag Save Links", "RagSaveLinks"), add("Add Rag Save Link", "RagSaveLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Rag Preset Chips", "RagPresetChips"), add("Add Rag Preset Chip", "RagPresetChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Inv Chips", "InvChips"), add("Add Inv Chip", "InvChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Inv Bag", "InvBagList"), add("Add Inv Bag", "InvBagList", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Inv Box", "InvBoxList"), add("Add Inv Box", "InvBoxList", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Inv Cat", "InvCatList"), add("Add Inv Cat", "InvCatList", U_VBOX, "AddChildToVerticalBox"), fn("Set Inv Catalog", [param("on", "bool")], graph=icv),
             clear("Clear Fol Bag", "FolBagList"), add("Add Fol Bag", "FolBagList", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Fol Box", "FolBoxList"), add("Add Fol Box", "FolBoxList", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Fol Rows", "FolRows"), add("Add Fol Row", "FolRows", U_VBOX, "AddChildToVerticalBox"),
             fn("Clear Fol Heads", graph=cfh), padded_add("Add Fol Bag Head", "FolBagBtns"), padded_add("Add Fol Box Head", "FolBoxBtns"),
             fn("Set Fol Layout", [param("bagshown", "bool"), param("boxshown", "bool")], graph=flo), fn("Set Fol Hint", [param("text", "text")], graph=fhi), fn("Set Fol Bag Note", [param("text", "text")], graph=fbn), fn("Set Inv Bag Note", [param("text", "text")], graph=ibn),
             fn("Clear Inv Heads", graph=cih), fn("Clear Inv Search", graph=cise), clear("Clear Inv Search Links", "InvSearchLinks"), add("Add Inv Search Link", "InvSearchLinks", U_HBOX, "AddChildToHorizontalBox"), padded_add("Add Inv Bag Head", "InvBagBtns"), padded_add("Add Inv Box Head", "InvBoxBtns"), padded_add("Add Inv Cat Head", "InvCatBtns"),
             fn("Set Inv Layout", [param(k + s, "bool") for k in ("bag", "box", "cat") for s in ("shown", "fill")], graph=ilo),
             fn("Set Inv Weight", [param("percent", "float"), param("text", "text"), param("over", "bool")], graph=iw),
             clear("Clear Kodex Cats", "KodexCats"), add("Add Kodex Cat", "KodexCats", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Kodex Tiles", "KodexTiles"), add("Add Kodex Tile", "KodexTiles", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Kodex Links", "KodexLinks"), add("Add Kodex Link", "KodexLinks", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Kodex Back", "KodexBack"), add("Add Kodex Back", "KodexBack", U_HBOX, "AddChildToHorizontalBox"),
             fn("Set Kodex Text", [param("title", "text"), param("body", "text")], graph=kt), fn("Set Kodex Image", [param("tex", "object:" + E_TEX2D)], graph=ki),
             fn("Kodex Scroll Top", graph=ks),
             clear("Clear Option Cats", "OptionCats"), add("Add Option Cat", "OptionCats", U_VBOX, "AddChildToVerticalBox"), fn("Set Option Cat", [param("cat", "name")], graph=soc),
             clear("Clear Tab Chips", "TabChips"), add("Add Tab Chip", "TabChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Tab Style Chips", "TabStyleChips"), add("Add Tab Style Chip", "TabStyleChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Tab Icon Pos Chips", "TabIconPosChips"), add("Add Tab Icon Pos Chip", "TabIconPosChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Tab Row Chips", "TabRowChips"), add("Add Tab Row Chip", "TabRowChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear BgImage Chips", "BgImageChips"), add("Add BgImage Chip", "BgImageChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear BgFit Chips", "BgFitChips"), add("Add BgFit Chip", "BgFitChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear BgHAlign Chips", "BgHAlignChips"), add("Add BgHAlign Chip", "BgHAlignChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear BgVAlign Chips", "BgVAlignChips"), add("Add BgVAlign Chip", "BgVAlignChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear BtnImage Chips", "BtnImageChips"), add("Add BtnImage Chip", "BtnImageChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear BgInv Chips", "BgInvChips"), add("Add BgInv Chip", "BgInvChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear BtnInv Chips", "BtnInvChips"), add("Add BtnInv Chip", "BtnInvChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear ImgThumbs Chips", "ImgThumbsChips"), add("Add ImgThumbs Chip", "ImgThumbsChips", U_WRAP, "AddChildToWrapBox"),
             thumb_filters_fn("Bg Thumb Filters", "BgImageChips"), thumb_filters_fn("Btn Thumb Filters", "BtnImageChips"),
             set_hint_fn("Set Image Hint", "LblImgHint"), fn("Set Bg Image", [param("tex", "object:" + E_TEX2D), param("mat", "object:/Script/Engine.MaterialInterface"), param("fit", "int"), param("h", "int"), param("v", "int"), param("alpha", "float"), param("on", "bool")], graph=sbi),
             fn("Top Tabs Width", outputs=[param("width", "float")], graph=ttw, pure=True), fn("Fit Top Tabs", [param("avail", "float")], graph=ftt),
             clear("Clear Quick Key Links", "QuickKeyLinks"), qkl, fn("Set Quick Key Hint", [param("text", "text")], graph=qkh),
             clear("Clear Quick In Wheel", "QuickInWheel"), add("Add Quick In Wheel", "QuickInWheel", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Key Binds", "KeyBinds"), add("Add Key Bind", "KeyBinds", U_VBOX, "AddChildToVerticalBox"), fn("Set Key Bind Hint", [param("text", "text")], graph=kbh),
             *vlist_panel_fns("Qa", "OptionsScroll", "QuickAvailable", "QaTop", "QaWrap", "QaBottom"),
             clear("Clear Look", "LookList"), add("Add Look", "LookList", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Look Rows", "LookRowList"), add("Add Look Row", "LookRowList", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Look Fav", "LookFavList"), add("Add Look Fav", "LookFavList", U_WRAP, "AddChildToWrapBox"), fn("Set Look Fav Visible", [param("visible", "bool")], graph=lfv), fn("Set Manage Content Space", [param("keep", "bool")], graph=mcs),
             clear("Clear Look SubTabs", "LookSubTabs"), add("Add Look SubTab", "LookSubTabs", U_WRAP, "AddChildToWrapBox"), fn("Set Look Chips Visible", [param("visible", "bool")], graph=lcv),
             clear("Clear Pose Cats", "PoseCats"), add("Add Pose Cat", "PoseCats", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Mod Entries", "ModEntries"), add("Add Mod Entry", "ModEntries", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Mod Fields", "ModFieldList"), add("Add Mod Field Widget", "ModFieldList", U_VBOX, "AddChildToVerticalBox"), set_mod_hint(),
             clear("Clear Face Groups", "FaceGroups"), add("Add Face Group", "FaceGroups", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Face Links", "FaceLinks"), add("Add Face Link", "FaceLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Face Rows", "FaceRowList"), add("Add Face Row", "FaceRowList", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Face Tiles", "FaceTiles"), add("Add Face Tile", "FaceTiles", U_WRAP, "AddChildToWrapBox"), set_hint_fn("Set Face Hint", "FaceHint"),
             clear("Clear Pose", "PoseList"), add("Add Pose", "PoseList", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Pose Fav", "PoseFavList"), add("Add Pose Fav", "PoseFavList", U_WRAP, "AddChildToWrapBox"), fn("Set Pose Fav Visible", [param("visible", "bool")], graph=pfv),
             clear("Clear Pose SubTabs", "PoseSubTabs"), add("Add Pose SubTab", "PoseSubTabs", U_WRAP, "AddChildToWrapBox"), fn("Set Pose Chips Visible", [param("visible", "bool")], graph=pcv),
             clear("Clear Pose Links", "PoseLinks"), add("Add Pose Link", "PoseLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Pose Search Links", "PoseSearchLinks"), add("Add Pose Search Link", "PoseSearchLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Weapon Cats", "WeaponCats"), add("Add Weapon Cat", "WeaponCats", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Weapon Models", "WeaponModelList"), add("Add Weapon Model", "WeaponModelList", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Weapon Attach", "WeaponAttachList"), add("Add Weapon Attach", "WeaponAttachList", U_VBOX, "AddChildToVerticalBox"), fn("Set Weapon Attach Visible", [param("visible", "bool")], graph=wav),
             clear("Clear Weapon Sounds", "WeaponSoundList"), add("Add Weapon Sound", "WeaponSoundList", U_WRAP, "AddChildToWrapBox"), fn("Set Weapon Sounds Visible", [param("visible", "bool")], graph=wsv),
             clear("Clear Weapon Skins", "WeaponList"), add("Add Weapon Skin", "WeaponList", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Weapon Skin Fav", "WeaponFavList"), add("Add Weapon Skin Fav", "WeaponFavList", U_WRAP, "AddChildToWrapBox"), fn("Set Weapon Fav Visible", [param("visible", "bool")], graph=wfv),
             clear("Clear Weapon SubTabs", "WeaponSubTabs"), add("Add Weapon SubTab", "WeaponSubTabs", U_WRAP, "AddChildToWrapBox"), fn("Set Weapon Chips Visible", [param("visible", "bool")], graph=wcv),
             clear("Clear Weapon Search Links", "WeaponSearchLinks"), add("Add Weapon Search Link", "WeaponSearchLinks", U_HBOX, "AddChildToHorizontalBox"),
             fn("Get Weapon Search", outputs=[param("text", "text")], graph=gwse, pure=True), fn("Clear Weapon Search", graph=cwse),
             fn("Get Pose Search", outputs=[param("text", "text")], graph=gps, pure=True), fn("Clear Pose Search", graph=cps),
             fn("Get Look Only Fav", outputs=[param("yes", "bool")], graph=glf, pure=True), fn("Set Look Only Fav", [param("yes", "bool")], graph=slf),
             fn("Get Look Only Worn", outputs=[param("yes", "bool")], graph=glw, pure=True), fn("Set Look Only Worn", [param("yes", "bool")], graph=slw),
             fn("Get Option Values", outputs=[param(k.lower(), "float") for k, _ in OPTION_ROWS] + [param("unlimited", "bool"), param("pan", "bool"), param("nude", "bool"), param("merge", "bool"), param("mergemods", "bool"), param("chipsearch", "bool"), param("tipnoprefix", "bool"), param("tipnoids", "bool"), param("camright", "bool"), param("kodexall", "bool"), param("moveon", "bool"), param("invcatalog", "bool"), param("invautoequip", "bool"), param("slowmoon", "bool"), param("freenocollide", "bool"), param("freenolimit", "bool"), param("nonotices", "bool")], graph=gov),
             fn("Set Option Checks", [param("unlimited", "bool"), param("pan", "bool"), param("nude", "bool"), param("merge", "bool"), param("mergemods", "bool"), param("chipsearch", "bool"), param("tipnoprefix", "bool"), param("tipnoids", "bool"), param("camright", "bool"), param("kodexall", "bool"), param("moveon", "bool"), param("invcatalog", "bool"), param("invautoequip", "bool"), param("slowmoon", "bool"), param("freenocollide", "bool"), param("freenolimit", "bool"), param("nonotices", "bool")], graph=su), fn("Set Left Free", [param("fraction", "float")], graph=la), fn("Set Cam Mode", [param("on", "bool")], graph=scm), fn("Set Palette Lock", [param("on", "bool")], graph=spl),
             clear("Clear Layout Chips", "LayoutChips"), add("Add Layout Chip", "LayoutChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Unowned Chips", "UnownedChips"), add("Add Unowned Chip", "UnownedChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Conflict Rows", "ConflictRows"), add("Add Conflict Row", "ConflictRows", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Conflict Links", "ConflictLinks"), add("Add Conflict Link", "ConflictLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Multi Slot Chips", "MultiSlotChips"), add("Add Multi Slot Chip", "MultiSlotChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Move Links", "MoveLinks"), add("Add Move Link", "MoveLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Walk Style Chips", "WalkStyleChips"), add("Add Walk Style Chip", "WalkStyleChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Run Style Chips", "RunStyleChips"), add("Add Run Style Chip", "RunStyleChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Idle Style Chips", "IdleStyleChips"), add("Add Idle Style Chip", "IdleStyleChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Body Chips", "BodyChips"), add("Add Body Chip", "BodyChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Lang Chips", "LangChips"), add("Add Lang Chip", "LangChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Key Chips", "KeyChips"), add("Add Key Chip", "KeyChips", U_WRAP, "AddChildToWrapBox"),
             fn("Set Strings", [param(p, "text") for p, _ in PANEL_TEXTS], graph=sst), fn("Init Buttons", graph=ib),
             clear("Clear Status", "StatusLinks"), add("Add Status", "StatusLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Status Right", "StatusRight"), add("Add Status Right", "StatusRight", U_HBOX, "AddChildToHorizontalBox"),
             fn("Set Option Values", [param(k.lower(), "float") for k, _ in OPTION_ROWS] + [param(k.lower() + " text", "text") for k, _ in OPTION_ROWS], graph=sov),
             fn("Set Scroll Mult", [param("mult", "float")], graph=sm), *scroll_keep_fns(),
             fn("Set SubTabs Height", [param("height", "float")], graph=sth),
             fn("Get Body Values", outputs=[param("breast", "float"), param("waist", "float")], graph=gb),
             fn("Set Body Values", [param("breast", "float"), param("waist", "float")], graph=sb),
             fn("Get Body Scales", outputs=[param(key.lower(), "float") for _, key in SCALE_ROWS], graph=gsc),
             fn("Set Body Scales", [param(key.lower(), "float") for _, key in SCALE_ROWS], graph=ssc),
             fn("Set Body Scales Enabled", [param("enabled", "bool")], graph=esc),
             *vlist_panel_fns("Clo", "ListScroll", "ListVB", "CloTop", "List", "CloBottom"),
             fn("Set Fav Visible", [param("visible", "bool")], graph=fv2), fn("OnMouseButtonDown", override=True, graph=pm), fn("OnMouseMove", override=True, graph=mm), fn("OnMouseButtonUp", override=True, graph=mu), fn("OnMouseWheel", override=True, graph=mw),

             clear("Clear SubTabs", "SubTabs"), add("Add SubTab", "SubTabs", U_WRAP, "AddChildToWrapBox"),
             fn("Get Search", outputs=[param("text", "text")], graph=gs, pure=True),
             fn("Get Chip Search", outputs=[param("text", "text")], graph=gcse, pure=True), fn("Clear Chip Search", graph=ccse),
             fn("Set Chip Search Visible", [param("visible", "bool")], graph=csv_),
             fn("Get Look Chip Search", outputs=[param("text", "text")], graph=glcs, pure=True), fn("Clear Look Chip Search", graph=clcs),
             fn("Set Look Chip Search Visible", [param("visible", "bool")], graph=lcsv),
             fn("Set Manage Chips Visible", [param("chips", "bool"), param("search", "bool")], graph=mcv), fn("Clear Manage Chip Search", graph=cmcs),
             clear("Clear Manage Chips", "ManageChips"), add("Add Manage Chip", "ManageChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Manage Chip Search Links", "ManageChipSearchLinks"), add("Add Manage Chip Search Link", "ManageChipSearchLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Look Chip Search Links", "LookChipSearchLinks"), add("Add Look Chip Search Link", "LookChipSearchLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Chip Search Links", "ChipSearchLinks"), add("Add Chip Search Link", "ChipSearchLinks", U_HBOX, "AddChildToHorizontalBox"),
             fn("Get Only Owned", outputs=[param("yes", "bool")], graph=go, pure=True),
             fn("Get Only Fav", outputs=[param("yes", "bool")], graph=gf, pure=True),
             fn("Get Only Vanilla", outputs=[param("yes", "bool")], graph=gv, pure=True),
             fn("Get Only Worn", outputs=[param("yes", "bool")], graph=gw, pure=True),
             clear("Clear Manage Cats", "ManageCats"), add("Add Manage Cat", "ManageCats", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Manage Rows", "ManageRows"), add("Add Manage Row", "ManageRows", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Hair Swatches", "HairSwatches"), add("Add Hair Swatch", "HairSwatches", U_WRAP, "AddChildToWrapBox"),
             fn("Get Manage Search", outputs=[param("text", "text")], graph=gms, pure=True), fn("Get Theme Name", outputs=[param("text", "text")], graph=gtn, pure=True), fn("Clear Theme Name", graph=ctn),
             clear("Clear Theme Presets", "ThemePresetChips"), add("Add Theme Preset", "ThemePresetChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Theme Save Links", "ThemeSaveLinks"), add("Add Theme Save Link", "ThemeSaveLinks", U_HBOX, "AddChildToHorizontalBox"), fn("Get Only Mods", outputs=[param("yes", "bool")], graph=gom, pure=True),
             fn("Set Only Mods", [param("on", "bool")], graph=som), fn("Get Case Sens", outputs=[param("yes", "bool")], graph=gcs, pure=True), fn("Set Case Sens", [param("on", "bool")], graph=scs), fn("Set Hair Swatches Visible", [param("visible", "bool")], graph=shs), fn("Set Only Mods Visible", [param("visible", "bool")], graph=somv),
             fn("Clear Manage Search", graph=cms), fn("Set Manage Search", [param("text", "text")], graph=sms),
             fn("Get Look Search", outputs=[param("text", "text")], graph=gls, pure=True), fn("Clear Look Search", graph=cls_), clear("Clear Look Search Links", "LookSearchLinks"), add("Add Look Search Link", "LookSearchLinks", U_HBOX, "AddChildToHorizontalBox"), clear("Clear Manage Search Links", "ManageSearchLinks"), add("Add Manage Search Link", "ManageSearchLinks", U_HBOX, "AddChildToHorizontalBox"),
             fn("Set Filter Toggles", [param("owned", "bool"), param("fav", "bool"), param("vanilla", "bool"), param("worn", "bool")], graph=ft),
             fn("OnKeyDown", override=True, graph=kd), fn("OnKeyUp", override=True, graph=ku), fn("OnPreviewKeyDown", override=True, graph=pk),
             fn("OnPreviewMouseButtonDown", override=True, graph=pvm)]
    return blueprint(W_PANEL, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("ScrollMem", "float", "array"), var("ShownOptCat", "name"), var("TmpKnown", "bool"), var("CheckSize", "float"), var("FitDone", "bool"), var("FitSum", "float"),
                                                       var("FitKids", "object:" + E_WIDGET, "array"), var("BgImgOn", "bool"), var("TileBrush", "struct:/Script/SlateCore.SlateBrush")], functions=funcs, widget_tree=tree,
                     defaults={"bIsFocusable": "true"})


# ---------------- W_QuickRow (Options › Quick menu: one item; mode 0 = in the wheel with ↑ ↓ ✕ links, 1 = available with a check
# box - a click toggles it, 2 = group heading) ----------------
W_QROW = M + "/W_QuickRow"


def w_quick_row():
    tree = w(E_BORDER, "Bg", props={"BrushColor": "(R=1,G=1,B=1,A=0)", "Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(6), sz(3), sz(6), sz(3)),
                                    "VerticalAlignment": "VAlign_Center"}, children=[   # one or two lines: centred in the fixed row height
        w(U_HBOX, "Row", children=[
            sizebox("CheckBox", 20, 20, [w(E_IMAGE, "Check")], slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
            sizebox("IconBox", 32, 32, [w(U_SCALE, "IconScale", props={"Stretch": "ScaleToFit"}, children=[w(E_IMAGE, "Icon")])],
                    slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
            text("Label", "", 13, wrap=True, break_all=True, slot={"Size": "(SizeRule=Fill,Value=1)", "VerticalAlignment": "VAlign_Center"}),   # two lines in a third of the row, also without spaces
            w(U_HBOX, "Links", slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(12)})])])
    tree = w(U_SIZE, "Box", props={"Clipping": "ClipToBounds"}, children=[tree])   # Set Tile Size: a third of the row in the "Available" list
    g = G(); tail = ["entry"]
    g.set("si", "Item", inp={"Item": "@entry.item"}); g.set("sm", "Mode", inp={"Mode": "@entry.mode"}); tail += ["si", "sm"]
    g.get("gl", "Label"); g.call("st", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@entry.caption"}); tail.append("st")
    g.call("m1", K_MATH, "EqualEqual_IntInt", inp={"A": "@entry.mode", "B": "1"})
    g.branch("bc", "@m1.ReturnValue"); tail.append("bc")
    g.call("ct", K_MATH, "SelectObject", inp={"A": T_CHECK_ON, "B": T_CHECK_OFF, "bSelectA": "@entry.checked"}); g.cast("ctc", E_TEX2D, "@ct.ReturnValue")
    g.get("gc", "Check"); g.call("sb", E_IMAGE, "SetBrushFromTexture", inp={"self": "@gc.Check", "Texture": "@ctc.AsTexture2D", "bMatchSize": "false"})
    g.get("gcb", "CheckBox"); g.call("hc", E_WIDGET, "SetVisibility", inp={"self": "@gcb.CheckBox", "InVisibility": "Collapsed"})
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@entry.icon"}); g.branch("bi", "@iv.ReturnValue")
    g.get("gi", "Icon"); g.call("sbi", E_IMAGE, "SetBrushFromTexture", inp={"self": "@gi.Icon", "Texture": "@entry.icon", "bMatchSize": "true"})
    g.call("hd", K_MATH, "EqualEqual_IntInt", inp={"A": "@entry.mode", "B": "2"}); g.branch("bhd", "@hd.ReturnValue")   # no icon: keep its space so the names line up; headings take none
    g.get("gib", "IconBox"); g.call("hi", E_WIDGET, "SetVisibility", inp={"self": "@gib.IconBox", "InVisibility": "Collapsed"})
    g.get("gib4", "IconBox"); g.call("hh", E_WIDGET, "SetVisibility", inp={"self": "@gib4.IconBox", "InVisibility": "Hidden"})
    g.call("op", K_MATH, "SelectFloat", inp={"A": "1.0", "B": "0.45", "bPickA": "@entry.valid"})
    g.get("gl2", "Label"); g.call("so", E_WIDGET, "SetRenderOpacity", inp={"self": "@gl2.Label", "InOpacity": "@op.ReturnValue"})
    # pooled by the "Available" list: what one item hides, the next one shows again (else icons stayed hidden, game test 2026-10-06)
    g.get("gcb2", "CheckBox"); g.call("vc", E_WIDGET, "SetVisibility", inp={"self": "@gcb2.CheckBox", "InVisibility": "Visible"})
    g.get("gib2", "IconBox"); g.call("vi", E_WIDGET, "SetVisibility", inp={"self": "@gib2.IconBox", "InVisibility": "Visible"})
    g.chain(*tail); g.chain("bc", "vc", "sb", "bi"); g.chain("bc:else", "hc", "bi"); g.chain("bi", "vi", "sbi", "so"); g.chain("bi:else", "bhd", "hi", "so"); g.chain("bhd:else", "hh", "so")
    g.n("cc", "call_self", function="Compute Colors"); g.chain("so", "sbg", "cc")
    # zebra stripe like the slot conflicts: tinted rows a light white, headings never
    g.call("tbc", K_MATH, "SelectColor", inp={"A": "(R=1,G=1,B=1,A=0.05)", "B": "(R=1,G=1,B=1,A=0)", "bPickA": "@entry.tinted"})
    g.get("gbg", "Bg"); g.call("sbg", E_BORDER, "SetBrushColor", inp={"self": "@gbg.Bg", "InBrushColor": "@tbc.ReturnValue"})
    init = fn("Init", [param("item", "string"), param("caption", "text"), param("icon", "object:" + E_TEX2D), param("mode", "int"), param("checked", "bool"), param("valid", "bool"),
                       param("tinted", "bool")], graph=g)
    a = G(); a.get("g", "Links"); a.call("a", U_HBOX, "AddChildToHorizontalBox", inp={"self": "@g.Links", "Content": "@entry.widget"})
    a.call("ss", "/Script/UMG.HorizontalBoxSlot", "SetPadding", inp={"self": "@a.ReturnValue", "InPadding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(10)}); a.chain("entry", "a", "ss")
    c = G(); tail = ["entry"]; c.get("gmo", "Mode"); c.call("isg", K_MATH, "EqualEqual_IntInt", inp={"A": "@gmo.Mode", "B": "2"})
    c.call("col", K_MATH, "SelectColor", inp={"A": mcol(c, "ch", "ColHead"), "B": mcol(c, "ct", "ColText"), "bPickA": "@isg.ReturnValue"})
    text_color(c, "tl", "Label", "@col.ReturnValue", tail); c.chain(*tail)
    # a left click on an available row toggles it, a right click waits for a key for it (own keys); rows of the wheel list and headings ignore clicks
    md = G(); md.get("gmo", "Mode"); md.call("is1", K_MATH, "EqualEqual_IntInt", inp={"A": "@gmo.Mode", "B": "1"}); md.branch("b", "@is1.ReturnValue")
    md.call("btn", K_IN, "PointerEvent_GetEffectingButton", inp={"Input": "@entry.MouseEvent"}); md.call("isr", K_IN, "EqualEqual_KeyKey", inp={"A": "@btn.ReturnValue", "B": "RightMouseButton"}); md.branch("br", "@isr.ReturnValue")
    md.get("gm", "Manager"); md.get("gi", "Item"); md.call("t", MGR, "Quick Toggle", inp={"self": "@gm.Manager", "item": "@gi.Item"})
    md.get("gm2", "Manager"); md.get("gi2", "Item"); md.call("kb", MGR, "Bind Begin", inp={"self": "@gm2.Manager", "item": "@gi2.Item"})
    md.call("h", K_WBL, "Handled"); md.link("h.ReturnValue", "return.ReturnValue"); md.n("r2", "return_new"); md.call("u", K_WBL, "Unhandled"); md.link("u.ReturnValue", "r2.ReturnValue")
    md.chain("entry", "b", "br", "kb", "return"); md.chain("br:else", "t", "return"); md.chain("b:else", "r2")
    return blueprint(W_QROW, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Item", "string"), var("Mode", "int")],
                     functions=[fn("Set Tile Size", [param("width", "float"), param("height", "float")], graph=tile_size_graph()), init, fn("Add Link", [param("widget", "object:" + E_WIDGET)], graph=a), compute_fn(c), fn("OnMouseButtonDown", override=True, graph=md)],
                     widget_tree=tree, defaults=HAND)


# ---------------- Quick menu wheel (docs/specs/2026-10-03-quick-menu-design.md) ----------------
# W_QuickWheel: full screen, the wheel centred; one W_QuickSector per item (each the full wheel size: the sector material picks
# its own wedge), the item name in the dark centre. Mouse move -> Manager.Quick Hover, the quick key's release / a left click ->
# Quick Release, Esc -> Quick Cancel.
W_QUICK = M + "/W_QuickWheel"; W_QSECTOR = M + "/W_QuickSector"
M_QSECTOR = M + "/Mat/M_QuickSector"
MID = "/Script/Engine.MaterialInstanceDynamic"
QUICK_SIZE = 560                 # wheel diameter (units, x SC)
QUICK_INNER = 0.36               # dead zone / centre radius share (= the material's Inner, manager QUICK_INNER)
QUICK_LABEL_R = (1 + QUICK_INNER) / 2   # labels sit halfway across the ring
QUICK_TEXT_MAX = 12              # up to this many sectors a name under the icon; more: icon only
QUICK_ICON = 56                  # icon size with names (units)
QUICK_ICON_MIN = 22
QSEC_BRUSH = "(ResourceObject=Material'%s.M_QuickSector',ImageSize=(X=%d,Y=%d),DrawAs=Image)" % (M_QSECTOR, sz(QUICK_SIZE), sz(QUICK_SIZE))
FILL_OV = {"HorizontalAlignment": "HAlign_Fill", "VerticalAlignment": "VAlign_Fill"}


def w_quick_sector():
    R = sz(QUICK_SIZE) / 2.0; RL = R * QUICK_LABEL_R
    tree = sizebox("Box", QUICK_SIZE, QUICK_SIZE, [w(U_OVERLAY, "Ov", children=[
        w(E_IMAGE, "Seg", props={"Brush": QSEC_BRUSH, "Visibility": "HitTestInvisible"}, slot=FILL_OV),
        w(U_CANVAS, "Cv", props={"Visibility": "HitTestInvisible"}, slot=FILL_OV, children=[
            w(U_VBOX, "Lbl", slot={"LayoutData": "(Anchors=(Minimum=(X=0,Y=0),Maximum=(X=0,Y=0)),Offsets=(Left=0,Top=0,Right=0,Bottom=0),Alignment=(X=0.5,Y=0.5))", "bAutoSize": True}, children=[
                sizebox("IconBox", QUICK_ICON, QUICK_ICON, [w(U_SCALE, "IconScale", props={"Stretch": "ScaleToFit"}, children=[w(E_IMAGE, "Icon")])], slot={"HorizontalAlignment": "HAlign_Center"}),
                text("Name", "", 12, center=True, slot={"HorizontalAlignment": "HAlign_Center", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(2)})])])])])
    g = G(); tail = ["entry"]
    g.set("sv", "Valid", inp={"Valid": "@entry.valid"}); tail.append("sv")
    g.get("gs", "Seg"); g.call("dm", E_IMAGE, "GetDynamicMaterial", inp={"self": "@gs.Seg"}); g.set("sm", "Mid", inp={"Mid": "@dm.ReturnValue"}); tail += ["dm", "sm"]
    g.call("cf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@entry.count"}); g.call("if", K_MATH, "Conv_IntToFloat", inp={"InInt": "@entry.index"})
    g.get("gm1", "Mid"); g.call("pc", MID, "SetScalarParameterValue", inp={"self": "@gm1.Mid", "ParameterName": "Count", "Value": "@cf.ReturnValue"}); tail.append("pc")
    g.get("gm2", "Mid"); g.call("pi", MID, "SetScalarParameterValue", inp={"self": "@gm2.Mid", "ParameterName": "Index", "Value": "@if.ReturnValue"}); tail.append("pi")
    g.n("mk", "call_self", function="Set Marked", inp={"on": "false"}); tail.append("mk")
    # label position: sector centre angle, clockwise from the top
    g.call("c1", K_MATH, "Max", inp={"A": "@entry.count", "B": "1"}); g.call("c1f", K_MATH, "Conv_IntToFloat", inp={"InInt": "@c1.ReturnValue"})
    g.call("st", K_MATH, "Divide_FloatFloat", inp={"A": "360.0", "B": "@c1f.ReturnValue"}); g.call("ang", K_MATH, "Multiply_FloatFloat", inp={"A": "@if.ReturnValue", "B": "@st.ReturnValue"})
    g.call("sn", K_MATH, "DegSin", inp={"A": "@ang.ReturnValue"}); g.call("cs", K_MATH, "DegCos", inp={"A": "@ang.ReturnValue"})
    g.call("x1", K_MATH, "Multiply_FloatFloat", inp={"A": "@sn.ReturnValue", "B": str(RL)}); g.call("x", K_MATH, "Add_FloatFloat", inp={"A": "@x1.ReturnValue", "B": str(R)})
    g.call("y1", K_MATH, "Multiply_FloatFloat", inp={"A": "@cs.ReturnValue", "B": str(RL)}); g.call("y", K_MATH, "Subtract_FloatFloat", inp={"A": str(R), "B": "@y1.ReturnValue"})
    g.call("pos", K_MATH, "MakeVector2D", inp={"X": "@x.ReturnValue", "Y": "@y.ReturnValue"})
    g.get("gl", "Lbl"); g.call("sl", "/Script/UMG.WidgetLayoutLibrary", "SlotAsCanvasSlot", inp={"Widget": "@gl.Lbl"})
    g.call("sp", "/Script/UMG.CanvasPanelSlot", "SetPosition", inp={"self": "@sl.ReturnValue", "InPosition": "@pos.ReturnValue"}); tail.append("sp")
    # icon size: with names fixed, else 55 % of the arc at the label radius, QUICK_ICON_MIN..QUICK_ICON
    g.call("few", K_MATH, "LessEqual_IntInt", inp={"A": "@entry.count", "B": str(QUICK_TEXT_MAX)})
    g.call("arc", K_MATH, "Divide_FloatFloat", inp={"A": str(2 * 3.14159265 * RL * 0.55), "B": "@c1f.ReturnValue"})
    g.call("acl", K_MATH, "FClamp", inp={"Value": "@arc.ReturnValue", "Min": str(float(sz(QUICK_ICON_MIN))), "Max": str(float(sz(QUICK_ICON)))})
    g.call("isz", K_MATH, "SelectFloat", inp={"A": str(float(sz(QUICK_ICON))), "B": "@acl.ReturnValue", "bPickA": "@few.ReturnValue"})
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@entry.icon"}); g.branch("bi", "@iv.ReturnValue"); tail.append("bi")
    g.get("gi", "Icon"); g.call("sb", E_IMAGE, "SetBrushFromTexture", inp={"self": "@gi.Icon", "Texture": "@entry.icon", "bMatchSize": "true"})
    g.get("gib", "IconBox"); g.call("sw", U_SIZE, "SetWidthOverride", inp={"self": "@gib.IconBox", "InWidthOverride": "@isz.ReturnValue"})
    g.get("gib2", "IconBox"); g.call("sh", U_SIZE, "SetHeightOverride", inp={"self": "@gib2.IconBox", "InHeightOverride": "@isz.ReturnValue"})
    g.get("gib3", "IconBox"); g.call("ic", E_WIDGET, "SetVisibility", inp={"self": "@gib3.IconBox", "InVisibility": "Collapsed"})
    # name: up to QUICK_TEXT_MAX sectors, cut to 14 characters + ".." (the centre shows the whole name)
    g.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@entry.caption"}); g.call("ln", K_STR, "Len", inp={"S": "@t2s.ReturnValue"})
    g.call("lg", K_MATH, "Greater_IntInt", inp={"A": "@ln.ReturnValue", "B": "16"}); g.call("lf", K_STR, "Left", inp={"SourceString": "@t2s.ReturnValue", "Count": "14"})
    g.call("ld", K_STR, "Concat_StrStr", inp={"A": "@lf.ReturnValue", "B": ".."}); g.call("ls", K_MATH, "SelectString", inp={"A": "@ld.ReturnValue", "B": "@t2s.ReturnValue", "bPickA": "@lg.ReturnValue"})
    # icons only (more than QUICK_TEXT_MAX) and no icon: the initials of the name's words instead (at most 3, upper case)
    g.call("wd", K_STR, "ParseIntoArray", inp={"SourceString": "@t2s.ReturnValue", "Delimiter": " ", "CullEmptyStrings": "true"}); g.set("swd", "Words", inp={"Words": "@wd.ReturnValue"})
    g.set("si0", "Initials", inp={"Initials": ""}); g.get("gwd", "Words"); g.foreach("fw", "@gwd.Words")
    g.call("w1", K_STR, "Left", inp={"SourceString": "@fw.Array Element", "Count": "1"}); g.call("wu", K_STR, "ToUpper", inp={"SourceString": "@w1.ReturnValue"})
    g.get("gin", "Initials"); g.call("wc", K_STR, "Concat_StrStr", inp={"A": "@gin.Initials", "B": "@wu.ReturnValue"}); g.call("w3", K_STR, "Left", inp={"SourceString": "@wc.ReturnValue", "Count": "3"})
    g.set("si1", "Initials", inp={"Initials": "@w3.ReturnValue"}); g.chain("fw", "si1")
    g.get("gin2", "Initials"); g.call("tsel", K_MATH, "SelectString", inp={"A": "@ls.ReturnValue", "B": "@gin2.Initials", "bPickA": "@few.ReturnValue"})
    g.call("lt", K_TXT, "Conv_StringToText", inp={"InString": "@tsel.ReturnValue"})
    g.get("gn", "Name"); g.call("stx", E_TEXT, "SetText", inp={"self": "@gn.Name", "InText": "@lt.ReturnValue"})
    g.call("noi", K_MATH, "Not_PreBool", inp={"A": "@iv.ReturnValue"}); g.call("shw", K_MATH, "BooleanOR", inp={"A": "@few.ReturnValue", "B": "@noi.ReturnValue"})
    g.branch("bf", "@shw.ReturnValue")   # the name line: with names, or as initials when there is no icon
    g.get("gn2", "Name"); g.call("nh", E_WIDGET, "SetVisibility", inp={"self": "@gn2.Name", "InVisibility": "Collapsed"})
    g.call("op", K_MATH, "SelectFloat", inp={"A": "1.0", "B": "0.4", "bPickA": "@entry.valid"})
    g.get("gl2", "Lbl"); g.call("so", E_WIDGET, "SetRenderOpacity", inp={"self": "@gl2.Lbl", "InOpacity": "@op.ReturnValue"})
    tc = []; text_color(g, "tcn", "Name", mcol(g, "ctx", "ColText"), tc)
    g.chain(*tail); g.chain("bi", "sb", "sw", "sh", "swd"); g.chain("bi:else", "ic", "swd"); g.chain("swd", "si0", "fw"); g.chain("fw:Completed", "stx"); g.chain("stx", "bf", "so"); g.chain("bf:else", "nh", "so"); g.chain("so", *tc)
    init = fn("Init", [param("index", "int"), param("count", "int"), param("caption", "text"), param("icon", "object:" + E_TEX2D), param("valid", "bool")], graph=g)
    m = G(); m.call("c", K_MATH, "SelectColor", inp={"A": mcol(m, "ca", "ColAccent"), "B": mcol(m, "cb", "ColMenuBg"), "bPickA": "@entry.on"})
    # the fill takes the quick menu opacity (Options › Quick menu; follows the panel background until set) - only the fill: icon and
    # name are widgets of their own and stay opaque
    m.get("gqm", "Manager"); m.call("qa", MGR, "Quick Alpha", inp={"self": "@gqm.Manager"}); m.call("bc", K_MATH, "BreakColor", inp={"InColor": "@c.ReturnValue"})
    m.call("mc", K_MATH, "MakeColor", inp={"R": "@bc.R", "G": "@bc.G", "B": "@bc.B", "A": "@qa.alpha"})
    m.get("gm", "Mid"); m.call("sv", MID, "SetVectorParameterValue", inp={"self": "@gm.Mid", "ParameterName": "Color", "Value": "@mc.ReturnValue"}); m.chain("entry", "sv")
    marked = fn("Set Marked", [param("on", "bool")], graph=m)
    return blueprint(W_QSECTOR, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Mid", "object:" + MID), var("Valid", "bool"), var("Words", "string", "array"), var("Initials", "string")],
                     functions=[init, marked], widget_tree=tree)


def w_quick_wheel():
    S = sz(QUICK_SIZE); C = QUICK_SIZE * QUICK_INNER * 0.97   # QUICK_INNER is a share of the radius: diameter = size x inner
    # Root hit-testable over the whole screen: panels default to SelfHitTestInvisible, so only the centre image got OnMouseMove
    # and the marking stuck over the sectors; the angle counts everywhere, also outside the ring
    tree = w(U_CANVAS, "Root", props={"Visibility": "Visible"}, children=[
        w(U_SIZE, "Wheel", props={"bOverride_WidthOverride": True, "WidthOverride": S, "bOverride_HeightOverride": True, "HeightOverride": S},
          slot={"LayoutData": "(Anchors=(Minimum=(X=0.5,Y=0.5),Maximum=(X=0.5,Y=0.5)),Offsets=(Left=0,Top=0,Right=%d,Bottom=%d),Alignment=(X=0.5,Y=0.5))" % (S, S)}, children=[
            w(U_OVERLAY, "WheelOv", children=[
                w(U_OVERLAY, "Sectors", slot=FILL_OV),
                sizebox("CenterBox", C, C, [w(U_OVERLAY, "CenterOv", children=[
                    w(E_IMAGE, "CenterBg", props={"Brush": QSEC_BRUSH}, slot=FILL_OV),
                    sizebox("CenterTextBox", C * 0.8, None, [text("CenterText", "", 13, wrap=True, center=True, break_all=True)], slot={"HorizontalAlignment": "HAlign_Center", "VerticalAlignment": "VAlign_Center"})])],
                        slot={"HorizontalAlignment": "HAlign_Center", "VerticalAlignment": "VAlign_Center"})])])])
    # Init Center: the centre disc (the sector material with one sector, no hole) in a darker menu colour
    ic = G(); tail = ["entry"]
    ic.get("gc", "CenterBg"); ic.call("dm", E_IMAGE, "GetDynamicMaterial", inp={"self": "@gc.CenterBg"}); tail.append("dm")
    for i, (pn, v) in enumerate((("Count", "1.0"), ("Index", "0.0"), ("Inner", "0.0"), ("Gap", "0.0"))):
        ic.call("sp%d" % i, MID, "SetScalarParameterValue", inp={"self": "@dm.ReturnValue", "ParameterName": pn, "Value": v}); tail.append("sp%d" % i)
    ic.call("bc", K_MATH, "BreakColor", inp={"InColor": mcol(ic, "cb", "ColMenuBg")}); ic.call("r", K_MATH, "Multiply_FloatFloat", inp={"A": "@bc.R", "B": "0.6"})
    ic.call("gg", K_MATH, "Multiply_FloatFloat", inp={"A": "@bc.G", "B": "0.6"}); ic.call("b", K_MATH, "Multiply_FloatFloat", inp={"A": "@bc.B", "B": "0.6"})
    ic.get("gqm", "Manager"); ic.call("qa", MGR, "Quick Alpha", inp={"self": "@gqm.Manager"})   # the same opacity as the sectors
    ic.call("mc", K_MATH, "MakeColor", inp={"R": "@r.ReturnValue", "G": "@gg.ReturnValue", "B": "@b.ReturnValue", "A": "@qa.alpha"})
    ic.call("sc", MID, "SetVectorParameterValue", inp={"self": "@dm.ReturnValue", "ParameterName": "Color", "Value": "@mc.ReturnValue"}); tail.append("sc")
    text_color(ic, "tct", "CenterText", mcol(ic, "ctx", "ColText"), tail); ic.chain(*tail)
    sc = G(); sc.get("gt", "CenterText"); sc.call("st", E_TEXT, "SetText", inp={"self": "@gt.CenterText", "InText": "@entry.text"}); sc.chain("entry", "st")
    cl = G(); cl.get("gs", "Sectors"); cl.call("c", E_PANEL, "ClearChildren", inp={"self": "@gs.Sectors"}); cl.chain("entry", "c")
    ad = G(); ad.get("gs", "Sectors"); ad.call("a", U_OVERLAY, "AddChildToOverlay", inp={"self": "@gs.Sectors", "Content": "@entry.widget"})
    ad.call("h", "/Script/UMG.OverlaySlot", "SetHorizontalAlignment", inp={"self": "@a.ReturnValue", "InHorizontalAlignment": "HAlign_Fill"})
    ad.call("v", "/Script/UMG.OverlaySlot", "SetVerticalAlignment", inp={"self": "@a.ReturnValue", "InVerticalAlignment": "VAlign_Fill"}); ad.chain("entry", "a", "h", "v")
    # mouse: offset from the screen centre (the wheel sits there) -> Manager.Quick Hover
    mm = G(); mm.call("sp", K_IN, "PointerEvent_GetScreenSpacePosition", inp={"Input": "@entry.MouseEvent"})
    mm.call("loc", K_SLATE, "AbsoluteToLocal", inp={"Geometry": "@entry.MyGeometry", "AbsoluteCoordinate": "@sp.ReturnValue"}); mm.call("sz", K_SLATE, "GetLocalSize", inp={"Geometry": "@entry.MyGeometry"})
    mm.call("bl", K_MATH, "BreakVector2D", inp={"InVec": "@loc.ReturnValue"}); mm.call("bs", K_MATH, "BreakVector2D", inp={"InVec": "@sz.ReturnValue"})
    mm.call("hx", K_MATH, "Multiply_FloatFloat", inp={"A": "@bs.X", "B": "0.5"}); mm.call("hy", K_MATH, "Multiply_FloatFloat", inp={"A": "@bs.Y", "B": "0.5"})
    mm.call("dx", K_MATH, "Subtract_FloatFloat", inp={"A": "@bl.X", "B": "@hx.ReturnValue"}); mm.call("dy", K_MATH, "Subtract_FloatFloat", inp={"A": "@bl.Y", "B": "@hy.ReturnValue"})
    mm.get("gm", "Manager"); mm.call("qh", MGR, "Quick Hover", inp={"self": "@gm.Manager", "dx": "@dx.ReturnValue", "dy": "@dy.ReturnValue", "radius": str(S / 2.0)})
    mm.call("h", K_WBL, "Handled"); mm.link("h.ReturnValue", "return.ReturnValue"); mm.chain("entry", "qh", "return")
    # keys: the quick key's release runs the marked item, Esc cancels; every key is kept from the game while the wheel is open
    ku = G(); ku.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"}); ku.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Escape"}); ku.branch("be", "@esc.ReturnValue")
    ku.call("kdn", K_IN, "Key_GetDisplayName", inp={"Key": "@key.ReturnValue"}); ku.call("kds", K_TXT, "Conv_TextToString", inp={"InText": "@kdn.ReturnValue"})
    ku.get("gmk", "Manager"); ku.get("gqk", "QuickKey", cls=MGR); ku.link("gmk.Manager", "gqk.self"); ku.call("qks", K_STR, "Conv_NameToString", inp={"InName": "@gqk.QuickKey"})
    ku.call("kk", K_STR, "EqualEqual_StriStri", inp={"A": "@kds.ReturnValue", "B": "@qks.ReturnValue"}); ku.branch("bk", "@kk.ReturnValue")
    ku.get("gm", "Manager"); ku.call("qc", MGR, "Quick Cancel", inp={"self": "@gm.Manager"}); ku.get("gm2", "Manager"); ku.call("qr", MGR, "Quick Release", inp={"self": "@gm2.Manager"})
    ku.call("h", K_WBL, "Handled"); ku.link("h.ReturnValue", "return.ReturnValue")
    ku.chain("entry", "be", "qc", "return"); ku.chain("be:else", "bk", "qr", "return"); ku.chain("bk:else", "return")
    kd = G(); kd.call("h", K_WBL, "Handled"); kd.link("h.ReturnValue", "return.ReturnValue"); kd.chain("entry", "return")
    mu = G(); mu.call("btn", K_IN, "PointerEvent_GetEffectingButton", inp={"Input": "@entry.MouseEvent"}); mu.call("isl", K_IN, "EqualEqual_KeyKey", inp={"A": "@btn.ReturnValue", "B": "LeftMouseButton"})
    mu.branch("b", "@isl.ReturnValue"); mu.get("gm", "Manager"); mu.call("qr", MGR, "Quick Release", inp={"self": "@gm.Manager"})
    mu.call("h", K_WBL, "Handled"); mu.link("h.ReturnValue", "return.ReturnValue"); mu.chain("entry", "b", "qr", "return"); mu.chain("b:else", "return")
    md = G(); md.call("h", K_WBL, "Handled"); md.link("h.ReturnValue", "return.ReturnValue"); md.chain("entry", "return")
    return blueprint(W_QUICK, E_USERWIDGET, variables=[var("Manager", "object:" + MGR)],
                     functions=[fn("Init Center", graph=ic), fn("Set Center", [param("text", "text")], graph=sc), fn("Clear Sectors", graph=cl), fn("Add Sector", [param("widget", "object:" + E_WIDGET)], graph=ad),
                                fn("OnMouseMove", override=True, graph=mm), fn("OnKeyUp", override=True, graph=ku), fn("OnKeyDown", override=True, graph=kd),
                                fn("OnMouseButtonUp", override=True, graph=mu), fn("OnMouseButtonDown", override=True, graph=md)],
                     widget_tree=tree, defaults={"bIsFocusable": "true"})


assets = [w_quick_row(), w_quick_sector(), w_quick_wheel(), w_tooltip(), w_group_header(), w_value_row(), w_content_section(), w_slot_tab(), w_clothes_button(), w_sub_tab(), w_top_tab(), w_list_head(), w_vrow(), w_outfit_button(), w_look_button(scale_fn="Look Scale"), w_look_button(W_FACEBTN, "On Face Clicked", "On Face Context", "Set Face Name", "Btn_SaveFace", (104, 164), (88, 88)),
          w_look_button(W_KODEXTILE, "Kodex Tile Clicked", "Kodex Tile Clicked", "Kodex Noop Rename", "Btn_SaveLook", (136, 236), (120, 180)),
          w_look_button(W_RAGTILE, "Rag Kind Clicked", "Rag Kind Clicked", "Kodex Noop Rename", "Btn_SaveLook", (104, 196), (88, 132), scale_fn="Rag Scale", links=True), w_text_button(), w_link_row(), w_rag_poses(), w_name_row(), w_conflict_row(), w_fol_row(), w_kodex_lock_row(), w_hair_swatch(), w_mod_field(), w_face_row(), w_round_button(), w_menu_row(), w_menu_slider(), w_menu_amount(), w_context_menu(), w_color_swatch(), w_hex_bar(), w_version_warning(), w_panel()]
write(os.path.join(os.path.dirname(__file__), "..", "40_widgets.json"), assets)
