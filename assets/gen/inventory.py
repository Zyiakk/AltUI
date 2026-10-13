"""Inventory tab (docs/specs/2026-10-07-inventory-tab-design.md): groups, item kinds and which actions a tile offers.
The generators build the blueprint branches from these tables; the unit test checks them without the editor."""
INV_GROUPS = ["Weapon", "Ammo", "Equipment", "Tool"]   # ItemTable.HyperBoxGroup, chip order; "None" = all
ACTIONS = ["Store1", "StoreHalf", "StoreAll", "Take1", "TakeHalf", "TakeAll", "Use", "Check", "Drop1", "DropAll", "Shortcut1", "Shortcut2", "Unload",
           "CatBag1", "CatBag5", "CatBox1", "CatBox5", "Attach"]   # Attach: to the weapons tab, the weapon's accessories   # Cat*: from the all-items catalog, 1 or 5 packs (ItemTable.NumberOfPick)
CAT_GROUP = "Collect"   # catalog only: rows without a box group that are no keys / cards (ItemClass 2) and have an actor class
KINDS = ["gun", "weapon", "ammo", "usable", "other"]


def kind_of(item_class, flag):
    """ItemClass 3 with flag bit 2 = gun (a Weapon_Gun_Base actor, Gun_Struct in the box); other class 3 = melee / thrown;
    4 = ammo; 0 and 5 = usable (pills, flashlight, sewing kit ...)."""
    if item_class == 3: return "gun" if flag & 2 else "weapon"
    if item_class == 4: return "ammo"
    if item_class in (0, 5): return "usable"
    return "other"


def left_action(box):
    return {"bag": "Store1", "box": "Take1", "cat": "CatBag1"}[box]


_STACK = ["StoreHalf", "StoreAll"]
MENUS = {
    ("bag", "gun"): ["Use", "Check", "Drop1", "Shortcut1", "Shortcut2", "Unload", "Attach"],   # one actor per gun: the left click stores it
    ("bag", "weapon"): ["Use", "Check"] + _STACK + ["Drop1", "DropAll", "Shortcut1", "Shortcut2"],
    ("bag", "ammo"): ["Check"] + _STACK + ["Drop1", "DropAll"],
    ("bag", "usable"): ["Use", "Check"] + _STACK + ["Drop1", "DropAll", "Shortcut1", "Shortcut2"],
    ("bag", "other"): ["Check"] + _STACK + ["Drop1", "DropAll"],
    ("box", "gun"): ["Check"],                                                       # left click takes it
}
for _k in ("weapon", "ammo", "usable", "other"): MENUS[("box", _k)] = ["TakeHalf", "TakeAll", "Check"]
# catalog: always placed by hand (never used automatically); a gun only into the backpack - the game builds a box gun only
# from a carried actor (Add a Gun); "collect" (CAT_GROUP rows) has no box group, so no box either
for _k in ("weapon", "ammo", "usable", "other"): MENUS[("cat", _k)] = ["CatBag1", "CatBag5", "CatBox1", "CatBox5", "Check"]
MENUS[("cat", "gun")] = ["CatBag1", "Check"]
MENUS[("cat", "collect")] = ["CatBag1", "CatBag5", "Check"]


def menu(box, kind):
    return list(MENUS[(box, kind)])
