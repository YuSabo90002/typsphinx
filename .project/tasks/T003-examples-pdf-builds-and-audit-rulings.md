---
id: T003
title: Compile every example and the project docs to PDF under codly 2.0, fix charged-ieee approach1's title and the advanced README claims
wave: 1
deps: [T001, T002]
status: done
agent: build_T003
base: 2277b882636c6c88436827971b2438fe5457ec55
worktree: null
task_branch: null
files:
  - examples/charged-ieee/approach1/conf.py
  - examples/charged-ieee/README.md
  - examples/advanced/README.md
  - examples/advanced/_typst/custom.typ
  - tests/test_examples_charged_ieee_gate.py
  - tests/test_examples_typstpdf_gate.py
---

# T003 — Compile every example and the project docs to PDF under codly 2.0, fix charged-ieee approach1's title and the advanced README claims

## Context

After T001 (codly 2.0.0 deps.typ, code-mode emission, contract docs) and T002 (surface gates, any emission correction) have landed, SC5 requires `typstpdf` builds of `examples/basic`, `examples/advanced`, both `examples/charged-ieee` approaches and the project docs (`tox -e docs-pdf`) to complete without error. Three doc-audit rulings ride along (DOCS-AUDIT Remediation queue rows 1–3, INTENT C1 "5-1 fix-code 5-2 fix-doc 5-3 fix-doc"): `examples/charged-ieee/README.md:152` says both approaches produce identical output, but approach1's PDF title is the charged-ieee default "Paper Title" because `examples/charged-ieee/approach1/conf.py`'s `typst_template_function["params"]` (the complete, exclusive parameter set, D-B) omits `title` — fix-code: add it; `examples/advanced/README.md:206` says seealso renders as `#info(title: "See Also")[]` but the translator renders it through `tip` (translator.py:6315-6321) — fix-doc; `examples/advanced/README.md:138` shows inline math as `#mi(`E = mc^2`)` but the translator emits code-mode `mi(...)` with no `#` — fix-doc. This task is also the milestone's last landing, so it carries SC9.

## Approach

- `examples/charged-ieee/approach1/conf.py`: add `"title": project` to `typst_template_function["params"]`; keep every other param and the package-alone shape that `tests/test_examples_charged_ieee_gate.py` already asserts. Leave the README's identical-output statement true (adjust its wording only if it now overstates).
- Extend `tests/test_examples_charged_ieee_gate.py`: the approach1 PDF's extracted text (pypdf, whitespace-normalised — the IEEE title may wrap) contains the project title "Machine Learning Applications in Computer Vision" and not "Paper Title"; do the same for approach2 so the identical-title claim is checked on both. Keep the existing assertions. These builds fetch `@preview/charged-ieee` as the existing gate already does.
- New `tests/test_examples_typstpdf_gate.py`: `sys.executable -m sphinx -E -b typstpdf` builds of `examples/basic` and `examples/advanced` into `tmp_path` exit 0 and produce non-empty `%PDF` files for each `typst_documents` target; a `-b typst` build of `examples/advanced` shows that the README's quoted inline-math form (read from README.md, not hard-coded) occurs verbatim in the emitted content, and that a seealso renders through `tip(` and not `info(`. Never build inside `examples/` (no `_build` left in the tree).
- `examples/advanced/README.md`: seealso → rendered through `#tip` (with the See Also title); inline math → the code-mode form the translator actually emits for `:math:`E = mc^2`` (check the built `.typ`; SYNTHESIS records `mi(`E = mc^2`)` with no `#`). Do not change unrelated README claims. `examples/advanced/_typst/custom.typ` needs only a comment touch if its codly wording now misleads; it must keep importing deps.typ and pin no `@preview` package (`tests/test_preview_version_sync.py`).
- SC5's docs build is the literal `tox -e docs-pdf` (`tox.ini` `[testenv:docs-pdf]`: `uv-venv-lock-runner`, `extras = docs`, `sphinx-build -b typstpdf source _build/pdf` in `docs/`), run through `uv run`.
- Tests stay OS-neutral: compare extracted text, never paths or colour codes. No version bump, release section or publish (vetoed).

## Interface contract

- None

## Intent coverage

- SC5
- SC7
- SC8
- SC9

## Acceptance criteria

1. SC5: `typstpdf` builds of `examples/basic`, `examples/advanced`, `examples/charged-ieee/approach1` and `approach2` complete with exit 0 and a non-empty PDF each (`tests/test_examples_typstpdf_gate.py`, `tests/test_examples_charged_ieee_gate.py`), and `uv run tox -e docs-pdf` completes without error.
2. SC7: the PDF built from `examples/charged-ieee/approach1` has "Machine Learning Applications in Computer Vision" (the conf.py `project`) as its paper title and does not contain "Paper Title"; approach2's PDF carries the same title, so the README's identical-output claim holds.
3. SC8: `examples/advanced/README.md` states that seealso renders through `#tip` (no remaining `#info(title: "See Also")` claim) and shows the inline-math form the translator actually emits (no `#mi(` form); a test reads that form from the README and finds it verbatim in a `-b typst` build of examples/advanced.
4. No build in this task writes output under `examples/` or leaves untracked files outside the sidecar's temp directories and `docs/_build`.
5. SC9: on this task's tree, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/` are clean.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && LC_ALL=C uv run pytest tests/test_examples_typstpdf_gate.py tests/test_examples_charged_ieee_gate.py -o addopts="" -q -rs && grep -q '#tip' examples/advanced/README.md && ! grep -qF '#info(title: "See Also")' examples/advanced/README.md && ! grep -qF '#mi(' examples/advanced/README.md && LC_ALL=C uv run tox -e docs-pdf && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/
```

Heavy: yes

## Log

- 2026-11-03 — created by planner
- 2026-11-03 — build_T003: approach1/conf.py params gain `"title": project` (charged-ieee README's Approach 1 snippet updated to match, noting the "Paper Title" default when omitted); examples/advanced/README.md inline math now quotes ``mi(`E = mc^2`)`` (code mode, no `#`) and seealso is "rendered through #tip[] with a "See also" title" (emitted title is Sphinx's "See also"); examples/advanced/_typst/custom.typ left unchanged (its codly wording is not misleading). tests/test_examples_charged_ieee_gate.py: both approaches' PDF text (pypdf, whitespace-normalised) contains "Machine Learning Applications in Computer Vision" and not "Paper Title", approach1 show-rule region carries `title:`; confirmed RED with the title param removed. New tests/test_examples_typstpdf_gate.py: typstpdf builds of examples/basic and examples/advanced into tmp_path (exit 0, `%PDF`, non-empty), README inline-math form read from README and found verbatim in a `-b typst` build of examples/advanced, seealso in a tmp_path copy of examples/advanced (it has no seealso of its own) renders via `tip(` not `info(`. Verify run as written: EXIT=0 — gates 6 passed; README greps pass; `tox -e docs-pdf` OK (build succeeded); `LC_ALL=C uv run pytest tests/` 1883 passed, 1 skipped, 0 failed; black/ruff/mypy clean. No build output left under examples/.
- 2026-11-03 — orchestrator Verify (sidecar gsd-path-verify/task-t003-verify): pass, exit 0; output tail:
  ```
   + sphinxcontrib-bibtex==2.7.0
   + sphinxcontrib-devhelp==2.0.0
   + sphinxcontrib-htmlhelp==2.1.0
   + sphinxcontrib-jsmath==1.0.1
   + sphinxcontrib-qthelp==2.0.0
   + sphinxcontrib-serializinghtml==2.0.0
   + tomli-w==1.2.0
   + tox==4.64.10
   + tox-uv==1.37.2
   + tox-uv-bare==1.37.2
   + twine==7.0.0
   + types-docutils==0.23.0.20260923
   + typing-extensions==4.16.0
   + typsphinx==0.9.8 (from file:///home/yuta/.gsd-path/projects/4018706f853274cd7713143cf7ba094e230867e5ad2bfc5891d0cd69027eb98b/4b529697c911aff5766d6b9c03f122ba2ed9565d87a00e2f51ea62f3fd0642ec/verify/task-t003-verify)
   + typst==0.15.0
   + urllib3==2.7.0
   + uv==0.13.6
   + virtualenv==21.5.1
  All done! ✨ 🍰 ✨
  398 files would be left unchanged.
  ```
