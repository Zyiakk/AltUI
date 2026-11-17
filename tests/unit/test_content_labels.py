"""Content views (look / outfit / preset / face: Rebuild Content; a mod preset: Rebuild Mod Preset Content) show tables of
label | value. Every row must be told apart by what it says: in every UI language its label is unique under its heading
line (2026-11-10: a look showed "Angle (with less jiggle)" and "Jiggle" twice each - breast and glutes - without the
headings the Body Shape page has). Also: a ragdoll copy takes the source's component scale (Jodi's height slider)."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, os.path.join(H, "..", "..", "scripts"))
from strings import STRINGS, LANGS
import bodyscale_groups as bg
ASSETS = os.path.join(H, "..", "..", "assets")
W_VALROW = "/Game/Mod/AltUI/W_ValueRow"; W_SECTION = "/Game/Mod/AltUI/W_ContentSection"


def fn_graph(file, name):
    for a in json.load(open(os.path.join(ASSETS, file)))["assets"]:
        for f in a.get("functions", []):
            if f.get("name") == name and f.get("graph"):
                return f["graph"]
    raise AssertionError("function %s not found" % name)


def walk(graph, start):
    """Exec ids from `start` with every branch taken (no ':else' / ':Completed' exits): every row the view can show, in order."""
    nxt = {}
    for chain in graph["exec"]:
        for a, b in zip(chain, chain[1:]):
            if ":" not in a: nxt.setdefault(a, b.split(":")[0])
    out, cur, seen = [], start, set()
    while cur and cur not in seen:
        seen.add(cur); out.append(cur); cur = nxt.get(cur)
    return out


def content_lines(graph, start):
    """[(section no, header?, string key)] of the W_ValueRow / W_ContentSection Init nodes on the walk from `start`."""
    nodes = {n["id"]: n for n in graph["nodes"]}; sec = 0; out = []
    for i in walk(graph, start):
        n = nodes.get(i, {})
        if n.get("function") != "Init": continue
        if n.get("class") == W_SECTION: sec += 1; continue
        if n.get("class") != W_VALROW: continue
        lab = n["in"]["label"]; src = nodes[lab[1:].split(".")[0]]
        out.append((sec, n["in"]["header"] == "true", src["in"]["key"]))
    return out


def duplicates(lines, lang):
    """Labels that occur twice under one heading of one section, in language lang."""
    li = LANGS.index(lang); scope = None; seen = {}; dup = []
    for sec, head, key in lines:
        if head: scope = (sec, key); continue
        s = (sec, scope if scope and scope[0] == sec else None)
        text = STRINGS[key][li] or STRINGS[key][0]
        if text in seen.setdefault(s, set()): dup.append((key, text))
        seen[s].add(text)
    return dup


class ContentLabels(unittest.TestCase):
    def setUp(self):
        self.g = fn_graph("50_manager_ui.json", "Rebuild Content")
        self.lines = content_lines(self.g, "bsl")   # body values, then the face section

    def test_every_body_value_has_a_row(self):
        keys = [k for _, h, k in self.lines if not h]
        for k, _ in bg.SLIDERS:
            if k not in bg.RETIRED: self.assertIn("Lbl_Sc" + k, keys)
        self.assertIn("Lbl_Breast", keys); self.assertIn("Lbl_Waist", keys)

    def test_body_rows_like_the_body_shape_page(self):
        """The bone-scale rows in SLIDER_ORDER, "Angle" / "Jiggle" each under its group heading."""
        body = [(h, k) for _, h, k in self.lines if k.startswith("Lbl_Sc")]
        want = [(kind == "head", key) for kind, key, _ in bg.content_rows()]
        self.assertEqual(body, want)
        self.assertLess(body.index((True, "Lbl_ScGrpBreast")), body.index((False, "Lbl_ScBreastAngle")))
        self.assertLess(body.index((True, "Lbl_ScGrpGlutes")), body.index((False, "Lbl_ScGlutesAngle")))
        self.assertLess(body.index((False, "Lbl_ScBreastJiggle")), body.index((True, "Lbl_ScGrpGlutes")))

    def test_group_heading_gated_like_its_first_row(self):
        """A heading shows as soon as the saved array reaches one row of its group (the smallest index below it), not only
        when it reaches all of them."""
        rows = bg.content_rows()
        for n, (kind, key, i) in enumerate(rows):
            if kind != "head": continue
            grp = []
            for k2, _, i2 in rows[n + 1:]:
                if k2 == "head": break
                grp.append(i2)
            self.assertEqual(i, min(grp), key)

    def test_labels_unique_per_language(self):
        for lang in LANGS:
            self.assertEqual(duplicates(self.lines, lang), [], lang)

    def test_mod_preset_view_shows_tabs_and_headings(self):
        """Mod fields under different tabs / headings may share a label: their heading lines come along (pending until the next
        row of a value, so an empty tab or heading draws nothing)."""
        g = fn_graph("50_manager_ui.json", "Rebuild Mod Preset Content")
        nodes = {n["id"]: n for n in g["nodes"]}
        heads = [n for n in g["nodes"] if n.get("class") == W_VALROW and n.get("function") == "Init" and n["in"]["header"] == "true"]
        self.assertEqual(sorted(nodes[n["in"]["label"][1:].split(".")[0]]["var"] for n in heads), ["MPHdrSub", "MPHdrTab"])
        sets = {n["var"]: n["in"][n["var"]] for n in g["nodes"] if n.get("kind") == "set" and n["in"].get(n["var"]) == "@bf.Label"}
        self.assertEqual(sorted(sets), ["MPHdrSub", "MPHdrTab"])   # a Tab field -> MPHdrTab, a Header field -> MPHdrSub
        path = walk(g, "bty")   # a value: pending headings, then its own row
        self.assertLess(path.index("bht"), path.index("rw_cr")); self.assertLess(path.index("bhs"), path.index("rw_cr"))


class RagdollCopyScale(unittest.TestCase):
    def test_copy_from_takes_the_component_scale(self):
        """Jodi's height slider scales her mesh component, which the pose snapshot does not carry: Copy From sets the body's world
        scale to the source mesh's, before anything is attached to it."""
        g = fn_graph("28_ragdoll.json", "Copy From")
        nodes = {n["id"]: n for n in g["nodes"]}
        gs = [n for n in g["nodes"] if n.get("function") == "K2_GetComponentScale"]
        ss = [n for n in g["nodes"] if n.get("function") == "SetWorldScale3D"]
        self.assertEqual(len(gs), 1); self.assertEqual(len(ss), 1)
        self.assertEqual(ss[0]["in"]["NewScale"], "@%s.ReturnValue" % gs[0]["id"])
        self.assertEqual(nodes[gs[0]["in"]["self"][1:].split(".")[0]]["var"], "Mesh")   # the source character's mesh
        self.assertEqual(nodes[ss[0]["in"]["self"][1:].split(".")[0]]["var"], "Body")
        path = walk(g, "entry")
        self.assertLess(path.index(ss[0]["id"]), path.index("sb"))


if __name__ == "__main__":
    unittest.main()
