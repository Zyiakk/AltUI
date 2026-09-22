# Paks and assets without the editor

A mod for this game is a pak, and inside a pak are cooked assets. You do not need Unreal to look inside one, and for a surprising number of jobs you do not need it to write one either: a data table, a changed asset reference, a whole mod pak built around a mesh someone else made. This page describes what a mod pak looks like, how to read one, what is in a `.uasset`, and how to build and change assets from Python.

Every script named here is in `scripts/`, plain Python 3 without dependencies. They are the reference implementation of everything below – when a description here is not enough, read the file.

## What a mod pak is

A pak is an archive with an index and a **mount point**: the path prefix every entry inside is relative to. It is written as a path leading back out of the folder the game mounts paks from, which is why these all start with `../../../`. The mount point is what decides the nature of the pak:

| Mount point | What the pak is |
|---|---|
| `../../../TheKillingAntidote/Content/Mod/<ModName>/` | a mod; the game's loader lists it and reads its tables |
| `../../../TheKillingAntidote/Content/Project/…` | a replacement for an asset the game ships |

Assets come in pairs, `<Asset>.uasset` next to `<Asset>.uexp`, and meshes and textures may add `<Asset>.ubulk`. The pair always belongs together, and the `.ubulk` belongs to it when there is one; a pak carrying only part of a set is broken.

Mod paks for this game exist in versions 3 to 11. Old ones are usually uncompressed or zlib, version 11 also uses Oodle (Kraken). Mod paks are not encrypted.

## Reading one

`scripts/pakio.py` opens any of them behind one interface:

```python
import sys; sys.path.insert(0, "scripts")
from pakio import open_pak

pk = open_pak("Body_Curvy.pak")
for key in sorted(pk.files):
    print(key)                       # /Female.uasset, /Female.uexp, /TKA_Mod_Table.uasset, …
data = pk.read("/Female.uasset")     # decompressed bytes
```

`open_pak` returns the version 11 reader when it can and the old-format reader otherwise; both have `files` and `read()`. The keys are relative to the mount point, so they tell you the layout inside the mod folder, not the path in the game.

From the command line, `scripts/pak11_extract.py` lists, inspects and extracts:

```
python3 scripts/pak11_extract.py Body_Curvy.pak list
python3 scripts/pak11_extract.py Body_Curvy.pak info "Female"
python3 scripts/pak11_extract.py Body_Curvy.pak /tmp/out "Female"
```

`info` prints the compression method, the stored and uncompressed size and the number of blocks per entry – the quickest way to see whether a pak is zlib, Oodle or plain. The third form writes every matching entry into a folder.

Oodle is handled by `scripts/oodle_kraken.py`, a pure-Python port of [ooz](https://github.com/powzix/ooz) (GPL-3). It needs no library and is slow enough that you notice it on a big mesh but fast enough to be practical. `scripts/oodle_native.py` uses a compiled ooz through ctypes when `tools/fetch_ooz.sh` has built it, and the readers pick it up automatically.

## What is inside a `.uasset`

A cooked package has a summary, a **name table**, an **import table** (everything the package refers to elsewhere), an **export table** (the objects it defines), and – in the `.uexp` – the export data itself.

Two things surprise everyone reading this format for the first time:

* **Names are pairs.** A name is stored as an index into the name table plus a number, and that number encodes the numeric suffix: 0 means no suffix at all, any other value means the suffix is the number minus one. So `Breasts_2` is either the entry `Breasts_2` with number 0, or the entry `Breasts` with number 3, depending on how it was made – and in the second case the string `Breasts_2` appears nowhere in the file. Searching the raw bytes for a name with a suffix often finds nothing.
* **Properties are tagged.** Each property carries its name, type and size, and the engine reads them by name. This is what makes assets from different builds compatible, and it is why the *internal* name matters: in a cooked user-defined struct a member is called `Caption_2_CF40F849410064585CC285AFBAD051F2`, not `Caption`. A row you write has to use that internal name.

`scripts/uasset_props.py` decodes it, data table rows included:

```
python3 scripts/uasset_props.py TKA_Mod_Table.uasset
```

Use it as a library with `read_summary(path)` and `dump(path)`; `scripts/uasset_funcs.py` does the same for the functions of a blueprint class.

## Building a table from scratch

`scripts/uasset_datatable.py` writes cooked data tables from Python values – no editor involved. The generic parts are `new_datatable()`, the `*_prop` builders (`text_prop`, `bool_prop`, `float_prop`, `name_prop`, `vector_prop`, `name_array_prop`, `object_prop`), `end_props()` and `finish_table()`. On top of them sit two finished recipes. The mod table every mod needs:

```python
import sys; sys.path.insert(0, "scripts")
from uasset_datatable import make_mod_table

ua, ux = make_mod_table("/Game/Mod/Body_Curvy", "Curvy body", "Body mod", []).write()
open("TKA_Mod_Table.uasset", "wb").write(ua)
open("TKA_Mod_Table.uexp", "wb").write(ux)
```

`write()` returns the two files as bytes. The arguments are the mod's package path, the caption the game shows, the description, and the list of mod tables the pak brings (see [how the game finds mods](mods-and-tables.md)); an optional fifth is the version number.

Writing the pak around it is the same kind of work; `scripts/bodypak.py` has the pieces as `write_pak(out_path, mount, comps, entries, seed)` and `plain_entry(data)`, and uses them to produce a complete mod pak. Reading that file top to bottom is the fastest way to see a full build.

## Changing an existing asset

`scripts/uasset_pkg.py` reads a cooked package into `Package`, `Import` and `Export` objects and writes it back byte for byte if you change nothing. That property – lossless round-trip – is what makes it useful: you can rewrite the import table of a mesh, point a reference somewhere else, rename a package, and leave the export data untouched.

This is how a body replacer becomes a normal mod: the mesh keeps its bytes, but its imports are rewritten so it lives under `/Game/Mod/Body_<Name>/` instead of the game's own path. `scripts/bodypak.py` does exactly that, and it also shows the harder case – inserting one property tag into an export and re-serialising the rest unchanged.

Prefer this over patching bytes by hand. Sizes, offsets and the dependency lists in the export header all have to stay consistent, and getting one of them subtly wrong produces a package that may still load – until something reads the part you moved.

## Where it goes wrong

* **The internal name.** A row written with `Caption` instead of `Caption_2_CF40F849…` loads as an empty row. Get the internal names from a table that already works, with `uasset_props.py`.
* **Preload dependencies.** A cooked export lists what must be created and serialised before it. `finish_table()` fills those lists; if you build a package yourself and leave them empty, the asset may load in the wrong order and take the game down with it.
* **The mount point.** Right files, wrong mount point, and the game sees nothing. The folder under `Content/Mod/` has to match the pak's name.
* **Oodle without a decoder.** An Oodle-compressed pak read with a zlib-only tool looks corrupt. Check with `info` first.
* **The `.uexp` left behind.** Changing a `.uasset` without writing the matching `.uexp` produces a package whose offsets no longer line up.
