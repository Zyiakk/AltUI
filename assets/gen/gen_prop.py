#!/usr/bin/env python3
"""Generates assets/28c_prop.json: BP_AltUIProp, one model spawned from the Objects tab (spec docs/specs/2026-10-23-objects-tab-design.md).
The root is a box sized to the model's bounds; the model hangs under it as a static mesh (furniture, props, mod models) or a skeletal
mesh (weapon models). Fixed: no physics, the box has no collision, the mesh blocks (clicks and figures hit it). Physics: the mesh
simulates if it can; a mesh without a simple collision body (many decoration meshes, weapons without a physics asset) does not,
then the box becomes the simulated body and carries the mesh - physics works for every model, only with a box shape."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *

from objects import PROP, CACHE_SG, SG_PROPS, S_PROPOBJ, S_PROPSCENE, S_PROPPLACE
E_BOX = "/Script/Engine.BoxComponent"; E_SHAPE = "/Script/Engine.ShapeComponent"
E_STM = "/Script/Engine.StaticMeshComponent"; E_SKM = "/Script/Engine.SkeletalMeshComponent"; E_SKIN = "/Script/Engine.SkinnedMeshComponent"
E_PRIMC = "/Script/Engine.PrimitiveComponent"; E_SCENEC = "/Script/Engine.SceneComponent"
E_STMESH = "/Script/Engine.StaticMesh"; E_SKMESH = "/Script/Engine.SkeletalMesh"
S_VEC = "struct:/Script/CoreUObject.Vector"; S_BSB = "/Script/CoreUObject.BoxSphereBounds"; S_TF = "struct:/Script/CoreUObject.Transform"
PROFILE = "PhysicsActor"   # blocks the cursor trace (Visibility), figures and the world; simulates like a crate of the game
MIN_EXTENT = 1.0           # cm: a flat plane still gets a box that can lie on the floor
E_MIDC = "/Script/Engine.MaterialInstanceDynamic"; E_ACTOR = "/Script/Engine.Actor"
FRAME_MESH = "/Engine/BasicShapes/Cube"   # 100 cm
FRAME_MAT = "/Game/Mod/AltUI/Mat/M_JointMarker"   # the joint spheres' material: unlit, drawn over everything, pale behind surfaces
FRAME_COLOR = "(R=1.0,G=0.72,B=0.1,A=1.0)"
FRAME_CM = 0.6             # thickness of an edge in the world (cm)
FRAME_NEAR, FRAME_FAR, FRAME_PALE = 2.0, 40.0, 0.3


def frame_edges():
    """The 12 edges of the bounds box: (axis along, signs on the two other axes) - mesh space, around Center, half sizes Extent."""
    out = []
    for a in range(3):
        o = [x for x in range(3) if x != a]
        for k in range(4): out.append((a, o[0], 1 if k & 1 else -1, o[1], 1 if k & 2 else -1))
    return out


def mesh_pin(g, p):
    """The model's component (KMesh for a weapon model, else SMesh) as a primitive component."""
    g.n(p, "call_self", function="Mesh"); return "@%s.comp" % p


def f_mesh():
    g = G(); g.get("gs", "SMesh"); g.get("gk", "KMesh"); g.get("gsk", "Skeletal")
    g.call("sel", K_MATH, "SelectObject", inp={"A": "@gk.KMesh", "B": "@gs.SMesh", "bSelectA": "@gsk.Skeletal"})
    g.cast("c", E_PRIMC, "@sel.ReturnValue"); g.link("c.AsPrimitive Component", "return.comp")
    return fn("Mesh", [], [param("comp", "object:" + E_PRIMC)], graph=g, pure=True)


def f_body():
    """What the object is in the world: the box while it carries the mesh with physics, else the mesh."""
    g = G(); g.n("m", "call_self", function="Mesh"); g.get("gb", "Box"); g.get("gbb", "BoxBody")
    g.call("sel", K_MATH, "SelectObject", inp={"A": "@gb.Box", "B": "@m.comp", "bSelectA": "@gbb.BoxBody"})
    g.cast("c", E_PRIMC, "@sel.ReturnValue"); g.link("c.AsPrimitive Component", "return.comp")
    return fn("Body", [], [param("comp", "object:" + E_PRIMC)], graph=g, pure=True)


def f_set_model():
    """The model by its object path (blocking load). ok = it is a static or skeletal mesh; the other component stays empty."""
    g = G(); g.call("sp", K_SYS, "MakeSoftObjectPath", inp={"PathString": "@entry.path"}); g.call("sr", K_SYS, "Conv_SoftObjPathToSoftObjRef", inp={"SoftObjectPath": "@sp.ReturnValue"})
    g.call("ld", K_SYS, "LoadAsset_Blocking", inp={"Asset": "@sr.ReturnValue"}); g.set("spa", "Path", inp={"Path": "@entry.path"})
    g.cast("cs", E_STMESH, "@ld.ReturnValue"); g.call("vs", K_SYS, "IsValid", inp={"Object": "@cs.AsStatic Mesh"}); g.branch("bs", "@vs.ReturnValue")
    g.get("gs", "SMesh"); g.call("ss", E_STM, "SetStaticMesh", inp={"self": "@gs.SMesh", "NewMesh": "@cs.AsStatic Mesh"}); g.set("sk0", "Skeletal", inp={"Skeletal": "false"})
    g.cast("ck", E_SKMESH, "@ld.ReturnValue"); g.call("vk", K_SYS, "IsValid", inp={"Object": "@ck.AsSkeletal Mesh"}); g.branch("bk", "@vk.ReturnValue")
    g.get("gk", "KMesh"); g.call("sk", E_SKIN, "SetSkeletalMesh", inp={"self": "@gk.KMesh", "NewMesh": "@ck.AsSkeletal Mesh", "bReinitPose": "true"}); g.set("sk1", "Skeletal", inp={"Skeletal": "true"})
    m = mesh_pin(g, "m"); g.call("mp", E_PRIMC, "SetCollisionProfileName", inp={"self": m, "InCollisionProfileName": PROFILE, "bUpdateOverlaps": "true"})
    g.get("gb", "Box"); g.call("bp", E_PRIMC, "SetCollisionProfileName", inp={"self": "@gb.Box", "InCollisionProfileName": "NoCollision", "bUpdateOverlaps": "true"})
    g.n("fb", "call_self", function="Fit Box")
    g.n("rok", "return_new", inp={"ok": "true"}); g.n("rno", "return_new", inp={"ok": "false"})
    g.chain("entry", "ld", "spa", "bs", "ss", "sk0", "mp", "bp", "fb", "rok"); g.chain("bs:else", "bk", "sk", "sk1", "mp"); g.chain("bk:else", "rno")
    return fn("Set Model", [param("path", "string")], [param("ok", "bool")], graph=g)


def f_fit_box():
    """Box = the model's own bounds (StaticMesh / SkeletalMesh GetBounds: in mesh space, at least MIN_EXTENT per half axis); the mesh
    moves so that the middle of its bounds sits on the middle of the box (Center keeps that middle for Set Physics)."""
    g = G(); g.get("gsk", "Skeletal"); g.branch("bsk", "@gsk.Skeletal")
    g.get("gk", "KMesh"); g.get("gkm", "SkeletalMesh", cls=E_SKIN); g.link("gk.KMesh", "gkm.self"); g.call("kb", E_SKMESH, "GetBounds", inp={"self": "@gkm.SkeletalMesh"})
    g.brk("kbb", S_BSB, "@kb.ReturnValue"); g.set("kc", "Center", inp={"Center": "@kbb.Origin"}); g.set("ke", "Extent", inp={"Extent": "@kbb.BoxExtent"})
    g.get("gs", "SMesh"); g.get("gsm", "StaticMesh", cls=E_STM); g.link("gs.SMesh", "gsm.self"); g.call("sb", E_STMESH, "GetBounds", inp={"self": "@gsm.StaticMesh"})
    g.brk("sbb", S_BSB, "@sb.ReturnValue"); g.set("sc", "Center", inp={"Center": "@sbb.Origin"}); g.set("se", "Extent", inp={"Extent": "@sbb.BoxExtent"})
    g.get("gx", "Extent"); g.call("bx", K_MATH, "BreakVector", inp={"InVec": "@gx.Extent"})
    for a in "XYZ": g.call("mx" + a, K_MATH, "FMax", inp={"A": "@bx.%s" % a, "B": str(MIN_EXTENT)})
    g.call("ext", K_MATH, "MakeVector", inp={"X": "@mxX.ReturnValue", "Y": "@mxY.ReturnValue", "Z": "@mxZ.ReturnValue"})
    g.get("gb", "Box"); g.call("sbx", E_BOX, "SetBoxExtent", inp={"self": "@gb.Box", "InBoxExtent": "@ext.ReturnValue", "bUpdateOverlaps": "false"})
    g.get("gc", "Center"); g.call("neg", K_MATH, "Multiply_VectorFloat", inp={"A": "@gc.Center", "B": "-1.0"}); m = mesh_pin(g, "m")
    g.call("rl", E_SCENEC, "K2_SetRelativeLocation", inp={"self": m, "NewLocation": "@neg.ReturnValue", "bSweep": "false", "bTeleport": "true"})
    g.chain("entry", "bsk", "kc", "ke", "sbx", "rl"); g.chain("bsk:else", "sc", "se", "sbx")
    return fn("Fit Box", graph=g)


def f_show_frame():
    """Selection frame (spec): the edges of the bounds box as thin bars (cubes with the joint-sphere material), attached to the mesh so
    they follow it simulating too; made on first use."""
    g = G(); g.get("gf", "Frame"); g.call("ln", K_ARR, "Array_Length", inp={"TargetArray": "@gf.Frame"}); g.call("none", K_MATH, "EqualEqual_IntInt", inp={"A": "@ln.ReturnValue", "B": "0"})
    g.call("mk", K_MATH, "BooleanAND", inp={"A": "@entry.on", "B": "@none.ReturnValue"}); g.branch("bmk", "@mk.ReturnValue"); g.self_("me")
    chain = []
    for i in range(12):
        p = "e%d" % i
        g.call(p + "tf", K_MATH, "MakeTransform", inp={"Location": "(X=0,Y=0,Z=0)", "Rotation": "(Pitch=0,Yaw=0,Roll=0)", "Scale": "(X=1,Y=1,Z=1)"})
        g.call(p + "nc", E_ACTOR, "AddComponentByClass", inp={"self": "@me.self", "Class": E_STM, "bManualAttachment": "true", "RelativeTransform": "@%stf.ReturnValue" % p, "bDeferredFinish": "false"})
        g.cast(p + "cs", E_STM, "@%snc.ReturnValue" % p); c = "@%scs.AsStatic Mesh Component" % p; m = mesh_pin(g, p + "m")
        g.call(p + "at", E_SCENEC, "K2_AttachToComponent", inp={"self": c, "Parent": m, "SocketName": "None", "LocationRule": "KeepRelative", "RotationRule": "KeepRelative", "ScaleRule": "KeepRelative", "bWeldSimulatedBodies": "false"})
        g.call(p + "sm", E_STM, "SetStaticMesh", inp={"self": c, "NewMesh": FRAME_MESH}); g.call(p + "mt", E_PRIMC, "SetMaterial", inp={"self": c, "ElementIndex": "0", "Material": FRAME_MAT})
        g.call(p + "md", E_PRIMC, "CreateDynamicMaterialInstance", inp={"self": c, "ElementIndex": "0", "SourceMaterial": "None", "OptionalName": "None"})
        g.call(p + "pc", E_MIDC, "SetVectorParameterValue", inp={"self": "@%smd.ReturnValue" % p, "ParameterName": "Color", "Value": FRAME_COLOR})
        g.call(p + "pn", E_MIDC, "SetScalarParameterValue", inp={"self": "@%smd.ReturnValue" % p, "ParameterName": "Near", "Value": str(FRAME_NEAR)})
        g.call(p + "pf", E_MIDC, "SetScalarParameterValue", inp={"self": "@%smd.ReturnValue" % p, "ParameterName": "Far", "Value": str(FRAME_FAR)})
        g.call(p + "pp", E_MIDC, "SetScalarParameterValue", inp={"self": "@%smd.ReturnValue" % p, "ParameterName": "Pale", "Value": str(FRAME_PALE)})
        g.call(p + "ce", E_PRIMC, "SetCollisionEnabled", inp={"self": c, "NewType": "NoCollision"}); g.call(p + "sh", E_PRIMC, "SetCastShadow", inp={"self": c, "NewCastShadow": "false"})
        g.get(p + "gf", "Frame"); g.call(p + "ad", K_ARR, "Array_Add", inp={"TargetArray": "@%sgf.Frame" % p, "NewItem": c})
        chain += [p + x for x in ("nc", "at", "sm", "mt", "md", "pc", "pn", "pf", "pp", "ce", "sh", "ad")]
    g.n("fit", "call_self", function="Fit Frame")
    g.get("gf2", "Frame"); g.foreach("fv", "@gf2.Frame"); g.call("vis", E_SCENEC, "SetVisibility", inp={"self": "@fv.Array Element", "bNewVisibility": "@entry.on", "bPropagateToChildren": "false"})
    g.chain("entry", "bmk", *chain, "fit", "fv"); g.chain("bmk:else", "fit"); g.chain("fv", "vis")
    return fn("Show Frame", [param("on", "bool")], graph=g)


def f_fit_frame():
    """The 12 bars on the edges of the bounds box (mesh space: Center +- Extent), FRAME_CM thick in the world whatever the scale."""
    g = G(); g.get("gc", "Center"); g.call("bc", K_MATH, "BreakVector", inp={"InVec": "@gc.Center"}); g.get("ge", "Extent"); g.call("be", K_MATH, "BreakVector", inp={"InVec": "@ge.Extent"})
    m = mesh_pin(g, "m"); g.call("ws", E_SCENEC, "K2_GetComponentScale", inp={"self": m}); g.call("bws", K_MATH, "BreakVector", inp={"InVec": "@ws.ReturnValue"})
    g.call("ws0", K_MATH, "FMax", inp={"A": "@bws.X", "B": "0.001"}); g.call("th", K_MATH, "Divide_FloatFloat", inp={"A": str(FRAME_CM / 100.0), "B": "@ws0.ReturnValue"})
    ax = "XYZ"; chain = []
    for i, (a, b, sb, c, sc) in enumerate(frame_edges()):
        p = "f%d" % i; g.get(p + "gf", "Frame"); g.call(p + "e", K_ARR, "Array_Get", inp={"TargetArray": "@%sgf.Frame" % p, "Index": str(i)})
        g.call(p + "v", K_SYS, "IsValid", inp={"Object": "@%se.Item" % p}); g.branch(p + "b", "@%sv.ReturnValue" % p)
        loc = {}; scl = {}
        for k, sign in ((b, sb), (c, sc)):
            g.call(p + "o" + ax[k], K_MATH, "Multiply_FloatFloat", inp={"A": "@be.%s" % ax[k], "B": str(float(sign))})
            g.call(p + "l" + ax[k], K_MATH, "Add_FloatFloat", inp={"A": "@bc.%s" % ax[k], "B": "@%so%s.ReturnValue" % (p, ax[k])}); loc[k] = "@%sl%s.ReturnValue" % (p, ax[k]); scl[k] = "@th.ReturnValue"
        loc[a] = "@bc.%s" % ax[a]; g.call(p + "s" + ax[a], K_MATH, "Multiply_FloatFloat", inp={"A": "@be.%s" % ax[a], "B": "0.02"}); scl[a] = "@%ss%s.ReturnValue" % (p, ax[a])   # 2 x half size / 100 cm
        g.call(p + "lv", K_MATH, "MakeVector", inp={"X": loc[0], "Y": loc[1], "Z": loc[2]}); g.call(p + "sv", K_MATH, "MakeVector", inp={"X": scl[0], "Y": scl[1], "Z": scl[2]})
        g.call(p + "sl", E_SCENEC, "K2_SetRelativeLocation", inp={"self": "@%se.Item" % p, "NewLocation": "@%slv.ReturnValue" % p, "bSweep": "false", "bTeleport": "true"})
        g.call(p + "ss", E_SCENEC, "SetRelativeScale3D", inp={"self": "@%se.Item" % p, "NewScale3D": "@%ssv.ReturnValue" % p})
        chain.append((p + "b", [p + "sl", p + "ss"]))
    prev = "entry"   # each bar that exists, then the next (a bar missing: straight to the next)
    for j, (b, body) in enumerate(chain):
        g.chain(prev, b, *body); prev = body[-1]
        if j + 1 < len(chain): g.chain(b + ":else", chain[j + 1][0])
    return fn("Fit Frame", graph=g)


def f_where():
    """Where the object is as a whole (for saving): the actor - except while the mesh simulates on its own (it leaves the box behind),
    then the transform the actor would take (as Set Physics off does: middle of its bounds, its turn and scale)."""
    g = G(); g.get("gp", "Physics"); g.get("gb", "BoxBody"); g.call("nb", K_MATH, "Not_PreBool", inp={"A": "@gb.BoxBody"})
    g.call("own", K_MATH, "BooleanAND", inp={"A": "@gp.Physics", "B": "@nb.ReturnValue"})
    m = mesh_pin(g, "m"); g.call("wt", E_SCENEC, "K2_GetComponentToWorld", inp={"self": m}); g.get("gc", "Center")
    g.call("wc", K_MATH, "TransformLocation", inp={"T": "@wt.ReturnValue", "Location": "@gc.Center"}); g.call("bt", K_MATH, "BreakTransform", inp={"InTransform": "@wt.ReturnValue"})
    g.call("mt", K_MATH, "MakeTransform", inp={"Location": "@wc.ReturnValue", "Rotation": "@bt.Rotation", "Scale": "@bt.Scale"})
    g.self_("me"); g.call("at", E_ACTOR, "GetTransform", inp={"self": "@me.self"})
    g.call("sel", K_MATH, "SelectTransform", inp={"A": "@mt.ReturnValue", "B": "@at.ReturnValue", "bPickA": "@own.ReturnValue"}); g.link("sel.ReturnValue", "return.where")
    return fn("Where", [], [param("where", S_TF)], graph=g, pure=True)


def f_set_physics():
    """on: the mesh simulates if it can, else the box does and carries the mesh (BoxBody). off: whatever simulated stops; a mesh that
    moved on its own (detached from the box while simulating) first takes the actor along - actor at the middle of its bounds, its
    turn and scale - and hangs on the box again where it was."""
    g = G(); g.branch("bon", "@entry.on")
    # on
    m = mesh_pin(g, "m1"); g.call("ms", E_PRIMC, "SetSimulatePhysics", inp={"self": m, "bSimulate": "true"})
    g.call("isim", E_PRIMC, "IsSimulatingPhysics", inp={"self": m, "BoneName": "None"}); g.branch("bsim", "@isim.ReturnValue")
    g.set("bb0", "BoxBody", inp={"BoxBody": "false"})
    g.call("ms0", E_PRIMC, "SetSimulatePhysics", inp={"self": m, "bSimulate": "false"})
    g.call("mnc", E_PRIMC, "SetCollisionProfileName", inp={"self": m, "InCollisionProfileName": "NoCollision", "bUpdateOverlaps": "true"})
    g.get("gb1", "Box"); g.call("bpc", E_PRIMC, "SetCollisionProfileName", inp={"self": "@gb1.Box", "InCollisionProfileName": PROFILE, "bUpdateOverlaps": "true"})
    g.get("gb2", "Box"); g.call("bsi", E_PRIMC, "SetSimulatePhysics", inp={"self": "@gb2.Box", "bSimulate": "true"}); g.set("bb1", "BoxBody", inp={"BoxBody": "true"})
    # off
    g.get("gbb", "BoxBody"); g.branch("bbx", "@gbb.BoxBody")
    g.get("gb3", "Box"); g.call("bso", E_PRIMC, "SetSimulatePhysics", inp={"self": "@gb3.Box", "bSimulate": "false"})
    g.get("gb4", "Box"); g.call("bnc", E_PRIMC, "SetCollisionProfileName", inp={"self": "@gb4.Box", "InCollisionProfileName": "NoCollision", "bUpdateOverlaps": "true"})
    m2 = mesh_pin(g, "m2"); g.call("mpc", E_PRIMC, "SetCollisionProfileName", inp={"self": m2, "InCollisionProfileName": PROFILE, "bUpdateOverlaps": "true"})
    g.set("bb2", "BoxBody", inp={"BoxBody": "false"})
    g.call("wt", E_SCENEC, "K2_GetComponentToWorld", inp={"self": m2}); g.call("mso", E_PRIMC, "SetSimulatePhysics", inp={"self": m2, "bSimulate": "false"})
    g.get("gce", "Center"); g.call("wc", K_MATH, "TransformLocation", inp={"T": "@wt.ReturnValue", "Location": "@gce.Center"})
    g.call("bt", K_MATH, "BreakTransform", inp={"InTransform": "@wt.ReturnValue"})
    g.call("at", K_MATH, "MakeTransform", inp={"Location": "@wc.ReturnValue", "Rotation": "@bt.Rotation", "Scale": "@bt.Scale"}); g.self_("me")
    g.call("sat", E_ACTOR, "K2_SetActorTransform", inp={"self": "@me.self", "NewTransform": "@at.ReturnValue", "bSweep": "false", "bTeleport": "true"})
    g.get("gb5", "Box")
    g.call("att", E_SCENEC, "K2_AttachToComponent", inp={"self": m2, "Parent": "@gb5.Box", "SocketName": "None", "LocationRule": "SnapToTarget",
                                                       "RotationRule": "SnapToTarget", "ScaleRule": "SnapToTarget", "bWeldSimulatedBodies": "false"})
    g.call("neg", K_MATH, "Multiply_VectorFloat", inp={"A": "@gce.Center", "B": "-1.0"})
    g.call("rl", E_SCENEC, "K2_SetRelativeLocation", inp={"self": m2, "NewLocation": "@neg.ReturnValue", "bSweep": "false", "bTeleport": "true"})
    g.set("sph", "Physics", inp={"Physics": "@entry.on"})
    g.chain("entry", "bon", "ms", "bsim", "bb0", "sph"); g.chain("bsim:else", "ms0", "mnc", "bpc", "bsi", "bb1", "sph")
    g.chain("bon:else", "bbx", "bso", "bnc", "mpc", "bb2", "sph"); g.chain("bbx:else", "mso", "sat", "att", "rl", "sph")
    return fn("Set Physics", [param("on", "bool")], graph=g)


def build():
    return [blueprint(PROP, E_ACTOR, components=[component("Box", E_BOX), component("SMesh", E_STM, parent="Box"), component("KMesh", E_SKM, parent="Box")],
                      variables=[var("Path", "string"), var("Label", "string"), var("Physics", "bool"), var("BoxBody", "bool"), var("Skeletal", "bool"), var("Center", S_VEC), var("Extent", S_VEC),
                                 var("Frame", "object:" + E_STM, "array")],
                      functions=[f_mesh(), f_body(), f_set_model(), f_fit_box(), f_set_physics(), f_show_frame(), f_fit_frame(), f_where()]),
            # mod models found by the scan (objects.CACHE_SLOT): the mod folders already scanned, the object paths of their static meshes,
            # Extra = folders only the full scan found (named unlike any pak; loaded at start while their directory exists)
            # scenes and positions (spec "Speichern"): an object = model path, its name, where it is (scale included), physics
            struct(S_PROPOBJ, [param("Path", "string"), param("Name", "string"), param("Where", S_TF), param("Physics", "bool")]),
            struct(S_PROPSCENE, [param("Name", "string"), param("Level", "string"), param("Objects", "struct:" + S_PROPOBJ, "array")]),
            struct(S_PROPPLACE, [param("Name", "string"), param("Level", "string"), param("Path", "string"), param("Where", S_TF), param("Physics", "bool")]),
            blueprint(SG_PROPS, "/Script/Engine.SaveGame", variables=[var("Scenes", "struct:" + S_PROPSCENE, "array"), var("Places", "struct:" + S_PROPPLACE, "array")]),
            blueprint(CACHE_SG, "/Script/Engine.SaveGame", variables=[var("Folders", "string", "array"), var("Paths", "string", "array"), var("Extra", "string", "array")])]


if __name__ == "__main__":
    write(os.path.join(os.path.dirname(__file__), "..", "28c_prop.json"), build())
