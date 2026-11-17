"""Text IDs of BPGen tables (spec internal design notes): namespace = package path, key as the JSON
import makes it (<row>_<column>[_Index<n>|_<member>|_ValueIndex<n>]); NSLOCTEXT / INVTEXT cells and keep_text_ids tables untouched.
Read through the exported column strings (NSLOCTEXT("<ns> [<package marker>]", "<key>", "<source>"); the cook strips the marker)."""
import sys, os, re; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *

LOC = re.compile(r'NSLOCTEXT\("((?:[^"\\]|\\.)*)", "((?:[^"\\]|\\.)*)", "((?:[^"\\]|\\.)*)"\)')
TEST, TWIN = "/Game/Mod/AltUIMod_Test", "/Game/Mod/AltUIMod_Twin"


def ids(table, column):
    """{row: [(namespace without package marker, key, source), ...]} of one column"""
    dt = unreal.load_asset(table)
    rows = [str(r) for r in unreal.DataTableFunctionLibrary.get_data_table_row_names(dt)]
    vals = unreal.DataTableFunctionLibrary.get_data_table_column_as_string(dt, column)
    return {r: [(re.sub(r" \[[^\]]*\]$", "", ns), k, src) for ns, k, src in LOC.findall(str(v))] for r, v in zip(rows, vals)}, {r: str(v) for r, v in zip(rows, vals)}


def main():
    a, _ = ids(TEST + "/AltUI_Fields", "Label"); b, _ = ids(TWIN + "/AltUI_Fields", "Label")
    expect("same row name, own namespace per mod (AltUIMod_Test)", a["F_Slider"], [(TEST + "/AltUI_Fields", "F_Slider_Label", "Size")])
    expect("same row name, own namespace per mod (AltUIMod_Twin)", b["F_Slider"], [(TWIN + "/AltUI_Fields", "F_Slider_Label", "Twin size")])
    o, _ = ids(TWIN + "/AltUI_Fields", "Options")
    expect("text array column", o["F_Slider"], [(TWIN + "/AltUI_Fields", "F_Slider_Options_Index0", "Small"), (TWIN + "/AltUI_Fields", "F_Slider_Options_Index1", "Big")])
    e, _ = ids(TEST + "/AltUI_Entries", "Caption")
    expect("entries table too", e["First"], [(TEST + "/AltUI_Entries", "First_Caption", "First")])

    t = TWIN + "/TextIdTable"
    c, raw = ids(t, "Caption")
    expect("plain text cell", c["R1"], [(t, "R1_Caption", "One")])
    expect("NSLOCTEXT cell keeps its own namespace and key", c["R2"], [("OwnNs", "OwnKey", "Own")])
    expect("array of text", ids(t, "Words")[0]["R1"], [(t, "R1_Words_Index0", "w0"), (t, "R1_Words_Index1", "w1")])
    inner, raw_inner = ids(t, "Inner")
    expect("text in a nested struct", inner["R1"], [(t, "R1_Inner_Note", "inner")])
    expect("INVTEXT stays culture invariant", ("INVTEXT" in raw_inner["R2"], inner["R2"]), (True, []))
    expect("text values of a map", ids(t, "ByName")[0]["R1"], [(t, "R1_ByName_ValueIndex0", "va")])

    k = TWIN + "/TextIdKept"
    expect("keep_text_ids: the import's namespace (table name)", ids(k, "Caption")[0]["R1"], [("TextIdKept", "R1_Caption", "One")])
    expect("keep_text_ids: nested too", ids(k, "Inner")[0]["R1"], [("TextIdKept", "R1_Inner_Note", "inner")])


run(main)
