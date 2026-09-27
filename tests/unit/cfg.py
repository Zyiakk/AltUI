"""Local paths for the tests: from the environment, else from config.sh, else the fallback.

The build scripts read config.sh, so a checkout that can build already has every path a test needs; nothing is written
into the test files. A test whose path is missing skips itself.
"""
import os, subprocess

H = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(H, "..", "..", "config.sh")
_cache = {}


def path(name, default=""):
    v = os.environ.get(name)
    if v:
        return v
    if name not in _cache:
        out = ""
        if os.path.exists(CONFIG):
            r = subprocess.run(["bash", "-c", 'source "$1" >/dev/null 2>&1; printf %%s "${%s-}"' % name, "_", CONFIG],
                               capture_output=True, text=True)
            out = r.stdout.strip()
        _cache[name] = out
    return _cache[name] or default
