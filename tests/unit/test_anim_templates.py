"""anim_templates: placeholder imports of a template ABP rewritten, export data untouched (idlepak, walkpak)."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts")); sys.path.insert(0, H)
import anim_templates, walk_mods
from test_idlepak import pkg_bytes, JODI_ANIM
from uasset_pkg import Package
from bodypak import import_name


class Retarget(unittest.TestCase):
    def tpl(self):
        return pkg_bytes("ABP_AltUIWalkRunTpl_Normal_C", "AnimBlueprintGeneratedClass",
                         [(JODI_ANIM, "AnimBlueprintGeneratedClass", "Jodi_Anim_C"), (walk_mods.TEMPLATE_WALK, "AnimSequence", "Female_WalkTemplate"),
                          (walk_mods.TEMPLATE_RUN, "AnimSequence", "Female_RunTemplate")], b"CDO")

    def test_two_placeholders(self):
        ua, ux = self.tpl()
        out = anim_templates.retarget(ua, ux, {walk_mods.TEMPLATE_WALK: ("/Game/Mod/WalkAltUI_X/Female_Walk", "Female_Walk"),
                                               walk_mods.TEMPLATE_RUN: ("/Game/Project/Character/Jodi/Animations/Female_Run", "Female_Run")})
        names = {import_name(i) for i in Package.from_bytes(out, ux).imports}
        self.assertIn("/Game/Mod/WalkAltUI_X/Female_Walk", names); self.assertIn("Female_Walk", names)
        self.assertIn("/Game/Project/Character/Jodi/Animations/Female_Run", names); self.assertIn("Female_Run", names)
        self.assertNotIn(walk_mods.TEMPLATE_WALK, names); self.assertNotIn("Female_WalkTemplate", names)

    def test_missing_placeholder_refused(self):
        ua, ux = self.tpl()
        with self.assertRaises(SystemExit):
            anim_templates.retarget(ua, ux, {"/Game/Mod/AltUI/Female_IdleTemplate": ("/Game/Mod/X/Female_Idle", "Female_Idle")})
