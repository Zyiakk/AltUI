"""Every node an exec chain names exists in its graph. A missing one fails only in BPGen, minutes into the build ("exec: unknown node")
- e.g. a comment added in the middle of a generator line that swallowed the statement after it (2026-10-04, QaHeadH)."""
import unittest, os, glob, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_graph_exec import graphs, ASSETS


class ChainIds(unittest.TestCase):
    def test_chain_nodes_exist(self):
        bad = []
        for f in sorted(glob.glob(os.path.join(ASSETS, "*.json"))):
            for name, g in graphs(json.load(open(f))):
                ids = {n["id"] for n in g.get("nodes", [])} | {"entry", "return"}
                for ch in g.get("exec", []):
                    bad += ["%s %s: %s" % (os.path.basename(f), name, x) for x in ch if x.split(":")[0] not in ids]
        self.assertEqual(sorted(set(bad)), [])

    def test_pin_sources_exist(self):
        """"@id.pin" inputs and links name existing nodes (BPGen: "link: unknown node")."""
        bad = []
        def refs(v):
            if isinstance(v, str) and v.startswith("@"): yield v[1:].split(".")[0]
            elif isinstance(v, dict):
                for x in v.values(): yield from refs(x)
            elif isinstance(v, list):
                for x in v: yield from refs(x)
        for f in sorted(glob.glob(os.path.join(ASSETS, "*.json"))):
            for name, g in graphs(json.load(open(f))):
                ids = {n["id"] for n in g.get("nodes", [])} | {"entry", "return"}
                for n in g.get("nodes", []):
                    bad += ["%s %s: %s <- %s" % (os.path.basename(f), name, n["id"], r) for r in refs(n.get("in", {})) if r not in ids]
                for lk in g.get("links", []):
                    for end in (lk if isinstance(lk, list) else [lk]):
                        if isinstance(end, str) and "." in end and end.split(".")[0] not in ids: bad.append("%s %s: link %s" % (os.path.basename(f), name, end))
        self.assertEqual(sorted(set(bad)), [])


if __name__ == "__main__": unittest.main()
