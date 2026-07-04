# Stack Research

**Domain:** CI dependency-pinning / compatibility repair for a Sphinx→Typst PDF extension
**Researched:** 2026-07-04
**Confidence:** MEDIUM-HIGH overall (root cause of the `kai` break is HIGH confidence; a few specific patch pins are flagged LOW/MEDIUM pending empirical CI confirmation — see per-item notes)

This is not a greenfield stack survey. It answers one question: **what exact, mutually-compatible version pins turn the currently-red CI green**, given the decision already locked in `PROJECT.md` (pin backward to known-good; do not port to sphinx 9 / typst 0.15).

## Recommended Stack

### Core pins (the fix)

| Technology | Version constraint (pyproject.toml) | Target lock (uv.lock) | Why |
|------------|--------------------------------------|------------------------|-----|
| `typst` (typst-py) | `>=0.14.1,<0.15` | `typst==0.14.9` | typst-py version numbers are 1:1 with the Rust `typst` compiler they wrap (confirmed via PyPI release cadence — `typst` 0.14.0 → 0.14.9 released 2025-10-29 → 2026-05-14, then `0.15.0` on 2026-06-16). Root cause: `mitex`'s CHANGELOG documents a fix titled **"fix 'kai is deprecated' warning for Typst v0.14.0"**, landed in mitex `0.2.6`. The bundled/hardcoded `mitex:0.2.4` predates that fix, so under typst 0.14.x it only emits a **deprecation warning** for the `kai` symbol — but under typst 0.15.0, Typst's normal deprecate-then-remove policy turns that same symbol into a **hard error**, exactly matching the observed `TypstError: unknown variable: kai`. Reverting the compiler to the 0.14.x line restores the warn-not-error behavior without touching any of the four pinned `@preview` packages. **Confidence: HIGH** on root cause (direct changelog match, cross-checked via two independent searches); **MEDIUM** on `0.14.9` specifically vs. `0.14.1` (no patch-by-patch regression testing found for 0.14.2–0.14.9 against this exact `@preview` combo — empirically confirm in CI before locking to the exact patch). |
| `sphinx` | `>=5.0,<9` | resolves to `8.1.3` on Py3.10 CI legs, `8.3.0` on Py3.11–3.13 legs (see Python note below) | Excludes `sphinx==9.x` (the version that resolved in the failing CI run). **Important honesty note:** the failure evidence in `PROJECT.md` traces *every* PDF/matrix failure to the `typst.TypstError: unknown variable: kai` cascade — none of the observed failures are a confirmed Sphinx-9-specific API break. The ceiling here is therefore a **defensive/reproducibility measure per the project's own Key Decision** ("pin known-good, don't port forward"), not a proven-necessary fix. **Confidence: HIGH** that `<9` is a safe, currently-installable ceiling; **MEDIUM** that sphinx 9 itself would have caused failures beyond the typst issue (untested — flag for empirical confirmation: try pinning only `typst<0.15` first, see if sphinx 9 also passes, before deciding whether the sphinx ceiling is load-bearing or just precautionary). |
| `docutils` | `>=0.18,<0.22` | resolves to `0.21.2` (last pre-0.22 release, 2024-04-23) | Sphinx itself already constrains `docutils<0.22,>=0.20` as of 8.0–8.3 (verified via each release's PyPI metadata), so this ceiling is redundant-but-explicit: it makes the intent visible in `typsphinx`'s own `pyproject.toml` rather than relying silently on Sphinx's transitive constraint, and it protects against a future Sphinx patch loosening that bound. **Confidence: HIGH** (directly read from Sphinx 8.0.0/8.1.0/8.3.0 `requires_dist` metadata via PyPI JSON API). |

**Do NOT** bump the hardcoded `@preview` package versions (`codly:1.3.0`, `codly-languages:0.1.1`, `mitex:0.2.4`, `gentle-clues:1.2.0`) in this cycle — that would be "porting forward," which `PROJECT.md` explicitly puts out of scope. The typst compiler pin above is the complete fix for the `kai` break; no changes to `writer.py`, `template_engine.py`, or `templates/base.typ` are required.

### Supporting/rejected alternative (documented, not chosen)

| Option | Why not chosen this cycle |
|--------|---------------------------|
| Bump `mitex` to `>=0.2.6` (which contains the `kai` fix) and keep `typst>=0.15` | This is the "port forward" path the project explicitly deferred. It only fixes the one known symbol (`kai`); `codly`, `codly-languages`, and `gentle-clues` have not been verified against typst 0.15 at all (codly 1.3.0's declared minimum is typst 0.12.0 — no confirmed ceiling), so this path reopens the exact configurability/compatibility-matrix tech debt already logged in `CONCERNS.md`. Revisit in a future "support typst 0.15" milestone. |

### Python range modernization

| Setting | Value | Why |
|---------|-------|-----|
| `requires-python` | `>=3.10` | Drops EOL Python 3.9 (EOL Oct 2025) per `PROJECT.md`. No explicit `<3.14` ceiling needed — nothing in the dependency graph blocks 3.13, and an artificial ceiling would just have to be revisited again for 3.14. |
| `[tool.black] target-version` | `["py310", "py311", "py312", "py313"]` | Matches the new floor/ceiling of the supported matrix; drop `"py39"`. |
| `[tool.ruff] target-version` | `"py310"` | Ruff's `target-version` should track the **minimum** supported Python (it gates which syntax Ruff assumes is available), same convention already in use (`"py39"` today). |
| `[tool.mypy] python_version` | `"3.10"` | Same reasoning as Ruff — mypy's `python_version` sets the minimum syntax/stdlib surface being type-checked against. |
| Ruff `ignore` list | Re-review `UP035`, `UP006`, `UP028` (currently ignored "for Python 3.9+ support") | These were suppressing `typing.Dict`/`typing.List` → `dict`/`list` modernization rules specifically because 3.9 was supported. With the floor now 3.10 (or later), these can likely stay ignored for compatibility with 3.10 itself (3.10 still benefits from `from __future__ import annotations` either way), but flag for a pass during execution: nothing forces removing them, but they're no longer a Python-3.9 requirement — a maintainer call, not a compatibility blocker. **Confidence: MEDIUM** — not verified against actual codebase usage patterns. |

**Python 3.13 blockers found:** none in the core runtime path.
- `typst` (typst-py) ships `cp38-abi3` wheels (stable ABI) plus dedicated `cp314`/`cp314t` builds — confirmed via PyPI file listing for `typst==0.14.9` and `0.15.0` — so 3.10–3.13 (and even 3.14) are covered by the same wheel.
- `sphinx` 8.0–8.3 classifiers explicitly list Python 3.10–3.13 (8.2+ lists 3.10→3.13→3.14; note 8.2.0 *raised* its own floor to `>=3.11`, see interaction note below).
- `docutils` is pure Python; no wheel/version blocker.

**One real risk found — unused dead dependency:** `sphinx-testing>=1.0` is declared in `dev` extras but **is not imported anywhere in `tests/`** (verified via repo-wide grep — zero matches). Its last PyPI release was `1.0.1` in 2019, it declares no `requires_python` metadata at all, and it predates Sphinx 5+ entirely (it's a legacy helper superseded by Sphinx's own bundled `sphinx.testing` pytest fixtures, which this project's test suite already relies on implicitly via `sphinx-testing`-adjacent conventions or plain pytest). **Recommendation: remove `sphinx-testing` from `dev` extras entirely** rather than "modernize" it — there is nothing to modernize; it's inert weight that only adds an unmaintained transitive dependency to the resolution graph. **Confidence: HIGH** (directly verified by grep — zero usages in the test suite).

### Sphinx-version/Python-version interaction (uv.lock nuance — flag for empirical confirmation)

Sphinx's own `requires-python` floor changed *mid-8.x-series*:
- Sphinx `8.0.0`/`8.1.x` → `requires_python: >=3.10`
- Sphinx `8.2.0` onward → `requires_python: >=3.11` (raised the floor, dropped 3.10)

With `sphinx>=5.0,<9` and the new project floor `requires-python>=3.10`, this means the **effective installed Sphinx version differs by Python minor version**:
- On the Python **3.10** CI leg → resolver can only pick `sphinx<=8.1.3`.
- On Python **3.11–3.13** legs → resolver can pick up to `sphinx==8.3.0` (latest 8.x).

This is standard PEP 508 environment-marker resolution and `uv`'s universal lock format is designed to handle exactly this (different pinned versions of the same package per Python-version marker within one `uv.lock`). It is *not* a blocker, but it does mean the 3.10 CI leg exercises a slightly older Sphinx than 3.11+ legs — worth a one-line note in the CI/test docs so a future contributor doesn't mistake it for drift. **Confidence: MEDIUM** — the marker-resolution mechanism is well-established uv/pip behavior, but the actual `uv lock` regeneration against this repo's dependency graph has not been run/observed in this research pass; **empirically confirm during planning/execution** that `uv lock` produces the expected per-marker split cleanly (no unsolvable conflict) before treating the pins as final.

## Installation

```bash
# pyproject.toml dependency changes
dependencies = [
    "sphinx>=5.0,<9",
    "docutils>=0.18,<0.22",
    "typst>=0.14.1,<0.15",
]

# regenerate the lockfile after editing pyproject.toml
uv lock

# sanity-check the resolved versions actually landed in range
uv pip list | grep -E "^(sphinx|docutils|typst) "
```

```bash
# dev extras: drop the dead dependency
# (remove this line from [project.optional-dependencies].dev)
- "sphinx-testing>=1.0",
```

## Alternatives Considered

| Recommended | Alternative | When to use the alternative |
|--------------|-------------|------------------------------|
| Pin `typst<0.15`, keep `@preview` versions as-is | Bump `mitex>=0.2.6` and support `typst>=0.15` | Once a future milestone commits to porting forward (i.e., building/maintaining a compatibility matrix across `codly`, `codly-languages`, `gentle-clues` for typst 0.15+); out of scope now per `PROJECT.md`. |
| `sphinx>=5.0,<9` (loose within 5–8.x) | `sphinx>=7.0,<9` or `sphinx>=8.0,<9` (tighter floor) | If CI stability under the wide 5–8.x range proves flaky in practice (e.g., an old edge case in 5.x/6.x that nobody has exercised in years), tightening the floor to `>=7.0` or `>=8.0` reduces the resolution matrix without reopening the typst-0.15 question. This is a low-risk follow-up, not required for the `kai` fix itself. |
| `typst==0.14.9` target in lockfile | `typst==0.14.1` exact pin (the previously-declared floor) | If `0.14.2`–`0.14.9` patch releases turn out to have their own regression against this exact `@preview` combo (unverified — see confidence note above), fall back to the last version known to have worked historically, `0.14.1`, and re-widen later once verified. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `typst>=0.15` (or unconstrained `typst>=0.14.1` as currently declared) | Resolves to `0.15.0`, which hard-errors on the `kai` symbol still present in pinned `mitex:0.2.4` (and possibly other pinned `@preview` packages not yet audited against 0.15) | `typst>=0.14.1,<0.15` |
| Unconstrained `sphinx>=5.0` / `docutils>=0.18` (current state) | Resolves to `sphinx==9.0.4` / `docutils==0.22.4` in fresh CI runs — the exact combination the project decided to move away from this cycle | `sphinx>=5.0,<9`, `docutils>=0.18,<0.22` |
| `sphinx-testing>=1.0` in dev deps | Dead since 2019, zero usages in the test suite, no Python-version metadata at all — pure risk with no benefit | Remove it; rely on Sphinx's own bundled test fixtures (`sphinx.testing`) which the suite already effectively uses |
| Jumping dev tooling straight to today's latest majors (`pytest==9.x`, `mypy==2.x`) without review | Both ship default-behavior changes that can turn previously-passing runs red: pytest 9 promotes `PytestRemovedIn9Warning` to a hard error by default (escape hatch: `filterwarnings = ignore::pytest.PytestRemovedIn9Warning`, only usable through the 9.0.x series); mypy 2.0 flips `--local-partial-types` and `--strict-bytes` on by default, which can surface new type errors in previously-clean code | Bump floors conservatively (see Dev Tooling table) and treat the very latest majors as a follow-up, not part of this CI-repair pass, unless verified clean against this codebase first |

## Dev Tooling Versions (current stable, as of 2026-07-04)

| Tool | Current latest stable | Recommended floor for this cycle | Notes |
|------|------------------------|-----------------------------------|-------|
| `black` | `26.5.1` | `black>=24.0` (keep unpinned-but-recent; the failing CI's 3 reformatted files are a formatting-drift symptom of an unconstrained floor picking up a newer yearly style — not a bug to "fix" beyond running `black` once to reformat and committing the result) | Confirmed via PyPI release list. Run `black .` locally after bumping `target-version` and commit the reformatted files as part of this milestone; do not fight the formatter. **Confidence: HIGH** (direct PyPI data). |
| `ruff` | `0.15.20` | `ruff>=0.8` | Confirmed via PyPI. Ruff has had no major-version-style breaking-change cadence comparable to mypy/pytest; safe to move the floor up meaningfully. **Confidence: MEDIUM** (version confirmed HIGH; breaking-change absence is a general characterization, not exhaustively verified against every 0.x release note). |
| `mypy` | `2.1.0` | `mypy>=1.13,<2.0` (stay on the 1.x line this cycle) | mypy 2.0 flips several defaults (`--local-partial-types`, `--strict-bytes` on by default; `--allow-redefinition-new` renamed) that can surface new errors in code that passed under 1.x. Given the current `[tool.mypy]` config already disables several strictness knobs (`check_untyped_defs = false`, etc.), staying on 1.x avoids re-litigating type-check debt in a CI-repair cycle. Revisit 2.x as a deliberate follow-up. **Confidence: MEDIUM** (breaking-change list confirmed via search of mypy's own docs/changelog references, not independently reproduced against this codebase). |
| `pytest` | `9.1.1` | `pytest>=7.0,<9` (stay on the 8.x line: target `~8.4`) | pytest 9.0 promotes previously-soft deprecation warnings to hard errors by default and drops Python 3.9 (irrelevant now that 3.9 is dropped anyway) — but the warning-to-error flip is the real risk for a ~400-test suite that hasn't been audited against it. Land on 8.x (`8.4.x`) this cycle; treat 9.x as a follow-up with its own verification pass. **Confidence: MEDIUM** (release notes confirmed via search; not reproduced against this suite). |
| `tox` / `tox-uv` | `tox 4.56.x` | `tox>=4.6` (bump floor from the currently very loose `>=4.0`) | Still 4.x line, no major-version jump found; safe to bump the floor for reproducibility without behavior risk. **Confidence: MEDIUM** (latest-version query only; did not diff every 4.x release). |
| `actions/checkout` | `v6` | Bump from whatever is currently pinned (check `.github/workflows/*.yml`) to `v6` | **Confidence: LOW-MEDIUM** — confirmed via web search convergence, not read directly from the GitHub Marketplace API; verify current pin and changelog compatibility during execution. |
| `actions/setup-python` | `v6` | Bump to `v6` | Same caveat as above — **Confidence: LOW-MEDIUM**, verify during execution against the actual `.github/workflows/*.yml` pins and any breaking notes in the v6 release. |
| `codecov/codecov-action` | `v6.0.0` (v6 requires Node 24 on the runner) | Bump to latest `v5.x` (`5.5.x`) rather than jumping to `v6` unless the CI runner image is confirmed to ship Node 24 | **Confidence: MEDIUM** — v6's Node 24 requirement is a concrete, sourced constraint; verify GitHub-hosted runner Node version before adopting v6, otherwise stay on `v5.5.x`. |

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|------------------|-------|
| `typst==0.14.1`–`0.14.9` | `mitex:0.2.4`, `codly:1.3.0`, `codly-languages:0.1.1`, `gentle-clues:1.2.0` (all as currently hardcoded) | `kai` symbol only warns (not errors) in this line; this is the known-good combination the project ran on historically. |
| `typst==0.15.0` | **NOT** compatible with `mitex:0.2.4` | Confirmed root cause of `TypstError: unknown variable: kai`; would require `mitex>=0.2.6` at minimum, and the other three `@preview` packages are unverified against 0.15 — do not pursue this cycle. |
| `sphinx>=8.0,<8.2` | Python `>=3.10` | Needed on the Python 3.10 CI leg specifically; `sphinx>=8.2` raises its own floor to Python `>=3.11` and will simply not resolve on a 3.10 interpreter (handled automatically by environment markers, not a manual per-leg pin). |
| `sphinx>=8.0,<9` | `docutils>=0.20,<0.22` | Sphinx's own declared constraint (verified against 8.0.0/8.1.0/8.1.3/8.3.0 PyPI metadata); typsphinx's explicit `docutils>=0.18,<0.22` is compatible with and slightly wider than this, so Sphinx's own floor (`>=0.20`) will dominate resolution in practice. |

## Sources

- PyPI JSON API (`https://pypi.org/pypi/<package>/json` and `/<version>/json`), queried directly for `typst`, `sphinx`, `docutils`, `black`, `ruff`, `mypy`, `pytest`, `tox`, `sphinx-testing`, `furo`, `sphinx-intl`, `sphinx-autodoc-typehints` — **HIGH confidence**, primary registry data, release dates and `requires_python`/`requires_dist` metadata read directly.
- `mitex-rs/mitex` `CHANGELOG.md` (GitHub, fetched via WebFetch) — the `"fix 'kai is deprecated' warning for Typst v0.14.0"` entry in `mitex 0.2.6` — **MEDIUM confidence** (single primary source, cross-checked against the independently-observed CI symptom, which is a strong corroboration, but the exact `0.14.0`→`0.15.0` transition-to-hard-error was inferred from Typst's general deprecation policy, not an explicit mitex/typst statement).
- Typst Universe package pages (`gentle-clues`, `codly`, `codly-languages`, `mitex`) via WebSearch/WebFetch — **LOW-MEDIUM confidence** per item (single-source, not cross-verified); used only to establish declared minimum-compiler versions, not to rule out 0.15 compatibility.
- GitHub Actions marketplace/release info for `actions/checkout`, `actions/setup-python`, `codecov/codecov-action` via WebSearch — **LOW-MEDIUM confidence**; verify exact current pins in `.github/workflows/*.yml` and re-check release notes during execution.
- Repo-local verification: `grep -rn "sphinx_testing" tests/` (zero matches) — **HIGH confidence**, directly executed against this codebase.
- `.planning/PROJECT.md`, `.planning/codebase/STACK.md`, `.planning/codebase/CONCERNS.md`, `pyproject.toml`, `typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ` — read directly, establish current pinned/hardcoded state this research modifies.

---
*Stack research for: typsphinx CI dependency-compatibility repair*
*Researched: 2026-07-04*
