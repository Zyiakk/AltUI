"""scripts/savegame_gvas.py – GVAS SaveGame files (Saved/SaveGames/*.sav): round trip, typed access, SG_Names creation."""
import unittest, os, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts"))
import savegame_gvas as gv
FX = os.path.join(H, "fixtures", "AltUI.sav")


class RoundTrip(unittest.TestCase):
    def test_fixture_byte_identical(self):
        raw = open(FX, "rb").read(); sg = gv.loads(raw)
        self.assertEqual(sg.class_name, "/Game/Mod/AltUI/SG_AltUI.SG_AltUI_C")
        self.assertEqual([p.name for p in sg.props][:3], ["Favorites", "OnlyVanilla", "GroupLen"])
        self.assertEqual(gv.dumps(sg), raw)

    def test_typed_values(self):
        sg = gv.load(FX)
        self.assertEqual(sg.get("SaveVersion"), 1); self.assertIsInstance(sg.get("OnlyVanilla"), bool)
        self.assertEqual(sg.get("Missing", "x"), "x")
        self.assertIsInstance(sg.get("BodyScales"), bytes)   # Map<Name, Struct>: passed through raw

    def test_edit_and_save(self):
        sg = gv.load(FX); sg.set_int("SaveVersion", 7); d = tempfile.mkdtemp(); p = os.path.join(d, "x.sav"); gv.save(sg, p)
        self.assertEqual(gv.load(p).get("SaveVersion"), 7); self.assertEqual(os.path.getsize(p), os.path.getsize(FX))


class Names(unittest.TestCase):
    def test_new_names_save(self):
        sg = gv.new_names_save()
        self.assertEqual(sg.class_name, "/Game/Mod/AltUI/SG_Names.SG_Names_C"); self.assertEqual(sg.get("SaveVersion"), 1); self.assertEqual(sg.get("Names"), {})
        raw = gv.dumps(sg); self.assertTrue(raw.startswith(b"GVAS")); self.assertEqual(gv.loads(raw).get("Names"), {})

    def test_map_round_trip_unicode_and_many(self):
        sg = gv.new_names_save()
        names = {"item:Jietouwaitao": "Straßenjacke", "mod:Wanba_New_001": "夏日连衣裙 – Лето", "group:Wanba·New": "Wanba Serie"}
        names.update({"item:R%03d" % i: "Name %d" % i for i in range(500)})
        sg.set_map("Names", names); back = gv.loads(gv.dumps(sg))
        self.assertEqual(back.get("Names"), names); self.assertEqual(len(back.get("Names")), 503)

    def test_set_map_replaces(self):
        sg = gv.new_names_save(); sg.set_map("Names", {"a:b": "c"}); sg.set_map("Names", {"d:e": "f"})
        self.assertEqual(gv.loads(gv.dumps(sg)).get("Names"), {"d:e": "f"})


if __name__ == "__main__":
    unittest.main()
