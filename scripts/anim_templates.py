#!/usr/bin/env python3
"""Template ABPs of AltUI (child ABPs of Jodi_Anim whose players point at placeholder animations) copied into a mod: the placeholder
imports (package + object) rewritten, the export data byte for byte. Shared by idlepak and walkpak. Standard library only."""
from uasset_pkg import Package
from bodypak import pkg_path, import_name
from pakio import open_pak


def retarget(ua, ux, mapping):
    """A template's .uasset with every placeholder in mapping ({placeholder package path: (new package path, new object name)}) pointed
    at its new animation. New names are appended to the name table, so the name indices of the export data stay valid."""
    pkg = Package.from_bytes(ua, ux); hits = set()
    objs = {p.rsplit("/", 1)[1]: p for p in mapping}
    for i in pkg.imports:
        n = import_name(i)
        if i.class_name == "Package" and n in mapping:
            i.object_name = mapping[n][0]; i.object_number = 0; hits.add(("pkg", n))
        elif i.class_name == "AnimSequence" and n in objs:
            i.object_name = mapping[objs[n]][1]; i.object_number = 0; hits.add(("obj", objs[n]))
    missing = [p for p in mapping if ("pkg", p) not in hits or ("obj", p) not in hits]
    if missing: raise SystemExit("not a template for %s (no import of it)" % ", ".join(missing))
    ua2, ux2 = pkg.write()
    if ux2 != ux: raise SystemExit("rewriting the template changed its export data")
    return ua2


def read_templates(altui, prefix, template_dir):
    """{name without prefix: (uasset bytes, uexp bytes)} of every template <template_dir>/<prefix>* in AltUI.pak."""
    pk = open_pak(altui); out = {}
    for k in sorted(pk.files):
        p = pkg_path(pk, k) or ""
        if p.startswith(template_dir + "/" + prefix):
            out[p.rsplit("/", 1)[1][len(prefix):]] = (pk.read(k), pk.read(k[:-len(".uasset")] + ".uexp"))
    return out
