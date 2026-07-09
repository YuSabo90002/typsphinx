# Phase 6: Raise Runtime Pins + Python Floor - Context

**Gathered:** 2026-07-09
**Status:** Ready for planning

<domain>
## Phase Boundary

An **atomic** pin-raise that stands up the real target ecosystem so downstream phases
can diagnose against it. This phase re-pins `sphinx>=9.1,<10`, `docutils>=0.21,<0.23`
(targeting docutils 0.22.4), raises the Python floor to **3.12–3.13** (dropping 3.10/3.11)
across every declaration site, and regenerates `uv.lock` — all as one atomic change so no
intermediate state tries to install Sphinx 9.1 on Python 3.10/3.11.

Requirements covered: **FWD-01, PIN-01, PIN-02, PIN-03**.

**Explicitly NOT in this phase** (locked scope anchors):
- `typst` stays at `>=0.14.1,<0.15` — the typst 0.15 raise + `kai` fix is **Phase 7** (FWD-02).
- The four `@preview` package bumps + the 3-way version-sync update are **Phase 7** (PKG-*).
- `doctree.traverse()`→`findall()` and full-suite API compatibility are **Phase 8** (API-*).
- **Expected end state:** PDF / `docs-pdf` lanes stay RED after this phase (they only go green
  once Phase 7 lands the `kai` fix). That red is intended, not a regression to chase here.

</domain>

<decisions>
## Implementation Decisions

### main Red-Window / Branch Strategy (the area discussed)
- **D-01: Milestone integration branch.** All of Phase 6→9 is developed on a single v0.5.0
  integration branch (proposed name `release/v0.5.0`), NOT on `main` and NOT via
  per-phase-to-main merges. `main` must stay green throughout the whole milestone.
- **D-02: Merge to main only at milestone completion, via a GitHub PR.** When Phase 9 has
  every CI lane green (PDF/`docs-pdf` included), open a **GitHub Pull Request** from the
  integration branch and merge it **on the GitHub side** (PR review → merge) — not a local
  fast-forward. `main` never goes red at any point.
- **D-03: Accept the intentionally-red PDF/`docs-pdf` lanes as-is on the branch.** During the
  Phase 6→7 window the PDF lanes are expected red on the integration branch. **Do NOT** touch
  CI config to hide them (no temporary `continue-on-error`, no skip, no allow-failure). They
  return to green naturally when Phase 7 lands the `kai` fix. This keeps CI config diffs out of
  the picture and avoids a "restore the skip" follow-up.

### Claude's Discretion (planner/researcher decide with these defaults)
These three gray areas were surfaced but the user deferred them to the planner. Sensible
defaults to carry forward unless research contradicts:
- **lockfile regeneration method:** prefer a **targeted upgrade** (e.g.
  `uv lock --upgrade-package sphinx --upgrade-package docutils`) to keep the diff minimal
  per PIN-03's "minimal-diff" requirement, over a full `uv lock` re-resolve. Verify with
  `uv sync --locked`.
- **Phase-6 done-ness verification gate:** since the full pytest suite is Phase 8, prove the
  atomic raise landed with a lightweight gate — a `sphinx-build` smoke against a minimal
  Sphinx project (or the existing `tests/roots/test-basic`) that confirms **both** the `typst`
  and `typstpdf` builders **register** under Sphinx 9.1, plus a clean import of `typsphinx`.
  Full suite green is explicitly Phase 8's gate, not this phase's.
- **non-matrix job Python version:** the single-runner jobs (lint / type / cov / build /
  `docs.yml` / `release.yml` / `drift.yml`) currently pin `uv python install 3.10`. Move them
  to the **new floor 3.12** (consistency with `requires-python`), not 3.13.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope & requirements (authoritative)
- `.planning/ROADMAP.md` § "Phase 6: Raise Runtime Pins + Python Floor" — goal, 4 success
  criteria, and the "PDF lanes stay red" expected-state note.
- `.planning/REQUIREMENTS.md` — FWD-01, PIN-01, PIN-02, PIN-03 (exact pin strings and the
  full list of Python-floor declaration sites); "Locked scope decisions" (latest-only,
  Python floor ≥3.12); "Out of Scope" table.

### Codebase pin/version sites (declaration surface this phase edits)
- `pyproject.toml` — `requires-python` (currently `>=3.10`), the `Programming Language ::
  Python :: 3.1x` classifiers, `dependencies` (`sphinx>=5.0,<9`, `docutils>=0.18,<0.22`,
  `typst>=0.14.1,<0.15` — **leave typst**), black `target-version` (`py310..py313`), ruff
  `target-version` (`py310`), and the mypy/dev pins.
- `tox.ini` — `env_list = py310, py311, py312, py313, lint, type, cov, docs`.
- `.github/workflows/ci.yml` — matrix `python-version: ['3.10','3.11','3.12','3.13']` +
  the several `uv python install 3.10` single-runner sites.
- `.github/workflows/docs.yml`, `.github/workflows/release.yml`, `.github/workflows/drift.yml`
  — each has a `uv python install 3.10` / `python-version: "3.10"` site.
- `uv.lock` — regenerated (PIN-03); gated by `uv sync --locked`.

### Project codebase maps (context, read as needed)
- `.planning/codebase/STACK.md`, `.planning/codebase/CONVENTIONS.md`,
  `.planning/codebase/CONCERNS.md` — existing stack, conventions, known concerns.

No external ADRs/specs — requirements are fully captured in ROADMAP.md + REQUIREMENTS.md
plus the decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **v0.4.4 Phase 3 precedent:** the Python floor was previously modernized (3.10–3.13) as its
  own phase; the same set of declaration sites (pyproject `requires-python` + classifiers,
  tox `env_list`, workflow matrices, black/ruff/mypy `target-version`) is the edit surface
  here, now shifted 3.12–3.13.
- **`tests/roots/test-basic`** — existing minimal Sphinx test project; usable for the
  `sphinx-build` builder-registration smoke gate.

### Established Patterns
- **Atomic pin coordination:** pins live in multiple files that must move in lockstep;
  the lockfile (`uv.lock`) must be regenerated in the *same* change so no intermediate commit
  installs Sphinx 9.1 on Python 3.10/3.11 (success criterion #4).
- **The 3-way `@preview` version-sync hazard** (`writer.py` / `template_engine.py` /
  `templates/base.typ`, guarded by `tests/test_preview_version_sync.py`) is **out of scope
  here** — it belongs to Phase 7. Do not touch it in Phase 6.

### Integration Points
- CI/CD: every workflow (`ci.yml`, `docs.yml`, `release.yml`, `drift.yml`) references the
  Python version and will run on the integration branch — expect PDF/`docs-pdf` red until
  Phase 7 (per D-03, do not paper over it).

</code_context>

<specifics>
## Specific Ideas

- Integration branch name proposed: `release/v0.5.0` (planner may confirm/adjust).
- Merge mechanism is a **GitHub PR merged on GitHub's side** at milestone completion — the
  plan should not assume a local merge to `main`.

</specifics>

<deferred>
## Deferred Ideas

- **typst 0.15 raise + `@preview` bumps + `kai` fix** → Phase 7 (already roadmapped, noted
  here only to reinforce the Phase 6 boundary).
- **`traverse()`→`findall()` + full API/test compatibility** → Phase 8 (already roadmapped).
- No new out-of-phase capabilities were raised during discussion.

</deferred>

---

*Phase: 6-raise-runtime-pins-python-floor*
*Context gathered: 2026-07-09*
