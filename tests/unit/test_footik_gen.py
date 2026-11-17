"""BP_AltUIFootIK (Foot IK driver, port of BenenG47's BP_FootIKTest): checks of the generated description, no editor.
Ported from the test chip's tests/test_gen.py (chip-only checks - page, presets, SaveGame, status box - dropped; the ABP nodes and
their defaults are checked in test_gen_bodyscale.py)."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, "..", "..")
sys.path.insert(0, os.path.join(W, "assets", "gen")); sys.path.insert(0, os.path.join(W, "scripts")); sys.path.insert(0, H)
import gen_footik as g   # writes assets/45_footik.json on import
import footik
import footik_sim as S

ABP = g.ABP
ABP_VAR_NAMES = {n for n, _, _ in footik.ABP_VARS}


def assets():
    return {a["path"]: a for a in g.build()}


def bp():
    return assets()[g.FOOTIK]


driver = bp


def fns():
    return {f["name"]: f for f in bp()["functions"]}


def graphs():
    b = bp(); out = {"EventGraph": b["event_graph"]}
    out.update({f["name"]: f["graph"] for f in b.get("functions", []) if "graph" in f})
    return out


def nodes(gr, **kw):
    return [n for n in gr["nodes"] if all(n.get(k) == v for k, v in kw.items())]


def test_push_every_tick():
    gr = graphs()["FootTick"]
    sets = {n["id"] for n in gr["nodes"] if n["kind"] == "set" and n.get("class") == ABP}
    assert {n["var"] for n in gr["nodes"] if n["id"] in sets} == ABP_VAR_NAMES
    chain = next(c for c in gr["exec"] if sets <= set(c))
    kinds = {n["id"]: n["kind"] for n in gr["nodes"]}
    # entry -> valid-pawn branch -> cast -> ... -> the sets: no other branch on the way (nothing "only on change");
    # AltUI: the idle check (tick off) comes after the sets
    upto = chain[1:max(chain.index(s) for s in sets)]
    assert chain[0] == "entry" and [kinds[i] for i in upto if i in kinds and kinds[i] == "branch"] == ["branch"]
    assert "cab" in chain and chain.index("cab") < min(chain.index(s) for s in sets)
    ev = graphs()["EventGraph"]
    tick = nodes(ev, kind="event", name="ReceiveTick")[0]["id"]
    ft = nodes(ev, kind="call_self", function="FootTick")[0]["id"]
    assert [tick, ft] in ev["exec"]


def test_no_footik_body_status():
    gr = graphs()["FootTick"]
    tail = next(c for c in gr["exec"] if c[0] == "cab:CastFailed")
    s = next(n for n in gr["nodes"] if n["id"] == tail[1])
    assert s["kind"] == "set" and s["var"] == "Reason" and s["in"]["Reason"] == "no Foot IK body"
    w = next(n for n in gr["nodes"] if n["id"] == tail[2])   # back on the Foot IK chip later: fades in, no snap
    assert w["kind"] == "set" and w["var"] == "W" and w["in"]["W"] == "0.0"
    assert tail[-2:] == ["bidf", "tidf"]   # AltUI: then tick off when all switches are off
    rest = [next(n for n in gr["nodes"] if n["id"] == i) for i in tail[3:-2]]   # round 3: every feature's weight
    got = {n["var"]: n["in"][n["var"]] for n in rest}   # round 3 + final review M1: weights and applied values back to 0
    assert set(got) == {"WB", "WHL", "WHR", "WKL", "WKR", "PelAp", "EcL", "EcR", "HEzL", "HEzR", "ThL", "ThR", "FwdL", "FwdR",
                        "HStillL", "HStillR", "ModeWord", "KneeMode", "HandState"}   # round 4 (+ review M2)
    assert all(v in ("0.0", "(X=0,Y=0,Z=0)", "", "-") for v in got.values())   # round 4: the status words "" / "-"


def test_trace_ignores_pawn_and_attached():
    tr = graphs()["Trace"]
    lt = nodes(tr, function="LineTraceSingle")[0]
    src = lt["in"]["ActorsToIgnore"]; gid = src[1:].split(".")[0]
    assert next(n for n in tr["nodes"] if n["id"] == gid)["var"] == "Ignore"
    assert lt["in"]["bIgnoreSelf"] == "true" and lt["in"]["TraceChannel"] == "TraceTypeQuery1"
    ft = graphs()["FootTick"]
    att = nodes(ft, function="GetAttachedActors")[0]
    assert att["in"]["self"] == "@gpc.ReturnValue"
    add = nodes(ft, function="Array_Add")[0]
    assert add["in"]["NewItem"] == "@gpc.ReturnValue"
    seti = nodes(ft, kind="set", var="Ignore")[0]
    chain = next(c for c in ft["exec"] if seti["id"] in c)
    tl = nodes(ft, kind="call_self", function="Trace")
    assert chain.index(seti["id"]) < chain.index(add["id"]) < min(chain.index(t["id"]) for t in tl) and len(tl) == 4   # feet + forward spots


def test_gate_reasons():
    txt = json.dumps(graphs()["FootTick"])
    for r in ("off", "ragdoll", "fitting", "cutscene", "climbing", "jumping", "air", "moving", "feet", "lying", "kneel", "sit",
              "stand", "pose off", "on", "no Foot IK body"):
        assert '"%s"' % r in txt, r


def test_no_ue4ss_no_debugdraw():
    for name, gr in graphs().items():
        for n in gr["nodes"]:
            assert not str(n.get("function", "")).startswith("DrawDebug"), name
            if n.get("function") == "LineTraceSingle": assert n["in"]["DrawDebugType"] == "None"
    assert not any(f.endswith(".lua") for f in os.listdir(os.path.join(W, "assets", "gen")))


def _strings(v):
    if isinstance(v, str): yield v
    elif isinstance(v, dict):
        for x in v.values(): yield from _strings(x)
    elif isinstance(v, list):
        for x in v: yield from _strings(x)


def test_only_own_and_engine_paths():
    ok = ("/Game/Mod/AltUI/",)
    for a in g.build():
        for s in _strings(a):
            if s.startswith("/Game/"): assert s.startswith(ok), s


def test_no_function_variable_clash():
    b = bp()
    assert not ({f["name"] for f in b["functions"]} & {v["name"] for v in b["variables"]})


def _refs(v):
    if isinstance(v, str) and v.startswith("@"): yield v[1:].split(".")[0]
    elif isinstance(v, dict):
        for x in v.values(): yield from _refs(x)
    elif isinstance(v, list):
        for x in v: yield from _refs(x)


def test_refs_resolve():
    for name, gr in graphs().items():
        ids = {n["id"] for n in gr["nodes"]} | ({"entry", "return"} if name != "EventGraph" else set())
        for n in gr["nodes"]:
            for r in _refs(n.get("in", {})): assert r in ids, (name, n["id"], r)
        for a, b in gr["links"]: assert a.split(".")[0] in ids and b.split(".")[0] in ids, (name, a, b)
        for c in gr["exec"]:
            for x in c: assert x.split(":")[0] in ids, (name, x)


def test_out_of_range_hit_rejected():
    ft = graphs()["FootTick"]; ids = {n["id"]: n for n in ft["nodes"]}
    for s in ("l", "r"):
        tg = ids["tg" + s]
        assert tg["in"]["A"] == "@hs%s.ReturnValue" % s and tg["in"]["B"] == "0.0"
        cond = ids[tg["in"]["bPickA"][1:].split(".")[0]]
        assert cond["function"] == "BooleanAND"
        rng = ids[cond["in"]["B"][1:].split(".")[0]]
        assert rng["function"] == "InRange_FloatFloat" and rng["in"]["Value"] == "@hs%s.ReturnValue" % s
        assert cond["in"]["A"] == "@tr%s.hit" % s


def test_floors():
    # review finding 2: traces measure from the real ground (capsule bottom - CurrentFloor.FloorDist), the gate from the mesh's Z
    ft = graphs()["FootTick"]; ids = {n["id"]: n for n in ft["nodes"]}
    assert ids["bcf"]["kind"] == "break" and ids["bcf"]["struct"] == "/Script/Engine.FindFloorResult"
    assert ids["gnd"]["in"]["B"] == "@bcf.FloorDist"
    for s in ("l", "r"): assert ids["tr" + s]["in"]["floor"] == "@gnd.ReturnValue"
    assert ids["mzl"]["function"] == "K2_GetComponentLocation" and ids["mzl"]["in"]["self"] == "@gm.Mesh"
    assert ids["fhl0"]["in"]["B"] == "@bmz.Z" and ids["fhr0"]["in"]["B"] == "@bmz.Z"



def test_mesh_scale():
    # world cm (traces, sockets) -> mesh cm (AnimBP): divided by the mesh's world Z scale (spec 7b, AltUI height slider)
    ft = graphs()["FootTick"]; ids = {n["id"]: n for n in ft["nodes"]}
    assert ids["gcs"]["function"] == "K2_GetComponentScale" and ids["gcs"]["in"]["self"] == "@gm.Mesh"
    for s in ("l", "r"):
        hs = ids["hs" + s]
        assert hs["function"] == "Divide_FloatFloat" and hs["in"] == {"A": "@tr%s.h" % s, "B": "@bcs.Z"}


def test_legs_only_keeps_hips():
    ft = graphs()["FootTick"]; ids = {n["id"]: n for n in ft["nodes"]}
    lo = ids["tpl"]
    assert lo["function"] == "SelectFloat" and lo["in"]["A"] == "0.0" and lo["in"]["B"] == "@tpm.ReturnValue"
    assert lo["in"]["bPickA"] == "@legs.ReturnValue"
    assert ids["npek"]["in"]["A"] == "@npe" + "d.ReturnValue" and ids["nped"]["in"]["A"] == "@tpl.ReturnValue"


def test_hard_off_signals():
    # regression guard for the ledger's round-2 signal list (written after the code: see ledger)
    ft = graphs()["FootTick"]; ids = {n["id"]: n for n in ft["nodes"]}
    assert ids["gsm"]["var"] == "bShowMouseCursor" and ids["gsm"]["class"] == "/Script/Engine.PlayerController"
    assert ids["mcl"]["in"]["Substring"] == "Climb" and ids["mju"]["in"]["Substring"] == "Jump"
    assert ids["gjc"]["var"] == "JumpCurrentCount"
    assert ids["gjh"]["var"] == "JodiHidden" and ids["gcmd"]["var"] == "CamMode" and ids["gjh"]["class"] == g.MGR
    assert ids["gjh"]["class"] == ids["gcmd"]["class"] == ids["gpno"]["class"] == g.MGR and ids["gmg"]["var"] == "Manager"
    assert ids["ovc"]["in"]["B"] == "@nfc.ReturnValue"   # another view target counts only outside AltUI free cam / photo
    # AltUI: "fitting" = the mouse cursor OR AltUI's panel open, in the reason chain and in Common's block list
    fit = ids["fit"]; assert fit["function"] == "BooleanOR" and fit["in"] == {"A": "@gsm.bShowMouseCursor", "B": "@fpo.ReturnValue"}
    # the open panel only counts in the play camera (free cam / photo mode collapse it and PanelOpen stays true)
    assert ids["fpo"]["function"] == "BooleanAND" and ids["fpo"]["in"] == {"A": "@gpno.PanelOpen", "B": "@fpc.ReturnValue"}
    assert ids["fpc"]["function"] == "EqualEqual_IntInt" and ids["fpc"]["in"]["A"] == "@cmo0.ReturnValue" and ids["fpc"]["in"]["B"] == "0"
    assert ids["gpno"]["var"] == "PanelOpen" and ["gmg.Manager", "gpno.self"] in ft["links"]
    assert any(n.get("in", {}).get("A") == "fitting" and n["in"]["bPickA"] == "@fit.ReturnValue" for n in ids.values())
    assert ids["blk0"]["in"]["B"] == "@fit.ReturnValue"
    assert "bShowMouseCursor" not in json.dumps([n for n in ids.values() if n["id"] not in ("fit", "gsm")])


# ---------------- round 3 (spec 7d) ----------------
def ids_of(name): return {n["id"]: n for n in graphs()[name]["nodes"]}


def test_trace_defaults_cover_max_step():
    d = {v["name"]: float(v["default"]) for v in bp()["variables"] if v["type"] == "float"}
    assert d["TraceUp"] >= d["MaxStep"] and d["TraceDown"] >= d["MaxStep"]


def test_forward_second_trace():
    ids = ids_of("FootTick")
    for s in ("l", "r"):
        tf = ids["tf" + s]; assert tf["kind"] == "call_self" and tf["function"] == "Trace"
        acc = ids["acc" + s]; assert acc["function"] == "BooleanAND"
        near = ids["fsm" + s]; assert near["function"] == "LessEqual_FloatFloat" and near["in"]["B"] == "@gFwdSame.FwdSame"
        S_ = s.upper(); cache = ids["sAc" + S_]; assert cache["kind"] == "set" and cache["in"]["Acc" + S_] == "@acc%s.ReturnValue" % s
        tgf = ids["tgf" + s]; assert tgf["function"] == "SelectFloat" and tgf["in"]["bPickA"] == "@gac%s.Acc%s" % (s, S_)
        assert ids["tgf" + s]["in"]["B"] == "@tg%s.ReturnValue" % s


def test_forward_from_actor():
    ids = ids_of("FootTick")
    assert ids["afw"]["function"] == "GetActorForwardVector" and ids["fwc"]["function"] == "InverseTransformDirection"
    txt = json.dumps(graphs()["FootTick"])
    assert '"Y": "-1.0"' not in txt and '"Y": "1.0"' not in txt


def test_component_space_sockets():
    for name, bones in (("FootTick", ("thigh_l", "calf_l", "foot_l")), ("KneeTick", ("thigh_l", "calf_l", "foot_l")),
                        ("HandTick", ("hand_l", "hand_r"))):
        st = [n for n in graphs()[name]["nodes"] if n.get("function") == "GetSocketTransform"]
        got = {n["in"]["InSocketName"] for n in st if n["in"]["TransformSpace"] == "RTS_Component"}
        assert set(bones) <= got, (name, got)


def test_hold_check_uses_hand_bones():
    ids = ids_of("HoldCheck")
    fns = {n.get("function") for n in ids.values()}
    assert {"GetChildrenComponents", "GetAttachSocketName", "GetSocketBoneName", "BoneIsChildOf"} <= fns
    parents = {n["in"]["ParentBoneName"] for n in ids.values() if n.get("function") == "BoneIsChildOf"}
    assert parents == {"hand_l", "hand_r"}
    assert any(n["kind"] == "foreach" for n in ids.values())


def test_contact_toggles_independent():
    for name, tog in (("KneeTick", "KneeOn"), ("HandTick", "HandOn")):
        vars_read = {n["var"] for n in graphs()[name]["nodes"] if n["kind"] == "get"}
        assert tog in vars_read and "Common" in vars_read and "On" not in vars_read, name


def test_knee_arc_rebuilds_animated_knee():
    ids = ids_of("KneeTick")
    for s in ("l", "r"):
        rot = ids["kin" + s]; assert rot["function"] == "RotateAngleAxis"
        assert rot["in"]["AngleDeg"] == "@nth%s.ReturnValue" % s and ids["nth" + s]["function"] == "Multiply_FloatFloat"


def test_contact_on_tick_chain():
    ft = graphs()["FootTick"]; chain = max(ft["exec"], key=len)
    calls = [n["id"] for n in ft["nodes"] if n["kind"] == "call_self" and n["function"] in ("KneeTick", "HoldCheck", "HandTick")]
    assert len(calls) == 3 and all(c in chain for c in calls)
    sets = [n["id"] for n in ft["nodes"] if n["kind"] == "set" and n.get("class") == ABP]
    assert max(chain.index(c) for c in calls) < min(chain.index(x) for x in sets)


def _uses_get(graph, node_id, var):
    """True if node_id's inputs reach a Get of var (through pure nodes), stopping at other impure (chained) nodes."""
    nodes_ = {n["id"]: n for n in graph["nodes"]}; chained = {x.split(":")[0] for c in graph["exec"] for x in c}
    seen = set(); todo = [node_id]
    while todo:
        i = todo.pop()
        if i in seen: continue
        seen.add(i); n = nodes_[i]
        if n["kind"] == "get" and n.get("var") == var: return True
        for ref in _refs(n.get("in", {})):
            if ref not in chained or ref == node_id: todo.append(ref)
    return False


def test_pure_reevaluation_safe():
    """Blueprint pure nodes are re-evaluated per impure consumer: a value decided from a variable must be cached before that
    variable is written (round 3 review of the graph)."""
    kt = graphs()["KneeTick"]
    for s_, S_ in (("l", "L"), ("r", "R")):
        th = next(n for n in kt["nodes"] if n["kind"] == "set" and n["var"] == "Th" + S_)
        assert not _uses_get(kt, th["id"], "WK" + S_), s_   # via the cached KinL/R
        assert _uses_get(kt, th["id"], "Kin" + S_)
    ht = graphs()["HandTick"]
    for S_ in ("L", "R"):
        ez = next(n for n in ht["nodes"] if n["kind"] == "set" and n["var"] == "HEz" + S_)
        assert not _uses_get(ht, ez["id"], "HEz" + S_)   # the near test is cached in HOn / HUse before HEz is written
        for vn in ("HTilt", "WH", "HOff"):
            st = next(n for n in ht["nodes"] if n["kind"] == "set" and n["var"] == vn + S_)
            assert not _uses_get(ht, st["id"], "HEz" + S_), vn
    ft = graphs()["FootTick"]
    for S_ in ("L", "R"):
        for vn in ("Off", "Fwd", "Tilt"):
            st = next(n for n in ft["nodes"] if n["kind"] == "set" and n["var"] == vn + S_)
            assert not _uses_get(ft, st["id"], "Ec" + S_), vn   # forward decision cached in Acc / Ft right after its trace


def test_return_only_with_outputs():
    """BPGen makes a return node only for functions with outputs (build 2026-11-08: 'exec: unknown node sKM or return')."""
    for f in bp()["functions"]:
        uses = any(x.split(":")[0] == "return" for c in f["graph"]["exec"] for x in c) or \
               any(b.split(".")[0] == "return" for _, b in f["graph"]["links"])
        if uses: assert f.get("outputs"), f["name"]


# ---------------- final review fixes (C1, C2, I1, I2, M1, M2, M4) ----------------
def _ids_reached(graph, node_id):
    nodes_ = {n["id"]: n for n in graph["nodes"]}; seen = set(); todo = [node_id]
    while todo:
        i = todo.pop()
        if i in seen: continue
        seen.add(i); todo += _refs(nodes_[i].get("in", {}))
    return seen


def _uses_ref(graph, node_id, ref): return ref in _ids_reached(graph, node_id)


def test_forward_pass_component_target_without_knee():
    """C1: pass B's joint target comes from the hip and the foot only (component space) - never from a calf / knee."""
    ft = graphs()["FootTick"]; ids = ids_of("FootTick")
    for S_ in ("L", "R"):
        st = next(n for n in ft["nodes"] if n["kind"] == "set" and n.get("var") == "FwdJ" + S_ and n.get("class") == ABP)
        reach = _ids_reached(ft, st["id"])
        socks = {ids[i]["in"].get("InSocketName") for i in reach if ids[i].get("function") == "GetSocketTransform"}
        assert socks == {"thigh_" + S_.lower(), "foot_" + S_.lower()}, socks
        assert any(ids[i].get("var") == "FwdReach" for i in reach)


def test_knee_arc_is_a_rotation():
    """C2: the arc = thigh rotated about the hip-foot axis by WK x Th, the foot rotated back by -WK x Th (relative to the input)."""
    kt = graphs()["KneeTick"]; ids = ids_of("KneeTick")
    for s_, S_ in (("l", "L"), ("r", "R")):
        for var, sign in (("KneeRot" + S_, False), ("KneeFoot" + S_, True)):
            st = next(n for n in kt["nodes"] if n["kind"] == "set" and n["var"] == var)
            src = ids[st["in"][var][1:].split(".")[0]]
            assert src["function"] == "RotatorFromAxisAndAngle" and src["in"]["Axis"] == "@ax%s.ReturnValue" % s_
            assert _uses_get(kt, st["id"], "WK" + S_) and _uses_get(kt, st["id"], "Th" + S_)
            assert ("-1.0" in json.dumps(ids[src["in"]["Angle"][1:].split(".")[0]]["in"])) == sign, var


def test_traces_at_animated_foot():
    """I1: the foot traces sample under the animated foot (final minus the forward move applied last frame)."""
    ids = ids_of("FootTick")
    for s_, S_ in (("l", "L"), ("r", "R")):
        x = ids["tr" + s_]["in"]["x"]; node = ids[x[1:].split(".")[0]]
        assert node["function"] == "BreakVector"
        av = ids[node["in"]["InVec"][1:].split(".")[0]]
        assert av["function"] == "Subtract_VectorVector" and av["in"]["A"] == "@sk%s.ReturnValue" % s_
        assert _uses_get(graphs()["FootTick"], av["id"], "Fwd" + S_)


def test_gate_feet_subtract_hips_and_effector():
    """I2: the gate's animated foot height subtracts the hips' move (PelAp) and the applied effector (Ec.z)."""
    ft = graphs()["FootTick"]
    for s_, S_ in (("l", "L"), ("r", "R")):
        assert _uses_get(ft, "an" + s_, "PelAp") and _uses_get(ft, "an" + s_, "Ec" + S_)


def test_forward_h2_in_range():
    ids = ids_of("FootTick")
    for s_ in ("l", "r"):
        assert ids["i2" + s_]["function"] == "InRange_FloatFloat" and ids["i2" + s_]["in"]["Value"] == "@h2%s.ReturnValue" % s_
        assert _uses_ref(graphs()["FootTick"], "acc" + s_, "i2" + s_)


def test_hold_none_guard():
    hc = graphs()["HoldCheck"]; ids = ids_of("HoldCheck")
    chain = next(c for c in hc["exec"] if c[0] == "fe")
    assert chain[1] == "bnn" and ids["bnn"]["kind"] == "branch" and ids["nn"]["function"] == "NotEqual_NameName" and chain[2] == "bh"


# ---------------- round 4 (spec 7e) ----------------
import numpy as np
import bp_eval


def _ids(name): return {n["id"]: n for n in graphs()[name]["nodes"]}


def _src(ids, ref): return ids[ref[1:].split(".")[0]]


def test_crouch_in_pose_chain():
    """crouch = paf < CrouchBelow, the lowest-priority type above stand (sit, lying, kneel, feet override it)."""
    ids = _ids("FootTick")
    sel = [n for n in ids.values() if n.get("function") == "SelectString" and n["in"].get("A") == "crouch"]
    assert len(sel) == 1 and sel[0]["in"]["B"] == "stand"
    cond = _src(ids, sel[0]["in"]["bPickA"])
    assert cond["function"] == "Less_FloatFloat" and cond["in"]["B"] == "@gCrouchBelow.CrouchBelow"
    assert _src(ids, cond["in"]["A"])["id"] == "mcpa"   # the hips above feet (mesh cm), the same as PAF
    nxt = [n for n in ids.values() if n.get("function") == "SelectString" and n["in"].get("B") == "@%s.ReturnValue" % sel[0]["id"]]
    assert len(nxt) == 1 and nxt[0]["in"]["A"] == "sit"


def test_crouch_mode_choice():
    ids = _ids("FootTick")
    md = [n for n in ids.values() if n.get("function") == "SelectFloat" and n["in"].get("A") == "@gCrouchMode.CrouchMode"]
    assert len(md) == 1
    pick = _src(ids, md[0]["in"]["bPickA"])
    assert pick["function"] == "EqualEqual_StrStr" and pick["in"]["B"] == "crouch"
    assert {v["name"]: v.get("default") for v in bp()["variables"]}["CrouchMode"] == "1.0"


def test_crouch_hip_limit_graph():
    ids = _ids("FootTick")
    neg = _src(ids, ids["tpm"]["in"]["A"])
    assert neg["function"] == "Multiply_FloatFloat" and neg["in"]["B"] == "-1.0"
    lim = _src(ids, neg["in"]["A"])
    assert lim["function"] == "SelectFloat" and lim["in"]["A"] == "@gCrouchDrop.CrouchDrop" and lim["in"]["B"] == "@gMaxPelvisDrop.MaxPelvisDrop"
    assert _src(ids, lim["in"]["bPickA"])["in"]["B"] == "crouch"


def test_mode_word():
    txt = json.dumps(graphs()["FootTick"])
    for w in ('"legs"', '"full"', '"off"'): assert w in txt, w
    assert any(n["kind"] == "set" and n["var"] == "ModeWord" for n in graphs()["FootTick"]["nodes"])


def _hst_run(frames, dt, p):
    v = {"HPrevL": np.zeros(3), "HPrevR": np.zeros(3), "HStillL": 0.0, "HStillR": 0.0, "HandStill": p["HandStill"]}
    fn_ = next(f for f in bp()["functions"] if f["name"] == "HandStillTick")
    out = []
    for pl, pr in frames:
        gr = json.loads(json.dumps(fn_["graph"]).replace('"@entry.pl"', json.dumps(_vec(pl))).replace('"@entry.pr"', json.dumps(_vec(pr)))
                        .replace('"@entry.dt"', '"%r"' % dt))
        bp_eval.Run(gr, v).run(); out.append((v["HStillL"], v["HStillR"]))
    return out


def _vec(p): return "(X=%r,Y=%r,Z=%r)" % tuple(float(x) for x in p)


def test_hand_still_graph():
    """HandStillTick (bp_eval) = footik_sim.hand_still_step, frame by frame (first frame from (0,0,0) resets)."""
    p = S.DEFAULTS; dt = 1 / 60
    frames = [((10 + 0.05 * (i % 2), 20, 5), (30 + i * 0.5, 20, 8)) for i in range(120)]   # left: 3 cm/s, right: 30 cm/s (sideways)
    got = _hst_run(frames, dt, p)
    sl, sr = {"prev": None, "t": 0.0}, {"prev": None, "t": 0.0}
    for (pl, pr), (tl, tr) in zip(frames, got):
        S.hand_still_step(sl, pl, dt, p); S.hand_still_step(sr, pr, dt, p)
        assert abs(tl - sl["t"]) < 1e-9 and abs(tr - sr["t"]) < 1e-9
    assert got[-1][0] > 1.5 and got[-1][1] == 0.0


def test_hand_still_in_hand_tick():
    ht = graphs()["HandTick"]; ids = {n["id"]: n for n in ht["nodes"]}
    chain = next(c for c in ht["exec"] if c[0] == "entry")
    assert chain[1] == "hst" and ids["hst"]["kind"] == "call_self" and ids["hst"]["function"] == "HandStillTick"
    assert chain.index("hst") < chain.index("sHOnL")
    for s, S_ in (("l", "L"), ("r", "R")):
        assert _uses_get(ht, "sHOn" + S_, "HStill" + S_) and _uses_get(ht, "sHOn" + S_, "HandStillFor")
        # the animated hand: the socket minus the hips' move and the hand IK's own vertical move (no feedback)
        pos = _src(ids, ids["hst"]["in"]["p" + s])
        assert pos["function"] == "Subtract_VectorVector"
        assert _uses_get(ht, pos["id"], "PelAp") and _uses_get(ht, pos["id"], "HEz" + S_)
    assert '"wait"' in json.dumps(ht)


def test_hand_still_reset_on_cast_fail():
    ft = graphs()["FootTick"]
    fail = next(c for c in ft["exec"] if c[0] == "cab:CastFailed")
    sets = {n["var"] for n in ft["nodes"] if n["kind"] == "set" and n["id"] in fail}
    assert {"HStillL", "HStillR"} <= sets




# ---------------- round 4 final review ----------------
def test_hand_still_graph_ignores_vertical():
    """Review I1: HandStillTick measures horizontal speed only (= footik_sim)."""
    dt = 1 / 60
    frames = [((10, 20, 5 + (i % 2) * 0.5), (30 + (i % 2) * 0.5, 20, 8)) for i in range(120)]
    got = _hst_run(frames, dt, S.DEFAULTS)
    assert got[-1][0] > 1.5 and got[-1][1] == 0.0
    fn_ = next(f for f in bp()["functions"] if f["name"] == "HandStillTick")["graph"]
    assert any(n.get("function") == "VSizeXY" for n in fn_["nodes"]) and not any(n.get("function") == "VSize" for n in fn_["nodes"])


def test_cast_fail_clears_status_words():
    """Review M2: another body -> the line shows no stale pose / knee / hand state."""
    ft = graphs()["FootTick"]
    fail = next(c for c in ft["exec"] if c[0] == "cab:CastFailed")
    got = {n["var"]: n["in"][n["var"]] for n in ft["nodes"] if n["kind"] == "set" and n["id"] in fail}
    assert got.get("ModeWord") == "" and got.get("KneeMode") == "-" and got.get("HandState") == "-"




# ---------------- AltUI port (plan Task 4) ----------------
def test_values_fixed_at_final():
    bp_ = driver()
    vs = {v["name"]: v for v in bp_["variables"]}
    for k, val in S.FINAL.items():
        if k not in vs: continue
        if vs[k]["type"] == "bool": assert vs[k]["default"] == "false", k   # the switches: copied from the manager every frame
        else: assert float(vs[k]["default"]) == float(val), k
    for k in g.VALUE_KEYS: assert float(vs[k]["default"]) == float(S.DEFAULTS[k]), k   # DEFAULTS = the final values (FINAL on top)
    assert "DbgShow" not in vs and "Mgr" not in vs and not any(k.startswith("Dbg") for k in vs)
    assert vs["Manager"]["type"] == "object:" + g.MGR


def test_switches_from_manager():
    f = fns()["FootTick"]; gets = [n for n in f["graph"]["nodes"] if n.get("kind") == "get"]
    names = {n.get("var") for n in gets}
    assert {"FootIKOn", "FootContactOn", "PanelOpen", "JodiHidden", "CamMode"} <= names
    ids = {n["id"]: n for n in f["graph"]["nodes"]}
    chain = next(c for c in f["graph"]["exec"] if c[0] == "entry")
    sw = chain[1:chain.index("bvp")]   # before the valid-pawn branch
    got = {ids[i]["var"]: ids[i]["in"][ids[i]["var"]] for i in sw}
    assert set(got) == {"On", "KneeOn", "HandOn"}
    assert got["KneeOn"] == got["HandOn"] != got["On"]
    for v, mv in (("On", "FootIKOn"), ("KneeOn", "FootContactOn")):
        a = ids[got[v][1:].split(".")[0]]
        assert a["function"] == "BooleanAND" and a["in"]["A"] == "@ivm.ReturnValue"   # Manager invalid -> false
        assert ids[a["in"]["B"][1:].split(".")[0]]["var"] == mv


def test_ticks_off_when_idle():
    f = fns()["FootTick"]
    assert any(n.get("function") == "SetActorTickEnabled" for n in f["graph"]["nodes"])
    assert "Wake" in fns()
    gr = f["graph"]; ids = {n["id"]: n for n in gr["nodes"]}
    main = next(c for c in gr["exec"] if c[0] == "entry")
    assert main[-2:] == ["bidl", "tidl"] and ids["tidl"]["in"]["bEnabled"] == "false" and main.index("sPA") < main.index("bidl")
    for v in ("On", "KneeOn", "HandOn", "W", "WB", "WKL", "WKR", "WHL", "WHR"): assert _uses_get(gr, "bidl", v), v
    fail = next(c for c in gr["exec"] if c[0] == "cab:CastFailed")
    assert fail[-2:] == ["bidf", "tidf"] and ids["tidf"]["in"]["bEnabled"] == "false"
    for v in ("On", "KneeOn", "HandOn"): assert _uses_get(gr, "bidf", v), v
    assert not _uses_get(gr, "bidf", "W")
    wake = fns()["Wake"]; assert "inputs" not in wake and "outputs" not in wake
    assert [n["in"]["bEnabled"] for n in wake["graph"]["nodes"] if n.get("function") == "SetActorTickEnabled"] == ["true"]


def test_manifest_order():
    with open(os.path.join(W, "assets", "manifest.txt")) as f: m = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    assert m.index("40_widgets.json") < m.index("45_footik.json") < m.index("50_manager_ui.json")


def test_event_graph_tick_only():
    ev = graphs()["EventGraph"]
    assert [n["kind"] for n in ev["nodes"]] == ["event", "call_self"] and bp().get("interfaces", []) == []
    names = set(fns())
    assert names == {"Trace", "SeqPlaying", "HoldCheck", "KneeTick", "HandTick", "FootTick", "HandStillTick", "Wake"}


def test_cast_to_body_scale():
    ids = {n["id"]: n for n in graphs()["FootTick"]["nodes"]}
    assert ids["cab"]["class"] == ABP == "/Game/Mod/AltUI/ABP_BodyScale"
    assert ids["aPel"]["var"] == "IKPelvis" and ids["aPel"]["in"]["self"] == "@cab.AsABP Body Scale"


def test_json_written():
    with open(os.path.join(W, "assets", "45_footik.json")) as f: data = json.load(f)["assets"]
    assert [a["path"] for a in data] == [g.FOOTIK] and data == json.loads(json.dumps(g.build()))


import footik_funcs
load_tests = footik_funcs.load_functions(sys.modules[__name__])
