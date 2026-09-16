"""The manager's Tmp* member variables serve as function locals (BPGen has no locals). A function that writes such a
variable, calls another function that (transitively) writes it too, and reads it afterwards gets the callee's value
("snapshot trap", 2026-09-14: Undo restored the current state). This test walks the exec graph of every manager
function: a read of X that is reachable from a write of X in the same function via a call_self whose callee writes X
(without an intervening own write) is an error. Loop bodies (ForEach/ForLoop macros) are closed with a back edge."""
import unittest, os, json, collections, functools
H = os.path.dirname(os.path.abspath(__file__)); ASSETS = os.path.join(H, "..", "..", "assets")
MANAGER = "/Game/Mod/AltUI/BP_AltUIManager"
LOOP_MACROS = ("ForLoop", "ForLoopWithBreak", "WhileLoop")


def manager_functions():
    """{name: graph} - bodies from 30_manager.json, overridden/added by 50_manager_ui.json (augment); the event graph as '<events>'."""
    fns = {}
    for f in ("30_manager.json", "50_manager_ui.json"):
        for a in json.load(open(os.path.join(ASSETS, f)))["assets"]:
            if a.get("path") != MANAGER: continue
            for fn in a.get("functions", []):
                if "graph" in fn: fns[fn["name"]] = fn["graph"]
            if "event_graph" in a: fns["<events>"] = a["event_graph"]
    return fns


class Graph:
    def __init__(self, g):
        self.nodes = {n["id"]: n for n in g["nodes"]}
        self.succ = collections.defaultdict(list)
        for chain in g["exec"]:
            for a, b in zip(chain, chain[1:]): self.succ[a.split(":")[0]].append(b.split(":")[0])
        self.exec_nodes = set(self.succ) | {b for bs in self.succ.values() for b in bs}
        # data consumers: node id -> ids of nodes reading one of its pins (in: "@id.pin" and explicit links)
        self.consumers = collections.defaultdict(set)
        for n in g["nodes"]:
            for v in n.get("in", {}).values():
                if isinstance(v, str) and v.startswith("@"): self.consumers[v[1:].split(".")[0]].add(n["id"])
        for a, b in g.get("links", []): self.consumers[a.split(".")[0]].add(b.split(".")[0])
        self.is_loop = lambda i: self.nodes.get(i, {}).get("kind") == "foreach" or (self.nodes.get(i, {}).get("kind") == "macro" and self.nodes[i].get("name") in LOOP_MACROS)
        self._close_loops(g)

    def _close_loops(self, g):
        """leaves of a loop body (no successor) continue with the next iteration -> back edge to the loop node"""
        for chain in g["exec"]:
            for a, b in zip(chain, chain[1:]):
                loop = a.split(":")[0]
                if self.is_loop(loop) and not a.endswith(":Completed"):
                    for leaf in self._reach(b.split(":")[0], stop=loop):
                        if not self.succ.get(leaf): self.succ[leaf].append(loop)

    def _reach(self, start, stop=None):
        seen, todo = set(), [start]
        while todo:
            n = todo.pop()
            if n in seen or n == stop: continue
            seen.add(n); todo.extend(self.succ.get(n, []))
        return seen

    def exec_readers(self, get_id):
        """exec nodes that consume the value of a get node (through pure nodes)"""
        out, todo, seen = set(), [get_id], set()
        while todo:
            n = todo.pop()
            for c in self.consumers.get(n, ()):
                if c in seen: continue
                seen.add(c)
                if c in self.exec_nodes or c == "return": out.add(c)
                else: todo.append(c)
        return out

    def tmp_reads(self):
        r = collections.defaultdict(set)
        for n in self.nodes.values():
            if n["kind"] == "get" and n["var"].startswith("Tmp") and "class" not in n:
                for e in self.exec_readers(n["id"]): r[n["var"]].add(e)
        return r

    def tmp_writes(self):
        w = collections.defaultdict(set)
        for n in self.nodes.values():
            if n["kind"] == "set" and n["var"].startswith("Tmp") and "class" not in n: w[n["var"]].add(n["id"])
        return w

    def calls(self):
        return {n["id"]: n["function"] for n in self.nodes.values() if n["kind"] == "call_self"}


def conflicts(fns):
    graphs = {k: Graph(g) for k, g in fns.items()}
    writes = {k: g.tmp_writes() for k, g in graphs.items()}

    @functools.lru_cache(None)
    def writes_of(fn, depth=0):
        if fn not in graphs or depth > 30: return frozenset()
        out = set(writes[fn])
        for callee in graphs[fn].calls().values(): out |= writes_of(callee, depth + 1)
        return frozenset(out)

    found = []
    for name, g in graphs.items():
        reads, calls = g.tmp_reads(), g.calls()
        for var, wnodes in writes[name].items():
            readers = reads.get(var, set())
            if not readers: continue
            clobber = {c for c, callee in calls.items() if var in writes_of(callee)}
            if not clobber: continue
            for w in wnodes:   # forward walk from the write: state = clobbered?
                todo, seen = [(s, False) for s in g.succ.get(w, [])], set()
                while todo:
                    n, dirty = todo.pop()
                    if (n, dirty) in seen: continue
                    seen.add((n, dirty))
                    if n in wnodes: continue                      # own write resets
                    if n in clobber: dirty = True
                    if dirty and n in readers: found.append((name, var, w, n, calls.get(n, ""))); break
                    todo.extend((s, dirty) for s in g.succ.get(n, []))
    return found


class TmpVars(unittest.TestCase):
    def test_conflict_is_detected(self):
        callee = {"nodes": [{"id": "s", "kind": "set", "var": "TmpX", "in": {"TmpX": "1"}}], "links": [], "exec": [["entry", "s"]]}
        caller = {"nodes": [{"id": "s", "kind": "set", "var": "TmpX", "in": {"TmpX": "0"}}, {"id": "c", "kind": "call_self", "function": "Callee"},
                            {"id": "g", "kind": "get", "var": "TmpX"}, {"id": "u", "kind": "set", "var": "TmpI", "in": {"TmpI": "@g.TmpX"}}], "links": [],
                  "exec": [["entry", "s", "c", "u"]]}
        self.assertEqual([c[:2] for c in conflicts({"Callee": callee, "Caller": caller})], [("Caller", "TmpX")])
        caller["exec"] = [["entry", "s", "u", "c"]]   # read before the call: fine
        self.assertEqual(conflicts({"Callee": callee, "Caller": caller}), [])
        caller["exec"] = [["entry", "s", "u", "c", "s"]]   # own write after the call resets
        self.assertEqual(conflicts({"Callee": callee, "Caller": caller}), [])

    def test_loop_body_back_edge(self):
        callee = {"nodes": [{"id": "s", "kind": "set", "var": "TmpX", "in": {"TmpX": "1"}}], "links": [], "exec": [["entry", "s"]]}
        caller = {"nodes": [{"id": "s", "kind": "set", "var": "TmpX", "in": {"TmpX": "0"}}, {"id": "fe", "kind": "foreach", "in": {"Array": "@entry.a"}},
                            {"id": "g", "kind": "get", "var": "TmpX"}, {"id": "u", "kind": "set", "var": "TmpI", "in": {"TmpI": "@g.TmpX"}}, {"id": "c", "kind": "call_self", "function": "Callee"}],
                  "links": [], "exec": [["entry", "s", "fe"], ["fe", "u", "c"]]}   # iteration 2 reads what the callee wrote in iteration 1
        self.assertEqual([c[:2] for c in conflicts({"Callee": callee, "Caller": caller})], [("Caller", "TmpX")])

    def test_manager_has_no_tmp_conflicts(self):
        self.assertEqual(conflicts(manager_functions()), [])
