# Phase 44 Plan 04 — Gate Evidence: SC#5 Repo-Wide Audit + Phase Gate

All output below was produced by commands executed in this plan's own session, in the
worktree at `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7ea89f4fa3d64727`,
against `HEAD` = `b819c8bfaeb18745db44ee909ed2d12314b673b6` (waves 1 and 2 merged). No
figure below is transcribed from `44-CONTEXT.md`, `44-RESEARCH.md`, or any other
planning document — every number is re-measured this session, and every divergence
from a planning-document figure is called out explicitly where it occurs.

This plan changes no code and no test. Its only artifact is this file (plus its own
`44-04-SUMMARY.md`).

## 1. Repo-wide `conf.py` census

**Command:**
```
$ grep -rl "typst_documents" --include=conf.py . | wc -l
107
```

**Divergence from `44-CONTEXT.md`:** the planning-time count was **103**. The
measured difference is **+4**, and it is fully accounted for: plan 44-01 added
`tests/fixtures/default_typst_documents_gate/conf.py` and
`tests/fixtures/explicit_typst_documents_wins_gate/conf.py`; plan 44-02 added
`tests/fixtures/non_str_docname_gate/conf.py` and
`tests/fixtures/empty_typst_documents_optout_gate/conf.py`. 103 + 4 = 107, confirmed
by listing the 107 paths and diffing against the pre-phase set (all four new paths
are the phase's own fixtures; nothing pre-existing was added or removed from the
census).

**Column-0 assignment check** — every file in the 107-file list, checked for a
literal `typst_documents` assignment starting at column 0:
```
$ grep -rl "typst_documents" --include=conf.py . | xargs grep -L '^typst_documents'
tests/fixtures/default_typst_documents_gate/conf.py
```

Exactly **one** file mentions `typst_documents` without assigning it at column 0:
`tests/fixtures/default_typst_documents_gate/conf.py` — confirmed by reading it
directly, its five `typst_documents` mentions are all inside comments explaining
*why* the line is deliberately absent (`grep -n 'typst_documents'` on that file:
lines 3, 5, 6, 15, 25, all `#`-prefixed prose).

**Conclusion this supports:** no pre-existing fixture's output filename changes,
because every `conf.py` in the repo that mentions the setting also sets it —
**except the two this phase added deliberately**, which are named here as the
intentional exceptions the plan's action block requires:

1. **`tests/fixtures/default_typst_documents_gate/conf.py`** (plan 44-01) — the
   repo's only fixture that omits `typst_documents` entirely, so it is the sole
   fixture that exercises the derived-default path at all. Fails the column-0 check
   above by design.
2. **`tests/fixtures/empty_typst_documents_optout_gate/conf.py`** (plan 44-02) —
   passes the column-0 check (`typst_documents = []` at column 0, confirmed:
   `grep -n 'typst_documents' tests/fixtures/empty_typst_documents_optout_gate/conf.py`
   → line 22, `typst_documents = []`), but is still an intentional exception to the
   "every conf.py already sets it so nothing changes" claim in a different sense: it
   is the one fixture that deliberately exercises the explicit-empty opt-out branch
   (D-03), which is only reachable post-CONF-08 by writing `typst_documents = []`
   explicitly.

No other file in the 107-file census is new or altered in its `typst_documents`
assignment by this phase; the remaining 105 all pre-date the phase and all set the
value explicitly, so none of their output filenames change.

## 2. `temp_sphinx_app` blast radius, re-measured with the corrected pattern set

**Test modules referencing `temp_sphinx_app`, with per-file reference count:**
```
$ grep -rc 'temp_sphinx_app' tests/*.py | grep -v ':0'
tests/conftest.py:1
tests/test_builder.py:36
tests/test_config.py:10
tests/test_inline_references.py:42
tests/test_builder_output_stem.py:48
tests/test_admonitions.py:54
tests/test_footnotes.py:13
tests/test_line_blocks.py:9
tests/test_extension.py:3
tests/test_pdf_generation.py:27
tests/test_topics.py:15
```

Ten test modules (excluding `conftest.py`, which defines the fixture rather than
consuming it) — matching `44-RESEARCH.md` Pitfall 2's set of nine PLUS
`test_topics.py`, which the research grep also found (the research prose names nine
files but its own table includes `test_topics.py` as the tenth; re-measured here
independently and confirmed as ten).

**Full-pass driver grep, corrected pattern set (`app.build(`, `.translate()`,
`builder.write(`, and — the pattern `44-RESEARCH.md`'s own blast-radius grep
omitted — `write_doc(`):**
```
$ grep -nE 'app\.build\(|\.translate\(\)|builder\.write\(|write_doc\(' tests/test_builder.py tests/test_config.py tests/test_inline_references.py tests/test_builder_output_stem.py tests/test_admonitions.py tests/test_footnotes.py tests/test_line_blocks.py tests/test_extension.py tests/test_pdf_generation.py tests/test_topics.py
tests/test_builder.py:128:    builder.write_doc("index", sample_doctree)
tests/test_builder.py:154:    builder.write_doc("index", sample_doctree)
tests/test_builder.py:180:    builder.write_doc("index", sample_doctree)
tests/test_builder.py:406:    """Test that write_doc() calls post_process_images()."""
tests/test_builder.py:436:    builder.write_doc("index", doc)
```

Per-file `write_doc(` count, confirming the match is isolated to exactly one file:
```
$ grep -c 'write_doc(' tests/test_builder.py tests/test_config.py tests/test_inline_references.py tests/test_builder_output_stem.py tests/test_admonitions.py tests/test_footnotes.py tests/test_line_blocks.py tests/test_extension.py tests/test_pdf_generation.py tests/test_topics.py
tests/test_builder.py:5
tests/test_config.py:0
tests/test_inline_references.py:0
tests/test_builder_output_stem.py:0
tests/test_admonitions.py:0
tests/test_footnotes.py:0
tests/test_line_blocks.py:0
tests/test_extension.py:0
tests/test_pdf_generation.py:0
tests/test_topics.py:0
```

**Adding `write_doc(` to the pattern set is what surfaces `tests/test_builder.py`.**
None of the other nine modules match ANY of the four full-pass driver patterns
(`app.build(`, `.translate()`, `builder.write(`, `write_doc(`) — the research
conclusion "no existing test needs a change" was **incomplete rather than merely
conservative**: its own pattern list (`.translate()`, `.write(`, `app.build(`,
`writer.translate`, `_is_master_document`) never included `write_doc(`, so it never
looked at the one file (`tests/test_builder.py`) that actually drives a
`write_doc()` call through `temp_sphinx_app`'s unset-`typst_documents` config.
Plan 44-01's own executor discovered this independently mid-plan (see
`44-GATE-EVIDENCE-01.md` §4) rather than from a corrected research pass; this
section re-derives the same finding from first principles as this plan's own
measurement, which is what SC#5 requires.

### The reconciliation this section owes wave 1

`44-01-SUMMARY.md`'s own deviation record additionally found
**`tests/test_builder_requirement13.py`** affected (3 tests), and it is
**intentionally invisible to the `temp_sphinx_app` grep above** — the reason is a
distinct blast-radius surface this plan's census would otherwise miss entirely:

```
$ grep -c 'temp_sphinx_app' tests/test_builder_requirement13.py
0
$ grep -n 'multifile_srcdir' tests/test_builder_requirement13.py | head -3
13:def multifile_srcdir(tmp_path):
59:def test_builder_generates_independent_typ_files(multifile_srcdir, tmp_path):
69:        srcdir=multifile_srcdir,
```

`test_builder_requirement13.py` defines its own **inline `conf.py`-writing fixture**
(`multifile_srcdir`), not `tests/conftest.py`'s `temp_sphinx_app`. A census that only
searches for `temp_sphinx_app` references — as both `44-RESEARCH.md`'s pitfall audit
and this section's opening grep do — structurally cannot see it. This is exactly the
class of miss this plan exists to catch, and it means the census methodology itself
has a documented blind spot: **inline/`write_text(...conf.py...)`-style fixtures are
a separate surface from `tests/conftest.py`'s named `temp_sphinx_app` fixture, and a
repo-wide audit must search for both, not just the latter.**

To close that blind spot rather than merely acknowledge it, a broader sweep for every
inline-`conf.py`-writing test module was run this session:
```
$ grep -rln 'conf.py").write_text\|conf_py.write_text\|conf_py = ' tests/*.py
tests/conftest.py
tests/test_builder_requirement13.py
tests/test_default_typst_documents_derivation.py
tests/test_corpus_gate.py
tests/test_config_other_options.py
tests/test_config_template_mapping.py
tests/test_config.py
tests/test_package_template_routing.py
tests/test_examples_basic.py
tests/test_package_only_config_gate.py
tests/test_template_assets.py
```

Each was checked for (a) whether its inline `conf.py` omits `typst_documents` and
(b) whether it drives a full pass (`app.build(`, `write_doc(`, `.finish()`) without
setting it. Findings, beyond `test_builder_requirement13.py` (already covered as a
`CHANGED` row in §3 below):

- **`tests/test_config_template_mapping.py::test_default_typst_template_mapping`**
  (line 46-63) writes an inline `conf.py` that omits `typst_documents` AND calls
  `app.build()` — a genuine full pass with the setting unset. It is unaffected only
  because its assertions read `app.config.typst_template_mapping`, never a filename
  or `typst_documents` itself: `uv run python -m pytest
  tests/test_config_template_mapping.py -q` → `7 passed` (this session). Recorded
  here as a second instance of the same blind-spot class, found and verified
  unaffected rather than left unexamined.
- **`tests/test_config_other_options.py`** (all 8 tests) writes inline `conf.py`
  content omitting `typst_documents`, but every test only constructs the app via
  `make_app(...)` and checks `hasattr`/equality on an unrelated config attribute
  (`typst_package`, `typst_package_imports`, `typst_template_function`,
  `typst_debug`) — no `write_doc(`/`app.build(`/`.translate()` call anywhere in the
  file (confirmed: `grep -c 'app.build(\|write_doc(\|\.translate(' tests/test_config_other_options.py`
  → `0`). Unaffected.
- The remaining modules in the list above (`test_default_typst_documents_derivation.py`,
  `test_corpus_gate.py`, `test_config.py`, `test_package_template_routing.py`,
  `test_examples_basic.py`, `test_package_only_config_gate.py`,
  `test_template_assets.py`) all set `typst_documents` explicitly in every inline
  `conf.py` they write (confirmed by `grep -c 'typst_documents'` returning ≥1 for
  each, all >0 in this session's measurement) — either because they are this phase's
  own new derivation-focused tests, or because they were already written to set the
  value, per the pre-phase 103-file census.

## 3. Per-file verdict table

One row per test module that references `temp_sphinx_app`, plus
`tests/test_pdf_generation.py` and `tests/test_builder_output_stem.py` (both already
included, since both reference `temp_sphinx_app`), plus the reconciled
`tests/test_builder_requirement13.py` row.

| File | Verdict | Reason | Proof |
|------|---------|--------|-------|
| `tests/test_builder.py` | **CHANGED** | `write_doc(` drives a real write pass through `temp_sphinx_app` (whose `conf.py` omits `typst_documents`, `project = 'Test Project'`); two tests asserted on the old literal `index.typ`, which after CONF-08 is now written as `testproject.typ` (`make_filename_from_project("Test Project")`). Fixed by plan 44-01 Task 2 (rename to derived stem + CONF-08 comment). | `git log --oneline -- tests/test_builder.py` → `dbcc07c test(44-01): pin D-01 degradation table and repair test_builder.py (CONF-08)` (plus 3 pre-phase commits). Diff verified in `44-GATE-EVIDENCE-01.md` §4. Re-run this session: `tests/test_builder.py ....................` (20 passed) inside the combined run below. |
| `tests/test_builder_requirement13.py` | **CHANGED** | Uses its own inline `multifile_srcdir` fixture (not `temp_sphinx_app` — see §2's reconciliation), whose `conf.py` also omits `typst_documents` (`project = 'Multi-File Test'`). 3 tests asserted on the old literal `index.typ`, now `multi-filetest.typ`. Missed by the planning-time census (which only covered on-disk `tests/fixtures/*/conf.py` files); found and fixed by plan 44-01 Task 3 mid-execution. | `git log --oneline -- tests/test_builder_requirement13.py` → `38e73b4 test(44-01): prove an explicit typst_documents still wins end-to-end (SC#2)` (the commit that carries this fix, plus its diff shown in §2 above). Re-run this session: `tests/test_builder_requirement13.py .....` (5 passed) inside the combined run below. |
| `tests/test_config.py` | **VERIFIED-NO-CHANGE** | Its two `temp_sphinx_app`-based assertions (`test_default_typst_documents_config`, `test_typst_documents_config_structure`, lines 6-19) check only `hasattr(app.config, "typst_documents")` and `isinstance(app.config.typst_documents, list)` — both still hold under a derived (non-empty) list. No filename, content, or emptiness assertion anywhere in the module touches the derivation. | `tests/test_config.py ........` (8 passed) — combined run below. |
| `tests/test_builder_output_stem.py` | **VERIFIED-NO-CHANGE** | Every test that exercises `_resolve_output_stem` sets `builder.config.typst_documents` explicitly before calling it; the config value is never read implicitly. Confirmed by per-function AST-level scan: 22/24 tests contain a `builder.config.typst_documents = [...]` line; the remaining 2 (`test_directory_preserving_relpath_keeps_nested_docname_directory`, `test_directory_preserving_relpath_identity_stem_is_unchanged`) call `_directory_preserving_relpath` directly with literal docname/stem string arguments and never read `config.typst_documents` at all (verified: neither function body contains the string `typst_documents`). | `tests/test_builder_output_stem.py ........................` (24 passed) — combined run below. |
| `tests/test_pdf_generation.py` | **VERIFIED-NO-CHANGE** | Every `finish()`-exercising test explicitly sets `builder.config.typst_documents` immediately before calling `finish()`. `grep -n 'typst_documents' tests/test_pdf_generation.py` → 9 assignment lines at 94, 126, 271, 299, 333, 371, 404, 437, 543 — exactly matching the 9 test functions that call `builder.finish()` after constructing a `TypstPDFBuilder(temp_sphinx_app, ...)` (verified by cross-referencing `grep -n 'finish()\|temp_sphinx_app' tests/test_pdf_generation.py`: 9 `finish()`-calling tests, all preceded by their own `typst_documents` assignment). The remaining 21 tests in the file either don't touch `TypstPDFBuilder` at all (pdf.py-level unit tests) or construct it without calling `finish()` (`test_builder_initialization` only asserts identity). | `tests/test_pdf_generation.py ..............................` (30 passed) — combined run below. |
| `tests/test_admonitions.py` | **VERIFIED-NO-CHANGE** | Zero matches for `app.build(`, `.translate()`, `builder.write(`, or `write_doc(` (§2's corrected grep). Builds hand-crafted doctrees fed directly to `TypstTranslator`, never a full `write()`/`translate()` pass through `temp_sphinx_app`. | `tests/test_admonitions.py ..................` (18 passed) — combined run below. |
| `tests/test_inline_references.py` | **VERIFIED-NO-CHANGE** | Same as `test_admonitions.py` — zero matches in §2's corrected grep. | `tests/test_inline_references.py ..............` (14 passed) — combined run below. |
| `tests/test_extension.py` | **VERIFIED-NO-CHANGE** | Same as above — zero matches. | `tests/test_extension.py ......` (6 passed) — combined run below. |
| `tests/test_line_blocks.py` | **VERIFIED-NO-CHANGE** | Same as above — zero matches. | `tests/test_line_blocks.py ...` (3 passed) — combined run below. |
| `tests/test_footnotes.py` | **VERIFIED-NO-CHANGE** | Same as above — zero matches. | `tests/test_footnotes.py .....` (5 passed) — combined run below. |
| `tests/test_topics.py` | **VERIFIED-NO-CHANGE** | Same as above — zero matches. | `tests/test_topics.py .....` (5 passed) — combined run below. |

**Combined passing pytest output (this session), proving every VERIFIED-NO-CHANGE
and CHANGED row's dot line above is real and not fabricated:**
```
$ uv run python -m pytest tests/test_config.py tests/test_builder.py tests/test_builder_output_stem.py tests/test_pdf_generation.py tests/test_admonitions.py tests/test_inline_references.py tests/test_extension.py tests/test_line_blocks.py tests/test_footnotes.py tests/test_topics.py tests/test_builder_requirement13.py -q
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7ea89f4fa3d64727
configfile: pyproject.toml
plugins: cov-7.1.0
collected 138 items

tests/test_config.py ........                                            [  5%]
tests/test_builder.py ....................                               [ 20%]
tests/test_builder_output_stem.py ........................               [ 37%]
tests/test_pdf_generation.py ..............................              [ 59%]
tests/test_admonitions.py ..................                             [ 72%]
tests/test_inline_references.py ..............                           [ 82%]
tests/test_extension.py ......                                           [ 86%]
tests/test_line_blocks.py ...                                            [ 89%]
tests/test_footnotes.py .....                                            [ 92%]
tests/test_topics.py .....                                               [ 96%]
tests/test_builder_requirement13.py .....                                [100%]

============================= 138 passed in 1.97s ==============================
```

**Row count:** 2 `CHANGED` rows, 9 `VERIFIED-NO-CHANGE` rows (satisfies the plan's
"at least one `CHANGED` row and at least six `VERIFIED-NO-CHANGE` rows"; includes the
required explicit `tests/test_config.py` row).

## 4. Phase file inventory

**PHASE_BASE resolution.** Taken as the parent of the RED commit SHA recorded in
`44-GATE-EVIDENCE-01.md` §2 (`eeb930429c2608c5245f2769fc6b7edbbed206c5^`):
```
$ git rev-parse eeb930429c2608c5245f2769fc6b7edbbed206c5^
8bb43d181f95c5c807613bae99f22fe00ea963a0
```

**PHASE_BASE scope check** — its own commit subject must not carry a `44-` scope
(confirming it predates this phase's own work):
```
$ git log -1 --oneline 8bb43d181f95c5c807613bae99f22fe00ea963a0
8bb43d1 docs(roadmap): map TOC-01 to inserted phase 44.1 in REQUIREMENTS
```

The subject's scope is `roadmap` (the "44.1" appearing in the prose is the phase
number being *described*, not a `(44-...)` commit-scope prefix) — this is a
Phase 44.1-roadmap-mapping commit made during v0.7.1 roadmap creation, before Phase
44 itself started executing. PHASE_BASE is confirmed to predate this phase.

**Full name-status diff, PHASE_BASE → HEAD:**
```
$ git diff --name-status 8bb43d181f95c5c807613bae99f22fe00ea963a0..HEAD
M	.planning/REQUIREMENTS.md
M	.planning/ROADMAP.md
M	.planning/STATE.md
A	.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-01-SUMMARY.md
A	.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-02-SUMMARY.md
A	.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-01.md
A	.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-02.md
A	tests/fixtures/default_typst_documents_gate/conf.py
A	tests/fixtures/default_typst_documents_gate/index.rst
A	tests/fixtures/empty_typst_documents_optout_gate/conf.py
A	tests/fixtures/empty_typst_documents_optout_gate/index.rst
A	tests/fixtures/explicit_typst_documents_wins_gate/conf.py
A	tests/fixtures/explicit_typst_documents_wins_gate/index.rst
A	tests/fixtures/non_str_docname_gate/conf.py
A	tests/fixtures/non_str_docname_gate/index.rst
M	tests/test_builder.py
M	tests/test_builder_requirement13.py
A	tests/test_default_typst_documents_derivation.py
A	tests/test_default_typst_documents_gate.py
A	tests/test_empty_typst_documents_optout_gate.py
A	tests/test_non_str_docname_gate.py
M	typsphinx/__init__.py
M	typsphinx/builder.py
```

This diff reflects waves 1 and 2 only (this plan's own HEAD, `b819c8bfaeb18745db44ee909ed2d12314b673b6`, is the wave-1+2 merge point; plan 44-03 is a concurrent sibling in this same wave and its files are not yet in this tree). This table therefore covers exactly what CONF-08 (44-01) and BLD-01 (44-02) produced.

| File | Requirement | Producing plan |
|------|-------------|-----------------|
| `typsphinx/builder.py` | CONF-08, BLD-01 | 44-01 (`_default_typst_documents`), 44-02 (`isinstance(docname, str)` guard) — both plans edit this file, in disjoint regions |
| `typsphinx/__init__.py` | CONF-08 | 44-01 (`add_config_value` callable-default registration) |
| `tests/test_builder.py` | CONF-08 | 44-01 (rename 2 assertions to the derived stem) |
| `tests/test_builder_requirement13.py` | CONF-08 | 44-01 (rename 3 assertions to the derived stem — the deviation reconciled in §2/§3 above) |
| `tests/test_default_typst_documents_derivation.py` | CONF-08 | 44-01 (13-test unit module pinning the degradation table) |
| `tests/test_default_typst_documents_gate.py` | CONF-08 | 44-01 (real-`sphinx-build` gate, unset-path + SC#2 explicit-wins) |
| `tests/fixtures/default_typst_documents_gate/conf.py` | CONF-08 | 44-01 |
| `tests/fixtures/default_typst_documents_gate/index.rst` | CONF-08 | 44-01 |
| `tests/fixtures/explicit_typst_documents_wins_gate/conf.py` | CONF-08 | 44-01 |
| `tests/fixtures/explicit_typst_documents_wins_gate/index.rst` | CONF-08 | 44-01 |
| `tests/test_non_str_docname_gate.py` | BLD-01 | 44-02 (real-`sphinx-build` must-fail gate) |
| `tests/test_empty_typst_documents_optout_gate.py` | CONF-08 | 44-02 (D-03 wording + Discretion (d)) |
| `tests/fixtures/non_str_docname_gate/conf.py` | BLD-01 | 44-02 |
| `tests/fixtures/non_str_docname_gate/index.rst` | BLD-01 | 44-02 |
| `tests/fixtures/empty_typst_documents_optout_gate/conf.py` | CONF-08 | 44-02 |
| `tests/fixtures/empty_typst_documents_optout_gate/index.rst` | CONF-08 | 44-02 |
| `.planning/phases/44-.../44-01-SUMMARY.md` | CONF-08 | 44-01 |
| `.planning/phases/44-.../44-02-SUMMARY.md` | BLD-01, CONF-08 | 44-02 |
| `.planning/phases/44-.../44-GATE-EVIDENCE-01.md` | CONF-08 | 44-01 |
| `.planning/phases/44-.../44-GATE-EVIDENCE-02.md` | BLD-01, CONF-08 | 44-02 |
| `.planning/REQUIREMENTS.md` | CONF-08 | 44-01 (its own final metadata commit, `bea3549 docs(44-01): mark CONF-08 complete in REQUIREMENTS.md`) — see finding below |
| `.planning/ROADMAP.md` | CONF-08, BLD-01 | orchestrator (wave-merge progress update, not an individual plan's own commit) |
| `.planning/STATE.md` | CONF-08, BLD-01 | orchestrator (wave-merge session/position update, not an individual plan's own commit) |

Every row is mapped to `CONF-08` and/or `BLD-01`; none required a blank cell.

**Finding (not a formatting gap — a genuine tracking-state divergence):**
`.planning/REQUIREMENTS.md`'s checkbox and traceability-table rows for **BLD-01**
still read `Pending` as of this plan's `HEAD`, even though BLD-01 is fully
implemented and evidenced (`44-GATE-EVIDENCE-02.md` §§1-2, and 44-02's own SUMMARY
frontmatter records `requirements-completed: [BLD-01, CONF-08]`). Only CONF-08 was
flipped, by plan 44-01's own final metadata commit (`bea3549`):
```
$ git log --oneline -- .planning/REQUIREMENTS.md
bea3549 docs(44-01): mark CONF-08 complete in REQUIREMENTS.md
8bb43d1 docs(roadmap): map TOC-01 to inserted phase 44.1 in REQUIREMENTS
...
$ grep -n 'BLD-01' .planning/REQUIREMENTS.md
87:- [ ] **BLD-01**: A non-`str` docname reaching `TypstPDFBuilder.finish()` fails with an actionable
180:| BLD-01 | Phase 44 | Pending |
203:- **Phase 44** groups CONF-08 and BLD-01 because both change `TypstPDFBuilder.finish()` -- the
```

No commit by plan 44-02 (or anyone else, as of this plan's `HEAD`) marks BLD-01
complete in `REQUIREMENTS.md`. This is a **tracking-artifact gap, not an
implementation gap** — the code, the tests, and the evidence file all show BLD-01 is
done — but per this plan's own transparency contract ("MUST NOT report SC#5
satisfied by silence"), it is recorded here rather than silently left for a later
phase to notice. This plan does not fix it (its own `files_modified` is scoped to
this evidence file only); it is surfaced for the orchestrator's post-wave
`requirements.mark-complete` step to close, or for Phase 45/46 to catch if it is
not.
