#!/usr/bin/env python3
"""Generates assets/28b_anims.json: the pipeline's animations (scripts/anim_build.py -> build/anim/out/<name>.json + .fbx) as bpgen
'animimport' entries under /Game/Mod/AltUI/Anims/ on Jodi's skeleton, with the game's curves, sync markers and Footstep notifies.
Test animations (assets/anim/anims.py 'test') only with ALTUI_ANIMTEST=1. Missing build output = error: run scripts/anim_extract.sh
and scripts/anim_build.py first (docs/specs/2026-10-06-anim-pipeline-design.md)."""
import os, sys, json, hashlib; sys.path[:0] = [os.path.dirname(__file__), os.path.join(os.path.dirname(__file__), "..", "anim")]
from bpdsl import write, M
from anims import ANIMS, enabled

ANIM_DIR = M + "/Anims"; SKELETON = "/Game/Project/Character/Jodi/Body/Female_Skeleton"
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "build", "anim", "out")


def wanted():
    return [n for n in ANIMS if enabled(n)]


def build():
    out = []
    for n in wanted():
        f = os.path.join(OUT, n + ".json")
        if not os.path.exists(f): sys.exit("gen_anims: %s missing - run scripts/anim_extract.sh and scripts/anim_build.py" % f)
        d = json.load(open(f))
        sha = hashlib.sha1(open(os.path.join(OUT, n + ".fbx"), "rb").read()).hexdigest()   # bpgen's incremental hash sees the entry only: a new FBX must change it
        out.append({"type": "animimport", "path": ANIM_DIR + "/" + n, "skeleton": SKELETON, "fbx": "../build/anim/out/%s.fbx" % n, "fbx_sha1": sha,
                    "curves": d["curves"], "markers": d["markers"], "notifies": d["notifies"]})
    return out


if __name__ == "__main__":
    write(os.path.join(os.path.dirname(__file__), "..", "28b_anims.json"), build())
