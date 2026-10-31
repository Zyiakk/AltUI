"""A look as an enemy (docs/notes/2026-10-30-look-als-gegner.md): a follower record of MODE_ENEMY that the NPC AI turns on Jodi."""
import json, os, sys, unittest
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
import followers as f
ASSETS = os.path.join(H, "..", "..", "assets")


def graph(name):
    for fn_ in ("30_manager.json", "50_manager_ui.json"):
        for a in json.load(open(os.path.join(ASSETS, fn_)))["assets"]:
            for e in a.get("functions", []):
                if e.get("name") == name and e.get("graph"): return e["graph"]
    raise AssertionError(name)


def calls(g, fname): return [n for n in g["nodes"] if n.get("function") == fname]


class Enemy(unittest.TestCase):
    def test_mode_is_its_own(self):
        self.assertNotIn(f.MODE_ENEMY, (f.MODE_FOLLOWER, f.MODE_NPC, 3))   # 3 = FolSpawnMode "new look for a record"

    def test_only_in_its_level_at_its_place(self):
        # an enemy's order is "follow" (the chase), yet it is no follower: it stays in its level, at its place
        self.assertTrue(f.comes_on_level_start(True, False, f.MODE_ENEMY, f.ORDER_FOLLOW, "Lv1", "Lv1"))
        self.assertFalse(f.comes_on_level_start(True, False, f.MODE_ENEMY, f.ORDER_FOLLOW, "Lv1", "Lv2"))
        self.assertTrue(f.spawn_at_place(f.MODE_ENEMY, f.ORDER_FOLLOW, "Lv1", "Lv1"))

    def test_menu_entry(self):
        self.assertIn("LookEnemy", json.dumps(graph("On Look Context")))
        self.assertTrue([n for n in graph("Spawn Look As Enemy")["nodes"] if n.get("in", {}).get("mode") == str(f.MODE_ENEMY)])

    def test_guard_turns_it_on_jodi(self):
        g = graph("Fol Npc Guard"); js = json.dumps(g)
        self.assertTrue(calls(g, "Change Target Zombie")); self.assertIn('"Order Flags": "1"', js)

    def test_new_enemy_gets_gun_and_ammo(self):
        g = graph("Finish Look Follower")
        self.assertTrue(calls(g, "Got A Gun")); self.assertIn("InfAmmo", json.dumps(g))

    def test_leaving_enemy_mode_lets_go(self):
        self.assertTrue(calls(graph("Fol Set Mode"), "Change Target Zombie"))


    def test_hostile_to_everyone(self):
        # its guns no longer skip Jodi (the weapon's ignore list), char type 1 (followers find it), no NPC to the others
        js = json.dumps(graph("Fol Npc Guard"))
        self.assertIn("Actors to Ignore Trace", js); self.assertIn('"char type": "1"', js); self.assertIn('"IsEnemy": "true"', js)
        self.assertTrue(calls(graph("Fol Npc Guard"), "Fol Defend"))
        self.assertTrue(calls(graph("Fol Defend"), "Change Target Zombie"))
        f = {a["path"].rsplit("/", 1)[1]: a for a in json.load(open(os.path.join(ASSETS, "29b_follower.json")))["assets"]}["BP_AltUIFollower"]
        self.assertTrue({"is Npc ?", "on Damage Event"} <= {x["name"] for x in f["functions"]})
        back = json.dumps(graph("Fol Set Mode")); self.assertIn("Array_AddUnique", back); self.assertIn('"IsEnemy": "false"', back)


    def test_fights_followers_too(self):
        # play test 2026-10-30: it only fought Jodi - its target is the nearest living one of Jodi and the other figures
        self.assertTrue(calls(graph("Fol Npc Guard"), "Enemy Target"))
        js = json.dumps(graph("Enemy Target")); self.assertIn("FolActors", js); self.assertIn("IsEnemy", js)

    def test_dead_target_is_dropped(self):
        # the Grim Reaper killed by magic hides without a ragdoll: followers kept attacking the air - a dead target is let go
        g = graph("Fol Defend"); ids = {x["id"]: x for x in g["nodes"]}
        self.assertEqual(ids["tz0"]["in"]["Zombie in front of me"], "None"); self.assertIn(["btv", "ct0", "tz0", "sbd"], [c[-4:] for c in g["exec"] if "tz0" in c])


class ZombieMode(unittest.TestCase):
    def test_mode_is_set_until_it_holds(self):
        # right after the spawn the zombie's Ai Controller is not set: Change Ai Mode did nothing, it stood in mode None (ENEMYLOG 2026-10-30)
        self.assertIn("EnemyModePending", json.dumps(graph("Enemy Apply Mode")))
        g = graph("Enemy Mode Watch"); self.assertTrue(calls(g, "Get Ai Mode")); self.assertTrue(calls(g, "Map_Remove"))
        self.assertTrue([n for n in g["nodes"] if n.get("function") == "Enemy Apply Mode"])
        gd = graph("Fol Npc Guard"); self.assertIn(["b:else", "emw"], gd["exec"])   # runs without figures in the world too

    def test_mode_goes_to_the_controller(self):
        # the zombie's own Change Ai Mode needs its Ai Controller variable - a runtime spawn never got it (ENEMYLOG round 2)
        g = graph("Enemy Apply Mode"); cm = [n for n in g["nodes"] if n.get("function") == "Change Ai Mode"]
        self.assertEqual(len(cm), 3); self.assertTrue(all(n["class"].endswith("/AI_Controller") for n in cm), [n["class"] for n in cm])


class Bodies(unittest.TestCase):
    def test_remove_all_takes_the_bodies(self):
        # play test 2026-10-30: killed zombies could not be removed any more (Enemy Prune dropped them from the list)
        self.assertIn("EnemyBodies", json.dumps(graph("Enemy Prune")))
        g = graph("Enemy Remove All"); self.assertIn("EnemyBodies", json.dumps(g)); self.assertTrue(calls(g, "K2_DestroyActor"))


class Cursor(unittest.TestCase):
    def test_hit_does_not_take_the_cursor(self):
        # a hit on Jodi hides the cursor (PlayingHud.Hide All Visible Panels): Focus Guard gives it back while the panel is open
        g = graph("Focus Guard"); js = json.dumps(g)
        self.assertIn('"bShowMouseCursor": "true"', js); self.assertTrue(calls(g, "SetInputMode_GameAndUIEx")); self.assertTrue(calls(g, "Set Input Control Enabled"))



class EnemiesPage(unittest.TestCase):
    def test_views(self):
        js = json.dumps(graph("Rebuild Enemies")); self.assertIn("EnView:1", js); self.assertTrue(calls(graph("Rebuild Enemies"), "Rebuild Followers"))
        self.assertIn("EnView:", json.dumps(graph("Enemy Mode Chip")))

    def test_rows_split_by_page(self):
        g = graph("Rebuild Followers Body"); js = json.dumps(g)   # KEEP_SCROLL wrapper: the body is its own function
        self.assertIn('"Enemies"', js); self.assertIn("EnemyActors", js); self.assertIn(f.STATE_ENEMY, js)
        for a in ("EnOne4", "EnOne2", "EnOne1", "EnOneR", "EnOneK"): self.assertIn(a, js)

    def test_one_zombie(self):
        g = graph("Enemy One Action")
        for fn_ in ("Remove Me", "Got Hurt", "Enemy Apply Mode"): self.assertTrue(calls(g, fn_), fn_)
        self.assertTrue(calls(graph("Enemy Action"), "Enemy One Action"))

    def test_rows_know_kind_and_mode(self):
        self.assertIn("EnemyKindOf", json.dumps(graph("Enemy Spawn One"))); self.assertIn("EnemyModeOf", json.dumps(graph("Enemy Apply Mode")))

    def test_state_key(self):
        self.assertEqual(f.state_key(f.MODE_ENEMY, f.ORDER_FOLLOW, True, False), f.STATE_ENEMY)


if __name__ == "__main__":
    unittest.main()
