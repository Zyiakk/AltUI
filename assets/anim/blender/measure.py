"""Measurements of a walk cycle in armature space (cm; Jodi faces -Y, +x her left, +z up) for the animation pipeline:
foot paths, stance phases, lateral foot position at contact, stance speed (the in-place walk slides the planted foot backwards at the
walk speed - on Female_Walk this must give its MoveData_Speed of 208), slide of the planted foot, lowest foot height, knee angles.
Used by scripts/animmeasure.py (report)."""
import math
import bpy
from mathutils import Vector

FEET = {"l": ("thigh_l", "calf_l", "foot_l", "ball_l"), "r": ("thigh_r", "calf_r", "foot_r", "ball_r")}


def sample(arm, frames):
    """Per frame: armature-space matrices of the bones we look at."""
    sc = bpy.context.scene; out = []
    names = ["pelvis", "spine_03", "head", "upperarm_l", "upperarm_r", "lowerarm_l", "lowerarm_r", "hand_l", "hand_r"] + [b for v in FEET.values() for b in v]
    for f in range(frames):
        sc.frame_set(f); out.append({n: arm.pose.bones[n].matrix.copy() for n in names})
    return out


def stance_flags(z, ys, frames):
    """Planted = low (within 4 cm of the lowest point) and sliding backwards (+y; the walk is in place, only the standing foot moves back).
    Height alone also catches the swinging foot passing low under the body."""
    zmin = min(z); n = frames - 1
    return [z[f] < zmin + 4.0 and ys[(f + 1) % n] - ys[f] > 0.0 for f in range(frames)]


def knee_angle(s, side):
    th, ca, fo, _ = FEET[side]
    a, b, c = s[th].to_translation(), s[ca].to_translation(), s[fo].to_translation()
    u, v = (a - b).normalized(), (c - b).normalized()
    return math.degrees(math.acos(max(-1.0, min(1.0, u.dot(v)))))   # 180 = straight


def analyze(arm, frames, fps=30.0):
    S = sample(arm, frames); res = {"frames": frames}
    mid_x = sum(s["pelvis"].to_translation().x for s in S) / frames          # her midline (in-place walk)
    res["midline_x"] = mid_x
    for side in ("l", "r"):
        foot = FEET[side][2]
        z = [s[foot].to_translation().z for s in S]; zmin = min(z)
        ys = [s[foot].to_translation().y for s in S]; xs = [s[foot].to_translation().x for s in S]
        stance = stance_flags(z, ys, frames)
        # stance speed: slope of y over the core of the longest stance run (contact and lift-off trimmed: the foot still moves there)
        runs, cur = [], []
        for f in range(frames - 1):
            if stance[f]: cur.append(f)
            elif cur: runs.append(cur); cur = []
        if cur: runs.append(cur)
        core = max(runs, key=len)[3:-3] if runs else []
        st_v = []
        if len(core) > 2:
            n = len(core); tm = sum(core) / n; ym = sum(ys[f] for f in core) / n
            slope = sum((f - tm) * (ys[f] - ym) for f in core) / sum((f - tm) ** 2 for f in core)
            st_v = [-slope * fps if -slope * fps > 0 else slope * fps]
        lat = [xs[f] - mid_x for f in range(frames) if stance[f]]
        slide_x = (max(lat) - min(lat)) if lat else 0.0
        res[side] = {"stance_frames": sum(stance[:-1]), "stance_speed": st_v[0] if st_v else 0.0,
                     "lateral_contact": sum(lat) / len(lat) if lat else 0.0, "lateral_slide": slide_x, "lowest_z": zmin,
                     "knee_min": min(knee_angle(s, side) for s in S), "knee_max": max(knee_angle(s, side) for s in S)}
    res["speed"] = (res["l"]["stance_speed"] + res["r"]["stance_speed"]) / 2.0
    # legs passing each other: smallest distance between the left and right knee-to-ankle and hip-to-knee segments (bone axes; the mesh is
    # about 5 cm thick around the knee / calf, so axes closer than ~10 cm mean the legs touch)
    def seg_dist(a0, a1, b0, b1, n=12):
        return min(((a0 + (a1 - a0) * (i / n)) - (b0 + (b1 - b0) * (j / n))).length for i in range(n + 1) for j in range(n + 1))
    res["calf_gap"] = min(seg_dist(s["calf_l"].to_translation(), s["foot_l"].to_translation(), s["calf_r"].to_translation(), s["foot_r"].to_translation()) for s in S)
    # hand against the hip / thigh of its side (axis distance; thigh ~8 cm, hand ~3 cm thick near the hip -> below ~11 cm they touch)
    def pt_seg(p, a, b):
        ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared)); return (p - (a + ab * t)).length
    res["hand_gap"] = min(pt_seg(s["hand_" + sd].to_translation(), s["thigh_" + sd].to_translation(), s["calf_" + sd].to_translation()) for s in S for sd in ("l", "r"))
    res["thigh_gap"] = min(seg_dist(s["thigh_l"].to_translation(), s["calf_l"].to_translation(), s["thigh_r"].to_translation(), s["calf_r"].to_translation()) for s in S)
    # knees bending sideways (X / O legs): on bent frames the angle between the bend plane's normal (joint positions) and the thigh's
    # hinge axis (its local axis most in line with that normal) - the kneecap points along the thigh's twist, so a bend out of that
    # plane folds the leg sideways; max over the cycle and the largest jump between two frames
    for side in ("l", "r"):
        th, ca, fo, _ = FEET[side]; bent = [s for s in S if knee_angle(s, side) < 165]; best = None
        nrm = lambda s: (s[ca].to_translation() - s[th].to_translation()).cross(s[fo].to_translation() - s[th].to_translation()).normalized()
        for k in range(3):
            acc = sum(s[th].to_3x3().col[k].normalized().dot(nrm(s)) for s in bent)
            if best is None or abs(acc) > abs(best[1]): best = (k, acc)
        offs = [math.degrees(math.acos(max(-1.0, min(1.0, abs(s[th].to_3x3().col[best[0]].normalized().dot(nrm(s))))))) for s in bent]
        res[side]["knee_off"] = max(offs) if offs else 0.0; res[side]["knee_off_step"] = max([abs(offs[i + 1] - offs[i]) for i in range(len(offs) - 1)] or [0.0])
    # arms against the body: horizontal distance of elbow / hand from the spine line (pelvis -> spine_03), smallest over the cycle
    def spine_dist(s, p):
        a, b = s["pelvis"].to_translation(), s["spine_03"].to_translation(); return math.hypot(*(p - (a + (b - a) * max(0.0, min(1.0, (p - a).dot(b - a) / (b - a).length_squared))))[:2])
    res["elbow_body"] = min(spine_dist(s, s["lowerarm_" + sd].to_translation()) for s in S for sd in ("l", "r"))
    res["hand_body"] = min(spine_dist(s, s["hand_" + sd].to_translation()) for s in S for sd in ("l", "r"))
    return res, S
