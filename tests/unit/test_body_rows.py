"""The game has only chest and waist morphs (Female_Morph_Breasts / Female_Morph_Waist); Makeup_Save.Hip and the
mirror's OptionRow_Hip are unused remnants. AltUI 1.1.0 showed a hip slider that changed nothing (Steam comment
2026-09-17). The UI must not offer it any more; the Hip field stays in S_Snapshot so 1.1.0 look saves still load."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
from strings import STRINGS
ASSETS = os.path.join(H, "..", "..", "assets")


def asset(file, suffix):
    return next(a for a in json.load(open(os.path.join(ASSETS, file)))["assets"] if a["path"].endswith(suffix))


def widget_names(node):
    yield node["name"]
    for c in node.get("children", []): yield from widget_names(c)


class BodyRows(unittest.TestCase):
    def test_panel_has_no_hip_row(self):
        names = set(widget_names(asset("40_widgets.json", "/W_AltUI")["widget_tree"]))
        self.assertTrue({"RowBreast", "SldBreast", "RowWaist", "SldWaist"} <= names)
        self.assertEqual({n for n in names if "Hip" in n}, set())

    def test_body_values_are_breast_and_waist(self):
        fns = {f["name"]: f for f in asset("40_widgets.json", "/W_AltUI")["functions"]}
        self.assertEqual([p["name"] for p in fns["Get Body Values"]["outputs"]], ["breast", "waist"])
        self.assertEqual([p["name"] for p in fns["Set Body Values"]["inputs"]], ["breast", "waist"])

    def test_no_hip_string(self):
        self.assertNotIn("Lbl_Hip", STRINGS); self.assertIn("Lbl_Waist", STRINGS)

    def test_snapshot_keeps_hip_field(self):
        members = [m["name"] for m in asset("30_manager.json", "/S_Snapshot")["members"]]
        self.assertEqual(members[6:9], ["Boobs", "Waist", "Hip"])   # save compatibility with 1.1.0 AltUI_Looks.sav


if __name__ == "__main__": unittest.main()
