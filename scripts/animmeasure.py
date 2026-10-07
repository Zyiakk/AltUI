#!/usr/bin/env python3
"""animmeasure.py - measurements of a walk cycle (assets/anim/blender/measure.py): stance speed, lateral foot position at contact,
lateral slide of the planted foot, lowest foot height, knee angles; with --compare a second animation side by side.
  scripts/animmeasure.py <anim.psa|anim.fbx> [--compare <anim>]"""
import os, sys, json, subprocess
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


BODY = os.path.join(W, "build", "kit", "female.fbx")


def measure(anim):
    spec = {"fbx": BODY}
    resolve(anim, spec)
    r = subprocess.run(["blender", "-b", "--factory-startup", "--python", os.path.join(W, "assets", "anim", "blender", "measure_cli.py"), "--", json.dumps(spec)], capture_output=True, text=True)
    line = next((l for l in r.stdout.splitlines() if l.startswith("MEASURE ")), None)
    if not line: sys.exit("MEASURE FAILED\n" + r.stdout[-3000:] + r.stderr[-2000:])
    return json.loads(line[8:])


def rows(m):
    out = [("speed (stance)", "%.1f cm/s" % m["speed"]), ("calf gap min", "%.1f cm" % m["calf_gap"]), ("thigh gap min", "%.1f cm" % m["thigh_gap"]), ("hand-thigh min", "%.1f cm" % m["hand_gap"]),
           ("elbow-spine min", "%.1f cm" % m["elbow_body"]), ("hand-spine min", "%.1f cm" % m["hand_body"])]
    for s in ("l", "r"):
        d = m[s]; out += [("%s lateral at contact" % s, "%+.1f cm" % d["lateral_contact"]), ("%s lateral slide" % s, "%.2f cm" % d["lateral_slide"]),
                          ("%s lowest z" % s, "%.2f cm" % d["lowest_z"]), ("%s knee min / max" % s, "%.0f / %.0f deg" % (d["knee_min"], d["knee_max"])),
                          ("%s stance frames" % s, "%d" % d["stance_frames"]),
                          ("%s knee sideways max/step" % s, "%.0f / %.0f deg" % (d["knee_off"], d["knee_off_step"]))]
    return out


if __name__ == "__main__":
    a = sys.argv[1:]; ms = [measure(a[0])] + ([measure(a[a.index("--compare") + 1])] if "--compare" in a else [])
    names = [os.path.basename(a[0])] + ([os.path.basename(a[a.index("--compare") + 1])] if "--compare" in a else [])
    print("%-24s" % "" + "".join("%-22s" % n[:21] for n in names))
    for i, (k, _) in enumerate(rows(ms[0])): print("%-24s" % k + "".join("%-22s" % rows(m)[i][1] for m in ms))
