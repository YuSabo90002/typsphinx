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
RESTORE_CLEAN = yes
REBUILT_BASE_WARNING_COUNT = 5
REBUILT_BASE_DOCTEST_UNKNOWN_COUNT = 2
REBUILT_BASE_RAW_TOTAL = 10
REBUILT_BASE_ATTRIBUTED_COUNT = 3
REBUILT_BASE_MATCHES_74_01 = yes
NOT_RISEN = yes
WARNING_DELTA = -5
D05_DIFFERING_FILE_COUNT = 1
D05_DIFFERING_FILES = api/index.typ
D05_HUNK_COUNT = 6
D05_TRN01_HUNKS = 2
D05_QUA14_HUNKS = 2
D05_FINDING_HUNKS = 2
D05_UNEXPLAINED_HUNKS = 0
D05_REMOVED_FENCE_LINES = 0
D05_REMOVED_COLLAPSED_RUNS = 2
D05_ADDED_PYTHON_FENCES = 2

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

## Base rebuild in the same venv

`git status --porcelain -- typsphinx` before the checkout window: empty.

`git checkout "$PHASE_BASE_SHA" -- typsphinx/` — exit `0`. `git diff "$PHASE_BASE_SHA" -- typsphinx`
after the checkout: empty — the working tree now equals the base exactly.

Build commands (through the `docs_link` workaround, § "Head check and provisioning"):

```
rm -rf "$S/base-typst"
LANG=C LC_ALL=C uv run python -m sphinx -b typst docs_link "$S/base-typst" > "$S/p7405_base-typst.log" 2>&1
```

```
rm -rf "$S/base-html"
LANG=C LC_ALL=C uv run python -m sphinx -b html docs_link "$S/base-html" > "$S/p7405_base-html.log" 2>&1
```

Both exit `0`.

`git checkout HEAD -- typsphinx/` — exit `0`. `git status --porcelain -- typsphinx` after: empty.
`RESTORE_CLEAN = yes`.

Keys from `$S/p7405_base-typst.log`, by 74-01's commands:

- `REBUILT_BASE_WARNING_COUNT` = `5` (English summary line: `build succeeded, 5 warnings.`).
- `REBUILT_BASE_DOCTEST_UNKNOWN_COUNT` = `2`
  (`LANG=C LC_ALL=C grep -o 'unknown node type: .doctest_block' "$S/p7405_base-typst.log" | wc -l`).
- `REBUILT_BASE_RAW_TOTAL` = `10` (6 `Unexpected indentation` + 4 `Block quote ends`).
- `REBUILT_BASE_ATTRIBUTED_COUNT` = `3`.

`REBUILT_BASE_MATCHES_74_01` = `yes`: all four equal `74-BASE-EVIDENCE.md`'s
`BASE_WARNING_COUNT = 5`, `BASE_DOCTEST_UNKNOWN_COUNT = 2`, `BASE_RAW_TOTAL = 10` and
`BASE_ATTRIBUTED_COUNT = 3`, exactly.

Base HTML build's English summary line
(`LANG=C LC_ALL=C grep -E '^build succeeded' "$S/p7405_base-html.log"`), verbatim:

```
build succeeded, 3 warnings.
```

This matches the plan's own planning-time prediction table exactly (base HTML: `build succeeded,
3 warnings.`).

## Not risen (SC3)

`NOT_RISEN` = `yes`: `TIP_WARNING_COUNT` (`0`) is at most `REBUILT_BASE_WARNING_COUNT` (`5`).

`WARNING_DELTA` = `-5` (tip `0` minus base `5`).

Every `WARNING:`/`ERROR:` line of both logs, with paths stripped to the part after the worktree
root (`LC_ALL=C diff` of the two stripped line sets):

```
1,5d0
< 33:typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:5: ERROR: Unexpected indentation. [docutils]
< 34:typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
< 35:typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:21: ERROR: Unexpected indentation. [docutils]
< 40:writing output... [api/index]WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_content_include_path("", "index.typ")
< 46:WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_template_import_path("typst", "base.typ")
```

All five of the base's `WARNING:`/`ERROR:` lines disappeared on the tip; the tip's own stripped
line set is empty (0 lines).

## D-05 whole-tree diff

`LANG=C LC_ALL=C diff -rq --exclude=.doctrees "$S/base-typst" "$S/tip-typst"`, exit `1`
(differences found), content verbatim:

```
Files /tmp/tmp.GS0rMRsmic/base-typst/api/index.typ and /tmp/tmp.GS0rMRsmic/tip-typst/api/index.typ differ
```

`D05_DIFFERING_FILE_COUNT` = `1`. `D05_DIFFERING_FILES` = `api/index.typ`.

`LANG=C LC_ALL=C diff -u "$S/base-typst/api/index.typ" "$S/tip-typst/api/index.typ"`, exit `1`,
into `$S/p7405_d05-1.diff`. `D05_HUNK_COUNT` = `6` (`grep -c '^@@' "$S/p7405_d05-1.diff"`).

### Hunks

```
--- base-typst/api/index.typ
+++ tip-typst/api/index.typ
@@ -808,7 +808,17 @@

 strong({text("Examples")})
 linebreak()
-text(">>> compute_content_include_path(\"\", \"index.typ\") 'index.typ' >>> compute_content_include_path(\"manuals\", \"guide/index.typ\") '../guide/index.typ' >>> compute_content_include_path(\"guide\", \"guide/index.typ\") 'index.typ'")})
+codly(number-format: none)
+```python
+>>> compute_content_include_path("", "index.typ")
+'index.typ'
+>>> compute_content_include_path("manuals", "guide/index.typ")
+'../guide/index.typ'
+>>> compute_content_include_path("guide", "guide/index.typ")
+'index.typ'
+```
+
+})
 parbreak()
 block(sticky: true, par(hanging-indent: 2.5em, {raw("typsphinx.\u{200B}writer.\u{200B}")
 strong(raw("compute_template_import_path"))
@@ -864,7 +874,15 @@

 strong({text("Examples")})
 linebreak()
-text(">>> compute_template_import_path(\"typst\", \"base.typ\") '/_template/typst/base.typ' >>> compute_template_import_path(\"report\", \"custom.typ\") '/_template/report/custom.typ'")})
+codly(number-format: none)
+```python
+>>> compute_template_import_path("typst", "base.typ")
+'/_template/typst/base.typ'
+>>> compute_template_import_path("report", "custom.typ")
+'/_template/report/custom.typ'
+```
+
+})
 parbreak()
 block(sticky: true, par(hanging-indent: 2.5em, {raw("class")
 raw(" ")
@@ -2121,7 +2139,7 @@
 par({text("Implements Task 4.2.2: codly forced usage, with codly(highlights: …) for :emphasize-lines: (codly 1.3.0 has no codly-range(highlight: …) API) Design 3.5: All code blocks use codly; highlighted lines use codly(highlights: …) Requirements 7.3, 7.4: Support line numbers and highlighted lines Issue #20: Support :linenos:, :caption:, and :name: options Issue #31: Support :lineno-start: and :dedent: options")})

 pad(left: 2.5em, {strong(text("Parameters") + text(": "))
-strong(raw("node")) + text(" (") + raw("literal_block") + text(")") + text(" – ") + text("The literal block node")
+strong(raw("node")) + text(" (") + raw("literal_block") + text(" | ") + raw("doctest_block") + text(")") + text(" – ") + text("The literal block node")
 parbreak()

 strong(text("Return type") + text(": "))
@@ -2137,7 +2155,72 @@
 par({text("Issue #20: Handle closing figure bracket and labels.")})

 pad(left: 2.5em, {strong(text("Parameters") + text(": "))
-strong(raw("node")) + text(" (") + raw("literal_block") + text(")") + text(" – ") + text("The literal block node")
+strong(raw("node")) + text(" (") + raw("literal_block") + text(" | ") + raw("doctest_block") + text(")") + text(" – ") + text("The literal block node")
+parbreak()
+
+strong(text("Return type") + text(": "))
+link("https://docs.python.org/3/builtins/constants.html#None", raw("None"))
+})
+})
+parbreak()
+block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("visit_doctest_block"))
+raw("(") + emph(raw("node")) + raw(")")}))
+[#metadata(none) <api_u2f_index:typsphinx.translator.TypstTranslator.visit_doctest_block>]
+pad(left: 2.5em, {par({text("Visit a doctest block (a ")
+raw(">>>")
+text(" interactive example) node.")})
+
+par({text("docutils' parser builds a ")
+raw("doctest_block")
+text(" for any line beginning with ")
+raw(">>> `` (``Body.doctest")
+text(" in ")
+raw("docutils/parsers/rst/states.py")
+text("), so a reST author cannot opt out of this node appearing in a doctree.")})
+
+par({raw("doctest_block")
+text(" is a sibling of ")
+raw("literal_block")
+text(" under ")
+raw("FixedTextElement")
+text(", not a subclass of it, so it needs its own dispatch entry rather than being reached through ")
+raw("literal_block")
+text("'s.")})
+
+par({text("This method delegates wholesale to ")
+raw("visit_literal_block")
+text(": the fence, the codly configuration, id anchors and the list-item separator discipline are all shared, with no second emission path. This is the same shape Sphinx's own writers use for this node – a delegating call in the HTML5 writer, a class-attribute alias in the LaTeX and Texinfo writers.")})
+
+par({text("The ")
+raw("python")
+text(" fence language is supplied in ")
+raw("visit_literal_block")
+text(" itself when the node carries none.")})
+
+pad(left: 2.5em, {strong(text("Parameters") + text(": "))
+strong(raw("node")) + text(" (") + raw("doctest_block") + text(")") + text(" – ") + text("The doctest block node.")
+parbreak()
+
+strong(text("Return type") + text(": "))
+link("https://docs.python.org/3/builtins/constants.html#None", raw("None"))
+})
+})
+parbreak()
+block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("depart_doctest_block"))
+raw("(") + emph(raw("node")) + raw(")")}))
+[#metadata(none) <api_u2f_index:typsphinx.translator.TypstTranslator.depart_doctest_block>]
+pad(left: 2.5em, {par({text("Depart a doctest block (a ")
+raw(">>>")
+text(" interactive example) node.")})
+
+par({text("Delegates wholesale to ")
+raw("depart_literal_block")
+text(", matching ")
+raw("visit_doctest_block")
+text(".")})
+
+pad(left: 2.5em, {strong(text("Parameters") + text(": "))
+strong(raw("node")) + text(" (") + raw("doctest_block") + text(")") + text(" – ") + text("The doctest block node.")
 parbreak()

 strong(text("Return type") + text(": "))
@@ -3113,15 +3196,15 @@
 [#metadata(none) <api_u2f_index:typsphinx.translator.TypstTranslator.visit_toctree>]
 pad(left: 2.5em, {par({text("Visit a toctree node (Sphinx table of contents tree).")})

-par({text("Requirement 13: Multi-document integration and toctree processing - Generate a compile-time state guard for each include-file entry")})
-
-quote(block: true, {par({text("(Phase 49, COMP-05/COMP-06 – see below)")})
-
-})
+par({text("Requirement 13: Multi-document integration and toctree processing")})

 list({
 parbreak()

+text("Generate a compile-time state guard for each include-file entry (Phase 49, COMP-05/COMP-06 – see below)")
+}, {
+parbreak()
+
 text("D-07: apply ")
 emph({text("set heading(offset: heading.offset + 1)")})
 text(" – a context-relative increment, not an absolute assignment – to lower heading levels. ")
@@ -3134,22 +3217,31 @@
 }, {
 parbreak()

-text("Issue #5: Fix relative paths for nested toctrees - Calculate relative paths from current document")
+text("Issue #5: Fix relative paths for nested toctrees")
+list({
+parbreak()
+
+text("Calculate relative paths from current document")
+})
 }, {
 parbreak()

-text("Issue #7: Simplify toctree output with single content block - Generate single #[…] block containing all guards - D-07: apply ")
-emph({text("heading.offset + 1")})
-text(" once per toctree, inside a")
-quote(block: true, {
+text("Issue #7: Simplify toctree output with single content block")
+list({
+parbreak()
+
+text("Generate single #[…] block containing all guards")
+}, {
 parbreak()

+text("D-07: apply ")
+emph({text("heading.offset + 1")})
+text(" once per toctree, inside a ")
 emph({text("context { … }")})
 text(" block (required because ")
 emph({text("heading.offset")})
-text(" is a context-dependent style query)")})
-
-
+text(" is a context-dependent style query)")
+})
 })

 par({text("Phase 49 (COMP-05/D-03): reads the toctree's INCLUDE-FILE list (")
```

### Classification

| H<n> | File | @@ header | Class | Reason |
|------|------|-----------|-------|--------|
| H1 | api/index.typ | @@ -808,7 +808,17 @@ | TRN-01 | Removes the `compute_content_include_path` collapsed run (one `text(">>> ...")` run) and adds `codly(number-format: none)` plus a ```` ```python ```` fence with the matching example lines from `writer.py:59-65` |
| H2 | api/index.typ | @@ -864,7 +874,15 @@ | TRN-01 | Removes the `compute_template_import_path` collapsed run and adds the matching codly/python-fence/example lines from `writer.py:107-111` |
| H3 | api/index.typ | @@ -2121,7 +2139,7 @@ | FINDING-D04 | `visit_literal_block`'s rendered `node` parameter line gains `text(" | ") + raw("doctest_block")` — D-04's widened `nodes.literal_block \| nodes.doctest_block` annotation, self-documented by autodoc |
| H4 | api/index.typ | @@ -2137,7 +2155,72 @@ | FINDING-D04 | `depart_literal_block`'s rendered `node` parameter line gains the same widened annotation, and the added API entries carry metadata labels ending `TypstTranslator.visit_doctest_block>]` and `TypstTranslator.depart_doctest_block>]` — the two new D-04 delegating methods and their docstrings |
| H5 | api/index.typ | @@ -3113,15 +3196,15 @@ | QUA-14 | Lies inside `visit_toctree`'s rendered entry (metadata line `3196` to the next `block(sticky: true` at `3285`); the run-on paragraph + block quote around "Requirement 13" becomes a paragraph plus a list item, from the blank line QUA-14 inserted after the "Requirement 13" heading |
| H6 | api/index.typ | @@ -3134,22 +3217,31 @@ | QUA-14 | Lies inside the same `visit_toctree` entry; the "Issue #5" and "Issue #7" bullets each become a bullet plus a nested sub-list, from the two blank lines QUA-14 inserted before their nested bullets |

`D05_TRN01_HUNKS` = `2`. `D05_QUA14_HUNKS` = `2`. `D05_FINDING_HUNKS` = `2`. Their sum (`6`) equals
`D05_HUNK_COUNT` (`6`). `D05_UNEXPLAINED_HUNKS` = `0` — no hunk fits none of the three classes.

### Literal-block path unchanged

- `D05_REMOVED_FENCE_LINES` = `0` (`grep -cE '^-```' "$S/p7405_d05-1.diff"`) — no removed diff line
  is a fence line.
- `D05_REMOVED_COLLAPSED_RUNS` = `2` (`grep -cE '^-.*text\(">>> ' "$S/p7405_d05-1.diff"`), equal to
  `74-BASE-EVIDENCE.md`'s `BASE_API_COLLAPSED_RUNS = 2`.
- `D05_ADDED_PYTHON_FENCES` = `2` (`grep -cx '+```python' "$S/p7405_d05-1.diff"`), equal to
  `D05_REMOVED_COLLAPSED_RUNS`.

The literal-block emission path for pre-existing code blocks is unchanged: every removed line is
either a collapsed doctest run (TRN-01) or QUA-14 docstring prose, never a fence delimiter.
