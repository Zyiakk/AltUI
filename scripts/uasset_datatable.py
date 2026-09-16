#!/usr/bin/env python3
"""New cooked DataTables from Python values: the generic writer (new_datatable / *_prop / finish_table) and make_mod_table
(TKA_Mod_Table, the table the game lists a mod pak by). Byte layout and import/preload patterns follow the sample mod tables."""
import struct, os
from uasset_pkg import Package, Export, write_fstr

STRUCTS = {
    "DLC_Struct": "/Game/Project/Tables/DLC_Struct",
    "ClothesGroupStruct": "/Game/Project/Clothes/ClothesGroupStruct",
    "ClothesStruct": "/Game/Project/Clothes/ClothesStruct",
    "SkinStruct": "/Game/Project/Tables/SkinStruct",
}
T = {  # property tag names (struct GUID suffixes of game version 0.6.x)
    "Caption": "Caption_2_CF40F849410064585CC285AFBAD051F2", "Desc": "Desc_19_4AD3659040D04182C7F9D9AD8B806911",
    "Version": "Version_22_F42E252047240C6B9DE76395F37B9ED2", "Tables": "Tables_21_CE3E42574FF40670AE5465BCDC6ABBCB",
    "GroupName": "GroupName_7_8AA0AAEA40546BF0AD7B10B1731CEFB1", "Owning": "Owning_11_3A6836014E272C16301F7F8FAC7D5CC4",
    "icon": "icon_8_4C4B98104788963F3C3C0AAA93BA7643", "diffusetexture": "diffusetexture_5_444E164149587AAB9A4CDA82DA6B8F27",
    "normaltexture": "normaltexture_7_0DB866674611FAB2B77D06A399E20AAB",
}


def _fn(pkg, s):
    return struct.pack("<ii", pkg.name_index(s), 0)


def _tag(pkg, name, typ, size, extra=b""):
    return _fn(pkg, name) + _fn(pkg, typ) + struct.pack("<ii", size, 0) + extra + b"\0"


def text_prop(pkg, tag, s):
    v = struct.pack("<Ibi", 2, -1, 1) + write_fstr(s)
    return _tag(pkg, tag, "TextProperty", len(v)) + v


def bool_prop(pkg, tag, v):
    return _fn(pkg, tag) + _fn(pkg, "BoolProperty") + struct.pack("<ii", 0, 0) + (b"\1" if v else b"\0") + b"\0"


def float_prop(pkg, tag, v):
    return _tag(pkg, tag, "FloatProperty", 4) + struct.pack("<f", v)


def name_array_prop(pkg, tag, values):
    v = struct.pack("<i", len(values)) + b"".join(_fn(pkg, x) for x in values)
    return _tag(pkg, tag, "ArrayProperty", len(v), _fn(pkg, "NameProperty")) + v


def object_prop(pkg, tag, import_index):
    refs = pkg.__dict__.setdefault("_row_refs", [])
    if import_index < 0 and import_index not in refs and tag != "RowStruct":
        refs.append(import_index)
    return _tag(pkg, tag, "ObjectProperty", 4) + struct.pack("<i", import_index)


def end_props(pkg):
    return _fn(pkg, "None")


def new_datatable(package_path, object_name, struct_package, struct_name):
    pkg = Package()
    pkg.guid = os.urandom(16)
    eng = pkg.add_import("/Script/CoreUObject", "Package", 0, "/Script/Engine")
    cls = pkg.add_import("/Script/CoreUObject", "Class", eng, "DataTable")
    cdo = pkg.add_import("/Script/Engine", "DataTable", eng, "Default__DataTable")
    spkg = pkg.add_import("/Script/CoreUObject", "Package", 0, struct_package)
    sidx = pkg.add_import("/Script/Engine", "UserDefinedStruct", spkg, struct_name)
    pkg.name_index(package_path); pkg.name_index("/Script/CoreUObject")
    pkg.exports.append(Export(cls, 0, cdo, 0, object_name, 0, 0xb, b""))
    pkg.depends = [[]]
    pkg.generations = [(1, 0)]
    return pkg, sidx


def texture_import(pkg, package_path, object_name=None):
    eng = pkg.find_import("Package", "/Script/Engine")
    p = pkg.find_import("Package", package_path) or pkg.add_import("/Script/CoreUObject", "Package", 0, package_path)
    obj = object_name or package_path.rsplit("/", 1)[1]
    return pkg.find_import("Texture2D", obj, p) or pkg.add_import("/Script/Engine", "Texture2D", p, obj)


def finish_table(pkg, struct_index, rows):
    header = object_prop(pkg, "RowStruct", struct_index) + end_props(pkg) + struct.pack("<i", 0)
    body = struct.pack("<i", len(rows)) + b"".join(_fn(pkg, name) + data for name, data in rows)
    e = pkg.exports[0]
    e.data = header + body
    refs = [i for i in getattr(pkg, "_row_refs", []) if i != struct_index]   # collected by object_prop(), order = first occurrence
    e.deps_ser_before_ser = [struct_index]
    e.deps_create_before_ser = refs
    e.deps_ser_before_create = [pkg.find_import("Class", "DataTable"), pkg.find_import("DataTable", "Default__DataTable")]
    e.deps_create_before_create = []
    pkg.generations = [(1, len(pkg.names))]
    return pkg


def make_mod_table(package_dir, caption, desc, tables, version=1.0):
    pkg, s = new_datatable(package_dir + "/TKA_Mod_Table", "TKA_Mod_Table", STRUCTS["DLC_Struct"], "DLC_Struct")
    row = text_prop(pkg, T["Caption"], caption) + text_prop(pkg, T["Desc"], desc) + float_prop(pkg, T["Version"], version) \
        + name_array_prop(pkg, T["Tables"], tables) + end_props(pkg)
    return finish_table(pkg, s, [(package_dir.rsplit("/", 1)[1], row)])
