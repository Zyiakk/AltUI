"""Oodle decoding through the native ooz library (https://github.com/powzix/ooz, GPL-3) via ctypes – dev-repo accelerator only.

pak11_extract.oodle() uses this when the library is around (about 100x faster than the pure-Python scripts/oodle_kraken.py,
which matters for the pak tooling: mod_inventory, pakbuild, jodiskins_build, verify_pak) and falls back to oodle_kraken
otherwise. scripts/bodypak_dist.sh does not copy this module: bodypak.pyz ships without ctypes and without any native
file (the bundled DLL was flagged as a trojan in 1.3.1).

Library lookup: $OOZ, then tools/ooz/libooz.so (tools/fetch_ooz.sh) / tools/ooz/ooz.dll next to the repo.
"""
import os, sys
from oodle_kraken import OodleError

_lib = None   # None: not looked up yet; False: no library found


def find_lib():
    here = os.path.dirname(os.path.abspath(__file__))
    name = "ooz.dll" if sys.platform == "win32" else "libooz.so"
    for c in (os.environ.get("OOZ"), os.path.join(here, "..", "tools", "ooz", name)):
        if c and os.path.exists(c):
            return c
    return None


def _load():
    global _lib
    if _lib is None:
        p = find_lib()
        if p:
            import ctypes
            _lib = ctypes.CDLL(p)
            _lib.ooz_decompress.restype = ctypes.c_int
            _lib.ooz_decompress.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t]
        else:
            _lib = False
    return _lib


def available():
    return bool(_load())


def decompress(src, usz):
    """One Oodle block -> its |usz| uncompressed bytes through ooz; OodleError when ooz rejects the data."""
    import ctypes
    lib = _load()
    if not lib:
        raise OodleError("ooz library not found (tools/fetch_ooz.sh or $OOZ)")
    out = ctypes.create_string_buffer(usz + 64)
    r = lib.ooz_decompress(bytes(src), len(src), out, usz)
    if r != usz:
        raise OodleError("ooz rejected the block (%d/%d bytes)" % (r, usz))
    return out.raw[:usz]
