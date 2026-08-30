# Phase 63: v0.9.2 Release Prep (prep-only) - Context

**Gathered:** 2026-08-30
**Status:** Ready for planning

<domain>
## Phase Boundary

The tree is bumped to 0.9.2 in one commit carrying `pyproject.toml`, a regenerated `uv.lock`,
`README.md` and `CHANGELOG.md`; `CHANGELOG.md`'s `## [Unreleased]` becomes a single curated
`## [0.9.2]` entry covering both the Windows-path work completed in v0.9.1 and this milestone's
inline-image blocker fix; `scripts/extract_changelog_section.py 0.9.2` is executed and its stdout
read rather than assumed; the bumped tree is proven green on runs executed **in this phase**; the
REL-09 checkbox is held at `[ ]` behind a recorded SHA-256 fence; and everything is handed off with
**zero irreversible action**.

**No irreversible action of any kind.** No tag (local or remote), no PyPI upload, no GitHub
Release, no PR, no `update-pin.yml` dispatch on the translations repository, no RTD re-flip. Every
one of those executes at `/gsd-complete-milestone` and is *recorded* here as `63-HANDOFF.md`, never
performed. This is the standing prep-only pattern held for eight consecutive milestones
(Phases 10, 41, 46, 52, 57, 61).

**Not in this phase:** any `typsphinx/` behaviour change; any new `typst_*` config value; any new
runtime or dev dependency; any `@preview` version bump; any `## [0.9.1]` heading or `[0.9.1]` tail
link, ever. REQUIREMENTS.md's Out of Scope table is binding and is the answer to any "while we're in
here" impulse.

</domain>

<decisions>
## Implementation Decisions

The owner selected **"おすすめ"** — all four presented gray areas were delegated at once, exactly as
in Phase 62. Every decision below is Claude's measured recommendation, accepted en bloc. Each is
grounded in a measurement taken during this discussion against the tree at `dd385436`, not in prior
prose. The measurements are quoted inline so a downstream agent can re-run them rather than trust
them.

### The `## [0.9.2]` CHANGELOG entry

- **D-01: The entry opens with a lead paragraph.** Measured across the whole file: every one of the
  last nine released sections — `0.6.1`, `0.6.2`, `0.6.3`, `0.6.4`, `0.6.5`, `0.7.0`, `0.7.1`,
  `0.8.0`, `0.9.0` — opens with one. The closest structural analog is **`## [0.6.5]`**
  (`CHANGELOG.md:381`): a hotfix patch release whose entire content is one compile-blocking
  *separator* defect in `typsphinx/translator.py` (MATH-01) — the same defect class as this
  milestone's IMG-08. Its lead paragraph names the defect, scopes the runtime change to the
  translator, and states "Zero new runtime dependencies; the bundled `@preview` version-sync surface
  is untouched." That is the model to follow. — **Reversibility:** reversible.

- **D-02: The lead paragraph never names "0.9.1".** The entry describes the Windows-path work as
  part of 0.9.2's own content, with no reference to a version that was completed but never
  published. Naming a version a user cannot install, in a document published on Read the Docs via
  `docs/source/changelog.rst:1-2`, contradicts PROJECT.md's core value that a URL the project
  publishes must actually resolve — the same reasoning that produced 61-CONTEXT D-01/D-04. This is
  the prose counterpart of REQUIREMENTS.md's binding ban on a `## [0.9.1]` heading and a `[0.9.1]`
  tail link. — **Reversibility:** reversible.

- **D-03: The inline-image blocker leads the `### Fixed` list; the three path bullets follow in the
  roadmap's own order** (PATH-01 → IMG-04..IMG-07 → MSG-02..MSG-05). Rationale, measured: the image
  defect refuses **every master** of any project containing an image anywhere but first in its
  container — including masters with no image at all, because Typst's `#include()` re-parses the
  included content file (ROADMAP constraint 2, proven by 62's 17-red/1-green aggregate
  `ExtensionError`). Its blast radius is platform-independent and unconditional; the path family's
  is Windows-shaped paths plus any path containing a quote character. Broader blast radius leads.
  — **Reversibility:** reversible.

- **D-04: The three existing `## [Unreleased]` bullets are promoted verbatim, not rewritten.**
  Measured: `CHANGELOG.md:10-36` holds exactly three `### Fixed` bullets (PATH-01;
  IMG-04..IMG-07; MSG-02..MSG-05), authored in Phase 61 specifically for this promotion
  (61-CONTEXT D-03, `61-CHANGELOG-EVIDENCE.md`, 61-HANDOFF § "What v0.9.2 must also pick up"). They
  are already published on RTD `latest`. Rewriting them would create a gratuitous diff between what
  readers already saw and what the release says. The only permitted edit is trimming a clause the
  new lead paragraph makes literally redundant — never re-deriving a technical claim.
  **Specifically preserved:** the MSG bullet's explicit statement that a POSIX path containing an
  apostrophe was affected too (60-CONTEXT D-01 AMENDED: `quote_path()` closes an apostrophe by
  **doubling** it). A lead paragraph calling this release "Windows fixes" would be inaccurate.
  — **Reversibility:** reversible.

- **D-05: One new `### Fixed` bullet is authored for the image separator, citing IMG-08, IMG-09 and
  IMG-10 in trailing parentheses** (house style since Phase 33 — measured on every 0.9.0 bullet).
  It must describe the user-visible shape, not the mechanism: an image node preceded by any sibling
  content in the same container was emitted adjacent to the preceding code-mode expression, so Typst
  refused the file with `expected semicolon or line break` and `-b typstpdf` raised `ExtensionError`
  and wrote **no PDF for any master document in the project**. The sixteen container shapes may be
  summarized ("mid-sentence, in a list item, a table cell, a definition-list body, an admonition, a
  footnote, a field-list body, a section title, or a figure's legend") rather than enumerated.
  — **Reversibility:** reversible.

- **D-06: A `### Verified` subsection is written.** Measured: `### Verified` appears in **nine
  consecutive** released sections — `0.6.1` through `0.9.0` without a single gap. Omitting it here
  would be the first break in that streak, and 61-CONTEXT's Claude's-Discretion note explicitly
  deferred the choice to this phase. Three bullets, each backed by a run recorded in this phase's or
  Phase 62's evidence — **never carried forward on prose**:
  1. Zero new runtime **and** dev dependencies across the `v0.9.0..HEAD` diff.
  2. The four bundled `@preview` package version strings unchanged across all four sync surfaces
     (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`) — this is the
     verbatim wording used in the 0.6.5 and 0.9.0 entries.
  3. The 16 previously-failing and 9 must-keep-passing image shapes bound by a **real
     `typst.compile()`** gate (TEST-05), 18/18 masters compiling.

  **Explicit warning to the planner:** prior entries' third bullet is "The full-corpus (Sphinx
  v9.1.0 `doc/`) `-b typstpdf` re-run remains fatal-free." Do **not** copy that sentence unless this
  phase actually runs that corpus. Bullet 3 above replaces it with a claim this milestone did
  measure. — **Reversibility:** reversible.

- **D-07: The section vocabulary is `### Fixed` and `### Verified` only.** No `### Added`,
  `### Changed`, `### Removed`, `### Known Limitations`. The milestone adds no capability, changes
  no configuration and removes nothing (ROADMAP milestone goal; REQUIREMENTS.md Out of Scope). This
  is `0.6.5`'s exact shape. A `### Known Limitations` subsection has exactly one precedent in the
  whole file, inside `0.1.0b1`. — **Reversibility:** reversible.

### How loudly the published-0.9.0 blocker is named

- **D-08: The disclosure is one sentence in the `## [0.9.2]` lead paragraph, and nothing else.** It
  states plainly that a project built with 0.9.0 whose document places an image anywhere but first
  in its container produced no PDF for any master, and that 0.9.0 users should upgrade. This is
  exactly what 61-CONTEXT D-05 promised its accepted trade-off would buy — "the defect first reaches
  a user-visible document as a `### Fixed` bullet in the v0.9.2 entry" — and it is what `0.6.5` did
  for the same class of defect and nothing more. — **Reversibility:** reversible.

- **D-09: `README.md` is not touched beyond its Status line.** Measured: `README.md:289`'s
  `## Known Limitations` list still holds exactly its two original entries (Bibliography,
  Citations) — 61-CONTEXT D-05 held, nothing about the image blocker was ever added, so there is
  nothing to remove and no cleanup owed. The only `README.md` edit in this phase is
  `README.md:347`'s `**Status**: Stable (v0.9.0) - Production ready` → `v0.9.2`, which SC#1 requires
  and `tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject` enforces.
  — **Reversibility:** reversible.

- **D-10: No GitHub Security Advisory, no PyPI yank of 0.9.0, no README banner.** Each is an
  outward-facing irreversible action and is excluded by the phase's own fence, independent of
  whether it would be justified. If the owner wants any of them, it is a decision taken at or after
  `/gsd-complete-milestone`, not inside a prep-only phase. Recorded as a deferred idea below rather
  than silently dropped. — **Reversibility:** n/a (a non-action).

### Guard surfaces around the release

- **D-11: `RELEASE_VERSIONS` gains `"0.9.2"`.** Measured: `tests/test_changelog_page_gate.py:50-66`
  currently ends at `"0.9.0"`; the two build classes assert that **every** listed version string
  appears in the rendered `changelog.html` (line 170) and in the compiled changelog PDF (line 251).
  Precedent measured in `git log`: `dcee0201 feat(57-03): roll over CHANGELOG tail block, extend
  page-gate coverage`, `0c784c48 test(52-02): extend RELEASE_VERSIONS to 14 entries through 0.8.0`,
  `075c07d0 test(46-03): extend RELEASE_VERSIONS to 0.7.1` — every release-prep phase since 46 has
  extended it. Phase 61 skipped it only because there was no `0.9.1` section for the gate to find;
  here there is one. The tuple's preceding comment ("The 15 releases the published page was frozen
  without (0.4.4 through 0.9.0, inclusive)") is updated in the same edit — a stale comment beside a
  changed tuple is its own defect. — **Reversibility:** reversible.

- **D-12: A `Migrating from 0.9.0 to 0.9.2` guide is NOT written.** Measured:
  `docs/source/changelog.rst`'s Migration Guides section holds guides for 0.8.x→0.9.0,
  0.7.x→0.8.0, 0.7.0→0.7.1, 0.6.x→0.7.0, 0.5.x→0.6.x, 0.2.x→0.3.x and 0.1.x→0.2.x. There is **no**
  guide for `0.6.5` — the one prior patch release with no breaking change. 0.9.2 breaks nothing and
  needs no rewrite from anyone; a "nothing to do" guide would be the first of its kind in this file.
  — **Reversibility:** reversible.

### The handoff, and REL-04

- **D-13: `63-HANDOFF.md` follows `61-HANDOFF.md`'s structure with `vX.Y.Z` resolved to `v0.9.2`,
  but opens by stating the POSITIVE.** 61's first line stated the negative ("this milestone
  publishes nothing") precisely because that was the anomaly; restoring the standing shape is the
  correction, not an oversight. The opening line says that this milestone **does** publish and that
  the checklist below **is** the sequence `/gsd-complete-milestone` executes. The three inherited
  steps are carried in full: the `typsphinx-doc-translations` `update-pin.yml` **dispatch** (a
  manual dispatch on that repository — it is not a side effect of the parent repo's tag push, and
  advancing the pin and tagging that repo are two separate steps); the Read the Docs `en`
  (`typsphinx`) and `ja` (`typsphinx-ja`) `stable` measurement, doable with unauthenticated public
  API calls; and the GitHub Release body being byte-identical to
  `scripts/extract_changelog_section.py 0.9.2`'s stdout. — **Reversibility:** reversible.

- **D-14: REL-04 is re-offered as a named pre-flight/post-flight observation inside
  `63-HANDOFF.md` — not folded into any plan, and not promoted to a requirement.** 61-HANDOFF
  § "What v0.9.2 must also pick up" explicitly instructs that it "should be re-offered at the
  v0.9.2 release-prep phase's own handoff, where a real tag push will finally exercise it"; this
  decision is that re-offer, and it lands where the instruction pointed. REQUIREMENTS.md keeps
  REL-04 in v2, and its own note settles the response: "a failure there is handled inside the
  release phase rather than deferred, but it is not a requirement of this milestone." So the handoff
  must record four things for the operator: (a) `release.yml`'s `create-release` job carries
  explicit `Install uv` steps at HEAD and ran green at the **v0.8.0 and v0.9.0 real tag pushes**, so
  a failure now would be a regression, not the known v0.7.0 `uv: command not found` defect; (b) the
  exact observation to make (`gh run watch` on the release run, then that job's conclusion read
  literally); (c) the response if it fails — fix it inside this release work and re-run the job, do
  not defer; (d) that
  `.planning/todos/pending/2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` stays in
  `pending/` and is closed only by an observed green `create-release` on a real tag push, which does
  not happen in this phase. — **Reversibility:** reversible.

- **D-15: The `pypi` GitHub Environment's manual approval is named as an EXPECTED gate, in the
  operator's own reading order.** SC#5 already requires this; the handoff must say it before the
  step that triggers it, because a workflow paused on an environment approval looks exactly like a
  failed workflow to an operator scanning `gh run list`. — **Reversibility:** reversible.

### Mechanics that bind every plan

- **D-16: The fence is `63-CLOSEOUT-GUARD.md`, reusing `61-CLOSEOUT-GUARD.md`'s procedure
  verbatim.** `sha256sum .planning/REQUIREMENTS.md` + `wc -l` + `git rev-parse HEAD` +
  `grep -n 'REL-09' .planning/REQUIREMENTS.md` recorded at phase head; the same commands re-run and
  compared at phase close; **and once more after `phase.complete`-family tooling has run** — that
  third observation is the one that actually catches the flip, because it runs outside any plan's
  reach. The flip is **reverted and reported, never accepted and never committed**
  (`git checkout -- .planning/REQUIREMENTS.md`). Every plan's `SUMMARY.md` frontmatter declares
  `requirements-completed: []` for REL-09 — the v0.9.1 audit found three of Phase 61's four plans
  declaring `[REL-09]` and contradicting the correctly-unmet checkbox. REL-09's state is read
  directly out of `.planning/REQUIREMENTS.md` as `[ ]` at close, never inferred from frontmatter.
  — **Reversibility:** reversible.

- **D-17: `uv lock` runs and is committed BEFORE the CI dispatch.** Every CI job begins with
  `uv sync --extra dev --locked` (57-CONTEXT D-13 AMENDED's corrected 10-step census across four
  workflows). Measured now: `uv.lock:1467` reads `version = "0.9.0"` for the self-package,
  independent of `pyproject.toml:7`. Dispatching before regenerating would reproduce the exact
  refusal already killing every dependabot PR, and it would fail at the *install* step of
  `release.yml`'s `validate`/`build` jobs on the real tag push, before any test runs. `uv.lock` is
  regenerated with `uv lock` and **never hand-edited**. — **Reversibility:** reversible.

- **D-18 (AMENDED — see § Amendments item 1 for the corrected step name; the rest stands):
  One CI dispatch, on the phase's final tip, after the bump commit.** Phase 57 ran two
  (pre-bump and post-bump); Phase 61 ran one, since it had no bump to split around. SC#4 names "the
  **bumped** tip", and this phase's only code-affecting change is `D-11`'s one-tuple test edit which
  lands with the release work — so one dispatch on the last commit is the default.
  `gh workflow run CI --ref gsd/v0.9.2-inline-image-blocker-fix-and-release`, waited to
  **completion**, with both `windows-latest` lanes and `macos-latest` named individually and every
  job conclusion transcribed literally. `ruff`'s verdict is taken from that run's `Run linters`
  step — never from this machine, where `ruff` is an unrunnable generic-linux ELF in any freshly
  `uv sync`-provisioned worktree venv. **[AMENDED: `ci.yml` has no step named `Run linters` — that
  name exists only at `release.yml:84`, which this phase must never trigger. Read the verdict from
  `ci.yml`'s `Lint and Format Check` job, step `Run lint with tox` (`ci.yml:69`). § Amendments
  item 1.]** A plan that lands a second code-affecting change mid-phase
  adds a second dispatch; that is the only justification for one. — **Reversibility:** reversible.

- **D-19: Evidence files follow `61-*`'s naming set exactly, and `63-VERIFICATION.md` is
  forbidden.** `{padded_phase}-VERIFICATION.md` is `gsd-verifier`'s reserved output name and a
  plan-authored file there is clobbered at verify time. Suggested set, mirroring Phase 61's:
  `63-CLOSEOUT-GUARD.md`, `63-CHANGELOG-EVIDENCE.md`, `63-GREEN-TREE-EVIDENCE.md`,
  `63-CI-EVIDENCE.md`, `63-SC5-INVARIANTS.md`, `63-HANDOFF.md`. — **Reversibility:** reversible.

- **D-20: The extractor's stdout is transcribed verbatim into `63-CHANGELOG-EVIDENCE.md`, with
  three named greps recorded beside it.** Measured why this matters:
  `scripts/extract_changelog_section.py`'s `_SECTION_HEADER_RE` matches **every** `## [...]` heading
  and the algorithm is purely positional — first heading naming the requested version, everything up
  to the next heading of any name. So the scratch block at `CHANGELOG.md:38`
  (`### Planned for Future Releases`) must be relocated under a fresh empty `## [Unreleased]` placed
  **above** `## [0.9.2]` **before** the rename, or it lands verbatim in the published GitHub Release
  body. The three greps: no `## [0.9.1]` heading anywhere; no `[0.9.1]:` tail link anywhere; no
  `Planned for Future Releases` line inside the extracted body. REL-10 is closed by reading the
  script's stdout, not by reasoning that the edit was correct. — **Reversibility:** reversible.

- **D-21: The docs warning baseline is taken from a clean build.** `rm -rf docs/_build` before each
  of `tox -e docs-html` and `tox -e docs-pdf`. An incremental rebuild under-reports warnings and
  manufactures a false "baseline match" — this is a repeat finding in this project, not a
  theoretical hazard. — **Reversibility:** reversible.

### Claude's Discretion

The owner delegated all four presented gray areas at once ("おすすめ"). Every D-01..D-21 above is
Claude's recommendation. Planning may refine:

- Plan decomposition, ordering and wave assignment; which plan owns which evidence file.
- The exact prose of the lead paragraph and of every CHANGELOG bullet, subject to D-02 (never name
  0.9.1), D-04 (promote verbatim), D-06's warning (no unmeasured `### Verified` claim) and the
  measured framing constraint that this is not a Windows-exclusive fix.
- The mechanical form of the checksum guard and where the two separated SC#5 fence probes are
  recorded — subject to SC#5's requirement that the two observations be separated by **intervening
  waves**, not by wall-clock luck, and that each remote probe carry a **positive control** (an
  assertion that would fail if the probe were vacuous).
- Whether a milestone-diff sweep anchored at the `v0.9.0` tag backs D-06's bullets 1 and 2, or
  whether targeted greps suffice. If a sweep is run, its positive control must be real.
- The heading structure of `63-HANDOFF.md`, provided D-13's positive opening, D-14's four REL-04
  items and D-15's approval-gate note all survive.

Planning may **not** weaken D-02 (no `0.9.1` in prose), D-07 (`### Fixed` + `### Verified` only),
D-16 (the three-observation fence and `requirements-completed: []`), D-17 (`uv lock` before
dispatch), or D-19 (the `63-VERIFICATION.md` ban) without returning to the owner.

### Folded Todos

None. All eight matched todos were reviewed and left in `.planning/todos/pending/` — see Reviewed
Todos below. REL-04's todo is *named in the handoff* by D-14, which is a record, not a fold: no plan
in this phase executes anything against it.

</decisions>

<amendments>
## Amendments (2026-08-30, planning time — owner-approved)

One item above was corrected by a direct read of both workflow files during planning: the
`gsd-phase-researcher` reported it under `63-RESEARCH.md` § "Contradictions Found", and the
orchestrator independently reproduced it with `grep -rn 'Run linters' .github/` before bringing it
to the owner. The locked text above is left as written; this is an additive correction. The same
correction was applied to the three matching sentences in `.planning/ROADMAP.md` (milestone
constraint 11, Phase 62's SC#5, and **Phase 63's own SC#4**) so the planner, the executor and the
verifier all read one wording.

1. **D-18 — `ruff`'s CI verdict comes from `ci.yml`'s `Lint and Format Check` job, not from a step
   named "Run linters".** Measured: `grep -rn 'Run linters' .github/` returns exactly **one** hit,
   `.github/workflows/release.yml:84`. `.github/workflows/ci.yml` has **no** such step. Its `lint`
   job (`ci.yml:51-70`, display name **`Lint and Format Check`**) has exactly one substantive step,
   named **`Run lint with tox`** (`ci.yml:69`), running `uv run tox -e lint` → `tox.ini`'s
   `[testenv:lint]` → `black --check .` then `ruff check .`.

   D-18's *intent* — CI holds lint authority, never this machine, where `ruff` is an unrunnable
   generic-linux ELF in a freshly `uv sync`-provisioned worktree venv — is **unaffected and
   stands**. Only the identifier was wrong; it was copied from `release.yml`, the one workflow this
   prep-only phase must never trigger. Two failure modes this closes: a plan searching literally for
   a step named "Run linters" inside the dispatched `ci.yml` run finds nothing, or — worse —
   concludes it must dispatch `release.yml` instead, breaching the prep-only fence.

   **This is the third recurrence, and the first one fixed at the source.** Phase 62 carried the
   identical wording (`62-CONTEXT.md:122`, `62-04-PLAN.md:21`); its executor hit the mismatch live
   and handled it honestly rather than silently — `62-RED-EVIDENCE.md:468-471` and
   `62-04-SUMMARY.md:36` both record "Run linters" as *a paraphrase, not the literal step name*, and
   `62-VERIFICATION.md` verified SC#5 against `Lint and Format Check = success`. Correcting
   ROADMAP's Phase 62 SC#5 therefore aligns the criterion with what was actually verified; it
   weakens nothing retroactively.

   **Binding on every plan in this phase:** `ruff`'s verdict is read as the **`Lint and Format
   Check`** job's conclusion in `gh run view <id> --json jobs` (the same row `61-CI-EVIDENCE.md`
   recorded as `success`), with the `Run lint with tox` step's own `ruff check .` output quoted
   verbatim in `63-CI-EVIDENCE.md`. No plan drills for a step named `Run linters` in either
   workflow, and no plan triggers `release.yml` for any reason.
</amendments>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and binding constraints

- `.planning/ROADMAP.md` § "🚧 v0.9.2 — Inline image blocker fix and release" constraints **6, 7, 8,
  9, 11, 12, 13** — the `uv.lock` lockstep, the CHANGELOG edit ordering, the prep-only fence, the
  checksum-fence history, CI's lint authority, worktree isolation, and the standing invariants. All
  six bear directly on this phase.
- `.planning/ROADMAP.md` § "Phase Details → Phase 63: v0.9.2 Release Prep (prep-only)" — SC#1–SC#5
  and the two cross-cutting constraints. Read in full; nothing in this CONTEXT supersedes them
  (unlike Phase 61, where D-11 mapped three criteria away — **there is no such mapping here**).
- `.planning/REQUIREMENTS.md` § "REL — release" — REL-09, REL-10, REL-11 verbatim; § "Out of Scope"
  (binding); § "Traceability" phase-mapping notes for Phase 63.
- `.planning/PROJECT.md` § "Current Milestone: v0.9.2" — including the 2026-08-30 amendments, which
  must not be re-litigated.

### The release-prep precedent to follow

- `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/61-CONTEXT.md` — the
  immediately preceding release-prep phase. Its D-05 (deferred disclosure), D-09 (the live-run
  green-proof set), D-10 (the fence), D-13 (the three inherited publish steps), and its
  Claude's-Discretion note deferring the `### Verified` choice **to this phase** all land here.
  Its D-01/D-02/D-03/D-04 (no bump, no versioned section, untouched tail block) are **reversed**
  here — this phase does all four.
- `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/61-CLOSEOUT-GUARD.md` — the
  fence procedure to reuse **verbatim**, including its "For the operator running phase.complete"
  section and its revert-never-accept rule.
- `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/61-HANDOFF.md` § "What the
  v0.9.2 milestone inherits" (the three publish steps, with command shapes) and § "What v0.9.2 must
  also pick up" (the REL-04 re-offer instruction D-14 answers, and the bullet-promotion
  instruction D-04 answers).
- `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/61-CHANGELOG-EVIDENCE.md` —
  the provenance of the three `## [Unreleased]` bullets D-04 promotes verbatim.
- `.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-CONTEXT.md` § D-13
  AMENDED — the `uv.lock`-before-dispatch sequencing constraint and the corrected 10-step
  `--locked` census that D-17 rests on. Its breaking-change and migration-guide decisions do **not**
  carry: 0.9.2 breaks nothing.

### What the CHANGELOG entry describes

- `.planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/62-VERIFICATION.md`
  and `62-RED-EVIDENCE.md` — the authority for every claim D-05 and D-06 make about the image fix
  and its gate (the 17-red/1-green RED run, the 18/18 post-fix result).
- `.planning/phases/62-.../62-CONTEXT.md` § `<amendments>` — the three planning-time corrections
  (the triad's scope, `pass_c`'s one added empty line, the 27-document count). The CHANGELOG must
  not describe a mechanism these amendments falsified.
- `.planning/milestones/v0.9.1-phases/60-.../60-CONTEXT.md` § D-01 AMENDED — `quote_path()` doubles
  an apostrophe, which is why the release is **not** "Windows-only" (D-04).
- `.planning/milestones/v0.9.1-phases/59-.../59-WINDOWS-URI-EVIDENCE.md` and
  `.../60-PATH-QUOTING-EVIDENCE.md` — evidence behind the promoted path bullets.

### Files this phase edits

- `pyproject.toml:7` — `version = "0.9.0"`, the sole hand-edited version literal.
- `uv.lock:1467` — the `typsphinx` self-package's own `version = "0.9.0"`; regenerated by `uv lock`,
  never hand-edited (D-17).
- `README.md:347` — `**Status**: Stable (v0.9.0) - Production ready`.
- `CHANGELOG.md:8` (`## [Unreleased]`), `:10-36` (the three bullets to promote), `:38`
  (`### Planned for Future Releases`, the scratch block to relocate first), `:45`
  (`## [0.9.0] - 2026-08-17`, the terminator the extractor stops at), and the tail link block
  ending `[Unreleased]: …/compare/v0.9.0...HEAD`.
- `tests/test_changelog_page_gate.py:50-66` — `RELEASE_VERSIONS` and its preceding comment (D-11).

### Gate and release machinery

- `scripts/extract_changelog_section.py` — its module docstring documents the positional algorithm
  and the two-`## [Unreleased]`-headings gotcha that REL-10 turns on. Read it before editing
  `CHANGELOG.md`.
- `tests/test_readme_version_sync.py`, `tests/test_extension.py::test_version_matches_pyproject_toml`,
  `tests/test_preview_version_sync.py` — the version-sync guard family; all three must be run, not
  reasoned about.
- `tests/test_changelog_extraction.py` — exercises the extractor via `subprocess.run`.
- `.github/workflows/release.yml` — the publish path; **recorded in the handoff, never triggered**.
  Its `create-release` job is D-14's subject.
- `.github/workflows/ci.yml` — triggers scoped to `main`/`develop` plus `workflow_dispatch`; the
  3-OS × py312/py313 matrix and the `Lint and Format Check` job (step `Run lint with tox`,
  `ci.yml:69`) D-18 takes `ruff`'s verdict from — see § Amendments item 1: `ci.yml` carries no step
  named `Run linters`.
- `.github/workflows/links.yml` — the repo-wide lychee scan **excludes `CHANGELOG.md`**, so a dead
  tail link would not be caught by CI. The `[0.9.2]` link this phase adds points at a tag that does
  not exist until `/gsd-complete-milestone`; that is expected and is the same state every prior
  release-prep phase ended in.
- `docs/source/changelog.rst:1-2` — the `.. include:: ../../CHANGELOG.md` with
  `:parser: myst_parser.sphinx_` that makes every CHANGELOG link a published link. The basis for
  D-02, and for D-12's Migration-Guides measurement.

### Execution environment

- `CLAUDE.md` § "Worktree-isolated execution" — mandatory per-worktree
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, then everything via `uv run`.
  Not conditional, not degraded for low parallelism.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`61-CLOSEOUT-GUARD.md`'s procedure** — the only measure that has ever stopped the REL-09
  auto-flip. Reused verbatim by D-16, with the phase number and baseline values re-measured fresh.
- **`61-HANDOFF.md`'s § "What the v0.9.2 milestone inherits"** — three publish steps already written
  with `vX.Y.Z` placeholders precisely so this phase can resolve them to `v0.9.2` without
  rediscovering them.
- **`scripts/extract_changelog_section.py`** — the GitHub Release body's single source. Phase 61
  deliberately did not invoke it (no versioned section existed); this phase is the first since
  Phase 57 that can.
- **`## [0.6.5]`'s section shape** (`CHANGELOG.md:381-403`) — lead paragraph + `### Fixed` +
  `### Verified`, for a hotfix patch closing one compile-blocking separator defect. The closest
  structural template in the file for what D-01/D-07 ask for.

### Established Patterns

- **CHANGELOG vocabulary, measured file-wide:** `### Fixed` (19), `### Added` (14), `### Changed`
  (13), `### Verified` (9), `### Removed` (5); `### Known Limitations` once, inside `0.1.0b1`.
- **`### Verified` in nine consecutive releases** (0.6.1 → 0.9.0), always three bullets, always
  facts measured over the milestone diff.
- **Requirement IDs in trailing parentheses** — house style since Phase 33.
- **Evidence-file naming** `{padded_phase}-{TOPIC}-EVIDENCE.md`; `{padded_phase}-VERIFICATION.md` is
  the verifier's reserved name (D-19).
- **Release-prep extends `RELEASE_VERSIONS`** — measured in `git log` at Phases 46, 52 and 57.

### Integration Points

- `CHANGELOG.md` is the only file whose *content* this phase authors; `pyproject.toml`, `uv.lock`,
  `README.md` and `tests/test_changelog_page_gate.py` each take a one-line/one-token mechanical
  edit. Nothing under `typsphinx/` is touched — SC#5's `git diff` over the phase proves it.
- `docs/source/changelog.rst` renders `CHANGELOG.md` into the published docs, so the `## [0.9.2]`
  prose **is** user-facing on Read the Docs. Write it as prose a user reads, not internal shorthand.
- The `docs-html` and `docs-pdf` tox environments consume the same file, so a malformed MyST block
  surfaces as a docs-build warning — which is what D-21's clean-build baseline is for.

### Measured hazard the planner must carry

- **The changelog-page gate's two build classes SKIP in a worktree venv.** Measured:
  `myst_parser` lives in the **`docs`** extra only (`pyproject.toml:49-54`); the module's own
  docstring says so, and `tests/test_changelog_page_gate.py:29` guards on
  `import myst_parser`. A worktree provisioned with `uv sync --extra dev` therefore skips both
  `TestChangelogPageContentCoverage` (`-b html`) and the PDF class — the exact two classes that
  enforce D-11's `RELEASE_VERSIONS` addition. **A green worktree `pytest` does not prove D-11.** It
  must be proven either in an environment carrying the `docs` extra or taken from the dispatched CI
  run, and the plan must say which.

</code_context>

<specifics>
## Specific Ideas

1. **`## [0.6.5]` is the template to read before writing anything.** Same defect class (a missing
   separator aborting the Typst compile), same release class (patch, no breaking change), same
   sections. Read `CHANGELOG.md:381-403` first.

2. **The lead paragraph carries the upgrade urgency; nothing else does.** One sentence naming what
   0.9.0 users hit. No banner, no advisory, no README entry (D-08, D-09, D-10).

3. **"Windows" is not the framing.** A POSIX path containing an apostrophe was affected by the same
   MSG family, and the image blocker is platform-independent. The accurate summary of the path work
   is "Windows-shaped paths, and any path containing a quote character."

4. **Order of operations inside `CHANGELOG.md` is load-bearing, not cosmetic.** Relocate the scratch
   block under a fresh empty `## [Unreleased]` **first**, rename **second**, add the tail link
   **third**, run the extractor **fourth** and read its stdout. Reversing steps one and two puts
   `### Planned for Future Releases` into the published GitHub Release body.

5. **Expect the decoy `gsd/v0.9.2-milestone` to reappear.** Measured now: `git branch -vv` shows
   exactly one `0.9.2` branch, the canonical
   `gsd/v0.9.2-inline-image-blocker-fix-and-release` at `dd385436`, tracking
   `origin/…` and **ahead 10**. If the decoy is re-created by a commit helper, advance the canonical
   pointer **before** deleting it — deleting first would orphan commits.

6. **`git tag -l 'v0.9.2'` and `git ls-remote --tags origin | grep 0.9.2` both come back empty
   today** (measured 2026-08-30). SC#5 asks for that state to be observed **twice, separated by
   intervening waves**, each with a positive control — a probe that would fail if it were vacuous
   (e.g. the same command shape finding `v0.9.0`, which does exist).

7. **Do not name any evidence file `63-VERIFICATION.md`.**

</specifics>

<deferred>
## Deferred Ideas

- **A GitHub Security Advisory, a PyPI yank of 0.9.0, or a README upgrade banner** for the blocker
  live in the published 0.9.0. Offered and declined for this phase by D-10: each is outward-facing
  and irreversible, and the prep-only fence excludes it categorically. The natural place to revisit
  is at or after `/gsd-complete-milestone`, once 0.9.2 is actually installable.
- **A `Migrating from 0.9.0 to 0.9.2` guide.** Declined by D-12 — nothing breaks, and no prior
  no-breaking-change patch release has one. Revisit only if a future release genuinely needs a
  rewrite from users.
- **Running the full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run** so that D-06's third
  `### Verified` bullet could reuse the wording nine prior releases used. Not adopted: it is a long
  run whose result this milestone did not need, and D-06 substitutes a claim this milestone did
  measure. Revisit if a future release wants the streak's exact wording back.

### Reviewed Todos (not folded)

All eight todos matched by `todo.match-phase 63` were reviewed and left in
`.planning/todos/pending/`. None is folded.

- `2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` (REL-04, v2) — **named in
  `63-HANDOFF.md` by D-14**, which is the re-offer 61-HANDOFF instructed. Not folded: nothing in a
  prep-only phase can exercise a real tag push, so there is no work here to do. It closes only on an
  observed green `create-release` at `/gsd-complete-milestone`.
- `2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md` (CI-01, v2) — its *lockstep
  obligation* is discharged by D-17 (`uv lock` in the bump commit, before dispatch), but the todo
  itself is about dependabot's own PRs and needs a workflow change this phase does not make.
- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md`
  (MSG-06, v2) — a `typsphinx/` behaviour change; excluded absolutely by the prep-only fence.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`
  (NUM-01, v2) — same fence exclusion.
- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` (QUA-09, v2) — source-wide change;
  `CLAUDE.md` independently forbids it until the filed todo lands.
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` (QUA-08, v2) — a new CI job. Noted for the record: it
  is the todo that would catch a dead CHANGELOG tail link, which `links.yml` deliberately excludes.
  Out of scope here.
- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` (QUA-10, v2) — its consequence is
  absorbed by D-18 (CI holds lint authority), not fixed.
- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md` (DOC-18, v2) — docs
  structure, unrelated to the release.

</deferred>

---

*Phase: 63-v0-9-2-release-prep-prep-only*
*Context gathered: 2026-08-30*
