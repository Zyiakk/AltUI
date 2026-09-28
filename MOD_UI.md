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
| `Type` | Name | `Header`, `Info`, `Toggle`, `Slider`, `Number`, `Choice`, `Color`, `Text`, `Key` or `Button` |
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
| `Key` | the bound key's name on a button; a click waits for the next key, a right click clears it | a key of the keyboard, reported when the player presses one; Esc or a click cancels. An empty key means none |
| `Button` | a button carrying the label | always 1, when it is clicked |

A field AltUI cannot draw is left out without a message: an unknown `Type`, a `Choice` without options, a `Slider`
or `Number` whose `Min` is not below its `Max`, or an `Entry` that is not a row of your `AltUI_Entries`.

## `BPI_AltUIMod`

In your actor's Class Settings, add `BPI_AltUIMod` under *Implemented Interfaces*. It brings four pairs - one per kind
of value. Fill in the ones your fields use; the others can stay empty.

| Fields | Read | Changed |
|---|---|---|
| `Toggle`, `Slider`, `Number`, `Choice`, `Button` | `Get AltUI Value (Key) -> Value` (float) | `On AltUI Changed (Key, Value)` |
| `Color` | `Get AltUI Color (Key) -> Color` (linear colour) | `On AltUI Color Changed (Key, Color)` |
| `Text`, `Info` | `Get AltUI Text (Key) -> Text` (string) | `On AltUI Text Changed (Key, Text)` |
| `Key` | `Get AltUI Key (Key) -> Pressed` (Key) | `On AltUI Key Changed (Key, Pressed)` |

* The **Get** functions return the current value of the field with this key. AltUI calls them for every field while
  its entry is shown, so keep them cheap: return a variable, do not compute anything heavy. For headers and buttons
  nothing is read. A text field the player is typing in is not overwritten.
* The **On … Changed** events tell you the player changed a field: apply the value. A button arrives in
  `On AltUI Changed` with the value 1; the key tells which button. A colour arrives while the player is still picking
  it in the palette, so your mod can show it live.
* A `Key` field takes any key of the keyboard, Shift, Ctrl and Alt on their own included; a mouse click cancels the wait.
  Test for an empty key with `Is Valid Key`.

The `Key` pair came later than the other three. A mod built with an older copy of `BPI_AltUIMod.uasset` keeps working
as it is; to use a `Key` field, replace your copy with the one in [`uassets/`](uassets/).

Because AltUI asks for the values instead of remembering them, your actor stays the only place they live. Changing
one from somewhere else - a key of your own, another UI - needs nothing extra; the panel picks it up.

### The Get functions are yours to fill, not to call

`Get AltUI Value`, `Get AltUI Color`, `Get AltUI Text` and `Get AltUI Key` are asked by AltUI, not by your mod. Open them under
*Interfaces* in your actor's *My Blueprint* panel and make each return your variable for the key it is given. Your
own graphs have no reason to call them: calling one on `self` only runs your own function again and hands back what
your variable already holds; wiring anything into `Target` changes nothing about that. When your mod needs a field's
value, read the variable you keep it in.

### Reacting to a field

Fields reach your actor one by one, each in its own call of an `On … Changed` event. The usual pattern:

1. In `On AltUI Changed`, add a **Switch on Name** on `Key`, with one case per key of your toggles, sliders, numbers,
   choices and buttons.
2. For a toggle, slider, number or choice: set its variable from `Value`, then apply it - switch the light, move the
   actor, whatever the field is for. (A toggle's 0 or 1 becomes a boolean with `Value > 0.5`, a choice's index an
   integer with `Round`.)
3. For a button: ignore `Value` and do what the button stands for. The other fields' values are already in their
   variables, because each change arrived in its own call before the click.
4. Do the same for colours in `On AltUI Color Changed`, for text in `On AltUI Text Changed` and for keys in
   `On AltUI Key Changed`.

Every change arrives at once, so most mods need no "Apply" button: the field applies itself. A button suits actions
that are not a value - reset, spawn, teleport, reload - or a step you want to happen only when the player asks for it.

## Keeping the values

AltUI does not save your values; your mod does, the same way it would without AltUI. A `SaveGame` of your own is
enough: load it in `BeginPlay`, save it in `On AltUI Changed`. The example below does exactly that.

## An example to start from

[`examples/AltUIMod_Example/`](examples/AltUIMod_Example/) is a complete mod: a lamp in front of Jodi with one field
of every type, started by the Blueprint Loader, keeping its values in a save of its own. Install the pak to see it in
the Mods tab; its `editor/` folder holds the uncooked assets. Its "Back to the defaults" button is the button pattern
above, wired up, and its key field switches the lamp in the game - the pattern of the next section's key question.

The assets refer to each other by their path, `/Game/Mod/AltUIMod_Example/`. Copy them into your project at exactly
`Content/Mod/AltUIMod_Example/` - in any other folder the references break, the blueprint shows broken nodes and the
project does not cook - and rename them afterwards in the editor's Content Browser, which rewrites the references.
The example's README lists the steps.

## Questions that come up

**How do I trigger something with a button?** In `On AltUI Changed`: the button's key arrives with the value 1.
Switch on the key and run what the button does - see [Reacting to a field](#reacting-to-a-field).

**What does "always 1, when it is clicked" mean?** A button has no state to show, so nothing is read for it. Each
click is one call of `On AltUI Changed` with its key and the value 1; the value tells you nothing, the key everything.

**Do I plug something into `Target` on `Get AltUI Value`?** No - you do not call it at all. AltUI calls it on your
actor to learn what to show; you only fill in what it returns. In your own graph, read your variable instead. See
[The Get functions are yours to fill, not to call](#the-get-functions-are-yours-to-fill-not-to-call).

**Can a button's caption (or any field's label) change while the game runs?** No. Labels come from `AltUI_Fields`
and stay as they are. What your mod supplies live is values, and for text the `Info` field: put one next to the
button to show what the button would change or what it did last. If the button would only step through a list of
options, a `Choice` field does that already - its arrows cycle, the current option is shown, and each step arrives at
once.

**Can the player pick a key for my mod - "press the key you want"?** Yes: a `Key` field. The player clicks it, presses
the key, and `On AltUI Key Changed` brings it; store it and save it like any other value. To react to the key in the
game, your actor needs input of its own:

* In `BeginPlay`, call `Enable Input` with the player controller (`Get Player Controller`, index 0).
* Add an `Any Key` event; compare its key with the stored one (`Equal (Key)`, and `Is Valid Key` so an empty key does
  nothing) and do what the key is for.
* In the `Any Key` node's details, untick **Consume Input**. An actor with input enabled stands before the player's
  controls, and an `Any Key` that consumes takes every key away from the game.

While the panel is open it keeps the keyboard to itself, so the key works once the panel is closed. The example's
"Key for on/off" field is exactly this.

**I copied the example's assets into my project and the blueprint is full of broken nodes.** They were copied into a
folder with another name. Put them at `Content/Mod/AltUIMod_Example/` first, open the editor, then rename in the
Content Browser.

**My tables are not read / my entry does not show.** Check that the row structures sit at exactly
`Content/Mod/AltUI/` in your project, that the tables are named `AltUI_Entries` and `AltUI_Fields` and lie in
`Content/Mod/<ModName>/` where `<ModName>` is your pak's name without `.pak`, and that your pak does not ship its own
copy of AltUI's three assets.

**My entry is shown, but greyed out.** The actor of the entry's `Actor` class is not in the level - check that the
Blueprint Loader is installed and your loader row names that class.
