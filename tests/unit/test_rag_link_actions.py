"""Links of the Ragdolls page reach Ragdoll Action only through On Menu Action's prefix test StartsWith(name, "Rag"):
every action a rag_link() is built with must start with "Rag" (a follower prototype link "FollowerProto" did not and did
nothing, game test 2026-10-09)."""
import os, re, unittest
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen", "gen_manager_ui.py")


class RagLinks(unittest.TestCase):
    def test_actions_start_with_rag(self):
        src = open(SRC, encoding="utf-8").read()
        actions = re.findall(r'rag_link\(g, "[^"]+", "([^"]+)"', src)
        self.assertTrue(actions)
        self.assertEqual([a for a in actions if not a.startswith("Rag")], [])


if __name__ == "__main__":
    unittest.main()
