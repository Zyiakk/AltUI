# AltUI

A replacement wardrobe and appearance UI for *The Killing Antidote* (game version 0.6.x). The vanilla wardrobe gives every mod author their own tab, so with a few clothing mods installed the same kind of item is scattered across a dozen tabs and there is no way to search. AltUI sorts every item from the game and from all installed mods into **one list per slot** (tops, skirts, shoes, …), with search, filters, favourites and hiding – and puts hair, makeup, body and outfits into the same panel. It opens anywhere in a level with **B**; no trips to the wardrobe or the mirror.

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

Uninstall: delete the files you copied. The mod's own saves may go too: `Saved/SaveGames/AltUI.sav`, `AltUI_Looks.sav`, `AltUI_Names.sav`, the look photos in `Saved/SaveGames/AltUI/` and the weapon tile pictures in `Saved/SaveGames/WeaponIcons/`. Nothing else is touched – clothes, outfits, makeup and hair are written through the game's own save files.

## What it does

| Tab | Content |
|---|---|
| **Clothes** | Every item the game and your mods know, grouped by slot, sub-tabs per mod (collapsible), search (also by mod and group name), "owned only" / "favourites only" / "vanilla only" filters, favourites, colour via the game's palette, colour reset, backpack in/out, hide items; right-click: only this group, view mod content. |
| **Outfits** | The game's outfit presets, with names (right-click → rename). |
| **Looks** | A complete look – clothes with colours, hairstyle and colour, makeup, eyes, skin, body sliders, body mod – saved with an in-game full-body photo. Apply, update, rename, delete. |
| **Backpack** | What Jodi wears and carries: wear, remove, repair, back to wardrobe, clean up. |
| **Coiffure** | All hairstyles, hair colour, 14 natural hair colour presets, factory reset. |
| **Poses** | Every action animation the game and your pose mods know (the list behind the phone's "rhythm" app), one tile per pose with its title, chips per mod, search, favourites, hide; click plays the pose, click again or "Stop pose" stops it. |
| **Weapons** | One entry per weapon; for each of them its model and its skin, chosen separately: mesh mods above, below the game's own gun paints (no spray can needed) and every installed skin mod. Both kinds are converted with `weaponpak.pyz`; the choice is remembered and re-applied when the weapon is picked up again. |
| **Appearance** | Skin, every makeup type, eyes, appearance presets with icons. |
| **Body Shape** | Breast / waist sliders, a switcher for installed body mods (below) and – for converted bodies – bone-scale sliders: scale, bust, waist extra, glutes/hips, thighs, calves, arms, hands, feet, saved per body. |
| **Options** | Panel key, language, scroll speed, tile size, length of group names and height of the group row, screen share kept free for Jodi, camera FOV / distance / pan, colour scheme and opacity, "underwear may be taken off", not-owned items locked / greyed / like owned, slot conflicts (free the game's bra-vs-shirt-style pairs), merge groups / mods with the same name, tooltip options. |
| **Manage** | Your own display names for mods, groups (mod and vanilla), clothes, hairstyles, skins and make-up – used everywhere in the panel and by the search; "only mods" filter, search, revert per row. Exportable/importable as JSON with `altui_names.pyz` (see below). |

Undo / redo (5 steps) in the status bar; tooltips show which mod an item comes from. Languages: English, German, Chinese, Russian, Spanish, Polish (auto-detected, switchable).

**Controls:** **B** opens / closes (changeable in Options), **Esc** closes. Left click selects / wears / applies, right click opens the context menu, mouse wheel scrolls. While the panel is open Jodi cannot walk; drag on the background to turn the camera, click on Jodi and drag to turn her (she turns back when the panel closes), +/− changes the distance in 5 % steps, the mouse wheel over Jodi in 4 % steps. The two round buttons above +/− open a free camera (mouse turns, W A S D / Q E move, Shift faster, wheel = speed, within 6 m of Jodi, stops at walls; Esc back) and the game's photo mode (Esc back).

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

**For weapon-mod authors.** A weapon mod can also be built for AltUI directly in the Unreal Editor, without the converter. [`uassets/`](uassets/) holds the two row structures it takes - `S_WeaponSkin` and `S_WeaponModel` - and [uassets/README.md](uassets/README.md) describes the tables, the columns and how a model's meshes have to be named. A finished example to install and to rebuild is in [`examples/WeaponAltUI_Example/`](examples/WeaponAltUI_Example/). Such a pak needs AltUI and does nothing without it.

## Settings of other mods

Mods that the player controls in the game can put their settings into AltUI instead of binding keys of their own: a
**Mods** tab lists every mod that registered there and shows its settings - toggles, sliders, numbers, choices,
colours, text fields, info lines and buttons - in AltUI's style. The tab only appears when such a mod is installed.

**For mod authors.** A mod registers through two data tables in its own folder and an interface on its actor;
[MOD_UI.md](MOD_UI.md) describes both, the assets are in [`uassets/`](uassets/), and a finished example to install and to
rebuild is in [`examples/AltUIMod_Example/`](examples/AltUIMod_Example/).

## Custom names

Mod packs often ship cryptic identifiers. The Manage tab lets you give any mod, group, piece, hairstyle, skin or make-up your own display name; the name is used everywhere in the panel and found by the search (the identifier stays searchable too, and the tooltip shows both). Names are stored in `Saved/SaveGames/AltUI_Names.sav`. To edit them as text, close the game and run `python3 altui_names.pyz export` (writes `names.json`), edit the file, then `python3 altui_names.pyz import names.json`; the previous save is kept as `AltUI_Names.sav.bak`. Without a path the tool looks in the game's save folder (Windows `%LOCALAPPDATA%\TheKillingAntidote\Saved\SaveGames`, Linux/Proton the Steam compatdata prefix).

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
| **Clothes** – one list per slot, group chips, search, filters ![Clothes](versions/1.5.0/screenshots/clothes-open.jpg) | **Weapons** – a model and a skin per weapon, rendered tiles ![Weapons](versions/1.5.0/screenshots/weapons.jpg) |
| **Weapons** – the game's material forced onto a mod model ![Forced skin](versions/1.5.0/screenshots/weapons-forced-skin.jpg) | **Poses** – every action animation, sorted by stance ![Poses](versions/1.5.0/screenshots/poses.jpg) |
| **Outfits** – the game's presets with names ![Outfits](versions/1.5.0/screenshots/outfits.jpg) | **Looks** – complete looks with photo ![Looks](versions/1.5.0/screenshots/looks.jpg) |
| **Backpack** – worn and carried items, context menu ![Backpack](versions/1.5.0/screenshots/bagpack.jpg) | **Coiffure** – hairstyles, natural hair colours ![Coiffure](versions/1.5.0/screenshots/coiffure-natural-colours.jpg) |
| **Appearance** – skin, make-up, eyes, mod chips, search ![Appearance](versions/1.5.0/screenshots/appearance.jpg) | **Appearance** – cosmetics, each entry tintable ![Cosmetics](versions/1.5.0/screenshots/appearance-cosmetics.jpg) |
| **Appearance** – tattoos ![Tattoos](versions/1.5.0/screenshots/appearance-tattoos.jpg) | **Body Shape** – body switcher and bone-scale sliders ![Body Shape](versions/1.5.0/screenshots/body-shape.jpg) |
| **Manage** – your own display names ![Manage](versions/1.5.0/screenshots/manage.jpg) | **Options** – key, language, camera, not-owned items, colours ![Options](versions/1.5.0/screenshots/options.jpg) |
| **Options** – slot conflicts ![Slot conflicts](versions/1.5.0/screenshots/options-slot-conflicts.jpg) | **Free camera** – a close-up from the Jodi view ![Free camera](versions/1.5.0/screenshots/free-cam.jpg) |

## License

MIT – see `LICENSE`. AltUI is a fan project and not affiliated with the game's developer.
