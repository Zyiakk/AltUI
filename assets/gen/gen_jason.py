"""Generates assets/29c_jason.json: BP_AltUIJason, the Jason prototype (docs/notes/2026-10-18-follower-munition-und-npc-typen.md).
A child of the story's Jason (Character_NPC, Jason_Controller - a follower by build: he fights zombies and falls back to his
master; without path points his controller waits and runs the NPC orders of Npc_Controller). The game never saves it, and
his death skips Jason's own Character Die: that one spawns Camera_Death and turns the player's view onto him for good."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *
from gen_follower import f_need_to_save, f_count_weapon_ammo, f_is_ragdoll_or_dying

JASON = M + "/BP_AltUIJason"; JASONCTRL = M + "/BP_AltUIJasonCtrl"


def f_character_die():
    """Character_Player_Base's death (ragdoll, health 0, its delegates) - past Jason's (death camera, Jodi's "Jason!") and past
    Character_NPC's: that one calls AI Controller.on Character Die, and Jason_Controller's ends the game (Game Over(false), the
    story's mission lost; ui-test-120 #5). The controller's own part of it (AI_Controller: tick off) here. An override of on
    Character Die in our controller is no way: the game defines it in AI_Controller, which the kit's stub chain lacks - its
    SuperStruct pointed at Npc_Controller_C and the game stopped on load ("Could not find SuperStruct on Character Die")."""
    g = G(); g.n("pd", "call_parent", function="Character Die", cls=P_CPB, inp={"murderer": "@entry.murderer"})
    g.self_("me"); g.call("gc", E_PAWN, "GetController", inp={"self": "@me.self"}); g.call("tk", E_ACTOR, "SetActorTickEnabled", inp={"self": "@gc.ReturnValue", "bEnabled": "false"})
    g.chain("entry", "pd", "tk")
    return fn("Character Die", [param("murderer", "object:" + P_CB)], graph=g, override=True)


def f_change_controller():
    """Init Jason (and every later controller change) asks for Jason_Controller: ours instead (ui-test-120 #2: with Jason's own he
    turned to Jodi but never walked - its Decide Next State never runs the orders)."""
    g = G(); g.n("pc", "call_parent", function="Change Controller", cls=P_CB, inp={"Class": JASONCTRL})
    g.chain("entry", "pc")
    return fn("Change Controller", [param("Class", "class:/Script/AIModule.AIController")], graph=g, override=True)


def f_ctrl_decide_next_state():
    """Npc_Controller's Decide Next State instead of Jason_Controller's (that one only fights and walks his story path): the orders -
    follow = walk to master when farther than 300 (600 while busy), wait = stay at Order Location - and Jason's Need to Do for the
    fighting when near."""
    g = G(); g.n("pd", "call_parent", function="Decide Next State", cls=P_NPCCTRL); g.chain("entry", "pd")
    return fn("Decide Next State", graph=g, override=True)


def build():
    return [blueprint(JASONCTRL, P_JASONCTRL, functions=[f_ctrl_decide_next_state()]),
            # InfAmmo: his own Count Weapon Ammo is a fixed 100 (the story's endless ammo) - ours makes it the chip's (ui-test-123)
            blueprint(JASON, P_JASON, variables=[var("InfAmmo", "bool"), var("NotTarget", "bool")],   # NotTarget: gear menu "attackable" off (gen_follower)
                      functions=[f_need_to_save(), f_character_die(), f_change_controller(), f_count_weapon_ammo(), f_is_ragdoll_or_dying()])]


if __name__ == "__main__":
    write(os.path.join(os.path.dirname(__file__), "..", "29c_jason.json"), build())
