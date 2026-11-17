#!/usr/bin/env python3
"""mod_ui_check.py - shared text IDs between the AltUI tables of installed mods (spec 2026-11-15-mod-table-text-ids).

Every text cell of a cooked DataTable carries a localization ID (namespace, key); the engine keeps one display string per ID, so
two mods with the same ID show one label for both - the one loaded last. A table filled from JSON/CSV gets namespace = table
name and key = <row>_<column>, and every mod names its tables AltUI_Entries / AltUI_Fields / AltUI_Actions / AltUI_Presets:
equal row names in two mods collide. This reads those four tables from every pak below the given folder (or the given paks)
and lists each ID that two paks use with different texts.

  python3 scripts/mod_ui_check.py <game>/TheKillingAntidote/Mods        # or single .pak files
  --ids   also list every text ID found (pak, table, row, namespace, key, text)
Exit code 1 if a collision was found.
"""
import argparse
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pakio import open_pak, norm_key
from uasset_pkg import Package
from uasset_props import Reader
from uasset_rows import read_table

TABLES = ("AltUI_Entries", "AltUI_Fields", "AltUI_Actions", "AltUI_Presets")
_MEMBER = re.compile(r"_\d+_[0-9A-F]{32}$")


def texts(value, path):
    """(path, ns, key, text) of every localized text in a parsed property value (culture-invariant texts have no ID)."""
    if isinstance(value, dict):
        if "ns" in value and "key" in value and "text" in value:
            yield path, value["ns"], value["key"], value["text"]
            return
        for k, v in value.items():
            k = _MEMBER.sub("", str(k))   # Label_8_5E50…: the member name of a user-defined struct without index and GUID
            yield from texts(v, path + "." + k if path else k)
    elif isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            yield from texts(v, "%s[%d]" % (path, i))


def table_texts(ua, ux):
    """[(row, column path, ns, key, text)] of one cooked DataTable (.uasset + .uexp bytes)."""
    pkg = Package.from_bytes(ua, ux)
    imps = [(im.class_package, im.class_name, im.outer, im.object_name) for im in pkg.imports]
    exps = [(e.object_name,) for e in pkg.exports]
    out = []
    for row in read_table(pkg).rows:
        name = row.name if not row.number else "%s_%d" % (row.name, row.number - 1)
        for path, ns, key, text in texts(Reader(row.data, pkg.names, imps, exps).props(), ""):
            out.append((name, path, ns, key, text))
    return out


def pak_texts(pak_path):
    """[(table asset path, row, column, ns, key, text)] of the AltUI tables in one pak; problems go to stderr."""
    out = []
    try:
        pak = open_pak(pak_path)
    except (Exception, SystemExit) as e:   # an encrypted pak without the game's exe nearby ends with SystemExit
        print("skipped %s: %s" % (pak_path, e), file=sys.stderr); return out
    with pak:
        for f in sorted(pak.files):
            base = os.path.basename(f)
            if not base.endswith(".uasset") or base[:-7] not in TABLES:
                continue
            try:
                ux_name = f[:-7] + ".uexp"
                ua = pak.read(f); ux = pak.read(ux_name) if ux_name in pak.files else b""
                asset = norm_key(pak.mount, f)[:-7]
                for row, col, ns, key, text in table_texts(ua, ux):
                    out.append((asset, row, col, ns, key, text))
            except Exception as e:
                print("unreadable %s in %s: %s" % (f, os.path.basename(pak_path), e), file=sys.stderr)
    return out


def collisions(found):
    """found: {pak: [(asset, row, col, ns, key, text)]} -> [((ns, key), [(pak, asset, row, col, text)])] with different texts in two paks."""
    by_id = defaultdict(list)
    for pak, cells in found.items():
        for asset, row, col, ns, key, text in cells:
            by_id[(ns, key)].append((pak, asset, row, col, text))
    out = []
    for tid, uses in sorted(by_id.items()):
        if len({u[0] for u in uses}) > 1 and len({u[4] for u in uses}) > 1:
            out.append((tid, uses))
    return out


def paks_below(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in sorted(files):
                    if f.lower().endswith(".pak"):
                        yield os.path.join(root, f)
        else:
            yield p


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+", help="Mods folder(s) or .pak files")
    ap.add_argument("--ids", action="store_true", help="list every text ID found")
    a = ap.parse_args(argv)
    found = {}
    for p in paks_below(a.paths):
        cells = pak_texts(p)
        if cells:
            found[os.path.relpath(p, a.paths[0]) if os.path.isdir(a.paths[0]) else os.path.basename(p)] = cells
    if a.ids:
        for pak, cells in sorted(found.items()):
            for asset, row, col, ns, key, text in cells:
                print("%s\t%s\t%s\t%s\t%s\t%s\t%s" % (pak, os.path.basename(asset), row, col, ns, key, text))
    hits = collisions(found)
    print("%d paks with AltUI tables, %d text cells, %d shared IDs with different texts" % (len(found), sum(len(c) for c in found.values()), len(hits)))
    for (ns, key), uses in hits:
        print("\n%s / %s" % (ns, key))
        for pak, asset, row, col, text in uses:
            print("  %s: %r  (row %s, %s)" % (pak, text, row, col))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
