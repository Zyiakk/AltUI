#!/usr/bin/env python3
"""bodybones – give a converted body mesh the bones of Jodi's own mesh that it lacks.

Some body mods were built against an older Female_Skeleton without the bones `Cam` and `Prop_R2` (80 instead of 82 bones:
Silly Face, UN Dv1/Dv2/Dv3A). With such a body Jodi's left hand stays off a gun: the left-hand IK of Jodi_Anim (TwoBoneIK
hand_l -> Prop_R_IK, alpha from the curve "Left Hand IK") does not take hold (docs/notes/2026-09-25-waffen-kacheln-und-skins.md).
This tool inserts every missing bone at the index it has in the game's mesh - name, parent and reference pose as there - and
renumbers what follows: RawRefBoneInfo (parents), RawRefBonePose, RawNameToIndexMap, and in every LOD RequiredBones (the new
bones are added: the game's mesh requires all its bones), the sections' BoneMaps and ActiveBoneIndices. Skin weights index into
the BoneMaps and stay as they are; nothing is weighted to the new bones.

  bodybones.py <Body_X.pak ...> [--check] [--game | --ref Female.uasset]      rewrites each pak in place (a .bak is kept)

Without --game / --ref the two bones known to be missing (Cam, Prop_R2) are inserted from built-in values (BUILTIN, taken from
the game's mesh) - no game install needed. --game / --ref compare against the whole game mesh (finds other gaps, if any).
"""
import os, sys, struct, zlib, shutil, argparse
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from uasset_pkg import Package
from uasset_props import Reader

GAME = os.environ.get("GAME")   # the game's installation folder (optional; found next to the source pak otherwise)
GAME_PAK = os.path.join(GAME, "Content/Paks/pakchunk0-WindowsNoEditor.pak") if GAME else None
REF_KEY = "Project/Character/Jodi/Body/Female"


# ---------------- reading the mesh ----------------
class Layout:
    """Offsets of everything bone-indexed in a cooked USkeletalMesh export (UE 4.27, cooked, LODs inlined)."""

    def __init__(self, pkg):
        self.pkg = pkg
        self.mesh = next(x for x in pkg.exports if x.class_index < 0 and pkg.imports[-x.class_index - 1].object_name == "SkeletalMesh")
        d = self.d = self.mesh.data
        r = Reader(d, pkg.names, pkg.imports, pkg.exports)
        while True:
            t = r.tag()
            if t is None: break
            r.p += t["size"]
        pos = r.p + 4 + 2 + 28                                                   # guid flag, strip flags, bounds
        nmat = struct.unpack_from("<i", d, pos)[0]
        self.skel = p = pos + 4 + nmat * 40                                       # FReferenceSkeleton
        n = struct.unpack_from("<i", d, p)[0]
        self.bones = []                                                           # (name, parent, name_number)
        for b in range(n):
            idx, num, par = struct.unpack_from("<iii", d, p + 4 + 12 * b); self.bones.append((pkg.names[idx], par, num))
        p += 4 + 12 * n
        if struct.unpack_from("<i", d, p)[0] != n: raise ValueError("RawRefBonePose count")
        self.poses = [d[p + 4 + 40 * b: p + 4 + 40 * (b + 1)] for b in range(n)]; p += 4 + 40 * n
        m = struct.unpack_from("<i", d, p)[0]; p += 4 + 12 * m                   # RawNameToIndexMap
        self.skel_end = p
        cooked, nlod = struct.unpack_from("<ii", d, p); p += 8
        if cooked != 1: raise ValueError("not a cooked mesh")
        self.arrays = []                                                          # (offset, kind) of every bone index array: req / map / act
        for _ in range(nlod):
            p += 2                                                                # strip flags
            cooked_out, inlined = struct.unpack_from("<ii", d, p); p += 8
            if cooked_out: raise ValueError("LOD cooked out")
            p = self._arr(p, "req")
            nsec = struct.unpack_from("<i", d, p)[0]; p += 4
            for _ in range(nsec):
                gflags, cflags = struct.unpack_from("<BB", d, p); p += 2
                p += 2 + 4 + 4 + 4 + 1 + 4 + 4                                    # MaterialIndex, BaseIndex, NumTriangles, bRecomputeTangent, mask channel, bCastShadow, BaseVertexIndex
                p += 4 + 64 * struct.unpack_from("<i", d, p)[0]                   # ClothMappingData
                p = self._arr(p, "map")
                p += 4 + 4 + 2 + 20                                               # NumVertices, MaxBoneInfluences, CorrespondClothAssetIndex, ClothingData
                if not (cflags & 1):
                    for es in (4, 8): p += 4 + es * struct.unpack_from("<i", d, p)[0]
                p += 4                                                            # bDisabled
            p = self._arr(p, "act")
            if nlod > 1 or not inlined:
                # the rest of an LOD (buffers) is not walked: one inlined LOD only (all converted bodies so far)
                raise NotImplementedError("only one inlined LOD is supported (found %d LODs, inlined=%d)" % (nlod, inlined))
        for off, kind in self.arrays:
            v = self.values(off)
            if any(v[i] >= v[i + 1] for i in range(len(v) - 1)) and kind != "map" or (v and max(v) >= n):
                raise ValueError("bone index array %s at %d not understood" % (kind, off))

    def _arr(self, p, kind):
        self.arrays.append((p, kind)); return p + 4 + 2 * struct.unpack_from("<i", self.d, p)[0]

    def values(self, off):
        n = struct.unpack_from("<i", self.d, off)[0]; return list(struct.unpack_from("<%dH" % n, self.d, off + 4))


# ---------------- the merge ----------------
def merged_order(mesh_names, ref_names):
    """New bone order: the mesh's bones, each missing reference bone inserted right after its predecessor in the reference.
    Requires the shared bones to keep the reference's relative order."""
    shared = [b for b in mesh_names if b in ref_names]
    if [b for b in ref_names if b in shared] != shared:
        raise ValueError("the mesh's bones are not in the order of the game's mesh")
    order = list(mesh_names)
    for i, b in enumerate(ref_names):
        if b in order: continue
        order.insert(0 if i == 0 else order.index(ref_names[i - 1]) + 1, b)
    return order


# The bones bodies built against an older Female_Skeleton lack, as in the game's Female mesh (UE 4.27, 2026-10): name, parent,
# predecessor in the bone list, reference pose (FTransform as cooked: rotation xyzw, translation, scale - 10 floats) and the
# name map hashes of the game's package. Built in, so the converter needs no game install (the source pak is usually somewhere
# in Downloads); --game / --ref compare against the whole game mesh instead.
BUILTIN = [
    ("Cam", "root", "root", "f604353ff104353f62c084b265c084320000000000000080000000000000803f0000803f0000803f", (10506, 11412)),
    ("Prop_R2", "hand_r", "Prop_R1", "e9d185bbe03f1fbd62d248bf3c731ebfcd80f5c077b45c40187bc5bcc9ff7f3f1600803f0800803f", (19041, 25677)),
]


def plan_builtin(names):
    """(order, new) for the built-in bones the mesh lacks; a bone is only added where its parent and predecessor exist."""
    order = list(names); new = {}
    for name, parent, after, pose, hashes in BUILTIN:
        k = name.lower()
        if k in order or parent.lower() not in order or after.lower() not in order: continue
        order.insert(order.index(after.lower()) + 1, k); new[k] = (name, parent.lower(), 0, bytes.fromhex(pose), hashes)
    return order, new


def plan_ref(lay, names, ref):
    """(order, new) for every bone of ref (Layout of the game's mesh) the mesh lacks; refuses meshes whose shared bones have
    other parents or another order than the game's."""
    ref_names = [b[0].lower() for b in ref.bones]
    for n, par, _ in lay.bones:                                                  # same parents as in the game for every shared bone
        if n.lower() in ref_names:
            rp = ref.bones[ref_names.index(n.lower())][1]
            if (ref_names[rp] if rp >= 0 else None) != (names[par] if par >= 0 else None):
                raise ValueError("bone %s has another parent than in the game's mesh" % n)
    order = merged_order(names, ref_names); new = {}
    for k in ref_names:
        if k in names: continue
        i = ref_names.index(k); name, par, num = ref.bones[i]
        hashes = ref.pkg.name_hashes[ref.pkg.names.index(name)] if name in ref.pkg.names else None
        new[k] = (name, ref_names[par] if par >= 0 else None, num, ref.poses[i], hashes)
    return order, new


def fill(pkg, ref=None):
    """Insert the bones pkg's mesh lacks: the built-in ones (BUILTIN), or with ref (Layout of the game's mesh) every bone of the
    game's mesh. Returns the added bone names ([] = nothing to do)."""
    lay = Layout(pkg); names = [b[0].lower() for b in lay.bones]               # FNames compare without case ("Root" = "root")
    order, new = plan_ref(lay, names, ref) if ref is not None else plan_builtin(names)
    if not new: return []
    new_index = {b: i for i, b in enumerate(order)}
    old_to_new = [new_index[b] for b in names]
    # reference skeleton
    info = b""; poses = b""; nmap = b""
    for i, b in enumerate(order):
        if b in new:
            name, parent_name, num, pose, hashes = new[b]
        else:
            k = names.index(b); name, par, num = lay.bones[k]; pose = lay.poses[k]; parent_name = names[par] if par >= 0 else None; hashes = None
        pi = new_index[parent_name] if parent_name is not None else -1
        if pi >= i: raise ValueError("parent of %s after it" % b)
        known = name in pkg.names; ni = pkg.name_index(name)
        if b in new and hashes is not None and not known:                       # a name new to the package: the game's hashes
            pkg.name_hashes[ni] = tuple(hashes)
        info += struct.pack("<iii", ni, num, pi); poses += pose; nmap += struct.pack("<iii", ni, num, i)
    n = len(order)
    skel = struct.pack("<i", n) + info + struct.pack("<i", n) + poses + struct.pack("<i", n) + nmap
    # bone index arrays after the skeleton
    d = lay.d; out = d[:lay.skel] + skel; p = lay.skel_end
    added = sorted(new_index[b] for b in new)
    for off, kind in lay.arrays:
        v = [old_to_new[x] for x in lay.values(off)]
        if kind == "req": v = sorted(set(v) | set(added))
        out += d[p:off] + struct.pack("<i", len(v)) + struct.pack("<%dH" % len(v), *v)
        p = off + 4 + 2 * struct.unpack_from("<i", d, off)[0]
    lay.mesh.data = out + d[p:]
    check = Layout(pkg)                                                         # the result must parse again, with the new bone list
    if [b[0].lower() for b in check.bones] != order: raise AssertionError("re-read bone list differs")
    return [new[b][0] for b in order if b in new]


def find_game_pak(near=None):
    """The game's main pak: $GAME, else the first TheKillingAntidote/Content/Paks above `near` (a source pak in the game's Mods
    or ~mods folder - how other users run bodypak.pyz), else None."""
    cands = [GAME_PAK] if GAME_PAK else []
    p = os.path.abspath(near) if near else None
    while p and os.path.dirname(p) != p:
        p = os.path.dirname(p)
        for sub in ("Content/Paks", "TheKillingAntidote/Content/Paks"):
            cands.append(os.path.join(p, sub, "pakchunk0-WindowsNoEditor.pak"))
    return next((c for c in cands if os.path.isfile(c)), None)


def load_ref(path=None, near=None):
    if path:
        return Layout(Package.load(path))
    from pak11_extract import Pak
    game_pak = find_game_pak(near)
    if not game_pak: raise FileNotFoundError("the game's pakchunk0-WindowsNoEditor.pak was not found (set GAME or convert a pak from the game's Mods folder)")
    pk = Pak(game_pak)
    key = next(k for k in pk.files if k.endswith(REF_KEY + ".uasset"))
    return Layout(Package.from_bytes(pk.read(key), pk.read(key[:-len(".uasset")] + ".uexp")))


# ---------------- body paks ----------------
def patch_pak(path, ref=None, check=False, backup=True):
    """Rewrite a converted body pak (BodyAltUI_X / Body_X) with the missing bones in its Female mesh. Returns the added bones."""
    from pakio import open_pak
    from bodypak import write_pak, raw_entry, plain_entry, verify
    with open_pak(path) as pk:   # closed before os.replace below: Windows refuses to replace a file that is still open
        mk = next(k for k in pk.files if k.lstrip("/") == "Female.uasset")
        pkg = Package.from_bytes(pk.read(mk), pk.read(mk[:-len(".uasset")] + ".uexp"))
        added = fill(pkg, ref)
        if not added or check: return added
        ua, ux = pkg.write()
        entries = []
        for k in sorted(pk.files):
            rel = k.lstrip("/")
            if rel == "Female.uasset": entries.append((rel,) + plain_entry(ua))
            elif rel == "Female.uexp": entries.append((rel,) + plain_entry(ux))
            else: entries.append((rel,) + raw_entry(pk, k))
        mount, comps = pk.mount, list(pk.comps)
    name = mount.rstrip("/").rsplit("/", 1)[-1]
    bak = path + ".bak"
    if backup and not os.path.exists(bak): shutil.copy2(path, bak)
    tmp = path + ".tmp"
    write_pak(tmp, mount, comps, entries, zlib.crc32(name.lower().encode()))
    errs = verify(tmp, name, entries)
    if errs:
        os.remove(tmp); raise SystemExit("verify failed: " + "; ".join(errs))
    os.replace(tmp, path)
    return added


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paks", nargs="+"); ap.add_argument("--ref", help="compare against this Female.uasset of the game instead of the built-in bones")
    ap.add_argument("--game", action="store_true", help="compare against the game's Female mesh (read from the game pak) instead of the built-in bones")
    ap.add_argument("--check", action="store_true", help="report only")
    a = ap.parse_args(argv)
    ref = load_ref(a.ref, near=a.paks[0]) if (a.ref or a.game) else None
    for p in a.paks:
        try:
            added = patch_pak(p, ref, a.check)
        except (ValueError, NotImplementedError) as e:
            print("%-28s skipped: %s" % (os.path.basename(p), e)); continue
        print("%-28s %s" % (os.path.basename(p), ("missing: " if a.check else "added: ") + ", ".join(added) if added else "complete"))


if __name__ == "__main__":
    main()
