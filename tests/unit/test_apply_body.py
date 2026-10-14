"""Apply Body must restore what SetSkeletalMesh destroys: the morph curves (the "Nipple" morph among them, set by the
game's `update body mask`) and the physics state (`Enable Boobs Physics`). USkeletalMeshComponent::SetSkeletalMesh
calls ClearMorphTargets() - MorphTargetCurves.Empty() - and recreates the physics state when the physics asset differs.
Without these two calls the nipple stays round under clothes after a body swap, until the next dressing action calls
`update body mask` again (user report "nipple skin breakage", 2026-09-26)."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def find_fn(o, name):
    if isinstance(o, dict):
        if o.get("name") == name and isinstance(o.get("graph"), dict): return o
        for v in o.values():
            r = find_fn(v, name)
            if r is not None: return r
    elif isinstance(o, list):
        for v in o:
            r = find_fn(v, name)
            if r is not None: return r
    return None


class ApplyBody(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ASSETS, "50_manager_ui.json"), encoding="utf-8") as f:
            self.fn = find_fn(json.load(f), "Apply Body")
        self.assertIsNotNone(self.fn, "Apply Body not found in 50_manager_ui.json")

    def calls(self):
        return {n["id"]: n.get("function") for n in self.fn["graph"]["nodes"] if n.get("kind") == "call"}

    def main_chain(self):
        for chain in self.fn["graph"]["exec"]:
            if chain and chain[0] == "entry": return [s.split(":")[0] for s in chain]
        self.fail("no exec chain starting at entry")

    def test_mask_and_physics_are_called_after_the_swap(self):
        calls, chain = self.calls(), self.main_chain()
        ids = {f: i for i, f in calls.items() if f in ("update body mask", "Enable Boobs Physics", "SetSkeletalMesh")}
        for f in ("update body mask", "Enable Boobs Physics"):
            self.assertIn(f, ids, f + " is never called in Apply Body")
            self.assertIn(ids[f], chain, f + " hangs in no exec chain from entry")
        self.assertLess(chain.index(ids["SetSkeletalMesh"]), chain.index(ids["update body mask"]))
        self.assertLess(chain.index(ids["SetSkeletalMesh"]), chain.index(ids["Enable Boobs Physics"]))


if __name__ == "__main__": unittest.main()
