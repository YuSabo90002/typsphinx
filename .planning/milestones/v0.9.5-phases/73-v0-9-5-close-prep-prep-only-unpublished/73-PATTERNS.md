# Phase 73: v0.9.5 Close Prep (prep-only, unpublished) - Pattern Map

**Mapped:** 2026-09-14
**Files analyzed:** 9 (1 product file + 8 `.planning/` evidence/handoff artifacts)
**Analogs found:** 9 / 9 (all exact-shape analogs, all git-tracked)

This is a release-process phase, not application code. Every "file" is either the single
product-tree file (`CHANGELOG.md`) or a `.planning/` evidence artifact whose exact structural
twin already exists from Phase 71 (v0.9.4's identical close-prep shape) or Phase 69 (the SC#1
fence shape this phase must reuse instead of Phase 71's masked-AST variant). All commands below
were re-copied verbatim from tracked files this session; none were invented.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `CHANGELOG.md` (edited, not created) | config/documentation (Markdown, MyST-included by Sphinx) | CRUD (pure-addition, two new subsections) | `CHANGELOG.md`'s own prior edit at `71-CHANGELOG-EVIDENCE.md` (single-bullet insert into `### Changed`) | role-match (same file type, one hunk vs. two) |
| `73-CLOSEOUT-GUARD.md` | evidence/guard artifact | event-driven (baseline → re-verify → third-observation triad) | `.planning/milestones/v0.9.4-phases/71-.../71-CLOSEOUT-GUARD.md` | exact |
| `73-CHANGELOG-EVIDENCE.md` | evidence artifact | transform (pre/post diff proof) | `.../71-CHANGELOG-EVIDENCE.md` | exact (adjust for 2-hunk shape) |
| `73-PREFLIGHT-EVIDENCE.md` | evidence artifact | batch (non-committing trial merge + lock/lint check) | `.../71-PREFLIGHT-EVIDENCE.md` | exact |
| `73-GREEN-TREE-EVIDENCE.md` | evidence artifact | batch (pytest/lint/type/docs/linkcheck transcript) | `.../71-GREEN-TREE-EVIDENCE.md`, plus `.../72-.../72-LINKCHECK-EVIDENCE.md` for the new `tox -e linkcheck` leg | exact (71) + role-match (72, new leg) |
| `73-CI-EVIDENCE.md` | evidence artifact | event-driven (dispatch → watch → transcribe) | `.../71-CI-EVIDENCE.md`, plus `.../72-.../72-CI-EVIDENCE.md` (most recent transcript shape) | exact |
| `73-SC1-INVARIANTS.md` | evidence artifact | pub-sub (two-observation remote-probe fence with positive controls) | `.planning/milestones/v0.9.3-phases/69-.../69-SC1-INVARIANTS.md` (NOT 71's masked-AST variant — RESEARCH.md D-13 says use 69's lightweight shape since `typsphinx/` is untouched this milestone) | exact |
| `73-HANDOFF.md` | handoff/config artifact (consumed by `/gsd-complete-milestone`) | request-response (ordered step list for a human/tool operator) | `.../71-HANDOFF.md` | exact |
| `COVERAGE.md` | evidence artifact | transform (requirement-to-plan coverage table) | `.../71-.../COVERAGE.md` (sibling in same directory) | exact |

`73-VERIFICATION.md` is explicitly reserved for the verifier — no plan authors it (do not classify/assign it here).

## Pattern Assignments

### `CHANGELOG.md` (config/documentation, CRUD pure-addition)

**Analog:** `CHANGELOG.md` itself, using `71-CHANGELOG-EVIDENCE.md` as the proof-method analog (git-tracked; the CHANGELOG file being edited is its own best structural analog).

**Current structure to insert into** (verified live, `CHANGELOG.md:1-50`):
```markdown
## [Unreleased]

### Changed

- **Contributor tooling returns to `tox-uv` from `tox-uv-bare` (TOX-01, TOX-02, TOX-03, TOX-04).**
  ...
- **Type annotations in typsphinx's source now use builtin generics (QUA-09, QUA-11, QUA-12,
  DOC-22, DOC-23).** ...
  167 projects.

### Planned for Future Releases
- BibTeX/bibliography support
```
Insert `### Added` immediately after `## [Unreleased]` (before `### Changed`), and `### Fixed`
immediately after the last `### Changed` bullet (before `### Planned for Future Releases`) —
per CONTEXT D-01. This is now **two hunks**, not Phase 71's one.

**Bullet register to copy** (from the existing four `### Changed` bullets, e.g. the `tox-uv`
bullet's opening and closing shape):
```markdown
- **Contributor tooling returns to `tox-uv` from `tox-uv-bare` (TOX-01, TOX-02, TOX-03, TOX-04).**
  The `dev` extra and `tox.ini`'s `requires` line once again name `tox-uv`, with `uv.lock`
  regenerated in the same change. This has no effect on installing or using typsphinx. A CI run
  dispatched against the branch carrying this change was green across the Linux, Windows and
  macOS test lanes.
```
Bold lead phrase with a verb (not a bare noun phrase — `71-CHANGELOG-EVIDENCE.md` explicitly
calls out avoiding the `69-REVIEW.md` WR-01 bare-noun-phrase defect) → trailing requirement IDs in
parens → prose → exactly one "This has no effect on installing or using typsphinx." sentence → at
most one evidence sentence.

**Pure-addition proof pattern** (`71-CHANGELOG-EVIDENCE.md` "Pure-addition proof" / "Fence
assertions" sections — reuse verbatim, adapted to 2 hunks per RESEARCH.md Pattern 1):
```bash
git diff --numstat "$BASE_73_01" -- CHANGELOG.md   # expect: N added, 0 removed
git diff -U0 "$BASE_73_01" -- CHANGELOG.md | grep -c '^@@'   # expect: 2 (not 71's 1)
grep -cE '^## \[' CHANGELOG.md                      # unchanged before/after
grep -cE '^\[[^]]+\]: https' CHANGELOG.md            # unchanged before/after
awk '/^### Planned for Future Releases$/{f=1} /^## \[0\.9\.2\]/{exit} f' CHANGELOG.md | sha256sum
tail -n 1 CHANGELOG.md
grep -cF 'compare/v0.9.2...HEAD' CHANGELOG.md
grep -cE '0\.9\.[345]' CHANGELOG.md                   # 0 — no version literal anywhere
# NEW for 73 (two new siblings around ### Changed instead of one bullet appended into it):
awk '/^### Changed$/{f=1} /^### Fixed$/{exit} f' CHANGELOG.md | sha256sum
# compare against the same awk range's pre-edit sha256 — proves the untouched ### Changed block
# is truly untouched even though new subsections now sit on both sides of it
```

**Docs-render pure-addition check** (`71-CHANGELOG-EVIDENCE.md` "Docs baseline"/"Docs render"
sections — reuse verbatim, but this phase's expected `multiple toctrees` count is **zero** at
both base and tip per D-14/RESEARCH.md, not Phase 71's N=N-unrelated-to-toctrees check):
```bash
rm -rf docs/_build
LC_ALL=C uv run tox -e docs-html    # record DOCS_HTML_WARN_BASE
# ... insert bullets ...
rm -rf docs/_build
LC_ALL=C uv run tox -e docs-html    # record DOCS_HTML_WARN_TRACER / _POST, must equal BASE
```

**What must differ from the 71 analog:**
- Two hunks, not one — the new `### Changed`-block-untouched assertion above.
- Insert points are `## [Unreleased]`→before `### Changed` and after-last-`### Changed`-bullet→
  before `### Planned for Future Releases`, not a single append into `### Changed`.
- Bullet subsections are `### Added` and `### Fixed`, each with exactly one bullet — not a fifth
  `### Changed` bullet.
- No "167 projects" or similar hard-coded evidence number carries over; D-03/D-04 forbid a link
  count or page-path enumeration in this phase's bullets (constraint 8).

---

### `73-CLOSEOUT-GUARD.md` (evidence/guard, event-driven baseline→reverify→third-observation)

**Analog:** `.planning/milestones/v0.9.4-phases/71-v0-9-4-close-prep-prep-only-unpublished/71-CLOSEOUT-GUARD.md`

**Baseline section shape** (lines 1-47, reuse verbatim, substituting REL-14 for REL-13 and this
phase's fresh SHAs):
```bash
git rev-parse HEAD                              # -> PHASE_BASE_SHA
sha256sum .planning/REQUIREMENTS.md             # -> REQ_SHA256_BASE
wc -l .planning/REQUIREMENTS.md                 # -> REQ_LINES_BASE
grep -n 'REL-14' .planning/REQUIREMENTS.md       # verbatim, classify state-bearing vs informational
date -u +"%Y-%m-%dT%H:%M:%SZ"                   # -> GUARD_AT
```
Key-line block to reproduce:
```
PHASE_BASE_SHA = <fresh>
REQ_SHA256_BASE = <fresh>
REQ_LINES_BASE = <fresh>
REL14_HITS_BASE = <fresh>
GUARD_AT = <fresh>
```

**Classification pattern** (lines 83-95): split grep hits into "state-bearing" (the requirement's
own checkbox line + its Traceability-row line) vs. "informational" (any prose tail or coverage-
count line mentioning the ID without a checkbox/Pending token of its own).

**Why-SHA256-not-wc-l rationale paragraph** (lines 96-105) — reuse verbatim; cites this project's
own Phase 63 flip-of-three-requirements precedent.

**Re-verification protocol** (lines 125-143, phase close) and **"For the operator running
phase.complete"** section (lines 145-189, both entry points: `phase.complete` from
`/gsd-execute-phase` and `/gsd-verify-work`'s inline transition) — reuse verbatim structure,
including the backup-three-files-to-scratch instruction and the "reverted and reported, never
committed" rule.

**Third observation** section (lines 293-331) — the orchestrator, outside any plan, records this
after `phase.complete` actually runs; reuse the `OBS3_AT` / `REQ_SHA256_OBS3` / `REQ_VERDICT_OBS3`
key-line vocabulary and the note about `phase.complete` also touching STATE.md's
`current_phase_name` / `Plan: Not started` and ROADMAP.md's Status-cell padding — hand-correct
those, do not treat them as the REL-14 guard's own failure.

**What must differ:** requirement ID is `REL-14` (not `REL-13`); the guarded prose is REL-14's own
verbatim text from `.planning/REQUIREMENTS.md` (must be freshly grepped, not assumed identical to
REL-13's wording); the AMENDED-commit ancestor check should re-target REL-14's own AMENDED block if
one exists at Phase 73's head — confirm fresh rather than assuming Phase 71's shape.

---

### `73-CHANGELOG-EVIDENCE.md` (evidence, transform: pre/post diff proof)

**Analog:** `.../71-CHANGELOG-EVIDENCE.md` (full structure reused, see excerpt inline in the
`CHANGELOG.md` section above for the diff/fence commands). Additional structural sections to copy:

**Head check and provisioning** (lines 1-52):
```bash
date -u +%FT%TZ
pwd -P
test -f .git; echo "exit:$?"
command -v uv
grep -c typsphinx-fhs-run "$(command -v uv)"
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
uv --version
```
(Pin `--python 3.13.13` explicitly — RESEARCH.md Pitfall 2.)

**"What this file is NOT" section** (lines 91-99) — reuse verbatim reasoning: no
`scripts/extract_changelog_section.py` run (no versioned heading exists yet), no `### Verified`
subsection, no lead paragraph under `## [Unreleased]`.

**Discretion-exercised section** (lines 430-440) — document the chosen lead-sentence wording and
why the evidence sentence was chosen, mirroring this project's own review-defect-avoidance habit
(WR-01 bare-noun-phrase).

**What must differ:** two bullets/two hunks instead of one; the accuracy-basis table cites Phase
72's evidence files (`72-TOCTREE-EVIDENCE.md`, `72-LINKCHECK-EVIDENCE.md`) instead of Phase 70's;
no `167`-style hard-coded corpus count — D-03 forbids any link count in the linkcheck bullet.

---

### `73-PREFLIGHT-EVIDENCE.md` (evidence, batch: non-committing trial merge)

**Analog:** `.../71-PREFLIGHT-EVIDENCE.md`

**Header discipline** (lines 1-4) — reuse verbatim: "Nothing in this file is committed... no value
is copied from CONTEXT.md or RESEARCH.md."

**Head check + provisioning block** (lines 6-34) — same shape as above (`73-CHANGELOG-EVIDENCE.md`
excerpt), plus recording `BASE_73_05` / `TRIAL_HEAD` / `START_CANONICAL` from
`git rev-parse HEAD` and `git rev-parse gsd/v0.9.5-docs-link-check-and-navigation` before any
commit.

**Trial-merge command sequence** (RESEARCH.md Pattern 2, sourced from `71-PREFLIGHT-EVIDENCE.md`):
```bash
git fetch origin
git merge-tree --write-tree HEAD origin/main; echo "exit:$?"
git merge-base --is-ancestor origin/main HEAD; echo "exit:$?"
mkdir -p "$SCRATCH/lock_scratch"
git archive --format=tar -o "$SCRATCH/lock.tar" "$MERGE_TREE" pyproject.toml uv.lock
tar -xf "$SCRATCH/lock.tar" -C "$SCRATCH/lock_scratch"
uv --directory "$SCRATCH/lock_scratch" lock --check; echo "exit:$?"
git archive --format=tar -o "$SCRATCH/lint.tar" "$MERGE_TREE"
tar -xf "$SCRATCH/lint.tar" -C "$SCRATCH/lint_scratch"
uv --directory "$SCRATCH/lint_scratch" sync --locked --extra dev --no-install-project
uv --directory "$SCRATCH/lint_scratch" run --no-sync ruff check .; echo "exit:$?"
```

**Branch-protection read** (RESEARCH.md "Code Examples"):
```bash
gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq .strict
gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq '[.contexts[]] | sort | join("|")'
```
Must equal the six contexts recorded in `72-BASE-EVIDENCE.md`'s `REQUIRED_CONTEXTS_HEAD`, with
`strict: true` (D-09).

**Dependabot census** (new to Phase 73 vs. Phase 71's empty census — RESEARCH.md "Code Examples",
D-06/D-12 shape):
```bash
gh pr list --state open --json number,title,author,headRefName,baseRefName,updatedAt
```
Record all five PRs (#146-#150) by number/package/version-range — unlike 71's empty census, this
one is non-empty and must be transcribed in full, then repeated in `73-HANDOFF.md`.

**Merge-method precedent** section (mirrors `71-PREFLIGHT-EVIDENCE.md` § "Merge-method
precedent"): confirm `#143`-style `Merge pull request` commits, never squash/rebase, on `main`'s
first-parent history.

**What must differ:** the Dependabot census is non-empty (five rows, not zero) and must be
transcribed fully rather than recorded as "none open."

---

### `73-GREEN-TREE-EVIDENCE.md` (evidence, batch: pytest/lint/type/docs/linkcheck transcript)

**Analogs:** `.../71-GREEN-TREE-EVIDENCE.md` for the pytest/lint/type/docs-html/docs-pdf/changelog-
gate structure; `.planning/phases/72-.../72-LINKCHECK-EVIDENCE.md` for the new `tox -e linkcheck`
leg this phase must add (RESEARCH.md Pattern 4, D-14):
```bash
rm -rf docs/_build/linkcheck
uv run tox -e linkcheck > "$SCRATCH/lc_run1.log" 2>&1; echo "exit:$?"
python3 -c "
import json
rows = [json.loads(l) for l in open('docs/_build/linkcheck/output.json') if l.strip()]
total = len(rows)
working = sum(1 for r in rows if r.get('status') == 'working')
print(f'total={total} working={working}')
for r in rows:
    if r.get('status') != 'working':
        print(r)
"
```
Failure classification (D-01..D-03, from `72-LINKCHECK-EVIDENCE.md`/`72-GATES-EVIDENCE.md`):
transient row → re-run from a clean output dir, at most 3 runs total; recurring same-URL → add a
timed `conf.py` key with a measured-failure comment; anything else non-transient → stop, escalate
to the owner (do not silently retry-and-ignore).

**Docs-warning baseline positive control** (D-14): expect `multiple toctrees` count = 0 at both
base and tip this phase; cite Phase 72's own pre-fix `BASE_MULTI_TOCTREE_COUNT = 5` as the positive
control proving the `LC_ALL=C` grep genuinely detects the message when present, rather than
re-measuring a positive control locally.

**Changelog-gate zero-skip provisioning** (Pitfall 1): `--extra dev --extra docs --python
3.13.13`, not a bare `--extra dev`.

**What must differ:** adds the `tox -e linkcheck` leg entirely (didn't exist at Phase 71); the
`multiple toctrees` expectation flips from N (open defect) to 0 (fixed in Phase 72).

---

### `73-CI-EVIDENCE.md` (evidence, event-driven: dispatch→watch→transcribe)

**Analogs:** `.../71-CI-EVIDENCE.md` for the overall shape; `.planning/phases/72-.../72-CI-EVIDENCE.md`
for the most recent live transcript idiom (RESEARCH.md "Code Examples"):

**Decoy census + safe push** (verbatim reusable, from `72-CI-EVIDENCE.md`):
```bash
git branch --list 'gsd/v0.9.5*' -v
git ls-remote --heads origin 'gsd/v0.9.5*'
# fast-forward canonical ref to any decoy carrying commits FIRST, re-point HEAD, THEN delete decoy
git push --no-follow-tags -u origin gsd/v0.9.5-docs-link-check-and-navigation
gh workflow run CI --ref gsd/v0.9.5-docs-link-check-and-navigation
```

**Watch-to-completion + full job transcript** (from `72-CI-EVIDENCE.md`):
```bash
timeout 590 gh run watch <RUN_ID> --interval 30
gh run view <RUN_ID> --json status,conclusion,workflowName,headSha,url,createdAt,updatedAt
gh run view <RUN_ID> --json jobs --jq '.jobs[] | [.name, .conclusion] | @tsv'
```
D-12 transcription requirement: name both `windows-latest` and both `macos-latest` lanes
explicitly, and read `ruff`'s verdict from the `Lint and Format Check` job's own log text, not
just its conclusion.

**5xx-before-retry guard** (Pitfall 5, from `71-HANDOFF.md`'s own `DISPATCH_COUNT` note): before
retrying a failed `gh workflow run`, run
`gh run list --workflow=ci.yml --branch <branch> --event workflow_dispatch --limit 5 --json databaseId,headSha,status,createdAt`
and look for a row at the just-pushed SHA.

**What must differ:** none structurally; this is the most mechanically identical of all the
evidence files — only the branch name, SHAs and run ID are fresh.

---

### `73-SC1-INVARIANTS.md` (evidence, pub-sub: two-observation remote-probe fence)

**Analog:** `.planning/milestones/v0.9.3-phases/69-v0-9-3-close-prep-prep-only-unpublished/69-SC1-INVARIANTS.md`
— **use this one, not `71-SC1-INVARIANTS.md`** (RESEARCH.md D-13: no masked-AST harness is needed
because `git diff --stat 098a8ff6..HEAD -- typsphinx/ .github/workflows/` is empty for the whole
milestone; Phase 71 needed the heavier masked-AST proof only because Phase 70 rewrote type
annotations under `typsphinx/`).

**Two-observation framing** (lines 1-11): "Observation 1 of 2" recorded early (before wave 2/CI),
"Observation 2 of 2" recorded by a later plan after CI dispatch — reuse this split verbatim.

**Version-line probe:**
```bash
sed -n 7p pyproject.toml   # -> VERSION_LINE, expect: version = "0.9.2"
```

**Local tag probe with positive control:**
```bash
git tag -l 'v0.9*'          # positive control: v0.9.0, v0.9.2 present
git tag -l 'v0.9.5'          # expect: no output -> LOCAL_V095_TAGS = 0
```

**Remote tag probe (unfiltered, avoiding the silent-filter trap):**
```bash
git ls-remote --tags origin   # fetch once, unfiltered; derive both the positive control
                               # (v0.9.0/v0.9.2 present) and the negative count (v0.9.3/.4/.5 absent)
                               # from this single fetch, never a filtered ls-remote alone
```
(The unfiltered-fetch-then-derive-two-counts idiom is the key reusable trick — a bare
`git ls-remote --tags origin 'v0.9.5'` returning nothing is indistinguishable from a network
failure.)

**What to add for this phase's SC#1** (D-13, not present in 69's original since it predates the
milestone-wide-diff framing but matches its lightweight spirit):
```bash
git diff --stat 098a8ff6..HEAD -- typsphinx/ .github/workflows/   # expect: empty
# widened-diff positive control proving the scoped diff isn't silently empty due to a bad path:
git diff --stat 098a8ff6..HEAD -- .   # non-empty (the 5-file, +11/-5 CLAUDE.md/README.md/etc diff)
```
Plus PyPI-404 and GitHub-Release-absence probes for all three unclaimed version numbers
(`0.9.3`, `0.9.4`, `0.9.5`), each with `0.9.2`'s existing (200/Release-present) row as the positive
control — same idiom as the tag probes.

**What must differ from 69:** the unclaimed-version set is three numbers (`0.9.3`/`0.9.4`/`0.9.5`),
not 69's single `v0.9.3`; add the milestone-wide `typsphinx/`+`.github/workflows/` scoped-diff
assertion (D-13), which 69 (a milestone with actual code changes to fence) didn't need in this
exact form.

---

### `73-HANDOFF.md` (handoff, request-response: ordered operator steps)

**Analog:** `.../71-HANDOFF.md`

**Negative-first opening paragraph** (lines 1-7) — reuse verbatim structure: "This milestone
publishes nothing... not applicable... Recorded as a fact, not a step: the daily `update-pin.yml`
schedule...".

**Ordered step list** (lines 9-40+): fence-first backup → re-run trial merge (cite fresh
`MERGE_TREE`/`MAIN_MOVED`/`LOCK_CHECK_EXIT`/`MERGED_RUFF_LOCK_VERSION`/`TRIAL_MERGE_VERDICT`) →
conditional branch update (merge commit only, never rebase, only if `origin/main` moved) → push →
open PR (`gh pr create --base main --head <branch> --title <English> --body-file <file>`, body via
file not command substitution — memory: sandbox-refuses-command-substitution-in-gh-comment) → wait
for the six named required checks → merge (`gh pr merge <number> --merge`, cite merge-method
precedent `#143`/`#145`-style) → REL-14's five post-merge observations.

**Post-merge REL-14 observation list** (mirrors 71's REL-13 § 7, substitute REL-14 and drop the
per-requirement description text for D-10's own five bullets):
```bash
git log --first-parent -1 --format='%h %s' origin/main
git show origin/main:pyproject.toml | sed -n 7p     # expect: version = "0.9.2"
git ls-remote --tags origin                          # no v0.9.3/.4/.5 tag
# PyPI 404 for 0.9.5 (and 0.9.3/0.9.4), 200 for 0.9.2 (positive control)
gh release list                                      # no v0.9.5 (or .3/.4) Release
```

**Dependabot ordering note** (D-06, adapting 71's empty-census note into a populated one): list
all five PRs by number/package/version-range, state milestone-PR-first-then-Dependabot-second
ordering, per v0.9.3 precedent (#143 then #142/#141).

**What must differ:** REL-13 → REL-14; the Dependabot section is populated (five real PRs to
name) rather than 71's "none open" note; cite this phase's own fresh `73-PREFLIGHT-EVIDENCE.md` /
`73-CI-EVIDENCE.md` key-line values, not 71's.

---

### `COVERAGE.md` (evidence, transform: requirement-to-plan coverage table)

**Analog:** `.planning/milestones/v0.9.4-phases/71-v0-9-4-close-prep-prep-only-unpublished/COVERAGE.md`
(sibling file in the same phase directory — same generation mechanism the planner/executor already
runs for every phase; no bespoke content beyond mapping REL-14 to Phase 73's plans, all under
`requirements-completed: []` per D-08).

## Shared Patterns

### `KEY = value` bare-line evidence vocabulary
**Source:** every 71/72/69 evidence file cited above.
**Apply to:** all 8 evidence/handoff files in this phase.
```
PHASE_BASE_SHA = <sha>
REQ_SHA256_BASE = <sha256>
DOCS_HTML_WARN_BASE = <int>
TRIAL_MERGE_VERDICT = MET|NOT-MET
```
Every measured value that a later plan or the verifier needs to compare against is written as a
bare `KEY = value` line immediately after the command block that produced it — never only prose.

### Fresh-worktree provisioning line
**Source:** `71-CHANGELOG-EVIDENCE.md` / `71-PREFLIGHT-EVIDENCE.md` head-check blocks; CLAUDE.md
§ "Worktree-isolated execution".
**Apply to:** every plan in this phase.
```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
uv run pytest   # run ALL subsequent commands via `uv run`
```
Always both extras (`dev` + `docs`) and an explicit `--python 3.13.13` pin (Pitfalls 1 and 2).

### Clean-build-under-`LC_ALL=C` discipline
**Source:** `71-CHANGELOG-EVIDENCE.md` docs-baseline sections; CLAUDE.md § Locale.
**Apply to:** every docs-html/docs-pdf/linkcheck build whose warning or link count is compared.
```bash
rm -rf docs/_build
LC_ALL=C uv run tox -e docs-html
```
Never an incremental rebuild for a counted comparison; never a locale-unqualified grep against
Sphinx output.

### Non-hard-coded measurement discipline (constraint 8)
**Source:** RESEARCH.md "Anti-Patterns to Avoid"; applies project-wide to this phase.
**Apply to:** every evidence file and the CHANGELOG bullets themselves.
Every count (link `working` total, `multiple toctrees` count, warning count, required-context set,
Dependabot PR list) must be measured fresh inside the plan's own run — RESEARCH.md's and this
PATTERNS.md's numbers (e.g. "95 links," "5 pre-fix toctree messages," "six required contexts") are
context only, never values a plan asserts without re-measuring.

## No Analog Found

None. Every file this phase touches or authors has a git-tracked, structurally exact analog from
Phase 69 or Phase 71/72.

## Metadata

**Analog search scope:** `.planning/milestones/v0.9.3-phases/69-.../`,
`.planning/milestones/v0.9.4-phases/71-.../`, `.planning/phases/72-.../`, and the repository root
`CHANGELOG.md`.
**Files scanned:** `CHANGELOG.md`; `71-CLOSEOUT-GUARD.md`; `71-CHANGELOG-EVIDENCE.md`;
`71-PREFLIGHT-EVIDENCE.md`; `71-HANDOFF.md`; `69-SC1-INVARIANTS.md`; `72-CI-EVIDENCE.md`;
`72-LINKCHECK-EVIDENCE.md` (all confirmed `git ls-files`-tracked before citing).
**Pattern extraction date:** 2026-09-14
