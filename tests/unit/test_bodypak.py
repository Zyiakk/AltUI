import unittest, os, sys, tempfile, shutil, struct, hashlib, subprocess, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts"))
import bodypak
from pak11_extract import Pak, rstr
from pakio import open_pak
A = "/mnt/linDataSSD/games/TKA_mods_archive/original"
DV1 = A + "/Mods/TKA-UN_Dv1-fix1.3d.pak"; PUSSY = A + "/workshop/3612645999/Jodi_New_Pussy.pak"
OG = A + "/workshop/3432791726/FemaleOGMORPH-0.6_P.pak"; SHOES = A + "/Mods/HMs_Shoes.pak"
THICC = A + "/nexus/783/Jodithicctest4_P.pak"   # mesh + PostProcessAnimBlueprint TESTABP (bone scaling) in the same pak
UNREALPAK = os.environ.get("UNREALPAK", "/mnt/linDataSSD/apps/UnrealEngine/UnrealEngine-4.27/Engine/Binaries/Linux/UnrealPak")


def path_hash_index(path):
    """Seed + PathHashIndex {hash: encoded offset} of a v11 pak (reference for bodypak.path_hash)."""
    f = open(path, "rb"); f.seek(0, 2); size = f.tell(); f.seek(size - 221); d = f.read(221)
    off, sz = struct.unpack("<QQ", d[25:41]); f.seek(off); idx = f.read(sz)
    _, pos = rstr(idx, 0); pos += 4; seed = struct.unpack("<Q", idx[pos:pos + 8])[0]; pos += 8 + 4
    ph_off, ph_sz = struct.unpack("<QQ", idx[pos:pos + 16]); f.seek(ph_off); ph = f.read(ph_sz)
    n = struct.unpack("<i", ph[:4])[0]
    return seed, {struct.unpack_from("<Q", ph, 4 + 12 * i)[0]: struct.unpack_from("<i", ph, 12 + 12 * i)[0] for i in range(n)}


class PathHash(unittest.TestCase):
    def test_matches_kit_paks(self):
        for p in (DV1, PUSSY, SHOES):
            pk = Pak(p); seed, ph = path_hash_index(p)
            self.assertGreater(len(ph), 0)
            for key, loc in pk.files.items():
                self.assertEqual(ph.get(bodypak.path_hash(key.lstrip("/"), seed)), loc, key)


class Writer(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)

    def test_plain_entries_roundtrip(self):
        a, b = b"hello world" * 100, b"\x00\x01\x02" * 5000
        entries = [("A.uasset",) + bodypak.plain_entry(a), ("Sub/Dir/B.uexp",) + bodypak.plain_entry(b)]
        out = os.path.join(self.d, "t.pak")
        bodypak.write_pak(out, "../../../TheKillingAntidote/Content/Mod/Body_T/", [], entries, 12345)
        pk = Pak(out)
        self.assertEqual(pk.mount, "../../../TheKillingAntidote/Content/Mod/Body_T/")
        self.assertEqual(sorted(pk.files), ["/A.uasset", "Sub/Dir/B.uexp"])
        self.assertEqual(pk.read("/A.uasset"), a); self.assertEqual(pk.read("Sub/Dir/B.uexp"), b)
        self.assertEqual(pk.entry(pk.files["/A.uasset"])["comp"], 0)
        seed, ph = path_hash_index(out); self.assertEqual(seed, 12345)
        for key, loc in pk.files.items():
            self.assertEqual(ph[bodypak.path_hash(key.lstrip("/"), seed)], loc)

    def test_raw_entry_copies_region_verbatim(self):
        src = Pak(DV1); region, e = bodypak.raw_entry(src, "/Female.uexp")
        en = src.entry(src.files["/Female.uexp"])
        self.assertEqual(len(region), en["blocks"][-1][1]); self.assertEqual(e["usz"], en["usz"]); self.assertEqual(e["comp"], en["comp"])
        self.assertEqual(struct.unpack_from("<qqqI", region, 0), (0, en["sz"], en["usz"], en["comp"]))   # embedded header: offset 0
        out = os.path.join(self.d, "raw.pak")
        bodypak.write_pak(out, "../../../TheKillingAntidote/Content/Mod/Body_Raw/", src.comps, [("Female.uexp", region, e)], 7)
        pk = Pak(out); en2 = pk.entry(pk.files["/Female.uexp"])
        self.assertEqual((en2["usz"], en2["sz"], en2["comp"], en2["bs"], en2["blocks"]), (en["usz"], en["sz"], en["comp"], en["bs"], en["blocks"]))
        self.assertEqual(hashlib.sha256(pk.read("/Female.uexp")).digest(), hashlib.sha256(src.read("/Female.uexp")).digest())   # Oodle via tools/ooz

    @unittest.skipUnless(os.path.exists(UNREALPAK), "UnrealPak fehlt")
    def test_unrealpak_reads_our_pak(self):
        src = Pak(DV1); entries = [("Female.uasset",) + bodypak.raw_entry(src, "/Female.uasset"), ("Female.uexp",) + bodypak.raw_entry(src, "/Female.uexp"), ("T.uasset",) + bodypak.plain_entry(b"x" * 999)]
        out = os.path.join(self.d, "u.pak")
        bodypak.write_pak(out, "../../../TheKillingAntidote/Content/Mod/Body_U/", src.comps, entries, 99)
        r = subprocess.run([UNREALPAK, out, "-Test"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-3000:])
        x = os.path.join(self.d, "x"); r = subprocess.run([UNREALPAK, out, "-Extract", x], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-3000:])
        self.assertEqual(open(os.path.join(x, "Female.uexp"), "rb").read(), src.read("/Female.uexp"))
        self.assertEqual(open(os.path.join(x, "T.uasset"), "rb").read(), b"x" * 999)


class Convert(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)

    def test_derive_name(self):
        self.assertEqual(bodypak.derive_name("/x/TKA-UN_Dv1-fix1.3d.pak"), "Body_TKA_UN_Dv1_fix1_3d")
        self.assertEqual(bodypak.derive_name("Body_Foo.pak"), "Body_Foo")

    def test_v11_source(self):
        out, log = bodypak.convert(DV1, out_dir=self.d)
        self.assertEqual(os.path.basename(out), "Body_TKA_UN_Dv1_fix1_3d.pak"); self.assertEqual(log["status"], "ok"); self.assertEqual(log["verify"], [])
        self.assertEqual(log["title"], "TKA_UN_Dv1_fix1_3d")
        pk = Pak(out); src = Pak(DV1)
        self.assertEqual(pk.mount, "../../../TheKillingAntidote/Content/Mod/Body_TKA_UN_Dv1_fix1_3d/")
        self.assertEqual(sorted(pk.files), ["/Female.uasset", "/Female.uexp", "/TKA_Mod_Table.uasset", "/TKA_Mod_Table.uexp"])
        for k in ("/Female.uasset", "/Female.uexp"):
            self.assertEqual(pk.read(k), src.read(k))
        self.assertEqual(pk.entry(pk.files["/Female.uexp"])["comp"], src.entry(src.files["/Female.uexp"])["comp"])
        self.assertTrue(os.path.exists(os.path.join(self.d, "Body_TKA_UN_Dv1_fix1_3d_convert.json")))
        # mod table: row = name, Caption = title, no tables
        import uasset_props
        p = os.path.join(self.d, "TKA_Mod_Table.uasset"); open(p, "wb").write(pk.read("/TKA_Mod_Table.uasset")); open(p[:-7] + ".uexp", "wb").write(pk.read("/TKA_Mod_Table.uexp"))
        t = next(iter(uasset_props.dump(p).values())); row = t["rows"]["Body_TKA_UN_Dv1_fix1_3d"]
        self.assertEqual(row["Caption_2_CF40F849410064585CC285AFBAD051F2"], "TKA_UN_Dv1_fix1_3d")
        self.assertEqual(row["Tables_21_CE3E42574FF40670AE5465BCDC6ABBCB"], [])

    def test_v11_nested_mount(self):
        out, log = bodypak.convert(PUSSY, name="Body_NewPussy", title="New Pussy", out_dir=self.d)
        pk = Pak(out); src = Pak(PUSSY)
        self.assertEqual(sorted(pk.files), ["/Female.uasset", "/Female.uexp", "/TKA_Mod_Table.uasset", "/TKA_Mod_Table.uexp"])   # skin_hye/Eyelashes are left out
        self.assertEqual(pk.read("/Female.uexp"), src.read("Jodi/Body/Female.uexp")); self.assertEqual(log["title"], "New Pussy")
        self.assertEqual(log["companions"], {})
        self.assertEqual(sorted(log["dropped"]), ["Jodi/Body/Skin/skin_hye.uasset", "Jodi/Body/Skin/skin_hye.ubulk", "Jodi/Body/Skin/skin_hye.uexp",
                                                  "Makeup/Eyelashes_1.uasset", "Makeup/Eyelashes_1.ubulk", "Makeup/Eyelashes_1.uexp"])

    def test_companion_assets_travel_with_the_mesh(self):
        """Nexus 783: the mesh imports /Game/Project/Character/Jodi/Body/TESTABP (PostProcessAnimBlueprint) that only exists in the
        mod pak. Without it the body loads without its bone scaling = looks like vanilla. The companion is relocated into the mod
        folder and the mesh import is rewritten; TESTABP itself (imports only vanilla) stays byte-identical."""
        from uasset_pkg import Package
        out, log = bodypak.convert(THICC, name="Body_Thicc", title="Thicc", out_dir=self.d)
        pk = Pak(out); src = Pak(THICC)
        new = "/Game/Mod/Body_Thicc/Project/Character/Jodi/Body/TESTABP"
        self.assertEqual(sorted(pk.files), ["/Female.uasset", "/Female.uexp", "/TKA_Mod_Table.uasset", "/TKA_Mod_Table.uexp",
                                            "Project/Character/Jodi/Body/TESTABP.uasset", "Project/Character/Jodi/Body/TESTABP.uexp"])
        self.assertEqual(log["companions"], {"/Game/Project/Character/Jodi/Body/TESTABP": new}); self.assertEqual(log["dropped"], [])
        self.assertEqual(pk.read("Project/Character/Jodi/Body/TESTABP.uasset"), src.read("/TESTABP.uasset"))
        self.assertEqual(pk.read("Project/Character/Jodi/Body/TESTABP.uexp"), src.read("/TESTABP.uexp"))
        self.assertEqual(pk.read("/Female.uexp"), src.read("/Female.uexp"))
        mesh = Package.from_bytes(pk.read("/Female.uasset"), pk.read("/Female.uexp"))
        pkgs = [im.object_name for im in mesh.imports if im.class_name == "Package"]
        self.assertIn(new, pkgs); self.assertNotIn("/Game/Project/Character/Jodi/Body/TESTABP", pkgs)
        orig = Package.from_bytes(src.read("/Female.uasset"), src.read("/Female.uexp"))
        self.assertEqual(mesh.names[:len(orig.names)], orig.names)          # name indices used by the export data are unchanged
        self.assertEqual([e.data for e in mesh.exports], [e.data for e in orig.exports])

    def test_v3_source_stored_uncompressed(self):
        out, log = bodypak.convert(OG, name="Body_OGMORPH", title="OGMORPH 0.6", out_dir=self.d)
        pk = Pak(out); src = open_pak(OG); self.assertEqual(src.ver, 3)
        self.assertEqual(pk.entry(pk.files["/Female.uexp"])["comp"], 0)
        self.assertEqual(pk.read("/Female.uexp"), src.read("Female.uexp")); self.assertEqual(pk.read("/Female.uasset"), src.read("Female.uasset"))

    def test_errors(self):
        with self.assertRaises(SystemExit): bodypak.convert(SHOES, out_dir=self.d)                       # no body mesh
        with self.assertRaises(SystemExit): bodypak.convert(DV1, name="Body_Ä", out_dir=self.d)          # invalid name
        bodypak.convert(DV1, out_dir=self.d)
        with self.assertRaises(SystemExit): bodypak.convert(DV1, out_dir=self.d)                         # target exists
        bodypak.convert(DV1, out_dir=self.d, force=True)

    def test_cli(self):
        r = subprocess.run([sys.executable, os.path.join(H, "..", "..", "scripts", "bodypak.py"), DV1, "--name", "Body_CLI", "--title", "CLI", "--out", self.d], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("Body_CLI.pak", r.stdout)
        self.assertEqual(json.load(open(os.path.join(self.d, "Body_CLI_convert.json")))["status"], "ok")

    @unittest.skipUnless(os.path.exists(UNREALPAK), "UnrealPak fehlt")
    def test_unrealpak_test_passes(self):
        for src, name in ((DV1, "Body_A"), (OG, "Body_B")):
            out, _ = bodypak.convert(src, name=name, out_dir=self.d)
            r = subprocess.run([UNREALPAK, out, "-Test"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-3000:])


class Dist(unittest.TestCase):
    def test_zipapp_runs_without_third_party_packages(self):
        w = os.path.join(H, "..", ".."); d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        r = subprocess.run(["bash", os.path.join(w, "scripts", "bodypak_dist.sh")], capture_output=True, text=True); self.assertEqual(r.returncode, 0, r.stderr)
        pyz = os.path.join(w, "build", "bodypak.pyz"); self.assertTrue(os.path.exists(pyz))
        # -I -S: isolated, without site-packages -> `cryptography` cannot be imported; the converter must not need it
        r = subprocess.run([sys.executable, "-I", "-S", pyz, DV1, "--name", "Body_Zip", "--out", d], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr); self.assertTrue(os.path.exists(os.path.join(d, "Body_Zip.pak")))
        r = subprocess.run([sys.executable, "-I", "-S", pyz, OG, "--name", "Body_ZipV3", "--out", d], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        # Oodle-compressed source with a companion asset: the decoder bundled in the zip is unpacked and used (no tools/ooz next to the pyz)
        import zipfile
        self.assertLessEqual({"ooz.dll", "libooz.so"}, set(zipfile.ZipFile(pyz).namelist()))
        env = {k: v for k, v in os.environ.items() if k != "OOZ"}
        r = subprocess.run([sys.executable, "-I", "-S", pyz, THICC, "--name", "Body_ZipThicc", "--out", d], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("companion asset used by the mesh: /Game/Project/Character/Jodi/Body/TESTABP", r.stdout)
        self.assertEqual(json.load(open(os.path.join(d, "Body_ZipThicc_convert.json")))["companions"], {"/Game/Project/Character/Jodi/Body/TESTABP": "/Game/Mod/Body_ZipThicc/Project/Character/Jodi/Body/TESTABP"})


if __name__ == "__main__":
    unittest.main()
