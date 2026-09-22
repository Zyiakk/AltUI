# Generating assets instead of clicking them

Every asset in AltUI's paks is generated. There is no blueprint anyone opened in the editor and wired by hand, no widget anyone laid out by dragging: Python writes a description, a commandlet builds the assets in the modding kit from it, and the build cooks and packs them. The blueprints are deleted and rebuilt from scratch on every run.

This is unusual enough to be worth explaining, because for a mod above a certain size it solves problems that are otherwise unsolvable – and it costs things that are worth knowing before you copy the approach.

## Why

**Diffs.** A blueprint is a binary asset. Change one node and version control shows you "this file changed", which is useless when you want to know what you did last week, or which change broke something. A generated blueprint has a readable source: the change shows up as a few lines of Python or JSON, in a diff you can read and review.

**Reproducibility.** The same source produces the same assets on any machine. Nothing depends on which nodes someone dragged where, and a rebuild after an engine or kit update is a build, not an afternoon of clicking.

**Scale.** A panel with a dozen tabs is thousands of nodes. Hand-wiring that in the editor is possible; maintaining it – renaming a variable used in eighty places, changing a function's signature, applying the same fix to twelve similar widgets – is not. In a generator those are one edit and a rebuild.

**Tests.** Because the description is data, it can be checked before anything is built: that every graph node is reachable, that every variable used exists, that no two nodes claim the same identifier. Those tests run in well under a second, without an editor.

## The chain

```
assets/gen/*.py     generators: readable Python, one file per area
      │  run them
      ▼
assets/*.json       a description per asset: structs, blueprints, widgets, tables
      │  scripts/bpgen.sh  (an editor commandlet, one run)
      ▼
kit project         the assets, created and compiled in the modding kit
      │  scripts/cook.sh
      ▼
cooked assets
      │  scripts/pak.sh
      ▼
the paks
```

`build.sh` runs the whole chain. The commandlet lives in `bpgen/`, a plugin for the kit project; it reads `assets/manifest.txt`, which lists the JSON files in the order they have to be built, and creates each asset described there.

The asset types it can build are `struct`, `enum`, `datatable`, `texture`, `blueprint` (variables, functions, event graph, and widget trees for UMG assets) and `animblueprint` (with `ModifyBone` nodes bound to variables).

Note what `scripts/bpgen.sh` does first: it deletes the generated assets in the kit before the run. Generated assets are disposable. If you find yourself opening one in the editor to fix something, the fix belongs in the generator.

## Stable identities

One detail that is easy to miss and expensive to learn the hard way: in a user-defined struct, each member has an internal name of the form `<Name>_<index>_<GUID>`, and the editor draws a fresh random GUID every time a member is created. Save-game data is matched against struct members by that internal name.

So a naively generated struct would get new member GUIDs on every build, and every rebuild would quietly empty the players' saved data. The generator therefore derives the GUID deterministically, as a hash of the struct path and the member name, so the same member keeps the same identity across rebuilds on any machine.

The same reasoning applies anywhere an identity crosses a build boundary – saved data, tables written by other tools, references from other mods. If you generate assets, make the identities a function of the source, never of the build.

## What it costs

* **An engine you can build a plugin for and run commandlets with.** The generator is a C++ editor plugin, so the engine has to be one you can compile against – this project uses a source build.
* **A build step.** Nothing is editable by clicking any more. In exchange, nothing is broken by clicking either.
* **The generator is now your codebase.** Writing a blueprint graph as data means writing a small compiler's worth of helper code first. That investment pays off somewhere around the point where hand-editing becomes unmaintainable – for a mod with two assets it is pure overhead.

## Trying it yourself

The plugin and the generators in this repository are a working example rather than a library. To see the chain run: copy `bpgen/` into your kit project's `Plugins/`, build the project once, copy `config.example.sh` to `config.sh` and set the paths in it, then run `./build.sh`. The README's *Building from source* section has the requirements in full.

If you only want the idea and not the machinery: start with the assets that hurt most to maintain by hand – tables and structs – and generate those. Writing cooked data tables needs no editor at all, see [paks and assets without the editor](paks-and-assets.md#building-a-table-from-scratch).
