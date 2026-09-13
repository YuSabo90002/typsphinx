# Requirements: typsphinx

**Defined:** 2026-09-13
**Milestone:** v0.9.5 Docs Link Check and Navigation
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered and well-typeset output, and the documented configuration actually takes effect. The same standard applies to the publishing surface: a URL the project publishes must actually resolve. This milestone changes no builder output: it makes Sphinx's own link check a one-command check over the documentation (`tox -e linkcheck`), and removes a navigation defect from this project's own docs site.

## v1 Requirements

Requirements for this milestone. Each maps to exactly one roadmap phase.

### Quality

- [x] **QUA-13**: `tox.ini` gains a `[testenv:linkcheck]` environment, shaped like `docs-html` (`runner = uv-venv-lock-runner`, `extras = docs`, `changedir = docs`), that runs `sphinx-build -b linkcheck source _build/linkcheck`. It is **not** added to `env_list`, because it needs the network. On the tree at execution time it exits 0 with every checked link `working`. The count is measured fresh, never hard-coded (95 `working` on 2026-09-13). Any `linkcheck_*` setting added to `docs/source/conf.py` (ignore patterns, timeouts, retries, rate limits) carries a comment naming the measured failure that required it. None is added speculatively.

### Documentation

- [x] **DOC-18**: The root `docs/source/index.rst` "User Guide" and "Examples" toctrees list only `user_guide/index` and `examples/index`. The `user_guide/configuration`, `user_guide/builders`, `user_guide/templates`, `examples/basic` and `examples/advanced` entries are removed, so the HTML sidebar shows each page once, nested under its section (owner decision 2026-09-13: the conventional hierarchy, not flat visibility). The fix is gated on a **clean** HTML build (`rm -rf` of the output first). That build must emit **zero** `document is referenced in multiple toctrees` messages (5 measured on 2026-09-13), and its `build succeeded, N warnings.` count must stay unchanged (3 measured). Under `-b typst`, each of the five pages is still included exactly once, through its section index, and the root `index.typ` no longer carries dead state-guarded `include()` lines for them.
- [x] **DOC-24**: Every surface that lists the project's tox environments names `tox -e linkcheck` beside `docs-html`/`docs-pdf`. On 2026-09-13 these were `CLAUDE.md` § Commands, `README.md`'s development commands block and `docs/source/contributing.rst`'s tox block. Discovery is by a repo-wide grep for `tox -e docs-pdf` at execution time, never limited to these three.

### Release

- [ ] **REL-14**: Close prep only, unpublished. CHANGELOG bullet(s) go under the existing `## [Unreleased]`, in the register of the four bullets already there, and name the docs sidebar fix and the new `tox -e linkcheck` environment (owner decision 2026-09-13; revised the same day when QUA-08, the CI job, was deferred — no bullet may claim a CI job that does not exist). `pyproject.toml` stays `0.9.2`. There is no tag, no PyPI upload and no GitHub Release. The milestone branch is merged to `main` through a PR, as REL-12 and REL-13 were. This checkbox is checked only at `/gsd-complete-milestone`, on the observed merge, and never by phase-completion tooling.

## Future Requirements

Deferred. Tracked but not in this roadmap.

- **NUM-01**: `:numref:` numbers diverge per master and vanish for figures reachable only from a non-root master.
- **TRN-01**: `doctest_block` has no translator handler; `>>>` examples collapse onto one line (todo 2026-09-13).
- **MSG-06**: `translator.py`'s two relative-path DEBUG logs quote with a hardcoded `'...'` delimiter.
- **QUA-08**: a GitHub Actions workflow running `tox -e linkcheck` on a weekly `schedule` and on `workflow_dispatch` as an advisory check (no push/PR trigger, never required, failure = red run only, no issue filing). Supersedes the older **LNK-01**. Scoped into v0.9.5 at requirements time, then deferred by the owner on 2026-09-13 at roadmap review. GitHub runs `schedule` only on the default branch, and runs `workflow_dispatch` only for a workflow file that exists on the default branch (docs.github.com, events-that-trigger-workflows / manually-run-a-workflow, checked 2026-09-13). A new workflow therefore cannot be proven on an unmerged milestone branch, so every proof route needed a side PR to `main` or a post-merge observation. A future pickup should plan the side PR to `main` from the start, as v0.9.3 did for `dependabot.yml` (#137).
- **WR-02** / **WR-03**: the `templates_path` collision check resolves against `srcdir`; the "Custom template not found" warning fires three times.
- A docs warnings gate (`-W`, or a warning-count gate), together with the fix for the 3 rST errors in `TypstTranslator.visit_toctree`'s docstring that such a gate first needs. Note that `-W` cannot catch the `multiple toctrees` class (those messages are not counted as warnings).
- Issue filing on a failed scheduled linkcheck run, in `drift.yml`'s deduplicated-issue shape (declined by the owner on 2026-09-13; relevant only once QUA-08 is picked up).
- SEED-001, SEED-003, SEED-004, SEED-005 (dormant).

## Out of Scope

| Feature | Reason |
|---------|--------|
| Publishing (tag / PyPI / GitHub Release) | Owner decision 2026-09-13: merge-only, as v0.9.3 and v0.9.4. Accepted consequence: the DOC-18 fix reaches `/en/latest/` and ja `latest`, but not the default `/en/stable/` (tag `v0.9.2`) until the next published release |
| Switching Read the Docs' default version to `latest` | Would put unreleased documentation on the default pages ahead of PyPI |
| Any CI job running linkcheck (scheduled, per push / pull request, or required) | QUA-08, the scheduled advisory job, is deferred to Future (see above). Per-push/PR or required runs were declined outright on 2026-09-13: lychee (`links.yml`) already checks raw URLs per push/PR, and external-site flakiness must not block merges |
| Link-checking `README.md` / `pyproject.toml` / the repository root | Already covered by `links.yml`'s lychee job; Sphinx's `linkcheck` walks only `docs/source/` |
| Link-checking the ja site | Built from `typsphinx-doc-translations`; its links mirror the English source |
| Fixing the HTML-vs-Typst parent divergence for `examples/basic` beyond what DOC-18's dedup produces | The 2026-08-16 todo records it as a probable consequence of the duplication; re-measured after DOC-18, and filed separately only if it survives |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| QUA-13 | Phase 72 | Complete |
| DOC-18 | Phase 72 | Complete |
| DOC-24 | Phase 72 | Complete |
| REL-14 | Phase 73 | Pending |

**Coverage:**

- v1 requirements: 4 total
- Mapped to phases: 4 (Phase 72: QUA-13, DOC-24, DOC-18 · Phase 73: REL-14)
- Unmapped: 0 ✓
- QUA-08 was deferred to Future by the owner at roadmap review (2026-09-13) and maps to no phase.
- REL-14 is mapped to Phase 73 for coverage only; its checkbox is checked at
  `/gsd-complete-milestone`, on the observed merge.

---
*Requirements defined: 2026-09-13*
*Last updated: 2026-09-13 after roadmap revision (QUA-08 deferred to Future; Phases 72–73, 4/4 mapped)*
