# Modding notes

These are the techniques behind AltUI, written up so you can use them in your own mod for *The Killing Antidote*: what the game does, how to do it yourself, and where it goes wrong. Nothing here is specific to AltUI unless a page says so – most of it is about paks, assets and the tables the game reads.

Everything described here can be done with a text editor, Python 3 and the game's modding kit. The scripts named on these pages are in this repository; they are plain Python without dependencies, so you can read them as the reference implementation of whatever a page describes.

## The guides

**[Paks and assets without the editor](paks-and-assets.md)** – what a mod pak looks like, how to read one from Python, what is inside a `.uasset`, and how to build data tables or rewrite asset references without Unreal. Start here if you want to build tooling of your own.

**[How the game finds mods](mods-and-tables.md)** – the mod table every pak needs, the tables a mod can bring, the two folders paks live in, `_P` overrides, and why two replacers for the same asset can never coexist.

**[Running your own code in the game](running-your-own-code.md)** – how a mod gets logic running at all: replacing a practically empty game class with your own, spawning your actor from it, and keeping both paks independent of each other.

**[Making a mod that AltUI reads well](altui-integration.md)** – what AltUI takes from your tables, which field becomes which part of the panel, and what a body mod needs. Relevant if your mod ships clothes, hairstyles, skins, make-up or a body.

**[Asset pitfalls](asset-pitfalls.md)** – mistakes that pass every test in the editor and crash the game later. Right now: cloth physics meshes weighted to bones the rendered mesh does not use – one cause of the fatal error players run into while putting clothes on, and an easy one to avoid on export.

**[Generating assets instead of clicking them](generated-assets.md)** – how every blueprint, widget and table in AltUI is built from a description rather than wired by hand, what that buys, and what it costs.

**[How this project works](how-this-project-works.md)** – the repository layout, how a change goes from a design note to a release, and how the reasoning behind decisions is kept so it outlives the session it was made in.

**[The hard parts, and how they were solved](hard-problems.md)** – the pieces where the obvious approach turned out to be impossible: running code at all, reading Oodle without shipping a binary, adjustable body shapes, a crash in someone else's asset, and living without files or logging in a shipped build.

## Elsewhere

Two guides live outside this folder: [installing body mods](../BODY_MODS.md) for players, and [the editor assets](../uassets/README.md) for building a body mod for AltUI in the Unreal Editor.
