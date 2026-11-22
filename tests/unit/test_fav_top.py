"""Options > Tiles "Show favourites on top of everything" (2026-11-22): stored inverted (NoFavBlock, on by default). Off: no
favourites block in any of the five lists that have one. On together with "only favourites": the block is the whole list - the
same pieces are not listed a second time below it (Clothes, Appearance)."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_options_cats import graph
from strings import STRINGS
import strings_fr, gen_manager as gm, gen_widgets as gw


def g(name): return graph("50_manager_ui.json", name)
def nodes(gr): return {n["id"]: n for n in gr["nodes"]}
def chain_of(gr, a): return next(c for c in gr["exec"] if c[0] == a)


class FavTop(unittest.TestCase):
    def test_setting_and_strings(self):
        self.assertIn(("NoFavBlock", "NoFavBlock", "copy", None), gm.SETTINGS)
        self.assertEqual(len(STRINGS["Lbl_FavTop"]), 7); self.assertTrue(all(STRINGS["Lbl_FavTop"]))
        self.assertIn("RowFavTop", gw.OPT_CAT_ROWS["Tiles"])

    def test_block_needs_the_option_in_every_list(self):
        for name, cond in (("Rebuild Hair", "ffa"), ("Rebuild Poses", "fok"), ("Rebuild Weapon Skins", "fok"), ("Rebuild Look", "fok")):
            n = nodes(g(name))
            self.assertEqual(n["bf"]["in"]["Condition"], "@%s.ReturnValue" % cond, name)
            self.assertEqual(n[cond]["in"]["B"], "@ftop.ReturnValue", name)
            self.assertEqual(n["ftop"]["function"], "Not_PreBool"); self.assertEqual(n["ftop"]["in"]["A"], "@gfnt.NoFavBlock", name)
        n = nodes(g("Rebuild List"))
        self.assertEqual(n["fbr"]["in"]["Condition"], "@ffvt.ReturnValue"); self.assertEqual(n["ffvt"]["in"], {"A": "@ffv.yes", "B": "@ftop.ReturnValue"})

    def test_clothes_only_favourites_shows_the_block_alone(self):
        gr = g("Rebuild List"); n = nodes(gr)
        self.assertEqual(n["bofo"]["in"]["Condition"], "@of.yes")
        c = chain_of(gr, "fl:Completed"); self.assertEqual(c[:3], ["fl:Completed", "bofo", "slh"], "after the block: straight to the end, no 'All' heading, no second pass")
        self.assertEqual(chain_of(gr, "bofo:else")[-1], "ci0", "without the filter the list follows as before")

    def test_look_only_favourites_shows_the_block_alone(self):
        gr = g("Rebuild Look"); n = nodes(gr)
        self.assertEqual(n["be"]["in"]["Condition"], "@pe2.ReturnValue"); self.assertEqual(n["pe2"]["in"], {"A": "@pe.yes", "B": "@nonly.ReturnValue"})
        self.assertEqual(n["onlyb"]["in"], {"A": "@gofl.LookOnlyFav", "B": "@ftop.ReturnValue"})
        self.assertEqual(n["slav"]["function"], "Set Look All Visible"); self.assertEqual(n["allv"]["in"], {"A": "@gt0.ReturnValue", "B": "@nonly.ReturnValue"})
        c = chain_of(gr, "ff:Completed"); self.assertLess(c.index("sfv"), c.index("slav"))

    def test_options_wiring(self):
        n = nodes(g("Rebuild Fav Top Option")); self.assertEqual(n["s"]["in"]["on"], "@on.ReturnValue"); self.assertEqual(n["on"]["in"]["A"], "@gn.NoFavBlock")
        gr = g("Poll Fav Top Option"); n = nodes(gr)
        self.assertEqual(n["s"]["in"], {"NoFavBlock": "@noff.ReturnValue"}); self.assertEqual(chain_of(gr, "entry"), ["entry", "b", "s", "sv"])
        ro = g("Rebuild Options"); self.assertIn("Rebuild Fav Top Option", [x.get("function") for x in ro["nodes"]])
        common = chain_of(ro, "entry"); self.assertEqual(common[-1], "rfto", "set in every category, before the category branches - the poll reads it everywhere")
        self.assertTrue(any(c[0] == "rfto" and c[1].startswith("boc_") for c in ro["exec"]))
        self.assertTrue(any("Poll Fav Top Option" == x.get("function") for a in json.load(open(os.path.join(H, "..", "..", "assets", "50_manager_ui.json")))["assets"]
                            for x in ((a.get("event_graph") or {}).get("nodes", []))), "polled while the Options page is open")
        panel = json.dumps(json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json"))))
        for w in ("OptFavTop", "LblFavTop", "Set Fav Top Option", "Get Fav Top Option", "Set Look All Visible"): self.assertIn(w, panel)


if __name__ == "__main__":
    unittest.main()
