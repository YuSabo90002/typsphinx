# Stack Research

**Domain:** Sphinx extension forward-compat port (typsphinx v0.5.0 — Sphinx 9 + typst 0.15+, latest-only)
**Researched:** 2026-07-09
**Confidence:** MEDIUM (cross-verified against PyPI JSON API + official changelogs + GitHub package registry; one item — the exact origin package of the `kai` compile error — remains LOW/unconfirmed and is flagged as a phase-time verification task, not guessed here)

## Recommended Stack

### Core Technologies (runtime pins to raise)

| Technology | Current pin (v0.4.4) | New latest release | Why this version |
|------------|----------------------|---------------------|-------------------|
| Sphinx | `>=5.0,<9` (resolves ~7-8.x) | **9.1.0** (released 2025-12-31) | Latest Sphinx 9.x. Confirmed via PyPI JSON API (`pypi.org/pypi/Sphinx/9.1.0/json` and the unpinned `/json` endpoint, which shows `9.1.0` as `info.version`). This is the release the milestone targets (FWD-01, latest-only — no compat range). |
| docutils | `>=0.18,<0.22` | **0.22.4** (NOT 0.23) | Sphinx 9.1.0's own `requires_dist` pins `docutils<0.23,>=0.21`, so `docutils==0.23` (released 2026-05-27) is **excluded by Sphinx itself** — installing it alongside Sphinx 9.1 will fail resolution. The newest docutils release actually resolvable with Sphinx 9.1 is the 0.22.x line, latest patch **0.22.4**. This matches the CI failure evidence already on record in PROJECT.md (loose pins resolved `docutils==0.22.4` on the failing run). |
| typst (typst-py) | `>=0.14.1,<0.15` | **0.15.0** (released 2026-06-16) | PyPI package `typst` (messense/typst-py) is a 1:1 Python binding to the Rust `typst` compiler — package version tracks compiler version exactly. `0.15.0` is the only `0.15.x` release on PyPI as of research date (no `0.15.1` patch yet); it wraps typst compiler `0.15.0` (released 2026-06-15, per `github.com/typst/typst/releases/tag/v0.15.0` and the official Typst blog post "Typst 0.15 contains multitudes"). **`typst 0.16` does not exist yet** — do not pre-emptively widen the ceiling for it. |
| Python (floor) | `>=3.10` | **>=3.11 minimum, `>=3.12` recommended** | See the dedicated "Python floor" section below — this is the loudest flag in this research. |

### Bundled `@preview` Typst Universe packages (version-synced across 3 files)

| Package | Current pin (v0.4.4) | Latest published to registry | Recommended new pin | Rationale |
|---------|----------------------|-------------------------------|----------------------|-----------|
| `gentle-clues` | `1.2.0` | **1.3.1** (registry dir list: …, 1.2.0, 1.3.0, 1.3.1 — confirmed via `github.com/typst/packages/tree/main/packages/preview/gentle-clues`) | **`1.3.1`** | Two minor versions ahead of the pinned 1.2.0. The Universe package page states its declared minimum compiler is `typst 0.13.0`, and the 1.3.0 GitHub release note explicitly says "update to typst 0.13" — i.e. this is the version line that was updated *for* newer typst compilers after 1.2.0. Given PROJECT.md's own suspicion that `kai` originates from `gentle-clues:1.2.0` (an un-updated old pin), this is the single highest-priority bump candidate to verify first. |
| `codly` | `1.3.0` | **1.3.0** (same — registry dir list tops out at 1.3.0; a `v1.3.1` GitHub *tag* exists on `Dherse/codly` but has **not** been published to the `@preview` registry as of research date) | **`1.3.0`** (no registry bump available) | typsphinx is already pinned to codly's registry ceiling — there is nothing newer to move to. A known open upstream issue (`Dherse/codly#131`, opened 2026-06-17: "Text is vertically off-center with highlight(s) in Typst 0.15.0") confirms codly has *some* typst-0.15 rendering friction, but it is a cosmetic misalignment, not a compile-breaking error, and no "kai"/unknown-variable report exists against codly. **If `kai` persists after bumping gentle-clues/mitex/codly-languages, codly is the remaining suspect and has no newer registry release to fall back on** — flag for phase-time empirical bisection (see Pitfalls/PITFALLS.md). |
| `codly-languages` | `0.1.1` | **0.1.10** (registry dir list: 0.1.0 … 0.1.10, confirmed via `github.com/typst/packages/tree/main/packages/preview/codly-languages`) | **`0.1.10`** | Nine patch releases ahead of the pinned 0.1.1 — the largest version gap of the four bundled packages. This is a plain data package (language name → icon/color mappings) with no typst-version-gating info published, but its sheer staleness relative to registry HEAD makes it a strong second candidate for whatever the `kai` incompatibility turns out to be. |
| `mitex` | `0.2.4` | **0.2.7** (registry dir list: 0.1.0 … 0.2.7, confirmed via `github.com/typst/packages/tree/main/packages/preview/mitex` and `mitex-rs/mitex` GitHub releases) | **`0.2.7`** | Three patch versions ahead. The `0.2.6` GitHub release note explicitly says it "addressed a deprecation warning for Typst v0.14.0" — i.e. mitex is the one package with a documented history of chasing compiler deprecations, making it plausible it also needs the 0.2.7 bump to compile cleanly under 0.15. |

**Update all three version-sync sites in lockstep** (per CLAUDE.md's documented hazard): `typsphinx/writer.py` (lines ~94-97), `typsphinx/template_engine.py` (lines ~313-316), `typsphinx/templates/base.typ` (lines 8-19). `tests/test_preview_version_sync.py` will fail CI if any one of the three drifts from the others — treat that test as the acceptance gate for this bump, not just a lint nicety.

## Python Floor — LOUD FLAG

**Sphinx 9 forces the Python floor up, and it forces it up *twice within the 9.x line itself*:**

- **Sphinx 9.0.0** (2025-11-30): PyPI `requires_python = ">=3.11"` (confirmed via `pypi.org/pypi/Sphinx/9.0.0/json`).
- **Sphinx 9.1.0** (2025-12-31, the current latest): PyPI `requires_python = ">=3.12"` (confirmed via `pypi.org/pypi/Sphinx/9.1.0/json` and the unpinned `Sphinx/json` endpoint). Classifiers list only `3.12, 3.13, 3.14, 3.15` — **3.11 support was dropped one point-release after being added in 9.0.0.**

This is a hard blocker, not a nice-to-have: **typsphinx's current floor of Python 3.10 (and even 3.11) cannot install Sphinx 9.1.0.** Because the milestone is explicitly latest-only (target Sphinx 9.1.0, not 9.0.0), typsphinx's `requires-python` must rise from `>=3.10` to **`>=3.12`**, dropping both Python 3.10 and 3.11 from the supported/tested matrix (currently 3.10–3.13; would become 3.12–3.13, or 3.12–3.14 if adding the newest interpreter is in scope — that decision belongs to the roadmap, not this research).

Consequences to carry into requirements/roadmap:
- `pyproject.toml`: `requires-python = ">=3.12"`, drop the `3.10`/`3.11` classifiers, add nothing new unless 3.14 support is separately decided.
- `tox.ini` `env_list`: drop `py310`, `py311`.
- CI matrix (`ci.yml`): drop the 3.10 and 3.11 lanes (6 of the current 12 matrix jobs, 2 Python versions × 3 OSes) — required-status-check list on `main` branch protection will need the same PATCH-based cleanup Phase 4 already did for the 3.9 straggler (see PROJECT.md Key Decisions).
- `black`/`ruff` `target-version`: `py310` → `py312`.
- `mypy` `python_version`: `"3.10"` → `"3.12"`.
- `docs` extra's `tomli>=2.0; python_version < '3.11'` shim becomes dead weight once the floor is 3.12 (stdlib `tomllib` covers 3.11+) — can be dropped, though leaving it is harmless.

**If the roadmap prefers a softer landing**, pinning to `sphinx>=9.0,<9.1` instead of `>=9,<10` would only require a `>=3.11` floor (drop 3.10 only, keep 3.11). This contradicts "latest-only" as currently scoped in PROJECT.md, so it is flagged here as an option, not a recommendation — the default recommendation is Python `>=3.12` + Sphinx `9.1.0`/`>=9.1,<10`.

### Supporting Libraries

No new supporting libraries are needed for this milestone — it is a pin-and-fix port, not a features milestone. `sphinxcontrib-*`, `Jinja2`, `Pygments`, `babel`, `alabaster`, `imagesize`, `requests`, `roman-numerals`, `packaging`, `snowballstemmer`, `colorama` are all *transitive* Sphinx 9.1.0 dependencies (per its `requires_dist`) — typsphinx does not declare them directly and shouldn't start now; `uv sync` / `uv lock` will resolve them automatically once the `sphinx` pin is raised.

### Development Tools

| Tool | Current guard ceiling (v0.4.4) | Needs bumping for Sphinx 9 / Python 3.12 floor? | Notes |
|------|----------------------------------|--------------------------------------------------|-------|
| pytest | `>=8.4,<10` | **No** | Already supports 3.12/3.13 fine; ceiling has headroom (pytest 9.x already in range). |
| mypy | `>=1.13,<3.0` | **No** (config change only) | Version ceiling is fine; only `python_version = "3.12"` in `[tool.mypy]` needs updating, not the pip/uv version range. |
| black | `>=26,<27` | **No** (config change only) | Ceiling fine; only `target-version` list changes. |
| ruff | `>=0.15,<0.16` | **No** (config change only) | Ceiling fine; only `target-version = "py312"` changes. |
| tox / tox-uv | `>=4.56,<5` / `~=1.35` | **No** | Unaffected by Sphinx/Python floor change; `env_list` content changes (drop py310/py311) but the tool versions themselves don't need bumping. |
| types-docutils | `>=0.18` (pyproject `dev`) / `>=0.22.2.20251006` (`[dependency-groups] dev`) | **Yes, floor** | Should track the new docutils floor — bump the pyproject `dev` extra's `types-docutils>=0.18` up to something like `>=0.22` to match the runtime docutils pin; the `[dependency-groups]` entry is already ahead of this. |

**Conclusion: no dev-tooling *version ceiling* needs raising for this milestone.** The Phase 4 (v0.4.4) dev-tooling modernization already landed ceilings with headroom for 3.12+. What changes is *target-version configuration* inside those already-adequate tools (`black`/`ruff`/`mypy` python-version knobs), plus dropping dead CI lanes — not new floors/ceilings in `pyproject.toml`'s dependency specifiers.

## Installation

```bash
# Runtime — raise pins in pyproject.toml [project.dependencies]
# sphinx>=9.1,<10
# docutils>=0.21,<0.23     (Sphinx 9.1's own docutils<0.23 ceiling — do NOT try to allow docutils 0.23)
# typst>=0.15.0,<0.16      (no 0.16 exists yet; ceiling guards against a future breaking major)

uv lock          # regenerate uv.lock against the new pins
uv sync --locked # reproducible install matching lockfile
```

```bash
# Bundled @preview packages — NOT pip-installable; update the three version-sync
# sites directly (writer.py, template_engine.py, templates/base.typ):
#   @preview/gentle-clues:1.3.1     (was 1.2.0)
#   @preview/codly:1.3.0            (unchanged — already at registry ceiling)
#   @preview/codly-languages:0.1.10 (was 0.1.1)
#   @preview/mitex:0.2.7            (was 0.2.4)
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|--------------------------|
| `sphinx>=9.1,<10` (latest, Python floor 3.12) | `sphinx>=9.0,<9.1` (Python floor 3.11) | If dropping Python 3.11 support (in addition to 3.10) is judged too disruptive for typsphinx's user base — trades "latest-only" purity for one extra supported Python minor. Explicitly out of scope per PROJECT.md's "latest-only" decision, but documented here since the floor jump is unusually steep for a single major version. |
| Bump all four `@preview` packages to registry-latest in one shot | Bisect one package at a time, re-running `docs-pdf` after each bump | If CI time/iteration cost matters more than diagnostic clarity, the "bump everything, test once" approach is faster. Recommended alternative (bisect) if the `kai` error *doesn't* disappear after bumping all four — see Pitfalls. |
| `docutils>=0.21,<0.23` | `docutils==0.22.4` (exact pin) | If reproducibility is prioritized over Dependabot being able to pick up 0.22.x patch releases automatically within the range; an exact pin trades flexibility for zero-surprise builds. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|--------------|
| `docutils>=0.22,<0.24` or an unbounded `docutils>=0.22` | Sphinx 9.1.0 itself constrains to `docutils<0.23,>=0.21` — a wider typsphinx ceiling doesn't help and could mislead a reader into thinking 0.23 is viable; it will never resolve because Sphinx blocks it. | `docutils>=0.21,<0.23` (mirrors Sphinx's own constraint) |
| `typst>=0.15,<1.0` or unbounded `typst>=0.15` | No `typst 0.16` exists yet (verified: PyPI's `typst` package release list tops out at `0.15.0`; no `typst/typst` GitHub release beyond `v0.15.0` as of research date). An overly wide ceiling would silently absorb a future `0.16` compiler bump — which is exactly the kind of unpinned-drift failure mode this whole milestone (and the durability guardrails from the prior milestone) exists to prevent. | `typst>=0.15.0,<0.16` — tight ceiling, let Dependabot/`drift.yml` file an issue when 0.16 lands so it gets a deliberate, tested bump. |
| Keeping `requires-python = ">=3.10"` while adopting `sphinx>=9.1` | Will fail to resolve entirely — Sphinx 9.1.0 hard-requires Python >=3.12; `uv lock` will error immediately. | `requires-python = ">=3.12"` |
| Assuming `codly:1.3.0` needs a version bump to fix `kai` | It is already at the registry ceiling — there is no newer `codly` release to pin to. Time spent "looking for a newer codly" is time wasted. | Bump the other three packages first; if `kai` persists, treat codly itself as a suspect requiring source-level investigation (patched fork, `#show`-based workaround, or an upstream issue filed against `Dherse/codly`) rather than a routine version bump — this is exactly the kind of finding that belongs in a phase-specific research flag, not resolved here. |

## Stack Patterns by Variant

**If the roadmap wants to de-risk the Python-floor jump:**
- Land the `sphinx>=9.1,<10` + `requires-python>=3.12` bump and the `@preview` package bumps as two *separate* phases/PRs (matches this milestone's existing phase-per-concern pattern from v0.4.4: pin phase, then CI-green phase, then Python-modernization phase, then dev-tooling phase, then durability phase).
- Because CI is currently green on 3.10-3.13 + typst 0.14.9, dropping 3.10/3.11 lanes should happen in the *same* PR that raises the Sphinx pin (they're causally linked — you cannot install Sphinx 9.1 on 3.10/3.11 to test it), not as an afterthought.

**If `kai` is not resolved by the four package bumps:**
- Bisect: revert to the old pin for gentle-clues/codly-languages/mitex one at a time (keep the other two bumped) and rerun `tox -e docs-pdf` locally with `typst==0.15.0` forced, to isolate which single package still emits `kai`. This is exactly the kind of investigation PROJECT.md already flagged as unresolved ("kai origin ... likely gentle-clues:1.2.0 or codly") — this research narrows the field (codly has no newer release to try; gentle-clues and codly-languages are the biggest version-gap suspects) but cannot fully resolve it without an actual typst-0.15 compile attempt, which is implementation-phase work, not research-phase work.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|------------------|-------|
| `sphinx==9.1.0` | `docutils>=0.21,<0.23` | Hard constraint from Sphinx's own `requires_dist`; do not widen typsphinx's docutils ceiling past this. |
| `sphinx==9.1.0` | `python>=3.12` | Hard constraint from Sphinx's own `requires_python`; this is the floor-forcing fact of this milestone. |
| `sphinx==9.0.0` (not recommended, listed for context) | `python>=3.11` | One point-release looser than 9.1.0 — only relevant if the roadmap chooses the softer-landing alternative above. |
| `typst==0.15.0` (PyPI) | typst compiler `0.15.0` | 1:1 version tracking; the PyPI package IS the compiler binding, no separate "compiler version" to reconcile. |
| `@preview/gentle-clues:1.3.1` | declared min typst `0.13.0` | Declared minimum is not the same as "verified working on 0.15" — treat as necessary-but-not-sufficient; verify by actually compiling `docs-pdf` in the implementation phase. |
| `@preview/codly:1.3.0` | declared min typst `0.12.0`; known open issue on 0.15.0 rendering (`Dherse/codly#131`, cosmetic only) | No newer registry release exists to address 0.15-specific issues; if a compile-blocking (not just cosmetic) issue is found, it will require a workaround or upstream fix, not a version bump. |

## Sources

- `pypi.org/pypi/Sphinx/9.1.0/json` (PyPI JSON API — official registry data) — `requires_python`, `requires_dist`, upload date. MEDIUM/verified confidence.
- `pypi.org/pypi/Sphinx/9.0.0/json` — cross-check of the 9.0.0→9.1.0 Python-floor jump (3.11→3.12). MEDIUM/verified confidence.
- `pypi.org/pypi/Sphinx/json` (unpinned, latest) — confirms 9.1.0 is current latest as of research date. MEDIUM/verified confidence.
- `raw.githubusercontent.com/sphinx-doc/sphinx/master/pyproject.toml` — cross-check of `requires-python` against PyPI metadata (master/dev branch shows `>=3.12` consistent with the 9.1.0 release). MEDIUM/verified confidence.
- `www.sphinx-doc.org/en/master/changes/9.0.html` — official Sphinx 9.0 changelog; confirms "Support Docutils 0.22" and lists autodoc-rewrite / builder API breaking changes relevant to translator/writer code. MEDIUM confidence.
- `pypi.org/pypi/docutils/json` — PyPI JSON API; confirms latest overall (0.23, 2026-05-27) and the full 0.22.x patch list (0.22.4 latest in that line). MEDIUM/verified confidence.
- `pypi.org/pypi/typst/json` — PyPI JSON API; confirms `typst` package latest is `0.15.0`, no `0.15.x` patches or `0.16` yet, `requires_python>=3.8`. MEDIUM/verified confidence.
- `github.com/typst/typst/releases/tag/v0.15.0` and `typst.app/blog/2026/typst-0.15/` — official typst 0.15.0 compiler release (2026-06-15) and its blog post enumerating breaking changes (removed deprecated stdlib symbols, variable-font naming, HTML export changes, CSL/citation-style renames). MEDIUM confidence.
- `github.com/typst/packages/tree/main/packages/preview/{gentle-clues,codly,codly-languages,mitex}` — ground-truth registry version-directory listings (authoritative for "what's actually installable via `@preview/x:version`", more reliable than the Typst Universe web page which showed some staleness/drift against GitHub tags during this research). MEDIUM confidence.
- `typst.app/universe/package/{gentle-clues,codly,codly-languages,mitex}/` — Typst Universe package pages; used for declared minimum-typst-version metadata. LOW-MEDIUM confidence (one instance of drift observed vs. the GitHub registry directory listing for `codly`, where Universe under-reported relative to `Dherse/codly`'s own GitHub release tags — registry directory listing was treated as ground truth where the two disagreed).
- `github.com/Dherse/codly/releases` and `github.com/Dherse/codly/issues` — confirms `codly` has no registry-published version beyond 1.3.0, and one open (non-fatal, cosmetic) typst-0.15.0 rendering issue (#131). MEDIUM confidence.
- `github.com/jomaway/typst-gentle-clues/releases`, `.../issues` and `github.com/mitex-rs/mitex/releases` — release/issue history for the other two bundled packages; no direct "kai" hits found in any upstream issue tracker searched. LOW confidence on the "kai origin" question specifically — **this is an open gap, not resolved by this research**, and should be treated as a phase-time empirical-verification task (compile `docs-pdf` under typst 0.15.0 with each bumped package and observe).

---
*Stack research for: typsphinx v0.5.0 forward-ecosystem milestone (Sphinx 9 + typst 0.15+, latest-only)*
*Researched: 2026-07-09*
