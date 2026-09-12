# Phase 69: v0.9.3 Close Prep (prep-only, unpublished) - Research

**Researched:** 2026-09-13
**Domain:** Prep-only milestone closeout — CHANGELOG authoring under `## [Unreleased]`, checksum-fenced
requirement closure, evidence-file conventions, GitHub Actions CI, pre-flight trial-merge, git/GitHub
read-only probes. No product code (`typsphinx/`) is touched.
**Confidence:** HIGH — every load-bearing claim in this document was measured live against the
current tree in this research session (not recalled from CONTEXT.md or ROADMAP.md prose), or is a
direct quote from a file this session opened with `Read`.

## Summary

Phase 69 is a template-shaped phase: this project has now closed **two** structurally identical
prep-only phases (61 — unpublished, like this one; 63 — published) and the CONTEXT.md already
resolves every open design question (D-01..D-14) with the owner's approval. The research task here
is therefore not "what stack/pattern to use" but "reproduce the precedent decomposition faithfully,
and re-measure every number CONTEXT.md quotes, because CONTEXT.md itself says its own numbers are
stale by execution time." That prediction was already correct at research time: the trial-merge tree
SHA CONTEXT.md recorded (`7c9e3002…`) is `2a8a5907…` today, and the branch is 116 commits ahead of
`origin`, not 114 — both because two more commits landed between context-gathering and this research
session. Nothing else measured has drifted: `pyproject.toml` is still `0.9.2`, no `v0.9.3` tag exists
locally or on the remote, no GitHub Release or PyPI upload exists for `0.9.3`, the `typsphinx/` diff
against `origin/main`'s merge-base is empty, and the decoy branch `gsd/v0.9.3-milestone` does not
exist today.

Phase 61 (`.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/`) is the load-bearing
precedent, not Phase 63: it is the one prior unpublished close (v0.9.1 was completed but never
released — its work shipped as part of v0.9.2), so its `61-HANDOFF.md` opens with the negative
("this milestone publishes nothing"), exactly the polarity Phase 69's D-09 calls for. Phase 63
published, so its handoff opens with the positive checklist; Phase 69 must not copy that opening.
Both phases share the fence mechanism (`{phase}-CLOSEOUT-GUARD.md`: baseline SHA-256 + `wc -l` +
`grep -n 'REL-NN'` recorded at phase head, re-verified at phase close, and reproduced verbatim inside
the handoff for a third post-`phase.complete` observation) — reuse it unchanged, scoped to `REL-12`.

**Primary recommendation:** Decompose as 4 plans across 3 waves, mirroring Phase 61's shape exactly
(wave 1: CHANGELOG bullets + closeout-guard baseline + fence-probe-1, run in parallel since they touch
disjoint files; wave 2: green-tree proof + CI dispatch, depends on wave 1's CHANGELOG landing; wave 3:
fence-probe-2 + handoff, depends on wave 2). Add one CONTEXT-specific addition Phase 61/63 did not
need: a non-committing D-07 trial-merge pre-flight, which this research already executed once
read-only (see § Code Examples) and which any plan can safely re-run identically.

## Architectural Responsibility Map

This phase makes no product-behavior change, so the conventional client/server/API/database tiers do
not apply. The relevant "tiers" here are project-maintenance surfaces:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| CHANGELOG authoring | Documentation / release surface (`CHANGELOG.md` → `docs/source/changelog.rst` → Read the Docs) | — | `CHANGELOG.md` is included wholesale into published docs via `myst_parser.sphinx_`; a malformed bullet is a docs warning, not a silent no-op |
| Requirement-state fencing | `.planning/` project metadata | — | `.planning/REQUIREMENTS.md`'s REL-12 checkbox is read by `phase.complete`-family tooling; the fence is pure measurement, no product code involved |
| Tree-greenness proof | CI (GitHub Actions, `ci.yml`) | Local (`pytest`/`black`/`mypy`/tox docs envs) | CI holds authority for `ruff` and the Windows/macOS lanes (constraint 7); local runs cover everything CI does not gate faster |
| Branch/PR mechanics | git + GitHub (remote) | — | Push, `workflow_dispatch`, and (at `/gsd-complete-milestone`, out of phase) PR open/merge |
| Handoff authoring | `.planning/` documentation | — | Consumed by a human operator running `/gsd-complete-milestone`, not by any automated tool |

## User Constraints

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: The milestone is described in three bullets under a `### Changed` subsection of the
  existing `## [Unreleased]`.** One bullet per track, bold lead phrase, requirement IDs in trailing
  parentheses (house style since Phase 33): (1) the `dev` extra and `tox.ini` return to `tox-uv` from
  `tox-uv-bare` (TOX-01..TOX-04); (2) Dependabot's Python updates switch from the `pip` to the `uv`
  ecosystem, so each dependency PR updates `pyproject.toml` and `uv.lock` in the same commit and
  passes `uv sync --locked` (DEP-01..DEP-05); (3) a NixOS development shell in which `flake.nix` runs
  the project's own `.venv` tools inside an FHS sandbox, with the contributor notes updated to match
  (NIX-01..NIX-08, DOC-19..DOC-21). Precedent measured: `0.4.4` (`### Changed` → "CI/Release
  Durability") and `0.5.0` (`### Added` → "CI Durability Guardrails", Dependabot group) both recorded
  tooling-only work as bold-lead bullets; `### Changed` fits because every item modifies existing
  tooling.
- **D-02: Each bullet states plainly that it has no effect on installing or using typsphinx.**
  `docs/source/changelog.rst` includes `CHANGELOG.md` wholesale, so the bullets are published on Read
  the Docs `latest` once REL-12 merges. Write them as prose a user reads, not internal shorthand, and
  do not name `v0.9.3` or `0.9.3` anywhere in the prose (no release carries that number).
- **D-03: The new `### Changed` block sits above `### Planned for Future Releases`, which stays
  byte-identical.** Same placement Phase 61 used. The tail link-reference block is untouched: no
  `[0.9.3]` line, `[Unreleased]` compare base stays `v0.9.2` (SC#2).
- **D-04: No `### Verified` subsection and no lead paragraph under `## [Unreleased]`.** The next
  release-prep phase authors `### Verified` against its own whole diff when it promotes these bullets
  into a versioned section, exactly as Phase 63 did with Phase 61's bullets.
- **D-05: The `ruff` 0.15.20 → 0.16.6 bump (#138) gets no bullet of its own.** It is a routine
  `dev`-extra version bump already on `main`; the DEP bullet describes the mechanism that produced it.
  The DEP bullet may cite it as the first dependency PR to pass under the new ecosystem if that reads
  naturally (Claude's discretion), but it is not a separate entry.
- **D-06: The milestone branch does not absorb `main` in this phase; Phase 67 D-04 carries forward
  unchanged.** No `origin/main` → milestone merge commit and no local re-provisioning against `main`'s
  lock inside Phase 69. SC#3's green is proven on this phase's own tip; the merged tree is linted
  under `ruff` 0.16.x by the PR's own required checks at `/gsd-complete-milestone`.
- **D-07: Phase 69 records a non-committing trial-merge pre-flight as evidence.** Re-run at execution
  time and transcribe verbatim — `git fetch origin`, `git merge-tree --write-tree HEAD origin/main`
  (exit code and tree SHA), and `uv lock --check` against that tree's `pyproject.toml` + `uv.lock`
  extracted to scratch (for example via `git archive <tree> pyproject.toml uv.lock`). Optionally also
  `ruff check .` at the merged lock's `ruff` version over the merged tree inside the FHS runner.
  Nothing from this pre-flight is committed to the branch.
- **D-08: `69-HANDOFF.md` includes the branch-update step, required by `main`'s strict protection.**
  In order: merge `origin/main` into the canonical milestone branch with a merge commit (never a
  rebase), push, open the PR, wait for all six required checks to be green on the updated head, then
  merge with a merge commit — the method every prior milestone PR used. The handoff states the reason
  the update is mandatory (`strict: true`), and that the post-update `ruff` is the merged lock's
  version (0.16.x).
- **D-09: `69-HANDOFF.md` opens by stating the negative.** Its first lines say this milestone
  publishes nothing — no tag, no PyPI upload, no GitHub Release, no version bump — and that the
  `typsphinx-doc-translations` `update-pin.yml` dispatch and the Read the Docs `stable` verification
  are not applicable.
- **D-10: The open dependabot PRs #139..#142 are named in `69-HANDOFF.md` and left untouched.** No
  merge, close, rebase request or comment in this phase or as part of REL-12.
- **D-11: The `0.9.3` version number is recorded as unclaimed, not decided.** No `v0.9.3` tag exists
  and none is created; the next release-prep phase promotes D-01's bullets into its versioned section.
- **D-12: The fence is `69-CLOSEOUT-GUARD.md`, reusing the `61-CLOSEOUT-GUARD.md` /
  `63-CLOSEOUT-GUARD.md` procedure.** `sha256sum`, `wc -l`, `git rev-parse HEAD` as `PHASE_BASE_SHA`,
  and `grep -n 'REL-12' .planning/REQUIREMENTS.md` recorded at phase head; re-run and MATCH at phase
  close; and once more after `phase.complete`-family tooling runs. A flip is reverted with
  `git checkout -- .planning/REQUIREMENTS.md` and reported, never committed. Every plan's
  `SUMMARY.md` declares `requirements-completed: []`. SHA-256 is the primary probe (a flip leaves
  `wc -l` unchanged).
- **D-13: One CI dispatch on the phase's final tip, after the branch is pushed.**
  `git push origin gsd/v0.9.3-toolchain-and-dependency-update-repair` first (origin is behind), then
  `gh workflow run CI --ref gsd/v0.9.3-toolchain-and-dependency-update-repair`, waited to completion,
  every job conclusion transcribed literally with both `windows-latest` lanes and `macos-latest`
  named, and `ruff`'s verdict read from the `Lint and Format Check` job. No plan triggers
  `release.yml`. A second dispatch is justified only if a later plan lands a code-affecting change.
- **D-14: Before any push, re-check the decoy branch.** Constraint 9's `gsd/v0.9.3-milestone` decoy
  is absent today (confirmed again in this research session), but the commit helper re-creates it per
  milestone. If it reappears, advance the canonical pointer before deleting the decoy, and push only
  the canonical branch.

### Claude's Discretion

- Exact prose of the three bullets, within D-01..D-05.
- Plan decomposition, waves, and evidence-file naming following the Phase 61/63 set
  (`69-CLOSEOUT-GUARD.md`, `69-CHANGELOG-EVIDENCE.md`, `69-GREEN-TREE-EVIDENCE.md`, `69-CI-EVIDENCE.md`,
  `69-HANDOFF.md`, plus a pre-flight evidence file for D-07). `69-VERIFICATION.md` is reserved for the
  verifier and must not be plan-authored.
- Whether the D-07 pre-flight includes the optional `ruff` run on the merged tree.
- Docs warning baselines for SC#3, provided both are taken from a clean build (`rm -rf docs/_build`
  first).

### Deferred Ideas (OUT OF SCOPE)

- Disposition of dependabot PRs #139..#142 — after REL-12, as ordinary dependency maintenance (D-10).
- Choosing whether the next published release is `0.9.3` — next milestone's scoping (D-11).
- `PROJECT.md`'s superseded claim that #123/#128 "will need closing so the `uv` ecosystem opens fresh
  ones" — for the milestone-close `PROJECT.md` update, not this phase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-12 | the milestone is merged to `main` via a PR, with no tag, no PyPI upload and no GitHub Release, and `pyproject.toml` still at `0.9.2` | Cited for coverage only, per D-12/D-13/constraint 14. This phase never checks the box; it fences it (§ Code Examples, § Common Pitfalls) and hands off the merge steps to `/gsd-complete-milestone` (§ Code Examples § Handoff shape). Verified this session: `pyproject.toml:7` reads `0.9.2`; no `v0.9.3` tag anywhere; no PyPI/GitHub Release for `0.9.3`; trial-merge against `origin/main` is clean. |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- **Worktree-isolated execution is the standing mode.** Every plan executes in its own worktree;
  provision with `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` first, then run
  everything via `uv run`. This is mandatory even for a low-parallelism phase like this one — do not
  degrade to sequential main-tree execution.
- **A fresh worktree's `uv sync --extra dev` does not install the `docs` extra.** `myst_parser` lives
  only in the `docs` extra (`pyproject.toml:49-54`); any plan comparing docs-build warning counts, or
  running `tests/test_changelog_page_gate.py`'s content-coverage classes, must sync
  `--extra dev --extra docs` explicitly and report skipped counts honestly (verified again this
  session: `import myst_parser` succeeds in the **main checkout's** current venv, which already
  carries `--extra docs` from Phase 68's restoration — a **fresh worktree** starts without it).
- **Locale.** The NixOS FHS sandbox passes `LANG` through unchanged; CI runs English. A plan that
  compares warning/error text against a recorded baseline should run under `LC_ALL=C` locally to
  pre-empt the locale-dependent CI-only defect class.
- **On the maintainer's NixOS machine only:** the seven bare shims (`uv`, `tox`, `ruff`, `black`,
  `mypy`, `pytest`, `sphinx-build`) resolve to `.venv/bin/<tool>` via `typsphinx-fhs-run`. This does
  not change how CI or a non-NixOS contributor runs anything, and is irrelevant to a worktree's own
  provisioning (which still needs the standing `uv sync --extra dev` + `uv run` recipe above).
- **No `ln -sf`/`patchelf` manual step exists or should be re-introduced.**
- **Toolchain-pin sync hazard:** if `tox-uv` vs `tox-uv-bare` rationale text is touched anywhere in
  this phase (it should not be — Phase 68 already updated all five sync points), all five locations
  must move together. Not expected to apply to Phase 69's scope (CHANGELOG + evidence files only).

## Standard Stack

No new library, package, or tool is introduced by this phase — it is CHANGELOG prose, git/GitHub
read-only probes, and `.planning/` evidence files. The "stack" here is the project's own existing
toolchain, unchanged:

### Core (existing, unchanged)
| Tool | Version (measured this session) | Purpose | Why Standard |
|------|-----|---------|--------------|
| `uv` | `0.12.13` (main checkout) | Dependency/lock management, `uv lock --check` for D-07 | Already the project's sole package manager |
| `git` | `2.54.0` | `merge-tree`, `ls-remote`, `diff`, `archive` — all read-only probes this phase runs | Standard |
| `gh` | `2.100.0` | `pr list`, `release list`, `run list/view`, `workflow run` (D-13's dispatch) | Standard, already used by every prior release-prep phase |
| `pytest` | via `tox` (`4.56.1` main checkout) | Full-suite green-tree proof | Existing test runner |
| `black` | `26.5.1` | Format check | Existing |
| `ruff` | `0.15.20` (main checkout, dev-extra pinned `<0.16`) | Lint — **authority is CI**, not this host | Existing; CONTEXT constraint 7 |
| `mypy` | `2.1.0` | Type check | Existing |

### Installation

No installation step. This phase adds zero lines to `pyproject.toml` or `uv.lock`.

## Package Legitimacy Audit

**Not applicable — this phase installs, adds, or upgrades zero packages.** `pyproject.toml` and
`uv.lock` are read-only in this phase (the only earlier `pyproject.toml`/`tox.ini` edit in the whole
milestone was Phase 65's `tox-uv-bare` → `tox-uv` revert, already merged and verified). Confirmed this
session: the milestone branch's own diff against `origin/main`'s merge-base under `typsphinx/` is
empty, and the trial-merge (D-07) shows the only `pyproject.toml` difference from `main` is the
already-landed `tox-uv`/`ruff` range lines, not a new dependency.

## Architecture Patterns

### System Architecture Diagram

```
 CONTEXT.md (D-01..D-14, locked)
        │
        ▼
 ┌─────────────────────────────┐        ┌──────────────────────────────┐
 │ Wave 1 (parallel, disjoint   │        │  git/GitHub (read-only)      │
 │ files)                       │        │                               │
 │  Plan A: CHANGELOG.md edit   │───┐    │  git fetch origin             │
 │   (D-01..D-05)                │   │    │  git merge-tree --write-tree  │
 │  Plan B: closeout-guard       │   │    │  git ls-remote --tags/--heads │
 │   baseline + fence probe 1    │   │    │  gh release list / pr list    │
 │   (D-12, REL-12 read-only)    │   │    │  gh run list/view             │
 └─────────────┬────────────────┘   │    └──────────────┬───────────────┘
               │ (CHANGELOG lands)  │                   │ (probes feed
               ▼                    │                    evidence files)
 ┌─────────────────────────────┐    │
 │ Wave 2 (depends on wave 1)   │◀───┘
 │  Plan C: green-tree proof    │
 │   (pytest/black/mypy/docs)   │
 │   + push + CI dispatch (D-13)│
 └─────────────┬────────────────┘
               │ (tree proven green, CI run recorded)
               ▼
 ┌─────────────────────────────┐
 │ Wave 3 (depends on wave 2)   │
 │  Plan D: fence probe 2       │
 │   (re-verify CLOSEOUT-GUARD) │
 │   + 69-HANDOFF.md (D-07..D-11)│
 └─────────────┬────────────────┘
               │
               ▼
   /gsd-complete-milestone (OUT OF PHASE)
   — merges origin/main into branch, opens PR, waits
     for 6 required checks, merges — REL-12 closes HERE
```

### Recommended Plan/Wave Decomposition

Following Phase 61's shape exactly (4 plans / 3 waves), with D-07's pre-flight folded into wave 3's
handoff plan (research already executed it once, read-only, reproducibly — see § Code Examples):

```
Wave 1 (parallel — disjoint files):
  69-01  CHANGELOG.md bullets (D-01..D-05)                 -> CHANGELOG.md, 69-CHANGELOG-EVIDENCE.md
  69-02  Closeout-guard baseline + fence probe 1 (D-12)      -> 69-CLOSEOUT-GUARD.md,
                                                                 69-SC-INVARIANTS.md (or equivalent),
                                                                 COVERAGE.md

Wave 2 (depends on 69-01, 69-02 — tree must carry the CHANGELOG edit before proving green):
  69-03  Green-tree proof + push + CI dispatch (D-13)        -> 69-GREEN-TREE-EVIDENCE.md,
                                                                 69-CI-EVIDENCE.md

Wave 3 (depends on 69-02, 69-03):
  69-04  Fence probe 2 + D-07 pre-flight + 69-HANDOFF.md      -> 69-CLOSEOUT-GUARD.md (extended),
                                                                 69-PREFLIGHT-EVIDENCE.md,
                                                                 69-HANDOFF.md
```

**Why this shape, not something novel:** Phase 61 used exactly this wave count and dependency
structure for the identical phase shape (unpublished close, checksum fence, standalone handoff), and
it passed verification 4/4 (61-VERIFICATION.md) with a clean code review (0/0/0 findings). Phase 63
needed two extra gap-closure waves (4, 5) only because it *published* — a real version bump and a
GitHub-Release-bound extractor byte-identity proof, both absent from Phase 69's unpublished shape.

### Pattern 1: The three-command checksum fence
**What:** Record `sha256sum`, `wc -l`, and a scoped `grep -n 'REL-NN'` against
`.planning/REQUIREMENTS.md` at phase head; re-run the identical three commands at phase close, then a
third time after `phase.complete`-family tooling runs (which includes `/gsd-verify-work`'s inline
auto-transition, not only a manual `phase.complete` invocation).
**When to use:** Any phase holding a release requirement `[ ]` through its own close, where
`phase.complete`-family tooling has a documented history of auto-flipping it.
**Example (verbatim commands, reusable unchanged for REL-12):**
```bash
# Wave 1 (phase head)
sha256sum .planning/REQUIREMENTS.md
wc -l .planning/REQUIREMENTS.md
git rev-parse HEAD               # -> PHASE_BASE_SHA
grep -n 'REL-12' .planning/REQUIREMENTS.md

# Wave 3 (phase close) — compare all four against the wave-1 values
sha256sum .planning/REQUIREMENTS.md
git diff --name-only -- .planning/REQUIREMENTS.md   # expect: no output
grep -n 'REL-12' .planning/REQUIREMENTS.md          # expect: byte-identical

# After phase.complete-family tooling runs (outside any plan's reach — reproduce
# this exact block inside 69-HANDOFF.md so the operator reaches it without
# opening 69-CLOSEOUT-GUARD.md separately)
sha256sum .planning/REQUIREMENTS.md
git diff --name-only -- .planning/REQUIREMENTS.md
grep -n 'REL-12' .planning/REQUIREMENTS.md
# On divergence: git checkout -- .planning/REQUIREMENTS.md   (never commit the flip)
```
**Track record in this project:** the flip has landed at **seven of eight** consecutive
release-prep closes (41, 46, 52, 57 held; 61 held; 63 flipped twice — once via `phase.complete`
directly, once again via `/gsd-verify-work`'s auto-transition — and was reverted both times). It has
never *not* been caught once this exact three-command fence was in place. Expect it to fire here too;
budget the revert step as a certainty, not a contingency.

### Pattern 2: Positive-control remote probes
**What:** Every "prove X does not exist on the remote" probe is paired with a probe for something
that *does* exist, from the same fetch, so an unreachable remote cannot be mistaken for a clean
negative.
**When to use:** Any SC#1-shaped "prove unpublished" claim.
**Example (measured live this session):**
```bash
$ git ls-remote --tags origin 'v0.9*'
ada0b845cf1f5a495dc7c522b80e79ed5c76004d	refs/tags/v0.9.0
68b92e24e6ca3df410ca0435d226629ef7ef1e2e	refs/tags/v0.9.0^{}
8797b1783df23187bdce3eec231f0578dcdb9ecb	refs/tags/v0.9.2
45962faad21520c72ac9f1e14c7f684050826bb6	refs/tags/v0.9.2^{}
# v0.9.0 and v0.9.2 present (positive control) — v0.9.3 absent (the claim)

$ curl -s -o /dev/null -w "%{http_code}\n" https://pypi.org/pypi/typsphinx/0.9.2/json
200
$ curl -s -o /dev/null -w "%{http_code}\n" https://pypi.org/pypi/typsphinx/0.9.3/json
404
# 0.9.2 reachable (positive control) — 0.9.3 404 (the claim)

$ gh release list --limit 5
Release v0.9.2	Latest	v0.9.2	2026-08-30T15:11:29Z
Release v0.9.0		v0.9.0	2026-08-22T07:46:15Z
...
# v0.9.2 is Latest and present; no v0.9.3 row exists
```

### Pattern 3: D-07's non-committing trial-merge pre-flight
**What:** Prove the eventual `origin/main` merge (executed at `/gsd-complete-milestone`, out of
phase) is conflict-free and lock-consistent, without creating a commit or touching the branch.
**When to use:** Any prep-only phase whose eventual PR must pass `main`'s `strict: true` branch
protection (requiring the branch be up to date with `main` before merge).
**Example (executed this session, read-only, reproducible verbatim):**
```bash
$ git fetch origin
$ git merge-tree --write-tree HEAD origin/main
2a8a590724e3dcfcfcdc62dccd20ac2ce444d3c3
$ echo "rc=$?"
rc=0
# rc=0 with a real tree SHA means: no conflict.

$ mkdir -p /tmp/scratch-69-preflight
$ git archive 2a8a590724e3dcfcfcdc62dccd20ac2ce444d3c3 pyproject.toml uv.lock \
    | tar -x -C /tmp/scratch-69-preflight
$ cd /tmp/scratch-69-preflight && uv lock --check
Using CPython 3.14.4
Resolved 91 packages in 0.61ms
# exit 0, no drift -- the post-merge lock is self-consistent

$ grep -n '^version' pyproject.toml            # still 0.9.2 (D-11: this pre-flight never bumps)
7:version = "0.9.2"
$ grep -n '^name = "ruff"' -A2 uv.lock          # merged lock's ruff, matches D-08
1209:name = "ruff"
1210-version = "0.16.6"
```
**Important:** the tree SHA is **not stable** across research/planning/execution sessions — it moves
every time either branch gains a commit. CONTEXT.md's `7c9e3002…` (recorded 2026-09-13, discussion
time) is already stale versus this session's `2a8a5907…` (same day, ~2 commits later). **Any plan
must re-run this command fresh and record its own value — never copy a prior session's tree SHA.**

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Proving the eventual merge is conflict-free | A scratch branch + real `git merge` + `git reset --hard` cleanup | `git merge-tree --write-tree HEAD origin/main` | Zero side effects, no branch/HEAD ever moves, no cleanup step that can be forgotten or fail |
| Checking the merged lock is consistent | Checking out the merge result and running `uv sync` in the live tree | `git archive <tree> pyproject.toml uv.lock` into a scratch dir, then `uv lock --check` there | Isolates the check from the live worktree; nothing in the live tree is touched |
| Detecting the `phase.complete` requirement flip | Trusting `phase_complete: true` / a green `/gsd-verify-work` transcript | The three-command SHA-256/`wc -l`/`grep` fence, re-run a third time *after* the tooling runs | This project's own history: the flip has recurred through **two different entry points** (`/gsd-execute-phase`'s `phase.complete` call, and `/gsd-verify-work`'s inline auto-transition) — a fence that only checks once, or only checks the requirement's own grep instead of the whole-file digest, has already missed a wider blast radius (Phase 63 flipped REL-09 **and** REL-10 **and** REL-11 together; a REL-09-scoped grep alone would have missed two of three) |
| Deciding whether a remote probe reached its source | Trusting an empty result | Pair every negative probe with a positive control from the identical fetch | An unreachable `git ls-remote`/`gh api` call and a genuinely clean negative are byte-identical without one |

**Key insight:** every mechanism this phase needs already exists in this project's own history as a
working, verified precedent (Phase 61 for the fence+handoff shape, Phase 65/66/67 evidence files for
the D-07-style non-committing probe idiom). There is no external library or novel technique to
research here — the entire research task is re-measurement and faithful reuse of precedent shape.

## Common Pitfalls

### Pitfall 1: Citing a stale trial-merge tree SHA or ahead-count
**What goes wrong:** CONTEXT.md's `git merge-tree` tree SHA (`7c9e3002…`) and "114 commits behind"
figure are already wrong by the time planning/execution runs — this research session measured
`2a8a5907…` and 116 commits, only hours after CONTEXT.md was written.
**Why it happens:** the branch keeps gaining commits (context-gathering, research, planning docs) and
`origin/main` may too; both sides of the trial merge are moving targets.
**How to avoid:** every plan that reports a trial-merge result, an ahead/behind count, or a decoy-branch
census must re-run the measurement itself and record its own fresh value, never quote CONTEXT.md's or
this RESEARCH.md's numbers as current.
**Warning signs:** a plan's evidence file citing a tree SHA or commit count with no accompanying
"measured at <timestamp>" and no live command transcript.

### Pitfall 2: The `phase.complete` flip has now hit two different entry points
**What goes wrong:** Phase 63 measured the requirement-checkbox flip landing not only through
`/gsd-execute-phase`'s direct `phase.complete` call, but a **second time**, identically, through
`/gsd-verify-work`'s inline auto-transition (which calls the same underlying verb via
`transition.md`). A fence that only re-checks after one specific command has a blind spot.
**Why it happens:** any workflow that transitions a phase's status calls the same tooling internally.
**How to avoid:** `69-HANDOFF.md` must state the guard applies to **every** transition entry point,
not just a manual `phase.complete` invocation, and the decisive third observation must be taken by
whichever orchestrator step runs last (outside any plan's own reach), not folded into the last plan.
**Warning signs:** a closeout guard section titled only "after `phase.complete` runs" with no mention
of `/gsd-verify-work`.

### Pitfall 3: `pytest --collect-only -q` output is `=`-decorated
**What goes wrong:** `grep -oE '^[0-9]+ tests? collected'` or a line-anchored `sed` looking for the
count returns empty, because the actual line is `==== 1548 tests collected in 0.33s ====`.
**How to avoid:** use an unanchored extraction, e.g. `grep -oE '[0-9]+ tests? collected'`.

### Pitfall 4: Evidence-file `KEY = value` lines with trailing prose break exact comparisons
**What goes wrong:** a verify step doing `sed -n "s/^KEY = //p"` gets polluted output if the value
line carries trailing explanation.
**How to avoid:** put the bare value on its own line; put any explanation on the next line.

### Pitfall 5: A fresh worktree silently skips the changelog content-coverage tests
**What goes wrong:** `tests/test_changelog_page_gate.py`'s two content-coverage classes guard on
`import myst_parser`, which lives only in the `docs` extra. A worktree provisioned with the standing
`uv sync --extra dev` recipe has no `docs` extra, so both classes SKIP silently — a green `pytest`
exit code proves nothing about CHANGELOG content rendering.
**How to avoid:** any plan that needs this proof syncs `--extra dev --extra docs` explicitly, and
reports **PASSED counts with zero SKIPPED**, not the bare exit code. (Measured baseline at Phase 68
close, main checkout: 1547 passed / 1 skipped. A worktree run will show a different skip count purely
from the missing `docs` extra, not from a defect.)

### Pitfall 6: An incremental docs rebuild under-reports warnings
**What goes wrong:** `tox -e docs-html` / `docs-pdf` run against a stale `docs/_build` reuses cached
output and reports fewer warnings than a clean build would, manufacturing a false "matches baseline."
**How to avoid:** `rm -rf docs/_build` immediately before each counted build, every time, on both
sides of any comparison — this is a documented recurring finding in this project (Phase 63's D-21),
not a theoretical risk.

### Pitfall 7: The main checkout's `uv sync --extra dev` is an *exact* sync
**What goes wrong:** running `uv sync --extra dev` from the main checkout (not a worktree) removes
the `docs` extra if it was previously installed, silently breaking any subsequent docs-warning
comparison run from there.
**How to avoid:** restore with `uv sync --extra dev --extra docs` before running docs tox
environments from the main checkout. (Confirmed this session: the main checkout currently *does*
carry `myst_parser` — Phase 68 left it restored — but this is fragile to a bare re-sync.)

### Pitfall 8: The decoy branch recurs per milestone
**What goes wrong:** the commit helper (`gsd-tools query commit`) has, in this milestone's own
history, created a `gsd/v0.9.3-milestone` decoy branch alongside the canonical
`gsd/v0.9.3-toolchain-and-dependency-update-repair` — verified absent as of this research session,
but its recurrence pattern in this project is "created again next commit," not "gone for good."
**How to avoid:** re-check `git branch -a | grep '0.9.3'` immediately before any push. If the decoy
exists and carries HEAD, fast-forward the canonical ref (`git merge-base --is-ancestor` first to
confirm linearity), re-point HEAD with `git symbolic-ref` (never `git checkout`, to preserve
uncommitted files), then delete the decoy — never delete the decoy first.

### Pitfall 9: A stale CI run cited as this phase's own green
**What goes wrong:** the branch's most recent completed CI run (`34681968010` / `34681962740`,
2026-09-12, head `d9c75553`) predates this phase's own tip by 116 commits — none of Phase 66–69's
commits are covered by it.
**How to avoid:** D-13's dispatch must run **after** the branch is pushed with this phase's own final
tip (post-CHANGELOG edit), and the evidence file must record the dispatched run's own head SHA,
matched against the phase-close `git rev-parse HEAD`, not the prior run's ID.

### Pitfall 10: Reading `ruff`'s verdict from the wrong CI job or the wrong workflow
**What goes wrong:** `ci.yml` has no step named `Run linters` — that name exists only in
`release.yml:84`, the workflow this phase must never trigger. Reaching for that name (e.g., while
grepping for "the lint step") risks citing the wrong workflow's step.
**How to avoid:** `ruff`'s verdict is the `Lint and Format Check` job's conclusion (`ci.yml:51-70`,
its one substantive step is `Run lint with tox` at `ci.yml:69`, running `uv run tox -e lint` =
`black --check .` + `ruff check .`).

### Pitfall 11: Miscounting CI's job total
**What goes wrong:** CONTEXT.md and ROADMAP.md name "6 required checks" (the branch-protection
subset) — but the full `ci.yml` run has **12 jobs total**: 6 `test` matrix jobs (3 OS × 2 Python:
`ubuntu-latest`/`windows-latest`/`macos-latest` × `3.12`/`3.13`), plus `lint`, `type-check`,
`coverage`, `build`, and 2 `integration` matrix jobs (`basic`, `advanced`). A plan transcribing "every
job conclusion" that stops at 6 has undercounted.
**How to avoid:** `gh run view <id> --json jobs` and assert exactly 12 `conclusion: success` rows,
naming both `windows-latest` test jobs and both `macos-latest` test jobs individually, matching Phase
65/66/67's own precedent (`65-02`: "12/12 success").

## Code Examples

### The full current CI job matrix (measured this session, `.github/workflows/ci.yml`)
```yaml
# jobs, with display names, in file order:
test:          "Test Python ${{ matrix.python-version }} on ${{ matrix.os }}"
  # matrix: os in [ubuntu-latest, windows-latest, macos-latest] × python-version in ['3.12', '3.13']
  # -> 6 jobs: e.g. "Test Python 3.12 on ubuntu-latest", "... on windows-latest", "... on macos-latest"
lint:          "Lint and Format Check"        # one step: "Run lint with tox" -> tox -e lint
type-check:    "Type Check"                   # "Run type check with tox" -> tox -e type
coverage:      "Code Coverage"                # "Run coverage with tox" -> tox -e cov
build:         "Build Package"                # includes the wheel template-bundle canary check
integration:   "Integration Test - ${{ matrix.example }}"
  # matrix: example in [basic, advanced] -> 2 jobs
# Total: 6 + 1 + 1 + 1 + 1 + 2 = 12 jobs.
# Required-check subset (branch protection on main, measured live this session):
#   "Test Python 3.12 on ubuntu-latest", "Test Python 3.13 on ubuntu-latest",
#   "Lint and Format Check", "Type Check", "Code Coverage", "Build Package"
#   strict: true  (branch must be up to date with main before merge)
```

### Current `## [Unreleased]` block (measured this session, `CHANGELOG.md:8-14`)
```markdown
## [Unreleased]

### Planned for Future Releases
- BibTeX/bibliography support
- Glossary generation
- Index generation
- Pre-commit hooks
- Additional Typst Universe template integration
```
`CHANGELOG.md` is 1297 lines total. The tail link block's last two lines (measured):
```
[0.1.0b1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.1.0b1
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.2...HEAD
```
D-03 requires the new `### Changed` block inserted **between** line 8 (`## [Unreleased]`) and line 10
(`### Planned for Future Releases`) — i.e. immediately after the heading, before the existing
subsection — matching Phase 61's placement.

### Requirement traceability row and checkbox to fence (verbatim, `.planning/REQUIREMENTS.md`)
```
75:- [ ] **REL-12**: the milestone is merged to `main` via a PR, with no tag, no PyPI upload and no
76:      GitHub Release, and `pyproject.toml` still at `0.9.2`
...
147:| REL-12 | Phase 69 | Pending |
```
(Line numbers current as of this research session; re-run `grep -n 'REL-12' .planning/REQUIREMENTS.md`
at plan time rather than trusting these — the same caveat as every other fence quote in this project's
history.)

### Handoff shape to reproduce (from `61-HANDOFF.md`, the correct unpublished-close analog)
Opening lines (negative-first, D-09):
```markdown
**This milestone publishes nothing.** `/gsd-complete-milestone` performs no tag (local or
remote), no PyPI publish, no GitHub Release, and no pull request for this milestone [for v0.9.1].
```
For Phase 69, this must be corrected: unlike v0.9.1, **a PR to `main` IS opened and merged** at
`/gsd-complete-milestone` — REL-12 — so `69-HANDOFF.md`'s negative opening must name precisely which
publish actions are absent (tag, PyPI, GitHub Release, version bump) while explicitly retaining the
PR-merge step, and must include Phase 61's three-item "what the next milestone inherits" pattern
adapted to this milestone (dependabot PRs #139-#142 named per D-10, D-08's branch-update step, D-07's
pre-flight result feeding the branch-update step's confidence).

## State of the Art

Not applicable in the conventional sense (no external library ecosystem is being tracked). The
"state of the art" here is this project's own accumulated precedent:

| Prior approach | Current approach | When changed | Impact |
|--------------|------------------|--------------|--------|
| Handoff opens with a publish checklist (Phases 46-57, published closes) | Handoff opens by stating the negative when nothing publishes | Phase 61 (v0.9.1, 2026-08-29) | Phase 69 must follow the negative-first shape, not the majority-precedent positive one |
| Single-observation requirement fence | Three-observation fence (head, close, post-`phase.complete`) | Phase 42 (v0.7.0, three observations formalized), widened again after Phase 63 discovered the flip recurs via `/gsd-verify-work` too | Phase 69's handoff must state the guard applies to every transition entry point |
| REL-checkbox grep scoped to one requirement ID | Whole-file SHA-256 as primary probe | Phase 63 (discovered the flip can widen to sibling requirements — REL-09/10/11 flipped together) | Even though Phase 69 has only one REL requirement (REL-12) in this cycle, the whole-file digest remains the correct primary probe, not a REL-12-scoped grep alone |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The recommended 4-plan/3-wave decomposition is optimal for this specific phase's task list, not merely "what Phase 61 did." | Architecture Patterns § Recommended Plan/Wave Decomposition | Low — this is a planning-discretion area per CONTEXT.md ("Plan decomposition, waves, and evidence-file naming... [is Claude's Discretion]"); the planner may reshape it, this is a recommendation, not a locked decision. |
| A2 | The pre-flight `ruff check .` step (D-07's optional half) is worth running given the FHS runner is available on this machine. | Code Examples § D-07 pre-flight | Low — explicitly Claude's Discretion per CONTEXT.md; omitting it does not fail any success criterion. |

No other claim in this document is `[ASSUMED]`: every factual claim about current repository state,
CI job names, CHANGELOG content, requirement text, and precedent-phase structure was verified live in
this research session via `Read`, `git`, `gh`, or `curl`, and is cited with its measured value inline
rather than recalled from training data.

## Open Questions

1. **Will the D-13 CI dispatch need a second run?**
   - What we know: D-13 states "a second dispatch is justified only if a later plan lands a
     code-affecting change." The only product-tree changes in this phase are `.planning/` evidence
     files and `CHANGELOG.md` — neither is code, and CI's lint/type/test jobs do not read
     `CHANGELOG.md` content (confirmed: no CI job installs the `docs` extra or imports `myst_parser`).
   - What's unclear: whether the CHANGELOG edit landing *after* wave 1 but *before* the wave-2 CI
     dispatch means the dispatch only needs to happen once, after wave 1 merges into the pushed tip.
   - Recommendation: sequence wave 2 (green-tree + CI dispatch) strictly after wave 1's CHANGELOG
     plan lands on the branch, so one dispatch on the final tip suffices — matching D-13's literal
     text ("One CI dispatch on the phase's final tip, after the branch is pushed").

2. **Exact evidence-file name for the two fence-probe observations (SC#1's remote/tag/PR/release
   checks).**
   - What we know: Phase 61 named this `61-SC4-INVARIANTS.md`; Phase 63 named it
     `63-SC5-INVARIANTS.md` (the SC number tracks each phase's own ROADMAP numbering, not a fixed
     name). Phase 69's ROADMAP maps this to SC#1.
   - What's unclear: whether to name it `69-SC1-INVARIANTS.md` for consistency with the SC-number
     convention, or something distinct.
   - Recommendation: `69-SC1-INVARIANTS.md`, following the established `{phase}-SC{N}-INVARIANTS.md`
     pattern where `N` is this phase's own success-criterion number for the no-irreversible-action
     fence (SC#1 here, per the ROADMAP phase-detail numbering in this phase's own section).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | all provisioning, `uv lock --check` (D-07) | ✓ (main checkout) | 0.12.13 | — |
| `git` | all probes, `merge-tree` (D-07) | ✓ | 2.54.0 | — |
| `gh` | remote probes, CI dispatch (D-13) | ✓ | 2.100.0 | — |
| `tox` | full-suite/lint/type/docs environments | ✓ (main checkout) | 4.56.1 | — |
| `black` | green-tree proof | ✓ | 26.5.1 | — |
| `ruff` | local attempt only — **CI is the authority** | ✓ (0.15.20, matches `uv.lock`'s pin — but see note) | 0.15.20 | Local run recorded additively; verdict always cited from CI's `Lint and Format Check` job |
| `mypy` | green-tree proof | ✓ | 2.1.0 | — |
| `myst_parser` (`docs` extra) | changelog content-coverage tests, docs builds | ✓ (main checkout, restored by Phase 68) — **not present in a fresh worktree's `--extra dev` sync** | via `docs` extra | Sync `--extra dev --extra docs` explicitly wherever this proof is needed |
| NixOS FHS shims (`typsphinx-fhs-run`) | maintainer-machine bare-command execution | ✓ (main checkout, direnv-loaded) | — | Irrelevant to worktree execution and to CI |

**Missing dependencies with no fallback:** none identified for this phase's scope.

**Missing dependencies with fallback:** the `docs` extra in a fresh worktree — sync it explicitly
wherever the changelog content-coverage proof or a docs-warning baseline is needed (Pitfall 5, Pitfall
7).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml` `[tool.pytest.ini_options]`, `testpaths = ["tests"]`), orchestrated via `tox` (`env_list = py312, py313, lint, type, cov, docs`) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]`; `tox.ini` |
| Quick run command | `uv run pytest -m "not slow"` |
| Full suite command | `uv run pytest` (matches CI) |
| Baseline (carried in, re-measure — never inherited) | **1547 passed, 1 skipped** — main checkout, Phase 68 close (2026-09-13); a fresh worktree without `--extra docs` will show a different skip count purely from the missing extra, not a defect |

### Phase Requirements → Test Map

This phase has one requirement (REL-12), and it is explicitly **not** closed by any test — it closes
at `/gsd-complete-milestone`, out of phase. The "tests" this phase actually runs are the standing
green-tree proof (SC#3) and the fence probes (SC#1, SC#4), which are audits/observations, not
pass/fail assertions against new product behavior:

| Req/SC | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SC#1 | unpublished-shaped, positive-controlled | audit (git/gh/curl probes) | see § Pattern 2 above | ✅ (no new file needed — git/gh/curl already present) |
| SC#2 | CHANGELOG under `## [Unreleased]`, no new heading/tail link | audit (grep + diff) | `grep -c '^## \[0\.9\.3\]' CHANGELOG.md` → 0; `grep -c '^\[0\.9\.3\]:' CHANGELOG.md` → 0; `git diff` scoped to the tail-link block → empty | ✅ |
| SC#3 | tree proven green, this phase's own runs | full-suite + lint + type + docs + CI | `uv run pytest`; `uv run black --check .`; `uv run mypy typsphinx/`; `rm -rf docs/_build && uv run tox -e docs-html`; same for `docs-pdf`; `gh workflow run CI --ref <branch>` → `gh run watch <id> --exit-status` → `gh run view <id> --json jobs` (12 jobs, all success) | ✅ |
| SC#4 (REL-12 fence) | checksum-fenced, three observations | audit (checksum) | see § Pattern 1 above | ✅ (creates `69-CLOSEOUT-GUARD.md`) |

### Sampling Rate
- **Per task commit:** the CHANGELOG-edit task's own evidence file (`69-CHANGELOG-EVIDENCE.md`) reads
  back the edit and its structural properties (heading count, bullet count) immediately.
- **Per wave merge:** full pytest suite + `black`/`mypy` (wave 2); the fence re-verification (wave 3).
- **Phase gate:** one fresh 3-OS CI dispatch on the phase's own final tip (D-13), both docs tox
  environments from a clean build, and the third checksum observation reproduced in the handoff for
  the operator to run after `phase.complete`-family tooling.

### Wave 0 Gaps
None. Every command this phase needs (`pytest`, `black`, `ruff`, `mypy`, `tox -e docs-html/docs-pdf`,
`git`, `gh`) already exists and was exercised as recently as Phase 68's close (2026-09-13).

## Security Domain

`security_enforcement: true` in `.planning/config.json`, so this section is required. Phase 63's
`63-SECURITY.md` (the closest precedent, same phase shape) recorded `asvs_level: 1`,
`security_block_on: high`, and closed with `threats_open: 0` after re-measuring every mitigation live
— that same shape applies here.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth surface touched |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | marginal | CHANGELOG prose is MyST/Markdown rendered by Sphinx — malformed syntax is a docs-build warning, not a security defect, but is checked (Pitfall 6, docs-warning baseline) |
| V6 Cryptography | no | The SHA-256 checksum fence is an integrity check, not a cryptographic security boundary, but reuses `sha256sum` correctly for its actual purpose (tamper/drift detection, not confidentiality) |

### Known Threat Patterns for this phase's stack (repudiation/tampering-focused, not the OWASP web-app taxonomy)

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Scratch/unreleased content leaking into a future published Release body | Tampering | Structural checks on `CHANGELOG.md`'s heading positions (D-03 keeps the block above `### Planned for Future Releases`, never inside a versioned section this phase creates) |
| `phase.complete`-family tooling silently flipping REL-12's checkbox | Tampering | Three-observation checksum fence (Pattern 1) |
| A vacuous remote-absence proof (unreachable endpoint mistaken for a clean negative) | Repudiation | Positive-control pairing on every probe (Pattern 2) |
| A stale/inherited CI run cited as this phase's own green | Repudiation | D-13's dispatch on the phase's own pushed final tip, with the run's head SHA matched against `git rev-parse HEAD` |
| The decoy branch (`gsd/v0.9.3-milestone`) reappearing and being pushed instead of, or in addition to, the canonical branch | Tampering | D-14's pre-push re-check; verified absent this session, but documented as recurring per-milestone |
| A probe escalating into an irreversible action (e.g., a `gh run list` check becoming a `gh workflow run release.yml`) | Elevation of Privilege | Every command in this research and every plan is read-only or a reversible `ci.yml` dispatch; `release.yml` is never invoked |

## Sources

### Primary (HIGH confidence — read directly this session)
- `.planning/phases/69-v0-9-3-close-prep-prep-only-unpublished/69-CONTEXT.md` — full read, all D-01..D-14
- `.planning/REQUIREMENTS.md` — full read, REL-12 verbatim, traceability table
- `.planning/ROADMAP.md` § v0.9.3 (all 15 constraints, Phase 69 detail block) — full read
- `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/` — `61-CONTEXT.md` (prior
  read, cited in CONTEXT.md), `61-CLOSEOUT-GUARD.md`, `61-HANDOFF.md`, `61-REVIEW.md`, all four
  `61-0N-PLAN.md` frontmatter+must_haves — full read this session
- `.planning/milestones/v0.9.2-phases/63-v0-9-2-release-prep-prep-only/` — `63-CLOSEOUT-GUARD.md`,
  `63-HANDOFF.md`, `63-REVIEW.md`, `63-SECURITY.md`, `63-VALIDATION.md`, all six `63-0N-PLAN.md`
  frontmatter — full read this session
- `.github/workflows/ci.yml` — full read this session, all 12 jobs enumerated
- `CHANGELOG.md` — head, tail, and `[Unreleased]` block read this session; 1297 lines total
- `pyproject.toml` — version literal, `dev`/`docs` extras, `tox-uv` line all read this session
- `tests/test_changelog_page_gate.py` — `RELEASE_VERSIONS` tuple and skip conditions read this session
- Live commands this session: `git tag -l`, `git ls-remote --tags/--heads origin`, `git branch -a`,
  `git merge-tree --write-tree`, `git archive` + `uv lock --check`, `gh pr list`, `gh release list`,
  `gh run list`, `gh api .../branches/main/protection`, `curl` to `pypi.org/pypi/typsphinx/{0.9.2,0.9.3}/json`

### Secondary (MEDIUM confidence)
None — no external (non-project) documentation source was needed for this phase; every mechanism is
internal precedent.

### Tertiary (LOW confidence)
None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new stack; every tool/version quoted was measured live this session
- Architecture (wave/plan decomposition): HIGH for the precedent shape (Phase 61 measured directly);
  MEDIUM for whether 4 plans/3 waves is the exact optimal split for this phase's specific task list
  (flagged as Claude's Discretion in CONTEXT.md, not a locked decision)
- Pitfalls: HIGH — every pitfall either quotes a project-hazard already supplied in the task prompt
  and independently confirmed this session (docs extra, decoy branch, stale CI run, job count), or is
  a direct read of a precedent phase's own recorded incident (the `phase.complete` flip's two entry
  points, Phase 63's blast-radius widening)

**Research date:** 2026-09-13
**Valid until:** This phase should execute within days of this research (prep-only, precedent-driven).
Any git-state number in this document (tree SHAs, ahead/behind counts, current CHANGELOG line numbers)
must be re-measured at plan/execution time regardless of elapsed time — see Pitfall 1.
