# Phase 75: v0.9.6 Release Prep (prep-only) - Research

**Researched:** 2026-09-20
**Domain:** Release engineering / CHANGELOG curation for a Python package built with `uv` + `tox`, prep-only (no publish action)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**The `## [0.9.6]` section's shape**

- **D-01: The Phase 74 doctest bullet goes at the head of `### Fixed`; the six carried bullets are
  byte-identical.** They are promoted in their current assignment — `### Added` (linkcheck) →
  `### Changed` (four contributor-tooling bullets) → `### Fixed` — which is the house order
  `[0.9.2]`, `[0.9.0]` and `[0.8.0]` use. The carried bullets are not compressed, re-worded or
  re-ordered. Within `### Fixed` the order is: doctest (new) → QUA-14 (new, D-09) → the carried
  sidebar bullet.
- **D-02: `## [0.9.6]` carries a lead paragraph, framed on the doctest rendering fix as the
  release's subject.** The contributor tooling is acknowledged in one sentence as a side note.
- **D-03: The lead paragraph recommends the upgrade explicitly**, in the register `[0.9.2]` used
  ("0.9.0 users should upgrade to this release"). The reader's previous release is **0.9.2**, not
  0.9.5 — `0.9.3`, `0.9.4` and `0.9.5` are permanently unclaimed on PyPI. The recommendation's
  justification: the pre-fix failure was not only cosmetic — a `doctest_block` followed by further
  content in the same container aborted `typst.compile()` with `expected semicolon or line break`.
- **D-04: `## [0.9.6]` carries a `### Verified` section, and its invariance claims are stated
  precisely.** The blanket sentence `[0.9.2]` used — "Zero new runtime or dev dependencies across
  this milestone's diff" — is **false for v0.9.6** and must not be copied: the measured
  `v0.9.2..HEAD` diff leaves runtime `dependencies` untouched but does change the `dev` extra
  (`tox-uv-bare` → `tox-uv`, `ruff` cap `<0.16` → `<0.17`). Correct shape: "zero new runtime
  dependencies; the `dev` extra changed only by the `tox-uv` return." Other `### Verified` items:
  the four `@preview` packages unchanged across the three sync surfaces, GATE-01 real-compile
  coverage, and the clean-build warning ledger.
- **D-05: The `## [0.9.6] - YYYY-MM-DD` date is the prep authoring date, fixed, and not corrected
  if the tag lands later.** Precedent: `[0.9.2] - 2026-08-30` written 2026-08-30, merged 2026-08-31
  (one day out); `[0.9.0] - 2026-08-17` written 2026-08-17, tagged 2026-08-22 (five days out).
  `75-HANDOFF.md` records this as a **fact, not a step**.

**The Phase 74 CHANGELOG bullets**

- **D-06: The doctest bullet claims both the rendering fix and the compile failure.** Lead claim:
  a `>>>` example now renders as a Typst code block with its line structure intact. Second
  sentence: in the shape where further content follows the block in the same container, the PDF
  compile itself failed. Measured basis: pre-fix the translator emitted
  `unknown node type: <doctest_block …>` and let the node's `Text` children flow as running prose
  (two such lines in this project's own `api/index` build); the GATE-01 context (a) fixture
  reproduced the `expected semicolon or line break` compile abort on the pre-handler tree.
- **D-07: The bullet discloses the `python`-fence trade-off in one sentence** — the whole block is
  highlighted as Python, so output lines are coloured as Python source rather than console output.
  Measured basis (74-CONTEXT D-01): `codly-languages:0.1.10` has a `python` entry and no `pycon`
  entry. The "honour an existing non-empty language" path (74 D-02) is **not** mentioned — standard
  Sphinx never sets `language` on a `doctest_block`.
- **D-08: The bullet's single evidence sentence is the reflection into the published
  documentation** — typsphinx's own API reference reaches the published docs with this release.
  This **inverts** 73 D-04's standing prohibition ("must not claim the fix is visible on the
  default (`stable`) documentation"), deliberately: that rule existed because v0.9.5 published
  nothing, whereas publishing v0.9.6 moves Read the Docs' `/en/stable/` off `v0.9.2` on its own. The
  sentence does not name warning counts or build numbers.
- **D-09: QUA-14 gets its own bullet, second in `### Fixed`.** Not folded into the doctest bullet,
  not omitted. Says typsphinx's own docstrings no longer raise docutils `Unexpected indentation` /
  `Block quote ends without a blank line` errors when the package is autodoc'd. Measured basis: base
  `6cc44f22` clean `LC_ALL=C -b typst` build reported 3 attributed / 10 raw such messages; tip
  reports zero. Sites fixed: `translator.py`'s `visit_toctree` docstring, `pathfmt.py`'s
  `quote_path` docstring.

**REL-16 — the `### Known Limitations` question**

- **AMENDED 2026-09-20 (owner-approved, measured during discussion): two of the three candidate
  defects REL-16 names are already closed.** `REQUIREMENTS.md:23`, ROADMAP SC3 and `PROJECT.md:88-90`
  all name the candidate set as "NUM-01's per-master `numref` divergence, the converted-image
  rehome collision, the `typst_documents` duplicate-target cluster". Measured: the rehome-collision
  todo and all three `typst_documents`-modelling todos are in `.planning/todos/completed/`;
  `builder.py:40`'s `RESERVED_IMAGE_NAMESPACE` and `builder.py:1068`'s
  `_validate_output_path_collisions()` are the code that closed them (both v0.8.0).
  `.planning/todos/pending/` holds exactly three records: QUA-08, **NUM-01**, MSG-06. The
  requirement text in `REQUIREMENTS.md`/`ROADMAP.md` stays literal and unedited; the reframing lives
  in CONTEXT. What changes is the candidate set, not REL-16's demand for an explicit answer.
- **D-10: `## [0.9.6]` carries a `### Known Limitations` section, holding NUM-01 and nothing
  else.** Writing the two closed defects would publish already-fixed issues as current
  limitations. WR-02/WR-03 (genuinely open) are **not** added — REL-16 does not name them.
- **D-11: The NUM-01 entry states the precondition, both symptoms, and a workaround.** Shape
  follows the existing `### Known Limitations` precedent at `CHANGELOG.md:1205` (bold lead,
  sub-bullets, a `Workaround:` line): precondition (only in a multi-master `typst_documents`
  configuration); symptom (a) (a figure reachable from two masters gets one baked-in Sphinx number
  while Typst counts per compiled wrapper — silently wrong in one master's PDF); symptom (b) (a
  figure reachable only from a non-root master never enters the `root_doc` scan — falls back to
  raw label text, with exactly **one** Sphinx warning naming the label); workaround (single-master
  config, or `:ref:` instead of `:numref:`). No fix promise, no version promise.
- **D-12: The `grep` over `CHANGELOG.md` for `Known Limitations` and this decision record must
  agree, and the phase evidence names which branch was taken (SC3).** After this phase the file
  carries **two** `### Known Limitations` headings: the pre-existing one in `[0.1.0b1]` at `:1205`
  and the new one in `[0.9.6]`. Any grep-based check expects two, not one.

**Phase 74's leftovers**

- **D-13: The five untracked `probe_*.typ` files at the repo root are deleted in this phase.**
  Untracked, so the deletion produces no commit. `.gitignore` is **not** edited.
- **D-14: IN-01 is not fixed here; it is filed as a pending todo.** `74-REVIEW.md`'s unresolved
  Info finding — `visit_literal_block`/`depart_literal_block` still document `node: The literal
  block node` although both signatures widened to `nodes.literal_block | nodes.doctest_block` —
  stays untouched; a new record goes in `.planning/todos/pending/`.

**Push and CI dispatch**

- **D-15: The branch is pushed whenever it is convenient; exactly one CI run is dispatched, on the
  bumped tip.** `ci.yml`'s triggers are scoped to `main`/`develop`, so a push to the milestone
  branch runs no CI — push cost is zero and push timing carries no evidence weight. The single
  `gh workflow run CI --ref gsd/v0.9.6-doctest-block-rendering-and-release` happens **after** the
  bump and CHANGELOG work is pushed. If a dispatch returns HTTP 5xx, `gh run list` is checked before
  any retry.

### Claude's Discretion

- **The fence.** `75-CLOSEOUT-GUARD.md` recording `sha256sum`/`wc -l` of `.planning/REQUIREMENTS.md`,
  `PHASE_BASE_SHA`, and the verbatim `grep -n 'REL-15'` lines at phase head; re-run and MATCH at
  phase close **and once more after `phase.complete`-family tooling has run**, including
  `/gsd-verify-work`'s inline transition. SHA-256 is the primary probe. REL-16's line is recorded
  separately as expected-to-move. On a flip: `git checkout -- .planning/REQUIREMENTS.md`, reported,
  never committed. Every plan's `SUMMARY.md` declares `requirements-completed: []` for REL-15. Back
  up REQUIREMENTS/ROADMAP/STATE to scratch before `phase.complete`/`/gsd-verify-work` runs.
- **The trial merge is non-committing** (71 D-05 / 73 D-09): `git fetch origin`;
  `git merge-tree --write-tree HEAD origin/main` with exit code and tree SHA transcribed;
  `git archive <tree> pyproject.toml uv.lock` into scratch then `uv lock --check`; `ruff check .`
  on the merged tree. `main`'s protection, merge method and required contexts are read with
  `gh api`, not assumed. Expected to be a no-op — `origin/main` is still the milestone base.
- **The bump mechanics.** `pyproject.toml:7` is the sole hand-edited version literal; `uv.lock` is
  regenerated by `uv lock`, never edited; `README.md`'s Status line goes to `v0.9.6`;
  `tests/test_changelog_page_gate.py`'s `RELEASE_VERSIONS` gains `"0.9.6"`; all of it lands in one
  commit whose `git show --name-only` lists the four files together.
- **The fresh `## [Unreleased]`.** Placed above `## [0.9.6]` and retaining only
  `### Planned for Future Releases`, which is **not** promoted.
- **The tail link block.** `[Unreleased]`'s compare base `v0.9.2` → `v0.9.6`, plus a new
  `[0.9.6]: …/releases/tag/v0.9.6` line above `[0.9.2]`. No `## [0.9.3]`, `## [0.9.4]` or
  `## [0.9.5]` heading or tail link is created.
- **`scripts/extract_changelog_section.py 0.9.6` is executed** and its stdout transcribed into the
  phase evidence, verified non-empty, byte-faithful to the `## [0.9.6]` section, and free of the
  `Planned for Future Releases` scratch block.
- **Requirement IDs** are attached in the trailing-parenthesis style existing bullets use, and the
  two new bullets do **not** carry "This has no effect on installing or using typsphinx."
- **The handoff.** `75-HANDOFF.md` enumerates the PR to `main` and required checks, the `v0.9.6`
  tag push, the expected manual approval of the `pypi` GitHub Environment, the GitHub Release body
  being byte-identical to the extract script's stdout, the **manual**
  `typsphinx-doc-translations` `update-pin.yml` dispatch, the Read the Docs `en`/`ja` `stable`
  endpoints reporting `0.9.6`, and the four observations REL-15 is checked on. It records that
  `create-release` has never run on a v0.9.x tag and a failure there is handled inside the release
  work rather than deferred. It also carries D-05's date fact, D-14's filed todo, and the
  Dependabot ordering rule if any PR has opened by then.
- **The decoy branch.** If `gsd/v0.9.6-milestone` appears carrying commits, the canonical ref is
  fast-forwarded to it and HEAD re-pointed with `git symbolic-ref` **before** the decoy is deleted.
- **The probes.** `git tag -l 'v0.9.6'` and a remote tag probe, empty at two observations separated
  by intervening waves, each remote probe carrying a `v0.9.2` positive control; PyPI 404 for
  `0.9.6` with a 200 for `0.9.2`; no `v0.9.6` GitHub Release.

### Deferred Ideas (OUT OF SCOPE)

- **Fixing NUM-01.** Only its disclosure is in scope. The todo stays pending after this phase.
- **Disclosing WR-02 / WR-03 in the CHANGELOG.** Genuinely open, but not named by REL-16.
- **Fixing IN-01** (`visit_literal_block`/`depart_literal_block` `Args:` text). Filed as a pending
  todo for a future milestone.
- **Adding `probe_*.typ` to `.gitignore`.** Rejected as a product-tree commit outside REL-15's file
  set. Deletion alone is sufficient.
- QUA-08 (linkcheck CI workflow) — needs a side PR to `main`, not this phase.
- MSG-06 (hardcoded delimiter in `translator.py` DEBUG logs) — touches `typsphinx/`, out of reach
  behind the prep-only fence.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-15 | v0.9.6 is published — bump, CHANGELOG promotion, tail-link move, PR/tag/PyPI/Release. **Mapped to Phase 75 for coverage only; checkbox stays `[ ]` at this phase's close** — see Pattern 3 (closeout-guard fence) and the Recommended Plan Decomposition's guard/handoff plans. | Bump mechanics ([VERIFIED: pyproject.toml:7, README.md:348] confirmed this session), CHANGELOG promotion shape ([VERIFIED: CHANGELOG.md:1-69] confirmed this session), extractor invocation ([VERIFIED: scripts/extract_changelog_section.py] read in full), the closeout-guard pattern (reused from Phases 46/69/71/73) |
| REL-16 | The `### Known Limitations` question is settled on the record — **closes inside this phase**. | AMENDED block + D-10/D-11/D-12 (verified this session against `.planning/todos/completed/` listing and `builder.py:40`/`builder.py:1068`), the NUM-01 todo's exact symptom text ([VERIFIED: `.planning/todos/pending/2026-08-14-numref-…md`] read in full), the existing `### Known Limitations` precedent at `CHANGELOG.md:1205` (read this session) |
</phase_requirements>

## Summary

Phase 75 is a release-prep phase that produces zero irreversible action: it curates one
`## [0.9.6]` CHANGELOG section (promoting six carried `## [Unreleased]` bullets plus two new
Phase-74 bullets and a new `### Known Limitations` section naming NUM-01 alone), bumps
`pyproject.toml`/`uv.lock`/`README.md` to `0.9.6`, re-proves the bumped tree green through fresh
runs (pytest ×2, lint/type/format, docs builds, linkcheck, one dispatched CI run, a non-committing
trial merge against `origin/main`), holds REL-15's checkbox at `[ ]` behind a SHA-256 fence
re-verified three times, and writes a standalone `75-HANDOFF.md` for `/gsd-complete-milestone` to
execute against. Every mechanism this phase needs — the extractor script, the three version-sync
tests, the closeout-guard fence, the non-committing trial merge, the decoy-branch handling, the CI
dispatch discipline — already exists in this repository and was proven working across four prior
release-prep phases (46, 69, 71, 73). This is not exploratory work: the shape is settled, and the
job is to adapt that settled shape to this phase's two deltas from precedent (a genuine publish,
not a merge-only close; and a `### Known Limitations` section, which none of the four precedents
carried).

**Primary recommendation:** Reuse Phase 73's 7-plan/4-wave evidence-file decomposition
(closeout-guard baseline → combined bump+CHANGELOG commit → green-tree/CI/trial-merge evidence in
parallel → closeout-guard re-verification + handoff), adapted per the "What must change from a
literal copy" list below — most importantly, **bundle the version bump, the CHANGELOG edit, and
the `RELEASE_VERSIONS` test edit into one commit** (a genuine divergence from Phase 46's two-commit
precedent), and add the `### Known Limitations` drafting work that no prior prep-only phase needed.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Version-literal bump (`pyproject.toml`, `uv.lock`, `README.md`) | Build/Release config | — | Pure metadata edit; no runtime code path reads these differently |
| CHANGELOG curation (`CHANGELOG.md`) | Documentation | Release config | Published documentation (`docs/source/changelog.rst` includes it) that also feeds `release.yml`'s GitHub Release body |
| Known Limitations disclosure | Documentation | — | User-facing disclosure text, not a code change; NUM-01 itself lives in `typsphinx/translator.py` but is untouched this phase |
| Green-tree proof (pytest/lint/type/docs/linkcheck) | CI/Build | — | Re-measurement only; no test or fixture is authored |
| Closeout-guard fence | Release process / tooling | — | Guards `.planning/REQUIREMENTS.md` against auto-flip by `phase.complete`-family tooling; not a product-tree concern |
| Non-committing trial merge | Release process | Git/VCS | Read-only probe of `origin/main` divergence; never mutates a ref |
| Handoff (`75-HANDOFF.md`) | Release process | — | Procedure document for `/gsd-complete-milestone`, executed by a different command entirely |

This phase touches **no** Browser/Client, Frontend-Server, API/Backend or Database/Storage tier —
it is entirely Build/Release-config and Documentation tier work over a Python package's own
metadata files. `**UI hint**: no` in ROADMAP is correct; there is no frontend-shaped capability
anywhere in this phase's scope.

## Standard Stack

### Core (already pinned in this repo; no new dependency this phase)
| Tool | Version (verified this session) | Purpose | Why Standard |
|------|-----|---------|--------------|
| `uv` | 0.12.13 (`[VERIFIED: uv --version, this session]`) | Lockfile regeneration (`uv lock`), sync (`uv sync --extra dev --locked`) | Project's standing dependency manager since v0.9.3 |
| `tox` (via `tox-uv`) | env_list `py312, py313, lint, type, cov, docs` (`[VERIFIED: tox.ini:2]`) | `docs-html`, `docs-pdf`, `linkcheck` envs | Project's standing task runner |
| `ruff` | pinned `>=0.15,<0.17` in `pyproject.toml` dev extra (`[VERIFIED: pyproject.toml:40]`) | Lint | Standing gate; **on this NixOS machine `ruff` must be invoked via the PATH shim, not `.venv/bin/ruff` directly** — see Pitfall below |
| `black` | pinned `>=26,<27` (`[VERIFIED: pyproject.toml:39]`) | Format check | Standing gate |
| `mypy` | pinned `>=1.13,<3.0` (`[VERIFIED: pyproject.toml:41]`) | Type check | Standing gate |
| `myst-parser`, `furo`, `sphinx-intl`, `sphinx-autodoc-typehints` | `docs` extra (`[VERIFIED: pyproject.toml:49-54]`) | Doc build; **the changelog-page gate needs `myst-parser` importable or it skips** | Standing `docs` extra |
| `gh` CLI | authenticated this session (`[VERIFIED: gh auth status]`) | Branch protection reads, CI dispatch, decoy census, PR-related probes | Standing release tooling |

No new runtime or dev dependency is introduced by this phase (ROADMAP constraint 7; D-04's
`### Verified` wording covers exactly this). Skip the Package Legitimacy Audit section entirely —
**not applicable: this phase installs no new package.**

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `scripts/extract_changelog_section.py` for the release-notes body | Hand-copy the `## [0.9.6]` section into the evidence file | Rejected — SC2 explicitly requires *executing* the script and transcribing its stdout, not reimplementing or hand-copying the extraction (D-06 in the script's own docstring: this is "the ONE committed, pytest-covered implementation") |
| `git merge --no-ff origin/main` now | `git merge-tree --write-tree` (non-committing) | The non-committing form is mandated (71 D-05 / 73 D-09) — a real merge commit is irreversible action, forbidden this phase |

## Architecture Patterns

### System Architecture Diagram

```
                    ┌─────────────────────────┐
                    │ .planning/REQUIREMENTS.md│  (READ-ONLY this phase)
                    │  REL-15 [ ]  REL-16 [ ]  │
                    └───────────┬──────────────┘
                                │ sha256sum + wc -l + grep -n 'REL-15'
                                ▼
                    ┌─────────────────────────┐
                    │ 75-CLOSEOUT-GUARD.md    │◄── re-verified 3x (head / close / post-tooling)
                    │  (fence baseline)       │
                    └─────────────────────────┘

  CHANGELOG.md (## [Unreleased] : 6 bullets)          pyproject.toml (0.9.2)
        │                                                    │
        │  promote 6 + Phase-74's 2 new bullets               │  edit version literal
        │  + new ### Known Limitations (NUM-01 only)          ▼
        │  + fresh empty ## [Unreleased] above               uv lock  ──►  uv.lock (0.9.6)
        │  + move tail link block                              │
        ▼                                                      ▼
  CHANGELOG.md (## [0.9.6] curated)             README.md Status line → v0.9.6
        │                                                      │
        └──────────────────┬───────────────────────────────────┘
                            │  ONE commit (git show --name-only lists all 4/5 files)
                            ▼
                 scripts/extract_changelog_section.py 0.9.6
                            │  stdout → transcribed, non-empty, byte-faithful
                            ▼
                 ┌───────────────────────────────┐
                 │ bumped, curated tree (HEAD)   │
                 └───────────┬───────────────────┘
                             │
        ┌────────────────────┼─────────────────────────┐
        ▼                    ▼                         ▼
  pytest ×2 / lint /   git push + gh workflow      git merge-tree
  type / docs-html /   run CI --ref <branch>       (non-committing,
  docs-pdf / linkcheck  → observe to completion     origin/main probe)
        │                    │                         │
        ▼                    ▼                         ▼
  75-GREEN-TREE-        75-CI-EVIDENCE.md         75-PREFLIGHT-EVIDENCE.md
  EVIDENCE.md
        │                    │                         │
        └────────────────────┴─────────────────────────┘
                             │
                             ▼
              re-run closeout-guard fence (MATCH) + probes
              (tag / PyPI / GitHub Release — all empty, v0.9.2 positive control)
                             │
                             ▼
                     75-HANDOFF.md  (procedure for /gsd-complete-milestone)
```

A reader can trace the primary use case end to end: REQUIREMENTS.md is fenced first (read-only),
the CHANGELOG+bump edit lands as one commit, the extractor proves the section is well-formed, three
independent green-tree checks run off that one commit (local suite, CI dispatch, trial merge), and
the fence is re-verified before a handoff document is written — never a tag, a PyPI upload, or a
merge.

### Recommended Project Structure (evidence files, following the reused naming convention)
```
.planning/phases/75-v0-9-6-release-prep-prep-only/
├── 75-CLOSEOUT-GUARD.md        # fence baseline + close + post-tooling re-verification
├── 75-BUMP-EVIDENCE.md         # pyproject.toml/uv.lock/README.md diff proof + uv sync --locked
├── 75-CHANGELOG-EVIDENCE.md    # promotion proof, Known Limitations section, tail links, extractor
│                                #   transcript, byte-identity of carried bullets
├── 75-GREEN-TREE-EVIDENCE.md   # pytest x2, lint/type/format, docs-html/docs-pdf, linkcheck
├── 75-CI-EVIDENCE.md           # decoy census, push, single CI dispatch, all job conclusions
├── 75-PREFLIGHT-EVIDENCE.md    # non-committing trial merge, main protection, Dependabot census
├── 75-SC-INVARIANTS.md         # (optional) scope-fence + two-observation probe roll-up
├── 75-HANDOFF.md               # standalone procedure for /gsd-complete-milestone
├── COVERAGE.md
└── 75-0N-PLAN.md / 75-0N-SUMMARY.md  (per plan)
```

### Pattern 1: The combined bump+CHANGELOG commit — a genuine divergence from Phase 46's precedent
**What:** Phase 46 (v0.7.1, the only prior prep-only phase that both bumped the version *and*
published) split this into **two commits**: `46-01` edited `CHANGELOG.md` alone, `46-02` then
bumped `pyproject.toml`/`uv.lock`/`README.md` in a separate commit. Phase 75's own binding text
(75-CONTEXT.md's Phase Boundary bullet 1, and ROADMAP SC1's literal wording) instead requires **one
commit** whose `git show --name-only` lists `pyproject.toml`, `uv.lock`, `README.md` **and**
`CHANGELOG.md` together.
**When to use:** This phase, specifically — do not default to Phase 46's split-commit precedent
without checking this divergence first.
**Caution — a genuine text ambiguity to resolve before planning (see Open Questions):**
75-CONTEXT.md's "Claude's Discretion → The bump mechanics" bullet names exactly four files as
landing in "one commit" — `pyproject.toml`, `uv.lock`, `README.md`, and
`tests/test_changelog_page_gate.py` (the `RELEASE_VERSIONS` edit) — and does **not** list
`CHANGELOG.md` in that same sentence. But the Phase Boundary section (bullet 1) and ROADMAP SC1
both explicitly say the one commit touches "`pyproject.toml`, `uv.lock`, `README.md` and
`CHANGELOG.md` together." The safe resolution that satisfies both readings: **bundle all five
files — `pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md`, and
`tests/test_changelog_page_gate.py` — into one commit.** Nothing in either text forbids a
superset; SC1's explicit four-file list is satisfied as a subset, and the test edit's presence in
the same tree state is in any case needed before SC1's own "zero skipped" changelog-gate reading
can be taken on the bumped tip.
```bash
# Source: 75-CONTEXT.md Phase Boundary bullet 1 + Claude's Discretion "The bump mechanics";
# ROADMAP.md Phase 75 SC1. Adapt Pattern 1 from 46-RESEARCH.md (version-literal bump), but land
# it in the SAME commit as the CHANGELOG edit, not a separate one.
# 1. Edit pyproject.toml:7 -- version = "0.9.2" -> "0.9.6"
# 2. Regenerate the lock so its cached typsphinx entry picks up the new version:
uv lock
# 3. Sync --locked to PROVE the lock now matches pyproject.toml:
uv sync --extra dev --locked
# 4. Edit README.md's Status line -> **Status**: Stable (v0.9.6) - Production ready
# 5. Edit CHANGELOG.md: promote the six carried bullets + Phase 74's two new bullets into
#    ## [0.9.6], add ### Known Limitations (NUM-01 only), move the tail link block, leave a
#    fresh empty ## [Unreleased] with only ### Planned for Future Releases above it.
# 6. Edit tests/test_changelog_page_gate.py's RELEASE_VERSIONS tuple: append "0.9.6".
# 7. ONE commit:
git add pyproject.toml uv.lock README.md CHANGELOG.md tests/test_changelog_page_gate.py
git commit -m "..."
git show --name-only HEAD   # must list exactly these five (superset of both readings)
```

### Pattern 2: SHA-256 closeout-guard fence with three re-verification points
**What:** Guards `.planning/REQUIREMENTS.md` against the auto-flip `phase.complete`-family tooling
has produced at 9 of the 10 prior release-prep closes (ROADMAP constraint 9). Line-scoped to
**REL-15** specifically this time (not the whole file), because REL-16 legitimately closes inside
this phase and its lines are expected to move.
**When to use:** Baseline recorded at phase head (before any plan commits); re-verified at phase
close; re-verified **once more** after `phase.complete`/`/gsd-verify-work` have run — this third
observation is the one that actually catches the flip.
```bash
# Source: 73-RESEARCH.md Pattern 3, adapted for a line-scoped (not whole-file) fence.
# At phase head:
PHASE_BASE_SHA=$(git rev-parse HEAD)
REQ_SHA256_BASE=$(sha256sum .planning/REQUIREMENTS.md | awk '{print $1}')
REQ_LINES_BASE=$(wc -l < .planning/REQUIREMENTS.md)
grep -n 'REL-15' .planning/REQUIREMENTS.md   # transcribe every hit verbatim; classify each as
                                              # state-bearing (checkbox / traceability row) or
                                              # informational (prose mention) -- verified this
                                              # session: 4 hits at lines 22, 59, 73, 76; only 22
                                              # (checkbox) and 59 (traceability) are state-bearing
grep -n 'REL-16' .planning/REQUIREMENTS.md   # recorded SEPARATELY as expected-to-move: verified
                                              # this session: 4 hits at lines 23, 30, 47, 60; 23
                                              # (checkbox) and 60 (traceability) are state-bearing
                                              # and MAY flip to [x]/Complete inside this phase

# At phase close, and AGAIN after phase.complete/gsd-verify-work:
sha256sum .planning/REQUIREMENTS.md   # compare to REQ_SHA256_BASE -- MATCH expected
wc -l .planning/REQUIREMENTS.md       # compare to REQ_LINES_BASE
git diff --name-only -- .planning/REQUIREMENTS.md   # empty expected
# On divergence: git checkout -- .planning/REQUIREMENTS.md ; report, never commit.
```
Every count above (line numbers, hit counts) was measured **this research session** on the current
tip and will have shifted by the time any plan executes — re-measure fresh at each plan's own base,
exactly as constraint 4 requires; the point of transcribing it here is to show the exact command
shape and the exact classification discipline (state-bearing vs. informational), not to hand the
planner a number to assert blind.

### Pattern 3: Non-committing trial merge against `origin/main`
**What:** Proves the bumped/curated tree would merge cleanly with whatever `origin/main` currently
is, without ever creating a merge commit.
**When to use:** Every release-prep phase since 71/73; this phase's measured expectation is a
no-op, since `origin/main` (`6cc44f22`) still equals the milestone base — but re-measure, don't
assume, since Phase 73's own Dependabot census went from 9 stale branches to 0 stale branches
between this phase's discussion and this research session (see Common Pitfalls).
```bash
# Source: 73-RESEARCH.md Pattern 2, unchanged.
git fetch origin
git merge-tree --write-tree HEAD origin/main   # exit code + printed tree SHA, both transcribed
# Re-run once to confirm idempotency (same tree SHA both times).
mkdir -p /tmp/trial-merge-scratch && cd /tmp/trial-merge-scratch
git -C /path/to/repo archive <tree-sha> pyproject.toml uv.lock | tar -x
uv lock --check                                # against the merged tree's own lock
ruff check .                                   # against the merged tree (superficial; full
                                                # merged-tree check needs the whole tree archived)
gh api repos/YuSabo90002/typsphinx/branches/main/protection \
  --jq '{required_status_checks: .required_status_checks.contexts, strict: .required_status_checks.strict}'
# Verified this session: 6 contexts (Test Python 3.12/3.13 on ubuntu-latest, Lint and Format Check,
# Type Check, Code Coverage, Build Package), strict: true.
```

### Pattern 4: The `### Known Limitations` entry shape — new to this phase, no prior prep-only
### phase authored one from scratch
**What:** v0.9.0's precedent (`MILESTONES.md:618-638`) is a *declined* carve-out recorded only in
the handoff and pending-todos — never in `CHANGELOG.md` itself. The only in-`CHANGELOG.md`
precedent is the `[0.1.0b1]` section at `:1205`, written for a wholly different (early,
feature-incompleteness) context. D-10/D-11 require a genuinely new, disclosure-only entry.
**Draft shape** (adapt, do not copy verbatim — the planner's plan should re-derive wording from the
NUM-01 todo and D-11's four elements at execution time):
```markdown
### Known Limitations

- **`:numref:` numbers can diverge or vanish in a multi-master `typst_documents` configuration
  (NUM-01).** This affects only projects declaring more than one master document; a single-master
  project is unaffected. A figure reachable from two masters gets one Sphinx-assigned number baked
  into the `:numref:` reference text, while each compiled Typst wrapper counts captions
  independently — so the same reference reads correctly in one master's PDF and points at the
  wrong number in another's, with nothing reporting the divergence. A figure reachable only from a
  non-root master never enters Sphinx's root-document figure-number scan, so its `:numref:`
  reference falls back to the raw label text instead of a number — Sphinx does emit one warning
  naming the label, so a build-log reader gets a diagnostic even though the PDF reader does not.
  **Workaround:** use a single-master configuration, or `:ref:` in place of `:numref:` for the
  affected figures.
```
Source for the precondition/symptom wording: `.planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` (read in full this session — both symptoms, corrected "one warning, not silent" finding, confirmed matching D-11 verbatim) — `[VERIFIED: .planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md]`.

### Anti-Patterns to Avoid
- **Reconstructing the three-item Known-Limitations candidate set from `REQUIREMENTS.md:23` or
  ROADMAP SC3's literal text.** Both name three defects; two are already closed. Follow the AMENDED
  block and D-10, not the literal requirement text.
- **Copying `[0.9.2]`'s blanket "Zero new runtime or dev dependencies" sentence into `### Verified`.**
  Measured false for this milestone's diff (the `dev` extra changed). D-04 gives the corrected
  wording.
- **A single-file bump commit.** ROADMAP SC1 explicitly calls out "a commit touching only
  `pyproject.toml` is the exact shape that once killed every dependabot PR" — this project has a
  standing memory of that exact failure mode.
- **Fixing anything under `typsphinx/`.** The prep-only fence (D-14, and 46 D-03/D-27's precedent)
  forbids it even for a small, well-understood defect like IN-01.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| GitHub Release body extraction | A new script or hand-copy of the `## [0.9.6]` section | `scripts/extract_changelog_section.py 0.9.6` | It is the ONE committed, pytest-covered implementation; `release.yml` calls this exact script from both its `validate` and `create-release` jobs — a second, independently-hand-copied extraction could silently diverge from what CI actually runs |
| Lockfile version sync | Manually editing `uv.lock`'s `typsphinx` stanza | `uv lock` (regenerate), then `uv sync --extra dev --locked` (prove it matches) | `uv.lock` is a generated artifact; a hand edit risks drifting from the resolver's actual output and would not be re-derivable |
| Branch protection / required-checks knowledge | Assuming the 6-context set from a prior phase's memory | `gh api repos/.../branches/main/protection` | Verified this session to still be 6 contexts and `strict: true` — but this is exactly the kind of fact that changes between milestones and must be re-read, not assumed (ROADMAP constraint 10) |
| Merge conflict pre-check | A hand-simulated diff review | `git merge-tree --write-tree` | The project's standing non-committing-trial-merge mechanism (71 D-05 / 73 D-09); reproducible, exit-code-checkable, and never mutates a ref |

**Key insight:** every mechanism this phase needs is already a committed, tested artifact in this
repository (the extractor script, the three version-sync tests, `tox.ini`'s five relevant envs, and
four prior prep-only phases' evidence-file conventions). The work is disciplined re-execution and
fresh measurement, not construction.

## Common Pitfalls

### Pitfall 1: Worktree `uv sync --extra dev` omits the `docs` extra, producing a false pass
**What goes wrong:** `tests/test_changelog_page_gate.py`'s content-coverage classes (which assert
`RELEASE_VERSIONS` including `"0.9.6"` actually renders) are gated by
`@pytest.mark.skipif(not MYST_PARSER_AVAILABLE, ...)`. A fresh worktree provisioned only with
`--extra dev` per CLAUDE.md's standing worktree-isolation recipe never installs `myst-parser`
(it lives in the `docs` extra), so these classes **skip silently** rather than fail — and SC1
explicitly demands a **zero-skipped** reading.
**Why it happens:** `uv sync --extra dev` installs exactly the `dev` extra; `docs` is a separate
extra (`furo`, `sphinx-autodoc-typehints`, `sphinx-intl`, `myst-parser` — `[VERIFIED: pyproject.toml:33-54]`, read this session).
**How to avoid:** provision the worktree with `uv sync --extra dev --extra docs`. Verified this
session in the main checkout: `.venv/pyvenv.cfg` shows a uv-managed CPython 3.13.13 and
`myst_parser` imports cleanly there — meaning the main checkout *does* currently carry the `docs`
extra, but a fresh worktree built strictly per CLAUDE.md's `env -u VIRTUAL_ENV -u
UV_PROJECT_ENVIRONMENT uv sync --extra dev` recipe will not, unless the plan widens that command.
**Warning signs:** `pytest -rs` reporting skips in `test_changelog_page_gate.py`; a `0 skipped`
assertion silently passing on the wrong test file instead of this one.

### Pitfall 2: `ruff` cannot run as `.venv/bin/ruff` on this NixOS machine
**What goes wrong:** Verified this session — `.venv/bin/ruff --version` fails with `Could not
start dynamically linked executable`. The PATH-resolved `ruff` (the FHS shim,
`/nix/store/.../ruff/bin/ruff` on `PATH`) runs fine (`ruff check .` → `All checks passed!`).
**Why it happens:** `ruff` ships a generic-linux binary that NixOS cannot exec directly; CLAUDE.md's
"NixOS development shell" section documents the shim mechanism.
**How to avoid:** invoke bare `ruff`/`black`/`mypy`/`pytest`/`tox`/`uv`/`sphinx-build` (relying on
the shims already on `PATH` from the direnv-loaded session), never `.venv/bin/<tool>` directly, on
this machine.
**Warning signs:** a `Could not start dynamically linked executable` error — per CLAUDE.md this
means the shim is not on PATH (session not launched from the direnv-loaded checkout), not a code
regression.

### Pitfall 3: Localized console text hides English-string greps
**What goes wrong:** A grep for `unknown node type`, `Unexpected indentation`, or
`build succeeded, N warnings.` finds zero and looks like a pass, when the real cause is that
Sphinx's console text is localized under the host's `LANG` inside the FHS sandbox.
**How to avoid:** every docs-build grep this phase performs (re-proving Phase 74's zero counts on
the bumped tip, per SC4) runs under `LC_ALL=C`, paired with a positive control — the same command
on a known-warning-carrying build must find the messages before any zero is believed.

### Pitfall 4: Incremental docs rebuilds under-report warnings
**What goes wrong:** An incremental Sphinx build reuses cached state and reports fewer warnings
than a clean build would, manufacturing a false "baseline match".
**How to avoid:** `rm -rf` the output directory before every counted docs build this phase runs
(`docs-html`, `docs-pdf`, `linkcheck`), matching ROADMAP constraint 5 exactly.

### Pitfall 5: `gh workflow run` returning HTTP 5xx while still creating a run
**What goes wrong:** A dispatch call can error transport-side while GitHub still enqueues the run.
Retrying blind risks a second run, breaking the "exactly one CI dispatch" reading D-15 requires.
**How to avoid:** on any dispatch error, run `gh run list --workflow=CI.yml --branch
gsd/v0.9.6-doctest-block-rendering-and-release` first; only retry if no matching run exists.

### Pitfall 6: The Dependabot census has already drifted since the discussion that produced 75-CONTEXT.md
**What goes wrong:** 75-CONTEXT.md records "nine stale `dependabot/uv/*` remote branches" as of
2026-09-20's discussion. This research session, on the same calendar day, measured **zero**
Dependabot branches on `origin` (`git ls-remote --heads origin` lists only the three `gsd/*`
milestone branches and `main`) — `[VERIFIED: git ls-remote --heads origin, this session]`. Whatever
the plan finds at its own execution time is very likely to be a *third* different count.
**How to avoid:** this is exactly what ROADMAP constraint 4 and CONTEXT's own domain-section caveat
("Context only — constraint 4 requires each plan to re-measure fresh at its own base") anticipate.
Never transcribe the "nine" figure into a plan's `must_haves`; measure at execution time and adapt
the handoff's Dependabot-ordering note to whatever is actually open then (D-15's precedent: if any
PR has opened by execution, order it after the milestone PR — v0.9.3's #143→#142→#141 precedent).

### Pitfall 7: `phase.complete` / `/gsd-verify-work` mangling STATE.md/ROADMAP.md incidentally, not
just REQUIREMENTS.md
**What goes wrong:** this project's own memory record
(`roadmap-update-plan-progress-mangles-wrapped-line.md`) documents that these tooling paths have
orphaned wrapped lines and flipped HALTED status incorrectly in prior phases, beyond just the
REQUIREMENTS.md auto-flip this phase's fence targets.
**How to avoid:** back up `ROADMAP.md` and `STATE.md` to scratch (outside the repo) before
`phase.complete`/`/gsd-verify-work` runs, per Claude's Discretion → The fence; diff them against
the backup afterward, not just REQUIREMENTS.md.

## Code Examples

### Decoy-branch census and safe push (reusable verbatim from prior phases' evidence files)
```bash
# Source: 72-CI-EVIDENCE.md "Decoy census" pattern, reused by 73-04.
# If a decoy carrying commits exists: fast-forward canonical ref to it FIRST,
# re-point HEAD with git symbolic-ref, THEN delete the decoy. Never delete first.
git branch --list 'gsd/v0.9.6*'
git ls-remote --heads origin 'gsd/v0.9.6*'
# Verified this session: no gsd/v0.9.6-milestone decoy exists yet, locally or on origin.
```

### Probing the four release-not-yet-happened facts, each with a positive control
```bash
# Source: 73-SC1-INVARIANTS.md shape, adapted for v0.9.6/v0.9.2.
git tag -l 'v0.9.6' 'v0.9.2'                 # expect: v0.9.2 present, v0.9.6 absent
git ls-remote --tags origin | grep -E 'v0\.9\.(2|6)'   # same expectation, remote
curl -sf -o /dev/null -w '%{http_code}\n' https://pypi.org/pypi/typsphinx/0.9.6/json  # expect 404
curl -sf -o /dev/null -w '%{http_code}\n' https://pypi.org/pypi/typsphinx/0.9.2/json  # expect 200 (control)
gh release list --limit 5   # expect no v0.9.6 entry
```
Verified this session: `git tag -l 'v0.9.6'` → empty; `v0.9.0`/`v0.9.2` present as remote tags
(`git ls-remote --tags origin`).

### Reading `main`'s branch protection and merge-method settings, exact `jq` shape
```bash
# Source: 71-PREFLIGHT-EVIDENCE.md / 72-BASE-EVIDENCE.md shape; re-verified this session.
gh api repos/YuSabo90002/typsphinx/branches/main/protection \
  --jq '{required_status_checks: .required_status_checks.contexts, strict: .required_status_checks.strict}'
# -> {"required_status_checks":["Test Python 3.12 on ubuntu-latest","Lint and Format Check",
#     "Type Check","Code Coverage","Build Package","Test Python 3.13 on ubuntu-latest"],"strict":true}
gh api repos/YuSabo90002/typsphinx --jq '{allow_merge_commit, allow_squash_merge, allow_rebase_merge}'
# -> all three true; precedent (#132/#136/#143/#145/#151) has been a merge commit every time.
```

### Extracting and verifying the curated release section
```bash
# Source: scripts/extract_changelog_section.py's own module docstring + release.yml's `validate`
# job step "Verify CHANGELOG has a section for this version".
uv run python scripts/extract_changelog_section.py 0.9.6 > /tmp/release_notes_0.9.6.md
test -s /tmp/release_notes_0.9.6.md && echo "non-empty: OK"
grep -c 'Planned for Future Releases' /tmp/release_notes_0.9.6.md   # expect 0
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Dependabot on the `pip` ecosystem, whose PRs stalled at `uv sync --locked` | Dependabot on the `uv` ecosystem | v0.9.3 (Phase 65-ish, `DEP-01..05`) | Dependency PRs actually run CI now; this phase's Dependabot census reads the current (possibly zero) state of that pipeline, not the old stalled one |
| `tox-uv-bare` (worked around an unrelated NixOS `uv` exec issue) | `tox-uv` | v0.9.3 (`TOX-01..04`) — the FHS shims made the workaround unnecessary | `pyproject.toml`'s `dev` extra changed shape, which is exactly why D-04 forbids copying `[0.9.2]`'s "zero dependency change" sentence |
| `ruff` cap `<0.16` | `ruff` cap `<0.17` | Same v0.9.3-era commit that returned `tox-uv` | Same D-04 relevance |
| Hand-rolled `git log $PREV_TAG..$TAG` dump as the GitHub Release body | `scripts/extract_changelog_section.py`'s positional extraction | REL-04, ~v0.7.0/v0.7.1 | Release notes are the curated CHANGELOG, not a commit-message dump |

**Deprecated/outdated:** none specific to this phase's own scope — no library or API this phase
touches has moved since the last release-prep phase (73, 2026-09-16).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The "one commit" file set is best satisfied as the superset {pyproject.toml, uv.lock, README.md, CHANGELOG.md, tests/test_changelog_page_gate.py} — resolving an apparent wording mismatch between 75-CONTEXT.md's "Claude's Discretion" bullet (names 4 files, omitting CHANGELOG.md) and the Phase Boundary/ROADMAP SC1 text (names 4 files, omitting the test file) | Pattern 1, Open Questions | If the owner intended a strict 4-file commit excluding the test file, the plan would need a second small commit for the `RELEASE_VERSIONS` edit — low risk either way since both readings are satisfied by the superset, but worth a one-line confirmation at plan-checker time |
| A2 | The Dependabot branch census (currently 0, per this session's measurement) will not have grown back to a nonzero count by the time Phase 75's plans actually execute | Common Pitfalls #6 | Low risk — the handoff already has a documented fallback (D-15's ordering rule) for a nonzero count; this assumption only affects which branch of that fallback fires |
| A3 | The `### Known Limitations` draft text in Pattern 4 is close enough to D-11's four required elements that the executing plan can adapt it directly rather than re-deriving from scratch | Pattern 4 | Low risk — sourced directly from the NUM-01 todo file, itself already cited as the authoritative source in 75-CONTEXT.md D-11 |

**If this table is empty:** N/A — see rows above. Everything else in this research is either
`[VERIFIED]` (read/executed this session) or `[CITED]` (quoted from a committed source file).

## Open Questions

1. **The exact file set of the "one commit" (see Pattern 1 / Assumption A1).**
   - What we know: ROADMAP SC1 and 75-CONTEXT.md's Phase Boundary bullet both explicitly name
     `pyproject.toml`, `uv.lock`, `README.md` and `CHANGELOG.md` as landing together. 75-CONTEXT.md's
     "Claude's Discretion → The bump mechanics" bullet separately says "all of it lands in one
     commit whose `git show --name-only` lists the four files together" immediately after naming
     `pyproject.toml`, `uv.lock`, `README.md`, and the `RELEASE_VERSIONS` test-file edit — a
     *different* four-item list that omits `CHANGELOG.md`.
   - What's unclear: whether the discretion bullet's "four files" is a drafting slip (intending to
     refer to the same four SC1 names, with the test-file mention being an aside rather than a
     fifth member) or a genuinely narrower scope than SC1's binding text.
   - Recommendation: bundle all five files into one commit (Pattern 1) — this is a strict superset
     that satisfies both readings and creates no conflict with any locked decision. Flag to the
     plan-checker / owner as a one-line confirmation if there is appetite for it, but it should not
     block planning.

2. **`75-HANDOFF.md`'s Dependabot section — what will actually be open at execution time.**
   - What we know: nine stale branches existed at 75-CONTEXT.md's discussion time (2026-09-20);
     zero remote-tracked Dependabot branches exist as of this research session, same calendar day
     (`[VERIFIED: git ls-remote --heads origin, this session]`); zero open PRs of any kind exist
     right now (`[VERIFIED: gh pr list --state open, this session]`).
   - What's unclear: whether this reflects the branches having been pruned/closed, or a
     `git ls-remote` limitation — worth a `gh pr list --state all --limit 20` sanity check inside
     the executing plan if the zero count looks surprising.
   - Recommendation: the executing plan (75-05 / the CI-dispatch or preflight plan) re-measures
     fresh and writes whatever it finds; do not carry either "nine" or "zero" as an assumption into
     `must_haves`.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | Lockfile regen, all `uv run`/`uv sync` invocations | ✓ (`[VERIFIED]`) | 0.12.13 | — |
| `tox` (via `tox-uv`) | `docs-html`, `docs-pdf`, `linkcheck` envs | ✓ (`[VERIFIED]`) | present on PATH via shim | — |
| `ruff` | Lint gate | ✓ (`[VERIFIED]`, via PATH shim only — see Pitfall 2) | pinned `<0.17` in lockfile | `.venv/bin/ruff` does NOT work on this NixOS machine — always invoke bare `ruff` |
| `black`, `mypy` | Format/type gates | ✓ (`[VERIFIED]`, run fine from `.venv/bin/`) | black 26.5.1, mypy 2.3.1 | — |
| `myst-parser` (docs extra) | Changelog-page-gate zero-skip reading | ✓ in main checkout (`[VERIFIED]`); **NOT present in a bare `--extra dev` worktree** (Pitfall 1) | — | `uv sync --extra dev --extra docs` in the executing worktree |
| `gh` CLI | Branch protection reads, CI dispatch, tag/release probes | ✓ (`[VERIFIED]`, authenticated as `YuSabo90002`) | — | — |
| PyPI (network) | 404-probe positive control for `0.9.2`/`0.9.6` | Assumed reachable — not re-probed this research session to conserve rate limit, but is a standing, cheap, unauthenticated `curl` per prior phases' evidence files | — | — |
| `.venv/bin/*` binaries directly (Nix generic-linux ELF) | — | ✗ for `ruff` specifically (`Could not start dynamically linked executable`) | — | PATH shim (see Pitfall 2); black/mypy/pytest run fine from `.venv/bin/` in this same environment |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** the `docs` extra in a freshly-provisioned worktree (fallback:
widen the `uv sync` invocation to `--extra dev --extra docs`); `.venv/bin/ruff` on NixOS (fallback:
PATH shim, already the standing practice per CLAUDE.md).

## Validation Architecture

`workflow.nyquist_validation` is `true` in `.planning/config.json` (`[VERIFIED: .planning/config.json]`, read this session), so this section is required.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (via `tox`'s `uv-venv-lock-runner`), plus `ruff`/`black`/`mypy` as static gates and Sphinx's own `linkcheck`/`html`/`typstpdf` builders as build-time gates |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`, `[tool.ruff]`, `[tool.black]`, `[tool.mypy]`); `tox.ini` (env definitions) |
| Quick run command | `uv run pytest tests/test_changelog_page_gate.py tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v -rs` — the fastest subset that actually exercises this phase's own edits |
| Full suite command | `uv run pytest -q -rs` (expect roughly `1569 passed, 1 skipped` per the milestone audit's own tip measurement — **re-measure fresh, do not transcribe**) |

### Phase Requirements → Validation Map

Neither REL-15 nor REL-16 is code-tested in the conventional sense — REL-15 closes on observed
git/GitHub/PyPI state outside this phase entirely; REL-16 closes on a documentation artifact
(the CHANGELOG section) plus a decision record. The table below maps the phase's actual observable
contract (ROADMAP SC1–SC5) to concrete commands and evidence files.

| SC / D-ID | Observable Behavior | Verification Type | Concrete Command | Evidence File | File Exists? |
|-----------|---------------------|--------------------|-------------------|----------------|--------------|
| SC1 (version bump, one commit) | `pyproject.toml:7` = `0.9.6`; `uv.lock` regenerated; `README.md:348` = `v0.9.6`; `uv sync --extra dev --locked` exits 0; `RELEASE_VERSIONS` gains `"0.9.6"`; changelog-page gate zero-skipped | unit + build | `sed -n 7p pyproject.toml`; `uv sync --extra dev --locked`; `pytest tests/test_readme_version_sync.py tests/test_changelog_page_gate.py -rs` | `75-BUMP-EVIDENCE.md` | ❌ Wave 1 |
| SC2 (curated `## [0.9.6]`, tail link moved) | Six carried bullets byte-identical; two new bullets; tail link block moved; extractor stdout transcribed | unit + build | `git diff` byte-identity checks; `python scripts/extract_changelog_section.py 0.9.6` | `75-CHANGELOG-EVIDENCE.md` | ❌ Wave 1 |
| SC3 (Known Limitations settled) | `### Known Limitations` in `## [0.9.6]` names NUM-01 only; `grep` count = 2 headings total | build + state | `grep -c 'Known Limitations' CHANGELOG.md` (expect 2) | `75-CHANGELOG-EVIDENCE.md` | ❌ Wave 1 |
| SC4 (bumped tree proven green) | pytest ×2, lint/type/format, docs-html/docs-pdf clean + zero doctest/QUA-14 regressions, linkcheck, one CI dispatch, non-committing trial merge | unit + integration + build + remote | see Code Examples | `75-GREEN-TREE-EVIDENCE.md`, `75-CI-EVIDENCE.md`, `75-PREFLIGHT-EVIDENCE.md` | ❌ Wave 2 |
| SC5 (zero irreversible action, fence, handoff) | Tag/PyPI/Release probes empty ×2 observations; SHA-256 fence MATCH ×3 observations; standalone handoff | state | see Pattern 2 / Code Examples | `75-CLOSEOUT-GUARD.md`, `75-HANDOFF.md` | ❌ Wave 1 baseline / Wave 3 close+handoff |

### Sampling Rate
- **Per task commit:** the fast subset (`test_changelog_page_gate.py`, `test_readme_version_sync.py`, `test_preview_version_sync.py`) after every product-tree edit
- **Per wave merge:** the full local green-tree suite (once, after the bump/CHANGELOG wave); the single CI dispatch (once, on the bumped/pushed tip)
- **Phase gate:** SC1–SC5 all MET, transcribed in `75-VERIFICATION.md` before `/gsd-verify-work`

### Wave 0 Gaps
None — every test file this phase needs (`test_changelog_page_gate.py`, `test_preview_version_sync.py`, `test_readme_version_sync.py`, the full suite) already exists and passed at Phase 74's close (milestone audit: `1569 passed, 1 skipped`). This phase adds no new test infrastructure; it edits one existing test file's data tuple (`RELEASE_VERSIONS`).

## Security Domain

`workflow.security_enforcement` is `true`, `security_asvs_level` is `1` (`[VERIFIED: .planning/config.json]`, read this session), so this section is required even though the phase makes no runtime/application change.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | No authentication surface touched; `gh`/git operations use the operator's own already-authenticated credentials |
| V3 Session Management | No | N/A |
| V4 Access Control | No | Branch-protection *reading* is the only access-control-adjacent action, and it is read-only |
| V5 Input Validation | Marginal | The only "input" authored is CHANGELOG prose (human-written); `scripts/extract_changelog_section.py`'s own security note (`[VERIFIED: scripts/extract_changelog_section.py]`, read in full this session) states its `version` argument is used only for string-equality comparison, never interpolated into a shell command or filesystem path |
| V6 Cryptography | Marginal | `sha256sum` is used purely as a change-detection fence (Pattern 2), not for any security boundary |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A checkbox-flip in `.planning/REQUIREMENTS.md` silently committed by automation, misrepresenting publish state | Tampering / Repudiation | The SHA-256 closeout-guard fence (Pattern 2), re-verified 3× (head/close/post-tooling), revert-and-report on divergence, never committed |
| A `gh pr create`/`gh release` command built via `$(...)` command substitution from untrusted content | Injection | This project's own standing memory record confirms the sandbox already refuses this shape; use `--body-file <path>`, never command substitution, for any PR/release body this phase's evidence or the handoff document produces |
| A stale/forged positive control making an "empty" or "zero" claim unfalsifiable | Repudiation | Every empty-diff or zero-count claim this phase makes is paired with a positive control from a real, cited prior measurement (e.g. `v0.9.2`'s 200 response as the PyPI control against `0.9.6`'s expected 404) |
| `release.yml`'s `${{ }}` interpolation-vs-`env:` discipline (unrelated to this phase's edits, but the file this phase's evidence reads) | Injection | Already-present in the committed workflow (`[VERIFIED: .github/workflows/release.yml]`, read in full this session — every `${{ }}` is passed through `env:`, never interpolated directly into a `run:` body); this phase does not edit `release.yml` and should not need to |

This phase introduces no new attack surface (no new dependency, no new endpoint, no new user-input
parser); the security-relevant work is entirely about not misrepresenting project state.

## Recommended Plan Decomposition

Reusing Phase 73's 7-plan/4-wave shape, adapted for this phase's two deltas from every prior
prep-only precedent: (1) the version bump lands in the same commit as the CHANGELOG edit
(Pattern 1), unlike Phase 46's split; (2) a `### Known Limitations` section must be authored from
scratch (Pattern 4), which no prior prep-only phase needed.

| Plan | Wave | `depends_on` | Scope | Evidence file(s) |
|------|------|--------------|-------|-------------------|
| 75-01 | 1 | `[]` | Closeout-guard baseline (SHA-256/`wc -l`/`grep -n 'REL-15'` and `grep -n 'REL-16'` on `.planning/REQUIREMENTS.md` at phase head, each hit classified state-bearing vs. informational, per Pattern 2); `COVERAGE.md` | `75-CLOSEOUT-GUARD.md` (baseline section), `COVERAGE.md` |
| 75-02 | 1 | `[]` | Phase-74 leftovers: delete the five untracked `probe_*.typ` files (D-13, no commit — untracked); file the IN-01 pending todo (D-14) | (no evidence file needed beyond `git status` transcript in `75-CLOSEOUT-GUARD.md` or a small `75-LEFTOVERS-EVIDENCE.md`) |
| 75-03 | 1 | `[]` | **The combined bump+CHANGELOG commit** (Pattern 1): promote six carried bullets + two new Phase-74 bullets into `## [0.9.6]` with lead paragraph, `### Verified` (D-04's corrected wording), new `### Known Limitations` (Pattern 4, NUM-01 only); fresh empty `## [Unreleased]`; move tail link block; bump `pyproject.toml`/`uv.lock`/`README.md`; append `"0.9.6"` to `RELEASE_VERSIONS`; ONE commit; run `scripts/extract_changelog_section.py 0.9.6` and transcribe stdout | `75-CHANGELOG-EVIDENCE.md`, `75-BUMP-EVIDENCE.md` |
| 75-04 | 2 | `["75-03"]` | Green-tree local evidence on the bumped/curated tip: pytest ×2 (default + `LC_ALL=C`); `black`/`mypy`/`ruff`; `@preview` + readme-version-sync family; changelog-page-gate zero-skip reading (needs `--extra docs` — Pitfall 1); docs-html/docs-pdf clean rebuild re-proving Phase 74's zero doctest/QUA-14 counts on the bumped tip; `tox -e linkcheck` fresh run | `75-GREEN-TREE-EVIDENCE.md` |
| 75-05 | 2 | `["75-02", "75-03"]` | Decoy census; push canonical branch; single `gh workflow run CI --ref ...`; observe to completion in the foreground; transcribe every job by name/conclusion, both windows-latest and both macos-latest lanes, `ruff` verdict read from the job's own log | `75-CI-EVIDENCE.md` |
| 75-06 | 2 | `["75-03"]` | Non-committing trial merge (`git merge-tree --write-tree`, idempotency re-check); merged-tree `uv lock --check` + `ruff check .`; `main` protection read (contexts + `strict`); merge-method precedent; Dependabot census (re-measured fresh — see Pitfall 6, likely a different count from either "nine" or "zero" by execution time) | `75-PREFLIGHT-EVIDENCE.md` |
| 75-07 | 3 | `["75-01", "75-02", "75-03", "75-04", "75-05", "75-06"]` | Closeout-guard observation 2 of 2 (repeat every probe from 75-01, separated in time, spanning wave 2's CI dispatch + trial merge); tag/PyPI/GitHub-Release probes (empty, `v0.9.2` positive control); scope-fence check (`typsphinx/` diff still exactly `pathfmt.py` + `translator.py`, unchanged since Phase 74 — nothing under `typsphinx/` touched this phase); write `75-HANDOFF.md` (negative-first opening per Claude's Discretion; PR/checks/tag/pypi-environment/GitHub-Release-body/update-pin.yml/RTD-stable checklist; REL-15's five-observation close criteria; Dependabot ordering note keyed on 75-06's fresh census; D-05's date fact; D-14's filed-todo note) | `75-CLOSEOUT-GUARD.md` (close + note that the third, post-tooling observation happens outside any plan, by the orchestrator), `75-HANDOFF.md` |

**What must change from a literal copy of Phase 73's plans (do not copy verify commands verbatim
without adapting):**
1. **75-03 must bundle the bump AND the CHANGELOG edit into one commit** (Pattern 1) — unlike
   Phase 46's two-plan/two-commit split (46-01 CHANGELOG, 46-02 bump). Do not split this into two
   plans expecting two commits; if the plan-checker or owner resolves Open Question 1 toward a
   strict 4-file reading that excludes `CHANGELOG.md`, this plan's commit boundary needs revisiting
   accordingly — but the superset resolution recommended above needs no such split.
2. **75-03 must author a `### Known Limitations` section from measured content** (Pattern 4) —
   entirely absent from every prior prep-only phase's plan set (46, 69, 71, 73 never needed one).
   Do not treat this as a mechanical promotion like the six carried bullets; it is new prose that
   must independently satisfy D-10/D-11 and the AMENDED block's candidate-set correction.
3. **75-04's docs-build assertions must re-prove Phase 74's TRN-01/QUA-14 zero-counts on the bumped
   tip**, not merely check `multiple toctrees` (that was Phase 73's own delta) — this phase's SC4
   explicitly requires re-proving the prior phase's fix by measurement on the changed tree, since a
   version bump touches `pyproject.toml`, which some doc-building code paths could theoretically
   read (unlikely to matter here, but the re-proof is the point of SC4, not an optional extra).
4. **75-05/75-06's Dependabot census will almost certainly show a count different from both "nine"
   (discussion-time) and "zero" (this research session)** — do not transcribe either number into
   `must_haves`; write whatever `gh pr list`/`git ls-remote` shows at execution time.
5. **75-07's scope-fence positive control is `typsphinx/pathfmt.py` + `typsphinx/translator.py`**
   (Phase 74's own diff, `[VERIFIED: git diff --stat 6cc44f22..HEAD -- typsphinx/, this session]`),
   not Phase 73's "nothing under `typsphinx/`" (Phase 73 had zero product-tree work). Widen the
   positive control accordingly so an empty diff genuinely proves nothing new landed under
   `typsphinx/` during Phase 75 itself, distinct from what Phase 74 already landed.
6. **Every count copied from this RESEARCH.md must be re-measured fresh inside the executing
   plan's own worktree** (ROADMAP constraint 4) — this file's numbers exist to show command shape
   and expected structure, not values to assert without measuring.

## Sources

### Primary (HIGH confidence — read/executed directly, this session)
- `.planning/phases/75-v0-9-6-release-prep-prep-only/75-CONTEXT.md` — full read, all 15 decisions + AMENDED block
- `.planning/REQUIREMENTS.md` — REL-15/REL-16 text, Traceability, Future, Out of Scope (full read + live `grep`/`sha256sum`/`wc -l`)
- `.planning/ROADMAP.md` — Phase 75 section (goal, SC1–5, cross-cutting constraints) and the v0.9.6 milestone section (13 binding constraints), both read in full
- `.planning/STATE.md` — Current Position section, v0.9.5/v0.9.4/v0.9.3 shipped-milestone entries (release-prep precedent pattern)
- `.planning/v0.9.6-MILESTONE-AUDIT.md` — full read (gaps_found status, tech_debt items, independent re-measurement table)
- `CHANGELOG.md` — full read of lines 1–135 (Unreleased, Planned for Future Releases, [0.9.2]), tail block, `### Known Limitations` at `:1205`, `wc -l` (1349 lines)
- `scripts/extract_changelog_section.py` — read in full (positional extraction algorithm, security note)
- `tests/test_changelog_page_gate.py` — `RELEASE_VERSIONS` tuple (ends at `"0.9.2"`), skip conditions, module docstring
- `tests/test_readme_version_sync.py` — read in full
- `.github/workflows/release.yml` — read in full (validate/build/publish-pypi/create-release job order, `${{ }}`-vs-`env:` discipline)
- `.github/workflows/ci.yml` — trigger scope confirmed (`push`/`pull_request` on `main`/`develop` only)
- `tox.ini` — `env_list`, `[testenv:linkcheck]` config
- `pyproject.toml` — version literal (`0.9.2`), `dev`/`docs` extras, ruff cap
- `README.md` — Status line (`v0.9.2`)
- `typsphinx/builder.py` — `RESERVED_IMAGE_NAMESPACE` (`:40`) and `_validate_output_path_collisions()` def (`:1068`), confirming the AMENDED block's closed-defect citations
- `.planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` — read in full
- `.planning/todos/completed/` directory listing — confirmed the two closed-defect todos are present
- `.planning/MILESTONES.md` lines 615–638 — v0.9.0's `### Known limitations shipped` precedent
- `.planning/config.json` — `workflow.nyquist_validation: true`, `security_enforcement: true`, `security_asvs_level: 1`, `use_worktrees: true`
- Live git/gh probes this session: `git status`, `git branch -a`, `git ls-remote --heads/--tags origin`, `git merge-base HEAD origin/main`, `git diff --stat 6cc44f22..HEAD`, `gh auth status`, `gh api .../branches/main/protection`, `gh api repos/...`, `gh pr list --state open`, `uv --version`, `ruff check .`, `.venv/pyvenv.cfg`

### Secondary (MEDIUM confidence — prior-phase artifacts, read this session)
- `.planning/milestones/v0.9.5-phases/73-v0-9-5-close-prep-prep-only-unpublished/73-RESEARCH.md` — full heading structure + Recommended Plan Decomposition section, quoted patterns
- `.planning/milestones/v0.9.5-phases/73-v0-9-5-close-prep-prep-only-unpublished/73-0N-PLAN.md` (all 7) — frontmatter + `must_haves.truths` read for each
- `.planning/milestones/v0.7.1-phases/46-v0-7-1-release-prep-prep-only/46-RESEARCH.md` — heading structure (Pattern 1/2/3 sources)
- `.planning/milestones/v0.7.1-phases/46-v0-7-1-release-prep-prep-only/46-0N-PLAN.md` (all 6) — frontmatter, confirming the two-commit split this phase must diverge from

### Tertiary (LOW confidence — not independently re-verified this session)
- PyPI reachability for the 404/200 positive-control probe (not re-curled this session to conserve
  external-network calls; every prior phase's evidence file confirms this probe works reliably)

## Metadata

**Confidence breakdown:**
- Standard stack / mechanisms: HIGH — every tool and script is already committed and was read/executed this session
- Architecture / plan decomposition: HIGH — directly adapted from four prior prep-only phases' own executed plans, with the two deltas independently verified against this phase's own binding text
- Pitfalls: HIGH — five of seven are directly reproduced or confirmed by live commands this session (docs extra, ruff shim, Dependabot drift); two (locale, incremental rebuild) are carried from this project's own standing memory/CLAUDE.md and not re-triggered this session
- The "one commit" file-set ambiguity: flagged explicitly as an Open Question, not silently resolved

**Research date:** 2026-09-20
**Valid until:** ~7 days (fast-moving — branch/PR/tag/Dependabot state changes daily; re-measure everything at plan execution regardless of this file's age, per ROADMAP constraint 4)
