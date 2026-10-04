"""Generates assets/20_hook.json: replacement PlayerCameraManager (override pak in ~mods).

Two jobs, both "spawn one actor and get out of the way":
 * the inventory manager, with the controller as owner, once Jodi exists (or at once in a main menu / loading scene);
 * Katsumi's Blueprint Loader actor (Nexus 994) if his pak is installed. His pak replaces this same class, so without
   this hook, AltUI would shut his loader mods out. By path, no hard reference - his discovery logic stays in his pak.

The camera framing used to live here as a BlueprintUpdateCamera override. It moved to CM_AltUICam (gen_cammod.py),
a UCameraModifier that attaches to whatever camera manager a level has, so it also works when this pak is not installed."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *

HOOK = "/Game/Project/Classes/TKA_PlayerCameraManager"
MGR = M + "/BP_AltUIManager"
BPL = "/Game/Mod/TKA_BlueprintLoader/BlueprintLoader"
E_PCM = "/Script/Engine.PlayerCameraManager"


def event_graph():
    g = G()
    g.event("bp", E_ACTOR, "ReceiveBeginPlay")
    # host his loader: same place (BeginPlay) and same parameters (Identity, no owner) as his own camera class uses
    g.call("ldl", K_SYS, "LoadClassAsset_Blocking", inp={"AssetClass": BPL + ".BlueprintLoader_C"})
    g.n("ccl", "class_cast", pure=True, cls=E_ACTOR, inp={"Class": "@ldl.ReturnValue"})
    g.call("ivl", K_SYS, "IsValidClass", inp={"Class": "@ccl.AsActor"}); g.branch("brl", "@ivl.ReturnValue")   # his pak not installed -> nothing to host
    g.call("trl", K_MATH, "MakeTransform", inp={"Scale": "1,1,1"})
    g.n("spl", "spawn", inp={"SpawnTransform": "@trl.ReturnValue", "Class": "@ccl.AsActor"})
    g.self_("me")
    g.call("tm", K_SYS, "K2_SetTimer", inp={"Object": "@me.self", "FunctionName": "TryInit", "Time": "0.5", "bLooping": "true"})
    g.custom("ev", "TryInit"); g.get("gsp", "Spawned"); g.branch("br", "@gsp.Spawned")
    g.call("pc", E_PCM, "GetOwningPlayerController"); g.call("pawn", E_CTRL, "K2_GetPawn", inp={"self": "@pc.ReturnValue"})
    g.cast("cj", P_JODI, "@pawn.ReturnValue", pure=False)   # no Jodi yet (loading): the timer retries
    look_scene_branch(g)   # main menu / loading scene: no Jodi pawn ever, spawn anyway
    g.call("ld", K_SYS, "LoadClassAsset_Blocking", inp={"AssetClass": MGR + ".BP_AltUIManager_C"})
    g.n("cc", "class_cast", pure=True, cls=E_ACTOR, inp={"Class": "@ld.ReturnValue"})
    g.call("iv", K_SYS, "IsValidClass", inp={"Class": "@cc.AsActor"}); g.branch("br2", "@iv.ReturnValue")
    # a loader table (AltUI's own, via BP_AltUILoaderEntry) may have spawned the manager already: whoever is first wins
    g.call("all", K_GS, "GetAllActorsOfClass", inp={"ActorClass": "@cc.AsActor"})
    g.call("cnt", K_ARR, "Array_Length", inp={"TargetArray": "@all.OutActors"})
    g.call("gt", K_MATH, "Greater_IntInt", inp={"A": "@cnt.ReturnValue", "B": "0"}); g.branch("br3", "@gt.ReturnValue")
    g.call("tr", K_MATH, "MakeTransform", inp={"Scale": "1,1,1"})
    g.n("sp", "spawn", inp={"SpawnTransform": "@tr.ReturnValue", "Class": "@cc.AsActor", "Owner": "@pc.ReturnValue"})
    g.set("ssp", "Spawned", inp={"Spawned": "true"}); g.self_("me2"); g.call("ct", K_SYS, "K2_ClearTimer", inp={"Object": "@me2.self", "FunctionName": "TryInit"})
    # mod pak missing (only the hook pak installed): the class never appears -> stop the timer instead of a blocking load every 0.5 s forever
    g.self_("me3"); g.call("ct2", K_SYS, "K2_ClearTimer", inp={"Object": "@me3.self", "FunctionName": "TryInit"})
    g.self_("me4"); g.call("ct3", K_SYS, "K2_ClearTimer", inp={"Object": "@me4.self", "FunctionName": "TryInit"})
    g.chain("bp", "ldl", "brl", "spl", "tm"); g.chain("brl:else", "tm")
    g.chain("ev", "br"); g.chain("br:else", "cj", "ld", "br2", "all", "br3", "ct3")
    g.chain("cj:CastFailed", "lvl"); g.chain("bm", "ld")
    g.chain("br3:else", "sp", "ssp", "ct"); g.chain("br2:else", "ct2")
    return g


assets = [blueprint(HOOK, E_PCM, variables=[var("Spawned", "bool")], defaults={"ViewPitchMin": "-80.0", "ViewPitchMax": "70.0"},
                    event_graph=event_graph())]
write(os.path.join(os.path.dirname(__file__), "..", "20_hook.json"), assets)
