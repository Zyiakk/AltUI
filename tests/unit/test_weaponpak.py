import unittest, os, sys, tempfile, shutil, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts"))
import weapon_skins as ws, weaponpak, bodypak
from pak11_extract import Pak
from uasset_pkg import Package, Export

SKIN = os.path.expanduser("~/Downloads")   # the real skin paks live in the extracted archive; the test builds its own input


def fake_uasset(tag):
    """Minimal payload - the converter copies texture packages byte for byte, it never parses them."""
    return b"UASSET" + tag


def mesh_pkg(object_name, cls, refs=(), extra_exports=()):
    """A cooked package with one export of class <cls> and one import per (package path, class) in refs - meshes are
    parsed and rewritten by the converter, so a payload of fake bytes would not do. extra_exports come first, like the
    BodySetup and NavCollision a real cooked StaticMesh carries ahead of the mesh itself."""
    pkg = Package(); pkg.guid = b"\0" * 16
    eng = pkg.add_import("/Script/CoreUObject", "Package", 0, "/Script/Engine")
    for path, icls in refs:
        p = pkg.add_import("/Script/CoreUObject", "Package", 0, path)
        pkg.add_import("/Script/Engine", icls, p, path.rsplit("/", 1)[1])
    for ecls in extra_exports:
        c = pkg.add_import("/Script/CoreUObject", "Class", eng, ecls)
        cdo = pkg.add_import("/Script/Engine", ecls, eng, "Default__" + ecls)
        pkg.exports.append(Export(c, 0, cdo, 0, ecls, 0, 0xb, b"X"))
    c = pkg.add_import("/Script/CoreUObject", "Class", eng, cls)
    cdo = pkg.add_import("/Script/Engine", cls, eng, "Default__" + cls)
    pkg.exports.append(Export(c, 0, cdo, 0, object_name, 0, 0xb, b"MESHDATA"))
    pkg.depends = [[] for _ in pkg.exports]; pkg.generations = [(len(pkg.exports), 0)]
    return pkg.write()


PHYS = "/Game/Project/Models/Weapon/UMP45/ump45_PhysicsAsset"
SKEL = "/Game/Project/Models/Weapon/UMP45/ump45_Skeleton"


def mesh_entries(rel, object_name, cls, refs=(), extra_exports=()):
    ua, ux = mesh_pkg(object_name, cls, refs, extra_exports)
    return [(rel + ".uasset",) + bodypak.plain_entry(ua), (rel + ".uexp",) + bodypak.plain_entry(ux)]


def model_pak(path, extra=()):
    """A weapon model mod as it comes from Nexus: skeletal mesh (with skeleton and physics asset), pickup mesh, magazine."""
    entries = list(extra)
    entries += mesh_entries("models/weapon/UMP45/ump45", "ump45", "SkeletalMesh", [(SKEL, "Skeleton"), (PHYS, "PhysicsAsset")])
    entries += mesh_entries("models/weapon/UMP45/SM_UMP45", "SM_UMP45", "StaticMesh", extra_exports=("BodySetup", "NavCollision"))
    entries += mesh_entries("models/weapon/UMP45/SM_SMG_magEmpty", "SM_SMG_magEmpty", "StaticMesh", extra_exports=("BodySetup", "NavCollision"))
    entries += mesh_entries("models/weapon/UMP45/ump45_PhysicsAsset", "ump45_PhysicsAsset", "PhysicsAsset")
    bodypak.write_pak(path, "../../../TheKillingAntidote/Content/Project/", [], entries, 3)
    return entries


class Definition(unittest.TestCase):
    def test_tex_roles(self):
        self.assertEqual(ws.tex_role("T_UMP45_BaseColor.uasset"), "MainTex")
        self.assertEqual(ws.tex_role("T_UMP45_Normal.uasset"), "NormalTex")
        self.assertEqual(ws.tex_role("T_UMP45_OcclusionRoughnessMetallic.uasset"), "MetallicTex")
        self.assertEqual(ws.tex_role("T_Skin_ORM.uasset"), "MetallicTex")
        self.assertIsNone(ws.tex_role("T_Something_Else.uasset"))

    def test_weapon_of_folder(self):
        self.assertEqual(ws.weapon_of_folder("UMP45"), "UMP45")
        self.assertEqual(ws.weapon_of_folder("ump45"), "UMP45")
        self.assertEqual(ws.weapon_of_folder("M1014"), "Shotgun")
        self.assertIsNone(ws.weapon_of_folder("Meelee"))

    def test_member_names_are_stable(self):
        names = [i for _, i, _ in ws.struct_members()]
        self.assertEqual(len(set(names)), len(names))
        self.assertTrue(names[0].startswith("Weapon_2_"), names[0])

    def test_shot_targets(self):
        self.assertEqual(ws.shot_targets("/Game/Project/Sounds/Weapons/HK416/HK416_Shot"), [("HK416", "wave")])
        self.assertEqual(ws.shot_targets("/Game/Project/sounds/weapons/HK416/HK416_Shot_Cue"), [("HK416", "sound")])
        self.assertEqual(ws.shot_targets("/Game/Project/Sounds/Weapons/SMG_Single_Shot"), [("UMP45", "sound")])
        self.assertEqual(ws.shot_targets("/Game/Project/sounds/weapons/DesertEagle/DesertEagle_Shot"), [("DesertEagle", "sound")])
        self.assertEqual(ws.shot_targets("/Game/Project/Sounds/Weapons/Shotgun_DryFire"), [])

    def test_every_shot_weapon_is_a_tab_weapon(self):
        self.assertEqual([w for w in ws.VANILLA_SHOT if w not in ws.WEAPONS], [])

    def test_sound_member_names_are_stable(self):
        names = [i for _, i, _ in ws.sound_struct_members()]
        self.assertEqual(len(set(names)), 3)
        self.assertTrue(names[2].startswith("Sound_6_"), names[2])


class Convert(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        entries = []
        for rel in ("models/weapon/UMP45/Material/T_UMP45_BaseColor", "models/weapon/UMP45/Material/T_UMP45_Normal",
                    "models/weapon/UMP45/Material/T_UMP45_OcclusionRoughnessMetallic", "UserInterface/Items/item_icons_ump45"):
            entries.append((rel + ".uasset",) + bodypak.plain_entry(fake_uasset(rel.encode())))
            entries.append((rel + ".uexp",) + bodypak.plain_entry(b"UEXP"))
        self.skin_entries = list(entries)
        self.src = os.path.join(self.d, "ump45_skin.pak")
        bodypak.write_pak(self.src, "../../../TheKillingAntidote/Content/Project/", [], entries, 1)

    def test_converts_to_a_mod_pak(self):
        log = weaponpak.convert(self.src, name="TestSkin", title="TestSkin", out_dir=self.d)
        self.assertEqual(log["weapon"], "UMP45")
        self.assertEqual(log["textures"]["MainTex"], "T_UMP45_BaseColor")
        self.assertEqual(log["mod"], ws.MOD_PREFIX + "TestSkin")
        pk = Pak(log["pak"])
        self.assertEqual(pk.mount, "../../../TheKillingAntidote/Content/Mod/" + ws.MOD_PREFIX + "TestSkin/")
        got = sorted(k.lstrip("/") for k in pk.files)
        self.assertIn("Mod_WeaponSkin.uasset", got); self.assertIn("TKA_Mod_Table.uasset", got)
        self.assertIn("T_UMP45_BaseColor.uasset", got); self.assertIn("item_icons_ump45.uasset", got)   # original names: package name == object name
        self.assertEqual(pk.read("/T_UMP45_BaseColor.uasset"), fake_uasset(b"models/weapon/UMP45/Material/T_UMP45_BaseColor"))
        self.assertTrue(os.path.isfile(os.path.join(self.d, ws.MOD_PREFIX + "TestSkin_build.json")))

    def test_refuses_without_base_colour(self):
        entries = [("models/weapon/UMP45/Material/T_UMP45_Normal.uasset",) + bodypak.plain_entry(b"X"),
                   ("models/weapon/UMP45/Material/T_UMP45_Normal.uexp",) + bodypak.plain_entry(b"Y")]
        src = os.path.join(self.d, "only_normal.pak")
        bodypak.write_pak(src, "../../../TheKillingAntidote/Content/Project/", [], entries, 2)
        with self.assertRaises(SystemExit):
            weaponpak.convert(src, name="X", out_dir=self.d)


class Models(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        self.src = os.path.join(self.d, "UMP45_Main.pak"); model_pak(self.src)

    def test_meshes_keep_their_names(self):
        """The runtime finds the replacement by the name of the mesh it replaces - so the packages must stay flat and keep it."""
        log = weaponpak.convert(self.src, name="NewUMP", out_dir=self.d)
        self.assertEqual(log["weapon"], "UMP45")
        self.assertEqual(log["mod"], ws.MOD_PREFIX + "NewUMP")
        self.assertEqual(sorted(log["meshes"]), ["SM_SMG_magEmpty", "SM_UMP45", "ump45"])
        got = sorted(k.lstrip("/") for k in Pak(log["pak"]).files)
        for name in ("ump45", "SM_UMP45", "SM_SMG_magEmpty"):
            self.assertIn(name + ".uasset", got); self.assertIn(name + ".uexp", got)
        self.assertIn(ws.MODEL_TABLE_NAME + ".uasset", got)
        self.assertNotIn(ws.TABLE_NAME + ".uasset", got)   # no textures in this pak

    def test_companions_move_along_and_the_mesh_points_at_them(self):
        log = weaponpak.convert(self.src, name="NewUMP", out_dir=self.d)
        pk = Pak(log["pak"])
        rel = "Project/models/weapon/UMP45/ump45_PhysicsAsset.uasset"   # the pak's own spelling; pak lookups ignore case
        self.assertIn(rel, [k.lstrip("/") for k in pk.files])
        pkg = Package.from_bytes(pk.read("/ump45.uasset"), pk.read("/ump45.uexp"))
        pkgs = [im.object_name for im in pkg.imports if im.class_name == "Package"]
        self.assertIn("/Game/Mod/" + ws.MOD_PREFIX + "NewUMP/Project/models/weapon/UMP45/ump45_PhysicsAsset", pkgs)
        self.assertIn(SKEL, pkgs)   # the game's skeleton stays where it is

    def test_model_row_names_the_weapon(self):
        log = weaponpak.convert(self.src, name="NewUMP", title="New UMP45", out_dir=self.d)
        pk = Pak(log["pak"])
        rows = str(pk.read("/" + ws.MODEL_TABLE_NAME + ".uasset")) + str(pk.read("/" + ws.MODEL_TABLE_NAME + ".uexp"))
        self.assertIn("NewUMP", rows); self.assertIn("UMP45", rows)

    def test_a_pak_with_both_writes_both_tables(self):
        src = os.path.join(self.d, "both.pak")
        tex = []
        for rel in ("models/weapon/UMP45/Material/T_UMP45_BaseColor", "models/weapon/UMP45/Material/T_UMP45_Normal"):
            tex.append((rel + ".uasset",) + bodypak.plain_entry(fake_uasset(rel.encode())))
            tex.append((rel + ".uexp",) + bodypak.plain_entry(b"UEXP"))
        model_pak(src, tex)
        log = weaponpak.convert(src, name="Both", out_dir=self.d)
        got = sorted(k.lstrip("/") for k in Pak(log["pak"]).files)
        self.assertIn(ws.TABLE_NAME + ".uasset", got); self.assertIn(ws.MODEL_TABLE_NAME + ".uasset", got)
        self.assertEqual(log["textures"]["MainTex"], "T_UMP45_BaseColor")
        self.assertIn("ump45", log["meshes"])

    def test_a_model_mods_own_textures_are_no_skin(self):
        """A model mod whose material set happens to end in _Normal / _ORM has no base colour to build a skin from - and
        none is meant: the meshes carry those textures along. It converts as a model instead of being refused."""
        tex = [("models/weapon/UMP45/Material/Material__27_Normal.uasset",) + bodypak.plain_entry(fake_uasset(b"N")),
               ("models/weapon/UMP45/Material/Material__27_Normal.uexp",) + bodypak.plain_entry(b"Y")]
        src = os.path.join(self.d, "model_with_normal.pak"); model_pak(src, tex)
        log = weaponpak.convert(src, name="ModelOnly", out_dir=self.d)
        self.assertEqual(log["textures"], {})
        self.assertIn("SM_UMP45", log["meshes"])
        files = {os.path.basename(k) for k in Pak(log["pak"]).files}
        self.assertNotIn(ws.TABLE_NAME + ".uasset", files)          # no skin table
        self.assertIn(ws.MODEL_TABLE_NAME + ".uasset", files)

    def test_a_mesh_shipped_twice_keeps_the_one_that_replaces(self):
        """Some mods ship their source variant in a subfolder next to the replacement. Both flatten to the same package
        name, so only the one sitting where the game's mesh sits may be taken - otherwise the pak fails its own verify."""
        dup = mesh_entries("models/weapon/UMP45/Variants/SM_UMP45", "SM_UMP45", "StaticMesh", extra_exports=("BodySetup", "NavCollision"))
        src = os.path.join(self.d, "with_duplicate.pak"); model_pak(src, dup)
        log = weaponpak.convert(src, name="Dup", out_dir=self.d)
        self.assertEqual(log["verify"], [])
        self.assertEqual(log["meshes"].count("SM_UMP45"), 1)
        self.assertIn("models/weapon/UMP45/Variants/SM_UMP45.uasset", log["dropped"])

    def test_refuses_a_mod_with_its_own_skeleton(self):
        """A mesh on its own skeleton has no animations in the game - better to say so than to ship a weapon that never moves."""
        src = os.path.join(self.d, "own_skeleton.pak")
        extra = mesh_entries("models/weapon/UMP45/ump45_Skeleton", "ump45_Skeleton", "Skeleton")
        model_pak(src, extra)
        with self.assertRaises(SystemExit):
            weaponpak.convert(src, name="Own", out_dir=self.d)


def sound_pak(path, rel, cls="SoundWave", extra=()):
    """A shot-sound replacer: one sound package at <rel> below Content/Project/."""
    entries = list(extra) + mesh_entries(rel, rel.rsplit("/", 1)[1], cls)
    bodypak.write_pak(path, "../../../TheKillingAntidote/Content/Project/", [], entries, 5)


class Sounds(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)

    def files(self, log):
        return sorted(k.lstrip("/") for k in Pak(log["pak"]).files)

    def test_a_shot_sound_replacer_becomes_a_sound_row(self):
        src = os.path.join(self.d, "UMP45-SFX.pak"); sound_pak(src, "sounds/weapons/SMG_Single_Shot")
        log = weaponpak.convert(src, name="UMPSound", title="UMP Sound", out_dir=self.d)
        self.assertEqual(log["weapon"], "UMP45"); self.assertEqual(log["sound"], "SMG_Single_Shot")
        got = self.files(log)
        self.assertIn("SMG_Single_Shot.uasset", got); self.assertIn(ws.SOUND_TABLE_NAME + ".uasset", got)
        self.assertNotIn(ws.MODEL_TABLE_NAME + ".uasset", got); self.assertNotIn(ws.TABLE_NAME + ".uasset", got)
        pk = Pak(log["pak"])
        table = Package.from_bytes(pk.read("/" + ws.SOUND_TABLE_NAME + ".uasset"), pk.read("/" + ws.SOUND_TABLE_NAME + ".uexp"))
        refs = [(im.class_name, im.object_name) for im in table.imports]
        self.assertIn(("Package", "/Game/Mod/" + ws.MOD_PREFIX + "UMPSound/SMG_Single_Shot"), refs)
        self.assertIn(("SoundWave", "SMG_Single_Shot"), refs)

    def test_a_model_pak_with_a_sound_writes_both_rows(self):
        src = os.path.join(self.d, "UMP45_Main.pak")
        model_pak(src, mesh_entries("sounds/weapons/SMG_Single_Shot", "SMG_Single_Shot", "SoundWave"))
        log = weaponpak.convert(src, name="NewUMP", out_dir=self.d)
        got = self.files(log)
        self.assertIn(ws.MODEL_TABLE_NAME + ".uasset", got); self.assertIn(ws.SOUND_TABLE_NAME + ".uasset", got)
        self.assertEqual(log["sound"], "SMG_Single_Shot")

    def test_a_wave_behind_the_cue_gets_a_copy_of_the_cue(self):
        S = "/Game/Project/Sounds/Weapons/HK416/"
        game = os.path.join(self.d, "pakchunk0-WindowsNoEditor.pak")
        bodypak.write_pak(game, "../../../TheKillingAntidote/Content/Project/", [],
                          mesh_entries("Sounds/Weapons/HK416/HK416_Shot_Cue", "HK416_Shot_Cue", "SoundCue",
                                       [(S + "HK416_Shot", "SoundWave"), ("/Game/Project/Sounds/SoundAttenuation", "SoundAttenuation")]), 6)
        src = os.path.join(self.d, "G36C-SFX.pak"); sound_pak(src, "sounds/weapons/HK416/HK416_Shot")
        log = weaponpak.convert(src, name="G36CSound", title="G36C", out_dir=self.d, game=game)
        self.assertEqual(log["weapon"], "HK416"); self.assertEqual(log["sound"], "HK416_Shot_Cue")
        pk = Pak(log["pak"]); got = self.files(log)
        self.assertIn("HK416_Shot.uasset", got); self.assertIn("HK416_Shot_Cue.uasset", got)
        cue = Package.from_bytes(pk.read("/HK416_Shot_Cue.uasset"), pk.read("/HK416_Shot_Cue.uexp"))
        pkgs = [bodypak.import_name(im) for im in cue.imports if im.class_name == "Package"]
        self.assertIn("/Game/Mod/" + ws.MOD_PREFIX + "G36CSound/HK416_Shot", pkgs)
        self.assertNotIn(S + "HK416_Shot", pkgs)
        self.assertIn("/Game/Project/Sounds/SoundAttenuation", pkgs)   # the game's attenuation stays the game's
        table = Package.from_bytes(pk.read("/" + ws.SOUND_TABLE_NAME + ".uasset"), pk.read("/" + ws.SOUND_TABLE_NAME + ".uexp"))
        self.assertIn(("SoundCue", "HK416_Shot_Cue"), [(im.class_name, im.object_name) for im in table.imports])

    def test_a_wave_behind_the_cue_without_the_game_is_refused(self):
        src = os.path.join(self.d, "G36C-SFX.pak"); sound_pak(src, "sounds/weapons/HK416/HK416_Shot")
        with self.assertRaises(SystemExit):
            weaponpak.convert(src, name="X", out_dir=self.d, game=os.path.join(self.d, "missing.pak"))

    def test_other_sounds_stay_skipped(self):
        src = os.path.join(self.d, "dry.pak"); sound_pak(src, "sounds/weapons/Shotgun_DryFire")
        with self.assertRaises(SystemExit):
            weaponpak.convert(src, name="Dry", out_dir=self.d)


if __name__ == "__main__":
    unittest.main()
