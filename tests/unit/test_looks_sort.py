"""Looks sorting, part 1: S_Look carries Created / Changed (Unix UTC seconds, int64), appended so older saves keep loading
(an older look brings 0 = unknown). Every make of S_Look sets both, none may leave a pin open (that would silently give 0)."""
import unittest, os, json, glob

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")
S_LOOK = "/Game/Mod/AltUI/S_Look"
# internal member names of the struct before the stamps were appended (saves match members by these names)
OLD_NAMES = {"Name": "Name_2_C31AEEC6DADBE7E8F13399D360845AB9", "Id": "Id_4_32936D368C68DF577F27AFF8F549B969",
             "Snap": "Snap_6_A993766F2E3E53CA51CAD1CCE8739C28"}


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)


def all_assets():
    for f in sorted(glob.glob(os.path.join(ASSETS, "*.json"))):
        yield f, json.load(open(f))


class LooksSortStamps(unittest.TestCase):
    def struct(self):
        for f, d in all_assets():
            for a in d["assets"]:
                if a.get("type") == "struct" and a["path"] == S_LOOK: return a
        raise AssertionError("S_Look not found")

    def test_fields_and_order(self):
        ms = self.struct()["members"]
        self.assertEqual([m["name"] for m in ms], ["Name", "Id", "Snap", "Created", "Changed"])
        self.assertEqual([m["type"] for m in ms[3:]], ["int64", "int64"])

    def test_old_member_names_stable(self):
        got = {m["name"]: m["internal_name"] for m in self.struct()["members"]}
        for k, v in OLD_NAMES.items(): self.assertEqual(got[k], v)

    def test_every_make_sets_both_stamps(self):
        n = 0
        for f, d in all_assets():
            for node in walk(d):
                if node.get("kind") == "make" and node.get("struct") == S_LOOK:
                    n += 1
                    for k in ("Name", "Id", "Snap", "Created", "Changed"):
                        self.assertIn(k, node.get("in", {}), "%s: make %s lacks %s" % (os.path.basename(f), node.get("id"), k))
        self.assertGreaterEqual(n, 5)



H = os.path.dirname(os.path.abspath(__file__))


def load(fname):
    with open(os.path.join(ASSETS, fname)) as f: return json.load(f)["assets"]


def mgr():
    return [a for f in ("30_manager.json", "50_manager_ui.json") for a in load(f) if a.get("path") == "/Game/Mod/AltUI/BP_AltUIManager"]


def fn_graph(name):
    names = {e.get("name") for a in mgr() for e in a.get("functions", [])}
    if name + " Body" in names: name += " Body"   # KEEP_SCROLL wrapper
    for a in mgr():
        for e in a.get("functions", []):
            if e.get("name") == name and e.get("graph"): return e["graph"]
    raise AssertionError("function %s not found" % name)


def has_fn(name): return any(e.get("name") == name for a in mgr() for e in a.get("functions", []))


class LooksSortOrder(unittest.TestCase):
    def test_variable_in_manager_and_settings_save(self):
        gm = open(os.path.join(H, "..", "..", "assets", "gen", "gen_manager.py")).read()
        self.assertEqual(gm.count('var("LooksSort", "int")'), 2, "manager + settings savegame")
        self.assertIn('("LooksSort", "LooksSort", "copy", None)', gm)
        names = {v["name"] for a in mgr() for v in a.get("variables", [])}
        for v in ("LooksSort", "LookOrder", "TmpInts"): self.assertIn(v, names)

    def test_functions_exist(self):
        for f in ("Look Order", "Look Before"): self.assertTrue(has_fn(f), f)
        ev = {n.get("name") for a in mgr() for n in a.get("event_graph", {}).get("nodes", []) if n.get("kind") == "custom_event"}
        for f in ("Test Look Order", "Test Set Look Stamps"): self.assertIn(f, ev)

    def test_rebuild_iterates_order_not_looks(self):
        g = fn_graph("Rebuild Looks")
        self.assertTrue([n for n in g["nodes"] if n.get("kind") == "call_self" and n.get("function") == "Look Order"])
        loops = [n for n in g["nodes"] if n.get("kind") == "foreach"]; self.assertEqual(len(loops), 1)
        src = loops[0]["in"]["Array"]
        gets = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(gets[src.split(".")[0][1:]].get("var"), "LookOrder")
        init = [n for n in g["nodes"] if n.get("function") == "Init" and n["id"] == "il"][0]
        self.assertEqual(init["in"]["index"], "@%s.Array Element" % loops[0]["id"])

    def test_look_order_uses_look_before(self):
        g = fn_graph("Look Order")
        self.assertTrue([n for n in g["nodes"] if n.get("function") == "Look Before"])

    def test_move_rows_only_in_custom(self):
        g = fn_graph("On Look Context")
        self.assertTrue([n for n in g["nodes"] if n.get("kind") == "get" and n.get("var") == "LooksSort"])


SORT_KEYS = ["Btn_LooksSort", "Sort_Custom", "Sort_NameAZ", "Sort_NameZA", "Sort_Newest", "Sort_Oldest", "Sort_Changed", "Sort_Unchanged", "Tip_LookCreated", "Tip_LookChanged"]


class LooksSortMenu(unittest.TestCase):
    def test_strings_in_all_languages(self):
        import sys; sys.path.insert(0, os.path.join(ASSETS, "gen"))
        import strings, strings_fr
        for k in SORT_KEYS:
            self.assertIn(k, strings.STRINGS, k); self.assertEqual(len(strings.STRINGS[k]), 7, k)   # en de zh ru es pl fr
            for t in strings.STRINGS[k]:
                self.assertTrue(t.strip(), k)
                for ch in "▾▸▶▼◀►▲△▽◂▴•": self.assertNotIn(ch, t, k)   # the panel font has no symbol glyphs
            self.assertIn(k, strings_fr.FR, k)
            for t in strings.STRINGS[k]: self.assertEqual(t.count("%s"), 1 if k in ("Btn_LooksSort", "Tip_LookCreated", "Tip_LookChanged") else 0, (k, t))

    def test_status_link_only_on_looks(self):
        g = fn_graph("Rebuild Status"); ns = {n["id"]: n for n in g["nodes"]}
        init = [n for n in g["nodes"] if n.get("function") == "Init" and n["in"].get("action") == "LooksSort"]
        self.assertEqual(len(init), 1)
        # reached only through the branch whose condition compares Page with Looks
        br = [n for n in g["nodes"] if n.get("id") == "bls"][0]
        cmp_ = ns[br["in"]["Condition"].split(".")[0][1:]] if "Condition" in br.get("in", {}) else None
        self.assertIsNotNone(cmp_); self.assertEqual(cmp_["in"]["B"], "Looks")

    def test_menu_wiring(self):
        self.assertTrue(has_fn("Open Looks Sort Menu")); self.assertTrue(has_fn("Set Looks Sort"))
        g = fn_graph("Open Looks Sort Menu")
        acts = {n["in"].get("action") for n in g["nodes"] if n.get("function") == "Init"}
        self.assertEqual(acts, {"LookSort%d" % i for i in range(7)} | {"Cancel"})
        # right click: On Link Context hands every link but RandomOutfit to On Menu Action, which opens the menu for LooksSort and sets the order for LookSort<n>
        ma = {n["id"]: n for n in fn_graph("On Menu Action")["nodes"]}
        self.assertEqual(ma["lks_a"]["function"], "Set Looks Sort"); self.assertEqual(ma["lks_p"]["in"]["InPrefix"], "LookSort")
        self.assertIn("Open Looks Sort Menu", {n.get("function") for n in ma.values()})


if __name__ == "__main__": unittest.main()
