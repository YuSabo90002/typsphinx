---
phase: 16
slug: silent-drop-node-handlers-length-converter-refactor
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-07-16
---

# Phase 16 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| rST author text → generated Typst source | untrusted document content (todo bodies, `:manpage:` text) crosses into compiled code | author-controlled inline text |
| Sphinx config (`todo_include_todos`) → published PDF | publication-intent boundary: draft notes vs shipped output | draft/internal notes |
| rST author length attributes → generated Typst source | author-controlled `:figwidth:`/`:width:` strings cross into compiled code | length/unit strings |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-16-01 | Information Disclosure | visit_todo_node | medium | mitigate | Gated on `config.todo_include_todos` via `raise nodes.SkipNode` (translator.py:3898), mirroring official Sphinx builders; pinned by `test_todo_typ_omits_body_when_todo_include_todos_false` (test_pdf_render_gate.py:1908) | closed |
| T-16-02 | Tampering | todo body text → Typst source | low | mitigate | Body children flow through the existing, unmodified visit_Text/escape_typst_string chain (no new interpolation point); LEAK_SIGNATURES negative check in PDF render gates | closed |
| T-16-03 | Tampering | manpage text → Typst source | low | mitigate | visit_manpage/depart_manpage fully delegate to visit_emphasis/depart_emphasis (translator.py:1054, 1065) — Text child routes through the existing escape chain; LEAK_SIGNATURES negative check | closed |
| T-16-04 | Denial of Service (build-time) | bespoke inline handler breaking separator/mode state | low | mitigate | Full delegation to visit_emphasis (no bespoke state machine); manpage_render_gate fixture exercises paragraph + list-item + caption contexts under a real compile | closed |
| T-16-05 | Denial of Service (build-time) | width: kwarg passed directly to figure()/table() | high | mitigate | Real-compile-verified `block(width: ...)[#figure(...)]` wrapper shape (translator.py:1960); render-gate tests compile fatal-free with wrappers present — a kwarg regression aborts the compile and fails the gate loudly | closed |
| T-16-06 | Tampering / Denial of Service | malformed or unsupported length unit reaching Typst unconverted (FIG-01 regression class) | medium | mitigate | All width/height values route through `_convert_length_to_typst` (translator.py:3116; regex-validated numeric output, unknown unit → drop + one logger.warning); fixtures assert raw unit strings never appear in the .typ | closed |
| T-16-SC | Tampering | package installs | low | accept | No npm/pip/cargo/typst-package installs in this phase (zero new dependencies; gentle-clues 1.3.1 pre-existing and unchanged) | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-16-01 | T-16-SC | Supply-chain surface unchanged: phase adds zero new packages (RESEARCH Package Legitimacy Audit); gentle-clues 1.3.1 pre-existing and version-sync-tested | plan-time disposition (16-01/02/03-PLAN.md) | 2026-07-16 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-07-16 | 7 | 7 | 0 | gsd-secure-phase (L1 grep-depth short-circuit; register authored at plan time) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-07-16
