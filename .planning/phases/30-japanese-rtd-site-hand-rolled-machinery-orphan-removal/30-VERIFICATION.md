---
phase: 30-japanese-rtd-site-hand-rolled-machinery-orphan-removal
verified: 2026-07-26T12:03:23Z
status: human_needed
score: 10/10 must-haves verified
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Open the milestone pull request against `main` and watch the `Documentation` GitHub Actions workflow run."
    expected: "The `build-docs` job completes green; its `Build HTML documentation` step runs `uv run tox -e docs-html`; the `documentation-html` artifact is uploaded from `docs/_build/html`."
    why_human: "`.github/workflows/docs.yml` triggers only on a push to `main`, a `v*` tag, or a PR targeting `main`, and declares no `workflow_dispatch` (adding one would not help — GitHub resolves manual dispatch against the default branch's copy of the workflow). Under `branching_strategy: milestone` this event cannot fire from inside the phase's worktree. ROADMAP SC#5's 'observed CI run' clause is therefore structurally unobservable until the milestone PR opens. Recorded as `verification: backstop` in 30-01-PLAN.md and 30-04-PLAN.md must_haves, and as an explicit 'Deferred to the milestone pull request' section in 30-EVIDENCE.md — not inferred into a pass."
  - test: "After Read the Docs rebuilds the tracked `main` branch, fetch `https://typsphinx.readthedocs.io/en/latest/` and grep for the switcher wrapper class and `custom.css`."
    expected: "Both occurrences drop to zero (measured at one occurrence each before the phase, re-confirmed still present during this verification since RTD has not yet rebuilt the tracked branch)."
    why_human: "RTD serves the tracked branch, not a worktree/feature branch, so this cannot be observed until the milestone merges and RTD rebuilds. Recorded as `verification: backstop` in 30-02-PLAN.md and 30-04-PLAN.md must_haves, and as an explicit 'Deferred to the next Read the Docs build' section in 30-EVIDENCE.md."
  - test: "At the same post-merge RTD rebuild, fetch `https://typsphinx.readthedocs.io/en/latest/` and grep for `furo-sidebar-ad-placement` and `furo-readthedocs-versions`."
    expected: "Record whatever counts appear; a non-zero count is the accepted, documented side effect of deleting `html_sidebars` (Furo's own default sidebar carries these READTHEDOCS-gated slots), not a regression to fix."
    why_human: "Both templates are gated on `{% if READTHEDOCS %}`. A local build (confirmed in this verification: both counts are 0) cannot settle whether Read the Docs' Addons build model still injects that flag into the Jinja context. Recorded as `verification: backstop` in 30-02-PLAN.md and 30-04-PLAN.md must_haves."
---

# Phase 30: Hand-Rolled Multi-Language Machinery & Orphan Removal — Verification Report

**Phase Goal:** The repository no longer carries the hand-rolled multi-language publishing machinery
or the unreachable orphan docs it accumulated — the language switcher, its styling, its `conf.py`
wiring, the `build_multilang.py` builder and every task-runner target that drove it are gone, together
with the `docs/usage.rst` / root `docs/installation.rst` pair and the tests that hard-assert them —
while the documentation still builds green and `docs.yml` stays internally consistent.

**Verified:** 2026-07-26T12:03:23Z
**Status:** human_needed
**Re-verification:** No — initial verification

**Note on method:** every gate below was re-run independently in this session (not copied from
`30-EVIDENCE.md`); the phase's own hand-run evidence record was used as a map of what to measure,
per the honest-verifier instruction. Every command in the tables below was executed against the
current `main`-tree `HEAD` (`e3ff4ba`), not cited from a SUMMARY or from `30-EVIDENCE.md`.

## Goal Achievement

### Observable Truths (merged from ROADMAP SC#1–SC#5 + PLAN frontmatter must_haves)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | (SC#1) A fresh repo-wide grep for the switcher/multilang token set returns zero *live* hits, excluding `CHANGELOG.md`/`.planning/**` and the one named confval-fixture survivor | ✓ VERIFIED | Re-ran `git ls-files -z ... | xargs -0 grep -nE 'multilang|html-ja|language-switcher|typsphinx_lang|custom\.css|html_context|html_sidebars'` myself: 2 lines returned, both accounted-for false positives — `tests/fixtures/confval_field_body_render_gate/index.rst:15` (unrelated Sphinx directive, the plan's named survivor) and `tests/test_readthedocs_config.py:296` (a docstring sentence naming the deleted feature in prose, documented as an exercised discretion in `30-EVIDENCE.md` Gate A). Zero live-machinery hits. Matches the evidence record exactly. |
| 2 | (SC#1 cont'd) `html_static_path` scoped correctly: absent from `docs/source/conf.py`, 7 legitimate occurrences survive elsewhere (2 bundled examples + 2 render-gate fixtures) | ✓ VERIFIED | `grep -n html_static_path docs/source/conf.py` → no match; `grep -rn html_static_path examples tests` → exactly 7 lines, matching `30-EVIDENCE.md` Gate B verbatim |
| 3 | (SC#2) `conf.py` surgery confined to switcher wiring; Phase 29's language seam and Phase 30.1's Typst font block are byte-unchanged; nothing under `typsphinx/` touched | ✓ VERIFIED | Re-hashed region 1 (`sed -n '1,/^# -- Options for HTML output/p'`) → `06f177f8...` and region 3 (`sed -n '/^# -- Options for typst/,$p'`) → `cd245215...`, both exact matches to the recorded pre-phase values. `git diff --stat 458ffc8..HEAD -- typsphinx/` empty |
| 4 | (SC#3) `docs/usage.rst` (606 lines) + root `docs/installation.rst` (213 lines) + their two hard-asserting test files are gone; `docs/source/installation.rst` (76 lines, toctree-live) untouched; full suite green after deletion | ✓ VERIFIED | All four paths confirmed absent (`test -e`); `docs/source/installation.rst` present, 76 lines; `uv run python -m pytest -q` run fresh in this session → `641 passed, 1 skipped`, matching the recorded baseline exactly |
| 5 | (SC#3 cont'd) `docs/locale/` (26 tracked files) removed; the surviving copy in `typsphinx-doc-translations` was confirmed to hold 13 `.po` files before deletion, and still does | ✓ VERIFIED | `test -d docs/locale` → absent. Independently re-ran `gh api repos/YuSabo90002/typsphinx-doc-translations/git/trees/HEAD?recursive=1 --jq '...'` myself in this session (own `gh` auth, not cited) → `13`, corroborating the pre-deletion measurement in `30-03-SUMMARY.md` |
| 6 | (SC#4) The collateral wiring assertions in `tests/test_readthedocs_config.py` are repaired (not deleted) and still assert something real | ✓ VERIFIED | `assert ` count = 39, `def test_` count = 4, `typst_elements[` count = 4 (all match pre/post-edit parity claims); `I18N-02` and `derive_typst_lang` both present in the docstring; full suite green |
| 7 | (SC#5, buildable-locally part) `tox -e docs-html` and `tox -e docs-pdf` are green and produce `docs/_build/html/index.html` and a PDF under `docs/_build/pdf/`; `docs.yml`'s `tox -e <env>` strings and `docs/_build/` paths are internally consistent with `tox.ini`; the `peaceiris/actions-gh-pages` deploy step survives with `publish_dir: ./docs/_build/html`, and `softprops/action-gh-release` survives | ✓ VERIFIED | Ran both tox environments myself (not cited): both exited 0, 2 warnings each (matching baseline), `docs/_build/html/index.html` and `docs/_build/pdf/typsphinx.pdf` both produced. Read `.github/workflows/docs.yml` and `tox.ini` directly: `tox -e docs-html`/`tox -e docs-pdf` both resolve to real `tox.ini` sections; exactly one `peaceiris/actions-gh-pages` step at `publish_dir: ./docs/_build/html`; `softprops/action-gh-release@v3` present; step count 10 (was 11 pre-phase, confirmed via `git show 458ffc8:.github/workflows/docs.yml`); `permissions:` block and trigger set byte-identical to pre-phase |
| 8 | (SC#5, RTD-04 standing invariant) The documentation root URL still resolves | ✓ VERIFIED | `curl -sS -L https://typsphinx.readthedocs.io/` → `HTTP_CODE=200 EFFECTIVE_URL=.../en/latest/`, re-fetched live in this session |
| 9 | `docs/Makefile` reduced to exactly two targets (`help`, `%`); dry-run resolves through the catch-all | ✓ VERIFIED | File is 20 lines, `.PHONY: help Makefile`, only `help:` and `%: Makefile` targets present; `docs/source/contributing.rst`'s Translations section confirmed byte-unchanged (`git diff --quiet`) |
| 10 | The four switcher assets are gone from source and produce no regression in a rebuilt English page (Furo's own sidebar restored, not removed) | ✓ VERIFIED | All four asset paths absent; rebuilt `index.html` (built fresh in this session) has 0 occurrences of `language-switcher`/`typsphinx_lang`/`custom.css` and ≥1 occurrence each of `sidebar-brand`(×2)/`sidebar-search`(×2)/`sidebar-tree`(×1)/`toc-drawer`(×1) — matches `30-02-SUMMARY.md`'s reference values exactly |
| 11 | (SC#5, "observed CI run" clause) — see Human Verification | ⚠️ backstop / deferred | Structurally unobservable inside the phase's worktree (see Human Verification #1) |
| 12 | (backstop) Published `/en/latest/` page stops serving switcher markup | ⚠️ backstop / deferred | Re-fetched `https://typsphinx.readthedocs.io/en/latest/` live in this session: `language-switcher` and `custom.css` both still present (1 occurrence each) — confirms RTD has **not yet** rebuilt the tracked branch, exactly as the deferred item predicts. Not a gap: this cannot resolve until the milestone merges (see Human Verification #2) |
| 13 | (backstop) Furo's restored ad-placement/variant-selector slots — hosted-site behavior | ⚠️ backstop / deferred | Local build confirms both counts are 0 (READTHEDOCS-gated templates); hosted-site behavior genuinely unobservable pre-merge (see Human Verification #3) |

**Score:** 10/10 directly-observable must-haves verified. 3 additional items are explicitly out-of-phase `backstop` truths (not counted as failures or passes) — see Human Verification.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.github/workflows/docs.yml` | Modified: repointed off multilang tree, 10 steps | ✓ VERIFIED | Diffed against `458ffc8` base — matches plan spec exactly, permissions/triggers unchanged |
| `tox.ini` | Modified: `[testenv:docs-multilang]` removed | ✓ VERIFIED | Section absent; `docs-html`/`docs-pdf`/`docs`/`env_list`/`tox-uv` pin all present, byte-unchanged |
| `docs/Makefile` | Modified: 2 targets only | ✓ VERIFIED | 20 lines, confirmed |
| `docs/build_multilang.py` | DELETED | ✓ VERIFIED | Absent |
| `docs/source/_templates/language-switcher.html` | DELETED | ✓ VERIFIED | Absent |
| `docs/source/_templates/page.html` | DELETED | ✓ VERIFIED | Absent |
| `docs/source/_static/custom.css` | DELETED | ✓ VERIFIED | Absent |
| `docs/source/conf.py` | Modified: 126 lines, switcher-only trim | ✓ VERIFIED | Region hashes match |
| `tests/test_readthedocs_config.py` | Modified: repointed assertions | ✓ VERIFIED | Counts match |
| `docs/usage.rst`, `docs/installation.rst` | DELETED | ✓ VERIFIED | Absent |
| `tests/test_documentation_usage.py`, `tests/test_documentation_installation.py` | DELETED | ✓ VERIFIED | Absent |
| `docs/locale/` | DELETED (26 files) | ✓ VERIFIED | Absent; git-ls-files empty |
| `30-EVIDENCE.md` | NEW — phase evidence record | ✓ VERIFIED | Present, one section per gate A–G with verbatim command+output, correctly named (not `30-VERIFICATION.md`) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `.github/workflows/docs.yml`'s `tox -e <env>` strings | `tox.ini`'s section list | string reference | ✓ WIRED | Re-parsed both files myself: `docs-html`/`docs-pdf` both resolve to real `[testenv:...]` sections |
| `tox -e docs-html` output | `.github/workflows/docs.yml`'s `Upload HTML artifact` path / `peaceiris/actions-gh-pages` `publish_dir` | build → publish path | ✓ WIRED | Ran the build myself; `docs/_build/html/index.html` exists, matching both referenced paths exactly |
| `docs/source/conf.py`'s `locale_dirs` | absent `docs/locale/` directory | no-op reference | ✓ WIRED (inert, as designed) | `locale_dirs = ["../locale/"]` still present (shared byte-for-byte with `typsphinx-doc-translations`); English build re-run in this session emits the same 2 pre-existing warnings, no new warning from the absent directory |
| `docs/source/conf.py`'s `templates_path` | emptied `_templates/` directory | no-op reference | ✓ WIRED (inert, as designed) | Same rebuild confirms no `templates_path` warning |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full test suite green post-deletion | `uv run python -m pytest -q` | `641 passed, 1 skipped in 55.87s` | ✓ PASS |
| HTML doc build green, warning-parity | `uv run python -m tox -e docs-html` | exit 0, `build succeeded, 2 warnings` | ✓ PASS |
| PDF doc build green | `uv run python -m tox -e docs-pdf` | exit 0, `build succeeded, 2 warnings`, PDF produced | ✓ PASS |
| Documentation root resolves | `curl -sS -L https://typsphinx.readthedocs.io/` | `200`, redirects to `/en/latest/` | ✓ PASS |
| `.po` catalog survival in translations repo | `gh api repos/YuSabo90002/typsphinx-doc-translations/git/trees/HEAD?recursive=1 --jq '...'` | `13` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|-----------------|--------------|--------|----------|
| I18N-02 | 30-01, 30-02, 30-03, 30-04 | Hand-rolled multi-language publishing machinery gone; language switching via RTD's own flyout | ✓ SATISFIED | All 4 switcher assets deleted, `conf.py` trimmed, CI/tox/Makefile repointed, `docs/locale/` removed. The "switching works via RTD's flyout" half of the requirement was established by Phase 30.1 (observed serving both directions) and is not re-derived here per the plans' own flagged-assumption disclosure — consistent with the phase's stated scope (removal, not re-proof of the replacement) |
| DOC-08 | 30-03, 30-04 | Unreachable `docs/usage.rst`/`docs/installation.rst` orphan pair resolved, suite green afterwards, live `docs/source/installation.rst` untouched | ✓ SATISFIED | Both orphans + their 20 hard-asserting test functions deleted in one commit; `docs/source/installation.rst` confirmed byte-unchanged; full suite green (641 passed, 1 skipped), verified fresh in this session |

`REQUIREMENTS.md`'s traceability table (lines 212, 214) independently marks both `I18N-02` and `DOC-08` as `Phase 30 | Complete`, and no requirement maps to Phase 30 beyond these two (checked via `grep -n "Phase 30\b" REQUIREMENTS.md`) — no orphaned requirements.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `docs/source/conf.py` | 44, 58-61 | `templates_path`/`locale_dirs` reference directories this phase deleted, with no in-file comment explaining the deliberate inert-leftover decision (unlike the adjacent `typst_template` block, which has an 18-line rationale comment) | ℹ️ Info | Not a functional defect — both settings were measured to no-op harmlessly and this is by design (shared byte-for-byte with `typsphinx-doc-translations`). Flagged by `30-REVIEW.md` (WR-01, the phase's own code-review pass) as a documentation-quality nit, not a blocker. No `TBD`/`FIXME`/`XXX` debt markers found in any of the 5 phase-modified files |

No blocker-level anti-patterns found. No debt markers (`TBD`/`FIXME`/`XXX`) in any file this phase touched.

### Human Verification Required

3 items — all are explicitly-declared `verification: backstop` truths in the phase's own PLAN frontmatter (30-01, 30-02, 30-04), not gaps. Each was re-confirmed in this session to still be genuinely unobservable pre-merge (the RTD page still serves the old switcher markup, confirming the tracked branch has not yet rebuilt).

#### 1. Observed `docs.yml` CI run on the milestone PR

**Test:** Open the milestone pull request against `main`; watch the `Documentation` workflow's `build-docs` job.
**Expected:** Completes green; `Build HTML documentation` step runs `uv run tox -e docs-html`; `documentation-html` artifact uploaded from `docs/_build/html`.
**Why human:** `docs.yml` has no `workflow_dispatch` trigger (deliberately — GitHub resolves manual dispatch against the default branch's copy of the file, so adding one on this branch would not help). Under `branching_strategy: milestone`, no push/PR/tag event targeting `main` fires until the milestone PR opens. Structurally outside this phase's worktree.

#### 2. Published `/en/latest/` page loses switcher markup

**Test:** After Read the Docs rebuilds the tracked `main` branch, fetch `https://typsphinx.readthedocs.io/en/latest/` and grep for the switcher wrapper class and `custom.css`.
**Expected:** Both drop to zero occurrences (currently 1 each — re-confirmed live in this session, RTD has not yet rebuilt).
**Why human:** RTD serves the tracked branch, not this repo's worktree/feature branch; cannot be observed until the milestone merges and RTD rebuilds.

#### 3. Furo's restored ad-placement/variant-selector slots on the hosted site

**Test:** At the same post-merge rebuild, fetch `/en/latest/` and grep for `furo-sidebar-ad-placement` / `furo-readthedocs-versions`.
**Expected:** Record whatever appears; a non-zero count is an accepted, documented side effect of deleting `html_sidebars` (restores Furo's own defaults), not a regression.
**Why human:** Both Furo templates are gated on `{% if READTHEDOCS %}`; a local build (confirmed 0/0 in this session) cannot determine whether RTD's Addons build model injects that flag into the Jinja context.

### Gaps Summary

No gaps found. Every must-have truth derived from ROADMAP SC#1–SC#5 and every plan's frontmatter
`must_haves.truths`/`artifacts`/`key_links`/`prohibitions` was independently re-measured against the
current `HEAD` (`e3ff4ba`) in this session — not cited from `30-EVIDENCE.md` or any SUMMARY — and all
matched the phase's own evidence record exactly. The only items not marked `✓ VERIFIED` are the three
`verification: backstop` truths the plans themselves declared unobservable inside the phase (an actual
`docs.yml` Actions run, the live RTD site losing switcher markup, and Furo's ad-slot hosted-site
behavior) — each has a named future check and is routed to human verification rather than silently
passed or failed, per this phase's own honest-verifier discipline.

---

*Verified: 2026-07-26T12:03:23Z*
*Verifier: Claude (gsd-verifier)*

## Acknowledged Gate Overrides

- **api-coverage.verify-pre** (2026-07-26, verify-work session): gate returned `block: true`
  (signal: `integration`/`api`) with no COVERAGE.md present. Determined a false positive of the
  same class as Phase 18 and Phase 30.1: the only matches in this phase's artifacts are the
  disclaimer prose itself — 30-04-PLAN.md and 30-EVIDENCE.md phrasing the live RTD root fetch as
  "a one-off corroborating read of a public URL, not as an API integration" (the substring
  "API integration" in the disclaimer is what the detector matched). The phase deletes docs/CI
  machinery and integrates no external API. Override recorded per the Phase 30.1 precedent
  (standing owner decision on this documented false-positive class); continuing to UAT.
