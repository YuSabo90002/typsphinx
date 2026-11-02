# Synthesis

<!-- Written by the decider role. The planner treats Decisions as settled. -->

## Settled

- Release version — fold `[Unreleased]` Added/Changed into `## [0.9.8]`, keep `pyproject.toml` at 0.9.8, no 0.9.9 (INTENT.md SC2; DOCS-AUDIT.md User rulings #1, #2)
- 0.9.8 date — the release-prep commit's date, not the later tag date (INTENT.md Edge coverage E4)
- 0.9.8 entry order — existing Graphviz items first, former Unreleased bibliography items after, within Added and within Changed (INTENT.md Edge coverage E2)
- CHANGELOG link block — `[Unreleased]` already compares `v0.9.8...HEAD` (CHANGELOG.md last line) and `[0.9.8]` already points at `releases/tag/v0.9.8` (DOCS-AUDIT.md § Doc: CHANGELOG.md row "## [0.9.8]"); the task verifies both rather than re-adding them (INTENT.md SC2)
- Tag and PyPI publication — out of milestone; post-merge, owner-approved, on the CI-green `main` merge commit only, via `.github/workflows/release.yml` (INTENT.md Constraints, Prohibitions N1/N2, Scope: out)
- Graphviz in the dev shell — `flake.nix` keeps `pkgs.graphviz`; the fix lives in the test only (INTENT.md Scope: out, Corrections C1)
- R010 proof mechanism — the proof build runs with every PATH entry containing an executable `dot` removed, not by skipping the test or deleting `dot` (INTENT.md SC1, Edge coverage E1)
- `typst_debug` — removed, not implemented: unregister at `typsphinx/__init__.py:57`, add an entry to `REMOVED_CONFIG_VALUES` in `typsphinx/removed_config.py`, drop from `examples/advanced/conf.py:103` and `examples/advanced/README.md:267` (INTENT.md SC4, Scope: out; evidence-codebase.md § Finding: `typst_debug` is registered but never read)
- Removed-config warning shape — bare `logger.warning`, no keyword args, fires on name presence regardless of value, once per name, build continues (typsphinx/removed_config.py `check_config_at_init` docstring D-06/D-07/D-08/A-03; tests/test_removed_config_deprecation_gate.py:237-250)
- CLAUDE.md worktree section — drop GSD Core-specific text (`use_worktrees`, `#683`, `baseref-head`, `base-check`) and keep the per-worktree `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` + `uv run` recipe (INTENT.md SC3; DOCS-AUDIT.md User rulings #8)
- CLAUDE.md architecture fixes — DOCS-AUDIT #4–#7 as suggested: content-file + `render_wrapper()` split replaces `_is_master_document()`, translator figures updated or dropped, five `@preview` packages incl. `diagraph`, `typst_documents` optional fifth element (INTENT.md SC3; DOCS-AUDIT.md § Remediation queue #4–#7)
- Other doc fixes — DOCS-AUDIT #3, #9–#13 take each row's Suggested action (INTENT.md SC5; DOCS-AUDIT.md § Remediation queue)
- `.planning/` comment references — left as-is (INTENT.md Scope: out, "全部推奨で")
- `@preview` versions — unchanged; codly 1.3.0, codly-languages 0.1.10, mitex 0.2.7, gentle-clues 1.3.1, diagraph 0.3.7 stay in lockstep across `writer.py`, `template_engine.py`, `templates/base.typ` (INTENT.md Constraints; evidence-codebase.md § Map)
- Bibliography — no runtime dependency or extra added; sphinxcontrib-bibtex stays dev-only (evidence-codebase.md § Finding: Bibliography support is achieved with zero typsphinx code)
- Sphinx invocation in tests — `sys.executable -m sphinx` subprocess, never `uv run sphinx-build` or a PATH-resolved binary (tests/test_graphviz_render_gate.py:142-158; tests/test_removed_config_deprecation_gate.py:60-80)
- Integration — `pull-request` mode; Path opens the PR, owner merges; six required checks must be green (INTENT.md Constraints, SC6)

## Decisions

### R010 proof: how `dot` is stripped from PATH

- **Decision**: Add a module-level helper in `tests/test_graphviz_render_gate.py` that returns `os.pathsep`-joined PATH minus every entry where `os.path.isfile(entry/"dot")` (and `dot.exe` on Windows) and `os.access(..., os.X_OK)`. The module fixture `graphviz_render_gate_build` passes `env={**os.environ, "PATH": stripped}` to its existing `sys.executable -m sphinx` subprocess, and runs its in-process `typst.compile(...)` inside `pytest.MonkeyPatch.context()` with `PATH` set to the same stripped value; it records the stripped PATH in its returned dict. `test_no_graphviz_binary_is_installed` then asserts `shutil.which("dot", path=build["stripped_path"]) is None` (the build that produced the diagrams saw no `dot`) instead of checking the host PATH. A separate fast test proves the helper against a tmp PATH with two dirs each holding an executable `dot` plus one clean dir: both `dot` dirs removed, clean dir kept, order preserved (Edge E1).
- **Runner-up**: Monkeypatch `os.environ["PATH"]` for the whole module and let the subprocess inherit it — lost because module-scope fixtures cannot take the function-scoped `monkeypatch` fixture, a module-wide environ mutation leaks into other tests on failure paths, and an explicit `env=` makes the PATH the proof build saw visible in one place. Also rejected: running in-process Sphinx (`make_app`) — `shutil.which` in a child library call would read the mutated environ, but the module already builds by subprocess and changing that would alter what the other render-gate assertions measure.
- **Evidence**: tests/test_graphviz_render_gate.py:127-158 (fixture already builds via `subprocess.run([sys.executable, "-m", "sphinx", ...])`, absolute interpreter, no PATH dependency); tests/test_graphviz_render_gate.py:494-510 (current host-PATH assertion that fails); tests/test_corpus_gate.py:176 and tests/test_bibtex_multi_bibliography_render_gate.py:417 (precedent for passing `env=` to the Sphinx subprocess); evidence-codebase.md § Finding: The graphviz "no dot binary" test fails on the maintainer's own dev shell by construction; INTENT.md Risks ("must not also remove tools the proof build needs (the build itself only needs Python and typst-py)").
- **Confidence**: medium — the stripped-PATH subprocess has not yet been run inside the NixOS FHS sandbox (`typsphinx-fhs-run`); verify in wave 1 that the build exits 0 and diagrams still render under the stripped PATH in the devShell.

### Removed-config test coverage for `typst_debug`

- **Decision**: Extend `tests/test_removed_config_deprecation_gate.py` (`REMOVED_NAMES`, `REQUIRED_PHRASES`, and the "three" wording in names/docstrings/messages) to the four names, add a SC4 test that builds the same minimal project with and without `typst_debug = True` and asserts exit 0, the warning body appears exactly once, and the emitted `.typ` trees are byte-identical; delete or rewrite the two registration tests at `tests/test_config_other_options.py:141-179`. Message names v0.9.8 as the removal version and states no replacement and no output change.
- **Runner-up**: A new standalone test module for `typst_debug` — lost because the existing gate already iterates `REMOVED_CONFIG_VALUES` for once-each/declaration-order checks (tests/test_removed_config_deprecation_gate.py:263-296) and the hand-written `REMOVED_NAMES` list would otherwise silently skip the new name in the per-name tests.
- **Evidence**: tests/test_removed_config_deprecation_gate.py:27-41, :101, :176, :255-296; tests/test_config_other_options.py:141-179; typsphinx/removed_config.py `REMOVED_CONFIG_VALUES` (`typst_toctree_defaults` message is the model for a never-read value); INTENT.md SC4, Edge E6.
- **Confidence**: high

## For the planner

- **Wave-1 blockers**: (1) The stripped-PATH R010 proof in the NixOS devShell — must show `LC_ALL=C uv run pytest tests/test_graphviz_render_gate.py` green with `dot` on host PATH before anything depends on a 0-failed full suite (SC1). (2) Dependabot bumps since 2026-09-30 (black 26.10.1, mypy, tox, tox-uv, sphinx-autodoc-typehints 3.17.4) are untested on this branch's CI; run `black --check .`, `ruff check .`, `mypy typsphinx/` early so a lint/type delta is not discovered at the PR.
- **Walking skeleton**: Graphviz test fix (SC1) landing first gives a trustworthy 0-failed local baseline; then `typst_debug` removal (SC4) and doc/CLAUDE.md fixes (SC3, SC5) in parallel; release prep (CHANGELOG fold, README status, version check, `uv build` + `twine check`, PR with six green checks) last (SC2, SC6).
- **Pitfalls → tasks**:
  - Stripping must remove every `dot` entry, not the first, and must keep entries the build needs → R010 test task (Edge E1; Decision above).
  - Full-suite and warning-text assertions run under `LC_ALL=C`; NixOS sandbox passes host `LANG` → every task Verify touching warnings, especially the `typst_debug` task (INTENT.md Constraints; CLAUDE.md § Locale).
  - CHANGELOG fold, 0.9.8 date, link-block check and README status line belong in one release-prep task, together with the `typst_debug` removal line in 0.9.8 → release-prep task must run after the `typst_debug` task lands (SC2, SC4). `scripts/extract_changelog_section.py 0.9.8` must print both `Graphviz` and `BibTeX`.
  - Do not bump or touch any `@preview` version; CLAUDE.md edit changes only the prose count to five → CLAUDE.md task (`tests/test_preview_version_sync.py` guards it).
  - CLAUDE.md toolchain-pin paragraphs (`tox-uv~=1.35`, multi-place sync) are verified and must not drift when the worktree section is trimmed → CLAUDE.md task.
  - `REMOVED_NAMES` in the gate test is hand-listed; forgetting it leaves `typst_debug` untested per-name → `typst_debug` task.
  - Every 0.9.8 claim must match shipped code (Prohibition N3): do not claim `typst_debug` did anything; message says it was never read → `typst_debug` and release-prep tasks.
  - Fresh worktree `.venv` is uv-managed CPython 3.14, outside CI's 3.12–3.13; local green is not CI green → final release-readiness task relies on the PR's six required checks (SC6; evidence-codebase.md § Finding: Tests escalate deprecation warnings).
  - `tox -e docs-html` HTML parity (graphviz PNG) must still build from a clean `docs/_build` → R010 task or release task re-checks it (SC1).

## User rulings

- none

## Still unknown

- Whether the stripped-PATH Sphinx subprocess behaves identically inside the NixOS FHS sandbox — plan: wave-1 spike (R010 task Verify in devShell)
- Whether the Dependabot-bumped toolchain changes CI results on the release-prep HEAD — plan: wave-1 lint/type check, then PR's six required checks (accept risk until PR)
- Skip reasons of the 18 skipped tests — accept risk (evidence-codebase.md § Blocked areas; not required by any success criterion)
