"""Blender helpers of the animation pipeline (docs/specs/2026-10-06-anim-pipeline-design.md): load Jodi from the kit FBX, put a
.psa animation (umodel) on her skeleton as an action, sample bone positions.

Conventions (measured against female.fbx, docs/notes/2026-10-06-tempo.md): the armature keeps the kit's centimetres under an object
scale of 0.01; Blender's bone-local rest transform equals the psa reference with Y negated and the quaternion as (w, -x, y, -z); the
psa keys are mirrored in Y against that reference, so a key maps to the Blender bone-local transform as  position unchanged, quaternion
conjugated. Bones not listed under [UseTranslationBoneNames] in umodel's .config keep their rest translation (bAnimRotationOnly)."""
import os, sys
import bpy
from mathutils import Matrix, Quaternion, Vector
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import psa as psalib


def load_jodi(fbx):
    """Empty scene + the kit FBX; returns (armature, body mesh). Armature in cm under object scale 0.01, faces -Y."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx)
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    body = next((o for o in bpy.data.objects if o.type == "MESH" and o.find_armature() == arm), None)
    return arm, body


def translation_bones(config_path):
    out, on = set(), False
    for line in open(config_path):
        line = line.strip()
        if line.startswith("["): on = line == "[UseTranslationBoneNames]"; continue
        if on and line: out.add(line)
    return out


def local_rest(bone):
    return bone.matrix_local if bone.parent is None else bone.parent.matrix_local.inverted() @ bone.matrix_local


def key_to_local(pos, quat_xyzw):
    x, y, z, w = quat_xyzw
    return Matrix.Translation(Vector(pos)) @ Quaternion((w, -x, -y, -z)).to_matrix().to_4x4()


def apply_psa(arm, psa_path, config_path=None, action_name=None):
    """Keys every frame of the .psa onto the armature as a new action; returns (frames, fps)."""
    d = psalib.read(psa_path); a = d["anims"][0]; names = [b["name"] for b in d["bones"]]
    tbones = translation_bones(config_path) if config_path and os.path.exists(config_path) else None
    act = bpy.data.actions.new(action_name or a["name"]); arm.animation_data_create(); arm.animation_data.action = act
    pbs = arm.pose.bones
    for pb in pbs: pb.rotation_mode = "QUATERNION"
    rest = {pb.name: local_rest(pb.bone) for pb in pbs}
    for f in range(a["frames"]):
        keys = psalib.frame(d, f)
        for i, name in enumerate(names):
            pb = pbs.get(name)
            if pb is None: continue
            loc = key_to_local(*keys[i])
            if tbones is not None and name not in tbones:
                loc = Matrix.Translation(rest[name].to_translation()) @ loc.to_quaternion().to_matrix().to_4x4()
            pb.matrix_basis = rest[name].inverted() @ loc
            pb.keyframe_insert("location", frame=f); pb.keyframe_insert("rotation_quaternion", frame=f)
    bpy.context.scene.frame_start, bpy.context.scene.frame_end = 0, a["frames"] - 1
    # umodel's rate is frames / length (57 / 1.8667 = 30.5); the keys are 1/30 s apart (frame 56 = the loop end at 1.8667 s)
    bpy.context.scene.render.fps, bpy.context.scene.render.fps_base = 30, 1.0; return a["frames"], 30.0


def bone_world(arm, name, frame):
    """World position (metres) of a bone's head at a frame."""
    bpy.context.scene.frame_set(frame)
    return arm.matrix_world @ arm.pose.bones[name].head


def export_fbx(arm, path):
    """The armature with its action as an animation FBX for the kit: centimetres like the kit's own export (UE ignores the FBX unit
    factor), axes and bone axes as the kit's import expects (the export_scene.fbx arguments below). The armature object is the UE bone
    'root'; it is taken out of the 0.01 empty and given scale 1 so its centimetre bones and keys export as centimetres."""
    sc = bpy.context.scene; old = sc.unit_settings.scale_length
    mw_parent = arm.parent; arm.parent = None; arm.matrix_world = Matrix.Identity(4)
    bpy.ops.object.select_all(action="DESELECT"); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    try:
        sc.unit_settings.scale_length = 0.01
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"ARMATURE"}, apply_unit_scale=True,
                                 apply_scale_options="FBX_SCALE_NONE", global_scale=1.0, add_leaf_bones=False, use_armature_deform_only=False,
                                 primary_bone_axis="Y", secondary_bone_axis="X", axis_forward="-Z", axis_up="Y",
                                 bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=False, bake_anim_use_all_actions=False,
                                 bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=0.0)
    finally:
        sc.unit_settings.scale_length = old


def load_action_fbx(arm, path):
    """Puts the action of an exported animation FBX on arm; returns the frame count."""
    before = set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]; src = next(o for o in new if o.type == "ARMATURE")
    act = src.animation_data.action; slot = getattr(src.animation_data, "action_slot", None)
    arm.animation_data_create(); arm.animation_data.action = act
    if slot is not None: arm.animation_data.action_slot = slot   # Blender 4.4+: an action acts through its slot
    for pb in arm.pose.bones: pb.rotation_mode = "QUATERNION"
    for o in new: bpy.data.objects.remove(o, do_unlink=True)
    bpy.context.scene.render.fps, bpy.context.scene.render.fps_base = 30, 1.0
    return int(round(act.frame_range[1] - act.frame_range[0])) + 1
