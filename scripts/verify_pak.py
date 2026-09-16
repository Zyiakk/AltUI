#!/usr/bin/env python3
"""verify_pak.py <mod.pak> <hook.pak> – checks contents, mount paths, imports, hook CDO. Exit 1 on error."""
import sys, os, tempfile
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from pak11_extract import Pak
from uasset_props import read_summary, Reader
W = os.path.dirname(H)
_FL = os.environ.get("GAME_PAK_FILELIST")   # optional: text file listing every file in the game's paks -> import targets are checked against it
GAME_FILES = set(l.strip() for l in open(_FL)) if _FL and os.path.exists(_FL) else None
errors = []


def err(m):
    errors.append(m); print("VERIFY FAIL:", m)


def load_pak(p):
    pk = Pak(p)
    return pk, {k: pk.read(k) for k in pk.files}


def full_path(pk, k):
    # Mount "../../../TheKillingAntidote/Content/X/" + "Y.uasset" -> "TheKillingAntidote/Content/X/Y.uasset"
    return (pk.mount + k).replace("../../../", "").replace("//", "/")


def summary_of(uasset_bytes, uexp_bytes):
    d = tempfile.mkdtemp()
    ua = os.path.join(d, "a.uasset"); open(ua, "wb").write(uasset_bytes); open(ua[:-7] + ".uexp", "wb").write(uexp_bytes or b"")
    data, names, imps, exps, th = read_summary(ua)
    pkgs = sorted({on for (cp, cn, outer, on) in imps if cn == "Package" and on.startswith("/")})
    return names, imps, exps, pkgs, data + (uexp_bytes or b"")


def pkg_to_file(pkg):
    if pkg.startswith("/Game/"): return "TheKillingAntidote/Content/" + pkg[len("/Game/"):] + ".uasset"
    if pkg.startswith("/Engine/"): return "Engine/Content/" + pkg[len("/Engine/"):] + ".uasset"
    return None


mod_pak, mod_files = load_pak(sys.argv[1]); hook_pak, hook_files = load_pak(sys.argv[2])
mod_full = {full_path(mod_pak, k) for k in mod_files}
print("mod mount:", mod_pak.mount, "files:", sorted(mod_full))
print("hook mount:", hook_pak.mount, "files:", sorted(full_path(hook_pak, k) for k in hook_files))

# 1) mod pak: no Project/ assets, manager + Mod_Table present
for f in mod_full:
    if "/Content/Project/" in f: err("mod pak contains Project asset: " + f)
if not any(f.endswith("BP_AltUIManager.uasset") for f in mod_full): err("mod pak lacks BP_AltUIManager")
if not any(f.endswith("TKA_Mod_Table.uasset") for f in mod_full): err("mod pak lacks TKA_Mod_Table")

# 2) hook pak: exactly the one asset
hook_full = sorted(full_path(hook_pak, k) for k in hook_files)
if hook_full != ["TheKillingAntidote/Content/Project/Classes/TKA_PlayerCameraManager.uasset",
                 "TheKillingAntidote/Content/Project/Classes/TKA_PlayerCameraManager.uexp"]:
    err("hook pak content unexpected: %s" % hook_full)

# 3) imports of all assets resolvable (game pak or mod pak)
def check_imports(label, ua, ue):
    names, imps, exps, pkgs, data = summary_of(ua, ue)
    for p in pkgs:
        f = pkg_to_file(p)
        if f is None: continue
        if GAME_FILES is not None and f not in GAME_FILES and f not in mod_full: err("%s: import target missing in game+mod: %s" % (label, p))
    return names, imps, exps, data


for k, b in mod_files.items():
    if k.endswith(".uasset"): check_imports(k, b, mod_files.get(k[:-7] + ".uexp"))
hk = [k for k in hook_files if k.endswith(".uasset")][0]
names, imps, exps, data = check_imports(hk, hook_files[hk], hook_files.get(hk[:-7] + ".uexp"))

# 4) hook CDO: parent + ViewPitch; no hard reference to the mod pak
if not any(cn == "Class" and on == "PlayerCameraManager" for (cp, cn, outer, on) in imps): err("hook: parent PlayerCameraManager not imported")
cdo = [e for e in exps if e[0].startswith("Default__TKA_PlayerCameraManager")]
if not cdo:
    err("hook: CDO export missing")
else:
    r = Reader(data, names, imps, exps); r.p = cdo[0][5]; props = r.props()
    if abs(props.get("ViewPitchMin", 0) + 80.0) > 1e-3 or abs(props.get("ViewPitchMax", 0) - 70.0) > 1e-3: err("hook: ViewPitch defaults wrong: %s" % props)
    else: print("hook CDO ok:", {k: v for k, v in props.items() if k.startswith("ViewPitch")})
if any("/Game/Mod/AltUI" in on for (cp, cn, outer, on) in imps): err("hook: hard reference to mod pak (must be soft)")
print("VERIFY PAK", "FAILED" if errors else "OK")
sys.exit(1 if errors else 0)
