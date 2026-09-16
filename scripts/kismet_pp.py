#!/usr/bin/env python3
"""Prints UAssetAPI KismetSerializer JSON (scratch bpdump) as pseudocode: one statement per line with offset."""
import json, sys


def ex(e):
    if e is None: return "?"
    if not isinstance(e, dict): return json.dumps(e, ensure_ascii=False)
    i = e.get("Inst", "?")
    if i in ("LocalVariable", "InstanceVariable", "DefaultVariable", "LocalOutVariable", "ClassSparseDataVariable"):
        return e.get("Variable Name", "?")
    if i in ("True", "False", "Self", "Nothing", "NoObject", "EndOfScript"): return i.lower()
    if i in ("IntConst", "ByteConst", "IntConstByte", "FloatConst", "Int64Const", "UInt64Const"): return str(e.get("Value"))
    if i in ("StringConst", "UnicodeStringConst", "NameConst"): return json.dumps(e.get("Value"), ensure_ascii=False)
    if i == "TextConst": return "T" + json.dumps(str(e.get("Value") or e.get("SourceString") or e), ensure_ascii=False)[:60]
    if i == "ObjectConst": return "obj:" + str(e.get("Object") or e.get("Value")).rsplit("/", 1)[-1]
    if i == "Context" or i == "Context_FailSilent" or i == "ClassContext":
        return ex(e.get("Context") or e.get("ObjectExpression")) + "." + ex(e.get("Expression") or e.get("ContextExpression"))
    if i in ("CallMath", "LocalFinalFunction", "FinalFunction", "VirtualFunction", "LocalVirtualFunction", "CallMulticastDelegate"):
        f = e.get("FunctionName") or e.get("Function") or e.get("Delegate") or "?"
        if isinstance(f, dict): f = f.get("MemberName") or f.get("Function") or str(f)
        return "%s(%s)" % (f, ", ".join(ex(p) for p in e.get("Parameters", [])))
    if i in ("Let", "LetBool", "LetObj", "LetWeakObjPtr", "LetDelegate", "LetMulticastDelegate", "LetValueOnPersistentFrame"):
        return "%s = %s" % (ex(e.get("Variable")), ex(e.get("Expression")))
    if i == "Jump": return "goto %s" % e.get("Offset", e.get("CodeOffset"))
    if i == "JumpIfNot": return "if not %s goto %s" % (ex(e.get("Condition") or e.get("BooleanExpression")), e.get("Offset", e.get("CodeOffset")))
    if i == "ComputedJump": return "goto *%s" % ex(e.get("OffsetExpression"))
    if i == "PushExecutionFlow": return "push %s" % e.get("PushingAddress", e.get("Offset"))
    if i == "PopExecutionFlow": return "pop"
    if i == "PopExecutionFlowIfNot": return "if not %s pop" % ex(e.get("Condition") or e.get("BooleanExpression"))
    if i == "Return": return "return " + ex(e.get("Expression") or e.get("ReturnExpression"))
    if i == "StructMemberContext": return ex(e.get("StructExpression")) + "." + str(e.get("Property", {}).get("MemberName") if isinstance(e.get("Property"), dict) else e.get("Property"))
    if i in ("StructConst", "SetArray", "ArrayConst", "SetSet", "SetMap", "MapConst", "SetConst"):
        return "%s[%s]" % (i, ", ".join(ex(p) for p in (e.get("Value") or e.get("Elements") or [])))
    if i in ("Cast", "PrimitiveCast", "DynamicCast", "ObjToInterfaceCast", "MetaCast", "InterfaceToObjCast", "CrossInterfaceCast"):
        return "cast<%s>(%s)" % (e.get("ClassPtr") or e.get("ConversionType"), ex(e.get("Target")))
    if i == "SwitchValue": return "switch(%s){%s}" % (ex(e.get("IndexTerm")), "; ".join("%s:%s" % (ex(c.get("CaseIndexValueTerm")), ex(c.get("CaseTerm"))) for c in e.get("Cases", [])) + " default:" + ex(e.get("DefaultTerm")))
    if i == "Skip": return ex(e.get("SkipExpression") or e.get("Expression"))
    if i == "VariableBase" or "Variable Name" in e: return e.get("Variable Name", "?")
    if i == "InterfaceContext": return ex(e.get("InterfaceValue"))
    if i in ("Assert", "Breakpoint", "Tracepoint", "WireTracepoint", "InstrumentationEvent", "DebugInfo"): return ""
    if i == "AddMulticastDelegate": return "%s += %s" % (ex(e.get("Delegate")), ex(e.get("DelegateToAdd")))
    if i == "RemoveMulticastDelegate": return "%s -= %s" % (e.get("Delegate") and ex(e.get("Delegate")), ex(e.get("DelegateToAdd")))
    if i == "BindDelegate": return "bind %s -> %s.%s" % (ex(e.get("Delegate")), ex(e.get("ObjectTerm")), e.get("FunctionName"))
    if i == "ClearMulticastDelegate": return "clear %s" % ex(e.get("DelegateToClear"))
    if i == "InstanceDelegate": return "delegate:" + str(e.get("FunctionName"))
    if i == "ArrayGetByRef": return "%s[%s]" % (ex(e.get("ArrayVariable")), ex(e.get("ArrayIndex")))
    if i in ("RotationConst", "VectorConst", "TransformConst", "Vector3fConst"): return i + str(e.get("Value"))
    if i == "SoftObjectConst": return "soft:" + ex(e.get("Value"))
    if i in ("EndFunctionParms", "EndArray", "EndStructConst", "EndMap", "EndSet", "EndArrayConst", "EndSetConst", "EndMapConst"): return ""
    return i + "{" + ",".join("%s=%s" % (k, ex(v) if isinstance(v, dict) else str(v)[:40]) for k, v in e.items() if k not in ("Inst", "StatementIndex")) + "}"


def main(path, fns):
    d = json.load(open(path))
    for name, stmts in d.items():
        if fns and not any(f.lower() in name.lower() for f in fns): continue
        print("==== " + name)
        for s in stmts:
            t = ex(s)
            if t: print("%6s  %s" % (s.get("StatementIndex", ""), t))


if __name__ == "__main__": main(sys.argv[1], sys.argv[2:])
