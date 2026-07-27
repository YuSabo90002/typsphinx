# Project Research Summary

**Project:** typsphinx
**Domain:** Documentation-hosting-platform migration (GitHub Pages -> Read the Docs) for a Sphinx extension that dogfoods its own `typstpdf` builder
**Researched:** 2026-07-25
**Confidence:** HIGH overall, with two explicitly UNVERIFIED empirical unknowns that only a real RTD build can resolve

## Executive Summary

This milestone replaces a hand-rolled GitHub Pages + custom-multilang publishing pipeline with Read the Docs (RTD), a vendor platform that provides version/language flyouts, server-side search, PR previews, and "Edit on GitHub" links for free once a `.readthedocs.yaml` and two linked RTD projects (`en` parent + `ja` translation) exist. The repo-side footprint is small and well-understood: one new file (`.readthedocs.yaml` using RTD's native `python.install: method: uv` plus a `build.jobs.build.pdf` override so `typstpdf` -- not RTD's own LaTeX pipeline -- produces the downloadable PDF), a one-line `conf.py` env-var seam (`READTHEDOCS_LANGUAGE` layered in front of the existing `SPHINX_LANGUAGE`), and a defined deletion set (the ~180-line `build_multilang.py`, its tox env, its Makefile targets, its language-switcher template/CSS, plus a `docs/usage.rst`/`docs/installation.rst` orphan pair that carries two collateral test files). All four research agents converged HIGH confidence on RTD's config schema, translation-project mechanics, and the wheel/font situation for `typst-py`; STACK.md's `formats:[pdf]`-plus-override reading is confirmed correct against RTD's docs (a claim PITFALLS.md got backwards and which this summary corrects -- see Key Findings).

The single largest residual risk this migration carries is **not** the one the milestone brief names. The brief calls "does typst-py's wheel run on RTD" the sole technical unknown, but STACK.md/PITFALLS.md jointly settle that at HIGH confidence (verified `manylinux2014_x86_64` wheel on PyPI, verified embedded-fonts feature in typst-py's own `Cargo.toml`). The genuinely open question -- raised only by ARCHITECTURE.md and confirmed by no other agent -- is whether `typst.compile()` can reach `packages.typst.org` from inside RTD's build sandbox at all, since typsphinx's own docs pull in four `@preview` packages (mitex, codly, codly-languages, gentle-clues) that must be fetched over the network on a cold cache. No documentation source states RTD's build-sandbox egress policy. If this network fetch is blocked, the "serve a typstpdf PDF from RTD" decision does not hold -- the fallback is that HTML still ships from RTD (no PDF regression there) and the PDF stays a CI-artifact + GitHub-Release-asset-only deliverable, exactly as it is today, just without an RTD download link.

The recommended approach is to sequence irreversible/manual steps last: prove the `en` RTD project builds green (HTML + PDF, with the real build log inspected -- not just a green checkmark) before creating the `ja` translation project, before deleting the multilang machinery, and -- critically -- before deleting `gh-pages`/GitHub Pages, which this milestone's own locked decision treats as immediate and unredirected (a real, accepted SEO/inbound-link cost). Default Version should be left at `latest` through the whole migration and only flipped to `stable` after the `v0.6.4` tag is pushed and built -- `stable` cannot exist, and RTD's root-URL redirect will otherwise point at nothing, until that tag lands. The linkcheck CI job and the README/pyproject URL-rewrite work need independent verification bars: linkcheck cannot see the files that actually broke (README.md, pyproject.toml), so its green status must never be cited as proof those links are fixed.

## Key Findings

### Recommended Stack

`.readthedocs.yaml` schema v2, `build.os: ubuntu-24.04`, `build.tools.python: "3.13"` (or `"3.12"` -- either is fine), and RTD's native `python.install: method: uv` / `command: sync` / `extras: [docs]` (not `groups:`, which targets PEP 735 `[dependency-groups]` -- this repo's `docs` extra lives under `[project.optional-dependencies]`). No new Python runtime packages are needed anywhere; `sphinx-build -b linkcheck` is a built-in Sphinx builder, configured only via existing `linkcheck_*` conf values (`linkcheck_ignore`, `_retries`, `_timeout`, `_workers`, `_anchors_ignore_for_url`, `_exclude_documents`).

**Core technologies:**
- `.readthedocs.yaml` (schema v2) -- RTD's sole build manifest; mandatory since 2023-09-25, no build without it, no version without it in the tag history.
- `python.install: method: uv` -- RTD-native, installs the project (typsphinx itself, editable via `uv sync`) plus the `docs` extra in one declarative block; supersedes the older manual `asdf`+`uv` `build.jobs` workaround.
- `build.jobs.build.pdf` override running `sphinx-build -b typstpdf docs/source $READTHEDOCS_OUTPUT/pdf/` -- replaces only the PDF step; `html` keeps RTD's own default `sphinx:`-driven build untouched.
- `typst` (typst-py) `>=0.15.0,<0.16` -- unchanged pin; ships a `manylinux2014_x86_64` `cp38-abi3` wheel (confirmed via PyPI JSON metadata), so no Rust/cargo compile happens on RTD's x86_64 Ubuntu image.
- Furo theme -- unchanged; RTD's Addons flyout (version/language switcher, search, downloads, "Edit on GitHub") is theme-independent and requires zero `conf.py` wiring.

### Expected Features

RTD's Addons system (enabled by default on all projects since 2024-10-07) gives, for free and without code: flyout version/language switcher, server-side search, downloadable-PDF listing from `$READTHEDOCS_OUTPUT/pdf/`, and an automatic "view/edit on GitHub" link for GitHub-connected projects. None of these need `conf.py` changes.

**Must have (table stakes):**
- `.readthedocs.yaml` present and valid -- RTD refuses to build without it.
- Working root URL / correct Default Version -- sequenced per Roadmap Implications below (stays `latest` until the v0.6.4 tag exists).
- Flyout version + language switcher, server-side search, "Edit on GitHub" -- all automatic once the project is RTD-connected.

**Should have (differentiators over GitHub Pages):**
- PR preview builds (owner-manual checkbox) + inline visual diff -- additive to, not a replacement for, the existing `docs.yml` PR gate. PDF is never built on PR previews (RTD policy: only HTML on `external`/PR builds) and search is not indexed on them.
- One canonical PDF surfaced two ways (RTD downloads + GitHub Release) instead of only via GitHub Release today.
- `llms.txt`/Markdown content-negotiation for AI agents -- a free side effect, worth a one-line release-notes mention, not a requirement.

**Defer / accepted loss:**
- Browser-language auto-redirect at the root -- `build_multilang.py`'s `navigator.language`-based redirect has no RTD equivalent. A Japanese-browser visitor lands on English and must click through the flyout manually. Record this explicitly as an accepted UX regression, not an oversight.
- RTD's own default LaTeX PDF pipeline, `sphinx-rtd-theme`, the `readthedocs-sphinx-search` extension, RTD Business paid ad removal, and the Subprojects feature (translations use "Translations," not "Subprojects") -- all explicit anti-features for this milestone.

### Architecture Approach

Two parallel, non-overlapping build paths after migration: RTD (triggered by its own GitHub webhook, reading only `.readthedocs.yaml`, responsible for publishing HTML+PDF for both the `en` and `ja` projects) and GitHub Actions' `docs.yml` (reading only `tox.ini`, now purely a CI regression gate + GitHub-Release-asset attacher, no longer a deploy pipeline). RTD bypasses tox entirely -- do not wrap `build.jobs` commands in a `tox -e docs-*` invocation, since RTD's own `python.install` step already provisions an equivalent environment and nesting tox inside it is redundant. `tox -e docs-pdf` remains critical as the PR-blocking regression gate precisely because RTD builds are async and off the merge-blocking critical path -- a red RTD build would otherwise only be discovered hours after merge.

**Major components:**
1. `.readthedocs.yaml` (new) -- RTD's build manifest: Python env, Sphinx config path, PDF-only `build.jobs` override.
2. `docs/source/conf.py`'s `language` seam -- `os.getenv("READTHEDOCS_LANGUAGE", os.getenv("SPHINX_LANGUAGE", "en"))`, built identically by both the `en` and `ja` RTD projects from the same commit.
3. `docs.yml` (`build-docs` job) -- CI-only regression gate: `docs-html` (renamed from `docs-multilang`, no publish target), `docs-pdf` (unchanged fatal-free gate + tag-time Release attachment), plus a new advisory `linkcheck` step.
4. Two RTD projects sharing one repo -- `en` parent (Language=en) and `typsphinx-ja` (Language=ja), linked via the parent's Settings -> Translations page -- each with its own independently-activated version list.

### Critical Pitfalls

1. **Declaring `formats: [pdf]` without a `build.jobs.build.pdf` override** activates RTD's own LaTeX (`-b latex` + `latexmk`) pipeline, which this project has no toolchain for and would silently ship a different, undogfooded PDF. *Resolved fact, not open for debate:* the correct configuration is **both** `formats: [pdf]` **and** the `build.jobs.build.pdf` override together -- RTD's docs state the override *replaces* the default step for that format, it does not run alongside it. (This corrects PITFALLS.md's independent claim that `formats:` should be omitted entirely; STACK.md's reading is the one to build against.)
2. **RTD never installs the project package by default** -- without an explicit `python.install` block, `conf.py`'s `extensions = [..., "typsphinx"]` fails with `ModuleNotFoundError`, or worse, silently resolves a stale PyPI wheel instead of the in-repo commit. Use RTD-native `python.install: method: uv` / `command: sync` / `extras: [docs]`.
3. **`conf.py` keeps reading only `SPHINX_LANGUAGE`** -- RTD never sets that variable; both the `en` and `ja` projects would silently resolve `language` to the `"en"` fallback, and the `ja` project would build green while rendering 100% English with zero visible error. Fix: layer `READTHEDOCS_LANGUAGE` in front of the existing fallback, and separately confirm the `ja` project's RTD Admin Language dropdown is actually set to Japanese (the env var reflects that dropdown, not the project's mere existence).
4. **Translation-project version lists are independent** -- activating `latest`/`stable` on `en` does not activate anything on `ja`; each project needs its own version activation, re-checked specifically after the `v0.6.4` tag lands (`/ja/stable/` must be confirmed to exist and match, not assumed).
5. **A green `sphinx-build -b linkcheck` job proves nothing about the bug it was added to prevent** -- a repo-wide grep found **zero** `github.io` occurrences under `docs/source/`; the dead links that motivated adding linkcheck live entirely in `README.md` and `pyproject.toml`, files linkcheck structurally never scans. Treat linkcheck and the URL-rewrite work as needing separate verification bars; something other than linkcheck (a real HTTP fetch / grep) must cover README/pyproject.

## Un-Researchable Blocker (rank above the wheel/font questions)

typsphinx's own documentation build pulls in four Typst Universe `@preview` packages (mitex, codly, codly-languages, gentle-clues). `typst.compile()` fetches these from `packages.typst.org` on a cold cache. **No documentation source -- from any of the four research agents -- states RTD's build-sandbox outbound network policy.** This is the milestone's actual #1 empirical unknown, ranked above CPU-architecture/wheel-availability (now HIGH confidence, effectively settled) and above font-fallback risk (also now well-understood, see below). If this fetch is blocked mid-build, the `typstpdf`-via-`build.jobs.build.pdf` step fails independent of whether the `typst-py` wheel itself installs correctly. **Fallback if it fails:** HTML still ships from RTD with no regression; the PDF remains exactly what it is today -- a CI-artifact (`tox -e docs-pdf`) plus tag-time GitHub Release asset -- just without an additional RTD download link. This is not a milestone-blocking failure mode, but it must be observed directly in the first real RTD build log (watch for `@preview` package download lines), not assumed resolved by a green build status.

## Settled Technical Questions (do not re-open)

- **Wheel availability:** `typst` 0.15.0 ships `cp38-abi3` `manylinux2014_x86_64` wheels on PyPI (verified via PyPI JSON metadata) against RTD's Ubuntu 20.04/22.04/24.04 x86_64 build images (verified via RTD's dev build-images docs). No Rust/cargo compilation occurs. HIGH confidence.
- **Font risk:** `typst-py`'s `Cargo.toml` enables `typst-kit`'s `embedded-fonts` feature (Libertinus Serif / New Computer Modern set, identical to the Typst CLI) -- no `build.apt_packages` font installs are needed for this project's English-only docs. **But** Typst's font-fallback is silent-by-design (no error, no warning, on a missing/substituted font). Combine these two facts: the mitigation is not "install fonts," it is "a green RTD build proves nothing about glyph correctness" -- the empirical gate for the PDF feature must include downloading the actual RTD-built PDF and visually/textually comparing it against the `docs-pdf` CI baseline (byte/page-count/text-extraction check), not just a build-succeeded status.
- **`formats:` vs. `build.jobs.build.pdf`:** both keys together, as stated above -- this is settled against RTD's own config-file reference wording, not a judgment call.

## Sequencing Amendment to a Locked Decision

The owner locked Default Version = `stable`. This does not need to be reversed, but it must be **sequenced**, not applied at project-creation time: RTD's root-URL redirect always targets whatever Default Version says, even if that version doesn't exist or has no active build yet. `stable` cannot exist until the `v0.6.4` tag is pushed and built (RTD refuses builds on any tag lacking `.readthedocs.yaml`, so no pre-v0.6.4 tag can ever qualify). **Keep Default Version = `latest` through the entire migration and flip it to `stable` only after the `v0.6.4` tag builds green** -- this is a sequencing change to *when* the owner's decision takes effect, not a change to *what* was decided.

## Deletion Blast Radius (file-path level)

Beyond what the milestone brief names, research surfaced two additional dead artifacts and one conflation hazard:

- **Delete together with `build_multilang.py`:** `docs/Makefile`'s `multilang:` and `serve-multilang:` targets (not named in the milestone brief -- found by grep; both are dead the moment the script is gone) and `docs/source/_templates/page.html` (writes a `sessionStorage` key only the old redirect page ever read -- also not in the brief).
- **Delete together with `docs/usage.rst`:** `tests/test_documentation_usage.py` (11 test functions hard-asserting the file's existence -- this is the exact Phase-27 trap that reddened the suite in the prior milestone; delete both files in the same commit).
- **Delete together with `docs/installation.rst`:** `tests/test_documentation_installation.py` (same trap). **Conflation hazard:** `docs/source/installation.rst` is a **different, live, toctree-reachable** file (referenced from `index.rst`, with its own `.po` catalog) -- do not touch it or its translation file. Only the root-level orphan `docs/installation.rst` is in scope.
- **Standard deletions confirmed, no surprises:** `docs/build_multilang.py`, `[testenv:docs-multilang]` in `tox.ini`, `docs/source/_templates/language-switcher.html`, the `html_context`/`html_sidebars` wiring in `conf.py`, `docs/source/_static/custom.css` (its entire content is language-switcher CSS, confirmed by reading the full 41-line file -- this is a full delete, not a trim), and the `gh-pages` remote branch (a separate git-ref-deletion operation, not a repo-file edit).
- **Pre-deletion discipline (repeat of a pattern that has already bitten this project twice -- Phase 27):** run a fresh, repo-wide grep for each target's filename/env-name/identifier immediately before the deletion commit lands, not scoped only to files the requirement text names, and explicitly decide the fate of every collateral test file in the same commit as its subject.

## Behavior Actually Lost (accepted, not an oversight)

Deleting `build_multilang.py` removes the root-page browser-language auto-redirect (`navigator.language`-based JS that sent a Japanese-browser visitor straight to `/ja/`). RTD has no equivalent -- it redirects to a *version*, never auto-detects a visitor's *language*. A `ja`-language visitor landing on the `en` root sees English first and must click through the flyout manually. Record this as an accepted, minor UX regression versus today, not a bug to work around.

## Owner-Manual Work (cannot be automated or tested)

Translation-project setup has **no `.readthedocs.yaml` key at all** -- it is entirely RTD web-UI work by the owner: create the `en` project (import + connect GitHub); create a second, separate project for `ja` (re-import the same repo, set Language=Japanese in that project's own Admin settings -- this is what actually causes RTD to emit `READTHEDOCS_LANGUAGE=ja` at build time, not anything derivable from `conf.py`); link `ja` under the `en` parent's Settings -> Translations page (the step most likely to be missed or done out of order -- creating both projects without linking them leaves two working-but-unswitchable sites); set Default Version = `stable` (after the tag, per above); enable PR builds; set the repo's GitHub "About" Website field. None of these six steps is assertable by any test in this repo -- they must be tracked as explicit manual checklist items with no automated acceptance criterion, and the `ja` project's version activation (`latest`/`stable`) must be independently re-verified after the tag, since translation projects are fully independent and do not inherit the parent's activated-version list.

## Implications for Roadmap

Based on combined research, suggested phase structure (dependency-ordered per ARCHITECTURE.md's Suggested Build Order, cross-checked against PITFALLS.md's irreversibility sequencing):

### Phase 1: RTD build establishment (en parent)
**Rationale:** Everything downstream depends on `.readthedocs.yaml` existing and the `language` seam being correct before any RTD project is created -- the seam must be right on the `ja` project's very first build, not patched after.
**Delivers:** `.readthedocs.yaml` (uv-native install, `build.jobs.build.pdf` override, no HTML override); `conf.py`'s `READTHEDOCS_LANGUAGE`-then-`SPHINX_LANGUAGE`-then-`"en"` fallback chain; a real RTD project created and observed green -- HTML build inspected for the install-step log lines (local checkout, not stale PyPI), PDF build inspected for zero `latexmk`/LaTeX lines and successful `@preview` package resolution, and the downloaded PDF diffed against the `docs-pdf` CI baseline.
**Addresses:** RTD build establishment (per PROJECT.md); the milestone's stated technical unknown (now understood as two layered unknowns -- wheel/font (settled) and `@preview` network egress (open, see above)).
**Avoids:** Pitfalls 1, 2, 8 (formats/pdf collision, missing package install, wheel/font false confidence).

### Phase 2: ja translation project + multilang-machinery removal
**Rationale:** Must happen only after Phase 1 proves the config sound -- no point building `ja` against a broken seam, and no point deleting the old JS-redirect switcher before RTD's flyout replacement is confirmed working, or `ja` docs go dark with nothing replacing them.
**Delivers:** Second RTD project (Language=ja) created and linked as a Translation of the parent; `/ja/latest/` verified to render visibly-Japanese prose (not just "build succeeded"); `build_multilang.py`, its tox env, `docs/Makefile`'s `multilang`/`serve-multilang` targets, `language-switcher.html`, `page.html`, `custom.css`, and the `html_context`/`html_sidebars` wiring all deleted together.
**Uses:** The `language` seam from Phase 1; RTD's native flyout/Translations mechanism.
**Avoids:** Pitfalls 3, 4, 6 (silent-English ja project, unsynced version lists, collateral deletion damage).

### Phase 3: Orphan docs resolution
**Rationale:** Independent of the RTD work but shares the same "delete collateral tests in the same commit" discipline this project has already been burned by twice.
**Delivers:** `docs/usage.rst` + `tests/test_documentation_usage.py` deleted together; `docs/installation.rst` (root orphan only, not the live `docs/source/installation.rst`) + `tests/test_documentation_installation.py` deleted together; full `pytest` run green post-deletion as the actual proof, not the deletion commit itself.
**Addresses:** `docs/usage.rst` / `docs/installation.rst` orphan resolution.
**Avoids:** Pitfall 6 (repeat of the Phase-27 collateral-test trap).

### Phase 4: GitHub Pages removal + linkcheck CI job
**Rationale:** Only safe once Phases 1-3 prove RTD serves both languages and the PDF correctly -- this is the literal "RTD green before Pages removal" ordering constraint, and the one genuinely irreversible step in the milestone (no redirect stubs, owner-accepted SEO cost). The linkcheck job has no dependency on the rest but is grouped here since it touches the same `docs.yml` file.
**Delivers:** `docs.yml`'s `docs-multilang`->`docs-html` swap, PDF-copy step and GH-Pages-deploy step deleted, `tox.ini`'s `docs-multilang` env deleted, `gh-pages` remote branch deleted (as its own explicit git-ref operation); a new advisory (`continue-on-error`) `sphinx-build -b linkcheck` step with `linkcheck_ignore` configured, its scope documented as doc-tree-only.
**Avoids:** Pitfall 7 (irreversible steps out of order) and Pitfall 5 (linkcheck false confidence) -- the linkcheck job's SC must explicitly state it does not cover README/pyproject.

### Phase 5: URL rewrite + Issue #119 close
**Rationale:** Must come after Phase 4 -- the final RTD URL is only fully confirmed once the project exists and serves correctly; rewriting URLs to point at a not-yet-green RTD project trades one broken-link class for another.
**Delivers:** README's ~10 `github.io` occurrences repointed (badge, header, and deep links -- recount at execution time, don't trust the milestone brief's historical figure), `pyproject.toml:56`'s `Documentation` URL, `.planning/codebase/INTEGRATIONS.md`'s hosting-prose update, verified by a real HTTP fetch/grep -- **not** by the linkcheck job from Phase 4; repository About Website field set; Issue #119 replied-to and closed.
**Avoids:** Pitfall 5 (must not lean on linkcheck for this proof).

### Phase 6: v0.6.4 release (final phase)
**Rationale:** Cannot move earlier -- `stable` only becomes a real, buildable RTD version once this tag exists, and this is standard last-phase practice for this project (`branching_strategy: milestone`).
**Delivers:** Version bump, CHANGELOG entry, tag `v0.6.4` pushed, RTD's `stable` version confirmed to build and serve real content (not a 404/placeholder), Default Version flipped from `latest` to `stable` only now, `/ja/stable/` independently re-verified to exist and match the same tag as `/en/stable/`, publish via `/gsd-complete-milestone`.
**Avoids:** The Default-Version sequencing amendment described above; Pitfall 4's re-check requirement.

### Research Flags

Phases likely needing deeper research/empirical probing during planning:
- **Phase 1:** the two layered technical unknowns (wheel/font -- largely settled, but the PDF-content-comparison gate must be designed; `@preview` network egress -- genuinely open, no documentation resolves it) mean this phase's plan should build in an explicit "read the raw RTD build log" verification step, not just a green-checkmark check.
- **Phase 5:** needs its own verification mechanism (real HTTP fetch or a tool like `lychee` against README/pyproject) since linkcheck cannot cover it -- this is a design decision, not just execution, and should be planned explicitly.

Phases with standard, well-documented patterns (research-phase can likely be skipped):
- **Phase 2:** RTD's translation-project mechanics are fully documented (localization guide, manage-translations-for-sphinx guide) -- the only risk is sequencing/verification discipline, not unknown mechanics.
- **Phase 3:** identical to the already-executed Phase-27 pattern from the prior milestone -- a known playbook.
- **Phase 4/6:** standard CI-workflow editing and this project's own established release process (`branching_strategy: milestone`).

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | RTD config schema, env vars, uv integration, linkcheck config all verified against current official docs; typst-py font embedding verified against source `Cargo.toml`. Only the RTD builder CPU architecture was left MEDIUM/inferred by STACK.md alone, but PITFALLS.md's independent PyPI-wheel verification effectively settles it -- treat as HIGH combined. |
| Features | HIGH for RTD platform mechanics (verified against official `docs.readthedocs.com`); a few UI-label/click-path details (exact "Default Version" dashboard location, precise Furo+Addons "Edit on GitHub" reproduction) remain UNVERIFIED and should be confirmed by the owner during the actual manual step, not assumed. |
| Architecture | HIGH for repo-internal facts (all grep-verified with file:line citations); MEDIUM for RTD platform behavior generally (official docs quoted); explicitly UNVERIFIED for the two things no documentation resolves -- `@preview` network egress and the exact byte-for-byte content-comparison expectation for the PDF. |
| Pitfalls | MEDIUM-HIGH -- RTD official docs are current and directly cited; the one true unknown (a real build inside RTD's actual container, covering both the wheel/font question and the network-egress question) is correctly flagged UNVERIFIED rather than guessed at. |

**Overall confidence:** HIGH, with two explicitly-scoped empirical unknowns (both resolvable only by observing a real RTD build log -- not by further documentation research) carried forward rather than glossed over.

### Gaps to Address

- **`@preview` package network egress during RTD build** (the milestone's actual top risk, per the synthesis above) -- no documentation resolves this; must be observed in Phase 1's first real RTD build log. If blocked, the fallback (HTML-only on RTD, PDF stays CI+Release-only) should be pre-agreed so Phase 1 isn't blocked on it.
- **Exactly-one-file constraint on `$READTHEDOCS_OUTPUT/pdf/`** -- STACK.md flagged this as unconfirmed by any RTD reference page (a dedicated "where to put files" page 404'd during research); should not matter for this project's single-master case, but confirm empirically on the first real build.
- **RTD builder CPU architecture "x86_64-only"** -- not explicitly documented, only inferred from the absence of an architecture selector in `build.os`; the cheapest probe is simply observing which wheel tag RTD's `pip`/`uv` resolves on the first real build.
- **Exact current RTD dashboard label/click-path for "Default Version"** -- UI has been reorganized across RTD's own doc versions; confirm the precise location when the owner performs this manual step, don't assume today's exact label from this research.
- **Whether `uv sync`'s editable install of the workspace-root project satisfies `conf.py`'s `sys.path.insert` + `extensions=[...,"typsphinx"]` specifically on RTD's container** (vs. only verified locally/in GitHub Actions) -- standard, well-trodden behavior, low risk, but the real settling probe is the first live RTD build, not more research.

## Sources

### Primary (HIGH confidence)
- `docs.readthedocs.com/platform/stable/config-file/v2.html` -- `.readthedocs.yaml` v2 schema, `build.jobs`, `python.install` (incl. native `method: uv`), `formats`
- `docs.readthedocs.com/platform/stable/build-customization.html` -- build lifecycle stages, format-specific `build.jobs.build.<format>` override semantics
- `docs.readthedocs.com/platform/stable/reference/environment-variables.html` -- `READTHEDOCS_LANGUAGE`, `READTHEDOCS_OUTPUT`, `READTHEDOCS_VERSION`, `READTHEDOCS_VERSION_TYPE`
- `docs.readthedocs.com/platform/stable/localization.html`, `.../guides/manage-translations-sphinx.html` -- translation-project model, per-project independence
- `docs.readthedocs.com/platform/stable/versions.html` / `readthedocs/readthedocs.org` `docs/user/versions.rst` -- stable-from-tags behavior, Default Version redirect targeting a non-existent version
- `docs.readthedocs.com/platform/latest/flyout-menu.html`, `.../addons.html`, `github.com/readthedocs/addons` -- Addons flyout feature list incl. "Edit on GitHub", enabled-by-default since 2024-10-07
- `docs.readthedocs.com/platform/stable/faq.html` -- project-slug change process (support-email only, irreversible in practice)
- `dev.readthedocs.io/en/latest/design/build-images.html` -- Ubuntu 20.04/22.04/24.04 x86_64 build images
- `pypi.org/pypi/typst/json` -- confirms `manylinux2014_x86_64`/`cp38-abi3` prebuilt wheel
- `github.com/messense/typst-py` `Cargo.toml` (fetched directly) -- confirms `typst-kit`'s `embedded-fonts` feature enabled
- Repo-internal grep verification (all four research files) -- `conf.py:51`, `build_multilang.py:44`, `docs.yml:29-63`, `tox.ini:78-84`, `docs/Makefile`, `tests/test_documentation_usage.py`, `tests/test_documentation_installation.py`, `docs/source/_static/custom.css` (full 41-line read)

### Secondary (MEDIUM confidence)
- `about.readthedocs.com/blog/2025/01/override-build-process-with-build-jobs` -- worked example directly analogous to typsphinx's typstpdf case
- `github.com/typst/typst` issues #2818, #4378 -- silent font-fallback behavior (upstream issue tracker, corroborated across multiple issues)
- `pydata-sphinx-theme.readthedocs.io` -- corroborates flyout independence from theme choice

### Tertiary (LOW confidence, corroborating only)
- Community blog walkthrough on "re-import same repo as second RTD project" mechanic for translations -- official docs describe this more abstractly; the blog corroborates the practical mechanic
- Stack Overflow threads on historical `display_github`/`github_url` -- used only to distinguish the pre-Addons mechanism from the current automatic one

---
*Research completed: 2026-07-25*
*Ready for roadmap: yes*
