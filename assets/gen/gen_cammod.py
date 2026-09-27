"""Generates assets/27_cammod.json: CM_AltUICam, a UCameraModifier that frames Jodi in the free area beside the open panel.

Ported from the PlayerCameraManager override in 20_hook.json. A modifier attaches to whichever camera manager the game
already has (AddNewCameraModifier, applied in UpdateViewTarget after the view target's POV is computed), so the framing
no longer needs a replaced class and survives next to other mods that replace TKA_PlayerCameraManager.
Against the old override: the search for the view target's active CameraComponent is gone - location, rotation and FOV
arrive as parameters; the rest (closed-loop lateral offset, FOV/distance maths, FInterpTo easing) is unchanged.
On top of that the modifier carries the dragged camera height (UserZ) and a wall probe that limits the pull-back."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *

CAMMOD = M + "/CM_AltUICam"
E_CAMMOD = "/Script/Engine.CameraModifier"; E_PCM = "/Script/Engine.PlayerCameraManager"
CAM_TRACE_R = 15.0      # sphere radius of the wall probe: the camera keeps that much clearance from the surface
CAM_MIN_F = 0.05        # smallest fraction of the set distance the probe may leave over
CAM_MIN_DIST = 70.0     # cm, never closer to Jodi than this, whatever the probe reports
CAM_BACK_SPEED = 6.0    # FInterpTo speed for going back out once the way is free (going closer is instant)
DIST_SPEED = 10.0       # FInterpTo speed of the distance itself: the wheel changes it in steps, the camera glides


def f_modify_camera():
    """BlueprintModifyCamera: with ViewShift > 0 offset the camera by d*tan(FOV/2)*k to the right (Jodi moves left);
    otherwise hand the incoming view straight back."""
    g = G()
    g.get("gvs", "ViewShift")   # set by the inventory manager
    g.call("gt0", K_MATH, "Greater_FloatFloat", inp={"A": "@gvs.ViewShift", "B": "0.0"}); g.branch("bk", "@gt0.ReturnValue")
    # the view target is Jodi; during free cam / photo mode it is a CameraActor, but then ViewShift is 0 and this branch is off
    g.call("vt", E_CAMMOD, "GetViewTarget")
    g.call("vtv", K_SYS, "IsValid", inp={"Object": "@vt.ReturnValue"}); g.branch("bvt", "@vtv.ReturnValue")
    # focus (camera follows slot/face) and the dragged camera height: ease towards target height and zoom; off -> 0 / 1
    g.get("gfo", "FocusOn"); g.get("gfz", "FocusZ"); g.get("gfm", "FocusZoom")
    g.call("tz0", K_MATH, "SelectFloat", inp={"A": "@gfz.FocusZ", "B": "0.0", "bPickA": "@gfo.FocusOn"}); g.call("tm", K_MATH, "SelectFloat", inp={"A": "@gfm.FocusZoom", "B": "1.0", "bPickA": "@gfo.FocusOn"})
    # the dragged camera height adds to the focus height instead of replacing it: dragging still works while a slot is focused
    g.get("guz", "UserZ"); g.call("tz", K_MATH, "Add_FloatFloat", inp={"A": "@tz0.ReturnValue", "B": "@guz.UserZ"})
    g.get("gcz", "CurZ"); g.call("iz", K_MATH, "FInterpTo", inp={"Current": "@gcz.CurZ", "Target": "@tz.ReturnValue", "DeltaTime": "@entry.DeltaTime", "InterpSpeed": "4.0"}); g.set("scz", "CurZ", inp={"CurZ": "@iz.ReturnValue"})
    g.get("gcm", "CurZoom"); g.call("im", K_MATH, "FInterpTo", inp={"Current": "@gcm.CurZoom", "Target": "@tm.ReturnValue", "DeltaTime": "@entry.DeltaTime", "InterpSpeed": "4.0"}); g.set("scm", "CurZoom", inp={"CurZoom": "@im.ReturnValue"})
    # the wheel moves DistScale in steps; the camera follows it smoothly instead of jumping a notch at a time
    g.get("gcd0", "CurDist"); g.get("gds0", "DistScale")
    g.call("icd", K_MATH, "FInterpTo", inp={"Current": "@gcd0.CurDist", "Target": "@gds0.DistScale", "DeltaTime": "@entry.DeltaTime", "InterpSpeed": str(DIST_SPEED)})
    g.set("scd2", "CurDist", inp={"CurDist": "@icd.ReturnValue"})
    g.call("aloc0", E_ACTOR, "K2_GetActorLocation", inp={"self": "@vt.ReturnValue"}); g.get("gcz2", "CurZ")
    g.call("zv", K_MATH, "MakeVector", inp={"X": "0.0", "Y": "0.0", "Z": "@gcz2.CurZ"}); g.call("aloc", K_MATH, "Add_VectorVector", inp={"A": "@aloc0.ReturnValue", "B": "@zv.ReturnValue"})
    # depth along the view axis (not euclidean: the third-person camera sits higher than Jodi's centre)
    g.call("fwd0", K_MATH, "GetForwardVector", inp={"InRot": "@entry.ViewRotation"})
    g.call("dvec", K_MATH, "Subtract_VectorVector", inp={"A": "@aloc.ReturnValue", "B": "@entry.ViewLocation"})
    g.call("dist", K_MATH, "Dot_VectorVector", inp={"A": "@dvec.ReturnValue", "B": "@fwd0.ReturnValue"})
    # incoming FOV (the game's, after the view target was evaluated), narrowed by FovScale; camera moved back so Jodi stays the same size
    g.call("half", K_MATH, "Divide_FloatFloat", inp={"A": "@entry.FOV", "B": "2.0"}); g.call("tan", K_MATH, "DegTan", inp={"A": "@half.ReturnValue"})
    g.get("gfs", "FovScale"); g.call("nfov", K_MATH, "Multiply_FloatFloat", inp={"A": "@entry.FOV", "B": "@gfs.FovScale"})
    g.call("nhalf", K_MATH, "Divide_FloatFloat", inp={"A": "@nfov.ReturnValue", "B": "2.0"}); g.call("ntan", K_MATH, "DegTan", inp={"A": "@nhalf.ReturnValue"})
    g.call("halfw", K_MATH, "Multiply_FloatFloat", inp={"A": "@dist.ReturnValue", "B": "@tan.ReturnValue"})        # half image width at Jodi's distance
    g.call("ndist0", K_MATH, "Divide_FloatFloat", inp={"A": "@halfw.ReturnValue", "B": "@ntan.ReturnValue"})       # new distance with the narrower FOV (same image size)
    g.get("gcd1", "CurDist"); g.call("ndist1", K_MATH, "Multiply_FloatFloat", inp={"A": "@ndist0.ReturnValue", "B": "@gcd1.CurDist"})
    g.get("gcm2", "CurZoom"); g.call("ndist", K_MATH, "Multiply_FloatFloat", inp={"A": "@ndist1.ReturnValue", "B": "@gcm2.CurZoom"})
    # a wall between Jodi and where the pull-back would put the camera: probe from the target point to that position (the lateral and
    # vertical offsets of the last frame included, so side walls count too) and keep only the free part of the distance. The camera
    # then sits closer and Jodi is framed the same, just larger - better than a frame of wall. Turning away gives the set distance back.
    g.call("back0", K_MATH, "Subtract_FloatFloat", inp={"A": "@ndist.ReturnValue", "B": "@dist.ReturnValue"})
    g.call("fwdp", K_MATH, "GetForwardVector", inp={"InRot": "@entry.ViewRotation"}); g.call("boffp", K_MATH, "Multiply_VectorFloat", inp={"A": "@fwdp.ReturnValue", "B": "@back0.ReturnValue"})
    g.call("rightp", K_MATH, "GetRightVector", inp={"InRot": "@entry.ViewRotation"}); g.get("gswp", "ShiftWorld"); g.call("offp", K_MATH, "Multiply_VectorFloat", inp={"A": "@rightp.ReturnValue", "B": "@gswp.ShiftWorld"})
    g.call("upp", K_MATH, "GetUpVector", inp={"InRot": "@entry.ViewRotation"}); g.get("gsup", "ShiftUp"); g.call("offup", K_MATH, "Multiply_VectorFloat", inp={"A": "@upp.ReturnValue", "B": "@gsup.ShiftUp"})
    g.call("pr0", K_MATH, "Subtract_VectorVector", inp={"A": "@entry.ViewLocation", "B": "@boffp.ReturnValue"})
    g.call("pr1", K_MATH, "Add_VectorVector", inp={"A": "@pr0.ReturnValue", "B": "@offp.ReturnValue"}); g.call("probe", K_MATH, "Add_VectorVector", inp={"A": "@pr1.ReturnValue", "B": "@offup.ReturnValue"})
    g.n("ign", "make_array", count=1, type="object:" + E_ACTOR, inp={"[0]": "@vt.ReturnValue"})   # Jodi herself never blocks the view of Jodi
    g.call("tr", K_SYS, "SphereTraceSingle", inp={"Start": "@aloc.ReturnValue", "End": "@probe.ReturnValue", "Radius": str(CAM_TRACE_R), "TraceChannel": "TraceTypeQuery1",
                                                 "bTraceComplex": "false", "ActorsToIgnore": "@ign.Array", "DrawDebugType": "None", "bIgnoreSelf": "true",
                                                 "TraceColor": "(R=1,G=0,B=0,A=1)", "TraceHitColor": "(R=0,G=1,B=0,A=1)", "DrawTime": "5.0"})
    g.call("bhr", K_GS, "BreakHitResult", inp={"Hit": "@tr.OutHit"})
    g.call("nio", K_MATH, "Not_PreBool", inp={"A": "@bhr.bInitialOverlap"})   # target point itself inside geometry: the probe says nothing, keep the set distance
    g.call("blocked", K_MATH, "BooleanAND", inp={"A": "@tr.ReturnValue", "B": "@nio.ReturnValue"})
    g.call("tcl", K_MATH, "FClamp", inp={"Value": "@bhr.Time", "Min": str(CAM_MIN_F), "Max": "1.0"})
    g.call("tgtf", K_MATH, "SelectFloat", inp={"A": "@tcl.ReturnValue", "B": "1.0", "bPickA": "@blocked.ReturnValue"})
    # closer takes effect at once - a wall must never flash; going back out is eased, so turning away does not snap
    g.get("gdf", "CurDistF"); g.call("ef", K_MATH, "FInterpTo", inp={"Current": "@gdf.CurDistF", "Target": "@tgtf.ReturnValue", "DeltaTime": "@entry.DeltaTime", "InterpSpeed": str(CAM_BACK_SPEED)})
    g.call("clsr", K_MATH, "Less_FloatFloat", inp={"A": "@tgtf.ReturnValue", "B": "@gdf.CurDistF"})
    g.call("nf", K_MATH, "SelectFloat", inp={"A": "@tgtf.ReturnValue", "B": "@ef.ReturnValue", "bPickA": "@clsr.ReturnValue"}); g.set("sdf", "CurDistF", inp={"CurDistF": "@nf.ReturnValue"})
    g.get("gdf2", "CurDistF"); g.call("ndist2", K_MATH, "Multiply_FloatFloat", inp={"A": "@ndist.ReturnValue", "B": "@gdf2.CurDistF"})
    g.call("ndistc", K_MATH, "FClamp", inp={"Value": "@ndist2.ReturnValue", "Min": str(CAM_MIN_DIST), "Max": "100000.0"})
    g.call("back", K_MATH, "Subtract_FloatFloat", inp={"A": "@ndistc.ReturnValue", "B": "@dist.ReturnValue"})
    g.call("fwd", K_MATH, "GetForwardVector", inp={"InRot": "@entry.ViewRotation"}); g.call("boff", K_MATH, "Multiply_VectorFloat", inp={"A": "@fwd.ReturnValue", "B": "@back.ReturnValue"})
    g.call("nhalfw", K_MATH, "Multiply_FloatFloat", inp={"A": "@ndistc.ReturnValue", "B": "@ntan.ReturnValue"})     # half image width at Jodi's (new) distance
    # closed-loop lateral offset: compare Jodi's actual screen position (ProjectWorldToScreen of the last rendered view) with the
    # target NDC x = -k and track the offset (gain 0.6). Initial value analytic: lateral + k * half image width.
    g.call("right", K_MATH, "GetRightVector", inp={"InRot": "@entry.ViewRotation"})
    g.call("lat", K_MATH, "Dot_VectorVector", inp={"A": "@dvec.ReturnValue", "B": "@right.ReturnValue"})
    g.call("m1", K_MATH, "Multiply_FloatFloat", inp={"A": "@nhalfw.ReturnValue", "B": "@gvs.ViewShift"})
    g.call("m0", K_MATH, "Add_FloatFloat", inp={"A": "@lat.ReturnValue", "B": "@m1.ReturnValue"})
    g.get("gsi", "ShiftInit"); g.branch("bsi", "@gsi.ShiftInit")
    g.set("ss0", "ShiftWorld", inp={"ShiftWorld": "@m0.ReturnValue"}); g.set("ssi", "ShiftInit", inp={"ShiftInit": "true"})
    g.get("co", "CameraOwner")   # inherited, so a self member: the modifier belongs to the camera manager, not to a controller
    g.call("pc", E_PCM, "GetOwningPlayerController", inp={"self": "@co.CameraOwner"})
    g.call("prj", K_GS, "ProjectWorldToScreen", inp={"Player": "@pc.ReturnValue", "WorldPosition": "@aloc.ReturnValue", "bPlayerViewportRelative": "false"}); g.branch("bpj", "@prj.ReturnValue")
    g.call("vp", "/Script/UMG.WidgetLayoutLibrary", "GetViewportSize"); g.call("bvp", K_MATH, "BreakVector2D", inp={"InVec": "@vp.ReturnValue"}); g.call("bsl", K_MATH, "BreakVector2D", inp={"InVec": "@prj.ScreenPosition"})
    g.call("nx0", K_MATH, "Divide_FloatFloat", inp={"A": "@bsl.X", "B": "@bvp.X"}); g.call("nx1", K_MATH, "Multiply_FloatFloat", inp={"A": "@nx0.ReturnValue", "B": "2.0"}); g.call("nx", K_MATH, "Subtract_FloatFloat", inp={"A": "@nx1.ReturnValue", "B": "1.0"})
    g.call("tgt", K_MATH, "Multiply_FloatFloat", inp={"A": "@gvs.ViewShift", "B": "-1.0"})
    g.call("err", K_MATH, "Subtract_FloatFloat", inp={"A": "@nx.ReturnValue", "B": "@tgt.ReturnValue"})
    g.call("e1", K_MATH, "Multiply_FloatFloat", inp={"A": "@err.ReturnValue", "B": "@nhalfw.ReturnValue"}); g.call("e2", K_MATH, "Multiply_FloatFloat", inp={"A": "@e1.ReturnValue", "B": "0.6"})
    g.get("gsw", "ShiftWorld"); g.call("nsw", K_MATH, "Add_FloatFloat", inp={"A": "@gsw.ShiftWorld", "B": "@e2.ReturnValue"}); g.set("ssw", "ShiftWorld", inp={"ShiftWorld": "@nsw.ReturnValue"})
    # vertical: target point to the image centre (NDC y = 0) while a focus or a dragged height is active, otherwise ease the offset back to 0
    g.call("ny0", K_MATH, "Divide_FloatFloat", inp={"A": "@bsl.Y", "B": "@bvp.Y"}); g.call("ny1", K_MATH, "Multiply_FloatFloat", inp={"A": "@ny0.ReturnValue", "B": "2.0"}); g.call("ny", K_MATH, "Subtract_FloatFloat", inp={"A": "@ny1.ReturnValue", "B": "1.0"})
    g.call("asp", K_MATH, "Divide_FloatFloat", inp={"A": "@bvp.X", "B": "@bvp.Y"}); g.call("halfh", K_MATH, "Divide_FloatFloat", inp={"A": "@nhalfw.ReturnValue", "B": "@asp.ReturnValue"})
    g.call("ey1", K_MATH, "Multiply_FloatFloat", inp={"A": "@ny.ReturnValue", "B": "@halfh.ReturnValue"}); g.call("ey2", K_MATH, "Multiply_FloatFloat", inp={"A": "@ey1.ReturnValue", "B": "-0.6"})
    g.get("gsu", "ShiftUp"); g.call("nsu", K_MATH, "Add_FloatFloat", inp={"A": "@gsu.ShiftUp", "B": "@ey2.ReturnValue"})
    g.get("gsu2", "ShiftUp"); g.call("dsu", K_MATH, "FInterpTo", inp={"Current": "@gsu2.ShiftUp", "Target": "0.0", "DeltaTime": "@entry.DeltaTime", "InterpSpeed": "4.0"})
    g.get("gfo2", "FocusOn"); g.get("guz2", "UserZ"); g.call("uzn", K_MATH, "NotEqual_FloatFloat", inp={"A": "@guz2.UserZ", "B": "0.0"})
    g.call("von", K_MATH, "BooleanOR", inp={"A": "@gfo2.FocusOn", "B": "@uzn.ReturnValue"})
    g.call("selu", K_MATH, "SelectFloat", inp={"A": "@nsu.ReturnValue", "B": "@dsu.ReturnValue", "bPickA": "@von.ReturnValue"}); g.set("ssu", "ShiftUp", inp={"ShiftUp": "@selu.ReturnValue"})
    g.get("gsw2", "ShiftWorld"); g.call("off", K_MATH, "Multiply_VectorFloat", inp={"A": "@right.ReturnValue", "B": "@gsw2.ShiftWorld"})
    g.call("up", K_MATH, "GetUpVector", inp={"InRot": "@entry.ViewRotation"}); g.get("gsu3", "ShiftUp"); g.call("offu", K_MATH, "Multiply_VectorFloat", inp={"A": "@up.ReturnValue", "B": "@gsu3.ShiftUp"})
    g.call("loc0", K_MATH, "Subtract_VectorVector", inp={"A": "@entry.ViewLocation", "B": "@boff.ReturnValue"})
    g.call("loc1", K_MATH, "Add_VectorVector", inp={"A": "@loc0.ReturnValue", "B": "@off.ReturnValue"})
    g.call("loc", K_MATH, "Add_VectorVector", inp={"A": "@loc1.ReturnValue", "B": "@offu.ReturnValue"})
    g.link("loc.ReturnValue", "return.NewViewLocation"); g.link("entry.ViewRotation", "return.NewViewRotation"); g.link("nfov.ReturnValue", "return.NewFOV")
    # pass-through: hand back what came in (no "not handled" flag on a modifier - unchanged values are the way to stay out)
    g.n("r2", "return_new")
    g.link("entry.ViewLocation", "r2.NewViewLocation"); g.link("entry.ViewRotation", "r2.NewViewRotation"); g.link("entry.FOV", "r2.NewFOV")
    g.set("rsi", "ShiftInit", inp={"ShiftInit": "false"})   # panel closed / no view target: reset the controllers
    g.set("rsu", "ShiftUp", inp={"ShiftUp": "0.0"}); g.set("rcz", "CurZ", inp={"CurZ": "0.0"}); g.set("rcm", "CurZoom", inp={"CurZoom": "1.0"}); g.set("rdf", "CurDistF", inp={"CurDistF": "1.0"})
    g.get("gds2", "DistScale"); g.set("rcd2", "CurDist", inp={"CurDist": "@gds2.DistScale"})
    g.chain("entry", "bk", "bvt", "scz", "scm", "scd2", "tr", "sdf", "bsi", "bpj", "ssw", "ssu", "return")
    g.chain("bsi:else", "ss0", "ssi", "return"); g.chain("bpj:else", "return")
    g.chain("bk:else", "rsi", "rsu", "rcz", "rcm", "rdf", "rcd2", "r2"); g.chain("bvt:else", "r2")
    return fn("BlueprintModifyCamera", override=True, graph=g)


assets = [blueprint(CAMMOD, E_CAMMOD,
                    variables=[var("ViewShift", "float"), var("FovScale", "float", default="0.8"), var("DistScale", "float", default="1.0"),
                               var("ShiftWorld", "float"), var("ShiftInit", "bool"),
                               var("FocusOn", "bool"), var("FocusZ", "float"), var("FocusZoom", "float", default="1.0"), var("UserZ", "float"),
                               var("CurZ", "float"), var("CurZoom", "float", default="1.0"), var("ShiftUp", "float"), var("CurDistF", "float", default="1.0"), var("CurDist", "float", default="1.0")],
                    functions=[f_modify_camera()])]
write(os.path.join(os.path.dirname(__file__), "..", "27_cammod.json"), assets)
