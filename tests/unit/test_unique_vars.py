"""Every generated blueprint declares each variable once (names compare case-insensitively, like the engine's).

2026-10-04: the virtual outfit list's state variables took the prefix "Outfit", so its column count became OutfitCols - the very
setting "pieces per row": the list wrote how many tiles fit side by side into it, the tiles were drawn with that grid and Options ›
Tiles showed it."""
import unittest, os, glob, json, collections

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


class UniqueVariables(unittest.TestCase):
    def test_no_duplicate_variables(self):
        bad = []
        for f in sorted(glob.glob(os.path.join(ASSETS, "*.json"))):
            for a in json.load(open(f)).get("assets", []):
                names = collections.Counter(v["name"].lower() for v in a.get("variables", []))
                bad += ["%s %s" % (a["path"], n) for n, c in names.items() if c > 1]
        self.assertEqual(bad, [])


if __name__ == "__main__": unittest.main()
