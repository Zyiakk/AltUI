"""Generates assets/40_widgets.json: panel and element widgets (thin; the logic lives in the manager)."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *

MGR = M + "/BP_AltUIManager"
S_ITEM = M + "/S_ClothesItem"
T_ITEM = "struct:" + S_ITEM
W_PANEL = M + "/W_AltUI"
W_HEAD = M + "/W_GroupHeader"
W_TAB = M + "/W_SlotTab"
W_BTN = M + "/W_ClothesButton"
W_SUB = M + "/W_SubTab"
W_ROUND = M + "/W_RoundButton"; T_PLUS = M + "/T_Plus"; T_MINUS = M + "/T_Minus"; T_COLORIZE = M + "/T_Colorize"
W_TOP = M + "/W_TopTab"
W_OUTFIT = M + "/W_OutfitButton"; W_LOOK = M + "/W_LookButton"; W_TOOLTIP = M + "/W_Tooltip"; W_SECTION = M + "/W_ContentSection"
U_OVERLAY = "/Script/UMG.Overlay"
U_VBOX = "/Script/UMG.VerticalBox"; U_HBOX = "/Script/UMG.HorizontalBox"; U_SCROLL = "/Script/UMG.ScrollBox"
U_WRAP = "/Script/UMG.WrapBox"; U_SCALE = "/Script/UMG.ScaleBox"; U_SIZE = "/Script/UMG.SizeBox"; U_CANVAS = "/Script/UMG.CanvasPanel"; U_PANELW = "/Script/UMG.PanelWidget"

SC = 1.9   # global size factor (2560x1440)
def sz(v): return int(round(v * SC))
FULL = {"LayoutData": "(Anchors=(Minimum=(X=0,Y=0),Maximum=(X=1,Y=1)),Offsets=(Left=0,Top=0,Right=0,Bottom=0))"}
FILL = {"Size": "(SizeRule=Fill,Value=1)"}
COL_BG = "(R=0.02,G=0.02,B=0.03,A=0.88)"
# COL_* below are the widget-tree initial values only: at runtime every colour comes from the manager theme (Manager.Col*, theme.py)
# via Compute Colors / W_AltUI.Apply Theme; the defaults of theme.py mirror these values.
# tiles / chips: round box texture (white, tinted via BrushColor), 9-slice with 16px corners
T_ROUNDBOX = M + "/T_RoundBox"
T_CHECK_ON = M + "/T_CheckOn"; T_CHECK_OFF = M + "/T_CheckOff"
W_TXT = M + "/W_TextButton"
SEARCH_FONT = 16; SEARCH_PAD = 7
CHECK_SIZE = int(round(sz(SEARCH_FONT) * 1.2 + 2 * sz(SEARCH_PAD) + 2 * sz(1)))   # = height of the search bar
COL_LINK = "(SpecifiedColor=(R=0.62,G=0.76,B=1.0,A=1))"
ROUNDBOX = "(ResourceObject=Texture2D'%s.T_RoundBox',ImageSize=(X=48,Y=48),DrawAs=Box,Margin=(Left=0.33,Top=0.33,Right=0.33,Bottom=0.33))" % T_ROUNDBOX
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


def text(name, txt="", size=12, color=WHITE, wrap=False, slot=None, center=False, break_all=False):
    p = {"Text": txt, "Font": "(Size=%d)" % sz(size), "ColorAndOpacity": color}
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


def tile_scale(g, tail, boxes):
    """Multiply SizeBox sizes by Manager.TileScale (init chain)."""
    g.get("tsm", "Manager"); g.get("tsv", "TileScale", cls=MGR); g.link("tsm.Manager", "tsv.self")
    for name, wd, ht in boxes:
        g.call("tw_" + name, K_MATH, "Multiply_FloatFloat", inp={"A": str(float(sz(wd))), "B": "@tsv.TileScale"})
        g.call("th_" + name, K_MATH, "Multiply_FloatFloat", inp={"A": str(float(sz(ht))), "B": "@tsv.TileScale"})
        g.get("tg_" + name, name); g.call("tsw_" + name, U_SIZE, "SetWidthOverride", inp={"self": "@tg_%s.%s" % (name, name), "InWidthOverride": "@tw_%s.ReturnValue" % name})
        g.get("tg2_" + name, name); g.call("tsh_" + name, U_SIZE, "SetHeightOverride", inp={"self": "@tg2_%s.%s" % (name, name), "InHeightOverride": "@th_%s.ReturnValue" % name})
        tail += ["tsw_" + name, "tsh_" + name]


def roundbox(name, color, pad, children, props=None, slot=None):
    """Border with the round box texture (frame or fill)."""
    p = {"Background": ROUNDBOX, "BrushColor": color, "Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % ((sz(pad),) * 4)}
    if props: p.update(props)
    return w(E_BORDER, name, props=p, slot=slot, children=children)


def hover_parts(cls, frame, fill):
    """Hover mechanics: variables Base*/Hover*, function `Apply Colors(hover)` and event graph OnMouseEnter/Leave.
    frame/fill = name of the border widget (frame optional). Returns (variables, functions, event_graph)."""
    names = [n for n in (("Frame", frame), ("Fill", fill)) if n[1]]
    vars_ = [var(pre + part, S_LINCOLOR) for part, _ in names for pre in ("Base", "Hover")]
    g = G(); chain = ["entry"]
    for part, wn in names:
        g.get("gb" + part, "Base" + part); g.get("gh" + part, "Hover" + part)
        g.call("c" + part, K_MATH, "SelectColor", inp={"A": "@gh%s.Hover%s" % (part, part), "B": "@gb%s.Base%s" % (part, part), "bPickA": "@entry.hover"})
        g.get("gw" + part, wn); g.call("s" + part, E_BORDER, "SetBrushColor", inp={"self": "@gw%s.%s" % (part, wn), "InBrushColor": "@c%s.ReturnValue" % part})
        chain.append("s" + part)
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
    return w(U_SIZE, name, props={"bOverride_WidthOverride": True, "WidthOverride": sz(wd), "bOverride_HeightOverride": True, "HeightOverride": sz(ht)}, slot=slot, children=children)


def mt(g, id, key):
    """Manager.T(key) (pure) -> text pin; widgets know the manager through the variable Manager."""
    g.get(id + "_m", "Manager"); g.call(id, MGR, "T", inp={"self": "@%s_m.Manager" % id, "key": key}); return "@%s.text" % id


def mts(g, id, key):
    """Manager.T(key) as a string pin."""
    g.call(id + "_2s", K_TXT, "Conv_TextToString", inp={"InText": mt(g, id, key)}); return "@%s_2s.ReturnValue" % id


def mouse_down_override(left_fn, right_fn, arg_var, pin="name"):
    """OnMouseButtonDown: right mouse button -> right_fn, else left_fn (manager function with one argument `pin`). Remembers the widget as Manager.LastButton."""
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
    g.chain("entry", "slb", "b", "r", "return"); g.chain("b:else", "l", "return")
    return fn("OnMouseButtonDown", override=True, graph=g)


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


def rename_tick():
    """Tick of the renameable tiles: Editing and the text field lost the keyboard focus -> End Rename."""
    tk = G(); tk.get("ged", "Editing"); tk.get("ge", "NameEdit"); tk.call("hf", E_WIDGET, "HasKeyboardFocus", inp={"self": "@ge.NameEdit"})
    tk.call("nf", K_MATH, "Not_PreBool", inp={"A": "@hf.ReturnValue"}); tk.call("and", K_MATH, "BooleanAND", inp={"A": "@ged.Editing", "B": "@nf.ReturnValue"}); tk.branch("b", "@and.ReturnValue")
    tk.n("er", "call_self", function="End Rename"); tk.chain("entry", "b", "er"); return tk


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
        w(U_WRAP, "Tiles", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)}),
        w(E_TEXT, "Note", props={"Text": "", "Font": "(Size=%d)" % sz(12), "ColorAndOpacity": GREY, "Visibility": "Collapsed"}, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(6)})])
    g = G(); g.get("gh", "Header"); g.call("st", E_TEXT, "SetText", inp={"self": "@gh.Header", "InText": "@entry.caption"}); g.n("cc", "call_self", function="Compute Colors"); g.chain("entry", "st", "cc")
    a = G(); a.get("gt", "Tiles"); a.call("ad", U_WRAP, "AddChildToWrapBox", inp={"self": "@gt.Tiles", "Content": "@entry.widget"}); a.chain("entry", "ad")
    n = G(); n.get("gn", "Note"); n.call("sn", E_TEXT, "SetText", inp={"self": "@gn.Note", "InText": "@entry.text"})
    n.get("gn2", "Note"); n.call("vn", E_WIDGET, "SetVisibility", inp={"self": "@gn2.Note", "InVisibility": "Visible"}); n.chain("entry", "sn", "vn")
    c = G(); tail = ["entry"]; text_color(c, "th", "Header", mcol(c, "ch", "ColHead"), tail); text_color(c, "tn", "Note", mcol(c, "cn", "ColTextDim"), tail); c.chain(*tail)
    return blueprint(W_SECTION, E_USERWIDGET, variables=[var("Manager", "object:" + MGR)],
                     functions=[fn("Init", [param("caption", "text")], graph=g), fn("Add Tile", [param("widget", "object:" + E_WIDGET)], graph=a),
                                fn("Set Note", [param("text", "text")], graph=n), compute_fn(c)], widget_tree=tree)


# ---------------- W_SlotTab ----------------
def w_slot_tab():
    tree = w(E_BORDER, "Fill", props={"BrushColor": COL_ROW, "Padding": "(Left=0,Top=0,Right=0,Bottom=0)"}, children=[
        w(U_VBOX, "Col", children=[
            w(U_HBOX, "HB", children=[
                w(U_SIZE, "AccentBox", props={"bOverride_WidthOverride": True, "WidthOverride": sz(2)}, slot={"VerticalAlignment": "VAlign_Fill"},
                  children=[w(E_BORDER, "Accent", props={"BrushColor": COL_NONE, "Padding": "(Left=0,Top=0,Right=0,Bottom=0)"})]),
                fit_image("Thumb", 44, 44, hidden=True, slot={"Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(9), sz(4), sz(8), sz(4)), "VerticalAlignment": "VAlign_Center"}),
                w(U_VBOX, "VB", slot={**FILL, "VerticalAlignment": "VAlign_Center"}, children=[text("Name", "Slot", 13), text("Count", "0", 10, GREY)]),
            ]),
            w(U_SIZE, "LineBox", props={"bOverride_HeightOverride": True, "HeightOverride": 1},
              children=[w(E_BORDER, "Line", props={"BrushColor": COL_LINE, "Padding": "(Left=0,Top=0,Right=0,Bottom=0)"})]),
        ])])
    hv, hf, eg = hover_parts(W_TAB, None, "Fill")
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
    g.n("cc", "call_self", function="Compute Colors"); tail.append("cc")
    g.n("ap", "call_self", function="Apply Colors", inp={"hover": "false"}); tail.append("ap")
    g.call("iv", K_SYS, "IsValid", inp={"Object": "@entry.worn icon"})
    g.branch("b", "@iv.ReturnValue"); tail.append("b")
    g.get("gt", "Thumb"); g.call("sb", E_IMAGE, "SetBrushFromTexture", inp={"self": "@gt.Thumb", "Texture": "@entry.worn icon", "bMatchSize": "true"})
    g.get("gt2", "Thumb"); g.call("sv", E_WIDGET, "SetVisibility", inp={"self": "@gt2.Thumb", "InVisibility": "Visible"})
    g.get("gt3", "Thumb"); g.call("sh", E_WIDGET, "SetVisibility", inp={"self": "@gt3.Thumb", "InVisibility": "Hidden"})
    g.chain(*tail, "sb", "sv"); g.chain("b:else", "sh")
    init = fn("Init", [param("slot", "name"), param("caption", "text"), param("count", "int"), param("worn icon", "object:" + E_TEX2D),
                       param("selected", "bool"), param("has items", "bool"), param("filtered", "int")], graph=g)
    # colours from the manager theme: red accent bar + lighter row when selected; line, text
    c = G(); tail = ["entry"]; c.get("gsl", "Selected")
    c.call("ac", K_MATH, "SelectColor", inp={"A": mcol(c, "ca", "ColAccent"), "B": COL_NONE, "bPickA": "@gsl.Selected"}); brush(c, "sac", "Accent", "@ac.ReturnValue", tail)
    brush(c, "sln", "Line", mcol(c, "cl", "ColLine"), tail)
    c.call("c1", K_MATH, "SelectColor", inp={"A": mcol(c, "crs", "ColRowSel"), "B": mcol(c, "cr", "ColRow"), "bPickA": "@gsl.Selected"})
    c.call("c2", K_MATH, "SelectColor", inp={"A": mcol(c, "crsh", "ColRowSelHover"), "B": mcol(c, "crh", "ColRowHover"), "bPickA": "@gsl.Selected"})
    set_colors(c, "Fill", "@c1.ReturnValue", "@c2.ReturnValue", tail)
    text_color(c, "tn", "Name", mcol(c, "ct", "ColText"), tail); text_color(c, "tcn", "Count", mcol(c, "ctd", "ColTextDim"), tail); c.chain(*tail)
    return blueprint(W_TAB, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("SlotName", "name"), var("Selected", "bool")] + hv,
                     functions=[init, compute_fn(c), mouse_down_override("Select Slot", "Take Off Slot", "SlotName")] + hf, event_graph=eg, widget_tree=tree, defaults=HAND)


# ---------------- W_ClothesButton ----------------
def w_clothes_button():
    tree = sizebox("Box", 104, 160, [   # room for 3 name lines + badge
        roundbox("Frame", COL_FRAME, 1, props={"Clipping": "ClipToBounds"}, children=[
            roundbox("Fill", COL_FILL, 4, children=[
                w(U_VBOX, "VB", children=[
                    # icon + "colour adjustable" subscript (vanilla ItemButton.Image_subscript) in the lower right corner
                    w(U_OVERLAY, "IconOv", slot={"HorizontalAlignment": "HAlign_Center"}, children=[
                        fit_image("Icon", 88, 88),
                        sizebox("ColorizeBox", 20, 20, [w(E_IMAGE, "Colorize", props={"Brush": "(ResourceObject=Texture2D'%s.T_Colorize',ImageSize=(X=48,Y=48),DrawAs=Image)" % T_COLORIZE, "Visibility": "Collapsed"})],
                                slot={"HorizontalAlignment": "HAlign_Right", "VerticalAlignment": "VAlign_Bottom"}),
                        # stored colour of a piece in the content view (replaces the "colour adjustable" symbol there)
                        w(U_SIZE, "SwatchBox", props={"bOverride_WidthOverride": True, "WidthOverride": sz(20), "bOverride_HeightOverride": True, "HeightOverride": sz(20), "Visibility": "Collapsed"},
                          slot={"HorizontalAlignment": "HAlign_Right", "VerticalAlignment": "VAlign_Bottom"},
                          children=[roundbox("SwatchFrame", COL_FRAME, 1, [roundbox("Swatch", "(R=1,G=1,B=1,A=1)", 0, [])])])]),
                    text("Name", "Name", 11, WHITE, wrap=True, center=True, break_all=True, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    text("Badge", "", 9, "(SpecifiedColor=(R=1,G=0.6,B=0.3,A=1))", center=True),
                ])])])])
    hv, hf, eg = hover_parts(W_BTN, "Frame", "Fill")
    g = G(); tail = ["entry"]
    tile_scale(g, tail, [("Box", 104, 160), ("IconBox", 88, 88), ("ColorizeBox", 20, 20), ("SwatchBox", 20, 20)])
    g.brk("bi", S_ITEM, "@entry.item")
    g.set("sn", "ItemName", inp={"ItemName": "@bi.Name"}); tail.append("sn")
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
    g.call("ic", K_MATH, "SelectColor", inp={"A": "(R=1,G=1,B=1,A=1)", "B": "(R=0.5,G=0.5,B=0.5,A=0.6)", "bPickA": "@entry.owned"})
    g.get("gi2", "Icon"); g.call("sic", E_IMAGE, "SetColorAndOpacity", inp={"self": "@gi2.Icon", "InColorAndOpacity": "@ic.ReturnValue"}); tail2.append("sic")
    g.call("bs", K_MATH, "SelectString", inp={"A": "", "B": mts(g, "sno", "State_NotOwned"), "bPickA": "@entry.owned"})
    g.call("fs", K_MATH, "SelectString", inp={"A": mts(g, "sfv", "State_Fav"), "B": "@bs.ReturnValue", "bPickA": "@entry.fav"})
    g.call("ds", K_MATH, "SelectString", inp={"A": mts(g, "sdm", "State_Damaged"), "B": "@fs.ReturnValue", "bPickA": "@entry.damaged"})
    g.call("bt", K_TXT, "Conv_StringToText", inp={"InString": "@ds.ReturnValue"})
    g.get("gbd", "Badge"); g.call("stb", E_TEXT, "SetText", inp={"self": "@gbd.Badge", "InText": "@bt.ReturnValue"}); tail2.append("stb")
    # tail: ... "sn", "bca" | "vcz"/"ccz" -> rest
    i = tail.index("bca"); rest = tail[i + 1:]; tail = tail[:i + 1]
    g.chain(*tail, "vcz", *rest, "sb", *tail2); g.chain("bca:else", "ccz", rest[0]); g.chain("b:else", tail2[0])
    init = fn("Init", [param("item", T_ITEM), param("worn", "bool"), param("owned", "bool"), param("fav", "bool"), param("damaged", "bool"), param("tip", "text")], graph=g)
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
    return blueprint(W_BTN, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("ItemName", "name"), var("ItemSlot", "name"), var("Worn", "bool"), var("Owned", "bool"), var("Highlight", "bool")] + hv,
                     functions=[init, compute_fn(c), mouse_down_override("On Item Clicked", "On Item Context", "ItemName"), fn("Set Color Swatch", [param("color", S_LINCOLOR)], graph=sc)] + hf,
                     event_graph=eg, widget_tree=tree, defaults=HAND)


# ---------------- W_SubTab ----------------
def w_sub_tab():
    tree = roundbox("Frame", COL_CHIP_FRAME, 1, children=[
        roundbox("Fill", COL_CHIP, 0, props={"Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(10), sz(4), sz(10), sz(4))}, children=[text("Label", "Alle", 12)])])
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
    return blueprint(W_SUB, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Group", "name"), var("Selected", "bool")] + hv,
                     functions=[init, compute_fn(c), refresh_fn(), mouse_down_override("Select SubTab", "Select SubTab", "Group")] + hf, event_graph=eg, widget_tree=tree, defaults=HAND)


# ---------------- W_TopTab (tab bar at the top: text + red underline) ----------------
def w_top_tab():
    tree = w(E_BORDER, "Fill", props={"BrushColor": COL_NONE, "Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(14), sz(4), sz(14), sz(0))}, children=[
        w(U_VBOX, "VB", children=[
            text("Label", "Reiter", 14, slot={"HorizontalAlignment": "HAlign_Center", "Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(5)}),
            w(U_SIZE, "LineBox", props={"bOverride_HeightOverride": True, "HeightOverride": sz(1.5)},
              children=[w(E_BORDER, "Accent", props={"BrushColor": COL_NONE, "Padding": "(Left=0,Top=0,Right=0,Bottom=0)"})]),
        ])])
    hv, hf, eg = hover_parts(W_TOP, None, "Fill")
    g = G(); tail = ["entry"]
    g.set("sp", "Page", inp={"Page": "@entry.page"}); tail.append("sp")
    g.set("ssl", "Selected", inp={"Selected": "@entry.selected"}); tail.append("ssl")
    g.get("gl", "Label"); g.call("st", E_TEXT, "SetText", inp={"self": "@gl.Label", "InText": "@entry.caption"}); tail.append("st")
    g.call("op", K_MATH, "SelectFloat", inp={"A": "1.0", "B": "0.7", "bPickA": "@entry.selected"})
    g.get("gl2", "Label"); g.call("so", E_TEXT, "SetOpacity", inp={"self": "@gl2.Label", "InOpacity": "@op.ReturnValue"}); tail.append("so")
    g.n("cc", "call_self", function="Compute Colors"); tail.append("cc")
    g.n("ap", "call_self", function="Apply Colors", inp={"hover": "false"}); tail.append("ap")
    g.chain(*tail)
    init = fn("Init", [param("page", "name"), param("caption", "text"), param("selected", "bool")], graph=g)
    c = G(); tail = ["entry"]; c.get("gsl", "Selected")
    c.call("ac", K_MATH, "SelectColor", inp={"A": mcol(c, "ca", "ColAccent"), "B": COL_NONE, "bPickA": "@gsl.Selected"}); brush(c, "sac", "Accent", "@ac.ReturnValue", tail)
    set_colors(c, "Fill", COL_NONE, mcol(c, "cth", "ColTopHover"), tail)
    text_color(c, "tl", "Label", mcol(c, "ct", "ColText"), tail); c.chain(*tail)
    return blueprint(W_TOP, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Page", "name"), var("Selected", "bool")] + hv,
                     functions=[init, compute_fn(c), refresh_fn(), mouse_down_override("Select Page", "Select Page", "Page")] + hf, event_graph=eg, widget_tree=tree, defaults=HAND)


def tile_colors(*texts):
    """Compute Colors of a plain tile (frame/fill without state) + text colours [(widget, ColX), ...]."""
    c = G(); tail = ["entry"]
    set_colors(c, "Frame", mcol(c, "cf", "ColFrame"), mcol(c, "cfh", "ColFrameHover"), tail); set_colors(c, "Fill", mcol(c, "cfi", "ColFill"), mcol(c, "cfih", "ColFillHover"), tail)
    for i, (wn, col) in enumerate(texts): text_color(c, "tc%d" % i, wn, mcol(c, "cc%d" % i, col), tail)
    c.chain(*tail); return compute_fn(c)


# ---------------- W_OutfitButton (3x2 icons + label; index -1 = "+ save") ----------------
OUTFIT_ICONS = 9


def w_outfit_button():
    def icon(i): return fit_image("Icon%d" % i, 46, 46, hidden=True, slot={"Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(1), sz(1), sz(1), sz(1))})
    tree = sizebox("Box", 160, 198, [
        roundbox("Frame", COL_FRAME, 1, props={"Clipping": "ClipToBounds"}, children=[
            roundbox("Fill", COL_FILL, 4, children=[
                w(U_VBOX, "VB", children=[
                    w(U_HBOX, "Row0", slot={"HorizontalAlignment": "HAlign_Center"}, children=[icon(0), icon(1), icon(2)]),
                    w(U_HBOX, "Row1", slot={"HorizontalAlignment": "HAlign_Center"}, children=[icon(3), icon(4), icon(5)]),
                    w(U_HBOX, "Row2", slot={"HorizontalAlignment": "HAlign_Center"}, children=[icon(6), icon(7), icon(8)]),
                    sizebox("PlusBox", 144, 144, [text("Plus", "+", 44, WHITE, center=True, slot={"VerticalAlignment": "VAlign_Center", "HorizontalAlignment": "HAlign_Fill"})],
                            slot={"HorizontalAlignment": "HAlign_Center"}),
                    text("Label", "Outfit", 11, WHITE, wrap=True, center=True, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(E_EDIT, "NameEdit", props={"Visibility": "Collapsed", "SelectAllTextWhenFocused": True, "ClearKeyboardFocusOnCommit": False,   # otherwise focus is lost on the Enter key-down -> Tick ends editing before the Enter key-up
                                                "WidgetStyle": "(Font=(Size=%d),Padding=(Left=%d,Top=%d,Right=%d,Bottom=%d),BackgroundColor=(SpecifiedColor=(R=0.1,G=0.1,B=0.12,A=1)),ForegroundColor=(SpecifiedColor=(R=1,G=1,B=1,A=1)))" % (sz(11), sz(4), sz(2), sz(4), sz(2))},
                      slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                ])])])])
    hv, hf, eg = hover_parts(W_OUTFIT, "Frame", "Fill")
    g = G(); tail = ["entry"]
    tile_scale(g, tail, [("Box", 160, 198), ("PlusBox", 144, 144)] + [("Icon%dBox" % i, 46, 46) for i in range(OUTFIT_ICONS)])
    g.set("si", "Index", inp={"Index": "@entry.index"}); tail.append("si")
    g.call("neg", K_MATH, "Less_IntInt", inp={"A": "@entry.index", "B": "0"})
    # visibility: the "+" tile shows only the plus, otherwise the icon rows
    for wn, when_add in (("Row0", "Collapsed"), ("Row1", "Collapsed"), ("Row2", "Collapsed"), ("PlusBox", "Visible")):
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
    # icons 0..5: set the existing ones, hide the rest (layout stays)
    icon_chain = []
    for i in range(OUTFIT_ICONS):
        g.call("vi%d" % i, K_ARR, "Array_IsValidIndex", inp={"TargetArray": "@entry.icons", "IndexToTest": str(i)}); g.branch("bi%d" % i, "@vi%d.ReturnValue" % i)
        g.call("gt%d" % i, K_ARR, "Array_Get", inp={"TargetArray": "@entry.icons", "Index": str(i)})
        g.get("gi%d" % i, "Icon%d" % i); g.call("sb%d" % i, E_IMAGE, "SetBrushFromTexture", inp={"self": "@gi%d.Icon%d" % (i, i), "Texture": "@gt%d.Item" % i, "bMatchSize": "true"})
        g.get("gv%d" % i, "Icon%d" % i); g.call("sv%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@gv%d.Icon%d" % (i, i), "InVisibility": "Visible"})
        g.get("gh%d" % i, "Icon%d" % i); g.call("sh%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@gh%d.Icon%d" % (i, i), "InVisibility": "Hidden"})
        icon_chain.append(i)
    g.n("cc", "call_self", function="Compute Colors"); g.n("ap", "call_self", function="Apply Colors", inp={"hover": "false"})
    g.chain(*tail); g.chain("badd", "vRow0", "vRow1", "vRow2", "vPlusBox", "stl"); g.chain("badd:else", "cRow0", "cRow1", "cRow2", "cPlusBox", "stl")
    g.chain("stl", "bi0")
    for i in icon_chain:
        g.chain("bi%d" % i, "sb%d" % i, "sv%d" % i); g.chain("bi%d:else" % i, "sh%d" % i)
        nxt = "bi%d" % (i + 1) if i + 1 < OUTFIT_ICONS else "cc"
        g.chain("sv%d" % i, nxt); g.chain("sh%d" % i, nxt)
    g.chain("cc", "ap")
    init = fn("Init", [param("index", "int"), param("icons", "object:" + E_TEX2D, "array"), param("count", "int"), param("caption", "text")], graph=g)
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
    er.chain("entry", "se", "hv", "sl")
    # OnKeyUp: only responsible while editing (key-ups bubble up from the text field; BPGen cannot bind OnTextCommitted).
    # Enter -> Manager.Set Outfit Name, Esc -> cancel; always Handled while editing (the panel never sees Esc/K), otherwise Unhandled
    ku = G(); ku.get("ged", "Editing"); ku.branch("be", "@ged.Editing")
    ku.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"})
    ku.call("ent", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Enter"}); ku.branch("ben", "@ent.ReturnValue")
    ku.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Escape"}); ku.branch("bes", "@esc.ReturnValue")
    ku.get("ge", "NameEdit"); ku.call("gt", E_EDIT, "GetText", inp={"self": "@ge.NameEdit"}); ku.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@gt.ReturnValue"})
    ku.get("gm", "Manager"); ku.get("gi", "Index"); ku.call("sn", MGR, "Set Outfit Name", inp={"self": "@gm.Manager", "index": "@gi.Index", "name": "@t2s.ReturnValue"})
    ku.n("er", "call_self", function="End Rename")
    ku.call("h", K_WBL, "Handled"); ku.link("h.ReturnValue", "return.ReturnValue")
    ku.n("r2", "return_new"); ku.call("u", K_WBL, "Unhandled"); ku.link("u.ReturnValue", "r2.ReturnValue")
    ku.chain("entry", "be", "ben", "sn", "return"); ku.chain("ben:else", "bes", "er", "return"); ku.chain("bes:else", "return"); ku.chain("be:else", "r2")
    # Tick: focus lost while renaming (click elsewhere) -> cancel (BPGen cannot bind OnTextCommitted)
    tk = rename_tick()
    return blueprint(W_OUTFIT, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Index", "int"), var("Editing", "bool")] + hv,
                     functions=[init, tile_colors(("Label", "ColText"), ("Plus", "ColText")), mouse_down_override("On Outfit Clicked", "On Outfit Context", "Index", pin="index"),
                                fn("Begin Rename", [param("current", "string")], graph=br), fn("End Rename", graph=er),
                                fn("OnKeyUp", override=True, graph=ku), fn("Tick", override=True, graph=tk)] + hf, event_graph=eg, widget_tree=tree, defaults=HAND)


# ---------------- W_LookButton (portrait photo + name; index -1 = "+ save"; inline rename like W_OutfitButton) ----------------
def w_look_button():
    tree = sizebox("Box", 104, 236, [
        roundbox("Frame", COL_FRAME, 1, props={"Clipping": "ClipToBounds"}, children=[
            roundbox("Fill", COL_FILL, 4, children=[
                w(U_VBOX, "VB", children=[
                    sizebox("PhotoBox", 88, 176, [w(U_OVERLAY, "PhotoOv", children=[
                        w(E_IMAGE, "Photo", props={"Visibility": "Collapsed"}, slot={"HorizontalAlignment": "HAlign_Fill", "VerticalAlignment": "VAlign_Fill"}),
                        text("NoPhoto", "", 10, GREY, center=True, slot={"HorizontalAlignment": "HAlign_Center", "VerticalAlignment": "VAlign_Center"}),
                        text("Plus", "+", 44, WHITE, center=True, slot={"HorizontalAlignment": "HAlign_Center", "VerticalAlignment": "VAlign_Center"})])],
                            slot={"HorizontalAlignment": "HAlign_Center"}),
                    text("Label", "Look", 11, WHITE, wrap=True, center=True, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                    w(E_EDIT, "NameEdit", props={"Visibility": "Collapsed", "SelectAllTextWhenFocused": True, "ClearKeyboardFocusOnCommit": False,
                                                "WidgetStyle": "(Font=(Size=%d),Padding=(Left=%d,Top=%d,Right=%d,Bottom=%d),BackgroundColor=(SpecifiedColor=(R=0.1,G=0.1,B=0.12,A=1)),ForegroundColor=(SpecifiedColor=(R=1,G=1,B=1,A=1)))" % (sz(11), sz(4), sz(2), sz(4), sz(2))},
                      slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(3)}),
                ])])])])
    hv, hf, eg = hover_parts(W_LOOK, "Frame", "Fill")
    g = G(); tail = ["entry"]
    tile_scale(g, tail, [("Box", 104, 236), ("PhotoBox", 88, 176)])
    g.set("si", "Index", inp={"Index": "@entry.index"}); tail.append("si")
    g.call("neg", K_MATH, "Less_IntInt", inp={"A": "@entry.index", "B": "0"}); g.branch("badd", "@neg.ReturnValue"); tail.append("badd")
    # "+" tile: plus only; look tile: photo (or "no photo" text) + name
    g.get("gpl", "Plus"); g.call("vpl", E_WIDGET, "SetVisibility", inp={"self": "@gpl.Plus", "InVisibility": "Visible"})
    g.get("gph", "Photo"); g.call("cph", E_WIDGET, "SetVisibility", inp={"self": "@gph.Photo", "InVisibility": "Collapsed"})
    g.get("gnp", "NoPhoto"); g.call("cnp", E_WIDGET, "SetVisibility", inp={"self": "@gnp.NoPhoto", "InVisibility": "Collapsed"})
    g.get("gl1", "Label"); g.call("sl1", E_TEXT, "SetText", inp={"self": "@gl1.Label", "InText": mt(g, "mtsv", "Btn_SaveLook")})
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
    g.chain(*tail); g.chain("badd", "vpl", "cph", "cnp", "sl1", "cc"); g.chain("badd:else", "cpl", "biv", "sb", "vph", "cnp2", "sl2"); g.chain("biv:else", "snp", "vnp", "cph2", "sl2")
    g.chain("sl2", "cc"); g.chain("cc", "ap")
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
    er.chain("entry", "se", "hv", "sl")
    ku = G(); ku.get("ged", "Editing"); ku.branch("be", "@ged.Editing")
    ku.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"})
    ku.call("ent", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Enter"}); ku.branch("ben", "@ent.ReturnValue")
    ku.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Escape"}); ku.branch("bes", "@esc.ReturnValue")
    ku.get("ge", "NameEdit"); ku.call("gt", E_EDIT, "GetText", inp={"self": "@ge.NameEdit"}); ku.call("t2s", K_TXT, "Conv_TextToString", inp={"InText": "@gt.ReturnValue"})
    ku.get("gm", "Manager"); ku.get("gi", "Index"); ku.call("sn", MGR, "Set Look Name", inp={"self": "@gm.Manager", "index": "@gi.Index", "name": "@t2s.ReturnValue"})
    ku.n("er", "call_self", function="End Rename")
    ku.call("h", K_WBL, "Handled"); ku.link("h.ReturnValue", "return.ReturnValue")
    ku.n("r2", "return_new"); ku.call("u", K_WBL, "Unhandled"); ku.link("u.ReturnValue", "r2.ReturnValue")
    ku.chain("entry", "be", "ben", "sn", "return"); ku.chain("ben:else", "bes", "er", "return"); ku.chain("bes:else", "return"); ku.chain("be:else", "r2")
    tk = rename_tick()
    return blueprint(W_LOOK, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Index", "int"), var("Editing", "bool")] + hv,
                     functions=[init, tile_colors(("Label", "ColText"), ("Plus", "ColText"), ("NoPhoto", "ColTextDim")), mouse_down_override("On Look Clicked", "On Look Context", "Index", pin="index"),
                                fn("Begin Rename", [param("current", "string")], graph=br), fn("End Rename", graph=er),
                                fn("OnKeyUp", override=True, graph=ku), fn("Tick", override=True, graph=tk)] + hf, event_graph=eg, widget_tree=tree, defaults=HAND)


# ---------------- W_TextButton (text link: click -> Manager.On Menu Action(action)) ----------------
def w_text_button():
    tree = w(E_BORDER, "Fill", props={"BrushColor": COL_NONE, "Padding": "(Left=%d,Top=%d,Right=%d,Bottom=%d)" % (sz(6), sz(2), sz(6), sz(2))},
             children=[w(U_HBOX, "HB", children=[
                 w(U_SIZE, "IconBox", props={"bOverride_WidthOverride": True, "WidthOverride": sz(20), "bOverride_HeightOverride": True, "HeightOverride": sz(20), "Visibility": "Collapsed"},
                   slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(5)}, children=[w(E_IMAGE, "Icon", props={"ColorAndOpacity": "(R=0.62,G=0.76,B=1.0,A=1)"})]),
                 text("Label", "Link", 12, COL_LINK, slot={"VerticalAlignment": "VAlign_Center"})])])
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
    g.chain("entry", "sa", "sb")
    eg = G()
    eg.event("en", E_USERWIDGET, "OnMouseEnter"); eg.get("gi1", "Icon"); eg.call("c1", E_IMAGE, "SetColorAndOpacity", inp={"self": "@gi1.Icon", "InColorAndOpacity": "(R=1,G=1,B=1,A=1)"}); eg.chain("en", "c1")
    eg.event("lv", E_USERWIDGET, "OnMouseLeave"); eg.get("gi2", "Icon"); eg.call("c2", E_IMAGE, "SetColorAndOpacity", inp={"self": "@gi2.Icon", "InColorAndOpacity": "(R=1,G=1,B=1,A=0.75)"}); eg.chain("lv", "c2")
    md = G(); md.get("gm", "Manager"); md.get("ga", "Action")
    md.call("c", MGR, "On Menu Action", inp={"self": "@gm.Manager", "name": "@ga.Action"})
    md.call("h", K_WBL, "Handled"); md.link("h.ReturnValue", "return.ReturnValue"); md.chain("entry", "c", "return")
    return blueprint(W_ROUND, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("Action", "name")],
                     functions=[fn("Init", [param("action", "name"), param("icon", "object:" + E_TEX2D)], graph=g), fn("OnMouseButtonDown", override=True, graph=md)],
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


def w_context_menu():
    tree = roundbox("Frame", COL_CHIP_FRAME, 1, children=[roundbox("Bg", "(R=0.05,G=0.05,B=0.06,A=0.98)", 3, children=[w(U_VBOX, "Rows")])])
    c = G(); c.get("g", "Rows"); c.call("cl", U_PANELW, "ClearChildren", inp={"self": "@g.Rows"}); c.chain("entry", "cl")
    a = G(); a.get("g", "Rows"); a.call("ad", U_VBOX, "AddChildToVerticalBox", inp={"self": "@g.Rows", "Content": "@entry.widget"}); a.chain("entry", "ad")
    cc = G(); tail = ["entry"]; brush(cc, "sf", "Frame", mcol(cc, "cf", "ColChipFrame"), tail); brush(cc, "sb", "Bg", mcol(cc, "cb", "ColMenuBg"), tail); cc.chain(*tail)
    return blueprint(W_MENU, E_USERWIDGET, variables=[var("Manager", "object:" + MGR)],
                     functions=[fn("Clear Rows", graph=c), fn("Add Row", [param("widget", "object:" + E_WIDGET)], graph=a), compute_fn(cc)], widget_tree=tree)


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


# ---------------- W_AltUI (Panel) ----------------
BODY_ROWS = [("Breast", "Breast"), ("Waist", "Waist")]   # the game has no hip morph (Makeup_Save.Hip is an unused remnant)
OPTION_ROWS = [("Scroll", "Scroll speed"), ("Scale", "Tile size"), ("Fov", "Camera FOV (Jodi view)"), ("Dist", "Camera distance (Jodi view)"), ("GroupLen", "Group names: max. characters"), ("ChipH", "Group chip area: max. height"),
               ("BgAlpha", "Background opacity"), ("TileAlpha", "Tile opacity")]   # sliders of Get/Set Option Values (the last two sit in the theme block)
PANEL_TEXTS = [("search", "Search"), ("onlyowned", "LblOwned"), ("onlyfav", "LblFav"), ("onlyvanilla", "LblVanilla"), ("favorites", "FavHeader"), ("all", "AllHeader"), ("listhint", "ListHint"),
               ("worn", "BagWornHeader"), ("inbag", "BagListHeader"), ("bagempty", "BagEmpty"), ("breast", "LblBreast"), ("waist", "LblWaist"),
               ("scroll", "LblScroll"), ("scale", "LblScale"), ("fov", "LblFov"), ("dist", "LblDist"), ("grouplen", "LblGroupLen"), ("chiph", "LblChipH"), ("unlimited", "LblUnlimited"), ("layout", "LblLayout"),
               ("language", "LblLanguage"), ("placeholder", "PlaceholderText"), ("pan", "LblPan"), ("nude", "LblNude"),
               ("theme", "LblTheme"), ("bgalpha", "LblBgAlpha"), ("tilealpha", "LblTileAlpha"), ("key", "LblKey")]   # parameter of Set Strings -> widget name (order = gen_manager_ui.PANEL_STRINGS)
THEME_COLS = 5   # theme grid: fixed columns (entries fill column-wise), the wrap box wraps whole columns on narrow panels
THEME_REFRESH = [("TopTabs", W_TOP), ("LayoutChips", W_SUB), ("LangChips", W_SUB), ("KeyChips", W_SUB), ("ThemeLinks", W_TXT), ("StatusLinks", W_TXT)] + [("ThemeCol%d" % i, W_SWATCH) for i in range(THEME_COLS)]
SUBTABS_MAX_H, SUBTABS_MAX_H_MAX = 112, 500   # default ~3.5 chip rows (80 showed 2.5); option range (unscaled units, x SC at runtime)
SCROLL_PAGES = ["LeftScroll", "SubTabsScroll", "ListScroll", "OutfitScroll", "LooksScroll", "ContentScroll", "BagScroll", "HairScroll", "LookCatScroll", "LookScroll", "OptionsScroll"]
# panel-owned texts coloured by Apply Theme: widget -> derived colour
PANEL_TEXT_COLORS = {"ColHead": ["BagWornHeader", "BagListHeader", "FavHeader", "LblTheme", "ContentTitle"],
                     "ColTextDim": ["AllHeader", "ListHint", "BagEmpty", "PlaceholderText"] + ["Val" + k for k, _ in OPTION_ROWS] + ["Val" + k for k, _ in BODY_ROWS],
                     "ColText": ["LblOwned", "LblFav", "LblVanilla", "LblUnlimited", "LblPan", "LblNude", "LblLayout", "LblLanguage", "LblKey"] + ["Lbl" + k for k, _ in OPTION_ROWS] + ["Lbl" + k for k, _ in BODY_ROWS]}


def body_row(key, caption, lbl_w=120):
    return w(U_HBOX, "Row" + key, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(6), sz(6))}, children=[
        sizebox("Lbl%sBox" % key, lbl_w, 24, [text("Lbl" + key, caption, 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Center"}),
        sizebox("Sld%sBox" % key, 420, 24, [w(E_SLIDER, "Sld" + key, props={"Value": 0.5, "StepSize": 0.01, "SliderBarColor": "(R=0.35,G=0.42,B=0.55,A=1)", "SliderHandleColor": "(R=1,G=1,B=1,A=1)",
                                              "WidgetStyle": "(BarThickness=5.0)"})],   # the engine default of 2 px drops below 1 px at panel scale ~0.4 and is not rasterised on some rows
                slot={"VerticalAlignment": "VAlign_Center"}),
        sizebox("Val%sBox" % key, 70, 24, [text("Val" + key, "50 %", 12, GREY, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(10)}),
    ])


def round_btn(name, top):
    return w(W_ROUND, name, props={"Visibility": "Collapsed"},
             slot={"LayoutData": "(Anchors=(Minimum=(X=0,Y=1),Maximum=(X=0,Y=1)),Offsets=(Left=%d,Top=%d,Right=%d,Bottom=%d),Alignment=(X=1,Y=1))" % (-sz(10.5), -top, BTN_R, BTN_R), "ZOrder": 5})


def w_panel():
    tree = w(U_CANVAS, "Root", children=[
        round_btn("BtnPlus", sz(10.5) + BTN_R + sz(5)), round_btn("BtnMinus", sz(10.5)),
        w(E_BORDER, "Bg", props={"BrushColor": COL_BG, "Padding": "(Left=46,Top=30,Right=46,Bottom=46)"}, slot=FULL, children=[
          w(U_VBOX, "Main", children=[
            w(U_HBOX, "TopTabs", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(10)}),
            w(U_SCROLL, "OutfitScroll", props={"Visibility": "Collapsed", "WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_WRAP, "OutfitList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)})]),
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
                w(U_WRAP, "HairList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)})])]),
            # Appearance: categories on the left, tiles on the right
            w(U_HBOX, "LookHB", props={"Visibility": "Collapsed"}, slot=FILL, children=[
                sizebox("LookLeftSize", 300, 100, [w(U_SCROLL, "LookCatScroll", props={"WheelScrollMultiplier": 2.0}, children=[w(U_VBOX, "LookCats")])],
                        slot={"Size": "(SizeRule=Automatic)", "VerticalAlignment": "VAlign_Fill", "Padding": "(Left=0,Top=0,Right=30,Bottom=0)"}),
                w(U_SCROLL, "LookScroll", props={"WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_WRAP, "LookList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)})])]),
            # Body Shape: body chips (Standard + body mods) above the sliders
            w(U_VBOX, "BodyBox", props={"Visibility": "Collapsed"}, slot=FILL, children=[
                w(U_WRAP, "BodyChips", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(4) + 1, sz(4) + 1)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(14)})] +
              [body_row(k, cap) for k, cap in BODY_ROWS]),
            # Options: sliders (scroll speed, tile size, camera), checks, chips, theme block (scrollable: the theme block makes the page tall)
            w(U_SCROLL, "OptionsScroll", props={"Visibility": "Collapsed", "WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "OptionsBox", children=[body_row(k, cap, 330) for k, cap in OPTION_ROWS[:6]] + [
                w(U_HBOX, "RowUnlimited", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    w(E_CHECK, "OptUnlimited", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblUnlimited", "show unlimited items at once", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowPan", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    w(E_CHECK, "OptPan", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblPan", "Camera follows slot / face", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowNude", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    w(E_CHECK, "OptNude", props={"WidgetStyle": check_style(CHECK_SIZE)}, slot={"VerticalAlignment": "VAlign_Center", "Padding": "(Left=0,Top=0,Right=%d,Bottom=0)" % sz(8)}),
                    text("LblNude", "Underwear may be taken off", 13, slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowLayout", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    sizebox("LblLayoutBox", 330, 24, [text("LblLayout", "Space for Jodi", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Center"}),
                    w(U_HBOX, "LayoutChips", slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowLanguage", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    sizebox("LblLanguageBox", 330, 24, [text("LblLanguage", "Language", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Center"}),
                    w(U_HBOX, "LangChips", slot={"VerticalAlignment": "VAlign_Center"})]),
                w(U_HBOX, "RowKey", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(10), sz(6))}, children=[
                    sizebox("LblKeyBox", 330, 24, [text("LblKey", "Panel key", 13, slot={"VerticalAlignment": "VAlign_Center"})], slot={"VerticalAlignment": "VAlign_Center"}),
                    w(U_HBOX, "KeyChips", slot={"VerticalAlignment": "VAlign_Center"})]),
                # theme: heading, swatch grid (W_ColorSwatch per base colour), opacity sliders, reset link
                text("LblTheme", "Colours", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=%d)" % (sz(16), sz(6))}),
                w(U_WRAP, "ThemeGrid", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(10) + 1, sz(6) + 1)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(18)},
                  children=[w(U_VBOX, "ThemeCol%d" % i) for i in range(THEME_COLS)])] +
                [body_row(k, cap, 330) for k, cap in OPTION_ROWS[6:]] + [
                w(U_HBOX, "ThemeLinks", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(16)})])]),
            w(U_SCROLL, "BagScroll", props={"Visibility": "Collapsed", "WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "BagVB", children=[
                text("BagWornHeader", "Worn", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(6)}),
                w(U_WRAP, "BagWorn", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(14)}),
                w(U_HBOX, "BagListHead", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=%d)" % sz(6)}, children=[
                    text("BagListHeader", "In backpack", 14, "(SpecifiedColor=(R=0.85,G=0.75,B=0.4,A=1))", slot={"VerticalAlignment": "VAlign_Center"}),
                    w(U_HBOX, "BagLinks", slot={"Padding": "(Left=%d,Top=0,Right=0,Bottom=0)" % sz(12), "VerticalAlignment": "VAlign_Center"})]),
                w(U_WRAP, "BagList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)}),
                text("BagEmpty", "Backpack is empty", 11, GREY)])]),
            w(U_HBOX, "HB", slot=FILL, children=[
                sizebox("LeftSize", 340, 100, [w(U_SCROLL, "LeftScroll", props={"WheelScrollMultiplier": 2.0}, children=[w(U_VBOX, "LeftBox")])],
                        slot={"Size": "(SizeRule=Automatic)", "VerticalAlignment": "VAlign_Fill", "Padding": "(Left=0,Top=0,Right=30,Bottom=0)"}),
                w(U_VBOX, "RightBox", slot=FILL, children=[
                    # group chips: at most ~3 rows, then the box scrolls (one tab per mod gets long)
                    w(U_SIZE, "SubTabsBox", props={"bOverride_MaxDesiredHeight": True, "MaxDesiredHeight": sz(SUBTABS_MAX_H)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=15)"}, children=[
                        w(U_SCROLL, "SubTabsScroll", props={"WheelScrollMultiplier": 2.0}, children=[
                            w(U_WRAP, "SubTabs", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(4) + 1, sz(4) + 1)})])]),
                    w(U_HBOX, "Filters", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=15)"}, children=[
                        roundbox("SearchFrame", COL_CHIP_FRAME, 1, slot=FILL, children=[roundbox("SearchFill", COL_CHIP, 0, children=[w(U_HBOX, "SearchHB", children=[
                            w(E_EDIT, "Search", props={"HintText": "Search...", "WidgetStyle": "(Font=(Size=%d),Padding=(Left=%d,Top=%d,Right=%d,Bottom=%d),BackgroundColor=(SpecifiedColor=(R=0,G=0,B=0,A=0)),ForegroundColor=(SpecifiedColor=(R=1,G=1,B=1,A=1)))" % (sz(SEARCH_FONT), sz(10), sz(SEARCH_PAD), sz(10), sz(SEARCH_PAD))}, slot=FILL),
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
                    ]),
                    w(U_SCROLL, "ListScroll", props={"WheelScrollMultiplier": 2.0}, slot=FILL, children=[w(U_VBOX, "ListVB", children=[
                        text("FavHeader", "Favourites", 13, "(SpecifiedColor=(R=0.95,G=0.8,B=0.3,A=1))", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=8)"}),
                        w(U_WRAP, "FavList", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)}, slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=23)"}),
                        text("AllHeader", "All", 13, "(SpecifiedColor=(R=0.7,G=0.7,B=0.7,A=1))", slot={"Padding": "(Left=0,Top=0,Right=0,Bottom=8)"}),
                        w(U_WRAP, "List", props={"InnerSlotPadding": "(X=%d,Y=%d)" % (sz(6) + 1, sz(6) + 1)}),
                        text("ListHint", "Only the first 400 matches are shown - please narrow the search.", 11, GREY, slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(8)})])]),
                ]),
            ]),
            w(U_VBOX, "StatusBar", slot={"Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(8)}, children=[
                w(U_SIZE, "StatusLineBox", props={"bOverride_HeightOverride": True, "HeightOverride": 1}, children=[w(E_BORDER, "StatusLine", props={"BrushColor": "(R=1,G=1,B=1,A=0.35)", "Padding": "(Left=0,Top=0,Right=0,Bottom=0)"})]),
                w(U_HBOX, "StatusLinks", slot={"HorizontalAlignment": "HAlign_Center", "Padding": "(Left=0,Top=%d,Right=0,Bottom=0)" % sz(6)})]),
            ])])])
    # small helper functions for the manager
    def clear(name, box):
        g = G(); g.get("g", box); g.call("c", U_PANELW, "ClearChildren", inp={"self": "@g." + box}); g.chain("entry", "c"); return fn(name, graph=g)
    def add(name, box, cls, func):
        g = G(); g.get("g", box); g.call("a", cls, func, inp={"self": "@g." + box, "Content": "@entry.widget"}); g.chain("entry", "a")
        return fn(name, [param("widget", "object:" + E_WIDGET)], graph=g)
    gs = G(); gs.get("g", "Search"); gs.call("t", E_EDIT, "GetText", inp={"self": "@g.Search"}); gs.link("t.ReturnValue", "return.text")
    go = G(); go.get("g", "OnlyOwned"); go.call("c", E_CHECK, "IsChecked", inp={"self": "@g.OnlyOwned"}); go.link("c.ReturnValue", "return.yes")
    gf = G(); gf.get("g", "OnlyFav"); gf.call("c", E_CHECK, "IsChecked", inp={"self": "@g.OnlyFav"}); gf.link("c.ReturnValue", "return.yes")
    gv = G(); gv.get("g", "OnlyVanilla"); gv.call("c", E_CHECK, "IsChecked", inp={"self": "@g.OnlyVanilla"}); gv.link("c.ReturnValue", "return.yes")
    # keyboard: game actions (Esc, HideUI=Backspace, Inventory=Tab, Screenshot=F9) are bound to IE_Released in the controller.
    # Hence: swallow all key-downs AND key-ups while the panel is open; close only on key-up (Esc / K),
    # so no release slips through to the game. K does not close while the search field has focus (typing).
    kd = G(); kd.call("h", K_WBL, "Handled"); kd.link("h.ReturnValue", "return.ReturnValue"); kd.chain("entry", "return")
    # OnPreviewKeyDown (tunnel, before the text field): swallow Escape (the text field must not react)
    pk = G()
    pk.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"})
    pk.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Escape"}); pk.branch("b", "@esc.ReturnValue")
    pk.call("h", K_WBL, "Handled"); pk.link("h.ReturnValue", "return.ReturnValue")
    pk.n("r2", "return_new"); pk.call("u", K_WBL, "Unhandled"); pk.link("u.ReturnValue", "r2.ReturnValue")
    pk.chain("entry", "b", "return"); pk.chain("b:else", "r2")
    # OnKeyUp: search -> Manager.On Search Changed(text); Esc or the panel key (without search focus) -> Close Panel; always Handled
    ku = G()
    ku.get("gs", "Search"); ku.call("t", E_EDIT, "GetText", inp={"self": "@gs.Search"})
    ku.get("gm", "Manager"); ku.call("sc", MGR, "On Search Changed", inp={"self": "@gm.Manager", "text": "@t.ReturnValue"})
    ku.call("key", K_IN, "GetKey", inp={"Input": "@entry.InKeyEvent"})
    ku.call("esc", K_IN, "EqualEqual_KeyKey", inp={"A": "@key.ReturnValue", "B": "Escape"})
    ku.call("kdn", K_IN, "Key_GetDisplayName", inp={"Key": "@key.ReturnValue"}); ku.call("kds", K_TXT, "Conv_TextToString", inp={"InText": "@kdn.ReturnValue"})
    ku.get("gmk", "Manager"); ku.get("gtk", "ToggleKey", cls=MGR); ku.link("gmk.Manager", "gtk.self"); ku.call("tks", K_STR, "Conv_NameToString", inp={"InName": "@gtk.ToggleKey"})
    ku.call("kk", K_STR, "EqualEqual_StriStri", inp={"A": "@kds.ReturnValue", "B": "@tks.ReturnValue"})
    ku.get("gs2", "Search"); ku.call("hf", E_WIDGET, "HasKeyboardFocus", inp={"self": "@gs2.Search"})
    ku.call("nf", K_MATH, "Not_PreBool", inp={"A": "@hf.ReturnValue"})
    ku.call("kx", K_MATH, "BooleanAND", inp={"A": "@kk.ReturnValue", "B": "@nf.ReturnValue"})
    ku.call("or", K_MATH, "BooleanOR", inp={"A": "@esc.ReturnValue", "B": "@kx.ReturnValue"}); ku.branch("b", "@or.ReturnValue")
    ku.get("gm2", "Manager"); ku.call("cl", MGR, "Close Panel", inp={"self": "@gm2.Manager"})
    ku.call("h", K_WBL, "Handled"); ku.link("h.ReturnValue", "return.ReturnValue")
    ku.chain("entry", "sc", "b", "cl", "return"); ku.chain("b:else", "return")
    # SetVisibility expects ESlateVisibility: via two branch paths (Visible / Collapsed)
    fv2 = G(); fv2.branch("b", "@entry.visible")
    for i, wn in enumerate(["FavHeader", "FavList", "AllHeader"]):
        fv2.get("g%d" % i, wn); fv2.call("v%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@g%d.%s" % (i, wn), "InVisibility": "Visible"})
        fv2.get("h%d" % i, wn); fv2.call("c%d" % i, E_WIDGET, "SetVisibility", inp={"self": "@h%d.%s" % (i, wn), "InVisibility": "Collapsed"})
    fv2.chain("entry", "b", "v0", "v1", "v2"); fv2.chain("b:else", "c0", "c1", "c2")
    # panel click (no child handled the click): close the context menu
    pm = G(); pm.get("gm", "Manager"); pm.call("cm", MGR, "Close Menu", inp={"self": "@gm.Manager"})
    pm.call("u", K_WBL, "Unhandled"); pm.link("u.ReturnValue", "return.ReturnValue"); pm.chain("entry", "cm", "return")
    # Set Page(page): exactly one page visible (Clothes = HB, Outfits = OutfitScroll, Bag = BagScroll)
    sp = G(); pages = [("HB", "Clothes"), ("OutfitScroll", "Outfits"), ("LooksScroll", "Looks"), ("BagScroll", "Bag"), ("HairScroll", "Hair"), ("LookHB", "Look"), ("BodyBox", "Body"), ("OptionsScroll", "Options"), ("ContentBox", "Content")]
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
    # read / set the body sliders (values 0..1, displayed as percent)
    gb = G()
    for k, _ in BODY_ROWS:
        gb.get("g" + k, "Sld" + k); gb.call("v" + k, E_SLIDER, "GetValue", inp={"self": "@g%s.Sld%s" % (k, k)}); gb.link("v%s.ReturnValue" % k, "return." + k.lower())
    gb.chain("entry", "return")
    sb = G(); tail = ["entry"]
    for k, _ in BODY_ROWS:
        sb.get("g" + k, "Sld" + k); sb.call("s" + k, E_SLIDER, "SetValue", inp={"self": "@g%s.Sld%s" % (k, k), "InValue": "@entry." + k.lower()}); tail.append("s" + k)
        sb.call("m" + k, K_MATH, "Multiply_FloatFloat", inp={"A": "@entry." + k.lower(), "B": "100.0"}); sb.call("r" + k, K_MATH, "Round", inp={"A": "@m%s.ReturnValue" % k})
        sb.call("i" + k, K_STR, "Conv_IntToString", inp={"InInt": "@r%s.ReturnValue" % k}); sb.call("c" + k, K_STR, "Concat_StrStr", inp={"A": "@i%s.ReturnValue" % k, "B": " %"})
        sb.call("t" + k, K_TXT, "Conv_StringToText", inp={"InString": "@c%s.ReturnValue" % k})
        sb.get("gv" + k, "Val" + k); sb.call("st" + k, E_TEXT, "SetText", inp={"self": "@gv%s.Val%s" % (k, k), "InText": "@t%s.ReturnValue" % k}); tail.append("st" + k)
    sb.chain(*tail)
    # read / set the option sliders (0..1; display computed by the manager)
    gov = G()
    for k, _ in OPTION_ROWS:
        gov.get("g" + k, "Sld" + k); gov.call("v" + k, E_SLIDER, "GetValue", inp={"self": "@g%s.Sld%s" % (k, k)}); gov.link("v%s.ReturnValue" % k, "return." + k.lower())
    gov.get("gu", "OptUnlimited"); gov.call("vu", E_CHECK, "IsChecked", inp={"self": "@gu.OptUnlimited"}); gov.link("vu.ReturnValue", "return.unlimited")
    gov.get("gpn", "OptPan"); gov.call("vp", E_CHECK, "IsChecked", inp={"self": "@gpn.OptPan"}); gov.link("vp.ReturnValue", "return.pan")
    gov.get("gnd", "OptNude"); gov.call("vn", E_CHECK, "IsChecked", inp={"self": "@gnd.OptNude"}); gov.link("vn.ReturnValue", "return.nude")
    gov.chain("entry", "return")
    # static texts (language): search field hint + labels
    sst = G(); tail = ["entry"]
    for p, widget in PANEL_TEXTS:
        sst.get("g" + p, widget)
        if widget == "Search":
            sst.call("s" + p, E_EDIT, "SetHintText", inp={"self": "@g%s.%s" % (p, widget), "InText": "@entry." + p})
        else:
            sst.call("s" + p, E_TEXT, "SetText", inp={"self": "@g%s.%s" % (p, widget), "InText": "@entry." + p})
        tail.append("s" + p)
    sst.chain(*tail)
    su = G(); su.get("g", "OptUnlimited"); su.call("s", E_CHECK, "SetIsChecked", inp={"self": "@g.OptUnlimited", "InIsChecked": "@entry.unlimited"})
    su.get("g2", "OptPan"); su.call("s2", E_CHECK, "SetIsChecked", inp={"self": "@g2.OptPan", "InIsChecked": "@entry.pan"})
    su.get("g3", "OptNude"); su.call("s3", E_CHECK, "SetIsChecked", inp={"self": "@g3.OptNude", "InIsChecked": "@entry.nude"}); su.chain("entry", "s", "s2", "s3")
    # keep the left side of the panel free: anchor of the background border (Minimum.X = fraction)
    la = G(); la.get("g", "Bg"); la.call("sl", "/Script/UMG.WidgetLayoutLibrary", "SlotAsCanvasSlot", inp={"Widget": "@g.Bg"})
    la.call("mk", K_MATH, "MakeVector2D", inp={"X": "@entry.fraction", "Y": "0.0"})
    la.make("an", "/Script/Slate.Anchors", Minimum="@mk.ReturnValue", Maximum="(X=1,Y=1)")
    la.call("sa", "/Script/UMG.CanvasPanelSlot", "SetAnchors", inp={"self": "@sl.ReturnValue", "InAnchors": "@an.Anchors"})
    # +/- buttons: anchored at the edge of the free area, visible only when a free area exists
    la.call("mk2", K_MATH, "MakeVector2D", inp={"X": "@entry.fraction", "Y": "1.0"}); la.make("an2", "/Script/Slate.Anchors", Minimum="@mk2.ReturnValue", Maximum="@mk2.ReturnValue")
    la.call("gt0", K_MATH, "Greater_FloatFloat", inp={"A": "@entry.fraction", "B": "0.0"}); la.branch("bv", "@gt0.ReturnValue")
    tail = ["sa"]; on = ["bv"]; off = ["bv:else"]
    for b in ("BtnPlus", "BtnMinus"):
        la.get("g" + b, b); la.call("sl" + b, "/Script/UMG.WidgetLayoutLibrary", "SlotAsCanvasSlot", inp={"Widget": "@g%s.%s" % (b, b)})
        la.call("sa" + b, "/Script/UMG.CanvasPanelSlot", "SetAnchors", inp={"self": "@sl%s.ReturnValue" % b, "InAnchors": "@an2.Anchors"}); tail.append("sa" + b)
        la.get("h" + b, b); la.call("sv" + b, E_WIDGET, "SetVisibility", inp={"self": "@h%s.%s" % (b, b), "InVisibility": "Visible"}); on.append("sv" + b)
        la.get("k" + b, b); la.call("sc" + b, E_WIDGET, "SetVisibility", inp={"self": "@k%s.%s" % (b, b), "InVisibility": "Collapsed"}); off.append("sc" + b)
    la.chain("entry", *tail, "bv"); la.chain(*on); la.chain(*off)
    # +/- round buttons: pass the manager through, set action + icon (tree instances otherwise never get an init)
    ib = G(); tail = ["entry"]
    for b, action, tex in (("BtnPlus", "DistPlus", T_PLUS), ("BtnMinus", "DistMinus", T_MINUS)):
        ib.get("g" + b, b); ib.get("m" + b, "Manager"); ib.n("s" + b, "set", var="Manager", cls=W_ROUND, inp={"self": "@g%s.%s" % (b, b), "Manager": "@m%s.Manager" % b})
        ib.get("h" + b, b); ib.call("i" + b, W_ROUND, "Init", inp={"self": "@h%s.%s" % (b, b), "action": action, "icon": tex}); tail += ["s" + b, "i" + b]
    ib.chain(*tail)
    sov = G(); tail = ["entry"]
    for k, _ in OPTION_ROWS:
        sov.get("g" + k, "Sld" + k); sov.call("s" + k, E_SLIDER, "SetValue", inp={"self": "@g%s.Sld%s" % (k, k), "InValue": "@entry." + k.lower()}); tail.append("s" + k)
        sov.get("gv" + k, "Val" + k); sov.call("st" + k, E_TEXT, "SetText", inp={"self": "@gv%s.Val%s" % (k, k), "InText": "@entry." + k.lower() + " text"}); tail.append("st" + k)
    sov.chain(*tail)
    # max height of the group chip area (option; unscaled units -> x SC)
    sth = G(); sth.call("m", K_MATH, "Multiply_FloatFloat", inp={"A": "@entry.height", "B": str(SC)})
    sth.get("gb", "SubTabsBox"); sth.call("s", U_SIZE, "SetMaxDesiredHeight", inp={"self": "@gb.SubTabsBox", "InMaxDesiredHeight": "@m.ReturnValue"}); sth.chain("entry", "s")
    # scroll multiplier for all scroll areas
    sm = G(); tail = ["entry"]
    for i, wn in enumerate(SCROLL_PAGES):
        sm.get("g%d" % i, wn); sm.call("s%d" % i, U_SCROLL, "SetWheelScrollMultiplier", inp={"self": "@g%d.%s" % (i, wn), "NewWheelScrollMultiplier": "@entry.mult"}); tail.append("s%d" % i)
    sm.chain(*tail)
    # bring the checkbox boxes to the actual height of the search field (Tick; only sets on change)
    cs2 = G(); cs2.get("gsf", "SearchFrame"); cs2.call("ds", E_WIDGET, "GetDesiredSize", inp={"self": "@gsf.SearchFrame"}); cs2.call("bv", K_MATH, "BreakVector2D", inp={"InVec": "@ds.ReturnValue"})
    cs2.get("gcs", "CheckSize"); cs2.call("ne0", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@bv.Y", "B": "@gcs.CheckSize", "ErrorTolerance": "0.5"}); cs2.call("ne", K_MATH, "Not_PreBool", inp={"A": "@ne0.ReturnValue"})
    cs2.call("gt", K_MATH, "Greater_FloatFloat", inp={"A": "@bv.Y", "B": "1.0"}); cs2.call("and", K_MATH, "BooleanAND", inp={"A": "@ne.ReturnValue", "B": "@gt.ReturnValue"}); cs2.branch("b", "@and.ReturnValue")
    cs2.set("scs", "CheckSize", inp={"CheckSize": "@bv.Y"}); tail = ["entry", "b", "scs"]
    for i, wn in enumerate(["OwnedBox", "FavBox"]):
        cs2.get("g%d" % i, wn); cs2.call("w%d" % i, U_SIZE, "SetWidthOverride", inp={"self": "@g%d.%s" % (i, wn), "InWidthOverride": "@bv.Y"})
        cs2.get("h%d" % i, wn); cs2.call("hh%d" % i, U_SIZE, "SetHeightOverride", inp={"self": "@h%d.%s" % (i, wn), "InHeightOverride": "@bv.Y"}); tail += ["w%d" % i, "hh%d" % i]
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
    ft.get("g3", "OnlyVanilla"); ft.call("c3", E_CHECK, "SetIsChecked", inp={"self": "@g3.OnlyVanilla", "InIsChecked": "@entry.vanilla"}); ft.chain("entry", "c1", "c2", "c3")
    # Apply Theme: panel-owned parts from Manager.Col* (background, status line, search box, headings, labels, slider bars)
    at = G(); tail = ["entry"]
    brush(at, "sbg", "Bg", mcol(at, "cbg", "ColBg"), tail); brush(at, "ssl", "StatusLine", mcol(at, "csl", "ColStatusLine"), tail)
    brush(at, "ssf", "SearchFrame", mcol(at, "csf", "ColChipFrame"), tail); brush(at, "ssi", "SearchFill", mcol(at, "csi", "ColChip"), tail)
    for col, names in PANEL_TEXT_COLORS.items():
        pin = mcol(at, "c_" + col, col)
        for wn in names: text_color(at, "t_" + wn, wn, pin, tail)
    sld = mcol(at, "c_slider", "ColSlider")
    for k, _ in OPTION_ROWS + BODY_ROWS:
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
    ct = G(); ct.get("g", "ContentTitle"); ct.call("s", E_TEXT, "SetText", inp={"self": "@g.ContentTitle", "InText": "@entry.text"}); ct.chain("entry", "s")
    si = G(); prev = "entry"
    for i, (page, box) in enumerate([("Clothes", "ListScroll"), ("Hair", "HairScroll"), ("Look", "LookScroll")]):
        si.call("e%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@entry.page", "B": page}); si.branch("b%d" % i, "@e%d.ReturnValue" % i)
        si.get("g%d" % i, box); si.call("s%d" % i, U_SCROLL, "ScrollWidgetIntoView", inp={"self": "@g%d.%s" % (i, box), "WidgetToFind": "@entry.widget", "AnimateScroll": "false", "ScrollDestination": "Center"})
        si.chain(prev, "b%d" % i, "s%d" % i); prev = "b%d:else" % i
    funcs = [clear("Clear Left", "LeftBox"), add("Add Left", "LeftBox", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Content", "ContentList"), add("Add Content Section", "ContentList", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Content Links", "ContentLinks"), add("Add Content Link", "ContentLinks", U_HBOX, "AddChildToHorizontalBox"),
             fn("Set Content Title", [param("text", "text")], graph=ct), fn("Scroll Into View", [param("page", "name"), param("widget", "object:" + E_WIDGET)], graph=si),
             fn("Apply Theme", graph=at), fn("Clear Theme Swatches", graph=cts), fn("Add Theme Swatch", [param("widget", "object:" + E_WIDGET), param("column", "int")], graph=ats),
             clear("Clear Theme Links", "ThemeLinks"), add("Add Theme Link", "ThemeLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear TopTabs", "TopTabs"), add("Add TopTab", "TopTabs", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Outfits", "OutfitList"), add("Add Outfit", "OutfitList", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Look Tiles", "LooksList"), add("Add Look Tile", "LooksList", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Bag Worn", "BagWorn"), add("Add Bag Worn", "BagWorn", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Bag List", "BagList"), add("Add Bag Item", "BagList", U_WRAP, "AddChildToWrapBox"),
             fn("Set Page", [param("page", "name")], graph=sp), fn("Set Bag Empty", [param("visible", "bool")], graph=be),
             fn("Clear Search", graph=cs), fn("Set List Hint", [param("visible", "bool")], graph=lh), fn("Sync Check Size", graph=cs2),
             clear("Clear Bag Links", "BagLinks"), add("Add Bag Link", "BagLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Search Links", "SearchLinks"), add("Add Search Link", "SearchLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Hair Links", "HairLinks"), add("Add Hair Link", "HairLinks", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Hair", "HairList"), add("Add Hair", "HairList", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Look Cats", "LookCats"), add("Add Look Cat", "LookCats", U_VBOX, "AddChildToVerticalBox"),
             clear("Clear Look", "LookList"), add("Add Look", "LookList", U_WRAP, "AddChildToWrapBox"),
             fn("Get Option Values", outputs=[param(k.lower(), "float") for k, _ in OPTION_ROWS] + [param("unlimited", "bool"), param("pan", "bool"), param("nude", "bool")], graph=gov),
             fn("Set Option Checks", [param("unlimited", "bool"), param("pan", "bool"), param("nude", "bool")], graph=su), fn("Set Left Free", [param("fraction", "float")], graph=la),
             clear("Clear Layout Chips", "LayoutChips"), add("Add Layout Chip", "LayoutChips", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Body Chips", "BodyChips"), add("Add Body Chip", "BodyChips", U_WRAP, "AddChildToWrapBox"),
             clear("Clear Lang Chips", "LangChips"), add("Add Lang Chip", "LangChips", U_HBOX, "AddChildToHorizontalBox"),
             clear("Clear Key Chips", "KeyChips"), add("Add Key Chip", "KeyChips", U_HBOX, "AddChildToHorizontalBox"),
             fn("Set Strings", [param(p, "text") for p, _ in PANEL_TEXTS], graph=sst), fn("Init Buttons", graph=ib),
             clear("Clear Status", "StatusLinks"), add("Add Status", "StatusLinks", U_HBOX, "AddChildToHorizontalBox"),
             fn("Set Option Values", [param(k.lower(), "float") for k, _ in OPTION_ROWS] + [param(k.lower() + " text", "text") for k, _ in OPTION_ROWS], graph=sov),
             fn("Set Scroll Mult", [param("mult", "float")], graph=sm),
             fn("Set SubTabs Height", [param("height", "float")], graph=sth),
             fn("Get Body Values", outputs=[param("breast", "float"), param("waist", "float")], graph=gb),
             fn("Set Body Values", [param("breast", "float"), param("waist", "float")], graph=sb),
             clear("Clear Fav", "FavList"), add("Add Fav", "FavList", U_WRAP, "AddChildToWrapBox"),
             fn("Set Fav Visible", [param("visible", "bool")], graph=fv2), fn("OnMouseButtonDown", override=True, graph=pm),
             clear("Clear List", "List"), add("Add Item", "List", U_WRAP, "AddChildToWrapBox"),
             clear("Clear SubTabs", "SubTabs"), add("Add SubTab", "SubTabs", U_WRAP, "AddChildToWrapBox"),
             fn("Get Search", outputs=[param("text", "text")], graph=gs, pure=True),
             fn("Get Only Owned", outputs=[param("yes", "bool")], graph=go, pure=True),
             fn("Get Only Fav", outputs=[param("yes", "bool")], graph=gf, pure=True),
             fn("Get Only Vanilla", outputs=[param("yes", "bool")], graph=gv, pure=True),
             fn("Set Filter Toggles", [param("owned", "bool"), param("fav", "bool"), param("vanilla", "bool")], graph=ft),
             fn("OnKeyDown", override=True, graph=kd), fn("OnKeyUp", override=True, graph=ku), fn("OnPreviewKeyDown", override=True, graph=pk)]
    return blueprint(W_PANEL, E_USERWIDGET, variables=[var("Manager", "object:" + MGR), var("TmpKnown", "bool"), var("CheckSize", "float")], functions=funcs, widget_tree=tree,
                     defaults={"bIsFocusable": "true"})


assets = [w_tooltip(), w_group_header(), w_content_section(), w_slot_tab(), w_clothes_button(), w_sub_tab(), w_top_tab(), w_outfit_button(), w_look_button(), w_text_button(), w_round_button(), w_menu_row(), w_context_menu(), w_color_swatch(), w_panel()]
write(os.path.join(os.path.dirname(__file__), "..", "40_widgets.json"), assets)
