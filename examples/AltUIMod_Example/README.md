# `AltUIMod_Example` - settings in AltUI's Mods tab

A complete, working mod that puts its settings into AltUI's **Mods** tab instead of binding keys of its own. It is a
lamp in front of Jodi, and the Mods tab shows one entry, **"Example lamp"**, with a header and one field of every other kind:

| Field | Type | What it does |
|---|---|---|
| Now | info | shows the lamp's state and the note, updated live |
| Light | toggle | switches the lamp on and off |
| Brightness | slider, 0 to 20000 in steps of 500 | its intensity |
| Height (cm) | number, -100 to 200 in steps of 10 | how high it hangs in front of her |
| Colour | choice: Warm, Cold, Red, Custom | its colour |
| Custom colour | colour, AltUI's palette | the colour for "Custom" - picking one switches the choice to it |
| Note | text | any text; the info line shows it |
| Back to the defaults | button | everything back as it was |

## Try it

1. Install the [Blueprint Loader](https://www.nexusmods.com/thekillingantidote/mods/994) - it starts the lamp's actor.
2. Copy `AltUIMod_Example.pak` into `TheKillingAntidote/Mods/`.
3. Start a level, open AltUI: a tab **Mods** appears. Pick "Example lamp" and use the fields.

The lamp keeps its settings across level loads in a save file of its own (`AltUIMod_Example.sav`): AltUI only shows
the values and reports changes, the mod holds and saves them. Remove the pak to get rid of it; it changes no game file.
Without AltUI the lamp still shines, it just has no settings.

## Build your own from it

The six files under `editor/` are the uncooked assets; [MOD_UI.md](../../MOD_UI.md) explains each of them and the
rules. In short: copy them into your project at `Content/Mod/<YourModName>/`, and copy `S_AltUIModEntry.uasset`,
`S_AltUIModField.uasset` and `BPI_AltUIMod.uasset` from [`uassets/`](../../uassets/) into `Content/Mod/AltUI/` - at
exactly that path, because your tables and your actor refer to them there. Do not ship those three in your pak.
