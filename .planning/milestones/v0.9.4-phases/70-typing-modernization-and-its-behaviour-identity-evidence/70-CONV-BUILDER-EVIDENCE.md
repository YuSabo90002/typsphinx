# Phase 70 — Conversion: typsphinx/builder.py

BASE_70_05 = 6d75e9d5b9254be7f3ff3712b61878a7ae85d332
(from `git rev-parse HEAD` at the start of this plan's execution, before any commit)

## Head check and provisioning

Fresh measurements at the start of this plan's execution, in this worktree.

```
$ date -u +%FT%TZ
2026-09-13T05:04:45Z
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa03dac9c9a0f3cd8
$ test -f .git; echo "exit:$?"
exit:0
$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

Preconditions (task 1's `<precondition>`), each checked before any conversion:

```
$ grep -n "^PILOT_TRANSLATOR\|^PILOT_LEDGER\|^CONTROL_RENAME\|^CONTROL_IMPORT\|^MASK_HARNESS_SHA256" 70-MASK-PILOT-EVIDENCE.md
MASK_HARNESS_SHA256 = 11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65
PILOT_TRANSLATOR = EQUAL
PILOT_LEDGER = EQUAL
CONTROL_RENAME = DIFFER
CONTROL_IMPORT = DIFFER
$ grep -q '^## HALT' 70-MASK-PILOT-EVIDENCE.md && echo HALT_FOUND || echo NO_HALT
NO_HALT
```
All four keys hold their expected values, with no HALT heading — the pilot's harness is proven
non-vacuous and both pilot files hashed EQUAL to base.

```
$ git log --format=%H 697a113221a8a267d7e8c6dd1f2b95672f9454d2..HEAD -- CLAUDE.md
3c5e281cccf7efea39fe38ffc10c72ebe74d95fa
```
Exactly one CLAUDE.md commit since `PHASE_BASE_SHA`.

```
$ git merge-base --is-ancestor 697a113221a8a267d7e8c6dd1f2b95672f9454d2 HEAD; echo "exit:$?"
exit:0
```
`PHASE_BASE_SHA` is an ancestor of HEAD (this plan's fork point, `BASE_70_05`), and the single
CLAUDE.md commit `3c5e281c` is itself an ancestor of `BASE_70_05` (it is the only commit between
`PHASE_BASE_SHA` and `BASE_70_05` touching `CLAUDE.md`, and `BASE_70_05` IS `HEAD` at fork time).

```
$ git diff --quiet 697a113221a8a267d7e8c6dd1f2b95672f9454d2 HEAD -- typsphinx/builder.py; echo "exit:$?"
exit:0
```
`typsphinx/builder.py` is unchanged between `PHASE_BASE_SHA` and this plan's fork point — the
conversion below is the first edit this file receives.

Provisioning: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`
exited 0, installing 90 packages including `typsphinx==0.9.2` (editable, this worktree's own path),
`ruff==0.16.6`, `mypy==2.3.1`, `myst-parser==5.1.0` (docs extra present), `pytest==9.1.1`.

`.venv/pyvenv.cfg`:
```
home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
implementation = CPython
uv = 0.11.25
version_info = 3.13.13
include-system-site-packages = false
prompt = typsphinx
```

VENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
VENV_VERSION_INFO = 3.13.13

Both keys equal 70-02's recorded `VENV_HOME`/`VENV_VERSION_INFO` exactly — same interpreter,
confirming constraint 6.

## Conversion

```
$ uv run ruff check typsphinx/builder.py --select UP006,UP035 --output-format=concise
[... 30 diagnostic lines ...]
Found 30 errors.
[*] 26 fixable with the `--fix` option.
exit:1
```
30 findings, matching `70-BASELINE-EVIDENCE.md`'s per-file breakdown for `typsphinx/builder.py`
(`30`). Non-zero finding count confirmed before any fix.

Pass 1: `uv run ruff check typsphinx/builder.py --select UP006,UP035 --fix`
```
Found 30 errors (26 fixed, 4 remaining).
exit:1
```
The 4 remaining are the file's own `from typing import Any, Dict, List, Set, Tuple` header line
(one UP035 diagnostic per removed name) — not independently fixable by the `--select`-scoped pass
because the header rewrite is a config-rule concern (I001/F401), covered by pass 2.

Pass 2: `uv run ruff check typsphinx/builder.py --fix`
```
Found 4 errors (4 fixed, 0 remaining).
exit:0
```
This pass used the config rules, shrinking the header line in place to `from typing import Any`.
No hand edit was made. `sed`, `--preview` and `--unsafe-fixes` were never invoked.

Confirming both scoped and config-rule passes now exit 0:
```
$ uv run ruff check typsphinx/builder.py --select UP006,UP035
All checks passed!
exit1:0
$ uv run ruff check typsphinx/builder.py
All checks passed!
exit2:0
```

Typing and `collections.abc` import lines, quoted from the converted file:
```
from collections.abc import Iterator
from os import path
from typing import Any
```
`from collections.abc import Iterator` (line 11) is untouched. `from typing import Any` (line 13)
is the sole survivor of the typing import shrink.

`git diff --stat -- typsphinx/builder.py`:
```
 typsphinx/builder.py | 34 +++++++++++++++++-----------------
 1 file changed, 17 insertions(+), 17 deletions(-)
```

Every changed line is a `Dict`/`List`/`Set`/`Tuple` → `dict`/`list`/`set`/`tuple` rename or the one
header-line shrink; confirmed in full by the Task 2 changed-line census below. Docstring prose
("Iterator of document names" at line ~1601, "Set of document names" at line ~1649) and the
`@preview` lines are untouched — no diff hunk touches either.

Commit: `3cda095a` — `refactor(70-05): move builder.py onto builtin generics (QUA-11)`, touching
only `typsphinx/builder.py`.

## Leg (a)

Harness extracted per the worktree_provisioning block:
```
$ H="$(sed -n '/^~~~python mask-harness$/,/^~~~$/p' "$PE" | sed '1d;$d')"
$ printf '%s\n' "$H" | sha256sum
11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65  -
```
Equal to `MASK_HARNESS_SHA256`. Confirmed before use; never retyped (the harness was extracted
verbatim by `sed` into a script file and run with `uv run python <script> < <input>`, which is
byte-for-byte equivalent to `uv run python -c "$H"` for a harness that only reads stdin).

```
$ git show "697a113221a8a267d7e8c6dd1f2b95672f9454d2:typsphinx/builder.py" | sk
dd763862e7a610157eab1ee2c4ba675e1801d09e27e9bb3b8c614495522165e4
$ sk < typsphinx/builder.py
dd763862e7a610157eab1ee2c4ba675e1801d09e27e9bb3b8c614495522165e4
```
Both hashes are 64-character hex digests and are equal.

BUILDER_MASK = EQUAL

## Changed-line census

Over `git diff "$PHASE_BASE_SHA" HEAD -- typsphinx/builder.py`, with diff headers (`+++`/`---`) and
blank added/removed lines excluded:

```
$ git diff 697a113221a8a267d7e8c6dd1f2b95672f9454d2 HEAD -- typsphinx/builder.py | grep -E '^[+-]' \
    | grep -vE '^(\+\+\+|---)( |$)' | grep -vE '^[+-][[:space:]]*$' \
    | grep -cvE '(Dict|List|Set|Tuple|Iterator|dict|list|set|tuple|typing|collections\.abc)'
0
```

NON_TYPING_LINES_70_05 = 0
(every non-blank changed line carries a typing name)

```
$ git diff 697a113221a8a267d7e8c6dd1f2b95672f9454d2 HEAD -- typsphinx/builder.py | grep -E '^[+-]' \
    | grep -vE '^(\+\+\+|---)( |$)' | grep -cwE 'assert|@preview'
0
```
No changed line contains `assert` or `@preview`.

## Gates

```
$ uv run black --check typsphinx/builder.py
All done! ✨ 🍰 ✨
1 file would be left unchanged.
exit:0
```

```
$ uv run ruff check .
All checks passed!
exit:0
```
Repo-wide, config-rule ruff is clean — the still-present `UP006`/`UP035` ignores mean this check
does not itself re-verify `builder.py`'s UP006/UP035 cleanliness (Task 1 already did, with
`--select` explicitly overriding the ignores); it confirms the conversion introduced no other
config-rule violation anywhere in the repo, including in the other three wave-3 siblings'
in-flight, uncommitted-to-this-branch changes (not visible from this worktree).

```
$ uv run mypy typsphinx/ 2>/dev/null
Success: no issues found in 9 source files
```

MYPY_STDOUT_SHA256_70_05 = 46984ca20bf69f7b14ec1fd9bd82101d56a4e109e68f016fd2a04f22481b09b3
(stdout only, stderr excluded — equal to `MYPY_STDOUT_SHA256_BEFORE`)

```
$ LC_ALL=C uv run pytest -q -rs -p no:cacheprovider > pytest_out.txt 2>&1; echo "exit:$?"
exit:0
$ tail -n 1 pytest_out.txt
================= 1547 passed, 1 skipped in 131.92s (0:02:11) ==================
```

PYTEST_RESULT_70_05 = 1547 passed 1 skipped
(from the same `grep -oE '[0-9]+ (passed|failed|skipped|errors?|xfailed|xpassed)' | paste -sd' '`
extraction 70-02 used — equal to `PYTEST_RESULT_BEFORE`)

Both leg (e) (mypy) and leg (b) (pytest) are unchanged from base: the conversion altered no runtime
behaviour, no type-checking outcome, and no test outcome.

`git diff --name-only BASE_70_05 HEAD` (quoted verbatim):
```
.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONV-BUILDER-EVIDENCE.md
typsphinx/builder.py
```
Only this plan's two declared files changed (the SUMMARY is added and committed after this
evidence file, per the plan's own `<output>` step) — confirming isolation from the three
file-disjoint wave-3 siblings (70-06, 70-07, 70-08).
