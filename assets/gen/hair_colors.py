"""Natural hair colour presets for the Coiffure page (W_Swatch row under the "Natural hair colours" link).
Values are sRGB 0..255 converted to linear – the game's hair material takes a LinearColor. Tune the sRGB triples in game
(docs/checklists/ui-test-20.md); nothing else needs to change."""


def lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(r, g, b):
    return (round(lin(r), 5), round(lin(g), 5), round(lin(b), 5))


# (key, linear RGB, (EN, DE, ZH, RU, ES))
COLORS = [
    ("Black", rgb(12, 10, 10), ("Black", "Schwarz", "黑色", "Чёрный", "Negro")),
    ("BlackBrown", rgb(32, 22, 18), ("Black-brown", "Schwarzbraun", "黑棕色", "Чёрно-каштановый", "Castaño oscuro")),
    ("DarkBrown", rgb(58, 38, 26), ("Dark brown", "Dunkelbraun", "深棕色", "Тёмно-каштановый", "Marrón oscuro")),
    ("Chestnut", rgb(92, 54, 32), ("Chestnut", "Kastanie", "栗色", "Каштановый", "Castaño")),
    ("MediumBrown", rgb(120, 78, 48), ("Medium brown", "Mittelbraun", "中棕色", "Русый", "Marrón medio")),
    ("LightBrown", rgb(160, 112, 70), ("Light brown", "Hellbraun", "浅棕色", "Светло-русый", "Marrón claro")),
    ("DarkBlonde", rgb(176, 138, 88), ("Dark blonde", "Dunkelblond", "深金色", "Тёмно-русый", "Rubio oscuro")),
    ("Honey", rgb(205, 165, 100), ("Honey blonde", "Honigblond", "蜂蜜金色", "Медовый", "Rubio miel")),
    ("LightBlonde", rgb(228, 200, 140), ("Light blonde", "Hellblond", "浅金色", "Светлый блонд", "Rubio claro")),
    ("Platinum", rgb(240, 230, 205), ("Platinum blonde", "Platinblond", "白金色", "Платиновый", "Rubio platino")),
    ("Copper", rgb(170, 78, 36), ("Copper", "Kupfer", "铜红色", "Медный", "Cobre")),
    ("Auburn", rgb(120, 50, 32), ("Auburn", "Rotbraun", "赤褐色", "Тёмно-рыжий", "Caoba")),
    ("StrawberryBlonde", rgb(215, 150, 105), ("Strawberry blonde", "Erdbeerblond", "草莓金色", "Клубничный блонд", "Rubio fresa")),
    ("Silver", rgb(190, 190, 195), ("Silver grey", "Silbergrau", "银灰色", "Серебристый", "Gris plateado")),
]


def string_rows():
    return {"Hair_" + k: names for k, _, names in COLORS}
