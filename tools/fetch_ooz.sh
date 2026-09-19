#!/bin/bash
# Fetches powzix/ooz (GPL-3, open-source Oodle decompressor) into tools/ooz and builds libooz.so with a C export
# `ooz_decompress` (the Windows command-line part of kraken.cpp is cut off). Needed only by scripts/pak11_extract.py
# for Oodle-compressed paks (body-pak conversion: reading the mesh's imports, test_bodypak); everything else works without it.
set -e; cd "$(dirname "$0")"
[ -f ooz/kraken.cpp ] || git clone --depth 1 https://github.com/powzix/ooz.git ooz
cd ooz
n=$(grep -n "typedef int WINAPI OodLZ_CompressFunc" kraken.cpp | cut -d: -f1); [ -n "$n" ] || { echo "kraken.cpp: marker not found"; exit 1; }
head -n $((n - 1)) kraken.cpp > kraken_lib.cpp
echo 'extern "C" int ooz_decompress(const unsigned char *src, size_t src_len, unsigned char *dst, size_t dst_len) { return Kraken_Decompress(src, src_len, dst, dst_len); }' >> kraken_lib.cpp
g++ -O2 -shared -fPIC -o libooz.so kraken_lib.cpp bitknit.cpp lzna.cpp && echo "built tools/ooz/libooz.so"
# Windows x64 DLL for bodypak.pyz, cross-compiled with zig (`pip install ziglang` or a zig on PATH); verified under Proton's wine (test_bodypak)
if python3 -c "import ziglang" 2>/dev/null; then ZIG="python3 -m ziglang"; elif command -v zig >/dev/null; then ZIG=zig; else echo "no zig -> tools/ooz/ooz.dll not built (needed by scripts/bodypak_dist.sh)"; exit 0; fi
$ZIG c++ -target x86_64-windows-gnu -O2 -shared -o ooz.dll kraken_lib.cpp bitknit.cpp lzna.cpp 2>/dev/null && echo "built tools/ooz/ooz.dll"
