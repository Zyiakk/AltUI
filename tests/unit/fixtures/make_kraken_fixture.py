#!/usr/bin/env python3
"""Builds kraken_fixture.pak for tests/unit/test_kraken.py with the kit's UnrealPak (-compressionformats=Oodle).
The inputs are generated deterministically (seeded), so the SHA-256 of each file in the test never changes.
Usage: python3 make_kraken_fixture.py [UnrealPak]   (default: $UNREALPAK or the 4.27 kit path)"""
import os, sys, random, subprocess, tempfile, hashlib
H = os.path.dirname(os.path.abspath(__file__))
UNREALPAK = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("UNREALPAK", "/mnt/linDataSSD/apps/UnrealEngine/UnrealEngine-4.27/Engine/Binaries/Linux/UnrealPak")
WORDS = ("body mesh pak mod jodi skeleton blueprint texture material outfit shape chip switch level load convert name title "
         "folder file python steam nexus workshop the a of and in to with for is not").split()


def inputs():
    r = random.Random(20260919)
    text = " ".join(r.choice(WORDS) for _ in range(6000)).encode()[:30000]
    skew_w = [max(1, int(200 * 0.93 ** i)) for i in range(256)]
    skew = bytes(r.choices(range(256), weights=skew_w, k=50000))
    runs = bytearray()
    while len(runs) < 40000:
        runs += bytes(r.getrandbits(8) for _ in range(r.randint(1, 20))) + b"\0" * r.randint(5, 200)
    return {"text.bin": text, "skew.bin": skew, "runs.bin": bytes(runs), "zeros.bin": b"\0" * 30000,
            "big.bin": (text * 6)[:150000], "random.bin": bytes(r.getrandbits(8) for _ in range(20000))}


if __name__ == "__main__":
    d = tempfile.mkdtemp()
    rsp = os.path.join(d, "list.rsp")
    with open(rsp, "w") as f:
        for name, data in inputs().items():
            p = os.path.join(d, name); open(p, "wb").write(data)
            f.write('"%s" "../../../Fixture/%s"\n' % (p, name))
            print("%-12s %6d bytes  sha256 %s" % (name, len(data), hashlib.sha256(data).hexdigest()))
    out = os.path.join(H, "kraken_fixture.pak")
    subprocess.run([UNREALPAK, out, "-create=" + rsp, "-compress", "-compressionformats=Oodle"], check=True, capture_output=True)
    print(out, os.path.getsize(out), "bytes")
