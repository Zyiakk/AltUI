"""2026-11-15: Options > General "Clothes follow the body shape" (ClothFitOn -> Apply Cloth Fit -> SetClothMaxDistanceScale)."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, os.path.join(H, "..", "..", "scripts")); sys.path.insert(0, H)
import gen_manager, gen_manager_ui, gen_widgets as gw
import bodyscale_groups as bg
from strings import STRINGS, LANGS
from strings_fr import FR
from test_play_zoom import load, walk


def fns(name="50_manager_ui.json"): return {o["name"]: o for o in walk(load(name)) if isinstance(o.get("graph"), dict) and "name" in o}
def by_id(g): return {n["id"]: n for n in g["nodes"]}


def cloth_scale(factors, on, active):
    """Evaluates the pure value pins of Apply Cloth Fit (the Scale input of SetClothMaxDistanceScale) for the given slider factors."""
    g = fns()["Apply Cloth Fit"]["graph"]; nodes = by_id(g)
    vars_ = {"ClothFitOn": on, "ScaleActive": active}
    ops = {"BooleanAND": lambda a: a["A"] and a["B"], "FMax": lambda a: max(a["A"], a["B"]), "Subtract_FloatFloat": lambda a: a["A"] - a["B"],
           "Multiply_FloatFloat": lambda a: a["A"] * a["B"], "FClamp": lambda a: min(max(a["Value"], a["Min"]), a["Max"]),
           "SelectFloat": lambda a: a["A"] if a["bPickA"] else a["B"], "Array_Get": lambda a: factors[a["Index"]]}

    def pin(v):
        if isinstance(v, str) and v.startswith("@"):
            nid = v[1:].split(".")[0]; n = nodes[nid]
            if n["kind"] == "get": return vars_[n["var"]]
            if n.get("function") == "Body Scale Factors" or nid == "fac": return factors
            args = {k: pin(x) for k, x in n.get("in", {}).items() if k != "TargetArray"}
            return ops[n["function"]](args)
        if v in ("true", "false"): return v == "true"
        try: return int(v)
        except ValueError: return float(v)
    smd = next(n for n in nodes.values() if n.get("function") == "SetClothMaxDistanceScale")
    return pin(smd["in"]["Scale"])


class Option(unittest.TestCase):
    def test_saved_default_off(self):
        rows = {m: (k, d) for m, _, k, d in gen_manager.SETTINGS}
        self.assertEqual(rows["ClothFitOn"][0], "copy")
        mgr = next(o for o in walk(load("30_manager.json")) if str(o.get("path", "")).endswith("/BP_AltUIManager") and o.get("variables"))
        names = {x["name"]: x for x in mgr["variables"]}
        for v in ("ClothFitOn", "ClothFitApplied"):
            self.assertIn(names[v].get("default", "false"), ("false", None, ""), v)

    def test_row_after_underwear(self):
        rows = gw.OPT_CAT_ROWS["General"]; i = rows.index("RowNude")
        self.assertEqual(rows[i + 1:i + 3], ["RowClothFit", "HintClothFit"])

    def test_strings(self):
        for k in ("Lbl_ClothFit", "Hint_ClothFit"):
            self.assertEqual(len(STRINGS[k]), len(LANGS), k); self.assertTrue(all(STRINGS[k]), k); self.assertTrue(FR.get(k), k)
        for pin, widget, key in (("clothfit", "LblClothFit", "Lbl_ClothFit"), ("clothfithint", "HintClothFit", "Hint_ClothFit")):
            self.assertIn((pin, widget), gw.PANEL_TEXTS); self.assertIn((pin, key), gen_manager_ui.PANEL_STRINGS)
        self.assertIn("LblClothFit", gw.PANEL_TEXT_COLORS["ColText"]); self.assertIn("HintClothFit", gw.PANEL_TEXT_COLORS["ColTextDim"])

    def test_checks_round_trip(self):
        w = fns("40_widgets.json"); ui = fns()
        self.assertTrue(any(n.get("in", {}).get("InIsChecked") == "@entry.clothfit" for n in w["Set Option Checks"]["graph"]["nodes"]))
        self.assertIn("clothfit", [p["name"] for p in w["Get Option Values"]["outputs"]])
        self.assertTrue(any(n.get("function") == "Set Option Checks" and str(n.get("in", {}).get("clothfit", "")).endswith(".ClothFitOn") for n in ui["Rebuild Options Body"]["graph"]["nodes"]))

    def test_greyed_without_converted_body(self):
        nodes = fns("40_widgets.json")["Set Foot IK Enabled"]["graph"]["nodes"]
        self.assertTrue(any(n.get("kind") == "get" and n.get("var") == "OptClothFit" for n in nodes))


class Apply(unittest.TestCase):
    def test_poll_sets_applies_and_saves(self):
        g = fns()["Poll Options"]["graph"]
        self.assertIn(["bclf", "sclf", "aclf", "svclf", "btvw"], g["exec"])
        nodes = by_id(g)
        self.assertEqual(nodes["aclf"].get("function"), "Apply Cloth Fit"); self.assertEqual(nodes["svclf"].get("function"), "Save Settings")

    def test_every_half_second_after_physics(self):
        g = fns()["Body Physics Step"]["graph"]; nodes = by_id(g)
        ch = next(c for c in g["exec"] if "ap" in c)
        self.assertEqual(nodes[ch[ch.index("ap") + 1]].get("function"), "Apply Cloth Fit")

    def test_every_skeletal_mesh_of_the_wearer(self):
        g = fns()["Apply Cloth Fit"]["graph"]; nodes = by_id(g)
        cmp = next(n for n in nodes.values() if n.get("function") == "K2_GetComponentsByClass")
        self.assertEqual(cmp["in"]["ComponentClass"], "/Script/Engine.SkeletalMeshComponent")
        self.assertIn(["fe", "smd"], g["exec"])

    def test_scale(self):
        n = [float(v) for v in bg.NEUTRAL]; i = {k: j for j, (k, _) in enumerate(bg.SLIDERS)}
        self.assertEqual(cloth_scale(n, True, True), 1.0)
        big = list(n); big[i["Glutes"]] = 1.3; big[i["Breast"]] = 1.1
        self.assertAlmostEqual(cloth_scale(big, True, True), 1 - 0.3 * bg.CLOTH_FIT_GAIN)
        huge = list(n); huge[i["Thighs"]] = 1.8
        self.assertAlmostEqual(cloth_scale(huge, True, True), bg.CLOTH_FIT_MIN)
        small = list(n); small[i["Breast"]] = 0.7; small[i["Arms"]] = 2.0   # shrinking and arms do not count
        self.assertEqual(cloth_scale(small, True, True), 1.0)
        self.assertEqual(cloth_scale(huge, False, True), 1.0)   # off: back to the engine default
        self.assertEqual(cloth_scale(huge, True, False), 1.0)   # body without ABP_BodyScale: the sliders do nothing

    def test_off_touches_nothing_unless_it_was_on(self):
        g = fns()["Apply Cloth Fit"]["graph"]; nodes = by_id(g)
        self.assertEqual(g["exec"][0][:4], ["entry", "bv", "bany", "sap"])
        anyn = nodes[nodes["bany"]["in"]["Condition"][1:].split(".")[0]]
        self.assertEqual(anyn["function"], "BooleanOR")
        self.assertEqual(nodes["sap"]["in"]["ClothFitApplied"], "@act.ReturnValue")


if __name__ == "__main__": unittest.main()
