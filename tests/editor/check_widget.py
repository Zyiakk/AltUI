import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *

def main():
    dt = unreal.load_object(None, "/Game/Mod/BPGenTest/DT_R.DT_R")
    names = [str(n) for n in unreal.DataTableFunctionLibrary.get_data_table_row_names(dt)]
    expect("rows", names, ["a", "b"])
    cdt = unreal.load_object(None, "/Game/Mod/BPGenTest/CDT_R.CDT_R")
    cn = [str(n) for n in unreal.DataTableFunctionLibrary.get_data_table_row_names(cdt)]
    expect("composite rows", cn, ["a", "b"])
run(main)
