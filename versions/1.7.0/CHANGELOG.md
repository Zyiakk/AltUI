# Changelog

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
