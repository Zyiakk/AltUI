"""Photos with the free cam instead of "as seen" (docs/specs/2026-10-28-free-cam-photo-design.md): Capture Photo keeps a PhotoView
job (Defer Shot), the left click in the free cam takes it from the free cam's pose (Take Shot), Esc / B the front photo (Shot Fallback)."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
ASSETS = os.path.join(H, "..", "..", "assets")
MGR = "/Game/Mod/AltUI/BP_AltUIManager"


def assets(name):
    with open(os.path.join(ASSETS, name)) as f:
        return json.load(f)["assets"]


def mgr_fns():
    return {f["name"]: f for a in assets("50_manager_ui.json") if a.get("path") == MGR for f in a.get("functions", [])}


def node(g, id):
    return next(n for n in g["nodes"] if n["id"] == id)


def calls(g, function):
    return [n for n in g["nodes"] if n.get("function") == function]


def in_exec(g, id):
    return any(id == s.split(":")[0] for chain in g.get("exec", []) for s in chain)


def exec_order(g):
    """Every exec chain flattened, in order (ids without pins)."""
    return [s.split(":")[0] for chain in g.get("exec", []) for s in chain]


class Capture(unittest.TestCase):
    def test_view_photo_is_deferred(self):
        g = mgr_fns()["Capture Photo"]["graph"]
        d = calls(g, "Defer Shot"); self.assertEqual(len(d), 1); self.assertTrue(in_exec(g, d[0]["id"]))
        self.assertEqual(set(d[0]["in"]), {"target", "distance", "rise", "width", "height", "dir", "file"})
        cond = {n.get("var") for n in g["nodes"] if n.get("kind") == "get"}
        self.assertLessEqual({"PhotoView", "CamMode", "PanelOpen", "PhotoOnly", "PhotoFree"}, cond)

    def test_free_branch(self):
        """PhotoFree: the kept pose and angle, no fill light."""
        g = mgr_fns()["Capture Photo"]["graph"]
        got = {n.get("var") for n in g["nodes"] if n.get("kind") == "get"}
        self.assertLessEqual({"ShotLoc", "ShotRot", "ShotFov"}, got)
        li = [n for n in calls(g, "SetIntensity") if n["id"] == "li2"][0]
        sel = node(g, li["in"]["NewIntensity"].lstrip("@").split(".")[0])
        self.assertEqual((sel["function"], sel["in"]["A"]), ("SelectFloat", "0.0"))
        self.assertTrue(any(n.get("kind") == "set" and n.get("var") == "PhotoFree" for n in g["nodes"]), "PhotoFree is not reset")


class Shot(unittest.TestCase):
    def test_defer_keeps_the_job_and_starts_the_free_cam(self):
        g = mgr_fns()["Defer Shot"]["graph"]
        sets = {n.get("var") for n in g["nodes"] if n.get("kind") == "set"}
        self.assertLessEqual({"ShotTarget", "ShotDistance", "ShotRise", "ShotW", "ShotH", "ShotDir", "ShotFile", "ShotKind", "ShotNumber", "ShotFace", "ShotPending", "ShotWidget"}, sets)
        self.assertTrue(in_exec(g, next(n["id"] for n in g["nodes"] if n.get("function") == "Start Free Cam")))
        self.assertTrue(calls(g, "AddToViewport"))

    def test_take_keeps_the_free_cam_until_the_photo_is_written(self):
        """The camera light follows the game camera and the capture renders for frames after the click: the free cam (and the
        light with it) ends only in Finish Photo, the photo uses the free cam's post-process."""
        f = mgr_fns(); g = f["Take Shot"]["graph"]; order = exec_order(g)
        cap = next(n["id"] for n in g["nodes"] if n.get("function") == "Capture Photo")
        tk = next(n["id"] for n in g["nodes"] if n.get("kind") == "set" and n.get("var") == "ShotTaking")
        self.assertLess(order.index(cap), order.index(tk))
        # no Stop Free Cam anywhere after the capture: follow each node's one exec out from the capture to the end
        nxt = {}
        for c in g["exec"]:
            for a, b in zip(c, c[1:]): nxt.setdefault(a, []).append(b.split(":")[0])
        seen, todo = set(), [cap]
        while todo:
            x = todo.pop(); seen.add(x); todo += [y for y in nxt.get(x, []) if y not in seen]
        self.assertFalse({n["id"] for n in g["nodes"] if n.get("function") == "Stop Free Cam"} & seen, "the free cam must not end right after the click")
        sets = {n.get("var") for n in g["nodes"] if n.get("kind") == "set"}
        self.assertLessEqual({"ShotPending", "ShotLoc", "ShotRot", "ShotFov", "ShotPP", "ShotPPW", "PhotoFree", "PhotoKind", "IconNumber", "PhotoFace", "IconFrames"}, sets)
        self.assertTrue(calls(g, "DegTan") and calls(g, "DegAtan"), "the frame's angle is not derived from the free cam's FOV")
        fp = f["Finish Photo"]["graph"]
        self.assertIn(["entry", "btk", "stk", "sse", "ex"], fp["exec"])
        self.assertFalse(calls(fp, "Stop Free Cam"), "Finish Photo must not end the free cam while the button may be held")
        # Free Cam Step ends it once ShotEnd is set and the left button is up
        st = f["Free Cam Step"]["graph"]
        self.assertIn(["entry", "bse", "sse0", "sstp"], st["exec"])
        self.assertTrue(any(n.get("function") == "IsInputKeyDown" and n["in"].get("Key") == "LeftMouseButton" for n in st["nodes"]))
        cp = f["Capture Photo"]["graph"]
        self.assertTrue(any(n.get("kind") == "get" and n.get("var") == "ShotPP" for n in cp["nodes"]))

    def test_fallback_is_a_front_photo(self):
        g = mgr_fns()["Shot Fallback"]["graph"]
        pf = [n for n in g["nodes"] if n.get("kind") == "set" and n.get("var") == "PhotoFree"]
        self.assertEqual(pf[0]["in"]["PhotoFree"], "false")
        self.assertTrue(in_exec(g, next(n["id"] for n in g["nodes"] if n.get("function") == "Capture Photo")))

    def test_stop_free_cam_falls_back_only_when_waiting(self):
        g = mgr_fns()["Stop Free Cam"]["graph"]
        fb = next(n for n in g["nodes"] if n.get("function") == "Shot Fallback")
        self.assertIn(["bsp", fb["id"]], [c[-2:] for c in g["exec"]])
        self.assertEqual(node(g, "bsp")["kind"], "branch")

    def test_frame_size(self):
        f = mgr_fns()["Shot Frame"]
        self.assertTrue(f.get("pure"))
        self.assertEqual([p["name"] for p in f["outputs"]], ["w", "h", "frac"])

    def test_left_click_takes_it(self):
        cam = next(a for a in assets("50_manager_ui.json") if a.get("path") == "/Game/Mod/AltUI/BP_CamInput")
        g = cam["event_graph"]
        self.assertTrue(calls(g, "Take Shot"))
        self.assertTrue(any(n.get("in", {}).get("B") == "LeftMouseButton" for n in g["nodes"]))
        tsh = next(n["id"] for n in g["nodes"] if n.get("function") == "Take Shot")
        self.assertTrue(any(c[0] == "k:Pressed" and tsh in c for c in g["exec"]), "the shot must be taken on the press, not the release")


class Frame(unittest.TestCase):
    def test_widget(self):
        w = next(a for a in assets("40_widgets.json") if a.get("path") == "/Game/Mod/AltUI/W_ShotFrame")
        names = []
        def walk(n):
            names.append(n["name"]); [walk(c) for c in n.get("children", [])]
        walk(w["widget_tree"])
        self.assertLessEqual({"Top", "Left", "Hole", "Right", "Bottom", "Hint"}, set(names))
        self.assertEqual(w["widget_tree"]["props"]["Visibility"], "HitTestInvisible")
        tk = next(f for f in w["functions"] if f["name"] == "Tick")["graph"]
        self.assertTrue(calls(tk, "Shot Frame") and calls(tk, "SetWidthOverride") and calls(tk, "SetHeightOverride"))


class Texts(unittest.TestCase):
    def test_no_as_seen_left(self):
        import strings, strings_fr
        for k in ("Btn_SaveLookView", "Menu_UpdateView"):
            self.assertNotIn("as seen", strings.STRINGS[k][0]); self.assertIn("free cam", strings.STRINGS[k][0])
        # square tiles: short (play test 2026-10-29, "too much text for the tile")
        for k in ("Btn_SavePresetView", "Btn_SaveFaceView", "Btn_SaveModPresetView"):
            self.assertNotIn("as seen", strings.STRINGS[k][0]); self.assertTrue(strings.STRINGS[k][0].endswith("photo free"), k)
            self.assertTrue(strings.STRINGS[k.replace("View", "Front")][0].endswith("photo front"), k)
        self.assertIn("Hint_ShotFrame", strings.STRINGS); self.assertIn("Hint_ShotFrame", strings_fr.FR)


if __name__ == "__main__":
    unittest.main()
