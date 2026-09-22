import unittest, os, re
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, "..", "..")
P = os.path.join(W, "pubdocs")
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SCRIPT = re.compile(r"scripts/([A-Za-z0-9_]+\.(?:py|sh))")
# scripts/ files of the public snapshot - a pubdocs text may only send readers to these
PUBLIC = {"pak11_extract.py", "pakio.py", "oodle_kraken.py", "oodle_native.py", "uasset_datatable.py", "uasset_props.py",
          "uasset_pkg.py", "uasset_funcs.py", "savegame_gvas.py", "bodypak.py", "bodypak_abp.py", "altui_names.py",
          "kismet_pp.py", "verify_pak.py", "verify_stubs.py", "bodyscale_groups.py", "bpgen.sh", "cook.sh", "pak.sh",
          "deploy.sh", "ue.sh", "edtest.sh", "build_plugin.sh", "bodypak_dist.sh", "altui_names_dist.sh"}
# dev-only tooling and unreleased features: naming them would point readers at something they do not have
FORBIDDEN = ["clothfix", "weaponpak", "weapon_skins", "pakbuild", "mod_inventory", "mods_archive", "mods_assemble",
             "map_repack", "table_patch", "override_fix", "plan_extract", "game_profile", "knowledge/", "S_WeaponSkin"]


class PubdocsLinks(unittest.TestCase):
    def docs(self):
        return [f for f in sorted(os.listdir(P)) if f.endswith(".md")]

    def test_index_lists_every_document(self):
        index = open(os.path.join(P, "README.md")).read()
        for f in self.docs():
            if f != "README.md":
                self.assertIn(f, index, "not linked from the index: " + f)

    def test_relative_links_resolve(self):
        for f in self.docs():
            for target in LINK.findall(open(os.path.join(P, f)).read()):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path = os.path.normpath(os.path.join(P, target.split("#")[0]))
                self.assertTrue(os.path.exists(path), "%s -> %s" % (f, target))

    def test_only_public_scripts_named(self):
        for f in self.docs():
            for name in SCRIPT.findall(open(os.path.join(P, f)).read()):
                self.assertIn(name, PUBLIC, "%s names a script that is not in the public repo: %s" % (f, name))

    def test_no_dev_only_or_unreleased_topics(self):
        for f in self.docs():
            text = open(os.path.join(P, f)).read()
            for word in FORBIDDEN:
                self.assertNotIn(word, text, "%s mentions %s" % (f, word))


if __name__ == "__main__": unittest.main()
