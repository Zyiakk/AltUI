# Making a mod that AltUI reads well

AltUI adds a panel beside the game's own wardrobe that lists everything installed – vanilla and modded, sorted by slot, with chips per mod and a search. The mirror wardrobe keeps working as it always did. It builds that list from the same tables the game reads, so a mod that follows the conventions on this page needs nothing extra to show up correctly. Most of what follows is simply *fill the fields in*, but each field maps to something the player sees.

This page assumes you know [how the game finds mods](mods-and-tables.md).

## What AltUI reads from a mod

Two things, both described on that page:

* `DLC_MainTable`, which the loader fills with one row per mounted mod pak. That is AltUI's list of installed mods, and the row name is your mod folder.
* Your mod's own tables – `Mod_ClothesTable`, `Mod_HairstyleTable`, `Mod_SkinTable`, `Mod_MakeupTable`, `Mod_EyesTable` – which AltUI walks to find out **which rows came from which mod**.

That second point is the one that catches people. The loader appends your rows to the game's tables, and after that nothing distinguishes them from the game's own. AltUI attributes an item to your mod by finding its row name in one of your mod tables. A piece that reaches the game some other way – appended by a replacement of a game table, say – shows up as vanilla, in the right slot, but with no mod chip and no way for the player to filter by your mod.

So: ship the tables, list them in `Tables`, and keep your row names in them.

## What the player sees, field by field

| Where it comes from | What it becomes in the panel |
|---|---|
| `Caption` in your `TKA_Mod_Table` row | the label of your mod's chip, and the mod name in every tooltip |
| the row name in `DLC_MainTable` (your mod folder) | the fallback label when `Caption` is empty, and what the search matches |
| `TypeName` in a clothing row | which slot list the piece appears in |
| `Group` in a clothing row | the group chip the piece sits under, and the group filter |
| `ColorAdjustable` | whether the colour swatches are offered for the piece |
| the row name of the piece | the tile's name, unless the player renames it |

Two practical consequences. Fill in `Caption` – without it the chip carries the pak's file name, and a name you chose reads better in the panel than `SomePack_v3_final`. And give related pieces the same `Group`: groups are how a player with a long list of installed pieces finds yours.

Players can rename anything in the panel to whatever they like. Those names live in their save file and never touch your mod, so a clumsy row name is not fatal – but it is what everyone else sees first.

## Bodies

A body mod is not a clothing row; it is a mesh AltUI loads on demand, and it needs its own shape:

* the mod name starts with `Body_` (`Body_[A-Za-z0-9_]+`, case-sensitive)
* the mesh sits at `/Game/Mod/Body_<Name>/Female`
* optionally, a one-row table `Body_Scale` next to it describes the body's own bone scales
* optionally, the mesh points at `ABP_BodyScale` as its post-process animation blueprint, which is what makes the shape sliders work on it

There are two ways to get there: convert an existing replacer with `bodypak.pyz` – the players' guide is [installing body mods](../BODY_MODS.md) – or build the mod in the Unreal Editor against the two assets in [uassets/](../uassets/README.md), which is the route if the body is yours and you would rather not round-trip through a converter.

Either way the result works only with AltUI installed: the mesh is under your own path, and without AltUI nothing loads it. It is a second file to offer beside your replacer, not a replacement for it.

## Where it goes wrong

* **Rows without a mod table.** The pieces work, but they look vanilla in the panel: no chip, no filter, no attribution.
* **Empty `Caption`.** Your mod is listed under its folder name.
* **Row names that collide with another mod's.** The panel shows whichever row survived the loader, and the player sees one of you missing content. Prefix your row names with something of your own.
* **The wrong slot in `TypeName`.** A piece in the wrong slot list is a piece nobody finds, and it takes the wrong slot when worn.
* **A body mod that is also still a replacer.** If the original replacer stays installed, the game applies it on top and both the converted chip and the "Standard" chip show the same body.
