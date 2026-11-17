## About AltUI {#about}

AltUI is an alternative to the wardrobe and appearance screens of The Killing Antidote: one panel for all of it.

### At a glance
- The game's own screens keep working.
- It opens anywhere in a level with B – no trips to the wardrobe or the mirror.
- The panel opens on the tab it was left on. Tabs you do not use can be switched off under Options › Tabs. A switched-off tab costs nothing; what you set there keeps working.

### What is in it
- Every item from the game and from all installed mods, sorted into one list per slot, with search, filters, favourites and hiding.
- Hair, make-up, body, face, poses, weapons and saved outfits and looks.
- Ragdolls: copies of Jodi, zombies and people to place and pose.
- Jodi's walk and run speed.
- An Inventory tab moves items between Jodi's backpack and the Hyper Storage Box.
- Looks become followers and NPCs who walk and fight with her.

## Installation and updates {#install}

AltUI.pak holds the whole mod and goes into TheKillingAntidote/Mods/.

### Installation
One more file starts it:
- the Blueprint Loader (a separate small mod): TKA_BlueprintLoader.pak in TheKillingAntidote/Content/Paks/~mods/, or
- AltUI's own hook: AltUI_Hook_P.pak in the same ~mods/ folder.
- Either one is enough; both together work as well.
- With AltUI.pak alone, B does nothing.

### Updates
- An update normally only replaces AltUI.pak.
- The changelog says when the hook changes too; an old hook must not stay in ~mods/.

### Game version warning
- After a game update, or with a mod that replaces tables of the game, AltUI may meet a game it was not made for. Then it shows a warning before it does anything.
- "Go on anyway (my own risk)" is remembered for this game version.
- "AltUI off for now" asks again in the next level.

### Removing AltUI
Delete the files you copied:
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
- AltUI_Drawers.sav – clothes drawers
- AltUI_BodyPresets.sav – body presets
- AltUI_ModPresets_<mod>.sav – presets of a mod's settings (Mods tab), one file per mod
- AltUI_Props.sav – placed objects and object scenes
- AltUI_ObjCache.sav – the objects the mod search found
- AltUI_ModScan.sav – which mod each piece comes from; written anew by itself
- AltUI_Log.sav, BPLoader_Log.sav – only from test builds
- the folder AltUI – photos of looks, faces, appearance, body and mod presets, your own background and button images
- the folder WeaponIcons – weapon pictures
- the folder ObjectIcons – object pictures

Clothes, outfits, make-up and hair are stored in the game's own save files and stay.

## Controls {#controls}

Keys and mouse in the panel, around Jodi and while you play.

### Panel
- B opens and closes the panel (another key under Options › Controls); Esc closes it.
- Left click selects, wears or applies; right click opens the context menu of a tile, a row or a tab.
- The mouse wheel scrolls; the scroll speed is set under Options › Controls.
- Undo and redo (five steps) are in the status bar at the bottom.
- Hold 4 for the quick menu (see "Quick menu").

### Camera and Jodi
- While the panel is open Jodi cannot walk.
- Drag on the background to turn the camera.
- Click on Jodi and drag to turn her – she turns back when the panel closes.
- + and − change the camera distance in 5 % steps, the mouse wheel over Jodi in 4 % steps.

### While you play
- With the panel closed, the mouse wheel moves the camera closer to Jodi or further away.
- With the quick menu entry "Camera height (wheel)" it moves the camera up or down instead (left click or Esc ends that).
- Aiming keeps the game's view. Distance and height are kept.

### Round buttons
The round buttons above + and −:
- A free camera: the mouse turns, W A S D and Q E move, Shift is faster, the wheel sets the speed, Esc returns.
- The game's photo mode (Esc returns).
- The ragdolls mode (see "Ragdolls mode").
- The topmost one (the bulb) is the camera light: it lights up what the camera sees – beside the panel, in the free camera and in photo mode.
- A click on the bulb opens a small menu: on / off, the light's colour (palette) and a brightness slider.
- The light only brightens (no shine spots, no beam in fog). It is off while you play and comes back as you left it when the panel opens again.

### Main menu
- In the main menu, B opens a small menu: the three menu scenes and the loading scene, the next camera, and hiding the game's menu and texts (Esc brings them back).

## Clothes {#clothes}

The slots are on the left, the items of the chosen slot on the right.

### Wearing and finding
- Click an item to wear it, click a worn item to take it off.
- The chips above the list filter by mod or group; "..." folds the chip rows.
- A search field narrows down the chips; the search above the list finds items by name, mod or group.
- The search also finds a mod by the name of its pak, here and in every other tab.
- Filters: only owned, only favourites, only vanilla, only worn.
- Tooltips show which mod an item comes from.

### Context menu
- Right click on an item: favourite, keep on, hide, colour via the game's palette, reset colour, put in backpack, rename, only this group, view mod content, show in tab.
- Damage: 0 to 100 %, live on a worn piece; on any other piece it is kept until the piece is worn. Worn pieces without damage textures have no slider.

### Keep on
- A marked piece that you put on yourself stays on when you put on a look or an outfit.
- The look then leaves out pieces of the same slot (or of a slot that does not go with it) and names them in the notice.
- A piece that a look or outfit put on does not stay through the next change, even when it is marked – trying outfits never piles pieces up.
- The tile shows "kept on". Undo restores the state before exactly.

### Colour codes
- Under the game's colour palette a field shows the colour as #RRGGBB; type a code and press Enter to set it.
- "Remember" keeps the colour in AltUI, "Use" puts it on another piece or slot.

### Drawers
Your own collections of clothes, in a bar above the list.
- "Default" shows everything; "+" makes a new drawer ("Drawer 1", "Drawer 2" …).
- A drawer shows the same page – slots, chips, search, filters, favourites – with only its pieces, and the slots count only those.
- Right click on an item › "Drawer ›" opens the list of drawers next to the menu: a tick means the piece is in it, a click puts it in or takes it out, "+ New drawer" makes one with the piece in it.
- A piece can be in any number of drawers; inside a drawer the menu also has "Remove from this drawer".
- Right click on a drawer: rename (Enter keeps the name, Esc cancels), move left / right, delete (asks first – the pieces stay).
- The shown drawer is kept after a restart.

## Outfits {#outfits}

The game's saved outfits, the same ones the wardrobe and the mirror use.

### Saving and wearing
- The "+" tile saves what Jodi wears now as a new outfit.
- Click an outfit to wear it.
- An outfit without a name of its own is shown as "Outfit" with its place in the list.
- The tile size and how many pieces a tile shows are set under Options › Tiles.

### Context menu
- Right click: wear, view content, add to or remove from the quick menu, rename, move left / right / to start / to end, delete.
- "Update with what she wears": the outfit takes what Jodi wears now, in its current colours; name, place, quick menu entry and own key stay.

### Colours
- An outfit saved here keeps every colour slot of its pieces, as AltUI coloured them.
- The game itself keeps one colour per piece; an outfit saved at the mirror has only that one.

### Share
- Right click → "Export (share)…" shows it as text – Ctrl+A, Ctrl+C and send it.
- "Import…" at the bottom right: paste with Ctrl+V; "Check" lists what is in it and which mods are missing (what is already saved here exactly like this is left out).
- Then import everything or without the missing pieces.
- Photos are not shared – take a new one with "Update".

## Looks {#looks}

A look is everything at once: clothes with their colours, hairstyle and hair colour, make-up, eyes, skin, mutation, body sliders, body mod and face.

### Saving and applying
- The "+" tile saves the current look with a full-body photo: from the front, or with the free camera – fly it wherever you like and click to take the photo (Esc: the front photo instead).
- Click a look to apply it.

### Sorting
- "Sort: …" at the bottom right of the Looks tab (left or right click) opens a menu with seven orders: Custom, Name A–Z, Name Z–A, Newest first, Oldest first, Recently changed, Least recently changed. The active one is marked with ">".
- Custom keeps your own order – the one you get with "Move". Move is only offered in Custom; in the other orders the position follows the sorting.
- The dates are stored from this version on. Looks saved earlier have none: they count as the oldest in the date orders and show no date in the tooltip.
- Hover a look to see when it was created and last changed ("Created … · Changed …"). Renaming does not change the date; "Update" does. An imported look counts as new.
- The quick menu lists looks in the same order.

### Context menu
- Right click: view content, rename, update (photo from the front, with the free camera, or keeping the photo), move, delete, add to or remove from the quick menu.
- "View content" lists the body values in the order of the Body Shape page, with its headings "Breast" and "Glutes & hips" above angle and jiggle.
- Also: "Spawn as ragdoll", "Spawn as follower", "Spawn as NPC", "Spawn as enemy" (see "Ragdolls" and "Followers").

### Clean copy
- "Clean copy (without missing parts)" is only shown when the look holds pieces of a mod that is no longer installed, or make-up / eye rows no table has.
- It makes a new look right after it without those entries, with the same photo.
- The original stays as it is; saving a look again never removes them by itself.

### Share
- Right click → "Export (share)…" shows it as text – Ctrl+A, Ctrl+C and send it.
- "Import…" at the bottom right: paste with Ctrl+V; "Check" lists what is in it and which mods are missing (what is already saved here exactly like this is left out).
- Then import everything or without the missing pieces.
- Photos are not shared – take a new one with "Update".

## Backpack {#bag}

What Jodi wears and what she carries.

### Single items
- Click a worn item to take it off, a carried one to wear it.
- Right click: wear or take off, repair (needs a sewing kit), remove from backpack, back to the wardrobe.
- The context menu also has the damage slider (see "Clothes").

### Whole backpack
- "Tidy up backpack" removes the items that are not worn and are also in the wardrobe.
- "Everything into the backpack" takes off every worn item and puts it into the backpack.

## Inventory {#inventory}

Jodi's items and the Hyper Storage Box, one list under the other.

### Lists
- The chips filter by the game's groups (weapons, ammo, weapon accessories, tools …).
- The weight shows what Jodi carries, what she can carry and how far she is overloaded.
- "..." above a list folds it, ↑↓ gives it the full height (click again: back).
- The tile size of this tab is set under Options › Tiles.
- On maps where the game never saves the backpack (the shooting range, for example) the tab says so: keep what you want in the box.

### Moving items
- A click puts one item into the box or takes one out.
- Right click: half or all, use, inspect, discard, quick slot 1 or 2, unload ammo, "Accessories…" (opens the gun in the Weapons tab).
- The context menu of a stack ends with "Amount": a slider and a number field, and below one entry per target with that number ("Put 5 in the box", "Take 5"). Enter in the field runs the first entry.
- In the catalogue the number counts pieces and the field takes more than the slider reaches. Guns and single items have no amount.
- "Auto-equip weapons" (Options › General, on by default): a gun from the box or the catalogue goes into Jodi's hand as in the game; off, she keeps what she holds.
- Everything goes through the game's own functions, so the game's rules stay – overloading included.

### Discard all
- "Discard all" puts one object on the ground per pack.
- From 100 objects on a window asks first: "Cancel", "Destroy instead" (the items are gone, nothing falls) or "Drop anyway" – that many objects with physics at once can crash the game. Esc cancels.

### Always auto-equip
- "Always auto-equip" (right click, also on catalogue items): after every level load AltUI puts the item into Jodi's backpack, made anew, up to the amount the tile had when you marked it (at least one pack). It never takes anything away.
- Such tiles show a gold loop arrow and a gold frame. "Stop auto-equip" ends it.
- "Refill marked items in story mode too" (Options › General, on by default): off, AltUI fills nothing up on story levels; the marks stay and the office and challenges go on as before.
- A marked gun comes back as it was when you marked it (the one carried or the one in the box, from the catalogue without attachments), with a full magazine; a spare part in the backpack stays.
- If Jodi carries it with other attachments at a level load, they are set back and parts taken off go into the backpack.
- For a new setup, stop auto-equip and mark it again.

### All items
- "All items" is off by default (Options › General): every item of the game as a third list with its own search.
- A click puts one pack into the backpack; right click: five, or into the box.
- "Collectibles" also holds the game's Invisible Hand: while it is in the backpack it brings items near Jodi to her, one after another, faster with more hands (one every 2.5 s, from six on every 0.1 s).
- "Collectibles" in the backpack shows how many Jodi has.

## Coiffure {#hair}

All hairstyles from the game and from mods.

### Choosing
- Click a hairstyle to wear it.
- Favourites stand at the top, above all hairstyles.
- The search box above the tiles finds hairstyles by shown name, identifier, mod name and pak file; × clears it.

### Hair colour
- "Hair colour..." opens the game's palette.
- "Natural hair colours" shows 14 ready-made colours.

### Context menu
- Right click: add to / remove from favourites, reset hair colour, rename, view mod content.
- On a hairstyle from a mod also: "Rename mod…".

## Poses {#poses}

Every action animation the game and your pose mods know – the list behind the "rhythm" app of the phone.

### Playing
- Click a pose to play it; click again or press "Stop pose" to stop.
- "Repeat poses: on" in the status bar starts a pose that ends by itself again, until Jodi moves, the use key or "Stop pose" ends it, or another pose is chosen. Many pose mods repeat their poses anyway.
- A speaker in the corner of a tile marks a pose with a sound.

### Sorting and finding
- Poses are sorted by stance (standing, sitting, lying) and by chapter.
- Chips filter by mod, the search finds titles.
- "Measure all" plays every pose that has no stance yet once and sorts it; it shows the name of the pose being measured.

### Context menu
- Right click: favourite, hide, mark as standing / sitting / lying / in motion, rename, add to the quick menu.
- "Use as idle": the pose starts after 1.5 s of standing still and ends when Jodi walks, draws a weapon or crouches. "No longer as idle" switches it off.

## Weapons {#weapons}

One entry per weapon on the left, melee weapons included. For each weapon, its model, its skin and its shot sound are chosen separately. The choice is kept and put on again when the weapon is picked up or taken out of the storage box.

### Models and skins
- Above: the models – the game's own and every installed weapon model mod.
- Below: the skins – the game's gun paints (no spray can needed) and every installed skin mod.
- If a model mod brings its own versions of the game's gun paints (made for its model), they appear as extra skins next to the game's while that model is chosen.
- The model tiles show each model with the chosen skin.
- A model's own paint works only on its own model – on any other the weapon stays as it is, and so does its tile.
- A skin mod's tile is dimmed when the skin does nothing on the chosen model; that is known once the weapon has been in Jodi's hand with that model.
- A paint put on with a spray can in the game is kept: it becomes the chosen skin.

### Sound
- The weapon's own shot sound ("Original") and every installed shot sound made for it.
- A click picks the sound and plays it; every other weapon keeps its own.
- A mounted suppressor with a sound of its own still wins.

### Filters and context menu
- The chips above filter all three sections at once.
- Right click on a tile: favourite, hide, only this mod.
- Right click on a mod model: force skins onto it, leave the magazine, optics, suppressor or grip out, show the mod's own picture.
- Right click on a model, skin or sound from a mod: "Rename mod…".

### Pictures
- "Take pictures again" in the status bar renders every tile of the weapon anew.
- "Show item pictures" in the status bar puts the item's or the mod's own picture on every tile instead of the rendered one.

### Accessories
- One row per slot the weapon takes (sights, barrel, grip, magazine), "None" first.
- Parts come from the backpack, or from the storage box and are taken into the backpack.
- Accessories only go on weapons Jodi carries; the weapon keeps the model, skin and sound chosen here.

### Weapon mods
- Weapon mods and shot sound mods have to be converted with weaponpak.pyz first; see the WEAPON_MODS guide on the mod's page.

## Appearance {#look}

Skin, every make-up type, eyes and the game's appearance presets.

### Make-up and eyes
- Click an entry to put it on.
- Right click on make-up: tint with the game's palette, reset the tint.
- Eyes: iris and eyelash colour in the context menu.

### Oiled skin
- "Oiled skin" above the skins makes her skin glossy, as wet skin in the game (the game's own wet skin is 50 %).
- Ticked = your value, also against the story; unticked = the game decides again.
- Only on Jodi. Looks and appearance presets keep the setting; older ones bring "the game decides".

### Mutation
Jodi's mutated look from the story in parts.
- Skin colour and glow as sliders (ticked = on), veins and eyes as switches; "Reset" turns everything off.
- Make-up stays visible on the discoloured skin; your own iris colour tints the mutated eye.
- "Story look" sets the cutscene's look: the story's own skin material, every row at full; you can take single rows back afterwards. Make-up and scars are not visible with it.
- While the story mutates Jodi herself, the story's look applies.

### Presets
- The "+" tile saves the current appearance with a photo.
- Right click: apply, view content, rename, update, move, delete, quick menu.

### Share
- Right click a preset → "Export (share)…", "Import…" at the bottom right – as with looks.
- Without missing pieces, a missing hairstyle, skin or make-up row is left out.
- One text may mix looks, outfits, faces and every kind of preset; every page with "Import…" takes all of it.

## Body Shape {#body}

The game's breast and waist sliders, and more on converted body mods.

### Bodies
- Chips switch between the game's body and every converted body mod.
- Body replacer mods have to be converted with bodypak.pyz first; see the BODY_MODS guide on the mod's page.

### Sliders
- Breast and waist sliders of the game.
- Converted bodies also get bone-scale sliders: scale, bust, waist, glutes and hips, thighs, calves, arms, hands, feet.
- They are kept per body; "Reset shape" sets them back.
- The nipple slider only works while the chest is uncovered.

### Jiggle
- Breast and glutes & hips: jiggle (0 % = animation only) adjusts the game's physics and works on every body.
- A bra still dampens as in the game.
- Angle (only on converted bodies): the angle shows the more, the less jiggle there is (not at all at 100 %).

### Hips and legs
- Hip width and leg spacing exist only on converted bodies.
- Leg spacing moves the whole leg sideways, in cm per side.
- Hip width pushes the legs apart too (at 1.3× about -2 cm brings them back), but it costs a little hip width.

### Presets
- Above the sliders, "+" saves every slider of the page – the body's own and the game's breast and waist – with a photo as a preset of the selected body chip.
- Upper half of the "+": photo from the front; lower half: free camera.
- Each body chip shows only its own presets. "..." folds the presets away.
- A click loads one; right click: apply, rename, update, move, delete, quick menu.
- From the quick menu a preset switches to its body first.

### Share
- Right click a preset → "Export (share)…", "Import…" at the bottom right – as with looks.
- A preset goes to its body, even when that body is not here; it shows up once the body is converted.

## Face {#face}

Jodi's facial expression.

### Expressions
- Sliders for the game's expressions (relaxed, focused, smile, pain, fright, tired, suffering), gaze and mouth shapes.
- Expressions are blended (together at most 100 %) or added up.
- A ticked entry keeps its value, also in poses; an unticked one is left to the game's animation.
- "Fix all" and "All to the game" switch every entry at once.

### Eyes closed
- "Eyes closed" (under Gaze) closes the eyes, from open to fully shut; the game's own blinking goes on as before.
- Only on converted bodies, like the body sliders. On any other body these rows are greyed out; the tooltip says why.
- "Left eye closed" and "Right eye closed" close one eye (Jodi's left / right), e.g. for a wink.
- Each eye closes as far as the larger of its row and "Eyes closed".

### Saved faces
- The "+" tile saves the current face with a photo.
- Right click: apply, view content, rename, update, move, delete.
- Share: right click a face → "Export (share)…", "Import…" at the bottom right – as with looks.

## Mods {#mods}

Settings of other mods that register with AltUI: their entries on the left, the chosen one's toggles, sliders, numbers, choices, colours, text fields, keys and buttons on the right. This tab only appears when such a mod is installed.

### Tabs and sections
- A mod can split its page into tabs: they look like the tabs at the top and sit above its fields.
- What stands before the first tab stays visible on every tab.
- The fields of a tab and of every section lie on a light surface of their own, so you can see what belongs together.
- A heading with an arrow folds the fields below it with a click.
- AltUI remembers the chosen tab of every page and which sections are folded.

### Presets
- Above the fields: presets of the page. The "+" tile saves the current settings with a photo (from the front or with the free camera); a click applies a preset.
- Presets always hold the whole page, whichever tab is shown.
- Right click: apply, view content, rename, update, move, delete, quick menu.
- "View content" lists the values with a check box each: only ticked values are applied, unticked ones stay stored.
- The tabs and headings of the page stand above their values there too, so fields with the same name stay apart.
- Kept per mod in AltUI_ModPresets_<mod>.sav.
- "..." in the bar above the tiles folds the preset area of every mod page and opens it again.

### Presets a mod brings
- They come first.
- They can be applied, renamed, given a photo of your own ("New photo") and their values ticked or unticked – not changed or deleted.
- They can be hidden (right click "Hide"); "Show hidden presets" in the bar above the tiles brings this page's back.

### Share
- Right click an own preset → "Export (share)…", "Import…" at the bottom right – as with looks.
- Shipped presets come with the mod itself.
- An imported preset goes to its mod page, even when the mod is not installed; it shows up once it is.

## Options {#options}

The categories are on the left. What each one holds:

### General
- Language and how much of the screen stays free for Jodi.
- Underwear may be taken off; how items you do not own are shown.
- The Codex switch for the encyclopedia.
- The "All items" catalogue and "Auto-equip weapons" for the Inventory tab.
- "No notices" hides every notice at the bottom, AltUI's and the game's own.
- "Clothes follow the body shape" (off by default, converted bodies only): cloth that swings, like skirts and coats, stays closer to bigger breast, hip, glute, thigh and waist sliders instead of falling into the body; it swings less the bigger the shape.

### Tiles
- Tile size, own sizes for outfit, look and ragdoll tiles.
- Pieces per outfit tile, no limit on long lists.
- Tooltip details.
- The tile size of the Inventory tab.

### Groups
- Merge groups or mods with the same name.
- Length of group names, height of the chip area, chip search.

### Camera
- Field of view, distance, height, camera follows the chosen slot.
- Two switches for the free camera (also in the ragdolls mode): no collision – it flies through walls and Jodi – and any distance from Jodi.

### Controls
- Panel key, scroll speed, camera height with the right mouse button.
- How far the mouse wheel lifts a ragdoll per notch.

### Movement
Jodi's own walk and run speed (50 to 200 %); crouching and jumping stay as they are. "Reset to default" sets walk, run and slow motion speed back.

- "Jumping in the office" (off by default) lets Jodi jump and climb in her office, where the game blocks both; the Esc menu then pauses there too, as it does in the levels.
- "Slow motion on" switches slow motion, "Slow motion speed" (5 to 90 %, default 25 %) sets how slow it runs. The quick menu entry "Slow motion on / off" does the same as the switch.

Feet on the ground (off by default, only on converted bodies):
- "Feet follow the ground": feet stand on steps and slopes while Jodi stands still.
- "Knees and hands follow the ground": knees and hands lie on the floor in floor poses.
- Tip: leave the first on, switch the second on for poses. Foot IK by BenenG47.

Standing and walk styles:
- "Standing" picks Jodi's idle: the game's standing animations (looking around, checking nails, checking leg, careful, injured, posing) and those of installed idle mods (IdleAltUI_…).
- Walk / run mods (WalkAltUI_…) add chips to "Walk style" and "Run style"; those rows only show when there is a choice.
- A walk mod beats a run mod or an idle mod chosen at the same time: that side plays normal and says so under its row.

### Theme
- Every panel colour and its opacity.
- A background picture (fill, alignment, hue, sepia, invert, its own opacity) and a picture for tiles and tabs.
- Colour schemes saved under a name; a saved theme keeps the pictures and their settings too. Reset is in the status bar.
- Your own pictures: Background_1 … Background_30 and Button_1 … Button_30 (.png, .jpg or .jpeg) in the folder the page names.
- "Show previews" shows the pictures themselves on their chips. Right click on the preview of an own picture: "Redo preview".

### Slot conflicts
- Free the game's slot pairs (for example bra and shirt) so both can be worn.
- "Several pieces in one slot": a slot switched on keeps its pieces when another one is put on (for example knee socks over tights), for Jodi, followers and looks.

### Tabs
- Text, icons or both in the tab bar; switch tabs off.
- Right-click a tab in the bar to move it; "Tab order" puts the default order back.
- "Try to fit in one row": the captions get smaller and then shorter, so the bar fits on one row where it can.

## Manage {#manage}

Display names, the mods in use and sharing many things at once.

### Names
Your own display names for mods, groups, clothes, hairstyles, skins, make-up, poses and appearance presets.
- The names are used everywhere in the panel and found by the search; the original identifier stays searchable and shows in the tooltip.
- Chips and a search filter the list; "only mods" hides the game's own entries; ↺ goes back to the default name.
- Weapon mods are listed with the other mods.
- With altui_names.pyz the names can be exported to a text file and imported again.
- "Read mods again" (next to the search) reads anew which piece comes from which mod. AltUI keeps that between game starts and notices changed mods by itself; the link is for the case it does not.

### Usage
"Usage" shows which mods are in use right now.
- Per mod: the pieces in use and where they are (Jodi now, outfits, looks, presets, favourites, followers, ragdoll scenes, standing idle, weapons, object scenes and positions, clothes drawers).
- Object scenes and saved object positions count as use too (models from mods).
- Pieces that are only in the wardrobe do not count as in use.
- Unused mods are listed below in grey, as are mods whose use AltUI cannot detect (maps, script mods). "View content" opens any of them.
- Each mod is a tile with its shown name and its pak file; the places of a piece are summed up per kind (e.g. "Outfits 4–6, 8").
- The list is collected when you open "Usage"; elsewhere the number on the left is the one from the last time (none before the first time).

### Share
"Share" puts every look, outfit, face, appearance preset, body preset and own mod preset on one page.
- Grouped by kind ("all" / "none" per kind), with the body or the mod next to it.
- Tick them, then "Export (n)…" at the bottom right gives all ticked ones as one text; "Import…" next to it reads such a text.
- The ticks hold only while the page is open.
- Mod presets of mods that are not installed right now are not listed.

## Ragdolls {#ragdolls}

Figures with physics to place in the level and pose: copies of Jodi, zombies and people.

### Spawning
- "+ Spawn a copy of Jodi" puts a copy in front of her, standing and frozen in her current pose, with everything she wears.
- A look becomes a figure with "Spawn as ragdoll" in its context menu.
- "Zombies and people": one picture tile per kind of zombie, plus the nurse and a survivor. A click spawns it; the links under a tile spawn its variants.
- The mercenary is a kind of figure too; he keeps his rifle in his hands.

### Figure rows
- Every figure has a row: active (physics, it falls and can be thrown) or frozen (it keeps its pose), "joints ›", lock all, free all, remove.
- Bottom right in the status bar: "Remove all" (removes every figure) and "Joint spheres: on/off".

### Joints
- "joints ›" opens the 17 joints of the figure, each with two switches: locked/free and movable/fixed.
- A locked joint stays stiff while the figure is active; a movable one can be posed on the frozen figure.
- Joint spheres show where you can grab: grey, red = locked, green = movable, blue = pinned.
- Hidden ones shimmer pale through the body; a click on a sphere grabs exactly that joint.
- They show only on this tab and in the Ragdolls mode.

### Poses and scenes
- Poses (in the opened row): a name and "save pose" keep how the body parts are placed and which joints are locked or movable.
- A pose loads onto every figure of the same kind, in every level – a click loads, right click: load / delete. The figure freezes and stands on the floor.
- Scenes: "Save scene as" keeps every figure of the level with its look, place, pose and joints; the same name in the same level overwrites.
- Only the scenes of the current level are shown. A click loads a scene and replaces the figures that are there; right click: load / delete.

### Attackable
- "Make attackable" (Jodi copies, NPC and mercenary copies): zombies attack the ragdoll like a figure; its header then shows "· attackable".
- Every hit pushes the body part nearest to the zombie; a frozen ragdoll springs back into its pose about a second after the last hit.
- Ragdolls do not die. The state is saved with the scene.

### Mouse on a figure
Beside the panel and in the ragdolls mode:
- Left drag on a frozen figure moves it over the floor; the mouse wheel lifts or lowers it while you drag.
- Left drag on an active figure grabs the body part under the mouse; let go and it falls. The mouse wheel lifts or lowers the held point meanwhile.
- A right click while dragging pins the part where it is; the rest of the figure hangs on it. Grab it again and it is free. "release all" in the figure's row frees them all.
- Right drag turns the figure about its hips.

### Posing with the mouse
- Shift + left click locks or frees the joint you click.
- Shift + right click on a frozen figure makes the joint movable.
- Left drag on a body part below a movable joint then moves only that part; it stays where you let go – that is how a figure is posed.
- Right drag on a body part below a movable joint of a frozen figure turns that limb about the joint: the point you grabbed follows the mouse, hand and fingers turn with it.
- The mouse wheel twists the limb about its own axis meanwhile.
- The turn stays in the pose and is saved with poses and scenes; joint limits do not apply until the figure becomes active.

### Fingers and eyes
Frozen figures with Jodi's body:
- Up close (within about 1 m) small spheres appear on the finger joints and the lids.
- Right-drag a finger sphere to turn that joint, the mouse wheel twists it; left-drag curls the whole finger (pull the tip towards the knuckle).
- Left-drag a lid sphere to aim both eyes; the wheel opens and closes the lids meanwhile (with Shift when grabbing: only that lid).
- In an opened figure, "Left hand" and "Right hand" set ready-made hand poses (open, relaxed, fist, thumbs up, peace, point, hold, base pose).
- "Eyes: reset" opens the lids and looks straight ahead.
- Poses and scenes save fingers, lids and gaze.

### Quick menu
Without the panel, the quick menu activates or freezes figures:
- "Ragdoll: activate / freeze the one in view" takes the figure in the middle of the screen.
- "Ragdolls: active / frozen" switches all of them.

## Ragdolls mode {#ragmode}

Moves and poses the figures without the panel, with the camera free in the room.

### Start and end
- Start it with the third round button above + and − or from the quick menu.
- Esc or B ends the mode.

### Camera
- W A S D and Q E move the camera, Shift is faster; Shift + mouse wheel sets the speed.
- Drag on nothing to turn the camera.
- Hold the middle mouse button to turn the camera without the screen edges stopping it; the pointer comes back where it was.

### Figures
- The mouse pointer stays visible; on a figure everything works as beside the panel (see "Ragdolls").

## Enemies {#enemies}

Living, hostile zombies of every kind.

### Spawning
- A tile spawns its kind, the links below it its variants.
- They appear in the camera's direction at the distance you set, as many as "Count" says, spread around that point.

### Behaviour
- *Hunt* – they come for Jodi at once.
- *Lurk* – they wait until they see or hear someone (followers too).
- *Passive* – they stand still and nothing wakes them.
- A change applies to every enemy AltUI spawned.

### Removing
- *Remove all* / *Remove nearest* take them away (no loot, no EXP).
- *Kill all* lets them die as in the game – the bodies stay until *Remove all*.

### Spawn and Alive views
- Two views: "Spawn" (above) and "Alive (n)".
- "Alive: n" counts the living enemies AltUI spawned; the game's own zombies are never touched.
- "Alive (n)": one row per enemy – figures spawned from a look (with everything the Followers tab offers) and, below them, every zombie AltUI spawned with its kind, distance and behaviour.
- Links per zombie: hunt, lurk, passive, remove, kill.

### Good to know
- The game saves living enemies with the save game: after loading they are the game's zombies. Remove or kill them before saving.
- In a challenge, living enemies keep you from winning (the game counts every living zombie). Cut scenes remove them.
- Where there are no walkways (Jodi's office, Level 3, the shooting range) they only walk straight towards a target they can see.

### Quick menu
- "Spawn: <kind>" per kind and variant (with the current count, distance and behaviour).
- "Enemies: remove all / kill all / passive / active".
- Both in the Actions tab, also on own keys.

## Navigation {#navigation}

Flying, and the beds of the current level to teleport to.

### Fly / Land
- Fly: Jodi flies. Move as usual, Space rises, Ctrl sinks, Shift is three times as fast; the slider sets the speed. Walls stop her.
- Land lets her drop to the ground – a high fall hurts as in the game.
- Also in the quick menu, so it can have a key of its own (Actions › Own keys).

### Beds and teleport
- Lists the beds of the current level where Jodi can save, nearest first, with the room's name and the distance.
- Teleport puts Jodi next to that bed, facing it; save as usual by using the bed.
- Followers that follow her come along, waiting ones stay.
- A teleport skips everything on the way: story steps the game starts when Jodi walks through an area do not happen on the way, only when she walks into them later.
- Jodi's office, Level 3 and the shooting range have no such beds.

## Objects {#objects}

Put models from the game, weapons and models from mods (e.g. props from pose mods) into the world, move them and save them as a scene.

### Catalogue
- Left, CATALOGUE: All, ★ Favourites, the game's folders, "From level: …", Weapons and Mods (+ opens the single mods).
- On the right a search and the models as tiles, sorted by name; "Show more" loads further ones. Pictures only with "Load" ticked (off at first): then AltUI takes them itself and keeps them; unticked, no picture is loaded or taken.
- Clicking a tile puts the model on the floor in front of Jodi, fixed. Right click: favourite, "Spawn with physics".

### Mod models
- AltUI finds mod models by searching the mods once, folder by folder (the counter is shown at the top), and keeps the result; after that only new mods are searched.
- "Search mods again" starts over.
- Some mods put models in folders named unlike their pak; "Search all mod folders" finds those (the game pauses for about half a minute).

### Selected object
- At the bottom the "Selected" block: picture, name, fixed or with physics, deselect, physics on/off, to the floor, copy, remove.
- Fields for position, turn (yaw, pitch, roll) and size – Enter applies.
- The selected object has a yellow frame.

### In the world
- WORLD › In the world: a row per object with select (on the selected one: deselect), physics on/off, copy, remove.
- "Positions" opens a block: a name and "Save position" keep place, turn, size and physics.
- The position shows for every object of the same model in the same level – a click puts it there, right click: apply / delete.

### Scenes
- WORLD › Scenes: a name and "Save scene" keep every object of the level; the same name in the same level overwrites.
- Only the current level's scenes are shown. A click loads a scene and replaces the objects there; right click: load / delete.
- A missing model (mod not installed) is skipped and reported.
- Objects go with the level; a scene brings them back.

### Mouse on an object
Beside the panel and in the Ragdolls mode:
- Click selects it.
- Left drag slides a fixed object at its height; an object with physics is grabbed, letting go throws it.
- Right drag turns it about its vertical axis, Shift + right drag turns it freely. An object with physics keeps still meanwhile and falls again afterwards.
- The mouse wheel while dragging lifts or lowers it (also when held with physics); Ctrl + wheel changes its size.

## Followers {#followers}

Looks as people in the game: a follower walks with Jodi, fights and takes orders; an NPC stays where it is and defends itself.

### Spawning
- In the Looks tab, right click a look: "Spawn as follower", "Spawn as NPC" or "Spawn as enemy". The figure appears in front of Jodi wearing that look.
- Every figure wears the make-up of its look and has one of the game's NPC voices.
- A figure made with AltUI before 2.2.0 shows Jodi's make-up until "Change look…" gives it its own.

### Enemies from looks
- An enemy hunts Jodi with a pistol (infinite ammo) and hurts her. Your followers fight it.
- Its row is on the Enemies page under "Alive" with everything the Followers tab offers (only in its level) – delete it there, or make it a follower.

### Jason
- "+ Jason" (bottom right of the tab) adds Jason from the story as a follower, with his Glock. He takes orders, comes along and is saved.
- He fights only with his own Glock: a Glock you give him becomes his, other weapons he does not take.
- He has no look, clothes or make-up; when he is down he cannot be healed – "Revive" brings him back.

### The list
- The tab "Followers" lists every figure with its status (follows, waits, NPC, inactive, fallen) and chips.
- Followers are listed above NPCs, with a line between the two groups. The chips above the rows show all, only followers or only NPCs (kept after a restart).
- "..." folds the figure's tiles (clothes and backpack) away and back; it stays folded per figure, also after a restart.
- Click a row to select the figure.

### Chips
- "Follow me", "Wait here", "Bring here", → NPC / → Follower.
- "Active" off takes a figure out of the world, with everything it carries; on again, it comes back in front of Jodi.
- ∞ with a heart, "Invulnerable": the figure cannot die, its health fills up again after every hit. It still shows hit reactions and its clothes still take damage.
- ∞ with cartridges, "Infinite ammo": the figure keeps reloading its guns without needing ammo in its bag. Guns with a magazine leave its ammo untouched; the shotgun and the grenade launcher use up what it carries first.

### Gear menu
- The gear: attackable / unattackable, rename, change look, revive, remove.
- "Attackable": zombies only target attackable figures, whether invulnerable or not. After "Make unattackable" zombies and mercenaries do not pick the figure as a target; it still takes damage (unhurt is "Invulnerable"). The switch is saved; new figures are attackable.
- "Change look" switches to the Looks tab: click the look the figure should wear.
- A figure that is not invulnerable can fall. It stays in the list and "Revive" brings it back with what it carried. Figures never turn into zombies.
- "Remove" asks first; the figure's items and guns go into the storage box, its clothes into Jodi's backpack.

### Items
- The backpack (left) and the storage box (right) are at the top: a click gives one item to the selected figure, a gun with its paint and accessories.
- A click on one of the figure's own tiles gives it back into the backpack; right click: everything, or into the box.
- "..." above a list folds it.
- The context menu of a stack – Jodi's or the figure's – has the amount row as in the Inventory tab: "Give 5", "Take 5", into the box.

### Clothes
- Clothes are real pieces of the figure, as with the game's NPCs: they take damage, can tear off and show up in the game's own NPC inventory, where you can swap them too.
- Under a figure, its pieces are tiles (a badge marks damaged ones): a click takes one off into Jodi's backpack.
- Right click: repair with a sewing kit from Jodi's backpack, or repair all.
- In the backpack column, "Clothes" lists Jodi's pieces: a click gives one to the selected figure, which puts it on (her damage and colours go along).
- Gear menu "Restore outfit (no sewing kit)": the figure wears exactly its look's outfit again, every piece as new, free – lost pieces (torn off, taken away) come back, other pieces come off into its bag (followers, NPCs and enemies).
- "Restore all outfits" at the bottom right of the Followers tab does it for every figure of that tab.

### Saving and levels
- AltUI keeps the figures in a save of its own (AltUI_Followers.sav); the game's save never contains them.
- Following followers come along to every level and after loading.
- Waiting followers and NPCs stay in their level at their place.

### Quick menu
- "Follower: follow me / wait here" orders the follower in view, "All followers: follow / wait" all of them.
- "All followers: come to me" brings every active follower to the places in front of Jodi – also one waiting in another level.

### Figure in a pose
- The quick menu group "Figure: favourite poses" holds each of your favourite poses as "Figure: <pose>".
- The item puts the follower or NPC figure in view into that pose (not Jason).
- It then neither walks nor fights, holds the pose even after hits and does not turn away.
- If it is attackable, zombies attack it, and a figure that is not invulnerable can die – a way to set up scenes.
- "Figure: stop pose" makes it get up; it then follows or waits as before. A level change ends the pose.

## Codex {#kodex}

Three pages:

- Encyclopedia: the entries of the archive on Jodi's office computer, with picture and text. Only the ones the game has unlocked are shown – or all of them with the switch under Options › General.
- Passwords: the code locks of the current level, nearest first, with how far away they are and whether they are locked. Each code stays hidden until you click it.
- AltUI manual: this text.

## TV {#tv}

The TV of the current level, from the panel.

### When it shows
- Only shown when the current level has a TV (Jodi's office), or always with the switch under Options › General.
- With several TVs it controls the one nearest to Jodi.

### Playing
- Switch on / Switch off work like the E key on the TV.
- The TV reads its video list the first time it is switched on – until then the tab asks you to switch it on once.
- "Play" next to a video plays it; the one playing is highlighted.
- A video started earlier carries on where it was left, as on the TV itself.

### Own videos
- Put .mp4 files into the game folder TheKillingAntidote/Videos/TV/.
- They appear after the level is loaded again.

## Quick menu {#quick}

Hold 4 (another key under Actions) and a wheel opens around the mouse. Let go on an item to run it; let go in the middle to do nothing.

### Items
- Outfits, looks, faces, appearance presets, poses, tabs and settings of other mods.
- Actions: free camera, photo mode, ragdolls mode, a copy of Jodi as a ragdoll, switch every ragdoll between active and frozen, activate / freeze the one in view, remove all ragdolls, own speed on / off.
- "Slow motion on / off".
- "Stop time / go on": everything stands still; the panel and the cameras keep working, also the camera of the game's photo mode.
- "Hide / show Jodi" (with clothes, hair and weapon; she is back in the next level).
- "Hide / show the game's UI" switches the game's HUD off and on, as its photo mode does.
- "+1 Invisible Hand" puts one Invisible Hand into the backpack (see Inventory › All items).
- The orders for followers (see "Followers").

### Camera height
- "Camera height (wheel)": two arrows appear in the middle of the screen, and the mouse wheel now moves the camera up or down instead of closer or further away.
- A left click or Esc ends it. The height is kept.

### The Actions tab
- Add items under Actions, or with a right click on a tile, a tab or a mod's entry ("Add to quick menu").
- On the left: "In the wheel" (key, opacity, order with ↑ ↓ ✕), "Own keys", then "All" and every group that has items – outfits, looks, faces, presets, poses, tabs, mod entries – and one row per mod with actions.
- On the right: the items of that group with a check box (in the wheel or not) and a search above them. Each group keeps its scroll position.
- The order in the wheel is the order in the list under Actions › In the wheel.

### Own keys
- Under Actions, right click an item under "Available" and press a key – the item then runs on that key, with the panel closed, also in the free camera and in the game's photo mode.
- Click the key of a row for another one, ✕ removes it.
- The panel key, the quick menu key and a key already given are refused; a key the game uses itself triggers both.

## For mod authors {#modding}

How other mods work with AltUI.

### Clothes, body and weapon mods
- Clothes mods need nothing special: AltUI reads the game's tables and sorts every item by slot.
- Body and weapon replacer mods can be converted with bodypak.pyz and weaponpak.pyz so that several can be installed side by side.
- They can also be built for AltUI directly in the Unreal Editor.

### Idle mods
- A pak that replaces Jodi's idle animation can be converted with idlepak.pyz: python3 idlepak.pyz <mod>.pak.
- The new IdleAltUI_….pak goes into Mods/ and appears under Options › Movement › "Standing"; the game's own idle stays.
- AltUI must be installed: the converter builds the new pak partly from AltUI.pak and looks for it in the usual Steam folders. If it is somewhere else, give the path with --altui <path to AltUI.pak>.

### Walk and run mods
- A pak that replaces Jodi's walk or run animation can be converted with walkpak.pyz: python3 walkpak.pyz <mod>.pak.
- The new WalkAltUI_….pak goes into Mods/ and appears under Options › Movement › "Walk style" (and "Run style" if it brings a run); the game's own walk stays.
- walkpak refuses an animation without the game's movement curves (MoveData_Speed, Rotation Speed) and says which one is missing.
- Like idlepak it needs AltUI.pak (--altui <path> if it is not in the usual Steam folders).

### Settings in the Mods tab
- Mods can show their settings in the Mods tab through two data tables and an interface; MOD_UI.md in the source repository describes how.
