import sys, os, struct, glob; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


# storysave.Parse Save Worn: Save Player Clothes out of the ByteData of a story save's Player Save Data (tagged properties).
# Built here the way UE writes them (docs/notes/2026-10-24-laden-story-stand.md); a real story save of the user is read too if present.
def fstr(s):
    try:
        b = s.encode("ascii") + b"\0"; return struct.pack("<i", len(b)) + b
    except UnicodeEncodeError:
        b = s.encode("utf-16-le") + b"\0\0"; return struct.pack("<i", -(len(b) // 2)) + b


def name_array(prop, names):
    body = struct.pack("<i", len(names)) + b"".join(fstr(n) for n in names)
    return fstr(prop) + fstr("ArrayProperty") + struct.pack("<q", len(body)) + fstr("NameProperty") + b"\0" + body


def bool_prop(prop):
    return fstr(prop) + fstr("BoolProperty") + struct.pack("<q", 0) + b"\0\0"


def player_bytes(worn, before=b"", after=b""):
    return before + bool_prop("Wanna Shower") + name_array("Shortcuts", ["Knife", "None"]) + (name_array("Save Player Clothes", worn) if worn is not None else b"") + after + fstr("None")


def real_save_bytes():
    """ByteData of Player Save Data in the newest Level_*.sav of the game, or None."""
    d = os.path.expandvars("$GAME_SAVES") if os.environ.get("GAME_SAVES") else None
    if not d: return None
    files = sorted(glob.glob(os.path.join(d, "Level_*_*.sav")), key=os.path.getmtime)
    for f in reversed(files):
        data = open(f, "rb").read(); i = data.find(b"Player Save Data")
        j = data.find(b"ByteData", i) if i >= 0 else -1
        if j < 0: continue
        p = j + 9 + 4 + 14 + 8 + 4 + 13 + 1   # name, "ArrayProperty", size, "ByteProperty", guid flag
        n = struct.unpack_from("<i", data, p)[0]
        return data[p + 4:p + 4 + n], os.path.basename(f)
    return None


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")

    def parse(b):
        mgr.set_editor_property("SaveBytes", list(b))
        mgr.call_method("Test Parse Save Worn"); ok = mgr.get_editor_property("TmpBool")
        return ok, [str(n) for n in mgr.get_editor_property("TmpNames3")], len(mgr.get_editor_property("SaveBytes"))

    worn = ["NikAirWhite", "BomberLatex", "BunnySuit_Fishnet", "Skirt01_1", "AltUI#x#0"]
    ok, names, left = parse(player_bytes(worn))
    expect("list read", (ok, names), (True, worn)); expect("bytes freed", left, 0)
    # a name before the property that looks like it (same length byte and first letter) must not confuse the search
    ok, names, _ = parse(player_bytes(["Bra01"], before=name_array("Save Player Clothez", ["Wrong"])))
    expect("near miss skipped", (ok, names), (True, ["Bra01"]))
    expect("nothing worn: property absent", parse(player_bytes(None))[0], False)
    expect("empty array", parse(player_bytes([]))[:2], (True, []))
    # a UTF-16 name is skipped, the ones after it are still read
    ok, names, _ = parse(player_bytes(["A1", "旗袍", "B2"]))
    expect("utf16 skipped", (ok, names), (True, ["A1", "B2"]))
    # wrong layout (an int instead of names) -> not trusted
    bad = fstr("Save Player Clothes") + fstr("IntProperty") + struct.pack("<q", 4) + b"\0" + struct.pack("<i", 7)
    expect("wrong layout", parse(bad + fstr("None"))[0], False)
    # truncated in the middle of a name: that name is dropped, nothing reads past the end
    t = player_bytes(["Long_Name_Here"]); ok, names, _ = parse(t[:t.find(b"Long_Name") + 4])
    expect("truncated", names, [])
    r = real_save_bytes()
    if r:
        b, f = r; ok, names, _ = parse(b)
        report("real save %s: %s" % (f, names), ok and len(names) > 0)


run(main)
