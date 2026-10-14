"""Cutscenes must not cost the body shape. At the end of a level sequence with an animation track (completion mode
RestoreState) UE 4.27 restores Jodi's anim instance and calls InitializeAnimScriptInstance(true) on her mesh
(MovieSceneSkeletalAnimationTemplate.cpp, FPreAnimatedAnimationTokenProducer::RestoreState). With bForceReinit the
post-process instance is spawned anew (SkeletalMeshComponent.cpp, NeedToSpawnPostPhysicsInstance) - a fresh ABP_BodyScale
with its class defaults, so the body's default bone scales and every slider are gone until Apply Body Scales runs again
(Nexus report 2026-10-07, docs/notes/2026-10-07-cutscene-body-reset.md).

Body Scale Watch (every frame) compares the mesh's post-process instance with the one Apply Body Scales last wrote to and
re-applies on a change - only bone scales and physics, no clothing (towel), no materials (mutation)."""
import unittest, os, json

from test_apply_body import find_fn, ASSETS


def load():
    with open(os.path.join(ASSETS, "50_manager_ui.json"), encoding="utf-8") as f:
        return json.load(f)


def chains_from(g, start):
    """Every exec node reachable from start."""
    adj = {}
    for chain in g.get("exec", []):
        for a, b in zip(chain, chain[1:]): adj.setdefault(a.split(":")[0], set()).add(b.split(":")[0])
    seen, stack = set(), [start]
    while stack:
        n = stack.pop()
        if n in seen: continue
        seen.add(n); stack += list(adj.get(n, ()))
    return seen


def event_graphs(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "event_graph" and isinstance(v, dict): yield v
            else: yield from event_graphs(v)
    elif isinstance(o, list):
        for v in o: yield from event_graphs(v)


class BodyScaleWatch(unittest.TestCase):
    def setUp(self):
        self.d = load()
        self.watch = find_fn(self.d, "Body Scale Watch")
        self.assertIsNotNone(self.watch, "Body Scale Watch not found in 50_manager_ui.json")

    def test_reapplies_on_a_new_post_process_instance(self):
        g = self.watch["graph"]; nodes = {n["id"]: n for n in g["nodes"]}
        fns = {n.get("function") for n in nodes.values()}
        self.assertIn("GetPostProcessInstance", fns)
        self.assertTrue(fns & {"EqualEqual_ObjectObject", "NotEqual_ObjectObject"}, "no comparison with the remembered instance")
        self.assertIn("LastPostProcess", {n.get("var") for n in nodes.values() if n.get("kind") == "get"})
        ap = [i for i, n in nodes.items() if n.get("kind") == "call_self" and n.get("function") == "Apply Body Scales"]
        self.assertTrue(ap, "Body Scale Watch never calls Apply Body Scales")
        self.assertIn(ap[0], chains_from(g, "entry"))

    def test_touches_neither_clothes_nor_materials(self):
        fns = {n.get("function") for n in self.watch["graph"]["nodes"]}
        for f in ("Apply Body", "Apply Saved Body", "Apply Saved Colors", "Apply Face", "Fix Loaded Underwear", "Apply Nude",
                  "Load Player Makeup", "SetSkeletalMesh"):
            self.assertNotIn(f, fns)

    def test_only_while_scales_are_ours(self):
        """No ABP_BodyScale -> ScaleActive false -> nothing to restore (and nothing before the Version Gate lets AltUI start)."""
        self.assertIn("ScaleActive", {n.get("var") for n in self.watch["graph"]["nodes"] if n.get("kind") == "get"})

    def test_apply_body_scales_remembers_the_instance(self):
        abs_ = find_fn(self.d, "Apply Body Scales"); g = abs_["graph"]
        sets = [n["id"] for n in g["nodes"] if n.get("kind") == "set" and n.get("var") == "LastPostProcess"]
        self.assertTrue(sets, "Apply Body Scales does not remember the post-process instance")
        self.assertIn(sets[0], chains_from(g, "entry"))

    def test_runs_every_frame(self):
        found = False
        for eg in event_graphs(self.d):
            ids = [n["id"] for n in eg.get("nodes", []) if n.get("kind") == "call_self" and n.get("function") == "Body Scale Watch"]
            if ids:
                self.assertIn(ids[0], chains_from(eg, "tick")); found = True
        self.assertTrue(found, "no event graph calls Body Scale Watch")


if __name__ == "__main__": unittest.main()
