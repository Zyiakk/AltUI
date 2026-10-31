"""Generates assets/29b_follower.json: BP_AltUIFollower, the figure AltUI spawns for a follower / NPC
(docs/specs/2026-10-09-followers-design.md). A child of the game's NPC_Female (AI, bag, weapons, orders stay the game's):
the game never saves it (Need to Save -> false; AltUI keeps its own save) and it never mutates. Its look comes from a look
of the Looks tab as data (S_RagPart list + the body's morph values, see the Ragdolls figures): Apply Npc Appearance - which
the game calls in On Begun Play, 0.2 s after the spawn - puts that look on instead of the game's NPC appearance. Clothes and
hair are the game's (docs/specs/2026-10-12-follower-echte-kleidung-design.md): Set Look puts the pieces into the figure before
its start, the game's On Begun Play puts them on (colour, damage, heels, body mask)."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *
import multislot as ms
from gen_ragdoll import f_load_path, f_apply_mats, S_RAGPART, ident_tf, E_SKM, E_SKIN, E_STM, E_MESHC, E_SCENEC, E_ACTC, E_SKMESH, E_STMESH, E_CHAR, E_MIDC, E_PRIMC

FOLLOWER = M + "/BP_AltUIFollower"


def f_need_to_save():
    """Plots_GameState.Save Game Ex writes every Character_Base whose Need to Save is true into the game's save (spawned ones
    under Spawned Actor, re-spawned on load) - ours never: AltUI saves and loads them itself."""
    g = G(); g.call("no", K_MATH, "BooleanAND", inp={"A": "false", "B": "false"}); g.link("no.ReturnValue", "return.yes")
    return fn("Need to Save", graph=g, pure=True, override=True)


def f_is_npc():
    """An enemy figure (IsEnemy, docs/notes/2026-10-30-look-als-gegner.md) is no NPC to the others: Character_NPC.on Damage Event drops
    hits whose murderer is an NPC - without this its shots would not hurt followers. Else as Character_NPC's (not Is Changed: a
    figure never mutates)."""
    g = G(); g.get("ge", "IsEnemy"); g.call("n", K_MATH, "Not_PreBool", inp={"A": "@ge.IsEnemy"}); g.link("n.ReturnValue", "return.yes")
    return fn("is Npc ?", outputs=[param("yes", "bool")], graph=g, pure=True, override=True)


def f_on_damage_event():
    """An enemy figure takes hits from NPCs (followers): Character_NPC's own drops them (murderer.is Npc ?, @367) - it gets them
    without a murderer then (no 'under attack' from them, no kill credit). Every other hit as the game does it."""
    ins = {"damage": "@entry.damage", "damage type": "@entry.damage type", "weapon actor": "@entry.weapon actor", "hit info": "@entry.hit info",
           "location": "@entry.location", "is explosive": "@entry.is explosive"}
    g = G(); g.get("ge", "IsEnemy"); g.call("mv", K_SYS, "IsValid", inp={"Object": "@entry.murderer"}); g.call("mn", P_CB, "is Npc ?", inp={"self": "@entry.murderer"})
    g.call("a1", K_MATH, "BooleanAND", inp={"A": "@ge.IsEnemy", "B": "@mv.ReturnValue"}); g.call("a2", K_MATH, "BooleanAND", inp={"A": "@a1.ReturnValue", "B": "@mn.yes"}); g.branch("b", "@a2.ReturnValue")
    g.n("p0", "call_parent", function="on Damage Event", cls=P_CNPC, inp=dict(ins, murderer="None"))
    g.n("p1", "call_parent", function="on Damage Event", cls=P_CNPC, inp=dict(ins, murderer="@entry.murderer"))
    g.chain("entry", "b", "p0"); g.chain("b:else", "p1")
    return fn("on Damage Event", [param("damage", "float"), param("damage type", "object:/Script/Engine.DamageType"), param("murderer", "object:" + P_CB),
                                  param("weapon actor", "object:/Script/Engine.Actor"), param("hit info", "struct:/Script/Engine.HitResult", ref=True),
                                  param("location", "struct:/Script/CoreUObject.Vector"), param("is explosive", "bool")], graph=g, override=True)


def f_try_to_destruct_clothing():
    """The game tears a piece off (Character_Player_Base.Try to Destruct Clothing: Remove Clothing From Bag, Take off, Start Destruction):
    gone for good. What was worn before and is not now goes into LostPieces - the record keeps it (Fol Sync), "Restore outfit" gives
    it back (play test 2026-10-30: destroyed pieces did not come back)."""
    g = G(); g.self_("me"); g.call("wb", P_CPB, "Get Wearing Clothes Names", inp={"self": "@me.self"}); g.set("sb", "WornBefore", inp={"WornBefore": "@wb.clothes list"})
    g.n("pp", "call_parent", function="Try to Destruct Clothing", cls=P_CPB)
    g.self_("me2"); g.call("wa", P_CPB, "Get Wearing Clothes Names", inp={"self": "@me2.self"}); g.get("gb", "WornBefore"); g.foreach("fe", "@gb.WornBefore")
    g.call("still", K_ARR, "Array_Contains", inp={"TargetArray": "@wa.clothes list", "ItemToFind": "@fe.Array Element"}); g.branch("bs", "@still.ReturnValue")
    g.get("gl", "LostPieces"); g.call("al", K_ARR, "Array_AddUnique", inp={"TargetArray": "@gl.LostPieces", "NewItem": "@fe.Array Element"})
    g.chain("entry", "wb", "sb", "pp", "wa", "fe"); g.chain("fe", "bs"); g.chain("bs:else", "al")
    return fn("Try to Destruct Clothing", graph=g, override=True)


def f_is_ragdoll_or_dying():
    """Not attackable (NotTarget, gear menu "attackable" off): to the zombies' and mercenaries' target check (AI_Controller.is my target
    Character asks this first) the figure lies on the ground - nobody picks it as a target, yet it takes damage (bCanBeDamaged stays;
    being unhurt is the "Invulnerable" chip). Before 2026-10-30 bCanBeDamaged = false made an unattackable figure immortal. Else the
    game's (Character_Base: Is Ragdoll ?)."""
    g = G(); g.get("gn", "NotTarget"); g.self_("me"); g.call("ir", P_CB, "Is Ragdoll ?", inp={"self": "@me.self"})
    g.call("o", K_MATH, "BooleanOR", inp={"A": "@gn.NotTarget", "B": "@ir.yes"}); g.link("o.ReturnValue", "return.yes")
    return fn("Is Ragdoll or Dying", outputs=[param("yes", "bool")], graph=g, pure=True, override=True)


def f_count_weapon_ammo():
    """Infinite ammo (InfAmmo, docs/notes/2026-10-18-follower-munition-und-npc-typen.md): the game reloads a gun when this is > 0
    (Npc_Controller.Try to Reload) and fills the magazine with Min(this, missing) before it takes that many from the bag
    (Weapon_Gun_Base.New Mag Installed) - with 9999 the magazine is filled and the take fails, the bag stays as it is. Off: the
    game's own count, the weapon's ammo in her bag."""
    g = G(); g.call("an", P_WEAPON, "Get Ammo Name", inp={"self": "@entry.weapon"}); g.self_("me"); g.get("gb", "Bag", cls=P_CPB); g.link("me.self", "gb.self")
    g.call("ci", P_BAG, "Count Items", inp={"self": "@gb.Bag", "item name": "@an.ammo name"}); g.get("gi", "InfAmmo")
    g.call("sel", K_MATH, "SelectInt", inp={"A": "9999", "B": "@ci.count", "bPickA": "@gi.InfAmmo"}); g.link("sel.ReturnValue", "return.num")
    return fn("Count Weapon Ammo", [param("weapon", "object:" + P_WEAPON)], [param("num", "int")], graph=g, pure=True, override=True)


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
    g.n("amt", "call_self", function="Apply Makeup Tex")   # after the body's materials: they came with Jodi's make-up target
    g.n("ast", "call_self", function="Apply Skin Tex")   # ... and with her mutated skin's target (mutation look)
    g.chain("fh:Completed", "bhas", "l0", "c0", "ssk", "show", "am0", "sab", "cbm", "sbm", "amt", "ast", "fmn"); g.chain("cbm:CastFailed", "nbm", "sbm2", "amt"); g.chain("fmn", "smv")
    g.chain("fmn:Completed", "bhh", "chx", "fhc"); g.chain("fhc", "hcc"); g.chain("fhc:Completed", "fp"); g.chain("bhh:else", "fp"); g.chain("fp", "bgt", "lp", "bsk", "nk", "katt", "ksk", "kmp", "amk", "ak"); g.chain("bsk:else", "ns", "ssm", "srt", "att", "ams", "as")
    return fn("Apply Look", graph=g)


def f_apply_makeup_tex():
    """LookMakeupTex (the figure's own make-up, drawn by the manager) into every material of the body that samples MakeupTex -
    the copied skin points at the game's one Skin_RenderTarget, which always holds Jodi's make-up. Without it nothing changes."""
    g = G(); g.get("gt", "LookMakeupTex"); g.call("vt", K_SYS, "IsValid", inp={"Object": "@gt.LookMakeupTex"}); g.branch("bt", "@vt.ReturnValue")
    g.get("gm", "Mesh"); g.call("ms", E_MESHC, "GetMaterials", inp={"self": "@gm.Mesh"}); g.foreach("fm", "@ms.ReturnValue")
    g.cast("cm", E_MIDC, "@fm.Array Element"); g.call("vm", K_SYS, "IsValid", inp={"Object": "@cm.AsMaterial Instance Dynamic"})
    g.call("gtp", E_MIDC, "K2_GetTextureParameterValue", inp={"self": "@cm.AsMaterial Instance Dynamic", "ParameterName": "MakeupTex"})
    g.call("vp", K_SYS, "IsValid", inp={"Object": "@gtp.ReturnValue"}); g.call("ok", K_MATH, "BooleanAND", inp={"A": "@vm.ReturnValue", "B": "@vp.ReturnValue"}); g.branch("bok", "@ok.ReturnValue")
    g.get("gt2", "LookMakeupTex"); g.call("st", E_MIDC, "SetTextureParameterValue", inp={"self": "@cm.AsMaterial Instance Dynamic", "ParameterName": "MakeupTex", "Value": "@gt2.LookMakeupTex"})
    g.chain("entry", "bt", "fm"); g.chain("fm", "gtp", "bok", "st")   # the getter is impure (BlueprintCallable)
    return fn("Apply Makeup Tex", graph=g)


def f_apply_skin_tex():
    """LookSkinTex (the look's mutated skin, drawn by the manager: Mutation Skin Tex) as MainTex of every skin material of the body (samples
    MakeupTex) - its materials come back from paths, a render target has none. Without it nothing changes."""
    g = G(); g.get("gt", "LookSkinTex"); g.call("vt", K_SYS, "IsValid", inp={"Object": "@gt.LookSkinTex"}); g.branch("bt", "@vt.ReturnValue")
    g.get("gm", "Mesh"); g.call("ms", E_MESHC, "GetMaterials", inp={"self": "@gm.Mesh"}); g.foreach("fm", "@ms.ReturnValue")
    g.cast("cm", E_MIDC, "@fm.Array Element"); g.call("vm", K_SYS, "IsValid", inp={"Object": "@cm.AsMaterial Instance Dynamic"})
    g.call("gtp", E_MIDC, "K2_GetTextureParameterValue", inp={"self": "@cm.AsMaterial Instance Dynamic", "ParameterName": "MakeupTex"})   # the skin: lashes / eyes have MainTex too
    g.call("vp", K_SYS, "IsValid", inp={"Object": "@gtp.ReturnValue"}); g.call("ok", K_MATH, "BooleanAND", inp={"A": "@vm.ReturnValue", "B": "@vp.ReturnValue"}); g.branch("bok", "@ok.ReturnValue")
    g.get("gt2", "LookSkinTex"); g.call("st", E_MIDC, "SetTextureParameterValue", inp={"self": "@cm.AsMaterial Instance Dynamic", "ParameterName": "MainTex", "Value": "@gt2.LookSkinTex"})
    g.chain("entry", "bt", "fm"); g.chain("fm", "gtp", "bok", "st")
    return fn("Apply Skin Tex", graph=g)


def f_init_npc_appearance():
    """The game's On Begun Play rolls a random NPC here (skin, hair, head, name) and, with Save Player Clothes empty, a random clothes
    preset into the bag - which Character_Player_Base.On Begun Play then puts on, over our look. The figure's look is ours: nothing."""
    return fn("Init Npc Appearance", graph=G(), override=True)


def f_check_appearence():
    """Character_Player_Base.On Begun Play: a figure without clothes components gets the game's whole default outfit (Default Clothes)
    when nudity is off - Jodi only ever gets underwear (ui-test-88 #10/#11: a look without clothes came back fully dressed). The
    game runs its underwear rule only after Wear These Clothes, which a look without clothes never reaches: run it here instead
    (Is Nude Allowed = AltUI's option "underwear may be taken off").
    Before that: Wear These Clothes kept one piece per slot - the look's other pieces of a slot go on next to it (multislot)."""
    g = G(); g.self_("me"); g.get("glw", "LookWorn"); g.foreach("fw", "@glw.LookWorn")   # On Begun Play has cleared Save Player Clothes by now
    g.call("iw", P_CPB, "is clothes wearing", inp={"self": "@me.self", "clothes name": "@fw.Array Element"}); g.call("nw", K_MATH, "Not_PreBool", inp={"A": "@iw.yes"})
    g.call("ex", K_DT, "DoesDataTableRowExist", inp={"Table": P_CT, "RowName": "@fw.Array Element"}); g.call("go", K_MATH, "BooleanAND", inp={"A": "@nw.ReturnValue", "B": "@ex.ReturnValue"}); g.branch("bgo", "@go.ReturnValue")
    g.n("wk", "call_self", function="Wear Kept", inp={"char": "@me.self", "name": "@fw.Array Element", "check covering": "false", "update mask": "false", "ignore compatible": "true", "keep": "true"})
    g.call("cc", P_CPB, "check clothes covering", inp={"self": "@me.self"}); g.call("bm", P_CPB, "update body mask", inp={"self": "@me.self"})
    g.chain("entry", "fw"); g.chain("fw", "ex", "bgo", "wk"); g.chain("fw:Completed", "cc", "bm")   # DoesDataTableRowExist is an exec node
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
    g.set("spc", "Save Player Clothes", cls=P_CPB, inp={"self": "@me.self", "Save Player Clothes": "@entry.worn"}); g.set("slw", "LookWorn", inp={"LookWorn": "@entry.worn"})
    g.get("gbg", "Bag", cls=P_CPB); g.link("me.self", "gbg.self"); g.call("apc", P_BAG, "Append Clothes", inp={"self": "@gbg.Bag", "Clothes": "@entry.clothes"})
    g.set("scc", "Clothes Colors", cls=P_CPB, inp={"self": "@me.self", "Clothes Colors": "@entry.colors"})
    g.set("scd", "Save Clothes Damaged", cls=P_CPB, inp={"self": "@me.self", "Save Clothes Damaged": "@entry.damage"})
    g.n("al", "call_self", function="Apply Look")
    g.chain("entry", "sp", "sn", "sv", "sh", "shc", "spc", "slw", "apc", "scc", "scd", "al")
    return fn("Set Look", [param("parts", "struct:" + S_RAGPART, "array"), param("names", "name", "array"), param("values", "float", "array"),
                           param("clothes", "name", "array"), param("worn", "name", "array"), param("colors", "name", "map", value_type=S_LINCOLOR),
                           param("damage", "name", "map", value_type="float"), param("hair", "name"), param("haircolor", S_LINCOLOR)], graph=g)


VARS = [var("FollowerId", "name"), var("LookParts", "struct:" + S_RAGPART, "array"), var("LookMorphN", "name", "array"), var("LookMorphV", "float", "array"),
        var("LookComps", "object:" + E_SCENEC, "array"), var("TmpMid", "object:" + E_MIDC), var("LookHair", "name"), var("LookHairColor", S_LINCOLOR), var("LookWorn", "name", "array"),
        var("LookMakeupTex", "object:/Script/Engine.TextureRenderTarget2D"), var("InfAmmo", "bool"), var("IsEnemy", "bool"), var("NotTarget", "bool"), var("LostPieces", "name", "array"), var("WornBefore", "name", "array"),   # LostPieces: torn off for good (Try to Destruct Clothing)   # IsEnemy: a look figure hunting Jodi (Fol Npc Guard sets it; is Npc ? / on Damage Event)
       
        var("LookSkinTex", "object:/Script/Engine.TextureRenderTarget2D")] + ms.held_vars()


def build():
    return [blueprint(FOLLOWER, P_NPCF, variables=VARS,
                      functions=[f_need_to_save(), fn("Mutate", graph=G(), override=True), fn("delay to mutant", graph=G(), override=True),
                                 f_load_path(), f_apply_mats(), f_apply_makeup_tex(), f_apply_skin_tex(), f_apply_look(), f_init_npc_appearance(), f_check_appearence(), f_apply_npc_appearance(), f_set_look(), f_count_weapon_ammo(), f_is_npc(), f_on_damage_event(), f_try_to_destruct_clothing(), f_is_ragdoll_or_dying()] + ms.functions())]


if __name__ == "__main__":
    write(os.path.join(os.path.dirname(__file__), "..", "29b_follower.json"), build())
