---
phase: 48
slug: compile-time-cross-reference-guard
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-14
---

# Phase 48 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

**Register origin:** `register_authored_at_plan_time: true` — all seven of `48-01`…`48-07-PLAN.md`
carry a parseable `<threat_model>` block, so this audit VERIFIES the plan-time register rather than
retroactively reconstructing one.

**Applicability.** ASVS **V2 (Authentication)**, **V3 (Session Management)**, **V4 (Access Control)**
and **V6 (Cryptography)** are structurally inapplicable — typsphinx is a local Sphinx/Typst
document-build tool with no network service, no authentication, no session and no cryptographic
surface (`48-RESEARCH.md` § Security Domain, `48-VALIDATION.md` § Security Domain). **V5 (Input
Validation)** is carried by the pre-existing `escape_typst_string` / `_sanitize_label` machinery,
which this phase did not change; the phase's one new label token (`__tsx-doc__`) is a fixed literal
whose docname half is sanitized by that same helper.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `conf.py` / `.rst` author input → emitted Typst source | User-authored docnames, ids, citation keys and section labels are interpolated into the guard expression at every emission site | Untrusted-by-convention author text; non-sensitive |
| Emitted `.typ` → `typst.compile()` | The Typst compiler consumes text this project generates; a malformed label or a duplicate definition is a compile fatal | Generated markup; non-sensitive |
| Published PDF → reader's PDF viewer | A link annotation instructs the reader's viewer to open a destination — internal `/Dest` or a `/URI` action | Local filesystem paths (this is the G-48-4 surface) |
| Built PDF → measurement snippet | Read-only pypdf enumeration of an artifact this repository itself produced | Generated artifact; non-sensitive |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-48-01 | Tampering | Label interpolated into the guard expression at every emission site | low | mitigate | `_label_existence_guard()` takes an already-namespaced `label: str` and never re-derives one; all four call sites pass `_namespace_label()` output, which routes through `_sanitize_label()` | closed |
| T-48-02 | Denial of Service | Per-reference `query()` introspection pass at Typst compile time | low | accept | Measured at full-corpus scale against tiers fixed before measurement: **-2.37%** (28.92s/27.21s after vs. 28.93s/28.56s before) — bottom tier, "record only" | closed (accepted) |
| T-48-03 | Tampering | The `visit_pending_xref` site's own close-string state slot | low | mitigate | Dedicated `_pending_xref_guard_close` slot (translator.py:402), deliberately NOT shared with `_reference_guard_close` (translator.py:391) — an unreachable path cannot corrupt the reachable one | closed |
| T-48-05-01 | Information Disclosure | A dead `file://` URI in a published PDF | low | mitigate | Enumerated pre-fix in `48-RED-EVIDENCE.md` Baseline 4 (40 annotations / 20 targets) and closed by plan 48-07 — see T-48-07-01 | closed |
| T-48-05-02 | Tampering | Expected values derived from the emitter instead of from first principles | medium | mitigate | Structural: `git status --porcelain typsphinx/` asserted empty in every task's acceptance criteria while 48-05 ran, so no emitter existed to read expectations off | closed |
| T-48-06-01 | Tampering | A gate that looks red but is measuring the wrong tree | **high** | mitigate | Mandatory per-worktree `uv sync` + `uv run` protocol, plus a provenance header naming the exact tree (`48-RED-EVIDENCE.md:753-768`: HEAD SHA `67f28df0af2ae4dfa35b17051a9d5d2cf46b912a`, worktree-local venv python, resolved `typsphinx/__init__.py` path inside the worktree) | closed |
| T-48-06-02 | Repudiation | A laundered expected value (read off a build, presented as derived) | medium | mitigate | Every assertion cites the `48-EXPECTED-STRUCTURE.md` sub-part it came from; `git status --porcelain typsphinx/` empty throughout | closed |
| T-48-07-01 | Information Disclosure | Dead `file://` URI actions in a published PDF | medium | mitigate | Closed and measured out: sub-population A went **15 targets / 35 annotations → 0 / 0**; `.pdf`-suffixed URI actions 40 → 5; internal `/Dest` 37 → 72; total annotations unchanged at 502 (`48-EVIDENCE.md` § "G-48-4 post-fix re-measurement") | closed |
| T-48-07-02 | Denial of Service | A duplicate self-anchor label aborting a whole compile | medium | mitigate | The `__tsx-doc__` token is unreachable from any docutils `make_id` output or domain id; the anchor is emitted at most once per content file (translator.py:733-736); `tests/test_duplicate_include_label_render_gate.py` passes | closed |
| T-48-07-03 | Spoofing | A reference resolving to the wrong document via a label-string collision | low | accept | Pre-existing, filed and owner-accepted limit (todo `2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md`, `48-REVIEW.md` WR-02). The whole-document path cannot worsen it — its raw id is a fixed token no `make_id` output can spell | closed (accepted) |
| T-48-07-04 | Tampering | A relative link to a genuine file asset silently losing its link | low | mitigate | The policy predicate is deliberately narrow; the invariance property is pinned by `test_option_a_internal_reference_onto_unknown_target_keeps_string_url` and `test_non_internal_reference_onto_known_document_not_guarded` | closed |
| T-48-SC | Tampering | npm/pip/cargo installs (supply chain) | low | accept | Not applicable — phase 48 installs no packages. No `pyproject.toml`/`uv.lock` change falls inside the phase-48 commit range (the only dep bump, `cc1f2e2c`, predates it by a day); still exactly four `@preview` packages, no fifth | closed (accepted) |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above `workflow.security_block_on` (high) count toward `threats_open`*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-48-01 | T-48-02 | Per-reference compile-time `query()` cost measured at **-2.37%** against tiers fixed before measurement — bottom tier, "record only", no todo or blocker warranted | Owner (UAT test 2) | 2026-08-13 |
| R-48-02 | T-48-07-03 | Label-collision false negative: a coincidental docname/label-namespace collision (`a/b` vs `a_u2f_b` via the `/`→`_u2f_` transform) renders a working link to the wrong document instead of degrading to plain text. Narrow, measured, filed as a todo, and not worsened by the whole-document path | Owner (UAT test 1) | 2026-08-13 |
| R-48-03 | T-48-07-01 (residual) | Five Sphinx-generated virtual pages (`genindex`, `py-modindex`, `search`, and the two `../` forms) have no PDF counterpart and stay as dead `file://` URI actions — the owner's **option-a** choice at the 48-05 Task 2 blocking checkpoint | Owner (48-05 Task 2 checkpoint; re-confirmed UAT test 6) | 2026-08-14 |
| R-48-04 | — (D-01) | Post-phase, a reference to a deliberately `:orphan:`-marked target degrades with zero diagnostic at any layer; no published-docs contract broke | Owner (UAT test 3) | 2026-08-13 |
| R-48-05 | T-48-SC | Supply-chain disposition is "accept" only in the vacuous sense — the phase installs nothing, so there is no install to vet | Owner (binding constraint #7) | 2026-08-14 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-14 | 12 | 12 | 0 | orchestrator (ASVS L1 short-circuit — `threats_open: 0` + `register_authored_at_plan_time: true` + `asvs_level == 1`) |

**Verification method.** ASVS L1 grep-depth, per this workflow's own short-circuit rule for a
plan-time-authored register with zero open threats at L1. Evidence gathered live against the main
tree at `f137bd25`:

- `grep -c 'query(<{label}>)' typsphinx/translator.py` → **1** (single guard-string derivation point)
- All four `_label_existence_guard(...)` call sites (translator.py:3524, 3536, 4575, 5305) pass a
  `_namespace_label()` product; `_namespace_label` → `_sanitize_label` confirmed by source read
- `_pending_xref_guard_close` and `_reference_guard_close` confirmed as separate slots
- `uv run python -m pytest -q tests/test_whole_document_xref_unit.py
  tests/test_duplicate_include_label_render_gate.py
  tests/test_xref_whole_document_guard_render_gate.py` → **19 passed** (0.75s)
- `git log -- pyproject.toml uv.lock` shows no dependency change inside the phase-48 commit range
- Four `@preview` package pins unchanged across `writer.py`, `template_engine.py`, `base.typ`

**Scope note.** No auditor subagent was spawned: the workflow's Step 3 short-circuit rule routes a
`threats_open: 0` + plan-time register + ASVS L1 phase directly to the SECURITY.md write. L1
grep-depth is the declared sufficient depth at this level; L2 boundary-placement and L3 end-to-end
trace checks were therefore not performed and are not claimed.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-14
