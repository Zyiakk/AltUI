"""Renders phases of a walk cycle from several directions (one PNG per phase x view) for scripts/animlook.py.
  blender -b --python assets/anim/blender/sheet.py -- <json spec>
spec: {"fbx": kit body, "psa": ..., "config": ..., "anim_fbx": instead of psa an exported animation, "phases": 8, "views": [...],
       "res": [w, h], "out": dir}. Jodi faces -Y; the camera follows the pelvis in x/y so she stays centred while the cycle plays
(the walk is in place in the game - the root does not move). A thin line on the ground marks her midline (x of the pelvis at rest)."""
import json, os, sys, math
import bpy
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import animlib

spec = json.loads(sys.argv[sys.argv.index("--") + 1])
arm, body = animlib.load_jodi(spec["fbx"])
if spec.get("psa"):
    frames, _ = animlib.apply_psa(arm, spec["psa"], spec.get("config"))
    if spec.get("modifier"):   # build it here instead of reading an exported FBX back (Blender's re-import changes bone axes)
        import importlib; importlib.import_module(spec["modifier"]).apply(arm, frames, spec.get("params", {}))
else:
    bpy.ops.import_scene.fbx(filepath=spec["anim_fbx"])
    src = next(o for o in bpy.data.objects if o.type == "ARMATURE" and o != arm)
    arm.animation_data_create(); arm.animation_data.action = src.animation_data.action
    frames = int(src.animation_data.action.frame_range[1]) + 1
    for o in list(bpy.data.objects):
        if o == src or (o.parent == src) or (o.type == "EMPTY" and o != arm.parent): bpy.data.objects.remove(o, do_unlink=True)

# clothes (glTF from umodel, same skeleton): bound to Jodi's animated armature by bone name, their own armature removed
cloth_meshes = []
for path in spec.get("meshes", []):
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        if o.type != "MESH": continue
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
        for m in o.modifiers:
            if m.type == "ARMATURE": m.object = arm
        cloth_meshes.append(o)
    for o in new:
        if o.type != "MESH": bpy.data.objects.remove(o, do_unlink=True)

sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"
sc.render.resolution_x, sc.render.resolution_y = spec.get("res", [300, 400]); sc.render.film_transparent = False
sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.18, 0.18, 0.2)
mat = bpy.data.materials.new("clay"); mat.diffuse_color = (0.78, 0.62, 0.52, 1)
if body: body.data.materials.clear(); body.data.materials.append(mat)
cm = bpy.data.materials.new("cloth"); cm.diffuse_color = (0.25, 0.45, 0.75, 1)
for o in cloth_meshes: o.data.materials.clear(); o.data.materials.append(cm)
# ground + midline
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0)); g = bpy.context.object
gm = bpy.data.materials.new("ground"); gm.diffuse_color = (0.32, 0.34, 0.36, 1); g.data.materials.append(gm)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.001)); line = bpy.context.object; line.scale = (0.004, 2.0, 0.001)
lm = bpy.data.materials.new("line"); lm.diffuse_color = (0.9, 0.85, 0.2, 1); line.data.materials.append(lm)

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
VIEWS = {"front": (0, -1, 0), "left": (1, 0, 0), "back": (0, 1, 0), "right": (-1, 0, 0), "top": (0, 0, 1)}
phases = spec.get("phases", 8); os.makedirs(spec["out"], exist_ok=True)
sc.frame_set(0); pelvis0 = animlib.bone_world(arm, "pelvis", 0)
line.location.x = pelvis0.x
for i in range(phases):
    f = int(round(i * (frames - 1) / phases)); sc.frame_set(f)
    pel = arm.matrix_world @ arm.pose.bones["pelvis"].head
    for v in spec.get("views", ["front", "left", "back", "top"]):
        d = Vector(VIEWS[v])
        if v == "top":
            cam.data.type = "ORTHO"; cam.data.ortho_scale = 1.1; cam.location = (pel.x, pel.y, 3.0); cam.rotation_euler = (0, 0, 0)
        else:
            cam.data.type = "ORTHO"; cam.data.ortho_scale = spec.get("ortho", 2.0)
            target = Vector((pel.x, pel.y, spec.get("target_z", 0.88))); cam.location = target + d * 4.0
            cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        line.location.y = pel.y
        sc.render.filepath = os.path.join(spec["out"], "p%d_%s.png" % (i, v)); bpy.ops.render.render(write_still=True)
print("SHEET OK", frames)
