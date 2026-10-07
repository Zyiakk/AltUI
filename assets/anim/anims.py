"""The animations the pipeline builds (docs/specs/2026-10-06-anim-pipeline-design.md): name -> source animation of the game, Blender
modifier (module in assets/anim/blender) and its parameters. 'test': only in a test build (ALTUI_ANIMTEST=1, the round trip copy of
Female_Walk)."""
import os
ANIMS = {
    "Female_WalkCopy": {"source": "Female_Walk", "modifier": None, "params": {}, "test": True},
}


def enabled(name):
    """Whether this build includes the animation (and a style playing it): 'test' needs ALTUI_ANIMTEST=1."""
    return not (ANIMS[name].get("test") and os.environ.get("ALTUI_ANIMTEST") != "1")
