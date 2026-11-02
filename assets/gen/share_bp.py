"""Share as JSON in Blueprint (internal design notes): generated from share_format.py.
Tokenizer: the text split once (quotes, then commas), the short parts into ShTokK / ShTokS / ShTokN / ShTokP. Readers walk the tokens (ShPos), writers append
pieces to ShOut (joined once at the end - Concat in a loop would copy the whole text again for every piece)."""
from bpdsl import G, fn, param, K_ARR, K_STR, K_MATH, S_LINCOLOR
import share_format as sf

T = sf.TOK
DIGITS = "-0123456789"; LETTERS = "abcdefghijklmnopqrstuvwxyz"; WS = " \t\r\n"
ESC = {"n": "\n", "t": "\t", "r": "\r", "b": "", "f": ""}   # \" \\ \/ give the character itself


def f_sh_emit():
    g = G()
    for v, pin in (("ShTokK", "@entry.kind"), ("ShTokS", "@entry.s"), ("ShTokN", "@entry.n"), ("ShTokP", "@entry.pos")):
        g.get("g" + v, v); g.call("a" + v, K_ARR, "Array_Add", inp={"TargetArray": "@g%s.%s" % (v, v), "NewItem": pin})
    g.chain("entry", "aShTokK", "aShTokS", "aShTokN", "aShTokP")
    return fn("Sh Emit", [param("kind", "int"), param("s", "string"), param("n", "float"), param("pos", "int")], graph=g)


def f_sh_fail():
    g = G(); g.set("so", "ShOk", inp={"ShOk": "false"}); g.set("se", "ShErr", inp={"ShErr": "@entry.key"}); g.set("sp", "ShErrPos", inp={"ShErrPos": "@entry.pos"})
    g.chain("entry", "so", "se", "sp"); return fn("Sh Fail", [param("key", "string"), param("pos", "int")], graph=g)


def contains(g, id, chars, c_pin):
    g.call(id, K_STR, "Contains", inp={"SearchIn": chars, "Substring": c_pin, "bUseCase": "true", "bSearchFromEnd": "false"}); return "@%s.ReturnValue" % id


STRUCT = "{}[]:"
PIECE_END = ["{", "}", "[", "]", ":", " ", "\t", "\r", "\n"]


def f_share_tokenize():
    """The text is split once at every quote: the parts alternate between "outside a string" and "inside" (Sh Tok Out / Sh Tok In);
    a part inside that ends in an odd number of backslashes was cut at an escaped quote and goes on in the next part. ShCur is the
    character position of the part (for error messages). The big text is not touched again - a Blueprint call that takes it
    copies it (2026-10-31: 3.1 s for 50 looks that way; character by character 0.66 s and the editor's runaway-loop guard)."""
    g = G()
    for v in ("ShTokK", "ShTokS", "ShTokN", "ShTokP"): g.get("c" + v, v); g.call("x" + v, K_ARR, "Array_Clear", inp={"TargetArray": "@c%s.%s" % (v, v)})
    g.set("ok0", "ShOk", inp={"ShOk": "true"}); g.set("in0", "ShInStr", inp={"ShInStr": "false"}); g.set("b0", "ShBuf", inp={"ShBuf": ""}); g.set("c0", "ShCur", inp={"ShCur": "0"})
    g.call("sp", K_STR, "ParseIntoArray", inp={"SourceString": "@entry.text", "Delimiter": '"', "CullEmptyStrings": "false"}); g.set("ss", "ShSegs", inp={"ShSegs": "@sp.ReturnValue"})
    g.get("gs", "ShSegs"); g.foreach("fe", "@gs.ShSegs"); g.get("gok", "ShOk"); g.branch("bok", "@gok.ShOk")
    g.call("ln", K_ARR, "Array_Length", inp={"TargetArray": "@gs.ShSegs"}); g.call("lst", K_MATH, "Subtract_IntInt", inp={"A": "@ln.ReturnValue", "B": "1"})
    g.call("isl", K_MATH, "EqualEqual_IntInt", inp={"A": "@fe.Array Index", "B": "@lst.ReturnValue"}); g.set("sl", "ShLastSeg", inp={"ShLastSeg": "@isl.ReturnValue"})
    g.get("gin", "ShInStr"); g.branch("bin", "@gin.ShInStr")
    g.n("ti", "call_self", function="Sh Tok In", inp={"seg": "@fe.Array Element"}); g.n("to", "call_self", function="Sh Tok Out", inp={"seg": "@fe.Array Element"})
    g.get("gc", "ShCur"); g.call("sl2", K_STR, "Len", inp={"S": "@fe.Array Element"}); g.call("a1", K_MATH, "Add_IntInt", inp={"A": "@gc.ShCur", "B": "@sl2.ReturnValue"})
    g.call("a2", K_MATH, "Add_IntInt", inp={"A": "@a1.ReturnValue", "B": "1"}); g.set("sc", "ShCur", inp={"ShCur": "@a2.ReturnValue"})
    g.chain("entry", "xShTokK", "xShTokS", "xShTokN", "xShTokP", "ok0", "in0", "b0", "c0", "ss", "fe")
    g.chain("fe", "bok", "sl", "bin", "ti", "sc"); g.chain("bin:else", "to", "sc")
    g.chain("fe:Completed", "return"); g.get("rok", "ShOk"); g.link("rok.ShOk", "return.ok")
    return fn("Share Tokenize", [param("text", "string")], [param("ok", "bool")], graph=g)


def f_sh_tok_in():
    """A part inside a string. Odd number of trailing backslashes: the quote after it was escaped - keep it, the string goes on.
    Otherwise the string ends: unescaped, emitted. The last part being inside a string = no closing quote."""
    g = G(); g.get("gl", "ShLastSeg"); g.branch("bl", "@gl.ShLastSeg"); g.get("gc0", "ShCur")
    g.n("bad", "call_self", function="Sh Fail", inp={"key": "Share_ErrJson", "pos": "@gc0.ShCur"})
    # trailing backslashes, counted from the end (bounded by the part's length)
    g.set("n0", "ShSkip", inp={"ShSkip": "0"}); g.call("ln", K_STR, "Len", inp={"S": "@entry.seg"})
    g.call("lm", K_MATH, "Subtract_IntInt", inp={"A": "@ln.ReturnValue", "B": "1"})
    g.n("fl", "macro", name="ForLoopWithBreak", inp={"First Index": "0", "Last Index": "@lm.ReturnValue"})
    g.call("ix", K_MATH, "Subtract_IntInt", inp={"A": "@lm.ReturnValue", "B": "@fl.Index"}); g.call("ch", K_STR, "GetSubstring", inp={"SourceString": "@entry.seg", "StartIndex": "@ix.ReturnValue", "Length": "1"})
    g.call("isb", K_STR, "EqualEqual_StrStr", inp={"A": "@ch.ReturnValue", "B": "\\"}); g.branch("bb", "@isb.ReturnValue")
    g.get("gn", "ShSkip"); g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gn.ShSkip", "B": "1"}); g.set("sn", "ShSkip", inp={"ShSkip": "@inc.ReturnValue"})
    g.get("gn2", "ShSkip"); g.call("odd", K_MATH, "Percent_IntInt", inp={"A": "@gn2.ShSkip", "B": "2"}); g.call("isodd", K_MATH, "EqualEqual_IntInt", inp={"A": "@odd.ReturnValue", "B": "1"}); g.branch("bo", "@isodd.ReturnValue")
    g.get("gb", "ShBuf"); g.call("j1", K_STR, "Concat_StrStr", inp={"A": "@gb.ShBuf", "B": "@entry.seg"}); g.call("j2", K_STR, "Concat_StrStr", inp={"A": "@j1.ReturnValue", "B": '"'})
    g.set("sb", "ShBuf", inp={"ShBuf": "@j2.ReturnValue"})
    g.get("gb2", "ShBuf"); g.call("f1", K_STR, "Concat_StrStr", inp={"A": "@gb2.ShBuf", "B": "@entry.seg"}); g.n("ue", "call_self", function="Sh Unescape", inp={"s": "@f1.ReturnValue"})
    g.get("gsp", "ShStrPos"); g.n("em", "call_self", function="Sh Emit", inp={"kind": str(T["str"]), "s": "@ue.out", "n": "0.0", "pos": "@gsp.ShStrPos"})
    g.set("b0", "ShBuf", inp={"ShBuf": ""}); g.set("ou", "ShInStr", inp={"ShInStr": "false"})
    # the usual string: no backslash, nothing buffered -> as it is (no loop, no unescape)
    g.call("hb", K_STR, "Contains", inp={"SearchIn": "@entry.seg", "Substring": "\\", "bUseCase": "true", "bSearchFromEnd": "false"})
    g.get("gbz", "ShBuf"); g.call("be", K_STR, "IsEmpty", inp={"InString": "@gbz.ShBuf"}); g.call("nhb", K_MATH, "Not_PreBool", inp={"A": "@hb.ReturnValue"})
    g.call("fast", K_MATH, "BooleanAND", inp={"A": "@nhb.ReturnValue", "B": "@be.ReturnValue"}); g.branch("bf", "@fast.ReturnValue")
    g.get("gsp0", "ShStrPos"); g.n("ef", "call_self", function="Sh Emit", inp={"kind": str(T["str"]), "s": "@entry.seg", "n": "0.0", "pos": "@gsp0.ShStrPos"}); g.set("ouf", "ShInStr", inp={"ShInStr": "false"})
    g.chain("entry", "bl", "bad"); g.chain("bl:else", "bf", "ef", "ouf"); g.chain("bf:else", "n0", "fl"); g.chain("fl", "bb", "sn"); g.chain("bb:else", "fl:Break")
    g.chain("fl:Completed", "bo", "sb"); g.chain("bo:else", "em", "b0", "ou")
    return fn("Sh Tok In", [param("seg", "string")], graph=g)


def f_sh_unescape():
    """\\\\ \\" \\/ \\n \\t \\r \\b \\f -> the characters (\\\\ through a placeholder first, so "\\\\n" stays a backslash + n);
    \\uXXXX stays as written (AltUI never writes it)."""
    g = G(); s_ = "@entry.s"; PH = "\u0001"
    for i, (a, b) in enumerate((("\\\\", PH), ('\\"', '"'), ("\\/", "/"), ("\\n", "\n"), ("\\t", "\t"), ("\\r", "\r"), ("\\b", ""), ("\\f", ""), (PH, "\\"))):
        g.call("r%d" % i, K_STR, "Replace", inp={"SourceString": s_, "From": a, "To": b, "SearchCase": "CaseSensitive"}); s_ = "@r%d.ReturnValue" % i
    g.link(s_[1:], "return.out"); g.chain("entry", "return")
    return fn("Sh Unescape", [param("s", "string")], [param("out", "string")], graph=g, pure=True)


def f_sh_tok_out():
    """A part outside strings: pieces between commas (a comma token between them); not the last part -> a string starts at the
    quote after it (ShStrPos)."""
    g = G(); g.call("sp", K_STR, "ParseIntoArray", inp={"SourceString": "@entry.seg", "Delimiter": ",", "CullEmptyStrings": "false"}); g.set("sps", "ShPieces", inp={"ShPieces": "@sp.ReturnValue"})
    g.get("gc", "ShCur"); g.set("po", "ShPieceOff", inp={"ShPieceOff": "@gc.ShCur"})
    g.get("gp", "ShPieces"); g.foreach("fe", "@gp.ShPieces")
    g.call("gt", K_MATH, "Greater_IntInt", inp={"A": "@fe.Array Index", "B": "0"}); g.branch("bc", "@gt.ReturnValue")
    g.get("go", "ShPieceOff"); g.call("cp", K_MATH, "Subtract_IntInt", inp={"A": "@go.ShPieceOff", "B": "1"})
    g.n("ec", "call_self", function="Sh Emit", inp={"kind": str(T[","]), "s": "", "n": "0.0", "pos": "@cp.ReturnValue"})
    g.get("go2", "ShPieceOff"); g.n("tp", "call_self", function="Sh Tok Piece", inp={"p": "@fe.Array Element", "pos": "@go2.ShPieceOff"})
    # most pieces need no loop: empty ones (between two strings) and plain numbers ("0.500000")
    g.call("pe", K_STR, "IsEmpty", inp={"InString": "@fe.Array Element"}); g.branch("bpe", "@pe.ReturnValue")
    g.call("pn", K_STR, "IsNumeric", inp={"SourceString": "@fe.Array Element"}); g.branch("bpn", "@pn.ReturnValue")
    g.call("pf", K_STR, "Conv_StringToFloat", inp={"InString": "@fe.Array Element"})
    g.n("pen", "call_self", function="Sh Emit", inp={"kind": str(T["num"]), "s": "@fe.Array Element", "n": "@pf.ReturnValue", "pos": "@go2.ShPieceOff"})
    g.call("pl", K_STR, "Len", inp={"S": "@fe.Array Element"}); g.get("go3", "ShPieceOff"); g.call("o1", K_MATH, "Add_IntInt", inp={"A": "@go3.ShPieceOff", "B": "@pl.ReturnValue"})
    g.call("o2", K_MATH, "Add_IntInt", inp={"A": "@o1.ReturnValue", "B": "1"}); g.set("so", "ShPieceOff", inp={"ShPieceOff": "@o2.ReturnValue"})
    g.get("gl", "ShLastSeg"); g.branch("bl", "@gl.ShLastSeg"); g.set("si", "ShInStr", inp={"ShInStr": "true"})
    g.get("gc2", "ShCur"); g.call("ln", K_STR, "Len", inp={"S": "@entry.seg"}); g.call("qp", K_MATH, "Add_IntInt", inp={"A": "@gc2.ShCur", "B": "@ln.ReturnValue"}); g.set("ssp", "ShStrPos", inp={"ShStrPos": "@qp.ReturnValue"})
    g.chain("entry", "sps", "po", "fe"); g.chain("fe", "bc", "ec", "bpe", "so"); g.chain("bc:else", "bpe"); g.chain("bpe:else", "bpn", "pen", "so"); g.chain("bpn:else", "tp", "so")
    g.chain("fe:Completed", "bl"); g.chain("bl:else", "si", "ssp")
    return fn("Sh Tok Out", [param("seg", "string")], graph=g)


def f_sh_tok_piece():
    """A piece between commas (at most a few characters): brackets / colons and blanks one by one; the first other character
    starts a value that runs to the next bracket, colon or blank (Sh Tok Value); then the rest one by one again."""
    g = G(); g.call("ln", K_STR, "Len", inp={"S": "@entry.p"}); g.call("lm", K_MATH, "Subtract_IntInt", inp={"A": "@ln.ReturnValue", "B": "1"})
    g.set("v0", "ShPieceVal", inp={"ShPieceVal": "-1"})
    g.n("fl", "macro", name="ForLoopWithBreak", inp={"First Index": "0", "Last Index": "@lm.ReturnValue"})
    g.get("gv", "ShPieceVal"); g.call("inv", K_MATH, "Less_IntInt", inp={"A": "@fl.Index", "B": "@gv.ShPieceVal"}); g.branch("bskip", "@inv.ReturnValue")   # inside the value
    g.call("ch", K_STR, "GetSubstring", inp={"SourceString": "@entry.p", "StartIndex": "@fl.Index", "Length": "1"}); C = "@ch.ReturnValue"
    g.call("pos", K_MATH, "Add_IntInt", inp={"A": "@entry.pos", "B": "@fl.Index"})
    tail = "bskip:else"
    for i, ch in enumerate(STRUCT):
        p = "s%d" % i
        g.call(p + "e", K_STR, "EqualEqual_StrStr", inp={"A": C, "B": ch}); g.branch(p + "b", "@%se.ReturnValue" % p)
        g.n(p + "x", "call_self", function="Sh Emit", inp={"kind": str(T[ch]), "s": "", "n": "0.0", "pos": "@pos.ReturnValue"})
        g.chain(tail, p + "b", p + "x"); tail = p + "b:else"
    g.call("ws", K_STR, "Contains", inp={"SearchIn": WS, "Substring": C, "bUseCase": "true", "bSearchFromEnd": "false"}); g.branch("bws", "@ws.ReturnValue")
    g.call("rest", K_STR, "RightChop", inp={"SourceString": "@entry.p", "Count": "@fl.Index"}); g.n("tv", "call_self", function="Sh Tok Value", inp={"v": "@rest.ReturnValue", "pos": "@pos.ReturnValue"})
    g.call("ve", K_MATH, "Add_IntInt", inp={"A": "@fl.Index", "B": "@tv.len"}); g.set("sv", "ShPieceVal", inp={"ShPieceVal": "@ve.ReturnValue"})
    g.chain("entry", "v0", "fl"); g.chain("fl", "bskip"); g.chain(tail, "bws"); g.chain("bws:else", "tv", "sv")
    return fn("Sh Tok Piece", [param("p", "string"), param("pos", "int")], graph=g)


def f_sh_tok_value():
    """A number or true / false / null at the start of v, up to the next bracket, colon or blank. len = its length (at least 1)."""
    g = G(); g.call("vl", K_STR, "Len", inp={"S": "@entry.v"}); best = "@vl.ReturnValue"
    for i, d in enumerate(PIECE_END):
        g.call("f%d" % i, K_STR, "FindSubstring", inp={"SearchIn": "@entry.v", "Substring": d, "bUseCase": "true", "bSearchFromEnd": "false", "StartPosition": "-1"})
        g.call("ok%d" % i, K_MATH, "GreaterEqual_IntInt", inp={"A": "@f%d.ReturnValue" % i, "B": "0"})
        g.call("mn%d" % i, K_MATH, "Min", inp={"A": best, "B": "@f%d.ReturnValue" % i}); g.call("s%d" % i, K_MATH, "SelectInt", inp={"A": "@mn%d.ReturnValue" % i, "B": best, "bPickA": "@ok%d.ReturnValue" % i})
        best = "@s%d.ReturnValue" % i
    g.call("tok", K_STR, "Left", inp={"SourceString": "@entry.v", "Count": best}); g.call("c0", K_STR, "Left", inp={"SourceString": "@entry.v", "Count": "1"})
    g.call("isn", K_STR, "Contains", inp={"SearchIn": DIGITS, "Substring": "@c0.ReturnValue", "bUseCase": "true", "bSearchFromEnd": "false"}); g.branch("bn", "@isn.ReturnValue")
    g.call("nf", K_STR, "Conv_StringToFloat", inp={"InString": "@tok.ReturnValue"})
    g.n("en", "call_self", function="Sh Emit", inp={"kind": str(T["num"]), "s": "@tok.ReturnValue", "n": "@nf.ReturnValue", "pos": "@entry.pos"})
    tail = "bn:else"
    for wd in ("true", "false", "null"):
        g.call("e" + wd, K_STR, "EqualEqual_StrStr", inp={"A": "@tok.ReturnValue", "B": wd}); g.branch("b" + wd, "@e%s.ReturnValue" % wd)
        g.n("x" + wd, "call_self", function="Sh Emit", inp={"kind": str(T[wd]), "s": "", "n": "0.0", "pos": "@entry.pos"})
        g.chain(tail, "b" + wd, "x" + wd, "return"); tail = "b%s:else" % wd
    g.n("bad", "call_self", function="Sh Fail", inp={"key": "Share_ErrJson", "pos": "@entry.pos"}); g.chain(tail, "bad", "return")
    g.call("one", K_MATH, "Max", inp={"A": best, "B": "1"}); g.link("one.ReturnValue", "return.len")
    g.chain("entry", "bn", "en", "return")
    return fn("Sh Tok Value", [param("v", "string"), param("pos", "int")], [param("len", "int")], graph=g)


def tokenizer_functions():
    return [f_sh_emit(), f_sh_fail(), f_share_tokenize(), f_sh_tok_in(), f_sh_unescape(), f_sh_tok_out(), f_sh_tok_piece(), f_sh_tok_value()]


# ---------------- reading (ShPos walks the tokens) and writing (pieces into ShOut) ----------------
S_COLOR = "struct:/Script/CoreUObject.Color"


def tok_get(g, id, arr, idx_pin):
    g.get(id + "_a", arr); g.call(id, K_ARR, "Array_Get", inp={"TargetArray": "@%s_a.%s" % (id, arr), "Index": idx_pin}); return "@%s.Item" % id


def f_sh_noop():
    """An empty step: a join point for exec chains (no outputs, so no return node - an empty graph, like Mutate on the follower)."""
    return fn("Sh Noop", graph=G())


def f_sh_peek():
    g = G(); g.get("gp", "ShPos"); g.get("gk", "ShTokK"); g.call("vi", K_ARR, "Array_IsValidIndex", inp={"TargetArray": "@gk.ShTokK", "IndexToTest": "@gp.ShPos"})
    k = tok_get(g, "tk", "ShTokK", "@gp.ShPos"); g.call("sel", K_MATH, "SelectInt", inp={"A": k, "B": "0", "bPickA": "@vi.ReturnValue"})
    g.link("sel.ReturnValue", "return.kind"); g.chain("entry", "return")
    return fn("Sh Peek", [], [param("kind", "int")], graph=g, pure=True)


def f_sh_next():
    g = G(); g.get("gp", "ShPos"); g.call("a", K_MATH, "Add_IntInt", inp={"A": "@gp.ShPos", "B": "1"}); g.set("s", "ShPos", inp={"ShPos": "@a.ReturnValue"})
    g.chain("entry", "s"); return fn("Sh Next", graph=g)


def err_pos(g, id):
    """Character position of the current token (-1 past the last one)."""
    g.get(id + "_p", "ShPos"); g.get(id + "_k", "ShTokP"); g.call(id + "_v", K_ARR, "Array_IsValidIndex", inp={"TargetArray": "@%s_k.ShTokP" % id, "IndexToTest": "@%s_p.ShPos" % id})
    p = tok_get(g, id + "_g", "ShTokP", "@%s_p.ShPos" % id); g.call(id, K_MATH, "SelectInt", inp={"A": p, "B": "-1", "bPickA": "@%s_v.ReturnValue" % id}); return "@%s.ReturnValue" % id


def f_sh_expect():
    g = G(); g.n("pk", "call_self", function="Sh Peek"); g.call("eq", K_MATH, "EqualEqual_IntInt", inp={"A": "@pk.kind", "B": "@entry.kind"}); g.branch("b", "@eq.ReturnValue")
    g.n("nx", "call_self", function="Sh Next"); g.n("fl", "call_self", function="Sh Fail", inp={"key": "Share_ErrJson", "pos": err_pos(g, "ep")})
    g.get("rok", "ShOk"); g.link("rok.ShOk", "return.ok")   # not eq: the return node would compare the next token (pure nodes are read late)
    g.chain("entry", "b", "nx", "return"); g.chain("b:else", "fl", "return")
    return fn("Sh Expect", [param("kind", "int")], [param("ok", "bool")], graph=g)


READ_VAR = {"string": "ShRS", "float": "ShRN", "bool": "ShRB"}


def reader(name, kinds, out, conv):
    """Read one scalar token of one of `kinds`: conv(g, token_index_pin) is stored (ShRS / ShRN / ShRB) before Sh Next - a pure node
    is evaluated only when the return node reads it, by then ShPos already points at the next token. Another kind -> Sh Fail."""
    g = G(); g.n("pk", "call_self", function="Sh Peek"); g.get("gp", "ShPos"); ok = None
    for i, k in enumerate(kinds):
        g.call("e%d" % i, K_MATH, "EqualEqual_IntInt", inp={"A": "@pk.kind", "B": str(k)})
        if ok is None: ok = "@e%d.ReturnValue" % i
        else: g.call("o%d" % i, K_MATH, "BooleanOR", inp={"A": ok, "B": "@e%d.ReturnValue" % i}); ok = "@o%d.ReturnValue" % i
    v = READ_VAR[out[1]]
    g.branch("b", ok); g.set("sv", v, inp={v: conv(g, "@gp.ShPos")})
    g.n("nx", "call_self", function="Sh Next"); g.n("fl", "call_self", function="Sh Fail", inp={"key": "Share_ErrJson", "pos": err_pos(g, "ep")})
    g.get("rv", v); g.link("rv." + v, "return." + out[0]); g.chain("entry", "b", "sv", "nx", "return"); g.chain("b:else", "fl", "return")
    return fn(name, [], [param(*out)], graph=g)


def f_sh_r_str(): return reader("Sh R Str", [T["str"]], ("s", "string"), lambda g, p: tok_get(g, "v", "ShTokS", p))
def f_sh_r_num(): return reader("Sh R Num", [T["num"]], ("n", "float"), lambda g, p: tok_get(g, "v", "ShTokN", p))


def f_sh_r_bool():
    def conv(g, p):
        k = tok_get(g, "v", "ShTokK", p); g.call("t", K_MATH, "EqualEqual_IntInt", inp={"A": k, "B": str(T["true"])}); return "@t.ReturnValue"
    return reader("Sh R Bool", [T["true"], T["false"]], ("b", "bool"), conv)


def f_sh_r_color(byte=False):
    """[r, g, b, a] -> LinearColor, or Color (bytes, rounded, clamped 0..255) with byte=True."""
    g = G(); g.n("o", "call_self", function="Sh Expect", inp={"kind": str(T["["])}); ids = ["o"]; comps = []
    for i, c in enumerate("RGBA"):
        if i: g.n("cm%d" % i, "call_self", function="Sh Expect", inp={"kind": str(T[","])}); ids.append("cm%d" % i)
        g.n("r" + c, "call_self", function="Sh R Num"); ids.append("r" + c); comps.append("@r%s.n" % c)
    g.n("cl", "call_self", function="Sh Expect", inp={"kind": str(T["]"])}); ids.append("cl")
    if byte:
        bs = []
        for c, pin in zip("RGBA", comps):
            g.call("rd" + c, K_MATH, "Round", inp={"A": pin}); g.call("cp" + c, K_MATH, "Clamp", inp={"Value": "@rd%s.ReturnValue" % c, "Min": "0", "Max": "255"})
            g.call("by" + c, K_MATH, "Conv_IntToByte", inp={"InInt": "@cp%s.ReturnValue" % c}); bs.append("@by%s.ReturnValue" % c)
        g.make("mk", "/Script/CoreUObject.Color", R=bs[0], G=bs[1], B=bs[2], A=bs[3]); g.link("mk.Color", "return.c"); out = S_COLOR
    else:
        g.make("mk", "/Script/CoreUObject.LinearColor", R=comps[0], G=comps[1], B=comps[2], A=comps[3]); g.link("mk.LinearColor", "return.c"); out = S_LINCOLOR
    g.chain("entry", *ids, "return")
    return fn("Sh R BColor" if byte else "Sh R Color", [], [param("c", out)], graph=g)


def f_sh_skip_value():
    """Skip one value of any kind (an unknown field): count brackets until the depth is back at 0 - bounded by MAX_TOKENS."""
    g = G(); g.set("d0", "ShSkip", inp={"ShSkip": "0"})
    g.n("fl", "macro", name="ForLoopWithBreak", inp={"First Index": "0", "Last Index": str(sf.MAX_TOKENS)})
    g.n("pk", "call_self", function="Sh Peek")
    g.call("op1", K_MATH, "EqualEqual_IntInt", inp={"A": "@pk.kind", "B": str(T["{"])}); g.call("op2", K_MATH, "EqualEqual_IntInt", inp={"A": "@pk.kind", "B": str(T["["])})
    g.call("op", K_MATH, "BooleanOR", inp={"A": "@op1.ReturnValue", "B": "@op2.ReturnValue"})
    g.call("cl1", K_MATH, "EqualEqual_IntInt", inp={"A": "@pk.kind", "B": str(T["}"])}); g.call("cl2", K_MATH, "EqualEqual_IntInt", inp={"A": "@pk.kind", "B": str(T["]"])})
    g.call("cl", K_MATH, "BooleanOR", inp={"A": "@cl1.ReturnValue", "B": "@cl2.ReturnValue"})
    g.get("gd", "ShSkip"); g.call("inc", K_MATH, "Add_IntInt", inp={"A": "@gd.ShSkip", "B": "1"}); g.call("dec", K_MATH, "Subtract_IntInt", inp={"A": "@gd.ShSkip", "B": "1"})
    g.call("s1", K_MATH, "SelectInt", inp={"A": "@dec.ReturnValue", "B": "@gd.ShSkip", "bPickA": "@cl.ReturnValue"})
    g.call("s2", K_MATH, "SelectInt", inp={"A": "@inc.ReturnValue", "B": "@s1.ReturnValue", "bPickA": "@op.ReturnValue"}); g.set("sd", "ShSkip", inp={"ShSkip": "@s2.ReturnValue"})
    g.call("end", K_MATH, "EqualEqual_IntInt", inp={"A": "@pk.kind", "B": "0"}); g.n("nx", "call_self", function="Sh Next")
    g.get("gd2", "ShSkip"); g.call("z", K_MATH, "LessEqual_IntInt", inp={"A": "@gd2.ShSkip", "B": "0"}); g.branch("bz", "@z.ReturnValue"); g.branch("be", "@end.ReturnValue")
    g.n("fe", "call_self", function="Sh Fail", inp={"key": "Share_ErrJson", "pos": "-1"})
    g.chain("entry", "d0", "fl"); g.chain("fl", "be", "fe", "fl:Break"); g.chain("be:else", "sd", "nx", "bz", "fl:Break")
    return fn("Sh Skip Value", graph=g)


def f_sh_esc():
    """A string as JSON: quoted, \\ " line break, tab, carriage return escaped; other control characters are not written by AltUI."""
    g = G(); s_ = "@entry.s"
    for i, (a, b) in enumerate((("\\", "\\\\"), ('"', '\\"'), ("\n", "\\n"), ("\t", "\\t"), ("\r", "\\r"))):
        g.call("r%d" % i, K_STR, "Replace", inp={"SourceString": s_, "From": a, "To": b, "SearchCase": "CaseSensitive"}); s_ = "@r%d.ReturnValue" % i
    g.call("q1", K_STR, "Concat_StrStr", inp={"A": '"', "B": s_}); g.call("q2", K_STR, "Concat_StrStr", inp={"A": "@q1.ReturnValue", "B": '"'})
    g.link("q2.ReturnValue", "return.out"); g.chain("entry", "return")
    return fn("Sh Esc", [param("s", "string")], [param("out", "string")], graph=g, pure=True)


def writer(name, params, piece):
    """Append piece(g) (a string pin) to ShOut."""
    g = G(); p = piece(g); g.get("go", "ShOut"); g.call("a", K_ARR, "Array_Add", inp={"TargetArray": "@go.ShOut", "NewItem": p}); g.chain("entry", "a")
    return fn(name, params, graph=g)


def _esc_piece(src):
    def p(g):
        g.n("e", "call_self", function="Sh Esc", inp={"s": src}); return "@e.out"
    return p


def _key_piece(g):
    g.n("e", "call_self", function="Sh Esc", inp={"s": "@entry.k"}); g.call("c", K_STR, "Concat_StrStr", inp={"A": "@e.out", "B": ":"}); return "@c.ReturnValue"


def f_sh_w_raw(): return writer("Sh W Raw", [param("s", "string")], lambda g: "@entry.s")
def f_sh_w_str(): return writer("Sh W Str", [param("s", "string")], _esc_piece("@entry.s"))
def f_sh_w_key(): return writer("Sh W Key", [param("k", "string")], _key_piece)


def f_sh_w_num():
    def p(g): g.call("c", K_STR, "Conv_FloatToString", inp={"InFloat": "@entry.n"}); return "@c.ReturnValue"
    return writer("Sh W Num", [param("n", "float")], p)


def f_sh_w_bool():
    def p(g): g.call("c", K_MATH, "SelectString", inp={"A": "true", "B": "false", "bPickA": "@entry.b"}); return "@c.ReturnValue"
    return writer("Sh W Bool", [param("b", "bool")], p)


def f_sh_w_color(byte=False):
    """[r,g,b,a]: LinearColor as floats, Color as whole numbers 0..255."""
    g = G()
    g.brk("bc", "/Script/CoreUObject.Color" if byte else "/Script/CoreUObject.LinearColor", "@entry.c")
    pins = []
    for i, c in enumerate("RGBA"):
        if byte:
            g.call("i%d" % i, K_MATH, "Conv_ByteToInt", inp={"InByte": "@bc." + c}); g.call("s%d" % i, K_STR, "Conv_IntToString", inp={"InInt": "@i%d.ReturnValue" % i})
        else:
            g.call("s%d" % i, K_STR, "Conv_FloatToString", inp={"InFloat": "@bc." + c})
        pins.append("@s%d.ReturnValue" % i)
    g.call("j0", K_STR, "Concat_StrStr", inp={"A": "[", "B": pins[0]}); acc = "@j0.ReturnValue"
    for i in range(1, 4):
        g.call("k%d" % i, K_STR, "Concat_StrStr", inp={"A": acc, "B": ","}); g.call("j%d" % i, K_STR, "Concat_StrStr", inp={"A": "@k%d.ReturnValue" % i, "B": pins[i]}); acc = "@j%d.ReturnValue" % i
    g.call("jz", K_STR, "Concat_StrStr", inp={"A": acc, "B": "]"})
    g.get("go", "ShOut"); g.call("a", K_ARR, "Array_Add", inp={"TargetArray": "@go.ShOut", "NewItem": "@jz.ReturnValue"}); g.chain("entry", "a")
    return fn("Sh W BColor" if byte else "Sh W Color", [param("c", S_COLOR if byte else S_LINCOLOR)], graph=g)


def primitive_functions():
    return [f_sh_noop(), f_sh_peek(), f_sh_next(), f_sh_expect(), f_sh_r_str(), f_sh_r_num(), f_sh_r_bool(), f_sh_r_color(), f_sh_r_color(byte=True), f_sh_skip_value(),
            f_sh_esc(), f_sh_w_raw(), f_sh_w_str(), f_sh_w_key(), f_sh_w_num(), f_sh_w_bool(), f_sh_w_color(), f_sh_w_color(byte=True)]


PRIMITIVE_SIGNATURES = [fn("Sh Noop"), fn("Sh Peek", [], [param("kind", "int")], pure=True), fn("Sh Next"), fn("Sh Expect", [param("kind", "int")], [param("ok", "bool")]),
                        fn("Sh R Str", [], [param("s", "string")]), fn("Sh R Num", [], [param("n", "float")]), fn("Sh R Bool", [], [param("b", "bool")]),
                        fn("Sh R Color", [], [param("c", S_LINCOLOR)]), fn("Sh R BColor", [], [param("c", S_COLOR)]), fn("Sh Skip Value"),
                        fn("Sh Esc", [param("s", "string")], [param("out", "string")], pure=True), fn("Sh W Raw", [param("s", "string")]), fn("Sh W Str", [param("s", "string")]),
                        fn("Sh W Key", [param("k", "string")]), fn("Sh W Num", [param("n", "float")]), fn("Sh W Bool", [param("b", "bool")]),
                        fn("Sh W Color", [param("c", S_LINCOLOR)]), fn("Sh W BColor", [param("c", S_COLOR)])]


# ---------------- schema readers / writers (share_format.SNAP_SCHEMA, MUT_SCHEMA, OUTFIT_SCHEMA) ----------------
# Every generator returns (head, tail): the first exec id of its part and the exec output to go on from ("x" or "fl:Completed").
import mutation as mutn
from bpdsl import K_MAP, var
S_SNAP_PATH = "/Game/Mod/AltUI/S_Snapshot"   # gen_manager.S_SNAP (gen_manager imports this module: no import back)
S_SHAREOUTFIT = "/Game/Mod/AltUI/S_ShareOutfit"; S_MDATA = "/Game/Project/Tables/MakeupDataStruct"
S_SHAREAPP = "/Game/Mod/AltUI/S_ShareAppearance"
SCHEMAS = {"Snap": (S_SNAP_PATH, sf.SNAP_SCHEMA), "Mut": (mutn.S_MUT, sf.MUT_SCHEMA), "Outfit": (S_SHAREOUTFIT, sf.OUTFIT_SCHEMA),
           "Face": ("/Game/Mod/AltUI/S_Face", sf.FACE_SCHEMA), "BodyP": ("/Game/Mod/AltUI/S_BodyPreset", sf.BODYP_SCHEMA),
           "ModP": ("/Game/Mod/AltUI/S_ModPreset", sf.MODP_SCHEMA), "App": (S_SHAREAPP, sf.APP_SCHEMA)}
VAR_TYPE = {"str": ("name", None, None), "num": ("float", None, None), "bool": ("bool", None, None), "color": (S_LINCOLOR, None, None),
            "bcolor": (S_COLOR, None, None), "strs": ("name", "array", None), "nums": ("float", "array", None),
            "map_color": ("name", "map", S_LINCOLOR), "map_num": ("name", "map", "float"), "map_bcolor": ("name", "map", S_COLOR),
            "map_list": ("name", "map", "struct:" + S_MDATA), "mut": ("struct:" + mutn.S_MUT, None, None), "map_str": ("name", "map", "string")}
DEFAULT = {"str": "None", "num": "0.0", "bool": "false", "color": "(R=0.000000,G=0.000000,B=0.000000,A=0.000000)", "bcolor": "(B=0,G=0,R=0,A=0)"}


def field_var(schema, field): return "ShF%s_%s" % (schema, field)


def field_vars():
    out = [var("ShListTmp", "name", "array")]
    for sname, (_, sch) in SCHEMAS.items():
        for f, t in sch:
            base, cont, vt = VAR_TYPE[t]
            out.append(var(field_var(sname, f), base, cont, value_type=vt) if cont else var(field_var(sname, f), base))
    return out


def raw(g, id, text):
    g.n(id, "call_self", function="Sh W Raw", inp={"s": text}); return id


def w_value(g, p, t, pin):
    """Write value `pin` of type t; returns (head, tail)."""
    single = {"num": ("Sh W Num", "n"), "bool": ("Sh W Bool", "b"), "color": ("Sh W Color", "c"), "bcolor": ("Sh W BColor", "c"), "mut": ("Sh W Mut", "v")}
    if t in single:
        f, arg = single[t]; g.n(p + "w", "call_self", function=f, inp={arg: pin}); return p + "w", p + "w"
    if t == "str":
        g.call(p + "ns", K_STR, "Conv_NameToString", inp={"InName": pin}); g.n(p + "w", "call_self", function="Sh W Str", inp={"s": "@%sns.ReturnValue" % p}); return p + "w", p + "w"
    is_map = t.startswith("map_")
    raw(g, p + "o", "{" if is_map else "[")
    if is_map: g.call(p + "ks", K_MAP, "Map_Keys", inp={"TargetMap": pin}); arr = "@%sks.Keys" % p
    else: arr = pin
    g.foreach(p + "fe", arr); E = "@%sfe.Array Element" % p
    g.call(p + "gt", K_MATH, "Greater_IntInt", inp={"A": "@%sfe.Array Index" % p, "B": "0"}); g.branch(p + "b", "@%sgt.ReturnValue" % p); raw(g, p + "c", ",")
    if is_map:
        g.call(p + "kn", K_STR, "Conv_NameToString", inp={"InName": E}); g.n(p + "k", "call_self", function="Sh W Key", inp={"k": "@%skn.ReturnValue" % p})
        g.call(p + "f", K_MAP, "Map_Find", inp={"TargetMap": pin, "Key": E}); val = "@%sf.Value" % p
        if t == "map_list":
            g.brk(p + "ml", S_MDATA, val); raw(g, p + "lo", '{"List":'); lh, lt = w_value(g, p + "lv", "strs", "@%sml.List" % p); raw(g, p + "lc", "}")
            g.chain(p + "k", p + "lo", lh); g.chain(lt, p + "lc"); eh, et = p + "k", p + "lc"
        else:
            if t == "map_str": g.n(p + "vw", "call_self", function="Sh W Str", inp={"s": val}); vh = vt = p + "vw"
            else: vh, vt = w_value(g, p + "v", {"map_color": "color", "map_num": "num", "map_bcolor": "bcolor"}[t], val)
            g.chain(p + "k", vh); eh, et = p + "k", vt
    else:
        eh, et = w_value(g, p + "e", "str" if t == "strs" else "num", E)
    g.chain(p + "fe", p + "b", p + "c", eh); g.chain(p + "b:else", eh)
    raw(g, p + "x", "}" if is_map else "]"); g.chain(p + "o", *([p + "ks"] if is_map else []), p + "fe"); g.chain(p + "fe:Completed", p + "x")   # Map_Keys is impure
    return p + "o", p + "x"


def f_sh_w_schema(sname):
    path, sch = SCHEMAS[sname]
    g = G(); g.brk("bv", path, "@entry.v"); raw(g, "o", "{"); prev = "o"
    for i, (f, t) in enumerate(sch):
        k = "k%d" % i; g.n(k, "call_self", function="Sh W Key", inp={"k": f})
        if i: raw(g, "cm%d" % i, ","); g.chain(prev, "cm%d" % i, k)
        else: g.chain(prev, k)
        h, tl = w_value(g, "f%d_" % i, t, "@bv." + f); g.chain(k, h); prev = tl
    raw(g, "x", "}"); g.chain(prev, "x"); g.chain("entry", "o")
    return fn("Sh W " + sname, [param("v", "struct:" + path)], graph=g)


def r_value(g, p, t, target):
    """Read a value of type t into Manager variable `target`; returns (head, tail)."""
    single = {"num": ("Sh R Num", "n"), "bool": ("Sh R Bool", "b"), "color": ("Sh R Color", "c"), "bcolor": ("Sh R BColor", "c"), "mut": ("Sh R Mut", "v"), "str": ("Sh R Str", "s")}
    if t in single:
        f, out = single[t]; g.n(p + "r", "call_self", function=f); val = "@%sr.%s" % (p, out)
        if t == "str": g.call(p + "cn", K_STR, "Conv_StringToName", inp={"InString": val}); val = "@%scn.ReturnValue" % p
        g.set(p + "s", target, inp={target: val}); g.chain(p + "r", p + "s"); return p + "r", p + "s"
    is_map = t.startswith("map_")
    g.get(p + "g0", target)
    if is_map: g.call(p + "cl", K_MAP, "Map_Clear", inp={"TargetMap": "@%sg0.%s" % (p, target)})
    else: g.call(p + "cl", K_ARR, "Array_Clear", inp={"TargetArray": "@%sg0.%s" % (p, target)})
    g.n(p + "op", "call_self", function="Sh Expect", inp={"kind": str(T["{" if is_map else "["])})
    g.n(p + "fl", "macro", name="ForLoopWithBreak", inp={"First Index": "0", "Last Index": str(sf.MAX_LIST)})
    g.n(p + "pk", "call_self", function="Sh Peek"); g.call(p + "isc", K_MATH, "EqualEqual_IntInt", inp={"A": "@%spk.kind" % p, "B": str(T["}" if is_map else "]"])})
    g.get(p + "ok", "ShOk"); g.call(p + "nok", K_MATH, "Not_PreBool", inp={"A": "@%sok.ShOk" % p}); g.call(p + "stop", K_MATH, "BooleanOR", inp={"A": "@%sisc.ReturnValue" % p, "B": "@%snok.ReturnValue" % p})
    g.branch(p + "bs", "@%sstop.ReturnValue" % p); g.n(p + "nx", "call_self", function="Sh Next")
    if is_map:
        g.n(p + "k", "call_self", function="Sh R Str"); g.call(p + "kn", K_STR, "Conv_StringToName", inp={"InString": "@%sk.s" % p})
        g.n(p + "co", "call_self", function="Sh Expect", inp={"kind": str(T[":"])}); g.chain(p + "k", p + "co")
        if t == "map_list":
            g.n(p + "lo", "call_self", function="Sh Expect", inp={"kind": str(T["{"])}); g.n(p + "lk", "call_self", function="Sh R Str")
            g.n(p + "lc", "call_self", function="Sh Expect", inp={"kind": str(T[":"])}); lh, lt = r_value(g, p + "lv", "strs", "ShListTmp")
            g.n(p + "le", "call_self", function="Sh Expect", inp={"kind": str(T["}"])})
            g.chain(p + "co", p + "lo", p + "lk", p + "lc", lh); g.chain(lt, p + "le")
            g.get(p + "glt", "ShListTmp"); g.make(p + "mk", S_MDATA, List="@%sglt.ShListTmp" % p); val = "@%smk.MakeupDataStruct" % p; last = p + "le"
        else:
            f, out = {"map_color": ("Sh R Color", "c"), "map_num": ("Sh R Num", "n"), "map_bcolor": ("Sh R BColor", "c"), "map_str": ("Sh R Str", "s")}[t]
            g.n(p + "v", "call_self", function=f); g.chain(p + "co", p + "v"); val = "@%sv.%s" % (p, out); last = p + "v"
        g.get(p + "g1", target); g.call(p + "add", K_MAP, "Map_Add", inp={"TargetMap": "@%sg1.%s" % (p, target), "Key": "@%skn.ReturnValue" % p, "Value": val})
        eh = p + "k"; g.chain(last, p + "add")
    else:
        f, out = ("Sh R Str", "s") if t == "strs" else ("Sh R Num", "n")
        g.n(p + "v", "call_self", function=f); val = "@%sv.%s" % (p, out)
        if t == "strs": g.call(p + "vn", K_STR, "Conv_StringToName", inp={"InString": val}); val = "@%svn.ReturnValue" % p
        g.get(p + "g1", target); g.call(p + "add", K_ARR, "Array_Add", inp={"TargetArray": "@%sg1.%s" % (p, target), "NewItem": val}); eh = p + "v"; g.chain(p + "v", p + "add")
    g.n(p + "pk2", "call_self", function="Sh Peek"); g.call(p + "isco", K_MATH, "EqualEqual_IntInt", inp={"A": "@%spk2.kind" % p, "B": str(T[","])}); g.branch(p + "bc", "@%sisco.ReturnValue" % p)
    g.n(p + "nx2", "call_self", function="Sh Next")
    g.chain(p + "cl", p + "op", p + "fl"); g.chain(p + "fl", p + "bs", p + "nx", p + "fl:Break"); g.chain(p + "bs:else", eh); g.chain(p + "add", p + "bc", p + "nx2")
    return p + "cl", p + "fl:Completed"


def reset_field(g, p, sname, f, t):
    """A field starts empty: a missing key in the JSON leaves it so."""
    v = field_var(sname, f); base, cont, _ = VAR_TYPE[t]
    if cont == "map": g.get(p + "g", v); g.call(p, K_MAP, "Map_Clear", inp={"TargetMap": "@%sg.%s" % (p, v)})
    elif cont == "array": g.get(p + "g", v); g.call(p, K_ARR, "Array_Clear", inp={"TargetArray": "@%sg.%s" % (p, v)})
    elif t == "mut": g.make(p + "m", mutn.S_MUT); g.set(p, v, inp={v: "@%sm.S_Mutation" % p})
    else: g.set(p, v, inp={v: DEFAULT[t]})
    return p


def f_sh_r_schema(sname):
    path, sch = SCHEMAS[sname]
    g = G(); resets = [reset_field(g, "z%d" % i, sname, f, t) for i, (f, t) in enumerate(sch)]
    g.n("op", "call_self", function="Sh Expect", inp={"kind": str(T["{"])})
    g.n("fl", "macro", name="ForLoopWithBreak", inp={"First Index": "0", "Last Index": str(sf.MAX_FIELDS)})
    g.n("pk", "call_self", function="Sh Peek"); g.call("isc", K_MATH, "EqualEqual_IntInt", inp={"A": "@pk.kind", "B": str(T["}"])})
    g.get("ok", "ShOk"); g.call("nok", K_MATH, "Not_PreBool", inp={"A": "@ok.ShOk"}); g.call("stop", K_MATH, "BooleanOR", inp={"A": "@isc.ReturnValue", "B": "@nok.ReturnValue"})
    g.branch("bs", "@stop.ReturnValue"); g.n("nx", "call_self", function="Sh Next")
    g.n("k", "call_self", function="Sh R Str"); g.n("co", "call_self", function="Sh Expect", inp={"kind": str(T[":"])}); g.n("after", "call_self", function="Sh Noop")
    prev = "co"
    for i, (f, t) in enumerate(sch):
        g.call("ke%d" % i, K_STR, "EqualEqual_StrStr", inp={"A": "@k.s", "B": f}); g.branch("kb%d" % i, "@ke%d.ReturnValue" % i); g.chain(prev, "kb%d" % i)
        h, tl = r_value(g, "r%d_" % i, t, field_var(sname, f)); g.chain("kb%d" % i, h); g.chain(tl, "after"); prev = "kb%d:else" % i
    g.n("sk", "call_self", function="Sh Skip Value"); g.chain(prev, "sk", "after")
    g.n("pk3", "call_self", function="Sh Peek"); g.call("isco", K_MATH, "EqualEqual_IntInt", inp={"A": "@pk3.kind", "B": str(T[","])}); g.branch("bc", "@isco.ReturnValue")
    g.n("nx2", "call_self", function="Sh Next")
    g.chain("entry", *resets, "op", "fl"); g.chain("fl", "bs", "nx", "fl:Break"); g.chain("bs:else", "k", "co"); g.chain("after", "bc", "nx2"); g.chain("fl:Completed", "return")
    fields = {}
    for f, t in sch: v = field_var(sname, f); g.get("m_" + f, v); fields[f] = "@m_%s.%s" % (f, v)
    g.make("mk", path, **fields); g.link("mk." + path.rsplit("/", 1)[1], "return.v")
    return fn("Sh R " + sname, [], [param("v", "struct:" + path)], graph=g)


def schema_functions():
    return [f_sh_w_schema(s_) for s_ in SCHEMAS] + [f_sh_r_schema(s_) for s_ in SCHEMAS]


SCHEMA_SIGNATURES = [fn("Sh W " + s_, [param("v", "struct:" + SCHEMAS[s_][0])]) for s_ in SCHEMAS] + [fn("Sh R " + s_, [], [param("v", "struct:" + SCHEMAS[s_][0])]) for s_ in SCHEMAS]


# ---------------- the document: generic loops and the reader into staging (ShLooks, ShOutfits, ShRefs, ShModNames) ----------------
S_LOOK_PATH = "/Game/Mod/AltUI/S_Look"; S_SHAREREF = "/Game/Mod/AltUI/S_ShareRef"


def stop_or_close(g, p, close_kind):
    """Branch p+"bs": the next token closes the container, or reading failed already."""
    g.n(p + "pk", "call_self", function="Sh Peek"); g.call(p + "isc", K_MATH, "EqualEqual_IntInt", inp={"A": "@%spk.kind" % p, "B": str(T[close_kind])})
    g.get(p + "ok", "ShOk"); g.call(p + "nok", K_MATH, "Not_PreBool", inp={"A": "@%sok.ShOk" % p}); g.call(p + "stop", K_MATH, "BooleanOR", inp={"A": "@%sisc.ReturnValue" % p, "B": "@%snok.ReturnValue" % p})
    g.branch(p + "bs", "@%sstop.ReturnValue" % p); g.n(p + "nx", "call_self", function="Sh Next")


def comma(g, p, after):
    """After an element: a comma is consumed. Returns the exec id that starts it (chain `after` into it)."""
    g.n(p + "pk2", "call_self", function="Sh Peek"); g.call(p + "isco", K_MATH, "EqualEqual_IntInt", inp={"A": "@%spk2.kind" % p, "B": str(T[","])}); g.branch(p + "bc", "@%sisco.ReturnValue" % p)
    g.n(p + "nx2", "call_self", function="Sh Next"); g.chain(after, p + "bc", p + "nx2")


def obj_loop(g, p, cases):
    """{ key: value, ... }: cases = [(key, builder(g, prefix) -> (head, tail))]; other keys are skipped. Returns (head, tail)."""
    g.n(p + "op", "call_self", function="Sh Expect", inp={"kind": str(T["{"])})
    g.n(p + "fl", "macro", name="ForLoopWithBreak", inp={"First Index": "0", "Last Index": str(sf.MAX_FIELDS)}); stop_or_close(g, p, "}")
    g.n(p + "k", "call_self", function="Sh R Str"); g.n(p + "co", "call_self", function="Sh Expect", inp={"kind": str(T[":"])}); g.n(p + "after", "call_self", function="Sh Noop")
    prev = p + "co"
    for i, (key, build) in enumerate(cases):
        g.call(p + "ke%d" % i, K_STR, "EqualEqual_StrStr", inp={"A": "@%sk.s" % p, "B": key}); g.branch(p + "kb%d" % i, "@%ske%d.ReturnValue" % (p, i)); g.chain(prev, p + "kb%d" % i)
        h, t = build(g, "%sc%d_" % (p, i)); g.chain(p + "kb%d" % i, h); g.chain(t, p + "after"); prev = p + "kb%d:else" % i
    g.n(p + "sk", "call_self", function="Sh Skip Value"); g.chain(prev, p + "sk", p + "after"); comma(g, p, p + "after")
    g.chain(p + "op", p + "fl"); g.chain(p + "fl", p + "bs", p + "nx", p + "fl:Break"); g.chain(p + "bs:else", p + "k", p + "co")
    return p + "op", p + "fl:Completed"


def list_loop(g, p, elem):
    """[ value, ... ] with elem(g, prefix) -> (head, tail) per element. Returns (head, tail)."""
    g.n(p + "op", "call_self", function="Sh Expect", inp={"kind": str(T["["])})
    g.n(p + "fl", "macro", name="ForLoopWithBreak", inp={"First Index": "0", "Last Index": str(sf.MAX_LIST)}); stop_or_close(g, p, "]")
    h, t = elem(g, p + "e_"); comma(g, p, t)
    g.chain(p + "op", p + "fl"); g.chain(p + "fl", p + "bs", p + "nx", p + "fl:Break"); g.chain(p + "bs:else", h)
    return p + "op", p + "fl:Completed"


def call_step(fn_name, **inp):
    def b(g, p): g.n(p + "c", "call_self", function=fn_name, inp=inp); return p + "c", p + "c"
    return b


def read_into(var_name, conv=None):
    """Sh R Str (or Num with conv='round') into a Manager variable."""
    def b(g, p):
        if conv == "round":
            g.n(p + "r", "call_self", function="Sh R Num"); g.call(p + "rd", K_MATH, "Round", inp={"A": "@%sr.n" % p}); val = "@%srd.ReturnValue" % p
        else:
            g.n(p + "r", "call_self", function="Sh R Str"); val = "@%sr.s" % p
        g.set(p + "s", var_name, inp={var_name: val}); g.chain(p + "r", p + "s"); return p + "r", p + "s"
    return b


def mark_and_skip(pos_var):
    """Remember where a value starts (read later, when the whole entry is known) and skip it for now."""
    def b(g, p):
        g.get(p + "g", "ShPos"); g.set(p + "s", pos_var, inp={pos_var: "@%sg.ShPos" % p}); g.n(p + "k", "call_self", function="Sh Skip Value"); g.chain(p + "s", p + "k"); return p + "s", p + "k"
    return b


def f_share_read_mods():
    def entry_(g, p):
        g.n(p + "k", "call_self", function="Sh R Str"); g.n(p + "co", "call_self", function="Sh Expect", inp={"kind": str(T[":"])}); g.n(p + "v", "call_self", function="Sh R Str")
        g.call(p + "kn", K_STR, "Conv_StringToName", inp={"InString": "@%sk.s" % p}); g.get(p + "gm", "ShModNames")
        g.call(p + "add", K_MAP, "Map_Add", inp={"TargetMap": "@%sgm.ShModNames" % p, "Key": "@%skn.ReturnValue" % p, "Value": "@%sv.s" % p}); g.chain(p + "k", p + "co", p + "v", p + "add"); return p + "k", p + "add"
    # an object of pak -> caption: the generic object loop reads the key itself, so walk it by hand with the same parts
    g = G(); g.n("op", "call_self", function="Sh Expect", inp={"kind": str(T["{"])})
    g.n("fl", "macro", name="ForLoopWithBreak", inp={"First Index": "0", "Last Index": str(sf.MAX_LIST)}); stop_or_close(g, "", "}")
    h, t = entry_(g, "e_"); comma(g, "", t)
    g.chain("entry", "op", "fl"); g.chain("fl", "bs", "nx", "fl:Break"); g.chain("bs:else", h)
    return fn("Share Read Mods", graph=g)


def f_share_read_ref():
    g = G(); resets = []
    for v in ("ShRType", "ShRItem", "ShRLabel", "ShRMod"): g.set("z" + v, v, inp={v: ""}); resets.append("z" + v)
    h, t = obj_loop(g, "o_", [("type", read_into("ShRType")), ("item", read_into("ShRItem")), ("label", read_into("ShRLabel")), ("mod", read_into("ShRMod"))])
    pins = {}
    for v in ("ShRType", "ShRItem", "ShRMod"):
        g.get("g" + v, v); g.call("n" + v, K_STR, "Conv_StringToName", inp={"InString": "@g%s.%s" % (v, v)}); pins[v] = "@n%s.ReturnValue" % v
    g.get("gen", "ShEntryName"); g.get("glb", "ShRLabel")
    g.make("mk", S_SHAREREF, Entry="@gen.ShEntryName", Type=pins["ShRType"], Item=pins["ShRItem"], Label="@glb.ShRLabel", Mod=pins["ShRMod"])
    g.get("gr", "ShRefs"); g.call("add", K_ARR, "Array_Add", inp={"TargetArray": "@gr.ShRefs", "NewItem": "@mk.S_ShareRef"})
    g.chain("entry", *resets, h); g.chain(t, "add")
    return fn("Share Read Ref", graph=g)


def f_share_read_refs():
    g = G(); h, t = list_loop(g, "l_", call_step("Share Read Ref")); g.chain("entry", h); return fn("Share Read Refs", graph=g)


# kind -> (schema reader, struct of the staging list, staging variable, schema); look and outfit are built by hand below
KIND_STAGING = [("face", "Face", "/Game/Mod/AltUI/S_Face", "ShFaces", sf.FACE_SCHEMA), ("appearance", "App", S_SHAREAPP, "ShApps", sf.APP_SCHEMA),
                ("bodypreset", "BodyP", "/Game/Mod/AltUI/S_BodyPreset", "ShBodyPresets", sf.BODYP_SCHEMA), ("modpreset", "ModP", "/Game/Mod/AltUI/S_ModPreset", "ShModPresets", sf.MODP_SCHEMA)]


def f_share_read_entry():
    """One entry: kind and name may come after data / refs, so data and refs are only marked on the first pass and read once
    the object is through (ShPos set back to them, then to the end of the object). Every known kind goes into its staging list
    with the entry's name; an unknown one is counted (ShUnknown) and its references are not read."""
    g = G(); resets = []
    for v, d in (("ShKind", ""), ("ShEntryName", ""), ("ShDataPos", "-1"), ("ShRefsPos", "-1")): g.set("z" + v, v, inp={v: d}); resets.append("z" + v)
    h, t = obj_loop(g, "o_", [("kind", read_into("ShKind")), ("name", read_into("ShEntryName")), ("data", mark_and_skip("ShDataPos")), ("refs", mark_and_skip("ShRefsPos"))])
    g.get("gp", "ShPos"); g.set("se", "ShEndPos", inp={"ShEndPos": "@gp.ShPos"})
    g.get("gd", "ShDataPos"); g.call("hd", K_MATH, "GreaterEqual_IntInt", inp={"A": "@gd.ShDataPos", "B": "0"}); g.branch("bhd", "@hd.ReturnValue")
    g.get("gk", "ShKind"); g.n("refs", "call_self", function="Sh Noop")   # every known kind ends here, then its references
    def kind_branch(k, i):
        g.call("ik%d" % i, K_STR, "EqualEqual_StriStri", inp={"A": "@gk.ShKind", "B": k}); g.branch("bk%d" % i, "@ik%d.ReturnValue" % i)
        g.get("gdp%d" % i, "ShDataPos"); g.set("sp%d" % i, "ShPos", inp={"ShPos": "@gdp%d.ShDataPos" % i}); return "bk%d" % i, "sp%d" % i
    # look
    bl, pl = kind_branch("look", 0); g.n("rs", "call_self", function="Sh R Snap")
    g.get("gen", "ShEntryName"); g.make("mkl", S_LOOK_PATH, Name="@gen.ShEntryName", Id="0", Snap="@rs.v")
    g.get("gl", "ShLooks"); g.call("al", K_ARR, "Array_Add", inp={"TargetArray": "@gl.ShLooks", "NewItem": "@mkl.S_Look"}); g.chain(bl, pl, "rs", "al", "refs")
    # outfit
    bo, po = kind_branch("outfit", 1); g.n("ro", "call_self", function="Sh R Outfit"); g.brk("bo2", S_SHAREOUTFIT, "@ro.v")
    g.get("gen2", "ShEntryName"); g.make("mko", S_SHAREOUTFIT, Name="@gen2.ShEntryName", Pieces="@bo2.Pieces", SlotColors="@bo2.SlotColors")
    g.get("go", "ShOutfits"); g.call("ao", K_ARR, "Array_Add", inp={"TargetArray": "@go.ShOutfits", "NewItem": "@mko.S_ShareOutfit"}); g.chain(bo, po, "ro", "ao", "refs"); g.chain(bl + ":else", bo)
    prev = bo + ":else"
    for i, (kind, sname, path, var_, sch) in enumerate(KIND_STAGING, start=2):
        b, sp = kind_branch(kind, i); g.n("r%d" % i, "call_self", function="Sh R " + sname); g.brk("b%d" % i, path, "@r%d.v" % i)
        g.get("en%d" % i, "ShEntryName"); fields = {f: "@b%d.%s" % (i, f) for f, _ in sch}
        g.make("mk%d" % i, path, Name="@en%d.ShEntryName" % i, **fields)
        g.get("gs%d" % i, var_); g.call("a%d" % i, K_ARR, "Array_Add", inp={"TargetArray": "@gs%d.%s" % (i, var_), "NewItem": "@mk%d.%s" % (i, path.rsplit("/", 1)[1])})
        g.chain(prev, b); g.chain(b, sp, "r%d" % i, "a%d" % i, "refs"); prev = b + ":else"
    g.get("gu", "ShUnknown"); g.call("ui", K_MATH, "Add_IntInt", inp={"A": "@gu.ShUnknown", "B": "1"}); g.set("su", "ShUnknown", inp={"ShUnknown": "@ui.ReturnValue"})
    g.get("gr", "ShRefsPos"); g.call("hr", K_MATH, "GreaterEqual_IntInt", inp={"A": "@gr.ShRefsPos", "B": "0"}); g.branch("bhr", "@hr.ReturnValue")
    g.get("gr2", "ShRefsPos"); g.set("pr", "ShPos", inp={"ShPos": "@gr2.ShRefsPos"}); g.n("rr", "call_self", function="Share Read Refs")
    g.get("ge", "ShEndPos"); g.set("pe", "ShPos", inp={"ShPos": "@ge.ShEndPos"})
    g.chain("entry", *resets, h); g.chain(t, "se", "bhd", bl); g.chain(prev, "su", "pe"); g.chain("bhd:else", "su")
    g.chain("refs", "bhr", "pr", "rr", "pe"); g.chain("bhr:else", "pe")
    return fn("Share Read Entry", graph=g)


def f_share_read_entries():
    g = G(); h, t = list_loop(g, "l_", call_step("Share Read Entry")); g.chain("entry", h); return fn("Share Read Entries", graph=g)


def f_share_parse():
    """Whole document into ShLooks / ShOutfits / ShRefs / ShModNames; unknown kinds counted (ShUnknown). Header after the object
    (keys in any order): "altui" must be FORMAT, "version" at most VERSION. Nothing is applied here."""
    g = G(); clears = []
    for v, cont in (("ShLooks", "a"), ("ShOutfits", "a"), ("ShRefs", "a"), ("ShModNames", "m"), ("ShFaces", "a"), ("ShApps", "a"), ("ShBodyPresets", "a"), ("ShModPresets", "a")):
        g.get("g" + v, v)
        if cont == "m": g.call("c" + v, K_MAP, "Map_Clear", inp={"TargetMap": "@g%s.%s" % (v, v)})
        else: g.call("c" + v, K_ARR, "Array_Clear", inp={"TargetArray": "@g%s.%s" % (v, v)})
        clears.append("c" + v)
    g.set("su", "ShUnknown", inp={"ShUnknown": "0"}); g.set("sfm", "ShFormat", inp={"ShFormat": ""}); g.set("sv0", "ShVersion", inp={"ShVersion": "0"})
    g.n("tk", "call_self", function="Share Tokenize", inp={"text": "@entry.text"}); g.branch("btk", "@tk.ok"); g.set("sp", "ShPos", inp={"ShPos": "0"})
    h, t = obj_loop(g, "d_", [("altui", read_into("ShFormat")), ("version", read_into("ShVersion", "round")), ("entries", call_step("Share Read Entries")), ("mods", call_step("Share Read Mods"))])
    g.get("gok", "ShOk"); g.branch("bok", "@gok.ShOk")
    g.get("gf", "ShFormat"); g.call("fok", K_STR, "EqualEqual_StrStr", inp={"A": "@gf.ShFormat", "B": sf.FORMAT}); g.branch("bf", "@fok.ReturnValue")
    g.n("ff", "call_self", function="Sh Fail", inp={"key": "Share_ErrFormat", "pos": "0"})
    g.get("gv", "ShVersion"); g.call("vok", K_MATH, "LessEqual_IntInt", inp={"A": "@gv.ShVersion", "B": str(sf.VERSION)}); g.branch("bv", "@vok.ReturnValue")
    g.n("fv", "call_self", function="Sh Fail", inp={"key": "Share_ErrVersion", "pos": "0"})
    g.chain("entry", *clears, "su", "sfm", "sv0", "tk", "btk"); g.chain("btk", "sp", h); g.chain("btk:else", "return")
    g.chain(t, "bok", "bf", "bv", "return"); g.chain("bok:else", "return"); g.chain("bf:else", "ff", "return"); g.chain("bv:else", "fv", "return")
    g.get("rok", "ShOk"); g.link("rok.ShOk", "return.ok")
    return fn("Share Parse", [param("text", "string")], [param("ok", "bool")], graph=g)


def document_functions():
    return [f_share_read_mods(), f_share_read_ref(), f_share_read_refs(), f_share_read_entry(), f_share_read_entries(), f_share_parse()]


DOCUMENT_SIGNATURES = [fn(n) for n in ("Share Read Mods", "Share Read Ref", "Share Read Refs", "Share Read Entry", "Share Read Entries")] + \
                      [fn("Share Parse", [param("text", "string")], [param("ok", "bool")])] + \
                      [fn("Share Begin"), fn("Share Add Look", [param("index", "int")]), fn("Share Look Snap", [param("snap", "struct:" + S_SNAP_PATH)], [param("shared", "struct:" + S_SNAP_PATH)]), fn("Share Add Outfit", [param("index", "int")]), fn("Share End", [], [param("text", "string")]),
                       fn("Share Ref Exists", [param("type", "name"), param("item", "name")], [param("yes", "bool")]), fn("Share Missing", [param("type", "name"), param("item", "name")], [param("yes", "bool")]),
                       fn("Share Check", [], [param("summary", "text"), param("missing", "int"), param("left", "int")]), fn("Share Drop Existing"), fn("Share Scan Pieces"), fn("Share Has Ref", [param("type", "name"), param("item", "name")], [param("yes", "bool")]), fn("Share Outfit Data", [param("index", "int")], [param("v", "struct:" + S_SHAREOUTFIT)]), fn("Share Free Icon Number", [], [param("number", "int")]), fn("Share Body Caption", [param("body", "name")], [param("s", "string")], pure=True), fn("Share Page Keys"), fn("Share Add Mod Preset At", [param("pak", "name"), param("index", "int")]), fn("Share Tick", [param("key", "string")]), fn("Share Tick Kind", [param("kind", "string"), param("on", "bool")]), fn("Share Selected Text", [], [param("text", "string")]), fn("Share Export Selected"), fn("Rebuild Share Page"), fn("Share Import", [param("drop_missing", "bool"), param("save", "bool")], [param("looks", "int"), param("outfits", "int")]),
                       fn("Open Share Export", [param("text", "string")]), fn("Open Share Import"), fn("Share Check Click"), fn("Share Import All"), fn("Share Import Clean"), fn("Share Close"),
                       fn("Share Export Look", [param("index", "int")]), fn("Share Export Outfit", [param("index", "int")])] + \
                      [fn("Share Add " + k, [param("index", "int")]) for k in ("Face", "Appearance", "Body Preset", "Mod Preset")] + \
                      [fn("Share Export " + k, [param("index", "int")]) for k in ("Face", "Appearance", "Body Preset", "Mod Preset")]   # gen_manager_ui
DOCUMENT_VARS = [var("ShDupN", "name", "map", value_type="int"), var("ShDupNames", "string", "array"), var("ShDupShown", "string", "array"), var("ShKeepNames", "string", "array"), var("ShDupIdx", "int", "array"),
                 var("ShHave", "string", "array"), var("ShCanon", "string"), var("ShLeft", "int"), var("ShUnowned", "string", "array"), var("ShHasRef", "bool"),
                 var("ShLooks", "struct:" + S_LOOK_PATH, "array"), var("ShOutfits", "struct:" + S_SHAREOUTFIT, "array"), var("ShRefs", "struct:" + S_SHAREREF, "array"),
                 var("ShModNames", "name", "map", value_type="string"), var("ShUnknown", "int"), var("ShExpMods", "name", "array"), var("ShEntryName", "string"),
                 var("ShKind", "string"), var("ShFormat", "string"), var("ShVersion", "int"), var("ShDataPos", "int"), var("ShRefsPos", "int"), var("ShEndPos", "int"),
                 var("ShRefStart", "int"), var("ShEntries", "int"), var("ShRType", "string"), var("ShRItem", "string"), var("ShRLabel", "string"), var("ShRMod", "string"),
                 var("ShExists", "bool"), var("ShMissFlag", "bool"), var("ShMissMods", "name", "array"), var("ShMissItems", "name", "map", value_type="string"),
                 var("ShMissIn", "name", "map", value_type="string"), var("ShMissSeen", "string", "array"), var("ShMissN", "int"), var("ShLines", "string", "array"), var("ShSummary", "string"),
                 var("ShImpL", "int"), var("ShImpO", "int"), var("ShImpSnap", "struct:" + S_SNAP_PATH), var("ShImpPieces", "name", "map", value_type=S_COLOR),
                 var("ShImpSC", "name", "map", value_type=S_LINCOLOR),
                 var("ShLkSlot", "name", "map", value_type=S_LINCOLOR), var("ShLkMk", "name", "map", value_type=S_LINCOLOR), var("ShLkRows", "name", "array"), var("ShLkSnap", "struct:" + S_SNAP_PATH),
                 *[var(v, "struct:" + path, "array") for _, _, path, v, _ in KIND_STAGING], var("ShParts", "string", "array"), var("ShImpN", "name", "map", value_type="int"),
                 var("ShImpApp", "struct:" + S_SHAREAPP), var("ShImpPaks", "name", "array"), var("ShImpPak", "name"), var("ShImpRow", "name"), var("ShIconN", "int"), var("ShIconUsed", "bool"),
                 var("ShPageKeys", "string", "array"), var("ShPageNames", "string", "array"), var("ShPageSubs", "string", "array"), var("ShPageKinds", "name", "map", value_type="int"), var("ShPagePaks", "name", "array"),
                 var("ShareSel", "string", "array"), var("ShPageRows", "string", "map", value_type="object:/Script/UMG.UserWidget"), var("ShShareKey", "name")]


SIGNATURES = [fn("Share Tokenize", [param("text", "string")], [param("ok", "bool")]),
              fn("Sh Emit", [param("kind", "int"), param("s", "string"), param("n", "float"), param("pos", "int")]),
              fn("Sh Fail", [param("key", "string"), param("pos", "int")]), fn("Sh Tok In", [param("seg", "string")]), fn("Sh Tok Out", [param("seg", "string")]),
              fn("Sh Unescape", [param("s", "string")], [param("out", "string")], pure=True), fn("Sh Tok Piece", [param("p", "string"), param("pos", "int")]),
              fn("Sh Tok Value", [param("v", "string"), param("pos", "int")], [param("len", "int")])] + PRIMITIVE_SIGNATURES + SCHEMA_SIGNATURES + DOCUMENT_SIGNATURES
