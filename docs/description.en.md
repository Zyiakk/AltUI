# AltUI – wardrobe & appearance panel

Full description of the [Steam Workshop item](https://steamcommunity.com/sharedfiles/filedetails/?id=3802875867) – the workshop page itself shows a short version.

This description in other languages: [DE](https://github.com/Zyiakk/AltUI/blob/main/docs/description.de.md) · [ZH](https://github.com/Zyiakk/AltUI/blob/main/docs/description.zh.md) · [RU](https://github.com/Zyiakk/AltUI/blob/main/docs/description.ru.md) · [ES](https://github.com/Zyiakk/AltUI/blob/main/docs/description.es.md) · [PL](https://github.com/Zyiakk/AltUI/blob/main/docs/description.pl.md) · [FR](https://github.com/Zyiakk/AltUI/blob/main/docs/description.fr.md)

The vanilla wardrobe gives every mod author their own tab, so with a few clothing mods installed the same kind of item is scattered across a dozen tabs and there is no way to search. AltUI sorts every item from the game and from all installed mods into **one list per slot** (tops, skirts, shoes, …), with search, filters, favourites and hiding – and puts hair, makeup, body and outfits into the same panel. It opens anywhere in a level with **B**; no trips to the wardrobe or the mirror.

Also on [Nexus Mods](https://www.nexusmods.com/thekillingantidote/mods/988) (both files in one archive). Same mod – pick one source, not both.

> ⚠️ **Warning:** Made for game version 0.6.x. A game update that changes the clothes / makeup tables or the camera manager may break the mod.

## ⚠ Installation – read this first

Subscribing installs the mod itself, **AltUI.pak**. One more file has to start it, and the workshop cannot place that one for you, because it goes into a folder of the game the workshop does not touch. Without it, **B does nothing**. Two ways to do it – pick one, both together work as well.

**1. With the Blueprint Loader (AltUI replaces nothing of the game)**

1. Subscribe to this item.
2. Get **TKA_BlueprintLoader.pak** from https://www.nexusmods.com/thekillingantidote/mods/994
3. Copy it to
   `Steam\steamapps\common\TheKillingAntidote\TheKillingAntidote\Content\Paks\~mods\`
   Create the folder **~mods** if it does not exist (the name starts with a tilde). The game folder name appears twice in the path – that is correct.
4. Start the game, press B in a level.

AltUI carries a table the loader reads, and the loader starts the panel from it. The same loader starts every other mod that ships such a table, so this is the way to go if you use more than one of them.

**Upgrading from an older AltUI: if an AltUI_Hook_P.pak is still in ~mods, delete it. The hook claims the camera manager class for itself, and one from before 1.5.0 does not start the loader - the panel would open without the view moving aside, and mods built for the loader would stay dead.**

**2. With the hook pak (one file, from the AltUI release)**

1. Subscribe to this item.
2. Download **AltUI_Hook_P.pak**: https://github.com/Zyiakk/AltUI/releases/latest/download/AltUI_Hook_P.pak
3. Copy it into the same *~mods* folder as above.
4. Start the game, press B in a level.

The hook replaces *TKA_PlayerCameraManager* and starts the panel from there. Any mod that replaces the same blueprint conflicts with it – the Blueprint Loader is one of them, and that pair is the exception: with both installed the hook wins the class and starts the loader itself, so mods that need the loader keep working.

**“I subscribed but B does nothing”** → nothing has started the panel: either the second file is missing, or it sits in *Mods* or in the workshop folder instead of *Content\Paks\~mods*.

## What it does

* **Clothes** – every item of the game and of your mods, one list per slot, with search, filters, favourites and hiding.
* **Outfits · Looks** – the game's presets with names, and complete looks (clothes with colours, hair, makeup, eyes, skin, body, face) saved with an in-game photo.
* **Backpack · Coiffure · Appearance** – what Jodi wears and carries; hairstyles and hair colours; skin, makeup and eyes, each tintable.
* **Body Shape** – breast / waist sliders, a switcher for converted body mods, bone-scale sliders per body.
* **Face** – Jodi's expression, gaze and mouth as sliders; the face holds in poses and while dancing; saved faces with a photo, their values under “View content”.
* **Weapons** – model, skin and shot sound per weapon, melee weapons included, side by side from every weapon mod, with a rendered picture on each tile; a click on a sound plays it.
* **Poses** – every action animation of the game and of pose mods, sorted into standing, sitting and lying.
* **Mods** – the settings of other mods that register there: toggles, sliders, numbers, choices, colours, text fields, info lines, keys and buttons. Only shown when such a mod is installed.
* **Quick menu** – hold **4** (changeable) and a wheel opens with what you use most: free camera, photo mode, a saved outfit, look, face or preset, a favourite pose, a tab, and actions of other mods. Up to 32 items, picked and sorted in Options; let go on one to run it. A right click on a tile, a tab or a mod's entry puts it into the wheel or takes it out.
* **Options** – sorted into categories you pick from a list on the left: panel key, language, colours (schemes can be saved under a name), a tab bar with icons, text or both, and tile sizes, set separately for outfits and looks. Tabs you do not need can be switched off.
* **Manage** – your own display names for mods, groups and items. As in Clothes, chips filter the list by mod or group, and a search field narrows down the chips.
* **Ragdolls** – copies of Jodi, zombies and people as figures with physics: place them, pose them joint by joint, freeze them or let them fall; poses per kind of figure and whole scenes per level are saved. A ragdolls mode moves them without the panel.
* **Codex** – the AltUI manual in all seven languages, the game's encyclopedia and the code locks of the current level, each code hidden until you click it.
* **Movement** – Jodi's own walk and run speed (50–200 %), under Options.
* Undo / redo (5 steps), tooltips showing which mod an item comes from.

Languages: English, German, Chinese, Russian, Spanish, Polish, French (auto-detected, switchable in Options).

## Controls

* **B** – open / close (changeable in Options). **Esc** closes.
* **4** – hold for the quick menu (changeable in Options); let go on an item to run it, or in the middle to do nothing.
* Left click – select / wear / apply. Right click – context menu. Mouse wheel – scroll.

## Body mods

Body replacer paks all overwrite the same game file, so only one can be active. A small converter turns a replacer into a regular mod pak that keeps the mesh under its own path; any number of converted bodies can be installed side by side and appear as chips in the Body Shape tab.

Guide (Windows, Linux): [BODY_MODS.md](https://github.com/Zyiakk/AltUI/blob/main/BODY_MODS.md) · bodypak.pyz: https://github.com/Zyiakk/AltUI/releases/latest/download/bodypak.pyz

## Mod updates and the second file

Whatever starts the panel is deliberately kept apart from the panel itself: everything the mod does lives in the workshop pak. So when this item updates through Steam, the file you put into *~mods* **normally keeps working – no need to touch it**.

The Blueprint Loader itself needs nothing: it is its own mod and updates on its own page. An AltUI_Hook_P.pak from before 1.5.0 must not stay in ~mods (see the note under Installation): delete it or replace it with the current one.

**Using the hook without the Blueprint Loader:** Since 1.8.0 AltUI also puts your look on Jodi in the main menu and on the loading screen. With the hook alone that needs the current AltUI_Hook_P.pak – replace an older one to get it; in levels the older one keeps working. With the Blueprint Loader, AltUI.pak does it by itself.

No game assets are included; everything in the pak is generated.

## What each combination does

* **AltUI.pak alone** – nothing starts the panel – B does nothing.
* **AltUI.pak + Blueprint Loader** – the loader reads AltUI’s table and starts the panel. AltUI itself replaces nothing of the game; the loader replaces the game’s camera manager class, which is how it works.
* **AltUI.pak + AltUI_Hook_P.pak** – the hook replaces the game’s camera manager and starts the panel.
* **AltUI.pak + both** – fine, and nothing is lost. Both replace the same game class, so only one of the two paks wins it – and whichever it is, AltUI starts: through the loader’s table, or through the hook, which then also starts the loader itself, so mods built for it keep running.
* **The hook or the loader without AltUI.pak** – nothing – the mod itself is missing.

## What it cannot do

Two limits worth knowing:

* **Make-up takes a tint, not a new colour.** The colour is multiplied onto the drawing that is already there, so a pale or neutral one takes it almost fully while a dark one can only be darkened or shifted. White means “unchanged”, not white make-up.
* **A converted body can show parts of itself through tight clothes.** The game presses those flat with morph targets that sit on the body mesh, and a body whose mesh brings none has nothing to press with. That is the body, not the conversion: the converter keeps whatever the original has, and where the original has none, nothing can add them.

## Source & issues

https://github.com/Zyiakk/AltUI – source code (MIT), all downloads, bug reports.
