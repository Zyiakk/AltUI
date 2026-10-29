#!/usr/bin/env python3
"""rag_detail_measure.py - where assets/gen/rag_detail.py comes from: the reference pose of finger and lid bones (game mesh
Character/Jodi/Body/Female via bodybones.load_ref), finger curl axes / angles (Female_Idle_Grip) and the lid's closed rotation
(Female_EyeClosed, additive). The .psa files: scripts/anim_extract.sh with ANIMS="Female_Idle_Grip Female_EyeClosed".
psa keys -> UE local: (x, -y, z, w) (docs/notes/2026-10-06-tempo.md, assets/anim/blender/animlib.py).
  scripts/rag_detail_measure.py            prints REF_ROT, grip axes / angles, lid delta"""
import os, sys, math, struct
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(W, "scripts")); sys.path.insert(0, os.path.join(W, "assets", "anim")); sys.path.insert(0, os.path.join(W, "assets", "gen"))
PSA = os.path.join(W, "build", "anim", "psa", "Project", "Character", "Jodi", "Animations")


def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx, aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def conj(q): return (-q[0], -q[1], -q[2], q[3])


def axis_angle(q):
    if q[3] < 0: q = tuple(-c for c in q)
    s = math.sqrt(max(0.0, 1 - q[3] ** 2)); ang = math.degrees(2 * math.acos(max(-1.0, min(1.0, q[3]))))
    return ((0.0, 0.0, 0.0) if s < 1e-6 else tuple(round(c / s, 3) for c in q[:3])), round(ang, 1)


def rotator(q):
    """FQuat::Rotator() of UE 4.27."""
    X, Y, Z, Wq = q
    st = Z * X - Wq * Y; yaw = math.degrees(math.atan2(2 * (Wq * Z + X * Y), 1 - 2 * (Y * Y + Z * Z)))
    if st < -0.4999995: pitch = -90.0; roll = -yaw - 2 * math.degrees(math.atan2(X, Wq))
    elif st > 0.4999995: pitch = 90.0; roll = yaw - 2 * math.degrees(math.atan2(X, Wq))
    else: pitch = math.degrees(math.asin(2 * st)); roll = math.degrees(math.atan2(-2 * (Wq * X + Y * Z), 1 - 2 * (X * X + Y * Y)))
    return (round(pitch, 3), round(yaw, 3), round((roll + 180) % 360 - 180, 3))


def ref_quats():
    """bone -> local reference rotation (x, y, z, w) of the game's mesh; FileNotFoundError without the game."""
    import bodybones
    lay = bodybones.load_ref(near=os.environ.get("GAME"))
    return {name: struct.unpack_from("<4f", raw, 0) for (name, _, _), raw in zip(lay.bones, lay.poses)}


def ref_rotators():
    import rag_detail as rd
    q = ref_quats(); return {b: rotator(q[b]) for b in rd.DETAIL_BONES}


def psa_ue(name, frame):
    import psa
    p = psa.read(os.path.join(PSA, name + ".psa")); names = [b["name"] for b in p["bones"]]
    return {n: (k[0], -k[1], k[2], k[3]) for n, (_, k) in zip(names, psa.frame(p, frame))}, p["anims"][0]["frames"]


def main():
    import rag_detail as rd
    print("REF_ROT = {"); [print('    "%s": %s,' % (b, r)) for b, r in ref_rotators().items()]; print("}")
    ref = ref_quats(); grip, _ = psa_ue("Female_Idle_Grip", 0)
    for b in rd.FINGER_BONES: print("grip %-12s axis %-26s angle %s" % ((b,) + axis_angle(qmul(conj(ref[b]), grip[b]))))
    _, n = psa_ue("Female_EyeClosed", 0); lid, _ = psa_ue("Female_EyeClosed", n - 1)
    for b in rd.LID_BONES: print("lid  %-12s axis %-26s angle %s" % ((b,) + axis_angle(lid[b])))


if __name__ == "__main__":
    main()
