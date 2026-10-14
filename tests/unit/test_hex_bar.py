"""W_HexBar over the game's palette: every palette AltUI opens shows the bar, every way it closes removes it again, and the
bar's keys never reach the game while its field has focus."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")
PALETTE_OPENERS = ["Open Slot Color", "Open Mod Color", "Open Theme Color", "Open Eye Color", "Open Makeup Color", "Open Hair Color"]


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)


def load(name):
    with open(os.path.join(ASSETS, name), encoding="utf-8") as f:
        return json.load(f)


class HexBar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fns = {o["name"]: o for o in walk(load("50_manager_ui.json")) if isinstance(o.get("graph"), dict) and "name" in o}
        cls.bar = next(o for o in walk(load("40_widgets.json")) if str(o.get("path", "")).endswith("/W_HexBar"))

    def calls(self, fn, target):
        return any(n.get("kind") == "call_self" and n.get("function") == target for n in self.fns[fn]["graph"]["nodes"])

    def test_every_palette_shows_the_bar(self):
        for fn in PALETTE_OPENERS:
            with self.subTest(fn=fn):
                self.assertTrue(self.calls(fn, "Show Hex Bar"))

    def test_close_color_hides_the_bar_on_both_ways(self):
        g = self.fns["Close Color"]["graph"]
        self.assertIn(["entry", "bo", "cm", "s", "hhb", "ulk", "b", "cf", "rm"], g["exec"]); self.assertIn(["bo:else", "s"], g["exec"])
        self.assertTrue(self.calls("Close Color", "Hide Hex Bar"))

    def test_bar_handles_keys_while_typing(self):
        fns = {f["name"]: f for f in self.bar["functions"]}
        for k in ("OnKeyDown", "OnKeyUp"):
            nodes = fns[k]["graph"]["nodes"]
            self.assertTrue(any(n.get("function") == "HasKeyboardFocus" for n in nodes), k)
            self.assertTrue(any(n.get("function") == "Handled" for n in nodes), k)

    def test_bar_follows_the_palette_window(self):
        fns = {f["name"]: f for f in self.bar["functions"]}
        self.assertEqual(fns["Tick"]["graph"]["exec"][0][:2], ["entry", "plc"])
        g = self.fns["Place Hex Bar"]["graph"]
        self.assertIn(["entry", "b", "bs", "sp", "sa", "vis"], g["exec"])   # placed and shown only once the window has a size

    def test_paste_and_commit_go_through_init_paletter(self):
        for fn in ("Hex Commit", "Color Clip Paste"):
            with self.subTest(fn=fn):
                self.assertTrue(any(n.get("function") == "Init Paletter" for n in self.fns[fn]["graph"]["nodes"]))


if __name__ == "__main__":
    unittest.main()
