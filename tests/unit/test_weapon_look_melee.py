"""Apply Weapon Look must dress melee weapons too.

A knife or a hatchet is no Weapon_Gun_Base: the impure cast to it fails. From 2026-09-22 to 2026-10-07 its CastFailed
exit was unwired (waived with miss="ignore"), so the function ended right there for every melee weapon - their models
and skins were stored, shown as chosen, and never put on the weapon in Jodi's hand. Only the gun-specific steps (the
game's paint) may depend on that cast."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def function(name):
    def find(o):
        if isinstance(o, dict):
            if o.get("name") == name and isinstance(o.get("graph"), dict): return o
            for v in o.values():
                r = find(v)
                if r: return r
        elif isinstance(o, list):
            for v in o:
                r = find(v)
                if r: return r
    return find(json.load(open(os.path.join(ASSETS, "50_manager_ui.json"), encoding="utf-8")))["graph"]


def reachable_without(g, cut):
    """Node ids reachable from entry when node <cut> only ever leaves through its CastFailed exit."""
    out = {}                                           # node id -> successors over any of its exits
    for chain in g["exec"]:
        for a, b in zip(chain, chain[1:]):
            if a == cut: continue                      # the success exit of the failed cast
            out.setdefault(a.split(":")[0], []).append(b.split(":")[0])
    seen, todo = set(), ["entry"]
    while todo:
        n = todo.pop()
        if n not in seen:
            seen.add(n); todo += out.get(n, [])
    return seen


class MeleeWeaponLook(unittest.TestCase):
    def setUp(self):
        self.g = function("Apply Weapon Look")
        self.nodes = {n["id"]: n for n in self.g["nodes"]}

    def gun_cast(self):
        ids = [i for i, n in self.nodes.items() if n["kind"] == "cast" and n.get("class", "").endswith("Weapon_Gun_Base") and not n.get("pure", True)]
        self.assertEqual(len(ids), 1, ids)
        return ids[0]

    def test_model_and_sound_are_reached_when_the_weapon_is_no_gun(self):
        got = reachable_without(self.g, self.gun_cast())
        for step in ("asd", "am"):
            self.assertIn(step, got, "%s (%s) is not reached for a melee weapon" % (step, self.nodes[step].get("function")))


if __name__ == "__main__": unittest.main()
