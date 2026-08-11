# Phase 44: `typst_documents` Default Derivation + Builder Input Hardening - Context

**Gathered:** 2026-08-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Make `typst_documents` resolve to a Sphinx-native derived default when the user never sets it, so
that following the Quick Start exactly produces a PDF instead of zero output — and harden the one
method that resolution flows through against a non-`str` docname.

Two requirements:

- **CONF-08** — with `typst_documents` unset, `sphinx-build -b typstpdf` produces a PDF. The default
  is derived from `root_doc` / `project` / `author`, with the target name in Sphinx's own LaTeX
  shape (`make_filename_from_project(project)` → `<project>.typ`). An explicitly-set
  `typst_documents` always wins.
- **BLD-01** — a non-`str` docname reaching `TypstPDFBuilder.finish()` fails with an actionable
  typsphinx-level error rather than a raw `TypeError` out of `posixpath.dirname()`.

Already locked before this discussion (ROADMAP.md §"Phase 44", REQUIREMENTS.md CONF-08, and the
REQUIREMENTS.md "Out of Scope" table):

- The LaTeX-consistent `<project>.typ` shape is chosen over the rename-free `<root_doc>.typ` shape.
- The resulting output-filename rename is an accepted cost; v0.7.1 is **not** bumped to v0.8.0 to
  absorb it. Framing accepted by the owner: the renamed path produced no PDF at all before, so it is
  a broken path being repaired rather than a working one being changed.
- The measured before/after filename pair is handed to Phase 46 as CHANGELOG source text.

Not in this phase: wiring `typst_documents` entry elements `[2]` (title) / `[3]` (author) into the
rendered output (deferred — see Deferred Ideas), the toctree heading-depth work (Phase 44.1), and
the README/`configuration.rst` documentation of the new default (DOC-11, Phase 45).
</domain>

<decisions>
## Implementation Decisions

### The derived default — shape and degenerate inputs

- **D-01: A degenerate `project` name keeps Sphinx's `'sphinx'` sentinel verbatim.** No typsphinx-side
  fallback, no extra warning, no branch. Measured 2026-08-04 (Sphinx 9.1.0):
  `make_filename_from_project()` (1) removes a trailing `' Documentation'`, (2) deletes every
  character matching `[^a-zA-Z0-9_-]` (`_no_fn_re`), (3) lowercases, (4) returns `'sphinx'` if the
  result is empty. So `project='日本語 プロジェクト'` → `'sphinx'`, `project='Проект'` → `'sphinx'`,
  `project=''` → `'sphinx'`, `project='ドキュメント v1'` → `'v1'`, `project='MyApp Documentation'`
  → `'myapp'`, `project='My Cool Project'` → `'mycoolproject'`. A project with a non-ASCII name gets
  `sphinx.typ` / `sphinx.pdf` — exactly as it already gets `sphinx.tex` from `-b latex` today. Users
  who want another name set `typst_documents` explicitly, which always wins (SC#2).
  — **Reversibility:** reversible — adding a fallback branch later is local to the derivation function.

- **D-02: The derived entry is a 5-tuple in LaTeX's shape.** The wiring of explicit `[2]`/`[3]` is
  deferred to a todo.

  > **⚠ SUPERSEDED 2026-08-04 — the deferral was reversed, this decision's *shape* half still
  > stands.** Owner decision taken after Phase 45.1 was created: the missing consumption is now
  > **in** v0.7.1 as **Phase 44.2 / CONF-09**, not outside it. What changed: `templates.rst:189`
  > tells readers `title` comes "from `typst_documents`", which is false while the wiring is
  > missing, so Phase 45.1's SC#2 (published contract and behaviour agree both ways) would have had
  > to document the gap rather than close it. The patch-release cost this decision weighed is
  > accepted rather than avoided: v0.7.1 now ships two user-visible changes, and Phase 46's
  > CHANGELOG must call out both. Everything below about the derived entry's *shape* — what Phase 44
  > actually built — is unchanged and still accurate. See `ROADMAP.md` §Roadmap Evolution,
  > 2026-08-04, "Phase 44.2 inserted".

  Derived value:
  `[(config.root_doc, make_filename_from_project(config.project) + ".typ", config.project, config.author, "typst")]`.
  The trailing `.typ` is included because `default_latex_documents` includes `.tex`;
  `_resolve_output_stem` strips a literal trailing `.typ` already (builder.py:180), so both forms
  work and LaTeX-consistency decides it.

  Measured during this discussion, in both directions:
  - typsphinx reads **only** `entry[0]` and `entry[1]` — `writer.py:68`, `builder.py:118`,
    `builder.py:165-166`, `builder.py:928` are the complete set of indexed accesses. `[2]` title,
    `[3]` author and `[4]` class are documented in
    `docs/source/user_guide/configuration.rst` but referenced by nothing; title/author actually come
    from `config.project` / `config.author` / `typst_authors` via `template_engine.py`.
  - Sphinx's LaTeX builder **does** read them: `LaTeXBuilder.write_documents()` destructures
    `docname, targetname, title, author, themename = entry[:5]` and feeds
    `update_doc_context(title, author, theme)` plus `docsettings._title` / `docsettings._author`;
    `init_document_data()` also keeps `entry[2]` in `self.titles`. So in LaTeX an explicit entry's
    title/author **override** `config.project` / `config.author`.

  Owner decision: match LaTeX's **shape** here, and file the missing **consumption** as its own item
  rather than adding a second user-visible behaviour change to a patch release. Blast radius measured
  for whoever picks it up: of 104 `typst_documents` entries in the repo, only **5** have
  `entry[2] != project`.
  — **Reversibility:** reversible — the arity is one literal in one function; the deferral is a todo
  file, not a code change.

### Opt-out semantics

- **D-03: An explicit `typst_documents = []` stays an opt-out.** The `WARNING` is kept at `WARNING`
  severity and only its wording is corrected. Once the derived default lands, unset can never be
  empty (verified: with a callable default, `config.typst_documents` returns the derived list when
  unset and `[]` when the user wrote `[]`), so the existing message at `builder.py:907-909` —
  `"No documents defined in typst_documents. Nothing to compile."` — is only reachable via an
  explicit empty list, where it reads as if the setting were absent. New wording must say the setting
  is present and empty, and that removing it restores the derived default. Severity stays `WARNING`
  so `-W` builds keep failing, matching Sphinx's LaTeX builder, which emits
  `no "latex_documents" config value found; no documents will be written` at `WARNING` in the
  equivalent situation.
  — **Reversibility:** reversible — message text and log level.

- **D-04: The default is registered as a Sphinx callable default, exactly as `latex_documents` is.**
  `app.add_config_value("typst_documents", <derivation callable>, "html", [list])` in
  `typsphinx/__init__.py:44`. Verified live 2026-08-04 with that exact signature: type validation
  accepts a callable default, an unset project yields the derived list, and an explicit `[]` yields
  `[]`. Every existing reader then sees the same resolved value with no further change —
  `writer.py:55` `_is_master_document`, `builder.py:117` `_compute_master_included_docnames`,
  `builder.py:160` `_resolve_output_stem`, `builder.py:904` `finish`. Rejected: a `config-inited`
  handler that materializes the value (adds a handler + priority to manage, diverges from LaTeX), and
  a builder-local helper (leaves `config.typst_documents` empty, and missing one of the four call
  sites would silently desynchronize the writer's untemplated `index.typ` from `finish()`'s lookup of
  `<project>.typ`).
  — **Reversibility:** reversible pre-release — one registration line. The **rename it causes** is the
  milestone-level accepted cost already recorded in REQUIREMENTS.md, not a new decision here.

### The user-visible-change record (SC#4)

- **D-05: The before/after record covers the filename AND the content change.** Measured 2026-08-04
  on a real build of a minimal project with `project = 'My Cool Project'` and no `typst_documents`:
  `sphinx-build -b typstpdf` exits 0, emits exactly one `WARNING`, writes **zero PDFs**, and writes
  `out/index.typ` at **373 bytes** — `@preview` imports plus body only, with **no template applied**,
  because `_is_master_document('index')` is False. (That file does still compile standalone:
  `typst.compile()` on it produced an 8209-byte PDF.) After the change the same project emits
  `mycoolproject.typ` + `mycoolproject.pdf` **with the full template applied**, because the derived
  entry makes `index` a master.

  So the change is not only a rename: the emitted `.typ`'s structure changes too. Both facts go into
  the SC#4 evidence and into the source text handed to Phase 46, so the CHANGELOG can explain how an
  existing unset-config user who `#include`s the old `index.typ` from their own Typst file is
  affected.
  — **Reversibility:** reversible — it widens what the evidence file records, nothing else.

### Claude's Discretion

Deliberately left to research/planning — the owner did not select these, so nothing is locked and the
planner should choose on measured grounds:

- **BLD-01's error shape and validation width.** Measured path: `finish()` (builder.py:930) calls
  `self._directory_preserving_relpath(docname, stem)`, which reaches `posixpath.dirname(docname)`
  (builder.py:270) and raises a raw `TypeError`. That call sits **before** the `try:` block
  (builder.py:946) that aggregates into `failures`, so the whole build dies with a bare traceback.
  Note `_resolve_output_stem(docname)` itself tolerates a non-`str` docname — it only does `==`
  comparisons — so the crash point is specifically `_directory_preserving_relpath`. Open: (a) collect
  into the existing `failures` list and report through the single end-of-loop `ExtensionError`
  (consistent with the WR-01 aggregate design, and other masters still compile) versus raise
  immediately; (b) validate only "docname is not `str`" (the todo's exact scope) versus broader
  `typst_documents` entry-shape validation — the latter plus a `difflib` "did you mean" suggestion
  were both explicitly deferred in Phase 22.3's `<deferred>` and should not be widened into by
  accident.
- **Which existing tests are updated and how** (SC#5 requires each change be traceable to this
  requirement rather than absorbed silently). Measured starting point: **all 103** `conf.py` files in
  the repo that mention `typst_documents` already set it, so no existing fixture's output filename
  changes. `tests/test_config.py:6-19` asserts only that the config value exists and is a `list` —
  both still hold under a callable default. A new fixture is needed to exercise the unset path at all.
- **Where the SC#4 evidence file lives and what it is named** (a `44-GATE-EVIDENCE-*.md` in the phase
  directory is the established shape).
- **Whether `-b typst` alone should warn on an explicit empty list.** Today the "nothing to compile"
  warning lives only in `TypstPDFBuilder.finish()`; a plain `-b typst` build with an empty list emits
  nothing and silently writes untemplated files. D-03 decided the message for the `typstpdf` path
  only.

### Folded Todos

- `.planning/todos/pending/2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md` → **BLD-01**
  (`resolves_phase: 44`). Carries the verified traceback and call chain, the reason Phase 22.3's D-06
  scoped it out, and the note that this defect is loud (non-zero exit, full traceback) rather than
  silent — so it is a diagnostic-quality problem, not a WR-01 regression.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap
- `.planning/REQUIREMENTS.md` — CONF-08 (incl. the "known accepted cost" clause) and BLD-01; the
  "Out of Scope" rows that reject a v0.8.0 bump and the `<root_doc>.typ` shape; the traceability
  table (CONF-08 / BLD-01 → Phase 44).
- `.planning/ROADMAP.md` §"Phase 44" — SC#1-#5, and §"Phase 44.1" for what is deliberately **not**
  here (TOC-01 runs after this phase so its heading-shape change cannot contaminate SC#4's measured
  before/after pair).

### Source todo
- `.planning/todos/pending/2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md` — BLD-01's
  verified traceback, call chain, and the two sibling items Phase 22.3 deferred alongside it.

### Prior-phase decisions that constrain this one
- `.planning/phases/43-table-state-correctness-nested-tables-empty-title-anchors/43-CONTEXT.md` —
  D-05 established the "follow the builder Sphinx already ships, measured on identical input"
  method that CONF-08 originated and this phase reuses throughout.
- `.planning/milestones/v0.7.0-phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-05.md`
  — the two-build byte-invariance method (`git archive` an old tree, assert `typsphinx.__file__`
  resolves into it, plus a positive control) if a byte-comparison is used for the SC#4 evidence.

### Code under change
- `typsphinx/__init__.py:44` — the `add_config_value("typst_documents", [], "html", [list])`
  registration D-04 replaces.
- `typsphinx/builder.py` — `_compute_master_included_docnames` L117-118, `_resolve_output_stem`
  L133-238 (target normalization, `.typ` stripping at L180, path guard L182-220),
  `_directory_preserving_relpath` L240-273 (**BLD-01's crash site is `posixpath.dirname` at L270**),
  `TypstPDFBuilder.finish` L875-967 (empty-config early return L906-910, the `if not doc_tuple` guard
  L924-927, the unguarded `_directory_preserving_relpath` call L930, the `try:` aggregation L946-961,
  the terminal `ExtensionError` L963-967).
- `typsphinx/writer.py:41-71` — `_is_master_document`, the switch that decides template-vs-included
  and therefore the content half of D-05.

### Upstream reference implementation (measured, not remembered)
- `sphinx/builders/latex/__init__.py` — `default_latex_documents()` (the callable default D-04
  mirrors), its `add_config_value('latex_documents', default_latex_documents, '', ...)` registration,
  `LaTeXBuilder.init_document_data()` (the `WARNING` D-03 mirrors), and
  `LaTeXBuilder.write_documents()` (the `entry[:5]` consumption D-02 defers).
- `sphinx/util/osutil.py` — `make_filename_from_project()` / `make_filename()` / `_no_fn_re`, the
  degradation D-01 accepts.

### Project conventions
- `CLAUDE.md` — worktree-isolated execution is the standing mode:
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, then run everything via
  `uv run`. Also: do not modernize typing imports (`UP006`/`UP035`) in this phase.
- `docs/source/user_guide/configuration.rst` — the published 5-element `typst_documents` contract and
  the "Target name" wording `_resolve_output_stem` implements.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`sphinx.util.osutil.make_filename_from_project`** — the exact function CONF-08's target-name
  shape is defined by. No typsphinx-side filename derivation needs to be written.
- **`_resolve_output_stem` / `_directory_preserving_relpath`** — the derived entry flows through the
  same normalization every explicit entry already does. Its guards are inert for a derived value
  (`make_filename_from_project` strips `/` and `\` along with everything else outside
  `[a-zA-Z0-9_-]`, and can never return an empty string), so no new guard is required for the
  derivation itself.
- **`failures: List[Tuple[str, str]]` + the terminal `ExtensionError`** in `finish()` — the existing
  aggregate-and-report mechanism BLD-01's error can join without inventing a new one.
- **`tests/fixtures/*/conf.py` (97 fixtures) + `tests/roots/test-basic`** — the established
  fixture-project pattern; a new fixture that omits `typst_documents` is the only way to exercise the
  unset path, since every existing one sets it.

### Established Patterns
- **Config registration is a flat block in `setup()`** (`__init__.py:44-60`), all using the
  `(name, default, "html", [types])` positional form. A callable default fits without changing the
  call shape.
- **One normalization rule, one place.** `_resolve_output_stem`'s docstring states it is the single
  implementation of the target-name rule and that every write/read-back site calls it rather than
  re-deriving. D-04's callable default preserves that: the derivation feeds the config, and the
  config feeds the one normalizer.
- **`get_target_uri` is deliberately NOT target-name-aware** (builder.py:287-307) — labels are
  namespaced by source docname, never by output filename. The derivation must not tempt a "fix" here;
  the docstring says so explicitly.
- **Malformed entries are guarded, never indexed blindly**, at every iteration site
  (`writer.py:67-68`, `builder.py:118`, `builder.py:165`, `builder.py:924`), each with a comment
  explaining that reporting is `finish()`'s job alone.

### Integration Points
- `typsphinx/__init__.py:setup()` — where the derivation callable is registered.
- `TypstPDFBuilder.finish()` — where BLD-01's validation lands and where the D-03 warning lives.
- `TypstWriter._is_master_document()` — unchanged in code, but its **result** changes for the unset
  case, which is the content half of D-05.
- `TypstBuilder.write_doc` / `_write_template_file` — the `-b typst` path that now also renames and
  templates.

</code_context>

<specifics>
## Specific Ideas

Everything below was measured in this session against the repo venv (Sphinx 9.1.0). It is evidence
the researcher should build on, not re-derive.

**1. The current unset-config build, end to end.** Minimal project, `conf.py` containing only
`extensions = ["typsphinx"]`, `project = "My Cool Project"`, `author = "A. Author"`, `release = "1.0"`:

- `sphinx-build -b typstpdf src out` → **exit 0**, `build succeeded, 1 warning`, warning text
  `WARNING: No documents defined in typst_documents. Nothing to compile.`
- Output tree: `out/_template.typ` and `out/index.typ`. **No PDF.**
- `out/index.typ` is **373 bytes**: the `// Essential imports for included document` header, four
  `@preview` imports, `codly-init`, then the body — **no template call**.
- That file nevertheless compiles: `typst.compile("out/index.typ", root="out")` → 8209-byte PDF.

**2. `make_filename_from_project` degradation table** (Sphinx 9.1.0, `_no_fn_re = [^a-zA-Z0-9_-]`):

| `project` | result |
|---|---|
| `typsphinx` | `typsphinx` |
| `My Cool Project` | `mycoolproject` |
| `MyApp Documentation` | `myapp` |
| `a-b_c.d` | `a-b_cd` |
| `ドキュメント v1` | `v1` |
| `日本語 プロジェクト` | `sphinx` |
| `Проект` | `sphinx` |
| `` (empty) | `sphinx` |

**3. Callable-default viability, verified with typsphinx's own registration signature.** A throwaway
extension registering `app.add_config_value("demo_documents", <callable>, "html", [list])` and
printing the value at `config-inited`:

- unset → `[('index', 'mycoolproject.typ', 'My Cool Project', 'A. Author', 'typst')]`
- `demo_documents = []` in `conf.py` → `[]`

No type-validation warning in either case. Unset and explicit-empty are therefore cleanly
distinguishable at read time, which is what D-03 depends on.

**4. LaTeX's consumption of `latex_documents`, verbatim** (`LaTeXBuilder.write_documents`):

```python
for entry in self.document_data:
    docname, targetname, title, author, themename = entry[:5]
    ...
    self.update_doc_context(title, author, theme)
    ...
    docsettings._author = author
    docsettings._title = title
```

and in `init_document_data()`: `self.titles.append((docname, entry[2]))`, plus the empty-config
warning `no "latex_documents" config value found; no documents will be written`.

**5. Repo-wide `typst_documents` census.** 103 `conf.py` files mention `typst_documents`; **all** of
them set it, so the derived default changes no existing fixture's filename. Across 104 parsed
entries, `entry[2] != project` in exactly 5 (listed in the new todo). No entry has fewer than 3
elements.

**6. The complete set of indexed accesses to a `typst_documents` entry in typsphinx:**
`writer.py:68` (`doc_tuple[0]`), `builder.py:118` (`entry[0]`), `builder.py:165-166`
(`entry[0]`, `entry[1]`), `builder.py:928` (`doc_tuple[0]`). Nothing reads `[2]`, `[3]` or `[4]`.

</specifics>

<deferred>
## Deferred Ideas

- **Wiring `typst_documents` entry `[2]` (title) / `[3]` (author) into the rendered output** —
  filed 2026-08-04 as
  `.planning/todos/pending/2026-08-04-typst-documents-title-author-elements-ignored.md`, carrying the
  measured LaTeX destructuring, the complete list of typsphinx's indexed accesses, and the 5-entry
  blast radius. Owner decision (D-02): out of v0.7.1 — it would put a second user-visible behaviour
  change into a patch release alongside CONF-08's rename.
- **Giving the 5th tuple element (`"Document class (usually 'typst')"`) an actual meaning.** Recorded
  in the same todo. This phase emits `"typst"` there for shape-consistency only.
- **Exhaustive `typst_documents` shape validation** and a **`difflib`-based "did you mean" suggestion
  for an unknown docname** — both deferred in Phase 22.3's `<deferred>` and still deferred. BLD-01's
  discretion note warns the planner not to widen into them by accident.
- **A `-b typst`-side warning for an explicit empty list.** D-03 only settled the `typstpdf` path;
  see Claude's Discretion.

### Reviewed Todos (not folded)

- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — matched on keywords only
  (`ruff`, `set`). Explicitly forbidden here by `CLAUDE.md` and by REQUIREMENTS.md's Future
  Requirements.
- `2026-08-04-toctree-heading-offset-ignored-because-visit-title-emits-abs.md` → TOC-01, Phase 44.1.
  Deliberately sequenced **after** this phase so its heading-shape change cannot contaminate SC#4's
  measured before/after pair.
- `2026-07-25-derive-typst-lang-duplicated-warning-block.md`,
  `2026-07-29-project-md-unterminated-html-comments.md`,
  `2026-08-04-docs-changelog-page-stale-at-0-4-0.md` — `resolves_phase: 45`.
- `2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` — `resolves_phase: 46`.
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` — LNK-01, future requirement, not in v0.7.1.

</deferred>

---

*Phase: 44-`typst_documents` Default Derivation + Builder Input Hardening*
*Context gathered: 2026-08-04*
