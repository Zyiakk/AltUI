"""AltUI's own pictures for Options > Theme: panel backgrounds and button images, drawn here (no outside sources).
Each entry: (key, text key of its chip, size, draw function). The textures are T_Bg<Key> / T_Btn<Key>; own files of the user
come from Saved/SaveGames/AltUI/Images (Background_<n> / Button_<n>, .png, .jpg or .jpeg - Blueprints cannot list a folder, so the
names are fixed and probed)."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageFilter
from bpdsl import M

USER_DIR = "SaveGames/AltUI/Images"   # under ProjectSavedDir
USER_MAX = 30                           # Background_1 .. Background_30, Button_1 .. Button_30
USER_EXT = [".png", ".jpg", ".jpeg"]
# how the background fills the panel (ScaleBox stretch; tile = an Image brush with Tiling)
FITS = ["Img_FitFill", "Img_FitFit", "Img_FitStretch", "Img_FitTile"]
H_ALIGN = ["Img_AlignLeft", "Img_AlignCenter", "Img_AlignRight"]
V_ALIGN = ["Img_AlignTop", "Img_AlignMiddle", "Img_AlignBottom"]
TEX_BIG = {"CompressionSettings": "TC_Default", "LODGroup": "TEXTUREGROUP_UI", "MipGenSettings": "TMGS_NoMipmaps", "NeverStream": True, "SRGB": True, "Filter": "TF_Bilinear"}


def _rng(seed): return np.random.default_rng(seed)


def _save(arr, path):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").save(path)


def night(n):
    """Dark blue-violet, lighter towards the top, soft vignette."""
    y, x = np.mgrid[0:n, 0:n] / (n - 1)
    top, bot = np.array([38, 40, 68]), np.array([10, 10, 18])
    c = top * (1 - y[..., None]) + bot * y[..., None]
    v = 1 - 0.45 * (((x - 0.5) ** 2 + (y - 0.45) ** 2) ** 0.5)[..., None]
    return c * v + _rng(1).normal(0, 1.5, (n, n, 1))


def carbon(n, cell=16):
    """Carbon weave (tiles seamlessly when n is a multiple of 2 * cell)."""
    y, x = np.mgrid[0:n, 0:n]
    cx, cy = (x // cell) % 2, (y // cell) % 2
    u, v = (x % cell) / cell, (y % cell) / cell
    shade = np.where(cx == cy, 0.55 + 0.45 * np.sin(np.pi * u), 0.55 + 0.45 * np.sin(np.pi * v))
    base = 18 + 26 * shade
    return np.stack([base, base, base * 1.08], -1)


def bokeh(n):
    """Dark ground with soft, blurred circles of light."""
    im = Image.new("RGB", (n, n), (12, 12, 16)); r = _rng(7)
    from PIL import ImageDraw
    layer = Image.new("RGB", (n, n), (0, 0, 0)); d = ImageDraw.Draw(layer)
    for _ in range(26):
        cx, cy, rad = r.integers(0, n), r.integers(0, n), r.integers(n // 30, n // 9)
        col = tuple(int(v) for v in r.choice([[120, 60, 140], [60, 90, 150], [150, 70, 90], [70, 120, 130]]) * r.uniform(0.35, 0.8))
        d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=col)
    layer = layer.filter(ImageFilter.GaussianBlur(n / 60))
    return np.asarray(im, float) + 0.55 * np.asarray(layer, float)


def grid(n, step=64):
    """Slate blue with thin lines (tiles seamlessly when n is a multiple of step)."""
    y, x = np.mgrid[0:n, 0:n]
    c = np.ones((n, n, 3)) * np.array([22, 27, 36])
    line = ((x % step) < 1) | ((y % step) < 1); fine = ((x % (step // 4)) < 1) | ((y % (step // 4)) < 1)
    c[fine] += 6; c[line] += 18
    return c


def metal(n):
    """Brushed metal: horizontal streaks, slightly darker at the bottom."""
    r = _rng(3); streak = r.normal(0, 1, (n, 1)) * np.ones((1, n)) + 0.35 * r.normal(0, 1, (n, n))
    y = np.mgrid[0:n, 0:n][0] / (n - 1)
    base = 92 - 30 * y + 7 * streak
    return np.stack([base, base * 1.02, base * 1.06], -1)


def glass(n):
    """Dark glass: a bright band at the top fading into deep grey-blue."""
    y = np.mgrid[0:n, 0:n][0] / (n - 1)
    c = np.array([70, 78, 96]) * (1 - y[..., None]) ** 1.6 + np.array([16, 18, 24])
    c += np.where(y < 0.06, 40 * (1 - y / 0.06), 0)[..., None]
    return c


def linen(n):
    """Woven fabric: fine noise stretched along both axes."""
    r = _rng(11); a = r.normal(0, 1, (n, n))
    h = np.asarray(Image.fromarray(((a + 3) * 40).clip(0, 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(2)), float)
    v = np.asarray(Image.fromarray(((a.T + 3) * 40).clip(0, 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(2)), float)
    base = 54 + 0.25 * (h - 120) + 0.25 * (v - 120)
    return np.stack([base * 1.05, base, base * 0.92], -1)


# card stock (the elegant business cards of the late eighties): off-white papers with fibre, laid lines, a raised weave
def _blur(a, r):
    lo, hi = a.min(), a.max(); im = Image.fromarray(((a - lo) / (hi - lo + 1e-9) * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), float) / 255 * (hi - lo) + lo


def _fibre(n, seed):
    """Paper fibre: noise at a few scales, stretched a little along x."""
    r = _rng(seed); f = np.zeros((n, n))
    for sc, w in ((1, 0.5), (3, 0.8), (9, 1.0), (40, 0.6)):
        f += w * _blur(r.normal(0, 1, (n, n)), sc)
    return (f - f.mean()) / (f.std() + 1e-9)


def _card(n, base, seed, grain):
    f = _fibre(n, seed); c = np.array(base, float)[None, None, :] + grain * f[..., None]
    return c


def bone(n): return _card(n, (226, 219, 201), 21, 4.0)


def eggshell(n):
    """Cream with the fine stipple of an eggshell finish."""
    c = _card(n, (236, 231, 214), 22, 3.0); st = _blur(_rng(23).normal(0, 1, (n, n)), 0.8)
    return c + 3.5 * st[..., None]


def laid(n):
    """Laid paper: dense fine lines across, chain lines every few centimetres."""
    y, x = np.mgrid[0:n, 0:n]; c = _card(n, (229, 228, 222), 24, 2.5)
    lines = 2.2 * np.sin(2 * np.pi * y / 6.0) + 3.0 * np.exp(-((x % 96) - 48) ** 2 / 8.0)
    return c - lines[..., None]


def nimbus(n):
    """Pale cloudy grey-white, very soft: coarse noise scaled up smoothly (a wide Gaussian in PIL leaves blocks)."""
    r = _rng(25); cl = np.zeros((n, n))
    for m, w in ((6, 1.0), (12, 0.5), (24, 0.25)):
        small = ((r.normal(0, 1, (m, m)) + 3) * 40).clip(0, 255).astype(np.uint8)
        cl += w * (np.asarray(Image.fromarray(small).resize((n, n), Image.BICUBIC), float) / 40 - 3)
    cl = (cl - cl.mean()) / (cl.std() + 1e-9)
    return _card(n, (222, 223, 224), 26, 1.5) + 5.0 * cl[..., None]


def emboss(n):
    """Raised linen weave lit from the top left."""
    y, x = np.mgrid[0:n, 0:n]; w = np.sin(2 * np.pi * x / 5.0) * np.sin(2 * np.pi * y / 5.0) + 0.5 * _fibre(n, 27)
    h = _blur(w, 0.7); light = (np.roll(h, 1, 0) - h) + (np.roll(h, 1, 1) - h)
    return np.array([231, 226, 214], float)[None, None, :] + 9.0 * light[..., None]


CARDS = [("Bone", "Img_Bone", bone), ("Eggshell", "Img_Eggshell", eggshell), ("Laid", "Img_Laid", laid), ("Nimbus", "Img_Nimbus", nimbus), ("Emboss", "Img_Emboss", emboss)]


BACKGROUNDS = [("Night", "Img_BgNight", 1024, night), ("Carbon", "Img_Carbon", 1024, carbon), ("Bokeh", "Img_BgBokeh", 1024, bokeh), ("Grid", "Img_BgGrid", 1024, grid)]
BUTTONS = [("Metal", "Img_BtnMetal", 256, metal), ("Carbon", "Img_Carbon", 256, lambda n: carbon(n, 8)), ("Glass", "Img_BtnGlass", 256, glass), ("Linen", "Img_BtnLinen", 256, linen)]
BACKGROUNDS += [(k, t, 1024, f) for k, t, f in CARDS]
BUTTONS += [(k, t, 256, f) for k, t, f in CARDS]


# previews in the chips (option "Show previews"): pixel size of the picture = three times its size in layout units (THUMB_UNITS);
# AltUI's own come as textures T_BgThumb<Key> / T_BtnThumb<Key>, the user's are rendered once into USER_DIR/Thumbs (Manager: Write User Thumb)
THUMB_UNITS = {"bg": (80, 45), "btn": (45, 45)}
THUMB_PX = {k: (3 * w, 3 * h) for k, (w, h) in THUMB_UNITS.items()}   # x SC 1.9 x DPI 1.33 at 1440p ~ 2.5 screen pixels per unit
THUMB_DIR = "Thumbs/"
THUMB_STEPS = 3   # user pictures: drawn at 2^3 x the preview size, then halved three times (each halving averages 2 x 2 pixels - no flicker from skipped pixels)


def tex_path(kind, key): return M + ("/T_Bg" if kind == "bg" else "/T_Btn") + key


def thumb_path(kind, key): return M + ("/T_BgThumb" if kind == "bg" else "/T_BtnThumb") + key


def thumb(arr, kind):
    """The preview: the middle of the picture cut to the chip's aspect, scaled down (Lanczos)."""
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB"); tw, th = THUMB_PX[kind]
    w, h = im.size; cw, ch = (w, round(w * th / tw)) if w * th <= h * tw else (round(h * tw / th), h)
    im = im.crop(((w - cw) // 2, (h - ch) // 2, (w - cw) // 2 + cw, (h - ch) // 2 + ch))
    return im.resize((tw, th), Image.LANCZOS)


def build(assets_dir):
    out = []
    for kind, lst in (("bg", BACKGROUNDS), ("btn", BUTTONS)):
        for key, _, n, f in lst:
            arr = f(n); rel = "tex/%s_%s.png" % (kind, key.lower()); _save(arr, os.path.join(assets_dir, rel))
            out.append({"type": "texture", "path": tex_path(kind, key), "file": rel, "props": TEX_BIG})
            rel = "tex/%s_%s_thumb.png" % (kind, key.lower()); thumb(arr, kind).save(os.path.join(assets_dir, rel))
            out.append({"type": "texture", "path": thumb_path(kind, key), "file": rel, "props": TEX_BIG})
    return out
