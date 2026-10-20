"""2026-10-20: search box on the Coiffure tab - above the tiles (does not scroll away), filters both passes of Rebuild Hair,
x clears it, "Show in tab" clears it before the jump."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)


def load(name):
    with open(os.path.join(ASSETS, name), encoding="utf-8") as f: return json.load(f)


def fns(doc): return {o["name"]: o for o in walk(doc) if isinstance(o.get("graph"), dict) and "name" in o}


class HairSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wdoc = load("40_widgets.json"); cls.u = fns(load("50_manager_ui.json")); cls.w = fns(cls.wdoc)

    def nodes(self, fn): return {n["id"]: n for n in self.u[fn]["graph"]["nodes"]}

    def test_search_box_sits_outside_the_scroll(self):
        page = next(o for o in walk(self.wdoc) if o.get("name") == "HairPage")
        names = [c.get("name") for c in page["children"]]
        self.assertEqual(names, ["HairFilters", "HairScroll"])
        self.assertIn("HairSearch", {o.get("name") for o in walk(page["children"][0])})

    def test_matches_searches_shown_row_mod_and_pak(self):
        n = self.nodes("Hair Matches")
        srcs = {x["in"]["SourceString"] for x in n.values() if x.get("function") == "ToLower"}
        self.assertTrue({"@dn.s", "@rs.ReturnValue", "@mcp.s", "@mds.ReturnValue", "@pkn.ReturnValue"} <= srcs)
        self.assertEqual(n["dn"]["in"]["kind"], "hair"); self.assertEqual(n["imd"]["function"], "Hair Mod")
        self.assertTrue(n["pkn"]["in"]["bPickA"].endswith(".found"))

    def test_rebuild_filters_both_passes(self):
        g = self.u["Rebuild Hair Body"]["graph"]; n = {x["id"]: x for x in g["nodes"]}   # Rebuild Hair = panel guard around it
        self.assertEqual(n["ffm"]["function"], "Hair Matches"); self.assertEqual(n["ffa"]["in"]["B"], "@ffm.yes"); self.assertEqual(n["bf"]["in"]["Condition"], "@ffa.ReturnValue")
        self.assertEqual(n["efm"]["function"], "Hair Matches"); self.assertEqual(n["be"]["in"]["Condition"], "@efm.yes")
        self.assertTrue(any(c[:3] == ["fe", "be", "th_tp"] or c[:2] == ["fe", "be"] for c in g["exec"]))
        self.assertEqual(n["xi"]["in"]["action"], "ClearHairSearch")

    def test_key_up_forwards_hair_search(self):
        ku = next(o for o in walk(self.wdoc) if o.get("name") == "OnKeyUp" and any(x.get("function") == "On Hair Search Changed" for x in o["graph"]["nodes"]))
        self.assertTrue(any("sch" in c for c in ku["graph"]["exec"]))

    def test_go_to_item_clears_hair_search(self):
        g = self.u["Go To Item"]["graph"]
        self.assertTrue(any(c[:6] == ["hh", "hk", "hcs", "phs", "hsp", "hsc"] or "hcs" in c and "phs" in c for c in g["exec"]))


if __name__ == "__main__":
    unittest.main()
