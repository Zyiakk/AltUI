"""Generates assets/10_stubs.json: stub additions + editor test rows in the stub tables (editor only, never end up in a pak)."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *
from slots import SLOTS

def row(t, group="None", icon=None, color=True):
    r = {"TypeName": t, "Group": group, "ColorAdjustable": color, "Quality": 2}
    return r

test_clothes = {
    "Briefs03": row("Briefs"), "Dress05": row("Dress", "Lace"), "Casual_Mina_Neck": row("Neck", "Kpop"),
    "Casual_Mina_Necklace": row("Necklace"), "SpikeBoots": row("Boots"), "Weird": row("Nonsense"),
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
    datatable(P_EYE_T, P_EYE_S, rows={"Eye_1": {"Type": "Eye"}}),
    datatable(P_MTYPE_T, P_MTYPE_S, rows={"Eyebrow": {"Single": True}, "Eye": {"Single": True, "EyeTable": True}, "Lips": {"Single": True, "Caption": "Lippen", "CameraPosition": 983}, "Cheeks": {"Single": False}}),
    datatable(P_DLC_T, P_DLC_S, rows={"Body_TestBody": {"Caption": "Test Body"}, "SomeMod": {"Caption": "Some Mod"}}),   # editor test: filter on prefix Body_
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
    blueprint(P_PSAVE, "/Script/Engine.SaveGame", variables=[var("Wear Clothes", "name", "array")]),   # player save game: pieces worn at save time
    blueprint(P_GI, "/Script/Engine.GameInstance", variables=[var("Hairstyles Save", "object:" + P_HAIR_SAVE)],
              functions=[fn("Save Hair Color Data", [param("player", "object:" + P_JODI)]), fn("Add Hairstyles", [param("hairstyle name", "name")])]),
    blueprint(P_PALR, E_USERWIDGET, variables=[var("Image_Color", "object:" + E_IMAGE)]),
    blueprint(P_PAL, E_USERWIDGET, variables=[var("Paletter", "object:" + P_PALR)],
              functions=[fn("Show Palette", [param("panel", "object:" + E_WIDGET), param("button", "object:" + E_WIDGET), param("flag", "int"), param("initial color", S_LINCOLOR)]),
                         fn("Close Frame")]),
    blueprint(P_WD, "/Script/CoreUObject.Object", variables=[var("Clothes", "name", "array")],
              functions=[fn("Has This Clothes", [param("clothes", "name")], [param("yes", "bool")], pure=True),
                         fn("Add Item And Save", [param("name", "name")], [param("new clothes", "bool")])]),
    blueprint(P_CC, "/Script/Engine.SkeletalMeshComponent",
              variables=[var("Color Adjustable", "bool"), var("Clothes Name", "name"), var("Type", "name")],
              functions=[fn("Change Color", [param("Color", S_LINCOLOR)])]),
    datatable(P_CTV, P_CS, rows=test_clothes),
    datatable("/Game/Mod/SomeMod/Mod_ClothesTable", P_CS, rows={"ModThing": row("Top")}),   # editor test: item origin = mod "SomeMod" (loader row in DLC_MainTable)
    datatable(P_CT, P_CS, composite=True, parent_tables=[P_CTV, "/Game/Mod/SomeMod/Mod_ClothesTable"]),
    struct(P_CTS, [param("CameraFocus", "int", internal_name="CameraFocus_17_DE98CCDE4FA8319FE550EC814F334C53")]),
    datatable(P_CTT, P_CTS, rows={s: ({"CameraFocus": 105} if s == "Boots" else {"CameraFocus": 365} if s == "Bra" else {}) for s in SLOTS}),
    datatable(P_CGV, P_CGS, rows={"Lace": {"GroupName": "Spitze", "Owning": False}, "Kpop": {"GroupName": "KPOP", "Owning": False}}),
    datatable(P_CG, P_CGS, composite=True, parent_tables=[P_CGV]),
    blueprint(P_CPB, mode="augment", functions=[
        fn("Wear The Clothes", [param("name", "name"), param("check covering", "bool"), param("update mask", "bool"), param("ignore compatible", "bool")], [param("successed", "bool")]),
        fn("Take off this clothes", [param("clothes name", "name")]),
        fn("Get Wearing Clothes Names", outputs=[param("clothes list", "name", "array")]),
        fn("is clothes wearing", [param("clothes name", "name")], [param("yes", "bool")], pure=True),
        fn("Find Clothes Component With Name", [param("name", "name")], [param("clothes comp", "object:" + P_CC)]),
        fn("Get Clothes Color", [param("clothes name", "name")], [param("found", "bool"), param("color", S_LINCOLOR)]),
        fn("Save Clothes Color", [param("clothes name", "name"), param("color", S_LINCOLOR)]),
        fn("Restore Clothes Color", [param("clothes", "name")]),
        fn("Is Clothes Damaged", [param("clothes", "name")], [param("yes", "bool")], pure=True),
        fn("Remove Clothing From Bag", [param("clothing name", "name")]), fn("Reset Clothes Physics")]),   # component "Bag" (Bag_Comp) exists in the kit
    blueprint(P_JODI, mode="augment", variables=[var("Camera", "object:/Script/Engine.CameraComponent")], functions=[fn("Save Appearance"), fn("Is Input Enabled ?", outputs=[param("yes", "bool")], pure=True),
                                                fn("Use Clothes from Bag", [param("clothes name", "name"), param("is wear", "bool")]),
                                                fn("Got Clothes", [param("clothes name", "name"), param("wear", "bool")]),
                                                fn("Get Makeup Data", outputs=[param("Makeup Data", "object:" + P_MAKEUP_SAVE)]),
                                                fn("Change Skin", [param("SkinName", "name")]), fn("Update Makeup Texture"), fn("Update Eyes Style"), fn("Save Makeup Data to File"), fn("Load Player Makeup"),
                                                fn("Play Montage With Name", [param("montage name", "name"), param("ignore when the montage playing", "bool")]),
                                                fn("Get Hairstyle Name", outputs=[param("name", "name")], pure=True), fn("Get Hairstyle Color", outputs=[param("color", S_LINCOLOR)], pure=True),
                                                fn("Change Hairstyle", [param("Hairstyle", "name")]), fn("Change Hairstyle Color", [param("color", S_LINCOLOR, ref=True)]),
                                                fn("Apply Makeup Preset", [param("data", "struct:" + P_PRESET_S, ref=True)])]),
    blueprint(P_GS, mode="augment", functions=[fn("Get Wardrobe Data", outputs=[param("wardrobe data", "object:" + P_WD)])]),
    # Backpack: Bag_Comp (kit), PlayingHud/InventoryPanel (new, repair only), TKA_GameState (UserInterface, Default Underwear)
    blueprint(P_BAG, mode="augment", variables=[var("Clothes in bag", "name", "array")],
              functions=[fn("Has this Clothes ?", [param("clothes name", "name")], [param("yes", "bool")], pure=True),
                         fn("Is Bag Full ?", outputs=[param("yes", "bool")], pure=True)]),
    blueprint(P_INV, E_USERWIDGET, functions=[fn("Repair Clothes", [param("clothes", "name"), param("all", "bool")], [param("done", "bool")]),
                                              fn("Remove all undressed clothes")]),
    blueprint(P_HUD, E_USERWIDGET, variables=[var("InventoryPanel", "object:" + P_INV)]),
    blueprint(P_GS2, mode="augment", variables=[var("UserInterface", "object:" + P_HUD), var("Default Underwear", "name", "array")],
              functions=[fn("Set Nude Allowed", [param("allow", "bool")])]),   # real function in TKA_GameState_Base (Allow Naked); in game only reachable via a disabled cheat
    blueprint(P_PC, mode="augment", functions=[fn("ShowMouseCursor", [param("show", "bool")]),
                                              fn("Set Widget Focus", [param("widget", "object:" + E_WIDGET)]),
                                              fn("Enable Player Control", [param("Base", "bool"), param("Playing", "bool")])]),
]
write(os.path.join(os.path.dirname(__file__), "..", "10_stubs.json"), assets)
