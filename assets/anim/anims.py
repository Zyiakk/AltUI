"""The animations the pipeline builds (internal design notes): name -> source animation of the game, Blender
modifier (module in assets/anim/blender) and its parameters. 'test': only in a test build (ALTUI_ANIMTEST=1, the round trip copy of
Female_Walk)."""
import os
ANIMS = {
    "Female_WalkCopy": {"source": "Female_Walk", "modifier": None, "params": {}, "test": True},
}
# entries for local tests only (anims_local.py: ANIMS_LOCAL, never published - release/snapshot.toml)
_LOCAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "anims_local.py")
if os.path.exists(_LOCAL):
    _ns = {}
    with open(_LOCAL) as _f: exec(compile(_f.read(), _LOCAL, "exec"), _ns)
    ANIMS.update(_ns["ANIMS_LOCAL"])


def enabled(name):
    """Whether this build includes the animation (and a style playing it): 'test' needs ALTUI_ANIMTEST=1."""
    return not (ANIMS[name].get("test") and os.environ.get("ALTUI_ANIMTEST") != "1")
