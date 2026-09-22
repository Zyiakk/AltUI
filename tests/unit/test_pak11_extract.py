import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts"))
from pak11_extract import out_path


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
