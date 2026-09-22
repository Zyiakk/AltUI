# Running your own code in the game

A mod pak is data. Meshes, textures, tables, blueprints – the loader reads the tables, the game shows the content, and nothing of yours ever *runs*. The game's mod system is generous with data and offers no place at all to put code. For a retexture that is fine. For anything that has to react while the player plays, you need a place where the game calls into code you wrote.

The game gives you one, almost by accident, and AltUI uses it: a class that is part of the game but practically empty, which a pak can replace with a version that does the same thing plus yours. This page describes that hook end to end – what it hooks, how it starts your actor, how it stays out of everyone else's way, and the one hard limit that comes with it.

## An empty class as the door

`/Game/Project/Classes/TKA_PlayerCameraManager` is a blueprint the game ships, deriving from the engine's `PlayerCameraManager`. It sets two values, `ViewPitchMin = -80` and `ViewPitchMax = 70`, and does nothing else. The player controller points at it through `PlayerCameraManagerClass`, and nothing else in the game refers to it.

That makes it an unusually cheap thing to take over. It is instantiated for every player, it exists from the moment a level starts, it derives from an engine class whose functions you can override – and because nothing else refers to it, replacing it cannot disturb any other system.

Replacing it means shipping your own version of that asset, built in the modding kit against the same path, with the same parent class. **Copy its default values.** A replacement that forgets `ViewPitchMin` and `ViewPitchMax` silently changes how far the player can look up and down – your mod would be changing the camera behaviour of a game you only wanted to attach to.

## The override pak

The replacement travels in its own pak, separate from the mod's content:

* content: exactly two files, `TKA_PlayerCameraManager.uasset` and `.uexp`
* mount point: `../../../TheKillingAntidote/Content/Project/Classes/`
* file name ends in `_P`, and the pak goes into `TheKillingAntidote/Content/Paks/~mods/`

The `_P` suffix and that folder are what get it mounted early and with priority over the game's own copy; see [two folders, and `_P`](mods-and-tables.md#two-folders-and-_p). `scripts/pak.sh` builds such a pak with `UnrealPak` and can serve as a template – the response file for it has one line per file, so two.

Keeping the hook in its own pak is worth the extra file. It changes rarely, it is the only part that replaces something, and a user who already has it does not have to replace it when the rest of the mod updates.

## Starting your actor

The hook itself does as little as possible: it waits until the world is ready, spawns one actor of your own, and then gets out of the way.

```
ReceiveBeginPlay
  └─ K2_SetTimer(self, "TryInit", 0.5 s, looping)

TryInit
  ├─ already spawned?  → done
  ├─ GetOwningPlayerController → K2_GetPawn → cast to the player character
  │     cast fails (main menu, still loading) → return, the timer tries again
  ├─ LoadClassAsset_Blocking("/Game/Mod/<YourMod>/BP_YourManager.BP_YourManager_C")
  │     not loadable (your mod pak is not installed) → stop the timer
  ├─ SpawnActor(class, transform, Owner = the controller)
  └─ mark as spawned, stop the timer
```

Two details in there are the difference between a hook that behaves and one that does not.

**It is a timer, not a tick.** Half a second is plenty for something that only has to happen once, and a looping timer costs nothing between firings. Doing this work every frame – or worse, loading a class every frame – is the usual way these hooks turn into a performance complaint.

**It stops itself, both ways.** On success it clears the timer, so after the actor exists the hook does nothing at all for the rest of the session. And if the class cannot be loaded, it clears the timer too: with only the hook pak installed and the mod pak missing, a blocking load every half second would run for as long as the game is open.

From there on, your actor is a normal actor: it has a tick if it wants one, it can spawn widgets, read tables, listen to input. Everything AltUI does – the panel, the wardrobe, the sliders – happens in that one actor and the assets it loads, all of them under `/Game/Mod/AltUI/`.

## Keeping it loose

The hook refers to your manager **by path**, through a blocking class load, not as a hard reference. That has consequences worth designing for:

* The hook pak does not depend on the mod pak. Installed alone, it is a camera manager that behaves exactly like the game's.
* The mod pak does not depend on the hook. Installed alone, nothing spawns it, and nothing breaks.
* The two can be versioned separately. If the hook does not change between releases, users keep the file they have.

Communication in the other direction works the same way: the manager sets variables on the camera manager, and the camera manager reads them. No casts to mod classes, no hard references in the asset that replaces a game asset. Keep that boundary thin and the hook can stay untouched for years.

## What the camera override does

The one thing AltUI's hook does beyond spawning is override `BlueprintUpdateCamera`, and it is worth describing because the vector maths in there is easy to misread from the outside.

While the panel is closed, the override returns `false` – "not handled" – on the first branch, and the engine computes the camera exactly as it always does. That is the state the game is in essentially all the time.

While the panel is open, it moves the camera so the character stands in the free area beside the panel instead of in the middle of the screen: it finds the active camera component of the view target, narrows the field of view by a factor, pulls the camera back along its view axis so the character keeps her size on screen, and offsets it sideways and vertically. The sideways offset is a closed loop rather than a formula – the character's world position is projected to screen space, compared against the target position, and the offset corrected by a fraction of the error each frame.

None of this touches the character: no bones, no meshes, no morphs. It changes where the camera is and how wide it sees, and returns the result.

## Doing it yourself

1. In the modding kit, create a blueprint at the same path and with the same parent class as the class you are taking over, and copy its default values.
2. Add your logic: a `BeginPlay` that starts a looping timer, and the timer function that loads and spawns your actor.
3. Put your actual mod – the actor, its widgets, its tables – in `/Game/Mod/<YourMod>/`, as an ordinary mod pak.
4. Cook, then build two paks: the mod pak from your mod folder, and the override pak from the one replaced asset. `scripts/pak.sh` shows both.
5. Test with each pak alone as well as with both. Neither should do harm on its own.

## Where it goes wrong

* **Only one mod can have it.** Two mods that replace `TKA_PlayerCameraManager` exclude each other, exactly like two replacers for the same mesh. There is no way around that from inside a pak, and it is the reason this technique does not scale to a modding scene. If you are building something that other mods should be able to join, spawn your actor from a hook that others can register with, rather than claiming the class yourself.
* **Blocking loads in a loop.** A timer that keeps trying to load a class that will never exist is a stutter every half second for the whole session. Stop after the first failure.
* **Spawning without an owner.** An actor spawned without the controller as owner loses the connection to the player it belongs to, which matters as soon as you want input or a widget on that player's screen.
* **Forgotten defaults.** Anything set on the class you replace has to be set on yours. Compare them property by property before you ship.
* **Doing the work in the hook.** Everything beyond "spawn one actor" belongs in your own assets, under your own path. The replaced class is the one piece of your mod that is in everyone else's way; keep it small enough that it never needs to change.
