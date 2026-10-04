"""Generates assets/87_modexample.json: AltUIMod_Example, a mod that puts its settings into AltUI's Mods tab, built the
way MOD_UI.md describes. A lamp in front of Jodi with one field of every type: a toggle (light on/off), a key (the key
that switches the light in the game), a slider (brightness), a number (height), a choice (colour: Warm, Cold, Red,
Custom), a colour (the custom colour), a text (a note), an info line (state and note) and a button (back to the
defaults), under one header, and a quick menu action of its own (AltUI_Actions: the next colour, with an icon). The mod keeps its values
in a SaveGame of its own (loaded at BeginPlay, saved after every change) - AltUI only shows and reports them.

The actor is started by the Blueprint Loader (a TKA_BlueprintLoader row in the mod's own folder) and implements
BPI_AltUIMod; the two tables use AltUI's row structs, which the pak must not ship. Built by scripts/modexample.sh,
outside the AltUI chain like the weapon example.
"""
import os, sys; sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
from bpdsl import *
import modui as mu

NAME = "AltUIMod_Example"
MOD = "/Game/Mod/" + NAME
BP = MOD + "/BP_AltUIModExample"
BP_CLASS = BP + ".BP_AltUIModExample_C"
T_ACTION = MOD + "/T_ExampleAction"   # icon of the quick menu action
SG_LAMP = MOD + "/SG_ExampleLamp"; SLOT = NAME   # the mod keeps its own values: AltUI only shows and reports them
BPL_STRUCT = "/Game/Mod/TKA_BlueprintLoader/BlueprintToLoad_Struct"   # the loader's own row structure
E_PLIGHT = "/Script/Engine.PointLight"; E_LIGHTC = "/Script/Engine.LightComponent"; E_SCENEC = "/Script/Engine.SceneComponent"
DEF_BRIGHT = 5000.0; DEF_HEIGHT = 60.0; DEF_CUSTOM = "(R=0.3,G=1.0,B=0.4,A=1)"
COLOURS = [("Warm", "(R=1.0,G=0.75,B=0.5,A=1)"), ("Cold", "(R=0.6,G=0.8,B=1.0,A=1)"), ("Red", "(R=1.0,G=0.15,B=0.1,A=1)")]
CUSTOM = len(COLOURS)   # the index of "Custom" in the choice: takes the colour field
# what the lamp keeps: (variable, type, default) - the actor's variables, the SaveGame's, and the defaults of Reset
STATE = [("LightOn", "bool", "true"), ("Brightness", "float", str(DEF_BRIGHT)), ("Colour", "int", "0"), ("Height", "float", str(DEF_HEIGHT)),
         ("CustomColor", S_LINCOLOR, DEF_CUSTOM), ("Note", "string", ""), ("LightKey", mu.KEY_TYPE, "L")]


def key_is(g, id, key_pin, key):
    g.call(id, K_MATH, "EqualEqual_NameName", inp={"A": key_pin, "B": key}); return "@%s.ReturnValue" % id


def f_get_value():
    """Get AltUI Value(Key): Light 0/1, Brightness, Height, Colour index; anything else 0."""
    g = G()
    g.get("gon", "LightOn"); g.call("onf", K_MATH, "SelectFloat", inp={"A": "1.0", "B": "0.0", "bPickA": "@gon.LightOn"})
    g.get("gc", "Colour"); g.call("cf", K_MATH, "Conv_IntToFloat", inp={"InInt": "@gc.Colour"}); g.get("gb", "Brightness"); g.get("gh", "Height")
    v = "0.0"
    for i, (key, pin) in enumerate([("Colour", "@cf.ReturnValue"), ("Height", "@gh.Height"), ("Brightness", "@gb.Brightness"), ("Light", "@onf.ReturnValue")]):
        g.call("s%d" % i, K_MATH, "SelectFloat", inp={"A": pin, "B": v, "bPickA": key_is(g, "k%d" % i, "@entry.Key", key)}); v = "@s%d.ReturnValue" % i
    g.link(v[1:], "return.Value"); g.chain("entry", "return")
    return fn(mu.GET_VALUE, graph=g)


def f_get_color():
    """Get AltUI Color(Key): the custom colour (the only colour field)."""
    g = G(); g.get("gc", "CustomColor"); g.link("gc.CustomColor", "return.Color"); g.chain("entry", "return")
    return fn(mu.GET_COLOR, graph=g)


def f_get_key():
    """Get AltUI Key(Key): the key that switches the light (the only key field)."""
    g = G(); g.get("gk", "LightKey"); g.link("gk.LightKey", "return.Pressed"); g.chain("entry", "return")
    return fn(mu.GET_KEY, graph=g)


def f_get_text():
    """Get AltUI Text(Key): Note for the text field; for the info line (Status) a summary of the lamp."""
    g = G(); g.get("gn", "Note"); g.get("gon", "LightOn"); g.get("gb", "Brightness")
    g.call("st0", K_MATH, "SelectString", inp={"A": "On", "B": "Off", "bPickA": "@gon.LightOn"})
    g.call("bi", K_MATH, "FTrunc", inp={"A": "@gb.Brightness"}); g.call("bs", K_STR, "Conv_IntToString", inp={"InInt": "@bi.ReturnValue"})
    g.call("c1", K_STR, "Concat_StrStr", inp={"A": "@st0.ReturnValue", "B": ", "}); g.call("c2", K_STR, "Concat_StrStr", inp={"A": "@c1.ReturnValue", "B": "@bs.ReturnValue"})
    g.call("c3", K_STR, "Concat_StrStr", inp={"A": "@c2.ReturnValue", "B": " cd"})
    g.call("ne", K_STR, "IsEmpty", inp={"InString": "@gn.Note"}); g.call("c4", K_STR, "Concat_StrStr", inp={"A": "@c3.ReturnValue", "B": " - "})
    g.call("c5", K_STR, "Concat_StrStr", inp={"A": "@c4.ReturnValue", "B": "@gn.Note"})
    g.call("stat", K_MATH, "SelectString", inp={"A": "@c3.ReturnValue", "B": "@c5.ReturnValue", "bPickA": "@ne.ReturnValue"})
    g.call("out", K_MATH, "SelectString", inp={"A": "@stat.ReturnValue", "B": "@gn.Note", "bPickA": key_is(g, "ks", "@entry.Key", "Status")})
    g.link("out.ReturnValue", "return.Text"); g.chain("entry", "return")
    return fn(mu.GET_TEXT, graph=g)


def f_apply():
    """Put the state on the lamp: visibility, intensity, colour (a preset or the custom one), height above the chest."""
    g = G(); g.get("gl", "Light"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gl.Light"}); g.branch("b", "@iv.ReturnValue")
    g.get("gl2", "Light"); g.get("gpc", "PointLightComponent", cls=E_PLIGHT); g.link("gl2.Light", "gpc.self")
    g.get("gon", "LightOn"); g.call("vis", E_SCENEC, "SetVisibility", inp={"self": "@gpc.PointLightComponent", "bNewVisibility": "@gon.LightOn", "bPropagateToChildren": "false"})
    g.get("gb", "Brightness"); g.call("int", E_LIGHTC, "SetIntensity", inp={"self": "@gpc.PointLightComponent", "NewIntensity": "@gb.Brightness"})
    g.get("gc", "Colour"); g.get("gcc", "CustomColor"); col = COLOURS[0][1]
    for i, (_, rgb) in list(enumerate(COLOURS))[1:] + [(CUSTOM, (None, "@gcc.CustomColor"))]:
        g.call("ci%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": "@gc.Colour", "B": str(i)})
        g.call("sc%d" % i, K_MATH, "SelectColor", inp={"A": rgb, "B": col, "bPickA": "@ci%d.ReturnValue" % i}); col = "@sc%d.ReturnValue" % i
    g.call("lc", E_LIGHTC, "SetLightColor", inp={"self": "@gpc.PointLightComponent", "NewLightColor": col, "bSRGB": "true"})
    g.get("gh", "Height"); g.call("loc", K_MATH, "MakeVector", inp={"X": "100.0", "Y": "0.0", "Z": "@gh.Height"})
    g.get("gl3", "Light"); g.call("rl", E_ACTOR, "K2_SetActorRelativeLocation", inp={"self": "@gl3.Light", "NewRelativeLocation": "@loc.ReturnValue", "bSweep": "false", "bTeleport": "true"})
    g.chain("entry", "b", "vis", "int", "lc", "rl")
    return fn("Apply", graph=g)


def f_save():
    """Everything in STATE into the mod's own SaveGame."""
    g = G()
    # CreateSaveGameObject already returns the class it was given (DeterminesOutputType) - no cast needed
    g.call("mk", K_GS, "CreateSaveGameObject", inp={"SaveGameClass": SG_LAMP + ".SG_ExampleLamp_C"})
    tail = ["entry", "mk"]
    for v, _, _ in STATE:
        g.get("g" + v, v); g.n("s" + v, "set", var=v, cls=SG_LAMP, inp={"self": "@mk.ReturnValue", v: "@g%s.%s" % (v, v)}); tail.append("s" + v)
    g.call("sv", K_GS, "SaveGameToSlot", inp={"SaveGameObject": "@mk.ReturnValue", "SlotName": SLOT, "UserIndex": "0"})
    g.chain(*tail, "sv")
    return fn("Save", graph=g)


def event_graph():
    g = G()
    # the values of last time, before the lamp exists
    g.event("bp0", E_ACTOR, "ReceiveBeginPlay")
    g.call("ex", K_GS, "DoesSaveGameExist", inp={"SlotName": SLOT, "UserIndex": "0"}); g.branch("bex", "@ex.ReturnValue")
    g.call("ld", K_GS, "LoadGameFromSlot", inp={"SlotName": SLOT, "UserIndex": "0"}); g.cast("csg", SG_LAMP, "@ld.ReturnValue", pure=False, miss="ignore")
    tail = ["bp0", "ex", "bex", "ld", "csg"]
    for v, _, _ in STATE:
        g.get("lg" + v, v, cls=SG_LAMP); g.link("csg.AsSG_ExampleLamp", "lg%s.self" % v); g.set("ls" + v, v, inp={v: "@lg%s.%s" % (v, v)}); tail.append("ls" + v)
    # the light key needs the actor's input: enabled here; the Any Key event below must not consume, or the game gets no keys
    g.call("pcn", K_GS, "GetPlayerController", inp={"PlayerIndex": "0"}); g.self_("me")
    g.call("ein", E_ACTOR, "EnableInput", inp={"self": "@me.self", "PlayerController": "@pcn.ReturnValue"})
    g.chain(*tail, "ein"); g.chain("bex:else", "ein"); g.chain("csg:CastFailed", "ein")
    # the light key, pressed in the game (while AltUI's panel is open it keeps the keys to itself)
    g.key("ak", "AnyKey", consume=False)
    g.get("glk", "LightKey"); g.call("kv", K_IN, "Key_IsValid", inp={"Key": "@glk.LightKey"})
    g.call("ke", K_IN, "EqualEqual_KeyKey", inp={"A": "@ak.Key", "B": "@glk.LightKey"}); g.call("kok", K_MATH, "BooleanAND", inp={"A": "@kv.ReturnValue", "B": "@ke.ReturnValue"}); g.branch("bk", "@kok.ReturnValue")
    g.get("gon", "LightOn"); g.call("non", K_MATH, "Not_PreBool", inp={"A": "@gon.LightOn"}); g.set("son", "LightOn", inp={"LightOn": "@non.ReturnValue"})
    g.n("apk", "call_self", function="Apply"); g.n("svk", "call_self", function="Save"); g.chain("ak", "bk", "son", "apk", "svk")
    # first tick with Jodi around: the lamp, attached to her, in front of her chest
    g.event("tk", E_ACTOR, "ReceiveTick")
    g.get("gl", "Light"); g.call("iv", K_SYS, "IsValid", inp={"Object": "@gl.Light"}); g.branch("bl", "@iv.ReturnValue")
    g.call("pc", K_GS, "GetPlayerCharacter", inp={"PlayerIndex": "0"}); g.call("pv", K_SYS, "IsValid", inp={"Object": "@pc.ReturnValue"}); g.branch("bp", "@pv.ReturnValue")
    g.call("tr", K_MATH, "MakeTransform", inp={"Location": "(X=0,Y=0,Z=0)", "Rotation": "(Pitch=0,Yaw=0,Roll=0)", "Scale": "(X=1,Y=1,Z=1)"})
    g.n("sp", "spawn", cls=E_PLIGHT, inp={"SpawnTransform": "@tr.ReturnValue"}); g.set("sl", "Light", inp={"Light": "@sp.ReturnValue"})
    # a spawned PointLight is Stationary like a placed one: it could neither follow Jodi nor change its height
    g.get("gmc", "PointLightComponent", cls=E_PLIGHT); g.link("sp.ReturnValue", "gmc.self")
    g.call("mov", E_SCENEC, "SetMobility", inp={"self": "@gmc.PointLightComponent", "NewMobility": "Movable"})
    g.call("at", E_ACTOR, "K2_AttachToActor", inp={"self": "@sp.ReturnValue", "ParentActor": "@pc.ReturnValue", "SocketName": "None",
                                                  "LocationRule": "KeepRelative", "RotationRule": "KeepRelative", "ScaleRule": "KeepRelative", "bWeldSimulatedBodies": "false"})
    g.n("ap", "call_self", function="Apply")
    g.chain("tk", "bl"); g.chain("bl:else", "bp", "sp", "sl", "mov", "at", "ap")
    # the Mods tab reports a number field
    g.event("oc", mu.INTERFACE_CLASS, mu.ON_CHANGED)
    g.branch("b1", key_is(g, "k1", "@oc.Key", "Light")); g.call("gt", K_MATH, "Greater_FloatFloat", inp={"A": "@oc.Value", "B": "0.5"}); g.set("s1", "LightOn", inp={"LightOn": "@gt.ReturnValue"})
    g.branch("b2", key_is(g, "k2", "@oc.Key", "Brightness")); g.set("s2", "Brightness", inp={"Brightness": "@oc.Value"})
    g.branch("b3", key_is(g, "k3", "@oc.Key", "Colour")); g.call("rd", K_MATH, "Round", inp={"A": "@oc.Value"}); g.set("s3", "Colour", inp={"Colour": "@rd.ReturnValue"})
    g.branch("b5", key_is(g, "k5", "@oc.Key", "Height")); g.set("s5", "Height", inp={"Height": "@oc.Value"})
    g.branch("b4", key_is(g, "k4", "@oc.Key", "Reset")); resets = []
    for v, _, d in STATE:
        g.set("r" + v, v, inp={v: d}); resets.append("r" + v)
    g.n("ap2", "call_self", function="Apply"); g.n("sv2", "call_self", function="Save")
    g.chain("oc", "b1", "s1", "ap2"); g.chain("b1:else", "b2", "s2", "ap2"); g.chain("b2:else", "b3", "s3", "ap2"); g.chain("b3:else", "b5", "s5", "ap2")
    # a quick menu action of its own (AltUI_Actions): the next of the colours, Custom included
    g.branch("b6", key_is(g, "k6", "@oc.Key", "NextColour")); g.get("gco", "Colour"); g.call("nx", K_MATH, "Add_IntInt", inp={"A": "@gco.Colour", "B": "1"})
    g.call("md", K_MATH, "Percent_IntInt", inp={"A": "@nx.ReturnValue", "B": str(CUSTOM + 1)}); g.set("s6", "Colour", inp={"Colour": "@md.ReturnValue"})
    g.chain("b5:else", "b4", *resets, "ap2"); g.chain("b4:else", "b6", "s6", "ap2"); g.chain("ap2", "sv2")
    # ... a colour field (the custom colour: choosing it also switches the choice to Custom)
    g.event("occ", mu.INTERFACE_CLASS, mu.ON_COLOR)
    g.set("scc", "CustomColor", inp={"CustomColor": "@occ.Color"}); g.set("scu", "Colour", inp={"Colour": str(CUSTOM)})
    g.n("ap3", "call_self", function="Apply"); g.n("sv3", "call_self", function="Save"); g.chain("occ", "scc", "scu", "ap3", "sv3")
    # ... a text field
    g.event("oct", mu.INTERFACE_CLASS, mu.ON_TEXT)
    g.set("snt", "Note", inp={"Note": "@oct.Text"}); g.n("sv4", "call_self", function="Save"); g.chain("oct", "snt", "sv4")
    # ... a key field (an empty key: the light has no key)
    g.event("ock", mu.INTERFACE_CLASS, mu.ON_KEY)
    g.set("slk", "LightKey", inp={"LightKey": "@ock.Pressed"}); g.n("sv5", "call_self", function="Save"); g.chain("ock", "slk", "sv5")
    return g


def build():
    fields = {
        "Header": {"Entry": "Lamp", "Key": "Header", "Type": "Header", "Label": "A lamp in front of Jodi", "Order": 0},
        "Status": {"Entry": "Lamp", "Key": "Status", "Type": "Info", "Label": "Now", "Order": 1},
        "Light": {"Entry": "Lamp", "Key": "Light", "Type": "Toggle", "Label": "Light", "Order": 2},
        "LightKey": {"Entry": "Lamp", "Key": "LightKey", "Type": "Key", "Label": "Key for on/off", "Order": 3},
        "Brightness": {"Entry": "Lamp", "Key": "Brightness", "Type": "Slider", "Label": "Brightness", "Min": 0.0, "Max": 20000.0, "Step": 500.0, "Order": 4},
        "Height": {"Entry": "Lamp", "Key": "Height", "Type": "Number", "Label": "Height (cm)", "Min": -100.0, "Max": 200.0, "Step": 10.0, "Order": 5},
        "Colour": {"Entry": "Lamp", "Key": "Colour", "Type": "Choice", "Label": "Colour", "Options": [c for c, _ in COLOURS] + ["Custom"], "Order": 6},
        "CustomColor": {"Entry": "Lamp", "Key": "CustomColor", "Type": "Color", "Label": "Custom colour", "Order": 7},
        "Note": {"Entry": "Lamp", "Key": "Note", "Type": "Text", "Label": "Note", "Order": 8},
        "Reset": {"Entry": "Lamp", "Key": "Reset", "Type": "Button", "Label": "Back to the defaults", "Order": 9},
    }
    variables = [var(v, t, default=d or None) for v, t, d in STATE]
    return [
        blueprint(SG_LAMP, "/Script/Engine.SaveGame", variables=[var(v, t, default=d or None) for v, t, d in STATE]),
        blueprint(BP, E_ACTOR, interfaces=[mu.INTERFACE],
                  variables=[var("Light", "object:" + E_PLIGHT)] + variables,
                  functions=[f_get_value(), f_get_color(), f_get_text(), f_get_key(), f_apply(), f_save()], event_graph=event_graph()),
        datatable(MOD + "/" + mu.ENTRIES_TABLE, mu.ENTRY_STRUCT, rows={"Lamp": {"Caption": "Example lamp", "Actor": BP_CLASS, "Order": 0}}),
        datatable(MOD + "/" + mu.FIELDS_TABLE, mu.FIELD_STRUCT, rows=fields),
        # the quick menu: an action that is no field - with an icon of its own (the toggle "Light" is offered there anyway)
        {"type": "texture", "path": T_ACTION, "file": "tex/example_action.png", "props": {"CompressionSettings": "TC_EditorIcon", "LODGroup": "TEXTUREGROUP_UI",
                                                                                         "MipGenSettings": "TMGS_NoMipmaps", "NeverStream": True, "SRGB": True, "Filter": "TF_Bilinear"}},
        datatable(MOD + "/" + mu.ACTIONS_TABLE, mu.ACTION_STRUCT, rows={"NextColour": {"Caption": "Lamp: next colour", "Icon": T_ACTION + ".T_ExampleAction", "Actor": BP_CLASS, "Key": "NextColour", "Order": 0}}),
        datatable(MOD + "/TKA_BlueprintLoader", BPL_STRUCT, rows={NAME: {"Actor Class": BP_CLASS}}),
        datatable(MOD + "/TKA_Mod_Table", "/Game/Project/Tables/DLC_Struct",
                  rows={NAME: {"Caption": "AltUI Mods tab example", "Desc": "A lamp in front of Jodi, set up from AltUI's Mods tab",
                               "Version": 1.0, "Tables": []}}),
    ]


if __name__ == "__main__":
    write(os.path.join(os.path.dirname(__file__), "..", "87_modexample.json"), build())
