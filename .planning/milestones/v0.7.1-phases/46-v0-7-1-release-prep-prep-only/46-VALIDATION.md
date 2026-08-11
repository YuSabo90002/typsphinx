---
phase: 46
slug: v0-7-1-release-prep-prep-only
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: true
created: 2026-08-11
---

# Phase 46 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded by `/gsd-plan-phase` from `46-RESEARCH.md` § Validation Architecture (read in full).
> Per-task rows are filled once plans exist; everything else below is already measured.

**Phase shape, and why it validates unusually.** Phase 46 is a **prep-only release phase**. It ships
no `typsphinx/` source change (D-03, D-27) and adds **zero new test modules**. Its two code edits are
mechanical data changes to *existing* test files — D-22's one-line `.as_posix()` repair at
`tests/test_docs_contract_claims_gate.py:170`, and appending `"0.7.1"` to `RELEASE_VERSIONS` at
`tests/test_changelog_page_gate.py:49-63`. Every validation row below is therefore a **rerun of an
already-existing, already-passing test or gate**, plus a set of evidence-collection commands that are
mechanically assertable but are not pytest tests (the D-21 invariant sweep, the REL-04 preconditions,
the prep/publish fence proof).

Two rows are structurally `human_needed` and must **not** be reported as closed by this phase:
D-22's Windows repair (only a real Windows CI run can prove it — no Windows on this machine) and
REL-04's actual acceptance (only a real tag push at `/gsd-complete-milestone` can generate it).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (Python 3.13.13); config in `pyproject.toml` `[tool.pytest.ini_options]` |
| **Config file** | `pyproject.toml` — `testpaths = ["tests"]`, `addopts = "-v --strict-markers"` |
| **Quick run command** | `uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py tests/test_docs_contract_claims_gate.py -q` (sub-second) |
| **Full suite command** | `uv run pytest -q` (993 tests collected; no default `-m` filter, so the slow full-corpus gate is included) |
| **Estimated runtime** | < 1 s (narrow guards) · ~190 s (full suite) · ~1 s `docs-html` · ~3 s `docs-pdf` · ~30 s corpus gate |

**Execution notes (environment-specific, measured 2026-08-11).**

- **Authority split (D-11).** pytest / `black` / `ruff` / `mypy` authority is the **branch CI run**,
  not local. Local evidence is `tox -e docs-html`, `tox -e docs-pdf`, and the full-corpus gate,
  invoked **per-environment** — a bare `tox` still dies because `.venv/bin/ruff` is a generic-linux
  ELF NixOS rejects (D-11 amendment (b)).
- **`tox -e py312` cannot provision locally** (RESEARCH.md Pitfall 1, new finding): `uv venv -p
  cpython3.12` downloads a standalone CPython whose ELF the NixOS stub loader rejects (exit 127).
  Use `tox -e py313`, or run `uv run pytest` directly. **No plan `<action>` may say "run `tox -e
  py312` locally".**
- **`myst-parser` is in the `docs` extra, not `dev`** (Pitfall 2). Running
  `pytest tests/test_changelog_page_gate.py` against the plain dev `.venv` **silently skips**
  `TestChangelogPageContentCoverage` and `TestChangelogIncludeCompilesToPdf`. Any plan asserting that
  gate must check the summary line for `skipped`, not just `passed`, or invoke it inside a
  `docs`-extras environment.
- `uv run pytest` works in the main tree as of Phase 45.2 (QUA-04); a prior `uv sync --extra dev` is
  still required. `.venv/bin/uv` no longer exists, so no PATH-shadowing hazard remains for `uv`.

---

## Sampling Rate

- **After every task commit:** the narrow, fast guard tests relevant to that task's own edit —
  `tests/test_readme_version_sync.py`, `tests/test_preview_version_sync.py`,
  `tests/test_docs_contract_claims_gate.py` (all sub-second locally).
- **After every plan wave:** the three local-authority items D-11 assigns —
  `tox -e docs-html`, `tox -e docs-pdf`, `uv run pytest tests/test_corpus_gate.py -v` —
  plus a push for the relevant CI run (check run or authority run per D-23).
- **Before `/gsd-verify-work`:** both D-23 CI runs green (run 1 = merge + Windows repair, run 2 =
  bump + CHANGELOG, the SC#3 authority); the D-21 invariant sweep re-run clean on the post-merge
  HEAD; REL-04's two precondition checks recorded; and the fence proof (`git tag -l v0.7.1` and
  `git ls-remote --tags origin v0.7.1`, both empty) taken as **two independent observations**, per
  the `41-HANDOFF.md` precedent.
- **Max feedback latency:** < 1 s (narrow guards) · ~190 s (full suite) · CI run wall-clock for the
  two authority runs.

---

## Per-Task Verification Map

Rows are the requirement→command map from `46-RESEARCH.md` § Validation Architecture. Task IDs are
assigned once plans exist; `{plan}-{task}` placeholders are filled by `/gsd-validate-phase` or by the
executor's SUMMARY frontmatter. Threat refs read `—` throughout: this phase changes no runtime
surface, so its threat register carries no code-level mitigations.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | REL-06 (version literal, SC#1) | — | N/A | unit | `uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml -v` | ✅ existing | ⬜ pending |
| TBD | TBD | TBD | REL-06 (README/pyproject lockstep, SC#1) | — | N/A | unit | `uv run pytest tests/test_readme_version_sync.py -v` | ✅ existing | ⬜ pending |
| TBD | TBD | TBD | REL-06 (`@preview` invariant, SC#1/SC#3) | — | N/A | unit | `uv run pytest tests/test_preview_version_sync.py -v` | ✅ existing | ⬜ pending |
| TBD | TBD | TBD | REL-06 (CHANGELOG page currency, SC#2) | — | N/A | integration (slow, `myst-parser`-gated — see Pitfall 2) | `tox -e docs-html` then `pytest tests/test_changelog_page_gate.py -v` inside a `docs`-extras env | ✅ existing; `RELEASE_VERSIONS` append must land **after** the CHANGELOG entry | ⬜ pending |
| TBD | TBD | TBD | REL-06 (Windows CI regression, D-22) | — | N/A | unit (Linux-provable) **+ CI-only (Windows-provable)** | `uv run pytest tests/test_docs_contract_claims_gate.py -v` (8/8 green locally today) — **the actual proof is D-23 run 1**, see M1 | ✅ existing, one-line edit | ⬜ pending |
| TBD | TBD | TBD | REL-06 (green tree — suite/lint/type, SC#3) | — | N/A | integration | CI: `uv run tox -e py312`/`py313`/`lint`/`type`/`cov` via `.github/workflows/ci.yml` — see M2 | ✅ CI-wired | ⬜ pending |
| TBD | TBD | TBD | REL-06 (green tree — docs builds, SC#3) | — | N/A | integration | `tox -e docs-html`; `tox -e docs-pdf` (both verified green 2026-08-11) | ✅ existing | ⬜ pending |
| TBD | TBD | TBD | REL-06 (full-corpus `-b typstpdf` gate, SC#3) | — | N/A | integration (slow, network-gated, honest-skip) | `uv run pytest tests/test_corpus_gate.py -v` (4 passed / 1 skipped in ~30 s, 2026-08-11) | ✅ existing | ⬜ pending |
| TBD | TBD | TBD | REL-06 (`ja` build, D-12) | — | N/A | integration | single `SPHINX_LANGUAGE=ja` docs-pdf build — exact invocation **`human_needed`**, see M3 | ✅ `docs/source/conf.py` exists | ⬜ pending |
| TBD | TBD | TBD | REL-06 (invariant sweep, D-21/SC#4) | — | N/A | mechanical `git`/`grep`, not pytest | command shapes in `46-RESEARCH.md` § Code Examples "SC#4's invariant sweep"; anchor `v0.7.0` = `75fd8ed`, re-measured on post-merge HEAD | N/A — ad hoc | ⬜ pending |
| TBD | TBD | TBD | REL-04 (**precondition only**, SC#4) | — | N/A | static read + script hand-run | `sed -n '162,168p' .github/workflows/release.yml`; `uv run python scripts/extract_changelog_section.py 0.7.1` | ✅ existing script | ⬜ pending |
| TBD | TBD | TBD | REL-06 (prep/publish fence, SC#5) | — | N/A | mechanical, two independent observations | `git tag -l v0.7.1` **and** `git ls-remote --tags origin v0.7.1` — both must be empty at phase close | N/A — ad hoc | ⬜ pending |
| — | — | — | **REL-04 (actual acceptance)** | — | N/A | **`human_needed`** | N/A — structurally impossible before `/gsd-complete-milestone` | N/A | 🚫 **must NOT be reported closed by this phase** |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky · 🚫 out of reach this phase*

---

## Wave 0 Requirements

**None.** Every test module, fixture, and gate this phase needs already exists and already passes
(or honestly skips) on this machine:

- [x] `tests/test_extension.py` — `test_version_matches_pyproject_toml` (existing)
- [x] `tests/test_readme_version_sync.py` (existing)
- [x] `tests/test_preview_version_sync.py` (existing)
- [x] `tests/test_changelog_page_gate.py` — needs `RELEASE_VERSIONS` to gain `"0.7.1"` (one tuple
      entry, **after** the CHANGELOG entry lands)
- [x] `tests/test_docs_contract_claims_gate.py` — needs D-22's one-line `.as_posix()` repair
- [x] `tests/test_corpus_gate.py` (existing)
- [x] Framework install — none needed

No new fixture, conftest addition, or framework install is required. `wave_0_complete: true` is set
in frontmatter on that basis.

---

## Manual-Only Verifications

| ID | Behavior | Requirement | Why Manual | Test Instructions |
|----|----------|-------------|------------|-------------------|
| M1 | D-22's Windows repair actually turns the two `windows-latest` lanes green | REL-06 | **Not locally reproducible.** Backslash path rendering is a Windows-`pathlib` behaviour; this machine is Linux. The local 8/8-green run proves only that the repair does not *regress* Linux. | Push the D-20 merge + D-22 repair (D-23 **run 1**), then `gh run view <id>` — `Test Python 3.12 on windows-latest` and `Test Python 3.13 on windows-latest` must both be `success`. Baseline: run `31445582363` (`failure`, those two jobs only). |
| M2 | The post-bump tree is green live for pytest / lint / type (SC#3) | REL-06 | D-11 assigns this authority to **CI**, not local: local never sees Windows or macOS, and `tox -e lint` cannot run here at all (`.venv/bin/ruff` ELF, D-11 amendment (b)). | Push the bump + `## [0.7.1]` commit (D-23 **run 2** = SC#3's authority), then read every job's conclusion. Record the run id in the evidence file. |
| M3 | A single `SPHINX_LANGUAGE=ja` docs-pdf build succeeds (D-12) | REL-06 | The exact invocation mechanism in `docs/source/conf.py` was **not read** during research — flagged as Assumption A2 / Open Question 1 rather than guessed. Resolve by reading `conf.py`, do not invent a command. | Read `docs/source/conf.py` for the language switch, then run the single `ja` docs-pdf build and transcribe the result. D-12 replaces Phase 41's four-check glyph bar — both of that bar's triggers were re-measured and neither holds. |
| M4 | REL-04's remainder is **owed, not closed** | REL-04 | Structurally impossible in a prep-only phase: acceptance is a real tag push whose `create-release` job runs to completion. v0.7.0 reported the mechanism as done and the release then failed — this phase must not repeat that. | The phase's own artifacts (`46-HANDOFF.md`, the evidence file) must state in writing that REL-04 remains open. `.planning/todos/pending/2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` stays **pending**. |
| M5 | No irreversible action was taken (SC#5) | REL-06 | Asserts the *absence* of an external side effect across two namespaces (local refs and `origin`); a pytest assertion would be vacuous and would not reach the remote. | At phase close, run both: `git tag -l v0.7.1` and `git ls-remote --tags origin v0.7.1`. Both must return empty. Record both transcripts as **two independent observations**, per `41-HANDOFF.md`. |

---

## Known Environmental Defects (not validation gaps)

Both are filed, unfixed, and out of this phase's scope:

- `.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` — `.venv/bin/ruff`
  is a generic-linux ELF the NixOS stub loader rejects (exit 127), so a bare local `tox` dies in its
  `lint` env. Does **not** weaken SC#3: D-11 already assigns lint authority to CI. The sibling
  `tox -e py312` interpreter-download failure (RESEARCH.md Pitfall 1) is the same root cause on a
  different binary.
- `.planning/todos/pending/2026-08-11-windows-path-separator-breaks-contract-claims-gate.md` — the
  D-22 defect itself. **Not deferred**: D-22 resolves it in this phase, and the record is filed to
  `todos/completed/` at phase close (D-16 amendment).

Neither may be reframed as an "environmental false positive" — that reframing is precisely the error
Phase 45.2's SC#6 was raised to correct.

---

## Correction carried forward from research (affects plan review)

`46-CONTEXT.md`'s "Ordering interaction the planner must resolve" states that
`docs/source/changelog.rst` "currently makes *no* contract claim under the gate's scan." **Direct
measurement contradicts this** (RESEARCH.md Pitfall 3): the page already satisfies
`_page_makes_contract_claim()` today via its existing "Migrating from 0.5.x to 0.6.x" section, and
all 8 tests in `tests/test_docs_contract_claims_gate.py` pass on Linux right now.

The real Windows failure is a pure backslash-vs-forward-slash key mismatch in
`_discovered_claim_pages()`. Consequences for validation:

- D-22's `.as_posix()` repair is still exactly correct, and is what fixes Windows — **independent of
  D-09's content**.
- D-09's migration fragments do not "newly" satisfy the predicate; they add more matching text to a
  page that already passes.
- **Neither edit must land before the other** for this module to stay green on Linux/macOS/CI-ubuntu.
- **Review trap:** if a plan's rationale for sequencing D-22 and D-09 cites "the page currently makes
  no claim," that premise is false and the plan should be corrected before it is trusted.

---

## Validation Sign-Off

- [ ] All tasks have an `<automated>` verify, a Wave 0 dependency, or a justified Manual-Only entry
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references — none exist; all infrastructure is pre-existing
- [x] No watch-mode flags
- [x] Feedback latency < 1 s (narrow guards) / ~190 s (full suite)
- [ ] `nyquist_compliant: true` — **not expected to be set by this phase.** M1 (Windows), M3 (`ja`),
      M4 (REL-04 acceptance) and M5 (fence absence) are structurally manual. This will be PARTIAL by
      design, not by omission.

**Approval:** pending
