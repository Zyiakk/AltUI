import struct, sys, re, os, zlib, ctypes

KEY = bytes.fromhex("020B81BE21191FCBDAE94F381EBB525F6F5556FCEA51243C99D26E42481D968D")


def aes(b):
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes   # only for encrypted paks (game paks); mod paks are unencrypted
    d = Cipher(algorithms.AES(KEY), modes.ECB()).decryptor()
    return d.update(b) + d.finalize()


def rstr(b, pos):
    l = struct.unpack("<i", b[pos:pos + 4])[0]
    pos += 4
    if l < 0:
        s = b[pos:pos - 2 * l].decode("utf-16-le").rstrip("\0")
        pos += -2 * l
    else:
        s = b[pos:pos + l].decode("latin1").rstrip("\0")
        pos += l
    return s, pos


_ooz = None


def oodle(d, usz):
    global _ooz
    if _ooz is None:
        _ooz = ctypes.CDLL(os.environ.get("OOZ", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "ooz", "libooz.so")))
        _ooz.ooz_decompress.restype = ctypes.c_int
        _ooz.ooz_decompress.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t]
    out = ctypes.create_string_buffer(usz + 64)
    r = _ooz.ooz_decompress(d, len(d), out, usz)
    if r != usz:
        raise Exception("oodle fail %d/%d" % (r, usz))
    return out.raw[:usz]


class Pak:
    def __init__(s, p):
        s.f = open(p, "rb")
        f = s.f
        f.seek(0, 2)
        size = f.tell()
        f.seek(size - 221)
        d = f.read(221)
        s.enc = d[16]
        s.ver = struct.unpack("<I", d[21:25])[0]
        off, sz = struct.unpack("<QQ", d[25:41])
        s.comps = [d[61 + i * 32:61 + (i + 1) * 32].strip(b"\0").decode() for i in range(5)]
        f.seek(off)
        idx = f.read(sz)
        idx = aes(idx) if s.enc else idx
        s.mount, pos = rstr(idx, 0)
        n = struct.unpack("<i", idx[pos:pos + 4])[0]
        pos += 4
        pos += 8
        has_ph = struct.unpack("<i", idx[pos:pos + 4])[0]
        pos += 4
        if has_ph:
            pos += 16 + 20
        has_fd = struct.unpack("<i", idx[pos:pos + 4])[0]
        pos += 4
        fd_off, fd_sz = struct.unpack("<QQ", idx[pos:pos + 16])
        pos += 16 + 20
        esz = struct.unpack("<i", idx[pos:pos + 4])[0]
        pos += 4
        s.encoded = idx[pos:pos + esz]
        f.seek(fd_off)
        fd = f.read(fd_sz)
        fd = aes(fd) if s.enc else fd
        s.files = {}
        pos = 0
        nd = struct.unpack("<i", fd[pos:pos + 4])[0]
        pos += 4
        for i in range(nd):
            dn, pos = rstr(fd, pos)
            nf = struct.unpack("<i", fd[pos:pos + 4])[0]
            pos += 4
            for j in range(nf):
                fn, pos = rstr(fd, pos)
                ei = struct.unpack("<i", fd[pos:pos + 4])[0]
                pos += 4
                s.files[dn + fn] = ei

    def entry(s, ei):
        e = s.encoded
        p = ei
        bits = struct.unpack("<I", e[p:p + 4])[0]
        p += 4
        comp = (bits >> 23) & 0x3f
        encr = (bits >> 22) & 1
        nblk = (bits >> 6) & 0xffff
        bs = bits & 0x3f
        off32 = bits & (1 << 31)
        usz32 = bits & (1 << 30)
        sz32 = bits & (1 << 29)
        if bs == 0x3f:
            bs = struct.unpack("<I", e[p:p + 4])[0]
            p += 4
        else:
            bs <<= 11
        if off32:
            off = struct.unpack("<I", e[p:p + 4])[0]
            p += 4
        else:
            off = struct.unpack("<Q", e[p:p + 8])[0]
            p += 8
        if usz32:
            usz = struct.unpack("<I", e[p:p + 4])[0]
            p += 4
        else:
            usz = struct.unpack("<Q", e[p:p + 8])[0]
            p += 8
        if comp:
            if sz32:
                sz = struct.unpack("<I", e[p:p + 4])[0]
                p += 4
            else:
                sz = struct.unpack("<Q", e[p:p + 8])[0]
                p += 8
        else:
            sz = usz
        hdr = 53 + ((4 + 16 * nblk) if comp else 0)
        blocks = []
        if comp:
            if nblk == 1 and not encr:
                blocks = [(hdr, hdr + sz)]
            else:
                start = hdr
                for i in range(nblk):
                    bsz = struct.unpack("<I", e[p:p + 4])[0]
                    p += 4
                    blocks.append((start, start + bsz))
                    start += (bsz + 15) // 16 * 16 if encr else bsz
        return dict(off=off, usz=usz, sz=sz, comp=comp, encr=encr, bs=bs, blocks=blocks, hdr=hdr)

    def read(s, path):
        en = s.entry(s.files[path])
        f = s.f
        base = en["off"]
        if en["comp"] == 0:
            f.seek(base + en["hdr"])
            d = f.read((en["sz"] + 15) // 16 * 16 if en["encr"] else en["sz"])
            return aes(d)[:en["sz"]] if en["encr"] else d
        parts = []; done = 0
        m = s.comps[en["comp"] - 1]
        for (a, b) in en["blocks"]:
            f.seek(base + a)
            d = f.read((b - a + 15) // 16 * 16 if en["encr"] else b - a)
            d = aes(d)[:b - a] if en["encr"] else d
            want = min(en["bs"], en["usz"] - done)
            if m == "Zlib":
                p_ = zlib.decompress(d)
            elif m == "Oodle":
                p_ = oodle(d, want)
            else:
                raise Exception("comp " + m)
            parts.append(p_); done += len(p_)
        return b"".join(parts)


if __name__ == "__main__":
    pk = Pak(sys.argv[1])
    if sys.argv[2] == "info":
        for pat in sys.argv[3:]:
            for k in pk.files:
                if re.search(pat, k):
                    en = pk.entry(pk.files[k])
                    print(k, "comp=", pk.comps[en["comp"] - 1] if en["comp"] else "none", "enc=", en["encr"],
                          "sz=", en["sz"], "usz=", en["usz"], "blocks=", len(en["blocks"]), "bs=", en["bs"])
    elif sys.argv[2] == "list":
        for k in sorted(pk.files):
            print(k)
    else:
        outdir = sys.argv[2]
        for pat in sys.argv[3:]:
            for k in list(pk.files):
                if re.search(pat, k):
                    d = pk.read(k)
                    p = os.path.join(outdir, k)
                    os.makedirs(os.path.dirname(p), exist_ok=True)
                    open(p, "wb").write(d)
                    print("ok", k, len(d))
