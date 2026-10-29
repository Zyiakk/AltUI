#!/usr/bin/env python3
"""Generates assets/29d_hand.json: BP_AltUIHand, the invisible hand with its own range and items per round
(docs/specs/2026-10-25-invisible-hand-design.md). The game's InvisibleHand_Comp scans a fixed box (half 180 x 180 x 100 around
the feet + 90 cm, a constant in its bytecode) and sends ONE item per round flying (FlyingItem_Comp -> Jodi.On Item Picked). While
the option is on, this actor does the same scan with its own box and count, keeps the game's scan waiting (Hand.time far ahead)
and gives it back (time 0) when it stops. Only items the game marks Can Be Auto Picked; the flag is never set here."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *
from gen_ragdoll import ident_tf

HAND = M + "/BP_AltUIHand"
E_ACTC = "/Script/Engine.ActorComponent"; E_PRIMC = "/Script/Engine.PrimitiveComponent"; E_SCENEC = "/Script/Engine.SceneComponent"
S_VEC = "struct:/Script/CoreUObject.Vector"
BOX_HALF = (180.0, 180.0, 100.0)   # InvisibleHand_Comp.On Tick: the extent of its BoxOverlapComponents
BOX_RISE = 90.0                    # ... centred at get Foot Location + (0, 0, 90)
Z_CAP = 2.0                        # the height grows at most to 2x: other floors stay out
RANGE_MIN, RANGE_MAX = 1.0, 10.0
BATCH_MIN, BATCH_MAX = 1, 20
NOHAND_INTERVAL = 2.5              # Update Power(1): max(3 - 0.5, 0.1) - the pace of one hand
QUIET = 1000000.0                  # Hand.time = now + QUIET: the game's scan waits while this one runs
OBJ_TYPE = "ObjectTypeQuery4"      # the game's ObjectTypes (byte 3)


def f_hand_extent():
    """Half extent of the scan box for range r (0 = never set = 1): (180 r, 180 r, 100 min(r, 2))."""
    g = G(); g.call("set", K_MATH, "Greater_FloatFloat", inp={"A": "@entry.range", "B": "0.0"})
    g.call("r0", K_MATH, "SelectFloat", inp={"A": "@entry.range", "B": "1.0", "bPickA": "@set.ReturnValue"})
    g.call("r", K_MATH, "FClamp", inp={"Value": "@r0.ReturnValue", "Min": str(RANGE_MIN), "Max": str(RANGE_MAX)})
    g.call("rz", K_MATH, "FMin", inp={"A": "@r.ReturnValue", "B": str(Z_CAP)})
    g.call("x", K_MATH, "Multiply_FloatFloat", inp={"A": "@r.ReturnValue", "B": str(BOX_HALF[0])})
    g.call("y", K_MATH, "Multiply_FloatFloat", inp={"A": "@r.ReturnValue", "B": str(BOX_HALF[1])})
    g.call("z", K_MATH, "Multiply_FloatFloat", inp={"A": "@rz.ReturnValue", "B": str(BOX_HALF[2])})
    g.call("v", K_MATH, "MakeVector", inp={"X": "@x.ReturnValue", "Y": "@y.ReturnValue", "Z": "@z.ReturnValue"}); g.link("v.ReturnValue", "return.extent")
    return fn("Hand Extent", [param("range", "float")], [param("extent", S_VEC)], graph=g, pure=True)


def f_hand_wanted():
    """Run instead of the game: on, and the hand is in the backpack (its tick is on) or the 'without a hand' option."""
    g = G(); g.call("o", K_MATH, "BooleanOR", inp={"A": "@entry.ticking", "B": "@entry.nohand"})
    g.call("a", K_MATH, "BooleanAND", inp={"A": "@entry.on", "B": "@o.ReturnValue"}); g.link("a.ReturnValue", "return.yes")
    return fn("Hand Wanted", [param("on", "bool"), param("ticking", "bool"), param("nohand", "bool")], [param("yes", "bool")], graph=g, pure=True)


def f_hand_interval():
    """Seconds per round: the hand's own interval while it ticks (faster with more hands), else the pace of one hand."""
    g = G(); g.call("m", K_MATH, "FMax", inp={"A": "@entry.interval", "B": "0.1"})
    g.call("s", K_MATH, "SelectFloat", inp={"A": "@m.ReturnValue", "B": str(NOHAND_INTERVAL), "bPickA": "@entry.ticking"}); g.link("s.ReturnValue", "return.v")
    return fn("Hand Interval", [param("ticking", "bool"), param("interval", "float")], [param("v", "float")], graph=g, pure=True)


def f_batch_count():
    """Items per round from the setting (0 = never set = 1), whole, BATCH_MIN..BATCH_MAX."""
    g = G(); g.call("set", K_MATH, "Greater_FloatFloat", inp={"A": "@entry.batch", "B": "0.0"})
    g.call("b0", K_MATH, "SelectFloat", inp={"A": "@entry.batch", "B": "1.0", "bPickA": "@set.ReturnValue"})
    g.call("r", K_MATH, "Round", inp={"A": "@b0.ReturnValue"}); g.call("c", K_MATH, "Clamp", inp={"Value": "@r.ReturnValue", "Min": str(BATCH_MIN), "Max": str(BATCH_MAX)})
    g.link("c.ReturnValue", "return.n")
    return fn("Batch Count", [param("batch", "float")], [param("n", "int")], graph=g, pure=True)


def f_pick_allowed():
    """An item of the box is taken: auto-pickable, not flying yet, and the round still has room."""
    g = G(); g.call("nf", K_MATH, "Not_PreBool", inp={"A": "@entry.flying"}); g.call("lt", K_MATH, "Less_IntInt", inp={"A": "@entry.count", "B": "@entry.max"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@entry.auto", "B": "@nf.ReturnValue"}); g.call("a2", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@lt.ReturnValue"})
    g.link("a2.ReturnValue", "return.yes")
    return fn("Pick Allowed", [param("auto", "bool"), param("flying", "bool"), param("count", "int"), param("max", "int")], [param("yes", "bool")], graph=g, pure=True)


def f_set_hand():
    g = G(); g.set("so", "On", inp={"On": "@entry.on"}); g.set("sr", "Range", inp={"Range": "@entry.range"}); g.set("sb", "Batch", inp={"Batch": "@entry.batch"})
    g.set("sn", "NoHand", inp={"NoHand": "@entry.nohand"}); g.chain("entry", "so", "sr", "sb", "sn")
    return fn("Set Hand", [param("on", "bool"), param("range", "float"), param("batch", "float"), param("nohand", "bool")], graph=g)


def f_release():
    """Give the game its scan back (time 0 = due at once), if this actor had taken it."""
    g = G(); g.get("gh", "Hand"); g.call("vh", K_SYS, "IsValid", inp={"Object": "@gh.Hand"}); g.branch("bh", "@vh.ReturnValue")
    g.get("ga", "Active"); g.branch("ba", "@ga.Active")
    g.set("st", "time", cls=P_IHC, inp={"self": "@gh.Hand", "time": "0.0"}); g.set("sa", "Active", inp={"Active": "false"})
    g.chain("entry", "bh", "ba", "st", "sa"); g.chain("bh:else", "sa"); g.chain("ba:else", "sa")
    return fn("Release", graph=g)


def f_bind():
    """A (new) player character: the old hand gets its scan back, the new one is Jodi's InvisibleHand_Comp (none on another pawn class)."""
    g = G(); g.n("rl", "call_self", function="Release")
    g.set("sb", "Bound", inp={"Bound": "@entry.jodi"}); g.set("sn", "Next", inp={"Next": "0.0"})
    g.cast("cj", P_JODI, "@entry.jodi"); g.call("vj", K_SYS, "IsValid", inp={"Object": "@cj.AsJodi"}); g.branch("bj", "@vj.ReturnValue")
    g.get("gih", "InvisibleHand_Comp", cls=P_JODI); g.link("cj.AsJodi", "gih.self")
    g.set("sh", "Hand", inp={"Hand": "@gih.InvisibleHand_Comp"}); g.set("sh0", "Hand")
    g.chain("entry", "rl", "sb", "sn", "bj", "sh"); g.chain("bj:else", "sh0")
    return fn("Bind", [param("jodi", "object:" + P_CPB)], graph=g)


def f_pick():
    """One item, the game's way (InvisibleHand_Comp.On Tick): a simulating body is first put where its component is, physics off,
    the component snapped to its actor's root; then a FlyingItem_Comp on the actor, Init with the hand - it flies there and calls
    Jodi.On Item Picked."""
    g = G(); g.call("ow", E_ACTC, "GetOwner", inp={"self": "@entry.comp"})
    g.call("sim", E_PRIMC, "IsSimulatingPhysics", inp={"self": "@entry.comp", "BoneName": "None"}); g.branch("bsim", "@sim.ReturnValue")
    g.call("cl", E_SCENEC, "K2_GetComponentLocation", inp={"self": "@entry.comp"})
    g.call("sal", E_ACTOR, "K2_SetActorLocation", inp={"self": "@ow.ReturnValue", "NewLocation": "@cl.ReturnValue", "bSweep": "false", "bTeleport": "false"})
    g.call("ssp", E_PRIMC, "SetSimulatePhysics", inp={"self": "@entry.comp", "bSimulate": "false"})
    g.call("rt", E_ACTOR, "K2_GetRootComponent", inp={"self": "@ow.ReturnValue"})
    g.call("att", E_SCENEC, "K2_AttachToComponent", inp={"self": "@entry.comp", "Parent": "@rt.ReturnValue", "SocketName": "None", "LocationRule": "SnapToTarget",
                                                           "RotationRule": "SnapToTarget", "ScaleRule": "SnapToTarget", "bWeldSimulatedBodies": "true"})
    g.call("ac", E_ACTOR, "AddComponentByClass", inp={"self": "@ow.ReturnValue", "Class": P_FLYING, "bManualAttachment": "false", "RelativeTransform": ident_tf(g), "bDeferredFinish": "false"})
    g.cast("cf", P_FLYING, "@ac.ReturnValue"); g.get("gh", "Hand")
    g.call("ini", P_FLYING, "Init", inp={"self": "@cf.AsFlying Item Comp", "invisible Comp": "@gh.Hand"})
    g.chain("entry", "bsim", "sal", "ssp", "att", "ac", "ini"); g.chain("bsim:else", "ac")
    return fn("Pick", [param("comp", "object:" + P_PICKABLE)], graph=g)


def f_scan():
    """One round: the box around Jodi's feet; the first <batch> auto-pickable items that are not flying yet."""
    g = G(); g.get("gb", "Bound"); g.call("ft", P_CB, "get Foot Location", inp={"self": "@gb.Bound"})
    g.call("ctr", K_MATH, "Add_VectorVector", inp={"A": "@ft.location", "B": "(X=0,Y=0,Z=%s)" % BOX_RISE})
    g.get("gr", "Range"); g.n("ex", "call_self", function="Hand Extent", inp={"range": "@gr.Range"})
    g.n("ot", "make_array", count=1, type="enum:/Script/Engine.EObjectTypeQuery", inp={"[0]": OBJ_TYPE})
    g.n("ign", "make_array", count=0, type="object:" + E_ACTOR); g.self_("me")
    g.call("bo", K_SYS, "BoxOverlapComponents", inp={"WorldContextObject": "@me.self", "BoxPos": "@ctr.ReturnValue", "Extent": "@ex.extent", "ObjectTypes": "@ot.Array",
                                                      "ComponentClassFilter": P_PICKABLE, "ActorsToIgnore": "@ign.Array"})
    g.set("s0", "Count", inp={"Count": "0"}); g.foreach("fe", "@bo.OutComponents")
    g.cast("cp", P_PICKABLE, "@fe.Array Element"); g.call("vp", K_SYS, "IsValid", inp={"Object": "@cp.AsItem Comp Pickable"}); g.branch("bv", "@vp.ReturnValue")
    g.get("gau", "Can Be Auto Picked", cls=P_PICKABLE); g.link("cp.AsItem Comp Pickable", "gau.self")
    g.call("ow", E_ACTC, "GetOwner", inp={"self": "@cp.AsItem Comp Pickable"})
    g.call("fl", E_ACTOR, "GetComponentByClass", inp={"self": "@ow.ReturnValue", "ComponentClass": P_FLYING}); g.call("vfl", K_SYS, "IsValid", inp={"Object": "@fl.ReturnValue"})
    g.get("gc", "Count"); g.get("gbt", "Batch"); g.n("bn", "call_self", function="Batch Count", inp={"batch": "@gbt.Batch"})
    g.n("pa", "call_self", function="Pick Allowed", inp={"auto": "@gau.Can Be Auto Picked", "flying": "@vfl.ReturnValue", "count": "@gc.Count", "max": "@bn.n"}); g.branch("bpa", "@pa.yes")
    g.n("pk", "call_self", function="Pick", inp={"comp": "@cp.AsItem Comp Pickable"})
    g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gc.Count", "B": "1"}); g.set("sc", "Count", inp={"Count": "@inc.ReturnValue"})
    g.chain("entry", "bo", "s0", "fe"); g.chain("fe", "bv", "bpa", "pk", "sc")
    return fn("Scan", graph=g)


def f_step():
    """Per tick on the bound hand: not wanted -> give the scan back; wanted -> hand.Jodi set, the game's scan kept waiting, a round when due
    (not while Jodi is a ragdoll, like the game)."""
    g = G(); g.get("gh", "Hand"); g.call("vh", K_SYS, "IsValid", inp={"Object": "@gh.Hand"}); g.branch("bh", "@vh.ReturnValue")
    g.call("tk", E_ACTC, "IsComponentTickEnabled", inp={"self": "@gh.Hand"}); g.get("go", "On"); g.get("gn", "NoHand")
    g.n("hw", "call_self", function="Hand Wanted", inp={"on": "@go.On", "ticking": "@tk.ReturnValue", "nohand": "@gn.NoHand"}); g.branch("bw", "@hw.yes")
    g.n("rl", "call_self", function="Release")
    g.get("gb", "Bound"); g.cast("cj", P_JODI, "@gb.Bound"); g.set("sj", "Jodi", cls=P_IHC, inp={"self": "@gh.Hand", "Jodi": "@cj.AsJodi"})
    g.call("now", E_ACTOR, "GetGameTimeSinceCreation", inp={"self": "@gb.Bound"})
    g.call("q", K_MATH, "Add_FloatFloat", inp={"A": "@now.ReturnValue", "B": str(QUIET)}); g.set("sq", "time", cls=P_IHC, inp={"self": "@gh.Hand", "time": "@q.ReturnValue"})
    g.set("sa", "Active", inp={"Active": "true"})
    g.get("gx", "Next"); g.call("due", K_MATH, "Greater_FloatFloat", inp={"A": "@now.ReturnValue", "B": "@gx.Next"}); g.branch("bd", "@due.ReturnValue")
    g.get("giv", "interval", cls=P_IHC); g.link("gh.Hand", "giv.self")
    g.n("iv", "call_self", function="Hand Interval", inp={"ticking": "@tk.ReturnValue", "interval": "@giv.interval"})
    g.call("nx", K_MATH, "Add_FloatFloat", inp={"A": "@now.ReturnValue", "B": "@iv.v"}); g.set("sn", "Next", inp={"Next": "@nx.ReturnValue"})
    g.call("rg", P_CB, "Is Ragdoll ?", inp={"self": "@gb.Bound"}); g.branch("brg", "@rg.yes"); g.n("sc", "call_self", function="Scan")
    g.chain("entry", "bh", "bw", "sj", "sq", "sa", "bd", "sn", "brg"); g.chain("bw:else", "rl"); g.chain("brg:else", "sc")
    return fn("Step", graph=g)


def event_graph():
    g = G()
    # tick: follow the player character (rebind when it changes, e.g. story mode after the shower), then one step
    g.event("tk", E_ACTOR, "ReceiveTick")
    g.call("pp", K_GS, "GetPlayerCharacter", inp={"PlayerIndex": "0"}); g.cast("cp", P_CPB, "@pp.ReturnValue"); g.get("gb", "Bound")
    g.call("ne", K_MATH, "NotEqual_ObjectObject", inp={"A": "@cp.AsCharacter Player Base", "B": "@gb.Bound"}); g.branch("bne", "@ne.ReturnValue")
    g.n("bd", "call_self", function="Bind", inp={"jodi": "@cp.AsCharacter Player Base"}); g.n("st", "call_self", function="Step")
    g.chain("tk", "bne", "bd", "st"); g.chain("bne:else", "st")
    g.event("ep", E_ACTOR, "ReceiveEndPlay"); g.n("rl", "call_self", function="Release"); g.chain("ep", "rl")
    # test entry points (editor Python on the CDO): pure helpers -> Tmp*
    g.custom("tex", "Test Hand Extent", [param("range", "float")])
    g.n("tex_c", "call_self", function="Hand Extent", inp={"range": "@tex.range"}); g.set("tex_s", "TmpVec", inp={"TmpVec": "@tex_c.extent"}); g.chain("tex", "tex_s")
    g.custom("thw", "Test Hand Wanted", [param("on", "bool"), param("ticking", "bool"), param("nohand", "bool")])
    g.n("thw_c", "call_self", function="Hand Wanted", inp={k: "@thw." + k for k in ("on", "ticking", "nohand")}); g.set("thw_s", "TmpBool", inp={"TmpBool": "@thw_c.yes"}); g.chain("thw", "thw_s")
    g.custom("thi", "Test Hand Interval", [param("ticking", "bool"), param("interval", "float")])
    g.n("thi_c", "call_self", function="Hand Interval", inp={k: "@thi." + k for k in ("ticking", "interval")}); g.set("thi_s", "TmpFloat", inp={"TmpFloat": "@thi_c.v"}); g.chain("thi", "thi_s")
    g.custom("tbc", "Test Batch Count", [param("batch", "float")])
    g.n("tbc_c", "call_self", function="Batch Count", inp={"batch": "@tbc.batch"}); g.set("tbc_s", "TmpInt", inp={"TmpInt": "@tbc_c.n"}); g.chain("tbc", "tbc_s")
    g.custom("tpa", "Test Pick Allowed", [param("auto", "bool"), param("flying", "bool"), param("count", "int"), param("max", "int")])
    g.n("tpa_c", "call_self", function="Pick Allowed", inp={k: "@tpa." + k for k in ("auto", "flying", "count", "max")}); g.set("tpa_s", "TmpBool", inp={"TmpBool": "@tpa_c.yes"}); g.chain("tpa", "tpa_s")
    return g


def build():
    return [blueprint(HAND, E_ACTOR,
                      variables=[var("On", "bool"), var("Range", "float"), var("Batch", "float"), var("NoHand", "bool"), var("Bound", "object:" + P_CPB), var("Hand", "object:" + P_IHC),
                                 var("Active", "bool"), var("Next", "float"), var("Count", "int"), var("TmpVec", S_VEC), var("TmpBool", "bool"), var("TmpFloat", "float"), var("TmpInt", "int")],
                      functions=[f_hand_extent(), f_hand_wanted(), f_hand_interval(), f_batch_count(), f_pick_allowed(), f_set_hand(), f_release(), f_bind(), f_pick(), f_scan(), f_step()],
                      event_graph=event_graph())]


if __name__ == "__main__":
    write(os.path.join(os.path.dirname(__file__), "..", "29d_hand.json"), build())
