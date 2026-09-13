---
phase: "70"
slug: "typing-modernization-and-its-behaviour-identity-evidence"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-09-13"
validated: "2026-09-13"
---

# Phase 70 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Reconstructed by `/gsd-validate-phase 70` on 2026-09-13 from the 13 PLAN/SUMMARY pairs,
> the phase's `*-EVIDENCE.md` files, `70-VERIFICATION.md` and `70-UAT.md` (the seeded draft
> was an unfilled template).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml` `[tool.pytest.ini_options]`), plus ruff, black, mypy |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run ruff check .` (enforces QUA-09/QUA-11: `UP` selected, `UP006`/`UP035` no longer ignored) |
| **Full suite command** | `LC_ALL=C uv run pytest` + `uv run black --check .` + `uv run mypy typsphinx/` |
| **Estimated runtime** | Not re-measured in this audit; the D-05 golden corpus loop alone took ~39 s after (`CORPUS_FULL_SECONDS_AFTER`) |

---

## Sampling Rate

- **After every task commit:** each task's `<automated>` block (evidence-file key checks plus the gate quartet where the task converts code)
- **After every plan wave:** ruff + black + mypy + full pytest suite (`1547 passed 1 skipped`, collected 1548, before and after)
- **Before `/gsd-verify-work`:** full suite green on the tip, and a completed CI run (`RUN_ID = 34742047126`, `RUN_CONCLUSION = success`, `70-CI-EVIDENCE.md`)
- **Max feedback latency:** one task — every one of the 26 tasks carries an `<automated>` block

---

## Per-Task Verification Map

Nature of the phase: a behaviour-preserving annotation refactor. QUA-12 and DOC-23 are
**before/after measurements**, not persistent tests — their automated commands compare the
pre-conversion base against the converted tree and record a verdict key in an evidence file.
The standing regression guards after the phase are `ruff check .` (QUA-09, QUA-11) and the
existing pytest suite (behaviour).

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 70-01-01 | 01 | 1 | DOC-22 | — | N/A | doc check | 70-01 T1 `<automated>` → `70-DOC22-EVIDENCE.md` | ✅ | ✅ green |
| 70-01-02 | 01 | 1 | DOC-22 | — | N/A | lint/test neutrality | 70-01 T2 `<automated>` (ruff, pytest, pending-path census) | ✅ | ✅ green |
| 70-02-01 | 02 | 1 | QUA-09, QUA-12 | — | N/A | baseline census | 70-02 T1 `<automated>` → `70-BASELINE-EVIDENCE.md` (fresh UP006/UP035 count, mypy before) | ✅ | ✅ green |
| 70-02-02 | 02 | 1 | QUA-12 (b) | — | N/A | suite baseline | 70-02 T2 `<automated>` (`PYTEST_COLLECTED_BEFORE = 1548`, `1547 passed 1 skipped`) | ✅ | ✅ green |
| 70-03-01 | 03 | 1 | QUA-12 (d) | — | N/A | golden corpus base | 70-03 T1 `<automated>` → `70-CORPUS-DOCS-BASE-EVIDENCE.md` | ✅ | ✅ green |
| 70-03-02 | 03 | 1 | DOC-23 | — | N/A | docs build base | 70-03 T2 `<automated>` (clean docs-html + docs-pdf at base) | ✅ | ✅ green |
| 70-04-01 | 04 | 2 | QUA-11, QUA-12 (a) | — | N/A | masked-AST pilot | 70-04 T1 `<automated>` → `70-MASK-PILOT-EVIDENCE.md` | ✅ | ✅ green |
| 70-04-02 | 04 | 2 | QUA-11, QUA-12 (c,e) | — | N/A | gate quartet | 70-04 T2 `<automated>` (census, black, ruff, mypy SHA, pytest) | ✅ | ✅ green |
| 70-05-01 | 05 | 3 | QUA-11, QUA-12 (a) | — | N/A | masked-AST | 70-05 T1 `<automated>` → `70-CONV-BUILDER-EVIDENCE.md` | ✅ | ✅ green |
| 70-05-02 | 05 | 3 | QUA-11, QUA-12 (c,e) | — | N/A | gate quartet | 70-05 T2 `<automated>` | ✅ | ✅ green |
| 70-06-01 | 06 | 3 | QUA-11, QUA-12 (a) | — | N/A | masked-AST | 70-06 T1 `<automated>` → `70-CONV-TEMPLATE-EVIDENCE.md` | ✅ | ✅ green |
| 70-06-02 | 06 | 3 | QUA-11, QUA-12 (c,e) | — | N/A | gate quartet | 70-06 T2 `<automated>` | ✅ | ✅ green |
| 70-07-01 | 07 | 3 | QUA-11, QUA-12 (a) | — | N/A | masked-AST | 70-07 T1 `<automated>` → `70-CONV-WRITER-INIT-EVIDENCE.md` | ✅ | ✅ green |
| 70-07-02 | 07 | 3 | QUA-11, QUA-12 (c,e) | — | N/A | gate quartet + `@preview` byte-identity | 70-07 T2 `<automated>` | ✅ | ✅ green |
| 70-08-01 | 08 | 3 | QUA-11, QUA-12 (a) | — | N/A | masked-AST (tests/) | 70-08 T1 `<automated>` → `70-CONV-TESTS-EVIDENCE.md` | ✅ | ✅ green |
| 70-08-02 | 08 | 3 | QUA-12 (b,c) | — | N/A | assert-line census + suite | 70-08 T2 `<automated>` | ✅ | ✅ green |
| 70-09-01 | 09 | 4 | QUA-09, DOC-22 | — | N/A | ignore flip + todo move | 70-09 T1 `<automated>` → `70-FLIP-EVIDENCE.md` | ✅ | ✅ green |
| 70-09-02 | 09 | 4 | QUA-09 | — | N/A | gate quartet | 70-09 T2 `<automated>` (`MYPY_EXIT_FLIP = 0`, `1547 passed 1 skipped`) | ✅ | ✅ green |
| 70-10-01 | 10 | 5 | QUA-11, QUA-12 (a,c) | — | N/A | static after-side | 70-10 T1 `<automated>` → `70-AFTER-STATIC-EVIDENCE.md` (`LEG_A_EQUAL_COUNT = 10`, `LEG_C_ASSERT_LINES = 0`) | ✅ | ✅ green |
| 70-10-02 | 10 | 5 | QUA-09, QUA-12 (e), DOC-22 | — | N/A | mypy identity + commit order | 70-10 T2 `<automated>` (mypy stdout SHA identical) | ✅ | ✅ green |
| 70-11-01 | 11 | 5 | QUA-12 (b) | — | N/A | suite after-side | 70-11 T1 `<automated>` → `70-AFTER-RUNTIME-EVIDENCE.md` (`LEG_B_VERDICT = MET`) | ✅ | ✅ green |
| 70-11-02 | 11 | 5 | QUA-12 (d) | — | N/A | golden corpus byte-identity | 70-11 T2 `<automated>` (`LEG_D_VERDICT = MET`) | ✅ | ✅ green |
| 70-12-01 | 12 | 5 | DOC-23 | — | N/A | A/B/C docs builds | 70-12 T1 `<automated>` → `70-DOCS-DIFF-EVIDENCE.md` (A/B control empty) | ✅ | ✅ green |
| 70-12-02 | 12 | 5 | DOC-23 | — | N/A | hunk classification | 70-12 T2 `<automated>` (`UNTRACED_HUNKS = 0`) + owner `<human-check>` | ✅ | ✅ green |
| 70-13-01 | 13 | 6 | QUA-09 | — | N/A | gate quartet on tip + push | 70-13 T1 `<automated>` → `70-CI-EVIDENCE.md` | ✅ | ✅ green |
| 70-13-02 | 13 | 6 | QUA-09 | — | N/A | CI run observed | 70-13 T2 `<automated>` (`RUN_CONCLUSION = success`) | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### Requirement coverage

| Requirement | Status | Standing guard after the phase |
|-------------|--------|--------------------------------|
| QUA-09 | COVERED | `ruff check .` (CI lint job) — `UP` selected, no `UP006`/`UP035` ignore; re-run 2026-09-13: `All checks passed!` |
| QUA-11 | COVERED | same `ruff check .` rejects any reintroduced `typing.Dict`/`List`/`Set`/`Tuple`/`Iterator`; repo grep 2026-09-13: zero residue |
| QUA-12 | COVERED | one-shot before/after measurement, legs (a)–(e) all `MET`; the existing pytest suite remains the behaviour guard |
| DOC-22 | COVERED | one-shot check in 70-01/70-09/70-10 `<automated>` blocks; `CLAUDE.md:75` and the todo in `.planning/todos/completed/` re-confirmed 2026-09-13 |
| DOC-23 | COVERED | one-shot A/B/C docs diff, `DOC23_VERDICT = MET`; judgment part is manual-only (below) |

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Every D-11 hunk (H-001..H-083) traces to a real rename | DOC-23 | Whether an HTML/`.typ` text difference is explained by a rename is a judgment call (70-12 T2 `<human-check>`) | Read `## D-11 classification` in `70-DOCS-DIFF-EVIDENCE.md`; confirm `UNTRACED_HUNKS = 0`. **Done:** `70-UAT.md` test 1 passed 2026-09-13 |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency: one task
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-09-13

---

## Validation Audit 2026-09-13

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
