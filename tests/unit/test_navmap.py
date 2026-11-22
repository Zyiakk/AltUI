"""Navigation tab map (spec 2026-11-17 navigation-map): tile / band arithmetic run with bp_eval, the capture and view graphs, the
widget, settings, strings and wiring."""
import unittest, os, sys, json, math
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_options_cats import graph, calls
from strings import STRINGS, LANGS
import strings_fr, navmap as nm, gen_manager as gm, gen_textures, gen_manager_ui as ui
import bp_eval


def g(name): return graph("50_manager_ui.json", name)
def fns(gr): return [n.get("function") for n in gr["nodes"]]
def js(gr): return json.dumps(gr)


class R(bp_eval.Run):
    """bp_eval with the function's inputs (@entry.<name>)."""
    def __init__(self, gr, v, inputs): super().__init__(gr, v); self.inp = inputs
    def pin(self, ref):
        if isinstance(ref, str) and ref.startswith("@entry."): return self.inp[ref[7:]]
        return super().pin(ref)


def pure(name, vars_=None, **inp):
    gr = g(name); r = R(gr, dict(vars_ or {}), inp)
    return {d.split(".", 1)[1]: r.pin("@" + s) for s, d in gr["links"] if d.startswith("return.")}


def band_ref(cur, has, z):
    lo = cur * nm.BAND_CM - nm.BAND_HYST; hi = (cur + 1) * nm.BAND_CM + nm.BAND_HYST
    return cur if has and lo <= z < hi else math.floor(z / nm.BAND_CM)


class Arithmetic(unittest.TestCase):
    def test_band_hysteresis(self):
        for cur, has, z in ((0, False, 10.0), (0, True, 349.0), (0, True, 360.0), (0, True, 449.0), (0, True, 451.0), (1, True, 260.0),
                            (1, True, 240.0), (2, True, -5.0), (-1, True, -460.0), (-1, True, -351.0), (3, False, 1060.0)):
            self.assertEqual(pure("Map Band Next", cur=cur, has=has, z=z)["band"], band_ref(cur, has, z), (cur, has, z))
        self.assertEqual(pure("Map Band Next", cur=0, has=True, z=420.0)["band"], 0)   # within the hysteresis: stays
        self.assertEqual(pure("Map Band Next", cur=0, has=True, z=460.0)["band"], 1)

    def test_key(self):
        self.assertEqual(pure("Map Key", band=nm.OUT_BAND, x=3, y=-2)["key"], "O_3_-2")
        self.assertEqual(pure("Map Key", band=-1, x=0, y=5)["key"], "-1_0_5")

    def test_tile_of(self):
        import numpy as np
        for x, y in ((0.0, 0.0), (3999.0, -1.0), (-4000.0, 4000.0), (-4001.0, 12345.0)):
            r = pure("Map Tile Of", v=np.array([x, y, 0.0]))
            self.assertEqual((r["x"], r["y"]), (math.floor(x / nm.TILE_CM), math.floor(y / nm.TILE_CM)))

    def test_screen_world_round_trip(self):
        v = {"MapCX": 1500.0, "MapCY": -800.0, "MapPx": 256.0, "MapW": float(nm.MAP_W), "MapH": float(nm.MAP_H)}
        s = pure("Map To Screen", v, wx=1500.0, wy=-800.0)
        self.assertAlmostEqual(s["sx"], nm.MAP_W / 2.0); self.assertAlmostEqual(s["sy"], nm.MAP_H / 2.0)   # the centre in the middle
        s = pure("Map To Screen", v, wx=1500.0 + nm.TILE_CM, wy=-800.0 + nm.TILE_CM)
        self.assertAlmostEqual(s["sx"], nm.MAP_W / 2.0 + 256.0); self.assertAlmostEqual(s["sy"], nm.MAP_H / 2.0 - 256.0)   # +Y right, +X up
        for wx, wy in ((0.0, 0.0), (-12000.0, 5555.0)):
            s = pure("Map To Screen", v, wx=wx, wy=wy); w = pure("Map To World", v, sx=s["sx"], sy=s["sy"])
            self.assertAlmostEqual(w["wx"], wx, places=3); self.assertAlmostEqual(w["wy"], wy, places=3)

    def test_pool_holds_min_zoom(self):
        # the map fills the panel: up to ~2000 x 1100 widget units (2560 x 1440, the right half, half the height)
        cols = math.ceil(2000 / nm.PX_MIN) + 1; rows = math.ceil(1100 / nm.PX_MIN) + 1
        self.assertLessEqual(cols * rows, nm.TILE_POOL)


class Capture(unittest.TestCase):
    def test_tile_capture(self):
        r = g("Map Capture Tile"); j = js(r)
        self.assertEqual(fns(r).count("CaptureScene"), 1 + len(nm.STYLES)); self.assertEqual(fns(r).count("ExportRenderTarget"), len(nm.STYLES)); self.assertIn("SCS_SceneDepth", j); self.assertIn("RTF_R32f", j)
        self.assertIn("DrawMaterialToRenderTarget", fns(r)); self.assertIn(nm.M_MAPCOMBINE, j)
        for f in ("CaptureScene", "HideActorComponents", "ExportRenderTarget", "CreateRenderTarget2D", "K2_DestroyActor", "Map_Add", "Map_Remove"): self.assertIn(f, fns(r), f)
        down = [n for n in r["nodes"] if n.get("function") == "MakeRotator"]
        self.assertEqual([(n["in"]["Pitch"], n["in"]["Yaw"], n["in"]["Roll"]) for n in down], [("-90.0", "0.0", "0.0")])
        for s in ('"Orthographic"', '"OrthoWidth": "%s"' % nm.TILE_CM, '"bCaptureEveryFrame": "false"', "/Script/Engine.Character", nm.MAP_EXT, "RTF_RGBA8_SRGB"): self.assertIn(s, j, s)
        for src in nm.STYLES: self.assertIn(src, j)
        self.assertIn(str(nm.CUT_IN), j); self.assertIn(str(nm.CUT_OUT), j)

    def test_styles_own_folders(self):
        """Every tile in every style, each style in its own folder; a style switch only drops the cache (play test 2026-11-19)."""
        r = g("Map Capture Tile"); dirs = [n for n in r["nodes"] if n.get("function") == "Map Dir"]
        self.assertEqual(sorted(n["in"]["style"] for n in dirs), [str(i) for i in range(len(nm.STYLES))])
        d = js(g("Map Dir")); [self.assertIn(k + "/", d) for k in nm.STYLE_DIRS]
        self.assertIn("MapStyle", js(g("Map Tile Tex"))); st = g("Map Style Next")
        self.assertFalse(calls(st, "Map Capture Next")); self.assertTrue(calls(st, "Map Redraw"))
        # MapDone goes only behind the MapOneStyle branch (the session's tiles are not there in the new style)
        bos = [n for n in st["nodes"] if n["id"] == "bos"][0]; self.assertEqual(bos["in"]["Condition"], "@gos.MapOneStyle")
        self.assertTrue(any("bos" in c and "cdn" in c and c.index("cdn") == c.index("bos") + 1 for c in st["exec"])); self.assertTrue(any(c[0] == "bos:else" for c in st["exec"]))

    def test_one_style_only(self):
        """Options > Map "Only take pictures for the active map style" (play test 2026-11-21): each style's picture hangs behind a
        branch "option off or the shown style"; the base colour is still captured for the lit gain."""
        r = g("Map Capture Tile"); nodes = {n["id"]: n for n in r["nodes"]}
        for i in range(len(nm.STYLES)):
            self.assertEqual(nodes["w%d" % i]["function"], "BooleanOR"); self.assertEqual(nodes["is%d" % i]["in"]["B"], str(i))
            self.assertEqual(nodes["bw%d" % i]["in"]["Condition"], "@w%d.ReturnValue" % i)
        ch = [c for c in r["exec"] if "bw0" in c][0]
        self.assertLess(ch.index("bcap"), ch.index("bw0")); self.assertLess(ch.index("bw0"), ch.index("s0ex")); self.assertLess(ch.index("s0ex"), ch.index("bw1"))
        self.assertIn(["bw0:else", "bw1"], r["exec"]); self.assertIn(["bw1:else", "bw2"], r["exec"]); self.assertIn(["bw2:else", "ds"], r["exec"])
        self.assertIn(("MapOneStyle", "bool", None), nm._PERSIST)
        p = g("Poll Map Options"); self.assertIn("@gv.onestyle", js(p)); self.assertIn("MapDone", js(p))

    def test_tile_taken_again_from_another_height(self):
        """Play test 2026-11-21: a tile taken on the stairs (the band changes there) showed the floor below for the whole session.
        Taken counts only while Jodi's feet are within Z_TOL of the height the tile was taken from - outside always."""
        r = g("Map Capture Next"); nodes = {n["id"]: n for n in r["nodes"]}
        for i in range(9):
            self.assertEqual(nodes["fz%d" % i]["in"]["TargetMap"], "@gz%d.MapDoneZ" % i); self.assertEqual(nodes["nz%d" % i]["in"]["B"], str(nm.Z_TOL))
            self.assertEqual(nodes["oz%d" % i]["in"]["B"], "@isout.ReturnValue"); self.assertEqual(nodes["b%d" % i]["in"]["Condition"], "@t%d.ReturnValue" % i)
        t = g("Map Capture Tile"); self.assertIn(["MapDoneZ"], [[n.get("var")] for n in t["nodes"] if n["id"] == "gdz"])
        self.assertTrue(any("adz" in c for c in t["exec"]))

    def test_lit_gain(self):
        """lit = HDR scene colour x a gain per level (mean base / mean lit, M_MapMean read back), saved; no eye adaptation in captures."""
        r = g("Map Capture Tile"); j = js(r)
        self.assertEqual(nm.STYLES[1], "SCS_SceneColorHDR"); self.assertIn("RTF_RGBA16f", j); self.assertIn(nm.M_MAPMEAN, j)
        self.assertNotIn("RTF_RGBA32f", j)   # ReadRenderTargetRawPixel reads 8 bit and 16f only (32f: red, round 2)
        for f in ("ReadRenderTargetRawPixel", "Map_Find", "Save Settings"): self.assertIn(f, fns(r), f)
        self.assertIn("MapLitGain", j); self.assertIn(str(nm.LIT_BOOST), j)
        self.assertIn("MapLitGain", [s[0] for s in gm.SETTINGS])
        mat = open(os.path.join(H, "..", "..", "scripts", "quickmenu", "material.py")).read()
        self.assertIn("clamp(UV + float2(px, 0), lo, hi)", mat); self.assertIn("return clamp(UV, 0.5 / 512, 1 - 0.5 / 512);", mat)   # no lines on tile edges
        self.assertIn("map_mean()", mat); self.assertIn('"Gain"', mat); self.assertIn('"Lit"', mat)

    def test_retake(self):
        """"Retake": the session forgets its tiles, they are taken again and the PNGs overwritten - no other format, no index, no deleting."""
        self.assertEqual(nm.MAP_EXT, ".png"); self.assertIn(nm.MAP_EXT, js(g("Map Tile Tex")))
        r = g("Map Retake"); f = fns(r); self.assertNotIn("DeleteGameInSlot", f)
        for x in ("Map Capture Next", "Map Redraw"): self.assertIn(x, f, x)
        self.assertIn("MapDone", js(r)); self.assertIn(("MapRetake", "Map Retake"), nm.ACTIONS); self.assertIn("Map_Retake", js(g("Map Rebuild Links")))
        self.assertNotIn("MapFiles", js(g("Map Capture Tile"))); self.assertNotIn("MapFiles", [s[0] for s in gm.SETTINGS])

    def test_next_tries_nine(self):
        r = g("Map Capture Next")
        self.assertEqual(sum(1 for n in r["nodes"] if n.get("function") == "Map Capture Tile"), 9)   # once per session (refresh in turn stuttered)
        self.assertEqual(sum(1 for n in r["nodes"] if n.get("function") == "Map_Contains"), 9)

    def test_tick(self):
        r = g("Map Tick"); j = js(r)
        self.assertTrue(calls(r, "Map Capture Next")); self.assertTrue(calls(r, "Map Update Band")); self.assertIn("MapNoRecord", j); self.assertIn(str(nm.CAPTURE_EVERY), j)

    def test_band_sky(self):
        r = g("Map Update Band"); self.assertIn("LineTraceSingle", fns(r)); self.assertIn("Z=%d" % nm.SKY_CM, js(r)); self.assertTrue(calls(r, "Map Band Next"))

    def test_settings(self):
        names = [s[0] for s in gm.SETTINGS]
        self.assertIn("MapNoRecord", names); self.assertIn("MapStyle", names)


class Literals(unittest.TestCase):
    def test_no_dropped_rotator_defaults(self):
        """A rotator pin default "(Pitch=..,Yaw=..,Roll=..)" is not parsed by K2 (only "P= Y= R=" or "p,y,r"): it silently stays 0.
        Only zero rotations may be written that way."""
        import re, glob
        bad = []
        for f in glob.glob(os.path.join(H, "..", "..", "assets", "*.json")):
            for m in re.finditer(r"\(Pitch=([-\d.]+),Yaw=([-\d.]+),Roll=([-\d.]+)\)", open(f).read()):
                if any(float(x) != 0 for x in m.groups()): bad.append((os.path.basename(f), m.group(0)))
        self.assertEqual(bad, [])


class View(unittest.TestCase):
    def test_widget(self):
        w = json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json")))["assets"]
        nav = [a for a in w if a["path"].endswith("/W_NavMap")][0]; t = json.dumps(nav["widget_tree"])
        self.assertEqual(t.count('"Tile'), nm.TILE_POOL); self.assertEqual(t.count('"Mark'), nm.MARK_POOL + 2); self.assertIn("M_MapTile", t)
        names = [f["name"] for f in nav["functions"]]
        for f in ("Place", "Set Tile", "Set Mark", "Hide Range", "OnMouseButtonDown", "OnMouseMove", "OnMouseButtonUp", "OnMouseWheel"): self.assertIn(f, names)
        panel = json.dumps([a for a in w if a["path"].endswith("/W_AltUI")][0]["widget_tree"])
        for wn in ("MapHead", "MapLabel", "MapLinks", '"NavMap"'): self.assertIn(wn, panel)
        self.assertLess(panel.index('"NavMap"'), panel.index('"NavHint"')); self.assertLess(panel.index('"NavHint"'), panel.index('"NavScroll"'))   # map, hint, beds
        self.assertIn('"Size": "(SizeRule=Fill,Value=1)", "HorizontalAlignment": "HAlign_Fill"', panel)   # full width, half the height
        idx = [a["path"] for a in w].index(nav["path"]); self.assertLess(idx, [a["path"] for a in w].index(nm.W_PANEL))

    def test_redraw(self):
        r = g("Map Redraw"); f = fns(r)
        for x in ("Place", "Set Tile", "Set Mark", "Hide Range", "Map Tile Tex", "GetAllActorsOfClass", "Map Kind Of"): self.assertIn(x, f, x)   # followers: Map Kind Of (2026-11-19)
        j = js(r)
        for t in (nm.T_BED, nm.T_DOT, nm.T_ARROW, nm.T_CROSS): self.assertIn(t, j)

    def test_marker_band_has_jodis_margin(self):
        """Play test 2026-11-21: spawned enemies had no dots. A figure's band was floor(z / BAND_CM), Jodi's keeps up to BAND_HYST
        outside - a figure on her floor near a band edge fell out. Shown: z within the shown band plus that margin."""
        gr = g("Map Mark Spot")   # the band part (eqb / bnd) alone: Map To Screen is another function
        ok = lambda z, band=0, pin="eqb": R(gr, {"MapShowBand": band}, {"v": [0.0, 0.0, z]}).pin("@%s.ReturnValue" % pin)
        for z, want in ((0.0, True), (-50.0, True), (-99.0, True), (-101.0, False), (349.0, True), (420.0, True), (451.0, False)):
            self.assertEqual(ok(z), want, z)
        self.assertTrue(ok(-3000.0, nm.OUT_BAND, "bnd")); self.assertEqual([n["in"]["B"] for n in gr["nodes"] if n["id"] == "ok"], ["@bnd.ReturnValue"])

    def test_missing_floor_tile_falls_back_to_outside(self):
        """Play test 2026-11-21: under an open roof the map changed to her floor, which had only a few tiles. A missing tile of a
        floor shows the outside tile of the place."""
        r = g("Map Redraw"); nodes = {n["id"]: n for n in r["nodes"]}
        self.assertEqual(nodes["keyo"]["in"]["band"], str(nm.OUT_BAND)); self.assertEqual(nodes["texo"]["in"]["key"], "@keyo.key")
        self.assertIn(["btv:else", "bno", "texo", "stto", "btvo", "tpl"], r["exec"]); self.assertEqual(nodes["tst"]["in"]["tex"], "@gtt.MapTileTmp")

    def test_head_line_does_not_move(self):
        """Play test 2026-11-21: the links moved when a caption changed. Changing captions sit in a W_MapSlot with every caption they
        can show; the label is behind a filling gap on the right; fullscreen has "Close" in its own box at the far right."""
        r = g("Map Rebuild Links"); slots = [n for n in r["nodes"] if n.get("function") == "Init" and n.get("class", "").endswith("/W_MapSlot")]
        self.assertEqual(sorted(n["id"] for n in slots), ["losi", "lrsi", "lssi"])
        adds = {n["id"]: n["function"] for n in r["nodes"] if n.get("function") in ("Add Map Link", "Add Map Close")}
        self.assertEqual(adds["lxad"], "Add Map Close"); self.assertEqual(adds["lfad"], "Add Map Link")
        self.assertTrue(any(c[0] == "bfo:else" and "lfad" in c for c in r["exec"]))
        import gen_widgets as gw
        def find(t, name):
            if t.get("name") == name: return t
            for c in t.get("children", []):
                f = find(c, name)
                if f: return f
        panel = [a for a in json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json")))["assets"] if a["path"].endswith("/W_AltUI")][0]
        for head, order in (("MapHead", ["MapLinks", "MapHeadGap", "MapLabel"]), ("MapFullHead", ["MapFullLinks", "MapFullHeadGap", "MapFullLabel", "MapFullClose"])):
            self.assertEqual([c["name"] for c in find(panel["widget_tree"], head)["children"]], order)
        slot = [a for a in json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json")))["assets"] if a["path"].endswith("/W_MapSlot")][0]
        self.assertEqual(find(slot["widget_tree"], "GhostBox")["props"]["HeightOverride"], 1)
        self.assertEqual(find(slot["widget_tree"], "Ghost0")["props"]["Visibility"], "Hidden")

    def test_drag_reads_last_before_setting_it(self):
        """dx / dy are pure: MapLast* must be set after the pan used them (else the step is always 0)."""
        ch = [c for c in g("Map Move")["exec"] if c[0] == "entry"][0]
        self.assertLess(ch.index("scy"), ch.index("slx")); self.assertLess(ch.index("scx"), ch.index("sly"))

    def test_size_from_layout(self):
        self.assertTrue(calls(g("Map Redraw"), "Map Read Size")); self.assertIn("GetLocalSize", fns(g("Map Read Size")))

    def test_tile_tex_no_repeat_probe(self):
        r = g("Map Tile Tex"); f = fns(r)
        self.assertIn("FileExists", f); self.assertIn("ImportFileAsTexture2D", f); self.assertIn("MapMiss", js(r))

    def test_open_from_select_page(self):
        self.assertTrue(calls(g("Select Page"), "Map Open")); self.assertTrue(calls(g("Map Open"), "Map Redraw"))

    def test_actions(self):
        acts = {a: f for a, f, _ in ui.MENU_ACTIONS}
        for a, f in nm.ACTIONS: self.assertEqual(acts.get(a), f)

    def test_teleport(self):
        r = g("Map Teleport"); f = fns(r)
        for x in ("K2_ProjectPointToNavigation", "Nav Teleport", "Nav Follow", "Close Panel", "Set Nav Hint", "K2_TeleportTo", "Stop Free Cam"): self.assertIn(x, f, x)
        self.assertIn("NavOk", js(r))

    def test_tiles_are_exported_opaque(self):
        """2026-11-22: the PNGs had alpha 0 everywhere (an opaque material writes it into the target) - empty in every image viewer.
        M_MapCombine is AlphaComposite with opacity 0 and the target is cleared to black, alpha 1, before each picture."""
        gr = g("Map Capture Tile"); n = {x["id"]: x for x in gr["nodes"]}; ch = [c for c in gr["exec"] if "s0drw" in c][0]
        for i in range(3):
            p = "s%d" % i
            self.assertEqual(n[p + "clr"]["function"], "ClearRenderTarget2D"); self.assertEqual(n[p + "clr"]["in"]["ClearColor"], "(R=0,G=0,B=0,A=1)")
        self.assertLess(ch.index("s0clr"), ch.index("s0drw")); self.assertLess(ch.index("s0drw"), ch.index("s0ex"))
        src = open(os.path.join(H, "..", "..", "scripts", "quickmenu", "material.py")).read()
        body = src[src.index("def map_combine"):src.index("MAPMEAN =")]
        self.assertIn("BLEND_ALPHA_COMPOSITE", body); self.assertIn("MP_OPACITY", body)

    def test_surfaces_dims_lower_floors_as_normals(self):
        """Play test 2026-11-22: from an upper floor the "surfaces" map showed only Jodi's own floor - the lower floors were scaled
        like a colour, their up component fell under 0.5 (= wall = empty ground in M_MapTile). The third picture sets Nrm 1."""
        n = {x["id"]: x for x in g("Map Capture Tile")["nodes"]}
        self.assertEqual([n["s%dpn" % i]["in"]["Value"] for i in range(3)], ["0.0", "0.0", "1.0"]); self.assertEqual(n["s2pn"]["in"]["ParameterName"], "Nrm")
        src = open(os.path.join(H, "..", "..", "scripts", "quickmenu", "material.py")).read(); code = src[src.index('MAPCOMB_CODE = """'):src.index("def map_combine")]
        self.assertIn("0.5 + (cc - 0.5) * lerp(1, 0.35, lowf)", code); self.assertIn("lerp(dim, nrm, Nrm)", code)
        up = lambda b, low: 0.5 + (b - 0.5) * (0.35 if low else 1.0); shade = lambda b: 0.12 + 0.88 * max(0.0, min(1.0, b * 2 - 1))   # M_MapTile
        self.assertAlmostEqual(shade(up(1.0, False)), 1.0); self.assertAlmostEqual(shade(up(1.0, True)), 0.428, places=3)   # a lower floor: grey, not gone
        self.assertAlmostEqual(shade(up(0.5, True)), 0.12)   # walls stay dark

    def test_teleport_without_navmesh(self):
        """Play test 2026-11-21: "No walkable spot" on every click in Jodi's office - the level has no navmesh. When Jodi's own place
        is on none either, the floor under the click comes from a line straight down (flat enough, not starting inside something);
        with a navmesh a click off it stays the hint."""
        r = g("Map Teleport"); nodes = {n["id"]: n for n in r["nodes"]}
        self.assertEqual(nodes["pjj"]["in"]["Point"], "@jf0.feet"); self.assertEqual(nodes["ftr"]["function"], "LineTraceSingle")
        self.assertIn(["bjn:else", "ftr", "bfl", "sps2", "sfc"], r["exec"]); self.assertIn(["bfl:else", "sh"], r["exec"])
        self.assertTrue(any(c[:3] == ["bpj:else", "bjn", "sh"] for c in r["exec"]))
        self.assertEqual(nodes["sps1"]["in"]["MapSpot"], "@pj.ProjectedLocation"); self.assertEqual(nodes["sps2"]["in"]["MapSpot"], "@fbh.ImpactPoint")
        self.assertEqual(nodes["dst"]["in"]["A"], "@gsp.MapSpot"); self.assertEqual(nodes["flat"]["in"]["B"], "0.7")
        self.assertNotIn("@pj.ProjectedLocation", json.dumps([n for n in r["nodes"] if n["id"] != "sps1"]))

    def test_strings(self):
        keys = set()
        for fname in ("Map Show Label", "Map Rebuild Links", "Map Teleport"):
            keys |= {n["in"]["key"] for n in g(fname)["nodes"] if n.get("function") == "T"}
        self.assertTrue({"Map_Floor", "Map_NoSpot", "Map_RecOn", "Map_StyleFlat"} <= keys)
        for k in keys: self.assertEqual(len(STRINGS[k]), len(LANGS), k)
        for k in keys - {"Nav_Go"}: self.assertIn(k, strings_fr.FR, k)

    def test_textures(self):
        paths = [a["path"] for a in gen_textures.build(os.path.join(H, "..", "..", "assets"))]
        for t in (nm.T_BED, nm.T_DOT, nm.T_ARROW, nm.T_CROSS): self.assertIn(t, paths)


if __name__ == "__main__":
    unittest.main()


class OffAndMinimap(unittest.TestCase):
    """Options > Map (play test 2026-11-17 wish): the map off costs nothing; a minimap in a chosen corner, size, margin, zoom."""
    def test_off_stops_everything(self):
        for name in ("Map Tick", "Map Poll", "Map Open", "Mini Tick"): self.assertIn("MapOff", js(g(name)), name)
        t = g("Map Tick"); ch = [c for c in t["exec"] if c[0] == "entry"][0]
        self.assertEqual(ch[:2], ["entry", "bof"])   # first thing: off -> nothing
        self.assertTrue(calls(g("Map Open"), "Set Map Shown"))

    def test_settings(self):
        names = {s[0] for s in gm.SETTINGS}
        for k in ("MapOff", "MiniOn", "MiniCorner", "MiniSize", "MiniMargin", "MiniZoom"): self.assertIn(k, names)

    def test_options_category(self):
        import gen_widgets as gw
        self.assertIn("Map", gw.OPT_CATS)
        self.assertEqual(gw.OPT_CAT_ROWS["Map"], ["RowMapOn", "HintMapOn", "RowMapLegend", "RowMapOneStyle", "HintMapOneStyle", "RowMiniOn", "RowMiniCorner", "RowMiniShape", "RowMiniSize", "RowMiniMargin", "RowMiniZoom"])
        self.assertTrue(calls(g("Rebuild Options Body"), "Rebuild Map Options"))
        self.assertTrue(calls(g("Select SubTab"), "Select Mini Corner")); self.assertIn("MiniCorner", js(g("Select SubTab")))
        r = g("Rebuild Map Options"); self.assertEqual(sum(1 for n in r["nodes"] if n.get("function") == "Add MiniCorner Chip"), 4)
        p = g("Poll Map Options"); self.assertIn("Save Settings Soon", fns(p)); self.assertIn("Range Value", fns(p))

    def test_minimap(self):
        t = g("Mini Tick"); f = fns(t)
        for x in ("AddToViewport", "SetPositionInViewport", "SetDesiredSizeInViewport", "Turn", "Layout", "Map Draw Mini", "GetCameraRotation"): self.assertIn(x, f, x)
        self.assertIn("PanelOpen", js(t))   # hidden while the panel (with the big map) is open ...
        self.assertIn('"B": "Options"', js(t)); self.assertIn('"B": "Map"', js(t))   # ... except on Options > Map
        self.assertLess(nm.MINI_Z, 100)   # behind the panel
        d = g("Map Draw Mini"); self.assertTrue(calls(d, "Map Redraw")); self.assertIn("MapSvView", js(d))
        rd = g("Map Redraw"); self.assertIn("MapMini", js(rd))
