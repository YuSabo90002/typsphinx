# Requirements: typsphinx v0.9.2 — Inline image blocker fix and release

**Defined:** 2026-08-30
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered
output — and the documented configuration actually takes effect. The same standard applies to the
publishing surface: a URL the project publishes must actually resolve, and the PDF a reader
downloads must be the one typsphinx itself produced.

**Milestone shape.** Two aims, nothing else: close the one blocker that stopped v0.9.1 from being
published, then publish v0.9.1's completed-but-unreleased work together with that fix as **0.9.2**.
Every claim below was measured at HEAD on 2026-08-30 by the four research agents, not carried over
from the pending todo's prose.

## v1 Requirements

### IMG — inline image separator

- [ ] **IMG-08**: An image node preceded by any sibling content in the same container is emitted
      with a separator before `image(`, so Typst accepts the file instead of refusing it with
      `expected semicolon or line break`. The container set is the **16 measured failing shapes**,
      not the four the pending todo recorded: a substitution image mid-sentence; two substitution
      images adjacent; an image inside a list item; a block-level `.. image::` as the second or
      later element of a list item; an image inside a table cell; an image inside a definition-list
      body; an image inside an admonition; an image inside a footnote; an image inside a
      field-list body; an image inside a section title; an image inside a figure's legend body;
      and an image following inline literal / emphasis / a reference rather than plain text.
- [ ] **IMG-09**: `sphinx-build -b typstpdf` produces a PDF for **every** master document of a
      project containing a mid-paragraph inline image. Today it raises `ExtensionError` and writes
      no PDF for any master — including masters that contain no image at all, because Typst's
      `#include()` re-parses the included content file, so one refused file poisons every master
      that transitively includes it.
- [ ] **IMG-10**: The fix routes through the separator triad the translator already uses —
      `_add_paragraph_separator()`, `_emit_inline_concat_separator()`, and the
      `in_list_item` / `list_item_needs_separator` pair — driven from `visit_image()`'s
      non-`in_figure` branch with the matching mark calls in `depart_image()`. The `in_figure`
      branch is not modified, no new line-boundary predicate is introduced, and **zero pre-existing
      tests are edited** — measured, not asserted, across the 144 `image(` matches in 20 test files.

      **AMENDED 2026-08-30 at planning time, owner-acknowledged.** A live 27-document / 18-master
      probe measured that driving the triad from the non-`in_figure` branch *alone* leaves 4 of the
      18 masters refused: both legend shapes (an image inside a figure legend has
      `self.in_figure == True`, so it never reaches that branch — `visit_legend`,
      `typsphinx/translator.py:3181-3183`, already sets `in_list_item` / `list_item_needs_separator`
      correctly; the image simply never consulted them), the field-list-body concat shape (where
      `depart_image()`'s unconditional trailing newlines break the concat expression with
      `cannot apply unary '+' to content`), and `index` transitively. The amended mechanism hoists
      the **leading** half above the `if self.in_figure:` / `else:` split so it runs on both paths,
      and makes the **trailing** half concat-aware — measured 18/18 masters compiling, exit 0, full
      suite 1517 passed / 1 skipped, zero test edits. The change is to the *scope of the call*, not
      the mechanism: the same three pre-existing helpers are used, no new predicate is introduced,
      and the diff is a 9-line pure insertion with zero deletions, so both branch **bodies** stay
      textually unmodified and ROADMAP SC#3's literal `in_figure`-branch-unmodified check still
      holds. This delivers strictly more of IMG-08, never less. See `62-01-PLAN.md` `<amendments>`.

### TEST — regression gate

- [ ] **TEST-05**: One regression gate module binds the 16 failing shapes **and** the shapes that
      must keep passing (a standalone block-level `.. image::`; a `.. figure::`; an image first in
      its paragraph; an image carrying `:width:` / `:height:` / `:scale:` / `:align:`; an image
      receiving a propagated explicit target's id; a figure that also has a legend; a figure nested
      in a list item; a bare image first in a list item), and the gate asserts on a **real
      `typst.compile()`**, not on the emitted string — the string looks plausible and only the
      parser rejects it, which is why nine existing string-level image tests never saw this. The
      gate is recorded RED against the unfixed tree before the fix lands.

### REL — release

- [ ] **REL-09**: 0.9.2 released to PyPI with a curated `## [0.9.2]` CHANGELOG entry, the version
      bumped as the sole literal in `pyproject.toml` with `uv.lock` and `README.md` in lockstep,
      and the GitHub Release body sourced from `scripts/extract_changelog_section.py`.
      *(Carried forward from v0.9.1 per D-08 with its obligations unchanged; only the version token
      is corrected from 0.9.1 to 0.9.2, because v0.9.1 will never be published and the literal
      wording was therefore unachievable. Owner-confirmed 2026-08-30.)* The single `## [0.9.2]`
      entry covers **both** v0.9.1's accumulated `## [Unreleased]` bullets (PATH-01, IMG-04..IMG-07,
      MSG-01..MSG-05) and this milestone's fix; **no `## [0.9.1]` heading is created**, because no
      such release exists. `uv.lock` carries its own `version = "0.9.0"` literal for the
      self-package and must be regenerated — omitting it reproduces the exact `uv sync --locked`
      failure class that is already killing every dependabot PR, across eleven CI steps.
- [ ] **REL-10**: The "Planned for Future Releases" scratch block currently nested under
      `## [Unreleased]` is relocated beneath a fresh empty `## [Unreleased]` heading before that
      heading becomes `## [0.9.2]`, and the extractor's actual output is inspected to confirm the
      block does not leak into the GitHub Release body. `scripts/extract_changelog_section.py`
      selects by **position**, not by heading name, so renaming the heading in place would carry
      the scratch block into the published release notes.
- [ ] **REL-11**: The release requirement's checkbox is protected by a SHA-256 of
      `.planning/REQUIREMENTS.md` recorded at release-phase head and re-verified at phase close and
      at milestone close, following `61-CLOSEOUT-GUARD.md`. `phase.complete` has auto-flipped the
      release requirement to `[x]` against the CONTEXT's explicit decision at **five consecutive**
      release-prep closes; the checksum guard is the only measure that has ever stopped it.

## v2 Requirements

Deferred to a future milestone. Tracked, not in this roadmap.

### Carried forward unchanged

- **NUM-01**: `numref` numbers diverge per master and vanish for figures reachable only from a
  non-root master.
- **CI-01**: Every dependabot PR dies before running a test — it bumps `pyproject.toml` without
  regenerating `uv.lock`, and all eleven `uv sync --locked` steps refuse the stale lockfile.
- **REL-04**: The `create-release` job proven end to end. *(Read at HEAD during research: the
  `uv: command not found` failure is fixed — explicit `Install uv` steps are present and the job
  ran green at the v0.8.0 and v0.9.0 real tag pushes. This milestone's own tag push exercises it
  again; a failure there is handled inside the release phase rather than deferred, but it is not a
  requirement of this milestone.)*
- **MSG-06**: `typsphinx/translator.py:5047,5152` quote `up_path`/`down_path` with a hardcoded
  `'...'` delimiter — the same MSG-02 shape Phase 60 fixed in three other modules.
- **WR-02**: `templates_path` collision detection resolves against `srcdir` rather than `confdir`,
  so `-c`/confdir projects are uncovered.
- **WR-03**: The "Custom template not found" warning fires three times instead of two for one
  narrow shape (54.1 WR-01).
- **QUA-08**: `sphinx-build -b linkcheck` CI job.
- **QUA-09**: Typing modernization — drop the `UP006`/`UP035` ruff ignores.
- **QUA-10**: `ruff` cannot run on this NixOS machine; CI holds lint authority.
- **DOC-18**: The root `index.rst` toctree duplicates section children in the HTML sidebar.
- **SEED-001**, **SEED-003**, **SEED-004**.

## Out of Scope

Explicitly excluded from v0.9.2. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Auditing the whole inline-juxtaposition family | Measured twice, independently: across fourteen inline constructs placed mid-sentence (`:ref:`, inline literal, emphasis, `:abbr:`, `:kbd:`, `:manpage:`, citation reference, `:term:`, `:index:`, `:guilabel:`, external link, footnote reference, `:math:`, `:download:`) the image is the **only** unseparated juxtaposition. This is one emitter, not a class. |
| Refactoring the separator machinery | The fix reuses the existing triad verbatim. A refactor would put every one of the ~140 handlers at risk to fix one. |
| `:scale:` / `:align:` support on images | Silently dropped today and unrelated to this defect. |
| Figure / legend styling changes | The `in_figure` branch is not modified. A newline inside `figure(...)` was measured to be cosmetic — the compiled PDF is byte-identical — so there is no hazard to defend against, and equally no reason to touch it. |
| A from-scratch `self.body` line-boundary predicate | No such predicate exists in the codebase (confirmed by exhaustive grep) and none is needed: the flag-driven triad sidesteps the `self.body` vs `self.table_cell_content` routing question entirely. |
| Bumping `typst-py`, `sphinx`, `docutils` or the four `@preview` packages | All verified current against PyPI and Typst Universe on 2026-08-30 and already matching this repo's pins. `docutils` 0.23 exists but is excluded by the repo's own deliberate `<0.23` pin. This is a blocker-fix-and-release round, not an ecosystem round. |
| A retroactive `## [0.9.1]` CHANGELOG heading | No such release exists or ever will. |
| Advancing the `typsphinx-doc-translations` pin and tag as a requirement | Owner decision 2026-08-30 — handled as post-publish procedure at `/gsd-complete-milestone`, as at the v0.8.0 and v0.9.0 closes. |
| Any other carried-forward defect | Owner decision 2026-08-30: this milestone is the blocker plus the publish. |

## Traceability

Which phases cover which requirements. Filled during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| IMG-08 | Phase 62 | Pending |
| IMG-09 | Phase 62 | Pending |
| IMG-10 | Phase 62 | Pending |
| TEST-05 | Phase 62 | Pending |
| REL-09 | Phase 63 | Pending |
| REL-10 | Phase 63 | Pending |
| REL-11 | Phase 63 | Pending |

**Coverage:**
- v1 requirements: 7 total
- Mapped to phases: 7 ✓
- Unmapped: 0
- Orphaned (no phase): none
- Duplicated (more than one phase): none

**Phase mapping notes:**

- **Phase 62 — The `visit_image()` Separator Fix and Its Real-Compile Gate** carries the whole
  product half: the separator itself (IMG-08), the per-master PDF it unblocks (IMG-09), the
  mechanism and zero-test-edit constraints on how it is written (IMG-10), and the real-compile
  regression gate that is its acceptance criterion (TEST-05). TEST-05 is mapped here rather than
  carried as a cross-cutting obligation because the gate must be recorded RED against the unfixed
  tree *before* the fix lands — an ordering only achievable inside the phase that writes both.

- **Phase 63 — v0.9.2 Release Prep (prep-only)** carries the release half. **REL-09 is cited for
  coverage only and closes at `/gsd-complete-milestone`, not inside the phase** — the phase takes
  zero irreversible action (no tag, no publish, no GitHub Release, no PR), matching the prep-only
  pattern held for eight consecutive milestones and v0.9.1's own explicit handling of the same
  requirement. Its checkbox is held at `[ ]` through every plan, guarded by REL-11's checksum fence,
  and every plan in the phase declares `requirements-completed: []` for it.

---
*Requirements defined: 2026-08-30*
*Last updated: 2026-08-30 — traceability filled during roadmap creation (Phases 62–63)*
