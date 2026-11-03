# Review — wave 1, cycle 1

Repo root: /home/yuta/Documents/typsphinx
Reviewed HEAD: 4533bda7cabcf437209f572dce44228acbed298a
Review scope: final
Inspection mode: reconstructed product (verify sidecar wave-1-cycle-1 at 4533bda7; product blobs of all four declared files at HEAD equal those at landing 9a1dc595; 9a1dc595..4533bda7 changes only `.project/build/verify-ledger.jsonl`)

Wave verdict: pass
Cycle: 1
Depth: full
Tasks reviewed: 1

## T001 — Make the eight Windows-failing tests platform-independent and add typst_deps.py to the README tree: pass

Landing 9a1dc59529cae4962c5ff3f7238d0aabf9805be7, parent = recorded base 3307123fceb391388cb8be1dab03467ad2913a75. Verify evidence: task Log `orchestrator Verify` entry (exit 0) and its full record `.git/gsd-path/dispatch/gsd-path-M003/T001/manual-2026-11-03T065532+0000/verify.json` (ledger entry in `.project/build/verify-ledger.jsonl`, result pass, exit_code 0).

- ✅ T001/AC1 — recorded Verify: `env -u NO_COLOR FORCE_COLOR=1 LC_ALL=C ... pytest tests/test_template_dependency_drift_gate.py` → `28 passed`; no-colour three-file run under `LC_ALL=C` → `48 passed` (includes the 28 drift-gate tests); coder Log records the pre-fix simulation failing 6/22 with trailing `\x1b[39;49;00m`, so the simulation colourises. Diff changes only `_drift_messages()` and adds `ANSI_SGR_RE` (tests/test_template_dependency_drift_gate.py:35, :95-97); no assert line added or removed (`git diff 3307123f 9a1dc595 -- tests/test_template_dependency_drift_gate.py` has zero `assert` lines).
- ✅ T001/AC2 — tests/test_preview_version_sync.py:66 uses `p.relative_to(REPO_ROOT).as_posix()`; :71 keeps `assert matches == ["typsphinx/typst_deps.py"]`, so a second matching file still fails; recorded Verify `! grep -n 'str(p.relative_to'` passed inside the exit-0 chain.
- ✅ T001/AC3 — `_names_missing_template()` at tests/test_hand_compile_root_gate.py:57-64 normalises `\` to `/`; used at :232 by `test_compile_without_root_raises_naming_the_missing_template` (in recorded 48 passed); `TestMissingTemplateMatchIsSeparatorAgnostic` at :249-267 covers the four forms.
- ✅ T001/AC4 — README.md:284 `│   ├── typst_deps.py       # Typst @preview package versions` under `typsphinx/` in `### Project Structure`; recorded Verify README `sed | grep -q 'typst_deps.py'` passed.
- ✅ T001/AC5 — recorded Verify: `1829 passed, 1 skipped`, ruff `All checks passed!`, mypy `Success: no issues found in 10 source files`, black `394 files would be left unchanged.`
- ✅ T001/AC6 — `ANSI_SGR_RE.sub("", line)` removes all matches before the marker test and slice; reviewer check in sidecar: `_drift_messages` on `"\x1b[91mWARNING: \x1b[39;49;00mtemplate dependency drift: \x1b[01mfoo\x1b[0m bar\x1b[39;49;00m"` returned exactly `['template dependency drift: foo bar']`.
- ✅ T001/AC7 — reviewer run in sidecar `LC_ALL=C uv run pytest tests/test_hand_compile_root_gate.py::TestMissingTemplateMatchIsSeparatorAgnostic -v` → 3 parametrized separator forms PASSED, `test_different_missing_file_does_not_match` PASSED (4 passed).

Warnings (non-blocking):
- none

Contract violations (blocking):
- none — changed paths are exactly the four declared files plus the task file; task-file changes are orchestrator fields (`status`, `agent`, `base`) and appended Log entries only.

## Intent coverage

### SC1 — Drift-gate colour portability: with `FORCE_COLOR=1` set and `NO_COLOR` unset in the environment, `LC_ALL=C uv run pytest tests/test_template_dependency_drift_gate.py` passes (the sphinx-build subprocesses then colourise their output as on win32), and it also passes without `FORCE_COLOR`.: pass
- ✅ Recorded Verify: FORCE_COLOR=1 / NO_COLOR unset run `28 passed`; run without FORCE_COLOR (three-file run) `48 passed`. Pre-fix simulation failed 6/22 per coder Log, proving colourised stderr.
- ✅ E1 (held-out, tests/test_template_dependency_drift_gate.py): recorded output `28 passed` under colour simulation; reviewer synthetic check strips leading, mid-line, and trailing SGR codes and yields the exact uncoloured message.
- ✅ N1 (judgment): observed diff touches only `_drift_messages()` colour handling; no expected message, count, or order assertion was changed (zero `assert` lines in the file diff).

### SC2 — Path-separator portability: `tests/test_preview_version_sync.py::test_five_specs_appear_only_in_typst_deps_module` compares POSIX-normalised relative paths (no `str()` of a native `Path` in that comparison), and still fails if a second file under `typsphinx/` names a five-package spec.: pass
- ✅ tests/test_preview_version_sync.py:66 `.as_posix()`, :71 exact-list equality; recorded three-file run 48 passed.

### SC3 — Missing-file message portability: `tests/test_hand_compile_root_gate.py::TestNestedTargetWrapperNeedsTheOutdirAsRoot::test_compile_without_root_raises_naming_the_missing_template` accepts typst's error text whether the missing path is written with `/` or `\` separators (including the `\\?\C:\` prefix form), and still fails when the error names a different missing file; a test exercises both separator forms on Linux.: pass
- ✅ tests/test_hand_compile_root_gate.py:57-64 and :232; recorded three-file run 48 passed.
- ✅ E3 (held-out, tests/test_hand_compile_root_gate.py): reviewer run of `TestMissingTemplateMatchIsSeparatorAgnostic` → `\\?\C:\x\_typsphinx\deps.typ`, `C:\x\_typsphinx\deps.typ`, `/x/_typsphinx/deps.typ` PASSED as matches; `/x/_typsphinx/other.typ` rejection PASSED (4 passed).

### SC4 — README.md surface: the Project Structure tree in README.md lists `typst_deps.py` under `typsphinx/` alongside the existing modules.: pass
- ✅ Walkthrough performed at review HEAD: the fenced tree lists `typst_deps.py` under `typsphinx/` with the other modules.
- **Surface**: README.md Project Structure section
- **Check**: `sed -n '/^### Project Structure/,/^## /p' README.md` in the review sidecar at 4533bda7 (steps 1-2 of the PLAN walkthrough)
- **Observed**: success state — under `├── typsphinx/              # Main package` the tree lists `builder.py`, `writer.py`, `translator.py`, `template_engine.py`, `pdf.py`, `typst_deps.py       # Typst @preview package versions`, then `└── templates/`; alignment of the comment column preserved. Error state (omission) not present.

### SC5 — On the final HEAD, `LC_ALL=C uv run pytest tests/` reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean.: pass
- ✅ Recorded Verify on the task product: `1829 passed, 1 skipped`, black/ruff/mypy clean. Final HEAD 4533bda7 differs from landing only in `.project/build/verify-ledger.jsonl` (`git diff --stat 9a1dc595 4533bda7`), so the product evaluated is identical.

## Summary for orchestrator

- blocked findings: none
- repeat offenders: none
- warnings worth a human eye: Windows CI run 41592991566 (ci-probe/m003-windows) not observed here; it is a Constraint observation, not a criterion.
