# Phase 64 Plan 03 Task 2 — NIX-08 Environment and Locale Evidence

## Definitions (written before measuring)

These definitions are written and committed before any locale probe in this file runs, so that a
MASKS or INCONCLUSIVE result cannot be reclassified after seeing the data (T-64-13).

- **The known class:** tests whose outcome depends on the process locale. Historically, Sphinx
  localizes a warning's BODY text under the maintainer's `LANG=ja_JP.UTF-8` while CI runs English.
  Phase 52 re-anchored `tests/test_state_guard_shapes_gate.py::TestNoLostDiagnostics` on the
  never-localized `file:line: WARNING:` prefix and the bracketed diagnostic tag, via
  `_locale_invariant_anchors()`.

- **Matrix:** the warning body Sphinx emits for one fixed scratch document that is outside any
  toctree, captured four ways:
  - **H-ja:** host, maintainer environment, via the worktree's absolute `.venv/bin/python -m
    sphinx` (an absolute path, so no shim is involved)
  - **H-C:** host, with `LC_ALL=C LANG=C LANGUAGE=C`
  - **S-ja:** through the `sphinx-build` shim, maintainer environment
  - **S-C:** through the shim, with `LC_ALL=C LANG=C LANGUAGE=C` set by the caller

  All four runs start from inside the worktree, so the shim's walk finds this worktree's `.venv`.
  All four use the same Sphinx.

- **Control:** H-ja ≠ H-C, meaning the locale axis actually changes Sphinx's text on the host. If
  H-ja = H-C, the finding is **INCONCLUSIVE**: record it and do not classify.

- **REPRODUCES:** the control holds, S-ja = H-ja and S-C = H-C. Through the shim, the locale axis
  behaves exactly as on the host. So the class exists through the shim exactly as it does on the
  host: invisible under ja_JP.UTF-8, surfaced by the `LC_ALL=C` pre-check.

- **MASKS:** the control holds, and S-ja ≠ H-ja or S-C ≠ H-C. The shim changes what the locale axis
  shows, so a shim run cannot stand in for a host run when reasoning about the class. Record which
  cell diverged and in which direction. Per CONTEXT § Specific Ideas, masking is a legitimate
  finding and is written as such.

<!-- gsd:write-continue -->
