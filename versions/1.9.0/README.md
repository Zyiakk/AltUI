# AltUI

A replacement wardrobe and appearance UI for *The Killing Antidote* (game version 0.6.x). The vanilla wardrobe gives every mod author their own tab, so with a few clothing mods installed the same kind of item is scattered across a dozen tabs and there is no way to search. AltUI sorts every item from the game and from all installed mods into **one list per slot** (tops, skirts, shoes, …), with search, filters, favourites and hiding – and puts hair, makeup, body and outfits into the same panel. It opens anywhere in a level with **B**; no trips to the wardrobe or the mirror. Next to that: ragdolls to place and pose (copies of Jodi, zombies, people), a Codex with the manual, the game's encyclopedia and the code locks of the level, Jodi's own walk and run speed, and a shot sound of your choice per weapon.

## Installation

`AltUI.pak` holds the whole mod, and one more file has to start it: either the **Blueprint Loader**, a small separate mod that starts any mod built for it, or AltUI's own **hook pak**. Pick one; both together work as well. Files come from the [latest release](../../releases) (also on [Nexus Mods](https://www.nexusmods.com/thekillingantidote/mods/988) and the [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3802875867)); paths are relative to the game installation, e.g. `Steam/steamapps/common/TheKillingAntidote/`.

**With the Blueprint Loader** – AltUI replaces nothing of the game:

| File | Where it comes from | Copy to |
|---|---|---|
| `TKA_BlueprintLoader.pak` | [Blueprint Loader](https://www.nexusmods.com/thekillingantidote/mods/994) | `TheKillingAntidote/Content/Paks/~mods/` (create the folder; the name starts with a tilde) |
| `AltUI.pak` | AltUI release | `TheKillingAntidote/Mods/` |

`AltUI.pak` carries a table the loader reads, so the loader starts the panel. The same loader starts every other mod that ships such a table, which is why this is the way to go if you use more than one mod of that kind.

**Upgrading from an older AltUI: if an `AltUI_Hook_P.pak` is still in `~mods/`, delete it.** The hook claims the camera
manager class for itself, and one from before 1.5.0 does not start the loader – the panel would open without the view moving
aside, and mods built for the loader would stay dead.

**With the hook pak** – no second mod to install:

| File | Copy to |
|---|---|
| `AltUI.pak` | `TheKillingAntidote/Mods/` |
| `AltUI_Hook_P.pak` | `TheKillingAntidote/Content/Paks/~mods/` (create the folder; the name starts with a tilde) |

The hook replaces the game's `TKA_PlayerCameraManager` blueprint and starts the panel from there. Any mod that replaces the same blueprint conflicts with it – the Blueprint Loader is one of them, and that pair is the exception: with both installed the hook wins the class and starts the loader itself, so mods that need the loader keep working.

**What each combination does**

| Installed | What happens |
|---|---|
| `AltUI.pak` alone | nothing starts the panel – **B does nothing** |
| `AltUI.pak` + Blueprint Loader | the loader reads AltUI's table and starts the panel; AltUI replaces nothing of the game (the loader replaces the camera manager class, which is how it works) |
| `AltUI.pak` + `AltUI_Hook_P.pak` | the hook replaces the game's camera manager and starts the panel |
| `AltUI.pak` + both | fine, and nothing is lost. Both replace the same game class, so only one of the two paks wins it – and whichever it is, AltUI starts: through the loader's table, or through the hook, which then also starts the loader itself so that mods built for it keep running |
| the hook or the loader without `AltUI.pak` | nothing – the mod itself is missing |

Either way: start the game, press **B** in a level.

The camera framing beside the open panel does not depend on the hook any more. It attaches to whichever camera manager the level has, the game's included.

If you use the hook, it rarely changes: it only starts the panel, everything else is in `AltUI.pak`. A mod update therefore normally does not need a new hook file – each changelog entry says whether it does. A new hook is only needed when the changelog says so or when a game update replaces the player camera manager. An old hook file must not simply stay behind: it is the one that claims the camera manager class, so it decides what happens – with an outdated one the panel may open without the view moving aside, and a hook from before 1.5.0 does not start the Blueprint Loader, so every mod built for the loader stays dead. Switching to the loader therefore means deleting `AltUI_Hook_P.pak` from `~mods/` or replacing it with the current one.

**Uninstall:** delete the files you copied – `TheKillingAntidote/Mods/AltUI.pak`, and `TheKillingAntidote/Content/Paks/~mods/AltUI_Hook_P.pak` if you use the hook (the Blueprint Loader only if no other mod needs it). AltUI keeps its own data in the game's save folder, on Windows `%LOCALAPPDATA%\TheKillingAntidote\Saved\SaveGames\`. To remove everything, delete these there too:

| File or folder | Content |
|---|---|
| `AltUI.sav` | settings and choices |
| `AltUI_Looks.sav` | saved looks |
| `AltUI_Faces.sav` | saved faces |
| `AltUI_Names.sav` | your own names |
| `AltUI_Ragdolls.sav` | ragdoll scenes and poses |
| `AltUI/` | photos of looks, faces and appearance presets |
| `WeaponIcons/` | weapon tile pictures |

Nothing else is touched – clothes, outfits, makeup and hair are written through the game's own save files.

## What it does

| Tab | Content |
|---|---|
| **Clothes** | Every item the game and your mods know, grouped by slot, sub-tabs per mod (collapsible), search (also by mod and group name), "owned only" / "favourites only" / "vanilla only" filters, favourites, colour via the game's palette, colour reset, backpack in/out, hide items; right-click: only this group, view mod content. |
| **Outfits** | The game's outfit presets, with names (right-click → rename). |
| **Looks** | A complete look – clothes with colours, hairstyle and colour, makeup, eyes, skin, body sliders, body mod, face – saved with an in-game full-body photo, taken from the front or as you see her. Apply, update, rename, delete. |
| **Backpack** | What Jodi wears and carries: wear, remove, repair, back to wardrobe, clean up. |
| **Coiffure** | All hairstyles, hair colour, 14 natural hair colour presets, factory reset. |
| **Poses** | Every action animation the game and your pose mods know (the list behind the phone's "rhythm" app), one tile per pose with its title, chips per mod, search, favourites, hide; click plays the pose, click again or "Stop pose" stops it. |
| **Weapons** | One entry per weapon, melee weapons included; for each of them its model, its skin and its shot sound, chosen separately: mesh mods above, below the game's own gun paints (no spray can needed) and every installed skin mod; the shot sounds: the weapon's own and every installed sound made for it (a click plays it; a mounted suppressor with a sound of its own still wins). All three kinds are converted with `weaponpak.pyz`; the choice is remembered and re-applied when the weapon is picked up again or taken out of the storage box. The list counts models and skins per weapon. |
| **Appearance** | Skin, every makeup type, eyes, appearance presets with icons (save, update, rename, delete). |
| **Body Shape** | Breast / waist sliders, a switcher for installed body mods (below) and – for converted bodies – bone-scale sliders: scale, bust, waist extra, glutes/hips, thighs, calves, arms, hands, feet, saved per body. |
| **Face** | Jodi's facial expression: the game's expressions (relaxed, focused, smile, pain, fright, tired, suffering), gaze and mouth shapes as sliders. A ticked entry keeps its value, also in poses; an unticked one is left to the game's animation. Expressions blended (at most 100 % together) or added up, "Close mouth", saved faces with a photo ("View content" lists their values). |
| **Mods** | The settings of other mods that register there – their entries on the left, the chosen one's toggles, sliders, numbers, choices, colours, text fields, info lines, keys and buttons on the right. Only shown when such a mod is installed; see [Settings of other mods](#settings-of-other-mods). |
| **Options** | In categories (list on the left). Tabs you do not use can be switched off; the tab bar shows text, icons or both (icon left or right). What goes into the quick menu, its key and its opacity. Movement: Jodi's own walk and run speed (50–200 %; crouching and jumping stay as they are). Panel key, language, scroll speed, tile size (and an own size for outfit, look and ragdoll tiles, how many pieces an outfit tile shows), length of group names and height of the group row, screen share kept free for Jodi, camera FOV / distance / pan, colour scheme and opacity (schemes saved under a name), "underwear may be taken off", not-owned items locked / greyed / like owned, slot conflicts (free the game's bra-vs-shirt-style pairs), merge groups / mods with the same name, tooltip options. |
| **Manage** | Your own display names for mods, groups (mod and vanilla), clothes, hairstyles, skins, make-up, poses and appearance presets – used everywhere in the panel and by the search; "only mods" filter, search; as in Clothes, chips filter the list by mod or group and a search field narrows down the chips; revert per row. Exportable/importable as JSON with `altui_names.pyz` (see below). |
| **Ragdolls** | Figures with physics to place and pose in the level: copies of Jodi (standing and frozen in her pose, with everything she wears; a look via "Spawn as ragdoll"), every kind of zombie from the encyclopedia with its variants, the nurse and a survivor. Each figure active (falls, can be thrown) or frozen (keeps its pose); 17 joints each locked, free or movable. Mouse beside the panel: drag a frozen figure to move it (wheel lifts it), drag an active one by a body part, right drag turns, Shift + click locks / frees a joint, Shift + right click makes it movable – dragging a body part below it then poses only that part. Poses saved per kind of figure, scenes saved per level (`AltUI_Ragdolls.sav`). |
| **Codex** | The AltUI manual in all seven languages; the encyclopedia from Jodi's office computer (unlocked entries, or all with a switch under Options › General); the code locks of the current level, nearest first, each code hidden until clicked. |

Undo / redo (5 steps) in the status bar; tooltips show which mod an item comes from. The panel opens on the tab it was left on, with the same slot, category or weapon chosen. Languages: English, German, Chinese, Russian, Spanish, Polish, French (auto-detected, switchable).

**Controls:** **B** opens / closes (changeable in Options), **Esc** closes. Hold **4** (changeable) for the quick menu: a wheel of the items you picked in Options (or with a right click on a tile, a tab or a mod's entry), let go on one to run it. Left click selects / wears / applies, right click opens the context menu, mouse wheel scrolls. While the panel is open Jodi cannot walk; drag on the background to turn the camera, click on Jodi and drag to turn her (she turns back when the panel closes), +/− changes the distance in 5 % steps, the mouse wheel over Jodi in 4 % steps. The three round buttons above +/− open a free camera (mouse turns, W A S D / Q E move, Shift faster, wheel = speed, within 6 m of Jodi, stops at walls; Esc back), the game's photo mode (Esc back) and the ragdolls mode (panel away, camera free with W A S D / Q E, Shift + wheel = speed, drag on nothing turns it; the figures under the mouse are moved and posed as beside the panel; Esc or B back).

## Body mods

Body replacer paks all overwrite the same game file, so only one can be active and nothing can switch between them. `bodypak.pyz` (in the release, Python 3.8+, no packages; GPL-3, see LICENSE) converts a replacer into a regular mod pak that keeps the mesh under its own path; any number of converted bodies can be installed side by side and appear as chips in the Body Shape tab. The choice is remembered and re-applied on every level load. Step-by-step instructions with a Windows and a Linux walk-through: [BODY_MODS.md](BODY_MODS.md).

```
python3 bodypak.pyz <Original.pak> [--name BodyAltUI_<Name>] [--title "Display name"] [--out <folder>] [--force]
python3 bodypak.pyz SomeBodyReplacer.pak --name BodyAltUI_Some --title "Some body"
```

`--name` must match `BodyAltUI_[A-Za-z0-9_]+` (default: derived from the file name); `--title` is the chip text. Copy the resulting `BodyAltUI_<Name>.pak` to `TheKillingAntidote/Mods/` and remove the original replacer from `Mods/` or `~mods/` (or keep it in `~mods/` – it then becomes the "Standard" chip). The mesh is taken byte for byte, together with the assets it uses from the same pak – some bodies get their shape from their own animation blueprint (bone scaling) rather than from the mesh, and without it the converted body would look like the standard one. Skin textures and other files the mesh does not use are left out; the converter lists them. Pak versions 3–11, uncompressed / zlib / Oodle (Kraken); the Oodle decoder is pure Python, ported from [ooz](https://github.com/powzix/ooz) (GPL-3).

**For body-mod authors.** A body can also be built for AltUI directly in the Unreal Editor, without the converter. [`uassets/`](uassets/) holds the two assets that takes – the row structure of the `Body_Scale` table, which carries the body's own bone scales, and the post-process animation blueprint the shape sliders drive – and [uassets/README.md](uassets/README.md) describes where they go and what the mod folder has to look like. Such a pak needs AltUI and does nothing without it, so it is an extra file next to the replacer, not a replacement for it.

## Weapon mods

Weapon mods replace the same files under `Project/Models/Weapon/<Weapon>/`, so two for one weapon exclude each other and nothing can switch between them in the game. `weaponpak.pyz` (in the release, Python 3.8+, no packages; GPL-3, see LICENSE) converts such a replacer into its own `WeaponAltUI_<Name>.pak`; any number of them can be installed side by side, and model and skin are picked per weapon in the Weapons tab and remembered. Step-by-step instructions with a Windows and a Linux walk-through: [WEAPON_MODS.md](WEAPON_MODS.md).

```
python3 weaponpak.pyz <Original.pak> [--name <Name>] [--title "Display name"] [--weapon <Weapon>] [--out <folder>] [--force]
python3 weaponpak.pyz SomeWeaponReplacer.pak --name SomeGun --title "Some gun"
```

`--name` takes the part after the prefix (letters, digits and `_`; default: derived from the file name), `--title` is the chip text, and `--weapon` is only needed where the mod's folder name does not say which weapon it is for. A pak can bring a skin, a model, or both - it becomes one mod with one row per kind. Copy the result to `TheKillingAntidote/Mods/` and remove the original replacer, or it keeps overriding the weapon whatever you pick in the panel.

**When `--weapon` is needed.** The converter reads the weapon from the folder the mod replaces, `Project/Models/Weapon/<Weapon>/`, or from the shot sound it replaces. That works for every gun. The game keeps all six melee weapons in one folder, `Project/Models/Weapon/Meelee/` (spelled that way), so for a melee mod the folder says nothing and the converter stops with `cannot tell which weapon this is (folders: meelee, …) - use --weapon <name>`. The same happens with a mod whose files sit in a folder of its own or that covers more than one weapon. Then name the weapon yourself, spelled exactly as below. Which weapon a melee mod replaces usually says its page or its file name (`RockGuitar_PipeWrench.pak`); after the conversion, the line `meshes:` shows the game's mesh it took, which should match the table:

| In the game | `--weapon` | The game's mesh the mod replaces |
|---|---|---|
| Knife | `Knife` | `KnifeCombat` |
| Fire Axe | `Hatchet` | `hatchet` |
| Machete | `Machete` | `SM_Machete` |
| Adjustable Wrench | `Wrench` | `SM_Wrench` |
| Pipe Wrench | `MonkeyWrench` | `SM_MonkeyWrench` |
| Hammer | `IronHammer` | `SM_IronHammer` |

```
python3 weaponpak.pyz SomeKnife.pak --weapon Knife --name SomeKnife --title "Some knife"
python3 weaponpak.pyz SomeAxe.pak --weapon Hatchet --name SomeAxe --title "Some axe"
python3 weaponpak.pyz SomeMachete.pak --weapon Machete --name SomeMachete --title "Some machete"
python3 weaponpak.pyz SomeWrench.pak --weapon Wrench --name SomeWrench --title "Some wrench"
python3 weaponpak.pyz SomePipeWrench.pak --weapon MonkeyWrench --name SomePipeWrench --title "Some pipe wrench"
python3 weaponpak.pyz SomeHammer.pak --weapon IronHammer --name SomeHammer --title "Some hammer"
```

On Windows the command is `python` instead of `python3`. The guns' names, for the rare case they are needed: `Glock`, `Revolver`, `DesertEagle`, `Shotgun`, `UMP45`, `HK416`, `SA58`, `Bow`, `Speargun`, `GrenadeLauncher`.

**For weapon-mod authors.** A weapon mod can also be built for AltUI directly in the Unreal Editor, without the converter. [`uassets/`](uassets/) holds the two row structures it takes - `S_WeaponSkin` and `S_WeaponModel` - and [uassets/README.md](uassets/README.md) describes the tables, the columns and how a model's meshes have to be named. A finished example to install and to rebuild is in [`examples/WeaponAltUI_Example/`](examples/WeaponAltUI_Example/). Such a pak needs AltUI and does nothing without it.

## Settings of other mods

Mods that the player controls in the game can put their settings into AltUI instead of binding keys of their own: a
**Mods** tab lists every mod that registered there and shows its settings - toggles, sliders, numbers, choices,
colours, text fields, info lines, keys and buttons - in AltUI's style. The tab only appears when such a mod is installed.

**For mod authors.** A mod registers through two data tables in its own folder and an interface on its actor;
[MOD_UI.md](MOD_UI.md) describes both, the assets are in [`uassets/`](uassets/), and a finished example to install and to
rebuild is in [`examples/AltUIMod_Example/`](examples/AltUIMod_Example/).

## Custom names

Mod packs often ship cryptic identifiers. The Manage tab lets you give any mod, group, piece, hairstyle, skin, make-up, pose or appearance preset your own display name; the name is used everywhere in the panel and found by the search (the identifier stays searchable too, and the tooltip shows both). Names are stored in `Saved/SaveGames/AltUI_Names.sav`. To edit them as text, close the game and run `python3 altui_names.pyz export` (writes `names.json`), edit the file, then `python3 altui_names.pyz import names.json`; the previous save is kept as `AltUI_Names.sav.bak`. Without a path the tool looks in the game's save folder (Windows `%LOCALAPPDATA%\TheKillingAntidote\Saved\SaveGames`, Linux/Proton the Steam compatdata prefix).

**Modding notes.** The techniques behind this mod, written up for other modders: paks and assets without the editor, how the game finds mods, running your own code, what AltUI reads from a mod, asset pitfalls, and generating assets instead of clicking them – [pubdocs/](pubdocs/).

## Building from source

Everything in the paks is generated – no game assets are included.

### Requirements

* Unreal Engine 4.27 built from source.
* Python 3.
* The official sample project *TKA_Workshop* linked in the Steam guide [Workshop Mod Creation](https://steamcommunity.com/sharedfiles/filedetails/?id=3360997448) – it contains the game's class blueprints the mod compiles against.

### Build

* Copy `bpgen/` to `<sample project>/Plugins/TKA_BPGen` and build the project once. Copy `config.example.sh` to `config.sh` and set the paths.
* `./build.sh` – runs the generators (`assets/gen/*.py` → `assets/*.json`), the BPGen commandlet (adds the missing function stubs to the sample project's game classes and creates the widgets and the manager blueprint), cook, pak, verify, deploy (`--no-deploy` to skip). BPGen builds only the blueprints whose generated JSON changed since the last run, plus whatever refers to them; `--full` rebuilds everything from scratch.
* Tests: `python3 -m unittest discover -s tests/unit`, editor tests `scripts/edtest.sh $PWD/tests/editor/test_<name>.py`.
* `scripts/bodypak_dist.sh` builds `bodypak.pyz` (Python files + `LICENSE-GPL-3.0.txt`, nothing native). `scripts/oodle_kraken.py` is the Oodle Kraken decoder, a pure-Python port of [ooz](https://github.com/powzix/ooz) (GPL-3). `tools/fetch_ooz.sh` builds the original as `tools/ooz/libooz.so`; the repo's pak tooling and `tests/unit/test_kraken.py` use it through `scripts/oodle_native.py` (ctypes, much faster, reference for the port) – it never goes into the pyz.

## Screenshots

| | |
|---|---|
| **Clothes** – one list per slot, group chips, search, “only worn” ![Clothes](versions/1.8.0/screenshots/01-clothes-only-worn.jpg) | **Clothes** – group chips folded with “...” ![Clothes](versions/1.8.0/screenshots/02-clothes-chips-folded.jpg) |
| **Clothes** – favourites above all pieces ![Clothes](versions/1.8.0/screenshots/03-clothes-favourites.jpg) | **Clothes** – one group chip chosen ![Clothes](versions/1.8.0/screenshots/04-clothes-chip-witch.jpg) |
| **Clothes** – the chosen chip stays when the row is folded ![Clothes](versions/1.8.0/screenshots/05-clothes-chip-witch-folded.jpg) | **Outfits** – the game's presets with names; pieces per tile adjustable ![Outfits](versions/1.8.0/screenshots/06-outfits.jpg) |
| **Outfits** – “View content” of an outfit ![Outfits](versions/1.8.0/screenshots/07-outfits-view-content.jpg) | **Looks** – complete looks with photo, saved from the front or as you see her ![Looks](versions/1.8.0/screenshots/08-looks.jpg) |
| **Looks** – “View content”: make-up, body values, face ![Looks](versions/1.8.0/screenshots/09-looks-view-content.jpg) | **Backpack** – worn and carried items ![Backpack](versions/1.8.0/screenshots/10-backpack.jpg) |
| **Coiffure** – hairstyles, natural hair colours ![Coiffure](versions/1.8.0/screenshots/11-coiffure.jpg) | **Poses** – every action animation, sorted by stance and chapter ![Poses](versions/1.8.0/screenshots/12-poses.jpg) |
| **Weapons** – a model and a skin per weapon; models and skins counted per weapon ![Weapons](versions/1.8.0/screenshots/13-weapons.jpg) | **Weapons** – the menu of a mod model: the game's material, parts left out ![Weapons](versions/1.8.0/screenshots/14-weapons-model-menu.jpg) |
| **Appearance** – presets with photo – apply, view, rename, update, delete ![Appearance](versions/1.8.0/screenshots/15-appearance-presets-rename.jpg) | **Appearance** – what she wears, the menu of an eye texture ![Appearance](versions/1.8.0/screenshots/16-appearance-worn-eye-menu.jpg) |
| **Appearance** – make-up: “Tint…” in the menu ![Appearance](versions/1.8.0/screenshots/17-appearance-lips-tint-menu.jpg) | **Appearance** – make-up in its own colour ![Appearance](versions/1.8.0/screenshots/18-appearance-lips-default-tint.jpg) |
| **Appearance** – make-up tinted with the game's palette ![Appearance](versions/1.8.0/screenshots/19-appearance-lips-tint-palette.jpg) | **Body Shape** – a converted body with bone-scale sliders ![Body Shape](versions/1.8.0/screenshots/20-body-shape-converted-body.jpg) |
| **Body Shape** – the game's own body ![Body Shape](versions/1.8.0/screenshots/21-body-shape-standard.jpg) | **Face** – saved faces with photo and their menu ![Face](versions/1.8.0/screenshots/22-face-saved-menu.jpg) |
| **Face** – “View content” of a saved face ![Face](versions/1.8.0/screenshots/23-face-saved-view-content.jpg) | **Face** – expressions, blended or added up ![Face](versions/1.8.0/screenshots/24-face-expression.jpg) |
| **Face** – gaze ![Face](versions/1.8.0/screenshots/25-face-gaze.jpg) | **Face** – mouth shapes and “Close mouth” ![Face](versions/1.8.0/screenshots/26-face-mouth.jpg) |
| **Mods** – settings of another mod – the example lamp ![Mods](versions/1.8.0/screenshots/27-mods-example-lamp.jpg) | **Options** – in categories – language, space for Jodi, ownership ![Options](versions/1.8.0/screenshots/28-options-general.jpg) |
| **Options › Tiles** – tile sizes for all tiles, outfits and looks; pieces per outfit tile ![Options › Tiles](versions/1.8.0/screenshots/29-options-tiles.jpg) | **Options › Groups** – merging, group names, chip area, chip search ![Options › Groups](versions/1.8.0/screenshots/30-options-groups.jpg) |
| **Options › Camera** – FOV, distance, height, “camera follows slot” ![Options › Camera](versions/1.8.0/screenshots/31-options-camera.jpg) | **Options › Controls** – panel key, scroll speed ![Options › Controls](versions/1.8.0/screenshots/32-options-controls.jpg) |
| **Options › Quick menu** – key, opacity, the items in the wheel; below, everything available, three to a row ![Options › Quick menu](versions/1.8.1/screenshots/33-options-quick-menu.jpg) | **Options › Colours** – colours, opacities, saved schemes ![Options › Colours](versions/1.8.0/screenshots/38-options-colours.jpg) |
| **Options › Colours** – a saved scheme applied ![Options › Colours](versions/1.8.0/screenshots/39-options-colours-scheme-oceanic.jpg) | **Options › Colours** – another saved scheme ![Options › Colours](versions/1.8.0/screenshots/40-options-colours-scheme-fire.jpg) |
| **Options › Slot conflicts** – free the game's slot pairs ![Options › Slot conflicts](versions/1.8.0/screenshots/41-options-slot-conflicts.jpg) | **Options › Tabs** – tab bar with icons and text ![Options › Tabs](versions/1.8.0/screenshots/42-options-tabs-icons-left.jpg) |
| **Options › Tabs** – text only ![Options › Tabs](versions/1.8.0/screenshots/43-options-tabs-text-only.jpg) | **Options › Tabs** – icons only ![Options › Tabs](versions/1.8.0/screenshots/44-options-tabs-icons-only.jpg) |
| **Options › Tabs** – icons right of the text ![Options › Tabs](versions/1.8.0/screenshots/45-options-tabs-icons-right.jpg) | **Options › Tabs** – tabs switched off ![Options › Tabs](versions/1.8.0/screenshots/46-options-tabs-switched-off.jpg) |
| **Manage** – display names of the game's groups ![Manage](versions/1.8.0/screenshots/47-manage-vanilla.jpg) | **Manage** – mods and their groups, with chips ![Manage](versions/1.8.0/screenshots/48-manage-mods-chips.jpg) |
| **Manage** – poses, with mod chips ![Manage](versions/1.8.0/screenshots/49-manage-poses-chips.jpg) | **Manage** – clothes, with group chips ![Manage](versions/1.8.0/screenshots/50-manage-clothes-chips.jpg) |
| **Manage** – hairstyles, skins and make-up, with mod chips ![Manage](versions/1.8.0/screenshots/51-manage-appearance-chips.jpg) | **Free camera** – a close-up from the Jodi view ![Free camera](versions/1.8.0/screenshots/52-free-camera.jpg) |
| **Quick menu** – hold 4: a wheel of what you use most ![Quick menu](versions/1.8.0/screenshots/53-quick-menu.jpg) | **Quick menu** – in the colours of a scheme ![Quick menu](versions/1.8.0/screenshots/54-quick-menu-scheme-oceanic.jpg) |
| **Quick menu** – in the colours of another scheme ![Quick menu](versions/1.8.0/screenshots/55-quick-menu-scheme-fire.jpg) | **Main menu** – Jodi as you made her ![Main menu](versions/1.8.0/screenshots/56-main-menu.jpg) |
| **Loading screen** – Jodi as you made her ![Loading screen](versions/1.8.0/screenshots/57-loading-screen.jpg) | **Looks** – “Spawn as ragdoll” and moving tiles in the context menu ![Looks](versions/1.9.0/screenshots/58-looks-spawn-as-ragdoll.jpg) |
| **Weapons** – a shot sound per weapon, above model and skin ![Weapons](versions/1.9.0/screenshots/59-weapons-sound.jpg) | **Weapons** – melee weapons take a model too ![Weapons](versions/1.9.0/screenshots/60-weapons-melee-model.jpg) |
| **Options › Movement** – own walk / run speed ![Options › Movement](versions/1.9.0/screenshots/61-options-movement.jpg) | **Options › Quick menu** – ragdoll actions and “Own speed on / off” ![Options › Quick menu](versions/1.9.0/screenshots/62-options-quick-menu-ragdolls.jpg) |
| **Ragdolls** – zombies and people, figures, joints, poses and scenes ![Ragdolls](versions/1.9.0/screenshots/63-ragdolls-figures-joints.jpg) | **Codex** – the AltUI manual ![Codex](versions/1.9.0/screenshots/64-codex-manual.jpg) |
| **Codex** – the code locks of the level ![Codex](versions/1.9.0/screenshots/65-codex-passwords.jpg) |  |

## License

MIT – see `LICENSE`. AltUI is a fan project and not affiliated with the game's developer.
