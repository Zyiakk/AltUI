"""blender -b --python assets/anim/blender/measure_cli.py -- <json {fbx, psa, config | anim_fbx}> : prints MEASURE <json>."""
import json, os, sys
import bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import animlib, measure
spec = json.loads(sys.argv[sys.argv.index("--") + 1])
arm, body = animlib.load_jodi(spec["fbx"])
if spec.get("psa"):
    frames, _ = animlib.apply_psa(arm, spec["psa"], spec.get("config"))
    if spec.get("modifier"):
        import importlib; importlib.import_module(spec["modifier"]).apply(arm, frames, spec.get("params", {}))
else: frames = animlib.load_action_fbx(arm, spec["anim_fbx"])
res, _ = measure.analyze(arm, frames)
print("MEASURE " + json.dumps(res))
