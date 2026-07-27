# Phase 29: RTD Build Establishment (English Parent) + PDF Path Decision - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-25
**Phase:** 29-RTD Build Establishment (English Parent) + PDF Path Decision
**Areas discussed:** RTD project slug, PDF output path, `@preview` egress probe order,
glyph-substitution proof

---

## Area selection

Presented four phase-specific gray areas after excluding everything already locked by
PROJECT.md / REQUIREMENTS.md / research (`.readthedocs.yaml` v2 + `python.install: method:
uv` + `extras: [docs]`; `formats: [pdf]` **and** `build.jobs.build.pdf` used together; the
`READTHEDOCS_LANGUAGE` → `SPHINX_LANGUAGE` → `"en"` seam; Default Version pinned to `latest`
through the migration; the `releases/latest/download/` fallback; no `typsphinx/` runtime
change).

| Option | Description | Selected |
|--------|-------------|----------|
| RTD project slug | Irreversible, owner-manual; Phase 31 burns it into every published URL | ✓ |
| PDF output path | Direct build vs. staged copy into `$READTHEDOCS_OUTPUT/pdf/` | ✓ |
| `@preview` egress probe order | One-shot full config vs. HTML-first two-stage | ✓ |
| Glyph-substitution proof | What counts as evidence that no font was silently substituted | ✓ |

**User's choice:** all four.

---

## RTD project slug

### 1. English parent slug

| Option | Description | Selected |
|--------|-------------|----------|
| `typsphinx` | Matches PyPI name and repository name → `https://typsphinx.readthedocs.io/en/latest/` | ✓ |
| `typsphinx-docs` | Avoids name collisions but diverges from the package name | |

**User's choice:** `typsphinx`.
**Notes:** Grounded in a live measurement — `https://typsphinx.readthedocs.io/` returned 404
on 2026-07-25, so the slug appears unclaimed. RTD's import screen remains the authoritative
check.

### 2. Behaviour if the slug is taken

| Option | Description | Selected |
|--------|-------------|----------|
| Stop and consult | Do not create the project; ask the owner for an alternative | ✓ |
| Pre-agree a fallback | Record a second candidate and use it without confirmation | |

**User's choice:** stop and consult.
**Notes:** The URL is not self-service changeable and Phase 31 publishes it, so the owner
wants eyes on the final form rather than fewer round trips.

### 3. Japanese project slug

| Option | Description | Selected |
|--------|-------------|----------|
| Note `typsphinx-ja` now | Record it for Phase 30's owner-manual checklist | |
| Decide in Phase 30 | Leave it to that phase's discussion | ✓ |

**User's choice:** decide in Phase 30.
**Notes:** Recorded as measurement only — `https://typsphinx-ja.readthedocs.io/` also
returned 404 on 2026-07-25.

---

## PDF output path

| Option | Description | Selected |
|--------|-------------|----------|
| Temp dir → copy `*.pdf` only | `$READTHEDOCS_OUTPUT/pdf/` holds just `typsphinx.pdf`; never touches the unconfirmed one-file constraint; `build.jobs` grows to 2–3 lines | ✓ |
| Build directly into the output dir | One command, but 15 `.typ` files and `.doctrees/` land in the published download area | |

**User's choice:** temp dir → copy `*.pdf` only.
**Notes:** Decided against a measurement taken during this discussion — a real
`sphinx-build -b typstpdf` run produced **31 files** (`typsphinx.pdf`, `_template.typ`, 14
`.typ`, and a 16-file `.doctrees/` tree), not the single PDF the direct-build option implies.

---

## `@preview` egress probe order

| Option | Description | Selected |
|--------|-------------|----------|
| HTML-first, two stage | Prove HTML green (RTD-01/RTD-04) first, then add `formats: [pdf]` + the override in a second commit; PDF failure is isolated and the English site never goes dark. Two RTD build cycles | ✓ |
| One-shot with PDF included | Single round trip, but a failing PDF step can take the whole build red and leave `/en/latest/` serving nothing | |

**User's choice:** HTML-first, two stage.
**Notes:** Chosen for RTD-04 safety over round-trip count — the documentation root must land
on a version that exists *at every point during the migration*, not only at the end.

---

## Branch B fallback link placement

| Option | Description | Selected |
|--------|-------------|----------|
| `docs/source/index.rst` only | Reaches documentation readers; avoids colliding with Phase 31's README rewrite | |
| `index.rst` + `README.md` | Both reach paths; the README edit spans two phases | ✓ |
| Decide after Branch B is confirmed | Defer the placement question entirely | |

**User's choice:** both.
**Notes:** The fallback URL was verified live before the question was asked —
`releases/latest/download/typsphinx.pdf` returned HTTP 200 / 1,678,961 bytes on 2026-07-25,
confirming RTD-03's "correct across releases without editing" clause empirically rather than
by inference.

---

## Glyph-substitution proof

### 1. CJK font provisioning

Surfaced mid-discussion as a **new measured risk**, not a pre-identified gray area: the
English documentation itself needs CJK glyphs
(`docs/source/user_guide/configuration.rst:186,240` — 「表 1」「図 1」「图 1」「圖 1」), the
local 93-page PDF embeds host-provided `IPAexGothic` / `NotoSansCJKjp-Thin`, and typst-py's
bundled fonts have no CJK coverage.

| Option | Description | Selected |
|--------|-------------|----------|
| `build.apt_packages: [fonts-noto-cjk]` up front | Deterministic; does not depend on RTD's image happening to ship CJK fonts | ✓ |
| Measure first, then decide | Run the PDF step bare, inspect the embedded-font list, add the package if needed. One extra build cycle | |

**User's choice:** add `fonts-noto-cjk` up front.
**Notes:** Explicitly distinguished from the deferred I18N-03 ("no Japanese PDF") — this is
four CJK strings inside the English docs, and `build.apt_packages` is build-environment
configuration rather than a Python runtime dependency, so the zero-new-runtime-dependencies
invariant is untouched.

### 2. Comparison bar

| Option | Description | Selected |
|--------|-------------|----------|
| Page count + text + CJK coverage | Three mechanical `pypdf` checks, robust to host differences | |
| The above + a human look | Same three checks plus the owner opening the two affected pages | ✓ |

**User's choice:** mechanical checks plus a human look.
**Notes:** "Embedded font list must match exactly" was ruled out *before* being offered — the
local baseline's 9-font list includes four host-provided fonts, so a healthy RTD build cannot
be expected to reproduce it. Text-extraction equality alone was also shown insufficient: a
tofu-rendered PDF still extracts the correct characters.

### 3. Implementation form

| Option | Description | Selected |
|--------|-------------|----------|
| One-off run, log recorded | Commands and output pasted verbatim into `29-VERIFICATION.md` | ✓ |
| Committed comparison script | Available for Phase 32's re-taken gate; adds a repository file | |

**User's choice:** one-off run, log recorded.
**Notes:** The RTD-built PDF is not reachable from CI, so a committed script would never run
automatically and would read as a gate that isn't one.

---

## Claude's Discretion

Delegated explicitly at the close of the discussion:

- `build.os` and `build.tools.python` (recommendation recorded in CONTEXT.md: `ubuntu-24.04`
  + Python `3.12`, matching `docs.yml` so the PDF baseline comparison spans one Python minor).
- Exact `sphinx:` key wording, `python.install` block shape, temp-directory naming, and
  `-d` doctrees placement in the `build.jobs` commands.
- Which specific raw-build-log lines are captured as evidence and how they are formatted.

## Deferred Ideas

- Japanese project slug → Phase 30.
- Default Version `latest` → `stable` flip → Phase 33 owner-manual handoff.
- PR preview builds (RTD-05) → Future; owner-side checkbox, enable any time.
- Japanese PDF (I18N-03) → Future; `fonts-noto-cjk` here is not a step toward it.
- Documentation for pre-`v0.6.4` tags (RTD-06) → structurally impossible.
