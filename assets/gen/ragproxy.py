"""Attackable ragdolls (spec docs/superpowers/specs/2026-10-25-ragdoll-attackable-design.md). A ragdoll is an actor, not a character:
zombies take targets only from the game's character list. An attackable human ragdoll gets an invisible, undying proxy figure
(BP_AltUIFollower without a look, its controller gone) at its pelvis; the proxy's lost health is a hit, passed to the ragdoll as a jolt."""
from bpdsl import *
from gen_ragdoll import RAGDOLL
from gen_follower import FOLLOWER
E_CHAR = "/Script/Engine.Character"; E_CMC = "/Script/Engine.CharacterMovementComponent"; E_PRIMC = "/Script/Engine.PrimitiveComponent"
E_SCENEC = "/Script/Engine.SceneComponent"; E_CONTROLLER = "/Script/Engine.Controller"; E_SKINNED = "/Script/Engine.SkinnedMeshComponent"
UNDEAD = 1.0e9   # Character_Base."undead time" far ahead: Got Hurt keeps health >= 0.1 (as FOL_UNDEAD, Fol Guard)
RAG_HIT_IMPULSE = 250.0   # cm/s: velocity change of the hit bone (AddImpulse bVelChange)
RAG_HIT_UP = 0.3          # a little upward in the push direction

VARS = [var("RagProxies", "object:" + RAGDOLL, "map", value_type="object:" + FOLLOWER), var("RagProxyHP", "object:" + RAGDOLL, "map", value_type="float"),
        var("RagProxyKeys", "object:" + RAGDOLL, "array"), var("RagProxyLoop", "object:" + RAGDOLL, "array"),
        var("RagHitBest", "float"), var("RagHitZombie", "object:" + E_ACTOR), var("RagHitCand", "object:" + E_ACTOR), var("RagHitBone", "name"), var("RagHitBoneBest", "float")]


def f_rag_is_human(humans):
    """A Jodi copy (Kind empty), an NPC or a mercenary copy - zombie ragdolls never get a proxy (zombies do not attack zombies)."""
    g = G(); g.get("k", "Kind", cls=RAGDOLL); g.link("entry.rag", "k.self"); expr = None
    for i, h in enumerate(humans):
        if h: g.call("e%d" % i, K_STR, "EqualEqual_StrStr", inp={"A": "@k.Kind", "B": h})
        else: g.call("e%d" % i, K_STR, "IsEmpty", inp={"InString": "@k.Kind"})
        e = "@e%d.ReturnValue" % i
        if expr: g.call("o%d" % i, K_MATH, "BooleanOR", inp={"A": expr, "B": e}); expr = "@o%d.ReturnValue" % i
        else: expr = e
    g.link(expr[1:], "return.yes")
    return fn("Rag Is Human", [param("rag", "object:" + RAGDOLL)], [param("yes", "bool")], graph=g, pure=True)


def pelvis(g, p, rag_pin):
    """World location of the ragdoll's pelvis (pure)."""
    g.get(p + "b", "Body", cls=RAGDOLL); g.link(rag_pin[1:], p + "b.self")
    g.call(p, E_SCENEC, "GetSocketLocation", inp={"self": "@%sb.Body" % p, "InSocketName": "pelvis"}); return "@%s.ReturnValue" % p


def f_rag_proxy_spawn():
    """The proxy: BP_AltUIFollower at the pelvis, hidden, no movement (DisableMovement: no gravity, the watch places it), Jodi and the
    zombies walk through its capsule (Pawn ignored; traces still hit it), attackable (bCanBeDamaged), undying (undead time)."""
    g = G(); loc = pelvis(g, "pl", "@entry.rag")
    g.call("tf", K_MATH, "MakeTransform", inp={"Location": loc, "Rotation": "(Pitch=0,Yaw=0,Roll=0)", "Scale": "(X=1,Y=1,Z=1)"})
    g.n("sp", "spawn", cls=FOLLOWER, inp={"SpawnTransform": "@tf.ReturnValue", "CollisionHandlingOverride": "AlwaysSpawn"})
    g.call("hid", E_ACTOR, "SetActorHiddenInGame", inp={"self": "@sp.ReturnValue", "bNewHidden": "true"})
    g.get("cm", "CharacterMovement", cls=E_CHAR); g.link("sp.ReturnValue", "cm.self"); g.call("dm", E_CMC, "DisableMovement", inp={"self": "@cm.CharacterMovement"})
    g.get("cc", "CapsuleComponent", cls=E_CHAR); g.link("sp.ReturnValue", "cc.self")
    g.call("cr", E_PRIMC, "SetCollisionResponseToChannel", inp={"self": "@cc.CapsuleComponent", "Channel": "ECC_Pawn", "NewResponse": "ECR_Ignore"})
    g.n("dmg", "set", var="bCanBeDamaged", cls=E_ACTOR, inp={"self": "@sp.ReturnValue", "bCanBeDamaged": "true"})
    g.n("ud", "set", var="undead time", cls=P_CB, inp={"self": "@sp.ReturnValue", "undead time": str(UNDEAD)})
    g.get("gm", "RagProxies"); g.call("add", K_MAP, "Map_Add", inp={"TargetMap": "@gm.RagProxies", "Key": "@entry.rag", "Value": "@sp.ReturnValue"})
    g.get("hm", "Health Max", cls=P_CB); g.link("sp.ReturnValue", "hm.self")
    g.get("gh", "RagProxyHP"); g.call("hp", K_MAP, "Map_Add", inp={"TargetMap": "@gh.RagProxyHP", "Key": "@entry.rag", "Value": "@hm.Health Max"})
    g.chain("entry", "sp", "hid", "dm", "cr", "dmg", "ud", "add", "hp")
    return fn("Rag Proxy Spawn", [param("rag", "object:" + RAGDOLL)], graph=g)


def f_rag_proxy_watch():
    """Tick. Every ragdoll: wanted (Attackable + human) and no proxy -> Rag Proxy Spawn; wanted and one -> at the pelvis, a controller the
    game gave it goes (UnPossess + destroy; On Begun Play comes 0.2 s after the spawn), health filled up; not wanted and one -> destroyed.
    Then proxies whose ragdoll is gone (removed, all removed, scene replaced) are destroyed."""
    g = G(); g.get("gr", "Ragdolls"); g.set("cp", "RagProxyLoop", inp={"RagProxyLoop": "@gr.Ragdolls"}); g.get("gl", "RagProxyLoop"); g.foreach("fe", "@gl.RagProxyLoop")
    g.get("ga", "Attackable", cls=RAGDOLL); g.link("fe.Array Element", "ga.self"); g.n("hu", "call_self", function="Rag Is Human", inp={"rag": "@fe.Array Element"})
    g.call("want", K_MATH, "BooleanAND", inp={"A": "@ga.Attackable", "B": "@hu.yes"}); g.branch("bwant", "@want.ReturnValue")
    g.get("gm", "RagProxies"); g.call("fp", K_MAP, "Map_Find", inp={"TargetMap": "@gm.RagProxies", "Key": "@fe.Array Element"}); g.call("vp", K_SYS, "IsValid", inp={"Object": "@fp.Value"})
    g.branch("bhas", "@vp.ReturnValue"); g.branch("bhas2", "@vp.ReturnValue")
    g.n("spn", "call_self", function="Rag Proxy Spawn", inp={"rag": "@fe.Array Element"})
    loc = pelvis(g, "pl", "@fe.Array Element")
    g.call("mv", E_ACTOR, "K2_SetActorLocation", inp={"self": "@fp.Value", "NewLocation": loc, "bSweep": "false", "bTeleport": "true"})
    g.call("gc", E_PAWN, "GetController", inp={"self": "@fp.Value"}); g.call("vc", K_SYS, "IsValid", inp={"Object": "@gc.ReturnValue"}); g.branch("bc", "@vc.ReturnValue")
    g.call("un", E_CONTROLLER, "UnPossess", inp={"self": "@gc.ReturnValue"}); g.call("dc", E_ACTOR, "K2_DestroyActor", inp={"self": "@gc.ReturnValue"})
    g.get("hm", "Health Max", cls=P_CB); g.link("fp.Value", "hm.self"); g.n("fill", "set", var="Health", cls=P_CB, inp={"self": "@fp.Value", "Health": "@hm.Health Max"})
    # hit: the proxy lost health since the last tick (before it is filled up again)
    g.get("php", "Health", cls=P_CB); g.link("fp.Value", "php.self"); g.get("gh0", "RagProxyHP"); g.call("fh", K_MAP, "Map_Find", inp={"TargetMap": "@gh0.RagProxyHP", "Key": "@fe.Array Element"})
    g.call("hurt", K_MATH, "Less_FloatFloat", inp={"A": "@php.Health", "B": "@fh.Value"}); g.branch("bhu", "@hurt.ReturnValue")
    g.n("rh", "call_self", function="Rag Hit", inp={"rag": "@fe.Array Element"})
    g.get("gh1", "RagProxyHP"); g.call("sh", K_MAP, "Map_Add", inp={"TargetMap": "@gh1.RagProxyHP", "Key": "@fe.Array Element", "Value": "@hm.Health Max"})
    # a frozen figure's jolt is over: its pose again (also when it was made unattackable meanwhile)
    g.get("gha", "HitActive", cls=RAGDOLL); g.link("fe.Array Element", "gha.self"); g.get("ghu", "HitUntil", cls=RAGDOLL); g.link("fe.Array Element", "ghu.self")
    g.call("now", K_SYS, "GetGameTimeInSeconds"); g.call("late", K_MATH, "Greater_FloatFloat", inp={"A": "@now.ReturnValue", "B": "@ghu.HitUntil"})
    g.call("back", K_MATH, "BooleanAND", inp={"A": "@gha.HitActive", "B": "@late.ReturnValue"}); g.branch("bbk", "@back.ReturnValue")
    g.call("hb", RAGDOLL, "Hit Back", inp={"self": "@fe.Array Element"})
    g.call("kill", E_ACTOR, "K2_DestroyActor", inp={"self": "@fp.Value"}); g.get("gm2", "RagProxies"); g.call("rmp", K_MAP, "Map_Remove", inp={"TargetMap": "@gm2.RagProxies", "Key": "@fe.Array Element"})
    # proxies of ragdolls that are gone
    g.get("gm3", "RagProxies"); g.call("keys", K_MAP, "Map_Keys", inp={"TargetMap": "@gm3.RagProxies"}); g.set("sk", "RagProxyKeys", inp={"RagProxyKeys": "@keys.Keys"})
    g.get("gk", "RagProxyKeys"); g.foreach("fk", "@gk.RagProxyKeys"); g.call("vk", K_SYS, "IsValid", inp={"Object": "@fk.Array Element"}); g.branch("bk", "@vk.ReturnValue")
    g.get("gm4", "RagProxies"); g.call("fo", K_MAP, "Map_Find", inp={"TargetMap": "@gm4.RagProxies", "Key": "@fk.Array Element"}); g.call("ko", E_ACTOR, "K2_DestroyActor", inp={"self": "@fo.Value"})
    g.get("gm5", "RagProxies"); g.call("rmo", K_MAP, "Map_Remove", inp={"TargetMap": "@gm5.RagProxies", "Key": "@fk.Array Element"})
    g.get("gh", "RagProxyHP"); g.call("rmh", K_MAP, "Map_Remove", inp={"TargetMap": "@gh.RagProxyHP", "Key": "@fk.Array Element"})
    g.chain("entry", "cp", "fe"); g.chain("fe", "bbk", "hb", "bwant", "bhas", "mv", "bc", "un", "dc", "bhu"); g.chain("bbk:else", "bwant"); g.chain("bc:else", "bhu")
    g.chain("bhu", "rh", "fill"); g.chain("bhu:else", "fill"); g.chain("fill", "sh"); g.chain("bhas:else", "spn")
    g.chain("bwant:else", "bhas2", "kill", "rmp"); g.chain("fe:Completed", "keys", "sk", "fk"); g.chain("fk", "bk"); g.chain("bk:else", "ko", "rmo", "rmh")
    return fn("Rag Proxy Watch", graph=g)


def f_rag_hit(joints):
    """A hit on the ragdoll's proxy: the zombie nearest to the ragdoll (alive) is the attacker; the joint bone nearest to it gets a
    push away from it (Hit Jolt). No zombie found: nothing."""
    g = G(); loc = pelvis(g, "pl", "@entry.rag")
    g.set("s0", "RagHitBest", inp={"RagHitBest": "1.0e9"}); g.set("s1", "RagHitZombie", inp={"RagHitZombie": "None"})
    g.call("za", K_GS, "GetAllActorsOfClass", inp={"ActorClass": P_ZOMBIE}); g.foreach("fz", "@za.OutActors")
    g.call("zl", E_ACTOR, "K2_GetActorLocation", inp={"self": "@fz.Array Element"}); g.call("zd", K_MATH, "Vector_Distance", inp={"V1": "@zl.ReturnValue", "V2": loc})
    # the kit's Zombie_Base stub does not derive from Character_Base (the game's does): cast from an actor variable
    g.set("sc", "RagHitCand", inp={"RagHitCand": "@fz.Array Element"}); g.get("gc", "RagHitCand")
    g.cast("zc", P_CB, "@gc.RagHitCand"); g.get("zh", "Health", cls=P_CB); g.link("zc.AsCharacter Base", "zh.self")
    g.call("alive", K_MATH, "Greater_FloatFloat", inp={"A": "@zh.Health", "B": "0.0"}); g.get("gbst", "RagHitBest")
    g.call("near", K_MATH, "Less_FloatFloat", inp={"A": "@zd.ReturnValue", "B": "@gbst.RagHitBest"}); g.call("pick", K_MATH, "BooleanAND", inp={"A": "@alive.ReturnValue", "B": "@near.ReturnValue"})
    g.branch("bz", "@pick.ReturnValue"); g.set("sbz", "RagHitBest", inp={"RagHitBest": "@zd.ReturnValue"}); g.set("szz", "RagHitZombie", inp={"RagHitZombie": "@fz.Array Element"})
    g.get("gz", "RagHitZombie"); g.call("vz", K_SYS, "IsValid", inp={"Object": "@gz.RagHitZombie"}); g.branch("bvz", "@vz.ReturnValue")
    g.call("zl2", E_ACTOR, "K2_GetActorLocation", inp={"self": "@gz.RagHitZombie"})
    g.set("b0", "RagHitBoneBest", inp={"RagHitBoneBest": "1.0e9"}); g.set("b1", "RagHitBone", inp={"RagHitBone": "pelvis"})
    g.get("gbd", "Body", cls=RAGDOLL); g.link("entry.rag", "gbd.self"); prev = "b1"
    # the joint nearest to the zombie: every bb<i> leads on "yes" through the setters to the next check, on "no" straight there
    for i, bone in enumerate(joints):
        g.call("bi%d" % i, E_SKINNED, "GetBoneIndex", inp={"self": "@gbd.Body", "BoneName": bone}); g.call("hb%d" % i, K_MATH, "NotEqual_IntInt", inp={"A": "@bi%d.ReturnValue" % i, "B": "-1"})
        g.call("bl%d" % i, E_SCENEC, "GetSocketLocation", inp={"self": "@gbd.Body", "InSocketName": bone}); g.call("bd%d" % i, K_MATH, "Vector_Distance", inp={"V1": "@bl%d.ReturnValue" % i, "V2": "@zl2.ReturnValue"})
        g.get("gbb%d" % i, "RagHitBoneBest"); g.call("bn%d" % i, K_MATH, "Less_FloatFloat", inp={"A": "@bd%d.ReturnValue" % i, "B": "@gbb%d.RagHitBoneBest" % i})
        g.call("bp%d" % i, K_MATH, "BooleanAND", inp={"A": "@hb%d.ReturnValue" % i, "B": "@bn%d.ReturnValue" % i}); g.branch("bb%d" % i, "@bp%d.ReturnValue" % i)
        g.set("sbb%d" % i, "RagHitBoneBest", inp={"RagHitBoneBest": "@bd%d.ReturnValue" % i}); g.set("sbn%d" % i, "RagHitBone", inp={"RagHitBone": g.lit_name("ln%d" % i, bone)})
        g.chain(prev, "bb%d" % i); g.chain("bb%d" % i, "sbb%d" % i, "sbn%d" % i); g.chain("sbn%d" % i, "bb%d" % (i + 1) if i + 1 < len(joints) else "hj"); prev = "bb%d:else" % i
    g.get("gbn", "RagHitBone"); g.call("bwl", E_SCENEC, "GetSocketLocation", inp={"self": "@gbd.Body", "InSocketName": "@gbn.RagHitBone"})
    g.call("dir", K_MATH, "Subtract_VectorVector", inp={"A": "@bwl.ReturnValue", "B": "@zl2.ReturnValue"}); g.call("dn", K_MATH, "Normal", inp={"A": "@dir.ReturnValue", "Tolerance": "0.0001"})
    g.call("up", K_MATH, "Add_VectorVector", inp={"A": "@dn.ReturnValue", "B": "(X=0,Y=0,Z=%s)" % RAG_HIT_UP}); g.call("un", K_MATH, "Normal", inp={"A": "@up.ReturnValue", "Tolerance": "0.0001"})
    g.call("iv", K_MATH, "Multiply_VectorFloat", inp={"A": "@un.ReturnValue", "B": str(RAG_HIT_IMPULSE)})
    g.call("hj", RAGDOLL, "Hit Jolt", inp={"self": "@entry.rag", "bone": "@gbn.RagHitBone", "impulse": "@iv.ReturnValue"})
    g.chain("entry", "s0", "s1", "za", "fz"); g.chain("fz", "sc", "bz", "sbz", "szz"); g.chain("fz:Completed", "bvz", "b0", "b1"); g.chain(prev, "hj")
    return fn("Rag Hit", [param("rag", "object:" + RAGDOLL)], graph=g)


def functions(humans, joints):
    return [f_rag_is_human(humans), f_rag_proxy_spawn(), f_rag_proxy_watch(), f_rag_hit(joints)]
