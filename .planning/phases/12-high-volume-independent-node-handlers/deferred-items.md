# Deferred Items — Phase 12

Items observed during execution that are out of scope for the current task
(pre-existing, unrelated to the change being made) and therefore not fixed.

## Plan 12-01

- **Pre-existing sandbox failure (NOT caused by this plan's changes):** `pytest -m "not slow" -q`
  shows 45 failures in `tests/test_integration_advanced.py`, `tests/test_integration_basic.py`,
  `tests/test_integration_multi_doc.py`, and `tests/test_integration_nested_toctree.py`. All 45
  fail identically with `Could not start dynamically linked executable: uv` /
  `NixOS cannot run dynamically linked executables intended for generic linux environments`.
  These tests invoke `subprocess.run(["uv", "run", "sphinx-build", ...])` directly, which hits the
  exact PATH-shadowing/NixOS dynamic-linking hazard already documented in
  `tests/test_pdf_render_gate.py`'s own `_run_sphinx_build_typst` docstring (that helper was
  written specifically to route around this by using `sys.executable -m sphinx` instead of
  `["uv", "run", ...]`). None of these failing files were modified by 12-01's task 1 (the
  `visit_versionmodified`/`visit_inline` change), and `tests/test_translator.py` (104 tests,
  covering the modified `visit_inline`/`visit_emphasis` interaction) passes cleanly. Out of scope
  per the SCOPE BOUNDARY rule (pre-existing failures unrelated to the current task's files) —
  not fixed here. A future maintenance item could migrate these 4 files to the
  `sys.executable -m sphinx` invocation pattern.
- **Sandbox tooling note:** `uv run ruff`/`uv run black` (executable wheels installed into
  `.venv/bin`) cannot execute in this NixOS sandbox for the same dynamic-linking reason (`Could not
  start dynamically linked executable: ruff`). Verified lint compliance instead via
  `nix-shell -p ruff --run "ruff check ."` (ruff 0.15.14 from nixpkgs, vs. the pinned 0.15.20 —
  same rule set, no version-specific rules changed between these patch releases affected by this
  plan's diff) and `uv run black --check typsphinx/` (black itself runs fine via `uv run`, only
  ruff's own binary hit the ELF issue). `mypy typsphinx/` ran cleanly via `uv run mypy`.
