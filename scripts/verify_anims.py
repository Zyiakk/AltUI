#!/usr/bin/env python3
"""verify_anims.py - checks the cooked pipeline animations (docs/specs/2026-10-06-anim-pipeline-design.md) against their build data
(build/anim/out/<name>.json): length, curve names and values (every frame, 1 % / 0.01), sync markers and Footstep notifies. A copy of a
game animation (assets/anim/anims.py without modifier) is also compared with the game's original. Needs COOKED (config.sh)."""
import os, sys, json, subprocess
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path[:0] = [os.path.join(W, "scripts"), os.path.join(W, "assets", "gen"), os.path.join(W, "assets", "anim")]
import animcurves, gen_anims
from anims import ANIMS
COOKED = os.environ["COOKED"]
SRC = os.path.join(W, "build", "anim", "src", "TheKillingAntidote", "Content", "Project", "Character", "Jodi", "Animations")


def props(ua, name):
    out = subprocess.run([sys.executable, os.path.join(W, "scripts", "uasset_props.py"), ua], capture_output=True, text=True, check=True).stdout
    return json.loads(out)[name]["props"]


def compare(label, ua, name, want, bad, subset=False):
    """subset: the cooked curves may hold more than `want` (curves added from a donor) - only want's must be there and equal."""
    p = props(ua, name); c = animcurves.read(ua)
    if abs(p["SequenceLength"] - want["length"]) > 1e-3: bad.append("%s: length %.4f, expected %.4f" % (label, p["SequenceLength"], want["length"]))
    if (not set(want["curves"]) <= set(c["curves"])) if subset else sorted(c["curves"]) != sorted(want["curves"]): bad.append("%s: curves %s, expected %s" % (label, sorted(c["curves"]), sorted(want["curves"])))
    for n in want["curves"]:
        if n not in c["curves"]: continue
        for t in [(i + 0.5) / 30.0 for i in range(int(want["length"] * 30))]:   # mid-frame: a step curve's edge sits on a frame time
            v = animcurves.evaluate(want["curves_eval"][n], t); got = animcurves.evaluate(c["curves"][n], t)
            if abs(got - v) > max(0.01, abs(v) * 0.01): bad.append("%s: %s at %.3f = %.4f, expected %.4f" % (label, n, t, got, v)); break
    mk = [[m["MarkerName"], m["Time"]] for m in p.get("AuthoredSyncMarkers", [])]
    if [m for m, _ in mk] != [m for m, _ in want["markers"]] or any(abs(a[1] - b[1]) > 0.02 for a, b in zip(mk, want["markers"])):
        bad.append("%s: markers %s, expected %s" % (label, mk, want["markers"]))
    nt = sorted([n["NotifyName"], n["LinkValue"]] for n in p.get("Notifies", []))
    if [n for n, _ in nt] != [n for n, _ in sorted(want["notifies"])] or any(abs(a[1] - b[1]) > 0.02 for a, b in zip(nt, sorted(want["notifies"]))):
        bad.append("%s: notifies %s, expected %s" % (label, nt, want["notifies"]))


def main():
    bad = []
    d = os.path.join(COOKED, "Mod", "AltUI", "Anims")   # left over from a removed / test animation: bpgen and the iterative cook delete nothing
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.endswith(".uasset") and f[:-7] not in gen_anims.wanted():
            bad.append("%s: not in this build (removed or test only) - delete it in the kit (Content/Mod/AltUI/Anims) and in the cooked folder" % f[:-7])
    for n in gen_anims.wanted():
        want = json.load(open(os.path.join(gen_anims.OUT, n + ".json")))
        MODE = {"constant": animcurves.CONSTANT, "linear": animcurves.LINEAR, "cubic": animcurves.CUBIC}
        want["curves_eval"] = {cn: {"keys": [(t, v, 0.0, 0.0, MODE[m]) for t, v, m in ks], "pre": animcurves.X_CONSTANT, "post": animcurves.X_CONSTANT} for cn, ks in want["curves"].items()}
        ua = os.path.join(COOKED, "Mod", "AltUI", "Anims", n + ".uasset")
        if not os.path.exists(ua): bad.append("%s: not cooked" % n); continue
        compare(n, ua, n, want, bad)
        if not ANIMS[n].get("modifier"):   # a copy must equal the game's original (with a donor: plus the added curves)
            src = ANIMS[n]["source"]; sp = props(os.path.join(SRC, src + ".uasset"), src); sc = animcurves.read(os.path.join(SRC, src + ".uasset"))
            keep = {k: v for k, v in sc["curves"].items() if not (ANIMS[n].get("foot_phase") == "markers" and k == "MoveData_FootPhase")}
            orig = {"length": sp["SequenceLength"], "curves": keep, "curves_eval": keep, "markers": [[m["MarkerName"], m["Time"]] for m in sp["AuthoredSyncMarkers"]],
                    "notifies": [[x["NotifyName"], x["LinkValue"]] for x in sp["Notifies"]]}
            compare(n + " vs " + src, ua, n, orig, bad, subset=bool(ANIMS[n].get("donor")))
    if bad: print("VERIFY ANIMS FAILED"); [print("  " + b) for b in bad]; sys.exit(1)
    print("VERIFY ANIMS OK (%d animations)" % len(gen_anims.wanted()))


if __name__ == "__main__":
    main()
