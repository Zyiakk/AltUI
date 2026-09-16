#!/usr/bin/env python3
"""open_pak(path): reader for any TKA mod pak - v11 (pak11_extract.Pak) or old v3..v8 unencrypted zlib/none paks (PakV3), same interface."""
import struct, zlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pak11_extract import Pak


class PakV3:
    """Minimal reader for old (v3..v8, unencrypted, zlib/none) paks, same interface as Pak."""

    def __init__(s, path):
        f = open(path, "rb"); s.f = f
        f.seek(0, 2); size = f.tell()
        found = False
        for flen in (45, 61, 77, 93, 109, 125, 141, 157, 173, 189, 205, 221):
            f.seek(size - flen); d = f.read(flen)
            for o in range(0, 25):
                if d[o:o + 4] == b"\xe1\x12\x6f\x5a":
                    s.ver = struct.unpack("<I", d[o + 4:o + 8])[0]
                    off, sz = struct.unpack("<QQ", d[o + 8:o + 24]); found = True; break
            if found:
                break
        if not found:
            raise Exception("no pak footer")
        s.enc = 0
        s.comps = ["Zlib"]
        f.seek(off); idx = f.read(sz)
        s.mount, pos = rstr3(idx, 0)
        n = struct.unpack("<i", idx[pos:pos + 4])[0]; pos += 4
        s.files = {}
        for i in range(n):
            name, pos = rstr3(idx, pos)
            eoff, esz, eusz = struct.unpack("<QQQ", idx[pos:pos + 24]); pos += 24
            comp = struct.unpack("<I", idx[pos:pos + 4])[0]; pos += 4
            if s.ver <= 1:
                pos += 8
            pos += 20
            blocks = []
            if comp != 0:
                nb = struct.unpack("<I", idx[pos:pos + 4])[0]; pos += 4
                for b in range(nb):
                    blocks.append(struct.unpack("<QQ", idx[pos:pos + 16])); pos += 16
            pos += 5
            s.files[name] = (eoff, esz, comp, blocks)

    def read(s, name):
        eoff, esz, comp, blocks = s.files[name]
        hdr = 53 + (len(blocks) * 16 + 4 if comp else 0)
        if comp == 0:
            s.f.seek(eoff + hdr); return s.f.read(esz)
        parts = []
        for (a, b) in blocks:
            s.f.seek(a if a >= eoff else eoff + a); parts.append(zlib.decompress(s.f.read(b - a)))  # offsets absolute or entry-relative
        return b"".join(parts)


def rstr3(b, pos):
    l = struct.unpack("<i", b[pos:pos + 4])[0]; pos += 4
    if l < 0:
        return b[pos:pos - 2 * l].decode("utf-16-le").rstrip("\0"), pos - 2 * l
    return b[pos:pos + l].decode("latin1").rstrip("\0"), pos + l


def open_pak(path):
    try:
        return Pak(path)
    except Exception:
        return PakV3(path)


def norm_key(mount, key):
    """Mount point + entry key -> path relative to the game root ("../../../TheKillingAntidote/Content/X/" + "/a.uasset" -> "TheKillingAntidote/Content/X/a.uasset")."""
    m = mount
    while m.startswith("../"):
        m = m[3:]
    return (m + key.lstrip("/")).replace("//", "/")
