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
    manager_class_async(g, "tm", MGR)   # the class loads in the background; TryInit waits for it ("bld")
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
    g.chain("bp", "acl"); g.chain("ev", "br")
    g.chain("br:else", "cj", "bld"); g.chain("br2", "all", "br3", "ct3")
    g.chain("cj:CastFailed", "lvl"); g.chain("bm", "bld")
    g.chain("br3:else", "sp", "ssp", "ct"); g.chain("br2:else", "ct2")
    return g


MODLOADER = M + "/BP_AltUIModLoader"
MODLOADER_BATCH, MODLOADER_STEP = 40, 0.02   # file checks per step (~0.25 ms each), seconds between steps


def modloader_graph():
    """BP_AltUIModLoader - what Katsumi's loader actor does (Nexus 994: spawn the classes listed in /Game/Mod/<mod>/TKA_BlueprintLoader),
    without standing the game still. His run hosted by AltUI's hook made 2.1 s of every main menu and level start (2026-11-16):
    a blocking load attempt per installed mod, then the found mods' classes with all their assets, blocking. Here a file check
    per mod, MODLOADER_BATCH per step, then each found table loaded in the background (its classes come with it) and its rows
    spawned as his version does (identity, no owner), one mod after the other. State: 0 waiting for the game's mod list, 1 file
    checks, 2 loading, 3 done."""
    g = G()
    g.event("bp", E_ACTOR, "ReceiveBeginPlay"); g.self_("me")
    g.call("tm", K_SYS, "K2_SetTimer", inp={"Object": "@me.self", "FunctionName": "Step", "Time": str(MODLOADER_STEP), "bLooping": "true"})
    g.chain("bp", "tm")
    g.custom("st", "Step")
    g.get("gs0", "State"); g.call("e0", K_MATH, "EqualEqual_IntInt", inp={"A": "@gs0.State", "B": "0"}); g.branch("b0", "@e0.ReturnValue")
    g.get("gs1", "State"); g.call("e1", K_MATH, "EqualEqual_IntInt", inp={"A": "@gs1.State", "B": "1"}); g.branch("b1", "@e1.ReturnValue")
    g.get("gs2", "State"); g.call("e2", K_MATH, "EqualEqual_IntInt", inp={"A": "@gs2.State", "B": "2"}); g.branch("b2", "@e2.ReturnValue")
    g.chain("st", "b0"); g.chain("b0:else", "b1"); g.chain("b1:else", "b2")
    # 0: the game's loader has merged the mod tables (empty in an early main menu frame)
    g.call("rn", K_DT, "GetDataTableRowNames", inp={"Table": P_DLC_T}); g.call("rl", K_ARR, "Array_Length", inp={"TargetArray": "@rn.OutRowNames"})
    g.call("rg", K_MATH, "Greater_IntInt", inp={"A": "@rl.ReturnValue", "B": "0"}); g.branch("brl", "@rg.ReturnValue")
    g.set("sr", "Rows", inp={"Rows": "@rn.OutRowNames"}); g.set("s1", "State", inp={"State": "1"})
    g.chain("b0", "rn", "brl", "sr", "s1")
    # 1: the next MODLOADER_BATCH mods: Content/Mod/<mod>/TKA_BlueprintLoader.uasset (a lookup in the pak index)
    g.get("gi", "Idx"); g.get("gr", "Rows"); g.call("len", K_ARR, "Array_Length", inp={"TargetArray": "@gr.Rows"})
    g.call("ib", K_MATH, "Add_IntInt", inp={"A": "@gi.Idx", "B": str(MODLOADER_BATCH)}); g.call("mn", K_MATH, "Min", inp={"A": "@ib.ReturnValue", "B": "@len.ReturnValue"})
    g.call("last", K_MATH, "Subtract_IntInt", inp={"A": "@mn.ReturnValue", "B": "1"})
    g.n("fl", "macro", name="ForLoop", inp={"First Index": "@gi.Idx", "Last Index": "@last.ReturnValue"})
    g.get("gr2", "Rows"); g.call("ag", K_ARR, "Array_Get", inp={"TargetArray": "@gr2.Rows", "Index": "@fl.Index"})
    g.call("n2s", K_STR, "Conv_NameToString", inp={"InName": "@ag.Item"})
    g.call("pcd", K_PATHS, "ProjectContentDir"); g.call("f1", K_STR, "Concat_StrStr", inp={"A": "@pcd.ReturnValue", "B": "Mod/"})
    g.call("f2", K_STR, "Concat_StrStr", inp={"A": "@f1.ReturnValue", "B": "@n2s.ReturnValue"}); g.call("f3", K_STR, "Concat_StrStr", inp={"A": "@f2.ReturnValue", "B": "/TKA_BlueprintLoader.uasset"})
    g.call("fx", K_PATHS, "FileExists", inp={"InPath": "@f3.ReturnValue"}); g.call("na", K_MATH, "NotEqual_NameName", inp={"A": "@ag.Item", "B": "AltUI"})
    g.call("fxa", K_MATH, "BooleanAND", inp={"A": "@fx.ReturnValue", "B": "@na.ReturnValue"}); g.branch("bfx", "@fxa.ReturnValue")   # AltUI's own row: the hook spawns AltUI itself
    g.get("gh", "Hits"); g.call("ah", K_ARR, "Array_Add", inp={"TargetArray": "@gh.Hits", "NewItem": "@ag.Item"})
    g.get("gi2", "Idx"); g.call("ni", K_MATH, "Add_IntInt", inp={"A": "@gi2.Idx", "B": str(MODLOADER_BATCH)}); g.set("si", "Idx", inp={"Idx": "@ni.ReturnValue"})
    g.get("gi3", "Idx"); g.get("gr3", "Rows"); g.call("len3", K_ARR, "Array_Length", inp={"TargetArray": "@gr3.Rows"})
    g.call("dn", K_MATH, "GreaterEqual_IntInt", inp={"A": "@gi3.Idx", "B": "@len3.ReturnValue"}); g.branch("bdn", "@dn.ReturnValue"); g.set("s2", "State", inp={"State": "2"})
    g.chain("b1", "fl"); g.chain("fl", "bfx", "ah"); g.chain("fl:Completed", "si", "bdn", "s2")
    # 2: one found mod at a time - its table in the background, then its rows spawned
    g.get("gbz", "Busy"); g.branch("bbz", "@gbz.Busy")
    g.get("ghi", "HitIdx"); g.get("gh2", "Hits"); g.call("hl", K_ARR, "Array_Length", inp={"TargetArray": "@gh2.Hits"})
    g.call("hd", K_MATH, "GreaterEqual_IntInt", inp={"A": "@ghi.HitIdx", "B": "@hl.ReturnValue"}); g.branch("bhd", "@hd.ReturnValue")
    g.self_("me2"); g.call("ct", K_SYS, "K2_ClearTimer", inp={"Object": "@me2.self", "FunctionName": "Step"}); g.set("s3", "State", inp={"State": "3"})
    g.set("sb", "Busy", inp={"Busy": "true"})
    g.get("gh3", "Hits"); g.get("ghi2", "HitIdx"); g.call("hg", K_ARR, "Array_Get", inp={"TargetArray": "@gh3.Hits", "Index": "@ghi2.HitIdx"})
    g.call("hs", K_STR, "Conv_NameToString", inp={"InName": "@hg.Item"}); g.call("p1", K_STR, "Concat_StrStr", inp={"A": "/Game/Mod/", "B": "@hs.ReturnValue"})
    g.call("p2", K_STR, "Concat_StrStr", inp={"A": "@p1.ReturnValue", "B": "/TKA_BlueprintLoader.TKA_BlueprintLoader"})
    g.call("sp", K_SYS, "MakeSoftObjectPath", inp={"PathString": "@p2.ReturnValue"}); g.call("sr2", K_SYS, "Conv_SoftObjPathToSoftObjRef", inp={"SoftObjectPath": "@sp.ReturnValue"})
    g.n("la", "load_asset_async", inp={"Asset": "@sr2.ReturnValue"})
    g.cast("ck", E_DATATABLE, "@la.Object", pure=False)
    g.call("rn2", K_DT, "GetDataTableRowNames", inp={"Table": "@ck.AsData Table"}); g.foreach("fr", "@rn2.OutRowNames")
    g.n("row", "get_row", inp={"DataTable": "@ck.AsData Table", "RowName": "@fr.Array Element"}, miss="ignore"); g.brk("brk", BPL_STRUCT, "@row.OutRow")
    g.call("iv", K_SYS, "IsValidClass", inp={"Class": "@brk.Actor Class"}); g.branch("bv", "@iv.ReturnValue")
    g.call("tr", K_MATH, "MakeTransform", inp={"Scale": "1,1,1"})
    g.n("spw", "spawn", inp={"SpawnTransform": "@tr.ReturnValue", "Class": "@brk.Actor Class"})   # no owner, like his loader
    g.get("ghi3", "HitIdx"); g.call("hi", K_MATH, "Add_IntInt", inp={"A": "@ghi3.HitIdx", "B": "1"}); g.set("shi", "HitIdx", inp={"HitIdx": "@hi.ReturnValue"}); g.set("sb0", "Busy", inp={"Busy": "false"})
    g.chain("b2", "bbz"); g.chain("bbz:else", "bhd", "ct", "s3"); g.chain("bhd:else", "sb", "la")
    g.chain("la:Completed", "ck", "rn2", "fr"); g.chain("fr", "row", "bv", *(["pt0"] if os.environ.get("ALTUI_PERFLOG") == "1" else []), "spw"); g.chain("fr:Completed", "shi", "sb0"); g.chain("ck:CastFailed", "shi")
    if os.environ.get("ALTUI_PERFLOG") == "1":   # 2026-11-16: in which frame each mod's actor comes (the long frames ~2.5 s after a level start)
        g.call("pga", K_GS, "GetActorOfClass", inp={"ActorClass": MGR + ".BP_AltUIManager_C"}); g.cast("pgc", MGR + ".BP_AltUIManager_C", "@pga.ReturnValue", pure=False)
        g.set("pt0", "SpT", inp={"SpT": real_stamp(g, "pst")})   # the spawn's length (the actor's BeginPlay runs inside it)
        g.call("pcn", K_SYS, "GetClassDisplayName", inp={"Class": "@brk.Actor Class"}); g.call("pcs", K_STR, "Concat_StrStr", inp={"A": "bploader spawned ", "B": "@pcn.ReturnValue"})
        g.get("ptg", "SpT"); g.call("pd", K_MATH, "Subtract_FloatFloat", inp={"A": real_stamp(g, "pet"), "B": "@ptg.SpT"}); g.call("pm", K_MATH, "Multiply_FloatFloat", inp={"A": "@pd.ReturnValue", "B": "1000.0"})
        g.call("pms", K_STR, "Conv_FloatToString", inp={"InFloat": "@pm.ReturnValue"}); g.call("pcs2", K_STR, "Concat_StrStr", inp={"A": "@pcs.ReturnValue", "B": " ms="})
        g.call("pcs3", K_STR, "Concat_StrStr", inp={"A": "@pcs2.ReturnValue", "B": "@pms.ReturnValue"})
        g.call("plg", MGR + ".BP_AltUIManager_C", "Log Line", inp={"self": "@pgc.AsBP Alt UIManager", "text": "@pcs3.ReturnValue"})
        g.chain("spw", "pga", "pgc", "plg")
    return g


MODLOADER_VARS = [var("SpT", "float"), var("State", "int"), var("Rows", "name", "array"), var("Idx", "int"), var("Hits", "name", "array"), var("HitIdx", "int"), var("Busy", "bool")]


assets = [blueprint(ENTRY, E_ACTOR, variables=[var("Spawned", "bool")] + MGR_VARS, event_graph=event_graph()),
          blueprint(MODLOADER, E_ACTOR, variables=MODLOADER_VARS, event_graph=modloader_graph()),
          datatable(M + "/TKA_BlueprintLoader", BPL_STRUCT, rows={"AltUI": {"Actor Class": ENTRY + ".BP_AltUILoaderEntry_C"}})]
write(os.path.join(os.path.dirname(__file__), "..", "60_bploader.json"), assets)
