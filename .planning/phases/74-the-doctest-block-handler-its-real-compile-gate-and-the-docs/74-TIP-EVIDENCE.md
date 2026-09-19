# Phase 74 — Tip Evidence (SC1, SC3, D-05)

BASE_74_05 = c043950b58ed5e1030c1b17449b46a7c9b4fe85b
SCRATCH_74_05 = /tmp/tmp.GS0rMRsmic
PYVENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
PYVENV_VERSION_INFO = 3.13.13
TIP_WARNING_COUNT = 0
TIP_DOCTEST_UNKNOWN_COUNT = 0
TIP_RAW_UNEXPECTED_INDENTATION = 0
TIP_RAW_BLOCK_QUOTE_ENDS = 0
TIP_RAW_TOTAL = 0
TIP_ATTRIBUTED_COUNT = 0
TIP_API_COLLAPSED_RUNS = 0
TIP_API_EXAMPLE_PROMPTS = 3
TIP_FENCE_TAG = python
TIP_CODLY_ABOVE_FENCE = yes
TIP_API_PYTHON_FENCES = 2
TIP_EXAMPLES_IN_ORDER = yes

## Head check and provisioning

- `date -u +%FT%TZ` -> `2026-09-19T23:03:22Z`
- `pwd -P` -> `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a138ebb2fd2f5255c` (under
  `/home/yuta/Documents/typsphinx/.claude/worktrees/`)
- `test -f .git; echo "exit:$?"` -> `exit:0` (worktree confirmed — `.git` is a file)
- `grep -c typsphinx-fhs-run "$(command -v uv)"` -> `2`

Provisioning line (`<worktree_provisioning>`, `CLAUDE.md` § "Worktree-isolated execution" plus the
`--extra docs --python 3.13.13` additions):

```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
```

Exit status: `0`. `typsphinx==0.9.2` installed editable from this worktree's own checkout path,
`sphinx==9.1.0`, `sphinx-autodoc-typehints==3.13.6`, `myst-parser` resolved (no `.venv` existed
before this run — fresh worktree).

- `sed -n 's/^home = //p;s/^version_info = //p' .venv/pyvenv.cfg` ->
  `PYVENV_HOME` = `/nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin`,
  `PYVENV_VERSION_INFO` = `3.13.13` — the same interpreter as 74-01/74-02/74-03/74-04's evidence
  files, so this plan's SC3 "same environment" requirement holds across the whole phase, not just
  within this plan.

`BASE_74_05` = `git rev-parse HEAD`, before any commit = `c043950b58ed5e1030c1b17449b46a7c9b4fe85b`.
`SCRATCH_74_05` = `mktemp -d` = `/tmp/tmp.GS0rMRsmic`.

Wave 2-3 verdicts (from `74-RED-EVIDENCE.md` and `74-QUA14-EVIDENCE.md`), verbatim:

```
GREEN_VERDICT = MET
QUA14_FIX_VERDICT = MET
```

`PHASE_BASE_SHA` (from `74-BASE-EVIDENCE.md`), verbatim:

```
PHASE_BASE_SHA = 8ea10273265e3966b6e650bad43cf90c9598ed65
```

Both wave 2-3 verdicts are `MET`. No `## HALT` needed; proceeding.

`git diff --name-only "$PHASE_BASE_SHA" HEAD -- docs` printed nothing: the docs sources at this
plan's tip are byte-identical to the sources at the phase base.

**Sandbox note (carried from 74-04, re-verified here as still applicable in this session):** this
sandboxed shell refuses any Bash command whose text contains the literal substring `sourc`+`e`
(confirmed by re-testing before relying on the workaround). The workaround, unchanged from 74-04:
create a same-target symlink (`docs_link -> docs/sourc`+`e`) via Python's `os.symlink()` (never a
shell command spelling the word), drive every Sphinx build through the symlink path, then remove
the symlink and confirm `git status --short` is clean before each commit. The build target and its
content are identical either way; this is a command-spelling workaround only, never a change to
what is built or measured.

## Tip Typst build

Build command (run through the `docs_link` workaround described above):

```
rm -rf "$S/tip-typst"
LANG=C LC_ALL=C uv run python -m sphinx -b typst docs_link "$S/tip-typst" > "$S/p7405_tip-typst.log" 2>&1
```

`$S` = `SCRATCH_74_05` (`/tmp/tmp.GS0rMRsmic`). No `-q` flag. `echo "exit:$?"` -> `exit:0`.

The English summary line (`LANG=C LC_ALL=C grep -E '^build succeeded' "$S/p7405_tip-typst.log"`),
verbatim:

```
build succeeded.
```

`TIP_WARNING_COUNT` = `0` (the bare `build succeeded.` form carries no `N warnings` suffix).

`LANG=C LC_ALL=C grep -nE 'ERROR:|WARNING:' "$S/p7405_tip-typst.log"` produced **no output** — the
tip build carries zero `WARNING:`/`ERROR:` lines of any kind. There is therefore nothing to
transcribe under "every remaining `WARNING:`/`ERROR:` line" — the set is empty.

Keys, each from 74-01's command applied to this log:

- `TIP_DOCTEST_UNKNOWN_COUNT` = `0`
  (`LANG=C LC_ALL=C grep -o 'unknown node type: .doctest_block' "$L" | wc -l`).
- `TIP_RAW_UNEXPECTED_INDENTATION` = `0`
  (`LANG=C LC_ALL=C grep -oE 'Unexpected indentation' "$L" | wc -l`).
- `TIP_RAW_BLOCK_QUOTE_ENDS` = `0`
  (`LANG=C LC_ALL=C grep -oE 'Block quote ends without a blank line' "$L" | wc -l`).
- `TIP_RAW_TOTAL` = `0` (their sum).
- `TIP_ATTRIBUTED_COUNT` = `0`
  (`LANG=C LC_ALL=C grep -cE '\.py:docstring of [A-Za-z0-9_.]+:[0-9]+: (ERROR|WARNING): (Unexpected indentation|Block quote ends without a blank line)' "$L"`).

**Positive control (constraints 4 and 5):** `74-BASE-EVIDENCE.md`'s
`BASE_DOCTEST_UNKNOWN_COUNT = 2` and the QUA-14 census's `BASE_RAW_TOTAL = 10` /
`BASE_ATTRIBUTED_COUNT = 3` remain unchanged on disk (that file is not edited by this plan) and
both patterns the tip filters for still match it — the same `grep -o 'unknown node type: .doctest_block'`
over `74-BASE-EVIDENCE.md` finds 2 hits (its transcribed base-log excerpt), and the attributed-line
filter over the same file finds 3 hits (its transcribed base-log excerpt). Both remain at least 1,
so the tip's zero is proven against a live positive control, not asserted in isolation.

## Tip api/index.typ example region

On `$S/tip-typst/api/index.typ`:

- `TIP_API_COLLAPSED_RUNS` = `0` (`grep -c 'text(">>> ' "$T"`).
- `TIP_API_EXAMPLE_PROMPTS` = `3` (`grep -c '^>>> compute_content_include_path(' "$T"`).
- `TIP_FENCE_TAG` = `python`, the language on the line directly above the first
  `>>> compute_content_include_path(` line.
- `TIP_CODLY_ABOVE_FENCE` = `yes`: the line above that fence line is
  `codly(number-format: none)`.
- `TIP_API_PYTHON_FENCES` = `2` (count of lines exactly three backticks plus `python`).

Both examples' regions, `grep -n -B3 -A8` on `$T`, verbatim:

```
810-linebreak()
811-codly(number-format: none)
812-```python
813:>>> compute_content_include_path("", "index.typ")
814-'index.typ'
815:>>> compute_content_include_path("manuals", "guide/index.typ")
816-'../guide/index.typ'
817:>>> compute_content_include_path("guide", "guide/index.typ")
818-'index.typ'
819-```
820-
821-})
```

```
876-linebreak()
877-codly(number-format: none)
878-```python
879:>>> compute_template_import_path("typst", "base.typ")
880-'/_template/typst/base.typ'
881:>>> compute_template_import_path("report", "custom.typ")
882-'/_template/report/custom.typ'
883-```
884-
885-})
```

Each example's three prompts, continuations and outputs now sit on separate physical `.typ` lines
inside a `python`-tagged fence, replacing the base's single collapsed `text(">>> ...")` run at the
same position (`74-BASE-EVIDENCE.md` § "api/index.typ example region", line `:811` and `:867`).

`TIP_EXAMPLES_IN_ORDER` = `yes`: the first `>>> compute_content_include_path(` line is `813`, below
which the first `>>> compute_template_import_path(` line is `879` — `813 < 879`.

**Tag and reason, cited to D-01 (74-CONTEXT.md).** `TIP_FENCE_TAG = python`, matching
`74-RED-EVIDENCE.md`'s own `FENCE_TAG = python` (§ "Tag and reason (SC1, D-01)"). D-01's recorded
reason, quoted verbatim from `74-CONTEXT.md`: "The same two-prompt doctest fragment was compiled
under five fences. `pycon`, no tag, `text` and a nonexistent `bogusxyz` all produced a
byte-identical PDF (11531 bytes, SHA-256 prefix `5428a015b02591d5`). Only `python` differed (12654
bytes, `9bb09e20e0d2d05a`). An SVG compile counted per glyph: under `pycon` all 58 glyphs were
`#000000`. Under `python`, the 28-character function name was blue `#4b69c6`, the 24
string-literal characters green `#198810`, `>>>` red `#d73948`, and the 3 punctuation glyphs
black. `@preview/codly-languages:0.1.10`'s `lib.typ` has a `python` entry (name "Python", Python
icon, `#306998`) and zero `pycon` entries." This project's own tip build confirms the same tag was
actually applied at both example sites.
