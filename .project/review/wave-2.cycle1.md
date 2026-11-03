# Review — wave 2, cycle 1

Repo root: /home/yuta/Documents/typsphinx
Review base: e31599c8f61ec785ebc7b2ac0713b1ba02ce337d
Inspection mode: reconstructed product (verify sidecar at review base e31599c8; T003 patch = 9efd389a..761ebf7b, parent of 761ebf7b = recorded base 9efd389a; T004 patch = 99b32c62..e89e4571, parent of e89e4571 = recorded base 99b32c62; T005 patch = c7403260..bdbcdd17, parent of bdbcdd17 = recorded base c7403260; bdbcdd17..e31599c8 changes only `.project/build/verify-ledger.jsonl`)

Wave verdict: pass
Cycle: 1
Depth: full
Tasks reviewed: 3

## T003 — Warn once per (file, package) when a used template bundle pins one of the five packages at a version different from the effective deps.typ: pass

- ✅ T003/AC1 — `builder.py` (761ebf7b) `_warn_template_dependency_drift()` called in `finish()` right after `_copy_used_template_bundles()`; effective versions = `DEFAULT_PACKAGES` when `typst_dependencies is None`, else `extract_preview_versions()` over the copied `<outdir>/_typsphinx/deps.typ`; one `logger.warning` per (file, package) with a non-empty difference; never raises. `tests/test_template_dependency_drift_gate.py` TestSC4DefaultMode (mismatch warns once, exit 0 asserted in `_build`; matching, no import, default template silent) and TestSC4OverrideMode (`gentle-clues:1.3.1` template vs user 1.3.0 warns `... has @preview/gentle-clues:1.3.0`; matching 1.3.0 silent). Orchestrator Verify (task Log, sidecar task-t003-verify) pass, exit 0 — the chain runs this file under `LC_ALL=C` first.
- ✅ T003/AC2 — E7: TestE7Adjacency `@preview/charged-ieee:0.1.0` + `@local/codly:9.9.9` assert no drift line; unit `test_other_namespace_and_package_ignored`; regex `_PREVIEW_PIN_RE` (typst_deps.py) is anchored on `@preview/` and requires `:` right after the name. Passed in orchestrator Verify (exit 0).
- ✅ T003/AC3 — E8: TestE8Ordering asserts exactly three lines in order extra.typ/gentle-clues, main.typ/codly, main.typ/gentle-clues (same mismatch in two files = two warnings; two packages in one file = two warnings; sorted (file, package)); code iterates `sorted(typ_relpaths)` then `sorted(pinned)`. Passed (exit 0).
- ✅ T003/AC4 — E9: fixture `tests/fixtures/template_dependency_drift/user_deps.typ` omits diagraph; `test_e9_package_missing_from_user_deps_is_not_compared` asserts `diagraph:0.1.0` gives no line while `mitex:0.2.5` in the same file warns; code `if not deps_versions: continue`. Passed (exit 0).
- ✅ T003/AC5 — E10/C1: `strip_typst_comments()` is a character scanner (strings copied through with escapes, nested `/* */` with depth counting, `//` to EOL); TestE10Comments asserts no warning for `//`, `/* */`, nested `/* /* */ */` and a trailing `//` after code, and `test_url_string_does_not_hide_a_real_pin` asserts the pin after `"https://example.com"` on the same line still warns; unit tests cover each scanner branch. Passed (exit 0).
- ✅ T003/AC6 — scan input is the list `_copy_bundle_directory()` now returns (appended only after a successful `shutil.copy2`, post `_is_excluded_bundle_entry` filtering), filtered to `.typ`; TestScanScope asserts an unused key, `.git/` and `backup.typ~` are not scanned, a `typst_package`-only key produces no `_template/` and no warning; scan opens files read-only (`read_bytes`); `_assert_byte_identical` and the Verify's `cmp "$d/p/_tpl/base.typ" "$d/out/_template/typst/base.typ"` confirm byte-identical copies.
- ✅ T003/AC7 — Verify embeds the PLAN "sphinx-build console output" walkthrough: real `sphinx-build -E -b typst` with a `gentle-clues:1.2.0` pin plus a commented `codly:1.0.0` pin, `grep -c` = 1 line naming `'_template/typst/base`, `gentle-clues:1.2.0`, `gentle-clues:1.3.1`, then rerun with 1.3.1 and `grep -c` = 0; chain exit 0 (rc=0 required by `&&`). Reviewer probe in the sidecar: non-`-E` rebuild of the same project also prints exactly 1 drift line each time.
- ✅ T003/IF1 — K1: `typst_deps.py` stays a leaf (only `re`, `dataclasses` imported); new `strip_typst_comments`, `extract_preview_versions`, `version_sort_key` added; existing K1 exports untouched.
- ✅ T003/IF2 — K2: `_write_dependencies_file()` remains the first statement of `finish()`; the drift scan reads the file it left.
- ✅ T003/IF3 — K4: branch on `getattr(self.config, "typst_dependencies", None) is None`; non-None values were already validated by T002 in `write()`.
- ✅ T003/IF4 — K5: message f-string matches `template dependency drift: {quote_path(relpath)} pins @preview/{package}:{template_versions}, but _typsphinx/deps.typ has @preview/{package}:{deps_version}` exactly; `relpath` = `_template/<key>/<rel>` POSIX; differing versions sorted by `version_sort_key` and joined `, ` (`test_several_versions_in_one_file_sorted_numerically`: `1.2.0, 1.10.0`).
- ✅ Point (a), several user-pinned versions of one package: acceptable implementation decision. SC4 and K5 speak of "that package's version" (singular) and no edge (E7–E10) or prohibition rules a multi-version `deps.typ`; for the normal single-version case (always true of the default) the rule reduces exactly to SC4's "version different from", and listing all user versions in `{deps_version}` keeps the K5 shape. No conflict with any criterion.

Warnings (non-blocking):
- Scanner limit (markup-mode `"` treated as a string delimiter) is documented in the docstring and accepted under INTENT Risks bullet 4.
- Orchestrator Verify output tail shows only `uv sync` lines; the evidence is the recorded exit 0 of the `&&` chain.

Contract violations (blocking):
- none — changed paths: `typsphinx/typst_deps.py`, `typsphinx/builder.py`, `tests/test_template_dependency_drift_gate.py`, `tests/fixtures/template_dependency_drift/*`, and the task file (only `status`/`agent`/`base` plus appended Log).

## T004 — Remove the five-package pins and top-level codly init from the repository's own templates and samples: pass

- ✅ T004/AC1 — SC5 grep over the four directories in the review sidecar exits 1 with no output; also the first step of the orchestrator Verify (exit 0).
- ✅ T004/AC2 — diff of the five templates replaces the four pins and `#show: codly-init.with()` / `#codly(languages: codly-languages)` with `#import "/_typsphinx/deps.typ": *` only; Verify's `! grep -nE 'codly-init|codly\(languages'` over those five files passes; srcdir-shadow fixture keeps its CONF-12/D-I header and `lang` signature; `tests/test_typst_lang_gate.py` and `tests/test_admonition_greyscale_pipeline.py` run in Verify, exit 0.
- ✅ T004/AC3 — `tests/test_preview_version_sync.py`: `test_example_templates_match_canonical_versions` and its helper removed; `test_repo_templates_pin_none_of_the_five` walks `NO_PIN_DIRS` (the four dirs, asserted to exist) with `_FIVE_SPEC_RE`; `test_no_pin_check_catches_a_reintroduced_pin` proves the scan flags a pinned file; SC1 tests unchanged in the diff.
- ✅ T004/AC4 — Verify builds `examples/basic`, `examples/advanced`, `docs/source` with `-b typstpdf` and checks `basic-example.pdf`, `advanced-example.pdf`, `ls docs/*.pdf`; chain exit 0. `examples/advanced` `conf.py`/`README.md` commented sample rewritten to a pin-free `typst_package` + item-name `typst_package_imports` use; option names and behaviour unchanged (veto respected).
- ✅ T004/IF1 — K3: templates import `/_typsphinx/deps.typ` root-absolute and rely on the wrapper applying `typsphinx-init`, matching K3.

Warnings (non-blocking):
- none

Contract violations (blocking):
- none — every changed path is in `files` plus the task file (fields `status`/`agent`/`base` and appended Log only).

## T005 — Document typst_dependencies and the public /_typsphinx/deps.typ contract, record the change in CHANGELOG and CLAUDE.md, and prove the final quality bar: pass

- ✅ T005/AC1 — `configuration.rst` new "Typst Dependencies" subsection: path rule (srcdir-relative or absolute, resolved like `typst_template`), one global file, byte-identical verbatim copy, generated default when `None`, build stop with `typst_dependencies:` message; four rows added to "When the Build Stops" with the T002 fragments.
- ✅ T005/AC2 — `templates.rst` "Package Dependencies (deps.typ)": path `/_typsphinx/deps.typ`, table with all sixteen names; warning that output with a replaced `deps.typ` is not guaranteed because the translator emits calls written against the default versions' APIs. Point (b): reviewer compiled (typst-py, sidecar) a probe that imports exactly `codly, codly-init, codly-languages, mi, mitex, render, abstract, danger, error, info, memo, notify, task, tip, warning, typsphinx-init` by name from the generated default `render_default_deps()` file and calls the nine gentle-clues functions and `mi` — compiled `ok`; `grep '_visit_admonition('` in `translator.py` yields exactly the nine documented gentle-clues names. The documented list matches the names the default file exports (it re-exports more via `*`; the table is headed "Exported names typsphinx relies on").
- ✅ T005/AC3 — `templates.rst` "Take package names from deps.typ, do not pin versions" with `#import "/_typsphinx/deps.typ": info, codly` example; `output_layout.rst` names `_typsphinx/` reserved next to `_template/` and states the outdir compile root / `--root` rule.
- ✅ T005/AC4 — CHANGELOG `## [Unreleased]` gains `### Added` (deps.typ + `typsphinx-init`, `typst_dependencies`, drift warning) and `### Changed` (single source, in-repo cleanup, hand-compile root), `### Planned for Future Releases` kept; `tests/test_release_0_9_8_docs_gate.py` only relaxes the Unreleased check to "contains Planned for Future Releases", 0.9.8 tests untouched; run in Verify, exit 0.
- ✅ T005/AC5 — CLAUDE.md `@preview` section rewritten: single source `DEFAULT_PACKAGES` in `typsphinx/typst_deps.py`, generated `<outdir>/_typsphinx/deps.typ`, "three places" wording gone; `writer.py` bullet names the two-line preamble; `template_engine.py` bullet says it emits the same preamble and hard-codes no version; toolchain-pin and NixOS sections unchanged in the diff.
- ✅ T005/AC6 — `tests/test_deps_contract_docs_gate.py` derives exports from `render_default_deps()` plus translator `_visit_admonition` call sites; Verify runs it with the other two gates, then `sphinx-build -E -b html docs/source` and greps `typst_dependencies` in `configuration.html` and `/_typsphinx/deps` in `templates.html`; exit 0. Reviewer HTML build in the sidecar (`-q -E -b html`) printed no warnings; rendered text of templates.html contains `/_typsphinx/deps.typ`, all sixteen names, "not guaranteed", "own risk", "template dependency drift".
- ✅ T005/AC7 — orchestrator Verify (sidecar task-t005-verify) pass, exit 0, chain includes `LC_ALL=C uv run pytest tests/`, `uv run black --check .` (tail: "394 files would be left unchanged"), `uv run ruff check .`, `uv run mypy typsphinx/`; coder Log 1825 passed / 1 skipped / 0 failed. Base c7403260 contains the T003 (761ebf7b) and T004 (e89e4571) landings.
- ✅ T005/IF1 — K3: documented path, preamble lines and sixteen names match the generated default (probe above).
- ✅ T005/IF2 — K4: documented `None` default, srcdir-relative/absolute resolution, byte-identical copy and the `typst_dependencies:` error fragments match T002's messages (`expected a file path (str) or None`, `empty path`, `file not found:`, `not a regular file:`).
- ✅ T005/IF3 — K5: `templates.rst` warning sample `template dependency drift: '_template/<key>/<file>.typ' pins @preview/<package>:<template version>, but _typsphinx/deps.typ has @preview/<package>:<deps.typ version>` follows the K5 text.

Warnings (non-blocking):
- Orchestrator Verify tail does not show the pytest summary line; SC7 evidence is the recorded exit 0 of the `&&` chain plus the coder's count.

Contract violations (blocking):
- none — every changed path is in `files` plus the task file (fields `status`/`agent`/`base` and appended Log only); no `.py` under `typsphinx/` touched.

## Intent coverage

### SC4 — sphinx-build console output, drift warning: when any `.typ` file in a used template bundle contains `@preview/<one of the five>:<version>` with a version different from that package's version in the effective `deps.typ` (the user's file when `typst_dependencies` is set, else the defaults), the build prints one warning per (file, package) naming the file, the package, the template's version and the `deps.typ` version, and still exits 0; with matching versions, or no such import, no warning is printed.: pass
- ✅ T003/AC1–AC5, AC7 evidence above. Held-out edges, recorded output = T003 orchestrator Verify exit 0 running `tests/test_template_dependency_drift_gate.py`: E7 (`TestE7Adjacency`), E8 (`TestE8Ordering`), E9 (`test_e9_package_missing_from_user_deps_is_not_compared`), E10 (`TestE10Comments`, C1 comment exclusion). N2: drift is `logger.warning` only, build exits 0 (asserted in every integration test's `_build`). Surface "sphinx-build console output" walkthrough executed in T003 Verify (one line naming `'_template/typst/base.typ'`, `gentle-clues`, `1.2.0`, `1.3.1`, none for the commented codly; 0 after switching to 1.3.1).

### SC5 — In-repo templates: `grep -rnE '@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):' docs/source/_typst/ examples/ tests/fixtures/admonition_greyscale_probe/_templates/ tests/fixtures/typst_lang_gate/` prints nothing; those templates either import nothing from the five or import names from `/_typsphinx/deps.typ`; the docs `typstpdf` build and the examples still build.: pass
- ✅ Reviewer grep at review base e31599c8 prints nothing (rc=1); T004/AC2 shows the five templates import only `/_typsphinx/deps.typ`; T004 Verify built docs, examples/basic and examples/advanced to PDFs (exit 0).

### SC6 — Documentation surface: the configuration page documents `typst_dependencies` (path rule, single global file, verbatim copy, default when unset); a page lists the public `deps.typ` contract — the path `/_typsphinx/deps.typ`, every exported name (`codly`, `codly-init`, `codly-languages`, `mi`, `mitex`, `render`, the gentle-clues admonition functions the translator emits, `typsphinx-init`) — and states that output with a replaced `deps.typ` is not guaranteed because the translator targets the default versions' APIs; the templates page tells template authors to take package names from `/_typsphinx/deps.typ` rather than pinning versions; CHANGELOG `[Unreleased]` records the change; CLAUDE.md's `@preview` version-sync section describes the new single source.: pass
- ✅ T005/AC1–AC6 evidence above; documented export list matches the names the generated default exports (named-import compile probe ok; nine gentle-clues names equal the translator's `_visit_admonition` set). N4 (judgment): observed both pages say only the default versions are supported, output with a replaced `deps.typ` "is not guaranteed to compile or to render correctly", "used at your own risk"; CHANGELOG repeats "not guaranteed"; no wording calls another version compatible or tested — no promise of correct output. Surface "typsphinx documentation" walkthrough: reviewer HTML build, configuration.html and templates.html checked (steps 2–3), CHANGELOG/CLAUDE.md read (step 4).

### SC7 — On the final HEAD, `LC_ALL=C uv run pytest tests/` reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean.: pass
- ✅ T005 orchestrator Verify at landing bdbcdd17 (contains T001–T004; review base e31599c8 differs only by `.project/build/verify-ledger.jsonl`) exit 0 over full pytest under `LC_ALL=C`, black, ruff, mypy; coder Log 1825 passed / 1 skipped / 0 failed.

## Summary for orchestrator

- blocked findings: none
- repeat offenders: none
- warnings worth a human eye: orchestrator Verify output tails for T003/T005 show only dependency-sync / black lines, so test counts rest on exit status and coder Logs; T003 multi-version `deps.typ` rule is an unruled implementation decision judged acceptable
