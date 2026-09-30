# Phase 70 — After-side Static Evidence

BASE_70_10 = 44c43e345f8d5916486e5b7c2790bcb16c58f9d0
(from `git rev-parse HEAD` at the start of this plan's execution, before any commit)

## Head check and provisioning

Fresh measurements at the start of this plan's execution, in this worktree.

```
$ date -u +%FT%TZ
2026-09-13T05:39:40Z
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aacdace25a411b095
$ grep -q typsphinx-fhs-run "$(command -v uv)" && echo SHIM_OK
SHIM_OK
```

Precondition for Task 1: `70-FLIP-EVIDENCE.md` exists at HEAD with no `## HALT` heading, and
exactly one commit since `PHASE_BASE_SHA` touches `pyproject.toml`.

```
$ grep -q '^## HALT' .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-FLIP-EVIDENCE.md && echo HALT_FOUND || echo NO_HALT
NO_HALT
$ git log --format=%H 697a113221a8a267d7e8c6dd1f2b95672f9454d2..HEAD -- pyproject.toml
0224b5ea7f565dfcf7db0a9d8b4394a6a815524d
```

One commit (`0224b5ea`), no HALT — precondition met.

Provisioning: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`
exited 0, installing 90 packages including `ruff==0.16.6`, `mypy==2.3.1`, `myst-parser==5.1.0`
(docs extra present), `pytest==9.1.1`.

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

RUFF_VERSION_AFTER = ruff 0.16.6
(from `uv run ruff --version 2>/dev/null`)

`RUFF_VERSION_AFTER` equals `RUFF_VERSION_BASE` (`70-BASELINE-EVIDENCE.md`, `ruff 0.16.6`) — no
dependabot ruff bump moved the baseline mid-conversion (constraint 4, QUA-09/concurrency edge).

## Changed-file set

`PHASE_BASE_SHA` (`B`) = `697a113221a8a267d7e8c6dd1f2b95672f9454d2`.

```
$ git diff --name-only "$B" HEAD -- . ':(exclude).planning' | LC_ALL=C sort
CLAUDE.md
pyproject.toml
tests/conftest.py
tests/test_bundle_layout_sweep_gate.py
tests/test_include_edge_derivation_unit.py
tests/test_include_ledger_removal_gate.py
typsphinx/__init__.py
typsphinx/builder.py
typsphinx/template_engine.py
typsphinx/template_registry.py
typsphinx/translator.py
typsphinx/writer.py
```

This is exactly `CLAUDE.md`, `pyproject.toml` and the ten `up-files` paths from
`70-BASELINE-EVIDENCE.md`, sorted identically — no other path is present. No `## HALT` needed.

## SC#2 static checks

**`[tool.ruff.lint]` section — no `UP006`/`UP035`:**

```
$ sed -n '/^\[tool\.ruff\.lint\]/,/^\[/p' pyproject.toml
[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "T20"]
ignore = [
    "E501",   # Line too long (handled by black)
    "T201",   # print found (used in tests for debugging)
    "B017",   # asserting blind exception in tests
    "UP028",  # yield from (minor optimization)
    "N802",   # Function naming (docutils visitor pattern uses PascalCase)
    "A001",   # Shadowing builtins (copyright in conf.py is Sphinx convention)
    "F841",   # Unused variable (acceptable in tests and mocks)
]

[tool.mypy]
```

Neither `UP006` nor `UP035` appears. PASS.

**Fresh repo-wide ruff, against `UP_TOTAL_BASE` = 113 (non-zero):**

```
$ uv run ruff check . --select UP006,UP035
All checks passed!
$ echo "exit:$?"
exit:0
$ uv run ruff check .
All checks passed!
$ echo "exit:$?"
exit:0
```

Both exit 0. PASS (base was non-zero: `UP_TOTAL_BASE = 113`).

**No `preview` setting, no `--preview` flag:**

```
$ grep -nE '^[[:space:]]*preview[[:space:]]*=' pyproject.toml; echo "exit:$?"
exit:1
$ grep -qF -- '--preview' tox.ini .github/workflows/ci.yml; echo "exit:$?"
exit:1
```

Both exit 1 (no match). PASS.

**Typing-import grep (banned names), HEAD vs. `PHASE_BASE_SHA` positive control:**

```
$ RX='^[[:space:]]*from typing import (.*[ ,])?(Dict|List|Set|Tuple|Iterator)([ ,]|$)'
$ git grep -nE "$RX" HEAD -- 'typsphinx/*.py' 'tests/*.py'; echo "exit:$?"
exit:1
```
Empty at HEAD (exit 1, no match). PASS.

```
$ git grep -nE "$RX" 697a113221a8a267d7e8c6dd1f2b95672f9454d2 -- 'typsphinx/*.py' 'tests/*.py'
697a113221a8a267d7e8c6dd1f2b95672f9454d2:tests/conftest.py:6:from typing import Any, Dict
697a113221a8a267d7e8c6dd1f2b95672f9454d2:tests/test_bundle_layout_sweep_gate.py:42:from typing import Dict, List
697a113221a8a267d7e8c6dd1f2b95672f9454d2:tests/test_include_edge_derivation_unit.py:25:from typing import Dict, List
697a113221a8a267d7e8c6dd1f2b95672f9454d2:tests/test_include_ledger_removal_gate.py:47:from typing import Dict, Iterator, Set
697a113221a8a267d7e8c6dd1f2b95672f9454d2:typsphinx/__init__.py:15:from typing import Any, Dict
697a113221a8a267d7e8c6dd1f2b95672f9454d2:typsphinx/builder.py:13:from typing import Any, Dict, List, Set, Tuple
697a113221a8a267d7e8c6dd1f2b95672f9454d2:typsphinx/template_engine.py:13:from typing import Any, Dict, List
697a113221a8a267d7e8c6dd1f2b95672f9454d2:typsphinx/template_registry.py:29:from typing import Any, Dict
697a113221a8a267d7e8c6dd1f2b95672f9454d2:typsphinx/translator.py:9:from typing import Any, Dict, List, NamedTuple, Tuple
697a113221a8a267d7e8c6dd1f2b95672f9454d2:typsphinx/writer.py:10:from typing import Any, Tuple
```
10 lines at base (non-empty, exit 0) — positive control confirms the grep is not broken. PASS.

**`typsphinx/__init__.py:15`:**

```
$ sed -n 15p typsphinx/__init__.py
from typing import Any
```
Exact match. PASS.

**The four SC#2 counts, HEAD vs. `_BASE`:**

```
$ git grep -hoE 'from __future__ import annotations' HEAD -- 'typsphinx/*.py' 'tests/*.py' | wc -l
0
$ git grep -hoE 'Optional\[' HEAD -- 'typsphinx/*.py' 'tests/*.py' | wc -l
0
$ git grep -hoE 'Union\[' HEAD -- 'typsphinx/*.py' 'tests/*.py' | wc -l
0
$ git grep -hoE '[|] None' HEAD -- 'typsphinx/*.py' 'tests/*.py' | wc -l
82
```

FUTURE_ANNOTATIONS_AFTER = 0
OPTIONAL_AFTER = 0
UNION_AFTER = 0
PIPE_NONE_AFTER = 82

Each equals its `_BASE` key (`FUTURE_ANNOTATIONS_BASE = 0`, `OPTIONAL_BASE = 0`, `UNION_BASE = 0`,
`PIPE_NONE_BASE = 82`). PASS — no PEP 604 sweep or `__future__` import happened, and the 82
`X | None` pipes are unchanged (Edge QUA-11/adjacency).

**The three vanish files carry no `from typing import` line:**

```
$ grep -nE '^from typing import' tests/test_bundle_layout_sweep_gate.py tests/test_include_edge_derivation_unit.py tests/test_include_ledger_removal_gate.py; echo "exit:$?"
exit:1
```
Empty (exit 1). PASS (Edge QUA-11/empty).

**No `@preview` line in the milestone diff for `typsphinx/`/`tests/`; templates unchanged:**

```
$ git diff "$B" HEAD -- typsphinx tests | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)( |$)' | grep -F '@preview'; echo "exit:$?"
exit:1
$ git diff --quiet "$B" HEAD -- typsphinx/templates; echo "exit:$?"
exit:0
```
No `@preview` diff line; `typsphinx/templates/` byte-identical to base. PASS.

**`tests/test_authors_pipeline_stage_gate.py` absent from the diff, `ast.Dict` intact at line 515:**

```
$ git diff --quiet "$B" HEAD -- tests/test_authors_pipeline_stage_gate.py; echo "exit:$?"
exit:0
$ sed -n 515p tests/test_authors_pipeline_stage_gate.py
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
```
Untouched, `ast.Dict` present. PASS.

Every check above holds.

SC2_VERDICT = MET

## Leg (a) — every converted file

Harness extraction and hash check (from `70-MASK-PILOT-EVIDENCE.md`):

```
$ H="$(sed -n '/^~~~python mask-harness$/,/^~~~$/p' 70-MASK-PILOT-EVIDENCE.md | sed '1d;$d')"
$ printf '%s\n' "$H" | sha256sum
11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65  -
```

MASK_HARNESS_SHA256 (this run) = 11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65
Equal to `70-MASK-PILOT-EVIDENCE.md`'s recorded `MASK_HARNESS_SHA256`. Confirmed, then run as
`sk() { uv run python -c "$H"; }`.

For each path in the `up-files` block, the masked hash of the HEAD file vs. the masked hash of
`git show "$B:<path>"`:

| Path | Base masked hash | HEAD masked hash | Verdict |
|---|---|---|---|
| tests/conftest.py | e86284ce44fd0afa1077e595be4b05080990810c11657b03ed430f9e24c31a6e | e86284ce44fd0afa1077e595be4b05080990810c11657b03ed430f9e24c31a6e | EQUAL |
| tests/test_bundle_layout_sweep_gate.py | 813565e78879f6fd6637a267a4da432acf3b988d75662ee610435e80473de84b | 813565e78879f6fd6637a267a4da432acf3b988d75662ee610435e80473de84b | EQUAL |
| tests/test_include_edge_derivation_unit.py | adffe23b45742160fba01dd0668dc92c4944976c2d10d58bf84aeb5bdc617d8a | adffe23b45742160fba01dd0668dc92c4944976c2d10d58bf84aeb5bdc617d8a | EQUAL |
| tests/test_include_ledger_removal_gate.py | 6af6dd86276c3acb15479940e325e6db77931ec60d7b0a444c7d2e3bc7204849 | 6af6dd86276c3acb15479940e325e6db77931ec60d7b0a444c7d2e3bc7204849 | EQUAL |
| typsphinx/__init__.py | 6b44c4dc942282ea3b94733831b5f343793d9ec453fa5fcde7899d6da1d34b7b | 6b44c4dc942282ea3b94733831b5f343793d9ec453fa5fcde7899d6da1d34b7b | EQUAL |
| typsphinx/builder.py | dd763862e7a610157eab1ee2c4ba675e1801d09e27e9bb3b8c614495522165e4 | dd763862e7a610157eab1ee2c4ba675e1801d09e27e9bb3b8c614495522165e4 | EQUAL |
| typsphinx/template_engine.py | 7288a028075f8d778fdfa1a64ae89ea5af60a8ac720e6e30d222bc77e6c8d822 | 7288a028075f8d778fdfa1a64ae89ea5af60a8ac720e6e30d222bc77e6c8d822 | EQUAL |
| typsphinx/template_registry.py | 655662483067c768432fe0ddcd6bb8ad9c101b50897a7ae4fb8ce0db77e421dc | 655662483067c768432fe0ddcd6bb8ad9c101b50897a7ae4fb8ce0db77e421dc | EQUAL |
| typsphinx/translator.py | 8c766e23d771c614aa166b6ebe9ea481b8969a9b0726ed31eea2b176afe3c329 | 8c766e23d771c614aa166b6ebe9ea481b8969a9b0726ed31eea2b176afe3c329 | EQUAL |
| typsphinx/writer.py | ef10bdb40b105c61d0bdaa73749ffa62c1050a93a1833ae41cdf1f40fdc9bc08 | ef10bdb40b105c61d0bdaa73749ffa62c1050a93a1833ae41cdf1f40fdc9bc08 | EQUAL |

All 10 files EQUAL.

LEG_A_EQUAL_COUNT = 10

Equal to `UP_FILE_COUNT_BASE` (`10`).

**Pilot ordering.** The commit that added the pilot evidence (`70-MASK-PILOT-EVIDENCE.md`):

```
$ git log --diff-filter=A --format=%H "$B"..HEAD -- .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-MASK-PILOT-EVIDENCE.md
64eafb52fc256b41ff392fbc1670e898e7f8c23a
```
One commit. It must be an ancestor of every wave-3 conversion commit over the eight files
(builder.py, template_engine.py, template_registry.py, writer.py, `__init__.py`, and the three
tests converted by 70-08):

```
$ git log --format=%H "$B"..HEAD -- typsphinx/builder.py typsphinx/template_engine.py typsphinx/template_registry.py typsphinx/writer.py typsphinx/__init__.py tests/conftest.py tests/test_bundle_layout_sweep_gate.py tests/test_include_edge_derivation_unit.py
e721ff899a981eafdad696ef1a9c93aaab41ece5
3fb256d86211a89199a7488154246b292dccc72c
0f8ca546a5049a0819eeb091721fcdae950e6f08
3b4738948fbada7fde7203b01e77836199b65cd1
a7f35d33cf43d34b3f6b3c389d8dac8a93e1774b
47159f965ae6c962dbf77ac826c5e408c954ebd1
3cda095a809ed04d3977d3cc9adc135a737528d8
```
`git merge-base --is-ancestor 64eafb52fc256b41ff392fbc1670e898e7f8c23a <c>` exits 0 for every one
of the 7 commits listed. (The eight files above land in 7 distinct commits.) PASS — the pilot was
recorded before the check was automated.

PILOT_BEFORE_AUTOMATION = YES

Leg (a) proves the non-import, non-annotation code (statements, expressions, calls, control flow)
is structurally unchanged in every converted file. It does not independently prove the import list
itself is correct — that an annotation-referenced name (e.g. `Any`) stayed imported — which legs
(b) and (e) close instead (mypy would flag an undefined name; pytest collection would fail to
import a broken module).

LEG_A_VERDICT = MET

## Leg (c) — tests/

```
$ git diff --name-only "$B" HEAD -- tests/ | LC_ALL=C sort
tests/conftest.py
tests/test_bundle_layout_sweep_gate.py
tests/test_include_edge_derivation_unit.py
tests/test_include_ledger_removal_gate.py
```
Exactly the four converted test files.

Per-file added/removed line counts (`git diff --numstat`):

| File | Added | Removed |
|---|---|---|
| tests/conftest.py | 2 | 2 |
| tests/test_bundle_layout_sweep_gate.py | 4 | 5 |
| tests/test_include_edge_derivation_unit.py | 1 | 2 |
| tests/test_include_ledger_removal_gate.py | 7 | 7 |

Changed non-blank lines without a typing name:

```
$ git diff "$B" HEAD -- tests/ | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)( |$)' | grep -vE '^[+-][[:space:]]*$' | grep -vE '(Dict|List|Set|Tuple|Iterator|dict|list|set|tuple|typing|collections\.abc)'
(empty — exit 1)
```

LEG_C_NON_TYPING_LINES = 0

Changed lines containing `assert`:

```
$ git diff "$B" HEAD -- tests/ | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)( |$)' | grep -w assert
(empty — exit 1)
```

LEG_C_ASSERT_LINES = 0

Every changed line in `tests/` is an import or annotation line naming a typing/builtin-generic
type, and no changed line touches an `assert` statement — read off `git diff`, not asserted.

LEG_C_VERDICT = MET

## Leg (e) — mypy

```
$ uv run mypy --version 2>/dev/null
mypy 2.3.1 (compiled: yes)
```

MYPY_VERSION_AFTER = mypy 2.3.1 (compiled: yes)

Equal to `MYPY_VERSION_BASE` (`70-BASELINE-EVIDENCE.md`, `mypy 2.3.1 (compiled: yes)`).

```
$ uv run mypy typsphinx/ 2>/dev/null > "$(mktemp)"; echo "exit:$?"
exit:0
```

MYPY_EXIT_AFTER = 0

```
$ uv run mypy typsphinx/ 2>/dev/null | sha256sum
46984ca20bf69f7b14ec1fd9bd82101d56a4e109e68f016fd2a04f22481b09b3  -
```

MYPY_STDOUT_SHA256_AFTER = 46984ca20bf69f7b14ec1fd9bd82101d56a4e109e68f016fd2a04f22481b09b3

Equal to `MYPY_STDOUT_SHA256_BEFORE` (`70-BASELINE-EVIDENCE.md`,
`46984ca20bf69f7b14ec1fd9bd82101d56a4e109e68f016fd2a04f22481b09b3`).

Stdout verbatim (identical on both sides):
```
Success: no issues found in 9 source files
```

Both sides use the same interpreter (`VENV_HOME`/`VENV_VERSION_INFO` recorded above, equal to
70-02's) and the same `uv.lock`-pinned mypy version.

LEG_E_VERDICT = MET

## SC#1 — commit order

`PHASE_BASE_SHA` (`B`) = `697a113221a8a267d7e8c6dd1f2b95672f9454d2`.

**`CLAUDE_COMMIT` — the only commit since `B` touching `CLAUDE.md`:**

```
$ git log --format=%H "$B"..HEAD -- CLAUDE.md
3c5e281cccf7efea39fe38ffc10c72ebe74d95fa
$ git show --name-only --format= 3c5e281cccf7efea39fe38ffc10c72ebe74d95fa
CLAUDE.md
```
One commit, touching only `CLAUDE.md`.

CLAUDE_COMMIT = 3c5e281cccf7efea39fe38ffc10c72ebe74d95fa

**`FLIP_COMMIT` — the only commit since `B` touching `pyproject.toml`:**

```
$ git log --format=%H "$B"..HEAD -- pyproject.toml
0224b5ea7f565dfcf7db0a9d8b4394a6a815524d
$ git show --name-status -M --format= 0224b5ea7f565dfcf7db0a9d8b4394a6a815524d
R100	.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md	.planning/todos/completed/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md
M	pyproject.toml
```
Exactly `M pyproject.toml` plus the R100 todo rename from `pending/` to `completed/`.

FLIP_COMMIT = 0224b5ea7f565dfcf7db0a9d8b4394a6a815524d

**Conversion commits over the ten census files, ordered between `CLAUDE_COMMIT` and `FLIP_COMMIT`:**

```
$ git log --format=%H "$B"..HEAD -- <ten up-files paths>
e721ff899a981eafdad696ef1a9c93aaab41ece5
3fb256d86211a89199a7488154246b292dccc72c
0f8ca546a5049a0819eeb091721fcdae950e6f08
3b4738948fbada7fde7203b01e77836199b65cd1
a7f35d33cf43d34b3f6b3c389d8dac8a93e1774b
47159f965ae6c962dbf77ac826c5e408c954ebd1
3cda095a809ed04d3977d3cc9adc135a737528d8
b4d044d487f7255eeac696f0f46bbaf9d2101167
```

| Commit | `is-ancestor CLAUDE_COMMIT <c>` | `is-ancestor <c> FLIP_COMMIT` |
|---|---|---|
| e721ff899a981eafdad696ef1a9c93aaab41ece5 | exit 0 | exit 0 |
| 3fb256d86211a89199a7488154246b292dccc72c | exit 0 | exit 0 |
| 0f8ca546a5049a0819eeb091721fcdae950e6f08 | exit 0 | exit 0 |
| 3b4738948fbada7fde7203b01e77836199b65cd1 | exit 0 | exit 0 |
| a7f35d33cf43d34b3f6b3c389d8dac8a93e1774b | exit 0 | exit 0 |
| 47159f965ae6c962dbf77ac826c5e408c954ebd1 | exit 0 | exit 0 |
| 3cda095a809ed04d3977d3cc9adc135a737528d8 | exit 0 | exit 0 |
| b4d044d487f7255eeac696f0f46bbaf9d2101167 | exit 0 | exit 0 |

Every conversion commit descends from `CLAUDE_COMMIT` and is an ancestor of `FLIP_COMMIT`.

CONVERSION_COMMIT_COUNT = 8

**Todo move and pending-path census:**

```
$ test -f .planning/todos/completed/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md; echo "exit:$?"
exit:0
$ test -e .planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md; echo "exit:$?"
exit:1
```
The todo exists in `completed/` and not in `pending/`.

```
$ git grep -n 'todos/pending/2026-07-22-modernize' HEAD -- . ':!.planning'; echo "exit:$?"
exit:1
```
Empty at HEAD — zero tracked references to the pending path outside `.planning/`.

```
$ git grep -n 'todos/pending/2026-07-22-modernize' 0224b5ea7f565dfcf7db0a9d8b4394a6a815524d^ -- . ':!.planning'
0224b5ea7f565dfcf7db0a9d8b4394a6a815524d^:pyproject.toml:128:    "UP035",  # typing.Dict/List/Set deprecation; modernization deferred (see .planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md)
```
One line at `FLIP_COMMIT^` (the pre-flip commit) — positive control confirming the grep is not
broken and the last reference disappeared in the same commit that moved the todo.

## SC#1 — CLAUDE.md read at two commits

Extracting the line beginning `- **Python 3.12+ is required.**`:

```
$ git show 0224b5ea7f565dfcf7db0a9d8b4394a6a815524d^:CLAUDE.md | grep '^- \*\*Python 3\.12+ is required\.\*\*'
- **Python 3.12+ is required.** Annotations use builtin generics (`dict[str, Any]`, `list[str]`, `set[str]`, `tuple[str, ...]`) and take abstract types such as `Iterator` from `collections.abc`, not `typing.Dict`/`List`/`Set`/`Tuple`/`Iterator`.
$ git show HEAD:CLAUDE.md | grep '^- \*\*Python 3\.12+ is required\.\*\*'
- **Python 3.12+ is required.** Annotations use builtin generics (`dict[str, Any]`, `list[str]`, `set[str]`, `tuple[str, ...]`) and take abstract types such as `Iterator` from `collections.abc`, not `typing.Dict`/`List`/`Set`/`Tuple`/`Iterator`.
```

The two lines are byte-identical.

Each contains `dict[str, Any]`, `list[str]`, `collections.abc`, `Iterator` and `typing.Dict`
(D-01 tokens: all present).

Each contains none of `UP006`, `UP035`, `ignore`, `deferral`, `todos/pending` and `odernize`
(D-02), and neither `__future__` nor `604` (D-03) — checked by literal substring search against
the quoted bullet text above; none of these tokens appear.

**Reading at `FLIP_COMMIT^` (the last pre-flip commit):** the ignores are still present in
`pyproject.toml`, and the bullet makes no claim about them — it states only that annotations use
builtin generics and `collections.abc`, an instruction about how to write code. Every one of the
ten census files already uses that shape by this commit (the conversion commits above all precede
`FLIP_COMMIT`), so the bullet reads true here even though ruff has not yet started enforcing it.

**Reading at HEAD (the post-flip tip):** `ruff check .` now enforces `UP006`/`UP035`, but the
bullet's text is unchanged from `FLIP_COMMIT^` and still makes no claim about ruff's
configuration — it never mentions ruff, `ignore`, or a rule code. The same instruction is now also
the enforced rule, but nothing about the bullet's own wording became stale or false when the
ignore lines were removed.

CLAUDE_BULLET_IDENTICAL = YES

SC1_VERDICT = MET
