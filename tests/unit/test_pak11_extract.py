import unittest, os, sys, tempfile, shutil
from unittest import mock
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts"))
import pak11_extract, pakio, bodypak
from pak11_extract import out_path, aes_ecb_decrypt, KEY

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
    def test_same_as_cryptography_with_the_game_key(self):
        data = os.urandom(4096)
        d = Cipher(algorithms.AES(KEY), modes.ECB()).decryptor()
        self.assertEqual(aes_ecb_decrypt(KEY, data), d.update(data) + d.finalize())

    def test_aes_without_cryptography(self):
        with mock.patch.dict(sys.modules, {"cryptography": None, "cryptography.hazmat.primitives.ciphers": None}):
            self.assertEqual(pak11_extract.aes(b"\0" * 32), aes_ecb_decrypt(KEY, b"\0" * 32))

    def test_length_not_a_multiple_of_16(self):
        with self.assertRaises(ValueError): aes_ecb_decrypt(KEY, b"\0" * 17)


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
