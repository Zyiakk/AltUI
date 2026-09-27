# Editor assets

Seven assets from `AltUI.pak` to build a mod against in the Unreal Editor, so it arrives ready for AltUI without
going through the converters. They are needed while you build only: in the finished game they are loaded from
`AltUI.pak`, which the player has installed.

| Files | For |
|---|---|
| `S_BodyScale.uasset`, `ABP_BodyScale.uasset` | a body for the **Body Shape** tab, without `bodypak.pyz` |
| `S_WeaponSkin.uasset`, `S_WeaponModel.uasset` | a weapon skin or model for the **Weapons** tab, without `weaponpak.pyz` |
| `S_AltUIModEntry.uasset`, `S_AltUIModField.uasset`, `BPI_AltUIMod.uasset` | your mod's settings in the **Mods** tab - see [MOD_UI.md](../MOD_UI.md) |

Bodies come first below, weapons after. The Mods tab has a guide of its own, [MOD_UI.md](../MOD_UI.md): the three
assets go to `Content/Mod/AltUI/` in your project and stay out of your pak, like all the others here.

## This is an extra version of your body, not a replacement

A body built this way runs with AltUI and only with AltUI. It is not a replacer: its mesh sits under its own path
(`/Game/Mod/BodyAltUI_<Name>/Female`) instead of the game's, and nothing but AltUI ever puts it on Jodi. Installed
without AltUI, the pak simply does nothing.

That is the point of the format – any number of such bodies can be installed side by side and switched in the panel,
where replacers all overwrite the same file and only one of them can win. But it means the AltUI version is a second
file you offer next to your normal replacer, for the players who use AltUI, not a new form of your mod for everyone.

## How AltUI uses a body mod

A body mod is a normal TKA mod whose name starts with `BodyAltUI_` (case-sensitive, `BodyAltUI_[A-Za-z0-9_]+`). Paks
from releases up to 1.4.0 carry `Body_` and are still read; where both names are installed for one body, the
`BodyAltUI_` one is listed and the other ignored. AltUI gives
every such mod a chip in the Body Shape tab and loads three things from it:

* `/Game/Mod/BodyAltUI_<Name>/Female` – the body mesh, put on Jodi when the chip is picked.
* the mesh's **Post Process Anim Blueprint** – has to be `ABP_BodyScale`, the blueprint whose variables the shape
  sliders drive. A body without it is still selectable and wearable, but its sliders stay off.
* `/Game/Mod/BodyAltUI_<Name>/Body_Scale` – a one-row data table with the body's own bone scales, the starting point the
  sliders multiply. Its row structure is `S_BodyScale`.

## `S_BodyScale.uasset`

A User Defined Struct with one `Vector` per bone group, and no references besides engine types – it opens in any
Unreal Engine 4.27 project.

**Where the file goes:** `Content/Mod/AltUI/S_BodyScale.uasset`, that exact path. The struct's internal member names
are derived from `/Game/Mod/AltUI/S_BodyScale`, and your table stores its row structure under the same path; moving
or renaming the file breaks both.

**Building the table**

1. Copy the file into `Content/Mod/AltUI/` and start the editor.
2. In your mod folder `/Game/Mod/BodyAltUI_<Name>/` – the one holding the body mesh as `Female` – create a **Data Table**
   with `S_BodyScale` as its row structure and name it `Body_Scale`.
3. Give it exactly one row, named `Default`.
4. Fill in the body's own bone scales. A member left at `0,0,0` is read as `1,1,1`.

**What the values mean.** Each member is the **net** scale of its bone group on the finished body, measured against
the game's body: `1,1,1` leaves the group alone, `1,1.2,1.2` makes it 20 % thicker. X runs along the bone, Y and Z
across it.

Net means the scale the body ends up with, not the value of a single node in a chain: a bone inherits its parent's
scale, so a body whose thighs are at 1.2 and whose calves end up at 1.2 as well has 1.2 in *both* members, not 1.2
and 1.0. AltUI divides each group by its parent group before it sets the bones.

If the body gets its shape from the mesh rather than from scaled bones, leave every member at `1,1,1` – the sliders
then start from the mesh as it is.

| Member | Bones |
|---|---|
| `Breasts` | `Breast_L`, `Breast_R` |
| `GlutesHips` | `Hip_L`, `Hip_R` |
| `Thighs` | `thigh_l`, `thigh_r` |
| `LowerThighs` | `thigh_twist_01_l`, `thigh_twist_01_r` |
| `UpperCalfs` | `calf_l`, `calf_r` |
| `LowerCalfs` | `calf_twist_01_l`, `calf_twist_01_r` |
| `Upperarms` | `upperarm_l`, `upperarm_r` |
| `Lowerarms` | `lowerarm_l`, `lowerarm_r` |
| `Hands` | `hand_l`, `hand_r` |
| `Feet` | `foot_l`, `foot_r` |
| `Waist` | `Morph_Waist` (the game's own waist morph bone) |

The members and their order are part of the struct: a table written with an edited or reordered copy cannot be read
back. Use the file as it is.

## `ABP_BodyScale.uasset`

The post-process animation blueprint that does the scaling: one `ModifyBone` node per bone above, plus three that
translate the root and the feet to keep the soles on the floor when the height and feet sliders move. Its variables are set by AltUI
at runtime – the defaults in the asset scale nothing. It targets the skeleton
`/Game/Project/Character/Jodi/Body/Female_Skeleton`, so it needs the modding kit's project.

**Where the file goes:** `Content/Mod/AltUI/ABP_BodyScale.uasset`, again that exact path – it is the path the game
resolves to `AltUI.pak` at runtime.

**Using it:** open your body mesh (`/Game/Mod/BodyAltUI_<Name>/Female`), and in its asset details set **Post Process Anim
Blueprint** to `ABP_BodyScale`. That is the whole hook-up; the sliders work on the body from then on.

**If your body has a post-process blueprint of its own** – some bodies get their shape from one instead of from the
mesh – note that a mesh has room for exactly one. Put that blueprint's net bone scales into the `Body_Scale` row,
point the mesh at `ABP_BodyScale` and leave your own blueprint out of the pak: the body then looks the way it did,
with the sliders on top. Keeping your own blueprint is a valid choice too – the body works, only without the shape
sliders.

## Packing

Cook and pack **your mod folder only** (`/Game/Mod/BodyAltUI_<Name>/`). Both files here live outside it, under
`/Game/Mod/AltUI/`, so a pak built that way leaves them out by itself – which is what you want, because the copies
in `AltUI.pak` are the ones the game uses.

A pak that does ship its own `/Game/Mod/AltUI/ABP_BodyScale` or `/Game/Mod/AltUI/S_BodyScale` puts them in the place
of AltUI's, for everyone who installs the mod. A blueprint compiled in a different project is not the class AltUI
addresses, so this breaks the shape sliders – for every body, not just yours. The cooker follows the reference from
your mesh, so both assets can turn up in your cooked output; check the file list of the finished pak before you
publish it.

And the hook-up is one more thing tying the pak to AltUI: even if something else loaded the mesh, nothing would set
the blueprint's variables, and the body would show its mesh shape with no bone scaling. Your replacer stays the
version for everyone else.

## Weapons

A weapon mod is built the same way as a body: your assets under your own path, one table AltUI reads, and the
struct from this folder as its row structure. There are two kinds, and a mod can bring both - a **skin** replaces
the textures on the game's weapon, a **model** replaces the meshes.

### This is an extra version of your weapon mod, not a replacement

Built this way, the mod runs with AltUI and only with AltUI. It is not a replacer: nothing in it sits where the
game's own files sit, and nothing but AltUI ever puts it on a weapon. Installed without AltUI, the pak does nothing.

That is the point of the format. Weapon replacers all overwrite the same files under
`Project/Models/Weapon/<Weapon>/`, so only one of them can win, and none can be switched while the game runs. Any
number of the converted kind can be installed side by side, and the player picks one per weapon. But it does mean
this is a second file you offer next to your normal replacer, for the players who use AltUI.

### What every weapon mod needs

* **The mod folder, and the pak, are called `WeaponAltUI_<Name>`** - case-sensitive. That prefix is what AltUI
  scans for, and it says what the pak is: `WeaponAltUI_<Name>` would be a name any weapon mod might pick for itself.
* Everything lives under `/Game/Mod/WeaponAltUI_<Name>/`.
* A `TKA_Mod_Table` there with **one row, named like the folder**. The game's loader writes one row per mounted mod
  pak into `DLC_MainTable`, and that list is where AltUI looks - a mod without this table never appears in it.
  `Caption` becomes the label of your mod's chip.
* In that row, leave **`Tables` empty**. That column names tables the loader appends to the game's own; the weapon
  tables are not among them, AltUI loads them by path out of your folder.
* One table per kind, both optional: `Mod_WeaponSkin` and `Mod_WeaponModel`, next to the mod table.

### `S_WeaponSkin.uasset`

A User Defined Struct with a name, a text and four texture slots, and no references besides engine types - it opens
in any Unreal Engine 4.27 project.

**Where the file goes:** `Content/Mod/AltUI/S_WeaponSkin.uasset`, that exact path. The struct's internal member
names are derived from `/Game/Mod/AltUI/S_WeaponSkin`, and your table stores its row structure under the same path.
Moving it, renaming it or building the struct yourself breaks both - a struct you create by hand gets different
member names, and AltUI cannot read a table written against it.

**Building the table**

1. Copy the file into `Content/Mod/AltUI/` and start the editor.
2. In your mod folder `/Game/Mod/WeaponAltUI_<Name>/`, create a **Data Table** with `S_WeaponSkin` as its row structure
   and name it `Mod_WeaponSkin`.
3. Add one row per skin you offer.

| Column | What goes in |
|---|---|
| `Weapon` | the weapon the skin is for - one of the row names listed further down |
| `Caption` | the name the player sees on the tile |
| `MainTex` | your base colour texture |
| `NormalTex` | your normal map |
| `MetallicTex` | your metallic texture |
| `Icon` | optional; shown on the tile until AltUI has rendered a picture of its own |

Leave out what you do not replace - an empty slot keeps the game's texture.

**Row names are global.** AltUI remembers which mod a skin came from by its row name alone, so two mods with a row
called `Red` overwrite each other's entry. Put your mod name in front: `MyMod_Red`.

**A skin only reaches materials that have those parameters.** It is applied by setting `MainTex`, `NormalTex` and
`MetallicTex` on the material of the weapon. The game's own weapon materials have them; the materials shipped with
a model mod usually do not, and setting a parameter a material does not have does nothing at all - silently. So
your skin shows on the game's weapon and may do nothing on top of someone else's model.

### `S_WeaponModel.uasset`

**Where the file goes:** `Content/Mod/AltUI/S_WeaponModel.uasset` - same rule, same reason as above.

**Building the table:** a **Data Table** with `S_WeaponModel` as its row structure, named `Mod_WeaponModel`, in your
mod folder. One row per model.

| Column | What goes in |
|---|---|
| `Weapon` | the weapon this model replaces |
| `Caption` | the name on the tile |
| `Icon` | optional, as above |

**The meshes are not named in the table.** To put your model on a weapon, AltUI takes the name of the mesh the game
would use and loads `/Game/Mod/WeaponAltUI_<Name>/<that name>`. Is there a package of that name, it is used; is there
none, the original stays.

Two things follow from that:

* Your meshes go **flat into your mod folder**, each package named **exactly** like the game package it replaces -
  no subfolders, no renaming.
* Whatever you leave out keeps its original. That is also how the magazine, optics, suppressor and grip come along:
  ship a package named like the game's magazine and yours is used, leave it out and the game's stays.

**Finding those names** - list the game's pak and look into the weapon's folder:

```
python3 pak11_extract.py "<game>/Content/Paks/pakchunk0-WindowsNoEditor.pak" list | grep -i Models/Weapon/UMP45
```

`pak11_extract.py` is in `scripts/` of this repository and needs nothing but Python 3.

### The weapons

`Weapon` takes one of these 16 row names, the game's own item names:

```
Knife         Hatchet   Machete   Wrench   MonkeyWrench   IronHammer   Glock      Revolver
DesertEagle   Shotgun   UMP45     HK416    SA58           Bow          Speargun   GrenadeLauncher
```

Two of the game's asset folders are named differently from the weapon inside them: `m1014` is the `Shotgun`, `mgl`
the `GrenadeLauncher`. In the table, use the names above whatever the folder is called.

### Packing a weapon mod

Cook and pack **your mod folder only** (`/Game/Mod/WeaponAltUI_<Name>/`). The struct files live outside it, under
`/Game/Mod/AltUI/`, so a pak built that way leaves them out by itself - which is what you want, because the copies
in `AltUI.pak` are the ones the game uses. A pak that ships its own `/Game/Mod/AltUI/S_WeaponSkin` puts it in the
place of AltUI's for everyone who installs the mod, so check the file list of the finished pak before you publish
it. The pak itself goes to `TheKillingAntidote/Mods/`, like any other mod.

### An example to start from

`examples/WeaponAltUI_Example/` in this repository is a complete, working skin mod: one texture, one `Mod_WeaponSkin`
row, one `TKA_Mod_Table` row. Install its pak to watch the entry appear in the Weapons tab, or copy the editor
files into your own project and edit them from there. There is no model example - that would need a mesh, and
everything shipped here is made from scratch.
