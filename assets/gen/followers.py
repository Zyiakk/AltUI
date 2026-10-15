"""Followers and NPCs from looks (docs/specs/2026-10-09-followers-design.md): the saved record per figure, the save game,
names and constants the manager (gen_manager.py: signatures, structs; gen_manager_ui.py: bodies) and the panel share.

A figure is a BP_AltUIFollower (gen_follower.py). AltUI keeps one S_Follower per figure in its own save AltUI_Followers.sav -
the game never saves our figures - and re-spawns them on every level start: active, not fallen, and either a follower that
follows (at Jodi) or one whose level this is (at its place)."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from bpdsl import *

VOICES = ["Female_1", "Female_2", "Female_3", "Female_4"]   # the game's NPC voices (NPC_Female.Init Npc Appearance rolls one)
S_FOL = M + "/S_Follower"; SG_FOL = M + "/SG_Followers"; FOL_SLOT = "AltUI_Followers"
W_FOLROW = M + "/W_FolRow"   # one figure in the Followers tab (gen_widgets.py)
S_RAGPART = M + "/S_RagPart"
MODE_FOLLOWER, MODE_NPC = 1, 2
ORDER_FOLLOW, ORDER_STAY = "NpcFollow", "NpcStay"   # Npc_Controller orders (Change Order / Receive Order)
FOL_DIST = 150.0          # spawn distance in front of Jodi (cm)
FOL_SYNC = 10.0           # seconds between two syncs of the figures into the save (position, bag, weapons, fallen)
FOL_WATCH = 0.02          # seconds between two looks at the figures' clothes counts (a piece from the game's swap dialog gets AltUI's colours at once)
FOL_START_DELAY = 1.5     # seconds after the manager's BeginPlay before the level's figures come (Jodi placed, level streamed)
FOL_QUICK_RANGE = 1500.0  # quick menu: the looked-at follower at most this far (cm)
FOL_QUICK_CONE = 0.8      # ... and within this cosine of the camera direction (about 37 degrees)

# real clothes (docs/specs/2026-10-12-follower-echte-kleidung-design.md): a figure's pieces are bag entries of its own, as with
# every NPC of the game. Tiles of the Followers tab: a piece the figure has / a piece in Jodi's backpack.
TILE_FOL_CLOTHES = "folc:"   # folc:<id>:<piece>
TILE_BAG_CLOTHES = "bagc:"   # bagc:<piece>
SEWING_KIT = "SewingKit"     # what repairing a piece costs (InventoryPanel.Repair Clothes)


def is_old_record(clothes, worn, hair):
    """A record from before real clothes: its Parts carry clothes and hair as copies (it keeps working that way)."""
    return not clothes and not worn and not hair


def back_to_jodi(piece, jodi_bag):
    """A piece leaving a figure goes into Jodi's backpack - unless it is there already (her wardrobe keeps it anyway)."""
    return piece not in jodi_bag


def relook_returns(old, new):
    """Look ändern: the figure's pieces the new look does not bring again go back to Jodi (order kept)."""
    return [p for p in old if p not in new]


def slot_keys_of(piece, keys):
    """AltUI's slot colour keys (<piece>#<slot>) of one piece."""
    pre = piece + "#"
    return [k for k in keys if k.startswith(pre)]


def new_pieces(before, now):
    """Pieces a figure has now and did not have at the last sync (the game's swap dialog gave them)."""
    return [p for p in now if p not in before]

STATE_FOLLOWS, STATE_WAITS, STATE_NPC, STATE_INACTIVE, STATE_FALLEN = "Fol_Follows", "Fol_Waits", "Fol_Npc", "Fol_Inactive", "Fol_Fallen"


# Followers tab rows are a table: name, status, then one column per chip in this order. A chip a state does not have leaves its
# column empty, so the chips of all rows stay in line. Widths (layout units) from the longest caption over all languages.
FOL_COLS = [("Follow", ["Fol_Follow"]), ("Wait", ["Fol_Wait"]), ("Here", ["Fol_Here"]), ("Mode", ["Fol_ToNpc", "Fol_ToFollower"]),
            ("Active", ["Fol_Active"]), ("Invuln", ["Fol_Invulnerable"]), ("More", ["Chip_More"])]
FOL_NAME_W = 150          # name column, the status below it (longer names are cut at its edge; the status sets the minimum)
FOL_ROW_GAP = 12          # space between two rows (and above the first) = the gap between backpack and box (6 + 6)
CHIP_CHAR, CHIP_PAD = 7.5, 24   # chip text (12 pt): units per character; padding + frame of a chip
STATE_CHAR, STATE_PAD = 6.5, 16   # status text (11 pt); gap to the chips


def _longest(keys):
    import strings
    return max(len(t) for k in keys for t in strings.STRINGS[k])


def col_width(keys):
    """Width of a chip column: its longest caption (any language) plus the chip's padding."""
    return int(round(_longest(keys) * CHIP_CHAR + CHIP_PAD))


def state_width():
    return int(round(_longest([STATE_FOLLOWS, STATE_WAITS, STATE_NPC, STATE_INACTIVE, STATE_FALLEN]) * STATE_CHAR + STATE_PAD))


def state_key(mode, order, active, fallen):
    """String key of a figure's status line (strings.py): fallen beats inactive beats mode / order."""
    if fallen: return STATE_FALLEN
    if not active: return STATE_INACTIVE
    if mode == MODE_NPC: return STATE_NPC
    return STATE_FOLLOWS if order == ORDER_FOLLOW else STATE_WAITS


def spawn_at_place(mode, order, record_level, level):
    """Where a figure comes on a level start / activation: True = at its saved place, False = in front of Jodi (a following
    follower always comes along; everybody else stays in its level)."""
    following = mode == MODE_FOLLOWER and order == ORDER_FOLLOW
    return (not following) and record_level == level


def comes_on_level_start(active, fallen, mode, order, record_level, level):
    """A figure is spawned on a level start if it is active, not fallen, and either follows Jodi or belongs to this level."""
    if not active or fallen: return False
    return (mode == MODE_FOLLOWER and order == ORDER_FOLLOW) or record_level == level


def structs():
    """S_Follower (one figure) and the save game holding them (bpgen order: after S_RagPart, before the manager)."""
    return [struct(S_FOL, [param("Id", "name"), param("Name", "string"), param("Mode", "int"), param("Order", "name"), param("Active", "bool"),
                           param("Invulnerable", "bool"), param("Fallen", "bool"), param("Parts", "struct:" + S_RAGPART, "array"),
                           param("MorphNames", "name", "array"), param("MorphValues", "float", "array"),
                           param("Items", "name", "map", value_type="int"), param("Guns", "struct:" + P_GUN_S, "array"),
                           param("Level", "string"), param("Where", "struct:/Script/CoreUObject.Transform"),
                           param("Heel", "struct:/Script/CoreUObject.Vector"),   # heels of the look: X Heels Height Ratio, Y Heel Height, Z Feet Additive
                           param("Scales", "float", "array"), param("BodyDef", "struct:" + S_BODYSCALE),   # the look's body sliders (factors) and its body's Body_Scale defaults
                           param("Clothes", "name", "array"), param("Worn", "name", "array"),   # real clothes: its bag's pieces, what it wears
                           param("Colors", "name", "map", value_type=S_LINCOLOR), param("Damage", "name", "map", value_type="float"),   # its Clothes Colors / Save Clothes Damaged
                           param("SlotColors", "name", "map", value_type=S_LINCOLOR),   # AltUI's slot colours of its pieces (<piece>#<slot>)
                           param("Hair", "name"), param("HairColor", S_LINCOLOR),   # its hairstyle (HairstyleTable row) and colour; all empty = an old record
                           # its make-up (worn MakeupTable rows, AltUI's make-up colours): drawn into a target of its own - Jodi's skin
                           # samples one global render target (Skin_RenderTarget), so a copied skin showed HER make-up. Kept false = an old record
                           param("MakeupRows", "name", "array"), param("MakeupColors", "name", "map", value_type=S_LINCOLOR), param("MakeupKept", "bool"),
                           # its voice: VoiceTable row (Character_Base.Play Voice With Name looks it up by Npc Name); None = an old record, gets one on its next spawn
                           param("Voice", "name")]),
            blueprint(SG_FOL, "/Script/Engine.SaveGame", variables=[var("Followers", "struct:" + S_FOL, "array"), var("Counter", "int")])]
