---
phase: 45
slug: documentation-currency-carried-hygiene
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: false
wave_0_complete: true
created: 2026-08-09
validated: 2026-08-10
---

# Phase 45 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `45-RESEARCH.md` § Validation Architecture, task rows bound and statuses
> measured by `/gsd-validate-phase 45` on 2026-08-10 against the executed tree.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (config in `pyproject.toml`, `[tool.pytest.ini_options]`) |
| **Config file** | `pyproject.toml` (`testpaths = ["tests"]`, `addopts = "-v --strict-markers"`) |
| **Quick run command** | `uv run pytest tests/test_changelog_extraction.py tests/test_template_engine.py::TestDeriveTypstLang tests/test_typst_lang_gate.py -v` |
| **Phase-45 gate command** | `uv run pytest tests/test_changelog_page_gate.py tests/test_quickstart_docs_gate.py -v` (56 tests incl. the quick run; **16.8s**, all green, zero skips) |
| **Full suite command** | `uv run pytest` then `uv run black --check .` && `uv run ruff check .` && `uv run mypy typsphinx/` |
| **Estimated runtime** | quick ~5s; phase gates ~17s; full suite + lint/type ~3.5 min |
| **Extras required** | `dev` **and** `docs` — without `docs`, `myst-parser` is absent and the four `tests/test_changelog_page_gate.py` gate classes SKIP instead of running (measured: 948 passed/5 skipped with `dev` only vs. 952 passed/1 skipped with both) |

> **Worktree note (CLAUDE.md):** executors run in isolated git worktrees. Provision first with
> `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs`, then run
> **every** command above via `uv run`. Without this, pytest imports the unchanged main-tree
> package and gates stay green/red misleadingly.

---

## Sampling Rate

- **After every task commit:** Run the quick run command, plus `uv run black --check .` and
  `uv run ruff check .` on touched files.
- **After every plan wave:** Run the full suite command (pytest + black + ruff + mypy).
- **Phase gate (before `/gsd-verify-work`):** both `uv run tox -e docs-html` and
  `uv run tox -e docs-pdf` run live, output captured as evidence for DOC-12's "build clean" bar;
  plus the QUA-03 opener-stack script output recorded verbatim.
- **Max feedback latency:** 60 seconds for the code path; docs builds are wave/phase-gated, not
  per-task.

**As executed:** the sampling contract held — no 3 consecutive tasks ran without an automated
verify, and the two net-new gate files (`test_changelog_page_gate.py`, `test_quickstart_docs_gate.py`)
both landed in `test(...)`-typed commits (`13d7743`, `687fc7d`) inside their own plans' waves.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| T1 (`687fc7d`) | 45-03 | W1 | DOC-11 | T-45-09, T-45-11 | Fixture builds into `tmp_path`, never the repo tree | build-check | `uv run pytest tests/test_quickstart_docs_gate.py::TestQuickstartFirstPdfGate -v` — asserts the Quick-Start-mirroring fixture emits `<project>.pdf` **and** does not emit `index.pdf`; expected stem computed from the same `make_filename_from_project` helper the builder calls | ✅ `tests/test_quickstart_docs_gate.py`, `tests/fixtures/quickstart_docs_gate/` | ✅ green (2 tests) |
| T2–T3 (`7ed6457`, `d6fe2d9`) | 45-03 | W1 | DOC-11 | T-45-09, T-45-10 | Prose cannot drift from measured behaviour | prose↔build binding | `uv run pytest tests/test_quickstart_docs_gate.py::TestPublishedQuickstartTextMatchesBuild -v` — binds `README.md` + `quickstart.rst` text to the measured build; no skip marker, no `slow` marker, so it runs in every CI lane | ✅ same file | ✅ green (3 tests) |
| T3 (`b6b1778`) | 45-01 | W1 | DOC-12 | T-45-SC, T-45-01, T-45-02, T-45-03 | `myst-parser>=5.0` in the `docs` extra only (D-01); no `myst_*` config, so raw-HTML extensions stay off | structural | `uv run pytest tests/test_changelog_page_gate.py::TestPublishedChangelogPageDelegates -v` — `changelog.rst` carries the `include::` directive and **zero** hand-maintained release history | ✅ `tests/test_changelog_page_gate.py` | ✅ green (2 tests) — **upgraded past the seed**, which recorded "N/A — code review of diff, no test possible pre-Phase-46" |
| T1–T3 (`0fbfe1d`, `66304e2`, `13d7743`) | 45-02 | W2 | DOC-12 | T-45-05, T-45-06 | Extractor untouched; `test_unreleased_headings_do_not_leak` is an acceptance gate | build-check | `uv run pytest tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage -v` — real `-b html` build of the whole `docs/source` tree; asserts all **12** release strings (`0.4.1`…`0.7.0`, incl. the backfilled `0.4.4`) render, and exactly one `Changelog` heading | ✅ same file | ✅ green (2 of the 3 tests in this class) |
| T3 (`13d7743`) | 45-02 | W2 | DOC-12 | T-45-07 | "Clean" is a measured delta, not a green exit code | build-check | `test_build_emits_no_changelog_warnings` — zero `WARNING` lines mentioning `changelog`, corroborated by `45-GATE-EVIDENCE-02-docs-build-clean.md`: `html=1, pdf=1, changelog_attributable=0` — **delta 0/0/0** vs. the 45-01 baseline at `8c74b85`, fresh output dir per build | ✅ same file + evidence | ✅ green |
| T3 (`13d7743`) | 45-02 | W2 | DOC-12 | T-45-06, T-45-08 | Fixture reads the real repo-root `CHANGELOG.md` by fixed literal path | build-check | `uv run pytest tests/test_changelog_page_gate.py::TestChangelogIncludeCompilesToPdf -v` — real `-b typstpdf` compile, asserts `%PDF` magic plus extracted content (`slow`-marked; skips without `docs`/`typst-py`) | ✅ same file + `tests/fixtures/changelog_include_gate/` | ✅ green (ran, not skipped) |
| T1 (`d37a3ab`) | 45-04 | W3 | QUA-02 | T-45-12, T-45-13 | `re.fullmatch(r"[a-z]{2,3}", head)` preserved verbatim (`template_engine.py:133`) — ASVS V5 | regression | `uv run pytest tests/test_template_engine.py::TestDeriveTypstLang tests/test_typst_lang_gate.py -v` — green **before and after** the refactor (39/39 both times); both assert warning *content*, so a green run on both sides is itself the identity proof, backed by a character-for-character message capture | ✅ existing coverage sufficient | ✅ green (18 + 21 = 39) |
| T1 (`d37a3ab`) | 45-04 | W3 | QUA-02 (structural) | — | N/A | structural | *No standing test.* "Exactly one `logger.warning(` inside `derive_typst_lang()`" was measured once in `45-GATE-EVIDENCE-04-phase-terminal.md` § SC#3 and re-measured at audit time | ❌ none — **moved to Manual-Only** per user decision 2026-08-10 (Wave 0 pre-labelled it "optional, low value") | 🔒 manual-only |
| T2 (`255c2e0`) | 45-04 | W3 | QUA-03 | T-45-14, T-45-15 | Opener-stack walk with fence + inline-backtick exclusion; naive token counts forbidden by D-09 | verification | *No standing guard by decision (D-07).* One-off scan recorded in `45-GATE-EVIDENCE-04-qua03-comment-scan.md`: 34 openers / 34 closers / **0 residual** at `d37a3ab`, plus 3 self-checks | 🔒 by design — see Manual-Only | 🔒 manual-only |
| T3 (`d850ebf`) | 45-04 | W3 | (SC#5 regression guard) | T-45-16 | `typsphinx/` change confined to QUA-02's refactor | full-suite | `uv run pytest` → **952 passed, 1 skipped**; `black --check .` / `ruff check .` / `mypy typsphinx/` all exit 0; `git diff --name-only 8c74b85 HEAD -- typsphinx/` → `template_engine.py` only (re-confirmed at audit time) | ✅ existing full suite is the guard | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky · 🔒 manual-only*

**Measured at audit time (2026-08-10, main tree, `dev`+`docs` provisioned):**
`tests/test_changelog_page_gate.py` (6) + `tests/test_quickstart_docs_gate.py` (5) +
`tests/test_changelog_extraction.py` (6) + `TestDeriveTypstLang` (18) + `tests/test_typst_lang_gate.py` (21)
= **56 passed in 16.79s, zero skips.**

> Note on a count in the phase evidence: `45-GATE-EVIDENCE-04-phase-terminal.md` § SC#3 splits the
> QUA-02 pinning suites as "18 tests + 18 tests"; the actual split is 18 + 21. Its stated **total**
> (39/39) is correct and is the number the identity proof rests on — the per-file split is a
> transcription slip, not a coverage gap.

---

## Wave 0 Requirements

- [x] A build-check asserting the rendered changelog page contains all 12 previously-missing
      versions (`0.4.4` through `0.7.0`) — **delivered** as
      `TestChangelogPageContentCoverage::test_rendered_page_carries_every_release` (HTML) plus
      `TestChangelogIncludeCompilesToPdf` (extracted PDF text).
- [x] A build-check capturing zero `WARNING:` lines attributable to the changelog page —
      **delivered** as `test_build_emits_no_changelog_warnings`, with the delta-against-baseline
      framing preserved in `45-GATE-EVIDENCE-01/02` (0/0/0).
- [ ] *(Optional, low value)* A structural one-liner asserting `derive_typst_lang()` contains
      exactly one `logger.warning(` call. **Declined 2026-08-10** — the existing 39-test
      behavioural coverage already proves identity; moved to Manual-Only rather than adding a
      standing guard. This is the sole reason `nyquist_compliant` stays `false`.
- [x] **No new test infrastructure for QUA-03.** D-07's decline was honoured — the opener-stack
      scan ran once, its result and script were recorded as evidence, and nothing was added to
      the pytest suite.

*Framework install: none needed — pytest was already fully configured. The phase's only new
tooling dependency is `myst-parser>=5.0`, landed in the `docs` extra of
`[project.optional-dependencies]` only (`pyproject.toml:53`) — **not** `[project].dependencies`,
honouring D-01's zero-new-runtime-dependency invariant.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `derive_typst_lang()` emits its rejection warning from exactly one `logger.warning(` site | QUA-02 | Structural, not behavioural. The 39 existing tests already pin the rendered message character-for-character, so a standing structural guard adds no failure-detection power — Wave 0 pre-labelled it "optional, low value" and the user declined it on 2026-08-10 | `grep -n "logger.warning" typsphinx/template_engine.py` and confirm exactly one hit falls inside `derive_typst_lang()`'s line span (currently `84`–`148`; the hit is at `141`). The second hit (`303`) belongs to `TemplateEngine._resolve_template` and is unrelated |
| `.planning/PROJECT.md` comment balance | QUA-03 | D-07 explicitly declines a standing recurrence guard; this is a one-off verification, not an ongoing invariant | Re-run the fence/backtick-aware opener-stack scan reproduced verbatim in `45-GATE-EVIDENCE-04-qua03-comment-scan.md`; expect `len(stack) == 0`. A naive `<!--`/`-->` count is **not** valid (D-09) — `.planning/REQUIREMENTS.md:141` and `.planning/ROADMAP.md:731` are measured false-positive sites |
| Quick Start reads accurately to a human | DOC-11 | "A reader is not surprised" is a comprehension property; the automated fixture proves the *behaviour* matches, not that the *prose* explains it | Read README Quick Start top-to-bottom against the real build output; confirm it states (a) what `typst_documents` does, (b) when it must be set, (c) the derived default incl. the `<project>.typ` name shape, (d) that an explicit setting overrides the default, (e) which documents become PDFs |
| Changelog page heading nesting in the PDF outline | DOC-12 | Cosmetic rendering quality under the myst include + Phase 44.1's relative heading-depth offset — no compile-fatal risk, but only a real build shows it (RESEARCH Open Question 1) | After `tox -e docs-pdf`, open the PDF outline and confirm changelog release headings nest sensibly rather than flattening or over-indenting |
| Shortcut-reference-link rendering of `[0.7.0]`-shaped headings | DOC-12 | CommonMark resolves these against `CHANGELOG.md`'s own tail link definitions; mechanically fine (translator handles `reference` nodes) but visual acceptability is a judgement call (RESEARCH Open Question 2) | Inspect the rendered HTML and PDF headings; confirm linked headings are acceptable or suppress the link definitions |
| Phase 46 one-line-addition property | DOC-12 | Cannot be tested before Phase 46 exists | Confirm by diff inspection that adding a `0.7.1` section to `CHANGELOG.md` alone would surface on the docs page with no `changelog.rst` edit. `TestPublishedChangelogPageDelegates` now guards the precondition (the page holds no hand-maintained history), so this reduces to a one-time confirmation during Phase 46 |

---

## Validation Audit 2026-08-10

| Metric | Count |
|--------|-------|
| Gaps found | 1 |
| Resolved | 0 |
| Escalated | 1 (QUA-02 structural → manual-only, by user decision) |

**Method.** State A (VALIDATION.md existed in `draft`). Task rows were bound to the 12 executed
task commits across plans 45-01…45-04, and every automated command in the map was re-run live on
the main tree with both `dev` and `docs` extras provisioned — 56 passed, zero skips, 16.79s. Two
structural claims were re-measured rather than taken from the evidence files: the `typsphinx/`
scope diff against baseline `8c74b85`, and the `logger.warning` call-site span inside
`derive_typst_lang()`. No `gsd-nyquist-auditor` subagent was spawned, since the single gap was
resolved by decision rather than by generating a test.

**Why `nyquist_compliant: false`.** Exactly one requirement-level check has no standing automated
guard: QUA-02's "exactly one call site" structural assertion. Its behavioural counterpart is fully
covered (39 tests, message pinned character-for-character), and both Wave 0 and the user judged a
separate structural test not worth a standing guard. QUA-03's absence of a guard is likewise a
recorded decision (D-07), not an oversight. This phase is **PARTIAL by design**, not under-tested.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or a recorded manual-only disposition
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (2 delivered, 1 declined by decision, 1 honoured as a decline)
- [x] No watch-mode flags
- [x] Feedback latency < 60s (quick ~5s, phase gates ~17s)
- [ ] `nyquist_compliant: true` — **not set**: 1 requirement is manual-only by decision (see audit above)

**Approval:** validated (PARTIAL) 2026-08-10
