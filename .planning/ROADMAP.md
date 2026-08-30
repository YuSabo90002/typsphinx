# Roadmap: typsphinx

## Milestones

- ✅ **v0.4.4 — CI-repair + modernize** — Phases 1–5 (shipped 2026-07-05) → [archive](milestones/v0.4.4-ROADMAP.md)
- ✅ **v0.5.0 — forward-ecosystem** — Phases 6–10 + 8.1 (shipped 2026-07-11) → [archive](milestones/v0.5.0-ROADMAP.md)
- ✅ **v0.6.0 — real-world robustness** — Phases 11–15 (shipped 2026-07-13) → [archive](milestones/v0.6.0-ROADMAP.md)
- ✅ **v0.6.1 — rendering fidelity** — Phases 16–18 (shipped 2026-07-19) → [archive](milestones/v0.6.1-ROADMAP.md)
- ✅ **v0.6.2 — rendering fidelity round 2** — Phases 19–23 (+22.1–22.4) (shipped 2026-07-23) → [archive](milestones/v0.6.2-ROADMAP.md)
- ✅ **v0.6.3 — config & docs measured fidelity + captioned tables** — Phases 24–28 (+27.1) (shipped 2026-07-25) → [archive](milestones/v0.6.3-ROADMAP.md)
- ✅ **v0.6.4 — Read the Docs migration** — Phases 29–33 (+30.1) (shipped 2026-07-28) → [archive](milestones/v0.6.4-ROADMAP.md)
- ✅ **v0.6.5 — inline-math separator hotfix** — Phases 34–35 (shipped 2026-07-29) → [archive](milestones/v0.6.5-ROADMAP.md)
- ✅ **v0.7.0 — API rendering design overhaul** — Phases 36–42 (+40.1) (shipped 2026-08-04) → [archive](milestones/v0.7.0-ROADMAP.md)
- ✅ **v0.7.1 — bug-fix round** — Phases 43–46 (+44.1, 44.2, 45.1, 45.2) (shipped 2026-08-11) → [archive](milestones/v0.7.1-ROADMAP.md)
- ✅ **v0.8.0 — multi-master composition** — Phases 47–52 (shipped 2026-08-15) → [archive](milestones/v0.8.0-ROADMAP.md)
- ✅ **v0.9.0 — per-document templates** — Phases 53–57 (+54.1) (shipped 2026-08-22) → [archive](milestones/v0.9.0-ROADMAP.md)
- ✅ **v0.9.1 — Windows path correctness** — Phases 58–61 (completed 2026-08-30, **never published**) → [archive](milestones/v0.9.1-ROADMAP.md)
- 🚧 **v0.9.2 — Inline image blocker fix and release** — Phases 62–63 (active, started 2026-08-30)

**Active milestone: v0.9.2 — Inline image blocker fix and release.** Two phases (62–63), and two
aims, nothing else: close the blocker that stopped v0.9.1 from being published — an image node not
first in its container is emitted adjacent to the preceding code-mode expression, so Typst refuses
the file with `expected semicolon or line break` and `-b typstpdf` writes **no PDF for any master** —
then publish that fix together with v0.9.1's completed-but-unreleased work as **0.9.2** on PyPI.

**v0.9.1 completed but was never released, and the next published version is 0.9.2.** No `v0.9.1`
tag exists, locally or on the remote; `pyproject.toml` is still `0.9.0` and the milestone's CHANGELOG
bullets wait under `## [Unreleased]`. REL-09 carries forward unmet per D-08 with its obligations
unchanged — only its version token is corrected from 0.9.1 to 0.9.2, because v0.9.1 will never be
published and the literal wording was therefore unachievable (owner-confirmed 2026-08-30).

Phase numbering is **continuous across milestones** — v0.9.1 ran Phases 58–61, so v0.9.2 starts at
**Phase 62**.

## Phases

**Phase Numbering:**

- Integer phases (62, 63, …): Planned milestone work
- Decimal phases (62.1, 62.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.9.1 ran Phases 58–61, so this milestone starts at **Phase 62**.

<details>
<summary>✅ v0.9.1 Windows path correctness (Phases 58–61) — COMPLETED 2026-08-30, NOT PUBLISHED</summary>

- [x] Phase 58: `repr()`-Format Decoupling (test-side only) (3/3 plans) — completed 2026-08-28
- [x] Phase 59: Path-Shape Predicate and Image-URI Correctness (5/5 plans) — completed 2026-08-29
- [x] Phase 60: One Delimiter-Aware Path-Quoting Helper, Routed Everywhere (5/5 plans) — completed 2026-08-29
- [x] Phase 61: v0.9.1 Release Prep (prep-only) (4/4 plans) — completed 2026-08-30

10/11 v1 requirements complete. REL-09 (publish to PyPI) deliberately unmet — the release was
cancelled, not missed; it is carried forward into this milestone. Full phase detail, the 14 binding
constraints, success criteria and decisions: [milestones/v0.9.1-ROADMAP.md](milestones/v0.9.1-ROADMAP.md)

</details>

<details>
<summary>✅ v0.9.0 per-document templates (Phases 53–57, +54.1) — SHIPPED 2026-08-22</summary>

- [x] Phase 53: Template Registry Foundation (10/10 plans) — completed 2026-08-15
- [x] Phase 54: One Bundle Rule — `_template/<key>/`, Per-Document Selection, Four Deletions (7/7 plans) — completed 2026-08-16
- [x] Phase 54.1: Bundle Directory Safety — `templates_path` Collision Refusal and Pre-Write Path Validation (INSERTED) (5/5 plans) — completed 2026-08-16
- [x] Phase 55: v0.8.0-Derived Defects (4/4 plans) — completed 2026-08-16
- [x] Phase 56: Per-Document Template Documentation (5/5 plans) — completed 2026-08-16
- [x] Phase 57: v0.9.0 Release Prep (prep-only) (11/11 plans) — completed 2026-08-22

Full phase detail, success criteria, and decisions: [milestones/v0.9.0-ROADMAP.md](milestones/v0.9.0-ROADMAP.md)

</details>

<details>
<summary>✅ v0.4.4 – v0.8.0 (Phases 1–52) — SHIPPED 2026-07-05 → 2026-08-15</summary>

Each milestone's phase detail lives in its own archive, linked from the **Milestones** list above.

</details>

## 🚧 v0.9.2 — Inline image blocker fix and release (ACTIVE)

**Milestone Goal:** a document that puts an image anywhere other than first in its container still
compiles, and the fix reaches users — because the blocker is live in the *published* 0.9.0 today
with no public-surface disclosure, and publishing 0.9.2 is what repays that. This is a blocker-fix-
and-ship round: no new user-facing capability, no new runtime or dev dependency, no new `typst_*`
config value, no `@preview` bump.

**Everything below was measured at HEAD on 2026-08-30** by the four research agents — probe builds,
real `typst.compile()` runs, file:line reads, and live PyPI / Typst Universe / GitHub / RTD API
calls — not carried over from the pending todo's prose. Where research contradicted the milestone's
own initial framing, the measurement won: PROJECT.md's `visit_target` precedent was falsified as a
**false precedent**, and the `in_figure` "hazard" was measured to be cosmetic (byte-identical PDF).
Both corrections are recorded as amendments in PROJECT.md and must not be re-litigated in planning.

**Binding constraints this roadmap is built on** (settled decisions and measured facts, not open
questions):

1. **The defect is one emitter, not a class.** Fourteen inline constructs were placed mid-sentence
   and the emitted `.typ` scanned for juxtaposed code-mode calls (`:ref:`, inline literal, emphasis,
   `:abbr:`, `:kbd:`, `:manpage:`, citation reference, `:term:`, `:index:`, `:guilabel:`, external
   link, footnote reference, `:math:`, `:download:`). Exactly **one** unseparated juxtaposition was
   found and it was the image; the survey document itself compiled OK. Auditing that family is in
   REQUIREMENTS.md's **Out of Scope** table, which is binding.

2. **The trigger surface is 16 measured shapes, not the 4 the todo recorded.** The same single root
   cause also breaks a block-level `.. image::` as the second-or-later element of a list item, a
   table cell, a definition-list body, an admonition, a footnote, a field-list body, a section
   title, and a figure's own legend body. One fix closes all sixteen; the count matters only for
   the gate. **Blast radius confirmed by measurement:** the probe's `index.rst`, which contains no
   image at all, *also* failed to compile, because Typst's `#include()` re-parses the included
   content file — one refused file poisons every master that transitively includes it.

3. **The mechanism is the existing triad, called verbatim, scoped to the non-`in_figure` branch.**
   `_add_paragraph_separator()` + `_emit_inline_concat_separator()` + the
   `in_list_item`/`list_item_needs_separator` pair, exactly as `visit_Text`, `visit_literal`,
   `visit_math`, `visit_footnote_reference` and `visit_reference` already call it, with the matching
   `_mark_inline_concat_content()` bookkeeping in `depart_image()`. Row 14 of the failing matrix (a
   field-list body) is a **concat context**, which is why the `_emit_inline_concat_separator()` half
   is required and an unconditional `"\n"` would still be a syntax error there. **No new
   line-boundary predicate**: `grep` for `endswith("\n")` / `rstrip().endswith` / `[-1:]` across
   `translator.py` returns nothing today, and REQUIREMENTS.md's Out of Scope table forbids building
   one.

4. **The gate is the fix's acceptance criterion, not a separate deliverable — and it must be RED
   against the unfixed tree before the fix lands.** The emitted string *looks* plausible; only the
   parser rejects it, which is exactly why nine existing string-level image tests in
   `tests/test_translator.py` (lines 1706–3918, none of which import `TYPST_AVAILABLE` or call
   `typst.compile()`) never saw this. A gate observed only green is tautological. The RED proof is
   the choreography Phase 59 already executed: restore `typsphinx/translator.py` from the phase base
   SHA, re-run the gate, transcribe Typst's verbatim refusal, restore the fix, record
   `git status --porcelain` empty. This is why the fix and the gate are **one phase**, not two.

5. **Zero pre-existing test edits is a measured property, not an aspiration.** The instrument is
   `git diff --name-status` scoped to `tests/` over the phase's own range: only `A` entries, no `M`
   against any of the 20 files carrying the 144 `image(` matches. Research measured this achievable
   — every non-figure `image(` assertion is a substring check, and the only two exact, position-
   sensitive matches (`tests/test_nested_figure_render_gate.py:256`,
   `tests/test_pdf_render_gate.py:2303`) are both in the untouched `in_figure` branch and were
   measured byte-unchanged under the recommended fix. If a plan finds it must edit a pre-existing
   test, that is a signal the fix over-reached, not a licence to edit.

6. **`uv.lock` must be regenerated in the same commit as the `pyproject.toml` bump.** `uv.lock`
   carries its own `version = "0.9.0"` literal for the self-package (line 1467) independent of
   `pyproject.toml:7`. Omitting the regeneration reproduces the exact `uv sync --extra dev --locked`
   refusal already killing every dependabot PR in this repository across **eleven** CI steps — and
   it would fail at the *install* step of `release.yml`'s `validate`/`build` jobs on the real tag
   push, before any test runs. `uv.lock` is regenerated with `uv lock`, never hand-edited.

7. **The CHANGELOG scratch block is relocated BEFORE the heading is renamed, and the extractor is
   executed and its output inspected.** `scripts/extract_changelog_section.py` selects by
   **position** — first `## [<version>]` line, everything up to the next `## [...]` of any name — so
   renaming `## [Unreleased]` in place would carry the nested `### Planned for Future Releases`
   scratch block verbatim into the published GitHub Release body. REL-10 is closed by running the
   script and reading its stdout, not by reasoning that the edit was correct.

8. **Phase 63 is prep-only and takes zero irreversible action.** No tag (local or remote), no PyPI
   upload, no GitHub Release, no PR. This is the standing pattern held for eight consecutive
   milestones (Phases 10, 41, 46, 52, 57, 61). **REL-09 closes at `/gsd-complete-milestone`, not in
   the phase** — it is held at `[ ]` through every plan and cited for coverage purposes only, exactly
   as v0.9.1's Phase 61 held it.

9. **REL-11's checksum fence is required, and it is the only measure that has ever worked.**
   `phase.complete` has auto-flipped the release requirement to `[x]` against the CONTEXT's explicit
   decision at **five consecutive** release-prep closes (Phases 41, 46, 52, 57, and the one before);
   v0.9.1's Phase 61 was the first to hold, via `61-CLOSEOUT-GUARD.md`. Reuse that procedure
   verbatim: SHA-256 + `wc -l` + `git rev-parse HEAD` recorded at phase head, re-verified at phase
   close, **and re-verified once more after `phase.complete`-family tooling runs** — that third
   observation is the one that actually catches the flip, because it runs outside any plan's reach.
   A second, subtler hazard the v0.9.1 audit found: three of Phase 61's four plans declared
   `requirements-completed: [REL-09]` in their SUMMARY frontmatter, contradicting the correctly
   unmet checkbox. Every plan in Phase 63 declares `requirements-completed: []` for REL-09.

10. **The milestone branch reaches `origin` in the FIRST phase** (milestone invariant #5, adopted
    v0.7.1; its absence cost v0.7.0 two defects found only at the release PR). Evidenced by a
    **completed CI run** including the `windows-latest` and `macos-latest` lanes, dispatched with
    `gh workflow run CI --ref <branch>` — `ci.yml`'s push/PR triggers are scoped to `main`/`develop`,
    so a push alone runs no CI. **The decoy pair fired again and has already been resolved
    (2026-08-30, before this roadmap was committed).** The roadmapper measured
    `gsd/v0.9.2-inline-image-blocker-fix-and-release` (the canonical name, derived from
    `config.json`'s `git.milestone_branch_template`) at `d75ea6dd` while the decoy
    `gsd/v0.9.2-milestone` sat at `1e4ea286`, three commits further ahead and carrying HEAD — the
    **mirror image** of v0.9.1's case, where the decoy was the stale pointer. Because the two were
    strictly linear, the canonical ref was fast-forwarded to `1e4ea286` and HEAD re-pointed at it
    with `git symbolic-ref` (no checkout, so the roadmapper's uncommitted files survived), and only
    then was the decoy deleted — `Deleted branch gsd/v0.9.2-milestone (was 1e4ea286)`, zero commits
    orphaned. **Current state:** one branch, `gsd/v0.9.2-inline-image-blocker-fix-and-release` at
    `1e4ea286`, HEAD on it, no decoy. It is still local-only: nothing matching `0.9.2` exists on
    `origin` and no `v0.9.2` tag exists anywhere, so SC#5's push and CI dispatch are still owed.
    Expect the decoy to be re-created by the next `gsd-tools query commit` — it is a per-milestone
    recurrence, not a one-off.

11. **CI holds lint authority.** `ruff` is unrunnable on this machine in a freshly
    `uv sync --extra dev`-provisioned worktree venv — the exact provisioning `CLAUDE.md` mandates —
    failing with `Could not start dynamically linked executable: ruff` / exit 127, reproduced as
    recently as 2026-08-22. A green `black --check .` + `mypy typsphinx/` is **not** "lint clean".
    Either run `nix run nixpkgs#ruff -- check .` or take the verdict from a dispatched `ci.yml`
    run's **`Lint and Format Check`** job — whose one step, **`Run lint with tox`** (`ci.yml:69`),
    runs `uv run tox -e lint` = `black --check .` + `ruff check .`. `ci.yml` carries no step named
    `Run linters`; that name exists only at `release.yml:84`, which prep-only phases must never
    trigger (measured 2026-08-30; Phase 62's executor hit the same mismatch and recorded it as a
    paraphrase in `62-RED-EVIDENCE.md`). Compounding: the post-merge wave gate runs `pytest` only,
    so a lint-breaking file can merge on a green pytest.

12. **Worktree isolation is the standing execution mode** (owner decision, `CLAUDE.md`). Every
    executor provisions its own venv with
    `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` and runs everything via
    `uv run`. Do **not** degrade to sequential main-tree execution merely because a phase has low
    parallelism benefit.

13. **Standing invariants carried forward:** zero new runtime *and* dev dependencies (research
    verified every element of the stack already current against PyPI and Typst Universe on
    2026-08-30, and the gate idiom needs nothing `typst-py` does not already provide); no new
    `typst_*` config value; the `@preview` package count stays at **four** with no version change,
    so `tests/test_preview_version_sync.py` is already green and stays green; typing-import
    modernization is forbidden (`CLAUDE.md` independently instructs it); **no `## [0.9.1]` heading
    and no `[0.9.1]` tail link are ever created**, because no such release exists; new test files
    read `.typ`/`.pdf` output with an explicit `encoding="utf-8"` (v0.7.1 lost a Windows lane to a
    bare `Path.read_text()`); and every phase closes green on the full pytest suite.

14. **Not a frontend UI milestone** (standing project note): both phases are translator, test and
    release work. `ui.plan-gate` false-positives on words this milestone cannot avoid — "image",
    "render", "figure", "page", "legend". Each phase detail therefore carries an explicit
    `**UI hint**: no` line, the authoritative override `ui-safety-gate.cjs` reads, rather than
    relying on a per-run `--skip-ui`.

**`research/SUMMARY.md`'s suggested three-phase A/B/C structure is adopted as two phases, not
three.** Its Phase A (fix + gate) is Phase 62 unchanged — the research's own rationale for keeping
them together is constraint 4 above. Its Phase B (release-prep) is Phase 63. **Its Phase C
(publish) is deliberately not a phase**: this project's established convention, held for eight
consecutive milestones under `branching_strategy: milestone`, is a prep-only final phase that takes
zero irreversible action, with the tag push, PyPI upload, GitHub Release, `typsphinx-doc-translations`
`update-pin.yml` dispatch and RTD `stable` verification all executed at `/gsd-complete-milestone`.
Every step research listed under its Phase C is preserved as Phase 63's handoff checklist (SC#5), so
nothing is lost — only relocated to where this project actually performs it.

- [x] **Phase 62: The `visit_image()` Separator Fix and Its Real-Compile Gate** - An image node preceded by any sibling content in the same container is separated before `image(` by the same triad every other inline emitter already uses, proven by a gate that drives a real `typst.compile()` over all 16 measured failing shapes and all 9 that must keep passing, recorded RED against the unfixed tree first (completed 2026-08-30)
- [ ] **Phase 63: v0.9.2 Release Prep (prep-only)** - The tree is bumped to 0.9.2 in one commit carrying `pyproject.toml`, a regenerated `uv.lock`, `README.md` and a curated `## [0.9.2]` CHANGELOG entry whose extracted body was read rather than assumed, behind a checksum fence on the release checkbox and with zero irreversible action taken

## Phase Details

### Phase 62: The `visit_image()` Separator Fix and Its Real-Compile Gate

**Goal**: `sphinx-build -b typstpdf` produces a PDF for every master document of a project that
places an image anywhere other than first in its container. `visit_image()`'s non-`in_figure` branch
joins the separator discipline the rest of the translator already runs on, and the proof is a real
`typst.compile()` over the whole measured trigger matrix — not a string assertion, which is what let
this survive every suite to date.

The fix and its gate are one phase by constraint 4: splitting them buys nothing and risks a phase
boundary at which "fixed" is claimed before "proven by a real compile". This is also the first phase
of the milestone, so it carries the branch-to-`origin` invariant (constraint 10).

**Depends on**: Nothing (first phase of the milestone)
**Requirements**: IMG-08, IMG-09, IMG-10, TEST-05
**Success Criteria** (what must be TRUE):

  1. **A project containing every failing shape builds a PDF for every one of its masters.** One
     fixture project carrying all **16** measured failing shapes builds under
     `sphinx-build -b typstpdf` with `returncode == 0`, `"Typst compilation failed"` absent from
     stderr, and a non-empty file beginning with the `%PDF` magic bytes written for **every** master
     — including the master that contains no image at all and fails today only because Typst's
     `#include()` re-parses a poisoned content file. Today this project raises `ExtensionError` and
     writes no PDF for any master.

  2. **The gate was RED against the unfixed tree, and the RED is transcribed.** Before the fix
     lands, `typsphinx/translator.py` is restored from the phase base SHA
     (`git checkout $PHASE_BASE_SHA -- typsphinx/translator.py`), the gate is re-run, and Typst's
     verbatim refusal — `expected semicolon or line break` — is transcribed into the phase's
     evidence file for each failing shape; the fix is then restored and `git status --porcelain`
     recorded empty, proving the restore was byte-identical. The gate module itself greps positive
     for `typst.compile` / `TYPST_AVAILABLE`. A gate observed only green does not satisfy this
     criterion, however many assertions it carries.

  3. **All 9 must-keep-passing shapes still pass, and the fix stayed inside its branch.** The same
     fixture carries the standalone block-level `.. image::`, the `.. figure::`, the image first in
     its paragraph, the image with `:width:`/`:height:`/`:scale:`/`:align:`, the image receiving a
     propagated explicit target's id, the figure with a legend, the figure nested in a list item,
     the figure first in a list item, and the bare image first in a list item — all compiling. The
     phase diff shows `visit_image()`'s `in_figure` branch unmodified; a repo-wide `grep` for
     `endswith("\n")` / `rstrip().endswith` / `[-1:]` over `typsphinx/translator.py` still returns
     nothing; and the two exact-byte figure assertions
     (`tests/test_nested_figure_render_gate.py:256`, `tests/test_pdf_render_gate.py:2303`) pass
     unedited.

  4. **Zero pre-existing test edits, measured rather than asserted.**
     `git diff --name-status` over this phase's own range, scoped to `tests/`, shows only `A`
     (added) entries — no `M` against any of the 20 files carrying the 144 `image(` matches, and in
     particular none against the nine string-level image tests in `tests/test_translator.py`. Any
     `M` entry is reported as an over-reach signal with its justification, never absorbed as routine
     test maintenance.

  5. **The milestone branch is on `origin` with a completed 3-OS CI run.**
     `gsd/v0.9.2-inline-image-blocker-fix-and-release` — the canonical, config-derived name; see
     constraint 10 for the live decoy pair and the pointer-advance that must precede any deletion —
     is pushed and tracking, and a run dispatched with `gh workflow run CI --ref <branch>` has
     **completed**, with the `windows-latest` and `macos-latest` lanes named individually and green,
     and `ruff`'s verdict taken from that run's `Lint and Format Check` job (step `Run lint with
     tox`) rather than from this machine.

**Plans**: 4/4 plans executed

Plans:
**Wave 1**

- [x] 62-01-PLAN.md — Tracer: one failing shape end to end (3-master fixture, the separator triad fix, a real-compile gate) plus the milestone branch to `origin`

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 62-02-PLAN.md — Expand to the full measured matrix: 16 FAIL + 9 PASS documents, 18 masters, 27 documents, and the widened gate

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 62-03-PLAN.md — RED-first evidence against a restored unfixed tree, the 9 committed goldens, and the byte-identity binding

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 62-04-PLAN.md — The single authority 3-OS CI run and the phase-close measurements (zero test edits, `in_figure` bodies untouched, release fence held)

**Planning note (2026-08-30):** two locked decisions were falsified by measurement during planning and
are AMENDED in `62-01-PLAN.md`'s `<amendments>` block. (1) The triad scoped to `visit_image()`'s
non-`in_figure` branch alone leaves 3 of the 16 FAIL shapes broken (both legend shapes, because a
legend image has `in_figure` true; and the field-list body, where the trailing newlines break the
concat expression with a NEW `cannot apply unary '+' to content` refusal); the leading half is
therefore hoisted above the figure/non-figure split and the trailing half made concat-aware — measured
18/18 masters compiling, with both branch bodies still textually unmodified, so SC#3's literal check
holds. (2) 8 of the 9 must-keep-passing shapes are byte-identical, not 9: an image first in its
paragraph gains exactly one empty line. D-06 is not weakened to "compiles" — that shape is bound by
two committed goldens and an exact-delta assertion.

**UI hint**: no

### Phase 63: v0.9.2 Release Prep (prep-only)

**Goal**: the 0.9.2 tree is bumped, its CHANGELOG curated into a single `## [0.9.2]` entry covering
both v0.9.1's accumulated bullets and this milestone's fix, the extracted release body read rather
than assumed, and the whole thing handed off — with **zero irreversible action**. No tag, local or
remote; no publish; no GitHub Release; no PR.

v0.9.2 is a **patch release with no breaking change**: no new capability, no new runtime or dev
dependency, no new `typst_*` config value. The CHANGELOG entry describes v0.9.1's three Windows
path defect families (PATH-01, IMG-04..IMG-07, MSG-01..MSG-05) *and* the inline-image blocker as
user-visible fixes under one heading, because 0.9.1 is a version users will never see.

**Depends on**: Phase 62
**Requirements**: REL-09, REL-10, REL-11
**Success Criteria** (what must be TRUE):

  1. **The version moves to 0.9.2 in one commit touching all four files.**
     `git show --name-only` on the bump commit lists `pyproject.toml`, `uv.lock`, `README.md` and
     `CHANGELOG.md` together — a commit touching only `pyproject.toml` is the exact shape currently
     killing every dependabot PR. `pyproject.toml:7` is the sole hand-edited literal; `uv.lock`'s
     `typsphinx` stanza reads `0.9.2` because `uv lock` regenerated it; `README.md`'s Status line
     reads `v0.9.2`; `uv sync --extra dev --locked` exits 0 against the bumped tree; and
     `tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject` is green.

  2. **The extractor was run and its output inspected.**
     `scripts/extract_changelog_section.py 0.9.2` is executed and its stdout transcribed into the
     phase evidence: it is non-empty, reproduces the `## [0.9.2]` section byte-for-byte, and
     contains **no** `Planned for Future Releases` line — because that scratch block was relocated
     under a fresh, empty `## [Unreleased]` heading placed *above* `## [0.9.2]` before the rename,
     not after. `grep` confirms no `## [0.9.1]` heading and no `[0.9.1]` tail link exist anywhere in
     `CHANGELOG.md`, and the tail block carries a new `[0.9.2]` release/tag link with the
     `[Unreleased]` compare base advanced from `v0.9.0` to `v0.9.2`.

  3. **The release-checkbox fence is proven held by a recorded SHA-256.** A
     `63-CLOSEOUT-GUARD.md` records `sha256sum .planning/REQUIREMENTS.md`, `wc -l`, the
     `PHASE_BASE_SHA`, and the verbatim guarded lines (`grep -n 'REL-09'`) at phase head; the same
     three commands re-run MATCH at phase close **and once more after `phase.complete`-family
     tooling has run** — the observation that actually catches the flip, because it runs outside any
     plan's reach. Every plan's `SUMMARY.md` frontmatter declares `requirements-completed: []` for
     REL-09, and REL-09's checkbox is read directly out of `.planning/REQUIREMENTS.md` as `[ ]` at
     close, never inferred from frontmatter.

  4. **The bumped tree is proven green on runs executed in this phase, not on the preceding
     phase's word.** Full pytest suite, `black --check .`, `mypy typsphinx/`, both docs tox
     environments against a warning baseline taken from a **clean** build (`rm -rf docs/_build`
     first — an incremental rebuild under-reports warnings and manufactures a false "baseline
     match"), and one fresh 3-OS CI run dispatched on the **bumped** tip with every job conclusion
     transcribed literally, both `windows-latest` lanes named, and `ruff` green in that run's
     `Lint and Format Check` job (its one step, `Run lint with tox`, runs `tox -e lint` =
     `black --check .` + `ruff check .`; `ci.yml` carries no step named `Run linters`).

  5. **Zero irreversible action, probed twice, and the handoff is standalone.** `git tag -l 'v0.9.2'`
     and a remote tag probe both come back empty, with a positive control on each remote probe, at
     two observations separated by intervening waves rather than by wall-clock luck; no PyPI upload
     and no GitHub Release exist; `git diff` over the phase shows no unintended change under
     `typsphinx/`. A `63-HANDOFF.md` enumerates every step `/gsd-complete-milestone` must execute:
     the `v0.9.2` tag push, the expected manual approval of the `pypi` GitHub Environment (an
     expected gate, not a failure), the GitHub Release body being byte-identical to
     `scripts/extract_changelog_section.py 0.9.2`'s stdout, the `typsphinx-doc-translations`
     `update-pin.yml` dispatch (a manual dispatch — it does not happen as a side effect of the
     parent repo's tag push), and the Read the Docs `en` and `ja` `stable` endpoints reporting
     `0.9.2`.

**Plans**: 3/4 plans executed across 3 waves

Plans:
**Wave 1**

- [x] 63-01-PLAN.md — Bump the version literal, lockfile and README, promote `## [Unreleased]` into a curated `## [0.9.2]` section in the load-bearing four-step order, extend `RELEASE_VERSIONS`, and prove it by running the extractor and reading its stdout (wave 1, tracer-led)
- [x] 63-02-PLAN.md — Record the phase-head REL-09 checksum fence with its PHASE_BASE_SHA anchor and the three-observation protocol, take SC#5 fence observation 1 of 2 with positive controls, and write the external-API coverage declaration (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 63-03-PLAN.md — Prove the bumped tree green on runs executed in this phase (full suite, format, type, version-sync, both docs builds from a clean build directory) and dispatch one 3-OS CI run on the bumped tip, taking `ruff`'s verdict from the `Lint and Format Check` job (wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 63-04-PLAN.md — Take SC#5 fence observation 2 of 2 with the scoped/widened `typsphinx/` diff pair, re-verify the checksum fence at phase close, and author the standalone `63-HANDOFF.md` (wave 3)

**Cross-cutting constraints** *(truths any plan in this phase must carry)*:

- REL-09 is cited by every plan as a coverage ID **only**. No plan closes it and no plan touches its
  checkbox; per constraint 8 it stays `[ ]` and closes at `/gsd-complete-milestone`. This is the
  same handling v0.9.1's Phase 61 used, with the correction the v0.9.1 audit named: the
  `requirements-completed: []` declaration is required in **every** plan's frontmatter, not one.

- `release.yml`'s `create-release` job is **confirmed fixed** for the `uv: command not found` failure
  that killed the v0.7.0 tag push (explicit `Install uv` steps present at HEAD; ran green at the
  v0.8.0 and v0.9.0 real tag pushes). Per PROJECT.md's binding constraint 7, a failure at the real
  v0.9.2 tag push is handled inside this release work rather than deferred — but it is not a
  requirement of this milestone, and REL-04 stays out of scope.

**UI hint**: no

## Progress

**Execution Order:**
Active milestone phases execute in numeric order (decimal insertions between their surrounding
integers), with the prep-only Release phase last so its CHANGELOG entry describes work already
proven by the preceding phase's gate. v0.9.2 executes **62 → 63**, and that single arrow is a real
dependency, not a convention: the `## [0.9.2]` entry must describe a fix that has actually landed
and been proven by a real compile, and the version bump must not be in the tree while the fix is
still being RED/GREEN-proved against a restored pre-fix `translator.py`.

Phases 1–61 shipped or completed across v0.4.4 → v0.9.1; their per-phase plan counts, statuses and
completion dates are preserved in each milestone's archived roadmap under `milestones/`. The table
below tracks the active milestone only.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 62. The `visit_image()` Separator Fix and Its Real-Compile Gate | v0.9.2 | 4/4 | Complete | 2026-08-30 |
| 63. v0.9.2 Release Prep (prep-only) | v0.9.2 | 3/4 | In Progress | - |

## Roadmap Evolution

Per-milestone evolution notes are archived with their milestone. v0.9.1's — the three structural
decisions baked into the 58–61 phase split, the `gsd/v0.9.1-milestone` decoy-branch correction, and
the deliberate decision to give the 3-OS matrix run no REQ-ID — live in
[milestones/v0.9.1-ROADMAP.md](milestones/v0.9.1-ROADMAP.md).

- **2026-08-30** — v0.9.2 roadmap created: **Phases 62–63**, 7/7 v1 requirements mapped, zero
  orphans, continuing numbering from v0.9.1's Phase 61. Two phases at `granularity: standard`, which
  nominally suggests 4–6 — deliberately under-shot, because this milestone has exactly two aims and
  padding it would manufacture the thin phases the granularity guidance itself warns against. Four
  decisions are baked into the structure and should not be re-derived during planning:

  - **The fix and its gate are one phase** (62), following `research/ARCHITECTURE.md`'s own Q5
    recommendation and its stated reason: a phase boundary between them would let "fixed" be claimed
    before "proven by a real compile", which is the precise failure mode that let this defect ship
    in 0.9.0. TEST-05 is therefore mapped to Phase 62, the phase that writes the gate, rather than
    carried as a cross-cutting milestone obligation.

  - **`research/SUMMARY.md`'s Phase C (publish) is not a phase.** This project's prep-only
    convention — eight consecutive milestones, most recently Phase 61 — puts every irreversible
    action at `/gsd-complete-milestone`. Research's Phase C content survives in full as Phase 63's
    SC#5 handoff checklist. **REL-09 therefore closes at `/gsd-complete-milestone`, not inside any
    phase**, and is mapped to Phase 63 for coverage purposes only.

  - **REL-10 is folded into the release-prep phase rather than given its own.** It is a CHANGELOG
    edit ordering constraint (relocate the scratch block, *then* rename the heading) plus one
    command whose output must be read — a plan-sized unit inside Phase 63, not a delivery boundary.

  - **The 3-OS matrix run and the branch-to-`origin` invariant were deliberately given no REQ-ID**,
    matching v0.9.1's own decision. They remain the milestone's acceptance bar and are carried in
    the success criteria of both phases (62 SC#5, 63 SC#4), where they are checked rather than
    merely intended.

- **2026-08-30** — **The `gsd/v0.9.2-*` decoy pair is live and inverted relative to v0.9.1's.**
  Measured at roadmap time: the canonical config-derived branch
  `gsd/v0.9.2-inline-image-blocker-fix-and-release` is at `d75ea6dd` (`main` + 2), while
  `gsd/v0.9.2-milestone` is at `1e4ea286` (canonical + 3) and is where HEAD sits. Strictly linear —
  the canonical branch is an ancestor of the decoy, so nothing has diverged and nothing is lost. But
  v0.9.1's correction ran the other way (the decoy was the empty pointer and was safely deleted),
  and repeating that action here **would orphan three commits**. The canonical pointer must be
  fast-forwarded to `1e4ea286` before `gsd/v0.9.2-milestone` is deleted. Phase 62 carries the push
  as SC#5; every later phase inherits it.

- **2026-08-30** — Two of PROJECT.md's own target-feature claims were **falsified by research and
  amended in place** before this roadmap was written, and both amendments are load-bearing here.
  (1) The named precedent for the fix was `visit_target`; that is a **false precedent** — its
  unconditional `\n[#metadata(none) <id>]\n` is markup-mode zero-width content that Typst joins to
  anything on either side, not a code-mode function-call operand like `image(...)`. The real
  precedent is the triad five other inline visitors drive (constraint 3). (2) The `in_figure`
  suppression was stated as a hazard the fix "must not violate"; measured, a newline injected inside
  a `figure(...)` argument list compiles to a **byte-identical PDF** — insignificant whitespace, not
  a syntax error. The branch is still left alone, but as minimum-diff discipline, not as a
  constraint the fix could break. Neither correction is to be re-litigated during planning.

## Backlog

Candidate work not yet scoped into a milestone. Promote items with `/gsd-review-backlog`, or
pull a whole cluster into the next milestone via `/gsd-new-milestone`.
Numbered 999.x so milestone reorganization never renumbers or drops them.

New items land here as `999.x` entries. **No item is open** — the backlog has been empty since
2026-08-04. Item **999.1** (inline math after text: missing separator before `#mi()` causes a Typst
error) was promoted into v0.6.5 as Phase 34 / requirement MATH-01 and shipped 2026-07-29. Item
**999.2** (a captioned table drops the id of an immediately preceding standalone target) was promoted
into v0.7.0 as **Phase 42 / requirement TBL-03** and shipped in v0.7.0. Numbering does not reuse
retired numbers, so the next item filed here is **999.3**.

**Todos and seeds promoted into v0.8.0** (2026-08-11) — the three-defect `typst_documents`-modelling
cluster the v0.7.1 close named first among next-milestone candidates, plus the two image defects that
shipped in v0.7.1 unfixed by owner decision D-27:

- `shared-document-silently-dropped-from-all-but-first-master` → Phase 49 (defect A: COMP-07, and the
  whole COMP-05..COMP-12 include-graph set that closes it)

- `a-master-that-is-also-a-toctree-child-is-unrepresentable` → Phase 47 (B-1: COMP-03)
- `duplicate-typst-documents-target-silently-drops-a-master` → Phase 47 (BLD-02) — re-measured live in
  Phase 46 and still reachable, because Phase 44's guard compares only against `env.found_docs` and
  the reserved `_template`, never against already-resolved targets

- `rehomed-converted-image-collides-with-srcdir-images-dir` → Phase 50 (IMG-01, major — a regression
  in failure mode: the same project used to abort loudly)

- `track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri` → Phase 50 (IMG-02, minor)

Each todo record stays **pending** until its phase executes; the todo is the detail record, the phase
entry above is the sequencing record.

**Still open and deferred, not in v0.8.0 scope:**

- `modernize-typing-imports-drop-up006-up035-ignore` — deferred *doubly deliberately*, since
  `CLAUDE.md` independently instructs "don't modernize typing imports until that todo lands", and
  binding constraint #9 forbids it this milestone.

- `add-sphinx-linkcheck-ci-job` — tracked as Future requirement LNK-01; `links.yml`'s repo-wide
  lychee check already covers the links each release adds.

- `ruff-generic-linux-elf-unrunnable-on-nixos` — a `flake.nix`-side toolchain repair in the same
  family as QUA-04 (Future requirement QUA-06); CI holds lint authority, so it blocks nothing.

- Dormant seeds: `SEED-001-readme-quickstart-typst-documents-pdf` (substantially discharged by v0.7.1's
  CONF-08 + DOC-11) and `SEED-003-tox-dependency-groups-per-env` (Future requirement QUA-07).

**Todos and seeds promoted into v0.9.0** (2026-08-15) — the five v0.8.0-derived defects that shipped
unfixed by decision D-01 or with only a test-side fix, all closed on the product side by Phase 55:

- `label-collision-false-negative-in-compile-time-xref-guard` → Phase 55 (XREF-05)
- `include-edge-key-separators-unescaped-two-edges-can-collide` → Phase 55 (BLD-07)
- `unbounded-recursion-in-derive-master-edge-keys` → Phase 55 (BLD-08)
- `escape-branch-relocation-key-uses-basename-only-two-escaping-images-can-collide` → Phase 55 (IMG-03)
- `track-image-isabs-not-drive-aware-on-py313-windows` → Phase 55 (BLD-09)

**Todos promoted into v0.9.1** (2026-08-27) — the three path-handling records Phase 57's prep-only
fence held back, each now carrying a REQ-ID and a phase:

- `2026-08-16-escapes-outdir-isabs-not-backslash-normalized` → Phase 59 (**PATH-01**). Re-measured at
  roadmap time: **not reachable from either production call site**, because both pre-normalize. Kept
  in scope deliberately as hardening of the function's own contract — a future third call site would
  inherit the gap silently — with the standing instruction that its gate call `_escapes_outdir()`
  directly, since an integration test through either call site is tautologically green.

- `2026-08-16-track-image-escape-branch-basename-not-normalized` → Phase 59 (**IMG-04**), together
  with its two never-filed siblings scoped in alongside it: the unescaped `image("...")` emission
  (**IMG-05**) and the unbounded key length (**IMG-06**). IMG-04 and IMG-05 are coupled by Typst's
  value-level backslash refusal, so the real-compile gate (**IMG-07**) closes both at once.

- `2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages` → Phase 60 (**MSG-02** through
  **MSG-05**), with its test-side prerequisite split out as **MSG-01** in Phase 58. This record
  carries **both** halves of the defect — the `!r` backslash-doubling at the sites 57-11 left alone,
  and 57-REVIEW WR-01's fixed-`'...'` delimiter that closes early on a path containing a single
  quote — and one delimiter-aware helper closes both.

Each todo record stays **pending** until its phase executes; the todo is the detail record, the phase
entry above is the sequencing record.

**Still open and deferred after the v0.9.0 close** (2026-08-22), and **not** in v0.9.1 scope — full
dispositions in
`.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-HANDOFF.md`
§ "Deferrals carried forward", and one row each in STATE.md's Deferred Items ledger:

- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos` — **kept open with a live 2026-08-22
  recurrence annotated**, which falsified v0.9.0's own 2026-08-16 "ruff works here" measurement. The
  main tree's stale binary masks it; only a freshly-provisioned venv reproduces it. Tracked as Future
  requirement QUA-06. CI holds lint authority, so it blocks nothing — including this milestone's
  worktree-isolated executors.
- `2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch` — `severity: major`; its `--locked`
  census is what made v0.9.0's D-13 sequencing constraint concrete. Tracked as a Future CI requirement.
- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar` — an HTML sidebar defect in
  this project's own docs.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures` — still
  excluded from every published surface by owner override D-07.
- `2026-08-04-release-create-job-missing-uv-verify-end-to-end` — REL-04's own record, whose acceptance
  criteria were met at the v0.7.1 publish and again at v0.8.0 and v0.9.0. Raised for the third close
  with the settling measurement attached; the disposition is the owner's.
- `2026-07-22-add-sphinx-linkcheck-ci-job` (Future LNK-01) and
  `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore` (forbidden by `CLAUDE.md` until the
  todo itself lands) — both deferred again.
- Dormant seeds: `SEED-001-readme-quickstart-typst-documents-pdf`,
  `SEED-003-tox-dependency-groups-per-env` (Future QUA-07), and **`SEED-004-typst-py-maintenance-risk-vendored-compile-path`**
  — `typst-py` upstream maintenance is slowing and typsphinx may eventually need to carry an
  equivalent compile path. The largest structural risk on the horizon; never scoped into a milestone,
  and explicitly not scoped into this bug-fix round either.

**Known limitations shipped in v0.9.0**, deferred by owner decision with no published surface:
WR-02 (`templates_path` resolved against `srcdir`, not `confdir`, so `-c`/confdir projects keep the
republication hole — shipped *silent*, making the CHANGELOG's validation sentence read
unconditional) and the tripled "Custom template not found" warning; both are carried forward as v2
requirements and are **not** in v0.9.1 scope. The third — the fixed-`'...'`-delimiter path quoting —
**is** closed this milestone, by MSG-02's delimiter-aware helper.

**Closed by v0.9.1** (2026-08-30) — the three records promoted above all executed:
`2026-08-16-escapes-outdir-isabs-not-backslash-normalized` (PATH-01),
`2026-08-16-track-image-escape-branch-basename-not-normalized` (IMG-04), and
`2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages` — **both** halves, by MSG-01
through MSG-05.

**Filed during v0.9.1 and open** (2026-08-30), both in `translator.py`, neither in that milestone's
requirement scope:

- `2026-08-29-inline-image-in-paragraph-emits-unseparated-expression` — `severity: blocker`, and
  **the single strongest candidate for the next milestone**. An image node that is not the first
  thing in its paragraph is emitted adjacent to the preceding code-mode expression, so Typst refuses
  the file with `expected semicolon or line break` and `-b typstpdf` raises `ExtensionError`
  rather than degrading — **no PDF is produced for any master document in the project**. Owner-
  reported 2026-08-29 and root-caused the same day; measured **pre-existing, not a v0.9.1
  regression** (D-06), so it is live in the published 0.9.0. It is the reason v0.9.1 was never
  released (D-02), was deliberately not fixed in that milestone (D-07), and has **no public-surface
  disclosure** (D-05).
- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs` —
  `severity: minor`. `translator.py`'s two relative-path DEBUG logs carry the same
  hardcoded-`'...'`-delimiter shape Phase 60 closed in three other modules; found by that phase's own
  repo-wide discovery grep and filed rather than fixed, being a fourth module outside
  MSG-02..MSG-05's scope. The one-line fix is `quote_path()`, which now exists.

**Still open and deferred after the v0.9.1 close** (2026-08-30), one row each in STATE.md's Deferred
Items ledger: `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos` (Future QUA-06),
`2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch` (`severity: major`),
`2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar`,
`2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures` (still
excluded from every published surface by D-07),
`2026-08-04-release-create-job-missing-uv-verify-end-to-end` (untestable at this close, since
nothing was published), `2026-07-22-add-sphinx-linkcheck-ci-job` (Future LNK-01),
`2026-07-22-modernize-typing-imports-drop-up006-up035-ignore` (forbidden by `CLAUDE.md` until the
todo itself lands), and the three dormant seeds — SEED-001, SEED-003 (Future QUA-07) and
**SEED-004** (`typst-py` upstream maintenance slowing; the largest structural risk on the horizon,
never scoped into any milestone across three consecutive closes).

**Known limitations still shipped with no published surface** after v0.9.1: WR-02's `confdir` gap
and the tripled "Custom template not found" warning, both carried unchanged from v0.9.0, joined now
by the inline-image blocker. That is the **fourth consecutive** cycle at which a
`### Known Limitations` section was declined.

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29), v0.7.0 (2026-08-04), v0.7.1 (2026-08-11), v0.8.0 (2026-08-15), v0.9.0 (2026-08-22), v0.9.1 (2026-08-30 — completed, not published). Per-milestone phase detail, success criteria, and decisions for completed milestones live in `milestones/vX.Y-ROADMAP.md`. Active milestone: v0.9.2 (Phases 62–63), roadmap created 2026-08-30.*
