#!/bin/bash
# Runs an editor Python script headless; scripts print "EDTEST PASS ..." / "EDTEST FAIL ...".
set -e; source "$(dirname "$0")/../config.sh"; mkdir -p "$BUILD"
"$UE_CMD" "$UPROJECT" -run=pythonscript -script="$1" -unattended -nullrhi -nosplash -stdout 2>&1 | grep -E "EDTEST|LogPython: Error|Traceback|Error:" | grep -v LogDerivedDataCache | sed "s/^\[[^]]*\]\[[ 0-9]*\]//" | sort -u | tee "$BUILD/edtest.log"
grep -q "EDTEST PASS" "$BUILD/edtest.log" && ! grep -q "EDTEST FAIL\|LogPython: Error\|Traceback" "$BUILD/edtest.log"
