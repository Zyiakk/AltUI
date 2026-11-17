"""2026-11-16: Katsumi's loader, hosted by AltUI's hook, made 2.1 s of every main menu and level start (a blocking load attempt per
installed mod, then the found mods loaded blocking). The hook spawns AltUI's BP_AltUIModLoader instead: file checks in steps, each
found table loaded in the background, its rows spawned as his loader does."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def asset(f, path):
    with open(os.path.join(ASSETS, f)) as fh:
        return next(a for a in json.load(fh)["assets"] if a.get("path") == path)


class ModLoader(unittest.TestCase):
    def test_hook_hosts_ours_not_his(self):
        eg = asset("20_hook.json", "/Game/Project/Classes/TKA_PlayerCameraManager")["event_graph"]; n = {x["id"]: x for x in eg["nodes"]}
        self.assertFalse([x for x in eg["nodes"] if x.get("function") == "LoadClassAsset_Blocking"])
        self.assertEqual(n["mlc"]["kind"], "load_class_async"); self.assertIn("BP_AltUIModLoader", n["mlc"]["in"]["AssetClass"])
        self.assertIn(["bp", "bhs", "tml", "acl"], eg["exec"]); self.assertIn(["mlc:Completed", "mlb", "mls"], eg["exec"])
        self.assertIn("BlueprintToLoad_Struct.uasset", n["hsp"]["in"]["B"])   # only with his pak installed
        self.assertIn(["br2:else", "bmg", "mgts", "mgl0", "acl"], eg["exec"])   # the manager class asked again while AltUI.pak is not mounted

    def test_loader_steps(self):
        eg = asset("60_bploader.json", "/Game/Mod/AltUI/BP_AltUIModLoader")["event_graph"]; n = {x["id"]: x for x in eg["nodes"]}
        self.assertEqual(n["fx"]["function"], "FileExists"); self.assertEqual(n["f3"]["in"]["B"], "/TKA_BlueprintLoader.uasset")
        self.assertEqual(n["na"]["in"]["B"], "AltUI")   # AltUI's own row: the hook spawns AltUI
        self.assertEqual(n["la"]["kind"], "load_asset_async"); self.assertIn(["la:Completed", "ck", "rn2", "fr"], eg["exec"])
        self.assertIn(["fr", "row", "bv", "spw"], eg["exec"]); self.assertNotIn("Owner", n["spw"].get("in", {}))
        self.assertFalse([x for x in eg["nodes"] if x.get("function") in ("LoadAsset_Blocking", "LoadClassAsset_Blocking")])


if __name__ == "__main__":
    unittest.main()
