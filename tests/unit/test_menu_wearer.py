"""Main menu and loading scene: the figure there is a Jodi_Intro placed in the level (a Jodi_Base, not the pawn, not a Jodi). AltUI puts
body, face and colours on it through "Wearer" - so the manager must take the menu branch (cast to Jodi failed -> Load
Settings -> Find Menu Wearer), and none of the functions that put the saved look on may read "Player" (a Jodi_C,
None in the menu)."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")
P_JODI_BASE = "/Game/Project/Character/Jodi/Jodi_Base"
LOOK_FNS = ["Apply Saved Body", "Apply Body", "Apply Body Scales", "Apply Face", "Apply Saved Colors", "Apply All Item Colors",
            "Apply Item Colors", "Set Slot Color", "Apply Eye Colors", "Apply Makeup Colors", "Current Look Row", "Is Look Selected"]


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)


class MenuWearer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ASSETS, "50_manager_ui.json"), encoding="utf-8") as f:
            cls.doc = json.load(f)
        cls.fns = {o["name"]: o for o in walk(cls.doc) if isinstance(o.get("graph"), dict) and "name" in o}
        cls.eg = next(o for o in walk(cls.doc) if o.get("path", "").endswith("BP_AltUIManager"))["event_graph"]

    def test_menu_branch_loads_settings_then_looks_for_the_figure(self):
        self.assertIn(["cj:CastFailed", "mlds", "mfind"], self.eg["exec"])
        nodes = {n["id"]: n for n in self.eg["nodes"]}
        self.assertEqual(nodes["mlds"].get("function"), "Load Settings")
        self.assertEqual(nodes["mfind"].get("function"), "Find Menu Wearer")

    def test_game_branch_sets_wearer_and_goes_on_without_it(self):
        chain = next(c for c in self.eg["exec"] if c and c[0] == "bp")
        self.assertLess(chain.index("swr"), chain.index("isg"))
        self.assertIn(["cjb:CastFailed", "isg"], self.eg["exec"])   # a failed Wearer cast must not cost the panel

    def test_level_applies_the_look_at_once(self):
        """No level-load timers any more: the game dresses Jodi in her own BeginPlay (and on possession), before the
        manager exists - the look goes on at the end of BeginPlay, in the order body, underwear, colours, face."""
        nodes = {n["id"]: n for n in self.eg["nodes"]}
        timers = {n["in"].get("FunctionName") for n in self.eg["nodes"] if n.get("function") == "K2_SetTimer"}
        self.assertFalse(timers & {"Apply Saved Body", "Fix Loaded Underwear", "Apply Saved Colors", "Apply Face"})
        chain = next(c for c in self.eg["exec"] if c and c[0] == "bp")
        order = [nodes[i].get("function") for i in chain if nodes.get(i, {}).get("kind") == "call_self"]
        self.assertEqual(order[-4:], ["Apply Saved Body", "Fix Loaded Underwear", "Apply Saved Colors", "Apply Face"])
        self.assertLess(order.index("Build Catalog"), order.index("Fix Loaded Underwear"))   # Worn In Slot needs the catalog

    def test_find_menu_wearer_searches_jodi_base_and_retries(self):
        g = self.fns["Find Menu Wearer"]["graph"]; nodes = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(nodes["ga"]["in"]["ActorClass"], P_JODI_BASE)
        timers = {n["in"]["FunctionName"] for n in g["nodes"] if n.get("function") == "K2_SetTimer"}
        self.assertEqual(timers, {"Find Menu Wearer"})   # only the retry: the loading scene can be over in two seconds
        chain = next(c for c in g["exec"] if c and c[0] == "entry")
        order = [nodes[i].get("function") for i in chain if nodes.get(i, {}).get("kind") == "call_self"]
        self.assertEqual(order, ["Apply Saved Body", "Apply Saved Colors", "Apply Face"])   # body first: Apply Body re-applies the game's make-up

    def test_look_functions_do_not_read_player(self):
        for name in LOOK_FNS:
            with self.subTest(fn=name):
                g = self.fns[name]["graph"]
                self.assertFalse([n for n in g["nodes"] if n.get("kind") == "get" and n.get("var") == "Player"], name)


class MenuSpawn(unittest.TestCase):
    """The spawners wait for a Jodi pawn - in the menu scenes the pawn is Menu_Pawn, so without a menu path of their own
    the manager never came to be there (and Find Menu Wearer never ran)."""
    def check(self, json_name):
        with open(os.path.join(ASSETS, json_name), encoding="utf-8") as f:
            eg = next(o for o in walk(json.load(f)) if "event_graph" in o)["event_graph"]
        nodes = {n["id"]: n for n in eg["nodes"]}
        self.assertEqual(nodes["lvl"].get("function"), "GetCurrentLevelName")
        self.assertEqual(nodes["menu"]["in"]["InPrefix"], "Menu_")
        self.assertEqual(nodes["load"]["in"]["B"], "Loading")   # the loading scene (Loading.umap) shows the same figure
        self.assertEqual(nodes["bm"]["in"]["Condition"], "@or.ReturnValue")
        self.assertIn(["cj:CastFailed", "lvl"], eg["exec"])
        self.assertIn(["lvl", "bm"], eg["exec"])   # GetCurrentLevelName is impure: off the exec chain it is pruned
        self.assertIn(["bm", "ld"], eg["exec"])   # a menu scene goes on to the spawn like a Jodi pawn

    def test_loader_entry(self):
        self.check("60_bploader.json")

    def test_hook(self):
        self.check("20_hook.json")


if __name__ == "__main__":
    unittest.main()
