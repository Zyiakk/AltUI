#!/usr/bin/env python3
"""Generates assets/45_footik.json: BP_AltUIFootIK, the Foot IK driver (Options > Movement: "Feet follow the ground",
"Knees and hands follow the ground"). Every frame (FootTick) it finds the player's mesh, casts its post-process instance to
ABP_BodyScale (another body: nothing, weights back to 0), computes the gate and the pose type, traces under both feet (and at
the forward spot of a raised foot), runs KneeTick (knee contact), HoldCheck + HandTick (hand contact) and pushes everything into
the Foot IK nodes of ABP_BodyScale (footik.py) - the maths of footik_sim.py. Values are pre-multiplied by each feature's own
weight; ALeg / AHand are 0/1 group switches, the knee-arc nodes' alpha is its weight.
Origin: BenenG47's Foot IK test chip v0.5 (BP_FootIKTest, his gen_footik.py); the graphs are his, unchanged except: the values are
fixed at his final ones (footik_sim.DEFAULTS), the switches On / KneeOn / HandOn are copied from the manager (FootIKOn,
FootContactOn) every frame, "fitting" also counts AltUI's open panel, and the actor turns its tick off when everything is off
and faded out (the manager calls Wake). The chip's page, SaveGame, presets and status box are gone.
Spec: internal design notes (the chip's own: internal design notes/)."""
import os, sys; sys.path[:0] = [os.path.dirname(__file__), os.path.join(os.path.dirname(__file__), "..", "..", "scripts")]
from bpdsl import *
import footik, footik_sim as S, bodyscale_groups as bg
from footik import VEC, ROT, V0, R0

FOOTIK = M + "/BP_AltUIFootIK"
ABP = bg.ABP_PATH
MGR = M + "/BP_AltUIManager"   # FootIKOn / FootContactOn (options), JodiHidden, CamMode (0 play / 1 free cam / 2 photo / 3 ragdoll), PanelOpen
E_PRIMC = "/Script/Engine.PrimitiveComponent"; E_NAVMC = "/Script/Engine.NavMovementComponent"
E_CAPSULE = "/Script/Engine.CapsuleComponent"; E_CMC = "/Script/Engine.CharacterMovementComponent"
MESH_T = "object:" + E_SKELMESHCOMP
E_PC_ = "/Script/Engine.PlayerController"; E_ANIMI = "/Script/Engine.AnimInstance"
E_LSA = "/Script/LevelSequence.LevelSequenceActor"; E_MSP = "/Script/MovieScene.MovieSceneSequencePlayer"
# the test chip's sliders and choices (pose modes: 0 Off / 1 Legs only / 2 Legs + hips), fixed at BenenG47's final values
_FOOT = ["StillSpeed", "PlantedHeight", "MinPelvisHeight", "FootHeight", "TraceUp", "TraceDown", "MaxStep", "MaxTilt", "MaxPelvisDrop",
         "BlendTime", "Smoothing", "KneeFollow", "FwdSame", "FwdBlend", "FwdReach", "KneelKnee", "SitHoriz", "CrouchBelow", "CrouchDrop"]
_KNEE = ["KneeNear", "MaxKneeLift", "MaxKneeHip"]
_HAND = ["HandNear", "MaxHandStep", "MaxHandTilt", "HandStill", "HandStillFor"]
CHOICES = ["SitMode", "KneelMode", "CrouchMode"]
VALUE_KEYS = _FOOT + _KNEE + _HAND + CHOICES
SWITCHES = ["On", "KneeOn", "HandOn"]   # copied from the manager at the start of every FootTick


def R(i): return "@%s.ReturnValue" % i


# BenenG47's maths helper; it shadows bpdsl's path prefix M from here on (the paths above are already built)
class M:
    """Small maths helper on a graph: every call returns its output reference."""
    def __init__(self, g): self.g = g
    def __call__(self, id, fn, **inp): self.g.call(id, K_MATH, fn, inp=inp); return R(id)
    def add(self, id, a, b): return self(id, "Add_FloatFloat", A=a, B=b)
    def sub(self, id, a, b): return self(id, "Subtract_FloatFloat", A=a, B=b)
    def mul(self, id, a, b): return self(id, "Multiply_FloatFloat", A=a, B=b)
    def div(self, id, a, b): return self(id, "Divide_FloatFloat", A=a, B=b)
    def vec(self, id, x, y, z): return self(id, "MakeVector", X=x, Y=y, Z=z)
    def brk(self, id, v): self.g.call(id, K_MATH, "BreakVector", inp={"InVec": v}); return ("@%s.X" % id, "@%s.Y" % id, "@%s.Z" % id)
    def vadd(self, id, a, b): return self(id, "Add_VectorVector", A=a, B=b)
    def vsub(self, id, a, b): return self(id, "Subtract_VectorVector", A=a, B=b)
    def vmul(self, id, a, k): return self(id, "Multiply_VectorFloat", A=a, B=k)
    def dot(self, id, a, b): return self(id, "Dot_VectorVector", A=a, B=b)
    def cross(self, id, a, b): return self(id, "Cross_VectorVector", A=a, B=b)
    def size(self, id, a): return self(id, "VSize", A=a)
    def norm(self, id, a): return self(id, "Normal", A=a, Tolerance="0.0001")
    def AND(self, id, a, b): return self(id, "BooleanAND", A=a, B=b)
    def OR(self, id, a, b): return self(id, "BooleanOR", A=a, B=b)
    def NOT(self, id, a): return self(id, "Not_PreBool", A=a)
    def sel(self, id, a, b, pick): return self(id, "SelectFloat", A=a, B=b, bPickA=pick)
    def smooth(self, id, cur, target, k): return self.add(id, cur, self.mul(id + "k", self.sub(id + "d", target, cur), k))
    def fade(self, id, cur, on, dt, speed):
        """weight toward 1 / 0 at a constant speed (footik_sim: dt / BlendTime per frame)."""
        return self(id, "FInterpTo_Constant", Current=cur, Target=self.sel(id + "t", "1.0", "0.0", on), DeltaTime=dt, InterpSpeed=speed)


def sock_cs(g, id, mesh, bone):
    """(location, rotation) of a bone in component space (last frame's final pose)."""
    g.call(id, E_SCENECOMP, "GetSocketTransform", inp={"self": mesh, "InSocketName": bone, "TransformSpace": "RTS_Component"})
    g.call("b" + id, K_MATH, "BreakTransform", inp={"InTransform": R(id)})
    return "@b%s.Location" % id, "@b%s.Rotation" % id


def gets(g, *names):
    for v in names: g.get("g" + v, v)
    return {v: "@g%s.%s" % (v, v) for v in names}


def blend_speed(m, id, bt):
    return m.div(id, "1.0", m(id + "m", "FMax", A=bt, B="0.001"))


def tilt_target(g, m, p, normal_world, ctw, max_tilt, use):
    """Surface normal (world) -> component-space rotator of MakeRotFromZX(normal clamped to max_tilt, X); zero when not `use`
    (footik_sim.tilt). p = id prefix."""
    nc = m(p + "nc", "InverseTransformDirection", T=ctw, Direction=normal_world)
    nc = m(p + "nu", "Normal", A=nc, Tolerance="0.0001")   # a scaled transform scales the direction too
    bx, by, bz = m.brk(p + "bn", nc)
    over = m(p + "ov", "Greater_FloatFloat", A=m(p + "ag", "DegAcos", A=bz), B=max_tilt)
    hor = m(p + "ho", "Normal", A=m.vec(p + "hv", bx, by, "0.0"), Tolerance="0.0001")
    clv = m.vadd(p + "cv", m.vmul(p + "hx", hor, m(p + "sn", "DegSin", A=max_tilt)), m.vec(p + "cz", "0.0", "0.0", m(p + "cs", "DegCos", A=max_tilt)))
    nn = m(p + "nn", "SelectVector", A=clv, B=nc, bPickA=over)
    rot = m(p + "rf", "MakeRotFromZX", Z=nn, X=m.vec(p + "xa", "1.0", "0.0", "0.0"))
    return m(p + "rt", "SelectRotator", A=rot, B=m(p + "zr", "MakeRotator", Roll="0.0", Pitch="0.0", Yaw="0.0"), bPickA=use)


def arc_nodes(m, p, H, K, F, zT):
    """footik_sim.knee_arc in nodes: (joint target cs, swing angle deg, ok = arc radius >= 2 cm). H/K/F component space."""
    hf = m.vsub(p + "hf", F, H); d = m.size(p + "d", hf); a = m.norm(p + "ax", hf)
    lt = m.size(p + "lt", m.vsub(p + "kh", K, H)); lc = m.size(p + "lc", m.vsub(p + "fk", F, K))
    num = m.sub(p + "nm", m.add(p + "n1", m.mul(p + "d2", d, d), m.mul(p + "lt2", lt, lt)), m.mul(p + "lc2", lc, lc))
    t = m.div(p + "t", num, m(p + "dd", "FMax", A=m.mul(p + "d2x", d, "2.0"), B="0.001"))
    c = m.vadd(p + "c", H, m.vmul(p + "at", a, t))
    r = m(p + "r", "Sqrt", A=m(p + "r2", "FMax", A=m.sub(p + "r1", m.mul(p + "lt2b", lt, lt), m.mul(p + "t2", t, t)), B="0.0"))
    q = m.vsub(p + "q", K, c)
    u = m.norm(p + "u", m.vsub(p + "w", q, m.vmul(p + "qa", a, m.dot(p + "qd", q, a))))
    v = m.cross(p + "v", a, u)
    _, _, uz = m.brk(p + "bu", u); _, _, vz = m.brk(p + "bv", v); _, _, cz = m.brk(p + "bc", c)
    A = m.mul(p + "A", r, uz); B = m.mul(p + "B", r, vz)
    rho = m(p + "rho", "Sqrt", A=m.add(p + "rs", m.mul(p + "A2", A, A), m.mul(p + "B2", B, B)))
    phi = m(p + "phi", "DegAtan2", Y=B, X=A)
    cosv = m(p + "cl", "FClamp", Value=m.div(p + "kz", m.sub(p + "dz", zT, cz), m(p + "rm", "FMax", A=rho, B="0.0001")), Min="-1.0", Max="1.0")
    delta = m(p + "de", "DegAcos", A=cosv)
    th1 = m(p + "th1", "NormalizeAxis", Angle=m.sub(p + "pm", phi, delta))
    th2 = m(p + "th2", "NormalizeAxis", Angle=m.add(p + "pp", phi, delta))
    th = m.sel(p + "th", th1, th2, m(p + "le", "LessEqual_FloatFloat", A=m(p + "ab1", "Abs", A=th1), B=m(p + "ab2", "Abs", A=th2)))
    dr = m.vadd(p + "dr", m.vmul(p + "uc", u, m(p + "co", "DegCos", A=th)), m.vmul(p + "vs", v, m(p + "si", "DegSin", A=th)))
    jt = m.vadd(p + "jt", c, m.vmul(p + "j2", dr, m.mul(p + "r2x", r, "2.0")))
    ok = m(p + "ok", "GreaterEqual_FloatFloat", A=r, B="2.0")
    return jt, th, ok


def f_trace():
    """Straight down under (x, y) from floor + TraceUp to floor - TraceDown (Visibility, ignores the pawn, what is attached to
    it and this actor). hit, h = impact height above the floor, n = impact normal (world)."""
    g = G(); m = M(g)
    g.get("gtu", "TraceUp"); g.get("gtd", "TraceDown")
    st = m.vec("st", "@entry.x", "@entry.y", m.add("z0", "@entry.floor", "@gtu.TraceUp"))
    en = m.vec("en", "@entry.x", "@entry.y", m.sub("z1", "@entry.floor", "@gtd.TraceDown"))
    g.get("gig", "Ignore")
    g.call("lt", K_SYS, "LineTraceSingle", inp={"Start": st, "End": en, "TraceChannel": "TraceTypeQuery1", "bTraceComplex": "false",
                                                "ActorsToIgnore": "@gig.Ignore", "DrawDebugType": "None", "bIgnoreSelf": "true",
                                                "TraceColor": "(R=1,G=0,B=0,A=1)", "TraceHitColor": "(R=0,G=1,B=0,A=1)", "DrawTime": "0.0"})
    g.call("bh", K_GS, "BreakHitResult", inp={"Hit": "@lt.OutHit"})
    _, _, iz = m.brk("bip", "@bh.ImpactPoint")
    h = m.sub("h", iz, "@entry.floor")
    g.link("lt.ReturnValue", "return.hit"); g.link(h[1:], "return.h"); g.link("bh.ImpactNormal", "return.n")
    g.chain("entry", "lt", "return")
    return fn("Trace", [param("x", "float"), param("y", "float"), param("floor", "float")],
              [param("hit", "bool"), param("h", "float"), param("n", VEC)], graph=g)


def f_seq_playing():
    """yes = a level sequence (cutscene) is playing."""
    g = G(); g.set("s0", "SeqOn", inp={"SeqOn": "false"})
    g.call("ga", K_GS, "GetAllActorsOfClass", inp={"ActorClass": E_LSA}); g.set("cp", "SeqLoop", inp={"SeqLoop": "@ga.OutActors"})
    g.get("gl", "SeqLoop"); g.foreach("fe", "@gl.SeqLoop")
    g.cast("cs", E_LSA, "@fe.Array Element"); g.call("sp", E_LSA, "GetSequencePlayer", inp={"self": "@cs.AsLevelSequenceActor"})
    g.call("ip", E_MSP, "IsPlaying", inp={"self": R("sp")}); g.branch("bp", R("ip")); g.set("s1", "SeqOn", inp={"SeqOn": "true"})
    g.get("go", "SeqOn"); g.link("go.SeqOn", "return.yes")
    g.chain("entry", "s0", "ga", "cp", "fe"); g.chain("fe", "bp", "s1"); g.chain("fe:Completed", "return")
    return fn("SeqPlaying", outputs=[param("yes", "bool")], graph=g)


def f_hold_check():
    """yes = something (gun, prop, its actor's root) is attached to the mesh at a socket on hand_l / hand_r or a bone under them
    (Prop_L, Prop_R, Prop_R1 ... are children of the hands) -> hand contact off for both hands (spec 7d.4)."""
    g = G(); m = M(g); MESH = "@entry.mesh"
    g.set("s0", "HeldOn", inp={"HeldOn": "false"})
    g.call("gc", E_SCENECOMP, "GetChildrenComponents", inp={"self": MESH, "bIncludeAllDescendants": "false"})
    g.set("cp", "HoldLoop", inp={"HoldLoop": "@gc.Children"})
    g.get("gl", "HoldLoop"); g.foreach("fe", "@gl.HoldLoop")
    g.call("sn", E_SCENECOMP, "GetAttachSocketName", inp={"self": "@fe.Array Element"})
    g.call("bn", E_SKINNED, "GetSocketBoneName", inp={"self": MESH, "InSocketName": R("sn")})
    hits = []
    for s in ("l", "r"):
        g.call("ch" + s, E_SKINNED, "BoneIsChildOf", inp={"self": MESH, "BoneName": R("bn"), "ParentBoneName": "hand_" + s})
        hits.append(m.OR("or" + s, R("ch" + s), m("eq" + s, "EqualEqual_NameName", A=R("bn"), B="hand_" + s)))
    g.branch("bnn", m("nn", "NotEqual_NameName", A=R("bn"), B="None"))
    g.branch("bh", m.OR("any", *hits)); g.set("s1", "HeldOn", inp={"HeldOn": "true"})
    g.get("go", "HeldOn"); g.link("go.HeldOn", "return.yes")
    g.chain("entry", "s0", "cp", "fe"); g.chain("fe", "bnn", "bh", "s1"); g.chain("fe:Completed", "return")
    return fn("HoldCheck", [param("mesh", MESH_T)], [param("yes", "bool")], graph=g)


def f_knee_tick():
    """Knee contact (spec 7d.3, footik_sim.contact_step + knee_arc). Kneeling (pose kneel, both knees near): the hips move by the
    higher knee surface (PelK, weight WB). Else each near knee is lifted along its arc (joint target KneeJL/R, weight WKL/R). The
    animated knee = the final knee rotated back by last frame's weight x swing angle (ledger round 3, Task 1)."""
    g = G(); m = M(g); MESH = "@entry.mesh"; DT = "@entry.dt"; SZ = "@entry.sz"
    v = gets(g, "KneeOn", "Common", "Pose", "KneeNear", "MaxKneeLift", "MaxKneeHip", "Smoothing", "BlendTime", "PelAp",
             "WKL", "WKR", "ThL", "ThR", "LiftL", "LiftR", "PelK", "WB")
    act = m.AND("act", v["KneeOn"], v["Common"])
    g.call("ipk", K_STR, "EqualEqual_StrStr", inp={"A": v["Pose"], "B": "kneel"})
    pos = {}; near = {}; hk = {}
    for s, S_ in (("l", "L"), ("r", "R")):
        H, _ = sock_cs(g, "th" + s, MESH, "thigh_" + s); K, _ = sock_cs(g, "kn" + s, MESH, "calf_" + s); F, _ = sock_cs(g, "ft" + s, MESH, "foot_" + s)
        a = m.norm("ax" + s, m.vsub("hf" + s, F, H))
        ang = m.mul("nth" + s, m.mul("nw" + s, v["WK" + S_], "-1.0"), v["Th" + S_])
        kin0 = m.vadd("ki" + s, H, m("kin" + s, "RotateAngleAxis", InVect=m.vsub("kq" + s, K, H), AngleDeg=ang, Axis=a))
        g.set("sKin" + S_, "Kin" + S_, inp={"Kin" + S_: kin0})          # cached: Th / WK are written later in this chain
        g.get("gki" + s, "Kin" + S_); kin = "@gki%s.Kin%s" % (s, S_)
        _, _, kz = m.brk("bk" + s, kin)
        near[s] = m("nr" + s, "Less_FloatFloat", A=m.sub("kh" + s, kz, v["PelAp"]), B=v["KneeNear"])
        g.call("kw" + s, E_SCENECOMP, "GetSocketLocation", inp={"self": MESH, "InSocketName": "calf_" + s}); wx, wy, _ = m.brk("bw" + s, R("kw" + s))
        g.n("tk" + s, "call_self", function="Trace", inp={"x": wx, "y": wy, "floor": "@entry.ground"})
        hk[s] = m.sel("hk" + s, m.div("hs" + s, "@tk%s.h" % s, SZ), "0.0", "@tk%s.hit" % s)
        pos[s] = (H, kin, F, kz)
    both = m.AND("kb", m.AND("kb1", act, R("ipk")), m.AND("kb2", near["l"], near["r"]))
    bt = blend_speed(m, "bsp", v["BlendTime"]); k = m("ks", "FMin", A="1.0", B=m.mul("kd", v["Smoothing"], DT))
    pk_t = m.sel("pkt", m("pkc", "FClamp", Value=m("pkm", "FMax", A=hk["l"], B=hk["r"]), Min=m.mul("nmh", v["MaxKneeHip"], "-1.0"),
                                         Max=v["MaxKneeHip"]), "0.0", both)
    g.set("sWB", "WB", inp={"WB": m.fade("fwb", v["WB"], both, DT, bt)})
    g.set("sPK", "PelK", inp={"PelK": m.smooth("smk", v["PelK"], pk_t, k)})
    arcs = {}
    for s, S_ in (("l", "L"), ("r", "R")):
        H, kin, F, kz = pos[s]
        lift_t = m("lc" + s, "FClamp", Value=hk[s], Min="0.0", Max=v["MaxKneeLift"])
        lift = m.smooth("sl" + s, v["Lift" + S_], m.sel("lt" + s, lift_t, "0.0", m.AND("la" + s, act, near[s])), k)
        # after sLf this Get returns the new lift (the arc reads it, not the smoothing expression again)
        jt, th, ok = arc_nodes(m, "a" + s, H, kin, F, m.add("zt" + s, kz, v["Lift" + S_]))
        arcs[s] = m.AND("ka" + s, m.AND("ka1" + s, act, m.NOT("nb" + s, both)), m.AND("ka2" + s, near[s], ok))
        g.set("sLf" + S_, "Lift" + S_, inp={"Lift" + S_: lift})
        g.set("sTh" + S_, "Th" + S_, inp={"Th" + S_: th})
        g.set("sWK" + S_, "WK" + S_, inp={"WK" + S_: m.fade("fk" + s, v["WK" + S_], arcs[s], DT, bt)})
        # read after sTh / sWK: the swing applied this frame = WK x Th (deg) about the hip-foot axis; the foot turned back
        sw = m.mul("kra" + s, v["WK" + S_], v["Th" + S_]); axis = "@ax%s.ReturnValue" % s
        g.set("sKR" + S_, "KneeRot" + S_, inp={"KneeRot" + S_: m("krr" + s, "RotatorFromAxisAndAngle", Axis=axis, Angle=sw)})
        g.set("sKF" + S_, "KneeFoot" + S_, inp={"KneeFoot" + S_: m("kfr" + s, "RotatorFromAxisAndAngle", Axis=axis, Angle=m.mul("kfa" + s, sw, "-1.0"))})
    g.call("km1", K_MATH, "SelectString", inp={"A": "arc", "B": "-", "bPickA": m.OR("ao", arcs["l"], arcs["r"])})
    g.call("km2", K_MATH, "SelectString", inp={"A": "kneel", "B": R("km1"), "bPickA": both})
    g.set("sKM", "KneeMode", inp={"KneeMode": R("km2")})
    g.chain("entry", "sKinL", "sKinR", "tkl", "tkr", "sWB", "sPK", "sLfL", "sThL", "sWKL", "sKRL", "sKFL", "sLfR", "sThR", "sWKR", "sKRR", "sKFR", "sKM")
    return fn("KneeTick", [param("mesh", MESH_T), param("ground", "float"), param("sz", "float"), param("dt", "float")], graph=g)


def f_hand_tick():
    """Hand contact (spec 7d.4, footik_sim.contact_step): a hand near the floor in the animation (and nothing held) is put on
    the surface under it (Two Bone IK effector HEffL/R, hand-bone space, cancels the hips' move) and tilted to it. Values are
    pre-multiplied by the hand's weight WHL/R."""
    g = G(); m = M(g); MESH = "@entry.mesh"; DT = "@entry.dt"; SZ = "@entry.sz"
    v = gets(g, "HandOn", "Common", "Held", "HandNear", "MaxHandStep", "MaxHandTilt", "Smoothing", "BlendTime", "PelAp", "PelNow",
             "WHL", "WHR", "HOffL", "HOffR", "HEzL", "HEzR", "HTiltL", "HTiltR", "HStillL", "HStillR", "HandStillFor")
    act = m.AND("act", v["HandOn"], v["Common"]); free = m.AND("fre", act, m.NOT("nh", v["Held"]))
    g.call("ctw", E_SCENECOMP, "K2_GetComponentToWorld", inp={"self": MESH})
    bt = blend_speed(m, "bsp", v["BlendTime"]); k = m("ks", "FMin", A="1.0", B=m.mul("kd", v["Smoothing"], DT))
    nms = m.mul("nms", v["MaxHandStep"], "-1.0"); ons = {}; tail = []; apos = {}
    for s, S_ in (("l", "L"), ("r", "R")):
        loc, rot = sock_cs(g, "hd" + s, MESH, "hand_" + s); _, _, hz = m.brk("bh" + s, loc)
        hh = m.sub("hh" + s, m.sub("hh0" + s, hz, v["PelAp"]), v["HEz" + S_])        # animated hand height above the floor
        # round 4 (spec 7e.2): the animated hand (component) for HandStillTick; still long enough -> it may take part
        apos[s] = m.vsub("ha" + s, loc, m.vec("hv" + s, "0.0", "0.0", m.add("hz2" + s, v["PelAp"], v["HEz" + S_])))
        near = m.AND("nf" + s, free, m("nr" + s, "Less_FloatFloat", A=hh, B=v["HandNear"]))
        still = m("hsf" + s, "GreaterEqual_FloatFloat", A=v["HStill" + S_], B=v["HandStillFor"])
        on = m.AND("on" + s, near, still)
        g.set("sHW" + S_, "HWait" + S_, inp={"HWait" + S_: m.AND("wt" + s, near, m.NOT("nst" + s, still))})   # cached as HOn
        g.call("hw" + s, E_SCENECOMP, "GetSocketLocation", inp={"self": MESH, "InSocketName": "hand_" + s}); wx, wy, _ = m.brk("bw" + s, R("hw" + s))
        g.n("th" + s, "call_self", function="Trace", inp={"x": wx, "y": wy, "floor": "@entry.ground"})
        h = m.div("hs" + s, "@th%s.h" % s, SZ)
        ok = m.AND("ok" + s, "@th%s.hit" % s, m("ir" + s, "InRange_FloatFloat", Value=h, Min=nms, Max=v["MaxHandStep"], InclusiveMin="true", InclusiveMax="true"))
        use = m.AND("us" + s, on, ok)
        g.set("sHOn" + S_, "HOn" + S_, inp={"HOn" + S_: on}); g.set("sHUse" + S_, "HUse" + S_, inp={"HUse" + S_: use})
        g.get("gon" + s, "HOn" + S_); g.get("gus" + s, "HUse" + S_); on, use = "@gon%s.HOn%s" % (s, S_), "@gus%s.HUse%s" % (s, S_); ons[s] = on
        tail += ["sHOn" + S_, "sHW" + S_, "sHUse" + S_]
        w = m.fade("fw" + s, v["WH" + S_], on, DT, bt)
        off = m.smooth("so" + s, v["HOff" + S_], m.sel("ht" + s, h, "0.0", use), k)
        ez = m.mul("ez" + s, v["WH" + S_], m.sub("ed" + s, v["HOff" + S_], v["PelNow"]))   # read after sWH / sHOff: the new values
        eff = m("ef" + s, "LessLess_VectorRotator", A=m.vec("ev" + s, "0.0", "0.0", ez), B=rot)   # UnrotateVector: hand-bone axes
        tilt = m("ri" + s, "RInterpTo", Current=v["HTilt" + S_], Target=tilt_target(g, m, "t" + s, "@th%s.n" % s, R("ctw"), v["MaxHandTilt"], use),
                 DeltaTime=DT, InterpSpeed=v["Smoothing"])
        for vn, val in (("WH", w), ("HOff", off), ("HEz", ez), ("HEff", eff), ("HTilt", tilt)):
            g.set("s" + vn + S_, vn + S_, inp={vn + S_: val}); tail.append("s" + vn + S_)
        g.get("gt2" + s, "HTilt" + S_); g.get("gw2" + s, "WH" + S_)
        g.set("sHTP" + S_, "HTiltP" + S_, inp={"HTiltP" + S_: m("rl" + s, "RLerp", A=R0, B="@gt2%s.HTilt%s" % (s, S_), Alpha="@gw2%s.WH%s" % (s, S_),
                                                                     bShortestPath="true")})
        tail.append("sHTP" + S_)
    g.get("gwl", "HWaitL"); g.get("gwr", "HWaitR")
    g.call("hs0", K_MATH, "SelectString", inp={"A": "wait", "B": "-", "bPickA": m.OR("aw", "@gwl.HWaitL", "@gwr.HWaitR")})
    g.call("hs1", K_MATH, "SelectString", inp={"A": "on", "B": R("hs0"), "bPickA": m.OR("ao", ons["l"], ons["r"])})
    g.call("hs2", K_MATH, "SelectString", inp={"A": "held", "B": R("hs1"), "bPickA": m.AND("hd", act, v["Held"])})
    g.set("sHS", "HandState", inp={"HandState": R("hs2")})
    g.n("hst", "call_self", function="HandStillTick", inp={"pl": apos["l"], "pr": apos["r"], "dt": DT})   # before the near / on tests
    g.chain("entry", "hst", "thl", "thr", *tail, "sHS")
    return fn("HandTick", [param("mesh", MESH_T), param("ground", "float"), param("sz", "float"), param("dt", "float")], graph=g)


def f_hand_still_tick():
    """Round 4 (spec 7e.2, footik_sim.hand_still_step): per hand, the animated hand's speed (component cm/s) from last frame's
    position; slower than HandStill -> HStill += dt, else 0. The first frame (HPrev = 0) is a big jump -> 0."""
    g = G(); m = M(g); DT = "@entry.dt"; tail = []
    g.get("ghs", "HandStill")
    for s, S_ in (("l", "L"), ("r", "R")):
        P_ = "@entry.p" + s
        g.get("gp" + s, "HPrev" + S_); g.get("gt" + s, "HStill" + S_)
        # review I1: horizontal speed only - the hips' move and the hand IK move a hand in component Z only, so X / Y equal the
        # animation's whatever frame the reconstruction lags (no grab / let go / grab cycle)
        sp = m.div("sp" + s, m("ds" + s, "VSizeXY", A=m.vsub("dv" + s, P_, "@gp%s.HPrev%s" % (s, S_))), m("dm" + s, "FMax", A=DT, B="0.0001"))
        t = m.sel("tn" + s, m.add("ta" + s, "@gt%s.HStill%s" % (s, S_), DT), "0.0", m("sl" + s, "Less_FloatFloat", A=sp, B="@ghs.HandStill"))
        g.set("sHS" + S_, "HStill" + S_, inp={"HStill" + S_: t}); g.set("sHP" + S_, "HPrev" + S_, inp={"HPrev" + S_: P_})
        tail += ["sHS" + S_, "sHP" + S_]   # HStill reads HPrev before it is overwritten
    g.chain("entry", *tail)
    return fn("HandStillTick", [param("pl", VEC), param("pr", VEC), param("dt", "float")], graph=g)


def f_foot_tick():
    """Every frame: hard-off checks, pose type + mode, gate -> traces (+ forward spots) -> smoothed offsets / weight / tilts ->
    knee and hand contact -> the AnimBP's variables (footik_sim.decide / step / forward_shift / joint_offset). World cm (sockets,
    traces) are turned into mesh cm by the mesh's Z scale; the IK maths uses component-space sockets."""
    g = G(); m = M(g); PAWN = "@gpc.ReturnValue"
    g.call("gpc", K_GS, "GetPlayerCharacter", inp={"PlayerIndex": "0"})
    g.call("ivp", K_SYS, "IsValid", inp={"Object": PAWN}); g.branch("bvp", R("ivp"))
    g.get("gm", "Mesh", cls=E_CHARACTER); g.link("gpc.ReturnValue", "gm.self"); MESH = "@gm.Mesh"
    g.call("ppi", E_SKELMESHCOMP, "GetPostProcessInstance", inp={"self": MESH})
    g.cast("cab", ABP, R("ppi"), pure=False); AB = "@cab.AsABP Body Scale"   # AltUI: ABP_BodyScale
    g.set("rnb", "Reason", inp={"Reason": "no Foot IK body"}); g.set("rnw", "W", inp={"W": "0.0"})
    zero_w = ["WB", "WKL", "WKR", "WHL", "WHR", "PelAp", "HEzL", "HEzR", "ThL", "ThR", "FwdL", "FwdR", "EcL", "EcR", "HStillL", "HStillR"]   # + review M1, round 4
    for wv in zero_w: g.set("rz" + wv, wv, inp={wv: V0 if wv in ("EcL", "EcR") else "0.0"})
    words = [("ModeWord", ""), ("KneeMode", "-"), ("HandState", "-")]   # review M2: no stale words on the status line
    for wv, val in words: g.set("rz" + wv, wv, inp={wv: val})
    g.n("sqp", "call_self", function="SeqPlaying")
    # ---- scale + floors (review finding 2): traces from the real ground under the capsule, the gate from the mesh's Z
    g.call("gcs", E_SCENECOMP, "K2_GetComponentScale", inp={"self": MESH}); _, _, SZ = m.brk("bcs", R("gcs"))
    g.get("gcm", "CharacterMovement", cls=E_CHARACTER); g.link("gpc.ReturnValue", "gcm.self")
    g.get("gcap", "CapsuleComponent", cls=E_CHARACTER); g.link("gpc.ReturnValue", "gcap.self")
    g.call("hh", E_CAPSULE, "GetScaledCapsuleHalfHeight", inp={"self": "@gcap.CapsuleComponent"})
    g.call("al", E_ACTOR, "K2_GetActorLocation", inp={"self": PAWN}); _, _, az = m.brk("bal", R("al"))
    cap_bottom = m.sub("flr", az, R("hh"))
    g.get("gcf", "CurrentFloor", cls=E_CMC); g.link("gcm.CharacterMovement", "gcf.self")
    g.brk("bcf", "/Script/Engine.FindFloorResult", "@gcf.CurrentFloor")
    GROUND = m.sub("gnd", cap_bottom, "@bcf.FloorDist")
    g.call("mzl", E_SCENECOMP, "K2_GetComponentLocation", inp={"self": MESH}); _, _, MESHZ = m.brk("bmz", R("mzl"))
    # ---- the animated pose = the final pose minus what was applied last frame (mesh cm x scale = world cm)
    pos = {}; loc = {}
    for s, bone in (("l", "foot_l"), ("r", "foot_r"), ("p", "pelvis"), ("kl", "calf_l"), ("kr", "calf_r")):
        g.call("sk" + s, E_SCENECOMP, "GetSocketLocation", inp={"self": MESH, "InSocketName": bone}); loc[s] = R("sk" + s); pos[s] = m.brk("bk" + s, loc[s])
    for v in ("W", "OffL", "OffR", "Pel", "PelAp", "FwdL", "FwdR"): g.get("g" + v, v)
    for s, S_ in (("l", "L"), ("r", "R")): g.get("gec" + s, "Ec" + S_)
    pel_w = m.mul("pap", "@gPelAp.PelAp", SZ)   # round 3: the hips' applied move (foot IK + kneeling), last frame
    # final review I2: the final foot = animated + hips' move + the applied effector (Ec, component space)
    def applied(s, S_): return m.mul("ap" + s, m.add("ap0" + s, "@gPelAp.PelAp", m.brk("bec" + s, "@gec%s.Ec%s" % (s, S_))[2]), SZ)
    anim_l = m.sub("anl", pos["l"][2], applied("l", "L"))
    anim_r = m.sub("anr", pos["r"][2], applied("r", "R"))
    anim_p = m.sub("anp", pos["p"][2], pel_w)
    def mesh_cm(id, world): return m("mc" + id, "Divide_FloatFloat", A=world, B=SZ)
    g.get("gfh", "FootHeight")
    fh_l = m.sub("fhl", mesh_cm("fl", m.sub("fhl0", anim_l, MESHZ)), "@gfh.FootHeight")
    fh_r = m.sub("fhr", mesh_cm("fr", m.sub("fhr0", anim_r, MESHZ)), "@gfh.FootHeight")
    paf = mesh_cm("pa", m.sub("paf", anim_p, m.mul("mft", m.add("sft", anim_l, anim_r), "0.5")))
    kh_l = mesh_cm("kl", m.sub("khl", m.sub("khl0", pos["kl"][2], pel_w), MESHZ))
    kh_r = mesh_cm("kr", m.sub("khr", m.sub("khr0", pos["kr"][2], pel_w), MESHZ))
    mid = m("mid", "Multiply_VectorFloat", A=m("fsum", "Add_VectorVector", A=loc["l"], B=loc["r"]), B="0.5")
    horiz = mesh_cm("hz", m("hzw", "VSizeXY", A=m("pmv", "Subtract_VectorVector", A=loc["p"], B=mid)))
    # ---- pose type (footik_sim.pose_type) and its mode
    for k in ("On", "StillSpeed", "PlantedHeight", "MinPelvisHeight", "KneelKnee", "SitHoriz", "SitMode", "KneelMode", "CrouchBelow", "CrouchMode", "CrouchDrop"): g.get("g" + k, k)
    feet_up = m("cfe", "Greater_FloatFloat", A=m("mxf", "FMax", A=fh_l, B=fh_r), B="@gPlantedHeight.PlantedHeight")
    knees_low = m("ckn", "Less_FloatFloat", A=m("mxk", "FMax", A=kh_l, B=kh_r), B="@gKneelKnee.KneelKnee")
    near = m("cnr", "Less_FloatFloat", A=horiz, B="@gSitHoriz.SitHoriz")
    kneel = m("ckb", "BooleanAND", A=knees_low, B=near)
    low = m("cpe", "Less_FloatFloat", A=paf, B="@gMinPelvisHeight.MinPelvisHeight")
    sit = m("cst", "Not_PreBool", A=near)
    crouch = m("ccr", "Less_FloatFloat", A=paf, B="@gCrouchBelow.CrouchBelow")   # round 4 (spec 7e.1)
    pose = "stand"
    for i, (lit, cond) in enumerate([("crouch", crouch), ("sit", sit), ("lying", low), ("kneel", kneel), ("feet", feet_up)]):
        g.call("ps%d" % i, K_MATH, "SelectString", inp={"A": lit, "B": pose, "bPickA": cond}); pose = R("ps%d" % i)
    g.set("sPose", "Pose", inp={"Pose": pose})
    g.get("gpo", "Pose")
    def is_pose(id, name): g.call(id, K_STR, "EqualEqual_StrStr", inp={"A": "@gpo.Pose", "B": name}); return R(id)
    is_crouch = is_pose("ipc", "crouch")   # round 4 (spec 7e.1)
    mode = m("md0", "SelectFloat", A="@gCrouchMode.CrouchMode", B="2.0", bPickA=is_crouch)
    mode = m("md1", "SelectFloat", A="@gKneelMode.KneelMode", B=mode, bPickA=is_pose("ipk", "kneel"))
    mode = m("md2", "SelectFloat", A="@gSitMode.SitMode", B=mode, bPickA=is_pose("ips", "sit"))
    mode_off = m("mof", "Less_FloatFloat", A=mode, B="0.5")
    g.set("sLegs", "Legs", inp={"Legs": m("mlg", "NearlyEqual_FloatFloat", A=mode, B="1.0", ErrorTolerance="0.1")})
    # round 4 (spec 7e.3): the mode word of the on-screen line - only for the pose types that have a mode
    mw = m("mw1", "SelectString", A="legs", B="full", bPickA=R("mlg"))
    mw = m("mw2", "SelectString", A="off", B=mw, bPickA=mode_off)
    has_mode = m.OR("hmo", m.OR("hmo1", is_crouch, R("ips")), R("ipk"))
    g.set("sMW", "ModeWord", inp={"ModeWord": m("mw3", "SelectString", A=mw, B="", bPickA=has_mode)})
    # ---- hard off (spec 7b / 7c; signals: ledger round 2)
    g.call("sim", E_PRIMC, "IsSimulatingPhysics", inp={"self": MESH, "BoneName": "pelvis"})
    g.get("gmg", "Manager"); g.call("ivm", K_SYS, "IsValid", inp={"Object": "@gmg.Manager"})
    g.get("gjh", "JodiHidden", cls=MGR); g.link("gmg.Manager", "gjh.self"); g.get("gcmd", "CamMode", cls=MGR); g.link("gmg.Manager", "gcmd.self")
    # AltUI: the switches come from the manager's options, copied at the start of every frame (no manager -> all off)
    g.get("gfo", "FootIKOn", cls=MGR); g.link("gmg.Manager", "gfo.self"); g.get("gfc", "FootContactOn", cls=MGR); g.link("gmg.Manager", "gfc.self")
    g.set("swOn", "On", inp={"On": m.AND("swa", R("ivm"), "@gfo.FootIKOn")})
    contact = m.AND("swb", R("ivm"), "@gfc.FootContactOn")
    g.set("swKn", "KneeOn", inp={"KneeOn": contact}); g.set("swHn", "HandOn", inp={"HandOn": contact})
    cam = m("cmo0", "SelectInt", A="@gcmd.CamMode", B="0", bPickA=R("ivm"))
    hid = m("hid", "BooleanAND", A=R("ivm"), B="@gjh.JodiHidden")
    ragdoll = m("rg2", "BooleanOR", A=m("rg1", "BooleanOR", A=R("sim"), B=hid), B=m("cm3", "EqualEqual_IntInt", A=cam, B="3"))
    g.call("gpcc", K_GS, "GetPlayerController", inp={"PlayerIndex": "0"})
    g.get("gsm", "bShowMouseCursor", cls=E_PC_); g.link("gpcc.ReturnValue", "gsm.self")
    # AltUI: fitting room / menus = the mouse cursor OR AltUI's panel open
    g.get("gpno", "PanelOpen", cls=MGR); g.link("gmg.Manager", "gpno.self"); fit = m.OR("fit", "@gsm.bShowMouseCursor", m.AND("fpo", "@gpno.PanelOpen", m("fpc", "EqualEqual_IntInt", A=cam, B="0")))
    g.call("gvt", E_PC_, "GetViewTarget", inp={"self": R("gpcc")})
    other_cam = m("ovt", "NotEqual_ObjectObject", A=R("gvt"), B=PAWN)
    free_cam = m("fcm", "BooleanOR", A=m("cm1", "EqualEqual_IntInt", A=cam, B="1"), B=m("cm2", "EqualEqual_IntInt", A=cam, B="2"))
    cut = m("cut", "BooleanOR", A="@sqp.yes", B=m("ovc", "BooleanAND", A=other_cam, B=m("nfc", "Not_PreBool", A=free_cam)))
    g.call("gai", E_SKELMESHCOMP, "GetAnimInstance", inp={"self": MESH})
    g.call("gmo", E_ANIMI, "GetCurrentActiveMontage", inp={"self": R("gai")})
    g.call("mon", K_SYS, "GetObjectName", inp={"Object": R("gmo")})
    def mon_has(id, word):
        g.call(id, K_STR, "Contains", inp={"SearchIn": R("mon"), "Substring": word, "bUseCase": "false", "bSearchFromEnd": "false"}); return R(id)
    climbing = mon_has("mcl", "Climb")
    g.get("gjc", "JumpCurrentCount", cls=E_CHARACTER); g.link("gpc.ReturnValue", "gjc.self")
    jumping = m("jmp", "BooleanOR", A=m("jc0", "Greater_IntInt", A="@gjc.JumpCurrentCount", B="0"), B=mon_has("mju", "Jump"))
    g.call("grd", E_NAVMC, "IsMovingOnGround", inp={"self": "@gcm.CharacterMovement"})
    g.call("vel", E_ACTOR, "GetVelocity", inp={"self": PAWN}); spd = m("spd", "VSizeXY", A=R("vel"))
    moving = m("cmv", "GreaterEqual_FloatFloat", A=spd, B="@gStillSpeed.StillSpeed"); air = m("cai", "Not_PreBool", A=R("grd"))
    # ---- reason: same order as footik_sim.decide (built from the last check backwards)
    r = "on"
    checks = [("pose off", mode_off), ("lying", is_pose("ipl", "lying")), ("feet", is_pose("ipf", "feet")),
              ("moving", moving), ("air", air), ("jumping", jumping), ("climbing", climbing), ("cutscene", cut),
              ("fitting", fit), ("ragdoll", ragdoll), ("off", m("cof", "Not_PreBool", A="@gOn.On"))]
    for i, (lit, cond) in enumerate(checks):
        g.call("rs%d" % i, K_MATH, "SelectString", inp={"A": lit, "B": r, "bPickA": cond}); r = R("rs%d" % i)
    # Common (round 3): knee / hand contact run in every pose type but not with a hard off, in the air or moving
    blocked = ragdoll
    for i, c in enumerate((fit, cut, climbing, jumping, air, moving)): blocked = m.OR("blk%d" % i, blocked, c)
    g.set("sCom", "Common", inp={"Common": m.NOT("com", blocked)})
    g.set("sR", "Reason", inp={"Reason": r}); g.set("sPAF", "PAF", inp={"PAF": paf})
    g.set("sFHL", "FHL", inp={"FHL": fh_l}); g.set("sFHR", "FHR", inp={"FHR": fh_r})
    # ---- what the traces ignore: the pawn and everything attached to it (gun, props)
    g.call("gat", E_ACTOR, "GetAttachedActors", inp={"self": PAWN}); g.set("sig", "Ignore", inp={"Ignore": "@gat.OutActors"})
    g.get("gig", "Ignore"); g.call("aig", K_ARR, "Array_Add", inp={"TargetArray": "@gig.Ignore", "NewItem": PAWN})
    g.call("ctw", E_SCENECOMP, "K2_GetComponentToWorld", inp={"self": MESH})
    g.call("afw", E_ACTOR, "GetActorForwardVector", inp={"self": PAWN}); fx, fy, _ = m.brk("baf", R("afw"))
    fwd_w = m.norm("afh", m.vec("afz", fx, fy, "0.0"))                                 # Jodi's facing, world, horizontal
    fwc = m("fwc", "InverseTransformDirection", T=R("ctw"), Direction=fwd_w); cx, cy, _ = m.brk("bfc", fwc)
    FWD = m.norm("fwn", m.vec("fwz", cx, cy, "0.0"))                                    # the same in mesh space
    anim_xy = {}
    for s, S_ in (("l", "L"), ("r", "R")):   # final review I1: under the animated foot (final minus last frame's forward move)
        anim_xy[s] = m.vsub("axy" + s, loc[s], m.vmul("axm" + s, fwd_w, m.mul("axw" + s, m.mul("axf" + s, "@gW.W", "@gFwd%s.Fwd%s" % (S_, S_)), SZ)))
        ax_, ay_, _ = m.brk("bxy" + s, anim_xy[s])
        g.n("tr" + s, "call_self", function="Trace", inp={"x": ax_, "y": ay_, "floor": GROUND})
    # ---- targets (footik_sim.targets), in mesh cm; Legs only: no hip drop
    for k in ("MaxStep", "MaxPelvisDrop", "Smoothing", "BlendTime", "MaxTilt", "KneeFollow", "FwdSame"): g.get("g" + k, k)
    nms = m.mul("nms", "@gMaxStep.MaxStep", "-1.0")
    tgt = {}; ok1 = {}
    for s in ("l", "r"):
        hs = m("hs" + s, "Divide_FloatFloat", A="@tr%s.h" % s, B=SZ)
        # a hit beyond +-MaxStep (chair seat over the ankle, a ledge) counts as no hit (review finding 3)
        inr = m("ir" + s, "InRange_FloatFloat", Value=hs, Min=nms, Max="@gMaxStep.MaxStep", InclusiveMin="true", InclusiveMax="true")
        ok1[s] = m("ok" + s, "BooleanAND", A="@tr%s.hit" % s, B=inr)
        tgt[s] = m("tg" + s, "SelectFloat", A=hs, B="0.0", bPickA=ok1[s])
    # ---- knee follows foot (spec 7d.1, footik_sim.forward_shift / forward_accept): a raised foot goes forward by k x rise,
    # limited to 98 % of thigh + calf; it lands at the forward spot only if that spot is within FwdSame of the first trace
    kf = m.mul("kf", "@gKneeFollow.KneeFollow", "0.01")
    tgf = {}; nrm = {}; fwd_t = {}; cs = {}
    for s, S_ in (("l", "L"), ("r", "R")):
        hip, _ = sock_cs(g, "sth" + s, MESH, "thigh_" + s); knee, krot = sock_cs(g, "scl" + s, MESH, "calf_" + s)
        foot, frot = sock_cs(g, "sx" + s, MESH, "foot_" + s); cs[s] = (hip, frot, foot)
        rise = m("rs" + s + "x", "FMax", A="0.0", B=m.sub("rd" + s, "@gOff%s.Off%s" % (S_, S_), "@gPel.Pel"))
        D = m.vsub("dv" + s, m.vadd("dt" + s, m.vsub("fa" + s, foot, "@gec%s.Ec%s" % (s, S_)), m.vec("ru" + s, "0.0", "0.0", rise)), hip)
        leg = m.add("lg" + s, m.size("l1" + s, m.vsub("u1" + s, knee, hip)), m.size("l2" + s, m.vsub("u2" + s, foot, knee)))
        rr = m.mul("rr" + s, leg, repr(S.REACH))
        df = m.dot("df" + s, D, FWD)
        disc = m.add("ds" + s, m.sub("ds1" + s, m.mul("ds2" + s, df, df), m.dot("ds3" + s, D, D)), m.mul("ds4" + s, rr, rr))
        f = m("fm" + s, "FMin", A=m.mul("fw" + s, kf, rise),
              B=m.sub("fx" + s, m("sq" + s, "Sqrt", A=m("dp" + s, "FMax", A=disc, B="0.0")), df))
        inreach = m("rch" + s, "LessEqual_FloatFloat", A=m.size("fd" + s, m.vadd("fv" + s, D, m.vmul("ff" + s, FWD, f))), B=m.add("rre" + s, rr, "0.001"))
        fok = m.AND("fk" + s, m.AND("fk1" + s, m("dg" + s, "GreaterEqual_FloatFloat", A=disc, B="0.0"),
                                       m("fp" + s, "Greater_FloatFloat", A=f, B="0.0")), inreach)
        fT = m.sel("ft" + s, f, "0.0", fok)
        spot = m.vadd("sp" + s, anim_xy[s], m.vmul("sw" + s, fwd_w, m.mul("swz" + s, fT, SZ)))
        sx_, sy_, _ = m.brk("bs" + s, spot)
        g.n("tf" + s, "call_self", function="Trace", inp={"x": sx_, "y": sy_, "floor": GROUND})
        h2 = m.div("h2" + s, "@tf%s.h" % s, SZ)
        same = m("fsm" + s, "LessEqual_FloatFloat", A=m("fab" + s, "Abs", A=m.sub("fdh" + s, h2, tgt[s])), B="@gFwdSame.FwdSame")
        h2ok = m("i2" + s, "InRange_FloatFloat", Value=h2, Min=nms, Max="@gMaxStep.MaxStep", InclusiveMin="true", InclusiveMax="true")   # review M2
        acc = m.AND("acc" + s, m.AND("ac1" + s, m.AND("ac2" + s, fok, ok1[s]), m.AND("ac3" + s, "@tf%s.hit" % s, h2ok)), same)
        g.set("sAc" + S_, "Acc" + S_, inp={"Acc" + S_: acc}); g.set("sFt" + S_, "Ft" + S_, inp={"Ft" + S_: fT})   # cached (Ec / Off change later)
        g.get("gac" + s, "Acc" + S_); g.get("gft" + s, "Ft" + S_); acc, fT = "@gac%s.Acc%s" % (s, S_), "@gft%s.Ft%s" % (s, S_)
        tgf[s] = m.sel("tgf" + s, h2, tgt[s], acc)
        nrm[s] = m("nm" + s, "SelectVector", A="@tf%s.n" % s, B="@tr%s.n" % s, bPickA=acc)
        fwd_t[s] = m.sel("fT" + s + "x", fT, "0.0", acc)
        ok1[s] = m.OR("okf" + s, ok1[s], acc)
    m("tpm", "FMax", A=m("npd", "Multiply_FloatFloat", A=m("hlm", "SelectFloat", A="@gCrouchDrop.CrouchDrop",   # round 4: crouch limit
                                                       B="@gMaxPelvisDrop.MaxPelvisDrop", bPickA=is_crouch), B="-1.0"),
      B=m("tpn", "FMin", A=m("tpz", "FMin", A="0.0", B=tgf["l"]), B=tgf["r"]))
    g.get("glg", "Legs"); g.call("legs", K_MATH, "Not_PreBool", inp={"A": m("nlg", "Not_PreBool", A="@glg.Legs")})   # = Legs, a typed bool pin
    tp = m("tpl", "SelectFloat", A="0.0", B="@tpm.ReturnValue", bPickA="@legs.ReturnValue")
    k = m("ks", "FMin", A="1.0", B=m.mul("kd", "@gSmoothing.Smoothing", "@entry.dt"))
    g.get("gR2", "Reason"); g.call("ison", K_STR, "EqualEqual_StrStr", inp={"A": "@gR2.Reason", "B": "on"})
    wt = m("wt", "SelectFloat", A="1.0", B="0.0", bPickA=R("ison"))
    wsp = m("wsp", "Divide_FloatFloat", A="1.0", B=m("bt", "FMax", A="@gBlendTime.BlendTime", B="0.001"))
    g.set("sW", "W", inp={"W": m("wn", "FInterpTo_Constant", Current="@gW.W", Target=wt, DeltaTime="@entry.dt", InterpSpeed=wsp)})
    def smooth(id, cur, target): return m.add(id, cur, m.mul(id + "k", m.sub(id + "d", target, cur), k))
    g.set("sOL", "OffL", inp={"OffL": smooth("nol", "@gOffL.OffL", tgf["l"])})
    g.set("sOR", "OffR", inp={"OffR": smooth("nor", "@gOffR.OffR", tgf["r"])})
    g.set("sP", "Pel", inp={"Pel": smooth("npe", "@gPel.Pel", tp)})
    g.set("sFL", "FwdL", inp={"FwdL": smooth("nfl", "@gFwdL.FwdL", fwd_t["l"])})
    g.set("sFR", "FwdR", inp={"FwdR": smooth("nfr", "@gFwdR.FwdR", fwd_t["r"])})
    # ---- foot tilts: impact normal in component space, clamped to MaxTilt, MakeRotFromZX (footik_sim.tilt), smoothed
    for s, side in (("l", "L"), ("r", "R")):
        trot = tilt_target(g, m, "f" + s, nrm[s], R("ctw"), "@gMaxTilt.MaxTilt", ok1[s])
        g.get("gt" + side, "Tilt" + side)
        g.set("sT" + side, "Tilt" + side, inp={"Tilt" + side: m("ri" + s, "RInterpTo", Current="@gt%s.Tilt%s" % (side, side), Target=trot,
                                                                 DeltaTime="@entry.dt", InterpSpeed="@gSmoothing.Smoothing")})
    # ---- knee contact, the hips' total move, hand contact (round 3)
    cargs = {"mesh": MESH, "ground": GROUND, "sz": SZ, "dt": "@entry.dt"}
    g.n("ckt", "call_self", function="KneeTick", inp=dict(cargs))
    for v in ("W", "OffL", "OffR", "Pel", "TiltL", "TiltR", "WB", "PelK", "FwdL", "FwdR", "WKL", "WKR", "KneeRotL", "KneeRotR",
              "KneeFootL", "KneeFootR", "HEffL", "HEffR", "HTiltPL", "HTiltPR", "WHL", "WHR", "PelNow", "FwdBlend", "FwdReach"): g.get("n" + v, v)
    g.set("sPN", "PelNow", inp={"PelNow": m.add("pn", m.mul("pn1", "@nW.W", "@nPel.Pel"), m.mul("pn2", "@nWB.WB", "@nPelK.PelK"))})
    g.n("chk", "call_self", function="HoldCheck", inp={"mesh": MESH}); g.set("sHe", "Held", inp={"Held": "@chk.yes"})
    g.n("cht", "call_self", function="HandTick", inp=dict(cargs))
    # ---- into the AnimBP (every frame, pre-multiplied: a new post-process instance gets them at once)
    eff = {}; feff = {}; fj = {}; afw_ = {}; ec_sets = []
    for s, side in (("l", "L"), ("r", "R")):
        hip, frot, foot = cs[s]
        upz = m.sub("ez" + s, m.sub("ez0" + s, "@nOff%s.Off%s" % (side, side), "@nPel.Pel"), m.mul("ezk" + s, "@nWB.WB", "@nPelK.PelK"))
        up_cs = m.vmul("eu" + s, m.vec("ev" + s, "0.0", "0.0", upz), "@nW.W")                                 # pass A (component)
        fw_amt = m.mul("fa" + s + "x", "@nW.W", "@nFwd%s.Fwd%s" % (side, side))
        fw_cs = m.vmul("eb" + s, FWD, fw_amt)                                                                  # pass B (component)
        g.set("sEc" + side, "Ec" + side, inp={"Ec" + side: m.vadd("ec" + s, up_cs, fw_cs)}); ec_sets.append("sEc" + side)
        eff[side] = m("ef" + s, "LessLess_VectorRotator", A=up_cs, B=frot)   # UnrotateVector: into the foot's own axes
        feff[side] = m("fe" + s, "LessLess_VectorRotator", A=fw_cs, B=frot)  # the foot keeps its rotation through pass A
        # pass B's joint target (component space): middle of hip - foot + (forward + up) x FwdReach (no knee: no feedback)
        fj[side] = m.vadd("fj" + s, m.vmul("fm" + s + "x", m.vadd("fs" + s, hip, foot), "0.5"),
                          m.vmul("fr" + s + "x", m.vadd("fu" + s, FWD, m.vec("fz" + s, "0.0", "0.0", "1.0")), "@nFwdReach.FwdReach"))
        afw_[side] = m("fc" + s, "FClamp", Value=m.div("fb" + s, fw_amt, m("fbm" + s, "FMax", A="@nFwdBlend.FwdBlend", B="0.001")), Min="0.0", Max="1.0")
    pv = m.vec("pv", "0.0", "0.0", "@nPelNow.PelNow")
    def active(id, a, b): return m.sel(id, "1.0", "0.0", m.OR(id + "o", m("%sa" % id, "Greater_FloatFloat", A=a, B="0.0"),
                                                              m("%sb" % id, "Greater_FloatFloat", A=b, B="0.0")))
    tilt = {sd: m("rl" + sd, "RLerp", A=R0, B="@nTilt%s.Tilt%s" % (sd, sd), Alpha="@nW.W", bShortestPath="true") for sd in ("L", "R")}
    sets = [("aPel", "IKPelvis", pv), ("aTL", "TiltL", tilt["L"]), ("aTR", "TiltR", tilt["R"]), ("aEL", "EffL", eff["L"]), ("aER", "EffR", eff["R"]),
            ("aFEL", "FwdEffL", feff["L"]), ("aFER", "FwdEffR", feff["R"]), ("aFJL", "FwdJL", fj["L"]), ("aFJR", "FwdJR", fj["R"]),
            ("aKRL", "KneeRotL", "@nKneeRotL.KneeRotL"), ("aKRR", "KneeRotR", "@nKneeRotR.KneeRotR"),
            ("aKFL", "KneeFootL", "@nKneeFootL.KneeFootL"), ("aKFR", "KneeFootR", "@nKneeFootR.KneeFootR"),
            ("aHTL", "HandTiltL", "@nHTiltPL.HTiltPL"), ("aHTR", "HandTiltR", "@nHTiltPR.HTiltPR"),
            ("aHEL", "HandEffL", "@nHEffL.HEffL"), ("aHER", "HandEffR", "@nHEffR.HEffR"),
            ("aAL", "ALeg", active("alg", "@nW.W", "@nWB.WB")), ("aAFL", "AFwdL", afw_["L"]), ("aAFR", "AFwdR", afw_["R"]),
            ("aAK", "AKnee", active("akn", "@nWKL.WKL", "@nWKR.WKR")),
            ("aAH", "AHand", active("ahd", "@nWHL.WHL", "@nWHR.WHR"))]
    for id, v, val in sets: g.n(id, "set", var=v, cls=ABP, inp={"self": AB, v: val})
    g.set("sPA", "PelAp", inp={"PelAp": "@nPelNow.PelNow"})
    # AltUI: nothing left to do -> tick off (after the ABP sets, so the zeros arrive); the manager's Wake turns it on again.
    # Another body (cast failed): off as soon as all switches are off (the weights are set to 0 there).
    for v in ("KneeOn", "HandOn"): g.get("gi" + v, v)
    def all_off(p): return m.AND(p + "a", m.NOT(p + "n0", "@gOn.On"), m.AND(p + "b", m.NOT(p + "n1", "@giKneeOn.KneeOn"), m.NOT(p + "n2", "@giHandOn.HandOn")))
    wsum = m.add("iw4", m.add("iw3", m.add("iw2", m.add("iw1", "@nWB.WB", "@nWKL.WKL"), "@nWKR.WKR"), "@nWHL.WHL"), "@nWHR.WHR")
    zero = m.AND("iz", m("iz0", "EqualEqual_FloatFloat", A="@nW.W", B="0.0"), m("iz1", "EqualEqual_FloatFloat", A=wsum, B="0.0"))
    g.branch("bidl", m.AND("idl", all_off("io"), zero)); g.call("tidl", E_ACTOR, "SetActorTickEnabled", inp={"bEnabled": "false"})
    g.branch("bidf", all_off("if")); g.call("tidf", E_ACTOR, "SetActorTickEnabled", inp={"bEnabled": "false"})
    g.chain("entry", "swOn", "swKn", "swHn", "bvp", "cab", "sqp", "sPose", "sLegs", "sMW", "sCom", "sR", "sPAF", "sFHL", "sFHR", "sig", "aig", "trl", "trr", "tfl", "tfr", "sAcL", "sFtL", "sAcR", "sFtR",
            "sW", "sOL", "sOR", "sP", "sFL", "sFR", "sTL", "sTR", "ckt", "sPN", "chk", "sHe", "cht", *ec_sets, *[s[0] for s in sets], "sPA", "bidl", "tidl")
    g.chain("cab:CastFailed", "rnb", "rnw", *["rz" + wv for wv in zero_w + [w_ for w_, _ in words]], "bidf", "tidf")
    return fn("FootTick", [param("dt", "float")], graph=g)


def f_wake():
    """The manager calls this after changing a switch (the actor turns its tick off when there is nothing to do)."""
    g = G(); g.call("te", E_ACTOR, "SetActorTickEnabled", inp={"bEnabled": "true"}); g.chain("entry", "te")
    return fn("Wake", graph=g)


def event_graph():
    g = G()
    g.event("tk", E_ACTOR, "ReceiveTick"); g.n("ft", "call_self", function="FootTick", inp={"dt": "@tk.DeltaSeconds"}); g.chain("tk", "ft")
    return g


def prune_dead_math(f):
    """KneeTick ignores arc_nodes' joint target (jt): its maths nodes feed nobody. The compiler drops them anyway; removing them
    here keeps BenenG47's code unchanged and test_graph_exec's dead-node check clean."""
    gr = f["graph"]
    while True:
        used = {v[1:].split(".")[0] for n in gr["nodes"] for v in n.get("in", {}).values() if isinstance(v, str) and v.startswith("@")}
        used |= {a.split(".")[0] for a, _ in gr["links"]} | {s.split(":")[0] for c in gr["exec"] for s in c}
        dead = [n for n in gr["nodes"] if n["kind"] == "call" and n.get("class") == K_MATH and n["id"] not in used]
        if not dead: return f
        gr["nodes"] = [n for n in gr["nodes"] if n not in dead]


def build():
    flt = lambda n: var(n, "float", default="0.0")
    values = [var(k, "bool", default="false") for k in SWITCHES] + [var(k, "float", default=repr(float(S.DEFAULTS[k]))) for k in VALUE_KEYS]
    work = [var("Reason", "string", default="off"), *map(flt, ("W", "OffL", "OffR", "Pel", "PAF", "FHL", "FHR")), var("TiltL", ROT, default=R0),
            var("TiltR", ROT, default=R0), var("Ignore", "object:" + E_ACTOR, "array"),
            var("Pose", "string", default="stand"), var("Legs", "bool", default="false"), var("Manager", "object:" + MGR), var("SeqOn", "bool", default="false"),
            var("SeqLoop", "object:" + E_ACTOR, "array"),
            # round 3: forward foot, knee contact, hand contact, the hips' total move
            var("KinL", VEC, default=V0), var("KinR", VEC, default=V0), var("HOnL", "bool", default="false"), var("HOnR", "bool", default="false"),
            var("HUseL", "bool", default="false"), var("HUseR", "bool", default="false"), var("AccL", "bool", default="false"),
            var("AccR", "bool", default="false"), *map(flt, ("FtL", "FtR")),
            *map(flt, ("FwdL", "FwdR", "PelAp", "PelNow", "WB", "PelK", "WKL", "WKR", "ThL", "ThR", "LiftL", "LiftR",
                       "WHL", "WHR", "HOffL", "HOffR", "HEzL", "HEzR")),
            var("EcL", VEC, default=V0), var("EcR", VEC, default=V0), var("KneeRotL", ROT, default=R0), var("KneeRotR", ROT, default=R0),
            var("KneeFootL", ROT, default=R0), var("KneeFootR", ROT, default=R0),
            var("HEffL", VEC, default=V0), var("HEffR", VEC, default=V0), var("HTiltL", ROT, default=R0), var("HTiltR", ROT, default=R0),
            var("HTiltPL", ROT, default=R0), var("HTiltPR", ROT, default=R0),
            var("Common", "bool", default="false"), var("Held", "bool", default="false"), var("HeldOn", "bool", default="false"),
            var("HoldLoop", "object:" + E_SCENECOMP, "array"), var("KneeMode", "string", default="-"), var("HandState", "string", default="-"),
            # round 4: mode word, still hands (spec 7e.2)
            var("ModeWord", "string", default=""), var("HPrevL", VEC, default=V0), var("HPrevR", VEC, default=V0),
            *map(flt, ("HStillL", "HStillR")), var("HWaitL", "bool", default="false"), var("HWaitR", "bool", default="false")]
    return [blueprint(FOOTIK, E_ACTOR, variables=values + work,
                      functions=[f_trace(), f_seq_playing(), f_hold_check(), prune_dead_math(f_knee_tick()), f_hand_tick(), f_foot_tick(), f_hand_still_tick(),
                                 f_wake()], event_graph=event_graph())]


assets = build()
write(os.path.join(os.path.dirname(__file__), "..", "45_footik.json"), assets)
