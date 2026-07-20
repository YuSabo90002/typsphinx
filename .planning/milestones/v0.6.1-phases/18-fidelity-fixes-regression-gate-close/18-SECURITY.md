---
phase: 18
slug: fidelity-fixes-regression-gate-close
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-07-19
---

# Phase 18 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| docutils doctree → emitted Typst source | `colspec['colwidth']` integers and inline-literal cell text (`node.astext()`) cross from the parsed doctree into the emitted Typst markup string. | Structured doctree values (integer column widths; literal identifier text). No untrusted external/network input — the doctree is produced from the project's own reStructuredText. |
| test suite → CI/operator report | GATE-03 outcome (corpus fatal-free + empty `unknown_visit`) is read from a real `-b typstpdf` build; a falsely-green report is the only risk surface. | Build-result booleans / catalogue reported to the operator. |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-18-01 | Tampering | `_build_columns_fr_arg` / `depart_table` | low | mitigate | Validity guard `len(widths)==n and n>0 and all(w and w>0 for w in widths)` (`translator.py:2272`); malformed / negative / zero / length-mismatched `colwidth` falls back to equal `[1]*n` (`:2274`) → never emits an empty `columns: ()`, a non-positive `fr` weight, or injectable markup. Weights are integers formatted via `f"{w}fr"`, not free text. | closed |
| T-18-02 | Tampering | `visit_literal` ZWSP injection | low | mitigate | U+200B (`chr(0x200B)`, `translator.py:1184`) injected into raw `code_content` **before** the unchanged `escape_typst_string` (`:1194`); gated on `self.in_table` (`:1175`) so non-table literal content is byte-unchanged. U+200B is not special to the escape helper, so no new unescaped-text path is introduced. | closed |
| T-18-03 | Repudiation | GATE-03 result reporting | low | mitigate | The gate (`tests/test_corpus_gate.py`) is a real `-b typstpdf` corpus build asserting a produced `index.pdf` (`%PDF` magic + non-empty) and an empty `unknown_visit` catalogue; a sandbox that cannot run it records an explicit environmental deferral (never a silent pass), so the reported state always corresponds to an actual run. | closed |
| T-18-SC | Tampering | package installs (supply chain) | low | accept | No new runtime packages installed this phase — `typst` / `pypdf` / `docutils` / `sphinx` are pre-existing pinned deps in `pyproject.toml`; the milestone "zero new runtime deps" invariant is itself verified by SC#4 (`test_preview_version_sync.py` + empty `git diff` on `pyproject.toml`). No supply-chain surface added. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on (high) count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-18-SC | T-18-SC | No new runtime dependencies were introduced; the "zero new runtime deps / no `@preview` bump" invariant is enforced and verified (SC#4). Residual supply-chain risk is that of the pre-existing pinned dependency set, unchanged by this phase. | yuta | 2026-07-19 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-07-19 | 4 | 4 | 0 | secure-phase (State B, ASVS L1 short-circuit — register authored at plan-time, all threats low, no blocking threat at/above `high`; mitigations verified live at L1 grep depth against `translator.py` / `test_corpus_gate.py`) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-07-19
