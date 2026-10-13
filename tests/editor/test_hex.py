import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


# W_HexBar: Color To Hex / Hex To Color are sRGB codes over the linear colours of the palette (Discord: copy a colour from
# one piece to another, or see its hex code). Expected values from the sRGB curve, as Conv_LinearColorToColor computes it.
def srgb(c):
    c = min(max(c, 0.0), 1.0)
    return round(255 * (12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055))


def lin(b):
    s = b / 255.0
    return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    def hx(s="", color=(0, 0, 0)):
        mgr.call_method("Test Hex", args=(s, unreal.LinearColor(color[0], color[1], color[2], 1)))
        c = mgr.get_editor_property("TmpColor")
        return str(mgr.get_editor_property("TmpStr")), mgr.get_editor_property("TmpBool"), (c.r, c.g, c.b, c.a)
    expect("white", hx(color=(1, 1, 1))[0], "#FFFFFF")
    expect("black", hx(color=(0, 0, 0))[0], "#000000")
    expect("clamped above 1 and below 0", hx(color=(4, -1, 1))[0], "#FF00FF")
    for col in ((0.5, 0.2, 0.05), (0.002, 0.0031308, 0.9), (0.214, 0.5, 0.75)):
        want = "#" + "".join("%02X" % srgb(c) for c in col)
        expect("encode %s" % (col,), hx(color=col)[0], want)
    for code, rgb in (("#FF8000", (255, 128, 0)), ("ff8000", (255, 128, 0)), ("  #0a1B2c ", (10, 27, 44)), ("#000000", (0, 0, 0))):
        s, ok, c = hx(code)
        expect("decode ok " + code, ok, True)
        for got, b in zip(c[:3], rgb):
            expect("decode %s channel %d" % (code, b), abs(got - lin(b)) < 1e-4, True)
        expect("decode alpha " + code, round(c[3], 3), 1.0)
    for bad in ("", "#FFF", "#GG0000", "#12345", "#1234567", "12 456"):
        expect("invalid " + repr(bad), hx(bad)[1], False)
    # round trip: every code survives decode -> encode
    for code in ("#FF8000", "#0A1B2C", "#808080", "#010203", "#FEFDFC"):
        mgr.call_method("Test Hex", args=(code, unreal.LinearColor(0, 0, 0, 1)))
        c = mgr.get_editor_property("TmpColor")
        expect("round trip " + code, hx(color=(c.r, c.g, c.b))[0], code)


run(main)
