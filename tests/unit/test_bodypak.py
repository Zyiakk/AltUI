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

    def assertTagAdded(self, out_uexp, src_uexp):
        """Mesh without its own ABP: the export data grew by the 29-byte PostProcessAnimBlueprint tag, the mesh data behind it is unchanged."""
        self.assertEqual(len(out_uexp), len(src_uexp) + 29); self.assertEqual(out_uexp[-4096:], src_uexp[-4096:])

    def test_derive_name(self):
        self.assertEqual(bodypak.derive_name("/x/TKA-UN_Dv1-fix1.3d.pak"), "Body_TKA_UN_Dv1_fix1_3d")
        self.assertEqual(bodypak.derive_name("Body_Foo.pak"), "Body_Foo")

    def test_v11_source(self):
        out, log = bodypak.convert(DV1, out_dir=self.d)
        self.assertEqual(os.path.basename(out), "Body_TKA_UN_Dv1_fix1_3d.pak"); self.assertEqual(log["status"], "ok"); self.assertEqual(log["verify"], [])
        self.assertEqual(log["title"], "TKA_UN_Dv1_fix1_3d")
        pk = Pak(out); src = Pak(DV1)
        self.assertEqual(pk.mount, "../../../TheKillingAntidote/Content/Mod/Body_TKA_UN_Dv1_fix1_3d/")
        self.assertEqual(sorted(pk.files), ["/Body_Scale.uasset", "/Body_Scale.uexp", "/Female.uasset", "/Female.uexp", "/TKA_Mod_Table.uasset", "/TKA_Mod_Table.uexp"])
        self.assertTagAdded(pk.read("/Female.uexp"), src.read("/Female.uexp"))   # the uasset gets the ABP imports (test_abp_added_dv1)
        self.assertEqual(pk.entry(pk.files["/Female.uexp"])["comp"], 0)   # tag inserted -> stored uncompressed (raw block copy: test_abp_attached_783)
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
        self.assertEqual(sorted(pk.files), ["/Body_Scale.uasset", "/Body_Scale.uexp", "/Female.uasset", "/Female.uexp", "/TKA_Mod_Table.uasset", "/TKA_Mod_Table.uexp"])   # skin_hye/Eyelashes are left out
        self.assertTagAdded(pk.read("/Female.uexp"), src.read("Jodi/Body/Female.uexp")); self.assertEqual(log["title"], "New Pussy")
        self.assertEqual(log["companions"], {}); self.assertEqual(log["abp"], "AltUI")
        self.assertEqual(sorted(log["dropped"]), ["Jodi/Body/Skin/skin_hye.uasset", "Jodi/Body/Skin/skin_hye.ubulk", "Jodi/Body/Skin/skin_hye.uexp",
                                                  "Makeup/Eyelashes_1.uasset", "Makeup/Eyelashes_1.ubulk", "Makeup/Eyelashes_1.uexp"])

    def test_companion_assets_travel_with_the_mesh(self):
        """Nexus 783: the mesh imports /Game/Project/Character/Jodi/Body/TESTABP (PostProcessAnimBlueprint) that only exists in the
        mod pak. Without it the body loads without its bone scaling = looks like vanilla. The companion is relocated into the mod
        folder and the mesh import is rewritten; TESTABP itself (imports only vanilla) stays byte-identical."""
        from uasset_pkg import Package
        out, log = bodypak.convert(THICC, name="Body_Thicc", title="Thicc", out_dir=self.d, keep_abp=True)
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

    def test_abp_attached_783(self):
        """Default: the mod's ABP import is redirected to AltUI's ABP_BodyScale, its defaults land in Body_Scale, TESTABP is not shipped."""
        from uasset_pkg import Package
        import bodyscale_groups as bg, uasset_props
        out, log = bodypak.convert(THICC, name="Body_Thicc", title="Thicc", out_dir=self.d)
        pk = Pak(out); src = Pak(THICC)
        self.assertEqual(sorted(pk.files), ["/Body_Scale.uasset", "/Body_Scale.uexp", "/Female.uasset", "/Female.uexp", "/TKA_Mod_Table.uasset", "/TKA_Mod_Table.uexp"])
        self.assertEqual(log["abp"], "AltUI"); self.assertEqual(log["warnings"], []); self.assertEqual(log["companions"], {})
        self.assertEqual([round(x, 3) for x in log["scale_defaults"]["GlutesHips"]], [2.5, 1.5, 2.0])
        mesh = Package.from_bytes(pk.read("/Female.uasset"), pk.read("/Female.uexp"))
        pkgs = [im.object_name for im in mesh.imports if im.class_name == "Package"]
        self.assertIn(bg.ABP_PATH, pkgs); self.assertFalse(any("TESTABP" in p for p in pkgs))
        self.assertTrue(any(im.class_name == "AnimBlueprintGeneratedClass" and im.object_name == bg.ABP_CLASS for im in mesh.imports))
        self.assertTrue(any(im.class_name == bg.ABP_CLASS and im.object_name == "Default__" + bg.ABP_CLASS and im.class_package == bg.ABP_PATH for im in mesh.imports))
        self.assertEqual(pk.read("/Female.uexp"), src.read("/Female.uexp"))          # export data untouched: the tag already existed
        p = os.path.join(self.d, "Body_Scale.uasset"); open(p, "wb").write(pk.read("/Body_Scale.uasset")); open(p[:-7] + ".uexp", "wb").write(pk.read("/Body_Scale.uexp"))
        row = next(iter(uasset_props.dump(p).values()))["rows"]["Default"]
        self.assertEqual([round(row[bg.member_internal(0, "Breasts")][k], 3) for k in "xyz"], [1.3, 1.2, 1.15])

    def test_abp_added_dv1(self):
        """A mesh without a post-process ABP gets the imports and the PostProcessAnimBlueprint tag; every other tag stays byte-identical."""
        from uasset_pkg import Package
        import bodyscale_groups as bg, uasset_props
        out, log = bodypak.convert(DV1, name="Body_Dv1", out_dir=self.d)
        pk = Pak(out); src = Pak(DV1)
        self.assertEqual(log["abp"], "AltUI"); self.assertEqual(log["scale_defaults"], {v: [1.0, 1.0, 1.0] for v, _, _ in bg.GROUPS})
        a = Package.from_bytes(pk.read("/Female.uasset"), pk.read("/Female.uexp")); b = Package.from_bytes(src.read("/Female.uasset"), src.read("/Female.uexp"))
        fa = next(e for e in a.exports if e.object_name == "Female"); fb = next(e for e in b.exports if e.object_name == "Female")
        self.assertEqual(len(a.imports), len(b.imports) + 3)
        cls_idx = -(next(k for k, im in enumerate(a.imports) if im.object_name == bg.ABP_CLASS and im.class_name == "AnimBlueprintGeneratedClass") + 1)
        self.assertIn(cls_idx, fa.deps_create_before_ser)
        # tags: same as before plus PostProcessAnimBlueprint -> class import
        def tags(p, e):
            r = uasset_props.Reader(e.data, p.names, p.imports, p.exports); out = []
            while True:
                t = r.tag()
                if t is None: return out
                out.append((t["name"], e.data[r.p:r.p + t["size"]])); r.p += t["size"]
        ta, tb = tags(a, fa), tags(b, fb)
        self.assertEqual([t for t in ta if t[0] != "PostProcessAnimBlueprint"], tb)
        self.assertEqual(dict(ta)["PostProcessAnimBlueprint"], struct.pack("<i", cls_idx))
        # the rest of the export (mesh data after the tags) is unchanged
        self.assertEqual(fa.data[-1000:], fb.data[-1000:]); self.assertEqual(len(fa.data) - len(fb.data), 29)   # tag: name 8 + type 8 + size/index 8 + guid flag 1 + int32 4
        self.assertEqual([e.data for e in a.exports if e.object_name != "Female"], [e.data for e in b.exports if e.object_name != "Female"])

    def test_keep_abp(self):
        out, log = bodypak.convert(THICC, name="Body_Keep", out_dir=self.d, keep_abp=True)
        pk = Pak(out); src = Pak(THICC)
        self.assertEqual(log["abp"], "kept"); self.assertNotIn("scale_defaults", log)
        self.assertIn("Project/Character/Jodi/Body/TESTABP.uexp", pk.files); self.assertNotIn("/Body_Scale.uasset", pk.files)
        self.assertEqual(pk.read("/Female.uexp"), src.read("/Female.uexp"))

    def test_v3_source_stored_uncompressed(self):
        out, log = bodypak.convert(OG, name="Body_OGMORPH", title="OGMORPH 0.6", out_dir=self.d)
        pk = Pak(out); src = open_pak(OG); self.assertEqual(src.ver, 3)
        self.assertEqual(pk.entry(pk.files["/Female.uexp"])["comp"], 0)
        self.assertTagAdded(pk.read("/Female.uexp"), src.read("Female.uexp"))

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
        for src, name in ((DV1, "Body_A"), (OG, "Body_B"), (THICC, "Body_C"), (PUSSY, "Body_D")):
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
        # Oodle-compressed source with a companion asset: decoded by the pure-Python oodle_kraken inside the zip – no native
        # library in the pyz (antivirus false positive in 1.3.1), no tools/ooz, no environment variable
        import zipfile
        names = zipfile.ZipFile(pyz).namelist()
        self.assertIn("oodle_kraken.py", names); self.assertIn("LICENSE-GPL-3.0.txt", names)
        self.assertFalse([n for n in names if n.endswith((".dll", ".so", ".dylib"))], names)
        self.assertNotIn("oodle_native.py", names)   # the ctypes accelerator stays in the dev repo
        env = {k: v for k, v in os.environ.items() if k not in ("OOZ", "PYTHONPATH")}
        r = subprocess.run([sys.executable, "-I", "-S", pyz, THICC, "--name", "Body_ZipThicc", "--out", d], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("ABP_BodyScale", r.stdout)
        self.assertEqual(json.load(open(os.path.join(d, "Body_ZipThicc_convert.json")))["abp"], "AltUI")


if __name__ == "__main__":
    unittest.main()
