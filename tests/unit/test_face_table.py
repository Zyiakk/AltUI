"""Face tab data: the entry table (assets/gen/face.py) names only morphs the body mesh Female has, every caption has a
string, and the assets and fields that hold a face exist."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
import face as fc
from strings import STRINGS

ASSETS = os.path.join(H, "..", "..", "assets")
# morph targets of /Game/Project/Character/Jodi/Body/Female (name table of the cooked mesh, docs/notes/2026-09-27-gesichtsausdruck-override.md)
FEMALE_MORPHS = {"Face_Eye2Down", "Face_Eye2Left", "Face_Eye2Right", "Face_Eye2Up", "Face_Focus", "Face_Fright", "Face_Idle", "Face_Pain",
                 "Face_Smile", "Face_Sufferring01", "Face_Sufferring02", "Face_Tired", "Mouth_AH CDG KN", "Mouth_BPM", "Mouth_EE", "Mouth_FV",
                 "Mouth_TH L", "Mouth_UU OO", "Mouth_Zh Ch SH RI", "Nipple"}


def load(fname):
    with open(os.path.join(ASSETS, fname)) as f:
        return json.load(f)["assets"]


def asset(path, fname="30_manager.json"):
    for a in load(fname):
        if a.get("path") == path: return a
    raise AssertionError("asset %s missing" % path)


class FaceTable(unittest.TestCase):
    def test_morphs_exist_on_the_mesh(self):
        self.assertEqual(len(fc.ENTRIES), 18); self.assertEqual(len(fc.MORPHS), 19); self.assertEqual(len(set(fc.MORPHS)), 19)
        for m in fc.MORPHS: self.assertIn(m, FEMALE_MORPHS)
        for k in fc.KEYS: self.assertTrue(k in FEMALE_MORPHS or k in fc.VIRTUAL, k)

    def test_close_mouth_counters_the_open_mouth(self):
        self.assertEqual(fc.VIRTUAL, {"Mouth_Close": ("Mouth_AH CDG KN", -1.0)})
        self.assertIn(("MouthClose", "FaceMouth", None, "Mouth_Close"), fc.ENTRIES)
        self.assertEqual(len(fc.EXPRESSIONS), 8)

    def test_groups_and_captions(self):
        for key, group, neg, pos in fc.ENTRIES:
            self.assertIn(group, fc.GROUPS); self.assertIn("Face_" + key, STRINGS)
            self.assertEqual(neg is not None, group == "FaceEyes", key)   # only the gaze is bipolar
        for g in fc.GROUPS + [fc.SAVED]: self.assertIn("Cat_" + g, STRINGS)

    def test_assets(self):
        members = {p["name"] for p in asset(fc.S_FACE)["members"]}
        self.assertEqual(members, {"Name", "Id", "Values", "FaceAdd"})
        self.assertEqual({v["name"] for v in asset(fc.SG_FACES)["variables"]}, {"Faces", "NextId"})
        self.assertIn("Face", {p["name"] for p in asset("/Game/Mod/AltUI/S_Snapshot")["members"]})
        sg = {v["name"] for v in asset("/Game/Mod/AltUI/SG_AltUI")["variables"]}
        self.assertTrue({"Face", "LastFaceGroup", "FaceAdd"} <= sg)


if __name__ == "__main__":
    unittest.main()
