#!/usr/bin/env python3
"""gate-forgery-test: prove gates can fail. usage: forge_test.py spec.json"""
import json, os, shutil, subprocess, sys, tempfile

UNMEASURED_DEFAULT = 3


def run(cmd, target):
    argv = [c.replace("{target}", target) for c in cmd]
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=120)
        return p.returncode
    except OSError:
        return 127
    except subprocess.TimeoutExpired:
        return 124


def main():
    if len(sys.argv) != 2:
        print(__doc__); return 2
    spec_path = os.path.abspath(sys.argv[1])
    base = os.path.dirname(spec_path)
    try: spec = json.load(open(spec_path))
    except (OSError, ValueError) as e: print(f"bad spec: {e}"); return 2
    gates = spec.get("gates", []) if isinstance(spec, dict) else []
    if not isinstance(gates, list) or not gates:
        print("spec has no gates - nothing proved"); return 2
    for g in gates:
        if not isinstance(g, dict) or not isinstance(g.get("name"), str) or not g["name"].strip():
            print("each gate needs a nonempty name"); return 2
        cmd = g.get("cmd")
        if not isinstance(cmd, list) or not cmd or not all(isinstance(c, str) and c for c in cmd):
            print("cmd must be a nonempty argv array"); return 2
        for field in ("good", "bad"):
            fixtures = g.get(field)
            if not isinstance(fixtures, list) or not fixtures or not all(isinstance(t, str) and t for t in fixtures):
                print("each gate needs nonempty good and bad fixture lists"); return 2
        reject, unavailable = g.get("reject_exit", 1), g.get("unmeasured_exit", UNMEASURED_DEFAULT)
        if type(reject) is not int or not 1 <= reject <= 123 or type(unavailable) is not int or not 1 <= unavailable <= 123 or reject == unavailable:
            print("reject_exit and unmeasured_exit must be distinct codes in 1..123"); return 2
    os.chdir(base)
    bad = 0
    rows = []

    def check(gate, layer, ok, detail):
        nonlocal bad
        rows.append((gate, layer, "ok" if ok else "BLIND/NOISY", detail))
        if not ok:
            bad += 1

    for g in gates:
        name, cmd = g["name"], g["cmd"]
        unmeasured = g.get("unmeasured_exit", UNMEASURED_DEFAULT)
        reject = g.get("reject_exit", 1)
        # layer 2: wiring - the executable must resolve, otherwise the gate fails forever (or is skipped)
        exe = cmd[0]
        wired = shutil.which(exe) is not None or os.path.exists(exe)
        check(name, "wiring", wired, f"{exe} resolves" if wired else f"{exe} not found")
        script = next((c for c in cmd[1:] if not c.startswith("-") and "{target}" not in c and os.path.splitext(c)[1]), None)
        if script:
            ok = os.path.exists(script)
            check(name, "wiring", ok, f"{script} exists" if ok else f"{script} MISSING")
        # layer 1: forgery - every bad fixture must be rejected (non-zero, and not merely 'unmeasured')
        for t in g.get("bad", []):
            rc = run(cmd, t)
            check(name, "forgery", os.path.exists(t) and rc == reject, f"bad fixture {t}: exit {rc}")
        # layer 4: false positive
        for t in g.get("good", []):
            rc = run(cmd, t)
            check(name, "false-positive", os.path.exists(t) and rc == 0, f"good fixture {t}: exit {rc}")
        # layer 3: vacuity
        if g.get("empty"):
            d = tempfile.mkdtemp(prefix="forge-empty-")
            rc = run(cmd, d); shutil.rmtree(d, ignore_errors=True)
            check(name, "vacuity", rc in (reject, unmeasured, 2), f"empty input: exit {rc} (0 would mean 'nothing measured = clean')")
        if g.get("missing"):
            with tempfile.TemporaryDirectory(prefix="forge-missing-") as absent:
                rc = run(cmd, os.path.join(absent, "missing"))
            check(name, "vacuity", rc in (reject, unmeasured, 2), f"missing input: exit {rc}")
        # declaration check: exemptions need reasons
        for ex in g.get("exemptions", []):
            ok = bool(str(ex.get("reason", "")).strip())
            check(name, "exemption", ok, f"{ex.get('item')}: " + ("reason given" if ok else "NO REASON - a bare exemption reopens the hole"))

    w = max(len(r[0]) for r in rows)
    for gate, layer, st, detail in rows:
        print(f"[{st:11}] {gate:<{w}}  {layer:<15} {detail}")
    print("\n" + ("all gates behaved" if not bad else f"{bad} problem(s): fix the gate before trusting its green"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
