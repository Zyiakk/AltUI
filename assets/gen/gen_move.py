#!/usr/bin/env python3
"""Generates assets/29_move.json: BP_AltUIMove, Jodi's walk / run speed (docs/specs/2026-10-06-move-speed-design.md).
The game takes her speed from the curve MoveData_Speed of the running animation (Jodi.Update Max Speed) and writes it to
CharacterMovement.MaxWalkSpeed every tick (Update Move Input Vector). This actor ticks after Jodi and before her
CharacterMovement (tick prerequisites both ways) and scales that value; the mesh's GlobalAnimRateScale follows while she
moves on the ground without a montage, so the feet keep their grip. Off, crouching or in the air: factor 1."""
import os, sys; sys.path[:0] = [os.path.dirname(__file__), os.path.join(os.path.dirname(__file__), "..", "anim")]
from bpdsl import *
import anims

MOVE = M + "/BP_AltUIMove"
E_CMC = "/Script/Engine.CharacterMovementComponent"; E_ACTC = "/Script/Engine.ActorComponent"; E_ANIMI = "/Script/Engine.AnimInstance"
INTERP = "8.0"          # FInterpTo speed: about 0.25 s from walk to run factor
RATE_MIN_SPEED = "10.0"  # Speed 2d above which the animation rate follows the factor
RUN_TOGGLE_SPEED = "250.0"   # Jodi.On Input Action Run, RunMode 2: Get Speed > this -> stop running, else start
E_INSET = "/Script/Engine.InputSettings"; S_ACTMAP = "/Script/Engine.InputActionKeyMapping"

# walk / run styles (docs/specs/2026-10-06-move-styles-design.md): child ABPs of Jodi_Anim that swap the loop players. The kit has no
# Jodi_Anim: a stub at the game path carries the two players under the game's node names (the child's cooked CDO addresses them by
# name), stand-in sequences cover the animations the kit lacks. Only the loop is swapped: starting off always plays the game's start
# animations (Move Start picks them in code). A loop needs the game's movement curves: MoveData_Speed (speed), Rotation Speed (Rotate
# Actor turns her with it - without it she does not turn), Forward Moving Alpha (Apply Move Input), MoveData_FootPhase, Enable_LeanLR and
# the L/R sync markers. The game's injured loops (Female_WalkHurt_F, Female_Run_Hurt) lack Rotation Speed - tried 2026-10-06, Jodi could
# not change direction; they come back with copied curves from the animation pipeline (sub-project 3).
J = "/Game/Project/Character/Jodi"; JODI_ANIM = J + "/Jodi_Anim"; SKELETON = J + "/Body/Female_Skeleton"
STYLE_NODES = {"walk": "AnimGraphNode_SequencePlayer_1", "run": "AnimGraphNode_SequencePlayer_4"}   # Female_Walk / Female_Run in Jodi_Anim
WALK_STYLES = [("Normal", None), ("Copy", M + "/Anims/Female_WalkCopy")]   # (key, loop; assets/anim/anims.py); Copy = round trip test of the animation pipeline
RUN_STYLES = [("Normal", None)]
# only styles whose loop this build has (anims.enabled: Copy only with ALTUI_ANIMTEST=1); a saved style
# missing here plays Normal (Style Class / Style Loop: unknown = Normal), and the save keeps it until another one is picked
WALK_STYLES = [(k, p) for k, p in WALK_STYLES if not p or anims.enabled(p.rsplit("/", 1)[1])]
RUN_STYLES = [(k, p) for k, p in RUN_STYLES if not p or anims.enabled(p.rsplit("/", 1)[1])]
STYLE_ABPS = {"%s_%s" % (w, r): M + "/ABP_AltUIStyle_%s_%s" % (w, r) for w, _ in WALK_STYLES for r, _ in RUN_STYLES if (w, r) != ("Normal", "Normal")}


def f_target_factor():
    """Factor the speed is heading for: 1 when off, crouching or in the air, else run / walk percent / 100 (0 = never set = 100)."""
    g = G()
    g.call("pct", K_MATH, "SelectFloat", inp={"A": "@entry.run", "B": "@entry.walk", "bPickA": "@entry.wanna run"})
    g.call("set", K_MATH, "Greater_FloatFloat", inp={"A": "@pct.ReturnValue", "B": "0.0"})
    g.call("p0", K_MATH, "SelectFloat", inp={"A": "@pct.ReturnValue", "B": "100.0", "bPickA": "@set.ReturnValue"})
    g.call("f", K_MATH, "Divide_FloatFloat", inp={"A": "@p0.ReturnValue", "B": "100.0"})
    g.call("off", K_MATH, "Not_PreBool", inp={"A": "@entry.on"})
    g.call("n1", K_MATH, "BooleanOR", inp={"A": "@off.ReturnValue", "B": "@entry.crouch"})
    g.call("n2", K_MATH, "BooleanOR", inp={"A": "@n1.ReturnValue", "B": "@entry.falling"})
    g.call("r", K_MATH, "SelectFloat", inp={"A": "1.0", "B": "@f.ReturnValue", "bPickA": "@n2.ReturnValue"}); g.link("r.ReturnValue", "return.factor")
    return fn("Target Factor", [param("on", "bool"), param("walk", "float"), param("run", "float"), param("wanna run", "bool"), param("crouch", "bool"), param("falling", "bool")],
              [param("factor", "float")], graph=g, pure=True)


def f_rate_target():
    """Animation rate the mesh is heading for: the factor while moving on the ground without a montage, else 1 (attacks, doors, idle keep theirs)."""
    g = G()
    g.call("mv", K_MATH, "Greater_FloatFloat", inp={"A": "@entry.speed", "B": RATE_MIN_SPEED})
    g.call("nm", K_MATH, "Not_PreBool", inp={"A": "@entry.montage"}); g.call("ok", K_MATH, "BooleanAND", inp={"A": "@mv.ReturnValue", "B": "@nm.ReturnValue"})
    g.call("r", K_MATH, "SelectFloat", inp={"A": "@entry.factor", "B": "1.0", "bPickA": "@ok.ReturnValue"}); g.link("r.ReturnValue", "return.rate")
    return fn("Rate Target", [param("factor", "float"), param("speed", "float"), param("montage", "bool")], [param("rate", "float")], graph=g, pure=True)


def f_run_fix():
    """Run key in RunMode 2: the game decided by the scaled speed (> 250 -> stop running, else start); the decision it would make
    without the factor. 0 = the same (nothing to do), 1 = start running, 2 = stop running."""
    g = G()
    g.call("gs", K_MATH, "Greater_FloatFloat", inp={"A": "@entry.speed", "B": RUN_TOGGLE_SPEED})
    g.call("fm", K_MATH, "FMax", inp={"A": "@entry.factor", "B": "0.01"}); g.call("un", K_MATH, "Divide_FloatFloat", inp={"A": "@entry.speed", "B": "@fm.ReturnValue"})
    g.call("gu", K_MATH, "Greater_FloatFloat", inp={"A": "@un.ReturnValue", "B": RUN_TOGGLE_SPEED})
    g.call("same", K_MATH, "EqualEqual_BoolBool", inp={"A": "@gs.ReturnValue", "B": "@gu.ReturnValue"})
    g.call("act", K_MATH, "SelectInt", inp={"A": "2", "B": "1", "bPickA": "@gu.ReturnValue"})
    g.call("r", K_MATH, "SelectInt", inp={"A": "0", "B": "@act.ReturnValue", "bPickA": "@same.ReturnValue"}); g.link("r.ReturnValue", "return.action")
    return fn("Run Fix", [param("speed", "float"), param("factor", "float")], [param("action", "int")], graph=g, pure=True)


def f_check_run_key():
    """After the game handled a press of the run key (any key of the action "Run"; seen once per press, the frame the controller processed it
    or the next): in RunMode 2 with Jodi taking input, redo its speed decision without the factor (Run Fix)."""
    g = G(); g.get("gb", "Bound"); g.cast("cj", P_JODI, "@gb.Bound")
    g.call("ie", P_JODI, "Is Input Enabled ?", inp={"self": "@cj.AsJodi"})
    g.get("gst", "Settings", cls=P_JODI); g.link("cj.AsJodi", "gst.self"); g.call("vs", K_SYS, "IsValid", inp={"Object": "@gst.Settings"})
    g.get("grm", "RunMode", cls=P_SETTINGS_SAVE); g.link("gst.Settings", "grm.self"); g.call("m2", K_MATH, "EqualEqual_IntInt", inp={"A": "@grm.RunMode", "B": "2"})
    g.call("ok1", K_MATH, "BooleanAND", inp={"A": "@ie.yes", "B": "@vs.ReturnValue"}); g.branch("bok", "@ok1.ReturnValue"); g.branch("bm2", "@m2.ReturnValue")
    g.call("pc", K_GS, "GetPlayerController", inp={"PlayerIndex": "0"}); g.call("ins", E_INSET, "GetInputSettings")
    g.call("am", E_INSET, "GetActionMappingByName", inp={"self": "@ins.ReturnValue", "InActionName": "Run"}); g.foreach("fk", "@am.OutMappings")
    g.brk("bk", S_ACTMAP, "@fk.Array Element"); g.call("jp", E_PC, "WasInputKeyJustPressed", inp={"self": "@pc.ReturnValue", "Key": "@bk.Key"}); g.branch("bjp", "@jp.ReturnValue")
    g.get("gsp", "Speed 2d", cls=P_CB); g.link("gb.Bound", "gsp.self"); g.get("gf", "Factor")
    g.n("rf", "call_self", function="Run Fix", inp={"speed": "@gsp.Speed 2d", "factor": "@gf.Factor"}); g.set("sa", "RunAction", inp={"RunAction": "@rf.action"})
    g.call("e1", K_MATH, "EqualEqual_IntInt", inp={"A": "@sa.Output_Get", "B": "1"}); g.branch("b1", "@e1.ReturnValue")
    g.call("e2", K_MATH, "EqualEqual_IntInt", inp={"A": "@sa.Output_Get", "B": "2"}); g.branch("b2", "@e2.ReturnValue")
    g.call("wr", P_JODI, "Wanna Running", inp={"self": "@cj.AsJodi"}); g.call("sr", P_CPB, "Change Wanna Run", inp={"self": "@gb.Bound", "run": "false"})
    g.chain("entry", "bok", "bm2", "fk"); g.chain("fk", "bjp", "sa", "b1", "wr"); g.chain("b1:else", "b2", "sr")
    return fn("Check Run Key", graph=g)


def f_style_class():
    """Anim class for a walk / run style (None = Normal): the child ABP of the combination, Jodi_Anim for Normal / Normal."""
    g = G()
    if not STYLE_ABPS:   # no styles yet: always Jodi_Anim
        g.call("s0", K_MATH, "SelectClass", inp={"A": JODI_ANIM, "B": JODI_ANIM, "bSelectA": "true"}); g.link("s0.ReturnValue", "return.cls")
        return fn("Style Class", [param("walk", "name"), param("run", "name")], [param("cls", "class:/Script/CoreUObject.Object")], graph=g, pure=True)
    # each side to a known style key, anything else (None, a removed style still in the settings) = Normal on that side only
    for k, styles in (("walk", WALK_STYLES), ("run", RUN_STYLES)):
        prev = None
        if len(styles) > 1: g.call(k + "s", K_STR, "Conv_NameToString", inp={"InName": "@entry." + k})
        for i, (key, _) in enumerate(styles[1:]):
            g.call("%se%d" % (k, i), K_STR, "EqualEqual_StriStri", inp={"A": "@%ss.ReturnValue" % k, "B": key})
            g.call("%sk%d" % (k, i), K_MATH, "SelectString", inp={"A": key, "B": prev or "Normal", "bPickA": "@%se%d.ReturnValue" % (k, i)}); prev = "@%sk%d.ReturnValue" % (k, i)
        if prev is None: g.call(k + "k", K_STR, "Concat_StrStr", inp={"A": "Normal", "B": ""}); prev = "@%sk.ReturnValue" % k
        g.call(k + "kk", K_STR, "Concat_StrStr", inp={"A": prev, "B": ""})   # one name for the key below
    g.call("k1", K_STR, "Concat_StrStr", inp={"A": "@walkkk.ReturnValue", "B": "_"}); g.call("key", K_STR, "Concat_StrStr", inp={"A": "@k1.ReturnValue", "B": "@runkk.ReturnValue"})
    prev = None
    for i, (key, path) in enumerate(sorted(STYLE_ABPS.items())):
        g.call("e%d" % i, K_STR, "EqualEqual_StriStri", inp={"A": "@key.ReturnValue", "B": key})   # ignoring case: an FName keeps the spelling of its first use ("Hurt" came back as "hurt" in the game)
        g.call("s%d" % i, K_MATH, "SelectClass", inp={"A": path, "B": prev or JODI_ANIM, "bSelectA": "@e%d.ReturnValue" % i}); prev = "@s%d.ReturnValue" % i
    g.link(prev[1:], "return.cls")
    return fn("Style Class", [param("walk", "name"), param("run", "name")], [param("cls", "class:/Script/CoreUObject.Object")], graph=g, pure=True)


def f_style_loop():
    """The style's loop animation for the current gait (None on a Normal side or for an unknown style) - what Apply Start Loop puts
    into Jodi_Anim's 'Anim Move Start'."""
    g = G(); outs = {}
    for k, styles in (("walk", WALK_STYLES), ("run", RUN_STYLES)):
        prev = None
        extra = [(key, path) for key, path in styles[1:] if path]
        if extra: g.call(k + "s", K_STR, "Conv_NameToString", inp={"InName": "@entry." + k})
        for i, (key, path) in enumerate(extra):
            g.call("%se%d" % (k, i), K_STR, "EqualEqual_StriStri", inp={"A": "@%ss.ReturnValue" % k, "B": key})
            if prev is None: g.call("%sn%d" % (k, i), K_MATH, "SelectObject", inp={"A": path, "B": "None", "bSelectA": "@%se%d.ReturnValue" % (k, i)})
            else: g.call("%sn%d" % (k, i), K_MATH, "SelectObject", inp={"A": path, "B": prev, "bSelectA": "@%se%d.ReturnValue" % (k, i)})
            prev = "@%sn%d.ReturnValue" % (k, i)
        outs[k] = prev
    if outs["walk"] and outs["run"]: g.call("r", K_MATH, "SelectObject", inp={"A": outs["run"], "B": outs["walk"], "bSelectA": "@entry.running"}); res = "@r.ReturnValue"
    elif outs["walk"] or outs["run"]:
        one = outs["walk"] or outs["run"]; g.call("r", K_MATH, "SelectObject", inp={"A": "None" if outs["walk"] else one, "B": one if outs["walk"] else "None", "bSelectA": "@entry.running"}); res = "@r.ReturnValue"
    else: g.call("r", K_MATH, "SelectObject", inp={"A": "None", "B": "None", "bSelectA": "@entry.running"}); res = "@r.ReturnValue"
    g.link(res[1:], "return.loop")
    return fn("Style Loop", [param("walk", "name"), param("run", "name"), param("running", "bool")], [param("loop", "object:/Script/CoreUObject.Object")], graph=g, pure=True)


def f_apply_start_loop():
    """While a style ABP runs: the game's start / walk <-> run animation in Jodi_Anim's 'Anim Move Start' (2 - 2.6 s of the normal walk
    before the loop) is replaced by the style's loop for the current gait, so the style shows from the first step. Stops stay the game's."""
    g = G(); g.get("gb", "Bound"); g.get("gm", "Mesh", cls=E_CHARACTER); g.link("gb.Bound", "gm.self")
    g.call("ai", E_SKELMESHCOMP, "GetAnimInstance", inp={"self": "@gm.Mesh"}); g.cast("ja", JODI_ANIM, "@ai.ReturnValue")
    g.call("vja", K_SYS, "IsValid", inp={"Object": "@ja.AsJodi Anim"})
    g.get("gws", "WalkStyle"); g.get("grs", "RunStyle"); g.call("wr", P_CPB, "Is Wanna Run ?", inp={"self": "@gb.Bound"})
    g.n("sl", "call_self", function="Style Loop", inp={"walk": "@gws.WalkStyle", "run": "@grs.RunStyle", "running": "@wr.Yes"})
    g.cast("cs", "/Script/Engine.AnimSequence", "@sl.loop"); g.call("vl", K_SYS, "IsValid", inp={"Object": "@cs.AsAnim Sequence"})
    g.get("gms", "Anim Move Start", cls=JODI_ANIM); g.link("ja.AsJodi Anim", "gms.self"); g.call("vms", K_SYS, "IsValid", inp={"Object": "@gms.Anim Move Start"})
    g.call("ne", K_MATH, "NotEqual_ObjectObject", inp={"A": "@gms.Anim Move Start", "B": "@cs.AsAnim Sequence"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@vja.ReturnValue", "B": "@vl.ReturnValue"}); g.call("a2", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@vms.ReturnValue"})
    g.call("a3", K_MATH, "BooleanAND", inp={"A": "@a2.ReturnValue", "B": "@ne.ReturnValue"}); g.branch("b", "@a3.ReturnValue")
    g.set("sms", "Anim Move Start", cls=JODI_ANIM, inp={"self": "@ja.AsJodi Anim", "Anim Move Start": "@cs.AsAnim Sequence"})
    g.chain("entry", "b", "sms")
    return fn("Apply Start Loop", graph=g)


def f_set_style():
    g = G(); g.set("sw", "WalkStyle", inp={"WalkStyle": "@entry.walk"}); g.set("sr", "RunStyle", inp={"RunStyle": "@entry.run"}); g.chain("entry", "sw", "sr")
    return fn("Set Style", [param("walk", "name"), param("run", "name")], graph=g)


def f_apply_style():
    """Puts the anim class of the chosen style on the bound Jodi - only over Jodi_Anim or a child of it (an ABP another mod put there stays),
    and only without a montage (the switch restarts the anim instance). The game sets Anim Blueprint once in Begin Play Ex: reset it.
    Called every tick: if the game puts its class back, the next tick switches again."""
    g = G(); g.get("gb", "Bound"); g.get("gm", "Mesh", cls=E_CHARACTER); g.link("gb.Bound", "gm.self")
    g.call("ai", E_SKELMESHCOMP, "GetAnimInstance", inp={"self": "@gm.Mesh"}); g.call("vai", K_SYS, "IsValid", inp={"Object": "@ai.ReturnValue"})
    g.call("oc", K_GS, "GetObjectClass", inp={"Object": "@ai.ReturnValue"})
    g.call("jc", K_MATH, "SelectClass", inp={"A": JODI_ANIM, "B": JODI_ANIM, "bSelectA": "true"})
    g.call("ours", K_MATH, "ClassIsChildOf", inp={"TestClass": "@oc.ReturnValue", "ParentClass": "@jc.ReturnValue"})
    g.get("gws", "WalkStyle"); g.get("grs", "RunStyle"); g.n("sc", "call_self", function="Style Class", inp={"walk": "@gws.WalkStyle", "run": "@grs.RunStyle"})
    g.call("ne", K_MATH, "NotEqual_ClassClass", inp={"A": "@oc.ReturnValue", "B": "@sc.cls"})
    g.call("mp", E_ANIMI, "IsAnyMontagePlaying", inp={"self": "@ai.ReturnValue"}); g.call("nmp", K_MATH, "Not_PreBool", inp={"A": "@mp.ReturnValue"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@vai.ReturnValue", "B": "@ours.ReturnValue"}); g.call("a2", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@ne.ReturnValue"})
    g.call("a3", K_MATH, "BooleanAND", inp={"A": "@a2.ReturnValue", "B": "@nmp.ReturnValue"}); g.branch("bgo", "@a3.ReturnValue")
    g.call("sac", E_SKELMESHCOMP, "SetAnimClass", inp={"self": "@gm.Mesh", "NewClass": "@sc.cls"})
    g.call("ai2", E_SKELMESHCOMP, "GetAnimInstance", inp={"self": "@gm.Mesh"})
    g.set("sab", "Anim Blueprint", cls=P_CB, inp={"self": "@gb.Bound", "Anim Blueprint": "@ai2.ReturnValue"})
    g.chain("entry", "bgo", "sac", "sab")
    return fn("Apply Style", graph=g)


def f_bind():
    """Bind to a (new) Jodi: the old one loses the prerequisites and gets rate 1 back; order Jodi -> this -> her CharacterMovement."""
    g = G(); g.self_("me")
    g.get("gb", "Bound"); g.call("vb", K_SYS, "IsValid", inp={"Object": "@gb.Bound"}); g.branch("bb", "@vb.ReturnValue")
    g.call("ra", E_ACTOR, "RemoveTickPrerequisiteActor", inp={"self": "@me.self", "PrerequisiteActor": "@gb.Bound"})
    g.get("gcm0", "CharacterMovement", cls=E_CHARACTER); g.link("gb.Bound", "gcm0.self")
    g.call("rc", E_ACTC, "RemoveTickPrerequisiteActor", inp={"self": "@gcm0.CharacterMovement", "PrerequisiteActor": "@me.self"})
    g.get("gm0", "Mesh", cls=E_CHARACTER); g.link("gb.Bound", "gm0.self")
    g.set("r1", "GlobalAnimRateScale", cls=E_SKELMESHCOMP, inp={"self": "@gm0.Mesh", "GlobalAnimRateScale": "1.0"})
    g.set("sb", "Bound", inp={"Bound": "@entry.jodi"}); g.call("vn", K_SYS, "IsValid", inp={"Object": "@entry.jodi"}); g.branch("bn", "@vn.ReturnValue")
    g.call("aa", E_ACTOR, "AddTickPrerequisiteActor", inp={"self": "@me.self", "PrerequisiteActor": "@entry.jodi"})
    g.get("gcm1", "CharacterMovement", cls=E_CHARACTER); g.link("entry.jodi", "gcm1.self")
    g.call("ac", E_ACTC, "AddTickPrerequisiteActor", inp={"self": "@gcm1.CharacterMovement", "PrerequisiteActor": "@me.self"})
    g.set("sf", "Factor", inp={"Factor": "1.0"}); g.set("sr", "Rate", inp={"Rate": "1.0"}); g.set("sl", "LastSet", inp={"LastSet": "-1.0"}); g.set("si", "Idle", inp={"Idle": "false"})
    g.chain("entry", "bb", "ra", "rc", "r1", "sb"); g.chain("bb:else", "sb"); g.chain("sb", "sf", "sr", "sl", "si", "bn", "aa", "ac")
    return fn("Bind", [param("jodi", "object:" + P_CPB)], graph=g)


def f_set_speeds():
    g = G(); g.set("so", "On", inp={"On": "@entry.on"}); g.set("sw", "Walk", inp={"Walk": "@entry.walk"}); g.set("sr", "Run", inp={"Run": "@entry.run"})
    g.set("si", "Idle", inp={"Idle": "false"}); g.chain("entry", "so", "sw", "sr", "si")
    return fn("Set Speeds", [param("on", "bool"), param("walk", "float"), param("run", "float")], graph=g)


def f_apply():
    """One tick on the bound Jodi (dt). MaxWalkSpeed: when Jodi did not write it this frame (input off: her tick skips Update
    Max Speed) it still holds our last value - then scale the remembered base again instead of compounding."""
    g = G(); g.get("gb", "Bound")
    g.call("wr", P_CPB, "Is Wanna Run ?", inp={"self": "@gb.Bound"}); g.call("cr", P_CB, "Is Crouching", inp={"self": "@gb.Bound"})
    g.get("gcm", "CharacterMovement", cls=E_CHARACTER); g.link("gb.Bound", "gcm.self"); g.call("fa", E_CMC, "IsFalling", inp={"self": "@gcm.CharacterMovement"})
    g.get("go", "On"); g.get("gw", "Walk"); g.get("gr", "Run")
    g.n("tf", "call_self", function="Target Factor", inp={"on": "@go.On", "walk": "@gw.Walk", "run": "@gr.Run", "wanna run": "@wr.Yes", "crouch": "@cr.yes", "falling": "@fa.ReturnValue"})
    g.get("gf", "Factor"); g.call("fi", K_MATH, "FInterpTo", inp={"Current": "@gf.Factor", "Target": "@tf.factor", "DeltaTime": "@entry.dt", "InterpSpeed": INTERP})
    g.set("sf", "Factor", inp={"Factor": "@fi.ReturnValue"})
    # idle: off and both back at 1 -> rate 1 once, then no more writes until Set Speeds
    g.get("gr1", "Rate"); g.call("f1", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@sf.Output_Get", "B": "1.0", "ErrorTolerance": "0.001"})
    g.call("r1", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gr1.Rate", "B": "1.0", "ErrorTolerance": "0.001"})
    g.call("noff", K_MATH, "Not_PreBool", inp={"A": "@go.On"}); g.call("i1", K_MATH, "BooleanAND", inp={"A": "@f1.ReturnValue", "B": "@r1.ReturnValue"})
    g.call("i2", K_MATH, "BooleanAND", inp={"A": "@i1.ReturnValue", "B": "@noff.ReturnValue"}); g.branch("bi", "@i2.ReturnValue")
    g.get("gm", "Mesh", cls=E_CHARACTER); g.link("gb.Bound", "gm.self")
    g.set("rs1", "GlobalAnimRateScale", cls=E_SKELMESHCOMP, inp={"self": "@gm.Mesh", "GlobalAnimRateScale": "1.0"}); g.set("si", "Idle", inp={"Idle": "true"})
    # speed: base = what Jodi wrote, or the remembered base when the value is still ours
    g.get("gmw", "MaxWalkSpeed", cls=E_CMC); g.link("gcm.CharacterMovement", "gmw.self"); g.get("gls", "LastSet"); g.get("glb", "LastBase")
    g.call("ours", K_MATH, "NearlyEqual_FloatFloat", inp={"A": "@gmw.MaxWalkSpeed", "B": "@gls.LastSet", "ErrorTolerance": "0.01"})
    g.call("base", K_MATH, "SelectFloat", inp={"A": "@glb.LastBase", "B": "@gmw.MaxWalkSpeed", "bPickA": "@ours.ReturnValue"}); g.set("slb", "LastBase", inp={"LastBase": "@base.ReturnValue"})
    g.call("mul", K_MATH, "Multiply_FloatFloat", inp={"A": "@slb.Output_Get", "B": "@sf.Output_Get"})
    g.set("smw", "MaxWalkSpeed", cls=E_CMC, inp={"self": "@gcm.CharacterMovement", "MaxWalkSpeed": "@mul.ReturnValue"}); g.set("sls", "LastSet", inp={"LastSet": "@mul.ReturnValue"})
    # animation rate
    g.call("ai", E_SKELMESHCOMP, "GetAnimInstance", inp={"self": "@gm.Mesh"}); g.call("mp", E_ANIMI, "IsAnyMontagePlaying", inp={"self": "@ai.ReturnValue"})
    g.get("gsp", "Speed 2d", cls=P_CB); g.link("gb.Bound", "gsp.self")
    g.n("rt", "call_self", function="Rate Target", inp={"factor": "@sf.Output_Get", "speed": "@gsp.Speed 2d", "montage": "@mp.ReturnValue"})
    g.get("gr2", "Rate"); g.call("ri", K_MATH, "FInterpTo", inp={"Current": "@gr2.Rate", "Target": "@rt.rate", "DeltaTime": "@entry.dt", "InterpSpeed": INTERP})
    g.set("sr", "Rate", inp={"Rate": "@ri.ReturnValue"}); g.set("rs2", "GlobalAnimRateScale", cls=E_SKELMESHCOMP, inp={"self": "@gm.Mesh", "GlobalAnimRateScale": "@sr.Output_Get"})
    g.n("crk", "call_self", function="Check Run Key")
    g.chain("entry", "sf", "bi", "rs1", "si"); g.chain("bi:else", "slb", "smw", "sls", "sr", "rs2", "crk")
    return fn("Apply", [param("dt", "float")], graph=g)


def event_graph():
    g = G()
    # tick: follow the player pawn (rebind when it changes), then one step unless idle
    g.event("tk", E_ACTOR, "ReceiveTick")
    g.call("pp", K_GS, "GetPlayerCharacter", inp={"PlayerIndex": "0"}); g.cast("cp", P_CPB, "@pp.ReturnValue"); g.get("gb", "Bound")   # not a player character (main menu): None
    g.call("ne", K_MATH, "NotEqual_ObjectObject", inp={"A": "@cp.AsCharacter Player Base", "B": "@gb.Bound"}); g.branch("bne", "@ne.ReturnValue")
    g.n("bd", "call_self", function="Bind", inp={"jodi": "@cp.AsCharacter Player Base"})
    g.get("gb2", "Bound"); g.call("vb", K_SYS, "IsValid", inp={"Object": "@gb2.Bound"}); g.get("gi", "Idle"); g.call("ni", K_MATH, "Not_PreBool", inp={"A": "@gi.Idle"})
    g.call("go", K_MATH, "BooleanAND", inp={"A": "@vb.ReturnValue", "B": "@ni.ReturnValue"}); g.branch("bgo", "@go.ReturnValue")
    g.n("ap", "call_self", function="Apply", inp={"dt": "@tk.DeltaSeconds"})
    g.get("gb3", "Bound"); g.call("vb3", K_SYS, "IsValid", inp={"Object": "@gb3.Bound"}); g.branch("bvs", "@vb3.ReturnValue")
    g.n("aps", "call_self", function="Apply Style")   # every tick, also while the speed part is idle
    g.n("asl", "call_self", function="Apply Start Loop")
    g.chain("tk", "bne", "bd", "bvs", "aps", "asl", "bgo", "ap"); g.chain("bne:else", "bvs"); g.chain("bvs:else", "bgo")
    # test entry points (editor Python on the CDO): pure helpers -> TmpFloat
    g.custom("ttf", "Test Target Factor", [param("on", "bool"), param("walk", "float"), param("run", "float"), param("wanna run", "bool"), param("crouch", "bool"), param("falling", "bool")])
    g.n("ttf_c", "call_self", function="Target Factor", inp={k: "@ttf." + k for k in ("on", "walk", "run", "wanna run", "crouch", "falling")})
    g.set("ttf_s", "TmpFloat", inp={"TmpFloat": "@ttf_c.factor"}); g.chain("ttf", "ttf_s")
    g.custom("trt", "Test Rate Target", [param("factor", "float"), param("speed", "float"), param("montage", "bool")])
    g.n("trt_c", "call_self", function="Rate Target", inp={k: "@trt." + k for k in ("factor", "speed", "montage")})
    g.set("trt_s", "TmpFloat", inp={"TmpFloat": "@trt_c.rate"}); g.chain("trt", "trt_s")
    g.custom("tsc", "Test Style Class", [param("walk", "name"), param("run", "name")])
    g.n("tsc_c", "call_self", function="Style Class", inp={"walk": "@tsc.walk", "run": "@tsc.run"}); g.set("tsc_s", "TmpClass", inp={"TmpClass": "@tsc_c.cls"}); g.chain("tsc", "tsc_s")
    g.custom("tslp", "Test Style Loop", [param("walk", "name"), param("run", "name"), param("running", "bool")])
    g.n("tslp_c", "call_self", function="Style Loop", inp={"walk": "@tslp.walk", "run": "@tslp.run", "running": "@tslp.running"}); g.set("tslp_s", "TmpObj", inp={"TmpObj": "@tslp_c.loop"}); g.chain("tslp", "tslp_s")
    g.custom("trf", "Test Run Fix", [param("speed", "float"), param("factor", "float")])
    g.n("trf_c", "call_self", function="Run Fix", inp={"speed": "@trf.speed", "factor": "@trf.factor"}); g.set("trf_s", "TmpInt", inp={"TmpInt": "@trf_c.action"}); g.chain("trf", "trf_s")
    return g


def style_assets():
    """Stand-in sequences, the Jodi_Anim stub and one child ABP per style combination (Normal / Normal is Jodi_Anim itself)."""
    seqs = [J + "/Animations/Female_Walk", J + "/Animations/Female_Run"] + [a for _, a in WALK_STYLES + RUN_STYLES if a and a.startswith(J)]   # stand-ins for game animations only
    out = [animsequence_stub(a, SKELETON) for a in seqs]
    out.append(animstub(JODI_ANIM, SKELETON, [(STYLE_NODES["walk"], seqs[0]), (STYLE_NODES["run"], seqs[1])]))
    # Move Start / Move Change write the game's start and walk <-> run animations (2 - 2.6 s) into this variable; BP_AltUIMove puts the
    # style's loop there so a style shows from the first step
    out.append(blueprint(JODI_ANIM, mode="augment", variables=[var("Anim Move Start", "object:/Script/Engine.AnimSequence")]))
    walk, run = dict(WALK_STYLES), dict(RUN_STYLES)
    for key, path in STYLE_ABPS.items():
        w, r = key.split("_"); ov = {}
        if walk[w]: ov[STYLE_NODES["walk"]] = walk[w]
        if run[r]: ov[STYLE_NODES["run"]] = run[r]
        out.append(animchild(path, JODI_ANIM, SKELETON, ov))
    return out


def build():
    return style_assets() + [blueprint(MOVE, E_ACTOR,
                      variables=[var("On", "bool"), var("Walk", "float"), var("Run", "float"), var("Bound", "object:" + P_CPB), var("Factor", "float", default="1.0"),
                                 var("Rate", "float", default="1.0"), var("LastSet", "float", default="-1.0"), var("LastBase", "float"), var("Idle", "bool"), var("TmpFloat", "float"), var("TmpInt", "int"), var("RunAction", "int"), var("WalkStyle", "name"), var("RunStyle", "name"), var("TmpClass", "class:/Script/CoreUObject.Object"), var("TmpObj", "object:/Script/CoreUObject.Object")],
                      functions=[f_target_factor(), f_rate_target(), f_run_fix(), f_check_run_key(), f_style_class(), f_style_loop(), f_apply_start_loop(), f_set_style(), f_apply_style(), f_bind(), f_set_speeds(), f_apply()], event_graph=event_graph())]


if __name__ == "__main__":
    write(os.path.join(os.path.dirname(__file__), "..", "29_move.json"), build())
