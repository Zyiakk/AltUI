"""BP_AltUIMove: target factor (off / walk / run / crouch / air, 0 = 100 %) and animation rate target."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *


def main():
    mv = cdo("/Game/Mod/AltUI/BP_AltUIMove.BP_AltUIMove_C")
    def tf(*a): mv.call_method("Test Target Factor", args=a); return round(mv.get_editor_property("TmpFloat"), 3)
    def rt(*a): mv.call_method("Test Rate Target", args=a); return round(mv.get_editor_property("TmpFloat"), 3)
    expect("off -> 1", tf(False, 150.0, 200.0, True, False, False), 1.0)
    expect("walk", tf(True, 150.0, 200.0, False, False, False), 1.5)
    expect("run", tf(True, 150.0, 200.0, True, False, False), 2.0)
    expect("never set = 100 %", tf(True, 0.0, 0.0, True, False, False), 1.0)
    expect("crouch -> 1", tf(True, 50.0, 50.0, False, True, False), 1.0)
    expect("in the air -> 1", tf(True, 50.0, 50.0, True, False, True), 1.0)
    expect("moving: rate follows", rt(1.5, 300.0, False), 1.5)
    expect("standing: rate 1", rt(1.5, 5.0, False), 1.0)
    expect("montage: rate 1", rt(1.5, 300.0, True), 1.0)
    # run key in RunMode 2: the game decides by Speed 2d > 250 (running -> stop); with the factor the decision has to use the unscaled speed
    # 0 = the game decided right, 1 = start running, 2 = stop running
    def rf(*a): mv.call_method("Test Run Fix", args=a); return mv.get_editor_property("TmpInt")
    expect("walking 130 %: start running", rf(282.0, 1.3), 1)
    expect("walking 100 %: game is right", rf(217.0, 1.0), 0)
    expect("running 50 %: stop running", rf(240.0, 0.5), 2)
    expect("running 150 %: game is right", rf(700.0, 1.5), 0)
    expect("standing: game is right", rf(0.0, 1.5), 0)
    # walk / run style -> anim class (None = Normal; Normal / Normal = Jodi_Anim itself)
    def sc(w, r, i="None"): mv.call_method("Test Style Class", args=(w, r, i)); c = mv.get_editor_property("TmpClass"); return c.get_name() if c else None
    expect("normal / normal = Jodi_Anim", sc("None", "None"), "Jodi_Anim_C")
    expect("normal spelled out", sc("Normal", "Normal"), "Jodi_Anim_C")
    expect("unknown style = Jodi_Anim", sc("Moonwalk", "None"), "Jodi_Anim_C")
    expect("another unknown walk style = Jodi_Anim", sc("Limp", "None"), "Jodi_Anim_C")
    # a style saved before it was removed (RunStyle "hurt" in a user's AltUI.sav, 2026-10-06) counts as Normal on its own side only
    expect("removed walk style, normal run", sc("Hurt", "Normal"), "Jodi_Anim_C")
    # the loop that replaces the game's start animation: per gait, None on a Normal side
    def sl(w, r, run): mv.call_method("Test Style Loop", args=(w, r, run)); o = mv.get_editor_property("TmpObj"); return o.get_name() if o else None
    expect("start loop normal", sl("Normal", "Normal", False), None)
    expect("start loop unknown", sl("hurt", "hurt", True), None)   # also a style saved before it was removed (Hurt, 2026-10-06)
    expect("removed style = Jodi_Anim", sc("Hurt", "Hurt"), "Jodi_Anim_C")
    # idle styles: the game's standing loops in every build
    idles = [k for k in ("Afk1", "Afk2", "Afk3", "Careful", "Hurt", "Mirror") if unreal.EditorAssetLibrary.does_asset_exist("/Game/Mod/AltUI/ABP_AltUIStyle_Normal_Normal_" + k)]
    expect("game idles built", len(idles), 6)
    expect("idle only", sc("None", "None", "Careful"), "ABP_AltUIStyle_Normal_Normal_Careful_C")
    expect("idle ignoring case", sc("None", "None", "careful"), "ABP_AltUIStyle_Normal_Normal_Careful_C")
    expect("removed idle = Jodi_Anim", sc("None", "None", "Yawn"), "Jodi_Anim_C")
    def wc(w, r, i): mv.call_method("Test Want Class", args=(w, r, i)); c = mv.get_editor_property("TmpClass"); return c.get_name() if c else None
    expect("want class game idle", wc("None", "None", "Afk2"), "ABP_AltUIStyle_Normal_Normal_Afk2_C")
    expect("want class normal", wc("None", "None", "None"), "Jodi_Anim_C")
    expect("want class missing idle mod = Jodi_Anim", wc("None", "None", "IdleAltUI_NotInstalled"), "Jodi_Anim_C")
    # walk / run mods (docs/specs/2026-10-27-walk-mods-design.md): a test mod made of AltUI's own templates
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts")); import walk_mods as wm
    eal = unreal.EditorAssetLibrary; mod = "WalkAltUI_EdTest"; d = "/Game/Mod/" + mod
    for n in (wm.walk_tpl("Normal", "Normal"), wm.walk_tpl("Normal", "Afk1"), wm.run_tpl("Normal", "Normal"), wm.both_tpl("Normal")):
        eal.duplicate_asset(wm.TEMPLATE_DIR + "/" + n, d + "/" + n)
    def wp(w, r, i="None"): mv.call_method("Test Want Class", args=(w, r, i)); c = mv.get_editor_property("TmpClass"); return c.get_path_name() if c else None
    def cp(n): return "%s/%s.%s_C" % (d, n, n)
    try:
        expect("walk mod", wp(mod, "None"), cp(wm.walk_tpl("Normal", "Normal")))
        expect("walk mod ignoring case", wp(mod.lower(), "None"), cp(wm.walk_tpl("Normal", "Normal")))
        expect("walk mod + built-in idle", wp(mod, "None", "Afk1"), cp(wm.walk_tpl("Normal", "Afk1")))
        expect("walk mod + idle without template -> Normal", wp(mod, "None", "Careful"), cp(wm.walk_tpl("Normal", "Normal")))
        expect("walk + run of the same mod", wp(mod, mod), cp(wm.both_tpl("Normal")))
        expect("run mod", wp("None", mod), cp(wm.run_tpl("Normal", "Normal")))
        expect("run mod not lost", mv.get_editor_property("MoveRunLost"), False)
        expect("walk mod beats an idle mod", wp(mod, "None", "IdleAltUI_Nope"), cp(wm.walk_tpl("Normal", "Normal")))
        expect("idle lost", mv.get_editor_property("MoveIdleLost"), True)
        expect("walk mod beats another run mod", wp(mod, "WalkAltUI_Other"), cp(wm.walk_tpl("Normal", "Normal")))
        expect("run lost", mv.get_editor_property("MoveRunLost"), True)
        expect("missing walk mod = Normal", wp("WalkAltUI_Missing", "None"), "/Game/Project/Character/Jodi/Jodi_Anim.Jodi_Anim_C")
        expect("missing walk mod, the run mod still counts", wp("WalkAltUI_Missing", mod), cp(wm.run_tpl("Normal", "Normal")))
        expect("no lost side without mods", (wp("None", "None"), mv.get_editor_property("MoveRunLost"), mv.get_editor_property("MoveIdleLost")),
               ("/Game/Project/Character/Jodi/Jodi_Anim.Jodi_Anim_C", False, False))
    finally:
        eal.delete_directory(d)
    mv.call_method("Test Want Class", args=("None", "None", "None"))


run(main)
