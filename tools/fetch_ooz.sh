#!/bin/bash
# Fetches powzix/ooz (GPL-3, open-source Oodle decompressor) into tools/ooz and builds libooz.so with a C export
# `ooz_decompress` (the Windows command-line part of kraken.cpp is cut off; upstream's stdafx.h needs Windows headers and is
# replaced by stdafx_linux.h). Test tool only: tests/unit/test_kraken.py compares the pure-Python decoder
# (scripts/oodle_kraken.py) against it. Nothing at runtime needs it.
set -e; cd "$(dirname "$0")"
[ -f ooz/kraken.cpp ] || git clone --depth 1 https://github.com/powzix/ooz.git ooz
cd ooz
cat > stdafx_linux.h <<'H'
#pragma once
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <assert.h>
#include <x86intrin.h>
typedef unsigned char byte; typedef unsigned char uint8; typedef unsigned int uint32; typedef uint64_t uint64;
typedef int64_t int64; typedef signed int int32; typedef unsigned short uint16; typedef signed short int16; typedef unsigned int uint;
#define __forceinline inline __attribute__((always_inline))
static inline unsigned char _BitScanReverse(unsigned long *i, unsigned long x) { if (!x) return 0; *i = 31 - __builtin_clz(x); return 1; }
static inline unsigned char _BitScanForward(unsigned long *i, unsigned long x) { if (!x) return 0; *i = __builtin_ctz(x); return 1; }
#define _byteswap_ushort __builtin_bswap16
#define _byteswap_ulong __builtin_bswap32
#define _byteswap_uint64 __builtin_bswap64
H
n=$(grep -n "typedef int WINAPI OodLZ_CompressFunc" kraken.cpp | cut -d: -f1); [ -n "$n" ] || { echo "kraken.cpp: marker not found"; exit 1; }
head -n $((n - 1)) kraken.cpp | sed 's/#include "stdafx.h"/#include "stdafx_linux.h"/' > kraken_lib.cpp
echo 'extern "C" int ooz_decompress(const unsigned char *src, size_t src_len, unsigned char *dst, size_t dst_len) { return Kraken_Decompress(src, src_len, dst, dst_len); }' >> kraken_lib.cpp
for f in bitknit lzna; do sed 's/#include "stdafx.h"/#include "stdafx_linux.h"/' $f.cpp > ${f}_lib.cpp; done
g++ -O2 -shared -fPIC -o libooz.so kraken_lib.cpp bitknit_lib.cpp lzna_lib.cpp && echo "built tools/ooz/libooz.so"
