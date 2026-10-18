"""Mutation look (spec docs/specs/2026-10-18-mutation-look-design.md): the story's mutated skin/eyes worn in parts.

Colour: the skin row's diffuse drawn opaque into a render target of the figure's own, Mutations_D over it at alpha = Color;
that target is MainTex (the make-up layer still lies above it in ShaderSkin). Glow: EmissiveTex Mutations_E and
EmissiveColor = (GLOW_RED * Glow, 0, 0) as in Skin_Jodi_Mutanted. Veins: NormalTex Mutations_N. Eyes: Eyes_Jodi_Mutanted.
Mutations_D/N/E are 4096^2 and share the UV of Jodi's skin (docs/notes/2026-10-18-mutation-look.md)."""
M = "/Game/Mod/AltUI"
S_MUT = M + "/S_Mutation"
S_ORIG = M + "/S_MutOrig"   # a skin instance's own MainTex / NormalTex before AltUI (Mutate Mesh puts them back)
BODY = "/Game/Project/Character/Jodi/Body"
# object paths, loaded at run time (Load Mutation Assets): the mod kit does not have them, so no hard reference
MUT_D, MUT_N, MUT_E = (BODY + "/Skin/%s.%s" % (n, n) for n in ("Mutations_D", "Mutations_N", "Mutations_E"))
MUT_EYES = BODY + "/Eyes_Jodi_Mutanted.Eyes_Jodi_Mutanted"
ASSETS = [("MutTexD", MUT_D, "texture"), ("MutTexN", MUT_N, "texture"), ("MutTexE", MUT_E, "texture"), ("MutEyeMat", MUT_EYES, "material"),
          ("MutStoryMat", BODY + "/Skin_Jodi_Mutanted.Skin_Jodi_Mutanted", "material")]   # manager variable, path, kind
GLOW_RED = 0.5          # Skin_Jodi_Mutanted: EmissiveColor (0.5, 0, 0)
EYE_GLOW = 2.0          # Eyes_Jodi_Mutanted: EmissiveColor (2, 0, 0); an own iris colour glows at this factor
MUT_RT_SIZE = 4096      # Jodi's skin target: the size of Mutations_D and of her skin (no detail lost)
MUT_COPY_RT_SIZE = 2048 # ragdoll copies / followers (each has a target of its own, 16 MB instead of 64)
CAT = "Mutation"        # the appearance page's list entry (LookCat)
# rows of the page: (key, caption string, slider?) - keys are W_FaceRow keys, all start with PREFIX (Face Row Changed dispatches on that)
ROWS = [("MutColor", "Mut_Color", True), ("MutGlow", "Mut_Glow", True), ("MutVeins", "Mut_Veins", False), ("MutEyes", "Mut_Eyes", False),
        ("MutStory", "Mut_Story", False)]   # Story: slot 0 = the story's skin variant (true glow; no make-up, no scars)
PREFIX = "Mut"
STORY_SKIN = BODY + "/Skin_Jodi_Mutanted.Skin_Jodi_Mutanted"   # the story's own skin variant (UseEmissiveTex, no make-up / scars)
GLOW_MAT = "/Game/Mod/AltUI/Mat/M_MutGlow"   # AltUI's glow layer material (scripts/quickmenu/material.py, cooked for Windows)
