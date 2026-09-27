"""examples/AltUIMod_Example is a mod built the way MOD_UI.md describes: two tables on AltUI's row structs, one actor
that implements BPI_AltUIMod, started by the Blueprint Loader - and nothing of AltUI itself inside."""
import unittest, os, json, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "assets", "gen"))
import modui as mu

ASSETS = os.path.join(HERE, "..", "..", "assets")
MOD = "/Game/Mod/AltUIMod_Example"


def assets():
    with open(os.path.join(ASSETS, "87_modexample.json")) as f:
        return {a["path"]: a for a in json.load(f)["assets"]}


class Example(unittest.TestCase):
    def test_tables_use_altuis_structs(self):
        a = assets()
        self.assertEqual(a[MOD + "/AltUI_Entries"]["row_struct"], mu.ENTRY_STRUCT)
        self.assertEqual(a[MOD + "/AltUI_Fields"]["row_struct"], mu.FIELD_STRUCT)

    def test_every_field_type_once_and_valid(self):
        rows = assets()[MOD + "/AltUI_Fields"]["rows"]
        self.assertEqual(sorted({r["Type"] for r in rows.values()}), sorted(mu.TYPES))
        entries = assets()[MOD + "/AltUI_Entries"]["rows"]
        for r in rows.values():
            self.assertIn(r["Entry"], entries)
            if r["Type"] == "Slider": self.assertLess(r["Min"], r["Max"])
            if r["Type"] == "Choice": self.assertTrue(r["Options"])

    def test_actor_implements_the_interface(self):
        bp = assets()[MOD + "/BP_AltUIModExample"]
        self.assertEqual(bp.get("interfaces"), [mu.INTERFACE])
        for f in (mu.GET_VALUE, mu.GET_COLOR, mu.GET_TEXT): self.assertIn(f, [x["name"] for x in bp["functions"]])
        for e in (mu.ON_CHANGED, mu.ON_COLOR, mu.ON_TEXT):
            ev = [n for n in bp["event_graph"]["nodes"] if n.get("kind") == "event" and n.get("name") == e]
            self.assertEqual(len(ev), 1, e)
        entry = assets()[MOD + "/AltUI_Entries"]["rows"]
        self.assertTrue(all(r["Actor"].startswith(MOD + "/BP_AltUIModExample.") for r in entry.values()))

    def test_keeps_its_own_values(self):
        """The mod holds the values, so it saves them itself: loaded before the lamp exists, saved after every change."""
        a = assets()
        self.assertIn(MOD + "/SG_ExampleLamp", a)
        bp = a[MOD + "/BP_AltUIModExample"]; eg = bp["event_graph"]
        self.assertIn("LoadGameFromSlot", [n.get("function") for n in eg["nodes"]])
        save = [f for f in bp["functions"] if f["name"] == "Save"][0]["graph"]
        self.assertIn("SaveGameToSlot", [n.get("function") for n in save["nodes"]])
        saves = [n for n in eg["nodes"] if n.get("kind") == "call_self" and n.get("function") == "Save"]
        self.assertEqual(len(saves), 3, "number, colour and text changes each save")

    def test_started_by_the_loader_and_nothing_of_altui_inside(self):
        a = assets()
        self.assertIn(MOD + "/TKA_BlueprintLoader", a)
        self.assertFalse([p for p in a if p.startswith("/Game/Mod/AltUI/")])


if __name__ == "__main__":
    unittest.main()
