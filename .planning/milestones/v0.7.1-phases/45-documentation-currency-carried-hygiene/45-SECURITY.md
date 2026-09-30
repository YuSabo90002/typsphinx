---
phase: 45
slug: documentation-currency-carried-hygiene
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-10
---

# Phase 45 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: authored at plan time — all four PLAN files (45-01 … 45-04) carried a
parseable `<threat_model>` block. No SUMMARY file declared a `## Threat Flags` section, so
the register below is the union of the four plan-time registers, verified against the
implemented tree at HEAD.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| PyPI → build environment | A new build-time dependency (`myst-parser`) enters the `docs` extra, installed by RTD and CI's docs lane | Third-party package code executed at docs-build time |
| repo-root file → Sphinx source tree | `docs/source/changelog.rst:1` reads `../../CHANGELOG.md`, a path outside `docs/source/` | First-party repo-tracked Markdown, already public |
| `CHANGELOG.md` → rendered HTML/PDF | Repo-authored Markdown parsed by a newly added parser and rendered into published output | First-party release notes |
| `CHANGELOG.md` → `release.yml` (CI tier) | The same file supplies the GitHub Release body via `scripts/extract_changelog_section.py` | Release body text; a structural break breaks a release |
| test fixture → repository root | `tests/fixtures/changelog_include_gate/changelog.rst:1` reads `../../../CHANGELOG.md` | First-party repo-tracked Markdown |
| published documentation → user's `conf.py` | Docs edited in this phase are copied verbatim by readers into their own build config | Configuration guidance (a wrong statement becomes a wrong downstream config) |
| test fixture → real `sphinx-build` subprocess | Gates spawn `sys.executable -m sphinx` and compile Typst, executing the code under test | Build inputs / generated artifacts (written to `tmp_path`) |
| Sphinx build-time config → `derive_typst_lang()` | A user's `language` config value (arbitrary string, incl. non-ASCII) flows into this helper and its output reaches a Typst `lang` parameter | Untrusted-shaped config string — the phase's only input-validation surface (ASVS V5) |
| planning record → downstream readers | `.planning/PROJECT.md` is read by every subsequent agent; an unterminated comment silently swallows the rest of the file | Planning context |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-45-05 | Tampering | `CHANGELOG.md` edits breaking `scripts/extract_changelog_section.py` section slicing, aborting/corrupting a release (REL-04) | high | mitigate | Extractor algorithm is positional and name-agnostic; no code in it changed this phase (`git diff` scope confirms only `typsphinx/template_engine.py` under `typsphinx/`). `tests/test_changelog_extraction.py::test_unreleased_headings_do_not_leak` present and green; extractor exercised directly on `0.4.4` and `0.7.0`, `0.7.0` body compared byte-for-byte pre/post edit | closed |
| T-45-SC | Tampering | `pyproject.toml` docs extra — `myst-parser` supply-chain install | medium | mitigate | Package legitimacy gate ran (RESEARCH § Package Legitimacy Audit: `SUS` traced to a null downloads-API response, contradicted by ~1.5M weekly downloads); blocking human checkpoint preceded the edit; floor pinned `myst-parser>=5.0` (`pyproject.toml:53`); `uv.lock` regenerated and committed (resolved artifact reviewable at `uv.lock:779`, `:1522`) | closed |
| T-45-06 | Denial of Service | Malformed Markdown in the new `## [0.4.4]` section aborting the Typst PDF compile | medium | mitigate | `tests/test_changelog_page_gate.py::TestChangelogIncludeCompilesToPdf` compiles the real `CHANGELOG.md` through `-b typstpdf` and asserts `%PDF` magic plus extracted content; ran green (not skipped) in the terminal gate with the `docs` extra provisioned | closed |
| T-45-07 | Repudiation | "Build clean" claimed from a green exit code while warnings were emitted (no tox docs env passes `-W`) | medium | mitigate | Clean defined and measured as a delta against the 45-01 baseline: `45-GATE-EVIDENCE-02-docs-build-clean.md` records `html_warning_count=1`, `pdf_warning_count=1`, `changelog_attributable_warning_count=0` — delta 0/0/0 vs. baseline `8c74b85`, fresh output dir per build, method stated verbatim | closed |
| T-45-09 | Repudiation | Documentation asserting an unmeasured behaviour — the exact DOC-11 failure mode (`README.md:203`, `quickstart.rst:67` were both false) | medium | mitigate | `tests/test_quickstart_docs_gate.py::TestPublishedQuickstartTextMatchesBuild` binds every output-filename claim to a real `-b typstpdf` fixture build, with the expected stem computed from the same `make_filename_from_project` helper the builder calls rather than hardcoded | closed |
| T-45-12 | Tampering | `derive_typst_lang()` refactor weakening the ASCII-scoped accept test, letting CJK/Cyrillic `language` through to Typst and aborting the compile (ASVS V5) | medium | mitigate | `re.fullmatch(r"[a-z]{2,3}", head)` preserved verbatim at `typsphinx/template_engine.py:133` (and documented at `:96`); `tests/test_template_engine.py::TestDeriveTypstLang` (18 tests) and `tests/test_typst_lang_gate.py` (18 real-build tests) green 39/39 on both sides of the refactor | closed |
| T-45-13 | Repudiation | Claiming warning-for-warning identity without measuring it | medium | mitigate | Rendered message for a rejected input (`derive_typst_lang("abcd")`) captured character-for-character before and after and found byte-identical; recorded verbatim in `45-GATE-EVIDENCE-04-phase-terminal.md` § SC#3 | closed |
| T-45-15 | Tampering | The QUA-03 scan written naively (token counts) reporting a false clean because prose false positives balance | medium | mitigate | D-09 forbids the count comparison; `45-GATE-EVIDENCE-04-qua03-comment-scan.md` reproduces an opener-stack walk with fence and inline-backtick exclusion, plus three self-checks (same-line pair neutrality, zero-opener safety, LIFO/ascending residual pairing) proving the pairing semantics | closed |
| T-45-16 | Elevation of Privilege | An out-of-scope `typsphinx/` change riding along inside a documentation phase | medium | mitigate | Terminal gate diffs `typsphinx/` against baseline `8c74b85`; re-confirmed at audit time on current HEAD: `git diff --name-only 8c74b85 HEAD -- typsphinx/` → `typsphinx/template_engine.py` only. Full hunk diff recorded verbatim in the evidence file | closed |
| T-45-02 | Denial of Service | Docs build when `CHANGELOG.md` is missing (partial checkout, or the `ja` submodule build) | low | mitigate | docutils' `include` fails loudly with a build error rather than rendering an empty page; recorded as a backstop truth and re-checked at verify time (`45-GATE-EVIDENCE-01-include-shape.md:210` — "does not paper over a missing source file with a blank-but-successful page") | closed |
| T-45-10 | Tampering | A future edit silently re-introducing the false claim or renaming the derived target | low | mitigate | `tests/test_quickstart_docs_gate.py::TestPublishedQuickstartTextMatchesBuild` runs in every CI lane (no skip marker, no `slow` marker) and fails if prose and measured build diverge | closed |
| T-45-11 | Information Disclosure | The quickstart gate fixture writing build output into the repository tree | low | mitigate | Gate builds into pytest's `tmp_path`, following `tests/test_default_typst_documents_gate.py`; nothing is written under `tests/fixtures/` at run time | closed |
| T-45-14 | Information Disclosure | An unterminated `<!--` in a planning record hiding the rest of the file from every downstream reader (QUA-03) | low | mitigate | Whole-file fence- and backtick-aware opener-stack scan against `.planning/PROJECT.md` at `d37a3ab`: 34 openers, 34 closers, zero residual; self-checked on three crafted inputs; recorded in `45-GATE-EVIDENCE-04-qua03-comment-scan.md` | closed |
| T-45-01 | Information Disclosure | `.. include:: ../../CHANGELOG.md` path traversal out of `docs/source/` | low | accept | Accepted — see AR-01 | closed |
| T-45-03 | Tampering | myst-parser rendering raw HTML from Markdown into published pages | low | accept | Accepted — see AR-02 | closed |
| T-45-08 | Information Disclosure | The changelog fixture reaching outside its directory to read a repository-root file | low | accept | Accepted — see AR-03 | closed |
| T-45-04 | Spoofing | RTD `ja` build resolving a different `CHANGELOG.md` through the translations-repo submodule | low | accept | Accepted — see AR-04 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-01 | T-45-01 | The include path is a fixed literal in a repo-tracked file, never user- or build-input-derived; the target is first-party and already public on GitHub. Nothing outside the repository is reachable | Phase 45 plan 45-01 (plan-time disposition) | 2026-08-10 |
| AR-02 | T-45-03 | No `myst_*` config value is set in `docs/source/conf.py` (verified — only the `"myst_parser"` extensions entry at `:41`), so `html_admonition` / `html_image` / raw-HTML extensions stay off at their defaults; `CHANGELOG.md` is first-party repo-tracked content, not user submission | Phase 45 plan 45-01 (plan-time disposition) | 2026-08-10 |
| AR-03 | T-45-08 | Fixed literal relative path to a first-party, already-public, repo-tracked file; no build input controls it | Phase 45 plan 45-02 (plan-time disposition) | 2026-08-10 |
| AR-04 | T-45-04 | Out of this repository's phase scope (45-CONTEXT `<deferred>`); recorded in `45-GATE-EVIDENCE-01-include-shape.md` for the milestone close rather than mitigated here | Phase 45 plan 45-01 (plan-time disposition) | 2026-08-10 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-10 | 17 | 17 | 0 | /gsd-secure-phase 45 (orchestrator, L1 grep-depth) |

### Security Audit 2026-08-10

| Metric | Count |
|--------|-------|
| Threats found | 17 |
| Closed | 17 |
| Open | 0 |

Method: State B (no prior SECURITY.md). Register built from the four PLAN `<threat_model>`
blocks (`register_authored_at_plan_time: true`); no SUMMARY declared `## Threat Flags`.
ASVS level 1 with `block_on: high`, so the L1 short-circuit applied — every mitigation was
verified by direct inspection of the implemented tree and the phase's gate-evidence files,
and no `gsd-security-auditor` subagent was spawned. Two claims were re-measured live at audit
time rather than taken from the evidence files: the `typsphinx/` scope diff against baseline
`8c74b85` (T-45-16) and the absence of any `myst_*` setting in `docs/source/conf.py` (AR-02).

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-10
