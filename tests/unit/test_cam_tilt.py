"""2026-10-25: camera distance mode, wheel-zoom switch, screen tilt (spec docs/superpowers/specs/2026-10-25-camera-distance-tilt-design.md)."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
import gen_manager, gen_widgets as gw
from strings import STRINGS, LANGS
from test_play_zoom import load, walk, exec_has

OPTS = ("PlayWheelZoom", "TiltPanelOff")


def fns(name="50_manager_ui.json"): return {o["name"]: o for o in walk(load(name)) if isinstance(o.get("graph"), dict) and "name" in o}
def by_id(g): return {n["id"]: n for n in g["nodes"]}


class Options(unittest.TestCase):
    def test_saved_default_off(self):
        rows = {m: (k, d) for m, _, k, d in gen_manager.SETTINGS}
        for o in OPTS: self.assertEqual(rows[o][0], "copy", o)   # bool, default false: zoom off, tilt shown with the panel open
        mgr = next(o for o in walk(load("30_manager.json")) if str(o.get("path", "")).endswith("/BP_AltUIManager") and o.get("variables"))
        for v in mgr["variables"]:
            if v["name"] in OPTS: self.assertIn(v.get("default", "false"), ("false", None, ""))

    def test_rows_in_camera(self):
        self.assertLessEqual({"RowPlayWheelZoom", "RowTiltPanelOff"}, set(gw.OPT_CAT_ROWS["Camera"]))

    def test_strings(self):
        for k in ("Lbl_PlayWheelZoom", "Lbl_TiltPanelOff"): self.assertEqual(len(STRINGS[k]), len(LANGS), k)

    def test_checks_round_trip(self):
        w = fns("40_widgets.json")
        self.assertTrue(any(n.get("in", {}).get("InIsChecked") == "@entry.playwheelzoom" for n in w["Set Option Checks"]["graph"]["nodes"]))
        self.assertTrue(any(n.get("in", {}).get("InIsChecked") == "@entry.tiltpaneloff" for n in w["Set Option Checks"]["graph"]["nodes"]))


class Tilt(unittest.TestCase):
    def test_modifier_adds_roll_on_both_paths(self):
        mod = next(o for o in walk(load("27_cammod.json")) if o.get("name") == "BlueprintModifyCamera")
        g = mod["graph"]; b = by_id(g)
        self.assertEqual(b["rl"]["function"], "Add_FloatFloat"); self.assertEqual(b["rl"]["in"]["B"], "@grl.Roll")
        links = g.get("links", [])
        self.assertIn(["nr.ReturnValue", "return.NewViewRotation"], links); self.assertIn(["nr.ReturnValue", "r2.NewViewRotation"], links)

    def test_tick_writes_roll(self):
        f = fns(); b = by_id(f["Tilt Tick"]["graph"])
        self.assertEqual(b["sr"]["var"], "Roll"); self.assertEqual(b["sel"]["in"]["A"], "0.0")   # panel open + option: straight
        self.assertTrue(exec_has(f["Cam Tick"]["graph"], "entry", "pz", "tlt"))

    def test_nudge_wraps(self):
        b = by_id(fns()["Nudge Tilt"]["graph"]); self.assertEqual(b["nw"]["function"], "NormalizeAxis")

    def test_quick_items(self):
        import gen_manager_ui as ui
        for k in ("tiltleft", "tiltright", "tiltreset"): self.assertIn(k, ui.QUICK_FIXED); self.assertIn(k, ui.QUICK_FIXED_TEXT); self.assertIn(k, ui.QUICK_FIXED_ICON)
        b = by_id(fns()["Run Quick Item"]["graph"])
        self.assertEqual(b["ntl"]["in"]["deg"], "-1.0"); self.assertEqual(b["ntr"]["in"]["deg"], "1.0"); self.assertEqual(b["trs"]["in"]["PlayTilt"], "0.0")

    def test_not_saved(self):
        self.assertNotIn("PlayTilt", {m for m, _, _, _ in gen_manager.SETTINGS})


class WheelModes(unittest.TestCase):
    def test_quick_items_start_modes(self):
        b = by_id(fns()["Run Quick Item"]["graph"])
        self.assertEqual((b["sph"]["function"], b["sph"]["in"]["mode"]), ("Start Play Wheel", "1"))
        self.assertEqual((b["spdm"]["function"], b["spdm"]["in"]["mode"]), ("Start Play Wheel", "2"))
        self.assertEqual((b["sptm"]["function"], b["sptm"]["in"]["mode"]), ("Start Play Wheel", "3"))

    def test_tilt_step_wraps(self):
        b = by_id(fns()["Play Zoom"]["graph"]); self.assertEqual(b["ntw"]["function"], "NormalizeAxis"); self.assertEqual(b["dtl"]["in"]["B"], "1.0")

    def test_restart_switches_arrows(self):
        g = fns()["Start Play Wheel"]["graph"]; b = by_id(g)
        self.assertEqual(b["shm"]["function"], "Show Mode"); self.assertTrue(exec_has(g, "bw", "shm"))   # running already: only the arrows change

    def test_widget_has_three_groups(self):
        wp = next(o for o in walk(load("40_widgets.json")) if str(o.get("path", "")).endswith("/W_PlayHeight"))
        names = {o.get("name") for o in walk(wp.get("widget_tree", {}))}
        self.assertLessEqual({"Arrows", "DistArrows", "TiltArrows"}, names)


if __name__ == "__main__":
    unittest.main()
