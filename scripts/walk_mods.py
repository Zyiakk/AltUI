#!/usr/bin/env python3
"""Walk / run mods - the single source for the generator (gen_move: template ABPs, BP_AltUIMove), the converter (walkpak) and the
manager's scan (docs/specs/2026-10-27-walk-mods-design.md).

A walk mod is a pak Mod/WalkAltUI_<Name>/ with the mod's Female_Walk and / or Female_Run (moved, not renamed) and child ABPs of
Jodi_Anim copied from AltUI's templates, their placeholder imports pointed at the mod's animations. Three families:
  ABP_AltUIWalkTpl_<run>_<idle>   walk = the mod, run / idle = AltUI's built-in styles
  ABP_AltUIRunTpl_<walk>_<idle>   run = the mod
  ABP_AltUIWalkRunTpl_<idle>      walk and run = the mod
The prefix says the pak is built for AltUI."""

MOD_PREFIX = "WalkAltUI_"                                   # what the converter writes and the manager's scan accepts
TEMPLATE_DIR = "/Game/Mod/AltUI"
TEMPLATE_WALK = "/Game/Mod/AltUI/Female_WalkTemplate"     # placeholders the templates' players point at (not in Anims/: verify_anims)
TEMPLATE_RUN = "/Game/Mod/AltUI/Female_RunTemplate"
GAME_WALK = "/Game/Project/Character/Jodi/Animations/Female_Walk"   # what a replacer pak overwrites
GAME_RUN = "/Game/Project/Character/Jodi/Animations/Female_Run"
ANIM_WALK, ANIM_RUN = "Female_Walk", "Female_Run"          # object names of the moved animations (cooked objects keep their name)
WALK_PREFIX, RUN_PREFIX, BOTH_PREFIX = "ABP_AltUIWalkTpl_", "ABP_AltUIRunTpl_", "ABP_AltUIWalkRunTpl_"
# a loop the game can drive (docs/notes/2026-10-06-tempo.md): without MoveData_Speed she stands still, without Rotation Speed she cannot turn
REQUIRED_CURVES = {"MoveData_Speed": "she would stand still", "Rotation Speed": "she could not turn"}
WANTED_CURVES = ("Forward Moving Alpha", "MoveData_FootPhase", "Enable_LeanLR", "Upper Body Yaw Ratio")


def walk_tpl(run, idle): return "%s%s_%s" % (WALK_PREFIX, run, idle)
def run_tpl(walk, idle): return "%s%s_%s" % (RUN_PREFIX, walk, idle)
def both_tpl(idle): return "%s%s" % (BOTH_PREFIX, idle)


def mod_class_path(mod, tpl):
    """Object path of a mod's child ABP class, as LoadClassAsset_Blocking wants it."""
    return "/Game/Mod/%s/%s.%s_C" % (mod, tpl, tpl)


def check_anim(ua, ux):
    """Whether a cooked AnimSequence can be a walk / run loop: errors (refuse) for a missing required curve, warnings for the rest.
    speed = mean MoveData_Speed (cm/s)."""
    import animcurves, uasset_props as up
    rc = animcurves.read_bytes(ua, ux); c = rc["curves"]
    errors = ["curve %s missing - %s" % (k, why) for k, why in REQUIRED_CURVES.items() if k not in c]
    warnings = ["curve %s missing" % k for k in WANTED_CURVES if k not in c]
    props = next((v["props"] for k, v in up.dump_bytes(ua, ux).items() if isinstance(v, dict) and "props" in v and not k.startswith("Default")), {})
    markers = {m.get("MarkerName") for m in props.get("AuthoredSyncMarkers", [])}
    if not {"L", "R"} <= markers: warnings.append("sync markers L / R missing - blending walk <-> run may slide")
    if "Footstep" not in {n.get("NotifyName") for n in props.get("Notifies", [])}: warnings.append("no Footstep notifies - no step sounds")
    speed = None
    if "MoveData_Speed" in c:
        rows = animcurves.sample({"length": rc["length"] or 1.0, "curves": {"s": c["MoveData_Speed"]}})["s"]   # one row per frame
        speed = sum(v for _, v in rows) / len(rows)
    return {"errors": errors, "warnings": warnings, "speed": speed}
