"""Pure-Python decoder for Oodle Kraken data (as written by UnrealPak with -compressionformats=Oodle).

Derived from kraken.cpp of ooz (https://github.com/powzix/ooz), Copyright (C) 2016 Powzix, an open-source Oodle
decompressor released under the GNU General Public License v3.0 or later. This port, Copyright (C) 2026 Zyiakk, is
therefore GPL-3.0-or-later as well (LICENSE-GPL-3.0.txt; the rest of AltUI is MIT). Function names follow the C source
so the two can be read side by side.

Only the Kraken path is ported (decoder type 6). Mermaid/Selkie, Leviathan, LZNA and Bitknit raise OodleError.
Standard library only, Python 3.8+.

    decompress(src, dst_size) -> bytes
"""


class OodleError(Exception):
    pass


DECODER_NAMES = {5: "LZNA", 6: "Kraken", 10: "Mermaid/Selkie", 11: "Bitknit", 12: "Leviathan"}
M32 = 0xFFFFFFFF


def _u32le(d, i):
    return d[i] | d[i + 1] << 8 | d[i + 2] << 16 | d[i + 3] << 24


def _u32be(d, i):
    return d[i] << 24 | d[i + 1] << 16 | d[i + 2] << 8 | d[i + 3]


def _rotl32(x, n):
    n &= 31
    return ((x << n) | (x >> (32 - n))) & M32 if n else x


def _clz32(x):
    """CountLeadingZeros for x != 0."""
    return 32 - x.bit_length()


# ---------------------------------------------------------------------------------------------- BitReader
class BitReader:
    """kraken.cpp BitReader: |bits| holds the unread bits at the top (MSB first), 24 - bitpos of them are valid."""
    __slots__ = ("d", "p", "p_end", "bits", "bitpos")

    def __init__(self, d, p, p_end):
        self.d = d; self.p = p; self.p_end = p_end; self.bits = 0; self.bitpos = 24

    def refill(self):
        d = self.d
        while self.bitpos > 0:
            self.bits |= (d[self.p] if self.p < self.p_end else 0) << self.bitpos
            self.bitpos -= 8; self.p += 1
        self.bits &= M32

    def refill_backwards(self):
        d = self.d
        while self.bitpos > 0:
            self.p -= 1
            self.bits |= (d[self.p] if self.p >= self.p_end else 0) << self.bitpos
            self.bitpos -= 8
        self.bits &= M32

    def read_bit(self):
        self.refill()
        return self.read_bit_no_refill()

    def read_bit_no_refill(self):
        r = self.bits >> 31
        self.bits = (self.bits << 1) & M32; self.bitpos += 1
        return r

    def read_bits_no_refill(self, n):
        r = self.bits >> (32 - n)
        self.bits = (self.bits << n) & M32; self.bitpos += n
        return r

    def read_bits_no_refill_zero(self, n):
        """n may be zero."""
        r = (self.bits >> 1) >> (31 - n)
        self.bits = (self.bits << n) & M32; self.bitpos += n
        return r

    def read_more_than_24_bits(self, n):
        if n <= 24:
            rv = self.read_bits_no_refill_zero(n)
        else:
            rv = self.read_bits_no_refill(24) << (n - 24)
            self.refill()
            rv += self.read_bits_no_refill(n - 24)
        self.refill()
        return rv

    def read_more_than_24_bits_b(self, n):
        if n <= 24:
            rv = self.read_bits_no_refill_zero(n)
        else:
            rv = self.read_bits_no_refill(24) << (n - 24)
            self.refill_backwards()
            rv += self.read_bits_no_refill(n - 24)
        self.refill_backwards()
        return rv

    def read_fluff(self, num_symbols):
        """BitReader_ReadFluff"""
        if num_symbols == 256:
            return 0
        x = 257 - num_symbols
        if x > num_symbols:
            x = num_symbols
        x *= 2
        y = (x - 1).bit_length()
        v = self.bits >> (32 - y)
        z = (1 << y) - x
        if (v >> 1) >= z:
            self.bits = (self.bits << y) & M32; self.bitpos += y
            return v - z
        self.bits = (self.bits << (y - 1)) & M32; self.bitpos += y - 1
        return v >> 1

    def read_distance(self, v, backwards=False):
        """BitReader_ReadDistance / BitReader_ReadDistanceB"""
        refill = self.refill_backwards if backwards else self.refill
        if v < 0xF0:
            n = (v >> 4) + 4
            w = _rotl32(self.bits | 1, n); self.bitpos += n
            m = (2 << n) - 1
            self.bits = w & ~m & M32
            rv = ((w & m) << 4) + (v & 0xF) - 248
        else:
            n = v - 0xF0 + 4
            w = _rotl32(self.bits | 1, n); self.bitpos += n
            m = (2 << n) - 1
            self.bits = w & ~m & M32
            rv = 8322816 + ((w & m) << 12)
            refill()
            rv += self.bits >> 20
            self.bitpos += 12; self.bits = (self.bits << 12) & M32
        refill()
        return rv

    def read_length(self, backwards=False):
        """BitReader_ReadLength / BitReader_ReadLengthB; None on error."""
        refill = self.refill_backwards if backwards else self.refill
        if not self.bits:
            return None
        n = _clz32(self.bits)
        if n > 12:
            return None
        self.bitpos += n; self.bits = (self.bits << n) & M32
        refill()
        n += 7
        self.bitpos += n
        rv = (self.bits >> (32 - n)) - 64
        self.bits = (self.bits << n) & M32
        refill()
        return rv

    def byte_position(self):
        """Byte index of the first byte not consumed (bits->p - (24 - bits->bitpos) / 8)."""
        return self.p - ((24 - self.bitpos) >> 3)


# ------------------------------------------------------------------------------------- Golomb-Rice (BitReader2)
def _decode_golomb_rice_lengths(d, p, p_end, bitpos, n):
    """DecodeGolombRiceLengths: n unary values (number of 0 bits before a 1), MSB first, starting at bit |bitpos| of
    byte |p|. Returns (values, p, bitpos) positioned right after the 1 bit that ends the last value; None on error."""
    out = []
    count = 0
    if p >= p_end:
        return None
    while True:
        if p >= p_end:
            return None
        b = d[p]
        for bit in range(bitpos, 8):
            if (b >> (7 - bit)) & 1:
                out.append(count); count = 0
                if len(out) == n:
                    if bit == 7:
                        return out, p + 1, 0
                    return out, p, bit + 1
            else:
                count += 1
        p += 1; bitpos = 0


def _decode_golomb_rice_bits(d, p, p_end, bitpos, values, size, bitcount):
    """DecodeGolombRiceBits: values[i] = values[i] << bitcount | next |bitcount| bits (MSB first), for i < size.
    Returns (p, bitpos) after the bits; None if the buffer is too short."""
    if bitcount == 0:
        return p, bitpos
    bits_required = bitpos + bitcount * size
    if (bits_required + 7) >> 3 > p_end - p:
        return None
    acc = 0; nacc = 0; q = p
    for i in range(size):
        while nacc < bitcount + bitpos:
            acc = (acc << 8) | d[q]; q += 1; nacc += 8
        # drop the already consumed |bitpos| bits of the first byte
        if bitpos:
            acc &= (1 << (nacc - bitpos)) - 1; nacc -= bitpos; bitpos = 0
        nacc -= bitcount
        values[i] = (values[i] << bitcount) | (acc >> nacc)
        acc &= (1 << nacc) - 1
    return p + (bits_required >> 3), bits_required & 7


# ------------------------------------------------------------------------------------------------ Huffman
CODE_PREFIX_ORG = (0x0, 0x0, 0x2, 0x6, 0xE, 0x1E, 0x3E, 0x7E, 0xFE, 0x1FE, 0x2FE, 0x3FE)


def _huff_read_code_lengths_old(br, syms, code_prefix):
    """Huff_ReadCodeLengthsOld: returns the number of symbols or -1."""
    if br.read_bit_no_refill():
        sym = 0; num_symbols = 0; avg_bits_x4 = 32
        forced_bits = br.read_bits_no_refill(2)
        thres = 1 << (31 - (20 >> forced_bits))
        skip_zeros = br.read_bit()
        while True:
            if not skip_zeros:
                # run of zeros
                if not (br.bits & 0xff000000):
                    return -1
                sym += br.read_bits_no_refill(2 * (_clz32(br.bits) + 1)) - 2 + 1
                if sym >= 256:
                    break
            skip_zeros = False
            br.refill()
            if not (br.bits & 0xff000000):
                return -1
            n = br.read_bits_no_refill(2 * (_clz32(br.bits) + 1)) - 2 + 1
            if sym + n > 256:
                return -1
            br.refill()
            num_symbols += n
            while True:
                if br.bits < thres:
                    return -1
                lz = _clz32(br.bits)
                v = br.read_bits_no_refill(lz + forced_bits + 1) + ((lz - 1) << forced_bits)
                codelen = (-(v & 1) ^ (v >> 1)) + ((avg_bits_x4 + 2) >> 2)
                if codelen < 1 or codelen > 11:
                    return -1
                avg_bits_x4 = codelen + ((3 * avg_bits_x4 + 2) >> 2)
                br.refill()
                syms[code_prefix[codelen]] = sym; code_prefix[codelen] += 1; sym += 1
                n -= 1
                if not n:
                    break
            if sym == 256:
                break
        return num_symbols if (sym == 256 and num_symbols >= 2) else -1
    # sparse symbol encoding
    num_symbols = br.read_bits_no_refill(8)
    if num_symbols == 0:
        return -1
    if num_symbols == 1:
        syms[0] = br.read_bits_no_refill(8)
    else:
        codelen_bits = br.read_bits_no_refill(3)
        if codelen_bits > 4:
            return -1
        for _ in range(num_symbols):
            br.refill()
            sym = br.read_bits_no_refill(8)
            codelen = br.read_bits_no_refill_zero(codelen_bits) + 1
            if codelen > 11:
                return -1
            syms[code_prefix[codelen]] = sym; code_prefix[codelen] += 1
    return num_symbols


def _huff_convert_to_ranges(num_symbols, P, symlen, br):
    """Huff_ConvertToRanges: [(symbol, num)] or None."""
    num_ranges = P >> 1; sym_idx = 0; si = 0
    if P & 1:
        br.refill()
        v = symlen[si]; si += 1
        if v >= 8:
            return None
        sym_idx = br.read_bits_no_refill(v + 1) + (1 << (v + 1)) - 1
    syms_used = 0; ranges = []
    for _ in range(num_ranges):
        br.refill()
        v = symlen[si]
        if v >= 9:
            return None
        num = br.read_bits_no_refill_zero(v) + (1 << v)
        v = symlen[si + 1]
        if v >= 8:
            return None
        space = br.read_bits_no_refill(v + 1) + (1 << (v + 1)) - 1
        ranges.append((sym_idx, num))
        syms_used += num; sym_idx += num + space; si += 2
    if sym_idx >= 256 or syms_used >= num_symbols or sym_idx + num_symbols - syms_used > 256:
        return None
    ranges.append((sym_idx, num_symbols - syms_used))
    return ranges


def _huff_read_code_lengths_new(br, syms, code_prefix):
    """Huff_ReadCodeLengthsNew: returns the number of symbols or -1."""
    forced_bits = br.read_bits_no_refill(2)
    num_symbols = br.read_bits_no_refill(8) + 1
    fluff = br.read_fluff(num_symbols)
    p2 = br.p - ((24 - br.bitpos + 7) >> 3); bitpos2 = (br.bitpos - 24) & 7
    r = _decode_golomb_rice_lengths(br.d, p2, br.p_end, bitpos2, num_symbols + fluff)
    if r is None:
        return -1
    code_len, p2, bitpos2 = r
    code_len += [0] * 16
    r = _decode_golomb_rice_bits(br.d, p2, br.p_end, bitpos2, code_len, num_symbols, forced_bits)
    if r is None:
        return -1
    p2, bitpos2 = r
    # reset the bit reader
    br.bitpos = 24; br.p = p2; br.bits = 0
    br.refill()
    br.bits = (br.bits << bitpos2) & M32; br.bitpos += bitpos2

    running_sum = 0x1e
    for i in range(num_symbols):
        v = code_len[i]
        v = -(v & 1) ^ (v >> 1)
        code_len[i] = v + (running_sum >> 2) + 1
        if code_len[i] < 1 or code_len[i] > 11:
            return -1
        running_sum = (running_sum + v) & M32

    ranges = _huff_convert_to_ranges(num_symbols, fluff, code_len[num_symbols:], br)
    if not ranges:
        return -1
    cp = 0
    for sym, n in ranges:
        for _ in range(n):
            syms[code_prefix[code_len[cp]]] = sym; code_prefix[code_len[cp]] += 1; sym += 1; cp += 1
    return num_symbols


def _huff_make_lut(code_prefix, syms):
    """Huff_MakeLut + ReverseBitsArray2048: (bits2len, bits2sym) indexed by the next 11 stream bits (LSB first);
    None if the code is not complete."""
    bits2len = [0] * 2048; bits2sym = [0] * 2048
    currslot = 0
    for i in range(1, 11):
        start = CODE_PREFIX_ORG[i]; count = code_prefix[i] - start
        if count:
            stepsize = 1 << (11 - i); num_to_set = count << (11 - i)
            if currslot + num_to_set > 2048:
                return None
            bits2len[currslot:currslot + num_to_set] = [i] * num_to_set
            for j in range(count):
                bits2sym[currslot + j * stepsize:currslot + (j + 1) * stepsize] = [syms[start + j]] * stepsize
            currslot += num_to_set
    count = code_prefix[11] - CODE_PREFIX_ORG[11]
    if count:
        if currslot + count > 2048:
            return None
        bits2len[currslot:currslot + count] = [11] * count
        bits2sym[currslot:currslot + count] = syms[CODE_PREFIX_ORG[11]:CODE_PREFIX_ORG[11] + count]
        currslot += count
    if currslot != 2048:
        return None
    rev = _REV11
    return [bits2len[rev[i]] for i in range(2048)], [bits2sym[rev[i]] for i in range(2048)]


_REV11 = [int("{:011b}".format(i)[::-1], 2) for i in range(2048)]


def _decode_bytes_core(d, out, o, o_end, src, src_mid, src_end, bits2len, bits2sym):
    """Kraken_DecodeBytesCore: three interleaved Huffman streams, |src| and |src_mid| forwards, |src_end| backwards."""
    src_mid_org = src_mid
    src_bits = src_mid_bits = src_end_bits = 0
    src_bitpos = src_mid_bitpos = src_end_bitpos = 0
    if src > src_mid:
        return False
    if src_end - src_mid >= 4 and o_end - o >= 6:
        o_end -= 5; src_end -= 4
        while o < o_end and src <= src_mid and src_mid <= src_end:
            src_bits = (src_bits | (_u32le(d, src) << src_bitpos)) & M32
            src += (31 - src_bitpos) >> 3
            src_end_bits = (src_end_bits | (_u32be(d, src_end) << src_end_bitpos)) & M32
            src_end -= (31 - src_end_bitpos) >> 3
            src_mid_bits = (src_mid_bits | (_u32le(d, src_mid) << src_mid_bitpos)) & M32
            src_mid += (31 - src_mid_bitpos) >> 3
            src_bitpos |= 0x18; src_end_bitpos |= 0x18; src_mid_bitpos |= 0x18

            k = src_bits & 0x7FF; n = bits2len[k]; src_bits >>= n; src_bitpos -= n; out[o] = bits2sym[k]
            k = src_end_bits & 0x7FF; n = bits2len[k]; src_end_bits >>= n; src_end_bitpos -= n; out[o + 1] = bits2sym[k]
            k = src_mid_bits & 0x7FF; n = bits2len[k]; src_mid_bits >>= n; src_mid_bitpos -= n; out[o + 2] = bits2sym[k]
            k = src_bits & 0x7FF; n = bits2len[k]; src_bits >>= n; src_bitpos -= n; out[o + 3] = bits2sym[k]
            k = src_end_bits & 0x7FF; n = bits2len[k]; src_end_bits >>= n; src_end_bitpos -= n; out[o + 4] = bits2sym[k]
            k = src_mid_bits & 0x7FF; n = bits2len[k]; src_mid_bits >>= n; src_mid_bitpos -= n; out[o + 5] = bits2sym[k]
            o += 6
        o_end += 5
        src -= src_bitpos >> 3; src_bitpos &= 7
        src_end += 4 + (src_end_bitpos >> 3); src_end_bitpos &= 7
        src_mid -= src_mid_bitpos >> 3; src_mid_bitpos &= 7
    while o < o_end:
        if src_mid - src <= 1:
            if src_mid - src == 1:
                src_bits |= d[src] << src_bitpos
        else:
            src_bits |= (d[src] | d[src + 1] << 8) << src_bitpos
        k = src_bits & 0x7FF; n = bits2len[k]
        src_bitpos -= n; src_bits >>= n
        out[o] = bits2sym[k]; o += 1
        src += (7 - src_bitpos) >> 3; src_bitpos &= 7
        if o < o_end:
            if src_end - src_mid <= 1:
                if src_end - src_mid == 1:
                    src_end_bits |= d[src_mid] << src_end_bitpos
                    src_mid_bits |= d[src_mid] << src_mid_bitpos
            else:
                src_end_bits |= (d[src_end - 1] | d[src_end - 2] << 8) << src_end_bitpos
                src_mid_bits |= (d[src_mid] | d[src_mid + 1] << 8) << src_mid_bitpos
            k = src_end_bits & 0x7FF; n = bits2len[k]
            out[o] = bits2sym[k]; o += 1
            src_end_bitpos -= n; src_end_bits >>= n
            src_end -= (7 - src_end_bitpos) >> 3; src_end_bitpos &= 7
            if o < o_end:
                k = src_mid_bits & 0x7FF; n = bits2len[k]
                out[o] = bits2sym[k]; o += 1
                src_mid_bitpos -= n; src_mid_bits >>= n
                src_mid += (7 - src_mid_bitpos) >> 3; src_mid_bitpos &= 7
        if src > src_mid or src_mid > src_end:
            return False
    return src == src_mid_org and src_end == src_mid


def _decode_bytes_type12(d, src, src_size, out, output_size, typ):
    """Kraken_DecodeBytes_Type12: Huffman coded bytes, one (type 1) or two (type 2) halves of three streams each.
    Returns the bytes consumed (== src_size on success) or -1."""
    src_end = src + src_size
    br = BitReader(d, src, src_end)
    br.refill()
    code_prefix = list(CODE_PREFIX_ORG)
    syms = [0] * 1280
    if not br.read_bit_no_refill():
        num_syms = _huff_read_code_lengths_old(br, syms, code_prefix)
    elif not br.read_bit_no_refill():
        num_syms = _huff_read_code_lengths_new(br, syms, code_prefix)
    else:
        return -1
    if num_syms < 1:
        return -1
    src = br.byte_position()
    if num_syms == 1:
        out[0:output_size] = bytes([syms[0]]) * output_size
        return src - src_end
    lut = _huff_make_lut(code_prefix, syms)
    if lut is None:
        return -1
    bits2len, bits2sym = lut
    if typ == 1:
        if src + 3 > src_end:
            return -1
        split_mid = d[src] | d[src + 1] << 8; src += 2
        if not _decode_bytes_core(d, out, 0, output_size, src, src + split_mid, src_end, bits2len, bits2sym):
            return -1
    else:
        if src + 6 > src_end:
            return -1
        half = (output_size + 1) >> 1
        split_mid = d[src] | d[src + 1] << 8 | d[src + 2] << 16; src += 3
        if split_mid > src_end - src:
            return -1
        src_mid = src + split_mid
        split_left = d[src] | d[src + 1] << 8; src += 2
        if src_mid - src < split_left + 2 or src_end - src_mid < 3:
            return -1
        split_right = d[src_mid] | d[src_mid + 1] << 8
        if src_end - (src_mid + 2) < split_right + 2:
            return -1
        if not _decode_bytes_core(d, out, 0, half, src, src + split_left, src_mid, bits2len, bits2sym):
            return -1
        if not _decode_bytes_core(d, out, half, output_size, src_mid + 2, src_mid + 2 + split_right, src_end, bits2len, bits2sym):
            return -1
    return src_size


# ---------------------------------------------------------------------------------------------------- TANS
def _tans_decode_table(br, L_bits):
    """Tans_DecodeTable: (A, B) with A = symbols of weight 1, B = (symbol, weight) for weight >= 2; None on error."""
    br.refill()
    L = 1 << L_bits
    if br.read_bit_no_refill():
        Q = br.read_bits_no_refill(3)
        num_symbols = br.read_bits_no_refill(8) + 1
        if num_symbols < 2:
            return None
        fluff = br.read_fluff(num_symbols)
        p2 = br.p - ((24 - br.bitpos + 7) >> 3); bitpos2 = (br.bitpos - 24) & 7
        r = _decode_golomb_rice_lengths(br.d, p2, br.p_end, bitpos2, fluff + num_symbols)
        if r is None:
            return None
        rice, p2, bitpos2 = r
        rice += [0] * 16
        br.bitpos = 24; br.p = p2; br.bits = 0
        br.refill()
        br.bits = (br.bits << bitpos2) & M32; br.bitpos += bitpos2
        ranges = _huff_convert_to_ranges(num_symbols, fluff, rice[num_symbols:], br)
        if not ranges:
            return None
        br.refill()
        A = []; B = []; ri = 0; average = 6; somesum = 0
        for symbol, num in ranges:
            for _ in range(num):
                br.refill()
                nextra = Q + rice[ri]; ri += 1
                if nextra > 15:
                    return None
                v = br.read_bits_no_refill_zero(nextra) + (1 << nextra) - (1 << Q)
                average_div4 = average >> 2
                limit = 2 * average_div4
                if v <= limit:
                    v = average_div4 + (-(v & 1) ^ (v >> 1))
                if limit > v:
                    limit = v
                v += 1
                average += limit - average_div4
                if v == 1:
                    A.append(symbol)
                else:
                    B.append((symbol, v))
                somesum += v; symbol += 1
        if somesum != L:
            return None
        return A, B
    seen = [False] * 256
    count = br.read_bits_no_refill(3) + 1
    bits_per_sym = (L_bits.bit_length() - 1) + 1
    max_delta_bits = br.read_bits_no_refill(bits_per_sym)
    if max_delta_bits == 0 or max_delta_bits > L_bits:
        return None
    A = []; B = []; weight = 0; total_weights = 0
    for _ in range(count):
        br.refill()
        sym = br.read_bits_no_refill(8)
        if seen[sym]:
            return None
        weight += br.read_bits_no_refill(max_delta_bits)
        if weight == 0:
            return None
        seen[sym] = True
        if weight == 1:
            A.append(sym)
        else:
            B.append((sym, weight))
        total_weights += weight
    br.refill()
    sym = br.read_bits_no_refill(8)
    if seen[sym]:
        return None
    if L - total_weights < weight or L - total_weights <= 1:
        return None
    B.append((sym, L - total_weights))
    A.sort(); B.sort()
    return A, B


def _tans_init_lut(A, B, L_bits):
    """Tans_InitLut: list of (x, bits_x, symbol, w) with L entries."""
    L = 1 << L_bits
    lut = [None] * L
    slots_left = L - len(A)
    sa = slots_left >> 2
    ptr = [0, 0, 0, 0]
    sb = sa + ((slots_left & 3) > 0); ptr[1] = sb
    sb += sa + ((slots_left & 3) > 1); ptr[2] = sb
    sb += sa + ((slots_left & 3) > 2); ptr[3] = sb
    for i, sym in enumerate(A):
        lut[slots_left + i] = ((1 << L_bits) - 1, L_bits, sym, 0)
    weights_sum = 0
    for symbol, weight in B:
        if weight > 4:
            sym_bits = weight.bit_length() - 1
            Z = L_bits - sym_bits
            x = (1 << Z) - 1; bits_x = Z; w = (L - 1) & (weight << Z)
            what_to_add = 1 << Z
            X = (1 << (sym_bits + 1)) - weight
            for j in range(4):
                dst = ptr[j]
                Y = (weight + ((weights_sum - j - 1) & 3)) >> 2
                if X >= Y:
                    for _ in range(Y):
                        lut[dst] = (x, bits_x, symbol, w); dst += 1; w += what_to_add
                    X -= Y
                else:
                    for _ in range(X):
                        lut[dst] = (x, bits_x, symbol, w); dst += 1; w += what_to_add
                    Z -= 1
                    what_to_add >>= 1
                    bits_x = Z; w = 0; x >>= 1
                    for _ in range(Y - X):
                        lut[dst] = (x, bits_x, symbol, w); dst += 1; w += what_to_add
                    X = weight
                ptr[j] = dst
        else:
            bits = ((1 << weight) - 1) << (weights_sum & 3)
            bits |= bits >> 4
            ww = weight
            for _ in range(weight):
                idx = (bits & -bits).bit_length() - 1
                bits &= bits - 1
                dst = ptr[idx]; ptr[idx] += 1
                weight_bits = ww.bit_length() - 1
                lut[dst] = ((1 << (L_bits - weight_bits)) - 1, L_bits - weight_bits, symbol, (L - 1) & (ww << (L_bits - weight_bits)))
                ww += 1
        weights_sum += weight
    return lut


def _krak_decode_tans(d, src, src_size, out, dst_size):
    """Krak_DecodeTans: returns the bytes consumed (== src_size on success) or -1."""
    if src_size < 8 or dst_size < 5:
        return -1
    src_end = src + src_size
    br = BitReader(d, src, src_end)
    br.refill()
    if br.read_bit_no_refill():   # reserved
        return -1
    L_bits = br.read_bits_no_refill(2) + 8
    tab = _tans_decode_table(br, L_bits)
    if tab is None:
        return -1
    src = br.byte_position()
    if src >= src_end:
        return -1
    lut = _tans_init_lut(tab[0], tab[1], L_bits)
    L_mask = (1 << L_bits) - 1
    bits_f = _u32le(d, src); src += 4
    bits_b = _u32be(d, src_end - 4); src_end -= 4
    bitpos_f = bitpos_b = 32
    state = [0] * 5
    state[0] = bits_f & L_mask; state[1] = bits_b & L_mask
    bits_f >>= L_bits; bitpos_f -= L_bits; bits_b >>= L_bits; bitpos_b -= L_bits
    state[2] = bits_f & L_mask; state[3] = bits_b & L_mask
    bits_f >>= L_bits; bitpos_f -= L_bits; bits_b >>= L_bits; bitpos_b -= L_bits
    bits_f = (bits_f | (_u32le(d, src) << bitpos_f)) & M32
    src += (31 - bitpos_f) >> 3; bitpos_f |= 24
    state[4] = bits_f & L_mask
    bits_f >>= L_bits; bitpos_f -= L_bits
    ptr_f = src - (bitpos_f >> 3); bitpos_f &= 7
    ptr_b = src_end + (bitpos_b >> 3); bitpos_b &= 7
    # Tans_Decode: five interleaved states, three forward and three backward refills per round
    if ptr_f > ptr_b:
        return -1
    o = 0; o_end = dst_size - 5
    STEPS = ("F", 0, 1, "F", 2, 3, "F", 4, "B", 0, 1, "B", 2, 3, "B", 4)
    done = o >= o_end
    forward = True
    while not done:
        for step in STEPS:
            if step == "F":
                bits_f = (bits_f | (_u32le(d, ptr_f) << bitpos_f)) & M32
                ptr_f += (31 - bitpos_f) >> 3; bitpos_f |= 24; forward = True
            elif step == "B":
                bits_b = (bits_b | (_u32be(d, ptr_b - 4) << bitpos_b)) & M32
                ptr_b -= (31 - bitpos_b) >> 3; bitpos_b |= 24; forward = False
            else:
                x, bits_x, symbol, w = lut[state[step]]
                out[o] = symbol; o += 1
                if forward:
                    bitpos_f -= bits_x; state[step] = (bits_f & x) + w; bits_f >>= bits_x
                else:
                    bitpos_b -= bits_x; state[step] = (bits_b & x) + w; bits_b >>= bits_x
                if o >= o_end:
                    done = True
                    break
    if ptr_b - ptr_f + (bitpos_f >> 3) + (bitpos_b >> 3) != 0:
        return -1
    if (state[0] | state[1] | state[2] | state[3] | state[4]) & ~0xFF:
        return -1
    out[o_end:o_end + 5] = bytes(state)
    return src_size


# ----------------------------------------------------------------------------------------------------- RLE
def _krak_decode_rle(d, src, src_size, out, dst_size):
    """Krak_DecodeRLE: returns the bytes consumed (== src_size on success) or -1."""
    if src_size <= 1:
        if src_size != 1:
            return -1
        out[0:dst_size] = bytes([d[src]]) * dst_size
        return 1
    if d[src]:
        # the first part of the command buffer is entropy coded
        n, dec = _decode_bytes(d, src, src + src_size, 0x40000)
        if n <= 0:
            return -1
        cmd = bytearray(dec) + d[src + n:src + src_size]
    else:
        cmd = d[src + 1:src + src_size]
    cp = 0; ce = len(cmd); o = 0; rle_byte = 0
    while cp < ce:
        c = cmd[ce - 1]
        if c == 0 or c >= 0x30:
            ce -= 1
            bytes_to_copy = (~c) & 0xF; bytes_to_rle = c >> 4
            if dst_size - o < bytes_to_copy + bytes_to_rle or ce - cp < bytes_to_copy:
                return -1
            out[o:o + bytes_to_copy] = cmd[cp:cp + bytes_to_copy]; cp += bytes_to_copy; o += bytes_to_copy
            out[o:o + bytes_to_rle] = bytes([rle_byte]) * bytes_to_rle; o += bytes_to_rle
        elif c >= 0x10:
            data = (cmd[ce - 2] | cmd[ce - 1] << 8) - 4096
            ce -= 2
            bytes_to_copy = data & 0x3F; bytes_to_rle = data >> 6
            if dst_size - o < bytes_to_copy + bytes_to_rle or ce - cp < bytes_to_copy:
                return -1
            out[o:o + bytes_to_copy] = cmd[cp:cp + bytes_to_copy]; cp += bytes_to_copy; o += bytes_to_copy
            out[o:o + bytes_to_rle] = bytes([rle_byte]) * bytes_to_rle; o += bytes_to_rle
        elif c == 1:
            rle_byte = cmd[cp]; cp += 1; ce -= 1
        elif c >= 9:
            bytes_to_rle = ((cmd[ce - 2] | cmd[ce - 1] << 8) - 0x8ff) * 128
            ce -= 2
            if dst_size - o < bytes_to_rle:
                return -1
            out[o:o + bytes_to_rle] = bytes([rle_byte]) * bytes_to_rle; o += bytes_to_rle
        else:
            bytes_to_copy = ((cmd[ce - 2] | cmd[ce - 1] << 8) - 511) * 64
            ce -= 2
            if ce - cp < bytes_to_copy or dst_size - o < bytes_to_copy:
                return -1
            out[o:o + bytes_to_copy] = cmd[cp:cp + bytes_to_copy]; cp += bytes_to_copy; o += bytes_to_copy
    if ce != cp or o != dst_size:
        return -1
    return src_size


# -------------------------------------------------------------------------------------- multi array / recursive
def _decode_multi_array(d, src, src_end, dst_capacity, array_count):
    """Kraken_DecodeMultiArray: (bytes consumed, [array bytes]) or None."""
    src_org = src
    if src_end - src < 4:
        return None
    num_arrays_in_file = d[src]; src += 1
    if not (num_arrays_in_file & 0x80):
        return None
    num_arrays_in_file &= 0x3f
    if num_arrays_in_file == 0:
        arrays = []; left = dst_capacity
        for _ in range(array_count):
            n, dec = _decode_bytes(d, src, src_end, left)
            if n < 0:
                return None
            arrays.append(dec); left -= len(dec); src += n
        return src - src_org, arrays
    entropy = []
    total_size = 0
    for _ in range(num_arrays_in_file):
        n, dec = _decode_bytes(d, src, src_end, 0x40000)
        if n < 0:
            return None
        entropy.append(bytearray(dec)); total_size += len(dec); src += n
    if src_end - src < 3:
        return None
    Q = d[src] | d[src + 1] << 8; src += 2
    r = _block_size(d, src, src_end, total_size)
    if r is None:
        return None
    num_indexes = r
    num_lens = num_indexes - array_count
    if num_lens < 1:
        return None
    if Q & 0x8000:
        n, idx = _decode_bytes(d, src, src_end, num_indexes)
        if n < 0 or len(idx) != num_indexes:
            return None
        src += n
        interval_lenlog2 = [t >> 4 for t in idx]
        interval_indexes = [t & 0xF for t in idx]
        num_lens = num_indexes
    else:
        lenlog2_chunksize = num_indexes - array_count
        n, idx = _decode_bytes(d, src, src_end, num_indexes)
        if n < 0 or len(idx) != num_indexes:
            return None
        src += n
        interval_indexes = list(idx)
        n, ll = _decode_bytes(d, src, src_end, lenlog2_chunksize)
        if n < 0 or len(ll) != lenlog2_chunksize:
            return None
        src += n
        interval_lenlog2 = list(ll)
        for v in interval_lenlog2:
            if v > 16:
                return None
    varbits_complen = Q & 0x3FFF
    if src_end - src < varbits_complen:
        return None
    f = src; bits_f = 0; bitpos_f = 24
    src_end_actual = src + varbits_complen
    b = src_end_actual; bits_b = 0; bitpos_b = 24
    decoded_intervals = [0] * num_lens
    i = 0
    while i + 2 <= num_lens:
        bits_f |= _u32be(d, f) >> (24 - bitpos_f); f += (bitpos_f + 7) >> 3
        bits_b |= _u32le(d, b - 4) >> (24 - bitpos_b); b -= (bitpos_b + 7) >> 3
        numbits_f = interval_lenlog2[i]; numbits_b = interval_lenlog2[i + 1]
        bits_f = _rotl32(bits_f | 1, numbits_f); bitpos_f += numbits_f - 8 * ((bitpos_f + 7) >> 3)
        bits_b = _rotl32(bits_b | 1, numbits_b); bitpos_b += numbits_b - 8 * ((bitpos_b + 7) >> 3)
        mf = (2 << numbits_f) - 1; mb = (2 << numbits_b) - 1   # ooz bitmasks[n] has n + 1 bits: the marker bit from |1 is part of the value
        decoded_intervals[i] = bits_f & mf; bits_f &= ~mf & M32
        decoded_intervals[i + 1] = bits_b & mb; bits_b &= ~mb & M32
        i += 2
    if i < num_lens:
        bits_f |= _u32be(d, f) >> (24 - bitpos_f)
        numbits_f = interval_lenlog2[i]
        bits_f = _rotl32(bits_f | 1, numbits_f)
        decoded_intervals[i] = bits_f & ((2 << numbits_f) - 1)
    if interval_indexes[num_indexes - 1]:
        return None
    indi = leni = 0
    increment_leni = 1 if (Q & 0x8000) else 0
    arrays = []; total_out = 0
    for _ in range(array_count):
        cur = bytearray()
        if indi >= num_indexes:
            return None
        while True:
            source = interval_indexes[indi]; indi += 1
            if source == 0:
                break
            if source > num_arrays_in_file:
                return None
            if leni >= num_lens:
                return None
            cur_len = decoded_intervals[leni]; leni += 1
            ea = entropy[source - 1]
            if cur_len > len(ea) or cur_len > dst_capacity - total_out:
                return None
            cur += ea[:cur_len]; del ea[:cur_len]; total_out += cur_len
        leni += increment_leni
        arrays.append(bytes(cur))
    if indi != num_indexes or leni != num_lens:
        return None
    for ea in entropy:
        if len(ea):
            return None
    return src_end_actual - src_org, arrays


def _krak_decode_recursive(d, src, src_size, out, output_size):
    """Krak_DecodeRecursive: returns the bytes consumed (== src_size on success) or -1."""
    src_org = src; src_end = src + src_size
    if src_size < 6:
        return -1
    n = d[src] & 0x7f
    if n < 2:
        return -1
    if not (d[src] & 0x80):
        src += 1; o = 0
        for _ in range(n):
            used, dec = _decode_bytes(d, src, src_end, output_size - o)
            if used < 0:
                return -1
            out[o:o + len(dec)] = dec; o += len(dec); src += used
        if o != output_size:
            return -1
        return src - src_org
    r = _decode_multi_array(d, src, src_end, output_size, 1)
    if r is None:
        return -1
    used, arrays = r
    if len(arrays[0]) != output_size:
        return -1
    out[0:output_size] = arrays[0]
    return used


# ------------------------------------------------------------------------------------------ Kraken_DecodeBytes
def _block_size(d, src, src_end, dest_capacity):
    """Kraken_GetBlockSize: the decoded size of the entropy block at |src| (its header only), None on error."""
    if src_end - src < 2:
        return None
    chunk_type = (d[src] >> 4) & 0x7
    if chunk_type == 0:
        if d[src] >= 0x80:
            src_size = (d[src] << 8 | d[src + 1]) & 0xFFF; src += 2
        else:
            if src_end - src < 3:
                return None
            src_size = d[src] << 16 | d[src + 1] << 8 | d[src + 2]
            if src_size & ~0x3ffff:
                return None
            src += 3
        if src_size > dest_capacity or src_end - src < src_size:
            return None
        return src_size
    if chunk_type >= 6:
        return None
    if d[src] >= 0x80:
        if src_end - src < 3:
            return None
        bits = d[src] << 16 | d[src + 1] << 8 | d[src + 2]
        src_size = bits & 0x3ff; dst_size = src_size + ((bits >> 10) & 0x3ff) + 1; src += 3
    else:
        if src_end - src < 5:
            return None
        bits = d[src + 1] << 24 | d[src + 2] << 16 | d[src + 3] << 8 | d[src + 4]
        src_size = bits & 0x3ffff; dst_size = (((bits >> 18) | (d[src] << 14)) & 0x3FFFF) + 1
        if src_size >= dst_size:
            return None
        src += 5
    if src_end - src < src_size or dst_size > dest_capacity:
        return None
    return dst_size


def _decode_bytes(d, src, src_end, output_size):
    """Kraken_DecodeBytes: one entropy coded block. Returns (bytes consumed, decoded bytes); (-1, None) on error."""
    src_org = src
    if src_end - src < 2:
        return -1, None
    chunk_type = (d[src] >> 4) & 0x7
    if chunk_type == 0:
        if d[src] >= 0x80:
            src_size = (d[src] << 8 | d[src + 1]) & 0xFFF; src += 2
        else:
            if src_end - src < 3:
                return -1, None
            src_size = d[src] << 16 | d[src + 1] << 8 | d[src + 2]
            if src_size & ~0x3ffff:
                return -1, None
            src += 3
        if src_size > output_size or src_end - src < src_size:
            return -1, None
        return src + src_size - src_org, bytes(d[src:src + src_size])
    if d[src] >= 0x80:
        if src_end - src < 3:
            return -1, None
        bits = d[src] << 16 | d[src + 1] << 8 | d[src + 2]
        src_size = bits & 0x3ff; dst_size = src_size + ((bits >> 10) & 0x3ff) + 1; src += 3
    else:
        if src_end - src < 5:
            return -1, None
        bits = d[src + 1] << 24 | d[src + 2] << 16 | d[src + 3] << 8 | d[src + 4]
        src_size = bits & 0x3ffff; dst_size = (((bits >> 18) | (d[src] << 14)) & 0x3FFFF) + 1
        if src_size >= dst_size:
            return -1, None
        src += 5
    if src_end - src < src_size or dst_size > output_size:
        return -1, None
    out = bytearray(dst_size)
    if chunk_type in (2, 4):
        src_used = _decode_bytes_type12(d, src, src_size, out, dst_size, chunk_type >> 1)
    elif chunk_type == 5:
        src_used = _krak_decode_recursive(d, src, src_size, out, dst_size)
    elif chunk_type == 3:
        src_used = _krak_decode_rle(d, src, src_size, out, dst_size)
    elif chunk_type == 1:
        src_used = _krak_decode_tans(d, src, src_size, out, dst_size)
    else:
        src_used = -1
    if src_used != src_size:
        return -1, None
    return src + src_size - src_org, bytes(out)


# ------------------------------------------------------------------------------------------------- LZ stage
def _unpack_offsets(d, src, src_end, packed_offs, packed_offs_extra, multi_dist_scale, packed_litlen):
    """Kraken_UnpackOffsets: (offs_stream, len_stream) or None."""
    bits_a = BitReader(d, src, src_end); bits_a.refill()
    bits_b = BitReader(d, src_end, src); bits_b.refill_backwards()
    # excess_flag is always false in Kraken_ReadLzTable
    if bits_b.bits < 0x2000:
        return None
    n = _clz32(bits_b.bits)
    bits_b.bitpos += n; bits_b.bits = (bits_b.bits << n) & M32
    bits_b.refill_backwards()
    n += 1
    u32_len_stream_size = (bits_b.bits >> (32 - n)) - 1
    bits_b.bitpos += n; bits_b.bits = (bits_b.bits << n) & M32
    bits_b.refill_backwards()

    offs = []
    n_off = len(packed_offs)
    if multi_dist_scale == 0:
        for i in range(n_off):
            offs.append(-bits_a.read_distance(packed_offs[i]) if not (i & 1) else -bits_b.read_distance(packed_offs[i], True))
    else:
        for i in range(n_off):
            cmd = packed_offs[i]
            if (cmd >> 3) > 26:
                return None
            if not (i & 1):
                o = ((8 + (cmd & 7)) << (cmd >> 3)) | bits_a.read_more_than_24_bits(cmd >> 3)
            else:
                o = ((8 + (cmd & 7)) << (cmd >> 3)) | bits_b.read_more_than_24_bits_b(cmd >> 3)
            offs.append(8 - o)
        if multi_dist_scale != 1:
            offs = [multi_dist_scale * o - packed_offs_extra[i] for i, o in enumerate(offs)]
    if u32_len_stream_size > 512:
        return None
    u32_len = []
    for i in range(u32_len_stream_size):
        v = bits_a.read_length() if not (i & 1) else bits_b.read_length(True)
        if v is None:
            return None
        u32_len.append(v)
    bits_a.p -= (24 - bits_a.bitpos) >> 3
    bits_b.p += (24 - bits_b.bitpos) >> 3
    if bits_a.p != bits_b.p:
        return None
    lens = []; ui = 0
    for v in packed_litlen:
        if v == 255:
            if ui >= len(u32_len):
                return None
            v = u32_len[ui] + 255; ui += 1
        lens.append(v + 3)
    if ui != len(u32_len):
        return None
    return offs, lens


def _read_lz_table(d, src, src_end, dst_size):
    """Kraken_ReadLzTable (offset != 0 handled by the caller: the first 8 raw bytes are already taken).
    Returns (lit, cmd, offs, lens) or None."""
    if d[src] & 0x80:
        return None   # excess bytes not supported (reserved flag)
    n, lit = _decode_bytes(d, src, src_end, dst_size)
    if n < 0:
        return None
    src += n
    n, cmd = _decode_bytes(d, src, src_end, dst_size)
    if n < 0:
        return None
    src += n
    if src_end - src < 3:
        return None
    offs_scaling = 0; packed_offs_extra = None
    if d[src] & 0x80:
        offs_scaling = d[src] - 127; src += 1
        n, packed_offs = _decode_bytes(d, src, src_end, len(cmd))
        if n < 0:
            return None
        src += n
        if offs_scaling != 1:
            n, packed_offs_extra = _decode_bytes(d, src, src_end, len(packed_offs))
            if n < 0 or len(packed_offs_extra) != len(packed_offs):
                return None
            src += n
    else:
        n, packed_offs = _decode_bytes(d, src, src_end, len(cmd))
        if n < 0:
            return None
        src += n
    n, packed_len = _decode_bytes(d, src, src_end, dst_size >> 2)
    if n < 0:
        return None
    src += n
    r = _unpack_offsets(d, src, src_end, packed_offs, packed_offs_extra, offs_scaling, packed_len)
    if r is None:
        return None
    return lit, cmd, r[0], r[1]


def _copy_match(out, o, offset, n):
    """out[o:o+n] = out[o+offset:...] with LZ overlap semantics (offset < 0)."""
    s = o + offset
    if -offset >= n:
        out[o:o + n] = out[s:s + n]
    else:
        for i in range(n):
            out[o + i] = out[s + i]


def _process_lz_runs(mode, out, o, o_end, o_start, lzt):
    """Kraken_ProcessLzRuns_Type0 (mode 0, delta literals) / _Type1 (mode 1). |o| is the write position, |o_start| the
    start of the whole output (offsets are bounded by it)."""
    lit, cmd, offs, lens = lzt
    li = 0; oi = 0; ni = 0
    recent = [0, 0, 0, -8, -8, -8, 0]
    last_offset = -8
    for f in cmd:
        litlen = f & 3; offs_index = f >> 6; matchlen = (f >> 2) & 0xF
        if litlen == 3:
            if ni >= len(lens):
                return False
            litlen = lens[ni]; ni += 1
        if oi < len(offs):
            recent[6] = offs[oi]
        if litlen:
            if li + litlen > len(lit) or o + litlen > o_end:
                return False
            if mode == 0:
                for i in range(litlen):
                    out[o + i] = (lit[li + i] + out[o + i + last_offset]) & 0xFF
            else:
                out[o:o + litlen] = lit[li:li + litlen]
            o += litlen; li += litlen
        offset = recent[offs_index + 3]
        recent[offs_index + 3] = recent[offs_index + 2]
        recent[offs_index + 2] = recent[offs_index + 1]
        recent[offs_index + 1] = recent[offs_index]
        recent[3] = offset
        last_offset = offset
        if offs_index == 3:
            if oi >= len(offs):
                return False
            oi += 1
        if offset >= 0 or o + offset < o_start:
            return False   # offset out of bounds
        if matchlen != 15:
            matchlen += 2
        else:
            if ni >= len(lens):
                return False
            matchlen = 14 + lens[ni]; ni += 1
        if matchlen > o_end - o:
            return False
        _copy_match(out, o, offset, matchlen)
        o += matchlen
    if oi != len(offs) or ni != len(lens):
        return False
    final_len = o_end - o
    if final_len != len(lit) - li:
        return False
    if final_len:
        if mode == 0:
            for i in range(final_len):
                out[o + i] = (lit[li + i] + out[o + i + last_offset]) & 0xFF
        else:
            out[o:o_end] = lit[li:]
    return True


def _decode_quantum(d, src, src_end, out, o, o_end, o_start):
    """Kraken_DecodeQuantum: returns the bytes consumed or -1."""
    src_in = src
    while o_end - o:
        dst_count = min(o_end - o, 0x20000)
        if src_end - src < 4:
            return -1
        chunkhdr = d[src + 2] | d[src + 1] << 8 | d[src] << 16
        if not (chunkhdr & 0x800000):
            # stored as entropy without any match copying
            src_used, dec = _decode_bytes(d, src, src_end, dst_count)
            if src_used < 0 or len(dec) != dst_count:
                return -1
            out[o:o + dst_count] = dec
        else:
            src += 3
            src_used = chunkhdr & 0x7FFFF
            mode = (chunkhdr >> 19) & 0xF
            if src_end - src < src_used:
                return -1
            if src_used < dst_count:
                if mode > 1 or src_used < 13:
                    return -1
                s = src; p = o
                if o == o_start:
                    out[o:o + 8] = d[s:s + 8]; s += 8; p += 8
                lzt = _read_lz_table(d, s, src + src_used, dst_count)
                if lzt is None:
                    return -1
                if not _process_lz_runs(mode, out, p, o + dst_count, o_start, lzt):
                    return -1
            elif src_used > dst_count or mode != 0:
                return -1
            else:
                out[o:o + dst_count] = d[src:src + dst_count]
        src += src_used
        o += dst_count
    return src - src_in


# ------------------------------------------------------------------------------------------------ top level
def _parse_header(d, p, src_end):
    """Kraken_ParseHeader: (uncompressed, use_checksums, next position); raises for non-Kraken data."""
    if src_end - p < 2:
        raise OodleError("truncated Oodle header")
    b = d[p]
    if (b & 0xF) != 0xC or ((b >> 4) & 3) != 0:
        raise OodleError("not an Oodle block (header byte 0x%02x)" % b)
    decoder_type = d[p + 1] & 0x7F
    if decoder_type != 6:
        name = DECODER_NAMES.get(decoder_type, "type %d" % decoder_type)
        raise OodleError("unsupported Oodle codec %s - only Kraken is supported; please open an issue with the mod name" % name)
    return (b >> 6) & 1, d[p + 1] >> 7, p + 2


def decompress(src, dst_size):
    """Decompresses one Oodle Kraken stream of exactly |dst_size| bytes (the Oodle raw size stored by the caller).
    Raises OodleError on any malformed or unsupported input; never returns partial data."""
    d = bytes(src) + b"\0" * 16   # SAFE_SPACE: word reads near the end read zeros instead of failing
    src_end = len(src)
    out = bytearray(dst_size)
    p = 0; offset = 0
    uncompressed = use_checksums = 0
    while offset < dst_size:
        if (offset & 0x3FFFF) == 0:
            uncompressed, use_checksums, p = _parse_header(d, p, src_end)
        left = min(0x40000, dst_size - offset)
        if uncompressed:
            if src_end - p < left:
                raise OodleError("truncated uncompressed block")
            out[offset:offset + left] = d[p:p + left]
            p += left; offset += left
            continue
        # Kraken_ParseQuantumHeader
        if src_end - p < 3:
            raise OodleError("truncated quantum header")
        v = d[p] << 16 | d[p + 1] << 8 | d[p + 2]
        size = v & 0x3FFFF
        if size != 0x3FFFF:
            compressed_size = size + 1
            p += 6 if use_checksums else 3
        elif (v >> 18) == 1:
            # memset quantum
            out[offset:offset + left] = bytes([d[p + 3]]) * left
            p += 4; offset += left
            continue
        else:
            raise OodleError("bad quantum header")
        if p > src_end or src_end - p < compressed_size:
            raise OodleError("truncated quantum")
        if compressed_size > left:
            raise OodleError("quantum larger than its output")
        if compressed_size == left:
            out[offset:offset + left] = d[p:p + left]
        else:
            n = _decode_quantum(d, p, p + compressed_size, out, offset, offset + left, 0)
            if n != compressed_size:
                raise OodleError("corrupt Kraken quantum at offset %d" % offset)
        p += compressed_size; offset += left
    if p != src_end:
        raise OodleError("%d trailing bytes after the Kraken stream" % (src_end - p))
    return bytes(out)
