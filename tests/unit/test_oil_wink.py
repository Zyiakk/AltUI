"""2026-10-23 (spec 2026-10-23-oel-zwinkern-design): oiled skin (Jodi's own wet skin target, held by AltUI) and closing each eye
on its own (the game's blink animation once per lid in ABP_BodyScale)."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, asset
import face as fc

MGR = "/Game/Mod/AltUI/BP_AltUIManager"


def calls(g, f): return [n for n in g["nodes"] if n.get("function") == f]
def sets(g, v): return [n for n in g["nodes"] if n.get("kind") == "set" and n.get("var") == v]


class Oil(unittest.TestCase):
    def test_variables_and_setting(self):
        mv = {v["name"]: v for v in asset(MGR)["variables"]}
        self.assertEqual(mv["SkinOil"]["default"], "-1.0"); self.assertEqual(mv["OilGameTarget"]["default"], "-1.0")
        sv = {v["name"]: v for v in asset("/Game/Mod/AltUI/SG_AltUI")["variables"]}
        self.assertEqual(sv["SkinOil"]["default"], "-1.0")   # an older settings file: the game decides

    def test_jodi_stub(self):
        jodi = [a for a in asset_all("/Game/Project/Character/Jodi/Jodi")]
        self.assertTrue(any(v["name"] == "Skin Wet Alpha Target" for a in jodi for v in a.get("variables", [])))

    def test_apply_holds_and_gives_back(self):
        g = mgr_graph("Apply Skin Oil")
        held = sets(g, "Skin Wet Alpha Target"); self.assertEqual(len(held), 2)
        self.assertEqual(held[0]["in"]["Skin Wet Alpha Target"], "@go.SkinOil")            # ticked: ours
        self.assertEqual(held[1]["in"]["Skin Wet Alpha Target"], "@gg2.OilGameTarget")     # unticked: the game's back
        self.assertEqual([n["in"]["OilGameTarget"] for n in sets(g, "OilGameTarget")], ["@gt.Skin Wet Alpha Target", "-1.0"])

    def test_watch_every_second(self):
        self.assertTrue(calls(mgr_graph("Mutation Watch"), "Apply Skin Oil"))

    def test_row_on_the_skin_page(self):
        g = mgr_graph("Rebuild Look")
        inits = [n for n in calls(g, "Init") if n.get("in", {}).get("key") == "SkinOil"]; self.assertEqual(len(inits), 1)
        self.assertTrue(any(n["in"].get("B") == "Skin" for n in calls(g, "EqualEqual_NameName") if n["id"] == "iso"))

    def test_dispatch_and_row(self):
        g = mgr_graph("Face Row Changed"); self.assertTrue(calls(g, "Skin Oil Row Changed"))
        r = mgr_graph("Skin Oil Row Changed"); self.assertTrue(calls(r, "Apply Skin Oil")); self.assertTrue(sets(r, "FaceDirty"))
        self.assertEqual(sets(r, "SkinOil")[0]["in"]["SkinOil"], "@val.ReturnValue")


class OilInLooksAndPresets(unittest.TestCase):
    """Looks (S_Snapshot) and make-up presets (S_PresetColors) carry the oil as OilOn + Oil: an older one brings false = the game decides."""
    def test_struct_fields(self):
        for path in ("/Game/Mod/AltUI/S_Snapshot", "/Game/Mod/AltUI/S_PresetColors"):
            f = {p["name"]: p["type"] for p in asset(path)["members"]}
            self.assertEqual((f["OilOn"], f["Oil"]), ("bool", "float"), path)

    def test_taken_and_put_back(self):
        mk = [n for n in mgr_graph("Take Snapshot")["nodes"] if n.get("kind") == "make"][0]
        self.assertIn("OilOn", mk["in"]); self.assertIn("Oil", mk["in"])
        for f, src in (("Finish Apply Snapshot", "@bs.OilOn"), ("Preset Clicked", "@bpc.OilOn")):
            g = mgr_graph(f); sel = [n for n in calls(g, "SelectFloat") if n["in"].get("bPickA") == src]
            self.assertEqual(len(sel), 1, f); self.assertEqual(sel[0]["in"]["B"], "-1.0")   # off / older = the game decides
            self.assertTrue(calls(g, "Apply Skin Oil"), f)
        mk = [n for n in mgr_graph("Store Preset Colors")["nodes"] if n.get("kind") == "make"][0]
        self.assertIn("OilOn", mk["in"])


class Wink(unittest.TestCase):
    def test_entries(self):
        keys = [e[0] for e in fc.ENTRIES if e[1] == "FaceEyes"]
        self.assertEqual(keys[-3:], ["EyesClosed", "EyeClosedL", "EyeClosedR"])

    def test_apply_takes_the_larger_per_lid(self):
        g = mgr_graph("Apply Eyes Closed")
        self.assertEqual(sorted(n["var"] for n in g["nodes"] if n.get("kind") == "set"), ["EyeClosedL", "EyeClosedR"])
        self.assertEqual(len(calls(g, "FMax")), 2)   # each lid: max(both, its own)


def asset_all(path):
    from test_fol_tab import assets
    return [a for a in assets() if a.get("path") == path]


if __name__ == "__main__": unittest.main()
