#!/usr/bin/env python3
"""animcurves.py - curves of a cooked UE 4.27 AnimSequence (codec CompressedRichCurve), e.g. MoveData_Speed / Rotation Speed of
Jodi's walk (docs/specs/2026-10-06-anim-pipeline-design.md). umodel does not export curves; this reads them from the .uexp.

Layout (FCompressedAnimSequence::SerializeCompressedData): ... CompressedCurveNames (int32 count, FName = name index + number) ...
bone stream ... FString BoneCodecDDCHandle, FString CurveCodecPath, int32 NumCurveBytes, curve bytes. The curve bytes start with one
12-byte FCurveDesc per curve (format, key time format, pre / post extrapolation as bytes, ConstantValue (float) or NumKeys (int32),
KeyDataOffset (int32)), then the keys (RichCurve.cpp: InterpEvalMap and the key adapters).

  animcurves.py <file.uasset> [--fps 30]   -> JSON {"length": s, "curves": {name: [[t, v], ...]}} sampled per frame
"""
import sys, os, struct, json, math
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import uasset_props as up

EMPTY, CONSTANT, LINEAR, CUBIC, MIXED, WEIGHTED = range(6)          # ERichCurveCompressionFormat
T_U16, T_F32 = 0, 1                                                 # ERichCurveKeyTimeCompressionFormat
X_CYCLE, X_CYCLE_OFFSET, X_OSCILLATE, X_LINEAR, X_CONSTANT = range(5)   # ERichCurveExtrapolation
CODEC = b"/Engine/Animation/DefaultAnimCurveCompressionSettings"


def _align(v, a): return (v + a - 1) // a * a


def _curve_names(b, names, count_hint):
    """CompressedCurveNames: int32 count + count x (name index, number) whose names are all in the name table, right after
    CompressedTrackToSkeletonMapTable (int32 count + bone indices) - searched, its offset depends on the tagged properties."""
    for p in range(0, len(b) - 8):
        n = struct.unpack_from("<i", b, p)[0]
        if n != count_hint: continue
        idx = [struct.unpack_from("<ii", b, p + 4 + 8 * k) for k in range(n)]
        if not (all(0 <= i < len(names) and num == 0 for i, num in idx) and len({i for i, _ in idx}) == n): continue
        # right before it: CompressedTrackToSkeletonMapTable = int32 count M + M bone indices (small, distinct)
        for m in range(1, 400):
            q = p - 4 - 4 * m
            if q < 0: break
            if struct.unpack_from("<i", b, q)[0] == m:
                bones = struct.unpack_from("<%di" % m, b, q + 4)
                if all(0 <= x < 1000 for x in bones) and len(set(bones)) == m: return [names[i] for i, _ in idx]
    raise ValueError("CompressedCurveNames not found")


def _desc(cb, k):
    fmt, tf, pre, post = cb[12 * k:12 * k + 4]
    return {"format": fmt, "time_format": tf, "pre": pre, "post": post, "num_keys": struct.unpack_from("<i", cb, 12 * k + 4)[0],
            "constant": struct.unpack_from("<f", cb, 12 * k + 4)[0], "offset": struct.unpack_from("<i", cb, 12 * k + 8)[0]}


def _keys(cb, d):
    """Key list [(time, value, arrive, leave, interp)] of a keyed curve."""
    n, base, fmt = d["num_keys"], d["offset"], d["format"]
    modes_off = 0
    if fmt == MIXED: times_off = _align(n, 2 if d["time_format"] == T_U16 else 4)
    elif fmt == WEIGHTED: times_off = _align(2 * n, 2 if d["time_format"] == T_U16 else 4)
    else: times_off = 0
    if d["time_format"] == T_U16:
        raw = struct.unpack_from("<%dH" % n, cb, base + times_off)
        range_off = _align(times_off + 2 * n, 4); tmin, tdelta = struct.unpack_from("<ff", cb, base + range_off)
        times = [r / 65535.0 * tdelta + tmin for r in raw]; data_off = range_off + 8
    else:
        times = list(struct.unpack_from("<%df" % n, cb, base + times_off)); data_off = _align(times_off + 4 * n, 4)
    stride = 3 if fmt in (CUBIC, MIXED) else 5 if fmt == WEIGHTED else 1
    vals = struct.unpack_from("<%df" % (n * stride), cb, base + data_off)
    keys = []
    for i in range(n):
        mode = cb[base + modes_off + i] if fmt in (MIXED, WEIGHTED) else fmt
        if stride == 1: keys.append((times[i], vals[i], 0.0, 0.0, mode))
        else: keys.append((times[i], vals[i * stride], vals[i * stride + 1], vals[i * stride + 2], mode))
    return keys


def read(uasset):
    """{"length": seconds, "curves": {name: curve}}; a curve is {"constant": v} or {"keys": [...], "pre": x, "post": x}."""
    d, names, imps, exps, th = up.read_summary(uasset)
    b = open(os.path.splitext(uasset)[0] + ".uexp", "rb").read()
    i = b.find(CODEC); n = struct.unpack_from("<i", b, i - 4)[0]
    p = i + n; nbytes = struct.unpack_from("<i", b, p)[0]; cb = b[p + 4:p + 4 + nbytes]
    # the compressor starts KeyDataOffset after the descriptors: the first one's offset is 12 x the number of curves
    count = struct.unpack_from("<i", cb, 8)[0] // 12 if len(cb) >= 12 else 0
    curve_names = _curve_names(b, names, count)
    curves = {}
    for k, name in enumerate(curve_names):
        dd = _desc(cb, k)
        if dd["format"] in (EMPTY, CONSTANT): curves[name] = {"constant": dd["constant"]}
        else: curves[name] = {"keys": _keys(cb, dd), "pre": dd["pre"], "post": dd["post"]}
    length = None
    try:
        import subprocess
        out = json.loads(subprocess.run([sys.executable, os.path.join(H, "uasset_props.py"), uasset], capture_output=True, text=True).stdout)
        length = next(v["props"].get("SequenceLength") for k, v in out.items() if isinstance(v, dict) and "props" in v and not k.startswith("Default"))
    except Exception: pass
    return {"length": length, "curves": curves}


def _bezier(p0, p1, p2, p3, a):
    q0, q1, q2 = p0 + (p1 - p0) * a, p1 + (p2 - p1) * a, p2 + (p3 - p2) * a
    r0, r1 = q0 + (q1 - q0) * a, q1 + (q2 - q1) * a
    return r0 + (r1 - r0) * a


def evaluate(curve, t):
    """Value at time t like FCompressedRichCurve::Eval (cycle / oscillate / linear / constant extrapolation; weighted keys as cubic)."""
    if "constant" in curve: return curve["constant"]
    keys = curve["keys"]; t0, tn = keys[0][0], keys[-1][0]; off = 0.0
    if len(keys) == 1: return keys[0][1]
    for edge, mode in ((t <= t0, curve["pre"]), (t >= tn, curve["post"])):
        if not edge: continue
        if mode in (X_LINEAR, X_CONSTANT):
            (ka, kb) = (keys[0], keys[1]) if t <= t0 else (keys[-1], keys[-2])
            if mode == X_CONSTANT or abs(kb[0] - ka[0]) < 1e-8: return ka[1]
            return ka[1] + (kb[1] - ka[1]) / (kb[0] - ka[0]) * (t - ka[0])
        dur = tn - t0; cycles = math.floor((t - t0) / dur); tt = t - cycles * dur
        if mode == X_CYCLE_OFFSET: off = (keys[-1][1] - keys[0][1]) * cycles
        if mode == X_OSCILLATE and cycles % 2: tt = t0 + (tn - tt)
        t = tt
    for i in range(1, len(keys)):
        if t < keys[i][0] or i == len(keys) - 1: break
    k0, k1 = keys[i - 1], keys[i]; diff = k1[0] - k0[0]
    if diff <= 0 or k0[4] == CONSTANT: return k0[1] + off
    a = (t - k0[0]) / diff
    if k0[4] == LINEAR: return k0[1] + (k1[1] - k0[1]) * a + off
    third = diff / 3.0
    return _bezier(k0[1], k0[1] + k0[3] * third, k1[1] - k1[2] * third, k1[1], a) + off


def sample(c, fps=30.0):
    """{name: [[t, v], ...]} one row per frame over the sequence length (inclusive)."""
    n = int(round((c["length"] or 0) * fps)) + 1
    return {name: [[i / fps, evaluate(cv, i / fps)] for i in range(n)] for name, cv in c["curves"].items()}


if __name__ == "__main__":
    a = sys.argv[1:]; fps = float(a[a.index("--fps") + 1]) if "--fps" in a else 30.0
    c = read(a[0]); print(json.dumps({"length": c["length"], "curves": sample(c, fps)}, indent=1))
