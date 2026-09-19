# Phase 74 — QUA-14 Evidence (census-derived docstring repairs)

BASE_74_04 = cf68ab4a4c9e6f1a14124602f17324e9bcd061a0
SCRATCH_74_04 = /tmp/tmp.xzhoIOQscX
PYVENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
PYVENV_VERSION_INFO = 3.13.13
AFTER_TOCTREE_ATTRIBUTED_COUNT = 0
AFTER_TOCTREE_RAW_TOTAL = 4

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
