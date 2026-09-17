"""W_OutfitButton is used for outfits (plus tile: "Save current outfit") and for makeup presets (plus tile caption
passed in by the manager: "Save current appearance"). 2026-09-17: the plus tile ignored the caption and always
showed the outfit text on the Presets page."""
import unittest, os, json, re
H = os.path.dirname(os.path.abspath(__file__)); ASSETS = os.path.join(H, "..", "..", "assets")
REF = re.compile(r"^@([A-Za-z0-9_]+)\.")


def init_graph():
    a = next(a for a in json.load(open(os.path.join(ASSETS, "40_widgets.json")))["assets"] if a["path"].endswith("/W_OutfitButton"))
    return next(f for f in a["functions"] if f["name"] == "Init")["graph"]


def depends_on(nodes, links, start_id, pin):
    """transitive data dependency: does node start_id read `pin` (e.g. 'entry.caption') through its inputs or links?"""
    seen, todo = set(), [start_id]
    while todo:
        i = todo.pop()
        if i in seen: continue
        seen.add(i)
        for v in nodes[i].get("in", {}).values():
            m = REF.match(str(v))
            if v == "@" + pin: return True
            if m: todo.append(m.group(1))
        for src, dst in links:
            if dst.split(".")[0] == i:
                if src == pin: return True
                todo.append(src.split(".")[0])
    return False


class OutfitButtonLabel(unittest.TestCase):
    def test_plus_tile_label_depends_on_caption(self):
        g = init_graph(); nodes = {n["id"]: n for n in g["nodes"]}; links = [(l[0], l[1]) for l in g.get("links", [])]
        # the plus tile is index < 0: the SelectString picking A on that condition decides its label
        neg = next(n for n in g["nodes"] if n.get("function") == "Less_IntInt" and n["in"].get("A") == "@entry.index" and n["in"].get("B") == "0")
        sel = next(n for n in g["nodes"] if n.get("function") == "SelectString" and n["in"].get("bPickA") == "@%s.ReturnValue" % neg["id"])
        a_src = REF.match(sel["in"]["A"]).group(1)
        self.assertTrue(depends_on(nodes, links, a_src, "entry.caption"), "plus tile label must use the caption input (preset page passes its own text)")
        # the normal tile keeps its "Outfit N · k pieces" label
        b_src = REF.match(sel["in"]["B"]).group(1)
        self.assertTrue(depends_on(nodes, links, b_src, "entry.count"))


if __name__ == "__main__": unittest.main()
