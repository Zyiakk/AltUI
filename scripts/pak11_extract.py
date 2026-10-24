import struct, sys, re, os, zlib, glob
import oodle_kraken
try:
    import oodle_native as _native   # dev repo: ooz via ctypes, ~100x faster; not in bodypak.pyz (scripts/bodypak_dist.sh)
except ImportError:
    _native = None

def aes(b, key):
    """AES-256-ECB decryption - only for encrypted paks (game paks, key from game_key); mod paks are unencrypted.
    cryptography when installed (dev repo), else the pure-Python decryptor below (the pyz files and the AltUI Mod Converter
    carry no packages)."""
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    except ImportError:
        return aes_ecb_decrypt(key, b)
    d = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
    return d.update(b) + d.finalize()


# The game's pak key is not shipped: it is read from the player's own game exe. UE4 compiles the key callback into eight
# "mov dword [rbp|rsp+d], imm32" (C7 45 d imm / C7 44 24 d imm), two movups between them; every run of such moves that
# fills 32 consecutive bytes is a candidate, and the one that decrypts the pak's index to a mount point is the key.
_KEY_MOV = re.compile(rb"\xC7(?:\x45|\x44\x24)([\s\S])([\s\S]{4})")
_KEYS = {}   # (exe, size, mtime) -> key


def game_exe(pak_path):
    """The Shipping exe of the game a pak in <game>/TheKillingAntidote/Content/Paks/ belongs to, else None."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(pak_path))))
    exes = sorted(glob.glob(os.path.join(root, "Binaries", "Win64", "*-Shipping.exe")))
    return exes[0] if exes else None


def key_candidates(code):
    """32-byte keys built by runs of mov-immediates in code (see _KEY_MOV)."""
    out, run, last = [], {}, -100
    for m in _KEY_MOV.finditer(code):
        if m.start() - last > 16:   # anything longer than a movups in between ends the run
            run = {}
        last = m.end()
        run[struct.unpack("b", m.group(1))[0]] = m.group(2)
        if len(run) >= 8:
            for d in sorted(run):
                k = b"".join(run.get(d + 4 * i, b"") for i in range(8))
                if len(k) == 32 and k not in out:
                    out.append(k)
    return out


def opens_index(key, block):
    """Whether key decrypts the first 16 bytes of a pak index to the start of its mount point ("../…")."""
    p = aes_ecb_decrypt(key, block)
    return 0 < struct.unpack("<i", p[:4])[0] < 1024 and p[4:7] == b"../"


def game_key(pak_path, index_block):
    """The key of an encrypted game pak, read from the game's exe next to it (found once per exe)."""
    exe = game_exe(pak_path)
    if exe is None:
        raise SystemExit("%s is encrypted; its key comes from the game's exe, which was not found "
                         "(…/TheKillingAntidote/Binaries/Win64/*-Shipping.exe next to …/Content/Paks)" % pak_path)
    st = os.stat(exe); tag = (exe, st.st_size, st.st_mtime)
    if tag not in _KEYS or not opens_index(_KEYS[tag], index_block):
        with open(exe, "rb") as f:
            key = next((k for k in key_candidates(f.read()) if opens_index(k, index_block)), None)
        if key is None:
            raise SystemExit("no key in %s opens %s (a game update with a new kind of exe?)" % (exe, pak_path))
        _KEYS[tag] = key
    return _KEYS[tag]


_AES = None


def _aes_tables():
    """S-box, inverse S-box and the four decryption T-tables (FIPS-197), built from GF(2^8) once."""
    global _AES
    if _AES is None:
        exp, log, x = [0] * 510, [0] * 256, 1
        for i in range(255):
            exp[i] = exp[i + 255] = x; log[x] = i
            x ^= ((x << 1) ^ 0x1B) & 0xFF if x & 0x80 else x << 1    # x * 3: 3 generates the multiplicative group
        mul = lambda a, c: exp[log[a] + log[c]] if a else 0
        sbox, inv = [0] * 256, [0] * 256
        for a in range(256):
            v = exp[255 - log[a]] if a else 0
            s = v
            for _ in range(4):
                v = ((v << 1) | (v >> 7)) & 0xFF; s ^= v
            sbox[a] = s ^ 0x63; inv[s ^ 0x63] = a
        td0 = [mul(s, 14) << 24 | mul(s, 9) << 16 | mul(s, 13) << 8 | mul(s, 11) for s in inv]
        ror = lambda t: [(w >> 8) | ((w & 0xFF) << 24) for w in t]
        td1 = ror(td0); td2 = ror(td1); td3 = ror(td2)
        _AES = sbox, inv, td0, td1, td2, td3
    return _AES


def aes_ecb_decrypt(key, b):
    """AES-ECB decryption of b (length a multiple of 16) in pure Python; key of 16, 24 or 32 bytes."""
    sbox, inv, td0, td1, td2, td3 = _aes_tables()
    nk = len(key) // 4; nr = nk + 6
    w = list(struct.unpack(">%dI" % nk, key)); rcon = 1
    for i in range(nk, 4 * (nr + 1)):
        t = w[-1]
        if i % nk == 0:
            t = (sbox[(t >> 16) & 255] << 24 | sbox[(t >> 8) & 255] << 16 | sbox[t & 255] << 8 | sbox[t >> 24]) ^ (rcon << 24)
            rcon = ((rcon << 1) ^ 0x1B) & 0xFF if rcon & 0x80 else rcon << 1
        elif nk > 6 and i % nk == 4:
            t = sbox[t >> 24] << 24 | sbox[(t >> 16) & 255] << 16 | sbox[(t >> 8) & 255] << 8 | sbox[t & 255]
        w.append(w[i - nk] ^ t)
    # equivalent inverse cipher: round keys in reverse order, InvMixColumns on the inner ones
    imc = lambda k: td0[sbox[k >> 24]] ^ td1[sbox[(k >> 16) & 255]] ^ td2[sbox[(k >> 8) & 255]] ^ td3[sbox[k & 255]]
    dk = list(w[4 * nr:4 * nr + 4])
    for r in range(nr - 1, 0, -1):
        dk += [imc(k) for k in w[4 * r:4 * r + 4]]
    dk += w[0:4]
    if len(b) % 16:
        raise ValueError("AES-ECB: length %d is not a multiple of 16" % len(b))
    words = struct.unpack(">%dI" % (len(b) // 4), b); out = []
    for j in range(0, len(words), 4):
        s0, s1, s2, s3 = words[j] ^ dk[0], words[j + 1] ^ dk[1], words[j + 2] ^ dk[2], words[j + 3] ^ dk[3]
        for r in range(4, 4 * nr, 4):
            s0, s1, s2, s3 = (td0[s0 >> 24] ^ td1[(s3 >> 16) & 255] ^ td2[(s2 >> 8) & 255] ^ td3[s1 & 255] ^ dk[r],
                              td0[s1 >> 24] ^ td1[(s0 >> 16) & 255] ^ td2[(s3 >> 8) & 255] ^ td3[s2 & 255] ^ dk[r + 1],
                              td0[s2 >> 24] ^ td1[(s1 >> 16) & 255] ^ td2[(s0 >> 8) & 255] ^ td3[s3 & 255] ^ dk[r + 2],
                              td0[s3 >> 24] ^ td1[(s2 >> 16) & 255] ^ td2[(s1 >> 8) & 255] ^ td3[s0 & 255] ^ dk[r + 3])
        k = 4 * nr
        out += [(inv[s0 >> 24] << 24 | inv[(s3 >> 16) & 255] << 16 | inv[(s2 >> 8) & 255] << 8 | inv[s1 & 255]) ^ dk[k],
                (inv[s1 >> 24] << 24 | inv[(s0 >> 16) & 255] << 16 | inv[(s3 >> 8) & 255] << 8 | inv[s2 & 255]) ^ dk[k + 1],
                (inv[s2 >> 24] << 24 | inv[(s1 >> 16) & 255] << 16 | inv[(s0 >> 8) & 255] << 8 | inv[s3 & 255]) ^ dk[k + 2],
                (inv[s3 >> 24] << 24 | inv[(s2 >> 16) & 255] << 16 | inv[(s1 >> 8) & 255] << 8 | inv[s0 & 255]) ^ dk[k + 3]]
    return struct.pack(">%dI" % len(out), *out)


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


def oodle(d, usz):
    """One Oodle block -> its |usz| uncompressed bytes: ooz when the dev repo has it, else the pure-Python Kraken decoder
    (scripts/oodle_kraken.py – the only path inside bodypak.pyz)."""
    try:
        if _native is not None and _native.available():
            return _native.decompress(d, usz)
        return oodle_kraken.decompress(d, usz)
    except oodle_kraken.OodleError as e:
        raise SystemExit("Oodle: %s" % e)


class Pak:
    def __init__(s, p, key=None):
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
        s.key = (key or game_key(p, idx[:16])) if s.enc else None
        idx = aes(idx, s.key) if s.enc else idx
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
        fd = aes(fd, s.key) if s.enc else fd
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

    def close(s):
        s.f.close()

    def __enter__(s):
        return s

    def __exit__(s, *exc):
        s.close()

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
            return aes(d, s.key)[:en["sz"]] if en["encr"] else d
        parts = []; done = 0
        m = s.comps[en["comp"] - 1]
        for (a, b) in en["blocks"]:
            f.seek(base + a)
            d = f.read((b - a + 15) // 16 * 16 if en["encr"] else b - a)
            d = aes(d, s.key)[:b - a] if en["encr"] else d
            want = min(en["bs"], en["usz"] - done)
            if m == "Zlib":
                p_ = zlib.decompress(d)
            elif m == "Oodle":
                p_ = oodle(d, want)
            else:
                raise Exception("comp " + m)
            parts.append(p_); done += len(p_)
        return b"".join(parts)


def out_path(outdir, key):
    """Destination file for an extracted entry: entry keys are relative to the mount point and start with "/",
    which os.path.join would read as an absolute path (extraction into the file system root)."""
    return os.path.join(outdir, *[part for part in key.split("/") if part not in ("", ".", "..")])


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
                    p = out_path(outdir, k)
                    os.makedirs(os.path.dirname(p), exist_ok=True)
                    open(p, "wb").write(d)
                    print("ok", k, len(d))
