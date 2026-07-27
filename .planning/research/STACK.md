# Stack Research

**Domain:** Documentation hosting migration (GitHub Pages → Read the Docs) for a Sphinx extension that dogfoods its own `typstpdf` builder
**Researched:** 2026-07-25
**Confidence:** HIGH (RTD config schema, env vars, uv integration, linkcheck config — all verified against current official docs) / HIGH (typst-py font embedding — verified against source `Cargo.toml`) / MEDIUM (RTD builder CPU architecture — inferred, not explicitly documented; see Gaps)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `.readthedocs.yaml` schema | `version: 2` | RTD build config | Only schema RTD accepts today; v1 is long removed. Verified against `docs.readthedocs.com/platform/stable/config-file/v2.html`. |
| `build.os` | `ubuntu-24.04` | RTD builder OS image | Current default in every official RTD example (Sphinx quickstart, MkDocs quickstart, the uv example) as of this research. Valid enum is `ubuntu-22.04` / `ubuntu-24.04` / `ubuntu-26.04` / `ubuntu-lts-latest`; pin an explicit version (not `-lts-latest`) per RTD's own reproducibility guidance — a floating tag can shift glibc/toolchain under you without a corresponding commit. |
| `build.tools.python` | `"3.13"` | Python interpreter RTD provisions | Valid enum includes `"3.12"`/`"3.13"`/`"latest"` etc.; `"3.13"` satisfies the project's `requires-python = ">=3.12"` and matches the newer end of the supported range. `"3.12"` is an equally valid pin if parity with the CI matrix's lead lane is preferred — either works, this is a style choice not a constraint. |
| `python.install` method `uv` | native RTD support (no version pin needed — RTD provisions its own `uv`) | Installs the project + its `docs` extra via `uv sync` | RTD added **native uv support inside `python.install`** (not just a `build.jobs` escape hatch): `method: uv` with `command: sync` and `extras:`/`groups:` lists. RTD's own build-customization docs state "Read the Docs' own build steps expect it by setting the `UV_PROJECT_ENVIRONMENT` variable" — i.e. `uv` is preinstalled/wired into the image, you don't provision it yourself via `asdf` (an older doc example does that; it is now superseded by native support). `uv sync` installs the workspace-root project itself (typsphinx) in addition to declared deps — this replaces the current `docs.yml` two-step `uv sync --extra dev --extra docs --locked` + `uv pip install -e .` with one declarative block. |
| `typst` (typst-py) | `>=0.15.0,<0.16` (unchanged — already pinned in `pyproject.toml`) | Compiles `typstpdf` output on the RTD builder | manylinux2014 wheel (glibc 2.17+) for x86_64/aarch64/etc — see Q2 discussion below. No RTD-specific version change needed; this milestone does not touch runtime deps. |

### Supporting Libraries

No new Python packages are needed. Everything below is either already a `docs` extra or built into Sphinx/RTD:

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `sphinx-build -b linkcheck` | built into Sphinx (already a dependency) | Advisory CI job checking external URLs | Zero new dependency — it's a stdlib Sphinx builder, same binary already installed for `-b html`/`-b typstpdf`. |
| `linkcheck_ignore` | Sphinx conf value | Suppress known-noisy/unreachable-in-CI URLs | Regex list matched against target URIs before a network request is made (`is_ignored_uri` in `sphinx/builders/linkcheck.py`). |
| `linkcheck_retries` | Sphinx conf value, default `1` | Retry count per broken link before reporting | Raise if flaky third-party hosts cause false positives in the advisory job. |
| `linkcheck_timeout` | Sphinx conf value | Per-request timeout (seconds) | Set if slow hosts (e.g. PyPI project pages) cause the advisory job to hang. |
| `linkcheck_workers` | Sphinx conf value, default `5` | Parallel link-check worker threads | Rarely needs tuning; only relevant for large link counts. |
| `linkcheck_anchors` / `linkcheck_anchors_ignore` / `linkcheck_anchors_ignore_for_url` | Sphinx conf values | Control `#fragment` validation | Use `linkcheck_anchors_ignore_for_url` to skip anchor-checking on hosts known to render anchors client-side (e.g. GitHub's rendered Markdown anchors, which linkcheck's static HTML fetch cannot see). |
| `linkcheck_exclude_documents` | Sphinx conf value | Skip specific docnames entirely | Use if a specific page (e.g. an auto-generated API index with many external refs) is noisy. |
| `linkcheck_rate_limit_timeout` | Sphinx conf value | Backoff window on HTTP 429 | Default is usually sufficient; only relevant if a target host rate-limits. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| RTD web dashboard (2 projects: parent `typsphinx` + a `ja` translation project) | Hosts `en` (parent) and links `ja` (translation project) | **Manual, one-time, cannot be automated from this repo** — project creation, the Translations link, and setting the default version to `stable` are all done in the RTD UI/API by a human with an RTD account. Out of scope for `.readthedocs.yaml` itself. |
| GitHub repository "About" → Website field | Points external users (incl. Issue #119's reporter) at the new RTD URL | Also manual; not a file in this repo. |

## Installation

No `pip install` / `npm install` step changes for the Python package itself. The only new file is `.readthedocs.yaml` at the repo root:

```yaml
# .readthedocs.yaml
version: 2

build:
  os: ubuntu-24.04
  tools:
    python: "3.13"
  jobs:
    build:
      pdf:
        - mkdir -p $READTHEDOCS_OUTPUT/pdf/
        - sphinx-build -b typstpdf docs/source $READTHEDOCS_OUTPUT/pdf/
        # NOTE: confirm the on-disk filename `sphinx-build -b typstpdf`
        # actually writes here (per this repo's typst_documents target-stem
        # naming / the PDF-01 output-stem resolver in builder.py) lands
        # correctly inside $READTHEDOCS_OUTPUT/pdf/ — see "What NOT to Add"
        # / Gaps below for the exactly-one-file caveat.

sphinx:
  configuration: docs/source/conf.py

formats:
  - pdf   # required whenever the `pdf` build.jobs step is overridden — RTD
          # docs: "If any of the pdf, epub, or htmlzip steps are overridden,
          # they should be included in the formats list."

python:
  install:
    - method: uv
      command: sync
      extras:
        - docs
```

Key points this encodes (each traced to a verified source below):

1. **`build.jobs.build.pdf` overrides only the PDF step**; `html` keeps RTD's default `sphinx-build -b html` behavior driven by the top-level `sphinx:` key. This is exactly the "keep using the default commands ... but extend or override the ones you need" pattern RTD's build-customization page documents, and it lands the typst-generated PDF in the one directory (`$READTHEDOCS_OUTPUT/pdf/`) RTD's Downloads/flyout UI reads from.
2. **`python.install: method: uv`** is the RTD-native mechanism (documented at `docs.readthedocs.com/platform/stable/config-file/v2.html`) — not a hand-rolled `build.jobs.install` override. `command: sync` runs `uv sync` against this project's root `pyproject.toml`/`uv.lock`; `extras: [docs]` maps to `uv sync --extra docs` (this project's `docs` group lives under `[project.optional-dependencies]`, **not** `[dependency-groups]`, so `extras:` is the correct key — `groups:` is for PEP 735 `[dependency-groups]` entries like this repo's `dev`). `uv sync` installs the workspace-root project itself (typsphinx) in editable mode as part of the sync, satisfying `conf.py`'s `extensions = [..., "typsphinx"]` without a separate `uv pip install -e .` step.
3. **Only one entry is allowed under `python.install` when `method: uv` is used** (RTD constraint) — so this is deliberately a single list item, not `method: uv` alongside a second `method: pip` entry.

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|--------------------------|
| `python.install: method: uv` (native) | `build.jobs` override with `asdf plugin add uv` + `uv venv "$READTHEDOCS_VIRTUALENV_PATH"` + `UV_PROJECT_ENVIRONMENT=... uv sync` | Use the manual `build.jobs` form only if you need an argument the native `method: uv` schema doesn't expose (RTD's own docs: "Use `build.jobs` only when you need an advanced uv workflow that isn't covered by `python.install`"). This project's needs (sync + one extras group) are fully covered by the native form, so prefer it — less YAML, less surface to drift from RTD's own maintained defaults. |
| `formats: [pdf]` + `build.jobs.build.pdf` override (typst-generated PDF) | `formats: [pdf]` alone, letting RTD build its own LaTeX-based PDF | Never, for this milestone — this project's whole point is dogfooding `typstpdf`; RTD's default LaTeX PDF path is a completely separate Sphinx `-b latex` + `latexmk`/TeX Live pipeline that has nothing to do with this extension and would silently ship a *different, worse* PDF (no `typst_use_mitex`, no custom template) alongside — or instead of — the one this project exists to produce. See "What NOT to Add." |
| `build.os: ubuntu-24.04` (pinned) | `build.os: ubuntu-lts-latest` | Use `-lts-latest` only if you want RTD to auto-advance the OS image for you and are comfortable with the image (and its glibc/apt package versions) changing without a corresponding commit to this repo. Given the "one genuine technical unknown" framing of this milestone (does `typst-py` work on RTD's image), an **explicit, pinned** OS version is the more cautious choice — a future OS bump becomes a deliberate, reviewable diff instead of a silent surprise. |

## What NOT to Add

| Avoid | Why | Use Instead |
|-------|-----|--------------|
| `formats: [pdf]` **without** a `build.jobs.build.pdf` override | RTD's default Sphinx PDF path runs its own LaTeX (`-b latex` + `latexmk`) pipeline requiring a TeX Live toolchain — an entirely different, much heavier build than `typstpdf`, and produces a PDF this project does not control the styling of. This directly contradicts the milestone's "keep dogfooding `typstpdf`" invariant. | `formats: [pdf]` **with** `build.jobs.build.pdf` overridden to run `sphinx-build -b typstpdf ...` and write into `$READTHEDOCS_OUTPUT/pdf/`. |
| `sphinx-rtd-theme` | RTD does not require its own theme — Furo (already in `docs` extras) works fine on RTD and is what this project already ships. Swapping themes is an unrelated, unrequested visual change and risks breaking the custom CSS (`custom.css`) already tuned for Furo. | Keep `furo` unchanged. |
| RTD "Addons" flyout-integration Sphinx extensions (e.g. `sphinx-notfound-page`, `sphinx-hoverxref`) | Not requested by this milestone's scope (only "URL 張り替え" + "版別/言語別に正しく引ける" + linkcheck). RTD's Addons (search, flyout version/language menu) are injected automatically at the platform level — no Sphinx extension is required to get the baseline version/language flyout described in the milestone brief. Adding extensions here would be scope creep against the "zero new runtime deps" invariant this project holds tightly across milestones. | Nothing — RTD's Addons work out of the box; only add `sphinx-notfound-page`-class extensions later if a *specific* subsequent requirement calls for them. |
| `build.apt_packages` entries for fonts (e.g. `fonts-liberation`, `fonts-dejavu`) | **Not needed** — `typst-py`'s `Cargo.toml` enables `typst-kit`'s `embedded-fonts` feature (confirmed by direct inspection of `messense/typst-py`'s `Cargo.toml`: `typst-kit = { version = "0.15.1", features = ["embedded-fonts", "scan-fonts", "system-downloader", "system-packages", "vendor-openssl"] }`). This bakes Libertinus Serif / New Computer Modern / New Computer Modern Math / DejaVu Sans Mono directly into the compiled wheel — identical to what the Typst CLI ships. English-only docs (this project's case) need zero system font packages to compile. `scan-fonts` is also enabled, meaning it will *additionally* look for system fonts if present, but absence of any system fonts is not a failure — it falls back to the embedded set. | Nothing. If a future milestone adds non-Latin-script or CJK-heavy Typst output (not this milestone — the PDF stays English-only per scope), *then* revisit `build.apt_packages` for fonts; not needed here. |
| Manually installing/pinning `uv` via `asdf`/`pip install uv` in a `build.jobs.pre_create_environment` step | Superseded by RTD's native `method: uv` support in `python.install`; RTD's own build-customization docs describe the manual `asdf` pattern as the pre-native-support workaround, and separately state "Read the Docs' own build steps expect [`uv`], by setting the `UV_PROJECT_ENVIRONMENT` variable" — i.e. `uv` is already provisioned on the image when `method: uv` is used. | `python.install: - method: uv` as shown above. |
| A second/duplicate `docs-multilang`-style tox env for RTD | RTD does not invoke `tox` at all in the recommended flow — it drives Sphinx directly via `sphinx:`/`python.install`/`build.jobs`. The existing `tox -e docs-html` / `tox -e docs-pdf` envs stay as the **local-dev and CI** entry points (`docs.yml` keeps running `tox -e docs-pdf` as the regression gate per this milestone's explicit "残す" decision); `.readthedocs.yaml` is a parallel, RTD-only build description, not a tox wrapper. | Keep `tox.ini`'s `docs-html`/`docs-pdf`/`docs` envs exactly as-is for local/CI use; `.readthedocs.yaml` calls `sphinx-build` directly. |

## Stack Patterns by Variant

**If the `ja` translation project needs the same PDF behavior as the `en` parent:**
- RTD translation ("child") projects each get their **own** `.readthedocs.yaml` resolution from the **same repository** (translation projects in RTD point at the same VCS repo, just with a different configured `Language` and, typically, the same config file) — so the identical `build.jobs.build.pdf` step will also run for the `ja` project unless conditioned.
- Because `conf.py:51` will read `READTHEDOCS_LANGUAGE` (see below) and `typst_use_mitex`/templates are language-agnostic already, no additional `.readthedocs.yaml` branching is needed for v1 — the same PDF job runs for both, producing an (English-content) PDF under both `/en/` and `/ja/` unless a future requirement asks for a Japanese-specific PDF. This matches the milestone brief's explicit "PDF stays English" framing — no action needed, just note it's a shared artifact across both language projects unless later scoped otherwise.

**If `READTHEDOCS_LANGUAGE` is unset (local dev, plain `sphinx-build`, or CI's `tox -e docs-html`/`docs-pdf`):**
- Use `os.getenv("READTHEDOCS_LANGUAGE", "en")` — the same fallback-to-`"en"` pattern the current `SPHINX_LANGUAGE` line already uses — so `conf.py` keeps working identically outside RTD.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|------------------|-------|
| `typst-py 0.15.0` (manylinux2014, glibc 2.17+, `cp38-abi3`) | `ubuntu-24.04` RTD image | Ubuntu 24.04's glibc is 2.39 — vastly newer than the wheel's `manylinux2014`/glibc-2.17 floor, so the wheel is installable on any RTD Ubuntu image currently offered (`22.04`/`24.04`/`26.04`). This is a purely-`pip`-resolvable wheel install; no compilation, no Rust toolchain, no `cargo` needed on the builder. |
| `typst-py`'s embedded fonts | English-only Typst output (this project's docs) | Confirmed via `typst-kit`'s `embedded-fonts` feature in `typst-py`'s `Cargo.toml` (see "What NOT to Add"). No `build.apt_packages` font installs required. |
| `python.install: method: uv` | `[project.optional-dependencies]` (this repo's `docs` group) | Use `extras:`, not `groups:` — `groups:` targets PEP 735 `[dependency-groups]` (this repo's `dev` group lives there), while `docs` is a classic setuptools "extra." Getting this backwards silently installs the wrong (or no) additional packages. |
| `sphinx>=9.1,<10` / `docutils>=0.21,<0.23` (already pinned, unchanged) | RTD's own default `sphinx-build -b html` step | RTD's zero-config `sphinx:` key runs the same `sphinx-build` binary this project's `tox -e docs-html` already runs — no version skew risk since it's the one `uv sync`-installed interpreter/environment, not a separate RTD-bundled Sphinx. |

## Sources

- `docs.readthedocs.com/platform/stable/config-file/v2.html` — HIGH. `.readthedocs.yaml` v2 schema: `build.os` enum, `build.tools.python` enum, `build.jobs` key list (`post_checkout` … `post_build`, with `build.pdf`/`build.html`/`build.epub`/`build.htmlzip` sub-keys), `python.install` schema including the native `method: uv` (`command: sync|pip`, `extras`, `groups`, one-entry-only constraint), `formats` key, `build.apt_packages`.
- `docs.readthedocs.com/platform/stable/build-customization.html` (and its `.io` mirror) — HIGH. Confirms `build.jobs` overrides only the steps you name while defaults still run for the rest; documents the (now-superseded-for-most-cases) manual `asdf`+`uv` pattern and explicitly states "Read the Docs' own build steps expect [uv], by setting the `UV_PROJECT_ENVIRONMENT` variable," i.e. `uv` ships on the image.
- `docs.readthedocs.com/platform/stable/reference/environment-variables.html` — HIGH. Full `READTHEDOCS_*` variable enumeration, verbatim quoted for `READTHEDOCS_LANGUAGE` ("The locale name, or the identifier for the locale, for the project being built," lowercase-dash-separated, e.g. `en`, `de-at`-style values), `READTHEDOCS_OUTPUT`, `READTHEDOCS_VERSION`, `READTHEDOCS_CANONICAL_URL`, `READTHEDOCS_PROJECT`, `READTHEDOCS_VIRTUALENV_PATH` (pip/virtualenv builds only, not Conda), `READTHEDOCS` (bool).
- `docs.readthedocs.io/page/intro/sphinx.html` — HIGH. Minimal Sphinx-on-RTD example confirming `build.os: ubuntu-24.04` as the currently-recommended default.
- `docs.readthedocs.com/platform/stable/downloadable-documentation.html` and `.../guides/enable-offline-formats.html` — HIGH for the general `formats:` mechanism; did **not** yield an explicit statement on the exactly-one-PDF-file constraint for `$READTHEDOCS_OUTPUT/pdf/` — flagged as a gap below.
- `github.com/messense/typst-py` (`Cargo.toml`, fetched directly) — HIGH (primary source, direct dependency declaration, cross-checked against `typst/typst`'s own `docs/Cargo.toml` using the identical `typst-kit`/`embedded-fonts` pattern and against `typst.app/docs/reference/text/text` which names the same embedded font set for the CLI). This is the load-bearing evidence for the milestone's "one genuine technical unknown" (fonts) — **not** UNVERIFIED.
- `pypi.org/project/typst` (file listing) — HIGH. `typst-0.15.0-cp38-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` and the `aarch64` counterpart confirmed to exist; glibc 2.17 floor is far below any RTD Ubuntu image's glibc.
- `sphinx-doc.org` (`sphinx/builders/linkcheck.py` source, fetched directly) — HIGH, primary source. Confirms the full `linkcheck_*` config-value surface consumed by `HyperlinkAvailabilityCheckWorker`/`HyperlinkAvailabilityChecker`.
- RTD build-server CPU architecture (x86_64/amd64) — **MEDIUM, inferred not documented**. See Gaps below.

## Gaps / UNVERIFIED — named probes

1. **RTD builder CPU architecture is not explicitly documented as "x86_64-only."** Evidence supporting x86_64 is circumstantial: (a) RTD's `build.os` enum (`ubuntu-22.04`/`24.04`/`26.04`/`ubuntu-lts-latest`) carries no architecture selector at all — if RTD offered ARM builders, this is the natural place a project would pick one, and it isn't there; (b) RTD's own blog documents an AWS-hosted infrastructure migration, and standard AWS-hosted CI/build fleets default to x86_64 unless a project opts into Graviton/ARM instances, which RTD's docs never mention. **This is not a confirmed fact, just the best inference available from current docs.** Named probe: push this milestone's `.readthedocs.yaml` as a real RTD build and inspect the build log for the resolved `pip`/`uv` wheel selection — a `manylinux2014_x86_64` wheel being selected confirms x86_64; a fallback to source-build or an `aarch64` wheel would falsify this. This is the cheapest possible probe (one real build, already required for the milestone regardless) and should be the actual verification, not further documentation research.
2. **Exactly-one-file constraint on `$READTHEDOCS_OUTPUT/pdf/` is not confirmed from docs.** RTD's guides describe the mechanism generally ("files in these directories will automatically be found, uploaded, and published") but a dedicated "Where to put files" reference page returned HTTP 404 during this research (URL structure appears to have changed/moved) and no substitute page stated a hard one-file rule. Named probe: after wiring the `build.jobs.build.pdf` step, check the RTD Project dashboard → Downloads UI and/or the build log for a warning if more than one `.pdf` ends up in that directory (should not happen here — `sphinx-build -b typstpdf` writes exactly one PDF for this project's single `typst_documents` master — but confirm empirically on the first real build rather than assuming).
3. **Whether `uv sync`'s editable install of the workspace-root project fully satisfies `conf.py`'s `sys.path.insert(0, os.path.abspath("../.."))` + `extensions = [..., "typsphinx"]` on RTD specifically** (vs. only verified locally/in GitHub Actions) is not yet empirically confirmed on RTD's actual container. This is standard, well-trodden `uv sync` behavior and not considered a serious risk, but — like #1 — the real settling probe is simply the first live RTD build, not further documentation research.

---
*Stack research for: Read the Docs migration (typsphinx v0.6.4)*
*Researched: 2026-07-25*
