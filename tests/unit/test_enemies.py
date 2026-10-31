"""Enemies tab: hostile zombies (spec docs/specs/2026-10-30-enemies-tab-design.md)."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_options_cats import graph, calls


def stubs(): return json.load(open(os.path.join(H, "..", "..", "assets", "10_stubs.json")))["assets"]


def stub(path): return next(a for a in stubs() if a.get("path") == path)


class Stubs(unittest.TestCase):
    def test_zombie_functions(self):
        names = {f["name"] for f in stub("/Game/Project/Zombie/Zombie_Base").get("functions", [])}
        for f in ("on Spawn in Runtime", "Set Loot Item with Name", "Change Ai Mode", "Remove Me", "Is Alive ?"): self.assertIn(f, names)

    def test_controllers(self):
        ai = {f["name"] for f in stub("/Game/Project/Classes/Controller/AI_Controller").get("functions", [])}
        self.assertTrue({"Change Target Character", "Start Wait"} <= ai)
        zc = stub("/Game/Project/Classes/Controller/Zombie_Controller")
        self.assertEqual(zc.get("parent"), "/Game/Project/Classes/Controller/AI_Controller")
        self.assertIn("Stop Following Path", {f["name"] for f in zc.get("functions", [])})

    def test_ai_mode_enum(self):
        e = stub("/Game/Project/Classes/Enum/Zombie_AIMode")
        self.assertEqual(e["values"][:7], ["None", "NoSoul", "Inactive", "Active", "ChasePlayer", "Following", "Patrol"])

    def test_got_hurt(self):
        cb = {f["name"] for f in stub("/Game/Project/Classes/Character_Base").get("functions", [])}
        self.assertIn("Got Hurt", cb)


import gen_manager_ui as ui, gen_widgets as gw, gen_textures
from strings import STRINGS, LANGS
import strings_fr


def g(name): return graph("50_manager_ui.json", name)


TAB_STRINGS = ("Tab_Enemies", "En_Count", "En_Dist", "En_Hunt", "En_Lurk", "En_Passive", "En_RemoveAll", "En_RemoveNearest",
               "En_KillAll", "En_TogglePassive", "En_Live", "En_SaveHint", "En_NoNavHint", "En_NoRoom")


class Tab(unittest.TestCase):
    def test_after_ragdolls(self):
        self.assertEqual(ui.TOP_TABS[ui.TOP_TABS.index("Ragdolls") + 1], "Enemies")

    def test_strings(self):
        for k in TAB_STRINGS:
            self.assertEqual(len(STRINGS[k]), len(LANGS), k); self.assertIn(k, strings_fr.FR, k)

    def test_icon(self):
        self.assertIn("Enemies", gen_textures.TAB_ICONS)

    def test_page(self):
        w = json.dumps(json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json"))))
        for wn in ("EnemyBox", "SldEnemyCount", "SldEnemyDist", "EnemyModes", "EnemyLinks", "EnemyLive", "EnemyHint", "EnemyKinds", "W_EnemyTile"):
            self.assertIn(wn, w, wn)

    def test_select_page_and_tick(self):
        self.assertTrue(calls(g("Select Page"), "Rebuild Enemies"))
        mgr = next(a for a in json.load(open(os.path.join(H, "..", "..", "assets", "50_manager_ui.json")))["assets"] if a.get("path", "").endswith("BP_AltUIManager") and a.get("event_graph"))
        self.assertIn('"Poll Enemies"', json.dumps(mgr["event_graph"]))

    def test_catalog_has_no_humans(self):
        keys = [ui.RAG_KINDS[k][0] for k in ui.ENEMY_KINDS]
        self.assertNotIn("Npc", keys); self.assertNotIn("Mercenary", keys); self.assertIn("Brute", keys)

    def test_settings_saved(self):
        import gen_manager as gm
        src = open(gm.__file__).read()
        for v in ("EnemyCount", "EnemyMode", "EnemyActiveMode"): self.assertIn('("%s", "%s", "copy", None)' % (v, v), src, v)
        self.assertIn('("EnemyDist", "EnemyDistM", "copy", None)', src)   # renamed with the 2 m default (the old 8 m is not carried over)


class Spawn(unittest.TestCase):
    def test_spawn_chain(self):
        s = g("Enemy Spawn One"); f = [n.get("function") for n in s["nodes"]]
        order = [x for x in f if x in ("on Spawn in Runtime", "Set Loot Item with Name", "Change Ai Mode", "Enemy Apply Mode")]
        self.assertIn("on Spawn in Runtime", order); self.assertLess(order.index("on Spawn in Runtime"), order.index("Enemy Apply Mode"))
        js = json.dumps(s)
        self.assertIn("AdjustIfPossibleButAlwaysSpawn", js); self.assertNotIn("SetActorHiddenInGame", f); self.assertNotIn("K2_DestroyActor", f)
        loot = [n for n in s["nodes"] if n.get("function") == "Set Loot Item with Name"]
        self.assertEqual(len(loot), 1); self.assertEqual(loot[0].get("in", {}).get("item"), "None")

    def test_modes(self):
        a = json.dumps(g("Enemy Apply Mode"))
        # Zombie_AIMode bytes 1 / 2 / 4 as the stub's INTERNAL names NewEnumerator<byte - 1>: the display names ("ChasePlayer") compiled
        # to 0 = None - every spawned zombie stood still (cooked bytecode, 2026-10-30)
        for m in ("NewEnumerator0", "NewEnumerator1", "NewEnumerator3"): self.assertIn('"%s"' % m, a)
        for m in ("NoSoul", "Inactive", "ChasePlayer"): self.assertNotIn('"mode": "%s"' % m, a)
        for f in ("Change Target Character", "Stop Following Path", "Start Wait", "Change Ai Mode"): self.assertIn(f, a)

    def test_spawn_count_and_room(self):
        s = g("Enemy Spawn"); js = json.dumps(s)
        self.assertIn("EnemyCount", js); self.assertIn("En_NoRoom", js); self.assertIn("K2_ProjectPointToNavigation", js)

    def test_places_close_and_enough(self):
        import math
        c = ui.EN_CANDIDATES
        self.assertGreaterEqual(len(c), ui.EN_COUNT_MAX)   # one click can place EnemyCount enemies
        self.assertEqual(c[0], (0.0, 0.0)); d = [round(math.hypot(*p)) for p in c]; self.assertEqual(d, sorted(d))   # nearest first (ring by ring)
        gaps = [min(math.hypot(a[0] - b[0], a[1] - b[1]) for b in c if b is not a) for a in c]
        self.assertGreaterEqual(min(gaps), 70.0); self.assertLessEqual(max(gaps), 80.0)   # side by side, capsules not inside each other
        self.assertLessEqual(ui.EN_DIST_MIN, ui.RAG_DIST / 100.0)   # as near as a ragdoll

    def test_dispatch(self):
        a = json.dumps(g("On Menu Action")); self.assertIn("Enemy Action", a)
        self.assertIn("EnZ:", json.dumps(g("Enemy Action"))); self.assertTrue(calls(g("Enemy Kind Clicked"), "Enemy Spawn"))


class Control(unittest.TestCase):
    def test_set_mode_applies_to_all(self):
        s = g("Enemy Set Mode"); self.assertTrue(calls(s, "Enemy Apply Mode")); self.assertTrue(calls(s, "Enemy Prune"))
        self.assertIn("EnemyActiveMode", json.dumps(s)); self.assertIn("Save Settings Soon", json.dumps(s))

    def test_remove_and_kill(self):
        self.assertIn("Remove Me", json.dumps(g("Enemy Remove All"))); self.assertIn("Remove Me", json.dumps(g("Enemy Remove Nearest")))
        k = g("Enemy Kill All"); gh = [n for n in k["nodes"] if n.get("function") == "Got Hurt"]
        self.assertEqual(len(gh), 1); self.assertIn(gh[0].get("in", {}).get("murderer", "None"), ("None", None, ""))

    def test_toggle_and_chip(self):
        self.assertTrue(calls(g("Enemy Toggle Passive"), "Enemy Set Mode")); self.assertTrue(calls(g("Enemy Mode Chip"), "Enemy Set Mode"))
        a = json.dumps(g("Enemy Action"))
        for k in ("EnRemove", "EnNearest", "EnKill", "EnPassive"): self.assertIn(k, a)


if __name__ == "__main__": unittest.main()


class Quick(unittest.TestCase):
    def test_kind_everywhere(self):
        for f in ("Quick Find", "Quick Item Caption", "Quick Item Icon", "Run Quick Item"):
            self.assertTrue(any(n.get("function") == "EqualEqual_StrStr" and n.get("in", {}).get("B") == "enemy" for n in g(f)["nodes"]), f)
        self.assertTrue(calls(g("Run Quick Item"), "Run Enemy Item"))

    def test_catalog_group(self):
        js = json.dumps(g("Act Catalog Build"))
        for it in ("enemy:remove", "enemy:kill", "enemy:passive", "enemy:spawn:"): self.assertIn(it, js)

    def test_run(self):
        r = json.dumps(g("Run Enemy Item"))
        for f in ("Enemy Spawn", "Enemy Remove All", "Enemy Kill All", "Enemy Toggle Passive"): self.assertIn(f, r)
