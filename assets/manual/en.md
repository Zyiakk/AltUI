## About AltUI {#about}

AltUI is an alternative to the wardrobe and appearance screens of The Killing Antidote: one panel for all of it, and the game's own screens keep working. It opens anywhere in a level with B – no trips to the wardrobe or the mirror.

Every item from the game and from all installed mods is sorted into one list per slot, with search, filters, favourites and hiding. Hair, make-up, body, face, poses, weapons and saved outfits and looks are in the same panel, and so are ragdolls – copies of Jodi, zombies and people to place and pose – and Jodi's walk and run speed.

The panel opens on the tab it was left on. Tabs you do not use can be switched off under Options › Tabs.

An Inventory tab moves items between Jodi's backpack and the Hyper Storage Box, and looks become followers and NPCs who walk and fight with her.

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
- AltUI_Followers.sav – followers and NPCs
- the folder AltUI – photos of looks, faces and appearance presets
- the folder WeaponIcons – weapon pictures

Clothes, outfits, make-up and hair are stored in the game's own save files and stay.

After a game update, or with a mod that replaces tables of the game, AltUI may meet a game it was not made for. Then it shows a warning before it does anything: "Go on anyway (my own risk)" is remembered for this game version, "AltUI off for now" asks again in the next level.

## Controls {#controls}

- B opens and closes the panel (another key under Options › Controls); Esc closes it.
- Left click selects, wears or applies; right click opens the context menu of a tile, a row or a tab.
- The mouse wheel scrolls; the scroll speed is set under Options › Controls.
- While the panel is open Jodi cannot walk. Drag on the background to turn the camera; click on Jodi and drag to turn her – she turns back when the panel closes.
- + and − change the camera distance in 5 % steps, the mouse wheel over Jodi in 4 % steps.
- The three round buttons above + and − open a free camera (mouse turns, W A S D and Q E move, Shift is faster, the wheel sets the speed, Esc returns), the game's photo mode (Esc returns) and the ragdolls mode (see "Ragdolls mode").
- Undo and redo (five steps) are in the status bar at the bottom.
- Hold 4 for the quick menu (see "Quick menu").
- In the main menu, B opens a small menu: the three menu scenes and the loading scene, the next camera, and hiding the game's menu and texts (Esc brings them back).

## Clothes {#clothes}

The slots are on the left, the items of the chosen slot on the right.

- Click an item to wear it, click a worn item to take it off.
- The chips above the list filter by mod or group; "..." folds the chip rows. A search field narrows down the chips, the search above the list finds items by name, mod or group.
- Filters: only owned, only favourites, only vanilla, only worn.
- Right click on an item: favourite, hide, colour via the game's palette, reset colour, put in backpack, rename, only this group, view mod content, show in tab.
- Tooltips show which mod an item comes from.
- Damage (in the context menu): 0 to 100 %, live on a worn piece; on any other piece it is kept until the piece is worn. Worn pieces without damage textures have no slider.
- Under the game's colour palette a field shows the colour as #RRGGBB; type a code and press Enter to set it. "Remember" keeps the colour in AltUI, "Use" puts it on another piece or slot.
- The search also finds a mod by the name of its pak, here and in every other tab.

## Outfits {#outfits}

The game's saved outfits, the same ones the wardrobe and the mirror use.

- The "+" tile saves what Jodi wears now as a new outfit.
- Click an outfit to wear it.
- Right click: wear, view content, add to or remove from the quick menu, rename, move left / right / to start / to end, delete.
- An outfit without a name of its own is shown as "Outfit" with its place in the list.
- The tile size and how many pieces a tile shows are set under Options › Tiles.
- An outfit saved here keeps every colour slot of its pieces, as AltUI coloured them; the game itself keeps one colour per piece. An outfit saved at the mirror has only that one.

## Looks {#looks}

A look is everything at once: clothes with their colours, hairstyle and hair colour, make-up, eyes, skin, body sliders, body mod and face.

- The "+" tile saves the current look with a full-body photo – from the front or as you see her.
- Click a look to apply it.
- Right click: view content, rename, update (photo from the front or as seen), move, delete, add to or remove from the quick menu.
- Right click also: "Spawn as ragdoll", "Spawn as follower", "Spawn as NPC" (see "Ragdolls" and "Followers").
- Right click "Clean copy (without missing parts)" – only shown when the look holds pieces of a mod that is no longer installed, or make-up / eye rows no table has: a new look right after it without those entries, with the same photo. The original stays as it is; saving a look again never removes them by itself.

## Backpack {#bag}

What Jodi wears and what she carries.

- Click a worn item to take it off, a carried one to wear it.
- Right click: wear or take off, repair (needs a sewing kit), remove from backpack, back to the wardrobe.
- "Tidy up backpack" removes the items that are not worn and are also in the wardrobe.
- "Everything into the backpack" takes off every worn item and puts it into the backpack.
- The context menu also has the damage slider (see "Clothes").

## Inventory {#inventory}

Jodi's items and the Hyper Storage Box, one list under the other.

- The chips filter by the game's groups (weapons, ammo, weapon accessories, tools …). The weight shows what Jodi carries, what she can carry and how far she is overloaded.
- A click puts one item into the box or takes one out. Right click: half or all, use, inspect, discard, quick slot 1 or 2, unload ammo, "Accessories…" (opens the gun in the Weapons tab).
- The context menu of a stack ends with "Amount": a slider and a number field, and below one entry per target with that number ("Put 5 in the box", "Take 5"). Enter in the field runs the first entry. In the catalogue the number counts pieces and the field takes more than the slider reaches. Guns and single items have no amount.
- "Discard all" puts one object on the ground per pack. From 100 objects on a window asks first: "Cancel", "Destroy instead" (the items are gone, nothing falls) or "Drop anyway" – that many objects with physics at once can crash the game. Esc cancels.
- Everything goes through the game's own functions, so the game's rules stay – overloading included.
- "..." above a list folds it, ↑↓ gives it the full height (click again: back).
- On maps where the game never saves the backpack (the shooting range, for example) the tab says so: keep what you want in the box.
- "All items" is off by default (Options › General): every item of the game as a third list with its own search. A click puts one pack into the backpack; right click: five, or into the box.
- "Auto-equip weapons" (Options › General, on by default): a gun from the box or the catalogue goes into Jodi's hand as in the game; off, she keeps what she holds.
- The tile size of this tab is set under Options › Tiles.

## Coiffure {#hair}

All hairstyles from the game and from mods.

- Click a hairstyle to wear it.
- "Hair colour..." opens the game's palette; "Natural hair colours" shows 14 ready-made colours.
- Right click: add to / remove from favourites, reset hair colour, rename, view mod content.
- Favourites stand at the top, above all hairstyles.
- Right click on a hairstyle from a mod: "Rename mod…".

## Poses {#poses}

Every action animation the game and your pose mods know – the list behind the "rhythm" app of the phone.

- Click a pose to play it; click again or press "Stop pose" to stop.
- Poses are sorted by stance (standing, sitting, lying) and by chapter; chips filter by mod, the search finds titles.
- Right click: favourite, hide, mark as standing / sitting / lying / in motion, rename, add to the quick menu.
- Right click "Use as idle": the pose starts after 1.5 s of standing still and ends when Jodi walks, draws a weapon or crouches; "No longer as idle" switches it off.
- "Measure all" plays every pose that has no stance yet once and sorts it.
- A speaker in the corner of a tile marks a pose with a sound.
- "Measure all" shows the name of the pose being measured.
- "Repeat poses: on" in the status bar starts a pose that ends by itself again, until Jodi moves, the use key or "Stop pose" ends it, or another pose is chosen. Many pose mods repeat their poses anyway.

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
- Weapon accessories: one row per slot the weapon takes (sights, barrel, grip, magazine), "None" first. Parts come from the backpack, or from the storage box and are taken into the backpack. Accessories only go on weapons Jodi carries; the weapon keeps the model, skin and sound chosen here.
- "Show item pictures" in the status bar puts the item's or the mod's own picture on every tile instead of the rendered one.
- Right click on a model, skin or sound from a mod: "Rename mod…".

## Appearance {#look}

Skin, every make-up type, eyes and the game's appearance presets.

- Click an entry to put it on. Right click on make-up: tint with the game's palette, reset the tint.
- Eyes: iris and eyelash colour in the context menu.
- Presets: the "+" tile saves the current appearance with a photo. Right click: apply, view content, rename, update, move, delete, quick menu.

## Body Shape {#body}

- Breast and waist sliders of the game.
- Chips switch between the game's body and every converted body mod.
- Converted bodies also get bone-scale sliders: scale, bust, waist, glutes and hips, thighs, calves, arms, hands, feet. They are kept per body; "Reset shape" sets them back.
- Breast and glutes & hips: jiggle (0 % = animation only) adjusts the game's physics and works on every body; a bra still dampens as in the game. The nipple slider only works while the chest is uncovered. Angle and hip width exist only on converted bodies; the angle shows the more, the less jiggle there is (not at all at 100 %).
- Body replacer mods have to be converted with bodypak.pyz first; see the BODY_MODS guide on the mod's page.

## Face {#face}

Jodi's facial expression.

- Sliders for the game's expressions (relaxed, focused, smile, pain, fright, tired, suffering), gaze and mouth shapes.
- "Eyes closed" (under Gaze) closes the eyes, from open to fully shut; the game's own blinking goes on as before. Only on converted bodies, like the body sliders.
- A ticked entry keeps its value, also in poses; an unticked one is left to the game's animation. "Fix all" and "All to the game" switch every entry at once.
- Expressions are blended (together at most 100 %) or added up.
- The "+" tile saves the current face with a photo. Right click: apply, view content, rename, update, move, delete.

## Mods {#mods}

Settings of other mods that register with AltUI: their entries on the left, the chosen one's toggles, sliders, numbers, choices, colours, text fields, keys and buttons on the right.

This tab only appears when such a mod is installed.

## Options {#options}

The categories are on the left.

- General: language, how much of the screen stays free for Jodi, underwear may be taken off, how items you do not own are shown, the Codex switch for the encyclopedia, the "All items" catalogue and "Auto-equip weapons" for the Inventory tab. "No notices" hides every notice at the bottom, AltUI's and the game's own.
- Tiles: tile size, own sizes for outfit, look and ragdoll tiles, pieces per outfit tile, no limit on long lists, tooltip details, the tile size of the Inventory tab.
- Groups: merge groups or mods with the same name, length of group names, height of the chip area, chip search.
- Camera: field of view, distance, height, camera follows the chosen slot. Two switches for the free camera (also in the ragdolls mode): no collision – it flies through walls and Jodi – and any distance from Jodi.
- Controls: panel key, scroll speed, camera height with the right mouse button, how far the mouse wheel lifts a ragdoll per notch.
- Movement: Jodi's own walk and run speed (50 to 200 %); crouching and jumping stay as they are. "Slow motion on" switches slow motion, "Slow motion speed" (5 to 90 %, default 25 %) sets how slow it runs; the quick menu entry "Slow motion on / off" does the same as the switch. "Reset to default" sets walk, run and slow motion speed back. "Standing" picks Jodi's idle: the game's standing animations (looking around, checking nails, checking leg, careful, injured, posing) and those of installed idle mods (IdleAltUI_…).
- Quick menu: its key, its opacity, what is in the wheel, own keys.
- Theme: every panel colour and its opacity, a background picture (fill, alignment, hue, sepia, invert, its own opacity) and a picture for tiles and tabs, colour schemes saved under a name; reset is in the status bar. A theme saved now keeps the pictures and their settings too. Your own pictures: Background_1 … Background_30 and Button_1 … Button_30 (.png, .jpg or .jpeg) in the folder the page names. "Show previews" shows the pictures themselves on their chips; right click on the preview of an own picture: "Redo preview".
- Slot conflicts: free the game's slot pairs (for example bra and shirt) so both can be worn. Below: "Several pieces in one slot" – a slot switched on keeps its pieces when another one is put on (for example knee socks over tights), for Jodi, followers and looks.
- Tabs: text, icons or both in the tab bar; switch tabs off. "Try to fit in one row": the captions get smaller and then shorter, so the bar fits on one row where it can.

## Manage {#manage}

Your own display names for mods, groups, clothes, hairstyles, skins, make-up, poses and appearance presets.

- The names are used everywhere in the panel and found by the search; the original identifier stays searchable and shows in the tooltip.
- Chips and a search filter the list; "only mods" hides the game's own entries; ↺ goes back to the default name.
- With altui_names.pyz the names can be exported to a text file and imported again.
- Weapon mods are listed with the other mods.

## Ragdolls {#ragdolls}

Figures with physics to place in the level and pose: copies of Jodi, zombies and people.

- "+ Spawn a copy of Jodi" puts a copy in front of her, standing and frozen in her current pose, with everything she wears. A look becomes a figure with "Spawn as ragdoll" in its context menu.
- "Zombies and people": one picture tile per kind of zombie, plus the nurse and a survivor. A click spawns it; the links under a tile spawn its variants.
- The mercenary is a kind of figure too; he keeps his rifle in his hands.
- Every figure has a row: active (physics, it falls and can be thrown) or frozen (it keeps its pose), "joints ›", lock all, free all, remove. Bottom right in the status bar: "Remove all" (removes every figure) and "Joint spheres: on/off".
- "joints ›" opens the 17 joints of the figure, each with two switches: locked/free and movable/fixed. A locked joint stays stiff while the figure is active; a movable one can be posed on the frozen figure.
- Joint spheres show where you can grab: grey, red = locked, green = movable, blue = pinned. Hidden ones shimmer pale through the body; a click on a sphere grabs exactly that joint. They show only on this tab and in the Ragdolls mode.
- Poses (in the opened row): a name and "save pose" keep how the body parts are placed and which joints are locked or movable. A pose loads onto every figure of the same kind, in every level – a click loads, right click: load / delete. The figure freezes and stands on the floor.
- Scenes: "Save scene as" keeps every figure of the level with its look, place, pose and joints; the same name in the same level overwrites. Only the scenes of the current level are shown. A click loads a scene and replaces the figures that are there; right click: load / delete.

With the mouse on a figure, beside the panel and in the ragdolls mode:

- Left drag on a frozen figure moves it over the floor; the mouse wheel lifts or lowers it while you drag.
- Left drag on an active figure grabs the body part under the mouse; let go and it falls.
- A right click while dragging pins the part where it is; the rest of the figure hangs on it. Grab it again and it is free. "release all" in the figure's row frees them all.
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

## Followers {#followers}

Looks as people in the game: a follower walks with Jodi, fights and takes orders; an NPC stays where it is and defends itself.

- In the Looks tab, right click a look: "Spawn as follower" or "Spawn as NPC". The figure appears in front of Jodi wearing that look.
- The tab "Followers" lists every figure with its status (follows, waits, NPC, inactive, fallen) and chips: "Follow me", "Wait here", "Bring here", → NPC / → Follower, "Active", "Invulnerable" and "..." (rename, change look, revive, remove).
- Click a row to select the figure. The backpack (left) and the storage box (right) are at the top: a click gives one item to the selected figure, a gun with its paint and accessories. A click on one of the figure's own tiles gives it back into the backpack; right click: everything, or into the box. "..." above a list folds it.
- The context menu of a stack – Jodi's or the figure's – has the amount row as in the Inventory tab: "Give 5", "Take 5", into the box.
- Clothes are real pieces of the figure, as with the game's NPCs: they take damage, can tear off and show up in the game's own NPC inventory, where you can swap them too. Under a figure, its pieces are tiles (a badge marks damaged ones): a click takes one off into Jodi's backpack; right click: repair with a sewing kit from Jodi's backpack, or repair all. In the backpack column, "Clothes" lists Jodi's pieces: a click gives one to the selected figure, which puts it on (her damage and colours go along).
- "Active" off takes a figure out of the world, with everything it carries; on again, it comes back in front of Jodi.
- A figure that is not invulnerable can fall. It stays in the list and "Revive" brings it back with what it carried. Figures never turn into zombies.
- "Remove" asks first; the figure's items and guns go into the storage box, its clothes into Jodi's backpack.
- "Change look" switches to the Looks tab: click the look the figure should wear.
- Every figure wears the make-up of its look and has one of the game's NPC voices. A figure made with AltUI before 2.2.0 shows Jodi's make-up until "Change look…" gives it its own.

AltUI keeps the figures in a save of its own (AltUI_Followers.sav), the game's save never contains them. Following followers come along to every level and after loading; waiting followers and NPCs stay in their level at their place.

Quick menu: "Follower: follow me / wait here" orders the follower in view, "All followers: follow / wait" all of them. "All followers: come to me" brings every active follower to the places in front of Jodi – also one waiting in another level.

## Codex {#kodex}

- Encyclopedia: the entries of the archive on Jodi's office computer, with picture and text. Only the ones the game has unlocked are shown – or all of them with the switch under Options › General.
- Passwords: the code locks of the current level, nearest first, with how far away they are and whether they are locked. Each code stays hidden until you click it.
- AltUI manual: this text.

## Quick menu {#quick}

Hold 4 (another key under Options › Quick menu) and a wheel opens around the mouse. Let go on an item to run it; let go in the middle to do nothing.

- Items: outfits, looks, faces, appearance presets, poses, tabs, settings of other mods and actions: free camera, photo mode, ragdolls mode, a copy of Jodi as a ragdoll, switch every ragdoll between active and frozen, activate / freeze the one in view, remove all ragdolls, own speed on / off.
- More actions: "Slow motion on / off", "Stop time / go on" (everything stands still; the panel and the cameras keep working; also the camera of the game's photo mode), "Hide / show Jodi" (with clothes, hair and weapon; she is back in the next level) and the orders for followers (see "Followers").
- "Hide / show the game's UI" switches the game's HUD off and on, as its photo mode does.
- Own keys: under Options › Quick menu, right click an item under "Available" and press a key – the item then runs on that key, with the panel closed, also in the free camera and in the game's photo mode. Click the key of a row for another one, ✕ removes it. The panel key, the quick menu key and a key already given are refused; a key the game uses itself triggers both.
- Add them under Options › Quick menu, or with a right click on a tile, a tab or a mod's entry ("Add to quick menu").
- The order in the wheel is the order in the list under Options › Quick menu.

## For mod authors {#modding}

- Clothes mods need nothing special: AltUI reads the game's tables and sorts every item by slot.
- Body and weapon replacer mods can be converted with bodypak.pyz and weaponpak.pyz so that several can be installed side by side; they can also be built for AltUI directly in the Unreal Editor.
- Idle mods (a pak that replaces Jodi's idle animation) can be converted with idlepak.pyz: python3 idlepak.pyz <mod>.pak. The new IdleAltUI_….pak goes into Mods/ and appears under Options › Movement › "Standing"; the game's own idle stays. AltUI must be installed: the converter builds the new pak partly from AltUI.pak and looks for it in the usual Steam folders; if it is somewhere else, give the path with --altui <path to AltUI.pak>.
- Mods can show their settings in the Mods tab through two data tables and an interface; MOD_UI.md in the source repository describes how.
