#!/usr/bin/env python3
"""Bone groups of ABP_BodyScale – the single source for the generator (gen_bodyscale.py), the converter (bodypak) and the manager UI.
Groups and bones follow the Nexus body 783 (proven in game); variables stay vectors so a per-axis mode needs no ABP change.
Every node is Additive (multiplies the animated scale): Replace nodes crashed NvCloth's fabric cooker when clothes were put on
(three crashes, Additive at the same scales does not). A modified bone's children inherit the change (FCSPose re-derives them from
their local transforms), so the scale along a chain compounds: the table stores NET scales per group and Apply Body Scales sets each
node to net(group) / net(parent group) - see PARENT_GROUP."""
import hashlib

ABP_PATH = "/Game/Mod/AltUI/ABP_BodyScale"; ABP_CLASS = "ABP_BodyScale_C"
STRUCT_PATH = "/Game/Mod/AltUI/S_BodyScale"
TABLE_NAME = "Body_Scale"; ROW_NAME = "Default"

# (variable, bones, ModifyBone ScaleMode) - Additive everywhere, see above
GROUPS = [
    ("Breasts", ["Breast_L", "Breast_R"], "Additive"),
    ("GlutesHips", ["Hip_L", "Hip_R"], "Additive"),
    ("Thighs", ["thigh_l", "thigh_r"], "Additive"),
    ("LowerThighs", ["thigh_twist_01_l", "thigh_twist_01_r"], "Additive"),
    ("UpperCalfs", ["calf_l", "calf_r"], "Additive"),
    ("LowerCalfs", ["calf_twist_01_l", "calf_twist_01_r"], "Additive"),
    ("Upperarms", ["upperarm_l", "upperarm_r"], "Additive"),
    ("Lowerarms", ["lowerarm_l", "lowerarm_r"], "Additive"),
    ("Hands", ["hand_l", "hand_r"], "Additive"),
    ("Feet", ["foot_l", "foot_r"], "Additive"),
    ("Waist", ["Morph_Waist"], "Additive"),   # the game's own waist morph bone (child of spine_01, no children); added after the others - older Body_Scale rows lack it
]
# per-axis weight of a slider factor (x = along the bone): axis = 1 + w * (f - 1), so 1 = the full factor, 0 = untouched. Limbs get
# thicker only, hands grow in every direction, feet longer + wider (foot: y = length, z = width); the waist follows the direction of the
# game's Female_Morph_Waist (Morph_Waist scale (-0.1, -0.4, 0) per unit -> x:y = 1:4, z untouched)
AXES = {v: (0, 1, 1) for v, _, _ in GROUPS}; AXES["Hands"] = (1, 1, 1); AXES["Waist"] = (0.25, 1, 0)
BONE_GROUP = {b: v for v, bs, _ in GROUPS for b in bs}
# nearest scaled ancestor of each group's bones (skeleton: foot < calf < thigh, calf_twist < calf, thigh_twist < thigh, hand < lowerarm < upperarm)
PARENT_GROUP = {"LowerThighs": "Thighs", "UpperCalfs": "Thighs", "LowerCalfs": "UpperCalfs", "Feet": "UpperCalfs", "Lowerarms": "Upperarms", "Hands": "Lowerarms"}
BONE_PARENT = {}
for g, pg in PARENT_GROUP.items():
    for b, pb in zip(dict((v, bs) for v, bs, _ in GROUPS)[g], dict((v, bs) for v, bs, _ in GROUPS)[pg]):
        BONE_PARENT[b] = pb


def descendants(bone):
    """Scaled bones below `bone` (transitively), from BONE_PARENT."""
    out = [b for b, pb in BONE_PARENT.items() if pb == bone]
    for b in list(out):
        out += descendants(b)
    return out
# Floor compensation (measured 2026-09-21, AltUI_Log "geom" lines): the height slider scales the mesh about its origin, which sits above the
# sole (ball_l already 4.2 cm below it: heels pose) - everything below the origin lifts by (1 - h) x its depth. The feet slider scales foot_l/r
# about the ankle (7.4 cm above the origin): the heel under the joint moves with the full factor, the toes (own ball joint) hardly at all.
# Two additive component-space translations in ABP_BodyScale put the sole back: root by S(1 - 1/h) (component space is scaled by h afterwards)
# and foot_l/r by A(f - 1). S, A are calibration constants (cm).
SOLE_BELOW_ORIGIN = 7.0   # S: sole depth below the mesh origin at scale 1
ANKLE_TO_SOLE = 10.0      # A: ankle-to-sole distance in the scaled (y/z) foot axes
SHIFTS = [("RootShift", ["root"]), ("FeetShift", ["foot_l", "foot_r"])]   # ABP vector variables (Z used) and the bones they translate


def root_shift(h):
    """Component-space Z shift of the root bone for height factor h (0 at 1.0; negative = down)."""
    return SOLE_BELOW_ORIGIN * (1.0 - 1.0 / h)


def feet_shift(f):
    """Component-space Z shift of the foot bones for feet factor f (0 at 1.0; negative = down)."""
    return ANKLE_TO_SOLE * (f - 1.0)


# slider key -> groups it drives (uniform factor on y and z of every group)
SLIDERS = [("Breast", ["Breasts"]), ("Glutes", ["GlutesHips"]), ("Thighs", ["Thighs", "LowerThighs"]),
           ("Calves", ["UpperCalfs", "LowerCalfs"]), ("Arms", ["Upperarms", "Lowerarms"]), ("Hands", ["Hands"]), ("Feet", ["Feet"]),
           ("Height", []),   # no bone group: the whole mesh component is scaled (SetRelativeScale3D) - physics, cloth and attachments follow, works without the ABP
           ("Waist", ["Waist"])]   # appended last: factor arrays saved before it (8 entries) are padded with 1.0 (Body Scale Factors)
N_SLIDERS = len(SLIDERS); HEIGHT_INDEX = 7


def member_internal(i, name):
    """Internal name of member i of S_BodyScale (same formula as bpdsl.struct: <Name>_<2+2i>_<MD5(path/name)>)."""
    return "%s_%d_%s" % (name, 2 + 2 * i, hashlib.md5((STRUCT_PATH + "/" + name).encode()).hexdigest().upper())


def struct_members():
    return [(v, member_internal(i, v)) for i, (v, _, _) in enumerate(GROUPS)]


FACTOR_MIN, FACTOR_MAX = 0.5, 2.0
# per-slider factor ranges (in-game findings 2026-09-19): height 1.2 still fits through doors, feet tip beyond 1.1, hands/arms/legs bend
RANGES = {"Height": (0.9, 1.2), "Feet": (0.8, 1.1), "Hands": (0.8, 1.3), "Arms": (0.7, 2.0), "Calves": (0.8, 1.8), "Thighs": (0.8, 1.8), "Breast": (0.7, 1.7),
          "Waist": (1.5, 0.6)}   # waist: reversed (left = wider) like the game's own waist slider; 0.6 on y = one more full vanilla morph
SLIDER_ORDER = ["Height", "Breast", "Waist", "Glutes", "Thighs", "Calves", "Arms", "Hands", "Feet"]   # rows on the Body Shape page (the factor array keeps SLIDERS' order)
# The game's breast / waist values are the Alpha of an "Apply Additive" node in Jodi_Anim (Female_Morph_Breasts = scale of Breast_L/R,
# Female_Morph_Waist = scale of Morph_Waist); FInputScaleBias::ApplyTo clamps that Alpha to 0..1 in the engine (InputScaleBias.cpp), so
# values outside 0..1 change nothing (checked 2026-09-21, an extended -0.5..1.5 range had no visible effect). Beyond 100 % the bone
# slider "Breast" (Breast_L/R via ABP_BodyScale) takes over.
VANILLA_RANGE = (0.0, 1.0)


def factor_range(key):
    """(factor at slider 0, factor at slider 1) - may be descending (Waist)."""
    return RANGES.get(key, (FACTOR_MIN, FACTOR_MAX))


def slider_factor(v, key=None):
    """Slider 0..1 -> factor within the slider's range."""
    lo, hi = factor_range(key); return lo + (hi - lo) * v


def slider_value(f, key=None):
    lo, hi = factor_range(key); return (f - lo) / (hi - lo)
