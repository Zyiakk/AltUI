# How the game finds mods

The game has its own mod loader, and it is table-driven: a pak is a mod because it carries a table that says so, and everything the mod adds – clothes, hairstyles, skins, make-up, levels – arrives as rows appended to the game's own tables. Once you know the handful of names involved, a mod stops being magic.

This page covers what makes a pak a mod, which tables it can bring, the two folders paks can live in, and why two replacers for the same thing can never coexist.

## A mod is a pak with a table

Three things have to line up:

* The pak's content lives under `/Game/Mod/<ModName>/`.
* The **folder name equals the pak name**: `Body_Curvy.pak` carries `/Game/Mod/Body_Curvy/…`.
* Inside it sits `TKA_Mod_Table`, a data table whose row structure is `/Game/Project/Tables/DLC_Struct`. Its row is the mod's entry, so it has one.

That row has four fields:

| Field | Meaning |
|---|---|
| `Caption` | the name shown for the mod |
| `Desc` | a description |
| `Version` | a float, yours to use |
| `Tables` | array of names: which of the mod's tables the loader should read |

At startup the game mounts the paks it finds and then, **for every mounted pak**, looks for `/Game/Mod/<pak name>/TKA_Mod_Table` and merges its row into `/Game/Project/Tables/DLC_MainTable` (the row name is the pak's name without the extension). That is what makes a pak a mod: no such table, no row, and the game knows nothing about the pak even though its files are mounted. Afterwards the rows of the tables listed in `Tables` are appended to the game's own tables. From that moment a modded piece of clothing is an ordinary row like any other – which is worth remembering, because it means nothing in the game's data says where a row came from except that mod table.

You can write `TKA_Mod_Table` without the editor; see [building a table from scratch](paks-and-assets.md#building-a-table-from-scratch).

## The tables a mod can bring

The names are fixed. An entry in `Tables` makes the loader look for the matching asset in your mod folder:

| `Tables` entry | Asset in your mod folder | Row structure | What it adds |
|---|---|---|---|
| `Clothes` | `Mod_ClothesTable` | `ClothesStruct` | clothing pieces |
| `ClothesGroup` | `Mod_ClothesGroup` | `ClothesGroupStruct` | groups the pieces belong to |
| `Hairstyle` | `Mod_HairstyleTable` | – | hairstyles |
| `Skin` | `Mod_SkinTable` | `SkinStruct` | skins |
| `Makeup` | `Mod_MakeupTable` | – | make-up |
| `Eyes` | `Mod_EyesTable` | – | eyes |
| `Animation` | `Mod_AnimationTable` | – | animations |
| `Levels` | `Mod_LevelTable` | `LevelStruct` | challenge maps |

A clothing row carries the fields that decide where the piece ends up: `TypeName` is the slot, `Group` the group it belongs to, `ColorAdjustable` whether the colour can be changed, and `Quality` a rating the game keeps for the piece. A level row takes the level name as its row name and the mod folder as `Path`.

`Tables` may be empty, and often is. The list is only about the *content* tables above; `TKA_Mod_Table` itself is what gets the pak listed and is always needed. A mod with an empty `Tables` is a pak the game lists and mounts without adding anything to its own tables – which is exactly what a body mod is: the mesh is loaded by path, by whoever asks for it.

## Two folders, and `_P`

| Folder | Mounted by | Used for |
|---|---|---|
| `TheKillingAntidote/Mods/` | the game's loader | mod paks as described above |
| `TheKillingAntidote/Content/Paks/~mods/` | the engine, at startup | paks that replace assets the game ships |

The difference is *when*, not *whether*: the loader walks every mounted pak, so a mod pak in the engine's folder is listed as well. What the engine's folder buys you is that the pak is in place before the game's own code runs, which is what a pak that replaces a game asset needs. A mod pak belongs in the loader's folder simply because that is where players expect it.

Those two are not the only sources: the game also mounts what the player is subscribed to on the Steam Workshop, from Steam's own folder, and the loader treats those paks like any other.

A pak file whose name ends in `_P` is mounted with a higher priority than its siblings. When two paks provide the same path, the one mounted later and with the higher priority wins – that is the mechanism behind every override pak in this game.

## Replacers and why they collide

A pak whose mount point targets a path the game itself uses does not add anything; it **replaces** what is there. The engine maps one path to exactly one pak, so with two such paks installed, one of them silently wins and the other has no effect. Nothing at runtime can switch between them, because as far as the engine is concerned the loser does not exist.

This is why body mods used to be an either-or choice: every body replacer writes to the same mesh path. The same applies to any pair of mods that replace the same asset – two mods that both replace the player blueprint, or the same table, cannot be used together, whatever order you install them in.

## Turning a replacer into a mod

The way out is to stop replacing and start adding: put the asset under your own path and let something load it from there. `scripts/bodypak.py` does this for body replacers, and the sequence generalises:

1. Read the original pak and find the asset (for a body: the mesh at the game's path).
2. Copy its bytes unchanged into a new pak under `/Game/Mod/<ModName>/`.
3. Rewrite the asset's imports so the references that pointed into the old location now point into the new one – the mesh keeps every byte of its export data, only the table of names it refers to changes.
4. Bring along what the asset needs from the same pak: materials, an animation blueprint.
5. Add a `TKA_Mod_Table` with one row, so the loader lists the pak.

The result is a mod that can be installed beside any number of others. Something still has to load the asset at runtime – for bodies that is AltUI, see [what AltUI reads from a mod](altui-integration.md) – but the collision is gone.

For bodies there is a naming rule that comes from that side: the mod name has to match `Body_[A-Za-z0-9_]+`, case-sensitive.

## Where it goes wrong

* **Folder name and pak name differ.** The loader looks for the mod's tables inside the folder named after the pak. Rename one and the mod is listed with nothing in it.
* **A table is not in `Tables`.** The asset is in the pak, the rows never arrive. This fails quietly.
* **Row names collide.** Rows from all mods land in the same game tables. Two mods that use the same row name for different things will not both work, and the one that loses depends on mount order. Prefix your row names.
* **The wrong folder for an override.** A pak that replaces a game asset has to be mounted before the game reads that asset, so it belongs in `~mods/`; in the loader's folder it may be too late.
* **Replacing where adding would do.** Every asset you replace is an asset no other mod can touch. Replace the smallest thing that gets you there, and prefer your own path.
