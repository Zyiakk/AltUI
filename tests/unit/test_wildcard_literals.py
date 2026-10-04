"""A literal on a wildcard pin of an array / map / set function (Array_Add NewItem, Map_Add Key, ...) is dropped when the wildcard
resolves to the container's type: the node then adds 0 / "" / None. Such values must come from a typed literal node (bpdsl G.lit_int /
lit_str / lit_name / lit_bool / lit_float) or another pin.

2026-10-04: the virtual lists added their entry kinds as "1" / "2" - all came out as 0, so the headings of Options › Quick menu were
drawn as items and the "+" tile of the outfits page showed outfit 1; AltUI_Log's "--- session ---" line never appeared."""
import unittest, os, glob, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")
WILD = {"Array_Add": ["NewItem"], "Array_AddUnique": ["NewItem"], "Array_Contains": ["ItemToFind"], "Array_Find": ["ItemToFind"],
        "Array_RemoveItem": ["Item"], "Array_Insert": ["NewItem"], "Array_Set": ["Item"], "Map_Add": ["Key", "Value"], "Map_Find": ["Key"],
        "Map_Contains": ["Key"], "Map_Remove": ["Key"], "Set_Add": ["NewItem"], "Set_Contains": ["ItemToFind"], "Set_Remove": ["Item"]}


def literal_wildcards(o, where, out):
    if isinstance(o, dict):
        if o.get("kind") == "call" and o.get("function") in WILD:
            for pin in WILD[o["function"]]:
                v = o.get("in", {}).get(pin)
                if v is not None and not str(v).startswith("@"): out.append("%s %s.%s = %r" % (where, o["id"], pin, v))
        name = o.get("name") if isinstance(o.get("name"), str) else where
        for v in o.values(): literal_wildcards(v, name, out)
    elif isinstance(o, list):
        for v in o: literal_wildcards(v, where, out)


class WildcardLiterals(unittest.TestCase):
    def test_no_literal_on_wildcard_pins(self):
        bad = []
        for f in sorted(glob.glob(os.path.join(ASSETS, "*.json"))): literal_wildcards(json.load(open(f)), os.path.basename(f), bad)
        self.assertEqual(bad, [])


if __name__ == "__main__": unittest.main()
