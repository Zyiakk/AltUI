"""Theme: the 10 base colours (picker, RGB) with their defaults (= the former constants of gen_widgets.py) and the
derived colours the manager computes in `Apply Theme` (widgets read only those: Manager.Col*)."""

# key, default RGB, string key of the caption
THEME = [("Bg", (0.02, 0.02, 0.03), "Theme_Bg"), ("Accent", (0.75, 0.10, 0.10), "Theme_Accent"), ("Fill", (0.02, 0.02, 0.03), "Theme_Fill"),
         ("Frame", (1.0, 1.0, 1.0), "Theme_Frame"), ("Worn", (0.20, 0.80, 0.30), "Theme_Worn"), ("Row", (0.0, 0.0, 0.0), "Theme_Row"),
         ("Text", (1.0, 1.0, 1.0), "Theme_Text"), ("Head", (0.85, 0.75, 0.40), "Theme_Head"), ("Link", (0.62, 0.76, 1.0), "Theme_Link"),
         ("Line", (1.0, 1.0, 1.0), "Theme_Line"),
         # 2026-10-19: surfaces that had fixed colours. Appended only: saved themes (S_ThemePreset.Colors) are by index, and a
         # theme or settings file from before has no value for them -> the default (Apply Theme Preset, Load Settings "col0")
         ("Input", (0.10, 0.10, 0.12), "Theme_Input"), ("Area", (1.0, 1.0, 1.0), "Theme_Area"), ("Warn", (1.0, 0.6, 0.3), "Theme_Warn"),
         ("Scroll", (1.0, 1.0, 1.0), "Theme_Scroll")]
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
    # 2026-10-19 (defaults = the former fixed colours): text fields, light areas / zebra rows and their rim, warnings, scroll bars,
    # the dimmed screen behind a dialog, buttons with a surface (Mods tab) and their pressed state, icons at rest, the check box
    # (frame + tick; its fill is ColChip like the search fields)
    ("ColInput", "Input", 0, 1, 1.0, False), ("ColArea", "Area", 0, 1, 0.05, False), ("ColAreaFrame", "Area", 0, 1, 0.16, False),
    ("ColWarn", "Warn", 0, 1, 1.0, False), ("ColScroll", "Scroll", 0, 1, 1.0, False), ("ColDim", "Bg", 0, 1, 0.6, False),
    ("ColBtn", "Line", 0, 1, 0.08, False), ("ColBtnHover", "Line", 0, 1, 0.18, False), ("ColPress", "Bg", 0, 1, 0.35, False),
    ("ColIcon", "Text", 0, 1, 0.75, False), ("ColCheck", "Frame", 0, 1, 1.0, False),
]
DERIVED_NAMES = [d[0] for d in DERIVED]


def rgb_lit(rgb, a=1.0):
    return "(R=%g,G=%g,B=%g,A=%g)" % (rgb[0], rgb[1], rgb[2], a)
