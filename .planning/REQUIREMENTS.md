# Requirements: typsphinx v0.6.4 — Read the Docs 移行

**Defined:** 2026-07-25
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered
output — and the documented configuration actually takes effect. For this milestone the same standard
is applied to the *publishing* surface: a URL the project publishes must actually resolve, and the PDF
a reader downloads must be the one typsphinx itself produced.

**Research:** `.planning/research/SUMMARY.md` (2026-07-25) — HIGH confidence overall, with one
genuinely open empirical unknown carried into Phase 1 (`@preview` package network egress inside RTD's
build sandbox).

---

## v1 Requirements

### RTD Hosting (RTD)

- [ ] **RTD-01**: A reader can browse typsphinx's English documentation on Read the Docs, built from a
      `.readthedocs.yaml` in the repository — with typsphinx itself installed from the in-repo commit
      (not a stale PyPI wheel), so `conf.py`'s `extensions = [..., "typsphinx"]` resolves the code
      under test.
- [ ] **RTD-02**: The PDF a reader downloads from Read the Docs is the one typsphinx's own `typstpdf`
      builder produced — not RTD's LaTeX pipeline — and its *content* is verified against the
      `tox -e docs-pdf` CI baseline, not merely its build status.
- [ ] **RTD-03**: If `typst.compile()` cannot reach `packages.typst.org` from inside RTD's build
      sandbox, the documentation instead links to the PDF attached to the GitHub Release, via a URL
      that stays correct across releases without editing.
- [ ] **RTD-04**: A reader who visits the documentation root URL lands on a version that exists and
      serves real content — at every point during the migration, not only at the end.

### Japanese Documentation (I18N)

- [ ] **I18N-01**: A reader can browse the Japanese documentation on Read the Docs and see actual
      Japanese prose — the failure mode being guarded against is a Japanese project that builds green
      while rendering 100% English.
- [ ] **I18N-02**: The hand-rolled multi-language publishing machinery is gone from the repository, and
      language switching works through Read the Docs' own flyout instead.

### Documentation Accuracy (DOC)

- [ ] **DOC-08**: The unreachable `docs/usage.rst` / `docs/installation.rst` orphan pair is resolved,
      and the test suite is green afterwards — the live, toctree-reachable
      `docs/source/installation.rst` is untouched.
- [ ] **DOC-09**: Every documentation URL the project publishes — in the README, in the PyPI package
      metadata, and in the codebase notes — resolves to a real page, proven by an actual HTTP fetch.
- [ ] **DOC-10**: The external bug report about the broken documentation link (Issue #119) is closed
      with the promised fix actually delivered, and a visitor to the GitHub repository can reach the
      documentation from the repository's own Website field.

### CI & Hosting Teardown (CI)

- [ ] **CI-04**: GitHub Pages no longer hosts or publishes typsphinx documentation, while the
      `typstpdf` regression gate and the tag-time PDF Release attachment keep working.
- [ ] **CI-05**: A broken published link anywhere in the repository — including files Sphinx never
      scans, which is where the links that motivated this milestone actually lived — surfaces
      automatically in CI instead of after months.

### Release (REL)

- [ ] **REL-02**: `typsphinx 0.6.4` is published to PyPI, its `Documentation` metadata points at Read
      the Docs, and both `/en/stable/` and `/ja/stable/` serve that same released version.

---

## Future Requirements

Acknowledged but deliberately not in this milestone.

### Documentation & CI

- **LNK-01**: `sphinx-build -b linkcheck` as a CI job over the `docs/source/` tree. Deferred by owner
  decision 2026-07-25: it structurally cannot see `README.md` / `pyproject.toml`, where the 7 dead
  links that motivated the idea actually live (repo-wide grep found **zero** `github.io` occurrences
  under `docs/source/`), so a green linkcheck job would create false confidence about precisely the
  bug class it was added to prevent. CI-05 covers the real failure class instead. The pending todo
  `.planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md` stays open.
- **I18N-03**: A Japanese PDF. Deferred: `typst-py` embeds only Libertinus Serif / New Computer Modern,
  neither of which has CJK coverage, so this needs `build.apt_packages` font provisioning plus a gate
  that proves the glyphs are right (Typst's font fallback is silent — the failure mode is a
  tofu-rendered PDF that builds successfully). v0.6.3 Phase 27.1 explicitly declined to bundle CJK
  binaries for the same reason; reversing that is its own scoped piece of work.
- **RTD-05**: Pull-request preview builds. Dropped from v1 by owner decision 2026-07-25 — it is a
  single owner-side checkbox with no repo-side work, and `docs.yml` already gates documentation builds
  on PRs. Can be enabled at any time later without a code change; nothing in this milestone blocks it.
- **RTD-06**: Documentation versions for tags before `v0.6.4`. Structurally impossible to add later
  without rewriting history: RTD has refused builds without a `.readthedocs.yaml` since 2023-09-25 and
  no existing tag contains one.

### Carried forward from earlier milestones

- **CFG-01**: user-configurable `@preview` package versions (v2)
- **XOS-01**: cross-OS `docs-pdf` CI on macOS / Windows
- **DEG-03**: real rendering for `graphviz` / `inheritance_diagram` (v2, image pipeline)
- **XREF-02**: link `manpage` / xrefs to external URLs via a configured base URL
- **CONF-06**: `typst_elements` keys beyond `papersize` / `fontsize` / `lang`
- `visit_citation` support; non-str-docname hardening in `typstpdf.finish()`; typing-import
  modernization (`UP006`/`UP035`) — all tracked in `.planning/todos/pending/`

---

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Redirect stubs preserving old `github.io` URLs | Owner decision 2026-07-25: Pages is cut immediately, no redirects. Existing external links 404 — an accepted SEO/inbound-link cost |
| Browser-language auto-redirect at the documentation root | RTD redirects to a *version*, never auto-detects a visitor's *language*. Accepted UX regression; reimplementing it would re-add the custom template code this milestone exists to delete |
| RTD's own LaTeX-based PDF | Would ship an undogfooded PDF built by a toolchain this project doesn't use. `build.jobs.build.pdf` replaces it |
| `sphinx-rtd-theme` | The project uses Furo; RTD's flyout and search are theme-independent |
| RTD "Subprojects" | Translations use the Translations feature, not Subprojects |
| RTD Addons Sphinx extensions (`readthedocs-sphinx-search` etc.) | Superseded — Addons has been enabled by default platform-wide since 2024-10-07 and needs no `conf.py` wiring |
| Any change to `typsphinx/` runtime code | Milestone invariant: this is docs/CI/metadata work. No `@preview` version bump, 3-way version-sync surface untouched |
| `CHANGELOG.md:393`'s historical `github.io` mention | Historical record of what was true at the time. Same precedent as v0.6.3 Phase 24 D-02 |

---

## Milestone Invariants

Carried forward and re-asserted for v0.6.4:

1. **Zero new runtime dependencies.** `sphinx-build -b linkcheck` is built into Sphinx; RTD needs no
   Python package this project doesn't already declare.
2. **No `@preview` version bump.** The four bundled package versions and the (now four-surface)
   version-sync guard — `writer.py`, `template_engine.py`, `templates/base.typ`, `examples/**/*.typ` —
   stay untouched.
3. **No `typsphinx/` runtime code change.** If a requirement appears to need one, that is a signal to
   stop and re-scope, not to widen the diff.
4. **Repo-wide grep at discovery time.** Any success criterion phrased "anywhere under X" is verified
   by a repo-wide grep, never by grepping only the files the requirement names. This bit the project
   twice in v0.6.3 (Phase 27's `docs/source/examples/*.rst` miss, and the unbuildable
   `examples/advanced` sample found only at the milestone close).
5. **Delete collateral tests in the same commit as their subject.** Two test files
   (`tests/test_documentation_usage.py`, `tests/test_documentation_installation.py`) hard-assert the
   existence of files DOC-08 removes. This is the exact trap that reddened the suite in Phase 27.
6. **Irreversible steps last.** RTD must be observed serving both languages and the PDF correctly
   before GitHub Pages / `gh-pages` is deleted. There is no undo.
7. **A green build proves nothing about content.** Two failure modes in this milestone present as
   *successful* builds: a Japanese project rendering English (I18N-01), and a PDF with substituted
   glyphs (RTD-02). Both need content-level verification, not status checks.

---

## Owner-Manual Steps (no automated acceptance criterion possible)

Read the Docs project setup has no `.readthedocs.yaml` representation — it is web-UI work. No test in
this repository can assert any of it. Tracked as an explicit checklist:

1. Create the English RTD project (import + connect GitHub).
2. Create a **separate** RTD project for Japanese — re-import the same repository — and set
   Language = Japanese in *that project's* Admin settings. This setting, not anything in `conf.py`, is
   what makes RTD emit `READTHEDOCS_LANGUAGE=ja` at build time.
3. Link the Japanese project under the English parent's Settings → Translations. **Most likely step to
   be missed**: creating both projects without linking them leaves two working but unswitchable sites.
4. Activate versions on the Japanese project independently — translation projects do not inherit the
   parent's activated-version list.
5. Set Default Version = `stable` — **only after** the `v0.6.4` tag has been pushed and built green
   (RTD-04 / REL-02). Before then it stays `latest`.
6. Set the GitHub repository's About → Website field (DOC-10).

---

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| RTD-01 | TBD | Pending |
| RTD-02 | TBD | Pending |
| RTD-03 | TBD | Pending |
| RTD-04 | TBD | Pending |
| I18N-01 | TBD | Pending |
| I18N-02 | TBD | Pending |
| DOC-08 | TBD | Pending |
| DOC-09 | TBD | Pending |
| DOC-10 | TBD | Pending |
| CI-04 | TBD | Pending |
| CI-05 | TBD | Pending |
| REL-02 | TBD | Pending |

**Coverage:**
- v1 requirements: 12 total
- Mapped to phases: 0 ⚠️ (roadmap not yet created)
- Unmapped: 12

---
*Requirements defined: 2026-07-25*
*Last updated: 2026-07-25 after milestone v0.6.4 scoping (questioning + 4-agent research)*
