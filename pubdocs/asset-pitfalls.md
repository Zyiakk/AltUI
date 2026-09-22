# Asset pitfalls

Some asset mistakes do not show up in the editor, do not show up in your own test, and then crash the game on someone else's machine every twenty minutes. This page collects the ones worth knowing about, each with what the engine actually does and what to change on export.

## Cloth physics bones

**The symptom.** The game dies with a fatal error in `NvCloth` while clothes are being put on. It is sporadic: the same garment works ten times and takes the game down the eleventh. It gets more likely the more cloth garments are created in the same frame – a full outfit change, a wardrobe preset, a mod that dresses the character in one go.

**What the engine does.** Before it cooks the cloth simulation for a garment, Unreal 4.27 skins the physics mesh into the current pose (`FClothingSimulationNv::CreateActor` → `SkinPhysicsMesh`). The bone matrices for that come from `UpdateRefToLocalMatrices`, which fills the entries for the bones the current LOD actually renders and leaves the rest of the array uninitialised.

Now suppose the cloth physics mesh is weighted to a bone that the *rendered* mesh of that LOD does not use – the bone is in the clothing asset's `UsedBoneNames` but not in the LOD's `ActiveBoneIndices`. Those vertices get skinned with whatever was in that memory: usually a leftover matrix from an earlier operation, which is why it mostly works; sometimes nonsense; sometimes NaN.

A single NaN vertex is enough. The cloth cooker's tether stage walks the mesh with comparisons that a fast-math build resolves the wrong way for NaN, so the NaN spreads across the whole island and the walk never terminates. The game freezes for half a minute and dies when the allocation fails.

**What to change.** On export, make sure that every bone the cloth physics mesh is weighted to also carries weight in the rendered mesh of the same LOD. Pruning influences below 1 % on the physics mesh removes this kind of case: in the garments examined here the offending weight was 1–3 % on a bone left over from the body the garment was fitted on.

Do not try to fix it by setting the weight to zero. The engine multiplies weight by matrix, and 0 × NaN is still NaN.

## Bone names the skeleton does not have

The same crash, with a different cause: the cloth physics mesh names a bone that does not exist in the skeleton of that mesh at all. A common case is a physics mesh that refers to `root` while the mesh's own root bone is called something else – the garment was authored on a different skeleton and the name was never fixed up.

The lookup fails, the bone is treated as absent, and the vertices land in the same uninitialised-matrix situation as above. Check the physics mesh's bone list against the skeleton, not against the skeleton you authored on.

## How to check before you ship

Before exporting a garment with cloth:

1. List the bones the cloth physics mesh is weighted to.
2. List the bones the rendered mesh uses in LOD 0.
3. Every bone in the first list must appear in the second, and must exist in the skeleton.

If a bone in the first list is there only with a very small weight, remove the influence rather than keeping it: it contributes nothing visible and is exactly the case that crashes.

A garment that passes this check is not guaranteed to be free of every cloth problem, but it will not hit this one. For a sense of how often it occurs: in one collection of a few hundred installed mods, three garments had it, and correcting those three ended the crashes in testing.
