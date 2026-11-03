---
id: T002
title: Declare Python 3.14 in classifiers, black, the CI test matrix and tox, and prove tox -e py314 and the full suite pass
wave: 1
deps: []
status: done
agent: build_T002
base: b20a0dc545d698e67ae2cd23aead7794e5476578
worktree: null
task_branch: null
files:
  - pyproject.toml
  - .github/workflows/ci.yml
  - tox.ini
---

# T002 — Declare Python 3.14 in classifiers, black, the CI test matrix and tox, and prove tox -e py314 and the full suite pass

## Context

At 660e3436 worktree venvs already run the full suite green on uv-managed CPython 3.14 (1883 passed, 1 skipped), but `pyproject.toml` classifiers (lines 21-22) list only 3.12/3.13, black `target-version` (line 111) is `["py312", "py313"]`, the CI test matrix (`.github/workflows/ci.yml:18-23`, `python-version: ['3.12', '3.13']` with `include` rows mapping to `tox-env: py312`/`py313`, on ubuntu/windows/macos) and tox `env_list` (`tox.ini:2`, `py312, py313, lint, type, cov, docs`) stop at 3.13. The owner ruled Q3 a: add 3.14 to all four. ruff `target-version` (`py312`), mypy `python_version` (`3.12`) and `requires-python = ">=3.12"` stay unchanged (INTENT Scope out). CI results of the new jobs are observed on the integration PR, not here (INTENT Constraints).

## Approach

- Add `Programming Language :: Python :: 3.14`, `py314` to black's `target-version`, `'3.14'` to the CI matrix with an `include` row `tox-env: py314` (so all three OSes get it), and `py314` to `tox.ini` `env_list`; add a `[testenv:py314]` section only if py312/py313 have their own sections.
- Do not touch the tox-uv `requires` pin or its comment (toolchain-pin sync hazard; `tests/test_toolchain_config_gate.py`).
- If black 26 rejects `py314`, stop and report `blocked` with the error (do not drop it silently).
- Check whether `uv.lock` needs regeneration after the pyproject edit (`uv lock --check`); `uv.lock` is not in `files`, so if it changes, report `NEEDS-ORCHESTRATOR`.

## Interface contract

- None

## Intent coverage

- SC3
- SC7

## Acceptance criteria

1. SC3: `pyproject.toml` classifiers include `Programming Language :: Python :: 3.14`; black `target-version` includes `py314`; `.github/workflows/ci.yml`'s test matrix includes python-version `3.14` mapped to tox env `py314` on ubuntu, windows and macos; `tox.ini` `env_list` includes `py314`; `uv run tox -e py314` passes on the task's tree.
2. SC7: on the task's tree, `LC_ALL=C uv run pytest tests/` reports 0 failed, and `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/` are clean.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && grep -q 'Programming Language :: Python :: 3.14' pyproject.toml && grep -E '^target-version = \[' pyproject.toml | grep -q 'py314' && grep -qE "python-version: \[.*'3\.14'" .github/workflows/ci.yml && grep -q 'tox-env: py314' .github/workflows/ci.yml && grep -E '^env_list' tox.ini | grep -q 'py314' && uv lock --check && LC_ALL=C uv run tox -e py314 && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/
```

Heavy: yes

## Log

- 2026-11-03 — created by plan (quick mode)
- 2026-11-03 — build_T002: added classifier `Programming Language :: Python :: 3.14` and black `target-version` `py314` (pyproject.toml); CI matrix python-version `'3.14'` + include row `tox-env: py314` (all three OSes via the `os` axis) in .github/workflows/ci.yml; `py314` in tox.ini `env_list` (no per-version testenv sections exist, so none added). tox-uv `requires` pin and comment untouched; ruff/mypy/requires-python unchanged. Verify run exactly as written: EXIT=0 — `uv lock --check` clean (uv.lock unchanged), `LC_ALL=C uv run tox -e py314` OK on cpython3.14 (1856 passed, 28 skipped; tox env has extras=dev only), `LC_ALL=C uv run pytest tests/` 1883 passed, 1 skipped, black --check clean, ruff "All checks passed!", mypy "Success: no issues found in 10 source files". Log: /tmp/claude-1000/t002.PomI/verify.log
- 2026-11-03 — orchestrator Verify (isolate gsd-path-task/T002): pass, exit 0; output tail:
  ```
  tests/test_xref_orphan_degrade_render_gate.py::TestXrefOrphanDegradeRenderGate::test_typstpdf_orphan_xref_degrades_included_xref_links PASSED [ 99%]
  tests/test_xref_whole_document_guard_render_gate.py::TestXrefWholeDocumentGuardRenderGate::test_build_exits_0_no_dangling_label PASSED [ 99%]
  tests/test_xref_whole_document_guard_render_gate.py::TestXrefWholeDocumentGuardRenderGate::test_reference_visible_text_present_in_pdf PASSED [ 99%]
  tests/test_xref_whole_document_guard_render_gate.py::TestXrefWholeDocumentGuardRenderGate::test_orphan_body_marker_never_appears_in_master_pdf PASSED [ 99%]
  tests/test_xref_whole_document_guard_render_gate.py::TestXrefWholeDocumentGuardRenderGate::test_index_typ_carries_both_guard_expressions PASSED [ 99%]
  tests/test_xref_whole_document_guard_render_gate.py::TestXrefWholeDocumentGuardRenderGate::test_index_typ_carries_no_string_url_link_to_targets PASSED [ 99%]
  tests/test_xref_whole_document_guard_render_gate.py::TestXrefWholeDocumentGuardRenderGate::test_included_and_orphan_typ_each_carry_self_anchor_once PASSED [ 99%]
  tests/test_xref_whole_document_guard_render_gate.py::TestXrefWholeDocumentGuardRenderGate::test_master_pdf_zero_uri_actions_ending_in_out_suffix PASSED [ 99%]
  tests/test_xref_whole_document_guard_render_gate.py::TestXrefWholeDocumentGuardRenderGate::test_pdf_positional_destination_resolves_to_included_page PASSED [100%]
  
  ================= 1883 passed, 1 skipped in 211.66s (0:03:31) ==================
  All checks passed!
  Success: no issues found in 10 source files
  Resolved 95 packages in 0.57ms
  Checked 94 packages in 0.48ms
  Resolved 95 packages in 0.54ms
  Cannot read termcap database;
  using dumb terminal settings.
  All done! ✨ 🍰 ✨
  398 files would be left unchanged.
  ```
