# Changelog

## 2.9.0 – 2026-10-29

* Photos: **free camera instead of "as seen"**. The lower half of a "+" tile (looks, faces, appearance presets, mod presets)
  and "Update (photo with free cam)" start the free camera with a frame of the photo's shape; fly it wherever you like and
  left-click to take the photo – exactly what you see, without the fill light. Esc takes the photo from the front instead;
  the settings are saved either way. The split "+" tiles of faces, appearance presets and mod presets say it short:
  "photo front" / "photo free".
* Mods tab: the value of a **number field** can be typed in. Click it, type, Enter or a click elsewhere applies it; a
  comma counts as the decimal point, the value is kept within the field's range, and anything that is no number brings
  the old value back. − and + work as before.
* Mods tab: **presets** for every page. "+" saves the page's settings with a photo (from the front / free camera), a click
  applies them, the right-click menu renames, updates, moves, deletes and puts them into the quick menu or onto an own
  key. Mods need no change for this; a mod can ship ready-made presets in an optional `AltUI_Presets` table
  (`S_AltUIModPreset`, see MOD_UI.md). One file per mod: `Saved/SaveGames/AltUI_ModPresets_<mod>.sav`.
  "View content" lists a preset's values with a check box each: unticked ones stay stored but are not applied. Shipped
  presets can get a photo of their own ("New photo"). Colour and text fields are applied before the choices, so a
  choice that a colour field switches to "Custom" comes back as saved.
* Walk / run mods: `walkpak.pyz` turns a pak that replaces Jodi's walk or run animation into a `WalkAltUI_<Name>.pak`
  that replaces nothing. It shows up as a chip under Options › Movement › Walk style / Run style, next to the built-in
  styles, and combines with them and the standing idles. A walk mod chosen together with an idle mod wins; Options says so.
* Navigation: **Fly / Land**. Jodi flies with Space / Ctrl for up / down, Shift x3 and a speed slider; also in the quick menu.
* New tab **Navigation**: the beds of the level where Jodi can save, nearest first, with name and distance. *Teleport* puts
  Jodi next to the bed, facing it; followers that follow her come along. The place next to the bed must be in sight of it (Level 1, A2 Lounge
  sent her into a closed shaft behind the wall); a bed in a room without navmesh gets free floor next to it.
* Ragdolls mode: holding the middle mouse button turns the camera without the screen edges stopping it; the pointer comes
  back where it was. Left / right and the wheel work as before.
* New tab **Actions**: the quick menu's settings left Options. On the left: In the wheel, Own keys, All, each group with
  items and one row per mod; on the right the items of that group with a search. Each group keeps its scroll position;
  ticking an item no longer moves the list.
* Ragdolls: fingers and eyes. On frozen figures with Jodi's body small spheres appear on the finger joints and the lids when
  the camera is close. Right-drag turns a finger joint, left-drag curls the whole finger; left-drag on a lid aims both eyes and
  the mouse wheel opens / closes the lids (Shift: one lid, to wink). The opened figure has hand poses per hand (open,
  relaxed, fist, thumbs up, peace, point, hold, base pose) and "Eyes: reset". Poses and scenes keep fingers, lids and gaze.
* Options › Invisible hand: with "Own settings" on, the invisible hand picks up items in a larger area (range 1x to 10x,
  the height grows at most to 2x) and more than one item per round (up to 20). The pace stays the game's, faster with more
  hands in the backpack. "Also without a hand in the backpack" makes it work without the item (off by default). It only
  takes what the game's hand takes, and items still fly to you the game's way. Switched off, the game's hand works as
  before. Quick menu: "Invisible hand: own settings on / off".
* Figures in a pose: the quick menu group "Figure: favourite poses" puts the follower or NPC you look at into one of your
  favourite poses (Jason excepted). It neither walks nor fights, holds the pose through hits and does not turn on the
  spot; seated poses keep sitting. "Figure: stop pose" makes it get up and follow or wait as before. The pose ends with
  a level change.
* Followers and NPCs: new switch "Attackable" in the gear menu (saved, on for new figures). Zombies only target
  attackable figures; an unattackable one is left alone and takes no damage.
* Followers and NPCs: "Invulnerable" no longer keeps zombies away – that is the "Attackable" switch now. An invulnerable
  figure cannot die and its health fills up again after every hit; it still reacts to hits and its clothes take damage.
* Ragdolls: "Make attackable" lets zombies attack a human ragdoll (copy of Jodi, NPC or mercenary). Hits push the body
  part nearest to the zombie; a frozen ragdoll springs back into its pose. Ragdolls do not die. Saved with the scene.
* Clothes: right click › "Keep on" marks a piece. When you put it on yourself it stays on through looks and outfits;
  pieces of the look that would take its slot are left out and named. A piece a look or outfit put on does not stay,
  so trying outfits never piles pieces up. Undo restores exactly.
* Camera zoom while playing: with the panel closed, the mouse wheel moves the camera closer to Jodi or further away
  (from about a third to four times the game's distance). Aiming keeps the game's view, the panel's Jodi view is
  unchanged, and the distance is kept.
* Camera height while playing: the quick menu entry "Camera height (wheel)" shows two arrows in the middle of the
  screen; the mouse wheel then moves the camera up or down instead of closer or further away. A left click or Esc ends
  it. The height is kept.
* Objects: a selected object can be deselected again – "Deselect" in the Selected block, and in WORLD › In the world
  the selected row's "Select" link turns into "Deselect".

## 2.8.0 – 2026-10-24

Replace `AltUI.pak`. `weaponpak.pyz`, `bodypak.pyz` and `idlepak.pyz` are new too. When weaponpak reads the game's own pak
(for a sound behind one of the game's sound cues), `--game` now has to point into the installed game folder, not to a copy
of the pak. Paks converted with older versions keep working. `AltUI_Hook_P.pak` and `altui_names.pyz` are the same as in
2.7.0.

* **New Objects tab.** Put models from the game, weapons and models from mods (for example props from pose mods) into
  the world. On the left the catalogue (all, favourites, the game's folders, levels, weapons, every mod) with a search and
  pictures AltUI takes itself; a click puts the model in front of Jodi, right click spawns it with physics. Objects move
  like the ragdolls: left drag slides them (with physics: grab and throw), right drag turns them (Shift: freely), the
  wheel lifts them, Ctrl + wheel scales them. The selected one has a frame; the "Selected" block below shows it with
  fields for position, turn and size and links for physics, to the floor, copy and remove. WORLD › In the world (at the top of
  the left column) lists the objects and keeps positions per model, WORLD › Scenes saves all objects of a level and
  loads them back (replacing); the search box filters these lists too.
  Mod models are found by searching the mods once in the background; the result is kept, so later starts only search new
  mods.
* **Oiled skin.** Appearance › Skin has a row "Oiled skin" above the skins: it makes Jodi's skin glossy through the game's
  own wet-skin effect (the game's wet skin is 50 %). Ticked, the value holds, also against the story; unticked, the game
  decides again. Only on Jodi. Looks and appearance presets keep it; looks and presets saved before bring "the game
  decides".
* **Close one eye.** Face › Gaze has "Left eye closed" and "Right eye closed" next to "Eyes closed", e.g. for a wink in a
  pose. Like "Eyes closed", only on converted bodies.
* **Ragdolls: the wheel lifts a held part.** Holding a part of an active figure, the mouse wheel now lifts or lowers the
  held point (as with objects); before, the camera zoomed.
* **Fix: the game froze after many quick pose changes.** Every click on a pose rebuilt the whole poses list (twice),
  and with many pose mods the game's memory grew with every click until it froze. A click now only moves the marking.
* **Fix: a second click on the running pose ends it.** It started the pose again instead.
* **Fix: loading a story save with "Several pieces in one slot".** Jodi wore the save's outfit plus pieces of the one worn
  before. On load, AltUI now puts the extra pieces of a multi-piece slot on from the list of the loaded save (before: from the
  last clothes the game had stored outside the saves). "Underwear may be taken off" checks against the same list.
* **Fix: Manage › Usage counts the clothes drawers.** A mod whose pieces were only in a drawer was listed as unused;
  drawers now count like favourites, shown as "Drawer “name”".

## 2.7.2 – 2026-10-22

Replace `AltUI.pak` – nothing else. `AltUI_Hook_P.pak`, `weaponpak.pyz`, `bodypak.pyz`, `idlepak.pyz` and `altui_names.pyz`
are the same as in 2.7.0. 2.7.1 came out on GitHub only, so on Steam and Nexus this version also brings its two fixes:
magnifying scopes no longer show a black ring after AltUI was open, and opening AltUI while aiming ends the aim.

* **New TV tab.** In Jodi's office the TV's videos are listed in AltUI: click one to play it, switch the TV on or off from
  there. The tab only appears in a level with a TV (with several, the one nearest to Jodi); Options › General can show it
  always. Your own videos: put .mp4 files into `TheKillingAntidote/Videos/TV/` – they appear after the level is loaded
  again. The TV reads its list the first time it is switched on, so until then the tab asks to switch it on once.
* **A chosen game paint stays on new weapons.** A paint picked in the Weapons tab (for example `GunPaint_Pink`) was
  removed again when Jodi picked up a new, unpainted copy of that weapon – in the shooting range after every restart – and
  the tab showed Original. Picking up a weapon now keeps the choice; only a paint put on in the game (spray can) on the
  weapon Jodi carries replaces it.
* **A spray paint survives the storage box.** A weapon painted with a spray can and put into the box before AltUI was
  opened came back out with AltUI's earlier choice. The spray paint is now taken over the moment it is put on.

## 2.7.1 – 2026-10-21

Replace `AltUI.pak` – nothing else. `AltUI_Hook_P.pak`, `weaponpak.pyz`, `bodypak.pyz`, `idlepak.pyz` and `altui_names.pyz`
are the same as in 2.7.0.

* **Scopes stay clear after AltUI.** A magnifying scope (4x, 8x …) aimed after AltUI had been open showed its lens behind a
  black ring, until the scope was taken off and put on again. Opening AltUI no longer touches what the scope shows while aiming.
* **Opening AltUI while aiming ends the aim**, the way the game's own menus do. Before, Jodi went on looking through the
  sight after the panel closed, without the aim button held and without the zoom, until the button was pressed again.

## 2.7.0 – 2026-10-21

Replace `AltUI.pak`; `weaponpak.pyz`, `bodypak.pyz` and `idlepak.pyz` are new. `AltUI_Hook_P.pak` and `altui_names.pyz`
are the same as in 2.6.0. A body converted with `bodypak.pyz` on Windows that lacked bones (the left hand off the gun)
should be converted again; weapon sound mods for the HK416 and the SA58 too, and model mods that bring their own Camo / Pink (`--force`).

* **Clothes: drawers.** Your own collections of clothes – a bar above the list holds "Default" (everything), your drawers
  and "+" (a new one, "Drawer 1", "Drawer 2" …); it wraps into more rows when it is full. A drawer shows the same page –
  slots, chips, search, filters, favourites – with only its pieces, and the slots count only those. Right click on a piece ›
  "Drawer ›" opens the drawers next to the menu: a tick shows where the piece is, a click puts it in or takes it out, "+ New
  drawer" makes one with the piece in it; inside a drawer the menu also has "Remove from this drawer". A piece can be in any
  number of drawers. Right click on a drawer: rename, move left / right, delete (asks first; the pieces stay). Drawers are
  kept in `AltUI_Drawers.sav`, for every save game; the shown drawer stays after a restart.
* **Ragdolls: turn a limb.** Right drag on a body part below a movable (green) joint of a frozen figure turns that limb
  about the joint – the grabbed point follows the mouse, hand and fingers turn with it; the mouse wheel twists it about its
  own axis meanwhile. Right drag anywhere else still turns the whole figure. The turn stays in the pose, so poses and
  scenes keep it; joint limits apply again once the figure is active.
* **Weapons: a model's own gun paints.** Some model mods also replace the game's Camo and Pink paints with versions made
  for their model (Samurai Edge for the Glock). `weaponpak.pyz` now keeps them: they appear as extra skins next to the
  game's paints while that model is chosen, and go on the weapon the way the game puts its paints on. Convert such mods
  again (`--force`) to get them.
* **Weapons tab: the tile pictures.** They are lit more evenly and with less gloss, so the colours of grips and paints
  come through and the corners no longer fall off into the dark. "Take pictures again" now takes the "Original" tiles
  anew as well (skin and model); before, those were only taken when clicked. While a model's own paint is chosen, the
  tiles of the other models show them without it – the way they look in the hand. A model whose mesh carries a long part
  of its own, such as the beam of a laser pistol, is framed to the weapon; its tile showed a dot before. Press "Take
  pictures again" once per weapon to get the new pictures.
* **Weapons tab: dimmed skin tiles.** For a weapon Jodi had not held yet, the skin mod tiles were dimmed – or not –
  according to whichever weapon had been put on last. Whether a skin does something now belongs to the weapon and its
  model, and a tile is only dimmed once that is known.
* **Converters on Windows:** `weaponpak.pyz` stopped with "No module named 'cryptography'" when it had to read the
  game's sound cue (for example a sound mod for the HK416); it now decrypts the game's pak on its own. `bodypak.pyz`
  could not add missing bones on Windows ("missing bones not checked", the left hand did not reach the gun) because the
  pak it was replacing was still open; it now closes it first. A converter error on a pak is now shown as it is instead
  of a misleading "struct.error".
* **Weapon sounds: the mod's shot instead of the game's.** Sound mods converted for the HK416 and the SA58 played the
  game's own shot (both chips sounded like "Original"): the copied sound cue still named the game's recording a second
  time, and the game loaded that one. Convert such mods again with the new `weaponpak.pyz` (`--force`).
* **`weaponpak.pyz` converts more sound mods:** mods that replace only the recordings behind the game's sound cue – the
  Glock, revolver, shotgun, UMP45 and grenade launcher pick from several – and mods that bring a cue of their own
  together with its recordings. A sound in its own pak next to the model becomes a sound mod of its own. Suppressor
  sounds are not converted (they belong to the part, not to a weapon); the converter says so.
* **`weaponpak.pyz`: names with spaces, hyphens or dots** (from the file name or `--name`) are turned into a valid name
  instead of stopping with "invalid name"; the converter prints the name it used, and a `--name` typed with spaces
  becomes the chip's title.
* **Coiffure tab: search.** A search box above the hairstyles (it stays in place while the tiles scroll) finds them by
  shown name, identifier, mod name and pak file, in the favourites block and in the full list; × clears it. "Show in
  tab" clears it before jumping to a hairstyle.
* **Manage › Usage** (new category): which mods are in use right now. Each mod in use lists its pieces and where they
  are used – Jodi now, outfits, looks, presets, favourites (clothes, hairstyles, appearance, poses, weapons), followers
  (worn and backpack), ragdoll scenes, the standing idle and the active weapon skins, models and sounds. Unused mods follow
  in grey, then the mods whose use AltUI cannot detect (maps, script mods). Every mod has "View content". The search
  finds mods by name and by the names of their pieces. Pieces only kept in the wardrobe do not count. Each mod is a tile
  with its shown name and its pak file, its pieces in a table (piece, kind, places), the places summed up per kind
  ("Outfits 4–6, 8 · Follower “Lea”"); long names wrap inside their column. The list is collected only when Usage is
  open, so the other Manage pages cost nothing extra; the number on the left is the one from the last time.
* **Followers tab:** each figure's row has a "…" chip that folds its tiles (clothes and backpack) away and back; it stays
  folded per figure, also after a restart. The row's menu chip now shows a gear.
* **Followers tab: symbols instead of long captions.** "Invulnerable" is now ∞ with a heart, "Infinite ammo" ∞ with
  cartridges (their names as tooltips), so a figure's chips fit one line in the half view.
* **Followers tab:** followers are listed above NPCs, with a line between the two groups. Chips above the rows show all,
  only followers or only NPCs (kept after a restart).
* **Appearance > Mutation:** no search row above the switches (there are no tiles to search).
* **Camera light** (new round button beside the panel, at the top): lights up what the camera sees – beside the panel, in
  the free camera and in photo mode. A click opens a small menu: on / off, the light's colour (palette) and a brightness
  slider. The light only brightens: no shine spots on skin or floor, no visible beam in fog. It is off while you play and
  comes back as you left it when the panel opens again.
* **Options › Theme: every surface follows the theme.** Text fields (Manage › display names, the rename fields of
  tiles, Mods tab, amount and hex fields), check boxes, scroll bars, the light areas of Inventory and Followers, the
  striped rows (slot conflicts, quick menu, Kodex locks), the buttons of the Mods tab, the warning window, the weight bar
  and a few labels kept fixed colours until now. Four new colours: **Text fields**, **Areas / stripes**, **Warnings**,
  **Scroll bars**. Saved themes and settings from before keep working; the new colours start at their defaults there.

## 2.6.0 – 2026-10-18

Replace `AltUI.pak`. `AltUI_Hook_P.pak`, `bodypak.pyz`, `weaponpak.pyz`, `idlepak.pyz` and `altui_names.pyz` are the
same as in 2.5.0; converted bodies do not need to be converted again.

* **Appearance › Mutation** (new entry under "Skin"): Jodi's mutated look from the story, in parts – skin colour and glow as
  sliders, veins and eyes as switches. Make-up stays visible on the discoloured skin, and your own iris colour tints the
  mutated eye. "Story look" sets the cutscene's look in full (the story's own skin material, every row
  on) – without make-up and scars. It is part of a look, so followers and ragdolls made from a look carry it too.
* **Followers: "Infinite ammo"** (chip in a figure's row): the figure keeps reloading its guns without needing ammo in
  its bag. Guns with a magazine leave the ammo it carries untouched; the shotgun and the grenade launcher use up what it
  carries first.
* **Followers: "+ Jason"** (bottom right of the tab) adds Jason from the story as a follower, with his Glock: orders, "come to
  me", active, invulnerable, NPC mode, bag, saving and level changes work as for every figure. He fights only with his own
  Glock: a Glock given to him becomes his, other weapons he refuses. He has no look, clothes or make-up, and cannot be
  healed when down ("Revive" brings him back). His death does not end the game.
* **Inventory › All items:** the game's Invisible Hand is in "Collectibles". While it is in the backpack it brings items
  near Jodi to her, one after another – faster with more hands (one every 2.5 s, from six on every 0.1 s). It now also
  works right after loading a save, and stops when the last hand leaves the backpack.
* **Inventory:** backpack and box show "Collectibles" too – the invisible hands, decor, crystals – so you can see how many
  hands Jodi carries.
* **Quick menu: "+1 Invisible Hand"** puts one hand into the backpack.
* **Fix:** closing the panel after a challenge was won or lost (or the story ended) took the mouse away from the game's
  Congratulations / results screens, and Esc did not work there either – the game had to be closed. The mouse now stays.

## 2.5.0 – 2026-10-18

Replace `AltUI.pak`. `AltUI_Hook_P.pak`, `bodypak.pyz`, `weaponpak.pyz`, `idlepak.pyz` and `altui_names.pyz` are the
same as in 2.4.0; converted bodies do not need to be converted again.

Several pieces in one slot, and ragdolls you can pin in the air.

* **Several pieces in one slot** (Options › Slot conflicts): a chip per slot. A slot switched on keeps what is worn
  there when another piece of it is put on – for example knee socks over tights. Works for Jodi, looks and followers, and
  survives saving and loading. The mirror wardrobe and its outfits still keep one piece per slot.
* **Body Shape:** "Reset shape" is in the status bar, bottom right (where the other pages keep their actions), instead of
  a link below the sliders.
* **Ragdolls › joints ›:** every joint has a second switch, movable / fixed, for posing a frozen figure (before it could only
  be set with Shift + right click on the figure).
* **Ragdolls: pin parts in the air** (like the physics gun in Garry's Mod): while you drag a part of an active figure,
  a right click pins it where it is, turn included, and the rest of the figure hangs on it. Grab it again and it is free;
  "release all" in the figure's row frees every pin. Pins rest while the figure is frozen (and move with it), and scenes
  keep them.
* **Ragdolls: joint spheres** show where a figure can be grabbed: grey, red = locked, green = movable, blue = pinned.
  Spheres behind the body shimmer pale through it, and a click on a sphere grabs exactly that joint – also one behind
  the body. They show on the Ragdolls tab and in the Ragdolls mode, never in the photo mode; "Joint spheres: on/off" in
  the status bar turns them off for good.
* **Ragdolls:** "Remove all" moved to the status bar, bottom right.
* **Ragdolls › poses** also keep which joints are locked or movable (poses saved before keep the joints as they are).

Fixes:

* **Ragdolls:** a figure held with the mouse is let go when the panel closes (B) or the Ragdolls mode ends (Esc). Before,
  the grabbed body part stayed hanging in the air until the next grab, and then the figure dropped.
* **Stop time** also stops the hair and cloth of ragdoll figures (before, their hair kept moving).

## 2.4.0 – 2026-10-17

Replace `AltUI.pak`. `AltUI_Hook_P.pak`, `bodypak.pyz`, `weaponpak.pyz`, `idlepak.pyz` and `altui_names.pyz` are the
same as in 2.3.0; converted bodies do not need to be converted again.

Outfits that keep their colours, previews of the theme pictures, and lists that stay where you left them.

* **Options › Theme: "Show previews"** (off by default): the picture chips of the background and button picture show
  the picture itself instead of its name – with the hue, sepia and invert of their row, the name in the tooltip. Your
  own pictures get a small preview of their own the first time, kept in `Images/Thumbs`; after that the page loads only
  those. A picture replaced under the same name gets its new preview when it is chosen (or the game starts with it).
  Right click on the preview of one of your own pictures: **Redo preview** draws it anew from the file.
* **Own pictures** may also end in `.jpeg` (before: only `.png` and `.jpg` were found).
* **Lists keep their place:** pages no longer jump to the top when they are rebuilt – choosing a button picture,
  clicking a pose or an outfit, a pose ending on its own. Coming back to a page finds it where you left it; another
  options category starts at the top.

Fixes:

* **Outfits keep AltUI's colours.** An outfit saved in AltUI could come back with one colour on everything or none at
  all – with many pieces or long piece names (mods) its colours all ended up on one shared entry. And outfits with the
  same pieces shared their colours and name: saving the same pieces again changed or wiped the colours of the first.
  Every outfit now keeps its own colours and name, also when moved or deleted. Outfits saved before are taken over as
  they were shown; one whose colours were already lost has to be saved once more. Outfits saved at the game's mirror
  still keep only the game's one colour per piece.
* **NPCs stay NPCs:** the game's untargeted "Follow me" (and "Attack") reached AltUI's NPCs too, so they followed Jodi.
  They now stay at their place; followers still follow.
* **Body Shape:** with many body mods the body chips no longer push the sliders off the page – they scroll in an area as
  tall as the group chips (Options › Groups › "Group chip area: max. height").
* **Ragdolls:** the colour variants under a figure no longer run past the tile – they break into a second line
  (Squirter: blue, red, yellow; longer names in other languages).

## 2.3.0 – 2026-10-16

Replace `AltUI.pak`. `AltUI_Hook_P.pak`, `bodypak.pyz`, `weaponpak.pyz`, `idlepak.pyz` and `altui_names.pyz` are the
same as in 2.2.0; converted bodies do not need to be converted again.

Pictures for the panel and its buttons, themes that keep them, all followers at once, a clean copy of a look, a free
camera without limits, and a switch for the notices.

* **Options › Theme** – formerly *Options › Colours* – in sections: colours, background picture, button picture,
  themes. "Reset colours" moved to the status bar, bottom right.
  * **Background picture:** a picture behind the panel – fill, fit, stretch or tile, aligned left / centre / right and
    top / middle / bottom, with hue, sepia and invert. The background colour lies over it: "Background opacity" sets
    the colour, the new "Pattern opacity" the picture.
  * **Button picture:** a picture on the tiles, slot tabs and tabs (not on chips and round buttons), with rounded
    corners, its own hue, sepia and invert, at the tile opacity.
  * AltUI brings its own pictures, among them off-white card stocks (bone, eggshell, laid paper, pale cloud, embossed
    linen). Your own go into `Saved/SaveGames/AltUI/Images` as `Background_1.png` … `Background_30.png` and
    `Button_1.png` … `Button_30.png` (or `.jpg`); the hint on the page shows the full folder.
  * Saved colour schemes are now **themes**: a theme saved from now on keeps the pictures and their settings too;
    schemes saved before still change only the colours.
* **Quick menu: "All followers: come to me".** Every active follower comes to the places in front of Jodi, side by side
  in rows of five – also one left waiting in another level. A waiting follower waits at its new place.
* **Looks: "Clean copy (without missing parts)"** in a look's context menu, shown when the look holds pieces of a mod
  that is no longer installed, or eye / make-up rows no table has any more. It makes a new look right after the original,
  without those entries and with the same picture; the original stays as it is. Saving a look again keeps such entries,
  as it always did – removing them is up to you.
* **Free camera without collision and at any distance** – two new checkboxes under *Options › Camera*: fly through walls
  and Jodi, and as far away from her as you like. Both also apply to the Ragdolls mode.
* **No notices** – a checkbox under *Options › General*: none of the notices at the bottom any more, neither AltUI's nor
  the game's own.
* **Repeat poses** – *Repeat poses: on / off* in the Poses tab's status bar: a pose that ends by itself starts again,
  until Jodi moves, the use key or "Stop pose" ends it, or another pose is chosen. Many pose mods repeat their poses
  anyway; this is for the ones that play once or stop after a while.
* **Poses › Measure all** shows the name of the pose being measured next to the progress.
* **Options › Tabs › Tab rows: "try to fit in one row".** The captions get smaller first, then shorter ("…"), so the tab
  bar fits on one row where it can; with every tab shown on a narrow panel it still wraps. The default wraps as before.
* **Ragdolls: the Mercenary** as a new kind of figure, with his rifle in his hands.

Fixes:

* **Running with a gun no longer stutters.** Since 1.9.0 AltUI's walk and run speed changed the order in which the game
  moves Jodi and updates the camera, also with "Own walk / run speed" off; the order could change from frame to frame,
  which made Jodi stutter on screen, most visibly when running with a pistol.
* **Followers and ragdolls made from a look get its hairstyle**, also when Jodi was not wearing the look before: the copy
  waited only until her clothes were on, not until the whole look was (the hairstyle comes last). A follower now takes
  the look's own hairstyle even when that one is locked for Jodi.

## 2.2.0 – 2026-10-16

Replace `AltUI.pak`. `AltUI_Hook_P.pak`, `bodypak.pyz`, `weaponpak.pyz`, `idlepak.pyz` and `altui_names.pyz` are the
same as in 2.1.0; converted bodies do not need to be converted again.

Keys of your own for anything in the quick menu, closed eyes, favourite hairstyles, and followers with their own make-up
and voice.

* **Own keys.** *Options › Quick menu* has a new block **Own keys**: right click any item under "Available" and press a
  key – slow motion, stop time, free camera, photo mode, a look, a pose, a tab, anything the quick menu offers, as many
  as you like. Click the key of a row to give it another one, ✕ removes it. The keys work with the panel closed, also in
  the free camera and in the game's photo mode. The panel key, the quick menu key and a key another item already has are
  refused. AltUI cannot keep a key from the game: a key the game uses itself triggers both.
* **Hide / show the game's UI.** A new quick menu item that switches the game's HUD off and on, as the photo mode does –
  on a key of its own also inside AltUI's free camera.
* **Eyes closed.** The Face tab has a new slider "Eyes closed" under *Gaze*: from open to fully closed. The game's own
  blinking goes on as before. It works on converted bodies, like the body sliders – not on the standard body without a
  body mod.
* **Favourite hairstyles.** Right click a hairstyle: "Add to favourites". Favourites show at the top of the Coiffure
  tab, above all others.

Fixes:

* **Followers and NPCs wear the make-up of their look.** They showed whatever make-up Jodi wore at the moment – the
  game keeps all make-up in one shared texture. Each figure now draws its own, AltUI's make-up colours included. A
  figure made with an earlier version keeps showing Jodi's make-up until "Change look…" gives it its own.
* **Ragdoll copies of Jodi keep the make-up they were made with** instead of changing along with Jodi.
* **Followers and NPCs have a voice.** They were silent – no pain, no calls. Each figure now gets one of the game's NPC
  voices and keeps it.
* **Stop time in the game's photo mode.** With time stopped by AltUI the photo mode's camera could not move. It now
  moves while Jodi and the world stand still, whether time was stopped before or during the photo mode.
* **A context menu closes when another tile is clicked.** It stayed open until a click on an empty spot.

## 2.1.0 – 2026-10-15

Replace `AltUI.pak`. New: `idlepak.pyz`, a converter for idle mods. `AltUI_Hook_P.pak`, `bodypak.pyz`,
`weaponpak.pyz` and `altui_names.pyz` are the same as in 2.0.0.

Idle animations to choose, a chosen amount when moving items, and the body shape survives cutscenes.

* **Idle animations.** *Options › Movement* has a new row **Standing**: besides the game's usual idle, Jodi can stand
  with one of six other animations of the game – looking around, checking nails, checking leg, careful, injured,
  posing.
  * **Idle mods** appear in the same row. `idlepak.pyz` turns a mod that replaces Jodi's idle into an `IdleAltUI_…`
    pak: it no longer replaces anything, the game's idle stays, and the mod becomes one more choice:
    `python3 idlepak.pyz <mod>.pak [--name Name] [--title "Shown name"]`. AltUI must be installed: the converter
    builds the new pak partly from `AltUI.pak` and looks for it in the usual Steam folders; if it is somewhere else,
    give the path with `--altui <path to AltUI.pak>`. Put the new pak into `Mods/` like `AltUI.pak`.
  * **A pose as idle.** Right click a pose tile: "Use as idle". The pose starts after 1.5 s of standing still and ends
    when Jodi walks, draws a weapon or crouches; "No longer as idle" switches it off. The row *Standing* shows it as
    "Pose: <name>".
* **A chosen amount.** The context menu of a stack has a row with a slider and a number field, and one entry per target
  with that number: into the box, take, into the backpack (Inventory tab, also in the "All items" catalogue, there in
  pieces), give and take back (Followers tab). Enter in the field runs the first entry. Guns and single items have no
  such row.
* **A warning before very many objects on the ground.** "Discard all" puts one object on the ground per pack of an item.
  From 100 objects on a window asks first: cancel, destroy instead (nothing falls), or drop anyway – that many objects
  with physics at once can crash the game.

Fixes:

* **Cutscenes no longer reset the body shape.** After a cutscene (and after the shower) Jodi had the body's default
  shape again, without AltUI's slider values; AltUI now puts them back as soon as the game rebuilds the body's animation.
* **Jodi can be turned while the colour palette is open.** Dragging beside the palette turned the camera instead.
* **Esc with the colour palette open** closes only the palette; it opened the game's pause menu behind it before.

## 2.0.0 – 2026-10-13

Replace `AltUI.pak`, `bodypak.pyz` and `weaponpak.pyz`. `AltUI_Hook_P.pak` and `altui_names.pyz` are the same as in
1.8.0.

Followers and NPCs made from looks, an Inventory tab with the Hyper Storage Box, weapon accessories, body physics,
clothing colours per save game and a check for unknown game versions.

* **Followers and NPCs.** Right click a look in the Looks tab: "Spawn as follower" or "Spawn as NPC". The figure appears
  in front of Jodi wearing that look, its body sliders and the weapon looks chosen in AltUI included. A follower walks
  with Jodi, fights and takes orders; an NPC stays where it is and defends itself.
  * A new tab **Followers** lists every figure with its status (follows, waits, NPC, inactive, fallen) and chips:
    Follow me, Wait here, Bring here (also from another level), → NPC / → Follower, Active, Invulnerable, and "..." for
    rename, change look, revive and remove.
  * Jodi's backpack and the storage box are at the top of the tab: a click gives one item or gun to the selected figure,
    a click on one of its tiles takes it back.
  * **Clothes are real pieces of the figure**, as with the game's own NPCs: they take damage, can tear off and show up in
    the game's NPC inventory, where they can be swapped too. Under a figure its pieces are tiles: take one off into
    Jodi's backpack, give her one, repair with a sewing kit. Damage, colours and AltUI's slot colours go along.
  * A figure that is not invulnerable can fall; "Revive" brings it back with what it carried. Figures never turn into
    zombies. "Remove" asks first; items and guns go into the storage box, clothes into Jodi's backpack.
  * The figures are kept in `AltUI_Followers.sav`, never in the game's save: a save loaded without AltUI simply has
    none of them. Following figures come along to every level; waiting ones and NPCs stay where they are.
  * Quick menu: "Follower: follow me / wait here" for the follower in view, "All followers: follow / wait".
* **Inventory tab.** Jodi's items and the **Hyper Storage Box** one under the other, with the game's groups as chips, the
  weight with a bar (and how far she is overloaded), and its own tile size under *Options › Tiles*.
  * A click puts one item into the box or takes one out; right click: half or all, use, inspect, discard, quick slot 1
    or 2, unload ammo, accessories.
  * Everything goes through the game's own functions, so the game's rules stay: Jodi may be overloaded and the game
    deals with it. On maps where the game never saves the backpack (the shooting range, for example) the tab says so.
  * Each list can be folded ("...") or given the full height (↑↓).
  * **"All items" catalogue** – off by default (*Options › General*): every item of the game as a third list,
    into the backpack or the box, one or five at a time.
  * **Auto-equip weapons** (*Options › General*, on by default): a gun taken from the box or the catalogue goes into
    Jodi's hand as the game does it; off, she keeps what she holds.
* **Weapons: accessories.** A new section *Weapon accessories* in the Weapons tab: one row per slot the weapon takes
  (sights, barrel, grip, magazine). Parts come from the backpack or the storage box; mounting and taking off work as in
  the game, and the weapon keeps the model, skin and sound chosen in AltUI. "Accessories…" in the inventory menu of a
  gun jumps there.
* **Body physics.** Body Shape has new rows for breast and glutes & hips: **jiggle** (adjusts the game's physics, works on
  every body; 0 % = animation only), **angle** and **hip width** (converted bodies), and **nipples** (only while the
  chest is uncovered).
* **Clothing colours per save game.** The slot colours set in AltUI now belong to the save game, like the game's own
  colours: each save keeps its own, and a save that has none of AltUI's shows the game's colours. The colours from
  before go into the first save loaded with 2.0.0.
* **Clothes: damage slider.** The context menu of a piece (Clothes and Backpack tabs) has a *Damage* slider from 0 to
  100 %: live on a worn piece, kept for later on any other. Worn pieces without damage textures show none.
* **Colour palette: hex code.** Under the game's colour palette a field shows the colour as `#RRGGBB` and takes a typed
  code. "Remember" keeps a colour inside AltUI and "Use" puts it on another piece.
* **Main menu scenes.** The panel key (B) in the main menu opens a small menu: the three menu scenes and the loading
  scene, the next camera, and hiding the game's menu and texts (Esc brings them back).
* **Slow motion, stop time, hide Jodi.** New quick menu entries: "Slow motion on / off", "Stop time / go on" and
  "Hide / show Jodi". *Options › Movement* has a switch for slow motion and its speed.
* **Check for unknown game versions.** When the game has changed – an update, or a mod that replaces the game's tables
  – AltUI shows a warning before it touches anything: go on anyway (remembered for this game version) or leave AltUI off
  for now.
* Smaller additions:
  * The search finds a mod by its pak name, in every tab.
  * Weapons: "Show item pictures" puts the item's or mod's own picture on every tile instead of the rendered one.
  * Weapon mods are listed under *Manage › Mods*, and "View content" shows their models, skins and sounds. Skin, model
    and sound tiles and hairstyles from mods have "Rename mod…"; the tooltip of a weapon tile names its mod.
  * Pose tiles with a sound show a speaker in the corner.
  * Body Shape: all rows share one label column, and "Reset shape" is a link below the sliders.
  * *Options › Controls*: how far the mouse wheel lifts a ragdoll per notch.

Fixes:

* **Changing the body with a gun in hand** no longer spoils how Jodi holds it; before, her left hand came off the gun
  and stayed off.
* **Converted bodies hold guns with both hands.** `bodypak.pyz` adds the bones (`Cam`, `Prop_R2`) that bodies built
  against an older skeleton lack; without them the left hand stayed off the gun. Convert such bodies again.
* **`bodypak.pyz` and `weaponpak.pyz` convert mods cooked with Unreal's version stamp** (4.27), which they refused
  before. A body that brings its own skeleton or physics asset keeps the game's, so the game's animations run on it.
* **A colour set in the game's mirror wins** over AltUI's slot colours of that piece; opening the panel used to put
  AltUI's colours back on.
* **Resetting a piece's colour** gives every slot its own factory colour. AltUI used the game's reset before, which
  gave all slots the colour of the first one.
* **Mods with the same row names in different tables** no longer get mixed up (for example, eyes shown as another mod's
  poses).
* **Looks with eyes or make-up that are no longer installed** list them in the "not available" note with the missing
  clothes.
* **Weapons: mod chips** no longer go missing for a weapon whose mods bring only a model or a sound – when the tab
  opens, after a click on a chip or while searching.
* ***Manage › Mods*** opens noticeably faster with many mods installed.
* **The panel camera** is no longer pulled in by followers, NPCs, zombies or ragdolls standing close.
* **Context menus** stay on the screen near its edges.
* **AltUI's notices** show above the panel instead of behind it.
* **The panel key** no longer closes the panel while you type a scene, pose or theme name or into a Mods tab field.
* French: the slot *Briefs* is now called *Dessous*.

## 1.9.0 – 2026-10-07

Replace `AltUI.pak`, and `weaponpak.pyz` if you convert weapon mods. `AltUI_Hook_P.pak`, `bodypak.pyz` and
`altui_names.pyz` are the same as in 1.8.0.

Ragdolls, a Codex with the AltUI manual, Jodi's walk and run speed, and shot sounds per weapon.

* **Ragdolls.** A new tab puts figures with physics into the level to place and pose: copies of Jodi, standing and
  frozen in her current pose with everything she wears, every kind of zombie from the encyclopedia with its variants,
  the nurse and a survivor. A look becomes a figure with "Spawn as ragdoll" in its context menu. Each figure is active
  (it falls and can be thrown) or frozen (it keeps its pose), and each of its 17 joints can be locked, free or movable.
  * With the mouse, beside the panel: drag a frozen figure to move it, the mouse wheel lifts it while you drag; drag an
    active one by a body part; right drag turns a figure; Shift + click locks or frees a joint; Shift + right click
    makes a joint movable, and dragging a body part below it then poses only that part.
  * **Poses** are saved per kind of figure and load onto every figure of that kind, in every level.
  * **Scenes** keep every figure of the level with its look, place, pose and joints; loading one replaces the figures
    that are there. Scenes belong to their level. Everything is saved in `AltUI_Ragdolls.sav`.
  * **Ragdolls mode**, a third round button above + and −: the panel goes away, the camera moves freely (W A S D, Q E),
    and the figures are moved and posed with the mouse as beside the panel. Esc or B ends it.
  * Quick menu actions: Ragdolls mode, a copy of Jodi, all figures active / frozen, activate / freeze the one in the
    middle of the screen, remove all. Ragdoll tiles have a size of their own under *Options › Tiles*.
* **Codex.** A new last tab with three sections:
  * **AltUI manual** – how every tab, the quick menu, the ragdolls and the installation work, in all seven languages.
  * **Encyclopedia** – the entries of the archive on Jodi's office computer, with picture and text. It shows the ones
    the game has unlocked, or all of them with a switch under *Options › General*.
  * **Passwords** – the code locks of the current level, nearest first, with their distance, the floor and whether they
    are locked. A code stays hidden until you click it.
* **Jodi's own walk and run speed**, under the new *Options › Movement*: walk and run from 50 to 200 %, "Reset to
  100 %", and "Own speed on / off" for the quick menu. Crouching and jumping stay as they are. The animation follows
  the speed, so the feet keep their grip.
* **Weapons: shot sounds to choose.** The Weapons tab has a third section, *Sound*, above model and skin: pick a
  weapon's shot sound on its own – a model you like with the sound you like, and every other weapon keeps its own. A
  click on a sound plays it. Weapons without a sound mod show no such section. A mounted suppressor with a sound of its own still wins. `weaponpak.pyz` converts
  shot-sound replacers (`…-SFX.pak`) into such entries; for the HK416 and SA58 it keeps the game's fade with distance.
* **Outfits, looks, saved faces and appearance presets can be moved** from their context menu: left, right, to the
  start or to the end. Names, colours and quick menu items stay with them.

Fixes:

* **Melee weapons get the model and skin chosen for them.** Until now AltUI put the choice only on guns.
* **A paint put on with a spray can survives opening the panel.** Opening the panel used to put the skin chosen in
  AltUI back on.
* **Outfits that differ only in a colour** each keep their own name, quick menu item and slot colours; before, they
  shared them.
* **Options › Quick menu: icons no longer go missing** while you scroll the list of available items.
* **AltUI no longer writes `AltUI_Log.sav`.** "Measure all" on the Poses tab and the weapon pictures wrote a log file
  into the save folder; if you have one, it can be deleted.

## 1.8.1 – 2026-10-04

Replace `AltUI.pak` – nothing else. `AltUI_Hook_P.pak`, `bodypak.pyz`, `weaponpak.pyz` and `altui_names.pyz` are the
same as in 1.8.0.

French, faster long lists, and the quick menu in every context menu.

* **French.** The panel now speaks French as its seventh language: chosen automatically when the game runs in French,
  or by hand under *Options › General*. It uses the game's own French words (Sac à dos, Garde-robe, Apparence,
  Morphologie, Fard à paupières …).
* **Long lists build faster.** The outfits page, the clothes list and "Available" under *Options › Quick menu* now
  create tiles only for the rows in view (and one more above and below) and refill them as you scroll; the scroll bar
  and the scroll length are those of the whole list. Before, every list built all its tiles at once, which took longer
  the more items it held. Rows still grow with their longest name.
* **The panel opens straight on its page.** It used to build the clothes page first, whatever page it then showed.
* **Options › Quick menu, "Available": three items to a row.** Long names wrap onto several lines, mods' actions are
  grouped under the mod's name, and ticking an item no longer rebuilds the whole page.
* **"Add to quick menu" / "Remove from quick menu" in the context menus** of outfits, looks, saved faces, appearance
  presets and poses, and – with a small menu of their own – on the tabs, on the entries of the Mods tab's list and on a
  mod's buttons and toggles.
* **Scroll speed up to 20x** (*Options › Controls*; it went up to 10x).
* **Mods tab: a mod that is not running** now says what usually causes that: the Blueprint Loader belongs in
  `Content\Paks\~mods`, and an `AltUI_Hook_P.pak` there must be from 1.5.0 or newer. Some mods only run in certain
  levels.

Fixes:

* **No more fatal error "Failed to find function Reset Clothes Physics in Jodi_C"** when a body is switched, the panel
  closes or a look is applied, in a game whose Jodi lacks that function (another game build, or a mod that replaces
  Jodi). AltUI now calls it by name and only logs a warning when it is missing.
* **Make-up and eye tints stay when the body is switched** in Body Shape or by a look with another body. The new body
  comes with fresh materials, and the tints were lost until the look was applied again.
* **Free camera and photo mode from the quick menu:** Esc now closes the panel again when it was opened only for them.
* **A wheel item whose target is gone** (for example a mod renamed its action) shows its id instead of the name of the
  item next to it.
* **Long names without spaces wrap in the middle of the wheel** instead of running out of it.

## 1.8.0 – 2026-10-04

With the Blueprint Loader, replace `AltUI.pak` and nothing else: it brings your look to the main menu and the loading
screen by itself. If you start AltUI with the hook alone, there is a new `AltUI_Hook_P.pak` (the first change since
1.5.0): replace it together with `AltUI.pak` to get the look there too - the old one keeps working in levels as before.
A hook from before 1.5.0 must not stay in `~mods/` (see 1.5.0). `altui_names.pyz` has changed (poses and presets);
`bodypak.pyz` and `weaponpak.pyz` are the same as in 1.5.0.

A quick menu on a key, options in categories, icons for the tabs, and Jodi as you made her in the main menu.

* **Quick menu.** Hold **4** (changeable) and a wheel opens in the middle of the screen; point at an item and let go
  to run it, or let go in the middle to do nothing. What goes into the wheel is ticked under *Options › Quick menu*, in
  an order you set yourself, up to 32 items: the free camera, the photo mode, opening AltUI, a saved outfit, look, face
  or make-up preset to put on, a favourite pose or "stop pose", a tab or a mod's entry to open AltUI on. Up to 12 items
  show their name under the picture; with more, the wheel shows pictures only and the name of the item under the mouse
  sits in the middle. The ring and its centre follow the panel's background opacity, or one of their own set right
  below the key; pictures and names always stay fully visible.
* **Mods can put actions into the quick menu.** The buttons and toggles a mod shows in the Mods tab are offered there
  by themselves (a toggle flips), and a mod can bring actions of its own with an icon in a table `AltUI_Actions`; see
  MOD_UI.md. The Mods tab example has one, "Lamp: next colour".
* **Options are sorted into categories.** A list on the left, like the other tabs have, chooses what the page shows:
  General, Tiles, Groups, Camera, Controls, Quick menu, Colours, Slot conflicts and Tabs. The page remembers the last
  category. Rows of chips wrap onto a second line on a narrow panel, and the sliders take the width that is there.
* **Tabs you do not use can be switched off** under *Options › Tabs*. A switched-off tab is left out of the tab bar.
  What a tab has applied stays applied: switching off Body Shape or Face does not change Jodi. A jump into a
  switched-off tab, such as "Show in tab", still opens it, and it stays in the tab bar until you leave it. Options
  itself cannot be switched off.
* **Icons for the tabs.** Under *Options › Tabs* the tab bar can show text only (as before), icons only, or icons with
  text, and the icon can sit left or right of the text. The quick menu shows the same icons for its tab items, and
  "Open AltUI" has an icon of its own: a small picture of the panel.
* **Jodi in the main menu and on the loading screen looks the way you made her.** Your chosen body and Body Shape
  values, the face settings and the colours of clothes, eyes and make-up used to appear only once a level was loaded.
  `AltUI.pak` does this with the Blueprint Loader; with the hook alone it needs the new hook file.
* **Your look is there as soon as a level has loaded.** Body, Body Shape, face and your own colours used to follow one
  to two and a half seconds later; they now come with the level.
* **Colour schemes can be saved under a name.** Under *Options › Colours*, type a name and click "save": all ten
  colours and both opacities are kept. Each saved scheme is a chip below; click it to apply it, right-click it to apply
  or delete it. Saving under an existing name overwrites that scheme.
* **Outfit and look tiles have a size of their own**, under *Options › Tiles*; look tiles go up to 250 %. Until you
  move these sliders they follow the general tile size. How many pieces an outfit tile shows is adjustable too: pieces
  per row and rows, 1 to 6 each, 3 × 3 by default. All tile sizes move in 1 % steps.
* **Appearance presets can be renamed.** Right-click a preset → Rename. The tile, the search and the quick menu show
  the name, and it stays with its preset when another one is deleted. Clearing the field gives back "Preset 2" and so on.
* **"View content" for saved faces.** Right-click a saved face → View content: a table of the values it fixes, per group
  (expression, gaze, mouth) and how the expressions mix, the same as the face part of a look's content view. A preset's
  content view shows the preset's own name.
* **Group and mod chips are in alphabetical order** on the Clothes, Appearance, Poses and Weapons tabs, by the name the
  chip shows, so your own names count. The game's own pieces (Basis / Vanilla) stay first and Hidden stays last.
* **Manage has chips** in Mods, Clothes, Appearance and Poses, like the tabs themselves: groups for clothes, mods for
  the others (a mod's chip shows that mod with its groups), with a search field for the chips and "..." to fold them. A chip narrows
  the rows; the list on the left keeps the totals and puts the hits in brackets behind them. Outside Mods, the
  identifier column no longer keeps room for a "View content" link those rows never have, Vanilla groups are no longer
  indented, and a shared group has an empty line before "also affects:".
* **Weapons: the left column counts models and skins separately** ("4 models, 6 skins"), matching the tiles the tab
  shows. With a search or a chosen chip, the hits follow in brackets, as on the other tabs.
* **A mod's content view opens faster.** Each slot section now looks only at the pieces of that slot instead of the
  whole catalogue, and each pose chapter only at the mod's own poses.
* **Filtering the clothes list does less work.** The text search is skipped while the search field is empty, and
  otherwise only runs for pieces the other filters let through.
* **Body Shape sliders no longer write the settings file every frame while you drag them.** The values are saved half
  a second after the slider comes to rest, when the panel closes, and when the level ends.
* The Mods tab example (`examples/AltUIMod_Example`) saves its settings without an unneeded cast; the editor files and
  the pak are rebuilt.

Fixes:

* **Weapon skins and models stay on a gun taken back out of the storage box.** The box gives back a new gun, and a gun
  put in and taken out while the box was open came back with its original look. The game's own gun paints were never
  affected.
* **"Camera follows slot / face" frames the slot in the middle of the picture** whatever camera height you set. Before,
  that height was added on top, so with the camera raised for the face the shoes ended up out of the picture. Dragging
  moves the picture from there until the next slot, within the same range for every slot; your own camera height
  comes back when no slot is in focus.
* **`altui_names.pyz` keeps the names of poses.** An import replaces all names, and the JSON had no section for poses:
  export and import lost every pose you had renamed. The JSON now has `poses` and `presets`.
* **The lines between the entries of the left-hand lists no longer go missing.** At some screen sizes every second or
  third line was not drawn.
* **Slider values are no longer cut off** in the Mods tab and on the Face tab. The slider takes the width that is
  there, and the value next to it always keeps its room.

## 1.7.0 – 2026-09-28

`AltUI_Hook_P.pak` (the hook file): unchanged since 1.5.0. Coming from 1.5.x or 1.6.0, replace only `AltUI.pak`. Coming
from an older version, the hook change of 1.5.0 still applies: replace the hook together with `AltUI.pak`, or delete it
from `~mods/` if you start AltUI with the Blueprint Loader. The converters in the archive are the same as in 1.5.0.

Jodi's face as a tab of its own, photos from the front or as you see her, and a key field for other mods.

* **Face tab: Jodi's facial expression, set by you.** A new **Face** tab mixes her face from the expressions the game
  has (relaxed, focused, smile, pain, fright, tired, two kinds of suffering), the direction of her gaze and seven
  mouth shapes, each with a slider. A ticked entry keeps its value, also in poses and while dancing; an unticked one is
  left to the game's animation as before. "Fix all" makes the whole face your own, "All to the game" gives it back.
  Every expression is a whole face and opens the mouth a little, so two of them at full strength would add up to a
  wide open mouth: by default the expressions are blended - together at most 100 % - and a link switches to adding
  them up. A "Close mouth" slider counters an opening you don't want. Faces can be saved with a photo, renamed,
  overwritten and applied again. A body mod without the game's face morphs is not affected, the tab says so. No game
  file is replaced.
* **Looks keep the face.** A look saved from now on brings back its face, blending included; a look saved before brings
  back the game's own face. "View content" of a look lists the face, and the body values there are now a table.
* **Photos from the front, or as you see her.** The tile that saves a look, a make-up preset or a face is split in two.
  The upper half takes the photo from the front - also when Jodi has been turned round by dragging, which used to give
  a photo of her back; for a preset or a face "front" follows her face, also when a pose turns her head. The lower half
  takes it just as the camera next to the panel sees her, from the side or from above. "Update" on a saved look, face
  or make-up preset offers both as well.
* **Make-up presets can be updated.** Right click on a preset: "Update" puts the current appearance into it and takes a
  new photo; the preset keeps its place.
* **Make-up presets keep your own eye and make-up colours.** The game's preset has no room for them, so AltUI keeps them
  beside it; applying the preset brings them back. A preset saved before brings the factory colours, like an old look.
* **"View content" shows your own colours** of make-up, lenses and lashes as a swatch on the tile, for looks and presets.
* **The panel leaves a third of the screen to Jodi by default.** Options → layout starts at "one third" instead of "no
  space for Jodi". Settings from an earlier version that still hold "no space" are switched to "one third" once; choose
  "no space" again in Options if you want it, and it stays.
* **Tiles only as tall as their content.** The space around a tile's picture is the same on all four sides; a tile with a
  long name grows, and the others in its row with it.
* **Mods tab: a key field.** A mod can let the player choose a key for it: a click on the field, then the key - Esc
  or a click cancels, a right click clears it. The mod gets the key through a fourth pair in `BPI_AltUIMod`; mods built
  with the older interface keep working as they are. The example lamp has one, the key that switches it on and off.
* **Mods tab: buttons answer the mouse.** Buttons, the key field, the arrows of a choice and - / + of a number light up
  under the mouse, stay dark while pressed and act when the mouse button is released over them.

Fixes:

* **Own eye and make-up colours survive a restart again.** Since 1.6.0 they were only kept until the game was closed.
* **A front photo is no longer white when something stands in the way.** With a wall or furniture 2 m in front of Jodi
  the camera sat behind it; now it stops in front and widens its angle, so the frame stays the same.
* **The Mods tab example's height works.** The lamp's light was not movable, so it could neither follow Jodi nor change
  its height.

## 1.6.0 – 2026-09-27

`AltUI_Hook_P.pak` (the hook file): unchanged since 1.5.0. Coming from 1.5.x, replace only `AltUI.pak`. Coming from an
older version, the hook change of 1.5.0 still applies: replace the hook together with `AltUI.pak`, or delete it from
`~mods/` if you start AltUI with the Blueprint Loader. The converters in the archive are the same as in 1.5.0.

A place in the panel for other mods, a panel that opens where it was left, and one more outfit colour fix.

* **Mods tab: other mods can put their settings into AltUI.** A mod that the player controls in the game - a lamp,
  say - no longer needs keys of its own: it registers entries and their fields in two data tables in its own folder,
  and AltUI shows them in a new **Mods** tab - toggles, sliders, numbers, choices, colours (with AltUI's
  palette), text fields, info lines and buttons - in its own style and colours. The mod's actor holds the values;
  AltUI reads them while the tab is open and sends every change at once, so a change the mod makes itself shows in the
  panel too. The tab only appears when such a mod is installed. `MOD_UI.md` describes it for mod authors, `uassets/`
  has the two row structures and the interface, and `examples/AltUIMod_Example/` is a finished mod to install and to
  rebuild.
* **The panel opens where it was left.** The tab and the choice inside it - clothes slot, appearance category, pose
  category, weapon, Mods entry - are kept, also across level loads and game restarts. A kept Mods tab without any such
  mod installed opens on the clothes page.
* **An outfit's colours land on the first try.** A piece that an outfit put on in place of another one sometimes kept
  the wrong colour and only took the outfit's colour when the outfit was worn a second time. For exactly those pieces
  the colour step asked AltUI's own list of worn pieces, which is only brought up to date once the whole outfit is on,
  and skipped them as not worn. It now asks the game.
* **Building from source is faster:** the blueprint generator builds only what changed since the last run, and a full
  run takes about half the time. `./build.sh --full` builds everything from scratch as before.

## 1.5.1 – 2026-09-27

`AltUI_Hook_P.pak` (the hook file): unchanged since 1.5.0. Coming from 1.5.0, replace only `AltUI.pak`. Coming from an
older version, the hook change of 1.5.0 still applies: replace the hook together with `AltUI.pak`, or delete it from
`~mods/` if you start AltUI with the Blueprint Loader. The converters in the archive are the same as in 1.5.0.

Mostly colour fixes, and the content views learned to put things on.

* **Colours are back as soon as a level has loaded.** The colours AltUI keeps of its own - one per material slot of a piece,
  the eye colours and the make-up tints - only went back on Jodi once the panel had been opened; until then she wore the
  game's colours. They are now put on two seconds after the level starts, without opening the panel.
* **A colour chosen in the palette is kept however the palette closes.** Closing the panel, or switching to free camera or
  photo mode, while the palette was still open left the new colour on Jodi but did not store it: the palette opened with
  the old colour next time, and the next time the panel opened the old colour went back on. This applied to clothes,
  eye and hair colours alike.
* **Content views put things on.** In the content of a mod, an outfit, a look or a preset, a click on a piece now puts it
  on or takes it off, and a click on a hairstyle, skin, make-up, body or pose applies it - as on its own tab. The right-click
  menu starts with the same action ("Wear", "Take off" or "Apply"). Before, the tiles there only showed what was inside,
  and "Show in tab" was the way to use one.
* **An outfit comes back in its own colours.** Wearing an outfit left every piece in the colour AltUI had given it since
  the outfit was saved - an outfit only knows the game's one colour per piece, and AltUI's colours were painted over it.
  AltUI now remembers the colours of each material slot when an outfit is saved and puts exactly those back when it is
  worn. A piece without remembered colours - every piece of an outfit saved before this version - shows the outfit's
  own colour, or the factory colour, instead of the one it wore last.

## 1.5.0 – 2026-09-27

`AltUI_Hook_P.pak` (the hook file): **changed** – replace it together with `AltUI.pak`. Whoever starts AltUI with the
Blueprint Loader instead deletes the old hook from `~mods/`: it claims the camera manager class for itself, and one from
before 1.5.0 does not start the loader. New in the archive: `weaponpak.pyz`, the converter for weapon mods.
Bodies converted before keep working; convert them again where the old converter dropped numbered materials, or to get the
new `BodyAltUI_` name.

### Weapons

* New tab **Weapons**, with `weaponpak.pyz` to feed it. Weapon mods replace the same files of the game and used to exclude
  each other; the converter turns such a pak into its own `WeaponAltUI_<Name>.pak`, so any number of them can be installed
  side by side. Each weapon of the game gets an entry, and for it a **model** and a **skin** are chosen separately and
  remembered - so a modded model can wear any skin, and the game's own gun paints are listed there too, without the spray
  can. Magazine, optics, suppressor and grip come along with a model.

  Every tile carries a rendered picture of that weapon with that model and that skin; **"Take pictures again"** in the
  status bar renders the ones of the weapon you are looking at. A model mod that brings a picture of its own can show that
  one instead - right-click the tile.

  A skin works by overwriting three texture parameters, and a mod's own materials often do not have them, so a skin can do
  nothing on a modded model. Tiles that cannot do anything are dimmed, and a model's tile menu can **force the game's own
  weapon material** onto the whole weapon, which makes skins work on it - at the price of the mod's own material setup, and
  with the skin's texture following a UV layout it was not painted for. Off by default, per model, reversible, and single
  pieces of equipment can be left out of it.

### Poses

* New tab **Poses**: every action animation of the game and of installed pose mods - the same list the phone offers - as
  tiles with chips per mod, search, favourites and hiding; click plays, click again or "Stop pose" stops; the panel stays
  open. "Measure all" sorts them by how Jodi ends up standing, sitting or lying; both it and "Stop pose" sit in the status
  bar.

### Colour

* **Make-up can be tinted**, each entry on its own - lipstick, eyeshadow, blush, eyeliner, brows, nails and tattoos:
  right-click a tile, "Tint…", pick a colour, and "Reset tint (default)" brings that one entry back to the game's own look.
  The colour multiplies the entry's own drawing, so a pale or neutral one takes it almost fully while a dark one can only be
  shifted or darkened - and white means "unchanged". Nothing else on the face is touched: the game draws everything as it
  always does, only the tinted entries are left out of its pass and drawn by AltUI afterwards.

* **Jewellery and everything else takes a colour**, and a piece with several materials takes **one colour per material
  slot**. The game's own slider is switched on by a flag in its clothes table, and that flag is off on almost all jewellery -
  no necklace, no pair of glasses could be coloured, although every clothes shader carries the parameter for it. AltUI now
  measures instead of reading the flag: it asks each material of a piece whether it knows the colour parameter, and the
  colour-wheel on a tile says what came out. The context menu of a worn piece lists one "Colour…" row per material slot that
  answers, named after the slot when there is more than one, so a dress can wear one colour on the fabric and another on the
  trim. Material slots the game leaves alone (their name carries `FixedColor`) stay untouched. Pieces that cannot take a
  colour are not greyed out - they are ordinary clothes, they just have no colour-wheel.

* Appearance: **iris and eyelashes get a colour of their own** - right-click a contact lens or a pair of lashes. The colour
  belongs to that lens (or those lashes), the way the game keeps a hair colour per hairstyle: another lens keeps its own.
  The game writes a colour from its eye table onto the same material parameters whenever it rebuilds the eyes, and these sit
  on top of that; "Reset colours (default)" on the tile brings the table colour back. Make-up is a different matter: it is
  drawn into a texture, and neither its table nor the skin shader carries a colour at all - there is no parameter to turn.
  That is why make-up is **tinted** instead, by AltUI drawing the tinted entries itself (above).

* **Where the colours are and are not.** AltUI puts them on Jodi while you are in a level, which is where it runs. The main
  menu is not one: the Jodi shown there wears the game's factory colours, whatever you picked. The same holds for anything
  else that looks at her without AltUI running.

* A saved **look carries all of it** - the slot colours of its pieces, the eye colours and the make-up tints. A look from an
  earlier version loads unchanged and means "factory colour".

### Filters and search

* New filter **"only worn"** on the clothes page and on the appearance page. On the clothes page it leaves the pieces Jodi
  has on, on the appearance page the entry that is applied in each category - skin, every make-up type, lenses, lashes - and
  where several entries of one type are on, all of them. It combines with the other filters, a group chip and the search,
  and it is remembered like they are.

* A **search of its own above the chip row**, on the clothes page and on the appearance page: it filters the group and mod
  chips by display name and identifier and leaves the list of tiles alone. "All", "...", "Vanilla", "Hidden" and the
  selected chip always stay, so the row is never empty; while there is text in the field the chips show even when "..." has
  collapsed them, and clearing it collapses them again. Where there is nothing to choose the row is gone. Switched off in
  Options ("Show chip search"), on by default.

* **Every search box follows the colour scheme.** Only the one on the clothes page did, so after a theme change the boxes on
  the appearance and manage pages sat visibly beside it.

### Jodi view

* The **mouse wheel over Jodi** changes the camera distance in 4 % steps (wheel up = closer); +/− stay at 5 %.

* **Click on Jodi and drag** – sideways turns her, up and down moves the camera along her, so you can look at her from
  higher or lower. She turns back when the panel closes; the camera height is kept and also sits in Options as a slider
  ("Camera height"), and it applies only while the panel is open. Anyone who wants the left button for turning alone can
  move the height to the right mouse button in Options.

* The camera **no longer backs into a wall**. Opening the panel moves the camera back to fit Jodi beside it, which in a
  narrow room used to put it behind the wall; it now stops in front of whatever is in the way and shows Jodi from closer
  instead. Turn the view and the set distance is back.

* The **mouse wheel over the panel no longer moves the Jodi view**. Over plain panel background, and in a list that has
  scrolled to its end, nothing consumed the notch, so it reached the camera and the view drifted while one was scrolling.

### Body Shape and converted bodies

* The **bust slider** lets the breast stand out, not just spread. It scaled the bone across but never along the axis the
  breast projects in, so turning it up only made her wider. It now takes that axis in the same proportion the game's own
  breast morph uses (0.2 against 0.35), which is why the shape no longer changes character where the game's slider ends at
  100 % and the bone slider takes over. A saved look with the bust above 100 % therefore looks a little fuller than before.
  The hips / glutes slider grows evenly in all directions now; it carried the setting meant for limbs, where only thickness
  should change.

* **A converted body can show parts of itself through tight clothes**, and that is the body, not the conversion. The game
  presses those parts flat with morph targets that sit on the body mesh; Jodi's own carries 23 of them. A body mod whose
  mesh brings none has nothing to press with, and no mod and no setting can add them afterwards. `bodypak.pyz` does not lose
  them - where the original has them the converted body has them too, and where the original has none, there is nothing to
  keep. If you see it, try another body or ask its author.

* Switching the **body mod while playing** no longer leaves body parts standing out under tight clothes. Replacing the mesh
  drops every morph the game had set on it - the ones that press such parts flat under clothing among them - and nothing
  brought them back until the next time something was put on or taken off. AltUI now asks the game to redo its body mask
  right after the swap, which restores those morphs and the mask; the breast and hip physics come back with it, instead of
  staying dead until the height slider was touched.

* `bodypak.pyz` lost a body's own materials and textures whenever the mod numbered them (`MI_Skin_1`, `MI_Skin_2`). Unreal
  keeps such a trailing number apart from the name - `MI_Skin_1` is stored as the name `MI_Skin` with the number 2 - and the
  converter compared the name alone, so a numbered package never matched and stayed behind. Convert affected bodies again
  with this release's converter.

* Converted bodies are named **`BodyAltUI_<Name>`**: the prefix says what the pak is built for, where a plain `Body_` is a
  name any body mod might pick for itself. Bodies converted before keep working - `Body_` is still read, and where one body
  is installed under both names the `BodyAltUI_` one is listed and the other ignored.

### Starting AltUI

* AltUI can be started by the **Blueprint Loader** instead of by its own hook pak: `AltUI.pak` carries a loader table
  (`TKA_BlueprintLoader`) and an entry actor, so the loader starts the panel. Installed that way AltUI replaces no file of
  the game at all, and the hook pak becomes optional – it stays in the release for anyone who does not want a second mod,
  and both installed together still work: only one of the two paks wins the replaced class, and whichever it is, AltUI
  starts - through the loader's table, or through the hook, which then starts the loader itself so that mods built for it
  keep running.

* The camera framing beside the open panel no longer needs a replaced class. It lives in a camera modifier that attaches to
  whichever `PlayerCameraManager` the level has, so the framing works on the game's own class as well. **The hook file
  changed with it and has to be replaced.** With the one from 1.4.0 the panel still opens, but nothing shifts the view any
  more: Jodi sits behind the panel instead of beside it. So replace `AltUI_Hook_P.pak` along with `AltUI.pak`. Whoever
  switches to the Blueprint Loader instead takes the old hook out of `~mods/`: it claims the camera manager class for
  itself, and one from 1.4.0 does not start the loader, so the mods built for it stay dead.

* AltUI now lists itself in the game's own mod list. Its mod table shipped without an entry, so the game mounted the pak but
  knew nothing about the mod – which also made AltUI invisible to anything that goes by that list.

### Language

* **Polish** as a sixth panel language, next to English, German, Chinese, Russian and Spanish: picked up automatically when
  the game runs in Polish, or chosen in Options → Language. The terms follow the game's own Polish text wherever it has one
  (Plecak, Szafa, Wygląd, Talia, Brwi, Cienie do powiek, Obuwie, Fryzura, Zestaw do szycia), so the panel reads like the
  rest of the game.

## 1.4.0 – 2026-09-21

`AltUI_Hook_P.pak` (the hook file): **unchanged since 1.1.0** – only `AltUI.pak` needs replacing. Bodies converted with an older `bodypak.pyz` keep working but have no bone-scale sliders; re-convert them with the 1.4.0 converter to get them. New in the archive: `altui_names.pyz` (export / import of your display names).

* Options: "Not owned items" – `locked` (as before: greyed, cannot be put on), `greyed` (greyed but wearable, also in looks) or `like owned` (shown like everything else); applies to clothes and hairstyles. The "only owned" filter and the tooltips keep showing real ownership.
* Jodi view: +/− now mean closer / farther (was the other way round). Two more round buttons above them. **Free camera** – starts from the current view; the mouse turns, W A S D move, Q / E go down / up, Shift is faster, the mouse wheel changes the speed; the camera stays within 6 m of Jodi, stops at walls and Jodi herself and slides along surfaces; Esc brings the panel back exactly as it was. **Photo mode** – opens the game's own photo mode (depth of field, focal length, light, screenshot); Esc returns to the panel. B closes everything in both. No hook update needed.
* **Manage tab**: your own display names for mods, groups, clothes, hairstyles, skins and make-up – used everywhere in the panel and found by the search (the identifier stays searchable; the tooltip shows both). `altui_names.pyz` exports/imports them as JSON. In the rows, upper-case prefixes (`PAK:`, `G:`) mark display names and lower-case ones (`pak:`, `g:`, `id:`) identifiers; a group shared by several paks lists the others as `PAK: <name>`; renaming updates every row showing that name at once; the Mods category has "search" and "like pak" / "like g" links under the display name (the identifier as display name); the search has a "case-sensitive" checkbox. Option "Merge groups with the same name (clothes)": groups that share a display name become one chip (and one filter) on the clothes page; "Merge mods with the same name (appearance)" does the same for the mod chips of the appearance page.
* Body Shape: bone-scale sliders for converted bodies (`bodypak.pyz` attaches the AltUI animation blueprint): scale (whole body), bust, waist extra, glutes/hips, thighs, calves, arms, hands, feet – each a factor on top of the body's own shape, saved per body, "Reset shape" chip; a note above the bone sliders says they need a converted body (the scale slider works for every body); scale slider range 90–120 %; the scale and feet sliders keep the soles on the floor (the skeleton is shifted to compensate – before, Jodi floated or sank by up to a few cm). "Waist extra" scales the game's own waist bone in the same direction (and orientation: left = wider) as the mirror's waist slider, so it reaches narrower and wider than the game allows (the game's breast/waist sliders themselves stop at 0 % / 100 % – the engine clamps them).
* Clothes context menu: "Only this group" (group chip + All), "View mod content" – everything a mod adds, across slots, hairstyles, skins and make-up. The search also matches mod and group names.
* Options: "Slot conflicts" – the game's slot conflicts (e.g. bra vs. shirt, top vs. coat), read from its own table, can be freed per pair, per slot or all at once; AltUI's wear actions (clothes page, looks, backpack) then keep the underneath piece on. The mirror wardrobe still follows the game; meshes may clip.
* Appearance: a search box like the one on the clothes page (identifier, display name, mod name; the categories show the hits). Category "All" on top: skins and every make-up type on one page (presets stay their own category). A chip row like the one on the clothes page – "All", "…", "Vanilla", one chip per mod (skins, make-up and eyes have no groups, only an origin) – with the same options (name length, area height), plus "only favourites"; favourites and hidden rows via the tile's context menu ("Hidden" chip like on the clothes page; kept apart from the clothes lists); mod rows also get "Rename mod…", "Only this mod" and "View mod content" there.
* Coiffure: "Natural hair colours" – 14 preset swatches, applied with one click.
* Tooltips: every tile (clothes, hairstyles, skins, make-up, mod content) uses the same layout with the prefix convention – name, `Default:` when renamed, `s:` slot or category, `Vanilla` or `PAK:` mod name + `pak:` pak name, `G:` group + `g:` id, `id:` row. Options "Tooltips without prefixes" and "Tooltips: display names only" (drops the `pak:` / `g:` / `id:` lines).
* Tooltip of a piece always ends with its identifier (`id: …`).
* Manage: the left column is Vanilla · Mods · Clothes (section: All, then the slots) · Appearance (section: All, Hairstyles, Skins, the make-up types); counts as on the clothes page – total, plus the hits while searching. In a piece's row the `pak:` line links to the mod's content view and a click on the image jumps to the piece. Vanilla lists the groups of the game's own clothes (their chips on the clothes page can now be renamed too; a group a mod also uses lists that pak under "also affects:"); the "only mods" checkbox is shown for Clothes and Appearance only.
* Clothes: with a group chip selected the slot counts show the pieces of that group in parentheses.
* Backpack: "Everything into the backpack" link – takes every worn piece off, into the backpack.
* "Rename…" in every tile's context menu (clothes, hairstyles, skins, make-up, backpack, content views) edits the display name on the tile; "Rename mod…" / "Rename group…" jump to the row in the Manage tab.
* Backpack context menu: "Show in tab" (jumps to the piece on the clothes page) and "Rename mod…" for mod pieces; content views (looks, outfits, presets, mod content) also offer "Rename mod…" on mod pieces.

## 1.3.2 – 2026-09-19

`AltUI.pak` and the hook file (`AltUI_Hook_P.pak`): **unchanged** – this release only replaces `bodypak.pyz`.

* Body-mod converter: no bundled native code any more. 1.3.1 shipped the Oodle decoder as a Windows DLL (plus a Linux `.so`) inside `bodypak.pyz`; unsigned, cross-compiled and unpacked to the temp folder at runtime, it was flagged as a trojan by Windows Defender's heuristics and the file could not be downloaded. The decoder is now a pure-Python port of the same open-source project ([ooz](https://github.com/powzix/ooz), GPL-3) – `bodypak.pyz` is a small script again with nothing in it to flag. The conversion itself is unchanged – bodies converted with 1.3.1 stay as they are, no re-convert needed.
* `bodypak.pyz` is licensed GPL-3 (it contains the ported decoder); the paks and the rest of AltUI stay MIT.

## 1.3.1 – 2026-09-19

`AltUI.pak` and the hook file (`AltUI_Hook_P.pak`): **unchanged** – this release only replaces `bodypak.pyz`.

* Body-mod converter: assets the mesh uses from the same pak now travel with it. Some body mods (e.g. "Jodi Bigger Retail Body") get their shape not from the mesh but from their own animation blueprint that scales bones; the converter used to take the mesh alone, so the converted body loaded without its blueprint and looked like the standard body. Re-convert such bodies with the new `bodypak.pyz`.
* Body-mod converter: files the mesh does not use (skin textures shipped in the same pak) are still left out, but are now listed in the output and in `Body_<Name>_convert.json`.
* Body-mod converter: reads Oodle-compressed paks on Windows and Linux with the bundled open-source decoder [ooz](https://github.com/powzix/ooz) (GPL-3). Still Python 3.8+, no packages.

## 1.3.0 – 2026-09-18

Hook file (`AltUI_Hook_P.pak`): **unchanged since 1.1.0** – no need to re-download it.

* Clothes: new **only vanilla** filter next to "only owned" / "only favourites" – hides every piece that comes from a mod, in any slot, sub-tab and in "All". The "Base" sub-tab was the closest thing before, but it only lists pieces without a group: vanilla pieces with a theme (Lace, Kpop, …) or with a wardrobe tab that differs from their slot (Suit02: slot Shirt, tab Dress) live under their own sub-tab. Like the other filters it is remembered, and "Show in tab" switches it off when it would hide the piece.
* Clothes: the "Base" sub-tab is now called **No group** – that is what it is.
* Clothes: with a filter or a search active, the slot list shows "total (matching)" per slot, e.g. `312 (41)`.
* Clothes: long group chip rows (one chip per mod) no longer push the list down – the chip area shows about three rows and scrolls beyond that, and a **...** chip right of "All" collapses the group chips to the selected one (click again to expand; remembered).
* Options: new slider **Group names: max. characters** (3 … 20 or unlimited) – shortens the group chip captions in the Clothes tab so long mod names take less room. The cut is in the middle (`Wan..029`, the dots do not count), so groups that share a prefix stay distinguishable; the selected chip stays complete while the row is collapsed.
* Options: new slider **Group chip area: max. height** (112 … 500) – how tall the chip area may grow before it scrolls.
* Clothes: clicking another slot keeps the selected group chip when that slot has the group too (before: always back to All).

## 1.2.0 – 2026-09-17

Hook file (`AltUI_Hook_P.pak`): **unchanged since 1.1.0** – no need to re-download it.

* Content view for outfits, presets and looks (right-click → **View content**): every piece, hairstyle, skin, makeup style and body setting inside, with the stored colours; stays open per tab until you go back.
* Right-click a piece in the content view → **Show in tab** jumps to it in its own tab (slot and group chip, coiffure, appearance category or body shape), clears the search, switches off a filter that would hide it, highlights the tile and scrolls it into view.
* Appearance → Presets: the "+" tile said "Save current outfit"; it now says "Save current appearance".
* Body Shape: the hip slider is gone – the game has no hip morph (only chest and waist), so it never changed anything. Saved looks keep loading.

## 1.1.0 – 2026-09-16

First public release.

* Eight tabs: Clothes, Outfits, Looks, Backpack, Coiffure, Appearance, Body Shape, Options; undo / redo; tooltips with origin mod.
* Looks with in-game full-body photo; outfit names; hide items; persistent filters; colour reset; colour-adjustable badge.
* Body switcher for converted body mods (`bodypak.pyz`).
* Options: panel key (default **B**), five languages (EN / DE / ZH / RU / ES), colour scheme and opacity, tile size, camera FOV / distance / pan, "underwear may be taken off".
