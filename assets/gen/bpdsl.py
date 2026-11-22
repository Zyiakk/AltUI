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
K_MCORE = "/Script/TheKillingAntidote.McoreFunctionLibrary"   # the game's native library (stub: bpgen/Source/TheKillingAntidote)
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
P_CB = "/Game/Project/Classes/Character_Base"
P_CNPC = "/Game/Project/Character/Npc/Character_NPC"; P_NPCF = "/Game/Project/Character/Npc/NPC_Female"
P_JASON = "/Game/Project/Character/Jason/Jason"; P_JASONCTRL = "/Game/Project/Character/Jason/Jason_Controller"   # the story's Jason (Character_NPC, Jason_Controller): AltUI's Jason prototype derives from it
P_NPCCTRL = "/Game/Project/Classes/Controller/Npc_Controller"   # followers (stubs: gen_stubs.py)
P_JODI = "/Game/Project/Character/Jodi/Jodi"
P_WVS = "/Game/Project/Classes/Struct/WeaponViewStruct"   # Jodi's camera view (unarmed / per weapon): fov, arm length, socket offset
P_IHC = "/Game/Project/Classes/Misc/InvisibleHand_Comp"   # the invisible hand: picks up items near Jodi while "InvisibleHand" is in her bag
P_PICKABLE_ACTOR = "/Game/Project/Classes/InteractiveActor/PickableActor_Base"   # parent of the game's pickup actors (Item_Machete <- PickableActor_MeleeWeapon <- this)
P_PICKABLE = "/Game/Project/Classes/Items/ItemComp_Pickable"   # a loose item's pick component (Can Be Auto Picked: the invisible hand may take it)
P_FLYING = "/Game/Project/Classes/Component/FlyingItem_Comp"   # flies an item to the invisible hand, then Jodi.On Item Picked (Init(hand))
P_JODI_BASE = "/Game/Project/Character/Jodi/Jodi_Base"   # parent of Jodi; the main menu's figure (Jodi_Intro) is one too, but no Jodi
P_GS = "/Game/Project/Classes/GameMode/TKA_GameState_Base"
P_ATTUI = "/Game/Project/UserInterface/AttentionUI"   # the game's notice widget (TKA_GameState_Base.Get Attention UI, on the player screen)
P_GS2 = "/Game/Project/Classes/GameMode/TKA_GameState"
P_BAG = "/Game/Project/Classes/Misc/Bag_Comp"
P_HUD = "/Game/Project/UserInterface/PlayingHud"
P_INVNPC = "/Game/Project/UserInterface/Widgets/InventoryNpc"   # the game's swap dialog with an NPC (PlayingHud.InventoryNpc)
P_IMGBTN = "/Game/Project/UserInterface/Widgets/ImageButton"   # the game's button widget (InventoryNpc.ImageButton_Close)
P_INV = "/Game/Project/UserInterface/Widgets/InventoryPanel"
P_GI = "/Game/Project/Classes/TKA_GameInstance"
P_HAIR_SAVE = "/Game/Project/Classes/Save/Hairstyle_Save"
P_PSAVE = "/Game/Project/Classes/Save/Player_Save"   # slot "TKAPlayer" (Functions.Get Player Save Slot Name)
P_PSAVE_LE = "/Game/Project/Classes/Save/Player_Save_LevelEnd"   # a chapter's end state: the next story level starts from it (Plots_GameState.Prev Level End Save)
P_TKASAVE = "/Game/Project/Classes/Save/TKA_Save"; S_ACTORSAVE = "struct:/Script/TheKillingAntidote.ActorSaveData"   # a story save (Level_<n>_<m>); the struct is native (kit stand-in: bpgen/Source/TheKillingAntidote)
P_OFFICE = "/Game/Project/Classes/GameMode/JodiOffice_GameState"   # the office level: Allow Player Climbing And Jumping off in its class defaults
P_PLOTS = "/Game/Project/Classes/GameMode/Plots_GameState"; P_JODI_SM = "/Game/Project/Character/Jodi/Jodi_StoryMode"   # story levels: their game state and player
P_MAKEUP_SAVE = "/Game/Project/Classes/Save/Makeup_Save"
P_HAIR_T = "/Game/Project/Hairstyle/HairstyleTable"; P_HAIR_S = "/Game/Project/Hairstyle/HairstyleStruct"
P_SKIN_T = "/Game/Project/Tables/SkinTable"; P_SKIN_S = "/Game/Project/Tables/SkinStruct"
P_MAKEUP_T = "/Game/Project/Tables/MakeupTable"; P_MAKEUP_S = "/Game/Project/Tables/MakeupStruct"
P_EYE_T = "/Game/Project/Tables/EyeTable"; P_EYE_S = "/Game/Project/Tables/EyeStruct"
P_MTYPE_T = "/Game/Project/Tables/MakeupTypeTable"; P_MTYPE_S = "/Game/Project/Tables/MakeupTypeStruct"
P_MDATA_S = "/Game/Project/Tables/MakeupDataStruct"
P_ANIM_T = "/Game/Project/Tables/AnimationTable"; P_ANIM_S = "/Game/Project/Tables/Animation_Struct"   # action animations ("poses"); the loader merges Mod_AnimationTable rows into it
P_ITEM_T = "/Game/Project/Tables/ItemTable"; P_ITEM_S = "/Game/Project/Tables/ItemStruct"
P_WEAPONTBL_T = "/Game/Project/Tables/WeaponTable"; P_WEAPONTBL_S = "/Game/Project/Tables/WeaponStruct"
P_MACHETE = "/Game/Project/Actors/Weapons/Weapon_Machete"; P_ITEM_MACHETE = "/Game/Project/Actors/Items/Item_Machete"
P_ITEMCLASS_E = "/Game/Project/Classes/Enum/ItemClass"   # ItemStruct.ItemClass: 0 tool, 1 collectible / part, 2 key / device, 3 weapon / thrown, 4 ammo, 5 consumable
P_GEQ_T = "/Game/Project/Tables/GunEquipment"; P_GEQ_S = "/Game/Project/Tables/GunEquipmentStruct"   # weapon attachments (type 0 optics, 1 barrel, 2 grip, 3 magazine)
P_HBSAVE = "/Game/Project/Classes/Save/HyperBox_Save"; P_HBDATA = "/Game/Project/Classes/Misc/HyperBoxData"   # storage box (inventory tab)
P_PAINT_T = "/Game/Project/Tables/GunPaint"; P_PAINT_S = "/Game/Project/Tables/GunPaintStruct"; P_GUN_S = "/Game/Project/Classes/Struct/Gun_Struct"
P_TV = "/Game/Project/Maps/JodisOffice/TV/TV_Actor"   # TV tab: the office TV (videos = the .mp4 files in <game>/Videos/TV/)
P_BED = "/Game/Project/Actors/Bed"   # Navigation tab: the save bed (On Use This -> Show Save Panel(Save Point Name)); Bed_Lab (Level 2) and Bed_Child are children of it; Sofa is furniture
P_DESCBASE = "/Game/Project/Classes/Misc/Description_Base"; P_DEPT = "/Game/Project/Actors/Misc/Department"   # room signs: Description (declared in Description_Base)
P_ARCH_T = "/Game/Project/Maps/JodisOffice/Computer/Jodi_Archives"; P_ARCH_S = "/Game/Project/Maps/JodisOffice/Computer/Jodi_Mail_Struct"   # Kodex: encyclopedia (Jodi's office PC)
P_NOTE_SAVE = "/Game/Project/Classes/Save/Note_Save"; P_SETTINGS_SAVE = "/Game/Project/Classes/Save/Settings_Save"; P_PWCOMP = "/Game/Project/Classes/Items/ItemComp_Password"; P_ZOMBIE = "/Game/Project/Zombie/Zombie_Base"; P_SHATTERER = "/Game/Project/Zombie/Shatterer"
P_AICTRL = "/Game/Project/Classes/Controller/AI_Controller"; P_ZOMBIECTRL = "/Game/Project/Classes/Controller/Zombie_Controller"   # Enemies tab (stubs: gen_stubs.py)
P_ZOMBIE_AIMODE = "/Game/Project/Classes/Enum/Zombie_AIMode"   # byte values: 0 None, 1 NoSoul, 2 Inactive, 3 Active, 4 ChasePlayer, 5 Following, 6 Patrol (Names array, not the NewEnumeratorN names)
P_TRADING = "/Game/Project/Actors/Misc/TradingMachine"   # vending machines (also _Ammo / _Refresh): map markers
P_INTERACTIVE = "/Game/Project/Classes/InteractiveActor/InteractiveActor_Base"; P_ITEMCOMP = "/Game/Project/Classes/Items/ItemComponent"
P_WEAPON = "/Game/Project/Actors/Weapons/Weapon_Base"; P_GUN = "/Game/Project/Actors/Weapons/Weapon_Gun_Base"; P_EQUIPBASE = "/Game/Project/Actors/Weapons/Equipment/Gun_Equipment_Base"; P_MAGCOMP = "/Game/Project/Actors/Weapons/Equipment/Gun_Mag_Comp"; P_OPTICSCOMP = "/Game/Project/Actors/Weapons/Equipment/Gun_Optics_Comp"; P_BARRELCOMP = "/Game/Project/Actors/Weapons/Equipment/Gun_Barrel_Comp"; P_GRIPCOMP = "/Game/Project/Actors/Weapons/Equipment/Gun_Grip_Comp"
P_PRESET_SAVE = "/Game/Project/Classes/Save/MakeupPreset_Save"; P_PRESET_S = "/Game/Project/Classes/Struct/MakeupPreset_Struct"
P_DLC_T = "/Game/Project/Tables/DLC_MainTable"; P_DLC_S = "/Game/Project/Tables/DLC_Struct"   # filled by the game loader: one row per mounted mod (pak base name)
E_SKELMESH = "/Script/Engine.SkeletalMesh"; E_CHARACTER = "/Script/Engine.Character"; E_SKINNED = "/Script/Engine.SkinnedMeshComponent"
E_SKELMESHCOMP = "/Script/Engine.SkeletalMeshComponent"; E_SCENECOMP = "/Script/Engine.SceneComponent"
K_PATHS = "/Script/Engine.BlueprintPathsLibrary"; K_REND = "/Script/Engine.KismetRenderingLibrary"
P_PC = "/Game/Project/Classes/TKA_Controller"
P_WD = "/Game/Project/Classes/Misc/WardrobeData"
P_CC = "/Game/Project/Classes/Misc/Clothes_Comp"
P_HAIRC = "/Game/Project/Classes/Misc/Hair_Comp"   # the game's hair pieces (Character_Player_Base.Hair Comps)
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
P_ABP = M + "/ABP_BodyScale"          # post-process ABP with the bone-scale variables (gen_bodyscale.py)
S_BODYSCALE = M + "/S_BodyScale"; S_FLOATS = M + "/S_Floats"; S_AUTOGUN = M + "/S_AutoGun"


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

    def lit_str(self, id, value):
        """Typed String literal (for wildcard pins like Array_Contains: a pin default is dropped when the wildcard resolves)."""
        self.call(id, K_SYS, "MakeLiteralString", inp={"Value": value}); return "@" + id + ".ReturnValue"

    def lit_bool(self, id, value):
        """Typed bool literal (for wildcard pins like Map_Add: a pin default is dropped when the wildcard resolves)."""
        self.call(id, K_SYS, "MakeLiteralBool", inp={"Value": value}); return "@" + id + ".ReturnValue"

    def lit_int(self, id, value):
        """Typed int literal (for wildcard pins like Array_Add: a pin default is dropped when the wildcard resolves)."""
        self.call(id, K_SYS, "MakeLiteralInt", inp={"Value": value}); return "@" + id + ".ReturnValue"

    def lit_float(self, id, value):
        """Typed float literal (for wildcard pins like Array_Add: a pin default is dropped when the wildcard resolves)."""
        self.call(id, K_SYS, "MakeLiteralFloat", inp={"Value": value}); return "@" + id + ".ReturnValue"

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


def blueprint(path, parent=None, mode="create", variables=(), functions=(), event_graph=None, widget_tree=None, defaults=None,
              interfaces=(), blueprint_type=None, components=(), remove_functions=()):
    """blueprint_type="interface" makes a Blueprint interface (functions = signatures only); interfaces = paths of
    interfaces this blueprint implements (their functions get bodies through `functions`, their events in the event graph);
    components = component() entries, parents before their children."""
    d = {"type": "blueprint", "path": path, "mode": mode}
    if parent: d["parent"] = parent
    if blueprint_type: d["blueprint_type"] = blueprint_type
    if interfaces: d["interfaces"] = list(interfaces)
    if components: d["components"] = list(components)
    if remove_functions: d["remove_functions"] = list(remove_functions)   # names to take out of an existing blueprint (augment)
    if variables: d["variables"] = list(variables)
    if functions: d["functions"] = list(functions)
    if event_graph is not None: d["event_graph"] = event_graph.json() if isinstance(event_graph, G) else event_graph
    if widget_tree is not None: d["widget_tree"] = widget_tree
    if defaults: d["defaults"] = defaults
    return d


def component(name, cls, parent=None, **properties):
    """A component in a blueprint's construction script: cls a component class path, parent the name of an earlier
    component (none = a root; the first root replaces DefaultSceneRoot), properties ImportText values on the template."""
    d = {"name": name, "class": cls}
    if parent: d["parent"] = parent
    if properties: d["properties"] = properties
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


def animblueprint(path, skeleton, variables, nodes, snapshot_var=None, additive=()):
    """AnimBlueprint: variables + a chain of ModifyBone nodes (component space), see BPGenAssets MakeAnimBlueprint. Without snapshot_var a
    post-process ABP (Input Pose first); with it a standalone ABP whose pose comes from that PoseSnapshot variable (Pose Snapshot node).
    additive = [(animation path, float variable, time[, bones])]: Apply Additive nodes before the bone nodes, the animation held at `time`
    (sequence evaluator), alpha = the variable; with bones only on those bones (Layered Blend per Bone against its identity frame)."""
    d = {"type": "animblueprint", "path": path, "skeleton": skeleton, "variables": list(variables), "nodes": list(nodes)}
    if additive: d["additive"] = [dict({"asset": a[0], "alpha": a[1], "time": a[2]}, **({"bones": list(a[3])} if len(a) > 3 else {})) for a in additive]
    if snapshot_var: d.update(source="snapshot", snapshot_var=snapshot_var)
    return d


def skeleton_stub(path):
    """A stand-in for a game skeleton the kit lacks (BPGenAssets MakeSkeletonStub): empty, only created when nothing is there, never packed."""
    return {"type": "skeleton", "path": path}


def animsequence_stub(path, skeleton, additive=False):
    """A stand-in for a game animation the kit lacks (BPGenAssets MakeAnimSequenceStub): empty, only created when nothing is there, never packed.
    additive: marked as a local-space additive (for an Apply Additive node)."""
    return {"type": "animsequence_stub", "path": path, "skeleton": skeleton, **({"additive": True} if additive else {})}


def animstub(path, skeleton, players):
    """A stand-in for a game ABP (BPGenAssets MakeAnimStub) carrying only sequence players under the game's node names: players = [(name, asset or None)]."""
    return {"type": "animstub", "path": path, "skeleton": skeleton, "players": [dict(name=n, **({"asset": a} if a else {})) for n, a in players]}


def animchild(path, parent, skeleton, overrides):
    """Child ABP of `parent` that swaps the assets of named parent nodes (BPGenAssets MakeAnimChild): overrides = {node name: asset path}."""
    return {"type": "animchild", "path": path, "parent": parent, "skeleton": skeleton, "overrides": dict(overrides)}


# Animation notifies and montages (BPGenAssets MakeAnimImport / MakeMontage). The game's notify classes are stubbed in 10_stubs.json with the
# game's variable names, types and defaults (never packed); their objects get the values by variable name.
SK_FEMALE = "/Game/Project/Character/Jodi/Body/Female_Skeleton"
NOTIFY_DIR = "/Game/Project/Classes/Notify"
N_MELEE = NOTIFY_DIR + "/MeleeAttack_NotifyState"     # hit window: BoneName, DamageScale (1.0), Reset Check State (true)
N_COMBO = NOTIFY_DIR + "/ComboAttack_NotifyState"     # combo window: Index = the NEXT step (Default 0, Second 1, ...)
N_SHAKE = NOTIFY_DIR + "/Shake_Notify"                # camera shake: Shake Class, Force Feedback
N_VOICE = NOTIFY_DIR + "/Voice_Notify"                # Voice (SoundBase), Voice Name (Grunt, GruntHeavy)
N_CHAREVENT = NOTIFY_DIR + "/CharacterEvent_Notify"   # Event (GrabWeapon, HolsterWeapon, ThrowWeapon)
E_PLAYSOUND = "/Script/Engine.AnimNotify_PlaySound"   # Sound
P_WHIP = "/Game/Project/Sounds/Weapons/Weapon_Whip"   # SoundCue of the melee swing
P_CAMSHAKE_MELEE = "/Game/Project/Classes/Camera/CameraShake_MeleeAttack"   # Shake Class of the melee attacks


def notify(time, cls=None, duration=None, values=None, name=None, track=None):
    """One notify for animimport / montage. cls: a notify class (Blueprint path or /Script/...); duration only for a NotifyState class (BPGen
    refuses it on a plain notify and requires it on a state). values: {variable name: value} set on the notify object; a name the class lacks,
    or a value of the wrong kind, fails the build (nothing is dropped silently); object and class values by path. Without cls: a notify by name
    only (the ABP's AnimNotify_<name> event, like the game's Footstep). track: the editor's notify track (the game: hits 1, combo windows 0)."""
    if cls is None and not name: raise ValueError("notify: needs a class or a name")
    if time < 0: raise ValueError("notify: time %r before the start" % time)
    if duration is not None and duration <= 0: raise ValueError("notify: duration %r" % duration)
    if values and cls is None: raise ValueError("notify: values need a class (%s)" % name)
    for k, v in (values or {}).items():
        if not isinstance(v, (bool, int, float, str)): raise ValueError("notify: value of %r must be a number, bool or string/path, not %r" % (k, v))
    d = {"time": float(time)}
    if cls: d["class"] = cls
    if name: d["name"] = name
    if duration is not None: d["duration"] = float(duration)
    if values: d["values"] = dict(values)
    if track is not None: d["track"] = int(track)
    return d


def _check_notifies(notifies, length=None, legacy=False, where=""):
    for n in notifies:
        if legacy and isinstance(n, (list, tuple)) and len(n) == 2 and isinstance(n[0], str): continue   # [name, time] (animimport, as before)
        if not isinstance(n, dict) or "time" not in n: raise ValueError("%s: notify %r is no notify() entry" % (where, n))
        if length is not None and n["time"] + n.get("duration", 0.0) > length + 1e-4:
            raise ValueError("%s: notify at %.3f%s past the end %.3f" % (where, n["time"], " + %.3f" % n["duration"] if "duration" in n else "", length))


def segment(anim, start=0.0, length=None, rate=1.0):
    """A montage segment: `length` seconds of sequence `anim` from `start` (both in the sequence; no length = to its end), played at `rate`.
    Segments follow each other in the montage."""
    if start < 0: raise ValueError("segment: start %r" % start)
    if length is not None and length <= 0: raise ValueError("segment: length %r" % length)
    if rate <= 0: raise ValueError("segment: rate %r" % rate)
    d = {"anim": anim, "start": float(start)}
    if length is not None: d["length"] = float(length)
    d["rate"] = float(rate); return d


def section(name, time, next=None):
    """A montage section starting at `time` (montage time); next = the section that follows when this one ends (none: the montage stops)."""
    if not isinstance(name, str) or not name.strip(): raise ValueError("section: name empty")
    d = {"name": name, "time": float(time)}
    if next: d["next"] = next
    return d


def montage(path, skeleton, slot, segments, sections=(), notifies=(), blend_in=None, blend_out=None, blend_out_trigger=None, auto_blend_out=None):
    """AnimMontage (BPGenAssets MakeMontage): one slot track (`slot`, a slot name the skeleton knows) of consecutive segments, sections (default:
    one "Default" at 0; the first at 0, ascending, unique; `next` names an existing one), notifies (notify() entries, montage time). blend_*:
    seconds (engine default 0.25 each, trigger -1, auto blend out on) - written only when given. The time checks here assume sequences with
    RateScale 1 (as animimport makes them); a segment of a sequence with another RateScale lasts length / (rate x RateScale), which BPGen
    checks against the real sequence."""
    if not slot: raise ValueError("montage %s: no slot" % path)
    if not segments: raise ValueError("montage %s: no segments" % path)
    length = None if any("length" not in s for s in segments) else sum(s["length"] / s["rate"] for s in segments)
    sections = list(sections) or [section("Default", 0)]
    names = [s["name"] for s in sections]
    if any(not n for n in names): raise ValueError("montage %s: section name empty" % path)
    if len(set(names)) != len(names): raise ValueError("montage %s: section names twice %s" % (path, names))
    if sections[0]["time"] != 0: raise ValueError("montage %s: the first section must start at 0" % path)
    if any(a["time"] >= b["time"] for a, b in zip(sections, sections[1:])): raise ValueError("montage %s: sections not ascending" % path)
    if length is not None and sections[-1]["time"] >= length: raise ValueError("montage %s: section %s at or past the end %.3f" % (path, names[-1], length))
    for s in sections:
        if s.get("next") and s["next"] not in names: raise ValueError("montage %s: section %s -> unknown %s" % (path, s["name"], s["next"]))
    _check_notifies(notifies, length, where="montage " + path)
    d = {"type": "montage", "path": path, "skeleton": skeleton, "slot": slot, "segments": list(segments), "sections": sections, "notifies": list(notifies)}
    for k, v in (("blend_in", blend_in), ("blend_out", blend_out), ("blend_out_trigger", blend_out_trigger), ("auto_blend_out", auto_blend_out)):
        if v is not None: d[k] = v
    return d


def animimport(path, skeleton, fbx, fbx_sha1=None, curves=None, markers=(), notifies=()):
    """FBX -> AnimSequence (BPGenAssets MakeAnimImport): curves {name: [[t, v(, interp)], ...]}, sync markers [[name, t]], notifies as notify()
    entries or [name, t] (by name only). A new FBX needs a new fbx_sha1, or the incremental build skips the entry."""
    _check_notifies(notifies, legacy=True, where="animimport " + path)
    d = {"type": "animimport", "path": path, "skeleton": skeleton, "fbx": fbx}
    if fbx_sha1: d["fbx_sha1"] = fbx_sha1
    d.update(curves=dict(curves or {}), markers=[list(m) for m in markers], notifies=list(notifies)); return d


def object_stub(path, cls):
    """A stand-in for a game asset the kit lacks (a SoundCue a notify names...): an empty object of `cls`, only created when nothing is at the
    path, never packed (BPGenAssets MakeObjectStub)."""
    return {"type": "object_stub", "path": path, "class": cls}


def blendspace1d(path, skeleton, axis, lo, hi, grid, samples, smoothing=0.0, scale_animation=False):
    """BlendSpace1D (BPGenAnim.cpp MakeBlendSpace1D): one axis `axis` from lo to hi in `grid` divisions; samples = [(sequence path, value)],
    at least two, each on a grid point (BPGen snaps nothing: off the grid fails), no value twice. smoothing: the axis' interpolation time in
    seconds; scale_animation: drive the play rate by the axis (UBlendSpace1D.bScaleAnimation)."""
    if hi <= lo or int(grid) < 1: raise ValueError("blendspace1d %s: axis %r..%r in %r divisions" % (path, lo, hi, grid))
    step = (hi - lo) / float(grid); vals = []
    if len(samples) < 2: raise ValueError("blendspace1d %s: needs at least two samples" % path)
    for a, v in samples:
        if not lo <= v <= hi: raise ValueError("blendspace1d %s: %s at %r outside %r..%r" % (path, a, v, lo, hi))
        k = (v - lo) / step
        if abs(k - round(k)) > 1e-4: raise ValueError("blendspace1d %s: %s at %r is off the grid (step %g)" % (path, a, v, step))
        if v in vals: raise ValueError("blendspace1d %s: value %r twice" % (path, v))
        vals.append(v)
    return {"type": "blendspace1d", "path": path, "skeleton": skeleton, "axis": {"name": axis, "min": float(lo), "max": float(hi), "grid": int(grid)},
            "samples": [[a, float(v)] for a, v in samples], "smoothing": float(smoothing), "scale_animation": bool(scale_animation)}


def animplayer(path, skeleton, blendspace, overlay, speed_var="Speed", alpha_var="OverlayAlpha", alpha_default=1.0, slot="DefaultSlot",
               add_slot=False, make_overlay_additive=False):
    """AnimBlueprint (BPGenAnim.cpp MakeAnimPlayer): BlendSpacePlayer(blendspace, X = float variable speed_var) -> Slot(slot) -> Apply Additive
    (looping player of `overlay`, Alpha = float variable alpha_var, default alpha_default) -> Output Pose. add_slot: a slot the skeleton lacks is
    added to DefaultGroup (the skeleton is saved); make_overlay_additive: a non-additive overlay becomes local-space additive against the
    reference pose (saved). Put it before the montages that use the slot."""
    if not slot: raise ValueError("animplayer %s: no slot" % path)
    if speed_var == alpha_var: raise ValueError("animplayer %s: speed_var and alpha_var have the same name" % path)
    return {"type": "animplayer", "path": path, "skeleton": skeleton, "blendspace": blendspace, "overlay": overlay, "speed_var": speed_var,
            "alpha_var": alpha_var, "alpha_default": float(alpha_default), "slot": slot, "add_slot": bool(add_slot),
            "make_overlay_additive": bool(make_overlay_additive)}


def subobject_defaults(path, component, **properties):
    """Class defaults of a component the parent class creates (BPGenAssets MakeSubobjectDefaults), e.g. a Character's CapsuleComponent,
    CharacterMovement or Mesh: `component` is the parent's property name of it (or its subobject name), properties are ImportText values
    (numbers and bools are converted). Put the entry after the blueprint entry of `path`; if that blueprint is rebuilt, this entry must
    run again."""
    if not component: raise ValueError("subobject_defaults %s: no component" % path)
    if not properties: raise ValueError("subobject_defaults %s.%s: no properties" % (path, component))
    for k, v in properties.items():
        if not isinstance(v, (bool, int, float, str)): raise ValueError("subobject_defaults %s.%s: value of %s must be a number, bool or string" % (path, component, k))
    return {"type": "subobject_defaults", "path": path, "component": component, "properties": dict(properties)}


def datatable(path, row_struct, composite=False, rows=None, parent_tables=None, keep_text_ids=False):
    """keep_text_ids: text cells keep the import's IDs (namespace = table name, key <row>_<column>) instead of the package path
    as namespace (BPGen default under /Game/Mod/ since 2026-11-15: equal row names of two mods' tables shared one label)."""
    d = {"type": "datatable", "path": path, "row_struct": row_struct, "composite": composite}
    if keep_text_ids: d["keep_text_ids"] = True
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


def real_stamp(g, id):
    """GetAccurateRealTime as float seconds (Seconds mod 1000 + PartialSeconds), the clock of the manager's "at=" log values."""
    g.call(id, K_GS, "GetAccurateRealTime"); g.call(id + "m", K_MATH, "Percent_IntInt", inp={"A": "@%s.Seconds" % id, "B": "1000"})
    g.call(id + "f", K_MATH, "Conv_IntToFloat", inp={"InInt": "@%sm.ReturnValue" % id}); g.call(id + "a", K_MATH, "Add_FloatFloat", inp={"A": "@%sf.ReturnValue" % id, "B": "@%s.PartialSeconds" % id})
    return "@%sa.ReturnValue" % id


def manager_class_async(g, bp_head, mgr):
    """For the spawners (hook, loader entry): the manager class loads in the background from BeginPlay on (Async Load Class Asset), not
    blocking in TryInit - a blocking load of the manager with all it references (~16 MB of Blueprint) stood the game still for
    0.6 s at every level start and main menu (2026-11-16). bp_head: the exec node BeginPlay goes on with (it runs at once; the
    class comes later). TryInit chains into "bld" (loaded yet? not yet: nothing, the timer comes again) and reads "@cc.AsActor";
    a class that never comes (mod pak missing) ends in "br2:else" as before. Variables: MgrClass, MgrLoaded (MGR_VARS)."""
    g.n("acl", "load_class_async", inp={"AssetClass": mgr + "." + mgr.rsplit("/", 1)[-1] + "_C"})
    g.set("acs", "MgrClass", inp={"MgrClass": "@acl.Class"}); g.set("acd", "MgrLoaded", inp={"MgrLoaded": "true"})
    g.chain("acl:Completed", "acs", "acd"); g.chain("acl", bp_head)
    g.get("gml", "MgrLoaded"); g.branch("bld", "@gml.MgrLoaded")
    g.get("gmc", "MgrClass"); g.n("cc", "class_cast", pure=True, cls=E_ACTOR, inp={"Class": "@gmc.MgrClass"})
    g.call("iv", K_SYS, "IsValidClass", inp={"Class": "@cc.AsActor"}); g.branch("br2", "@iv.ReturnValue")
    g.chain("bld", "br2")
    return "acl"


MGR_VARS = [var("MgrClass", "class:/Script/CoreUObject.Object"), var("MgrLoaded", "bool")]


def look_scene_branch(g):
    """For the spawners (hook, loader entry): branch "bm" is true in a level whose figure is no Jodi pawn but a Jodi_Intro
    - the main menu's scenes (Menu_Standing / Menu_Sitting, opened by Menu at random) and the loading scene (Loading).
    The manager comes there anyway and puts the look on that figure (Find Menu Wearer). Exec in "lvl", out of "bm":
    GetCurrentLevelName is not pure in 4.27, off the exec chain it is pruned."""
    g.call("lvl", K_GS, "GetCurrentLevelName", inp={"bRemovePrefixString": "true"})
    g.call("menu", K_STR, "StartsWith", inp={"SourceString": "@lvl.ReturnValue", "InPrefix": "Menu_", "SearchCase": "CaseSensitive"})
    g.call("load", K_STR, "EqualEqual_StrStr", inp={"A": "@lvl.ReturnValue", "B": "Loading"})
    g.call("or", K_MATH, "BooleanOR", inp={"A": "@menu.ReturnValue", "B": "@load.ReturnValue"}); g.branch("bm", "@or.ReturnValue")
    g.chain("lvl", "bm")


def mod_table_load(g, p, pak_pin, table):
    """/Game/Mod/<pak>/<table> loaded by path and cast to DataTable. Returns (head, cast, table pin): callers chain into head and on
    from cast. head is a branch on the file being in a pak (Content/Mod/<pak>/<table>.uasset, a lookup in the pak index): a load of a
    table that does not exist cost ~0.4 ms, with ~700 mods and four tables 1.25 s per level in Scan Mod Entries (2026-11-13). No
    file -> nothing after head runs (in a loop: the next mod)."""
    g.call(p + "_n2s", K_STR, "Conv_NameToString", inp={"InName": pak_pin})
    g.call(p + "_pcd", K_PATHS, "ProjectContentDir"); g.call(p + "_f1", K_STR, "Concat_StrStr", inp={"A": "@%s_pcd.ReturnValue" % p, "B": "Mod/"})
    g.call(p + "_f2", K_STR, "Concat_StrStr", inp={"A": "@%s_f1.ReturnValue" % p, "B": "@%s_n2s.ReturnValue" % p})
    g.call(p + "_f3", K_STR, "Concat_StrStr", inp={"A": "@%s_f2.ReturnValue" % p, "B": "/%s.uasset" % table})
    g.call(p + "_fx", K_PATHS, "FileExists", inp={"InPath": "@%s_f3.ReturnValue" % p}); g.branch(p + "_bx", "@%s_fx.ReturnValue" % p)
    g.call(p + "_c1", K_STR, "Concat_StrStr", inp={"A": "/Game/Mod/", "B": "@%s_n2s.ReturnValue" % p})
    g.call(p + "_c2", K_STR, "Concat_StrStr", inp={"A": "@%s_c1.ReturnValue" % p, "B": "/%s.%s" % (table, table)})
    g.call(p + "_sp", K_SYS, "MakeSoftObjectPath", inp={"PathString": "@%s_c2.ReturnValue" % p})
    g.call(p + "_sr", K_SYS, "Conv_SoftObjPathToSoftObjRef", inp={"SoftObjectPath": "@%s_sp.ReturnValue" % p})
    g.call(p + "_ld", K_SYS, "LoadAsset_Blocking", inp={"Asset": "@%s_sr.ReturnValue" % p})
    g.cast(p + "_ck", E_DATATABLE, "@%s_ld.ReturnValue" % p, pure=False, miss="ignore"); g.chain(p + "_bx", p + "_ld", p + "_ck")
    return p + "_bx", p + "_ck", "@%s_ck.AsData Table" % p


def write(path, assets):
    json.dump({"assets": list(assets)}, open(path, "w"), indent=1, ensure_ascii=False)
    print("wrote", path, len(assets), "assets")
