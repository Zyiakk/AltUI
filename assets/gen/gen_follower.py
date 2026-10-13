"""Generates assets/29b_follower.json: BP_AltUIFollower, the figure AltUI spawns for a follower / NPC
(docs/specs/2026-10-09-followers-design.md). A child of the game's NPC_Female (AI, bag, weapons, orders stay the game's):
the game never saves it (Need to Save -> false; AltUI keeps its own save) and it never mutates. Its look comes from a look
of the Looks tab as data (S_RagPart list + the body's morph values, see the Ragdolls figures): Apply Npc Appearance - which
the game calls in On Begun Play, 0.2 s after the spawn - puts that look on instead of the game's NPC appearance. Clothes and
hair are the game's (docs/specs/2026-10-12-follower-echte-kleidung-design.md): Set Look puts the pieces into the figure before
its start, the game's On Begun Play puts them on (colour, damage, heels, body mask)."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *
from gen_ragdoll import f_load_path, f_apply_mats, S_RAGPART, ident_tf, E_SKM, E_SKIN, E_STM, E_MESHC, E_SCENEC, E_ACTC, E_SKMESH, E_STMESH, E_CHAR, E_MIDC, E_PRIMC

FOLLOWER = M + "/BP_AltUIFollower"


def f_need_to_save():
    """Plots_GameState.Save Game Ex writes every Character_Base whose Need to Save is true into the game's save (spawned ones
    under Spawned Actor, re-spawned on load) - ours never: AltUI saves and loads them itself."""
    g = G(); g.call("no", K_MATH, "BooleanAND", inp={"A": "false", "B": "false"}); g.link("no.ReturnValue", "return.yes")
    return fn("Need to Save", graph=g, pure=True, override=True)


def f_apply_look():
    """LookParts / LookMorphN / LookMorphV onto this figure: the previous look's components go, every other mesh of the figure
    (the game's hair and clothes) is hidden; part 0 becomes the body (her Mesh: mesh, materials, morphs), every other part a new
    component on the Mesh - skeletal ones follow it (master pose), static ones sit at their socket. The mesh swap makes a new
    anim instance: Character_Base.Anim Blueprint is pointed at it (the game set it once)."""
    g = G(); g.get("gm", "Mesh"); mesh = "@gm.Mesh"
    # the previous look
    g.get("glc", "LookComps"); g.foreach("fo", "@glc.LookComps"); g.call("dc", E_ACTC, "K2_DestroyComponent", inp={"self": "@fo.Array Element", "Object": "@fo.Array Element"})
    g.get("glc2", "LookComps"); g.call("clc", K_ARR, "Array_Clear", inp={"TargetArray": "@glc2.LookComps"})
    # the game's meshes out of sight (the Mesh itself stays: it becomes the body)
    g.call("cmp", E_ACTOR, "K2_GetComponentsByClass", inp={"ComponentClass": E_MESHC}); g.foreach("fh", "@cmp.ReturnValue")
    g.get("gm1", "Mesh"); g.call("nm", K_MATH, "NotEqual_ObjectObject", inp={"A": "@fh.Array Element", "B": "@gm1.Mesh"})
    # ... and not the game's clothes and hair: since 2026-10-12 they are hers (Wear The Clothes / Change Hairstyle Ex)
    g.cast("icc", P_CC, "@fh.Array Element"); g.call("vcc", K_SYS, "IsValid", inp={"Object": "@icc.AsClothes Comp"})
    g.cast("ihc", P_HAIRC, "@fh.Array Element"); g.call("vhc", K_SYS, "IsValid", inp={"Object": "@ihc.AsHair Comp"})
    g.call("ogm", K_MATH, "BooleanOR", inp={"A": "@vcc.ReturnValue", "B": "@vhc.ReturnValue"}); g.call("nog", K_MATH, "Not_PreBool", inp={"A": "@ogm.ReturnValue"})
    g.call("hdo", K_MATH, "BooleanAND", inp={"A": "@nm.ReturnValue", "B": "@nog.ReturnValue"}); g.branch("bnm", "@hdo.ReturnValue")
    g.cast("chs", E_SCENEC, "@fh.Array Element"); g.call("hide", E_SCENEC, "SetVisibility", inp={"self": "@chs.AsScene Component", "bNewVisibility": "false", "bPropagateToChildren": "false"})
    # the body
    g.get("glp", "LookParts"); g.call("ln", K_ARR, "Array_Length", inp={"TargetArray": "@glp.LookParts"}); g.call("has", K_MATH, "Greater_IntInt", inp={"A": "@ln.ReturnValue", "B": "0"}); g.branch("bhas", "@has.ReturnValue")
    g.get("glp0", "LookParts"); g.call("p0", K_ARR, "Array_Get", inp={"TargetArray": "@glp0.LookParts", "Index": "0"}); g.brk("b0", S_RAGPART, "@p0.Item")
    g.n("l0", "call_self", function="Load Path", inp={"path": "@b0.Mesh"}); g.cast("c0", E_SKMESH, "@l0.object", pure=False, miss="ignore")
    g.get("gm2", "Mesh"); g.call("ssk", E_SKIN, "SetSkeletalMesh", inp={"self": "@gm2.Mesh", "NewMesh": "@c0.AsSkeletal Mesh", "bReinitPose": "true"})
    g.get("gm3", "Mesh"); g.call("show", E_SCENEC, "SetVisibility", inp={"self": "@gm3.Mesh", "bNewVisibility": "true", "bPropagateToChildren": "false"})
    g.get("gm4", "Mesh"); g.n("am0", "call_self", function="Apply Mats", inp={"mesh": "@gm4.Mesh", "mats": "@b0.Mats"})
    g.get("gm5", "Mesh"); g.call("gai", E_SKM, "GetAnimInstance", inp={"self": "@gm5.Mesh"}); g.set("sab", "Anim Blueprint", inp={"Anim Blueprint": "@gai.ReturnValue"})
    # the body's material instance for update body mask (MaskThreshold): slot 0, as Begin Play Ex makes it - the old one is gone with the mesh swap
    g.get("gmb", "Mesh"); g.call("gm0", E_PRIMC, "GetMaterial", inp={"self": "@gmb.Mesh", "ElementIndex": "0"}); g.cast("cbm", E_MIDC, "@gm0.ReturnValue", pure=False, miss="ignore")
    g.self_("me2"); g.set("sbm", "Body Material", cls=P_CPB, inp={"self": "@me2.self", "Body Material": "@cbm.AsMaterial Instance Dynamic"})
    g.get("gmb2", "Mesh"); g.call("nbm", E_PRIMC, "CreateDynamicMaterialInstance", inp={"self": "@gmb2.Mesh", "ElementIndex": "0", "SourceMaterial": "None", "OptionalName": "None"})
    g.set("sbm2", "Body Material", cls=P_CPB, inp={"self": "@me2.self", "Body Material": "@nbm.ReturnValue"})
    # its morph values (face, body mods)
    g.get("gmn", "LookMorphN"); g.foreach("fmn", "@gmn.LookMorphN"); g.get("gmv", "LookMorphV"); g.call("mv", K_ARR, "Array_Get", inp={"TargetArray": "@gmv.LookMorphV", "Index": "@fmn.Array Index"})
    g.get("gm6", "Mesh"); g.call("smv", E_SKM, "SetMorphTarget", inp={"self": "@gm6.Mesh", "MorphTargetName": "@fmn.Array Element", "Value": "@mv.Item", "bRemoveZeroWeight": "true"})
    # the game's hair (Hair_Comps follow hats in update body mask) in the look's colour; an old record (no LookHair) keeps its copied hair
    g.get("glh", "LookHair"); g.call("hh", K_MATH, "NotEqual_NameName", inp={"A": "@glh.LookHair", "B": "None"}); g.branch("bhh", "@hh.ReturnValue")
    g.self_("me3"); g.call("chx", P_CPB, "Change Hairstyle Ex", inp={"self": "@me3.self", "hairstyle": "@glh.LookHair"})
    g.get("ghc", "Hair Comps", cls=P_CPB); g.link("me3.self", "ghc.self"); g.foreach("fhc", "@ghc.Hair Comps"); g.get("glhc", "LookHairColor")
    g.call("hcc", P_HAIRC, "Change Color", inp={"self": "@fhc.Array Element", "color": "@glhc.LookHairColor"})
    # every other part
    g.get("glp1", "LookParts"); g.foreach("fp", "@glp1.LookParts"); g.call("gt0", K_MATH, "Greater_IntInt", inp={"A": "@fp.Array Index", "B": "0"}); g.branch("bgt", "@gt0.ReturnValue")
    g.brk("bp", S_RAGPART, "@fp.Array Element"); g.n("lp", "call_self", function="Load Path", inp={"path": "@bp.Mesh"}); g.branch("bsk", "@bp.Skeletal")
    # skeletal: on the Mesh (not the capsule), following its bones
    g.call("nk", E_ACTOR, "AddComponentByClass", inp={"Class": E_SKM, "bManualAttachment": "true", "RelativeTransform": ident_tf(g), "bDeferredFinish": "false"})
    g.cast("cnk", E_SKM, "@nk.ReturnValue"); nk = "@cnk.AsSkeletal Mesh Component"; g.cast("ckm", E_SKMESH, "@lp.object")
    g.get("gm7", "Mesh"); g.call("katt", E_SCENEC, "K2_AttachToComponent", inp={"self": nk, "Parent": "@gm7.Mesh", "SocketName": "None", "LocationRule": "SnapToTarget",
                                                                                          "RotationRule": "SnapToTarget", "ScaleRule": "SnapToTarget", "bWeldSimulatedBodies": "false"})
    g.call("ksk", E_SKIN, "SetSkeletalMesh", inp={"self": nk, "NewMesh": "@ckm.AsSkeletal Mesh", "bReinitPose": "true"})
    g.get("gm8", "Mesh"); g.call("kmp", E_SKIN, "SetMasterPoseComponent", inp={"self": nk, "NewMasterBoneComponent": "@gm8.Mesh", "bForceUpdate": "true"})
    g.n("amk", "call_self", function="Apply Mats", inp={"mesh": nk, "mats": "@bp.Mats"})
    g.get("glk", "LookComps"); g.call("ak", K_ARR, "Array_Add", inp={"TargetArray": "@glk.LookComps", "NewItem": nk})
    # static: at its socket
    g.call("ns", E_ACTOR, "AddComponentByClass", inp={"Class": E_STM, "bManualAttachment": "true", "RelativeTransform": ident_tf(g), "bDeferredFinish": "false"})
    g.cast("cns", E_STM, "@ns.ReturnValue"); ns = "@cns.AsStatic Mesh Component"; g.cast("csm", E_STMESH, "@lp.object")
    g.call("ssm", E_STM, "SetStaticMesh", inp={"self": ns, "NewMesh": "@csm.AsStatic Mesh"})
    g.call("srt", E_SCENEC, "K2_SetRelativeTransform", inp={"self": ns, "NewTransform": "@bp.Rel", "bSweep": "false", "bTeleport": "true"})
    g.get("gm9", "Mesh"); g.call("att", E_SCENEC, "K2_AttachToComponent", inp={"self": ns, "Parent": "@gm9.Mesh", "SocketName": "@bp.Socket", "LocationRule": "KeepRelative",
                                                                                          "RotationRule": "KeepRelative", "ScaleRule": "KeepRelative", "bWeldSimulatedBodies": "false"})
    g.n("ams", "call_self", function="Apply Mats", inp={"mesh": ns, "mats": "@bp.Mats"})
    g.get("gls", "LookComps"); g.call("as", K_ARR, "Array_Add", inp={"TargetArray": "@gls.LookComps", "NewItem": ns})
    g.chain("entry", "fo"); g.chain("fo", "dc"); g.chain("fo:Completed", "clc", "fh"); g.chain("fh", "bnm", "hide")
    g.chain("fh:Completed", "bhas", "l0", "c0", "ssk", "show", "am0", "sab", "cbm", "sbm", "fmn"); g.chain("cbm:CastFailed", "nbm", "sbm2", "fmn"); g.chain("fmn", "smv")
    g.chain("fmn:Completed", "bhh", "chx", "fhc"); g.chain("fhc", "hcc"); g.chain("fhc:Completed", "fp"); g.chain("bhh:else", "fp"); g.chain("fp", "bgt", "lp", "bsk", "nk", "katt", "ksk", "kmp", "amk", "ak"); g.chain("bsk:else", "ns", "ssm", "srt", "att", "ams", "as")
    return fn("Apply Look", graph=g)


def f_init_npc_appearance():
    """The game's On Begun Play rolls a random NPC here (skin, hair, head, name) and, with Save Player Clothes empty, a random clothes
    preset into the bag - which Character_Player_Base.On Begun Play then puts on, over our look. The figure's look is ours: nothing."""
    return fn("Init Npc Appearance", graph=G(), override=True)


def f_check_appearence():
    """Character_Player_Base.On Begun Play: a figure without clothes components gets the game's whole default outfit (Default Clothes)
    when nudity is off - Jodi only ever gets underwear (ui-test-88 #10/#11: a look without clothes came back fully dressed). The
    game runs its underwear rule only after Wear These Clothes, which a look without clothes never reaches: run it here instead
    (Is Nude Allowed = AltUI's option "underwear may be taken off")."""
    g = G(); g.self_("me"); g.call("cc", P_CPB, "check clothes covering", inp={"self": "@me.self"}); g.call("bm", P_CPB, "update body mask", inp={"self": "@me.self"})
    g.chain("entry", "cc", "bm")
    return fn("Check Appearence", graph=g, override=True)


def f_apply_npc_appearance():
    """The game's On Begun Play calls this (started by on Spawn in Runtime, see Fol Spawn; before it sets the anim class and the order):
    our look instead of the NPC's skin / hair / head. Without look data nothing happens (no hair, the NPC's default materials)."""
    g = G(); g.get("glp", "LookParts"); g.call("ln", K_ARR, "Array_Length", inp={"TargetArray": "@glp.LookParts"})
    g.call("has", K_MATH, "Greater_IntInt", inp={"A": "@ln.ReturnValue", "B": "0"}); g.branch("b", "@has.ReturnValue"); g.n("al", "call_self", function="Apply Look")
    g.chain("entry", "b", "al")
    return fn("Apply Npc Appearance", graph=g, override=True)


def f_set_look():
    """A new look (Look ändern, or right after the spawn - On Begun Play applies it once more, harmlessly). Its clothes go into the figure
    before the game's start: Character_Player_Base.On Begun Play puts Save Player Clothes on (Wear The Clothes: colour from Clothes
    Colors, damage from Save Clothes Damaged, heels, body mask) - as the game's Init Npc Appearance does with its presets."""
    g = G(); g.set("sp", "LookParts", inp={"LookParts": "@entry.parts"}); g.set("sn", "LookMorphN", inp={"LookMorphN": "@entry.names"})
    g.set("sv", "LookMorphV", inp={"LookMorphV": "@entry.values"}); g.set("sh", "LookHair", inp={"LookHair": "@entry.hair"}); g.set("shc", "LookHairColor", inp={"LookHairColor": "@entry.haircolor"})
    g.self_("me")
    g.set("spc", "Save Player Clothes", cls=P_CPB, inp={"self": "@me.self", "Save Player Clothes": "@entry.worn"})
    g.get("gbg", "Bag", cls=P_CPB); g.link("me.self", "gbg.self"); g.call("apc", P_BAG, "Append Clothes", inp={"self": "@gbg.Bag", "Clothes": "@entry.clothes"})
    g.set("scc", "Clothes Colors", cls=P_CPB, inp={"self": "@me.self", "Clothes Colors": "@entry.colors"})
    g.set("scd", "Save Clothes Damaged", cls=P_CPB, inp={"self": "@me.self", "Save Clothes Damaged": "@entry.damage"})
    g.n("al", "call_self", function="Apply Look")
    g.chain("entry", "sp", "sn", "sv", "sh", "shc", "spc", "apc", "scc", "scd", "al")
    return fn("Set Look", [param("parts", "struct:" + S_RAGPART, "array"), param("names", "name", "array"), param("values", "float", "array"),
                           param("clothes", "name", "array"), param("worn", "name", "array"), param("colors", "name", "map", value_type=S_LINCOLOR),
                           param("damage", "name", "map", value_type="float"), param("hair", "name"), param("haircolor", S_LINCOLOR)], graph=g)


VARS = [var("FollowerId", "name"), var("LookParts", "struct:" + S_RAGPART, "array"), var("LookMorphN", "name", "array"), var("LookMorphV", "float", "array"),
        var("LookComps", "object:" + E_SCENEC, "array"), var("TmpMid", "object:" + E_MIDC), var("LookHair", "name"), var("LookHairColor", S_LINCOLOR)]


def build():
    return [blueprint(FOLLOWER, P_NPCF, variables=VARS,
                      functions=[f_need_to_save(), fn("Mutate", graph=G(), override=True), fn("delay to mutant", graph=G(), override=True),
                                 f_load_path(), f_apply_mats(), f_apply_look(), f_init_npc_appearance(), f_check_appearence(), f_apply_npc_appearance(), f_set_look()])]


if __name__ == "__main__":
    write(os.path.join(os.path.dirname(__file__), "..", "29b_follower.json"), build())
