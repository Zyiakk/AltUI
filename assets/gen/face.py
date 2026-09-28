"""Face tab: the entries and the names of the face morph targets on Jodi's body mesh (Character/Jodi/Body/Female).

A face is a map morph name -> weight. Only the morphs set on the tab are in it; a missing morph is left to the
animation ("game"), an empty map is the game's own face. The values go onto Character.Mesh with SetMorphTarget, which the
engine (4.27) applies after the animation curves - so they hold during poses too (docs/notes/2026-09-27-gesichtsausdruck-override.md).
A bipolar entry (gaze) is one slider over two morphs: negative -> the first at |v|, positive -> the second, the other at 0.
"""
M = "/Game/Mod/AltUI"
S_FACE = M + "/S_Face"; SG_FACES = M + "/SG_Faces"; FACES_SLOT = "AltUI_Faces"

GROUPS = ["FaceExpr", "FaceEyes", "FaceMouth"]   # slider groups, in the order of the left column
SAVED = "FaceSaved"                              # the saved faces (tiles)

# (key, group, neg_morph or None, morph); caption string key = "Face_" + key
ENTRIES = [
    ("Idle", "FaceExpr", None, "Face_Idle"),
    ("Focus", "FaceExpr", None, "Face_Focus"),
    ("Smile", "FaceExpr", None, "Face_Smile"),
    ("Pain", "FaceExpr", None, "Face_Pain"),
    ("Fright", "FaceExpr", None, "Face_Fright"),
    ("Tired", "FaceExpr", None, "Face_Tired"),
    ("Suffering1", "FaceExpr", None, "Face_Sufferring01"),   # the game's spelling
    ("Suffering2", "FaceExpr", None, "Face_Sufferring02"),
    ("LookSide", "FaceEyes", "Face_Eye2Left", "Face_Eye2Right"),
    ("LookUpDown", "FaceEyes", "Face_Eye2Up", "Face_Eye2Down"),
    ("MouthAH", "FaceMouth", None, "Mouth_AH CDG KN"),
    ("MouthEE", "FaceMouth", None, "Mouth_EE"),
    ("MouthUU", "FaceMouth", None, "Mouth_UU OO"),
    ("MouthFV", "FaceMouth", None, "Mouth_FV"),
    ("MouthTH", "FaceMouth", None, "Mouth_TH L"),
    ("MouthBPM", "FaceMouth", None, "Mouth_BPM"),
    ("MouthSH", "FaceMouth", None, "Mouth_Zh Ch SH RI"),
    ("MouthClose", "FaceMouth", None, "Mouth_Close"),   # virtual: pulls Mouth_AH below 0 (see VIRTUAL)
]

# keys of FaceValues that are no morph of their own: key -> (morph, factor). Mouth_Close counters the opening every
# expression brings along (measured on the mesh: Smile 0.22, Tired 0.37, Pain 0.54 of a full Mouth_AH):
# Mouth_AH = (Mouth_AH value or 0) - Mouth_Close, set as soon as one of the two is fixed.
VIRTUAL = {"Mouth_Close": ("Mouth_AH CDG KN", -1.0)}

# the full-face expressions: each one carries a whole face, so two at full weight add up (mouth opens further).
# Blending (the default) scales them together down to a sum of 1.
EXPRESSIONS = [e[3] for e in ENTRIES if e[1] == "FaceExpr"]


def morphs_of(entry):
    """The morph names one entry writes."""
    return [m for m in (entry[2], entry[3]) if m]


KEYS = [m for e in ENTRIES for m in morphs_of(e)]          # every key FaceValues can hold
MORPHS = [m for m in KEYS if m not in VIRTUAL]              # the real morph targets
