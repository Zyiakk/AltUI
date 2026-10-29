"""Fingers and eyes of ragdoll figures (docs/specs/2026-10-26-ragdoll-finger-augen-design.md): data only, measured on the game's
mesh Character/Jodi/Body/Female and its animations with scripts/rag_detail_measure.py.
Left and right hand have the same local rotations (only positions are mirrored): one axis / angle serves both hands.
Fingers curl about their local -Z (Female_Idle_Grip against the reference pose); thumb_01 about THUMB1_AXIS. A curl is applied in
the bone's own space (ComposeRotators(A = delta, B = ref)); a lid closes like the game's additive Female_EyeClosed: delta in the
parent's space (ComposeRotators(A = ref, B = delta))."""

FINGERS = ["thumb", "index", "middle", "ring", "pinky"]
SIDES = ["l", "r"]
FINGER_BONES = ["%s_0%d_%s" % (f, j, s) for s in SIDES for f in FINGERS for j in (1, 2, 3)]   # index = side * 15 + finger * 3 + joint
LID_BONES = ["Eye_L", "Eye_R"]
DETAIL_BONES = FINGER_BONES + LID_BONES
GROUP_BONES = ["hand_l", "hand_r", "head"]   # a group's spheres show when the camera is near this bone
DETAIL_GROUP = {**{b: SIDES.index(b[-1]) for b in FINGER_BONES}, "Eye_L": 2, "Eye_R": 2}

# reference pose (local rotation, pitch / yaw / roll) of the game's mesh - scripts/rag_detail_measure.py
REF_ROT = {
    "thumb_01_l": (-35.202, -20.241, 93.685), "thumb_02_l": (-3.546, -15.552, -10.718), "thumb_03_l": (-0.553, 0.085, 4.322),
    "index_01_l": (-1.418, -13.005, 8.212), "index_02_l": (1.655, -9.978, -1.116), "index_03_l": (0.917, 1.726, 0.184),
    "middle_01_l": (1.026, -7.934, 3.228), "middle_02_l": (1.26, -14.356, 1.944), "middle_03_l": (-0.282, 2.628, 2.927),
    "ring_01_l": (5.606, -8.713, 3.609), "ring_02_l": (3.0, -13.978, -5.579), "ring_03_l": (-1.654, -1.993, -0.689),
    "pinky_01_l": (9.628, -7.556, 0.242), "pinky_02_l": (-0.385, -2.558, -1.587), "pinky_03_l": (2.884, -11.567, 6.689),
    "thumb_01_r": (-35.202, -20.242, 93.684), "thumb_02_r": (-3.546, -15.552, -10.718), "thumb_03_r": (-0.553, 0.084, 4.322),
    "index_01_r": (-1.418, -13.005, 8.212), "index_02_r": (1.648, -9.978, -1.116), "index_03_r": (0.917, 1.726, 0.185),
    "middle_01_r": (1.019, -7.935, 3.228), "middle_02_r": (1.273, -14.355, 1.942), "middle_03_r": (-0.291, 2.628, 2.927),
    "ring_01_r": (5.58, -8.715, 3.609), "ring_02_r": (3.026, -13.979, -5.586), "ring_03_r": (-1.644, -1.994, -0.689),
    "pinky_01_r": (9.628, -7.556, 0.241), "pinky_02_r": (-0.402, -2.558, -1.586), "pinky_03_r": (2.879, -11.57, 6.686),
    "Eye_L": (4.482, -14.831, -174.902), "Eye_R": (4.48, 165.168, 5.09),
}

CURL_AXIS = (0.0, 0.0, -1.0)            # every finger joint and thumb_02/03 (measured: Female_Idle_Grip)
THUMB1_AXIS = (-0.317, 0.945, -0.082)   # thumb_01 across the palm (measured)
CURL_DEG = {"thumb": (35.0, 40.0, 60.0), "index": (85.0, 100.0, 70.0), "middle": (85.0, 100.0, 70.0), "ring": (85.0, 100.0, 70.0),
            "pinky": (85.0, 100.0, 70.0)}   # a full fist per joint (grip measured 59 / 47 / 47 at about 2/3)
SPREAD_DEG = 25.0                       # thumb_01: "spread" turns it back out of the palm


def curl_axis(bone):
    return THUMB1_AXIS if bone.startswith("thumb_01") else CURL_AXIS


def curl_deg(bone):
    return CURL_DEG[bone.split("_")[0]][int(bone.split("_")[1]) - 1]


def spread_deg(bone):
    return SPREAD_DEG if bone.startswith("thumb_01") else 0.0


LID_AXIS = {"Eye_L": (-0.052, 0.106, 0.993), "Eye_R": (0.052, -0.106, 0.993)}   # Female_EyeClosed, last frame (additive)
LID_DEG = 40.0

# hand poses: curl of thumb, index, middle, ring, pinky (0 base pose .. 1 fist) and the thumb's spread (0..1)
HAND_POSES = [("Open", (0, 0, 0, 0, 0, 0.6)), ("Relaxed", (0.25, 0.2, 0.3, 0.4, 0.5, 0.2)), ("Fist", (1, 1, 1, 1, 1, 0)),
              ("ThumbsUp", (0, 1, 1, 1, 1, 0)), ("Peace", (1, 0, 0, 1, 1, 0)), ("Point", (1, 0, 1, 1, 1, 0)),
              ("Hold", (0.5, 0.6, 0.65, 0.7, 0.75, 0.1)), ("Base", (0, 0, 0, 0, 0, 0))]

DETAIL_NEAR = 100.0    # cm camera -> hand / head: its fine spheres show
DETAIL_TICK = 0.2      # s between proximity checks while spheres show
DETAIL_SCALE = 0.013   # sphere mesh scale: 1.3 cm
DETAIL_COLOR = "(R=0.9,G=0.9,B=0.9,A=1.0)"
GAZE_SIDE_DEG, GAZE_UP_DEG = 25.0, 20.0   # degrees off straight ahead for a full gaze morph
GAZE_SIDE_SIGN = 1.0   # +1: Face_Eye2Right looks to her right (play test ui-test-174 item 6; -1 if the eyes go the other way)
RAG_CURL_PX = 150.0    # mouse pixels along tip -> knuckle for a full curl
RAG_LID_STEP = 0.1     # lid closed share per wheel notch


def rot_lit(r):
    return "(Pitch=%s,Yaw=%s,Roll=%s)" % tuple(float(x) for x in r)


def vec_lit(v):
    return "(X=%s,Y=%s,Z=%s)" % tuple(float(x) for x in v)
