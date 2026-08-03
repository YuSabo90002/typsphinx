---
phase: 38
slug: structural-indentation-info-fields
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-02
---

# Phase 38 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: **authored at plan time** — all nine `38-0*-PLAN.md` files carry a parseable
`<threat_model>` block, so this audit verifies existing mitigations rather than building a
retroactive STRIDE register. `security_asvs_level: 1`, `security_block_on: high`
(`.planning/config.json`).

**Scope honesty.** typsphinx is a build-time Sphinx extension: no network listener, no
authentication, no session, no persistence, no multi-tenant untrusted input. An author who can write
the `.rst` already controls the build. ASVS **V5 Input Validation** is the only applicable category,
and its concrete instance is Typst string-literal escaping at emission sites. The remaining register
entries are availability/integrity threats against the *build* (a malformed emission aborts the whole
document's `typst.compile()`) and against the *evidence* (a gate assertion fitted to the code's own
output proves nothing). They are recorded as real STRIDE entries rather than padded out with
inapplicable web-application threats.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `.rst` / docstring source → doctree → translator | Author-controlled build-time text; the only untrusted-input analog in a build-time tool | Arbitrary document text, including non-ASCII parameter names and dotted type identifiers |
| translator → emitted `.typ` → `typst.compile()` | Typst source is executable markup; text escaping its string context becomes code, and one bad juxtaposition aborts the **entire** document, not just the offending node | Emitted Typst function calls and string literals |
| `self.body` vs. the table-cell emission buffer | Where a direct append or a stale position index silently targets the wrong emission list | Emission fragments and recorded buffer positions |
| `pyproject.toml` / `uv.lock` / `@preview` imports → shipped package | The milestone's supply-chain surface | Runtime deps, dev deps, four Typst Universe package pins |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-38-01 | Tampering | Typst string-literal injection via unescaped node text at an emission site | low–medium | accept | No escaping path changed outside T-38-04's new leaf emitter; the project-wide `escape_typst_string` boundary is untouched. `tests/test_typst_string_escape_gate.py` green (5 passed). | closed |
| T-38-02 | Denial of service | A gate assertion fitted to the translator's own output — a green that proves nothing | high | mitigate | Every expected token hand-derived from `38-EMISSION-CONTRACT.md`; RED recorded verbatim before any translator edit in `38-GATE-EVIDENCE-01/-02/-03.md`; hand-derive-then-confirm carried as a `must_haves` prohibition in each plan. | closed |
| T-38-03 | Information disclosure | A left-edge assertion built on `pypdf`'s per-glyph position API, which returns zeroes on this project's PDFs | medium | mitigate | Layout-mode extraction mandated; evidenced side-by-side against the zero-returning API in `38-GATE-EVIDENCE-01.md`. | closed |
| T-38-04 | Tampering | Unescaped parameter name / type text at the two NEW field-body leaf-emission sites (`visit_literal_strong` / `visit_literal_emphasis`) | high | mitigate | Both delegate to the single `_emit_field_body_monospace_leaf`, which calls `escape_typst_string(node.astext())` (`typsphinx/translator.py:6090`) before composing `{wrapper}(raw("…"))` at :6092. The gate asserts each emitted call equals a helper composed from that same function, so a bypass cannot pass. Non-ASCII round-trip covered by `test_fld03_nonascii_param_name_roundtrips_codepoints`. | closed |
| T-38-05 | Tampering | Reusing Phase 37's signature leaf wrapper, injecting an unauthorized zero-width space into every dotted field-body identifier | medium | mitigate | The leaf emitter deliberately does NOT apply SIG-07's post-`.` break opportunity (documented at `translator.py:6061`). Asserted as an **output** property — `test_fld03_no_zero_width_space_anywhere_in_field_bodies` — so it cannot be defeated by renaming a helper. | closed |
| T-38-06 | Information disclosure | A resolvable `:type:` losing its hyperlink while keeping its glyphs | medium | mitigate | Generic leaf body with no parent-node special-casing; the call nests inside the emitted `link(...)` because `link()`'s body argument is content (`translator.py:6074`). Gate asserts the monospace leaf nested inside the link with its label argument unchanged. | closed |
| T-38-07 | Denial of service | A structurally-required break silently suppressed, merging a nested member's body into following content | high | mitigate | The "content follows the nested member" control and the sibling body-less control are both asserted and green; the conjunction assertion catches the opposite failure (a doubled break). Recorded RED/CONTROL-GREEN in `38-GATE-EVIDENCE-03.md`. | closed |
| T-38-08 | Tampering | The emission-position marker comparing a recorded index against a different buffer after a `self.body` reassignment | medium | mitigate | Marker made buffer-identifying in plan 38-05 Task 2; the folded-todo fixture (a real buffer swap) is the control, measured before and after. | closed |
| T-38-09 | Repudiation | A Phase 37 expectation quietly re-pinned to accommodate Phase 38's wrapper, destroying SIG-08 evidence | medium | mitigate | Acceptance criterion reads `git diff` for changed expectation values; carried as a `must_haves` prohibition. Phase 37 signature gates green in the current run. | closed |
| T-38-10 | Repudiation | A census row produced by pattern matching rather than by reading | medium | mitigate | Every candidate file opened and read; the disagreement section in `38-TEST-CENSUS.md` is required evidence that reading happened. | closed |
| T-38-11 | Tampering | A Phase 39 rubric assertion edited during this phase's migration, destroying Phase 36's decoupling evidence | medium | mitigate | A must-not-touch section names the three rubric assertions and their owning phase. | closed |
| T-38-12 | Denial of service | The new wrapper juxtaposing against `depart_desc`'s break call, aborting the document with a Typst parse fatal | high | mitigate | Close carries a trailing newline per contract §2.2, matching the block-quote analog; the 38-01 fixture compiles as part of the plan's own gate. Real `typst.compile()` render gates green. | closed |
| T-38-13 | Tampering | Wrapper emitted by appending to the emission list directly, misrouting for a `desc` / field list inside a table cell | medium | mitigate | Buffer-aware writer mandated; all five field-list-family direct-append sites converted; the 38-01 fixture contains a table-cell `desc`. `tests/test_table_in_list_item_render_gate.py` green. | closed |
| T-38-14 | Denial of service | The inter-field separator firing for newly-inlined single-value bodies, merging a field-list block into one running line | high | mitigate | Contract §4.3 property 2 asserted by plan 38-02's consecutive-fields test; separator discriminator read from the diff in an acceptance criterion; carried as a `must_haves` prohibition. | closed |
| T-38-15 | Denial of service | The field-list wrapper juxtaposing against a neighbouring expression inside a list item — Typst parse fatal | high | mitigate | The bug #4 separator guard preserved unchanged; `tests/test_field_list_in_list_item_render_gate.py` is the named falsifier and is green. | closed |
| T-38-16 | Tampering | A second inline-concat mechanism introduced alongside the existing one | medium | mitigate | Reuse mandated and read from the diff; the one new attribute is scoped to the separator distinction, not to concatenation. | closed |
| T-38-17 | Denial of service | Reaching monospace by naming a font family, shadowing the CJK fallback and silently degrading the Japanese build | medium | mitigate | Monospace reached ONLY through Typst's `raw(...)` primitive, never a font family (`translator.py:6080-6081`); the diff was read for a font-family selection. `tests/test_typst_lang_gate.py` green (21 passed). | closed |
| T-38-18 | Repudiation | The census silently corrected at closeout so its predictions look better than they were | medium | mitigate | Finalisation section is append-only, verified by `git diff --stat`; the misses section is mandatory and present in `38-TEST-CENSUS.md`. | closed |
| T-38-19 | Denial of service | A corpus-wide document shape this phase's fixtures did not contain, breaking a real build only after release | high | mitigate | Full-corpus gate run explicitly (`tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`, **1 passed**, recorded in `38-08-SUMMARY.md`); RESEARCH Open Question 1's shape resolved as structurally unreachable, not merely absent — with 163 real field-list lines across 10 corpus files and zero fatal errors. | closed |
| T-38-SC | Tampering | Supply chain — a runtime dependency, a preview package, or a new version-lockstep site slipping in under this phase's work | high | mitigate | `git log -- pyproject.toml uv.lock` shows no phase-38 commit (most recent is `da09c07`, phase 35-03). The four `@preview` pins remain at **4 / 4 / 4** across `writer.py`, `template_engine.py` and `templates/base.typ`; `tests/test_preview_version_sync.py` green. `38-RESEARCH.md`'s Package Legitimacy Audit records "not applicable — this phase installs no external packages", so no `[ASSUMED]`/`[SUS]` human checkpoint is triggered. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-38-01 | T-38-01 | The pre-existing `escape_typst_string` boundary is the project-wide single source of truth and is unchanged by this phase. Phase 38 adds exactly one new user-text emission path (T-38-04) and that path routes through it. Accepting the residual risk on the *unchanged* paths, which are covered by their own standing gate. | yuta (project owner) | 2026-08-02 |
| R-38-02 | T-38-03 (test-runtime variant, 38-09) | Marginal test-suite runtime from the two new real-compile constructs: both attach to fixtures whose builds are already session-scoped and already compile to PDF, so the added cost is content, not a new build. | yuta (project owner) | 2026-08-02 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-02 | 20 | 20 | 0 | /gsd-secure-phase (orchestrator, ASVS L1 grep-depth short-circuit) |

**Evidence for this run (measured 2026-08-02, not recalled):**

- `uv run python -m pytest -q -m "not slow"` → **706 passed, 29 deselected, 0 failed** on the main
  tree at `8aee83e`. This run includes every gate named as a mitigation above:
  `test_typst_string_escape_gate.py` (5), `test_typst_lang_gate.py` (21),
  `test_field_list_in_list_item_render_gate.py`, `test_table_in_list_item_render_gate.py`,
  `test_preview_version_sync.py`, and the Phase 37 signature typography gates.
- `typsphinx/translator.py:6090` — `escaped = escape_typst_string(node.astext())`, the single
  escaping call for both new leaf emission sites; :6092 composes `{wrapper}(raw("{escaped}"))`.
- `grep -c '#import "@preview'` → `base.typ:4`, `writer.py:4`, `template_engine.py:4` — the
  three-place lockstep intact.
- `git log --oneline -- pyproject.toml uv.lock` → no phase-38 commit; newest is `da09c07` (phase 35).
- The full-corpus gate result is transcribed from `38-08-SUMMARY.md` (`-m slow`, 1 passed), not re-run
  in this audit.

**Why no auditor subagent was spawned:** the workflow's short-circuit rule applies —
`threats_open: 0` AND `register_authored_at_plan_time: true` AND `asvs_level == 1`. L1 grep-depth is
sufficient at this level; the deeper L2 boundary-placement / L3 end-to-end trace checks that force an
auditor spawn are not in scope for `security_asvs_level: 1`.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-02
