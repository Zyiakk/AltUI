"""Body presets (internal design notes): presets per body chip on the Body Shape page. A preset holds
the body's slider factors (Body Scale Factors: N_SLIDERS, padded) and the game's breast / waist (Makeup Data Boobs Size /
Waist). One save for every body; a preset belongs to one body (None = the Standard chip)."""
M = "/Game/Mod/AltUI"
S_BODYPRESET = M + "/S_BodyPreset"; SG_BODYPRESETS = M + "/SG_BodyPresets"
SLOT = "AltUI_BodyPresets"; VERSION = 1
PHOTO_DIR = "SaveGames/AltUI/BodyPresets"   # under ProjectSavedDir; <Id>.png
PHOTO_KIND = "BodyPreset"                   # Manager.PhotoKind for Finish Photo
QUICK_KIND = "bodypreset"                   # quick menu item "bodypreset:<Id>"
NAME_MAX = 40
# S_BodyPreset members in order (new ones only appended); "Factors" is an array of float
MEMBERS = [("Body", "name"), ("Name", "string"), ("Id", "int"), ("Factors", "float"), ("Boobs", "float"), ("Waist", "float")]
