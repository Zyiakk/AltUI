## About AltUI {#about}

AltUI replaces the wardrobe and appearance screens of The Killing Antidote with one panel. It opens anywhere in a level with B – no trips to the wardrobe or the mirror.

Every item from the game and from all installed mods is sorted into one list per slot, with search, filters, favourites and hiding. Hair, make-up, body, face, poses, weapons and saved outfits and looks are in the same panel, and so are ragdolls – copies of Jodi, zombies and people to place and pose – and Jodi's walk and run speed.

The panel opens on the tab it was left on. Tabs you do not use can be switched off under Options › Tabs.

## Installation and updates {#install}

AltUI.pak holds the whole mod and goes into TheKillingAntidote/Mods/. One more file starts it:

- the Blueprint Loader (a separate small mod, TKA_BlueprintLoader.pak in TheKillingAntidote/Content/Paks/~mods/), or
- AltUI's own hook, AltUI_Hook_P.pak in the same ~mods/ folder.

Either one is enough; both together work as well. With AltUI.pak alone, B does nothing.

An update normally only replaces AltUI.pak. The changelog says when the hook changes too; an old hook must not stay in ~mods/.

To remove AltUI, delete the files you copied:

- TheKillingAntidote/Mods/AltUI.pak
- TheKillingAntidote/Content/Paks/~mods/AltUI_Hook_P.pak – if you use the hook
- TheKillingAntidote/Content/Paks/~mods/TKA_BlueprintLoader.pak – only if no other mod needs it

AltUI keeps its own data in the game's save folder, on Windows %LOCALAPPDATA%\TheKillingAntidote\Saved\SaveGames. To remove everything, delete these there too:

- AltUI.sav – settings and choices
- AltUI_Looks.sav – saved looks
- AltUI_Faces.sav – saved faces
- AltUI_Names.sav – your own names
- AltUI_Ragdolls.sav – ragdoll scenes and poses
- the folder AltUI – photos of looks, faces and appearance presets
- the folder WeaponIcons – weapon pictures

Clothes, outfits, make-up and hair are stored in the game's own save files and stay.

## Controls {#controls}

- B opens and closes the panel (another key under Options › Controls); Esc closes it.
- Left click selects, wears or applies; right click opens the context menu of a tile, a row or a tab.
- The mouse wheel scrolls; the scroll speed is set under Options › Controls.
- While the panel is open Jodi cannot walk. Drag on the background to turn the camera; click on Jodi and drag to turn her – she turns back when the panel closes.
- + and − change the camera distance in 5 % steps, the mouse wheel over Jodi in 4 % steps.
- The three round buttons above + and − open a free camera (mouse turns, W A S D and Q E move, Shift is faster, the wheel sets the speed, Esc returns), the game's photo mode (Esc returns) and the ragdolls mode (see "Ragdolls mode").
- Undo and redo (five steps) are in the status bar at the bottom.
- Hold 4 for the quick menu (see "Quick menu").

## Clothes {#clothes}

The slots are on the left, the items of the chosen slot on the right.

- Click an item to wear it, click a worn item to take it off.
- The chips above the list filter by mod or group; "..." folds the chip rows. A search field narrows down the chips, the search above the list finds items by name, mod or group.
- Filters: only owned, only favourites, only vanilla, only worn.
- Right click on an item: favourite, hide, colour via the game's palette, reset colour, put in backpack, rename, only this group, view mod content, show in tab.
- Tooltips show which mod an item comes from.

## Outfits {#outfits}

The game's saved outfits, the same ones the wardrobe and the mirror use.

- The "+" tile saves what Jodi wears now as a new outfit.
- Click an outfit to wear it.
- Right click: wear, view content, add to or remove from the quick menu, rename, move left / right / to start / to end, delete.
- An outfit without a name of its own is shown as "Outfit" with its place in the list.
- The tile size and how many pieces a tile shows are set under Options › Tiles.

## Looks {#looks}

A look is everything at once: clothes with their colours, hairstyle and hair colour, make-up, eyes, skin, body sliders, body mod and face.

- The "+" tile saves the current look with a full-body photo – from the front or as you see her.
- Click a look to apply it.
- Right click: view content, rename, update (photo from the front or as seen), move, delete, add to or remove from the quick menu.

## Backpack {#bag}

What Jodi wears and what she carries.

- Click a worn item to take it off, a carried one to wear it.
- Right click: wear or take off, repair (needs a sewing kit), remove from backpack, back to the wardrobe.
- "Tidy up backpack" removes the items that are not worn and are also in the wardrobe.
- "Everything into the backpack" takes off every worn item and puts it into the backpack.

## Coiffure {#hair}

All hairstyles from the game and from mods.

- Click a hairstyle to wear it.
- "Hair colour..." opens the game's palette; "Natural hair colours" shows 14 ready-made colours.
- Right click: reset hair colour, rename, view mod content.

## Poses {#poses}

Every action animation the game and your pose mods know – the list behind the "rhythm" app of the phone.

- Click a pose to play it; click again or press "Stop pose" to stop.
- Poses are sorted by stance (standing, sitting, lying) and by chapter; chips filter by mod, the search finds titles.
- Right click: favourite, hide, mark as standing / sitting / lying / in motion, rename, add to the quick menu.
- "Measure all" plays every pose that has no stance yet once and sorts it.

## Weapons {#weapons}

One entry per weapon on the left, melee weapons included. For each weapon, its model, its skin and its shot sound are chosen separately.

- Above: the models – the game's own and every installed weapon model mod.
- Below: the skins – the game's gun paints (no spray can needed) and every installed skin mod.
- Sound: the weapon's own shot sound ("Original") and every installed shot sound made for it. A click picks the sound and plays it; every other weapon keeps its own. A mounted suppressor with a sound of its own still wins.
- The chips above filter all three sections at once. Right click on a tile: favourite, hide, only this mod.
- The choice is kept and put on again when the weapon is picked up or taken out of the storage box.
- A paint put on with a spray can in the game is kept: it becomes the chosen skin.
- Right click on a mod model: force skins onto it, leave the magazine, optics, suppressor or grip out, show the mod's own picture.
- Weapon mods and shot sound mods have to be converted with weaponpak.pyz first; see the WEAPON_MODS guide on the mod's page.

## Appearance {#look}

Skin, every make-up type, eyes and the game's appearance presets.

- Click an entry to put it on. Right click on make-up: tint with the game's palette, reset the tint.
- Eyes: iris and eyelash colour in the context menu.
- Presets: the "+" tile saves the current appearance with a photo. Right click: apply, view content, rename, update, move, delete, quick menu.

## Body Shape {#body}

- Breast and waist sliders of the game.
- Chips switch between the game's body and every converted body mod.
- Converted bodies also get bone-scale sliders: scale, bust, waist, glutes and hips, thighs, calves, arms, hands, feet. They are kept per body; "Reset shape" sets them back.
- Body replacer mods have to be converted with bodypak.pyz first; see the BODY_MODS guide on the mod's page.

## Face {#face}

Jodi's facial expression.

- Sliders for the game's expressions (relaxed, focused, smile, pain, fright, tired, suffering), gaze and mouth shapes.
- A ticked entry keeps its value, also in poses; an unticked one is left to the game's animation. "Fix all" and "All to the game" switch every entry at once.
- Expressions are blended (together at most 100 %) or added up.
- The "+" tile saves the current face with a photo. Right click: apply, view content, rename, update, move, delete.

## Mods {#mods}

Settings of other mods that register with AltUI: their entries on the left, the chosen one's toggles, sliders, numbers, choices, colours, text fields, keys and buttons on the right.

This tab only appears when such a mod is installed.

## Options {#options}

The categories are on the left.

- General: language, how much of the screen stays free for Jodi, underwear may be taken off, how items you do not own are shown, the Codex switch for the encyclopedia.
- Tiles: tile size, own sizes for outfit, look and ragdoll tiles, pieces per outfit tile, no limit on long lists, tooltip details.
- Groups: merge groups or mods with the same name, length of group names, height of the chip area, chip search.
- Camera: field of view, distance, height, camera follows the chosen slot.
- Controls: panel key, scroll speed, camera height with the right mouse button.
- Movement: Jodi's own walk and run speed (50 to 200 %, "Reset to 100 %"); crouching and jumping stay as they are.
- Quick menu: its key, its opacity, what is in the wheel.
- Colours: every panel colour, opacities, colour schemes saved under a name.
- Slot conflicts: free the game's slot pairs (for example bra and shirt) so both can be worn.
- Tabs: text, icons or both in the tab bar; switch tabs off.

## Manage {#manage}

Your own display names for mods, groups, clothes, hairstyles, skins, make-up, poses and appearance presets.

- The names are used everywhere in the panel and found by the search; the original identifier stays searchable and shows in the tooltip.
- Chips and a search filter the list; "only mods" hides the game's own entries; ↺ goes back to the default name.
- With altui_names.pyz the names can be exported to a text file and imported again.

## Ragdolls {#ragdolls}

Figures with physics to place in the level and pose: copies of Jodi, zombies and people.

- "+ Spawn a copy of Jodi" puts a copy in front of her, standing and frozen in her current pose, with everything she wears. A look becomes a figure with "Spawn as ragdoll" in its context menu.
- "Zombies and people": one picture tile per kind of zombie, plus the nurse and a survivor. A click spawns it; the links under a tile spawn its variants.
- Every figure has a row: active (physics, it falls and can be thrown) or frozen (it keeps its pose), "joints ›", lock all, free all, remove. "Remove all" removes every figure.
- "joints ›" opens the 17 joints of the figure, each one locked, free or movable. A locked joint stays stiff while the figure is active.
- Poses (in the opened row): a name and "save pose" keep how the body parts are placed. A pose loads onto every figure of the same kind, in every level – a click loads, right click: load / delete. The figure freezes and stands on the floor.
- Scenes: "Save scene as" keeps every figure of the level with its look, place, pose and joints; the same name in the same level overwrites. Only the scenes of the current level are shown. A click loads a scene and replaces the figures that are there; right click: load / delete.

With the mouse on a figure, beside the panel and in the ragdolls mode:

- Left drag on a frozen figure moves it over the floor; the mouse wheel lifts or lowers it while you drag.
- Left drag on an active figure grabs the body part under the mouse; let go and it falls.
- Right drag turns the figure about its hips.
- Shift + left click locks or frees the joint you click.
- Shift + right click on a frozen figure makes the joint movable. Left drag on a body part below a movable joint then moves only that part; it stays where you let go – that is how a figure is posed.

Without the panel, the quick menu activates or freezes figures: "Ragdoll: activate / freeze the one in view" takes the figure in the middle of the screen, "Ragdolls: active / frozen" switches all of them.

## Ragdolls mode {#ragmode}

Moves and poses the figures without the panel, with the camera free in the room. Start it with the third round button above + and − or from the quick menu.

- The mouse pointer stays visible; on a figure everything works as beside the panel (see "Ragdolls").
- W A S D and Q E move the camera, Shift is faster; Shift + mouse wheel sets the speed.
- Drag on nothing to turn the camera.
- Esc or B ends the mode.

## Codex {#kodex}

- Encyclopedia: the entries of the archive on Jodi's office computer, with picture and text. Only the ones the game has unlocked are shown – or all of them with the switch under Options › General.
- Passwords: the code locks of the current level, nearest first, with how far away they are and whether they are locked. Each code stays hidden until you click it.
- AltUI manual: this text.

## Quick menu {#quick}

Hold 4 (another key under Options › Quick menu) and a wheel opens around the mouse. Let go on an item to run it; let go in the middle to do nothing.

- Items: outfits, looks, faces, appearance presets, poses, tabs, settings of other mods and actions: free camera, photo mode, ragdolls mode, a copy of Jodi as a ragdoll, switch every ragdoll between active and frozen, activate / freeze the one in view, remove all ragdolls, own speed on / off.
- Add them under Options › Quick menu, or with a right click on a tile, a tab or a mod's entry ("Add to quick menu").
- The order in the wheel is the order in the list under Options › Quick menu.

## For mod authors {#modding}

- Clothes mods need nothing special: AltUI reads the game's tables and sorts every item by slot.
- Body and weapon replacer mods can be converted with bodypak.pyz and weaponpak.pyz so that several can be installed side by side; they can also be built for AltUI directly in the Unreal Editor.
- Mods can show their settings in the Mods tab through two data tables and an interface; MOD_UI.md in the source repository describes how.
