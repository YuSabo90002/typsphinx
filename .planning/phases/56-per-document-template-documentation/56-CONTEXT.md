# Phase 56: Per-Document Template Documentation - Context

**Gathered:** 2026-08-16
**Status:** Ready for planning

<domain>
## Phase Boundary

The published documentation describes the registry and bundle layout that actually shipped in
Phases 53/54/54.1. **No production code changes.** In scope: DOC-15, DOC-16, DOC-17, plus the
repo-wide sweep of claims the new layout invalidates (ROADMAP Phase 56 SC#4).

Concretely this phase (a) documents `typst_document_templates` — which today has **zero** mentions
anywhere under `docs/source/` — (b) retracts the `configuration.rst:80` "accepted and ignored"
definition of `typst_documents` element [4], (c) fixes the asset guidance that teaches a path the
bundle layout no longer resolves, (d) publishes migration guidance for the three removed config
values, and (e) sweeps the remaining `_template.typ`-era claims out of the reader-visible doc set.

New tests are in scope **only** as doc↔code binding gates (the shape DOC-11/DOC-13/DOC-14 already
established). Out of scope: any change to `typsphinx/*.py` behaviour; CHANGELOG curation and the
version bump (Phase 57); WR-02/WR-03/WR-04/IN-01 from `54-REVIEW.md`.

</domain>

<decisions>
## Implementation Decisions

### Where the registry is documented

- **D-01:** `typst_document_templates` gets **exactly one new subsection in
  `docs/source/user_guide/configuration.rst`**, as the fifth subsection of the existing "Template
  Configuration" section (which today holds Template Function / Custom Template File / Typst
  Package / Template Assets). `templates.rst` gets **no** registry walkthrough, and **no** new
  `user_guide/` page is created. Measured basis: DOC-15's requirement text names `configuration.rst`
  and nothing else; `user_guide/index.rst` currently lists four pages; and this repository has
  already paid once for a cross-page contract split — `45.1-REVIEW.md` CR-01 was exactly a claim
  published on a page the agreement proof never read, which is why
  `tests/test_docs_contract_claims_gate.py` exists. One page means one place to keep true.
  `configuration.rst` grows from 390 lines to roughly 470.

- **D-02:** `configuration.rst:80`'s element [4] is renamed from **"Document class (usually
  'typst') — accepted and ignored"** to the **registry key** into `typst_document_templates`, stating
  that an absent element [4] resolves to the reserved `"typst"` key. **Every existing five-element
  example stays byte-identical.** Measured basis: `RESERVED_REGISTRY_KEY = "typst"`
  (`typsphinx/template_registry.py:38`) is synthesized on every build, so all 15 published
  five-element examples (`quickstart.rst:93`; `templates.rst:25`; `configuration.rst:40,351`;
  `output_layout.rst:28,77,127`; `examples/basic.rst:20,224`; `examples/advanced.rst:155-157,258-259,418`;
  plus `examples/charged-ieee/approach1/conf.py:17`) resolve correctly as written. The worked example
  using a **non-default** key lives inside the new registry subsection and nowhere else. SC#1's
  "survives in **no** published surface" is therefore satisfied by fixing one line — but the
  discovery grep is still run repo-wide (milestone invariant #4/#11), not scoped to that line.

- **D-03:** `docs/source/user_guide/output_layout.rst` becomes the **canonical page for output
  layout**: the `_template/<key>/` directory story (one bundle per used key, copied wholesale,
  keys that are declared but unused are not copied), the corrected file-count rule, and the
  hand-compile consequence Phase 54 recorded for this phase (`typst compile build/typst/manual.typ`
  now needs `--root build/typst`, because the wrapper's `#import` is root-absolute). The `--root`
  note goes in that page's existing **"Which File to Compile"** section, which already discusses
  compiling the wrapper by hand — splitting it into `builders.rst` would send the reader between two
  pages. `builders.rst:122-127` gets **only** the file-count correction. The new registry subsection
  in `configuration.rst` links to `output_layout` rather than restating the layout.

  Measured stale sites: `output_layout.rst:34` ("`_template.typ`, which holds the template the
  wrapper imports"), `:119` ("the reserved `_template.typ` file"), `:140` ("not even
  `_template.typ`"), `:159` (the three-master file-count rule: "writes ten `.typ` files … nine on
  the `typst_package` route"); `builders.rst:127`; `examples/basic/README.md:38`;
  `examples/advanced/README.md:65`. Note the corresponding **test** was already corrected in
  Phase 54 — `tests/test_output_layout_docs_gate.py::test_three_master_project_emits_ten_typ_files`
  asserts a **nine**-file root set plus `_template/typst/base.typ` — so the prose is provably behind
  the measured build in a place no current assertion catches.

- **D-04:** The registry subsection's **central worked example is the `template` route with two
  masters and no network dependency** — one entry on the reserved `"typst"` key, one on a declared
  key resolving to a local `_typst/…typ`. The `package` route is shown only as a short
  schema-level example. Rationale: SC#2 requires each published example to be exercised by a real
  build; keeping the central example local-only keeps that gate free of a Typst Universe fetch.

### The error catalogue

- **D-05:** `configuration.rst`'s registry subsection carries a **"condition → how the build stops"
  table covering the seven config-caused `ExtensionError` shapes**, plus a short separate note for
  the two I/O-caused shapes stating they are not a `conf.py` problem. Each table row quotes only the
  **identifying leading clause** of the message, never the aggregated body — so a wording tweak
  inside an aggregate does not turn the docs RED.

  Measured inventory (nine distinct message shapes):
  1. `typst_document_templates must be a dict …` — `template_registry.py:303`
  2. `typst_document_templates: N invalid definition(s): …` — `template_registry.py:438`
     (aggregate: non-`str` key, non-`dict` definition, `template`/`package` exclusivity, CONF-17
     source-tree bundle, CONF-18 key shape, template file not found)
  3. `typst_documents entry names registry key X, which is not a string …` — `template_registry.py:513`
  4. `… which is not a registered typst_document_templates key …` — `template_registry.py:523`
  5. `typst: N output path collision(s): …` — `builder.py:950` (includes the `_template/` reservation)
  6. `typst: N pre-write template path failure(s): …` — `builder.py:1312` (54.1: `templates_path`
     collision, hoisted CONF-17, reserved-key case collision)
  7. `typst_document_templates: N bundle destination collision(s): …` — `builder.py:2174`
  8. `typst_document_templates: failed to copy the resolved template …` — `builder.py:1992` — **I/O**
  9. `typst_document_templates: the resolved template … was never copied …` — `builder.py:2002` — **I/O**

- **D-06:** doc↔code agreement is pinned by a **two-way leading-clause gate test**: every clause the
  catalogue publishes must exist in `typsphinx/*.py`, **and** every registry/bundle `ExtensionError`
  shape in `typsphinx/*.py` must appear in the catalogue. Discovery is a run-time scan, never a
  hardcoded file list (milestone invariant #11). The module carries **no** `typst-py` import guard
  and spawns **no** `sphinx-build` subprocess, so it never skips — the same design
  `tests/test_docs_contract_claims_gate.py` chose and for the same stated reason. Per-error runtime
  reproduction is **not** duplicated: `tests/test_registry_prewrite_validation_gate.py` and
  `tests/test_template_prefix_reservation_gate.py` already drive real builds for those shapes.

- **D-07:** CONF-18's key-shape rules get their **own small subsection ("registry key naming
  rules")**, placed before the error table, alongside the statement that a key becomes a directory
  name under `_template/`. It enumerates: empty, `.` / `..`, containing `/` or `\`, a Windows
  reserved device name, a trailing dot or space, and differing from another declared key only by
  case. The error table's row for shape #2 links to it. Rationale: these are rules for **writing** a
  key, not symptoms for looking up an error, so a reader choosing a key must be able to reach them
  without reading the error table.

- **D-08:** The 54.1 `templates_path` collision refusal is documented in **both** the "Custom
  Template File" subsection (preventively — "do not put a Typst template inside Sphinx's
  `templates_path` directory; this repository uses `_typst/`") **and** as one row of the error table
  (shape #6, so a user who already hit it can look it up). Constraint to honour either way:
  `tests/test_docs_template_layout_gate.py::test_every_surviving_jinja_dir_mention_names_templates_path`
  requires any surviving mention of the bare `_templates` token to name `templates_path` on the
  **same line**.

### Claude's Discretion

The two gray areas below were offered and the owner chose to leave them to Claude with the
recommendations recorded here. A planner may depart from a recommendation, but must say why.

- **DOC-16 — what "exercised by a real build" means for the asset examples.** Three precedents exist:
  a new `sphinx-build → typst.compile()` fixture (`tests/test_user_template_relative_asset_gate.py`),
  binding published prose to an existing fixture's measured output
  (`tests/test_output_layout_docs_gate.py`), and a repo-wide presence grep
  (`tests/test_docs_template_layout_gate.py`).
  **Recommendation:** extend the existing `tests/fixtures/user_template_relative_asset_gate/`
  (today: `conf.py`, `index.rst`, `_typst/branded.typ`, `_typst/logo.png`) with a `refs.bib` and a
  `#bibliography("refs.bib")` call, then bind `templates.rst`'s asset tree diagram and
  `advanced.rst`'s `refs.bib` paragraph to that fixture's measured destination paths — one fixture
  proves both published examples, and no new Typst Universe dependency enters the gate.
  The two sites the fix must reach: `templates.rst:79-118` (already rewritten for bundle copying in
  Phase 54, but its closing note still says bundle copying "only applies to custom local templates",
  which understates OUT-04's no-exceptions rule for the built-in `"typst"` key) and
  `advanced.rst:122-131`, which is wrong twice over — it tells the reader the template is written to
  the output root as `_template.typ` and to reference the asset as `"_typst/refs.bib"`, when under
  the bundle layout the template sits at `_template/<key>/custom_ieee.typ` with `refs.bib` beside it,
  so the correct reference is the bare `"refs.bib"`.

- **DOC-17 — where migration guidance is published, and how far the sweep reaches into history.**
  CHANGELOG curation is explicitly Phase 57's (WR-02), so guidance published *in this phase* must
  live under `docs/source/`.
  **Recommendation:** a new "Removed configuration values" subsection in `configuration.rst` covering
  `typst_template_assets`, `typst_authors`, `typst_toctree_defaults`, bound by a test to the three
  strings in `typsphinx/removed_config.py`'s `REMOVED_CONFIG_VALUES` dict (lines 36-57) — that dict
  is already the single source of the warning text, so agreement with "what CONF-19's warning says"
  is machine-checkable rather than asserted.
  **Recommendation on history:** do **not** rewrite historical release notes.
  `docs/source/changelog.rst:16,39,59,63` and `CHANGELOG.md`'s pre-0.9.0 entries describe what was
  true at the version they document; rewriting them would falsify the record. The sweep's target set
  is the current-state pages (`quickstart.rst`, `user_guide/*.rst`, `examples/*.rst`, `README.md`)
  and the runnable `examples/**` READMEs. Whatever set is chosen, the discovery grep runs repo-wide
  first and the exclusion is recorded with its reason — the failure mode invariants #4/#11 exist to
  catch is treating a written file list as the search set.

- Exact section titles, table column headers, and RST directive choices.
- Test file naming and placement for the two new doc gates, subject to D-06's no-skip constraint.
- Whether `examples/basic/README.md:38` and `examples/advanced/README.md:65` are corrected in the
  same plan as the `user_guide/` sweep or a separate one.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase contract

- `.planning/ROADMAP.md` § "Phase 56: Per-Document Template Documentation" — the four success
  criteria. SC#1's "no published surface" and SC#4's "sweep is run repo-wide at discovery time; the
  three requirements name where the fixes are expected, not where the search is scoped" are the two
  clauses most likely to be under-read.
- `.planning/REQUIREMENTS.md` lines 118-126 — DOC-15, DOC-16, DOC-17 verbatim.
- `.planning/ROADMAP.md` lines 392-472 — the eleven binding milestone constraints. Binding here:
  **#11** (repo-wide grep at discovery time for "anywhere under X" criteria; `@preview` count stays
  four with no new lockstep site; typing-import modernization forbidden; full pytest + black + ruff +
  mypy green at the phase boundary), **#2** (green at every phase boundary), **#9** (milestone branch
  stays pushed to `origin`).
- `.planning/PROJECT.md` § "Current Milestone: v0.9.0 per-document templates" — the "one output rule,
  no exceptions" statement the documentation must not contradict.

### Prior phases (do not re-litigate)

- `.planning/phases/54-one-bundle-rule-template-key-per-document-selection-four-del/54-CONTEXT.md` —
  D-01…D-14. Load-bearing here: **D-14** (the shadow route is `<srcdir>/_typst/base.typ`; already
  reflected at `templates.rst:213` and `configuration.rst:325`), **D-09** (the three CONF-19 message
  contents DOC-17 must agree with), **D-01** (no deletion under `outdir` — a stale file from a
  previous bundle can linger on an incremental rebuild; do not document cleanup that does not
  happen). Its **§ Specific Ideas** carries the explicit hand-off to this phase: `-b typst` output is
  no longer self-contained for a hand-run compile, and needs `--root build/typst`.
- `.planning/phases/54.1-bundle-directory-safety-templates-path-collision-refusal-and/54.1-CONTEXT.md` —
  **D-01** (the `templates_path` collision is a refusal, not a warning), **D-08/D-12** (the policed
  documentation scope is exactly `docs/source/` + `README.md` + `examples/`; `tests/` is deliberately
  not policed, with the measured reason), **D-10** (`_typst/` is the replacement directory name
  everywhere; not re-opened), **D-13** (a discovery-time re-grep found a hit the written floor
  missed — the precedent for how this phase's sweep must be run).
- `.planning/phases/53-template-registry-foundation/53-CONTEXT.md` — D-04 (only the literal `"typst"`
  is reserved; `"Typst"` is an ordinary user key) and D-07/D-08 (CONF-17's predicate).
- `.planning/phases/53-template-registry-foundation/deferred-items.md` — the pre-existing
  `tests/test_state_guard_shapes_gate.py` failure (7 tests reading an archived `.planning/` path).
  It predates Phase 53, is still open, and will surface in this phase's full-suite gate. It is **not**
  a regression this phase caused.

### Documentation pages this phase edits

- `docs/source/user_guide/configuration.rst` (390 lines) — element [4] at `:80`; the "Template
  Configuration" section at `:88-140` with its four existing subsections; "Template Assets" at
  `:131-139` (already bundle-correct, written in Phase 54); the shadow-route mention at `:325`.
- `docs/source/user_guide/output_layout.rst` (168 lines) — `:34`, `:119`, `:140`, `:159`; the
  "Which File to Compile" section at `:38-53` where D-03 puts the `--root` note.
- `docs/source/user_guide/templates.rst` (447 lines) — "Template Assets" at `:79-118`, including the
  closing note at `:114-118`; the shadow-route mention at `:213`.
- `docs/source/user_guide/builders.rst` (203 lines) — the file-count paragraph at `:122-130`.
- `docs/source/examples/advanced.rst` (427 lines) — the `refs.bib` note at `:122-131`.
- `docs/source/quickstart.rst`, `docs/source/examples/basic.rst`, `README.md`,
  `examples/basic/README.md:38`, `examples/advanced/README.md:20,22,65` — sweep surface.
- `docs/source/changelog.rst` — historical release notes; see the DOC-17 recommendation above before
  editing anything here.

### Source of truth in code (the docs must match these, not the reverse)

- `typsphinx/template_registry.py:38` `RESERVED_REGISTRY_KEY`; `:137-210` `_violates_conf17()`;
  `:303`, `:438`, `:513`, `:523` — four of the nine `ExtensionError` shapes.
- `typsphinx/builder.py:950`, `:1312`, `:1992`, `:2002`, `:2174` — the other five shapes.
- `typsphinx/removed_config.py:36-57` — `REMOVED_CONFIG_VALUES`, the three CONF-19 warning strings
  DOC-17's guidance must agree with; `:92` is the bare `logger.warning(message)` call (no
  `type`/`subtype`, so it is not individually suppressible — do not document a `suppress_warnings`
  route that does not exist).
- `typsphinx/template_engine.py:20-38` — `TEMPLATE_SEARCH_SUBDIR`'s docstring, which already states
  the `_templates/` hazard in the words the docs should echo.
- `typsphinx/pdf.py:143` — `typst.compile(typ_path, root=root_dir)`, the reason `typstpdf` is
  unaffected by the root-absolute import while a hand-run `typst compile` is not.

### Test precedents for the two new doc gates

- `tests/test_docs_contract_claims_gate.py` — prose↔code-predicate agreement, run-time page
  discovery, never skips. The model for D-06.
- `tests/test_output_layout_docs_gate.py` — real `sphinx-build` file-set assertions plus a
  prose-binding class; `test_three_master_project_emits_ten_typ_files` (`:351`) is already updated to
  the bundle layout while the page it names is not. Its docstring records why it carries no
  `typst-py` guard.
- `tests/test_quickstart_docs_gate.py` — the README + page ↔ real-build binding shape.
- `tests/test_docs_template_layout_gate.py` — the repo-wide-grep presence gate and its line-scoped
  `templates_path` exemption rule (D-08 must satisfy it).
- `tests/test_user_template_relative_asset_gate.py` and
  `tests/fixtures/user_template_relative_asset_gate/` (`conf.py`, `index.rst`, `_typst/branded.typ`,
  `_typst/logo.png`) — the fixture the DOC-16 recommendation extends.
- `tests/test_registry_prewrite_validation_gate.py`, `tests/test_template_prefix_reservation_gate.py`,
  `tests/test_removed_config_deprecation_gate.py` — existing runtime reproduction of the error shapes;
  D-06 deliberately does not duplicate them.

### Project conventions

- `CLAUDE.md` § "Worktree-isolated execution" — mandatory per-worktree
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, then everything through
  `uv run`. Worktree isolation is the standing execution mode, including for a docs-only phase.
- `CLAUDE.md` § "The `@preview` version-sync hazard" — three lockstep sites; this phase must not add
  a fourth by quoting a version into a doc page in a way a sync test would have to police.
- `CLAUDE.md` § Commands — `tox -e docs-html` and `tox -e docs-pdf` must both stay green (SC#4).
  `docs-pdf` dogfoods the `typstpdf` builder, so a doc edit that breaks the extension's own build
  fails here.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`tests/test_docs_contract_claims_gate.py`'s discovery pattern** — run-time `rglob` over
  `docs/source/**/*.rst` with an explicitly enumerated, justified exclusion set, plus a
  "patterns have teeth" self-test that proves the detector fires on a known-bad sentence. D-06's gate
  copies this whole shape; without the teeth test a doc gate can pass vacuously.
- **`tests/fixtures/user_template_relative_asset_gate/`** — a real `-b typstpdf` bundle-relocation
  fixture with a user template and a relative asset already in place. The DOC-16 recommendation adds
  one file to it rather than authoring a new project.
- **`typsphinx/removed_config.py`'s `REMOVED_CONFIG_VALUES` dict** — a single, importable source for
  the three warning strings, which makes DOC-17's "matching what CONF-19's warning says" a real
  assertion instead of a review opinion.
- **`test_output_layout_docs_gate.py`'s `_run_sphinx_build` helper** — this repository's per-module
  convention is to copy that helper near-verbatim rather than share it (stated in
  `test_removed_config_deprecation_gate.py`'s own docstring). Follow the convention.

### Established Patterns

- **Doc gates never skip.** The two existing prose-binding classes deliberately avoid `typst-py`
  import guards, because that guard tests importability rather than compile capability and would let
  the gate silently vanish in this sandbox.
- **Discovery is run-time, file lists are floors.** Every "anywhere under X" criterion in this
  milestone is verified by a repo-wide grep at discovery time; 54.1's D-13 recorded a live example of
  a written floor missing a hit.
- **Aggregated errors accumulate then raise once, `sorted()` for byte-identical messages.** The
  catalogue's row-per-shape structure (D-05) mirrors how the code actually groups failures.
- **Warnings carry no `type`/`subtype`.** Nothing in this extension is individually suppressible via
  `suppress_warnings`; documentation must not imply otherwise.

### Integration Points

1. `docs/source/user_guide/configuration.rst` — the new registry subsection, the key-naming
   subsection, the error table, the "Removed configuration values" subsection, and the element [4]
   rewrite.
2. `docs/source/user_guide/output_layout.rst` — the `_template/<key>/` layout, the corrected
   file-count rule, and the `--root` note.
3. `docs/source/user_guide/templates.rst` / `docs/source/examples/advanced.rst` — DOC-16's two asset
   examples.
4. `docs/source/user_guide/builders.rst`, `docs/source/quickstart.rst`,
   `docs/source/examples/basic.rst`, `README.md`, `examples/**/README.md` — the SC#4 sweep surface.
5. `tests/` — two new doc-gate modules (D-06's catalogue gate; DOC-16's example-binding assertions),
   plus one file added to `tests/fixtures/user_template_relative_asset_gate/`.
6. `tox -e docs-html` and `tox -e docs-pdf` — the build gate SC#4 names.

</code_context>

<specifics>
## Specific Ideas

- The owner's consistent preference across this discussion was **minimum published surface, maximum
  machine-checking**: one page for the registry (D-01), one line changed for element [4] (D-02), the
  error catalogue quoting leading clauses only (D-05) — but every one of those choices paired with a
  test that fails when the code and the page drift apart (D-06). Do not trade a gate away to shorten
  a plan.
- **The error table is a lookup surface; the key-naming rules are a writing surface.** D-07 splits
  them for that reason. A reader choosing a registry key must not have to read an error table to
  learn what characters are allowed.
- **`typstpdf` is unaffected by the root-absolute import; a hand-run `typst compile` is not.** The
  `--root build/typst` note (D-03) exists because `pdf.py:143` already passes `root=outdir` for every
  compile this project performs, so the breakage is invisible to anyone who only uses the builders —
  which is exactly why it has to be written down.
- **The prose is behind a test that already moved.** `test_three_master_project_emits_ten_typ_files`
  asserts nine root-level files today while `output_layout.rst:159` still publishes ten. Treat that
  as the phase's proof that eyeball review does not hold this doc set, and as the concrete shape the
  new gates must prevent recurring.

</specifics>

<deferred>
## Deferred Ideas

- **Phase 57 — CHANGELOG curation.** The `## [Unreleased]` section currently carries entries for the
  shadow-route relocation and the pre-write validation refusals, but **none** for
  `typst_document_templates` itself, the `_template.typ` → `_template/<key>/` output-layout change,
  or the `typst_template_assets` removal (WR-02). All of that is Phase 57's authoring/curation work,
  not this phase's.
- **Later milestone — a runnable `examples/` project demonstrating the registry.** Considered and not
  folded: DOC-15/16/17 do not ask for a new example project, and adding one is a new capability with
  its own maintenance and CI cost. `examples/**` is in this phase only as sweep surface.
- **Later milestone — `sphinx-build -b linkcheck` in CI.** A pending todo, adjacent to this phase's
  subject matter but not part of it.
- **Later milestone — documenting stale-bundle behaviour on incremental rebuilds.** Phase 54's D-01
  accepts that a file removed from a source bundle can linger at the destination. Whether that
  deserves a published caveat is a real question; it is not one of this phase's three requirements.

### Reviewed Todos (not folded)

`todo.match-phase 56` returned seven matches. **None folded** — this phase changes no production
code, and every match is either an assigned defect in another phase or a toolchain item.

- `2026-08-16-escapes-outdir-isabs-not-backslash-normalized.md` (0.9) — builder path predicate; a
  code defect, not documentation.
- `2026-08-16-track-image-escape-branch-basename-not-normalized.md` (0.9) — same class.
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` (0.6) — CI work, deferred above.
- `2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` (0.6) — release tooling, Phase 46.
- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` (0.6) — toolchain, not phase work.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` (0.6) —
  translator defect, not documentation.
- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` (0.2) — forbidden by `CLAUDE.md`
  until its own todo lands.

</deferred>

---

*Phase: 56-per-document-template-documentation*
*Context gathered: 2026-08-16*
