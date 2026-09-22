# The hard parts, and how they were solved

Most of a mod is ordinary work. A few pieces are not, and those are usually the ones where the obvious approach turns out to be impossible and the way around is only obvious afterwards. This page collects the ones from this project that are worth knowing about, each as *what was needed → why the obvious way fails → what worked → what generalises*.

## Getting any code to run at all

A pak is data. Before anything else could be built, there had to be a point where the game calls into code from a mod – and the mod system provides none.

The way in is a class the game ships that is practically empty, replaced by a pak with a version that keeps its defaults and adds a timer which spawns one actor. [Running your own code in the game](running-your-own-code.md) describes it in full, including the limit that comes with it: only one mod can hold that class.

## Reading Oodle-compressed paks without shipping a library

The body-mod converter has to read paks compressed with Oodle. There is no Python implementation in the standard library, and the compressor is proprietary.

The first attempt took the obvious route: bundle a compiled decoder built from an open-source reimplementation, unpack it to a temporary folder at runtime, load it. It worked, and it was unusable – an unsigned binary, cross-compiled, extracted to a temp folder and loaded by a script is close enough to the shape of a dropper that Windows Defender's heuristics flagged the tool as a trojan. Users could not even download it.

The fix was to stop shipping native code: the Kraken decode path was ported to pure Python (`scripts/oodle_kraken.py`, from [ooz](https://github.com/powzix/ooz), GPL-3). The tool became a plain script again, with nothing in it to flag. It is slower than the native version, which matters not at all for a tool that converts one pak at a time, and the development repository still uses the compiled version through ctypes where speed helps and as the reference the port is tested against.

**What generalises:** if you hand tools to players, a bundled native component can cost you the download entirely, and no amount of speed makes up for a tool nobody can obtain.

## Making body shapes adjustable

This one was a chain of four problems, each revealed by solving the one before.

**Not every body keeps its shape in the mesh.** Most body mods do, but at least one widely used one ships a mesh close to the game's and gets its actual proportions from a post-process animation blueprint that scales bones. So "switch the body" is not just "swap the mesh" – swap it without the blueprint and you get the standard body back.

**The blueprint cannot be attached at runtime.** A skeletal mesh's post-process animation blueprint is read-only from blueprints in this engine version. What *is* callable is the instance of it on the mesh component – so the reference has to be in the asset before the game starts. That moved the job into the converter: it rewrites the mesh's reference to point at the mod's own animation blueprint, and then the mod can drive that blueprint's variables at runtime.

**Bone scales inherit.** Scale a thigh and everything below it – the twist bone, the calf, the foot – is scaled too, because the engine derives the children from their local transforms. Setting each group to the value you want produces something entirely different from what you asked for. The fix is to be explicit about which number means what: the table stores the *net* scale each group ends up with, and when applying, each node is set to the group's net value divided by its parent group's. The values in the data are then the values you can measure on the body, which is also what a modder authoring a table expects.

**Scaling moves the body off the floor.** Make the figure taller and the soles sink into it; make the feet bigger and the heels do. There is no physical fix, only compensation: two additional translations, one on the root and one on the feet, each derived from the factor, with two constants that were measured from the mesh rather than guessed – which is why the sliders do not look wrong in motion.

There is a fifth, smaller one in the same area worth recording: the game's own bust and waist sliders are the alpha of an additive animation node, and the engine clamps that alpha to 0…1. No amount of passing 1.5 into it does anything. If you want a range beyond the game's, you need your own mechanism – in this case a bone scale in the same direction as the game's morph, which starts where the game's slider stops.

**What generalises:** when a value in a table can mean either "what this node does" or "what the result is", pick the result and convert on the way in. Every consumer of the data then agrees about what it means.

## A crash in someone else's asset

The game dies while clothes are being put on. It happens without this mod installed and through the game's own wardrobe, so the trigger is elsewhere: garments whose cloth physics mesh is weighted to a bone the rendered mesh does not use, which the engine then turns into a crash. [Asset pitfalls](asset-pitfalls.md) has the mechanism and how to avoid it on export.

Two things about it belong here rather than there. First, there is no runtime fix: nothing a mod can reach exposes the data involved. What a mod *can* do is reduce the exposure, and this one does – dressing actions are put through a queue that puts one garment on every few frames instead of all of them in one, which shrinks the window in which the bug is dangerous. Second, an affected asset can be corrected in place without touching the original mod: the physics mesh's reference to the unusable bone is re-pointed at the nearest bone that is actually used, in a small override pak that sits beside the mod. Both are worth knowing as patterns – *mitigate what you cannot fix*, and *patch the asset, not the mod*.

## No files, no logging, in a shipped game

Blueprints in a packaged build cannot write files, and the usual debug output is compiled out. For a mod that has to remember the player's choices – and for a developer who has to find out what went wrong on someone else's machine – that looks like a wall.

Both halves go through the same door: save game objects. Everything the mod remembers lives in save games it defines itself, which also makes the data portable – a small Python tool reads and writes those files outside the game, so the player's own display names can be exported to JSON, edited in a text editor and imported again (`scripts/altui_names.py`).

Logging works the same way: a log line appended to a save game object, flushed as the game writes it. It is clumsy compared to a log file, but it survives a crash, it can be read from outside, and it is the only channel that exists in a shipped build.

**What generalises:** when the platform closes the obvious door, look for the one facility it *does* give you and see how far it stretches. A save game is a serialised object with a name, which is most of what a file is.
