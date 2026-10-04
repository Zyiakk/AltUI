# Editor script (scripts/quickmenu/material.sh runs it through scripts/edtest.sh): the quick menu's sector material.
# /Game/Mod/AltUI/Mat/M_QuickSector - UI domain, translucent. One instance per sector (W_QuickWheel): Count sectors, this one
# is Index (0 centred at the top, clockwise); a ring from Inner to the edge (radius 1 = half the image), a gap of 2*Gap between
# neighbours, soft edges of width Soft; Color = fill (alpha = opacity). Cooked for Windows under Wine (D3D SM5 shaders).
import unreal
EAL, MEL = unreal.EditorAssetLibrary, unreal.MaterialEditingLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
PATH = "/Game/Mod/AltUI/Mat/M_QuickSector"

CODE = """float2 p = UV * 2 - 1;
float r = length(p);
float a = atan2(p.x, -p.y) / 6.2831853;
a = a < 0 ? a + 1 : a;
float n = max(Cnt, 1);
float s = frac(a + 0.5 / n) * n;   // sector 0 centred at the top
float inSec = abs(floor(s) - Idx) < 0.5 ? 1 : 0;
float edge = min(frac(s), 1 - frac(s)) / n * 6.2831853 * r;
float gap = n > 1.5 ? smoothstep(Gap, Gap + Soft, edge) : 1;
float ring = smoothstep(Inner, Inner + Soft, r) * (1 - smoothstep(1 - Soft, 1, r));
return inSec * gap * ring;"""


def main():
    if EAL.does_asset_exist(PATH): EAL.delete_asset(PATH)
    m = AT.create_asset(PATH.rsplit("/", 1)[1], PATH.rsplit("/", 1)[0], unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("material_domain", unreal.MaterialDomain.MD_UI)
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    tc = MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -900, -200)
    params = {}
    for i, (name, value) in enumerate((("Count", 1.0), ("Index", 0.0), ("Inner", 0.36), ("Gap", 0.008), ("Soft", 0.01))):
        p = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -900, i * 120)
        p.set_editor_property("parameter_name", name); p.set_editor_property("default_value", value); params[name] = p
    col = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -900, 700)
    col.set_editor_property("parameter_name", "Color"); col.set_editor_property("default_value", unreal.LinearColor(0.15, 0.15, 0.15, 0.85))
    cu = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, -500, 100)
    ins = []
    for n in ("UV", "Cnt", "Idx", "Inner", "Gap", "Soft"):
        ci = unreal.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    cu.set_editor_property("inputs", ins)
    cu.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    cu.set_editor_property("code", CODE)
    MEL.connect_material_expressions(tc, "", cu, "UV")
    for pin, name in (("Cnt", "Count"), ("Idx", "Index"), ("Inner", "Inner"), ("Gap", "Gap"), ("Soft", "Soft")):
        MEL.connect_material_expressions(params[name], "", cu, pin)
    op = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -250, 300)
    MEL.connect_material_expressions(cu, "", op, "A"); MEL.connect_material_expressions(col, "A", op, "B")
    MEL.connect_material_property(col, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.connect_material_property(op, "", unreal.MaterialProperty.MP_OPACITY)
    MEL.recompile_material(m); EAL.save_asset(PATH)
    unreal.log_warning("EDTEST PASS quick sector material saved")


try:
    main()
except Exception:
    import traceback; unreal.log_warning("EDTEST FAIL exception: " + traceback.format_exc().replace("\n", " | "))
