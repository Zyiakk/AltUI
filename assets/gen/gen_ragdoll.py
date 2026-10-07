#!/usr/bin/env python3
"""Generates assets/28_ragdoll.json: BP_AltUIRagdoll, a copy of a character as a physics puppet (prototype, see
docs/notes/2026-10-05-ragdolls-machbarkeit.md). No game logic of its own: Copy From takes over the mesh, materials and morph
values of a character and every visible mesh attached to it (clothes and hair follow the body via the master pose, static
meshes sit at their socket); Go Ragdoll switches the body to physics like the game's own Enable Ragdoll Ex; Toggle Lock
stiffens the joint between a bone and its parent in its current angle with a runtime PhysicsConstraintComponent (the game
does the same when Jodi drags a body)."""
import os, sys, re; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *

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
    g.chain("entry", "sp", "sa", "cj", "fe"); g.chain("fe", "ml"); return fn("Activate", graph=g)


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
    g.chain("entry", "sn", "sp", "lv", "fe"); g.chain("fe", "dc"); g.chain("fe:Completed", "cl", "off", "sa", "grv")
    return fn("Freeze", graph=g)


def f_toggle_joint():
    """A joint in or out of LockedJoints; while active its constraint comes / goes with it."""
    g = G(); g.get("gj", "LockedJoints"); g.call("has", K_ARR, "Array_Contains", inp={"TargetArray": "@gj.LockedJoints", "ItemToFind": "@entry.bone"}); g.branch("bh", "@has.ReturnValue")
    g.get("gj2", "LockedJoints"); g.call("rm", K_ARR, "Array_RemoveItem", inp={"TargetArray": "@gj2.LockedJoints", "Item": "@entry.bone"}); g.n("dl", "call_self", function="Drop Lock", inp={"bone": "@entry.bone"})
    g.get("gj3", "LockedJoints"); g.call("ad", K_ARR, "Array_Add", inp={"TargetArray": "@gj3.LockedJoints", "NewItem": "@entry.bone"})
    g.get("ga", "Active"); g.branch("ba", "@ga.Active"); g.n("ml", "call_self", function="Make Lock", inp={"bone": "@entry.bone"})
    g.chain("entry", "bh", "rm", "dl"); g.chain("bh:else", "ad", "ba", "ml"); return fn("Toggle Joint", [param("bone", "name")], graph=g)


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
    g.chain("entry", "bh", "rm"); g.chain("bh:else", "ad"); return fn("Toggle Loose", [param("bone", "name")], graph=g)


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
                                 var("TmpRots", S_ROT, "array"), var("TmpLocal", S_TF, "array"), var("TmpRootLocal", S_TF), var("TmpZ", "float")],
                      functions=[f_setup_body(), f_load_path(), f_collect_mats(), f_apply_mats(), f_collect_parts(), f_build_from_parts(), f_copy_from(), f_set_pose(), f_activate(), f_freeze(), f_toggle_joint(), f_lock_all(), f_free_all(), f_toggle_loose(), f_loose_root(), f_loosen_below(), f_drop_lock(), f_make_lock(),
                                 f_floor_below(), f_lowest_bone(), f_pose_data(), f_merge_rotations(), f_root_local(), f_apply_pose_data()],
                      event_graph=test_events())]


if __name__ == "__main__":
    write(os.path.join(os.path.dirname(__file__), "..", "28_ragdoll.json"), build())
