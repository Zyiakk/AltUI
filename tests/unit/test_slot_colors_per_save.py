"""Slot colours per save (spec docs/specs/2026-10-11-kleidungsfarben-pro-spielstand.md): they travel as AltUI#<piece>#<slot>
entries in the game's Clothes Colors map, which the game saves with TKAPlayer, every story save and Level_<n>_End."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def fn_graph(name):
    for f in ("30_manager.json", "50_manager_ui.json"):
        for a in json.load(open(os.path.join(ASSETS, f)))["assets"]:
            for entry in a.get("functions", []):
                if entry.get("name") == name and entry.get("graph"):
                    return entry["graph"]
    raise AssertionError("function %s not found" % name)


def calls(g, chain_start="entry"):
    nodes = {n["id"]: n for n in g["nodes"]}
    chain = next(c for c in g["exec"] if c and c[0] == chain_start)
    return [nodes[i].get("function") for i in chain if nodes.get(i, {}).get("kind") == "call_self"]


def chains(g):
    """exec chains without the protocol nodes (Log Line and the level-name / text nodes that feed it)."""
    skip = {n["id"] for n in g["nodes"] if n.get("function") in ("Log Line", "GetCurrentLevelName")}
    return [[i for i in c if i not in skip] for c in g["exec"]]


class PerSave(unittest.TestCase):
    def test_level_load_reads_the_saves_colours_first(self):
        self.assertEqual(calls(fn_graph("Apply Saved Colors"))[:3], ["Load Save Slot Colors", "Note Worn Game Colors", "Apply All Item Colors"])

    def test_save_settings_syncs_into_the_save_first(self):
        self.assertEqual(calls(fn_graph("Save Settings"))[0], "Sync Save Slot Colors")

    def test_sync_only_after_load_and_on_the_players_figure(self):
        g = fn_graph("Sync Save Slot Colors"); nodes = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(nodes["ok"]["in"], {"A": "@wip.yes", "B": "@gld.SlotColorsLoaded"})
        self.assertIn(["entry", "bok", "sc0", "keys", "sk", "fk"], chains(g))
        self.assertIn(["fo:Completed", "bch", "swn", "cdt"], chains(g))   # a change writes TKAPlayer at once (Save Worn)
        self.assertEqual(nodes["any"]["in"], {"A": "@gch.SyncChanged", "B": "@gdt.GameColorDirty"})

    def test_a_game_colour_altui_changed_reaches_tkaplayer(self):
        """ui-test-87: a reset in the story save left TKAPlayer (menu figure) pink - only AltUI# changes wrote it."""
        g = fn_graph("Note Game Color")
        self.assertTrue(any(n.get("kind") == "set" and n.get("var") == "GameColorDirty" for n in g["nodes"]))
        g = fn_graph("Note Worn Game Colors")   # a level load is no change
        self.assertFalse(any(n.get("function") == "Note Game Color" for n in g["nodes"]))
        self.assertFalse(any(n.get("var") == "GameColorDirty" for n in g["nodes"]))

    def test_both_directions_use_the_same_prefix(self):
        for name in ("Load Save Slot Colors", "Sync Save Slot Colors"):
            g = fn_graph(name); nodes = {n["id"]: n for n in g["nodes"]}
            self.assertEqual(nodes["sw"]["in"]["InPrefix"], "AltUI#", name)
            self.assertEqual(nodes["rc"]["in"]["Count"], "6", name)

    def test_migration_only_once_and_only_on_the_players_figure(self):
        g = fn_graph("Load Save Slot Colors"); nodes = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(nodes["mig"]["in"], {"A": "@wip.yes", "B": "@nps.ReturnValue"})
        self.assertIn(["entry", "bmig", "ssl", "spt", "sld1", "sv1"], chains(g))

    @unittest.skipUnless(os.environ.get("ALTUI_COLORLOG") == "1", "protocol only with ALTUI_COLORLOG=1")
    def test_protocol(self):
        """ALTUI_COLORLOG=1: AltUI_Log.sav records loads, sync changes, mirror drops and every TKAPlayer write by AltUI."""
        for name, needle in (("Load Save Slot Colors", "colors load "), ("Sync Save Slot Colors", "colors sync"),
                             ("Check Game Color", "colors mirror "), ("Save Worn", "TKAPlayer <- AltUI")):
            g = fn_graph(name)
            self.assertTrue(any(n.get("function") == "Log Line" for n in g["nodes"]), name)
            self.assertIn(needle, json.dumps(g), name)

    def test_a_mirror_change_leaves_the_save_at_once(self):
        self.assertIn("Sync Save Slot Colors", [n.get("function") for n in fn_graph("Check Game Color")["nodes"]])


if __name__ == "__main__":
    unittest.main()
