#!/bin/bash
# Runs one or more editor Python test scripts headless in ONE editor session (each start costs ~5 s + project load);
# scripts print "EDTEST PASS ..." / "EDTEST FAIL ...". A wrapper execs every script in its own namespace, so the files
# stay runnable on their own (each ends with run(main)). Result in build/edtest.log; exit 1 on any FAIL / Python error.
set -e; source "$(dirname "$0")/../config.sh"; mkdir -p "$BUILD"
WRAP="$BUILD/edtest_wrap.py"; : > "$WRAP"
for f in "$@"; do
  case "$f" in /*) ;; *) f="$PWD/$f";; esac
  printf 'import unreal, runpy\nunreal.log_warning("EDTEST file %s")\nrunpy.run_path(%s, run_name="__main__")\n' "$(basename "$f")" "\"$f\"" >> "$WRAP"
done
"$(dirname "$0")/ue.sh" "$UPROJECT" -run=pythonscript -script="$WRAP" -unattended -nullrhi -nosplash -stdout 2>&1 | grep -E "EDTEST|LogPython: Error|Traceback|Error:" | grep -v LogDerivedDataCache | sed "s/^\[[^]]*\]\[[ 0-9]*\]//" | sort -u | tee "$BUILD/edtest.log"
grep -q "EDTEST PASS" "$BUILD/edtest.log" && ! grep -q "EDTEST FAIL\|LogPython: Error\|Traceback" "$BUILD/edtest.log"
