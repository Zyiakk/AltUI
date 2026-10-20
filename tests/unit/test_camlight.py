"""Camera light in the Jodi view (spec 2026-10-19-kameralicht): a spot at the game camera that brightens without a glint or a
visible cone - BP_AltUILight with fixed values, moved by the manager every frame (also paused = photo mode), switched by a round
button beside the panel with a submenu (on/off, colour via the palette, vertical brightness slider)."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)


def load(name):
    with open(os.path.join(ASSETS, name), encoding="utf-8") as f:
        return json.load(f)


class LightClass(unittest.TestCase):
    def test_spot_values(self):
        bp = next(o for o in load("27_cammod.json")["assets"] if o.get("path", "").endswith("/BP_AltUILight"))
        spot = next(c for c in bp["components"] if c["name"] == "Spot")
        self.assertTrue(spot["class"].endswith("SpotLightComponent"))
        p = spot["properties"]
        for k, v in {"Mobility": "Movable", "bUseInverseSquaredFalloff": "false", "SpecularScale": "0.0", "VolumetricScatteringIntensity": "0.0",
                     "CastShadows": "false", "InnerConeAngle": "30.0", "OuterConeAngle": "70.0", "LightFalloffExponent": "2.0", "bVisible": "false"}.items():
            self.assertEqual(p.get(k), v, k)


def exec_has(graph, *ids):
    """ids follow each other directly in one exec chain of the graph."""
    for ch in graph["exec"]:
        for i in range(len(ch) - len(ids) + 1):
            if tuple(ch[i:i + len(ids)]) == ids: return True
    return False


def graph_with(doc, node_id):
    return next(o for o in walk(doc) if isinstance(o.get("nodes"), list) and any(n.get("id") == node_id for n in o["nodes"]))


class Manager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ui = load("50_manager_ui.json")
        cls.fns = {o["name"]: o for o in walk(cls.ui) if isinstance(o.get("graph"), dict) and "name" in o}
        cls.sg = next(o for o in walk(load("30_manager.json")) if str(o.get("path", "")).endswith("/SG_AltUI"))

    def test_tick_moves_the_light_paused_and_not(self):
        g = graph_with(self.ui, "tls0")
        self.assertTrue(exec_has(g, "tpzt", "tls0"))   # paused = photo mode
        self.assertTrue(exec_has(g, "tct", "tls1"))
        self.assertTrue(exec_has(g, "tsc", "tplg"))    # slider polled with the panel open
        for i in ("tls0", "tls1"):
            self.assertEqual(next(n for n in g["nodes"] if n["id"] == i)["function"], "Light Step")

    def test_light_step_follows_the_camera_and_hides(self):
        g = self.fns["Light Step"]["graph"]; fs = [n.get("function") for n in g["nodes"]]
        for f in ("GetCameraLocation", "GetCameraRotation", "K2_SetActorLocationAndRotation", "IsValid"): self.assertIn(f, fs)
        vis = [n["in"]["bNewVisibility"] for n in g["nodes"] if n.get("function") == "SetVisibility"]
        self.assertEqual(sorted(vis), ["false", "true"])
        self.assertTrue(any(n.get("kind") == "spawn" and n["class"].endswith("/BP_AltUILight") for n in g["nodes"]))   # spawned anew after a level change

    def test_light_apply_power_squared(self):
        g = self.fns["Light Apply"]["graph"]; fs = [n.get("function") for n in g["nodes"]]
        self.assertIn("SetLightColor", fs); self.assertIn("SetIntensity", fs)
        self.assertEqual(next(n for n in g["nodes"] if n.get("function") == "SetLightColor")["in"]["bSRGB"], "false")

    def test_menu_actions(self):
        g = self.fns["On Menu Action"]["graph"]; called = {n.get("function") for n in g["nodes"]}
        for f in ("Toggle Light Menu", "Toggle Light", "Open Light Color", "Close Light Menu"): self.assertIn(f, called)
        self.assertTrue(exec_has(g, "cm", "blmp", "bscn")); self.assertTrue(exec_has(g, "blmp:else", "clmp", "bscn"))

    def test_palette_light_mode(self):
        self.assertIn("Light", json.dumps(self.fns["Apply Preview"]["graph"]))
        self.assertTrue(exec_has(self.fns["Commit Color"]["graph"], "bli", "lsv"))
        g = self.fns["Open Light Color"]["graph"]
        self.assertTrue(any(n.get("function") == "Show Palette" for n in g["nodes"]))

    def test_settings_and_defaults(self):
        for f in ("Load Settings", "Save Settings"):
            g = json.dumps(self.fns[f]["graph"]) if f in self.fns else json.dumps(next(o for o in walk(load("30_manager.json")) if o.get("name") == f and "graph" in o)["graph"])
            for k in ("LightOn", "LightColor", "LightPower"): self.assertIn(k, g, f)
        v = {x["name"]: x for x in self.sg["variables"]}
        self.assertNotIn("default", v["LightOn"])   # off
        self.assertEqual(v["LightPower"]["default"], "0.5"); self.assertEqual(v["LightColor"]["default"], "(R=1,G=0.76,B=0.515,A=1)")

class Panel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        w = load("40_widgets.json")
        cls.panel = next(o for o in walk(w) if str(o.get("path", "")).endswith("/W_AltUI"))
        cls.pfn = {f["name"]: f for f in cls.panel["functions"]}
        cls.round = next(o for o in walk(w) if str(o.get("path", "")).endswith("/W_RoundButton"))
        cls.names = {o.get("name") for o in walk(cls.panel.get("widget_tree", cls.panel)) if isinstance(o, dict)}

    def test_widgets(self):
        for n in ("BtnLight", "LightMenu", "SldLight", "BtnLightPower", "BtnLightColor"): self.assertIn(n, self.names)
        sld = next(o for o in walk(self.panel) if o.get("name") == "SldLight")
        self.assertEqual(sld["props"]["Orientation"], "Orient_Vertical")
        menu = next(o for o in walk(self.panel) if o.get("name") == "LightMenu")
        self.assertEqual([c["name"] for c in menu["children"]], ["SldLightBox", "BtnLightColor", "BtnLightPower"])   # top to bottom = bottom to top: on/off, colour, slider

    def test_init_buttons(self):
        g = json.dumps(self.pfn["Init Buttons"]["graph"])
        for a in ("LightMenu", "LightPower", "LightColor", "Tip_Light", "T_Light", "T_Power", "T_Swatch"): self.assertIn(a, g)

    def test_cam_mode_hides_light(self):
        g = json.dumps(self.pfn["Set Cam Mode"]["graph"]); self.assertIn("BtnLight", g); self.assertIn("LightMenu", g)

    def test_click_beside_closes_menu(self):
        g = self.pfn["OnPreviewMouseButtonDown"]["graph"]
        self.assertTrue(any(n.get("function") == "Close Light Menu" for n in g["nodes"]))
        self.assertTrue(exec_has(g, "blh:else", "clm", "bc"))

    def test_round_button_lit_and_tint(self):
        fns = {f["name"] for f in self.round["functions"]}; self.assertTrue({"Set Lit", "Set Tint", "Apply Icon"} <= fns)
        self.assertTrue({"Lit", "Tint", "HasTint"} <= {v["name"] for v in self.round["variables"]})

    def test_update_and_get(self):
        self.assertIn("Update Light Menu", self.pfn); self.assertTrue(self.pfn["Get Light Slider"].get("pure"))


if __name__ == "__main__":
    unittest.main()
