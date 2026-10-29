#!/usr/bin/env python3
"""Idle mod converter: a pak that replaces Jodi's Female_Idle -> IdleAltUI_<Name>.pak (docs/specs/2026-10-13-idle-styles-design.md),
selectable in AltUI (Options > Move > Standing) next to the game's idles - and no longer a replacer: the game's own idle stays.

  idlepak.py <Replacer.pak> [--name Adjust] [--title "Display name"] [--out DIR] [--force] [--altui <AltUI.pak>]

Taken over: the animation (byte for byte, it keeps its object name), plus one child ABP of Jodi_Anim per walk / run combination,
copied from the templates in the installed AltUI.pak with the placeholder import pointed at the moved animation. Everything else in
the pak is skipped and listed. Standard library only at runtime."""
import os, sys, re, json, zlib, argparse
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import idle_mods as im, anim_templates
from bodypak import plain_entry, write_pak, verify, sha256_file, MOUNT_PREFIX, pkg_path, load_pkg, import_name
from weaponpak import asset_class, copy_package
from pakio import open_pak
from pak11_extract import Pak

ALTUI_REL = "steamapps/common/TheKillingAntidote/TheKillingAntidote/Mods/AltUI.pak"
# the usual install places; $GAME (the game folder TheKillingAntidote/TheKillingAntidote, as in config.sh) comes first when set
ALTUI_PAKS = ([os.path.join(os.environ["GAME"], "Mods", "AltUI.pak")] if os.environ.get("GAME") else []) + \
             [os.path.expanduser("~/.local/share/Steam/" + ALTUI_REL), os.path.expanduser("~/.steam/steam/" + ALTUI_REL), "C:/Program Files (x86)/Steam/" + ALTUI_REL]


def altui_pak(given=None):
    """The installed AltUI.pak - given, or the first of the usual install places that exists."""
    for p in ([given] if given else ALTUI_PAKS):
        if p and os.path.isfile(p): return p
    raise SystemExit("the idle templates come from AltUI itself: --altui <…/TheKillingAntidote/Mods/AltUI.pak>")


def retarget_template(ua, ux, mod):
    """A template's .uasset with its placeholder animation pointed at /Game/Mod/<mod>/Female_Idle (anim_templates.retarget)."""
    try: return anim_templates.retarget(ua, ux, {im.TEMPLATE_ANIM: ("/Game/Mod/%s/%s" % (mod, im.ANIM_NAME), im.ANIM_NAME)})
    except SystemExit as e:
        raise SystemExit("not an idle template (no import of %s)" % im.TEMPLATE_ANIM if "not a template" in str(e) else str(e))


def templates(altui):
    """{"<walk>_<run>": (uasset bytes, uexp bytes)} of every idle template in AltUI.pak."""
    out = anim_templates.read_templates(altui, im.TEMPLATE_PREFIX, im.TEMPLATE_DIR)
    if "Normal_Normal" not in out: raise SystemExit("%s has no idle templates - it is older than idle styles; update AltUI first" % altui)
    return out


def find_idle(pk):
    """Entry key of the pak's Female_Idle; refuses anything that is not a self-contained AnimSequence."""
    key = next((k for k in pk.files if (pkg_path(pk, k) or "").lower() == im.GAME_IDLE.lower()), None)
    if key is None: raise SystemExit("this pak does not replace %s" % im.GAME_IDLE)
    if asset_class(pk, key) != "AnimSequence": raise SystemExit("%s in this pak is no AnimSequence" % im.GAME_IDLE)
    own = {(pkg_path(pk, k) or "").lower() for k in pk.files} - {""}
    deps = [import_name(i) for i in load_pkg(pk, key).imports if i.class_name == "Package" and import_name(i).lower() in own]
    if deps: raise SystemExit("the animation imports other packages of the pak (%s) - not supported" % ", ".join(deps))
    return key


def convert(src, name=None, title=None, out_dir=None, force=False, altui=None):
    pk = open_pak(src)
    name = name or re.sub(r"[^A-Za-z0-9_]", "_", os.path.splitext(os.path.basename(src))[0])
    if not re.fullmatch(r"[A-Za-z0-9_]+", name): raise SystemExit("invalid name (allowed: A-Z a-z 0-9 _): " + name)
    mod = im.MOD_PREFIX + name; title = title or name
    out_dir = out_dir or os.path.dirname(os.path.abspath(src)); out_pak = os.path.join(out_dir, mod + ".pak")
    if os.path.exists(out_pak) and not force: raise SystemExit("target already exists (--force to overwrite): " + out_pak)
    key = find_idle(pk); tpl = templates(altui_pak(altui))
    entries = copy_package(pk, key, im.ANIM_NAME)
    for combo, (ua, ux) in sorted(tpl.items()):
        n = im.TEMPLATE_PREFIX + combo
        entries += [(n + ".uasset",) + plain_entry(retarget_template(ua, ux, mod)), (n + ".uexp",) + plain_entry(ux)]
    ma, mx = __import__("uasset_datatable").make_mod_table("/Game/Mod/" + mod, title, "Idle animation, converted from %s" % os.path.basename(src), []).write()
    entries += [("TKA_Mod_Table.uasset",) + plain_entry(ma), ("TKA_Mod_Table.uexp",) + plain_entry(mx)]
    keep = {key[:-len(".uasset")] + ext for ext in (".uasset", ".uexp", ".ubulk")}
    dropped = sorted(k.lstrip("/") for k in pk.files if k not in keep)
    comps = list(pk.comps) if isinstance(pk, Pak) else []
    os.makedirs(out_dir, exist_ok=True)
    write_pak(out_pak, MOUNT_PREFIX + mod + "/", comps, entries, zlib.crc32(mod.lower().encode()))
    errs = verify(out_pak, mod, entries)
    log = {"name": name, "mod": mod, "title": title, "templates": sorted(tpl), "source": os.path.abspath(src), "source_sha256": sha256_file(src),
           "pak": out_pak, "size": os.path.getsize(out_pak), "files": [rel for rel, _, _ in entries], "dropped": dropped, "verify": errs}
    with open(os.path.splitext(out_pak)[0] + "_build.json", "w") as f: json.dump(log, f, indent=1)
    if errs: raise SystemExit("verify failed: " + "; ".join(errs))
    return log


def main(argv=None):
    ap = argparse.ArgumentParser(description="Female_Idle replacer pak -> AltUI idle mod")
    ap.add_argument("src"); ap.add_argument("--name"); ap.add_argument("--title"); ap.add_argument("--out"); ap.add_argument("--force", action="store_true")
    ap.add_argument("--altui", help="the installed AltUI.pak (the idle templates come from there)")
    a = ap.parse_args(argv)
    log = convert(a.src, a.name, a.title, a.out, a.force, a.altui)
    print("%s  (%d bytes, templates: %s)" % (log["pak"], log["size"], ", ".join(log["templates"])))
    for k in log["dropped"]: print("  skipped:", k)


if __name__ == "__main__": main()
