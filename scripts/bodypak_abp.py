#!/usr/bin/env python3
"""Reads the bone-scale defaults of a body mod's own post-process AnimBlueprint (cooked): ModifyBone nodes + the variables their
Scale pins are bound to (PropertyAccessLibrary copy records) -> {group: [x, y, z]} in ABP_BodyScale's groups."""
import os, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import uasset_props
import bodyscale_groups as bg


def _dump(ua, ux):
    d = tempfile.mkdtemp(prefix="abp_")
    p = os.path.join(d, "A.uasset"); open(p, "wb").write(ua); open(p[:-7] + ".uexp", "wb").write(ux)
    return uasset_props.dump(p)


def _chain_order(props):
    """Anim node keys in evaluation order: follow ComponentPose/LocalPose LinkIDs back from the output (ComponentToLocalSpace).
    LinkID = index of the target node among the class's AnimGraphNode_* properties (CDO order)."""
    nodes = [k for k in props if k.startswith("AnimGraphNode_")]
    c2l = next((k for k in nodes if k.split("_")[1] == "ComponentToLocalSpace"), None)
    if c2l is None:
        return [k for k in nodes if isinstance(props[k], dict) and "BoneToModify" in props[k]]   # no chain info: CDO order
    order = []; cur = props[c2l].get("ComponentPose", {}).get("LinkID", -1)
    while 0 <= cur < len(nodes):
        k = nodes[cur]
        if k.split("_")[1] in ("LocalToComponentSpace", "LinkedInputPose", "Root"):
            break
        order.append(k); cur = props[k].get("ComponentPose", {}).get("LinkID", -1)
    return list(reversed(order))


def read_abp_defaults(ua, ux):
    """NET bone scales per group after the mod's whole chain ran (see bodyscale_groups: children inherit a bone's change,
    Replace sets the bone's scale absolutely, Additive multiplies the inherited one; nodes run in graph link order)."""
    d = _dump(ua, ux)
    cls = next((v for v in d.values() if v["class"] == "AnimBlueprintGeneratedClass"), None)
    cdo = next((v for v in d.values() if v["class"].endswith("_C") and any(k.startswith("AnimGraphNode_") for k in v["props"])), None)
    warns = []
    if cls is None or cdo is None:
        return {v: [1.0, 1.0, 1.0] for v, _, _ in bg.GROUPS}, ["no AnimBlueprintGeneratedClass / CDO found in the ABP"]
    props = cdo["props"]
    # node -> variable bound to its Scale pin
    bound = {}
    lib = cls["props"].get("PropertyAccessLibrary") or {}
    segs = lib.get("PathSegments", []); src = lib.get("SrcPaths", []); dst = lib.get("DestPaths", [])
    batches = lib.get("CopyBatches", []); batches = [batches] if isinstance(batches, dict) else batches
    for b in batches:
        for c in b.get("Copies", []):
            s_ = src[c["AccessIndex"]]; spath = [x["Name"] for x in segs[s_["PathSegmentStartIndex"]:s_["PathSegmentStartIndex"] + s_["PathSegmentCount"]]]
            for di in range(c["DestAccessStartIndex"], c["DestAccessEndIndex"]):
                t = dst[di]; dpath = [x["Name"] for x in segs[t["PathSegmentStartIndex"]:t["PathSegmentStartIndex"] + t["PathSegmentCount"]]]
                if len(spath) == 1 and len(dpath) == 2 and dpath[1] == "Scale":
                    bound[dpath[0]] = spath[0]
    cs = {b: [1.0, 1.0, 1.0] for b in bg.BONE_GROUP}
    for key in _chain_order(props):
        node = props[key]
        if not isinstance(node, dict) or "BoneToModify" not in node:
            warns.append("node %s is not a ModifyBone node - its effect is not carried over (use --keep-abp to keep the mod's blueprint)" % key); continue
        if node.get("TranslationMode", "BMM_Ignore") != "BMM_Ignore" or node.get("RotationMode", "BMM_Ignore") != "BMM_Ignore":
            warns.append("node %s moves/rotates a bone - only scaling is carried over" % key)
        bone = node["BoneToModify"]["BoneName"]
        if bone not in bg.BONE_GROUP:
            warns.append("bone %s is not in ABP_BodyScale's groups - its scaling is not carried over" % bone); continue
        mode = node.get("ScaleMode", "BMM_Ignore")
        if mode == "BMM_Ignore":
            continue
        val = props.get(bound[key]) if key in bound else node.get("Scale")
        vec = [float(val["x"]), float(val["y"]), float(val["z"])]
        old = cs[bone]; new = vec if mode == "BMM_Replace" else [o * v for o, v in zip(old, vec)]
        delta = [n / o if o else 1.0 for n, o in zip(new, old)]
        cs[bone] = new
        for child in bg.descendants(bone):
            cs[child] = [c * dl for c, dl in zip(cs[child], delta)]
    out = {}
    for v, bs, _ in bg.GROUPS:
        l = cs[bs[0]]
        if len(bs) > 1 and [round(x, 4) for x in l] != [round(x, 4) for x in cs[bs[1]]]:
            warns.append("group %s: %s and %s end up with different scales - left side kept" % (v, bs[0], bs[1]))
        out[v] = l
    return out, warns

import struct
PP_TAG = "PostProcessAnimBlueprint"


def attach_abp(pkg):
    """Points the mesh's PostProcessAnimBlueprint at ABP_BodyScale. Returns (had_abp, old_package_path).
    Existing ABP: the three imports (package, class, CDO) are renamed in place - export data untouched.
    No ABP: imports are added and the ObjectProperty tag is inserted before the closing 'None' of the Female export's tags."""
    cls = [im for im in pkg.imports if im.class_name == "AnimBlueprintGeneratedClass"]
    if cls:
        c = cls[0]; old_pkg = pkg.imports[-c.outer - 1].object_name; old_cls = c.object_name
        for im in pkg.imports:
            if im.class_name == "Package" and im.object_name == old_pkg: im.object_name = bg.ABP_PATH
            if im.class_package == old_pkg: im.class_package = bg.ABP_PATH
            if im.class_name == old_cls: im.class_name = bg.ABP_CLASS
            if im.object_name == old_cls: im.object_name = bg.ABP_CLASS
            if im.object_name == "Default__" + old_cls: im.object_name = "Default__" + bg.ABP_CLASS
        return True, old_pkg
    pi = pkg.add_import("/Script/CoreUObject", "Package", 0, bg.ABP_PATH)
    ci = pkg.add_import("/Script/Engine", "AnimBlueprintGeneratedClass", pi, bg.ABP_CLASS)
    pkg.add_import(bg.ABP_PATH, bg.ABP_CLASS, pi, "Default__" + bg.ABP_CLASS)
    e = next(x for x in pkg.exports if x.object_name == "Female")
    r = uasset_props.Reader(e.data, pkg.names, pkg.imports, pkg.exports)
    while True:
        pos = r.p; t = r.tag()
        if t is None: break
        r.p += t["size"]
    tag = struct.pack("<ii", pkg.name_index(PP_TAG), 0) + struct.pack("<ii", pkg.name_index("ObjectProperty"), 0) + struct.pack("<ii", 4, 0) + b"\0" + struct.pack("<i", ci)
    e.data = e.data[:pos] + tag + e.data[pos:]
    e.deps_create_before_ser = list(e.deps_create_before_ser) + [ci]
    return False, None
