# Phase 77: v0.9.7 Release Prep (prep-only) and the Trusted-Publishing Proof Handoff - Research

**Researched:** 2026-09-28
**Domain:** Release-mechanics prep (version bump, CHANGELOG curation, CI/lint/docs proof, PyPI
Trusted Publishing provenance handoff-writing) — no product code, no irreversible action.
**Confidence:** HIGH (this phase is almost entirely procedure this project has run six times before
— v0.9.2 Phase 63, v0.9.4 Phase 71, v0.9.5 Phase 73, v0.9.6 Phase 75 — plus two live external
measurements taken this session against PyPI's real Simple JSON and Integrity APIs)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Only area **D (failure branches and rollback placement)** was discussed; it is binding as written.
Areas A–C were offered and accepted at the owner's stated defaults without discussion, and are
equally binding — see "Claude's Discretion" below, which this project's convention treats as
locked once accepted.

**Failure branches of the publish half** (`77-HANDOFF.md` names all three):

| Shape | What happened | Path |
|---|---|---|
| ① pre-upload rejection (`invalid-publisher` / `invalid-pending-publisher`, or any failure before a file lands) | nothing on PyPI | fix registration → `gh run rerun <id> --failed` on the **same** run within 7 days; if that cannot succeed → D-02 |
| ② partial upload (e.g. wheel landed, sdist failed) | 0.9.7 filename(s) consumed | D-02 |
| ③ upload succeeded but ATT-03 fails (`provenance` null, or Integrity API not 200 / wrong `publisher`) | 0.9.7 is live and cannot be retried | D-01 |

- **D-01 (shape ③ — HALT, fix inside v0.9.7, no yank).** Close HALTs; ATT-05 (both secret
  deletions + PyPI revocation) and DOC-25 are **not** executed — the token stays the rollback path
  and DOC-25 would state a falsehood. Record the Simple JSON response, both Integrity API responses
  (status + body), and the release run's `Publish to PyPI` log excerpt; suspend
  `/gsd-complete-milestone`; insert a decimal phase (e.g. 77.1) to fix the cause; re-prove ATT-03 on
  **0.9.8** in the same milestone. 0.9.7 is **not** yanked. The five fenced checkboxes stay `[ ]`.
  **Reversibility: one-way** — 0.9.7 is permanently on PyPI once this branch is taken.
- **D-02 (leaving = always 0.9.8, never a re-tagged 0.9.7).** No branching on whether any file
  uploaded — even shape ① where Simple JSON shows zero 0.9.7 files. Delete the `v0.9.7` tag **both
  locally and on `origin`**, re-run release prep as **0.9.8** (bump, `## [0.9.7]` → `## [0.9.8]`
  CHANGELOG rewrite, tail links), publish 0.9.8, still on Trusted Publishing (D-03). 0.9.7 joins
  0.9.1 and 0.9.3–0.9.5 as unclaimed. **Reversibility: one-way** — a pushed-then-deleted tag with no
  release would be a first in this repository.
- **D-03 (restoring `password:` is a last resort, gated by explicit owner approval).** Default
  recovery order: (1) fix registration + same-run `gh run rerun --failed` within 7 days; (2)
  otherwise D-02's tag-delete + 0.9.8, **still without `password:`**. The two removed lines
  (`efde71a9`, ATT-01) are written out verbatim for the gated restore path only:
  ```yaml
          with:
            password: ${{ secrets.PYPI_API_TOKEN }}
  ```
  inserted directly after `uses: pypa/gh-action-pypi-publish@release/v1` in `Publish to PyPI`
  (measured this session at `release.yml:142`, re-measure at execution). Gated by "only when the
  owner explicitly states Trusted Publishing is being abandoned for this release." The token path
  disables attestations by construction — ATT-03 fails, landing in D-01's state (no ATT-05, no
  DOC-25, close suspended). **Reversibility: costly** — permanent, no provenance for that version.
- **D-04 (rollback lives inside `77-HANDOFF.md`, not a separate file).** Contains the ①–③ table,
  the re-run step, D-02's path, D-03's gated restore. Every ordered handoff step carries an
  explicit "on failure here → § <rollback section>" pointer (ROADMAP SC#4 requires the handoff
  readable standalone). **ATT-06's evidence** is the SHA of the commit adding this section, plus
  `git tag -l 'v0.9.7'` and `git ls-remote --tags origin` both empty at that commit, each with a
  `v0.9.6` positive control.

### Claude's Discretion

Offered as areas A–C, accepted at these defaults without discussion. Apply as written; do not re-ask.

- **A — ATT-04's grep target (carried from Phase 76 D-08 AMENDED).** `'attestations input ignored'`
  reads **0** on control run `35730551619` too — the phrase exists only in the annotation's
  `title=`, which `gh run view --log` never prints. Use the two-grep pair against the log body:
  `grep -c 'disabling Trusted Publishing'` (release **0** / control **1**) and
  `grep -c 'attestations input is ignored'` (release **0** / control **1**). `77-HANDOFF.md` uses
  this pair, names `35730551619` as the non-zero control, states the signal is
  necessary-but-not-sufficient. **`REQUIREMENTS.md:48` (ATT-04) and `ROADMAP.md:170/367/473` stay
  literal and unedited** — the reframing lives only in this CONTEXT/RESEARCH, per project
  convention, and keeps ATT-04's guarded line byte-stable under `77-CLOSEOUT-GUARD.md`.
- **B — `## [0.9.7]` section shape.** Re-count `## [Unreleased]` bullets at phase base (measured
  this session: **zero**, only `### Planned for Future Releases`). A short **lead paragraph**
  (modest register — MSG-06 is a DEBUG-log correctness fix, the publishing change affects artifact
  provenance not behaviour; do not reuse `[0.9.6]`'s "should upgrade" register). `### Changed`:
  Trusted Publishing / PEP 740 attestations bullet (ATT-01, ATT-02 IDs in trailing parens).
  `### Fixed`: MSG-06 bullet. `### Known Limitations`: **re-state NUM-01** verbatim-in-spirit —
  carry `[0.9.6]`'s content, promise no fix or version; expect **three** `### Known Limitations`
  headings after this phase (`[0.1.0b1]`, `[0.9.6]`, `[0.9.7]`) — measured this session at **two**
  before the phase (lines 91, 1256). `### Verified`: zero new runtime/zero new dev deps across
  `v0.9.6..HEAD` (**measure fresh** — do not copy `[0.9.6]`'s sentence, which was scoped to
  `v0.9.2..HEAD`; measured this session as **empty diff**, see § Verified Facts), the four
  `@preview` versions unchanged across the three sites (measured unchanged this session), MSG-06's
  recorded-RED gate (`tests/test_translator_path_quoting_gate.py`, closed in Phase 76). Heading
  date is the prep authoring date, fixed, not corrected at tag time.
- **C — Provenance wording.** Written before ATT-03 can pass, so it describes the **mechanism**:
  0.9.7 is published through PyPI Trusted Publishing, under which the publish action attaches PEP
  740 attestations recording the building workflow. States in words that these are **audit
  provenance, not an install-time gate — neither `pip` nor `uv` verifies them today**. May add one
  sentence on how a reader inspects provenance on PyPI — **measured this session**, see § Provenance
  UI Wording. If D-01/D-02 fire, this wording is revisited in 0.9.8 prep, not patched post-hoc.
- **Carried unchanged from Phase 75 precedent:** the bump commit carries the union `pyproject.toml`,
  `uv.lock` (regenerated by `uv lock`, never hand-edited), `README.md`
  (`**Status**: Stable (v0.9.7)`, measured this session at `README.md:348`), `CHANGELOG.md` and
  `tests/test_changelog_page_gate.py` (`RELEASE_VERSIONS` gains `"0.9.7"`; comment "17 releases …
  0.4.1 through 0.9.6" updated) in **one** commit; fresh `## [Unreleased]` keeps only
  `### Planned for Future Releases`; tail links: `[Unreleased]` compare `v0.9.6` → `v0.9.7`, new
  `[0.9.7]: …/releases/tag/v0.9.7` above `[0.9.6]`; `scripts/extract_changelog_section.py 0.9.7`
  executed and transcribed; non-committing trial merge (`git merge-tree --write-tree`,
  `uv lock --check`, `ruff check .`); `main` protection read via `gh api`; exactly one CI dispatch
  on the bumped, pushed tip (5xx → `gh run list` before any retry); clean docs builds
  (`rm -rf docs/_build`); the decoy `gsd/v0.9.7-milestone` branch rule; CLOSEOUT-GUARD mechanics
  (sha256 primary, re-run after `phase.complete`-family tooling, restore via `git checkout`, never
  committed; back up REQUIREMENTS/ROADMAP/STATE before that tooling runs). Guarded lines: ATT-03,
  ATT-04, ATT-05, REL-17, DOC-25 (plus traceability rows); ATT-06's line is expected to move.
- **DOC-25's target is one line, not two.** Measured this session:
  `.planning/codebase/INTEGRATIONS.md:116` reads
  `` `PYPI_API_TOKEN` - PyPI trusted publishing (used in release.yml, alternative to deprecated password) ``
  — exactly backwards (it is now the sole mechanism, not an alternative). `:117` is
  `TEST_PYPI_API_TOKEN` and stays. Handoff's DOC-25 step targets `:116` (re-measure at close), may
  pre-draft the replacement text, but the edit is applied only after ATT-05 completes.

### Deferred Ideas (OUT OF SCOPE)

None raised in discussion. Reviewed-but-not-folded todos: `2026-07-22-add-sphinx-linkcheck-ci-job.md`
(QUA-08, Future) and `2026-08-14-numref-…-non-root-only-figures.md` (NUM-01, disclosed only,
handled by Discretion B).

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ATT-06 | Rollback procedure recorded before any tag exists (closes in this phase) | § Architecture Patterns (Handoff/Closeout-Guard pattern), § Code Examples (rollback section skeleton), CONTEXT D-01..D-04 verbatim above |
| REL-17 | 0.9.7 published — bump + CHANGELOG + green tree (prep half closes here; tag/upload/Release checked at close) | § Code Examples (bump-commit shape, CHANGELOG section shape), § Common Pitfalls (version-sync, changelog-gate skip trap, linkcheck baseline), § Validation Architecture |
| ATT-03 | PyPI-served-state proof: Simple JSON non-null `provenance` + Integrity API 200 with correct `publisher` (coverage only — observed at close) | § Provenance Mechanics (live-measured this session against `pip` on real PyPI), § Code Examples (handoff command skeletons) |
| ATT-04 | Zero `attestations input ignored`/`disabling Trusted Publishing` annotation on the v0.9.7 release run (coverage only — observed at close) | § User Constraints Discretion A (the two-grep pair, carried from Phase 76 D-08 AMENDED) |
| ATT-05 | `PYPI_API_TOKEN` retired at both GitHub scopes + PyPI revocation, strictly after ATT-03 (coverage only — observed at close) | § Code Examples (handoff command skeleton), CONTEXT D-01/D-03 |
| DOC-25 | `.planning/codebase/INTEGRATIONS.md:116` corrected to describe the post-ATT-05 state (coverage only — observed at close) | § Verified Facts (exact current line text measured this session) |

</phase_requirements>

## Summary

Phase 77 is a **prep-only release phase**, the seventh of its kind in this project
(v0.7.0/v0.7.1/v0.8.0/v0.9.0/v0.9.2/v0.9.5/v0.9.6 each ran one). There is no new library to
evaluate, no new architectural pattern to introduce, and no product code to touch — the entire
domain is: bump the version in lockstep across four files in one commit, curate one CHANGELOG
section whose wording must not overclaim what PEP 740 attestations do, prove the bumped tree green
on runs *executed in this phase* (not inherited from Phase 76), write a rollback procedure before
any tag exists, and write a standalone `77-HANDOFF.md` that turns five post-tag requirements into
pre-written, already-measured commands — with **zero irreversible action** taken anywhere in the
phase. This project has run this exact shape six times before and has a live precedent
(`75-HANDOFF.md`, `75-CLOSEOUT-GUARD.md`) that is close enough to a structural template to be
copied and specialized rather than designed fresh.

Two things make this instance non-routine relative to the v0.9.6 precedent. First, the release's
own content is a **provenance claim about the release mechanism**, so the CHANGELOG wording is
under an accuracy constraint no prior release carried: it must describe PEP 740 attestations as
*audit* provenance, never an install-time gate, because — measured this session via WebSearch
against PyPI's own blog and PEP 740's own text — **neither `pip` nor `uv` verifies attestations at
install time today**; PEP 740 governs only how the index receives and serves them. Second, the
five post-tag requirements (ATT-03/04/05, DOC-25, REL-17's publish clauses) are **coverage-only**
in this phase — they close at `/gsd-complete-milestone`, never here — so this phase's own
Success-Criterion 4 is unusually load-bearing: the handoff must carry pre-written commands with
*already-measured* expected outputs and controls, not "go check X." This session live-measured the
real shape of that PyPI provenance data (against `pip`, a real PEP-740-attested project) so the
handoff's ATT-03 commands can be written with confidence rather than guessed.

**Primary recommendation:** copy `75-HANDOFF.md` and `75-CLOSEOUT-GUARD.md` structurally (same
section order, same fence mechanics, same three-observation protocol), splice in Phase 77's own
five-requirement publish sequence (merge → tag push → `pypi` approval → ATT-04 → ATT-03(a)/(b) →
ATT-05 → DOC-25 → translations `update-pin.yml` → RTD `en`/`ja` re-measure) with CONTEXT's D-01..D-04
failure-branch table folded in as the rollback section, and re-measure every line number, digest,
and `gh`/`curl` reading fresh at phase execution time rather than trusting this document's own
numbers past their capture moment.

## Architectural Responsibility Map

This phase touches no runtime code, so the usual browser/server/API/CDN/database tiers do not
apply. The relevant "tiers" here are process layers:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Version bump (pyproject.toml/uv.lock/README/CHANGELOG) | Repository (git commit) | — | A single atomic commit is the unit; splitting it is the exact shape that killed prior Dependabot PRs (SC#1) |
| CHANGELOG curation and wording accuracy | Documentation (CHANGELOG.md) | Release automation (`extract_changelog_section.py` reads it) | The extractor is purely positional and has no opinion on wording — accuracy is entirely a human/agent authoring responsibility |
| Green-tree proof (pytest, lint, docs, linkcheck, CI) | CI/CD (GitHub Actions `ci.yml`) | Local (`tox`) | `ci.yml`'s six required contexts are what `main`'s branch protection actually gates on; local `tox` runs are the pre-CI cross-check this project always performs in-phase |
| Rollback procedure (ATT-06) | Documentation (`77-HANDOFF.md`) | — | A written procedure, not code; "closes" by existing and being measured against, not by being executed |
| Post-tag proof commands (ATT-03/04/05, DOC-25) | Release automation (`/gsd-complete-milestone`) | PyPI's own served state (Simple JSON + Integrity APIs) | These requirements are explicitly coverage-only in this phase — the tier that actually closes them is outside this phase's fence entirely |
| Secret retirement (ATT-05) | GitHub repo/environment secrets + PyPI account | — | Two distinct GitHub-scoped secrets plus one PyPI-side revocation; none of the three is a code change |

## Standard Stack

No new libraries are introduced or evaluated in this phase. Every tool below is already in the
repository's `dev`/`docs` extras or is a system CLI already used by prior release-prep phases.

### Core (already in-repo, used as-is)
| Tool | Version (measured this session) | Purpose | Why Standard |
|------|------|---------|---------------|
| `uv` | 0.12.13 (main checkout; a fresh worktree resolves its own pinned/managed version — see Pitfalls) | dependency lock/sync, `uv lock` regeneration | Project's sole package manager since Phase 3x-era migration |
| `gh` (GitHub CLI) | 2.101.0 | CI dispatch, run inspection, secrets listing (names only), release/PR/branch-protection reads | Used identically in every prior release-prep phase (63/71/73/75) and in Phase 76 |
| `curl` + `jq` | present | PyPI Simple JSON API + Integrity API reads | Same tool pair Phase 76 used for `ATT-02`'s pre/post PyPI captures |
| `tox` (with `tox-uv`) | present | `docs-html`, `docs-pdf`, `linkcheck` environments | Standard per `CLAUDE.md` § Commands |
| `pytest`, `ruff`, `black`, `mypy` | present, versions to be re-measured at phase base (ruff has moved 0.16.8 → 0.16.9 on `origin/main` since Phase 76 — see § Verified Facts) | the four-part lint/type/test gate `ci.yml`'s `validate` job and `release.yml`'s `validate` job both run | Standard per `CLAUDE.md` |

### Supporting
| Tool | Purpose | When to Use |
|------|---------|-------------|
| `scripts/extract_changelog_section.py` | Produces the GitHub Release body from `CHANGELOG.md`'s `## [X.Y.Z]` section, purely positionally | Run against `0.9.7` in this phase (SC#2) to prove the section extracts cleanly before any tag exists |
| `git merge-tree --write-tree` | Non-committing trial merge of `origin/main` into the branch | SC#3's trial-merge requirement; `origin/main` has moved since this milestone's base (measured this session — see § Verified Facts), so this is not a no-op this time |
| `sha256sum`, `wc -l`, `git diff --name-only` | The CLOSEOUT-GUARD fence's four probes | Copy `75-CLOSEOUT-GUARD.md`'s exact probe set, line-scoped to this phase's five guarded requirements |

### Alternatives Considered

None — this phase has no library-selection decision to make. The only "alternative" that exists in
the domain is *whether* to restore `password:` on `publish-pypi` as a rollback path, which CONTEXT
D-03 has already settled (last resort, explicit owner gate only).

**Installation:** none — no new dependency is added. `uv sync --extra dev --extra docs` (docs extra
required for the changelog-page-gate tests, see Pitfalls) in a freshly provisioned worktree per
`CLAUDE.md` § Worktree-isolated execution.

**Version verification performed this session:**
- `uv --version` → `0.12.13` (main checkout only; re-measure per-worktree)
- `gh --version` → `2.101.0`
- `python3 --version` → `3.13.13` (main checkout, nixpkgs-provided; a fresh worktree resolves
  uv-managed CPython — measured 3.14 in Phase 75's worktree, per its own `75-CLOSEOUT-GUARD.md`)
- `pyproject.toml`/`uv.lock` diff `v0.9.6..HEAD`: **empty** — zero dependency change since the last
  tag, confirming Discretion B's "zero new runtime/dev dependency" claim for the `v0.9.6..HEAD`
  range as it stands today. **Re-measure at phase base**, not trusted from this document, because
  the open Dependabot PR #157 (`types-docutils` bump) has not yet merged as of this measurement.

## Package Legitimacy Audit

**Not applicable.** This phase installs zero new external packages — measured this session as an
empty `git diff v0.9.6..HEAD -- pyproject.toml uv.lock`. No `npm view`/`pip index versions` legitimacy
check is needed because no package name is being newly introduced anywhere in this phase's scope.

## Architecture Patterns

### System flow this phase produces (not a runtime data-flow diagram — a documentation/proof pipeline)

```
┌─────────────────┐      ┌──────────────────────┐      ┌───────────────────────┐
│ 1. Bump commit    │ ──▶ │ 2. Green-tree proof   │ ──▶ │ 3. ATT-06 + Handoff    │
│  pyproject.toml   │      │  pytest×2, lint trio, │      │  rollback procedure    │
│  uv.lock (uv lock) │      │  docs-html/pdf clean, │      │  + pre-written,        │
│  README.md status  │      │  linkcheck, CI dispatch│     │  pre-measured publish- │
│  CHANGELOG.md       │      │  on bumped tip,        │     │  half commands         │
│  test_changelog_    │      │  non-committing trial  │     │  (77-HANDOFF.md)       │
│  page_gate.py        │      │  merge of origin/main  │     └───────────┬────────────┘
└─────────┬───────────┘      └───────────┬────────────┘                 │
          │                              │                              ▼
          │                              │                  ┌───────────────────────┐
          │                              │                  │ 4. CLOSEOUT-GUARD fence│
          │                              │                  │  sha256/wc-l/grep on   │
          │                              │                  │  ATT-03/04/05/REL-17/  │
          │                              │                  │  DOC-25 lines, 3       │
          └──────────────┬───────────────┘                  │  observations          │
                          ▼                                 └───────────┬────────────┘
              ┌────────────────────────┐                                │
              │ Phase 77 close:         │◀───────────────────────────────┘
              │ SUMMARY.md's            │
              │ requirements-completed  │
              │ = [ATT-06] only         │
              └────────────────────────┘
                          │
                          ▼   (OUTSIDE this phase — /gsd-complete-milestone)
              ┌─────────────────────────────────────────────┐
              │ Publish half: PR merge → tag push → pypi     │
              │ approval → ATT-04 (log grep) → ATT-03(a)     │
              │ Simple JSON → ATT-03(b) Integrity API →      │
              │ ATT-05 (2 GH secrets + PyPI revoke) → DOC-25 │
              │ → update-pin.yml → RTD en/ja re-measure      │
              └─────────────────────────────────────────────┘
```

### Recommended Artifact Structure (mirrors `75-*`, renamed for Phase 77)

```
.planning/phases/77-.../
├── 77-01-PLAN.md .. 77-0N-PLAN.md   # per-plan work (bump, changelog, green-tree, trial-merge, CI, closeout-guard, handoff)
├── 77-0N-SUMMARY.md                 # one per plan; requirements-completed: [] until the ATT-06 plan
├── 77-BUMP-EVIDENCE.md              # the one-commit bump, verbatim `git show --name-only`
├── 77-CHANGELOG-EVIDENCE.md         # extractor stdout transcript, byte-match digest
├── 77-GREEN-TREE-EVIDENCE.md        # local pytest×2/lint/docs/linkcheck readings
├── 77-CI-EVIDENCE.md                # dispatch id, job table, both windows/macos lanes named
├── 77-PREFLIGHT-EVIDENCE.md         # trial-merge, main protection, open-PR census
├── 77-ATT06-EVIDENCE.md             # rollback procedure's own evidence (tag-empty × 2 observations)
├── 77-CLOSEOUT-GUARD.md             # line-scoped fence for ATT-03/04/05/REL-17/DOC-25
├── 77-HANDOFF.md                    # standalone, self-contained publish-half procedure
└── COVERAGE.md
```

### Pattern 1: The prep-half / publish-half split with a standalone `NN-HANDOFF.md`
**What:** every irreversible release action (PR merge, tag push, PyPI upload, GitHub Release,
secret deletion, PyPI revocation) is deferred to `/gsd-complete-milestone` and enumerated in a
standalone handoff document, never executed inside the phase.
**When to use:** every published-release milestone this project has shipped since v0.9.2 (Phase 63,
71, 73, 75).
**Example (this session's live-measured skeleton for the ATT-03 step, the one genuinely new command
pair in this milestone's handoff):**
```bash
# ATT-03(a) — Simple JSON API, non-null provenance for BOTH files
curl -s https://pypi.org/simple/typsphinx/ \
  -H 'Accept: application/vnd.pypi.simple.v1+json' \
| jq -r '.files[] | select(.filename | startswith("typsphinx-0.9.7")) | "\(.filename)\t\(.provenance)"'
# Expected (measured this session against a real attested project, `pip`):
# a NON-null value here is a URL string pointing at the Integrity API endpoint below —
# not a boolean `true`. Example real reading (pip 26.2.1, not typsphinx):
#   pip-26.2.1-py3-none-any.whl   https://pypi.org/integrity/pip/26.2.1/pip-26.2.1-py3-none-any.whl/provenance
# The 0.9.6 control (measured Phase 76, re-confirm at Phase 77 base):
#   typsphinx-0.9.6-py3-none-any.whl   null
#   typsphinx-0.9.6.tar.gz             null

# ATT-03(b) — Integrity API, 200 with correct publisher
curl -s -o /dev/null -w '%{http_code}\n' \
  "https://pypi.org/integrity/typsphinx/0.9.7/<filename>/provenance"
curl -s "https://pypi.org/integrity/typsphinx/0.9.7/<filename>/provenance" \
| jq '.attestation_bundles[0].publisher'
# Expected shape (measured this session against pip's real Integrity API response):
#   {"environment": "pypi", "kind": "GitHub", "repository": "YuSabo90002/typsphinx", "workflow": "release.yml"}
# The 0.9.6 control (measured Phase 76): HTTP 404 for the wheel filename.
```

### Pattern 2: Line-scoped `NN-CLOSEOUT-GUARD.md` fence, re-checked after `phase.complete`-family tooling
**What:** a SHA-256 digest of `.planning/REQUIREMENTS.md`, plus `wc -l` and a scoped `grep -n`
transcript of exactly the guarded requirement lines, recorded at phase head, re-verified at phase
close, and **re-verified a third time after `phase.complete`-family tooling has actually run** —
because that tooling has flipped a deferred release checkbox at **9 of the 10** prior release-prep
closes (measured and recorded in every prior `NN-CLOSEOUT-GUARD.md` back to Phase 61).
**When to use:** every release-prep phase where some requirements close in-phase (here: ATT-06 only)
and others are coverage-only (here: ATT-03/04/05/REL-17/DOC-25) — a whole-file digest would false-
positive on the legitimate ATT-06 flip, so the fence must be **line-scoped**, exactly as Phase 75's
was line-scoped to REL-15 while letting REL-16 move freely.
**Example — the exact reversion recipe Phase 75 used and this phase should copy verbatim:**
```bash
sha256sum .planning/REQUIREMENTS.md      # compare against the phase-head digest
wc -l .planning/REQUIREMENTS.md          # compare against the phase-head line count
git diff --name-only -- .planning/REQUIREMENTS.md   # expect empty until phase-completion tooling runs
grep -n 'ATT-03\|ATT-04\|ATT-05\|REL-17\|DOC-25' .planning/REQUIREMENTS.md
# On divergence confined to those five: git checkout -- .planning/REQUIREMENTS.md, re-run probes, MATCH.
# On divergence confined to ATT-06's own lines flipping [ ] -> [x]: that is this phase's own
# legitimate completion and is NOT reverted (mirrors Phase 75's REL-16 exception).
```

### Anti-Patterns to Avoid
- **Trusting a cached line-number citation instead of re-measuring.** ROADMAP's own `:141-144`
  citation for ATT-01 was wrong by two lines (would have deleted the publish step itself) and
  Phase 76 caught it only by re-measuring. This phase inherits the identical risk for
  `README.md:348`, `release.yml:142`, `INTEGRATIONS.md:116`, `REQUIREMENTS.md:48`,
  `ROADMAP.md:170/367/473` — every one of these was re-measured this session (see § Verified Facts)
  but **must be re-measured again at phase execution**, since this document's numbers age from the
  moment they were captured.
- **Treating a non-null `provenance` field as a boolean.** The Simple JSON API's `provenance` value
  for an attested file is a **URL string** pointing at the Integrity API endpoint, not `true` —
  measured this session against `pip`'s real PyPI listing. A plan that writes `jq '.provenance == true'`
  would silently fail to match even a correctly-attested 0.9.7.
- **Writing the CHANGELOG's provenance wording as a completed fact.** The section is authored
  *before* ATT-03 can possibly pass (no tag exists yet), so it must describe the *mechanism*
  ("0.9.7 is published through PyPI Trusted Publishing, which attaches PEP 740 attestations"), never
  a result ("0.9.7's provenance has been verified") — CONTEXT Discretion C states this explicitly and
  ROADMAP SC#2 requires the wording "cannot be misread as an install-time guarantee."
- **Re-dating the `## [0.9.7]` heading at tag time.** Phase 75's own handoff records this as a
  standing non-step: the heading date is the prep-authoring date and stays fixed even if the actual
  tag lands days later (precedent: `[0.9.2]` merged a day after its heading date, `[0.9.0]` tagged
  five days later).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Extracting a release's CHANGELOG body for the GitHub Release notes | A second parser or a `git log` dump | `scripts/extract_changelog_section.py` (already the ONE committed, pytest-covered implementation, D-06 of an earlier phase) | Prevents the exact regression `release.yml` used to have — a 296-commit raw `git log` dump as release notes (v0.6.4) |
| Detecting whether `origin/main` has moved and whether a merge would be clean | Manually diffing files by eye | `git merge-tree --write-tree` (non-committing) + `uv lock --check` + `ruff check .` on the merged tree | Exactly the check Phase 75's `75-PREFLIGHT-EVIDENCE.md` ran; **this phase's origin/main has in fact moved** (measured this session — three Dependabot PRs merged, `uv.lock`-only diff), so this is not a formality this time |
| Confirming a fresh worktree has the right tooling before running any gate | Assuming `uv sync --extra dev` is sufficient | `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs` (docs extra is required for the 4 changelog-page-gate tests to run rather than skip) | Documented worktree hazard (CLAUDE.md, memory) — omitting `--extra docs` produces a false "gate passed" reading via 4 silent skips |

**Key insight:** every tool this phase needs already exists and is already proven working in this
exact repository across six prior release-prep phases. The only genuine risk in this domain is
*measurement discipline* — trusting a stale line number, a stale grep target, or an unmeasured
"zero new dependencies" claim — not a missing library or an unfamiliar pattern.

## Common Pitfalls

### Pitfall 1: Worktree provisioning omits the `docs` extra, producing silent skips read as a pass
**What goes wrong:** `uv sync --extra dev` alone leaves `myst_parser` absent, so all 4 tests in
`tests/test_changelog_page_gate.py` that require it **skip** rather than run — and a naive pytest
summary line ("4 passed" elsewhere, nothing failing) reads as clean.
**Why it happens:** the `docs` extra is not part of the default worktree-provisioning line named in
CLAUDE.md's headline example; it must be added explicitly for this specific gate.
**How to avoid:** provision with `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs`,
and read skip reasons with `pytest -rs`, not just the pass/fail totals. SC#1 explicitly requires
"the changelog page gate running at zero skipped in an environment carrying the docs extra."
**Warning signs:** any pytest summary line containing `skipped` for this test file.

### Pitfall 2: Incremental docs rebuild under-reports warnings, manufacturing a false baseline match
**What goes wrong:** comparing a warning count from an incremental `tox -e docs-html`/`docs-pdf`
build against a "clean" baseline produces a match even when the bumped tree actually introduces new
warnings, because Sphinx's incremental builder skips unchanged pages.
**Why it happens:** `docs/_build` caches per-page build state across invocations.
**How to avoid:** `rm -rf docs/_build` before every warning-baseline reading, both the "baseline
taken at this phase's own base" reading and the "bumped tip" reading — ROADMAP SC#3 requires this
explicitly.
**Warning signs:** a warning count that looks suspiciously identical to a much earlier reading
despite intervening content changes.

### Pitfall 3: Locale-dependent tool/diff output silently diverges from what CI actually produces
**What goes wrong:** a `grep`/`diff`/pytest-output comparison run under the host's `ja_JP.UTF-8`
locale can format numbers, dates, or diagnostic text differently than the English locale CI runs
under, producing a spurious mismatch (or a spurious match) when comparing local output against a
CI-recorded expectation.
**Why it happens:** the host's `LANG` is `ja_JP.UTF-8` (documented project convention); CI always
runs English.
**How to avoid:** run the full pytest suite once under plain locale and once under `LC_ALL=C`
(ROADMAP SC#3 requires exactly this — "the full pytest suite passes twice, once under `LC_ALL=C`").
Any command whose output will be compared byte-for-byte against a CI transcript should run under
`LC_ALL=C`.
**Warning signs:** a diff or grep count that differs between two runs of the identical command with
no code change in between.

### Pitfall 4: A cached line-number or grep-target citation is trusted instead of re-measured
**What goes wrong:** ROADMAP's own `release.yml:141-144` citation for ATT-01 was off by two lines
(measured and corrected in Phase 76); `76-CONTEXT.md`'s original ATT-04 grep target
(`attestations input ignored`) was measured to read **zero on the non-zero control too** (D-08
AMENDED) because the phrase lives only in a workflow-command `title=` attribute that `gh run view
--log` never renders.
**Why it happens:** planning documents (ROADMAP, REQUIREMENTS, CONTEXT) cite line numbers and
strings captured at an earlier moment; the file moves.
**How to avoid:** every plan in this phase that cites a line number or a grep target must re-derive
it with a live command (`grep -n`, `sed -n`) rather than copy the number from ROADMAP/REQUIREMENTS/
this RESEARCH document.
**Warning signs:** a `sed -n '<N>,<M>p'` readout that doesn't match the expected surrounding context
verbatim.

### Pitfall 5: `phase.complete`-family tooling auto-flips a deferred release checkbox
**What goes wrong:** `/gsd-execute-phase`'s `phase.complete` step and `/gsd-verify-work`'s inline
transition have both flipped a coverage-only release requirement's checkbox to `[x]` against an
explicit CONTEXT decision, at **9 of the 10** prior release-prep closes (per `75-CLOSEOUT-GUARD.md`
§ "Why this file exists," itself citing `73-CLOSEOUT-GUARD.md`).
**Why it happens:** unknown root cause internal to that tooling; it is treated as a known, recurring
hazard rather than something this phase can fix.
**How to avoid:** the three-observation CLOSEOUT-GUARD protocol (phase head, phase close, and once
more **after** `phase.complete`-family tooling has actually run) — the third observation is the one
that actually catches the flip, since it happens after the tooling call. Revert with
`git checkout -- .planning/REQUIREMENTS.md` if the flip is confined to the five guarded requirements;
do **not** revert if it is confined to ATT-06's own lines (that flip is legitimate).
**Warning signs:** `sha256sum .planning/REQUIREMENTS.md` no longer matching the phase-head digest
after `phase.complete`-family tooling has run.

### Pitfall 6: `origin/main` moves between this phase's close and `/gsd-complete-milestone`
**What goes wrong:** the trial merge recorded in this phase (against `origin/main` as it stood at
measurement time) can go stale before the actual release PR merges, especially since Dependabot is
active on this repository (three PRs merged since this milestone's base, per § Verified Facts, plus
one currently open — #157).
**Why it happens:** Dependabot runs continuously and is not paused for a release-prep phase.
**How to avoid:** `77-HANDOFF.md` must instruct `/gsd-complete-milestone` to re-read `origin/main`
live at release time rather than trust this phase's own trial-merge reading — exactly the
instruction `75-HANDOFF.md` step 1 already contains ("`origin/main` must be re-read live at release
time regardless, because it can move between this phase's close and `/gsd-complete-milestone`'s own
run").
**Warning signs:** `git merge-base HEAD origin/main` at release time differing from the SHA recorded
in this phase's trial-merge evidence.

## Verified Facts (measured this session, phase base = commit `d872bafa`)

All of the following were measured live against this repository and, where noted, against real
external services, in this research session. Re-measure at plan/execution time — these are a
starting point, not a substitute for each plan's own fresh reading.

| Fact | Value | Source |
|---|---|---|
| `pyproject.toml` current version | `0.9.6` | [VERIFIED: pyproject.toml:7] — `version = "0.9.6"` |
| `README.md` Status line | `**Status**: Stable (v0.9.6) - Production ready` at line 348 | [VERIFIED: README.md:348] |
| `release.yml`'s `Publish to PyPI` step | no `with:`/`password:` (already two-line-deleted by Phase 76) | [VERIFIED: .github/workflows/release.yml:141-143] — `- name: Publish to PyPI` / `uses: pypa/gh-action-pypi-publish@release/v1` / blank line before `# Create GitHub Release` |
| CONTEXT D-03's restore-target line | `uses: pypa/gh-action-pypi-publish@release/v1` at line 142 | [VERIFIED: .github/workflows/release.yml:142] |
| `INTEGRATIONS.md` DOC-25 target | `- \`PYPI_API_TOKEN\` - PyPI trusted publishing (used in release.yml, alternative to deprecated password)` at line 116; `- \`TEST_PYPI_API_TOKEN\` - TestPyPI API token (optional, for pre-release testing)` at line 117 (stays) | [VERIFIED: .planning/codebase/INTEGRATIONS.md:116-117] |
| `CHANGELOG.md` `## [Unreleased]` content | empty except `### Planned for Future Releases`, zero release bullets | [VERIFIED: CHANGELOG.md:8-15] |
| `CHANGELOG.md` `### Known Limitations` heading count | 2 (`[0.1.0b1]` and `[0.9.6]`) | [VERIFIED: `grep -n '^### Known Limitations' CHANGELOG.md` → lines 91, 1256] |
| `CHANGELOG.md` tail link block | `[0.9.6]: …/releases/tag/v0.9.6` present; `[Unreleased]: …/compare/v0.9.6...HEAD` present | [VERIFIED: CHANGELOG.md tail, last ~15 lines] |
| `pyproject.toml`/`uv.lock` diff since `v0.9.6` tag | empty | [VERIFIED: `git diff v0.9.6..HEAD -- pyproject.toml uv.lock`] — confirms Discretion B's zero-new-dependency claim for the current tree; **re-measure**, Dependabot PR #157 is still open |
| `git log v0.9.6..HEAD -- CHANGELOG.md` | empty | [VERIFIED] — every `[0.9.7]` bullet is written fresh in this phase, none pre-exists |
| `tests/test_changelog_page_gate.py` `RELEASE_VERSIONS` | 17-tuple, `"0.4.1"` .. `"0.9.6"`, comment reads "The 17 releases the published page was frozen without (0.4.1 through 0.9.6, inclusive)" | [VERIFIED: tests/test_changelog_page_gate.py:44-62] |
| `@preview` version-sync sites | `codly:1.3.0`, `codly-languages:0.1.10`, `mitex:0.2.7`, `gentle-clues:1.3.1`, identical across `typsphinx/writer.py:266-269`, `typsphinx/template_engine.py:705-708`, `typsphinx/templates/base.typ:8,9,14,19` | [VERIFIED: three files' grep output, quoted above] |
| `v0.9.7` tag, local | absent | [VERIFIED: `git tag -l 'v0.9.7'` → empty] |
| `v0.9.7` tag, remote | absent | [VERIFIED: `git ls-remote --tags origin 'refs/tags/v0.9.7*'` → empty] |
| `v0.9.6` tag positive control | present, both local and remote | [VERIFIED: `git tag -l 'v0.9.6'` → `v0.9.6`; `git ls-remote --tags origin 'refs/tags/v0.9.6*'` → `refs/tags/v0.9.6` + `^{}`] |
| `origin/main` has moved since milestone base | **yes** | [VERIFIED: `git merge-base HEAD origin/main` = `9fa1cb89…` ≠ `git rev-parse origin/main` = `eeba55aa…`] — three Dependabot PRs merged (#158 tox, #159 ruff, #160 sphinx-autodoc-typehints), `uv.lock`-only diff, 27 insertions/27 deletions |
| Open pull requests | 1 — Dependabot #157 (`types-docutils` bump) | [VERIFIED: `gh pr list --state open`] — re-measure at execution, this census is a snapshot |
| `main` branch protection | `strict: true`; 6 required contexts: `Test Python 3.12 on ubuntu-latest`, `Lint and Format Check`, `Type Check`, `Code Coverage`, `Build Package`, `Test Python 3.13 on ubuntu-latest`; PR review NOT required | [VERIFIED: `gh api repos/YuSabo90002/typsphinx/branches/main/protection`] — note the required contexts do **not** include the Windows/macOS lanes by name, even though ROADMAP SC#3 requires the dispatched CI run to name both `windows-latest` and both `macos-latest` lanes in its own transcript regardless of protection-required status |
| Merge methods allowed on the repo | merge commit, squash, and rebase all allowed | [VERIFIED: `gh api repos/YuSabo90002/typsphinx` → `allow_merge_commit/allow_squash_merge/allow_rebase_merge` all `true`] — historically every milestone PR has landed as a real merge commit (Phase 75's own note: 103/103 first-parent `Merge pull request #` hits) |
| Local `HEAD` vs. pushed `gsd/v0.9.7-trusted-publishing-and-release` | local ahead by `.planning/`-only commits (`d872bafa` vs. pushed `987ec3fe`) | [VERIFIED: `git log`/`git ls-remote --heads origin`] — mirrors the exact situation Phase 75's handoff step 1 flagged ("push the branch again before tagging") |
| ruff version drift since Phase 76's own CI run | `0.16.8` (Phase 76 evidence) → `0.16.9` (merged via Dependabot PR #159, now on `origin/main`) | [VERIFIED: `git log` on the origin/main-moved range above] — the trial merge and the bumped-tip CI dispatch in this phase will run against `0.16.9`, not `0.16.8` |

## Provenance Mechanics (live-measured this session against PyPI's real APIs)

These are the concrete shapes ATT-03's handoff commands will read, measured against `pip` (a real,
already-Trusted-Publishing-attested PyPI project) rather than assumed from training knowledge —
`typsphinx` itself has no attested files yet (v0.9.6 was measured `provenance: null` in Phase 76).

- **Simple JSON API `provenance` field is a URL, not a boolean.** [VERIFIED: live `curl` against
  `https://pypi.org/simple/pip/` with `Accept: application/vnd.pypi.simple.v1+json`] — of 289 files
  listed for `pip`, 26 carry a non-null `provenance` value, and that value is itself a URL string
  of the exact shape `https://pypi.org/integrity/pip/<version>/<filename>/provenance`. A plan that
  checks `provenance != null` (not `provenance == true`) is correct; ROADMAP's own phrasing
  ("non-null `provenance`") already matches this shape.
- **Integrity API response shape.** [VERIFIED: live `curl` against
  `https://pypi.org/integrity/pip/26.2.1/pip-26.2.1-py3-none-any.whl/provenance`] — HTTP 200,
  JSON body with `attestation_bundles[0].publisher` = `{"environment": "pypi", "kind": "GitHub",
  "repository": "pypa/pip", "workflow": "release.yml"}`. This confirms ATT-03(b)'s exact assertion
  shape: `jq '.attestation_bundles[0].publisher'` and comparing `repository`/`workflow`/`environment`
  fields. For `typsphinx`, the expected values are `repository: "YuSabo90002/typsphinx"`,
  `workflow: "release.yml"`, `environment: "pypi"` (per REQUIREMENTS.md ATT-03's own text).
- **Neither `pip` nor `uv` verifies attestations at install time today.** [CITED:
  https://blog.pypi.org/posts/2024-11-14-pypi-now-supports-digital-attestations/ and
  https://peps.python.org/pep-0740/] — PEP 740 governs only how the index receives and serves
  attestations; it "does not make a policy recommendation around mandatory digital attestations on
  release uploads or their subsequent verification by installing clients like pip." Verification
  today is manual, via the Integrity API. This directly supports CONTEXT Discretion C's required
  CHANGELOG wording ("audit provenance, not an install-time gate").
- **PyPI's own UI wording for a reader inspecting provenance** (for Discretion C's optional one-
  sentence pointer). [CITED: https://pypi.org/project/pip/#files, fetched live this session] — the
  project files page shows, per attested file: "Provenance describes where a file came from. On
  PyPI, provenance is shared via **attestations**, which provide a verifiable record of the build or
  publishing details," with a "View details, limitations and caveats" link, and per-attestation:
  "PyPI verified that this artifact, at this checksum, originated from the publisher listed below,"
  followed by "Signed by GitHub Actions, verified by PyPI on <date>." A CHANGELOG sentence pointing
  a reader at "the file's page on pypi.org, which shows a 'Provenance' panel with the attesting
  workflow" would be accurate to this measured wording.

## Validation Architecture

`.planning/config.json`'s `workflow.nyquist_validation` is `true` (present, not absent) —
[VERIFIED: .planning/config.json:23] — so this section is required.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (pre-existing) |
| Quick run command | `LC_ALL=C pytest -q tests/test_readme_version_sync.py tests/test_changelog_page_gate.py tests/test_preview_version_sync.py` |
| Full suite command | `LC_ALL=C pytest -q` (run twice per SC#3: once plain locale, once `LC_ALL=C`) |

### Phase Requirements → Test Map
Phase 77's own requirements are documentation/process requirements, not code behaviors — the
"tests" here are the oracle commands SC#1–5 already specify verbatim, not new pytest functions.

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REL-17 (prep half, SC#1) | version bump lockstep | unit | `pytest -q tests/test_readme_version_sync.py` | ✅ |
| REL-17 (prep half, SC#1) | changelog-page-gate zero-skip | integration (needs `docs` extra) | `pytest -rs -q tests/test_changelog_page_gate.py` | ✅ |
| REL-17 (prep half, SC#2) | one curated `## [0.9.7]` section extracts cleanly | script | `uv run python scripts/extract_changelog_section.py 0.9.7` | ✅ |
| REL-17 (prep half, SC#3) | `@preview` sync unbroken | unit | `pytest -q tests/test_preview_version_sync.py` | ✅ |
| ATT-06 (SC#4) | no `v0.9.7` tag anywhere | probe | `git tag -l 'v0.9.7'` + `git ls-remote --tags origin 'refs/tags/v0.9.7*'` | n/a — shell probe |
| (SC#5, all 5 coverage-only reqs) | fence lines unchanged | probe | `sha256sum .planning/REQUIREMENTS.md` + scoped `grep -n` | n/a — shell probe |

### Sampling Rate
- **Per task commit:** the specific oracle command that task's own SC targets (e.g. the bump task
  runs `test_readme_version_sync.py`; the CHANGELOG task runs the extractor).
- **Per wave merge:** `LC_ALL=C pytest -q` full suite (once).
- **Phase gate:** full suite green (both locale runs) + lint trio + docs-html/docs-pdf clean +
  linkcheck + CI dispatch green, before the CLOSEOUT-GUARD and HANDOFF plans run — since those two
  plans' own evidence should be recorded against an already-proven-green tip.

### Wave 0 Gaps
None — every test file this phase depends on (`test_readme_version_sync.py`,
`test_changelog_page_gate.py`, `test_preview_version_sync.py`) already exists and passes today
(measured indirectly via Phase 76's own full-suite run, "1573 passed, 1 skipped" per
`76-VERIFICATION.md`; re-run fresh at this phase's own base rather than trusted from Phase 76's
reading).

## Security Domain

`.planning/config.json`'s `workflow.security_enforcement` is `true`
[VERIFIED: .planning/config.json:41], `security_asvs_level: 1`, so this section is required. This
phase, however, touches no application code, no user input path, and no authentication/session
surface — its only security-adjacent content is *secret lifecycle* (ATT-05, coverage-only, not
executed here) and *supply-chain provenance* (the subject of the CHANGELOG wording, also not a code
change).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | no auth surface touched |
| V3 Session Management | no | no session surface touched |
| V4 Access Control | no | no access-control surface touched |
| V5 Input Validation | no | no new input-handling code (the phase writes prose/config, not parsers) |
| V6 Cryptography | no (indirectly relevant, not owned here) | PEP 740 attestations use Sigstore/Rekor signing, already implemented by `pypa/gh-action-pypi-publish` — this phase never hand-rolls any cryptographic operation, only *describes* one in prose |
| V1 (Secure Design) — secret lifecycle | partially, coverage-only | ATT-05's two-scope GitHub secret deletion + PyPI revocation is written as a pre-measured handoff command in this phase, never executed; the existing `PYPI_API_TOKEN`/`TEST_PYPI_API_TOKEN` secrets are read by name only (`gh secret list --json name`), never by value, mirroring Phase 76's own `76-ATT-EVIDENCE.md` practice |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Overclaiming a security property in release notes (a reader believes attestations are verified automatically) | Spoofing (of assurance level) | The wording constraint this phase's own CONTEXT enforces: "audit provenance, not an install-time gate" — measured accurate against PEP 740's own text and PyPI's blog post this session |
| A rollback procedure that silently reintroduces the token path without an explicit gate | Repudiation / Tampering (of the publishing mechanism) | CONTEXT D-03's explicit owner-approval gate before restoring `password:`, with the consequence (ATT-03 fails by construction) stated in the handoff itself |
| A long-lived API token retired too early (before ATT-03 proves the new path works) | Elevation of Privilege (loss of rollback capability) | ATT-05 is strictly gated behind ATT-03 passing — a constraint this phase's handoff encodes as command *ordering*, not merely prose |

## Code Examples

### The one-commit version bump (SC#1 shape, mirrors `75-BUMP-EVIDENCE.md`'s pattern)
```bash
# Inside a provisioned worktree (uv sync --extra dev --extra docs already run)
sed -i 's/^version = "0.9.6"$/version = "0.9.7"/' pyproject.toml
uv lock                      # regenerates uv.lock's typsphinx stanza — never hand-edit uv.lock
sed -i 's/\*\*Status\*\*: Stable (v0.9.6)/\*\*Status\*\*: Stable (v0.9.7)/' README.md
# ... CHANGELOG.md edited by hand (curation, not scriptable) ...
# ... tests/test_changelog_page_gate.py's RELEASE_VERSIONS tuple + comment edited by hand ...
git add pyproject.toml uv.lock README.md CHANGELOG.md tests/test_changelog_page_gate.py
git commit -m "chore(release): bump version to 0.9.7"
git show --name-only HEAD   # must list exactly these five files together (SC#1)
uv sync --extra dev --locked   # must exit 0
```

### CHANGELOG section skeleton (Discretion B, mirrors `[0.9.6]`'s own shape at CHANGELOG.md:16-108)
```markdown
## [0.9.7] - <prep authoring date, fixed>

<Short, modest lead paragraph — no "should upgrade" register. Names the DEBUG-message fix and the
publishing-mechanics change in one or two sentences.>

### Changed

- **0.9.7 is published through PyPI Trusted Publishing (ATT-01, ATT-02).** `release.yml`'s
  `publish-pypi` step mints its own OIDC token rather than reading a long-lived API token, which
  turns on `pypa/gh-action-pypi-publish`'s default PEP 740 attestations. These attestations are
  **audit provenance, not an install-time gate** — neither `pip` nor `uv` verifies them
  automatically today. <optional one sentence, measured wording per § Provenance UI Wording, on
  how a reader can inspect them on PyPI's own project page.>

### Fixed

- **<MSG-06 bullet — the two cross-directory relative-path DEBUG logs no longer close a quote
  early when a path contains a literal single quote.>**

### Known Limitations

- **<NUM-01 bullet, carried verbatim in spirit from `[0.9.6]`'s own entry — still unfixed, no
  promised fix or version.>**

### Verified

- No new runtime dependency and no new dev dependency were added across this milestone's diff
  (`v0.9.6..HEAD`) — <state the measured empty-diff result fresh, do not copy [0.9.6]'s sentence,
  which was scoped to v0.9.2..HEAD>.
- The four bundled `@preview` package version strings are unchanged across all three declaration
  sites (`typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ`).
- <MSG-06's recorded-RED gate, `tests/test_translator_path_quoting_gate.py`, closed in Phase 76.>
```

### CLOSEOUT-GUARD baseline capture (mirrors `75-CLOSEOUT-GUARD.md`'s § "Baseline")
```bash
sha256sum .planning/REQUIREMENTS.md
wc -l .planning/REQUIREMENTS.md
grep -n 'ATT-03' .planning/REQUIREMENTS.md
grep -n 'ATT-04' .planning/REQUIREMENTS.md
grep -n 'ATT-05' .planning/REQUIREMENTS.md
grep -n 'REL-17' .planning/REQUIREMENTS.md
grep -n 'DOC-25' .planning/REQUIREMENTS.md
grep -n 'ATT-06' .planning/REQUIREMENTS.md   # NOT under guard — expected to move
# Also back up outside the repo, per Phase 75 precedent:
S=$(mktemp -d)
cp .planning/REQUIREMENTS.md .planning/ROADMAP.md .planning/STATE.md "$S/"
sha256sum "$S"/*.md
```

## State of the Art

Not applicable in the usual "library ecosystem moved" sense — this phase's domain is entirely
internal project process. The one genuine "state of the art" shift worth naming is the milestone's
own subject:

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `release.yml` publishes with a long-lived `PYPI_API_TOKEN` (`password:` key) | `release.yml` publishes via OIDC/Trusted Publishing, no stored credential | Phase 76 of this milestone (2026-09-27) | Phase 77 does not touch this mechanism again — it only writes the CHANGELOG wording and the post-tag proof commands that observe it |

**Deprecated/outdated:** long-lived `PYPI_API_TOKEN` as the *primary* publish credential — already
retired from the code path in Phase 76; this phase's only remaining relationship to it is ATT-05's
eventual (coverage-only, out-of-phase) deletion and ATT-06's rollback procedure, which may
*temporarily* reintroduce it only under CONTEXT D-03's explicit owner gate.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The exact `gh api repos/.../branches/main/protection` reading (6 named contexts, `strict: true`, no required PR review) will still hold at phase execution time | § Verified Facts | Low — branch protection changes rarely and is re-read live by every prior phase's own `PREFLIGHT-EVIDENCE.md`; SC#3 already requires re-reading it "rather than assumed" |
| A2 | `typsphinx-0.9.7-py3-none-any.whl` / `typsphinx-0.9.7.tar.gz` will be the exact filenames the wheel/sdist build produces (no name/version-normalization surprise) | § Code Examples (ATT-03 command skeleton) | Low — filenames have followed this exact pattern for every prior release (`typsphinx-0.9.6-py3-none-any.whl` etc., confirmed in Phase 76 evidence) |
| A3 | The Integrity API's `attestation_bundles[0]` index (element 0) will be the single relevant bundle for typsphinx's 0.9.7 files, as it was for the `pip` example measured this session | § Provenance Mechanics | Low-Medium — if a file somehow accumulates multiple attestation bundles the handoff's `jq` path would need `.attestation_bundles[]` (all) rather than `[0]`; worth a defensive read (`length`) in the actual handoff command rather than hardcoding index 0 |
| A4 | Zero new runtime/dev dependencies will still hold at the phase's actual execution base, after Dependabot PR #157 (`types-docutils`) is resolved one way or another | § User Constraints Discretion B, § Standard Stack | Medium — if #157 merges into `origin/main` before this phase's own trial-merge/CI-dispatch step, `uv.lock` will show a change that must be correctly attributed to the merge, not misread as "this phase added a dependency" — the CHANGELOG's own "Verified" sentence must be measured against `v0.9.6..<phase's own HEAD>`, not against `origin/main`'s moved tip |

**If this table is empty:** not applicable — see rows above. None of these assumptions bear on a
compliance, retention, or security-standard claim; all are measurement-currency risks intrinsic to
planning ahead of execution, and all are already mitigated by this phase's own SC text requiring
fresh re-measurement at each step.

## Open Questions

1. **Will `origin/main` move again between this phase's own trial-merge reading and
   `/gsd-complete-milestone`'s actual release PR merge?**
   - What we know: it has already moved once since the milestone base (three Dependabot PRs), and
     one more Dependabot PR (#157) is currently open.
   - What's unclear: whether #157 merges before this phase's own CI-dispatch/trial-merge plan runs,
     which would change the exact `origin/main` SHA this phase's evidence records.
   - Recommendation: follow Phase 75's own handoff instruction verbatim — record the phase's own
     trial-merge reading, but have `77-HANDOFF.md` explicitly instruct `/gsd-complete-milestone` to
     re-read `origin/main` live at release time rather than trust the phase-time reading.

2. **Will PyPI's real Integrity API response for `typsphinx` 0.9.7 have exactly one
   `attestation_bundles` entry, matching this session's `pip` measurement?**
   - What we know: `pip`'s real response (measured live this session) has exactly one bundle per
     file, with `publisher` at `.attestation_bundles[0].publisher`.
   - What's unclear: whether a first-time-attested project (typsphinx has never had an attested
     upload before) could differ in bundle count or shape.
   - Recommendation: the handoff's ATT-03(b) command should read `.attestation_bundles | length`
     defensively alongside `.attestation_bundles[0].publisher`, so a genuinely unexpected shape
     HALTs and is investigated rather than silently mis-indexed.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | version bump, `uv lock`, worktree provisioning | ✓ | 0.12.13 (main checkout; per-worktree may differ) | — |
| `gh` (authenticated) | CI dispatch, `gh api` protection reads, `gh pr list`, future `gh secret list` (names only) | ✓ | 2.101.0, logged in as `YuSabo90002` | — |
| `curl` + `jq` | PyPI Simple JSON + Integrity API reads (handoff commands) | ✓ | present | — |
| `tox` | `docs-html`, `docs-pdf`, `linkcheck` | ✓ | present (re-measure per-worktree) | — |
| `pytest`/`ruff`/`black`/`mypy` | green-tree proof | ✓ | present (re-measure per-worktree; ruff has moved 0.16.8→0.16.9 on `origin/main`) | — |
| Network access to `pypi.org` | ATT-03 handoff command rehearsal/verification | ✓ (confirmed live this session) | — | — |
| Network access to `github.com`/GitHub Actions API | CI dispatch, run-log reads, branch-protection reads | ✓ (confirmed live this session via `gh`) | — | — |

**Missing dependencies with no fallback:** none identified.

**Missing dependencies with fallback:** none identified — every tool this phase needs is already
present in this environment. The only genuine per-worktree risk is the documented uv-managed-CPython
interpreter drift (worktree resolves its own CPython, potentially 3.14 vs. the main checkout's
nixpkgs 3.13.13) and the `--extra docs` omission hazard, both already covered in § Common Pitfalls.

## Sources

### Primary (HIGH confidence — measured live this session, or read from source files this session)
- Local repository state: `pyproject.toml`, `README.md`, `CHANGELOG.md`, `.github/workflows/release.yml`,
  `.planning/codebase/INTEGRATIONS.md`, `tests/test_changelog_page_gate.py`,
  `tests/test_readme_version_sync.py`, `tests/test_preview_version_sync.py`,
  `scripts/extract_changelog_section.py`, `.planning/config.json` — all read directly with `Read`/`grep`/`sed` this session.
- `git` state: tags, `origin/main` merge-base, branch protection, merge-method config, open PRs —
  all measured live via `git`/`gh` this session.
- PyPI Simple JSON API — `curl https://pypi.org/simple/pip/` (live, this session).
- PyPI Integrity API — `curl https://pypi.org/integrity/pip/26.2.1/pip-26.2.1-py3-none-any.whl/provenance` (live, this session).
- `.planning/phases/76-.../76-ATT-EVIDENCE.md`, `76-VERIFICATION.md` — Phase 76's own live-measured
  evidence for typsphinx's 0.9.6 control readings (Simple JSON `provenance: null`, control-run grep
  counts), read this session, not re-executed (Phase 76 is closed and verified).
- `.planning/milestones/v0.9.6-phases/75-v0-9-6-release-prep-prep-only/75-HANDOFF.md`,
  `75-CLOSEOUT-GUARD.md` — the structural template this research recommends copying, read this
  session.

### Secondary (MEDIUM confidence — official documentation, fetched/searched this session)
- PEP 740 – Index support for digital attestations: https://peps.python.org/pep-0740/
- PyPI Blog, "PyPI now supports digital attestations":
  https://blog.pypi.org/posts/2024-11-14-pypi-now-supports-digital-attestations/
- PyPI project files page (`pip`), for the measured UI wording of the provenance panel:
  https://pypi.org/project/pip/#files

### Tertiary (LOW confidence)
- None used as evidence for any claim in this document.

## Metadata

**Confidence breakdown:**
- Standard stack / process: HIGH — no new tooling, six prior identical phases as precedent
- Architecture / handoff pattern: HIGH — copying a proven, twice-audited structural template
  (`75-HANDOFF.md`/`75-CLOSEOUT-GUARD.md`)
- Provenance mechanics (ATT-03 command shapes): HIGH for the mechanism (live-measured against a
  real attested PyPI project this session), MEDIUM for the exact typsphinx-specific values (cannot
  be measured until 0.9.7 is actually uploaded, which is out of this phase's scope by design)
- Pitfalls: HIGH — every pitfall listed is either directly measured this session or documented in a
  prior phase's own evidence file with a specific run/commit citation

**Research date:** 2026-09-28
**Valid until:** re-measure all § Verified Facts and § Provenance Mechanics readings at phase
execution — this document's git/PyPI/GitHub-API readings are point-in-time and this project's own
`origin/main` has already been shown to move mid-milestone. Treat this document as stale for any
line-number, digest, or live-API claim older than a few days.
