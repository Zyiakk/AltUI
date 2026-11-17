#!/usr/bin/env python3
"""Text IDs (namespace + key) that several installed mods give different texts in their own tables (Mod_*, TKA_Mod_Table).
The game keeps one display string per ID, the last pak loaded wins: a group or mod then shows another mod's name (2026-11-16:
two installed mods share five group keys). Usage: mod_text_ids.py [Mods folder]."""
import sys, glob, collections, io, contextlib, tempfile, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pak11_extract import Pak
import uasset_props as up
M = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("TKA_MODS", "")
seen = collections.defaultdict(set)
def walk(o, pak, tbl, row):
    if isinstance(o, dict):
        if "key" in o and "text" in o: seen[(o.get("ns",""), o["key"])].add((o["text"], pak, tbl, row)); return
        for v in o.values(): walk(v, pak, tbl, row)
    elif isinstance(o, list):
        for v in o: walk(v, pak, tbl, row)
for p in sorted(glob.glob(M + "/*.pak")):
    try: pk = Pak(p)
    except Exception: continue
    with pk:
        for k in pk.files:
            b = k.rsplit("/",1)[-1]
            if not k.endswith(".uasset") or not (b.startswith("Mod_") or b == "TKA_Mod_Table.uasset"): continue
            try:
                ua = pk.read(k); ue = pk.read(k[:-6]+"uexp")
                with tempfile.TemporaryDirectory() as d:
                    open(d+"/a.uasset","wb").write(ua); open(d+"/a.uexp","wb").write(ue)
                    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()): dd = up.dump(d+"/a.uasset")
            except Exception: continue
            for ex in dd.values():
                for rk, rv in (ex.get("rows") or {}).items(): walk(rv, os.path.basename(p), b[:-7], rk)
bad = {k: v for k, v in seen.items() if len({t for t, *_ in v}) > 1}
print("text ids", len(seen), "shared with different texts", len(bad))
tb = collections.Counter(t for v in bad.values() for _, _, t, _ in v); print("by table", dict(tb))
for k, v in sorted(bad.items()):
    print("%s/%s:" % k); [print("   %-30s %-24s %-22s %s" % (repr(t), p, tb, r)) for t, p, tb, r in sorted(v)]
