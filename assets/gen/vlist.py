"""Virtual tile lists: names shared by the manager (state, functions) and the panel (view, spacers, pool container).

A list L keeps its entries as two parallel arrays in the manager, L+"Kind" (HEAD = a heading row over the full width, any other
value = a tile of that kind) and L+"Ref" (what the entry shows, for the list's own Init functions). The panel holds, inside a
ScrollBox, a VerticalBox [top SizeBox, VerticalBox of rows, bottom SizeBox]: only the rows in view (plus one above and below) are
widgets - a heading, or a W_VRow holding exactly that row's tiles (a wrap box would break rows by its own width, not the list's columns) - taken from pools and refilled through "<L> Init Tile" / "<L> Init Head"; the two SizeBoxes stand in for the rows outside,
so the scroll bar and the scroll length stay those of the whole list. Every tile is TileW x TileH, every heading the full width x
HeadH; every row is its height + gap high, so the spacers add up exactly."""
from bpdsl import var, fn, param

HEAD = 1


def state_vars(L):
    return [var(L + "Kind", "int", "array"), var(L + "Ref", "int", "array"), var(L + "RowStart", "int", "array"), var(L + "RowY", "float", "array"),
            var(L + "Cols", "int"), var(L + "First", "int"), var(L + "Last", "int"), var(L + "Dirty", "bool"), var(L + "RowsDirty", "bool"),
            var(L + "TileW", "float"), var(L + "TileH", "float"), var(L + "HeadH", "float"), var(L + "Loop", "int", "array"),
            var(L + "TilePool", "object:/Script/UMG.UserWidget", "array"), var(L + "HeadPool", "object:/Script/UMG.UserWidget", "array"),
            var(L + "VTop", "float"), var(L + "VBottom", "float"), var(L + "VWidth", "float"), var(L + "Cur", "int"), var(L + "Y", "float"),
            var(L + "A", "int"), var(L + "B", "int"), var(L + "TC", "int"), var(L + "HC", "int"),
            var(L + "Loop2", "int", "array"), var(L + "RowPool", "object:/Script/UMG.UserWidget", "array"), var(L + "RC", "int"), var(L + "Seen", "bool"),
            var(L + "TCW", "object:/Script/UMG.UserWidget"), var(L + "HCW", "object:/Script/UMG.UserWidget"), var(L + "RCW", "object:/Script/UMG.UserWidget"),
            var(L + "RowH", "float", "array"), var(L + "MeasW", "object:/Script/UMG.UserWidget", "array"), var(L + "RowOf", "int", "array"), var(L + "Settle", "int"),
            var(L + "ScrollTo", "int", default="-1")]   # entry to scroll into view once the rows are known ("Show in tab")


def signatures(L):
    """Manager functions of list L (bodies: gen_manager_ui.vlist_fns; the list's own "<L> Init Tile" / "<L> Init Head" too)."""
    return [fn(L + " Window Update"), fn(L + " Rows Build"), fn(L + " Rows Y"), fn(L + " Measure"),
            fn(L + " Init Tile", [param("tile", "object:/Script/UMG.UserWidget"), param("kind", "int"), param("ref", "int")]),
            fn(L + " Init Head", [param("head", "object:/Script/UMG.UserWidget"), param("ref", "int")])]
