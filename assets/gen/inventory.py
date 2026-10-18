"""Inventory tab (docs/specs/2026-10-07-inventory-tab-design.md): groups, item kinds and which actions a tile offers.
The generators build the blueprint branches from these tables; the unit test checks them without the editor."""
INV_GROUPS = ["Weapon", "Ammo", "Equipment", "Tool"]   # ItemTable.HyperBoxGroup, chip order; "None" = all
ACTIONS = ["Store1", "StoreHalf", "StoreAll", "Take1", "TakeHalf", "TakeAll", "Use", "Check", "Drop1", "DropAll", "Shortcut1", "Shortcut2", "Unload",
           "CatBag1", "CatBag5", "CatBox1", "CatBox5", "Attach", "StoreN", "TakeN", "CatBagN", "CatBoxN"]   # *N: the amount row's number (Manager.MenuAmount)   # Attach: to the weapons tab, the weapon's accessories   # Cat*: from the all-items catalog, 1 or 5 packs (ItemTable.NumberOfPick)
CAT_GROUP = "Collect"   # catalog only: rows without a box group that are no keys / cards (ItemClass 2) and have an actor class - or are the invisible hand
CAT_NO_ACTOR = "InvisibleHand"   # no actor (it is never on the ground), works in the bag: picks up items near Jodi
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


# A chosen amount (docs/specs/2026-10-14-stack-amount-design.md): a slider + number row, then one row per target "<action> n".
# Not for guns (one actor each), a stack of one, or a catalogue item that does not stack (the game gives one anyway).
AMOUNT_ROWS = {"bag": ["StoreN"], "box": ["TakeN"], "cat": ["CatBagN", "CatBoxN"]}
FOL_AMOUNT_ROWS = {"jodi": ["GiveN"], "fol": ["TakeN", "TakeBoxN"]}   # Followers tab: Jodi's backpack / box tile, a figure's tile
AMOUNT_CAT_PACKS = 10      # catalogue slider: 1 .. 10 packs (ItemTable.NumberOfPick), counted in pieces
AMOUNT_FIELD_MAX = 99999   # catalogue field: more than the slider reaches; the game's own limits apply


def amount_rows(box, kind):
    if kind == "gun": return []
    if box == "cat" and kind == CAT_GROUP.lower(): return ["CatBagN"]   # collectibles have no box group
    return list(AMOUNT_ROWS[box])


def has_amount(box, kind, count, consumable):
    if kind == "gun": return False
    if box == "cat": return bool(consumable)
    return count > 1


def amount_range(count, pick, catalog):
    """(slider low, slider high, start, field high). Stack: 1 .. count, start half rounded up. Catalogue: in pieces, the slider
    up to AMOUNT_CAT_PACKS packs, the field up to AMOUNT_FIELD_MAX, start one pack."""
    if catalog:
        pk = max(pick, 1); return 1, AMOUNT_CAT_PACKS * pk, pk, AMOUNT_FIELD_MAX
    return 1, count, (count + 1) // 2, count


# "Discard all" (docs/specs/2026-10-15-drop-warning-design.md): Character_Player_Base.Drop Item throws min(count, NumberOfPick)
# pieces as one physics pickup actor per call. From DROP_WARN_ACTORS actors on, a window asks first (50000 rounds crashed the game).
DROP_WARN_ACTORS = 100


def drop_actors(count, pick):
    """Pickup actors "Discard all" creates: pieces / max(pack, 1), rounded up."""
    pk = max(pick, 1); return (count + pk - 1) // pk


def drop_warns(count, pick):
    return drop_actors(count, pick) >= DROP_WARN_ACTORS
