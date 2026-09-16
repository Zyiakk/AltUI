#!/usr/bin/env python3
"""Dump Blueprint class API (functions + signatures + class variables) from a cooked UE4.27 asset.

Usage: uasset_funcs.py <file.uasset> [--json]
"""
import struct, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uasset_props import read_summary, Reader, clsname

CPF_Parm = 0x80
CPF_OutParm = 0x100
CPF_ReturnParm = 0x400
CPF_ReferenceParm = 0x8000000
CPF_ConstParm = 0x2
CPF_BlueprintVisible = 0x4
CPF_BlueprintReadOnly = 0x10
CPF_Edit = 0x1
CPF_ExposeOnSpawn = 0x1000000000000

FUNC_Final = 0x1
FUNC_BlueprintCallable = 0x4000000
FUNC_BlueprintEvent = 0x8000000
FUNC_BlueprintPure = 0x10000000
FUNC_Static = 0x2000
FUNC_Public = 0x20000
FUNC_Protected = 0x40000
FUNC_Private = 0x80000
FUNC_Delegate = 0x100000
FUNC_Event = 0x800
FUNC_UbergraphFunction = 0x800000
FUNC_Const = 0x100000000 if False else 0x100000000  # (not in 4.27 uint32 flags)


class FieldReader(Reader):
    def obj(self):
        return self.objref()

    def field(self):
        """Serialize one FField (as in FField::SerializeSingleField)."""
        ftype = self.fname()
        if ftype == "None":
            return None
        name = self.fname()
        flags = self.u32()
        f = {"type": ftype, "name": name}
        if ftype.endswith("Property"):
            f["arraydim"] = self.i32()
            f["elemsize"] = self.i32()
            f["pflags"] = struct.unpack_from("<Q", self.d, self.p)[0]; self.p += 8
            f["repindex"] = struct.unpack_from("<H", self.d, self.p)[0]; self.p += 2
            f["repnotify"] = self.fname()
            f["repcond"] = self.u8()
            t = ftype
            if t in ("ObjectProperty", "WeakObjectProperty", "LazyObjectProperty", "SoftObjectProperty", "InterfaceProperty"):
                f["class"] = self.obj()
            elif t in ("ClassProperty", "SoftClassProperty"):
                f["class"] = self.obj(); f["metaclass"] = self.obj()
            elif t == "StructProperty":
                f["struct"] = self.obj()
            elif t in ("ArrayProperty", "SetProperty"):
                f["inner"] = self.field()
            elif t == "MapProperty":
                f["key"] = self.field(); f["value"] = self.field()
            elif t == "EnumProperty":
                f["enum"] = self.obj(); f["underlying"] = self.field()
            elif t == "ByteProperty":
                f["enum"] = self.obj()
            elif t == "BoolProperty":
                self.p += 4  # FieldSize, ByteOffset, ByteMask, FieldMask
                f["boolsize"] = self.u8()
                f["native"] = self.u8()
            elif t in ("DelegateProperty", "MulticastDelegateProperty", "MulticastInlineDelegateProperty", "MulticastSparseDelegateProperty"):
                f["signature"] = self.obj()
            elif t in ("IntProperty", "FloatProperty", "NameProperty", "StrProperty", "TextProperty", "Int64Property",
                       "UInt32Property", "UInt64Property", "Int16Property", "UInt16Property", "Int8Property", "DoubleProperty"):
                pass
            elif t == "FieldPathProperty":
                f["fieldclass"] = self.fname()
            else:
                raise Exception("unknown property type " + t)
        return f


def typestr(f):
    if f is None:
        return "?"
    t = f["type"]
    base = {"IntProperty": "int", "FloatProperty": "float", "BoolProperty": "bool", "NameProperty": "Name",
            "StrProperty": "String", "TextProperty": "Text", "Int64Property": "int64", "DoubleProperty": "double",
            "ByteProperty": "byte", "UInt32Property": "uint32"}.get(t)
    if t == "ObjectProperty" or t == "InterfaceProperty":
        return (f.get("class") or "Object").replace("import:", "").split(" (")[0]
    if t == "SoftObjectProperty":
        return "Soft<" + (f.get("class") or "Object").replace("import:", "").split(" (")[0] + ">"
    if t == "ClassProperty":
        return "Class<" + (f.get("metaclass") or "Object").replace("import:", "").split(" (")[0] + ">"
    if t == "SoftClassProperty":
        return "SoftClass<" + (f.get("metaclass") or "Object").replace("import:", "").split(" (")[0] + ">"
    if t == "StructProperty":
        return (f.get("struct") or "Struct").replace("import:", "").split(" (")[0]
    if t == "EnumProperty":
        return (f.get("enum") or "Enum").replace("import:", "").split(" (")[0]
    if t == "ByteProperty" and f.get("enum"):
        return (f.get("enum") or "byte").replace("import:", "").split(" (")[0]
    if t == "ArrayProperty":
        return "Array<" + typestr(f.get("inner")) + ">"
    if t == "SetProperty":
        return "Set<" + typestr(f.get("inner")) + ">"
    if t == "MapProperty":
        return "Map<" + typestr(f.get("key")) + "," + typestr(f.get("value")) + ">"
    if t in ("DelegateProperty", "MulticastInlineDelegateProperty", "MulticastSparseDelegateProperty"):
        return "Delegate<" + (f.get("signature") or "?").replace("export:", "").replace("import:", "") + ">"
    return base or t


def parse_struct_export(data, names, imps, exps, soff, is_function, is_class=False):
    r = FieldReader(data, names, imps, exps)
    r.p = soff
    props = r.props()  # UObject tagged props (usually empty)
    r.i32()  # guid flag
    # (UField::Next is no longer serialized since FFrameworkObjectVersion::RemoveUField_Next)
    # UStruct
    sup = r.obj()
    nchildren = r.i32()
    children = [r.obj() for _ in range(nchildren)]
    nfields = r.i32()
    fields = []
    for i in range(nfields):
        fields.append(r.field())
    bytecode_size = r.i32()
    script_size = r.i32()
    r.p += script_size
    out = {"super": sup, "children": children, "fields": fields, "bytecode": bytecode_size}
    if is_function:
        fflags = r.u32()
        out["flags"] = fflags
        if fflags & 0x40:  # FUNC_Net
            r.p += 2
        out["eventgraph"] = r.fname()
        out["eventgraph_off"] = r.i32()
    return out


def dump(path):
    d, names, imps, exps, th = read_summary(path)
    uexp = path[:-7] + ".uexp"
    data = d + (open(uexp, "rb").read() if os.path.exists(uexp) else b"")
    result = {"functions": {}, "class": None, "delegates": {}}
    for (on, cls, sup, outer, ssz, soff) in exps:
        cn = clsname(cls, imps, exps)
        try:
            if cn == "Function":
                fn = parse_struct_export(data, names, imps, exps, soff, True)
                params = [f for f in fn["fields"] if f and f.get("pflags", 0) & CPF_Parm]
                locals_ = [f for f in fn["fields"] if f and not (f.get("pflags", 0) & CPF_Parm)]
                sig = []
                ret = None
                for p in params:
                    pf = p["pflags"]
                    if pf & CPF_ReturnParm:
                        ret = typestr(p); continue
                    mod = ""
                    if pf & CPF_OutParm and not (pf & CPF_ConstParm):
                        mod = "out " if not (pf & CPF_ReferenceParm) else "ref "
                    elif pf & CPF_ReferenceParm:
                        mod = "const& "
                    sig.append(mod + p["name"] + ": " + typestr(p))
                fl = fn["flags"]
                kind = []
                if fl & FUNC_BlueprintPure: kind.append("pure")
                if fl & FUNC_BlueprintCallable: kind.append("callable")
                if fl & FUNC_BlueprintEvent: kind.append("event")
                if fl & FUNC_Static: kind.append("static")
                if fl & FUNC_Delegate: kind.append("delegate")
                if fl & FUNC_Private: kind.append("private")
                if fl & FUNC_Protected: kind.append("protected")
                if fl & FUNC_UbergraphFunction: kind.append("ubergraph")
                result["functions"][on] = {"outer": clsname(outer, imps, exps), "params": sig, "ret": ret,
                                           "kind": kind, "locals": len(locals_), "flags": hex(fl),
                                           "bytecode": fn["bytecode"], "super": fn["super"]}
            elif cn == "BlueprintGeneratedClass" or cn == "WidgetBlueprintGeneratedClass" or cn == "AnimBlueprintGeneratedClass":
                c = parse_struct_export(data, names, imps, exps, soff, False, True)
                vars_ = []
                for f in c["fields"]:
                    if not f: continue
                    pf = f.get("pflags", 0)
                    vis = []
                    if pf & CPF_Edit: vis.append("edit")
                    if pf & CPF_BlueprintVisible: vis.append("bpvisible")
                    if pf & CPF_BlueprintReadOnly: vis.append("readonly")
                    if pf & CPF_ExposeOnSpawn: vis.append("exposeonspawn")
                    vars_.append({"name": f["name"], "type": typestr(f), "vis": vis, "pflags": hex(pf)})
                result["class"] = {"name": on, "super": c["super"], "vars": vars_, "children": c["children"]}
        except Exception as e:
            result.setdefault("errors", {})[on] = str(e)
    return result


def fmt(result):
    lines = []
    c = result.get("class")
    if c:
        lines.append("CLASS %s : %s" % (c["name"], c["super"]))
        for v in c["vars"]:
            lines.append("  var %-45s %-50s %s" % (v["name"], v["type"], ",".join(v["vis"])))
    lines.append("FUNCTIONS (%d)" % len(result["functions"]))
    for n, f in result["functions"].items():
        if n.startswith("ExecuteUbergraph") or n.startswith("InpActEvt_") or n.startswith("InpAxisEvt_") or n.startswith("BndEvt__"):
            continue
        r = (" -> " + f["ret"]) if f["ret"] else ""
        lines.append("  %-50s (%s)%s   [%s]" % (n, ", ".join(f["params"]), r, ",".join(f["kind"])))
    for n, e in result.get("errors", {}).items():
        lines.append("  ERROR %s: %s" % (n, e))
    return "\n".join(lines)


if __name__ == "__main__":
    res = dump(sys.argv[1])
    if "--json" in sys.argv:
        print(json.dumps(res, indent=1))
    else:
        print(fmt(res))
