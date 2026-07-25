---
phase: 29
slug: rtd-build-establishment-english-parent-pdf-path-decision
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-25
---

# Phase 29 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `29-RESEARCH.md` § "Validation Architecture". Source of truth for the
> classification is that section plus CONTEXT.md's D-12 / D-15.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (already configured — `pyproject.toml [tool.pytest.ini_options]`, `testpaths = ["tests"]`) |
| **Config file** | `pyproject.toml` (no separate `pytest.ini`) |
| **Quick run command** | `pytest tests/test_readthedocs_config.py -x` |
| **Full suite command** | `pytest` |
| **Estimated runtime** | ~2 seconds (quick) / full suite as today — this phase touches no `typsphinx/` code |

**Scope note (load-bearing, do not "improve" away):** only the two local checks below are pytest-suite
members. The live checks (HTTP fetches of RTD URLs, raw-build-log reads, downloading and comparing the
RTD-built PDF) are **one-off commands run by hand with their output pasted verbatim into
`29-VERIFICATION.md`**, per D-15. Wrapping them in a committed pytest fixture would plant a flaky,
unreproducible network dependency inside an otherwise hermetic suite — D-15 already rejected the
analogous "committed comparison script" idea for exactly this reason.

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_readthedocs_config.py -x` (fast, no network)
- **After every plan wave:** Run `pytest` — bar is "suite stays exactly as green as before", since this
  phase changes no runtime code
- **Before `/gsd-verify-work`:** Full suite must be green **plus** the live-fetch / raw-log evidence must
  be recorded in `29-VERIFICATION.md`. The automated suite alone cannot certify this phase; the live
  evidence is mandatory, not supplementary (REQUIREMENTS.md invariant #7 — a green build proves nothing
  about content).
- **Max feedback latency:** ~2 seconds for the local checks

---

## Per-Task Verification Map

*Seeded as draft — task IDs are filled by `/gsd-validate-phase` after plans exist. Rows below map the
phase's requirements, not yet individual tasks.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | RTD-01 (config shape) | — | N/A | unit | `pytest tests/test_readthedocs_config.py::test_readthedocs_yaml_shape -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | RTD-01 (language seam) | — | N/A | unit | `pytest tests/test_readthedocs_config.py::test_language_seam_precedence -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | RTD-01 (live half) | — | N/A | live-fetch + `human_needed` | real HTTP GET of `/en/latest/`; raw build-log excerpt pasted verbatim | N/A | ⬜ pending |
| TBD | TBD | TBD | RTD-02 (Branch A compare) | — | N/A | live one-off (D-15) | `pypdf` page-count / text / embedded-`/BaseFont` checks, output pasted verbatim | N/A by design | ⬜ pending |
| TBD | TBD | TBD | RTD-02 (D-12 check 4) | — | N/A | `human_needed` | owner opens the two CJK-bearing pages, confirms no tofu | N/A | ⬜ pending |
| TBD | TBD | TBD | RTD-03 (Branch B link) | — | N/A | live-fetch | `curl -sI https://github.com/YuSabo90002/typsphinx/releases/latest/download/typsphinx.pdf`, output recorded | N/A | ⬜ pending |
| TBD | TBD | TBD | RTD-04 (root URL) | — | N/A | live-fetch | real HTTP GET of the documentation root, output recorded | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_readthedocs_config.py` — new file, two tests:
  1. `test_readthedocs_yaml_shape` — parse `.readthedocs.yaml` and assert the required v2 keys exist
     with correct nesting (`version`, `build.os`, `build.tools.python`, `sphinx.configuration`,
     `python.install`). Confirm `import yaml` is available before relying on PyYAML; fall back to
     explicit string/key assertions if it is not importable outside a build context.
  2. `test_language_seam_precedence` — assert the `language` seam resolves `"en"` when both
     `READTHEDOCS_LANGUAGE` and `SPHINX_LANGUAGE` are unset, resolves each env var's value when set, and
     that `READTHEDOCS_LANGUAGE` wins over `SPHINX_LANGUAGE`. `conf.py` is not importable via plain
     `import` in the pytest path — **factor the seam into a tiny testable expression rather than
     standing up a full `sphinx.testing` app fixture just to assert an `os.getenv` chain.**
- [ ] `tests/conftest.py` — **no changes needed**; this phase adds no new fixture requirements.
- [ ] Framework install — **none**. pytest, PyYAML (transitively via Sphinx), and `pypdf`
      (`dev` extra, `pyproject.toml:46`) are all already available.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| RTD project creation + GitHub connection; Admin Language = English; Default Version left at `latest` | RTD-01, RTD-04 | Web-UI actions in a third-party dashboard; no test can assert the click happened. Criteria 1–4 verify the *outcome* via real fetches and the raw log, never the action itself. | Owner performs in the RTD dashboard; **confirm the slug `typsphinx` is unclaimed before creating** (D-01/D-02 — slugs are not self-service changeable and Phase 31 burns this URL into `README.md` / `pyproject.toml` / About→Website). If taken, **stop and consult the owner** — no silent fallback. |
| Reading the raw build log end to end and recording the `@preview` verdict | RTD-02 (SC#2) | The verdict must be a **recorded log excerpt, not an inference** (D-07). Branch A needs the four Typst Universe packages resolving *and* zero `latexmk` / `pdflatex` / `.tex` lines anywhere; Branch B needs the registry fetch shown blocked/failed. | Owner opens the build-detail page's raw log, pastes the decisive excerpt verbatim into `29-VERIFICATION.md`. |
| SC#1's "installed from the checked-out commit, not resolved from a PyPI index" | RTD-01 | The exact distinguishing `uv sync` log wording is **unconfirmed** (RESEARCH.md Open Question #1 / assumption A3). Do **not** pre-commit the plan to a grep pattern. | Read the first real build's log, identify the actual distinguishing line, record it verbatim. |
| D-12 check 4 — no tofu / glyph substitution on the two CJK-bearing pages | RTD-02 | Text extraction cannot detect glyph substitution — a tofu-rendered PDF still extracts the correct characters (D-14). Only a human look closes this. | Owner opens the pages rendering `docs/source/user_guide/configuration.rst:186,240` (「表 1」「図 1」「图 1」「圖 1」) in the RTD-downloaded PDF and confirms real glyphs. Record honestly as `human_needed`, never asserted machine-verified. |

**Abstention culture (STATE.md § Accumulated Context):** an honest `human_needed` beats an unevidenced
assertion. Do not invent a machine check for anything in this table.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies, **or** are explicitly classified
      `human_needed` / live-only in the table above
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (`tests/test_readthedocs_config.py`)
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s for the local checks
- [ ] Live-fetch and raw-log evidence recorded verbatim in `29-VERIFICATION.md` (D-15)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
