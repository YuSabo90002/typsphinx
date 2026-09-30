# Phase 77: v0.9.7 Release Prep (prep-only) and the Trusted-Publishing Proof Handoff - Context

**Gathered:** 2026-09-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Bump the tree to 0.9.7, curate one `## [0.9.7]` CHANGELOG section, prove the bumped tree green,
record the rollback procedure (ATT-06 — the one requirement this phase closes) while **no `v0.9.7`
tag exists anywhere**, and write a standalone `77-HANDOFF.md` that turns the publish half (ATT-03,
ATT-04, ATT-05, DOC-25 and REL-17's publish clauses) into pre-written commands with expected
outputs and controls, in a fixed order. **Zero irreversible action inside the phase**: no tag
(local or remote), no PyPI upload, no GitHub Release, no secret deleted, no PR merged. Prep-only
fence: nothing under `typsphinx/`, nothing under `.github/workflows/`, no `docs/source/` content
change beyond version strings. ROADMAP Phase 77 SC 1–5 and its cross-cutting constraints are the
binding acceptance text; this file records only what the discussion added or settled on top.

</domain>

<decisions>
## Implementation Decisions

Only area **D (failure branches and rollback placement)** was discussed. Areas A–C were offered and
the owner chose to write context at their stated defaults — they are recorded under
**Claude's Discretion** below and are binding on the planner as written.

### Failure branches of the publish half (all written into `77-HANDOFF.md`)

Measured basis (`.github/workflows/release.yml` at phase base): `publish-pypi` is `needs: build`;
`build` uploads `dist-packages` with `retention-days: 7` (`:124`); `create-release` is
`needs: [build, publish-pypi]` with no `if:` override, so a failed publish leaves it *skipped* and
no GitHub Release is created. Three failure shapes follow and the handoff names all three:

| Shape | What happened | Path |
|---|---|---|
| ① pre-upload rejection (`invalid-publisher` / `invalid-pending-publisher`, or any failure before a file lands) | nothing on PyPI | fix the PyPI registration → `gh run rerun <id> --failed` on the **same** run within the 7-day window; if that cannot succeed → D-02 |
| ② partial upload (e.g. wheel landed, sdist failed) | 0.9.7 filename(s) consumed | D-02 |
| ③ upload succeeded but ATT-03 fails (`provenance` null for either file, or Integrity API not 200 / wrong `publisher`) | 0.9.7 is live and cannot be retried | D-01 |

- **D-01: On shape ③ the close HALTs and the fix happens inside v0.9.7.** ATT-05 (both secret
  deletions and the PyPI revocation) and DOC-25 are **not** executed — the token is still the
  rollback path and DOC-25 would describe a state that is not true. The handoff instructs:
  record the Simple JSON API response, both Integrity API responses (status + body), and the
  release run's `Publish to PyPI` log excerpt as evidence; suspend `/gsd-complete-milestone`;
  investigate; insert a decimal phase (e.g. 77.1) into v0.9.7 to fix the cause; re-prove ATT-03 on
  **0.9.8** in the same milestone. 0.9.7 is **not** yanked (missing provenance is not a user-facing
  defect). The five fenced checkboxes stay `[ ]` throughout. — **Reversibility:** one-way — by the
  time this branch is taken 0.9.7 is permanently on PyPI; the decision only governs what the close
  does next.

- **D-02: Leaving the same-run re-run always means 0.9.8, never a re-tagged 0.9.7.** No branching
  on whether any file was uploaded. ATT-06 literal: delete the `v0.9.7` tag **both locally and on `origin`**,
  re-run release prep as 0.9.8 (version bump, `## [0.9.7]` → `## [0.9.8]` CHANGELOG rewrite, tail
  links), and publish 0.9.8 — still on Trusted Publishing (D-03). This holds even in shape ① where
  Simple JSON shows zero 0.9.7 files and re-tagging 0.9.7 would technically be possible: the owner
  chose one unconditional rule over a judgement step at close time. 0.9.7 then joins 0.9.1 and
  0.9.3–0.9.5 as unclaimed. No AMENDED reading of ATT-06 is needed. — **Reversibility:** one-way —
  deleting a pushed tag is visible to anyone who fetched it, and a pushed-then-deleted tag with no
  release would be a first in this repository.

- **D-03: Restoring `password:` is a last resort behind explicit owner approval.** Never a default
  step. The handoff's default recovery order is: (1) fix registration + same-run
  `gh run rerun --failed` within 7 days; (2) otherwise D-02's tag delete + 0.9.8, **still without
  `password:`**. The restore procedure is written out verbatim — the two lines removed by
  `efde71a9` (Phase 76 / ATT-01), re-inserted directly after `uses: pypa/gh-action-pypi-publish@release/v1`
  in the `Publish to PyPI` step (measured at phase base as `release.yml:142`; re-measure before use):

  ```yaml
          with:
            password: ${{ secrets.PYPI_API_TOKEN }}
  ```

  and gated by the condition "only when the owner explicitly states that Trusted Publishing is being
  abandoned for this release". The handoff must say why: the token path makes the action disable
  attestations, so ATT-03 fails **by construction** — using it ships MSG-06 but lands the milestone
  in D-01's state (no ATT-05, no DOC-25, close suspended). — **Reversibility:** costly — a
  token-path upload is permanent and carries no provenance for that version.

### Placement of the rollback procedure

- **D-04: The rollback procedure is a section inside `77-HANDOFF.md`, not a separate file.**
  It contains the ①–③ table, the re-run step, D-02's tag-delete + 0.9.8 path, and D-03's gated
  `password:` restore. Every ordered step of the handoff's main sequence (merge → tag push → `pypi`
  approval → ATT-04 → ATT-03 → ATT-05 → DOC-25 → translations pin → RTD) carries an explicit
  "on failure here → § <rollback section>" pointer. Reason: ROADMAP SC#4 requires the handoff to be
  readable without the roadmap or any phase file, and a split file would break that literally.
  **ATT-06's evidence** is the SHA of the commit that adds this section, together with
  `git tag -l 'v0.9.7'` and a remote tag probe (`git ls-remote --tags origin`) both empty at that
  commit, each with a positive control (e.g. `v0.9.6`).

### Claude's Discretion

Offered to the owner as areas A–C and accepted at these defaults without discussion. The planner
applies them as written and does not re-ask.

- **A — ATT-04's grep target (carried from Phase 76 D-08 AMENDED).** Measured in Phase 76:
  `'attestations input ignored'` reads **0** on control run `35730551619` too (the phrase exists
  only in the annotation's `title=`, which `gh run view --log` never prints). The evidence pair is
  therefore two greps on the log body, each against the control:
  `grep -c 'disabling Trusted Publishing'` → release run **0** / control **1**, and
  `grep -c 'attestations input is ignored'` → release run **0** / control **1**.
  - **`77-HANDOFF.md` uses this two-grep pair** for ATT-04, names `35730551619` as the non-zero
    control, and states the signal is necessary-but-not-sufficient.
  - **`.planning/REQUIREMENTS.md:48` (ATT-04) and `.planning/ROADMAP.md:170`, `:367`, `:473` are
    left literal and unedited.** The reframing lives here, per this project's convention that
    requirement text stays literal and reframings live in phase CONTEXT. This also keeps ATT-04's
    guarded line byte-stable under `77-CLOSEOUT-GUARD.md`. The handoff says in one sentence that
    the requirement's quoted phrase is superseded by this pair and why.
  - This is the "alignment in Phase 77" that Phase 76 D-08 AMENDED deferred here.

- **B — `## [0.9.7]` section shape.** Measured at discussion time: `## [Unreleased]` holds **no**
  bullets (only `### Planned for Future Releases`), and `git log v0.9.6..HEAD -- CHANGELOG.md` is
  empty — every `[0.9.7]` bullet is written fresh in this phase (re-count at phase base per SC#2).
  - A short **lead paragraph**, like every released section. Upgrade recommendation is **modest**:
    MSG-06 only corrects DEBUG-log quoting, and the publishing change affects artifact provenance,
    not behaviour — do not use the "should upgrade" register `[0.9.6]` used.
  - `### Changed`: the Trusted Publishing / PEP 740 attestations bullet (ATT-01, ATT-02 IDs in the
    trailing-parenthesis style). `### Fixed`: the MSG-06 bullet (a path containing a literal `'` no
    longer closes the quote early in the two cross-directory relative-path DEBUG messages).
  - `### Known Limitations`: **re-state NUM-01** — it is still unfixed in 0.9.7 and a reader of
    only the newest section must not conclude it was fixed. Carry the `[0.9.6]` entry's content;
    promise no fix or version. Any grep-based check must then expect **three**
    `### Known Limitations` headings in the file (`[0.1.0b1]`, `[0.9.6]`, `[0.9.7]`).
  - `### Verified`: precise invariance claims only, each measured — zero new runtime and zero new
    dev dependencies across `v0.9.6..HEAD` (**measure; do not copy** `[0.9.6]`'s sentence, which
    was specific to that diff), the four `@preview` versions unchanged across the three sync
    sites, and MSG-06's recorded-RED gate (`tests/test_translator_path_quoting_gate.py`).
  - Heading date is the prep authoring date, fixed, not corrected at tag time (75 D-05 carried).

- **C — Provenance wording.** The CHANGELOG is written before ATT-03 can pass, so it describes the
  **mechanism**, not a proven result: 0.9.7 is published through PyPI Trusted Publishing, under
  which the publish action attaches PEP 740 attestations recording the building workflow. It states
  in words that these are **audit provenance, not an install-time gate — neither `pip` nor `uv`
  verifies them today**. It may add one sentence on how a reader can inspect provenance on PyPI;
  the exact PyPI UI wording/location must be **measured** (fetch a known attested project's PyPI
  file page or the Integrity API) before it is written, never recalled. If D-01/D-02 fire, this
  wording is revisited in the 0.9.8 prep rather than patched post-hoc.

- **Carried unchanged from Phase 75 (v0.9.6 release prep):** the bump commit carries the union
  `pyproject.toml`, `uv.lock` (regenerated by `uv lock`, never hand-edited), `README.md`
  (`**Status**: Stable (v0.9.7)`, measured at `README.md:348`), `CHANGELOG.md` and
  `tests/test_changelog_page_gate.py` (`RELEASE_VERSIONS` gains `"0.9.7"`; its comment "17 releases
  … 0.4.1 through 0.9.6" is updated to match) in **one** commit — bump and CHANGELOG are not split;
  fresh `## [Unreleased]` keeps only `### Planned for Future Releases`; tail links:
  `[Unreleased]` compare `v0.9.6` → `v0.9.7` and a new `[0.9.7]: …/releases/tag/v0.9.7` above
  `[0.9.6]`; `scripts/extract_changelog_section.py 0.9.7` executed and transcribed; non-committing
  trial merge (`git merge-tree --write-tree`, `uv lock --check`, `ruff check .` on the merged tree);
  `main` protection read via `gh api`; exactly one CI dispatch on the bumped, pushed tip (5xx →
  `gh run list` before any retry); clean docs builds (`rm -rf docs/_build`); the decoy
  `gsd/v0.9.7-milestone` branch rule; the CLOSEOUT-GUARD mechanics (sha256 primary, re-run after
  `phase.complete`-family tooling, restore via `git checkout`, never committed; back up
  REQUIREMENTS/ROADMAP/STATE before that tooling runs). The guarded lines are ATT-03, ATT-04,
  ATT-05, REL-17 and DOC-25 (plus their traceability rows); ATT-06's line is expected to move.

- **DOC-25's target is one line, not two.** Measured: `.planning/codebase/INTEGRATIONS.md:116` is
  the `PYPI_API_TOKEN - PyPI trusted publishing …` line; `:117` is `TEST_PYPI_API_TOKEN` and stays.
  The handoff's DOC-25 step targets `:116` (re-measured at close) and may pre-draft the replacement
  text, but the edit is applied only after ATT-05 completes.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and acceptance
- `.planning/ROADMAP.md` § v0.9.7 (binding constraints 1–14) and § Phase 77 (SC 1–5, cross-cutting constraints)
- `.planning/REQUIREMENTS.md` — ATT-03…ATT-06, REL-17, DOC-25; § Binding constraints; § Traceability (the "half" split and the fixed publish-half order)

### Phase 76 outputs this phase reads
- `.planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-ATT-EVIDENCE.md` — rehearsal run `36321530105`, pre-dispatch PyPI capture (0.9.6 `provenance: null`, file list), control-grep readings
- `.planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-CONTEXT.md` — D-07 (same-run rerun recovery), D-08 AMENDED (two-grep ATT-04 pair)
- `.planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-VERIFICATION.md` — records the ATT-04 wording alignment as deferred to Phase 77

### Release-prep precedent (v0.9.6)
- `.planning/milestones/v0.9.6-phases/75-v0-9-6-release-prep-prep-only/75-CONTEXT.md` — D-01…D-15 and Claude's Discretion (bump union, fence, trial merge, handoff shape)
- `.planning/milestones/v0.9.6-phases/75-v0-9-6-release-prep-prep-only/75-HANDOFF.md` — structural template for `77-HANDOFF.md`
- `.planning/milestones/v0.9.6-phases/75-v0-9-6-release-prep-prep-only/75-CLOSEOUT-GUARD.md` — line-scoped fence template

### Files the phase touches or reads
- `.github/workflows/release.yml` — job graph (`needs:`, `retention-days: 7`, `create-release` skip semantics); read only, never edited in this phase
- `CHANGELOG.md` — `## [0.9.6]` section as shape precedent (lead paragraph, Known Limitations NUM-01 entry, Verified)
- `scripts/extract_changelog_section.py`
- `tests/test_changelog_page_gate.py` (`RELEASE_VERSIONS`), `tests/test_readme_version_sync.py`
- `.planning/codebase/INTEGRATIONS.md:116` — DOC-25 target (edited only at the close, after ATT-05)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/extract_changelog_section.py` — produces the GitHub Release body; SC#2 requires executing it on `0.9.7`.
- `76-ATT-EVIDENCE.md` — already holds the 0.9.6 controls (Simple JSON `provenance: null`, run `35730551619` grep counts) the handoff cites.

### Established Patterns
- Prep-half / publish-half split with a standalone `NN-HANDOFF.md` (Phases 63, 71, 73, 75).
- Line-scoped `NN-CLOSEOUT-GUARD.md` fence re-checked after `phase.complete`-family tooling (Phase 75).
- Evidence in named `77-*-EVIDENCE.md` files, never in `77-VERIFICATION.md` (reserved by `gsd-verifier`).

### Integration Points
- `/gsd-complete-milestone` consumes `77-HANDOFF.md` and executes every irreversible step.
- `typsphinx-doc-translations` `update-pin.yml` (manual dispatch) and Read the Docs `en`/`ja` `stable` (cache-busted re-measure) at the tail of the handoff.

</code_context>

<specifics>
## Specific Ideas

- The owner's through-line for D: **the milestone does not close on an unproven provenance claim.**
  Every failure branch either recovers on Trusted Publishing or halts the close; none of them
  finishes the milestone on the token path.
- The handoff should make shape ③ unmistakable from shape ① — the distinguishing reading is
  whether the Simple JSON API lists any 0.9.7 file.

</specifics>

<deferred>
## Deferred Ideas

None raised in discussion.

### Reviewed Todos (not folded)
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` (QUA-08) — keyword-only match; a new workflow is out of this prep-only phase's fence and QUA-08 is Future.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` (NUM-01) — not fixed here; only re-disclosed in `[0.9.7]`'s `### Known Limitations` (Discretion B). The todo stays pending.

</deferred>

---

*Phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff*
*Context gathered: 2026-09-28*
