# Architecture Research — v0.6.4 Read the Docs Migration

**Domain:** Docs hosting / CI-build-pipeline migration (GitHub Pages → Read the Docs) for a Sphinx extension project. No `typsphinx/` runtime code changes.
**Researched:** 2026-07-25
**Confidence:** HIGH for repo-internal facts (all grep-verified with file:line); MEDIUM for RTD platform behavior (official docs fetched and quoted below); explicitly labeled **UNVERIFIED** for the two things no documentation source resolves — see "Open Risks."

## Standard Architecture

### System Overview — the two build paths after migration

```
┌──────────────────────────────────────────────────────────────────────┐
│                         GitHub repository (main + tags)              │
│   docs/source/conf.py · docs/source/**/*.rst · docs/locale/ja/*.po   │
│   .readthedocs.yaml (NEW)                                             │
└───────────────┬───────────────────────────────┬──────────────────────┘
                │                                │
                ▼                                ▼
   ┌─────────────────────────────┐   ┌──────────────────────────────────┐
   │   Read the Docs (RTD)       │   │   GitHub Actions (docs.yml)       │
   │   reads .readthedocs.yaml   │   │   reads tox.ini                   │
   │   ONLY — never sees tox.ini │   │                                   │
   ├─────────────────────────────┤   ├──────────────────────────────────┤
   │ Project "typsphinx" (en)    │   │ tox -e docs-html  (was:           │
   │  - RTD's own sphinx-build   │   │   docs-multilang)                 │
   │    via `sphinx:` key        │   │  → CI artifact only, NOT deployed │
   │    (no tox; RTD IS the      │   │    anywhere (no gh-pages target)  │
   │    task runner here)        │   │ tox -e docs-pdf                   │
   │  - build.jobs.build.pdf:    │   │  → regression gate (fatal-free    │
   │    sphinx-build -b typstpdf │   │    typstpdf compile) + tag-time   │
   │    → $READTHEDOCS_OUTPUT/   │   │    Release-asset attachment       │
   │    pdf/                     │   │    (UNCHANGED responsibility)     │
   │  - versions: latest+stable  │   │ sphinx-build -b linkcheck (NEW,   │
   ├─────────────────────────────┤   │  advisory, non-blocking)          │
   │ Project "typsphinx-ja" (ja) │   └──────────────────────────────────┘
   │  - Translation of the       │
   │    parent, linked in RTD's  │
   │    Admin → Translations UI  │
   │  - SAME repo, SAME commit,  │
   │    SAME conf.py             │
   │  - Project Language: ja     │
   │    → READTHEDOCS_LANGUAGE   │
   │    =ja at build time        │
   └─────────────────────────────┘
```

**Responsibility split (deliberate, not accidental overlap):**

| Concern | RTD | GitHub Actions (`docs.yml`) | Overlap? |
|---|---|---|---|
| HTML publish (en) | Yes — the live site | No (was gh-pages; step deleted) | None — CI no longer publishes anything |
| HTML publish (ja) | Yes — separate RTD project | No | None |
| PDF publish/download | Yes — RTD "Downloads" flyout | No | None |
| PDF as **regression gate** | No | Yes — `tox -e docs-pdf` fails the build/blocks merge on a fatal `TypstCompilationError` | **Deliberate.** RTD builds are async, off the PR critical path, and a red RTD build does not block a merge or fail a check. `tox -e docs-pdf` in CI is the only mechanism that gates a PR on "does the PDF still compile" before merge. Losing it would mean a broken typstpdf pipeline could reach `main` and only be discovered when RTD's build for that commit silently fails hours later. |
| PDF as GitHub Release asset | No | Yes — `softprops/action-gh-release@v3`, tag-only | None — this is a distribution channel RTD doesn't provide (a downloadable artifact attached to the GitHub Release page itself, not the docs site) |
| Local dev iteration | No (RTD only builds on push/PR/tag webhooks) | N/A | `tox -e docs-html` / `tox -e docs-pdf` remain the developer-facing entry points, unchanged |
| Link-rot detection | No | Yes — new advisory `linkcheck` job | None — new capability, not previously covered by either path |

**Concrete edits:**

- **`.readthedocs.yaml`** (NEW, repo root — RTD requires it at the root, not under `docs/`):
  ```yaml
  version: 2
  build:
    os: ubuntu-24.04
    tools:
      python: "3.12"
    jobs:
      build:
        pdf:
          - sphinx-build -b typstpdf docs/source $READTHEDOCS_OUTPUT/pdf
  python:
    install:
      - method: pip
        path: .
        extra_requirements:
          - docs
  sphinx:
    configuration: docs/source/conf.py
  formats:
    - pdf
  ```
  HTML is deliberately **not** overridden under `build.jobs.build.html` — RTD's own `sphinx:` key already runs `sphinx-build -b html` using `sphinx.configuration`; declaring a custom `html` job would be redundant and would additionally have to reimplement RTD's own output-path/versioning wiring for no benefit. Only `pdf` is overridden because `typstpdf` is not a format RTD knows how to invoke itself (RTD's built-in "pdf" format assumes the Sphinx LaTeX builder + `latexmk`, which this project deliberately does not use).

- **`tox.ini`:** delete `[testenv:docs-multilang]` (§ Deletion blast radius). No new tox env needed for RTD — RTD never invokes tox (see "RTD vs tox" decision below). `docs-html` / `docs-pdf` / `docs` envs are unchanged and remain the local-dev + CI entry points.

- **`.github/workflows/docs.yml`:**
  - Line 34–35: `Build multi-language HTML documentation` / `tox -e docs-multilang` → replace with `tox -e docs-html` (single language, CI-artifact-only, no publish target).
  - Lines 40–43 (`Copy PDF to multi-language build`): delete — there is no multilang tree to copy into anymore.
  - Lines 57–63 (`Deploy to GitHub Pages`, `peaceiris/actions-gh-pages@v4`): delete.
  - Lines 65–71 (`Upload PDF to Release`, tag-only): **keep**, unchanged.
  - `tox -e docs-pdf` step (line 38, "Build PDF documentation (English only)"): **keep**, unchanged — this is the regression gate described above. Its step name currently says "(English only)" as a description of what it happens to do today; that's accurate as-is (see Q3) and needs no rename unless the phase wants to make the "this is the CI gate, not the RTD publish path" distinction explicit in the step name.
  - Upload-artifact steps: HTML artifact path changes from `docs/_build/multilang` to `docs/_build/html` (since `build_multilang.py`'s output tree goes away); PDF artifact path (`docs/_build/pdf/*.pdf`) is unchanged.
  - **New job/step:** `sphinx-build -b linkcheck docs/source docs/_build/linkcheck` — advisory (`continue-on-error: true`), same precedent as `drift.yml` (D-07, never a required check).

- **RTD vs. tox — recommendation:** **RTD bypasses tox entirely; do not invoke tox from `.readthedocs.yaml`.** Rationale: RTD's `python.install` step already provisions an environment equivalent to what a tox env would build (installs the project + `docs` extras into RTD's own venv); wrapping that in `tox -e docs-html`/`tox -e docs-pdf` from inside `build.jobs` would mean tox creates a *second*, redundant venv nested inside RTD's already-provisioned one via `tox-uv`'s `uv-venv-lock-runner`, which additionally wants `uv sync --locked` semantics RTD's build image doesn't natively provide without an extra `uv` install step. For the HTML path, RTD's own `sphinx:` key already drives `sphinx-build` directly — there is no tox invocation to make at all, since RTD is the task runner. For the PDF `build.jobs.build.pdf` override, invoking `sphinx-build -b typstpdf docs/source $READTHEDOCS_OUTPUT/pdf` directly is simpler, faster, and matches what `tox -e docs-pdf` runs internally anyway (`changedir = docs; sphinx-build -b typstpdf source _build/pdf`) — the tox env buys nothing extra here since RTD's build environment *is* the isolated environment tox would otherwise build. Tox's role as "the project's task runner" is preserved for humans and CI (`docs.yml`, local dev); RTD is a separate build system with its own manifest format and does not read `tox.ini` at all.

### Component Responsibilities (docs pipeline only)

| Component | Responsibility | Status after migration |
|---|---|---|
| `.readthedocs.yaml` | RTD's sole build manifest — Python env, Sphinx config path, PDF override job, declared formats | NEW |
| `docs/source/conf.py` | Single conf.py built by BOTH RTD projects (en parent, ja translation) from the same commit | MODIFIED (language seam only — see below) |
| `docs.yml` (`build-docs` job) | CI regression gate (`docs-pdf`) + CI-only HTML build artifact (`docs-html`) + advisory `linkcheck`; no longer a deploy pipeline | MODIFIED |
| `docs/build_multilang.py` | Built the old GH Pages multilang tree + JS redirect page | DELETED (see blast radius) |
| `docs/source/_templates/language-switcher.html` | Furo sidebar language links, hand-rolled | DELETED — RTD injects its own version/language flyout widget outside Sphinx's template system entirely |
| `docs/source/_templates/page.html` | Sets `sessionStorage['typsphinx_lang']` so the old root redirect page wouldn't re-redirect a returning visitor | DELETED (see below — **not named in the milestone brief, found by grep**) |
| `docs/source/_static/custom.css` | Styles `.language-switcher` | MODIFIED (strip the language-switcher rule block; file itself likely stays for other custom styling — verify no other selectors exist before deciding delete vs. trim) |
| `docs/locale/ja/**/*.po` (13 files) | sphinx-intl translation catalogs | UNCHANGED — orthogonal to the hosting mechanism |
| `gh-pages` branch (remote) | Old GH Pages publish target | DELETED |

## The `language` Seam (Q2)

**Current state (grep-verified):** `docs/source/conf.py:51` — `language = os.getenv("SPHINX_LANGUAGE", "en")`. The only two producers of `SPHINX_LANGUAGE` in the whole repo are `docs/build_multilang.py:44` (sets it per-language before each `sphinx-build -b html -D language=<code>` subprocess call) and the CI-only default noted in `.planning/codebase/INTEGRATIONS.md:67`. There is no other consumer of `SPHINX_LANGUAGE` anywhere in the tree (confirmed by repo-wide grep — the only three hits are `build_multilang.py:44`, `conf.py:50-51` comment+read, and historical/planning-doc prose).

**Confirmed from RTD's official docs** ([environment-variables reference](https://docs.readthedocs.com/platform/stable/reference/environment-variables.html)): `READTHEDOCS_LANGUAGE` — *"The locale name... for the project being built. This value comes from the project's configured language code."* This is a per-**project** setting configured in each RTD project's Admin → Settings → Language dropdown, not something Sphinx or RTD auto-derives from `conf.py`. RTD does **not** document passing `-D language=` itself, and does not document rewriting `conf.py`'s `language` value for you — the project is responsible for making its own `conf.py` respect `READTHEDOCS_LANGUAGE`, exactly the same shape as the existing `SPHINX_LANGUAGE` mechanism.

**Recommended seam design:**

```python
language = os.getenv("READTHEDOCS_LANGUAGE", os.getenv("SPHINX_LANGUAGE", "en"))
```

- **RTD (both projects):** `READTHEDOCS` is set to `"True"` and `READTHEDOCS_LANGUAGE` is populated automatically by RTD's own build harness from each project's Admin-configured Language field — the en parent project must have Language=`en`, the ja translation project must have Language=`ja` (this is a manual RTD-console step, already captured in the milestone's "requires user operation" list as part of "2 プロジェクト作成"; the per-project Language dropdown should be called out explicitly as its own sub-step, not assumed implicit in project creation).
- **Local `tox -e docs-html`:** `READTHEDOCS` is unset on a dev machine, so `os.getenv("READTHEDOCS_LANGUAGE", ...)` falls through to the existing `SPHINX_LANGUAGE` (or the `"en"` default) unchanged — zero behavior change for local/CI use.
- **`sphinx-intl` workflows on `docs/locale/ja/`:** entirely unaffected. `docs/Makefile`'s `gettext` / `locale-init` / `locale-update` targets never read `SPHINX_LANGUAGE` or `READTHEDOCS_LANGUAGE` at all — they run `sphinx-build -M gettext` (language-agnostic extraction) and `sphinx-intl update -p ... -l ja` (which takes `-l ja` as an explicit CLI flag, not an env var). This seam change touches nothing in that workflow.
- **`build_multilang.py`'s deletion leaves no other consumer of `SPHINX_LANGUAGE` orphaned** — it was the only place that ever *set* the variable; `conf.py` is the only place that *reads* it, and it will keep reading it (now with `READTHEDOCS_LANGUAGE` layered in front) for the local/CI path.
- **Phase 27.1 interaction:** `template_engine.py::derive_typst_lang()` derives the Typst `lang:` parameter from `config.language` (Sphinx's resolved value), not from either env var directly — so once `conf.py`'s `language` resolves correctly from `READTHEDOCS_LANGUAGE`, the already-shipped CONF-07 wiring (Typst-native "Table N"/"表 1" labels) picks it up for free on both RTD projects with no further changes.

## PDF Placement (Q3)

**Lifecycle stage:** `build.jobs.build.pdf` (not `post_build`). Per RTD's [build customization reference](https://docs.readthedocs.com/platform/stable/build-customization.html), the build lifecycle is: `post_checkout → pre_system_dependencies → post_system_dependencies → pre_create_environment → post_create_environment → pre_install → post_install → pre_build → build → post_build`. The `build` step is **format-specific**: `build.jobs.build.html`, `build.jobs.build.pdf`, `build.jobs.build.epub`, `build.jobs.build.htmlzip` can each be overridden independently, and *"declaring one format's build job does not disable the defaults for the others"* — HTML keeps using RTD's own `sphinx:`-driven build untouched while only `pdf` is overridden. This is the correct slot rather than `post_build` because `post_build` is documented as running *after* all format builds complete and is meant for post-processing existing output, not producing a whole missing format from scratch — and because RTD explicitly gates a custom `pdf` job behind declaring `formats: [pdf]` in the top-level config (confirmed: *"If any of the pdf, epub, or htmlzip steps are overridden, they should be included in the formats list"*, [config-file v2 reference](https://docs.readthedocs.com/platform/stable/config-file/v2.html)).

**Interaction with the HTML output directory:** none — `$READTHEDOCS_OUTPUT/html/` and `$READTHEDOCS_OUTPUT/pdf/` are independent format directories RTD serves side-by-side; the PDF job does not need to run after or depend on the HTML job's output, and both can execute from the same checked-out `docs/source` tree.

**Should the ja translation project also build a PDF?** The current CI step is explicitly named "Build PDF documentation (English only)" (`docs.yml:37`) and that framing is accurate as-is — CI has never built a Japanese PDF. For RTD: because `.readthedocs.yaml` is committed once and read identically by *both* the en parent and ja translation projects (same repo, same commit), the `build.jobs.build.pdf` override applies to **both** by default unless something suppresses it per-project. RTD does not document a per-translation-project override of `build.jobs` in the config file itself — the same YAML applies everywhere. Practically this means: either (a) accept that the ja project also produces and serves a PDF (the `sphinx-build -b typstpdf docs/source ...` command already resolves `language` from `READTHEDOCS_LANGUAGE=ja` via the seam above, so the ja PDF would legitimately render "表 1"/"図 1" per CONF-07, giving a real localized PDF essentially for free), or (b) branch the `build.jobs.build.pdf` command on `$READTHEDOCS_LANGUAGE` to skip PDF generation for `ja` and only produce it on `en` (e.g. `[ "$READTHEDOCS_LANGUAGE" = "en" ] && sphinx-build -b typstpdf ... || true`, combined with per-project `formats:` — note `formats` itself is a single shared list in the same file, so suppressing the *download entry* for `ja` would need the shell command to still exit 0 without producing a file, which may leave a dangling "pdf" download link with no file. **Recommend (a):** ship the PDF for both projects — it is a natural consequence of already having the ja translation project build the exact same file, costs one extra `typst.compile()` per RTD build (cheap relative to the whole doc build), and turns "PDF is English-only" from a hard constraint into a bonus capability the migration unlocks, rather than a limitation to engineer around.

## Deletion Blast Radius (Q4)

Every artifact named for deletion in the milestone brief, cross-referenced against a repo-wide grep (file:line cited; `.git/` and `.planning/milestones/**` historical-record hits excluded from the "must fix" set — those are append-only history and correctly left alone per the D-02/D-10 CHANGELOG precedent already established in this project):

| Artifact | Grep-found consumers that must be updated/removed together | Verdict |
|---|---|---|
| `docs/build_multilang.py` | `tox.ini:84` (`[testenv:docs-multilang]` → delete env); `docs/Makefile:35-37` (`multilang:` target, **not named in the milestone brief** — must also be deleted, it's the only other invoker); `docs/Makefile:40-43` (`serve-multilang:` target depends on `multilang` — delete too, it has no other purpose) | DELETE the script + both Makefile targets |
| `[testenv:docs-multilang]` (`tox.ini:78-84`) | Only consumer is `docs.yml:35` (`uv run tox -e docs-multilang`) — already being changed to `docs-html` | DELETE |
| `docs/source/_templates/language-switcher.html` | `docs/source/conf.py:85` (`html_sidebars["**"]` list includes `"language-switcher.html"`) | DELETE file + remove list entry |
| `html_context`/`html_sidebars` wiring (`conf.py:65-89`) | Self-contained in `conf.py`; `html_css_files = ["custom.css"]` (`conf.py:67-68`) references the CSS file, not this block | MODIFY: remove `html_context` (lines 71-77) and the `language-switcher.html` sidebar entry (line 85); **keep** `html_css_files`/`custom.css` wiring itself since the file may retain non-language-switcher rules |
| `docs/source/_static/custom.css` | Only rule block is `.language-switcher*` (confirmed — read the full 41-line file, it contains nothing else) | Since the file's **entire** content is language-switcher CSS with no other rules, this is effectively a DELETE, not a trim — remove both the file and the `html_css_files = ["custom.css"]` line in `conf.py:66-68` (a dangling reference to a missing static file would otherwise emit a Sphinx build warning) |
| `docs/source/_templates/page.html` | **Not named in the milestone brief — found by grep.** Sole consumer/counterpart is `docs/build_multilang.py:86` (`sessionStorage.getItem('typsphinx_lang')` in the old redirect page, which reads what `page.html:8` writes). No other file references `page.html` or `sessionStorage`/`typsphinx_lang`. Once `build_multilang.py`'s redirect page is gone, this template writes to a sessionStorage key nothing ever reads again. | DELETE — dead the moment `build_multilang.py` is deleted; add to the phase's file list even though the milestone brief didn't name it |
| `gh-pages` branch | `remotes/origin/gh-pages` exists (confirmed via `git branch -a`); `.planning/STATE.md:47` documents it as a standing fact ("Milestone branches deleted; only `main` and `gh-pages` remain") | DELETE remote branch (`git push origin --delete gh-pages`) as its own explicit step, separate from the `docs.yml` edit — the branch persists independently of the workflow that used to write to it |
| `docs.yml` deploy step (`:57-63`) + PDF-copy step (`:40-43`) | Self-contained in the one workflow file; no other file invokes `peaceiris/actions-gh-pages` or reads `docs/_build/multilang/en/` | DELETE both blocks |
| `docs/usage.rst` | **Confirmed unreachable**: `docs/source/index.rst`'s toctrees list `installation`, `quickstart`, `user_guide/*`, `examples/*`, `api/index`, `contributing`, `changelog` — no `usage` entry anywhere in `docs/source/**/index.rst`. `tests/test_documentation_usage.py` (11 test functions, `tests/test_documentation_usage.py:14-149`) hard-asserts `docs/usage.rst` exists and has specific content — **this is the exact Phase-27 trap** (the orphan `docs/configuration.rst` deletion redenned the suite via its own collateral test until that test was deleted in the same commit). `CHANGELOG.md:632` references it historically (leave alone, D-02 precedent). | DELETE the `.rst` file AND `tests/test_documentation_usage.py` together, in the same change |
| `docs/installation.rst` (root, dead tree — distinct from the live `docs/source/installation.rst`, 1383 bytes, referenced by `index.rst:35` toctree) | `tests/test_documentation_installation.py` (10 test functions, `tests/test_documentation_installation.py:12-143`) hard-asserts `docs/installation.rst` exists via `os.path.join(..., "docs", "installation.rst")` — same trap, confirmed by reading the test header. `docs/locale/ja/LC_MESSAGES/installation.po` msgid comments reference `../../source/installation.rst` (a **different, live** file — the po file belongs to the canonical `docs/source/installation.rst`, not the orphan; do not touch the `.po` file). `CHANGELOG.md:631` historical, leave alone. | DELETE the root `.rst` file AND `tests/test_documentation_installation.py` together; do **not** touch `docs/source/installation.rst` or its `.po` catalog — they are the live, toctree-reachable file |
| README.md github.io links | Grep found **10** occurrences, not the 9 the milestone brief counted: line 8 (badge), line 12, line 267, and lines 271–277 (7 deep links, one per line). *(Flagging per the project's own "verify roadmap claims before asking" precedent — recount at execution time rather than trusting either number blind.)* | MODIFY: repoint all 10 to the final RTD URL once known |
| `pyproject.toml:56` `Documentation` URL | Currently `https://github.com/YuSabo90002/typsphinx#readme` | MODIFY → RTD URL |
| `.planning/codebase/INTEGRATIONS.md` | No literal github.io URL string in the file (grep-confirmed — only the repo's `Hosting:` line references GitHub itself, `INTEGRATIONS.md:45-46`); the file's `CI Pipeline` bullet for `docs.yml` (`INTEGRATIONS.md:52`) still describes the old "PDF via typstpdf builder on push" framing with no publish-destination mention, and its `Environment Configuration` section (`INTEGRATIONS.md:67`) still lists `SPHINX_LANGUAGE` as the CI-only env var | MODIFY — this file is prose describing current architecture, not a URL string to find/replace; needs a paragraph-level update reflecting RTD as the hosting/build system and the `READTHEDOCS_LANGUAGE` seam, not a grep-and-replace |
| `CHANGELOG.md:393`, `:631-632` | Historical entries | **Leave alone** — Phase 24's D-02 precedent (this project already has a standing decision to not rewrite CHANGELOG history) |

**Net new consumer found NOT in the milestone brief:** `docs/Makefile`'s `multilang`/`serve-multilang` targets and `docs/source/_templates/page.html`. Both are dead the moment `build_multilang.py` is deleted and should be added to whichever phase deletes it.

## New vs. Modified vs. Deleted (Q5)

**New files:**
- `.readthedocs.yaml` (repo root)

**New CI job/step:**
- `sphinx-build -b linkcheck` step in `docs.yml` (advisory, `continue-on-error`)

**Modified files:**
- `docs/source/conf.py` — `language` seam (line 51: layer `READTHEDOCS_LANGUAGE` in front of `SPHINX_LANGUAGE`); remove `html_context`/`html_sidebars` language wiring (lines 65-89); remove `html_css_files`/`custom.css` reference (lines 66-68, since the CSS file is deleted); add `linkcheck_ignore` per the milestone brief
- `.github/workflows/docs.yml` — replace `docs-multilang` → `docs-html` step; delete PDF-copy step; delete GH Pages deploy step; keep `docs-pdf` + tag-time Release attachment unchanged; update artifact upload paths; add linkcheck job
- `tox.ini` — delete `[testenv:docs-multilang]`
- `docs/Makefile` — delete `multilang`/`serve-multilang` targets (found this session, not in the original brief)
- `README.md` — 10 URL occurrences repointed
- `pyproject.toml` — `Documentation` URL (line 56)
- `.planning/codebase/INTEGRATIONS.md` — hosting/CI-pipeline prose updated
- `pyproject.toml` version bump (final release phase only — out of scope for the architecture phases, in scope for the last phase)

**Deleted files:**
- `docs/build_multilang.py`
- `docs/source/_templates/language-switcher.html`
- `docs/source/_templates/page.html` (found this session)
- `docs/source/_static/custom.css`
- `docs/usage.rst` + `tests/test_documentation_usage.py`
- `docs/installation.rst` (root orphan only) + `tests/test_documentation_installation.py`
- `gh-pages` remote branch (not a repo file — a git ref deletion, separate operational step)

**Unchanged (explicitly, to avoid accidental scope creep):**
- `docs/source/installation.rst` (the live, toctree-reachable file — do not confuse with the deleted root orphan)
- `docs/locale/ja/**/*.po` (all 13 files) and the `docs/Makefile` `gettext`/`locale-init`/`locale-update` targets
- `tox -e docs-pdf`, `tox -e docs-html`, `tox -e docs` envs
- `docs.yml`'s tag-time `Upload PDF to Release` step
- `typsphinx/` runtime code, `@preview` package versions, the 3-way version-sync surface

## Suggested Build Order (Q6)

Respecting the hard dependency constraints already identified in the milestone context (RTD must be green before Pages is removed; URLs can't be rewritten until the final RTD URL exists; `stable` only becomes real at the v0.6.4 tag) plus the ones this research surfaced (the `language` seam must land before the ja translation project is created, since RTD will build whatever `conf.py` says the moment the project exists; the orphan-pair deletion must delete its collateral tests in the same change, per the Phase 27 precedent):

1. **`.readthedocs.yaml` + `language` seam.** Add the RTD config file and the `READTHEDOCS_LANGUAGE`/`SPHINX_LANGUAGE` fallback in `conf.py`. This can be validated locally/in CI (env var unset → falls through to existing behavior, zero regression) before any RTD project exists. This is the prerequisite for everything downstream — RTD can't build without it, and the language seam must be correct *before* the ja project is created (manual RTD step) so its very first build already resolves `ja` correctly rather than needing a second pass.

2. **RTD en parent project created + building green (manual RTD console step + verification).** This is the "RTD green before Pages removal" gate — confirm both HTML and the `typstpdf`-via-`build.jobs.build.pdf` PDF build succeed on RTD's actual infrastructure before touching anything else. This phase is where the milestone's sole named technical unknown (does the `typst-py` wheel work in RTD's build image) gets resolved empirically, and where this research's own flagged UNVERIFIED risk (does typst's `@preview` package fetch succeed against RTD's build-sandbox network policy) also gets resolved empirically — both are only answerable by an actual RTD build, not by more research.

3. **RTD ja translation project created + linked (manual RTD console steps) + `docs/usage.rst`/`docs/installation.rst` orphan-pair resolution + multilang-machinery deletion.** These are independent of each other and can be sequenced within the same phase or split, but both must happen only after step 2 proves the `.readthedocs.yaml`/`conf.py` combination is sound (no point building the ja project against a broken config, and no point deleting the multilang machinery before RTD's own translation-flyout replacement is confirmed working, or GH Pages would go dark with no working replacement). The orphan-pair deletion must delete `tests/test_documentation_usage.py`/`tests/test_documentation_installation.py` in the same commit as their subject files (Phase 27 precedent).

4. **GitHub Pages removal** (`docs.yml` deploy step + PDF-copy step deletion, `docs-multilang`→`docs-html` swap, `gh-pages` branch deletion, `tox.ini`/`docs/Makefile` cleanup) + **advisory `linkcheck` CI job.** Only now, once steps 2–3 prove RTD serves both languages and the PDF correctly, is it safe to cut the old host — this is the literal "RTD green before Pages removal" ordering constraint. The linkcheck job has no ordering dependency on the rest and could be added any time after step 1, but grouping it here keeps "everything that touches `docs.yml`" in one phase.

5. **URL rewrite** (README's 10 occurrences, `pyproject.toml:56`, `.planning/codebase/INTEGRATIONS.md`) + **Issue #119 close + repository About Website field.** This must come *after* step 4, not before — the final RTD URL slug is only fully confirmed once the project exists and is serving correctly (steps 2–3), and rewriting URLs to point at a not-yet-green RTD project would trade one broken link class for another. The About Website field and Issue #119 close both depend on having a real, working URL to put in them.

6. **v0.6.4 release (final phase).** Tag `v0.6.4` — this is also the moment `stable` becomes a real, buildable RTD version for the first time (RTD's 2023-09-25 policy fails builds on tags lacking `.readthedocs.yaml`, and `v0.6.4` is the first tag that will have one). Bump `pyproject.toml`, curate `CHANGELOG.md`, publish per the established `branching_strategy: milestone` process. **This phase cannot move earlier** — `stable` cannot be verified real until the tag exists, and the tag is standard last-phase practice in this project regardless.

## Open Risks (label: UNVERIFIED)

Neither of these is resolvable by more documentation research — they require an actual RTD build to observe:

1. **`typst-py` wheel installability on RTD's build image.** Already flagged as the milestone's sole named technical unknown. typst-py ships PyO3/maturin-built wheels for common Linux x86_64 targets on PyPI, which makes success likely on RTD's `ubuntu-24.04` image, but this is inference, not confirmation.
2. **Network egress for Typst's `@preview` package fetch during compile.** `typst.compile()` fetches `@preview/codly`, `@preview/codly-languages`, `@preview/mitex`, `@preview/gentle-clues` from the Typst Universe registry (`packages.typst.org`) on first use if not already cached, caching the result under `~/.cache/typst/packages`. Web search did not surface a definitive RTD statement on build-sandbox outbound network policy (general RTD docs describe PyPI/npm/conda package-index access for dependency installation but say nothing about arbitrary HTTPS fetches mid-build). If RTD's build sandbox restricts outbound traffic to package indices only, the `typstpdf` `build.jobs.build.pdf` step could fail to resolve the `@preview` imports on a cold cache, independent of whether the `typst-py` wheel itself installs correctly. This is a second, more specific risk than "does the wheel install" and should be verified in the same empirical phase (step 2 of the build order above), ideally by observing the actual RTD build log for the `@preview` package downloads.

## Sources

- [Configuration file reference (v2) — Read the Docs](https://docs.readthedocs.com/platform/stable/config-file/v2.html) — `formats`, `build.jobs.build.<format>`, `sphinx.configuration`/`sphinx.builder`, `python.install` schema
- [Build process customization — Read the Docs](https://docs.readthedocs.com/platform/stable/build-customization.html) — full `build.jobs` lifecycle stage order, format-specific build override semantics
- [Build process overview — Read the Docs](https://docs.readthedocs.io/en/stable/builds.html)
- [Environment variable reference — Read the Docs](https://docs.readthedocs.com/platform/stable/reference/environment-variables.html) — `READTHEDOCS`, `READTHEDOCS_PROJECT`, `READTHEDOCS_LANGUAGE`, `READTHEDOCS_VERSION` definitions
- [How to manage translations for Sphinx projects — Read the Docs](https://docs.readthedocs.com/platform/stable/guides/manage-translations-sphinx.html)
- [Localization and Internationalization — Read the Docs](https://docs.readthedocs.com/platform/en/stable/localization.html) — "each language must have its own project... add each of the other projects as Translations of the parent project"
- ["You can now partially or completely override the build process" — Read the Docs blog, 2025-01](https://about.readthedocs.com/blog/2025/01/override-build-process-with-build-jobs/)
- Repo-internal facts: grep-verified against the working tree at commit `771ec56` (2026-07-25) — see file:line citations inline above

---
*Architecture research for: RTD migration (typsphinx v0.6.4)*
*Researched: 2026-07-25*
