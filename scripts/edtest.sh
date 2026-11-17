#!/bin/bash
# Runs one or more editor Python test scripts headless in ONE editor session (each start costs ~5 s + project load);
# scripts print "EDTEST PASS ..." / "EDTEST FAIL ...". A wrapper execs every script in its own namespace, so the files
# stay runnable on their own (each ends with run(main)). Result on stdout and in build/edtest.log (the last run's);
# exit 1 on any FAIL / Python error.
# Safe for parallel callers (several sessions, other mods' builds on the same kit): each run writes its own wrapper and
# log in a temp folder, and the editor runs one at a time under build/edtest.lock (a second caller waits, never mixes).
set -e; source "$(dirname "$0")/../config.sh"; mkdir -p "$BUILD"
RUN="$(mktemp -d "$BUILD/edtest.XXXXXX")"; trap 'rm -rf "$RUN"' EXIT
WRAP="$RUN/edtest_wrap.py"; LOG="$RUN/edtest.log"; : > "$WRAP"
for f in "$@"; do
  case "$f" in /*) ;; *) f="$PWD/$f";; esac
  printf 'import unreal, runpy\nunreal.log_warning("EDTEST file %s")\nrunpy.run_path(%s, run_name="__main__")\n' "$(basename "$f")" "\"$f\"" >> "$WRAP"
done
exec 9> "$BUILD/edtest.lock"
flock -n 9 || { echo "edtest: another editor test run holds $BUILD/edtest.lock, waiting" >&2; flock 9; }
"$(dirname "$0")/ue.sh" "$UPROJECT" -run=pythonscript -script="$WRAP" -unattended -nullrhi -nosplash -stdout 2>&1 | grep -E "EDTEST|LogPython: Error|Traceback|Error:" | grep -v LogDerivedDataCache | sed "s/^\[[^]]*\]\[[ 0-9]*\]//" | sort -u | tee "$LOG"
cp "$LOG" "$BUILD/edtest.log"
grep -q "EDTEST PASS" "$LOG" && ! grep -q "EDTEST FAIL\|LogPython: Error\|Traceback" "$LOG"
