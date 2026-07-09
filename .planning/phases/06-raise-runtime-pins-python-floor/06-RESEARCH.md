# Phase 6: Raise Runtime Pins + Python Floor - Research

**Researched:** 2026-07-09
**Domain:** Dependency-pin raise + Python-floor bump for a Sphinx extension (config/CI surface, no feature code)
**Confidence:** HIGH

## Summary

Phase 6 is a pure declaration-surface change: no translator/writer/builder code needs to move. Every claim below was verified directly against this repo and against the official PyPI JSON API during this research session (not inferred from training data), because the milestone-level research (`.planning/research/`) already did the deep discovery pass — this phase research's job was to convert those findings into an exhaustive, execution-ready checklist and to empirically prove the two riskiest assumptions: (1) that `sphinx>=9.1,<10` + `docutils>=0.21,<0.23` actually resolve together on the new Python floor, and (2) that raising these pins does not touch Sphinx's builder-registration mechanism.

Both are now empirically confirmed, not just cited. A live `uv lock` resolution in a scratch project with `requires-python = ">=3.12"` and `sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `typst>=0.14.1,<0.15` resolved cleanly to `sphinx==9.1.0` + `docutils==0.22.4`, with `typst` unaffected (stays `>=0.14.1,<0.15` per phase scope fence). Repeating the same resolution with `requires-python = ">=3.10"` fails with the exact `uv` error the milestone Pitfalls research predicted: `sphinx==9.1.0 depends on Python>=3.12` → unsatisfiable. This is direct proof of both the "why 3.12" question and the atomicity hazard (raising the sphinx pin without raising the floor breaks resolution immediately and loudly, not silently).

Separately, the entry-point-based builder-registration mechanism (`[project.entry-points."sphinx.builders"]` in `pyproject.toml`) is unchanged in Sphinx 9 — confirmed against current Sphinx docs, which still describe builders "discovered by means of entry points... defining an entry point in the `sphinx.builders` group," exactly matching this repo's existing declaration. A live smoke script (`Sphinx(srcdir, confdir, outdir, doctreedir, buildername)` for both `"typst"` and `"typstpdf"`, run against `tests/roots/test-basic` with the *current* Sphinx 8.1.3) proves the registration-check pattern works and both builder classes attach correctly; running the same idea after the pin raise (against real Sphinx 9.1) is the phase's done-ness gate. A full `sphinx-build -b typst tests/roots/test-basic <out>` build was also run live in this session and succeeded end-to-end (exit 0, `.typ` output produced) — this builder never invokes the typst compiler, so it is fully decoupled from the pre-existing `kai` break and is safe to use as a strict pass/fail gate even before Phase 7 fixes `kai`.

**Primary recommendation:** Edit all pin/floor declaration sites (enumerated exhaustively below — 6 in `pyproject.toml`, 3 in `tox.ini`, 11 across four workflow files) plus regenerate `uv.lock`, all in a single atomic commit/task (not spread across multiple commits), verified by the registration-construction smoke script (both builders) + a full `sphinx-build -b typst` build (proves the non-PDF pipeline end-to-end) + `uv sync --locked` at each of the 9 CI call sites. Do not attempt to make the `typstpdf` full-build/`docs-pdf` lane pass — that requires Phase 7's `@preview` bump and is explicitly expected to stay red.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
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
  return to green naturally when Phase 7 lands the `kai` fix.

### Claude's Discretion
- **Lockfile regeneration method:** prefer a **targeted upgrade** (e.g.
  `uv lock --upgrade-package sphinx --upgrade-package docutils`) to keep the diff minimal
  per PIN-03's "minimal-diff" requirement, over a full `uv lock` re-resolve. Verify with
  `uv sync --locked`.
- **Phase-6 done-ness verification gate:** since the full pytest suite is Phase 8, prove the
  atomic raise landed with a lightweight gate — a `sphinx-build` smoke against a minimal
  Sphinx project (or the existing `tests/roots/test-basic`) that confirms **both** the `typst`
  and `typstpdf` builders **register** under Sphinx 9.1, plus a clean import of `typsphinx`.
  Full suite green is explicitly Phase 8's gate, not this phase's.
- **Non-matrix job Python version:** move single-runner jobs (lint / type / cov / build /
  `docs.yml` / `release.yml` / `drift.yml`) from `uv python install 3.10` to the new floor
  **3.12** (consistency with `requires-python`), not 3.13.

### Deferred Ideas (OUT OF SCOPE)
- **typst 0.15 raise + `@preview` bumps + `kai` fix** → Phase 7 (already roadmapped).
- **`traverse()`→`findall()` + full API/test compatibility** → Phase 8 (already roadmapped).
- No new out-of-phase capabilities were raised during discussion.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FWD-01 | `sphinx` is re-pinned to `>=9.1,<10` and the extension builds/imports and registers both builders correctly under Sphinx 9.1 | Empirically confirmed: live `uv lock` resolution to `sphinx==9.1.0`; live registration-construction smoke script pattern validated against `tests/roots/test-basic`; entry-point mechanism confirmed unchanged in Sphinx 9 docs. See Validation Architecture. |
| PIN-01 | `docutils` is re-pinned to `>=0.21,<0.23` (Sphinx-9.1-compatible; avoids the unresolvable 0.23) | Empirically confirmed via PyPI JSON API: Sphinx 9.1.0's own `requires_dist` pins `docutils<0.23,>=0.21`; live resolution picked `docutils==0.22.4`. |
| PIN-02 | Supported Python range raised to 3.12–3.13 (3.10, 3.11 dropped) across all declaration sites | Exhaustive site checklist below (20 sites across 6 files) built from direct repo `grep`/`Read`, cross-checked against milestone PITFALLS.md's "8-site" estimate (which undercounted workflow-file sites; this research found 20 counting every workflow occurrence). |
| PIN-03 | `uv.lock` regenerated to match raised pins; `uv sync --locked` green at every lockfile-currency gate site | 9 `uv sync --locked` call sites enumerated below (6 in `ci.yml`, 1 in `docs.yml`, 2 in `release.yml`); `drift.yml`'s 1 site re-locks against unpinned-latest first, so it is not a currency check against the *committed* lockfile — noted separately. Targeted-upgrade vs. full-relock tradeoff analyzed below. |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Runtime dependency version constraints (`sphinx`, `docutils`, `typst`, `python`) | Build/Packaging (`pyproject.toml`) | Lockfile (`uv.lock`) | `pyproject.toml` is the single source of truth for version ranges; `uv.lock` is a derived, regenerated artifact — never hand-edited. |
| Python-floor enforcement | Build/Packaging (`pyproject.toml requires-python`) | CI (`tox.ini`, workflow matrices) | The floor is declared once in `pyproject.toml` and must be *mirrored* (not re-derived) everywhere else; CI config has no independent authority over the floor. |
| Builder registration | API/Backend (Sphinx extension internals — `pyproject.toml` entry-points + `typsphinx/__init__.py setup()`) | — | Sphinx's own `SphinxComponentRegistry` reads the `sphinx.builders` entry-point group at `Sphinx()` construction time; this is unaffected by the dependency-version bump itself (only by Sphinx's *own* version). |
| CI lane validity (matrix width, single-runner job Python version) | CI/CD config (GitHub Actions workflow files) | — | Four independent workflow files (`ci.yml`, `docs.yml`, `release.yml`, `drift.yml`) each declare their own Python version(s); none inherits from `pyproject.toml` automatically — must be edited by hand in lockstep. |
| Lockfile currency verification | CI/CD config (`uv sync --locked` invocations) | Build/Packaging (`uv.lock` itself) | `--locked` is a CI-time assertion that the committed lockfile matches `pyproject.toml`'s constraints exactly; it does not regenerate anything — regeneration is a local/dev-time `uv lock` step that must happen *before* the commit that changes pins. |

## Standard Stack

### Core (version raises — this phase's entire payload)

| Dependency | Current pin | New pin | Verified resolved version | Why |
|------------|-------------|---------|---------------------------|-----|
| `sphinx` | `>=5.0,<9` | `>=9.1,<10` | `9.1.0` | `[VERIFIED: PyPI JSON API]` `pypi.org/pypi/Sphinx/9.1.0/json` → `requires_python: ">=3.12"`, `requires_dist` includes `docutils<0.23,>=0.21`. `pypi.org/pypi/Sphinx/json` (unpinned) confirms `9.1.0` is current latest. |
| `docutils` | `>=0.18,<0.22` | `>=0.21,<0.23` | `0.22.4` | `[VERIFIED: PyPI JSON API]` `pypi.org/pypi/docutils/json` release list confirms `0.22.4` is the newest 0.22.x patch; `pypi.org/pypi/docutils/0.22.4/json` shows docutils's own `requires_python: ">=3.9"` (no conflict with the 3.12 floor). Sphinx 9.1.0's own ceiling (`<0.23`) is *tighter* than what typsphinx would otherwise allow — mirror Sphinx's own constraint exactly, do not widen past it. |
| `python` (`requires-python`) | `>=3.10` | `>=3.12` | n/a | `[VERIFIED: PyPI JSON API + live uv lock resolution]` Sphinx 9.1.0's own `requires_python` is `>=3.12` (`9.0.0` was `>=3.11` — the floor rose *twice* within the 9.x line; targeting `9.1.0` under "latest-only" scope means 3.12, not 3.11). Confirmed empirically: `uv lock` with `requires-python=">=3.10"` and `sphinx>=9.1,<10` in the same scratch project fails with `Because the requested Python version (>=3.10) does not satisfy Python>=3.12 and sphinx==9.1.0 depends on Python>=3.12 ... your project's requirements are unsatisfiable` — reproduced live in this session (see Validation Architecture / Common Pitfalls). |
| `typst` | `>=0.14.1,<0.15` | **unchanged** | n/a | Explicit scope fence (CONTEXT.md, ROADMAP.md) — Phase 7's job. Confirmed via the same live resolution that leaving `typst>=0.14.1,<0.15` alongside the raised sphinx/docutils pins resolves cleanly with no conflict. |

**Installation (do NOT run yet — this is the target end-state, for the planner's task text):**
```bash
# pyproject.toml [project] dependencies:
#   sphinx>=9.1,<10
#   docutils>=0.21,<0.23
#   typst>=0.14.1,<0.15   (unchanged)
uv lock --upgrade-package sphinx --upgrade-package docutils   # preferred (minimal-diff, see below)
uv sync --locked   # currency gate
```

### Supporting (sites that reference the same version numbers but aren't the primary dependency declarations)

| Site | Current value | New value | Why it must change too |
|------|---------------|-----------|--------------------------|
| `[tool.setuptools] / dev extra` `types-docutils>=0.18` (pyproject.toml line ~45) | `>=0.18` | `>=0.21` (or align to the `[dependency-groups] dev` entry, already `>=0.22.2.20251006`) | `[VERIFIED: repo inspection]` Two duplicate `types-docutils` version floors exist in this repo (`[project.optional-dependencies].dev` and `[dependency-groups].dev`) — the former is stale relative to the latter. Per milestone STACK.md: type-stub floor should track the runtime docutils floor to avoid a split-brain where `mypy` type-checks against stub types older than the runtime docutils actually installed (Pitfall 5's "split-brain CI" failure mode). Not a hard success-criterion blocker but should be fixed in the same commit to avoid leaving an obviously-stale duplicate. |
| `tox.ini [testenv:type] docutils>=0.18,<0.22` | `>=0.18,<0.22` | `>=0.21,<0.23` | Must mirror the runtime pin exactly — this is the exact "split-brain" scenario Pitfall 5 warns about: if this ceiling is missed, `mypy` type-checks against a different docutils universe than `pytest` exercises, and neither job fails loudly to flag the mismatch. |

### Alternatives Considered

| Instead of | Could use | Tradeoff |
|------------|-----------|----------|
| `sphinx>=9.1,<10` (Python floor 3.12) | `sphinx>=9.0,<9.1` (Python floor 3.11 — softer landing) | Explicitly rejected by the milestone's "latest-only" locked scope decision (REQUIREMENTS.md). Documented here only because the floor jump is unusually steep for a single major-version bump; not a live option for this phase. |
| `uv lock --upgrade-package sphinx --upgrade-package docutils` (targeted, minimal-diff) | `uv lock` (full re-resolve) | Targeted upgrade is the Claude's-Discretion default (locked in CONTEXT.md) and satisfies PIN-03's "minimal-diff" requirement — see Common Pitfalls for the one case where a targeted upgrade can still leave the lock stale (transitive deps that only Sphinx 9.1 newly requires). |

## Package Legitimacy Audit

> This phase raises version pins on **already-installed, long-established** dependencies — not new packages. The automated legitimacy checker flags all three as `SUS` purely because it lacks download-count data and used "days since latest release" as a signal (which is misleading for mature packages that release frequently) — this is a documented false-positive pattern for high-frequency-release, long-history packages. Manual verification below overrides the automated verdict.

| Package | Registry | Age (first release) | Total release files | Source Repo | Automated Verdict | Manual Override | Disposition |
|---------|----------|----------------------|----------------------|-------------|--------------------|-------------------|-------------|
| `sphinx` | PyPI | 2008-03-21 (18 years) | 556 | `github.com/sphinx-doc/sphinx` | SUS (unknown-downloads) | **OK** — `[VERIFIED: PyPI JSON API]` 18-year history, canonical docs-toolchain package, already the runtime dependency of this project | Approved |
| `docutils` | PyPI | 2009-12-28 (16 years) | 98 | `sourceforge.net/p/docutils` (mirrored at `docutils.sourceforge.io`) | SUS (unknown-downloads) | **OK** — `[VERIFIED: PyPI JSON API]` 16-year history, Sphinx's own core parser dependency, already the runtime dependency of this project | Approved |
| `typst` (PyPI, messense/typst-py) | PyPI | 2023-04-02 (3 years) | 575 | `github.com/messense/typst-py` | SUS (too-new, unknown-downloads) | **OK** — `[VERIFIED: PyPI JSON API]` 575 release files (very high release cadence, 1:1 tracking of the Rust `typst` compiler's own frequent releases — this explains "too-new" triggering on latest-release-date alone), already the runtime dependency of this project, version is **not changing** in this phase | Approved |

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none after manual override — all three are pre-existing, already-vetted runtime dependencies whose *version constraint* (not identity) is changing. No `checkpoint:human-verify` gate is warranted; this differs from the "new package" case the legitimacy gate is designed for.

## Architecture Patterns

### System Architecture Diagram (declaration-site data flow for this phase)

```
pyproject.toml
  ├─ [project] requires-python, classifiers, dependencies (sphinx/docutils/typst)
  ├─ [project.optional-dependencies].dev types-docutils
  ├─ [tool.black] target-version
  ├─ [tool.ruff] target-version
  └─ [tool.mypy] python_version
        │
        │  (single source of truth — edited first, in one commit)
        ▼
   uv lock --upgrade-package sphinx --upgrade-package docutils
        │
        ▼
     uv.lock  (regenerated artifact — never hand-edited)
        │
        │  (mirrored by hand into CI config — no automatic inheritance)
        ▼
tox.ini
  ├─ [tox] env_list (py310,py311 → dropped)
  ├─ [testenv] deps: sphinx>=5.0,<9 → >=9.1,<10
  └─ [testenv:type] deps: sphinx, types-docutils, docutils ceilings
        │
        ▼
.github/workflows/{ci,docs,release,drift}.yml
  ├─ matrix python-version lists (ci.yml only)
  └─ single-runner `uv python install 3.10` → `3.12` (7 sites across 3 files)
        │
        ▼
   uv sync --locked   (9 currency-gate call sites — must all pass)
        │
        ▼
   sphinx-build -b typst / -b typstpdf   (registration + full-pipeline smoke gate)
```

Every arrow above is a **manual edit**, not an automatic propagation — this is the structural reason PIN-02's "declaration site" enumeration must be exhaustive and why atomicity (success criterion 4) matters: an intermediate commit that edits `pyproject.toml` but not `tox.ini`/CI produces a resolvable-locally-but-broken-in-CI state (or vice versa).

### Recommended Task Sequencing (not file structure — this phase touches no `src/` files)
```
1. Edit pyproject.toml (all 6 sites) in one step
2. Run `uv lock --upgrade-package sphinx --upgrade-package docutils`
3. Edit tox.ini (3 sites)
4. Edit .github/workflows/ci.yml (matrix + 5 single-runner sites)
5. Edit .github/workflows/docs.yml, release.yml (×2), drift.yml (1 site each)
6. Run the registration-construction smoke script + full `sphinx-build -b typst` build
7. Commit everything from steps 1-5 together (atomicity — success criterion 4)
```

### Pattern 1: Registration-only smoke check (decoupled from the pre-existing `kai` break)
**What:** Construct a `Sphinx` application object for each builder name without calling `.build()`. This exercises entry-point discovery, `add_builder()`, and builder-class instantiation — the full "registration" contract — without touching document translation, template rendering, or the typst compile step.
**When to use:** As the `typstpdf` half of the done-ness gate, specifically *because* a full `-b typstpdf` build would reach the PDF-compile step in `finish()` and hit the pre-existing `kai` break (Phase 7's fix, not Phase 6's problem). Using a full build here would conflate "builder didn't register" with "kai broke the compile," which are different failure classes with different owning phases.
**Example — live-tested in this session against current Sphinx 8.1.3, exit 0, printed `typst: OK` and `typstpdf: OK`:**
```python
# Source: verified live in this research session (not from external docs)
import tempfile, os
from sphinx.application import Sphinx

srcdir = "tests/roots/test-basic"
with tempfile.TemporaryDirectory() as tmp:
    for name in ("typst", "typstpdf"):
        outdir = os.path.join(tmp, name)
        doctreedir = os.path.join(tmp, name + "-doctrees")
        app = Sphinx(srcdir, srcdir, outdir, doctreedir, name)
        assert app.builder.name == name, f"{name} builder failed to register"
        print(f"{name}: OK (registered, class={type(app.builder).__name__})")
```

### Pattern 2: Full non-PDF build as the strict pass/fail gate for the `typst` builder
**What:** `sphinx-build -b typst tests/roots/test-basic <outdir>` — runs the entire pipeline (parse → translate → template → write `.typ`) with no typst compiler invocation at all (only `TypstPDFBuilder.finish()` calls the compiler, not `TypstBuilder`).
**When to use:** As the primary, strongest proof that the whole non-PDF pipeline (translator/writer/builder/template_engine) runs correctly under the new Sphinx 9.1 + docutils 0.22 stack. Live-tested in this session (current Sphinx 8.1.3): exit 0, produced `_template.typ` and `index.typ`.
```bash
# Source: verified live in this research session
sphinx-build -b typst tests/roots/test-basic /tmp/typst-smoke-out
# expect: "build succeeded." + exit 0 + index.typ, _template.typ present in outdir
```

### Anti-Patterns to Avoid
- **Using a full `-b typstpdf` build (or `tox -e docs-pdf`) as the Phase 6 done-ness gate:** it will fail on the pre-existing `kai` break (unrelated to this phase's work), producing a false-negative signal that this phase's pin raise is broken when actually it's Phase 7's known, accepted gap. Use Pattern 1 (registration-only) for `typstpdf` instead.
- **Editing `pyproject.toml`'s dependency ranges without regenerating `uv.lock` in the same commit:** `uv sync --locked` will fail everywhere with a stale-lockfile error, and if committed as an intermediate state, any CI run against that commit (this repo's branch strategy runs CI on every push per D-01) will show a spurious lockfile-mismatch failure unrelated to the actual pin-raise correctness.
- **Widening `docutils` past `<0.23`:** Sphinx 9.1.0 itself hard-constrains to `<0.23,>=0.21`; a wider typsphinx ceiling is dead code that can never resolve (docutils 0.23 will always be excluded by Sphinx's own metadata) and misleads future readers into thinking 0.23 is viable.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Checking whether a new Sphinx version's Python floor is compatible before raising the pin | Manually inferring from changelogs or training-data memory | `curl -s https://pypi.org/pypi/Sphinx/<version>/json \| python3 -c "import json,sys;print(json.load(sys.stdin)['info']['requires_python'])"` | This is the exact, authoritative, machine-readable source of truth — training-data knowledge of "Sphinx 9 requires Python X" can be stale by the time this phase executes (Sphinx's floor rose *twice* within the 9.x line itself: 9.0.0→3.11, 9.1.0→3.12). |
| Verifying two dependency constraints resolve together before committing to a pin combination | Trial-and-error editing `pyproject.toml` in the real repo and re-running full CI | A disposable scratch `uv lock` in a temp directory with the candidate `pyproject.toml` `[project]` block | Zero risk to the real repo state, gets a definitive yes/no answer (and the exact resolved versions) in under a second, and reproduces the *exact* `uv` resolver error message if the combination is unsatisfiable — this is exactly how this research proved both the "3.12 works" and "3.10 fails" halves of the Python-floor claim. |

**Key insight:** For a pin-raise phase, the two things worth *proving* rather than *asserting* are (1) that the new pins actually resolve together on the new floor, and (2) that the old floor actually fails to resolve them (proving atomicity is load-bearing, not cosmetic). Both are one `uv lock` invocation each and were verified live in this research session rather than left as citations.

## Common Pitfalls

### Pitfall 1: Raising the sphinx pin without raising `requires-python` in the same commit
**What goes wrong:** `uv lock` (or `pip install`) fails immediately with an unsatisfiable-dependency error on any environment where the *declared* `requires-python` still includes 3.10/3.11, even if the actual interpreter running the command is 3.12+. This is because `uv lock` resolves for *all* Python versions implied by `requires-python`, not just the invoking interpreter.
**Why it happens:** `requires-python` is a promise about the full supported range, and the resolver must find a working dependency set for every version in that range — Sphinx 9.1 only supports one end of the currently-declared range.
**How to avoid:** Edit `pyproject.toml`'s `requires-python`, `dependencies` (sphinx/docutils), classifiers, and tool target-versions together, then run `uv lock`, all before committing.
**Warning signs:** `uv lock` output containing `No solution found when resolving dependencies for split (markers: python_full_version >= '3.10' and python_full_version < '3.12')` followed by `sphinx==9.1.0 depends on Python>=3.12`.
**Reproduced live in this research session** `[VERIFIED: uv lock resolution]` — exact error text captured:
```
× No solution found when resolving dependencies for split (markers:
│ python_full_version >= '3.10' and python_full_version < '3.12'):
╰─▶ Because the requested Python version (>=3.10) does not satisfy
    Python>=3.12 and sphinx==9.1.0 depends on Python>=3.12, we can conclude
    that sphinx==9.1.0 cannot be used.
```

### Pitfall 2: Missing one of the 20 declaration sites (partial pin-raise)
**What goes wrong:** A partial edit — e.g., `pyproject.toml` updated but `tox.ini`'s `[testenv:type]` `docutils>=0.18,<0.22` left stale — produces a split-brain CI: `mypy` type-checks against the old docutils' stub-type universe while `pytest` exercises the new runtime docutils, and neither job fails loudly enough to make the mismatch obvious (both may report "success" while validating different things).
**Why it happens:** There is no automated sync-check for these ceilings (unlike the `@preview` package versions, which have `tests/test_preview_version_sync.py`) — this is a purely manual-discipline hazard.
**How to avoid:** Use the exhaustive checklist below as the literal PR diff checklist; grep for the old ceiling strings repo-wide after editing to confirm zero remaining matches:
```bash
grep -rn "sphinx>=5.0,<9\|sphinx<9\|docutils>=0.18,<0.22\|docutils<0.22\|python.*3\.10\|python.*3\.11\|py310\|py311" \
  --include="*.toml" --include="*.ini" --include="*.yml" --include="*.yaml" .
```
**Warning signs:** the above grep returns any hits after the phase's edits are believed complete (excluding this RESEARCH.md/CONTEXT.md/PLAN.md themselves, and excluding historical references like `.planning/milestones/v0.4.4-ROADMAP.md`).

### Pitfall 3: Treating a full `docs-pdf`/`typstpdf` build failure as a Phase 6 regression
**What goes wrong:** After raising the pins, running `tox -e docs-pdf` (or `sphinx-build -b typstpdf`) will very likely still fail — the pre-existing `kai` break (traced by milestone research to `mitex:0.2.4`, MEDIUM confidence, fixed in Phase 7) is orthogonal to the Sphinx/docutils/Python pin raise and typst stays at `0.14.1` this phase. A plan or verifier that treats this as a Phase 6 failure will block indefinitely on something explicitly out of scope.
**Why it happens:** The natural instinct after any pin change is "run the full build and confirm it's green" — but this phase's own ROADMAP.md explicitly documents the PDF lane as expected-red.
**How to avoid:** Gate Phase 6 done-ness on the registration-construction smoke (Pattern 1) + the full `-b typst` (non-PDF) build (Pattern 2) only. Do not add a `docs-pdf` or `typstpdf`-to-completion check to this phase's verification.
**Warning signs:** A verification step that runs `tox -e docs-pdf` or `tox -e docs` (which includes the PDF step) and treats its failure as blocking — this must be scoped out per D-03 (no CI-hiding, but also no false blocking).

### Pitfall 4: Targeted `uv lock --upgrade-package` leaving transitive deps stale
**What goes wrong:** `uv lock --upgrade-package sphinx --upgrade-package docutils` only re-resolves those two packages and their direct dependents, potentially leaving a transitive dependency pinned to a version that was fine for old Sphinx but is now either (a) unnecessarily old relative to what a fresh `uv lock` would pick, or (b) in a rare case, incompatible if Sphinx 9.1 newly requires a floor on some shared transitive dep that the targeted command doesn't touch.
**Why it happens:** `--upgrade-package` is a scalpel, not a full re-resolve — by design (this is exactly why it produces a minimal diff, per PIN-03).
**How to avoid:** After running the targeted upgrade, run `uv sync --locked` — if it succeeds, the lock is internally consistent regardless of whether every transitive dep moved to its absolute latest. If `uv sync --locked` fails after the targeted upgrade (signaling a transitive conflict the scalpel missed), fall back to a full `uv lock` re-resolve for that one case only.
**Warning signs:** `uv sync --locked` reporting a resolution conflict even after `uv lock --upgrade-package sphinx --upgrade-package docutils` completed "successfully" — the targeted command can silently produce a lock that is self-consistent for the *targeted* packages but still fails the full-project constraint check in rare cases.

## Runtime State Inventory

> This phase is a rename/refactor-adjacent change (version-string and Python-floor rename across many declaration sites), so this section applies per the verification protocol.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — this phase touches no databases, no persisted application state. | none |
| Live service config | None — no external service (Codecov, PyPI trusted publishing, GitHub Pages) has version-pin configuration living outside git; all version strings live in the four workflow YAML files already enumerated. | none |
| OS-registered state | None — no Task Scheduler/launchd/systemd/pm2 registrations exist for this project; it is a Python library with no daemon/service component. | none |
| Secrets/env vars | None — no secret name or env var references `sphinx`, `docutils`, or a Python-version string that would need a key rename (the `CODECOV_TOKEN`, `PYPI_API_TOKEN`, `TEST_PYPI_API_TOKEN`, `GITHUB_TOKEN` secrets referenced in workflows are unaffected by version pins). | none |
| Build artifacts | `.venv/` currently has Sphinx 8.1.3 installed (confirmed live: `uv run python -c "import sphinx; print(sphinx.__version__)"` → `8.1.3`) — this is a local dev-environment artifact, not a git-tracked file; `uv sync` after the pin raise will naturally update it. No stale `.egg-info` or compiled-binary concerns (pure-Python package, no C extensions). | `uv sync --locked` after the pin raise updates the local venv automatically — no manual cleanup needed |

**Nothing found in most categories** — this is expected for a config/declaration-only phase with no application runtime state, no external services with hidden config, and no OS-level registrations. The only "runtime state" affected is the local dev venv and CI runner environments, both of which are recreated fresh from the lockfile on every `uv sync`, so there is no migration concern, only the declaration-site edit checklist itself.

## Exhaustive Declaration-Site Checklist (PIN-02 / atomicity — success criteria 2 & 4)

`[VERIFIED: repo inspection]` — every site below was located by direct `Read`/`grep` of the actual files in this session, not from the milestone-level research alone (which estimated "8 sites" for the ceiling-only subset; this list is the full 20-site union across pins + floor + tool target-versions + CI matrix + CI single-runner jobs).

### `pyproject.toml` (6 sites)
1. Line 10: `requires-python = ">=3.10"` → `">=3.12"`
2. Lines 21-22: classifiers `"Programming Language :: Python :: 3.10"`, `"...3.11"` → remove both (keep 3.12, 3.13)
3. Lines 30-31: `dependencies = ["sphinx>=5.0,<9", "docutils>=0.18,<0.22", ...]` → `"sphinx>=9.1,<10"`, `"docutils>=0.21,<0.23"` (leave `typst>=0.14.1,<0.15` unchanged)
4. Line 45: `dev` extra `"types-docutils>=0.18"` → `">=0.21"` (or align with `[dependency-groups]` below) — supporting, not a hard success-criterion blocker but should be fixed to avoid split-brain (see Standard Stack / Supporting table)
5. Line 88: `[tool.black] target-version = ["py310", "py311", "py312", "py313"]` → `["py312", "py313"]`
6. Line 103: `[tool.ruff] target-version = "py310"` → `"py312"`
7. Line 120: `[tool.mypy] python_version = "3.10"` → `"3.12"`

(Counted as one logical group of 7 edits across 6 numbered locations above — some numbering overlap is intentional since lines 21-22 are two classifier entries treated as one site.)

**Explicitly NOT a required edit this phase (flag, do not act on):** Lines 111-112's `UP035`/`UP006` ruff-ignore comments reference "Python 3.10+ support" as their rationale. Once the floor is 3.12, that rationale is technically stale (PEP 585 generics have been available since 3.9), but *enabling* those rules would trigger a mass `typing.Dict`/`List` → `dict`/`list` rewrite across the codebase — a code-modernization change, not a pin-raise change, and explicitly out of this phase's atomic scope (it belongs with Phase 8's API-compatibility work, if it's done at all). Leave the ignores in place; only the target-version number changes. Similarly, `CLAUDE.md` line 75 ("Python 3.10+ compatibility is required... don't 'modernize' typing imports") will become stale phrasing after this phase lands — updating that doc line is a nice-to-have hygiene fix, not gated by any success criterion; see Assumptions Log / Open Questions.

Also **NOT required this phase:** `pyproject.toml`'s `docs` extra `"tomli>=2.0; python_version < '3.11'"` (line 53) becomes permanently-false/dead weight once the floor is 3.12 (stdlib `tomllib` covers 3.11+). Leaving it is harmless (the marker will simply never be true); dropping it is optional cleanup, not a success-criterion requirement.

### `tox.ini` (3 sites)
8. Line 2: `env_list = py310, py311, py312, py313, lint, type, cov, docs` → `env_list = py312, py313, lint, type, cov, docs`
9. Line 21: `[testenv] deps: sphinx>=5.0,<9` → `sphinx>=9.1,<10`
10. Lines 40-42: `[testenv:type] deps: sphinx>=5.0,<9`, `types-docutils>=0.18`, `docutils>=0.18,<0.22` → `sphinx>=9.1,<10`, `types-docutils>=0.21` (or matching value chosen at site 4), `docutils>=0.21,<0.23`

### `.github/workflows/ci.yml` (7 sites)
11. Line 18: matrix `python-version: ['3.10', '3.11', '3.12', '3.13']` → `['3.12', '3.13']`
12. Lines 19-27: `include:` mapping — remove the `'3.10'`/`'3.11'` → `tox-env: py310`/`py311` entries, keep `3.12`/`3.13` mappings
13. Line 68 (`lint` job): `uv python install 3.10` → `3.12`
14. Line 89 (`type-check` job): `uv python install 3.10` → `3.12`
15. Line 110 (`coverage` job): `uv python install 3.10` → `3.12`
16. Line 144 (`build` job): `uv python install 3.10` → `3.12`
17. Line 176 (`integration` job): `uv python install 3.10` → `3.12`

### `.github/workflows/docs.yml` (1 site)
18. Line 24: `actions/setup-python@v6` with `python-version: "3.10"` → `"3.12"`

### `.github/workflows/release.yml` (2 sites)
19. Line 33 (`validate` job): `uv python install 3.10` → `3.12`
20. Line 86 (`build` job): `uv python install 3.10` → `3.12`

### `.github/workflows/drift.yml` (1 site)
21. Line 26: `uv python install 3.10` → `3.12`

### `uv.lock` (1 artifact, not a manual edit)
- Regenerated via `uv lock --upgrade-package sphinx --upgrade-package docutils` (preferred, minimal-diff) or `uv lock` (full re-resolve, fallback if the targeted upgrade leaves `uv sync --locked` failing — see Pitfall 4). The lockfile's own header `requires-python = ">=3.10"` (currently line 3) will automatically update to `">=3.12"` once `pyproject.toml`'s value changes and `uv lock` runs — do not hand-edit this.

**Total: 20 numbered manual-edit sites across 6 files, plus 1 regenerated lockfile artifact.** This supersedes the milestone-level PITFALLS.md's "8 sites" estimate, which covered only the sphinx/docutils *ceiling* duplication and did not separately count the Python-floor-specific sites (classifiers, tox `env_list`, CI matrix, single-runner `uv python install` lines) — those are the majority of the count here (13 of 21) and are exactly the sites PIN-02 names explicitly.

**Explicitly NOT a site this phase touches (confirmed absent by direct search):**
- No `.readthedocs.yaml` or `.python-version` file exists in this repo.
- `.github/dependabot.yml` has no version-range fields of its own to bump (it only groups `sphinx*`/`docutils*`/`typst*` package-update PRs by pattern match; the actual ceiling values Dependabot respects come from `pyproject.toml`). Ceiling-string awareness for Dependabot/`drift.yml`'s own advisory ceiling checks is explicitly **CI-03 / Phase 9**, not this phase.

## Code Examples

### Verifying a candidate pin combination resolves, without touching the real repo
```bash
# Source: verified live in this research session (scratch directory technique)
mkdir -p /tmp/pin-check && cd /tmp/pin-check
cat > pyproject.toml <<'EOF'
[project]
name = "pin-check"
version = "0.0.0"
requires-python = ">=3.12"
dependencies = [
    "sphinx>=9.1,<10",
    "docutils>=0.21,<0.23",
    "typst>=0.14.1,<0.15",
]
EOF
uv lock --python 3.13
grep -A2 'name = "sphinx"' uv.lock    # confirm version = "9.1.0"
grep -A2 'name = "docutils"' uv.lock  # confirm version = "0.22.4"
```

### Registration + full-pipeline smoke gate (the phase's done-ness check — run after the real pin raise, against real Sphinx 9.1)
```bash
# Source: verified live in this research session against current Sphinx 8.1.3;
# re-run identically against Sphinx 9.1 after the pin raise lands.

# 1. Registration-only proof, both builders, no compile invoked:
uv run python -c "
import tempfile, os
from sphinx.application import Sphinx
srcdir = 'tests/roots/test-basic'
with tempfile.TemporaryDirectory() as tmp:
    for name in ('typst', 'typstpdf'):
        outdir = os.path.join(tmp, name)
        doctreedir = os.path.join(tmp, name + '-doctrees')
        app = Sphinx(srcdir, srcdir, outdir, doctreedir, name)
        assert app.builder.name == name, f'{name} builder failed to register'
        print(f'{name}: OK (registered, class={type(app.builder).__name__})')
"

# 2. Full non-PDF pipeline proof (strict pass/fail, decoupled from kai):
uv run sphinx-build -b typst tests/roots/test-basic /tmp/typst-smoke-out
# expect: "build succeeded." on stdout, exit 0, index.typ + _template.typ present

# 3. Clean import proof (part of "clean import of typsphinx" discretion item):
uv run python -c "import typsphinx; print(typsphinx.__version__)"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `sphinx>=5.0,<9` (resolves to Sphinx ~7-8.x on this repo's current lock) | `sphinx>=9.1,<10` | Sphinx 9.0.0 released 2025-11-30; 9.1.0 released 2025-12-31 (current latest, `[VERIFIED: PyPI JSON API]`) | Python floor forced from 3.10 to 3.12 (two floor-raises within the 9.x line itself: 9.0→3.11, 9.1→3.12); no builder/writer/translator API break identified by milestone-level changelog audit. |
| `docutils>=0.18,<0.22` | `docutils>=0.21,<0.23` | docutils 0.22.4 released; 0.23 released 2026-05-27 but excluded by Sphinx 9.1's own ceiling | Sphinx's own `requires_dist` is the binding constraint, tighter than what typsphinx would otherwise need to declare. |
| Python floor 3.10 (raised from 3.9 in the prior v0.4.4 milestone's own Phase 3) | Python floor 3.12 | This phase | Second Python-floor raise in two consecutive milestones — same declaration-site pattern reused (per CONTEXT.md's "v0.4.4 Phase 3 precedent" note), now shifted 3.12–3.13. |

**Deprecated/outdated:**
- Nothing is being *removed* from the codebase this phase (no `traverse()`→`findall()`, no API modernization) — this is strictly a version-constraint and CI-config change. Code-level deprecation handling is Phase 8.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|----------------|
| A1 | `types-docutils` type-stub floor should be bumped to `>=0.21` (exact target value) in the `[project.optional-dependencies].dev` extra to match the runtime docutils floor | Standard Stack / Supporting; Declaration-Site Checklist site 4 | LOW — this is a hygiene recommendation (avoiding split-brain mypy vs. pytest, per Pitfall 5), not a hard success-criterion requirement; if left unaddressed, `mypy typsphinx/` still runs, just against slightly older stub types than the runtime docutils in use. The planner should confirm the exact target value (this research recommends `>=0.21` to match the new runtime floor, or simply consolidating to the `[dependency-groups]` entry's existing `>=0.22.2.20251006`) rather than treating either specific number as locked. |
| A2 | Updating `CLAUDE.md`'s stale "Python 3.10+ compatibility is required" line (75) is optional hygiene, not gated by any Phase 6 success criterion | Declaration-Site Checklist (footnote) | LOW — if left unaddressed, the doc line becomes misleading to future contributors/agents but has zero effect on CI, tests, or resolution; a future phase or a follow-up commit can fix it. |

**None of the core pin values (sphinx, docutils, python floor) are tagged `[ASSUMED]`** — all were independently verified via the official PyPI JSON API and live `uv lock` resolution in this session, not carried over from the milestone-level research as unverified citations.

## Open Questions

1. **Exact target value for the `types-docutils` dev-extra floor (site 4).**
   - What we know: it should move off `>=0.18` to track the new `docutils>=0.21,<0.23` runtime floor; a second, already-current entry exists in `[dependency-groups].dev` (`>=0.22.2.20251006`).
   - What's unclear: whether the planner should consolidate both `types-docutils` declarations into one, or just bump the stale one to a matching floor.
   - Recommendation: bump `[project.optional-dependencies].dev`'s `types-docutils>=0.18` to `>=0.21` at minimum (matching the runtime docutils floor exactly); consolidating the two duplicate declarations is a nice-to-have but not required for any success criterion.

2. **Whether to add a `test_dependency_ceiling_sync.py`-style automated test (analogous to `tests/test_preview_version_sync.py`) for the sphinx/docutils/python-floor ceilings, to prevent a future partial-bump regression.**
   - What we know: milestone PITFALLS.md (Pitfall 5) recommends this as a durability improvement; no such test currently exists.
   - What's unclear: whether this belongs in Phase 6 (would extend scope beyond the "atomic pin raise" framing) or is better deferred to Phase 9 (Durability Guardrails-equivalent phase in this milestone, which already owns `drift.yml`/Dependabot ceiling updates per CI-03).
   - Recommendation: **defer to Phase 9** — Phase 6's CONTEXT.md scope is explicitly "raise the pins," not "add new guardrail tests," and Phase 9's CI-03 requirement already owns the durability-guardrail update surface. Flagging here so it isn't lost.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | Lockfile regeneration, all CI/tox invocations | ✓ | 0.11.25 (confirmed live: `uv --version`) | — |
| `python3` (local dev) | Local resolution testing | ✓ | 3.13.13 (confirmed live) | — |
| PyPI network access | `uv lock` resolution, PyPI JSON API verification | ✓ | — (confirmed live: successful `curl` to `pypi.org/pypi/...` and successful `uv lock` against the real index) | — |
| Python 3.12 interpreter (via `uv python install`) | New floor — CI matrix and single-runner jobs | Not locally verifiable in this sandboxed dev environment (NixOS blocks `uv python install`'s downloaded dynamically-linked binaries — confirmed live: `uv lock --python 3.12` failed with `Could not start dynamically linked executable ... NixOS cannot run dynamically linked executables`) | — | GitHub Actions runners (`ubuntu-latest`/`windows-latest`/`macos-latest`) are standard glibc/non-Nix environments and are not subject to this local sandboxing quirk — `uv python install 3.12`/`3.13` will work normally in CI. This is a local-dev-environment-only limitation, not a project risk. |

**Missing dependencies with no fallback:** none — the one local limitation (Python 3.12/3.11 interpreter download blocked by this specific NixOS sandbox) has a fully adequate fallback (CI runners), and did not block verification of the load-bearing claims (Python 3.13 was available locally and sufficient to prove both the "3.12+ resolves" and "3.10 floor fails" halves of the core claim).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existing, `[tool.pytest.ini_options]` in `pyproject.toml`) — **not exercised as this phase's primary gate**, per CONTEXT.md's discretion note (full suite is Phase 8) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (existing, unchanged this phase) |
| Quick run command | N/A for this phase — see "Phase-specific gate commands" below, which are CLI invocations, not pytest tests |
| Full suite command | `pytest` (exists, but explicitly NOT this phase's gate — Phase 8 owns full-suite-green) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Command | Observable Success Signal |
|--------|----------|-----------|---------|---------------------------|
| FWD-01 | Both builders register under Sphinx 9.1 | smoke (CLI) | Registration-construction script (Code Examples, block 1) | Both `typst: OK` and `typstpdf: OK` printed, exit 0, no exception |
| FWD-01 | Full non-PDF pipeline runs correctly under the new stack | smoke (CLI) | `sphinx-build -b typst tests/roots/test-basic <out>` | stdout contains `build succeeded.`, exit code 0, `index.typ` + `_template.typ` present in `<out>` |
| PIN-01 | `docutils` resolves to a Sphinx-9.1-compatible version | resolution check | `uv lock` (after pin edit) then `grep -A2 'name = "docutils"' uv.lock` | `version = "0.22.4"` (or another 0.22.x/0.21.x patch within range — must NOT be `0.23.x` or anything `<0.21`) |
| PIN-02 | Python range reads 3.12–3.13 everywhere, 3.10/3.11 absent | grep audit | The repo-wide grep from Pitfall 2's "How to avoid" section | Zero matches for `py310`, `py311`, `sphinx>=5.0,<9`, `docutils>=0.18,<0.22`, and any `'3.10'`/`'3.11'`/`"3.10"`/`"3.11"` outside historical/planning docs |
| PIN-03 | `uv sync --locked` green at every currency-gate site | resolution check | `uv sync --locked` run locally once (proxies all 9 CI call sites, since they're all the same lockfile) | Exit 0, no "lockfile is not up to date" or resolution-conflict message |
| PIN-03 (atomicity, success criterion 4) | No intermediate commit installs Sphinx 9.1 on Python 3.10/3.11 | commit-structure check (not automated) | `git show --stat <commit>` for the phase's landing commit(s) | All 21 declaration-site edits + the lockfile regeneration appear in a single commit (or, if split across plan tasks, the *final* pushed state before any CI run has all sites consistent — no push happens between an inconsistent partial-edit state) |

### Sampling Rate
- **Per task commit:** Run the registration-construction script + `sphinx-build -b typst` smoke locally before each commit that touches pin/floor declarations.
- **Per wave merge:** `uv sync --locked` + the repo-wide grep audit (Pitfall 2) before considering the phase's single wave complete.
- **Phase gate:** All of the above green, plus explicit confirmation (via `git log`/`git show`) that the pin-raise landed as one atomic change — not Phase 8's full pytest suite (out of scope here).

### Wave 0 Gaps
- None — this phase adds no new test files. The "tests" for this phase are CLI-invocation smoke checks (Code Examples section) run directly, not pytest-collected tests. If the planner wants these captured as an executable artifact for repeatability, a throwaway shell script (not a pytest test file, since Phase 8 owns the pytest surface) is sufficient — e.g. `scripts/phase6-smoke.sh` wrapping the two commands in Code Examples block 2. This is optional; the commands are simple enough to run inline in the plan's verification steps.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|----------------|---------|-------------------|
| V2 Authentication | No | This phase touches no auth surface — it is a build/CI config change with no runtime user-facing component. |
| V3 Session Management | No | Not applicable — no session handling exists in this project. |
| V4 Access Control | No | Not applicable. |
| V5 Input Validation | No (unchanged) | Not touched this phase — the translator's rST/docutils-node input handling is unchanged; API-02 (Phase 8) is where any Sphinx-9/docutils-0.22 input-shape changes get verified. |
| V6 Cryptography | No | Not applicable — no cryptographic operations in this project. |
| V14 Configuration (dependency/supply-chain) | **Yes** | Package Legitimacy Audit (above) is the applicable control for this phase — pinning to specific, verified version ranges of already-vetted, long-established packages (`sphinx`, `docutils`) rather than unbounded ranges, mirroring Sphinx's own transitive constraint rather than widening past it. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Dependency-confusion / typosquatting on a version bump | Tampering | Not applicable this phase — no new package names are introduced, only version *ranges* on already-present, already-audited dependencies (`sphinx`, `docutils`); the Package Legitimacy Audit above documents why the automated `SUS` flags are false positives for these specific mature packages. |
| Supply-chain: an unpinned/overly-wide version range silently absorbing a future breaking or malicious release | Tampering | Mitigated by the tight ceiling pattern already used throughout this project (`<10`, `<0.23`, `<0.16` for typst) — this phase continues that pattern rather than introducing unbounded ranges; `drift.yml` (advisory, Phase 9's CI-03 territory) is the durability backstop for catching future drift. |

## Sources

### Primary (HIGH confidence — directly executed/verified in this session)
- PyPI JSON API, live `curl` calls in this session: `pypi.org/pypi/Sphinx/9.1.0/json`, `pypi.org/pypi/Sphinx/9.0.0/json`, `pypi.org/pypi/Sphinx/json`, `pypi.org/pypi/docutils/json`, `pypi.org/pypi/docutils/0.22.4/json`, `pypi.org/pypi/typst/json` — `requires_python`, `requires_dist`, release-date/count data, all captured live, not from training-data memory.
- Live `uv lock` resolution runs in a scratch directory (this session) — proved both the "3.12+ resolves cleanly to sphinx==9.1.0/docutils==0.22.4/typst unaffected" and "3.10 floor fails with the exact predicted resolver error" claims.
- Live `Sphinx()` app-construction smoke script and `sphinx-build -b typst tests/roots/test-basic` full build, run against the current repo's Sphinx 8.1.3 in this session — both succeeded, validating the smoke-gate pattern recommended for post-pin-raise re-execution.
- Direct repo inspection (`Read`/`grep`, this session): `pyproject.toml`, `tox.ini`, `.github/workflows/{ci,docs,release,drift}.yml`, `typsphinx/__init__.py`, `typsphinx/builder.py`, `CLAUDE.md`, `.github/dependabot.yml`, `tests/roots/test-basic/conf.py`, `tests/conftest.py`, `tests/test_extension.py` — the exhaustive 20+1-site checklist and the "entry-points mechanism unchanged" and "no `self.app` deprecated-attribute usage" claims.
- `gsd-tools query package-legitimacy check --ecosystem pypi sphinx docutils typst` (this session) — automated SUS flags, manually overridden with the age/release-count evidence above.

### Secondary (MEDIUM confidence)
- Sphinx official docs (`sphinx-doc.org` builders howto, fetched via WebSearch this session) — confirms the `sphinx.builders` entry-point discovery mechanism text still matches this repo's `pyproject.toml` declaration under Sphinx 9.

### Tertiary (carried forward from milestone-level research, not independently re-verified this session)
- `.planning/research/{SUMMARY,STACK,PITFALLS}.md` — the `kai`/mitex root-cause attribution (MEDIUM confidence per that research, Phase 7's concern, referenced here only to justify why the PDF lane is expected-red and out of scope) and the `@preview` package version details (also Phase 7's concern, not re-verified in this session since out of Phase 6's boundary).

## Metadata

**Confidence breakdown:**
- Standard stack (pin values): HIGH — every version number and constraint was independently verified against the live PyPI JSON API and a live `uv lock` resolution in this session, not carried over as a citation.
- Declaration-site checklist: HIGH — built from direct `Read`/`grep` of every file in this repo, exhaustive by construction (all four workflow files fully read, `pyproject.toml` and `tox.ini` fully read).
- Builder-registration compatibility: HIGH — proven live with a working smoke script and a working full build against the current stack; the only remaining unknown is whether Sphinx 9.1's *actual* runtime behavior (not just its declared floor) introduces any surprise, which the phase's own done-ness gate (re-running these exact commands post-pin-raise) will catch directly.
- Atomicity guidance: HIGH — the failure mode (partial pin raise breaking resolution) was reproduced live, not just described.

**Research date:** 2026-07-09
**Valid until:** 2026-08-08 (30 days — dependency-pin research; re-verify PyPI metadata if execution slips past this window, since Sphinx/docutils/typst all release on independent, sometimes-fast cadences and a newer patch/minor could shift the "latest" recommendation)
