---
phase: 23
slug: v0-6-2-release-prep-regression-gate-close
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-23
---

# Phase 23 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Derived from `23-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4+ (`pyproject.toml` `dev` extras: `pytest>=8.4,<10`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`addopts = "-v --strict-markers"`; markers `slow`, `integration` registered) |
| **Quick run command** | `pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` |
| **Full suite command** | `pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v` |
| **Estimated runtime** | Quick: <2 s (offline, no compile). Corpus gate: ~14–25 s (real compile, cached corpus, offline). |

**Environment note (NixOS sandbox):** run pytest as `python -m pytest …` / `uv run python -m pytest …`
rather than invoking the compiled `pytest` binary directly. The corpus gate itself is unaffected by the
documented ELF-exec limitation because it shells out via `sys.executable -m sphinx`, not a compiled
binary — confirmed in `23-RESEARCH.md` § Corpus Gate Execution Mechanics.

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` (sub-second, no network, no compile)
- **After every plan wave:** Run the full corpus gate command above
- **Before `/gsd-verify-work`:** Corpus gate must read `1 passed` — **not** `1 skipped` (D-12); `-rs` is mandatory so a skip cannot masquerade as green
- **Max feedback latency:** 25 seconds

---

## Per-Task Verification Map

Phase 23 carries no FID/PDF/CONF/WR/DOC requirement IDs (release/close phase — all v1 requirements are
delivered by Phases 19–22.3). The map below is keyed to the phase's own **success criteria** instead of
REQ-IDs. Task IDs are seeded as `TBD` by plan-phase and filled in by `/gsd-validate-phase`.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 1 | SC#1 (version bump) | — | N/A | other | `uv sync --extra dev --locked` | N/A — CLI acceptance, not pytest | ⬜ pending |
| TBD | TBD | 1 | SC#1 + D-13 (README ↔ pyproject sync) | — | N/A | unit | `pytest tests/test_readme_version_sync.py -v` | ❌ W0 — created by this phase | ⬜ pending |
| TBD | TBD | 1 | SC#2 (CHANGELOG `[0.6.2]`) | — | N/A | manual | see Manual-Only Verifications | N/A — prose artifact | ⬜ pending |
| TBD | TBD | 2 | SC#3 (full-corpus regression gate) | — | N/A | integration | `pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v` | ✅ `tests/test_corpus_gate.py:284` | ⬜ pending |
| TBD | TBD | 2 | SC#4 (no `@preview` bump / 3-way surface untouched) | — | N/A | unit | `pytest tests/test_preview_version_sync.py -v` | ✅ pre-existing | ⬜ pending |
| TBD | TBD | 2 | SC#4 (zero new runtime deps) | — | N/A | other | `git diff v0.6.1..HEAD -- pyproject.toml` | N/A — diff inspection | ⬜ pending |
| TBD | TBD | 2 | SC#5 (scope fence: no tag/publish) | — | N/A | other | `git tag --list 'v0.6.2'` returns empty | N/A — negative assertion | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_readme_version_sync.py` — new file; the D-13 deliverable. Asserts `README.md`'s
      `**Status**: Stable (vX.Y.Z)` line agrees with `pyproject.toml`'s `version`. Self-contained,
      zero fixtures — mirrors `tests/test_preview_version_sync.py`'s design.
- [ ] No framework install needed — `pytest` (dev extras), `tomllib` (stdlib, Python 3.12+), and `re`
      (stdlib) are all already available. **Zero new dependencies** — required by SC#4.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `CHANGELOG.md` `## [0.6.2]` covers all 23 v1 requirement IDs with zero silent drops | SC#2 / D-01 | Prose curation — no machine can assert that a bullet *describes* a given FID/CONF/WR/DOC item | Cross-read the entry against `.planning/REQUIREMENTS.md`; confirm every one of FID-02..FID-14, PDF-01, PDF-02, CONF-01..CONF-03, WR-01, WR-02, DOC-01..DOC-05 appears in some bullet's trailing ID range |
| Issue #117 presented as a **user-visible output filename change** with a before/after example | SC#2 / D-06 | Presentation requirement, not a behavioral one | Confirm the bullet leads with a bold heading and shows `index.pdf` → `mydoc.pdf` for `typst_documents = [("index", "mydoc", …)]` |
| `### Removed` section carries a BREAKING label for `typst_output_dir` / `typst_author_params` | SC#2 / D-05 | Formatting/labelling judgement | Confirm a `### Removed` section exists and its items carry the bullet-level bold BREAKING prefix |
| Corpus gate actually **passed** rather than skipped | SC#3 / D-12 | The distinction lives in pytest's summary line, which no assertion inspects | Paste the raw `-rs` output into `23-VERIFICATION.md`; it must read `1 passed`, and the short-summary section must list no `SKIPPED` line for the gate |
| Milestone invariant: 3-way `@preview` version-sync surface untouched | SC#4 | Requires a diff read against the milestone base | `git diff v0.6.1..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ` — confirm no `@preview` version literal changed |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 25s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
