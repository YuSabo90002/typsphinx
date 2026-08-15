---
phase: 49
slug: per-master-include-graph-with-state-guarded-includes
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-14
---

# Phase 49 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

Derived from `49-RESEARCH.md` §Validation Architecture. Runtime figures below are **carried forward
from Phase 48's 2026-08-12 measurement and were NOT re-measured for this phase** — they are labelled
as such everywhere they appear. Worktree executors must re-provision per CLAUDE.md
(`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`) and prefix every command with
`uv run`.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (`sphinx.testing.fixtures` loaded as a plugin) — *cited from Phase 48's live-captured header; no dependency change between phases* |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`, `testpaths = ["tests"]`) |
| **Quick run command** | `uv run pytest -m "not slow"` |
| **Full suite command** | `uv run pytest` (adds the `-m slow` corpus/render-gate tests) |
| **Estimated runtime** | quick **~173s** · full-corpus gate alone **~29s** — *both carried from Phase 48's 2026-08-12 numbers, not re-measured for Phase 49* |

**Toolchain confirmed live during Phase 49 research (2026-08-14):**

| Dependency | Version | Confirmed how |
|------------|---------|---------------|
| `typst-py` | 0.15.0 | real `typst.compile()` + `typst.query()` calls this research session |
| `sphinx` | 9.1.0 | real `sphinx-build -b typstpdf` reproduction this research session |
| `pypdf` | 6.14.2 | PDF text readback this research session |
| Cached Sphinx `doc/` corpus | `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/` | present and warm |

`sphinx-build` is a pure-Python console script, so the NixOS `uv run <compiled-binary>` hazard does
**not** apply to it. New fixtures must still follow `tests/test_pdf_render_gate.py`'s
`sys.executable -m sphinx` pattern rather than `["uv", "run", "sphinx-build", …]`.

---

## Sampling Rate

- **After every task commit:** run the phase-scoped subset (the new Phase 49 gate files plus
  `tests/test_translator.py`). Phase 48's equivalent subset ran in ~4s; Phase 49's will be slower
  because most of its new fixtures are real `typst.compile()` + `pypdf` round-trips, so the plans must
  keep the per-commit subset explicitly scoped rather than defaulting to the whole `tests/` tree.
- **After every plan wave:** `uv run pytest -m "not slow"`.
- **Before `/gsd-verify-work`:** full suite (`uv run pytest`) green. COMP-12's corpus gate is
  `-m slow`, so the quick run alone does not satisfy the phase.
- **COMP-12 convergence failure is NOT a normal test-fix loop.** D-02 / binding constraint #5 assign
  it a stop-and-escalate protocol: a `state`/`context` multi-pass convergence failure at corpus scale
  is a **design-level finding**, not a fixture bug. Do not iterate on the fixture to make it pass.
- **Max feedback latency:** ≤ 30s per task commit (real-compile fixtures are inherently slower than
  Phase 48's grep/unit-heavy subset); ≤ 180s per wave.

---

## Per-Task Verification Map

> Seeded by plan-phase before tasks exist. `/gsd-execute-phase` fills one row per task as plans are
> executed; `/gsd-validate-phase` audits completeness.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 49-01-01 | 01 | 1 | COMP-07 | — | N/A (no security surface — see below) | integration | *(assigned at plan time)* | ❌ W0 | ⬜ pending |

**Requirement → test mapping the plans must satisfy** (lifted from `49-RESEARCH.md`):

| Req | Behavior | Test type | Command / vehicle | File exists |
|-----|----------|-----------|-------------------|-------------|
| COMP-07 | A document toctree'd by two masters appears in **both** masters' PDFs, read back via `pypdf` | integration — real `typst.compile()` + `pypdf` | new two-master fixture (`conf.py` with two `typst_documents` entries + shared child) | ❌ Wave 0 |
| COMP-07 | **Pre-fix RED first**: the measured 2026-08-11 baseline (`index.pdf` reports `SHARED-CHAPTER-MARKER` **0** times, `bmaster.pdf` reports 1, exit 0, no warning) recorded before the new emitter runs | evidence artifact | `xfail(strict=True)` or a committed `49-*-RED-EVIDENCE.md` (Claude's Discretion) | ❌ Wave 0 |
| COMP-08 | Prose keeps position: `PROSE-BEFORE` → chapter bodies → `PROSE-AFTER` in the compiled PDF's **text order** | integration — `pypdf` text-order assertion | new fixture shaped like Sphinx's default `index.rst` (prose, `.. toctree::`, "Indices and tables") | ❌ Wave 0 |
| COMP-09 | Diamond `M → [p, q]`, `p → [c]`, `q → [c]`, `M' → [q]`: `C-BODY` appears **exactly once** in each master's PDF, from the same `q.typ` | integration — `pypdf` | new fixture; research's `manual`/`bmanual`/`zmid`/`shared`/`bmaster` shape is directly reusable | ❌ Wave 0 |
| COMP-10 | Mirror pair `xmaster [zmid, shared]` vs `[shared, zmid]` — nesting **tracks source order**, not a hardcoded "prefer deeper" rule | integration — `typst.query(f, "heading", field="level")` against the **compiled** document, never a `.typ` grep | new fixture; research's `xmasterA`/`xmasterB` shape is directly reusable | ❌ Wave 0 |
| COMP-05 | Fresh DFS with an ordered `traversed` threaded through recursion, iterating toctree entries in **source order** — explicitly **not** a generalization of the LIFO `stack.pop()`/`append()` walk (which reverses child order with no compile error) | unit + integration | new traversal unit tests + the COMP-10 mirror pair as the end-to-end witness | ❌ Wave 0 |
| COMP-05 (D-03) | Iterates `includefiles`, not `entries`; `self` / external-URL toctree entries no longer abort the compile | integration — real `sphinx-build -b typstpdf` | new fixture reproducing research's D-10 transcript (`self` / `Ext <https://example.com>` / `child` / `child`) | ❌ Wave 0 — **pre-fix RED already captured live**: `TypstError: file not found (searched at .../self.typ)` |
| COMP-05 (D-04) | Duplicate toctree entry (same child listed twice in one directive) includes exactly **once** under the new mechanism | integration — real `typst.compile()` | new fixture, same `.rst` shape as the D-10 reproduction | ❌ Wave 0 |
| COMP-05 (D-06) | Degenerate shapes, each with its outcome **decided at plan time**: 2-node cycle · self-referencing toctree · `:glob:` toctree · reference to an `:orphan:` document · ≥3 masters sharing ≥2 overlapping children | integration, one fixture per shape | new roots / `conf.py`+`.rst` pairs — `tests/roots/` currently holds only `test-basic`, so **zero existing coverage** | ❌ Wave 0 |
| COMP-06 | Wrapper publishes its master's edge set as `#state(<ns key>, ()).update((…))`; content files emit the state-guarded `context { … }` at the toctree's own position | unit (emission shape) + integration (the COMP-08 interleaving fixture is the behavioural witness) | translator/builder unit tests + COMP-08 fixture | ❌ Wave 0 |
| COMP-06 (D-09) | **One-element array literal type assertion.** Omitting the trailing comma is *not* a compile error — `("key")` parses as a plain string and `in` silently degrades from array membership to **substring containment**. A single-edge fixture passes either way; corruption only surfaces once two edge keys share a substring. | unit — explicit type/shape assertion, **plus** an integration fixture with two deliberately substring-overlapping edge keys | new assertion + new fixture | ❌ Wave 0 |
| COMP-11 | `visit_toctree` emits no unconditional `include()`; `builder._included_docnames` and its `init()`/`write()` resets are deleted | structural — repo-wide grep assertion embedded in a test | `grep -rn "_included_docnames" typsphinx/` must return nothing | ❌ Wave 0 (grep assertion is new) |
| COMP-12 | Full Sphinx `doc/` corpus compiles fatal-free under the new composition — valid `%PDF`, empty `unknown_visit` catalogue | integration, `-m slow` | `uv run pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow` | ✅ existing gate (`tests/test_corpus_gate.py:284`) |
| Open Q #2 | `:numref:` — **two** cases, not one: (a) figure reachable from `root_doc` *and* a second master at different DFS positions → numbers differ; (b) figure reachable **only** from a non-`root_doc` master → `env.toc_fignumbers` never assigns a number at all and `_resolve_numref_xref()` falls back to the reference's literal text with **zero warning** | integration — real `sphinx-build` + `typst.compile()` + `pypdf`, two masters; extract both the `:numref:` rendered text and the target figure's Typst-assigned caption number from each PDF | new fixture per the research's two-case procedure | ❌ Wave 0 |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Binding constraint #6 (no laundered gates) means every expected value below must be derived from the
fixture's `conf.py` and `.rst` alone and **written down before the new emitter runs** — the
`47-EXPECTED-STRUCTURE.md` procedure this milestone has been imitating since Phase 47.

- [ ] **Two-master defect-A fixture** (COMP-07) with its pre-fix RED recorded against the measured
      2026-08-11 baseline (`SHARED-CHAPTER-MARKER`: `index.pdf` 0, `bmaster.pdf` 1, exit 0, no warning).
- [ ] **Diamond fixture** (COMP-09) — `M → [p, q]`, `p → [c]`, `q → [c]`, `M' → [q]`, asserting
      `C-BODY` exactly once per master's PDF from one shared content file.
- [ ] **Mirror-pair fixture** (COMP-10) — `xmaster [zmid, shared]` vs `[shared, zmid]`, asserted on
      **resolved** heading levels via `typst.query(…, "heading", field="level")`.
- [ ] **Prose-interleaving fixture** (COMP-08) — Sphinx's own default `index.rst` shape.
- [ ] **`self` / external-URL / duplicate-entry fixture** (D-03, D-04) — research reproduced the RED
      live (`TypstError: file not found (searched at .../self.typ)`); that transcript must become a
      committed test asset, not just a research quote.
- [ ] **Five degenerate-shape fixtures** (D-06) — 2-node cycle, self-reference, `:glob:` toctree,
      `:orphan:`-referenced document, ≥3 masters with ≥2 overlapping children. **Each shape's expected
      outcome (include / skip / degrade-to-text) must be decided during planning**, not discovered as
      a test failure. Zero existing coverage confirmed.
- [ ] **Substring-collision edge-key fixture** (D-09 trailing-comma hazard) — two edge keys where one
      is a substring of the other, proving the guard tests array membership and not string
      containment. Without this, the trailing-comma defect is invisible.
- [ ] **`:numref:` two-case fixture** (Open Question #2) — the differing-number case *and* the
      no-number-assigned case.
- [ ] **`_included_docnames` removal grep assertion** (COMP-11).

*No framework install needed — pytest, typst-py 0.15.0, pypdf 6.14.2, and Sphinx 9.1.0 are all
installed and working in `.venv`, each confirmed by direct invocation during Phase 49 research.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| COMP-12 convergence-failure escalation | COMP-12 / D-02 | A `state`/`context` multi-pass convergence failure at corpus scale is a **design-level finding**, not a fixture bug (binding constraint #5). No automated assertion can make that judgement — the gate can only report pass/fail. | If `tests/test_corpus_gate.py -m slow` fails to converge under the new composition, **stop the phase** and escalate per D-02. Do not iterate on the fixture, do not narrow the corpus, do not mark it flaky. |
| `:numref:` divergence policy — fix vs. document | Open Question #2 | The *measurement* is automatable (both cases above); the *decision* (fix the numbering, or record a documented limitation and hand it to Phase 51 docs / Phase 52 CHANGELOG) is an owner-level call the fixture cannot make. | Run the two-case fixture, record both PDFs' extracted numbers verbatim in the phase evidence, then take the fix-or-document decision explicitly and write it down before closing the phase. |
| `visit_toctree` code-mode invariant note | COMP-06 | Research confirmed `visit_toctree` is always invoked from code mode (content-file bodies are unconditionally wrapped in a top-level `#{` block by `builder.py`'s `_write_typst_files`), so no `prefix = "#" if self._in_markup_mode else ""` is needed — unlike Phase 48's reference/citation sites. Guarding against a hypothetical future markup-mode caller is out of scope. | Add a one-line comment at the new guard-emission site recording the assumption, so a future change that violates it fails loudly rather than silently emitting `context` without its required `#`. Verified by reading the site, not by a test. |

---

## Security Domain

**Not applicable.** This phase changes compile-time include selection in a document-generation
pipeline with no authentication, session, access-control, network-input, or cryptographic surface.
ASVS V2/V3/V4/V6 are structurally inapplicable to a local Sphinx/Typst build tool exposing no network
service. V5 (Input Validation) is already covered by the existing `escape_typst_string` /
`_sanitize_label` machinery; the new edge-key derivation (D-04/D-05/D-07) emits **generated** keys
built from docnames into a Typst string literal, so the plans must route that emission through the
existing escaping helpers rather than interpolating raw docnames.

Each PLAN.md still carries a `<threat_model>` block (ASVS L1, block on `high`) recording this
determination explicitly rather than omitting the block.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s (phase-scoped) / < 180s (quick suite)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
