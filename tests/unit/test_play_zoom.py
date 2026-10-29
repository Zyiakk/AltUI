"""Zoom and height in play: with the panel closed the mouse wheel scales the game's own unarmed view distance (Jodi.View Data Unarmed
.armlength) and raises "need update camera view data", so the game eases its spring arm there with its own collision and
aiming keeps the weapon's view. PlayDist is a saved setting; with the panel open the game's length comes back."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")
VDU = "View Data Unarmed "   # the game's variable name ends in a space


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)


def load(name):
    with open(os.path.join(ASSETS, name), encoding="utf-8") as f:
        return json.load(f)


def exec_has(graph, *ids):
    for ch in graph["exec"]:
        for i in range(len(ch) - len(ids) + 1):
            if tuple(ch[i:i + len(ids)]) == ids: return True
    return False


class PlayZoom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ui = load("50_manager_ui.json")
        cls.fns = {o["name"]: o for o in walk(ui) if isinstance(o.get("graph"), dict) and "name" in o}
        cls.g = cls.fns["Play Zoom"]["graph"]
        cls.nodes = {n["id"]: n for n in cls.g["nodes"]}

    def test_cam_tick_runs_it_in_every_mode(self):
        self.assertTrue(exec_has(self.fns["Cam Tick"]["graph"], "entry", "pz"))   # before the camera mode branches: the wheel mode always ends

    def test_wheel_only_in_play(self):
        ins = [n.get("in", {}) for n in self.g["nodes"]]
        self.assertTrue(any(i.get("B") == "@gcur.bShowMouseCursor" for i in ins))   # game menus and the quick menu show the cursor
        self.assertEqual(self.nodes["ie"]["function"], "Is Input Enabled ?")
        self.assertTrue(exec_has(self.g, "bhm", "sph", "sdt"))               # mode 1: the height
        self.assertTrue(exec_has(self.g, "bhm:else", "btm", "spt", "beq"))   # mode 3: the tilt (not saved)
        self.assertTrue(exec_has(self.g, "btm:else", "bdz", "spd", "sdt"))   # mode 2, or the switch on: the distance; saved (DistSaveTimer)
        self.assertTrue(exec_has(self.g, "bdz:else", "beq"))                 # switch off, no mode: the wheel does nothing
        self.assertEqual(self.nodes["dok"]["in"]["B"], "@gpwz.PlayWheelZoom")
        self.assertTrue(exec_has(self.g, "sdt", "beq"))

    def test_height_mode_ends_outside_play(self):
        self.assertTrue(exec_has(self.g, "bhend", "eph"))
        self.assertEqual(self.nodes["eph"]["function"], "End Play Wheel")

    def test_height_input_swallows_click_and_esc(self):
        bp = next(o for o in walk(load("50_manager_ui.json")) if str(o.get("path", "")).endswith("/BP_HeightInput"))
        eg = bp["event_graph"]; keys = {n["key"] for n in eg["nodes"] if n["kind"] == "input_key"}
        self.assertEqual(keys, {"LeftMouseButton", "Escape"})
        self.assertTrue(all(n.get("consume", True) for n in eg["nodes"] if n["kind"] == "input_key"))
        for k in ("lmb", "esc"):   # both events wired (an unbound Released reaches the game: Esc opens its menu on release)
            self.assertTrue(exec_has(eg, k + ":Pressed", k + "_p")); self.assertTrue(exec_has(eg, k + ":Released", k + "_e"))

    def test_quick_menu_starts_it(self):
        g = self.fns["Run Quick Item"]["graph"]
        self.assertTrue(any(n.get("function") == "Start Play Wheel" and n["in"]["mode"] == "1" for n in g["nodes"]))

    def test_writes_the_games_view_and_flag(self):
        self.assertEqual(self.nodes["svd"]["var"], VDU)
        self.assertEqual(self.nodes["snu"]["var"], "need update camera view data")
        self.assertTrue(exec_has(self.g, "beq:else", "svd", "snu"))
        self.assertEqual(self.nodes["tgt"]["in"]["bPickA"], "@gpo2.PanelOpen")   # panel open: the game's own length

    def test_stubs_match_the_game(self):
        stubs = load("10_stubs.json")
        wvs = next(o for o in walk(stubs) if str(o.get("path", "")).endswith("/WeaponViewStruct"))
        names = {m["name"]: m.get("internal_name") for m in wvs["members"]}
        # the kit's stub already has these members under these display names; another name adds a duplicate member
        self.assertEqual(names["arm length"], "armlength_4_A0D45C7F4145C5F649D173884365ED33")
        self.assertEqual(names["socket offset"], "socketoffset_7_51B3ABFE4696FBC4E58B58ACDA4589F8")
        jodi = [o for o in walk(stubs) if str(o.get("path", "")).endswith("/Character/Jodi/Jodi") and o.get("mode") == "augment"]
        self.assertTrue(any(v["name"] == VDU for j in jodi for v in j["variables"]))

    def test_setting_saved(self):
        sg = next(o for o in walk(load("30_manager.json")) if str(o.get("path", "")).endswith("/SG_AltUI"))
        names = [v["name"] for v in sg["variables"]]
        self.assertIn("PlayDist", names); self.assertIn("PlayHeight", names)


if __name__ == "__main__":
    unittest.main()
