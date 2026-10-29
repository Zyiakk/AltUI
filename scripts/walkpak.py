#!/usr/bin/env python3
"""Walk / run mod converter: a pak that replaces Jodi's Female_Walk and / or Female_Run -> WalkAltUI_<Name>.pak
(docs/specs/2026-10-27-walk-mods-design.md), selectable in AltUI (Options > Move > Walk style / Run style) next to the built-in
styles - and no longer a replacer: the game's own walk stays.

  walkpak.py <Replacer.pak> [--name Strut] [--title "Display name"] [--out DIR] [--force] [--altui <AltUI.pak>]

Taken over: the animations (byte for byte, they keep their object names) and the template ABPs of the installed AltUI.pak that fit
(walk -> ABP_AltUIWalkTpl_*, run -> ABP_AltUIRunTpl_*, both -> also ABP_AltUIWalkRunTpl_*), their placeholder imports pointed at the
moved animations. A loop without MoveData_Speed or Rotation Speed is refused. Everything else in the pak is skipped and listed.
Standard library only at runtime."""
import os, sys, re, json, zlib, argparse
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import walk_mods as wm, anim_templates
from idlepak import altui_pak
from bodypak import plain_entry, write_pak, verify, sha256_file, MOUNT_PREFIX, pkg_path, load_pkg, import_name
from weaponpak import asset_class, copy_package
from pakio import open_pak
from pak11_extract import Pak

SIDES = (("walk", wm.GAME_WALK, wm.ANIM_WALK, wm.TEMPLATE_WALK), ("run", wm.GAME_RUN, wm.ANIM_RUN, wm.TEMPLATE_RUN))


def find_anims(pk):
    """{"walk": key or None, "run": key or None} of the pak's Female_Walk / Female_Run; refuses a pak with neither, and anything that is
    not a self-contained AnimSequence."""
    paths = {(pkg_path(pk, k) or "").lower(): k for k in pk.files if k.endswith(".uasset")}
    own = set(paths) - {""}; out = {}
    for side, game, _, _ in SIDES:
        key = paths.get(game.lower()); out[side] = key
        if key is None: continue
        if asset_class(pk, key) != "AnimSequence": raise SystemExit("%s in this pak is no AnimSequence" % game)
        deps = [import_name(i) for i in load_pkg(pk, key).imports if i.class_name == "Package" and import_name(i).lower() in own]
        if deps: raise SystemExit("%s imports other packages of the pak (%s) - not supported" % (game, ", ".join(deps)))
    if not any(out.values()): raise SystemExit("this pak replaces neither %s nor %s" % (wm.GAME_WALK, wm.GAME_RUN))
    return out


def families(sides):
    """(template prefix, the sides its placeholders stand for) of the families a mod with these sides gets."""
    out = []
    if "walk" in sides: out.append((wm.WALK_PREFIX, ("walk",)))
    if "run" in sides: out.append((wm.RUN_PREFIX, ("run",)))
    if len(sides) == 2: out.append((wm.BOTH_PREFIX, ("walk", "run")))
    return out


def convert(src, name=None, title=None, out_dir=None, force=False, altui=None, check=True):
    pk = open_pak(src)
    name = name or re.sub(r"[^A-Za-z0-9_]", "_", os.path.splitext(os.path.basename(src))[0])
    if not re.fullmatch(r"[A-Za-z0-9_]+", name): raise SystemExit("invalid name (allowed: A-Z a-z 0-9 _): " + name)
    mod = wm.MOD_PREFIX + name; title = title or name
    out_dir = out_dir or os.path.dirname(os.path.abspath(src)); out_pak = os.path.join(out_dir, mod + ".pak")
    if os.path.exists(out_pak) and not force: raise SystemExit("target already exists (--force to overwrite): " + out_pak)
    keys = find_anims(pk); sides = [s for s, _, _, _ in SIDES if keys[s]]; game = {s: g for s, g, _, _ in SIDES}
    warnings, speed = [], {}
    if check:
        for s in sides:
            r = wm.check_anim(pk.read(keys[s]), pk.read(keys[s][:-len(".uasset")] + ".uexp"))
            if r["errors"]: raise SystemExit("%s: %s" % (game[s], "; ".join(r["errors"])))
            warnings += ["%s: %s" % (s, w) for w in r["warnings"]]; speed[s] = r["speed"]
    altui = altui_pak(altui); entries, made = [], []
    for s, _, anim, _ in SIDES:
        if keys[s]: entries += copy_package(pk, keys[s], anim)
    place = {s: (ph, ("/Game/Mod/%s/%s" % (mod, anim), anim)) for s, _, anim, ph in SIDES}
    for prefix, used in families(sides):
        tpl = anim_templates.read_templates(altui, prefix, wm.TEMPLATE_DIR)
        if not any(k.endswith("Normal") for k in tpl): raise SystemExit("%s has no walk mod templates - it is older than walk mods; update AltUI first" % altui)
        mapping = dict(place[s] for s in used)
        for combo, (ua, ux) in sorted(tpl.items()):
            n = prefix + combo
            entries += [(n + ".uasset",) + plain_entry(anim_templates.retarget(ua, ux, mapping)), (n + ".uexp",) + plain_entry(ux)]; made.append(n)
    desc = "Walk / run animation (%s), converted from %s" % (" + ".join(sides), os.path.basename(src))
    ma, mx = __import__("uasset_datatable").make_mod_table("/Game/Mod/" + mod, title, desc, []).write()
    entries += [("TKA_Mod_Table.uasset",) + plain_entry(ma), ("TKA_Mod_Table.uexp",) + plain_entry(mx)]
    keep = {keys[s][:-len(".uasset")] + ext for s in sides for ext in (".uasset", ".uexp", ".ubulk")}
    dropped = sorted(k.lstrip("/") for k in pk.files if k not in keep)
    comps = list(pk.comps) if isinstance(pk, Pak) else []
    os.makedirs(out_dir, exist_ok=True)
    write_pak(out_pak, MOUNT_PREFIX + mod + "/", comps, entries, zlib.crc32(mod.lower().encode()))
    errs = verify(out_pak, mod, entries)
    log = {"name": name, "mod": mod, "title": title, "sides": sides, "templates": made, "warnings": warnings, "speed": speed,
           "source": os.path.abspath(src), "source_sha256": sha256_file(src), "pak": out_pak, "size": os.path.getsize(out_pak),
           "files": [rel for rel, _, _ in entries], "dropped": dropped, "verify": errs}
    with open(os.path.splitext(out_pak)[0] + "_build.json", "w") as f: json.dump(log, f, indent=1)
    if errs: raise SystemExit("verify failed: " + "; ".join(errs))
    return log


def main(argv=None):
    ap = argparse.ArgumentParser(description="Female_Walk / Female_Run replacer pak -> AltUI walk / run mod")
    ap.add_argument("src"); ap.add_argument("--name"); ap.add_argument("--title"); ap.add_argument("--out"); ap.add_argument("--force", action="store_true")
    ap.add_argument("--altui", help="the installed AltUI.pak (the templates come from there)")
    a = ap.parse_args(argv)
    log = convert(a.src, a.name, a.title, a.out, a.force, a.altui)
    print("%s  (%d bytes, %s, %d templates)" % (log["pak"], log["size"], " + ".join(log["sides"]), len(log["templates"])))
    for s, v in log["speed"].items(): print("  %s speed: %.0f cm/s" % (s, v or 0))
    for w in log["warnings"]: print("  warning:", w)
    for k in log["dropped"]: print("  skipped:", k)


if __name__ == "__main__": main()
