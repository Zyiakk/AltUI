"""Main menu scene picker (assets/gen/menuscene.py): in the main menu's scenes and in AltUI's own loading scene the panel key opens the
picker instead of the panel; the loading scene is only opened with no level to load, and its "press any key" stays collapsed there
(a key press would otherwise open level None)."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")
P_GI = "/Game/Project/Classes/TKA_GameInstance"


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)


def load(name):
    with open(os.path.join(ASSETS, name), encoding="utf-8") as f: return json.load(f)


class MenuScene(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        doc = load("50_manager_ui.json")
        cls.fns = {o["name"]: o for o in walk(doc) if isinstance(o.get("graph"), dict) and "name" in o}
        cls.eg = next(o for o in walk(doc) if o.get("path", "").endswith("BP_AltUIManager"))["event_graph"]
        cls.stubs = {a["path"]: a for a in load("10_stubs.json")["assets"]}

    def nodes(self, fn): return {n["id"]: n for n in self.fns[fn]["graph"]["nodes"]}

    def test_key_goes_to_the_picker_in_a_scene_and_to_the_panel_elsewhere(self):
        self.assertIn(["kAny:Released", "bson", "skey"], self.eg["exec"])
        self.assertIn(["bson:else", "bkey", "bk", "tp"], self.eg["exec"])

    def test_scene_init_runs_in_the_menu_branch_only(self):
        self.assertIn(["cj:CastFailed", "mlds", "mfind", "msi"], self.eg["exec"])
        calls = [n.get("function") for n in self.eg["nodes"] if n.get("kind") == "call_self"]
        self.assertEqual(calls.count("Scene Init"), 1)

    def test_scene_init_needs_no_target_level_for_the_loading_scene(self):
        n = self.nodes("Scene Init")
        self.assertEqual(n["gln"]["var"], "Level Name"); self.assertEqual(n["none"]["in"]["B"], "None")
        self.assertEqual(n["own"]["function"], "BooleanAND")   # Loading AND no level -> AltUI's own visit

    def test_picker_rows(self):
        acts = [n["in"]["action"] for n in self.fns["Open Scene Menu"]["graph"]["nodes"] if n.get("function") == "Init" and "action" in n.get("in", {})]
        self.assertEqual(acts, ["Scene:Menu_Standing", "Scene:Menu_Sitting", "Scene:Menu_Level2", "Scene:Loading", "SceneCam", "SceneHide", "Cancel"])

    def test_loading_scene_is_opened_with_level_name_none(self):
        g = self.fns["Scene Open"]["graph"]; n = {x["id"]: x for x in g["nodes"]}
        self.assertEqual(n["sln"]["var"], "Level Name"); self.assertEqual(n["sln"]["in"]["Level Name"], "None")
        self.assertIn(["entry", "bl", "sln", "ol"], g["exec"])

    def test_tick_keeps_any_key_collapsed(self):
        n = self.nodes("Scene Tick")
        self.assertEqual(n["gak"]["var"], "TextBlock_AnyKey"); self.assertEqual(n["hd"]["in"]["InVisibility"], "Collapsed")
        self.assertTrue(any(c[:3] == ["tbpz:else", "ttik", "tstk"] for c in self.eg["exec"]))   # since 2026-10-16 after the paused check

    def test_menu_actions_reach_scene_action(self):
        g = self.fns["On Menu Action"]["graph"]
        self.assertIn(["bdrw:else", "cm", "blmp", "bscn"], g["exec"]); self.assertIn(["bscn", "scn_a"], g["exec"])   # blmp: other actions close the light submenu; drawer rows (Drw:) go first

    def test_close_menu_gives_the_loading_scene_its_cursor_back(self):
        self.assertEqual(self.nodes("Close Menu")["scu"]["in"]["show"], "false")
        n = self.nodes("Scene Cursor")   # only where the game shows no cursor: loading scene, or main menu with its menu hidden
        self.assertEqual(n["bl"]["in"]["Condition"], "@need.ReturnValue"); self.assertEqual(n["need"]["in"], {"A": "@gl.SceneLoad", "B": "@gh.SceneHidden"})
        g = self.fns["Scene Cursor"]["graph"]
        self.assertIn(["b:else", "bld", "go"], g["exec"]); self.assertIn(["bld:else", "fv"], g["exec"])   # hidden main menu: keys to the viewport

    def test_stubs(self):
        self.assertIn({"name": "Level Name", "type": "name"}, self.stubs[P_GI]["variables"])
        pawn = self.stubs["/Game/Project/Maps/Loading/LoadingPawn"]
        self.assertEqual({v["name"] for v in pawn["variables"]}, {"ui", "jodi", "offset z"})
        self.assertEqual([f["name"] for f in pawn["functions"]], ["Init"])
        self.assertIn("/Game/Project/UserInterface/MainMenuUI", self.stubs)
        self.assertEqual(self.stubs["/Game/Project/UserInterface/LoadingUI"]["variables"][0]["name"], "TextBlock_AnyKey")


if __name__ == "__main__":
    unittest.main()
