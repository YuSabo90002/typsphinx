---
phase: "70"
slug: "typing-modernization-and-its-behaviour-identity-evidence"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-13"
---

# Phase 70 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
> Built by `/gsd-secure-phase 70` from the `<threat_model>` blocks of 70-01..70-13-PLAN.md
> (register authored at plan time). No SUMMARY carries a `## Threat Flags` section.
> ASVS L1, `block_on: high` — grep-depth verification against the phase evidence files and
> a fresh re-measurement of git state on 2026-09-13; auditor not spawned (short-circuit rule).

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Source tree → evidence files | Behaviour-identity claims are only as good as the measurement that wrote them | Hashes, counts, verdict keys (non-sensitive) |
| Worktree `.venv` → main checkout | The main `.venv` editable finder resolves `import typsphinx` to the main tree | Module imports during measurement |
| Local branch → `origin` / GitHub Actions | Push and workflow dispatch are outward-facing and hard to reverse | Commits, refs, CI dispatch (public repo) |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-70-01 | Tampering | CLAUDE.md lines other than 75 | medium | mitigate | `3c5e281c` touches only `CLAUDE.md`; `sed '75d'` equal to parent, 115 → 115 lines (re-measured) | closed |
| T-70-02 | Repudiation | flip-dependent claim in the bullet | medium | mitigate | `CLAUDE_BULLET_IDENTICAL = YES` (70-10); line 75 has none of the forbidden tokens (re-measured) | closed |
| T-70-03 | Repudiation | research number recorded as measured | medium | mitigate | `70-BASELINE-EVIDENCE.md` keys measured at `PHASE_BASE_SHA = 697a1132`, `UP_TOTAL_BASE = 113` | closed |
| T-70-04 | Tampering | measuring through another tree's `.venv` | medium | mitigate | Every evidence file records `VENV_HOME`/`VENV_VERSION_INFO` from the executing tree's `pyvenv.cfg` | closed |
| T-70-05 | Repudiation | path-dependent `.typ` blamed on conversion | medium | mitigate | `CORPUS_CONTROL = EQUAL` (cross-path base-vs-base) | closed |
| T-70-06 | Tampering | failing fixture silently dropped | medium | mitigate | `CORPUS_PROJECT_COUNT = 167`; `CORPUS_LIST_SHA256` identical before/after (`30857d43…`) | closed |
| T-70-07 | Denial of Service | prohibitive corpus run | low | mitigate | `CORPUS_FULL_SECONDS = 134` ≪ 1800 s halt threshold; corpus not narrowed | closed |
| T-70-08 | Tampering | non-annotation change hidden in conversion | medium | mitigate | `PILOT_*`/masks `EQUAL`, `NON_TYPING_LINES_70_04 = 0`, mypy SHA and pytest equal to base | closed |
| T-70-09 | Repudiation | vacuous mask certifying anything | high | mitigate | `CONTROL_RENAME = DIFFER`, `CONTROL_IMPORT = DIFFER`; `MASK_HARNESS_SHA256 = 11cdbeb6…` identical in 70-04/05/07/08 | closed |
| T-70-10 | Tampering | `--preview`/`--unsafe-fixes` widening rewrite | medium | mitigate | Changed-line census typing-only (`NON_TYPING_LINES_* = 0`, `LEG_C_NON_TYPING_LINES = 0`) | closed |
| T-70-11 | Tampering | non-annotation change in builder.py | medium | mitigate | `BUILDER_MASK = EQUAL`, `NON_TYPING_LINES_70_05 = 0` | closed |
| T-70-12 | Tampering | `@preview` version-sync lines | medium | mitigate | `git diff 697a1132..HEAD -- typsphinx/` has no `@preview` line (re-measured); sync test in suite | closed |
| T-70-13 | Tampering | non-annotation change in template modules | medium | mitigate | `TEMPLATE_ENGINE_MASK = EQUAL`, `TEMPLATE_REGISTRY_MASK = EQUAL`, `NON_TYPING_LINES_70_06 = 0` | closed |
| T-70-14 | Tampering | `@preview` strings in template_engine.py | medium | mitigate | Same re-measured diff: no `@preview` line changed | closed |
| T-70-15 | Tampering | `--preview` enabled to clear the survivor | medium | mitigate | Survivor closed by one edit, `INIT_LINE_15 = from typing import Any` | closed |
| T-70-16 | Tampering | writer.py `@preview` import strings | medium | mitigate | Same re-measured diff: no `@preview` line changed | closed |
| T-70-17 | Tampering | test assertion weakened | high | mitigate | `ASSERT_LINES_70_04 = 0`, `ASSERT_LINES_70_08 = 0`, `LEG_C_ASSERT_LINES = 0`; collected 1548 before/after | closed |
| T-70-18 | Tampering | `ast.Dict` corrupted by blind rewrite | medium | mitigate | `tests/test_authors_pipeline_stage_gate.py:515` still uses `ast.Dict` (re-measured) | closed |
| T-70-19 | Tampering | other pyproject.toml lines | high | mitigate | `48fb3fbc..0224b5ea -- pyproject.toml`: exactly two removed UP lines, zero added (re-measured); `IGNORE_LEN 9 → 7` | closed |
| T-70-20 | Denial of Service | flip onto unconverted remainder | medium | mitigate | Flip tree green (`MYPY_EXIT_FLIP = 0`, `1547 passed 1 skipped`); `ruff check .` passes today | closed |
| T-70-21 | Repudiation | dangling pending-path ref / separate todo move | low | mitigate | `0224b5ea` holds both the `pyproject.toml` edit and the `R100` todo move (re-measured) | closed |
| T-70-22 | Repudiation | verdict copied from a conversion plan's key | medium | mitigate | 70-10 keys re-derived in its own tree (`BASE_70_10`, `LEG_A_EQUAL_COUNT = 10`) | closed |
| T-70-23 | Repudiation | broken grep reported as zero hits | medium | mitigate | Positive controls at base recorded (`PIPE_NONE_BASE = 82` = `PIPE_NONE_AFTER`, `PENDING_REFS_AFTER_70_01 = 1`) | closed |
| T-70-24 | Tampering | emitted-output change hidden in annotation rewrite | high | mitigate | `CORPUS_MANIFEST_SHA256` before = after (`4c87a31d…`), `LEG_D_VERDICT = MET` | closed |
| T-70-25 | Repudiation | difference written off as flakiness | medium | mitigate | No inequality occurred; cross-path control `EQUAL` removed path/time explanations | closed |
| T-70-26 | Repudiation | hunk written off as nondeterminism | medium | mitigate | `DOCS_HTML_CONTROL = EQUAL`, `DOCS_TYP_CONTROL = EQUAL`, `UNTRACED_HUNKS = 0`; owner read passed (70-UAT test 1) | closed |
| T-70-27 | Spoofing | intersphinx inventory change between builds | low | mitigate | `DOCS_BASE_CROSSCHECK = EQUAL`, A/B control empty | closed |
| T-70-28 | Tampering | worktree W left registered | low | mitigate | `git worktree list` shows only the main checkout (re-measured) | closed |
| T-70-29 | Tampering | decoy push / force-push / tag riding along | high | mitigate | `DECOY = ABSENT`, `ORIGIN_BEFORE = ABSENT`; no `v0.9.4*` tag locally or on origin, only the canonical branch exists (re-measured) | closed |
| T-70-30 | Tampering | orphaning commits by deleting a decoy | high | mitigate | `DECOY = ABSENT` — the delete path never ran | closed |
| T-70-31 | Elevation of Privilege | triggering release.yml / update-pin.yml | high | mitigate | `RELEASE_RUNS_AT_PUSHED = 0`; only CI dispatched (`DISPATCH_COUNT = 1`) | closed |
| T-70-32 | Repudiation | citing another run / masking a red run | high | mitigate | `RUN_HEAD_SHA = PUSHED_SHA = e70e31fb`, `DISPATCH_COUNT = 1`, `RUN_CONCLUSION = success`, 12/12 jobs | closed |
| T-70-33 | Information Disclosure | CI log excerpts in committed evidence | low | accept | See AR-01 | closed |
| T-70-SC | Tampering | package installs (all plans) | low | accept | See AR-02 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-01 | T-70-33 | Repository and Actions logs are public; only tool-output lines (versions, lint verdicts) are quoted | plan-time disposition (70-13-PLAN.md) | 2026-09-13 |
| AR-02 | T-70-SC | Provisioning installs only what `uv.lock` pins; no new package, `uv.lock` untouched by the phase | plan-time disposition (70-01..70-13-PLAN.md) | 2026-09-13 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-13 | 35 | 35 | 0 | /gsd-secure-phase 70 (orchestrator, L1 short-circuit) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-13
