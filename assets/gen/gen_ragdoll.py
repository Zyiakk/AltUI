#!/usr/bin/env python3
"""Generates assets/28_ragdoll.json: BP_AltUIRagdoll, a copy of a character as a physics puppet (prototype, see
docs/notes/2026-10-05-ragdolls-machbarkeit.md). No game logic of its own: Copy From takes over the mesh, materials and morph
values of a character and every visible mesh attached to it (clothes and hair follow the body via the master pose, static
meshes sit at their socket); Go Ragdoll switches the body to physics like the game's own Enable Ragdoll Ex; Toggle Lock
stiffens the joint between a bone and its parent in its current angle with a runtime PhysicsConstraintComponent (the game
does the same when Jodi drags a body)."""
import os, sys, re; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *
from rag_detail import (FINGER_BONES, LID_BONES, DETAIL_BONES, GROUP_BONES, DETAIL_GROUP, REF_ROT, curl_axis, curl_deg, spread_deg, LID_AXIS, LID_DEG,
                        HAND_POSES, DETAIL_NEAR, DETAIL_TICK, DETAIL_SCALE, DETAIL_COLOR, GAZE_SIDE_DEG, GAZE_UP_DEG, GAZE_SIDE_SIGN, vec_lit)
E_PCM = "/Script/Engine.PlayerCameraManager"

RAGDOLL = "/Game/Mod/AltUI/BP_AltUIRagdoll"; RAG_ABP = "/Game/Mod/AltUI/ABP_AltUIRagdoll"; S_POSE = "/Script/Engine.PoseSnapshot"
SKELETON = "/Game/Project/Character/Jodi/Body/Female_Skeleton"
LOCK_UP = 4   # Toggle Lock: steps up the skeleton to find a parent bone with a body
POSE_RIGID = ["spine_01", "spine_02", "spine_03", "neck_01", "head", "upperarm_l", "upperarm_r", "lowerarm_l", "lowerarm_r", "hand_l", "hand_r",
              "thigh_l", "thigh_r", "calf_l", "calf_r", "foot_l", "foot_r", "Breast_L", "Breast_R", "Hip_L", "Hip_R"]   # Loosen Below holds these rigid unless loose
# the frozen pose needs an ABP per skeleton (the engine drops an anim BP whose target skeleton is not the mesh's): Jodi / NPC first, then the
# zombie skeletons - stand-ins in the kit (skeleton_stub), the real ones in the game by path. Copy From takes the first one that comes up.
RAG_SKELETONS = [("Zombie", "/Game/Mannequin/Zombie_Skeleton"), ("Glutton", "/Game/Project/Zombie/Glutton/Glutton_Skeleton"),
                 ("GrimReaper", "/Game/Project/Zombie/GrimReaper/GrimReaper_Skeleton"), ("Devourer", "/Game/Project/Zombie/Devourer/Mesh/Devourer_Skeleton"),
                 ("Bloodworm", "/Game/Project/Zombie/Bloodworm/Bloodworm_Skeleton")]
RAG_ABPS = [RAG_ABP] + [RAG_ABP + "_" + k for k, _ in RAG_SKELETONS]
LOOSE_UP = 8  # Loose Root: steps up from a clicked bone to the loose joint it hangs on (hand -> lowerarm -> upperarm -> clavicle -> spine ...)
E_SKM = "/Script/Engine.SkeletalMeshComponent"; E_SKIN = "/Script/Engine.SkinnedMeshComponent"; E_STM = "/Script/Engine.StaticMeshComponent"
E_MESHC = "/Script/Engine.MeshComponent"; E_PRIMC = "/Script/Engine.PrimitiveComponent"; E_SCENEC = "/Script/Engine.SceneComponent"
E_ACTC = "/Script/Engine.ActorComponent"; E_MIDC = "/Script/Engine.MaterialInstanceDynamic"; E_SKMESH = "/Script/Engine.SkeletalMesh"
E_CONSTR = "/Script/Engine.PhysicsConstraintComponent"; E_CHAR = "/Script/Engine.Character"
E_MI = "/Script/Engine.MaterialInstance"; E_MATI = "/Script/Engine.MaterialInterface"; E_STMESH = "/Script/Engine.StaticMesh"; E_TEX = "/Script/Engine.Texture"
S_LIN = "struct:/Script/CoreUObject.LinearColor"; S_TF = "struct:/Script/CoreUObject.Transform"
S_ROT = "struct:/Script/CoreUObject.Rotator"; S_VEC = "struct:/Script/CoreUObject.Vector"
# scenes with zombie figures (their clothes are random): every mesh of the figure with its materials, rebuilt from that on load
S_RAGMAT = "/Game/Mod/AltUI/S_RagMat"; S_RAGPART = "/Game/Mod/AltUI/S_RagPart"
PART_UP = 4   # Collect Parts: steps up from a mesh to the component that hangs on the body (crystal mesh -> crystal root -> body)
# joint markers (spec 2026-10-17): a sphere on every grabbable body - the pelvis and the 17 joints of the Ragdolls page
MARKER_BONES = ["pelvis", "spine_01", "spine_02", "spine_03", "neck_01", "head", "upperarm_l", "upperarm_r", "lowerarm_l", "lowerarm_r", "hand_l", "hand_r",
                "thigh_l", "thigh_r", "calf_l", "calf_r", "foot_l", "foot_r"]
MARK_MESH = "/Engine/BasicShapes/Sphere"   # 100 cm across
MARK_MAT = "/Game/Mod/AltUI/Mat/M_JointMarker"   # scripts/quickmenu/material.py: no depth test, full in front / inside its limb, pale behind the body
MARK_SCALE = 0.035   # scale of the sphere mesh: 3.5 cm
# how deep (cm) a sphere may lie behind the nearest surface and still count as "in its own body part" (about that part's thickness);
# up to MARK_BAND more it fades to MARK_PALE - one band for all made the torso's spheres never pale and the far ones barely (ui-test-116)
MARK_NEAR = {"pelvis": 13, "spine_01": 12, "spine_02": 12, "spine_03": 12, "neck_01": 6, "head": 10, "upperarm_l": 6, "upperarm_r": 6, "lowerarm_l": 5,
             "lowerarm_r": 5, "hand_l": 4, "hand_r": 4, "thigh_l": 9, "thigh_r": 9, "calf_l": 7, "calf_r": 7, "foot_l": 5, "foot_r": 5}
MARK_BAND, MARK_PALE = 6.0, 0.15
# (ui-test-116: a pair of opaque core + pale hull showed only the hull - the core sits at the bone, inside its own limb, so it was always hidden)
MARK_COLORS = {"pinned": "(R=0.1,G=0.35,B=1.0,A=1.0)", "locked": "(R=1.0,G=0.12,B=0.1,A=1.0)", "loose": "(R=0.1,G=0.9,B=0.2,A=1.0)", "plain": "(R=0.2,G=0.2,B=0.2,A=1.0)"}
E_SMC = "/Script/Engine.StaticMeshComponent"
# attackable (ragproxy.py): a hit on a frozen figure loosens the chain from this root (as posing does), then Hit Back
RAG_HIT_ROOT = {"head": "neck_01", "neck_01": "neck_01", "spine_03": "spine_03", "spine_02": "spine_02", "spine_01": "spine_01",
                "upperarm_l": "upperarm_l", "lowerarm_l": "upperarm_l", "hand_l": "upperarm_l", "upperarm_r": "upperarm_r", "lowerarm_r": "upperarm_r", "hand_r": "upperarm_r",
                "thigh_l": "thigh_l", "calf_l": "thigh_l", "foot_l": "thigh_l", "thigh_r": "thigh_r", "calf_r": "thigh_r", "foot_r": "thigh_r"}
RAG_HIT_BACK = 1.0   # s: a frozen figure's jolt, then its pose again


def ident_tf(g):
    """A wired identity transform (AddComponentByClass takes it by reference: a pin default does not compile)."""
    n = "idtf%d" % len(g.nodes)
    g.call(n, K_MATH, "MakeTransform", inp={"Location": "(X=0,Y=0,Z=0)", "Rotation": "(Pitch=0,Yaw=0,Roll=0)", "Scale": "(X=1,Y=1,Z=1)"}); return "@%s.ReturnValue" % n


def copy_materials(g, p, src, dst):
    """Every material slot of src onto dst: a dynamic instance becomes a copy of its own (dst instance from it + its parameters),
    so later colour changes on the source do not reach the copy; anything else is shared as it is. Returns (head, tail) ids."""
    g.call(p + "ms", E_MESHC, "GetMaterials", inp={"self": src}); g.foreach(p + "fm", "@%sms.ReturnValue" % p)
    g.cast(p + "cm", E_MIDC, "@%sfm.Array Element" % p); g.call(p + "vm", K_SYS, "IsValid", inp={"Object": "@%scm.AsMaterial Instance Dynamic" % p}); g.branch(p + "bm", "@%svm.ReturnValue" % p)
    # parent = the parent of the source instance, not the instance itself: a child of Jodi's instance would keep inheriting every parameter she
    # sets later (e.g. the body mask of what she wears next -> holes in the copy)
    g.get(p + "par", "Parent", cls=E_MIDC); g.link(p + "cm.AsMaterial Instance Dynamic", p + "par.self")
    g.call(p + "dm", E_PRIMC, "CreateDynamicMaterialInstance", inp={"self": dst, "ElementIndex": "@%sfm.Array Index" % p, "SourceMaterial": "@%spar.Parent" % p, "OptionalName": "None"})
    g.call(p + "cp", E_MIDC, "K2_CopyMaterialInstanceParameters", inp={"self": "@%sdm.ReturnValue" % p, "Source": "@%scm.AsMaterial Instance Dynamic" % p, "bQuickParametersOnly": "false"})
    g.call(p + "sm", E_PRIMC, "SetMaterial", inp={"self": dst, "ElementIndex": "@%sfm.Array Index" % p, "Material": "@%sfm.Array Element" % p})
    g.chain(p + "fm", p + "bm", p + "dm", p + "cp"); g.chain(p + "bm:else", p + "sm")   # GetMaterials is const -> pure
    return p + "fm", p + "fm:Completed"


def f_copy_from():
    g = G()
    g.get("gm", "Mesh", cls=E_CHAR); g.link("entry.source", "gm.self"); src = "@gm.Mesh"
    g.get("gb", "Body"); body = "@gb.Body"
    g.get("gsk", "SkeletalMesh", cls=E_SKIN); g.link("gm.Mesh", "gsk.self")
    g.call("ssk", E_SKIN, "SetSkeletalMesh", inp={"self": body, "NewMesh": "@gsk.SkeletalMesh", "bReinitPose": "true"}); g.n("sb", "call_self", function="Setup Body")
    mh, mt = copy_materials(g, "b_", src, body)
    # morph targets: every one the source mesh knows, at the value the source has now (face, body mods)
    g.call("mn", E_SKMESH, "K2_GetAllMorphTargetNames", inp={"self": "@gsk.SkeletalMesh"}); g.foreach("fmn", "@mn.ReturnValue")
    g.call("mnn", K_STR, "Conv_StringToName", inp={"InString": "@fmn.Array Element"})
    g.call("mv", E_SKM, "GetMorphTarget", inp={"self": src, "MorphTargetName": "@mnn.ReturnValue"})
    g.call("smv", E_SKM, "SetMorphTarget", inp={"self": body, "MorphTargetName": "@mnn.ReturnValue", "Value": "@mv.ReturnValue", "bRemoveZeroWeight": "true"})
    # everything visible attached to the source mesh: clothes, hair (skeletal: follow the body), accessories (static: at their socket)
    g.call("cmp", E_ACTOR, "K2_GetComponentsByClass", inp={"self": "@entry.source", "ComponentClass": E_MESHC}); g.set("scmp", "Comps", inp={"Comps": "@cmp.ReturnValue"})
    g.get("gcs", "Comps"); g.foreach("fc", "@gcs.Comps"); g.cast("cs", E_SCENEC, "@fc.Array Element")
    g.call("par", E_SCENEC, "GetAttachParent", inp={"self": "@cs.AsScene Component"}); g.call("isp", K_MATH, "EqualEqual_ObjectObject", inp={"A": "@par.ReturnValue", "B": src})
    g.call("vis", E_SCENEC, "IsVisible", inp={"self": "@cs.AsScene Component"}); g.call("ok", K_MATH, "BooleanAND", inp={"A": "@isp.ReturnValue", "B": "@vis.ReturnValue"}); g.branch("bok", "@ok.ReturnValue")
    # skeletal
    g.cast("ck", E_SKM, "@fc.Array Element"); g.call("vk", K_SYS, "IsValid", inp={"Object": "@ck.AsSkeletal Mesh Component"}); g.branch("bk", "@vk.ReturnValue")
    g.call("nk", E_ACTOR, "AddComponentByClass", inp={"Class": E_SKM, "bManualAttachment": "false", "RelativeTransform": ident_tf(g), "bDeferredFinish": "false"})
    g.cast("cnk", E_SKM, "@nk.ReturnValue"); nk = "@cnk.AsSkeletal Mesh Component"
    g.get("gksk", "SkeletalMesh", cls=E_SKIN); g.link("ck.AsSkeletal Mesh Component", "gksk.self")
    g.call("ksk", E_SKIN, "SetSkeletalMesh", inp={"self": nk, "NewMesh": "@gksk.SkeletalMesh", "bReinitPose": "true"})
    g.call("kmp", E_SKIN, "SetMasterPoseComponent", inp={"self": nk, "NewMasterBoneComponent": body, "bForceUpdate": "true"})
    kh, kt = copy_materials(g, "k_", "@ck.AsSkeletal Mesh Component", nk)
    # static
    g.cast("cst", E_STM, "@fc.Array Element"); g.call("vst", K_SYS, "IsValid", inp={"Object": "@cst.AsStatic Mesh Component"}); g.branch("bst", "@vst.ReturnValue")
    g.call("ns", E_ACTOR, "AddComponentByClass", inp={"Class": E_STM, "bManualAttachment": "true", "RelativeTransform": ident_tf(g), "bDeferredFinish": "false"})
    g.cast("cns", E_STM, "@ns.ReturnValue"); ns = "@cns.AsStatic Mesh Component"
    g.get("gsm", "StaticMesh", cls=E_STM); g.link("cst.AsStatic Mesh Component", "gsm.self")
    g.call("ssm", E_STM, "SetStaticMesh", inp={"self": ns, "NewMesh": "@gsm.StaticMesh"})
    g.call("sock", E_SCENEC, "GetAttachSocketName", inp={"self": "@cst.AsStatic Mesh Component"})
    g.call("att", E_SCENEC, "K2_AttachToComponent", inp={"self": ns, "Parent": body, "SocketName": "@sock.ReturnValue", "LocationRule": "KeepRelative",
                                                       "RotationRule": "KeepRelative", "ScaleRule": "KeepRelative", "bWeldSimulatedBodies": "false"})
    g.get("grl", "RelativeLocation", cls=E_SCENEC); g.link("cst.AsStatic Mesh Component", "grl.self"); g.get("grr", "RelativeRotation", cls=E_SCENEC); g.link("cst.AsStatic Mesh Component", "grr.self")
    g.get("grs", "RelativeScale3D", cls=E_SCENEC); g.link("cst.AsStatic Mesh Component", "grs.self")
    g.call("srl", E_SCENEC, "K2_SetRelativeLocationAndRotation", inp={"self": ns, "NewLocation": "@grl.RelativeLocation", "NewRotation": "@grr.RelativeRotation", "bSweep": "false", "bTeleport": "true"})
    g.call("srs", E_SCENEC, "SetRelativeScale3D", inp={"self": ns, "NewScale3D": "@grs.RelativeScale3D"})
    sh, st = copy_materials(g, "s_", "@cst.AsStatic Mesh Component", ns)
    g.chain("entry", "ssk", "sb", mh); g.chain(mt, "fmn"); g.chain("fmn", "smv"); g.chain("fmn:Completed", "scmp", "fc")   # morph names and the component list are pure
    g.chain("fc", "bok", "bk", "nk", "ksk", "kmp", kh); g.chain("bk:else", "bst", "ns", "ssm", "att", "srl", "srs", sh)
    return fn("Copy From", [param("source", "object:" + E_CHAR)], graph=g)


def f_setup_body():
    """After the body mesh is set: the snapshot ABP of the mesh's skeleton (tried in turn until an anim instance exists - the engine
    drops one whose target skeleton is not the mesh's), collision profile Ragdoll (clicks hit it frozen, too)."""
    g = G(); g.get("gb", "Body"); body = "@gb.Body"
    g.call("sac", E_SKM, "SetAnimClass", inp={"self": body, "NewClass": RAG_ABP + ".ABP_AltUIRagdoll_C"}); ends = ["sac"]
    for i, a in enumerate(RAG_ABPS[1:]):
        g.call("gai%d" % i, E_SKM, "GetAnimInstance", inp={"self": body}); g.call("vai%d" % i, K_SYS, "IsValid", inp={"Object": "@gai%d.ReturnValue" % i}); g.branch("bai%d" % i, "@vai%d.ReturnValue" % i)
        g.call("sa%d" % i, E_SKM, "SetAnimClass", inp={"self": body, "NewClass": "%s.%s_C" % (a, a.rsplit("/", 1)[1])})
        for e in ends: g.chain(e, "bai%d" % i)
        g.chain("bai%d:else" % i, "sa%d" % i); ends = ["bai%d" % i, "sa%d" % i]
    g.call("scp", E_PRIMC, "SetCollisionProfileName", inp={"self": body, "InCollisionProfileName": "Ragdoll", "bUpdateOverlaps": "true"})
    g.chain("entry", "sac")
    for e in ends: g.chain(e, "scp")
    return fn("Setup Body", graph=g)


def f_load_path():
    """An asset by its path string (soft path, blocking load); None when the path is empty or gone."""
    g = G(); g.call("sp", K_SYS, "MakeSoftObjectPath", inp={"PathString": "@entry.path"}); g.call("sr", K_SYS, "Conv_SoftObjPathToSoftObjRef", inp={"SoftObjectPath": "@sp.ReturnValue"})
    g.call("ld", K_SYS, "LoadAsset_Blocking", inp={"Asset": "@sr.ReturnValue"}); g.link("ld.ReturnValue", "return.object"); g.chain("entry", "ld", "return")
    return fn("Load Path", [param("path", "string")], [param("object", "object:/Script/CoreUObject.Object")], graph=g)


def f_collect_mats():
    """The material slots of a mesh: a dynamic instance as its parent + every scalar / vector / texture parameter it holds, anything else as its path."""
    g = G(); g.get("gm0", "TmpMats"); g.call("cm", K_ARR, "Array_Clear", inp={"TargetArray": "@gm0.TmpMats"})
    g.call("ms", E_MESHC, "GetMaterials", inp={"self": "@entry.mesh"}); g.foreach("fm", "@ms.ReturnValue")
    g.cast("cd", E_MIDC, "@fm.Array Element"); g.call("vd", K_SYS, "IsValid", inp={"Object": "@cd.AsMaterial Instance Dynamic"}); g.branch("bd", "@vd.ReturnValue")
    clears = []
    for v in ("TmpSN", "TmpSV", "TmpVN", "TmpVV", "TmpTN", "TmpTP"):
        g.get("gc" + v, v); g.call("c" + v, K_ARR, "Array_Clear", inp={"TargetArray": "@gc%s.%s" % (v, v)}); clears.append("c" + v)
    mid = "@cd.AsMaterial Instance Dynamic"
    loops = []
    for k, arr, s_val, nv, vv, conv in (("s", "ScalarParameterValues", "/Script/Engine.ScalarParameterValue", "TmpSN", "TmpSV", None),
                                        ("v", "VectorParameterValues", "/Script/Engine.VectorParameterValue", "TmpVN", "TmpVV", None),
                                        ("t", "TextureParameterValues", "/Script/Engine.TextureParameterValue", "TmpTN", "TmpTP", "path")):
        g.get(k + "ga", arr, cls=E_MI); g.link("cd.AsMaterial Instance Dynamic", k + "ga.self"); g.foreach(k + "fe", "@%sga.%s" % (k, arr))
        g.brk(k + "br", s_val, "@%sfe.Array Element" % k); g.brk(k + "bi", "/Script/Engine.MaterialParameterInfo", "@%sbr.ParameterInfo" % k)
        g.get(k + "gn", nv); g.call(k + "an", K_ARR, "Array_Add", inp={"TargetArray": "@%sgn.%s" % (k, nv), "NewItem": "@%sbi.Name" % k})
        val = "@%sbr.ParameterValue" % k
        if conv: g.call(k + "pn", K_SYS, "GetPathName", inp={"Object": val}); val = "@%spn.ReturnValue" % k
        g.get(k + "gv", vv); g.call(k + "av", K_ARR, "Array_Add", inp={"TargetArray": "@%sgv.%s" % (k, vv), "NewItem": val})
        g.chain(k + "fe", k + "an", k + "av"); loops.append(k + "fe")
    g.get("gpar", "Parent", cls=E_MI); g.link("cd.AsMaterial Instance Dynamic", "gpar.self"); g.call("ppn", K_SYS, "GetPathName", inp={"Object": "@gpar.Parent"})
    mk = {v: "@g%s2.%s" % (v, v) for v in ("TmpSN", "TmpSV", "TmpVN", "TmpVV", "TmpTN", "TmpTP")}
    for v in mk: g.get("g%s2" % v, v)
    g.make("md", S_RAGMAT, Path="@ppn.ReturnValue", Dynamic="true", ScalarNames=mk["TmpSN"], ScalarValues=mk["TmpSV"], VectorNames=mk["TmpVN"], VectorValues=mk["TmpVV"],
           TextureNames=mk["TmpTN"], TexturePaths=mk["TmpTP"])
    g.get("gm1", "TmpMats"); g.call("ad", K_ARR, "Array_Add", inp={"TargetArray": "@gm1.TmpMats", "NewItem": "@md.S_RagMat"})
    g.call("pn", K_SYS, "GetPathName", inp={"Object": "@fm.Array Element"}); g.make("mp", S_RAGMAT, Path="@pn.ReturnValue", Dynamic="false")
    g.get("gm2", "TmpMats"); g.call("ap", K_ARR, "Array_Add", inp={"TargetArray": "@gm2.TmpMats", "NewItem": "@mp.S_RagMat"})
    g.get("gm3", "TmpMats"); g.link("gm3.TmpMats", "return.mats")
    g.chain("entry", "cm", "fm"); g.chain("fm", "bd", *clears, loops[0]); g.chain(loops[0] + ":Completed", loops[1]); g.chain(loops[1] + ":Completed", loops[2]); g.chain(loops[2] + ":Completed", "ad")
    g.chain("bd:else", "ap"); g.chain("fm:Completed", "return")
    return fn("Collect Mats", [param("mesh", "object:" + E_MESHC)], [param("mats", "struct:" + S_RAGMAT, "array")], graph=g)


def f_apply_mats():
    """Collect Mats back onto a mesh: a dynamic instance anew from the parent with its parameters, anything else as it is."""
    g = G(); g.foreach("fm", "@entry.mats"); g.brk("bm", S_RAGMAT, "@fm.Array Element")
    g.n("lp", "call_self", function="Load Path", inp={"path": "@bm.Path"}); g.cast("cm", E_MATI, "@lp.object"); mat = "@cm.AsMaterial Interface"
    g.branch("bd", "@bm.Dynamic"); g.call("sm", E_PRIMC, "SetMaterial", inp={"self": "@entry.mesh", "ElementIndex": "@fm.Array Index", "Material": mat})
    g.call("dm", E_PRIMC, "CreateDynamicMaterialInstance", inp={"self": "@entry.mesh", "ElementIndex": "@fm.Array Index", "SourceMaterial": mat, "OptionalName": "None"})
    g.set("sdm", "TmpMid", inp={"TmpMid": "@dm.ReturnValue"})
    g.foreach("fs", "@bm.ScalarNames"); g.call("sv", K_ARR, "Array_Get", inp={"TargetArray": "@bm.ScalarValues", "Index": "@fs.Array Index"})
    g.get("gd1", "TmpMid"); g.call("ss", E_MIDC, "SetScalarParameterValue", inp={"self": "@gd1.TmpMid", "ParameterName": "@fs.Array Element", "Value": "@sv.Item"})
    g.foreach("fv", "@bm.VectorNames"); g.call("vv", K_ARR, "Array_Get", inp={"TargetArray": "@bm.VectorValues", "Index": "@fv.Array Index"})
    g.get("gd2", "TmpMid"); g.call("sv2", E_MIDC, "SetVectorParameterValue", inp={"self": "@gd2.TmpMid", "ParameterName": "@fv.Array Element", "Value": "@vv.Item"})
    g.foreach("ft", "@bm.TextureNames"); g.call("tv", K_ARR, "Array_Get", inp={"TargetArray": "@bm.TexturePaths", "Index": "@ft.Array Index"})
    g.n("tl", "call_self", function="Load Path", inp={"path": "@tv.Item"}); g.cast("tc", E_TEX, "@tl.object")
    g.get("gd3", "TmpMid"); g.call("st", E_MIDC, "SetTextureParameterValue", inp={"self": "@gd3.TmpMid", "ParameterName": "@ft.Array Element", "Value": "@tc.AsTexture"})
    g.chain("entry", "fm"); g.chain("fm", "lp", "bd", "dm", "sdm", "fs"); g.chain("bd:else", "sm"); g.chain("fs", "ss"); g.chain("fs:Completed", "fv"); g.chain("fv", "sv2"); g.chain("fv:Completed", "ft"); g.chain("ft", "tl", "st")
    return fn("Apply Mats", [param("mesh", "object:" + E_MESHC), param("mats", "struct:" + S_RAGMAT, "array")], graph=g)


def f_collect_parts():
    """The figure as data: the body, then every visible mesh hanging on it (clothes, and the meshes of attached actors - crystal, tank),
    each with the socket of the component that hangs on the body and its transform relative to that socket, and its materials."""
    g = G(); g.get("gp0", "TmpParts"); g.call("cp", K_ARR, "Array_Clear", inp={"TargetArray": "@gp0.TmpParts"})
    g.get("gb", "Body"); g.get("gbs", "SkeletalMesh", cls=E_SKIN); g.link("gb.Body", "gbs.self"); g.call("bpn", K_SYS, "GetPathName", inp={"Object": "@gbs.SkeletalMesh"})
    g.n("bcm", "call_self", function="Collect Mats", inp={"mesh": "@gb.Body"})
    g.make("bp", S_RAGPART, Mesh="@bpn.ReturnValue", Skeletal="true", Socket="None", Rel=ident_tf(g), Mats="@bcm.mats")
    g.get("gp1", "TmpParts"); g.call("ab", K_ARR, "Array_Add", inp={"TargetArray": "@gp1.TmpParts", "NewItem": "@bp.S_RagPart"})
    g.get("gb2", "Body"); g.call("ch", E_SCENEC, "GetChildrenComponents", inp={"self": "@gb2.Body", "bIncludeAllDescendants": "true"}); g.foreach("fc", "@ch.Children")
    g.cast("cmc", E_MESHC, "@fc.Array Element"); g.call("vmc", K_SYS, "IsValid", inp={"Object": "@cmc.AsMesh Component"})
    g.call("vis", E_SCENEC, "IsVisible", inp={"self": "@fc.Array Element"}); g.call("ok", K_MATH, "BooleanAND", inp={"A": "@vmc.ReturnValue", "B": "@vis.ReturnValue"}); g.branch("bok", "@ok.ReturnValue")
    # the component on the body this mesh hangs under (itself, or up to PART_UP parents up)
    g.set("sr0", "TmpRoot", inp={"TmpRoot": "@fc.Array Element"}); up = ["sr0"]
    for i in range(PART_UP):
        g.get("gr%d" % i, "TmpRoot"); g.call("pa%d" % i, E_SCENEC, "GetAttachParent", inp={"self": "@gr%d.TmpRoot" % i}); g.get("gb%d" % (i + 3), "Body")
        g.call("onb%d" % i, K_MATH, "EqualEqual_ObjectObject", inp={"A": "@pa%d.ReturnValue" % i, "B": "@gb%d.Body" % (i + 3)}); g.call("vpa%d" % i, K_SYS, "IsValid", inp={"Object": "@pa%d.ReturnValue" % i})
        g.call("nob%d" % i, K_MATH, "Not_PreBool", inp={"A": "@onb%d.ReturnValue" % i}); g.call("upq%d" % i, K_MATH, "BooleanAND", inp={"A": "@nob%d.ReturnValue" % i, "B": "@vpa%d.ReturnValue" % i})
        g.branch("bu%d" % i, "@upq%d.ReturnValue" % i); g.set("su%d" % i, "TmpRoot", inp={"TmpRoot": "@pa%d.ReturnValue" % i})
        for e in up: g.chain(e, "bu%d" % i)
        g.chain("bu%d" % i, "su%d" % i); up = ["su%d" % i, "bu%d:else" % i]
    g.get("grt", "TmpRoot"); g.call("sock", E_SCENEC, "GetAttachSocketName", inp={"self": "@grt.TmpRoot"})
    g.get("gb9", "Body"); g.call("stw", E_SCENEC, "GetSocketTransform", inp={"self": "@gb9.Body", "InSocketName": "@sock.ReturnValue", "TransformSpace": "RTS_World"})
    g.call("cw", E_SCENEC, "K2_GetComponentToWorld", inp={"self": "@fc.Array Element"}); g.call("rel", K_MATH, "MakeRelativeTransform", inp={"A": "@cw.ReturnValue", "RelativeTo": "@stw.ReturnValue"})
    g.cast("csk", E_SKIN, "@fc.Array Element"); g.call("isk", K_SYS, "IsValid", inp={"Object": "@csk.AsSkinned Mesh Component"})
    g.get("gsm", "SkeletalMesh", cls=E_SKIN); g.link("csk.AsSkinned Mesh Component", "gsm.self"); g.cast("cst", E_STM, "@fc.Array Element"); g.get("gst", "StaticMesh", cls=E_STM); g.link("cst.AsStatic Mesh Component", "gst.self")
    g.call("mo", K_MATH, "SelectObject", inp={"A": "@gsm.SkeletalMesh", "B": "@gst.StaticMesh", "bSelectA": "@isk.ReturnValue"}); g.call("mpn", K_SYS, "GetPathName", inp={"Object": "@mo.ReturnValue"})
    g.n("pcm", "call_self", function="Collect Mats", inp={"mesh": "@cmc.AsMesh Component"})
    g.make("pp", S_RAGPART, Mesh="@mpn.ReturnValue", Skeletal="@isk.ReturnValue", Socket="@sock.ReturnValue", Rel="@rel.ReturnValue", Mats="@pcm.mats")
    g.get("gp2", "TmpParts"); g.call("ap", K_ARR, "Array_Add", inp={"TargetArray": "@gp2.TmpParts", "NewItem": "@pp.S_RagPart"})
    g.get("gp3", "TmpParts"); g.link("gp3.TmpParts", "return.parts")
    g.chain("entry", "cp", "bcm", "ab", "fc"); g.chain("fc", "bok", "sr0")
    for e in up: g.chain(e, "pcm")
    g.chain("pcm", "ap"); g.chain("fc:Completed", "return")
    return fn("Collect Parts", [], [param("parts", "struct:" + S_RAGPART, "array")], graph=g)


def f_build_from_parts():
    """Collect Parts back into this (fresh) figure: body mesh + ABP + materials, then every other part as a new component - skeletal ones
    follow the body (master pose), static ones sit at their socket with their relative transform."""
    g = G(); g.call("p0", K_ARR, "Array_Get", inp={"TargetArray": "@entry.parts", "Index": "0"}); g.brk("b0", S_RAGPART, "@p0.Item")
    g.n("l0", "call_self", function="Load Path", inp={"path": "@b0.Mesh"}); g.cast("c0", E_SKMESH, "@l0.object")
    g.get("gb", "Body"); g.call("ssk", E_SKIN, "SetSkeletalMesh", inp={"self": "@gb.Body", "NewMesh": "@c0.AsSkeletal Mesh", "bReinitPose": "true"})
    g.n("sb", "call_self", function="Setup Body"); g.get("gb2", "Body"); g.n("am0", "call_self", function="Apply Mats", inp={"mesh": "@gb2.Body", "mats": "@b0.Mats"})
    g.foreach("fp", "@entry.parts"); g.call("gt0", K_MATH, "Greater_IntInt", inp={"A": "@fp.Array Index", "B": "0"}); g.branch("bgt", "@gt0.ReturnValue")
    g.brk("bp", S_RAGPART, "@fp.Array Element"); g.n("lp", "call_self", function="Load Path", inp={"path": "@bp.Mesh"}); g.branch("bsk", "@bp.Skeletal")
    # skeletal
    g.call("nk", E_ACTOR, "AddComponentByClass", inp={"Class": E_SKM, "bManualAttachment": "false", "RelativeTransform": ident_tf(g), "bDeferredFinish": "false"})
    g.cast("cnk", E_SKM, "@nk.ReturnValue"); nk = "@cnk.AsSkeletal Mesh Component"; g.cast("ckm", E_SKMESH, "@lp.object")
    g.call("ksk", E_SKIN, "SetSkeletalMesh", inp={"self": nk, "NewMesh": "@ckm.AsSkeletal Mesh", "bReinitPose": "true"})
    g.get("gb3", "Body"); g.call("kmp", E_SKIN, "SetMasterPoseComponent", inp={"self": nk, "NewMasterBoneComponent": "@gb3.Body", "bForceUpdate": "true"})
    g.n("amk", "call_self", function="Apply Mats", inp={"mesh": nk, "mats": "@bp.Mats"})
    # static
    g.call("ns", E_ACTOR, "AddComponentByClass", inp={"Class": E_STM, "bManualAttachment": "true", "RelativeTransform": ident_tf(g), "bDeferredFinish": "false"})
    g.cast("cns", E_STM, "@ns.ReturnValue"); ns = "@cns.AsStatic Mesh Component"; g.cast("csm", E_STMESH, "@lp.object")
    g.call("ssm", E_STM, "SetStaticMesh", inp={"self": ns, "NewMesh": "@csm.AsStatic Mesh"})
    g.call("srt", E_SCENEC, "K2_SetRelativeTransform", inp={"self": ns, "NewTransform": "@bp.Rel", "bSweep": "false", "bTeleport": "true"})
    g.get("gb4", "Body"); g.call("att", E_SCENEC, "K2_AttachToComponent", inp={"self": ns, "Parent": "@gb4.Body", "SocketName": "@bp.Socket", "LocationRule": "KeepRelative",
                                                                                "RotationRule": "KeepRelative", "ScaleRule": "KeepRelative", "bWeldSimulatedBodies": "false"})
    g.n("ams", "call_self", function="Apply Mats", inp={"mesh": ns, "mats": "@bp.Mats"})
    g.chain("entry", "l0", "ssk", "sb", "am0", "fp"); g.chain("fp", "bgt", "lp", "bsk", "nk", "ksk", "kmp", "amk"); g.chain("bsk:else", "ns", "ssm", "srt", "att", "ams")
    return fn("Build From Parts", [param("parts", "struct:" + S_RAGPART, "array")], graph=g)


def f_set_pose():
    """The pose the ABP shows while physics is off (also the one physics starts from when it comes on)."""
    g = G(); g.get("gb", "Body"); g.call("ai", E_SKM, "GetAnimInstance", inp={"self": "@gb.Body"}); prev = ["entry"]
    for i, a in enumerate(RAG_ABPS):   # whichever ABP of RAG_ABPS the mesh's skeleton took
        nm = a.rsplit("/", 1)[1]; pin = "As" + re.sub(r"(?<=[a-z0-9])(?=[A-Z])|_", " ", nm).replace("Alt U I", "Alt UI")
        g.cast("ca%d" % i, a, "@ai.ReturnValue", pure=False, miss="ignore")
        g.n("ss%d" % i, "set", var="Snap", cls=a, inp={"self": "@ca%d.%s" % (i, pin), "Snap": "@entry.snap"})
        for e in prev: g.chain(e, "ca%d" % i)
        g.chain("ca%d" % i, "ss%d" % i); prev = ["ss%d" % i, "ca%d:CastFailed" % i]
    return fn("Set Pose", [param("snap", "struct:" + S_POSE)], graph=g)


def f_activate():
    """Physics on, starting from the held pose; the locked joints get their constraints."""
    g = G(); g.get("gb", "Body"); g.call("sp", E_PRIMC, "SetSimulatePhysics", inp={"self": "@gb.Body", "bSimulate": "true"}); g.set("sa", "Active", inp={"Active": "true"})
    g.get("gj", "LockedJoints"); g.set("cj", "JointsLoop", inp={"JointsLoop": "@gj.LockedJoints"}); g.get("gjl", "JointsLoop"); g.foreach("fe", "@gjl.JointsLoop")
    g.n("ml", "call_self", function="Make Lock", inp={"bone": "@fe.Array Element"})
    # pinned parts (spec 2026-10-17): their constraints again, where the bones are now - a frozen figure moved took its pins along
    g.get("gpn", "Pinned"); g.set("cpl", "PinLoop", inp={"PinLoop": "@gpn.Pinned"}); g.get("gpl", "PinLoop"); g.foreach("fp", "@gpl.PinLoop")
    g.n("mp", "call_self", function="Make Pin", inp={"bone": "@fp.Array Element"})
    g.chain("entry", "sp", "sa", "cj", "fe"); g.chain("fe", "ml"); g.chain("fe:Completed", "cpl", "fp"); g.chain("fp", "mp"); return fn("Activate", graph=g)


def f_freeze():
    """The pose as it lies now (physics result) is held by the ABP, constraints go, physics off. Pose first: no frame in the
    reference pose."""
    g = G(); g.get("gb", "Body"); g.get("gpt", "PoseTmp"); g.call("sn", E_SKM, "SnapshotPose", inp={"self": "@gb.Body", "Snapshot": "@gpt.PoseTmp"})
    g.get("gpt2", "PoseTmp"); g.n("sp", "call_self", function="Set Pose", inp={"snap": "@gpt2.PoseTmp"})
    g.get("gl", "Locks"); g.call("lv", K_MAP, "Map_Values", inp={"TargetMap": "@gl.Locks"}); g.foreach("fe", "@lv.Values")
    g.call("dc", E_ACTC, "K2_DestroyComponent", inp={"self": "@fe.Array Element", "Object": "@fe.Array Element"})
    g.get("gl2", "Locks"); g.call("cl", K_MAP, "Map_Clear", inp={"TargetMap": "@gl2.Locks"})
    g.get("gb2", "Body"); g.call("off", E_PRIMC, "SetSimulatePhysics", inp={"self": "@gb2.Body", "bSimulate": "false"}); g.set("sa", "Active", inp={"Active": "false"})
    g.get("gb3", "Body"); g.call("grv", E_PRIMC, "SetEnableGravity", inp={"self": "@gb3.Body", "bGravityEnabled": "true"})   # a posed limb ran without it
    g.chain("entry", "sn", "sp", "lv", "fe"); g.chain("fe", "dc"); g.n("cpn", "call_self", function="Clear Pins"); g.set("sha", "HitActive", inp={"HitActive": "false"})   # frozen during a jolt (attackable): that pose, no Hit Back over it
    g.chain("fe:Completed", "cl", "cpn", "off", "sa", "grv", "sha")
    return fn("Freeze", graph=g)


def f_toggle_joint():
    """A joint in or out of LockedJoints; while active its constraint comes / goes with it."""
    g = G(); g.get("gj", "LockedJoints"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gj.LockedJoints", "ItemToFind": "@entry.bone"}); g.branch("bh", "@has.ReturnValue")
    g.get("gj2", "LockedJoints"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gj2.LockedJoints", "Item": "@entry.bone"}); g.n("dl", "call_self", function="Drop Lock", inp={"bone": "@entry.bone"})
    g.get("gj3", "LockedJoints"); g.call("ad", K_ARR, "Array_Add", inp={"TargetArray": "@gj3.LockedJoints", "NewItem": "@entry.bone"})
    g.get("ga", "Active"); g.branch("ba", "@ga.Active"); g.n("ml", "call_self", function="Make Lock", inp={"bone": "@entry.bone"})
    g.n("rmk", "call_self", function="Refresh Markers")
    g.chain("entry", "bh", "rm", "dl", "rmk"); g.chain("bh:else", "ad", "ba", "ml", "rmk"); g.chain("ba:else", "rmk"); return fn("Toggle Joint", [param("bone", "name")], graph=g)


def f_lock_all():
    """Every joint of `joints` that is free gets locked (Toggle Joint, so an active figure gets the constraints at once)."""
    g = G(); g.set("cp", "JointsLoop", inp={"JointsLoop": "@entry.joints"}); g.get("gl", "JointsLoop"); g.foreach("fe", "@gl.JointsLoop")
    g.get("gj", "LockedJoints"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gj.LockedJoints", "ItemToFind": "@fe.Array Element"})
    g.get("gb", "Body"); g.call("bi", E_SKIN, "GetBoneIndex", inp={"self": "@gb.Body", "BoneName": "@fe.Array Element"}); g.call("nob", K_MATH, "EqualEqual_IntInt", inp={"A": "@bi.ReturnValue", "B": "-1"})
    g.call("skip", K_MATH, "BooleanOR", inp={"A": "@has.ReturnValue", "B": "@nob.ReturnValue"}); g.branch("b", "@skip.ReturnValue")   # locked already, or a bone this mesh has not
    g.n("tj", "call_self", function="Toggle Joint", inp={"bone": "@fe.Array Element"})
    g.chain("entry", "cp", "fe"); g.chain("fe", "b"); g.chain("b:else", "tj"); return fn("Lock All", [param("joints", "name", "array")], graph=g)


def f_free_all():
    g = G(); g.get("gj", "LockedJoints"); g.set("cp", "JointsLoop", inp={"JointsLoop": "@gj.LockedJoints"}); g.get("gl", "JointsLoop"); g.foreach("fe", "@gl.JointsLoop")
    g.n("tj", "call_self", function="Toggle Joint", inp={"bone": "@fe.Array Element"})
    g.chain("entry", "cp", "fe"); g.chain("fe", "tj"); return fn("Free All", graph=g)


def f_toggle_loose():
    """Posing a frozen figure: a joint in or out of LooseJoints. Dragging a bone below a loose joint moves that chain only (Loosen Below)."""
    g = G(); g.get("gj", "LooseJoints"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gj.LooseJoints", "ItemToFind": "@entry.bone"}); g.branch("bh", "@has.ReturnValue")
    g.get("gj2", "LooseJoints"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gj2.LooseJoints", "Item": "@entry.bone"})
    g.get("gj3", "LooseJoints"); g.call("ad", K_ARR, "Array_Add", inp={"TargetArray": "@gj3.LooseJoints", "NewItem": "@entry.bone"})
    g.n("rmk", "call_self", function="Refresh Markers")
    g.chain("entry", "bh", "rm", "rmk"); g.chain("bh:else", "ad", "rmk"); return fn("Toggle Loose", [param("bone", "name")], graph=g)


def f_loose_root():
    """The loose joint a clicked bone hangs on: the bone itself or the first of up to LOOSE_UP parents in LooseJoints; None if none."""
    g = G(); g.set("s0", "LooseWalk", inp={"LooseWalk": "@entry.bone"}); g.set("f0", "LooseFound", inp={"LooseFound": "None"}); prev = ["s0", "f0"]; ends = []
    for i in range(LOOSE_UP + 1):
        g.get("gw%d" % i, "LooseWalk"); g.get("gj%d" % i, "LooseJoints")
        g.call("has%d" % i, K_ARR, "Array_Contains", inp={"TargetArray": "@gj%d.LooseJoints" % i, "ItemToFind": "@gw%d.LooseWalk" % i}); g.branch("b%d" % i, "@has%d.ReturnValue" % i)
        g.get("gw%db" % i, "LooseWalk"); g.set("sf%d" % i, "LooseFound", inp={"LooseFound": "@gw%db.LooseWalk" % i})
        g.get("gb%d" % i, "Body"); g.call("pb%d" % i, E_SKIN, "GetParentBone", inp={"self": "@gb%d.Body" % i, "BoneName": "@gw%d.LooseWalk" % i}); g.set("up%d" % i, "LooseWalk", inp={"LooseWalk": "@pb%d.ReturnValue" % i})
        g.chain(prev[-1], "b%d" % i); g.chain("b%d" % i, "sf%d" % i); ends.append("sf%d" % i); g.chain("b%d:else" % i, "up%d" % i); prev.append("up%d" % i)
    g.get("gf", "LooseFound"); g.link("gf.LooseFound", "return.root")
    for e in ends + [prev[-1]]: g.chain(e, "return")
    g.chain("entry", "s0", "f0")
    return fn("Loose Root", [param("bone", "name")], [param("root", "name")], graph=g)


def f_loosen_below():
    """Only the chain below `root` simulates, without gravity (the rest stays held by the ABP pose): drag it, Freeze takes the result.
    Inside the chain only the loose joints bend: every other simulating body below root gets a lock to its parent (Make Lock; Freeze
    removes them) - otherwise e.g. the wrist flops when the elbow is posed."""
    g = G(); g.get("gb", "Body"); g.call("gr", E_PRIMC, "SetEnableGravity", inp={"self": "@gb.Body", "bGravityEnabled": "false"})
    g.get("gb2", "Body"); g.call("sb", E_SKM, "SetAllBodiesBelowSimulatePhysics", inp={"self": "@gb2.Body", "InBoneName": "@entry.root", "bNewSimulate": "true", "bIncludeSelf": "true"})
    prev = ["sb"]
    for i, b in enumerate(POSE_RIGID):
        g.get("gs%d" % i, "Body"); g.call("sim%d" % i, E_SCENEC, "IsSimulatingPhysics", inp={"self": "@gs%d.Body" % i, "BoneName": b})
        g.get("gl%d" % i, "LooseJoints"); g.lit_name("ln%d" % i, b); g.call("lo%d" % i, K_ARR, "Array_Contains", inp={"TargetArray": "@gl%d.LooseJoints" % i, "ItemToFind": "@ln%d.ReturnValue" % i}); g.call("nl%d" % i, K_MATH, "Not_PreBool", inp={"A": "@lo%d.ReturnValue" % i})
        g.call("nr%d" % i, K_MATH, "NotEqual_NameName", inp={"A": "@entry.root", "B": b})
        g.call("a%d" % i, K_MATH, "BooleanAND", inp={"A": "@sim%d.ReturnValue" % i, "B": "@nl%d.ReturnValue" % i}); g.call("c%d" % i, K_MATH, "BooleanAND", inp={"A": "@a%d.ReturnValue" % i, "B": "@nr%d.ReturnValue" % i})
        g.branch("b%d" % i, "@c%d.ReturnValue" % i); g.n("ml%d" % i, "call_self", function="Make Lock", inp={"bone": b})
        for e in prev: g.chain(e, "b%d" % i)
        g.chain("b%d" % i, "ml%d" % i); prev = ["b%d:else" % i, "ml%d" % i]
    g.chain("entry", "gr", "sb"); return fn("Loosen Below", [param("root", "name")], graph=g)


def f_drop_lock():
    g = G(); g.get("gl", "Locks"); g.call("fl", K_MAP, "Map_Find", inp={"TargetMap": "@gl.Locks", "Key": "@entry.bone"}); g.branch("bfl", "@fl.ReturnValue")
    g.call("dc", E_ACTC, "K2_DestroyComponent", inp={"self": "@fl.Value", "Object": "@fl.Value"})
    g.get("gl2", "Locks"); g.call("rm", K_MAP, "Map_Remove", inp={"TargetMap": "@gl2.Locks", "Key": "@entry.bone"})
    g.chain("entry", "bfl", "dc", "rm"); return fn("Drop Lock", [param("bone", "name")], graph=g)


def f_make_lock():
    """The joint between that bone and its parent body is locked in its current angle (a constraint between the two bodies, all
    three angular axes locked). A bone without a parent body (the root) gets none; an existing lock stays."""
    g = G(); g.get("gb", "Body")
    # the parent body: up the skeleton until a bone that really simulates (twist and helper bones have no body; a constraint to one
    # binds to the wrong body and throws the puppet), at most LOCK_UP steps
    g.call("p0", E_SKIN, "GetParentBone", inp={"self": "@gb.Body", "BoneName": "@entry.bone"}); g.set("sp0", "LockParent", inp={"LockParent": "@p0.ReturnValue"}); up = ["sp0"]
    for i in range(LOCK_UP):
        g.get("glp%d" % i, "LockParent"); g.get("gub%d" % i, "Body"); g.call("sim%d" % i, E_SCENEC, "IsSimulatingPhysics", inp={"self": "@gub%d.Body" % i, "BoneName": "@glp%d.LockParent" % i})
        g.call("non%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@glp%d.LockParent" % i, "B": "None"}); g.call("stop%d" % i, K_MATH, "BooleanOR", inp={"A": "@sim%d.ReturnValue" % i, "B": "@non%d.ReturnValue" % i})
        g.branch("bup%d" % i, "@stop%d.ReturnValue" % i)
        g.call("pu%d" % i, E_SKIN, "GetParentBone", inp={"self": "@gub%d.Body" % i, "BoneName": "@glp%d.LockParent" % i}); g.set("su%d" % i, "LockParent", inp={"LockParent": "@pu%d.ReturnValue" % i})
        g.chain(up[-1], "bup%d" % i); g.chain("bup%d:else" % i, "su%d" % i)   # GetParentBone is const -> pure; up.append("su%d" % i)
    g.get("glp", "LockParent"); g.get("gbs", "Body"); g.call("psim", E_SCENEC, "IsSimulatingPhysics", inp={"self": "@gbs.Body", "BoneName": "@glp.LockParent"}); g.branch("bhp", "@psim.ReturnValue")
    for i in range(LOCK_UP): g.chain("bup%d" % i, "bhp")
    g.chain(up[-1], "bhp")
    g.get("gl", "Locks"); g.call("fl", K_MAP, "Map_Find", inp={"TargetMap": "@gl.Locks", "Key": "@entry.bone"}); g.branch("bfl", "@fl.ReturnValue")
    g.call("nc", E_ACTOR, "AddComponentByClass", inp={"Class": E_CONSTR, "bManualAttachment": "true", "RelativeTransform": ident_tf(g), "bDeferredFinish": "false"})
    g.cast("cc", E_CONSTR, "@nc.ReturnValue"); c = "@cc.AsPhysics Constraint Component"
    g.get("gb2", "Body"); g.call("bl", E_SCENEC, "GetSocketLocation", inp={"self": "@gb2.Body", "InSocketName": "@entry.bone"})
    g.call("swl", E_SCENEC, "K2_SetWorldLocation", inp={"self": c, "NewLocation": "@bl.ReturnValue", "bSweep": "false", "bTeleport": "true"})
    g.get("gb3", "Body"); g.get("glpc", "LockParent")
    g.call("scc", E_CONSTR, "SetConstrainedComponents", inp={"self": c, "Component1": "@gb3.Body", "BoneName1": "@glpc.LockParent", "Component2": "@gb3.Body", "BoneName2": "@entry.bone"})
    g.call("s1", E_CONSTR, "SetAngularSwing1Limit", inp={"self": c, "MotionType": "ACM_Locked", "Swing1LimitAngle": "0.0"})
    g.call("s2", E_CONSTR, "SetAngularSwing2Limit", inp={"self": c, "MotionType": "ACM_Locked", "Swing2LimitAngle": "0.0"})
    g.call("tw", E_CONSTR, "SetAngularTwistLimit", inp={"self": c, "ConstraintType": "ACM_Locked", "TwistLimitAngle": "0.0"})
    g.get("gl3", "Locks"); g.call("ad", K_MAP, "Map_Add", inp={"TargetMap": "@gl3.Locks", "Key": "@entry.bone", "Value": c})
    g.chain("entry", "sp0"); g.chain("bhp", "bfl"); g.chain("bfl:else", "nc", "swl", "scc", "s1", "s2", "tw", "ad")
    return fn("Make Lock", [param("bone", "name")], graph=g)


# ---- pinned in the air (spec 2026-10-17-ragdoll-festhalten-design): a bone held by a constraint against the world ----
def f_make_pin():
    """The constraint for a pinned bone: at the bone's place now, against the world (no second component), all six axes locked.
    An existing one stays."""
    g = G(); g.get("gp", "Pins"); g.call("fp", K_MAP, "Map_Find", inp={"TargetMap": "@gp.Pins", "Key": "@entry.bone"}); g.branch("bfp", "@fp.ReturnValue")
    g.call("nc", E_ACTOR, "AddComponentByClass", inp={"Class": E_CONSTR, "bManualAttachment": "true", "RelativeTransform": ident_tf(g), "bDeferredFinish": "false"})
    g.cast("cc", E_CONSTR, "@nc.ReturnValue"); c = "@cc.AsPhysics Constraint Component"
    g.get("gb", "Body"); g.call("bt", E_SCENEC, "GetSocketTransform", inp={"self": "@gb.Body", "InSocketName": "@entry.bone", "TransformSpace": "RTS_World"})
    g.call("swt", E_SCENEC, "K2_SetWorldTransform", inp={"self": c, "NewTransform": "@bt.ReturnValue", "bSweep": "false", "bTeleport": "true"})
    g.call("lx", E_CONSTR, "SetLinearXLimit", inp={"self": c, "ConstraintType": "LCM_Locked", "LimitSize": "0.0"})
    g.call("ly", E_CONSTR, "SetLinearYLimit", inp={"self": c, "ConstraintType": "LCM_Locked", "LimitSize": "0.0"})
    g.call("lz", E_CONSTR, "SetLinearZLimit", inp={"self": c, "ConstraintType": "LCM_Locked", "LimitSize": "0.0"})
    g.call("s1", E_CONSTR, "SetAngularSwing1Limit", inp={"self": c, "MotionType": "ACM_Locked", "Swing1LimitAngle": "0.0"})
    g.call("s2", E_CONSTR, "SetAngularSwing2Limit", inp={"self": c, "MotionType": "ACM_Locked", "Swing2LimitAngle": "0.0"})
    g.call("tw", E_CONSTR, "SetAngularTwistLimit", inp={"self": c, "ConstraintType": "ACM_Locked", "TwistLimitAngle": "0.0"})
    g.get("gb2", "Body"); g.call("scc", E_CONSTR, "SetConstrainedComponents", inp={"self": c, "Component1": "@gb2.Body", "BoneName1": "@entry.bone", "Component2": "None", "BoneName2": "None"})
    g.get("gp2", "Pins"); g.call("ad", K_MAP, "Map_Add", inp={"TargetMap": "@gp2.Pins", "Key": "@entry.bone", "Value": c})
    g.chain("entry", "bfp"); g.chain("bfp:else", "nc", "swt", "lx", "ly", "lz", "s1", "s2", "tw", "scc", "ad")
    return fn("Make Pin", [param("bone", "name")], graph=g)


def f_pin():
    """Pin a bone of the active figure where it is now (Rag Pin Grab, after letting go of the handle)."""
    g = G(); g.get("gn", "Pinned"); g.call("au", K_ARR, "Array_AddUnique", inp={"TargetArray": "@gn.Pinned", "NewItem": "@entry.bone"})
    g.n("mp", "call_self", function="Make Pin", inp={"bone": "@entry.bone"}); g.n("rm", "call_self", function="Refresh Markers")
    g.chain("entry", "au", "mp", "rm"); return fn("Pin", [param("bone", "name")], graph=g)


def f_unpin():
    """A pinned bone is free again (grabbing it does this)."""
    g = G(); g.get("gp", "Pins"); g.call("fp", K_MAP, "Map_Find", inp={"TargetMap": "@gp.Pins", "Key": "@entry.bone"}); g.branch("bfp", "@fp.ReturnValue")
    g.call("dc", E_ACTC, "K2_DestroyComponent", inp={"self": "@fp.Value", "Object": "@fp.Value"})
    g.get("gp2", "Pins"); g.call("mr", K_MAP, "Map_Remove", inp={"TargetMap": "@gp2.Pins", "Key": "@entry.bone"})
    g.get("gn", "Pinned"); g.call("ar", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gn.Pinned", "Item": "@entry.bone"}); g.n("rm", "call_self", function="Refresh Markers")
    g.chain("entry", "bfp", "dc", "mr", "ar"); g.chain("bfp:else", "ar"); g.chain("ar", "rm")
    return fn("Unpin", [param("bone", "name")], graph=g)


def f_clear_pins():
    """Every pin constraint goes; the names in Pinned stay (Freeze; Activate makes them again)."""
    g = G(); g.get("gp", "Pins"); g.call("mv", K_MAP, "Map_Values", inp={"TargetMap": "@gp.Pins"}); g.foreach("fe", "@mv.Values")
    g.call("dc", E_ACTC, "K2_DestroyComponent", inp={"self": "@fe.Array Element", "Object": "@fe.Array Element"})
    g.get("gp2", "Pins"); g.call("cl", K_MAP, "Map_Clear", inp={"TargetMap": "@gp2.Pins"})
    g.chain("entry", "mv", "fe"); g.chain("fe", "dc"); g.chain("fe:Completed", "cl"); return fn("Clear Pins", graph=g)


def f_unpin_all():
    """Link "release all": no pins any more."""
    g = G(); g.n("cp", "call_self", function="Clear Pins"); g.get("gn", "Pinned"); g.call("cl", K_ARR, "Array_Clear", inp={"TargetArray": "@gn.Pinned"})
    g.n("rm", "call_self", function="Refresh Markers"); g.chain("entry", "cp", "cl", "rm"); return fn("Unpin All", graph=g)


def mark_sphere(g, p, mat, scale, bone_pin, mids="MarkerMids"):
    """One sphere component on bone `bone_pin`: attached, fixed size, mesh + own MID, query-only as Destructible, hidden, no shadow.
    Leaves it in MarkTmp; returns the exec ids."""
    g.call(p + "nc", E_ACTOR, "AddComponentByClass", inp={"Class": E_SMC, "bManualAttachment": "true", "RelativeTransform": ident_tf(g), "bDeferredFinish": "false"})
    g.cast(p + "cs", E_SMC, "@%snc.ReturnValue" % p); g.set(p + "st", "MarkTmp", inp={"MarkTmp": "@%scs.AsStatic Mesh Component" % p}); m = "@%sgm.MarkTmp" % p
    g.get(p + "gm", "MarkTmp"); g.get(p + "gb", "Body")
    g.call(p + "at", E_SCENEC, "K2_AttachToComponent", inp={"self": m, "Parent": "@%sgb.Body" % p, "SocketName": bone_pin, "LocationRule": "SnapToTarget", "RotationRule": "SnapToTarget", "ScaleRule": "KeepWorld", "bWeldSimulatedBodies": "false"})
    g.call(p + "ab", E_SCENEC, "SetAbsolute", inp={"self": m, "bNewAbsoluteLocation": "false", "bNewAbsoluteRotation": "false", "bNewAbsoluteScale": "true"})
    g.call(p + "sc", E_SCENEC, "SetWorldScale3D", inp={"self": m, "NewScale": "(X=%s,Y=%s,Z=%s)" % (scale, scale, scale)})
    g.call(p + "sm", E_SMC, "SetStaticMesh", inp={"self": m, "NewMesh": MARK_MESH}); g.call(p + "mt", E_PRIMC, "SetMaterial", inp={"self": m, "ElementIndex": "0", "Material": mat})
    g.call(p + "md", E_PRIMC, "CreateDynamicMaterialInstance", inp={"self": m, "ElementIndex": "0", "SourceMaterial": "None", "OptionalName": "None"})
    g.get(p + "gmi", mids); g.call(p + "ami", K_ARR, "Array_Add", inp={"TargetArray": "@%sgmi.%s" % (p, mids), "NewItem": "@%smd.ReturnValue" % p})
    g.call(p + "ce", E_PRIMC, "SetCollisionEnabled", inp={"self": m, "NewType": "NoCollision"})
    g.call(p + "co", E_PRIMC, "SetCollisionObjectType", inp={"self": m, "Channel": "ECC_Destructible"})
    g.call(p + "cr", E_PRIMC, "SetCollisionResponseToAllChannels", inp={"self": m, "NewResponse": "ECR_Ignore"})
    g.call(p + "sh", E_PRIMC, "SetCastShadow", inp={"self": m, "NewCastShadow": "false"})
    g.call(p + "vi", E_SCENEC, "SetVisibility", inp={"self": m, "bNewVisibility": "false", "bPropagateToChildren": "false"})
    return [p + "nc", p + "st", p + "at", p + "ab", p + "sc", p + "sm", p + "mt", p + "md", p + "ami", p + "ce", p + "co", p + "cr", p + "sh", p + "vi"]


def f_build_markers():
    """Once per figure (Show Markers builds on first use): a sphere per MARKER_BONES bone this skeleton has (M_JointMarker decides how
    strong it shows); it also takes the clicks (Rag Pick). Arrays in step: MarkerBones[i], Markers[i], MarkerMids[i]."""
    g = G(); g.n("ba", "make_array", count=len(MARKER_BONES), type="name", inp={"[%d]" % i: g.lit_name("mb%d" % i, b) for i, b in enumerate(MARKER_BONES)})
    g.foreach("fe", "@ba.Array"); g.get("gb", "Body"); g.call("bi", E_SKIN, "GetBoneIndex", inp={"self": "@gb.Body", "BoneName": "@fe.Array Element"})
    g.call("hb", K_MATH, "NotEqual_IntInt", inp={"A": "@bi.ReturnValue", "B": "-1"}); g.branch("bh", "@hb.ReturnValue")
    g.get("gmb", "MarkerBones"); g.call("amb", K_ARR, "Array_Add", inp={"TargetArray": "@gmb.MarkerBones", "NewItem": "@fe.Array Element"})
    sph = mark_sphere(g, "h", MARK_MAT, MARK_SCALE, "@fe.Array Element")
    g.get("ghc", "Markers"); g.get("ght", "MarkTmp"); g.call("ahc", K_ARR, "Array_Add", inp={"TargetArray": "@ghc.Markers", "NewItem": "@ght.MarkTmp"})
    g.n("na", "make_array", count=len(MARKER_BONES), type="float", inp={"[%d]" % i: str(float(MARK_NEAR[b])) for i, b in enumerate(MARKER_BONES)})
    g.call("ng", K_ARR, "Array_Get", inp={"TargetArray": "@na.Array", "Index": "@fe.Array Index"}); g.call("fr", K_MATH, "Add_FloatFloat", inp={"A": "@ng.Item", "B": str(MARK_BAND)})
    g.call("pn", E_MIDC, "SetScalarParameterValue", inp={"self": "@hmd.ReturnValue", "ParameterName": "Near", "Value": "@ng.Item"})
    g.call("pf", E_MIDC, "SetScalarParameterValue", inp={"self": "@hmd.ReturnValue", "ParameterName": "Far", "Value": "@fr.ReturnValue"})
    g.call("pp", E_MIDC, "SetScalarParameterValue", inp={"self": "@hmd.ReturnValue", "ParameterName": "Pale", "Value": str(MARK_PALE)})
    g.set("sbt", "MarkersBuilt", inp={"MarkersBuilt": "true"})
    g.chain("entry", "fe"); g.chain("fe", "bh", "amb", *sph, "ahc", "pn", "pf", "pp"); g.chain("fe:Completed", "sbt")
    return fn("Build Markers", graph=g)


def f_show_markers():
    """Markers on / off (Apply Rag Markers): built on first use; hidden ones take no clicks. Colours follow the state (Refresh Markers)."""
    g = G(); g.get("gbt", "MarkersBuilt"); g.call("nb", K_MATH, "Not_PreBool", inp={"A": "@gbt.MarkersBuilt"}); g.call("nd", K_MATH, "BooleanAND", inp={"A": "@nb.ReturnValue", "B": "@entry.on"})
    g.branch("bb", "@nd.ReturnValue"); g.n("bm", "call_self", function="Build Markers")
    g.get("gh", "Markers"); g.foreach("fh", "@gh.Markers")
    g.call("vh", E_SCENEC, "SetVisibility", inp={"self": "@fh.Array Element", "bNewVisibility": "@entry.on", "bPropagateToChildren": "false"})
    g.branch("bon", "@entry.on")
    g.call("cq", E_PRIMC, "SetCollisionEnabled", inp={"self": "@fh.Array Element", "NewType": "QueryOnly"})
    g.call("cn", E_PRIMC, "SetCollisionEnabled", inp={"self": "@fh.Array Element", "NewType": "NoCollision"})
    g.n("rm", "call_self", function="Refresh Markers")
    g.n("sd", "call_self", function="Show Details", inp={"on": "@entry.on"})   # fingers and eyes (spec 2026-10-26)
    g.chain("entry", "bb", "bm", "fh"); g.chain("bb:else", "fh"); g.chain("fh", "vh", "bon", "cq"); g.chain("bon:else", "cn"); g.chain("fh:Completed", "rm", "sd")
    return fn("Show Markers", [param("on", "bool")], graph=g)


def f_refresh_markers():
    """Every marker in the colour of its bone's state: pinned blue, locked red, loose green, else grey."""
    g = G(); g.get("gmb", "MarkerBones"); g.foreach("fe", "@gmb.MarkerBones"); b = "@fe.Array Element"
    g.get("gpn", "Pinned"); g.call("ip", K_ARR, "Array_Contains", inp={"TargetArray": "@gpn.Pinned", "ItemToFind": b})
    g.get("glk", "LockedJoints"); g.call("il", K_ARR, "Array_Contains", inp={"TargetArray": "@glk.LockedJoints", "ItemToFind": b})
    g.get("glo", "LooseJoints"); g.call("io", K_ARR, "Array_Contains", inp={"TargetArray": "@glo.LooseJoints", "ItemToFind": b})
    g.call("c1", K_MATH, "SelectColor", inp={"A": MARK_COLORS["loose"], "B": MARK_COLORS["plain"], "bPickA": "@io.ReturnValue"})
    g.call("c2", K_MATH, "SelectColor", inp={"A": MARK_COLORS["locked"], "B": "@c1.ReturnValue", "bPickA": "@il.ReturnValue"})
    g.call("c3", K_MATH, "SelectColor", inp={"A": MARK_COLORS["pinned"], "B": "@c2.ReturnValue", "bPickA": "@ip.ReturnValue"})
    g.get("gm1", "MarkerMids"); g.call("m1", K_ARR, "Array_Get", inp={"TargetArray": "@gm1.MarkerMids", "Index": "@fe.Array Index"})
    g.call("v1", E_MIDC, "SetVectorParameterValue", inp={"self": "@m1.Item", "ParameterName": "Color", "Value": "@c3.ReturnValue"})
    g.chain("entry", "fe"); g.chain("fe", "v1"); return fn("Refresh Markers", graph=g)


# ---- fingers and eyes (spec 2026-10-26-ragdoll-finger-augen-design): fine spheres up close, only on Jodi's skeleton ----
def f_has_detail():
    """Jodi's skeleton (Jodi copies, NPC women): the mesh has the lids and the fingers the data was measured on."""
    g = G(); g.get("gb", "Body"); g.call("bi1", E_SKIN, "GetBoneIndex", inp={"self": "@gb.Body", "BoneName": "Eye_L"})
    g.call("bi2", E_SKIN, "GetBoneIndex", inp={"self": "@gb.Body", "BoneName": "index_01_l"})
    g.call("h1", K_MATH, "NotEqual_IntInt", inp={"A": "@bi1.ReturnValue", "B": "-1"}); g.call("h2", K_MATH, "NotEqual_IntInt", inp={"A": "@bi2.ReturnValue", "B": "-1"})
    g.call("a", K_MATH, "BooleanAND", inp={"A": "@h1.ReturnValue", "B": "@h2.ReturnValue"}); g.link("a.ReturnValue", "return.yes"); g.chain("entry", "return")
    return fn("Has Detail", [], [param("yes", "bool")], graph=g, pure=True)


def detail_names(g, id="dn"):
    g.n(id, "make_array", count=len(DETAIL_BONES), type="name", inp={"[%d]" % i: g.lit_name("%sl%d" % (id, i), b) for i, b in enumerate(DETAIL_BONES)})
    return "@%s.Array" % id


def f_detail_kind():
    """0 no fine sphere's bone, 1 a finger joint, 2 a lid."""
    g = G(); arr = detail_names(g); g.call("fi", K_ARR, "Array_Find", inp={"TargetArray": arr, "ItemToFind": "@entry.bone"})
    g.call("ge", K_MATH, "GreaterEqual_IntInt", inp={"A": "@fi.ReturnValue", "B": "0"}); g.call("lf", K_MATH, "Less_IntInt", inp={"A": "@fi.ReturnValue", "B": str(len(FINGER_BONES))})
    g.call("fg", K_MATH, "BooleanAND", inp={"A": "@ge.ReturnValue", "B": "@lf.ReturnValue"}); g.call("el", K_MATH, "GreaterEqual_IntInt", inp={"A": "@fi.ReturnValue", "B": str(len(FINGER_BONES))})
    g.call("k1", K_MATH, "SelectInt", inp={"A": "1", "B": "0", "bPickA": "@fg.ReturnValue"}); g.call("k2", K_MATH, "SelectInt", inp={"A": "2", "B": "@k1.ReturnValue", "bPickA": "@el.ReturnValue"})
    g.link("k2.ReturnValue", "return.kind"); g.chain("entry", "return")
    return fn("Detail Kind", [param("bone", "name")], [param("kind", "int")], graph=g, pure=True)


def f_finger_of():
    """A finger joint's finger: side * 5 + (thumb 0 .. pinky 4)."""
    g = G(); arr = detail_names(g); g.call("fi", K_ARR, "Array_Find", inp={"TargetArray": arr, "ItemToFind": "@entry.bone"})
    g.call("d", K_MATH, "Divide_IntInt", inp={"A": "@fi.ReturnValue", "B": "3"}); g.link("d.ReturnValue", "return.finger"); g.chain("entry", "return")
    return fn("Finger Of", [param("bone", "name")], [param("finger", "int")], graph=g, pure=True)


def f_finger_tip_base():
    """World places of a finger's last joint (tip) and first joint (knuckle)."""
    g = G(); arr = detail_names(g); g.call("b3", K_MATH, "Multiply_IntInt", inp={"A": "@entry.finger", "B": "3"})
    g.call("i2", K_MATH, "Add_IntInt", inp={"A": "@b3.ReturnValue", "B": "2"})
    g.call("nt", K_ARR, "Array_Get", inp={"TargetArray": arr, "Index": "@i2.ReturnValue"}); g.call("nb", K_ARR, "Array_Get", inp={"TargetArray": arr, "Index": "@b3.ReturnValue"})
    g.get("gb", "Body"); g.call("lt", E_SCENEC, "GetSocketLocation", inp={"self": "@gb.Body", "InSocketName": "@nt.Item"})
    g.call("lb", E_SCENEC, "GetSocketLocation", inp={"self": "@gb.Body", "InSocketName": "@nb.Item"})
    g.link("lt.ReturnValue", "return.tip"); g.link("lb.ReturnValue", "return.base"); g.chain("entry", "return")
    return fn("Finger Tip Base", [param("finger", "int")], [param("tip", S_VEC), param("base", S_VEC)], graph=g, pure=True)


def f_build_detail_markers():
    """Once (Show Details builds on first use): a small sphere on every finger joint and lid the mesh has. DetailBones / Details /
    DetailMids / DetailGroup in step (group 0 left hand, 1 right hand, 2 head); same object type as the joint spheres (Rag Pick finds them)."""
    g = G(); arr = detail_names(g, "ba")
    g.n("ga", "make_array", count=len(DETAIL_BONES), type="int", inp={"[%d]" % i: str(DETAIL_GROUP[b]) for i, b in enumerate(DETAIL_BONES)})
    g.foreach("fe", arr); g.get("gb", "Body"); g.call("bi", E_SKIN, "GetBoneIndex", inp={"self": "@gb.Body", "BoneName": "@fe.Array Element"})
    g.call("hb", K_MATH, "NotEqual_IntInt", inp={"A": "@bi.ReturnValue", "B": "-1"}); g.branch("bh", "@hb.ReturnValue")
    g.get("gdb", "DetailBones"); g.call("adb", K_ARR, "Array_Add", inp={"TargetArray": "@gdb.DetailBones", "NewItem": "@fe.Array Element"})
    g.call("gg", K_ARR, "Array_Get", inp={"TargetArray": "@ga.Array", "Index": "@fe.Array Index"})
    g.get("gdg", "DetailGroup"); g.call("adg", K_ARR, "Array_Add", inp={"TargetArray": "@gdg.DetailGroup", "NewItem": "@gg.Item"})
    sph = mark_sphere(g, "h", MARK_MAT, DETAIL_SCALE, "@fe.Array Element", mids="DetailMids")
    g.get("ghc", "Details"); g.get("ght", "MarkTmp"); g.call("ahc", K_ARR, "Array_Add", inp={"TargetArray": "@ghc.Details", "NewItem": "@ght.MarkTmp"})
    g.call("pn", E_MIDC, "SetScalarParameterValue", inp={"self": "@hmd.ReturnValue", "ParameterName": "Near", "Value": "1.0"})
    g.call("pf", E_MIDC, "SetScalarParameterValue", inp={"self": "@hmd.ReturnValue", "ParameterName": "Far", "Value": "3.0"})
    g.call("pp", E_MIDC, "SetScalarParameterValue", inp={"self": "@hmd.ReturnValue", "ParameterName": "Pale", "Value": str(MARK_PALE)})
    g.call("pc", E_MIDC, "SetVectorParameterValue", inp={"self": "@hmd.ReturnValue", "ParameterName": "Color", "Value": DETAIL_COLOR})
    g.set("sbt", "DetailBuilt", inp={"DetailBuilt": "true"})
    g.chain("entry", "fe"); g.chain("fe", "bh", "adb", "adg", *sph, "ahc", "pn", "pf", "pp", "pc"); g.chain("fe:Completed", "sbt")
    return fn("Build Detail Markers", graph=g)


def f_show_details():
    """With the joint spheres (Show Markers): on a figure with Jodi's skeleton the proximity check runs every DETAIL_TICK s; off: it
    stops and every fine sphere hides."""
    g = G(); g.n("hd", "call_self", function="Has Detail"); g.call("w", K_MATH, "BooleanAND", inp={"A": "@entry.on", "B": "@hd.yes"}); g.branch("bw", "@w.ReturnValue")
    g.get("gbt", "DetailBuilt"); g.branch("bbt", "@gbt.DetailBuilt"); g.n("bd", "call_self", function="Build Detail Markers")
    g.self_("me"); g.call("tm", K_SYS, "K2_SetTimer", inp={"Object": "@me.self", "FunctionName": "Detail Tick", "Time": str(DETAIL_TICK), "bLooping": "true"})
    g.n("dt", "call_self", function="Detail Tick")
    g.self_("me2"); g.call("ct", K_SYS, "K2_ClearTimer", inp={"Object": "@me2.self", "FunctionName": "Detail Tick"})
    g.get("gd", "Details"); g.foreach("fh", "@gd.Details")
    g.call("vh", E_SCENEC, "SetVisibility", inp={"self": "@fh.Array Element", "bNewVisibility": "false", "bPropagateToChildren": "false"})
    g.call("cn", E_PRIMC, "SetCollisionEnabled", inp={"self": "@fh.Array Element", "NewType": "NoCollision"})
    g.chain("entry", "bw", "bbt", "tm", "dt"); g.chain("bbt:else", "bd", "tm"); g.chain("bw:else", "ct", "fh"); g.chain("fh", "vh", "cn")
    return fn("Show Details", [param("on", "bool")], graph=g)


def f_detail_tick():
    """Fine spheres of a group show (and take clicks) while the camera is within DETAIL_NEAR of its hand / head and the figure is
    frozen; the one being dragged (DetailHold) stays."""
    g = G(); g.call("cm", K_GS, "GetPlayerCameraManager", inp={"PlayerIndex": "0"}); g.call("cl", E_PCM, "GetCameraLocation", inp={"self": "@cm.ReturnValue"})
    g.get("ga", "Active"); g.call("na", K_MATH, "Not_PreBool", inp={"A": "@ga.Active"})
    for i, b in enumerate(GROUP_BONES):
        g.get("gb%d" % i, "Body"); g.call("sl%d" % i, E_SCENEC, "GetSocketLocation", inp={"self": "@gb%d.Body" % i, "InSocketName": b})
        g.call("d%d" % i, K_MATH, "Vector_Distance", inp={"V1": "@cl.ReturnValue", "V2": "@sl%d.ReturnValue" % i})
        g.call("n%d" % i, K_MATH, "Less_FloatFloat", inp={"A": "@d%d.ReturnValue" % i, "B": str(DETAIL_NEAR)})
        g.call("a%d" % i, K_MATH, "BooleanAND", inp={"A": "@n%d.ReturnValue" % i, "B": "@na.ReturnValue"})
    g.n("nr", "make_array", count=len(GROUP_BONES), type="bool", inp={"[%d]" % i: "@a%d.ReturnValue" % i for i in range(len(GROUP_BONES))})
    g.get("gd", "Details"); g.foreach("fe", "@gd.Details")
    g.get("gg", "DetailGroup"); g.call("gi", K_ARR, "Array_Get", inp={"TargetArray": "@gg.DetailGroup", "Index": "@fe.Array Index"})
    g.call("nv", K_ARR, "Array_Get", inp={"TargetArray": "@nr.Array", "Index": "@gi.Item"})
    g.get("gdb", "DetailBones"); g.call("bn", K_ARR, "Array_Get", inp={"TargetArray": "@gdb.DetailBones", "Index": "@fe.Array Index"})
    g.get("gh", "DetailHold"); g.call("hq", K_MATH, "EqualEqual_NameName", inp={"A": "@bn.Item", "B": "@gh.DetailHold"})
    g.call("vis", K_MATH, "BooleanOR", inp={"A": "@nv.Item", "B": "@hq.ReturnValue"})
    g.call("sv", E_SCENEC, "SetVisibility", inp={"self": "@fe.Array Element", "bNewVisibility": "@vis.ReturnValue", "bPropagateToChildren": "false"}); g.branch("bv", "@vis.ReturnValue")
    g.call("cq", E_PRIMC, "SetCollisionEnabled", inp={"self": "@fe.Array Element", "NewType": "QueryOnly"})
    g.call("cn", E_PRIMC, "SetCollisionEnabled", inp={"self": "@fe.Array Element", "NewType": "NoCollision"})
    g.chain("entry", "fe"); g.chain("fe", "sv", "bv", "cq"); g.chain("bv:else", "cn")
    return fn("Detail Tick", graph=g)


def f_detail_begin():
    """The held pose into DetailPose: Detail Put changes it bone by bone, Detail Commit shows it (several puts in one frame stay together)."""
    g = G(); g.get("gb", "Body"); g.get("gdp", "DetailPose"); g.call("sn", E_SKM, "SnapshotPose", inp={"self": "@gb.Body", "Snapshot": "@gdp.DetailPose"})
    g.chain("entry", "sn"); return fn("Detail Begin", graph=g)


def f_detail_put():
    """One bone's local rotation in DetailPose (its translation and scale stay); a bone the pose lacks: nothing."""
    g = G(); g.get("gdp", "DetailPose"); g.brk("bp", S_POSE, "@gdp.DetailPose")
    g.call("fi", K_ARR, "Array_Find", inp={"TargetArray": "@bp.BoneNames", "ItemToFind": "@entry.bone"}); g.call("ok", K_MATH, "GreaterEqual_IntInt", inp={"A": "@fi.ReturnValue", "B": "0"})
    g.branch("bok", "@ok.ReturnValue"); g.set("stl", "TmpLocal", inp={"TmpLocal": "@bp.LocalTransforms"})
    g.get("gl", "TmpLocal"); g.call("ot", K_ARR, "Array_Get", inp={"TargetArray": "@gl.TmpLocal", "Index": "@fi.ReturnValue"}); g.call("bt", K_MATH, "BreakTransform", inp={"InTransform": "@ot.Item"})
    g.call("mt", K_MATH, "MakeTransform", inp={"Location": "@bt.Location", "Rotation": "@entry.rot", "Scale": "@bt.Scale"})
    g.get("gl2", "TmpLocal"); g.call("st", K_ARR, "Array_Set", inp={"TargetArray": "@gl2.TmpLocal", "Index": "@fi.ReturnValue", "Item": "@mt.ReturnValue", "bSizeToFit": "false"})
    g.get("gl3", "TmpLocal"); g.make("ms", S_POSE, LocalTransforms="@gl3.TmpLocal", BoneNames="@bp.BoneNames", SkeletalMeshName="@bp.SkeletalMeshName", bIsValid="true")
    g.set("sdp", "DetailPose", inp={"DetailPose": "@ms.PoseSnapshot"})
    g.chain("entry", "bok", "stl", "st", "sdp"); return fn("Detail Put", [param("bone", "name"), param("rot", S_ROT)], graph=g)


def f_detail_commit():
    g = G(); g.get("gdp", "DetailPose"); g.n("sp", "call_self", function="Set Pose", inp={"snap": "@gdp.DetailPose"}); g.chain("entry", "sp")
    return fn("Detail Commit", graph=g)


def f_curl_rot():
    """A finger joint's local rotation: its base pose turned by `angle` about `axis` in its own space."""
    g = G(); g.call("d", K_MATH, "RotatorFromAxisAndAngle", inp={"Axis": "@entry.axis", "Angle": "@entry.angle"})
    g.call("c", K_MATH, "ComposeRotators", inp={"A": "@d.ReturnValue", "B": "@entry.ref"}); g.link("c.ReturnValue", "return.rot"); g.chain("entry", "return")
    return fn("Curl Rot", [param("ref", S_ROT), param("axis", S_VEC), param("angle", "float")], [param("rot", S_ROT)], graph=g, pure=True)


def f_lid_rot():
    """A lid's local rotation: `angle` about `axis` in its parent's space on top of the base pose (as the game's additive blink)."""
    g = G(); g.call("d", K_MATH, "RotatorFromAxisAndAngle", inp={"Axis": "@entry.axis", "Angle": "@entry.angle"})
    g.call("c", K_MATH, "ComposeRotators", inp={"A": "@entry.ref", "B": "@d.ReturnValue"}); g.link("c.ReturnValue", "return.rot"); g.chain("entry", "return")
    return fn("Lid Rot", [param("ref", S_ROT), param("axis", S_VEC), param("angle", "float")], [param("rot", S_ROT)], graph=g, pure=True)


def make_rot(g, id, r):
    """A wired rotator node (pitch, yaw, roll): a "(Pitch=..)" pin default cooks as zero, in a make_array as on a call_self pin
    (bytecode, 2026-10-26; "(X=..)" vectors survive)."""
    g.call(id, K_MATH, "MakeRotator", inp={"Roll": str(float(r[2])), "Pitch": str(float(r[0])), "Yaw": str(float(r[1]))}); return "@%s.ReturnValue" % id


def finger_tables(g):
    """FINGER_BONES as arrays (index = side * 15 + finger * 3 + joint): names an, base pose ar, curl axis ax, curl angle ad, spread angle as."""
    fb = FINGER_BONES
    g.n("an", "make_array", count=len(fb), type="name", inp={"[%d]" % i: g.lit_name("anl%d" % i, b) for i, b in enumerate(fb)})
    g.n("ar", "make_array", count=len(fb), type=S_ROT, inp={"[%d]" % i: make_rot(g, "arr%d" % i, REF_ROT[b]) for i, b in enumerate(fb)})
    g.n("ax", "make_array", count=len(fb), type=S_VEC, inp={"[%d]" % i: vec_lit(curl_axis(b)) for i, b in enumerate(fb)})
    g.n("ad", "make_array", count=len(fb), type="float", inp={"[%d]" % i: str(curl_deg(b)) for i, b in enumerate(fb)})
    g.n("as", "make_array", count=len(fb), type="float", inp={"[%d]" % i: str(spread_deg(b)) for i, b in enumerate(fb)})


def f_curl_finger():
    """Finger `finger` (side * 5 + thumb 0 .. pinky 4) curled by `amount` (0 base pose .. 1 fist) into DetailPose; thumb_01 also spread
    back by its hand's ThumbSpread. Detail Begin before, Detail Commit after."""
    g = G(); finger_tables(g); g.call("sd", K_MATH, "Divide_IntInt", inp={"A": "@entry.finger", "B": "5"})
    g.get("gts", "ThumbSpread"); g.call("tv", K_ARR, "Array_IsValidIndex", inp={"TargetArray": "@gts.ThumbSpread", "IndexToTest": "@sd.ReturnValue"})
    g.call("tg", K_ARR, "Array_Get", inp={"TargetArray": "@gts.ThumbSpread", "Index": "@sd.ReturnValue"}); g.call("spv", K_MATH, "SelectFloat", inp={"A": "@tg.Item", "B": "0.0", "bPickA": "@tv.ReturnValue"})
    g.call("b3", K_MATH, "Multiply_IntInt", inp={"A": "@entry.finger", "B": "3"}); puts = []
    for j in range(3):
        p = "j%d" % j
        g.call(p + "i", K_MATH, "Add_IntInt", inp={"A": "@b3.ReturnValue", "B": str(j)})
        for arr, nm in (("an", "nm"), ("ar", "rf"), ("ax", "av"), ("ad", "dg"), ("as", "sg")):
            g.call(p + nm, K_ARR, "Array_Get", inp={"TargetArray": "@%s.Array" % arr, "Index": "@%si.ReturnValue" % p})
        g.call(p + "m1", K_MATH, "Multiply_FloatFloat", inp={"A": "@entry.amount", "B": "@%sdg.Item" % p})
        g.call(p + "m2", K_MATH, "Multiply_FloatFloat", inp={"A": "@spv.ReturnValue", "B": "@%ssg.Item" % p})
        g.call(p + "an", K_MATH, "Subtract_FloatFloat", inp={"A": "@%sm1.ReturnValue" % p, "B": "@%sm2.ReturnValue" % p})
        g.n(p + "cr", "call_self", function="Curl Rot", inp={"ref": "@%srf.Item" % p, "axis": "@%sav.Item" % p, "angle": "@%san.ReturnValue" % p})
        g.n(p + "pt", "call_self", function="Detail Put", inp={"bone": "@%snm.Item" % p, "rot": "@%scr.rot" % p}); puts.append(p + "pt")
    g.chain("entry", *puts); return fn("Curl Finger", [param("finger", "int"), param("amount", "float")], graph=g)


def f_finger_curl_of():
    """How far a finger is curled in DetailPose: the turn of its middle joint's long axis against the base pose / its fist angle, 0..1."""
    g = G(); finger_tables(g); g.call("b3", K_MATH, "Multiply_IntInt", inp={"A": "@entry.finger", "B": "3"}); g.call("i1", K_MATH, "Add_IntInt", inp={"A": "@b3.ReturnValue", "B": "1"})
    g.call("nm", K_ARR, "Array_Get", inp={"TargetArray": "@an.Array", "Index": "@i1.ReturnValue"}); g.call("rf", K_ARR, "Array_Get", inp={"TargetArray": "@ar.Array", "Index": "@i1.ReturnValue"})
    g.call("dg", K_ARR, "Array_Get", inp={"TargetArray": "@ad.Array", "Index": "@i1.ReturnValue"})
    g.get("gdp", "DetailPose"); g.brk("bp", S_POSE, "@gdp.DetailPose"); g.call("fi", K_ARR, "Array_Find", inp={"TargetArray": "@bp.BoneNames", "ItemToFind": "@nm.Item"})
    g.call("lt", K_ARR, "Array_Get", inp={"TargetArray": "@bp.LocalTransforms", "Index": "@fi.ReturnValue"}); g.call("bt", K_MATH, "BreakTransform", inp={"InTransform": "@lt.Item"})
    g.call("fc", K_MATH, "GetForwardVector", inp={"InRot": "@bt.Rotation"}); g.call("fr", K_MATH, "GetForwardVector", inp={"InRot": "@rf.Item"})
    g.call("dt", K_MATH, "Dot_VectorVector", inp={"A": "@fc.ReturnValue", "B": "@fr.ReturnValue"}); g.call("dc", K_MATH, "FClamp", inp={"Value": "@dt.ReturnValue", "Min": "-1.0", "Max": "1.0"})
    g.call("ac", K_MATH, "DegAcos", inp={"A": "@dc.ReturnValue"}); g.call("q", K_MATH, "Divide_FloatFloat", inp={"A": "@ac.ReturnValue", "B": "@dg.Item"})
    g.call("cl", K_MATH, "FClamp", inp={"Value": "@q.ReturnValue", "Min": "0.0", "Max": "1.0"}); g.link("cl.ReturnValue", "return.amount"); g.chain("entry", "return")
    return fn("Finger Curl Of", [param("finger", "int")], [param("amount", "float")], graph=g, pure=True)


def f_apply_hand_pose():
    """Hand pose `pose` (HAND_POSES) on one hand: its thumb spread, then the five fingers, shown at once."""
    g = G(); flat = [float(v) for _, vals in HAND_POSES for v in vals]
    g.n("tb", "make_array", count=len(flat), type="float", inp={"[%d]" % i: str(v) for i, v in enumerate(flat)})
    g.call("sd", K_MATH, "SelectInt", inp={"A": "1", "B": "0", "bPickA": "@entry.right"}); g.call("b6", K_MATH, "Multiply_IntInt", inp={"A": "@entry.pose", "B": "6"})
    g.n("db", "call_self", function="Detail Begin")
    g.call("i5", K_MATH, "Add_IntInt", inp={"A": "@b6.ReturnValue", "B": "5"}); g.call("sv", K_ARR, "Array_Get", inp={"TargetArray": "@tb.Array", "Index": "@i5.ReturnValue"})
    g.get("gts", "ThumbSpread"); g.call("ss", K_ARR, "Array_Set", inp={"TargetArray": "@gts.ThumbSpread", "Index": "@sd.ReturnValue", "Item": "@sv.Item", "bSizeToFit": "true"})
    g.call("s5", K_MATH, "Multiply_IntInt", inp={"A": "@sd.ReturnValue", "B": "5"}); fs = []
    for f in range(5):
        g.call("fi%d" % f, K_MATH, "Add_IntInt", inp={"A": "@b6.ReturnValue", "B": str(f)}); g.call("fv%d" % f, K_ARR, "Array_Get", inp={"TargetArray": "@tb.Array", "Index": "@fi%d.ReturnValue" % f})
        g.call("fn%d" % f, K_MATH, "Add_IntInt", inp={"A": "@s5.ReturnValue", "B": str(f)})
        g.n("cf%d" % f, "call_self", function="Curl Finger", inp={"finger": "@fn%d.ReturnValue" % f, "amount": "@fv%d.Item" % f}); fs.append("cf%d" % f)
    g.n("cm", "call_self", function="Detail Commit"); g.chain("entry", "db", "ss", *fs, "cm")
    return fn("Apply Hand Pose", [param("right", "bool"), param("pose", "int")], graph=g)


def f_apply_lids():
    """Both lids as LidL / LidR say (0 open = base pose .. 1 closed), shown at once."""
    g = G(); g.n("db", "call_self", function="Detail Begin"); puts = []
    for b, v in (("Eye_L", "LidL"), ("Eye_R", "LidR")):
        p = b[-1].lower(); g.get(p + "g", v); g.call(p + "a", K_MATH, "Multiply_FloatFloat", inp={"A": "@%sg.%s" % (p, v), "B": str(LID_DEG)})
        g.n(p + "r", "call_self", function="Lid Rot", inp={"ref": make_rot(g, p + "rf", REF_ROT[b]), "axis": vec_lit(LID_AXIS[b]), "angle": "@%sa.ReturnValue" % p})
        g.n(p + "pt", "call_self", function="Detail Put", inp={"bone": b, "rot": "@%sr.rot" % p}); puts.append(p + "pt")
    g.n("cm", "call_self", function="Detail Commit"); g.chain("entry", "db", *puts, "cm"); return fn("Apply Lids", graph=g)


def f_eye_lids_step():
    """The wheel on a lid sphere: lids by `delta` (+ closes), 0..1; which 0 both, 1 left, 2 right."""
    g = G(); sets = []
    for v, other in (("LidL", "2"), ("LidR", "1")):
        g.get("g" + v, v); g.call("w" + v, K_MATH, "NotEqual_IntInt", inp={"A": "@entry.which", "B": other})
        g.call("a" + v, K_MATH, "Add_FloatFloat", inp={"A": "@g%s.%s" % (v, v), "B": "@entry.delta"}); g.call("c" + v, K_MATH, "FClamp", inp={"Value": "@a%s.ReturnValue" % v, "Min": "0.0", "Max": "1.0"})
        g.call("s" + v, K_MATH, "SelectFloat", inp={"A": "@c%s.ReturnValue" % v, "B": "@g%s.%s" % (v, v), "bPickA": "@w%s.ReturnValue" % v})
        g.set("ss" + v, v, inp={v: "@s%s.ReturnValue" % v}); sets.append("ss" + v)
    g.n("al", "call_self", function="Apply Lids"); g.chain("entry", *sets, "al")
    return fn("Eye Lids Step", [param("delta", "float"), param("which", "int")], graph=g)


def f_gaze_from_target():
    """Gaze toward `target` from `eyes` with the head's world transform: side (+ her right) and up, each -1..1 (full morph at
    GAZE_SIDE_DEG / GAZE_UP_DEG). Head bone space of the game's mesh: +Y forward, +X up, +Z her right."""
    g = G(); g.call("v", K_MATH, "Subtract_VectorVector", inp={"A": "@entry.target", "B": "@entry.eyes"})
    g.call("l", K_MATH, "InverseTransformDirection", inp={"T": "@entry.head", "Direction": "@v.ReturnValue"}); g.call("b", K_MATH, "BreakVector", inp={"InVec": "@l.ReturnValue"})
    g.call("ys", K_MATH, "DegAtan2", inp={"Y": "@b.Z", "X": "@b.Y"}); g.call("hv", K_MATH, "MakeVector", inp={"X": "0.0", "Y": "@b.Y", "Z": "@b.Z"}); g.call("hl", K_MATH, "VSize", inp={"A": "@hv.ReturnValue"})
    g.call("up", K_MATH, "DegAtan2", inp={"Y": "@b.X", "X": "@hl.ReturnValue"})
    g.call("s1", K_MATH, "Multiply_FloatFloat", inp={"A": "@ys.ReturnValue", "B": str(GAZE_SIDE_SIGN / GAZE_SIDE_DEG)}); g.call("s2", K_MATH, "FClamp", inp={"Value": "@s1.ReturnValue", "Min": "-1.0", "Max": "1.0"})
    g.call("u1", K_MATH, "Divide_FloatFloat", inp={"A": "@up.ReturnValue", "B": str(GAZE_UP_DEG)}); g.call("u2", K_MATH, "FClamp", inp={"Value": "@u1.ReturnValue", "Min": "-1.0", "Max": "1.0"})
    g.link("s2.ReturnValue", "return.side"); g.link("u2.ReturnValue", "return.up"); g.chain("entry", "return")
    return fn("Gaze From Target", [param("head", S_TF), param("eyes", S_VEC), param("target", S_VEC)], [param("side", "float"), param("up", "float")], graph=g, pure=True)


def f_set_gaze():
    """The gaze morphs (both eyes): side + right / - left, up + up / - down; remembered for poses and scenes (GazeSet)."""
    g = G(); g.set("ss", "GazeSide", inp={"GazeSide": "@entry.side"}); g.set("su", "GazeUp", inp={"GazeUp": "@entry.up"}); g.set("sg", "GazeSet", inp={"GazeSet": "true"})
    g.call("ns", K_MATH, "Multiply_FloatFloat", inp={"A": "@entry.side", "B": "-1.0"}); g.call("nu", K_MATH, "Multiply_FloatFloat", inp={"A": "@entry.up", "B": "-1.0"})
    ms = []
    for i, (m, val) in enumerate((("Face_Eye2Right", "@entry.side"), ("Face_Eye2Left", "@ns.ReturnValue"), ("Face_Eye2Up", "@entry.up"), ("Face_Eye2Down", "@nu.ReturnValue"))):
        g.call("mx%d" % i, K_MATH, "FMax", inp={"A": val, "B": "0.0"}); g.get("gb%d" % i, "Body")
        g.call("mt%d" % i, E_SKM, "SetMorphTarget", inp={"self": "@gb%d.Body" % i, "MorphTargetName": m, "Value": "@mx%d.ReturnValue" % i, "bRemoveZeroWeight": "false"}); ms.append("mt%d" % i)
    g.chain("entry", "ss", "su", "sg", *ms); return fn("Set Gaze", [param("side", "float"), param("up", "float")], graph=g)


def f_look_at():
    """Both eyes toward world `target` (from the middle between the lids, in the head's frame)."""
    g = G(); g.get("gb", "Body"); g.call("ht", E_SCENEC, "GetSocketTransform", inp={"self": "@gb.Body", "InSocketName": "head", "TransformSpace": "RTS_World"})
    g.call("el", E_SCENEC, "GetSocketLocation", inp={"self": "@gb.Body", "InSocketName": "Eye_L"}); g.call("er", E_SCENEC, "GetSocketLocation", inp={"self": "@gb.Body", "InSocketName": "Eye_R"})
    g.call("es", K_MATH, "Add_VectorVector", inp={"A": "@el.ReturnValue", "B": "@er.ReturnValue"}); g.call("em", K_MATH, "Multiply_VectorFloat", inp={"A": "@es.ReturnValue", "B": "0.5"})
    g.n("gz", "call_self", function="Gaze From Target", inp={"head": "@ht.ReturnValue", "eyes": "@em.ReturnValue", "target": "@entry.target"})
    g.n("sg", "call_self", function="Set Gaze", inp={"side": "@gz.side", "up": "@gz.up"}); g.chain("entry", "sg")
    return fn("Look At", [param("target", S_VEC)], graph=g)


def f_reset_eyes():
    """Ragdolls tab "Eyes: reset": lids open, gaze straight ahead."""
    g = G(); g.set("sl", "LidL", inp={"LidL": "0.0"}); g.set("sr", "LidR", inp={"LidR": "0.0"}); g.n("al", "call_self", function="Apply Lids")
    g.n("sg", "call_self", function="Set Gaze", inp={"side": "0.0", "up": "0.0"}); g.chain("entry", "sl", "sr", "al", "sg")
    return fn("Reset Eyes", graph=g)


def f_set_joint_states():
    """Locked / loose joints as a saved pose has them (Load Rag Pose; the figure is frozen then, locks act once it is active)."""
    g = G(); g.set("sl", "LockedJoints", inp={"LockedJoints": "@entry.locked"}); g.set("so", "LooseJoints", inp={"LooseJoints": "@entry.loose"})
    g.n("rm", "call_self", function="Refresh Markers"); g.chain("entry", "sl", "so", "rm")
    return fn("Set Joint States", [param("locked", "name", "array"), param("loose", "name", "array")], graph=g)


# ---- poses of their own (docs/specs/2026-10-07-ragdoll-poses-design.md): rotations per bone + the pelvis' tilt and height ----
POSE_FLOOR = ["pelvis", "spine_01", "spine_02", "spine_03", "neck_01", "head", "upperarm_l", "upperarm_r", "lowerarm_l", "lowerarm_r", "hand_l", "hand_r",
              "thigh_l", "thigh_r", "calf_l", "calf_r", "foot_l", "foot_r", "ball_l", "ball_r"]   # the lowest of these stands on the floor (ik_ and helper bones lie anywhere)
POSE_GAP_MAX = 15.0   # cm: a gap between the lowest bone and the floor up to this is flesh / sole; more (a figure lifted in the air) is dropped
POSE_TRACE_UP, POSE_TRACE_DOWN = 100.0, 1000.0   # floor below the pelvis: trace from this far above it to this far below


def yaw_tf(g, p, yaw_pin):
    """A transform turned only about the vertical axis (the figure's facing)."""
    g.call(p + "r", K_MATH, "MakeRotator", inp={"Roll": "0.0", "Pitch": "0.0", "Yaw": yaw_pin})
    g.call(p, K_MATH, "MakeTransform", inp={"Location": "(X=0,Y=0,Z=0)", "Rotation": "@%sr.ReturnValue" % p, "Scale": "(X=1,Y=1,Z=1)"}); return "@%s.ReturnValue" % p


def body_yaw(g, p):
    g.get(p + "b", "Body"); g.call(p + "cr", E_SCENEC, "K2_GetComponentRotation", inp={"self": "@%sb.Body" % p}); g.call(p, K_MATH, "BreakRotator", inp={"InRot": "@%scr.ReturnValue" % p})
    return "@%s.Yaw" % p


def f_floor_below():
    """The floor under a point (Visibility, the figure itself ignored): hit + its height."""
    g = G(); g.call("up", K_MATH, "Add_VectorVector", inp={"A": "@entry.at", "B": "(X=0,Y=0,Z=%s)" % POSE_TRACE_UP})
    g.call("dn", K_MATH, "Subtract_VectorVector", inp={"A": "@entry.at", "B": "(X=0,Y=0,Z=%s)" % POSE_TRACE_DOWN})
    g.n("ign", "make_array", count=0, type="object:" + E_ACTOR)
    g.call("lt", K_SYS, "LineTraceSingle", inp={"Start": "@up.ReturnValue", "End": "@dn.ReturnValue", "TraceChannel": "TraceTypeQuery1", "bTraceComplex": "false", "ActorsToIgnore": "@ign.Array",
                                                "DrawDebugType": "None", "bIgnoreSelf": "true", "TraceColor": "(R=1,G=0,B=0,A=1)", "TraceHitColor": "(R=0,G=1,B=0,A=1)", "DrawTime": "0.0"})
    g.call("bh", K_GS, "BreakHitResult", inp={"Hit": "@lt.OutHit"}); g.call("bl", K_MATH, "BreakVector", inp={"InVec": "@bh.Location"})
    g.link("lt.ReturnValue", "return.hit"); g.link("bl.Z", "return.z"); g.chain("entry", "lt", "return")
    return fn("Floor Below", [param("at", S_VEC)], [param("hit", "bool"), param("z", "float")], graph=g)


def f_lowest_bone():
    """Height of the lowest of POSE_FLOOR the mesh has (world)."""
    g = G(); g.set("s0", "TmpZ", inp={"TmpZ": "1000000000.0"}); prev = ["s0"]
    for i, b in enumerate(POSE_FLOOR):
        g.get("gb%d" % i, "Body"); g.call("bi%d" % i, E_SKIN, "GetBoneIndex", inp={"self": "@gb%d.Body" % i, "BoneName": b}); g.call("hb%d" % i, K_MATH, "NotEqual_IntInt", inp={"A": "@bi%d.ReturnValue" % i, "B": "-1"})
        g.branch("b%d" % i, "@hb%d.ReturnValue" % i)
        g.call("sl%d" % i, E_SCENEC, "GetSocketLocation", inp={"self": "@gb%d.Body" % i, "InSocketName": b}); g.call("bv%d" % i, K_MATH, "BreakVector", inp={"InVec": "@sl%d.ReturnValue" % i})
        g.get("gz%d" % i, "TmpZ"); g.call("mn%d" % i, K_MATH, "FMin", inp={"A": "@gz%d.TmpZ" % i, "B": "@bv%d.Z" % i}); g.set("sz%d" % i, "TmpZ", inp={"TmpZ": "@mn%d.ReturnValue" % i})
        for e in prev: g.chain(e, "b%d" % i)
        g.chain("b%d" % i, "sz%d" % i); prev = ["sz%d" % i, "b%d:else" % i]
    g.get("gz", "TmpZ"); g.link("gz.TmpZ", "return.z")
    for e in prev: g.chain(e, "return")
    g.chain("entry", "s0")
    return fn("Lowest Bone", [], [param("z", "float")], graph=g)


def f_pose_data():
    """This figure's pose for saving: every bone's local rotation (fresh snapshot - an active figure's physics result too), the
    pelvis' world rotation relative to the figure's facing (yaw of the body) and the pelvis' height above the floor (the lowest bone's
    height + its gap to the floor, at most POSE_GAP_MAX: a lifted figure's pose lands on the floor)."""
    g = G(); g.get("gb", "Body"); g.get("gpt", "PoseTmp"); g.call("sn", E_SKM, "SnapshotPose", inp={"self": "@gb.Body", "Snapshot": "@gpt.PoseTmp"})
    g.get("gpt2", "PoseTmp"); g.brk("bp", S_POSE, "@gpt2.PoseTmp")
    g.get("gr0", "TmpRots"); g.call("cr", K_ARR, "Array_Clear", inp={"TargetArray": "@gr0.TmpRots"})
    g.foreach("fe", "@bp.LocalTransforms"); g.call("bt", K_MATH, "BreakTransform", inp={"InTransform": "@fe.Array Element"})
    g.get("gr1", "TmpRots"); g.call("ar", K_ARR, "Array_Add", inp={"TargetArray": "@gr1.TmpRots", "NewItem": "@bt.Rotation"})
    g.get("gb2", "Body"); g.call("pr", E_SCENEC, "GetSocketRotation", inp={"self": "@gb2.Body", "InSocketName": "pelvis"})
    g.call("pl", E_SCENEC, "GetSocketLocation", inp={"self": "@gb2.Body", "InSocketName": "pelvis"}); g.call("bpl", K_MATH, "BreakVector", inp={"InVec": "@pl.ReturnValue"})
    yt = yaw_tf(g, "yt", body_yaw(g, "by")); g.call("rr", K_MATH, "InverseTransformRotation", inp={"T": yt, "Rotation": "@pr.ReturnValue"})
    g.n("lo", "call_self", function="Lowest Bone"); g.n("fl", "call_self", function="Floor Below", inp={"at": "@pl.ReturnValue"})
    g.call("gap", K_MATH, "Subtract_FloatFloat", inp={"A": "@lo.z", "B": "@fl.z"}); g.call("gc", K_MATH, "FClamp", inp={"Value": "@gap.ReturnValue", "Min": "0.0", "Max": str(POSE_GAP_MAX)})
    g.call("g0", K_MATH, "SelectFloat", inp={"A": "@gc.ReturnValue", "B": "0.0", "bPickA": "@fl.hit"})
    g.call("ab", K_MATH, "Subtract_FloatFloat", inp={"A": "@bpl.Z", "B": "@lo.z"}); g.call("h", K_MATH, "Add_FloatFloat", inp={"A": "@ab.ReturnValue", "B": "@g0.ReturnValue"})
    g.get("gr2", "TmpRots"); g.link("bp.BoneNames", "return.bones"); g.link("gr2.TmpRots", "return.rots"); g.link("rr.ReturnValue", "return.rootRot"); g.link("h.ReturnValue", "return.rootHeight")
    g.chain("entry", "sn", "cr", "fe"); g.chain("fe", "ar"); g.chain("fe:Completed", "lo", "fl", "return")
    return fn("Pose Data", [], [param("bones", "name", "array"), param("rots", S_ROT, "array"), param("rootRot", S_ROT), param("rootHeight", "float")], graph=g)


def f_merge_rotations():
    """names / local of a snapshot with the rotations of a saved pose: a bone the pose has takes its rotation and keeps its own
    translation and scale (bone lengths, body shape); the root (index 0), the pelvis (placed by Root Local) and bones the pose lacks
    stay as they are. Result also in TmpLocal."""
    g = G(); g.set("s0", "TmpLocal", inp={"TmpLocal": "@entry.local"}); g.foreach("fe", "@entry.names")
    g.call("i0", K_MATH, "NotEqual_IntInt", inp={"A": "@fe.Array Index", "B": "0"}); g.call("np", K_MATH, "NotEqual_NameName", inp={"A": "@fe.Array Element", "B": "pelvis"})
    g.call("fd", K_ARR, "Array_Find", inp={"TargetArray": "@entry.bones", "ItemToFind": "@fe.Array Element"}); g.call("hf", K_MATH, "GreaterEqual_IntInt", inp={"A": "@fd.ReturnValue", "B": "0"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@i0.ReturnValue", "B": "@np.ReturnValue"}); g.call("a2", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@hf.ReturnValue"}); g.branch("b", "@a2.ReturnValue")
    g.call("rt", K_ARR, "Array_Get", inp={"TargetArray": "@entry.rots", "Index": "@fd.ReturnValue"})
    g.get("gl", "TmpLocal"); g.call("ot", K_ARR, "Array_Get", inp={"TargetArray": "@gl.TmpLocal", "Index": "@fe.Array Index"}); g.call("bt", K_MATH, "BreakTransform", inp={"InTransform": "@ot.Item"})
    g.call("mt", K_MATH, "MakeTransform", inp={"Location": "@bt.Location", "Rotation": "@rt.Item", "Scale": "@bt.Scale"})
    g.get("gl2", "TmpLocal"); g.call("st", K_ARR, "Array_Set", inp={"TargetArray": "@gl2.TmpLocal", "Index": "@fe.Array Index", "Item": "@mt.ReturnValue", "bSizeToFit": "false"})
    g.get("gl3", "TmpLocal"); g.link("gl3.TmpLocal", "return.out")
    g.chain("entry", "s0", "fe"); g.chain("fe", "b", "st"); g.chain("fe:Completed", "return")
    return fn("Merge Rotations", [param("names", "name", "array"), param("local", S_TF, "array"), param("bones", "name", "array"), param("rots", S_ROT, "array")],
              [param("out", S_TF, "array")], graph=g)


def f_root_local():
    """The pelvis' local transform (= component space, the root being the identity) for: facing `yaw`, tilt `rootRot` relative to
    it, at xy, height z (world)."""
    g = G(); yt = yaw_tf(g, "yt", "@entry.yaw"); g.call("wr", K_MATH, "TransformRotation", inp={"T": yt, "Rotation": "@entry.rootRot"})
    g.call("bx", K_MATH, "BreakVector", inp={"InVec": "@entry.xy"}); g.call("wl", K_MATH, "MakeVector", inp={"X": "@bx.X", "Y": "@bx.Y", "Z": "@entry.z"})
    g.call("ll", K_MATH, "InverseTransformLocation", inp={"T": "@entry.comp", "Location": "@wl.ReturnValue"}); g.call("lr", K_MATH, "InverseTransformRotation", inp={"T": "@entry.comp", "Rotation": "@wr.ReturnValue"})
    g.call("mt", K_MATH, "MakeTransform", inp={"Location": "@ll.ReturnValue", "Rotation": "@lr.ReturnValue", "Scale": "@entry.scale"})
    g.link("mt.ReturnValue", "return.local"); g.chain("entry", "return")
    return fn("Root Local", [param("comp", S_TF), param("yaw", "float"), param("rootRot", S_ROT), param("xy", S_VEC), param("z", "float"), param("scale", S_VEC)],
              [param("local", S_TF)], graph=g, pure=True)


def f_apply_pose_data():
    """A saved pose onto this figure: frozen first, then every bone the pose has takes its rotation (Merge Rotations); the root becomes
    the identity and the pelvis stands where it is now (XY), facing as the figure does, tilted as saved, its height rootHeight above
    the floor below it (no floor: as it is). A skeleton without a pelvis takes the rotations only. Joints (locked / loose) stay."""
    g = G(); g.get("gac", "Active"); g.branch("bac", "@gac.Active"); g.n("fz", "call_self", function="Freeze")
    g.get("gb", "Body"); g.get("gpt", "PoseTmp"); g.call("sn", E_SKM, "SnapshotPose", inp={"self": "@gb.Body", "Snapshot": "@gpt.PoseTmp"})
    g.get("gpt2", "PoseTmp"); g.brk("bp", S_POSE, "@gpt2.PoseTmp")
    g.n("mr", "call_self", function="Merge Rotations", inp={"names": "@bp.BoneNames", "local": "@bp.LocalTransforms", "bones": "@entry.bones", "rots": "@entry.rots"})
    g.call("pi", K_ARR, "Array_Find", inp={"TargetArray": "@bp.BoneNames", "ItemToFind": g.lit_name("pln", "pelvis")}); g.call("hp", K_MATH, "GreaterEqual_IntInt", inp={"A": "@pi.ReturnValue", "B": "0"}); g.branch("bhp", "@hp.ReturnValue")
    g.get("gb2", "Body"); g.call("pl", E_SCENEC, "GetSocketLocation", inp={"self": "@gb2.Body", "InSocketName": "pelvis"}); g.call("bpl", K_MATH, "BreakVector", inp={"InVec": "@pl.ReturnValue"})
    g.n("fl", "call_self", function="Floor Below", inp={"at": "@pl.ReturnValue"}); g.call("fz2", K_MATH, "Add_FloatFloat", inp={"A": "@fl.z", "B": "@entry.rootHeight"})
    g.call("z", K_MATH, "SelectFloat", inp={"A": "@fz2.ReturnValue", "B": "@bpl.Z", "bPickA": "@fl.hit"})
    g.get("gb3", "Body"); g.call("cw", E_SCENEC, "K2_GetComponentToWorld", inp={"self": "@gb3.Body"})
    g.get("gl0", "TmpLocal"); g.call("op", K_ARR, "Array_Get", inp={"TargetArray": "@gl0.TmpLocal", "Index": "@pi.ReturnValue"}); g.call("bop", K_MATH, "BreakTransform", inp={"InTransform": "@op.Item"})
    g.n("rl", "call_self", function="Root Local", inp={"comp": "@cw.ReturnValue", "yaw": body_yaw(g, "by"), "rootRot": "@entry.rootRot", "xy": "@pl.ReturnValue", "z": "@z.ReturnValue", "scale": "@bop.Scale"})
    g.get("gl1", "TmpLocal"); g.call("sp", K_ARR, "Array_Set", inp={"TargetArray": "@gl1.TmpLocal", "Index": "@pi.ReturnValue", "Item": "@rl.local", "bSizeToFit": "false"})
    g.get("gl2", "TmpLocal"); g.call("sr", K_ARR, "Array_Set", inp={"TargetArray": "@gl2.TmpLocal", "Index": "0", "Item": ident_tf(g), "bSizeToFit": "false"})
    g.get("gl3", "TmpLocal"); g.make("ms", S_POSE, LocalTransforms="@gl3.TmpLocal", BoneNames="@bp.BoneNames", SkeletalMeshName="@bp.SkeletalMeshName", bIsValid="true")
    g.n("set", "call_self", function="Set Pose", inp={"snap": "@ms.PoseSnapshot"})
    g.chain("entry", "bac", "fz", "sn"); g.chain("bac:else", "sn"); g.chain("sn", "mr", "bhp", "fl", "sp", "sr", "set"); g.chain("bhp:else", "set")
    return fn("Apply Pose Data", [param("bones", "name", "array"), param("rots", S_ROT, "array"), param("rootRot", S_ROT), param("rootHeight", "float")], graph=g)


# ---- turning a limb about its joint (spec 2026-10-20-ragdoll-glied-drehen-design): the held pose is turned directly, no physics ----
def f_turn_delta():
    """The rotation (world) that turns direction `from` onto direction `to`: about their cross product by the angle between them;
    the identity when they are (anti)parallel or one is zero."""
    g = G(); g.call("nf", K_MATH, "Normal", inp={"A": "@entry.from", "Tolerance": "0.0001"}); g.call("nt", K_MATH, "Normal", inp={"A": "@entry.to", "Tolerance": "0.0001"})
    g.call("cr", K_MATH, "Cross_VectorVector", inp={"A": "@nf.ReturnValue", "B": "@nt.ReturnValue"}); g.call("cl", K_MATH, "VSize", inp={"A": "@cr.ReturnValue"})
    g.call("ok", K_MATH, "Greater_FloatFloat", inp={"A": "@cl.ReturnValue", "B": "0.0001"}); g.call("ax", K_MATH, "Normal", inp={"A": "@cr.ReturnValue", "Tolerance": "0.0001"})
    g.call("ax2", K_MATH, "SelectVector", inp={"A": "@ax.ReturnValue", "B": "(X=0,Y=0,Z=1)", "bPickA": "@ok.ReturnValue"})
    g.call("dt", K_MATH, "Dot_VectorVector", inp={"A": "@nf.ReturnValue", "B": "@nt.ReturnValue"}); g.call("dc", K_MATH, "FClamp", inp={"Value": "@dt.ReturnValue", "Min": "-1.0", "Max": "1.0"})
    g.call("an", K_MATH, "DegAcos", inp={"A": "@dc.ReturnValue"}); g.call("an2", K_MATH, "SelectFloat", inp={"A": "@an.ReturnValue", "B": "0.0", "bPickA": "@ok.ReturnValue"})
    g.call("r", K_MATH, "RotatorFromAxisAndAngle", inp={"Axis": "@ax2.ReturnValue", "Angle": "@an2.ReturnValue"}); g.link("r.ReturnValue", "return.delta"); g.chain("entry", "return")
    return fn("Turn Delta", [param("from", S_VEC), param("to", S_VEC)], [param("delta", S_ROT)], graph=g, pure=True)


def f_turn_local():
    """A bone's world rotation `rot` turned by `delta` (world), and that as its rotation relative to its parent (world transform `parent`)."""
    g = G(); g.call("cr", K_MATH, "ComposeRotators", inp={"A": "@entry.rot", "B": "@entry.delta"})
    g.call("lr", K_MATH, "InverseTransformRotation", inp={"T": "@entry.parent", "Rotation": "@cr.ReturnValue"})
    g.link("cr.ReturnValue", "return.world"); g.link("lr.ReturnValue", "return.local"); g.chain("entry", "return")
    return fn("Turn Local", [param("parent", S_TF), param("rot", S_ROT), param("delta", S_ROT)], [param("world", S_ROT), param("local", S_ROT)], graph=g, pure=True)


def f_begin_turn():
    """Start turning `bone` (frozen figure), grabbed at world `point`: the held pose, the bone's place in it, its world rotation, its
    parent's world transform (stays put while turning), and - in the bone's own rotation - the grabbed point and the limb's long axis
    (towards the child joint farthest away; none: towards the grabbed point). ok = the bone is in the pose and has a parent."""
    g = G(); g.get("gb", "Body"); g.get("gtp", "TurnPose"); g.call("sn", E_SKM, "SnapshotPose", inp={"self": "@gb.Body", "Snapshot": "@gtp.TurnPose"})
    g.get("gtp2", "TurnPose"); g.brk("bp", S_POSE, "@gtp2.TurnPose"); g.call("fi", K_ARR, "Array_Find", inp={"TargetArray": "@bp.BoneNames", "ItemToFind": "@entry.bone"})
    g.set("si", "TurnIdx", inp={"TurnIdx": "@fi.ReturnValue"})
    g.get("gb2", "Body"); g.call("wr", E_SCENEC, "GetSocketRotation", inp={"self": "@gb2.Body", "InSocketName": "@entry.bone"}); g.set("sr", "TurnRot", inp={"TurnRot": "@wr.ReturnValue"})
    g.call("wl", E_SCENEC, "GetSocketLocation", inp={"self": "@gb2.Body", "InSocketName": "@entry.bone"}); g.set("sj", "TurnJoint", inp={"TurnJoint": "@wl.ReturnValue"})
    g.call("pb", E_SKIN, "GetParentBone", inp={"self": "@gb2.Body", "BoneName": "@entry.bone"})
    g.call("pt", E_SCENEC, "GetSocketTransform", inp={"self": "@gb2.Body", "InSocketName": "@pb.ReturnValue", "TransformSpace": "RTS_World"}); g.set("sp", "TurnParent", inp={"TurnParent": "@pt.ReturnValue"})
    g.call("pv", K_MATH, "Subtract_VectorVector", inp={"A": "@entry.point", "B": "@wl.ReturnValue"})
    g.get("gr1", "TurnRot"); g.call("pu", K_MATH, "LessLess_VectorRotator", inp={"A": "@pv.ReturnValue", "B": "@gr1.TurnRot"}); g.set("spl", "TurnPointLocal", inp={"TurnPointLocal": "@pu.ReturnValue"})
    # long axis: the child joint farthest from this one
    g.set("fa0", "TurnFar", inp={"TurnFar": "@pv.ReturnValue"}); g.set("fd0", "TurnFarDist", inp={"TurnFarDist": "0.0"})
    g.foreach("fe", "@bp.BoneNames"); g.get("gb3", "Body"); g.call("cp", E_SKIN, "GetParentBone", inp={"self": "@gb3.Body", "BoneName": "@fe.Array Element"})
    g.call("ic", K_MATH, "EqualEqual_NameName", inp={"A": "@cp.ReturnValue", "B": "@entry.bone"}); g.branch("bic", "@ic.ReturnValue")
    g.call("cl", E_SCENEC, "GetSocketLocation", inp={"self": "@gb3.Body", "InSocketName": "@fe.Array Element"}); g.get("gj", "TurnJoint")
    g.call("cv", K_MATH, "Subtract_VectorVector", inp={"A": "@cl.ReturnValue", "B": "@gj.TurnJoint"}); g.call("cd", K_MATH, "VSize", inp={"A": "@cv.ReturnValue"})
    g.get("gfd", "TurnFarDist"); g.call("fr", K_MATH, "Greater_FloatFloat", inp={"A": "@cd.ReturnValue", "B": "@gfd.TurnFarDist"}); g.branch("bfr", "@fr.ReturnValue")
    g.set("fa1", "TurnFar", inp={"TurnFar": "@cv.ReturnValue"}); g.set("fd1", "TurnFarDist", inp={"TurnFarDist": "@cd.ReturnValue"})
    g.get("gfa", "TurnFar"); g.call("fn", K_MATH, "Normal", inp={"A": "@gfa.TurnFar", "Tolerance": "0.0001"}); g.get("gr2", "TurnRot")
    g.call("au", K_MATH, "LessLess_VectorRotator", inp={"A": "@fn.ReturnValue", "B": "@gr2.TurnRot"}); g.set("sal", "TurnAxisLocal", inp={"TurnAxisLocal": "@au.ReturnValue"})
    g.call("hi", K_MATH, "GreaterEqual_IntInt", inp={"A": "@fi.ReturnValue", "B": "0"}); g.call("hp", K_MATH, "NotEqual_NameName", inp={"A": "@pb.ReturnValue", "B": "None"})
    g.call("ok", K_MATH, "BooleanAND", inp={"A": "@hi.ReturnValue", "B": "@hp.ReturnValue"}); g.link("ok.ReturnValue", "return.ok")
    g.chain("entry", "sn", "si", "sr", "sj", "sp", "spl", "fa0", "fd0", "fe"); g.chain("fe", "bic", "bfr", "fa1", "fd1"); g.chain("fe:Completed", "sal", "return")
    return fn("Begin Turn", [param("bone", "name"), param("point", S_VEC)], [param("ok", "bool")], graph=g)


def f_apply_turn():
    """Turn the bone being turned by `delta` (world): its new rotation relative to the parent goes into the held pose."""
    g = G(); g.get("gp", "TurnParent"); g.get("gr", "TurnRot"); g.n("tl", "call_self", function="Turn Local", inp={"parent": "@gp.TurnParent", "rot": "@gr.TurnRot", "delta": "@entry.delta"})
    g.set("sr", "TurnRot", inp={"TurnRot": "@tl.world"})
    g.get("gtp", "TurnPose"); g.brk("bp", S_POSE, "@gtp.TurnPose"); g.set("stl", "TmpLocal", inp={"TmpLocal": "@bp.LocalTransforms"})
    g.get("gi", "TurnIdx"); g.get("gl", "TmpLocal"); g.call("ot", K_ARR, "Array_Get", inp={"TargetArray": "@gl.TmpLocal", "Index": "@gi.TurnIdx"}); g.call("bt", K_MATH, "BreakTransform", inp={"InTransform": "@ot.Item"})
    g.call("mt", K_MATH, "MakeTransform", inp={"Location": "@bt.Location", "Rotation": "@tl.local", "Scale": "@bt.Scale"})
    g.get("gl2", "TmpLocal"); g.call("st", K_ARR, "Array_Set", inp={"TargetArray": "@gl2.TmpLocal", "Index": "@gi.TurnIdx", "Item": "@mt.ReturnValue", "bSizeToFit": "false"})
    g.get("gl3", "TmpLocal"); g.make("ms", S_POSE, LocalTransforms="@gl3.TmpLocal", BoneNames="@bp.BoneNames", SkeletalMeshName="@bp.SkeletalMeshName", bIsValid="true")
    g.set("stp", "TurnPose", inp={"TurnPose": "@ms.PoseSnapshot"}); g.get("gtp2", "TurnPose"); g.n("set", "call_self", function="Set Pose", inp={"snap": "@gtp2.TurnPose"})
    g.chain("entry", "sr", "stl", "st", "stp", "set"); return fn("Apply Turn", [param("delta", S_ROT)], graph=g)


def f_turn_toward():
    """The grabbed point of the limb turns towards world `target` about the joint."""
    g = G(); g.get("gpl", "TurnPointLocal"); g.get("gr", "TurnRot"); g.call("pv", K_MATH, "GreaterGreater_VectorRotator", inp={"A": "@gpl.TurnPointLocal", "B": "@gr.TurnRot"})
    g.get("gj", "TurnJoint"); g.call("tv", K_MATH, "Subtract_VectorVector", inp={"A": "@entry.target", "B": "@gj.TurnJoint"})
    g.n("td", "call_self", function="Turn Delta", inp={"from": "@pv.ReturnValue", "to": "@tv.ReturnValue"}); g.n("ap", "call_self", function="Apply Turn", inp={"delta": "@td.delta"})
    g.chain("entry", "ap"); return fn("Turn Toward", [param("target", S_VEC)], graph=g)


def f_twist():
    """The limb turns `deg` about its own long axis."""
    g = G(); g.get("gal", "TurnAxisLocal"); g.get("gr", "TurnRot"); g.call("ax", K_MATH, "GreaterGreater_VectorRotator", inp={"A": "@gal.TurnAxisLocal", "B": "@gr.TurnRot"})
    g.call("d", K_MATH, "RotatorFromAxisAndAngle", inp={"Axis": "@ax.ReturnValue", "Angle": "@entry.deg"}); g.n("ap", "call_self", function="Apply Turn", inp={"delta": "@d.ReturnValue"})
    g.chain("entry", "ap"); return fn("Twist", [param("deg", "float")], graph=g)


def f_hit_jolt():
    """A zombie's hit: active - an impulse on that bone (locked joints hold); frozen - the pose is kept aside at the first hit (HitPose),
    the chain from RAG_HIT_ROOT[bone] simulates without gravity (Loosen Below) and gets the impulse; Hit Back after RAG_HIT_BACK from the
    last hit (Rag Proxy Watch)."""
    g = G(); g.get("ga", "Active"); g.branch("bac", "@ga.Active")
    g.get("gb", "Body"); g.call("imp", E_PRIMC, "AddImpulse", inp={"self": "@gb.Body", "Impulse": "@entry.impulse", "BoneName": "@entry.bone", "bVelChange": "true"})
    g.get("gha", "HitActive"); g.branch("bha", "@gha.HitActive")
    g.get("gb2", "Body"); g.get("ghp", "HitPose"); g.call("snp", E_SKM, "SnapshotPose", inp={"self": "@gb2.Body", "Snapshot": "@ghp.HitPose"}); g.set("sha", "HitActive", inp={"HitActive": "true"})
    prev = []
    for i, (b, root) in enumerate(sorted(RAG_HIT_ROOT.items())):
        g.call("e%d" % i, K_MATH, "EqualEqual_NameName", inp={"A": "@entry.bone", "B": b}); g.branch("br%d" % i, "@e%d.ReturnValue" % i)
        g.n("lb%d" % i, "call_self", function="Loosen Below", inp={"root": root}); g.chain("br%d" % i, "lb%d" % i, "su")
        for e in prev: g.chain(e, "br%d" % i)
        prev = ["br%d:else" % i]
    g.call("now", K_SYS, "GetGameTimeInSeconds"); g.call("until", K_MATH, "Add_FloatFloat", inp={"A": "@now.ReturnValue", "B": str(RAG_HIT_BACK)})
    g.set("su", "HitUntil", inp={"HitUntil": "@until.ReturnValue"}); g.get("gb3", "Body")
    g.call("imp2", E_PRIMC, "AddImpulse", inp={"self": "@gb3.Body", "Impulse": "@entry.impulse", "BoneName": "@entry.bone", "bVelChange": "true"})
    g.chain("entry", "bac", "imp"); g.chain("bac:else", "bha", "br0"); g.chain("bha:else", "snp", "sha", "br0"); g.chain(prev[0], "su"); g.chain("su", "imp2")
    return fn("Hit Jolt", [param("bone", "name"), param("impulse", S_VEC)], graph=g)


def f_hit_back():
    """The jolt is over: locks of the loosened chain go, physics off, gravity on again, the pose from before the first hit. Activated
    meanwhile: physics and its locks stay, only gravity comes back (Loosen Below took it)."""
    g = G(); g.get("ga", "Active"); g.branch("bac", "@ga.Active")
    g.get("gb0", "Body"); g.call("grv0", E_PRIMC, "SetEnableGravity", inp={"self": "@gb0.Body", "bGravityEnabled": "true"}); g.set("sha0", "HitActive", inp={"HitActive": "false"})
    g.get("gl", "Locks"); g.call("lv", K_MAP, "Map_Values", inp={"TargetMap": "@gl.Locks"}); g.foreach("fe", "@lv.Values")
    g.call("dc", E_ACTC, "K2_DestroyComponent", inp={"self": "@fe.Array Element", "Object": "@fe.Array Element"})
    g.get("gl2", "Locks"); g.call("cl", K_MAP, "Map_Clear", inp={"TargetMap": "@gl2.Locks"})
    g.get("gb", "Body"); g.call("off", E_PRIMC, "SetSimulatePhysics", inp={"self": "@gb.Body", "bSimulate": "false"})
    g.get("gb2", "Body"); g.call("grv", E_PRIMC, "SetEnableGravity", inp={"self": "@gb2.Body", "bGravityEnabled": "true"})
    g.get("ghp", "HitPose"); g.n("sp", "call_self", function="Set Pose", inp={"snap": "@ghp.HitPose"}); g.set("sha", "HitActive", inp={"HitActive": "false"})
    g.chain("entry", "bac", "grv0", "sha0"); g.chain("bac:else", "lv", "fe"); g.chain("fe", "dc"); g.chain("fe:Completed", "cl", "off", "grv", "sp", "sha")
    return fn("Hit Back", graph=g)

def test_events():
    """Editor tests (tests/editor/test_ragdoll.py): Python cannot call the functions directly (locals), events can."""
    g = G()
    g.custom("ttj", "Test Toggle Joint", [param("bone", "name")]); g.n("ttj_c", "call_self", function="Toggle Joint", inp={"bone": "@ttj.bone"}); g.chain("ttj", "ttj_c")
    g.custom("tla", "Test Lock All", [param("joints", "name", "array")]); g.n("tla_c", "call_self", function="Lock All", inp={"joints": "@tla.joints"}); g.chain("tla", "tla_c")
    g.custom("tfa", "Test Free All"); g.n("tfa_c", "call_self", function="Free All"); g.chain("tfa", "tfa_c")
    g.custom("ttl", "Test Toggle Loose", [param("bone", "name")]); g.n("ttl_c", "call_self", function="Toggle Loose", inp={"bone": "@ttl.bone"}); g.chain("ttl", "ttl_c")
    # carried-over parts of a zombie (crystal, tank) hang on the figure as actors of their own: they go with it
    g.event("dst", E_ACTOR, "ReceiveDestroyed"); g.self_("me"); g.call("gaa", E_ACTOR, "GetAttachedActors", inp={"self": "@me.self", "bResetArray": "true"})
    g.foreach("fda", "@gaa.OutActors"); g.call("dda", E_ACTOR, "K2_DestroyActor", inp={"self": "@fda.Array Element"}); g.chain("dst", "fda"); g.chain("fda", "dda")
    g.custom("tmr", "Test Merge Rotations", [param("names", "name", "array"), param("local", S_TF, "array"), param("bones", "name", "array"), param("rots", S_ROT, "array")])
    g.n("tmr_c", "call_self", function="Merge Rotations", inp={"names": "@tmr.names", "local": "@tmr.local", "bones": "@tmr.bones", "rots": "@tmr.rots"}); g.chain("tmr", "tmr_c")
    g.custom("trl", "Test Root Local", [param("comp", S_TF), param("yaw", "float"), param("rootRot", S_ROT), param("xy", S_VEC), param("z", "float"), param("scale", S_VEC)])
    g.n("trl_c", "call_self", function="Root Local", inp={"comp": "@trl.comp", "yaw": "@trl.yaw", "rootRot": "@trl.rootRot", "xy": "@trl.xy", "z": "@trl.z", "scale": "@trl.scale"})
    g.set("trl_s", "TmpRootLocal", inp={"TmpRootLocal": "@trl_c.local"}); g.chain("trl", "trl_s")
    g.custom("tlr", "Test Loose Root", [param("bone", "name")]); g.n("tlr_c", "call_self", function="Loose Root", inp={"bone": "@tlr.bone"}); g.chain("tlr", "tlr_c")
    g.custom("ttd", "Test Turn", [param("from", S_VEC), param("to", S_VEC), param("parent", S_TF), param("rot", S_ROT)])
    g.n("ttd_d", "call_self", function="Turn Delta", inp={"from": "@ttd.from", "to": "@ttd.to"})
    g.n("ttd_l", "call_self", function="Turn Local", inp={"parent": "@ttd.parent", "rot": "@ttd.rot", "delta": "@ttd_d.delta"})
    g.set("ttd_s1", "TmpTurnDelta", inp={"TmpTurnDelta": "@ttd_d.delta"}); g.set("ttd_s2", "TmpTurnWorld", inp={"TmpTurnWorld": "@ttd_l.world"}); g.set("ttd_s3", "TmpTurnLocal", inp={"TmpTurnLocal": "@ttd_l.local"})
    g.chain("ttd", "ttd_s1", "ttd_s2", "ttd_s3")
    # fingers and eyes (spec 2026-10-26): the pure maths
    g.custom("tcr", "Test Curl Rot", [param("ref", S_ROT), param("axis", S_VEC), param("angle", "float")])
    g.n("tcr_c", "call_self", function="Curl Rot", inp={"ref": "@tcr.ref", "axis": "@tcr.axis", "angle": "@tcr.angle"}); g.set("tcr_s", "TmpTurnLocal", inp={"TmpTurnLocal": "@tcr_c.rot"}); g.chain("tcr", "tcr_s")
    g.custom("tlr2", "Test Lid Rot", [param("ref", S_ROT), param("axis", S_VEC), param("angle", "float")])
    g.n("tlr2_c", "call_self", function="Lid Rot", inp={"ref": "@tlr2.ref", "axis": "@tlr2.axis", "angle": "@tlr2.angle"}); g.set("tlr2_s", "TmpTurnWorld", inp={"TmpTurnWorld": "@tlr2_c.rot"}); g.chain("tlr2", "tlr2_s")
    g.custom("tgz", "Test Gaze", [param("head", S_TF), param("eyes", S_VEC), param("target", S_VEC)])
    g.n("tgz_c", "call_self", function="Gaze From Target", inp={"head": "@tgz.head", "eyes": "@tgz.eyes", "target": "@tgz.target"})
    g.call("tgz_v", K_MATH, "MakeVector", inp={"X": "@tgz_c.side", "Y": "@tgz_c.up", "Z": "0.0"}); g.set("tgz_s", "TmpGaze", inp={"TmpGaze": "@tgz_v.ReturnValue"}); g.chain("tgz", "tgz_s")
    return g


def build():
    return [struct(S_RAGMAT, [param("Path", "string"), param("Dynamic", "bool"), param("ScalarNames", "name", "array"), param("ScalarValues", "float", "array"),
                              param("VectorNames", "name", "array"), param("VectorValues", S_LIN, "array"), param("TextureNames", "name", "array"), param("TexturePaths", "string", "array")]),
            struct(S_RAGPART, [param("Mesh", "string"), param("Skeletal", "bool"), param("Socket", "name"), param("Rel", S_TF), param("Mats", "struct:" + S_RAGMAT, "array")])] + \
           [skeleton_stub(p) for _, p in RAG_SKELETONS] + [animblueprint(RAG_ABP, SKELETON, [var("Snap", "struct:" + S_POSE)], [], snapshot_var="Snap")] + \
           [animblueprint(RAG_ABP + "_" + k, p, [var("Snap", "struct:" + S_POSE)], [], snapshot_var="Snap") for k, p in RAG_SKELETONS] + [
            blueprint(RAGDOLL, E_ACTOR, components=[component("Body", E_SKM)],
                      variables=[var("Locks", "name", "map", value_type="object:" + E_CONSTR), var("Comps", "object:" + E_ACTC, "array"), var("LockParent", "name"),
                                 var("LockedJoints", "name", "array"), var("JointsLoop", "name", "array"), var("Active", "bool"), var("PoseTmp", "struct:" + S_POSE),
                                 var("DisplayName", "string"), var("Expanded", "bool"), var("LooseJoints", "name", "array"), var("LooseWalk", "name"), var("LooseFound", "name"),
                                 var("Kind", "string"), var("TmpParts", "struct:" + S_RAGPART, "array"), var("TmpMats", "struct:" + S_RAGMAT, "array"), var("TmpRoot", "object:" + E_SCENEC),
                                 var("TmpMid", "object:" + E_MIDC), var("TmpSN", "name", "array"), var("TmpSV", "float", "array"), var("TmpVN", "name", "array"), var("TmpVV", S_LIN, "array"),
                                 var("TmpTN", "name", "array"), var("TmpTP", "string", "array"),
                                 var("TmpRots", S_ROT, "array"), var("TmpLocal", S_TF, "array"), var("TmpRootLocal", S_TF), var("TmpZ", "float"),
                                 var("Pins", "name", "map", value_type="object:" + E_CONSTR), var("Pinned", "name", "array"), var("PinLoop", "name", "array"),
                                 var("MarkerBones", "name", "array"), var("Markers", "object:" + E_SMC, "array"),
                                 var("MarkerMids", "object:" + E_MIDC, "array"), var("MarkersBuilt", "bool"), var("MarkTmp", "object:" + E_SMC),
                                 var("DetailBones", "name", "array"), var("Details", "object:" + E_SMC, "array"), var("DetailMids", "object:" + E_MIDC, "array"),
                                 var("DetailGroup", "int", "array"), var("DetailBuilt", "bool"), var("DetailHold", "name"),
                                 var("DetailPose", "struct:" + S_POSE), var("ThumbSpread", "float", "array"), var("GazeSide", "float"), var("GazeUp", "float"),
                                 var("GazeSet", "bool"), var("LidL", "float"), var("LidR", "float"), var("TmpGaze", S_VEC),
                                 var("TurnPose", "struct:" + S_POSE), var("TurnIdx", "int"), var("TurnRot", S_ROT), var("TurnJoint", S_VEC), var("TurnParent", S_TF),
                                 var("TurnPointLocal", S_VEC), var("TurnAxisLocal", S_VEC), var("TurnFar", S_VEC), var("TurnFarDist", "float"),
                                 var("TmpTurnDelta", S_ROT), var("TmpTurnWorld", S_ROT), var("TmpTurnLocal", S_ROT),
                                 # attackable (ragproxy.py): zombies attack it through an invisible proxy figure; HitPose / HitUntil / HitActive: a frozen figure's jolt
                                 var("Attackable", "bool"), var("HitPose", "struct:" + S_POSE), var("HitUntil", "float"), var("HitActive", "bool")],
                      functions=[f_setup_body(), f_load_path(), f_collect_mats(), f_apply_mats(), f_collect_parts(), f_build_from_parts(), f_copy_from(), f_set_pose(), f_activate(), f_freeze(), f_toggle_joint(), f_lock_all(), f_free_all(), f_toggle_loose(), f_loose_root(), f_loosen_below(), f_drop_lock(), f_make_lock(),
                                 f_floor_below(), f_lowest_bone(), f_pose_data(), f_merge_rotations(), f_root_local(), f_apply_pose_data(),
                                 f_make_pin(), f_pin(), f_unpin(), f_clear_pins(), f_unpin_all(), f_build_markers(), f_show_markers(), f_refresh_markers(), f_set_joint_states(), f_has_detail(), f_detail_kind(), f_finger_of(), f_finger_tip_base(), f_build_detail_markers(), f_show_details(), f_detail_tick(), f_detail_begin(), f_detail_put(), f_detail_commit(), f_curl_rot(), f_lid_rot(), f_curl_finger(), f_finger_curl_of(), f_apply_hand_pose(), f_apply_lids(), f_eye_lids_step(), f_gaze_from_target(), f_set_gaze(), f_look_at(), f_reset_eyes(),
                                 f_turn_delta(), f_turn_local(), f_begin_turn(), f_apply_turn(), f_turn_toward(), f_twist(), f_hit_jolt(), f_hit_back()],
                      event_graph=test_events())]


if __name__ == "__main__":
    write(os.path.join(os.path.dirname(__file__), "..", "28_ragdoll.json"), build())
