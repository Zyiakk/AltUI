"""The chip row of the weapons tab must not depend on what ran before it.

Skin Groups reads the shared row lists SkinRows / ModelRows / SoundRows. Rebuild Weapons (left column) fills them with
every weapon in turn (Weapon Count Text), so after it they hold the last weapon's rows. Select Skin Group and the search
ran Rebuild Weapons right before Rebuild Weapon Chips: a mod that brings only a model or a sound lost its chip, one group
was left and the row was hidden (2026-10-13, ui-test-82). Rebuild Weapon Chips therefore fills all three lists itself.
"""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def find_fn(o, name):
    if isinstance(o, dict):
        if o.get("name") == name and isinstance(o.get("graph"), dict): return o
        for v in o.values():
            r = find_fn(v, name)
            if r: return r
    elif isinstance(o, list):
        for v in o:
            r = find_fn(v, name)
            if r: return r


class WeaponChips(unittest.TestCase):
    def test_chips_fill_their_own_row_lists(self):
        with open(os.path.join(ASSETS, "50_manager_ui.json"), encoding="utf-8") as f:
            g = find_fn(json.load(f), "Rebuild Weapon Chips")["graph"]
        nodes = {n["id"]: n for n in g["nodes"]}
        order = [x.split(":")[0] for x in g["exec"][0]]
        called = [nodes[i].get("function") for i in order if i in nodes and nodes[i]["kind"] == "call_self"]
        self.assertIn("Skin Groups", called)
        before = called[:called.index("Skin Groups")]
        for rows_fn in ("Skins For Weapon", "Models For Weapon", "Sounds For Weapon"):
            self.assertIn(rows_fn, before, rows_fn + " must run in Rebuild Weapon Chips before Skin Groups")
            n = next(nodes[i] for i in order if i in nodes and nodes[i].get("function") == rows_fn)
            self.assertEqual(nodes[n["in"]["weapon"][1:].split(".")[0]].get("var"), "CurrentWeapon")


if __name__ == "__main__":
    unittest.main()
