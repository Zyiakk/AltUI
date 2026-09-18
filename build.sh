#!/bin/bash
# Full chain: gen (assets/gen/*.py -> assets/*.json) -> bpgen -> cook -> pak -> verify -> deploy.  Options: --no-bpgen --no-cook --no-deploy --hook (force the hook deploy, see deploy.sh)
set -e; cd "$(dirname "$0")"; source ./config.sh; mkdir -p "$BUILD"
[[ " $* " == *" --no-bpgen "* ]] || { for g in assets/gen/gen_*.py; do python3 "$g"; done; scripts/bpgen.sh; }
[[ " $* " == *" --no-cook "* ]]  || scripts/cook.sh
scripts/pak.sh
python3 scripts/verify_stubs.py
python3 scripts/verify_pak.py "$BUILD/AltUI.pak" "$BUILD/AltUI_Hook_P.pak"
[[ " $* " == *" --no-deploy "* ]] || scripts/deploy.sh "$@"
echo "BUILD OK"
