"""Every node with an exec pin must be reachable from the entry node, and an impure call must sit in a chain.

A chain that nothing runs is silent: the Blueprint compiles without a warning and the function simply skips that part
(2026-09-22: a comment in the generator swallowed `g.chain("fc", "cc", ...)`, so the weapon icons were rendered without their
skin - and the preview weapon stayed visible in the game because SetVisibleInSceneCaptureOnly never ran).
Only kinds that always carry an exec pin are checked; calls can be pure and then legitimately sit outside every chain.
"""
import unittest, os, glob, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")
EXEC_KINDS = {"branch", "set", "foreach", "spawn", "get_row"}


def graphs(o):
    if isinstance(o, dict):
        if isinstance(o.get("graph"), dict) and "nodes" in o["graph"]: yield o.get("name", "?"), o["graph"]
        for v in o.values(): yield from graphs(v)
    elif isinstance(o, list):
        for v in o: yield from graphs(v)


def reachable(g):
    adj = {}
    for chain in g.get("exec", []):
        for a, b in zip(chain, chain[1:]): adj.setdefault(a.split(":")[0], set()).add(b.split(":")[0])
    seen, stack = set(), ["entry"]
    while stack:
        n = stack.pop()
        if n in seen: continue
        seen.add(n); stack += list(adj.get(n, ()))
    return seen


class GraphExec(unittest.TestCase):
    def test_every_exec_node_runs(self):
        files = sorted(glob.glob(os.path.join(ASSETS, "*.json"))); self.assertTrue(files); n = 0
        for f in files:
            for name, g in graphs(json.load(open(f))):
                seen = reachable(g); n += 1
                dead = [x["id"] for x in g["nodes"] if x.get("kind") in EXEC_KINDS and x["id"] not in seen]
                self.assertEqual(dead, [], "%s %s: unreachable exec nodes %s" % (os.path.basename(f), name, dead))
        self.assertGreater(n, 100)


def declared_purity():
    """{function name: pure?} over every function the assets declare - AltUI's own and the game-class stubs."""
    pure = {}
    for f in sorted(glob.glob(os.path.join(ASSETS, "*.json"))):
        for a in json.load(open(f)).get("assets", []):
            for fn in a.get("functions", []):
                pure[fn["name"]] = pure.get(fn["name"], False) or bool(fn.get("pure"))
    return pure


def impure_self_calls(path):
    """{function name: pure?} over all assets, plus every graph - a call_self of an impure function that hangs outside
    every exec chain is silently pruned by the compiler and answers with the default value ("was pruned because its Exec
    pin is not connected", 2026-09-25: Select Page never rebuilt the weapon models, and the colour probe answered 'no')."""
    pure, out = declared_purity(), []
    for f in sorted(glob.glob(os.path.join(ASSETS, "*.json"))):
        for name, g in graphs(json.load(open(f))):
            inchain = {s.split(":")[0] for c in g.get("exec", []) for s in c}
            for n in g["nodes"]:
                # calls into an AltUI class or a game class: purity is declared, so an impure one outside every chain is a bug
                # (engine libraries are not declared here and are skipped)
                if n.get("kind") in ("call", "call_self") and n.get("function") in pure \
                        and not pure[n["function"]] and n["id"] not in inchain:
                    out.append("%s %s -> %s (%s)" % (os.path.basename(f), name, n.get("function"), n["id"]))
    return out


def dead_calls():
    """Call nodes that neither hang in an exec chain nor feed anyone: the compiler drops them, so an impure one never
    runs (2026-09-25: Build Catalog cleared five of six maps because the chain counted the first five by hand)."""
    out = []
    for f in sorted(glob.glob(os.path.join(ASSETS, "*.json"))):
        for name, g in graphs(json.load(open(f))):
            inchain = {s.split(":")[0] for c in g.get("exec", []) for s in c}
            consumed = {v[1:].split(".")[0] for n in g["nodes"] for v in n.get("in", {}).values()
                        if isinstance(v, str) and v.startswith("@")}
            consumed |= {a.split(".")[0] for a, _ in g.get("links", [])}
            for n in g["nodes"]:
                if n.get("kind") in ("call", "call_self") and n["id"] not in inchain and n["id"] not in consumed:
                    out.append("%s %s -> %s (%s)" % (os.path.basename(f), name, n.get("function"), n["id"]))
    return out


class ImpureCalls(unittest.TestCase):
    def test_impure_calls_are_in_a_chain(self):
        self.assertEqual(impure_self_calls(ASSETS), [])

    def test_no_dead_call_nodes(self):
        self.assertEqual(dead_calls(), [])
