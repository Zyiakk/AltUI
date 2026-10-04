"""Generates assets/tex/*.png and assets/05_textures.json: the mod's UI textures (white, tintable via BrushColor)."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw
from bpdsl import M, write

T_ROUNDBOX = M + "/T_RoundBox"
T_CHECK_ON = M + "/T_CheckOn"
T_UNDO = M + "/T_Undo"; T_REDO = M + "/T_Redo"
T_CHECK_OFF = M + "/T_CheckOff"
T_PLUS = M + "/T_Plus"; T_MINUS = M + "/T_Minus"; T_CAM = M + "/T_Cam"; T_PHOTO = M + "/T_Photo"; T_POSE = M + "/T_Pose"
T_COLORIZE = M + "/T_Colorize"
TEX_PROPS = {"CompressionSettings": "TC_EditorIcon", "LODGroup": "TEXTUREGROUP_UI", "MipGenSettings": "TMGS_NoMipmaps",
             "NeverStream": True, "SRGB": True, "Filter": "TF_Bilinear"}


def round_box(path, size=48, radius=10, ss=4):
    """White rounded square with a smoothed edge (supersampling); alpha 0 outside."""
    big = Image.new("L", (size * ss, size * ss), 0)
    ImageDraw.Draw(big).rounded_rectangle((0, 0, size * ss - 1, size * ss - 1), radius=radius * ss, fill=255)
    alpha = big.resize((size, size), Image.LANCZOS)
    im = Image.new("RGBA", (size, size), (255, 255, 255, 0)); im.putalpha(alpha)
    im.save(path)


GRAYBLUE = (90, 107, 140, 255)


# search field = frame layer white 25 % + fill layer black 55 % -> composited grey 17 % at 66 % opacity
CHIP_FILL = (43, 43, 43, 169)
CHIP_FRAME = (255, 255, 255, 64)    # subtle white frame (COL_CHIP_FRAME: white 25 %)


def check_box(path, checked, size=48, radius=8, ss=4):
    """Round box in the style of the search field (dark fill, subtle white frame), optionally with a white check mark."""
    big = Image.new("RGBA", (size * ss, size * ss), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
    d.rounded_rectangle((0, 0, size * ss - 1, size * ss - 1), radius=radius * ss, fill=CHIP_FILL, outline=CHIP_FRAME, width=2 * ss)
    if checked:
        S = size * ss; w = int(S * 0.09)
        d.line([(S * 0.24, S * 0.52), (S * 0.43, S * 0.71), (S * 0.77, S * 0.30)], fill=(255, 255, 255, 255), width=w, joint="curve")
    big.resize((size, size), Image.LANCZOS).save(path)


def circle_arrow(path, clockwise, size=48, ss=4):
    """Circular arrow (undo/redo), white on transparent: arc 20..290 degrees, arrowhead at the end of the arc."""
    import math
    S = size * ss; big = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
    w = int(S * 0.11); cx = cy = S / 2; r = S * 0.33; end = 290
    d.arc((cx - r, cy - r, cx + r, cy + r), start=20, end=end, fill=(255, 255, 255, 255), width=w)
    a = math.radians(end); ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
    tx, ty = -math.sin(a), math.cos(a)          # tangent (direction of increasing angle)
    px, py = math.cos(a), math.sin(a)           # radial
    h = S * 0.20
    tip = (ex + tx * h, ey + ty * h); b1 = (ex + px * h * 0.75, ey + py * h * 0.75); b2 = (ex - px * h * 0.75, ey - py * h * 0.75)
    d.polygon([tip, b1, b2], fill=(255, 255, 255, 255))
    im = big.resize((size, size), Image.LANCZOS)
    if not clockwise: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im.save(path)


def circle_glyph(path, plus, size=128, ss=4):
    """White ring with a white minus (or plus) on transparent: distance buttons in the Jodi view."""
    S = size * ss; big = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
    w = int(S * 0.08); m = w // 2
    d.ellipse((m, m, S - 1 - m, S - 1 - m), outline=(255, 255, 255, 255), width=w)
    bw = int(S * 0.10); half = S * 0.22; c = S / 2
    d.rectangle((c - half, c - bw / 2, c + half, c + bw / 2), fill=(255, 255, 255, 255))
    if plus:
        d.rectangle((c - bw / 2, c - half, c + bw / 2, c + half), fill=(255, 255, 255, 255))
    big.resize((size, size), Image.LANCZOS).save(path)


def circle_cam(path, size=64, ss=4):
    """Camera glyph in a white ring: body (rounded rect) with a hump on top and a lens ring (free camera button)."""
    S = size * ss; big = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(big); W = (255, 255, 255, 255)
    w = int(S * 0.08); m = w // 2; d.ellipse((m, m, S - 1 - m, S - 1 - m), outline=W, width=w)
    d.rounded_rectangle((S * 0.26, S * 0.40, S * 0.74, S * 0.68), radius=int(S * 0.05), fill=W)
    d.rounded_rectangle((S * 0.40, S * 0.33, S * 0.60, S * 0.42), radius=int(S * 0.03), fill=W)   # hump
    d.ellipse((S * 0.42, S * 0.46, S * 0.58, S * 0.62), fill=(255, 255, 255, 0))                    # lens hole
    d.ellipse((S * 0.455, S * 0.495, S * 0.545, S * 0.585), fill=W)                                 # lens
    big.resize((size, size), Image.LANCZOS).save(path)


def circle_photo(path, size=64, ss=4):
    """Aperture glyph in a white ring: circle with six blades (photo mode button)."""
    import math
    S = size * ss; big = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(big); W = (255, 255, 255, 255)
    w = int(S * 0.08); m = w // 2; d.ellipse((m, m, S - 1 - m, S - 1 - m), outline=W, width=w)
    cx = cy = S / 2; r = S * 0.24; d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=W, width=int(S * 0.05))
    for i in range(6):
        a = math.radians(60 * i); b = math.radians(60 * i + 110)
        d.line([(cx + r * 0.95 * math.cos(a), cy + r * 0.95 * math.sin(a)), (cx + r * 0.45 * math.cos(b), cy + r * 0.45 * math.sin(b))], fill=W, width=int(S * 0.04))
    big.resize((size, size), Image.LANCZOS).save(path)


def color_glyph(path, size=48, ss=4):
    """Three overlapping pastel discs (red top, green left, blue right) with a light centre - the vanilla "colour adjustable" subscript."""
    S = size * ss; big = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
    r = S * 0.30; cx = S / 2; cy = S / 2
    for (dx, dy), col in (((0, -0.18), (255, 122, 122, 235)), ((-0.19, 0.14), (150, 240, 170, 235)), ((0.19, 0.14), (150, 165, 255, 235))):
        x, y = cx + dx * S, cy + dy * S
        layer = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ImageDraw.Draw(layer).ellipse((x - r, y - r, x + r, y + r), fill=col)
        big = Image.alpha_composite(big, layer)
    d = ImageDraw.Draw(big); rc = S * 0.11; d.ellipse((cx - rc, cy - rc, cx + rc, cy + rc), fill=(255, 255, 255, 240))
    big.resize((size, size), Image.LANCZOS).save(path)


def stick_figure(path, size=128, ss=4):
    """White stick figure on transparent (head, body, one arm on the hip, one raised, legs apart): tile icon of the poses tab."""
    S = size * ss; big = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(big); W = (255, 255, 255, 255); lw = int(S * 0.06); cx = S / 2
    d.ellipse((cx - S * 0.11, S * 0.06, cx + S * 0.11, S * 0.28), fill=W)                                                        # head
    d.line([(cx, S * 0.28), (cx, S * 0.62)], fill=W, width=lw)                                                                   # body
    d.line([(cx, S * 0.36), (cx - S * 0.20, S * 0.50), (cx - S * 0.15, S * 0.62)], fill=W, width=lw, joint="curve")             # arm on the hip
    d.line([(cx, S * 0.36), (cx + S * 0.18, S * 0.24), (cx + S * 0.32, S * 0.08)], fill=W, width=lw, joint="curve")             # arm raised
    d.line([(cx, S * 0.62), (cx - S * 0.18, S * 0.94)], fill=W, width=lw); d.line([(cx, S * 0.62), (cx + S * 0.18, S * 0.94)], fill=W, width=lw)   # legs
    big.resize((size, size), Image.LANCZOS).save(path)


# ---------------- tab icons (white glyphs without ring, same strokes as the camera / photo buttons; tab bar + quick menu) ----------------
def _glyph(path, draw, size=128, ss=4):
    """Draws the glyph and centres its visible part (alpha bounding box) in the texture: icons of different heights then share one
    centre line next to the tab text."""
    S = size * ss; big = Image.new("RGBA", (S, S), (0, 0, 0, 0)); draw(ImageDraw.Draw(big), S, (255, 255, 255, 255), (255, 255, 255, 0))
    x0, y0, x1, y1 = big.split()[3].getbbox()
    out = Image.new("RGBA", (S, S), (255, 255, 255, 0)); out.paste(big, (round((S - x1 - x0) / 2), round((S - y1 - y0) / 2)))
    out.resize((size, size), Image.LANCZOS).save(path)


def _pts(S, pts): return [(x * S, y * S) for x, y in pts]


def tab_clothes(d, S, W, C):
    """T-shirt."""
    d.polygon(_pts(S, [(0.37, 0.13), (0.63, 0.13), (0.80, 0.19), (0.96, 0.39), (0.83, 0.51), (0.75, 0.43), (0.75, 0.89), (0.25, 0.89),
                       (0.25, 0.43), (0.17, 0.51), (0.04, 0.39), (0.20, 0.19)]), fill=W)
    d.ellipse((S * 0.38, S * 0.03, S * 0.62, S * 0.23), fill=C)                                       # neckline


def tab_outfits(d, S, W, C):
    """Clothes hanger."""
    w = int(S * 0.07)
    d.arc((S * 0.40, S * 0.08, S * 0.60, S * 0.28), start=150, end=430, fill=W, width=w)              # hook
    d.line(_pts(S, [(0.5, 0.27), (0.5, 0.36)]), fill=W, width=w)
    d.line(_pts(S, [(0.5, 0.36), (0.07, 0.74), (0.93, 0.74), (0.5, 0.36)]), fill=W, width=w, joint="curve")
    for x in (0.07, 0.93): d.ellipse((S * x - w / 2, S * 0.74 - w / 2, S * x + w / 2, S * 0.74 + w / 2), fill=W)


def tab_looks(d, S, W, C):
    """Photo of a person (a saved look with its picture)."""
    d.rounded_rectangle((S * 0.14, S * 0.06, S * 0.86, S * 0.94), radius=int(S * 0.07), outline=W, width=int(S * 0.07))
    d.ellipse((S * 0.38, S * 0.22, S * 0.62, S * 0.46), fill=W)                                       # head
    d.pieslice((S * 0.24, S * 0.52, S * 0.76, S * 1.04), start=180, end=360, fill=W)                  # shoulders
    d.rectangle((S * 0.24, S * 0.78, S * 0.76, S * 0.87), fill=W)


def tab_bag(d, S, W, C):
    """Backpack: handle, body, front pocket."""
    w = int(S * 0.07)
    d.rounded_rectangle((S * 0.36, S * 0.05, S * 0.64, S * 0.26), radius=int(S * 0.09), outline=W, width=w)  # handle
    d.rounded_rectangle((S * 0.16, S * 0.18, S * 0.84, S * 0.95), radius=int(S * 0.20), fill=W)
    d.rounded_rectangle((S * 0.29, S * 0.55, S * 0.71, S * 0.84), radius=int(S * 0.06), fill=C)              # pocket
    d.rounded_rectangle((S * 0.34, S * 0.60, S * 0.66, S * 0.79), radius=int(S * 0.04), fill=W)
    d.rectangle((S * 0.29, S * 0.62, S * 0.71, S * 0.655), fill=C)                                           # pocket flap seam


def tab_hair(d, S, W, C):
    """Long hair around an open face, a side-swept fringe over the forehead."""
    d.ellipse((S * 0.14, S * 0.04, S * 0.86, S * 0.64), fill=W)
    d.polygon(_pts(S, [(0.14, 0.34), (0.86, 0.34), (0.93, 0.94), (0.07, 0.94)]), fill=W)              # hair falling to the shoulders
    d.ellipse((S * 0.32, S * 0.20, S * 0.68, S * 0.74), fill=C)                                       # face
    d.rectangle((S * 0.43, S * 0.66, S * 0.57, S * 0.94), fill=C)                                     # neck
    d.polygon(_pts(S, [(0.28, 0.16), (0.74, 0.16), (0.70, 0.32), (0.56, 0.40), (0.30, 0.52)]), fill=W)       # fringe


def tab_weapons(d, S, W, C):
    """Pistol, muzzle to the left."""
    d.rounded_rectangle((S * 0.05, S * 0.26, S * 0.93, S * 0.45), radius=int(S * 0.03), fill=W)      # slide
    d.polygon(_pts(S, [(0.60, 0.42), (0.90, 0.42), (0.95, 0.84), (0.73, 0.86)]), fill=W)               # grip
    d.arc((S * 0.43, S * 0.36, S * 0.67, S * 0.64), start=10, end=180, fill=W, width=int(S * 0.055))  # trigger guard
    d.line(_pts(S, [(0.58, 0.44), (0.55, 0.54)]), fill=W, width=int(S * 0.045))                       # trigger


def tab_look(d, S, W, C):
    """Lipstick (skin, makeup, eyes)."""
    d.rounded_rectangle((S * 0.30, S * 0.56, S * 0.70, S * 0.95), radius=int(S * 0.04), fill=W)      # case
    d.rectangle((S * 0.35, S * 0.40, S * 0.65, S * 0.52), fill=W)                                     # collar
    d.polygon(_pts(S, [(0.39, 0.38), (0.61, 0.38), (0.61, 0.13), (0.39, 0.25)]), fill=W)              # bullet, slanted tip


def _profile(keys, n=120):
    """Smooth half-width profile through (y, half width) keys (Catmull-Rom): [(y, hw), ...] from the first key to the last."""
    k = [keys[0]] + list(keys) + [keys[-1]]; out = []
    for i in range(1, len(k) - 2):
        p0, p1, p2, p3 = k[i - 1], k[i], k[i + 1], k[i + 2]
        for j in range(n // (len(keys) - 1)):
            t = j / (n // (len(keys) - 1)); t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[c] + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2 + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in (0, 1)))
    return out + [keys[-1]]


def _sym(S, prof, cx=0.5):
    """Closed outline, mirrored at x = cx."""
    return [(S * (cx + w), S * y) for y, w in prof] + [(S * (cx - w), S * y) for y, w in reversed(prof)]


def tab_body(d, S, W, C):
    """Female torso: neck, shoulders, a soft waist, hips, the tops of the thighs."""
    prof = _profile([(0.03, 0.065), (0.10, 0.075), (0.17, 0.23), (0.25, 0.26), (0.36, 0.235), (0.50, 0.16), (0.64, 0.235), (0.78, 0.265), (0.97, 0.215)])
    d.polygon(_sym(S, prof), fill=W)
    d.polygon(_pts(S, [(0.465, 0.98), (0.5, 0.82), (0.535, 0.98)]), fill=C)                           # between the legs


def tab_face(d, S, W, C):
    """Smiley: ring, two eyes, a smile."""
    w = int(S * 0.07); m = S * 0.06
    d.ellipse((m, m, S - m, S - m), outline=W, width=w)
    for x in (0.37, 0.63): d.ellipse((S * (x - 0.06), S * 0.30, S * (x + 0.06), S * 0.44), fill=W)
    d.arc((S * 0.27, S * 0.30, S * 0.73, S * 0.74), start=25, end=155, fill=W, width=w)


def tab_mods(d, S, W, C):
    """Puzzle piece."""
    d.rectangle((S * 0.12, S * 0.28, S * 0.74, S * 0.90), fill=W)
    d.ellipse((S * 0.32, S * 0.08, S * 0.54, S * 0.30), fill=W)                                       # knob top
    d.ellipse((S * 0.72, S * 0.48, S * 0.94, S * 0.70), fill=W)                                       # knob right
    d.ellipse((S * 0.03, S * 0.48, S * 0.21, S * 0.66), fill=C)                                       # notch left
    d.ellipse((S * 0.34, S * 0.81, S * 0.52, S * 0.99), fill=C)                                       # notch bottom


def tab_options(d, S, W, C):
    """Gear with eight teeth."""
    import math
    cx = cy = S / 2; ro, ri = S * 0.46, S * 0.34; pts = []
    for i in range(8):
        a = math.radians(45 * i)
        for da, r in ((-15, ri), (-9, ro), (9, ro), (15, ri)):
            b = a + math.radians(da); pts.append((cx + r * math.cos(b), cy + r * math.sin(b)))
    d.polygon(pts, fill=W); d.ellipse((cx - ri, cy - ri, cx + ri, cy + ri), fill=W)
    rh = S * 0.15; d.ellipse((cx - rh, cy - rh, cx + rh, cy + rh), fill=C)


def tab_manage(d, S, W, C):
    """List of names with a pencil."""
    lw = int(S * 0.07)
    for y in (0.20, 0.42, 0.64):
        d.ellipse((S * 0.05, S * (y - 0.05), S * 0.15, S * (y + 0.05)), fill=W)
        d.line(_pts(S, [(0.25, y), (0.86 if y < 0.6 else 0.48, y)]), fill=W, width=lw)
    # pencil from lower left to upper right, tip at the lower left
    import math
    a = math.radians(-40); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux; tx, ty = 0.52, 0.94; L, hw = 0.50, 0.07
    def p(u, n): return (S * (tx + ux * u + nx * n), S * (ty + uy * u + ny * n))
    d.polygon([p(0.0, 0), p(0.13, hw), p(L, hw), p(L, -hw), p(0.13, -hw)], fill=W)
    d.polygon([p(0.36, hw + 0.01), p(0.40, hw + 0.01), p(0.40, -hw - 0.01), p(0.36, -hw - 0.01)], fill=C)   # ferrule gap


def altui_panel(d, S, W, C):
    """The AltUI panel, stylised: frame, tab bar with the chosen tab underlined, category list on the left, tile grid on the right."""
    d.rounded_rectangle((S * 0.04, S * 0.10, S * 0.96, S * 0.90), radius=int(S * 0.08), outline=W, width=int(S * 0.06))
    for i, x in enumerate((0.15, 0.36, 0.57)):
        d.rectangle((S * x, S * 0.22, S * (x + 0.15), S * 0.27), fill=W)
    d.rectangle((S * 0.15, S * 0.31, S * 0.30, S * 0.34), fill=W)                                     # underline of the chosen tab
    for y in (0.45, 0.57, 0.69):
        d.rectangle((S * 0.15, S * y, S * 0.30, S * (y + 0.05)), fill=W)                              # category list
    for r, y in enumerate((0.43, 0.62)):
        for c, x in enumerate((0.39, 0.57, 0.75)):
            d.rounded_rectangle((S * x, S * y, S * (x + 0.13), S * (y + 0.15)), radius=int(S * 0.025), fill=W)


TAB_ICON_DRAW = {"Clothes": tab_clothes, "Outfits": tab_outfits, "Looks": tab_looks, "Bag": tab_bag, "Hair": tab_hair, "Weapons": tab_weapons,
                 "Look": tab_look, "Body": tab_body, "Face": tab_face, "Mods": tab_mods, "Options": tab_options, "Manage": tab_manage}
T_ALTUI = M + "/T_AltUI"
TAB_ICONS = dict({k: M + "/T_Tab" + k for k in TAB_ICON_DRAW}, Poses=T_POSE)   # page -> texture; Poses uses the pose tiles' stick figure


def build(assets_dir):
    """Writes the PNGs under <assets_dir>/tex and returns the asset list (file relative to assets_dir)."""
    os.makedirs(os.path.join(assets_dir, "tex"), exist_ok=True)
    round_box(os.path.join(assets_dir, "tex", "roundbox.png"))
    check_box(os.path.join(assets_dir, "tex", "check_on.png"), True); check_box(os.path.join(assets_dir, "tex", "check_off.png"), False)
    circle_arrow(os.path.join(assets_dir, "tex", "undo.png"), False); circle_arrow(os.path.join(assets_dir, "tex", "redo.png"), True)
    circle_glyph(os.path.join(assets_dir, "tex", "plus.png"), True); circle_glyph(os.path.join(assets_dir, "tex", "minus.png"), False)
    color_glyph(os.path.join(assets_dir, "tex", "colorize.png"))
    circle_cam(os.path.join(assets_dir, "tex", "cam.png")); circle_photo(os.path.join(assets_dir, "tex", "photo.png"))
    stick_figure(os.path.join(assets_dir, "tex", "pose.png"))
    for k, f in TAB_ICON_DRAW.items(): _glyph(os.path.join(assets_dir, "tex", "tab_%s.png" % k.lower()), f)
    _glyph(os.path.join(assets_dir, "tex", "altui.png"), altui_panel)
    return [{"type": "texture", "path": T_ROUNDBOX, "file": "tex/roundbox.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_CHECK_ON, "file": "tex/check_on.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_CHECK_OFF, "file": "tex/check_off.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_UNDO, "file": "tex/undo.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_REDO, "file": "tex/redo.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_PLUS, "file": "tex/plus.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_MINUS, "file": "tex/minus.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_COLORIZE, "file": "tex/colorize.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_CAM, "file": "tex/cam.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_PHOTO, "file": "tex/photo.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_POSE, "file": "tex/pose.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_ALTUI, "file": "tex/altui.png", "props": TEX_PROPS}] + \
           [{"type": "texture", "path": M + "/T_Tab" + k, "file": "tex/tab_%s.png" % k.lower(), "props": TEX_PROPS} for k in TAB_ICON_DRAW]


if __name__ == "__main__":
    A = os.path.join(os.path.dirname(__file__), "..")
    write(os.path.join(A, "05_textures.json"), build(A))
