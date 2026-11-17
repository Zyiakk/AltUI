"""bpdsl: notifies with class and values, montages, animimport entries (BPGenAssets MakeMontage / MakeAnimImport read this JSON)."""
import unittest, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
import bpdsl as b

SEQ_A = "/Game/Mod/X/Seq_A"; SEQ_B = "/Game/Mod/X/Seq_B"


class Notify(unittest.TestCase):
    def test_class_notify_with_values(self):
        n = b.notify(0.4, b.N_SHAKE, values={"Shake Class": b.P_CAMSHAKE_MELEE})
        self.assertEqual(n, {"time": 0.4, "class": b.N_SHAKE, "values": {"Shake Class": b.P_CAMSHAKE_MELEE}})

    def test_notify_state_has_duration(self):
        n = b.notify(0.633, b.N_COMBO, duration=0.234, values={"Index": 1}, track=1)
        self.assertEqual(n, {"time": 0.633, "class": b.N_COMBO, "duration": 0.234, "values": {"Index": 1}, "track": 1})

    def test_name_only_notify(self):
        self.assertEqual(b.notify(0.1, name="Footstep"), {"time": 0.1, "name": "Footstep"})

    def test_refuses_what_bpgen_would_drop(self):
        with self.assertRaises(ValueError): b.notify(0.1)                                   # neither class nor name
        with self.assertRaises(ValueError): b.notify(-0.1, b.N_SHAKE)                        # before the start
        with self.assertRaises(ValueError): b.notify(0.1, b.N_COMBO, duration=0)             # empty window
        with self.assertRaises(ValueError): b.notify(0.1, name="Footstep", values={"x": 1})  # values without an object to hold them
        with self.assertRaises(ValueError): b.notify(0.1, b.N_VOICE, values={"Voice Name": None})
        with self.assertRaises(ValueError): b.notify(0.1, b.N_VOICE, values={"Voice Name": ["Grunt"]})

    def test_game_paths(self):
        self.assertEqual(b.N_MELEE, "/Game/Project/Classes/Notify/MeleeAttack_NotifyState")
        self.assertEqual(b.N_COMBO, "/Game/Project/Classes/Notify/ComboAttack_NotifyState")
        self.assertEqual(b.N_SHAKE, "/Game/Project/Classes/Notify/Shake_Notify")
        self.assertEqual(b.N_VOICE, "/Game/Project/Classes/Notify/Voice_Notify")
        self.assertEqual(b.N_CHAREVENT, "/Game/Project/Classes/Notify/CharacterEvent_Notify")
        self.assertEqual(b.E_PLAYSOUND, "/Script/Engine.AnimNotify_PlaySound")
        self.assertEqual(b.P_WHIP, "/Game/Project/Sounds/Weapons/Weapon_Whip")
        self.assertEqual(b.P_CAMSHAKE_MELEE, "/Game/Project/Classes/Camera/CameraShake_MeleeAttack")
        self.assertEqual(b.SK_FEMALE, "/Game/Project/Character/Jodi/Body/Female_Skeleton")


class Montage(unittest.TestCase):
    def combo(self, **kw):
        args = dict(path="/Game/Mod/X/AM_T", skeleton=b.SK_FEMALE, slot="MeleeAttack",
                    segments=[b.segment(SEQ_A, length=1.5), b.segment(SEQ_B, start=0.2, length=1.0)],
                    sections=[b.section("Default", 0, next="Second"), b.section("Second", 1.5)],
                    notifies=[b.notify(0.6, b.N_COMBO, duration=0.25, values={"Index": 1}), b.notify(0.4, b.N_SHAKE, values={"Shake Class": b.P_CAMSHAKE_MELEE})])
        args.update(kw); return b.montage(**args)

    def test_shape(self):
        m = self.combo(blend_in=0.2, blend_out=0.3)
        self.assertEqual(m["type"], "montage"); self.assertEqual(m["path"], "/Game/Mod/X/AM_T"); self.assertEqual(m["skeleton"], b.SK_FEMALE)
        self.assertEqual(m["slot"], "MeleeAttack")
        self.assertEqual(m["segments"], [{"anim": SEQ_A, "start": 0.0, "length": 1.5, "rate": 1.0}, {"anim": SEQ_B, "start": 0.2, "length": 1.0, "rate": 1.0}])
        self.assertEqual(m["sections"], [{"name": "Default", "time": 0.0, "next": "Second"}, {"name": "Second", "time": 1.5}])
        self.assertEqual(len(m["notifies"]), 2); self.assertEqual(m["blend_in"], 0.2); self.assertEqual(m["blend_out"], 0.3)
        self.assertNotIn("blend_out_trigger", m); self.assertNotIn("auto_blend_out", m)   # engine defaults stay unwritten

    def test_segment_without_length_takes_the_rest(self):
        self.assertEqual(b.segment(SEQ_A), {"anim": SEQ_A, "start": 0.0, "rate": 1.0})

    def test_default_section(self):
        self.assertEqual(self.combo(sections=())["sections"], [{"name": "Default", "time": 0.0}])

    def test_section_rules(self):
        with self.assertRaises(ValueError): b.section("", 0)                                                                    # empty name
        with self.assertRaises(ValueError): self.combo(sections=[b.section("Second", 0.5)])                                   # none at 0
        with self.assertRaises(ValueError): self.combo(sections=[b.section("Default", 0), b.section("Default", 1.0)])         # twice
        with self.assertRaises(ValueError): self.combo(sections=[b.section("Default", 0), b.section("B", 1.0), b.section("A", 0.5)])   # out of order
        with self.assertRaises(ValueError): self.combo(sections=[b.section("Default", 0, next="Third")])                     # unknown next
        with self.assertRaises(ValueError): self.combo(sections=[b.section("Default", 0), b.section("Late", 2.5)])           # past the end (1.5 + 1.0)

    def test_times_inside_the_montage(self):
        with self.assertRaises(ValueError): self.combo(notifies=[b.notify(2.6, b.N_SHAKE)])
        with self.assertRaises(ValueError): self.combo(notifies=[b.notify(2.4, b.N_COMBO, duration=0.2)])
        self.combo(notifies=[b.notify(2.3, b.N_COMBO, duration=0.2)])   # ends at 2.5 = the end

    def test_segment_rules(self):
        with self.assertRaises(ValueError): self.combo(segments=[])
        with self.assertRaises(ValueError): b.segment(SEQ_A, start=-0.1)
        with self.assertRaises(ValueError): b.segment(SEQ_A, length=0)
        with self.assertRaises(ValueError): b.segment(SEQ_A, rate=0)
        with self.assertRaises(ValueError): self.combo(slot="")

    def test_legacy_name_lists_only_in_animimport(self):
        with self.assertRaises(ValueError): self.combo(notifies=[["Footstep", 0.1]])

    def test_rate_shortens_the_montage(self):
        m = b.montage("/Game/Mod/X/AM_R", b.SK_FEMALE, "MeleeAttack", [b.segment(SEQ_A, length=2.0, rate=2.0)], notifies=[b.notify(0.9, name="Hit")])
        with self.assertRaises(ValueError): b.montage("/Game/Mod/X/AM_R", b.SK_FEMALE, "MeleeAttack", [b.segment(SEQ_A, length=2.0, rate=2.0)], notifies=[b.notify(1.1, name="Hit")])
        self.assertEqual(m["segments"][0]["rate"], 2.0)


class AnimImport(unittest.TestCase):
    def test_entry(self):
        e = b.animimport("/Game/Mod/X/Seq", b.SK_FEMALE, "seq.fbx", fbx_sha1="abc", curves={"No Montage": [[0, 1], [1, 0]]},
                         notifies=[["Footstep", 0.2], b.notify(0.4, b.N_MELEE, duration=0.1, values={"DamageScale": 2.0})])
        self.assertEqual(e, {"type": "animimport", "path": "/Game/Mod/X/Seq", "skeleton": b.SK_FEMALE, "fbx": "seq.fbx", "fbx_sha1": "abc",
                             "curves": {"No Montage": [[0, 1], [1, 0]]}, "markers": [],
                             "notifies": [["Footstep", 0.2], {"time": 0.4, "class": b.N_MELEE, "duration": 0.1, "values": {"DamageScale": 2.0}}]})

    def test_bad_notify_refused(self):
        with self.assertRaises(ValueError): b.animimport("/Game/Mod/X/Seq", b.SK_FEMALE, "seq.fbx", notifies=["Footstep"])


class ObjectStub(unittest.TestCase):
    def test_shape(self):
        self.assertEqual(b.object_stub(b.P_WHIP, "/Script/Engine.SoundCue"), {"type": "object_stub", "path": b.P_WHIP, "class": "/Script/Engine.SoundCue"})


if __name__ == "__main__":
    unittest.main()
