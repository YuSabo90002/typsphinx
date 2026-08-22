---
phase: 57-v0-9-0-release-prep-prep-only
verified: 2026-08-22T07:26:24Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 57: v0.9.0 Release Prep (prep-only) Verification Report

**Phase Goal:** The v0.9.0 tree is bumped, its CHANGELOG curated, its claims re-proven on live runs
against the bumped tree, and handed off — with zero irreversible action. No tag, local or remote;
no publish; no GitHub Release. REL-08 closes at `/gsd-complete-milestone`, not in this phase — it
is held at `[ ]` through every plan.

**Verified:** 2026-08-22T07:26:24Z
**Status:** passed
**Re-verification:** No — initial verification

All evidence below comes from commands I re-ran myself against the checked-out tree
(`gsd/v0.9.0-per-document-templates`, HEAD `b55d4685`), plus independent `gh run view` calls
against GitHub Actions — not from transcribing `*-SUMMARY.md` or `*-EVIDENCE.md` prose. Where a
plan's evidence file is cited, it is because I re-ran the same command and got the same result.

## Goal Achievement

### Observable Truths (mapped to ROADMAP Success Criteria)

| # | Truth (ROADMAP SC) | Status | Evidence |
|---|---|---|---|
| 1 | SC#1 — Version moves atomically to 0.9.0 across manifest/lock/README; editable-install metadata regenerated; version-sync guards green | ✓ VERIFIED | `pyproject.toml:7` = `version = "0.9.0"`; `README.md:347` = `**Status**: Stable (v0.9.0)`; `uv.lock:1467` first-party `typsphinx` block = `version = "0.9.0"`; `uv run python -c "import typsphinx; print(typsphinx.__version__)"` → `0.9.0`; `uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py` → 5 passed |
| 2 | SC#2 — CHANGELOG `## [0.9.0]` curated, exactly 4 Breaking bullets each with migration sentence, tail link block rolled over | ✓ VERIFIED | `CHANGELOG.md` `## [0.9.0]` lead paragraph names `typst_document_templates` registry as headline and states the additive non-breaking case; exactly 4 `**Breaking` bullets counted (2 under `### Changed` promoted from Unreleased + 1 new `### Changed` bundle-relocation bullet + 1 `### Removed` `typst_template_assets` bullet), each with its own migration sentence; tail block: `[0.9.0]` tag line is topmost, `[Unreleased]` compare base reads `v0.9.0...HEAD`; `uv run python scripts/extract_changelog_section.py 0.9.0` exits 0 with 123 non-empty lines, `... 99.99.99` exits 1 |
| 3 | SC#3 — Bumped tree proven green on LIVE runs: full pytest, black/ruff/mypy, both docs tox envs, real multi-template `-b typstpdf` build producing two differently-typeset PDFs, built-wheel content check | ✓ VERIFIED | `uv run pytest -q` → 1425 passed, 1 skipped (skip is `tests/test_corpus_gate.py`'s documented env-gated case, `TYPSPHINX_CORPUS_REPORT=1` opt-in — quoted, not conflated with pass); `uv run black --check .` → all unchanged; `nix-shell -p ruff --run "ruff check ."` → All checks passed (NixOS ELF hazard avoided per known workaround); `uv run mypy typsphinx/` → Success; `uv run tox -e docs-html` → build succeeded, 3 warnings (matches recorded baseline); `uv run pytest tests/test_two_key_selection_gate.py` → 6 passed, 0 skipped, including `test_the_two_templates_produce_different_pdfs`; live `gh run view 32557477023` (independently dispatched, not the same call as the evidence file) → `conclusion: success`, 12/12 jobs `success` including both `windows-latest` lanes and the `Verify wheel carries the template bundle` step; local `uv build --wheel` + zipfile inspection confirms `typsphinx/templates/README.md` and `typsphinx/templates/base.typ` present in the wheel |
| 4 | SC#4 — Fence held: no local/remote v0.9.0 tag (probed twice, separated); no unintended `typsphinx/` change; REQUIREMENTS.md checksum matches phase-start baseline | ✓ VERIFIED | `git tag -l v0.9.0` → empty; `git ls-remote --tags origin v0.9.0` → empty (my own 3rd/4th independent observation, matching the 3 already recorded in `57-BUMP-EVIDENCE.md`, `57-SC4-INVARIANTS.md`, `57-HANDOFF.md`); `git diff --name-only 78bd595d..HEAD -- typsphinx/` → exactly `typsphinx/builder.py`, and that diff is confined to the three `!r`→explicit-quote message fixes described in the AMENDED 2026-08-17 block of `57-CONTEXT.md` (owner-approved, named exception) — no other `typsphinx/` file changed; `sha256sum .planning/REQUIREMENTS.md` → `503efc7ac...` matches `57-CLOSEOUT-GUARD.md`'s recorded baseline exactly; `.planning/REQUIREMENTS.md:128` REL-08 checkbox still `[ ]`, row 212 still `Pending` |
| 5 | SC#5 — Handoff checklist standalone and complete: every `/gsd-complete-milestone` step including second-repo's own `update-pin.yml` dispatch, RTD `stable` measurement for both projects, byte-identical Release body | ✓ VERIFIED | `57-HANDOFF.md` has 6 numbered checklist items, each with **Owner** and **Ordering**: (1) open/merge PR, (2) push release tag, (3) watch release workflow incl. human approval gate, (4) verify package index + GitHub Release with the byte-identity `diff` command against `scripts/extract_changelog_section.py 0.9.0`, (5) advance the second repo's pin via `gh workflow run update-pin.yml --repo YuSabo90002/typsphinx-doc-translations` (its OWN workflow, not a manual clone-edit-push) then tag separately, (6) measure RTD `stable` on both `typsphinx` (en) and `typsphinx-ja` projects via the public API. Also states "REL-08 remains open ... It closes at `/gsd-complete-milestone`, never here." |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `pyproject.toml` | version 0.9.0 | ✓ VERIFIED | line 7 |
| `README.md` | Status line 0.9.0 | ✓ VERIFIED | line 347 |
| `uv.lock` | first-party entry 0.9.0 | ✓ VERIFIED | line 1467 |
| `CHANGELOG.md` | `## [0.9.0]` curated section | ✓ VERIFIED | headline paragraph, 4 Breaking bullets, Removed shim note, Verified block unchanged (3 items) |
| `docs/source/changelog.rst` | `Migrating from 0.8.x to 0.9.0` guide | ✓ VERIFIED | present, most-recent-first |
| `tests/test_changelog_page_gate.py` | `RELEASE_VERSIONS` gains `"0.9.0"` | ✓ VERIFIED | line 65; gate green, 6 passed |
| `typsphinx/builder.py` | ONE owner-approved exception (repr-escaping fix) | ✓ VERIFIED | diff confined exactly to 3 message-construction sites, extracted to named helper functions; reviewed in `57-REVIEW.md` |
| `tests/test_templates_path_collision_gate.py` | separator-portable assertion + Windows-escaping regression guard | ✓ VERIFIED | 16 passed incl. `TestWindowsPathEscapingRegressionGuard` (4 tests) driving the real product functions directly |
| `57-HANDOFF.md` | standalone publish checklist | ✓ VERIFIED | 6 ordered items, owner+ordering, byte-identity check named |
| `57-CLOSEOUT-GUARD.md` | REQUIREMENTS.md checksum baseline | ✓ VERIFIED | digest matches live re-measurement |
| `57-CI-EVIDENCE-RUN3.md` | authority CI run 12/12 | ✓ VERIFIED | independently re-confirmed via `gh run view 32557477023` |
| `.planning/todos/pending/2026-08-17-repr-escaped-paths-...md` | WR-01/IN-01 filed forward | ✓ VERIFIED | extended 2026-08-22 with the code-review finding, not silently dropped |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `pyproject.toml` version | `typsphinx.__version__` | `uv sync` regenerated editable-install metadata | ✓ WIRED | `uv run python -c "..."` prints `0.9.0` |
| `CHANGELOG.md` `## [0.9.0]` | `release.yml`'s `validate`/`create-release` | `scripts/extract_changelog_section.py` | ✓ WIRED | exit 0 non-empty for `0.9.0`, exit 1 for absent version |
| `pyproject.toml` package-data glob | Build Package job's wheel-content step | `Verify wheel carries the template bundle` | ✓ WIRED | CI step `success`; local `uv build` + zipfile inspection confirms bundle files present |
| Wave-1 tip (bump+CHANGELOG+gate+guide) + 57-11 fix | dispatched `ci.yml` authority run | `gh workflow run ci.yml --ref ...` (`workflow_dispatch`, since branch is outside `push`/`pull_request` scope) | ✓ WIRED | run `32557477023`, headSha `fbbf48cd`, 12/12 success, confirmed live |
| `57-11`'s `builder.py` fix | `tests/test_templates_path_collision_gate.py` beta assertion | one native separator now supplied unescaped | ✓ WIRED | full suite green with zero test-file edits alongside the fix commit |
| 57-CONTEXT.md AMENDED block | SC#4 fence evaluation | names 57-08 and the phase verifier as intended readers | ✓ WIRED | read and applied in this verification; `typsphinx/` diff shows exactly the named exception and nothing else |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full local suite green | `uv run pytest -q` | 1425 passed, 1 skipped (documented env-gated skip) in 123.24s | ✓ PASS |
| black clean | `uv run black --check .` | 339 files unchanged | ✓ PASS |
| ruff clean | `nix-shell -p ruff --run "ruff check ."` | All checks passed | ✓ PASS |
| mypy clean | `uv run mypy typsphinx/` | Success, no issues in 8 source files | ✓ PASS |
| docs-html build | `uv run tox -e docs-html` | build succeeded, 3 warnings (matches recorded baseline) | ✓ PASS |
| Version-sync guards | `uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py` | 5 passed | ✓ PASS |
| Multi-template goal claim | `uv run pytest tests/test_two_key_selection_gate.py -v` | 6 passed, 0 skipped | ✓ PASS |
| CHANGELOG extractor, both directions | `uv run python scripts/extract_changelog_section.py 0.9.0` / `... 99.99.99` | exit 0 (123 lines) / exit 1 | ✓ PASS |
| Wheel carries template bundle (local) | `uv build --wheel` + zipfile namelist | `typsphinx/templates/README.md`, `typsphinx/templates/base.typ` present | ✓ PASS |
| Fence: no tag | `git tag -l v0.9.0` / `git ls-remote --tags origin v0.9.0` | both empty | ✓ PASS |
| Fence: typsphinx/ scope | `git diff --name-only 78bd595d..HEAD -- typsphinx/` | `typsphinx/builder.py` only | ✓ PASS |
| REQUIREMENTS.md checksum | `sha256sum .planning/REQUIREMENTS.md` | matches `57-CLOSEOUT-GUARD.md` baseline | ✓ PASS |

### CI Authority Run — Independent Re-confirmation

| Run | Command | Result | Status |
|---|---|---|---|
| Run 1 (pre-bump, `78bd595d`) | `gh run view 31956166848 --json conclusion,headSha` | `conclusion: failure`, `headSha: 78bd595d...` | matches recorded evidence |
| Run 2 (post-bump pre-fix, `bfcc6f6d`) | `gh run view 31959060298 --json conclusion,headSha` + jobs filter | `conclusion: failure`; failing jobs = both `windows-latest` lanes | matches recorded evidence |
| Run 3 (post-fix, `fbbf48cd`) | `gh run view 32557477023 --json conclusion,headSha,...` + full jobs list | `conclusion: success`; 12/12 `success` incl. both `windows-latest` lanes and `Verify wheel carries the template bundle` | matches recorded evidence — **authoritative for SC#3's toolchain half** |
| `fbbf48cd` → HEAD (`b55d4685`) diff | `git diff --name-only fbbf48cd..HEAD` | only `.planning/` files changed (tracking, HANDOFF, todo annotation) | confirms CI result still applies to the current tree |

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|---|---|---|---|---|
| REL-08 | 57-01 through 57-11 (all 11) | v0.9.0 published — closes at `/gsd-complete-milestone`, not this phase | ✓ SATISFIED (as a prep phase) | Requirement deliberately stays `[ ]`/Pending; confirmed by checksum-baseline match and live grep of REQUIREMENTS.md; this is the CORRECT outcome per the phase goal, not a defect |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s Traceability table maps only REL-08 to Phase 57, and all 11 plans declare `requirements: [REL-08]`.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `typsphinx/builder.py` (3 message-construction functions) | 329-402 | Explicit `'{value}'` quoting loses `repr()`'s automatic quote-disambiguation for a path containing a literal single quote | Warning (pre-existing code-review finding, not a new discovery) | Message-quality edge case only — refusal logic is unaffected. Already found and filed by `57-REVIEW.md` (WR-01/IN-01) and forwarded into `.planning/todos/pending/2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages.md` in the tree's last commit before this verification (`b55d4685`) — not silently dropped, does not block any ROADMAP SC |

No `TBD`/`FIXME`/`XXX` markers found in any file touched by this phase (`typsphinx/builder.py`, `CHANGELOG.md`, `docs/source/changelog.rst`, `tests/test_templates_path_collision_gate.py`, `tests/test_changelog_page_gate.py`).

### Human Verification Required

None. All 5 ROADMAP Success Criteria were independently re-measured against live commands (git, gh, pytest, black, ruff, mypy, tox, uv build) and each matched the recorded evidence. The publish steps themselves (PR merge, tag push, PyPI/GitHub Release, second-repo pin, RTD `stable`) are explicitly out of this phase's scope by design (SC#5's handoff describes them for `/gsd-complete-milestone`, and the fence proof confirms none of them were taken here) — they are not human-verification gaps in Phase 57, they are the next command's job.

### Gaps Summary

No gaps. All 5 must-haves verified against live re-runs, not SUMMARY narration:

- Version bump is atomic and propagates to the actual installed package metadata (not just the manifest literal).
- The CHANGELOG's `## [0.9.0]` section has the exact structure (4 Breaking bullets, correct headline framing, correct tail-link rollover) the plan mandated, verified by direct read and by running the extractor script itself.
- The bumped tree is proven green by re-running the full test suite, lint/format/type checks, both docs builds, the multi-template PDF gate, and the CI authority run — all independently re-executed or re-queried by this verifier, not copied from evidence files.
- The prep/publish fence holds: zero tags, and the only `typsphinx/` change across the whole phase is the one owner-approved, narrowly-scoped `builder.py` fix documented in the `57-CONTEXT.md` AMENDED block — confirmed by diffing from the phase-start SHA, not by trusting the AMENDED block's own narration.
- REL-08 is still open, matching the phase's explicit design intent (it closes at `/gsd-complete-milestone`), and the REQUIREMENTS.md checksum shows no accidental `phase.complete` auto-flip occurred anywhere across the phase's history.
- The single warning-level code-review finding (WR-01, a path-quoting edge case for embedded single quotes) was found, disclosed, and filed forward as a todo rather than silently shipped or silently dropped — consistent with this project's established deferral discipline.

---

_Verified: 2026-08-22T07:26:24Z_
_Verifier: Claude (gsd-verifier)_
