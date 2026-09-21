"""Generates assets/tex/*.png and assets/05_textures.json: the mod's UI textures (white, tintable via BrushColor)."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw
from bpdsl import M, write

T_ROUNDBOX = M + "/T_RoundBox"
T_CHECK_ON = M + "/T_CheckOn"
T_UNDO = M + "/T_Undo"; T_REDO = M + "/T_Redo"
T_CHECK_OFF = M + "/T_CheckOff"
T_PLUS = M + "/T_Plus"; T_MINUS = M + "/T_Minus"; T_CAM = M + "/T_Cam"; T_PHOTO = M + "/T_Photo"
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


def build(assets_dir):
    """Writes the PNGs under <assets_dir>/tex and returns the asset list (file relative to assets_dir)."""
    os.makedirs(os.path.join(assets_dir, "tex"), exist_ok=True)
    round_box(os.path.join(assets_dir, "tex", "roundbox.png"))
    check_box(os.path.join(assets_dir, "tex", "check_on.png"), True); check_box(os.path.join(assets_dir, "tex", "check_off.png"), False)
    circle_arrow(os.path.join(assets_dir, "tex", "undo.png"), False); circle_arrow(os.path.join(assets_dir, "tex", "redo.png"), True)
    circle_glyph(os.path.join(assets_dir, "tex", "plus.png"), True); circle_glyph(os.path.join(assets_dir, "tex", "minus.png"), False)
    color_glyph(os.path.join(assets_dir, "tex", "colorize.png"))
    circle_cam(os.path.join(assets_dir, "tex", "cam.png")); circle_photo(os.path.join(assets_dir, "tex", "photo.png"))
    return [{"type": "texture", "path": T_ROUNDBOX, "file": "tex/roundbox.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_CHECK_ON, "file": "tex/check_on.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_CHECK_OFF, "file": "tex/check_off.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_UNDO, "file": "tex/undo.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_REDO, "file": "tex/redo.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_PLUS, "file": "tex/plus.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_MINUS, "file": "tex/minus.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_COLORIZE, "file": "tex/colorize.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_CAM, "file": "tex/cam.png", "props": TEX_PROPS},
            {"type": "texture", "path": T_PHOTO, "file": "tex/photo.png", "props": TEX_PROPS}]


if __name__ == "__main__":
    A = os.path.join(os.path.dirname(__file__), "..")
    write(os.path.join(A, "05_textures.json"), build(A))
