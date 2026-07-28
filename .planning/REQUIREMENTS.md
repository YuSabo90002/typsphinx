# Requirements: typsphinx — milestone v0.6.5

**Defined:** 2026-07-28
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered
output on the current ecosystem — and the documented behavior actually happens.

## v1 Requirements

Requirements for milestone v0.6.5 (inline-math separator hotfix). Each maps to roadmap phases.

### Math rendering

- [ ] **MATH-01**: A paragraph where inline math immediately follows text builds through
  `typstpdf` without a Typst compile error — the emitted `.typ` carries a valid separator
  between the preceding text emission and the `mi(...)` / `$...$` call (backlog 999.1;
  suspected `translator.py` math/Text visit ordering — `visit_math` at `translator.py:3936`
  already calls `_add_paragraph_separator()`, so the root cause needs measuring). Covers both
  the mitex default path (`typst_use_mitex=True` → `mi(...)`) and the native path
  (`typst-native` class or `typst_use_mitex=False` → `$...$`). Pinned by a real
  `typst.compile()` GATE-01 regression fixture proven fail-pre-fix.

### Release

- [ ] **REL-03**: v0.6.5 release prepared — `pyproject.toml` bumped to `0.6.5` as the sole
  version literal with `uv.lock` in lockstep, plus a curated `## [0.6.5]` CHANGELOG entry with
  the tail link-block rollover (`[0.6.5]:` tag link added, `[Unreleased]:` compare advanced).
  The publish half (tag `v0.6.5` → `release.yml` → PyPI + GitHub Release, two-repo tagging per
  the v0.6.4 standing cost) executes at `/gsd-complete-milestone`.

## v2 Requirements

Deferred. Tracked but not in the current roadmap (see also STATE.md Deferred Items).

- **CFG-01**: user-configurable `@preview` package versions
- **XOS-01**: cross-OS `docs-pdf` CI (macOS/Windows)
- **DEG-03**: real rendering for `graphviz` / `inheritance_diagram`
- **XREF-02**: xref links to external URLs via a configured base URL
- **CONF-06**: `typst_elements` keys beyond papersize/fontsize/lang
- **LNK-01**: `sphinx-build -b linkcheck` CI job
- **RTD-05**: RTD pull-request preview builds

## Out of Scope

Explicitly excluded from v0.6.5. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| All 5 pending todos (`citation-node-support`, `non-str-docname-typeerror`, `modernize-typing-imports`, `derive-typst-lang-duplicated-warning-block`, `add-sphinx-linkcheck-ci-job`) | Minimal hotfix scope — the owner wants 999.1 fixed and released promptly |
| All deferred requirements (CFG-01, XOS-01, DEG-03, XREF-02, CONF-06, LNK-01, RTD-05) | Same — nothing beyond the 999.1 fix + release enters this milestone |
| Any `@preview` version bump or new runtime dependency | Standing milestone invariant; the 3-way version-sync surface (4 package version strings) stays unchanged |
| The 30.1-review quality warnings (contributing.rst toolchain step, `custom_template.typ` fourth lockstep site, translations-manifest structural tests) | Quality follow-ups, not blocking a hotfix |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| MATH-01 | TBD | Pending |
| REL-03 | TBD | Pending |

**Coverage:**
- v1 requirements: 2 total
- Mapped to phases: 0
- Unmapped: 2 ⚠️

---
*Requirements defined: 2026-07-28*
*Last updated: 2026-07-28 after initial definition (milestone v0.6.5)*
