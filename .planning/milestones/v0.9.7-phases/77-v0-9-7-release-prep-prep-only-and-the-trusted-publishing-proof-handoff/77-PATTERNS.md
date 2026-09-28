# Phase 77: v0.9.7 Release Prep - Pattern Map

**Mapped:** 2026-09-28
**Files analyzed:** 12 (all new; this is a docs/evidence-only phase, no `typsphinx/` or
`.github/workflows/` files are created or modified)
**Analogs found:** 12 / 12

This phase's entire output is `.planning/` prose/evidence files plus a five-file version-bump
commit (`pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md`,
`tests/test_changelog_page_gate.py`). Every analog below is git-tracked; verified via
`git ls-files` before being named (both `.planning/milestones/v0.9.6-phases/75-v0-9-6-release-prep-prep-only/*`
and `.planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/*` returned
non-empty, i.e. tracked source, not a gitignored mirror).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `77-BUMP-EVIDENCE.md` | evidence/transcript | batch (one commit, recorded verbatim) | `75-BUMP-EVIDENCE.md` | exact |
| `77-CHANGELOG-EVIDENCE.md` | evidence/transcript | transform (extractor stdout vs. committed section, digest compare) | `75-CHANGELOG-EVIDENCE.md` | exact |
| `77-GREEN-TREE-EVIDENCE.md` | evidence/transcript | batch (pytest/lint/docs/linkcheck readings) | `75-GREEN-TREE-EVIDENCE.md` | exact |
| `77-CI-EVIDENCE.md` | evidence/transcript | event-driven (CI dispatch + job polling) | `75-CI-EVIDENCE.md` | exact |
| `77-PREFLIGHT-EVIDENCE.md` | evidence/transcript | batch (trial-merge, branch-protection read, open-PR census) | `75-PREFLIGHT-EVIDENCE.md` | exact |
| `77-ATT06-EVIDENCE.md` | evidence/transcript | probe (tag-absence, 2 observations) | new shape — closest structural analog is `76-ATT-EVIDENCE.md`'s "measured, not trusted" probe format | role-match |
| `77-CLOSEOUT-GUARD.md` | config/fence (line-scoped guard) | probe (sha256 + wc -l + grep, 3 observations) | `75-CLOSEOUT-GUARD.md` | exact |
| `77-HANDOFF.md` | handoff/runbook | request-response (pre-written commands + expected outputs) | `75-HANDOFF.md` | exact |
| `CHANGELOG.md` `## [0.9.7]` section | content/config | CRUD (append one released section) | `CHANGELOG.md` `## [0.9.6]` section (lines 16-108, per RESEARCH) | exact |
| `pyproject.toml` version bump | config | CRUD (single literal edit) | Phase 75's bump of the same line (see `75-BUMP-EVIDENCE.md` "Before"/"After") | exact |
| `README.md` Status line bump | config | CRUD (single literal edit) | Phase 75's bump of `README.md:348`-equivalent line | exact |
| `tests/test_changelog_page_gate.py` `RELEASE_VERSIONS` edit | test/config | CRUD (tuple append + comment edit) | Phase 75's edit of the same tuple (0.9.5→0.9.6 add) | exact |

## Pattern Assignments

### `77-BUMP-EVIDENCE.md` (evidence, batch)

**Analog:** `.planning/milestones/v0.9.6-phases/75-v0-9-6-release-prep-prep-only/75-BUMP-EVIDENCE.md`

**Header/provisioning pattern** (lines 1-24):
```
# Phase 75 — Bump Evidence (SC1)

## Head check and provisioning

$ date -u +%FT%TZ
2026-09-20T08:38:21Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a64ee11a04ac3c9ef

$ test -f .git; echo "exit:$?"
exit:0

$ grep -q typsphinx-fhs-run "$(command -v uv)" && echo "shim_check:ok"
shim_check:ok

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
...
exit:0
```
Copy this exact worktree-detection + provisioning preamble (`date`, `pwd -P`, `test -f .git`,
shim grep, `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs`) into
every `77-*-EVIDENCE.md` file that runs its own commands — it is the CLAUDE.md worktree-isolation
recipe, restated verbatim in every Phase 75 evidence file.

**BASE_/SCRATCH_ variable naming convention:** `BASE_75_03 = <sha>`, `SCRATCH_75_03 = <tmp dir>` —
carry the same `BASE_77_0N` / `SCRATCH_77_0N` naming per plan number for cross-referencing in
later evidence files and in `77-HANDOFF.md`.

**Commit-shape assertion pattern** (used in `75-HANDOFF.md`'s SC1 row): the bump commit's
`git show --name-only HEAD` output is captured as a single `|`-joined variable, e.g.
`BUMP_COMMIT_FILES = CHANGELOG.md|README.md|pyproject.toml|tests/test_changelog_page_gate.py|uv.lock`.
Reuse this exact five-file set (same files, `0.9.6`→`0.9.7`), and reuse the `uv lock --check` +
`CHANGELOG_GATE_SKIPS = 0` verification pair.

---

### `77-CHANGELOG-EVIDENCE.md` (evidence, transform)

**Analog:** `75-CHANGELOG-EVIDENCE.md`

**Core pattern** (from `75-HANDOFF.md`'s SC2 row, restated): run
`scripts/extract_changelog_section.py 0.9.7`, capture stdout byte count and a digest
(`sha256sum`), and assert it is byte-identical to the committed `## [0.9.7]` section via matching
digests, e.g. `EXTRACT_MATCHES_SECTION = yes`. Copy the exact two-digest-comparison shape from
`75-CHANGELOG-EVIDENCE.md` (transcript of extractor stdout + `sha256sum` of both sources +
explicit equality statement).

---

### `77-GREEN-TREE-EVIDENCE.md` (evidence, batch)

**Analog:** `75-GREEN-TREE-EVIDENCE.md`

**Core pattern:** local pytest×2 (plain locale + `LC_ALL=C`), lint trio (`ruff check .`,
`black --check .`, `mypy typsphinx/`), `rm -rf docs/_build` before each of `docs-html`/`docs-pdf`,
and `tox -e linkcheck` with a classified-exceptions table if any link fails. **Known deviation to
carry forward:** Phase 75's SC4 needed an owner AMENDED reading for 2 "Class A" changelog-compare
links that are structurally unreachable before the tag exists, plus 1 "Class B" PyPI
bot-interstitial false-positive — expect the identical two Class-A links
(`.../compare/v0.9.6...v0.9.7` style, now for 0.9.7) to reappear and pre-empt them with the same
classification language rather than treating them as new failures.

---

### `77-CI-EVIDENCE.md` (evidence, event-driven)

**Analog:** `75-CI-EVIDENCE.md`

**Core pattern** (from `75-HANDOFF.md`'s SC4 CI half): record `RUN_ID`, `PUSHED_SHA`,
`JOB_COUNT`, `NON_SUCCESS_JOBS` for exactly one CI dispatch on the bumped, pushed tip; if a
dispatch 5xx's, run `gh run list` before any retry (never blind-retry) and record both run ids if
a second dispatch was needed, same as Phase 75's superseded-by-WR-01-fix note. Must name both
Windows and macOS lanes explicitly in the job table per ROADMAP SC#3, even though they are not in
`main`'s required-contexts list (measured this session — see RESEARCH § Verified Facts).

---

### `77-PREFLIGHT-EVIDENCE.md` (evidence, batch)

**Analog:** `75-PREFLIGHT-EVIDENCE.md`

**Core pattern:** `git merge-tree --write-tree` (non-committing trial merge of `origin/main`),
`uv lock --check` and `ruff check .` on the merged tree, `gh api .../branches/main/protection`
read, and an open-PR census via `gh pr list --state open`. This phase's `origin/main` has
genuinely moved (3 Dependabot PRs merged since milestone base, 1 open — #157) so this is not a
formality; capture `git merge-base HEAD origin/main` vs `git rev-parse origin/main` explicitly as
Phase 75 did.

---

### `77-ATT06-EVIDENCE.md` (evidence, probe — new file, no direct precedent)

**Structural analog:** `76-ATT-EVIDENCE.md`'s "measured, not trusted" probe idiom (re-derive every
line number/grep target live rather than copying from ROADMAP/REQUIREMENTS):
```
Command: `grep -nF 'secrets.PYPI_API_TOKEN' .github/workflows/release.yml`
...
ATT01_BASE_SHA = e3c169d4e7b52d828f6ebe2b04e55513df49ddfc
Taken from `git rev-parse HEAD` before any edit in this plan.
```

**Core content for `77-ATT06-EVIDENCE.md`** (per CONTEXT D-04): the SHA of the commit that adds
the rollback section inside `77-HANDOFF.md`, plus two empty-tag observations each with a positive
control:
```bash
git tag -l 'v0.9.7'                              # expect: empty
git ls-remote --tags origin 'refs/tags/v0.9.7*'  # expect: empty
git tag -l 'v0.9.6'                              # positive control: v0.9.6
git ls-remote --tags origin 'refs/tags/v0.9.6*'  # positive control: refs/tags/v0.9.6 + ^{}
```
This exact control pattern (empty target + non-empty control on the immediately-prior release tag)
is already measured in RESEARCH § Verified Facts — reuse those readings as the "before" baseline
and re-measure fresh at the commit that lands the rollback section.

---

### `77-CLOSEOUT-GUARD.md` (config/fence, probe)

**Analog:** `75-CLOSEOUT-GUARD.md`

**Header/provisioning pattern** (lines 1-24): identical worktree-detection preamble as
`75-BUMP-EVIDENCE.md` above, plus the file's own framing sentence:
```
# Phase 75 — Closeout Guard (REL-15 fence)

This file changes no requirement state: REL-15 stays an unchecked box (`- [ ]`) and its
Traceability row stays `Pending`. `.planning/REQUIREMENTS.md` is read and quoted here, never
edited — no plan in Phase 75 writes it.
```
Copy this framing verbatim, substituting REL-15 → the five coverage-only IDs of this phase
(ATT-03, ATT-04, ATT-05, REL-17, DOC-25).

**Fence probe set** (from RESEARCH § Pattern 2, itself copied from `75-CLOSEOUT-GUARD.md`):
```bash
sha256sum .planning/REQUIREMENTS.md      # compare against phase-head digest
wc -l .planning/REQUIREMENTS.md          # compare against phase-head line count
git diff --name-only -- .planning/REQUIREMENTS.md   # expect empty until phase-completion tooling
grep -n 'ATT-03\|ATT-04\|ATT-05\|REL-17\|DOC-25' .planning/REQUIREMENTS.md
```
Reuse the exact three-observation protocol (phase head, phase close, and a third observation
**after** `phase.complete`-family tooling has run) — Phase 75's file documents this is the
observation that actually catches the auto-flip hazard (9 of 10 prior closes). The ATT-06 lines
are expected to move (legitimate, not reverted); the five listed above must MATCH across all
three observations or be reverted via `git checkout -- .planning/REQUIREMENTS.md`.

---

### `77-HANDOFF.md` (handoff/runbook, request-response)

**Analog:** `75-HANDOFF.md`

**Opening framing pattern** (lines 1-4):
```
# Phase 75 — Handoff to /gsd-complete-milestone

This document is standalone: every number it cites is written into it, not linked. A reader with
only this file can execute the whole release, in order.
```
Copy verbatim (renumber to Phase 77). This is the literal text ROADMAP SC#4 ("readable without the
roadmap or any phase file") is checked against.

**"What this phase satisfied" section pattern** (lines 6-29): quotes the closing requirement
(here ATT-06, there REL-15) verbatim from REQUIREMENTS.md in a blockquote, states which
`77-0N-SUMMARY.md` files declare `requirements-completed: []`, and cross-references the
CLOSEOUT-GUARD digest by name. For Phase 77, additionally note (per CONTEXT D-04) that ATT-03,
ATT-04, ATT-05, DOC-25, REL-17's publish clauses are the coverage-only reqs — same shape as
Phase 75's REL-15/REL-16 split, but with five coverage-only reqs instead of one.

**Success-criteria table pattern** (the `| SC | Verdict | Evidence |` table): one row per SC,
each Evidence cell naming the exact evidence file and inline variable (e.g.
`BUMP_COMMIT_FILES = ...`, `EXTRACT_MATCHES_SECTION = yes`). Reuse this table shape 1:1 for
Phase 77's SC1-SC5.

**Rollback-section pattern (new to this phase, per CONTEXT D-04):** does not exist in `75-HANDOFF.md`
verbatim (Phase 75 had no comparable multi-branch rollback) — construct fresh from CONTEXT's
①–③ failure-shape table and D-01/D-02/D-03, but follow `75-HANDOFF.md`'s per-step
"on failure here → § <section>" pointer convention structurally, and its command-block style
(fenced bash/yaml with inline `# Expected:` comments) as shown in RESEARCH § Code Examples'
ATT-03(a)/(b) skeleton.

**Publish-half step-ordering pattern:** `75-HANDOFF.md`'s numbered checklist (merge → tag push →
publish → verify → close) is the direct precedent for Phase 77's own ordered sequence: merge → tag
push → `pypi` environment approval → ATT-04 (log grep) → ATT-03(a)/(b) (PyPI proof) → ATT-05
(secret retirement) → DOC-25 (doc correction) → translations `update-pin.yml` → RTD `en`/`ja`
re-measure. Each step must carry the rollback pointer per D-04.

---

### `CHANGELOG.md` `## [0.9.7]` section (content, CRUD)

**Analog:** `CHANGELOG.md`'s own `## [0.9.6]` section (measured at `CHANGELOG.md:16-108` per
RESEARCH; re-measure line numbers at execution since the file grows).

**Section skeleton** (RESEARCH § Code Examples, reproduced here as the pattern to copy structurally,
with wording per CONTEXT Discretion B/C — do not copy `[0.9.6]`'s "should upgrade" register or its
`v0.9.2..HEAD` dependency sentence, both explicitly called out as non-reusable):
```markdown
## [0.9.7] - <prep authoring date, fixed>

<short, modest lead paragraph>

### Changed

- **0.9.7 is published through PyPI Trusted Publishing (ATT-01, ATT-02).** ...audit provenance,
  not an install-time gate...

### Fixed

- **<MSG-06 bullet>**

### Known Limitations

- **<NUM-01 bullet, carried from [0.9.6]>**

### Verified

- No new runtime dependency and no new dev dependency were added across `v0.9.6..HEAD` (measured
  fresh, not copied from [0.9.6]).
- The four `@preview` package version strings are unchanged across all three declaration sites.
- <MSG-06's recorded-RED gate, `tests/test_translator_path_quoting_gate.py`>
```
This yields **three** `### Known Limitations` headings total after this phase
(`[0.1.0b1]`, `[0.9.6]`, `[0.9.7]`) — any grep-based SC check must expect 3, not 2.

**Tail-link pattern:** move `[Unreleased]` compare target from `v0.9.6` to `v0.9.7`, insert a new
`[0.9.7]: .../releases/tag/v0.9.7` line above the existing `[0.9.6]` line — identical mechanics to
Phase 75's own tail-link edit for `[0.9.6]`.

---

### `pyproject.toml`, `README.md`, `tests/test_changelog_page_gate.py` bump edits (config, CRUD)

**Analog:** Phase 75's identical single-literal edits, captured in `75-BUMP-EVIDENCE.md`'s
"Before"/"After" sections and RESEARCH § Code Examples' bump-commit skeleton:
```bash
sed -i 's/^version = "0.9.6"$/version = "0.9.7"/' pyproject.toml
uv lock                      # regenerates uv.lock's typsphinx stanza — never hand-edit uv.lock
sed -i 's/\*\*Status\*\*: Stable (v0.9.6)/\*\*Status\*\*: Stable (v0.9.7)/' README.md
# CHANGELOG.md edited by hand (curation, not scriptable)
# tests/test_changelog_page_gate.py's RELEASE_VERSIONS tuple + comment edited by hand
git add pyproject.toml uv.lock README.md CHANGELOG.md tests/test_changelog_page_gate.py
git commit -m "chore(release): bump version to 0.9.7"
git show --name-only HEAD   # must list exactly these five files together
uv sync --extra dev --locked   # must exit 0
```
`RELEASE_VERSIONS` edit: append `"0.9.7"` to the 17-tuple (measured at `tests/test_changelog_page_gate.py:44-62`,
currently `"0.4.1"`..`"0.9.6"`), and update the comment "The 17 releases..." → "The 18 releases...
(0.4.1 through 0.9.7, inclusive)" — same mechanical pattern as Phase 75's 16→17 edit.

## Shared Patterns

### Worktree provisioning preamble
**Source:** `75-BUMP-EVIDENCE.md` lines 1-24, repeated identically across every `75-*-EVIDENCE.md`
file.
**Apply to:** every `77-*-EVIDENCE.md` and `77-CLOSEOUT-GUARD.md` file that records its own shell
commands.
```
$ date -u +%FT%TZ
$ pwd -P
$ test -f .git; echo "exit:$?"
$ grep -q typsphinx-fhs-run "$(command -v uv)" && echo "shim_check:ok"
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
```

### Measured-not-trusted line citation
**Source:** `76-ATT-EVIDENCE.md` "ATT-01 — measurement at the phase base" section; also RESEARCH
Pitfall 4.
**Apply to:** every file/plan that cites a line number for `release.yml`, `INTEGRATIONS.md`,
`README.md`, `REQUIREMENTS.md`, or `ROADMAP.md` — re-derive with `grep -n`/`sed -n` at execution
time, never copy the number from a planning document.
```
Command: `grep -nF 'secrets.PYPI_API_TOKEN' .github/workflows/release.yml`
```
(then quote 3 lines of context above/below to confirm the surrounding shape matches expectation)

### BASE_/SCRATCH_ evidence variable naming
**Source:** `75-BUMP-EVIDENCE.md`: `BASE_75_03 = <sha>`, `SCRATCH_75_03 = <tmpdir>`.
**Apply to:** every `77-*-EVIDENCE.md` file, using `BASE_77_0N` / `SCRATCH_77_0N` keyed to the
plan number that produced them, so `77-HANDOFF.md` and later evidence files can cross-reference by
name instead of re-deriving.

### Three-observation CLOSEOUT-GUARD fence
**Source:** `75-CLOSEOUT-GUARD.md` + RESEARCH § Pattern 2 + Pitfall 5.
**Apply to:** `77-CLOSEOUT-GUARD.md`, line-scoped to ATT-03, ATT-04, ATT-05, REL-17, DOC-25 (not
ATT-06, which legitimately flips).
```bash
sha256sum .planning/REQUIREMENTS.md
wc -l .planning/REQUIREMENTS.md
grep -n 'ATT-03\|ATT-04\|ATT-05\|REL-17\|DOC-25' .planning/REQUIREMENTS.md
```
Recorded 3 times: phase head, phase close, and once more after `phase.complete`-family tooling.

## No Analog Found

None — every file in scope has at least a role-match analog (see `77-ATT06-EVIDENCE.md` above,
the one file with no exact predecessor; it borrows its probe idiom from `76-ATT-EVIDENCE.md` and
its evidence content directly from this phase's own CONTEXT D-04 and RESEARCH § Verified Facts).

## Metadata

**Analog search scope:** `.planning/milestones/v0.9.6-phases/75-v0-9-6-release-prep-prep-only/`,
`.planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/`, `CHANGELOG.md`
**Files scanned:** 12 analog candidates read/grepped, all git-tracked (verified via `git ls-files`)
**Pattern extraction date:** 2026-09-28
