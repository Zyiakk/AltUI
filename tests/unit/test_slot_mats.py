"""Material swap between clothing items, core (spec internal design notes): SlotMats
(<piece>#<slot> -> "<source piece>#<source slot>"), resolution, putting on and taking off."""
import json
import unittest
from tests.unit.test_slot_colors_per_save import fn_graph, calls


def funcs(g):
    return [n.get("function") for n in g["nodes"]]


class SlotMatsCore(unittest.TestCase):
    def test_apply_item_colors_puts_mats_first(self):
        g = fn_graph("Apply Item Colors")
        nodes = {n["id"]: n for n in g["nodes"]}
        self.assertEqual([c for c in calls(g) if c != "Log Line"][0], "Apply Item Mats On")   # Log Line: measuring build (MATLOG)
        aim = next(n for n in g["nodes"] if n.get("function") == "Apply Item Mats On")
        self.assertEqual(nodes[aim["in"]["mats"].lstrip("@").split(".")[0]]["var"], "SlotMats")

    def test_set_slot_mat_uses_set_material(self):
        g = fn_graph("Set Slot Mat On")
        self.assertIn("SetMaterial", funcs(g))
        self.assertIn("Mat Of Slot", funcs(g))

    def test_item_color_slots_probes_swapped_material(self):
        g = fn_graph("Item Color Slots")
        self.assertIn("Mat Of Slot", funcs(g), "a swapped slot is probed with its new material")

    def test_reset_restores_own_material(self):
        g = fn_graph("Restore Slot Mat On")
        self.assertIn("Own Slot Mat", funcs(g))   # the row's override, else the mesh's (TestRowMaterialOverride)
        self.assertIn("SetMaterial", funcs(g))

    def test_mat_of_slot_splits_from_the_end(self):
        g = fn_graph("Mat Of Slot")
        sp = next(n for n in g["nodes"] if n.get("function") == "Split")
        self.assertEqual(sp["in"]["SearchDir"], "FromEnd")

    def test_item_mat_slots_has_no_colour_probe(self):
        g = fn_graph("Item Mat Slots")
        self.assertNotIn("Material Takes Color", funcs(g))
        self.assertNotIn("Contains", funcs(g))   # no FixedColor exception

    def test_set_and_reset_drop_the_slot_cache_and_save(self):
        for name in ("Slot Set Mat", "Slot Reset Mat", "Item Reset Mats"):
            f = funcs(fn_graph(name))
            self.assertIn("Apply Item Colors", f, name)
            self.assertIn("Save Settings", f, name)
            self.assertIn("Map_Remove", f, name)


class SlotMatsPerSave(unittest.TestCase):
    def test_load_colors_calls_load_mats_in_both_branches(self):
        g = fn_graph("Load Save Slot Colors")
        lsm = [n["id"] for n in g["nodes"] if n.get("function") == "Load Save Slot Mats"]
        self.assertEqual(len(lsm), 2)
        for i in lsm:
            self.assertTrue(any(i in c for c in g["exec"]), "Load Save Slot Mats is on an exec chain")

    def test_sync_colors_syncs_mats_before_the_write(self):
        g = fn_graph("Sync Save Slot Colors")
        nodes = {n["id"]: n for n in g["nodes"]}
        chain = next(c for c in g["exec"] if "ssm" in c)
        self.assertEqual(chain[0], "fo:Completed")
        self.assertEqual(nodes[chain[1]].get("function"), "Sync Save Slot Mats")
        self.assertEqual(nodes[chain[3]].get("function"), "Save Worn")

    def test_sync_mats_prefix_and_separator(self):
        g = fn_graph("Sync Save Slot Mats")
        self.assertIn("AltUIMat#", json.dumps(g))
        self.assertTrue(any(n.get("in", {}).get("B") == "=" for n in g["nodes"]), "key = prefix + target#slot + '=' + source")
        self.assertTrue(any(n.get("var") == "SlotMatsLoaded" for n in g["nodes"]))
        self.assertFalse(any(n.get("var") == "SyncChanged" and n.get("in", {}).get("SyncChanged") == "false"
                             for n in g["nodes"]), "the caller owns the SyncChanged reset")

    def test_load_mats_splits_at_equals_from_start_and_clears_caches(self):
        g = fn_graph("Load Save Slot Mats")
        sp = next(n for n in g["nodes"] if n.get("function") == "Split")
        self.assertEqual(sp["in"]["InStr"], "=")
        self.assertEqual(sp["in"]["SearchDir"], "FromStart")
        nodes = {n["id"]: n for n in g["nodes"]}
        cleared = {nodes[n["in"]["TargetMap"].lstrip("@").split(".")[0]]["var"]
                   for n in g["nodes"] if n.get("function") == "Map_Clear"}
        self.assertEqual(cleared, {"SlotMats", "ColorSlotsOf"})
        self.assertIn("Map_Add", funcs(g))


class SlotMatsSnapshot(unittest.TestCase):
    """Task 3: snapshot, undo, looks, keep-items."""

    def test_take_snapshot_carries_slot_mats(self):
        g = fn_graph("Take Snapshot"); nodes = {n["id"]: n for n in g["nodes"]}
        mk = next(n for n in g["nodes"] if n["id"] == "mk")
        self.assertEqual(nodes[mk["in"]["SlotMats"].lstrip("@").split(".")[0]]["var"], "SlotMats")

    def test_snap_struct_has_slot_mats_last(self):
        from tests.unit.test_fol_tab import asset
        members = asset("/Game/Mod/AltUI/S_Snapshot")["members"]
        self.assertEqual(members[-1]["name"], "SlotMats")

    def test_finish_apply_snapshot_order(self):
        g = fn_graph("Finish Apply Snapshot"); b = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(b["wkm"]["function"], "Look Mats"); self.assertEqual(b["wkm"]["in"]["snap"], "@gps.PendingSnap")
        self.assertEqual(b["rdm"]["function"], "Reset Dropped Mats"); self.assertEqual(b["rdm"]["in"]["next"], "@wkm.mats")
        self.assertEqual(b["ssm9"]["in"]["SlotMats"], "@wkm.mats")
        chain = next(c for c in g["exec"] if "wkm" in c)
        self.assertEqual(chain[chain.index("wkm"):chain.index("wkm") + 4], ["wkm", "rdm", "ssm9", "ccs9"])
        self.assertLess(chain.index("ccs9"), chain.index("aicA"))
        self.assertEqual(b["ccs9"]["function"], "Map_Clear")   # the colourable slots depend on the swapped materials
        self.assertEqual(b[b["ccs9"]["in"]["TargetMap"].lstrip("@").split(".")[0]]["var"], "ColorSlotsOf")

    def test_look_mats_merges_like_look_colors(self):
        g = fn_graph("Look Mats"); b = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(b["gpm"]["var"], "PendingMerge")
        self.assertEqual(b["wkm"]["function"], "With Kept Mats")
        self.assertIn(["bm:else", "wkm", "rs", "return"], g["exec"])
        self.assertEqual(b["rs"]["in"]["LcMats"], "@wkm.mats")

    def test_reset_dropped_mats_restores_from_the_end(self):
        g = fn_graph("Reset Dropped Mats")
        self.assertIn("Restore Slot Mat On", funcs(g))
        sp = next(n for n in g["nodes"] if n.get("function") == "Split")
        self.assertEqual(sp["in"]["SearchDir"], "FromEnd")

    def test_with_kept_mats_copies_kept_pieces(self):
        g = fn_graph("With Kept Mats"); b = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(b["s0"]["in"]["KeepMats"], "@entry.next")
        self.assertEqual(b["gk"]["var"], "KeptOn")
        self.assertEqual(b["gsm"]["var"], "SlotMats")

    def test_clean_and_share_filter_slot_mats(self):
        for name, var in (("Clean Snap", "CsMats"), ("Share Look Snap", "ShLkMats")):
            g = fn_graph(name); out = next(n for n in g["nodes"] if n["id"] == "out")
            src = {n["id"]: n for n in g["nodes"]}[out["in"]["SlotMats"].lstrip("@").split(".")[0]]
            self.assertEqual(src["var"], var, name)
            self.assertIn("Map_Add", funcs(g), name)


class SlotMatsOutfitsAndShare(unittest.TestCase):
    """Task 4: outfits (Settings.OutfitMats) and the share JSON."""

    def vars_of(self, g):
        return {n["id"]: n.get("var") for n in g["nodes"] if n.get("var")}

    def test_remember_outfit_colors_writes_outfit_mats(self):
        g = fn_graph("Remember Outfit Colors"); b = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(b[b["mf"]["in"]["TargetMap"].lstrip("@").split(".")[0]]["var"], "SlotMats")
        self.assertEqual(b["madd"]["function"], "Map_Add"); self.assertEqual(b["mrem"]["function"], "Map_Remove")
        for k in ("madd", "mrem"): self.assertEqual(b[b[k]["in"]["TargetMap"].lstrip("@").split(".")[0]]["var"], "OutfitMats")
        self.assertEqual(b["madd"]["in"]["Key"], "@mosk.key", "the outfit key of the material-slot loop")

    def test_outfit_slot_colors_fills_outfit_sm(self):
        g = fn_graph("Outfit Slot Colors"); b = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(b["cpm"]["in"]["OutfitSM"], "@gsm.SlotMats")
        self.assertEqual(b[b["mf"]["in"]["TargetMap"].lstrip("@").split(".")[0]]["var"], "OutfitMats")
        for k in ("madd", "mrem"): self.assertEqual(b[b[k]["in"]["TargetMap"].lstrip("@").split(".")[0]]["var"], "OutfitSM")
        self.assertEqual(b["madd"]["in"]["Key"], "@msk.key")

    def test_on_outfit_clicked_snapshot_carries_outfit_sm(self):
        g = fn_graph("On Outfit Clicked"); b = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(b[b["mk"]["in"]["SlotMats"].lstrip("@").split(".")[0]]["var"], "OutfitSM")

    def test_delete_and_replace_drop_outfit_mats(self):
        for name in ("Delete Outfit In Array", "Replace Outfit With Last"):
            g = fn_graph(name)
            crm = [n for n in g["nodes"] if n.get("function") == "Map_Remove" and self.vars_of(g).get(n["in"]["TargetMap"].lstrip("@").split(".")[0]) == "OutfitMats"]
            self.assertEqual(len(crm), 1, name)

    def test_rekey_moves_outfit_mats(self):
        g = fn_graph("Rekey Outfit Ids"); b = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(b["cOidMats"]["function"], "Map_Clear")
        v = lambda nid, key="TargetMap": b[b[nid]["in"][key].lstrip("@").split(".")[0]]["var"]
        self.assertEqual(v("mck"), "OutfitMats"); self.assertEqual(v("mcv"), "OutfitMats"); self.assertEqual(v("mcrm"), "OutfitMats")
        self.assertEqual(v("mcadd"), "OidMats"); self.assertEqual(v("mcadd2"), "OutfitMats")
        self.assertIn(["mfc2:Completed", "q0f"], [c[c.index("mfc2:Completed"):c.index("mfc2:Completed") + 2] for c in g["exec"] if "mfc2:Completed" in c])

    def test_outfit_struct_and_schema_end_with_slot_mats(self):
        from tests.unit.test_fol_tab import asset
        self.assertEqual([m["name"] for m in asset("/Game/Mod/AltUI/S_ShareOutfit")["members"]], ["Name", "Pieces", "SlotColors", "SlotMats"])
        import share_format as sf
        self.assertEqual(sf.OUTFIT_SCHEMA[-1], ("SlotMats", "map_str")); self.assertEqual(sf.SNAP_SCHEMA[-1], ("SlotMats", "map_str"))

    def test_settings_hold_outfit_mats(self):
        from tests.unit.test_fol_tab import asset
        sg = asset("/Game/Mod/AltUI/SG_AltUI")
        self.assertIn("OutfitMats", [v["name"] for v in sg["variables"]])

    def test_share_outfit_data_exports_outfit_mats(self):
        g = fn_graph("Share Outfit Data"); b = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(b["om"]["var"], "OutfitMats")
        self.assertEqual(b[b["mk"]["in"]["SlotMats"].lstrip("@").split(".")[0]]["var"], "ShFOutfit_SlotMats")

    def test_share_import_puts_outfit_mats_under_the_new_id(self):
        g = fn_graph("Share Import"); b = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(b["ssm"]["in"]["ShImpSM"], "@ob.SlotMats")
        self.assertTrue(any(c[c.index("ssc"):c.index("ssc") + 2] == ["ssc", "ssm"] for c in g["exec"] if "ssc" in c))
        self.assertEqual(b[b["xaom"]["in"]["TargetMap"].lstrip("@").split(".")[0]]["var"], "OutfitMats")
        self.assertEqual(b["xk1"]["in"]["A"], "@oid.key")
        self.assertEqual(b[b["xrs"]["in"]["TargetMap"].lstrip("@").split(".")[0]]["var"], "ShImpSM", "mats of dropped pieces go")

    def test_look_import_goes_through_clean_snap(self):
        g = fn_graph("Share Import"); self.assertIn("Clean Snap", [n.get("function") for n in g["nodes"]])

    def test_look_roundtrip_with_slot_mats_and_without(self):
        import share_format as sf
        look = sf.sample_look(1); self.assertIn("SlotMats", look["data"])
        look["data"]["SlotMats"] = {"Shorts#1": "Jacket#2"}
        back = json.loads(sf.encode(look)); self.assertEqual(back["data"]["SlotMats"], {"Shorts#1": "Jacket#2"})
        del look["data"]["SlotMats"]
        self.assertNotIn("SlotMats", json.loads(sf.encode(look))["data"])

    def test_reader_resets_slot_mats_so_a_file_without_it_reads_empty(self):
        import share_bp as sbp
        for name in ("Sh R Snap", "Sh R Outfit"):
            g = fn_graph(name)
            fv = "ShFSnap_SlotMats" if name == "Sh R Snap" else "ShFOutfit_SlotMats"
            self.assertTrue(any(n.get("var") == fv for n in g["nodes"]), name)
            first = [n for n in g["nodes"] if n.get("function") == "Map_Clear" and next(m for m in g["nodes"] if m["id"] == n["in"]["TargetMap"].lstrip("@").split(".")[0]).get("var") == fv]
            self.assertTrue(first, "%s clears %s before reading" % (name, fv))

    def test_older_reader_skips_slot_mats(self):
        """A reader built from a schema without SlotMats (an older AltUI) sends the unknown key to Sh Skip Value."""
        import share_bp as sbp, share_format as sf
        old = [f for f in sf.OUTFIT_SCHEMA if f[0] != "SlotMats"]
        saved = sbp.SCHEMAS["Outfit"]
        sbp.SCHEMAS["Outfit"] = (saved[0], old)
        try: fnd = sbp.f_sh_r_schema("Outfit")
        finally: sbp.SCHEMAS["Outfit"] = saved
        g = fnd["graph"]
        self.assertNotIn("SlotMats", [n["in"].get("B") for n in g["nodes"] if n.get("id", "").startswith("ke")])
        sk = next(n for n in g["nodes"] if n["id"] == "sk"); self.assertEqual(sk["function"], "Sh Skip Value")
        self.assertTrue(any("sk" in c and "after" in c for c in g["exec"]))


class SlotMatsContextMenu(unittest.TestCase):
    def _rows(self, name):
        g = fn_graph(name)
        return g, [n["in"].get("action") for n in g["nodes"] if n.get("function") == "Init" and "action" in n.get("in", {})]

    def test_both_menus_have_material_rows(self):
        for name in ("On Item Context", "On Bag Item Context"):
            _, acts = self._rows(name)
            self.assertIn("ClothesMaterial", acts, name)
            self.assertIn("ClothesResetMat", acts, name)

    def test_reset_row_sits_behind_item_has_own_mat(self):
        for name in ("On Item Context", "On Bag Item Context"):
            g, _ = self._rows(name)
            nodes = {n["id"]: n for n in g["nodes"]}
            for ch in g["exec"]:
                fs = [nodes[i].get("function") for i in ch if i in nodes]
                if "Item Has Own Mat" in fs:
                    ids = [i for i in ch if i in nodes]
                    row = [i for i in ids if nodes[i].get("function") == "Init" and nodes[i]["in"].get("action") == "ClothesResetMat"]
                    self.assertTrue(row, name)
                    self.assertLess(fs.index("Item Has Own Mat"), ids.index(row[0]))
                    return
            self.fail(name)

    def test_bag_material_row_only_when_worn(self):
        g, _ = self._rows("On Bag Item Context")
        nodes = {n["id"]: n for n in g["nodes"]}
        for ch in g["exec"]:
            if any(nodes.get(i, {}).get("in", {}).get("action") == "ClothesMaterial" for i in ch):
                # the row hangs behind the colour loop, which only the "worn" branch of bc reaches (bc:else skips to the damage row)
                self.assertEqual(ch[0], "cc_fe:Completed")
                self.assertTrue(any("bc" in c and "cc_fe" in c for c in g["exec"]))
                self.assertTrue(any(c[0] == "bc:else" for c in g["exec"]))
                return
        self.fail("no chain with the material row")

    def test_clothes_material_row_only_when_worn(self):
        """Play test 2026-11-21: "Material..." stood on pieces that are not worn too; the picker needs a worn target (Rebuild List closes
        it otherwise), so the click did nothing. The row hangs behind an Is Worn branch whose else skips it."""
        g, _ = self._rows("On Item Context")
        nodes = {n["id"]: n for n in g["nodes"]}
        for ch in g["exec"]:
            ids = [i for i in ch if i in nodes]
            if any(nodes[i].get("in", {}).get("action") == "ClothesMaterial" for i in ids):
                row = [i for i in ids if nodes[i].get("in", {}).get("action") == "ClothesMaterial"][0]
                self.assertIn("bmtw", ids); self.assertLess(ids.index("bmtw"), ids.index(row))
                self.assertEqual(nodes["mtw"].get("function"), "Is Worn")
                self.assertTrue(any(c[0] == "bmtw:else" and c[1] == "gcr" for c in g["exec"]))
                return
        self.fail("no chain with the material row")

    def test_menu_actions_and_picker_signature(self):
        with open("assets/gen/gen_manager_ui.py") as f:
            ui = f.read()
        self.assertIn('("ClothesMaterial", "Open Mat Picker", "ContextItem")', ui)
        fn_graph("Open Mat Picker")

    def test_texts_in_all_languages(self):
        from assets.gen import strings, strings_fr
        for k in ("Menu_Material", "Menu_MaterialReset"):
            self.assertEqual(len(strings.STRINGS[k]), 7, k)   # en de zh ru es pl + fr
            self.assertIn(k, open("assets/gen/strings_fr.py").read())


class SlotMatsPicker(unittest.TestCase):
    """The picker on the clothes page (spec, "Picker"): MatPickTarget set = picking mode."""

    def _nodes(self, g):
        return {n["id"]: n for n in g["nodes"]}

    def _src(self, nodes, pin):
        return nodes[pin.lstrip("@").split(".")[0]]

    def test_item_click_branches_to_the_picker_before_can_wear(self):
        g = fn_graph("On Item Clicked"); nodes = self._nodes(g)
        cw = next(i for i, n in nodes.items() if n.get("function") == "Can Wear")
        ch = next(c for c in g["exec"] if c[0] == "bpl:else")
        b = ch[1]
        self.assertEqual(nodes[b]["kind"], "branch")
        cond = self._src(nodes, nodes[b]["in"]["Condition"])
        self.assertEqual(self._src(nodes, cond["in"]["A"]).get("var"), "MatPickTarget")
        self.assertTrue(any(c[0] == b + ":else" and c[1] == cw for c in g["exec"]), "not picking: Can Wear as before")
        picked = [nodes[i].get("function") for i in ch[2:]] + [nodes[i].get("function") for c in g["exec"] if c[0] == b for i in c[1:]]
        self.assertEqual(picked, ["Open Mat Pick Menu"], "the tile's material menu, nothing else")
        om = next(n for n in g["nodes"] if n.get("function") == "Open Mat Pick Menu")
        self.assertEqual((om["in"]["name"], om["in"]["place"]), ("@entry.name", "true"), "a new menu at the mouse")
        for f in ("Push History", "Wear", "Rebuild List"):
            self.assertNotIn(f, calls(fn_graph("Open Mat Pick Menu")), f)

    def test_menu_action_knows_the_picker_prefixes(self):
        g = fn_graph("On Menu Action")
        prefixes = [n["in"].get("InPrefix") for n in g["nodes"] if n.get("function") == "StartsWith"]
        for p in ("MatSlot:", "MatX:", "MatPick:"):
            self.assertIn(p, prefixes)
        for p in ("MatRow:", "MatSrc:"):
            self.assertNotIn(p, prefixes)
        f = funcs(g)
        self.assertIn("Slot Set Mat", f)
        self.assertIn("Slot Reset Mat", f)

    def test_reset_x_pushes_history_first(self):
        g = fn_graph("On Menu Action"); nodes = self._nodes(g)
        ch = next(c for c in g["exec"] if any(nodes.get(i, {}).get("function") == "Slot Reset Mat" for i in c))
        fs = [nodes[i].get("function") for i in ch if i in nodes]
        self.assertLess(fs.index("Push History"), fs.index("Slot Reset Mat"))

    def test_mat_pick_row_swaps_and_keeps_the_menu_open(self):
        g = fn_graph("On Menu Action"); nodes = self._nodes(g)
        ch = next(c for c in g["exec"] if "mpk_h" in c)   # main chain: the own-slot branch (Slot Reset Mat) is on it, the swap on its else
        fs = [nodes[i].get("function") for i in ch if i in nodes]
        self.assertEqual([f for f in fs if f], ["Push History", "Slot Reset Mat", "Rebuild Mat Pick Bar", "Open Mat Pick Menu"])
        self.assertEqual(ch[ch.index("mpk_h") + 1], "bmpe")
        self.assertNotIn("Close Menu", fs, "the menu stays open")
        self.assertNotIn("Rebuild List", fs)
        # the branch sits before the usual Close Menu: drawer rows, then MatPick:, then everything else after Close Menu
        self.assertEqual(ch[0], "bdrw:else"); br = ch[1]
        sw = self._src(nodes, nodes[br]["in"]["Condition"])
        self.assertEqual(sw["in"]["InPrefix"], "MatPick:")
        nxt = next(c for c in g["exec"] if c[0] == br + ":else")
        self.assertEqual(nodes[nxt[1]].get("function"), "Close Menu")
        # source = everything after "MatPick:", the menu drawn again for the piece before the last '#', not placed anew
        ss = next(n for n in g["nodes"] if n.get("function") == "Slot Set Mat")
        self.assertEqual(self._src(nodes, ss["in"]["slot"]).get("var"), "MatPickSlot")
        self.assertEqual(self._src(nodes, ss["in"]["name"]).get("var"), "MatPickTarget")
        rc = self._src(nodes, ss["in"]["source"]); self.assertEqual((rc.get("function"), rc["in"]["Count"]), ("RightChop", "8"))
        om = next(n for n in g["nodes"] if n.get("function") == "Open Mat Pick Menu")
        self.assertEqual(om["in"]["place"], "false")
        sp = self._src(nodes, self._src(nodes, om["in"]["name"])["in"]["InString"])
        self.assertEqual((sp.get("function"), sp["in"]["InStr"], sp["in"]["SearchDir"]), ("Split", "#", "FromEnd"))

    def test_picker_actions_never_rebuild_the_list(self):
        g = fn_graph("On Menu Action"); nodes = self._nodes(g)
        for p in ("MatSlot:", "MatX:", "MatPick:"):
            sw = next(i for i, n in nodes.items() if n.get("function") == "StartsWith" and n["in"].get("InPrefix") == p)
            br = next(i for i, n in nodes.items() if n.get("kind") == "branch" and n["in"]["Condition"].lstrip("@").split(".")[0] == sw)
            ch = next(c for c in g["exec"] if br in c and not c[0].startswith(br + ":"))
            fs = [nodes[i].get("function") for i in ch[ch.index(br) + 1:] if i in nodes]
            self.assertNotIn("Rebuild List", fs, p)
            self.assertIn("Rebuild Mat Pick Bar", fs, p)
        self.assertNotIn("Rebuild List", funcs(fn_graph("Rebuild Mat Pick Bar")) + funcs(fn_graph("Open Mat Pick Menu")))

    def test_mat_pick_menu(self):
        g = fn_graph("Open Mat Pick Menu"); nodes = self._nodes(g); f = funcs(g)
        for x in ("Item Mat Slots", "Clear Rows", "Add Row", "Init", "Mat Pick Row", "Place At", "AddToViewport", "GetMousePositionOnViewport"):
            self.assertIn(x, f)
        init = next(n for n in g["nodes"] if n.get("function") == "Init")
        self.assertEqual((init["in"]["action"], init["in"]["caption"]), ("@mpr.action", "@mpr.text"))
        r = fn_graph("Mat Pick Row"); rf = funcs(r)
        self.assertIn("Slot Color Key", rf)
        self.assertIn("MatPick:", [n["in"].get("A") for n in r["nodes"] if n.get("function") == "Concat_StrStr"])
        self.assertTrue(any(n.get("kind") == "get" and n.get("var") == "SlotMats" for n in r["nodes"]), "the row on the active slot is marked")
        self.assertIn(("> ", "   "), [(n["in"].get("A"), n["in"].get("B")) for n in r["nodes"] if n.get("function") == "SelectString"])
        self.assertEqual(sum(1 for n in g["nodes"] if n.get("function") == "Init"), 1, "material rows only, no Cancel row")
        # placed only for a new menu (place); a redraw keeps it where it stands
        ch = next(c for c in g["exec"] if c[0] == "fe:Completed")
        self.assertEqual(nodes[ch[1]]["kind"], "branch"); self.assertEqual(nodes[ch[1]]["in"]["Condition"], "@entry.place")
        self.assertIn("spv", ch)
        self.assertFalse(any(c[0] == ch[1] + ":else" for c in g["exec"]))
        # the same widgets and placement as On Item Context
        oic = fn_graph("On Item Context")
        cls = lambda gr, fn_: {n.get("cls") or n.get("class") for n in gr["nodes"] if n.get("function") == fn_}
        for x in ("Place At", "Add Row", "Init"):
            self.assertEqual(cls(g, x), cls(oic, x), x)
        z = lambda gr: [n["in"].get("ZOrder") for n in gr["nodes"] if n.get("function") == "AddToViewport"]
        self.assertEqual(z(g), z(oic))

    def test_no_source_bar_left(self):
        import os
        for f in ("30_manager.json", "40_widgets.json", "50_manager_ui.json"):
            t = open(os.path.join("assets", f)).read()
            for x in ("MatSrc", "Mat Src", "Refresh Mat Pick Tiles", "MatPickOpen", "MatPickIdx", "MatPickCaps", "MatSource"):
                self.assertNotIn(x, t, (f, x))
        for f in ("gen_manager.py", "gen_manager_ui.py", "gen_widgets.py", "strings.py", "strings_fr.py"):
            t = open(os.path.join("assets", "gen", f)).read()
            for x in ("MatSrc", "MAT_SRC_H", "MatSource", "Set Highlight"):
                self.assertNotIn(x, t, (f, x))
        self.assertNotIn("Set Highlight", funcs(fn_graph("Clo Init Tile")))

    def test_x_only_beside_swapped_chips(self):
        g = fn_graph("Rebuild Mat Pick Bar"); nodes = self._nodes(g)
        self.assertNotIn("SetVisibility", funcs(g), "no hidden ✕ keeping its place")
        ch = next(c for c in g["exec"] if c[0] == "fe")
        self.assertLess(ch.index("bsw"), ch.index("x_cr"), "the ✕ is created in the swapped branch only")

    def test_filtered_items_shows_everything_while_picking(self):
        g = fn_graph("Rebuild List Body"); nodes = self._nodes(g)
        it = next(n for n in g["nodes"] if n.get("function") == "Filtered Items")
        src = nodes[it["in"]["onlyOwned"].lstrip("@").split(".")[0]]
        self.assertEqual(src.get("function"), "BooleanAND", "onlyOwned = the check box and not picking")
        self.assertIn("Rebuild Mat Pick Bar", funcs(g))
        self.assertIn("Close Mat Picker", funcs(g), "the target taken off closes the picker")

    def test_no_slot_rows_in_the_list(self):
        import sys, os
        sys.path.insert(0, os.path.join("assets", "gen")); import vlist
        self.assertFalse(hasattr(vlist, "LINE"))
        w = json.load(open("assets/40_widgets.json"))
        self.assertFalse(any(a["path"].endswith("/W_MatRow") for a in w["assets"]))
        for f in ("30_manager.json", "50_manager_ui.json"):
            self.assertNotIn("Init Line", open(os.path.join("assets", f)).read(), f)

    def test_close_paths(self):
        self.assertIn("Close Mat Picker", funcs(fn_graph("Panel Key Close")))
        self.assertIn("Mat Pick End", funcs(fn_graph("Select Page Body")))
        with open("assets/gen/gen_manager_ui.py") as f:
            self.assertIn('("MatClose", "Close Mat Picker", None)', f.read())

    def test_esc_closes_the_open_menu_before_the_picker(self):
        g = fn_graph("Panel Key Close"); nodes = self._nodes(g)
        ch = next(c for c in g["exec"] if "mno" in c)
        fs = [nodes[i].get("function") for i in ch if i in nodes]
        self.assertEqual([f for f in fs if f], ["Menu Open", "Close Menu"])
        self.assertTrue(any(c[0] == "bmp" or (c[0] == "bl:else" and c[1] == "bmp") for c in g["exec"]))
        self.assertIn(["bmno:else", "cmp"], g["exec"], "no menu: the picker closes")
        self.assertEqual(nodes["cmp"]["function"], "Close Mat Picker")
        mo = fn_graph("Menu Open")
        self.assertIn("IsInViewport", funcs(mo))

    def test_open_keeps_where_the_panel_stood(self):
        g = fn_graph("Open Mat Picker")
        sets = {n.get("var") for n in g["nodes"] if n.get("kind") == "set"}
        for v in ("MatPickTarget", "MatPickSlot", "MatPickBack", "MatPickBackSlot", "MatPickBackGroup", "MatPickScrolls"):
            self.assertIn(v, sets)
        self.assertIn("Rebuild List", funcs(g))

    def test_chip_right_click_does_nothing(self):
        g = fn_graph("SubTab Context")
        self.assertIn("MatSlot:", [n["in"].get("InPrefix") for n in g["nodes"] if n.get("function") == "StartsWith"])
        self.assertIn("MatSlot:", [n["in"].get("InPrefix") for n in fn_graph("Select SubTab")["nodes"] if n.get("function") == "StartsWith"])

    def test_texts_in_all_languages(self):
        from assets.gen import strings
        for k in ("Menu_MatFor", "MatFrom"):
            self.assertEqual(len(strings.STRINGS[k]), 7, k)
            self.assertIn(k, open("assets/gen/strings_fr.py").read())
        self.assertEqual(strings.STRINGS["Menu_MatFor"][1], "Material für: %s")
        self.assertEqual(strings.STRINGS["MatFrom"][1], "%s, aus %s")
        for k in ("MatSource", "MatSourceHint"):
            self.assertNotIn(k, strings.STRINGS)


class SlotMatsFollowers(unittest.TestCase):
    """Followers and "look as enemy" (Spawn Look Follower): the material goes on before the colours, at every place."""

    def test_fol_apply_slot_mats_splits_from_the_end(self):
        g = fn_graph("Fol Apply Slot Mats")
        sp = next(n for n in g["nodes"] if n.get("function") == "Split")
        self.assertEqual(sp["in"]["SearchDir"], "FromEnd")
        self.assertIn("Set Slot Mat On", funcs(g))

    def test_s_fol_slotmats_is_the_last_member(self):
        with open("assets/gen/followers.py") as f:
            src = f.read()
        with open("assets/gen/gen_manager_ui.py") as f:
            ui = f.read()
        tail = src[src.index('param("Boobs", "float")'):]
        self.assertLess(tail.index('param("Waist"'), tail.index('param("SlotMats", "name", "map", value_type="string")'))
        self.assertIn('"Waist", "SlotMats"]', ui)

    def test_mats_applied_before_colors_everywhere(self):
        for name in ("Finish Look Follower", "Fol Spawn", "Fol Sync", "Fol Clothes Give", "Fol Restore Outfit"):
            g = fn_graph(name)
            nodes = {n["id"]: n for n in g["nodes"]}
            seq = [nodes[i].get("function") for c in g["exec"] for i in c if i in nodes]
            for ch in g["exec"]:
                f = [nodes[i].get("function") for i in ch if i in nodes]
                if "Fol Apply Slot Colors" in f:
                    self.assertIn("Fol Apply Slot Mats", f, name)
                    self.assertLess(f.index("Fol Apply Slot Mats"), f.index("Fol Apply Slot Colors"), name)
            self.assertEqual(seq.count("Fol Apply Slot Mats"), seq.count("Fol Apply Slot Colors"), name)

    def test_finish_look_follower_copies_jodis_mats_by_prefix(self):
        g = fn_graph("Finish Look Follower")
        vars_ = [n.get("var") for n in g["nodes"]]
        self.assertIn("SlotMats", vars_)
        self.assertIn("FolSlotMats", vars_)
        self.assertGreaterEqual(funcs(g).count("StartsWith"), 2)


class SlotMatsReviewFixes(unittest.TestCase):
    """Final review (2026-11-17): Random Outfit keeps swaps, resets re-lay the game colour, outfits cover every material slot."""

    def _nodes(self, g):
        return {n["id"]: n for n in g["nodes"]}

    def _src_var(self, g, pin):
        return self._nodes(g)[pin.lstrip("@").split(".")[0]].get("var")

    def test_random_outfit_snapshot_carries_slot_mats(self):
        g = fn_graph("Random Outfit"); b = self._nodes(g)
        self.assertEqual(self._src_var(g, b["mk"]["in"]["SlotMats"]), "SlotMats")
        self.assertEqual(self._src_var(g, b["mk"]["in"]["SlotColors"]), "SlotColors")

    def test_relay_game_color_keeps_the_save_entry(self):
        g = fn_graph("Relay Game Color"); f = funcs(g); b = self._nodes(g)
        self.assertNotIn("Map_Remove", f, "the save's Clothes Colors entry stays")
        self.assertIn("Get Clothes Color", f)
        chg = next(n for n in g["nodes"] if n.get("function") == "Change Color")
        self.assertEqual(chg["in"]["Color"], "@gc.color")
        self.assertIn(["bf:else", "ric"], g["exec"])
        self.assertEqual(b["ric"]["function"], "Reset Item Colors")
        self.assertEqual(b["bf"]["in"]["Condition"], "@gc.found")

    def test_reset_paths_relay_instead_of_restore(self):
        for name in ("Slot Reset Mat", "Item Reset Mats", "Reset Dropped Mats"):
            f = funcs(fn_graph(name))
            self.assertNotIn("Restore Piece Color", f, name)
            self.assertIn("Relay Game Color", f, name)
        for name in ("Slot Reset Mat", "Item Reset Mats"):
            g = fn_graph(name); nodes = self._nodes(g)
            ch = next(c for c in g["exec"] if any(nodes.get(i, {}).get("function") == "Relay Game Color" for i in c))
            fs = [nodes[i].get("function") for i in ch if i in nodes]
            self.assertLess(fs.index("Relay Game Color"), fs.index("Apply Item Colors"), name)

    def test_reset_dropped_mats_does_not_apply_old_swaps(self):
        g = fn_graph("Reset Dropped Mats"); nodes = self._nodes(g)
        self.assertNotIn("Apply Item Colors", funcs(g), "SlotMats still holds the old swaps here")
        ch = next(c for c in g["exec"] if "rs" in c)
        self.assertEqual(ch[ch.index("rs"):ch.index("rs") + 2], ["rs", "rgc"])
        self.assertEqual(nodes["rgc"]["in"]["name"], "@pn.ReturnValue")

    def test_item_reset_mats_tail_only_after_a_removal(self):
        g = fn_graph("Item Reset Mats"); b = self._nodes(g)
        self.assertEqual(b["ra0"]["in"]["MatResetAny"], "false"); self.assertEqual(b["ra1"]["in"]["MatResetAny"], "true")
        self.assertIn(["fe", "bf", "rm", "rs", "ra1"], g["exec"])
        tail = next(c for c in g["exec"] if c[0] == "fe:Completed")
        self.assertEqual(tail[1], "bra")
        self.assertEqual(self._src_var(g, b["bra"]["in"]["Condition"]), "MatResetAny")

    def test_slot_reset_color_ends_with_apply_item_colors(self):
        g = fn_graph("Slot Reset Color"); nodes = self._nodes(g)
        tail = next(c for c in g["exec"] if c[0] == "fe:Completed")
        fs = [nodes[i].get("function") for i in tail if i in nodes]
        self.assertLess(fs.index("Restore Piece Color"), fs.index("Apply Item Colors"))
        self.assertLess(fs.index("Apply Item Colors"), fs.index("Save Settings"))

    def test_outfits_walk_every_material_slot(self):
        for name in ("Remember Outfit Colors", "Outfit Slot Colors"):
            g = fn_graph(name); b = self._nodes(g)
            self.assertEqual(b["ms"]["function"], "Item Mat Slots", name)
            self.assertEqual(b["fm"]["in"]["Array"], "@bms.Idx", name)
            self.assertIn(["fi:Completed", "ms", "fm"], g["exec"], name)
            self.assertIn(["fm", "bmf", "madd"], g["exec"], name)
            self.assertEqual(b["msk"]["in"]["slot"], "@fm.Array Element", name)
            self.assertEqual(b["mosk"]["in"]["slot"], "@fm.Array Element", name)
            self.assertFalse(any("fi" in c and "bmf" in c for c in g["exec"]), name + ": the mats are no longer in the colour loop")

    def test_load_save_slot_mats_skips_keys_without_equals(self):
        g = fn_graph("Load Save Slot Mats"); b = self._nodes(g)
        self.assertEqual(b["bsp"]["in"]["Condition"], "@sp.ReturnValue")
        self.assertIn(["fk", "bsw", "bsp", "add"], g["exec"])

    def test_menu_reset_mat_pushes_history(self):
        g = fn_graph("On Menu Action"); nodes = self._nodes(g)
        ch = next(c for c in g["exec"] if any(nodes.get(i, {}).get("function") == "Item Reset Mats" for i in c))
        fs = [nodes[i].get("function") for i in ch if i in nodes]
        self.assertLess(fs.index("Push History"), fs.index("Item Reset Mats"))
        self.assertEqual(self._src_var(g, nodes["crm_r"]["in"]["name"]), "ContextItem")

    def test_picker_ignores_only_worn_and_counts_follow(self):
        g = fn_graph("Rebuild List Body"); nodes = self._nodes(g)
        it = next(n for n in g["nodes"] if n.get("function") == "Filtered Items")
        self.assertEqual(nodes[it["in"]["onlyWorn"].lstrip("@").split(".")[0]].get("function"), "BooleanAND")
        g = fn_graph("Rebuild Left"); nodes = self._nodes(g)
        fc = next(n for n in g["nodes"] if n.get("function") == "Filtered Counts")
        for k in ("onlyOwned", "onlyWorn"):
            self.assertEqual(nodes[fc["in"][k].lstrip("@").split(".")[0]].get("function"), "BooleanAND", k)


class TestMatPickOwnSlot(unittest.TestCase):
    def test_own_active_slot_resets_instead_of_swap(self):
        g = fn_graph("On Menu Action"); nodes = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(nodes["mpk_eq"]["function"], "EqualEqual_StrStr")
        self.assertEqual(nodes["bmpe"]["in"]["Condition"], "@mpk_eq.ReturnValue")
        self.assertEqual(nodes["mpk_z"]["function"], "Slot Reset Mat")
        self.assertEqual(nodes["mpk_c"]["function"], "Slot Set Mat")
        ex = g["exec"]
        yes = next(c for c in ex if "mpk_z" in c); no = next(c for c in ex if "mpk_c" in c)
        self.assertLess(yes.index("mpk_h"), yes.index("bmpe")); self.assertLess(yes.index("bmpe"), yes.index("mpk_z"))
        self.assertEqual(no, ["bmpe:else", "mpk_c", "mpk_b", "mpk_m"])


class TestRowMaterialOverride(unittest.TestCase):
    """Play test 2026-11-18: colour variants (Witch02_Top_0/_1/_2) share the mesh; their own material sits in the ClothesTable row's
    Materials ({SlotName, Material}), which Clothes_Comp.Wear puts on by slot name (None -> slot 0). A slot's own material is that
    override, else the mesh's."""
    MAT_STRUCT = "/Game/Project/Classes/Struct/MaterialStruct"

    def test_own_slot_mat_walks_the_row_overrides(self):
        g = fn_graph("Own Slot Mat"); nodes = {n["id"]: n for n in g["nodes"]}
        br = next(n for n in g["nodes"] if n.get("kind") == "break" and n.get("struct") == "/Game/Project/Clothes/ClothesStruct")
        fe = [n for n in g["nodes"] if n.get("kind") == "foreach"]
        self.assertTrue(any(n["in"]["Array"] == "@%s.Materials" % br["id"] for n in fe), "loop over the row's Materials")
        bo = next(n for n in g["nodes"] if n.get("kind") == "break" and n.get("struct") == self.MAT_STRUCT)
        eqs = [n for n in g["nodes"] if n.get("function") == "EqualEqual_NameName"]
        self.assertTrue(any(n["in"].get("A") == "@%s.SlotName" % bo["id"] and "MaterialSlotName" in n["in"].get("B", "") for n in eqs),
                        "matched by slot name")
        self.assertTrue(any(n["in"].get("A") == "@%s.SlotName" % bo["id"] and n["in"].get("B") == "None" for n in eqs),
                        "SlotName None means slot 0")
        sets = [n for n in g["nodes"] if n.get("kind") == "set" and n.get("var") == "OwnMatTmp"]
        self.assertTrue(any(n["in"]["OwnMatTmp"] == "@%s.Material" % bo["id"] for n in sets), "the override wins")
        self.assertTrue(any("MaterialInterface" in n["in"]["OwnMatTmp"] for n in sets), "else the mesh material")

    def test_mesh_material_set_before_the_override_loop(self):
        g = fn_graph("Own Slot Mat")
        ch = next(c for c in g["exec"] if c[0] == "entry")
        nodes = {n["id"]: n for n in g["nodes"]}
        mesh_set = next(i for i in ch if nodes.get(i, {}).get("var") == "OwnMatTmp" and "MaterialInterface" in nodes[i]["in"]["OwnMatTmp"])
        loop = next(i for i in ch if nodes.get(i, {}).get("kind") == "foreach")
        self.assertLess(ch.index(mesh_set), ch.index(loop))

    def test_every_own_material_read_goes_through_own_slot_mat(self):
        for name in ("Mat Of Slot", "Restore Slot Mat On", "Item Color Slots", "Reset Item Colors"):
            g = fn_graph(name)
            self.assertIn("Own Slot Mat", funcs(g), name)
            self.assertFalse(any("MaterialInterface" in json.dumps(n.get("in", {})) for n in g["nodes"]),
                             "%s reads no mesh material itself" % name)

    def test_restore_puts_the_own_material_on(self):
        g = fn_graph("Restore Slot Mat On"); nodes = {n["id"]: n for n in g["nodes"]}
        sm = next(n for n in g["nodes"] if n.get("function") == "SetMaterial")
        self.assertEqual(nodes[sm["in"]["Material"].lstrip("@").split(".")[0]].get("function"), "Own Slot Mat")


    def test_restore_prefers_the_games_own_instance(self):
        """Play test 2026-11-21 (open-since-3.0.0 F.11): after "Reset material" the mirror colour was not seen any more - Change Color
        writes on the instances in Materials for Color, and the slot showed the plain asset material. The game's instance of the own
        material goes back on the slot; the asset material only without one."""
        g = fn_graph("Restore Slot Mat On"); nodes = {n["id"]: n for n in g["nodes"]}
        dumped = json.dumps(g)
        self.assertIn("Materials for Color", dumped); self.assertIn("Materials for Damage", dumped)
        sms = [n for n in g["nodes"] if n.get("function") == "SetMaterial"]; self.assertEqual(len(sms), 2)
        self.assertEqual(sms[1]["in"]["Material"], "@gmid.GameMIDTmp")
        br = next(c for c in g["exec"] if "bmid" in c and "smg" in c); self.assertLess(br.index("bmid"), br.index("smg"))
        self.assertTrue(any(c[0] == "bmid:else" and "sm" in c for c in g["exec"]), "no instance of the game's: the asset material")
        self.assertIn("Array_Contains", funcs(g), "an instance another slot shows is not taken")


class TestMatLog(unittest.TestCase):
    """Measuring build for play test 2026-11-18 (B: picker does not open on a many-slot target, C: colour on a swapped material):
    MATLOG (gen_manager.py) wires "Log Line" into the picker path and every material / colour put on a slot - and nothing without it."""
    FUNCS = ("On Menu Action", "Open Mat Picker", "Rebuild List Body", "Select Page Body", "Close Mat Picker", "Mat Pick End",
             "Rebuild Mat Pick Bar", "Apply Item Colors", "Apply Item Mats On", "Set Slot Mat On", "Set Slot Color On")

    def test_log_follows_the_switch(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "assets", "gen"))
        from gen_manager import MATLOG
        for name in self.FUNCS:
            self.assertEqual("Log Line" in funcs(fn_graph(name)), MATLOG, name)


if __name__ == "__main__":
    unittest.main()
