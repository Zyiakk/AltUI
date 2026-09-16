"""Helpers for editor Python tests (output via unreal.log_warning so it shows up in the commandlet log)."""
import unreal, traceback

def report(name, ok, detail=""):
    unreal.log_warning("EDTEST %s %s%s" % ("PASS" if ok else "FAIL", name, (": " + str(detail)) if detail else ""))
    return ok

def expect(name, actual, expected):
    return report(name, actual == expected, "" if actual == expected else "got %r expected %r" % (actual, expected))

def run(fn):
    try:
        fn()
    except Exception:
        unreal.log_warning("EDTEST FAIL exception: " + traceback.format_exc().replace("\n", " | "))



def cdo(class_path):
    """Class Default Object of a Blueprint class (for logic tests without a world; actor spawn crashes in the commandlet)."""
    cls = unreal.load_class(None, class_path)
    obj = unreal.get_default_object(cls)
    unreal.log_warning("EDTEST step cdo %s" % obj)
    return obj
