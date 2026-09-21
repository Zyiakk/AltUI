# Changelog

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
