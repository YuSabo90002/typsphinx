# Requirements: typsphinx

**Defined:** 2026-09-16
**Milestone:** v0.9.6 Doctest block rendering and release
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered and well-typeset output, and the documented configuration actually takes effect. The same standard applies to the publishing surface: a URL the project publishes must actually resolve, and the PDF a reader downloads must be the one typsphinx itself produced. This milestone restores a node family that is currently rendered wrong rather than merely unsupported, clears the reST errors in this project's own docstrings, and — after three merge-only milestones — publishes.

## v1 Requirements

Requirements for this milestone. Each maps to exactly one roadmap phase.

### Rendering

- [x] **TRN-01**: A `>>>` block in any reST source or docstring renders in Typst output as a code block — the same construct `literal_block` produces, with codly styling and a language tag the handler supplies itself — instead of falling through `unknown_visit()` and collapsing onto one line of plain text. `doctest_block` is a parser-level construct, not a directive: `docutils/parsers/rst/states.py:1251` matches `r'>>>( +|$)'` and `:1698`'s `Body.doctest()` builds the node, so an author writing a Google/NumPy-style `Examples:` docstring cannot opt out of it. `TypstTranslator` has no handler today (`grep -n doctest typsphinx/translator.py` is empty), so the node lands in `unknown_visit()` (`translator.py:5819`), which warns and continues while its `Text` children are still visited as ordinary inline text. The chosen shape matches all three of Sphinx's own writers — `visit_doctest_block = visit_literal_block` at `sphinx/writers/latex.py:2324` and `sphinx/writers/texinfo.py:812`, and a delegating call at `sphinx/writers/html5.py:665`. The language tag cannot be inherited: `HighlightLanguageTransform` (`sphinx/transforms/post_transforms/code.py`) assigns `node['language']` only to `literal_block`, never to `doctest_block`, so `translator.py:2570`'s `node.get("language", "")` would read empty and emit an unhighlighted fence. Both ` ```pycon ` and ` ```python ` were confirmed to compile under a real `typst.compile()`, so the tag is a highlighting-quality choice, not a validity one. **Acceptance:** a clean `sphinx-build -b typst docs/source <tmp>` emits **zero** `unknown node type: <doctest_block` warnings — 2 measured on `main` at `6cc44f22` on 2026-09-16, inside a `build succeeded, 5 warnings.` run — and `api/index.typ` carries the three-prompt `compute_content_include_path` example across separate lines rather than as the single `text("...")` run currently at `api/index.typ:811`. The counts are re-measured fresh at execution time, never transcribed from here.
- [x] **TRN-02**: The handler is correct in both contexts where autodoc/napoleon actually place a doctest block: (a) a plain paragraph position, and (b) a definition-list / field-body position — the `terms.item(text("Examples:"), {...})` shape measured in the 2026-09-13 sphinx-autoapi run and reproduced in this project's own `api/index.typ`. In (b) it respects the same separator discipline `visit_literal_block` applies via `in_list_item` / `list_item_needs_separator`. **Acceptance:** a GATE-01 fixture per context, each recorded RED against the pre-handler translator (a line-structure assertion on the emitted `.typ`, plus the absence of an `unknown node type` warning) before the handler lands, then green through one real `typst.compile()` each.

### Quality

- [x] **QUA-14**: A clean `-b typst` build of `docs/source` reports no docutils `Unexpected indentation` or `Block quote ends without a blank line` message originating in typsphinx's own docstrings. Baseline measured on `main` at `6cc44f22` on 2026-09-16: 3 such messages, attributed to `TypstTranslator.visit_toctree`'s docstring (`:5` and `:21` ERROR, `:6` WARNING). `milestones/v0.9.5-REQUIREMENTS.md`'s Future section names exactly these as the prerequisite a docs warnings gate would first need fixed. **Discovery is a fresh full-build measurement at execution time, not a lookup of the docstrings named here** — any other docstring in the tree raising the same message class is in scope, and the build's total `build succeeded, N warnings.` count must not rise.

### Release

- [x] **REL-15**: v0.9.6 is published. `pyproject.toml` goes `0.9.2` → `0.9.6` as the sole version literal, with `uv.lock` regenerated in the same change and `uv sync --extra dev --locked` green. The six bullets standing under `## [Unreleased]` — carried from v0.9.3, v0.9.4 and v0.9.5 — are promoted into a new `## [0.9.6]` section together with this milestone's own bullets, and the link block at the file's end is updated in the same phase: the `[Unreleased]` compare target moves up to `v0.9.6` and a `[0.9.6]` releases/tag link is added. The milestone branch merges to `main` through a PR with CI green across the Linux, Windows and macOS lanes; tag `v0.9.6` is pushed; `release.yml` publishes the wheel and sdist to PyPI and creates the GitHub Release. **This checkbox is checked only at `/gsd-complete-milestone`, against observed evidence (merge commit on `origin/main`'s first-parent history, `git ls-remote --tags origin`, a PyPI 200 for `0.9.6`, and `gh release list`), and never by phase-completion tooling** — `phase.complete` has flipped REL rows against an explicit decision before. Note that `release.yml`'s `create-release` job has end-to-end evidence from the v0.7.1 publish (run `31462027486`) and v0.8.0 (run `31861043480`) but has never run on a v0.9.x tag.
- [x] **REL-16**: The `### Known Limitations` question is settled on the record for this release. Either `## [0.9.6]` carries such a section naming the carried major defects (NUM-01's per-master `numref` divergence, the converted-image rehome collision, the `typst_documents` duplicate-target cluster), or the release-prep phase's decision record states that the owner declined it and why. v0.9.0's MILESTONES.md entry has a `### Known limitations shipped` precedent, and v0.7.1's D-27 has a precedent for declining one in full; v0.9.5 could leave the question open only because it published nothing. It cannot be left implicit here.

## Future Requirements

Deferred. Tracked but not in this roadmap.

- **MSG-06**: `translator.py`'s two relative-path DEBUG logs quote `up_path`/`down_path` with a hardcoded `'...'` delimiter, the same MSG-02 shape Phase 60 closed in three other modules. The one-line fix is `quote_path()`, which now exists.
- **NUM-01**: `:numref:` numbers diverge per master and vanish for figures reachable only from a non-root master. Only its *disclosure* is in scope this milestone, via REL-16; the fix is not.
- **QUA-08**: a GitHub Actions workflow running `tox -e linkcheck` on a weekly `schedule` and on `workflow_dispatch` as an advisory check. Deferred at v0.9.5's roadmap review because a new workflow file cannot be scheduled or dispatched from an unmerged milestone branch; the environment it calls is now on `main`, so the obstacle is gone and a future pickup should plan the side PR to `main` from the start.
- **LNK-01**: `[testenv:linkcheck]` has no failure-tolerance override or accept-list, so one flaky external URL fails the env locally with no guidance nearby.
- **WR-02** / **WR-03**: the `templates_path` collision check resolves against `srcdir` rather than `confdir`; the "Custom template not found" warning fires three times for one narrow shape.
- A docs warnings gate (`-W`, or a warning-count gate). QUA-14 clears its stated prerequisite but does not install the gate. Note `-W` cannot catch the `multiple toctrees` class, whose messages are not counted as warnings.
- SEED-001, SEED-003, SEED-004, SEED-005 (dormant).

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| A sweep of every other node still reaching `unknown_visit()` | Owner decision 2026-09-16: scope held to TRN-01 plus the adjacent reST errors. The clean `-b typst` build of this project's own docs shows `doctest_block` as the only node falling through; any broader candidate set would first need re-measuring against a large corpus, as v0.6.0 Phase 15 did with Sphinx's own `doc/` tree |
| `sphinx.ext.doctest`'s directives (`.. doctest::`, `.. testcode::`, `.. testoutput::`) | Measured working already — they build `literal_block` subclasses and go through `visit_literal_block`. Only the unmarked-up `>>>` form is broken |
| Adding `:private-members:` or sphinx-autoapi to this project's docs to surface more doctest blocks | That changes exposure, not rendering correctness. The two blocks the current docs build already carries are a sufficient acceptance fixture; the source tree's other 49 `>>>` prompts are covered by the same one handler |
| A `trim_doctest_flags` equivalent in the translator | Measured unnecessary: `TrimDoctestFlagsTransform` (`sphinx/transforms/post_transforms/code.py:100`) already strips `# doctest: +FLAG` from `doctest_block` nodes before any writer sees them |
| Fixing NUM-01, the converted-image rehome collision, or the `typst_documents` duplicate-target cluster | Carried major defects, unchanged in scope. REL-16 decides whether they are *disclosed* in the `## [0.9.6]` notes, not whether they are fixed |
| Switching Read the Docs' default version | Unnecessary: publishing v0.9.6 moves `/en/stable/` forward on its own, which is the point of publishing |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| TRN-01 | Phase 74 | Complete |
| TRN-02 | Phase 74 | Complete |
| QUA-14 | Phase 74 | Complete |
| REL-15 | Phase 75 | Complete |
| REL-16 | Phase 75 | Complete |

**Coverage:**

- v1 requirements: 5 total
- Mapped to phases: 5
- Unmapped: 0
- Duplicated across phases: 0

Phase numbering continues from v0.9.5's Phase 73. Phase 74 is the work phase (the `doctest_block`
handler, its two-context real-compile gate, and the docstring reST errors); Phase 75 is the
prep-only release phase.

**REL-15 is mapped to Phase 75 for coverage only.** Its checkbox is checked at
`/gsd-complete-milestone`, against observed publish evidence, and never by phase-completion tooling
(ROADMAP constraints 1 and 9). **REL-16 does close inside Phase 75** — "settled on the record" is a
phase artifact — which is why that phase's `REQUIREMENTS.md` fence is line-scoped to REL-15 rather
than whole-file.

---
*Requirements defined: 2026-09-16*
*Last updated: 2026-09-22 — REL-15 checked at `/gsd-complete-milestone` against the four
observations its own text names: the merge commit `6fcc5adb` on `origin/main`'s first-parent
history (PR #156, 15/15 checks green including both `windows-latest` and both `macos-latest`
lanes); `git ls-remote --tags origin` carrying `refs/tags/v0.9.6` → `6fcc5adb`; PyPI HTTP 200
for `0.9.6` serving both the wheel (194,339 B) and the sdist (860,244 B), against a 404 for
`0.9.5` as negative control; and `gh release list` showing `Release v0.9.6  Latest`.
`release.yml` run `35730551619` was `success` on every job — including `create-release`, which
this requirement's own text noted had never run on a v0.9.x tag.*
