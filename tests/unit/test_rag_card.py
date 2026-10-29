"""Ragdolls tab: one tile per figure (W_RagCard), joint / hand / eye rows striped alternately (play test 2026-10-26)."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_weapon_look_melee import function
from test_options_cats import calls, graph
import gen_widgets as gw


class RagCard(unittest.TestCase):
    def test_widget(self):
        a = next(x for x in json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json")))["assets"] if x["path"] == gw.W_RAGCARD)
        self.assertIn("Add Row", {f["name"] for f in a["functions"]})

    def test_rows_go_into_the_card(self):
        g = graph("50_manager_ui.json", "Rebuild Ragdolls"); n = {x["id"]: x for x in g["nodes"]}
        self.assertEqual(len(calls(g, "Add Rag Row")), 1)   # only the card itself goes into the panel
        self.assertEqual(n["cda"]["in"]["widget"], "@cd.AsW_RagCard")
        adds = calls(g, "Add Row"); self.assertGreater(len(adds), 10)   # head, joints, hands, eyes, poses
        stripes = [x for x in g["nodes"] if x.get("function") == "Set Stripe"]
        self.assertEqual(len(stripes), len(adds) - 2)   # all but the head row and the poses box

    def test_link_row_stripe_is_the_area_tint(self):
        a = next(x for x in json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json")))["assets"] if x["path"].endswith("/W_LinkRow"))
        self.assertIn("ColArea", json.dumps(a))

    def test_remove_is_the_last_link(self):
        g = graph("50_manager_ui.json", "Rebuild Ragdolls"); pairs = {(a, b) for c in g["exec"] for a, b in zip(c, c[1:])}
        self.assertIn(("bpn:else", "krw_cr"), pairs); self.assertIn(("krad", "cd_cr"), pairs)
        self.assertTrue(any((a, b) == ("kuad", "krw_cr") for a, b in pairs))   # after "release all" (and "attackable" before it)


class KeyCapture(unittest.TestCase):
    def test_lock_keys_do_not_end_the_wait(self):
        js = json.dumps(graph("40_widgets.json", "OnPreviewKeyDown"))
        for k in ("NumLock", "CapsLock", "ScrollLock"): self.assertIn('"%s"' % k, js)


if __name__ == "__main__": unittest.main()
