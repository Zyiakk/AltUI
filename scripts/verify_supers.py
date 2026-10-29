#!/usr/bin/env python3
"""verify_supers.py - every function AltUI's cooked assets import from a game class (outer = <Class>_C under /Game/Project/) must be
defined by that very class in the game. Such an import is the SuperStruct of an override or the target of a call_parent; the kit's
stub chain can name a class that only inherits the function in the game (2026-10-18: Npc_Controller_C:on Character Die, defined in
AI_Controller) - the game then stops on load: "Could not find SuperStruct on <fn> to create <fn>".
Game assets come from $EXTRACTED/game (default extracted/game) (missing ones are extracted from the game pak). Requires COOKED and GAME (config.sh)."""
import os, sys, subprocess, glob
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from uasset_props import read_summary
W = os.path.dirname(H)
COOKED = os.environ["COOKED"]; GAME = os.environ["GAME"]
PAK = os.path.join(GAME, "Content/Paks/pakchunk0-WindowsNoEditor.pak")
X = os.environ.get("EXTRACTED") or os.path.join(W, "extracted")   # extracted game files (config.sh; dev: the knowledge base's)
EXTRACTED = os.path.join(X, "game/TheKillingAntidote/Content")


def imported_functions(path):
    """(class package path, class name, function name) for every Function import whose outer is a /Game/Project class."""
    _, _, imps, _, _ = read_summary(path)
    out = []
    for cpkg, cname, outer, oname in imps:
        if cname != "Function" or outer >= 0: continue
        _, ccls, couter, cobj = imps[-outer - 1]
        if not ccls.endswith("GeneratedClass") or couter >= 0: continue
        pkg = imps[-couter - 1][3]
        if pkg.startswith("/Game/Project/"): out.append((pkg, cobj, oname))
    return out


def own_functions(pkg):
    """Names of the functions the game asset defines itself (exports of class Function)."""
    rel = pkg[len("/Game/"):] + ".uasset"; path = os.path.join(EXTRACTED, rel)
    if not os.path.exists(path):
        rx = "Content/%s\\.(uasset|uexp)$" % pkg[len("/Game/"):].replace(".", "\\.")
        subprocess.run([sys.executable, os.path.join(H, "pak11_extract.py"), PAK, os.path.join(X, "game"), rx], check=True, stdout=subprocess.DEVNULL)
    _, _, imps, exps, _ = read_summary(path)
    fn = set()
    for on, cls, sup, outer, ssz, soff in exps:
        if cls < 0 and imps[-cls - 1][3] == "Function": fn.add(on)   # import (/Script/CoreUObject, Class, -, Function)
    return fn


def main():
    bad, n, cache = [], 0, {}
    for path in sorted(glob.glob(os.path.join(COOKED, "Mod/AltUI/**/*.uasset"), recursive=True)):
        for pkg, cls, f in imported_functions(path):
            n += 1
            if pkg not in cache: cache[pkg] = own_functions(pkg)
            if f not in cache[pkg]: bad.append("%s: %s:%s - the game's %s does not define it" % (os.path.basename(path), cls, f, pkg))
    for b in bad: print("BAD", b)
    if bad: print("VERIFY SUPERS FAILED"); sys.exit(1)
    print("VERIFY SUPERS OK (%d imported game functions, %d classes)" % (n, len(cache)))


if __name__ == "__main__":
    main()
