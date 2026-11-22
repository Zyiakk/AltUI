"""Backward compatibility of Get AltUI Greyed (internal design notes), the cooked side:
fixtures/modui_old_example/AltUIMod_Example-3.0.0.pak is the example mod as shipped before the function existed (built
against the older BPI_AltUIMod). Its class implements the interface by AltUI's path - in the game it resolves to the new one
in AltUI.pak - and has no function of that name. UClass::FindFunctionByName then falls back to the interface's own function,
which has no bytecode, so AltUI's output stays at its zero default = not greyed; a mod that implements the new interface but
leaves the function empty answers false as well (tests/editor/test_modui_greyed.py, kit). The same path carried the Key pair
for older mods (in game, ui-test-36 A)."""
import unittest, os, sys, tempfile, json
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, "..", "..", "scripts")); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
import modui as mu
from pak11_extract import Pak
import uasset_funcs
from uasset_props import read_summary

OLD = os.path.join(H, "fixtures", "modui_old_example", "AltUIMod_Example-3.0.0.pak")


class OldExample(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(); pk = Pak(OLD); cls.ua = None
        for k in pk.files:
            if "BP_AltUIModExample." in k:
                p = os.path.join(cls.tmp.name, k.rsplit("/", 1)[-1]); open(p, "wb").write(pk.read(k))
                if p.endswith(".uasset"): cls.ua = p

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_old_class_lacks_the_function(self):
        fns = uasset_funcs.dump(self.ua)["functions"]
        for f in (mu.GET_VALUE, mu.GET_COLOR, mu.GET_TEXT, mu.GET_KEY): self.assertIn(f, fns, "the fixture is the real old example")
        self.assertNotIn(mu.GET_GREYED, fns)

    def test_old_class_implements_the_interface_by_altuis_path(self):
        _, names, imps, _, _ = read_summary(self.ua)
        self.assertIn(mu.INTERFACE, json.dumps(imps) + json.dumps(names))


if __name__ == "__main__":
    unittest.main()
