"""Foot IK (BenenG47's test chip): constants shared by ABP_BodyScale (gen_bodyscale.py) and the driver actor.

The driver sets the 22 ABP variables every frame; the 15 nodes are appended after the scales, leg spacing and angles, so IK
reads the scaled and shifted pose. All alphas default to 0 (off).
  - pelvis translate (IKPelvis) and the two foot tilts (TiltL/R), alpha ALeg
  - Pass A: TwoBoneIK foot_l / foot_r (effector EffL/R, joint calf), alpha ALeg
  - Pass B: forward foot, TwoBoneIK with a component-space joint target (FwdEffL/R, FwdJL/R), alpha AFwdL/R
  - Knee arc: thigh rotation KneeRotL/R and the foot rotated back KneeFootL/R, alpha AKnee
  - Hands: tilt HandTiltL/R, then TwoBoneIK hand_l / hand_r (HandEffL/R, joint lowerarm), alpha AHand
"""
VEC = "struct:/Script/CoreUObject.Vector"; ROT = "struct:/Script/CoreUObject.Rotator"
V0 = "(X=0,Y=0,Z=0)"; R0 = "(P=0,Y=0,R=0)"
# "IKPelvis", not BenenG47's "Pelvis": ABP_BodyScale already has a scale variable "Pelvis" (bodyscale_groups.GROUPS)
ABP_VECS = ["IKPelvis", "EffL", "EffR", "FwdEffL", "FwdEffR", "FwdJL", "FwdJR", "HandEffL", "HandEffR"]
ABP_ROTS = ["TiltL", "TiltR", "KneeRotL", "KneeRotR", "KneeFootL", "KneeFootR", "HandTiltL", "HandTiltR"]
ABP_ALPHAS = ["ALeg", "AFwdL", "AFwdR", "AKnee", "AHand"]
ABP_VARS = [(v, VEC, V0) for v in ABP_VECS] + [(v, ROT, R0) for v in ABP_ROTS] + [(v, "float", "0.0") for v in ABP_ALPHAS]


def abp_nodes():
    """Everything relative to the node's own input pose. Pass A = foot up, knee in its animated plane; pass B = forward foot
    with a component-space joint target from hip + foot (no knee: nothing feeds back); knee arc = thigh rotated about the
    hip-foot line (the foot is on it) and the foot rotated back."""
    n = [{"bone": "pelvis", "kind": "translate", "var": "IKPelvis", "alpha_var": "ALeg"},
         {"bone": "foot_l", "kind": "rotate", "var": "TiltL", "alpha_var": "ALeg"},
         {"bone": "foot_r", "kind": "rotate", "var": "TiltR", "alpha_var": "ALeg"}]
    for s, S_ in (("l", "L"), ("r", "R")):
        n.append({"bone": "foot_" + s, "kind": "twoboneik", "joint_bone": "calf_" + s, "var": "Eff" + S_, "alpha_var": "ALeg"})
    for s, S_ in (("l", "L"), ("r", "R")):
        n.append({"bone": "foot_" + s, "kind": "twoboneik", "joint_bone": "calf_" + s, "var": "FwdEff" + S_, "alpha_var": "AFwd" + S_,
                  "joint_var": "FwdJ" + S_, "joint_space": "component"})
    for s, S_ in (("l", "L"), ("r", "R")):
        n += [{"bone": "thigh_" + s, "kind": "rotate", "var": "KneeRot" + S_, "alpha_var": "AKnee"},
              {"bone": "foot_" + s, "kind": "rotate", "var": "KneeFoot" + S_, "alpha_var": "AKnee"}]
    n += [{"bone": "hand_l", "kind": "rotate", "var": "HandTiltL", "alpha_var": "AHand"},
          {"bone": "hand_r", "kind": "rotate", "var": "HandTiltR", "alpha_var": "AHand"}]
    for s, S_ in (("l", "L"), ("r", "R")):
        n.append({"bone": "hand_" + s, "kind": "twoboneik", "joint_bone": "lowerarm_" + s, "var": "HandEff" + S_, "alpha_var": "AHand"})
    return n
