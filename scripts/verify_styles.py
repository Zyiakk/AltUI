#!/usr/bin/env python3
"""verify_styles.py - checks the cooked walk / run / idle style ABPs, the idle templates and the walk mod templates (docs/specs/2026-10-06-move-styles-design.md): the CDO of every
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
    import idle_mods, walk_mods
    walk, run, idle = dict(gen_move.WALK_STYLES), dict(gen_move.RUN_STYLES), dict(gen_move.IDLE_STYLES); bad = []
    d = os.path.join(COOKED, "Mod", "AltUI")
    want = {p.rsplit("/", 1)[1] for p in list(gen_move.STYLE_ABPS.values()) + list(gen_move.TEMPLATE_ABPS.values()) + [p for p, _ in gen_move.WALKMOD_TEMPLATES.values()]}
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:   # bpgen and the iterative cook delete nothing: a removed style would ship
        if f.startswith(("ABP_AltUIStyle_", idle_mods.TEMPLATE_PREFIX, walk_mods.WALK_PREFIX, walk_mods.RUN_PREFIX, walk_mods.BOTH_PREFIX)) and f.endswith(".uasset") and f[:-7] not in want:
            bad.append("%s: left over from a removed style - delete it in the kit (Content/Mod/AltUI) and in the cooked folder" % f[:-7])
    checks = []
    for key, path in gen_move.STYLE_ABPS.items():
        w, r, i = key.split("_"); checks.append((key, path, {"walk": walk[w], "run": run[r], "idle": idle[i]}))
    for key, path in gen_move.TEMPLATE_ABPS.items():
        w, r = key.split("_"); checks.append(("template " + key, path, {"walk": walk[w], "run": run[r], "idle": idle_mods.TEMPLATE_ANIM}))
    node_side = {v: k for k, v in gen_move.STYLE_NODES.items()}
    for key, (path, ov) in gen_move.WALKMOD_TEMPLATES.items():
        checks.append(("walk mod template " + key, path, {node_side[n]: a for n, a in ov.items()}))
    for key, path, anims in sorted(checks):
        f = os.path.join(COOKED, path[len("/Game/"):] + ".uasset")
        if not os.path.exists(f): bad.append("%s: not cooked" % key); continue
        exp = {gen_move.STYLE_NODES[k]: a.rsplit("/", 1)[1] for k, a in anims.items() if a}
        props = cdo_props(f)
        if set(props) != set(exp): bad.append("%s: CDO props %s, expected %s" % (key, sorted(props), sorted(exp))); continue
        for node, anim in exp.items():
            v = props[node]
            if not isinstance(v, dict) or set(v) != {"Sequence"} or ("import:%s " % anim) not in str(v["Sequence"]):
                bad.append("%s: %s = %r, expected only Sequence = %s" % (key, node, v, anim))
    if bad:
        print("VERIFY STYLES FAILED"); [print("  " + b) for b in bad]; sys.exit(1)
    print("VERIFY STYLES OK (%d style ABPs, %d idle templates, %d walk mod templates)" % (len(gen_move.STYLE_ABPS), len(gen_move.TEMPLATE_ABPS), len(gen_move.WALKMOD_TEMPLATES)))


if __name__ == "__main__":
    main()
