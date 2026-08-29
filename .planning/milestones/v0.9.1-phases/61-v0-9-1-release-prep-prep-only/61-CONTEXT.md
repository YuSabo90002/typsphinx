# Phase 61: v0.9.1 Release Prep (prep-only) - Context

**Gathered:** 2026-08-29
**Status:** Ready for planning

<domain>
## Phase Boundary

**This phase's shape changed materially during discussion.** ROADMAP.md's Phase 61 entry describes a
version-bumping release-prep phase that ends with a `## [0.9.1]` CHANGELOG section and a handoff to
`/gsd-complete-milestone` for publishing. The owner decided this session (see D-01 through D-07) that
**v0.9.1 will never be published**. The phase is therefore a *milestone close-out* phase, not a
release-prep phase: it records this milestone's work in the CHANGELOG's `## [Unreleased]` section,
proves the milestone-final tree green on live runs, proves the no-irreversible-action fence held, and
hands the publish job forward to a v0.9.2 milestone that will also carry the inline-image blocker fix.

**Decisions in this file supersede ROADMAP.md's Phase 61 Success Criteria wherever they conflict.**
The owner chose to leave ROADMAP.md unedited rather than rewrite it, so the conflict is real and
recorded here deliberately. See D-11 for the precise mapping of which ROADMAP criteria survive intact,
which are dropped, and which are reworded — downstream agents (planner, plan-checker, verifier,
decision-coverage gate) must read D-11 before evaluating this phase against ROADMAP SC#1–SC#5.

**In scope:**

- Authoring the three defect families of this milestone as real bullets under the existing
  `## [Unreleased]` heading in `CHANGELOG.md`. Measured this session: `## [Unreleased]` currently
  holds **zero real bullets** — only a `### Planned for Future Releases` list of five future features.
  Unlike Phase 57, which promoted seven already-written bullets, every bullet here is authored new.
- SC#3's live-run green proof, retained in full but re-anchored: full `pytest`, `black` / `ruff` /
  `mypy`, both docs tox environments against their measured warning baselines, and a **fresh 3-OS CI
  dispatch** with both `windows-latest` lanes green — measured on the milestone-final tree rather than
  on a "bumped tree", because there is no bump (D-01).
- SC#4's fence proof, retained in full: no local or remote `v0.9.1` tag, no publish, no GitHub
  Release, no PR — probed and recorded twice at separated times; `git diff` over the phase showing no
  unintended change under `typsphinx/`; and a `REQUIREMENTS.md` checksum recorded at phase head to
  catch the `phase.complete` auto-flip of REL-09 (fired at **five consecutive** release-prep closes).
- `61-HANDOFF.md`, re-aimed: it records that publishing does **not** happen for this milestone, what
  the next milestone's release-prep phase inherits, and the standing publish steps (second-repository
  tag via `typsphinx-doc-translations`' own `update-pin.yml` dispatch, the Read the Docs `stable`
  measurement for both projects, and the GitHub Release body being byte-identical to
  `scripts/extract_changelog_section.py`'s stdout) so none of them is lost across the milestone
  boundary.

**Out of scope:**

- **Any version bump.** `pyproject.toml:7` stays `0.9.0`; `README.md:347`'s Status line stays
  `Stable (v0.9.0)`; `uv.lock` is not regenerated for a version change; the editable-install metadata
  is not touched for a version change. (D-01)
- **Any `## [0.9.1]` CHANGELOG section, and any change to the tail link-reference block.** No
  `[0.9.1]` release-tag line, no advancing `[Unreleased]` past `v0.9.0...HEAD`. (D-03, D-04)
- **Any public-surface disclosure of the inline-image blocker** — no `README.md` Known Limitations
  entry, no CHANGELOG `### Known Limitations`, no docs note. (D-05)
- **Any fix for the inline-image blocker.** It belongs to the v0.9.2 milestone. (D-07)
- **Any `typsphinx/` behaviour change.** The prep-only fence is absolute in this phase — there is no
  Phase-57-style amended exception, and any pressure to create one is a signal to stop and ask the
  owner rather than to proceed.
- **Any irreversible action:** no tag (local or remote), no PyPI publish, no GitHub Release, no PR.
- Adding `"0.9.1"` to `RELEASE_VERSIONS` in `tests/test_changelog_page_gate.py` — there is no 0.9.1
  release section for that gate to find.
- A `Migrating from 0.9.0 to 0.9.1` guide in `docs/source/changelog.rst` — no release, no breaking
  change, nothing to migrate.

</domain>

<decisions>
## Implementation Decisions

### The release that will not happen

- **D-01: This phase performs no version bump.** `pyproject.toml:7` (measured this session as still the sole version literal, holding `0.9.0`), `README.md:347`'s `**Status**: Stable (v0.9.0) - Production ready` line, and `uv.lock` all stay where they are. ROADMAP SC#1 asked for an atomic move to `0.9.1`; that criterion is dropped, not deferred. The reason is measured, not stylistic: `docs/source/changelog.rst:1` includes `../../CHANGELOG.md` wholesale via `myst_parser.sphinx_`, so a `[0.9.1]: …/releases/tag/v0.9.1` link for a tag that will never exist would be published on Read the Docs as a 404 — which contradicts PROJECT.md's stated core value that "a URL the project publishes must actually resolve". Bumping without the link block would leave `README.md` advertising a `v0.9.1` nobody can install and `typsphinx.__version__` reporting a version absent from PyPI. — **Reversibility:** reversible — nothing is written, so a later phase that decides to publish 0.9.1 after all simply performs the bump it would have performed anyway.

- **D-02: v0.9.1 is never published. The next published release is 0.9.2.** No `v0.9.1` tag will ever exist, local or remote. The version number is skipped outright rather than held. The owner's reason is the blocker in D-06: publishing a release whose headline claim is image-URI correctness, while any mid-paragraph inline image aborts the whole PDF compile, is not a release worth making. — **Reversibility:** costly — reversing this means publishing 0.9.1 later from a tree that will by then contain the v0.9.2 milestone's work, so the CHANGELOG section and the tag content would both have to be reconstructed.

- **D-03: The three defect families are written under the existing `## [Unreleased]` heading, not under a new `## [0.9.1]` heading.** Measured this session: `## [Unreleased]` holds only `### Planned for Future Releases` with five entries and **zero** real change bullets, so this is authoring from scratch (the Phase 52 shape), not the Phase 57 promote-seven-existing-bullets shape. When the v0.9.2 release-prep phase runs, it promotes these bullets into its `## [0.9.2]` section together with the blocker fix's own bullet — exactly the mechanism Phase 57's D-02 used. — **Reversibility:** reversible — promoting an `## [Unreleased]` block into a versioned section is a heading edit.

- **D-04: The tail link-reference block is not touched.** No `[0.9.1]` release-tag line is added and `[Unreleased]` stays at `v0.9.0...HEAD`. This is the one piece of standing release-prep procedure (recorded in prior milestones as "the link block rollover is release-prep work, done in the same phase as the bump") that is *suspended* here rather than carried, and it is suspended for the same measured reason as D-01: the link would 404 on the published docs page. Note for the future reader: `.github/workflows/links.yml` excludes `CHANGELOG.md` from the repo-wide lychee scan, so CI would **not** have caught such a dead link — the exclusion is deliberate ("historical record deliberately left stale") and is not a licence to publish a new dead link. — **Reversibility:** reversible.

- **D-05: The inline-image blocker gets no public-surface disclosure in this phase.** No entry in `README.md`'s `## Known Limitations` list (measured at `README.md:289`, currently two entries: Bibliography, Citations), no `### Known Limitations` subsection in `CHANGELOG.md` (the only precedent is inside the `0.1.0b1` section), and no note under `docs/source/`. The owner's rationale: no version carrying this defect will be newly published, so the defect first reaches a user-visible document as a `### Fixed` bullet in the v0.9.2 entry. **Recorded trade-off the owner accepted:** users already running the published `0.9.0` do hit this defect today and will receive no notice of it until 0.9.2 ships. — **Reversibility:** reversible — a README bullet can be added at any time.

- **D-06: The inline-image blocker is a pre-existing defect, not a v0.9.1 regression, and this was measured rather than assumed.** `git diff v0.9.0..HEAD -- typsphinx/translator.py` is 25 lines and touches exactly one thing: IMG-05's `escape_typst_string()` call on the already-relativized URI. `visit_image()`'s missing leading separator is byte-identical to the `v0.9.0` tag. The defect is recorded in full — reproduction, root cause, six-row trigger matrix, and solution sketch — at `.planning/todos/pending/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md`. Its shape in one sentence: any image node preceded by sibling content in the same paragraph or list item is emitted adjacent to the preceding code-mode expression, Typst answers `expected semicolon or line break`, and `-b typstpdf` raises `ExtensionError` so **no** master document in the project produces a PDF. — **Reversibility:** n/a (a measurement, not a choice).

- **D-07: The blocker fix belongs to the next milestone (v0.9.2), not to this milestone.** No repair phase is inserted before or after Phase 61, and the ROADMAP's phase ordering is left as it stands. The todo stays in `.planning/todos/pending/` and is picked up by the v0.9.2 requirements-gathering pass. `61-HANDOFF.md` names it explicitly so the next milestone does not have to rediscover it. — **Reversibility:** reversible — inserting a repair phase later costs a roadmap edit.

- **D-08: REL-09 carries forward unmet, with its wording unchanged.** It stays `[ ]` in `.planning/REQUIREMENTS.md` and moves to the v0.9.2 milestone as written, including its literal `v0.9.1` version string. The owner explicitly rejected both rewriting it to say `v0.9.2` and closing it as superseded. The only inconsistency this leaves behind is the version number inside a requirement that has never been satisfied — which is accurate, because nothing was released. No plan in this phase touches REL-09's checkbox. — **Reversibility:** reversible.

### What survives from ROADMAP SC#3 and SC#4

- **D-09: SC#3's live-run green proof is retained in full, re-anchored to the milestone-final tree.** The evidence set is unchanged from what ROADMAP SC#3 lists — full `pytest`, `black` / `ruff` / `mypy`, both docs tox environments against their measured warning baselines, and a fresh 3-OS CI dispatch with both `windows-latest` lanes green — but the phrase "the **bumped** tip" everywhere becomes "the milestone-final tip", since D-01 removes the bump. Measured this session: the most recent successful full CI run on this branch is `33252336287` (`workflow_dispatch`, 2026-08-29T12:22Z, success, 6m37s), and every commit since is documentation-only (`764463aa`, `4e113c6a`, `dbae1ee8`, `47c0054c`). A fresh dispatch is still required — SC#3's whole point is that the green is observed here, not inherited — but unlike Phase 57 there is no pre-bump/post-bump split to justify two dispatches, so **one dispatch on the phase's final code tip is the default**; the planner may add a second only if a plan lands a code-affecting change mid-phase. — **Reversibility:** reversible.

- **D-10: SC#4's fence proof is retained in full and is strictly easier to satisfy than in prior milestones.** The `v0.9.1`-tag probe, the no-publish probe (both recorded twice at separated times), the `git diff` showing no unintended change under `typsphinx/`, and the `REQUIREMENTS.md` checksum recorded at phase head all stay. Two notes for whoever writes this plan. First, the checksum guard exists because `phase.complete` has auto-flipped the release requirement to `[x]` against the phase's own recorded decision at **five consecutive** release-prep closes; D-08 makes that flip more likely to slip through unnoticed here, not less, because REL-09's wording no longer matches what the phase did. Second, the `typsphinx/`-diff check has no amended exception in this phase — unlike Phase 57, where an owner-approved `builder.py` message fix broke the fence mid-phase — so a clean diff is the expected result and any hit is a real finding. — **Reversibility:** reversible.

- **D-11: The ROADMAP-to-CONTEXT mapping is stated explicitly here because the owner chose not to rewrite ROADMAP.md.** Downstream agents must evaluate this phase against this mapping, not against ROADMAP.md's Phase 61 Success Criteria read in isolation, or they will report false violations. The mapping: **SC#1 (atomic move to 0.9.1) is DROPPED** — D-01. **SC#2 (curated `## [0.9.1]` section, tail link rollover, `extract_changelog_section.py 0.9.1` byte-for-byte reproduction) is REWORDED** — the curated content is authored under `## [Unreleased]`, the link block is untouched (D-03, D-04), and the extraction-script reproduction check moves to the v0.9.2 release-prep phase along with the section it would extract. **SC#3 is RETAINED, re-anchored** — D-09. **SC#4 is RETAINED in full** — D-10. **SC#5 (standalone handoff checklist) is RETAINED, re-aimed** — the checklist enumerates what the *v0.9.2* release-prep phase and its `/gsd-complete-milestone` inherit, not what this milestone's `/gsd-complete-milestone` executes, because this milestone's close performs no publish (D-02, D-12). The named readers of this decision are the **gsd-planner** (which derives plan acceptance from success criteria), the **gsd-plan-checker**, and the **phase verifier** (which re-derives criteria at close). — **Reversibility:** reversible.

### The handoff

- **D-12: `/gsd-complete-milestone` runs for this milestone but performs no publish step.** It archives the phase directories and prepares the v0.9.2 milestone; it does not tag, does not publish to PyPI, and does not create a GitHub Release. `61-HANDOFF.md` must say this in its own words at the top so that an operator following the checklist does not reach for the standing publish sequence out of habit — the standing pattern across the last seven milestones is that the handoff checklist *is* the publish sequence, and this is the first time it is not. — **Reversibility:** reversible.

- **D-13: `61-HANDOFF.md` preserves the standing publish steps as an inheritance record, not as instructions to execute now.** The three that must survive the milestone boundary because they are easy to lose and expensive to rediscover: (a) the second-repository tag for `typsphinx-doc-translations`, advanced by dispatching **that repository's own `update-pin.yml`** rather than by a hand-made clone-edit-push; (b) the Read the Docs `stable` measurement for both projects, which is doable with unauthenticated public API calls; (c) the GitHub Release body being byte-identical to `scripts/extract_changelog_section.py <version>`'s stdout. Each is written with the version left as a placeholder rather than hard-coded to `0.9.1`. — **Reversibility:** reversible.

### Claude's Discretion

- The exact wording of the `## [Unreleased]` bullets, their `### Added` / `### Changed` / `### Fixed` section assignment, and their granularity — including whether the new internal module `typsphinx/pathfmt.py` earns a user-visible bullet at all (it is internal, and this project's CHANGELOG has historically described user-visible behaviour rather than module structure), and whether Phase 58's MSG-01 test-side decoupling earns one (it produced no user-visible change by construction). Requirement IDs attached in trailing parentheses is the settled house style since Phase 33.
- Whether the `## [Unreleased]` bullets sit above or below the existing `### Planned for Future Releases` subsection, and whether that subsection is left exactly as it is (it should be — nothing in this phase changes what is planned).
- Whether a `### Verified` subsection is written under `## [Unreleased]` now or left for the v0.9.2 release-prep phase to author against the whole 0.9.2 diff. The latter is the cheaper default.
- Plan decomposition and ordering, and how the docs warning baselines for SC#3 are established (a prior phase's recorded baseline versus a fresh measurement on this tree).
- The mechanical form of the `REQUIREMENTS.md` checksum guard and where the two separated fence probes are recorded.
- The format and heading structure of `61-HANDOFF.md`, and where live-run evidence is recorded — **subject to the reserved-name constraint: do not name any evidence file `61-VERIFICATION.md`**, which the phase verifier owns and will clobber. The `52-*-EVIDENCE.md` / `60-*-EVIDENCE.md` families are the naming precedent.
- Whether a milestone-diff sweep anchored at the `v0.9.0` tag is worth running given that no `### Verified` claims are being authored in this phase (see the discretion item above). If one is run and it records a positive control, that control must be a real one — an assertion that *would* fail if the sweep were vacuous.

### Folded Todos

None. Every matched todo was reviewed and left in `pending/` — see Reviewed Todos below.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### This phase's requirements and success criteria

- `.planning/ROADMAP.md` § "Phase 61: v0.9.1 Release Prep (prep-only)" — the original goal and SC#1–SC#5. **Read together with D-11 above, never in isolation** — three of the five criteria are dropped or reworded by this file.
- `.planning/REQUIREMENTS.md` § "REL — release" — REL-09's exact wording, which D-08 leaves unchanged and unmet.
- `.planning/REQUIREMENTS.md` § "Standing constraints for every phase in this milestone" — constraint 5 (worktree isolation is the standing execution mode) and constraint 6 (the 3-OS CI acceptance bar) both bind this phase; constraints 1–4 concern product-code phases and do not.
- `.planning/REQUIREMENTS.md` § "Traceability" — the 11-of-11 v1 coverage table, which the CHANGELOG bullets' requirement-ID citations must agree with.

### The release-prep precedent to follow

- `.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-CONTEXT.md` — the immediately preceding release-prep phase. Its D-12 (CI dispatch count and rationale), D-13 AMENDED (the `uv.lock`-before-dispatch sequencing constraint, and the corrected 10-step `--locked` census), and its `### Claude's Discretion` reserved-name warning all carry forward. Its D-01–D-08 (breaking-change bullets, migration guide) do **not** — v0.9.1 has no breaking change and no migration guide.
- `.planning/milestones/v0.8.0-phases/52-v0-8-0-release-prep-prep-only/52-CONTEXT.md` — the authoring-from-scratch shape this phase's CHANGELOG work follows, and the `52-*-EVIDENCE.md` file-naming precedent.

### The defect families the CHANGELOG bullets describe

- `.planning/phases/58-repr-format-decoupling-test-side-only/58-REPR-CENSUS.md` — the census MSG-01 produced; the authority on which message sites existed before Phase 60 re-quoted them.
- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md` — PATH-01 / IMG-04 / IMG-05 / IMG-06 / IMG-07 evidence, including the real `typst.compile()` gate.
- `.planning/phases/60-one-delimiter-aware-path-quoting-helper-routed-everywhere/60-PATH-QUOTING-EVIDENCE.md` — MSG-02 through MSG-05 evidence, consolidated.
- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-VERIFICATION.md` and `.planning/phases/60-one-delimiter-aware-path-quoting-helper-routed-everywhere/60-VERIFICATION.md` — the two phases' verdicts; the source for any claim the CHANGELOG makes about what is now guaranteed.
- `.planning/phases/60-one-delimiter-aware-path-quoting-helper-routed-everywhere/60-CONTEXT.md` § D-01 AMENDED — records that `quote_path()` closes an apostrophe by **doubling** it rather than backslash-escaping. This is why a lead paragraph claiming the fixes are Windows-only would be inaccurate: a POSIX path containing an apostrophe was affected too.

### The blocker that is not being fixed or disclosed

- `.planning/todos/pending/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md` — reproduction, root cause, the six-row trigger matrix, and the solution sketch. D-05 and D-07 turn on this file.

### Version-literal and gate surfaces (must all stay untouched)

- `pyproject.toml:7` — `version = "0.9.0"`, the sole version literal.
- `README.md:347` — `**Status**: Stable (v0.9.0) - Production ready`.
- `tests/test_readme_version_sync.py` — asserts the two above agree; stays green because neither moves.
- `tests/test_changelog_page_gate.py:50-66` — `RELEASE_VERSIONS`, currently ending at `"0.9.0"`; **not** extended in this phase (D-01, out of scope).
- `tests/test_preview_version_sync.py` — the three-place `@preview` version lockstep guard; unrelated to the release version but part of the green bar.
- `CHANGELOG.md` — `## [Unreleased]` at the head (currently bullet-free) and the tail link-reference block ending `[Unreleased]: …/compare/v0.9.0...HEAD`.
- `docs/source/changelog.rst:1-2` — the `.. include:: ../../CHANGELOG.md` with `:parser: myst_parser.sphinx_` that makes every CHANGELOG link a published link. This is the measured basis for D-01 and D-04.

### Release machinery (recorded, not triggered)

- `scripts/extract_changelog_section.py` — the GitHub Release body's source. Exercised only by the v0.9.2 release-prep phase; named in `61-HANDOFF.md` (D-13).
- `.github/workflows/release.yml` — the publish path, not triggered in this phase.
- `.github/workflows/ci.yml` — the 3-OS matrix; `workflow_dispatch` is the only route that does not require opening a PR, and every job begins with `uv sync --extra dev --locked`.
- `.github/workflows/links.yml` — repo-wide lychee scan; **excludes `CHANGELOG.md`**, which is why a dead `[0.9.1]` link would not have been caught by CI (D-04).

### Standing project constraints

- `CLAUDE.md` § "Worktree-isolated execution" — mandatory per-worktree `uv sync` + `uv run` for every executor.
- `.planning/PROJECT.md` — the core-value statement that "a URL the project publishes must actually resolve", which D-01 and D-04 apply directly.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `scripts/extract_changelog_section.py` — extracts one `## [X.Y.Z]` section verbatim. Not usable in this phase (there is no versioned section to extract) but named in the handoff.
- `tests/test_readme_version_sync.py`, `tests/test_extension.py::test_version_matches_pyproject_toml`, `tests/test_preview_version_sync.py` — the version-sync guard family. All stay green trivially under D-01 because nothing moves; the plan should still run them as part of the SC#3 suite rather than reasoning that they cannot fail.
- The `.github/workflows/ci.yml` `workflow_dispatch` route — the only way to get a 3-OS run on this branch without opening a PR (`ci.yml`'s push trigger is `[main, develop]` only). Used at every prior milestone close.

### Established Patterns

- **CHANGELOG section vocabulary, measured across the whole file:** `### Fixed` (19 uses), `### Added` (14), `### Changed` (13), `### Verified` (9), `### Removed` (5). A `### Known Limitations` subsection exists exactly once, inside the `0.1.0b1` section. This is the vocabulary the `## [Unreleased]` bullets should draw from.
- **Requirement IDs in trailing parentheses** — house style since Phase 33; every 0.9.0 bullet carries them.
- **Evidence-file naming** — `{padded_phase}-{TOPIC}-EVIDENCE.md`, established by the `52-*` family and followed by `60-01-EVIDENCE.md` … `60-05-EVIDENCE.md`. `{padded_phase}-VERIFICATION.md` is reserved for the verifier and must not be used for plan-authored evidence.
- **`uv.lock` before CI dispatch** — every CI job starts with `uv sync --extra dev --locked` (10 steps across four workflows, per 57-CONTEXT D-13 AMENDED). Nothing in this phase should change dependencies, but if anything does, the lock must be regenerated and committed before dispatching.

### Integration Points

- `CHANGELOG.md`'s `## [Unreleased]` block is the only product-tree file this phase's content work writes to. Everything else it produces lives under `.planning/phases/61-*/`.
- `docs/source/changelog.rst` renders `CHANGELOG.md` into the published docs, so the `## [Unreleased]` bullets *are* user-visible on Read the Docs' `latest` even though no release exists. Write them as prose a user would read, not as internal shorthand.
- The `docs-html` and `docs-pdf` tox environments consume the same file, so a malformed MyST bullet block shows up as a docs-build warning — which is exactly what SC#3's warning-baseline check is for.

</code_context>

<specifics>
## Specific Ideas

1. **The lead framing, if the bullets carry one.** Do not write that these fixes are Windows-only. Measured basis: Phase 60's `quote_path()` closes an apostrophe by doubling it, so a POSIX user whose path contains an apostrophe was affected by the same defect family. "Windows-shaped paths, and any path containing a quote character" is accurate; "Windows users" alone is not.

2. **Three defect families, in the order the roadmap names them** — a Windows-shaped `typst_documents` target now refused by a predicate that normalizes before it decides; a Windows-shaped absolute image URI that now compiles; path-naming diagnostics that no longer double a separator or close their quote early.

3. **The handoff's first line should state the negative.** `61-HANDOFF.md` opens by saying that this milestone publishes nothing and that the checklist below is inherited by v0.9.2 — not by listing steps. Seven consecutive milestones have trained the reverse habit.

4. **Watch for the REL-09 auto-flip on `phase.complete`.** It has fired five times running. D-10's checksum guard is the detector; the response is to revert the flip before committing, not to accept it.

</specifics>

<deferred>
## Deferred Ideas

- **Rewriting ROADMAP.md's Phase 61 entry to match this file.** Offered and declined this session — the owner chose to let CONTEXT.md's decisions govern and leave the roadmap as the historical record of what was originally planned. D-11 exists to make that survivable. If a downstream gate proves too noisy about the mismatch, revisiting this is cheap.
- **Publishing v0.9.1 after all.** Foreclosed by D-02 for this milestone; a future milestone could revisit, at the cost described in D-02's reversibility note.
- **Disclosing the inline-image blocker on a public surface.** Foreclosed by D-05 for this phase; the natural place to revisit is the v0.9.2 release-prep phase, where it becomes a `### Fixed` bullet instead.

### Reviewed Todos (not folded)

All nine todos matched by `todo.match-phase 61` were reviewed and left in `.planning/todos/pending/`. None is folded into this phase.

- `2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md` (blocker) — **the reason this phase changed shape.** Deferred to the v0.9.2 milestone by D-07. Not folded: fixing it here would break the prep-only fence, and the owner chose the next milestone instead.
- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md` (minor) — the same MSG-02-shaped defect Phase 60 fixed, found by 60-05's repo-wide discovery grep in a fourth module (`translator.py:5047`, `:5152`) outside MSG-02..MSG-05's requirement scope. A natural companion to the blocker fix in v0.9.2, since both live in `translator.py`. Not folded: it is a `typsphinx/` behaviour change, which this phase excludes absolutely.
- `2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` — `release.yml`'s `create-release` job failed on the v0.7.0 tag push with `uv: command not found`, and has not been proven end-to-end since. Considered for `61-HANDOFF.md` as a pre-publish check. Not folded: with no publish in this milestone (D-02) there is nothing here to verify it against; it belongs to the v0.9.2 release-prep phase's handoff instead, and should be re-offered there.
- `2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md` — CI/tooling; unrelated to a phase that changes no dependency.
- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` — kept in `pending/` deliberately (57-CONTEXT D-13 AMENDED re-measured `ruff` as working and annotated rather than closed the todo, so the record survives if it recurs). No action here.
- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — a `typsphinx/` source-wide change; excluded by the fence.
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` — a new CI job; out of scope, though note it is the todo that would have caught the class of dead link D-04 avoids.
- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md` — docs structure; unrelated.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` — a translator defect; same fence exclusion as the blocker.

</deferred>

---

*Phase: 61-v0-9-1-release-prep-prep-only*
*Context gathered: 2026-08-29*
