"""Node ids of a graph must be unique case-insensitively: BPGen keeps them in a TMap<FString,...>
(FString keys compare case-insensitively in UE), Ids.Add silently overwrites -> links end up on the wrong
node (2026-09-15: 'bD'/'bd' in 'On Menu Action' -> endless loop, game freezes)."""
import unittest, os, sys, glob, json, collections
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
from bpdsl import G

ASSETS = os.path.join(H, "..", "..", "assets")


def graphs(o):
    """all {nodes, links, exec} objects of an asset JSON"""
    if isinstance(o, dict):
        if isinstance(o.get("nodes"), list) and "exec" in o: yield o
        for v in o.values(): yield from graphs(v)
    elif isinstance(o, list):
        for v in o: yield from graphs(v)


class GraphIds(unittest.TestCase):
    def test_dsl_rejects_duplicate_id(self):
        g = G(); g.branch("bd")
        with self.assertRaises(ValueError): g.branch("bd")
        with self.assertRaises(ValueError): g.branch("bD")   # FString comparison is case-insensitive

    def test_generated_assets_have_unique_ids(self):
        files = sorted(glob.glob(os.path.join(ASSETS, "*.json"))); self.assertTrue(files)
        for f in files:
            for g in graphs(json.load(open(f))):
                seen = collections.defaultdict(list)
                for n in g["nodes"]: seen[n["id"].lower()].append(n["id"])
                dup = {k: v for k, v in seen.items() if len(v) > 1}
                self.assertEqual(dup, {}, os.path.basename(f))
