#!/usr/bin/env python3
"""Weapon skins and models – the single source for the generator (AltUI struct / manager) and the converter (weaponpak).

A weapon mod is a pak Mod/WeaponAltUI_<Name>/ for one weapon with one or both of:
  * textures  -> Mod_WeaponSkin  (row struct S_WeaponSkin), the skin axis of the tab
  * meshes    -> Mod_WeaponModel (row struct S_WeaponModel), the model axis
  * a shot sound -> Mod_WeaponSound (row struct S_WeaponSound), the sound axis
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
# Material: a model mod's own version of a game paint (see GAME_PAINTS) - the row is then that paint for the mod's model and
# carries no textures; appended last, so tables written before it read as before (the member is simply unset)
MEMBERS = [("Weapon", "name"), ("Caption", "text"), ("MainTex", "tex"), ("NormalTex", "tex"), ("MetallicTex", "tex"), ("Icon", "tex"), ("Material", "mat")]
MODEL_MEMBERS = [("Weapon", "name"), ("Caption", "text"), ("Icon", "tex")]
SOUND_STRUCT_PATH = "/Game/Mod/AltUI/S_WeaponSound"
SOUND_TABLE_NAME = "Mod_WeaponSound"
SOUND_MEMBERS = [("Weapon", "name"), ("Caption", "text"), ("Sound", "sound")]
TEX_MEMBERS = [m for m, t in MEMBERS if t == "tex"]

# The game's paints (Tables/GunPaint: row -> Guns {weapon: material}), read from the game 2026-10-20. The game puts the material
# on slot 0 of the weapon (Apply Gun Paint). A model mod that replaces one of these paths brings that paint made for its own
# mesh (Samurai Edge: M_Camo_Pistol = its M_SE_2 with a camo base colour); the converter turns it into a skin row with Material.
_M = "/Game/Project/Models/Weapon/"
GAME_PAINTS = {
    _M + "DesertEagle/Material/MI_Camo_DesertEagle": "Camo", _M + "DesertEagle/Material/MI_Pink_DesertEagle": "Pink",
    _M + "Glock/Materials/M_Camo_Pistol": "Camo", _M + "Glock/Materials/M_Pink_Pistol": "Pink",
    _M + "HK416/MI_Camo_HK416": "Camo", _M + "HK416/MI_Pink_HK416": "Pink",
    _M + "MGL/Camo_M32": "Camo", _M + "MGL/Pink_M32": "Pink",
    _M + "Revolver/Material/MI_Camo_Revolver_Silver": "Camo", _M + "Revolver/Material/MI_Pink_Revolver_Silver": "Pink",
    _M + "SA58/MI_Camo_SA58": "Camo", _M + "SA58/MI_Pink_SA58": "Pink",
    _M + "Shotgun/Material/MI_Camo_Shotgun": "Camo", _M + "Shotgun/Material/MI_Pink_Shotgun": "Pink",
    _M + "Speargun/MI_Camo_speargun_a": "Camo", _M + "Speargun/MI_Pink_speargun_a": "Pink",
    _M + "UMP45/Material/MI_Camo_UMP45": "Camo", _M + "UMP45/Material/MI_Pink_UMP45": "Pink",
}


def game_paint(package_path):
    """"Camo" / "Pink" when the path is one of the game's paint materials (any spelling), else None."""
    p = package_path.lower()
    return next((paint for path, paint in GAME_PAINTS.items() if path.lower() == p), None)
MESH_CLASSES = ("SkeletalMesh", "StaticMesh")   # what counts as a weapon model in a pak

# ItemTable rows with HyperBoxGroup "Weapon" (the tab lists these)
WEAPONS = ["Knife", "Hatchet", "Machete", "Wrench", "MonkeyWrench", "IronHammer", "Glock", "Revolver", "DesertEagle",
           "Shotgun", "UMP45", "HK416", "SA58", "Bow", "Speargun", "GrenadeLauncher"]
FOLDER_TO_WEAPON = {"m1014": "Shotgun", "mgl": "GrenadeLauncher"}   # Project/Models/Weapon/<folder> -> item name; other folders match a weapon name

# The game plays the actor variable `Shot Sound` (Weapon_Gun_Base_C.Shoot Fx); each weapon class sets it in Reset Default
# Attributes (Shotgun: class default). Value = (what Shot Sound is, the waves behind it when that is a SoundCue - the cue
# picks one of them at random). A replacer of any of these paths is a shot sound made for that weapon. From the game's
# bytecode, 2026-10-07; the waves read from the game's cues, 2026-10-20 (most cues have more than one: sound replacers
# that only swap the waves - GLOCK19SFX, Spas12_SFX - were not recognised before).
_S = "/Game/Project/Sounds/"
VANILLA_SHOT = {
    "HK416": (_S + "Weapons/HK416/HK416_Shot_Cue", (_S + "Weapons/HK416/HK416_Shot",)),
    "SA58": (_S + "Weapons/SA58/SA58_Shot_Cue", (_S + "Weapons/SA58/SA58_Shot",)),
    "UMP45": (_S + "Weapons/SMG_Single_Shot", (_S + "Weapons/SMG_Single_Shot_0",)),
    "DesertEagle": (_S + "Weapons/DesertEagle/DesertEagle_Shot", ()),
    "Glock": (_S + "Weapons/gun_pistol_shot", (_S + "Weapons/gun_pistol_shot_01", _S + "Weapons/gun_pistol_shot_02")),
    "Revolver": (_S + "Weapons/Revoler_Shot", (_S + "Weapons/Revoler_Shot_0", _S + "Weapons/Revoler_Shot_1")),
    "Shotgun": (_S + "Weapons/Shotgun_Shot", tuple(_S + "Weapons/Shotgun_Shot_%d" % i for i in range(3))),
    "GrenadeLauncher": (_S + "Weapons/GrenadeLauncher/GL_Shot", (_S + "Weapons/GrenadeLauncher/GL_Shot_0", _S + "Weapons/GrenadeLauncher/GL_Shot_1")),
    "Speargun": (_S + "Device/Speargun_Shot", ()),
}
# Shot sounds of the barrel attachments (Actors/Weapons/Equipment/Barrel/<part>.Shot Sound): with a suppressor on, the
# gun fires with the part's sound instead of its own. Not converted - a replacer of these (Marksman1A_SFX) is a sound
# for the part on every gun, not for one weapon.
SUPPRESSED_SHOT = {"Silencer_SDII": _S + "Weapons/Suppressed/M16_Single_Shot__Suppressed", "Silencer_PRS": _S + "Weapons/Suppressed/Silenced_Pistol_5"}


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


def sound_member_internal(i, name):
    """Internal name of member i of S_WeaponSound."""
    return "%s_%d_%s" % (name, 2 + 2 * i, hashlib.md5((SOUND_STRUCT_PATH + "/" + name).encode()).hexdigest().upper())


def sound_struct_members():
    return [(name, sound_member_internal(i, name), typ) for i, (name, typ) in enumerate(SOUND_MEMBERS)]


def shot_targets(package_path):
    """[(weapon, "sound" | "wave")] for a package path a replacer overwrites: "sound" = it IS the weapon's Shot Sound,
    "wave" = it is one of the waves behind the weapon's SoundCue. Case does not matter - replacers spell paths as they like."""
    p = package_path.lower(); out = []
    for weapon, (shot, waves) in VANILLA_SHOT.items():
        if p == shot.lower(): out.append((weapon, "sound"))
        elif any(p == w.lower() for w in waves): out.append((weapon, "wave"))
    return out


def suppressed_target(package_path):
    """The barrel part whose shot sound this path is, else None."""
    p = package_path.lower()
    return next((part for part, path in SUPPRESSED_SHOT.items() if p == path.lower()), None)


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
