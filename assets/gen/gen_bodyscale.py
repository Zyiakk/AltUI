#!/usr/bin/env python3
"""ABP_BodyScale: post-process AnimBlueprint that scales bone groups of Jodi's skeleton (Body Shape sliders for converted bodies)."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
from bpdsl import animblueprint, var, write
import bodyscale_groups as bg

SKELETON = "/Game/Project/Character/Jodi/Body/Female_Skeleton"
assets = [animblueprint(bg.ABP_PATH, SKELETON,
                        variables=[var(v, "struct:/Script/CoreUObject.Vector", default="(X=1,Y=1,Z=1)") for v, _, _ in bg.GROUPS]
                                  + [var(v, "struct:/Script/CoreUObject.Vector", default="(X=0,Y=0,Z=0)") for v, _ in bg.SHIFTS],
                        # floor compensation first (root / foot translation, component space), then the scale nodes
                        nodes=[{"bone": b, "kind": "translate", "var": v} for v, bs in bg.SHIFTS for b in bs]
                              + [{"bone": b, "mode": m, "var": v} for v, bs, m in bg.GROUPS for b in bs])]
write(os.path.join(os.path.dirname(__file__), "..", "25_bodyscale.json"), assets)
