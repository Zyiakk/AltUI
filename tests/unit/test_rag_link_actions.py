"""Links of the Ragdolls page reach Ragdoll Action only through On Menu Action's prefix test StartsWith(name, "Rag"):
every action a rag_link() is built with must start with "Rag" (a follower prototype link "FollowerProto" did not and did
nothing, game test 2026-10-09). An action On Menu Action knows by its exact name (MENU_ACTIONS) works too (Objects page, 2026-10-23)."""
import os, re, unittest
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen", "gen_manager_ui.py")


class RagLinks(unittest.TestCase):
    def test_actions_start_with_rag(self):
        src = open(SRC, encoding="utf-8").read()
        actions = re.findall(r'rag_link\(g, "[^"]+", "([^"]+)"', src)
        self.assertTrue(actions)
        import sys; sys.path.insert(0, os.path.dirname(SRC)); import gen_manager_ui as ui
        exact = {a[0] for a in ui.MENU_ACTIONS}
        self.assertEqual([a for a in actions if not a.startswith("Rag") and a not in exact], [])


if __name__ == "__main__":
    unittest.main()
