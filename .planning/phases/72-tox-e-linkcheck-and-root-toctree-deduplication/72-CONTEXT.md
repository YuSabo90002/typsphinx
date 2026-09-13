# Phase 72: `tox -e linkcheck` and Root Toctree Deduplication - Context

**Gathered:** 2026-09-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Two changes to this project's own documentation, and nothing the builders emit.
- **QUA-13:** add a `[testenv:linkcheck]` tox environment, shaped like `docs-html`.
- **DOC-24:** name `tox -e linkcheck` on every surface that lists the tox environments.
- **DOC-18:** remove the five duplicate child entries from the root `docs/source/index.rst`
  toctrees, so each User Guide and Examples page appears once in the HTML sidebar, nested under
  its section.

**The ROADMAP already binds almost everything about this phase.** That covers the in-phase ordering
(QUA-13 before DOC-24, DOC-18 independent, base builds first, evidence last), constraints 1–13 and
SC#1..SC#5. None of it is re-decided here. This discussion settled only four things the ROADMAP left
open:
- what happens when linkcheck reports a non-`working` link at execution time;
- how the DOC-24 line reads;
- what happens to the 2026-07-22 linkcheck todo;
- how the UI-gate false positive is handled.

The owner accepted the recommended option for all four.

**Measured at discussion time (2026-09-13, main checkout, Sphinx 9.1.0, HEAD `34fe03b4`).** These
figures are context only. Constraint 8 still requires the executing plan to re-measure fresh.
- **Command:** `LC_ALL=C .venv/bin/sphinx-build -q -b linkcheck docs/source <scratch>/linkcheck`,
  run on an empty output directory.
- **Result:** exit 0 in about 10 s. `output.json` holds 95 entries, **all** `working`, with no
  `redirected`, `ignored`, `timeout` or `broken` entry.
- **Anchors:** 41 of the 95 URIs carry a `#anchor`: `www.sphinx-doc.org` 23, `docs.python.org`
  17, `pypi.org` 1.
- **Sources:** `changelog.rst` (that is, `CHANGELOG.md`) 50, `api/…` 40, `contributing.rst` 2,
  `examples/…` 2, `index.rst` 1.
- **Why the 40 `api/…` entries matter:** they come from autodoc docstrings under `typsphinx/`, which
  constraint 2 forbids editing in this milestone.
- **`docs/source/conf.py` today:** no `linkcheck_*` key at all.
- **`git grep -n 'tox -e docs-pdf' -- ':!.planning'`:** the same five hits constraint 11 lists.
  They are `.github/workflows/docs.yml:36`, `CHANGELOG.md:921`, `CLAUDE.md:33`, `README.md:262` and
  `docs/source/contributing.rst:124`.

**Sphinx behaviour measured in `sphinx/builders/linkcheck.py` (Sphinx 9.1.0).** It drives D-04.
- **`output.json`:** `write_linkstat()` writes a row to `output.json` for **every** result,
  whatever its status. A URL matched by `linkcheck_ignore` therefore appears as `ignored`, and SC#1's
  "total equals `working`" fails for it.
- **HTTP 503:** it is reported as `ignored` ("service unavailable") with no configuration involved.
- **HTTP 429:** it is re-queued as `rate-limited`, or reported `broken` once
  `linkcheck_rate_limit_timeout` runs out.
- **Timeouts and redirects:** they are written as `timeout` and `redirected …` but do not make the
  exit status non-zero. Only `broken` does. So exit 0 alone does not satisfy SC#1; the `output.json`
  status census is the binding half.

</domain>

<decisions>
## Implementation Decisions

### QUA-13 — what happens when linkcheck reports a link that is not `working`

- **D-01 — A transient failure is re-run from a clean output directory, never read around.** In this decision, a
  *transient* status means one of the following in `output.json`:
  - `timeout`;
  - `ignored` with info `service unavailable` (HTTP 503);
  - `rate-limited`;
  - `broken` whose info is a connection-level exception rather than an HTTP status (for example
    a reset, DNS or TLS error).

  On a transient status the executor removes `docs/_build/linkcheck` and runs `tox -e linkcheck`
  again. It stops after **three runs in total**. Every run is transcribed: its exit code, the status
  census from `output.json`, and each non-`working` row verbatim. A run counts as the pass only if
  it meets SC#1 in full on its own: exit 0, and every `output.json` entry `working`. An earlier failed
  run is never deleted from the evidence.

- **D-02 — A timing key is allowed only for a transient failure that recurs on the same URL across runs.** If the same URL fails
  transiently in two or more of D-01's runs, the executor may add exactly the key that addresses it
  to `docs/source/conf.py`: `linkcheck_timeout`, `linkcheck_retries` or
  `linkcheck_rate_limit_timeout`. The key carries a comment naming the URL, the status and the run
  numbers that showed it, as SC#1 requires. It is then followed by a fresh clean run that meets SC#1.
  No key is added on a single observation. No key is added speculatively.

- **D-03 — Anything that is not transient stops the phase and goes to the owner.** That covers these cases:
  - `broken` with an HTTP status (404, 410, and so on);
  - any `redirected` entry;
  - an anchor reported missing;
  - any case where passing would take `linkcheck_ignore`, `linkcheck_anchors_ignore`,
    `linkcheck_anchors_ignore_for_url`, `linkcheck_allowed_redirects` or any other key that turns a
    row into something other than `working`.

  The executor does not edit the link, and it does not add a key. It records the URL and where the
  URL comes from. The source is either (i) an editable docs source, meaning a `docs/source/**.rst`
  file or `CHANGELOG.md` through `changelog.rst`, or (ii) an autodoc docstring under `typsphinx/`,
  which constraint 2 makes unfixable in this milestone. The owner decides from there.

- **D-04 [informational] — SC#1 is read literally and is not amended.** "Every `output.json` entry has status `working`, and the
  total equals the `working` count" stays the pass condition. D-02's timing keys are compatible with
  it, because they make a flaky link come back `working`. The ignore-style keys D-03 names are not
  compatible with it: Sphinx writes their rows as `ignored`. That is why they route to the owner
  instead of into the diff.

### DOC-24 — the line added to each listing surface

- **D-05 — The new line goes last in each tox block, and its comment says the environment needs the network and is not part of a plain tox run.** The placement differs by surface:
  - `CLAUDE.md` § Commands: after `tox -e docs-pdf`.
  - `README.md`'s development block and `docs/source/contributing.rst`'s "Using Tox" block: after
    the `… tox -e docs` line.

  In each case it uses the prefix the neighbouring lines use (SC#2): `tox -e linkcheck` in
  `CLAUDE.md`, `uv run tox -e linkcheck` in the other two. Its `#` comment starts in the same column
  as the neighbours. Reference wording is
  `# Check external links and anchors (needs network; not run by plain tox)`. The exact text is at
  discretion, but it must say both that the network is needed and that plain `tox` does not run it.

- **D-06 — Nothing else on those surfaces changes.** Every existing line in each block stays byte-identical. That
  includes `contributing.rst`'s `# Run all tox environments (tests, lint, type check, docs)` comment
  and `CLAUDE.md`'s `tox  # env_list: py312, py313, lint, type, cov, docs` comment. Both stay true,
  because `linkcheck` is not in `env_list`. No prose sentence or paragraph about linkcheck is added to
  any surface. Every other grep hit gets a recorded disposition per SC#2, and that includes
  `docs.yml:36` and `CHANGELOG.md:921`.

### Todos

- **D-07 — The 2026-07-22 linkcheck todo stays in `todos/pending/` and gains a status note.** The note is appended after QUA-13's
  environment has landed, so that it is true when written. It records three things: the
  `[testenv:linkcheck]` environment the todo's first Solution bullet asks for now exists (Phase 72,
  QUA-13); the part still open is the CI job, which is **QUA-08** and a Future requirement; and a
  future pickup must plan a side PR to `main`, per ROADMAP constraint 4. The todo's existing text and
  frontmatter are otherwise left as they are. It is not moved to `completed/`, and no new todo is
  filed for QUA-08.

- **D-08 — The 2026-08-16 root-toctree todo is folded into DOC-18 and moves to `todos/completed/` in the same commit as the `index.rst` edit.** Its
  `resolves_phase` is already 72. Its "PDF is not affected" section and its `examples/basic`
  parent-divergence observation feed SC#4 directly (see Folded Todos).

### Process

- **D-09 — The UI-gate false positive is handled with `--skip-ui` at plan time. No UI hint line is added to the ROADMAP.** This is the owner's call
  that constraint 13 left open. `/gsd-plan-phase 72` is invoked with `--skip-ui`. `.planning/ROADMAP.md`
  gains no UI hint line for Phase 72, which keeps the roadmapper's orchestrator instruction intact.

### Claude's Discretion

- The exact comment text of the DOC-24 line, within D-05.
- The `description =` text of `[testenv:linkcheck]`. The section's other keys are fixed by SC#1
  (`runner`, `extras`, `changedir`, `commands`). Whether it copies `docs-html`'s other attributes
  is also discretionary, as long as `tox.ini`'s diff only adds lines.
- The plan split and wave shape within the ROADMAP's binding ordering.
- The evidence file names and layout. By this project's convention, evidence is verbatim
  transcripts in phase markdown, with no new committed script and no new test.
  `72-VERIFICATION.md` is reserved for the verifier and must not be authored by a plan.
- How the `PHASE_BASE_SHA` builds are materialised: a second worktree, or `git archive` into
  scratch.
- How SC#4's sidebar link count is taken from the markup, as long as it is a count over
  `index.html`'s sidebar navigation and not a reading of prose.

### Folded Todos

- **`2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md`** — DOC-18's own todo.
  The problem: the root `index.rst` lists section indexes **and** their children, so the sidebar
  shows five pages twice, and Sphinx reports `document is referenced in multiple toctrees` (4 on
  2026-08-16, 5 on 2026-09-13). Its measured PDF analysis is carried as-is: the Typst side is
  already deduplicated by the include-edge state guard, and the root `index.typ`'s dead guarded
  `include()` lines are what disappear. So is its warning that Sphinx picked different parents
  (`index` for `examples/basic`, section indexes for the rest). Folded in full. It moves per D-08.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase contract
- `.planning/ROADMAP.md` § "🚧 v0.9.5 — Docs Link Check and Navigation (ACTIVE)": binding constraints
  1–13. The ones that matter most here are 2 (zero `typsphinx/` lines), 3 (no workflow edits,
  required checks), 6 (branch census, decoy, first push, CI dispatch), 7 (clean builds, `LC_ALL=C`,
  positive control), 8 (fresh counts), 11 (DOC-24 grep) and 12 (worktree isolation, `docs` extra).
- `.planning/ROADMAP.md` § "Phase 72": the goal, the binding in-phase ordering, and SC#1..SC#5.
- `.planning/REQUIREMENTS.md`: QUA-13, DOC-18 and DOC-24 verbatim, and the Out of Scope table
  (which includes the `examples/basic` divergence row).

### Todos
- `.planning/todos/pending/2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md`:
  the folded DOC-18 todo (D-08).
- `.planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md`: the QUA-08 todo that gains
  D-07's status note.

### Files edited
- `tox.ini:67-73`: `[testenv:docs-html]`, the shape QUA-13 copies. `:2` is `env_list` and `:4-17`
  is the `requires` pin and its comment; both stay untouched.
- `docs/source/index.rst:38-53`: the User Guide and Examples toctrees. The lines removed are
  `:43-45` and `:52-53`.
- `CLAUDE.md:30-33`, `README.md:255-264` and `docs/source/contributing.rst:112-126`: the three
  listing blocks DOC-24 edits.
- `docs/source/conf.py`: gains a `linkcheck_*` key only under D-02.

### Files read, not edited
- `docs/source/user_guide/index.rst:6-12` and `docs/source/examples/index.rst:6-10`: the toctrees
  that own the five pages. They must be absent from the diff.
- `.github/workflows/docs.yml:36` and `CHANGELOG.md:921`: grep hits that need a recorded
  disposition, not an edit.
- `sphinx/builders/linkcheck.py` in the installed Sphinx 9.1.0: `write_linkstat()` and the
  status-match block (about `:120-210`), and the 429/503 handling (about `:600-620`). This is the
  source of D-04's facts.

### Prior art
- `.planning/milestones/v0.9.4-phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONTEXT.md`:
  the D-09 clean base/after docs-build pattern with a control, and the evidence conventions.
- `.planning/milestones/v0.9.4-phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CI-EVIDENCE.md`:
  the shape of the CI-dispatch evidence SC#5 reuses.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `[testenv:docs-html]` in `tox.ini` is the template: `runner = uv-venv-lock-runner`,
  `extras = docs`, `changedir = docs`, then one `sphinx-build` command. The new section differs in
  the builder (`-b linkcheck`) and the output directory (`_build/linkcheck`).
- The `docs` extra already installs Sphinx and furo. `linkcheck` is built into Sphinx, so no
  `pyproject.toml` change is expected (constraint 2).

### Established Patterns
- In all three listing blocks the `#` comments are column-aligned. `README.md` and
  `contributing.rst` pad `uv run tox -e <env>` to one comment column; `CLAUDE.md` pads
  `tox -e <env>` to its own column.
- The `docs/_build/` output directories are the tox environments' own (`changedir = docs`). Clean
  builds for comparison remove the specific output directory first (constraint 7).

### Integration Points
- `docs/source/changelog.rst` includes `CHANGELOG.md`, which is why 50 of the 95 checked links come
  from the changelog. Phase 73's REL-14 bullets will add to that set later. This phase does not touch
  `CHANGELOG.md`.
- `Lint and Format Check` in `ci.yml` runs lint through tox, so SC#5's dispatched CI run also
  exercises the edited `tox.ini` on the runner.

</code_context>

<specifics>
## Specific Ideas

- The linkcheck run is fast, about 10 s at discussion time. D-01's three-run ceiling therefore costs
  little, and the planner need not budget for a long network step.
- Sphinx reports the HTML "multiple toctrees" message but does not count it as a warning. SC#3's two
  numbers are independent, and each needs its own `LC_ALL=C` grep with the positive control on the
  base build.

</specifics>

<deferred>
## Deferred Ideas

None came up in discussion; it stayed within the phase scope.

### Reviewed Todos (not folded)
- `2026-07-22-add-sphinx-linkcheck-ci-job.md`: QUA-08, a Future requirement. It needs a workflow
  file, which constraint 3 forbids. It stays pending, with D-07's status note.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`: NUM-01.
  It edits `typsphinx/` (constraint 2).
- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md`: MSG-06.
  It edits `typsphinx/` (constraint 2).
- `2026-09-13-doctest-block-unhandled-collapses-examples-to-one-line.md`: TRN-01. It edits
  `typsphinx/` and changes output (constraint 2).

</deferred>

---

*Phase: 72-tox-e-linkcheck-and-root-toctree-deduplication*
*Context gathered: 2026-09-13*
