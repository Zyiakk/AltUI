# Changelog

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
