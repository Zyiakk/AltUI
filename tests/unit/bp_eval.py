"""bp_eval.py - a tiny interpreter for generated Blueprint function graphs (bpdsl JSON), test-only.

Runs a function graph from its 'entry' node on a dict of member variables, with the math / array / component calls the
generators use (round 5: DripUpdate). Pure nodes are evaluated on demand each time a pin is pulled (as in the BP VM);
component calls are recorded in `calls`. Unknown functions raise, so a new node type is noticed.
"""
import math
import re

import numpy as np

_VEC = re.compile(r"\(X=([-\d.eE+]+),Y=([-\d.eE+]+),Z=([-\d.eE+]+)\)")


def lit(v):
    if isinstance(v, (int, float, bool, np.ndarray)):
        return v
    s = str(v)
    if s in ("true", "false"):
        return s == "true"
    m = _VEC.fullmatch(s.replace(" ", ""))
    if m:
        return np.array([float(m.group(i)) for i in (1, 2, 3)])
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s          # an enum / a name (e.g. RTS_World, a bone name)


def _normal(a, tol):
    n = float(np.linalg.norm(a))
    return a / n if n * n > tol else np.zeros(3)


def _rot_from_z(z):
    n = float(np.linalg.norm(z))
    return ("rotz", z / n if n > 1e-12 else np.array([0.0, 0.0, 1.0]))


MATH = {
    "Add_FloatFloat": lambda a: a["A"] + a["B"], "Subtract_FloatFloat": lambda a: a["A"] - a["B"],
    "Multiply_FloatFloat": lambda a: a["A"] * a["B"], "Divide_FloatFloat": lambda a: a["A"] / a["B"],
    "Add_IntInt": lambda a: int(a["A"]) + int(a["B"]), "Subtract_IntInt": lambda a: int(a["A"]) - int(a["B"]),
    "Multiply_IntInt": lambda a: int(a["A"]) * int(a["B"]),
    "Add_VectorVector": lambda a: a["A"] + a["B"], "Subtract_VectorVector": lambda a: a["A"] - a["B"],
    "Multiply_VectorFloat": lambda a: a["A"] * a["B"],
    "FMin": lambda a: min(a["A"], a["B"]), "FMax": lambda a: max(a["A"], a["B"]),
    "FClamp": lambda a: min(max(a["Value"], a["Min"]), a["Max"]),
    "Lerp": lambda a: a["A"] + (a["B"] - a["A"]) * a["Alpha"], "VLerp": lambda a: a["A"] + (a["B"] - a["A"]) * a["Alpha"],
    "SelectFloat": lambda a: a["A"] if a["bPickA"] else a["B"], "SelectVector": lambda a: a["A"] if a["bPickA"] else a["B"],
    "SelectInt": lambda a: a["A"] if a["bPickA"] else a["B"],
    "Greater_FloatFloat": lambda a: a["A"] > a["B"], "Less_FloatFloat": lambda a: a["A"] < a["B"],
    "GreaterEqual_FloatFloat": lambda a: a["A"] >= a["B"], "LessEqual_FloatFloat": lambda a: a["A"] <= a["B"],
    "EqualEqual_IntInt": lambda a: int(a["A"]) == int(a["B"]), "NotEqual_IntInt": lambda a: int(a["A"]) != int(a["B"]),
    "Less_IntInt": lambda a: int(a["A"]) < int(a["B"]), "GreaterEqual_IntInt": lambda a: int(a["A"]) >= int(a["B"]),
    "BooleanAND": lambda a: bool(a["A"]) and bool(a["B"]), "BooleanOR": lambda a: bool(a["A"]) or bool(a["B"]),
    "Not_PreBool": lambda a: not a["A"],
    "VSize": lambda a: float(np.linalg.norm(a["A"])), "VSizeXY": lambda a: float(np.linalg.norm(np.asarray(a["A"], float)[:2])), "Normal": lambda a: _normal(a["A"], a["Tolerance"]),
    "MakeVector": lambda a: np.array([a["X"], a["Y"], a["Z"]], dtype=float), "Sqrt": lambda a: math.sqrt(a["A"]),
    "MultiplyMultiply_FloatFloat": lambda a: a["Base"] ** a["Exp"], "Conv_IntToFloat": lambda a: float(a["InInt"]),
    "MakeRotFromZ": lambda a: _rot_from_z(a["Z"]),
    "MakeLiteralInt": lambda a: int(a["Value"]), "MakeLiteralFloat": lambda a: float(a["Value"]),
    "MakeLiteralBool": lambda a: bool(a["Value"]),
    # drips (plan 2026-11-04-jodis-sky-drips.md Task 5)
    "Exp": lambda a: math.exp(a["A"]), "Sin": lambda a: math.sin(a["A"]), "Cos": lambda a: math.cos(a["A"]),
    "Acos": lambda a: math.acos(a["A"]), "FTrunc": lambda a: int(math.trunc(a["A"])), "FFloor": lambda a: int(math.floor(a["A"])), "Abs": lambda a: abs(a["A"]),
    "Dot_VectorVector": lambda a: float(np.dot(a["A"], a["B"])), "NotEqual_FloatFloat": lambda a: a["A"] != a["B"],
    "Divide_IntInt": lambda a: int(int(a["A"]) / int(a["B"])),
    "MakeRotationFromAxes": lambda a: ("axes", np.asarray(a["Forward"], float), np.asarray(a["Right"], float), np.asarray(a["Up"], float)),
    "MakeTransform": lambda a: {"loc": np.asarray(a["Location"], float), "rot": a["Rotation"], "scale": np.asarray(a["Scale"], float)},
    # Foot IK round 4 (copied from JodisSky_AltUI 2026-11-09): strings, UE's Round (half away from zero)
    "SelectString": lambda a: a["A"] if a["bPickA"] else a["B"],
    "EqualEqual_StrStr": lambda a: str(a["A"]) == str(a["B"]), "NotEqual_StrStr": lambda a: str(a["A"]) != str(a["B"]),
    "Round": lambda a: int(math.copysign(math.floor(abs(a["A"]) + 0.5), a["A"])),
    "Conv_IntToString": lambda a: str(int(a["InInt"])),
    "NearlyEqual_FloatFloat": lambda a: abs(a["A"] - a["B"]) <= a["ErrorTolerance"],
}
COMPONENT = {"SetFogDensity", "SetVolumetricFogExtinctionScale", "SetVectorParameterValueOnMaterials", "SetScalarParameterValueOnMaterials", "SetActorTickEnabled",   # rain take 2 Task 4
             "SetPositionInViewport", "SetRenderScale", "SetText", "AddToViewport", "SetAlignmentInViewport",   # Task 3c
             "K2_SetWorldLocationAndRotation", "SetWorldScale3D", "SetVisibility", "K2_SetWorldLocation",
             "K2_SetWorldTransform", "SetCustomPrimitiveDataVector3", "SetScalarParameterValue", "SetMaterial"}


class Run:
    def __init__(self, graph, variables, random=lambda: 0.5, functions=None):
        self.functions = functions or {}       # name -> graph (call_self)
        self.loop = {}                         # foreach node id -> (element, index)
        self.g = graph
        self.v = variables
        self.random = random
        self.nodes = {n["id"]: n for n in graph["nodes"]}
        self.next = {}
        for ch in graph["exec"]:
            for a, b in zip(ch, ch[1:]):
                key = a if ":" in a else a + ":then"
                self.next[key] = b
        self.calls = []
        self.cs_ret = {}

    def pin(self, ref):
        if not (isinstance(ref, str) and ref.startswith("@")):
            return lit(ref)
        nid, out = ref[1:].split(".", 1)
        n = self.nodes[nid]
        if n["kind"] == "get":
            if (n.get("cls") or n.get("class")) and n["var"] not in self.v: return n["var"]   # a native member of a passed-in object (fixes round 1)
            val = self.v[n["var"]]
            return val.copy() if isinstance(val, np.ndarray) else val
        if n["kind"] == "self":
            return "self"
        if n["kind"] == "foreach":
            el, ix = self.loop[nid]
            return el if out == "Array Element" else ix
        if n["kind"] == "macro":      # rain take 2 Task 4: ForLoop's Index
            return self.loop[nid][1]
        if n["kind"] == "cast":      # pure cast: the object itself (tests hand in objects of the right kind)
            return self.pin(n["in"]["Object"])
        if n["kind"] == "call_self":   # Task 3c: an output of a function called earlier on the chain
            return self.cs_ret[nid][out]
        if n["kind"] == "make_array":
            return [self.pin(n["in"]["[%d]" % i]) for i in range(n["count"])]
        if n["kind"] != "call":
            raise KeyError("pure node kind %s" % n["kind"])
        a = {k: self.pin(x) for k, x in n.get("in", {}).items()}
        f = n["function"]
        if f == "Array_Get":
            item = a["TargetArray"][int(a["Index"])]
            return item.copy() if isinstance(item, np.ndarray) else item
        if f == "Array_Length":
            return len(a["TargetArray"])
        # drip sync (hair tips, clothes): a mock object answers a call named after its method (e.g. GetBoneIndex)
        if hasattr(a.get("self"), f) and not isinstance(a.get("self"), (str, np.ndarray)):
            return getattr(a["self"], f)(a, out)
        if f == "Array_Contains": return a["ItemToFind"] in list(a["TargetArray"])
        if f == "MinOfFloatArray":
            arr = list(a["TargetArray"] if "TargetArray" in a else a["FloatArray"])
            if not arr: return -1 if out == "IndexOfMinValue" else 0.0
            i = int(np.argmin(arr)); return i if out == "IndexOfMinValue" else arr[i]
        if f == "EqualEqual_NameName": return str(a["A"]) == str(a["B"])
        if f == "Contains": return (a["Substring"].lower() in str(a["SearchIn"]).lower()) if not a["bUseCase"] else (a["Substring"] in str(a["SearchIn"]))
        if f == "IsValid": return a["Object"] is not None
        if f == "GetPathName": return getattr(a["Object"], "path", "")
        if f == "K2_GetComponentsByClass": return list(self.v.get("__comps", {}).get(a["ComponentClass"], []))
        if f == "GetObjectClass": return getattr(a["Object"], "cls", "")
        if f == "GetClassDisplayName": return str(a["Class"])
        if f == "Conv_FloatToString": return "%g" % a["InFloat"]
        if f == "Conv_NameToString": return str(a["InName"])
        if f == "Concat_StrStr": return str(a["A"]) + str(a["B"])
        # drips: a mesh / hair component is a dict {bone name: 4x4 world matrix} in the test's variables
        if f == "GetPlayerCharacter": return "player"
        if f == "GetWorldDeltaSeconds": return self.v["__dt"]
        if f == "GetPlayerCameraManager": return "pcm"
        if f == "GetCameraLocation": return np.asarray(self.v["__cam"], float)
        # rain take 2 Task 3c (debug widget): UMG stand-ins - the test hands in __mouse / __viewport (viewport-local units)
        if f == "GetMousePositionOnViewport": return np.asarray(self.v["__mouse"], float)
        if f == "GetViewportWidgetGeometry": return "viewport"
        if f == "GetLocalSize": return np.asarray(self.v["__viewport"], float)
        if f == "MakeVector2D": return np.array([float(a["X"]), float(a["Y"])])
        if f == "BreakVector2D": return float(np.asarray(a["InVec"], float)[0 if out == "X" else 1])
        if f == "Subtract_Vector2DVector2D": return np.asarray(a["A"], float) - np.asarray(a["B"], float)
        if f in ("Handled", "Unhandled"): return f
        if f == "MakeLiteralString": return str(a["Value"])
        if f == "CaptureMouse": return str(a["Reply"]) + "+capture"
        if f == "ReleaseMouseCapture": return str(a["Reply"]) + "+release"
        if f == "Conv_StringToText": return str(a["InString"])
        if f == "FCeil": return int(math.ceil(a["A"]))
        # rain take 2 Task 4: grid snap (FMath::GridSnap = round to the nearest step), int maths, instance counts
        if f == "Vector_SnappedToGrid":
            st = float(a["InGridSize"]); return np.array([math.floor((float(v) + st / 2.0) / st) * st for v in np.asarray(a["InVect"], float)])
        if f == "Percent_IntInt": return int(a["A"]) % int(a["B"])
        if f == "K2_GetActorLocation": return np.asarray(self.v.get("__actor_loc", (0.0, 0.0, 90.0)), float)
        if f == "GetScaledCapsuleHalfHeight": return float(self.v.get("__half", 90.0))
        if f == "LessEqual_IntInt": return int(a["A"]) <= int(a["B"])
        if f == "GetInstanceCount": return len(self.v.get("__instances", {}).get(a["self"], []))
        if f == "Min": return min(int(a["A"]), int(a["B"]))
        if f == "GetSocketTransform": return np.asarray(a["self"][str(a["InSocketName"])], float)
        if f == "GetSocketLocation": return np.asarray(a["self"][str(a["InSocketName"])], float)[:3, 3].copy()
        if f == "TransformLocation": return (a["T"] @ np.append(a["Location"], 1.0))[:3]
        if f == "TransformDirection": return a["T"][:3, :3] @ a["Direction"]
        if f == "Cross_VectorVector": return np.cross(a["A"], a["B"])
        if f == "FMod":   # outputs: Remainder (float), ReturnValue (int quotient)
            q = math.trunc(a["Dividend"] / a["Divisor"])
            return a["Dividend"] - q * a["Divisor"] if out == "Remainder" else int(q)
        if f == "BreakVector":
            return float(a["InVec"]["XYZ".index(out)])
        if f == "RandomFloat":
            return self.random()
        if f == "RandomFloatInRange":   # fixes round 2: deterministic - the middle of the range
            return 0.5 * (float(a["Min"]) + float(a["Max"]))
        return MATH[f](a)

    def run(self, start="entry"):
        cur = self.next.get(start + ":then")
        return self._chain(cur)

    def _chain(self, cur):
        steps = 0
        while cur:
            steps += 1
            if cur == "return" or self.nodes.get(cur, {}).get("kind") == "return_new":   # Task 3c: a function's reply
                self.ret = {d.split(".", 1)[1]: self.pin("@" + s) for s, d in self.g.get("links", []) if d.split(".", 1)[0] == cur}
                break
            n = self.nodes[cur]
            pin_out = "then"
            if n["kind"] == "set":
                self.v[n["var"]] = self.pin(n["in"][n["var"]])
            elif n["kind"] == "sequence":   # a join (count 1): straight on; then_0 .. then_n in order (rain take 2 Task 4)
                for i in range(int(n.get("count", 1))):
                    body = self.next.get(cur + ":then_%d" % i)
                    if body: steps += self._chain(body)
                pin_out = "then"
            elif n["kind"] == "macro" and n.get("name") == "ForLoop":
                lo, hi = int(self.pin(n["in"]["First Index"])), int(self.pin(n["in"]["Last Index"]))
                for ix in range(lo, hi + 1):
                    self.loop[cur] = (None, ix)
                    body = self.next.get(cur + ":then")
                    if body: steps += self._chain(body)
                cur = self.next.get(cur + ":Completed"); continue
            elif n["kind"] == "call_self":
                sub = Run(self.functions[n["function"]], self.v, self.random, self.functions); steps += sub.run()
                self.calls.extend(sub.calls)
                self.cs_ret[cur] = getattr(sub, "ret", {})                     # Task 3c: its outputs, read by later pins
            elif n["kind"] == "foreach":
                arr = self.pin(n["in"]["Array"])
                for ix, el in enumerate(list(arr)):
                    self.loop[cur] = (el, ix)
                    body = self.next.get(cur + ":then")
                    if body: steps += self._chain(body)
                cur = self.next.get(cur + ":Completed"); continue
            elif n["kind"] == "branch":
                pin_out = "then" if self.pin(n["in"]["Condition"]) else "else"
            elif n["kind"] == "call":
                f = n["function"]
                if f == "Array_Set" and n["in"]["TargetArray"][1:].split(".")[0] in self.nodes and isinstance(self.pin(n["in"]["Item"]), dict):
                    tgt = n["in"]["TargetArray"][1:].split(".")[0]
                    self.v[self.nodes[tgt]["var"]][int(self.pin(n["in"]["Index"]))] = self.pin(n["in"]["Item"])
                elif f == "Array_Set":
                    arr = self.pin(n["in"]["TargetArray"]) if False else None
                    tgt = n["in"]["TargetArray"][1:].split(".")[0]
                    name = self.nodes[tgt]["var"]
                    item = self.pin(n["in"]["Item"])
                    self.v[name][int(self.pin(n["in"]["Index"]))] = item.copy() if isinstance(item, np.ndarray) else item
                elif f in ("Array_Clear", "Array_Resize"):   # rain take 2 Task 4 (a resized transform array = identities)
                    tgt = n["in"]["TargetArray"][1:].split(".")[0]
                    name = self.nodes[tgt]["var"]
                    if f == "Array_Clear": self.v[name] = []
                    else:
                        size = int(self.pin(n["in"]["Size"])); arr = list(self.v[name])[:size]
                        self.v[name] = arr + ["identity"] * (size - len(arr))
                elif f == "AddInstances":
                    comp = self.pin(n["in"]["self"])
                    self.v.setdefault("__instances", {}).setdefault(comp, []).extend(list(self.pin(n["in"]["InstanceTransforms"])))
                    self.calls.append((f, comp, {"count": len(self.pin(n["in"]["InstanceTransforms"]))}))
                elif f == "Array_Add":
                    tgt = n["in"]["TargetArray"][1:].split(".")[0]
                    item = self.pin(n["in"]["NewItem"])
                    self.v[self.nodes[tgt]["var"]].append(item.copy() if isinstance(item, np.ndarray) else item)
                elif f in ("GetMousePositionOnViewport", "GetViewportWidgetGeometry"):   # impure getters: read by their pins
                    pass
                elif f in COMPONENT:
                    self.calls.append((f, self.pin(n["in"]["self"]), {k: self.pin(x) for k, x in n["in"].items() if k != "self"}))
                elif f == "K2_SetTimer":   # fixes round 2 (ArmStrike): recorded, the timer itself is not run
                    self.calls.append((f, n["in"].get("FunctionName"), {"Time": self.pin(n["in"]["Time"])}))
                else:
                    raise KeyError("exec call %s" % f)
            else:
                raise KeyError("exec kind %s" % n["kind"])
            cur = self.next.get(cur + ":" + pin_out) or (self.next.get(cur) if pin_out == "then" else None)
        return steps
