"""Generates assets/20_hook.json: replacement PlayerCameraManager (override pak in ~mods).
Spawns the inventory manager at startup and, while the panel is open, shifts the camera sideways (Jodi centred in the free area)."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *

HOOK = "/Game/Project/Classes/TKA_PlayerCameraManager"
MGR = M + "/BP_AltUIManager"
E_PCM = "/Script/Engine.PlayerCameraManager"; FOV_SCALE = 0.8; E_CAMC = "/Script/Engine.CameraComponent"; S_MVI = "/Script/Engine.MinimalViewInfo"


def event_graph():
    g = G()
    g.event("bp", E_ACTOR, "ReceiveBeginPlay"); g.self_("me")
    g.call("tm", K_SYS, "K2_SetTimer", inp={"Object": "@me.self", "FunctionName": "TryInit", "Time": "0.5", "bLooping": "true"})
    g.custom("ev", "TryInit"); g.get("gsp", "Spawned"); g.branch("br", "@gsp.Spawned")
    g.call("pc", E_PCM, "GetOwningPlayerController"); g.call("pawn", E_CTRL, "K2_GetPawn", inp={"self": "@pc.ReturnValue"})
    g.cast("cj", P_JODI, "@pawn.ReturnValue", pure=False, miss="ignore")   # no Jodi yet (loading, main menu): the timer retries
    g.call("ld", K_SYS, "LoadClassAsset_Blocking", inp={"AssetClass": MGR + ".BP_AltUIManager_C"})
    g.n("cc", "class_cast", pure=True, cls=E_ACTOR, inp={"Class": "@ld.ReturnValue"})
    g.call("iv", K_SYS, "IsValidClass", inp={"Class": "@cc.AsActor"}); g.branch("br2", "@iv.ReturnValue")
    g.call("tr", K_MATH, "MakeTransform", inp={"Scale": "1,1,1"})
    g.n("sp", "spawn", inp={"SpawnTransform": "@tr.ReturnValue", "Class": "@cc.AsActor", "Owner": "@pc.ReturnValue"})
    g.set("ssp", "Spawned", inp={"Spawned": "true"}); g.self_("me2"); g.call("ct", K_SYS, "K2_ClearTimer", inp={"Object": "@me2.self", "FunctionName": "TryInit"})
    # mod pak missing (only the hook pak installed): the class never appears -> stop the timer instead of a blocking load every 0.5 s forever
    g.self_("me3"); g.call("ct2", K_SYS, "K2_ClearTimer", inp={"Object": "@me3.self", "FunctionName": "TryInit"})
    g.chain("bp", "tm"); g.chain("ev", "br"); g.chain("br:else", "cj", "ld", "br2", "sp", "ssp", "ct"); g.chain("br2:else", "ct2")
    return g


def f_update_camera():
    """BlueprintUpdateCamera: with ViewShift > 0 offset the camera by d*tan(FOV/2)*k to the right (Jodi moves left)."""
    g = G()
    g.get("gvs", "ViewShift")   # set by the inventory manager (no hard reference to the mod pak)
    g.call("gt0", K_MATH, "Greater_FloatFloat", inp={"A": "@gvs.ViewShift", "B": "0.0"}); g.branch("bk", "@gt0.ReturnValue")
    # active camera component of the view target (like Pawn::CalcCamera: first active CameraComponent)
    g.call("cams", E_ACTOR, "K2_GetComponentsByClass", inp={"self": "@entry.CameraTarget", "ComponentClass": E_CAMC})
    g.set("c0", "Cam", inp={"Cam": "None"}); g.foreach("fe", "@cams.ReturnValue"); g.cast("cc", E_CAMC, "@fe.Array Element")
    g.call("act", "/Script/Engine.ActorComponent", "IsActive", inp={"self": "@cc.AsCamera Component"})
    g.get("gc0", "Cam"); g.call("cv0", K_SYS, "IsValid", inp={"Object": "@gc0.Cam"}); g.call("ncv", K_MATH, "Not_PreBool", inp={"A": "@cv0.ReturnValue"})
    g.call("pick", K_MATH, "BooleanAND", inp={"A": "@act.ReturnValue", "B": "@ncv.ReturnValue"}); g.branch("bp", "@pick.ReturnValue")
    g.set("sc", "Cam", inp={"Cam": "@cc.AsCamera Component"})
    g.get("gc", "Cam"); g.call("cv", K_SYS, "IsValid", inp={"Object": "@gc.Cam"}); g.branch("bc", "@cv.ReturnValue")
    g.get("gc2", "Cam"); g.call("gv", E_CAMC, "GetCameraView", inp={"self": "@gc2.Cam", "DeltaTime": "0.0"}); g.brk("bm", S_MVI, "@gv.DesiredView")
    # focus (camera follows slot/face): ease towards target height and zoom; off -> 0 / 1
    g.call("dt", K_GS, "GetWorldDeltaSeconds"); g.get("gfo", "FocusOn"); g.get("gfz", "FocusZ"); g.get("gfm", "FocusZoom")
    g.call("tz", K_MATH, "SelectFloat", inp={"A": "@gfz.FocusZ", "B": "0.0", "bPickA": "@gfo.FocusOn"}); g.call("tm", K_MATH, "SelectFloat", inp={"A": "@gfm.FocusZoom", "B": "1.0", "bPickA": "@gfo.FocusOn"})
    g.get("gcz", "CurZ"); g.call("iz", K_MATH, "FInterpTo", inp={"Current": "@gcz.CurZ", "Target": "@tz.ReturnValue", "DeltaTime": "@dt.ReturnValue", "InterpSpeed": "4.0"}); g.set("scz", "CurZ", inp={"CurZ": "@iz.ReturnValue"})
    g.get("gcm", "CurZoom"); g.call("im", K_MATH, "FInterpTo", inp={"Current": "@gcm.CurZoom", "Target": "@tm.ReturnValue", "DeltaTime": "@dt.ReturnValue", "InterpSpeed": "4.0"}); g.set("scm", "CurZoom", inp={"CurZoom": "@im.ReturnValue"})
    g.call("aloc0", E_ACTOR, "K2_GetActorLocation", inp={"self": "@entry.CameraTarget"}); g.get("gcz2", "CurZ")
    g.call("zv", K_MATH, "MakeVector", inp={"X": "0.0", "Y": "0.0", "Z": "@gcz2.CurZ"}); g.call("aloc", K_MATH, "Add_VectorVector", inp={"A": "@aloc0.ReturnValue", "B": "@zv.ReturnValue"})
    # depth along the view axis (not euclidean: the third-person camera sits higher than Jodi's centre)
    g.call("fwd0", K_MATH, "GetForwardVector", inp={"InRot": "@bm.Rotation"})
    g.call("dvec", K_MATH, "Subtract_VectorVector", inp={"A": "@aloc.ReturnValue", "B": "@bm.Location"})
    g.call("dist", K_MATH, "Dot_VectorVector", inp={"A": "@dvec.ReturnValue", "B": "@fwd0.ReturnValue"})
    # FOV of the camera component (the game's base FOV), narrowed by FOV_SCALE; camera moved back so Jodi stays the same size
    g.call("half", K_MATH, "Divide_FloatFloat", inp={"A": "@bm.FOV", "B": "2.0"}); g.call("tan", K_MATH, "DegTan", inp={"A": "@half.ReturnValue"})
    g.get("gfs", "FovScale"); g.call("nfov", K_MATH, "Multiply_FloatFloat", inp={"A": "@bm.FOV", "B": "@gfs.FovScale"})
    g.call("nhalf", K_MATH, "Divide_FloatFloat", inp={"A": "@nfov.ReturnValue", "B": "2.0"}); g.call("ntan", K_MATH, "DegTan", inp={"A": "@nhalf.ReturnValue"})
    g.call("halfw", K_MATH, "Multiply_FloatFloat", inp={"A": "@dist.ReturnValue", "B": "@tan.ReturnValue"})        # half image width at Jodi's distance
    g.call("ndist0", K_MATH, "Divide_FloatFloat", inp={"A": "@halfw.ReturnValue", "B": "@ntan.ReturnValue"})       # new distance with the narrower FOV (same image size)
    g.get("gds", "DistScale"); g.call("ndist1", K_MATH, "Multiply_FloatFloat", inp={"A": "@ndist0.ReturnValue", "B": "@gds.DistScale"})
    g.get("gcm2", "CurZoom"); g.call("ndist", K_MATH, "Multiply_FloatFloat", inp={"A": "@ndist1.ReturnValue", "B": "@gcm2.CurZoom"})
    g.call("back", K_MATH, "Subtract_FloatFloat", inp={"A": "@ndist.ReturnValue", "B": "@dist.ReturnValue"})
    g.call("fwd", K_MATH, "GetForwardVector", inp={"InRot": "@bm.Rotation"}); g.call("boff", K_MATH, "Multiply_VectorFloat", inp={"A": "@fwd.ReturnValue", "B": "@back.ReturnValue"})
    g.call("nhalfw", K_MATH, "Multiply_FloatFloat", inp={"A": "@ndist.ReturnValue", "B": "@ntan.ReturnValue"})     # half image width at Jodi's (new) distance
    # closed-loop lateral offset: compare Jodi's actual screen position (ProjectWorldToScreen of the last rendered view) with the
    # target NDC x = -k and track the offset (gain 0.6). Initial value analytic: lateral + k * half image width.
    g.call("right", K_MATH, "GetRightVector", inp={"InRot": "@bm.Rotation"})
    g.call("lat", K_MATH, "Dot_VectorVector", inp={"A": "@dvec.ReturnValue", "B": "@right.ReturnValue"})
    g.call("m1", K_MATH, "Multiply_FloatFloat", inp={"A": "@nhalfw.ReturnValue", "B": "@gvs.ViewShift"})
    g.call("m0", K_MATH, "Add_FloatFloat", inp={"A": "@lat.ReturnValue", "B": "@m1.ReturnValue"})
    g.get("gsi", "ShiftInit"); g.branch("bsi", "@gsi.ShiftInit")
    g.set("ss0", "ShiftWorld", inp={"ShiftWorld": "@m0.ReturnValue"}); g.set("ssi", "ShiftInit", inp={"ShiftInit": "true"})
    g.call("pc", E_PCM, "GetOwningPlayerController")
    g.call("prj", K_GS, "ProjectWorldToScreen", inp={"Player": "@pc.ReturnValue", "WorldPosition": "@aloc.ReturnValue", "bPlayerViewportRelative": "false"}); g.branch("bpj", "@prj.ReturnValue")
    g.call("vp", "/Script/UMG.WidgetLayoutLibrary", "GetViewportSize"); g.call("bvp", K_MATH, "BreakVector2D", inp={"InVec": "@vp.ReturnValue"}); g.call("bsl", K_MATH, "BreakVector2D", inp={"InVec": "@prj.ScreenPosition"})
    g.call("nx0", K_MATH, "Divide_FloatFloat", inp={"A": "@bsl.X", "B": "@bvp.X"}); g.call("nx1", K_MATH, "Multiply_FloatFloat", inp={"A": "@nx0.ReturnValue", "B": "2.0"}); g.call("nx", K_MATH, "Subtract_FloatFloat", inp={"A": "@nx1.ReturnValue", "B": "1.0"})
    g.call("tgt", K_MATH, "Multiply_FloatFloat", inp={"A": "@gvs.ViewShift", "B": "-1.0"})
    g.call("err", K_MATH, "Subtract_FloatFloat", inp={"A": "@nx.ReturnValue", "B": "@tgt.ReturnValue"})
    g.call("e1", K_MATH, "Multiply_FloatFloat", inp={"A": "@err.ReturnValue", "B": "@nhalfw.ReturnValue"}); g.call("e2", K_MATH, "Multiply_FloatFloat", inp={"A": "@e1.ReturnValue", "B": "0.6"})
    g.get("gsw", "ShiftWorld"); g.call("nsw", K_MATH, "Add_FloatFloat", inp={"A": "@gsw.ShiftWorld", "B": "@e2.ReturnValue"}); g.set("ssw", "ShiftWorld", inp={"ShiftWorld": "@nsw.ReturnValue"})
    # vertical: target point to the image centre (NDC y = 0) while FocusOn, otherwise ease the offset back to 0
    g.call("ny0", K_MATH, "Divide_FloatFloat", inp={"A": "@bsl.Y", "B": "@bvp.Y"}); g.call("ny1", K_MATH, "Multiply_FloatFloat", inp={"A": "@ny0.ReturnValue", "B": "2.0"}); g.call("ny", K_MATH, "Subtract_FloatFloat", inp={"A": "@ny1.ReturnValue", "B": "1.0"})
    g.call("asp", K_MATH, "Divide_FloatFloat", inp={"A": "@bvp.X", "B": "@bvp.Y"}); g.call("halfh", K_MATH, "Divide_FloatFloat", inp={"A": "@nhalfw.ReturnValue", "B": "@asp.ReturnValue"})
    g.call("ey1", K_MATH, "Multiply_FloatFloat", inp={"A": "@ny.ReturnValue", "B": "@halfh.ReturnValue"}); g.call("ey2", K_MATH, "Multiply_FloatFloat", inp={"A": "@ey1.ReturnValue", "B": "-0.6"})
    g.get("gsu", "ShiftUp"); g.call("nsu", K_MATH, "Add_FloatFloat", inp={"A": "@gsu.ShiftUp", "B": "@ey2.ReturnValue"})
    g.get("gsu2", "ShiftUp"); g.call("dsu", K_MATH, "FInterpTo", inp={"Current": "@gsu2.ShiftUp", "Target": "0.0", "DeltaTime": "@dt.ReturnValue", "InterpSpeed": "4.0"})
    g.get("gfo2", "FocusOn"); g.call("selu", K_MATH, "SelectFloat", inp={"A": "@nsu.ReturnValue", "B": "@dsu.ReturnValue", "bPickA": "@gfo2.FocusOn"}); g.set("ssu", "ShiftUp", inp={"ShiftUp": "@selu.ReturnValue"})
    g.get("gsw2", "ShiftWorld"); g.call("off", K_MATH, "Multiply_VectorFloat", inp={"A": "@right.ReturnValue", "B": "@gsw2.ShiftWorld"})
    g.call("up", K_MATH, "GetUpVector", inp={"InRot": "@bm.Rotation"}); g.get("gsu3", "ShiftUp"); g.call("offu", K_MATH, "Multiply_VectorFloat", inp={"A": "@up.ReturnValue", "B": "@gsu3.ShiftUp"})
    g.call("loc0", K_MATH, "Subtract_VectorVector", inp={"A": "@bm.Location", "B": "@boff.ReturnValue"})
    g.call("loc1", K_MATH, "Add_VectorVector", inp={"A": "@loc0.ReturnValue", "B": "@off.ReturnValue"})
    g.call("loc", K_MATH, "Add_VectorVector", inp={"A": "@loc1.ReturnValue", "B": "@offu.ReturnValue"})
    g.link("loc.ReturnValue", "return.NewCameraLocation"); g.link("bm.Rotation", "return.NewCameraRotation"); g.link("nfov.ReturnValue", "return.NewCameraFOV")
    g.call("t", K_MATH, "BooleanOR", inp={"A": "true", "B": "true"}); g.link("t.ReturnValue", "return.ReturnValue")
    g.n("r2", "return_new"); g.call("f", K_MATH, "BooleanAND", inp={"A": "false", "B": "false"}); g.link("f.ReturnValue", "r2.ReturnValue")
    g.set("rsi", "ShiftInit", inp={"ShiftInit": "false"})   # outside the Jodi view: reset the controllers
    g.set("rsu", "ShiftUp", inp={"ShiftUp": "0.0"}); g.set("rcz", "CurZ", inp={"CurZ": "0.0"}); g.set("rcm", "CurZoom", inp={"CurZoom": "1.0"})
    g.chain("entry", "bk", "c0", "fe"); g.chain("fe", "bp", "sc"); g.chain("fe:Completed", "bc", "gv", "scz", "scm", "bsi", "bpj", "ssw", "ssu", "return")
    g.chain("bsi:else", "ss0", "ssi", "return"); g.chain("bpj:else", "return"); g.chain("bk:else", "rsi", "rsu", "rcz", "rcm", "r2"); g.chain("bc:else", "r2")
    return fn("BlueprintUpdateCamera", override=True, graph=g)


assets = [blueprint(HOOK, E_PCM, variables=[var("Spawned", "bool"), var("ViewShift", "float"), var("FovScale", "float", default="0.8"), var("DistScale", "float", default="1.0"), var("Cam", "object:" + E_CAMC), var("ShiftWorld", "float"), var("ShiftInit", "bool"),
                                                 var("FocusOn", "bool"), var("FocusZ", "float"), var("FocusZoom", "float", default="1.0"), var("CurZ", "float"), var("CurZoom", "float", default="1.0"), var("ShiftUp", "float")], defaults={"ViewPitchMin": "-80.0", "ViewPitchMax": "70.0"},
                    functions=[f_update_camera()], event_graph=event_graph())]
write(os.path.join(os.path.dirname(__file__), "..", "20_hook.json"), assets)
