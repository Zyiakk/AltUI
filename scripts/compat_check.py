#!/usr/bin/env python3
"""compat_check.py – after a game update: does everything AltUI relies on still exist in the installed game, unchanged?

AltUI is compiled against stubs of the game's classes (assets/10_stubs.json, cooked into the kit). A stub declares exactly
what AltUI uses: functions with their parameters, variables, the members of structs (by their internal names), the row
struct of each data table. In the shipped game a call to a function that is gone, or a struct member that was renamed,
does not fail politely - the Blueprint VM follows a null reference and the game crashes. This script compares every
stub with the asset of the same path in the game's pak:

  BROKEN    a function / variable / struct member AltUI uses is missing, or its type or parameter list changed;
            a data table has another row struct; a game asset AltUI loads by path is gone.
            -> AltUI must not be released for this game version as it is.
  HOOK      the game's own TKA_PlayerCameraManager differs from the baseline: AltUI_Hook_P.pak replaces that class
            with a copy of the OLD one, so in hook mode the game would run with its previous camera manager.
  CHANGED   an asset AltUI declares changed, but everything AltUI uses of it is intact (new functions, new members).
  ok        identical contract.

  scripts/compat_check.py                      check the installed game against the cooked stubs
  scripts/compat_check.py --pak <file.pak>     another pak (e.g. a copied old/new version)
  scripts/compat_check.py --write-baseline     after a release-ready check: store the hashes of the checked game assets
                                               (knowledge/compat_baseline.json) - CHANGED / HOOK compare against them

Needs the cooked kit (COOKED from config.sh, i.e. one ./build.sh) and the game's pak (GAME). Exit code 1 on BROKEN or HOOK.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H); sys.path.insert(0, H)
import uasset_funcs, uasset_props, compat_fp

STUBS = os.path.join(W, "assets", "10_stubs.json")
BASELINE = os.path.join(W, "knowledge", "compat_baseline.json")
HOOK_BASE = "/Game/Project/Classes/TKA_PlayerCameraManager"
OWN_PREFIXES = ("/Game/Mod/",)   # AltUI's own and other mods' folders: not the game's
FILELIST = os.path.join(W, "knowledge", "game_pak_filelist.txt")


def env():
    out = subprocess.run(["bash", "-c", "source '%s/config.sh' >/dev/null 2>&1; echo \"$COOKED\"; echo \"$GAME\"" % W], capture_output=True, text=True).stdout.splitlines()
    return out[0], out[1]


def game_rel(path):
    """/Game/Project/X/Y -> Project/X/Y (relative to Content)."""
    return path[len("/Game/"):]


def extract(pak, paths, out):
    """Pull <path>.uasset/.uexp of every path out of the game's pak (pak11_extract with one regex)."""
    rx = "TheKillingAntidote/Content/(%s)\\.(uasset|uexp)$" % "|".join(re.escape(game_rel(p)) for p in paths)
    subprocess.run([sys.executable, os.path.join(H, "pak11_extract.py"), pak, out, rx], check=True, capture_output=True)


def pak_files(pak):
    r = subprocess.run([sys.executable, os.path.join(H, "pak11_extract.py"), pak, "list"], capture_output=True, text=True)
    return set(l.strip() for l in r.stdout.split("\n") if l.strip()) if r.returncode == 0 and r.stdout.strip() else None


def sha(path):
    h = hashlib.sha256()
    for ext in (".uasset", ".uexp"):
        f = path + ext
        if os.path.exists(f): h.update(open(f, "rb").read())
    return h.hexdigest()


PRIM = {"int", "float", "bool", "Name", "String", "Text", "int64", "double", "byte", "uint32"}


def ptypes(f):
    """Parameter types of a dumped function, out/ref marks dropped (const& Name and ref Name pass the same way), return last."""
    return [re.sub(r"^(out |ref |const& )?[^:]*: ", "", p) for p in f["params"]] + (["-> " + f["ret"]] if f["ret"] else [])


def same_kind(a, b):
    """Two parameter types AltUI can pass interchangeably: equal, or both object references (a stub may name a subclass
    the game's function takes as its base class - Jodi_C for Jodi_Base_C)."""
    if a == b: return True
    strip = lambda t: t.replace("-> ", "")
    a, b = strip(a), strip(b)
    if a in PRIM or b in PRIM: return False
    if any(t.startswith(("Array<", "Map<", "Set<")) for t in (a, b)): return a.split("<")[0] == b.split("<")[0]
    return True


class Game:
    """The game's classes as AltUI sees them: a class and its parents (resolved by class name through the pak listing)."""
    def __init__(self, pak, listing, tmp):
        self.pak, self.tmp, self.cache = pak, tmp, {}
        self.by_name = {}
        for k in listing or []:
            if k.endswith(".uasset") and k.startswith("TheKillingAntidote/Content/"):
                self.by_name.setdefault(os.path.basename(k)[:-7], "/Game/" + k[len("TheKillingAntidote/Content/"):-7])

    def dump(self, path):
        if path not in self.cache:
            f = os.path.join(self.tmp, "TheKillingAntidote", "Content", game_rel(path))
            if not os.path.exists(f + ".uasset"): extract(self.pak, [path], self.tmp)
            self.cache[path] = uasset_funcs.dump(f + ".uasset") if os.path.exists(f + ".uasset") else None
        return self.cache[path]

    def chain(self, path):
        """[dump of the class, its parent, ...] while the parents are game Blueprints."""
        out, seen = [], set()
        while path and path not in seen:
            seen.add(path); d = self.dump(path)
            if not d: break
            out.append(d)
            sup = str((d.get("class") or {}).get("super") or "")
            m = re.match(r"import:(\w+?)_C\b", sup)
            path = self.by_name.get(m.group(1)) if m else None
        return out

    def function(self, path, name):
        for d in self.chain(path):
            if name in d["functions"]: return d["functions"][name]
        return None

    def var(self, path, name):
        for d in self.chain(path):
            for v in (d.get("class") or {}).get("vars", []):
                if v["name"] == name: return v["type"]
        return None


def altui_calls(cooked, decls=()):
    """(game package, function) AltUI calls on game classes: every function AltUI declares in its stubs (10_stubs.json) - a call to
    another Blueprint's function is compiled as a call BY NAME (EX_VirtualFunction) and resolved when it runs, so a missing one
    is a fatal error then - plus every game function its cooked assets import (final / static calls)."""
    out = {(x["path"], f["name"]) for x in decls if x.get("type") == "blueprint" for f in x.get("functions", [])}
    root = os.path.join(cooked, "Mod", "AltUI")
    files = [os.path.join(root, f) for f in os.listdir(root) if f.endswith(".uasset")] if os.path.isdir(root) else []
    hook = os.path.join(cooked, "Project", "Classes", "TKA_PlayerCameraManager.uasset")
    for f in files:
        _, _, imps, _, _ = uasset_props.read_summary(f)
        def pkg(i):
            while i < 0:
                cp, cn, outer, on = imps[-i - 1]
                if cn == "Package": return on
                i = outer
            return None
        for cp, cn, outer, on in imps:
            if cn == "Function" and outer < 0:
                p = pkg(outer)
                if p and p.startswith("/Game/") and not p.startswith(OWN_PREFIXES): out.add((p, on))
    return out


def compare(kind, path, stub_file, game, decl, report):
    gf = os.path.join(game.tmp, "TheKillingAntidote", "Content", game_rel(path))
    if game.dump(path) is None and kind != "datatable":
        report["BROKEN"].append("%s: gone from the game" % path); return
    if kind == "datatable":
        if not os.path.exists(gf + ".uasset"): report["BROKEN"].append("%s: gone from the game" % path); return
        want = decl.get("row_struct"); got = row_struct(gf + ".uasset")
        if want and got and want.rsplit("/", 1)[-1] != got.rsplit("/", 1)[-1]:
            report["BROKEN"].append("%s: row struct %s, AltUI expects %s" % (path, got, want))
        return
    if kind == "enum": return
    if not os.path.exists(stub_file + ".uasset"):
        report["BROKEN"].append("%s: cooked stub missing (run ./build.sh)" % path); return
    s = uasset_funcs.dump(stub_file + ".uasset")
    if kind == "struct":
        gm = {m["name"]: m["type"] for m in (game.dump(path).get("struct") or {}).get("members", [])}
        for m in (s.get("struct") or {}).get("members", []):
            if m["name"] not in gm: report["BROKEN"].append("%s: member %s gone" % (path, m["name"]))
            elif not same_kind(gm[m["name"]], m["type"]): report["BROKEN"].append("%s: member %s is %s, AltUI expects %s" % (path, m["name"], gm[m["name"]], m["type"]))
            elif gm[m["name"]] != m["type"]: report["NOTE"].append("%s: member %s is %s, the stub says %s" % (path, m["name"], gm[m["name"]], m["type"]))
        return
    # the variables AltUI declares (10_stubs.json) - the kit's own stubs carry more (DefaultSceneRoot, ...) that AltUI never reads
    declared = {v["name"] for v in decl.get("variables", [])}
    for n, t in {v["name"]: v["type"] for v in (s.get("class") or {}).get("vars", [])}.items():
        if n not in declared: continue
        gt = game.var(path, n)
        if gt is None: report["BROKEN"].append("%s: variable '%s' gone" % (path, n))
        elif not same_kind(gt, t): report["BROKEN"].append("%s: variable '%s' is %s, AltUI expects %s" % (path, n, gt, t))


def check_calls(calls, cooked, game, report):
    """Every function AltUI imports from a game class: found in the class or a parent, same parameter list."""
    for pkgpath, fname in sorted(calls):
        g = game.function(pkgpath, fname)
        if g is None:
            report["BROKEN"].append("%s: function '%s' gone (AltUI calls it)" % (pkgpath, fname)); continue
        sf = os.path.join(cooked, game_rel(pkgpath))
        st = None
        if os.path.exists(sf + ".uasset"):
            st = uasset_funcs.dump(sf + ".uasset")["functions"].get(fname)
        if not st: continue
        a, b = ptypes(g), ptypes(st)
        if len(a) != len(b) or not all(same_kind(x, y) for x, y in zip(a, b)):
            report["BROKEN"].append("%s: function '%s' is (%s), AltUI calls (%s)" % (pkgpath, fname, ", ".join(a), ", ".join(b)))
        elif a != b:
            report["NOTE"].append("%s: function '%s' is (%s), the stub says (%s)" % (pkgpath, fname, ", ".join(a), ", ".join(b)))


def row_struct(uasset):
    try:
        d = uasset_props.dump(uasset) if hasattr(uasset_props, "dump") else None
    except Exception:
        d = None
    if not d: return None
    for v in d.values():
        rs = str((v.get("props") or {}).get("RowStruct") or "")
        m = re.match(r"import:(\w+)", rs)
        if m: return m.group(1)
    return None


def row_count(uasset):
    try:
        d = uasset_props.dump(uasset)
    except Exception:
        return -1
    return sum(len(v.get("rows") or {}) for v in d.values()) if d else -1


def referenced_game_paths():
    """Every /Game/... path (outside /Game/Mod/) the generated AltUI assets name - loaded by path at run time."""
    found = set()
    for f in sorted(os.listdir(os.path.join(W, "assets"))):
        if not f.endswith(".json") or f == "10_stubs.json": continue
        for m in re.finditer(r"/Game/([A-Za-z0-9_/\-]+)", open(os.path.join(W, "assets", f), encoding="utf-8").read()):
            p = "/Game/" + m.group(1).split(".")[0]
            if not p.startswith(OWN_PREFIXES): found.add(p)
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pak"); ap.add_argument("--write-baseline", action="store_true"); ap.add_argument("--keep", help="keep the extracted files here")
    ap.add_argument("--notes", action="store_true", help="also print the NOTE lines (stub types that differ harmlessly)")
    a = ap.parse_args()
    cooked, gamedir = env()
    pak = a.pak or os.path.join(gamedir, "Content", "Paks", "pakchunk0-WindowsNoEditor.pak")
    decls = [x for x in json.load(open(STUBS))["assets"] if x.get("path", "").startswith("/Game/") and not x["path"].startswith(OWN_PREFIXES)]
    tmp = a.keep or tempfile.mkdtemp(prefix="compat_")
    try:
        listing = pak_files(pak)
        game = Game(pak, listing, tmp)
        extract(pak, sorted({x["path"] for x in decls} | {HOOK_BASE}), tmp)
        report = {"BROKEN": [], "HOOK": [], "CHANGED": [], "NOTE": [], "ok": []}
        base = json.load(open(BASELINE)) if os.path.exists(BASELINE) else {}
        base_assets = {k: v for k, v in base.items() if k.startswith("/")}
        hashes = {}
        for x in decls:
            p = x["path"]; gf = os.path.join(tmp, "TheKillingAntidote", "Content", game_rel(p))
            n = len(report["BROKEN"]); compare(x["type"], p, os.path.join(cooked, game_rel(p)), game, x, report)
            if os.path.exists(gf + ".uasset"): hashes[p] = sha(gf)
            if len(report["BROKEN"]) == n:
                (report["CHANGED"] if base.get(p) and hashes.get(p) != base[p] else report["ok"]).append(p)
        calls = altui_calls(cooked, decls); check_calls(calls, cooked, game, report)
        hf = os.path.join(tmp, "TheKillingAntidote", "Content", game_rel(HOOK_BASE))
        if os.path.exists(hf + ".uasset"):
            hashes[HOOK_BASE] = sha(hf)
            if base.get(HOOK_BASE) and hashes[HOOK_BASE] != base[HOOK_BASE]:
                report["HOOK"].append("%s changed in the game: AltUI_Hook_P.pak would put the old one back - rebuild the hook from the new class, or use the Blueprint Loader only" % HOOK_BASE)
        if listing:
            roots = {k.split("/")[2] for k in listing if k.startswith("TheKillingAntidote/Content/") and k.count("/") > 2}
            for p in sorted(referenced_game_paths()):
                if game_rel(p).split("/")[0] not in roots: continue   # editor test fixtures (/Game/X/...) - never in a game
                if not any(("TheKillingAntidote/Content/%s.%s" % (game_rel(p), e)) in listing for e in ("uasset", "umap")):
                    report["BROKEN"].append("%s: referenced by AltUI, not in the pak" % p)
        for k in ("BROKEN", "HOOK", "CHANGED") + (("NOTE",) if a.notes else ()):
            for line in report[k]: print("%-8s %s" % (k, line))
        print("ok       %d declared assets intact, %d game functions AltUI calls checked%s" % (len(report["ok"]), len(calls), "" if a.notes else ", %d notes (--notes)" % len(report["NOTE"])))
        counts = {p: row_count(os.path.join(tmp, "TheKillingAntidote", "Content", game_rel(p)) + ".uasset") for p in compat_fp.FP_TABLES}
        fp = compat_fp.fp_string(counts)
        if base.get("fingerprint") and base["fingerprint"] != fp: print("FINGERPRINT %s (baseline %s) - AltUI will warn in the main menu until rebuilt" % (fp, base["fingerprint"]))
        if a.write_baseline:
            os.makedirs(os.path.dirname(BASELINE), exist_ok=True)
            out = dict(sorted(hashes.items())); out["fingerprint"] = fp
            json.dump(out, open(BASELINE, "w"), indent=1); print("baseline written:", BASELINE, len(hashes), "assets, fingerprint", fp)
        bad = report["BROKEN"] or report["HOOK"]
        print("COMPAT", "PROBLEMS" if bad else "OK")
        return 1 if bad else 0
    finally:
        if not a.keep: shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
