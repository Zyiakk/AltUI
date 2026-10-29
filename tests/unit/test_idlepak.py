"""idlepak (docs/specs/2026-10-13-idle-styles-design.md, part 2): Female_Idle replacer -> IdleAltUI_<Name>."""
import unittest, os, sys, tempfile, shutil
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts"))
import idlepak, idle_mods, bodypak
from pak11_extract import Pak
from uasset_pkg import Package, Export

SKEL = "/Game/Project/Character/Jodi/Body/Female_Skeleton"
JODI_ANIM = "/Game/Project/Character/Jodi/Jodi_Anim"


def pkg_bytes(object_name, cls, refs, data=b"DATA"):
    """A cooked package: one export of class <cls>, imports (package path, class, object name) in refs."""
    pkg = Package(); pkg.guid = b"\0" * 16
    eng = pkg.add_import("/Script/CoreUObject", "Package", 0, "/Script/Engine")
    for path, icls, obj in refs:
        p = pkg.add_import("/Script/CoreUObject", "Package", 0, path)
        pkg.add_import("/Script/Engine", icls, p, obj)
    c = pkg.add_import("/Script/CoreUObject", "Class", eng, cls)
    cdo = pkg.add_import("/Script/Engine", cls, eng, "Default__" + cls)
    pkg.exports.append(Export(c, 0, cdo, 0, object_name, 0, 0xb, data))
    pkg.depends = [[] for _ in pkg.exports]; pkg.generations = [(len(pkg.exports), 0)]
    return pkg.write()


def entries(rel, ua_ux):
    ua, ux = ua_ux
    return [(rel + ".uasset",) + bodypak.plain_entry(ua), (rel + ".uexp",) + bodypak.plain_entry(ux)]


def template(walk, run):
    n = idle_mods.template_name(walk, run)
    return entries("Mod/AltUI/" + n, pkg_bytes(n + "_C", "AnimBlueprintGeneratedClass",
                   [(JODI_ANIM, "AnimBlueprintGeneratedClass", "Jodi_Anim_C"), (idle_mods.TEMPLATE_ANIM, "AnimSequence", "Female_IdleTemplate")], b"CDO" + n.encode()))


def read(pk, rel):
    return pk.read(next(k for k in pk.files if k.lstrip("/") == rel))


class Convert(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        # the replacer as it comes: Female_Idle at the game path + an unrelated file
        e = entries("Project/Character/Jodi/Animations/Female_Idle", pkg_bytes("Female_Idle", "AnimSequence", [(SKEL, "Skeleton", "Female_Skeleton")], b"ANIM"))
        e += entries("Project/Something/Else", pkg_bytes("Else", "Texture2D", []))
        self.src = os.path.join(self.d, "Jodi_Idle_Adjustment_P.pak")
        bodypak.write_pak(self.src, "../../../TheKillingAntidote/Content/", [], e, 1)
        # an AltUI.pak with two templates
        self.altui = os.path.join(self.d, "AltUI.pak")
        bodypak.write_pak(self.altui, "../../../TheKillingAntidote/Content/", [], template("Normal", "Normal") + template("Copy", "Normal"), 2)

    def test_converts(self):
        log = idlepak.convert(self.src, name="Adjust", title="Idle Adjustment", out_dir=self.d, altui=self.altui)
        self.assertEqual(log["mod"], idle_mods.MOD_PREFIX + "Adjust")
        pk = Pak(log["pak"])
        self.assertEqual(pk.mount, "../../../TheKillingAntidote/Content/Mod/" + log["mod"] + "/")
        got = sorted(k.lstrip("/") for k in pk.files)
        self.assertEqual(got, sorted(["Female_Idle.uasset", "Female_Idle.uexp", "TKA_Mod_Table.uasset", "TKA_Mod_Table.uexp"]
                                     + [idle_mods.template_name(w, r) + ext for w, r in (("Normal", "Normal"), ("Copy", "Normal")) for ext in (".uasset", ".uexp")]))
        self.assertEqual(sorted(log["templates"]), ["Copy_Normal", "Normal_Normal"])
        self.assertIn("Project/Something/Else.uasset", log["dropped"])
        self.assertEqual(read(pk, "Female_Idle.uexp"), pkg_bytes("Female_Idle", "AnimSequence", [(SKEL, "Skeleton", "Female_Skeleton")], b"ANIM")[1])

    def test_template_points_at_the_mod_animation(self):
        log = idlepak.convert(self.src, name="Adjust", out_dir=self.d, altui=self.altui)
        pk = Pak(log["pak"]); n = idle_mods.template_name("Normal", "Normal")
        names = {(i.class_name, bodypak.import_name(i)) for i in Package.from_bytes(read(pk, n + ".uasset"), read(pk, n + ".uexp")).imports}
        self.assertIn(("Package", "/Game/Mod/%s/Female_Idle" % log["mod"]), names)
        self.assertIn(("AnimSequence", "Female_Idle"), names)
        self.assertNotIn(("Package", idle_mods.TEMPLATE_ANIM), names)
        self.assertIn(("Package", JODI_ANIM), names)

    def test_retarget_keeps_export_data(self):
        ua, ux = pkg_bytes("X_C", "AnimBlueprintGeneratedClass", [(idle_mods.TEMPLATE_ANIM, "AnimSequence", "Female_IdleTemplate")], b"CDO")
        out = idlepak.retarget_template(ua, ux, "IdleAltUI_T")
        self.assertEqual(Package.from_bytes(out, ux).write()[1], ux)

    def test_retarget_refuses_a_non_template(self):
        ua, ux = pkg_bytes("X_C", "AnimBlueprintGeneratedClass", [(JODI_ANIM, "AnimBlueprintGeneratedClass", "Jodi_Anim_C")])
        with self.assertRaises(SystemExit): idlepak.retarget_template(ua, ux, "IdleAltUI_T")

    def test_refuses_a_pak_without_female_idle(self):
        p = os.path.join(self.d, "other.pak")
        bodypak.write_pak(p, "../../../TheKillingAntidote/Content/", [], entries("Project/Something/Else", pkg_bytes("Else", "Texture2D", [])), 3)
        with self.assertRaises(SystemExit): idlepak.convert(p, out_dir=self.d, altui=self.altui)

    def test_refuses_an_altui_without_templates(self):
        p = os.path.join(self.d, "old_AltUI.pak")
        bodypak.write_pak(p, "../../../TheKillingAntidote/Content/", [], entries("Mod/AltUI/BP_X", pkg_bytes("BP_X_C", "BlueprintGeneratedClass", [])), 4)
        with self.assertRaises(SystemExit): idlepak.convert(self.src, out_dir=self.d, altui=p)

    def test_no_overwrite_without_force(self):
        idlepak.convert(self.src, name="Adjust", out_dir=self.d, altui=self.altui)
        with self.assertRaises(SystemExit): idlepak.convert(self.src, name="Adjust", out_dir=self.d, altui=self.altui)
        idlepak.convert(self.src, name="Adjust", out_dir=self.d, altui=self.altui, force=True)


class RealMod(unittest.TestCase):
    def test_the_installed_replacer(self):
        arch = os.environ.get("TKA_MOD_ARCHIVE")
        src = os.path.join(os.path.dirname(arch or "."), "library", "override", "Jodi_Idle_Adjustment_qhlys_P.pak")
        altui = os.path.join(H, "..", "..", "build", "AltUI.pak")
        real = os.path.exists(src) and (os.stat(src).st_blocks > 0 or os.path.getsize(src) == 0)   # not a placeholder
        if not (arch and real and os.path.exists(altui)): self.skipTest("no archive / no AltUI build")
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        log = idlepak.convert(src, name="IdleAdjustment", out_dir=d, altui=altui)
        self.assertIn("Normal_Normal", log["templates"]); self.assertEqual(log["verify"], [])
