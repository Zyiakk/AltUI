#!/usr/bin/env python3
"""anim_build.py - animation pipeline step 2 (docs/specs/2026-10-06-anim-pipeline-design.md): for every entry of assets/anim/anims.py
Blender builds the FBX (build_anim.py: source .psa on Jodi, optional modifier), and the game data of the source is carried over into
build/anim/out/<name>.json for bpgen's animimport: curves (scripts/animcurves.py, sampled per frame), sync markers and Footstep notifies
(scripts/uasset_props.py), all times scaled to the new length. Needs scripts/anim_extract.sh first.
  scripts/anim_build.py [name ...]"""
import os, sys, json, subprocess
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path[:0] = [os.path.join(W, "scripts"), os.path.join(W, "assets", "anim")]
import animcurves
from anims import ANIMS
SRC = os.path.join(W, "build", "anim", "src", "TheKillingAntidote", "Content", "Project", "Character", "Jodi", "Animations")
PSA = os.path.join(W, "build", "anim", "psa", "Project", "Character", "Jodi", "Animations")
OUT = os.path.join(W, "build", "anim", "out"); BODY = os.path.join(W, "build", "kit", "female.fbx")


def source_data(src):
    ua = os.path.join(SRC, src + ".uasset")
    p = json.loads(subprocess.run([sys.executable, os.path.join(W, "scripts", "uasset_props.py"), ua], capture_output=True, text=True, check=True).stdout)[src]["props"]
    c = animcurves.read(ua)
    return {"length": p["SequenceLength"], "curves": c["curves"], "markers": [[m["MarkerName"], m["Time"]] for m in p.get("AuthoredSyncMarkers", [])],
            "notifies": [[n["NotifyName"], n["LinkValue"]] for n in p.get("Notifies", [])]}


def foot_phase(markers, length):
    """MoveData_FootPhase like the game's loops: 1 around the L markers, 0 around the R ones, switching halfway between two markers
    (constant keys; Female_Walk / Female_Run follow this). Markers are cyclic over the loop."""
    ms = sorted((t % length, m) for m, t in markers); n = len(ms); keys = []
    for i in range(n):
        t0, m0 = ms[i]; t1 = ms[(i + 1) % n][0] + (length if i == n - 1 else 0.0)
        keys.append([(round((t0 + t1) / 2.0 * 30.0) / 30.0) % length, 1.0 if ms[(i + 1) % n][1] == "L" else 0.0])   # on a frame, as in the game's loops
    keys.sort(); first = keys[-1][1]   # value at time 0 = the value after the last switch
    out = [[0.0, first, "constant"]] + [[t, v, "constant"] for t, v in keys if t > 1e-4] + [[length, first if not keys else keys[-1][1], "constant"]]
    return out


def build(name, spec):
    os.makedirs(OUT, exist_ok=True); src = spec["source"]
    fbx, info = os.path.join(OUT, name + ".fbx"), os.path.join(OUT, name + ".blender.json")
    bspec = {"fbx": BODY, "psa": os.path.join(PSA, src + ".psa"), "config": os.path.join(PSA, src + ".config"), "out_fbx": fbx, "out_json": info,
             "modifier": spec.get("modifier"), "params": spec.get("params", {})}
    r = subprocess.run(["blender", "-b", "--factory-startup", "--python", os.path.join(W, "assets", "anim", "blender", "build_anim.py"), "--", json.dumps(bspec)],
                       capture_output=True, text=True)
    if "BUILD ANIM OK" not in r.stdout: sys.exit("ANIM BUILD FAILED %s\n%s\n%s" % (name, r.stdout[-3000:], r.stderr[-2000:]))
    bi = json.load(open(info)); sd = source_data(src)
    length = (bi["frames"] - 1) / bi["fps"]; k = length / sd["length"]
    over = bi.get("curves", {})   # a modifier may replace a curve (e.g. MoveData_Speed from the new stride)
    # keys [t, v, mode]: a constant as two keys, a keyed curve with its own keys and interpolation (FootPhase is a step curve), stretched by k;
    # a modifier's value replaces the curve by a constant
    MODE = {animcurves.CONSTANT: "constant", animcurves.LINEAR: "linear"}
    curves = {}
    src_curves = dict(sd["curves"])
    if spec.get("donor"):   # movement curves the source lacks, as the donor's constants (Rotation Speed, Forward Moving Alpha, ...)
        for n, cv in source_data(spec["donor"])["curves"].items():
            if n not in src_curves and "constant" in cv and not n.startswith("Face_"): src_curves[n] = cv   # movement only, the face stays the source's
    if spec.get("foot_phase") == "markers": src_curves.pop("MoveData_FootPhase", None)
    for n, cv in src_curves.items():
        if n in over: curves[n] = [[0.0, over[n], "linear"], [length, over[n], "linear"]]
        elif "constant" in cv: curves[n] = [[0.0, cv["constant"], "linear"], [length, cv["constant"], "linear"]]
        else: curves[n] = [[t * k, v, MODE.get(m, "cubic")] for t, v, _, _, m in cv["keys"] if t * k <= length + 1e-4]
    markers = bi.get("markers") or [[m, t * k] for m, t in sd["markers"]]
    if spec.get("foot_phase") == "markers": curves["MoveData_FootPhase"] = foot_phase(markers, length)
    notifies = bi.get("notifies") or [[m, t * k] for m, t in sd["notifies"]]
    json.dump({"name": name, "fbx": fbx, "length": length, "fps": bi["fps"], "curves": curves, "markers": markers, "notifies": notifies, "test": spec.get("test", False)},
              open(os.path.join(OUT, name + ".json"), "w"), indent=1)
    print("ANIM", name, "len %.4f" % length, "curves", len(curves), "markers", len(markers), "notifies", len(notifies))


if __name__ == "__main__":
    for n in (sys.argv[1:] or ANIMS): build(n, ANIMS[n])
