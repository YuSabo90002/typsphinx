# Phase 51 Sweep Completeness Audit

**Written by:** 51-06, Task 2
**Purpose:** Close the phase by measuring what it claimed — the whole suite, a real documentation
build, the D-07 exclusion, and the completeness of D-04's repo-wide falsified-claim sweep against
`51-RESEARCH.md` Part A's 13 rows and 4 STILL-TRUE sites.

This audit was run against the search-set methodology described in `<audit_integrity>`: the sweep
below was re-derived independently, by grepping the repository for the claim PATTERNS themselves
(`index.typ` mentions, one-file-per-entry counting language, unconditional `#include()`
walkthroughs, `path component is not supported` language, directory/build-output listings) across
`docs/source/**`, `README.md`, and `examples/**`, rather than by re-reading the earlier plans' own
file lists. Two residual false claims were found this way, in files no prior plan's `key-files`
named — see "Residual sweep findings" below.

---

## Part A row disposition

| # | Path:Line | Verdict | Disposition | Closed by | Evidence |
|---|---|---|---|---|---|
| 1 | `docs/source/user_guide/builders.rst:39` — "One file per document defined in `typst_documents`" | FALSE | FIXED | 51-04 | `builders.rst`'s Output section now states the wrapper+content split; `git log` commit `21be0c7e` |
| 2 | `docs/source/user_guide/builders.rst:61` — `typst compile build/typst/index.typ output.pdf` | FALSE | FIXED | 51-04 | Manual Compilation walkthrough now reads `typst compile build/typst/myproject.typ output.pdf` (verified live: line 69) — commit `21be0c7e` |
| 3 | `docs/source/user_guide/builders.rst:108-121` — "the second tuple element … governs both the emitted `.typ` file and the compiled `.pdf`" | FALSE / INCOMPLETE | FIXED | 51-04 | Document Definitions paragraph now scopes element 2 to the wrapper only and enumerates all four `.typ` files the shown config emits — commit `21be0c7e` |
| 4 | `docs/source/user_guide/builders.rst:156` — `open build/pdf/index.pdf` | FALSE (pre-existing, orthogonal to the split) | FIXED | 51-04 | Flagged by the researcher as a possible out-of-scope, pre-existing CONF-08-era staleness (the PDF has been named from `project`, never `index`, since v0.7.1). 51-04's own decision log records the explicit call: fixed rather than deferred, because D-04 scopes the sweep to every falsified claim found repo-wide and the fix is one line. Development walkthrough now reads `open build/pdf/myproject.pdf` (verified live: line 166) — commit `21be0c7e` |
| 5 | `docs/source/user_guide/builders.rst:170` — `typst compile build/typst/index.typ output.pdf` | FALSE | FIXED | 51-04 | Production → Option 2 walkthrough now reads `typst compile build/typst/myproject.typ output.pdf` (verified live: line 182) — commit `21be0c7e` |
| 6 | `docs/source/user_guide/configuration.rst:46-52` — "A path component is not supported…" | FALSE | FIXED | 51-04 | `typst_documents` element-2 contract reverses the OUT-01-falsified claim: a path is honoured relative to the outdir; only `..`, absolute, or drive-qualified is refused (verified live: `manuals/guide.typ` example present, `path component is not supported` string absent) — commit `4f170f69` |
| 7 | `docs/source/user_guide/templates.rst:453-462` — `cat build/typst/index.typ` under "Check the generated template usage" | FALSE | FIXED | 51-04 | Template-debugging walkthrough now reads `cat build/typst/myproject.typ` (verified live: line 463), with prose explaining why the content file cannot show a template problem — commit `4955efba` |
| 8 | `docs/source/changelog.rst:184` (historical `## [0.2.0]` "Old way (still works)" entry) — `typst compile build/typst/index.typ output.pdf` | BORDERLINE / historical | FIXED | 51-02 | Corrected per its own explicit disposition: the borderline historical example was rewritten to name the wrapper `myproject.typ` instead of the now-content-only `index.typ`, with an inline comment stating the derivation, while the surrounding "Old way (still works)" / "New way (recommended)" framing was left untouched (verified live: `build/typst/myproject.typ` present, `build/typst/index.typ` absent from the Migration Guides section) — commit `a6786f7a` |
| 9 | `README.md:82-85` — "each entry produces one emitted `.typ` file" | FALSE | FIXED | 51-05 | Quick Start `typst_documents` paragraph now states an entry produces a wrapper plus a content file for its source document (verified live: "produces one emitted" absent, "wrapper" present) — commit `dc8359b4` |
| 10 | `README.md:228` — `typst_documents` summary bullet | STALE (companion to #9) | FIXED | 51-05 | Configuration Options bullet now adds "The target names the entry's wrapper file" for consistency with the corrected Quick Start prose — commit `dc8359b4` |
| 11 | `examples/basic/README.md:36` — "This will create `_build/typst/basic-example.typ` with the Typst markup" | FALSE (by omission) | FIXED | 51-05 | Emitted-file sentence now names both files a real build writes (`basic-example.typ` wrapper, `index.typ` content) — verified live against a real build transcript recorded in `51-05-SUMMARY.md` — commit `5e8e1c01` |
| 12 | `examples/advanced/README.md:59-65` — generated-file list omits `index.typ`, calls `advanced-example.typ` the "Master document" using `#include()` | FALSE | FIXED | 51-05 | Generated-file list now includes `index.typ`; prose attributes chapter inclusion to the content file rather than the wrapper — verified live against a real build transcript — commit `5e8e1c01` |
| 13 | `examples/advanced/README.md:113-125` — unconditional `#set heading(offset: 1)` / `#include()` code block | FALSE, twice over | FIXED | 51-05 | Replaced with the real state-guarded compile-time emission (`context { set heading(offset: heading.offset + 1) } … if "index#0>chapterN" in state("typsphinx:include-edges", ()).get() { include("chapterN.typ") }`), verified byte-identical to a real build's emitted `index.typ` lines 45-49 (`51-05-SUMMARY.md`'s "Real Build Transcripts" section) — commit `5e8e1c01` |

All 13 rows are dispositioned FIXED. No row was dropped without a recorded reason.

---

## STILL-TRUE sites deliberately unchanged

| Path:Line | Claim | Why it survives (independently re-verified this task) |
|---|---|---|
| `docs/source/quickstart.rst:74-77,92-105` | "Find your PDF in `build/pdf/myproject.pdf`!" … `typst_documents = [("index", "myproject", …)]` | Only the wrapper is ever compiled to PDF — the two-layer split changes the `.typ` file SET but not which file becomes the `.pdf`. Re-read live this task (lines 70-77): text unchanged, still correct — a bare target is itself a valid worked-example shape. |
| `examples/basic/README.md:57` (now line 59 after 51-05's edit shifted line numbers) | `typst compile _build/typst/basic-example.typ output.pdf` | `basic-example.typ` IS the wrapper (target from `examples/basic/conf.py:30-35`) — re-verified live this task, the command is unchanged and correct. |
| `examples/charged-ieee/README.md:107,116` | `typst compile paper.typ output.pdf` | `examples/charged-ieee/{approach1,approach2}/conf.py` set `typst_documents = [("index", "paper", …)]`; `paper.typ` is the wrapper. Re-verified live this task via grep — both occurrences unchanged and correct. |
| `README.md:100-103` (now lines 104-107 after 51-05's edit shifted line numbers) | "A document reached only through a toctree is not a separate PDF — it is emitted as its own `.typ` file and pulled into its master through Typst's `#include()`." | Re-read live this task: still true in outcome (a toctree child gets its own content file and is transitively included), though it does not explain the wrapper/content mechanics in full. D-03 explicitly scopes README to false-claim correction only, not a full explanation, so no fix was mandated here — unchanged from `51-RESEARCH.md`'s own note. |

---

## Cited, not re-derived

Two claims this page and the migration guide publish require a real `typst.compile()`, which
raises `FileNotFoundError` in this sandbox (measured, `51-RESEARCH.md` §"Environment Availability").
Both are cited to Phase 49's own recorded real-compile transcripts and were never re-derived in this
phase:

1. **The standalone-content compile.** `49-EVIDENCE.md` §"Handoff to Phase 51 and Phase 52", item 1
   — `shared.typ` compiled directly (no wrapper) succeeds and produces only that document's own
   body (`SHARED-CHAPTER-MARKER` present, `NESTED-DOCNAME-BODY-MARKER` absent). Published as plain
   prose in `output_layout.rst`'s "Which File to Compile" section (D-08, 51-01).

2. **The per-master marker/heading-level counts for the shared-child composition.**
   `49-EVIDENCE.md` §"Degenerate-shape closure", the `state_guard_three_master_gate` row —
   `COMMON-B-MARKER` count = 1 in all three masters' compiled PDFs; resolved heading levels for
   `common_b` = `[3]` in m1 (nested under `mid`), `[2]` in m2 and m3 (both direct). Published as
   prose in `output_layout.rst`'s "Documents Shared by Several Masters" section (D-09, this plan's
   Task 1). The file-COUNT half of this claim (ten `.typ` files) WAS re-measured live this phase
   (`test_three_master_project_emits_ten_typ_files`, a real `-b typst` build) — only the
   compiled-PDF-level marker/heading-level proof is cited rather than re-run.

---

## D-07 exclusion measurement

`51-VALIDATION.md`'s originally-proposed single repo-wide grep
(`grep -rn ':numref:' docs/source/ README.md CHANGELOG.md` returning empty) is unsatisfiable and
would be wrong to satisfy: `CHANGELOG.md` already carries two pre-existing occurrences (lines 68 and
246) in v0.7.x entries about a table anchor, entirely unrelated to the Phase 49 divergence D-07
excludes. Corrected here to three scoped checks, run and recorded:

**(a) absence across every surface this phase writes into:**
```
$ grep -rn ':numref:' docs/source/ README.md examples/ | wc -l
0
```

**(b) the repo-root `CHANGELOG.md` is untouched by this phase:**
```
$ git diff --name-only HEAD -- CHANGELOG.md | wc -l
0
```

**(c) `CHANGELOG.md`'s own occurrence count is still exactly the pre-existing two:**
```
$ grep -c ':numref:' CHANGELOG.md
2
```

All three checks pass. `:numref:` appears in no page, no admonition, and no sentence this phase
publishes, per the owner override recorded in `51-CONTEXT.md` D-07. No standing pytest module was
added for this exclusion — D-07 forbids publishing, not testing, and the decision is rated `costly`
because a later milestone is expected to reverse it (per `51-06-PLAN.md`'s own explicit instruction
not to add one).

---

## Closing measurements

### Full suite

```
$ uv run python -m pytest -q -m "not slow"
================ 1101 passed, 73 deselected in 85.12s (0:01:25) ================
```

Exit code 0. (1101 rather than the plan's stated `13 passed` for the gate module alone — this is
the WHOLE suite, which includes this plan's own 3 new tests bringing
`tests/test_output_layout_docs_gate.py` from 10 to 13.)

### Real documentation build (`-b html`, outside the repository working tree)

```
$ sphinx-build -b html docs/source <tmpdir>/html
Sphinx v9.1.0 を実行中
...
ソースを読み込み中...[ 93%] user_guide/output_layout
...
<repo>/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:5: ERROR: Unexpected indentation. [docutils]
<repo>/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
<repo>/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:21: ERROR: Unexpected indentation. [docutils]
...
整合性をチェック中... <repo>/docs/source/examples/advanced.rst: document is referenced in multiple toctrees: ['examples/index', 'index'], selecting: index <- examples/advanced
<repo>/docs/source/examples/basic.rst: document is referenced in multiple toctrees: ['examples/index', 'index'], selecting: index <- examples/basic
<repo>/docs/source/user_guide/builders.rst: document is referenced in multiple toctrees: ['index', 'user_guide/index'], selecting: user_guide/index <- user_guide/builders
<repo>/docs/source/user_guide/configuration.rst: document is referenced in multiple toctrees: ['index', 'user_guide/index'], selecting: user_guide/index <- user_guide/configuration
<repo>/docs/source/user_guide/templates.rst: document is referenced in multiple toctrees: ['index', 'user_guide/index'], selecting: user_guide/index <- user_guide/templates
完了
...
build succeeded, 3 warnings.
EXIT_CODE=0
```

Exit code 0, "build succeeded, 3 warnings." The 3 warnings are pre-existing structural RST issues
in `typsphinx/translator.py`'s `visit_toctree` docstring (unindentation/block-quote errors),
unrelated to this phase — zero lines under `typsphinx/` changed this phase (see below). The
"referenced in multiple toctrees" lines are Sphinx's own informational log messages (not
`WARNING`-level), pre-existing structural duplication between `index.rst`'s and each section
index's toctrees, also unrelated to this phase. **No warning names `output_layout`, and no
`undefined label` / `unknown document` warning appears anywhere in the build output** — every
`:doc:` cross-reference this phase added (including this plan's own `See Also` section) resolves.

### Zero lines changed under `typsphinx/`, across the whole phase

```
$ git diff --name-only ae75040f..HEAD -- typsphinx/ | wc -l
0
```

(`ae75040f` is Phase 50's own completion merge commit — the commit immediately preceding Phase 51's
first commit.)

---

## Residual sweep findings — outside this plan's fix scope

The independent re-derivation described at the top of this audit (grepping the repository for the
claim PATTERNS, not the earlier plans' file lists) surfaced **two** residual false/incomplete claims
in files that no `51-RESEARCH.md` Part A row named and no prior Phase 51 plan's `key-files` touched.
Per this plan's own prohibition ("MUST NOT narrow the repo-wide falsified-claim sweep… without
recording an explicit reason") and the `<audit_integrity>` instruction to report residue honestly
rather than silently narrow scope, both are recorded here as OUTSTANDING, not fixed — this plan's
declared `files_modified` is exactly `docs/source/user_guide/output_layout.rst`,
`tests/test_output_layout_docs_gate.py`, and this audit file; fixing either finding below would
require editing a fourth file outside that declared scope.

1. **`docs/source/examples/advanced.rst:160`** — "Each document is built separately with its own
   output file." This sentence follows a `typst_documents` block with three entries
   (`("index", "main", …)`, `("api/index", "api-reference", …)`, `("tutorial/index", "tutorial",
   …)`). Under the two-layer split, each entry's own docname ALSO gets an unconditional content
   file — the sentence undercounts in the same shape Part A row 3 was verdicted FALSE/INCOMPLETE
   for (`builders.rst`'s now-fixed "second tuple element governs both" paragraph). This file
   (`docs/source/examples/advanced.rst`, a *documentation* page distinct from the bundled
   `examples/advanced/README.md` that 51-05 corrected) was not in `51-RESEARCH.md`'s Part A table
   and not in any Phase 51 plan's declared `files_modified`.

2. **`examples/advanced/index.rst:37-39`** — "Each chapter is a separate `.rst` file that gets
   converted to a separate `.typ` file. Typst's `#include()` directive is used to combine them into
   a single document." This is the SOURCE `.rst` file for the bundled `advanced` example (compiled
   into the example's own PDF), distinct from `examples/advanced/README.md` (which 51-05 already
   corrected at the equivalent claim, Part A row 13). The unconditional-`#include()` framing here is
   the same falsified shape Part A row 13 fixed elsewhere — this file was not in Part A's table and
   not in any Phase 51 plan's declared `files_modified`.

Both findings are genuine — confirmed by direct reading, not inferred — and are recorded here with
enough detail to file as a todo or fold into a future phase. **Recommendation:** file a todo
(`docs/source/examples/advanced.rst` and `examples/advanced/index.rst` output-shape corrections)
for a follow-up pass, since fixing them here would violate this plan's own declared scope fence.

No code defect under `typsphinx/` was noticed during this phase — the residue above is
documentation-only, and zero lines under `typsphinx/` were touched (confirmed above).

---

## Summary

- 13/13 Part A rows: FIXED, each with a named closing plan and evidence.
- 4/4 STILL-TRUE sites: independently re-verified this task, unchanged and still correct.
- 2/2 real-compile-dependent claims: cited to `49-EVIDENCE.md`, not re-derived (sandbox cannot run
  `typst.compile()`).
- D-07 exclusion: measured with the three corrected scoped checks, all passing.
- Full suite: 1101 passed, 73 deselected, exit 0.
- Real `-b html` docs build: exit 0, 3 pre-existing unrelated warnings, zero `output_layout`
  warnings, zero undefined-label/unknown-document warnings.
- `typsphinx/`: zero lines changed across the whole phase.
- 2 residual findings outside this plan's fix scope, recorded above as outstanding — not silently
  dropped, not fixed out of scope.
