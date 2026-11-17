"""Reference model of the per-frame Foot IK maths. Origin: BenenG47's test chip BP_FootIKTest (spec 5.2 of the Foot IK design).
The Blueprint generator builds the same steps as nodes; tests/unit/test_footik_sim.py checks this model on the game's
measured poses (tests/unit/fixtures/footik/measure.json, private).
Units: cm, deg, s. Heights are relative to the capsule floor; "foot_h" = animated ankle height above floor - FootHeight."""
import math

ROUND3 = {"StillSpeed": 10.0, "PlantedHeight": 12.0, "MinPelvisHeight": 20.0, "FootHeight": 7.5,
            "TraceUp": 50.0, "TraceDown": 60.0, "MaxStep": 40.0, "MaxTilt": 30.0, "MaxPelvisDrop": 40.0,   # round 3: 40 / 40
            "BlendTime": 0.25, "Smoothing": 12.0,
            # round 2 (spec 7c): pose types and their modes (0 Off / 1 Legs only / 2 Legs + hips)
            "SitMode": 1, "KneelMode": 0, "KneelKnee": 15.0, "SitHoriz": 25.0,
            # round 3 (spec 7d): knee follows foot, knee contact, hand contact (toggles 1 = on)
            "KneeFollow": 70.0, "FwdSame": 10.0, "KneeOn": 1, "KneeNear": 12.0, "MaxKneeLift": 30.0, "MaxKneeHip": 30.0,
            "HandOn": 1, "HandNear": 15.0, "MaxHandStep": 20.0, "MaxHandTilt": 30.0,
            # final review C1: pass B (forward foot) fades in over FwdBlend cm; its joint target lies FwdReach cm ahead / above
            "FwdBlend": 3.0, "FwdReach": 50.0}
# round 4 (spec 7e): crouch pose type, still hands, the on-screen Status box (Dbg*)
NEW4 = {"CrouchBelow": 57.0, "CrouchMode": 1, "CrouchDrop": 10.0, "HandStill": 10.0, "HandStillFor": 1.5,
        "DbgShow": 1, "DbgX": 1.0, "DbgY": 62.0, "DbgSize": 100.0}
# BenenG47's tuned round-3 values (2026-11-09) = the defaults from round 4 on (the round-3 tests keep ROUND3 + NEW4)
TUNED_R3 = {"StillSpeed": 1.0, "PlantedHeight": 100.0, "MinPelvisHeight": 0.0, "FootHeight": 30.0, "TraceUp": 80.0, "TraceDown": 80.0,
          "MaxStep": 75.0, "MaxTilt": 25.0, "MaxPelvisDrop": 100.0, "BlendTime": 0.5, "Smoothing": 10.0, "KneeFollow": 20.0,
          "FwdSame": 50.0, "FwdBlend": 1.0, "FwdReach": 40.0, "KneelKnee": 15.0, "SitHoriz": 25.0}
# BenenG47's FINAL values (2026-11-09, end of stage 1: screenshots Default_values01/02 = FootIKTest.sav = AltUI Preset 1; spec 7f).
# Knee / hand contact off by default (BenenG47 switches them on for poses only), so "still for" 0 is fine.
FINAL = {"PlantedHeight": 30.0, "FootHeight": 7.5, "MaxPelvisDrop": 75.0, "KneeFollow": 30.0, "FwdSame": 15.0, "KneelMode": 1,
         "KneeOn": 0, "HandOn": 0, "HandStillFor": 0.0, "DbgX": 0.0, "DbgY": 93.0, "DbgSize": 165.0}
DEFAULTS = {**ROUND3, **TUNED_R3, **NEW4, **FINAL}


def clamp(v, lo, hi): return max(lo, min(hi, v))


HARD_OFF = ("ragdoll", "fitting", "cutscene", "climbing", "jumping")   # spec 7b/7c: always weight 0, in this order (after "off")
MODE_OFF, MODE_LEGS, MODE_FULL = 0, 1, 2   # pose mode choices: Off / Legs only (no hip drop) / Legs + hips


def pose_type(inp, p):
    """'feet' (a foot not planted) / 'kneel' (both knees low, pelvis over the feet) / 'lying' (pelvis low: lying, floor
    sitting) / 'sit' (pelvis far from the feet horizontally: chair) / 'stand'. Measured thresholds: spec 7c."""
    if max(inp["foot_h"]) > p["PlantedHeight"]: return "feet"
    if max(inp["knee_h"]) < p["KneelKnee"] and inp["pelvis_horiz"] < p["SitHoriz"]: return "kneel"
    if inp["pelvis_above_feet"] < p["MinPelvisHeight"]: return "lying"
    if inp["pelvis_horiz"] >= p["SitHoriz"]: return "sit"
    if inp["pelvis_above_feet"] < p["CrouchBelow"]: return "crouch"   # round 4 (spec 7e.1)
    return "stand"


def pose_mode(pose, p):
    return {"stand": MODE_FULL, "sit": int(p["SitMode"]), "kneel": int(p["KneelMode"]),
            "crouch": int(p["CrouchMode"])}.get(pose, MODE_OFF)


def hip_limit(pose, p):
    """The hips' drop limit: Crouch: max hip drop for crouch (spec 7e.1), Max hip drop otherwise."""
    return p["CrouchDrop"] if pose == "crouch" else p["MaxPelvisDrop"]


def hand_still_step(st, pos, dt, p):
    """Spec 7e.2: st = {"prev": last animated hand position or None, "t": seconds still}. A frame slower than HandStill
    (cm/s) adds dt, a faster one (or the first frame) resets. -> still long enough (t >= HandStillFor)."""
    prev = st.get("prev")
    if prev is None or dt <= 0: st["t"] = 0.0
    else:
        sp = math.hypot(pos[0] - prev[0], pos[1] - prev[1]) / dt   # review I1: horizontal only (the IK moves hands in Z)
        st["t"] = st["t"] + dt if sp < p["HandStill"] else 0.0
    st["prev"] = tuple(pos)
    return st["t"] >= p["HandStillFor"]


def decide(inp, p, on_toggle=True):
    """(on, reason, pose, legs_only). reason: 'off' (toggle), a HARD_OFF name, 'air', 'moving', the pose ('feet', 'lying')
    or 'pose off' (its mode is Off), else 'on'."""
    pose = pose_type(inp, p)
    if not on_toggle: return False, "off", pose, False
    for h in HARD_OFF:
        if inp.get(h): return False, h, pose, False
    if not inp["grounded"]: return False, "air", pose, False
    if inp["speed"] >= p["StillSpeed"]: return False, "moving", pose, False
    if pose in ("feet", "lying"): return False, pose, pose, False
    mode = pose_mode(pose, p)
    if mode == MODE_OFF: return False, "pose off", pose, False
    return True, "on", pose, mode == MODE_LEGS


def targets(hit_l, hit_r, p, pose="stand"):
    """Hit heights above the ground under the capsule (None = no hit) -> (off_l, off_r, pelvis). A hit beyond +-MaxStep (a
    chair seat over the ankle, a ledge) counts as no hit. Pelvis only goes down, by at most hip_limit(pose)."""
    m = p["MaxStep"]
    l = hit_l if hit_l is not None and -m <= hit_l <= m else 0.0
    r = hit_r if hit_r is not None and -m <= hit_r <= m else 0.0
    return l, r, max(-hip_limit(pose, p), min(0.0, l, r))


def effector(off, pelvis, w):
    """Component-Z offset of the IK effector relative to the (already pelvis-shifted) animated foot."""
    return w * (off - pelvis)


def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def qrot(q, v):
    r = qmul(qmul(q, (v[0], v[1], v[2], 0.0)), (-q[0], -q[1], -q[2], q[3]))
    return r[:3]


def to_bone_space(v_cs, q):
    """Component-space vector -> the foot bone's local axes (= UnrotateVector by the foot's component rotation)."""
    return qrot((-q[0], -q[1], -q[2], q[3]), v_cs)


def clamp_normal(n, max_tilt_deg):
    x, y, z = n; l = math.sqrt(x * x + y * y + z * z); x, y, z = x / l, y / l, z / l
    a = math.acos(clamp(z, -1.0, 1.0)); m = math.radians(max_tilt_deg)
    if a <= m: return x, y, z
    h = math.sqrt(x * x + y * y)
    return x / h * math.sin(m), y / h * math.sin(m), math.cos(m)


def tilt_angle(n, max_tilt_deg):
    return math.acos(clamp(clamp_normal(n, max_tilt_deg)[2], -1.0, 1.0))


def tilt(normal_cs, max_tilt_deg):
    """Rotator (pitch, yaw, roll) of UE's MakeRotFromZX(clamped normal, X axis) - zero on flat ground."""
    Z = clamp_normal(normal_cs, max_tilt_deg); X0 = (1.0, 0.0, 0.0)
    cross = lambda a, b: (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    norm = lambda v: tuple(c / math.sqrt(sum(d * d for d in v)) for c in v)
    Y = norm(cross(Z, X0)); X = cross(Y, Z)
    pitch = math.degrees(math.atan2(X[2], math.sqrt(X[0] ** 2 + X[1] ** 2))); yaw = math.degrees(math.atan2(X[1], X[0]))
    sy = (-math.sin(math.radians(yaw)), math.cos(math.radians(yaw)), 0.0)   # Y axis of FRotator(pitch, yaw, 0)
    dot = lambda a, b: sum(i * j for i, j in zip(a, b))
    roll = math.degrees(math.atan2(dot(Z, sy), dot(Y, sy)))
    return pitch, yaw, roll


def new_state():
    return {"off_l": 0.0, "off_r": 0.0, "pel": 0.0, "w": 0.0, "reason": "off", "pose": "stand"}


def step(state, inp, dt, p):
    """One frame. Offsets always follow their targets (smoothed); the weight follows the gate linearly over BlendTime,
    so a target that jumps while the gate is off fades in instead of snapping."""
    on, reason, pose, legs_only = decide(inp, p)
    tl, tr, tp = targets(inp["hit_l"], inp["hit_r"], p, pose)
    if legs_only: tp = 0.0   # Legs only: the feet follow, the hips stay
    k = min(1.0, p["Smoothing"] * dt)
    s = dict(state)
    s["off_l"] += (tl - s["off_l"]) * k; s["off_r"] += (tr - s["off_r"]) * k; s["pel"] += (tp - s["pel"]) * k
    rate = dt / max(p["BlendTime"], 1e-3)
    s["w"] = min(1.0, s["w"] + rate) if on else max(0.0, s["w"] - rate)
    s["reason"] = reason; s["pose"] = pose
    return s


def two_bone_ok(hip, foot_target, thigh, calf):
    """(reachable, knee interior angle in deg) for a target at foot_target."""
    d = math.sqrt(sum((a - b) ** 2 for a, b in zip(hip, foot_target)))
    ok = abs(thigh - calf) <= d <= thigh + calf
    c = clamp((thigh * thigh + calf * calf - d * d) / (2 * thigh * calf), -1.0, 1.0)
    return ok, math.degrees(math.acos(c))


# ===================== round 3 (spec 7d) =====================
REACH = 0.98   # the forward foot never asks for more than 98 % of thigh + calf (no stretching)
UP = (0.0, 0.0, 1.0)


def _v(a): return [float(x) for x in a]
def _sub(a, b): return [x - y for x, y in zip(a, b)]
def _add(a, b): return [x + y for x, y in zip(a, b)]
def _mul(a, k): return [x * k for x in a]
def _dot(a, b): return sum(x * y for x, y in zip(a, b))
def _len(a): return math.sqrt(_dot(a, a))
def _cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def solve_two_bone(hip, knee, foot, joint_target, effector):
    """Port of UE 4.27 AnimationCore::SolveTwoBoneIK (no stretching). Lengths from the input pose. -> (knee2, foot2)."""
    hip, knee, foot, jt, eff = map(_v, (hip, knee, foot, joint_target, effector))
    up_len, lo_len = _len(_sub(knee, hip)), _len(_sub(foot, knee))
    d = _sub(eff, hip); dl = _len(d)
    if dl < 1e-4: return knee, foot
    dd = _mul(d, 1.0 / dl)
    jd = _sub(jt, hip)
    if _dot(jd, jd) < 1e-8: bend = [0.0, 1.0, 0.0]
    else:
        bend = _sub(jd, _mul(dd, _dot(jd, dd))); bl = _len(bend)
        if bl < 1e-4:   # UE: FindBestAxisVectors - any perpendicular
            bend = _cross(dd, [1.0, 0.0, 0.0] if abs(dd[0]) < 0.9 else [0.0, 1.0, 0.0]); bl = _len(bend)
        bend = _mul(bend, 1.0 / bl)
    mx = up_len + lo_len
    if dl >= mx: return _add(hip, _mul(dd, up_len)), _add(hip, _mul(dd, mx))
    ca = clamp((up_len * up_len + dl * dl - lo_len * lo_len) / (2 * up_len * dl), -1.0, 1.0)
    sa = math.sqrt(max(0.0, 1.0 - ca * ca))
    return _add(hip, _add(_mul(dd, up_len * ca), _mul(bend, up_len * sa))), eff


def forward_shift(rise, k, hip, foot_target, fwd, leg_len):
    """How far the high foot goes forward (Jodi's facing): k x rise, limited so hip -> foot <= REACH x leg. 0 if it cannot."""
    want = k * rise
    if want <= 0.0: return 0.0
    d = _sub(_v(foot_target), _v(hip)); df = _dot(d, fwd); r = REACH * leg_len
    disc = df * df - _dot(d, d) + r * r
    if disc < 0.0: return 0.0
    f = min(want, -df + math.sqrt(disc))
    if f <= 0.0 or _len(_add(d, _mul(fwd, f))) > r + 1e-6: return 0.0
    return f


def forward_accept(h1, h2, fwd_same):
    """The forward spot counts only if it was hit and lies within FwdSame of the first trace (else: riser, edge, nothing)."""
    return h2 is not None and abs(h2 - h1) <= fwd_same


FWD_REACH = DEFAULTS["FwdReach"]   # cm: pass B's joint target lies this far ahead / above the middle of the hip-foot line


def follow_joint_target(hip, foot_b, fwd):
    """Pass B's joint target, component space, from the hip and pass B's target foot only (no knee: nothing feeds back):
    the middle of the hip-foot line + (forward + up) x FWD_REACH -> the knee bends forward / up in Jodi's facing plane."""
    mid = _mul(_add(_v(hip), _v(foot_b)), 0.5)
    return _add(mid, _mul(_add(list(fwd), list(UP)), FWD_REACH))


def leg_with_follow(hip, knee, foot, rise, k, fwd, leg_len, fwd_blend=DEFAULTS["FwdBlend"]):
    """Foot raised by rise with Knee follows foot = k (final review C1): pass A lifts the foot (joint target = the animated
    calf, round 2); pass B moves it forward by forward_shift with follow_joint_target, faded in over the first fwd_blend cm
    (approximated here as a position blend of the knee). -> (knee2, foot2)."""
    tgt = _add(_v(foot), [0.0, 0.0, rise])
    ka, fa = solve_two_bone(hip, knee, foot, knee, tgt)
    f = forward_shift(rise, k, hip, tgt, fwd, leg_len)
    if f <= 0.0: return ka, fa
    fb = _add(fa, _mul(fwd, f))
    kb, fb2 = solve_two_bone(hip, ka, fa, follow_joint_target(hip, fb, fwd), fb)
    al = clamp(f / fwd_blend, 0.0, 1.0) if fwd_blend > 0 else 1.0
    return _add(_mul(ka, 1 - al), _mul(kb, al)), _add(_mul(fa, 1 - al), _mul(fb2, al))


def rotate_about(pt, centre, axis, ang):
    """pt rotated by ang (rad) about the line through centre along unit axis (Rodrigues = UE RotateAngleAxis)."""
    q = _sub(_v(pt), _v(centre)); a = _v(axis); c, s = math.cos(ang), math.sin(ang)
    r = _add(_add(_mul(q, c), _mul(_cross(a, q), s)), _mul(a, _dot(a, q) * (1 - c)))
    return _add(_v(centre), r)


def leg_axis(hip, foot):
    hf = _sub(_v(foot), _v(hip)); d = _len(hf)
    return _mul(hf, 1.0 / d) if d > 1e-3 else [0.0, 0.0, -1.0]


def knee_arc(hip, knee, foot, z_target):
    """(joint target in component space, swing angle in rad) that puts the knee at height z_target on the circle it can take
    with hip and foot fixed - the smaller swing from `knee`; the highest point if z_target is out of reach. (None, 0.0) if the
    leg is almost straight (arc radius < 2 cm). Target = centre + 2 x radius x direction (well-defined bend plane).
    The driver keeps the angle: next frame the animated knee = final knee rotated back by weight x angle (rotate_about)."""
    H, K, F = _v(hip), _v(knee), _v(foot)
    d = _len(_sub(F, H))
    if d < 1e-3: return None, 0.0
    a = leg_axis(H, F); lt, lc = _len(_sub(K, H)), _len(_sub(F, K))
    t = (d * d + lt * lt - lc * lc) / (2 * d); c = _add(H, _mul(a, t)); r = math.sqrt(max(lt * lt - t * t, 0.0))
    w = _sub(_sub(K, c), _mul(a, _dot(_sub(K, c), a))); wl = _len(w)
    if r < 2.0 or wl < 1e-6: return None, 0.0
    u = _mul(w, 1.0 / wl); v = _cross(a, u)
    A, B = r * u[2], r * v[2]; rho = math.hypot(A, B)
    th = 0.0
    if rho > 1e-6:
        phi = math.atan2(B, A); delta = math.acos(clamp((z_target - c[2]) / rho, -1.0, 1.0))
        wrap = lambda x: (x + math.pi) % (2 * math.pi) - math.pi
        th = min((wrap(phi - delta), wrap(phi + delta)), key=abs)
    return _add(c, _mul(_add(_mul(u, math.cos(th)), _mul(v, math.sin(th))), 2 * r)), th


def new_contact_state():
    return {"wb": 0.0, "wkl": 0.0, "wkr": 0.0, "whl": 0.0, "whr": 0.0, "pelk": 0.0, "lift_l": 0.0, "lift_r": 0.0,
            "hand_l": 0.0, "hand_r": 0.0, "knee_mode": "-", "hand_state": "-"}


def contact_step(state, inp, dt, p):
    """One frame of knee and hand contact (spec 7d.3 / 7d.4). Independent of the foot IK toggle. Hits: surface height relative
    to the ground under Jodi (None = no hit); knee_h / hand_h: animated heights above the floor."""
    common = not any(inp.get(h) for h in HARD_OFF) and inp["grounded"] and inp["speed"] < p["StillSpeed"]
    pose = pose_type(inp, p)
    nl, nr = (h < p["KneeNear"] for h in inp["knee_h"])
    hk = [0.0 if h is None else h for h in (inp["hit_knee_l"], inp["hit_knee_r"])]
    knee_ok = bool(p["KneeOn"]) and common
    t = {"wb": 0.0, "wkl": 0.0, "wkr": 0.0, "pelk": 0.0, "lift_l": 0.0, "lift_r": 0.0}; mode = "-"
    if knee_ok and pose == "kneel" and nl and nr:
        mode = "kneel"; t["wb"] = 1.0; t["pelk"] = clamp(max(hk), -p["MaxKneeHip"], p["MaxKneeHip"])
    elif knee_ok and (nl or nr):
        mode = "arc"
        for s, near, h in (("l", nl, hk[0]), ("r", nr, hk[1])):
            if near: t["wk" + s] = 1.0; t["lift_" + s] = clamp(h, 0.0, p["MaxKneeLift"])
    hand_ok = bool(p["HandOn"]) and common
    held = hand_ok and bool(inp["held"])
    t.update({"whl": 0.0, "whr": 0.0, "hand_l": 0.0, "hand_r": 0.0}); hstate = "held" if held else "-"
    if hand_ok and not held:
        m = p["MaxHandStep"]
        still = inp.get("hand_still", (True, True))   # round 4 (spec 7e.2): hand_still_step per hand
        for s, hh, hit, st in (("l", inp["hand_h"][0], inp["hit_hand_l"], still[0]), ("r", inp["hand_h"][1], inp["hit_hand_r"], still[1])):
            if hh < p["HandNear"] and not st:
                if hstate == "-": hstate = "wait"
            elif hh < p["HandNear"]:
                t["wh" + s] = 1.0; hstate = "on"
                t["hand_" + s] = hit if hit is not None and -m <= hit <= m else 0.0
    k = min(1.0, p["Smoothing"] * dt); rate = dt / max(p["BlendTime"], 1e-3); s2 = dict(state)
    for key in ("wb", "wkl", "wkr", "whl", "whr"):
        s2[key] = min(t[key], s2[key] + rate) if t[key] > s2[key] else max(t[key], s2[key] - rate)
    for key in ("pelk", "lift_l", "lift_r", "hand_l", "hand_r"):
        s2[key] += (t[key] - s2[key]) * k
    s2["knee_mode"], s2["hand_state"] = mode, hstate
    return s2
