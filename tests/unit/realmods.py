"""Paks of real mods for the tests that convert or read them. They are not part of the repository: a test names the pak
by file name, and find() looks for exactly that file (SHA-256 and size below)

  - in a store of mod files laid out by SHA-256 (TKA_MOD_STORE: <first two hex digits>/<sha256>/<file name>), or
  - in a folder of original mod paks (TKA_MOD_ARCHIVE) under the path it had there.

Not found (or only a zero-filled placeholder) -> "", and the test skips itself.
"""
import glob, os
import cfg

# file name: (sha256, size, path below TKA_MOD_ARCHIVE)
PAKS = {
    "TKA-UN_Dv1-fix1.3d.pak": ("63d8e7e402befcad68a8aa4cb9bd9d91411605ff6314c5cfc9be457b17907d35", 1753528,
                               "Mods/TKA-UN_Dv1-fix1.3d.pak"),
    "Jodi_New_Pussy.pak": ("53af31d863aaf674c3840ed6a0b5ee2d02f2810f4d31f464e817d6b5b1050d3a", 7034647,
                           "workshop/3612645999/Jodi_New_Pussy.pak"),
    "FemaleOGMORPH-0.6_P.pak": ("81f89aac44ce21f744c1c871f4d1d44d0a43b490456c771f50a93891a0814e17", 1914217,
                                "workshop/3432791726/FemaleOGMORPH-0.6_P.pak"),
    "HMs_Shoes.pak": ("7b21029a9e2f7f3b7ee75523624fe0161ff6263b906911e058f6db5a3e32d2b4", 1171225, "Mods/HMs_Shoes.pak"),
    "Jodithicctest4_P.pak": ("763c8125116838ba00d182fc985ae4f83bc6d6e58990dde85b8a5cf6bf8abcc8", 830414,
                             "nexus/783/Jodithicctest4_P.pak"),
    "JodiCustomWIP_P.pak": ("", 0, "other/JodiCustomWIP_P.pak"),     # only in the archive folder, any size
    "TKA_Workshop_EscapefromRC.pak": ("e89f8b909fedd5efc51a388b4adc9bb91f0afdbf2e60391d75f2e46ad08eb617", 1577842859,
                                      "Mods/TKA_Workshop_EscapefromRC.pak"),
    "Car_Dealer.pak": ("fccedec8c6cf5e4e691b067065c145c22856bcc8c82d1d431117cb331e7bde4d", 1185651495, "Mods/Car_Dealer.pak"),
    "Bikini_Bottom.pak": ("369b5d60cfd89db6179e2b8ec20886023ae160b13490b37e14ea4e429c3115e5", 207158419,
                          "Mods/Bikini_Bottom.pak"),
    "Cat_ear_headphones.pak": ("7eb54c9f1f160e82cbb98f2cc054d76cad08d9a345bbcdc7e5cee4e04c14d53a", 42223409,
                               "Mods/Cat_ear_headphones.pak"),
    "Lost_in_Abandoned_Factory.pak": ("5faec1c1c76dc0f6a75e6aea5053bd62f8610b2763ccce58b9799d638fccd472", 692777821,
                                      "Mods/Lost_in_Abandoned_Factory.pak"),
    "Racing_Suit.pak": ("bd46bcccd98d7a9bad81673d8330cbf718dd79595ba1a5571f7fc5bc93e94919", 16814559,
                        "workshop/3595414420/Racing_Suit.pak"),
    "Brefg_Poses.pak": ("8cb01725189fbae6c8b9c97917250b90ecaed879a20b9528d5465bfffe6d2fbe", 53326853,
                        "workshop/3549720881/Brefg_Poses.pak"),
    "LowPolyJunglePack.pak": ("78c0a34912db32e20da791d51350305cd5858023e61e2d64958009bf3c5a2bd8", 1315723518,
                              "workshop/3597992051/LowPolyJunglePack.pak"),
    "Jodi_Idle_Adjustment_qhlys_P.pak": ("baa006e52d45f040df6249e737d272167a410f30e8edf63a8e7d84238b8d061f", 9618,
                                         "../library/_sources/IdleAltUI_IdleAdjustment_qhlys/Jodi_Idle_Adjustment_qhlys_P.pak"),
}


def store():
    return cfg.path("TKA_MOD_STORE")


def archive():
    return cfg.path("TKA_MOD_ARCHIVE")


def _ok(p, size):
    return cfg.real_file(p) and (not size or os.path.getsize(p) == size)


def find(name):
    """Path of the real pak `name` (a key of PAKS), or "" when neither place has it."""
    sha, size, old = PAKS[name]
    s, a = store(), archive()
    if s and sha:
        p = os.path.join(s, sha[:2], sha, name)
        if _ok(p, size):
            return p
    if a:
        p = os.path.normpath(os.path.join(a, old))
        if _ok(p, size):
            return p
    return ""


def have(*names):
    return all(find(n) for n in names)


def every_pak():
    """All paks of both places (KRAKEN_FULL)."""
    out = []
    if store():
        out += glob.glob(os.path.join(store(), "*", "*", "*.pak"))
    if archive():
        out += glob.glob(os.path.join(archive(), "**", "*.pak"), recursive=True)
    return sorted(p for p in out if cfg.real_file(p))
