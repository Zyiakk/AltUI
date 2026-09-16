"""Slot -> group from slot_groups.py (slot order = the game's ClothesTypeTable order); group order is fixed."""
GROUPS = ["Tops", "Bottoms", "Dresses", "Shoes", "Accessories"]
from slot_groups import SLOT_GROUP as _PAIRS
SLOT_GROUP = dict(_PAIRS)   # slot -> group, table order
SLOTS = list(SLOT_GROUP)
ORDERED = [s for g in GROUPS for s in SLOTS if SLOT_GROUP[s] == g]
if __name__ == "__main__":
    print(len(SLOTS), ORDERED)
