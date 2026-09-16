#!/usr/bin/env python3
"""Lossless reading/writing of cooked UE 4.27 packages (.uasset + .uexp) as found in TKA mod paks.

Supported: unversioned cooked packages (FileVersionUE4 == 0), names, imports (28 B), exports (104 B),
depends, AssetRegistry block (raw), PreloadDependencies. Not supported (-> NotImplementedError):
GatherableText, SoftPackageReferences, SearchableNames, Thumbnails, WorldTileInfo, CompressedChunks.
On write all offsets are recomputed; .ubulk files stay untouched (offsets in them are
relative to BulkDataStartOffset, which is written along).
"""
import struct
from dataclasses import dataclass, field

PKG_TAG = 0x9E2A83C1
IMPORT_SIZE = 28
EXPORT_SIZE = 104


def read_fstr(b, pos):
    l = struct.unpack_from("<i", b, pos)[0]; pos += 4
    if l == 0:
        return "", pos
    if l < 0:
        return b[pos:pos - 2 * l].decode("utf-16-le").rstrip("\0"), pos - 2 * l
    return b[pos:pos + l].decode("latin1").rstrip("\0"), pos + l


def write_fstr(s):
    if s == "":
        return b"\0\0\0\0"
    if all(ord(c) < 128 for c in s):
        raw = s.encode("ascii") + b"\0"
        return struct.pack("<i", len(raw)) + raw
    raw = (s + "\0").encode("utf-16-le")
    return struct.pack("<i", -(len(raw) // 2)) + raw


@dataclass
class Import:
    class_package: str
    class_name: str
    outer: int
    object_name: str
    object_number: int = 0


@dataclass
class Export:
    class_index: int
    super_index: int
    template_index: int
    outer_index: int
    object_name: str
    object_number: int
    object_flags: int
    data: bytes
    forced_export: int = 0
    not_for_client: int = 0
    not_for_server: int = 0
    guid: bytes = b"\0" * 16
    package_flags: int = 0
    not_always_loaded: int = 1
    is_asset: int = 1
    deps_ser_before_ser: list = field(default_factory=list)
    deps_create_before_ser: list = field(default_factory=list)
    deps_ser_before_create: list = field(default_factory=list)
    deps_create_before_create: list = field(default_factory=list)


class Package:
    def __init__(self):
        self.legacy_file_version = -7
        self.legacy_ue3_version = 0
        self.file_version_ue4 = 0
        self.file_version_licensee = 0
        self.custom_versions = b"\0\0\0\0"   # raw block incl. count (empty = count 0)
        self.folder_name = "None"
        self.package_flags = 0x80000000
        self.guid = b"\0" * 16
        self.generations = []                # [(export_count, name_count)]
        self.saved_by = (0, 0, 0, 0, "")
        self.compatible_with = (0, 0, 0, 0, "")
        self.compression_flags = 0
        self.package_source = 0
        self.additional_packages = []
        self.chunk_ids = []
        self.names = []
        self.name_hashes = []
        self.imports = []
        self.exports = []
        self.depends = []
        self.asset_registry = b"\0\0\0\0"

    # ---------- read ----------
    @classmethod
    def load(cls, uasset_path):
        d = open(uasset_path, "rb").read()
        try:
            ux = open(uasset_path[:-7] + ".uexp", "rb").read()
        except FileNotFoundError:
            ux = b""
        return cls.from_bytes(d, ux)

    @classmethod
    def from_bytes(cls, d, ux):
        p = cls()
        pos = 0

        def i32():
            nonlocal pos
            v = struct.unpack_from("<i", d, pos)[0]; pos += 4; return v

        def i64():
            nonlocal pos
            v = struct.unpack_from("<q", d, pos)[0]; pos += 8; return v

        def fstr():
            nonlocal pos
            s, pos = read_fstr(d, pos); return s

        tag = struct.unpack_from("<I", d, 0)[0]; pos = 4
        if tag != PKG_TAG:
            raise ValueError("not a UE package (tag %08x)" % tag)
        p.legacy_file_version = i32()
        if p.legacy_file_version != -4:
            p.legacy_ue3_version = i32()
        p.file_version_ue4 = i32(); p.file_version_licensee = i32()
        if p.file_version_ue4 != 0:
            raise NotImplementedError("versioned package (FileVersionUE4=%d)" % p.file_version_ue4)
        ncv = i32(); p.custom_versions = d[pos - 4:pos + ncv * 20]; pos += ncv * 20
        total_header = i32()
        p.folder_name = fstr()
        p.package_flags = struct.unpack_from("<I", d, pos)[0]; pos += 4
        name_count, name_off = i32(), i32()
        gt_count, gt_off = i32(), i32()
        if gt_count:
            raise NotImplementedError("GatherableTextData")
        exp_count, exp_off = i32(), i32()
        imp_count, imp_off = i32(), i32()
        depends_off = i32()
        spr_count, spr_off = i32(), i32()
        if spr_count:
            raise NotImplementedError("SoftPackageReferences")
        searchable_off = i32(); thumb_off = i32()
        if searchable_off or thumb_off:
            raise NotImplementedError("SearchableNames/Thumbnails")
        p.guid = d[pos:pos + 16]; pos += 16
        ngen = i32(); p.generations = [(i32(), i32()) for _ in range(ngen)]
        for attr in ("saved_by", "compatible_with"):
            a, b, c = struct.unpack_from("<HHH", d, pos); pos += 6
            ch = i32(); s = fstr(); setattr(p, attr, (a, b, c, ch, s))
        p.compression_flags = struct.unpack_from("<I", d, pos)[0]; pos += 4
        if i32():
            raise NotImplementedError("CompressedChunks")
        p.package_source = struct.unpack_from("<I", d, pos)[0]; pos += 4
        nap = i32(); p.additional_packages = [fstr() for _ in range(nap)]
        asset_reg_off = i32(); bulk_start = i64(); wti_off = i32()
        if wti_off:
            raise NotImplementedError("WorldTileInfo")
        nch = i32(); p.chunk_ids = [i32() for _ in range(nch)]
        preload_count, preload_off = i32(), i32()
        # names
        pos = name_off
        for _ in range(name_count):
            s = fstr(); h = struct.unpack_from("<HH", d, pos); pos += 4
            p.names.append(s); p.name_hashes.append(h)

        def fname_at(q):
            i, n = struct.unpack_from("<ii", d, q)
            return p.names[i], n

        # imports
        pos = imp_off
        for _ in range(imp_count):
            cp, _n = fname_at(pos); cn, _n2 = fname_at(pos + 8)
            outer = struct.unpack_from("<i", d, pos + 16)[0]
            on, onum = fname_at(pos + 20)
            p.imports.append(Import(cp, cn, outer, on, onum)); pos += IMPORT_SIZE
        # exports
        pos = exp_off
        raw_exports = []
        for _ in range(exp_count):
            ci, si, ti, oi = struct.unpack_from("<iiii", d, pos)
            on, onum = fname_at(pos + 16)
            flags = struct.unpack_from("<I", d, pos + 24)[0]
            ssz, soff = struct.unpack_from("<qq", d, pos + 28)
            fe, nc, ns = struct.unpack_from("<iii", d, pos + 44)
            guid = d[pos + 56:pos + 72]
            pf, nal, isa, first, n1, n2, n3, n4 = struct.unpack_from("<Iiiiiiii", d, pos + 72)
            raw_exports.append((ci, si, ti, oi, on, onum, flags, ssz, soff, fe, nc, ns, guid, pf, nal, isa, first, n1, n2, n3, n4))
            pos += EXPORT_SIZE
        # depends
        pos = depends_off
        for _ in range(exp_count):
            n = i32(); p.depends.append([i32() for _ in range(n)])
        p.asset_registry = d[asset_reg_off:preload_off]
        preload = list(struct.unpack_from("<%di" % preload_count, d, preload_off))
        full = d + ux
        for (ci, si, ti, oi, on, onum, flags, ssz, soff, fe, nc, ns, guid, pf, nal, isa, first, n1, n2, n3, n4) in raw_exports:
            data = full[soff:soff + ssz]
            if len(data) != ssz:
                raise ValueError("export data incomplete (uexp missing?)")
            q = first if first >= 0 else 0
            deps = [preload[q:q + n1], preload[q + n1:q + n1 + n2], preload[q + n1 + n2:q + n1 + n2 + n3], preload[q + n1 + n2 + n3:q + n1 + n2 + n3 + n4]]
            p.exports.append(Export(ci, si, ti, oi, on, onum, flags, data, fe, nc, ns, guid, pf, nal, isa, *deps))
        if ux and ux[-4:] != struct.pack("<I", PKG_TAG):
            raise ValueError("uexp does not end with the package tag")
        p._total_header_check = total_header
        return p

    # ---------- helpers ----------
    def name_index(self, s):
        try:
            return self.names.index(s)
        except ValueError:
            self.names.append(s); self.name_hashes.append((0, 0)); return len(self.names) - 1

    def import_by_index(self, i):
        return self.imports[-i - 1]

    def find_import(self, class_name, object_name, outer=None):
        for k, im in enumerate(self.imports):
            if im.class_name == class_name and im.object_name == object_name and (outer is None or im.outer == outer):
                return -(k + 1)
        return 0

    def add_import(self, class_package, class_name, outer, object_name):
        self.imports.append(Import(class_package, class_name, outer, object_name)); return -len(self.imports)

    # ---------- write ----------
    def _fname(self, s, num=0):
        return struct.pack("<ii", self.name_index(s), num)

    def write(self):
        # the names of imports/exports must be known before the summary
        imp_bytes = b"".join(self._fname(im.class_package) + self._fname(im.class_name) + struct.pack("<i", im.outer) + self._fname(im.object_name, im.object_number) for im in self.imports)
        preload = []
        exp_meta = []
        for e in self.exports:
            first = len(preload) if (e.deps_ser_before_ser or e.deps_create_before_ser or e.deps_ser_before_create or e.deps_create_before_create) else -1
            preload += e.deps_ser_before_ser + e.deps_create_before_ser + e.deps_ser_before_create + e.deps_create_before_create
            exp_meta.append(first)
        names_bytes = b"".join(write_fstr(s) + struct.pack("<HH", *h) for s, h in zip(self.names, self.name_hashes))
        depends_bytes = b"".join(struct.pack("<i", len(dl)) + struct.pack("<%di" % len(dl), *dl) for dl in self.depends) or b""
        if len(self.depends) != len(self.exports):
            depends_bytes = b"\0\0\0\0" * len(self.exports)
        preload_bytes = struct.pack("<%di" % len(preload), *preload)

        def summary(name_off, imp_off, exp_off, dep_off, ar_off, pre_off, total, bulk_start):
            s = struct.pack("<Iii", PKG_TAG, self.legacy_file_version, self.legacy_ue3_version) if self.legacy_file_version != -4 else struct.pack("<Ii", PKG_TAG, self.legacy_file_version)
            s += struct.pack("<ii", self.file_version_ue4, self.file_version_licensee) + self.custom_versions
            s += struct.pack("<i", total) + write_fstr(self.folder_name) + struct.pack("<I", self.package_flags)
            s += struct.pack("<ii", len(self.names), name_off) + struct.pack("<ii", 0, 0)
            s += struct.pack("<ii", len(self.exports), exp_off) + struct.pack("<ii", len(self.imports), imp_off) + struct.pack("<i", dep_off)
            s += struct.pack("<ii", 0, 0) + struct.pack("<ii", 0, 0) + self.guid
            s += struct.pack("<i", len(self.generations)) + b"".join(struct.pack("<ii", *g) for g in self.generations)
            for (a, b, c, ch, br) in (self.saved_by, self.compatible_with):
                s += struct.pack("<HHHi", a, b, c, ch) + write_fstr(br)
            s += struct.pack("<Ii", self.compression_flags, 0) + struct.pack("<I", self.package_source)
            s += struct.pack("<i", len(self.additional_packages)) + b"".join(write_fstr(x) for x in self.additional_packages)
            s += struct.pack("<iqi", ar_off, bulk_start, 0)
            s += struct.pack("<i", len(self.chunk_ids)) + struct.pack("<%di" % len(self.chunk_ids), *self.chunk_ids)
            s += struct.pack("<ii", len(preload), pre_off)
            return s

        sum_len = len(summary(0, 0, 0, 0, 0, 0, 0, 0))
        name_off = sum_len
        imp_off = name_off + len(names_bytes)
        exp_off = imp_off + len(imp_bytes)
        dep_off = exp_off + EXPORT_SIZE * len(self.exports)
        ar_off = dep_off + len(depends_bytes)
        pre_off = ar_off + len(self.asset_registry)
        total = pre_off + len(preload_bytes)
        exp_bytes = b""; uexp = b""; soff = total
        for e, first in zip(self.exports, exp_meta):
            exp_bytes += struct.pack("<iiii", e.class_index, e.super_index, e.template_index, e.outer_index) + self._fname(e.object_name, e.object_number)
            exp_bytes += struct.pack("<Iqq", e.object_flags, len(e.data), soff)
            exp_bytes += struct.pack("<iii", e.forced_export, e.not_for_client, e.not_for_server) + e.guid
            exp_bytes += struct.pack("<Iiiiiiii", e.package_flags, e.not_always_loaded, e.is_asset, first, len(e.deps_ser_before_ser), len(e.deps_create_before_ser), len(e.deps_ser_before_create), len(e.deps_create_before_create))
            uexp += e.data; soff += len(e.data)
        bulk_start = soff
        # the name map may have grown through _fname() -> rebuild names_bytes and offsets (a second pass suffices since nothing is added afterwards)
        names_bytes = b"".join(write_fstr(s) + struct.pack("<HH", *h) for s, h in zip(self.names, self.name_hashes))
        imp_off = name_off + len(names_bytes); exp_off = imp_off + len(imp_bytes); dep_off = exp_off + len(exp_bytes)
        ar_off = dep_off + len(depends_bytes); pre_off = ar_off + len(self.asset_registry); total = pre_off + len(preload_bytes)
        if total != soff - sum(len(e.data) for e in self.exports):
            # the header size changed through new names -> adjust the export offsets
            delta = total - (soff - sum(len(e.data) for e in self.exports))
            fixed = b""
            for k in range(len(self.exports)):
                rec = exp_bytes[k * EXPORT_SIZE:(k + 1) * EXPORT_SIZE]
                so = struct.unpack_from("<q", rec, 36)[0] + delta
                fixed += rec[:36] + struct.pack("<q", so) + rec[44:]
            exp_bytes = fixed; bulk_start += delta
        head = summary(name_off, imp_off, exp_off, dep_off, ar_off, pre_off, total, bulk_start)
        assert len(head) == sum_len
        uasset = head + names_bytes + imp_bytes + exp_bytes + depends_bytes + self.asset_registry + preload_bytes
        assert len(uasset) == total
        return uasset, uexp + struct.pack("<I", PKG_TAG)

    def save(self, uasset_path):
        ua, ux = self.write()
        open(uasset_path, "wb").write(ua); open(uasset_path[:-7] + ".uexp", "wb").write(ux)
