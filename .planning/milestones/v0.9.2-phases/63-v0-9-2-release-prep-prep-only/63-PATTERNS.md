# Phase 63: v0.9.2 Release Prep (prep-only) - Pattern Map

**Mapped:** 2026-08-30
**Files analyzed:** 11 (5 mechanically-edited repo files + 6 evidence/handoff documents)
**Analogs found:** 11 / 11

This is a release-prep phase: "analog" means a prior phase's own artifact of the same kind, not a
source-code sibling. Two classes are mapped separately per the phase-specific guidance.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `pyproject.toml:7` | config | mechanical edit (version literal) | `pyproject.toml` at every prior bump (v0.9.0 bump: `0.8.0`→`0.9.0`) | exact |
| `uv.lock` (self-package stanza, ~line 1467) | config | generated, never hand-edited | same file, regenerated at every prior bump via `uv lock` | exact |
| `README.md:347` | config/doc | mechanical edit (status line) | `README.md` Status line at every prior bump | exact |
| `tests/test_changelog_page_gate.py:50-66` | test | CRUD (append tuple entry) | same file, `dcee0201` (57-03, extended to 0.9.0) | exact |
| `CHANGELOG.md` (`## [0.9.2]` section) | doc | transform (content authoring) | `## [0.6.5]` section, `CHANGELOG.md:381-403` | exact (same defect class: compile-blocking separator) |
| `CHANGELOG.md` (4-step edit: relocate/rename/tail-link/extract) | doc | transform (structural edit) | `CHANGELOG.md`'s own `## [Unreleased]`→`## [0.9.0]` promotion at Phase 57 | exact |
| `63-CLOSEOUT-GUARD.md` | evidence | request-response (probe + compare) | `61-CLOSEOUT-GUARD.md` | exact |
| `63-CHANGELOG-EVIDENCE.md` | evidence | transform (transcription) | `61-CHANGELOG-EVIDENCE.md` (+ `57-CHANGELOG-EVIDENCE.md` for the real-bump/real-extraction shape) | exact |
| `63-GREEN-TREE-EVIDENCE.md` | evidence | batch (test-run transcription) | `61-GREEN-TREE-EVIDENCE.md` | exact |
| `63-CI-EVIDENCE.md` | evidence | event-driven (dispatch + poll) | `61-CI-EVIDENCE.md` | exact |
| `63-SC5-INVARIANTS.md` | evidence | request-response (probe + positive control) | `61-SC4-INVARIANTS.md` (rename SC4→SC5; numbering differs, shape identical) | exact (name differs) |
| `63-HANDOFF.md` | evidence/doc | transform (checklist authoring) | `61-HANDOFF.md` structure, but **polarity inverted** (positive opening per D-13) + `57-HANDOFF.md` for the "real publish checklist" shape 61 lacked | exact-with-inversion |

**Hard constraint:** `63-VERIFICATION.md` must NOT appear anywhere in this list or in any plan's
file-creation set — it is `gsd-verifier`'s reserved output name (D-19).

---

## Pattern Assignments

### `pyproject.toml:7` (config, mechanical edit)

**Analog:** same file, every prior bump commit (most recent: `0.8.0`→`0.9.0`)

**Diff shape** (measured via `git log -p -- pyproject.toml`):
```diff
 [project]
 name = "typsphinx"
-version = "0.8.0"
+version = "0.9.0"
 description = "Sphinx extension for Typst output"
 readme = "README.md"
```
For this phase: `-version = "0.9.0"` / `+version = "0.9.2"`. This is the **sole hand-edited version
literal** in the repo (D-17); everything else derives from it.

---

### `uv.lock` (self-package stanza)

**Analog:** same file, regenerated (never hand-edited) at every prior bump

**Command pattern** (from `57-BUMP-EVIDENCE.md`, reproduced in `63-RESEARCH.md` Pattern 1):
```bash
uv lock
# Expect: "Resolved N packages in Xms" / "Updated typsphinx v0.9.0 -> v0.9.2"
uv sync --extra dev --locked
# Expect an uninstall/install pair: "- typsphinx==0.9.0" / "+ typsphinx==0.9.2"
uv lock --check   # exit 0
uv run python -c "import typsphinx; print(typsphinx.__version__)"   # -> 0.9.2
```
Never hand-edit the `version = "..."` line inside `uv.lock` (D-17) — `uv lock --check` would then
catch the drift.

---

### `README.md:347` (config/doc, mechanical edit)

**Analog:** same file, Status line at every prior bump

**Diff shape** (measured via `git log -p -- README.md`):
```diff
 ---

-**Status**: Stable (v0.8.0) - Production ready
+**Status**: Stable (v0.9.0) - Production ready
 **Python**: 3.12+ | **Sphinx**: 9.1+ | **Typst**: 0.15+
```
For this phase: `v0.9.0`→`v0.9.2`. No other `README.md` edit is permitted (D-09) —
`## Known Limitations` (line 289) is untouched, its two entries (Bibliography, Citations) unchanged.
Enforced by `tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject`.

---

### `tests/test_changelog_page_gate.py:50-66` (test, CRUD append)

**Analog:** same file, commit `dcee0201` ("feat(57-03): roll over CHANGELOG tail block, extend
page-gate coverage")

**Actual diff** (from `git show dcee0201 -- tests/test_changelog_page_gate.py`):
```diff
-# The 14 releases the published page was frozen without (0.4.4 through 0.8.0,
+# The 15 releases the published page was frozen without (0.4.4 through 0.9.0,
 # inclusive) -- shared by both the HTML and PDF content-coverage assertions
 # below so the two builders are held to the identical bar.
 RELEASE_VERSIONS = (
@@
     "0.7.0",
     "0.7.1",
     "0.8.0",
+    "0.9.0",
 )
```
Earlier precedents with the identical shape: `0c784c48` ("test(52-02): extend RELEASE_VERSIONS to
14 entries through 0.8.0"), `075c07d0` ("test(46-03): extend RELEASE_VERSIONS to 0.7.1"). For this
phase: append `"0.9.2"`, bump the comment's count (currently 15, "0.4.4 through 0.9.0") and its
tail version to "16 … through 0.9.2". **Proof hazard (D-11, Pitfall 3 in RESEARCH):** the two
content-coverage test classes SKIP under a `dev`-only sync (`myst_parser` lives only in the `docs`
extra). Must run:
```bash
uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v
```
and confirm `PASSED` (not `SKIPPED`) on the two coverage classes, or cite the dispatched CI docs
job's own conclusion (which always carries the `docs` extra via `tox.ini`).

---

### `CHANGELOG.md` — new `## [0.9.2]` section (doc, transform)

**Analog:** `## [0.6.5]` section, `CHANGELOG.md:381-403` — verbatim, reproduced in full below.
Same defect class (a missing separator aborting the Typst compile), same release class (patch, no
breaking change), same section vocabulary.

```markdown
## [0.6.5] - 2026-07-29

Fixes a compile-blocking defect where a document mixing prose and math could abort the Typst
compile: inline and display math no longer emit without a valid separator from surrounding text.
The runtime change is confined to the math handlers in `typsphinx/translator.py` — both the inline
and the display-math visitor gained separator participation — with no other file under `typsphinx/`
touched. Zero new runtime dependencies; the bundled `@preview` version-sync surface is untouched.

### Fixed

- **Inline math immediately after text no longer aborts the `typstpdf` compile (MATH-01)** — in
  bullet-list items, definition-list terms, and the like (including display math inside a list
  item, which is the same user-visible change), a missing separator between the preceding text
  emission and the `mi(...)` / `$...$` call previously produced Typst that failed to compile. Fixed
  on both emission paths — the mitex default and the native path.

### Verified

- Zero new runtime dependencies across the full milestone diff.
- The four bundled `@preview` package version strings unchanged across all four sync surfaces
  (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`).
- The full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run remains fatal-free.
```

**What to keep from this template:** lead paragraph names the defect + scopes the runtime change +
states "Zero new runtime dependencies"; `### Fixed` then `### Verified` only (no `### Added`/
`### Changed`/`### Removed`); each `### Verified` bullet is a measured fact, never carried on prose.

**What NOT to keep (D-06's explicit warning):** the third `### Verified` bullet
("The full-corpus … `-b typstpdf` re-run remains fatal-free") must **not** be copied — this
milestone did not run that corpus. Substitute the TEST-05 gate result (16 previously-failing + 9
must-keep-passing image shapes, 18/18 masters compiling via a real `typst.compile()`).

**Current live `## [Unreleased]` bullets to promote verbatim** (`CHANGELOG.md:8-36`, read this
session):
```markdown
## [Unreleased]

### Fixed

- **A Windows-shaped `typst_documents` target that reaches outside the output directory is now
  refused on the normalized path, matching its sibling image-URI check (PATH-01).** ...

- **A Windows-shaped absolute image URI now compiles instead of aborting the PDF build (IMG-04,
  IMG-05, IMG-06, IMG-07).** ...

- **A path named in a diagnostic message now reads exactly as it appears on disk (MSG-02, MSG-03,
  MSG-04, MSG-05).** ... a POSIX path with an apostrophe in it (for example, a directory named
  `O'Brien`) was affected by the same defect family as a Windows-shaped path, so this is not a
  Windows-exclusive fix. ...

### Planned for Future Releases
- BibTeX/bibliography support
- Glossary generation
- Index generation
- Pre-commit hooks
- Additional Typst Universe template integration
```
Per D-04: promote these three bullets **verbatim** (trim only a clause the new lead paragraph makes
literally redundant). Per D-05: prepend a new IMG-08/IMG-09/IMG-10 bullet describing the inline-image
separator fix, citing all three IDs in trailing parentheses, leading the `### Fixed` list. Per D-03
order: IMG-08/09/10 → PATH-01 → IMG-04..07 → MSG-02..05.

---

### `CHANGELOG.md` — the 4-step structural edit (doc, transform, REL-10)

**Analog:** `scripts/extract_changelog_section.py`'s own positional algorithm (read this session:
`_SECTION_HEADER_RE = r"^## \[(?P<version>[^\]]+)\]"`, `extract_section()` lines 62-116) — the
edit order is dictated by this script's behavior, not by a prior phase's diff, because this is the
first release-prep phase since 57 with both a scratch block AND a real heading rename to sequence.

**Current headings measured this session** (`grep -n '^## \[' CHANGELOG.md`):
```
Line 8:  ## [Unreleased]
Line 38: ### Planned for Future Releases   (scratch block, 5 bullets)
Line 45: ## [0.9.0] - 2026-08-17           (terminator the extractor stops at today)
```

**Tail-link block** (`CHANGELOG.md:1246-1250`, read this session):
```
[0.9.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.0
[0.8.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.8.0
[0.7.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.1
```
Insert `[0.9.2]: .../releases/tag/v0.9.2` immediately above the `[0.9.0]:` line; advance
`[Unreleased]: .../compare/v0.9.0...HEAD` to `.../compare/v0.9.2...HEAD`, staying the last line.

**Order (load-bearing, per Pattern 2 in RESEARCH.md and Pitfall 2):**
1. Relocate `### Planned for Future Releases` under a **fresh empty** `## [Unreleased]` placed
   **above** the existing heading.
2. Rename the (old, now-second) `## [Unreleased]` → `## [0.9.2] - 2026-08-30`; add lead paragraph,
   IMG-08/09/10 bullet first, `### Verified`.
3. Tail-link roll (insert `[0.9.2]:`, advance `[Unreleased]:` compare base).
4. Run the extractor and read stdout:
```bash
uv run python scripts/extract_changelog_section.py 0.9.2
echo $?   # expect 0
grep -c '^## \[0\.9\.1\]' CHANGELOG.md          # expect 0
grep -c '^\[0\.9\.1\]:' CHANGELOG.md            # expect 0
uv run python scripts/extract_changelog_section.py 0.9.2 | grep -c 'Planned for Future Releases'
                                                  # expect 0
```

---

### `63-CLOSEOUT-GUARD.md` (evidence, request-response probe+compare)

**Analog:** `61-CLOSEOUT-GUARD.md` — reused **verbatim** per D-16, phase number and baseline
re-measured fresh.

**Section skeleton** (`grep -n '^#'`):
```
# Phase 61 — REL-09 Checkbox-Flip Closeout Guard
## Baseline
## The lines under guard
### REL-09's requirement bullet's checkbox line
### REL-09's Traceability row
### The phase-totals line
## Why this file exists
## Re-verification protocol (phase close)
## Post-close detection and reversion (after phase.complete runs)
## This task's own effect on `.planning/REQUIREMENTS.md`
## Re-verification at phase close
## For the operator running phase.complete
```

**Baseline block, verbatim shape** (lines 1-22):
```markdown
# Phase 61 — REL-09 Checkbox-Flip Closeout Guard

This task changes NO requirement state: REL-09 stays an unchecked box (`- [ ]`) and its
Traceability row stays `Pending`. `.planning/REQUIREMENTS.md` is read and quoted here and never
edited.

## Baseline

Recorded at phase head, inside this plan's isolated worktree (`worktree-agent-a9f8e61dc22c6d378`),
before any other plan in Phase 61 has run.

```
$ sha256sum .planning/REQUIREMENTS.md
4682f8cde6b068c2ebbe42201fdff4b0b4cf17558d68c889baaf2f4506d531e1  .planning/REQUIREMENTS.md

$ wc -l .planning/REQUIREMENTS.md
258 .planning/REQUIREMENTS.md

$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-29T15:04:23Z

$ git rev-parse HEAD
5e28fa9dac8576f1f1665560eb5c4ccbd2e13b41
```

**PHASE_BASE_SHA:** <the same commit, quoted again as the anchor plan 63-final's scoped diff reads>
```

**Re-verification protocol, exact command triad** (lines 103-118, reuse literally):
```bash
sha256sum .planning/REQUIREMENTS.md
# compare the printed digest against this file's Baseline: <sha256>

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-09' .planning/REQUIREMENTS.md
# expected: byte-identical to the three quoted lines above (line numbers)
```
This same triad is run a **third time**, after `phase.complete`-family tooling has run (D-16) — the
"Post-close detection and reversion" section reproduces it again so an operator following
`63-HANDOFF.md` reaches it without opening this file separately.

**Pitfall 6 (this project's own measured hazard for Phase 63):** do not copy 61's exact three grep
line numbers (127/206/220) — re-run `grep -n 'REL-09' .planning/REQUIREMENTS.md` against the
CURRENT tree; this research measured **three hits at lines 70, 154, 175** this session, and line
175 begins a six-line prose paragraph, not a single terse line like 61's line 220 — decide
explicitly (following 61's own precedent) whether that third hit is state-bearing or
informational-only for the fence.

---

### `63-CHANGELOG-EVIDENCE.md` (evidence, transcription)

**Analog:** `61-CHANGELOG-EVIDENCE.md` (structure) + `57-CHANGELOG-EVIDENCE.md` (real-bump,
real-extraction content — 61 never ran the extractor since it had no versioned section; 63 is the
first phase since 57 that can).

**Section skeleton** (`61-CHANGELOG-EVIDENCE.md`):
```
# Phase 61 — CHANGELOG Evidence (SC#2 as REWORDED by D-11)
## This plan's base SHA
## Pre-edit measurements (taken before touching CHANGELOG.md)
## What this file is NOT
## The PATH-01 bullet (tracer slice)
### Fixed
## Fence assertions after the bullet landed
## Docs render — tracer slice
## The remaining two defect families (IMG and MSG)
## Pure-addition proof
## Fence assertions over CHANGELOG.md and the version literals
## Docs render — full comparison against the 3 / 5 baseline
```
For 63, retitle to reflect REL-10 (the extractor-leakage check) and D-20's three named greps. The
extractor's stdout must be **transcribed verbatim**, not summarized — D-20's binding requirement.

---

### `63-GREEN-TREE-EVIDENCE.md` (evidence, batch test-run transcription)

**Analog:** `61-GREEN-TREE-EVIDENCE.md`

**Section skeleton:**
```
# Phase 61 — Local Green-Tree Evidence (SC#3, local half, re-anchored per D-09)
## Provisioning and tree identity
## Product-tree delta from the phase base
## Division of authority
## SC#3 — full pytest suite
## SC#3 — format, type and version-sync gates
### Executed versus skipped
```
For 63: run `rm -rf docs/_build` before each of `tox -e docs-html`/`docs-pdf` (D-21) — cite the
**fresh** `build succeeded, N warnings.` tail line, not the recalled 3/5 baseline (Pitfall 5).

---

### `63-CI-EVIDENCE.md` (evidence, event-driven dispatch+poll)

**Analog:** `61-CI-EVIDENCE.md`

**Section skeleton:**
```
# Phase 61 — 3-OS CI Evidence (SC#3, dispatch half, re-anchored per D-09)
## Pre-dispatch confirmation
## Dispatch
## Run
### Both windows-latest lanes
## 12-job census
## Dispatch count
```

**Pre-dispatch confirmation excerpt** (real shape, lines 1-30):
```
# Phase 61 — 3-OS CI Evidence (SC#3, dispatch half, re-anchored per D-09)

## Pre-dispatch confirmation

$ git rev-parse HEAD
14fcb460919455d8910fff4dece8b948de96ecc4

$ uv sync --extra dev --locked
Resolved 89 packages in 0.61ms
Checked 79 packages in 0.55ms
```
Succeeded with no drift — confirms `uv.lock` regeneration (D-17) landed BEFORE dispatch.

**Dispatch command shape (D-18, ⚠️ amended step name):**
```bash
gh workflow run CI --ref gsd/v0.9.2-inline-image-blocker-fix-and-release
gh run watch <run-id>
gh run view <run-id> --json jobs
```
`ruff`'s verdict is read from the `lint` job (displayed as **"Lint and Format Check"** in
`gh run view`'s job list) — its one substantive step is **"Run lint with tox"** (`ci.yml:69`), never
a step literally named "Run linters" (that name belongs to `release.yml:84`'s `validate` job, which
must never be triggered in this phase). Both `windows-latest` lanes and `macos-latest` are named
individually; all 12 job conclusions are transcribed literally.

---

### `63-SC5-INVARIANTS.md` (evidence, request-response probe+positive-control)

**Analog:** `61-SC4-INVARIANTS.md` — Phase 61 named it `61-SC4-INVARIANTS.md` because its own SC
numbering differed; map to `63-SC5-INVARIANTS.md` per this phase's SC numbering (CONTEXT/RESEARCH
already resolved this naming).

**Section skeleton:**
```
# Phase 61 — SC#4 Fence Invariants (RETAINED in full per D-11)
## Observation 1 of 2
### Local tag probe
### Remote tag probe (unfiltered, with positive control)
### Publish probe
### Release-workflow probe
### Observation 1 verdict
## Milestone anchor (recorded, not swept)
## The milestone-invariant sweep — resolved in writing, not left as a silent absence
## Handoff to observation 2
## Observation 2 of 2
### Local tag probe
### Remote tag probe (unfiltered, with positive control)
### Publish probe
### Release-workflow probe
### Observation 2 verdict — the separation, stated explicitly
## The typsphinx/ diff (SC#4)
### The scoped diff (the SC#4 claim)
### The widened diff (the positive control)
## Commits after the CI dispatch
```

**Positive-control pattern (do not omit — Anti-Pattern in RESEARCH.md):**
```bash
# Local tag probe
git tag -l 'v0.9.2'                       # expect empty

# Remote tag probe, unfiltered, with positive control
git ls-remote --tags origin | grep -c 'v0\.9\.0'   # positive control, expect >=1 (known to exist)
git ls-remote --tags origin | grep -c 'v0\.9\.2'   # the actual assertion, expect 0

# Publish probe
gh release list        # positive control: v0.9.0 (or later) present with a "Latest" marker
gh release view v0.9.2 # expect: release not found

# Release-workflow probe
gh run list --workflow=release.yml --limit 5   # expect: no run against this phase's tip
```
For SC#4's scoped/widened diff (renamed SC#5 here): the widened diff's expected non-empty result is
**this phase's own five bump-commit files** (`pyproject.toml`, `uv.lock`, `README.md`,
`CHANGELOG.md`, `tests/test_changelog_page_gate.py`), not 61's single-file `CHANGELOG.md` result —
do not copy 61's expected file list.

The two observations must be separated by **intervening waves**, not wall-clock luck (SC#5's own
requirement, unweakenable per CONTEXT §Claude's Discretion boundary).

---

### `63-HANDOFF.md` (evidence/doc, transform checklist authoring)

**Analog:** `61-HANDOFF.md`'s structure, **with polarity inverted per D-13** — 61 opened negative
("this milestone publishes nothing") because that was the anomaly; 63 restores the standing
positive-opening shape `46-HANDOFF.md` through `57-HANDOFF.md` used, because 63 **does** publish
(at `/gsd-complete-milestone`, not in this phase).

**Section skeleton (61's, for structural reference):**
```
# Phase 61: v0.9.1 Release Prep (prep-only) — Milestone Close-Out, No Publish
## What this phase satisfied, and what it did not
## What the v0.9.2 milestone inherits
### 1. The second-repository tag for `typsphinx-doc-translations`
### 2. The Read the Docs `stable` measurement for both projects
### 3. The GitHub Release body reproduction check
## What v0.9.2 must also pick up
## Before declaring the milestone closed
## Fence observation
## What this phase deliberately did not do
```

**The three inherited publish-step command shapes (`vX.Y.Z` → resolve to `v0.9.2`)**, verbatim from
`61-HANDOFF.md:77-116`:
```bash
# 1. typsphinx-doc-translations pin dispatch (a MANUAL dispatch, not a tag-push side effect)
gh workflow run update-pin.yml --repo YuSabo90002/typsphinx-doc-translations
gh run list --repo YuSabo90002/typsphinx-doc-translations --workflow=update-pin.yml --limit 1
gh run watch --repo YuSabo90002/typsphinx-doc-translations <run-id>
# Pin commit does not itself tag; tag that repo's tracked branch with vX.Y.Z separately.

# 2. Read the Docs `stable` measurement — unauthenticated public API calls, both `en` (typsphinx)
#    and `ja` (typsphinx-ja): root resolves to /en/stable/; stable version identifier matches;
#    both PDFs served as application/pdf.

# 3. GitHub Release body byte-identity check
uv run python scripts/extract_changelog_section.py vX.Y.Z > /tmp/expected-notes.md
gh release view vX.Y.Z --json body -q .body > /tmp/actual-notes.md
diff /tmp/expected-notes.md <(head -n "$(wc -l < /tmp/expected-notes.md)" /tmp/actual-notes.md)
# A non-empty diff is a hard failure, not a formatting difference.
```

**REL-09 verbatim-quote convention** (61-HANDOFF.md's "What this phase satisfied" section) — quote
the requirement's exact checkbox text out of `.planning/REQUIREMENTS.md`, not a paraphrase:
```markdown
**REL-09**, quoted verbatim from `.planning/REQUIREMENTS.md`:

> - [ ] **REL-09**: v0.9.2 released to PyPI with a curated `## [0.9.2]` CHANGELOG entry, ...
```

**D-14's four REL-04 items** must be recorded as a named sub-section (no direct 61 analog — 61
deferred this to 63 explicitly): (a) `create-release`'s `Install uv` steps ran green at real v0.8.0
and v0.9.0 tag pushes, so a failure now is a regression; (b) observe via `gh run watch` then read
the job conclusion literally; (c) fix-and-rerun inside this release work, never defer; (d) the todo
`2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` stays `pending/`, closed only by an
observed green `create-release` on a real tag push.

**D-15's approval-gate note:** name the `pypi` GitHub Environment's manual approval as an EXPECTED
gate, positioned in the handoff **before** the step that triggers it — a paused-for-approval run
looks identical to a failed one on a bare `gh run list` scan.

---

## Shared Patterns

### The one-commit version-literal lockstep (SC#1)
**Source:** `pyproject.toml` + `uv.lock` + `README.md` + `CHANGELOG.md`, every prior bump commit
(most recently the v0.9.0 bump).
**Apply to:** the single bump-plan.
```bash
git diff --name-only   # expect exactly: README.md pyproject.toml uv.lock CHANGELOG.md
                        # (+ tests/test_changelog_page_gate.py, D-11's tuple edit, per this phase)
```
All land in **one commit** — `git show --name-only` on it lists all five together.

### The closeout-guard checksum fence (D-16, REL-11)
**Source:** `61-CLOSEOUT-GUARD.md`, reused verbatim.
**Apply to:** every plan (frontmatter discipline) + the dedicated closeout-guard plan (baseline +
three re-verifications).
```bash
sha256sum .planning/REQUIREMENTS.md
wc -l .planning/REQUIREMENTS.md
git rev-parse HEAD
grep -n 'REL-09' .planning/REQUIREMENTS.md
```
Every plan's `SUMMARY.md` frontmatter must declare `requirements-completed: []` for REL-09 (Pitfall
1 — three of Phase 61's four plans got this wrong).

### The positive-control probe pattern (SC#5)
**Source:** `61-SC4-INVARIANTS.md` §§ "Remote tag probe (unfiltered, with positive control)",
"Publish probe".
**Apply to:** the SC#5-invariants plan, both observations.
Never trust a bare negative probe (`git ls-remote --tags origin 'v0.9.2'` alone) — always fetch
unfiltered and derive both a positive control (grep against `v0.9.0`, known to exist) and the
negative assertion (grep against `v0.9.2`, expect 0) from the same fetch.

### CI's lint authority, correctly named (D-18 amended)
**Source:** `.github/workflows/ci.yml:51-70` (job `lint`, display name `Lint and Format Check`,
step `Run lint with tox`) vs. `.github/workflows/release.yml:84` (step `Run linters`, a different
workflow this phase must never trigger).
**Apply to:** the CI-dispatch plan and any plan reading a lint verdict.
```bash
gh run view <id> --json jobs   # find job "Lint and Format Check"; read its conclusion
```

### Clean-build docs warning baseline (D-21)
**Source:** repeat finding across `61-CHANGELOG-EVIDENCE.md` § "Docs render" and this project's own
`docs-warning-baseline-needs-clean-build` lesson.
**Apply to:** the green-tree-evidence plan.
```bash
rm -rf docs/_build && uv run tox -e docs-html
rm -rf docs/_build && uv run tox -e docs-pdf
```
Cite the fresh `build succeeded, N warnings.` line; do not assert "matches the 3/5 baseline" without
a fresh transcript.

## No Analog Found

None — every file this phase creates or edits has a direct, same-kind analog from Phase 57 and/or
Phase 61.

## Metadata

**Analog search scope:** `pyproject.toml`, `README.md`, `uv.lock`, `CHANGELOG.md`,
`tests/test_changelog_page_gate.py` (via `git log -p`); `.planning/milestones/v0.9.1-phases/61-*`
and `.planning/milestones/v0.9.0-phases/57-*` evidence/handoff files (via `Read` + `grep -n '^#'`
section-skeleton extraction).
**Files scanned:** ~14 (5 repo files' git history + 6 evidence/handoff analog files + CHANGELOG.md
itself, read directly).
**Pattern extraction date:** 2026-08-30
