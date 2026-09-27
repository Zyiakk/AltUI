"""Every call_self of an asset must name a function that asset declares. BPGen only finds this after minutes in the
editor ("function not in skeleton class"), and an augmenting asset may add functions to a class another file created,
so the check collects the declarations of all asset files per path first."""
import unittest, os, json, collections
H = os.path.dirname(os.path.abspath(__file__)); ASSETS = os.path.join(H, "..", "..", "assets")


def call_targets():
    decl = collections.defaultdict(set); calls = collections.defaultdict(list)
    for f in sorted(os.listdir(ASSETS)):
        if not f.endswith(".json"):
            continue
        for a in json.load(open(os.path.join(ASSETS, f))).get("assets", []):
            path = a.get("path")
            for fn in a.get("functions", []):
                decl[path].add(fn["name"])
            for g in [fn.get("graph") for fn in a.get("functions", [])] + [a.get("event_graph")]:
                for n in (g or {}).get("nodes", []):
                    if n.get("kind") == "call_self":
                        calls[path].append((f, n.get("function")))
    return decl, calls


class CallTargets(unittest.TestCase):
    def test_every_call_self_has_a_function(self):
        decl, calls = call_targets()
        missing = ["%s %s -> %s" % (f, path, name) for path, cs in calls.items() for f, name in cs if name not in decl[path]]
        self.assertEqual(sorted(set(missing)), [])


if __name__ == "__main__": unittest.main()
