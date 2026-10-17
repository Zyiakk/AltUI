"""Every appearance tile menu offers "Rename mod..." for a piece that comes from a mod (Discord: the row was missing on
some appearance tiles - the hairstyle menu never had it). The row is conditional on the kind's own mod lookup."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")
MENUS = {"On Item Context": "Item Mod", "On Look Item Context": "Look Mod", "On Hair Context": "Hair Mod", "On Pose Context": "Pose Mod"}


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)


class RenameModRows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ASSETS, "50_manager_ui.json"), encoding="utf-8") as f:
            doc = json.load(f)
        cls.fns = {o["name"]: o for o in walk(doc) if isinstance(o.get("graph"), dict) and "name" in o}

    def test_each_appearance_menu_has_rename_mod(self):
        for menu, lookup in MENUS.items():
            with self.subTest(menu=menu):
                nodes = self.fns[menu]["graph"]["nodes"]
                self.assertTrue(any(n.get("function") == "Init" and n.get("in", {}).get("action") == "RenameMod" for n in nodes))
                self.assertTrue(any(n.get("kind") == "call_self" and n.get("function") == lookup for n in nodes))

    def test_weapon_menus_have_rename_mod(self):
        for menu, action, lookup in (("On Skin Context", "SkinRenameMod", "Skin Mod"), ("On Model Context", "ModelRenameMod", "Model Mod"), ("On Sound Context", "SoundRenameMod", "Sound Mod")):
            with self.subTest(menu=menu):
                nodes = self.fns[menu]["graph"]["nodes"]
                self.assertTrue(any(n.get("function") == "Init" and n.get("in", {}).get("action") == action for n in nodes))
                self.assertTrue(any(n.get("kind") == "call_self" and n.get("function") == lookup for n in nodes))
        for k in ("Skin", "Model", "Sound"):
            n = {x["id"]: x for x in self.fns["Rename %s Mod" % k]["graph"]["nodes"]}
            self.assertEqual(n["mr"]["in"], {"kind": "mod", "row": "@wm.mod", "cat": "Mods"})

    def test_weapon_mods_join_the_mod_list(self):
        with open(os.path.join(ASSETS, "30_manager.json"), encoding="utf-8") as f:
            m = {o["name"]: o for o in walk(json.load(f)) if isinstance(o.get("graph"), dict) and "name" in o}
        n = {x["id"]: x for x in m["Scan Mod Items"]["graph"]["nodes"]}
        self.assertEqual(n["bf"]["in"]["Condition"], "@fw.ReturnValue")
        self.assertEqual(n["wsw0"]["in"]["InPrefix"], "WeaponAltUI_")

    def test_pose_tiles_mark_sound(self):
        g = self.fns["Rebuild Poses Body"]["graph"]   # KEEP_SCROLL wrapper: the logic is in the body
        self.assertTrue(any(n.get("function") == "Set Sound Mark" for n in g["nodes"]))
        self.assertTrue(any(n.get("function") == "Pose Has Sound" for n in g["nodes"]))

    def test_rename_mod_action_is_dispatched(self):
        nodes = self.fns["Rename Mod Of Item"]["graph"]["nodes"]
        self.assertTrue(any(n.get("function") == "Context Mod" for n in nodes))


if __name__ == "__main__":
    unittest.main()
