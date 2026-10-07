# Installing weapon mods with AltUI

This is a step-by-step guide for getting weapon mods into the **Weapons** tab of AltUI, where each weapon gets its
own model and skin, chosen separately and remembered. It covers where weapon mods come from, how to convert them
with `weaponpak.pyz`, where the files go, and what to do when something does not work. There is a complete
walk-through for Windows and one for Linux.

## 1. Why a conversion is needed

A weapon mod for *The Killing Antidote* is a *replacer*: its pak contains files that sit at the game's own paths
under `Project/Models/Weapon/<Weapon>/`. The engine maps a path to exactly one pak, so with two mods for the same
weapon installed one of them silently wins, and nothing – no mod, no menu – can switch between them while the game
runs. Two mods for *different* weapons coexist fine; two for the UMP45 do not.

`weaponpak.pyz` rewrites such a pak into a regular TKA mod pak named `WeaponAltUI_<Name>.pak`. Inside, the files
live under their own path (`/Game/Mod/WeaponAltUI_<Name>/`) instead of the game's, and a small table is added that
AltUI reads. Any number of converted weapon mods can be installed side by side, and you pick one model and one skin
per weapon in the panel.

The textures and meshes themselves are copied unchanged, so the result is exactly what the modder made. Whatever a
mesh needs from the same pak – materials, physics assets – travels with it.

A mod that replaces a weapon's **shot sound** (often a separate `…-SFX.pak` next to the model) is converted the same
way. The sound then has its own section in the panel: you pick it per weapon, independent of the model, and every
other weapon keeps its sound. For the HK416 and the SA58 the game plays the shot through a sound cue, and a replacer
changes only the wave behind it; the converter then copies the game's cue into the mod so the shot keeps fading with
distance. It reads that cue from the game's `pakchunk0-WindowsNoEditor.pak` and looks for it at the usual Steam place –
pass `--game <…/Content/Paks/pakchunk0-WindowsNoEditor.pak>` when the game is installed elsewhere.

## 2. What you need

| | |
|---|---|
| **AltUI** installed and working | `AltUI.pak` in `TheKillingAntidote/Mods/`, plus whatever starts it in `TheKillingAntidote/Content/Paks/~mods/` – the Blueprint Loader or `AltUI_Hook_P.pak` – and **B** opens the panel in a level. See the [README](README.md#installation). |
| **`weaponpak.pyz`** | From the [latest release](../../releases/latest) (also inside `AltUI-<version>.zip`). Put the file anywhere, e.g. your Downloads folder. |
| **Python 3.8 or newer** | Nothing else: no packages, no Unreal tools. Windows: [python.org](https://www.python.org/downloads/windows/) installer, tick **"Add python.exe to PATH"**. Linux: `python3` from your distribution (almost always already there). |
| **The weapon mod's `.pak` file** | Section 3. |
| **A terminal** | `weaponpak.pyz` takes its arguments on the command line. Double-clicking it does nothing useful – a window flashes and closes. Windows: PowerShell or Command Prompt. Linux: any terminal. |

Check Python first:

```
python --version        # Windows
python3 --version       # Linux
```

Anything from `Python 3.8.0` upwards is fine.

## 3. Getting the weapon mod's `.pak`

**Nexus Mods**: download the file and extract the archive (`.zip`, `.rar`, `.7z`). Inside is one `.pak`, sometimes
more:

* A mod may ship **variants** – "choose one to install" folders with a pak each. Convert the one you want; convert
  several under different `--name`s if you want to switch between them in the panel.
* A mod may ship a separate **sound pak** (`…_SFX.pak`). That one is not a weapon model or skin; leave it where it
  is and install it the normal way if you want it.
* An **update archive** may contain only the changed pak. Use the newest one.

**Steam Workshop**: the pak sits under
`steamapps/workshop/content/2254890/<id>/`. Copy it out; do not convert it in place.

## 4. Converting

```
python  weaponpak.pyz <Original.pak> [--name <Name>] [--title "Display name"] [--weapon <Weapon>] [--out <folder>] [--force] [--game <pakchunk0>]     (Windows)
python3 weaponpak.pyz <Original.pak> [--name <Name>] [--title "Display name"] [--weapon <Weapon>] [--out <folder>] [--force] [--game <pakchunk0>]     (Linux)
```

| Option | What it does | Default |
|---|---|---|
| `--name` | The part after the prefix. The pak becomes `WeaponAltUI_<Name>.pak` and the mod folder inside carries the same name. Letters, digits and `_` only – no spaces, no hyphens, no dots. | Taken from the input file name, with every other character turned into `_`. |
| `--title` | The text on the mod's chip and in the game's "Installed DLC" list. Any text, spaces allowed. | The name. |
| `--weapon` | Which of the game's weapons this mod is for. Only needed when the converter cannot tell – see below. | Read from the folder the mod replaces. |
| `--out` | Where to write the converted pak. | Next to the input file. |
| `--force` | Overwrite an existing output pak. | Off; the converter stops instead. |
| `--game` | The game's `pakchunk0-WindowsNoEditor.pak`. Only needed for a shot sound of the HK416 or SA58, and only when the game is not at the usual Steam place. | The usual Steam install path. |

### When `--weapon` is needed

The converter reads the weapon from the folder the mod replaces, `Project/Models/Weapon/<Weapon>/`, or from the shot
sound it replaces. That works for every gun. Two of the game's gun folders are named differently from the weapon in
them – `m1014` is the `Shotgun`, `mgl` the `GrenadeLauncher` – and the converter knows that too.

**Melee weapons always need `--weapon`.** The game keeps all six of them in one folder, `Project/Models/Weapon/Meelee/`
(spelled that way), so the folder does not say which one a mod replaces, and the converter stops with
`cannot tell which weapon this is (folders: meelee, …) - use --weapon <name>`. The same happens with a mod whose files
sit in a folder of its own or that covers more than one weapon. Which weapon a melee mod replaces usually says its page
or its file name (`RockGuitar_PipeWrench.pak`); after the conversion, the line `meshes:` shows the game's mesh it took
(see [Reading the output](#reading-the-output)), which should match the table:

| In the game | `--weapon` | The game's mesh the mod replaces |
|---|---|---|
| Knife | `Knife` | `KnifeCombat` |
| Fire Axe | `Hatchet` | `hatchet` |
| Machete | `Machete` | `SM_Machete` |
| Adjustable Wrench | `Wrench` | `SM_Wrench` |
| Pipe Wrench | `MonkeyWrench` | `SM_MonkeyWrench` |
| Hammer | `IronHammer` | `SM_IronHammer` |

Windows:

```
python weaponpak.pyz SomeKnife.pak --weapon Knife --name SomeKnife --title "Some knife"
python weaponpak.pyz SomeAxe.pak --weapon Hatchet --name SomeAxe --title "Some axe"
python weaponpak.pyz SomeMachete.pak --weapon Machete --name SomeMachete --title "Some machete"
python weaponpak.pyz SomeWrench.pak --weapon Wrench --name SomeWrench --title "Some wrench"
python weaponpak.pyz SomePipeWrench.pak --weapon MonkeyWrench --name SomePipeWrench --title "Some pipe wrench"
python weaponpak.pyz SomeHammer.pak --weapon IronHammer --name SomeHammer --title "Some hammer"
```

Linux: the same with `python3`.

The guns' names, for the rare case they are needed: `Glock`, `Revolver`, `DesertEagle`, `Shotgun`, `UMP45`, `HK416`,
`SA58`, `Bow`, `Speargun`, `GrenadeLauncher`. The names are case-sensitive.

### Reading the output

A **skin** mod prints one line – the pak, the weapon it is for, and its size:

```
WeaponAltUI_MySkin.pak  (UMP45, 6124543 bytes)
```

A **model** mod also lists the meshes it took over:

```
WeaponAltUI_MyShotgun.pak  (Shotgun, 18607771 bytes)
  meshes: SM_Shotgun, Shotgun
```

`skipped:` lines name files the converter left out because nothing in the pak uses them – usually leftovers from
the modder's project:

```
WeaponAltUI_MyPistol.pak  (Glock, 9786337 bytes)
  meshes: Ammo_AmmoEmpty, Ammo_AmmoFull, Glock, Glock_Static
  skipped: Models/Weapon/Glock/Materials/Cartridge_Mat_009.uasset
```

A **sound** mod names the sound the weapon will fire with:

```
WeaponAltUI_G36CSound.pak  (HK416, 19150 bytes)
  sound: HK416_Shot_Cue
```

Skipped files are normal. What matters is that the `meshes:` line (for a model mod) is there and that no error
stopped the run. A `WeaponAltUI_<Name>_build.json` next to the pak records everything the converter did.

## 5. Installing the converted pak

1. Copy `WeaponAltUI_<Name>.pak` into `TheKillingAntidote/Mods/` – the same folder `AltUI.pak` is in. Do **not**
   rename the file: the game derives the mod's name from it, and AltUI only reads paks whose name starts with
   `WeaponAltUI_`.
2. **Take the original replacer out of the game folder** - `Mods/` and `Content/Paks/~mods/`. As long as it is
   there it keeps replacing the game's weapon, and you see its model no matter which tile you pick in the panel.
3. Start the game. In the **main menu**, the "Installed DLC" list now contains an entry with the title you chose.
   That is the game confirming the pak was mounted; if it is missing there, AltUI cannot see it either.
4. Load a level, press **B**, open **Weapons**.

Repeat for every weapon mod you want. Each needs its own `--name`.

## 6. In the game

The Weapons tab lists one entry per weapon of the game. Pick a weapon, and you get two rows of tiles:

* **Models** – the game's own, plus one tile per installed model mod for that weapon.
* **Skins** – the game's gun paints, plus one tile per installed skin mod.

Model and skin are chosen independently, so a modded model can wear any skin. The choice is remembered per weapon
(in `Saved/SaveGames/AltUI.sav`, AltUI's own save – nothing is written into the game's saves) and re-applied when
the weapon is picked up again.

One thing to expect: **a skin will often do nothing on a modded model.** A skin works by setting the texture
parameters `MainTex`, `NormalTex` and `MetallicTex` on the weapon's material. The game's own weapon materials have
those parameters; the materials that come with a model mod usually bring their own and do not. The tile's context
menu has **"Force skins onto this model"** for exactly this case – it puts the game's material on the modded mesh so
skins and gun paints bite again, at the cost of the mod's own look.

## 7. Walk-throughs

### 7a. Windows – a Nexus weapon mod

Example: a mod archive `SomeRevolver.zip` containing `SomeRevolver.pak`.

1. **Extract the archive** (right-click → Extract All). You get the `.pak`.
2. **Put `weaponpak.pyz` and the pak in the same folder**, say `Downloads`.
3. **Open PowerShell there**: in Explorer, click the address bar, type `powershell`, press Enter.
4. **Convert**:

   ```
   python .\weaponpak.pyz .\SomeRevolver.pak --name SomeRevolver --title "Some Revolver"
   ```

   Windows' "Extract All" normally unpacks into a subfolder named after the archive, so the pak may be at
   `.\SomeRevolver\SomeRevolver.pak` – write the subfolder into the path, in quotes if it contains spaces.

5. **Check the output.** It names the pak, the weapon and the meshes.
6. **Copy** `WeaponAltUI_SomeRevolver.pak` into
   `…\steamapps\common\TheKillingAntidote\TheKillingAntidote\Mods\`.
7. **Delete the original** `SomeRevolver.pak` from that folder if you had installed it before.
8. Start the game, press **B**, **Weapons**, pick the Revolver – the new model is a tile there.

### 7b. Linux – a Steam Workshop weapon mod

Example: a subscribed Workshop mod for the shotgun. `<item id>` is the number at the end of its Workshop URL.

1. **Find the pak**:

   ```
   ls ~/.steam/steam/steamapps/workshop/content/2254890/<item id>/
   ```

2. **Convert it** into your Downloads folder:

   ```
   python3 ~/Downloads/weaponpak.pyz \
       ~/.steam/steam/steamapps/workshop/content/2254890/<item id>/SomeShotgun.pak \
       --name SomeShotgun --title "Some Shotgun" --weapon Shotgun --out ~/Downloads
   ```

   `--weapon` is in there because some mods spell the folder they replace differently from the weapon's name, and
   the converter then cannot map it. Without it you get `cannot tell which weapon this is (folders: …) - use
   --weapon <name>`.

3. **Install**:

   ```
   cp ~/Downloads/WeaponAltUI_SomeShotgun.pak \
      ~/.steam/steam/steamapps/common/TheKillingAntidote/TheKillingAntidote/Mods/
   ```

4. **Take the original out of the game folder**, or it keeps replacing the shotgun whatever you pick in the panel.

### 7c. Several mods for the same weapon

That is the point of the format: convert each one under its own `--name`, install all of them, and switch in the
panel. Only the original replacers have to go.

## 8. Updates and removing

* **New version of a weapon mod:** download it, run the same command with `--force`, replace the pak in `Mods/`.
  The name stays the same, so your saved choice keeps pointing at it.
* **Removing a mod:** delete `WeaponAltUI_<Name>.pak` from `Mods/`. If it was the selected model or skin, the
  weapon goes back to the game's own.

## 9. Troubleshooting

### Converter messages

| Message | What it means |
|---|---|
| `no weapon textures or meshes in this pak (expected Models/Weapon/<weapon>/…)` | Not a weapon mod, or it replaces something else. Check that you picked the right pak – a sound pak (`…_SFX.pak`) gives this too. |
| `cannot tell which weapon this is (folders: …)` | A melee mod (`folders: meelee` – all melee weapons share that folder), or the mod's folder name is not one the converter knows. Pass `--weapon <Weapon>`; see [When `--weapon` is needed](#when---weapon-is-needed). |
| `unknown weapon '…' (known: …)` | The `--weapon` you passed is not one of the game's weapon names. |
| `the pak has skin textures but no base colour texture (…_BaseColor / _BC / _D)` | A skin needs a base colour texture; this pak has only extras. Nothing to convert. |
| `the pak brings its own skeleton (…)` | The mod ships a skeleton of its own. Converting it would leave the weapon standing still in the game, because the animations are made for the original skeleton – so the converter stops instead. |
| `invalid name (allowed: A-Z a-z 0-9 _)` | `--name` contains a space, hyphen, dot or other character. Put the pretty text into `--title`. |
| `target already exists (--force to overwrite)` | There is already a pak of that name in the output folder. Add `--force`. |
| `verify failed: …` | The converter checked its own output and found a problem. Please report it with the message and the mod. |

### In the game

* **The mod is not in "Installed DLC".** The pak is not being mounted: wrong folder, or the file was renamed. It
  has to be in `Mods/` and keep its `WeaponAltUI_` name.
* **It is in "Installed DLC" but no tile appears.** Check that you are looking at the right weapon – a mod shows up
  only under the weapon it replaces, named in the converter's output.
* **The modded model shows, but a skin does nothing.** Expected on many model mods – see section 6, and try "Force skins onto
  this model" in the tile's context menu.
* **The weapon looks like the mod even with the game's model picked.** The original replacer is still there - look
  in `Mods/` and in `Content/Paks/~mods/`.

## 10. Building an AltUI weapon mod in the editor

If the mod is yours, you can build the AltUI version directly instead of converting a replacer: the three structs to
build against are in [`uassets/`](uassets/README.md), and a finished example – one texture, one table row – is in
[`examples/WeaponAltUI_Example/`](examples/WeaponAltUI_Example/).
