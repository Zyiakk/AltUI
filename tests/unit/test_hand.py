"""Invisible hand (docs/specs/2026-10-25-invisible-hand-design.md): stubs, BP_AltUIHand, manager, options."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
import cfg
import bpdsl, gen_stubs


def stub(path):
    return [a for a in gen_stubs.assets if a.get("path") == path]


class Stubs(unittest.TestCase):
    def test_paths(self):
        self.assertEqual(bpdsl.P_PICKABLE, "/Game/Project/Classes/Items/ItemComp_Pickable")
        self.assertEqual(bpdsl.P_FLYING, "/Game/Project/Classes/Component/FlyingItem_Comp")

    def test_hand_vars(self):
        names = {v["name"] for a in stub(bpdsl.P_IHC) for v in a.get("variables", [])}
        self.assertLessEqual({"Number", "interval", "time", "Jodi"}, names)

    def test_pickable_flag(self):
        a = stub(bpdsl.P_PICKABLE); self.assertEqual(a[0]["mode"], "augment")   # the kit has the class already
        self.assertIn("Can Be Auto Picked", {v["name"] for v in a[0]["variables"]})

    def test_flying_init(self):
        a = stub(bpdsl.P_FLYING)[0]
        self.assertEqual(a["parent"], "/Script/Engine.ActorComponent")
        init = next(f for f in a["functions"] if f["name"] == "Init")
        self.assertEqual([p["name"] for p in init["inputs"]], ["invisible Comp"])

    def test_character_base(self):
        fns = {f["name"] for a in stub(bpdsl.P_CB) for f in a.get("functions", [])}
        self.assertLessEqual({"get Foot Location", "Is Ragdoll ?"}, fns)


import gen_hand


class HandAsset(unittest.TestCase):
    def setUp(self): self.bp = gen_hand.build()[0]

    def test_path_and_parent(self):
        self.assertEqual(self.bp["path"], "/Game/Mod/AltUI/BP_AltUIHand"); self.assertEqual(self.bp["parent"], "/Script/Engine.Actor")

    def test_functions(self):
        names = {f["name"] for f in self.bp["functions"]}
        self.assertLessEqual({"Hand Extent", "Hand Wanted", "Hand Interval", "Batch Count", "Pick Allowed", "Set Hand", "Release", "Bind", "Pick", "Scan", "Step"}, names)
        pure = {f["name"] for f in self.bp["functions"] if f.get("pure")}
        self.assertEqual(pure, {"Hand Extent", "Hand Wanted", "Hand Interval", "Batch Count", "Pick Allowed"})

    def test_scan_like_the_game(self):
        js = json.dumps(next(f for f in self.bp["functions"] if f["name"] == "Scan"))
        for s in ("BoxOverlapComponents", "ObjectTypeQuery4", "(X=0,Y=0,Z=90.0)", gen_hand.P_PICKABLE, "Can Be Auto Picked", gen_hand.P_FLYING): self.assertIn(s, js)

    def test_pick_like_the_game(self):
        js = json.dumps(next(f for f in self.bp["functions"] if f["name"] == "Pick"))
        for s in ("IsSimulatingPhysics", "K2_SetActorLocation", "SetSimulatePhysics", "K2_AttachToComponent", "SnapToTarget", "AddComponentByClass", "\"Init\""): self.assertIn(s, js)

    def test_step_quiets_and_releases(self):
        step = json.dumps(next(f for f in self.bp["functions"] if f["name"] == "Step"))
        self.assertIn(str(gen_hand.QUIET), step); self.assertIn("\"Jodi\"", step); self.assertIn("IsComponentTickEnabled", step)
        rel = json.dumps(next(f for f in self.bp["functions"] if f["name"] == "Release"))
        self.assertIn("\"time\"", rel)
        self.assertIn("ReceiveEndPlay", json.dumps(self.bp["event_graph"]))

    def test_manifest(self):
        lines = open(os.path.join(H, "..", "..", "assets", "manifest.txt")).read().split()
        self.assertIn("29d_hand.json", lines)
        self.assertLess(lines.index("29c_jason.json"), lines.index("29d_hand.json")); self.assertLess(lines.index("29d_hand.json"), lines.index("30_manager.json"))


import gen_manager
from strings import STRINGS, LANGS


def mgr_fns():
    d = json.load(open(os.path.join(H, "..", "..", "assets", "50_manager_ui.json")))
    mgr = next(a for a in d["assets"] if a["path"].endswith("BP_AltUIManager"))
    return {f["name"]: f for f in mgr["functions"]}, mgr


class HandManager(unittest.TestCase):
    def test_settings(self):
        rows = {m: (s, k) for m, s, k, _ in gen_manager.SETTINGS}
        for k in ("HandOn", "HandRange", "HandBatch", "HandNoHand"): self.assertEqual(rows[k], (k, "copy"), k)

    def test_functions(self):
        fns, _ = mgr_fns()
        for n in ("Hand Range", "Hand Batch", "Apply Hand", "Reset Hand", "Toggle Hand"): self.assertIn(n, fns)
        self.assertIn("Set Hand", json.dumps(fns["Apply Hand"]))

    def test_spawned_at_begin_play(self):
        _, mgr = mgr_fns(); js = json.dumps(mgr["event_graph"])
        self.assertIn("BP_AltUIHand", js); self.assertIn("Apply Hand", js)

    def test_quick_toggle(self):
        import gen_manager_ui as ui
        self.assertIn("handtoggle", ui.QUICK_FIXED); self.assertEqual(ui.QUICK_FIXED_TEXT["handtoggle"], "Quick_HandToggle")
        self.assertIn("handtoggle", ui.QUICK_FIXED_ICON); self.assertEqual(len(STRINGS["Quick_HandToggle"]), len(LANGS))
        self.assertIn("Toggle Hand", json.dumps(mgr_fns()[0]["Run Quick Item"]))


import gen_widgets as gw


class HandOptions(unittest.TestCase):
    def test_category(self):
        self.assertEqual(gw.OPT_CATS[gw.OPT_CATS.index("Move") + 1], "Hand")
        self.assertEqual(gw.OPT_CAT_ROWS["Hand"], ["RowHandOn", "RowHandRange", "RowHandBatch", "RowHandNoHand", "HandLinks"])
        self.assertIn(("HandRange", "Range"), gw.OPTION_ROWS); self.assertIn(("HandBatch", "Items per round"), gw.OPTION_ROWS)

    def test_strings(self):
        for k in ("OptCat_Hand", "Lbl_HandOn", "Lbl_HandRange", "Lbl_HandBatch", "Lbl_HandNoHand", "Btn_HandReset"): self.assertEqual(len(STRINGS[k]), len(LANGS), k)

    def test_panel_texts_match(self):
        import gen_manager_ui as ui
        self.assertEqual([k for k, _ in gw.PANEL_TEXTS], [k for k, _ in ui.PANEL_STRINGS])
        for k in ("handon", "handnohand", "handrange", "handbatch"): self.assertIn(k, dict(ui.PANEL_STRINGS))

    def test_checks_round_trip(self):
        w = json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json")))
        js = json.dumps(w)
        for s in ("@entry.handon", "@entry.handnohand", "return.handon", "return.handnohand", "Clear Hand Links", "Add Hand Link"): self.assertIn(s, js)

    def test_poll_and_rebuild(self):
        fns, _ = mgr_fns()
        poll = json.dumps(fns["Poll Options"]); reb = json.dumps(fns["Rebuild Options Body"])   # Rebuild Options keeps the scroll positions around it
        for s in ("@gv.handrange", "@gv.handbatch", "@gv.handon", "@gv.handnohand", "Apply Hand", "HandRange", "HandBatch"): self.assertIn(s, poll)
        for s in ("handrange text", "handbatch text", "HandReset", "Add Hand Link", "\"handon\"", "\"handnohand\""): self.assertIn(s, reb)


if __name__ == "__main__":
    unittest.main()
