---
id: T001
title: Make the R010 graphviz proof build with every dot-bearing PATH entry stripped
wave: 1
deps: []
status: pending
agent: null
base: null
worktree: null
task_branch: null
files:
  - tests/test_graphviz_render_gate.py
---

# T001 — Make the R010 graphviz proof build with every dot-bearing PATH entry stripped

## Context

`tests/test_graphviz_render_gate.py::test_no_graphviz_binary_is_installed` (around line 494) asserts `shutil.which("dot") is None` on the host PATH. `flake.nix` deliberately provisions `pkgs.graphviz` in the maintainer's devShell for the local HTML docs build (owner correction C1; graphviz must stay in the flake), so the test fails there by construction while passing on CI ubuntu-latest. SYNTHESIS settled the fix: the proof build itself runs with a PATH from which every entry containing an executable `dot` is removed, and R010 is asserted against that stripped PATH rather than the host PATH. The module fixture `graphviz_render_gate_build` already builds via `subprocess.run([sys.executable, "-m", "sphinx", ...])` and then calls `typst.compile(...)` in-process. This is the wave-1 risk: the stripped-PATH subprocess has not yet been run inside the NixOS FHS sandbox (`typsphinx-fhs-run`).

## Approach

- Add a module-level helper in `tests/test_graphviz_render_gate.py` that returns the `os.pathsep`-joined PATH minus every entry where `<entry>/dot` (and `dot.exe` on Windows) is a file and `os.access(..., os.X_OK)`; preserve the order of kept entries; tolerate empty and nonexistent entries.
- The fixture passes `env={**os.environ, "PATH": stripped}` to its existing `sys.executable -m sphinx` subprocess and runs its in-process `typst.compile(...)` inside `pytest.MonkeyPatch.context()` with `PATH` set to the same stripped value; it records the stripped PATH in its returned dict (e.g. key `stripped_path`).
- `test_no_graphviz_binary_is_installed` asserts `shutil.which("dot", path=<stripped_path from the fixture>) is None` — i.e. the build that produced the diagrams saw no `dot` — and must pass whether or not the host PATH has `dot`. Update its docstring and the module docstring's point 4 accordingly.
- Add a fast, non-slow test `test_path_without_dot_removes_every_dot_entry` that builds a tmp PATH of two directories each holding an executable `dot` plus one clean directory (interleaved), and asserts both `dot` directories are removed, the clean directory is kept, and order is preserved (Edge E1). On Windows create `dot.exe` or skip the executable-bit part as appropriate; the test must pass on the CI matrix (ubuntu, windows, macos).
- Do not skip the test, do not delete or shadow `dot`, do not touch `flake.nix` (veto: graphviz stays in the flake). Keep `sys.executable -m sphinx` (never `uv run sphinx-build` or a PATH-resolved binary). Do not use the function-scoped `monkeypatch` fixture in the module-scoped fixture, and do not mutate `os.environ` module-wide.
- The build only needs Python and typst-py (INTENT Risks); stripping must not remove anything else. Keep all other assertions in the module measuring the same artifact.
- Wave-1 toolchain probe (SYNTHESIS wave-1 blocker 2): at the start, run `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/` once in your worktree and record the results in this task's Log. If the Dependabot-bumped toolchain reports findings outside this task's files, do not fix them here — report `NEEDS-ORCHESTRATOR` with the output.
- Run in the direnv devShell (shims on PATH) with `dot` resolvable on host PATH so the proof is exercised in the environment that used to fail. Warning-text assertions run under `LC_ALL=C`.

## Interface contract

- None

## Intent coverage

- SC1

## Acceptance criteria

1. With `dot` on host PATH (maintainer devShell), `LC_ALL=C uv run pytest tests/test_graphviz_render_gate.py` passes, including `test_no_graphviz_binary_is_installed`, which now asserts that `shutil.which("dot", path=<the PATH the proof build ran with>)` is `None`.
2. E1 (held-out, ruling): every PATH entry that contains an executable `dot` is removed for the proof build, not only the first; the proof passes whether or not the host PATH has `dot`. `tests/test_graphviz_render_gate.py::test_path_without_dot_removes_every_dot_entry` proves two `dot` directories are both removed, a clean directory is kept, and order is preserved.
3. `LC_ALL=C uv run pytest tests/` reports 0 failed at this task's landing.
4. `flake.nix` is unchanged (still provisions `pkgs.graphviz`), and a clean `tox -e docs-html` build (after `rm -rf docs/_build`) still emits a rendered `graphviz-*.png` under `docs/_build/html`.

## Verify

```bash
grep -q 'pkgs.graphviz' flake.nix && env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && command -v dot && LC_ALL=C uv run pytest tests/test_graphviz_render_gate.py -o addopts="" -q && LC_ALL=C uv run pytest "tests/test_graphviz_render_gate.py::test_path_without_dot_removes_every_dot_entry" -o addopts="" -q && LC_ALL=C uv run pytest tests/ -o addopts="" -q -p no:cacheprovider && uv run black --check tests/test_graphviz_render_gate.py && uv run ruff check tests/test_graphviz_render_gate.py && rm -rf docs/_build && uv run tox -e docs-html && find docs/_build/html -name 'graphviz-*.png' | grep -q .
```

Heavy: yes

## Log

- 2026-11-03 — created by planner
- 2026-11-03 — build_T001: toolchain probe at base (worktree, uv-managed venv): `uv run black --check .` 381 files unchanged; `uv run ruff check .` All checks passed; `uv run mypy typsphinx/` no issues in 9 files — no out-of-scope findings.
- 2026-11-03 — build_T001: implemented in tests/test_graphviz_render_gate.py — module helper `path_without_dot(path)` (drops every entry with an executable `dot`/`dot.exe`, keeps order, tolerates empty/nonexistent entries); fixture runs `sys.executable -m sphinx` with `env={**os.environ, "PATH": stripped}` and `typst.compile` inside `pytest.MonkeyPatch.context()` with the same PATH, returns `stripped_path`; `test_no_graphviz_binary_is_installed` now uses the fixture and asserts `shutil.which("dot", path=stripped_path) is None` (docstrings + module point 4 updated); added non-slow `test_path_without_dot_removes_every_dot_entry` (two dot dirs interleaved with clean/empty/missing entries). flake.nix untouched.
- 2026-11-03 — build_T001: Verify pass with host `dot` at /nix/store/...-graphviz-12.2.1/bin/dot: render gate 14 passed; E1 test 1 passed; `tests/` 1730 passed, 1 skipped, 0 failed; black/ruff clean; clean `tox -e docs-html` exit 0, emits docs/_build/html/_images/graphviz-9d601b68….png.
- 2026-11-03 — orchestrator: landing of attempt 1 (isolate gsd-path-task/T001 at base 31b56a4a) was refused by the GSD Path ignore-rule check because that base predates T003's  negation (landed in 85543e35). Rejected diff product patch sha256 390c60b993053f7e437b2eceeeff30519b3364672b28d2bd5dde11cda876fc3d; implementation is not at fault. Isolate retired; T001 is redispatched at the current clean HEAD.
