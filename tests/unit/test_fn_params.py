"""A function's inputs and outputs must not share a name: cooked bytecode resolves local properties by name, so an output named like an
input ends up on the input property and EX_LocalOutVariable walks off the OutParms list -> null read in the Blueprint VM
(2026-09-21: 'Vector Or One(v) -> v' crashed the game at level start, while the editor - live property pointers - ran it fine)."""
import unittest, os, glob, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def functions(o):
    if isinstance(o, dict):
        if "name" in o and "outputs" in o and ("inputs" in o or "graph" in o): yield o   # fn() omits empty inputs / outputs
        for v in o.values(): yield from functions(v)
    elif isinstance(o, list):
        for v in o: yield from functions(v)


class FnParams(unittest.TestCase):
    def test_inputs_and_outputs_share_no_name(self):
        files = sorted(glob.glob(os.path.join(ASSETS, "*.json"))); self.assertTrue(files); n = 0
        for f in files:
            for fn in functions(json.load(open(f))):
                names = [p["name"].lower() for p in (fn.get("inputs") or []) + (fn.get("outputs") or [])]; n += 1
                self.assertEqual(len(names), len(set(names)), "%s %s: duplicate parameter name" % (os.path.basename(f), fn["name"]))
        self.assertGreater(n, 50)
