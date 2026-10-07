#!/usr/bin/env python3
"""animlook.py - one sheet of a walk cycle: rows = views (front, left, back, top with the midline), columns = phases; with --ref a
second animation is drawn below for comparison (docs/howto/sichtpruefung.md for animations).

  scripts/animlook.py <anim.psa|anim.fbx> [--ref <anim.psa|fbx>] [--phases 8] [--views front,left,back,top] [--out file.png]
A .psa needs umodel's .config next to it (translation bones). Body: build/kit/female.fbx (exported from the kit by scripts/anim_extract.sh). Prints the sheet path."""
import os, sys, json, subprocess, argparse, tempfile
from PIL import Image, ImageDraw
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(W, "assets", "anim"))
PSA = os.path.join(W, "build", "anim", "psa", "Project", "Character", "Jodi", "Animations")


def resolve(anim, spec):
    """A pipeline name (assets/anim/anims.py) is built in Blender from its source .psa + modifier; else a .psa / .fbx path."""
    from anims import ANIMS
    if anim in ANIMS:
        a = ANIMS[anim]; spec.update(psa=os.path.join(PSA, a["source"] + ".psa"), config=os.path.join(PSA, a["source"] + ".config"),
                                     modifier=a.get("modifier"), params=a.get("params", {}))
    elif anim.endswith(".psa"): spec.update(psa=anim, config=anim[:-4] + ".config")
    else: spec["anim_fbx"] = anim
BODY = os.path.join(W, "build", "kit", "female.fbx"); ZOOM = {}


def render(anim, phases, views, out):
    spec = {"fbx": BODY, "phases": phases, "views": views, "res": [240, 320], "out": out, **ZOOM}
    resolve(anim, spec)
    r = subprocess.run(["blender", "-b", "--factory-startup", "--python", os.path.join(W, "assets", "anim", "blender", "sheet.py"), "--", json.dumps(spec)],
                       capture_output=True, text=True)
    if "SHEET OK" not in r.stdout: sys.exit("ANIMLOOK FAILED\n" + r.stdout[-3000:] + r.stderr[-2000:])


def block(d, phases, views, title):
    tiles = [[Image.open(os.path.join(d, "p%d_%s.png" % (i, v))) for i in range(phases)] for v in views]
    tw, th = tiles[0][0].size; img = Image.new("RGB", (tw * phases, th * len(views) + 22), (30, 30, 34)); dr = ImageDraw.Draw(img)
    dr.text((6, 4), title, fill=(230, 230, 230))
    for r, row in enumerate(tiles):
        for c, t in enumerate(row): img.paste(t, (c * tw, 22 + r * th))
    return img


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("anim"); ap.add_argument("--ref"); ap.add_argument("--phases", type=int, default=8)
    ap.add_argument("--views", default="front,left,back,top"); ap.add_argument("--out")
    ap.add_argument("--mesh", action="append", default=[], help="clothing glTF (umodel) worn while walking")
    ap.add_argument("--zoom", choices=["full", "legs", "hips", "upper"], default="full"); a = ap.parse_args()
    ZOOM["meshes"] = [os.path.abspath(m) for m in a.mesh]
    ZOOM.update({"full": {}, "legs": {"ortho": 1.0, "target_z": 0.45}, "hips": {"ortho": 0.8, "target_z": 0.9}, "upper": {"ortho": 0.9, "target_z": 1.3}}[a.zoom])
    views = a.views.split(","); blocks = []
    for anim in [a.anim] + ([a.ref] if a.ref else []):
        d = tempfile.mkdtemp(prefix="animlook_"); render(anim, a.phases, views, d)
        blocks.append(block(d, a.phases, views, os.path.basename(anim) + "   phases 0..%d of the cycle, rows: %s" % (a.phases - 1, ", ".join(views))))
    w = max(b.width for b in blocks); sheet = Image.new("RGB", (w, sum(b.height for b in blocks)), (30, 30, 34)); y = 0
    for b in blocks: sheet.paste(b, (0, y)); y += b.height
    out = a.out or os.path.join(W, "build", "look", "anim_" + os.path.splitext(os.path.basename(a.anim))[0] + ".png")
    os.makedirs(os.path.dirname(out), exist_ok=True); sheet.save(out); print(out)


if __name__ == "__main__":
    main()
