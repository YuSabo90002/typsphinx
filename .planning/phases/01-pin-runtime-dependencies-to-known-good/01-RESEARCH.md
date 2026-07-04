# Phase 1: Pin Runtime Dependencies to Known-Good - Research

**Researched:** 2026-07-04
**Domain:** Python dependency pinning / lockfile regeneration / tox-uv config for a Sphinx→Typst PDF extension
**Confidence:** HIGH — the phase's two hardest open questions (which `typst` 0.14.x patch works, and whether the `sphinx`/`docutils` ceilings are load-bearing) were empirically reproduced **in this research session** against the real project source tree, not just inferred from docs.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Pin Expression Style**
- **D-01:** In `pyproject.toml`, add **upper bounds only** and keep existing floors: `typst>=0.14.1,<0.15`, `sphinx>=5.0,<9`, `docutils>=0.18,<0.22`. Do **not** raise floors and do **not** pin `typst==0.14.x` exactly in `pyproject.toml`.
- **D-02:** Strict reproducibility is carried by the regenerated `uv.lock`, not by exact `==` pins in `pyproject.toml`. `pyproject.toml` expresses the *compatible range*; `uv.lock` captures the exact resolved patch. (Lock currency is later enforced by DUR-01 in Phase 5, so a range here is safe.)

**PIN-06 — Load-Bearing Determination**
- **D-03:** Apply all three ceilings per PIN-02 (they are required regardless). **Additionally**, empirically verify whether `typst<0.15` **alone** turns the `docs-pdf` target green — i.e. determine whether the `sphinx<9` / `docutils<0.22` ceilings are load-bearing or precautionary — and record that finding in `PROJECT.md`'s Key Decisions table alongside the confirmed-good typst patch (and any rejected candidates).

**Commit / Plan Granularity**
- **D-04:** Land the **PIN change and the `black` reformat as separate commits** (separate landing units within Phase 1). This honors ROADMAP's directive that the pin fix land alone so a red/green result is unambiguous, and keeps `git blame` on the reformatted lines clean. The planner may split these into separate plans or separate atomic commits within one plan, but they must not be squashed into a single mixed commit.

**Ceiling Target Scope**
- **D-05:** Add upper bounds to the **runtime three only** (`typst`, `sphinx`, `docutils`). Do **not** add precautionary ceilings to `docs` deps (`furo`, `sphinx-autodoc-typehints`, `sphinx-intl`) or `dev` deps in this phase — dev tooling is Phase 4, and minimizing the diff keeps the red/green attribution clean. `docs.yml` green is confirmed in Phase 2.

**Carried-Forward / Pre-Locked (do not re-open)**
- Fallback if no single typst 0.14.x satisfies all four bundled `@preview` packages (codly 1.3.0, codly-languages 0.1.1, mitex 0.2.4, gentle-clues 1.2.0): pin one `@preview` package to an older release rather than moving the typst pin. (STATE.md, Blockers/Concerns.) **Research update: this session directly compiled all three tested 0.14.x candidates — 0.14.1, 0.14.5, 0.14.9 — against all four bundled packages simultaneously, and all three passed. The fallback path is now very low-probability, but the decision to keep it documented is unchanged.**
- `tox.ini` `[testenv]` and `[testenv:type]` dep lists must mirror the same ceilings as `pyproject.toml` so no tox env independently re-resolves an unbounded version (PIN-04).
- Dead `sphinx-testing` dependency (unused since 2019) is removed from `pyproject.toml` **and** `tox.ini` `[testenv] deps` **and** `uv.lock` (PIN-05).
- `black --check .` must pass on the **full tree** (reformats `docs/build_multilang.py`, `tests/test_config_other_options.py`, `tests/test_config_toctree_defaults.py`); `ruff` clean on the full tree (LINT-01/02).

### Claude's Discretion
- Exact `typst` patch within `0.14.x` (empirical — the planner/executor confirms in CI; not assumed at plan time). **Research narrowed this to a strong recommendation — see Standard Stack — but final CI confirmation across the 3-OS matrix is still an execution-time step, not asserted here as final.**
- Precise plan decomposition (how many plans, ordering of pin vs lint within the separate-commit constraint of D-04).
- Mechanical details of `uv.lock` regeneration command invocation. **Research verified the exact invocation this session — see Standard Stack / Code Examples.**

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope. (Forward-port to sphinx 9 / typst 0.15, configurable `@preview` versions, dev-tooling bumps, and durability guardrails are already tracked as v2 / later phases in REQUIREMENTS.md and ROADMAP.md.)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PIN-01 | `typst` pinned to `>=0.14.1,<0.15` in `pyproject.toml` | Confirmed via direct PyPI/tag data (0.14.1–0.14.9 exist, then 0.15.0) and via **empirical compile testing** (see Standard Stack) that `>=0.14.1,<0.15` compiles the bundled `@preview` set cleanly at three sampled patches. |
| PIN-02 | `sphinx<9`, `docutils<0.22` upper bounds in `pyproject.toml` | Confirmed via direct PyPI metadata reads (`requires_dist`/`yanked` fields) for the candidate Sphinx 8.x releases; see Standard Stack for the corrected effective-ceiling finding (8.3.0 is yanked). |
| PIN-03 | `uv.lock` regenerated, resolving cleanly across per-Python-version markers | **Empirically executed** `uv lock` against a scratch copy of this exact repo with the D-01/D-05 edits applied — resolved cleanly, 125 packages, no conflicts. Exact per-marker sphinx versions captured below (differs slightly from REQUIREMENTS.md's illustrative text — see State of the Art). |
| PIN-04 | `tox.ini` dependency lists mirror `pyproject.toml` ceilings; no independent unbounded re-resolution path | Confirmed via tox-uv official docs: **all `[testenv]`/`[testenv:type]` environments already use `runner = uv-venv-lock-runner`, under which the `deps=` key is completely ignored at runtime** — see Architecture Patterns for the important nuance this creates for how the planner should scope this edit. |
| PIN-05 | Dead `sphinx-testing` removed | Confirmed via repo-wide grep (zero usages) and via the scratch `uv lock` run, which cleanly dropped it from the lock with no side effects. |
| PIN-06 | Exact typst 0.14.x patch confirmed empirically green in CI; sphinx/docutils ceiling load-bearing question documented | **This is the core empirical deliverable of this research pass** — see Standard Stack for the full reproduction (both the `kai` failure and its fix, plus the direct answer to the ceiling question via a full `sphinx-build -b typstpdf` run against the real `docs/source` tree). |
| LINT-01 | `black --check .` exits 0 on full tree (3 named files reformatted) | **Empirically executed** `black --check .`/`black --diff .` (black 26.5.1) against the current tree — confirms exactly the 3 files named in CONTEXT.md need reformatting, 46 unchanged. Exact diffs captured in Code Examples. |
| LINT-02 | `ruff check .` passes clean on full tree | **Could not be executed in this research sandbox** (ruff is a native Rust binary; sandbox is NixOS without `nix-ld`, so downloaded generic-linux binaries cannot execute — this is an environment-specific limitation, not a finding about the codebase). See Environment Availability and Assumptions Log — must be confirmed by the executor on a normal Linux/macOS/Windows dev machine or in CI. |
</phase_requirements>

## Summary

This phase's risk was concentrated in one question: does pinning `typst<0.15` alone (plus the two required-but-possibly-precautionary `sphinx`/`docutils` ceilings) actually restore a green `docs-pdf` build? Rather than leaving this to CI iteration, this research session used the `uv` binary available in the sandbox to **directly reproduce both the failure and the fix** against the real project tree:

- `typst==0.15.0` (unbounded-resolution behavior) fails compiling the bundled `@preview` import block with the *exact* CI error: `TypstError: unknown variable: kai`.
- `typst==0.14.9` (the newest 0.14.x, and what `uv lock` naturally resolves to under `typst>=0.14.1,<0.15`) compiles the same import block cleanly, only emitting the expected deprecation warning (`` `kai` is deprecated, use ϗ or `\u{3d7}` instead ``).
- A **full `sphinx-build -b typstpdf` run against the actual `docs/source` tree**, with `typst` pinned to 0.14.9 but `sphinx` and `docutils` left at their *unbounded* latest-resolved versions (9.1.0 and 0.22.4 — the exact "known-bad" combination from the CI failure evidence), **succeeded**, producing a valid 101-page PDF. This directly answers D-03/PIN-06's load-bearing question: **the `sphinx<9`/`docutils<0.22` ceilings are precautionary, not load-bearing** — the `typst` pin alone is sufficient to turn `docs-pdf` green. (Confirmed on Linux only, single-shot; still apply all three ceilings per D-03, and still watch the full 3-OS CI matrix before declaring the phase done — see Common Pitfalls.)
- A scratch-repo `uv lock` run with the exact D-01/D-05 edits applied resolved cleanly (125 packages, zero conflicts) and is idempotent (`uv lock --check` reports "up to date" immediately after).
- `black --check .` (26.5.1) was run directly against the tree and reproduces exactly the 3 files CONTEXT.md names, with no additional files affected.

**Primary recommendation:** Apply the D-01 pins exactly as locked (`typst>=0.14.1,<0.15`, `sphinx>=5.0,<9`, `docutils>=0.18,<0.22`), regenerate `uv.lock` with a plain `uv lock`, remove `sphinx-testing`, edit `tox.ini`'s `deps=` lines to match (for documentation-truth — see the important nuance in Architecture Patterns), run `black .` to apply the 3-file reformat as its own commit, and treat `typst==0.14.9` as the primary expected/most-likely CI-confirmed patch — with 0.14.1 as an already-tested fallback if 0.14.9 somehow fails on a specific OS leg.

## Architectural Responsibility Map

This is a config/build-tooling maintenance phase, not a multi-tier application phase — the standard Browser/API/DB tiers don't apply. Instead, ownership is mapped across the project's actual dependency-resolution pipeline, so the planner doesn't misassign an edit to the wrong config surface.

| Capability | Primary Surface | Secondary Surface | Rationale |
|------------|-----------------|--------------------|-----------|
| Declare compatible version *ranges* | `pyproject.toml` `[project.dependencies]` | — | Source of truth for what's *allowed* (D-01/D-02) |
| Pin the exact resolved patch | `uv.lock` (regenerated via `uv lock`) | — | Source of truth for what's *installed*; carries strict reproducibility per D-02 |
| Propagate the lock to test/lint/type/docs environments | `tox.ini` (`runner = uv-venv-lock-runner` on every env) | — | All environments sync from `uv.lock` automatically; `tox.ini`'s own `deps=` lists are inert under this runner (see Architecture Patterns) |
| Invoke the pipeline in CI | `.github/workflows/ci.yml` / `docs.yml` | `release.yml` (separate, self-contained — Phase 2/PITFALLS.md Pitfall 7, not this phase) | `ci.yml`/`docs.yml` call `uv sync` then `uv run tox -e ...`; no edits needed here this phase |
| Enforce lint cleanliness | `black`/`ruff` via `tox -e lint` | `pyproject.toml [tool.black]`/`[tool.ruff]` config (untouched this phase) | LINT-01/02 — target-version settings stay `py39` this phase per CONTEXT.md |
| Record the empirical finding | `PROJECT.md` Key Decisions table | `STATE.md` Blockers/Concerns (close out once confirmed) | D-03 requires the finding to be durable, not just implied by a green CI run |

## Standard Stack

### Core (verified this session)

| Dependency | pyproject.toml constraint (D-01, locked) | Empirically-tested / recommended lock target | Verification method |
|------------|--------------------------------------------|-----------------------------------------------|----------------------|
| `typst` (typst-py) | `>=0.14.1,<0.15` | **`0.14.9`** (released 2026-05-14) — the newest 0.14.x; also what a plain `uv lock` naturally resolves to under this range | `[VERIFIED: local reproduction — uv + typst-py, this session]` Installed and ran `typst.compile()` against a `.typ` file replicating the exact bundled `@preview` import block (`codly:1.3.0`, `codly-languages:0.1.1`, `mitex:0.2.4`, `gentle-clues:1.2.0`) at three 0.14.x patches (0.14.1, 0.14.5, 0.14.9) — **all three compiled successfully**, with only the expected deprecation warning (`` `kai` is deprecated, use ϗ or `\u{3d7}` instead ``), never a hard error. Then ran the **full `sphinx-build -b typstpdf docs/source <out>`** against the real repo with typst pinned to 0.14.9 — produced a valid 101-page PDF. Reinstalling `typst==0.15.0` and re-running the identical full build reproduced the exact CI error: `TypstError: unknown variable: kai` at PDF compile time. |
| `sphinx` | `>=5.0,<9` | Effective resolution (this session's scratch `uv lock`): **`8.1.3`** for Python 3.10 through 3.14+, **`7.4.7`** for Python 3.9 | `[VERIFIED: local reproduction — uv lock, this session]` Ran `uv lock` in a scratch copy of this repo with the D-01 pins + PIN-05 removal applied. Resolved cleanly (125 packages, no conflicts). Per-marker `sphinx` entries: `python_full_version <= '3.9'` and `> '3.9' and < '3.10'` → `7.4.7`; `python_full_version == '3.10.*'`, `== '3.11.*'`, `>= '3.12' and < '3.15'`, `>= '3.15'` → `8.1.3`. **Important correction to REQUIREMENTS.md's illustrative acceptance text** ("sphinx ≤8.1.3 on 3.10, up to 8.3.0 on 3.11–3.13"): Sphinx **8.3.0 is YANKED on PyPI** (`yanked: true`, reason `"Bad release"` — confirmed via direct PyPI JSON API read, cross-referenced with `astral-sh/uv` issue #12737 which independently documents uv's resolver encountering this same yank). uv does not select yanked releases by default, so the actual ceiling landed on is `8.1.3`, not `8.2.3`/`8.3.0`. This doesn't change PIN-03's actual goal (clean, conflict-free per-marker resolution) — it changes only the specific version numbers the acceptance text illustrates. Flag this for the executor so nobody is surprised the lock doesn't contain `8.2.x`/`8.3.0`. |
| `docutils` | `>=0.18,<0.22` | `0.21.2` (released 2024-04-23) uniformly across all markers | `[VERIFIED: local reproduction — uv lock, this session]` Same scratch `uv lock` run — resolved to a single `0.21.2` entry (no per-marker split needed; Sphinx's own `docutils<0.22,>=0.20` constraint, read directly from Sphinx 8.1.3/8.2.3/8.3.0 PyPI metadata, already narrows this before typsphinx's own `<0.22` ceiling has to do any work). |
| `sphinx-testing` | *(removed — PIN-05)* | n/a | `[VERIFIED: local reproduction, this session]` `grep -rn "sphinx_testing\|sphinx-testing" --include="*.py" .` → zero matches. Scratch `uv lock` run confirms clean removal with no dependents. |

### uv.lock regeneration mechanics (verified this session)

```bash
# 1. Edit pyproject.toml per D-01 (add ceilings, keep floors) and remove
#    the sphinx-testing line per PIN-05.
# 2. Regenerate the lock:
uv lock
# 3. Confirm it's not just "changed" but internally consistent / not stale:
uv lock --check
```
`[VERIFIED: local reproduction, this session]` — `uv lock` on a scratch copy of this repo with the exact edits applied output:
```
Resolved 125 packages in 785ms
Updated docutils v0.21.2, v0.22.4 -> v0.21.2
Removed roman-numerals v4.1.0
Removed six v1.17.0
Updated sphinx v7.4.7, v8.1.3, v9.0.4, v9.1.0 -> v7.4.7, v8.1.3
Updated sphinx-autodoc-typehints v2.3.0, v3.0.1, v3.6.1, v3.12.1 -> v2.3.0, v3.0.1
Removed sphinx-testing v1.0.1
Updated typst v0.15.0 -> v0.14.9
```
A follow-up `uv lock --check` run (no changes) resolved instantly and reported no drift — the lock is stable/idempotent. No manual conflict resolution, `--resolution=lowest` flag, or per-marker override was needed; a plain `uv lock` closes PIN-03 completely.

`[CITED: docs.astral.sh/uv/concepts/projects/sync]` — `uv lock --check` exits non-zero without writing if the lock is stale relative to `pyproject.toml` (a fast pre-commit/CI gate); `uv sync --locked` errors instead of silently re-resolving; plain `uv sync` (what `ci.yml`/`docs.yml` currently run) silently re-resolves and rewrites a stale lock — this silent-rewrite behavior is exactly the mechanism Pitfall 1 (PITFALLS.md) warns about, and is why PIN-03 requires the regenerated lock to be committed in the same change as the `pyproject.toml` edit, not regenerated later by CI.

**Installation / regeneration commands for the executor:**
```bash
uv lock
git diff pyproject.toml uv.lock   # review both together, never one without the other
uv run tox -e docs-pdf            # empirical confirmation of PIN-06 (see Validation Architecture)
```

### Alternatives Considered

| Instead of | Could use | Tradeoff |
|------------|-----------|----------|
| `typst==0.14.9` as the primary CI-confirmed target | `typst==0.14.1` (the pre-existing floor) | Already empirically confirmed to work too (see above) — use as the documented fallback if `0.14.9` somehow fails a specific OS leg in the real CI matrix (rather than reopening the whole empirical search). |
| Plain `sphinx>=5.0,<9` (wide floor) | `sphinx>=7.0,<9` or `>=8.0,<9` (tighter floor) | Not needed this phase — D-01 explicitly locks "keep existing floor." Noting only as a documented non-choice, per STACK.md. |

## Package Legitimacy Audit

This phase does not introduce any *new* runtime dependency — it re-pins three pre-existing, long-established packages (`typst`, `sphinx`, `docutils`) and *removes* one (`sphinx-testing`). Ran the legitimacy gate anyway for completeness:

| Package | Registry | Signal notes | Verdict (raw) | Disposition |
|---------|----------|---------------|----------------|-------------|
| `typst` | PyPI | `repoUrl: github.com/messense/typst-py`; heuristic flagged `too-new`/`unknown-downloads` because it keys off the *latest release date* (2026-06-16, i.e. 0.15.0) rather than the package's founding date. `typst-py` has shipped continuously since 2023 under a known, verified-signature-tagging maintainer (`messense`). | SUS | **Approved — heuristic false positive.** This is the exact package already declared in `pyproject.toml` today; this phase only narrows its version range. |
| `sphinx` | PyPI | `repoUrl: sphinx-doc.org`; flagged `unknown-downloads` only (the download-count signal wasn't available to the checker). Sphinx is the de facto standard Python documentation generator, in continuous use since 2008. | SUS | **Approved — heuristic false positive** (download-count API unavailable to the checker, not a real risk signal). |
| `docutils` | PyPI | `repoUrl: docutils.sourceforge.io`; same `unknown-downloads` flag. Docutils is the foundational reST processing library Sphinx itself depends on; in continuous use since the early 2000s. | SUS | **Approved — heuristic false positive.** |
| `sphinx-testing` | PyPI | Not checked (this phase *removes* it, not installs it). | n/a | **Removed per PIN-05** — dormant since its last release (1.0.1, 2019), zero usages in the test suite (confirmed by grep this session). |

**Packages removed due to `[SLOP]` verdict:** none — no `SLOP` verdicts this run.
**Packages flagged as suspicious `[SUS]`:** `typst`, `sphinx`, `docutils` — all three dispositioned as approved heuristic false positives (see table); **no `checkpoint:human-verify` gate is warranted** because these are pre-existing dependencies already relied upon by the project for years, not new installs, and the "suspicious" signal in every case is a checker limitation (recency-of-latest-release / unavailable download-count API), not a supply-chain risk indicator. The planner may still choose to add a lightweight human-verify note if project policy prefers extra caution on any pin change, but it is not required by this research's findings.

## Architecture Patterns

### System Diagram — the dependency-resolution → CI pipeline this phase edits

```
pyproject.toml                          tox.ini                        CI workflows
[project.dependencies]                  [testenv] runner=              (ci.yml / docs.yml)
  typst>=0.14.1,<0.15  ─┐                uv-venv-lock-runner  ─┐          │
  sphinx>=5.0,<9        │                (deps= INERT under      │          │  uv sync --extra dev
  docutils>=0.18,<0.22  │                this runner — see        │          ▼
  (sphinx-testing REMOVED)│               note below)              │        uv run tox -e <env>
        │                │                                        │          │
        ▼                │                                        ▼          ▼
   `uv lock`  ────────────┴──────────►  uv.lock  ◄── every tox env syncs from this
        │                                  (per-Python-version-marker
        │                                   resolved exact versions)
        ▼
  committed uv.lock diff (PIN-03)
        │
        ▼
  tox -e docs-pdf  ──►  sphinx-build -b typstpdf docs/source _build/pdf
        │                       │
        │                       ▼
        │                 typsphinx.builder / writer / template_engine
        │                 (emits `#import "@preview/...` block, UNCHANGED
        │                  this phase — hardcoded versions stay as-is)
        ▼
  typst.compile() (via typst-py, now pinned <0.15)
        │
        ▼
  PDF produced ── if `kai` symbol only WARNS (0.14.x) → success
                  if `kai` symbol ERRORS (0.15.x)      → TypstCompilationError
```

### Pattern: Lockfile as the single reproducibility source of truth (D-02)
**What:** `pyproject.toml` expresses a *range*; `uv.lock` pins the *exact* patch actually installed. Never rely on the range alone for reproducibility.
**When to use:** Always, per this project's existing convention (`tox.ini` already uses `uv-venv-lock-runner` everywhere) — this phase doesn't introduce the pattern, it just needs to keep exercising it correctly (regenerate + commit the lock together with the `pyproject.toml` edit).
**Example:** see the "uv.lock regeneration mechanics" block above.

### Pattern (important nuance): `tox.ini`'s `deps=` lists are inert under `uv-venv-lock-runner`
**What:** `[testenv]`, `[testenv:lint]`, `[testenv:type]` in this repo's `tox.ini` all set `runner = uv-venv-lock-runner` (and `[testenv:cov]`/`[testenv:docs*]` inherit it from `[testenv]` since none override `runner`). `[CITED: github.com/tox-dev/tox-uv README]`: *"Note that when using `uv-venv-lock-runner`, all dependencies will come from the lock file, controlled by `extras`. Therefore, options like `deps` are ignored."*
**Why this matters for PIN-04:** the `deps=` blocks in `[testenv]`/`[testenv:type]` currently listing `sphinx>=5.0`, `docutils>=0.18` unbounded are **not actually a live, independent re-resolution path today** — they have no runtime effect under this runner. Editing them to mirror the new ceilings is still required to satisfy PIN-04's literal acceptance text (and to stop the file from *documenting* an unbounded intent that contradicts `pyproject.toml`), but the planner/executor should not expect this edit, by itself, to change any installed version — that already happens entirely through `uv.lock` (PIN-03). Frame the PIN-04 task as "fix stale/misleading documentation of intent in `tox.ini`," not "close a functional resolution hole."
**When to use:** Apply this understanding when writing the PIN-04 task/verification step — the check should be "grep `tox.ini` for the old unbounded strings, replace with the matching ceilinged strings," not "run `tox -e type` and see a different sphinx version get installed" (it won't change, because `uv.lock` is what governs the install either way).

### Anti-Patterns to Avoid
- **Guessing the typst patch instead of testing it:** already covered in depth by PITFALLS.md Pitfall 3 — this research session's empirical results (three 0.14.x patches tested, all pass) substantially de-risk this but do not replace the full-matrix CI confirmation.
- **Editing `uv.lock` by hand:** it's machine-managed; always regenerate via `uv lock`, never hand-edit version strings in it.
- **Treating `tox.ini`'s `deps=` edit as functionally load-bearing:** see the nuance above — don't let this task balloon into "investigate why sphinx didn't change" during execution; it won't, by design.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| Cross-Python-version dependency resolution | A manual per-Python-version pin matrix in `pyproject.toml` (e.g. environment markers per Sphinx version) | `uv lock`'s universal resolver — it already produces the correct per-marker split automatically (verified this session: 7.4.7 for py3.9, 8.1.3 for 3.10+) | `uv`'s resolver already handles Sphinx's own mid-series `requires-python` floor change (8.2.0 raised its floor to `>=3.11`) transparently via PEP 508 markers; hand-rolling this is strictly more error-prone and unnecessary. |
| Confirming the typst/`@preview` compatibility | A custom CI matrix job that iterates every 0.14.x patch against every `@preview` package pairwise | The single `tox -e docs-pdf` target already exercises the exact production import block (`templates/base.typ`) with all four packages at once — this is the fastest and most representative empirical check (used directly in this research session). | The full-matrix approach is what Pitfall 3's "Performance Traps" section (PITFALLS.md) warns against — it burns CI minutes reconfirming the same known error. |
| Verifying `tox.ini` dependency mirroring "worked" | Re-running the full test suite and diffing installed package versions | A plain `grep -n "sphinx>=5.0\|docutils>=0.18" tox.ini` (should return zero unbounded matches after the edit) | Given the `deps=` inertness finding above, functional re-verification via test runs proves nothing about this specific edit; a static grep is the correct and sufficient check. |

**Key insight:** this phase's entire risk profile is empirical (does the pin work?), not architectural (there's no new code, no new design pattern to invent) — so "don't hand-roll" here mostly means "don't hand-roll a bespoke verification process when `uv lock` + `tox -e docs-pdf` + `grep` already do the job directly."

## Common Pitfalls

Full pitfalls catalog for this milestone already exists at `.planning/research/PITFALLS.md` (researched 2026-07-04, same day) — **do not duplicate it here; read it directly.** It covers, in depth: under-pinning (Pitfall 1), the 3-way `@preview` desync hazard (Pitfall 2 — explicitly NOT this phase's job per CONTEXT.md scope, but touch nothing there), guessing the typst pin (Pitfall 3 — this research session directly executed its recommended empirical method), cross-platform pin failures (Pitfall 4), Python-floor bump hazards (Pitfall 5 — Phase 3, not this phase), green-but-frozen durability gaps (Pitfall 6 — Phase 5), and release-workflow parity (Pitfall 7 — final-phase concern).

**New findings from this session that refine those pitfalls:**

### Pitfall (refinement of PITFALLS.md #4): Cross-platform confirmation is still open — this session tested Linux only
**What goes wrong:** It would be easy to read this research's strong empirical results (typst 0.14.1/0.14.5/0.14.9 all compile; full docs-pdf succeeds with typst pinned and sphinx/docutils unbounded) as "the pin is proven" and skip watching the full 3-OS CI matrix.
**Why it happens:** The reproduction in this session ran on a Linux sandbox only (no macOS/Windows runners available here).
**How to avoid:** Treat this session's findings as "very high confidence the pin is correct" (it reproduces the exact failure and exact fix on real project source), but still require the executor to watch at least one full green run of the 3-OS × Python-version matrix before considering PIN-06 fully closed, per the already-locked D-03 requirement and PITFALLS.md Pitfall 4. Wheel availability for `typst==0.14.9` was separately confirmed cross-platform (see Standard Stack — manylinux2014 multi-arch, macOS x86_64+arm64, Windows win_amd64 all published), which further reduces — but does not eliminate — the risk.
**Warning signs:** Declaring PIN-06 "confirmed" from this research document alone without a real CI run.

### Pitfall (new): REQUIREMENTS.md's illustrative Sphinx version text is now stale
**What goes wrong:** REQUIREMENTS.md's PIN-03 acceptance text says "resolving cleanly across the per-Python-version markers (sphinx ≤8.1.3 on 3.10, up to 8.3.0 on 3.11–3.13)". Sphinx `8.3.0` is **yanked** (confirmed via direct PyPI metadata + a corroborating `astral-sh/uv` issue), so a real `uv lock` run cannot and will not select it — the executor should not treat "the lock contains 8.1.3 for 3.11+ instead of 8.2.3/8.3.0" as a bug or as PIN-03 failing.
**Why it happens:** REQUIREMENTS.md's parenthetical was written from a training-data/assumed version snapshot, not a live registry read, and the yank likely postdates that assumption.
**How to avoid:** Treat PIN-03's actual acceptance bar as "resolves cleanly, no conflicts, every marker lands on a version satisfying `sphinx>=5.0,<9`" — not "matches the exact version numbers in the parenthetical illustration." This session's scratch `uv lock` run is the ground truth: `7.4.7` (Python ≤3.9) / `8.1.3` (Python 3.10+).
**Warning signs:** Executor spends time trying to force a `8.2.x`/`8.3.0` resolution that doesn't naturally occur.

## Code Examples

Verified patterns from this research session's direct reproduction (not official docs — tagged accordingly):

### Empirical typst/`@preview` compatibility check (the PIN-06 core method)
```python
# Source: [VERIFIED: local reproduction, this session] — minimal repro of templates/base.typ's import block
# kai_test.typ:
#   #import "@preview/codly:1.3.0": *
#   #import "@preview/codly-languages:0.1.1": *
#   #import "@preview/mitex:0.2.4": *
#   #import "@preview/gentle-clues:1.2.0": *
#   #show: codly-init.with()
#   #codly(languages: codly-languages)
#   = Test document
#   #mi("x^2 + y^2 = z^2")
#   #info[This is a test admonition.]
#   ```python
#   print("hello")
#   ```

import typst
result = typst.compile_with_warnings("kai_test.typ", output="kai_test.pdf")
# under typst==0.14.1 / 0.14.5 / 0.14.9:
#   (None, [TypstWarning('`kai` is deprecated, use ϗ or `\u{3d7}` instead')])
#   -> compiles successfully, PDF produced
# under typst==0.15.0:
#   raises typst.TypstError: unknown variable: kai
#   -> exact match for the CI failure evidence
```

### Full end-to-end reproduction (equivalent of `tox -e docs-pdf`)
```bash
# Source: [VERIFIED: local reproduction, this session]
# with typst pinned to 0.14.9 and sphinx/docutils left UNBOUNDED (resolved to 9.1.0 / 0.22.4 —
# the exact "known-bad" combination from PROJECT.md's failure evidence):
python -m sphinx -b typstpdf docs/source /tmp/pdf_out
# -> "build succeeded, 4 warnings." + a valid 101-page PDF at /tmp/pdf_out/index.pdf

# Re-running the IDENTICAL command with only typst swapped to 0.15.0:
python -m sphinx -b typstpdf docs/source /tmp/pdf_out_015
# -> ERROR: Failed to compile .../index.typ: Typst compilation failed: TypstError: unknown variable: kai
```
This directly answers D-03: the `sphinx`/`docutils` ceilings are **precautionary**, not load-bearing, for the `kai` break specifically — `typst<0.15` alone is sufficient.

### `black --diff` output for the 3 flagged files (LINT-01)
```diff
# Source: [VERIFIED: local reproduction — black 26.5.1, this session]
--- docs/build_multilang.py
+++ docs/build_multilang.py
@@ -2,10 +2,11 @@
 """Multi-language documentation build script for typsphinx.
...
 """
+
 import os
 import shutil
 import subprocess
 from pathlib import Path
```
(Black inserts a blank line between the module docstring and the first import.)

```diff
# tests/test_config_other_options.py and tests/test_config_toctree_defaults.py:
# black collapses `foo.write_text(\n    """..."""\n)` into `foo.write_text("""...""")`
# — this is black's stable "hug parens with braces/brackets" style behavior in
# current black versions, not related to Python target-version.
-    conf_py.write_text(
-        """
+    conf_py.write_text("""
 extensions = ['typsphinx']
 typst_package = "@preview/diagraph:0.2.5"
-"""
-    )
+""")
```
`black --check .` output confirms scope precisely: `3 files would be reformatted, 46 files would be left unchanged` — matches CONTEXT.md's named list exactly, no surprises.

## State of the Art

| Old Approach (assumed at context-gathering time) | Current Approach (confirmed this session) | When Changed | Impact |
|---------------------------------------------------|----------------------------------------------|----------------|--------|
| Sphinx 3.11+ CI legs would resolve up to `8.3.0` per REQUIREMENTS.md's illustrative text | Effective resolution lands on `8.1.3` for Python 3.10+ (8.3.0 is yanked, never selectable) | `8.3.0` yank predates this research pass (exact yank date not directly surfaced, but corroborated via `astral-sh/uv#12737`, an April 2025-dated issue) | PIN-03's acceptance check should verify "clean resolution, ceilings respected" — not the specific version numbers in REQUIREMENTS.md's parenthetical |
| PIN-06 treated as "must be confirmed only in CI at execution time" | Substantially pre-confirmed via direct local reproduction this session (Linux only) | This research session, 2026-07-04 | Reduces expected CI iteration count for PIN-06 from "several guess-and-check cycles" (PITFALLS.md Pitfall 3's original risk framing) to "one confirmation run," since the underlying compile behavior is already known |

**Deprecated/outdated:** none introduced by this phase — no `@preview` package versions change (out of scope, D-05/CONTEXT.md).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|----------------|
| A1 | `typst-py` PyPI version numbers track 1:1 with the underlying Rust `typst` compiler version it bundles | Standard Stack / PITFALLS.md (carried over) | LOW — this session's direct behavioral tests (0.14.x warns, 0.15.x errors on the same symbol) are consistent with this claim, but no single official doc states the correspondence explicitly; if wrong in some edge patch, the empirical compile test (already demonstrated, cheap to re-run) is the actual safety net, not this assumption. |
| A2 | `ruff check .` is clean on the current tree (or has only pre-existing findings unrelated to this phase) | Phase Requirements (LINT-02) | MEDIUM — **not verified this session** (native binary couldn't execute in this sandbox). If ruff surfaces findings, the executor needs an additional fix pass before LINT-02 can close; plan should include a `checkpoint` or explicit "run ruff, fix findings" task rather than assuming clean. |
| A3 | Windows/macOS behave identically to the Linux reproduction in this session for the `typst<0.15` fix | Common Pitfalls (cross-platform refinement) | MEDIUM — wheel *availability* is confirmed cross-platform, but actual compile *behavior* (e.g. any platform-specific `@preview` package quirk) was only tested on Linux this session. Mitigated by requiring the full 3-OS CI matrix per D-03/Pitfall 4 before declaring PIN-06 fully closed. |
| A4 | No `[tool.uv]` config section exists to override uv's default dependency-group sync behavior | Architecture Patterns | LOW — directly confirmed by reading the full `pyproject.toml` this session (no `[tool.uv]` section present); low risk of being wrong since it was a direct file read, not an inference. |

**If this table is empty:** N/A — see above; two items (A2, A3) carry real execution-time risk and should not be treated as settled.

## Open Questions

1. **Does `ruff check .` pass clean on the current tree?**
   - What we know: STACK.md rated ruff's own breaking-change cadence as low risk (MEDIUM confidence), and no ruff findings were reported anywhere in the CI failure evidence (`PROJECT.md`) — only `black` reformatting was named.
   - What's unclear: This session couldn't execute the native `ruff` binary in the sandbox to confirm directly.
   - Recommendation: The executor should run `ruff check .` early in Phase 1 execution (via `tox -e lint` or directly) as a fast, cheap first step, and treat any findings as in-scope fix-up work for LINT-02, not a surprise requiring replanning.

2. **Will the full 3-OS × Python-version CI matrix stay green with these exact pins?**
   - What we know: The core compile logic is confirmed correct on Linux, for the exact production import block, via direct reproduction.
   - What's unclear: macOS/Windows-specific behavior (file-locking, path handling per PITFALLS.md Pitfall 4) is untested this session.
   - Recommendation: Treat the first full CI run after landing the pin as the actual PIN-06/D-03 confirmation gate — this research substantially de-risks it but the ROADMAP/CONTEXT.md decision to empirically confirm in CI still stands and should not be skipped.

## Environment Availability

| Dependency | Required By | Available (this research sandbox) | Version | Fallback |
|------------|--------------|--------------------------------------|---------|----------|
| `uv` | All PIN-01..06 work, lock regeneration | Yes | 0.11.25 | — |
| Python (system/nix-native) | Running `uv lock`, `black`, `sphinx-build` directly | Yes | 3.13.13 (nix-native), plus a separately-downloaded 3.12 via `uv python install` | — |
| `black` | LINT-01 | Yes (pure-Python, installs and runs fine) | 26.5.1 (latest stable) | — |
| `ruff` | LINT-02 | **No** — native Rust binary, this sandbox is NixOS without `nix-ld`; downloaded generic-linux binaries fail with `Could not start dynamically linked executable` | — | Executor must run `ruff check .` on a normal (non-NixOS-restricted) machine or in CI — this is a sandbox limitation, not a project/codebase issue. |
| `typst` (typst-py) | PIN-06 empirical confirmation | Yes — the compiled `.so` extension loads fine via Python's `dlopen` (unlike standalone executables, which fail under the same NixOS restriction) | Tested: 0.14.1, 0.14.5, 0.14.9, 0.15.0 | — |
| `uv`-managed standalone Python interpreters (e.g. via `uv venv --python 3.12`) | Would be needed to fully replicate `tox`'s per-env venv creation | **No** — `uv`'s downloaded standalone CPython builds are generic dynamically-linked binaries and fail identically to `ruff` under this sandbox's NixOS restriction | — | Workaround used this session: created venvs against the *system* nix-native Python instead, which resolved this for `uv lock`/`black`/`typst`/`sphinx-build` testing. The executor's real CI runners (GitHub Actions ubuntu/macos/windows) do not have this restriction and will run `tox`'s own venvs normally. |
| `mypy` | Not this phase's job (TEST-04 says "must not regress" — Phase 2 concern) | Installed successfully but not exercised this session | 1.20.2 | — |

**Missing dependencies with no fallback:** none blocking — `ruff` and full `tox`-driven venv creation are sandbox-only limitations with clear fallbacks (real CI / real dev machine).
**Missing dependencies with fallback:** `ruff` (fallback: run in CI/normal machine), `tox`'s own venv creation (fallback: this session's direct-invocation equivalent already produced usable, representative results).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (via `[tool.pytest.ini_options]` in `pyproject.toml`); this phase's own acceptance criteria (PIN-01..06, LINT-01/02) are **not** pytest-based — they're static config assertions plus one CLI-invoked empirical PDF compile, not new test files. |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (existing, untouched this phase) |
| Quick run command | `black --check . && ruff check .` (LINT-01/02, seconds) |
| Full/empirical run command | `uv run tox -e docs-pdf` (PIN-06 empirical confirmation, ~30s–2min depending on `@preview` package cache state) |

### Phase Requirements → Verification Map
| Req ID | Behavior | Verification Type | Command | Verified this session? |
|--------|----------|---------------------|---------|--------------------------|
| PIN-01 | `typst` ceiling present | static grep | `grep -n 'typst>=0.14.1,<0.15' pyproject.toml` | Constraint text confirmed correct against locked D-01; grep itself is trivial and not separately run |
| PIN-02 | `sphinx`/`docutils` ceilings present | static grep | `grep -nE 'sphinx>=5.0,<9|docutils>=0.18,<0.22' pyproject.toml` | Same as above |
| PIN-03 | `uv.lock` regenerated, resolves cleanly | CLI resolution | `uv lock && uv lock --check` | **Yes** — full scratch-repo reproduction this session, 125 packages, zero conflicts, idempotent |
| PIN-04 | `tox.ini` deps mirror ceilings | static grep | `grep -nE 'sphinx>=5\.0[^,]|docutils>=0\.18[^,]' tox.ini` (should return zero matches after edit — i.e. no more *unbounded* declarations) | Mechanism understood and confirmed (deps= is inert under uv-venv-lock-runner) — the grep itself is trivial |
| PIN-05 | `sphinx-testing` removed everywhere | static grep + lock diff | `grep -rn sphinx-testing pyproject.toml tox.ini uv.lock` (expect zero matches) | **Yes** — confirmed absent from all three in the scratch reproduction |
| PIN-06 | Empirical typst-patch confirmation + ceiling load-bearing finding documented | empirical build + doc update | `uv run tox -e docs-pdf` (or CI matrix); finding written into `PROJECT.md` Key Decisions | **Yes, substantially** — Linux-only direct reproduction this session; full 3-OS CI confirmation still required per D-03 |
| LINT-01 | `black --check .` exits 0 | CLI | `black --check .` (via `tox -e lint` or directly) | **Yes** — confirmed exactly 3 files need reformatting, 46 unchanged |
| LINT-02 | `ruff check .` exits 0 | CLI | `ruff check .` (via `tox -e lint` or directly) | **No** — sandbox limitation (native binary); executor must run this early in execution |

### Sampling Rate
- **Per task commit:** `black --check .` (or `black --diff .` before applying) — instant, run before every commit touching Python files.
- **Per plan/wave merge:** `uv lock --check` (confirms no drift was introduced) + `ruff check .`.
- **Phase gate:** `uv run tox -e docs-pdf` green locally (or in one CI run) before considering PIN-06 closed; full 3-OS CI matrix green is the final phase-exit confirmation for D-03.

### Wave 0 Gaps
- [ ] No new pytest test files are needed for this phase — its acceptance criteria are static-config assertions (grep-verifiable) plus one CLI-invoked empirical build check, not unit/integration tests. The existing ~400-test pytest suite (including the 7 PDF-integration tests referenced by TEST-02) is Phase 2's concern, not a Wave 0 gap here.
- [ ] `ruff check .` has not been executed against the current tree this session (sandbox limitation) — the executor should run it as an early, cheap step rather than assume clean.

## Security Domain

`security_enforcement` is enabled (`security_asvs_level: 1`) per `.planning/config.json`, so this section is included for completeness, but this phase's actual attack surface is minimal — it is a dependency-pinning and lint-formatting change with no new input handling, authentication, session, or cryptography code.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|----------------|---------|--------------------|
| V2 Authentication | No | N/A — no auth code touched |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | No | N/A — no new parsing/input-handling code; the existing reST→Typst translator is unchanged this phase |
| V6 Cryptography | No | N/A |
| V14 Configuration (closest fit) | Yes | Explicit, verified version ceilings in `pyproject.toml` + a committed, regenerated lockfile (`uv.lock`) — the actual "standard control" for this phase's real risk category, which is supply-chain/dependency integrity, not a classic ASVS input-handling category. |

### Known Threat Patterns for this phase's actual risk surface

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|------------------------|
| Dependency confusion / unbounded version drift silently reintroducing a known-bad combination | Tampering (of the build environment, not the app) | Explicit upper bounds (PIN-01/02) + committed, regenerated `uv.lock` (PIN-03) + (later, Phase 5/DUR-01) `uv sync --locked` in CI so drift fails loudly instead of silently re-resolving |
| Supply-chain package-name confusion (typosquat/slopsquat) | Spoofing | Package Legitimacy Audit above — all three re-pinned packages verified against their known, long-established repo URLs; no new package names introduced this phase |

## Sources

### Primary (HIGH confidence — direct execution / direct repository reads, this session)
- Direct `uv lock` execution against a scratch copy of this repository with the D-01/D-05 edits applied — full resolution output captured above.
- Direct `typst.compile()`/`typst.compile_with_warnings()` execution (typst-py 0.14.1, 0.14.5, 0.14.9, 0.15.0) against a minimal reproduction of `typsphinx/templates/base.typ`'s import block.
- Direct `python -m sphinx -b typstpdf docs/source <out>` execution against the real `docs/source` tree, both with typst pinned (success) and unbounded/0.15.0 (exact CI error reproduced).
- Direct `black --check .` / `black --diff .` (26.5.1) execution against the current tree.
- Direct PyPI JSON API reads (`pypi.org/pypi/Sphinx/8.1.3/json`, `.../8.2.3/json`, `.../8.3.0/json`) for `requires_python`, `requires_dist`, `yanked` fields.
- Direct repo reads: `pyproject.toml`, `tox.ini`, `uv.lock`, `.github/workflows/ci.yml`, `.github/workflows/docs.yml`, `typsphinx/templates/base.typ`, `docs/build_multilang.py`, `tests/test_config_other_options.py`, `tests/test_config_toctree_defaults.py`.
- Existing project research: `.planning/research/PITFALLS.md`, `.planning/research/STACK.md`, `.planning/codebase/CONCERNS.md` (all researched same day, 2026-07-04, HIGH confidence, reused not duplicated).

### Secondary (MEDIUM confidence)
- `[CITED: github.com/tox-dev/tox-uv]` — `uv-venv-lock-runner` behavior (deps ignored, extras/dependency_groups control sync) — WebFetch of the project README.
- `[CITED: docs.astral.sh/uv/concepts/projects/sync]` — `uv lock --check` / `uv sync --locked` semantics.
- `[CITED: github.com/mitex-rs/mitex CHANGELOG.md]` — the exact `0.2.6` changelog entry fixing the `kai` deprecation warning.
- WebSearch-sourced typst-py 0.14.x release dates (cross-checked against the `messense/typst-py` GitHub tags page and PyPI search results — two independent sources converge on the same dates).

### Tertiary (LOW confidence)
- `astral-sh/uv` issue #12737 (WebSearch summary only, not independently re-read in full) — used only as corroboration for the Sphinx 8.3.0 yank, which was already confirmed at HIGH confidence via direct PyPI JSON reads.

## Metadata

**Confidence breakdown:**
- Standard stack (exact pins): HIGH — empirically reproduced in this session, not just cited.
- PIN-06 / D-03 (typst patch choice + ceiling load-bearing question): HIGH for the underlying compile behavior (direct reproduction); MEDIUM for full cross-platform confirmation (Linux-only tested here — 3-OS CI run still required).
- LINT-01: HIGH — directly executed.
- LINT-02: LOW (not executed this session — sandbox limitation) — executor must confirm directly.
- Architecture/tox-uv mechanics: HIGH — official docs cited and cross-referenced against the actual `tox.ini` content.

**Research date:** 2026-07-04
**Valid until:** ~7 days for the exact version numbers (fast-moving PyPI release cadence for `typst`; a new 0.14.x patch or a 0.15.x point release could appear) — re-verify the exact resolved versions if execution happens more than a week after this research date. The underlying architecture/mechanics findings (tox-uv, uv lock semantics) are stable for ~90 days.

---
*Phase: 1-Pin Runtime Dependencies to Known-Good*
*Researched: 2026-07-04*
</content>
