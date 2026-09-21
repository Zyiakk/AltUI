#!/usr/bin/env python3
"""GVAS SaveGame files (UE 4.27 `Saved/SaveGames/*.sav`): header + tagged properties until "None".

Interpreted: IntProperty, StrProperty, NameProperty, BoolProperty, MapProperty<Name, Str>. Every other property is kept as a raw block
(type header + data) so a file that is loaded and saved unchanged stays byte-identical. Strings are FString (int32 length, UTF-8 with
terminating NUL; negative length = UTF-16LE)."""
import struct

MAGIC = b"GVAS"
NAMES_CLASS = "/Game/Mod/AltUI/SG_Names.SG_Names_C"
# header of a save written by the game (SaveGameFileVersion 2, PackageFileUE4Version 522, engine 4.27.2, no custom versions needed for our classes)
NAMES_HEADER = MAGIC + struct.pack("<ii", 2, 522) + struct.pack("<HHHI", 4, 27, 2, 18319896)


def _fstr(d, p):
    n = struct.unpack_from("<i", d, p)[0]; p += 4
    if n == 0:
        return "", p
    if n < 0:
        return d[p:p - 2 * n].decode("utf-16-le")[:-1], p - 2 * n
    return d[p:p + n].decode("utf-8")[:-1], p + n


def _pack_fstr(s):
    if s == "":
        return struct.pack("<i", 0)
    try:
        b = s.encode("ascii") + b"\0"; return struct.pack("<i", len(b)) + b
    except UnicodeEncodeError:
        b = s.encode("utf-16-le") + b"\0\0"; return struct.pack("<i", -(len(b) // 2)) + b


class Prop:
    def __init__(self, name, ptype, raw_header, data):
        self.name, self.type, self.raw_header, self.data = name, ptype, raw_header, data   # raw_header: bytes after the size (map key/value types, struct name+guid, guid flag)

    def __repr__(self):
        return "Prop(%s %s)" % (self.name, self.type)


class SaveGame:
    def __init__(self, header, class_name, props):
        self.header, self.class_name, self.props = header, class_name, props

    def find(self, name):
        for p in self.props:
            if p.name == name:
                return p
        return None

    def get(self, name, default=None):
        p = self.find(name); return default if p is None else p.data

    def set_int(self, name, value):
        p = self.find(name)
        if p is None:
            self.props.insert(0, Prop(name, "IntProperty", b"\0", int(value)))
        else:
            p.data = int(value)

    def set_map(self, name, mapping):
        p = self.find(name)
        if p is None:
            self.props.append(Prop(name, "MapProperty", _pack_fstr("NameProperty") + _pack_fstr("StrProperty") + b"\0", dict(mapping)))
        else:
            p.data = dict(mapping)


def _read_props(d, p):
    props = []
    while True:
        name, p = _fstr(d, p)
        if name == "None":
            return props, p
        ptype, p = _fstr(d, p); size = struct.unpack_from("<q", d, p)[0]; p += 8
        h0 = p
        if ptype == "MapProperty":
            kt, p = _fstr(d, p); vt, p = _fstr(d, p); p += 1   # guid flag
            hdr = d[h0:p]; body = d[p:p + size]; p += size
            if (kt, vt) == ("NameProperty", "StrProperty"):
                q = 8; n = struct.unpack_from("<i", body, 4)[0]; m = {}   # int32 NumKeysToRemove (0), int32 Num
                for _ in range(n):
                    k, q = _fstr(body, q); v, q = _fstr(body, q); m[k] = v
                props.append(Prop(name, ptype, hdr, m))
            else:
                props.append(Prop(name, ptype, hdr, body))
        elif ptype == "BoolProperty":
            val = d[p]; p += 1; p += 1   # value byte, guid flag; size is 0
            props.append(Prop(name, ptype, b"", bool(val)))
        else:
            if ptype in ("ArrayProperty", "SetProperty"):
                _, p = _fstr(d, p)
            elif ptype == "StructProperty":
                _, p = _fstr(d, p); p += 16
            elif ptype in ("ByteProperty", "EnumProperty"):
                _, p = _fstr(d, p)
            p += 1   # guid flag
            hdr = d[h0:p]; body = d[p:p + size]; p += size
            if ptype == "IntProperty":
                props.append(Prop(name, ptype, hdr, struct.unpack("<i", body)[0]))
            elif ptype in ("StrProperty", "NameProperty"):
                props.append(Prop(name, ptype, hdr, _fstr(body, 0)[0]))
            else:
                props.append(Prop(name, ptype, hdr, body))


def _write_prop(p):
    if p.type == "BoolProperty":
        return _pack_fstr(p.name) + _pack_fstr(p.type) + struct.pack("<q", 0) + bytes([1 if p.data else 0]) + b"\0"
    if p.type == "IntProperty":
        body = struct.pack("<i", p.data)
    elif p.type in ("StrProperty", "NameProperty"):
        body = _pack_fstr(p.data)
    elif p.type == "MapProperty" and isinstance(p.data, dict):
        body = struct.pack("<ii", 0, len(p.data)) + b"".join(_pack_fstr(k) + _pack_fstr(v) for k, v in p.data.items())
    else:
        body = p.data
    return _pack_fstr(p.name) + _pack_fstr(p.type) + struct.pack("<q", len(body)) + p.raw_header + body


def loads(d):
    if d[:4] != MAGIC:
        raise ValueError("not a GVAS save game")
    p = 4 + 8 + 10
    _, p = _fstr(d, p)   # engine branch
    p += 4; n = struct.unpack_from("<i", d, p)[0]; p += 4 + 20 * n   # custom version format + versions
    cls, p = _fstr(d, p)
    header = d[:p]
    props, p = _read_props(d, p)
    return SaveGame(header, cls, props)


def dumps(sg):
    return sg.header + b"".join(_write_prop(p) for p in sg.props) + _pack_fstr("None") + b"\0\0\0\0"


def load(path):
    return loads(open(path, "rb").read())


def save(sg, path):
    open(path, "wb").write(dumps(sg))


def new_names_save():
    """Empty SG_Names save (SaveVersion 1, Names {}), header like the game's own files (branch string, custom version format 3, none listed)."""
    header = NAMES_HEADER + _pack_fstr("++UE4+Release-4.27") + struct.pack("<ii", 3, 0) + _pack_fstr(NAMES_CLASS)
    sg = SaveGame(header, NAMES_CLASS, [])
    sg.set_int("SaveVersion", 1); sg.set_map("Names", {})
    return sg
