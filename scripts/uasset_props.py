#!/usr/bin/env python3
"""Minimal reader for cooked UE4.27 .uasset/.uexp pairs (tagged property format).

Usage:
  uasset_props.py <file.uasset> [export-name-regex]   -> JSON dump of export properties
  For DataTables the rows are decoded as well.
"""
import struct, sys, json, os, re

NATIVE_STRUCTS = {
    "Vector": ("<fff", ["x", "y", "z"]),
    "Vector2D": ("<ff", ["x", "y"]),
    "Vector4": ("<ffff", ["x", "y", "z", "w"]),
    "Rotator": ("<fff", ["pitch", "yaw", "roll"]),
    "Quat": ("<ffff", ["x", "y", "z", "w"]),
    "Color": ("<BBBB", ["b", "g", "r", "a"]),
    "LinearColor": ("<ffff", ["r", "g", "b", "a"]),
    "Guid": ("<IIII", ["a", "b", "c", "d"]),
    "IntPoint": ("<ii", ["x", "y"]),
    "Box2D": ("<ffffB", ["minx", "miny", "maxx", "maxy", "valid"]),
    "Transform": ("<ffff fff fff", ["qx", "qy", "qz", "qw", "tx", "ty", "tz", "sx", "sy", "sz"]),
    "DateTime": ("<q", ["ticks"]),
    "Timespan": ("<q", ["ticks"]),
    "SoftObjectPath": None,  # handled specially
    "SoftClassPath": None,
}


class Reader:
    def __init__(self, data, names, imports, exports):
        self.d = data
        self.p = 0
        self.names = names
        self.imports = imports
        self.exports = exports

    def u8(self):
        v = self.d[self.p]; self.p += 1; return v

    def i32(self):
        v = struct.unpack_from("<i", self.d, self.p)[0]; self.p += 4; return v

    def u32(self):
        v = struct.unpack_from("<I", self.d, self.p)[0]; self.p += 4; return v

    def i64(self):
        v = struct.unpack_from("<q", self.d, self.p)[0]; self.p += 8; return v

    def f32(self):
        v = struct.unpack_from("<f", self.d, self.p)[0]; self.p += 4; return v

    def fstr(self):
        l = self.i32()
        if l == 0:
            return ""
        if l < 0:
            s = self.d[self.p:self.p - 2 * l].decode("utf-16-le", errors="replace").rstrip("\0"); self.p += -2 * l
        else:
            s = self.d[self.p:self.p + l].decode("utf-8", errors="replace").rstrip("\0"); self.p += l
        return s

    def fname(self):
        i, num = struct.unpack_from("<ii", self.d, self.p); self.p += 8
        n = self.names[i] if 0 <= i < len(self.names) else "<bad:%d>" % i
        return n + ("_%d" % (num - 1) if num else "")

    def objref(self):
        i = self.i32()
        if i < 0:
            im = self.imports[-i - 1]
            return "import:" + im[3] + " (" + im[1] + ")"
        if i > 0:
            return "export:" + self.exports[i - 1][0]
        return None

    def ftext(self):
        flags = self.u32()
        ht = struct.unpack_from("<b", self.d, self.p)[0]; self.p += 1
        if ht == -1:
            has = self.i32()
            return self.fstr() if has else ""
        if ht == 0:
            ns = self.fstr(); key = self.fstr(); src = self.fstr()
            return {"text": src, "ns": ns, "key": key}
        if ht == 11:
            table = self.fname(); key = self.fstr()
            return {"stringtable": table, "key": key}
        return {"text_history_type": ht}

    # ---- tagged properties ----
    def tag(self):
        name = self.fname()
        if name == "None":
            return None
        typ = self.fname()
        size = self.i32()
        idx = self.i32()
        t = {"name": name, "type": typ, "size": size, "index": idx}
        if typ == "StructProperty":
            t["struct"] = self.fname(); self.p += 16
        elif typ == "BoolProperty":
            t["bool"] = bool(self.u8())
        elif typ in ("ByteProperty", "EnumProperty"):
            t["enum"] = self.fname()
        elif typ in ("ArrayProperty", "SetProperty"):
            t["inner"] = self.fname()
        elif typ == "MapProperty":
            t["key"] = self.fname(); t["value"] = self.fname()
        if self.u8():
            self.p += 16
        return t

    def value(self, typ, size, t=None):
        start = self.p
        try:
            if typ == "IntProperty": v = self.i32()
            elif typ == "UInt32Property": v = self.u32()
            elif typ == "Int64Property" or typ == "UInt64Property": v = self.i64()
            elif typ == "Int16Property" or typ == "UInt16Property": v = struct.unpack_from("<h", self.d, self.p)[0]; self.p += 2
            elif typ == "Int8Property": v = struct.unpack_from("<b", self.d, self.p)[0]; self.p += 1
            elif typ == "FloatProperty": v = self.f32()
            elif typ == "DoubleProperty": v = struct.unpack_from("<d", self.d, self.p)[0]; self.p += 8
            elif typ == "BoolProperty": v = t.get("bool") if t else bool(self.u8())
            elif typ == "NameProperty": v = self.fname()
            elif typ == "StrProperty": v = self.fstr()
            elif typ == "TextProperty": v = self.ftext()
            elif typ == "ObjectProperty" or typ == "ClassProperty" or typ == "InterfaceProperty": v = self.objref()
            elif typ in ("SoftObjectProperty", "SoftClassProperty", "AssetObjectProperty"):
                v = self.fname(); sub = self.fstr()
                if sub: v = v + ":" + sub
            elif typ == "EnumProperty": v = self.fname()
            elif typ == "ByteProperty":
                v = self.fname() if (t and t.get("enum") not in (None, "None")) else self.u8()
            elif typ == "StructProperty":
                v = self.struct_value(t.get("struct") if t else None, size)
            elif typ == "ArrayProperty" or typ == "SetProperty":
                v = self.array_value(t.get("inner"), size, typ == "SetProperty")
            elif typ == "MapProperty":
                v = self.map_value(t.get("key"), t.get("value"), size)
            elif typ == "MulticastInlineDelegateProperty" or typ == "MulticastSparseDelegateProperty" or typ == "DelegateProperty":
                v = "<delegate>"; self.p = start + size
            else:
                v = "<unhandled %s>" % typ; self.p = start + size
        except Exception as e:
            v = "<err %s: %s>" % (typ, e)
            self.p = start + size
        if size and self.p != start + size and typ not in ("BoolProperty",):
            # resync on size
            self.p = start + size
        return v

    def struct_value(self, sname, size):
        if sname in NATIVE_STRUCTS and NATIVE_STRUCTS[sname]:
            fmt, keys = NATIVE_STRUCTS[sname]
            vals = struct.unpack_from(fmt.replace(" ", ""), self.d, self.p); self.p += struct.calcsize(fmt.replace(" ", ""))
            return dict(zip(keys, vals))
        if sname in ("SoftObjectPath", "SoftClassPath"):
            v = self.fname(); sub = self.fstr()
            return v + (":" + sub if sub else "")
        return self.props()

    def array_value(self, inner, size, is_set=False):
        if is_set:
            self.i32()  # elements to remove
        n = self.i32()
        out = []
        if inner == "StructProperty":
            it = self.tag()  # inner tag with struct name
            sname = it.get("struct") if it else None
            for i in range(n):
                out.append(self.struct_value(sname, 0))
            return out
        if inner == "BoolProperty":
            return [bool(self.u8()) for _ in range(n)]
        if inner == "ByteProperty":
            # enum-bytes are stored as FName (8 bytes each) when size matches
            if size - 4 == n * 8:
                return [self.fname() for _ in range(n)]
            return [self.u8() for _ in range(n)]
        for i in range(n):
            out.append(self.value(inner, 0))
        return out

    def map_value(self, kt, vt, size):
        self.i32()  # remove count
        n = self.i32()
        out = []
        for i in range(n):
            k = self.value(kt, 0)
            v = self.value(vt, 0)
            out.append([k, v])
        return out

    def props(self):
        out = {}
        while True:
            t = self.tag()
            if t is None:
                return out
            v = self.value(t["type"], t["size"], t)
            key = t["name"] if t["index"] == 0 else "%s[%d]" % (t["name"], t["index"])
            out[key] = v


def read_summary(path):
    d = open(path, "rb").read()

    def rstr(pos):
        l = struct.unpack_from("<i", d, pos)[0]; pos += 4
        if l < 0:
            s = d[pos:pos - 2 * l].decode("utf-16-le").rstrip("\0"); pos += -2 * l
        else:
            s = d[pos:pos + l].decode("latin1").rstrip("\0"); pos += l
        return s, pos

    pos = 8
    legacy = struct.unpack_from("<i", d, 4)[0]
    if legacy != -4:
        pos += 4
    pos += 8
    n = struct.unpack_from("<i", d, pos)[0]; pos += 4 + n * 20
    total_hdr = struct.unpack_from("<i", d, pos)[0]; pos += 4
    folder, pos = rstr(pos)
    pos += 4
    name_count, name_off = struct.unpack_from("<ii", d, pos); pos += 8 + 8
    exp_count, exp_off, imp_count, imp_off = struct.unpack_from("<iiii", d, pos)
    names = []
    p = name_off
    for i in range(name_count):
        s, p = rstr(p); p += 4; names.append(s)

    def fname(p):
        i, num = struct.unpack_from("<ii", d, p)
        return names[i] + ("_%d" % (num - 1) if num else "")

    imps = []
    p = imp_off
    for i in range(imp_count):
        imps.append((fname(p), fname(p + 8), struct.unpack_from("<i", d, p + 16)[0], fname(p + 20))); p += 28
    exps = []
    p = exp_off
    for i in range(exp_count):
        cls, sup, tmpl, outer = struct.unpack_from("<iiii", d, p)
        on = fname(p + 16)
        ssz, soff = struct.unpack_from("<qq", d, p + 28)
        exps.append((on, cls, sup, outer, ssz, soff)); p += 104
    return d, names, imps, exps, total_hdr


def clsname(i, imps, exps):
    if i < 0: return imps[-i - 1][3]
    if i > 0: return exps[i - 1][0]
    return "-"


def dump(path, export_filter=None):
    d, names, imps, exps, total_hdr = read_summary(path)
    uexp = path[:-7] + ".uexp"
    if os.path.exists(uexp):
        data = d + open(uexp, "rb").read()
    else:
        data = d
    result = {}
    for (on, cls, sup, outer, ssz, soff) in exps:
        cn = clsname(cls, imps, exps)
        if export_filter and not re.search(export_filter, on):
            continue
        if cn in ("Function", "K2Node_Event") or ssz == 0:
            continue
        r = Reader(data, names, imps, exps)
        r.p = soff
        try:
            props = r.props()
            entry = {"class": cn, "props": props}
            if cn in ("DataTable", "CompositeDataTable"):
                rows = {}
                r.i32()  # bHasGuid flag (UObject::Serialize)
                nrows = r.i32()
                for i in range(nrows):
                    rn = r.fname()
                    rows[rn] = r.props()
                entry["rows"] = rows
            result[on] = entry
        except Exception as e:
            result[on] = {"class": cn, "error": str(e), "at": r.p - soff}
    return result


if __name__ == "__main__":
    res = dump(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(json.dumps(res, indent=1, ensure_ascii=False))
