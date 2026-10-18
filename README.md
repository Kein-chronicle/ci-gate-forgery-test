# ci-gate-forgery-test

**Prove your CI gates can actually fail: feed each gate forged-bad, empty and missing input and flag the ones that stay green.**

[![test](https://github.com/Kein-chronicle/ci-gate-forgery-test/actions/workflows/test.yml/badge.svg)](https://github.com/Kein-chronicle/ci-gate-forgery-test/actions/workflows/test.yml) ![license](https://img.shields.io/badge/license-MIT-blue.svg) ![dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)

## Why

A gate that has never been seen failing is decoration. Mutation testing checks whether tests catch broken code; this checks whether a gate catches broken input, and whether it fails closed when it measured nothing.

## Install

**As a Claude Code skill** (Claude uses it when the task matches the skill description):

```sh
git clone https://github.com/Kein-chronicle/ci-gate-forgery-test.git ~/.claude/skills/gate-forgery-test
```

For a single project, clone into `<project>/.claude/skills/gate-forgery-test` instead, then start a new Claude Code session.

**As plain scripts:**

```sh
git clone https://github.com/Kein-chronicle/ci-gate-forgery-test.git
cd ci-gate-forgery-test
```

**Requires:** Python 3.10+ and bash.

## Quick start

Run it against a good gate and a blind one:

```console
$ bash examples/demo.sh
# A gate that really detects TODOs: every forged case behaves
$ python3 scripts/forge_test.py examples/spec.json
[ok         ] no-todo (correct)  wiring          python3 resolves
[ok         ] no-todo (correct)  wiring          no_todo_good.py exists
[ok         ] no-todo (correct)  forgery         bad fixture fixtures/bad: exit 1
[ok         ] no-todo (correct)  false-positive  good fixture fixtures/good: exit 0
[ok         ] no-todo (correct)  vacuity         empty input: exit 3 (0 would mean 'nothing measured = clean')
[ok         ] no-todo (correct)  vacuity         missing input: exit 2
[ok         ] no-todo (correct)  exemption       legacy/: reason given

all gates behaved
[exit 0]

# A gate that always passes (blind): the forgery test catches it
$ python3 scripts/forge_test.py examples/spec_blind.json
[ok         ] no-todo (vacuous)  wiring          python3 resolves
[ok         ] no-todo (vacuous)  wiring          no_todo_vacuous.py exists
[ok         ] no-todo (vacuous)  forgery         bad fixture fixtures/bad: exit 1
[ok         ] no-todo (vacuous)  false-positive  good fixture fixtures/good: exit 0
[BLIND/NOISY] no-todo (vacuous)  vacuity         empty input: exit 0 (0 would mean 'nothing measured = clean')
[BLIND/NOISY] no-todo (vacuous)  vacuity         missing input: exit 0
[BLIND/NOISY] no-todo (vacuous)  exemption       legacy/: NO REASON - a bare exemption reopens the hole

3 problem(s): fix the gate before trusting its green
[exit 1]
```

The output above is real: it is produced by the files in `examples/`.

## Use it on your own files

```sh
python3 scripts/forge_test.py my-gates-spec.json
```

Sample inputs for every file format are in `examples/` and `tests/`; the details are in [SKILL.md](SKILL.md).

## What it checks

- For each gate in a JSON spec it runs: a known-bad fixture (must fail), a known-good fixture (must pass), an empty input and a missing input (must not pass).
- Checks wiring: the interpreter resolves and the gate script exists.
- Every exemption must carry a reason; a bare exemption is reported.
- Exit `0` every case behaved, `1` at least one blind or noisy gate, `2` missing or malformed spec or no gates.

## Limits

- You supply the bad fixtures; the tool cannot invent a realistic defect for your domain.
- A spec lists commands that are executed (without a shell): only run specs you trust.

## Related projects

These solve neighbouring problems; use them when they fit better.

- **Stryker / mutmut**: mutation testing: mutate the code under test

## More from the same collection

Small, tested tools that grew out of running AI agents and game/app pipelines for months:

- [**llm-verdict-gate**](https://github.com/Kein-chronicle/llm-verdict-gate): Make AI and human review gates impossible to pass by silence: machine-parsed PASS/FAIL, missing verdict = FAIL.
- [**stale-verdict-guard**](https://github.com/Kein-chronicle/stale-verdict-guard): Bind a pass/fail verdict to a fingerprint of the source it judged, so an edit after review makes the verdict stale.
- [**agent-definition-of-done-gate**](https://github.com/Kein-chronicle/agent-definition-of-done-gate): A completion rule for AI agents: a human can't close a gate that has an automated measurement, and parking work needs evidence.

## Development

```sh
bash run_tests.sh
```

The tests include inputs that are supposed to be rejected, so a green run also shows the checks can fail. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).

If this saved you a debugging session, a star helps other people find it. Bug reports and failing test cases are even better.

<sub>Keywords: testing, quality-gates, ci, claude-code, claude-skills, agent-skills, mutation-testing, test-quality</sub>
