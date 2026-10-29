"""BP_AltUIMove (docs/specs/2026-10-06-move-speed-design.md): asset, functions, manifest."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
import cfg
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


    def test_want_class_knows_walk_mods(self):
        import walk_mods as wm
        g = json.dumps(next(f["graph"] for f in self.bp["functions"] if f["name"] == "Want Class"))
        for s in (wm.MOD_PREFIX, wm.WALK_PREFIX, wm.RUN_PREFIX, wm.BOTH_PREFIX, "LoadAsset_Blocking", "MoveRunLost", "MoveIdleLost", "ModWalkLoop", "ModRunLoop"):
            self.assertIn(s, g, s)
        names = {v["name"] for v in self.bp["variables"]}
        self.assertLessEqual({"ModClass", "ModFrom", "ModWalkLoop", "ModRunLoop", "MoveRunLost", "MoveIdleLost"}, names)

    def test_style_loop_reads_mod_loops(self):
        g = json.dumps(next(f["graph"] for f in self.bp["functions"] if f["name"] == "Style Loop"))
        self.assertIn("ModWalkLoop", g); self.assertIn("ModRunLoop", g)

    def test_no_tick_cycle(self):
        """Only 'this after Jodi': the engine ticks her CharacterMovement before her already (bTickBeforeOwner); CMC after this
        closed a cycle, the engine broke it at a changing edge and the movement ran before or after her camera update (pistol
        run stutter, Nexus 2026-10-13)."""
        g = next(f["graph"] for f in self.bp["functions"] if f["name"] == "Bind")
        adds = [n for n in g["nodes"] if n.get("function") == "AddTickPrerequisiteActor"]
        self.assertEqual(len(adds), 1); self.assertEqual(adds[0]["in"], {"self": "@me.self", "PrerequisiteActor": "@entry.jodi"})


class MoveOptions(unittest.TestCase):
    def test_rows(self):
        import gen_widgets
        # "reset to default" below the slow motion row: it resets that one too (tester report 2026-10-12)
        self.assertEqual(gen_widgets.OPT_CAT_ROWS["Move"], ["RowMoveOn", "RowWalkSpeed", "RowRunSpeed", "RowWalkStyle", "RowRunStyle", "HintRunMod", "RowIdleStyle", "HintIdleMod", "RowSlowMoOn", "RowSlowMo", "MoveLinks"])
        self.assertIn(("WalkSpeed", "Walk speed"), gen_widgets.OPTION_ROWS); self.assertIn(("RunSpeed", "Run speed"), gen_widgets.OPTION_ROWS)

    def test_reset_includes_slow_motion(self):
        import json
        d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "50_manager_ui.json")))
        mgr = next(a for a in d["assets"] if a["path"].endswith("BP_AltUIManager"))
        g = next(f["graph"] for f in mgr["functions"] if f["name"] == "Reset Move Speeds")
        self.assertTrue(any(n.get("var") == "SlowMoPct" and n.get("kind") == "set" for n in g["nodes"]))

    def test_strings(self):
        from strings import STRINGS, LANGS
        keys = ("OptCat_Move", "Lbl_MoveOn", "Lbl_WalkSpeed", "Lbl_RunSpeed", "Btn_SpeedReset", "Quick_SpeedToggle", "Lbl_WalkStyle", "Lbl_RunStyle", "Lbl_IdleStyle") \
            + tuple("Style_" + k for k, _ in gen_move.WALK_STYLES + gen_move.RUN_STYLES) + tuple("Idle_" + k for k, _ in gen_move.IDLE_STYLES[1:])
        for k in keys: self.assertEqual(len(STRINGS[k]), len(LANGS), k)

    def test_walk_mod_strings(self):
        from strings import STRINGS, LANGS
        for k in ("Hint_RunModPaused", "Hint_IdleModPaused"): self.assertEqual(len(STRINGS[k]), len(LANGS), k)

    def test_walk_mod_chips(self):
        """walk / run mods (docs/specs/2026-10-27-walk-mods-design.md): scanned, chips after the built-in styles, rows and hints in Rebuild Options."""
        import gen_manager_ui
        d = json.load(open(os.path.join(H, "..", "..", "assets", "50_manager_ui.json")))
        mgr = next(a for a in d["assets"] if a["path"].endswith("BP_AltUIManager"))
        names = {f["name"] for f in mgr["functions"]}
        self.assertLessEqual({"Scan Walk Mods", "Add Walk Mod Chips"}, names)
        ro = json.dumps(next(f["graph"] for f in mgr["functions"] if f["name"] == "Rebuild Options Body"))
        self.assertIn("Add Walk Mod Chips", ro)
        ch = json.dumps(next(f["graph"] for f in mgr["functions"] if f["name"] == "Add Walk Mod Chips"))
        for s in ("Set Move Style Rows Visible", "MStyleW", "MStyleR", "MoveRunLost", "MoveIdleLost"): self.assertIn(s, ch, s)
        self.assertIn(("runmodhint", "Hint_RunModPaused"), gen_manager_ui.PANEL_STRINGS)

    def test_walk_mod_rows(self):
        import gen_widgets
        self.assertIn(("runmodhint", "HintRunMod"), gen_widgets.PANEL_TEXTS); self.assertIn(("idlemodhint", "HintIdleMod"), gen_widgets.PANEL_TEXTS)

    def test_settings(self):
        import gen_manager
        rows = {(m, s) for m, s, _, _ in gen_manager.SETTINGS}
        for k in ("MoveOn", "WalkSpeedPct", "RunSpeedPct", "WalkStyle", "RunStyle", "IdleStyle"): self.assertIn((k, k), rows)

    def test_select_move_style_has_idle(self):
        d = json.load(open(os.path.join(H, "..", "..", "assets", "50_manager_ui.json")))
        mgr = next(a for a in d["assets"] if a["path"].endswith("BP_AltUIManager"))
        js = json.dumps(next(f["graph"] for f in mgr["functions"] if f["name"] == "Select Move Style"))
        self.assertIn("MStyleI", js); self.assertIn("IdleStyle", js)
        am = json.dumps(next(f["graph"] for f in mgr["functions"] if f["name"] == "Apply Move"))
        self.assertIn("IdleStyle", am)


class MoveStyles(unittest.TestCase):
    """The style technique with a patched-in style (the shipped list may hold only Normal until sub-project 3)."""
    def patched(self):
        from unittest import mock
        walk = [("Normal", None), ("Limp", gen_move.J + "/Animations/Female_WalkHurt_F")]; run = [("Normal", None), ("Limp", gen_move.J + "/Animations/Female_Run_Hurt")]
        idle = [("Normal", None), ("Afk1", gen_move.J + "/Animations/Appearance/Female_Idle_Afk1")]
        abps = {"%s_%s_%s" % (w, r, i): gen_move.M + "/ABP_AltUIStyle_%s_%s_%s" % (w, r, i) for w, _ in walk for r, _ in run for i, _ in idle if (w, r, i) != ("Normal", "Normal", "Normal")}
        tpl = {"%s_%s" % (w, r): gen_move.M + "/ABP_AltUIIdleTpl_%s_%s" % (w, r) for w, _ in walk for r, _ in run}
        return mock.patch.multiple(gen_move, WALK_STYLES=walk, RUN_STYLES=run, IDLE_STYLES=idle, STYLE_ABPS=abps, TEMPLATE_ABPS=tpl)

    def test_style_abps(self):
        for s in (gen_move.WALK_STYLES, gen_move.RUN_STYLES, gen_move.IDLE_STYLES): self.assertEqual(s[0], ("Normal", None))
        want = {"%s_%s_%s" % (w, r, i) for w, _ in gen_move.WALK_STYLES for r, _ in gen_move.RUN_STYLES for i, _ in gen_move.IDLE_STYLES} - {"Normal_Normal_Normal"}
        self.assertEqual(set(gen_move.STYLE_ABPS), want)
        for k, p in gen_move.STYLE_ABPS.items(): self.assertEqual(p, "/Game/Mod/AltUI/ABP_AltUIStyle_" + k)
        self.assertGreater(len(gen_move.IDLE_STYLES), 1)   # the game's idles are in every build
        for k, _ in gen_move.IDLE_STYLES: self.assertNotIn("_", k)   # "_" separates the axes of a style key

    def test_templates(self):
        import idle_mods
        self.assertEqual(set(gen_move.TEMPLATE_ABPS), {"%s_%s" % (w, r) for w, _ in gen_move.WALK_STYLES for r, _ in gen_move.RUN_STYLES})
        for k, p in gen_move.TEMPLATE_ABPS.items(): self.assertEqual(p, idle_mods.TEMPLATE_DIR + "/" + idle_mods.TEMPLATE_PREFIX + k)
        stubs = [a for a in gen_move.build() if a["type"] == "animsequence_stub"]
        self.assertIn(idle_mods.TEMPLATE_ANIM, [a["path"] for a in stubs])
        tpl = next(a for a in gen_move.build() if a["path"] == gen_move.TEMPLATE_ABPS["Normal_Normal"])
        self.assertEqual(tpl["overrides"], {gen_move.STYLE_NODES["idle"]: idle_mods.TEMPLATE_ANIM})

    def test_assets_before_the_actor(self):
        with self.patched():
            assets = gen_move.build(); types = [a["type"] for a in assets]
            self.assertLess(types.index("animstub"), types.index("animchild")); self.assertLess(max(i for i, t in enumerate(types) if t == "animchild"), [a["path"] for a in assets].index(gen_move.MOVE))
            child = next(a for a in assets if a["path"].endswith("ABP_AltUIStyle_Limp_Normal_Normal"))
            self.assertEqual(child["overrides"], {"AnimGraphNode_SequencePlayer_1": gen_move.J + "/Animations/Female_WalkHurt_F"})
            both = next(a for a in assets if a["path"].endswith("ABP_AltUIStyle_Limp_Limp_Afk1"))
            self.assertEqual(set(both["overrides"]), {"AnimGraphNode_SequencePlayer_1", "AnimGraphNode_SequencePlayer_4", "AnimGraphNode_SequencePlayer_27"})
        stub = next(a for a in gen_move.build() if a["type"] == "animstub")
        self.assertEqual([p["name"] for p in stub["players"]], ["AnimGraphNode_SequencePlayer_1", "AnimGraphNode_SequencePlayer_4", "AnimGraphNode_SequencePlayer_27"])

    def test_nodes_match_the_game(self):
        """The stub's node names must be the loop players of the real Jodi_Anim (the child's cooked CDO addresses them by name)."""
        ja = os.path.join(cfg.path("EXTRACTED", os.path.join(H, "..", "..", "extracted")), "game", "TheKillingAntidote", "Content", "Project", "Character", "Jodi", "Jodi_Anim.uasset")
        if not os.path.exists(ja): self.skipTest("no extracted Jodi_Anim")
        import subprocess
        out = subprocess.run([sys.executable, os.path.join(H, "..", "..", "scripts", "uasset_props.py"), ja], capture_output=True, text=True).stdout
        p = json.loads(out)["Default__Jodi_Anim_C"]["props"]
        self.assertIn("Female_Walk ", p[gen_move.STYLE_NODES["walk"]]["Sequence"]); self.assertIn("Female_Run ", p[gen_move.STYLE_NODES["run"]]["Sequence"])
        self.assertTrue(p[gen_move.STYLE_NODES["walk"]]["bLoopAnimation"])
        self.assertIn("Female_Idle ", p[gen_move.STYLE_NODES["idle"]]["Sequence"]); self.assertTrue(p[gen_move.STYLE_NODES["idle"]]["bLoopAnimation"])


class StyleLookupCase(unittest.TestCase):
    def test_style_keys_compared_ignoring_case(self):
        """An FName keeps the spelling of its first use in the process: in the game the chip name "Hurt" came back as "hurt" from
        Conv_NameToString (the game had used "hurt" before) - a case-sensitive string compare never found the style (AltUI log 2026-10-06)."""
        with MoveStyles.patched(self):
            bp = next(a for a in gen_move.build() if a["path"] == gen_move.MOVE)
        for name in ("Style Class", "Style Key"):
            g = next(f["graph"] for f in bp["functions"] if f["name"] == name)
            cmp = [n["function"] for n in g["nodes"] if n.get("function", "").startswith(("EqualEqual_Str", "EqualEqual_Stri"))]
            self.assertTrue(cmp, name); self.assertEqual(set(cmp), {"EqualEqual_StriStri"}, name)


class WantClass(unittest.TestCase):
    def test_want_class_loads_mod_class_and_falls_back(self):
        import idle_mods
        bp = next(a for a in gen_move.build() if a["path"] == gen_move.MOVE)
        g = next(f["graph"] for f in bp["functions"] if f["name"] == "Want Class"); js = json.dumps(g)
        for v in ("LoadClassAsset_Blocking", "MakeSoftClassPath", idle_mods.MOD_PREFIX, idle_mods.TEMPLATE_PREFIX, "Normal_Normal", "Style Class", "Style Key"):
            self.assertIn(v, js, v)
        apply = next(f["graph"] for f in bp["functions"] if f["name"] == "Apply Style")
        self.assertNotIn("Style Class", json.dumps(apply))   # every tick: only the cached WantClass, no class load


class IdleMods(unittest.TestCase):
    def test_scan_and_chips(self):
        import idle_mods
        d = json.load(open(os.path.join(H, "..", "..", "assets", "50_manager_ui.json")))
        mgr = next(a for a in d["assets"] if a["path"].endswith("BP_AltUIManager"))
        scan = json.dumps(next(f["graph"] for f in mgr["functions"] if f["name"] == "Scan Idle Mods"))
        self.assertIn(idle_mods.MOD_PREFIX, scan); self.assertIn("IdleCaptions", scan)
        ro = json.dumps(next(f["graph"] for f in mgr["functions"] if f["name"] == "Rebuild Options Body"))   # KEEP_SCROLL wrapper: the logic is in the body
        self.assertIn("Add Idle Mod Chips", ro)
        self.assertIn("IdleMods", json.dumps(next(f["graph"] for f in mgr["functions"] if f["name"] == "Add Idle Mod Chips")))
        callers = [f["name"] for f in mgr["functions"] if "Scan Idle Mods" in json.dumps(f["graph"]) and f["name"] != "Scan Idle Mods"]
        self.assertTrue(callers)


class IdlePose(unittest.TestCase):
    def mgr(self):
        d = json.load(open(os.path.join(H, "..", "..", "assets", "50_manager_ui.json")))
        return next(a for a in d["assets"] if a["path"].endswith("BP_AltUIManager"))

    def fn(self, name): return json.dumps(next(f["graph"] for f in self.mgr()["functions"] if f["name"] == name))

    def test_tick_uses_the_games_pose_system_only(self):
        t = self.fn("Idle Pose Tick")
        for v in ("Change Next Action Animation", "Get Weapon In Hand", "Is Crouching", "IsAnyMontagePlaying", "Action Animation Name Current", "Action Animation Name Next", "IdlePoseStill"):
            self.assertIn(v, t, v)
        for v in ("Montage_Play", "PlaySlotAnimation", "SetAnimClass"): self.assertNotIn(v, t, v)
        self.assertIn("Idle Pose Tick", self.fn("Cam Tick"))

    def test_end_clears_the_pose_and_its_props(self):
        e = self.fn("End Idle Pose")
        self.assertIn("Change Next Action Animation", e); self.assertIn("K2_DestroyActor", e); self.assertIn("IdlePoseKnown", e)
        self.assertIn("Stop Action Animation", e)   # like the game's use key: a pose does not end by itself when Jodi wants to move

    def test_idle_pose_is_no_pose_of_the_tab(self):
        """ui-test-94: the running idle pose showed as the active pose of the tab; a tile click ends it first."""
        self.assertIn("IdlePoseOn", self.fn("Rebuild Poses") + self.fn("Rebuild Pose Chips") + json.dumps(self.mgr()))
        pc = json.loads(self.fn("Pose Clicked")); self.assertIn("End Idle Pose", json.dumps(pc))

    def test_options_show_the_idle_pose(self):
        """ui-test-94 round 2: with a pose as idle the options showed 'Normal' as active and no chip could be picked any more. Now a chip
        'Pose: <name>' is the active one, and picking an idle chip clears the idle pose."""
        ro = self.fn("Rebuild Options") + self.fn("Add Idle Mod Chips")
        self.assertIn("MStylePose", ro); self.assertIn("Chip_PosePrefix", ro); self.assertIn("IdlePose", ro)
        sel = json.loads(self.fn("Select Move Style"))
        sets = [n for n in sel["nodes"] if n.get("kind") == "set" and n.get("var") == "IdlePose"]; self.assertTrue(sets)
        self.assertIn("End Idle Pose", json.dumps(sel)); self.assertIn("MStyleP", json.dumps(sel))
        from strings import STRINGS, LANGS
        self.assertEqual(len(STRINGS["Chip_PosePrefix"]), len(LANGS))

    def test_ends_on_move_input_not_on_speed(self):
        """ui-test-94: a pose blocks movement, so Speed 2d stays 0 and the idle pose never ended - Jodi was stuck. The trigger is the
        controller's raw move input (TKA_Controller.Input Move Values, also read while Jodi's input is off)."""
        t = json.loads(self.fn("Idle Pose Tick"))
        self.assertIn("Input Move Values", json.dumps(t))
        for nid in ("keep", "calm", "calm2"):   # the "still running" check must not hang on the speed (st)
            self.assertNotIn("@st.", json.dumps(next(n for n in t["nodes"] if n.get("id") == nid)), nid)

    def test_menu_and_setting(self):
        import gen_manager
        self.assertIn(("IdlePose", "IdlePose"), {(m, s) for m, s, _, _ in gen_manager.SETTINGS})
        self.assertIn("PoseIdle", self.fn("On Pose Context"))
        from strings import STRINGS, LANGS
        for k in ("Menu_PoseIdleSet", "Menu_PoseIdleClear"): self.assertEqual(len(STRINGS[k]), len(LANGS), k)


class WalkModTemplates(unittest.TestCase):
    """walk / run mods (docs/specs/2026-10-27-walk-mods-design.md): three template families over the built-in styles."""
    def test_families(self):
        import walk_mods as wm
        w, r, i = [k for k, _ in gen_move.WALK_STYLES], [k for k, _ in gen_move.RUN_STYLES], [k for k, _ in gen_move.IDLE_STYLES]
        want = {wm.walk_tpl(a, b) for a in r for b in i} | {wm.run_tpl(a, b) for a in w for b in i} | {wm.both_tpl(b) for b in i}
        self.assertEqual(set(gen_move.WALKMOD_TEMPLATES), want)
        self.assertEqual(len(want), len(r) * len(i) + len(w) * len(i) + len(i))

    def test_overrides(self):
        import walk_mods as wm
        n = gen_move.STYLE_NODES
        _, ov = gen_move.WALKMOD_TEMPLATES[wm.walk_tpl("Normal", "Normal")]
        self.assertEqual(ov, {n["walk"]: wm.TEMPLATE_WALK})
        _, ov = gen_move.WALKMOD_TEMPLATES[wm.run_tpl("Normal", "Afk1")]
        self.assertEqual(ov, {n["run"]: wm.TEMPLATE_RUN, n["idle"]: dict(gen_move.IDLE_STYLES)["Afk1"]})
        _, ov = gen_move.WALKMOD_TEMPLATES[wm.both_tpl("Normal")]
        self.assertEqual(ov, {n["walk"]: wm.TEMPLATE_WALK, n["run"]: wm.TEMPLATE_RUN})

    def test_assets(self):
        import walk_mods as wm
        paths = {a["path"] for a in gen_move.style_assets()}
        self.assertLessEqual({wm.TEMPLATE_WALK, wm.TEMPLATE_RUN} | {p for p, _ in gen_move.WALKMOD_TEMPLATES.values()}, paths)
