import sys, os, re; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
import unreal
from edtest_lib import *
import compat_fp
M = "/Game/Mod/AltUI"


# Game Fingerprint (Version Gate) must build the same text as compat_fp.fp_string from the same tables: Name=rows;...
# except that ItemTable leaves out rows of a mod's Mod_ExtraItemTable it has: the SomeMod stub has "Medicine" (in the ItemTable stub,
# so -1) and "SomeModExtra" (not in it, so nothing); the other mods of the DLC_MainTable stub have no such table and add nothing.
def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Game Fingerprint"); fp = str(mgr.get_editor_property("TmpStr"))
    names = [p.rsplit("/", 1)[-1] for p in compat_fp.FP_TABLES]
    expect("format", bool(re.fullmatch(";".join(r"%s=-?\d+" % n for n in names), fp)), True)
    counts = {}
    for p in compat_fp.FP_TABLES:
        dt = unreal.load_asset(p)
        counts[p] = len(unreal.DataTableFunctionLibrary.get_data_table_row_names(dt)) if dt else -1
    item = "/Game/Project/Tables/ItemTable"; counts[item] -= 1
    expect("same as compat_fp, less the stub row", fp, compat_fp.fp_string(counts))
    mgr.call_method("Test Game Fingerprint"); expect("second call starts from 0 again", str(mgr.get_editor_property("TmpStr")), fp)
    # Keep Loaded (2026-11-16): its ItemTable row, once however often it runs, and the fingerprint leaves it out
    mgr.call_method("Test Keep Loaded"); mgr.call_method("Test Keep Loaded")
    rows = [str(r) for r in unreal.DataTableFunctionLibrary.get_data_table_row_names(unreal.load_asset(item))]
    expect("keep row once", rows.count("AltUI_Keep"), 1)
    mgr.call_method("Test Game Fingerprint"); expect("fingerprint without the keep row", str(mgr.get_editor_property("TmpStr")), fp)


run(main)
