"""psa.py - reads an ActorX .psa as umodel writes it (chunks ANIMHEAD, BONENAMES, ANIMINFO, ANIMKEYS; little endian).
Pure Python (also used inside Blender). Keys are per frame for every bone, bone-local, UE units (cm), as umodel stores them."""
import struct


def read(path):
    b = open(path, "rb").read(); p = 0; chunks = {}
    while p + 32 <= len(b):
        cid = b[p:p + 20].split(b"\0")[0].decode(); _, size, count = struct.unpack_from("<iii", b, p + 20); p += 32
        chunks[cid] = (p, size, count); p += size * count
    bones = []
    p, size, count = chunks["BONENAMES"]
    for i in range(count):
        o = p + i * size
        name = b[o:o + 64].split(b"\0")[0].decode(); flags, nchild, parent = struct.unpack_from("<iii", b, o + 64)
        q = struct.unpack_from("<4f", b, o + 76); pos = struct.unpack_from("<3f", b, o + 92)
        bones.append({"name": name, "parent": parent, "rot": q, "pos": pos})
    anims = []
    p, size, count = chunks["ANIMINFO"]
    for i in range(count):
        o = p + i * size
        name = b[o:o + 64].split(b"\0")[0].decode()
        total_bones, root_incl, comp, quotum, reduction, track_time, rate, start_bone, first, nframes = struct.unpack_from("<iiiiffffii", b, o + 128)[:10]
        anims.append({"name": name, "bones": total_bones, "rate": rate, "first": first, "frames": nframes, "track_time": track_time})
    p, size, count = chunks["ANIMKEYS"]
    keys = [struct.unpack_from("<3f4ff", b, p + i * size) for i in range(count)]   # pos xyz, quat xyzw, time
    return {"bones": bones, "anims": anims, "keys": keys}


def frame(psa, f, anim=0):
    """[(pos, quat xyzw)] per bone at frame f."""
    a = psa["anims"][anim]; n = a["bones"]; base = (a["first"] + f) * n
    return [(k[0:3], k[3:7]) for k in psa["keys"][base:base + n]]
