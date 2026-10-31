"""Navigation tab: teleport to the save beds (spec 2026-10-27)."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_options_cats import graph, calls
from strings import STRINGS, LANGS
import strings_fr, gen_widgets as gw, gen_manager_ui as ui, gen_textures


def g(name): return graph("50_manager_ui.json", name)


def fns(gr): return [n.get("function") for n in gr["nodes"]]


NAV_STRINGS = ("Tab_Navigation", "Nav_NoBeds", "Nav_Dead", "Nav_Falling", "Nav_Bed", "Nav_Meters", "Nav_Go")


class Tab(unittest.TestCase):
    def test_after_ragdolls(self):
        self.assertEqual(ui.TOP_TABS[ui.TOP_TABS.index("Enemies") + 1], "Navigation")

    def test_strings(self):
        for k in NAV_STRINGS:
            self.assertEqual(len(STRINGS[k]), len(LANGS), k); self.assertIn(k, strings_fr.FR, k)

    def test_icon(self):
        self.assertIn("Navigation", gen_textures.TAB_ICONS)

    def test_page(self):
        w = json.dumps(json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json"))))
        for wn in ("NavBox", "NavHint", "NavScroll", "NavList"): self.assertIn('"%s"' % wn, w, wn)
        self.assertIn("NavScroll", gw.SCROLL_PAGES)

    def test_select_page_rebuilds(self):
        self.assertTrue(calls(g("Select Page"), "Rebuild Nav"))


class List(unittest.TestCase):
    def test_scan(self):
        r = g("Rebuild Nav"); js = json.dumps(r)
        self.assertIn("GetAllActorsOfClass", fns(r)); self.assertIn("/Game/Project/Actors/Bed", js)
        self.assertIn("Save Point Name", js); self.assertIn("Array_Insert", fns(r))   # sorted by distance

    def test_rows(self):
        r = g("Rebuild Nav"); js = json.dumps(r)
        self.assertIn("NavGo:", js); self.assertIn("Set Stripe", fns(r)); self.assertIn("Set Nav Hint", fns(r)); self.assertIn("W_NavRow", js)
        for k in ("Nav_NoBeds", "Nav_Dead", "Nav_Falling", "Nav_Bed", "Nav_Meters", "Nav_Go"): self.assertIn(k, js, k)

    def test_story_order(self):
        self.assertEqual(ui.NAV_BED_ORDER["Level_1"][0], "Bed4_2")   # A3 duty room: the first save room
        self.assertEqual(len(ui.NAV_BED_ORDER["Level_1"]), 13); self.assertEqual(len(ui.NAV_BED_ORDER["Level_2"]), 6)
        rk = g("Nav Bed Rank"); js = json.dumps(rk)
        self.assertIn("GetObjectName", fns(rk)); self.assertIn("Level_1:Bed4_2", js); self.assertIn("Level_2:Bed_Lab6", js)
        r = g("Rebuild Nav"); self.assertTrue(calls(r, "Nav Bed Rank")); self.assertIn("NavKey", json.dumps(r)); self.assertIn("NavNear", json.dumps(r))

    def test_near_signs(self):
        r = g("Rebuild Nav"); js = json.dumps(r)
        self.assertIn("/Game/Project/Actors/Misc/Department", js); self.assertIn("Description", js); self.assertIn("Nav_Near", js)
        self.assertEqual(len(STRINGS["Nav_Near"]), len(LANGS)); self.assertIn("Nav_Near", strings_fr.FR)

    def test_blocked(self):
        r = g("Rebuild Nav"); f = fns(r)
        self.assertIn("Is Alive ?", f); self.assertIn("IsMovingOnGround", f); self.assertIn("NavOk", json.dumps(r)); self.assertIn("FlyOn", json.dumps(r))   # flying may teleport


class Teleport(unittest.TestCase):
    def test_spot(self):
        s = g("Nav Spot For Bed"); f = fns(s)
        self.assertEqual(f.count("K2_ProjectPointToNavigation"), 24)
        self.assertEqual(f.count("Abs"), 24)   # each place on the bed's floor (not the bottom of a shaft next to it)
        self.assertIn("GetActorForwardVector", f); self.assertIn("GetActorRightVector", f)
        # play test 2026-10-29 (A2 Lounge): every place in sight of the bed - one projected into a sealed box behind two walls
        self.assertEqual(f.count("LineTraceSingle"), 24)
        for n in s["nodes"]:
            if n.get("function") == "LineTraceSingle": self.assertTrue(any(n["id"] in c for c in s["exec"]), n["id"])

    def test_free_spot(self):
        """No navmesh place (the room has none): free floor in sight of the bed - a trace from the bed and one down per place."""
        s = g("Nav Free Spot For Bed"); f = fns(s)
        self.assertEqual(f.count("LineTraceSingle"), 2 * 8 * len(ui.NAV_FREE_DISTS))
        self.assertNotIn("K2_ProjectPointToNavigation", f); self.assertEqual(f.count("Abs"), 8 * len(ui.NAV_FREE_DISTS))
        t = g("Nav Teleport"); self.assertTrue(calls(t, "Nav Free Spot For Bed"))
        self.assertNotIn("GetActorForwardVector", fns(t))   # no more "100 cm in front of the bed" (behind the wall of A2 Lounge)

    def test_teleport(self):
        t = g("Nav Teleport"); f = fns(t)
        for c in ("Stop Free Cam", "Stop Pose", "End Idle Pose", "Nav Spot For Bed", "Nav Follow", "Close Panel"): self.assertTrue(calls(t, c), c)
        for c in ("K2_TeleportTo", "K2_SetActorLocation", "StopMovementImmediately", "SetControlRotation", "GetScaledCapsuleHalfHeight", "FindLookAtRotation"): self.assertIn(c, f, c)
        self.assertGreaterEqual(f.count("K2_TeleportTo"), 2); self.assertIn("SelectVector", f)   # navmesh place, else room found by the engine, else onto the bed
        self.assertEqual(sum(1 for n in t["nodes"] if n.get("function") == "Nav Spot For Bed"), 2)   # hers, and the followers' one

    def test_follow_only_following(self):
        n = g("Nav Follow"); js = json.dumps(n); f = fns(n)
        self.assertIn("GetAllActorsOfClass", f); self.assertIn("Npc_Controller", js); self.assertIn("master", js); self.assertIn("Current Order", js)
        self.assertIn("NpcFollow", js); self.assertIn("K2_SetActorLocation", f)
        self.assertIn("FolActors", js); self.assertIn("Array_Contains", f)   # only AltUI's own followers
        self.assertEqual(f.count("K2_TeleportTo"), 1); self.assertIn("NavFolSpot", js)   # room searched once, the rest on that spot
        self.assertNotIn("Fol Front", js)   # the place comes from Nav Teleport (the camera has not moved yet in that frame)

    def test_dispatch(self):
        a = g("On Menu Action"); js = json.dumps(a)
        self.assertIn("NavGo:", js); self.assertTrue(calls(a, "Nav Teleport"))


def mgr_assets(): return json.load(open(os.path.join(H, "..", "..", "assets", "50_manager_ui.json")))["assets"]


class Fly(unittest.TestCase):
    def test_start(self):
        s = g("Fly Start"); js = json.dumps(s)
        self.assertIn("SetMovementMode", fns(s)); self.assertIn("MOVE_Flying", js)
        for v in ("MaxFlySpeed", "BrakingDecelerationFlying", "MaxAcceleration", "FlyOldMax", "FlyOldBrake", "FlyOldAccel", "FlyInput", "FlyOn"): self.assertIn(v, js, v)
        self.assertIn("BP_FlyInput", js)

    def test_stop(self):
        s = g("Fly Stop"); js = json.dumps(s)
        self.assertIn("K2_DestroyActor", fns(s)); self.assertIn("MOVE_Falling", js); self.assertIn("MOVE_Walking", js)
        for v in ("FlyOldMax", "FlyOldBrake", "FlyOldAccel", "MaxAcceleration", "FlyOn"): self.assertIn(v, js, v)

    def test_tick(self):
        t = g("Fly Tick"); js = json.dumps(t); f = fns(t)
        self.assertIn("IsFlying", f); self.assertIn("Is Alive ?", f); self.assertIn("AddMovementInput", f); self.assertTrue(calls(t, "Fly Stop"))
        for k in ("SpaceBar", "LeftControl", "LeftShift"): self.assertIn(k, js, k)

    def test_input_helper(self):
        a = [x for x in mgr_assets() if x.get("path", "").endswith("BP_FlyInput")]; self.assertEqual(len(a), 1)
        js = json.dumps(a[0])
        for k in ("SpaceBar", "LeftControl", "RightControl"): self.assertIn(k, js, k)

    def test_manager_tick_calls_fly(self):
        mgr = [x for x in mgr_assets() if "Fly Tick" in json.dumps(x.get("event_graph", {}))]; self.assertTrue(mgr)

    def test_quick_and_link(self):
        self.assertIn("fly", ui.QUICK_FIXED); self.assertEqual(ui.QUICK_FIXED_TEXT["fly"], "Quick_Fly"); self.assertIn("fly", ui.QUICK_FIXED_ICON)
        self.assertIn(("NavFly", "Fly Toggle", None), ui.MENU_ACTIONS)
        self.assertTrue(calls(g("Run Quick Item"), "Fly Toggle"))
        r = g("Rebuild Nav"); self.assertIn("NavFly", json.dumps(r)); self.assertTrue(calls(r, "Show Fly Speed"))
        self.assertTrue(calls(g("Nav Teleport"), "Fly Stop"))

    def test_strings(self):
        for k in ("Nav_Fly", "Nav_Land", "Quick_Fly", "Nav_FlySpeedVal"):
            self.assertEqual(len(STRINGS[k]), len(LANGS), k); self.assertIn(k, strings_fr.FR, k)


if __name__ == "__main__": unittest.main()
