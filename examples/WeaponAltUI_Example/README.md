# `WeaponAltUI_Example` - a weapon skin for AltUI

A complete, working skin mod for the **UMP45**, built exactly the way [the editor guide](../../uassets/README.md)
describes. The texture is a hard orange checker with a white diagonal - deliberately artificial, so you can see at a
glance where it lands on the weapon and nobody mistakes it for a skin to actually play with.

## Try it

1. Copy `WeaponAltUI_Example.pak` into `TheKillingAntidote/Mods/`.
2. Start the game, open AltUI, go to the **Weapons** tab and pick the UMP45.
3. An entry **"Example checker"** appears among the skins. Click it, and the weapon wears the pattern.

AltUI has to be installed - this is a mod for AltUI, and nothing else reads it. Remove the pak to get rid of it; it
changes no game file.

## Build your own from it

The three files under `editor/` are the uncooked assets. Copy them into your own Unreal project at
`Content/Mod/WeaponAltUI_<YourName>/`, and copy `S_WeaponSkin.uasset` from [`uassets/`](../../uassets/) into
`Content/Mod/AltUI/` - that one has to sit at that exact path, because the table stores its row structure under it.

| File | What it is | What to change |
|---|---|---|
| `Mod_WeaponSkin.uasset` | the table AltUI reads: one row per skin | your row: `Weapon`, `Caption`, and the textures |
| `T_ExampleSkin.uasset` | the checker texture, wired into the row as `MainTex` | replace with your own; add `NormalTex` / `MetallicTex` if you have them |
| `TKA_Mod_Table.uasset` | what makes the pak a listed mod | the row name must match your folder name, and `Tables` stays empty |

Two rules worth repeating, because both are easy to get wrong and neither fails loudly:

* **The row name is global.** AltUI tells skins apart by row name alone, across every installed mod. This example
  uses `WeaponAltUI_Example_Checker`, not `Checker`, for that reason - put your mod name in front of yours too.
* **A skin only reaches materials that have the parameters.** It is applied by setting `MainTex`, `NormalTex` and
  `MetallicTex` on the weapon's material. The game's own weapon materials have them; the materials that come with a
  model mod usually do not, and setting a parameter that is not there does nothing at all.

Then cook and pack **your folder only** - `S_WeaponSkin` must not travel with your pak, because the copy in
`AltUI.pak` is the one the game uses.

## Not here: a model example

There is no example for a weapon **model** here - that would take a mesh, and a mesh is the one thing this example
cannot make up for you. The procedure is written out in [the editor guide](../../uassets/README.md#weapons); the
short version is that model meshes carry the names of the game packages they replace and sit flat in the mod folder.

## Rebuilding this example

`scripts/weaponexample.sh` generates the texture and the tables, cooks them and writes the pak.
