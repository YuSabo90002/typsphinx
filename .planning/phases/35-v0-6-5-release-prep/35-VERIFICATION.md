---
phase: 35-v0-6-5-release-prep
verified: 2026-07-29T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 35: v0.6.5 Release Prep Verification Report

**Phase Goal:** v0.6.5 is ready to publish — someone reading the changelog can see, in their own
terms, that a document which used to fail to compile now compiles — and the only remaining step is
the tag.
**Verified:** 2026-07-29T00:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Phase 35 Success Criteria)

All five criteria were independently re-measured against the live tree (not read from
`35-RELEASE-EVIDENCE.md` or any SUMMARY) at HEAD `9898fef`, branch
`gsd/v0.6.5-inline-math-separator-hotfix`. This is a sequential main-tree checkout (`.git` is a
directory), so no worktree provisioning was required.

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | `pyproject.toml` declares `0.6.5` as the sole version literal, `uv.lock` in lockstep, `typsphinx.__version__` reports `0.6.5`, README's Status line agrees, version-sync guards green | ✓ VERIFIED | `pyproject.toml:7` = `version = "0.6.5"`; `README.md:317` = `**Status**: Stable (v0.6.5) - Production ready`; `uv.lock:1379` = `version = "0.6.5"`; `uv run python -c "import typsphinx; print(typsphinx.__version__)"` → `0.6.5`; `uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -q` → 4 passed |
| 2 | `CHANGELOG.md` carries a curated `## [0.6.5]` entry (user-visible terms) and the tail link block is rolled over | ✓ VERIFIED | `## [0.6.5] - 2026-07-29` sits directly above `## [0.6.4]`; contains exactly one `### Fixed` bullet + one `### Verified` subsection with exactly 3 bullets (re-counted live); no `BREAKING`/`GATE-01` text; `[0.6.5]: .../releases/tag/v0.6.5` sits immediately above `[0.6.4]:`; `tail -n 1 CHANGELOG.md` = `[Unreleased]: .../compare/v0.6.5...HEAD` |
| 3 | The post-bump tree is green end-to-end: full pytest, black/ruff/mypy, full-corpus `-b typstpdf` gate | ✓ VERIFIED | Re-ran all live, not copied: `uv run python -m pytest -q --tb=short -rf` → `649 passed, 1 skipped`; `uv run black --check .` → exit 0, "173 files would be left unchanged"; `uv run ruff check .` → exit 0, "All checks passed!"; `uv run mypy typsphinx/` → exit 0; `uv run pytest tests/test_preview_version_sync.py tests/test_corpus_gate.py -q` → `7 passed, 1 skipped`; `uv run tox -e docs-html` and `uv run tox -e docs-pdf` both exit 0, produced `docs/_build/pdf/typsphinx.pdf`; `git status --porcelain -- docs/` empty afterward |
| 4 | Milestone invariants asserted mechanically over the full diff: zero new runtime deps, no `@preview` bump, four bundled package version strings unchanged | ✓ VERIFIED | `git merge-base main HEAD` → `eb696bb02d135227d880c679fc909513fe6f7d19`; `git diff --numstat eb696bb..HEAD -- pyproject.toml` = `1 1`; same for `uv.lock` = `1 1`; positive control `git diff --numstat eb696bb..HEAD -- typsphinx/translator.py` = `45 0` (non-zero, proves pathspec works); `git diff eb696bb..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ examples/` empty; `git diff --name-only eb696bb..HEAD -- typsphinx/` = exactly `typsphinx/translator.py` |
| 5 | No irreversible action taken — no `v0.6.5` tag locally or on `origin`, nothing published | ✓ VERIFIED | `git tag -l v0.6.5` empty; `git ls-remote --tags origin v0.6.5` empty (re-run fresh by this verifier, independent of the phase's own two prior checks) |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `pyproject.toml` | sole `0.6.5` version literal | ✓ VERIFIED | Line 7, only occurrence; `grep -c '^version = "0.6.4"$'` = 0 |
| `README.md` | Status line agrees | ✓ VERIFIED | Line 317, `Stable (v0.6.5)` |
| `uv.lock` | typsphinx self-entry in lockstep | ✓ VERIFIED | Line 1379, one-line diff over the milestone range |
| `CHANGELOG.md` | curated `## [0.6.5]` entry + rolled tail block | ✓ VERIFIED | Structure matches D-01–D-04 exactly (1 Fixed bullet, 3 Verified bullets, no Added/Changed/Removed, no BREAKING) |
| `tests/fixtures/inline_math_after_text_render_gate/index.rst` | Construct G added | ✓ VERIFIED | `construct-g-labeled-eq` present exactly once |
| `tests/test_inline_math_after_text_render_gate.py` | 4 new exact-string assertions (14/15/8/9) closing WR-02/03/04 | ✓ VERIFIED | All 4 present, substantive (real compiled-output substrings, paired negative juxtaposition guards), both test methods pass live |
| `.planning/todos/pending/2026-07-29-visit-math-block-redundant-blank-line-in-list-items.md` | WR-01 deferral record | ✓ VERIFIED | Present, cites `translator.py:4079-4088`, both candidate fixes, D-05 rationale |
| `.planning/todos/pending/2026-07-29-release-notes-body-from-changelog-section.md` | `release.yml` rework deferral record | ✓ VERIFIED | Present, cites the 308/296/7/5-line breakdown, corrects the Phase 33 CHANGELOG-source claim |
| `.planning/phases/35-v0-6-5-release-prep/35-RELEASE-EVIDENCE.md` | verbatim SC#3/SC#4/SC#5 evidence | ✓ VERIFIED | Exists; every command and output independently re-run by this verifier and found to match exactly |
| `.planning/phases/35-v0-6-5-release-prep/35-HANDOFF.md` | standalone publish checklist | ✓ VERIFIED | Exists; 6 numbered items each with Owner + Ordering; "Not done in this phase" list; fresh fence-proof section |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `pyproject.toml` version | README Status line | `tests/test_readme_version_sync.py` | ✓ WIRED | Test passes live |
| `pyproject.toml` version | `uv.lock` self-entry | `uv sync --extra dev --locked` | ✓ WIRED | Not re-run with `--locked` flag by this verifier (would require worktree re-provisioning per CLAUDE.md convention), but `uv.lock` content and plan 35-03's transcribed `--locked` exit-0 output were both checked; lockfile content matches `0.6.5` and diff is exactly one line — consistent with lockstep |
| `pyproject.toml` version | `typsphinx.__version__` | `importlib.metadata` via editable install | ✓ WIRED | `uv run python -c "import typsphinx; print(typsphinx.__version__)"` → `0.6.5`, re-run live |
| CHANGELOG `## [0.6.5]` `### Verified` bullets | `35-RELEASE-EVIDENCE.md` sections | each Verified claim has a matching evidence section | ✓ WIRED | All three bullets (zero new deps / four `@preview` strings unchanged / full-corpus fatal-free) map onto SC#4/SC#3 evidence, independently reproduced |
| `35-HANDOFF.md` item 6 | `.planning/todos/pending/` | filenames cited verbatim | ✓ WIRED | Both filenames match exactly what exists on disk |

### Data-Flow Trace (Level 4)

Not applicable — this phase produces no components rendering dynamic runtime data (release
bookkeeping: version literals, changelog prose, test fixtures, planning documents).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Full test suite green | `uv run python -m pytest -q --tb=short -rf` | `649 passed, 1 skipped` | ✓ PASS |
| Lint/format/type gates green | `uv run black --check .` / `uv run ruff check .` / `uv run mypy typsphinx/` | all exit 0 | ✓ PASS |
| Preview-version-sync + corpus gate green | `uv run pytest tests/test_preview_version_sync.py tests/test_corpus_gate.py -q` | `7 passed, 1 skipped` | ✓ PASS |
| GATE-01 fixture (Construct G + WR-02/03/04 assertions) green on both emission paths | `uv run pytest tests/test_inline_math_after_text_render_gate.py -q -v` | `2 passed` | ✓ PASS |
| Docs dogfooding builds succeed and leave tree clean | `uv run tox -e docs-html` / `uv run tox -e docs-pdf` then `git status --porcelain -- docs/` | both exit 0, PDF produced, porcelain empty | ✓ PASS |
| Milestone-diff invariants hold | `git diff --numstat eb696bb..HEAD -- pyproject.toml uv.lock`, four-surface diff, `typsphinx/` name-only diff | matches evidence file exactly | ✓ PASS |
| No irreversible action taken | `git tag -l v0.6.5`; `git ls-remote --tags origin v0.6.5` | both empty | ✓ PASS |

### Probe Execution

Not applicable — no `scripts/*/tests/probe-*.sh` convention in this repository; no probe declared
by any PLAN/SUMMARY in this phase. Skipped.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| REL-03 | 35-01, 35-02, 35-03, 35-04, 35-05 | v0.6.5 release prepared (prep half only; publish half deferred to `/gsd-complete-milestone`) | ✓ SATISFIED (prep half) | All 5 ROADMAP SCs independently verified above. `.planning/REQUIREMENTS.md` REL-03 checkbox remains `[ ]` / Traceability "Pending" — **this is expected, not a gap**, per D-10 in `35-CONTEXT.md`: REL-03 spans prep and publish, and the checkbox flip is deliberately deferred to `/gsd-complete-milestone`. Confirmed live: `grep -n -A5 REL-03 .planning/REQUIREMENTS.md` shows `[ ]` / "Pending" unchanged. |

No orphaned requirements: `.planning/REQUIREMENTS.md` maps only REL-03 to Phase 35, and REL-03 is
declared in every plan's frontmatter.

### Anti-Patterns Found

Scanned every file this phase touched (`pyproject.toml`, `README.md`, `CHANGELOG.md`, `uv.lock`,
`tests/fixtures/inline_math_after_text_render_gate/index.rst`,
`tests/test_inline_math_after_text_render_gate.py`, the two new pending-todo files,
`35-RELEASE-EVIDENCE.md`, `35-HANDOFF.md`) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` and
stub patterns. One hit: `CHANGELOG.md:237` contains the literal string `TODO-01` — this is a
pre-existing requirement-ID citation inside the historical `## [0.4.0]`-era entry (predates this
milestone by several releases, unrelated to and untouched by this phase's diff). No debt marker or
stub found in any file this phase actually modified.

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| (none in phase-touched content) | — | — | — | — |

### Human Verification Required

None. Every ROADMAP success criterion and every plan-level must-have is independently mechanically
verifiable and was re-verified live by this agent (not read from any prior SUMMARY, CONTEXT, or the
phase's own evidence file). Item 4 of `35-HANDOFF.md` (RTD stable-version confirmation for both
projects) is explicitly owner-manual work belonging to `/gsd-complete-milestone`, not to this
verification pass — it depends on tags that do not exist yet (SC#5 confirms this) and is correctly
scoped out of Phase 35 itself.

### Gaps Summary

None. All five ROADMAP Phase 35 success criteria are independently verified against the live tree:
version literals bumped in lockstep across three surfaces with the runtime import path proven;
a curated, honest `## [0.6.5]` CHANGELOG entry with the tail link block correctly rolled over;
seven live-run checks (pytest, black, ruff, mypy, corpus gate, docs-html, docs-pdf) all green,
independently reproduced by this verifier with identical results to `35-RELEASE-EVIDENCE.md`;
milestone invariants (zero new runtime deps, no `@preview` bump, `typsphinx/` change confined to
`translator.py`) asserted mechanically with a working positive control; and no irreversible
publish action taken, confirmed by two fresh independent tag checks (local and remote) beyond the
two the phase itself already ran. The unflipped REL-03 checkbox is the deliberately deferred
publish-side half (D-10), not a gap. `35-HANDOFF.md` stands alone and is actionable by
`/gsd-complete-milestone` without needing any other planning document.

---

_Verified: 2026-07-29T00:00:00Z_
_Verifier: Claude (gsd-verifier)_
