"""2026-10-11 package: pak name in every search, item pictures instead of rendered weapon pictures, ragdoll wheel step and slow
motion as options, quick menu: slow motion / stop time / hide Jodi. Time Tick never takes over from the game's own dilation."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)


def fns(name):
    with open(os.path.join(ASSETS, name), encoding="utf-8") as f:
        return {o["name"]: o for o in walk(json.load(f)) if isinstance(o.get("graph"), dict) and "name" in o}


class QuickWins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = fns("30_manager.json"); cls.u = fns("50_manager_ui.json")

    def nodes(self, d, fn): return {n["id"]: n for n in d[fn]["graph"]["nodes"]}

    def test_pak_name_searched_only_for_mod_pieces(self):
        for d, fn in ((self.m, "Filtered Items"), (self.u, "Look Matches"), (self.u, "Pose Matches"), (self.u, "Skin Row Passes"), (self.u, "Model Row Passes"), (self.u, "Sound Row Passes")):
            with self.subTest(fn=fn):
                n = self.nodes(d, fn)
                self.assertEqual(n["pkn"]["function"], "SelectString"); self.assertEqual(n["pkn"]["in"]["B"], "")
                self.assertTrue(n["pkn"]["in"]["bPickA"].endswith(".found"))
                self.assertTrue(any(x.get("function") == "ToLower" and x["in"].get("SourceString") == "@pkn.ReturnValue" for x in n.values()))   # it is one of the search sources

    def test_weapon_icon_switch_answers_nothing_missing(self):
        g = self.u["Weapon Icon"]["graph"]
        self.assertIn(["entry", "bnr", "rnone"], g["exec"])
        self.assertFalse(any(l[1].startswith("rnone.") for l in g["links"]))   # no tex, missing stays false: no photo is taken

    def test_time_tick_runs_every_tick_and_only_takes_over_from_1_or_own(self):
        n = self.nodes(self.u, "Time Tick")
        self.assertEqual(n["may"]["in"], {"A": "@c1.ReturnValue", "B": "@own.ReturnValue"})
        self.assertEqual(n["bo"]["in"]["Condition"], "@own.ReturnValue")
        eg = next(o for o in walk(json.load(open(os.path.join(ASSETS, "50_manager_ui.json")))) if str(o.get("path", "")).endswith("BP_AltUIManager"))["event_graph"]
        self.assertTrue(any(c[:2] == ["tbpz:else", "ttik"] for c in eg["exec"]))   # unpaused: everything
        self.assertIn(["tick", "tbpz", "tpzt", "tls0"], eg["exec"])   # paused (photo mode): Time Tick + the camera light

    def test_quick_items_run(self):
        g = self.u["Run Quick Item"]["graph"]; n = {x["id"]: x for x in g["nodes"]}
        for nid, fn in (("tsm", "Toggle Slow Mo"), ("tfz", "Toggle Freeze"), ("thj", "Toggle Hide Jodi")):
            self.assertEqual(n[nid]["function"], fn)

    def test_stopped_time_stops_cloth(self):
        """User report 2026-10-12: with time stopped the hair (NvCloth) kept moving - Toggle Freeze suspends / resumes cloth."""
        n = self.nodes(self.u, "Toggle Freeze"); self.assertEqual(n["cf"]["function"], "Freeze Cloth")
        fz = {x.get("function") for x in self.nodes(self.u, "Freeze Cloth").values()}
        self.assertTrue({"SuspendClothingSimulation", "ResumeClothingSimulation"} <= fz)

    def test_rag_lift_uses_the_option(self):
        n = self.nodes(self.u, "Rag Lift"); self.assertEqual(n["dz"]["in"]["B"], "@rwc.v")


if __name__ == "__main__":
    unittest.main()
