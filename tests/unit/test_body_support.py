"""2026-11-09 (Nexus, closing the eyes on the standard body): rows that need a converted body (ABP_BodyScale) are greyed out, not usable
and carry the hint as tooltip while the body is not converted - Body Shape bone sliders, the eye lid rows on the Face tab, the foot IK
switches."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, fn_graph
import gen_widgets as gw, face as fc, strings

M = "/Game/Mod/AltUI"


def by_id(g): return {n["id"]: n for n in g["nodes"]}
def calls(g, f): return [n for n in g["nodes"] if n.get("function") == f]
def targets(g, f): return sorted(n["in"]["self"] for n in calls(g, f))


class PanelRows(unittest.TestCase):
    def test_body_scale_rows_whole_row_and_tooltip_on_stripe(self):
        g = fn_graph(M + "/W_AltUI", "Set Body Scales Enabled")
        rows = [k for k, key in gw.SCALE_ROWS if key not in gw.bg.ALL_BODIES]
        self.assertTrue(rows)
        en = targets(g, "SetIsEnabled"); tip = targets(g, "SetToolTip")
        for k in rows:
            self.assertIn("@c%s_gw.Row%s" % (k, k), en)
            self.assertIn("@c%s_gt.RowBg%s" % (k, k), tip); self.assertIn("@c%s_gt2.RowBg%s" % (k, k), tip)   # cleared / set
        self.assertEqual(len(calls(g, "SetRenderOpacity")), len(rows))

    def test_foot_ik_switches(self):
        g = fn_graph(M + "/W_AltUI", "Set Foot IK Enabled")
        en = targets(g, "SetIsEnabled")
        for k in ("FootIK", "FootContact", "ClothFit"):   # + 2026-11-15 clothes follow the body shape
            self.assertIn("@o%s_gw.Opt%s" % (k, k), en); self.assertIn("@l%s_gw.Lbl%s" % (k, k), en)
        self.assertEqual(len(calls(g, "SetToolTip")), 6)   # one row hint each, cleared or set

    def test_tooltip_only_when_disabled(self):
        g = fn_graph(M + "/W_AltUI", "Set Foot IK Enabled"); ex = g["exec"]
        self.assertIn(["oFootIK_en", "oFootIK_ro", "oFootIK_b"], ex); self.assertIn(["oFootIK_b", "oFootIK_nt"], ex)   # enabled: no tooltip
        self.assertIn(["oFootIK_b:else", "oFootIK_ctt", "oFootIK_stm", "oFootIK_tti", "oFootIK_st"], ex)
        # Clothes follow the body shape (2026-11-16): where it works, as tooltip on a converted body too; not converted: the hint first
        self.assertIn(["oClothFit_b", "oClothFit_ectt", "oClothFit_estm", "oClothFit_etti", "oClothFit_nt"], ex)
        b = by_id(g); self.assertEqual(b["oClothFit_etx"]["in"]["key"], "Tip_ClothFit")
        self.assertEqual(b["oClothFit_dco"]["in"]["key"], "Tip_ConvertedOnly"); self.assertEqual(b["oClothFit_dfu"]["in"]["key"], "Tip_ClothFit")
        self.assertEqual(b["oClothFit_tti"]["in"]["text"], "@oClothFit_dct.ReturnValue")

    def test_text(self):
        self.assertEqual(len(strings.STRINGS["Tip_ConvertedOnly"]), 7); self.assertTrue(all(strings.STRINGS["Tip_ConvertedOnly"]))


class FaceRows(unittest.TestCase):
    def test_row_greys_only_when_marked(self):
        g = fn_graph(M + "/W_FaceRow", "Set Supported"); b = by_id(g)
        self.assertIn("@gnc.ConvertedOnly", b["bnc"]["in"].values())
        self.assertEqual(targets(g, "SetIsEnabled"), ["@cv_gw.Row"])
        self.assertIn("@cv_gt2.Bg", targets(g, "SetToolTip"))

    def test_eye_rows_marked_on_the_face_page(self):
        g = mgr_graph("Rebuild Face Right")
        marked = len(calls(g, "Mark Converted Only")); self.assertEqual(marked, len(fc.ANIM_KEYS))
        self.assertEqual(len(calls(g, "Set Supported")), marked)


class Manager(unittest.TestCase):
    def test_apply_reaches_all_three(self):
        g = mgr_graph("Apply Body Support")
        for f in ("Set Body Scales Enabled", "Set Foot IK Enabled", "Set Supported"): self.assertTrue(calls(g, f), f)

    def test_follows_a_change_of_body_and_a_new_panel(self):
        g = mgr_graph("Apply Body Scales"); self.assertEqual(len(calls(g, "Check Body Support")), 2)   # converted and not
        self.assertTrue(calls(mgr_graph("Open Panel"), "Apply Body Support"))
        c = mgr_graph("Check Body Support"); self.assertTrue(calls(c, "Apply Body Support"))
