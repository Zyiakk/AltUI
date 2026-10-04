"""Quick menu sector material: the Windows-cooked files (D3D SM5 shaders as inline DXBC, scripts/quickmenu/material.sh under Wine) sit in
the repo, match the material script, and replace the Linux-cooked copy in AltUI.pak (a Linux cook carries no D3D shaders:
the DX11 game would draw the default material)."""
import unittest, os, hashlib
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(H, "..", "..")
SCRIPT = os.path.join(ROOT, "scripts", "quickmenu", "material.py")
COOKED = os.path.join(ROOT, "assets", "cooked_win", "Mod", "AltUI", "Mat")


class QuickMaterial(unittest.TestCase):
    def test_cooked_files_match_script(self):
        stamp = open(os.path.join(COOKED, "stamp.sha256")).read().strip()
        self.assertEqual(stamp, hashlib.sha256(open(SCRIPT, "rb").read()).hexdigest())
        for ext in ("uasset", "uexp"): self.assertTrue(os.path.isfile(os.path.join(COOKED, "M_QuickSector." + ext)), ext)

    def test_windows_shaders(self):
        self.assertIn(b"DXBC", open(os.path.join(COOKED, "M_QuickSector.uexp"), "rb").read())   # D3D shader bytecode, inline

    @unittest.skipUnless(os.path.isfile(os.path.join(ROOT, "build", "mod.rsp")), "no build yet (scripts/pak.sh)")
    def test_pak_takes_windows_copy(self):
        rsp = open(os.path.join(ROOT, "build", "mod.rsp")).read().splitlines()
        lines = [l for l in rsp if "M_QuickSector" in l]
        self.assertEqual(len(lines), 2, lines)
        self.assertTrue(all("assets/cooked_win/" in l for l in lines), lines)


if __name__ == "__main__": unittest.main()
