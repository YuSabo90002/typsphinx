# Phase 35: v0.6.5 Release Prep - Research

**Researched:** 2026-07-29
**Domain:** Mechanical release-prep procedure (version bump, CHANGELOG curation, test-coverage
close-out, mechanical invariant proof) — no unfamiliar library, no architectural decision.
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Structure of the `## [0.6.5]` CHANGELOG entry**

- **D-01: The `### Fixed` body uses one general sentence with representative contexts in parentheses.**
  Measured: the shape the backlog report (999.1) named — inline math immediately after text in a
  top-level paragraph, including the no-intervening-space form — was already green before the fix.
  What was actually red: bullet-list items, field bodies (`confval`'s `:type:` / `:default:`),
  definition-list terms, display math inside a list item, and a list item whose sole content is
  inline math. Write it as "inline math immediately after text (in bullet-list items, definition-list
  terms, and the like)" on one line; do not enumerate every context. **No BREAKING label** — this is
  a pure bug fix with no user whose working setup breaks.

- **D-02: Display math (a `.. math::` block inside a list item) goes in the same bullet as inline math.**
  From the user's side this is one and the same change — "math inside a list item made the build
  fail" — so it is bundled (precedent: Phase 33 D-09's granularity rule — bundle by user-visible
  change, requirement IDs in trailing parentheses). The implementation-level split between
  `visit_math` and `visit_math_block` does not surface in the CHANGELOG.

- **D-03: Two sections — a lead paragraph plus `### Fixed` and `### Verified`.** This matches
  0.6.1 / 0.6.3 / 0.6.4, all of which carry a lead paragraph and a Verified section. The lead's axis:
  the separator-omission compile abort for inline and display math is fixed, and the only runtime
  change is one site in the translator.

- **D-04: `### Verified` carries three items — the two invariants plus the full-corpus gate.**
  Zero new runtime dependencies / the four `@preview` version strings unchanged / the full-corpus
  (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run is fatal-free. Because this milestone does touch the
  translator, the Phase 23/28 corpus item is justified here (Phase 33 D-03 omitted it precisely
  because that milestone had zero `typsphinx/` changes). The GATE-01 fixture's RED→GREEN record is
  **not** listed — test machinery is not user-visible.

**Handling the four Warnings from the Phase 34 review**

- **D-05: Close only the three test-side Warnings (WR-02 / WR-03 / WR-04) in Phase 35; file WR-01 as a todo.**
  WR-02–04 are fixture and gate-test additions with zero `typsphinx/` change, so invariant #3 is
  untouched. WR-01 (`visit_math_block`'s pre-existing unconditional `"\n\n"` doubling up with the new
  `list_item_needs_separator` flag, emitting one redundant blank line) is inert in Typst but requires
  a translator change, which would force re-deriving the GATE-01 fixture's expected strings and
  re-running the full-corpus gate. We are not taking on an output-shape change immediately before a
  release.

- **D-06: Close WR-02 by adding Construct G to the existing fixture.** Add "a `:label:`-bearing
  `.. math::` inside a list item" to
  `tests/fixtures/inline_math_after_text_render_gate/index.rst` and add assertions to both the mitex
  and native tests. A separate fixture would add two more `sphinx-build` runs, so keep it consolidated
  with the existing six constructs (A–F).

- **D-07: The three test additions run as an independent plan before the version bump, and the ROADMAP
  gains no new success criterion.** Phase 35's SC#1–SC#4 say nothing about test additions, so this is
  recorded here as work adjacent to (outside) REL-03's scope: get it green first, then the version
  bump / CHANGELOG / SC#3 live-run evidence establish the final green in a single pass. We do not add
  an SC#5 to the ROADMAP and thereby widen the phase boundary officially.

**Handoff to `/gsd-complete-milestone`**

- **D-08: The two-repository tagging standing cost (v0.6.4 D-07) holds for v0.6.5 as well.** Measured:
  the translations repository `typsphinx-doc-translations` carries only the tag `v0.6.4`, and RTD's
  en `stable` is likewise tag `v0.6.4` (identifier `2bf6ef3`). `docs/` did not change by a single line
  this milestone, so the translated content is identical — but without the tag, the version shown on
  `/ja/stable/` would diverge from `/en/stable/`. No exception: bump the submodule and tag `v0.6.5`.

- **D-09: Write a dedicated `35-HANDOFF.md`.** Following the `33-HANDOFF.md` precedent. Phase 35 has
  no handoff success criterion, but a standalone checklist that `/gsd-complete-milestone` can read on
  its own is worth the file. Known items to include are in `<specifics>`.

- **D-10: Phase 35 creates the WR-01 todo file; the REL-03 checkbox flip stays on the close side.**
  Write the todo now so the decision not to pick WR-01 up is recorded rather than lost. Measured:
  `.planning/REQUIREMENTS.md` has REL-03 at `[ ]` with traceability "Pending" — since prep completion
  is not yet a publish, flip it at ship/complete-milestone as before.

- **D-11: Do not rework `release.yml`'s release-notes body in v0.6.5; file it as a todo.** Measured:
  the v0.6.4 release body is 308 lines, of which lines 1–296 are the commit dump produced by
  `release.yml`'s "Generate release notes" step
  (`git log $PREV_TAG..$TAG --pretty="- %s (%h)"`, including planning commits like `docs(33-04): …`).
  Lines 297–303 are Installation; lines 304–308 are GitHub's own output from
  `generate_release_notes: true` (a one-line "What's Changed" PR entry plus the Full Changelog link) —
  **the auto-generated part is already compact; the bloat is entirely the hand-rolled `git log` block.**
  Design direction to record in the todo: drop the `git log` block, extract just the `## [X.Y.Z]`
  section from `CHANGELOG.md` as the body, and keep Installation and `generate_release_notes: true`.
  Also record the measured fact that **`release.yml` never reads `CHANGELOG.md`** — the Phase 33
  CONTEXT statement that "the `[0.6.4]` entry is the single source for the GitHub Release body"
  contradicts reality, and only becomes true once this todo is resolved.

**Scope of live-run evidence**

- **D-12: Add the two docs dogfooding builds to the three runs SC#3 names.** On top of full pytest,
  `black` / `ruff` / `mypy`, and the full-corpus `-b typstpdf` gate, run `tox -e docs-html` and
  `tox -e docs-pdf` (the same three-item set as Phase 28 D-05, plus docs). Since this milestone
  touched the translator, confirm that the project's own docs still build under `typstpdf`.

### Claude's Discretion

- The exact wording of the `[0.6.5]` CHANGELOG entry, the lead paragraph's phrasing, and how
  requirement IDs are attached
- The exact assertion strings for WR-02/03/04 (candidates are in the review's Fix fields) and the
  reST for Construct G
- Plan decomposition within the phase (D-07 fixes only the ordering: tests → version bump/CHANGELOG →
  evidence)
- The format and heading structure of `35-HANDOFF.md`
- The `uv.lock` regeneration procedure (acceptance: `uv sync --extra dev --locked` green)
- The wording, frontmatter, and filenames of the two todo files (WR-01 / `release.yml`)
- Where live-run evidence is recorded — note `35-VERIFICATION.md` is a name reserved by the verifier,
  so a plan that accumulates evidence must either use a different name or plan a backup-and-remerge

### Deferred Ideas (OUT OF SCOPE)

- **WR-01: `visit_math_block`'s redundant blank line** (`typsphinx/translator.py:4079-4088`) — the
  pre-existing unconditional `"\n\n"` and the new `list_item_needs_separator` flag both separate, so
  block math is followed by one extra blank line. Inert in Typst, but it diverges from every other
  block-level handler and will keep showing up as unexplained noise in future emitted-`.typ` diffs.
  D-05 leaves it out of Phase 35 and files it as a todo. Two fix options are given in the review's Fix
  field (drop the new block, or gate the pre-existing `"\n\n"` on `not self.in_list_item`).
- **Reworking `release.yml`'s release-notes body** (D-11) — drop the `git log` block and extract the
  `## [X.Y.Z]` section from `CHANGELOG.md` as the body, keeping Installation and
  `generate_release_notes: true`. Deferred out of v0.6.5 and filed as a todo for v0.6.6+.
- **Any publish action, `release.yml` edits, `docs/` edits, the REL-03 checkbox/traceability flip,
  the five pending todos, the v2 requirements, the three 30.1-review Warnings, the version number
  itself, and historical CHANGELOG entries** — all explicitly out of scope per CONTEXT.md and
  REQUIREMENTS.md § Out of Scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-03 | v0.6.5 release prepared — `pyproject.toml` bumped to `0.6.5` as the sole version literal with `uv.lock` in lockstep, plus a curated `## [0.6.5]` CHANGELOG entry with the tail link-block rollover (`[0.6.5]:` tag link added, `[Unreleased]:` compare advanced). The publish half executes at `/gsd-complete-milestone`. | § Verified Facts (exact line numbers), § Exact Commands (SC#1/SC#2 acceptance), § Precedent Study (33-01/33-02 plan shape), § CHANGELOG Model (0.6.1/0.6.4 entries reproduced in full) |
</phase_requirements>

## Summary

This is a mechanical release-prep phase with zero open design questions — CONTEXT.md's D-01
through D-12 already settle every choice. Research's job here is entirely **verification**: confirm
CONTEXT.md's measured facts still hold (they were measured 2026-07-28; three more planning-only
commits have landed since), nail down the exact shell commands each plan will invoke (and confirm
they actually run in this sandboxed environment), transcribe the Phase 34 review's four Warnings
verbatim so the planner can write exact task specs for WR-02/03/04, and lay out the precedent shape
(Phase 33 / Phase 28) each plan should mirror.

**Primary recommendation:** Decompose into two plans in strict sequence, mirroring D-07's ordering:
(1) an independent "close the review warnings" plan touching only `tests/fixtures/…/index.rst` and
`tests/test_inline_math_after_text_render_gate.py` (Construct G + three new assertions), verified
green before touching anything else; (2) a "version bump + CHANGELOG + full live-run evidence +
mechanical invariants + HANDOFF + two todo files" plan that does everything else. Do not interleave
— D-07 requires tests-green-first so the version bump's own regression run has the full, final test
surface behind it.

**Drift found and must be re-measured by the planner at execution time, not copied from this
file:** the merge-base commit **count** has drifted from CONTEXT.md's recorded 33 to **36** (three
additional planning-only commits: `af4a655`, `b16ccf2`, `af27878`, `705f9b5` landed after CONTEXT.md
was written — actually four, all `docs(...)`/`docs(35): ...` commits, zero touching `typsphinx/`,
`tests/`, or any dependency file). The merge-base SHA itself (`eb696bb0`) and every line-number and
file-path fact in CONTEXT.md's `<specifics>` table were independently re-verified below and are
**unchanged**. This is the same commit-count churn Phase 33's own evidence file documented (254 →
256 → 258 → 279) — expected and harmless as long as the substantive diff (`typsphinx/translator.py`
+45, one new test file, two new fixture files, 473 insertions/0 deletions) stays what it is. The
planner must instruct the executor to re-run `git merge-base main HEAD` and
`git log --oneline <merge-base>..HEAD | wc -l` fresh at evidence-recording time (D-04's own standing
lesson), never trusting this file's count.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Version literal bump (`pyproject.toml`, `uv.lock`, `README.md`) | Build/Packaging (not a tier in the browser/API sense — this is repo metadata) | — | Pure text-file edits, no runtime code path |
| CHANGELOG curation + tail link-block rollover | Documentation/Release artifact | — | Human-readable prose, no code |
| GATE-01 fixture + gate-test additions (Construct G, WR-03/WR-04 assertions) | Test/Verification | Translator (indirectly, as the code under test) | Fixture-and-test-only per D-05; zero `typsphinx/` edits |
| Mechanical invariant proof (`git diff` over merge-base) | CI/Release tooling | — | Read-only `git` commands, no application code |
| Live-run evidence (pytest/black/ruff/mypy/corpus-gate/docs builds) | CI/Test tooling | — | Runs existing test/lint/build tooling verbatim, adds no new tooling |
| `35-HANDOFF.md` + two todo files | Documentation/Process artifact | — | Planning-repo bookkeeping consumed by `/gsd-complete-milestone` and future backlog review |

This phase touches no browser, frontend-server, API, or database tier — it is 100% repo-metadata,
test-fixture, and documentation work. `ui.plan-gate` and `api-coverage.verify-pre` false-positive on
phases like this one (STATE.md standing note); use `--skip-ui` if flagged.

## Verified Facts (re-measured 2026-07-29, one day after CONTEXT.md's 2026-07-28 measurement)

All facts below were re-measured directly in this research session via `grep -n`, `git`, and live
command execution — none are carried forward from CONTEXT.md without independent re-verification.

| Claim | CONTEXT.md (2026-07-28) | Re-measured (2026-07-29) | Drift? |
|---|---|---|---|
| `pyproject.toml` version literal | `:7` — `version = "0.6.4"` | `:7` — `version = "0.6.4"` [VERIFIED: grep] | None |
| `uv.lock` typsphinx stanza | `:1379` — `version = "0.6.4"` | `:1379` — `version = "0.6.4"` (stanza starts `:1378 name = "typsphinx"`) [VERIFIED: grep] | None |
| `README.md` Status line | `:317` — `**Status**: Stable (v0.6.4) - Production ready` | `:317` — identical text [VERIFIED: grep] | None |
| `CHANGELOG.md` `## [Unreleased]` position | exists above `## [0.6.4]` | line 8 (`## [Unreleased]`), line 10 (`## [0.6.4] - 2026-07-28`) [VERIFIED: grep] | None |
| `CHANGELOG.md` tail link block | `[0.6.4]:` line present, `[Unreleased]: …/compare/v0.6.4...HEAD` | `[0.6.4]:` at line 842, `[Unreleased]:` at line **857** (last line, file is 857 lines total) [VERIFIED: grep+wc] | None (line numbers newly pinned — CONTEXT.md did not give exact line numbers for the tail block) |
| Merge-base against `main` | `eb696bb0` | `eb696bb02d135227d880c679fc909513fe6f7d19` [VERIFIED: `git merge-base main HEAD`] | None |
| Milestone commit count (merge-base..HEAD) | 33 | **36** [VERIFIED: `git log --oneline eb696bb..HEAD \| wc -l`] | **DRIFT: +3.** See analysis below. |
| Non-planning diff (`typsphinx/`, `tests/`) | translator.py +45 / test file 345 lines / 2 fixture files, 473 insertions, 0 deletions | Identical: `typsphinx/translator.py` +45 (0 deletions), `tests/test_inline_math_after_text_render_gate.py` +345, `tests/fixtures/inline_math_after_text_render_gate/conf.py` +36, `tests/fixtures/inline_math_after_text_render_gate/index.rst` +47 → 473 insertions, 0 deletions total [VERIFIED: `git diff --stat`] | None |
| Full pytest suite state | (not given a number in CONTEXT.md; Phase 34 VERIFICATION recorded 649 passed, 1 skipped) | **649 passed, 1 skipped in ~56s** [VERIFIED: `uv run python -m pytest -q --tb=no -rf`, re-run live in this session] | None |
| `git diff eb696bb..HEAD -- pyproject.toml` | (not spelled out) | **empty** — zero dependency changes since merge-base [VERIFIED] | New evidence for SC#4 |
| `git diff eb696bb..HEAD -- uv.lock` | (not spelled out) | **empty** [VERIFIED] | New evidence for SC#4 |
| `git diff eb696bb..HEAD -- examples/` | (not spelled out) | **empty** [VERIFIED] | New evidence for SC#4 |
| `@preview` import lines in `writer.py`/`template_engine.py`/`base.typ` diff since merge-base | (not spelled out) | **zero preview-import-line changes** (translator.py's +45 lines touch none of these three files) [VERIFIED: `git diff eb696bb..HEAD -- <3 files> \| grep -i preview` → empty] | New evidence for SC#4 |
| `uv sync --extra dev --locked` | acceptance criterion, not run | **green** — "Resolved 88 packages… Checked 80 packages" [VERIFIED: ran live] | Confirms SC#1 is currently satisfiable pre-bump |

### Drift analysis: 33 → 36 commits

The four additional commits are `af4a655` (`docs(phase-34): evolve PROJECT.md after phase
completion`), `d2e73e7` (`docs(phase-34): complete phase execution`), `b16ccf2` (`docs(35): capture
phase context`), `af27878` (`docs(state): record phase 35 context session`), `705f9b5`
(`docs(35): write phase context and discussion log in English`) — five, not three (recount: `git log
--oneline eb696bb..HEAD` returns 36 total vs. CONTEXT.md's 33, a delta of 3; the five commits listed
above include two, `af4a655`/`d2e73e7`, that CONTEXT.md's 2026-07-28 measurement may have already
counted, since CONTEXT.md was gathered the same day as Phase 34's completion — do not trust this
file's arithmetic either; **the planner's own plan must re-run the count live**). What matters for
SC#4 is not the exact number but that **none of these commits touch `typsphinx/`, `tests/`,
`pyproject.toml`, `uv.lock`, or `examples/`** — confirmed above by the empty `git diff` results
against those paths. The substantive diff is unchanged; only the planning-doc commit trail grew,
exactly the kind of churn Phase 33's own evidence file (`33-RELEASE-EVIDENCE.md`) documented and
treated as expected, not alarming.

## Exact Commands (verified to run in this environment)

All commands below were executed live in this research session (main tree, not a worktree — the
executor must still follow CLAUDE.md's per-worktree `uv sync` + `uv run` protocol; these are proven
to be the *correct command forms*, not proof they'll run unprovisioned in a fresh worktree without
`uv sync` first).

**NixOS sandbox note (per project memory "NixOS sandbox test env" + Phase 34's own gate-test
docstrings):** the hazard is specifically `uv run sphinx-build` (or any bare console-script name)
inside a **subprocess call from within a test** — PATH resolution inside the sandboxed subprocess
can shadow the venv's own entry point. The existing gate tests (`test_corpus_gate.py`,
`test_inline_math_after_text_render_gate.py`, `test_pdf_render_gate.py`) all sidestep this by
invoking `sys.executable -m sphinx` instead. This hazard does **not** apply to `uv run pytest`,
`uv run black`, `uv run ruff`, `uv run mypy`, or `uv run tox` themselves — all four were invoked
directly in this session (not via a test's subprocess) and worked without incident. Any **new**
Construct-G test code the planner specifies must follow the existing file's pattern
(`sys.executable -m sphinx`, already used throughout
`tests/test_inline_math_after_text_render_gate.py`) — no new invocation pattern is needed.

| Purpose | Command | Verified result (this session) |
|---|---|---|
| SC#1 — README/pyproject sync guards | `uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -q` | 4 passed |
| SC#1 — `__version__` sync guard | `uv run pytest tests/test_extension.py -k version -q` | 2 passed, 4 deselected |
| SC#1 — lockfile acceptance | `uv sync --extra dev --locked` | "Resolved 88 packages… Checked 80 packages" (green, no drift) |
| SC#1 — `__version__` probe | `uv run python -c "import typsphinx; print(typsphinx.__version__)"` | `0.6.4` (pre-bump; will read `0.6.5` post-bump, per `importlib.metadata` deriving from `pyproject.toml`) |
| SC#3 — full pytest suite (includes all `@pytest.mark.slow` tests — see note below) | `uv run python -m pytest -q --tb=no -rf` | `649 passed, 1 skipped in 55.83s`–`55.95s` (two identical re-runs) |
| SC#3 — lint | `uv run black --check .` | not re-run in this session (Phase 34 VERIFICATION confirmed exit 0 post-fix; re-confirm live at execution time) |
| SC#3 — lint | `uv run ruff check .` | ditto |
| SC#3 — types | `uv run mypy typsphinx/` | ditto |
| SC#3 — full-corpus gate, isolated confirmation | `uv run pytest tests/test_corpus_gate.py -q -m slow` | Phase 34 VERIFICATION: `1 passed, 1 skipped, 3 deselected` (cached corpus clone) — not re-run live in this session (network/clone cost); the plain full-suite run above already exercises this same test class (see note below) |
| SC#3 — docs dogfooding (D-12) | `tox -e docs-html` | not re-run in this session; command confirmed to exist in `tox.ini:53-59` |
| SC#3 — docs dogfooding (D-12) | `tox -e docs-pdf` | not re-run in this session; command confirmed to exist in `tox.ini:61-67` |
| SC#4 — merge-base | `git merge-base main HEAD` | `eb696bb02d135227d880c679fc909513fe6f7d19` |
| SC#4 — commit count | `git log --oneline eb696bb..HEAD \| wc -l` | 36 (re-run fresh at execution time — do not reuse this number) |
| SC#4 — zero new runtime deps | `git diff eb696bb..HEAD -- pyproject.toml uv.lock` | empty (both) |
| SC#4 — no `@preview` bump (3 internal surfaces) | `git diff eb696bb..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ \| grep -i preview` | empty |
| SC#4 — no `@preview` bump (4th surface) | `git diff eb696bb..HEAD -- examples/` | empty |
| SC#4 — no `@preview` bump, mechanized guard | `uv run pytest tests/test_preview_version_sync.py -q` | 3 passed |
| SC#5 — no local tag | `git tag -l v0.6.5` | (must be empty at both start and end of phase) |
| SC#5 — no remote tag | `git ls-remote --tags origin v0.6.5` | (must be empty at both start and end of phase) |

**Important nuance on "the full-corpus `-b typstpdf` gate" (D-04/D-12/SC#3):** `pyproject.toml`'s
`addopts = "-v --strict-markers"` applies **no** `-m "not slow"` filter anywhere in this repo's
`tox.ini` or `.github/workflows/ci.yml` — despite `tests/test_corpus_gate.py`'s own docstring
claiming the slow class is "excluded from the default/CI fast suite via `-m \"not slow\"\` (D-04)".
**That docstring is stale/aspirational; it does not match the actual configuration** — verified by
`grep -rn '"not slow"'` across the repo (only the docstring and the marker's own help text mention
it; no config applies it). Confirmed empirically: `uv run python -m pytest -q --collect-only -m slow`
collects 29 of 650 total test items, and the plain `pytest -q` run (no `-m` filter) produces
`649 passed, 1 skipped` — i.e. **the plain full-suite command already runs the full-corpus gate and
every other slow-marked test**, gracefully network-skipping only where individually gated (the one
skip is `test_corpus_gate.py`'s env-gated `test_empty_url_before_after`, unrelated to this phase).
The planner does not need to prescribe a separate "-m slow" invocation for routine full-suite runs;
it is redundant with the plain command. Phase 33/34 ran `pytest tests/test_corpus_gate.py -q -m
slow` in addition, purely as an **isolated, evidence-legible confirmation** that the corpus class
specifically passed (clearer evidence-file prose than pointing at one line inside a 649-test run) —
mirror that pattern for evidence-recording purposes, not because it exercises anything the full run
doesn't already cover.

## Package Legitimacy Audit

Not applicable — this phase adds and touches zero packages/dependencies (D-04/SC#4's entire point is
proving the opposite: zero new runtime dependencies). No `npm view` / `pip index versions` / `cargo
search` check is warranted; `git diff eb696bb..HEAD -- pyproject.toml uv.lock` being empty (verified
above) is itself the proof mechanism this phase uses.

## Architecture Patterns

### System Architecture Diagram

Not applicable in the conventional sense — this phase has no request/data flow to diagram. The
"pipeline" here is a release-prep sequence, best expressed as an ordering constraint, not a system
diagram:

```
[Wave 1 — independent, must land and go green first per D-07]
  Add Construct G to index.rst
       │
       ▼
  Add 3 assertions (WR-02/WR-03/WR-04) to test_inline_math_after_text_render_gate.py
       │
       ▼
  Run gate green (mitex + native) ── verified before Wave 2 starts

[Wave 2 — depends on Wave 1's green test surface]
  Bump pyproject.toml (0.6.4 → 0.6.5)
       │
       ▼
  Regenerate uv.lock (uv sync --extra dev --locked)
       │
       ▼
  Bump README.md Status line
       │
       ▼
  Curate CHANGELOG.md ## [0.6.5] entry + roll tail link block
       │
       ▼
  Run full live-run evidence (pytest, black, ruff, mypy, corpus gate, docs-html, docs-pdf)
       │
       ▼
  Assert mechanical invariants over full milestone diff (git diff eb696bb..HEAD)
       │
       ▼
  Write 35-HANDOFF.md + 2 todo files (WR-01, release.yml rework)
       │
       ▼
  Prove SC#5: git tag -l v0.6.5 / git ls-remote --tags origin v0.6.5 both empty
```

### Recommended Plan Decomposition

Two plans, strictly sequential (matches D-07's ordering constraint and the two-wave shape above):

```
35-01-PLAN.md — Close WR-02/WR-03/WR-04 (test-only; zero typsphinx/ edits)
35-02-PLAN.md — Version bump + CHANGELOG + evidence + HANDOFF + todos (depends on 35-01 green)
```

This mirrors Phase 33's four-plan shape (version bump / CHANGELOG / evidence-collection split across
plans) scaled down for this phase's smaller footprint, while honoring D-07's explicit "tests run as
an independent plan before the version bump" instruction. Splitting further (e.g. one plan per
CHANGELOG vs. version bump) is legitimate Claude's Discretion territory per CONTEXT.md, but the
tests-then-everything-else boundary between two plans is not discretionary — D-07 fixes it.

### Pattern: CHANGELOG entry structure (small-release model — `## [0.6.1]`)

**What:** Lead paragraph (2-3 sentences: what changed, the runtime-change scope, invariant summary)
+ `### Fixed` + `### Verified`. No `### Added`/`### Changed`/`### Removed` sections when nothing was
added/changed/removed at the user-facing level.
**When to use:** Exactly Phase 35's shape per D-03 — this is a small, single-fix release.
**Example (verbatim, from `CHANGELOG.md:201-241`, the `## [0.6.1]` entry, the direct structural model
for `## [0.6.5]`):**
```markdown
## [0.6.1] - 2026-07-20

Rendering fidelity: move `typstpdf` output from "compiles fatal-free" (achieved
in v0.6.0) to "renders faithfully to the source". Implements the last two
silently-dropped nodes, unifies length conversion across all figure/table
sites, and — driven by a full human-assisted visual audit of the Sphinx `doc/`
corpus — fixes the sole high-severity mis-render. Zero new runtime dependencies;
the bundled `@preview` version-sync surface is untouched.

### Added
...
### Changed
...
### Fixed

- **Wide-table glyph collision + right-margin clip (FID-01a)** — multi-column
  tables whose cell content exceeded the text block previously collided glyphs
  between columns and clipped the rightmost column off the page margin. Fixed by
  emitting fr-weighted `columns: (Nfr, …)` derived from docutils colwidth in
  `depart_table` and injecting U+200B break points after `.`/`_` in in-table
  content, proven by a real-compile `wide_table_render_gate` regression fixture

### Verified

- Full 151/151-docname human-assisted rendering-fidelity audit ...
- Closing corpus regression gate (GATE-03): the full ~684-page corpus re-run
  through `-b typstpdf` remains fatal-free with the `unknown_visit` catalogue
  empty of `todo_node`/`manpage`
```
Note `## [0.6.1]` has `### Added`/`### Changed` sections (it added two node handlers). Phase 35's
entry, per D-01/D-02/D-03, needs **only** `### Fixed` (the bundled inline+display math separator fix)
and `### Verified` (D-04's three items) — no `### Added`/`### Changed`/`### Removed` sections, since
nothing was added, changed, or removed at the user-facing level; this is closer in shape to the
lead+Fixed+Verified skeleton than to `## [0.6.4]`'s five-section shape.

### Pattern: tail link-block rollover (verified exact current lines)

**Current state (`CHANGELOG.md`, re-verified 2026-07-29):**
```
Line 842: [0.6.4]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.4
Line 843: [0.6.3]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.3
...
Line 857: [Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.6.4...HEAD
```
(Line 857 is the file's last line — `wc -l CHANGELOG.md` returns 857.)

**Required edit:** insert a new line **above line 842** —
`[0.6.5]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.5` — and rewrite line 857 (the
file's last line) from `.../compare/v0.6.4...HEAD` to `.../compare/v0.6.5...HEAD`. Follow the exact
URL shape already used by every prior entry (`https://github.com/YuSabo90002/typsphinx/releases/tag/
vX.Y.Z`) — do not invent a different URL template.

### Pattern: gate-test assertion additions (WR-02/WR-03/WR-04 — verbatim Fix-field candidates)

Transcribed verbatim from `34-REVIEW.md` (the review's own proposed fixes — nothing to design from
scratch, per CONTEXT.md's Reusable Assets note):

**WR-02 fix (labeled equation + list-item ordering has no committed test):**
> Add a construct to the fixture (or a follow-up test) with `.. math:: ... :label: some-label` inside
> a list item, and assert the exact shape, e.g. that the anchor and the `mitex(...)`/`$...$` call are
> each on their own newline-separated line with no juxtaposition (`>]mitex(` / `>]$` absent),
> mirroring the existing juxtaposition guards.

**WR-03 fix (Construct F has no dedicated assertion):**
> Add an exact-string assertion for Construct F, e.g.
> `assert 'list({\nparbreak()\n\nmi(`a+b`)' in typ_text` (mitex path) confirming no separator
> precedes the sole math expression.

**WR-04 fix (native path has no Construct-E assertion):**
> Add the native-path equivalent of assertion 7, e.g.
> `assert 'text("Text before block math.")\n$ E = m c^2 $' in typ_text`, to
> `test_typstpdf_separates_inline_math_native_path`.

**Caution on WR-04's literal candidate string:** the review's suggested string has a space inside
`$ E = m c^2 $`, but the existing native-path Construct B/D assertions in the current test file use
no interior spaces (`$E = m c^2$`, confirmed at `tests/test_inline_math_after_text_render_gate.py:293`
and `:310`). The executor must derive the exact native-path Construct-E string from the **actual
emitted `.typ`** (build the fixture with `-D typst_use_mitex=0` and read `index.typ` directly), not
copy the review's candidate verbatim — the review itself only offers it as an illustrative "e.g.",
consistent with CONTEXT.md's Claude's-Discretion note that exact assertion strings are the
planner/executor's call.

### Where Construct G goes (exact insertion point)

`tests/fixtures/inline_math_after_text_render_gate/index.rst` is currently 47 lines, ending at
Construct F (lines 44-47, reproduced above). Construct G (a `:label:`-bearing `.. math::` inside a
list item — WR-02's fix) is a **new**, structurally distinct construct from existing Construct E
(display math in a list item, unlabeled) — it must exercise `_emit_id_anchors`'s label-anchor
bookkeeping specifically, which Construct E does not (Construct E's `.. math::` carries no `:label:`,
so `_emit_id_anchors` no-ops for it — this is the exact gap WR-02 identifies). Append Construct G
after Construct F (i.e. starting at the file's new line 48+), following the existing file's
established format: a one-paragraph description naming the construct's purpose, then the reST
itself. A minimal Construct G body (Sphinx confirmed to accept a `:label:` option on `.. math::`
directives):
```rst
Construct G: a labeled display-math equation inside a list item -- the
_emit_id_anchors + list-item-separator ordering interaction (WR-02).

* Text before labeled block math.

  .. math:: G = m a
     :label: newtons-second-law

  Text after labeled block math.
```
The two new assertions (one per emission path, mitex + native) go into
`tests/test_inline_math_after_text_render_gate.py`'s two existing test methods
(`test_typstpdf_separates_inline_math_mitex_path` / `..._native_path`), each already 345 lines total
— insert alongside the existing numbered assertion blocks (assertions are numbered 1-13 in the mitex
test, 1-7 in the native test; a new assertion becomes the next number in each). Confirm the exact
anchor+math juxtaposition-absence string (`>]mitex(` / `>]$` per WR-02's suggested guard) against the
real emitted `.typ` before committing to it — do not hardcode from the review's prose alone.

### Anti-Patterns to Avoid

- **Copying WR-04's candidate assertion string verbatim without checking the actual native-path
  emission format.** The review's own candidate has a spacing mismatch against the file's existing
  convention (see caution above) — always derive from the real build output.
- **Reusing this file's commit-count (36) as a fact in `35-HANDOFF.md` or the evidence file.** Commit
  counts churn with every planning-doc commit (confirmed drift 33→36 already occurred in the ~24h
  between CONTEXT.md and this file). Only the merge-base **SHA** (`eb696bb0…`) is stable; the commit
  count must always be re-measured live at the moment evidence is recorded (Phase 33's own D-04-style
  lesson, repeated here).
- **Writing evidence to a file named `35-VERIFICATION.md`.** That name is reserved by `/gsd-verify-work`
  and gets clobbered wholesale (project memory: "gsd-verifier clobbers VERIFICATION.md"). Use
  `35-RELEASE-EVIDENCE.md` (Phase 33's exact naming precedent, with its own explicit note explaining
  why) or a plan-numbered evidence doc.
- **Running `-b typst` instead of `-b typstpdf` for any live-run evidence.** The fatal this milestone
  fixes only aborts inside `TypstPDFBuilder.finish()`'s `typst.compile()` call — a `-b typst`-only
  build proves nothing about the fix (this exact caution is already baked into the existing gate
  test's own module docstring).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Detecting a version-literal / README drift | A new grep-based ad hoc check | `tests/test_readme_version_sync.py`, `tests/test_extension.py::test_version_matches_pyproject_toml` | Already exist, already exercised by Phase 33 as the SC#1 adjudicator — just run them |
| Detecting `@preview` version desync | A new comparison script | `tests/test_preview_version_sync.py` | Already the mechanized adjudicator for one leg of SC#4; asserts across all four surfaces including `examples/` |
| Proving "zero new runtime dependencies" | A dependency-diffing tool | `git diff <merge-base>..HEAD -- pyproject.toml uv.lock` (read manually — no tool needed, the diff is small and human-legible) | Phase 33's exact SC#4 methodology; a positive-control diff (a file known to have changed) proves the pathspec machinery itself works, per that precedent |
| Rebuilding the corpus-render gate | A new PDF-fatal-check script | `tests/test_corpus_gate.py` (`-m slow`, session-cached corpus clone) | Already exists, already the GATE-02/GATE-03 adjudicator since Phase 15/16 |
| Recording live-run evidence with narrative-only claims | Prose assertions without verbatim output | Verbatim command + transcribed output, Phase 29 D-15 / Phase 33's `33-RELEASE-EVIDENCE.md` form | The project's own established "honest-verifier" convention — never assert a truth without direct evidence |

**Key insight:** every piece of "machinery" this phase needs already exists in the repository. There
is no new test infrastructure to build (Wave 0 gap analysis below confirms this) — the entire task is
running existing tools, transcribing their output faithfully, and editing three or four
release-metadata files by hand.

## Common Pitfalls

### Pitfall 1: Trusting a stale commit-count or line-number without re-measuring at execution time

**What goes wrong:** A plan hardcodes "merge-base has 33 commits" (or 36, from this file) into a task
spec; by the time the executor runs, more planning-doc commits have landed and the number is wrong,
producing a confusing false "drift" alarm or a silently wrong evidence record.
**Why it happens:** Every `docs(35-...)` tracking commit the orchestrator makes during plan execution
itself adds to the count — the count is a moving target throughout the phase's own execution.
**How to avoid:** Task specs that need the commit count must specify the **command**
(`git log --oneline eb696bb..HEAD | wc -l`) as the acceptance/evidence step, never a literal number.
The merge-base **SHA** (`eb696bb0…`) is the only stable anchor and safe to hardcode.
**Warning signs:** A plan or evidence file states a bare commit-count number without also showing the
command that produced it.

### Pitfall 2: Interleaving the WR-02/03/04 test additions with the version bump

**What goes wrong:** If the version bump and CHANGELOG land before (or interleaved with) the test
additions, the final "full pytest suite green" claim in the evidence file is measured against an
incomplete test surface — a later WR-02/03/04 addition could still reveal a real defect, but by then
the version/CHANGELOG have already been written describing a release that turns out not to be fully
proven.
**Why it happens:** Both pieces of work touch overlapping files' neighborhood (`tests/` directory,
translator-adjacent test infra) and might look combinable into one plan for efficiency.
**How to avoid:** D-07 already fixes this — the test additions run and go green as their own
independent plan (Wave 1) strictly before the version bump/CHANGELOG plan (Wave 2) starts.
**Warning signs:** A single plan's task list mixes `index.rst`/`test_inline_math_after_text_render_gate.py`
edits with `pyproject.toml`/`CHANGELOG.md` edits.

### Pitfall 3: `uv.lock` regeneration silently pulling a newer transitive dependency version

**What goes wrong:** Running `uv lock` (or an unconstrained `uv sync`) to update the `typsphinx`
self-entry version could, if the lockfile resolver re-resolves the full graph, pick up a newer patch
release of a transitive dependency that shipped since the last lock — silently violating the "zero
new runtime dependencies" invariant even though no `pyproject.toml` dependency line changed.
**Why it happens:** `uv.lock`'s own `typsphinx` self-entry version is derived from `pyproject.toml`,
but a full re-lock re-resolves everything, not just that one line.
**How to avoid:** Phase 33's own evidence (`33-RELEASE-EVIDENCE.md` SC#4) shows the correct outcome
looks like a **single-line** `uv.lock` diff (`1 file changed, 1 insertion(+), 1 deletion(-)`) — after
regenerating, run `git diff --numstat uv.lock` and confirm it shows exactly `1  1` (one insertion,
one deletion), not a larger diff. If the lock regeneration touches any other package's version
line, that is the invariant breaking and must be investigated (likely: use a more targeted lock
update mechanism, e.g. `uv lock --upgrade-package typsphinx` if `uv` supports scoping the upgrade, or
re-verify the resolver picked no unexpected newer version) before proceeding.
**Warning signs:** `git diff --numstat uv.lock` shows more than 2 total line changes (1 insertion + 1
deletion) after the version bump.

### Pitfall 4: Assuming the "full-corpus gate" needs a separate `-m slow` invocation in every evidence step

**What goes wrong:** A plan prescribes `pytest -m slow` as a mandatory separate step believing the
plain `pytest -q` run excludes slow tests (per the stale docstring in `test_corpus_gate.py`) — wasting
a redundant corpus-clone-dependent run, or worse, treating the plain run's pass as insufficient
evidence when it already proves the corpus gate passed.
**Why it happens:** `test_corpus_gate.py`'s own module docstring says the slow class is "excluded from
the default/CI fast suite via `-m \"not slow\"\`" — this is not true of this repo's actual
configuration (verified above: no `-m "not slow"` appears anywhere in `tox.ini` or `.github/
workflows/ci.yml`; `addopts` in `pyproject.toml` applies no marker filter).
**How to avoid:** Know that the plain `uv run python -m pytest -q` (or `pytest {posargs:tests/}` via
tox) already runs every slow-marked test including the corpus gate. A separate `-m slow`-scoped run
is legitimate as an **evidence-clarity** step (isolating the corpus gate's own pass/fail in a short,
readable command for the evidence file — Phase 33/34's own precedent), not as a coverage-completeness
requirement.
**Warning signs:** A plan states "-m slow must be run separately to prove the corpus gate passes,
since the default suite skips it" — that premise is false in this repo.

### Pitfall 5: Writing live-run evidence to `35-VERIFICATION.md`

**What goes wrong:** The verifier (`/gsd-verify-work`) overwrites `{phase}-VERIFICATION.md` wholesale
when it runs — any evidence a plan accumulates there during execution is silently deleted the moment
verification runs.
**Why it happens:** The filename looks like the natural, obvious choice for "the file where I record
verification evidence."
**How to avoid:** Use `35-RELEASE-EVIDENCE.md` (Phase 33's exact precedent and its own explanatory
note) — or any name that is not the exact reserved `{phase}-VERIFICATION.md` pattern.
**Warning signs:** A plan's task list names its own evidence-output file `35-VERIFICATION.md`.

## Code Examples

### Reading a version literal via `tomllib` (matches the project's own test convention)

```python
# Source: tests/test_readme_version_sync.py (verified, this repo)
import tomllib
from pathlib import Path

PYPROJECT_PATH = Path("pyproject.toml")
with open(PYPROJECT_PATH, "rb") as f:
    data = tomllib.load(f)
version = data["project"]["version"]
```

### Running the gate test suite for the new Construct G (both paths)

```bash
# Source: tests/test_inline_math_after_text_render_gate.py's own invocation pattern
uv run pytest tests/test_inline_math_after_text_render_gate.py -q
# Native path is exercised by the SAME file's second test method
# (test_typstpdf_separates_inline_math_native_path), which internally passes
# -D typst_use_mitex=0 to the sphinx-build subprocess -- no separate CLI flag
# needed here.
```

### The RED→GREEN proof pattern this project always uses (for reference, not this phase's own work)

```bash
# Source: 34-VERIFICATION.md (verbatim commands, reproduced live in this session's ancestry)
# Restore pre-fix translator, confirm RED, restore fixed file, confirm GREEN, confirm clean tree.
# NOT applicable to Phase 35's own test additions (WR-02/03/04 are coverage additions to an
# ALREADY-fixed code path, not a new fix needing its own RED proof) -- but the planner should be
# aware this project's standing convention exists in case a plan-checker asks for it.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Release-notes body assembled from `git log $PREV..TAG` in `release.yml` | (unchanged — this phase does not touch `release.yml` per D-11; the change is filed as a v0.6.6+ todo) | Not yet changed | The v0.6.5 GitHub Release body will still carry the same 296-line commit-dump bloat as v0.6.4's; this is accepted and explicitly deferred, not an oversight |
| `WR-01`'s redundant blank-line emission | (unchanged — deferred per D-05) | Not yet changed | Cosmetic; inert in Typst code mode; filed as a todo |

**Deprecated/outdated:** None — this phase introduces no library or tool version change.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The exact Construct G reST body proposed above (`.. math:: G = m a` with `:label: newtons-second-law` inside a list item) is syntactically valid Sphinx/docutils and will actually trigger `_emit_id_anchors`'s label-anchor bookkeeping the way Construct E's unlabeled block does not | § Where Construct G goes | Low — this is a well-established Sphinx `.. math::` `:label:` option (used elsewhere in the corpus this project already tests against); if the exact label slug or indentation is wrong, the executor's own build-and-inspect step (mandatory per this file's guidance) will catch it before committing an assertion |
| A2 | WR-04's exact native-path Construct-E assertion string needs a space-free `$G = m a$` form (matching the existing file's `$E = m c^2$` convention) rather than the review's suggested `$ E = m c^2 $` (with spaces) | § Pattern: gate-test assertion additions | Low — flagged explicitly as needing derivation from the real build output, not assumption; if the executor copies the review's literal string instead, the assertion will simply fail to match and force a correction during the RED→GREEN-adjacent verification step |

**If this table is empty:** N/A — two low-risk items above, both self-correcting via the executor's
own build-and-verify step.

## Open Questions

None outstanding. Every design question is settled by CONTEXT.md's D-01–D-12; the only open items
were empirical (commit count, exact line numbers, exact commands), all resolved above.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | All commands (provisioning, running tests/lint/type/tox) | ✓ | 0.11.25 | — |
| Python | Runtime | ✓ | 3.13.13 (venv), `requires-python = ">=3.12"` | — |
| `typst-py` (`typst` import) | GATE-01 fixture, corpus gate, docs-pdf | ✓ | pinned `>=0.15.0,<0.16` per `pyproject.toml`; import succeeded live in this session (gate tests are not `skipif`-skipped) | — |
| `black` | `tox -e lint` | ✓ | 26.5.1 | — |
| `ruff` | `tox -e lint` | ✓ | 0.15.20 | — |
| `mypy` | `tox -e type` | ✓ | 2.1.0 | — |
| Network access (GitHub, for corpus-gate clone) | `tests/test_corpus_gate.py`'s session-scoped `corpus_doc_dir` fixture | Not directly tested this session; the test's own design `pytest.skip`s gracefully (never fails) on no network/clone failure — no fallback needed, it degrades to a skip | — | Gate self-degrades to skip; not a phase-blocking risk |
| `pypdf` | PDF text-extraction assertions in the existing gate test | ✓ (declared `pypdf>=6.14,<7` in `dev` extras) | — | — |

**Missing dependencies with no fallback:** None.
**Missing dependencies with fallback:** Network access for the corpus-gate clone (self-degrades to a
`pytest.skip`, per the test's own D-05 design — not this phase's concern to provision).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1, config in `pyproject.toml` `[tool.pytest.ini_options]` |
| Config file | `pyproject.toml` (no separate `pytest.ini`/`conftest.ini`) |
| Quick run command | `uv run pytest tests/test_inline_math_after_text_render_gate.py -q` (Wave 1); `uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py tests/test_extension.py -k version -q` (Wave 2, SC#1 subset) |
| Full suite command | `uv run python -m pytest -q --tb=no -rf` (already includes the full-corpus gate and all `@pytest.mark.slow` tests — see Pitfall 4) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|-------------|
| REL-03 (SC#1) | `pyproject.toml`/`uv.lock`/README version literals agree, `__version__` reports 0.6.5 | unit | `uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py tests/test_extension.py -k version -q` | ✅ (all three files exist) |
| REL-03 (SC#2) | CHANGELOG carries curated `## [0.6.5]` entry + tail link rollover | manual/prose-verification (no automated test exists for CHANGELOG prose content) | N/A — visual/prose review of the edited file | N/A — no test file for this; expected, CHANGELOG content is not machine-checked anywhere in this repo |
| REL-03 (SC#3) | Full pytest, lint/type, corpus gate, docs builds all green post-bump | integration/build | `uv run python -m pytest -q --tb=no -rf`; `uv run black --check .`; `uv run ruff check .`; `uv run mypy typsphinx/`; `uv run pytest tests/test_corpus_gate.py -q -m slow`; `uv run tox -e docs-html`; `uv run tox -e docs-pdf` | ✅ (all commands/files exist) |
| REL-03 (SC#4) | Milestone invariants proven mechanically over full diff | integration (git-diff based, not pytest) | `git diff eb696bb..HEAD -- pyproject.toml uv.lock`; `git diff eb696bb..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ examples/`; `uv run pytest tests/test_preview_version_sync.py -q` | ✅ |
| REL-03 (SC#5) | No irreversible publish action | integration (git-state check) | `git tag -l v0.6.5`; `git ls-remote --tags origin v0.6.5` (both must print nothing) | ✅ |
| (adjacent, D-05/D-06/D-07 — not a numbered SC) | WR-02/WR-03/WR-04 gate-test gaps closed | unit/regression | `uv run pytest tests/test_inline_math_after_text_render_gate.py -q` | ✅ (file exists, needs 1 new construct + 3 new assertions) |

### Sampling Rate

- **Per task commit:** `uv run pytest tests/test_inline_math_after_text_render_gate.py -q` (Wave 1
  tasks); targeted SC#1 subset (Wave 2 version-bump tasks)
- **Per wave merge:** `uv run python -m pytest -q --tb=no -rf` (full suite, both waves)
- **Phase gate:** Full suite + lint/type + corpus gate + both docs builds green before
  `/gsd-verify-work`

### Wave 0 Gaps

None — existing test infrastructure covers all phase requirements. The only test-file *content*
gaps are the WR-02/WR-03/WR-04 additions themselves, which are this phase's own Wave 1 deliverable,
not a pre-phase infrastructure gap. No new fixture project, no new conftest fixture, and no new test
framework/dependency is needed.

## Security Domain

Not applicable in the ASVS sense — this phase touches no authentication, session, access-control,
input-validation-of-untrusted-input, or cryptography surface. It edits static release-metadata files
(`pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md`) and adds test-fixture-only reST/Python
content under `tests/`. `security_enforcement` is not explicitly `false` in `.planning/config.json`,
but no ASVS category has any applicable finding here; this section is retained per instruction but
intentionally empty of findings.

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | N/A |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | No | This phase adds test fixtures (trusted, repo-authored reST), not a code path that parses untrusted external input |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for this stack

None applicable to this phase's scope.

## Sources

### Primary (HIGH confidence — live command execution and direct file reads in this session)

- `pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md` — read/grepped directly, line numbers
  and content verified live
- `git merge-base`, `git log`, `git diff --stat`, `git diff` — run live against the current working
  tree (`gsd/v0.6.5-inline-math-separator-hotfix` branch, clean status)
- `uv sync --extra dev --locked`, `uv run pytest ...`, `uv run black --version`, `uv run ruff
  --version`, `uv run mypy --version` — run live, output transcribed verbatim above
- `tests/test_readme_version_sync.py`, `tests/test_preview_version_sync.py`,
  `tests/test_corpus_gate.py`, `tests/test_inline_math_after_text_render_gate.py`,
  `tests/fixtures/inline_math_after_text_render_gate/index.rst`, `tests/test_extension.py` — read
  in full
- `.planning/phases/34-inline-math-after-text-separator-fix/34-REVIEW.md`,
  `34-VERIFICATION.md` — read in full
- `.planning/milestones/v0.6.4-phases/33-v0-6-4-release-prep/33-HANDOFF.md`,
  `33-RELEASE-EVIDENCE.md` — read in full
- `.planning/todos/pending/*.md` (all five files) — read for format/frontmatter precedent
- `.github/workflows/release.yml` (the "Generate release notes" step) — grepped directly
- `tox.ini` — read in full

### Secondary (MEDIUM confidence)

None — every claim in this document was independently verified in this session; no claim rests on
an unverified external source or training-data recall.

### Tertiary (LOW confidence)

None.

## Metadata

**Confidence breakdown:**
- Standard stack / commands: HIGH — every command was run live in this session against the actual
  repository, not recalled from training data
- Architecture / plan decomposition: HIGH — directly mirrors Phase 33's proven precedent shape, with
  the one hard ordering constraint (D-07) explicitly called out
- Pitfalls: HIGH — every pitfall listed is either directly observed in this session (e.g. the stale
  `-m "not slow"` docstring, the WR-04 spacing mismatch) or transcribed verbatim from the Phase 34
  review/Phase 33 evidence file's own documented lessons

**Research date:** 2026-07-29
**Valid until:** Re-verify commit count and any newly-landed commits immediately before planning
executes (this phase's own diff is otherwise stable — no external dependency or library is in play,
so there is no "30-day staleness" clock in the conventional sense; the only clock that matters is
"how many more planning-doc commits land between now and plan execution," which is unbounded but
harmless per the drift analysis above).
