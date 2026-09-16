"""Theme: the 10 base colours (picker, RGB) with their defaults (= the former constants of gen_widgets.py) and the
derived colours the manager computes in `Apply Theme` (widgets read only those: Manager.Col*)."""

# key, default RGB, string key of the caption
THEME = [("Bg", (0.02, 0.02, 0.03), "Theme_Bg"), ("Accent", (0.75, 0.10, 0.10), "Theme_Accent"), ("Fill", (0.02, 0.02, 0.03), "Theme_Fill"),
         ("Frame", (1.0, 1.0, 1.0), "Theme_Frame"), ("Worn", (0.20, 0.80, 0.30), "Theme_Worn"), ("Row", (0.0, 0.0, 0.0), "Theme_Row"),
         ("Text", (1.0, 1.0, 1.0), "Theme_Text"), ("Head", (0.85, 0.75, 0.40), "Theme_Head"), ("Link", (0.62, 0.76, 1.0), "Theme_Link"),
         ("Line", (1.0, 1.0, 1.0), "Theme_Line")]
BG_ALPHA = 0.88; TILE_ALPHA = 1.0

# derived colour variables of the manager: name -> (base key, lighten-to-white t, rgb factor, alpha, alpha scaled by TileAlpha?)
DERIVED = [
    ("ColBg", "Bg", 0, 1, None, False),            # alpha = BgAlpha (special)
    ("ColMenuBg", "Bg", 0, 1, 0.98, False),
    ("ColFill", "Fill", 0, 1, 0.80, True), ("ColFillHover", "Fill", 0.10, 1, 0.85, True),
    ("ColFrameWorn", "Worn", 0, 1, 0.90, False), ("ColFillWorn", "Worn", 0, 0.18, 0.85, True), ("ColFillWornHover", "Worn", 0, 0.30, 0.90, True),
    ("ColFrame", "Frame", 0, 1, 0.35, False), ("ColFrameHover", "Frame", 0, 1, 0.90, False), ("ColFrameLocked", "Frame", 0, 1, 0.12, False),
    ("ColChipFrame", "Frame", 0, 1, 0.25, False), ("ColChipFrameHover", "Frame", 0, 1, 0.70, False),
    ("ColRow", "Row", 0, 1, 0.35, True), ("ColRowHover", "Row", 0.15, 1, 0.40, True), ("ColRowSel", "Row", 0.20, 1, 0.45, True), ("ColRowSelHover", "Row", 0.30, 1, 0.50, True),
    ("ColChip", "Row", 0, 1, 0.55, True), ("ColChipHover", "Row", 0.15, 1, 0.60, True), ("ColChipSel", "Row", 0.20, 1, 0.65, True), ("ColChipSelHover", "Row", 0.30, 1, 0.70, True),
    ("ColLine", "Line", 0, 1, 0.12, False), ("ColStatusLine", "Line", 0, 1, 0.35, False), ("ColMenuHover", "Line", 0, 1, 0.15, False),
    ("ColTopHover", "Line", 0, 1, 0.06, False), ("ColLinkHover", "Line", 0, 1, 0.10, False),
    ("ColText", "Text", 0, 1, 1.0, False), ("ColTextDim", "Text", 0, 0.6, 1.0, False),
    ("ColHead", "Head", 0, 1, 1.0, False), ("ColLink", "Link", 0, 1, 1.0, False), ("ColSlider", "Link", 0, 0.55, 1.0, False), ("ColAccent", "Accent", 0, 1, 1.0, False),
]
DERIVED_NAMES = [d[0] for d in DERIVED]


def rgb_lit(rgb, a=1.0):
    return "(R=%g,G=%g,B=%g,A=%g)" % (rgb[0], rgb[1], rgb[2], a)
