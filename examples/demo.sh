#!/usr/bin/env bash
cd "$(dirname "$0")/.."
run() { printf '$ %s\n' "$*"; "$@"; printf '[exit %s]\n\n' "$?"; }
echo "# A gate that really detects TODOs: every forged case behaves"
run python3 scripts/forge_test.py examples/spec.json
echo "# A gate that always passes (blind): the forgery test catches it"
run python3 scripts/forge_test.py examples/spec_blind.json
