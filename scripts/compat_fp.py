"""The game fingerprint AltUI checks when it starts (Game Fingerprint in BP_AltUIManager) and compat_check.py stores with a
known-good baseline: the row count of vanilla tables that no mod loader adds rows to. A content update of the game nearly always
changes one of them; installed mods do not - except old-style override paks that replace a whole table, which the player
confirms once. Not here: the tables the game's own mod loader merges mod rows into (TKA_GameInstance.Load DLC ->
MergeDLCTables: ClothesTable, HatsTable, HairstyleTable, AnimationTable, EyeTable, GunPaint, LevelTable, MakeupTable,
MakeupTypeTable, SkinTable) and ClothesGroup, which grows with clothing mods as well - with them in, every player with a
clothing mod got the warning (game test 2026-10-11: ClothesTable 4117 rows instead of 272, ClothesGroup 209 instead of 15)."""
FP_TABLES = ["/Game/Project/Clothes/ClothesTypeTable", "/Game/Project/Tables/ItemTable", "/Game/Project/Tables/GunEquipment"]


def fp_string(counts):
    """counts: table path -> row count (-1 = table missing). Same text as the Blueprint builds: Name=n;Name=n;..."""
    return ";".join("%s=%d" % (p.rsplit("/", 1)[-1], counts.get(p, -1)) for p in FP_TABLES)
