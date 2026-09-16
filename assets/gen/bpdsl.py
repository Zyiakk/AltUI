"""Small DSL for producing BPGen JSON (blueprints, graphs, widgets, tables) from Python."""
import json

# Engine libraries
K_SYS = "/Script/Engine.KismetSystemLibrary"
K_MATH = "/Script/Engine.KismetMathLibrary"
K_STR = "/Script/Engine.KismetStringLibrary"
K_TXT = "/Script/Engine.KismetTextLibrary"
K_ARR = "/Script/Engine.KismetArrayLibrary"
K_MAP = "/Script/Engine.BlueprintMapLibrary"
K_SET = "/Script/Engine.BlueprintSetLibrary"
K_DT = "/Script/Engine.DataTableFunctionLibrary"
K_GS = "/Script/Engine.GameplayStatics"
K_WBL = "/Script/UMG.WidgetBlueprintLibrary"
K_IN = "/Script/Engine.KismetInputLibrary"
K_STT = "/Script/Engine.KismetStringTableLibrary"
E_ACTOR = "/Script/Engine.Actor"
E_PC = "/Script/Engine.PlayerController"
E_CTRL = "/Script/Engine.Controller"
E_PAWN = "/Script/Engine.Pawn"
E_WIDGET = "/Script/UMG.Widget"
E_USERWIDGET = "/Script/UMG.UserWidget"
E_PANEL = "/Script/UMG.PanelWidget"
E_IMAGE = "/Script/UMG.Image"
E_TEXT = "/Script/UMG.TextBlock"
E_BORDER = "/Script/UMG.Border"
E_EDIT = "/Script/UMG.EditableTextBox"
E_CHECK = "/Script/UMG.CheckBox"
E_SLIDER = "/Script/UMG.Slider"
E_TEX2D = "/Script/Engine.Texture2D"
E_DATATABLE = "/Script/Engine.DataTable"
S_LINCOLOR = "struct:/Script/CoreUObject.LinearColor"
S_COLOR = "struct:/Script/CoreUObject.Color"

# Game stubs
P_CPB = "/Game/Project/Classes/Character_Player_Base"
P_JODI = "/Game/Project/Character/Jodi/Jodi"
P_GS = "/Game/Project/Classes/GameMode/TKA_GameState_Base"
P_GS2 = "/Game/Project/Classes/GameMode/TKA_GameState"
P_BAG = "/Game/Project/Classes/Misc/Bag_Comp"
P_HUD = "/Game/Project/UserInterface/PlayingHud"
P_INV = "/Game/Project/UserInterface/Widgets/InventoryPanel"
P_GI = "/Game/Project/Classes/TKA_GameInstance"
P_HAIR_SAVE = "/Game/Project/Classes/Save/Hairstyle_Save"
P_PSAVE = "/Game/Project/Classes/Save/Player_Save"   # slot "TKAPlayer" (Functions.Get Player Save Slot Name)
P_MAKEUP_SAVE = "/Game/Project/Classes/Save/Makeup_Save"
P_HAIR_T = "/Game/Project/Hairstyle/HairstyleTable"; P_HAIR_S = "/Game/Project/Hairstyle/HairstyleStruct"
P_SKIN_T = "/Game/Project/Tables/SkinTable"; P_SKIN_S = "/Game/Project/Tables/SkinStruct"
P_MAKEUP_T = "/Game/Project/Tables/MakeupTable"; P_MAKEUP_S = "/Game/Project/Tables/MakeupStruct"
P_EYE_T = "/Game/Project/Tables/EyeTable"; P_EYE_S = "/Game/Project/Tables/EyeStruct"
P_MTYPE_T = "/Game/Project/Tables/MakeupTypeTable"; P_MTYPE_S = "/Game/Project/Tables/MakeupTypeStruct"
P_MDATA_S = "/Game/Project/Tables/MakeupDataStruct"
P_PRESET_SAVE = "/Game/Project/Classes/Save/MakeupPreset_Save"; P_PRESET_S = "/Game/Project/Classes/Struct/MakeupPreset_Struct"
P_DLC_T = "/Game/Project/Tables/DLC_MainTable"; P_DLC_S = "/Game/Project/Tables/DLC_Struct"   # filled by the game loader: one row per mounted mod (pak base name)
E_SKELMESH = "/Script/Engine.SkeletalMesh"; E_CHARACTER = "/Script/Engine.Character"; E_SKINNED = "/Script/Engine.SkinnedMeshComponent"
K_PATHS = "/Script/Engine.BlueprintPathsLibrary"; K_REND = "/Script/Engine.KismetRenderingLibrary"
P_PC = "/Game/Project/Classes/TKA_Controller"
P_WD = "/Game/Project/Classes/Misc/WardrobeData"
P_CC = "/Game/Project/Classes/Misc/Clothes_Comp"
P_CT = "/Game/Project/Clothes/com_ClothesTable"
P_CTV = "/Game/Project/Clothes/ClothesTable"
P_CTT = "/Game/Project/Clothes/ClothesTypeTable"
P_CTS = "/Game/Project/Clothes/ClothesTypeStruct"   # stub with CameraFocus (mirror camera code per slot)
P_CS = "/Game/Project/Clothes/ClothesStruct"
P_CG = "/Game/Project/Clothes/com_ClothesGroup"
P_CGV = "/Game/Project/Clothes/ClothesGroup"
P_CGS = "/Game/Project/Clothes/ClothesGroupStruct"
P_OUTFITS = "/Game/Project/Classes/Save/Outfits_Save"
P_OUTFIT_S = "/Game/Project/Classes/Struct/Outfit_Struct"
OUTFIT_MEMBER = "clothes"   # internal name in the game: clothes_5_E1AD9C5C4635FD04BF2E71A226121A33
M = "/Game/Mod/AltUI"


class G:
    """Graph builder. Nodes get ids; links are 'id.pin'. `chain` wires exec pins in order."""

    def __init__(self):
        self.nodes = []; self.links = []; self.exec = []; self._ids = set()

    def n(self, id, kind, **kw):
        # unknown keys are ignored by the plugin; "miss": "ignore" waives an unwired error exit (get_row/cast) for tests/unit/test_graph_paths.py
        # BPGen keeps ids in a TMap<FString,...> (case-insensitive) and silently overwrites -> fail hard here
        if id.lower() in self._ids: raise ValueError("duplicate node id (case-insensitive): %r" % id)
        self._ids.add(id.lower())
        d = {"id": id, "kind": kind}
        for k, v in kw.items():
            if k == "cls": k = "class"
            if k == "inp": k = "in"
            d[k] = v
        self.nodes.append(d); return id

    def call(self, id, cls, fn, **kw):
        return self.n(id, "call", cls=cls, function=fn, **kw)

    def get(self, id, var, cls=None):
        return self.n(id, "get", var=var, **({"cls": cls} if cls else {}))

    def set(self, id, var, **kw):
        return self.n(id, "set", var=var, **kw)

    def event(self, id, cls, name): return self.n(id, "event", cls=cls, name=name)
    def custom(self, id, name, inputs=()): return self.n(id, "custom_event", name=name, inputs=list(inputs))
    def branch(self, id, cond=None): return self.n(id, "branch", **({"inp": {"Condition": cond}} if cond else {}))
    def cast(self, id, cls, obj=None, pure=True, miss=None):
        """Dynamic cast. miss="ignore" documents that an unwired CastFailed exit (impure cast) ends the chain on purpose (tests/unit/test_graph_paths.py)."""
        return self.n(id, "cast", cls=cls, pure=pure, **({"inp": {"Object": obj}} if obj else {}), **({"miss": miss} if miss else {}))
    def foreach(self, id, arr): return self.n(id, "foreach", inp={"Array": arr})
    def seq(self, id, count=2): return self.n(id, "sequence", count=count)
    def self_(self, id="me"): return self.n(id, "self")
    def key(self, id, key, consume=True):
        """InputKey event; consume=False leaves the key to lower input components (game, other mods). Output pin `Key` = the key (useful with "AnyKey")."""
        return self.n(id, "input_key", key=key, **({} if consume else {"consume": False}))
    def brk(self, id, struct, val): return self.n(id, "break", struct=struct, inp={struct.rsplit("/", 1)[-1].split(".")[-1]: val})
    def make(self, id, struct, **fields): return self.n(id, "make", struct=struct, inp=fields)

    def lit_name(self, id, value):
        """Typed Name literal (for wildcard pins like Map_Add/Array_Add instead of a pin default)."""
        self.call(id, K_SYS, "MakeLiteralName", inp={"Value": value}); return "@" + id + ".ReturnValue"

    def link(self, a, b): self.links.append([a, b])
    def chain(self, *ids): self.exec.append(list(ids))
    def json(self): return {"nodes": self.nodes, "links": self.links, "exec": self.exec}


def pin(t, container="", value_type=None, ref=False):
    d = {"type": t}
    if container: d["container"] = container
    if value_type: d["value_type"] = value_type
    if ref: d["ref"] = True
    return d


def param(name, t, container="", value_type=None, ref=False, internal_name=None):
    d = {"name": name, **pin(t, container, value_type, ref)}
    if internal_name: d["internal_name"] = internal_name
    return d


def var(name, t, container="", default=None, value_type=None, **kw):
    d = {"name": name, **pin(t, container, value_type)}
    if default is not None: d["default"] = default
    d.update(kw); return d


def fn(name, inputs=(), outputs=(), graph=None, pure=False, override=False):
    d = {"name": name}
    if inputs: d["inputs"] = list(inputs)
    if outputs: d["outputs"] = list(outputs)
    if pure: d["pure"] = True
    if override: d["override"] = True
    if graph is not None: d["graph"] = graph.json() if isinstance(graph, G) else graph
    return d


def blueprint(path, parent=None, mode="create", variables=(), functions=(), event_graph=None, widget_tree=None, defaults=None):
    d = {"type": "blueprint", "path": path, "mode": mode}
    if parent: d["parent"] = parent
    if variables: d["variables"] = list(variables)
    if functions: d["functions"] = list(functions)
    if event_graph is not None: d["event_graph"] = event_graph.json() if isinstance(event_graph, G) else event_graph
    if widget_tree is not None: d["widget_tree"] = widget_tree
    if defaults: d["defaults"] = defaults
    return d


def struct(path, members):
    """User-defined struct. Members without internal_name get a deterministic one (<Name>_<idx>_<GUID>, GUID = MD5 of path + name):
    FStructureEditorUtils::AddVariable would draw a random GUID per build, and SaveGame data of the struct (AltUI_Looks.sav) is
    matched by name + GUID on load -> every rebuild would empty the stored looks (2026-09-15)."""
    import hashlib
    out = []
    for i, m in enumerate(members):
        m = dict(m)
        if "internal_name" not in m:
            m["internal_name"] = "%s_%d_%s" % (m["name"], 2 + 2 * i, hashlib.md5((path + "/" + m["name"]).encode()).hexdigest().upper())
        out.append(m)
    return {"type": "struct", "path": path, "members": out}
def enum(path, values): return {"type": "enum", "path": path, "values": list(values)}


def datatable(path, row_struct, composite=False, rows=None, parent_tables=None):
    d = {"type": "datatable", "path": path, "row_struct": row_struct, "composite": composite}
    if rows: d["rows"] = rows
    if parent_tables: d["parent_tables"] = list(parent_tables)
    return d


def w(cls, name="", props=None, slot=None, children=()):
    """Widget tree node."""
    d = {"class": cls}
    if name: d["name"] = name
    if props: d["props"] = props
    if slot: d["slot"] = slot
    if children: d["children"] = list(children)
    return d


def write(path, assets):
    json.dump({"assets": list(assets)}, open(path, "w"), indent=1, ensure_ascii=False)
    print("wrote", path, len(assets), "assets")
