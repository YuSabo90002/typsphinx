# Review — wave 1, cycle 1

Repository root: /home/yuta/Documents/typsphinx
Review base: da3826df05c339537d9e809716b904750cacba56
Inspection mode: reconstructed product (verify sidecar at review base; per-task diffs `landing^..landing`; recorded isolated Verify JSON as evidence)

Wave verdict: pass
Cycle: 1
Depth: full
Tasks reviewed: 3

## T001 — Make the R010 graphviz proof build with every dot-bearing PATH entry stripped: pass

Identity: landing 66ff6b9b; `66ff6b9b^` = f649ed9b (T002 landing), not the recorded base 2de42b05, but `git diff 2de42b05 f649ed9b -- tests/test_graphviz_render_gate.py` is empty, so the T001 patch applied to the recorded base yields the landing blob. Recorded Verify (verify.json `base` 2de42b05, `location` isolate gsd-path-task/T001, exit 0) ran at base plus only the T001 patch. Changed paths: `tests/test_graphviz_render_gate.py`, task file (frontmatter `status`/`agent`/`base` + appended Log only).

- ✅ T001/AC1 — Verify stdout: `command -v dot` printed `/nix/store/d5nx177j7n96jmd38x9fpankrpkp5szj-graphviz-12.2.1/bin/dot` (host PATH has `dot`), then `14 passed` for `tests/test_graphviz_render_gate.py`; diff shows `test_no_graphviz_binary_is_installed` now takes `graphviz_render_gate_build` and asserts `shutil.which("dot", path=stripped_path) is None`; fixture passes `env={**os.environ, "PATH": stripped_path}` to the `sys.executable -m sphinx` subprocess and wraps `typst.compile` in `pytest.MonkeyPatch.context()` with the same PATH (tests/test_graphviz_render_gate.py fixture and test hunks).
- ✅ T001/AC2 — held-out E1: Verify stdout `1 passed` for `tests/test_graphviz_render_gate.py::test_path_without_dot_removes_every_dot_entry`; `path_without_dot` iterates every entry (not first-match) and the test asserts both `dot_a` and `dot_b` removed, result `[clean, "", missing]` in order, and the unstripped PATH does expose `dot`.
- ✅ T001/AC3 — Verify stdout `1730 passed, 1 skipped` for `LC_ALL=C uv run pytest tests/`, 0 failed.
- ✅ T001/AC4 — `git diff 2de42b05 66ff6b9b -- flake.nix` empty; `flake.nix:177` still `pkgs.graphviz`; Verify chain ended `rm -rf docs/_build && uv run tox -e docs-html` (`docs-html: OK`) `&& find docs/_build/html -name 'graphviz-*.png' | grep -q .` with exit 0.
- ✅ T001/IF1 — Interface contract is `None`; no cross-task shape exchanged.

Warnings (non-blocking):
- `test_no_graphviz_binary_is_installed` gained a `skipif` on typst-py/pypdf availability (same guard as the fixture's consumers); both are dev dependencies, so it does not defeat AC1.

Contract violations (blocking):
- none

## T002 — Remove the inert typst_debug config value through the removed-config path and fix examples/advanced/README.md: pass

Identity: landing f649ed9b; `f649ed9b^` = 2de42b05 = recorded base. Recorded Verify (isolate gsd-path-task/T002, base 2de42b05, exit 0). Changed paths: the eight declared files plus the task file (frontmatter + appended Log only).

- ✅ T002/AC1 — diff removes `app.add_config_value("typst_debug", False, "html", [bool])` from `typsphinx/__init__.py`; `typsphinx/removed_config.py:59-63` adds `"typst_debug"` with message "'typst_debug' was removed in v0.9.8 and has no replacement. It was registered but never read, so deleting it changes no build output."; `grep -rn typst_debug typsphinx/` at review base hits only removed_config.py.
- ✅ T002/AC2 — new `TestTypstDebugRemovalChangesNoOutput` asserts exit 0, `count(message) == 1`, and byte-identical `.typ` trees on first and repeated build (E6), plus parametrized `None`/`False`/`True`/`['x']`; Verify `47 passed`, and the real `sphinx-build -E -b typst` run with `typst_debug = True` printed `build succeeded, 2 warnings.` with exactly one `WARNING: 'typst_debug' was removed in v0.9.8 ...` line in err.txt, `test $(grep -c ...) -eq 1` and `diff -r -x .doctrees -x .buildinfo out1 out2` completed with chain exit 0.
- ✅ T002/AC3 — diff removes the Debug-mode blocks (incl. `SPHINX_TYPST_DEBUG`) from `examples/advanced/conf.py` and README, drops the `_templates/` tree line, replaces "edit `conf.py` and uncomment" with "The custom template is already enabled in `conf.py` by:"; Verify `! grep` clauses for `typst_debug`, `_templates/`, `and uncomment` passed; `grep -rn typst_debug examples/` at review base empty.
- ✅ T002/AC4 — Verify `47 passed` under `LC_ALL=C` for the three named test files; `REMOVED_NAME_TO_PHRASE["typst_debug"] = "v0.9.8"` and the new row in `docs/source/user_guide/configuration.rst:639-642` contains `v0.9.8`.
- ✅ T002/IF1 — `REMOVED_CONFIG_VALUES` remains `dict[str, str]`, key `"typst_debug"` present, message starts `'typst_debug' was removed in v0.9.8` (removed_config.py:60; Verify `grep -q` passed).
- ✅ T002/IF2 — `examples/advanced/README.md` has no `_templates/` line and no `edit \`conf.py\` and uncomment` text (diff hunks; Verify `! grep` clauses passed).

Warnings (non-blocking):
- none

Contract violations (blocking):
- none

## T003 — Correct CLAUDE.md architecture claims and drop the GSD Core worktree-execution text: pass

Identity: landing 85543e35; `85543e35^` = b1513663 = recorded base. `git diff 85543e35 da3826df -- CLAUDE.md .gitignore` is empty, so review-base checks read the landing blobs. Changed paths: `CLAUDE.md`, `.gitignore`, task file (frontmatter + appended Log only).

- ✅ T003/AC1 — Verify clause `! grep -nE "use_worktrees|#683|baseref-head|base-check" CLAUDE.md` passed (exit 0); re-read at review base prints nothing; diff deletes the "Applicability" paragraph.
- ✅ T003/AC2 — CLAUDE.md:107 and :111 keep `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, and the "Run everything via `uv run`" step is unchanged.
- ✅ T003/AC3 — no `_is_master_document` in CLAUDE.md; writer bullet now describes content files via `TypstWriter.translate()` and wrapper files via `TypstWriter.render_wrapper()`, both present at `typsphinx/writer.py:234` and `:279`.
- ✅ T003/AC4 — CLAUDE.md:64 "The five Typst Universe `@preview` package versions (... `diagraph`)", consistent with `tests/test_preview_version_sync.py:42`.
- ✅ T003/AC5 — `~2700`/`~140` removed (diff; grep at review base empty); figures dropped.
- ✅ T003/AC6 — CLAUDE.md:68 documents `[(source, target, title, author[, documentclass]), ...]` with the optional fifth element as a template registry key into `typst_document_templates` (matches README.md:84/233 naming); `typst_debug` absent; CLAUDE.md:78 `tox-uv~=1.35` intact.
- ✅ T003/IF1 — Interface contract is `None`.

Warnings (non-blocking):
- The Verify clause `! git check-ignore -q --no-index <3 paths>` is unfailable (git exits 128 "fatal: --quiet is only valid with a single pathname", inverted to success; recorded stderr). It backs the `.gitignore` repair, not an acceptance criterion. Re-checked per path at review base: the three `.project/**/build/` paths rc=1 (not ignored), `build/x` and `examples/basic/build/x` rc=0 (ignored). Does not defeat any criterion; the Verify should check paths one at a time.

Contract violations (blocking):
- none

## Intent coverage

### SC1 — In the maintainer's direnv devShell, where `dot` is on PATH, `LC_ALL=C uv run pytest tests/test_graphviz_render_gate.py` passes, including the R010 proof that diagrams render without Graphviz, whose build runs with a PATH from which every entry containing an executable `dot` has been removed; `LC_ALL=C uv run pytest tests/` reports 0 failed. `flake.nix` still provisions `pkgs.graphviz`, and a clean `tox -e docs-html` build still emits the rendered `graphviz-*.png` image (local HTML parity kept).: pass
- ✅ T001 recorded Verify (exit 0): host `dot` resolved at `/nix/store/...-graphviz-12.2.1/bin/dot`; render gate `14 passed`; full suite `1730 passed, 1 skipped` (0 failed); `flake.nix` unchanged with `pkgs.graphviz` at line 177; clean `tox -e docs-html` OK and `graphviz-*.png` found under `docs/_build/html`.
- ✅ Edge E1 (held-out): `tests/test_graphviz_render_gate.py::test_path_without_dot_removes_every_dot_entry` recorded `1 passed` in T001 Verify; helper removes every dot-bearing entry and the proof passed with host `dot` present.
- ✅ Prohibition N4: dismissed in INTENT (test-harness change); nothing to judge.

### SC3 — In CLAUDE.md, `grep -nE "use_worktrees|#683|baseref-head|base-check" CLAUDE.md` prints nothing; the per-worktree recipe `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` plus running commands via `uv run` remains documented; `grep -n _is_master_document CLAUDE.md` prints nothing; the `@preview` version-sync section names five packages including `diagraph`; the translator line/method figures match the code or are removed; and the `typst_documents` description documents the optional fifth element (template registry key).: pass
- ✅ T003 recorded Verify exit 0 for every grep clause, and re-read of CLAUDE.md at review base (unchanged since landing): no GSD Core tokens, no `_is_master_document`, recipe at lines 107/111, five packages incl. `diagraph` at line 64, translator figures removed, fifth element documented at line 68. E5 is `criterion SC3` and N5 is dismissed.

### SC4 — `typst_debug` is no longer registered in `typsphinx/__init__.py` and is listed in `typsphinx/removed_config.py`. At the sphinx-build console output surface, a `conf.py` that sets `typst_debug` (any value) prints the removed-config warning for it exactly once, the build exits 0, and the emitted `.typ` output is identical to the same project without the setting. `examples/advanced/conf.py` and `examples/advanced/README.md` no longer mention `typst_debug`, and the CHANGELOG 0.9.8 section records the removal.: pass
- ✅ T002-owned parts: unregistered in `__init__.py`, listed in `removed_config.py:59`; sphinx-build console surface walkthrough reproduced by T002's recorded Verify (copy of `examples/basic`, build without and with `typst_debug = True`, exactly one `'typst_debug' was removed` line in stderr, chain exit 0, `diff -r -x .doctrees -x .buildinfo` empty); any-value and repeated-build (E6) behaviour covered by `TestTypstDebugRemovalChangesNoOutput` (`47 passed`); examples no longer mention `typst_debug`. N6 is `criterion SC4` and is satisfied by the byte-identical `.typ` check.
- ✅ The subclaim "the CHANGELOG 0.9.8 section records the removal" is mapped by PLAN.md Intent coverage to T004/AC6 in wave 2 and is not judged in this wave; T002 correctly did not touch CHANGELOG.md.

## Summary for orchestrator

- blocked findings: none
- repeat offenders: none
- warnings worth a human eye: T003 Verify's multi-path `! git check-ignore -q` clause is unfailable (per-path re-check passes); SC4's CHANGELOG subclaim remains open for T004/AC6 in wave 2.
