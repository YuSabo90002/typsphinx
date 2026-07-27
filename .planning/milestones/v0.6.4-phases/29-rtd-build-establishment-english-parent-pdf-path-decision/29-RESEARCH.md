# Phase 29: RTD Build Establishment (English Parent) + PDF Path Decision - Research

**Researched:** 2026-07-25
**Domain:** Documentation-hosting build-manifest authoring (`.readthedocs.yaml`) + verification of an
owner-performed RTD web-UI setup. Not a code phase — no `typsphinx/` runtime change.
**Confidence:** HIGH for repo-internal facts and RTD config schema (all traceable to the milestone's
own `.planning/research/*.md`, already fetched from official RTD docs); explicitly LOW/UNVERIFIED for
the two things only a real RTD build can resolve (`@preview` network egress, exact raw-build-log
wording for "installed from local checkout").

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**RTD project slug (owner-manual, irreversible)**
- **D-01:** English parent slug is **`typsphinx`** → `https://typsphinx.readthedocs.io/en/latest/`.
  Measured 2026-07-25: root URL 404s today (unclaimed); RTD's import screen is authoritative.
- **D-02:** If the slug is taken at import time, **stop and consult the owner** — no silent fallback.
- **D-03:** The Japanese slug is **not** decided here — Phase 30's discussion. `typsphinx-ja.readthedocs.io` also 404s today (measurement only).

**PDF output path (`build.jobs.build.pdf`)**
- **D-04:** Build into a **temporary directory, then copy only `*.pdf`** into
  `$READTHEDOCS_OUTPUT/pdf/`. Do **not** point `sphinx-build -b typstpdf` directly at
  `$READTHEDOCS_OUTPUT/pdf/`. Measured: the builder writes 31 files (PDF + 14 `.typ` + 16-file
  `.doctrees/`) into its output directory — only the PDF belongs in RTD's download area.
- **D-05:** PDF filename stays **`typsphinx.pdf`** (from `typst_documents`'s target name) — matches
  the existing GitHub Release asset name.

**Probing the `@preview` egress unknown**
- **D-06:** **Two-stage, HTML first.** Commit 1: `.readthedocs.yaml` builds HTML only (no `formats:`,
  no `build.jobs.build.pdf`) — discharges RTD-01/RTD-04 first. Commit 2 (separate): add
  `formats: [pdf]` + `build.jobs.build.pdf` + read that build's raw log. Cost: two RTD build cycles,
  accepted, so the phase never passes through a state where `/en/latest/` is red.
- **D-07:** The `@preview` verdict must be a **recorded log excerpt**, not an inference. Branch A
  needs the log to show the four packages resolving **and** zero `latexmk`/`pdflatex`/`.tex` lines
  anywhere. Branch B needs the log to show the registry fetch blocked/failed.

**Branch B fallback (registry blocked)**
- **D-08:** Link to `https://github.com/YuSabo90002/typsphinx/releases/latest/download/typsphinx.pdf`
  from **both** `docs/source/index.rst` (Quick Links) **and** `README.md`. Measured 2026-07-25: that
  URL already returns HTTP 200, 1,678,961 bytes against `v0.6.3` — no per-release editing needed.
- **D-09:** The `README.md` edit lands in the same file Phase 31 rewrites — keep it a small,
  additive block.

**CJK fonts — new risk found by measurement**
- **D-10:** Add **`build.apt_packages: [fonts-noto-cjk]`** in the PDF-enabling commit. Measured: the
  English docs contain 「表 1」「図 1」「图 1」「圖 1」 at
  `docs/source/user_guide/configuration.rst:186,240` (CONF-07's `lang` explanation, v0.6.3 Phase
  27.1). typst-py's embedded fonts (Libertinus Serif / New Computer Modern) have no CJK coverage;
  Typst's font fallback is silent — an image without CJK fonts renders tofu in a build that reports
  success.
- **D-11:** D-10 is not a reversal of deferred I18N-03 (no Japanese PDF). Four CJK strings inside the
  English doc, not a full Japanese PDF. `build.apt_packages` is RTD build-environment config, not a
  Python runtime dependency — the zero-new-runtime-deps invariant is untouched.

**RTD-02 content-comparison gate (Branch A)**
- **D-12:** Bar against the local `tox -e docs-pdf` baseline for the same commit: (1) page count
  matches, (2) extracted text matches (`pypdf`, already a `dev` extra), (3) the RTD-built PDF embeds
  at least one font with CJK coverage, (4) the owner opens the two affected pages and confirms no
  tofu.
- **D-13:** "Embedded font list must match exactly" is **explicitly rejected** as a bar — the local
  baseline's 9-font list includes 5 host-provided fonts; only CJK *coverage* is asserted.
- **D-14:** Text-extraction equality alone cannot detect glyph substitution (tofu still extracts
  correct characters) — checks 3 and 4 exist for exactly this reason.
- **D-15:** The comparison is a **one-off**, run by hand, commands + output pasted verbatim into
  `29-VERIFICATION.md`. **No comparison script is committed** — the RTD-built PDF is unreachable from
  CI, so a committed script would never run automatically. The human-look half is recorded honestly
  (`human_needed`), not asserted as machine-verified.

### Claude's Discretion

- `build.os` / `build.tools.python`: **Recommendation confirmed by this research: `ubuntu-24.04` +
  Python `3.12`** — parity with `.github/workflows/docs.yml`'s `python-version: "3.12"` so the RTD
  PDF and the `tox -e docs-pdf` baseline in D-12 compare across the same Python minor. `ubuntu-24.04`
  is verified a currently-valid `build.os` enum value (see Standard Stack).
- Exact `sphinx:` key wording, `python.install` block shape (`method: uv`/`command: sync`/
  `extras: [docs]` — already locked by prior decisions), temp-directory name and `-d` doctrees
  placement in `build.jobs` commands — see Code Examples for a concrete recommendation.
- Which log lines are captured as evidence, and their formatting in `29-VERIFICATION.md`.

### Deferred Ideas (OUT OF SCOPE)

- Japanese RTD project / slug — Phase 30.
- multilang machinery / orphan-doc deletions — Phase 30.
- README / `pyproject.toml` URL rewrites (beyond D-08/D-09's small additive fallback block) — Phase 31.
- GitHub Pages teardown — Phase 32.
- Version bump / CHANGELOG — Phase 33.
- PR preview builds — dropped from v1 (RTD-05, Future).
- A Japanese-language PDF — deferred I18N-03.
- No `typsphinx/` source change of any kind — a re-scope signal if the phase appears to need one.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RTD-01 | Reader browses English docs on RTD, built from `.readthedocs.yaml`, typsphinx installed from the in-repo commit (not stale PyPI) | Standard Stack (`python.install: method: uv`); Validation Architecture SC#1 rows; Open Questions #1 (exact log-line wording is unconfirmed) |
| RTD-02 | Downloaded PDF is typsphinx's own `typstpdf` output, content-verified against `tox -e docs-pdf` baseline, not just build status | Code Examples (`build.jobs.build.pdf`); D-12/D-13/D-14 (already locked); Validation Architecture SC#3 Branch A |
| RTD-03 | If `@preview` egress is blocked, docs link to the GitHub Release PDF via a URL that stays correct across releases | D-08 (already measured 200/1,678,961 bytes); Validation Architecture SC#3 Branch B |
| RTD-04 | Root URL always lands on a version that exists and serves real content, at every point during migration | D-06 two-stage sequencing; Common Pitfalls (Default Version); Validation Architecture SC#4 |
</phase_requirements>

## Summary

This phase's repo-side deliverable is exactly two edits: a new `.readthedocs.yaml` at the repository
root (landed in two commits per D-06), and a two-line `language` seam in `docs/source/conf.py:51`
(`READTHEDOCS_LANGUAGE` → `SPHINX_LANGUAGE` → `"en"`). Everything else — the RTD project creation, the
GitHub connection, reading the raw build log, downloading and comparing the PDF, opening the two CJK
pages — is either owner-manual web-UI work or a live-network verification step. There is no ambiguity
left in the `.readthedocs.yaml` schema itself: `version: 2`, `build.os`, `build.tools.python`,
`build.apt_packages`, `build.jobs.build.pdf`, `sphinx.configuration`, `python.install` (native
`method: uv`), and `formats:` are all settled at HIGH confidence by the milestone's own prior research
(STACK.md, ARCHITECTURE.md) against RTD's official config-file-v2 and environment-variables reference
pages. This research does not re-derive any of that; it fills the one thing genuinely missing — a
phase-specific Validation Architecture that classifies all 4 ROADMAP success criteria into
machine-verifiable-now / machine-verifiable-only-live / `human_needed`.

Two facts newly confirmed in this research session (not previously pinned down in the milestone
research): (1) `$READTHEDOCS_OUTPUT` expands to `<checkout>/_readthedocs/` — the format subdirectory
(`pdf/`) is **not** pre-created by RTD, so the `build.jobs.build.pdf` script **must** `mkdir -p
$READTHEDOCS_OUTPUT/pdf/` itself before copying into it [CITED: docs.readthedocs.com environment-variables
reference, corroborating the same claim already made in STACK.md's example]. (2) The raw build log is
reached via each build's own detail page (`https://readthedocs.org/projects/<slug>/builds/<build-id>/`
or the newer `app.readthedocs.org` host) — click "View raw" for the plain-text log
[CITED: readthedocs.org build detail pages, cross-checked against two live example URLs].

**Primary recommendation:** Land `.readthedocs.yaml` in the two D-06 commits exactly as scoped, write
one new local pytest file asserting the YAML's shape and the `conf.py` seam's env-var-precedence
behavior (Wave 0 gap, both machine-verifiable-now), and treat every criterion that requires a live RTD
project or a downloaded artifact as machine-verifiable-only-live — do not attempt to fabricate a local
substitute for either.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| RTD build manifest (`.readthedocs.yaml`) | Build/CI config | — | Read only by RTD's own build orchestrator; not part of the Python package or the Sphinx extension runtime |
| `language` conf seam (`conf.py:51`) | Docs build config (Sphinx `conf.py`) | — | `conf.py` is Sphinx configuration, explicitly documentation not runtime per milestone invariant #3; consumed identically by RTD's `sphinx:` HTML step and the `build.jobs.build.pdf` override |
| PDF generation (`build.jobs.build.pdf`) | RTD build sandbox (ephemeral CI-like container) | Database/Storage (`$READTHEDOCS_OUTPUT/pdf/`, RTD's own storage) | typsphinx's `typstpdf` builder runs inside RTD's build container, an isolated build tier distinct from both the published HTML tier and this repo's own GitHub Actions CI tier |
| Published English HTML (`/en/latest/`) | CDN/Static (RTD's own hosting) | — | RTD serves static built HTML; no server-side app tier exists here |
| Fallback PDF link (D-08, Branch B) | Docs content (`index.rst`, `README.md`) | External static hosting (GitHub Releases CDN) | A documentation-content edit pointing at an artifact hosted entirely outside this phase's build pipeline |
| Owner-manual RTD project setup | Human/web-UI (RTD dashboard) | — | No `.readthedocs.yaml` key represents project creation, GitHub connection, Admin Language, or Default Version — all outside any tier this repo controls |

## Standard Stack

### Core

| Component | Version/Value | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| `.readthedocs.yaml` schema | `version: 2` | RTD's sole build manifest | Mandatory since 2023-09-25; v1 long removed [CITED: STACK.md, docs.readthedocs.com/platform/stable/config-file/v2.html] |
| `build.os` | `ubuntu-24.04` | RTD builder OS image | Currently-valid enum value (`ubuntu-22.04`/`24.04`/`26.04`/`ubuntu-lts-latest`); pin explicit, not `-lts-latest`, for reproducibility [CITED: STACK.md, docs.readthedocs.io/en/latest/intro/sphinx.html] |
| `build.tools.python` | `"3.12"` | Python interpreter RTD provisions | Discretion item, confirmed here: matches `docs.yml`'s `actions/setup-python@v6` `python-version: "3.12"` (verified by reading `.github/workflows/docs.yml:24` this session) so the D-12 baseline comparison is same-Python-minor on both sides [VERIFIED: repo grep] |
| `build.apt_packages` | `[fonts-noto-cjk]` | CJK font coverage for D-10 | Top-level key under `build:`, sibling of `os`/`tools`/`jobs` [CITED: STACK.md's config-file-v2 citation covers this key's existence; the CJK-need itself is D-10, locked by CONTEXT.md] |
| `build.jobs.build.pdf` | shell command list | Overrides only the PDF format step | RTD's docs state the override *replaces* the default LaTeX step for that format — does not run alongside it [CITED: STACK.md/ARCHITECTURE.md, docs.readthedocs.com/platform/stable/build-customization.html] |
| `sphinx.configuration` | `docs/source/conf.py` | Points RTD's own HTML step at the existing conf.py | Unambiguous single key; matches `tox.ini`'s `changedir = docs` + `source` layout |
| `python.install` | `method: uv`, `command: sync`, `extras: [docs]` | Installs typsphinx itself (editable, from the checked-out commit) + the `docs` extra | RTD-native `uv` support; `extras:` (not `groups:`) is correct because this repo's `docs` group is a classic `[project.optional-dependencies]` entry, not a PEP 735 `[dependency-groups]` entry — confirmed by reading `pyproject.toml:33,48-52` this session [VERIFIED: repo grep + STACK.md] |
| `formats: [pdf]` | list | Required whenever `build.jobs.build.pdf` is overridden | "If any of the pdf, epub, or htmlzip steps are overridden, they should be included in the formats list" [CITED: STACK.md quoting docs.readthedocs.com/platform/stable/config-file/v2.html] |

No new Python packages of any kind. `pypdf>=6.14,<7` needed for D-12 is already in the `dev` extra
[VERIFIED: `pyproject.toml:46` this session].

### Supporting

Not applicable — this phase adds zero runtime or dev dependencies (milestone invariant #1). The only
new "package" is the Ubuntu system package `fonts-noto-cjk` (D-10), an RTD build-environment artifact,
not a Python-ecosystem package — see Package Legitimacy Audit below for why it is out of scope for the
npm/pypi/crates gate.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `python.install: method: uv` (native) | `build.jobs` manual `asdf`+`uv venv` workaround | Superseded; RTD's own docs call this the pre-native-support pattern. Only use if a future need exceeds what `method: uv`'s schema exposes — not the case here |
| Explicit `build.os: ubuntu-24.04` | `build.os: ubuntu-lts-latest` | `-lts-latest` auto-advances the OS image with no corresponding repo commit — riskier for a phase whose whole point is observing a specific build's log |
| `build.apt_packages: [fonts-noto-cjk]` | Wait and see if RTD's image happens to have CJK coverage | Rejected by D-10 — measured, not hypothetical: the English docs already need CJK glyphs and Typst's fallback is silent |

**Installation:** No `pip install`/`uv add` step changes. `.readthedocs.yaml` is the only new file; see
Code Examples for its exact contents.

**Version verification:** No new package versions to verify against a registry — `typst>=0.15.0,<0.16`
is unchanged (already pinned in `pyproject.toml`), and `build.apt_packages: fonts-noto-cjk` is an
Ubuntu `apt` package name (Noto CJK font family), not something `npm view`/`pip index versions` can
check — its existence is confirmed by it being Ubuntu's standard CJK metapackage name, used widely in
Debian/Ubuntu documentation-build contexts. Flagged here as [ASSUMED] rather than independently
apt-cache-searched during this research session — the planner should have the executor run
`apt-cache search fonts-noto-cjk` or equivalent inside the RTD build (a `build.jobs.post_system_dependencies`
diagnostic step, or simply observe whether `apt_packages` install succeeds in the raw log) as part of
Branch A's first PDF-enabling build, since a wrong package name would surface immediately as an
`apt-get install` failure in that log.

## Package Legitimacy Audit

**Not applicable in the standard sense.** This phase installs zero new Python/npm/crates packages —
the `package-legitimacy check` seam (npm/pypi/crates registries) has no artifact to check. The one new
external name introduced is `fonts-noto-cjk`, an **Ubuntu apt package**, outside any ecosystem the
Package Legitimacy Gate protocol covers. It is not silently trusted, though: its correctness is
verifiable the moment Branch A's PDF-enabling build runs (a bad package name fails `apt-get install`
loudly in the raw build log, which D-07/SC#2 already requires reading end-to-end). No `checkpoint:
human-verify` task is warranted beyond that — reading the raw log is already a locked, mandatory step.

**Packages removed due to [SLOP] verdict:** none (no packages to check).
**Packages flagged as suspicious [SUS]:** none.

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  GitHub repo (this phase's 2 commits)                            │
│  .readthedocs.yaml (NEW)  ·  docs/source/conf.py (language seam) │
└───────────────┬───────────────────────────────────────────────┬─┘
                │ RTD webhook (push to main)                    │ existing GitHub Actions
                ▼                                                ▼
   ┌──────────────────────────────┐              ┌──────────────────────────────┐
   │ RTD "typsphinx" project (en) │              │ docs.yml (UNTOUCHED this phase)│
   │  Commit 1: HTML-only build   │              │  tox -e docs-pdf regression   │
   │   sphinx: → sphinx-build -b  │              │  gate; tag-time Release PDF   │
   │   html (RTD default)         │              │  attachment                   │
   │  → serves /en/latest/        │              └──────────────────────────────┘
   │  Commit 2: + formats:[pdf]   │
   │   + build.jobs.build.pdf:    │              Branch A (egress OK):
   │    sphinx-build -b typstpdf  │  ──────────►  PDF downloaded from RTD's Downloads
   │    → tmp dir → filter *.pdf  │               menu, content-compared to the
   │    → $READTHEDOCS_OUTPUT/pdf/│               tox -e docs-pdf baseline (D-12)
   └──────────────┬────────────────┘
                  │ raw build log (D-07 evidence)
                  ▼
        "View raw" on the build's detail page
        (readthedocs.org/projects/<slug>/builds/<id>/)
                  │
        ┌─────────┴──────────┐
        ▼                     ▼
  @preview resolves,     @preview fetch blocked
  0 latexmk/.tex lines   (registry unreachable)
  → Branch A             → Branch B: docs link to
                            releases/latest/download/
                            typsphinx.pdf (D-08, already
                            measured 200/1,678,961 bytes)
```

A reader's primary path: push to `main` → RTD webhook fires → `.readthedocs.yaml` drives the build →
`/en/latest/` is fetched over real HTTP (SC#1/SC#4) → the same build's raw log is read for the
install-provenance line (SC#1) and the `@preview` verdict (SC#2) → depending on the branch, either the
downloaded PDF is content-compared (SC#3 Branch A) or the fallback Release-PDF link is fetched over
real HTTP (SC#3 Branch B).

### Recommended Project Structure

```
.readthedocs.yaml          # NEW — repo root, RTD's sole build manifest
docs/source/conf.py        # MODIFIED — language seam only (2-line change at :51)
docs/source/index.rst      # MODIFIED only if Branch B (D-08 fallback link, Quick Links section)
README.md                  # MODIFIED only if Branch B (D-08/D-09 small additive block)
tests/
└── test_readthedocs_config.py   # NEW (Wave 0 gap) — local, machine-verifiable-now checks
```

### Pattern 1: Two-Commit Sequencing (D-06)

**What:** Land `.readthedocs.yaml` with HTML-only config first (no `formats:`, no
`build.jobs.build.pdf`), confirm green + `/en/latest/` serving, THEN add the PDF override in a
separate commit.
**When to use:** Any RTD onboarding where an unproven build step (here: the `@preview` network-egress
unknown) could fail and you don't want that failure to also take down the already-working HTML site's
verification story.
**Example:**
```yaml
# Commit 1 — .readthedocs.yaml (HTML only)
version: 2
build:
  os: ubuntu-24.04
  tools:
    python: "3.12"
sphinx:
  configuration: docs/source/conf.py
python:
  install:
    - method: uv
      command: sync
      extras:
        - docs
```
```yaml
# Commit 2 — same file, PDF override added
version: 2
build:
  os: ubuntu-24.04
  tools:
    python: "3.12"
  apt_packages:
    - fonts-noto-cjk
  jobs:
    build:
      pdf:
        - mkdir -p /tmp/typst-pdf-build/doctrees
        - sphinx-build -b typstpdf -d /tmp/typst-pdf-build/doctrees docs/source /tmp/typst-pdf-build/out
        - mkdir -p $READTHEDOCS_OUTPUT/pdf/
        - cp /tmp/typst-pdf-build/out/*.pdf $READTHEDOCS_OUTPUT/pdf/
sphinx:
  configuration: docs/source/conf.py
formats:
  - pdf
python:
  install:
    - method: uv
      command: sync
      extras:
        - docs
```
[CITED: STACK.md's worked example, adapted here for D-04's temp-dir-then-copy pattern and D-10's
`apt_packages`; the `mkdir -p $READTHEDOCS_OUTPUT/pdf/` line is required per this session's confirmed
finding that `$READTHEDOCS_OUTPUT/pdf/` is not pre-created — see Common Pitfalls #5]

### Pattern 2: The `language` Seam

**What:** `conf.py:51` layers `READTHEDOCS_LANGUAGE` in front of the existing `SPHINX_LANGUAGE`
fallback chain.
**When to use:** Any Sphinx project served by both RTD's own per-project Language setting and a
pre-existing local/CI env-var mechanism.
**Example:**
```python
# Source: pattern confirmed in ARCHITECTURE.md, verified against conf.py:51 this session
language = os.getenv("READTHEDOCS_LANGUAGE", os.getenv("SPHINX_LANGUAGE", "en"))
```
Locally and in `docs.yml`, both env vars are unset → falls through to `"en"`, identical to today's
behavior — a zero-behavior-change edit outside RTD [VERIFIED: repo grep confirms `SPHINX_LANGUAGE`'s
only producer, `build_multilang.py:44`, is unrelated to this phase and untouched here].

### Anti-Patterns to Avoid

- **`formats: [pdf]` without the `build.jobs.build.pdf` override:** activates RTD's own LaTeX pipeline
  — a silently different, undogfooded PDF. Settled fact, not a judgment call [CITED: STACK.md].
- **Pointing `sphinx-build -b typstpdf` directly at `$READTHEDOCS_OUTPUT/pdf/`:** the builder writes 31
  files there (measured); only the PDF belongs in RTD's download area (D-04).
- **Wrapping `build.jobs` commands in `tox -e docs-*`:** RTD's `python.install` step already
  provisions an equivalent environment; nesting tox creates a redundant second venv and needs `uv
  sync --locked` semantics the RTD image doesn't natively wire into a nested tox-uv runner
  [CITED: ARCHITECTURE.md's "RTD vs tox" analysis]. CLAUDE.md's own guidance repeats this explicitly.
- **Setting Default Version = `stable` at project-creation time:** `stable` cannot exist until the
  `v0.6.4` tag builds green; RTD's root redirect targets Default Version even for a non-existent
  version. Leave at `latest` (RTD-04, D-per-ROADMAP "RTD-04 ownership").

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| PDF content comparison (D-12) | A committed comparison script in the repo | A one-off hand-run sequence (page count via `pypdf`, text extraction via `pypdf`, font-list enumeration via `pypdf`), commands + output pasted into `29-VERIFICATION.md` | D-15 explicitly rejects a committed script — the RTD-built PDF is unreachable from CI, so a committed script would never run automatically and would only look like a gate that isn't one |
| Detecting tofu/glyph substitution | An automated pixel-diff or OCR check | The owner opening the two affected pages and confirming visually (D-12 check 4) | D-14: text-extraction equality cannot detect glyph substitution (tofu still extracts correct characters) — this is a case where the honest answer is `human_needed`, not a heavier automated check |
| RTD project/version/translation setup | Any script or API automation attempting to script RTD dashboard actions | Owner-manual web-UI steps, tracked as an explicit checklist with no automated acceptance criterion | No `.readthedocs.yaml` key represents project creation, Admin Language, or Default Version — these live purely in RTD's database via its web UI [CITED: FEATURES.md] |

**Key insight:** Every "don't hand-roll" item in this phase is really "don't fabricate a machine check
where only a human or a live network fetch can honestly answer" — the project's own standing
verification culture (STATE.md: honest `human_needed` abstention over unevidenced assertion) applies
directly here.

## Common Pitfalls

### Pitfall 1: `formats:`/`build.jobs.build.pdf` mismatch
**What goes wrong:** Declaring `formats: [pdf]` without the job override silently activates RTD's own
LaTeX pipeline instead of `typstpdf`.
**Why it happens:** RTD's default PDF path exists and looks like the zero-config option.
**How to avoid:** Always land both together, exactly as in Pattern 1's Commit 2.
**Warning signs:** The raw build log shows `latexmk`/`pdflatex`/`.tex` lines — this is precisely what
D-07/SC#2 requires checking for.

### Pitfall 2: RTD never installs the project package by default
**What goes wrong:** Without `python.install`, `conf.py`'s `extensions = [..., "typsphinx"]` either
fails with `ModuleNotFoundError` or — worse, silently — resolves a stale PyPI wheel instead of the
in-repo commit (exactly the SC#1 failure mode).
**Why it happens:** RTD's zero-config Sphinx build only installs what `sphinx.configuration` needs to
import, not the project itself, unless `python.install` says so.
**How to avoid:** `python.install: method: uv, command: sync, extras: [docs]` — `uv sync` installs the
workspace-root project (typsphinx) editable, from the checked-out commit, as part of the sync.
**Warning signs:** SC#1 explicitly requires reading the raw log for the install-provenance line rather
than trusting a green build status — see Open Questions #1 for the exact wording uncertainty.

### Pitfall 3: `$READTHEDOCS_OUTPUT/pdf/` not pre-created
**What goes wrong:** `cp *.pdf $READTHEDOCS_OUTPUT/pdf/` fails if the `pdf/` subdirectory doesn't
exist yet.
**Why it happens:** `$READTHEDOCS_OUTPUT` expands to `<checkout>/_readthedocs/` — the format
subdirectory is created by RTD's own post-build ingestion, not pre-provisioned before your job runs
[CITED: docs.readthedocs.com environment-variables reference, this session's search].
**How to avoid:** `mkdir -p $READTHEDOCS_OUTPUT/pdf/` as an explicit step before the `cp`.
**Warning signs:** A `cp: cannot create regular file … No such file or directory` line in the raw log.

### Pitfall 4: Default Version flipped too early
**What goes wrong:** Setting Default Version = `stable` before the `v0.6.4` tag exists means RTD's
root-URL redirect targets a version that doesn't exist — a broken root for the rest of the migration
window, directly violating RTD-04.
**Why it happens:** It's tempting to set the "final" value once during initial project setup.
**How to avoid:** Leave Default Version = `latest` through this entire phase (and the whole
milestone); the flip is an explicit Phase 33 owner-manual step, already documented in ROADMAP.md.
**Warning signs:** None locally observable — this is exactly why SC#4 requires a real HTTP fetch of the
root URL, not a read of the dashboard setting.

### Pitfall 5: Treating a green build as proof of content correctness
**What goes wrong:** RTD-02's failure mode (font substitution) and I18N-01's failure mode (Japanese
project rendering English) both present as **successful** builds (REQUIREMENTS.md invariant #7).
**Why it happens:** Typst's font fallback is silent by design — no warning, no error.
**How to avoid:** D-12's four-check bar (page count, text, CJK-font-coverage, human tofu-check) — never
substitute a build-status check for it.
**Warning signs:** A build log with zero errors is not evidence of anything beyond "the compile step
exited 0."

## Code Examples

### Recommended `.readthedocs.yaml` (Commit 2, PDF-enabled state)

```yaml
# Source: STACK.md's worked example, extended for D-04 (temp-dir-then-copy) and D-10
# (build.apt_packages) — both this phase's locked decisions, not present in the milestone-level
# example. `build.tools.python: "3.12"` per Claude's Discretion, confirmed against
# .github/workflows/docs.yml:24's python-version: "3.12" this session.
version: 2

build:
  os: ubuntu-24.04
  tools:
    python: "3.12"
  apt_packages:
    - fonts-noto-cjk
  jobs:
    build:
      pdf:
        - mkdir -p /tmp/typst-pdf-build/doctrees
        - sphinx-build -b typstpdf -d /tmp/typst-pdf-build/doctrees docs/source /tmp/typst-pdf-build/out
        - mkdir -p $READTHEDOCS_OUTPUT/pdf/
        - cp /tmp/typst-pdf-build/out/*.pdf $READTHEDOCS_OUTPUT/pdf/

sphinx:
  configuration: docs/source/conf.py

formats:
  - pdf

python:
  install:
    - method: uv
      command: sync
      extras:
        - docs
```

**Uncertain spellings, flagged explicitly rather than guessed:**
- The `-d /tmp/.../doctrees` flag for `sphinx-build` is the standard `-d <doctree-path>` option
  (separates the doctree cache from the output tree, matching `tox.ini`'s implicit
  `docs/_build/pdf/.doctrees` layout) — this is a real Sphinx CLI flag [VERIFIED: standard Sphinx
  `sphinx-build --help` surface, not RTD-specific], not RTD-specific syntax, so confidence here is
  independent of RTD's own docs.
- The temp-directory path `/tmp/typst-pdf-build` is an arbitrary, discretionary name (explicitly
  delegated to planning per CONTEXT.md) — any RTD-build-writable path works; `/tmp/` is writable in
  RTD's build sandbox per general Linux container conventions, but this specific claim about RTD's
  sandbox is [ASSUMED] rather than independently confirmed against an RTD source this session — the
  first Branch-A build's raw log is the actual confirmation point (a `mkdir`/`permission denied` would
  surface immediately).

### `conf.py:51` seam

```python
# Source: ARCHITECTURE.md's recommended seam design, cross-checked against conf.py:51 this session
language = os.getenv("READTHEDOCS_LANGUAGE", os.getenv("SPHINX_LANGUAGE", "en"))
```

### D-08 fallback block (Branch B only — index.rst Quick Links)

```rst
.. Source: pattern matches the existing Quick Links list at docs/source/index.rst:24-29,
   verified this session (GitHub Repository / PyPI Package / Issue Tracker bullets already present)
- **Download PDF** (typst-built, always current): https://github.com/YuSabo90002/typsphinx/releases/latest/download/typsphinx.pdf
```
Do not build this block preemptively — it only lands if Branch B is taken (D-07's recorded log
excerpt determines the branch).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (already configured — `pyproject.toml [tool.pytest.ini_options]`, `testpaths = ["tests"]`) |
| Config file | `pyproject.toml` (no separate pytest.ini) |
| Quick run command | `pytest tests/test_readthedocs_config.py -x` |
| Full suite command | `pytest` |

No new test framework needed. This phase's local checks are ordinary pytest functions; the live checks
(HTTP fetches, raw-log reads, PDF downloads) are **not** pytest-suite members — they are one-off
commands run by hand and recorded verbatim in `29-VERIFICATION.md` per D-15, exactly as the milestone's
own decisions require. Do not wrap them in a committed pytest fixture that "passes" against a live RTD
endpoint — that would create a flaky, unreproducible, hidden network dependency inside the otherwise
hermetic test suite, and D-15 already rejected the analogous idea for the PDF-comparison script.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| RTD-01 (partial) | `.readthedocs.yaml` is valid YAML with the required v2 keys (`version`, `build.os`, `build.tools.python`, `sphinx.configuration`, `python.install`) | unit | `pytest tests/test_readthedocs_config.py::test_readthedocs_yaml_shape -x` | ❌ Wave 0 |
| RTD-01 (partial) | `conf.py`'s `language` seam resolves to `"en"` when both env vars are unset, and to each env var's value when set, with `READTHEDOCS_LANGUAGE` taking precedence over `SPHINX_LANGUAGE` | unit | `pytest tests/test_readthedocs_config.py::test_language_seam_precedence -x` | ❌ Wave 0 |
| RTD-01 (live half) | `/en/latest/` serves real content; raw build log shows local-checkout install, not a PyPI resolve | **live-fetch, `human_needed` for the log read** | real HTTP GET recorded in `29-VERIFICATION.md`; raw log excerpt pasted verbatim | N/A — no test file, live evidence only |
| RTD-02 | Branch A: downloaded PDF page-count + text match the `tox -e docs-pdf` baseline; embeds a CJK-coverage font | **live, one-off (D-15)** | `pypdf` commands run by hand, output pasted into `29-VERIFICATION.md` — **not** a committed script | N/A by design (D-15) |
| RTD-02 (check 4) | No tofu on the two CJK-bearing pages | **`human_needed`** | Owner visually confirms; recorded as such, not asserted machine-verified | N/A |
| RTD-03 Branch B | `releases/latest/download/typsphinx.pdf` resolves over real HTTP | **live-fetch** (works today, independent of RTD's existence — see Open Questions) | `curl -sI` or equivalent, output recorded | N/A |
| RTD-04 | Root URL fetch lands on a version that exists and serves content | **live-fetch** | real HTTP GET, recorded per-phase (this phase) and re-fetched by Phases 30–32 per the standing invariant | N/A |

### Sampling Rate

- **Per task commit:** `pytest tests/test_readthedocs_config.py -x` (the two local, machine-verifiable
  checks — fast, no network).
- **Per wave merge:** `pytest` (full suite — confirms nothing else in the repo regressed; this phase
  touches no `typsphinx/` code, so the bar is "suite stays exactly as green as before").
- **Phase gate:** Full suite green **plus** the live-fetch/raw-log evidence recorded in
  `29-VERIFICATION.md` per D-15's "commands + output pasted verbatim" requirement — the automated
  suite alone cannot certify this phase; the live evidence is load-bearing and mandatory.

### Wave 0 Gaps

- [ ] `tests/test_readthedocs_config.py` — new file. Two tests: (1) parse `.readthedocs.yaml` with
  PyYAML (already available transitively via `sphinx`'s own dependency chain — verify with `python -c
  "import yaml"` before relying on it, or use `tomllib`-style manual key checks if PyYAML isn't
  importable outside a build context) and assert the required v2 keys are present with the correct
  nesting; (2) monkeypatch `os.environ` to unset/set `READTHEDOCS_LANGUAGE`/`SPHINX_LANGUAGE` in
  combination and assert `conf.py`'s resolved `language` value — this likely needs `importlib.reload`
  of a minimal extracted seam or a small `docs/source/conf.py`-local helper function, since `conf.py`
  itself is not an importable module in the normal pytest path (Sphinx's own test fixtures load it via
  `sphinx.testing.fixtures`, not a plain `import`). **Recommend factoring the one-line seam into a
  tiny testable expression** rather than building a full `sphinx.testing` app fixture just to assert
  an `os.getenv` chain — keep this test cheap.
- [ ] No `conftest.py` changes needed — this phase adds no new fixture requirements beyond what
  `tests/roots/` already provides.
- [ ] Framework install: none — pytest, PyYAML (if used), and `pypdf` are all already available.

## Runtime State Inventory

Not applicable — this is not a rename/refactor/migration phase in the STATE-Inventory sense (no
renamed identifiers, no data migration). The "state" this phase creates (an RTD project, its build
history, its DNS-served pages) is genuinely new, not a rename of anything pre-existing, and is entirely
owner-manual/RTD-side — there is no runtime datastore, OS-registered task, or secret this repo owns
that references an old name needing updating. `SPHINX_LANGUAGE` is not renamed or removed by this
phase — it stays as the fallback layer; only a new preferred layer (`READTHEDOCS_LANGUAGE`) is added in
front of it.

## Security Domain

`security_enforcement: true` per `.planning/config.json`. This phase's diff is a build-manifest file
and a two-line docs-config seam — the security surface is narrow, but not zero (a `.readthedocs.yaml`
`build.jobs` block executes arbitrary shell commands inside RTD's build container, and this phase adds
a new outbound-network dependency, the `@preview` package fetch, whose egress policy is the milestone's
own named open question).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V1 Architecture | Marginal | The two-build-path architecture (RTD vs. GitHub Actions, ARCHITECTURE.md) keeps the PR-blocking regression gate (`tox -e docs-pdf`) independent of the async, non-blocking RTD build — a deliberate defense against a broken pipeline reaching `main` undetected |
| V2 Authentication | No | No auth surface touched; RTD's GitHub OAuth connection is entirely owner-manual dashboard work, outside this repo's diff |
| V3 Session Management | No | Not applicable — no session-bearing code in this phase |
| V4 Access Control | No | Not applicable — publishing is public documentation by design |
| V5 Input Validation | No | `.readthedocs.yaml` is a static, maintainer-authored config file, not user input; no untrusted input is parsed by anything this phase adds |
| V6 Cryptography | No | Not applicable |
| V14 Configuration | Yes | `build.jobs` shell commands are maintainer-authored, not templated from any variable input, so there is no injection surface — but `build.apt_packages: [fonts-noto-cjk]` **is** a new supply-chain trust point (an Ubuntu apt package fetched from RTD's own build image's apt mirror at build time) worth naming even though it's out of scope for the npm/pypi Package Legitimacy Gate |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Supply-chain risk: `@preview` Typst packages fetched from `packages.typst.org` on a cold cache during the RTD build | Tampering (unpinned-at-fetch-time third-party content) | Already mitigated at the milestone level — the 4 `@preview` packages are pinned by exact version across `writer.py`/`template_engine.py`/`templates/base.typ`/`examples/**/*.typ` (the 4-surface version-sync guard), so even if the fetch succeeds, the *version* fetched is deterministic; this phase adds no new unpinned fetch |
| A malicious/compromised `build.jobs` command silently exfiltrating repo secrets during an RTD build | Information Disclosure | Out of scope for this phase's authored commands (all are read-only `sphinx-build`/`cp`/`mkdir` — no secrets are referenced or need to be); note for future phases: RTD build logs are public for a public project, so no secret should ever be echoed into a `build.jobs` command |
| Silent font-fallback producing a PDF that looks correct but has substituted glyphs (RTD-02's own named failure mode) | Tampering (content-level, not security-classical, but the project's own REQUIREMENTS.md invariant #7 treats it with equivalent rigor) | D-12's four-check comparison bar — already locked, not this research's to redesign |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|----------------|
| A1 | `fonts-noto-cjk` is a valid, installable Ubuntu apt package name on RTD's `ubuntu-24.04` image | Standard Stack / Code Examples | If wrong, `apt-get install` fails loudly in the raw build log during Branch A's PDF-enabling commit — self-correcting, low risk, but the planner should not assume success without checking that log line |
| A2 | `/tmp/` is writable inside RTD's build sandbox for a `build.jobs.build.pdf` intermediate output directory | Code Examples | If wrong, the `mkdir`/`sphinx-build` step fails immediately and visibly in the raw log — again self-correcting; alternative would be a path under `$READTHEDOCS_OUTPUT` itself or the checkout's own working directory |
| A3 | `uv sync`'s log output for a local/editable install includes a distinguishing marker (e.g. a `file://`-scheme source or a "Built <pkg> @ file://…" line) that differs visibly from a PyPI-resolved install, satisfying SC#1's "not resolved from a PyPI index" bar | Open Questions #1 | If the exact log wording differs from what's assumed here, the planner/executor may need to adjust what string SC#1's verification step actually greps for — this should be confirmed against the very first real RTD build log, not assumed in advance |
| A4 | The raw build log is reached via a build-detail-page "View raw" link at a URL of the shape `readthedocs.org/projects/<slug>/builds/<build-id>/` (or the `app.readthedocs.org` host) | Summary | Low risk — this is dashboard navigation, not something the plan encodes as a command; worst case the owner finds the raw-log link via a slightly different UI path than described here |

**If this table is empty:** N/A — see rows above.

## Open Questions

1. **Exact raw-build-log wording distinguishing a local-checkout install from a PyPI resolve.**
   - What we know: `uv sync` on a workspace-root project builds/installs it from the local
     filesystem path, and general `uv` behavior distinguishes a locally-built package (a "Built
     <pkg> @ file://…" or equivalent local-path-annotated line) from a registry-resolved one (a
     "Downloading <pkg>-<version>-py3-none-any.whl" line) — this is consistent with `uv`'s documented
     resolver/installer behavior, but was not verified against an actual RTD build log during this
     research session (none exists yet — the RTD project has not been created).
   - What's unclear: The precise string(s) SC#1's verification step should grep for in the real log.
   - Recommendation: Treat SC#1's "not resolved from a PyPI index" check as `human_needed`/live-read
     for its first execution — read the actual log, identify the exact distinguishing line, and record
     it in `29-VERIFICATION.md`. Do not pre-commit to a specific grep pattern in the plan; let the
     first real build's log dictate the exact wording.

2. **`apt_packages` `fonts-noto-cjk` — does it need `scan-fonts` cooperation from typst-py, or is
   embedding automatic?**
   - What we know: `typst-py`'s embedded feature set has no CJK coverage (settled, SUMMARY.md); its
     `scan-fonts` feature (also enabled per STACK.md's Cargo.toml citation) means it *additionally*
     looks for system fonts if present. `fonts-noto-cjk` installed via `apt` should register as a
     system font discoverable by `scan-fonts`.
   - What's unclear: Whether any Typst-side font-cache invalidation or explicit `--font-path` wiring
     is needed for a freshly-`apt`-installed font to be picked up mid-build, or whether `scan-fonts`
     finds it automatically with zero extra configuration.
   - Recommendation: This is exactly what D-12 check 3 (CJK-coverage font enumeration via `pypdf`)
     tests empirically — if the embedded-font list from the RTD-built PDF shows no CJK-coverage font
     despite `fonts-noto-cjk` being installed, that is itself the actionable signal, not something to
     pre-solve here.

3. **Does the second (`formats: [pdf]`) commit trigger a clean full rebuild, or could a stale
   HTML-only build state interfere?**
   - What we know: RTD builds are triggered fresh per-commit by its webhook; there is no documented
     "incremental build" caching behavior that would carry over stale artifacts between the two D-06
     commits (each commit is a distinct, independent build).
   - What's unclear: Nothing found suggesting this is a risk — flagged only because CONTEXT.md's task
     brief explicitly asked about it and no evidence surfaced a failure mode here.
   - Recommendation: No special handling needed; the two-commit sequencing (D-06) works as designed.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|----------|----------|
| RTD account + GitHub connection (owner-manual) | All of Phase 29's live verification | ✗ (not this repo's to check) | — | None — this is the phase's own first prerequisite, tracked as an owner-manual step, not a code fallback |
| `pypdf` | D-12 page-count/text/font checks | ✓ | `>=6.14,<7` (already in `dev` extra) [VERIFIED: `pyproject.toml:46`] | — |
| `uv` | `python.install: method: uv` on RTD; local dev already uses it | ✓ locally (this repo's whole workflow is `uv`-based per CLAUDE.md); RTD provisions its own per `python.install: method: uv` | — | — |
| Network egress from RTD's build sandbox to `packages.typst.org` | Branch A (PDF via typstpdf) | **UNKNOWN — the milestone's own named open question** | — | Branch B: `releases/latest/download/typsphinx.pdf` (already measured 200, 1,678,961 bytes — works today, independent of RTD) |

**Missing dependencies with no fallback:** none — even the one genuinely unresolved dependency
(`@preview` network egress) has a pre-agreed, already-measured fallback (Branch B).

**Missing dependencies with fallback:** `@preview` package registry access from inside RTD's build
sandbox — see above.

## Sources

### Primary (HIGH confidence)
- `.planning/research/STACK.md` — `.readthedocs.yaml` v2 schema, `python.install: method: uv`,
  `formats:`/`build.jobs.build.pdf` pairing, typst-py wheel/font settlement — all sourced from
  `docs.readthedocs.com/platform/stable/config-file/v2.html` and
  `docs.readthedocs.com/platform/stable/build-customization.html`.
- `.planning/research/ARCHITECTURE.md` — two-build-path system diagram, `language` seam design,
  RTD-vs-tox non-wrapping rationale, `$READTHEDOCS_LANGUAGE` env var citation.
- `.planning/research/FEATURES.md` — owner-manual step list, Default-Version sequencing rationale.
- `.planning/research/SUMMARY.md` — the `@preview` egress un-researchable blocker, ranked above the
  wheel/font questions; the "settled, do not re-open" list.
- `docs.readthedocs.com/platform/stable/reference/environment-variables.html` — this session's search
  confirms `$READTHEDOCS_OUTPUT` expands to `<checkout>/_readthedocs/` and format subdirectories are
  not pre-created — the `mkdir -p $READTHEDOCS_OUTPUT/pdf/` requirement (Common Pitfalls #3).
- Repo files read directly this session: `docs/source/conf.py`, `pyproject.toml`, `tox.ini`,
  `.github/workflows/docs.yml`, `docs/source/index.rst` (Quick Links section) — all file:line facts
  in this document marked [VERIFIED: repo grep] were re-confirmed by direct read in this session, not
  merely inherited from prior research.

### Secondary (MEDIUM confidence)
- readthedocs.org build-detail-page URL shape (`/projects/<slug>/builds/<build-id>/`, "View raw"
  link) — confirmed via two live example project URLs found in this session's search, not an official
  reference page explicitly documenting the URL shape.

### Tertiary (LOW confidence, corroborating only)
- `uv sync`'s exact log-line distinguishing a local/editable install from a PyPI resolve — general `uv`
  documentation on local-vs-registry dependency handling, not a directly observed RTD build log (none
  exists yet). See Open Questions #1 and Assumptions Log A3.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — inherited from the milestone's own already-fetched official-docs research,
  cross-checked against this session's direct repo reads (conf.py, pyproject.toml, tox.ini, docs.yml).
- Architecture: HIGH for repo-internal facts; MEDIUM for RTD platform behavior generally (official
  docs cited, not independently re-verified against a live build in this session).
- Pitfalls: HIGH — all five are either already-settled milestone facts or newly-confirmed this session
  ($READTHEDOCS_OUTPUT pre-creation).
- Validation Architecture (this research's primary deliverable): HIGH for the local/machine-verifiable
  classification; explicitly LOW/`human_needed` where the phase's own locked decisions (D-15) already
  require that classification — this is honest alignment with the locked decisions, not a gap.

**Research date:** 2026-07-25
**Valid until:** Effectively the life of this phase (RTD's config schema is stable; the one thing this
research cannot pre-validate — actual RTD build behavior — expires the moment the first real build
runs and either confirms or corrects Assumptions A1–A4).
