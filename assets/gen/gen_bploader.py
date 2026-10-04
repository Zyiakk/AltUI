"""Generates assets/60_bploader.json: AltUI's entry point for the Blueprint Loader (Nexus 994).

The loader starts the actor class named in a table called TKA_BlueprintLoader inside a mod's own folder. BP_AltUIManager
takes its controller from GetOwner and needs Jodi (or a main menu / loading scene), so the row cannot point at it directly: BP_AltUILoaderEntry does the
waiting and spawns the manager with the controller as owner - the same job the hook pak's camera class does, in an actor
the loader can spawn.

The table stays in AltUI.pak; no separate pak. Its row structure BlueprintToLoad_Struct belongs to the loader, lives in
the kit under /Game/Mod/TKA_BlueprintLoader/ and never ships with AltUI (pak.sh packs Mod/AltUI only).
"""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *

ENTRY = M + "/BP_AltUILoaderEntry"
MGR = M + "/BP_AltUIManager"
BPL_STRUCT = "/Game/Mod/TKA_BlueprintLoader/BlueprintToLoad_Struct"


def event_graph():
    g = G()
    g.event("bp", E_ACTOR, "ReceiveBeginPlay"); g.self_("me")
    g.call("tm", K_SYS, "K2_SetTimer", inp={"Object": "@me.self", "FunctionName": "TryInit", "Time": "0.5", "bLooping": "true"})
    g.custom("ev", "TryInit"); g.get("gsp", "Spawned"); g.branch("br", "@gsp.Spawned")
    g.call("pc", K_GS, "GetPlayerController", inp={"PlayerIndex": "0"})   # spawned without an owner, so not GetOwner as in the hook
    g.call("pawn", E_CTRL, "K2_GetPawn", inp={"self": "@pc.ReturnValue"})
    g.cast("cj", P_JODI, "@pawn.ReturnValue", pure=False)   # no Jodi yet (loading): the timer retries
    look_scene_branch(g)   # main menu / loading scene: no Jodi pawn ever, spawn anyway
    g.call("ld", K_SYS, "LoadClassAsset_Blocking", inp={"AssetClass": MGR + ".BP_AltUIManager_C"})
    g.n("cc", "class_cast", pure=True, cls=E_ACTOR, inp={"Class": "@ld.ReturnValue"})
    g.call("iv", K_SYS, "IsValidClass", inp={"Class": "@cc.AsActor"}); g.branch("br2", "@iv.ReturnValue")
    # the hook pak spawns the manager too (and a second loader table could point here): whoever is first wins, the other stops
    g.call("all", K_GS, "GetAllActorsOfClass", inp={"ActorClass": "@cc.AsActor"})
    g.call("cnt", K_ARR, "Array_Length", inp={"TargetArray": "@all.OutActors"})
    g.call("gt", K_MATH, "Greater_IntInt", inp={"A": "@cnt.ReturnValue", "B": "0"}); g.branch("br3", "@gt.ReturnValue")
    g.call("tr", K_MATH, "MakeTransform", inp={"Scale": "1,1,1"})
    g.n("sp", "spawn", inp={"SpawnTransform": "@tr.ReturnValue", "Class": "@cc.AsActor", "Owner": "@pc.ReturnValue"})
    g.set("ssp", "Spawned", inp={"Spawned": "true"}); g.self_("me2"); g.call("ct", K_SYS, "K2_ClearTimer", inp={"Object": "@me2.self", "FunctionName": "TryInit"})
    # mod pak missing: the class never appears -> stop the timer instead of a blocking load every 0.5 s forever
    g.self_("me3"); g.call("ct2", K_SYS, "K2_ClearTimer", inp={"Object": "@me3.self", "FunctionName": "TryInit"})
    g.self_("me4"); g.call("ct3", K_SYS, "K2_ClearTimer", inp={"Object": "@me4.self", "FunctionName": "TryInit"})   # someone else already spawned it
    g.chain("bp", "tm"); g.chain("ev", "br")
    g.chain("br:else", "cj", "ld", "br2", "all", "br3", "ct3")
    g.chain("cj:CastFailed", "lvl"); g.chain("bm", "ld")
    g.chain("br3:else", "sp", "ssp", "ct"); g.chain("br2:else", "ct2")
    return g


assets = [blueprint(ENTRY, E_ACTOR, variables=[var("Spawned", "bool")], event_graph=event_graph()),
          datatable(M + "/TKA_BlueprintLoader", BPL_STRUCT, rows={"AltUI": {"Actor Class": ENTRY + ".BP_AltUILoaderEntry_C"}})]
write(os.path.join(os.path.dirname(__file__), "..", "60_bploader.json"), assets)
