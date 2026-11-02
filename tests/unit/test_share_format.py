"""Share JSON format (internal design notes): the Python side of the contract."""
import json, os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
import share_format as sf


class Format(unittest.TestCase):
    def test_snapshot_schema_is_the_struct(self):
        import gen_manager_ui as ui
        self.assertEqual([n for n, _ in sf.SNAP_SCHEMA], ui.SNAP_FIELDS)

    def test_types_known(self):
        for sch in (sf.SNAP_SCHEMA, sf.MUT_SCHEMA, sf.OUTFIT_SCHEMA, sf.FACE_SCHEMA, sf.BODYP_SCHEMA, sf.MODP_SCHEMA, sf.APP_SCHEMA):
            for n, t in sch: self.assertIn(t, sf.VALUE_TYPES, n)

    def test_encoder_is_json(self):
        doc = {"altui": sf.FORMAT, "version": sf.VERSION, "entries": [sf.sample_look(i) for i in range(3)], "mods": {"M1": 'Mod "One"'}}
        self.assertEqual(json.loads(sf.encode(doc)), doc)

    def test_escapes(self):
        s = 'a"b\\c\nd\te'
        self.assertEqual(json.loads(sf.encode({"s": s})), {"s": s})
        self.assertEqual(sf.esc('a"b'), '"a\\"b"')
        self.assertEqual(json.loads(sf.encode({"s": "\x01x"})), {"s": "x"})   # other control characters dropped

    def test_size_of_fifty_looks(self):
        doc = {"altui": sf.FORMAT, "version": sf.VERSION, "entries": [sf.sample_look(i) for i in range(50)], "mods": {}}
        n = len(sf.encode(doc)); self.assertGreater(n, 100000); self.assertLess(n, 400000)


    def test_part2_schemas_are_struct_members(self):
        import json as j
        sts = {a["path"].rsplit("/", 1)[1]: [m["name"] for m in a.get("members", a.get("fields", []))]
               for a in j.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "30_manager.json")))["assets"] if "members" in a or "fields" in a}
        for st, sch in (("S_Face", sf.FACE_SCHEMA), ("S_BodyPreset", sf.BODYP_SCHEMA), ("S_ModPreset", sf.MODP_SCHEMA)):
            self.assertTrue(set(n for n, _ in sch) <= set(sts[st]), st)
        self.assertEqual(sts["S_ShareAppearance"], ["Name"] + [n for n, _ in sf.APP_SCHEMA])


if __name__ == "__main__":
    unittest.main()
