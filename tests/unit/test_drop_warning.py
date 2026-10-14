"""Warning before dropping very many pickup actors (docs/specs/2026-10-15-drop-warning-design.md): the number of actors
"Discard all" creates, the threshold, the window and its three ways."""
import json, os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "assets", "gen"))
import inventory as inv


class DropActors(unittest.TestCase):
    def test_actors_are_packs_rounded_up(self):
        self.assertEqual(inv.drop_actors(50000, 30), 1667)
        self.assertEqual(inv.drop_actors(29, 30), 1)
        self.assertEqual(inv.drop_actors(30, 30), 1)
        self.assertEqual(inv.drop_actors(31, 30), 2)
        self.assertEqual(inv.drop_actors(0, 30), 0)

    def test_pick_zero_counts_as_one(self):
        self.assertEqual(inv.drop_actors(7, 0), 7)
        self.assertEqual(inv.drop_actors(7, 1), 7)

    def test_threshold(self):
        self.assertEqual(inv.DROP_WARN_ACTORS, 100)
        self.assertFalse(inv.drop_warns(99 * 30, 30))
        self.assertTrue(inv.drop_warns(99 * 30 + 1, 30))   # 100 actors
        self.assertTrue(inv.drop_warns(100, 0))
        self.assertFalse(inv.drop_warns(99, 1))


class DropStrings(unittest.TestCase):
    def test_all_languages(self):
        import strings
        rows = strings.rows()
        for k in ("Drop_Warn_Title", "Drop_Warn_Text", "Drop_Warn_Destroy", "Drop_Warn_Drop", "Menu_Cancel"):
            for lang in strings.LANGS:
                with self.subTest(key=k, lang=lang):
                    t = rows[k][lang]; self.assertTrue(t)
                    if k == "Drop_Warn_Text": self.assertEqual((t.count("%o"), t.count("%n")), (1, 1))


def _walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from _walk(v)
    elif isinstance(o, list):
        for v in o: yield from _walk(v)


class DropManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "50_manager_ui.json"), encoding="utf-8") as f:
            cls.fns = {o["name"]: o for o in _walk(json.load(f)) if isinstance(o.get("graph"), dict) and "name" in o}

    def nodes(self, fn): return {n["id"]: n for n in self.fns[fn]["graph"]["nodes"]}
    def calls(self, fn, target): return [n for n in self.fns[fn]["graph"]["nodes"] if n.get("function") == target]


class DropAll(DropManager):
    def test_drop_all_loops_over_actors_not_pieces(self):
        n = self.nodes("Inv Drop All")
        self.assertEqual(n["fl"]["in"]["Last Index"], "@gn.InvDropN")            # actors, kept before the loop: ForLoop re-reads
        self.assertEqual(n["sn"]["in"]["InvDropN"], "@dv.ReturnValue")            # Last Index each round, the bag count shrinks
        self.assertEqual(n["dv"]["function"], "Divide_IntInt"); self.assertEqual(n["dv"]["in"]["B"], "@pk.ReturnValue")
        self.assertEqual(n["pk"]["in"]["B"], "1")                                  # pack 0 counts as 1
        self.assertEqual(len(self.calls("Inv Drop All", "Drop Item")), 1)
        self.assertIn(["entry", "ir", "sn", "fl", "x"], self.fns["Inv Drop All"]["graph"]["exec"])   # Inv Row is not pure

    def test_action_switches_at_the_threshold(self):
        n = self.nodes("Inv Action")
        self.assertEqual(n["a_dropallge"]["function"], "GreaterEqual_IntInt"); self.assertEqual(n["a_dropallge"]["in"]["B"], str(inv.DROP_WARN_ACTORS))
        self.assertEqual(n["a_dropallx"]["function"], "Inv Drop All")
        self.assertEqual(n["a_dropallsw"]["function"], "Show Drop Warning")
        self.assertEqual(n["a_dropallsw"]["in"]["pieces"], "@bcn.count")
        ex = self.fns["Inv Action"]["graph"]["exec"]
        self.assertIn(["a_dropallb", "a_dropallbw", "a_dropallsi", "a_dropallsw"], ex)
        self.assertIn(["a_dropallbw:else", "a_dropallx"], ex)
        self.assertFalse(any(x.get("name") == "ForLoop" for x in self.fns["Inv Action"]["graph"]["nodes"]))


class DropWindow(DropManager):
    def test_window_text_and_links(self):
        n = self.nodes("Show Drop Warning")
        self.assertEqual(n["ro"]["in"]["From"], "%o"); self.assertEqual(n["rn"]["in"]["From"], "%n")
        acts = [n["li%d" % i]["in"]["action"] for i in range(3)]
        self.assertEqual(acts, ["DropWarnCancel", "DropWarnDestroy", "DropWarnDrop"])
        self.assertEqual(n["atv"]["in"]["ZOrder"], "150")
        self.assertFalse(self.calls("Show Drop Warning", "SetInputMode_UIOnlyEx"))   # the panel keeps the keyboard

    def test_menu_actions(self):
        import gen_manager_ui as m
        acts = {a: f for a, f, _ in m.MENU_ACTIONS}
        self.assertEqual(acts["DropWarnCancel"], "Drop Warn Cancel"); self.assertEqual(acts["DropWarnDestroy"], "Drop Warn Destroy"); self.assertEqual(acts["DropWarnDrop"], "Drop Warn Drop")

    def test_destroy_consumes_everything(self):
        c = self.calls("Drop Warn Destroy", "Consume Item")[0]
        self.assertEqual(c["in"]["item name"], "@gi.DropWarnItem"); self.assertEqual(c["in"]["num"], "@cn.count")
        self.assertFalse(self.calls("Drop Warn Destroy", "Drop Item"))
        self.assertTrue(self.calls("Drop Warn Destroy", "Close Drop Warning")); self.assertTrue(self.calls("Drop Warn Destroy", "Rebuild Inventory"))

    def test_drop_anyway_and_cancel(self):
        self.assertEqual(self.calls("Drop Warn Drop", "Inv Drop All")[0]["in"]["item"], "@gi.DropWarnItem")
        self.assertTrue(self.calls("Drop Warn Drop", "Close Drop Warning")); self.assertTrue(self.calls("Drop Warn Cancel", "Close Drop Warning"))
        self.assertFalse(self.calls("Drop Warn Cancel", "Consume Item")); self.assertFalse(self.calls("Drop Warn Cancel", "Inv Drop All"))

    def test_esc_and_panel_close_take_it_along(self):
        ex = self.fns["Panel Key Close"]["graph"]["exec"]
        self.assertIn(["entry", "dwo", "bdw", "cdw"], ex)              # Esc with the window open: only the window (Drop Warn Open is not pure)
        self.assertTrue(self.calls("Close Panel", "Close Drop Warning"))
        self.assertTrue(self.calls("Close Drop Warning", "IsInViewport"))


if __name__ == "__main__":
    unittest.main()
