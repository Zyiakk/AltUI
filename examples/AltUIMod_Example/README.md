# `AltUIMod_Example` - settings in AltUI's Mods tab

A complete, working mod that puts its settings into AltUI's **Mods** tab. It is a
lamp in front of Jodi, and the Mods tab shows one entry, **"Example lamp"**, with a header and one field of every other kind:

| Field | Type | What it does |
|---|---|---|
| Now | info | shows the lamp's state and the note, updated live |
| Light | toggle | switches the lamp on and off |
| Key for on/off | key, L at first | the key that switches the lamp in the game (with the panel closed); right click: none |
| Brightness | slider, 0 to 20000 in steps of 500 | its intensity |
| Height (cm) | number, -100 to 200 in steps of 10 | how high it hangs in front of her |
| Colour | choice: Warm, Cold, Red, Custom | its colour |
| Custom colour | colour, AltUI's palette | the colour for "Custom" - picking one switches the choice to it |
| Note | text | any text; the info line shows it |
| Back to the defaults | button | everything back as it was |

It also brings one action for AltUI's **quick menu** (`AltUI_Actions`): **"Lamp: next colour"**, with an icon of its
own, steps through the colours. Tick it under *Options › Quick menu*, next to "Example lamp › Light" and "Example
lamp › Back to the defaults", which the quick menu offers by itself because they are a toggle and a button.

## Try it

1. Install the [Blueprint Loader](https://www.nexusmods.com/thekillingantidote/mods/994) - it starts the lamp's actor.
2. Copy `AltUIMod_Example.pak` into `TheKillingAntidote/Mods/`.
3. Start a level, open AltUI: a tab **Mods** appears. Pick "Example lamp" and use the fields.

The lamp keeps its settings across level loads in a save file of its own (`AltUIMod_Example.sav`): AltUI only shows
the values and reports changes, the mod holds and saves them. Remove the pak to get rid of it; it changes no game file.
Without AltUI the lamp still shines, it just has no settings.

## Build your own from it

The eight files under `editor/` are the uncooked assets; [MOD_UI.md](../../MOD_UI.md) explains each of them and the
rules. They refer to each other by their full path - the actor to its save game, the tables and the loader row to the
actor - and that path is `/Game/Mod/AltUIMod_Example/`. Copied into a folder with any other name, those references
point at nothing: the blueprint shows broken nodes, does not compile, and the project does not cook. So:

1. Copy the eight files into your project at exactly `Content/Mod/AltUIMod_Example/` - that folder name, no other.
2. Copy `S_AltUIModEntry.uasset`, `S_AltUIModField.uasset`, `S_AltUIModAction.uasset` and `BPI_AltUIMod.uasset` from
   [`uassets/`](../../uassets/) into `Content/Mod/AltUI/`, again at exactly that path. Do not ship those four in your
   pak.
3. The loader row needs the Blueprint Loader's `BlueprintToLoad_Struct` at `Content/Mod/TKA_BlueprintLoader/`, and
   `TKA_Mod_Table` needs the game's `DLC_Struct` at `Content/Project/Tables/` - both are in any project that already
   builds mods for the Blueprint Loader.
4. Start the editor. Everything opens and compiles; you can cook the example as it is.
5. To make it yours, rename in the editor's **Content Browser**, never in the file manager: rename the folder
   `AltUIMod_Example` to your mod's name (the pak's name without `.pak`), and the assets as you like. The editor
   rewrites every reference. Then right-click the folder and choose *Fix Up Redirectors in Folder*, so no redirector
   pointing to the old name is left behind.
