# Phase 75: v0.9.6 Release Prep (prep-only) - Pattern Map

**Mapped:** 2026-09-20
**Files analyzed:** 10 (5 product-tree edits landing in one commit; 2 procedure artifacts;
CHANGELOG prose sub-sections; evidence-file family)
**Analogs found:** 10 / 10

**No `typsphinx/` file appears anywhere below.** The prep-only fence (D-14) puts the entire
product source tree out of reach this phase; every file this phase creates or edits is either a
release-metadata literal, a documentation file (`CHANGELOG.md`), a test literal
(`RELEASE_VERSIONS`), or a phase-evidence/procedure artifact under `.planning/phases/75-…/`. All
analogs therefore come from the four prior prep-only phase directories (46, 69, 71, 73) and from
`CHANGELOG.md`'s own existing released sections — never from `typsphinx/` or `tests/` product
code.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `pyproject.toml:7` (version literal) | config | CRUD (single literal edit) | Phase 46's `pyproject.toml:7` edit, evidenced in `46-BUMP-EVIDENCE.md` | exact |
| `uv.lock` (regenerated) | config | batch (generated artifact) | Phase 46's `uv lock` / `uv sync --extra dev --locked` transcript in `46-BUMP-EVIDENCE.md` | exact |
| `README.md:348` (Status line) | config/doc | CRUD | Phase 46's `README.md` Status-line edit, `46-BUMP-EVIDENCE.md` "Before/after values" table | exact |
| `CHANGELOG.md` (curate `## [0.9.6]`, fresh `## [Unreleased]`, tail links) | documentation | transform (prose promotion + structural move) | `CHANGELOG.md`'s own `## [0.9.2]` section (`:69-118`) for lead-paragraph/`### Verified` shape; Phase 73's `73-01` promotion pattern for the byte-identical-carry mechanics; `CHANGELOG.md`'s `[0.1.0b1]` `### Known Limitations` (`:1205`) for the new sub-section's shape | exact (structural) / role-match (Known Limitations content, first fresh authorship since `[0.1.0b1]`) |
| `tests/test_changelog_page_gate.py` (`RELEASE_VERSIONS` gains `"0.9.6"`) | test | CRUD (tuple literal append) | Same file's own prior append pattern (each prior release-prep phase appends its own version; visible in the file's `RELEASE_VERSIONS` tuple history) | exact |
| `75-CLOSEOUT-GUARD.md` | phase-evidence (release process) | event-driven (fence + 3 re-verification checkpoints) | `73-CLOSEOUT-GUARD.md` (line-scoped REL-14 fence) / `71-CLOSEOUT-GUARD.md` | exact |
| `75-HANDOFF.md` | phase-evidence (release process) | request-response (ordered procedure the next command executes) | `46-HANDOFF.md` (**the genuine-publish precedent** — tag/PyPI/GitHub-Release/`update-pin.yml`/RTD enumeration) for the publish-step shape; `73-HANDOFF.md` (unpublished-close precedent) for the "What this phase satisfied" / SC table / "Recorded without acting" / "Before and after phase.complete-family tooling" sections | exact (46 for publish steps) / exact (73/71 for evidence-recap sections) |
| `75-BUMP-EVIDENCE.md` | phase-evidence | CRUD proof (before/after transcript) | `46-BUMP-EVIDENCE.md` | exact |
| `75-CHANGELOG-EVIDENCE.md` | phase-evidence | transform proof (diff/fence assertions) | `73-CHANGELOG-EVIDENCE.md` | exact |
| `75-GREEN-TREE-EVIDENCE.md`, `75-CI-EVIDENCE.md`, `75-PREFLIGHT-EVIDENCE.md` | phase-evidence | batch (re-run test/lint/docs/CI/merge-tree probes) | `73-GREEN-TREE-EVIDENCE.md` / `73-CI-EVIDENCE.md` / `73-PREFLIGHT-EVIDENCE.md` (also `71-*` equivalents) | exact |

## Pattern Assignments

### `pyproject.toml` / `uv.lock` / `README.md` (config, CRUD) — the bump commit

**Analog:** `.planning/milestones/v0.7.1-phases/46-v0-7-1-release-prep-prep-only/46-BUMP-EVIDENCE.md`

**Before/after table pattern** (evidence file's own shape, to be reproduced for 0.9.2 -> 0.9.6):
```markdown
| Surface | Before | After |
|---|---|---|
| `pyproject.toml` line 7 | `version = "0.7.0"` | `version = "0.7.1"` |
| `README.md` line 342 | `**Status**: Stable (v0.7.0) - Production ready` | `**Status**: Stable (v0.7.1) - Production ready` |
| `uv.lock`'s `typsphinx` entry | `version = "0.7.0"` | `version = "0.7.1"` |
```

**Regeneration + proof pattern** (never hand-edit `uv.lock`):
```
$ uv lock
$ uv sync --extra dev --locked
$ uv lock --check
$ uv run python -c "import typsphinx; print(typsphinx.__version__)"
0.7.1
```
For Phase 75: substitute `0.9.2` -> `0.9.6`; `pyproject.toml:7`, `README.md:348` per
75-CONTEXT.md's measured line numbers. **This commit is NOT split from the CHANGELOG edit** — see
Pattern 1 below; Phase 46's two-commit split (`46-01` CHANGELOG, `46-02` bump) is the one thing
NOT to copy from this analog.

---

### `CHANGELOG.md` (documentation, transform) — the `## [0.9.6]` section

**Analog 1 — structural shape:** `CHANGELOG.md:69-118` (the existing `## [0.9.2]` section)

**Lead paragraph + upgrade recommendation pattern** (`CHANGELOG.md:69-74`):
```markdown
## [0.9.2] - 2026-08-30

This release curates the Windows-shaped path-handling hardening accumulated since 0.9.0 — an
output-directory escape check, an absolute image URI that aborted the PDF build, and diagnostic
message quoting — together with a separate compile-blocking defect in the image visitor. A project
built with the published 0.9.0 release produced no PDF for any master document when an image was
not first in its container, and 0.9.0 users should upgrade to this release. Zero new runtime
dependencies; the bundled `@preview` version-sync surface is untouched.
```
D-03 requires the same register but anchored on **0.9.2** (not 0.9.0) as the reader's prior
release, and D-02 requires the doctest fix (not the contributor tooling) as the framed subject.

**`### Verified` section pattern** (`CHANGELOG.md:113-118`):
```markdown
### Verified

- Zero new runtime or dev dependencies across this milestone's diff (`v0.9.0..HEAD`) — the only
  change to `pyproject.toml` and `uv.lock` is the version literal itself.
- The four bundled `@preview` package version strings unchanged across all four sync surfaces
  (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`).
- The `visit_image()` separator fix is bound by a real `typst.compile()` gate covering the 16
  previously-failing and 9 must-keep-passing image shapes (TEST-05), with 18 of 18 master
  documents compiling.
```
D-04 forbids copying the first bullet's blanket "Zero new runtime or dev dependencies" sentence
verbatim — the `dev` extra changed (`tox-uv-bare` -> `tox-uv`, `ruff` cap `<0.16` -> `<0.17`); the
corrected wording is spelled out in D-04 itself. The GATE-01 real-compile-coverage bullet and the
clean-build-warning-ledger bullet follow this same one-bullet-per-invariant shape.

**Bullet register (bold lead + trailing requirement-ID parentheses)** (`CHANGELOG.md:96-104`):
```markdown
- **A path named in a diagnostic message now reads exactly as it appears on disk (MSG-02, MSG-03,
  MSG-04, MSG-05).** Path-valued messages across the extension no longer double a Windows
  separator, and the quoting that wraps a path no longer closes early on a path containing a
  quote character...
```

**Analog 2 — the byte-identical-promotion mechanics:** Phase 73's own `73-01` promotion (its
`73-CHANGELOG-EVIDENCE.md` records the measurement discipline to reuse):
```
$ grep -cE '^## \[' CHANGELOG.md          # HEADINGS_BEFORE
$ grep -cE '^\[[^]]+\]: https' CHANGELOG.md   # LINKREFS_BEFORE
$ awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' CHANGELOG.md | grep -cE '^- \*\*'
$ awk '/^### Changed$/{f=1;print;next} f && /^### /{exit} f' CHANGELOG.md | sha256sum
```
For Phase 75, run the same shape but stop the `awk` scan at `## \[0\.9\.6\]` (the new heading
being inserted, not `## [0.9.2]`), and re-verify each carried bullet's SHA-256 is unchanged after
promotion (D-01's "byte-identical" requirement).

**Analog 3 — `### Known Limitations` sub-section shape:** `CHANGELOG.md:1205` (in `[0.1.0b1]`):
```markdown
### Known Limitations

- **Requirement 11** (Extensibility and Plugin Support): Custom node handler registry not yet implemented
  - Planned for v0.2.0
  - Workaround: Extend TypstTranslator directly
- **Bibliography**: BibTeX integration not yet supported
```
D-11 requires the NUM-01 entry to follow this bold-lead / sub-bullets / `Workaround:` register,
but with the precondition + both symptoms spelled out in prose (not a one-line stub like the
`[0.1.0b1]` bullets above) — draft text is in 75-RESEARCH.md Pattern 4, sourced from
`.planning/todos/pending/2026-08-14-numref-…md`.

**Tail link block pattern** (`CHANGELOG.md` end):
```markdown
[0.7.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.1
...
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.2...HEAD
```
For Phase 75: insert `[0.9.6]: .../releases/tag/v0.9.6` above the `[0.9.2]` line, and move
`[Unreleased]`'s compare base to `v0.9.2...HEAD` -> re-pointed so its base becomes `v0.9.6` (the
new released tip), per Claude's Discretion "The tail link block".

---

### `tests/test_changelog_page_gate.py` (test, CRUD) — `RELEASE_VERSIONS`

**Analog:** the file's own existing tuple (read `RELEASE_VERSIONS` around line 50 at execution
time and append `"0.9.6"` in the same style prior entries used — a plain string literal appended
to the tuple, no reordering of existing entries).

---

### `75-CLOSEOUT-GUARD.md` (phase-evidence, event-driven fence)

**Analog:** `73-CLOSEOUT-GUARD.md` (full file read this session)

**Baseline-recording pattern:**
```
$ git rev-parse HEAD
$ git log -1 --format='%H %s'
$ sha256sum .planning/REQUIREMENTS.md
$ wc -l .planning/REQUIREMENTS.md
$ grep -c 'REL-14' .planning/REQUIREMENTS.md
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
```
followed by recording key lines:
```
PHASE_BASE_SHA = ...
REQ_SHA256_BASE = ...
REQ_LINES_BASE = ...
REL14_HITS_BASE = ...
GUARD_AT = ...
```

**"The lines under guard" pattern** — verbatim `grep -n` transcript, classified state-bearing vs.
informational:
```
$ grep -n 'REL-14' .planning/REQUIREMENTS.md
22:- [ ] **REL-14**: ...
57:| REL-14 | Phase 73 | Pending |
62:- Mapped to phases: ...
65:- REL-14 is mapped to Phase 73 for coverage only; ...
```
For Phase 75: **line-scope to REL-15 only** (per 75-CONTEXT.md's fence design, since REL-16
legitimately closes this phase and its lines are expected to move — record REL-16's `grep -n` hits
**separately**, explicitly marked expected-to-move, per 75-RESEARCH.md Pattern 2). Re-verify at
phase close and once more after `phase.complete`-family tooling, exactly as 73's guard structures
its "Re-verification at phase close" section (not shown above but present in the full file) and
its "For the operator running phase.complete" section (reproduced inside `73-HANDOFF.md`'s own
tail section, see below).

---

### `75-HANDOFF.md` (phase-evidence, request-response procedure)

**Analog A — the genuine-publish precedent (structurally closer to Phase 75 than 73/71):**
`46-HANDOFF.md` (full file read this session) — Phase 46 is the only prior prep-only phase whose
milestone actually published.

**Numbered-checklist-with-Owner/Ordering pattern** (`46-HANDOFF.md` "## Checklist"):
```markdown
### 1. Open the pull request and merge it to `main`
**Owner:** `/gsd-complete-milestone`.
**Ordering:** first — every item below depends on the milestone branch reaching `main`.

### 2. Push the `v0.7.1` tag on the merge commit
**Owner:** `/gsd-complete-milestone`.
**Ordering:** after item 1 ... Pushing `v0.7.1` fires `.github/workflows/release.yml`.

### 3. Let `release.yml` run to completion: `validate` -> `build` -> `publish-pypi` -> `create-release`
**Owner:** `/gsd-complete-milestone`, with a human approval step on the `pypi` environment.
**Watch `create-release` succeed and record the run id...**

### 4. Advance the `typsphinx-doc-translations` submodule pin and push a matching tag there
**Owner:** `/gsd-complete-milestone` plus human.

### 5. Confirm Read the Docs `stable` is green on BOTH projects (en and ja) and reports the version
**Owner:** human, via the RTD public API or real fetches (no authentication needed).

### 6. Flip the requirement checkboxes and Traceability rows in `REQUIREMENTS.md`
**Owner:** `/gsd-complete-milestone`.
**Standing warning, carried from `41-HANDOFF.md` item 6:** `phase.complete` has a recorded habit
of auto-flipping REL rows against a CONTEXT decision...

### 7. Re-date the CHANGELOG heading if needed, and re-confirm the extractor
```
For Phase 75, adapt this exact seven-item shape: item 4 becomes the **manual**
`typsphinx-doc-translations` `update-pin.yml` dispatch (not an automatic submodule-pin step — per
75-CONTEXT.md's Claude's Discretion "The handoff"); item 3's `create-release`-has-never-run-on-a-
v0.9.x-tag caveat must be stated (75-CONTEXT.md explicitly requires this fact recorded); item 5's
RTD confirmation covers both `en` and `ja` `stable` endpoints reporting `0.9.6`.

**Analog B — the "What this phase satisfied" / SC-table / "Recorded without acting" / fence-
reproduction sections:** `73-HANDOFF.md` / `71-HANDOFF.md` (both read in full this session).

**"What this phase satisfied" pattern** (quote the requirement verbatim, then the SC table):
```markdown
**REL-14**, quoted verbatim from `.planning/REQUIREMENTS.md:22`:
> - [ ] **REL-14**: Close prep only, unpublished. ...

**REL-14 stays open until step 7 above runs.** No plan in this phase — including this one —
touched its checkbox; every SUMMARY of this phase declares `requirements-completed: []`.

- **SC#1** (...) — **MET**. `73-SC1-INVARIANTS.md` § "Observation 1 of 2" ...
```

**"Recorded without acting" pattern** (Dependabot/open-PR census with a live re-read):
```markdown
**D-06.** The open-PR census from `71-PREFLIGHT-EVIDENCE.md` § "Open pull requests (D-12)":
PR_CENSUS_AT = ...
OPEN_PRS = 0
**Live re-read, taken during this plan's own execution:**
$ gh pr list --state open --json number,title,author,headRefName,baseRefName
[]
```

**"Before and after phase.complete-family tooling" pattern** (reproduces the guard's re-
verification commands inline so the operator needs no second file open):
```bash
sha256sum .planning/REQUIREMENTS.md   # compare against: <hash>
wc -l .planning/REQUIREMENTS.md       # compare against: <N>
git diff --name-only -- .planning/REQUIREMENTS.md   # expected: no output
grep -n 'REL-14' .planning/REQUIREMENTS.md   # expected: byte-identical to: <lines>
```
followed by a reversion recipe: `git checkout -- .planning/REQUIREMENTS.md`, re-run to show MATCH,
then diff `ROADMAP.md`/`STATE.md` against the scratch backup.

For Phase 75: this section is line-scoped to REL-15 (not the whole file, and not REL-16, which
legitimately closes) — the `grep -n 'REL-15'` transcript and its expected-unchanged lines go here
verbatim, with REL-16's lines recorded in a clearly separate "expected to move" callout.

---

### `75-BUMP-EVIDENCE.md`, `75-CHANGELOG-EVIDENCE.md`, `75-GREEN-TREE-EVIDENCE.md`,
### `75-CI-EVIDENCE.md`, `75-PREFLIGHT-EVIDENCE.md` (phase-evidence, batch proof)

**Analogs:** `46-BUMP-EVIDENCE.md` (bump); `73-CHANGELOG-EVIDENCE.md` (changelog fence
assertions); `73-GREEN-TREE-EVIDENCE.md` / `73-CI-EVIDENCE.md` / `73-PREFLIGHT-EVIDENCE.md`
(green-tree/CI/trial-merge triad; `71-*` equivalents are the same shape with the Phase 71 numbers).

**Provisioning-header pattern, reused verbatim in every evidence file** (`73-CHANGELOG-EVIDENCE.md`
head):
```
$ date -u +%FT%TZ
$ pwd -P
$ test -f .git; echo "exit:$?"
$ command -v uv
$ grep -c typsphinx-fhs-run "$(command -v uv)"
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
```
followed by a `.venv/pyvenv.cfg` transcript and named `PYVENV_HOME_*` / `PYVENV_VERSION_*` /
`SCRATCH_*` key lines — every evidence file in this phase should open with this same header, per
CLAUDE.md's worktree-provisioning requirement and Pitfall 1 (the `docs` extra must be present or
the changelog-page-gate content classes silently skip).

**Trial-merge pattern (`75-PREFLIGHT-EVIDENCE.md`):**
```
git fetch origin
git merge-tree --write-tree HEAD origin/main   # transcribe exit code + tree SHA
git archive <tree-sha> pyproject.toml uv.lock | tar -x   # into scratch
uv lock --check
ruff check .
gh api repos/YuSabo90002/typsphinx/branches/main/protection --jq '{...}'
```
(75-RESEARCH.md Pattern 3, itself lifted from `73-RESEARCH.md` Pattern 2 unchanged.)

## Shared Patterns

### The one-commit bump+CHANGELOG rule (this phase's own divergence — not reused from any prior
### phase's commit shape)
**Source:** 75-CONTEXT.md Phase Boundary bullet 1 + Claude's Discretion AMENDED block; 75-RESEARCH.md
Pattern 1.
**Apply to:** the single product-tree commit covering `pyproject.toml`, `uv.lock`, `README.md`,
`CHANGELOG.md`, and `tests/test_changelog_page_gate.py` together.
```bash
git add pyproject.toml uv.lock README.md CHANGELOG.md tests/test_changelog_page_gate.py
git commit -m "..."
git show --name-only HEAD   # must list exactly these five files
```
**Explicitly NOT Phase 46's precedent** (which split CHANGELOG and bump into two commits,
`46-01`/`46-02`) — this is the one place where copying the closest historical analog's shape
verbatim would be wrong; 75-CONTEXT.md's binding text requires the union in one commit.

### Provisioning + shim discipline
**Source:** `CLAUDE.md` §§ "Worktree-isolated execution" / "NixOS development shell"; every prior
evidence file's own header (see above).
**Apply to:** every evidence-file-generating plan in this phase.
```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
uv run pytest
```
Bare `ruff`/`black`/`mypy`/`pytest`/`tox`/`uv`/`sphinx-build` only (PATH shims), never
`.venv/bin/<tool>` directly, on this machine.

### `LC_ALL=C` + clean-rebuild discipline for every warning count
**Source:** 75-RESEARCH.md Pitfalls 3 and 4; every prior `*-GREEN-TREE-EVIDENCE.md`'s docs-build
sections.
**Apply to:** `75-GREEN-TREE-EVIDENCE.md`'s `docs-html`/`docs-pdf`/`linkcheck` sections and any
`### Fixed` bullet's warning-count claim (QUA-14).
```bash
rm -rf docs/_build
LC_ALL=C tox -e docs-html
```
with a positive control (a known-warning-carrying build) run first to prove the grep itself works.

## No Analog Found

None. Every file this phase creates or edits has a direct, exact-match analog in Phase 46, 69, 71
or 73's own artifacts, or in `CHANGELOG.md`'s own existing sections.

## Metadata

**Analog search scope:** `.planning/milestones/v0.9.5-phases/73-…/`,
`.planning/milestones/v0.9.4-phases/71-…/`, `.planning/milestones/v0.9.3-phases/69-…/` (named in
scope but not separately excerpted — its shape is intermediate between 71 and 73 and adds nothing
71/73 didn't already cover for this phase's purposes), `.planning/milestones/v0.7.1-phases/46-…/`
(the sole genuine-publish precedent), and `CHANGELOG.md` itself (`:1-118`, `:1195-1225`, tail
block).
**Files scanned:** ~14 (directory listings for 71/73; full reads of `73-CLOSEOUT-GUARD.md`,
`73-HANDOFF.md`, `71-HANDOFF.md`, `46-HANDOFF.md`, `46-BUMP-EVIDENCE.md` (partial),
`73-CHANGELOG-EVIDENCE.md` (partial); targeted reads of `CHANGELOG.md`).
**Pattern extraction date:** 2026-09-20
