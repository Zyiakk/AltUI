"""Ragdolls: every zombie / NPC class the page offers, and every picture it shows, exists in the game (the file list of the game paks, $GAME_PAK_FILELIST as in config.sh;
without it those two checks are skipped).
A wrong path only shows in the game: the class does not load and the link does nothing."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
import gen_manager_ui as ui

LIST = os.environ.get("GAME_PAK_FILELIST") or os.path.join(H, "..", "..", "knowledge", "game_pak_filelist.txt")
FILES = set(l.strip() for l in open(LIST)) if os.path.exists(LIST) else None
need_list = unittest.skipUnless(FILES, "no game pak file list (GAME_PAK_FILELIST)")


def game_file(obj_path):
    """/Game/X/Y.Y_C -> TheKillingAntidote/Content/X/Y.uasset"""
    return "TheKillingAntidote/Content/" + obj_path.split(".")[0][len("/Game/"):] + ".uasset"


class RagKinds(unittest.TestCase):
    @need_list
    def test_classes_exist(self):
        missing = [c[2] for c in ui.RAG_CLASSES if game_file(c[2]) not in FILES]
        self.assertEqual(missing, [])

    @need_list
    def test_pictures_exist(self):
        self.assertEqual([p for p in ui.RAG_KIND_PIC.values() if game_file(p) not in FILES], [])

    def test_every_kind_has_a_base_class_first(self):
        for k in range(len(ui.RAG_KINDS)):
            self.assertIsNone(ui.RAG_CLASSES[ui.RAG_KIND_FIRST[k]][1])

    def test_variant_texts(self):
        import strings
        for c in ui.RAG_CLASSES:
            if c[1]: self.assertIn("Rag_Var" + c[1], strings.STRINGS)
        for key, *_ in ui.RAG_KINDS: self.assertIn("Rag_Kind" + key, strings.STRINGS)

    def test_pose_types(self):
        """Saved poses go by base kind: every class (variants too) maps to its kind's key, Jodi copies (no class) to Jodi."""
        self.assertEqual(sorted(ui.RAG_POSE_TYPES), sorted(c[2] for c in ui.RAG_CLASSES))
        for k, v, c in ui.RAG_CLASSES: self.assertEqual(ui.RAG_POSE_TYPES[c], ui.RAG_KINDS[k][0])
        self.assertEqual(ui.RAG_POSE_TYPES["/Game/Project/Zombie/Brute_Armed.Brute_Armed_C"], "Brute")
        self.assertNotIn("Jodi", ui.RAG_POSE_TYPES.values())


if __name__ == "__main__":
    unittest.main()
