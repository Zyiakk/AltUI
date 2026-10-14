#!/usr/bin/env python3
"""Idle mods - the single source for the generator (gen_move: template ABPs, BP_AltUIMove) and the converter (idlepak).

An idle mod is a pak Mod/IdleAltUI_<Name>/ with the mod's Female_Idle (moved, not renamed) and one child ABP of
Jodi_Anim per walk / run combination, copied from AltUI's templates ABP_AltUIIdleTpl_<walk>_<run> with the placeholder
animation import pointed at the mod's Female_Idle. The prefix says the pak is built for AltUI."""

MOD_PREFIX = "IdleAltUI_"                                  # what the converter writes and the manager's scan accepts
TEMPLATE_PREFIX = "ABP_AltUIIdleTpl_"                      # + "<walk>_<run>"; package and class keep this name in a mod
TEMPLATE_DIR = "/Game/Mod/AltUI"
TEMPLATE_ANIM = "/Game/Mod/AltUI/Female_IdleTemplate"   # placeholder the templates' idle player points at (not in Anims/: that folder is the animation pipeline's, verify_anims)
GAME_IDLE = "/Game/Project/Character/Jodi/Animations/Female_Idle"   # what a replacer pak overwrites
ANIM_NAME = "Female_Idle"                                  # object name of the moved animation (cooked objects keep their name)


def template_name(walk, run):
    return "%s%s_%s" % (TEMPLATE_PREFIX, walk, run)


def mod_class_path(mod, walk, run):
    """Object path of a mod's child ABP class, as LoadClassAsset_Blocking wants it."""
    n = template_name(walk, run)
    return "/Game/Mod/%s/%s.%s_C" % (mod, n, n)
