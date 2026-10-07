#!/usr/bin/env python3
"""verify_styles.py - checks the cooked walk / run style ABPs (docs/specs/2026-10-06-move-styles-design.md): the CDO of every
ABP_AltUIStyle_* may only carry the overridden loop players of Jodi_Anim, each with nothing but its new Sequence - anything else
would overwrite the game's values (the child's CDO is a delta against the real Jodi_Anim at runtime). Needs COOKED (config.sh)."""
import sys, os, json, subprocess
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "assets", "gen"))
import gen_move

COOKED = os.environ["COOKED"]


def cdo_props(path):
    out = subprocess.run([sys.executable, os.path.join(H, "uasset_props.py"), path], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    return next(v["props"] for k, v in d.items() if k.startswith("Default__"))


def main():
    walk, run = dict(gen_move.WALK_STYLES), dict(gen_move.RUN_STYLES); bad = []
    # a style taken out of the lists leaves its ABP behind (bpgen and the iterative cook delete nothing) - it would ship
    d = os.path.join(COOKED, "Mod", "AltUI"); want = {p.rsplit("/", 1)[1] for p in gen_move.STYLE_ABPS.values()}
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.startswith("ABP_AltUIStyle_") and f.endswith(".uasset") and f[:-7] not in want:
            bad.append("%s: left over from a removed style - delete it in the kit (Content/Mod/AltUI) and in the cooked folder" % f[:-7])
    for key, path in sorted(gen_move.STYLE_ABPS.items()):
        f = os.path.join(COOKED, path[len("/Game/"):] + ".uasset")
        if not os.path.exists(f): bad.append("%s: not cooked" % key); continue
        w, r = key.split("_")
        want = {}
        if walk[w]: want[gen_move.STYLE_NODES["walk"]] = walk[w].rsplit("/", 1)[1]
        if run[r]: want[gen_move.STYLE_NODES["run"]] = run[r].rsplit("/", 1)[1]
        props = cdo_props(f)
        if set(props) != set(want): bad.append("%s: CDO props %s, expected %s" % (key, sorted(props), sorted(want))); continue
        for node, anim in want.items():
            v = props[node]
            if not isinstance(v, dict) or set(v) != {"Sequence"} or ("import:%s " % anim) not in str(v["Sequence"]):
                bad.append("%s: %s = %r, expected only Sequence = %s" % (key, node, v, anim))
    if bad:
        print("VERIFY STYLES FAILED"); [print("  " + b) for b in bad]; sys.exit(1)
    print("VERIFY STYLES OK (%d style ABPs)" % len(gen_move.STYLE_ABPS))


if __name__ == "__main__":
    main()
