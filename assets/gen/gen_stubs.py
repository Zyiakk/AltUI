"""Generates assets/10_stubs.json: stub additions + editor test rows in the stub tables (editor only, never end up in a pak)."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
import weapon_skins as ws
ANIM_MONTAGE = "/Game/Mod/TKA_Workshop_Anim/Female_Dance_Mod_Montage"   # montage that ships with the mod kit (stub rows only)
from bpdsl import *
from slots import SLOTS

FEMALE_MESH = "/Game/Project/Character/Jodi/Body/Female"   # skeletal mesh that ships with the mod kit (stub rows only)


def row(t, group="None", icon=None, color=True, mesh=None):
    r = {"TypeName": t, "Group": group, "ColorAdjustable": color, "Quality": 2}
    if mesh: r["Mesh"] = mesh   # editor test: a row with a real mesh, so the walk over its material slots is exercised
    return r

test_clothes = {
    "Briefs03": row("Briefs", mesh=FEMALE_MESH), "Dress05": row("Dress", "Lace"), "Casual_Mina_Neck": row("Neck", "Kpop"),
    "Casual_Mina_Necklace": row("Necklace"), "SpikeBoots": row("Boots"), "Weird": row("Nonsense", color=False),
    "Zeta_Neck": row("Neck"), "Alpha_Neck": row("Neck", "Kpop"),
    # sorted insert (binary search) + equal sort keys keep table order (first 24 characters identical -> B before A)
    "Sock_g": row("Socks"), "Sock_a": row("Socks"), "Sock_e": row("Socks"), "Sock_c": row("Socks"), "Sock_b": row("Socks"), "Sock_f": row("Socks"), "Sock_d": row("Socks"),
    "Sock_Same_Prefix_Twenty4_B": row("Socks"), "Sock_Same_Prefix_Twenty4_A": row("Socks"),
}
P_PAL = "/Game/Project/UserInterface/PaletteUI"; P_PALR = "/Game/Project/UserInterface/Widgets/Paletter"
assets = [
    # Outfits (vanilla): struct with Map<Name, Color>; the internal member name must match the game
    struct(P_OUTFIT_S, [param(OUTFIT_MEMBER, "name", "map", value_type=S_COLOR, internal_name="clothes_5_E1AD9C5C4635FD04BF2E71A226121A33")]),
    blueprint(P_OUTFITS, "/Script/Engine.SaveGame", variables=[var("outfits", "struct:" + P_OUTFIT_S, "array")],
              functions=[fn("Add Preset", [param("player", "object:" + P_JODI)]),
                         fn("Apply Preset to Player", [param("player", "object:" + P_JODI), param("index", "int")])]),
    # Coiffure / Appearance / Body Shape (vanilla tables with kit structs, save classes, GameInstance)
    struct(P_MDATA_S, [param("List", "name", "array", internal_name="List_3_E7EA677E4463B28539E691AC9F180706")]),
    struct(P_MTYPE_S, [param("Caption", "text", internal_name="Caption_2_0E996EBA487974C09D613892192A99FF"),
                       param("Single", "bool", internal_name="Single_5_D22B0C314B5AA7105E3979B0D67B603E"),
                       param("Animation", "name", internal_name="Animation_15_9696C0334F9C1EC26BD342902846ED50"),
                       param("EyeTable", "bool", internal_name="EyeTable_17_DF63FF92407675E8F12582B42622DD3D"),
                       param("CameraPosition", "int", internal_name="CameraPosition_20_A53A425B432771FB8C19C2A0FD6AA255")]),
    datatable(P_HAIR_T, P_HAIR_S, rows={"Hair": {"MirrorID": 0}, "TestHair": {"MirrorID": -1}}),
    datatable(P_SKIN_T, P_SKIN_S, rows={"Skin_Default": {}}),
    datatable(P_MAKEUP_T, P_MAKEUP_S, rows={"Eyebrow_01": {"Type": "Eyebrow"}, "Lips_01": {"Type": "Lips"}, "Lips_02": {"Type": "Lips"}}),
    # two lenses and one pair of lashes: the eye colours are kept per row, so the tests need more than one of each
    datatable(P_EYE_T, P_EYE_S, rows={"Eye_1": {"Type": "Eye"}, "Eye_2": {"Type": "Eye"}, "Eyelashes_1": {"Type": "Eyelashes"}}),
    datatable(P_MTYPE_T, P_MTYPE_S, rows={"Eyebrow": {"Single": True}, "Eye": {"Single": True, "EyeTable": True}, "Eyelashes": {"Single": True, "EyeTable": True}, "Lips": {"Single": True, "Caption": "Lippen", "CameraPosition": 983}, "Cheeks": {"Single": False}}),
    datatable(P_DLC_T, P_DLC_S, rows={"Body_TestBody": {"Caption": "Test Body"}, "SomeMod": {"Caption": "Some Mod"}, "WeaponAltUI_SkinTest": {"Caption": "Test Skin Mod"}, "WeaponAltUI_ModelTest": {"Caption": "Test Weapon Mod"}, "WeaponAltUI_SoundTest": {"Caption": "Test Sound Mod"}, "AltUIMod_Test": {"Caption": "Test Mods Tab"}}),   # editor test: filter on prefix Body_
    # Poses: AnimationTable (Animation_Struct) + a mod table for the origin test (Dressup_* rows are skipped by Collect Pose Rows)
    struct(P_ANIM_S, [param("Title", "text", internal_name="Title_5_5208877E43BB2E535DB3DFAF646E90DA"),
                      param("Montage", "object:/Script/Engine.AnimMontage", internal_name="Montage_2_99AB9F0E40D705D77C9E079E70FA0B9B"),
                      param("Sound", "object:/Script/Engine.SoundBase", internal_name="Sound_8_E18181D3438DCA7D23693593F2423CF4"),
                      param("ActionFlag", "int", internal_name="ActionFlag_15_B277E1494FAB471E5C2AD5A50658A7EC"),
                      param("Type", "int", internal_name="Type_11_FB6E225748CECEDC3C438D94C30A3021")]),
    # a real montage in the rows: Collect Pose Rows treats a row without one as a chapter marker (that is how pose packs write headings)
    datatable(P_ANIM_T, P_ANIM_S, rows={"Dressup_Leg": {"Montage": ANIM_MONTAGE}, "SitFloor": {"Title": "Sit on the floor", "Montage": ANIM_MONTAGE},
                                        "ModPose": {"Montage": ANIM_MONTAGE}, "ModMarker": {"Title": "- [ TEST CHAPTER ] -"}}),
    datatable("/Game/Mod/SomeMod/Mod_AnimationTable", P_ANIM_S, rows={"ModPose": {"Montage": ANIM_MONTAGE}}),
    # editor test (test_origin): a row name the mod also has as a clothes piece, and one that is a vanilla skin -> origin per table, "look:" only without an earlier table
    datatable("/Game/Mod/SomeMod/Mod_EyesTable", P_EYE_S, rows={"ModThing": {"Type": "Eye"}}),
    datatable("/Game/Mod/SomeMod/Mod_MakeupTable", P_MAKEUP_S, rows={"Skin_Default": {"Type": "Lips"}}),
    # Weapons: ItemTable (weapon rows), GunPaint (paint -> weapon -> material), a converted skin mod for the editor test
    # ItemClass: only the byte value counts at runtime (the game's enum); display names are ours
    enum(P_ITEMCLASS_E, ["Tool", "Collectible", "Key", "Weapon", "Ammo", "Consumable"]),
    struct(P_ITEM_S, [param("Caption", "text", internal_name="Caption_34_A1D1AEE6499506A034ED6E83F2123581"),
                      # inventory tab: weight, stacking, pack size, kind (inventory.kind_of), flag bits (2 = gun)
                      param("Weight", "int", internal_name="Weight_56_FFB819DE4B6F431FF2D096A9EE0A2195"),
                      param("IsConsumable", "bool", internal_name="IsConsumable_11_DD3ECA894EEB86F67E1EA3B2DC537792"),
                      param("NumberOfPick", "int", internal_name="NumberOfPick_59_F72BDAD8416971ADDC81DF9D6DD4A053"),
                      param("ItemClass", "enum:" + P_ITEMCLASS_E, internal_name="ItemClass_3_5CDBD46F4464FBF1033311A134618E0C"),
                      param("Flag", "int", internal_name="Flag_62_90A969094EF61FCCF71AB1B4C1584A25"),
                      param("Icon", "object:" + E_TEX2D, internal_name="Icon_8_9AB25FB442CDA342937A89A8A873CA63"),
                      param("HyperBoxGroup", "name", internal_name="HyperBoxGroup_47_F0D9C7BD4E11CB25AAFEDB863D1DF840"),
                      param("ActorClass", "class:" + E_ACTOR, internal_name="ActorClass_40_78EE9EE441407DEB19724494C04B03D6"),
                      # the weapon actor (Weapon_UMP45_C ...): unlike the pickup actor it carries the skeletal mesh with magazine and optics
                      param("InteractiveClass", "class:" + E_ACTOR, internal_name="InteractiveClass_35_A72AD9944C232F519D9186A845495978")]),
    struct(P_PAINT_S, [param("Guns", "name", "map", value_type="object:/Script/Engine.MaterialInterface", internal_name="Guns_4_974505F844690AA9345864A13AD9C39D"),
                       param("Flag", "int", internal_name="Flag_7_1EFEACDB4FF292F408E2F4AF64A1289A")]),
    datatable(P_ITEM_T, P_ITEM_S, rows={"UMP45": {"HyperBoxGroup": "Weapon", "Caption": "UMP45"}, "HK416": {"HyperBoxGroup": "Weapon", "Caption": "HK416"}, "Medicine": {"HyperBoxGroup": "Item"},
                                        # inventory tab (editor test): one row per kind, values as in the game
                                        "Glock": {"HyperBoxGroup": "Weapon", "Caption": "Glock", "Weight": 100, "ItemClass": "NewEnumerator3", "Flag": 2, "NumberOfPick": 1},
                                        "GlockAmmo": {"HyperBoxGroup": "Ammo", "Caption": "Glock ammo", "Weight": 1, "IsConsumable": True, "ItemClass": "NewEnumerator4", "NumberOfPick": 10},
                                        "Optics_RedDot": {"HyperBoxGroup": "Equipment", "Weight": 10, "IsConsumable": True, "ItemClass": "NewEnumerator1", "NumberOfPick": 1},
                                        "Flashlight": {"HyperBoxGroup": "Tool", "Weight": 10, "ItemClass": "NewEnumerator0", "NumberOfPick": 1},
                                        "Pills": {"HyperBoxGroup": "Tool", "Caption": "Pills", "Weight": 10, "IsConsumable": True, "ItemClass": "NewEnumerator0", "Flag": 4, "NumberOfPick": 1},
                                        "EntryCard_Red": {"HyperBoxGroup": "None", "ItemClass": "NewEnumerator2", "Flag": 1, "NumberOfPick": 1},
                                        "Decor_Dog": {"HyperBoxGroup": "None", "ItemClass": "NewEnumerator1", "Flag": 1, "NumberOfPick": 1, "ActorClass": "/Script/Engine.Actor"},
                                        "EntryCard_Blue": {"HyperBoxGroup": "None", "ItemClass": "NewEnumerator2", "Flag": 1, "NumberOfPick": 1, "ActorClass": "/Script/Engine.Actor"},
                                        "InvisibleHand": {"HyperBoxGroup": "None", "ItemClass": "NewEnumerator1", "Flag": 8, "NumberOfPick": 1}}),
    datatable(P_PAINT_T, P_PAINT_S, rows={"GunPaint_Pink": {}, "GunPaint_Camo": {}}),
    # Kodex encyclopedia: the archive of Jodi's office PC (Computer_Jodi reads rows 0-3 always, the rest from Note_Save.Notes);
    # only the members AltUI reads, internal names as in the game
    struct(P_ARCH_S, [param("Title", "text", internal_name="Title_2_B048B9A74E9883DAF84A80B1A875CC4F"),
                      param("Content", "text", internal_name="Content_4_EC3177DC4A1F131934EE488FA8EE4C64"),
                      param("Image", "object:" + E_TEX2D, internal_name="Image_12_C768945E4ACE98A45AC78BA2F6EDFFD6")]),
    datatable(P_ARCH_T, P_ARCH_S, rows={"Arch_%s" % c: {} for c in "ABCDEF"}),
    blueprint(P_NOTE_SAVE, "/Script/Engine.SaveGame", variables=[var("Notes", "string", "array")]),
    blueprint(P_SETTINGS_SAVE, "/Script/Engine.SaveGame", variables=[var("RunMode", "int")]),   # Jodi.Settings: RunMode 2 = run key toggles by speed (BP_AltUIMove)
    # Kodex passwords: code locks carry an ItemComp_Password (Password is in the kit already); locked = Item State 1
    blueprint(P_ITEMCOMP, mode="augment", functions=[fn("Is Locked", outputs=[param("Yes", "bool")], pure=True)]),
    blueprint(P_PWCOMP, mode="augment", variables=[var("Password", "string")]),
    blueprint(P_SHATTERER, mode="augment", variables=[var("gas tank", "object:/Script/Engine.Actor")]),   # Ragdolls: its tank moves to the copy, then cleared
    blueprint(P_ZOMBIE, mode="augment", variables=[var("Crystal", "object:/Script/Engine.Actor")]),   # Ragdolls: cleared before a copied zombie goes (its on destroyed drops it)   # the game reads/writes it (Dices_Password, ChangePassword)
    # the mesh components are reached with GetComponentsByClass (a stub variable named SkeletalMesh is refused - it collides with the engine class)
    blueprint(P_WEAPON, E_ACTOR, functions=[fn("Get Weapon Name", outputs=[param("name", "name")], pure=True),
                                            fn("Unload Ammo", outputs=[param("succeed", "bool")]),   # inventory tab: "Unload"
                                            fn("Attach to Hand"), fn("Set Visible", [param("visible", "bool")]),
                                            fn("Get Ammo Name", outputs=[param("ammo name", "name")], pure=True),   # followers: infinite ammo (Count Weapon Ammo)
                                            fn("Get Player Montage", [param("montage name", "name")], [param("montage", "object:/Script/Engine.AnimMontage")])]),   # Jason: which montage is which   # body switch: the weapon in hand back on its socket
    # Gun_Equipment_Base_C derives from StaticMeshComponent, so the magazine is a component of the weapon - Mount Mag hangs
    # one of the given class on it. A freshly spawned weapon actor has none; only the game's own equip flow puts it there.
    blueprint(P_EQUIPBASE, "/Script/Engine.StaticMeshComponent"),   # magazine, optics, suppressor, grip all derive from this
    blueprint(P_MAGCOMP, P_EQUIPBASE), blueprint(P_OPTICSCOMP, P_EQUIPBASE), blueprint(P_GRIPCOMP, P_EQUIPBASE),
    blueprint(P_BARRELCOMP, P_EQUIPBASE, variables=[var("Shot Sound", "object:/Script/Engine.SoundBase")]),   # the suppressor's own shot sound (Apply Influence sets it on the gun)
    # Gun Data: only the member AltUI reads (the game's paint, written by Change Gun Paint); the internal name must match the game
    struct(P_GUN_S, [param("PaintName", "name", internal_name="PaintName_29_FA1F96D44E7CE9841245EC85AD208267"),
                     param("GunName", "name", internal_name="GunName_20_398D82A0403D587DA0A681A117336AE6"),   # inventory tab: a gun in the storage box
                     param("Parts", "name", "array", internal_name="Parts_9_2957A5274990B0EE840FDB8AEC3E0EEA")]),   # its mounted attachments (GunEquipment rows)
    # Shot Sound: what Shoot Fx plays (Reset Default Attributes sets the class's own); Equipment Suppressor: the mounted barrel part
    blueprint(P_GUN, P_WEAPON, variables=[var("Equipment Mag", "object:" + P_MAGCOMP), var("Gun Data", "struct:" + P_GUN_S),
                                          var("Shot Sound", "object:/Script/Engine.SoundBase"), var("Equipment Suppressor", "object:" + P_BARRELCOMP)],
              functions=[fn("Change Gun Paint", [param("paint name", "name")]), fn("Reset Gun Paint"), fn("Mark to Need Update Anim"),   # body switch: Jodi_Anim reads the gun again
                         fn("Mount Mag", [param("class", "class:/Script/Engine.StaticMeshComponent")], [param("installed", "bool")]),
                         # weapons tab, attachments: mount a GunEquipment row (the bag loses it, the replaced one goes back; the
                         # mounted row again = take it off), then the stats
                         fn("Mount Equipment", [param("equipment", "name")]), fn("Apply Extra Attributes")]),
    struct(P_GEQ_S, [param("Class", "class:" + P_EQUIPBASE, internal_name="Class_2_5AA802504CA431146E46D188B581CB9F"),
                     param("Type", "int", internal_name="Type_18_FA4814DC41DC3CE847D1A392C5DE5EC2"),
                     param("Guns", "name", "array", internal_name="Guns_17_C8B5F0414A9A2B5140E8F1826AE1E82B")]),
    datatable(P_GEQ_T, P_GEQ_S, rows={"Optics_RedDot": {"Class": P_OPTICSCOMP + ".Gun_Optics_Comp_C", "Type": 0, "Guns": ["UMP45", "HK416"]},
                                      "Silencer_PRS": {"Class": P_BARRELCOMP + ".Gun_Barrel_Comp_C", "Type": 1, "Guns": ["UMP45", "HK416", "Glock"]},
                                      "UMP45": {"Type": 3, "Guns": []}}),   # a plain magazine row: no class, never offered
    # Inventory tab: the global storage box (TKA_GameState.Get Hyper Box Data, slot "StorageBox"). "Save Items_0" is the game's
    # FName "Save Items" with number 1 - the same name text gives the same FName.
    blueprint(P_HBSAVE, "/Script/Engine.SaveGame", variables=[var("Clothes", "name", "array"), var("Save Items_0", "name", "map", value_type="int"),
                                                              var("Guns", "struct:" + P_GUN_S, "array")]),
    blueprint(P_HBDATA, "/Script/CoreUObject.Object", variables=[var("HyperBoxSave", "object:" + P_HBSAVE)],
              functions=[fn("Add Item", [param("name", "name"), param("count", "int"), param("is consumable", "bool"), param("update ui", "bool")], [param("increased", "int")]),
                         fn("Consume Item Count", [param("item name", "name"), param("count", "int")]), fn("Save"),
                         fn("Count Items", [param("item", "name")], [param("num", "int")], pure=True),
                         fn("Add a Gun", [param("weapon", "object:" + P_WEAPON)]), fn("Remove a Gun", [param("IndexToRemove", "int")])]),
    struct(P_PRESET_S, [param("HairstyleName", "name", internal_name="HairstyleName_7_3260D22B43C665CF63750083BF1D2497"),
                        param("MakeupData", "name", "map", value_type="struct:" + P_MDATA_S, internal_name="MakeupData_8_229DF3ED46B7F843D59714B8DA28DCAE"),
                        param("SkinName", "name", internal_name="SkinName_10_D161C58143EEB746BDE0E195450CF92E"),
                        param("HairColor", S_LINCOLOR, internal_name="HairColor_13_2E49FD134AECED2C74BDBAA0B64005A2"),
                        param("Waist", "float", internal_name="Waist_16_877B264E42032AC07B0C5CA9A580981B"),
                        param("Hip", "float", internal_name="Hip_18_490CBF024F5D99374AFAB1897BB84E09"),
                        param("BoobsSize", "float", internal_name="BoobsSize_20_C70E33614D1991B60A6A16B1B45926E7"),
                        param("IconNumber", "int", internal_name="IconNumber_25_BAE5A8904A8F0BE67275D6908C7D51AB")]),
    blueprint(P_MAKEUP_SAVE, "/Script/Engine.SaveGame",
              variables=[var("Makeup Data", "name", "map", value_type="struct:" + P_MDATA_S), var("Hairstyle Name", "name"), var("Hair Color", S_LINCOLOR),
                         var("Skin Name", "name"), var("Waist", "float"), var("Hip", "float"), var("Boobs Size", "float")],
              functions=[fn("Save Makeup")]),
    blueprint(P_PRESET_SAVE, "/Script/Engine.SaveGame", variables=[var("Data", "struct:" + P_PRESET_S, "array")],
              functions=[fn("Save Makeup Preset"), fn("Get Available Icon Number", outputs=[param("number", "int")]),
                         fn("Add New Preset", [param("makeup", "object:" + P_MAKEUP_SAVE)], [param("number", "int")]),
                         fn("Remove A Preset", [param("index", "int")], [param("number", "int")])]),
    blueprint(P_HAIR_SAVE, "/Script/Engine.SaveGame", variables=[var("Hairstyles", "name", "set"), var("Hair Colors", "name", "map", value_type=S_COLOR)]),
    blueprint(P_PSAVE, "/Script/Engine.SaveGame", variables=[var("Wear Clothes", "name", "array")],
              functions=[fn("Collect Player Data", [param("player", "object:" + P_JODI)])]),   # player save game: pieces worn at save time; slot "TKAPlayer"
    blueprint(P_GI, "/Script/Engine.GameInstance", variables=[var("Hairstyles Save", "object:" + P_HAIR_SAVE), var("Level Name", "name")],   # Level Name: what Loading opens (menuscene.py)
              functions=[fn("Save Hair Color Data", [param("player", "object:" + P_JODI)]), fn("Add Hairstyles", [param("hairstyle name", "name")])]),
    blueprint(P_PALR, E_USERWIDGET, variables=[var("Image_Color", "object:" + E_IMAGE)],
              functions=[fn("Init Paletter", [param("initial color", S_LINCOLOR)])]),   # sets Image_Color and the hue / lightness pointers (W_HexBar paste)
    blueprint(P_PAL, E_USERWIDGET, variables=[var("Paletter", "object:" + P_PALR)],
              functions=[fn("Show Palette", [param("panel", "object:" + E_WIDGET), param("button", "object:" + E_WIDGET), param("flag", "int"), param("initial color", S_LINCOLOR)]),
                         fn("Close Frame")]),
    blueprint(P_WD, "/Script/CoreUObject.Object", variables=[var("Clothes", "name", "array")],
              functions=[fn("Has This Clothes", [param("clothes", "name")], [param("yes", "bool")], pure=True),
                         fn("Add Item And Save", [param("name", "name")], [param("new clothes", "bool")])]),
    blueprint(P_CC, "/Script/Engine.SkeletalMeshComponent",
              variables=[var("Color Adjustable", "bool"), var("Clothes Name", "name"), var("Type", "name"), var("Damage", "float"), var("Materials for Damage", "object:/Script/Engine.MaterialInstanceDynamic", "array")],
              functions=[fn("Change Color", [param("Color", S_LINCOLOR)]),
                         fn("Change Damage", [param("Value", "float"), param("save", "bool")]),   # scalar "Damage" on every damage material + Player.Store Clothes Damage
                         fn("Is Damaged", outputs=[param("yes", "bool")], pure=True)]),   # Damage > 0.1 (Repair Clothes, followers' badge)
    # followers wear the game's hair: Change Hairstyle Ex makes these, AltUI colours them with the look's hair colour
    blueprint(P_HAIRC, "/Script/Engine.SkeletalMeshComponent", functions=[fn("Change Color", [param("color", S_LINCOLOR, ref=True)])]),
    datatable(P_CTV, P_CS, rows=test_clothes),
    datatable("/Game/Mod/SomeMod/Mod_ClothesTable", P_CS, rows={"ModThing": row("Top", "SomeGroup")}),   # editor test: item origin = mod "SomeMod" (loader row in DLC_MainTable), group for the Manage tab
    datatable(P_CT, P_CS, composite=True, parent_tables=[P_CTV, "/Game/Mod/SomeMod/Mod_ClothesTable"]),
    struct(P_CTS, [param("CameraFocus", "int", internal_name="CameraFocus_17_DE98CCDE4FA8319FE550EC814F334C53"),
                   param("IncompatibleTypes", "name", "array", internal_name="IncompatibleTypes_24_3AC6063A4AB0269D2379B6ADBE2FC2B0"),   # slot conflicts (the game's asymmetric lists)
                   param("Flag", "int", internal_name="Flag_36_5EA1ED6B4519B8872DE4848FCAB44EA7")]),   # Flag & 1: several pieces per slot (only Acc)
    datatable(P_CTT, P_CTS, rows={s: dict(({"CameraFocus": 105} if s == "Boots" else {"CameraFocus": 365} if s == "Bra" else {}),
                                          **({"IncompatibleTypes": {"Top": ["Bra"], "Dress": ["Bra", "Panties", "Top"], "Pants": ["Socks"]}[s]} if s in ("Top", "Dress", "Pants") else {}),
                                          **({"Flag": 1} if s == "Acc" else {})) for s in SLOTS}),
    datatable(P_CGV, P_CGS, rows={"Lace": {"GroupName": "Spitze", "Owning": False}, "Kpop": {"GroupName": "KPOP", "Owning": False}}),
    datatable(P_CG, P_CGS, composite=True, parent_tables=[P_CGV]),
    blueprint(P_CPB, mode="augment", functions=[
        fn("Wear The Clothes", [param("name", "name"), param("check covering", "bool"), param("update mask", "bool"), param("ignore compatible", "bool")], [param("successed", "bool")]),
        fn("Take off this clothes", [param("clothes name", "name")]),
        fn("take off clothes", [param("type", "name"), param("update mask", "bool")]),
        fn("Take Off Clothes And Remove Component", [param("comp", "object:" + P_CC)]),   # one comp (multislot.Take Off Slot All)   # by slot, no covering check afterwards (the game's own forward conflict check uses it)
        fn("Get Wearing Clothes Names", outputs=[param("clothes list", "name", "array")]),
        fn("is clothes wearing", [param("clothes name", "name")], [param("yes", "bool")], pure=True),
        fn("Find Clothes Component With Name", [param("name", "name")], [param("clothes comp", "object:" + P_CC)]),
        fn("Get Clothes Color", [param("clothes name", "name")], [param("found", "bool"), param("color", S_LINCOLOR)]),
        fn("Save Clothes Color", [param("clothes name", "name"), param("color", S_LINCOLOR)]),
        fn("Restore Clothes Color", [param("clothes", "name")]),
        fn("Is Clothes Damaged", [param("clothes", "name")], [param("yes", "bool")], pure=True),
        fn("Get Clothes Damage", [param("clothes", "name", ref=True)], [param("damage", "float")], pure=True), fn("Store Clothes Damage", [param("clothes", "name"), param("damage", "float")]),   # Save Clothes Damaged: per piece, worn or not
        fn("Remove Clothing From Bag", [param("clothing name", "name")]), fn("Reset Clothes Physics"),
        fn("update body mask"),   # sets MaskThreshold, the morph "Nipple" and the breast constraint profile
        fn("Change Breast Constraint Profile", [param("morph", "float")]),
        fn("Is Wanna Run ?", outputs=[param("Yes", "bool")], pure=True), fn("Change Wanna Run", [param("run", "bool")]),
        # inventory tab: the item functions the game's inventory / storage box panels call
        fn("Put Item to Bag", [param("item name", "name"), param("num", "int"), param("is clothing", "bool"), param("fx", "bool")], [param("remove", "bool")]),
        fn("Consume Item", [param("item name", "name"), param("num", "int"), param("destroy weapon", "bool")], [param("successed", "bool"), param("count", "int")]),
        fn("Got A Gun", [param("Gun Data", "struct:" + P_GUN_S, ref=True)], [param("gun", "object:" + P_WEAPON)]),
        fn("Drop Item", [param("item name", "name")]), fn("Equip This Weapon", [param("weapon", "object:" + P_WEAPON)]),
        fn("Has This Item", [param("item name", "name")], [param("yes", "bool")], pure=True),
        fn("Get Weapon In Hand", outputs=[param("weapon", "object:" + P_WEAPON)], pure=True)], variables=[var("Breast Morph Weight", "float"), var("Body Material", "object:/Script/Engine.MaterialInstanceDynamic"), var("Clothes Colors", "name", "map", value_type=S_LINCOLOR)]),   # walk / run speed (BP_AltUIMove)   # component "Bag" (Bag_Comp) exists in the kit
    # breast / hip jiggle bodies: the game switches them on here; AltUI calls it again after re-instantiating the physics state (height slider)
    blueprint(P_CB, mode="augment", remove_functions=["Is Alive ?"],   # a stub of 2026-10-09 that collided with the kit's Jodi.Is Alive ?
              functions=[fn("Enable Boobs Physics", [param("hip", "bool")]),
                         # Jason prototype: Init Jason asks for Jason_Controller here, ours swaps the class (the game's pin is Class<AI_Controller_C>; the stub
                         # chain has no AI_Controller, the pointer is the same)
                         fn("Change Controller", [param("Class", "class:/Script/AIModule.AIController")]),
                                               fn("Is Crouching", outputs=[param("yes", "bool")], pure=True),
                                               ], variables=[var("Health", "float"), var("Speed 2d", "float"), var("Anim Blueprint", "object:/Script/Engine.AnimInstance")]),   # BP_AltUIMove (Anim Blueprint: set once in Begin Play Ex - reset after a style switch)
    # the invisible hand (catalog item): Jodi.Put Item to Bag sets its power from the hands in the bag, nothing else does - Hand Watch keeps it in step
    blueprint(P_IHC, "/Script/Engine.SceneComponent", variables=[var("Number", "int")], functions=[fn("Update Power", [param("Number", "int")])]),
    blueprint(P_JODI, mode="augment", variables=[var("InvisibleHand_Comp", "object:" + P_IHC), var("previous weapon", "object:" + P_WEAPON), var("wanna toggle weapon", "bool"),   # inventory tab: Got A Gun's equip request (Inv Got Gun)
                                                var("Settings", "object:" + P_SETTINGS_SAVE), var("Eye Material", "object:/Script/Engine.MaterialInstanceDynamic"), var("Eyelashes Material", "object:/Script/Engine.MaterialInstanceDynamic"), var("Makeup Tex", "object:/Script/Engine.TextureRenderTarget2D"), var("Camera", "object:/Script/Engine.CameraComponent"), var("Action Animation Name Next", "name"), var("Action Animation Name Current", "name"), var("current weapon", "object:" + P_WEAPON)], functions=[fn("Wanna Use This Item", [param("item name", "name")]), fn("Add Item to Shortcut", [param("item name", "name"), param("group", "int"), param("gun", "object:" + P_WEAPON)]),   # inventory tab
                                                fn("Save Appearance"), fn("Is Input Enabled ?", outputs=[param("yes", "bool")], pure=True), fn("Wanna Running"),
                                                fn("Use Clothes from Bag", [param("clothes name", "name"), param("is wear", "bool")]),
                                                fn("Got Clothes", [param("clothes name", "name"), param("wear", "bool")]),
                                                fn("Get Makeup Data", outputs=[param("Makeup Data", "object:" + P_MAKEUP_SAVE)]),
                                                fn("Change Skin", [param("SkinName", "name")]), fn("Update Makeup Texture"), fn("Update Eyes Style"), fn("Save Makeup Data to File"), fn("Load Player Makeup"),
                                                fn("Play Montage With Name", [param("montage name", "name"), param("ignore when the montage playing", "bool")]),
                                                fn("Change Next Action Animation", [param("Next Action Name", "name")]), fn("Stop Action Animation"), fn("Is Alive ?", outputs=[param("yes", "bool")], pure=True),
                                                fn("Get Hairstyle Name", outputs=[param("name", "name")], pure=True), fn("Get Hairstyle Color", outputs=[param("color", S_LINCOLOR)], pure=True),
                                                fn("Change Hairstyle", [param("Hairstyle", "name")]), fn("Change Hairstyle Color", [param("color", S_LINCOLOR, ref=True)]),
                                                fn("Apply Makeup Preset", [param("data", "struct:" + P_PRESET_S, ref=True)])]),
    # Jodi's parent in the game (the kit has no such asset): what AltUI puts on the body, face and colours through "Wearer" -
    # the main menu's figure (Jodi_Intro) is a Jodi_Base, not a Jodi. Members as the game declares them on Jodi_Base.
    blueprint(P_JODI_BASE, P_CPB, variables=[var("Eye Material", "object:/Script/Engine.MaterialInstanceDynamic"), var("Eyelashes Material", "object:/Script/Engine.MaterialInstanceDynamic"), var("Makeup Tex", "object:/Script/Engine.TextureRenderTarget2D")],
              functions=[fn("Get Makeup Data", outputs=[param("Makeup Data", "object:" + P_MAKEUP_SAVE)]), fn("Update Makeup Texture"), fn("Load Player Makeup"),
                         fn("Update Makeup Texture Ex", [param("tex", "object:/Script/Engine.TextureRenderTarget2D"), param("makeup data", "name", "map", value_type="struct:" + P_MDATA_S, ref=True)])]),   # followers: a figure's own make-up target
    # followers (docs/specs/2026-10-09-followers-design.md): NPC_Female and its parents, only what AltUI overrides or calls
    # Weapons (name -> weapon actor): on Character_Player_Base as in the game (the old kit had it on Jodi); Jodi and the followers inherit it
    # Check Appearence: the follower overrides it (it would put the game's default clothes on a figure without clothes components)
    # heels (Clothes_Comp.Wear of heeled shoes: Set Heel Height + Feet Additive; the anims read Heels Height Ratio / Feet Additive): the follower copies them
    blueprint(P_CPB, mode="augment", variables=[var("Weapons", "name", "map", value_type="object:" + P_WEAPON), var("in hand weapon", "object:" + P_WEAPON), var("Heels Height Ratio", "float"), var("Heel Height", "float"),
                                                var("Feet Additive", "float"),
                                                var("Save Player Clothes", "name", "array"),   # On Begun Play puts these on (Wear These Clothes), then clears them
                                                var("Save Clothes Damaged", "name", "map", value_type="float"),   # damage per piece (Store / Get Clothes Damage)
                                                var("Hair Comps", "object:" + P_HAIRC, "array"), var("clothes component list", "object:" + P_CC, "array"),
                                                var("Zombie in front of me", "object:" + P_CB), var("is paralleled animation playing", "bool")],   # ALTUI_FOLLOG (Fol Debug)
              functions=[fn("Check Appearence"), fn("Set Heel Height", [param("height ratio", "float"), param("thickness", "float")]),
                         fn("Change Hairstyle Ex", [param("hairstyle", "name")]),   # the hairstyle's Hair_Comps (HairstyleTable), unknown row -> the first
                         fn("check clothes covering"),
                         # Jason: his death skips Character_NPC's (that one calls the controller's on Character Die = Game Over for Jason_Controller)
                         fn("Character Die", [param("murderer", "object:" + P_CB)]),
                         # Jason: every weapon's montage goes through here - a foreign one (Jodi's skeleton) becomes his own
                         fn("Play Montage", [param("AnimMontage", "object:/Script/Engine.AnimMontage"), param("StartSectionName", "name")], [param("duration", "float")]),
                         fn("Attach Weapon to Right Hand"),
                         # the game's reload asks this (Npc_Controller.Try to Reload, Weapon_Gun_Base.New Mag Installed): the follower overrides it for infinite ammo
                         fn("Count Weapon Ammo", [param("weapon", "object:" + P_WEAPON)], [param("num", "int")], pure=True)]),   # the underwear rule (Bra01 / Briefs01 unless Is Nude Allowed); the follower's Check Appearence calls it
    # on Spawn in Runtime: the game's start of a figure spawned while playing (-> On Begun Play: anim class, order, health)
    blueprint(P_CNPC, P_CPB, variables=[var("Distance to Master", "float")], functions=[fn("Need to Save", outputs=[param("yes", "bool")], pure=True), fn("Mutate"), fn("on Spawn in Runtime"),
                                                                                 fn("Ani Notify Grab Weapon", [param("equip", "bool")])],   # Jason: a weapon on a socket he lacks goes to Prop_R
              remove_functions=["Character Die"]),   # since 2026-10-18 on Character_Player_Base (Jason's death skips Character_NPC's)
    # Jason (story NPC): State > 0 starts him in On Begun Play (Init Jason: Jason_Controller), 1 = hammer, 2 = Glock
    blueprint(P_JASON, P_CNPC, variables=[var("State", "int")], functions=[fn("Got Glock")]),   # Got Glock: his own (Jason_Glock: his montages) - a given Glock becomes it
    blueprint(P_NPCF, P_CNPC, variables=[var("save order", "name"), var("Order Location", "struct:/Script/CoreUObject.Vector"),
                                         var("Npc Name", "name")],   # Get Character Name -> VoiceTable row (Female_1..4): no name, no voice   # On Begun Play gives the controller these
              functions=[fn("delay to mutant"), fn("Apply Npc Appearance"), fn("Init Npc Appearance")]),   # the follower applies its look in Apply, rolls nothing in Init
    blueprint(P_NPCCTRL, "/Script/AIModule.AIController", variables=[var("master", "object:" + P_JODI), var("Order Location", "struct:/Script/CoreUObject.Vector"),   # Fol Spawn: order + place straight to the controller
                                                                                   var("Current Order", "name"), var("walking state", "int"), var("is busy", "bool")],   # Current Order: Fol Sync (the game's NPC menu); the last two: ALTUI_FOLLOG
              functions=[fn("Change Order", [param("order", "name")]), fn("Receive Order", [param("order", "name")]),   # Receive Order: as the game's NPC menu (voice, stay = here)
                         fn("Decide Next State")]),   # the orders (follow: walk to master); Jason_Controller's own never calls it, the prototype's controller does
    blueprint(P_JASONCTRL, P_NPCCTRL),   # Jason's AI: the prototype's controller derives from it
    blueprint(P_ATTUI, E_USERWIDGET),   # pop(): moved above AltUI's panel (the game adds it to the player screen, under every viewport widget)
    blueprint(P_GS, mode="augment", functions=[fn("Get Wardrobe Data", outputs=[param("wardrobe data", "object:" + P_WD)]),
                                               fn("Get Attention UI", outputs=[param("AttentionUI", "object:" + P_ATTUI)])]),
    # Backpack: Bag_Comp (kit), PlayingHud/InventoryPanel (new, repair only), TKA_GameState (UserInterface, Default Underwear)
    blueprint(P_BAG, mode="augment", variables=[var("Clothes in bag", "name", "array"), var("bag Tools", "name", "map", value_type="int"),   # inventory tab: items, weight
                                                var("total weight", "int"), var("weight capacity", "int"), var("Over weight ratio", "float")],
              functions=[fn("Count Items", [param("item name", "name")], [param("count", "int")], pure=True),
                         fn("Can I Pickup This Item ?", [param("item", "name"), param("num", "int"), param("is clothes", "bool")], [param("ok", "bool")], pure=True),
                         fn("Has this Clothes ?", [param("clothes name", "name")], [param("yes", "bool")], pure=True),
                         fn("Add Clothes To Bag", [param("itemName", "name")]), fn("Remove Clothes", [param("clothes", "name")]),
                         fn("Append Clothes", [param("Clothes", "name", "array", ref=True)]),   # followers: a figure's pieces before its start
                         fn("Is Bag Full ?", outputs=[param("yes", "bool")], pure=True)]),
    blueprint(P_INV, E_USERWIDGET, functions=[fn("Repair Clothes", [param("clothes", "name"), param("all", "bool")], [param("done", "bool")]),
                                              fn("Remove all undressed clothes")]),
    blueprint(P_INVNPC, E_USERWIDGET),   # followers: Fol Watch compares the figures' clothes only while it is shown
    blueprint(P_HUD, E_USERWIDGET, variables=[var("InventoryPanel", "object:" + P_INV), var("InventoryNpc", "object:" + P_INVNPC)],
              functions=[fn("Show Item Detail with Name", [param("item name", "name"), param("button", "object:" + E_WIDGET), param("gun", "object:" + P_WEAPON)])]),
    blueprint(P_GS2, mode="augment", variables=[var("UserInterface", "object:" + P_HUD), var("Default Underwear", "name", "array"),
                                                 var("photo mode camera", "object:/Script/Engine.Actor")],   # Camera_Free_C: held at real speed while AltUI stops time
              functions=[fn("Set Nude Allowed", [param("allow", "bool")]),   # real function in TKA_GameState_Base (Allow Naked); in game only reachable via a disabled cheat
                         # photo mode (Camera_Free + PhotoModeUI): entered from the game's pause menu; Is In Photo Mode = IsValid(photo mode camera)
                         fn("Enter Photo Mode"), fn("Try Exit Photo Mode"), fn("Is In Photo Mode", outputs=[param("yes", "bool")]),
                         fn("Show UI", [param("show", "bool")]), fn("Is UI Visible", outputs=[param("yes", "bool")]),   # the HUD (UserInterface), as the photo mode hides it
                         fn("Get Note Save", outputs=[param("note save", "object:" + P_NOTE_SAVE)]),
                         fn("Get Hyper Box Data", outputs=[param("data", "object:" + P_HBDATA)]),   # inventory tab: the global storage box
                         fn("Is Game Over ?", outputs=[param("yes", "bool")], pure=True)]),   # Close Panel: after the end the game's own screens keep the mouse
    blueprint(P_PC, mode="augment", variables=[var("Input Move Values", "struct:/Script/CoreUObject.Vector")],   # raw move input (idle pose: ends on it - a pose blocks the movement itself)
              functions=[fn("ShowMouseCursor", [param("show", "bool")]),
                                              fn("Set Widget Focus", [param("widget", "object:" + E_WIDGET)]),
                                              fn("Enable Player Control", [param("Base", "bool"), param("Playing", "bool")])]),
]
import menuscene
assets += menuscene.stubs()   # main menu scene picker: MainMenuUI, LoadingUI, Menu_Camera, LoadingPawn, Jodi_Intro (+ anim)
write(os.path.join(os.path.dirname(__file__), "..", "10_stubs.json"), assets)
