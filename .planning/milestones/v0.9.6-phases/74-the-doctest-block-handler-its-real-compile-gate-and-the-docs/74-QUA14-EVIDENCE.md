# Phase 74 — QUA-14 Evidence (census-derived docstring repairs)

BASE_74_04 = cf68ab4a4c9e6f1a14124602f17324e9bcd061a0
SCRATCH_74_04 = /tmp/tmp.xzhoIOQscX
PYVENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
PYVENV_VERSION_INFO = 3.13.13
AFTER_TOCTREE_ATTRIBUTED_COUNT = 0
AFTER_TOCTREE_RAW_TOTAL = 4
FIX_RAW_UNEXPECTED_INDENTATION = 0
FIX_RAW_BLOCK_QUOTE_ENDS = 0
FIX_RAW_TOTAL = 0
FIX_ATTRIBUTED_COUNT = 0
FIX_WARNING_COUNT = 0
FIX_DOCTEST_UNKNOWN_COUNT = 0
ADDED_BLANK_LINES = 4
REMOVED_LINES = 0
QUA14_FIX_VERDICT = MET

## Head check and fix list

- `date -u +%FT%TZ` -> `2026-09-19T22:44:10Z`
- `pwd -P` -> `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a9e59f8cf8962347b` (under
  `/home/yuta/Documents/typsphinx/.claude/worktrees/`)
- `test -f .git; echo "exit:$?"` -> `exit:0` (worktree confirmed — `.git` is a file)
- `grep -c typsphinx-fhs-run "$(command -v uv)"` -> `2`

Provisioning line (`<worktree_provisioning>`, `CLAUDE.md` § "Worktree-isolated execution" plus the
`--extra docs --python 3.13.13` additions):

```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
```

Exit status: `0`. `typsphinx==0.9.2` installed editable from this worktree's own checkout path,
`sphinx==9.1.0`, `sphinx-autodoc-typehints`, `myst-parser` all resolved.

- `sed -n 's/^home = //p;s/^version_info = //p' .venv/pyvenv.cfg` ->
  `PYVENV_HOME` = `/nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin`,
  `PYVENV_VERSION_INFO` = `3.13.13` — same interpreter version as 74-01/74-02/74-03.
- Before any commit: `BASE_74_04` = `git rev-parse HEAD` =
  `cf68ab4a4c9e6f1a14124602f17324e9bcd061a0`. `SCRATCH_74_04` = `mktemp -d` =
  `/tmp/tmp.xzhoIOQscX`.

`FIX_LIST` (from `74-BASE-EVIDENCE.md`), verbatim:

```
FIX_LIST = typsphinx.pathfmt.quote_path|typsphinx.translator.TypstTranslator.visit_toctree
```

`PHASE_BASE_SHA` (from `74-BASE-EVIDENCE.md`), verbatim:

```
PHASE_BASE_SHA = 8ea10273265e3966b6e650bad43cf90c9598ed65
```

`FIX_LIST` equals the plan's planned value
(`typsphinx.pathfmt.quote_path|typsphinx.translator.TypstTranslator.visit_toctree`) exactly — no
`## HALT` needed. Proceeding with the two docstrings as planned.

## visit_toctree repair

Probe script (`$S/p7404_docprobe.py`, never committed): resolves a fully qualified name, cleans its
docstring with `inspect.cleandoc()`, runs it through napoleon's `GoogleDocstring`, then parses the
joined result with `docutils.parsers.rst.Parser` at `report_level = 2`, printing one row per system
message of either QUA-14 message class (patching `document.reporter.system_message` to capture line
and level rather than relying on stream capture alone).

**Probe before** (`uv run python "$S/p7404_docprobe.py" typsphinx.translator.TypstTranslator.visit_toctree`),
verbatim:

```
typsphinx.translator.TypstTranslator.visit_toctree	5	ERROR	Unexpected indentation.
typsphinx.translator.TypstTranslator.visit_toctree	6	WARNING	Block quote ends without a blank line; unexpected unindent.
typsphinx.translator.TypstTranslator.visit_toctree	21	ERROR	Unexpected indentation.
```

This reproduces the three census lines 74-01 attributed to `visit_toctree` exactly (lines 5 ERROR,
6 WARNING, 21 ERROR).

**Repair.** Three empty lines inserted in `visit_toctree`'s docstring in `typsphinx/translator.py`,
per the planning-time probe table:

1. After `Requirement 13: Multi-document integration and toctree processing`.
2. Between `- Issue #5: Fix relative paths for nested toctrees` and its nested
   `- Calculate relative paths from current document`.
3. Between `- Issue #7: Simplify toctree output with single content block` and its nested
   `- Generate single #[...] block containing all guards`.

No other character was changed: no rewording, no re-indentation, no re-wrapping.

**Probe after** (same command): zero output, exit `0`. No residue — all three inserted blank lines
were needed and sufficient, matching the planning-time probe table exactly.

## Clean rebuild (fix verification)

Build command:

```
rm -rf "$S/after-toctree"
env LANG=C LC_ALL=C uv run python -m sphinx -b typst docs/source "$S/after-toctree"
```

stdout and stderr both redirected to `$S/p7404_after-toctree.log`. Exit: `0`.

English summary line (`LANG=C LC_ALL=C grep -E '^build succeeded' "$S/p7404_after-toctree.log"`),
verbatim:

```
build succeeded.
```

`AFTER_TOCTREE_ATTRIBUTED_COUNT` = `0`
(`LANG=C LC_ALL=C grep -cE '\.py:docstring of [A-Za-z0-9_.]+:[0-9]+: (ERROR|WARNING): (Unexpected indentation|Block quote ends without a blank line)' "$S/p7404_after-toctree.log"`).

`AFTER_TOCTREE_RAW_TOTAL` = `4`
(`LANG=C LC_ALL=C grep -cE 'Unexpected indentation|Block quote ends without a blank line' "$S/p7404_after-toctree.log"`).
The 4 remaining raw lines (verbatim, `LANG=C LC_ALL=C grep -nE '...' "$S/p7404_after-toctree.log"`):

```
12::19: (ERROR/3) Unexpected indentation.
13::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
14::19: (ERROR/3) Unexpected indentation.
15::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
```

These are `quote_path`'s own unattributed lines (`:19`/`:21`, matching `BASE_RAW_UNEXPECTED_INDENTATION`'s
and `BASE_RAW_BLOCK_QUOTE_ENDS`' `quote_path` half from `74-BASE-EVIDENCE.md`'s docstring probe) —
expected to remain until Task 2 repairs `quote_path`'s own docstring. `visit_toctree`'s attributed
half of the census is fully cleared: `AFTER_TOCTREE_ATTRIBUTED_COUNT = 0`, and the same attributed
filter matches 3 lines in `74-BASE-EVIDENCE.md` (the positive control, `BASE_ATTRIBUTED_COUNT = 3`).

## Lint and tests

```
$ uv run ruff check typsphinx/translator.py
All checks passed!
$ uv run black --check typsphinx/translator.py
All done! [ok]
1 file would be left unchanged.
$ uv run pytest tests/test_translator.py tests/test_doctest_block_render_gate.py -q -p no:cacheprovider
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
collected 133 items

tests/test_translator.py ............................................... [ 35%]
........................................................................ [ 89%]
...                                                                      [ 91%]
tests/test_doctest_block_render_gate.py ...........                      [100%]

============================= 133 passed in 0.69s ==============================
```

Diff shape for this task (`git diff -U0 "$BASE_74_04" HEAD -- typsphinx/translator.py`, checked
before commit): three hunks, each adding exactly one empty line, none removing anything, and all
three lying within `visit_toctree`'s docstring region (file lines ~5470-5490).

## quote_path repair

**Probe before** the edit, reconstructed from the pre-fix file content (`git show BASE_74_04 --
typsphinx/pathfmt.py`) run through the same napoleon-plus-docutils pipeline as
`p7404_docprobe.py`, verbatim:

```
typsphinx.pathfmt.quote_path	19	ERROR	Unexpected indentation.
typsphinx.pathfmt.quote_path	21	WARNING	Block quote ends without a blank line; unexpected unindent.
```

This reproduces the two lines 74-01 attributed to `quote_path` exactly (docstring-relative lines
19 ERROR and 21 WARNING).

**Repair.** Exactly one empty line inserted in `typsphinx/pathfmt.py`, between
`Delimiter rule (D-01), applied to the normalized string:` and the first bullet,
`` - no apostrophe present -> wrap in apostrophes (``'...'``) ``. No other character changed.

Per D-07, this docstring is repaired even though autodoc never renders it: the census reaches it
through `sphinx-autodoc-typehints`' probe-parse of the name imported into `builder.py` and
`writer.py` (`from typsphinx.pathfmt import quote_path`), which is evaluated as a documentable
candidate and probe-parsed even though it is excluded from the rendered page (imported members are
excluded by default).

**Probe after** (`uv run python "$S/p7404_docprobe.py" typsphinx.pathfmt.quote_path`): zero output,
exit `0`. No residue — the single inserted blank line was needed and sufficient.

Lint after the edit:

```
$ uv run ruff check typsphinx/pathfmt.py
All checks passed!
$ uv run black --check typsphinx/pathfmt.py
All done! [ok]
1 file would be left unchanged.
```

## Post-fix build

Build command:

```
rm -rf "$S/after-fix"
env LANG=C LC_ALL=C uv run python -m sphinx -b typst docs/source "$S/after-fix"
```

stdout and stderr both redirected to `$S/p7404_after-fix.log`. Exit: `0`.

English summary line, verbatim:

```
build succeeded.
```

`FIX_WARNING_COUNT` = `0` (the `build succeeded.` form with no `N warnings` suffix, which is at
most `BASE_WARNING_COUNT` = `5`).

`FIX_RAW_UNEXPECTED_INDENTATION` = `0`
(`LANG=C LC_ALL=C grep -o 'Unexpected indentation' "$S/p7404_after-fix.log" | wc -l`).

`FIX_RAW_BLOCK_QUOTE_ENDS` = `0`
(`LANG=C LC_ALL=C grep -o 'Block quote ends without a blank line' "$S/p7404_after-fix.log" | wc -l`).

`FIX_RAW_TOTAL` = `0` (their sum).

`FIX_ATTRIBUTED_COUNT` = `0`
(`LANG=C LC_ALL=C grep -cE '\.py:docstring of [A-Za-z0-9_.]+:[0-9]+: (ERROR|WARNING): (Unexpected indentation|Block quote ends without a blank line)' "$S/p7404_after-fix.log"`).

`FIX_DOCTEST_UNKNOWN_COUNT` = `0`
(`LANG=C LC_ALL=C grep -o 'unknown node type: .doctest_block' "$S/p7404_after-fix.log" | wc -l` —
zero since 74-03's handler).

`LANG=C LC_ALL=C grep -nE 'ERROR:|WARNING:' "$S/p7404_after-fix.log"` produced **no output** — the
post-fix build carries zero `WARNING:`/`ERROR:` lines of any kind. Every remaining line of the log
is a routine build-progress line (`writing output... [docname] done`, etc.); the full log ends:

```
...
writing output... [user_guide/templates] done
typst: wrote 1 wrapper file(s) -- compile these: typsphinx.typ
build succeeded.
```

No raw census line remains; no `## HALT` is needed.

## Diff shape

`git diff "$BASE_74_04" HEAD -- typsphinx/`, verbatim (`-U0`, both files, sole content diff of this
plan):

```
diff --git a/typsphinx/pathfmt.py b/typsphinx/pathfmt.py
index edcee460..1bdd2efe 100644
--- a/typsphinx/pathfmt.py
+++ b/typsphinx/pathfmt.py
@@ -62,0 +63 @@ def quote_path(value: str | os.PathLike[str] | None) -> str:
+
diff --git a/typsphinx/translator.py b/typsphinx/translator.py
index 629f918b..ba2fd225 100644
--- a/typsphinx/translator.py
+++ b/typsphinx/translator.py
@@ -5470,0 +5471 @@ class TypstTranslator(SphinxTranslator):
+
@@ -5483,0 +5485 @@ class TypstTranslator(SphinxTranslator):
+
@@ -5485,0 +5488 @@ class TypstTranslator(SphinxTranslator):
+
```

`ADDED_BLANK_LINES` = `4` (one in `pathfmt.py`, three in `translator.py`; every added line is
exactly empty, `git diff -U0 ... | grep -E '^\+' | grep -vE '^\+\+\+ '` is four bare `+` lines with
nothing else).

`REMOVED_LINES` = `0` (`git diff -U0 "$BASE_74_04" HEAD -- typsphinx | grep -E '^-' | grep -vE '^--- '` is empty).

| File | Docstring | Census line cleared |
|------|-----------|----------------------|
| `typsphinx/translator.py` | `TypstTranslator.visit_toctree` | `:5: ERROR Unexpected indentation` (after Requirement 13 heading) |
| `typsphinx/translator.py` | `TypstTranslator.visit_toctree` | `:6: WARNING Block quote ends` / a second `:21: ERROR` occurrence (before the Issue #5 nested bullet) |
| `typsphinx/translator.py` | `TypstTranslator.visit_toctree` | `:21: ERROR Unexpected indentation` (before the Issue #7 nested bullet) |
| `typsphinx/pathfmt.py` | `quote_path` | `:19: ERROR` / `:21: WARNING` (both cleared by the single inserted blank line before the Delimiter rule bullet list) |

Files changed since `BASE_74_04` under `typsphinx/`: exactly `typsphinx/pathfmt.py` and
`typsphinx/translator.py` (`git diff --name-only "$BASE_74_04" HEAD -- typsphinx`, sorted).

## Lint and tests

```
$ uv run ruff check .
All checks passed!
$ uv run black --check .
All done! [ok]
358 files would be left unchanged.
$ uv run mypy typsphinx/
Success: no issues found in 9 source files
$ uv run pytest tests/test_translator.py tests/test_doctest_block_render_gate.py -q -p no:cacheprovider
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
collected 133 items

tests/test_translator.py ............................................... [ 35%]
........................................................................ [ 89%]
...                                                                      [ 91%]
tests/test_doctest_block_render_gate.py ...........                      [100%]

============================= 133 passed in 0.65s ==============================
```

All exits `0`.

## Verdict

`QUA14_FIX_VERDICT` = `MET`:

- All four raw/attributed keys are `0`: `FIX_RAW_UNEXPECTED_INDENTATION = 0`,
  `FIX_RAW_BLOCK_QUOTE_ENDS = 0`, `FIX_RAW_TOTAL = 0`, `FIX_ATTRIBUTED_COUNT = 0`.
- `FIX_WARNING_COUNT = 0`, which is at most `BASE_WARNING_COUNT = 5`.
- `FIX_DOCTEST_UNKNOWN_COUNT = 0`.
- `REMOVED_LINES = 0`, and every one of the `ADDED_BLANK_LINES = 4` added lines is empty.
- Lint (`ruff`, `black`) and type-check (`mypy`) are green; the targeted test subset is green.

Both docstrings the base census named (`FIX_LIST`) are repaired in their own reST, with only empty
lines added and none removed, and a clean C-locale rebuild of `docs/source` reports zero raw and
zero attributed lines of either QUA-14 message class, with the total warning count not risen —
`docs/source/conf.py`, `docs/source/api/index.rst`, and every non-docstring line under `typsphinx/`
are unchanged by this plan.
