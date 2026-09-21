#!/usr/bin/env python3
"""Body mod converter: original body pak (replaces Project/Character/Jodi/Body/Female) -> Body_<Name>.pak
(TKA mod: /Game/Mod/Body_<Name>/Female + TKA_Mod_Table), selectable in AltUI (Body Shape tab).

  bodypak.py <Original.pak> [--name Body_X] [--title "Display name"] [--out DIR] [--force]

Writes a pak v11 (format of the kit's UnrealPak). v11 sources: compressed blocks are copied byte-identically (no Oodle needed);
v3–v8 sources (zlib/none): extracted and stored uncompressed. Standard library only at runtime.
Format reference: Engine/Source/Runtime/PakFile (FPakInfo::Serialize, FPakFile::EncodePakEntry, AddEntryToIndex, HashPath).
"""
import os, sys, re, json, struct, hashlib, zlib, argparse
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from pak11_extract import Pak
from pakio import open_pak, norm_key
from uasset_datatable import make_mod_table, make_body_scale_table
from uasset_pkg import Package
import bodypak_abp
import bodyscale_groups as bg

MAGIC = 0x5A6F12E1; VERSION = 11
MOUNT_PREFIX = "../../../TheKillingAntidote/Content/Mod/"
CONTENT = "TheKillingAntidote/Content/"
MESH_SUFFIX = "project/character/jodi/body/female.uasset"


def fstr(s):
    """FString, ASCII (length incl. null byte)."""
    b = s.encode("ascii") + b"\0"; return struct.pack("<i", len(b)) + b


def path_hash(rel, seed):
    """FPakFile::HashPath (v11): FFnv::MemFnv64 over the lower-cased relative path as UTF-16LE."""
    h = (0xcbf29ce484222325 + seed) & 0xFFFFFFFFFFFFFFFF
    for b in rel.lower().encode("utf-16-le"):
        h ^= b; h = (h * 0x00000100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h


def encode_entry(off, e):
    """FPakFile::EncodePakEntry: e = dict(usz, sz, comp, bs, blocks[(start, end) relative to the entry])."""
    if max(off, e["sz"], e["usz"]) > 0xFFFFFFFF:
        raise SystemExit("pak > 4 GB is not supported")
    nblk = len(e["blocks"]) if e["comp"] else 0
    bs_packed = (e["bs"] >> 11) & 0x3F
    if (bs_packed << 11) != e["bs"]:
        bs_packed = 0x3F
    flags = (1 << 31) | (1 << 30) | (1 << 29) | (e["comp"] << 23) | (nblk << 6) | bs_packed
    out = struct.pack("<I", flags)
    if bs_packed == 0x3F:
        out += struct.pack("<I", e["bs"])
    out += struct.pack("<II", off, e["usz"])
    if e["comp"]:
        out += struct.pack("<I", e["sz"])
        if nblk > 1:
            out += b"".join(struct.pack("<I", b - a) for a, b in e["blocks"])
    return out


def dir_index(locs):
    """FullDirectoryIndex: {dir: {file: encoded offset}}; root '/', subdirs 'A/B/', parents as empty entries (FPakFile::AddEntryToIndex)."""
    dirs = {"/": {}}
    for rel, loc in locs:
        d, _, f = rel.rpartition("/")
        d = d + "/" if d else "/"
        dirs.setdefault(d, {})[f] = loc
        while d != "/":
            d = d[:-1].rpartition("/")[0]; d = d + "/" if d else "/"
            dirs.setdefault(d, {})
    out = struct.pack("<i", len(dirs))
    for d, files in dirs.items():
        out += fstr(d) + struct.pack("<i", len(files)) + b"".join(fstr(f) + struct.pack("<i", loc) for f, loc in files.items())
    return out


def plain_entry(data):
    """Uncompressed entry: FPakEntry header (offset 0, SHA1 of the data, flags 0, block size 0) + data."""
    hdr = struct.pack("<qqqI", 0, len(data), len(data), 0) + hashlib.sha1(data).digest() + b"\0" + struct.pack("<I", 0)
    return hdr + data, dict(usz=len(data), sz=len(data), comp=0, bs=0, blocks=[])


def raw_entry(pk, key):
    """Data region (header + blocks) of a v11 entry, byte-identical; block offsets are relative and stay valid."""
    en = pk.entry(pk.files[key])
    if en["encr"]:
        raise SystemExit("encrypted entries are not supported: " + key)
    length = en["blocks"][-1][1] if en["comp"] else en["hdr"] + en["sz"]
    pk.f.seek(en["off"]); region = pk.f.read(length)
    if len(region) != length:
        raise SystemExit("pak truncated at " + key)
    return region, dict(usz=en["usz"], sz=en["sz"], comp=en["comp"], bs=en["bs"], blocks=en["blocks"])


def write_pak(out_path, mount, comps, entries, seed):
    """Pak v11, unencrypted: data, primary index, path hash index, directory index, footer. entries = [(relpath, region, e)]."""
    data = b""; encoded = b""; locs = []
    for rel, region, e in entries:
        locs.append((rel, len(encoded))); encoded += encode_entry(len(data), e); data += region
    ph = struct.pack("<i", len(locs)) + b"".join(struct.pack("<Qi", path_hash(rel, seed), loc) for rel, loc in locs)
    fd = dir_index(locs)
    idx_off = len(data)
    head = fstr(mount) + struct.pack("<iQ", len(locs), seed)
    primary_len = len(head) + (4 + 8 + 8 + 20) * 2 + 4 + len(encoded) + 4
    ph_off = idx_off + primary_len; fd_off = ph_off + len(ph)
    primary = head + struct.pack("<iQQ", 1, ph_off, len(ph)) + hashlib.sha1(ph).digest() \
        + struct.pack("<iQQ", 1, fd_off, len(fd)) + hashlib.sha1(fd).digest() \
        + struct.pack("<i", len(encoded)) + encoded + struct.pack("<i", 0)   # FilesNum = 0 (all entries encoded)
    assert len(primary) == primary_len
    names = (list(comps) + [""] * 5)[:5]
    footer = b"\0" * 16 + b"\0" + struct.pack("<Ii", MAGIC, VERSION) + struct.pack("<qq", idx_off, len(primary)) \
        + hashlib.sha1(primary).digest() + b"".join(n.encode("ascii").ljust(32, b"\0") for n in names)
    assert len(footer) == 221
    with open(out_path, "wb") as f:
        f.write(data); f.write(primary); f.write(ph); f.write(fd); f.write(footer)


def derive_name(src):
    base = os.path.basename(src)
    if base.lower().endswith(".pak"):
        base = base[:-4]
    base = re.sub(r"[^A-Za-z0-9_]", "_", base)
    return base if base.startswith("Body_") else "Body_" + base


def find_mesh(pk):
    """Key of the file whose full path ends in Project/Character/Jodi/Body/Female.uasset."""
    for key in pk.files:
        if norm_key(pk.mount, key).lower().endswith(MESH_SUFFIX):
            return key
    raise SystemExit("no body mesh (…/Project/Character/Jodi/Body/Female.uasset) in this pak")


def pkg_path(pk, key):
    """Entry key -> package path ("/Game/Project/.../TESTABP") for .uasset entries under Content/, else None."""
    p = norm_key(pk.mount, key)
    if p.lower().startswith(CONTENT.lower()) and p.lower().endswith(".uasset"):
        return "/Game/" + p[len(CONTENT):-len(".uasset")]


def load_pkg(pk, key):
    ux_key = key[:-len(".uasset")] + ".uexp"
    return Package.from_bytes(pk.read(key), pk.read(ux_key) if ux_key in pk.files else b"")


def companions(pk, mesh_key, name):
    """Packages of the source pak that the mesh imports, transitively (a body's own PostProcessAnimBlueprint, materials …).
    They move into the mod folder: /Game/X/Y -> /Game/Mod/<name>/X/Y. Returns {old package path: (entry key, new package path)}."""
    by_pkg = {}
    for k in pk.files:
        p = pkg_path(pk, k)
        if p and k != mesh_key:
            by_pkg[p] = k
    found = {}; todo = [mesh_key]
    while todo:
        for im in load_pkg(pk, todo.pop()).imports:
            if im.class_name == "Package" and im.object_name in by_pkg and im.object_name not in found:
                found[im.object_name] = (by_pkg[im.object_name], "/Game/Mod/" + name + im.object_name[len("/Game"):])
                todo.append(by_pkg[im.object_name])
    return found


def package_entries(pk, key, rel, relocate):
    """Entries (rel + .uasset/.uexp/.ubulk) for one package. Imports of relocated packages are rewritten (new name appended to the
    name table, so the export data's name indices stay valid); untouched packages are copied byte-identically."""
    out = []
    pkg = load_pkg(pk, key)
    hits = [im for im in pkg.imports if im.class_name == "Package" and im.object_name in relocate]
    if hits:
        for im in hits:
            im.object_name = relocate[im.object_name][1]
        ua, ux = pkg.write()
        if ux != pk.read(key[:-len(".uasset")] + ".uexp"):
            raise SystemExit("rewriting %s changed its export data" % key)
        out.append((rel + ".uasset",) + plain_entry(ua))
    else:
        out.append((rel + ".uasset",) + (raw_entry(pk, key) if isinstance(pk, Pak) else plain_entry(pk.read(key))))
    for ext in (".uexp", ".ubulk"):
        k = key[:-len(".uasset")] + ext
        if k in pk.files:
            out.append((rel + ext,) + (raw_entry(pk, k) if isinstance(pk, Pak) else plain_entry(pk.read(k))))
    return out


def verify(out_pak, name, entries):
    errs = []
    pk = Pak(out_pak)
    if pk.mount != MOUNT_PREFIX + name + "/":
        errs.append("mount point: " + pk.mount)
    for rel, region, e in entries:
        key = rel if "/" in rel else "/" + rel     # Pak keys: root files "/X", subdirectory files "A/B/X"
        if key not in pk.files:
            errs.append("missing: " + rel); continue
        en = pk.entry(pk.files[key]); pk.f.seek(en["off"])
        if pk.f.read(len(region)) != region:
            errs.append("data differs: " + rel)
        if (en["usz"], en["sz"], en["comp"]) != (e["usz"], e["sz"], e["comp"]):
            errs.append("entry differs: " + rel)
    if len(pk.files) != len(entries):
        errs.append("file count %d != %d" % (len(pk.files), len(entries)))
    return errs


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def convert(src, name=None, title=None, out_dir=None, force=False, keep_abp=False):
    pk = open_pak(src)
    name = name or derive_name(src)
    if not re.fullmatch(r"Body_[A-Za-z0-9_]+", name):
        raise SystemExit("invalid name (allowed: Body_[A-Za-z0-9_]+): " + name)
    title = title or name[len("Body_"):]
    out_dir = out_dir or os.path.dirname(os.path.abspath(src))
    out_pak = os.path.join(out_dir, name + ".pak")
    if os.path.exists(out_pak) and not force:
        raise SystemExit("target already exists (--force to overwrite): " + out_pak)
    mesh_key = find_mesh(pk)
    warnings = []; defaults = None; abp = "kept"
    relocate = companions(pk, mesh_key, name)          # before attach_abp: the mod's own ABP package is still referenced under its old path
    if keep_abp:
        entries = package_entries(pk, mesh_key, "Female", relocate)
        for old, (key, new) in sorted(relocate.items()):
            entries += package_entries(pk, key, new[len("/Game/Mod/" + name + "/"):], relocate)
        taken_keys = [mesh_key] + [k for k, _ in relocate.values()]
    else:
        abp = "AltUI"
        mesh = load_pkg(pk, mesh_key)
        had_abp, old_pkg = bodypak_abp.attach_abp(mesh)
        defaults = {v: [1.0, 1.0, 1.0] for v, _, _ in bg.GROUPS}
        if had_abp:
            if old_pkg in relocate:
                k = relocate[old_pkg][0]; defaults, warnings = bodypak_abp.read_abp_defaults(pk.read(k), pk.read(k[:-len(".uasset")] + ".uexp"))
            else:
                warnings.append("the mesh's animation blueprint %s is not in this pak - defaults 1.0" % old_pkg)
        other = {k: v for k, v in relocate.items() if k != old_pkg}   # materials etc. still travel along; the replaced ABP does not
        for im in mesh.imports:
            if im.class_name == "Package" and im.object_name in other:
                im.object_name = other[im.object_name][1]
        ua, ux = mesh.write()
        ux_key = mesh_key[:-len(".uasset")] + ".uexp"
        if had_abp and ux != pk.read(ux_key):
            raise SystemExit("rewriting the ABP import changed the mesh's export data")
        entries = [("Female.uasset",) + plain_entry(ua)]
        if had_abp:
            entries.append(("Female.uexp",) + (raw_entry(pk, ux_key) if isinstance(pk, Pak) else plain_entry(ux)))
        else:
            entries.append(("Female.uexp",) + plain_entry(ux))        # tag inserted -> export data changed, stored uncompressed
        bk = mesh_key[:-len(".uasset")] + ".ubulk"
        if bk in pk.files:
            entries.append(("Female.ubulk",) + (raw_entry(pk, bk) if isinstance(pk, Pak) else plain_entry(pk.read(bk))))
        for old, (key, new) in sorted(other.items()):
            entries += package_entries(pk, key, new[len("/Game/Mod/" + name + "/"):], other)
        sa, sx = make_body_scale_table("/Game/Mod/" + name, defaults).write()
        entries.append(("Body_Scale.uasset",) + plain_entry(sa)); entries.append(("Body_Scale.uexp",) + plain_entry(sx))
        taken_keys = [mesh_key] + [k for k, _ in other.values()] + ([relocate[old_pkg][0]] if had_abp and old_pkg in relocate else [])
        relocate = other
    taken = {key[:-len(".uasset")] + ext for key in taken_keys for ext in (".uasset", ".uexp", ".ubulk")}
    dropped = sorted(k.lstrip("/") for k in pk.files if k not in taken)
    ua, ux = make_mod_table("/Game/Mod/" + name, title, "Body mod, converted from " + os.path.basename(src), []).write()
    entries.append(("TKA_Mod_Table.uasset",) + plain_entry(ua)); entries.append(("TKA_Mod_Table.uexp",) + plain_entry(ux))
    comps = list(pk.comps) if isinstance(pk, Pak) else []
    os.makedirs(out_dir, exist_ok=True)
    write_pak(out_pak, MOUNT_PREFIX + name + "/", comps, entries, zlib.crc32(name.lower().encode()))
    errs = verify(out_pak, name, entries)
    log = {"name": name, "title": title, "source": os.path.abspath(src), "source_sha256": sha256_file(src), "source_pak_version": pk.ver,
           "pak": out_pak, "size": os.path.getsize(out_pak), "files": [rel for rel, _, _ in entries],
           "companions": {old: new for old, (_, new) in relocate.items()}, "dropped": dropped, "abp": abp, "warnings": warnings,
           "verify": errs, "status": "ok" if not errs else "verify-failed"}
    if defaults is not None:
        log["scale_defaults"] = defaults
    json.dump(log, open(os.path.join(out_dir, name + "_convert.json"), "w"), indent=1, ensure_ascii=False)
    if errs:
        raise SystemExit("verify failed: " + "; ".join(errs))
    return out_pak, log


def main(argv=None):
    ap = argparse.ArgumentParser(description="Body mod pak -> Body_<Name>.pak for AltUI")
    ap.add_argument("pak"); ap.add_argument("--name"); ap.add_argument("--title"); ap.add_argument("--out"); ap.add_argument("--force", action="store_true")
    ap.add_argument("--keep-abp", action="store_true", help="keep the mod's own post-process animation blueprint (no Body Shape sliders, works without AltUI)")
    a = ap.parse_args(argv)
    out, log = convert(a.pak, a.name, a.title, a.out, a.force, a.keep_abp)
    print("%s (%d bytes, %s) -> copy to <game>/TheKillingAntidote/Mods/" % (out, log["size"], ", ".join(log["files"])))
    if log["abp"] == "AltUI":
        custom = ", ".join("%s=%s" % (k, "/".join("%.2f" % x for x in v)) for k, v in log["scale_defaults"].items() if v != [1.0, 1.0, 1.0])
        print("post-process blueprint: AltUI ABP_BodyScale (Body Shape sliders); defaults: " + (custom or "all 1.0"))
    for w_ in log["warnings"]:
        print("warning: " + w_)
    for old, new in sorted(log["companions"].items()):
        print("companion asset used by the mesh: %s -> %s" % (old, new))
    if log["dropped"]:
        print("not used by the mesh, left out: " + ", ".join(log["dropped"]))


if __name__ == "__main__":
    main()
