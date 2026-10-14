"""Focus Guard: with the panel open the keyboard focus stays in AltUI, so Esc never reaches the game's pause menu. A click that sets
no focus itself gives it to the leaf-most focusable widget under the mouse (the game viewport beside the panel, on menu rows,
hex-bar buttons), and the palette's Close Frame focuses a LastButton that may be gone."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)


class FocusGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ASSETS, "50_manager_ui.json"), encoding="utf-8") as f:
            cls.fns = {o["name"]: o for o in walk(json.load(f)) if isinstance(o.get("graph"), dict) and "name" in o}
        with open(os.path.join(ASSETS, "40_widgets.json"), encoding="utf-8") as f:
            panel = next(o for o in walk(json.load(f)) if str(o.get("path", "")).endswith("/W_AltUI"))
        cls.panel = {f["name"]: f for f in panel["functions"]}
        cls.g = cls.fns["Focus Guard"]["graph"]
        cls.nodes = {n["id"]: n for n in cls.g["nodes"]}

    def test_runs_every_frame_without_camera_mode(self):
        cam = self.fns["Cam Tick"]["graph"]
        chain = next(c for c in cam["exec"] if c[0] == "b2:else")
        self.assertEqual(chain[-1], "fg"); self.assertEqual(next(n for n in cam["nodes"] if n["id"] == "fg")["function"], "Focus Guard")

    def test_only_with_panel_open_and_no_other_input_owner(self):
        s = json.dumps(self.g)
        for v in ("PanelOpen", "QuickOpen", "VerWarn"):
            self.assertIn('"%s"' % v, s)
        self.assertIn(["entry", "bon", "bvw", "bvi"], self.g["exec"])
        self.assertIn(["bvw:else", "bh"], self.g["exec"]); self.assertIn(["bvi:else", "bh"], self.g["exec"])   # warning shown: nothing
        self.assertEqual(self.nodes["vwi"]["function"], "IsInViewport")

    def test_waits_while_a_mouse_button_is_held(self):
        keys = sorted(n["in"]["Key"] for n in self.g["nodes"] if n.get("function") == "IsInputKeyDown")
        self.assertEqual(keys, ["LeftMouseButton", "MiddleMouseButton", "RightMouseButton"])
        self.assertTrue(any(c[0] == "bh:else" for c in self.g["exec"]))
        self.assertFalse(any(c[0] == "bh" and len(c) > 1 for c in self.g["exec"]))   # held: nothing happens

    def test_focus_goes_to_the_panel_hex_field_allowed_with_palette(self):
        self.assertIn(["bh:else", "bmv", "bmd"], self.g["exec"]); self.assertIn(["bmv:else", "bco"], self.g["exec"]); self.assertIn(["bmd:else", "bco"], self.g["exec"]); self.assertIn(["bco", "bhx"], self.g["exec"]); self.assertIn(["bhx:else", "bin"], self.g["exec"]); self.assertIn(["bco:else", "bin"], self.g["exec"])
        self.assertIn(["bin:else", "fpn"], self.g["exec"]); self.assertEqual(self.nodes["fpn"]["function"], "Focus Panel")
        self.assertNotIn("Paletter", json.dumps(self.g))   # the game's palette handles no Esc: focus there sends Esc to the game

    def test_panel_esc_closes_only_the_palette(self):
        g = self.fns["Panel Key Close"]["graph"]; nodes = {n["id"]: n for n in g["nodes"]}
        self.assertIn(["bdw:else", "b", "cc"], g["exec"]); self.assertIn(["b:else", "cp"], g["exec"])   # after the drop warning (test_drop_warning)
        self.assertEqual(nodes["cc"]["function"], "Close Color"); self.assertEqual(nodes["cp"]["function"], "Close Panel")
        self.assertIn("ColorOpen", json.dumps(g))

    def test_panel_key_up_hands_esc_to_panel_key_close(self):
        n = next(n for n in self.panel["OnKeyUp"]["graph"]["nodes"] if n.get("id") == "cl")
        self.assertEqual(n["function"], "Panel Key Close"); self.assertEqual(n["in"]["esc"], "@esc.ReturnValue")

    def test_color_keys_focus_the_panel(self):
        g = self.fns["Focus Color Keys"]["graph"]
        self.assertTrue(any(n.get("function") == "SetKeyboardFocus" and n["in"]["self"].endswith(".Panel") for n in g["nodes"]))

if __name__ == "__main__":
    unittest.main()
