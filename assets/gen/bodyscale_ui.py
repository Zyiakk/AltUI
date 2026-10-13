"""Display text of a body-shape factor (bodyscale_groups.DISPLAY): x = "×1.00", pct = "75 %", deg = "-5°", num = "0.40"."""
from bpdsl import K_MATH, K_STR, K_TXT
import bodyscale_groups as bg


def factor_text(g, p, key, pin):
    """Nodes that turn the factor at `pin` into a Text; returns "@<id>.ReturnValue" of that Text."""
    kind = bg.DISPLAY.get(key, "x")
    if kind == "pct":
        g.call(p + "_m", K_MATH, "Multiply_FloatFloat", inp={"A": pin, "B": "100.0"}); g.call(p + "_r", K_MATH, "Round", inp={"A": "@%s_m.ReturnValue" % p})
        g.call(p + "_i", K_STR, "Conv_IntToString", inp={"InInt": "@%s_r.ReturnValue" % p}); g.call(p + "_c", K_STR, "Concat_StrStr", inp={"A": "@%s_i.ReturnValue" % p, "B": " %"})
    elif kind == "deg":
        g.call(p + "_r", K_MATH, "Round", inp={"A": pin}); g.call(p + "_i", K_STR, "Conv_IntToString", inp={"InInt": "@%s_r.ReturnValue" % p})
        g.call(p + "_c", K_STR, "Concat_StrStr", inp={"A": "@%s_i.ReturnValue" % p, "B": "°"})
    else:
        g.call(p + "_f", K_TXT, "Conv_FloatToText", inp={"Value": pin, "MinimumFractionalDigits": "2", "MaximumFractionalDigits": "2"})
        g.call(p + "_s", K_TXT, "Conv_TextToString", inp={"InText": "@%s_f.ReturnValue" % p})
        g.call(p + "_c", K_STR, "Concat_StrStr", inp={"A": "×" if kind == "x" else "", "B": "@%s_s.ReturnValue" % p})
    g.call(p, K_TXT, "Conv_StringToText", inp={"InString": "@%s_c.ReturnValue" % p})
    return "@%s.ReturnValue" % p
