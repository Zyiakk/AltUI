"""A release build writes no AltUI_Log.sav: in the generated assets no graph calls "Log Line" - only the debug switches of
assets/gen/gen_manager_ui.py (ALTUI_WEAPONLOG, ALTUI_POSELOG, ALTUI_TABLOG, ALTUI_PERFLOG) wire it in. Perf Mark (the PERFLOG
helper) is declared in every build and calls it, so nothing may call Perf Mark either. Built with a switch on, this fails on purpose."""
import unittest, os, json
H = os.path.dirname(os.path.abspath(__file__)); ASSETS = os.path.join(H, "..", "..", "assets")
LOG_HELPERS = {"Log Line", "Perf Mark"}


def log_calls():
    out = []
    for f in sorted(os.listdir(ASSETS)):
        if not f.endswith(".json"):
            continue
        for a in json.load(open(os.path.join(ASSETS, f))).get("assets", []):
            graphs = [(fn["name"], fn.get("graph")) for fn in a.get("functions", [])] + [("EventGraph", a.get("event_graph"))]
            for name, g in graphs:
                if name in LOG_HELPERS:
                    continue
                for n in (g or {}).get("nodes", []):
                    if n.get("kind") == "call_self" and n.get("function") in LOG_HELPERS:
                        out.append("%s %s: %s -> %s" % (f, a.get("path"), name, n["function"]))
    return out


class NoReleaseLog(unittest.TestCase):
    def test_no_graph_writes_the_log(self):
        self.assertEqual(log_calls(), [])
