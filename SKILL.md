---
name: gate-forgery-test
description: Audit the quality gates themselves, not the product. Use when you run a pipeline with many automated checks/linters/gates and need proof they can actually fail - after writing or loosening a gate, when everything is suspiciously green, when a gate measured zero items and passed, when two gates might contradict each other, or when you add an exemption list. Runs each gate against forged-bad, empty, missing and known-good inputs and reports which gates are blind.
---

# gate-forgery-test

Most gate suites test whether the *product* passes. Nobody tests whether the *gate can fail*.
This skill does. A gate is only worth its green if a forged defect turns it red.

## Four layers (a gate can be wrong at any of them)

| Layer | Question | Typical bug found |
|---|---|---|
| 1. Forgery | Does a planted defect turn it red? | Regex never matches (`\b` before `\.`) |
| 2. Wiring | Does the command it calls exist and run? | Typo in the command -> always FAIL, a stage can never close |
| 3. Vacuity | Does an EMPTY input fail? | "No forbidden pattern found" over 0 files = green. Not measured is not clean |
| 4. False positive | Does a known-good input stay green? | A noisy gate teaches people to switch it off - same end state as a hole |

Plus two declaration checks the harness also runs:
- **Exemptions carry a reason.** A bare exemption list recreates the hole it was meant to cover.
- **Contradiction.** Before adding a gate ask: does this rule forbid code that another gate
  *requires*? (Real case: "no StoreKit import" vs "must call the rating prompt, which lives in
  StoreKit".) Fix by descending to the intent (ban payment symbols, not the framework name), then
  re-run the forgery test on the relaxed gate - the relaxation itself can ship a bad regex.

## Use

```bash
python3 scripts/forge_test.py examples/spec.json
# exit 0 = every case behaved; exit 1 = at least one blind or noisy gate
```

`spec.json`:

```json
{
  "gates": [
    {
      "name": "no-todo",
      "cmd": ["python3", "gates/no_todo.py", "{target}"],
      "good":  ["fixtures/good"],
      "bad":   ["fixtures/bad"],
      "empty": true,
      "missing": true,
      "unmeasured_exit": 3,
      "exemptions": [{ "item": "legacy/", "reason": "vendored, upstream owns it" }]
    }
  ]
}
```

- `{target}` is replaced with a fixture path. Exit codes: `0` pass, `3` = *could not measure*
  (never counts as pass), anything else = fail.
- `empty: true` creates an empty directory and requires the gate NOT to exit 0.
- `missing: true` points the gate at a path that does not exist and requires NOT 0.

## Rules of thumb

- A forgery test must fail when you revert the rule. Delete the fix, watch it go red, restore.
- Measuring a *symptom* often cannot be forged; find the cause (e.g. an EXIF flag) and test that.
- "Could not measure" gets its own exit code. Never collapse it into 0.
- Two gates reading the same artifact should share one parser. Copies drift apart.

## Command trust and exit contract

The spec executes local commands; only run specs you trust. This is not a sandbox. Each gate must include at least one existing good and bad fixture. Bad fixtures must return `reject_exit` (default 1), not an arbitrary failure such as a missing executable or timeout. `unmeasured_exit` defaults to 3. Empty/missing probes accept rejection, unmeasured, or input-error exit 2. A gate crashing with its own configured rejection code still needs an output-level assertion in the gate-specific tests.
