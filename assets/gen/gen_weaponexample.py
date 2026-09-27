"""Generates assets/85_weaponexample.json and assets/tex/example_skin.png: WeaponAltUI_Example, a skin mod built exactly
the way uassets/README.md describes - one generated checker texture, one Mod_WeaponSkin row, one TKA_Mod_Table row.
The weapon is addressed by its ItemTable row name, so no asset of the game is needed either.

Built by scripts/weaponexample.sh, which keeps the whole thing out of the AltUI chain: own manifest, own cook
directory, own pak.
"""
import os, sys; sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
from PIL import Image, ImageDraw
from bpdsl import datatable, write
import weapon_skins as ws

MOD = "/Game/Mod/WeaponAltUI_Example"
TEX = MOD + "/T_ExampleSkin"
ROW = "WeaponAltUI_Example_Checker"                  # the mod name as a prefix: row names are global keys in AltUI
WEAPON = "UMP45"
# a weapon texture, not a UI icon: compressed like the game's own, and a flat pattern needs no mip chain
TEX_PROPS = {"CompressionSettings": "TC_Default", "SRGB": True, "MipGenSettings": "TMGS_NoMipmaps", "NeverStream": True}


def checker(path, size=512, cell=64):
    """Two colours in a checker with a diagonal bar - unmistakably artificial, so nobody takes it for a real skin."""
    im = Image.new("RGBA", (size, size), (40, 40, 48, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, size, cell):
        for x in range(0, size, cell):
            if (x // cell + y // cell) % 2 == 0:
                d.rectangle((x, y, x + cell - 1, y + cell - 1), fill=(216, 88, 32, 255))
    d.line((0, size - 1, size - 1, 0), fill=(255, 255, 255, 255), width=max(2, cell // 4))
    im.save(path)


def build(assets_dir):
    """Writes the PNG under <assets_dir>/tex and returns the asset list (file relative to assets_dir)."""
    os.makedirs(os.path.join(assets_dir, "tex"), exist_ok=True)
    checker(os.path.join(assets_dir, "tex", "example_skin.png"))
    tex_ref = TEX + "." + TEX.rsplit("/", 1)[1]
    return [
        {"type": "texture", "path": TEX, "file": "tex/example_skin.png", "props": TEX_PROPS},
        datatable(MOD + "/" + ws.TABLE_NAME, ws.STRUCT_PATH,
                  rows={ROW: {"Weapon": WEAPON, "Caption": "Example checker", "MainTex": tex_ref}}),
        datatable(MOD + "/TKA_Mod_Table", "/Game/Project/Tables/DLC_Struct",
                  rows={MOD.rsplit("/", 1)[1]: {"Caption": "AltUI weapon example",
                                                "Desc": "A checker skin for the UMP45, built the way the guide describes",
                                                "Version": 1.0, "Tables": []}}),
    ]


if __name__ == "__main__":
    A = os.path.join(os.path.dirname(__file__), "..")
    write(os.path.join(A, "85_weaponexample.json"), build(A))
