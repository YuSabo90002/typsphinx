---
phase: 49
slug: per-master-include-graph-with-state-guarded-includes
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-14
---

# Phase 49 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

**ASVS scope note.** ASVS **V2 (Authentication)**, **V3 (Session Management)**, **V4 (Access
Control)** and **V6 (Cryptography)** are **structurally inapplicable** — typsphinx is a local
Sphinx/Typst document-generation tool with no network service, no authentication, no session and no
cryptographic surface. **V5 (Input Validation)** is the one real seam this phase introduces: edge
keys derived from author-supplied docnames are interpolated into Typst string literals on both the
publication side and the guard side. This is recorded rather than omitted, per the phase's own
security contract (all six PLAN files carry the same `<threat_model>` preamble).

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `conf.py` / `.rst` author input → emitted Typst source | Author-supplied docnames are interpolated into the edge-key string literals this phase introduces, on the wrapper's publication side and each content file's guard side | Docnames (untrusted text: may contain quotes, backslashes, path separators) |
| Emitted `.typ` → `typst.compile()` | The Typst compiler consumes text this project generates, including the new `state(...)` publication and `if ... in ... { include(...) }` guard lines. A malformed literal either aborts the compile or — in the arity-1 trailing-comma case — silently changes membership semantics with no diagnostic | Generated Typst markup |
| Sphinx `BuildEnvironment` → the new traversal | `derive_master_edge_keys()` reads `env.toctree_includes`, the same include-file mapping Sphinx's own inlining builders read; Sphinx never populates it with `self` entries or external URLs | Toctree include graph (may contain cycles) |
| Third-party corpus source (Sphinx doc tree) → the emitter | The GATE-02 corpus gate builds a large external documentation tree this project does not author, at a scale no fixture reaches | Third-party `conf.py` / `.rst` (version-pinned clone) |
| Production package source → the structural gate | The COMP-11 removal gate reads the package's own source text as its subject; a refactor relocating the emission can defeat a source-text assertion, so each structural assertion is paired with a behavioural one where a behavioural form exists | Package source text |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-49-01 | Tampering | Docname interpolated into an emitted Typst string literal by the edge-key derivation and by the state publication | low | mitigate | Both docnames route through the pre-existing `escape_typst_string()` helper inside the ONE shared derivation function `make_include_edge_key()` (`typsphinx/translator.py:229-231`), so no call site can bypass it; the guard side escapes its own relative include path in `render_include_guard()` (`translator.py:373`) — a gap the pre-Phase-49 unconditional include path did not close | closed |
| T-49-02 | Tampering | The guard's condition string spelled differently on the graph side and the emission side; or a second state-key spelling entering the package later | low | mitigate | D-05: one shared function, two callers (`TypstBuilder._build_include_edge_map()` via `derive_master_edge_keys()`, and `visit_toctree`). The state key is a single module constant `INCLUDE_STATE_KEY` (`translator.py:192`). Structural rather than diagnostic, because a mismatch would NOT fail the build — the guard simply never fires and content silently vanishes | closed |
| T-49-03 | Denial of Service | Corpus-scale Typst multi-pass layout convergence over the new state/context graph | medium | mitigate | Measured in 49-06 by running the existing GATE-02 corpus gate completely unmodified, twice, both green (14.53s / 13.63s; 15,412,931-byte valid PDF reproduced). Mean 14.08s vs. Phase 48's D-11 baseline of 28.745s / 28.065s — roughly −50%, an improvement, not a regression. Scope stated honestly: convergence for THIS corpus at THIS version pin; `PROJECT.md`'s named residual risk stays named | closed |
| T-49-04 | Information Disclosure | Fixture projects committed into the repository | low | accept | All Phase 49 fixture content is synthetic prose and all-caps markers. Re-measured at audit time: a credential/PII sweep over `tests/fixtures/state_guard_*` and `tests/fixtures/bld03_self_collision_gate` (password / secret / api-key / token / absolute home path / email / PEM header) returned zero hits | closed |
| T-49-05 | Tampering | An external URL or a `self` entry reaching the emitter as if it were a docname | low | mitigate | D-03: both sides iterate the toctree node's include-file list, which Sphinx never populates with an external URL or a `self` entry, so neither can become an include path. Asserted behaviourally against a real build by `tests/test_state_guard_shapes_gate.py::test_self_and_external_url_produce_no_guard` and `::test_self_referencing_entry_has_no_guard`, plus the unit-level `test_self_referencing_parent_produces_no_self_edge` | closed |
| T-49-06 | Denial of Service | A toctree cycle driving unbounded recursion in the new traversal | medium | mitigate | `derive_master_edge_keys()` seeds an ordered `traversed` with the master's own docname and appends BEFORE recursing (`translator.py:288-299`), mirroring Sphinx's `inline_all_toctrees()`, so no document is entered twice. Asserted at unit level (`test_two_node_cycle_terminates_with_forward_edge_only`) and behaviourally by the `state_guard_cycle_gate` fixture's build terminating and exiting 0 | closed |
| T-49-07 | Tampering | A single-element published array losing its trailing comma, silently degrading membership to substring containment with no diagnostic at any layer | medium | mitigate | `render_include_edge_state()` renders the array literal with a UNIFORM unconditional trailing-comma rule and no `len == 1` special case (`translator.py:330-335`), so the hazard cannot arise by construction. Driven at arities 0-3 with each result really compiled and the resolved Typst type asserted to be `array` (`TestRenderIncludeEdgeState`, `TestPublicationArityReadback`); the arity-1 case is the load-bearing one. Grounded in `49-EVIDENCE.md` Probes 1-5, which measured the silent `array`→`str` degradation for real | closed |
| T-49-08 | Repudiation | A removal claimed in a summary but not enforced by any test, regressing silently | low | mitigate | The `_included_docnames` ledger removal (COMP-11) became a committed, falsifiable gate: `tests/test_include_ledger_removal_gate.py` (10 tests / 5 classes) asserts absence from the production package and from repo-wide non-planning prose, that `visit_toctree` emits no raw `include(...)` and no builder-attribute membership test, and that exactly one state-key literal exists (AST-based, resolving f-string interpolations back to the module constant — not a naive text count). Proved able to go RED by temporarily reintroducing the deleted attribute, then reverted clean | closed |
| T-49-09 | Information Disclosure | A Sphinx diagnostic silently disappearing under the new mechanism, hiding a broken project from its author | medium | mitigate | All nine Phase 49 fixtures were rebuilt and every post-fix warning/notice compared item by item against its recorded pre-fix baseline (`49-RED-EVIDENCE.md`, `49-SHAPES-RED-EVIDENCE.md`) — all nine MATCH byte-for-byte, no diagnostic silently removed. Enforced going forward by `tests/test_state_guard_shapes_gate.py::test_warning_baseline_preserved` (parametrized per fixture) | closed |
| T-49-10 | Tampering | The corpus clone, fetched from a third party and cached locally | low | accept | The gate's pre-existing clone-and-cache helper is unchanged by this phase (`git diff --name-only HEAD -- tests/test_corpus_gate.py` empty), pins a specific Sphinx version tag, and builds documentation only — no corpus code is executed beyond that documentation project's own configuration. This is the pre-existing accepted posture of the gate since it was introduced, not a new exposure | closed |
| T-49-11 | Information Disclosure | A numbered reference silently rendering unrelated text, misleading a reader of the generated PDF | medium | mitigate | Both cases measured live in 49-06 rather than left latent, via `tests/fixtures/state_guard_numref_two_case_gate/` + `tests/test_state_guard_numref_gate.py` (6 tests, measurement gate): Case (a) diverges (Sphinx bakes "Fig. 1." into both masters while Typst assigns 1 and 3), Case (b) falls back to raw label text with a build warning. Recorded verbatim in `49-EVIDENCE.md` and handed forward per D-01 as a tracked pending todo (`.planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`), owner-approved, so a reader is warned even though no compile error exists to warn them | closed |
| T-49-SC | Tampering | Supply chain — npm/pip/cargo installs | low | accept | Not applicable: this phase installs no packages of any kind. `49-RESEARCH.md` §Package Legitimacy Audit records no new PyPI dependency and no new `@preview` package; ROADMAP binding constraint #7 forbids both. Re-measured in 49-05's SC#4 invariant sweep — `@preview` count re-confirmed at four across every declaring surface with the sync gate green, zero new `typst_*` config values, zero new runtime dependencies (empty `git diff --stat` over the phase base) | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above `workflow.security_block_on` (`high`) count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-49-01 | T-49-04 | Phase 49 fixture projects are committed to the repository. All content is synthetic prose and all-caps markers; a credential/PII sweep over every Phase 49 fixture returned zero hits | Phase 49 plan 49-02 threat model | 2026-08-14 |
| R-49-02 | T-49-10 | The GATE-02 corpus gate clones a version-pinned third-party documentation tree and builds documentation only. The clone-and-cache helper is unchanged by this phase; this is the gate's pre-existing accepted posture | Phase 49 plan 49-06 threat model | 2026-08-14 |
| R-49-03 | T-49-SC | No package of any kind is installed by this phase — no new PyPI dependency, no new `@preview` package. Re-measured in 49-05's SC#4 invariant sweep | ROADMAP binding constraint #7 | 2026-08-14 |
| R-49-04 | T-49-11 | The numref per-master divergence (Case a) and non-root-only fallback (Case b) are real, measured, and not fixed in this phase. Carried forward as a documented limitation with a tracked pending todo, per D-01 | Owner ("approved", 49-06 Task 3 human-verify checkpoint) | 2026-08-14 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-14 | 12 | 12 | 0 | /gsd-secure-phase (orchestrator, ASVS L1 short-circuit) |

**Audit method.** State B — no prior SECURITY.md; the register was built from the
`<threat_model>` blocks in all six PLAN files (deduplicated by threat ID across plans) and from
the SUMMARY files. No `## Threat Flags` section is present in any SUMMARY, so no additional
runtime-discovered threats entered the register. `register_authored_at_plan_time: true` and
`asvs_level: 1`, and every threat classified CLOSED at grep depth against the implementation and
its committed tests, so the workflow's L1 short-circuit applied and no separate auditor subagent
was spawned. Evidence cited in the register above was read directly from
`typsphinx/translator.py`, `tests/test_include_edge_derivation_unit.py`,
`tests/test_state_guard_shapes_gate.py`, `tests/test_include_ledger_removal_gate.py`,
`tests/test_state_guard_numref_gate.py`, and the phase's own SUMMARY/EVIDENCE artifacts.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-14
