"""Opening AltUI must leave a magnifying scope's aiming alone.

Dress Weapon empties and refills every material slot of the weapon's components, the scope included. The scope keeps the
dynamic instance it writes its aiming into (Scope Material, slot 1) and never looks again: refilled with the plain
material, the lens stayed behind a black ring until the scope was taken off (Discord 2026-10-21). Keep Scope Look puts an
instance back on slot 1, points Scope Material at it and carries Params over - after every Dress Weapon."""
import unittest
from test_weapon_look_melee import function


class KeepScopeLook(unittest.TestCase):
    def test_apply_weapon_look_dresses_then_keeps_the_scope(self):
        g = function("Apply Weapon Look")
        fns = {n["id"]: n.get("function") for n in g["nodes"]}
        self.assertIn(["entry", "dw", "ksl"], g["exec"])
        self.assertEqual((fns["dw"], fns["ksl"]), ("Dress Weapon", "Keep Scope Look"))

    def test_scope_gets_its_instance_and_params_back(self):
        g = function("Keep Scope Look")
        n = {x["id"]: x for x in g["nodes"]}
        self.assertEqual(n["dm"]["in"]["ElementIndex"], "1")
        self.assertEqual(n["ssm"]["var"], "Scope Material")
        self.assertEqual(n["ssm"]["in"]["Scope Material"], "@dm.ReturnValue")
        self.assertEqual(n["sp"]["in"], {"self": "@dm.ReturnValue", "ParameterName": "Params", "Value": "@old.ReturnValue"})
        self.assertEqual(n["old"]["in"]["self"], "@gsm.Scope Material")   # read from the old instance, before it is replaced
        self.assertIn(["fc", "co", "bv", "old", "dm", "ssm", "sp"], g["exec"])



class PanelEndsAiming(unittest.TestCase):
    """Aiming while the panel opened: the release of a held aim button went to the locked input, the view stayed in the scope
    (ui-test-142 #5). The panel tells Jodi what PlayingHud tells her for the game's menus."""
    def check(self, name, show, after):
        g = function(name)
        n = {x["id"]: x for x in g["nodes"]}
        self.assertEqual((n["omd"]["function"], n["omd"]["in"]["show"]), ("on Menu Displayed", show))
        self.assertTrue(any(after in c and "omd" in c and c.index("omd") == c.index(after) + 1 for c in g["exec"]))

    def test_open(self): self.check("Open Panel", "true", "so")
    def test_close(self): self.check("Close Panel", "false", "svc0")


if __name__ == "__main__": unittest.main()
