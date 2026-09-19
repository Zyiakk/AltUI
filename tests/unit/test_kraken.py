"""scripts/oodle_kraken.py (pure-Python Oodle Kraken decoder) against hand-made streams, fixtures and – when
tools/ooz/libooz.so and the mod archive exist – the ooz reference decoder."""
import unittest, os, sys, json, glob, hashlib, time
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts"))
FX = os.path.join(H, "fixtures")
A = "/mnt/linDataSSD/games/TKA_mods_archive/original"
OOZ = os.path.join(H, "..", "..", "tools", "ooz", "libooz.so")
import oodle_kraken
from oodle_kraken import OodleError
import oodle_native, pak11_extract
from pak11_extract import Pak

# sha256 of the files in fixtures/kraken_fixture.pak (built by fixtures/make_kraken_fixture.py, deterministic inputs)
FIXTURE_SHA = {
    "/text.bin": "4b0e0185a62206bc80697e8e3d867344567d60c1421ee5f2d58dd12c127cc659",     # Huffman + LZ mode 1
    "/skew.bin": "97c1f72bc1f2ddc0cb41aadd20257c44d1896892fa70e838b7e3614dec846662",     # entropy-only Huffman (new code lengths)
    "/runs.bin": "3ac13dbbaf1269b3cecac3e91becb43a90fad6314a89e1aeff831d8a406410d0",     # entropy-only RLE
    "/zeros.bin": "3755862355e2e7d0e0dc0f6b98a89978c0710890982862dd17975829e35be6b4",    # memset quantum
    "/big.bin": "1cbb3c19141a962d525dd4f7d9c3ff42f9d3da4dad76778f2bdc29eb1ab26eea",      # three 64 KB pak blocks
    "/random.bin": "6edadfa6c36eeb17804813b6f6266cd090f639fb02452493d73073bbe8e7208d",   # stored uncompressed by UnrealPak
}


def oodle_blocks(path, suffixes=None):
    """(entry key, block index, compressed bytes, uncompressed size) of every Oodle block of a v11 pak."""
    pk = Pak(path)
    for k in pk.files:
        if suffixes and not k.endswith(suffixes):
            continue
        en = pk.entry(pk.files[k])
        if not en["comp"] or pk.comps[en["comp"] - 1] != "Oodle":
            continue
        for n, (a, b) in enumerate(en["blocks"]):
            pk.f.seek(en["off"] + a)
            yield k, n, pk.f.read(b - a), min(en["bs"], en["usz"] - n * en["bs"])


def decode_entry(path, key):
    """The uncompressed bytes of one Oodle entry, block by block through oodle_kraken.decompress."""
    return b"".join(oodle_kraken.decompress(d, usz) for k, n, d, usz in oodle_blocks(path) if k == key)


def ref_decompress(src, usz):
    """The ooz reference (tools/ooz/libooz.so, built by tools/fetch_ooz.sh, via scripts/oodle_native.py); None when it rejects the data."""
    try:
        return oodle_native.decompress(src, usz)
    except OodleError:
        return None


class Streams(unittest.TestCase):
    """Hand-made streams: header, quantum header, memset / raw / uncompressed quanta, error paths (verified against ooz)."""
    DATA = bytes(range(20))

    def test_memset_quantum(self):
        self.assertEqual(oodle_kraken.decompress(b"\x8c\x06\x07\xff\xffA", 100), b"A" * 100)

    def test_uncompressed_block(self):
        self.assertEqual(oodle_kraken.decompress(b"\xcc\x06" + self.DATA, 20), self.DATA)

    def test_raw_quantum(self):
        self.assertEqual(oodle_kraken.decompress(b"\x8c\x06\x00\x00\x13" + self.DATA, 20), self.DATA)

    def test_header_every_256k(self):
        src = b"\x8c\x06\x07\xff\xffA" + b"\x8c\x06\x07\xff\xffB"
        self.assertEqual(oodle_kraken.decompress(src, 0x40000 + 5), b"A" * 0x40000 + b"B" * 5)

    def test_other_codecs_raise(self):
        for byte, name in ((0x0a, "Mermaid"), (0x0c, "Leviathan"), (0x05, "LZNA"), (0x0b, "Bitknit"), (0x07, "type 7")):
            with self.assertRaises(OodleError) as cm:
                oodle_kraken.decompress(b"\x8c" + bytes([byte]) + b"\x00\x00\x13" + self.DATA, 20)
            self.assertIn(name, str(cm.exception))

    def test_malformed_raises(self):
        for src, usz in ((b"\x8c\x06\x00\x00\x13" + self.DATA[:10], 20),   # truncated quantum
                         (b"\x8c\x06\x07\xff\xffA\x00", 100),                # trailing byte
                         (b"\x78\x9c" + self.DATA, 20),                        # zlib, not Oodle
                         (b"\x8c\x06\x00\x00\x14" + self.DATA + b"x", 20),    # quantum larger than its output
                         (b"", 20)):
            with self.assertRaises(OodleError):
                oodle_kraken.decompress(src, usz)


class EntropyBlocks(unittest.TestCase):
    """Kraken_DecodeBytes on real entropy blocks (fixtures/entropy_blocks.json: Huffman old/new, TANS, RLE, multi array, memcpy)
    and on the entropy-only fixture files."""

    def test_entropy_blocks(self):
        for v in json.load(open(os.path.join(FX, "entropy_blocks.json"), encoding="utf-8")):
            src = bytes.fromhex(v["src"]) + b"\0" * 16
            n, out = oodle_kraken._decode_bytes(src, 0, len(src) - 16, v["dst_size"])
            self.assertEqual(n, len(src) - 16, v["name"])
            self.assertEqual((len(out), hashlib.sha256(out).hexdigest()), (v["dst_size"], v["sha256"]), v["name"])

    def test_fixture_entropy_only(self):
        for key in ("/skew.bin", "/runs.bin", "/zeros.bin"):
            self.assertEqual(hashlib.sha256(decode_entry(os.path.join(FX, "kraken_fixture.pak"), key)).hexdigest(), FIXTURE_SHA[key], key)


class Blocks(unittest.TestCase):
    """Whole Oodle blocks with LZ stage (fixtures/blocks.json: mode 0 / 1, scaled offsets, memmove chunk, uncompressed …)
    and the complete fixture pak."""

    def test_blocks(self):
        for v in json.load(open(os.path.join(FX, "blocks.json"), encoding="utf-8")):
            out = oodle_kraken.decompress(bytes.fromhex(v["src"]), v["dst_size"])
            self.assertEqual(hashlib.sha256(out).hexdigest(), v["sha256"], v["name"])

    def test_fixture_pak(self):
        pk = Pak(os.path.join(FX, "kraken_fixture.pak"))
        self.assertEqual(set(pk.files), set(FIXTURE_SHA))
        for key, sha in FIXTURE_SHA.items():
            en = pk.entry(pk.files[key])
            data = decode_entry(pk.f.name, key) if en["comp"] else pk.read(key)
            self.assertEqual(hashlib.sha256(data).hexdigest(), sha, key)

    def test_runtime(self):
        t = time.time(); decode_entry(os.path.join(FX, "kraken_fixture.pak"), "/big.bin")
        self.assertLess(time.time() - t, 2.0)

    @unittest.skipUnless(os.path.exists(A), "Mod-Archiv fehlt")
    def test_runtime_largest_uasset(self):
        # 410 KB, the largest Oodle-compressed .uasset in the archive
        p = A + "/Mods/TKA_Workshop_EscapefromRC.pak"; key = "ModernCityEnvironment01/Blueprints/BP_MBuilding04.uasset"
        t = time.time(); data = decode_entry(p, key)
        self.assertLess(time.time() - t, 5.0); self.assertEqual(len(data), 410140)


@unittest.skipUnless(os.path.exists(OOZ), "libooz.so (tools/fetch_ooz.sh) fehlt")
class Native(unittest.TestCase):
    """scripts/oodle_native.py: the dev repo decodes through ooz (ctypes, ~100x faster); pak11_extract.oodle() prefers it and
    falls back to the pure-Python decoder – the only path inside bodypak.pyz, which does not ship oodle_native."""

    def test_native_equals_python(self):
        for v in json.load(open(os.path.join(FX, "blocks.json"), encoding="utf-8")):
            src = bytes.fromhex(v["src"])
            self.assertEqual(oodle_native.decompress(src, v["dst_size"]), oodle_kraken.decompress(src, v["dst_size"]), v["name"])
        with self.assertRaises(OodleError):
            oodle_native.decompress(b"\x78\x9c" + bytes(20), 20)

    def test_pak11_extract_prefers_native_and_falls_back(self):
        self.assertTrue(oodle_native.available())
        v = json.load(open(os.path.join(FX, "blocks.json"), encoding="utf-8"))[0]; src = bytes.fromhex(v["src"])
        want = oodle_kraken.decompress(src, v["dst_size"])
        self.assertIs(pak11_extract._native, oodle_native); self.assertEqual(pak11_extract.oodle(src, v["dst_size"]), want)
        pak11_extract._native = None
        try:
            self.assertEqual(pak11_extract.oodle(src, v["dst_size"]), want)
            with self.assertRaises(SystemExit):
                pak11_extract.oodle(b"\x78\x9c" + bytes(20), 20)
        finally:
            pak11_extract._native = oodle_native


@unittest.skipUnless(os.path.exists(OOZ) and os.path.exists(A), "libooz.so (tools/fetch_ooz.sh) oder Mod-Archiv fehlt")
class Reference(unittest.TestCase):
    """Python decoder == ooz on the archive: every .uasset of a sample of paks (all entries of all paks with KRAKEN_FULL=1)."""
    SAMPLE = ["Mods/TKA-UN_Dv1-fix1.3d.pak", "nexus/783/Jodithicctest4_P.pak", "Mods/HMs_Shoes.pak", "Mods/Car_Dealer.pak",
              "Mods/Bikini_Bottom.pak", "Mods/Cat_ear_headphones.pak", "Mods/Racing_Suit.pak", "Mods/Brefg_Poses.pak",
              "Mods/LowPolyJunglePack.pak", "Mods/Lost_in_Abandoned_Factory.pak"]

    def test_matches_ooz(self):
        full = os.environ.get("KRAKEN_FULL") == "1"
        paks = sorted(glob.glob(A + "/**/*.pak", recursive=True)) if full else [os.path.join(A, p) for p in self.SAMPLE]
        n = 0
        for p in paks:
            try:
                blocks = list(oodle_blocks(p, None if full else (".uasset",)))
            except Exception:
                continue   # v3 paks and paks pak11_extract cannot read are not Oodle
            for k, i, d, usz in blocks:
                want = ref_decompress(d, usz)
                self.assertIsNotNone(want, (p, k, i))
                self.assertEqual(oodle_kraken.decompress(d, usz), want, (p, k, i)); n += 1
        self.assertGreater(n, 100)


if __name__ == "__main__":
    unittest.main()
