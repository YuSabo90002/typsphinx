# Phase 71: v0.9.4 Close Prep (prep-only, unpublished) - Research

**Researched:** 2026-09-13
**Domain:** GSD release-prep mechanics (CHANGELOG authoring, checksum-fenced requirement guarding,
non-committing trial merge, CI dispatch and job-census transcription, standalone milestone handoff)
**Confidence:** HIGH — this phase is a near-exact repeat of a shape this project has executed nine
times before, most recently and most closely `v0.9.3`'s Phase 69, whose full plan/evidence/review/
verification set is archived and was read in full for this research.

## Summary

Phase 71 does not introduce new technology. It reuses a release-prep pattern this project has run
at every milestone close since `v0.7.0` and has held the requirement-flip fence correctly at both
of the last two closes (Phase 61, Phase 69). The nearest precedent, `v0.9.3`'s Phase 69
(`.planning/milestones/v0.9.3-phases/69-v0-9-3-close-prep-prep-only-unpublished/`), matches this
phase's shape almost line for line: one CHANGELOG bullet under the existing `## [Unreleased]` →
`### Changed`, a checksum-guard file for the release requirement's checkbox, a local green-tree
proof, one CI dispatch with a 12-job transcript, a non-committing trial-merge pre-flight, and a
standalone handoff for `/gsd-complete-milestone`. Every evidence-file name, `KEY = value` line
shape, and command sequence below is drawn from that precedent's own live transcripts (not
templates) — Phase 69's own `69-VERIFICATION.md` independently re-ran every measurement and scored
8/8, so the shape is proven, not merely documented.

Two things are genuinely new versus Phase 69 and must not be treated as reused boilerplate. First,
D-11 (a Phase-71-only obligation, absent from Phase 69's precedent because Phase 69 had no
immediately-preceding code phase in the same milestone): the close tip must show an empty
`typsphinx/`+`tests/` diff against **Phase 70's own final code commit** — measured here as
`e721ff899a981eafdad696ef1a9c93aaab41ece5` — and Phase 70's masked-AST hash equality must be
re-run against Phase 70's `PHASE_BASE_SHA` (`697a113221a8a267d7e8c6dd1f2b95672f9454d2`) for the ten
converted files. Second, D-02's AMENDED CONTEXT decision drops the "ja translation catalogs" clause
that Phase 69's bullet-writing precedent did not have to navigate (Phase 69's bullets carried no
such clause at all) — the new bullet's evidence sentence is Phase 70's leg (d) byte-identical `.typ`
corpus result, not a translation-catalog timing claim.

**Primary recommendation:** decompose into 6 plans across 3 waves, mirroring Phase 69's wave shape
exactly (Wave 1: CHANGELOG bullet + clean-docs proof, and the closeout-guard baseline + SC#1
observation 1 + COVERAGE.md; Wave 2: local green-tree proof, CI push+dispatch, and the D-07-shaped
trial-merge pre-flight; Wave 3: SC#1 observation 2 + closeout-guard re-verification + standalone
handoff), with the CHANGELOG-authoring plan additionally carrying D-11's masked-AST re-run and the
Phase-70-final-commit diff check (since both need the converted-file list and mask harness that
only that plan's context loads cleanly).

## User Constraints (from CONTEXT.md)

<user_constraints>

### Locked Decisions

- **D-01: One bullet, appended as the fourth under the existing `### Changed`, after the `flake.nix` bullet.** It follows the house register of the three above it: a bold lead phrase ending with the requirement IDs in trailing parentheses (`QUA-09, QUA-11, QUA-12, DOC-22, DOC-23`), then prose written for a reader of the published changelog page (`docs/source/changelog.rst` includes `CHANGELOG.md`, so this text reaches Read the Docs `latest` once REL-13 merges). It names the API-reference type-text change with the concrete example `Dict[str, Any]` → `dict[str, Any]`, and it states plainly that the change has no effect on installing or using typsphinx. It does not name `v0.9.4`, `0.9.4`, `v0.9.3` or `0.9.3` anywhere in the prose, because no release carries those numbers.

- **D-02: The bullet says nothing about the Japanese site or its translation catalogs. REL-13 and ROADMAP SC#2 carry an AMENDED block recording this.** The owner chose to drop the sentence, not correct it. The literal clause ("the ja translation catalogs pick it up at the next published release") was falsified by measurement (see the domain section). The ja `latest` site follows `main` within about a day through the daily `update-pin.yml` schedule, not at a release. The ja API reference is untranslated (0/668), so it shows the same English type text the en bullet already describes. The AMENDED blocks were appended in the same commit as this CONTEXT, before the phase's fence baseline. **No Phase 71 plan writes `.planning/REQUIREMENTS.md`.** `grep` for `ja`, `Japanese` or `catalog` inside the new bullet must come back empty.

- **D-03: The bullet carries exactly one evidence sentence, saying that emitted Typst output and runtime behaviour are unchanged.** It cites the byte-identical `.typ` output over the test-fixture corpus, the leg (d) result. Any number in it (the project count, for instance) is transcribed from `70-AFTER-RUNTIME-EVIDENCE.md` / `70-CORPUS-DOCS-BASE-EVIDENCE.md` at execution time, never from this file. It does not enumerate the five QUA-12 legs, and it does not cite pytest or mypy figures. This matches v0.9.3's one-sentence evidence register ("A CI run … was green across the Linux, Windows and macOS test lanes").

- **D-04: Everything else in `CHANGELOG.md` is byte-identical.** That covers the three v0.9.3 bullets, the `### Planned for Future Releases` block, every versioned section and the tail link block. The `[Unreleased]` compare base stays `v0.9.2`. There is no `### Verified` subsection and no lead paragraph under `## [Unreleased]` (Phase 69 D-04: the next release-prep phase authors those when it promotes the bullets). `scripts/extract_changelog_section.py` is not run for a new section.

- **D-05: The milestone branch does not absorb `main` inside this phase. Today there is nothing to absorb.** `origin/main` equals the merge-base (`d14ca458`), measured. SC#3's non-committing trial merge is still run at execution time and transcribed verbatim: `git fetch origin`, then `git merge-tree --write-tree HEAD origin/main` (exit code and tree SHA), `uv lock --check` on that tree's `pyproject.toml` + `uv.lock` extracted to scratch, and `ruff check .` on the merged tree at the merged lock's `ruff` version. It catches the case constraint 4 names, a `main` that moved (a dependabot `ruff` bump, say) between now and execution. Nothing from it is committed.

- **D-06: `71-HANDOFF.md`'s branch-update step is conditional, because `main` is `strict: true`.** If `origin/main` has moved past the merge-base when `/gsd-complete-milestone` runs, merge it into the canonical milestone branch with a merge commit (never a rebase), push, and re-check. Otherwise the step is a recorded no-op. Then:
  1. Open the PR from `gsd/v0.9.4-typing-modernization` to `main`.
  2. Wait for the six required checks, named literally as in the domain section, to be green on the head.
  3. Merge with a merge commit, the method #135, #136 and #143 used.

- **D-07: `71-HANDOFF.md` opens by stating the negative.** It publishes nothing: no tag, no PyPI upload, no GitHub Release, no version bump. The `update-pin.yml` dispatch and the Read the Docs `stable` check are not applicable. The handoff also records, as a fact and not a step, that the daily `update-pin.yml` schedule will move ja `latest` onto the merged `main` without any action. ja `stable` is unchanged, because it follows the translations repository's tags. It lists the observations REL-13 is checked on after the merge (SC#4): the merge commit on `origin/main`, `pyproject.toml` still `0.9.2`, no `v0.9.4` tag, PyPI 404 for `0.9.4`, and no `v0.9.4` Release.

- **D-08: The `0.9.3` and `0.9.4` version numbers are both recorded as unclaimed, not decided.** After this phase `## [Unreleased]` holds two unpublished milestones' bullets (three from v0.9.3 plus this one). The handoff states that the next release-prep phase promotes all four into its versioned section, the Phase 61 → 63 mechanism. Whether the next published release is `0.9.3`, `0.9.4` or something else belongs to that milestone's scoping.

- **D-09: The fence is `71-CLOSEOUT-GUARD.md`, reusing the `69-CLOSEOUT-GUARD.md` procedure.** At phase head it records `sha256sum`, `wc -l`, `git rev-parse HEAD` as this phase's own `PHASE_BASE_SHA`, and `grep -n 'REL-13' .planning/REQUIREMENTS.md`. The phase head is after D-02's AMENDED commit. The same commands re-run and MATCH at phase close, and once more after `phase.complete`-family tooling has run, including `/gsd-verify-work`'s inline transition. A flip is reverted with `git checkout -- .planning/REQUIREMENTS.md` and reported, never committed. Every plan's `SUMMARY.md` declares `requirements-completed: []`. SHA-256 is the primary probe, because a flip leaves `wc -l` unchanged.

- **D-10: One CI dispatch on the phase's final tip, after the branch is pushed.** First re-check for a decoy per constraint 9 (none exists today). If a decoy appears, advance the canonical pointer before deleting it. Push only the canonical branch. Then run `gh workflow run CI --ref gsd/v0.9.4-typing-modernization` and wait for it to finish. Transcribe every job conclusion literally, name both `windows-latest` and both `macos-latest` lanes, and read `ruff`'s verdict from `Lint and Format Check` (step `Run lint with tox`). No plan triggers `release.yml`. A second dispatch is justified only if a later plan lands a code-affecting change.

- **D-11: SC#1's "no code change slipped in" has two parts.**
  1. `git diff --stat <Phase 70's final code commit>..HEAD -- typsphinx/ tests/` is empty on the close tip.
  2. Phase 70's masked-AST harness re-runs on the close tip against Phase 70's `PHASE_BASE_SHA` (`697a1132…`) for the converted files, and the hashes equal.

  The remote probes (tags `v0.9.3` / `v0.9.4`, PyPI, GitHub Release) each carry a positive control against the existing `v0.9.2`.

- **D-12: Dependabot PRs.** None is open today. If one opens during the phase, it is named in `71-HANDOFF.md` and left untouched (Phase 69 D-10). A `ruff` bump merged to `main` meanwhile is caught by D-05's trial merge, and its count is authoritative (constraint 4).

### Claude's Discretion

- The exact prose of the bullet, within D-01..D-03.
- Plan decomposition, waves, and evidence-file naming, following the Phase 69 set: `71-CLOSEOUT-GUARD.md`, `71-CHANGELOG-EVIDENCE.md`, `71-PREFLIGHT-EVIDENCE.md`, `71-GREEN-TREE-EVIDENCE.md`, `71-CI-EVIDENCE.md`, `71-HANDOFF.md`, plus an SC#1 invariants file. `71-VERIFICATION.md` is reserved for the verifier and must not be plan-authored.
- How D-11's masked-AST re-run is invoked, as long as it is the Phase 70 mask (annotation subtrees plus `typing` / `collections.abc` `ImportFrom`) and non-vacuous.
- The docs warning baselines for SC#3, provided both come from a clean build (`rm -rf docs/_build` first).

### Deferred Ideas (OUT OF SCOPE)

- Choosing the next published version number (`0.9.3` / `0.9.4` / other) belongs to the next milestone's scoping (D-08).
- The REQUIREMENTS Out of Scope row "ja translation catalog resync — happens at the next published release" carries the same timing error D-02 measured. It is noted in REL-13's AMENDED block and left for the milestone-close archive, not edited separately.
- Todos reviewed and not folded into this phase: DOC-18 (docs structure), QUA-08 (linkcheck CI job — forbidden by constraint 12, no workflow edits), NUM-01, MSG-06, TRN-01 — all `typsphinx/` changes, forbidden by SC#1.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-13 | Close prep only, unpublished: one CHANGELOG bullet under `## [Unreleased]`, `pyproject.toml` stays `0.9.2`, no tag/PyPI/GitHub Release; milestone branch merged to `main` via PR at `/gsd-complete-milestone`, never by phase-completion tooling. AMENDED 2026-09-13: bullet drops the ja-catalog clause. | This document's "Architecture Patterns" (CHANGELOG bullet template, checksum-guard procedure, trial-merge pre-flight, CI dispatch, handoff structure) and "Code Examples" sections give the exact commands and file shapes; "Common Pitfalls" flags every verify-command trap this project has hit executing this exact shape twice before. REL-13's own checkbox is **not** closed by any plan — every plan declares `requirements-completed: []` (see `## Validation Architecture` and D-09). |

</phase_requirements>

## Architectural Responsibility Map

This phase has no application-tier architecture — it is entirely release/CI-process tooling. The
"tiers" below are process boundaries, not application layers.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| CHANGELOG bullet authoring | Product tree (`CHANGELOG.md`) | Docs build (renders via `docs/source/changelog.rst`) | `CHANGELOG.md` is the only product-tree file this phase writes; its content becomes published prose the moment REL-13 merges. |
| Requirement-checkbox fencing | `.planning/` (project-tracking tier) | — | `.planning/REQUIREMENTS.md` is process state, not product code; the fence is pure git/shell measurement. |
| Trial-merge / lock verification | Local git + `uv` (dependency tier) | GitHub (remote, read-only) | `git merge-tree` and `uv lock --check` run entirely locally against a fetched `origin/main`; nothing is pushed from this step. |
| CI dispatch and job census | GitHub Actions (CI tier) | — | `ci.yml`'s three-OS matrix is the only place Windows/macOS lanes and the authoritative `ruff` verdict exist; local runs are additive, never a substitute (ROADMAP constraint 8). |
| Unpublished-shape probes (tags, PyPI, GitHub Release) | External services (read-only) | — | GitHub API and PyPI are read-only trust boundaries this phase crosses with `git ls-remote`, `gh release/run/pr list`, and `curl` status probes — no write path exists in this phase (Phase 69's `COVERAGE.md` pattern). |
| Handoff authoring | `.planning/` (process tier) | — | `71-HANDOFF.md` is a standalone instruction set for a **later**, separate invocation (`/gsd-complete-milestone`); it performs no action itself. |

## Standard Stack

No new libraries or frameworks are introduced. This phase's entire toolchain is already pinned by
the repository and exercised at Phase 70's close.

### Core
| Tool | Version (pinned) | Purpose | Why Standard |
|---------|------|---------|--------------|
| `git` | host-provided | trial merge, diff/log measurements, push | Already the project's VCS; no alternative considered. |
| `gh` (GitHub CLI) | host-provided | PR/release/run listing, workflow dispatch (all read-only or the single canonical-branch push in this phase) | Used identically at every prior milestone close (Phases 41–69). [VERIFIED: live `gh pr list`/`gh api` runs in this session, 2026-09-13] |
| `uv` | 0.12.13 (per `.venv/pyvenv.cfg` in Phase 69/70 worktrees) | `uv sync`, `uv lock --check`, `uv run` | Project's package/venv manager (`CLAUDE.md`). |
| `pytest` | 9.1.1 (Phase 70 close, `uv.lock`) | full suite, version-sync tests, changelog page gate | Existing test runner; `pyproject.toml [tool.pytest.ini_options]`. |
| `ruff` | 0.16.6 (`uv.lock:1257-1258` per ROADMAP constraint 3; confirmed at Phase 70 close in `70-CI-EVIDENCE.md` `CI_RUFF_VERSION = 0.16.6`) [VERIFIED: 70-CI-EVIDENCE.md:249] | lint | CI's `Lint and Format Check` holds lint authority (ROADMAP constraint 8). |
| `black` | pinned via `uv.lock` | format check | `black --check .` |
| `mypy` | 2.3.1 (Phase 70 worktree; main checkout may show 2.1.0 drift, documented pre-existing and out of scope) | type check | `mypy typsphinx/` |
| `tox` (`tox-uv`) | per `uv.lock` | `docs-html` / `docs-pdf` environments | Existing docs build orchestration. |
| `curl` | host-provided | PyPI JSON-endpoint probes | Public, unauthenticated PyPI API. |

No package is installed or upgraded by this phase — the **Package Legitimacy Audit** section below
is therefore N/A per the protocol's own scope note ("whenever this phase installs external
packages").

### Supporting
None beyond the Core table — this is a zero-new-dependency phase (ROADMAP constraint 12).

### Alternatives Considered
Not applicable — every command and tool here is prescribed by locked decisions (D-01..D-12) and by
ROADMAP binding constraints, not chosen from alternatives.

**Installation:** none required — provision the worktree exactly as `CLAUDE.md` § "Worktree-isolated
execution" and § "Applicability" specify:
```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
```
The `--extra docs` is **mandatory**, not optional, for any plan that reads
`tests/test_changelog_page_gate.py`'s zero-skip count (ROADMAP constraint 11; see Pitfall 3 below).

## Package Legitimacy Audit

N/A — this phase installs no new external package. No `npm view` / `pip index versions` / `cargo
search` check applies. The **existing** `uv.lock` pins (`ruff`, `pytest`, `mypy`, `tox-uv`, etc.)
were already verified as legitimate, pinned dependencies at prior milestone closes (v0.9.1 through
v0.9.3); this phase reads their pinned versions but does not change them.

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│  Phase 71 execution (worktree, isolated per CLAUDE.md)               │
│                                                                       │
│  Wave 1                                                              │
│  ┌───────────────────────┐   ┌────────────────────────────────────┐ │
│  │ Plan A: CHANGELOG      │   │ Plan B: Closeout-guard baseline +   │ │
│  │  bullet + clean-docs   │   │  SC#1 observation 1 + D-11 code-    │ │
│  │  proof (D-01..D-04)    │   │  freeze checks + COVERAGE.md        │ │
│  └──────────┬────────────┘   └───────────────┬────────────────────┘ │
│             │  merged into canonical tip       │                     │
│             ▼                                  ▼                     │
│  Wave 2 (depends on Wave 1)                                          │
│  ┌───────────────┐  ┌────────────────┐  ┌──────────────────────────┐│
│  │ Plan C: Local  │  │ Plan D: push + │  │ Plan E: D-05/D-06 trial- ││
│  │  green-tree    │  │  CI dispatch + │  │  merge pre-flight        ││
│  │  proof (SC#3   │  │  job census    │  │  (git merge-tree, uv     ││
│  │  local half)   │  │  (SC#3 CI half)│  │  lock --check, protection││
│  │                │  │                │  │  + merge-method census)  ││
│  └───────┬────────┘  └────────┬───────┘  └────────────┬─────────────┘│
│          └────────────────────┴───────────────────────┘              │
│                              ▼                                       │
│  Wave 3 (depends on all of Wave 2)                                   │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Plan F: SC#1 observation 2 + closeout-guard re-verification +   │ │
│  │  standalone 71-HANDOFF.md (D-07/D-08, reproduces the fence      │ │
│  │  protocol inline)                                               │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼  (later, separate invocation — not this phase)
                    /gsd-complete-milestone
                    reads 71-HANDOFF.md, opens PR, merges, closes REL-13
```

### Recommended Project Structure
This phase writes exactly one product-tree file and a fixed set of `.planning/phases/71-*/`
evidence files. No `src/`-shaped layout applies.
```
CHANGELOG.md                                          # the only product-tree edit (D-01..D-04)
.planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/
├── 71-0N-PLAN.md / 71-0N-SUMMARY.md                  # per plan, per Phase 69's 6-plan/3-wave shape
├── 71-CLOSEOUT-GUARD.md                               # D-09, reuses 69-CLOSEOUT-GUARD.md procedure
├── 71-CHANGELOG-EVIDENCE.md                           # D-01..D-04 fence assertions + docs render
├── 71-SC1-INVARIANTS.md                               # unpublished-shape probes, 2 separated obs.
├── 71-GREEN-TREE-EVIDENCE.md                          # SC#3 local half
├── 71-CI-EVIDENCE.md                                  # SC#3 CI half (D-10)
├── 71-PREFLIGHT-EVIDENCE.md                            # D-05/D-06 non-committing trial merge
├── COVERAGE.md                                        # reasoned no-external-API declaration
└── 71-HANDOFF.md                                       # D-07/D-08, standalone for /gsd-complete-milestone
```
`71-VERIFICATION.md` is **reserved for the verifier** — no plan writes it (this project has clobbered
it before by planning an evidence file under that reserved name; see Common Pitfalls).

### Pattern 1: The CHANGELOG bullet — house register (D-01..D-04)
**What:** a bold-lead bullet under `### Changed`, requirement IDs inside the bold span, one
plain-English "no effect on installing or using typsphinx" sentence, and exactly one evidence
sentence.
**When to use:** any milestone that closes unpublished under `## [Unreleased]`.
**Example (Phase 69's tracer bullet, exact house shape; `CHANGELOG.md:12-16` today):**
```markdown
- **Contributor tooling returns to `tox-uv` from `tox-uv-bare` (TOX-01, TOX-02, TOX-03, TOX-04).**
  The `dev` extra and `tox.ini`'s `requires` line once again name `tox-uv`, with `uv.lock`
  regenerated in the same change. This has no effect on installing or using typsphinx. A CI run
  dispatched against the branch carrying this change was green across the Linux, Windows and
  macOS test lanes.
```
[VERIFIED: CHANGELOG.md:12-16, read live this session, 2026-09-13]

Phase 71's bullet must open with a verb-bearing bold lead (Phase 69's own code review, `69-REVIEW.md`
WR-01, flagged a bare-noun-phrase bold lead — "**A NixOS development shell (…).**" — as a
non-blocking but real defect; do not repeat that shape). A safe pattern:
```markdown
- **The API reference now shows builtin generics instead of `typing` aliases
  (QUA-09, QUA-11, QUA-12, DOC-22, DOC-23).** `typsphinx/`'s and `tests/`'s type annotations moved
  from `typing.Dict`/`List`/`Set`/`Tuple` to builtin `dict`/`list`/`set`/`tuple`, and `Iterator`
  moved from `typing` to `collections.abc`; the API reference now shows, for example,
  `dict[str, Any]` where it showed `Dict[str, Any]`. This has no effect on installing or using
  typsphinx: emitted Typst output is unchanged, byte-identical over the <N>-project test-fixture
  corpus.
```
`<N>` must be transcribed fresh from `70-CORPUS-DOCS-BASE-EVIDENCE.md` / `70-AFTER-RUNTIME-EVIDENCE.md`
at execution time (D-03) — Phase 70's own run recorded `CORPUS_PROJECT_COUNT = 167` with
`CORPUS_MANIFEST_SHA256 = 4c87a31da016b85f260915f6a0690c3fcf1602f17a0e2aa6a21725846d07464d`
[VERIFIED: 70-AFTER-RUNTIME-EVIDENCE.md:122,167,174,354-357], but that value is not to be copied
into the bullet from this RESEARCH.md — the plan re-reads it live. `Dict[str, Any]` →
`dict[str, Any]` is a real, traced example: `typsphinx/template_engine.py`'s `map_parameters`
function [VERIFIED: 70-DOCS-DIFF-EVIDENCE.md:515-518, quoting `sphinx_metadata: Dict[str, Any]` →
`sphinx_metadata: dict[str, Any]` at `typsphinx/template_engine.py:468-470`].

### Pattern 2: The checksum-fenced requirement guard (D-09, reused verbatim from `69-CLOSEOUT-GUARD.md`)
**What:** a `.planning/phases/71-*/71-CLOSEOUT-GUARD.md` that records, at phase head, the whole-file
SHA-256 of `.planning/REQUIREMENTS.md`, its line count, `PHASE_BASE_SHA`, and the verbatim
`grep -n 'REL-13' .planning/REQUIREMENTS.md` output — then re-runs the identical four probes at
phase close and once more after `phase.complete`-family tooling has run.
**When to use:** any phase where a requirement checkbox must NOT flip during the phase (release-prep
phases, per ROADMAP constraint 10).
**Why whole-file SHA-256, not a scoped grep:** a flip is line-count-neutral (`- [ ]` → `- [x]` is the
same length) and has moved **three** requirements at once in one prior incident (Phase 63,
`63-CLOSEOUT-GUARD.md` "Fourth observation") — a grep scoped to one requirement ID would have missed
the others [CITED: 69-CLOSEOUT-GUARD.md:93-102].
**Example (baseline block shape, reproduce this exactly):**
```
PHASE_BASE_SHA = <git rev-parse HEAD at phase head, after any CONTEXT-amendment commit>
REQ_SHA256_BASE = <sha256sum .planning/REQUIREMENTS.md, first field>
REQ_LINES_BASE = <wc -l .planning/REQUIREMENTS.md>
REL13_HITS_BASE = <grep -c 'REL-13' .planning/REQUIREMENTS.md>
GUARD_AT = <date -u +"%Y-%m-%dT%H:%M:%SZ">
```
Today's live values (2026-09-13, before any Phase 71 commit) [VERIFIED: live `sha256sum`/`wc -l`/
`grep -n` run this session against `.planning/REQUIREMENTS.md`]:
```
REQ_SHA256_BASE (current) = 4d98e0287552d2dce8f45b7939dfcb0e729523c6869bfa1cd2d1d041119c5636
REQ_LINES_BASE (current) = 80
REL13_HITS_BASE (current) = 4
```
`grep -n 'REL-13' .planning/REQUIREMENTS.md` live output (lines 24, 33, 71, 75) — **state-bearing**:
line 24 (the checkbox, `- [ ] **REL-13**:` — only the leading token is state-bearing) and line 71
(the Traceability row `| REL-13 | Phase 71 | Pending — coverage only; … |`); **informational-only**:
line 33 (AMENDED-block continuation prose) and line 75 (the "Mapped to phases" coverage-count line,
which contains the literal substring `REL-13` inside its parenthetical). These four values will
shift the instant any earlier Phase-71 plan (e.g. a bullet-authoring commit) lands, so the plan that
actually authors `71-CLOSEOUT-GUARD.md` must re-run all four commands fresh at its own execution
time, not copy the numbers above — this table exists only to show the expected shape and hit count
before this session's edits.

**The "third observation" is the one that actually catches the flip.** Reproduced from precedent:
`phase.complete`-family tooling has auto-flipped the release requirement's checkbox at **eight**
consecutive prior release-prep closes; Phase 61 and Phase 69 are the only two that held, and both
held only because the guard was re-checked **a third time**, after `phase.complete` ran, not merely
at phase close [VERIFIED: 69-CLOSEOUT-GUARD.md § "Third observation", reproducing the live
`phase.complete 69` diff that flipped REL-12 and the `git checkout --` revert that undid it before
any commit]. Plan the "operator" section of `71-CLOSEOUT-GUARD.md` (and its verbatim reproduction
inside `71-HANDOFF.md`) to instruct: back up `REQUIREMENTS.md`/`ROADMAP.md`/`STATE.md` to a scratch
directory **outside the repo** before either `/gsd-execute-phase`'s `phase.complete` step or
`/gsd-verify-work`'s inline transition runs (both are equally likely to trigger the flip — it has
landed through both entry points before, including **twice** at one single close), then re-run the
four probes and `git checkout -- .planning/REQUIREMENTS.md` on any divergence, reporting but never
committing the flipped state [CITED: 69-CLOSEOUT-GUARD.md § "For the operator running phase.complete"].

### Pattern 3: Non-committing trial merge (D-05/D-06, reused from `69-PREFLIGHT-EVIDENCE.md`)
**What:** measure whether `origin/main` merges cleanly into the milestone branch, and whether the
merged lock/lint are valid, without ever touching the branch.
**Commands (exact sequence, transcribe every line verbatim):**
```bash
git fetch origin
git rev-parse origin/main                       # ORIGIN_MAIN_SHA
git merge-tree --write-tree HEAD "$ORIGIN_MAIN_SHA"; echo "exit:$?"   # MERGE_RC, MERGE_TREE
S="$(mktemp -d)"
git archive "$MERGE_TREE" pyproject.toml uv.lock | tar -x -C "$S"
uv --directory "$S" lock --check; echo "exit:$?"                       # LOCK_CHECK_EXIT
git merge-base --is-ancestor "$ORIGIN_MAIN_SHA" HEAD; echo "exit:$?"   # must be 1 (D-05 non-absorption)
gh api repos/YuSabo90002/typsphinx/branches/main/protection --jq '.required_status_checks'
```
[CITED: 69-PREFLIGHT-EVIDENCE.md, full transcript]. Optional lint half (run when the milestone
touched test/lint-relevant files, which Phase 70 did):
```bash
S2="$(mktemp -d)"
git archive "$MERGE_TREE" | tar -x -C "$S2"
uv --directory "$S2" sync --locked --extra dev --no-install-project
uv --directory "$S2" run --no-sync ruff check .; echo "exit:$?"
uv --directory "$S2" run --no-sync black --check .; echo "exit:$?"
```
Today's live measurement (2026-09-13, before this phase's own edits): `origin/main` **is** an
ancestor of the current worktree's `HEAD` (`git merge-base --is-ancestor origin/main HEAD` → exit
`0`) because `origin/main`'s tip `d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d` **equals** the
merge-base with `HEAD` [VERIFIED: live `git merge-base HEAD origin/main` this session, 2026-09-13] —
i.e. there is currently nothing on `main` this branch lacks, matching D-05's "today there is nothing
to absorb." Re-measure fresh at plan-execution time; this can change if `main` moves.
**main protection, read live (2026-09-13)** [VERIFIED: live `gh api …/branches/main/protection`
this session]:
```
PROTECTION_STRICT = true
PROTECTION_CONTEXTS_COUNT = 6
```
The six contexts, verbatim: `Test Python 3.12 on ubuntu-latest`, `Lint and Format Check`,
`Type Check`, `Code Coverage`, `Build Package`, `Test Python 3.13 on ubuntu-latest` — unchanged from
Phase 69's own census.
**Merge-method precedent:** every prior milestone PR merged with a merge commit, never squash/rebase
(`#135`, `#136`, `#143` — `#143` per `71-CONTEXT.md`'s domain section, the v0.9.3 close). Plan the PR
merge step (inside `71-HANDOFF.md`, not this phase) as `gh pr merge <number> --merge`.

### Pattern 4: CI dispatch and job census (D-10, reused from `69-CI-EVIDENCE.md` / `70-CI-EVIDENCE.md`)
**What:** exactly one `workflow_dispatch` run of `ci.yml` on the phase's final pushed tip, with every
job's conclusion transcribed by name.
**Commands:**
```bash
gh workflow run CI --ref gsd/v0.9.4-typing-modernization
gh run list --workflow=ci.yml --branch gsd/v0.9.4-typing-modernization --event workflow_dispatch --limit 5 --json databaseId,headSha,status,createdAt,url
gh run view <RUN_ID> --json status,conclusion,workflowName,headSha,url,createdAt,updatedAt
gh run view <RUN_ID> --json jobs --jq '.jobs[] | [.name, .conclusion] | @tsv'
```
`ci.yml` currently defines **12 jobs** — confirmed twice, at both Phase 69's and Phase 70's own
dispatches, with identical job names both times: `Code Coverage`, `Integration Test - basic`,
`Integration Test - advanced`, `Lint and Format Check`, `Test Python {3.12,3.13} on {ubuntu,windows,
macos}-latest`, `Build Package`, `Type Check` [VERIFIED: 69-CI-EVIDENCE.md § "Job census";
70-CI-EVIDENCE.md § "Job census" — same 12 names both runs]. Expect the same 12 for Phase 71's
dispatch; if the count differs, `ci.yml` changed since Phase 70 and that is itself worth flagging
(ROADMAP constraint 12 forbids workflow edits in this milestone).
**Wait pattern (avoids the 600000ms Bash-tool timeout without polling loops):**
```bash
timeout 590 gh run watch <RUN_ID> --interval 30
gh run view <RUN_ID> --json status,conclusion   # confirms completion if the watch window elapsed first
```
[CITED: 69-CI-EVIDENCE.md § "Run"; 70-CI-EVIDENCE.md § "Run" — both runs finished inside the first
590s watch window, no second call needed].
**Read `ruff`'s verdict from the correct step**, quoting the job log directly:
```bash
gh run view --job <job_id> --log
```
looking for the `Lint and Format Check` job's `Install dependencies` step's `+ ruff==` line and the
`Run lint with tox` step's `lint: OK` line — never `release.yml`'s differently-named lint step
(never searched, never triggered by this phase; D-10, ROADMAP constraint 8).

### Pattern 5: Standalone handoff (D-07/D-08, reused from `69-HANDOFF.md`)
**What:** a self-contained instruction document for `/gsd-complete-milestone` that opens with the
negative ("this milestone publishes nothing"), states the one PR step as the sole irreversible
action, reproduces the closeout-guard's post-`phase.complete` re-verification protocol **inline**
(so an operator reaches it without opening a second file), and lists the five/four post-merge
observations REL-13 is checked on.
**Structural checklist** (from Phase 69's file, adapt names/SHAs for v0.9.4):
1. Opening negative-first paragraph (no tag/PyPI/Release/bump; `update-pin.yml`/RTD `stable` N/A).
2. "What `/gsd-complete-milestone` does, in order" — numbered steps: fence-first backup → re-run
   trial merge → merge `origin/main` if needed (never rebase) → `uv lock --check` + re-sync → push →
   open PR → wait on 6 named checks → merge (`--merge`, never squash/rebase) → observe the five
   post-merge facts, only then flip REL-13.
3. "What this phase satisfied" — quote REL-13 verbatim from `.planning/REQUIREMENTS.md`, state it
   stays open until step above runs, cite every SC verdict with its evidence-file section.
4. "Recorded without acting" — the dependabot census (D-12), the unclaimed-version-number statement
   (D-08).
5. "Before and after phase.complete-family tooling" — reproduce Pattern 2's third-observation
   protocol inline, verbatim.
6. "Fence observation" — a final live re-check inside this plan's own worktree.
7. "What this phase deliberately did not do" — an explicit negative checklist (no tag, no
   `release.yml` run, no PyPI upload, no GitHub Release, no PR opened/merged, no `origin/main` merged
   into the branch, no `update-pin.yml` dispatch, no dependabot-PR action, no requirements-checkbox
   change).

### Anti-Patterns to Avoid
- **A bare-noun-phrase bold lead** ("**A NixOS development shell (…).**") — Phase 69's own code
  review flagged this as a non-blocking-but-real prose defect (`69-REVIEW.md` WR-01). Give the bold
  lead a verb.
- **Authoring `71-VERIFICATION.md` from a plan.** That filename is reserved for `gsd-verifier` and
  gets fully overwritten/clobbered if a plan pre-creates evidence under it — a documented hazard in
  this project's own memory (`gsd-verifier-clobbers-verification-md`). Use `71-SC1-INVARIANTS.md`
  or another discretionary name for any SC#1-adjacent evidence.
- **Running `scripts/extract_changelog_section.py`.** There is no versioned section to extract this
  phase (D-04); running it anyway would be a wasted step signaling confusion about milestone status.
- **Treating the `.venv/pyvenv.cfg` interpreter as portable across environments.** A fresh worktree's
  `uv sync` may build on uv-managed CPython (e.g. 3.14.x), while a Phase-70-provisioned worktree used
  `--python 3.13.13` explicitly. Compare counts only within the same interpreter, and record
  `pyvenv.cfg`'s `version_info` at every measurement (this project's own documented hazard, restated
  in `CLAUDE.md` § "Interpreters may differ").

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Detecting the requirement-checkbox flip | A custom diff-parser or line-scoped grep | Whole-file SHA-256 + `wc -l` + verbatim `grep -n` (Pattern 2) | A scoped grep has already missed a multi-requirement flip once (Phase 63); SHA-256 is the only probe proven to catch every shape the flip has taken. |
| Proving a merge is conflict-free without committing | A throwaway branch + real merge + `git reset --hard` | `git merge-tree --write-tree` (Pattern 3) | Genuinely non-committing — adds only unreferenced objects to the object store, verified by `git rev-parse HEAD` before/after and `git rev-list --merges` staying empty. |
| Extracting a CI job's log line | Downloading and grepping the full log archive | `gh run view --job <id> --log` with a `grep`/quote on the specific step | Exact precedent (Pattern 4) already isolates the two relevant lines without downloading anything extra. |
| Waiting for a long-running CI run inside a 10-minute tool budget | A background polling loop with `sleep` | `timeout 590 gh run watch <id> --interval 30` followed by one `gh run view` | Precedent shows the run typically finishes inside the first watch window; the tool documentation explicitly discourages sleep-loop polling. |

**Key insight:** every mechanism this phase needs has already been built, run, and independently
re-verified by a `gsd-verifier` pass at Phase 69's close (8/8 truths verified, live-remeasured, not
copied from evidence files). There is no novel engineering here — the risk is entirely in
transcription discipline (exact `KEY = value` formatting, fresh re-measurement instead of copying
stale numbers) and in the two genuinely-new D-11 checks that have no Phase-69 precedent.

## Common Pitfalls

### Pitfall 1: Anchored sed/grep extraction on `pytest --collect-only`'s wrapped summary line
**What goes wrong:** `pytest --collect-only -q`'s final summary line is wrapped in `=` decoration
(e.g. `======================== 1548 tests collected in 1.22s =========================`), so a
`^`-anchored `sed` extraction always returns empty.
**Why it happens:** the wrapping is pytest's own terminal-width decoration, added regardless of
`-q`.
**How to avoid:** use `grep -oE '[0-9]+ tests? collected'` (unanchored) as Phase 70's own baseline
evidence does [CITED: 70-BASELINE-EVIDENCE.md:169-172].
**Warning signs:** a `sed -n '/^[0-9]/p'`-shaped extraction silently returning nothing where a count
is expected.

### Pitfall 2: Trailing prose on a `KEY = value` evidence line breaks exact comparison
**What goes wrong:** `sed -n "s/^KEY = //p"`-style extraction (used by later plans to cross-check
values) fails if the key line carries trailing prose, e.g. `DOCS_HTML_WARN_POST = 3 (equal to
DOCS_HTML_WARN_BASE)`.
**Why it happens:** the extraction regex captures everything after `= `, including the parenthetical.
**How to avoid:** keep the value bare on the key line; put any explanatory prose on the line(s)
**before or after** the key line, never on it. Phase 69 hit this exact defect and had to correct it
mid-phase: `69-CHANGELOG-EVIDENCE.md`'s own final section documents the fix (moving five key-line
parentheticals onto separate lines, commit `56880eca`) [VERIFIED: 69-CHANGELOG-EVIDENCE.md § "Orchestrator
note: key-line format correction", quoting the exact failure mode and fix].
**Warning signs:** an exact-string verify step failing even though the printed value "looks right"
to a human reader.

### Pitfall 3: `LC_ALL=C` and command-substitution-inside-`&&`-chain interactions
**What goes wrong:** `R="$(diff -rq …)"` or `VAR="$(grep …)"` inside an `&&` chain aborts the chain
on `diff`'s exit 1 (files differ) or `grep`'s no-match exit. The host runs `LANG=ja_JP.UTF-8`, so
matching English diff/sort/grep messages needs `LC_ALL=C` explicitly.
**Why it happens:** command substitution inherits the exit code of the substituted command; `&&`
short-circuits on any non-zero exit, including the "expected" non-zero exits of `diff`/`grep` when
used as boolean probes.
**How to avoid:** run probe-shaped commands (expected non-zero on "not found") outside an `&&` chain,
or capture with `; echo "exit:$?"` immediately after, as every precedent evidence file in this phase
family does.
**Warning signs:** a script that "just stops" partway through with no error message.

### Pitfall 4: `grep` on this host is `ugrep`; bounded-repeat patterns may misbehave
**What goes wrong:** patterns like `.\{0,60\}` may be rejected or hang under the NixOS host's `ugrep`.
**How to avoid:** prefer `node -e` or a short Python one-liner for complex matching; keep `grep`
patterns to simple literal/anchor/class forms, exactly as every precedent evidence file in this
project does (`grep -c`, `grep -n`, `grep -oE` with simple character classes only).

### Pitfall 5: Docs warning baseline from an incremental rebuild under-reports
**What goes wrong:** an incremental `tox -e docs-html`/`docs-pdf` rebuild reports fewer warnings than
a clean build, manufacturing a false "matches baseline" result.
**Why it happens:** Sphinx caches; a warning tied to a file that did not change in this incremental
build is not re-emitted.
**How to avoid:** `rm -rf docs/_build` immediately before **every** counted build, both baseline and
post-edit, on both sides of any comparison. Every precedent evidence file in this phase family
follows this discipline without exception.
**Warning signs:** a warning count that looks suspiciously identical across a build where content
visibly changed, when the count should plausibly have shifted line numbers even if not warning
counts.

### Pitfall 6: `--extra dev` alone drops the `docs` extra, causing a false "0 skipped" or false skip
**What goes wrong:** a fresh worktree provisioned with `uv sync --extra dev` (no `--extra docs`)
lacks `myst-parser`, so `tests/test_changelog_page_gate.py`'s build classes **skip** rather than
fail — a false-negative "the gate ran clean" reading when it did not run at all. In the **main
checkout**, running a bare `uv sync --extra dev` is an *exact* sync that **removes** the docs extra
if it was previously installed, actively regressing an already-correct environment.
**How to avoid:** always `uv sync --extra dev --extra docs` for any plan that must read the
changelog-gate's zero-skip count (ROADMAP constraint 11). Confirm via `uv run python -c "import
myst_parser; print(myst_parser.__version__)"` before trusting a "0 skipped" reading, exactly as
`69-GREEN-TREE-EVIDENCE.md` does.
**Warning signs:** `tests/test_changelog_page_gate.py -rs` reporting any `SKIPPED` line at all.

### Pitfall 7: `phase.complete`-family tooling flips the release requirement — twice through two entry points
**What goes wrong:** `/gsd-execute-phase`'s `phase.complete` step and `/gsd-verify-work`'s inline
transition both call the same underlying verb; either can (and, historically, sometimes both do at
one single close) flip the release requirement's checkbox and Traceability row against an explicit
CONTEXT decision — eight of eight prior closes it was tested at, before Phase 61 first held it and
Phase 69 held it a second time.
**Why it happens:** phase-completion tooling has a general "close every requirement mapped to this
phase" behavior that does not special-case a requirement deliberately held open for a **later**,
separate command.
**How to avoid:** the third-observation protocol in Pattern 2 — back up the three `.planning/` files
outside the repo before either entry point runs, re-check all four probes after, revert on
divergence with `git checkout --`, never commit the flipped state.
**Warning signs:** `.planning/REQUIREMENTS.md`'s SHA-256 not matching the phase-head baseline
immediately after a `phase.complete`-family step, even though `wc -l` still matches (line-count
neutral flip).

### Pitfall 8: The api-coverage seal-time gate false-positives on this phase's own read-only network language
**What goes wrong:** the detector that flags "external API integration" pattern-matches on verbs
like "integration" and nouns like "api" appearing anywhere in plan prose — including in a phase's
own `<threat_model>` "Trust Boundaries" table row that documents a **read-only** boundary, and in a
`COVERAGE.md`'s own required opening sentence that must literally contain the phrase "No external
API integration:".
**How to avoid:** write `COVERAGE.md` following Phase 69's exact reasoned-declaration shape — open
with "No external API integration: …", then walk through each detector signal explaining why it is
the detector matching its own required vocabulary rather than a real integration, exactly as
`.planning/milestones/v0.9.3-phases/69-.../COVERAGE.md` does. This is advisory/informational in this
project's own memory, not a hard blocker, but skipping the reasoned declaration invites a
false `issues_found` at seal time.
**Warning signs:** `api-coverage.verify-pre` reporting `detected: true` with signals whose
`snippet`s are visibly quoting the phase's own required-phrase prose or its own security-review
table, not a genuine outbound API call.

## Code Examples

### The mask harness (D-11's masked-AST re-run mechanism, exact reused code)
```python
# Source: 70-MASK-PILOT-EVIDENCE.md, "Mask harness" section — the harness this
# plan's re-run must reproduce byte-for-byte (MASK_HARNESS_SHA256 =
# 11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65)
import ast
import hashlib
import sys


class Mask(ast.NodeTransformer):
    def visit_ImportFrom(self, node):
        if node.module in ("typing", "collections.abc"):
            return None
        return node

    def visit_FunctionDef(self, node):
        return self._mask_func(node)

    def visit_AsyncFunctionDef(self, node):
        return self._mask_func(node)

    def _mask_func(self, node):
        self.generic_visit(node)
        node.returns = None
        a = node.args
        for arg in a.posonlyargs + a.args + a.kwonlyargs:
            arg.annotation = None
        if a.vararg:
            a.vararg.annotation = None
        if a.kwarg:
            a.kwarg.annotation = None
        return node

    def visit_AnnAssign(self, node):
        self.generic_visit(node)
        node.annotation = ast.Constant(value=None)
        return node


t = ast.parse(sys.stdin.read())
t = Mask().visit(t)
ast.fix_missing_locations(t)
print(
    hashlib.sha256(
        ast.dump(t, annotate_fields=True, include_attributes=False).encode()
    ).hexdigest()
)
```
[VERIFIED: 70-MASK-PILOT-EVIDENCE.md:206-250, quoted verbatim — the exact code block, byte-checked
via `sha256sum` against `MASK_HARNESS_SHA256 = 11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65`]

**How to invoke it (extraction pattern used by every later verify in Phase 70):**
```bash
H="$(sed -n '/^~~~python mask-harness$/,/^~~~$/p' 70-MASK-PILOT-EVIDENCE.md | sed '1d;$d')"
printf '%s\n' "$H" | sha256sum   # must equal 11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65
sk() { uv run python -c "$H"; }
sk < <(git show 697a113221a8a267d7e8c6dd1f2b95672f9454d2:typsphinx/translator.py)
sk < typsphinx/translator.py
```
[CITED: 70-AFTER-STATIC-EVIDENCE.md § "Leg (a)", exact extraction and invocation pattern]. The ten
converted files to re-check (identical set both times Phase 70 measured it) [VERIFIED:
70-AFTER-STATIC-EVIDENCE.md:61-75, quoting the `git diff --name-only` output]:
```
tests/conftest.py
tests/test_bundle_layout_sweep_gate.py
tests/test_include_edge_derivation_unit.py
tests/test_include_ledger_removal_gate.py
typsphinx/__init__.py
typsphinx/builder.py
typsphinx/template_engine.py
typsphinx/template_registry.py
typsphinx/translator.py
typsphinx/writer.py
```
Phase 70's own recorded per-file hashes (both base and post-flip HEAD; these were equal there — D-11
re-checks that they are **still** equal on Phase 71's close tip against the same `PHASE_BASE_SHA`,
`697a113221a8a267d7e8c6dd1f2b95672f9454d2`) are tabulated in `70-AFTER-STATIC-EVIDENCE.md` § "Leg (a)
— every converted file" [VERIFIED: 70-AFTER-STATIC-EVIDENCE.md:232-243, all 10 rows "EQUAL"]. Do not
copy those hash values into a Phase 71 evidence file as if pre-computed — re-run `sk()` fresh against
both sides on the close tip; the point of the re-check is that it is a **live** measurement, not a
transcription.

### D-11 part 1 — the code-freeze diff since Phase 70's final code commit
```bash
# Phase 70's final code commit (last commit touching typsphinx/ or tests/ on this branch),
# identified by measurement, not by reading a plan number:
git log --format='%H %s' -1 -- typsphinx/ tests/
# => e721ff899a981eafdad696ef1a9c93aaab41ece5 chore: merge executor worktree (worktree-agent-a9a3a29e4a793db3b)

git diff --stat e721ff899a981eafdad696ef1a9c93aaab41ece5..HEAD -- typsphinx/ tests/
# expected: empty
```
[VERIFIED: live `git log --format='%H %s' -1 -- typsphinx/ tests/` and `git diff --stat`, this
session, 2026-09-13, repo HEAD `5292a85b`]. Re-run this at the plan's own execution time — HEAD will
have advanced past `5292a85b` by then (this phase's own commits), but the anchor
`e721ff899a981eafdad696ef1a9c93aaab41ece5` does not change, since it is fixed history from Phase 70.

### The four SC#1 remote probes, each with a positive control (reused exactly from `69-SC1-INVARIANTS.md`)
```bash
sed -n 7p pyproject.toml                                  # must read: version = "0.9.2"

git tag -l 'v0.9*'                                         # positive control: v0.9.0, v0.9.2 present
git tag -l 'v0.9.3'; git tag -l 'v0.9.4'                    # both must be empty

git ls-remote --tags origin                                 # unfiltered fetch, not a bare grep for
                                                              # v0.9.3/v0.9.4 (silence would be
                                                              # indistinguishable from a network failure)
git ls-remote --tags origin | grep -c 'refs/tags/v0\.9\.2$'  # positive control: 1
git ls-remote --tags origin | grep -cE 'refs/tags/v0\.9\.[34]'  # must be 0

curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.2/json  # positive control: 200
curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.3/json  # 404
curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.4/json  # 404

gh release list --limit 20 --json tagName,isLatest,publishedAt  # positive control: v0.9.2 isLatest:true
gh pr list --head gsd/v0.9.4-typing-modernization --state all --json number,state  # must be []
```
Live confirmation this session (2026-09-13) [VERIFIED: live runs this session]: `sed -n 7p
pyproject.toml` → `version = "0.9.2"`; `git tag -l 'v0.9.3'` and `git tag -l 'v0.9.4'` both empty;
`git ls-remote --tags origin` shows `refs/tags/v0.9.2` and no `v0.9.3`/`v0.9.4` line; PyPI returns
`200`/`404`/`404` for `0.9.2`/`0.9.3`/`0.9.4` respectively; `gh release list` shows `v0.9.2` as
`isLatest: true` with no `v0.9.3`/`v0.9.4` entry; `gh pr list --state open` → `[]`.

## State of the Art

Not applicable in the usual sense — this is process/release tooling internal to the project, not a
public library ecosystem with an evolving "current best practice." The one relevant "old → new"
shift is internal to this project's own history:

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Flip the release requirement's checkbox inside the release-prep phase, catch and revert the auto-flip after the fact | Hold the checkbox at `[ ]` behind a SHA-256 fence for the entire phase, checked three times (head, close, post-`phase.complete`) | Phase 61 (v0.9.1), reused at Phase 69 (v0.9.3) | Two consecutive holds with zero unwanted commits, vs. eight consecutive prior flips that each needed manual revert. |
| Merge `origin/main` into the milestone branch inside the phase | Defer the `origin/main` merge to `/gsd-complete-milestone`, proven safe in advance by a non-committing `git merge-tree` trial | Phase 61 D-06/D-07-shaped decisions, reused at Phase 69 | `main`'s `strict: true` protection means the PR cannot merge until the head branch is current with `main` anyway, so nothing is lost by deferring, and the milestone branch's own tip stays exactly what the phase's CI dispatch tested. |

**Deprecated/outdated:** nothing platform-level is deprecated by this phase.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The `ci.yml` job count/names for Phase 71's dispatch will again be exactly the 12 seen at both Phase 69's and Phase 70's dispatches | Pattern 4 | Low — if `ci.yml` changed, that is itself a violation of ROADMAP constraint 12 (no workflow edits this milestone) and would surface immediately as a job-count mismatch, not a silent failure. |
| A2 | `main`'s branch protection (strict, 6 named contexts) and merge-method precedent (merge commit only) will still hold at `/gsd-complete-milestone` time | Pattern 3 | Low — this is read live by `71-PREFLIGHT-EVIDENCE.md` and again inside the handoff's own step; a change would only affect a **later**, separate invocation, not this phase's own success criteria. |
| A3 | Phase 70's `PHASE_BASE_SHA` (`697a113221a8a267d7e8c6dd1f2b95672f9454d2`) and its 10-file converted-file list remain the correct anchor for D-11's masked-AST re-run | Code Examples § "The mask harness" | Low — both values were read directly from `70-BASELINE-EVIDENCE.md` and `70-AFTER-STATIC-EVIDENCE.md` this session and cross-checked against a live `git log`/`git diff` in this session; they are fixed history and cannot drift. |

**If this table is empty:** not applicable — three low-risk assumptions are logged above, none of
which threatens a locked decision; all load-bearing facts in this document were independently
re-verified live in this session (git, `gh`, `curl`) rather than taken solely from the archived
Phase 69/70 evidence files.

## Open Questions

1. **Exact wording of the code-freeze sentence tying D-11's two checks into the CHANGELOG evidence
   trail.**
   - What we know: D-11 requires both an empty diff-stat since Phase 70's final code commit and a
     masked-AST re-equality check; both mechanisms and their exact commands are fully specified
     above.
   - What's unclear: whether the planner places both checks inside the same plan as the CHANGELOG
     bullet (which already needs the converted-file list and Phase 70 evidence citations) or as a
     dedicated task inside the closeout-guard/SC#1-observation plan (which already owns the
     `typsphinx/`-fence pattern from the milestone-base anchor).
   - Recommendation: co-locate with whichever plan already loads Phase 70's evidence files into
     context — this research recommends the closeout-guard/SC#1-observation-1 plan (Wave 1), since
     it already needs to read `70-BASELINE-EVIDENCE.md` for `PHASE_BASE_SHA` and is the plan that
     also owns the `typsphinx/`-empty-diff pattern from the milestone base.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `git` | every plan | ✓ [VERIFIED: live this session] | host-provided | — |
| `gh` (authenticated) | remote probes, push, CI dispatch | ✓ [VERIFIED: live `gh pr list`/`gh api`/`gh release list` succeeded this session] | — | — |
| `uv` (via NixOS FHS shim, per `CLAUDE.md`) | provisioning, `uv lock --check`, `uv run` | ✓ [VERIFIED: `CLAUDE.md`'s documented shim mechanism; confirmed working at Phase 69/70 closes] | 0.12.13 (worktree venvs) | — |
| Network access to `pypi.org`, `api.github.com` | unpublished-shape probes | ✓ [VERIFIED: live `curl`/`gh` calls succeeded this session] | — | — |
| `myst-parser` (the `docs` extra) | zero-skip changelog page gate | Conditional — present only when `uv sync --extra dev --extra docs` is run | 5.1.0 (Phase 69/70 worktrees) | Without it, `tests/test_changelog_page_gate.py` skips — not a hard blocker, but the SC#2 "zero skipped" reading requires the extra (ROADMAP constraint 11) |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** the `docs` extra is the only conditional dependency, and its
fallback (accepting skips) is explicitly disallowed by SC#2's "zero skipped" requirement — so in
practice every plan reading the changelog gate must provision with `--extra docs`, not treat its
absence as acceptable.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (`pyproject.toml [tool.pytest.ini_options]`, `testpaths = ["tests"]`), orchestrated by tox (`env_list = py312, py313, lint, type, cov, docs`) |
| Config file | `pyproject.toml`; `tox.ini` |
| Quick run command | `uv run pytest -m "not slow"` |
| Full suite command | `LC_ALL=C uv run pytest -q -rs -p no:cacheprovider` (run under `LC_ALL=C` at least once, per ROADMAP SC#3, since CI runs in English) |

Baseline carried in from Phase 70's close: `PYTEST_RESULT_AFTER = 1547 passed 1 skipped` (the one
skip is `tests/test_corpus_gate.py`'s env-gated before/after measurement, unrelated to this phase)
[VERIFIED: STATE.md "Phase 70's base and numbers"; 70-AFTER-RUNTIME-EVIDENCE.md]. Re-measure fresh —
never inherit — exactly as Phase 69's own `69-VALIDATION.md` instructs.

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REL-13 (coverage only; not closed by any test) | CHANGELOG bullet lands under `## [Unreleased]`, house register, no version literal moves | audit (grep/awk region checks) | `grep -c '0\.9\.[34]' CHANGELOG.md` → 0; `awk` region bold-bullet count → 4; `tail -n 1 CHANGELOG.md` unchanged | ✅ (pattern established in `69-CHANGELOG-EVIDENCE.md`) |
| REL-13 (coverage only) | Unpublished-shape probes hold with positive controls | audit (remote probes) | see Code Examples § "The four SC#1 remote probes" | ✅ |
| REL-13 (coverage only) | Tree green locally and on CI, including a trial merge of `origin/main` | full suite + lint + type + CI dispatch | `LC_ALL=C uv run pytest`, `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/`, `gh run view <id> --json jobs` | ✅ |
| REL-13 (coverage only) | Requirement checkbox held at `[ ]` behind a SHA-256 fence, three separated observations | audit (checksum) | `sha256sum .planning/REQUIREMENTS.md` equal at head/close/post-`phase.complete` | ✅ |
| REL-13 (coverage only) | D-11: no code change since Phase 70's final commit | audit (diff + masked-AST) | `git diff --stat e721ff89..HEAD -- typsphinx/ tests/` empty; `sk()` masked hashes equal per converted file | New this phase — no direct precedent, but both mechanisms are proven (git diff pattern from Phase 69's `typsphinx/`-fence; masked-AST harness from Phase 70) |

### Sampling Rate
- **Per task commit:** the task's own evidence read-back (e.g. `grep -c '^## \[0\.9\.[34]\]' CHANGELOG.md` = 0)
- **Per wave merge:** `LC_ALL=C uv run pytest` + `uv run black --check .` + `uv run mypy typsphinx/` + `uv run ruff check .`
- **Phase gate:** full suite green under `LC_ALL=C`, both docs tox environments from a clean build, one CI dispatch with all jobs `success`, before `/gsd-verify-work`

### Wave 0 Gaps
None — existing test infrastructure (`pytest`, `black`, `mypy`, `ruff`, `tox -e docs-html`/`docs-pdf`,
`git`, `gh`, `curl`) fully covers every gate this phase needs; every command was exercised
successfully at Phase 70's close six hours before this research, and this session independently
re-confirmed `gh`/`git`/`curl` access live.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | This phase handles no user authentication; `gh`'s own stored credential is out of scope (host-managed, pre-existing). |
| V3 Session Management | No | No sessions are created or consumed. |
| V4 Access Control | No | No access-control logic is written. |
| V5 Input Validation | No | The only "input" processed is this phase's own CHANGELOG prose (author-controlled) and remote read-only API responses (GitHub, PyPI), consumed only for status-code/JSON-field checks, never executed or interpolated into a shell command unescaped. |
| V6 Cryptography | No | `sha256sum` is used for content-identity fencing (Pattern 2), not for any security boundary — a collision would need to be adversarially engineered against a project maintainer's own local requirements file, which is outside this phase's threat model. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Command injection via unescaped shell interpolation of a remote API response (e.g. a GitHub API field embedded unquoted into a follow-up shell command) | Tampering | Every precedent evidence file consumes `gh`/`curl` output only through `--json`/`--jq` structured extraction or fixed-format `grep`/`sed`, never string-interpolated into a subsequent command without quoting. Continue that discipline. |
| Accidental irreversible action (tag push, PyPI upload, GitHub Release, PR merge) executed early by a plan that misreads "prep-only" | Repudiation / Elevation of Privilege (of the phase's own scope) | This is this phase's own central risk, already fully mitigated by design: every irreversible verb (`git push --tags`, `release.yml` dispatch, `gh pr create`/`merge`) is explicitly named as forbidden in every plan's scope, and D-07/Pattern 5 hands the one genuinely irreversible step (the PR) to a **separate**, later command (`/gsd-complete-milestone`), never to this phase. |
| Requirement-state tampering by automated tooling outside plan control | Tampering | Pattern 2 / Pitfall 7 — the checksum fence with a third post-tooling observation. |

Trust boundaries this phase crosses, all **read-only** (the `COVERAGE.md` pattern, Pitfall 8):
`origin` (this repository's own GitHub remote — read via `git fetch`/`git ls-remote`, written only
by the single fast-forward push of the canonical milestone branch, per D-10), GitHub Actions API
(read via `gh run`/`gh workflow run` for CI dispatch), GitHub Releases/PRs API (read-only via `gh
release list`/`gh pr list`), and PyPI's public JSON API (read-only via `curl`). No credential beyond
the host's own pre-existing `gh` auth token is used, and none is created, rotated, or logged by this
phase.

## Sources

### Primary (HIGH confidence)
- `.planning/milestones/v0.9.3-phases/69-v0-9-3-close-prep-prep-only-unpublished/` — the full plan/
  evidence/review/verification set for the nearest precedent phase, read in full this session.
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/` — `70-BASELINE-
  EVIDENCE.md`, `70-MASK-PILOT-EVIDENCE.md`, `70-AFTER-STATIC-EVIDENCE.md`, `70-AFTER-RUNTIME-
  EVIDENCE.md`, `70-DOCS-DIFF-EVIDENCE.md`, `70-CI-EVIDENCE.md` — the exact-value source for every
  D-11 anchor and D-03 evidence-sentence citation.
- Live `git`, `gh`, `curl` commands run in this session against the real repository and real remote
  services (GitHub API, PyPI) — see inline `[VERIFIED: live … this session]` tags throughout.
- `.planning/ROADMAP.md` (Phase 71 section and the 13 milestone-wide binding constraints), read in
  full this session.

### Secondary (MEDIUM confidence)
- `.planning/STATE.md` (top ~560 lines, read this session) — corroborates measured state at
  discussion time and Phase 70's close numbers.

### Tertiary (LOW confidence)
- None — every claim in this document is either `[VERIFIED]` (tool-confirmed this session or in a
  precedent evidence file this session opened and read) or `[CITED]` (referenced from a project
  artifact without independent live re-run this session, e.g. Phase 69's own `69-VERIFICATION.md`
  8/8 score, which this research did not re-run but which was itself an independent live
  re-verification at the time it was produced).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies; every tool version cited was read from a precedent
  evidence file or confirmed live this session.
- Architecture: HIGH — the entire pattern set is reused, not designed; Phase 69's own verifier
  independently re-confirmed the shape works end to end.
- Pitfalls: HIGH — every pitfall listed was an actual, documented incident in this project's own
  history (not a hypothetical), with the exact evidence-file citation for each.

**Research date:** 2026-09-13
**Valid until:** this research is anchored to fixed git history (SHAs, tags, requirement text) that
cannot drift; the only time-sensitive facts are the "measured live this session" values (open PRs,
`main` protection, tag/PyPI/release state) — re-verify those at plan-execution time if more than a
few hours pass, exactly as every precedent phase in this family does as a matter of course.
