"""BP_AltUIMove (docs/specs/2026-10-06-move-speed-design.md): asset, functions, manifest."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
import gen_move


class MoveAsset(unittest.TestCase):
    def setUp(self): self.bp = next(a for a in gen_move.build() if a["path"] == gen_move.MOVE)

    def test_functions(self):
        names = {f["name"] for f in self.bp["functions"]}
        self.assertLessEqual({"Bind", "Set Speeds", "Target Factor", "Rate Target", "Apply", "Run Fix", "Check Run Key"}, names)

    def test_pure_helpers(self):
        pure = {f["name"] for f in self.bp["functions"] if f.get("pure")}
        self.assertEqual(pure & {"Target Factor", "Rate Target"}, {"Target Factor", "Rate Target"})

    def test_manifest(self):
        lines = open(os.path.join(H, "..", "..", "assets", "manifest.txt")).read().split()
        self.assertIn("29_move.json", lines); self.assertLess(lines.index("28_ragdoll.json"), lines.index("29_move.json"))

    def test_tick_writes_speed_and_rate(self):
        js = json.dumps(self.bp)
        for v in ("WasInputKeyJustPressed", "GetActionMappingByName", "Wanna Running", "Change Wanna Run", "MaxWalkSpeed", "GlobalAnimRateScale", "AddTickPrerequisiteActor", "RemoveTickPrerequisiteActor", "IsAnyMontagePlaying"):
            self.assertIn(v, js, v)


class MoveOptions(unittest.TestCase):
    def test_rows(self):
        import gen_widgets
        self.assertEqual(gen_widgets.OPT_CAT_ROWS["Move"], ["RowMoveOn", "RowWalkSpeed", "RowRunSpeed", "MoveLinks", "RowWalkStyle", "RowRunStyle"])
        self.assertIn(("WalkSpeed", "Walk speed"), gen_widgets.OPTION_ROWS); self.assertIn(("RunSpeed", "Run speed"), gen_widgets.OPTION_ROWS)

    def test_strings(self):
        from strings import STRINGS, LANGS
        for k in ("OptCat_Move", "Lbl_MoveOn", "Lbl_WalkSpeed", "Lbl_RunSpeed", "Btn_SpeedReset", "Quick_SpeedToggle", "Lbl_WalkStyle", "Lbl_RunStyle") + tuple("Style_" + k for k, _ in gen_move.WALK_STYLES + gen_move.RUN_STYLES):
            self.assertEqual(len(STRINGS[k]), len(LANGS), k)

    def test_settings(self):
        import gen_manager
        rows = {(m, s) for m, s, _, _ in gen_manager.SETTINGS}
        for k in ("MoveOn", "WalkSpeedPct", "RunSpeedPct", "WalkStyle", "RunStyle"): self.assertIn((k, k), rows)


class MoveStyles(unittest.TestCase):
    """The style technique with a patched-in style (the shipped list may hold only Normal until sub-project 3)."""
    def patched(self):
        from unittest import mock
        walk = [("Normal", None), ("Limp", gen_move.J + "/Animations/Female_WalkHurt_F")]; run = [("Normal", None), ("Limp", gen_move.J + "/Animations/Female_Run_Hurt")]
        abps = {"%s_%s" % (w, r): gen_move.M + "/ABP_AltUIStyle_%s_%s" % (w, r) for w, _ in walk for r, _ in run if (w, r) != ("Normal", "Normal")}
        return mock.patch.multiple(gen_move, WALK_STYLES=walk, RUN_STYLES=run, STYLE_ABPS=abps)

    def test_style_abps(self):
        self.assertEqual(gen_move.WALK_STYLES[0], ("Normal", None)); self.assertEqual(gen_move.RUN_STYLES[0], ("Normal", None))
        want = {"%s_%s" % (w, r) for w, _ in gen_move.WALK_STYLES for r, _ in gen_move.RUN_STYLES} - {"Normal_Normal"}
        self.assertEqual(set(gen_move.STYLE_ABPS), want)
        for k, p in gen_move.STYLE_ABPS.items(): self.assertEqual(p, "/Game/Mod/AltUI/ABP_AltUIStyle_" + k)

    def test_assets_before_the_actor(self):
        with self.patched():
            assets = gen_move.build(); types = [a["type"] for a in assets]
            self.assertLess(types.index("animstub"), types.index("animchild")); self.assertLess(max(i for i, t in enumerate(types) if t == "animchild"), [a["path"] for a in assets].index(gen_move.MOVE))
            child = next(a for a in assets if a["path"].endswith("ABP_AltUIStyle_Limp_Normal"))
            self.assertEqual(child["overrides"], {"AnimGraphNode_SequencePlayer_1": gen_move.J + "/Animations/Female_WalkHurt_F"})
            both = next(a for a in assets if a["path"].endswith("ABP_AltUIStyle_Limp_Limp"))
            self.assertEqual(set(both["overrides"]), {"AnimGraphNode_SequencePlayer_1", "AnimGraphNode_SequencePlayer_4"})
        stub = next(a for a in gen_move.build() if a["type"] == "animstub")
        self.assertEqual([p["name"] for p in stub["players"]], ["AnimGraphNode_SequencePlayer_1", "AnimGraphNode_SequencePlayer_4"])

    def test_nodes_match_the_game(self):
        """The stub's node names must be the loop players of the real Jodi_Anim (the child's cooked CDO addresses them by name)."""
        ja = os.path.join(H, "..", "..", "extracted", "game", "TheKillingAntidote", "Content", "Project", "Character", "Jodi", "Jodi_Anim.uasset")
        if not os.path.exists(ja): self.skipTest("no extracted Jodi_Anim")
        import subprocess
        out = subprocess.run([sys.executable, os.path.join(H, "..", "..", "scripts", "uasset_props.py"), ja], capture_output=True, text=True).stdout
        p = json.loads(out)["Default__Jodi_Anim_C"]["props"]
        self.assertIn("Female_Walk ", p[gen_move.STYLE_NODES["walk"]]["Sequence"]); self.assertIn("Female_Run ", p[gen_move.STYLE_NODES["run"]]["Sequence"])
        self.assertTrue(p[gen_move.STYLE_NODES["walk"]]["bLoopAnimation"])


class StyleLookupCase(unittest.TestCase):
    def test_style_keys_compared_ignoring_case(self):
        """An FName keeps the spelling of its first use in the process: in the game the chip name "Hurt" came back as "hurt" from
        Conv_NameToString (the game had used "hurt" before) - a case-sensitive string compare never found the style (AltUI log 2026-10-06)."""
        with MoveStyles.patched(self):
            bp = next(a for a in gen_move.build() if a["path"] == gen_move.MOVE)
        g = next(f["graph"] for f in bp["functions"] if f["name"] == "Style Class")
        cmp = [n["function"] for n in g["nodes"] if n.get("function", "").startswith(("EqualEqual_Str", "EqualEqual_Stri"))]
        self.assertTrue(cmp); self.assertEqual(set(cmp), {"EqualEqual_StriStri"})
