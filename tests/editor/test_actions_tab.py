"""Actions tab (spec 2026-10-26): catalogue by category, filter by category and search (no case), headings only under All,
"Nothing found.", anchors found again / gone, and the filter's cost with 800 outfits."""
import sys, os, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.set_editor_property("Outfits", None); mgr.call_method("Test Load Outfits")
    for i in range(3): mgr.call_method("Test Add Outfit", (["Ac%d_a" % i, "Ac%d_b" % i],))
    mgr.call_method("Test Act Catalog")
    cats = [str(c) for c in mgr.get_editor_property("ActCats")]
    expect("groups in order", cats[:3], ["Camera", "Outfits", "Looks"])
    n = dict((str(k), v) for k, v in mgr.get_editor_property("ActCatN").items())
    expect("three outfits", n.get("Outfits"), 3)
    items = [str(x) for x in mgr.get_editor_property("QcItems")]; cat_of = [str(x) for x in mgr.get_editor_property("QcCat")]
    expect("parallel arrays", len(items), len(cat_of)); expect("captions cached", len(mgr.get_editor_property("QcCap")), len(items))

    mgr.call_method("Test Act Filter", ("Outfits", ""))
    kinds = list(mgr.get_editor_property("QaKind")); expect("one category: no heading", 1 in kinds, False); expect("its items", len(kinds), 3)
    mgr.call_method("Test Act Filter", ("All", ""))
    kinds = list(mgr.get_editor_property("QaKind")); heads = [str(h) for h in mgr.get_editor_property("QaHeads")]
    expect("All: headings", heads[:2], ["QuickGrp_Camera", "QuickGrp_Outfits"]); expect("All: every item", kinds.count(2), len(items))
    cap0 = str(mgr.get_editor_property("QcCap")[items.index(next(i for i in items if i.startswith("outfit:")))])
    mgr.call_method("Test Act Filter", ("All", cap0.upper()))
    hits = [str(x) for x in mgr.get_editor_property("QaItems")]
    expect("search without case finds the outfit", any(h.startswith("outfit:") for h in hits), True)
    mgr.call_method("Test Act Filter", ("All", "zzz-nothing-zzz"))
    expect("nothing found: one heading", [str(h) for h in mgr.get_editor_property("QaHeads")], ["Act_NoHits"])

    # anchors: an entry found again, a gone one -> -1
    mgr.call_method("Test Act Filter", ("Outfits", ""))
    mgr.call_method("Test Act Entry Key", (1,)); key = str(mgr.get_editor_property("TmpStr"))
    mgr.set_editor_property("ActAnchorKey", {"Outfits": key}); mgr.set_editor_property("ActAnchorOff", {"Outfits": 5.0})
    mgr.call_method("Test Act Anchor Restore", ("Outfits",)); expect("anchor found", mgr.get_editor_property("TmpI"), 1)
    mgr.set_editor_property("ActAnchorKey", {"Outfits": "outfit:gone"})
    mgr.call_method("Test Act Anchor Restore", ("Outfits",)); expect("anchor gone", mgr.get_editor_property("TmpI"), -1)

    # cost: 800 outfits, one keystroke = one filter
    for i in range(3, 800): mgr.call_method("Test Add Outfit", (["Ac%d_a" % i, "Ac%d_b" % i],))
    t = time.perf_counter(); mgr.call_method("Test Act Catalog"); tc = time.perf_counter() - t
    t = time.perf_counter()
    for _ in range(10): mgr.call_method("Test Act Filter", ("All", "Ac7"))
    tf = (time.perf_counter() - t) / 10
    unreal.log_warning("EDTEST step actions: catalogue %.1f ms, filter %.1f ms (800 outfits)" % (tc * 1000, tf * 1000))
    report("filter per keystroke under 30 ms", tf < 0.030, "%.1f ms" % (tf * 1000))
    report("catalogue under 400 ms", tc < 0.400, "%.1f ms" % (tc * 1000))
    mgr.set_editor_property("Outfits", None)


run(main)
