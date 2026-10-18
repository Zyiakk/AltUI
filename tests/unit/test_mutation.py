"""2026-10-18 (spec 2026-10-18-mutation-look-design): the story's mutation look worn in parts - colour and glow sliders,
veins and eyes switches, list entry "Mutation" on the appearance page, part of the look (snapshot, followers, ragdolls)."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, fn_graph, asset
import mutation as mutn

MGR = "/Game/Mod/AltUI/BP_AltUIManager"
FOL = "/Game/Mod/AltUI/BP_AltUIFollower"


def by_id(g): return {n["id"]: n for n in g["nodes"]}
def calls(g, f): return [n for n in g["nodes"] if n.get("function") == f]
def sets(g, v): return [n for n in g["nodes"] if n.get("kind") == "set" and n.get("var") == v]


def fields(path):
    a = asset(path)
    return [p["name"] for p in a.get("params") or a.get("fields") or a.get("members")]


class Data(unittest.TestCase):
    def test_struct(self):
        self.assertEqual(fields(mutn.S_MUT), ["Color", "Glow", "Veins", "Eyes", "Skin", "Story"])

    def test_appended_last(self):
        self.assertEqual(fields("/Game/Mod/AltUI/S_Snapshot")[-1], "Mutation")
        self.assertEqual(fields("/Game/Mod/AltUI/S_Follower")[-1], "Mutation")

    def test_snapshot_round_trip(self):
        mk = [n for n in mgr_graph("Take Snapshot")["nodes"] if n.get("kind") == "make"][0]
        self.assertEqual(mk["in"]["Mutation"], "@gmu9.Mutation")
        g = mgr_graph("Finish Apply Snapshot"); s = sets(g, "Mutation")
        self.assertTrue(s)
        self.assertTrue(calls(g, "Apply Eye Colors"))   # set before Update Eyes Style / Apply Eye Colors, which put it on

    def test_presets(self):
        # ui-test-126 round 5: the game's appearance presets know no mutation - an old one left it on. AltUI keeps its own per preset
        # (Settings.PresetColors, as the eye / make-up colours): an old preset brings zeros = none.
        self.assertEqual(fields("/Game/Mod/AltUI/S_PresetColors")[-1], "Mutation")
        mk = [n for n in mgr_graph("Store Preset Colors")["nodes"] if n.get("kind") == "make"][0]; self.assertEqual(mk["in"]["Mutation"], "@gmu.Mutation")
        g = mgr_graph("Preset Clicked"); s = sets(g, "Mutation"); self.assertTrue(s); self.assertEqual(s[0]["in"]["Mutation"], "@bpc.Mutation")
        ch = next(c for c in g["exec"] if "aec" in c); self.assertLess(ch.index(s[0]["id"]), ch.index("aec"))   # before Apply Eye Colors (it applies it)

    def test_settings(self):
        sv = json.dumps(mgr_graph("Save Settings")); self.assertIn('"Mutation"', sv)
        self.assertIn('"Mutation"', json.dumps(mgr_graph("Load Settings")))


class Core(unittest.TestCase):
    def test_assets_by_path(self):
        j = json.dumps(mgr_graph("Load Mutation Assets"))
        for _, path, _ in mutn.ASSETS: self.assertIn(path, j)
        self.assertEqual(len(calls(mgr_graph("Load Mutation Assets"), "LoadAsset_Blocking")), len(mutn.ASSETS))
        self.assertTrue([n for n in mgr_graph("Mutate Mesh")["nodes"] if n.get("function") == "Load Mutation Assets"])

    def test_skin_params(self):
        j = json.dumps(mgr_graph("Mutate Mesh"))
        for p in ("MainTex", "NormalTex", "EmissiveTex", "EmissiveColor"): self.assertIn('"ParameterName": "%s"' % p, j)

    def test_colour_drawn_opaque_then_translucent(self):
        g = mgr_graph("Mutate Mesh"); d = calls(g, "K2_DrawTexture")
        self.assertEqual([n["in"]["BlendMode"] for n in d], ["BLEND_Opaque", "BLEND_Translucent"])
        b = by_id(g); self.assertEqual(b["d1"]["in"]["RenderTexture"], "@bselt.AsTexture")
        self.assertEqual(b["bsel"]["in"], {"A": "@bb.Main", "B": "@br.diffusetexture", "bSelectA": "@ghb.MutHasBase"})   # her worn skin; the row only without a mesh
        self.assertEqual(by_id(g)["col"]["in"]["A"], "@bm.Color")
        self.assertTrue(calls(g, "CreateRenderTarget2D")); self.assertTrue(calls(g, "EndDrawCanvasToRenderTarget"))

    def test_glow_strength(self):
        b = by_id(mgr_graph("Mutate Mesh")); self.assertEqual(b["gr"]["in"]["B"], str(mutn.GLOW_RED)); self.assertEqual(b["ec"]["in"]["R"], "@gr.ReturnValue")

    def test_only_skin_materials(self):
        # ui-test-126 round 1: MainTex is on the lashes and eyes (ShaderPrincipled) too - they got the skin texture, even at 0.
        # A skin material is one that samples MakeupTex (as in Set Makeup Tex On).
        b = by_id(mgr_graph("Mutate Mesh")); self.assertEqual(b["agtp"]["in"]["ParameterName"], "MakeupTex"); self.assertEqual(b["bgtp"]["in"]["ParameterName"], "MakeupTex")
        self.assertEqual(by_id(fn_graph(FOL, "Apply Skin Tex"))["gtp"]["in"]["ParameterName"], "MakeupTex")

    def test_originals_kept_and_put_back(self):
        # ui-test-126 round 4: old looks - a body mod's skin was overwritten with the skin table's, even without a mutation.
        # Each skin instance's own textures are kept (anything the game puts there, AltUI's own not) and are what it falls back to.
        g = mgr_graph("Mutation Orig Of"); b = by_id(g)
        self.assertEqual(b["mn"]["in"]["bSelectA"], "@isrt.ReturnValue"); self.assertEqual(b["nn"]["in"]["bSelectA"], "@isn.ReturnValue")
        m = by_id(mgr_graph("Mutate Mesh"))
        self.assertEqual(m["sel"]["in"]["B"], "@om.ReturnValue"); self.assertEqual(m["seln"]["in"]["B"], "@on.ReturnValue")
        self.assertEqual(m["om"]["in"]["B"], "@bfb.Main")
        self.assertEqual(by_id(mgr_graph("Apply Jodi Mutation"))["mm"]["in"]["base"], "@gbm.Body Material")

    def test_eyes_off_in_every_apply(self):
        # round 4: a look without eyes left the mutated eye in the slot
        b = by_id(mgr_graph("Apply Jodi Mutation")); self.assertEqual(b["xset"]["in"]["MaterialSlotName"], "Female_Eyes")
        self.assertIn(["bey:else", "xeb", "xmb", "bxok", "xset"], mgr_graph("Apply Jodi Mutation")["exec"])

    def test_no_auto_mips(self):
        # ui-test-126 round 1: drawing a canvas fills mip 0 only - the other mips stayed black, the skin was black from afar
        self.assertEqual(calls(mgr_graph("Mutate Mesh"), "CreateRenderTarget2D")[0]["in"]["bAutoGenerateMipMaps"], "false")

    def test_skin_row_lookup(self):
        g = mgr_graph("Mutate Mesh")
        self.assertTrue([n for n in g["nodes"] if n.get("kind") == "get_row" and n.get("table", "").endswith("/SkinTable")])

    def test_eyes_slot(self):
        b = by_id(mgr_graph("Mutate Mesh")); self.assertEqual(b["mix"]["in"]["MaterialSlotName"], "Female_Eyes")
        self.assertEqual(b["cdm"]["in"]["SourceMaterial"], "@gem.MutEyeMat")


class GlowAndStory(unittest.TestCase):
    """ui-test-126 round 2: Skin_Jodi's static variant has no emissive texture (glow = all over) - glow is AltUI's own layer;
    the story's variant is a switch of its own (true glow, no make-up / scars)."""
    def test_skin_emissive_only_with_the_story_variant(self):
        b = by_id(mgr_graph("Mutate Mesh")); self.assertEqual(b["bst"]["in"]["Condition"], "@bm.Story")
        g = mgr_graph("Mutate Mesh"); self.assertIn(["bst", "set", "sec"], g["exec"])   # EmissiveTex / EmissiveColor only behind the story branch

    def test_glow_layer(self):
        g = mgr_graph("Mutation Glow Layer"); b = by_id(g)
        self.assertEqual(b["cdm"]["in"]["SourceMaterial"], mutn.GLOW_MAT)
        self.assertEqual(b["smp"]["in"]["NewMasterBoneComponent"], "@entry.mesh")   # follows bones and morphs
        self.assertEqual(b["gtp"]["in"]["ParameterName"], "MakeupTex")             # only the skin slots glow
        self.assertEqual(b["sst"]["in"]["ParameterName"], "Strength"); self.assertEqual(b["stx"]["in"]["ParameterName"], "GlowTex")
        self.assertTrue(calls(g, "K2_DestroyComponent"))

    def test_jodi_gets_layer_or_story_slot(self):
        g = mgr_graph("Apply Jodi Mutation"); b = by_id(g)
        self.assertEqual(b["ssl"]["in"]["on"], "@bms.Story"); self.assertEqual(b["lgs"]["in"]["bPickA"], "@bms.Story")   # no layer with the story variant
        self.assertTrue(sets(g, "MutGlowComp"))

    def test_story_slot_keeps_the_clothes_mask(self):
        j = json.dumps(mgr_graph("Mutation Story Slot")); self.assertIn('"MaskThreshold"', j)
        self.assertIn('"MaskThreshold"', json.dumps(mgr_graph("Mutation Watch")))
        self.assertIn(("MutStoryMat", mutn.STORY_SKIN, "material"), mutn.ASSETS)

    def test_story_on_sets_everything(self):
        # ui-test-126 round 3: the switch alone only took make-up and scars away - switching it on sets the story's look in full
        b = by_id(mgr_graph("Mutation Row Changed"))
        self.assertEqual(b["son"]["in"], {"A": "@ks.ReturnValue", "B": "@entry.fixed"})
        for k in ("cS", "glS"): self.assertEqual(b[k]["in"]["bPickA"], "@son.ReturnValue"); self.assertEqual(b[k]["in"]["A"], "1.0")
        for k in ("veS", "eyS"): self.assertEqual(b[k]["in"]["B"], "@son.ReturnValue")
        self.assertEqual(b["rlx"]["in"]["B"], "@son.ReturnValue")   # the rows show it

    def test_material_script(self):
        with open(os.path.join(H, "..", "..", "scripts", "quickmenu", "material.py")) as fh: src = fh.read()
        self.assertIn(mutn.GLOW_MAT, src); self.assertIn("BLEND_ADDITIVE", src); self.assertIn("used_with_morph_targets", src)
        with open(os.path.join(H, "..", "..", "scripts", "quickmenu", "material.sh")) as fh: self.assertIn("M_MutGlow", fh.read())


class Jodi(unittest.TestCase):
    def test_apply(self):
        g = mgr_graph("Apply Jodi Mutation"); b = by_id(g)
        self.assertEqual(calls(g, "Mutate Mesh")[0]["in"]["size"], str(mutn.MUT_RT_SIZE))
        self.assertEqual(b["mk"]["in"]["Skin"], "@gsn.Skin Name")   # mixed on her current skin row
        self.assertTrue(sets(g, "MutSkinRT"))

    def test_own_iris_colour_on_the_mutated_eye(self):
        b = by_id(mgr_graph("Apply Jodi Mutation"))
        self.assertEqual(b["smc"]["in"]["ParameterName"], "MainColor"); self.assertEqual(b["sgc"]["in"]["ParameterName"], "EmissiveColor")
        self.assertEqual(b["glw"]["in"]["B"], str(mutn.EYE_GLOW))

    def test_after_every_eye_rebuild_and_skin_change(self):
        self.assertTrue(calls(mgr_graph("Apply Eye Colors"), "Apply Jodi Mutation"))
        self.assertTrue(calls(mgr_graph("Look Clicked"), "Apply Jodi Mutation"))

    def test_watch(self):
        g = mgr_graph("Mutation Watch"); self.assertTrue(calls(g, "Apply Jodi Mutation")); self.assertTrue(calls(g, "Mutation Active"))
        self.assertEqual(by_id(g)["c0"].get("class"), "/Script/Engine.MaterialInstanceDynamic")   # a constant slot 0 = the story's mutation: hands off
        with open(os.path.join(H, "..", "..", "assets", "50_manager_ui.json")) as fh: self.assertIn('"FunctionName": "Mutation Watch"', fh.read())


class Page(unittest.TestCase):
    def test_list_entry_under_skin(self):
        b = by_id(mgr_graph("Rebuild Look Cats"))
        self.assertEqual(b["insm"]["in"]["Index"], "1")   # after "Skin" (0), before "All" goes in front
        self.assertTrue(any(mutn.CAT in json.dumps(n) for n in mgr_graph("Rebuild Look Cats")["nodes"] if n["id"].startswith("mut") or n["id"] == "ismu"))

    def test_rows(self):
        g = mgr_graph("Rebuild Look")
        inits = [n for n in g["nodes"] if n.get("function") == "Init" and n.get("class", "").endswith("W_FaceRow")]
        self.assertEqual([n["in"]["key"] for n in inits], [k for k, _, _ in mutn.ROWS])
        self.assertEqual(len(calls(g, "Set Switch")), len([r for r in mutn.ROWS if not r[2]]))
        self.assertIn('"MutReset"', json.dumps(g)); self.assertTrue(calls(g, "Clear Look Rows"))

    def test_dispatch(self):
        g = mgr_graph("Face Row Changed"); self.assertTrue(calls(g, "Mutation Row Changed"))
        h = mgr_graph("Mutation Row Changed")
        for f in ("Push History", "Apply Jodi Mutation", "Mutation Eyes Off"): self.assertTrue(calls(h, f), f)
        self.assertTrue(calls(mgr_graph("Mutation Eyes Off"), "Update Eyes Style"))
        r = mgr_graph("Mutation Reset"); self.assertTrue(calls(r, "Push History")); self.assertTrue(calls(r, "Save Settings"))

    def test_eyes_off_puts_her_eye_back(self):
        # ui-test-126 round 2: Update Eyes Style only sets parameters while her Eye Material exists - the mutated eye stayed in the
        # slot. As the story's Mutante(false): her Eye Material back into slot Female_Eyes.
        g = mgr_graph("Mutation Eyes Off"); sm = calls(g, "SetMaterialByName")
        self.assertTrue(sm); self.assertEqual(sm[0]["in"]["MaterialSlotName"], "Female_Eyes"); self.assertIn("Eye Material", sm[0]["in"]["Material"])

    def test_switch_row_widget(self):
        w = asset("/Game/Mod/AltUI/W_FaceRow"); names = [f["name"] for f in w["functions"]]
        self.assertIn("Set Switch", names)
        tick = next(f for f in w["functions"] if f["name"] == "Tick")["graph"]
        self.assertEqual(by_id(tick)["nomv"]["in"]["B"], "@gsw.Switch")   # a switch never takes the hidden slider's value

    def test_strings(self):
        import strings
        for key in [c for _, c, _ in mutn.ROWS] + ["Look_Mutation", "Btn_MutReset"]:
            self.assertIn(key, strings.STRINGS); self.assertEqual(len(strings.STRINGS[key]), len(strings.LANGS))


class Copies(unittest.TestCase):
    def test_ragdoll_copy_gets_its_own_target(self):
        mm = calls(mgr_graph("Mutate Copy"), "Mutate Mesh")[0]
        self.assertEqual(mm["in"]["rt"], "None"); self.assertEqual(mm["in"]["size"], str(mutn.MUT_COPY_RT_SIZE))
        self.assertTrue(calls(mgr_graph("Spawn Ragdoll Copy"), "Mutate Copy"))

    def test_follower_record_and_skin_target(self):
        g = mgr_graph("Finish Look Follower")
        self.assertTrue(sets(g, "FolMutation"))
        self.assertTrue([n for n in g["nodes"] if n.get("kind") == "make" and n["in"].get("Mutation") == "@gfmu.FolMutation"])   # a new record
        self.assertTrue(calls(g, "Mutation Skin Tex"))   # a new look for a figure in the world
        sp = mgr_graph("Fol Spawn"); self.assertTrue(calls(sp, "Mutation Skin Tex"))
        self.assertTrue([n for n in sp["nodes"] if n.get("kind") == "set" and n.get("var") == "LookSkinTex"])

    def test_figure_puts_it_back_on_every_apply(self):
        self.assertTrue(calls(fn_graph(FOL, "Apply Look"), "Apply Skin Tex"))
        self.assertIn('"ParameterName": "MainTex"', json.dumps(fn_graph(FOL, "Apply Skin Tex")))

    def test_skin_tex_draws_without_a_mesh(self):
        g = mgr_graph("Mutation Skin Tex"); self.assertEqual(calls(g, "Mutate Mesh")[0]["in"]["mesh"], "None")
        self.assertEqual(by_id(mgr_graph("Mutate Mesh"))["vme"]["in"]["Object"], "@entry.mesh")


if __name__ == "__main__": unittest.main()
