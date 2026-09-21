#!/usr/bin/env python3
"""AltUI custom display names: export Saved/SaveGames/AltUI_Names.sav to JSON, edit, import it back.

    python3 altui_names.pyz export [AltUI_Names.sav] [-o names.json]
    python3 altui_names.pyz import names.json [AltUI_Names.sav]

Without the .sav path the game's default folder is used (Windows: %LOCALAPPDATA%\\TheKillingAntidote\\Saved\\SaveGames;
Linux/Proton: the Steam compatdata prefix). JSON sections: mods, groups, items, hair, skins, makeup – identifier -> display name.
import replaces all names (what is missing in the JSON is removed) and keeps the previous file as AltUI_Names.sav.bak.
Changes apply when the game is started next. Standard library only."""
import sys, os, json, shutil, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import savegame_gvas as gv

SECTIONS = [("mods", "mod"), ("groups", "group"), ("items", "item"), ("hair", "hair"), ("skins", "skin"), ("makeup", "makeup")]
SAV = "AltUI_Names.sav"
APPID = "2254890"


def candidates():
    """Possible SaveGames folders on this machine."""
    out = []
    la = os.environ.get("LOCALAPPDATA")
    if la:
        out.append(os.path.join(la, "TheKillingAntidote", "Saved", "SaveGames"))
    tail = os.path.join("steamapps", "compatdata", APPID, "pfx", "drive_c", "users", "steamuser", "AppData", "Local", "TheKillingAntidote", "Saved", "SaveGames")
    roots = [os.path.expanduser("~/.local/share/Steam"), os.path.expanduser("~/.steam/steam"), os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam")]
    for r in list(roots):
        vdf = os.path.join(r, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf):
            for line in open(vdf, encoding="utf-8", errors="replace"):
                line = line.strip()
                if line.startswith('"path"'):
                    roots.append(line.split('"')[3].replace("\\\\", "\\"))
    out += [os.path.join(r, tail) for r in roots]
    return out


def default_save_path():
    for d in candidates():
        if os.path.isdir(d):
            return os.path.join(d, SAV)
    return None


def to_json(sg):
    """The kind prefix is matched case-insensitively: FNames compare that way in the game, so the save holds "mod:" next to "Group:" /
    "Item:" / "Hair:" (whatever case the first writer used). The identifier keeps its case."""
    names = sg.get("Names", {}) or {}
    doc = {sec: {} for sec, _ in SECTIONS}
    for k, v in names.items():
        kind, sep, ident = str(k).partition(":")
        if not sep: continue
        for sec, want in SECTIONS:
            if kind.lower() == want:
                doc[sec][ident] = v
    return doc


def from_json(sg, doc):
    if not isinstance(doc, dict):
        raise ValueError("JSON must be an object with the sections " + ", ".join(s for s, _ in SECTIONS))
    names = {}
    for sec, kind in SECTIONS:
        part = doc.get(sec, {})
        if not isinstance(part, dict):
            raise ValueError("section %r must be an object (identifier -> name)" % sec)
        for ident, name in part.items():
            name = str(name).strip()
            if name and str(ident).strip():
                names["%s:%s" % (kind, str(ident).strip())] = name
    sg.set_map("Names", names)
    return len(names)


def cmd_export(sav, out):
    if os.path.exists(sav):
        doc = to_json(gv.load(sav))
    else:
        print("no %s yet – writing an empty template" % sav); doc = {sec: {} for sec, _ in SECTIONS}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2); f.write("\n")
    print("wrote %s (%s)" % (out, ", ".join("%s: %d" % (sec, len(doc[sec])) for sec, _ in SECTIONS)))


def cmd_import(src, sav):
    with open(src, encoding="utf-8") as f:
        doc = json.load(f)
    sg = gv.load(sav) if os.path.exists(sav) else gv.new_names_save()
    from_json(sg, doc)
    if os.path.exists(sav):
        shutil.copy2(sav, sav + ".bak")
    gv.save(sg, sav)
    names = sg.get("Names")
    print("wrote %s (%s)" % (sav, ", ".join("%s: %d" % (sec, sum(1 for k in names if k.startswith(kind + ":"))) for sec, kind in SECTIONS)))
    print("takes effect when the game is started next")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export"); e.add_argument("sav", nargs="?"); e.add_argument("-o", "--out", default="names.json")
    i = sub.add_parser("import"); i.add_argument("json"); i.add_argument("sav", nargs="?")
    a = ap.parse_args(argv)
    sav = a.sav or default_save_path()
    if not sav:
        sys.exit("AltUI_Names.sav not found – looked in:\n  " + "\n  ".join(candidates()) + "\ngive the path as an argument")
    try:
        if a.cmd == "export":
            cmd_export(sav, a.out)
        else:
            cmd_import(a.json, sav)
    except (ValueError, json.JSONDecodeError, OSError) as ex:
        sys.exit("error: %s" % ex)


if __name__ == "__main__":
    main()
