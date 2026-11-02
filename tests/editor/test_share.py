import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
import json as _j
import unreal
from edtest_lib import *
import share_format as sf
M = "/Game/Mod/AltUI"


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    src = '{"a":[1,-2.5e1,true,false,null],"b":"x\\"y\\\\z\\n"}'
    mgr.call_method("Test Share Tokenize", args=(src,))
    expect("tokenize ok", mgr.get_editor_property("TmpBool"), True)
    expect("token kinds", list(mgr.get_editor_property("ShTokK")), [1, 7, 5, 3, 8, 6, 8, 6, 9, 6, 10, 6, 11, 4, 6, 7, 5, 7, 2])
    expect("string with escapes", str(mgr.get_editor_property("ShTokS")[17]), 'x"y\\z\n')
    expect("number", round(mgr.get_editor_property("ShTokN")[6], 3), -25.0)
    mgr.call_method("Test Share Tokenize", args=('{"a":tru}',)); expect("bad word", mgr.get_editor_property("TmpBool"), False)
    mgr.call_method("Test Share Tokenize", args=('{"a":"x',)); expect("open string", mgr.get_editor_property("TmpBool"), False)
    # timing: 50 looks (spec: at most 0.5 s for the whole read; the tokenizer gets 0.25 s of it)
    doc = sf.encode({"altui": sf.FORMAT, "version": sf.VERSION, "entries": [sf.sample_look(i) for i in range(50)], "mods": {}})
    mgr.call_method("Test Share Tokenize", args=(doc,))
    t = mgr.get_editor_property("TmpFloat"); unreal.log_warning("EDTEST info tokenize %d chars: %.3f s, %d tokens" % (len(doc), t, len(mgr.get_editor_property("ShTokK"))))
    expect("tokenize 50 looks ok", mgr.get_editor_property("TmpBool"), True)
    expect("tokenize 50 looks under 0.25 s", t < 0.25, True)

    # primitives: scalars, a skipped nested value, colours
    mgr.call_method("Test Share Primitives", args=('[1.5,"a",true,[1,{"x":[2,3]}],[0.5,0.25,0,1],[255,128,0,300]]',))
    expect("primitives", str(mgr.get_editor_property("TmpStr")), "1.5|a|true|skip|0.5,0.25,0.0,1.0|255,128,0,255|ok")   # Conv_FloatToString writes the shortest form
    mgr.call_method("Test Share Esc", args=('a"b\\c\nd',)); expect("esc", str(mgr.get_editor_property("TmpStr")), '"a\\"b\\\\c\\nd"')

    # schema round trips (unknown field skipped; numbers compared as numbers)
    def norm(x): return round(x, 4) if isinstance(x, float) else ({k: norm(v) for k, v in x.items()} if isinstance(x, dict) else ([norm(v) for v in x] if isinstance(x, list) else x))
    look = sf.sample_look(7)["data"]; look["Extra"] = {"x": [1, 2, {"y": "z"}]}
    mgr.call_method("Test Share Snap Roundtrip", args=(sf.encode(look),)); del look["Extra"]
    out = str(mgr.get_editor_property("TmpStr"))
    try: back = _j.loads(out)
    except Exception: back = {"unparsable": out[:200]}
    expect("snap roundtrip", norm(back), norm(_j.loads(sf.encode(look))))
    of = {"Pieces": {"A": [255, 0, 10, 255], "B": [1, 2, 3, 4]}, "SlotColors": {"A#0": [0.5, 0.5, 0.5, 1.0]}}
    mgr.call_method("Test Share Outfit Roundtrip", args=(sf.encode(of),)); out = str(mgr.get_editor_property("TmpStr"))
    try: back = _j.loads(out)
    except Exception: back = {"unparsable": out[:200]}
    expect("outfit roundtrip", norm(back), norm(of))
    # a look as shared: slot / make-up colours only of its own pieces and rows (the save's colour history stays at home)
    lk = sf.sample_look(4)["data"]; worn = lk["Worn"][0]
    lk.update({"Makeup": {"Eyebrow": {"List": ["Eyebrow_01"]}, "Lips": {"List": ["Lips_2"]}},
               "SlotColors": {worn + "#0": [1.0, 0.0, 0.0, 1.0], worn + "#2": [0.0, 1.0, 0.0, 1.0], "NotWorn#0": [0.0, 0.0, 0.0, 1.0], "NoSlot": [0.5, 0.5, 0.5, 1.0]},
               "MakeupColors": {"Lips_2": [0.1, 0.0, 0.0, 1.0], "Lips_3": [0.0, 0.0, 0.0, 1.0], "Blacklips": [1.0, 1.0, 1.0, 1.0]}})
    mgr.call_method("Test Share Look Snap", args=(sf.encode(lk),)); out = str(mgr.get_editor_property("TmpStr"))
    try: back = _j.loads(out)
    except Exception: back = {"unparsable": out[:200]}
    expect("shared look: slot colours of worn pieces", sorted(back.get("SlotColors", {})), sorted([worn + "#0", worn + "#2"]))
    expect("shared look: make-up colours of its rows", sorted(back.get("MakeupColors", {})), ["Lips_2"])
    expect("shared look: rest unchanged", norm({k: v for k, v in back.items() if k not in ("SlotColors", "MakeupColors")}),
           norm({k: v for k, v in lk.items() if k not in ("SlotColors", "MakeupColors")}))

    # applying a look merges its colours into the save's (other pieces and make-up rows keep theirs); undo replaces
    def lin(r, g_, b): return unreal.LinearColor(r, g_, b, 1.0)
    def keys(prop): return sorted(str(k) for k in mgr.get_editor_property(prop).keys())
    def red(prop, k): return round([v for kk, v in mgr.get_editor_property(prop).items() if str(kk) == k][0].r, 3)
    lk = sf.sample_look(5)["data"]
    lk.update({"Worn": ["Jacket", "Kept"], "Makeup": {"Lips": {"List": ["Lips_2"]}}, "SlotColors": {"Jacket#0": [0.9, 0.0, 0.0, 1.0], "Kept#0": [0.9, 0.0, 0.0, 1.0], "Other#0": [0.9, 0.0, 0.0, 1.0]},
               "MakeupColors": {"Lips_2": [0.9, 0.0, 0.0, 1.0], "Lips_3": [0.9, 0.0, 0.0, 1.0]}})
    def setup():
        mgr.set_editor_property("SlotColors", {"Jacket#0": lin(0.1, 0, 0), "Jacket#1": lin(0.1, 0, 0), "Kept#0": lin(0.1, 0, 0), "Shirt#0": lin(0.1, 0, 0), "Other#0": lin(0.1, 0, 0)})
        mgr.set_editor_property("MakeupColors", {"Lips_2": lin(0.1, 0, 0), "Eye_1": lin(0.1, 0, 0)}); mgr.set_editor_property("KeptOn", ["Kept"])
    setup(); mgr.call_method("Test Look Colors", args=(sf.encode(lk), True))
    expect("merge: slot keys", keys("LcSlot"), ["Jacket#0", "Kept#0", "Other#0", "Shirt#0"])   # Jacket#1 dropped (the look has none for it)
    expect("merge: look's piece takes its colour, kept / other pieces keep theirs", [red("LcSlot", k) for k in ("Jacket#0", "Kept#0", "Other#0", "Shirt#0")], [0.9, 0.1, 0.1, 0.1])
    expect("merge: make-up", (keys("LcMk"), red("LcMk", "Lips_2"), red("LcMk", "Eye_1")), (["Eye_1", "Lips_2"], 0.9, 0.1))
    setup(); mgr.call_method("Test Look Colors", args=(sf.encode(lk), False))
    expect("replace: the snapshot's map plus kept", (keys("LcSlot"), red("LcSlot", "Kept#0")), (["Jacket#0", "Kept#0", "Other#0"], 0.1))
    expect("replace: make-up as in the snapshot", keys("LcMk"), ["Lips_2", "Lips_3"])
    mgr.set_editor_property("KeptOn", []); mgr.set_editor_property("SlotColors", {}); mgr.set_editor_property("MakeupColors", {})

    # export of a look and an outfit made here, read back by Python and by AltUI
    mgr.call_method("Test Load Settings"); mgr.set_editor_property("LooksSave", None); mgr.call_method("Test Load Looks"); mgr.call_method("Test Add Look")
    mgr.call_method("Test Load Outfits"); mgr.call_method("Test Add Outfit", args=(["SharePieceA", "SharePieceB"],))
    mgr.call_method("Test Share Export Last"); text = str(mgr.get_editor_property("TmpStr"))
    try: doc = _j.loads(text)
    except Exception: doc = {"unparsable": text[:300]}
    expect("export header", (doc.get("altui"), doc.get("version")), ("share", 1))
    expect("ref types lower case", sorted({r["type"] for e in doc.get("entries", []) for r in e.get("refs", [])} - {"clothes", "hair", "skin", "makeup", "body", "modentry"}), [])
    expect("export kinds", [e["kind"] for e in doc.get("entries", [])], ["look", "outfit"])
    expect("export look fields", sorted(doc["entries"][0]["data"]) if doc.get("entries") else [], sorted(n for n, _ in sf.SNAP_SCHEMA))
    expect("export outfit pieces", sorted(doc["entries"][1]["data"]["Pieces"]) if doc.get("entries") else [], ["SharePieceA", "SharePieceB"])
    mgr.call_method("Test Share Parse", args=(text,)); expect("parse ok", mgr.get_editor_property("TmpBool"), True); expect("parsed looks", mgr.get_editor_property("TmpI"), 1)
    expect("parsed outfits", len(mgr.get_editor_property("ShOutfits")), 1)
    bad = sf.encode({"altui": "other", "version": 1, "entries": []}); mgr.call_method("Test Share Parse", args=(bad,))
    expect("foreign format", (mgr.get_editor_property("TmpBool"), str(mgr.get_editor_property("ShErr"))), (False, "Share_ErrFormat"))
    newer = sf.encode({"altui": "share", "version": 2, "entries": []}); mgr.call_method("Test Share Parse", args=(newer,))
    expect("newer version", str(mgr.get_editor_property("ShErr")), "Share_ErrVersion")
    unk = sf.encode({"entries": [{"data": {"a": [1]}, "kind": "future", "name": "x"}], "altui": "share", "version": 1}); mgr.call_method("Test Share Parse", args=(unk,))
    expect("unknown kind counted, keys in any order", (mgr.get_editor_property("TmpBool"), mgr.get_editor_property("ShUnknown")), (True, 1))
    lk = sf.sample_look(3); lk = {"refs": lk["refs"], "data": lk["data"], "name": lk["name"], "kind": "look"}   # data and refs before kind / name
    mgr.call_method("Test Share Parse", args=(sf.encode({"altui": "share", "version": 1, "entries": [lk], "mods": {"Mod_0": "Mod Zero"}}),))
    expect("data before kind", (mgr.get_editor_property("TmpBool"), mgr.get_editor_property("TmpI"), len(mgr.get_editor_property("ShRefs"))), (True, 1, 12))
    # 50 looks: tokenize + read under 0.5 s
    big = sf.encode({"altui": sf.FORMAT, "version": sf.VERSION, "entries": [sf.sample_look(i) for i in range(50)], "mods": {}})
    mgr.call_method("Test Share Parse Timed", args=(big,)); t = mgr.get_editor_property("TmpFloat")
    unreal.log_warning("EDTEST info parse 50 looks: %.3f s" % t); expect("parse 50 looks", (mgr.get_editor_property("TmpBool"), mgr.get_editor_property("TmpI")), (True, 50))
    expect("parse 50 looks under 0.5 s", t < 0.5, True)

    # check / import with a mod that is not installed
    mgr.call_method("Test Build"); mgr.call_method("Test Strings", args=(1,))
    mgr.call_method("Test Share Real Item"); real = str(mgr.get_editor_property("TmpName"))
    lk = sf.sample_look(1); d = lk["data"]
    d.update({"Worn": [real, "NoSuchPiece"], "Colors": {real: [1.0, 0.0, 0.0, 1.0], "NoSuchPiece": [0.0, 1.0, 0.0, 1.0]}, "Hair": "None", "Skin": "None", "Body": "None", "Makeup": {}, "SlotColors": {}})
    lk["refs"] = [{"type": "clothes", "item": "NoSuchPiece", "label": "Ghost skirt", "mod": "NoSuchMod"}]
    doc = sf.encode({"altui": "share", "version": 1, "entries": [lk], "mods": {"NoSuchMod": "Ghost Mod"}})
    mgr.call_method("Test Share Check", args=(doc,))
    summary = str(mgr.get_editor_property("TmpStr")); unreal.log_warning("EDTEST info summary: %r" % summary)
    expect("missing counted", mgr.get_editor_property("TmpI"), 1)
    expect("summary names mod, piece, entry", all(x in summary for x in ("Ghost Mod", "NoSuchMod", "Ghost skirt", lk["name"])), True)
    mgr.call_method("Test Share Import", args=(doc, True)); expect("clean import: one piece left", [str(x) for x in mgr.get_editor_property("TmpNames")], [real])
    mgr.call_method("Test Share Import", args=(doc, False)); expect("full import keeps it", [str(x) for x in mgr.get_editor_property("TmpNames")], [real, "NoSuchPiece"])
    ok = sf.encode({"altui": "share", "version": 1, "entries": [], "mods": {}}); mgr.call_method("Test Share Check", args=(ok,))
    expect("empty document: nothing new", (mgr.get_editor_property("TmpI"), "Nothing new to import." in str(mgr.get_editor_property("TmpStr"))), (0, True))
    # a piece without a reference (the sender could not tell its mod) that is not installed here: missing, from an unknown mod
    nr = sf.encode({"altui": "share", "version": 1, "entries": [{"kind": "outfit", "name": "From afar", "data": {"Pieces": {"NoRefPiece": [1, 2, 3, 255]}, "SlotColors": {}}}], "mods": {}})
    mgr.call_method("Test Share Check", args=(nr,)); summary = str(mgr.get_editor_property("TmpStr")); unreal.log_warning("EDTEST info summary noref: %r" % summary)
    expect("piece without ref: missing", (mgr.get_editor_property("TmpI"), "AltUI could not name" in summary, "NoRefPiece" in summary, "From afar" in summary), (1, True, True, True))
    # a reference typed "Clothes" (an FName in the game keeps its first spelling - Gonnor's outfit 2026-11-01): still checked
    cap = sf.encode({"altui": "share", "version": 1, "entries": [{"kind": "outfit", "name": "Gonnor", "data": {"Pieces": {"CapPiece": [1, 2, 3, 255]}, "SlotColors": {}},
                     "refs": [{"type": "Clothes", "item": "CapPiece", "label": "CapPiece", "mod": "CapMod"}]}], "mods": {"CapMod": "Cap Mod"}})
    mgr.call_method("Test Share Check", args=(cap,)); summary = str(mgr.get_editor_property("TmpStr"))
    expect("type 'Clothes': missing", (mgr.get_editor_property("TmpI"), "Cap Mod" in summary), (1, True))
    # entries saved here exactly so are not imported again (play test 2026-11-01); one changed value makes it new
    mgr.call_method("Test Share Check", args=(text,)); summary = str(mgr.get_editor_property("TmpStr")); unreal.log_warning("EDTEST info summary dup: %r" % summary)
    expect("already here: dropped", [len(mgr.get_editor_property(v)) for v in ("ShLooks", "ShOutfits")], [0, 0])
    expect("already here: said so", ("Already saved here exactly" in summary, "Nothing new to import." in summary, ", )" in summary), (True, True, False))
    changed = _j.loads(text); changed["entries"][0]["data"]["Oil"] = changed["entries"][0]["data"].get("Oil", 0) + 0.5
    mgr.call_method("Test Share Check", args=(_j.dumps(changed),)); summary = str(mgr.get_editor_property("TmpStr"))
    expect("changed look is new, outfit still here", [len(mgr.get_editor_property(v)) for v in ("ShLooks", "ShOutfits")], [1, 0])
    # the name counts: a deleted "Face 12" comes back although "Smile" has the same values (play test 2026-11-01)
    renamed = _j.loads(text); renamed["entries"][0]["name"] = "Same data, other name"
    mgr.call_method("Test Share Check", args=(_j.dumps(renamed),))
    expect("same data, other name: new", [len(mgr.get_editor_property(v)) for v in ("ShLooks", "ShOutfits")], [1, 0])
    expect("left: mods line", "Every mod it needs is installed." in summary, True)

    # part 2 schemas: round trips
    samples = {"Face": {"Values": {"Face_Smile": 0.5, "Mouth_EE": -0.25}, "FaceAdd": True},
               "BodyP": {"Body": "BodyAltUI_X", "Factors": [1.0] * 17, "Boobs": 0.5, "Waist": 0.25},
               "ModP": {"Entry": "SomePak/Page", "Values": {"A": 1.0}, "Colors": {"C": [0.5, 0.5, 0.5, 1.0]}, "Texts": {"T": 'say "hi"\\n'}, "Off": ["A"]},
               "App": {"HairstyleName": "Hair_1", "MakeupData": {"Eye": {"List": ["EyeA"]}}, "SkinName": "Skin_1", "HairColor": [0.2, 0.1, 0.05, 1.0], "Waist": 0.5, "Hip": 0.0,
                       "BoobsSize": 0.75, "EyeColors": {"Iris": [0.1, 0.2, 0.3, 1.0]}, "MakeupColors": {}, "Mutation": {"Color": 0.0, "Glow": 0.0, "Veins": False, "Eyes": False, "Skin": "None", "Story": False},
                       "OilOn": True, "Oil": 0.5}}
    for sname, v in samples.items():
        mgr.call_method("Test Share %s Roundtrip" % sname, args=(sf.encode(v),)); out = str(mgr.get_editor_property("TmpStr"))
        try: back = _j.loads(out)
        except Exception: back = {"unparsable": out[:200]}
        expect("roundtrip " + sname, norm(back), norm(v))

    # part 2 exports
    def export(hook):
        mgr.call_method(hook); t_ = str(mgr.get_editor_property("TmpStr"))
        try: return _j.loads(t_)["entries"][0]
        except Exception: return {"unparsable": t_[:200]}
    mgr.set_editor_property("FacesSave", None); mgr.call_method("Test Share Add Face Raw"); e = export("Test Share Export Face")
    expect("export face", (e.get("kind"), e.get("name"), sorted(e.get("data", {}))), ("face", "Shared face", ["FaceAdd", "Values"]))
    mgr.call_method("Test Load Presets"); mgr.call_method("Test Add Preset", args=("Skin_Default", "Hair_A")); e = export("Test Share Export Appearance")
    expect("export appearance", (e.get("kind"), sorted(e.get("data", {}))), ("appearance", sorted(n for n, _ in sf.APP_SCHEMA)))
    mgr.call_method("Test Body Presets Reset"); mgr.call_method("Test Add Body Preset Raw", args=("Body_X", "Slim", 1)); e = export("Test Share Export BodyPreset")
    expect("export body preset", (e.get("kind"), e.get("name"), e.get("data", {}).get("Body"), [r["type"] for r in e.get("refs", [])]), ("bodypreset", "Slim", "Body_X", ["body"]))
    mgr.call_method("Test Share Mod Page"); e = export("Test Share Export ModPreset")
    expect("export mod preset", (e.get("kind"), e.get("name"), e.get("data", {}).get("Entry"), [(r["type"], r["item"], r["mod"]) for r in e.get("refs", [])]),
           ("modpreset", "Warm", "TestPak/Page", [("modentry", "TestPak/Page", "TestPak")]))

    # part 2: a document with one entry of every kind; a mod page that is not installed is missing
    one = [sf.sample_look(9), {"kind": "outfit", "name": "O", "data": {"Pieces": {"A": [1, 2, 3, 4]}, "SlotColors": {}}},
           {"kind": "face", "name": "F", "data": samples["Face"]}, {"kind": "appearance", "name": "P", "data": samples["App"]},
           {"kind": "bodypreset", "name": "B", "data": samples["BodyP"]},
           {"kind": "modpreset", "name": "M", "data": samples["ModP"], "refs": [{"type": "modentry", "item": "SomePak/Page", "label": "SomePak/Page", "mod": "SomePak"}]}]
    one[0]["refs"] = []
    doc = sf.encode({"altui": "share", "version": 1, "entries": one, "mods": {"SomePak": "Some Mod"}})
    mgr.call_method("Test Share Check", args=(doc,)); summary = str(mgr.get_editor_property("TmpStr")); unreal.log_warning("EDTEST info summary 2: %r" % summary)
    expect("every kind parsed", [len(mgr.get_editor_property(v)) for v in ("ShLooks", "ShOutfits", "ShFaces", "ShApps", "ShBodyPresets", "ShModPresets")], [1] * 6)
    # the mod page, plus the sample look's and the outfit's pieces: no reference and not installed here (Share Scan Pieces)
    expect("mod page missing", (mgr.get_editor_property("TmpI"), "Some Mod" in summary), (1 + len(set(one[0]["data"]["Worn"])) + 1, True))

    # part 2: import of every kind (not saved); the new entries carry the document's fields
    app_e = {"kind": "appearance", "name": "P", "data": samples["App"], "refs": [{"type": "hair", "item": "Hair_1", "label": "Hair 1", "mod": "SomePak"}]}
    two = [{"kind": "face", "name": "F", "data": samples["Face"]}, app_e, {"kind": "bodypreset", "name": "B", "data": samples["BodyP"]},
           {"kind": "modpreset", "name": "M", "data": samples["ModP"], "refs": [{"type": "modentry", "item": "SomePak/Page", "label": "SomePak/Page", "mod": "SomePak"}]}]
    doc2 = sf.encode({"altui": "share", "version": 1, "entries": two, "mods": {"SomePak": "Some Mod"}})
    def counts():
        mps = mgr.get_editor_property("ModPresetSaves"); sv = mps.get("SomePak") if "SomePak" in [str(k) for k in mps.keys()] else None
        return (len(mgr.get_editor_property("FacesSave").get_editor_property("Faces")), len(mgr.get_editor_property("Presets").get_editor_property("Data")),
                len(mgr.get_editor_property("BodyPresetSave").get_editor_property("Presets")), len(sv.get_editor_property("Presets")) if sv else 0)
    def last_mod():
        mgr.call_method("Test Share Last Mod Preset", args=("SomePak",)); t_ = str(mgr.get_editor_property("TmpStr"))
        try: return _j.loads(t_)
        except Exception: return ["unparsable", t_[:200]]
    before = counts(); mgr.call_method("Test Share Import", args=(doc2, False)); icon1 = mgr.get_editor_property("ShIconN")
    expect("import: one more of every kind", [a - b for a, b in zip(counts(), before)], [1, 1, 1, 1])
    expect("import counted per kind", {str(k): v for k, v in mgr.get_editor_property("ShImpN").items() if v}, {"face": 1, "appearance": 1, "bodypreset": 1, "modpreset": 1})
    e = export("Test Share Export Face"); expect("imported face", (e.get("name"), norm(e.get("data"))), ("F", norm(samples["Face"])))
    e = export("Test Share Export Appearance"); expect("imported appearance (name, colours)", (e.get("name"), norm(e.get("data"))), ("P", norm(samples["App"])))
    expect("icon number free", icon1 > 0, True)
    e = export("Test Share Export BodyPreset"); expect("imported body preset", (e.get("name"), norm(e.get("data"))), ("B", norm(samples["BodyP"])))
    mp = dict(samples["ModP"], Entry="Page"); expect("imported mod preset (Entry = row)", norm(last_mod()), norm(["M", mp]))
    # without missing pieces: the appearance loses its missing hair and the make-up row no table has; body and mod presets stay
    mgr.call_method("Test Share Import", args=(doc2, True)); icon2 = mgr.get_editor_property("ShIconN")
    e = export("Test Share Export Appearance"); d = e.get("data", {})
    expect("clean appearance", (d.get("HairstyleName"), d.get("MakeupData"), d.get("SkinName")), ("None", {"Eye": {"List": []}}, "Skin_1"))
    expect("second icon number differs", icon2 != icon1, True)
    e = export("Test Share Export BodyPreset"); expect("clean body preset unchanged", norm(e.get("data")), norm(samples["BodyP"]))
    expect("clean mod preset unchanged", norm(last_mod()), norm(["M", mp]))

    # part 3: the entries of the collection page (keys "<kind>:<index>", mod presets "modpreset:<pak>|<index>")
    mgr.call_method("Test Share Page Keys")
    keys = [str(k) for k in mgr.get_editor_property("ShPageKeys")]; pnames = [str(k) for k in mgr.get_editor_property("ShPageNames")]; subs = [str(k) for k in mgr.get_editor_property("ShPageSubs")]
    nf, npre, nbp, nmp = counts(); per = lambda k: [x for x in keys if x.startswith(k + ":")]
    expect("page: one key per entry", [len(per(k)) for k in ("look", "outfit", "face", "appearance", "bodypreset")] + [len([x for x in per("modpreset") if x.startswith("modpreset:SomePak|")])],
           [len(mgr.get_editor_property("LooksSave").get_editor_property("Looks")), len(mgr.get_editor_property("Outfits").get_editor_property("outfits")), nf, npre, nbp, nmp])
    expect("page: lists of the same length", (len(pnames), len(subs)), (len(keys), len(keys)))
    at = lambda k: (pnames[keys.index(k)], subs[keys.index(k)]) if k in keys else None
    expect("page: names and subs", (at("face:%d" % (nf - 1))[0], at("appearance:%d" % (npre - 1))[0], at("bodypreset:%d" % (nbp - 1)), at("modpreset:SomePak|%d" % (nmp - 1))),
           ("F", "P", ("B", "BodyAltUI_X"), ("M", "SomePak")))

    # part 3: ticks and the export of the selection (in page order, not click order)
    mk = "modpreset:SomePak|%d" % (nmp - 1); fk = "face:%d" % (nf - 1)
    mgr.set_editor_property("ShareSel", [mk, fk]); mgr.call_method("Test Share Selected Text"); t_ = str(mgr.get_editor_property("TmpStr"))
    try: sel = _j.loads(t_)
    except Exception: sel = {"unparsable": t_[:200]}
    expect("selection exported in page order", [(e["kind"], e["name"]) for e in sel.get("entries", [])], [("face", "F"), ("modpreset", "M")])
    expect("selected mod preset: its page key", sel["entries"][1]["data"]["Entry"] if len(sel.get("entries", [])) > 1 else None, "SomePak/Page")
    mgr.set_editor_property("ShareSel", []); mgr.call_method("Test Share Tick", args=(fk,)); expect("tick", [str(x) for x in mgr.get_editor_property("ShareSel")], [fk])
    mgr.call_method("Test Share Tick", args=(fk,)); expect("tick again: off", list(mgr.get_editor_property("ShareSel")), [])
    mgr.call_method("Test Share Tick Kind", args=("face", True)); expect("all faces", sorted(str(x) for x in mgr.get_editor_property("ShareSel")), sorted(per("face")))
    mgr.call_method("Test Share Tick Kind", args=("face", False)); expect("no faces", list(mgr.get_editor_property("ShareSel")), [])

    # clean up: the names imported presets left under their icon numbers
    for ic in (icon1, icon2): mgr.call_method("Test Set Custom Name", args=("preset", str(ic), ""))


run(main)
