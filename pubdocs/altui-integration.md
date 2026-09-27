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

* the mod name starts with `BodyAltUI_` (`BodyAltUI_[A-Za-z0-9_]+`, case-sensitive). `Body_` is what releases up to 1.4.0 wrote and is still read; where one body is installed under both names, the `BodyAltUI_` one is listed and the other ignored
* the mesh sits at `/Game/Mod/BodyAltUI_<Name>/Female`
* optionally, a one-row table `Body_Scale` next to it describes the body's own bone scales
* optionally, the mesh points at `ABP_BodyScale` as its post-process animation blueprint, which is what makes the shape sliders work on it

There are two ways to get there: convert an existing replacer with `bodypak.pyz` – the players' guide is [installing body mods](../BODY_MODS.md) – or build the mod in the Unreal Editor against the two assets in [uassets/](../uassets/README.md), which is the route if the body is yours and you would rather not round-trip through a converter.

Either way the result works only with AltUI installed: the mesh is under your own path, and without AltUI nothing loads it. It is a second file to offer beside your replacer, not a replacement for it.

## Weapons

A weapon mod is not a row in a game table either; it is a mod of its own, with a table AltUI reads:

* the mod name starts with `WeaponAltUI_` - what AltUI scans for, and a name no ordinary weapon mod picks by accident
* everything sits under `/Game/Mod/WeaponAltUI_<Name>/`, with a `TKA_Mod_Table` whose single row is named like the folder – and whose `Tables` column stays **empty**: AltUI loads the weapon tables by path, they are not among the tables the loader appends to the game's own
* a **skin** is a row in `Mod_WeaponSkin` (row structure `S_WeaponSkin`): `Weapon`, `Caption`, `MainTex`, `NormalTex`, `MetallicTex`, `Icon`. Leave a texture out and the game's stays
* a **model** is a row in `Mod_WeaponModel` (row structure `S_WeaponModel`): `Weapon`, `Caption`, `Icon`. The meshes are not named in the table – AltUI loads `/Game/Mod/WeaponAltUI_<Name>/<name of the mesh the game would use>`, so your packages go flat into the mod folder under exactly the game's names, and whatever you leave out keeps its original. That is also how the magazine, the optics, the suppressor and the grip come along
* `Weapon` is an item row name – `Glock`, `UMP45`, `Shotgun` and thirteen more; the full list is in [the editor assets](../uassets/README.md)

Worth knowing before you build a skin: it is applied by setting `MainTex`, `NormalTex` and `MetallicTex` on the weapon's material, and a material without those parameters ignores it silently. The game's own weapon materials have them; the materials that come with a model mod usually do not, so a skin can look perfect on the vanilla weapon and do nothing on top of someone else's model.

Two routes, as for bodies: convert a replacer with `weaponpak.pyz` – the players' guide is [installing weapon mods](../WEAPON_MODS.md) – or build the mod in the editor against the two structs in [uassets/](../uassets/README.md), where a finished example sits in [examples/WeaponAltUI_Example/](../examples/WeaponAltUI_Example/). Either way it works only with AltUI installed: a second file beside your replacer, not a replacement for it.

## Where it goes wrong

* **Rows without a mod table.** The pieces work, but they look vanilla in the panel: no chip, no filter, no attribution.
* **Empty `Caption`.** Your mod is listed under its folder name.
* **Row names that collide with another mod's.** The panel shows whichever row survived the loader, and the player sees one of you missing content. Prefix your row names with something of your own.
* **The wrong slot in `TypeName`.** A piece in the wrong slot list is a piece nobody finds, and it takes the wrong slot when worn.
* **A body mod that is also still a replacer.** If the original replacer stays installed, the game applies it on top and both the converted chip and the "Standard" chip show the same body.
