# AltUI

An alternative wardrobe and appearance UI for *The Killing Antidote* (game version 0.6.x), usable next to the game's own wardrobe and mirror. The vanilla wardrobe gives every mod author their own tab, so with a few clothing mods installed the same kind of item is scattered across a dozen tabs and there is no way to search. AltUI sorts every item from the game and from all installed mods into **one list per slot** (tops, skirts, shoes, …), with search, filters, favourites and hiding – and puts hair, makeup, body and outfits into the same panel. It opens anywhere in a level with **B**; no trips to the wardrobe or the mirror. Next to that: an Inventory tab for Jodi's backpack and the Hyper Storage Box, followers and NPCs made from your looks, ragdolls to place and pose (copies of Jodi, zombies, people), a Codex with the manual, the game's encyclopedia and the code locks of the level, Jodi's own walk and run speed, slow motion, and per weapon a model, a skin, a shot sound and its accessories. Hold **4** for the quick menu: a wheel of what you use most – poses, outfits, looks, slow motion, orders for followers – one flick away without opening the panel.

![Quick menu – hold 4 for a wheel of what you use most](versions/2.0.0/screenshots/01-quick-menu.jpg)

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

**After a game update.** AltUI uses functions and tables of the game. When the game changes them, AltUI can stop working or, in the worst case, make the game crash – and so can the file that starts it: the hook and the Blueprint Loader both replace the game's `TKA_PlayerCameraManager` class, so after an update that changes this class, an old file puts the previous version of it back. Two things help:

* When AltUI starts in the main menu, it compares a few tables of the game with the version it was built for. If they differ, it shows a warning before it touches anything of the game: *Go on anyway* starts AltUI (and does not ask again for this game version), *AltUI off for now* leaves the game alone; the next level asks again. An old-style mod that replaces one of the game's own tables (clothes, items, weapon parts) can trigger the warning as well; then going on is fine.
* If the game behaves oddly after an update, remove `AltUI.pak` and the hook first and check whether a newer AltUI is out.

**Uninstall:** delete the files you copied – `TheKillingAntidote/Mods/AltUI.pak`, and `TheKillingAntidote/Content/Paks/~mods/AltUI_Hook_P.pak` if you use the hook (the Blueprint Loader only if no other mod needs it). AltUI keeps its own data in the game's save folder, on Windows `%LOCALAPPDATA%\TheKillingAntidote\Saved\SaveGames\`. To remove everything, delete these there too:

| File or folder | Content |
|---|---|
| `AltUI.sav` | settings and choices |
| `AltUI_Looks.sav` | saved looks |
| `AltUI_Faces.sav` | saved faces |
| `AltUI_Names.sav` | your own names |
| `AltUI_Ragdolls.sav` | ragdoll scenes and poses |
| `AltUI_Followers.sav` | followers and NPCs made from looks |
| `AltUI/` | photos of looks, faces and appearance presets |
| `WeaponIcons/` | weapon tile pictures |

Nothing else is touched – clothes, outfits, makeup and hair are written through the game's own save files. AltUI's slot colours belong to the save game as well: they are kept among the game's clothing colours as extra entries starting with `AltUI#`, which the game itself ignores.

## What it does

The panel has one tab per topic. Tabs you do not use can be switched off under *Options › Tabs*.

### Clothes

* Every piece the game and your mods know, in one list per slot.
* Chips per mod and group; the chip row folds.
* Search, also by mod and group name.
* Filters: only owned, only favourites, only vanilla and only worn.
* Favourites, and hiding pieces you never want to see.
* Colour through the game's palette, with a `#RRGGBB` field below it; colour reset per piece.
* Every piece that can take a colour gets one, jewellery included – and one colour per material slot, so a dress can
  wear one colour on the fabric and another on the trim.
* Slot colours are kept per save game.
* Into the backpack and out of it.
* Right click: only this group, view the mod's content and a damage slider (0–100 %).

### Outfits

* The game's outfit presets, with names; right click renames.
* Your own order: right click moves an outfit left, right, to the start or to the end.

### Looks

* A complete look: clothes with their colours, hairstyle and hair colour, make-up, eyes, skin, body sliders, body mod and
  face.
* Saved with a full-body photo from the game, taken from the front or as you see her.
* Apply, update, rename and delete; "View content" lists what a look holds.
* Your own order: right click moves a look left, right, to the start or to the end.
* Spawn a look as a ragdoll, a follower or an NPC.

### Backpack

* What Jodi wears and carries: wear, take off, repair, back to the wardrobe and tidy up.

### Inventory

* Jodi's items and the **Hyper Storage Box**, one list under the other.
* The game's item groups as chips; the weight with a bar.
* A click moves one item into the box or out of it.
* Right click: half or all, use, inspect, discard, quick slot, unload ammo and accessories.
* A stack's menu ends with an amount: a slider and a number field, then one entry per target with that number.
* "Discard all" asks first when it would put 100 or more objects on the ground – that many objects with physics at once
  can crash the game: cancel, destroy instead, or drop anyway.
* Everything runs through the game's own functions, so the game's rules stay.
* Each list can be folded or given the full height.
* On maps where the game never saves the backpack, the tab says so.
* Optional, off by default (*Options › General*): an "All items" catalogue with every item of the game, into the backpack
  or the box.

### Coiffure

* All hairstyles and the hair colour.
* 14 natural hair colours as presets; factory reset.
* Favourite hairstyles at the top (right click, "Add to favourites").

### Poses

* Every action animation the game and your pose mods know – the list behind the "rhythm" app on Jodi's phone.
* One tile per pose with its title; a speaker marks poses with a sound.
* Chips per mod, search, favourites and hiding.
* A click plays the pose; a second click or "Stop pose" stops it.
* "Use as idle" in a pose's menu: the pose starts after 1.5 s of standing still and ends when Jodi moves.

### Weapons

* One entry per weapon, melee weapons included; it counts the models and skins available for it.
* For each weapon a model, a skin and a shot sound, chosen separately:
  * models: the game's own and those from mods;
  * skins: the game's gun paints (no spray can needed) and every installed skin mod;
  * shot sounds: the weapon's own and every installed sound made for it. A click plays it; a mounted suppressor with a
    sound of its own still wins.
* Chips filter by mod.
* The choice is remembered and applied again when the weapon is picked up or taken out of the storage box.
* *Weapon accessories*: one row per slot the weapon takes (sights, barrel, grip, magazine), with parts from the backpack
  or the storage box.
* "Show item pictures" shows the item's or the mod's own picture on the tiles instead of the rendered one.
* Weapon mods are converted with `weaponpak.pyz` – see [Weapon mods](#weapon-mods).

### Appearance

* Skin, every kind of make-up and eyes.
* Make-up and eyes can be tinted, each entry on its own (right click, "Tint…"); "Reset tint" brings back the game's
  look.
* Appearance presets with a photo: save, update, rename and delete.
* Your own order: right click moves a preset left, right, to the start or to the end.

### Body Shape

* The game's breast and waist sliders.
* Switch between installed body mods – see [Body mods](#body-mods).
* For converted bodies, bone-scale sliders saved per body: scale, bust, waist extra, glutes / hips, thighs, calves, arms,
  hands and feet.
* For breast and for glutes & hips:
  * jiggle – the game's physics, works on every body;
  * angle and hip width – converted bodies;
  * nipples – only while the chest is uncovered.

### Face

* Jodi's facial expression as sliders: the game's expressions (relaxed, focused, smile, pain, fright, tired, suffering),
  gaze and mouth shapes.
* A ticked entry keeps its value, also during poses; an unticked one is left to the game's animation.
* Expressions blended (at most 100 % together) or added up; "Close mouth".
* "Eyes closed": from open to fully shut, on converted bodies (like the body sliders).
* Saved faces with a photo; "View content" lists their values.
* Your own order: right click moves a saved face left, right, to the start or to the end.

### Mods

* The settings of other mods that register with AltUI: the mods on the left, the chosen one's settings on the right –
  toggles, sliders, numbers, choices, colours, text fields, info lines, keys and buttons.
* Only shown when such a mod is installed – see [Settings of other mods](#settings-of-other-mods).

### Options

In categories, chosen in a list on the left:

* **General:** language, the share of the screen kept free for Jodi, "underwear may be taken off", pieces you do not own
  locked / greyed / like owned, all encyclopedia entries in the Codex, the "All items" catalogue and auto-equip for the
  Inventory tab.
* **Tiles:** tile size, and an own size for outfit, look, ragdoll and inventory tiles; how many pieces an outfit tile
  shows; tooltip options.
* **Groups:** merge groups / mods with the same name, length of group names, height of the chip area and chip search.
* **Camera:** field of view, distance and height of the view beside the panel; the camera follows the slot.
* **Controls:** panel key, scroll speed and how far the mouse wheel lifts a ragdoll.
* **Movement:** Jodi's own walk and run speed (50–200 %; crouching and jumping stay as they are), slow motion and its
  speed, and how she stands: the game's usual idle, six other idle animations of the game, or an idle mod converted with
  `idlepak.pyz` – see [Idle mods](#idle-mods).
* **Quick menu:** its key, its opacity, the items in the wheel, and **own keys**: right click any available item and press
  a key – it then runs on that key with the panel closed, also in the free camera and the game's photo mode.
* **Colours:** colour scheme and opacity; schemes saved under a name.
* **Slot conflicts:** free the game's slot pairs, such as bra and shirt.
* **Tabs:** switch tabs off; the tab bar shows text, icons or both, icon left or right of the text.

### Manage

* Your own display names for mods (weapon mods included), groups (mod and vanilla), clothes, hairstyles, skins, make-up,
  poses and appearance presets.
* The names are used everywhere in the panel and by the search.
* Filter "only mods", search; chips filter the list by mod or group, as in Clothes, and a search field narrows down the
  chips.
* Revert per row.
* Export and import as JSON with `altui_names.pyz` – see [Custom names](#custom-names).

### Ragdolls

* Figures with physics to place and pose in the level:
  * copies of Jodi, standing and frozen in her pose, with everything she wears – or a look via "Spawn as ragdoll";
  * every kind of zombie from the encyclopedia, with its variants;
  * the nurse and a survivor.
* Each figure is active (falls, can be thrown) or frozen (keeps its pose).
* 17 joints per figure, each locked, free or movable.
* With the mouse beside the panel:
  * drag a frozen figure to move it; the wheel lifts it;
  * drag an active figure by a body part;
  * right drag turns a figure;
  * Shift + click locks or frees a joint;
  * Shift + right click makes a joint movable – dragging a body part below it then poses only that part.
* Poses are saved per kind of figure, scenes per level (`AltUI_Ragdolls.sav`).

### Followers

* Figures made from a look: right click a look, "Spawn as follower" or "Spawn as NPC". They wear the look's clothes, body
  sliders and weapon looks.
* A follower walks with Jodi, fights and takes orders; an NPC stays where it is and defends itself.
* The tab lists every figure with its status, and chips: follow me, wait here, bring here (also from another level),
  → NPC / → follower, active, invulnerable, and "..." for rename, change look, revive and remove.
* Jodi's backpack and the storage box sit at the top: a click gives an item or a gun to the selected figure; a stack's
  menu has the amount row as in the Inventory tab.
* A figure's clothes are real pieces, as with the game's own NPCs: they take damage, tear off and show up in the game's
  NPC inventory. In the tab they are tiles to take off, give or repair.
* Each figure wears the make-up of its look and has one of the game's NPC voices.
* Figures are kept in `AltUI_Followers.sav`, never in the game's save.

### Codex

* The AltUI manual in all seven languages.
* The encyclopedia from Jodi's office computer: the entries unlocked in the game, or all of them (*Options › General*).
* The code locks of the current level, nearest first; each code stays hidden until clicked.

### Everywhere

* Undo / redo (5 steps) in the status bar.
* Tooltips show which mod a piece comes from.
* The search finds a mod by its pak name too, in every tab.
* The panel opens on the tab it was left on, with the same slot, category or weapon chosen.
* Jodi looks the way you made her as soon as a level has loaded, and in the main menu and on the loading screen too.
* Languages: English, German, Chinese, Russian, Spanish, Polish, French – detected from the game and switchable.

### Controls

* **B** opens and closes the panel (changeable in Options); **Esc** closes it.
* Left click selects, wears or applies; right click opens the context menu; the mouse wheel scrolls.
* While the panel is open, Jodi cannot walk:
  * drag on the background to turn the camera;
  * click on Jodi and drag to turn her – she turns back when the panel closes;
  * +/− changes the distance in 5 % steps, the mouse wheel over Jodi in 4 % steps.
* The three round buttons above +/−:
  * **free camera** – the mouse turns, W A S D / Q E move, Shift is faster, the wheel sets the speed; within 6 m of Jodi,
    stops at walls; Esc goes back;
  * **photo mode** of the game – Esc goes back;
  * **ragdolls mode** – the panel goes away and the camera is free (W A S D / Q E, Shift + wheel sets the speed, drag on
    nothing turns it); figures under the mouse are moved and posed as beside the panel; Esc or B goes back.
* **Quick menu:** hold **4** (changeable) for a wheel of the items you picked – in Options, or with a right click on a
  tile, a tab or a mod's entry – and let go on one to run it. It also offers slow motion, stop time (also in the game's
  photo mode, whose camera keeps moving), hide Jodi, hide the game's UI, orders for followers and the buttons and toggles
  of mods in the Mods tab. Any of these can also get a key of its own (Options › Quick menu, "Own keys").
* **Main menu:** **B** opens a small menu – the menu scenes, the loading scene, the next camera, and hiding the game's
  menu.

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

## Idle mods

Idle mods replace Jodi's standing animation, so only one can be active and nothing can switch between them.
`idlepak.pyz` (in the release, Python 3.8+, no packages; GPL-3, see LICENSE) converts such a replacer into an
`IdleAltUI_<Name>.pak`: it replaces nothing any more, the game's own idle stays, and the mod becomes one more choice
under *Options › Movement › Standing*.

```
python3 idlepak.pyz <Replacer.pak> [--name <Name>] [--title "Display name"] [--out <folder>] [--force] [--altui <AltUI.pak>]
python3 idlepak.pyz SomeIdleReplacer.pak --name SomeIdle --title "Some idle"
```

AltUI must be installed: the converter builds the new pak partly from `AltUI.pak` (AltUI's own idle template, pointed at
the mod's animation) and looks for it in the usual Steam folders; if it is somewhere else, give the path with
`--altui <path to AltUI.pak>`. Copy the resulting `IdleAltUI_<Name>.pak` to `TheKillingAntidote/Mods/` and remove the
original replacer. The animation is taken byte for byte; everything else in the pak is left out and listed. On Windows the
command is `python` instead of `python3`.

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
* `scripts/bodypak_dist.sh` builds `bodypak.pyz` (Python files + `LICENSE-GPL-3.0.txt`, nothing native); `weaponpak_dist.sh`, `idlepak_dist.sh` and `altui_names_dist.sh` build the other tools. `scripts/oodle_kraken.py` is the Oodle Kraken decoder, a pure-Python port of [ooz](https://github.com/powzix/ooz) (GPL-3). `tools/fetch_ooz.sh` builds the original as `tools/ooz/libooz.so`; the repo's pak tooling and `tests/unit/test_kraken.py` use it through `scripts/oodle_native.py` (ctypes, much faster, reference for the port) – it never goes into the pyz.

## Screenshots

| | |
|---|---|
| **Inventory** – a chosen amount: slider and number field, one entry per target (new in 2.1.0) ![Inventory](versions/2.1.0/screenshots/63-inventory-catalogue-amount.jpg) | **Options › Movement** – “Standing”: the game's idles and an idle mod (new in 2.1.0) ![Options › Movement](versions/2.1.0/screenshots/64-options-movement-standing.jpg) |
| **Poses** – “Use as idle” in a pose's menu (new in 2.1.0) ![Poses](versions/2.1.0/screenshots/65-poses-use-as-idle.jpg) | |
| **Quick menu** – hold 4: a wheel of what you use most – poses, outfits, looks, slow motion, stop time, orders for followers ![Quick menu](versions/2.0.0/screenshots/01-quick-menu.jpg) | **Clothes** – one list per slot, group chips, search, “only worn” ![Clothes](versions/2.0.0/screenshots/02-clothes.jpg) |
| **Clothes** – the chip row folded with “...” ![Clothes](versions/2.0.0/screenshots/03-clothes-chips-folded.jpg) | **Clothes** – favourites above all pieces ![Clothes](versions/2.0.0/screenshots/04-clothes-favourites.jpg) |
| **Clothes** – the chip “No group” chosen; counts per slot ![Clothes](versions/2.0.0/screenshots/05-clothes-no-group-chip.jpg) | **Clothes** – the menu of a piece: one colour per material slot, damage slider ![Clothes](versions/2.0.0/screenshots/06-clothes-menu-colour-per-slot-damage.jpg) |
| **Clothes** – “View mod content”: everything one mod brings ![Clothes](versions/2.0.0/screenshots/07-clothes-mod-content.jpg) | **Outfits** – the game's presets with names; the menu moves an outfit ![Outfits](versions/2.0.0/screenshots/08-outfits-menu-move.jpg) |
| **Outfits** – an outfit opened: its pieces ![Outfits](versions/2.0.0/screenshots/09-outfits-detail.jpg) | **Looks** – complete looks with photo; spawn one as ragdoll, follower or NPC ![Looks](versions/2.0.0/screenshots/10-looks-menu-spawn.jpg) |
| **Looks** – a look opened: clothes, coiffure, skin, make-up ![Looks](versions/2.0.0/screenshots/11-looks-detail-clothes.jpg) | **Looks** – a look opened: eyes, body values, face ![Looks](versions/2.0.0/screenshots/12-looks-detail-body-face.jpg) |
| **Backpack** – worn and carried ![Backpack](versions/2.0.0/screenshots/13-backpack.jpg) | **Inventory** – backpack, Hyper Storage Box and the “All items” catalogue; weight bar ![Inventory](versions/2.0.0/screenshots/14-inventory.jpg) |
| **Inventory** – the catalogue folded, the box takes the space ![Inventory](versions/2.0.0/screenshots/15-inventory-catalogue-folded.jpg) | **Inventory** – the menu of an item ![Inventory](versions/2.0.0/screenshots/16-inventory-menu.jpg) |
| **Coiffure** – hairstyles, natural hair colours ![Coiffure](versions/2.0.0/screenshots/17-coiffure.jpg) | **Poses** – every action animation, chapters, favourites; a speaker marks poses with a sound ![Poses](versions/2.0.0/screenshots/18-poses.jpg) |
| **Weapons** – accessories, shot sound, model; the menu of a mod model ![Weapons](versions/2.0.0/screenshots/19-weapons-accessories-model-menu.jpg) | **Weapons** – a mod model with parts left out – the menu brings them back ![Weapons](versions/2.0.0/screenshots/20-weapons-model-menu-parts.jpg) |
| **Weapons** – “Show item pictures”: the item's or the mod's own picture ![Weapons](versions/2.0.0/screenshots/21-weapons-item-pictures.jpg) | **Weapons** – melee weapons take a model too ![Weapons](versions/2.0.0/screenshots/22-weapons-melee-model.jpg) |
| **Appearance** – the “Vanilla” chip ![Appearance](versions/2.0.0/screenshots/23-appearance-vanilla-chip.jpg) | **Appearance** – only what she wears ![Appearance](versions/2.0.0/screenshots/24-appearance-only-worn.jpg) |
| **Appearance** – the menu of an eye texture: iris colour ![Appearance](versions/2.0.0/screenshots/25-appearance-menu-iris-colour.jpg) | **Appearance** – the menu of make-up: “Tint…” ![Appearance](versions/2.0.0/screenshots/26-appearance-menu-tint.jpg) |
| **Appearance** – tinting with the game's palette and the `#RRGGBB` field below it ![Appearance](versions/2.0.0/screenshots/27-appearance-tint-palette-hex.jpg) | **Appearance** – presets with photo and their menu ![Appearance](versions/2.0.0/screenshots/28-appearance-presets-menu.jpg) |
| **Appearance** – a preset opened ![Appearance](versions/2.0.0/screenshots/29-appearance-preset-detail.jpg) | **Body Shape** – a converted body: bone-scale sliders, jiggle, angle, hip width, nipples ![Body Shape](versions/2.0.0/screenshots/30-body-shape.jpg) |
| **Face** – expressions, blended or added up ![Face](versions/2.0.0/screenshots/31-face-expression.jpg) | **Face** – gaze ![Face](versions/2.0.0/screenshots/32-face-gaze.jpg) |
| **Face** – mouth shapes and “Close mouth” ![Face](versions/2.0.0/screenshots/33-face-mouth.jpg) | **Face** – saved faces with photo and their menu ![Face](versions/2.0.0/screenshots/34-face-saved-faces-menu.jpg) |
| **Face** – a saved face opened ![Face](versions/2.0.0/screenshots/35-face-saved-face-detail.jpg) | **Mods** – settings of other mods ![Mods](versions/2.0.0/screenshots/36-mods.jpg) |
| **Options › General** – language, space for Jodi, ownership, Codex, “All items” catalogue, auto-equip ![Options › General](versions/2.0.0/screenshots/37-options-general.jpg) | **Options › Tiles** – tile sizes, also for outfits, looks, ragdolls and the inventory ![Options › Tiles](versions/2.0.0/screenshots/38-options-tiles.jpg) |
| **Options › Groups** – merging, group names, chip area, chip search ![Options › Groups](versions/2.0.0/screenshots/39-options-groups.jpg) | **Options › Camera** – FOV, distance, height, “camera follows slot / face” ![Options › Camera](versions/2.0.0/screenshots/40-options-camera.jpg) |
| **Options › Controls** – panel key, scroll speed, ragdoll lift per wheel notch ![Options › Controls](versions/2.0.0/screenshots/41-options-controls.jpg) | **Options › Movement** – own walk / run speed, slow motion ![Options › Movement](versions/2.0.0/screenshots/42-options-movement.jpg) |
| **Options › Quick menu** – key, opacity, the items in the wheel; below, everything available ![Options › Quick menu](versions/2.0.0/screenshots/43-options-quick-menu.jpg) | **Options › Colours** – colours, opacities, saved schemes ![Options › Colours](versions/2.0.0/screenshots/44-options-colours.jpg) |
| **Options › Colours** – the saved scheme “oceanic” ![Options › Colours](versions/2.0.0/screenshots/45-options-colours-scheme-oceanic.jpg) | **Options › Colours** – the saved scheme “Fire” ![Options › Colours](versions/2.0.0/screenshots/46-options-colours-scheme-fire.jpg) |
| **Options › Slot conflicts** – free the game's slot pairs ![Options › Slot conflicts](versions/2.0.0/screenshots/47-options-slot-conflicts.jpg) | **Options › Tabs** – tab bar with icons and text, tabs switched off ![Options › Tabs](versions/2.0.0/screenshots/48-options-tabs.jpg) |
| **Options › Tabs** – icons only ![Options › Tabs](versions/2.0.0/screenshots/49-options-tabs-icons-only.jpg) | **Manage** – mods and their groups, with chips ![Manage](versions/2.0.0/screenshots/50-manage.jpg) |
| **Ragdolls** – a copy of Jodi, frozen in her pose ![Ragdolls](versions/2.0.0/screenshots/51-ragdolls-copy-of-jodi.jpg) | **Ragdolls** – zombies and their joints ![Ragdolls](versions/2.0.0/screenshots/52-ragdolls-joints.jpg) |
| **Ragdolls** – a saved pose, scenes of the level ![Ragdolls](versions/2.0.0/screenshots/53-ragdolls-poses-scenes.jpg) | **Followers** – backpack and storage box on top; figures with their clothes as tiles ![Followers](versions/2.0.0/screenshots/54-followers.jpg) |
| **Followers** – a follower and an NPC in the level ![Followers](versions/2.0.0/screenshots/55-followers-in-the-level.jpg) | **Codex** – the AltUI manual ![Codex](versions/2.0.0/screenshots/56-codex-manual.jpg) |
| **Codex** – the code locks of the level ![Codex](versions/2.0.0/screenshots/57-codex-passwords.jpg) | **Quick menu** – in the colours of the scheme “oceanic” ![Quick menu](versions/2.0.0/screenshots/58-quick-menu-scheme-oceanic.jpg) |
| **Quick menu** – in the colours of the scheme “Fire” ![Quick menu](versions/2.0.0/screenshots/59-quick-menu-scheme-fire.jpg) | **Main menu** – B: the menu scenes, the loading scene, the next camera, hiding the game's menu ![Main menu](versions/2.0.0/screenshots/60-main-menu-scenes.jpg) |
| **Loading screen** – Jodi as you made her ![Loading screen](versions/2.0.0/screenshots/61-loading-screen.jpg) | **Free camera** – a close-up ![Free camera](versions/2.0.0/screenshots/62-free-camera.jpg) |

## License

MIT – see `LICENSE`. AltUI is a fan project and not affiliated with the game's developer.
