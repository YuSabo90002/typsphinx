---
phase: 53-template-registry-foundation
verified: 2026-08-15T12:57:14Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 4/5
  gaps_closed:
    - "SC#5 — Milestone branch on origin with a completed 3-OS CI run over the code actually shipping. Branch re-pushed 48c957cd..35ee8a0e; fresh workflow_dispatch run 31884774067 completed 12/12 jobs success, including both windows-latest and both macos-latest Test Python legs. Re-measured this session: `git log 35ee8a0e..HEAD -- typsphinx/ tests/` is EMPTY — every commit after the certified head touches only `.planning/`, so the CI evidence still certifies the current shipping code."
  gaps_remaining: []
  regressions: []
deferred: []
---

# Phase 53: Template Registry Foundation Verification Report

**Phase Goal:** `typst_document_templates` exists as a validated, resolved-once-per-build data
structure, and `render_wrapper()` builds its `TemplateEngine` from the resolved definition
instead of reading `typst_template` / `typst_package` / `typst_template_function` straight off
`config` — but the built-in `"typst"` key synthesizes exactly those same global values, so this
phase changes no output.
**Verified:** 2026-08-15T12:57:14Z
**Status:** passed
**Re-verification:** Yes — after second gap-closure round (plans 53-08, 53-09, 53-10)

## Goal Achievement

### Observable Truths

| # | Truth (ROADMAP Success Criterion) | Status | Evidence |
|---|---|---|---|
| 1 | **SC#1** — Named template definitions are declarable and resolve once per build (TPL-01, TPL-05); params-exclusivity intact | ✓ VERIFIED | Re-measured live at HEAD `611382b7`: two `typst_documents` entries naming the same registered key resolve to the identical `TemplateRegistryEntry` object (`r1 is r2 → True`, direct `resolve_registry_key()` call). `resolve_template_registry()` unchanged in this area by 53-08/53-09/53-10 (53-08 only adds validation guards, 53-09/53-10 change no code). |
| 2 | **SC#2** — Untouched `conf.py` produces byte-identical output, proven by identity (TPL-03, TPL-04) | ✓ VERIFIED | Re-built `tests/fixtures/conf14_prewrite_control_gate` live this session: exit 0, exactly the six expected `.typ` files (`_template.typ`, `four.typ`, `four_out.typ`, `five.typ`, `five_out.typ`, `index.typ`). Full suite green (1270 passed, 5 skipped, 0 failed) confirms no output-shape regression from 53-08/53-09/53-10, none of which touch `render_wrapper()`/`write_doc()`/`prepare_writing()`. |
| 3 | **SC#3** — Every malformed registry stops the build with a message naming the specific reason; CONF-14/15/16/17 each fire once per build, order-independently, before any output is written | ✓ VERIFIED (literal ROADMAP enumeration, and now the module's whole input surface) | Live-reproduced this session via real `sphinx-build -b typst` subprocess: a truthy non-`dict` `typst_document_templates` (`["a", "b"]`) raises `typst_document_templates must be a dict mapping registry key to definition, got ['a', 'b']` from `resolve_template_registry()` and `find <outdir> -name '*.typ'` is EMPTY — zero files written. Also live-confirmed the WR-02 field-level guard (`resolve_template_registry()` over `{"k": {"template": ["a","b"]}}` raises `... must be a path string ...`). Both are the two prior-round ⚠ WARNING anti-patterns (WR-01/WR-02), now closed by plan 53-08. The prior round's CONF-14 gap (order-dependent partial output) remains closed — unchanged code path, re-confirmed by the unmodified test suite (`tests/test_registry_prewrite_validation_gate.py`, 10 tests, all passing). |
| 4 | **SC#4** — Registry-key shape validated as single path segment; wrong guard (`_escapes_outdir`/`_is_drive_qualified`) not reused; case-collision routed through `_collision_key()` | ✓ VERIFIED | `_KEY_SHAPE_REJECTION_CASES` still exactly 7 distinct entries (re-measured live this session). `_has_case_collision()` still imports and calls `TypstBuilder._collision_key()` directly. Untouched by 53-08/53-09/53-10 (none of their `files_modified` includes this validator). |
| 5 | **SC#5** — Milestone branch on `origin` with a completed 3-OS CI run over the code actually shipping | ✓ VERIFIED | `git ls-remote --heads origin gsd/v0.9.0-per-document-templates` → `35ee8a0e` (re-measured this session). Run `31884774067` (`workflow_dispatch`, headSha `35ee8a0e`) completed `success` on all 12 jobs, including both `windows-latest` and both `macos-latest` `Test Python …` legs (re-confirmed via `gh run view 31884774067 --json jobs` in `53-CI-EVIDENCE.md`, and CI run details supplied to this session independently agree). **Currency re-checked, not trusted:** `git log 35ee8a0e..HEAD -- typsphinx/ tests/` is EMPTY this session (HEAD is `611382b7`, seven commits ahead of the certified SHA, every one of them touching only `.planning/` — `docs(phase-53): update tracking after wave 8`, a worktree merge, `53-10-SUMMARY.md`/self-check commits, and `docs(53): add code review report`). The prior round's gap (evidence stale relative to `8f638768`, missing three `typsphinx/`+`tests/` commits) is closed: the branch was re-pushed to the wave-8 tip and a fresh CI run dispatched and captured over it. |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `typsphinx/template_registry.py` | WR-01 container-shape guard + WR-02 template-field guard (53-08) | ✓ VERIFIED (present, substantive, wired) | Container guard at line ~301-304 (`if not isinstance(declared, dict): raise ExtensionError(...)`), placed between `declared = getattr(...) or {}` and the `all_keys` comprehension. Field guard at line ~408 (`if template and not isinstance(template, (str, os.PathLike)): failures.append(...)`), joining the accumulate-then-raise-once `failures` list. Both confirmed by direct read and by two independent live reproductions this session (unit call + real `sphinx-build` subprocess). |
| `tests/test_registry_container_shape_gate.py` | WR-01 subprocess + unit gate coverage (53-08) | ✓ VERIFIED | 9 tests, all passing, re-run this session, including under `LC_ALL=C`. |
| `tests/test_template_registry.py` | WR-02 + prior coverage | ✓ VERIFIED | 76 tests, all passing (67 baseline + 9 from 53-08's WR-02 closure), re-run this session under both ambient and `LC_ALL=C` locales. |
| `.planning/REQUIREMENTS.md` | TPL-01/TPL-05/CONF-16 tracking correction (53-09) | ✓ VERIFIED | Re-grepped this session: all 9 Phase 53 requirement IDs (TPL-01, TPL-03, TPL-04, TPL-05, CONF-14, CONF-15, CONF-16, CONF-17, CONF-18) now read `Complete` in the traceability table; checkbox list correspondingly `[x]`. Prior round's stale-tracking WARNING closed. |
| `.planning/phases/53-.../53-CI-EVIDENCE.md` | SC#5 branch-push + fresh CI-run evidence (53-10) | ✓ VERIFIED | "Gap-closure round 2" section records the re-push (`48c957cd..35ee8a0e`), run `31884774067` (12/12 success), and a three-fact currency assertion (remote agreement, empty staleness log, positive content grep). Currency independently re-confirmed this session against the actual current HEAD, not just the artifact's own recorded moment. |
| `.planning/phases/53-.../53-REVIEW.md` | Fresh code review after 53-08 | ✓ VERIFIED | Dated this round, 24 files reviewed, 0 Critical / 0 Warning / 2 Info, status `clean`. Both Info items (IN-01 package-field type validation — owner-declined; IN-02 a comment-accuracy nit) are non-blocking and do not reopen SC#3. |
| `.planning/phases/53-.../53-08-RED-EVIDENCE.md` | Pre-fix WR-01/WR-02 transcripts | ✓ VERIFIED (exists) | Present on disk, referenced by 53-08-SUMMARY.md. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `builder.write()` | `resolve_template_registry()` | `self._document_template_registry = resolve_template_registry(...)` at line ~802 | ✓ WIRED | Confirmed by direct read this session: sits after `_validate_output_path_collisions()`, before `_validate_registry_key_references()` and `prepare_writing()`. Unchanged by 53-08/53-09/53-10. |
| `builder.write()` | `_validate_registry_key_references()` | Line ~813, between the registry assignment and `prepare_writing()` | ✓ WIRED | Confirmed by direct read; unchanged this round. |
| `resolve_template_registry()` | container/field type guards | Guards sit pre-accumulation (container) and inside the accumulate loop (field), both reachable before `prepare_writing()` runs | ✓ WIRED | Live-proven this session: a truthy non-`dict` container reaches `resolve_template_registry()` via a real `sphinx-build` and raises before any `.typ` file is written (`find` on the build dir is empty post-failure). |
| `render_wrapper(template_entry=...)` | `TemplateEngine(...)` | `writer.py` | ✓ WIRED | No plan in this round (53-08/53-09/53-10) touches `writer.py`; unchanged from the prior verification's confirmed wiring. |

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| TPL-01 | 53-02, 53-03, 53-08, 53-09 | ✓ SATISFIED | Named definitions accepted, shared-key identity live-confirmed this session (`r1 is r2 → True`). REQUIREMENTS.md now `Complete` (re-grepped this session). |
| TPL-03 | 53-01, 53-02, 53-04, 53-05, 53-10 | ✓ SATISFIED | REQUIREMENTS.md `Complete`. SC#2 byte-identity re-confirmed this session via the control fixture. |
| TPL-04 | 53-01, 53-02, 53-05, 53-06, 53-10 | ✓ SATISFIED | REQUIREMENTS.md `Complete`. Absent element [4] == explicit `"typst"`, unchanged this round. |
| TPL-05 | 53-02, 53-03, 53-09 | ✓ SATISFIED | Shared key resolves to one object, live-confirmed this session. REQUIREMENTS.md now `Complete`. |
| CONF-14 | 53-03, 53-06, 53-10 | ✓ SATISFIED | REQUIREMENTS.md `Complete`. Fires once-per-build, order-independently, zero partial output — unchanged this round; re-confirmed by the unmodified `tests/test_registry_prewrite_validation_gate.py` (10 passing). |
| CONF-15 | 53-03, 53-07, 53-08, 53-10 | ✓ SATISFIED | REQUIREMENTS.md `Complete`. `template`+`package` both-set rejected up front; a bad-typed `template` alongside a CONF-15 both-set failure reports both in one raise (D-09), live-confirmed by test. |
| CONF-16 | 53-03, 53-09 | ✓ SATISFIED | REQUIREMENTS.md now `Complete`. User-declared `"typst"` rejected up front, unchanged this round. |
| CONF-17 | 53-03, 53-07, 53-08, 53-10 | ✓ SATISFIED | REQUIREMENTS.md `Complete`. Parent-is-srcdir/ancestor rejected; cross-drive `ValueError` caught (53-07); a non-consumable `template` type now also rejected pre-`os.path.join` (53-08 WR-02). |
| CONF-18 | 53-03, 53-07, 53-08, 53-10 | ✓ SATISFIED | REQUIREMENTS.md `Complete`. Exactly 7 denylist cases (re-measured this session); case-collision via `_collision_key()`. |

No orphaned requirements — all 9 IDs ROADMAP maps to Phase 53 appear in at least one plan's
`requirements` field, and REQUIREMENTS.md's traceability table lists all 9 as `Complete`.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `typsphinx/template_registry.py` | 101-134 (`_validate_registry_key_shape`) | A bare Windows drive-qualified key (e.g. `"C:"`) is accepted, unrejected | ℹ️ INFO — NOT a gap | Unchanged. Deliberately out of scope: `53-CONTEXT.md`'s "Deferred Ideas" locks `< > : " \| ? *` as accepted in Phase 53 by design (`53-REVIEW.md` CR-01, carried forward). |
| `typsphinx/template_registry.py` | ~369, ~451-456 (`package` field) | The `package` field is never type-validated; a non-`str` value silently f-string-interpolates into `#import "{value}"`, producing syntactically valid but semantically nonsensical Typst | ℹ️ INFO — NOT a gap | This round's `53-REVIEW.md` IN-01. **Reviewed and explicitly declined by the project owner this round** (per phase task instructions and ROADMAP § Phase 53 "Plans": "`53-REVIEW.md` IN-01 was reviewed and declined by the owner and is deliberately unplanned"). Not scored as a gap. |
| `typsphinx/template_registry.py` | 380-407 | This round's `53-REVIEW.md` IN-02: a comment inaccurately calls two sibling `if` statements an `elif` relationship | ℹ️ INFO — NOT a gap | Documentation-precision nit only; no behavioral impact, confirmed by the reviewer and independently re-read this session (the code IS two independent `if` statements, and the described *behavior* — CONF-15 still firing for the same key regardless — is correct and test-proven). |

No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers found in any file modified by this
phase (re-scanned `builder.py`, `template_registry.py`, `writer.py`, `template_engine.py` this
session).

The two prior-round ⚠ WARNING rows (WR-01 non-`dict` container `AttributeError`; WR-02 non-`str`
`template` field `TypeError`) and the REQUIREMENTS.md tracking-stale WARNING are all closed this
round — none remain in this table.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full test suite | `uv run pytest tests/ -q` | `1270 passed, 5 skipped in 109.29s` | ✓ PASS |
| `black --check .` | `uv run black --check .` | `310 files would be left unchanged` | ✓ PASS |
| `ruff check .` | `uv run ruff check .` | `All checks passed!` | ✓ PASS |
| `mypy typsphinx/` | `uv run mypy typsphinx/` | `Success: no issues found in 7 source files` | ✓ PASS |
| WR-01 live e2e reproduction | real `sphinx-build -b typst` over a truthy non-`dict` `typst_document_templates` fixture | Non-zero exit; `ExtensionError: typst_document_templates must be a dict mapping registry key to definition, got ['a', 'b']`; `find <outdir> -name '*.typ'` → empty | ✓ PASS (gap closed) |
| WR-02 live unit reproduction | `resolve_template_registry()` over `{"k": {"template": ["a","b"]}}` | `ExtensionError: ... must be a path string ...` | ✓ PASS (gap closed) |
| SC#1 shared-key identity | direct `resolve_registry_key()` call, two entries naming the same key | `r1 is r2 → True` | ✓ PASS |
| SC#2 control fixture (no-op) | live build of `conf14_prewrite_control_gate` | Exit 0; exactly the 6 expected `.typ` files | ✓ PASS |
| SC#4 denylist count | `len(_KEY_SHAPE_REJECTION_CASES)` | `7`, all distinct | ✓ PASS |
| `tests/test_registry_container_shape_gate.py` + `tests/test_template_registry.py`, ambient and `LC_ALL=C` | `uv run pytest ...` | 85 passed both ways | ✓ PASS |
| SC#5 branch currency | `git ls-remote --heads origin` + `git log 35ee8a0e..HEAD -- typsphinx/ tests/` | `35ee8a0e` on origin; empty diff (HEAD is 7 commits ahead, all `.planning/`-only) | ✓ PASS |
| SC#5 CI run | 53-CI-EVIDENCE.md run `31884774067` cross-referenced | 12/12 jobs `success`, including both `windows-latest`/`macos-latest` `Test Python` legs | ✓ PASS |
| Fresh code review this round | `53-REVIEW.md` | 24 files, 0 Critical / 0 Warning / 2 Info, status `clean` | ✓ PASS |

### Human Verification Required

None. Every truth was resolvable programmatically (code read + live reproduction via real
`sphinx-build` subprocess and direct function calls), including the CI/branch evidence for SC#5,
which was independently re-measured against `git`/`git ls-remote` this session rather than trusted
from the artifact or from the orchestrator's supplied measurements.

### Gaps Summary

**All five ROADMAP Success Criteria are met on measured, independently re-verified evidence.**

This is the third verification pass on Phase 53. The first found SC#3 order-dependent (closed by
53-06). The second (`344b9510`) found SC#3 closed but flagged two new robustness gaps (WR-01/WR-02,
recorded as ⚠ WARNING) plus a stale-tracking WARNING and a stale SC#5 (CI evidence 17 commits
behind HEAD, missing three production commits). This round's three gap-closure plans addressed
each independently, and all three are confirmed closed by this session's own measurements, not by
transcribing SUMMARY.md claims:

- **WR-01/WR-02 (53-08):** both re-reproduced live this session via a real `sphinx-build`
  subprocess (WR-01) and a direct unit call (WR-02) — both now raise this module's own
  `ExtensionError`, never a raw `AttributeError`/`TypeError`. The WR-01 build left zero `.typ`
  files on disk, preserving the same pre-`prepare_writing()` zero-output guarantee CONF-14 already
  has.
- **REQUIREMENTS.md tracking (53-09):** re-grepped this session — all 9 Phase 53 requirement IDs
  read `Complete` in both the checkbox list and the traceability table, with no orphans.
- **SC#5 staleness (53-10):** the branch was re-pushed to `35ee8a0e` and a fresh 3-OS CI run
  (`31884774067`) dispatched and captured, all 12 jobs `success`. This session independently
  re-ran `git log 35ee8a0e..HEAD -- typsphinx/ tests/` against the actual current HEAD
  (`611382b7`, which includes this round's own code-review commit) and found it empty — every
  commit since the certified SHA touches only `.planning/`, so the CI evidence remains current at
  the moment of this verification, not merely at the moment the evidence artifact was written.

The fresh `53-REVIEW.md` for this round found zero Critical and zero Warning findings (2 Info
only): IN-01 (the `package` field's missing type validation) was explicitly reviewed and declined
by the project owner as out of scope, and IN-02 is a non-behavioral comment-accuracy nit. Neither
reopens any Success Criterion.

**No gaps remain.** Phase 53's goal is achieved: `typst_document_templates` is a validated,
resolved-once-per-build registry; malformed input across its entire measured surface (not just
the four literally-enumerated CONF-14/15/16/17 cases, but also the container-shape and
`template`-field robustness classes found in review) stops the build with a specific, actionable
message before any output is written; and an untouched `conf.py` still produces byte-identical
output. Phase 53 is ready to close and Phase 54 is unblocked.

---

_Verified: 2026-08-15T12:57:14Z_
_Verifier: Claude (gsd-verifier)_
