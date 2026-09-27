#!/usr/bin/env python3
"""Weapon skins and models – the single source for the generator (AltUI struct / manager) and the converter (weaponpak).

A weapon mod is a pak Mod/WeaponAltUI_<Name>/ for one weapon with one or both of:
  * textures  -> Mod_WeaponSkin  (row struct S_WeaponSkin), the skin axis of the tab
  * meshes    -> Mod_WeaponModel (row struct S_WeaponModel), the model axis
Both in one pak is the normal case for a mod that ships a model with matching skins; the game keys a mod row by the pak
name, so one pak has exactly one mod folder - which is why the prefix covers both kinds. The prefix says out loud
that the pak is built for AltUI: a plain Weapon_<Name> would be a name any weapon mod might pick for itself."""
import hashlib, re

STRUCT_PATH = "/Game/Mod/AltUI/S_WeaponSkin"
TABLE_NAME = "Mod_WeaponSkin"
MODEL_STRUCT_PATH = "/Game/Mod/AltUI/S_WeaponModel"
MODEL_TABLE_NAME = "Mod_WeaponModel"
MOD_PREFIX = "WeaponAltUI_"                     # what the converter writes
MOD_PREFIXES = ("WeaponAltUI_",)                # what the manager's scan accepts
MEMBERS = [("Weapon", "name"), ("Caption", "text"), ("MainTex", "tex"), ("NormalTex", "tex"), ("MetallicTex", "tex"), ("Icon", "tex")]
MODEL_MEMBERS = [("Weapon", "name"), ("Caption", "text"), ("Icon", "tex")]
TEX_MEMBERS = [m for m, t in MEMBERS if t == "tex"]
MESH_CLASSES = ("SkeletalMesh", "StaticMesh")   # what counts as a weapon model in a pak

# ItemTable rows with HyperBoxGroup "Weapon" (the tab lists these)
WEAPONS = ["Knife", "Hatchet", "Machete", "Wrench", "MonkeyWrench", "IronHammer", "Glock", "Revolver", "DesertEagle",
           "Shotgun", "UMP45", "HK416", "SA58", "Bow", "Speargun", "GrenadeLauncher"]
FOLDER_TO_WEAPON = {"m1014": "Shotgun", "mgl": "GrenadeLauncher"}   # Project/Models/Weapon/<folder> -> item name; other folders match a weapon name


def member_internal(i, name):
    """Internal name of member i of S_WeaponSkin (same formula as bpdsl.struct: <Name>_<2+2i>_<MD5(path/name)>)."""
    return "%s_%d_%s" % (name, 2 + 2 * i, hashlib.md5((STRUCT_PATH + "/" + name).encode()).hexdigest().upper())


def struct_members():
    return [(name, member_internal(i, name), typ) for i, (name, typ) in enumerate(MEMBERS)]


def model_member_internal(i, name):
    """Internal name of member i of S_WeaponModel."""
    return "%s_%d_%s" % (name, 2 + 2 * i, hashlib.md5((MODEL_STRUCT_PATH + "/" + name).encode()).hexdigest().upper())


def model_struct_members():
    return [(name, model_member_internal(i, name), typ) for i, (name, typ) in enumerate(MODEL_MEMBERS)]


def weapon_of_folder(folder):
    """Weapon (ItemTable row) of a Models/Weapon/<folder> path segment, None if unknown."""
    f = folder.lower()
    if f in FOLDER_TO_WEAPON: return FOLDER_TO_WEAPON[f]
    for w in WEAPONS:
        if w.lower() == f: return w
    return None


def tex_role(filename):
    """Texture parameter of a skin texture by its file name; None = not one of the three."""
    n = re.sub(r"\.(uasset|uexp|ubulk)$", "", filename.lower())
    for suffix, role in ((("_basecolor", "_bc", "_albedo", "_d"), "MainTex"),
                         (("_normal", "_n"), "NormalTex"),
                         (("_occlusionroughnessmetallic", "_orm", "_m"), "MetallicTex")):
        if n.endswith(suffix): return role
    return None
