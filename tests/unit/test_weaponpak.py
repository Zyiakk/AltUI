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


class Paints(unittest.TestCase):
    """A model mod that also replaces the game's paints (Samurai Edge: M_Camo_Pistol / M_Pink_Pistol made for its mesh)."""
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        own = "/Game/Project/Models/Weapon/UMP45/Material/M_Own"
        camo_tex = "/Game/Project/Models/Weapon/UMP45/Material/Camo/T_Own_Camo"
        self.extra = (mesh_entries("models/weapon/UMP45/Material/MI_Camo_UMP45", "MI_Camo_UMP45", "MaterialInstanceConstant",
                                   [(own, "Material"), (camo_tex, "Texture2D")])
                      + mesh_entries("models/weapon/UMP45/Material/M_Own", "M_Own", "Material")
                      + mesh_entries("models/weapon/UMP45/Material/Camo/T_Own_Camo", "T_Own_Camo", "Texture2D"))

    def test_game_paint_paths(self):
        self.assertEqual(ws.game_paint("/Game/Project/models/weapon/Glock/Materials/M_Camo_Pistol"), "Camo")
        self.assertEqual(ws.game_paint("/Game/Project/Models/Weapon/HK416/MI_Pink_HK416"), "Pink")
        self.assertIsNone(ws.game_paint("/Game/Project/Models/Weapon/Glock/Materials/M_Pistol"))   # the weapon's own material is no paint
        self.assertEqual(len(ws.GAME_PAINTS), 18)

    def test_member_names_keep_their_place(self):
        """Material comes last: the members before it keep their internal names, so tables written before still read."""
        names = [i for _, i, _ in ws.struct_members()]
        self.assertTrue(names[5].startswith("Icon_12_"), names[5]); self.assertTrue(names[6].startswith("Material_14_"), names[6])

    def test_a_models_own_paint_becomes_a_skin_row_with_its_material(self):
        src = os.path.join(self.d, "with_paint.pak"); model_pak(src, self.extra)
        log = weaponpak.convert(src, name="Own", title="Own UMP", out_dir=self.d)
        self.assertEqual(log["paints"], ["Camo"])
        pk = Pak(log["pak"]); files = [k.lstrip("/") for k in pk.files]
        self.assertIn("Project/models/weapon/UMP45/Material/MI_Camo_UMP45.uasset", files)   # moved along with what it builds on (the pak's spelling)
        self.assertIn("Project/models/weapon/UMP45/Material/Camo/T_Own_Camo.uasset", files)
        mi = Package.from_bytes(pk.read("Project/models/weapon/UMP45/Material/MI_Camo_UMP45.uasset"), pk.read("Project/models/weapon/UMP45/Material/MI_Camo_UMP45.uexp"))
        pkgs = [bodypak.import_name(im) for im in mi.imports if im.class_name == "Package"]
        self.assertIn("/Game/Mod/WeaponAltUI_Own/Project/models/weapon/UMP45/Material/M_Own", pkgs)
        table = Package.from_bytes(pk.read("/" + ws.TABLE_NAME + ".uasset"), pk.read("/" + ws.TABLE_NAME + ".uexp"))
        self.assertIn("/Game/Mod/WeaponAltUI_Own/Project/models/weapon/UMP45/Material/MI_Camo_UMP45",
                      [bodypak.import_name(im) for im in table.imports if im.class_name == "Package"])
        names = [str(n) for n in table.names]
        self.assertIn("Own_Camo", names); self.assertNotIn("Own", [n for n in names if n == "Own"])   # a paint row only, no skin row
        self.assertNotIn("models/weapon/UMP45/Material/MI_Camo_UMP45.uasset", log["dropped"])

    def test_a_paint_without_a_model_stays_out(self):
        """On the game's own model the mod's paint would not fit - without meshes there is nothing to convert."""
        src = os.path.join(self.d, "paint_only.pak")
        bodypak.write_pak(src, "../../../TheKillingAntidote/Content/Project/", [], list(self.extra), 6)
        with self.assertRaises(SystemExit):
            weaponpak.convert(src, name="PaintOnly", out_dir=self.d)


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

    def game_cue(self, cue_rel, waves):
        """The game's pakchunk0 with one SoundCue that plays <waves> - imported and named a second time as soft paths, as the
        wave player of a real cooked cue does."""
        game = os.path.join(self.d, "pakchunk0-WindowsNoEditor.pak")
        ua, ux = mesh_pkg(cue_rel.rsplit("/", 1)[1], "SoundCue", [(w, "SoundWave") for w in waves] + [("/Game/Project/Sounds/SoundAttenuation", "SoundAttenuation")])
        pkg = Package.from_bytes(ua, ux)
        for w in waves: pkg.names.append(w + "." + w.rsplit("/", 1)[1]); pkg.name_hashes.append((0, 0))
        ua, ux = pkg.write()
        bodypak.write_pak(game, "../../../TheKillingAntidote/Content/Project/", [], [(cue_rel + ".uasset",) + bodypak.plain_entry(ua), (cue_rel + ".uexp",) + bodypak.plain_entry(ux)], 6)
        return game

    def cue_of(self, log, rel):
        pk = Pak(log["pak"]); return Package.from_bytes(pk.read("/%s.uasset" % rel), pk.read("/%s.uexp" % rel))

    def test_the_soft_path_of_the_wave_points_at_the_mod(self):
        """2026-10-20, HK416 ("Cheetah"): the copy still named the game's wave as a soft path, and both chips played the original."""
        S = "/Game/Project/Sounds/Weapons/HK416/"
        game = self.game_cue("Sounds/Weapons/HK416/HK416_Shot_Cue", [S + "HK416_Shot"])
        src = os.path.join(self.d, "G36C-SFX.pak"); sound_pak(src, "sounds/weapons/HK416/HK416_Shot")
        log = weaponpak.convert(src, name="G36CSound", out_dir=self.d, game=game)
        names = self.cue_of(log, "HK416_Shot_Cue").names
        self.assertIn("/Game/Mod/WeaponAltUI_G36CSound/HK416_Shot.HK416_Shot", names)
        self.assertFalse([n for n in names if n.lower().startswith(S.lower() + "hk416_shot.")])

    def test_several_waves_behind_the_cue(self):
        """GLOCK19SFX replaces gun_pistol_shot_01 and _02, the two waves the game's gun_pistol_shot picks from."""
        S = "/Game/Project/Sounds/Weapons/"
        game = self.game_cue("Sounds/Weapons/gun_pistol_shot", [S + "gun_pistol_shot_01", S + "gun_pistol_shot_02"])
        src = os.path.join(self.d, "GLOCK19SFX.pak")
        sound_pak(src, "sounds/weapons/gun_pistol_shot_01", extra=mesh_entries("sounds/weapons/gun_pistol_shot_02", "gun_pistol_shot_02", "SoundWave"))
        log = weaponpak.convert(src, name="Glock19Sound", out_dir=self.d, game=game)
        self.assertEqual((log["weapon"], log["sound"]), ("Glock", "gun_pistol_shot"))
        cue = self.cue_of(log, "gun_pistol_shot")
        pkgs = [bodypak.import_name(im) for im in cue.imports if im.class_name == "Package"]
        for w in ("gun_pistol_shot_01", "gun_pistol_shot_02"):
            self.assertIn("/Game/Mod/WeaponAltUI_Glock19Sound/" + w, pkgs); self.assertNotIn(S + w, pkgs)
            self.assertIn("/Game/Mod/WeaponAltUI_Glock19Sound/%s.%s" % (w, w), cue.names)
            self.assertIn(w + ".uasset", self.files(log))

    def test_a_cue_of_its_own_brings_its_waves_along(self):
        """A pak that replaces the Shot Sound cue and its waves: the cue named the waves by their game paths and would play the game's."""
        S = "/Game/Project/Sounds/Weapons/"
        src = os.path.join(self.d, "UMP-SFX.pak")
        ua, ux = mesh_pkg("SMG_Single_Shot", "SoundCue", [(S + "SMG_Shot_New", "SoundWave")])
        pkg = Package.from_bytes(ua, ux); pkg.names.append(S + "SMG_Shot_New.SMG_Shot_New"); pkg.name_hashes.append((0, 0)); ua, ux = pkg.write()
        entries = [("sounds/weapons/SMG_Single_Shot.uasset",) + bodypak.plain_entry(ua), ("sounds/weapons/SMG_Single_Shot.uexp",) + bodypak.plain_entry(ux)]
        entries += mesh_entries("sounds/weapons/SMG_Shot_New", "SMG_Shot_New", "SoundWave")
        bodypak.write_pak(src, "../../../TheKillingAntidote/Content/Project/", [], entries, 5)
        log = weaponpak.convert(src, name="UMPSound", out_dir=self.d)
        self.assertEqual(log["sound"], "SMG_Single_Shot"); self.assertIn("SMG_Shot_New.uasset", self.files(log))
        cue = self.cue_of(log, "SMG_Single_Shot")
        self.assertIn("/Game/Mod/WeaponAltUI_UMPSound/SMG_Shot_New", [bodypak.import_name(im) for im in cue.imports])
        self.assertIn("/Game/Mod/WeaponAltUI_UMPSound/SMG_Shot_New.SMG_Shot_New", cue.names)

    def test_a_suppressor_sound_is_refused_with_a_reason(self):
        src = os.path.join(self.d, "Marksman1A_SFX.pak"); sound_pak(src, "Sounds/Weapons/Suppressed/M16_Single_Shot__Suppressed")
        with self.assertRaises(SystemExit) as e: weaponpak.convert(src, out_dir=self.d)
        self.assertIn("suppressor", str(e.exception))

    def test_names_with_spaces_and_hyphens_are_made_valid(self):
        src = os.path.join(self.d, "My Gun - SFX.pak"); sound_pak(src, "sounds/weapons/SMG_Single_Shot")
        log = weaponpak.convert(src, out_dir=self.d)
        self.assertEqual((log["name"], log["renamed_from"], log["title"]), ("My_Gun_SFX", "My Gun - SFX", "My_Gun_SFX"))
        log = weaponpak.convert(src, name="Glock 19", out_dir=self.d)
        self.assertEqual((log["name"], log["title"]), ("Glock_19", "Glock 19"))

    def test_other_sounds_stay_skipped(self):
        src = os.path.join(self.d, "dry.pak"); sound_pak(src, "sounds/weapons/Shotgun_DryFire")
        with self.assertRaises(SystemExit):
            weaponpak.convert(src, name="Dry", out_dir=self.d)


if __name__ == "__main__":
    unittest.main()


class FNameSplit(unittest.TestCase):
    """Relocated imports keep UE's name/number split (a paint whose parent is M_SE_2 or Material__27 lost it otherwise)."""
    def test_split(self):
        f = bodypak.fname_split
        self.assertEqual(f("/Game/Mod/X/Material/M_SE_2"), ("/Game/Mod/X/Material/M_SE", 3))
        self.assertEqual(f("/Game/Mod/X/Material__27"), ("/Game/Mod/X/Material_", 28))
        self.assertEqual(f("/Game/Mod/X/T_Camo_HK416"), ("/Game/Mod/X/T_Camo_HK416", 0))
        self.assertEqual(f("/Game/Mod/X/A_0"), ("/Game/Mod/X/A", 1))
        self.assertEqual(f("/Game/Mod/X/shot_01"), ("/Game/Mod/X/shot_01", 0))   # leading zero: no number
        self.assertEqual(f("/Game/Mod/X/Body"), ("/Game/Mod/X/Body", 0))

    def test_round_trip(self):
        class Im: pass
        for p in ("/Game/Mod/X/M_SE_2", "/Game/Mod/X/Material__356", "/Game/Mod/X/G36", "/Game/Mod/X/shot_01"):
            im = Im(); im.object_name, im.object_number = bodypak.fname_split(p)
            self.assertEqual(bodypak.import_name(im), p)
