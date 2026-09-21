#!/bin/bash
# Wrapper for every UE4Editor-Cmd run (bpgen, cook, edtest). The commandlet needs ~28 GB (10 GB resident, rest in zram
# swap, which is RAM too); with the game running (~9 GB) the kernel OOM-kills it - and because the build runs inside
# the IDE's systemd unit (OOMPolicy=stop) systemd then stops the IDE as well. Hence:
# 1) refuse to start while the game runs, 2) run in an own transient scope so an OOM kill only takes the commandlet.
set -e; source "$(dirname "$0")/../config.sh"
if pgrep -x TheKillingAntid >/dev/null; then echo "UE: game is running - close it first (commandlet + game do not fit in RAM)" >&2; exit 1; fi
if command -v systemd-run >/dev/null 2>&1; then exec systemd-run --user --scope -q "$UE_CMD" "$@"; fi
exec "$UE_CMD" "$@"
