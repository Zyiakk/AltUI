import unittest, os, sys, tempfile, shutil, struct
from unittest import mock
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts")); sys.path.insert(0, H)
import pak11_extract, pakio, bodypak, cfg
from pak11_extract import out_path, aes_ecb_decrypt

KEY = bytes(range(100, 132))   # any 256-bit key: the game's key is not in the sources (read from the game's exe)

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
except ImportError:
    Cipher = None


class Aes(unittest.TestCase):
    """The game paks are AES-256-ECB encrypted; the pyz files and the AltUI Mod Converter decrypt them without cryptography."""

    def test_fips197_vectors(self):   # FIPS-197 appendix C: plaintext 00112233..ff, key 000102..
        pt = bytes.fromhex("00112233445566778899aabbccddeeff")
        for n, ct in ((16, "69c4e0d86a7b0430d8cdb78070b4c55a"), (24, "dda97ca4864cdfe06eaf70a0ec0d7191"),
                      (32, "8ea2b7ca516745bfeafc49904b496089")):
            self.assertEqual(aes_ecb_decrypt(bytes(range(n)), bytes.fromhex(ct)), pt, n)

    @unittest.skipUnless(Cipher, "cryptography not installed")
    def test_same_as_cryptography(self):
        data = os.urandom(4096)
        d = Cipher(algorithms.AES(KEY), modes.ECB()).decryptor()
        self.assertEqual(aes_ecb_decrypt(KEY, data), d.update(data) + d.finalize())

    def test_aes_without_cryptography(self):
        with mock.patch.dict(sys.modules, {"cryptography": None, "cryptography.hazmat.primitives.ciphers": None}):
            self.assertEqual(pak11_extract.aes(b"\0" * 32, KEY), aes_ecb_decrypt(KEY, b"\0" * 32))

    def test_length_not_a_multiple_of_16(self):
        with self.assertRaises(ValueError): aes_ecb_decrypt(KEY, b"\0" * 17)


def key_code(key, disp=0xE0):
    """The game exe's key callback: eight mov dword [rbp+d], imm32 with a movups after each half (as compiled by UE4)."""
    movs = [b"\xC7\x45" + bytes([(disp + 4 * i) & 0xFF]) + key[4 * i:4 * i + 4] for i in range(8)]
    return (b"\x40\x55\x48\x8b\xec" + b"".join(movs[:4]) + b"\x0F\x10\x45\xE0" + b"".join(movs[4:]) + b"\x0F\x10\x4D\xF0"
            + b"\x0F\x11\x01\x0F\x11\x49\x10\xC3")


@unittest.skipUnless(Cipher, "cryptography not installed (needed to encrypt the test index)")
class GameKey(unittest.TestCase):
    """The game's pak key is read from the player's own game exe, never shipped."""

    def setUp(self):
        self.d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        pak11_extract._KEYS.clear()
        game = os.path.join(self.d, "TheKillingAntidote")
        os.makedirs(os.path.join(game, "Binaries", "Win64")); os.makedirs(os.path.join(game, "Content", "Paks"))
        self.exe = os.path.join(game, "Binaries", "Win64", "TheKillingAntidote-Win64-Shipping.exe")
        self.pak = os.path.join(game, "Content", "Paks", "pakchunk0-WindowsNoEditor.pak")
        e = Cipher(algorithms.AES(KEY), modes.ECB()).encryptor()
        self.block = e.update(struct.pack("<i", 10) + b"../../../\0" + b"\0\0") + e.finalize()   # an index starts with its mount point

    def write_exe(self, *keys):
        with open(self.exe, "wb") as f:
            f.write(b"\xCC" * 4096 + b"\x90\xCC".join(key_code(k) for k in keys) + b"\xCC" * 4096)

    def test_the_key_that_opens_the_index(self):   # a decoy: another run of 32 bytes of moves before the real one
        self.write_exe(bytes(range(32)), KEY)
        self.assertEqual(pak11_extract.game_key(self.pak, self.block), KEY)

    def test_moves_split_by_other_code_are_no_key(self):
        code = key_code(KEY); half = len(code) // 2
        self.assertNotIn(KEY, pak11_extract.key_candidates(code[:half] + b"\x90" * 40 + code[half:]))

    def test_no_exe_next_to_the_pak(self):
        with self.assertRaises(SystemExit) as c: pak11_extract.game_key(os.path.join(self.d, "copy.pak"), self.block)
        self.assertIn("Shipping.exe", str(c.exception))

    def test_no_key_in_the_exe(self):
        self.write_exe(bytes(range(32)))
        with self.assertRaises(SystemExit) as c: pak11_extract.game_key(self.pak, self.block)
        self.assertIn("no key in", str(c.exception))

    def test_found_once_per_exe(self):
        self.write_exe(KEY)
        self.assertEqual(pak11_extract.game_key(self.pak, self.block), KEY)
        with mock.patch.object(pak11_extract, "key_candidates", side_effect=AssertionError("scanned twice")):
            self.assertEqual(pak11_extract.game_key(self.pak, self.block), KEY)


GAME_PAK = os.path.join(cfg.path("GAME"), "Content", "Paks", "pakchunk0-WindowsNoEditor.pak")


@unittest.skipUnless(cfg.path("GAME") and os.path.exists(GAME_PAK), "game not installed (GAME)")
class GamePak(unittest.TestCase):
    def test_opens_with_the_key_from_the_exe(self):
        pak11_extract._KEYS.clear()
        with pak11_extract.Pak(GAME_PAK) as pk:
            self.assertEqual(pk.mount, "../../../")
            cue = next(k for k in pk.files if k.endswith("/HK416_Shot_Cue.uasset"))
            self.assertEqual(pk.read(cue)[:4], b"\xC1\x83\x2A\x9E")   # package magic


class OpenPak(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        self.p = os.path.join(self.d, "t.pak")
        bodypak.write_pak(self.p, "../../../TheKillingAntidote/Content/Mod/Body_T/", [], [("A.uasset",) + bodypak.plain_entry(b"x" * 99)], 1)

    def test_closes_with_the_block(self):   # Windows cannot replace a file that is still open (bodybones.patch_pak)
        with pakio.open_pak(self.p) as pk:
            self.assertEqual(pk.read("/A.uasset"), b"x" * 99)
        self.assertTrue(pk.f.closed)

    def test_error_of_a_v11_pak_is_not_hidden_behind_pakv3(self):
        """A missing AES once surfaced as PakV3's struct.error - the real cause must come through."""
        with mock.patch.object(pakio, "Pak", side_effect=ModuleNotFoundError("No module named 'cryptography'")):
            with self.assertRaises(ModuleNotFoundError): pakio.open_pak(self.p)


class OutPath(unittest.TestCase):
    """Entry keys are relative to the pak's mount point and start with "/" - os.path.join would treat that as
    an absolute path and try to write into the file system root (extraction failed with a permission error)."""

    def test_entry_at_the_pak_root(self):
        self.assertEqual(out_path("/tmp/out", "/S_BodyScale.uasset"), os.path.join("/tmp/out", "S_BodyScale.uasset"))

    def test_entry_in_a_folder(self):
        self.assertEqual(out_path("/tmp/out", "/Project/Classes/Foo.uasset"),
                         os.path.join("/tmp/out", "Project", "Classes", "Foo.uasset"))

    def test_key_without_leading_slash(self):
        self.assertEqual(out_path("out", "Female.uexp"), os.path.join("out", "Female.uexp"))

    def test_no_escape_from_the_target_folder(self):
        self.assertEqual(out_path("/tmp/out", "/../../etc/passwd"), os.path.join("/tmp/out", "etc", "passwd"))


if __name__ == "__main__": unittest.main()
