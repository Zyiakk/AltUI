"""Ragdoll mode: the middle mouse button turns the camera without screen edges (spec 2026-10-26)."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_options_cats import graph, calls


def g(name): return graph("50_manager_ui.json", name)


def fns(gr): return [n.get("function") for n in gr["nodes"]]


class MidLook(unittest.TestCase):
    def test_step_uses_the_middle_button(self):
        st = g("Ragdoll Mode Step"); js = json.dumps(st)
        self.assertIn("MiddleMouseButton", js)
        self.assertTrue(calls(st, "Rag Mid Begin")); self.assertTrue(calls(st, "Rag Mid End"))
        self.assertIn("IsInputKeyDown", fns(st))
        self.assertIn("RagMidLook", js)

    def test_begin_hides_the_cursor_and_goes_game_only(self):
        b = g("Rag Mid Begin"); f = fns(b); js = json.dumps(b)
        self.assertIn("SetInputMode_GameOnly", f); self.assertIn("GetMousePosition", f); self.assertIn("ShowMouseCursor", f)
        self.assertIn('"show": "false"', js); self.assertIn("RagMidX", js)

    def test_end_restores_cursor_mode_and_place(self):
        e = g("Rag Mid End"); f = fns(e); js = json.dumps(e)
        self.assertIn("SetInputMode_GameAndUIEx", f); self.assertIn("SetMouseLocation", f)
        self.assertIn('"show": "true"', js); self.assertIn("RagMidLook", js)

    def test_stop_free_cam_ends_it(self):
        s = g("Stop Free Cam"); js = json.dumps(s)
        self.assertIn("RagMidLook", js); self.assertIn("SetMouseLocation", fns(s))


if __name__ == "__main__": unittest.main()
