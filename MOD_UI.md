# Putting your mod's settings into AltUI

A mod that the player controls in the game usually binds keys of its own - one to switch a lamp on, one for the next
colour, one for a menu. With a few such mods installed, keys run out and nobody remembers which does what. AltUI
offers such mods a place in its panel instead: a **Mods** tab that lists every mod that registered there and shows
its settings - toggles, sliders, numbers, choices, colours, text fields, info lines and buttons - drawn in AltUI's own
style and colours.

The tab only appears when at least one installed mod registers something. A mod does not need AltUI to run: without
it, the two tables described below are simply never read.

## What the player sees

The Mods tab sits before Options. On its left is a list of entries - one mod can bring several, for example "Desk
lamp" and "Ceiling lamp". Choosing an entry shows its fields on the right. Every change goes to the mod at once (a slider
while it is being dragged), and a value the mod changes itself - through a key of its own, say - shows in the panel
as well. When the mod is not running in the current level, its fields are greyed out with a note saying so.

## What a mod needs

1. **An actor in the level** that holds the values - typically started by the
   [Blueprint Loader](https://www.nexusmods.com/thekillingantidote/mods/994) through a `TKA_BlueprintLoader` row in
   the mod's folder. AltUI finds it by its class, so there should be one instance of it.
2. **The interface `BPI_AltUIMod`** implemented on that actor - AltUI reads and writes the values through it.
3. **Two data tables** in the mod's own folder, `Content/Mod/<ModName>/`:
   `AltUI_Entries` (the list entries) and `AltUI_Fields` (their fields).

`<ModName>` is the pak's name without `.pak` - the same folder the game's mod loader uses for `TKA_Mod_Table`.

### The three editor assets

The two tables use AltUI's row structures, and the actor implements AltUI's interface. Copy these three files from
[`uassets/`](uassets/) into your Unreal project at exactly `Content/Mod/AltUI/`:

| File | What it is |
|---|---|
| `S_AltUIModEntry.uasset` | row structure of `AltUI_Entries` |
| `S_AltUIModField.uasset` | row structure of `AltUI_Fields` |
| `BPI_AltUIMod.uasset` | the interface your actor implements |

Your assets store these by their path, and in the game they are loaded from `AltUI.pak` at that path. **Do not ship
them in your pak**: a pak that brings its own copy replaces AltUI's for everyone who installs it. A table built on a
structure at any other path is not read at all.

## `AltUI_Entries`

One row per entry in the list. The row name is yours to choose; the fields refer to it.

| Column | Type | Meaning |
|---|---|---|
| `Caption` | Text | the entry's name in the list |
| `Actor` | Soft class reference (Actor) | the class of the actor that holds the values |
| `Order` | Integer | position in the list; lower first. Entries with the same order stay in the order they were found |

## `AltUI_Fields`

One row per field. The row name does not matter; what counts are the columns.

| Column | Type | Meaning |
|---|---|---|
| `Entry` | Name | row name in your `AltUI_Entries` this field belongs to |
| `Key` | Name | what your actor receives to tell the fields apart |
| `Type` | Name | `Header`, `Info`, `Toggle`, `Slider`, `Number`, `Choice`, `Color`, `Text` or `Button` |
| `Label` | Text | the text beside the field (a header's text, a button's caption) |
| `Min`, `Max` | Float | slider and number only: the range |
| `Step` | Float | slider: the value snaps to multiples of it from `Min`, 0 means continuous; number: what - and + change, 0 means 1 |
| `Options` | Array of Text | choice only: the options, shown one at a time with arrows |
| `Order` | Integer | position within the entry; lower first |

What each type shows and which value it carries:

| Type | Shows | Value |
|---|---|---|
| `Header` | a line of text above the fields that follow | none |
| `Info` | a line of text your mod supplies, updated live - a state, a counter | text, read only |
| `Toggle` | a checkbox | 0 or 1 |
| `Slider` | a slider with the value beside it | a number from `Min` to `Max` |
| `Number` | the value between − and + | a number from `Min` to `Max` |
| `Choice` | one option at a time, with arrows | the index of the option, starting at 0 |
| `Color` | a colour swatch; a click opens AltUI's colour palette | a colour |
| `Text` | a text field | text, reported when the player leaves the field or presses Enter |
| `Button` | a button carrying the label | always 1, when it is clicked |

A field AltUI cannot draw is left out without a message: an unknown `Type`, a `Choice` without options, a `Slider`
or `Number` whose `Min` is not below its `Max`, or an `Entry` that is not a row of your `AltUI_Entries`.

## `BPI_AltUIMod`

In your actor's Class Settings, add `BPI_AltUIMod` under *Implemented Interfaces*. It brings three pairs - one per kind
of value. Fill in the ones your fields use; the others can stay empty.

| Fields | Read | Changed |
|---|---|---|
| `Toggle`, `Slider`, `Number`, `Choice`, `Button` | `Get AltUI Value (Key) -> Value` (float) | `On AltUI Changed (Key, Value)` |
| `Color` | `Get AltUI Color (Key) -> Color` (linear colour) | `On AltUI Color Changed (Key, Color)` |
| `Text`, `Info` | `Get AltUI Text (Key) -> Text` (string) | `On AltUI Text Changed (Key, Text)` |

* The **Get** functions return the current value of the field with this key. AltUI calls them for every field while
  its entry is shown, so keep them cheap: return a variable, do not compute anything heavy. For headers and buttons
  nothing is read. A text field the player is typing in is not overwritten.
* The **On … Changed** events tell you the player changed a field: apply the value. A button arrives in
  `On AltUI Changed` with the value 1; the key tells which button. A colour arrives while the player is still picking
  it in the palette, so your mod can show it live.

Because AltUI asks for the values instead of remembering them, your actor stays the only place they live. Changing
one from somewhere else - a key of your own, another UI - needs nothing extra; the panel picks it up.

## Keeping the values

AltUI does not save your values; your mod does, the same way it would without AltUI. A `SaveGame` of your own is
enough: load it in `BeginPlay`, save it in `On AltUI Changed`. The example below does exactly that.

## An example to start from

[`examples/AltUIMod_Example/`](examples/AltUIMod_Example/) is a complete mod: a lamp in front of Jodi with one field
of every type, started by the Blueprint Loader, keeping its values in a save of its own. Install the pak to see it in
the Mods tab; its `editor/` folder holds the uncooked assets to copy and rename.
