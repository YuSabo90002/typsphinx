---
phase: 39
slug: admonition-taxonomy-rubric-nesting
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-02
---

# Phase 39 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

**Scope note.** typsphinx is a build-time Sphinx extension: it has no runtime authentication,
session, access-control or cryptography surface. Per `39-RESEARCH.md` § Security Domain, ASVS L1
**V5 Input Validation** is the only applicable category, joined by the supply-chain surface that
any dependency edit opens. Blocking threshold for this phase is `high`.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `.rst` fixture / document source → translator | Author-controlled build-time text; the only untrusted-input analog in a build-time tool | Document markup, directive arguments |
| `sphinx.locale.admonitionlabels` → translator → emitted `.typ` | An EXTERNAL catalog supplies a string interpolated into a Typst string literal — the boundary this phase moved (D-04/D-05) | Localized admonition titles (lazy i18n proxies, possibly non-ASCII / quote-bearing) |
| `.rst` directive argument → `visit_title` buffer swap → emitted `.typ` | The author-supplied title path, whose precedence over the catalog must not change | Author-written title content |
| translator → emitted `.typ` → `typst.compile()` | Where an unescaped or mis-separated emission becomes a build fatal or a rendering defect | Typst markup bytes |
| One handler's instance state → another handler's restore path | Three handlers wrote the same three `self.__dict__` save slots; the inner writer's `delattr` destroyed the outer writer's saved value | Translator save/restore state |
| `_emit_id_anchors`'s shared bookkeeping → every body-element handler that calls it | A change to the shared emitter would reach far beyond the rubric | Anchor emission + separator bookkeeping |
| PyPI → `pyproject.toml` → every developer and CI environment | A new package entering the dev dependency closure — the phase's only supply-chain surface | Third-party package code |
| translator → `.typ` → `typst.compile` → PNG → Pillow → committed artifact | The ADM-04 evidence chain; a break anywhere yields a plausible image evidencing the wrong build | Rendered PNG bytes |
| Committed artifact → human judgement → recorded verdict | The ADM-04 verification itself — deliberately human, no mechanical substitute | Owner's verbatim verdict |
| Network / upstream corpus → full-corpus gate → phase close decision | The gate's graceful skip makes an unavailable corpus visually indistinguishable from a passing one | Upstream Sphinx doc corpus |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-39-01 | Tampering | `_depart_admonition` static-title branch — title source moved from a hardcoded ASCII literal to the external `admonitionlabels` catalog, interpolated into a Typst string literal | high | mitigate | Branch routed through the project's single `escape_typst_string` helper after `str()`-coercing the lazy i18n proxy — `typsphinx/translator.py:4416`, docstring at `:4405`. No second, title-specific escaping routine introduced. Round-tripped with a quote+backslash title through `typst.compile()` (8798 bytes of PDF, no exception) — `39-05-SUMMARY.md:116`. | closed |
| T-39-02 | Denial of service | A structurally-required separator miscounted at the rubric/anchor seam, merging or over-separating adjacent blocks | high | mitigate | Anchoring detected via `len(self.body)` delta around `_emit_id_anchors` rather than a second `node.get("ids")` read; all four behavioural cases (anchored/unanchored × list-item/top-level) asserted; the decoupling module's two unanchored-rubric controls fail an indiscriminate separator strip — `39-06-SUMMARY.md:135,141`. | closed |
| T-39-03 | Tampering | A gate expectation fitted to the translator's current output rather than derived from the locked bucket table / catalog — a green that proves nothing | high | mitigate | Expected function names taken from `39-CONTEXT.md`'s locked table, expected titles read from `admonitionlabels` inside the test; RED recorded verbatim against named commits `61c0ad9` (`39-GATE-EVIDENCE-01.md:3`) and the 39-02 RED commit (`39-GATE-EVIDENCE-02.md:6-16`) before any translator edit existed. | closed |
| T-39-04 | Information disclosure | A left-edge assertion built on pypdf's per-glyph `visitor_text` callback, which returns zeroes on this project's PDFs — a gate green while measuring nothing | high | mitigate | `extraction_mode="layout"` mandated and used — `tests/test_rubric_indent_invariance.py:166` (`_layout_lines`), helpers copied from the in-repo module that established the technique; the correction to `39-CONTEXT.md`'s stated method recorded explicitly in `39-GATE-EVIDENCE-03.md`. | closed |
| T-39-06 | Spoofing | A region-unscoped bucket assertion greening because a DIFFERENT construct in the same document uses the expected function token | medium | mitigate | Every bucket assertion routes through `_clue_open_before`, which resolves the box actually containing the sentinel — `tests/test_admonition_bucket_render_gate.py:186`; a self-check test asserts it raises on a missing sentinel (`:326`). Document-wide substring/count assertions prohibited by name. | closed |
| T-39-07 | Elevation of privilege | A fix scoped to the wrong handler — renaming or restructuring `visit_strong` / `visit_desc_signature` instead of the rubric — silently reopening Phase 37's golden file | high | mitigate | Slot rename confined to `visit_rubric`/`depart_rubric` (`typsphinx/translator.py:5804,5916`), `_strong_was_*` → `_rubric_was_*`; `git diff -U0 typsphinx/translator.py` shows every hunk header above line 5700 across all three commits, and no hunk in the 380–470 range (`_emit_id_anchors` untouched) — `39-06-SUMMARY.md:73,140,141`. | closed |
| T-39-08 | Tampering | A pinned point value or character-column constant turning a structural guard into a change-detector | high | mitigate | Every comparison relative by construction; grep for integer-literal column comparisons in `tests/test_rubric_indent_invariance.py` returns nothing. | closed |
| T-39-09 | Repudiation | Presenting a guard that is green by design as though it were a GATE-01 RED, hiding where the phase's real RED came from | medium | mitigate | The D-12 framing is stated in the module docstring and in `39-GATE-EVIDENCE-03.md:8-16`, citing the Phase 36 SC#3 precedent; plan 39-02 carries the phase's actual RED and cross-references it. | closed |
| T-39-10 | Spoofing | An ADM-04 artifact rendered from a tree without the bucket-routing change — pre-phase buckets presented as post-phase evidence | high | mitigate | 39-04 deliberately produced tooling only, not the artifact (`39-04-SUMMARY.md:79`); 39-07 `depends_on` 39-05 and required `tests/test_admonition_bucket_render_gate.py` green in the same worktree BEFORE the render, with the render commit recorded in `39-ADM04-SIGNOFF.md`. | closed |
| T-39-11 | Denial of service | A silently-truncated render: a probe growing past one page makes typst-py's PNG export ambiguous, so the owner signs off on a partial image | medium | mitigate | One-page property asserted — `tests/test_admonition_greyscale_pipeline.py:110` (`test_probe_compiles_to_exactly_one_page`); the render script raises `RuntimeError` naming the page-template requirement rather than writing a partial artifact. | closed |
| T-39-12 | Spoofing | The catalog lookup silently overriding a directive-supplied title, replacing the author's words while every bucket assertion still passes | high | mitigate | Dynamic-title check keeps priority in `_depart_admonition` (not reordered); dedicated precedence test `tests/test_admonitions.py:448` `test_note_with_own_title_wins_over_catalog`, verified to catch a regression by temporarily reordering the check, observing failure, then reverting — `39-05-SUMMARY.md:117`. | closed |
| T-39-13 | Repudiation | A stale docstring or test name asserting a mapping the code no longer has, so the next reader trusts false documentation | medium | mitigate | Four falsified test functions renamed with their bodies re-derived and companion negative assertions updated (`39-05-SUMMARY.md:117`); both rubric handler docstrings rewritten to the actual diverged state (`39-06-SUMMARY.md:135`); no deferred-repair sentence remains in `typsphinx/translator.py` (grep returns nothing) and the folded todo was moved out of `pending/` (`78f0e93`). | closed |
| T-39-14 | Repudiation | A golden file regenerated blind, silently absorbing a collateral byte change outside the intended region | high | mitigate | `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` rebuilt via a direct `sphinx-build -b typst` into a scratch dir, diffed and attributed line by line BEFORE writing — not copied from pytest failure output; the only change is two blank lines in the propagated-target-inside-a-list-item region — `39-06-SUMMARY.md:35,120,136,143`. | closed |
| T-39-15 | Repudiation | ADM-04 `[V]` closed by a computed stand-in (contrast ratio / pixel diff) that greens without anyone having looked | high | mitigate | No automated ADM-04 assertion exists anywhere in the phase; only the artifact's production is checked. The blocking human checkpoint produced `39-ADM04-SIGNOFF.md`, whose §5 records the owner's operative verbatim verdict (Part 3), with the Part 1-2 → Part 3 reconciliation stated explicitly (`:75-94`). 39-08 reads the requirement status from that file only. | closed |
| T-39-16 | Tampering | A styling lever applied pre-emptively, turning the ADM-04 render into evidence of the fix rather than of the problem | medium | mitigate | Both levers were presented to the owner against the actual render and neither was applied; `git diff --stat -- typsphinx/` empty for 39-07 — `39-07-SUMMARY.md:33,70,120`. | closed |
| T-39-17 | Repudiation | A skipped corpus gate recorded as a passed corpus gate, closing SC#5 on a run that never happened | high | mitigate | The gate ran: resolved tag `v9.1.0`, duration 14.17s, verbatim result line recorded — `39-GATE-EVIDENCE-04.md:13-47,254`. The one SKIP in that output is a separate env-gated diagnostic (`TYPSPHINX_CORPUS_REPORT=1`), called out explicitly rather than glossed. | closed |
| T-39-SC | Tampering | `pillow` entering the dev dependency closure; `39-RESEARCH.md`'s Package Legitimacy Audit returned verdict **SUS** on the single signal `unknown-downloads` | high | mitigate | Blocking, non-auto-approvable `checkpoint:human-verify` ran BEFORE the `pyproject.toml` edit (39-04 Task 1) and presented the full signal breakdown including the researcher's coverage-gap reading. Package is dev-extra-only — `pyproject.toml:47`; the runtime array is byte-unchanged at `sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `typst>=0.15.0,<0.16` (`pyproject.toml:27-31`). Re-checked at close together with the `@preview` import count and pinned gentle-clues version (39-08 Task 2). | closed |

*Status: open · closed · open — below `high` threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above `workflow.security_block_on` (`high`) count toward `threats_open`*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

**Register provenance:** authored at plan time — all 17 threats come from `<threat_model>` blocks
present in all eight of `39-01`…`39-08-PLAN.md`. Duplicated IDs across plans (T-39-01, T-39-02,
T-39-03, T-39-07, T-39-10, T-39-13, T-39-15, T-39-SC) are merged here at their highest recorded
severity. No `## Threat Flags` entries were raised in any SUMMARY.md. There is no T-39-05 — the
plan-time numbering skips it.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|

No accepted risks. All 17 threats carry disposition `mitigate` and all mitigations landed.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-02 | 17 | 17 | 0 | /gsd-secure-phase (L1 verification, orchestrator) |

**Audit depth:** ASVS L1 — grep-depth mitigation-presence verification against the implementation.
Per the L1 short-circuit rule, no deeper boundary-placement (L2) or end-to-end trace (L3)
verification was performed; raise `workflow.security_asvs_level` to require it.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log (none)
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-02
