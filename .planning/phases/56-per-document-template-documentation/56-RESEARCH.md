# Phase 56: Per-Document Template Documentation - Research

**Researched:** 2026-08-16
**Domain:** Sphinx/reStructuredText documentation authoring, bound to shipped Python behaviour by
run-time doc-gate tests (no production-code changes)
**Confidence:** HIGH

**HEAD measured against:** commit `f07e8cb8c59b066779a92fd4cfa4142f31448b22` (2026-08-16), branch
`gsd/v0.9.0-per-document-templates`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** `typst_document_templates` gets exactly one new subsection in
  `docs/source/user_guide/configuration.rst`, as the fifth subsection of the existing "Template
  Configuration" section (which today holds Template Function / Custom Template File / Typst
  Package / Template Assets). `templates.rst` gets no registry walkthrough, and no new `user_guide/`
  page is created. `configuration.rst` grows from 390 lines to roughly 470.
- **D-02:** `configuration.rst:80`'s element [4] is renamed from "Document class (usually 'typst')
  — accepted and ignored" to the registry key into `typst_document_templates`, stating that an
  absent element [4] resolves to the reserved `"typst"` key. Every existing five-element example
  stays byte-identical. The worked example using a non-default key lives inside the new registry
  subsection and nowhere else.
- **D-03:** `docs/source/user_guide/output_layout.rst` becomes the canonical page for output
  layout: the `_template/<key>/` directory story, the corrected file-count rule, and the hand-compile
  consequence Phase 54 recorded (`typst compile build/typst/manual.typ` "now needs `--root
  build/typst`, because the wrapper's `#import` is root-absolute"). The `--root` note goes in that
  page's existing "Which File to Compile" section. `builders.rst:122-127` gets only the file-count
  correction. The new registry subsection in `configuration.rst` links to `output_layout` rather than
  restating the layout. **See Priority 5 below — this research measured the `--root` premise
  empirically and found it is narrower than stated; read that section before writing this note.**
- **D-04:** The registry subsection's central worked example is the `template` route with two
  masters and no network dependency — one entry on the reserved `"typst"` key, one on a declared key
  resolving to a local `_typst/…typ`. The `package` route is shown only as a short schema-level
  example.
- **D-05:** `configuration.rst`'s registry subsection carries a "condition → how the build stops"
  table covering the seven config-caused `ExtensionError` shapes, plus a short separate note for the
  two I/O-caused shapes stating they are not a `conf.py` problem. Each table row quotes only the
  identifying leading clause of the message, never the aggregated body.
- **D-06:** doc↔code agreement is pinned by a two-way leading-clause gate test: every clause the
  catalogue publishes must exist in `typsphinx/*.py`, and every registry/bundle `ExtensionError` shape
  in `typsphinx/*.py` must appear in the catalogue. Discovery is a run-time scan, never a hardcoded
  file list. The module carries no `typst-py` import guard and spawns no `sphinx-build` subprocess, so
  it never skips. Per-error runtime reproduction is not duplicated.
- **D-07:** CONF-18's key-shape rules get their own small subsection ("registry key naming rules"),
  placed before the error table, alongside the statement that a key becomes a directory name under
  `_template/`. It enumerates: empty, `.`/`..`, containing `/` or `\`, a Windows reserved device name,
  a trailing dot or space, and differing from another declared key only by case. The error table's row
  for shape #2 links to it.
- **D-08:** The 54.1 `templates_path` collision refusal is documented in both the "Custom Template
  File" subsection (preventively) and as one row of the error table (shape #6). Constraint:
  `tests/test_docs_template_layout_gate.py::test_every_surviving_jinja_dir_mention_names_templates_path`
  requires any surviving mention of the bare `_templates` token to name `templates_path` on the same
  line.

### Claude's Discretion

- **DOC-16 — what "exercised by a real build" means for the asset examples.** Recommendation: extend
  the existing `tests/fixtures/user_template_relative_asset_gate/` (today: `conf.py`, `index.rst`,
  `_typst/branded.typ`, `_typst/logo.png`) with a `refs.bib` and a `#bibliography("refs.bib")` call,
  then bind `templates.rst`'s asset tree diagram and `advanced.rst`'s `refs.bib` paragraph to that
  fixture's measured destination paths. The two sites the fix must reach: `templates.rst:79-118`
  (closing note at `115-118` still says bundle copying "only applies to custom local templates") and
  `advanced.rst:122-131` (tells the reader the template is written to the output root as
  `_template.typ` and to reference the asset as `"_typst/refs.bib"`; under the bundle layout the
  template sits at `_template/<key>/custom_ieee.typ` with `refs.bib` beside it, so the correct
  reference is the bare `"refs.bib"`).
- **DOC-17 — where migration guidance is published, and how far the sweep reaches into history.**
  Recommendation: a new "Removed configuration values" subsection in `configuration.rst` covering
  `typst_template_assets`, `typst_authors`, `typst_toctree_defaults`, bound by a test to the three
  strings in `typsphinx/removed_config.py`'s `REMOVED_CONFIG_VALUES` dict (lines 36-57).
  **Recommendation on history:** do not rewrite historical release notes (`docs/source/changelog.rst`,
  `CHANGELOG.md`'s pre-0.9.0 entries). The sweep's target set is the current-state pages
  (`quickstart.rst`, `user_guide/*.rst`, `examples/*.rst`, `README.md`) and the runnable `examples/**`
  READMEs.
- Exact section titles, table column headers, and RST directive choices.
- Test file naming and placement for the two new doc gates, subject to D-06's no-skip constraint.
- Whether `examples/basic/README.md:38` and `examples/advanced/README.md:65` are corrected in the
  same plan as the `user_guide/` sweep or a separate one.

### Deferred Ideas (OUT OF SCOPE)

- Phase 57 — CHANGELOG curation (the `## [Unreleased]` section's `typst_document_templates` /
  `_template.typ` → `_template/<key>/` / `typst_template_assets` entries).
- A runnable `examples/` project demonstrating the registry (later milestone).
- `sphinx-build -b linkcheck` in CI (later milestone, pending todo).
- Documenting stale-bundle behaviour on incremental rebuilds (Phase 54 D-01's accepted gap; not one
  of this phase's three requirements).
- Seven `todo.match-phase 56` matches, none folded (code defects in other phases, or toolchain items).

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DOC-15 | `configuration.rst` describes element [4] as the registry key, retracting the "accepted and ignored" definition | Priority 1 confirms `configuration.rst:80` is the sole surviving "accepted and ignored" claim on any published surface (grep table below); Priority 1's error-shape verification and Priority 3's D-06 gate-shape analysis give the planner the exact source lines the new subsection and error table must agree with. |
| DOC-16 | `templates.rst`'s asset example and `advanced.rst`'s `refs.bib` guidance describe what actually works under the bundle layout | Priority 4 confirms `typst-py` compiles for real in this sandbox (the fixture's existing 4 tests pass), measures the exact destination path (`_template/typst/logo.png`, `_template/typst/branded.typ`), and gives the exact code change needed to add `refs.bib` + `#bibliography()` to the fixture. |
| DOC-17 | Migration guidance for the removed config values is published | `typsphinx/removed_config.py:36-57` read and quoted verbatim below; confirmed zero `docs/source/` guidance exists for any of the three names today (grep table, Priority 1). |
| (SC#4, sweep) | No stale claim survives the repo-wide sweep; both docs builds stay green | Priority 1's full grep tables (7 patterns) give the real hit set, classified in/out of scope; Priority 6 measures both `tox -e docs-html`/`docs-pdf` green at HEAD with timing and pre-existing warnings. |

</phase_requirements>

## Summary

This is a documentation-only phase with two live test-gate additions; there is no production code to
change. CONTEXT.md already carries a file:line-level inventory from the discussion session, and this
research's job was to **verify that inventory still holds at HEAD, run the repo-wide discovery greps
the phase demands, and empirically test the two claims CONTEXT.md flagged as needing measurement**
(the DOC-16 fixture's build-ability, and the `--root` hand-compile claim). All nine
`ExtensionError` shapes and all ten stale-prose line citations verify byte-for-byte or line-for-line
against HEAD; none moved. The full pytest suite is green (1366 passed, 5 skipped — all five
pre-existing and unrelated to this phase), `black`/`ruff`/`mypy` are clean, and both `tox -e docs-html`
and `tox -e docs-pdf` build green in ~3.3s each with two pre-existing, unrelated autodoc warnings.

Two findings go beyond CONTEXT.md's floor and are load-bearing for the plan:

1. **The `--root build/typst` hand-compile claim (D-03) is empirically too broad as stated.**
   Compiling the *specific worked example* `output_layout.rst` already shows (`typst compile
   build/typst/manual.typ`, a bare/root-level target) **succeeds without `--root`**, because Typst's
   documented default root is "the directory containing the compiled file," which for a
   root-level wrapper already equals the outdir root the `_template/<key>/` bundle sits under.
   `--root` is empirically required only when the wrapper's own `typst_documents` target has a path
   component (e.g. `"manuals/guide.typ"`), moving the wrapper's own directory out of alignment with
   the bundle's parent. See Priority 5 for the full reproduction; the planner must write a narrower,
   correct note, not the blanket claim CONTEXT.md's phrasing suggests.
2. **Fixing `output_layout.rst:159`'s stale "ten" claim will break an existing passing test unless
   that test is fixed in the same plan.** `tests/test_output_layout_docs_gate.py`'s
   `TestPublishedOutputLayoutTextMatchesBuild::test_page_states_the_shared_child_composition`
   currently asserts the literal string `"writes ten ``.typ`` files"` is present in the page. This is
   a second, independent assertion from the one CONTEXT.md already flagged
   (`test_three_master_project_emits_ten_typ_files`, which asserts the *build* produces nine files and
   is correct); this second one asserts the *prose* still says ten, and will go RED the moment the
   prose is corrected. See Priority 3.

**Primary recommendation:** Follow CONTEXT.md's D-01…D-08 exactly, using this research's line-number
corrections and the two findings above; write the `--root` note conditioned on target-path shape, and
include the `test_page_states_the_shared_child_composition` string update as an explicit task inside
the plan that touches `output_layout.rst:159`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Registry/error documentation (`configuration.rst`) | Docs (RST source) | Test (doc↔code gate) | Prose describing `typsphinx/template_registry.py` and `typsphinx/builder.py` behaviour; verified, not implemented, by a Python test. |
| Output-layout documentation (`output_layout.rst`, `builders.rst`) | Docs (RST source) | Test (real `sphinx-build` subprocess gate) | Prose describing the write-time file set; bound to a real build's emitted files, not a mock. |
| Asset-example documentation (`templates.rst`, `advanced.rst`) | Docs (RST source) | Test (real `sphinx-build -b typstpdf` → `typst.compile()` gate) | Prose describing a bundle-relative asset reference; the only way to prove "this compiles" is a real Typst compile, which is what the extended fixture does. |
| Doc-gate test modules (new) | Test (`tests/*.py`) | — | Pure verification code; asserts prose against `typsphinx/*.py` source or against real build output. No production code touched. |
| Docs build pipeline (`tox -e docs-html`/`docs-pdf`) | Build/CI | — | Existing dogfooding gate; this phase's SC#4 requires it stays green, not that it changes. |

There is no Browser/Frontend-Server/API/CDN tier in this phase — it is a documentation-and-Python-test
change inside a single-repo Sphinx extension. `ui.plan-gate`'s "table"/"render"/"page" wording
false-positives on Sphinx/RST vocabulary here (see MEMORY.md); the `UI hint: no` on this phase is
correct.

## Package Legitimacy Audit

**Not applicable.** This phase installs no new packages (production or dev). It adds two Python test
modules using only `subprocess`, `pathlib`, `re`, and `typing` — all stdlib, already imported
elsewhere in this test suite — plus, for the DOC-16 fixture extension, one new fixture file
(`refs.bib`) that is data, not a package.

## Verified Inventory: Error Shapes and Stale Prose (Priority 1)

### The nine `ExtensionError` message shapes, verified at HEAD

All nine of CONTEXT.md's shapes verify at the exact cited lines, with the raw source read via `Read`
this session (`typsphinx/template_registry.py`, `typsphinx/builder.py`).

| # | Leading clause (verbatim) | Call site `[VERIFIED: …]` | Wrapping |
|---|---|---|---|
| 1 | `"typst_document_templates must be a dict mapping registry key to definition, got {declared!r}"` | `typsphinx/template_registry.py:303-306` | Bare raise, not aggregated. |
| 2 | `"typst_document_templates: {len(failures)} invalid definition(s): {summary}"` | `typsphinx/template_registry.py:438-441` | Aggregate. **Measured 8 distinct sub-case messages feed this aggregate**, not 6 as CONTEXT.md's summary lists — see refinement below. |
| 3 | `"typst_documents entry names registry key {raw_key!r}, which is not a string -- registered typst_document_templates keys: {sorted(registry.keys())!r}"` | `typsphinx/template_registry.py:513-516` | Bare raise. |
| 4 | `"typst_documents entry names registry key {key!r}, which is not a registered typst_document_templates key -- registered keys: {sorted(registry.keys())!r}"` | `typsphinx/template_registry.py:523-526` | Bare raise. |
| 5 | `"typst: {len(failures)} output path collision(s): {summary}"` | `typsphinx/builder.py:950` (loop starts `~870`) | Aggregate; includes the `_template/` reservation sub-case (`builder.py:879-886`, `937-944`). |
| 6 | `"typst: {len(failures)} pre-write template path failure(s): {summary}"` | `typsphinx/builder.py:1312` (loop starts `~1250`) | Aggregate. **A second, structurally different raise site (see below) shares this shape's leading condition but not its wrapper.** |
| 7 | `"typst_document_templates: {len(failures)} bundle destination collision(s): {summary}"` | `typsphinx/builder.py:2174` | Aggregate. |
| 8 (I/O) | `"typst_document_templates: failed to copy the resolved template for registry key {key!r} from {src_file!r} to {dest_file!r}: {e}"` | `typsphinx/builder.py:1992` | Bare raise inside a `try/except`. |
| 9 (I/O) | `"typst_document_templates: the resolved template for registry key {key!r} ({template_filename!r}) was never copied from {src_dir!r} to {dest_dir!r} -- a wrapper naming this key would import a file that does not exist"` | `typsphinx/builder.py:2002` | Bare raise. |

**Load-bearing correction for D-06's implementation (not in CONTEXT.md's floor):** `grep -n "raise
ExtensionError" typsphinx/builder.py` finds **seven** call sites in `builder.py`, not five:
`950, 1312, 1992, 2002, 2151, 2174, 2377`. Two of these need explicit handling by whatever scanner
implements D-06's two-way gate:

- **`builder.py:2151`** raises `ExtensionError(_conf17_violation_message(key, ...))` — a **bare,
  unwrapped** raise whose text is `"typst_document_templates: registry key {key!r}'s resolved
  template {resolved_path!r} has a parent directory that is srcdir itself, or an ancestor of srcdir
  ({srcdir!r}) -- put the template in its own subdirectory (CONF-17, A-01)"`
  (`typsphinx/builder.py:303-333`, the `_conf17_violation_message()` helper). This is the **same
  helper function**, called from a **second** site inside the pre-write loop that feeds shape #6's
  aggregate (`builder.py:1265-1274`), and the function's own docstring states the two call sites are
  "DELIBERATELY duplicated" so their output text is byte-for-byte identical — one guards
  `write()`-driven builds (feeding shape #6's `"N pre-write template path failure(s)"` wrapper), the
  other guards `finish()`-driven calls that bypass `write()` entirely (existing tests call
  `_write_typst_files()`/`finish()` directly). **A leading-clause scanner that keys off literal
  f-string tokens at each `raise ExtensionError(` call site will find TWO different leading clauses
  for what is conceptually one condition** — the aggregate wrapper's clause (`"typst: N pre-write
  template path failure(s): "`) at line 1312, and the bare CONF-17 sentence itself at line 2151 (whose
  argument is a function *call*, not an inline f-string, so a naive "grab the f-string literal
  following `raise ExtensionError(`" parser will not even see line 2151's text — it must follow the
  call into `_conf17_violation_message()`'s `return` statement to extract it). The catalogue only
  needs ONE row for this condition (D-05's shape #6); the scanner must be told to treat
  `_conf17_violation_message()`'s return value as the discovered text for both call sites, or it will
  either miss line 2151 (under-count, D-06's "every shape in code appears in docs" direction silently
  passes vacuously) or report a spurious extra shape.
- **`builder.py:2377`** raises `f"typstpdf: {len(failures)} master document(s) failed: {summary}"` —
  this is the **PDF-compile failure aggregate** inside `TypstPDFBuilder.finish()`, not a
  registry/bundle configuration error. It is out of scope for D-06's catalogue by construction (it
  reports a Typst *compile* failure, not a `conf.py` misconfiguration), but the scanner must be scoped
  to exclude it explicitly (e.g. by module region or by a denylist), not merely by discovering "every
  `raise ExtensionError`" and hoping the catalogue happens to match.

**Refinement to shape #2's aggregate (useful context for the row's explanatory prose, not a new
catalogue row):** the failures-accumulation loop feeding `template_registry.py:438`'s aggregate
(`typsphinx/template_registry.py:330-424`, read in full this session) actually appends up to **eight**
distinct sub-case messages, not the six CONTEXT.md's D-05 summary names: non-`str` key; each of the
seven `_KEY_SHAPE_REJECTION_CASES` (empty/dot-dotdot/separator/Windows-reserved/trailing-dot/
trailing-space/case-collision — collapsed to one sub-case class here since they share one
`_validate_registry_key_shape()` call); reserved-key redeclaration (**CONF-16**, not previously
listed: `"registry key {key!r} is reserved for the built-in {RESERVED_REGISTRY_KEY!r} key and cannot
be redeclared (CONF-16)"`, `template_registry.py:337-340`); non-`dict` definition; `template`+
`package` both set (CONF-15); **`template`'s wrong Python type** (not previously listed: `"registry
key {key!r}'s template {template!r} must be a path string or os.PathLike, not a
{type(template).__name__}"`, `template_registry.py:402-405`); CONF-17 violation; template file not
found. D-05's table only needs one row for shape #2 (the leading clause is invariant regardless of
which sub-case fired), so this does not change the row count — but if the plan's prose *illustrates*
shape #2's sub-cases (as CONTEXT.md's own summary already does), use this eight-item list, not the
six-item one.

**Parser note for D-06 (multi-line / concatenated f-strings):** several of the nine messages are built
across multiple source lines, and one (`template_registry.py:422`) uses Python's **implicit adjacent
string-literal concatenation**: `f"registry key {key!r}'s template {template!r} does " "not exist"` —
two separate string tokens, no `+`, that Python concatenates at parse time. A regex over a single
line will miss this; an AST-based parser (`ast.parse` + walking `Call` nodes whose `func` is
`ExtensionError`, then reading the `JoinedStr`/`Constant` argument, handling `ast.JoinedStr`
concatenation as CPython does it) is the correct approach, not a `grep -A N`-style heuristic.

### Stale-prose sites, verified at HEAD

All ten of CONTEXT.md's cited stale-prose lines verify exactly as stated:

| Site | Verified content `[VERIFIED: …]` |
|---|---|
| `configuration.rst:80` | `"5. **Document class** (usually \"typst\") -- **accepted and ignored**:"` — confirmed, file is 390 lines total, matching CONTEXT.md. |
| `output_layout.rst:34` | `"``_template.typ``, which holds the template the wrapper imports. The"` — confirmed, file is 168 lines total. |
| `output_layout.rst:119` | `"A path can be claimed by any of three things: the reserved ``_template.typ``"` — confirmed. |
| `output_layout.rst:140` | `"leaves no ``.typ`` files behind at all -- not even ``_template.typ``. The"` — confirmed. |
| `output_layout.rst:159` | `"``_template.typ``. A three-master project over six documents therefore"` / next line `"writes ten ``.typ`` files; on the ``typst_package`` route it writes nine,"` — confirmed. **See the test-gate collision below.** |
| `builders.rst:127` | `"``_template.typ``, which both wrappers import. Under the"` — confirmed, file is 203 lines total; the surrounding paragraph (`builders.rst:122-130`) says the two-doc example "emit[s] five `.typ` files," which is also stale for the same reason (the fifth file is now a bundle subdirectory entry, not a root-level file). |
| `templates.rst:114-118` (closing note) | `".. note::\n\n   Typst Universe packages (``typst_package``) handle assets automatically.\n   Bundle copying only applies to custom local templates (``typst_template``)."` — confirmed at lines 115-118; file is 447 lines total. This directly understates OUT-04's no-exceptions rule (the built-in `"typst"` key's bundle is copied wholesale too). |
| `advanced.rst:122-131` | Confirmed verbatim: `"...The template file itself is written to the output root (as ``_template.typ``), so a relative path written inside it resolves from the output root too -- reference the copied asset as ``\"_typst/refs.bib\"``, matching where the copy lands, not the bare filename."` File is 427 lines total. The Typst code-block at `advanced.rst:107` also needs its content updated (`bibliography("_typst/refs.bib")` → `bibliography("refs.bib")`), since it is presented as the literal template source the reader copies. |
| `examples/basic/README.md:38` | `"body that the wrapper includes; and `_template.typ`, the template the"` — confirmed, file is 126 lines. |
| `examples/advanced/README.md:65` | `"- `_build/typst/_template.typ` - Template imported by the wrapper (here, your `_typst/custom.typ`)"` — confirmed, file is 318 lines. |

**Line-number corrections found (files edited by intervening phases; content itself is NOT stale, just
CONTEXT.md's citation drifted):** CONTEXT.md's canonical-refs section cites the `<srcdir>/_typst/
base.typ` shadow-route mention at `templates.rst:213` and `configuration.rst:325`. At HEAD these
mentions are at `templates.rst:183` and `configuration.rst:297` — the content itself is
bundle-layout-correct and needs no fix; only the line citation moved.

### Repo-wide discovery grep (Priority 1, the mandatory "no published surface" sweep)

Run at HEAD, excluding `.git/` only (full repo), then re-run excluding `.planning/` (which quotes the
stale text extensively as part of describing this very phase — expected noise, not a doc defect).

**`"accepted and ignored"`** — 4 hits outside `.planning/`:
| Hit | Classification | Reason |
|---|---|---|
| `docs/source/user_guide/configuration.rst:80` | **In-scope fix** | The retracted claim itself (DOC-15). |
| `tests/test_entry_metadata_precedence.py:48,176` | Out of scope (test prose, not published docs) | Describes the *shipped, correct* fifth-element tolerance behaviour (`_is_usable_typst_documents_entry`'s tolerate-and-skip contract), which is a real code behaviour, not the retracted "reads nothing" claim — this wording is accurate for what it describes and is not a published-surface claim. |
| `tests/test_builder_output_stem.py:123` | Out of scope (test prose) | Same: describes D-09's arity tolerance, a different and still-true fact from the retracted definition. |

**`"_template.typ"` (root-basename mentions)** — full hit list (57 matches) grouped:
| Group | Files | Classification | Reason |
|---|---|---|---|
| In-scope fix | `docs/source/user_guide/output_layout.rst:34,119,140,159`; `docs/source/user_guide/builders.rst:127`; `docs/source/examples/advanced.rst:128`; `examples/basic/README.md:38`; `examples/advanced/README.md:65` | **In-scope** | Exactly CONTEXT.md's named sweep surface (`docs/source/`, `README.md`/`examples/**/README.md`). |
| Historical record | `docs/source/changelog.rst:63,197`; `CHANGELOG.md:482` | **Excluded, per DOC-17's own recommendation** | Describes what was true in the v0.8.0/v0.7.x release notes at the time they shipped; rewriting them falsifies the historical record (the same reasoning `test_docs_contract_claims_gate.py`'s `EXCLUDED_CLAIM_PAGES` already applies to `changelog.rst`). |
| Test fixtures / test code | ~40 hits across `tests/*.py` and `tests/fixtures/**/conf.py` | **Out of scope, per 54.1 D-12 precedent** | `tests/` is deliberately not policed (54.1 D-12 measured zero conflicting hits under `tests/`); these are regression assertions that `_template.typ` no longer exists, or fixtures deliberately naming a template file `_template.typ` to test the reserved-basename edge case (`test_examples_charged_ieee_gate.py:236-268` proves the bundle correctly nests such a file at `_template/typst/_template.typ` — legitimate, not stale). |
| Legitimately-named input file, not stale | `examples/charged-ieee/approach2/conf.py:21,23,25` (`typst_template = "_typst/_template.typ"`) | **Not stale — genuine edge-case demonstration** | The user's own template file happens to be *named* `_template.typ` (the input filename, not the reserved output path); `test_examples_charged_ieee_gate.py` proves this compiles correctly under the bundle layout at `_template/typst/_template.typ`. Comment wording ("skips emitting `_template.typ` into the output directory") is slightly imprecise post-bundle (the package-only route still emits nothing into any output subdirectory, so the comment's *conclusion* is accurate even if its literal phrasing predates the bundle) — flag for the planner's discretion, not a required fix. |
| **New finding, beyond CONTEXT.md's floor** | `CLAUDE.md:49` | **Discovered, out of DOC-15/16/17's named scope** | `CLAUDE.md`'s own Architecture section states: *"It also writes a shared `_template.typ` file once per build (`_write_template_file`)."* `grep -n "_write_template_file" typsphinx/*.py` returns **zero** hits — the method was fully deleted in Phase 54. `CLAUDE.md` is a dev-facing (not reader-published) file describing this repo's own architecture to future Claude Code sessions; it is outside `docs/source/`, `README.md`, and `examples/` (54.1 D-12's policed scope), so it is not required by DOC-15/16/17 or by SC#4's literal wording. It is nonetheless a genuine architectural inaccuracy discovered by this phase's repo-wide grep, in the spirit of 54.1's D-13 precedent (a discovery-time re-grep finding a hit the written floor missed). **Recommendation: the planner should decide whether to fold a one-line `CLAUDE.md` correction into this phase (cheap, low-risk, keeps the project's own onboarding doc honest) or file it as a separate housekeeping item — it is not one of DOC-15/16/17 and is not required for any of the four success criteria as literally worded, but leaving a known-stale architecture description in `CLAUDE.md` while touching every other`_template.typ` mention in the repo is an odd place to stop.** |
| Production code, not stale | `typsphinx/writer.py:190-231` | **Not stale — confirmed dead code, already self-documenting** | `_compute_template_import_path()` is marked in its own docstring as "DEAD CODE (confirmed zero non-docstring callers since Phase 53... Phase 54 does not chase its removal)" and explicitly points to the live equivalent (`compute_template_import_path()`). No action needed; already correctly labeled. |
| Not stale (naming convention, not output claim) | `docs/source/conf.py:94,96`; `typsphinx/template_engine.py:38` | **Not stale** | These name a template *input* file as `custom_template.typ` (this docs project's own template filename choice), unrelated to the reserved output basename. |
| Dev script, not published | `scripts/render_admonition_greyscale.py:149` | **Out of scope** | Internal tooling script, not `docs/source/`, `README.md`, or `examples/`. |

**`"_templates/refs.bib"`** — 0 hits (the exact phrase does not appear verbatim anywhere; the closest
matches are `advanced.rst:107,130`'s `"_typst/refs.bib"`, which is DOC-16's actual target — see the
Stale-prose table above. `.planning/research/PITFALLS.md:74,76` references the string as historical
context for *why* this pitfall matters, in planning docs, out of scope.)

**`"typst_template_assets"` / `"typst_authors"` / `"typst_toctree_defaults"`** (excluding `.planning/`
and `tests/`): only three kinds of hits exist for each — `typsphinx/removed_config.py` (the source of
truth), `CHANGELOG.md`/`docs/source/changelog.rst` (historical, excluded per DOC-17's own
recommendation), and **zero** hits anywhere under the *current-state* `docs/source/` pages
(`configuration.rst`, `templates.rst`, `output_layout.rst`, `builders.rst`, `quickstart.rst`). This
confirms DOC-17's premise exactly: there is currently **no published migration guidance at all** for
any of the three removed values — the gap is total, not partial.

**`typsphinx/removed_config.py:36-57` quoted verbatim** (the source DOC-17's guidance must agree
with) `[VERIFIED: typsphinx/removed_config.py:36-57]`:

```python
REMOVED_CONFIG_VALUES: dict[str, str] = {
    "typst_template_assets": (
        "'typst_template_assets' was removed in v0.9.0 and is now ignored. "
        "Every used template's bundle directory (the resolved template "
        "file's parent) is copied wholesale to the output tree, so MORE "
        "files now reach the output than the explicit list used to select "
        "-- no asset list is needed any more."
    ),
    "typst_authors": (
        "'typst_authors' was removed in v0.7.1 and is now ignored. Rich "
        "author structure (department, organization, location, email) is "
        "expressed through 'typst_template_function's 'params' route "
        "instead, so author department, organization, and email do not "
        "reach the output unless supplied that way."
    ),
    "typst_toctree_defaults": (
        "'typst_toctree_defaults' was removed in v0.6.3 and has no "
        "replacement. It was registered but never read even when it "
        "existed, so deleting it changes no build output."
    ),
}
```

Delivery mechanism (also verified, same file): `check_config_at_init()` is a bare `logger.warning`
call with no `type`/`subtype` (D-08 confirmed: no `suppress_warnings` route exists for this warning),
connected to Sphinx's `config-inited` event, so it fires for **every** builder including `-b html`
(D-10) — the docs sweep must not claim this is typst-builder-specific.

## RST Authoring Mechanics for D-05/D-07 (Priority 2)

**Table directive: use `.. list-table::`.** This docs corpus already uses `list-table` twice
(`docs/source/user_guide/builders.rst:9`, `docs/source/examples/basic.rst:100`) and both render
successfully through the *current* `tox -e docs-html` and `tox -e docs-pdf` builds (both measured
green in Priority 6, below) — i.e. this exact directive is already proven to survive both the furo
HTML build and this extension's own `typstpdf` dogfooding build. `typsphinx/translator.py` implements
the full docutils table node chain read this session
`[VERIFIED: typsphinx/translator.py:4079,4214,4465,4475,4484,4505,4525,4543,4562,4578]`:
`visit_table`/`depart_table`, `visit_tgroup`/`depart_tgroup`, `visit_colspec`, `visit_thead`,
`visit_tbody`, `visit_row`, `visit_entry`/`depart_entry` — including `morecols`/`morerows` → colspan/
rowspan translation (`translator.py:4573-4598`). Since `list-table`, a plain simple table, a grid
table, and `csv-table` all parse down to the *same* `table`/`tgroup`/`thead`/`tbody`/`row`/`entry`
doctree, the RST *source syntax* choice does not affect translator support — any of them would render.
`list-table` is recommended purely for corpus-convention consistency, not because an alternative would
fail.

**Cross-reference roles:** `:doc:` is used pervasively throughout `user_guide/*.rst` (18+ live uses
found, e.g. `configuration.rst:58,139,215,235,307,355,387-389`) and proven safe by both green builds.
`:ref:` is used in `docs/source/index.rst:71-73` (`genindex`/`modindex`/`search`) and safe. `:confval:`
is **not used anywhere** in this repo's docs; this codebase's convention for naming a config value is a
double-backtick inline literal (`` ``typst_document_templates`` ``), not the Sphinx `:confval:` role —
D-05/D-07's new content should follow this existing convention rather than introduce an unproven role.

## Doc-Gate Test Shapes (Priority 3)

Six existing gate modules read in full this session. Common shape across all of them:

- **Discovery is run-time, never a hard-coded list.** `test_docs_contract_claims_gate.py`'s
  `_iter_rst_pages()` does `sorted(DOCS_SOURCE_DIR.rglob("*.rst"))`;
  `test_docs_template_layout_gate.py`'s `_discover_policed_files()` does the same over three policed
  roots. D-06's new gate should copy this pattern for scanning `typsphinx/*.py`.
- **Exclusion sets are explicit dicts/sets with an inline reason string**, never a bare list.
  `test_docs_contract_claims_gate.py`'s `EXCLUDED_CLAIM_PAGES` is the canonical example (one entry:
  `changelog.rst`, with its reason). DOC-17's history-exclusion should follow this exact shape.
  Failure mode this defends: `test_every_excluded_page_still_makes_a_claim` catches a *stale*
  exclusion (a page that no longer matches the classifier but is still excluded).
- **"Patterns have teeth" self-tests are inline synthetic strings, never file reads.**
  `test_docs_template_layout_gate.py::test_patterns_have_teeth` and
  `test_docs_contract_claims_gate.py`'s `TestForbiddenClaimDetectorIsFailFirst` both feed a known-bad
  string directly to the classifier function and assert it fires, and feed a known-good string and
  assert it does not. D-06's gate needs the equivalent: feed a synthetic "leading clause present in
  code but absent from docs" case and a synthetic "leading clause present in docs but absent from
  code" case, proving both directions of the two-way check actually fire.
- **`_run_sphinx_build` is copied near-verbatim per module, never imported from a sibling.**
  Confirmed identical (modulo the `builder` default parameter) across
  `test_output_layout_docs_gate.py`, `test_user_template_relative_asset_gate.py`,
  `test_quickstart_docs_gate.py`, `test_removed_config_deprecation_gate.py`. All invoke
  `[sys.executable, "-m", "sphinx", "-b", builder, str(source_dir), str(build_dir)]` via
  `subprocess.run(..., capture_output=True, text=True)` — never `uv run sphinx-build` or a resolved
  `sphinx-build` binary, to sidestep the NixOS PATH-shadowing hazard. Follow this exact pattern for
  any new subprocess-based gate.
- **Never-skip modules avoid BOTH a `typst-py` import guard AND a subprocess call.**
  `test_docs_contract_claims_gate.py` and `test_output_layout_docs_gate.py`'s
  `TestPublishedOutputLayoutTextMatchesBuild` class both read `.rst` files and call plain Python
  functions/read plain text — no `typst-py` dependency, no `sphinx-build` subprocess — this is what
  lets them run in every CI lane unconditionally. D-06's gate (reading `typsphinx/*.py` source via
  `ast`/regex, reading `.rst` prose) fits this shape exactly and should follow it: no
  `@pytest.mark.skipif`.
- **Gates that DO need a real build use `@pytest.mark.skipif(not TYPST_AVAILABLE, ...)`**, checking
  `import typst` succeeds — this is a *narrower* guard than "can actually compile," but in this
  sandbox (Priority 4, below) both import and compile succeed, so the guard's imprecision is currently
  moot here; it still means CI environments without `typst-py` will skip these classes.

**Critical finding — a currently-passing assertion will break when `output_layout.rst:159` is
fixed, and must be updated in the same task:**
`tests/test_output_layout_docs_gate.py::TestPublishedOutputLayoutTextMatchesBuild::
test_page_states_the_shared_child_composition` (`test_output_layout_docs_gate.py:461-478`) currently
asserts:

```python
assert "writes ten ``.typ`` files" in text, (
    "docs/source/user_guide/output_layout.rst does not publish the "
    "'writes ten ``.typ`` files' count claim for the three-master "
    "example."
)
```

This is a **different, independent** assertion from the one CONTEXT.md already names
(`test_three_master_project_emits_ten_typ_files`, at lines 351-398 of the same file, which asserts the
*build output* is a **nine**-file root set and is already correct/green). This second assertion checks
the *published prose* still says "ten," and will go RED the instant the plan corrects
`output_layout.rst:159`'s "ten" to "nine." **The plan that fixes `output_layout.rst:159` must, in the
same task, update this assertion string to `"writes nine ``.typ`` files"` (or whatever exact wording
the corrected prose uses) — otherwise the fix breaks a previously-green test and the phase cannot
close green.** This is exactly the class of same-wave/same-plan evidence dependency the project's own
memory (`same-wave-evidence-dependency-blind-spot.md`) warns about, but inverted: here the *test*
depends on the *doc*, and both must move together within one task/commit, not across a wave boundary.

`test_output_layout_docs_gate.py`'s `TestPublishedOutputLayoutTextMatchesBuild` class (5 tests,
lines 401-509) is otherwise a template worth copying directly for D-06's second binding assertion class
(if the plan chooses to bind the error-table prose to a real build for any of the seven config-caused
shapes rather than relying solely on the leading-clause static scan).

## DOC-16 Fixture Extension (Priority 4)

**`typst-py` is available and *actually compiles* in this sandbox** `[VERIFIED: measured this
session]` — not merely importable. `uv run python3 -c "import typst"` succeeds (package resolves from
`.venv/lib/python3.13/site-packages/typst/`), and the existing fixture's full test class
(`tests/test_user_template_relative_asset_gate.py::TestUserTemplateRelativeAssetGate`, 4 tests: build
succeeds, PDF is valid, asset reached the bundle destination, wrapper imports the bundled template)
was run this session and **passed 4/4** in 0.31s. This is a real `sphinx-build -b typstpdf` →
`typst.compile()` round trip, not a mock. No native `typst` CLI binary exists on `PATH` in this
sandbox — but `typst-py` does not need one; it bundles its own compiled engine, callable only via
`typst.compile()`.

**Measured destination paths** (from the passing test, `test_asset_reached_the_bundle_destination`,
`test_user_template_relative_asset_gate.py:119-128`): the fixture uses the reserved `"typst"` key
(`conf.py`'s `typst_documents` entry has no fifth element, so it resolves to `RESERVED_REGISTRY_KEY`),
so its bundle lands at `<outdir>/_template/typst/`. A `refs.bib` added beside `branded.typ` in
`tests/fixtures/user_template_relative_asset_gate/_typst/` would, by the same wholesale-copy
mechanism already proven for `logo.png`, land at `<outdir>/_template/typst/refs.bib`.

**What adding `refs.bib` + `#bibliography("refs.bib")` requires**, concretely:

1. A new file `tests/fixtures/user_template_relative_asset_gate/_typst/refs.bib`, any valid BibTeX
   entry (Typst's `bibliography()` accepts `.bib` — Hayagriva `.yml` is the other supported format,
   but BibTeX is what `advanced.rst`'s existing example already uses, so BibTeX keeps the fixture
   consistent with the doc it is proving).
2. A `#bibliography("refs.bib")` call added to `_typst/branded.typ`'s body (or `show:` chain) — the
   bare relative filename, matching the corrected doc claim, not `"_typst/refs.bib"`.
3. A new assertion in `TestUserTemplateRelativeAssetGate` (or a sibling test class) asserting
   `(build_dir / "_template" / "typst" / "refs.bib").exists()`, following the exact pattern
   `test_asset_reached_the_bundle_destination` already uses for `logo.png`/`branded.typ`.
4. No `@preview` package needed — Typst's `bibliography()` is a built-in function, not a Universe
   package, so this does not risk becoming a fourth version-lockstep site.

This confirms CONTEXT.md's DOC-16 recommendation is fully executable with no environmental blocker.

## The `--root` Claim, Empirically Corrected (Priority 5)

**This is the most significant finding of this research and directly affects how D-03's note must be
worded.**

CONTEXT.md states: *"the hand-compile consequence Phase 54 recorded for this phase (`typst compile
build/typst/manual.typ` now needs `--root build/typst`, because the wrapper's `#import` is
root-absolute)."* This research tested that exact claim empirically, using `typst-py`'s `compile()`
function (which accepts the same `root` parameter the CLI's `--root` flag sets — confirmed via
`help(typst.compile)`, whose signature is `compile(input, output=None, root=None, ...)`, and via
`typsphinx/pdf.py:143`'s own call, `typst.compile(typ_path, root=root_dir)`).

**Reproduction 1 — the bare-target case (`output_layout.rst`'s own worked example, target
`"manual"`):**

```
$ sphinx-build -b typst <fixture> <build>   # wrapper written at <build>/manual.typ
$ python3 -c "import typst; typst.compile('<build>/manual.typ')"    # NO root kwarg
SUCCESS default-root, len=26131
```

The emitted wrapper's import line (`[VERIFIED: real build output, this session]`) is
`#import "/_template/typst/base.typ": project` — root-absolute, exactly as CONTEXT.md states. It
compiles fine with **no** `root` argument because Typst's documented default (confirmed via
WebSearch against typst.app-derived community documentation: "by default, Typst uses the directory
containing the input file as the project root") makes the default root `<build>/` — which is exactly
where `_template/typst/base.typ` already sits, one level down. **`typst compile build/typst/manual.typ`
with no `--root` succeeds** for this exact worked example.

**Reproduction 2 — the nested-target case (`typst_documents` target `"manuals/guide.typ"`):**

```
$ sphinx-build -b typst <fixture> <build>   # wrapper written at <build>/manuals/guide.typ
$ python3 -c "import typst; typst.compile('<build>/manuals/guide.typ')"    # NO root kwarg
FAILURE default-root: TypstError file not found (searched at <build>/manuals/_template/typst/base.typ)
$ python3 -c "import typst; typst.compile('<build>/manuals/guide.typ', root='<build>')"
SUCCESS explicit-root, len=26204
```

Here the default root becomes `<build>/manuals/` (the wrapper's own directory), which is **not** where
the bundle lives, so the root-absolute import fails to resolve — and passing `root=<build>` (the
outdir) fixes it, exactly matching what `--root build/typst` would do from the CLI.

**Conclusion for the plan:** the `--root` note is correct and necessary, but **only for a wrapper
written under a target with a path component** (i.e. not written directly at the outdir root). For the
common case — and specifically for the bare-target `manual.typ` example the "Which File to Compile"
section already shows — no `--root` flag is needed; Typst's own default root already equals the outdir
root. **Writing the note as an unconditional "you now need `--root build/typst` to hand-compile any
wrapper" would itself be a new inaccuracy** for the exact example the section uses. The plan should
either (a) scope the note explicitly to "a wrapper written under a target with a path component (see
`output_layout.rst`'s 'A path in the target' section) needs `--root <outdir>` to hand-compile; a
bare-target wrapper at the outdir root does not," or (b) recommend `--root` universally as a safe habit
while being honest that it is not strictly required for the bare case — but must not claim it is
*required* for the bare case, since this is measurably false. `pdf.py:143`'s own call
(`typst.compile(typ_path, root=root_dir)`, unconditionally passing `root=outdir`) is why neither
builder (`typst` nor `typstpdf`) is ever affected either way — this part of CONTEXT.md's framing is
correct and unaffected by this correction.

## Build-Gate Cost and Green-ness at HEAD (Priority 6)

All measured this session, on HEAD (`f07e8cb8`):

| Gate | Result | Time |
|---|---|---|
| `uv run pytest -q` (full suite) | **1366 passed, 5 skipped, 0 failed** | 121.6s |
| `uv run black --check .` | Clean, 336 files unchanged | — |
| `uv run ruff check .` | All checks passed | — |
| `uv run mypy typsphinx/` | Success: no issues found in 8 source files | — |
| `uv run tox -e docs-html` | build succeeded, 3 warnings (all pre-existing/unrelated — see below) | 3.28s (setup 0.05s + cmd 3.23s) |
| `uv run tox -e docs-pdf` | build succeeded, 2 warnings (pre-existing/unrelated, same class) | 3.18s (setup 0.02s + cmd 3.15s) |

**The five pytest skips**, verified by name, are all pre-existing and unrelated to this phase:
`tests/test_changelog_page_gate.py` (4 skips — myst-parser is docs-extra-gated, D-01 precedent) and
`tests/test_corpus_gate.py:530` (1 skip — env-gated behind `TYPSPHINX_CORPUS_REPORT=1`). **The
carve-out for `tests/test_state_guard_shapes_gate.py`'s 7 failures that STATE.md warns is a
"recurring stale note" is confirmed correctly retired — that module does not appear in the skip or
failure list at all; the suite is unconditionally 0-failed.**

**The docs-html/docs-pdf warnings are pre-existing and out of this phase's scope**, both instances of
`WARNING: unknown node type: <doctest_block ...>` — Sphinx's autodoc extension rendering a
`>>> compute_template_import_path(...)` doctest example from a Python docstring
(`writer.py`'s `compute_template_import_path`/`compute_content_include_path` functions) into the API
reference pages (`docs/source/api/index.rst` autodoc output), which the `typsphinx` translator does
not have a `doctest_block` node handler for. This is unrelated to any of the hand-authored `.rst` pages
this phase touches, and is not part of DOC-15/16/17's scope; it is not a regression to fix here, just a
pre-existing baseline the planner should not attribute to this phase's changes if it resurfaces in a
post-plan build.

**Baseline for the planner:** the tree is unconditionally green (0 failures, 0 lint/type errors, both
docs builds succeed) at the phase's starting point. Any RED introduced during this phase's plans is
attributable to the phase's own changes, with no ambient carve-out to lean on.

## Common Pitfalls

### Pitfall 1: Fixing stale prose without updating the test that currently asserts the stale text
**What goes wrong:** `output_layout.rst:159`'s "ten" is corrected to "nine," but
`test_page_states_the_shared_child_composition` (which asserts the literal string `"writes ten
``.typ`` files"`) is left untouched — the fix turns a passing test RED.
**Why it happens:** Two independent tests bind to the same underlying fact from opposite directions
(one asserts the build produces nine files; the other, less obviously, asserts the *page* still says
ten) and only one of them was already updated (in Phase 54), creating the illusion that the doc-gate
side is already handled.
**How to avoid:** Grep `test_output_layout_docs_gate.py` for the literal string `"ten"` before closing
any task that touches `output_layout.rst:159`, and update both the prose and this assertion in the
same commit.
**Warning signs:** `pytest tests/test_output_layout_docs_gate.py` going RED immediately after an
otherwise-correct prose fix.

### Pitfall 2: Writing an unconditional `--root` claim
**What goes wrong:** The plan writes "hand-compiling a wrapper now requires `--root build/typst`" as
a blanket statement, matching CONTEXT.md's literal phrasing — but the exact worked example the section
already shows (`manual.typ` at the outdir root) compiles fine without `--root`, so the new prose is
itself measurably false the moment a reader tries it against that example.
**Why it happens:** The underlying code fact (root-absolute import) is real and does create a genuine
hazard — just only for nested wrapper targets, not the common bare-target case the surrounding prose
walks through.
**How to avoid:** Scope the note to targets with a path component (see Priority 5), or test both cases
before publishing the claim.
**Warning signs:** A reader following the doc's own bare-target example and finding `--root` was
unnecessary — a "the docs told me to do something I didn't need to do" complaint, the softer sibling of
"the docs told me something false."

### Pitfall 3: Treating `_write_template_file`/`_template.typ` mentions in `tests/` as sweep targets
**What goes wrong:** A broad `_template.typ` cleanup pass edits `tests/*.py` or
`tests/fixtures/**/conf.py`, which either breaks passing regression tests (some deliberately assert
`_template.typ` no longer exists, or deliberately exercise a user template *named* `_template.typ` as
an edge case) or duplicates work 54.1 D-12 already decided against (tests/ is not policed).
**Why it happens:** A naive repo-wide grep for `_template.typ` returns ~40 test-directory hits
alongside the ~7 genuine doc hits, and it is tempting to "clean up everything the grep found."
**How to avoid:** Classify every grep hit by directory before touching it — only `docs/source/`,
`README.md`, and `examples/**` (per 54.1 D-12's already-established policed scope) are in-scope
sweep targets; `tests/` hits are either correct-as-is or out of this phase's jurisdiction.
**Warning signs:** A diff touching any file under `tests/` for a "docs sweep" task.

### Pitfall 4: Missing that shape #2's aggregate absorbs 8 sub-cases, not 6
**What goes wrong:** D-05's error-table row for shape #2 (or any explanatory prose accompanying it)
enumerates only the six sub-cases CONTEXT.md's summary names, silently omitting CONF-16 (reserved-key
redeclaration) and the `template`-wrong-Python-type guard — both real, both currently reachable, both
producing distinct sub-messages inside the same aggregate.
**Why it happens:** CONTEXT.md's own D-05 note is itself a summary, written during discussion without
re-reading the full accumulation loop.
**How to avoid:** If the plan's prose illustrates shape #2's sub-cases at all (the table row itself
only needs the leading clause, per D-05), use the eight-item list this research verified
(`typsphinx/template_registry.py:330-424`), not the six-item one.
**Warning signs:** A user hitting the CONF-16 or wrong-type sub-case and finding it undocumented despite
the aggregate row supposedly covering "every config-caused shape."

## Code Examples

### The verified error-table source-of-truth pattern (D-06's leading-clause extraction)

```python
# Source: typsphinx/template_registry.py:437-441 (verified this session)
if failures:
    summary = "; ".join(failures)
    raise ExtensionError(
        f"typst_document_templates: {len(failures)} invalid "
        f"definition(s): {summary}"
    )
```

The leading clause a doc-gate must extract and match is
`"typst_document_templates: {N} invalid definition(s): "` — i.e. everything up to and including the
first `: ` after the interpolated count, with `{N}`/`{len(failures)}` normalized to a wildcard. A
regex approach for the *simple* (non-concatenated, single-f-string) shapes:

```python
import re

LEADING_CLAUSE_RE = re.compile(
    r'raise ExtensionError\(\s*\n?\s*f?"([^"]*\{[^}]*\}[^"]*:)'
)
```

...but this will not reach `builder.py:2151`'s call-through-a-helper shape or
`template_registry.py:422`'s implicit-concatenation shape — an `ast`-based scanner (walking `Call`
nodes for `ExtensionError(...)`, resolving `JoinedStr` and adjacent `Constant` concatenation, and
following at least one level of same-module function-call indirection for the
`_conf17_violation_message()` case) is the only approach proven to reach all nine shapes at their real
source shapes. See Priority 1 above for the exact source excerpts to test the parser against.

### The doc-gate skip-avoidance pattern (D-06 must follow this)

```python
# Source: tests/test_docs_contract_claims_gate.py:16-24 (verified this session)
# "Subject: published prose, not emitted output. Every real-compile 'does the
#  code do what it says' proof already lives in [runtime gates]... This module
#  asks a different question -- does the PROSE agree with the code's own
#  predicate... No typst-py dependency, no sphinx-build subprocess: this
#  module never skips."
```

### The DOC-16 fixture destination path, measured

```python
# Source: tests/test_user_template_relative_asset_gate.py:119-128 (test passed
# this session, 4/4, 0.31s)
def test_asset_reached_the_bundle_destination(self, build):
    build_dir = build["build_dir"]
    assert (build_dir / "_template" / "typst" / "logo.png").exists()
    assert (build_dir / "_template" / "typst" / "branded.typ").exists()
    # A refs.bib added beside branded.typ would land at the same
    # _template/typst/ directory by the identical wholesale-copy mechanism.
```

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (config in `pyproject.toml`) |
| Config file | `pyproject.toml` |
| Quick run command | `uv run pytest tests/test_docs_contract_claims_gate.py tests/test_output_layout_docs_gate.py tests/test_docs_template_layout_gate.py tests/test_user_template_relative_asset_gate.py tests/test_quickstart_docs_gate.py tests/test_removed_config_deprecation_gate.py -q` (the six existing doc-gate modules; add the two new ones once written) |
| Full suite command | `uv run pytest -q` (1366 passed, 5 skipped, 121.6s measured this session) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DOC-15 | Element [4] documented as registry key; "accepted and ignored" retracted everywhere | Static prose-scan (new D-06 gate) + repo-wide grep self-test | `uv run pytest tests/test_registry_documentation_gate.py -x` (name TBD, planner's discretion) | ❌ Wave 0 — new module |
| DOC-15 | Every published error-table clause exists in code, and every code shape exists in the table (two-way) | Static AST-scan (new D-06 gate) | same module as above | ❌ Wave 0 |
| DOC-16 | `templates.rst`/`advanced.rst` asset examples describe what actually works | Real `sphinx-build -b typstpdf` → `typst.compile()` (extend existing fixture) | `uv run pytest tests/test_user_template_relative_asset_gate.py -x` | ✅ exists, extend with `refs.bib` case |
| DOC-16 | Prose names the measured bundle-relative destination | Prose-binding assertion against the extended fixture's build | new test method in the same module, or a sibling `test_asset_doc_binding_gate.py` | ❌ Wave 0 — new test method |
| DOC-17 | Migration guidance published for all three removed values, matching CONF-19's warning text | Prose ↔ `REMOVED_CONFIG_VALUES` dict binding | new module, or extend `test_removed_config_deprecation_gate.py` | ❌ Wave 0 |
| SC#4 | Repo-wide sweep leaves no stale claim; both doc builds stay green | Repo-wide grep self-test (new) + `tox -e docs-html`/`docs-pdf` | `uv run tox -e docs-html && uv run tox -e docs-pdf` | ✅ tox envs exist; grep self-test is new |
| SC#3 (`output_layout.rst:159`) | Published file-count claim matches real build | Existing prose-binding test, **must be updated in the same task as the prose fix** | `uv run pytest tests/test_output_layout_docs_gate.py -x` | ✅ exists — **update, don't create** |

### Sampling Rate

- **Per task commit:** run the specific gate module(s) the task's files touch (e.g.
  `pytest tests/test_output_layout_docs_gate.py -x` after any `output_layout.rst` edit).
- **Per wave merge:** `uv run pytest -q` (full suite, ~122s) plus `uv run black --check . && uv run ruff check . && uv run mypy typsphinx/` (all measured near-instant).
- **Phase gate:** `uv run tox -e docs-html && uv run tox -e docs-pdf` (both ~3.3s, green at HEAD) must
  stay green, per SC#4's explicit naming of these two commands.

### Wave 0 Gaps

- [ ] A new test module (name at planner's discretion, subject to D-06) binding
      `configuration.rst`'s new registry subsection + error table + key-naming rules + removed-values
      subsection to `typsphinx/template_registry.py`, `typsphinx/builder.py`, and
      `typsphinx/removed_config.py` — the two-way leading-clause gate (D-06) and the removed-config
      binding (DOC-17).
- [ ] `tests/fixtures/user_template_relative_asset_gate/_typst/refs.bib` — new fixture file (DOC-16).
- [ ] A new or extended test method proving `templates.rst`/`advanced.rst`'s corrected asset prose
      matches the extended fixture's real build output (DOC-16).
- [ ] Update (not create) `tests/test_output_layout_docs_gate.py`'s
      `test_page_states_the_shared_child_composition` string from "ten" to "nine" in the SAME task
      that corrects `output_layout.rst:159` (see Pitfall 1).

## Security Domain

`security_enforcement` is `true` in `.planning/config.json` (ASVS level 1, block on `high`). This
phase changes no production code, no input handling, no authentication, no authorization, no
cryptography, and no network-facing surface — it edits `.rst`/`.md` prose and adds Python test modules
that read source files and run local `sphinx-build` subprocesses against fixture directories already
present in the repo (no untrusted input, no new subprocess target shape).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | N/A — no auth surface touched. |
| V3 Session Management | No | N/A. |
| V4 Access Control | No | N/A. |
| V5 Input Validation | No | The new test modules invoke `subprocess.run([sys.executable, "-m", "sphinx", ...])` with a fixed argument list and fixture-controlled paths, following the exact pattern six existing gate modules already use — no user-controlled input reaches the subprocess call. |
| V6 Cryptography | No | N/A. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Test-fixture subprocess invocation with attacker-controlled paths | Tampering (theoretical) | Not applicable here — fixture directories are static, repo-committed content under `tests/fixtures/`, never derived from external/network input; the existing six gate modules establish this as safe practice already relied upon project-wide. |

No new threat surface is introduced by this phase.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The community-sourced WebSearch description of Typst's default-root behaviour ("the directory containing the input file") is accurate. | Priority 5 (`--root` claim) | Low — this claim was independently cross-checked by two direct empirical reproductions (`typst.compile()` succeeding without `root` for the bare-target case and failing without it for the nested case, matching the stated rule exactly in both directions), so the WebSearch description is corroborated by measurement, not relied on alone. |
| A2 | `examples/charged-ieee/approach2/conf.py:21,23,25`'s comment wording is "not required to fix" rather than a genuine sweep target. | Priority 1 grep table | Low — if wrong, the fix is a one-line comment edit with zero behavioural risk; flagged explicitly for the planner's discretion rather than asserted as settled. |
| A3 | `CLAUDE.md:49`'s stale `_write_template_file` architecture description is out of DOC-15/16/17's literal scope and can be deferred. | Priority 1 grep table (new finding) | Low-medium — if the planner disagrees and folds it in, it is a one-line fix with no test-gate dependency; if left unfixed, `CLAUDE.md` continues describing deleted code to future sessions, a minor but real onboarding-accuracy risk that is unrelated to any of this phase's four success criteria. |

**Assumption A1's residual risk is close to zero** given the empirical cross-check; A2 and A3 are
scope-boundary judgment calls, not factual risks.

## Open Questions

1. **Should the `CLAUDE.md:49` architecture staleness be fixed in this phase or filed separately?**
   - What we know: it is a genuine inaccuracy (`_write_template_file` no longer exists), discovered by
     this phase's own repo-wide grep, but outside `docs/source/`/`README.md`/`examples/**` (the
     policed scope 54.1 D-12 established) and not named by DOC-15/16/17 or SC#4's literal wording.
   - What's unclear: whether "no published surface" (SC#1) or "no stale claim survives the sweep"
     (SC#4) is meant to extend to `CLAUDE.md`, which is dev-facing rather than reader-published.
   - Recommendation: treat as Claude's discretion (like the two gray areas CONTEXT.md already left
     open) — a one-line fix, low risk either way; note it in the plan's rationale if included, or file
     a housekeeping todo if deferred.

2. **Exact wording for the scoped `--root` note (Priority 5).**
   - What we know: `--root <outdir>` is required exactly when the wrapper's own target has a path
     component; not required when the wrapper is at the outdir root.
   - What's unclear: whether to phrase this as a conditional rule (accurate, slightly more complex) or
     recommend `--root` unconditionally as a defensive habit while noting it is not strictly required
     for the bare case (simpler, avoids conditional prose, still accurate if worded carefully as "safe
     to always pass, required when...").
   - Recommendation: the planner should choose based on `configuration.rst`'s and `output_layout.rst`'s
     existing prose style (which already handles conditional cases carefully, e.g. the `lang`
     route-scope prose) — a conditional statement matching that established style is likely the better
     fit, but either is factually defensible as long as it does not claim `--root` is required for the
     bare-target case.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `typst-py` | DOC-16 fixture extension, `--root` empirical verification | ✓ | resolves from `.venv/lib/python3.13/site-packages/typst/`; `typst.compile()` confirmed working this session | — |
| `typst` CLI binary | Would be needed only to reproduce the `--root` CLI-flag claim literally via the command line | ✗ | — | Not needed — `typst-py`'s `typst.compile(..., root=...)` accepts the identical `root` parameter the CLI's `--root` flag sets, and was used for all empirical reproduction in Priority 5. |
| `sphinx-build` / Sphinx | Every doc-gate test's `_run_sphinx_build` helper | ✓ | invoked via `sys.executable -m sphinx`, per this repo's own NixOS-sandbox convention | — |
| `myst-parser` | `tox -e docs-html`/`docs-pdf` (Markdown → RST for `changelog.rst` includes) | ✓ (via `docs` tox extra) | build succeeded this session | The 4 `test_changelog_page_gate.py` skips in the base `uv run pytest` invocation are pre-existing and unrelated — the `docs` extra's own tox environment builds successfully. |

No missing dependencies block this phase.

## Sources

### Primary (HIGH confidence)
- `typsphinx/template_registry.py` (full file read this session) — the four `ExtensionError` shapes and the eight sub-cases feeding shape #2.
- `typsphinx/builder.py` (relevant regions read this session, lines ~870-960, 1250-1320, 1980-2010, 2140-2160, 2160-2185, 2365-2385) — the five `ExtensionError` shapes plus the `builder.py:2151`/`2377` findings.
- `typsphinx/writer.py` (lines 75-235 read this session) — `TEMPLATE_OUTPUT_DIR`, `compute_template_import_path()`'s root-absolute construction, and the confirmed-dead `_compute_template_import_path()`.
- `typsphinx/removed_config.py` (full file read this session) — `REMOVED_CONFIG_VALUES`, quoted verbatim above.
- `typsphinx/pdf.py` (lines 1-30, 120-155 read this session) — `typst.compile(typ_path, root=root_dir)` at line 143.
- `typsphinx/translator.py` (grep + line citations this session) — table-node and cross-reference-node method inventory.
- `docs/source/user_guide/configuration.rst`, `output_layout.rst`, `templates.rst`, `builders.rst`, `docs/source/examples/advanced.rst`, `docs/source/quickstart.rst`, `docs/source/examples/basic.rst` (all read in full or substantially this session).
- `examples/basic/README.md`, `examples/advanced/README.md`, `examples/charged-ieee/approach2/conf.py` (read this session).
- `tests/test_docs_contract_claims_gate.py`, `tests/test_output_layout_docs_gate.py`, `tests/test_docs_template_layout_gate.py`, `tests/test_user_template_relative_asset_gate.py`, `tests/test_quickstart_docs_gate.py`, `tests/test_removed_config_deprecation_gate.py` (all read in full this session).
- `tests/fixtures/user_template_relative_asset_gate/` (conf.py, index.rst, `_typst/branded.typ` read in full this session).
- Real command execution this session: full pytest suite, black/ruff/mypy, `tox -e docs-html`/`docs-pdf`, two real `sphinx-build` invocations plus four `typst.compile()` calls reproducing the `--root` claim.

### Secondary (MEDIUM confidence)
- WebSearch: Typst CLI `--root` default-behaviour description (cross-checked and corroborated by direct `typst.compile()` reproduction in this session — see Assumption A1).

### Tertiary (LOW confidence)
- None — every claim in this document is either read from source this session, or measured by a command run this session, or explicitly tagged `[ASSUMED]`/logged in the Assumptions table above.

## Metadata

**Confidence breakdown:**
- Standard stack: N/A — no new packages this phase.
- Architecture (doc-gate test shapes, error-shape inventory): HIGH — every claim traced to a specific file:line read this session.
- Pitfalls: HIGH — both named pitfalls (the "ten"/"nine" test collision and the `--root` overclaim) were discovered by direct measurement, not inferred.

**Research date:** 2026-08-16
**Valid until:** This research is tied to a specific commit (`f07e8cb8`). Re-verify line numbers if
the planner's own working tree has diverged from this commit before consuming this document (e.g. if
Phase 55's plans landed further commits after this research was written).
