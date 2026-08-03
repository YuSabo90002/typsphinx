---
phase: 40
slug: citations-full-round-trip
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-02
---

# Phase 40 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `.rst` source (fixture, shipped sample, real corpus) → translator | Author-controlled build-time text — the only untrusted-input analog in a build-time Sphinx extension. Citation keys, docnames and entry bodies all cross here. | Citation key tokens, docnames, entry body text |
| translator → emitted `.typ` → `typst.compile()` | Where a mis-derived label token, a duplicated label definition, or a miscounted separator becomes a whole-document compile abort rather than a cosmetic defect. | Typst label tokens, grid-cell expressions, separator bytes |
| docutils `backrefs` / `ids` → emitted `link()` targets | The definition side emits links to anchors the citing side defines; a mismatch is a fatal `label ... does not exist`, a double definition a fatal `label occurs multiple times`. | docutils id strings → Typst anchors |
| project dependency manifests (`pyproject.toml`, `uv.lock`) → build environment | Standing milestone invariant: zero new dependencies, `@preview` package count stays at four across all three declaration sites. | Package names / pinned versions |

ASVS L1 scope: **V5 Input Validation is the only applicable category.** A build-time Sphinx
extension has no runtime authentication, session, access-control or cryptography surface
(`40-RESEARCH.md` § Security Domain). Blocking threshold: `high`.

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-40-01 | Tampering | Citation label-token derivation in `visit_citation` / `visit_reference` — a key or docname carrying a character outside Typst's label set would produce an unclosed label and abort the entire compile | high | mitigate | Every new label token is produced by `_namespace_label` (`translator.py:3886`) over `_sanitize_label` (`translator.py:3829`) — D-13. No second sanitizer was introduced: the phase's translator diff adds exactly six methods (`_citation_run_neighbour`, `_find_citing_reference`, `_citing_reference_has_own_anchor`, `visit_citation`, `depart_citation`, `visit_label`), none of them a sanitizer. Label text and entry bodies reach the `.typ` only through the normal visitor chain, so the central `escape_typst_string` path applies unchanged. | closed |
| T-40-02 | Denial of service | Grid-open/grid-close and list-item leading-newline separators miscounted — merging two reference lists, splitting one, or juxtaposing two code-mode expressions with no separator (the phase's actual pre-fix defect) | high | mitigate | Run adjacency is decided by one shared helper, `_citation_run_neighbour` (`translator.py:2644`), used in both directions (`offset=-1` from `visit_citation`, `+1` from `depart_citation`); it scans THROUGH emit-nothing siblings (`nodes.comment`, `nodes.system_message`) so a fixture comment cannot split a run while a real paragraph does. Asserted by exact grid counts in `test_references_run_and_run_break_grid_counts` and by the list-item/concat boundary check in `test_separator_paragraph_concat_and_list_item_boundaries` (the latter repaired in 40-05 to add a region-wide dangling-operator guard). | closed |
| T-40-03 | Denial of service | A link emitted to a label that was never attached, or the same label attached twice | high | mitigate | Three verified guards: (1) the definition anchor is attached ONLY through the label cell's bracket-wrap (`translator.py:2885`) and `_emit_id_anchors` is deliberately NOT called on the citation node — documented at `translator.py:2756`; (2) a backref whose citing-site anchor `visit_reference` declined to emit is filtered out via `_citing_reference_has_own_anchor` and the remaining markers renumbered by enumerating the filtered list (`translator.py:2856-2862`); (3) the undefined-key case is asserted not to emit any link — `test_citation_render_gate.py:602-609` proves no link targets the `Nosuchkey` anchor while its text still renders as ordinary content. | closed |
| T-40-SC | Tampering | npm/pip/cargo installs — supply chain | high | mitigate | Phase installs nothing and adds no dependency. Measured: `git diff 1745b27..HEAD -- pyproject.toml uv.lock` is empty across the whole phase; `tests/test_preview_version_sync.py` is unmodified by the phase diff and green. `40-RESEARCH.md` § "Package Legitimacy Audit" records the phase as not applicable — `typst-py` and `pypdf` were already pinned and already used by every render gate. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Verification Evidence

Full-scale verification (40-04, recorded in `40-NONREGRESSION.md`):

- **Full-corpus `-b typstpdf` gate — actually run, not skipped.** `uv run pytest tests/test_corpus_gate.py -m slow -v` → `TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED` (`1 passed, 1 skipped, 3 deselected in 13.68s`). Builds the entire Sphinx `v9.1.0` `doc/` tree — the widest input this project compiles, and the only run that would surface a `label does not exist` / `label occurs multiple times` fatal arising from a document combination no fixture reproduces. This is the at-scale evidence for T-40-01, T-40-02 and T-40-03.
- **Citation render gate — all 9 tests PASSED** (`tests/test_citation_render_gate.py`), covering namespaced duplicate keys across two documents, run/run-break grid counts, uncited entries, separator/concat/list-item boundaries, real `typst.compile()`, and compiled-PDF layout + backref link geometry.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|

No accepted risks — all four threats closed by implemented, verified mitigations.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-02 | 4 | 4 | 0 | /gsd-secure-phase (orchestrator, ASVS L1 short-circuit) |

Register origin: `register_authored_at_plan_time: true` — plans 40-01 through 40-04 each carried a
parseable `<threat_model>` block with the same four-threat register (40-05 is a gap-closure plan for
defective gate assertions and carries none). With `threats_open: 0`, `asvs_level: 1` and a
plan-time-authored register, the workflow's short-circuit rule applies: L1 grep-depth verification is
sufficient and no auditor subagent was spawned.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-02
