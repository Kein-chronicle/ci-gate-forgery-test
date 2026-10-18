#!/usr/bin/env bash
# The harness itself needs a forgery test: it must pass the correct gate and flag the blind one.
set -u; here="$(cd "$(dirname "$0")" && pwd)"; bad=0
python3 "$here/scripts/forge_test.py" "$here/examples/spec.json" >/dev/null; [ $? = 0 ] && echo "ok   correct gate accepted" || { echo "FAIL correct gate rejected"; bad=1; }
out="$(python3 "$here/scripts/forge_test.py" "$here/examples/spec_blind.json" 2>&1)"; rc=$?
{ [ $rc = 1 ] && echo "$out" | grep -q "3 problem(s)" && echo "$out" | grep -q "BLIND/NOISY"; } && echo "ok   blind gate flagged for the right reasons (3 problems)" || { echo "FAIL blind gate: exit $rc"; echo "$out" | tail -5; bad=1; }
python3 "$here/scripts/forge_test.py" >/dev/null 2>&1; [ $? = 2 ] && echo "ok   missing spec is exit 2" || { echo "FAIL usage exit"; bad=1; }
python3 "$here/tests/test_release_regressions.py" || bad=1
exit $bad
