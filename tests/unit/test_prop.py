"""2026-10-23 (spec 2026-10-23-objects-tab-design): BP_AltUIProp - one spawned model, fixed or with physics."""
import json, os, unittest
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, "..", "..", "assets")
PROP = "/Game/Mod/AltUI/BP_AltUIProp"


def assets(f): return json.load(open(os.path.join(A, f)))["assets"]
def prop(): return next(a for a in assets("28c_prop.json") if a["path"] == PROP)
def fgraph(name): return next(f for f in prop()["functions"] if f["name"] == name)["graph"]


class Actor(unittest.TestCase):
    def test_components(self):
        c = {x["name"]: x for x in prop()["components"]}
        self.assertEqual(list(c), ["Box", "SMesh", "KMesh"])
        self.assertNotIn("parent", c["Box"]); self.assertEqual(c["SMesh"]["parent"], "Box"); self.assertEqual(c["KMesh"]["parent"], "Box")

    def test_functions_and_vars(self):
        self.assertTrue({"Set Model", "Fit Box", "Mesh", "Body", "Set Physics"} <= {f["name"] for f in prop()["functions"]})
        self.assertTrue({"Path", "Label", "Physics", "BoxBody", "Skeletal", "Center"} <= {v["name"] for v in prop()["variables"]})

    def test_box_fallback(self):
        fns = {n.get("function") for n in fgraph("Set Physics")["nodes"]}
        self.assertTrue({"SetSimulatePhysics", "IsSimulatingPhysics", "K2_AttachToComponent"} <= fns)

    def test_set_model_both_kinds(self):
        fns = {n.get("function") for n in fgraph("Set Model")["nodes"]}
        self.assertTrue({"SetStaticMesh", "SetSkeletalMesh", "LoadAsset_Blocking"} <= fns)

    def test_in_manifest(self):
        m = open(os.path.join(A, "manifest.txt")).read().split()
        self.assertLess(m.index("28c_prop.json"), m.index("30_manager.json"))


if __name__ == "__main__":
    unittest.main()
