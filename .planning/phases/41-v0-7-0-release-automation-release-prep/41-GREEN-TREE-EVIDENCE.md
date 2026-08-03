# Phase 41 Plan 05 — Green-Tree Evidence (SC#3, mechanical half)

This file records the full pytest suite, the lint/type trio, the full-corpus (Sphinx v9.1.0 `doc/`)
`-b typstpdf` regression gate, and both docs dogfooding builds, all run live on the POST-BUMP tree
(this worktree, after plans 41-01/41-02/41-03 landed). Every command below was actually run inside
this plan's isolated worktree; nothing is transcribed from a prior phase's evidence file, the
CHANGELOG, or memory. This plan takes no irreversible action and changes no source or test file — it
measures.

**The `ja` four-check glyph bar (SC#3's other half) is plan 41-04's, run in its own parallel worktree.
This file does not speak to it and does not reference its results.**

---

## Preconditions

Command:
```
$ git rev-parse HEAD
```
Verbatim output:
```
aa9d2f06ad854f6f96d285d669ba4bb91b053f31
```

Command:
```
$ uv run python -c "import typsphinx; print(typsphinx.__version__)"
```
Verbatim output:
```
0.7.0
```
This is the post-bump tree (plan 41-02's version bump has landed here) — the required precondition
before any measurement below is meaningful.

Command:
```
$ uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"
```
Verbatim output:
```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a53198d22b20ea40f/typsphinx/__init__.py
```
The resolved path is inside THIS worktree, not the main checkout or any other worktree — confirming
`import typsphinx` in every command below binds to this exact tree's code, not a stale editable
install pointing elsewhere.

**NixOS shim provisioning, confirmed created before any measurement:**

- Worktree venv provisioned via `uv sync --extra dev --extra docs` (with `VIRTUAL_ENV` and
  `UV_PROJECT_ENVIRONMENT` unset first, per CLAUDE.md's worktree-isolated-execution section).
- `uv` shim: `command -v uv` (run before any `.venv/bin` entry was added to `PATH`) resolved to
  `/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv`; symlinked to `.venv/bin/uv`.
  Verified: `readlink -f .venv/bin/uv` → `/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv`
  (a real Nix-store path, not a stale copy inside `.venv`).
- `ruff` shim: no bare `ruff` binary exists on `PATH` in this environment (`command -v ruff` exited
  1 — the same measurement plan 41-02's own SUMMARY recorded). `uv sync` installed a generic-linux
  ELF `.venv/bin/ruff` that fails under the NixOS stub loader (`Could not start dynamically linked
  executable`, exit 127, confirmed by directly invoking it before the fix). Fixed via
  `patchelf --set-interpreter /nix/store/8kvxvr3pmsypxiypq4g8zy13glnfr7nx-glibc-2.42-67/lib/ld-linux-x86-64.so.2 .venv/bin/ruff`
  (the same interpreter `patchelf --print-interpreter` reports for the working `python3` binary in
  this environment). Verified: `.venv/bin/ruff --version` → `ruff 0.15.20`.

Both shims confirmed working before Step 1 below ran.

---

## Step 1 — the full pytest suite, including slow-marked tests

Command:
```
$ uv run pytest -rA
```
Verbatim final result line:
```
================== 805 passed, 1 skipped in 75.85s (0:01:15) ===================
```

**The one skip, named individually with its verbatim reason** (no bare count):
```
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3
before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1
to run it (RESEARCH Open Question 1))
```
This is the same intentional, by-design env-var gate that `40.1-NONREGRESSION.md` §2.3/§2.5 and
Phase 40's own non-regression record already documented — a DIFFERENT (Phase 15/SC#3) concern,
unrelated to this phase's REL-04/REL-05. It is the ONLY skip in the entire collection. No failures,
no errors. (Some `ERROR    typsphinx.pdf:...` and `ERROR sphinx.typsphinx.builder:...` lines appear
in the raw log — these are `logging`-module output from tests that deliberately exercise Typst
compile-failure and missing-asset code paths, e.g. `test_builder_attempts_every_...`,
`test_copy_template_assets_...`; every one of those tests itself reports `PASSED`. They are not
pytest failures.)

**Pass-count delta against `40.1-NONREGRESSION.md` §2.3's recorded figure (799 passed, 1 skipped):**
```
$ grep -c "^PASSED tests/test_changelog_extraction.py" <captured pytest -rA log>
6
$ grep "^PASSED tests/test_changelog_extraction.py" <captured pytest -rA log>
PASSED tests/test_changelog_extraction.py::test_extracts_real_version
PASSED tests/test_changelog_extraction.py::test_section_terminates_at_next_version_heading
PASSED tests/test_changelog_extraction.py::test_absent_version_fails
PASSED tests/test_changelog_extraction.py::test_empty_section_fails
PASSED tests/test_changelog_extraction.py::test_unreleased_headings_do_not_leak
PASSED tests/test_changelog_extraction.py::test_changelog_path_override
```
805 − 799 = **+6**, explained exactly: plan 41-01 added `tests/test_changelog_extraction.py` with six
tests (D-06/D-10's pytest around `scripts/extract_changelog_section.py`), verified above to be
present and passing by name. No other file's test count changed. The skip count (1) is unchanged
from the 40.1 baseline.

---

## Step 2 — `uv run black --check .`

Command:
```
$ uv run black --check .
```
Verbatim output:
```
All done! ✨ 🍰 ✨
207 files would be left unchanged.
```
Exit status: `0` (`BLACK_EXIT:0`, captured via `echo "BLACK_EXIT:$?"` in the same shell invocation).

---

## Step 3 — `uv run ruff check .`

Command:
```
$ uv run ruff check .
```
Verbatim output:
```
All checks passed!
```
Exit status: `0` (`RUFF_EXIT:0`). Note per `tox.ini`'s `[testenv:lint]`: both `black --check .` and
`ruff check .` are run with no path restriction (`pyproject.toml`'s `[tool.black]` exclude list only
names `.git`/`.tox`/`.venv`/`_build`/`build`/`dist`; `[tool.ruff]` has no narrower `include`/`exclude`),
so both DO cover `scripts/` — this is the gate on plan 41-01's new
`scripts/extract_changelog_section.py`.

---

## Step 4 — `uv run mypy typsphinx/`

Command:
```
$ uv run mypy typsphinx/
```
Verbatim output:
```
Success: no issues found in 6 source files
```
Exit status: `0` (`MYPY_EXIT:0`).

**This invocation is directory-scoped and does NOT cover `scripts/extract_changelog_section.py`.**
`tox.ini`'s `[testenv:type]` runs exactly `mypy typsphinx/` — a path-scoped invocation that
structurally cannot reach anything under `scripts/`, and no `[tool.mypy]` `files`/`include` override
in `pyproject.toml` widens this. This is pre-existing repository configuration, not a gap this phase
or plan 41-01 introduced — the new extraction script simply falls outside `mypy`'s configured scope,
the same way `render_admonition_greyscale.py` (this milestone's other `scripts/`-resident module) has
always fallen outside it.

<!-- gsd:write-continue -->
