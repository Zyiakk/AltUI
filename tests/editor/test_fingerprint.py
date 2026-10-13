import sys, os, re; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
import unreal
from edtest_lib import *
import compat_fp
M = "/Game/Mod/AltUI"


# Game Fingerprint (Version Gate) must build the same text as compat_fp.fp_string from the same tables: Name=rows;...
def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Game Fingerprint"); fp = str(mgr.get_editor_property("TmpStr"))
    names = [p.rsplit("/", 1)[-1] for p in compat_fp.FP_TABLES]
    expect("format", bool(re.fullmatch(";".join(r"%s=-?\d+" % n for n in names), fp)), True)
    counts = {}
    for p in compat_fp.FP_TABLES:
        dt = unreal.load_asset(p)
        counts[p] = len(unreal.DataTableFunctionLibrary.get_data_table_row_names(dt)) if dt else -1
    expect("same as compat_fp", fp, compat_fp.fp_string(counts))


run(main)
