"""2026-11-16: Build Catalog was ~0.7 s of every level start. A level start builds only what it needs at once (Catalog Begin:
ItemSlot, the mods' origins); the rest follows in the background (Catalog Tick), finished at once wherever the catalog is read
(Ensure Catalog: panel, quick menu, a key of the player's, a look as ragdoll)."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def manager():
    fns, eg = {}, None
    for f in ("30_manager.json", "50_manager_ui.json"):
        with open(os.path.join(ASSETS, f)) as fh:
            for a in json.load(fh)["assets"]:
                if a.get("path", "").endswith("/BP_AltUIManager"):
                    fns.update({e["name"]: e["graph"] for e in a.get("functions", []) if e.get("graph")}); eg = a.get("event_graph") or eg
    return fns, eg


def calls(g, f): return [n["id"] for n in g["nodes"] if n.get("function") == f]


class Catalog(unittest.TestCase):
    def setUp(self): self.f, self.eg = manager()

    def test_level_start_only_begins(self):
        ids = {n["id"]: n for n in self.eg["nodes"]}; self.assertEqual(ids["bc"]["function"], "Catalog Begin")
        self.assertEqual(calls(self.f["Catalog Begin"], "Mod Origins"), ["smi"])
        self.assertTrue(calls(self.f["Catalog Begin"], "Map_Add"))   # ItemSlot at once
        self.assertFalse(calls(self.f["Catalog Begin"], "Sort Key"))
        self.assertEqual(ids["tcat"]["function"], "Catalog Tick")

    def test_whole_build_is_the_steps(self):
        self.assertEqual([c for c in self.f["Build Catalog"]["exec"]], [["entry", "cb", "cf"]])
        fin = self.f["Catalog Finish"]; self.assertTrue(calls(fin, "Catalog Rows") and calls(fin, "Catalog Slot") and calls(fin, "Catalog End"))

    def test_readers_ensure(self):
        for name in ("Open Panel", "Open Quick Wheel", "Quick Release", "Look Ragdoll Poll", "Bind Run"):
            self.assertEqual(calls(self.f[name], "Ensure Catalog"), ["ensc"], name)
        self.assertEqual(self.f["Open Panel"]["exec"][0][:2] if self.f["Open Panel"]["exec"][0][0] == "entry" else
                         next(c for c in self.f["Open Panel"]["exec"] if c[0] == "entry")[:2], ["entry", "ensc"])


if __name__ == "__main__":
    unittest.main()
