# Requirements: typsphinx

**Defined:** 2026-09-13
**Milestone:** v0.9.4 Typing Modernization
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered and well-typeset output, and the documented configuration actually takes effect. This milestone changes no output: it retires a lint deferral in the code that produces that output, and must prove it changed nothing else.

## v1 Requirements

Requirements for this milestone. Each maps to exactly one roadmap phase.

### Quality

- [ ] **QUA-09**: `pyproject.toml`'s `[tool.ruff.lint] ignore` no longer contains `UP006` or `UP035` (nor their deferral comments), and a repo-wide `ruff check .` passes with zero UP006/UP035 findings. The finding count is measured fresh at execution time by `ruff check . --select UP006,UP035`, never hard-coded (113 under ruff 0.16.6 on 2026-09-13), and discovery is repo-wide, never limited to the 2026-07-22 todo's file list.
- [ ] **QUA-11**: Every `typing.Dict`/`List`/`Set`/`Tuple` use in `typsphinx/` and `tests/` is on builtin generics (`dict`/`list`/`set`/`tuple`), and `typing.Iterator` is imported from `collections.abc`. No PEP 604 (`X | None`) rewrite, no `from __future__ import annotations`, no public API or signature change, and no edit to the `@preview` version-sync lines.
- [ ] **QUA-12**: Behaviour is evidenced unchanged, by measurement rather than assertion: (a) a masked-AST hash — annotation subtrees and the `typing` import line masked, reusing v0.9.3 Phase 68's harness shape — equal per converted file between the pre-conversion base and the converted tree; (b) pytest collected and passed counts identical before and after; (c) zero pre-existing test-assertion edits, measured with `git diff`; (d) byte-identical `.typ` output over the existing golden / render-gate fixture corpus; (e) `mypy typsphinx/` output string-identical before and after.

### Documentation

- [ ] **DOC-22**: `CLAUDE.md:75`'s "Don't 'modernize' typing imports until that todo lands" prohibition is rewritten to reflect the modernization, and the 2026-07-22 todo is moved to `.planning/todos/completed/`. The rewrite lands **before** any conversion plan runs (owner decision 2026-09-13), so its wording must be true both before and after the `pyproject.toml` ignore flip.
- [ ] **DOC-23**: A clean docs build (`rm -rf docs/_build` first) shows a diff against the pre-conversion base confined to API-reference type text (`Dict[…]` → `dict[…]` and siblings), and that diff is recorded as evidence.

### Release

- [ ] **REL-13**: Close prep only, unpublished: one CHANGELOG bullet under the existing `## [Unreleased]`, in the register of the three bullets already there, naming the API-reference type-text change and noting that the ja translation catalogs pick it up at the next published release; `pyproject.toml` stays `0.9.2`; no tag, no PyPI upload, no GitHub Release. The milestone branch is merged to `main` through a PR, as v0.9.3's REL-12 was. This checkbox is checked only at `/gsd-complete-milestone`, on the observed merge — never by phase-completion tooling.

## Future Requirements

Deferred. Tracked but not in this roadmap.

- **NUM-01**: `:numref:` numbers diverge per master and vanish for figures reachable only from a non-root master.
- **TRN-01**: `doctest_block` has no translator handler; `>>>` examples collapse onto one line (todo 2026-09-13).
- **MSG-06**: `translator.py`'s two relative-path DEBUG logs quote with a hardcoded `'...'` delimiter.
- **WR-02** / **WR-03**: `templates_path` collision check resolves against `srcdir`; tripled "Custom template not found" warning.
- **QUA-08**: `sphinx-build -b linkcheck` CI job.
- **DOC-18**: root `index.rst` toctree duplicates section children in the HTML sidebar.
- SEED-001, SEED-003, SEED-004, SEED-005 (dormant).

## Out of Scope

| Feature | Reason |
|---------|--------|
| PEP 604 `X \| None` sweep | Nothing to convert (zero `Optional`/`Union` uses) and no active rule forces it |
| `from __future__ import annotations` | Changes runtime annotation semantics; contradicts "behaviour unchanged" |
| mypy strictness changes | Orthogonal to the UP006/UP035 deferral |
| ja translation catalog resync | Happens at the next published release via `typsphinx-doc-translations` |
| Main-checkout `.venv` mypy drift (2.1.0 vs `uv.lock` 2.3.1) | Pre-existing and local-only; worktrees and CI sync to the lock |
| Publishing (tag / PyPI / GitHub Release) | Owner decision 2026-09-13: close prep only, as v0.9.3 |
| Merging a dependabot ruff bump while conversion is in flight | Would move the measured baseline mid-milestone; decide separately |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| QUA-09 | Phase 70 | Pending |
| QUA-11 | Phase 70 | Pending |
| QUA-12 | Phase 70 | Pending |
| DOC-22 | Phase 70 | Pending |
| DOC-23 | Phase 70 | Pending |
| REL-13 | Phase 71 | Pending — coverage only; checked at `/gsd-complete-milestone` on the observed merge, never by phase-completion tooling |

**Coverage:**
- v1 requirements: 6 total
- Mapped to phases: 6 (Phase 70: 5 — QUA-09, QUA-11, QUA-12, DOC-22, DOC-23; Phase 71: 1 — REL-13)
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-13*
*Last updated: 2026-09-13 after roadmap creation (Phases 70–71, 6/6 mapped)*
