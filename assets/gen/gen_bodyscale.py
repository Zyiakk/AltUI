#!/usr/bin/env python3
"""ABP_BodyScale: post-process AnimBlueprint that scales bone groups of Jodi's skeleton (Body Shape sliders for converted bodies)."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
from bpdsl import animblueprint, animsequence_stub, var, write
import bodyscale_groups as bg

SKELETON = "/Game/Project/Character/Jodi/Body/Female_Skeleton"
EYE_CLOSED = "/Game/Project/Character/Jodi/Animations/Female_EyeClosed"   # the game's blink (additive, Jodi_Anim "blink blend"); a stub in the kit
# per lid 0 open (the game blinks as always) .. 1 closed - Face tab "Eyes closed" / "Left eye closed" / "Right eye closed" (max of both).
# Female_EyeClosed turns only Eye_L / Eye_R (the lids): one additive per lid, limited to its bone
EYE_VARS = [("EyeClosedL", "Eye_L"), ("EyeClosedR", "Eye_R")]
assets = [animsequence_stub(EYE_CLOSED, SKELETON, additive=True),
          animblueprint(bg.ABP_PATH, SKELETON,
                        variables=[var(v, "struct:/Script/CoreUObject.Vector", default="(X=1,Y=1,Z=1)") for v, _, _ in bg.GROUPS]
                                  + [var(v, "struct:/Script/CoreUObject.Vector", default="(X=0,Y=0,Z=0)") for v, _ in bg.SHIFTS]
                                  + [var(v, "struct:/Script/CoreUObject.Rotator", default="(P=0,Y=0,R=0)") for v, _ in bg.ROTATIONS]
                                  + [var(v, "float", default="0.0") for v, _ in EYE_VARS],
                        additive=[(EYE_CLOSED, v, 1.0, [b]) for v, b in EYE_VARS],   # its last frame (eyes shut), as Jodi_Anim's evaluator
                        # floor compensation first (root / foot translation, component space), then the scale nodes, then the
                        # additive rotations (breast / glutes angle; the game's physics may override them while it simulates)
                        nodes=[{"bone": b, "kind": "translate", "var": v} for v, bs in bg.SHIFTS for b in bs]
                              + [{"bone": b, "mode": m, "var": v} for v, bs, m in bg.GROUPS for b in bs]
                              + [{"bone": b, "kind": "rotate", "var": v} for v, bs in bg.ROTATIONS for b in bs])]
write(os.path.join(os.path.dirname(__file__), "..", "25_bodyscale.json"), assets)
