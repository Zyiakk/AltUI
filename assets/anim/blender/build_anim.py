"""Builds one animation FBX: loads Jodi, puts the source .psa on her, optionally runs a modifier (a module in assets/anim/blender with a parameter set),
exports the FBX and writes timing info (frames, fps, contact times measured on the result) as JSON next to it.
  blender -b --python assets/anim/blender/build_anim.py -- <json spec {fbx, psa, config, out_fbx, out_json, modifier, params}>"""
import json, os, sys
import bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import animlib

spec = json.loads(sys.argv[sys.argv.index("--") + 1])
arm, body = animlib.load_jodi(spec["fbx"])
frames, rate = animlib.apply_psa(arm, spec["psa"], spec.get("config"))
info = {"frames": frames, "fps": 30.0}
if spec.get("modifier"):
    import importlib; mod = importlib.import_module(spec["modifier"])
    info.update(mod.apply(arm, frames, spec.get("params", {})) or {})
if body: bpy.data.objects.remove(body, do_unlink=True)
animlib.export_fbx(arm, spec["out_fbx"])
json.dump(info, open(spec["out_json"], "w"), indent=1)
print("BUILD ANIM OK", spec["out_fbx"])
