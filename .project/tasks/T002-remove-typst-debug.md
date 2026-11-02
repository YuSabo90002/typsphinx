---
id: T002
title: Remove the inert typst_debug config value through the removed-config path and fix examples/advanced/README.md
wave: 1
deps: []
status: pending
agent: null
base: null
worktree: null
task_branch: null
files:
  - typsphinx/__init__.py
  - typsphinx/removed_config.py
  - tests/test_removed_config_deprecation_gate.py
  - tests/test_config_other_options.py
  - tests/test_registry_documentation_gate.py
  - docs/source/user_guide/configuration.rst
  - examples/advanced/conf.py
  - examples/advanced/README.md
---

# T002 — Remove the inert typst_debug config value through the removed-config path and fix examples/advanced/README.md

## Context

`typst_debug` is registered at `typsphinx/__init__.py:57` (`app.add_config_value("typst_debug", False, "html", [bool])`) and nothing in `typsphinx/` reads it; the owner chose removal, not implementation (veto: do not implement `typst_debug` behaviour). SYNTHESIS settled the route: add an entry to `REMOVED_CONFIG_VALUES` in `typsphinx/removed_config.py`, so `check_config_at_init` (a `config-inited` handler reading `config._raw_config`) warns by name, once, regardless of value, with a bare `logger.warning` and the build continues. `tests/test_removed_config_deprecation_gate.py` hand-lists `REMOVED_NAMES` and `REQUIRED_PHRASES` (lines ~27-41) and uses "three" wording; `tests/test_registry_documentation_gate.py` binds `REMOVED_NAME_TO_PHRASE` and the "Removed Configuration Values" table in `docs/source/user_guide/configuration.rst` (around line 603) to `set(REMOVED_CONFIG_VALUES)` by exact set-equality, so both must gain `typst_debug`. `tests/test_config_other_options.py:141-179` holds two registration tests that become wrong. This task also owns DOCS-AUDIT #11 and #12 in `examples/advanced/README.md`, the same file that must stop mentioning `typst_debug`.

## Approach

- Message for `typst_debug` follows the `typst_toctree_defaults` model (a never-read value): names `'typst_debug'`, says it "was removed in v0.9.8", states it has no replacement and that it was registered but never read, so deleting it changes no build output. It must begin `'typst_debug' was removed in v0.9.8` (see Interface contract). Do not claim it ever did anything (Prohibition N3).
- Keep the warning shape: bare `logger.warning`, no keyword args, fires on name presence regardless of value (`None`, `False`, `True`, lists), once per name. Do not touch `check_config_at_init`'s mechanism; update the module docstring's "three" counts so they stay true.
- Extend the gate test's `REMOVED_NAMES`/`REQUIRED_PHRASES` and "three" wording to four names. Add an SC4 test that builds the same minimal project with and without `typst_debug = True` (same source directory path, so emitted paths match) and asserts exit 0, the warning body appears exactly once, and the emitted `.typ` trees are byte-identical. Also cover idempotency (Edge E6): a repeated build of the same `conf.py` still warns exactly once.
- Delete or rewrite `test_typst_debug_config_registered` and `test_typst_debug_default_false` in `tests/test_config_other_options.py` (e.g. assert `typst_debug` is no longer a registered config value).
- Add a `typst_debug` row (removed in v0.9.8, "Delete the setting ... no replacement ...") to the Removed Configuration Values table in `docs/source/user_guide/configuration.rst` and its key to `REMOVED_NAME_TO_PHRASE` with a phrase that appears in that row.
- `examples/advanced/conf.py` and `examples/advanced/README.md`: remove the whole "Debug mode (optional)" comment block, including the `SPHINX_TYPST_DEBUG` line (nothing in `typsphinx/` reads that env var).
- DOCS-AUDIT #11: drop the `_templates/` line from the `examples/advanced/README.md` directory tree (the directory does not exist; leave `templates_path` in `conf.py` alone). DOCS-AUDIT #12: replace "To use the custom template, edit `conf.py` and uncomment:" with a statement that the custom template is already enabled by `typst_template = "_typst/custom.typ"` in `conf.py`.
- Sphinx is invoked in tests as `sys.executable -m sphinx`, never `uv run sphinx-build`. Warning-text tests run under `LC_ALL=C`.
- Do not touch `.planning/` comment references, `@preview` versions, or CHANGELOG.md (T004 writes the 0.9.8 removal entry).

## Interface contract

- `typsphinx.removed_config.REMOVED_CONFIG_VALUES` (type `dict[str, str]`) contains the key `"typst_debug"`; its message string starts with `'typst_debug' was removed in v0.9.8`.
- `examples/advanced/README.md` contains no line with `_templates/` and no text `edit \`conf.py\` and uncomment`.

## Intent coverage

- SC4

## Acceptance criteria

1. `typst_debug` is no longer registered in `typsphinx/__init__.py` and is a key of `REMOVED_CONFIG_VALUES` in `typsphinx/removed_config.py` with a message stating removal in v0.9.8, no replacement, and no output change.
2. At the sphinx-build console output surface: a `conf.py` that sets `typst_debug` (any value) prints the removed-config warning for it exactly once, the build exits 0, and the emitted `.typ` output is identical to the same project without the setting; a repeated build warns exactly once again (E6). Proven by the new test in `tests/test_removed_config_deprecation_gate.py` and by the real `sphinx-build` run in Verify.
3. `examples/advanced/conf.py` and `examples/advanced/README.md` no longer mention `typst_debug`; `examples/advanced/README.md` no longer lists `_templates/` and no longer tells the reader to uncomment `typst_template` (DOCS-AUDIT #11, #12).
4. `tests/test_removed_config_deprecation_gate.py`, `tests/test_config_other_options.py`, and `tests/test_registry_documentation_gate.py` pass under `LC_ALL=C` with `typst_debug` covered per-name and in the documented Removed Configuration Values table.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev && LC_ALL=C uv run pytest tests/test_removed_config_deprecation_gate.py tests/test_config_other_options.py tests/test_registry_documentation_gate.py -o addopts="" -q && ! grep -n typst_debug typsphinx/__init__.py examples/advanced/conf.py examples/advanced/README.md && ! grep -n '_templates/' examples/advanced/README.md && ! grep -n 'and uncomment' examples/advanced/README.md && grep -q "'typst_debug' was removed in v0.9.8" typsphinx/removed_config.py && d=$(mktemp -d) && cp -r examples/basic "$d/p" && LC_ALL=C uv run sphinx-build -E -b typst "$d/p" "$d/out1" && echo 'typst_debug = True' >> "$d/p/conf.py" && LC_ALL=C uv run sphinx-build -E -b typst "$d/p" "$d/out2" 2> "$d/err.txt" && cat "$d/err.txt" && test "$(grep -c "'typst_debug' was removed" "$d/err.txt")" -eq 1 && diff -r -x .doctrees -x .buildinfo "$d/out1" "$d/out2"
```

Heavy: no

## Log

- 2026-11-03 — created by planner
