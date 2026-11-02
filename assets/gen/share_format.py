"""Share as JSON (internal design notes): the format. AltUI writes and reads it in Blueprint (share_bp.py
generates both from the schemas here); encode() is the same writer in Python, for test data and the docs.

Document: {"altui": "share", "version": 1, "entries": [entry, ...], "mods": {pak: caption}} - keys in any order.
Entry: {"kind": "look"|"outfit"|..., "name": str, "data": {...}, "refs": [{"type", "item", "label", "mod"}, ...]}."""

FORMAT = "share"; VERSION = 1
KINDS_P1 = ["look", "outfit"]
KINDS = KINDS_P1 + ["face", "appearance", "bodypreset", "modpreset"]   # the rest: plan 2 - read, counted, skipped
REF_TYPES = ["clothes", "hair", "makeup", "skin", "body", "modentry"]

# token kinds of the Blueprint tokenizer (ShTokK)
TOK = {"{": 1, "}": 2, "[": 3, "]": 4, ":": 5, ",": 6, "str": 7, "num": 8, "true": 9, "false": 10, "null": 11}
MAX_TOKENS = 400000   # bound of every token loop (a 50-look package has about 60 000)
MAX_LIST = 2000       # entries of one array / map that are read
MAX_FIELDS = 200      # keys of one object that are read (unknown ones included)

# value types: str (Name or String), num (float), bool, color (LinearColor -> [r, g, b, a]), bcolor (Color, bytes -> [r, g, b, a]),
# strs (array of names), nums (array of floats), map_color / map_num / map_bcolor (keys are strings), map_list (name -> MakeupDataStruct.List),
# mut (S_Mutation)
VALUE_TYPES = ["str", "num", "bool", "color", "bcolor", "strs", "nums", "map_color", "map_num", "map_bcolor", "map_list", "mut", "map_str"]   # map_str: name -> string
SNAP_SCHEMA = [("Worn", "strs"), ("Makeup", "map_list"), ("Skin", "str"), ("Hair", "str"), ("Colors", "map_color"), ("HairColor", "color"),
               ("Boobs", "num"), ("Waist", "num"), ("Hip", "num"), ("Body", "str"), ("Scales", "nums"), ("SlotColors", "map_color"),
               ("EyeColors", "map_color"), ("MakeupColors", "map_color"), ("Face", "map_num"), ("FaceAdd", "bool"), ("Mutation", "mut"),
               ("OilOn", "bool"), ("Oil", "num")]
MUT_SCHEMA = [("Color", "num"), ("Glow", "num"), ("Veins", "bool"), ("Eyes", "bool"), ("Skin", "str"), ("Story", "bool")]
OUTFIT_SCHEMA = [("Pieces", "map_bcolor"), ("SlotColors", "map_color")]   # the game's Outfit_Struct.clothes + AltUI's OutfitColors of it
# part 2 (internal design notes): field names are the members of the saved structs
FACE_SCHEMA = [("Values", "map_num"), ("FaceAdd", "bool")]                                       # S_Face
BODYP_SCHEMA = [("Body", "str"), ("Factors", "nums"), ("Boobs", "num"), ("Waist", "num")]        # S_BodyPreset
MODP_SCHEMA = [("Entry", "str"), ("Values", "map_num"), ("Colors", "map_color"), ("Texts", "map_str"), ("Off", "strs")]   # S_ModPreset; Entry = "<pak>/<row>" in the export
APP_SCHEMA = [("HairstyleName", "str"), ("MakeupData", "map_list"), ("SkinName", "str"), ("HairColor", "color"), ("Waist", "num"), ("Hip", "num"),
              ("BoobsSize", "num"), ("EyeColors", "map_color"), ("MakeupColors", "map_color"), ("Mutation", "mut"), ("OilOn", "bool"), ("Oil", "num")]   # the game's MakeupPreset_Struct + AltUI's PresetColors

ESCAPES = {'"': '\\"', "\\": "\\\\", "\n": "\\n", "\t": "\\t", "\r": "\\r"}   # the only escapes the writer uses; other control characters go


def esc(s):
    return '"' + "".join(ESCAPES.get(c, "" if ord(c) < 32 else c) for c in s) + '"'


def encode(v):
    """The writer of share_bp in Python: no spaces; floats with 6 decimals (Blueprint's Conv_FloatToString writes the shortest form,
    "1.5" - the same number for every JSON reader)."""
    if isinstance(v, bool): return "true" if v else "false"
    if isinstance(v, int): return str(v)
    if isinstance(v, float): return "%.6f" % v
    if isinstance(v, str): return esc(v)
    if isinstance(v, list): return "[" + ",".join(encode(x) for x in v) + "]"
    if isinstance(v, dict): return "{" + ",".join(esc(str(k)) + ":" + encode(x) for k, x in v.items()) + "}"
    raise TypeError(type(v))


def sample_look(i):
    """A look of realistic size for tests (about 3 KB)."""
    worn = ["Piece_%d_%d" % (i, k) for k in range(12)]
    return {"kind": "look", "name": "Look %d ä" % i,
            "data": {"Worn": worn, "Makeup": {"Eye": {"List": ["EyeA"]}, "Lips": {"List": ["LipB", "LipC"]}}, "Skin": "Skin_1", "Hair": "Hair_%d" % i,
                     "Colors": {w: [0.5, 0.25, 0.125, 1.0] for w in worn}, "HairColor": [0.2, 0.1, 0.05, 1.0], "Boobs": 0.5, "Waist": 0.25, "Hip": 0.0,
                     "Body": "BodyAltUI_Test", "Scales": [1.0] * 17, "SlotColors": {w + "#0": [1.0, 0.0, 0.0, 1.0] for w in worn[:6]},
                     "EyeColors": {"Iris": [0.1, 0.2, 0.3, 1.0]}, "MakeupColors": {}, "Face": {"Smile": 0.5}, "FaceAdd": False,
                     "Mutation": {"Color": 0.0, "Glow": 0.0, "Veins": False, "Eyes": False, "Skin": "None", "Story": False}, "OilOn": False, "Oil": 0.0},
            "refs": [{"type": "clothes", "item": w, "label": "Piece %d" % k, "mod": "Mod_%d" % (k % 3)} for k, w in enumerate(worn)]}
