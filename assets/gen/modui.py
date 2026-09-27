"""The Mods tab's contract with other mods - the single source for the generator, the example mod and the tests.

A mod lists its entries in /Game/Mod/<Pak>/AltUI_Entries (row struct S_AltUIModEntry) and their fields in
/Game/Mod/<Pak>/AltUI_Fields (S_AltUIModField). Its actor implements BPI_AltUIMod: AltUI reads each field with
Get AltUI Value and reports every change with On AltUI Changed. One number per field: a toggle is 0/1, a slider or
number its value, a choice the option index, a button always 1. Color fields go through Get AltUI Color / On AltUI Color
Changed, Text fields through Get AltUI Text / On AltUI Text Changed, and Info fields only read Get AltUI Text.
"""
M = "/Game/Mod/AltUI"
ENTRY_STRUCT = M + "/S_AltUIModEntry"
FIELD_STRUCT = M + "/S_AltUIModField"
LIST_STRUCT = M + "/S_ModFieldList"          # AltUI-internal: map values take no arrays
INTERFACE = M + "/BPI_AltUIMod"
INTERFACE_CLASS = INTERFACE + ".BPI_AltUIMod_C"
ENTRIES_TABLE = "AltUI_Entries"
FIELDS_TABLE = "AltUI_Fields"

ENTRY_MEMBERS = [("Caption", "text", ""), ("Actor", "softclass:/Script/Engine.Actor", ""), ("Order", "int", "")]
FIELD_MEMBERS = [("Entry", "name", ""), ("Key", "name", ""), ("Type", "name", ""), ("Label", "text", ""),
                 ("Min", "float", ""), ("Max", "float", ""), ("Step", "float", ""), ("Options", "text", "array"),
                 ("Order", "int", "")]
TYPES = ["Header", "Button", "Toggle", "Slider", "Choice", "Number", "Color", "Text", "Info"]
RANGED = ["Slider", "Number"]            # need Min < Max
TEXTUAL = ["Text", "Info"]              # read with Get AltUI Text

GET_VALUE = "Get AltUI Value"
ON_CHANGED = "On AltUI Changed"
GET_COLOR = "Get AltUI Color"; ON_COLOR = "On AltUI Color Changed"   # Color fields
GET_TEXT = "Get AltUI Text"; ON_TEXT = "On AltUI Text Changed"       # Text (both) and Info (read only) fields

# editor tests: a stub mod with entries in reverse order and one field for every rule of what is left out
TEST_MOD = "AltUIMod_Test"
TEST_ENTRIES = {"Second": {"Caption": "Second", "Actor": "/Script/Engine.PointLight", "Order": 2},
                "First": {"Caption": "First", "Actor": "/Script/Engine.PointLight", "Order": 1},
                "Empty": {"Caption": "Empty", "Actor": "/Script/Engine.PointLight", "Order": 3}}
TEST_FIELDS = {
    "F_Slider": {"Entry": "First", "Key": "Size", "Type": "Slider", "Label": "Size", "Min": 0.0, "Max": 10.0, "Step": 0.5, "Order": 2},
    "F_Header": {"Entry": "First", "Key": "Head", "Type": "Header", "Label": "Section", "Order": 1},
    "F_Toggle": {"Entry": "First", "Key": "On", "Type": "Toggle", "Label": "On", "Order": 3},
    "F_Choice": {"Entry": "Second", "Key": "Mode", "Type": "Choice", "Label": "Mode", "Options": ["A", "B"], "Order": 1},
    "F_Button": {"Entry": "Second", "Key": "Go", "Type": "Button", "Label": "Go", "Order": 2},
    # left out: unknown type, choice without options, slider without range, unknown entry
    "X_Type": {"Entry": "First", "Key": "Bad1", "Type": "Colour", "Label": "x", "Order": 9},
    "X_NoOpts": {"Entry": "First", "Key": "Bad2", "Type": "Choice", "Label": "x", "Order": 9},
    "X_Range": {"Entry": "First", "Key": "Bad3", "Type": "Slider", "Label": "x", "Min": 5.0, "Max": 5.0, "Order": 9},
    "X_Entry": {"Entry": "Nowhere", "Key": "Bad4", "Type": "Toggle", "Label": "x", "Order": 9},
}
