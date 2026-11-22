"""A mod greys out a single field (internal design notes): BPI_AltUIMod's
Get AltUI Greyed(Key) -> Greyed, asked with the values for every field that has one, the row greyed and locked like a page
without its actor; presets untouched; the quick menu's greyed toggles / buttons greyed and inert. An older interface copy
(no such function) answers false = not greyed."""
import unittest, os, json, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "assets", "gen"))
import modui as mu

ASSETS = os.path.join(HERE, "..", "..", "assets")
BPI = "/Game/Mod/AltUI/BPI_AltUIMod"


def load(fname):
    with open(os.path.join(ASSETS, fname)) as f:
        return json.load(f)["assets"]


def fn_graph(name, files=("30_manager.json", "50_manager_ui.json")):
    if name + " Body" in {e.get("name") for f in files for a in load(f) for e in a.get("functions", [])}: name += " Body"
    for f in files:
        for a in load(f):
            for e in a.get("functions", []):
                if e.get("name") == name and e.get("graph"): return e["graph"]
    raise AssertionError("function %s not found" % name)


def nodes(g, **kw):
    return [n for n in g["nodes"] if all(n.get(k) == v for k, v in kw.items())]


def in_exec(g, node_id):
    return any(node_id == s.split(":")[0] for chain in g.get("exec", []) for s in chain)


def modfield():
    return [a for a in load("40_widgets.json") if a.get("path", "").endswith("/W_ModField")][0]


def wfn(name):
    return [f for f in modfield()["functions"] if f["name"] == name][0]


class Contract(unittest.TestCase):
    def test_name(self):
        self.assertEqual(mu.GET_GREYED, "Get AltUI Greyed")
        self.assertEqual(mu.GREYED_SKIP, ["Header", "Info", "Tab"])   # every other type has a value and is asked

    def test_interface_function(self):
        bpi = [a for a in load("30_manager.json") if a.get("path") == BPI][0]
        f = [x for x in bpi["functions"] if x["name"] == mu.GET_GREYED]
        self.assertEqual(len(f), 1)
        self.assertEqual([(p["name"], p["type"]) for p in f[0]["inputs"]], [("Key", "name")])
        self.assertEqual([(p["name"], p["type"]) for p in f[0]["outputs"]], [("Greyed", "bool")])
        self.assertEqual(bpi["functions"][-1]["name"], mu.GET_GREYED, "added last: the older functions keep their place")


class Page(unittest.TestCase):
    def test_asked_with_the_values(self):
        g = fn_graph("Poll Mods")
        m = nodes(g, kind="message", function=mu.GET_GREYED)
        self.assertEqual(len(m), 1); self.assertEqual(m[0]["class"], BPI); self.assertTrue(in_exec(g, m[0]["id"]))
        sg = nodes(g, function="Set Greyed"); self.assertEqual(len(sg), 1); self.assertTrue(in_exec(g, sg[0]["id"]))
        self.assertEqual(sg[0]["in"]["greyed"], "@%s.Greyed" % m[0]["id"])

    def test_not_for_info_header_tab(self):
        g = fn_graph("Poll Mods")
        skipped = {n["in"]["B"] for n in g["nodes"] if n.get("function") == "EqualEqual_NameName" and n.get("in", {}).get("B") in mu.GREYED_SKIP}
        self.assertEqual(skipped, set(mu.GREYED_SKIP))

    def test_one_message_per_field_per_poll(self):
        """As cheap as the Get calls: the question sits in the field loop of Poll Mods, nowhere else on the page."""
        for f in ("Rebuild Mod Fields", "Mod Page Layout", "Capture Mod Values", "Apply Mod Values"):
            self.assertFalse(nodes(fn_graph(f), kind="message", function=mu.GET_GREYED), f)


class Widget(unittest.TestCase):
    def test_set_greyed(self):
        names = {f["name"] for f in modfield()["functions"]}
        for f in ("Set Greyed", "Set Enabled", "Apply Enabled"): self.assertIn(f, names)
        self.assertEqual([(p["name"], p["type"]) for p in wfn("Set Greyed")["inputs"]], [("greyed", "bool")])
        vs = {v["name"] for v in modfield()["variables"]}
        self.assertIn("Greyed", vs); self.assertIn("Live", vs)

    def test_same_look_as_a_missing_actor(self):
        """Set Enabled (actor) and Set Greyed (mod) both end in Apply Enabled: SetIsEnabled + opacity 0.4, enabled = Live and not Greyed."""
        ap = wfn("Apply Enabled")["graph"]
        self.assertTrue(nodes(ap, function="SetIsEnabled")); self.assertTrue(nodes(ap, function="SetRenderOpacity"))
        self.assertTrue(any(n.get("in", {}).get("B") == "0.4" for n in ap["nodes"]))
        self.assertTrue(nodes(ap, function="Not_PreBool")); self.assertTrue(nodes(ap, function="BooleanAND"))
        for f in ("Set Enabled", "Set Greyed"):
            g = wfn(f)["graph"]; c = nodes(g, kind="call_self", function="Apply Enabled")
            self.assertEqual(len(c), 1, f); self.assertTrue(in_exec(g, c[0]["id"]), f)
            self.assertFalse(nodes(g, function="SetIsEnabled"), f)

    def test_only_on_change(self):
        """Poll Mods asks every tick: the widget only redraws when the answer changes."""
        g = wfn("Set Greyed")["graph"]
        self.assertTrue(nodes(g, function="NotEqual_BoolBool"))


class Quick(unittest.TestCase):
    def test_greyed_toggle_shows_greyed(self):
        g = fn_graph("Quick Item Live")
        m = nodes(g, kind="message", function=mu.GET_GREYED); self.assertEqual(len(m), 1); self.assertTrue(in_exec(g, m[0]["id"]))

    def test_greyed_toggle_does_nothing(self):
        g = fn_graph("Run Quick Item")
        m = nodes(g, kind="message", function=mu.GET_GREYED); self.assertEqual(len(m), 1); self.assertTrue(in_exec(g, m[0]["id"]))
        self.assertTrue(any(n.get("in", {}).get("B") == "modfield" for n in g["nodes"]), "only fields are asked, actions are no fields")


class Presets(unittest.TestCase):
    def test_presets_unchanged(self):
        for f in ("Capture Mod Values", "Apply Mod Values", "Shipped To Tmp"):
            self.assertFalse(nodes(fn_graph(f), kind="message", function=mu.GET_GREYED), f)


class Example(unittest.TestCase):
    def test_example_greys_brightness_while_the_light_is_off(self):
        a = {x["path"]: x for x in load("87_modexample.json")}
        bp = a["/Game/Mod/AltUIMod_Example/BP_AltUIModExample"]
        f = [x for x in bp["functions"] if x["name"] == mu.GET_GREYED]; self.assertEqual(len(f), 1)
        g = f[0]["graph"]
        self.assertTrue(any(n.get("in", {}).get("B") == "Brightness" for n in g["nodes"]))
        self.assertTrue(any(n.get("var") == "LightOn" for n in g["nodes"]))


class Docs(unittest.TestCase):
    def test_mod_ui_md(self):
        with open(os.path.join(HERE, "..", "..", "MOD_UI.md")) as f: s = f.read()
        self.assertIn("`Get AltUI Greyed (Key) -> Greyed`", s)
        self.assertIn("Greying out a field", s)


if __name__ == "__main__":
    unittest.main()
