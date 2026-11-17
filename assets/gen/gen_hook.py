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
MODLOADER = M + "/BP_AltUIModLoader"   # gen_bploader.py
RETRIES = 20   # class loads asked again (TryInit beat, 0.5 s)
PERFLOG = os.environ.get("ALTUI_PERFLOG") == "1"


def event_graph():
    g = G()
    g.event("bp", E_ACTOR, "ReceiveBeginPlay")
    # Blueprint Loader mods: AltUI's own loader actor instead of hosting his (2026-11-16: his run, a blocking load attempt per
    # installed mod and the found mods loaded blocking, was 2.1 s of every main menu and level start). Only when his pak is there:
    # its row struct is what the mods' tables are built on.
    g.call("pcd", K_PATHS, "ProjectContentDir"); g.call("hsp", K_STR, "Concat_StrStr", inp={"A": "@pcd.ReturnValue", "B": "Mod/TKA_BlueprintLoader/BlueprintToLoad_Struct.uasset"})
    g.call("hsx", K_PATHS, "FileExists", inp={"InPath": "@hsp.ReturnValue"}); g.branch("bhs", "@hsx.ReturnValue")
    g.self_("me5"); g.call("tml", K_SYS, "K2_SetTimer", inp={"Object": "@me5.self", "FunctionName": "Load Mod Loader", "Time": "0.01", "bLooping": "false"})
    # Load Mod Loader: its class in the background, spawned once there (identity, no owner, as his loader was); missing (AltUI.pak not
    # mounted yet in a first main menu): TryInit asks again
    g.custom("lml", "Load Mod Loader")
    g.n("mlc", "load_class_async", inp={"AssetClass": MODLOADER + ".BP_AltUIModLoader_C"})
    g.n("mlcc", "class_cast", pure=True, cls=E_ACTOR, inp={"Class": "@mlc.Class"})
    g.call("mliv", K_SYS, "IsValidClass", inp={"Class": "@mlcc.AsActor"}); g.branch("mlb", "@mliv.ReturnValue")
    g.call("mlt", K_MATH, "MakeTransform", inp={"Scale": "1,1,1"})
    g.n("mls", "spawn", inp={"SpawnTransform": "@mlt.ReturnValue", "Class": "@mlcc.AsActor"})
    g.set("mlr1", "MlRetry", inp={"MlRetry": "true"})
    g.chain("lml", "mlc"); g.chain("mlc:Completed", "mlb", "mls"); g.chain("mlb:else", "mlr1")
    g.self_("me")
    g.call("tm", K_SYS, "K2_SetTimer", inp={"Object": "@me.self", "FunctionName": "TryInit", "Time": "0.5", "bLooping": "true"})
    g.chain("bp", "bhs", "tml", "acl"); g.chain("bhs:else", "acl")
    g.custom("ev", "TryInit"); g.get("gsp", "Spawned"); g.branch("br", "@gsp.Spawned")
    # the mod loader's class did not come: ask again (at most RETRIES times, with TryInit's beat)
    g.get("gmr", "MlRetry"); g.get("gmt", "MlTries"); g.call("mlt2", K_MATH, "Less_IntInt", inp={"A": "@gmt.MlTries", "B": str(RETRIES)})
    g.call("mla", K_MATH, "BooleanAND", inp={"A": "@gmr.MlRetry", "B": "@mlt2.ReturnValue"}); g.branch("bmr", "@mla.ReturnValue")
    g.set("mlr0", "MlRetry", inp={"MlRetry": "false"}); g.get("gmt2", "MlTries"); g.call("mli", K_MATH, "Add_IntInt", inp={"A": "@gmt2.MlTries", "B": "1"}); g.set("mlts", "MlTries", inp={"MlTries": "@mli.ReturnValue"})
    g.self_("me6"); g.call("tml2", K_SYS, "K2_SetTimer", inp={"Object": "@me6.self", "FunctionName": "Load Mod Loader", "Time": "0.01", "bLooping": "false"})
    g.chain("ev", "bmr", "mlr0", "mlts", "tml2", "br"); g.chain("bmr:else", "br")
    g.call("pc", E_PCM, "GetOwningPlayerController"); g.call("pawn", E_CTRL, "K2_GetPawn", inp={"self": "@pc.ReturnValue"})
    g.cast("cj", P_JODI, "@pawn.ReturnValue", pure=False)   # no Jodi yet (loading): the timer retries
    look_scene_branch(g)   # main menu / loading scene: no Jodi pawn ever, spawn anyway
    manager_class_async(g, "tm", MGR)   # the class loads in the background; TryInit waits for it ("bld")
    # a loader table (AltUI's own, via BP_AltUILoaderEntry) may have spawned the manager already: whoever is first wins
    g.call("all", K_GS, "GetAllActorsOfClass", inp={"ActorClass": "@cc.AsActor"})
    g.call("cnt", K_ARR, "Array_Length", inp={"TargetArray": "@all.OutActors"})
    g.call("gt", K_MATH, "Greater_IntInt", inp={"A": "@cnt.ReturnValue", "B": "0"}); g.branch("br3", "@gt.ReturnValue")
    g.call("tr", K_MATH, "MakeTransform", inp={"Scale": "1,1,1"})
    g.n("sp", "spawn", inp={"SpawnTransform": "@tr.ReturnValue", "Class": "@cc.AsActor", "Owner": "@pc.ReturnValue"})
    g.set("ssp", "Spawned", inp={"Spawned": "true"}); g.self_("me2"); g.call("ct", K_SYS, "K2_ClearTimer", inp={"Object": "@me2.self", "FunctionName": "TryInit"})
    # the class did not come: AltUI.pak not mounted yet (a first main menu) - load it again, at most RETRIES times; then (only the
    # hook pak installed) stop the timer
    g.get("gmt3", "MgrTries"); g.call("mgl", K_MATH, "Less_IntInt", inp={"A": "@gmt3.MgrTries", "B": str(RETRIES)}); g.branch("bmg", "@mgl.ReturnValue")
    g.get("gmt4", "MgrTries"); g.call("mgi", K_MATH, "Add_IntInt", inp={"A": "@gmt4.MgrTries", "B": "1"}); g.set("mgts", "MgrTries", inp={"MgrTries": "@mgi.ReturnValue"})
    g.set("mgl0", "MgrLoaded", inp={"MgrLoaded": "false"})
    g.self_("me3"); g.call("ct2", K_SYS, "K2_ClearTimer", inp={"Object": "@me3.self", "FunctionName": "TryInit"})
    g.self_("me4"); g.call("ct3", K_SYS, "K2_ClearTimer", inp={"Object": "@me4.self", "FunctionName": "TryInit"})
    g.chain("br2:else", "bmg", "mgts", "mgl0", "acl"); g.chain("bmg:else", "ct2")
    if PERFLOG:   # 2026-11-15: when TryInit spawns and when the spawn (incl. the manager's BeginPlay) returns - the manager logs both
        g.set("hk0", "HkT0", inp={"HkT0": real_stamp(g, "hka")}); g.set("hk1", "HkT1", inp={"HkT1": real_stamp(g, "hkb")})
        g.chain("br:else", "cj", "hk0", "bld"); g.chain("br2", "all", "br3", "ct3")
        g.chain("cj:CastFailed", "lvl"); g.chain("bm", "hk0")
        g.chain("br3:else", "sp", "hk1", "ssp", "ct")
    else:
        g.chain("br:else", "cj", "bld"); g.chain("br2", "all", "br3", "ct3")
        g.chain("cj:CastFailed", "lvl"); g.chain("bm", "bld")
        g.chain("br3:else", "sp", "ssp", "ct")
    return g

assets = [blueprint(HOOK, E_PCM, variables=[var("Spawned", "bool")] + MGR_VARS + [var("MgrTries", "int"), var("MlRetry", "bool"), var("MlTries", "int")] + ([var("HkT0", "float"), var("HkT1", "float")] if PERFLOG else []), defaults={"ViewPitchMin": "-80.0", "ViewPitchMax": "70.0"},
                    event_graph=event_graph())]
write(os.path.join(os.path.dirname(__file__), "..", "20_hook.json"), assets)
