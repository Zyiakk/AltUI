# Editor assets

Two assets from `AltUI.pak` to build a body mod against in the Unreal Editor, so it arrives ready for AltUI's
**Body Shape** tab without going through `bodypak.pyz`. Both are needed while you build only: in the finished game
they are loaded from `AltUI.pak`, which the player has installed.

## This is an extra version of your body, not a replacement

A body built this way runs with AltUI and only with AltUI. It is not a replacer: its mesh sits under its own path
(`/Game/Mod/Body_<Name>/Female`) instead of the game's, and nothing but AltUI ever puts it on Jodi. Installed
without AltUI, the pak simply does nothing.

That is the point of the format – any number of such bodies can be installed side by side and switched in the panel,
where replacers all overwrite the same file and only one of them can win. But it means the AltUI version is a second
file you offer next to your normal replacer, for the players who use AltUI, not a new form of your mod for everyone.

## How AltUI uses a body mod

A body mod is a normal TKA mod whose name starts with `Body_` (case-sensitive, `Body_[A-Za-z0-9_]+`). AltUI gives
every such mod a chip in the Body Shape tab and loads three things from it:

* `/Game/Mod/Body_<Name>/Female` – the body mesh, put on Jodi when the chip is picked.
* the mesh's **Post Process Anim Blueprint** – has to be `ABP_BodyScale`, the blueprint whose variables the shape
  sliders drive. A body without it is still selectable and wearable, but its sliders stay off.
* `/Game/Mod/Body_<Name>/Body_Scale` – a one-row data table with the body's own bone scales, the starting point the
  sliders multiply. Its row structure is `S_BodyScale`.

## `S_BodyScale.uasset`

A User Defined Struct with one `Vector` per bone group, and no references besides engine types – it opens in any
Unreal Engine 4.27 project.

**Where the file goes:** `Content/Mod/AltUI/S_BodyScale.uasset`, that exact path. The struct's internal member names
are derived from `/Game/Mod/AltUI/S_BodyScale`, and your table stores its row structure under the same path; moving
or renaming the file breaks both.

**Building the table**

1. Copy the file into `Content/Mod/AltUI/` and start the editor.
2. In your mod folder `/Game/Mod/Body_<Name>/` – the one holding the body mesh as `Female` – create a **Data Table**
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

**Using it:** open your body mesh (`/Game/Mod/Body_<Name>/Female`), and in its asset details set **Post Process Anim
Blueprint** to `ABP_BodyScale`. That is the whole hook-up; the sliders work on the body from then on.

**If your body has a post-process blueprint of its own** – some bodies get their shape from one instead of from the
mesh – note that a mesh has room for exactly one. Put that blueprint's net bone scales into the `Body_Scale` row,
point the mesh at `ABP_BodyScale` and leave your own blueprint out of the pak: the body then looks the way it did,
with the sliders on top. Keeping your own blueprint is a valid choice too – the body works, only without the shape
sliders.

## Packing

Cook and pack **your mod folder only** (`/Game/Mod/Body_<Name>/`). Both files here live outside it, under
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
