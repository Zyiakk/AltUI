"""Jodi stays draggable while the game's palette is open: its Show Palette makes the whole panel HitTestInvisible + disabled, so
AltUI unlocks the panel right after it and disables only Bg and the round buttons (the Jodi catcher stays live); every way the
palette closes (Close Color) enables them again, and a drag ends with the keyboard focus back on the palette (its Esc)."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")
PALETTE_OPENERS = ["Open Slot Color", "Open Mod Color", "Open Theme Color", "Open Eye Color", "Open Makeup Color", "Open Hair Color", "Open Light Color"]
LOCKED = ["Bg", "BtnPlus", "BtnMinus", "BtnCam", "BtnPhoto", "BtnRag", "BtnLight", "LightMenu"]


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)


def load(name):
    with open(os.path.join(ASSETS, name), encoding="utf-8") as f:
        return json.load(f)


def lock_calls(graph, on):
    return [n for n in graph["nodes"] if n.get("function") == "Set Palette Lock" and n.get("in", {}).get("on") == on]


def follows(graph, a, b):
    return any(a in ch and b in ch and ch.index(b) == ch.index(a) + 1 for ch in graph["exec"])


class PaletteJodiDrag(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fns = {o["name"]: o for o in walk(load("50_manager_ui.json")) if isinstance(o.get("graph"), dict) and "name" in o}
        panel = next(o for o in walk(load("40_widgets.json")) if str(o.get("path", "")).endswith("/W_AltUI"))
        cls.panel = {f["name"]: f for f in panel["functions"]}

    def test_every_palette_unlocks_the_panel_right_after_show_palette(self):
        for fn in PALETTE_OPENERS:
            with self.subTest(fn=fn):
                g = self.fns[fn]["graph"]
                ids = [n["id"] for n in lock_calls(g, "true")]
                self.assertTrue(ids)
                self.assertTrue(any(follows(g, "show", i) for i in ids))

    def test_close_color_locks_off_on_both_ways(self):
        g = self.fns["Close Color"]["graph"]
        ids = [n["id"] for n in lock_calls(g, "false")]
        self.assertEqual(ids, ["ulk"]); self.assertTrue(follows(g, "hhb", "ulk"))

    def test_lock_disables_only_bg_and_buttons(self):
        g = self.panel["Set Palette Lock"]["graph"]
        targets = sorted(n["in"]["self"].split(".")[1] for n in g["nodes"] if n.get("function") == "SetIsEnabled" and n["in"]["self"].split(".")[1] != "self")
        self.assertEqual(targets, sorted(LOCKED))
        self.assertNotIn("JodiCatcher", json.dumps(g))
        self.assertTrue(any(n.get("function") == "SetVisibility" and n["in"].get("InVisibility") == "Visible" for n in g["nodes"]))

    def test_drag_end_refocuses_open_palette(self):
        g = self.panel["OnMouseButtonUp"]["graph"]
        self.assertTrue(follows(g, "ed", "fp"))
        fp = self.fns["Focus Color Keys"]["graph"]
        self.assertIn("ColorOpen", json.dumps(fp))


if __name__ == "__main__":
    unittest.main()
