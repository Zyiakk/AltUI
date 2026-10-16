# Editor script (scripts/quickmenu/material.sh runs it through scripts/edtest.sh): the quick menu's sector material.
# /Game/Mod/AltUI/Mat/M_QuickSector - UI domain, translucent. One instance per sector (W_QuickWheel): Count sectors, this one
# is Index (0 centred at the top, clockwise); a ring from Inner to the edge (radius 1 = half the image), a gap of 2*Gap between
# neighbours, soft edges of width Soft; Color = fill (alpha = opacity). Cooked for Windows under Wine (D3D SM5 shaders).
# Also /Game/Mod/AltUI/Mat/M_ImageBox (button image, Options > Theme): the picture Tex over the whole element, corners rounded
# like T_RoundBox (computed in the shader; Radius 0 = none, the background), filters Invert / Sepia / Hue, tinted by the vertex
# colour (= BrushColor / ColorAndOpacity: hover, opacity).
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
    image_box()
    unreal.log_warning("EDTEST PASS quick sector material saved")


IMG = "/Game/Mod/AltUI/Mat/M_ImageBox"
ROUND = "/Game/Mod/AltUI/T_RoundBox"


ROUND_CODE = """if (R <= 0) return 1;   // background (also tiled, UV beyond 1): no corners
float2 fw = max(float2(abs(ddx(UV.x)) + abs(ddy(UV.x)), abs(ddx(UV.y)) + abs(ddy(UV.y))), 1e-5);
float2 size = 1.0 / fw;
float2 q = abs(UV * size - size * 0.5) - (size * 0.5 - R);
float d = length(max(q, 0)) + min(max(q.x, q.y), 0) - R;
return saturate(0.5 - d);"""


FILTER_CODE = """float3 c = pow(saturate(C), 1.0 / 2.2);   // in display (gamma) space, like an image editor: inverting linear values made dark pictures white
c = lerp(c, 1 - c, saturate(Inv));
float3 sp = float3(dot(c, float3(0.393, 0.769, 0.189)), dot(c, float3(0.349, 0.686, 0.168)), dot(c, float3(0.272, 0.534, 0.131)));
c = lerp(c, sp, saturate(Sep));
float a = Hue * 6.2831853; float co = cos(a); float si = sin(a);
float3x3 m = float3x3(0.213 + 0.787 * co - 0.213 * si, 0.715 - 0.715 * co - 0.715 * si, 0.072 - 0.072 * co + 0.928 * si,
                      0.213 - 0.213 * co + 0.143 * si, 0.715 + 0.285 * co + 0.140 * si, 0.072 - 0.072 * co - 0.283 * si,
                      0.213 - 0.213 * co - 0.787 * si, 0.715 - 0.715 * co + 0.715 * si, 0.072 + 0.928 * co + 0.072 * si);
return pow(saturate(mul(m, c)), 2.2);"""


def image_box():
    """The picture over the element (brush drawn as Image: TexCoord 0 runs 0-1 across it), corners rounded in the shader - the
    element's size in pixels from the UV derivatives, radius R pixels (Manager: T_RoundBox's 10 units x viewport scale). No engine
    material function (GetUserInterfaceUV is not in the game's pak)."""
    if EAL.does_asset_exist(IMG): EAL.delete_asset(IMG)
    m = AT.create_asset(IMG.rsplit("/", 1)[1], IMG.rsplit("/", 1)[0], unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("material_domain", unreal.MaterialDomain.MD_UI)
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    rb = unreal.load_asset(ROUND)
    if rb is None: raise RuntimeError("T_RoundBox missing in the kit")
    tc = MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -1100, 0)
    tex = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -700, -200)
    tex.set_editor_property("parameter_name", "Tex"); tex.set_editor_property("texture", rb)
    tex.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    MEL.connect_material_expressions(tc, "", tex, "UVs")
    rad = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -1100, 300)
    rad.set_editor_property("parameter_name", "Radius"); rad.set_editor_property("default_value", 10.0)
    cu = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, -700, 200)
    ins = []
    for n in ("UV", "R"):
        ci = unreal.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    cu.set_editor_property("inputs", ins); cu.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1); cu.set_editor_property("code", ROUND_CODE)
    MEL.connect_material_expressions(tc, "", cu, "UV"); MEL.connect_material_expressions(rad, "", cu, "R")
    # filters (Options > Theme, per picture): invert, sepia, hue rotation (like CSS invert / sepia / hue-rotate, in this order)
    fp = {}
    for i, n in enumerate(("Hue", "Invert", "Sepia")):
        q = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -1100, -700 + i * 120)
        q.set_editor_property("parameter_name", n); q.set_editor_property("default_value", 0.0); fp[n] = q
    fl = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, -500, -400)
    fins = []
    for n in ("C", "Hue", "Inv", "Sep"):
        ci = unreal.CustomInput(); ci.set_editor_property("input_name", n); fins.append(ci)
    fl.set_editor_property("inputs", fins); fl.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3); fl.set_editor_property("code", FILTER_CODE)
    MEL.connect_material_expressions(tex, "RGB", fl, "C"); MEL.connect_material_expressions(fp["Hue"], "", fl, "Hue")
    MEL.connect_material_expressions(fp["Invert"], "", fl, "Inv"); MEL.connect_material_expressions(fp["Sepia"], "", fl, "Sep")
    vc = MEL.create_material_expression(m, unreal.MaterialExpressionVertexColor, -700, 500)
    rgb = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -350, -150)
    MEL.connect_material_expressions(fl, "", rgb, "A"); MEL.connect_material_expressions(vc, "", rgb, "B")
    a1 = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -350, 200)
    MEL.connect_material_expressions(tex, "A", a1, "A"); MEL.connect_material_expressions(cu, "", a1, "B")
    a2 = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -150, 250)
    MEL.connect_material_expressions(a1, "", a2, "A"); MEL.connect_material_expressions(vc, "A", a2, "B")
    MEL.connect_material_property(rgb, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.connect_material_property(a2, "", unreal.MaterialProperty.MP_OPACITY)
    MEL.recompile_material(m); EAL.save_asset(IMG)


try:
    main()
except Exception:
    import traceback; unreal.log_warning("EDTEST FAIL exception: " + traceback.format_exc().replace("\n", " | "))
