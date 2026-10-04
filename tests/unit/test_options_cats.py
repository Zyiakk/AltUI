"""Options page in categories (left list) and hideable tabs: data, settings, strings, widget tree, graphs
(docs/specs/2026-10-03-options-categories-tabs-design.md)."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
from strings import STRINGS
import gen_manager, gen_widgets, gen_manager_ui as ui


class OptionsData(unittest.TestCase):
    def test_cats_and_tabs(self):
        self.assertEqual(gen_widgets.OPT_CATS, ["General", "Tiles", "Groups", "Camera", "Controls", "Quick", "Theme", "Conflicts", "Tabs"])
        self.assertIn("Options", ui.TOP_TABS); self.assertEqual(len(ui.TOP_TABS), 13)

    def test_strings(self):
        for c in gen_widgets.OPT_CATS: self.assertEqual(len(STRINGS["OptCat_" + c]), 6, c)

    def test_settings(self):
        rows = {(m, s) for m, s, _, _ in gen_manager.SETTINGS}
        self.assertIn(("OptionsCat", "LastOptionsCat"), rows); self.assertIn(("HiddenTabs", "HiddenTabs"), rows)


ASSETS = os.path.join(H, "..", "..", "assets")


def graph(file, fn_name):
    for a in json.load(open(os.path.join(ASSETS, file)))["assets"]:
        for f in a.get("functions", []):
            if f["name"] == fn_name: return f["graph"]
    raise KeyError(fn_name)


def after(g, start):
    """Node ids reachable over exec links from the exec output `start` ("id" or "id:pin")."""
    adj = {}
    for chain in g["exec"]:
        for a, b in zip(chain, chain[1:]): adj.setdefault(a, set()).add(b.split(":")[0])
    seen, stack = set(), list(adj.get(start, ()))
    while stack:
        n = stack.pop()
        if n in seen: continue
        seen.add(n); stack += list(adj.get(n, ())) + [x for k, v in adj.items() if k.startswith(n + ":") for x in v]
    return seen


def calls(g, function):
    return [n["id"] for n in g["nodes"] if n.get("function") == function]


class TopTabs(unittest.TestCase):
    def test_every_tab_but_options_asks_tab_shown(self):
        g = graph("50_manager_ui.json", "Rebuild TopTabs")
        pages = sorted(n["in"]["page"] for n in g["nodes"] if n.get("function") == "Tab Shown")
        self.assertEqual(pages, sorted(p for p in ui.TOP_TABS if p != "Options"))

    def test_mod_scan_only_when_mods_shown(self):
        g = graph("50_manager_ui.json", "Rebuild TopTabs"); i = ui.TOP_TABS.index("Mods")
        scan = calls(g, "Scan Mod Entries"); self.assertEqual(len(scan), 1)
        self.assertIn(scan[0], after(g, "bs%d" % i)); self.assertNotIn(scan[0], after(g, "bs%d:else" % i))

    def test_open_panel_skips_clothes_when_hidden(self):
        g = graph("50_manager_ui.json", "Open Panel")
        self.assertNotIn("rcd", after(g, "bclh")); self.assertIn("rcd", after(g, "bclh:else"))
        self.assertIn("sopf", after(g, "bokp:else")); self.assertEqual(len(calls(g, "First Visible Page")), 1)



OLD_OPTION_ROWS = ['RowScroll', 'RowScale', 'RowFov', 'RowDist', 'RowHeight', 'RowGroupLen', 'RowChipH', 'RowUnlimited', 'RowPan', 'RowCamRight', 'RowNude',
                   'RowMerge', 'RowMergeMods', 'RowChipSearch', 'RowTipNoPrefix', 'RowTipNoIds', 'RowUnowned', 'RowLayout', 'RowLanguage', 'RowKey', 'LblTheme',
                   'ThemeGrid', 'RowBgAlpha', 'RowTileAlpha', 'ThemeLinks', 'LblConflicts', 'LblConflictsHint', 'ConflictLinks', 'ConflictRows']   # OptionsBox before the categories


def panel_tree():
    return next(a for a in json.load(open(os.path.join(ASSETS, "40_widgets.json")))["assets"] if a["path"].endswith("/W_AltUI"))["widget_tree"]


def find(n, name):
    if n["name"] == name: return n
    for c in n.get("children", []):
        r = find(c, name)
        if r: return r


def names(n):
    yield n["name"]
    for c in n.get("children", []): yield from names(c)


class Tree(unittest.TestCase):
    def test_every_option_in_exactly_one_category(self):
        box = find(panel_tree(), "OptionsBox")
        self.assertEqual([c["name"] for c in box["children"]], ["OptCat_" + c for c in gen_widgets.OPT_CATS])
        seen = {}
        for c in box["children"]:
            for n in names(c):
                if n in OLD_OPTION_ROWS: seen.setdefault(n, []).append(c["name"])
        self.assertEqual(sorted(seen), sorted(OLD_OPTION_ROWS)); self.assertTrue(all(len(v) == 1 for v in seen.values()), seen)

    def test_assignment(self):
        box = find(panel_tree(), "OptionsBox")
        cat = {n: c["name"][7:] for c in box["children"] for n in names(c)}
        for row, want in (("RowLanguage", "General"), ("RowScale", "Tiles"), ("RowChipH", "Groups"), ("RowFov", "Camera"), ("RowKey", "Controls"),
                          ("RowScroll", "Controls"), ("ThemeGrid", "Theme"), ("ConflictRows", "Conflicts"), ("TabChips", "Tabs"), ("LblTabsHint", "Tabs")):
            self.assertEqual(cat.get(row), want, row)

    def test_left_list_and_page(self):
        t = panel_tree(); hb = find(t, "OptionsHB")
        self.assertIsNotNone(hb); self.assertIn("OptionCats", set(names(hb))); self.assertIn("OptionsScroll", set(names(hb)))
        fns = {f["name"] for a in json.load(open(os.path.join(ASSETS, "40_widgets.json")))["assets"] if a["path"].endswith("/W_AltUI") for f in a["functions"]}
        self.assertTrue({"Set Option Cat", "Clear Option Cats", "Add Option Cat", "Clear Tab Chips", "Add Tab Chip"} <= fns)
        sp = json.dumps(next(f for a in json.load(open(os.path.join(ASSETS, "40_widgets.json")))["assets"] if a["path"].endswith("/W_AltUI") for f in a["functions"] if f["name"] == "Set Page"))
        self.assertIn('"OptionsHB"', sp); self.assertNotIn('"OptionsScroll"', sp)



class Manager(unittest.TestCase):
    def cat_branch(self, g, cat):
        """id of the branch whose condition compares OptionsCat with `cat`."""
        eqs = {n["id"] for n in g["nodes"] if n.get("function") == "EqualEqual_NameName" and cat in n.get("in", {}).values()}
        brs = [n["id"] for n in g["nodes"] if n.get("kind") == "branch" and any(("@%s." % e) in json.dumps(n) for e in eqs)]
        self.assertEqual(len(brs), 1, (cat, brs)); return brs[0]

    def test_rebuild_options_per_category(self):
        g = graph("50_manager_ui.json", "Rebuild Options")
        for fn_name, cat in (("Rebuild Conflicts", "Conflicts"), ("Rebuild Tab Chips", "Tabs")):
            c = calls(g, fn_name); self.assertEqual(len(c), 1, fn_name); b = self.cat_branch(g, cat)
            self.assertIn(c[0], after(g, b)); self.assertNotIn(c[0], after(g, b + ":else"))
        for fn_name, cat in (("Clear Layout Chips", "General"), ("Clear Key Chips", "Controls"), ("Clear Theme Swatches", "Theme")):
            c = calls(g, fn_name); b = self.cat_branch(g, cat); self.assertIn(c[0], after(g, b)); self.assertNotIn(c[0], after(g, b + ":else"))

    def test_dispatch(self):
        sst = json.dumps(graph("50_manager_ui.json", "Select SubTab")); self.assertIn('"Tab:"', sst); self.assertIn("Toggle Tab Hidden", sst)
        self.assertTrue(calls(graph("50_manager_ui.json", "Select Slot"), "Select Option Cat"))
        sp = graph("50_manager_ui.json", "Select Page"); self.assertTrue(calls(sp, "Rebuild Option Cats")); self.assertTrue(calls(sp, "Set Option Cat"))

    def test_tab_chips(self):
        g = graph("50_manager_ui.json", "Rebuild Tab Chips")
        groups = sorted(v for n in g["nodes"] if n.get("function") == "Init" for k, v in n["in"].items() if k == "group")
        self.assertEqual(groups, sorted(["Tab:" + p for p in ui.TOP_TABS if p != "Options"] + ["TabStyle0", "TabStyle1", "TabStyle2", "TabIconPos0", "TabIconPos1"]))

    def test_tab_style_chips_reach_select_tab_style(self):
        """TabStyle<n> / TabIconPos<n> are caught before the "Tab:" prefix and before the layout fallback."""
        g = graph("50_manager_ui.json", "Select SubTab")
        sts = calls(g, "Select Tab Style"); self.assertEqual(len(sts), 1)
        self.assertIn(sts[0], after(g, "bts")); self.assertNotIn(calls(g, "Toggle Tab Hidden")[0], after(g, "bts"))

    def test_top_tab_gets_icon_style_side(self):
        g = graph("50_manager_ui.json", "Rebuild TopTabs")
        inits = [n for n in g["nodes"] if n.get("function") == "Init"]; self.assertEqual(len(inits), len(ui.TOP_TABS))
        for n in inits: self.assertTrue({"icon", "style", "right"} <= set(n["in"]), n["in"])
        self.assertEqual({n["in"]["icon"] for n in inits}, set(ui.TAB_ICONS.values()))



class TopTabWidget(unittest.TestCase):
    def test_icon_shift_only_next_to_text(self):
        """W_TopTab.Init: the icons move up (render translation) only when text stands next to them; icons only: 0."""
        g = next(f["graph"] for a in json.load(open(os.path.join(ASSETS, "40_widgets.json")))["assets"] if a["path"].endswith("/W_TopTab")
                 for f in a["functions"] if f["name"] == "Init")
        nodes = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(sorted(n["in"]["self"] for n in g["nodes"] if n.get("function") == "SetRenderTranslation"), ["@gtIconLBox.IconLBox", "@gtIconRBox.IconRBox"])
        self.assertEqual(nodes["ty"]["in"]["bPickA"], "@both.ReturnValue"); self.assertEqual(float(nodes["ty"]["in"]["B"]), 0.0); self.assertLess(float(nodes["ty"]["in"]["A"]), 0)
        for n in ("tIconLBox", "tIconRBox"): self.assertIn(n, after(g, "entry"))


if __name__ == "__main__": unittest.main()
