#!/usr/bin/env python3
"""Weapon mod converter: a pak that replaces Project/Models/Weapon/<W>/… -> WeaponAltUI_<Name>.pak
(TKA mod: /Game/Mod/WeaponAltUI_<Name>/ + Mod_WeaponSkin and/or Mod_WeaponModel), selectable in AltUI (Weapons tab).

  weaponpak.py <Replacer.pak> [--name MySkin] [--title "Display name"] [--weapon UMP45] [--out DIR] [--force]

Taken over are the skin textures (with the item icon, if the pak replaces one) and the weapon meshes with everything
they reference inside the pak; a pak with both becomes one mod with one row per kind. Everything else is skipped and
listed in the log. Standard library only at runtime; pak reading/writing comes from bodypak."""
import os, sys, re, json, zlib, argparse
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import weapon_skins as ws
from bodypak import plain_entry, raw_entry, write_pak, verify, sha256_file, MOUNT_PREFIX, pkg_path, load_pkg, package_entries, import_name
from pakio import open_pak, norm_key
from pak11_extract import Pak
from uasset_datatable import new_datatable, name_prop, text_prop, object_prop, end_props, texture_import, finish_table


def make_skin_table(package_dir, row, weapon, caption, textures):
    """Mod_WeaponSkin with one row: weapon, caption and the texture references (missing ones stay unset)."""
    pkg, s = new_datatable(package_dir + "/" + ws.TABLE_NAME, ws.TABLE_NAME, ws.STRUCT_PATH, "S_WeaponSkin")
    data = b""
    for name, internal, typ in ws.struct_members():
        if typ == "name": data += name_prop(pkg, internal, weapon)
        elif typ == "text": data += text_prop(pkg, internal, caption)
        elif name in textures: data += object_prop(pkg, internal, texture_import(pkg, package_dir + "/" + textures[name]))
    return finish_table(pkg, s, [(row, data + end_props(pkg))])


def make_model_table(package_dir, row, weapon, caption, icon):
    """Mod_WeaponModel with one row: weapon, caption, icon. The meshes are not named here - the runtime looks for a
    package of the same name as the mesh it replaces, so magazine and optics need no column."""
    pkg, s = new_datatable(package_dir + "/" + ws.MODEL_TABLE_NAME, ws.MODEL_TABLE_NAME, ws.MODEL_STRUCT_PATH, "S_WeaponModel")
    data = b""
    for name, internal, typ in ws.model_struct_members():
        if typ == "name": data += name_prop(pkg, internal, weapon)
        elif typ == "text": data += text_prop(pkg, internal, caption)
        elif icon: data += object_prop(pkg, internal, texture_import(pkg, package_dir + "/" + icon))
    return finish_table(pkg, s, [(row, data + end_props(pkg))])


def weapon_rel(pk, key):
    """Path of an entry below Models/Weapon/ ("UMP45/Material/T_X.uasset"), whatever the pak's mount point is.
    A skin pak mounts on …/Content/Project/, a model pak on …/Content/Project/models/weapon/<W>/ - the entry keys
    differ, the full path does not."""
    p = norm_key(pk.mount, key).lower()
    i = p.find("models/weapon/")
    return p[i + len("models/weapon/"):] if i >= 0 else None


def asset_class(pk, key):
    """Class of a package's main export ("SkeletalMesh", "StaticMesh", "PhysicsAsset", "Skeleton", …).

    The main export is the one named like the package: a cooked StaticMesh carries its BodySetup and its NavCollision
    as exports ahead of the mesh itself, so the first export says nothing about what the package is."""
    pkg = load_pkg(pk, key)
    base = os.path.splitext(os.path.basename(key))[0].lower()
    first = None
    for e in pkg.exports:
        if e.class_index >= 0: continue
        cls = pkg.import_by_index(e.class_index).object_name
        if e.object_name.lower() == base: return cls
        first = first or cls
    return first


def copy_package(pk, key, rel):
    """Entries (rel + .uasset/.uexp/.ubulk) for one package, byte for byte: a texture references no other mod package,
    so nothing has to be rewritten - the package name comes from the path inside the mod pak."""
    out = []
    for ext in (".uasset", ".uexp", ".ubulk"):
        k = key[:-len(".uasset")] + ext
        if k in pk.files:
            out.append((rel + ext,) + (raw_entry(pk, k) if isinstance(pk, Pak) else plain_entry(pk.read(k))))
    return out


def mesh_plan(pk, meshes, mod):
    """{entry key: path in the mod pak} and the relocate map for package_entries.

    The meshes stay flat and keep their name: the runtime looks for a package named like the mesh it replaces, which is
    what makes magazine and optics come along without a column of their own. Everything they pull in from the pak (the
    physics asset, own materials and textures) keeps its subpath, so two meshes can share it."""
    in_pak = {}
    for k in pk.files:
        p = pkg_path(pk, k)
        if p: in_pak[p.lower()] = (k, p)
    target, rel, relocate = {}, {}, {}

    def plan(key, path, flat):
        t = "/Game/Mod/" + mod + ("/" + path.rsplit("/", 1)[1] if flat else path[len("/Game"):])
        target[key] = t; rel[key] = t[len("/Game/Mod/" + mod + "/"):]; relocate[path] = (key, t)

    for key in meshes: plan(key, pkg_path(pk, key), True)
    todo = list(meshes)
    while todo:
        for im in load_pkg(pk, todo.pop()).imports:
            if im.class_name != "Package": continue
            hit = in_pak.get(import_name(im).lower())
            if not hit: continue
            key, spelled = hit
            if key not in target:
                if asset_class(pk, key) == "Skeleton":
                    raise SystemExit("the pak brings its own skeleton (%s): the weapon would stand still in the game, "
                                     "because its animations are made for the skeleton of the original" % spelled)
                plan(key, spelled, False); todo.append(key)
            relocate[import_name(im)] = (key, target[key])   # packages spell a path as they like: rewrite every spelling
    return rel, relocate


def collect(pk, weapon=None):
    """Skin textures {role: entry key}, model meshes {entry key: package name}, the weapon and the item icon key;
    raises SystemExit on unusable input."""
    tex, meshes, icon_key, folders = {}, {}, None, set()
    for key in sorted(pk.files):
        if not key.lower().endswith(".uasset"): continue
        rel = weapon_rel(pk, key)
        if rel and "/" in rel:
            folder, tail = rel.split("/", 1)
            if tail.split("/")[0] == "material":
                role = ws.tex_role(tail)
                if role and role not in tex: tex[role] = key; folders.add(folder)
            elif asset_class(pk, key) in ws.MESH_CLASSES:
                meshes[key] = os.path.splitext(os.path.basename(key))[0]; folders.add(folder)
        elif icon_key is None and re.search(r"userinterface/items/item_icons_.+\.uasset$", norm_key(pk.mount, key).lower()):
            icon_key = key
    # a mesh that a mod ships twice (its own source variant in a subfolder next to the replacement): the packages stay
    # flat, so only one of them can carry the name - keep the one that sits where the game's own mesh sits, drop the
    # deeper one. Without this both end up under the same name and the pak fails its own verify.
    by_name = {}
    for key, base in meshes.items():
        rank = (weapon_rel(pk, key).count("/"), key)
        if base not in by_name or rank < by_name[base][0]: by_name[base] = (rank, key)
    meshes = {key: base for base, (_, key) in by_name.items()}
    if not tex and not meshes:
        raise SystemExit("no weapon textures or meshes in this pak (expected Models/Weapon/<weapon>/…)")
    if tex and "MainTex" not in tex:
        # a model mod whose own material set happens to end in _Normal / _ORM: that is no skin one could put on another
        # model, and the meshes take their textures along anyway. Only a pak without meshes has nothing usable left.
        if not meshes: raise SystemExit("the pak has skin textures but no base colour texture (…_BaseColor / _BC / _D)")
        tex = {}
    if weapon is None:
        cand = {ws.weapon_of_folder(f) for f in folders}
        if len(cand) != 1 or None in cand:
            raise SystemExit("cannot tell which weapon this is (folders: %s) - use --weapon <name>" % ", ".join(sorted(folders)))
        weapon = cand.pop()
    if weapon not in ws.WEAPONS: raise SystemExit("unknown weapon %r (known: %s)" % (weapon, ", ".join(ws.WEAPONS)))
    return tex, meshes, weapon, icon_key


def convert(src, name=None, title=None, out_dir=None, force=False, weapon=None):
    pk = open_pak(src)
    name = name or re.sub(r"[^A-Za-z0-9_]", "_", os.path.splitext(os.path.basename(src))[0])
    if not re.fullmatch(r"[A-Za-z0-9_]+", name): raise SystemExit("invalid name (allowed: A-Z a-z 0-9 _): " + name)
    mod = ws.MOD_PREFIX + name
    title = title or name
    out_dir = out_dir or os.path.dirname(os.path.abspath(src))
    out_pak = os.path.join(out_dir, mod + ".pak")
    if os.path.exists(out_pak) and not force: raise SystemExit("target already exists (--force to overwrite): " + out_pak)
    tex, meshes, weapon, icon_key = collect(pk, weapon)
    entries, names, taken = [], {}, []
    # the package keeps its original asset name: a cooked package's object is named after the source file, so renaming it
    # would make /Game/Mod/<mod>/<file>.<file> unresolvable (the reference then silently stays None)
    for role, key in sorted(tex.items()):
        rel = os.path.splitext(os.path.basename(key))[0]; names[role] = rel
        entries += copy_package(pk, key, rel); taken.append(key)
    if icon_key:
        rel = os.path.splitext(os.path.basename(icon_key))[0]; names["Icon"] = rel
        entries += copy_package(pk, icon_key, rel); taken.append(icon_key)
    mesh_rel, relocate = mesh_plan(pk, meshes, mod) if meshes else ({}, {})
    for key, rel in sorted(mesh_rel.items(), key=lambda kv: kv[1]):
        entries += package_entries(pk, key, rel, relocate); taken.append(key)
    if tex:
        ua, ux = make_skin_table("/Game/Mod/" + mod, name, weapon, title, names).write()
        entries.append((ws.TABLE_NAME + ".uasset",) + plain_entry(ua)); entries.append((ws.TABLE_NAME + ".uexp",) + plain_entry(ux))
    if meshes:
        ua, ux = make_model_table("/Game/Mod/" + mod, name, weapon, title, names.get("Icon")).write()
        entries.append((ws.MODEL_TABLE_NAME + ".uasset",) + plain_entry(ua)); entries.append((ws.MODEL_TABLE_NAME + ".uexp",) + plain_entry(ux))
    kind = "skin and model" if tex and meshes else ("skin" if tex else "model")
    ma, mx = __import__("uasset_datatable").make_mod_table("/Game/Mod/" + mod, title, "Weapon %s, converted from %s" % (kind, os.path.basename(src)), []).write()
    entries.append(("TKA_Mod_Table.uasset",) + plain_entry(ma)); entries.append(("TKA_Mod_Table.uexp",) + plain_entry(mx))
    keep = {k[:-len(".uasset")] + ext for k in taken for ext in (".uasset", ".uexp", ".ubulk")}
    dropped = sorted(k.lstrip("/") for k in pk.files if k not in keep)
    comps = list(pk.comps) if isinstance(pk, Pak) else []
    os.makedirs(out_dir, exist_ok=True)
    write_pak(out_pak, MOUNT_PREFIX + mod + "/", comps, entries, zlib.crc32(mod.lower().encode()))
    errs = verify(out_pak, mod, entries)
    log = {"name": name, "mod": mod, "title": title, "weapon": weapon, "textures": names, "meshes": sorted(meshes.values()),
           "companions": sorted(v for k, v in mesh_rel.items() if k not in meshes), "source": os.path.abspath(src),
           "source_sha256": sha256_file(src), "pak": out_pak, "size": os.path.getsize(out_pak),
           "files": [rel for rel, _, _ in entries], "dropped": dropped, "verify": errs}
    with open(os.path.splitext(out_pak)[0] + "_build.json", "w") as f: json.dump(log, f, indent=1)
    if errs: raise SystemExit("verify failed: " + "; ".join(errs))
    return log


def main(argv=None):
    ap = argparse.ArgumentParser(description="Weapon replacer pak -> AltUI weapon mod (skin and/or model)")
    ap.add_argument("src"); ap.add_argument("--name"); ap.add_argument("--title"); ap.add_argument("--weapon"); ap.add_argument("--out"); ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    log = convert(a.src, a.name, a.title, a.out, a.force, a.weapon)
    print("%s  (%s, %d bytes)" % (log["pak"], log["weapon"], log["size"]))
    if log["meshes"]: print("  meshes:", ", ".join(log["meshes"]))
    for k in log["dropped"]: print("  skipped:", k)


if __name__ == "__main__": main()
