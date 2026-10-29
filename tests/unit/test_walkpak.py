"""walkpak (docs/specs/2026-10-27-walk-mods-design.md): Female_Walk / Female_Run replacer -> WalkAltUI_<Name>."""
import unittest, os, sys, tempfile, shutil
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts")); sys.path.insert(0, H)
import walk_mods

SRC = os.path.join(H, "..", "..", "build", "anim", "src", "TheKillingAntidote", "Content", "Project", "Character", "Jodi", "Animations")


def game_anim(name):
    p = os.path.join(SRC, name)
    if not os.path.exists(p + ".uasset"): raise unittest.SkipTest("game animations not extracted (scripts/anim_extract.sh)")
    return open(p + ".uasset", "rb").read(), open(p + ".uexp", "rb").read()


class Curves(unittest.TestCase):
    def test_game_walk_passes(self):
        r = walk_mods.check_anim(*game_anim("Female_Walk"))
        self.assertEqual(r["errors"], []); self.assertEqual(r["warnings"], [])
        self.assertAlmostEqual(r["speed"], 208, delta=15)

    def test_injured_walk_refused(self):
        r = walk_mods.check_anim(*game_anim("Female_WalkHurt_F"))
        self.assertTrue(any("Rotation Speed" in e for e in r["errors"]), r)
        self.assertTrue(any("Forward Moving Alpha" in w for w in r["warnings"]), r)


import walkpak, bodypak
from pak11_extract import Pak
from test_idlepak import pkg_bytes, entries, JODI_ANIM, SKEL


def tpl(name, placeholders):
    return entries("Mod/AltUI/" + name, pkg_bytes(name + "_C", "AnimBlueprintGeneratedClass",
                   [(JODI_ANIM, "AnimBlueprintGeneratedClass", "Jodi_Anim_C")] + [(p, "AnimSequence", p.rsplit("/", 1)[1]) for p in placeholders], b"CDO" + name.encode()))


class Convert(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        wm = walk_mods
        self.altui = os.path.join(self.d, "AltUI.pak")
        bodypak.write_pak(self.altui, "../../../TheKillingAntidote/Content/", [],
                          tpl(wm.walk_tpl("Normal", "Normal"), [wm.TEMPLATE_WALK]) + tpl(wm.walk_tpl("Normal", "Afk1"), [wm.TEMPLATE_WALK])
                          + tpl(wm.run_tpl("Normal", "Normal"), [wm.TEMPLATE_RUN]) + tpl(wm.both_tpl("Normal"), [wm.TEMPLATE_WALK, wm.TEMPLATE_RUN]), 2)

    def replacer(self, walk=True, run=False):
        e = []
        if walk: e += entries("Project/Character/Jodi/Animations/Female_Walk", pkg_bytes("Female_Walk", "AnimSequence", [(SKEL, "Skeleton", "Female_Skeleton")], b"W"))
        if run: e += entries("Project/Character/Jodi/Animations/Female_Run", pkg_bytes("Female_Run", "AnimSequence", [(SKEL, "Skeleton", "Female_Skeleton")], b"R"))
        e += entries("Project/Something/Else", pkg_bytes("Else", "Texture2D", []))
        p = os.path.join(self.d, "MyWalk_P.pak"); bodypak.write_pak(p, "../../../TheKillingAntidote/Content/", [], e, 1); return p

    def files(self, log): return sorted(k.lstrip("/") for k in Pak(log["pak"]).files)

    def test_walk_only(self):
        log = walkpak.convert(self.replacer(), name="Strut", title="Strut", out_dir=self.d, altui=self.altui, check=False)
        self.assertEqual(log["mod"], "WalkAltUI_Strut"); self.assertEqual(log["sides"], ["walk"])
        self.assertEqual(sorted(log["templates"]), sorted([walk_mods.walk_tpl("Normal", "Normal"), walk_mods.walk_tpl("Normal", "Afk1")]))
        self.assertIn("Female_Walk.uasset", self.files(log)); self.assertNotIn("Female_Run.uasset", self.files(log))
        self.assertEqual(log["dropped"], ["Project/Something/Else.uasset", "Project/Something/Else.uexp"])

    def test_run_only(self):
        log = walkpak.convert(self.replacer(walk=False, run=True), name="Dash", out_dir=self.d, altui=self.altui, check=False)
        self.assertEqual(log["sides"], ["run"]); self.assertEqual(log["templates"], [walk_mods.run_tpl("Normal", "Normal")])

    def test_both(self):
        log = walkpak.convert(self.replacer(run=True), name="Both", out_dir=self.d, altui=self.altui, check=False)
        self.assertEqual(log["sides"], ["walk", "run"]); self.assertEqual(len(log["templates"]), 4)

    def test_imports_point_at_the_mod_and_uexp_unchanged(self):
        log = walkpak.convert(self.replacer(), name="Strut", out_dir=self.d, altui=self.altui, check=False)
        pk, src = Pak(log["pak"]), Pak(self.altui)
        n = walk_mods.walk_tpl("Normal", "Normal")
        ua = next(pk.read(k) for k in pk.files if k.lstrip("/") == n + ".uasset")
        self.assertIn(b"/Game/Mod/WalkAltUI_Strut/Female_Walk", ua)
        ux_new = next(pk.read(k) for k in pk.files if k.lstrip("/") == n + ".uexp")
        ux_old = next(src.read(k) for k in src.files if k.endswith(n + ".uexp"))
        self.assertEqual(ux_new, ux_old)

    def test_run_only_points_at_its_run(self):
        """A run-only mod: its RunTpl plays the mod's Female_Run; walk and idle stay the template's built-in ones."""
        log = walkpak.convert(self.replacer(walk=False, run=True), name="Dash", out_dir=self.d, altui=self.altui, check=False)
        ua = next(Pak(log["pak"]).read(k) for k in Pak(log["pak"]).files if k.lstrip("/") == walk_mods.run_tpl("Normal", "Normal") + ".uasset")
        self.assertIn(b"/Game/Mod/WalkAltUI_Dash/Female_Run", ua)

    def test_no_walk_or_run_refused(self):
        p = os.path.join(self.d, "Other.pak")
        bodypak.write_pak(p, "../../../TheKillingAntidote/Content/", [], entries("Project/Something/Else", pkg_bytes("Else", "Texture2D", [])), 1)
        with self.assertRaises(SystemExit): walkpak.convert(p, out_dir=self.d, altui=self.altui, check=False)

    def test_altui_without_templates_refused(self):
        old = os.path.join(self.d, "OldAltUI.pak")
        bodypak.write_pak(old, "../../../TheKillingAntidote/Content/", [], entries("Mod/AltUI/BP_X", pkg_bytes("BP_X_C", "BlueprintGeneratedClass", [])), 3)
        with self.assertRaises(SystemExit) as cm: walkpak.convert(self.replacer(), out_dir=self.d, altui=old, check=False)
        self.assertIn("update AltUI", str(cm.exception))

    def test_curve_check_refuses(self):
        """The synthetic animation has no curves: with the check on, walkpak refuses and names the curve."""
        with self.assertRaises(SystemExit) as cm: walkpak.convert(self.replacer(), name="X", out_dir=self.d, altui=self.altui)
        self.assertIn("MoveData_Speed", str(cm.exception))
