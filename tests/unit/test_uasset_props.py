"""uasset_props.Reader: material inputs (binary structs) and the limits that stop a mis-read count (2026-10-31).

Synthetic bytes only. The pattern is the one of a clothes mod's parent material: its ScalarMaterialInput, read as a
tagged property list, claimed an array of 838 860 800 elements of a type named like a package (60 s, 7.7 GB)."""
import os, struct, sys, time, unittest
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts"))
import uasset_props

NAMES = ["/Game/Mod/T/M", "After", "ArrayProperty", "ColorMaterialInput", "EmissiveColor", "IntProperty", "Ints",
         "MapProperty", "MaterialAttributes", "MaterialAttributesInput", "MaterialExpressionMultiply", "None", "Normal",
         "ScalarMaterialInput", "Specular", "StructProperty", "VectorMaterialInput", "W", "Weird", "X",
         "Vector2MaterialInput", "ShadingModelMaterialInput", "ExpressionInput", "SetProperty", "S", "ObjectProperty", "Objs"]
IDX = {n: i for i, n in enumerate(NAMES)}
END = struct.pack("<ii", IDX["None"], 0)


def fn(name, num=0):
    return struct.pack("<ii", IDX[name], num)


def hdr(name, typ, size, extra=b""):
    return fn(name) + fn(typ) + struct.pack("<ii", size, 0) + extra + b"\0"


def struct_hdr(name, sname, size):
    return hdr(name, "StructProperty", size, fn(sname) + b"\0" * 16)


def int_prop(name, v):
    return hdr(name, "IntProperty", 4) + struct.pack("<i", v)


def expr_input():
    """FExpressionInput as cooked: OutputIndex, InputName, 5 masks, ExpressionName (40 bytes)."""
    return struct.pack("<i", 0) + fn("None") + struct.pack("<5i", 0, 0, 0, 0, 0) + fn("MaterialExpressionMultiply", 1)


def reader(data):
    return uasset_props.Reader(data, NAMES, [], [])


def read(data):
    return reader(data).props()


class MaterialInputs(unittest.TestCase):
    def test_scalar(self):
        body = expr_input() + struct.pack("<if", 0, 0.5)
        self.assertEqual(len(body), 48)
        p = read(struct_hdr("Specular", "ScalarMaterialInput", 48) + body + int_prop("After", 7) + END)
        self.assertEqual(p["Specular"], {"OutputIndex": 0, "InputName": "None", "Mask": [0, 0, 0, 0, 0],
                                         "ExpressionName": "MaterialExpressionMultiply_0", "UseConstant": False,
                                         "Constant": 0.5})
        self.assertEqual(p["After"], 7)

    def test_vector_color_attributes(self):
        n = expr_input() + struct.pack("<i3f", 1, 0.0, 0.0, 1.0)
        e = expr_input() + struct.pack("<i", 0) + bytes([10, 20, 30, 255])
        p = read(struct_hdr("Normal", "VectorMaterialInput", 56) + n + struct_hdr("EmissiveColor", "ColorMaterialInput", 48)
                 + e + struct_hdr("MaterialAttributes", "MaterialAttributesInput", 40) + expr_input() + END)
        self.assertTrue(p["Normal"]["UseConstant"]); self.assertEqual(p["Normal"]["Constant"], {"x": 0.0, "y": 0.0, "z": 1.0})
        self.assertEqual(p["EmissiveColor"]["Constant"], {"b": 10, "g": 20, "r": 30, "a": 255})
        self.assertEqual(p["MaterialAttributes"]["ExpressionName"], "MaterialExpressionMultiply_0")
        self.assertNotIn("Constant", p["MaterialAttributes"])

    def test_unexpected_size_is_an_error_not_garbage(self):
        body = expr_input() + struct.pack("<if", 0, 0.5) + b"\0" * 4
        p = read(struct_hdr("Specular", "ScalarMaterialInput", 52) + body + int_prop("After", 7) + END)
        self.assertTrue(str(p["Specular"]).startswith("<err"), p["Specular"])
        self.assertIn("bytes read, the tag says", p["Specular"])
        self.assertEqual(p["After"], 7)

    def test_vector2(self):
        body = expr_input() + struct.pack("<i2f", 1, 0.25, 0.5)
        p = read(struct_hdr("Normal", "Vector2MaterialInput", 52) + body + END)
        self.assertEqual((p["Normal"]["UseConstant"], p["Normal"]["Constant"]), (True, {"x": 0.25, "y": 0.5}))

    def test_shading_model(self):
        p = read(struct_hdr("Normal", "ShadingModelMaterialInput", 48) + expr_input() + struct.pack("<iI", 0, 3) + END)
        self.assertEqual((p["Normal"]["UseConstant"], p["Normal"]["Constant"]), (False, 3))

    def test_expression_input(self):
        p = read(struct_hdr("Normal", "ExpressionInput", 40) + expr_input() + END)
        self.assertEqual(p["Normal"]["ExpressionName"], "MaterialExpressionMultiply_0")
        self.assertNotIn("Constant", p["Normal"])


class Limits(unittest.TestCase):
    def test_bogus_array_in_a_struct_fails_fast(self):
        body = hdr("X", "ArrayProperty", 0, fn("/Game/Mod/T/M")) + struct.pack("<i", 0x7FFFFFFF)
        body += b"\0" * (40 - len(body))
        t = time.time()
        p = read(struct_hdr("W", "Weird", 40) + body + int_prop("After", 7) + END)
        self.assertLess(time.time() - t, 1.0)
        self.assertTrue(str(p["W"]).startswith("<err"), p["W"])
        self.assertEqual(p["After"], 7)

    def test_array_count_beyond_the_bytes(self):
        with self.assertRaisesRegex(ValueError, "count 1000 does not fit"):
            reader(struct.pack("<i", 1000) + b"\0" * 8).array_value("IntProperty", 0)

    def test_array_count_bounded_by_its_property(self):
        arr = hdr("Ints", "ArrayProperty", 12, fn("IntProperty")) + struct.pack("<iii", 3, 1, 2)
        p = read(arr + int_prop("After", 7) + END)
        self.assertTrue(str(p["Ints"]).startswith("<err"), p["Ints"])
        self.assertEqual(p["After"], 7)

    def test_map_count_beyond_the_bytes(self):
        with self.assertRaisesRegex(ValueError, "count 1000 does not fit"):
            reader(struct.pack("<ii", 0, 1000) + b"\0" * 8).map_value("IntProperty", "IntProperty", 0)

    def test_unknown_element_type_is_refused(self):
        with self.assertRaisesRegex(ValueError, "element size unknown"):
            reader(struct.pack("<i", 3) + b"\0" * 64).array_value("FooProperty", 0)

    def test_tag_with_a_name_as_type(self):
        with self.assertRaisesRegex(ValueError, "no property tag"):
            reader(hdr("X", "ArrayProperty", 0, fn("/Game/Mod/T/M")) + b"\0" * 8).tag()

    def test_tag_larger_than_the_data(self):
        with self.assertRaisesRegex(ValueError, "4000 bytes"):
            reader(hdr("After", "IntProperty", 4000) + struct.pack("<i", 7)).tag()

    def test_count_that_fits_exactly(self):
        self.assertEqual(reader(struct.pack("<i", 2) + struct.pack("<ii", 5, 6)).array_value("IntProperty", 0), [5, 6])

    def test_negative_count(self):
        with self.assertRaisesRegex(ValueError, "count -1 does not fit"):
            reader(struct.pack("<i", -1) + b"\0" * 8).array_value("IntProperty", 0)

    def test_set_reads(self):
        st = hdr("S", "SetProperty", 16, fn("IntProperty")) + struct.pack("<iiii", 0, 2, 5, 6)
        self.assertEqual(read(st + int_prop("After", 7) + END), {"S": [5, 6], "After": 7})

    def test_map_with_unknown_type_is_refused(self):
        with self.assertRaisesRegex(ValueError, "element size unknown"):
            reader(struct.pack("<ii", 0, 2) + b"\0" * 64).map_value("FooProperty", "IntProperty", 0)

    def test_end_is_restored_after_a_failed_property(self):
        bad = hdr("Ints", "ArrayProperty", 12, fn("IntProperty")) + struct.pack("<iii", 3, 1, 2)
        good = hdr("X", "ArrayProperty", 12, fn("IntProperty")) + struct.pack("<iii", 2, 1, 2)
        data = bad + good + END
        r = reader(data)
        p = r.props()
        self.assertTrue(str(p["Ints"]).startswith("<err"), p["Ints"])
        self.assertEqual(p["X"], [1, 2])
        self.assertEqual(r.end, len(data))

    def test_failing_elements_make_one_error_not_many(self):
        """Elements have no size of their own: a failing one cannot be skipped, so the property is one <err>."""
        arr = hdr("Objs", "ArrayProperty", 16, fn("ObjectProperty")) + struct.pack("<ii", 3, -5) + struct.pack("<ii", -5, -5)
        p = read(arr + int_prop("After", 7) + END)
        self.assertIsInstance(p["Objs"], str)
        self.assertTrue(p["Objs"].startswith("<err"), p["Objs"])
        self.assertEqual(p["After"], 7)

    def test_good_arrays_still_read(self):
        arr = hdr("Ints", "ArrayProperty", 12, fn("IntProperty")) + struct.pack("<iii", 2, 1, 2)
        self.assertEqual(read(arr + int_prop("After", 7) + END), {"Ints": [1, 2], "After": 7})


if __name__ == "__main__":
    unittest.main()
