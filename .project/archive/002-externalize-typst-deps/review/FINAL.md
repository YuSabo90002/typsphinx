# Final Review — typsphinx

Repo root: /home/yuta/Documents/typsphinx
Reviewed HEAD: 92714623a5c622f9f4a59ef978f82efb2ef5b323
Overall verdict: pass

## Success criteria

### SC1 — Single version source: under `typsphinx/` (all `.py` and `.typ` files, `templates/base.typ` included), `grep -rnE '@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):' typsphinx/` matches only the one Python module that defines the default specs; `typsphinx/writer.py`, `typsphinx/template_engine.py`, and `typsphinx/templates/base.typ` contain no such literal and no `codly-init` / `codly(languages:` initialisation lines; a test asserts the generated `deps.typ` content equals the definitions in that module.

- **Verdict**: met
- **Check**: `grep -rnE '@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):' typsphinx/` and `grep -nE 'codly-init|codly\(languages' typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ` in the review sidecar at 92714623; recorded project Verify for the module-equality test
- **Observed**: first grep matches only `typsphinx/typst_deps.py` (docstring line 41 and the five `DEFAULT_PACKAGES` entries at lines 66-70); second grep exits 1 (no init lines in the three files). `tests/test_preview_version_sync.py` (asserts the built deps.typ equals `render_default_deps()` from `DEFAULT_PACKAGES`) passed in the sidecar (79 passed across the five gate files) and in project Verify (1808 passed, 0 failed). E1 and N5 are dismissed in INTENT.
- **Reference**: typsphinx/typst_deps.py:66-70; tests/test_preview_version_sync.py; .project/build/verify-ledger.jsonl (commit 92714623); .project/review/final-gap-1.md
- **Finding**: none
- **Fix direction**: none

### SC2 — Generated output tree, default (no `typst_dependencies`): a `typst` build writes `<outdir>/_typsphinx/deps.typ` that imports the five packages at the default versions and defines `typsphinx-init`; every content `.typ` and every wrapper `.typ` in the output imports `/_typsphinx/deps.typ`, applies `#show: typsphinx-init`, and contains no `#import "@preview/<five>:...` line (escaped body text that quotes such a spec, e.g. CHANGELOG history rendered into `changelog.typ`, is not an import) (C2); `examples/basic`, `examples/advanced`, and the project docs build with `typstpdf` to a PDF, and the existing render-gate tests (codly code blocks with highlights, admonitions, inline/block math, graphviz) pass unchanged in what they assert about rendered output.

- **Verdict**: met
- **Surface**: generated Typst output tree
- **Check**: Walkthrough steps 1-3 in the sidecar: `uv sync --extra dev --extra docs`; `LC_ALL=C uv run sphinx-build -E -b typstpdf examples/basic $d/basic`, `cat $d/basic/_typsphinx/deps.typ`, `head -3 $d/basic/index.typ $d/basic/basic-example.typ`, the five-spec literal grep excluding `_typsphinx`/`_template`; same `-b typstpdf` build of `examples/advanced` and `docs/source` with a per-file preamble check over every content/wrapper `.typ` and a `^\s*#import "@preview/<five>:` grep; held-out tests `LC_ALL=C uv run pytest tests/test_typst_dependencies_gate.py tests/test_deps_output_gate.py ...`
- **Observed**: success state: examples/basic rc=0, `basic-example.pdf` written (86101 bytes); deps.typ holds `@preview/codly:1.3.0`, `@preview/codly-languages:0.1.10`, `@preview/mitex:0.2.7` (`mi, mitex`), `@preview/gentle-clues:1.3.1`, `@preview/diagraph:0.3.7` (`render`) and `#let typsphinx-init(body)`; both `index.typ` and `basic-example.typ` start `#import "/_typsphinx/deps.typ": *` / `#show: typsphinx-init`; literal grep rc=1. loading state: progress lines then `typst: wrote 1 wrapper file(s) -- compile these: basic-example.typ`. examples/advanced -> `advanced-example.pdf` (4 `.typ`, all with preamble); docs/source rc=0 -> `typsphinx.pdf` (17 `.typ`, all with preamble), import grep rc=1 for both; the only literal is in `docs/changelog.typ` as escaped body text (`raw("#import \"@preview/codly:1.3.0\": *")`, `strong({raw("@preview/diagraph:0.3.7")`), which C2 excludes. Held-out E2: `TestRebuildAndSwitch::test_rebuilds_identical_bytes[set]`, `[unset]`, `test_set_then_unset_then_set` PASSED. Held-out E3 (empty state): `TestPlainDocumentStillImportsDeps::test_plain_content_and_wrapper_carry_preamble` PASSED. Render gates (codly, admonition, math, graphviz) are in the project Verify run (1808 passed, 0 failed); wave-1 review found their diffs change only import/init-shape assertions and all 11 golden diffs identical (N1).
- **Reference**: .project/plan/PLAN.md Surface contract "generated Typst output tree"; tests/test_typst_dependencies_gate.py; tests/test_deps_output_gate.py; .project/review/wave-1.cycle1.md (T001/AC3); .project/build/verify-ledger.jsonl (92714623)
- **Finding**: none
- **Fix direction**: none

### SC3 — Generated output tree, override: with `typst_dependencies = "<srcdir-relative path>"`, the build copies that one file byte-identical to `<outdir>/_typsphinx/deps.typ` and generates no default file; a fixture whose own `deps.typ` uses a different, compiler-compatible version of one package (e.g. gentle-clues 1.3.0) builds with `typstpdf`, and its content files and wrappers import only `/_typsphinx/deps.typ`. A `typst_dependencies` path that does not exist stops the build with an error naming the configured value.

- **Verdict**: met
- **Surface**: generated Typst output tree
- **Check**: Walkthrough steps 4-5 in the sidecar: `cp -r tests/fixtures/typst_dependencies_override $d/p`; `LC_ALL=C uv run sphinx-build -E -b typstpdf $d/p $d/out`; `cmp $d/p/deps/my-deps.typ $d/out/_typsphinx/deps.typ`; `ls -A $d/out/_typsphinx`; import lines of every content/wrapper `.typ`; then append `typst_dependencies = "missing/deps.typ"` and build into `$d/out2`; held-out tests in `tests/test_typst_dependencies_gate.py`
- **Observed**: success state: rc=0, `depsoverride.pdf` written; `cmp` silent (rc=0); `_typsphinx/` contains only `deps.typ`; it pins `@preview/gentle-clues:1.3.0`; `index.typ` imports only `/_typsphinx/deps.typ`, wrapper `depsoverride.typ` imports `/_typsphinx/deps.typ` plus the template `/_template/typst/base.typ` (no package import), each with one `#show: typsphinx-init`. error state: rc=2, stderr `ExtensionError: typst_dependencies: file not found: 'missing/deps.typ' (resolved to '.../p/missing/deps.typ')`, 0 `.typ` files in the new outdir. Held-out E4: `TestNoneAndEmpty::test_explicit_none_generates_default` and `test_empty_string_refused` PASSED. Held-out E6: `TestAbsoluteAndBytes::test_absolute_path_builds` and `test_crlf_non_ascii_no_trailing_newline_byte_identical` PASSED. N3: copy is byte-identical (`cmp`) and the source fixture is unchanged (CRLF test asserts source bytes).
- **Reference**: tests/fixtures/typst_dependencies_override/; tests/test_typst_dependencies_gate.py; .project/review/wave-1.cycle1.md (T002)
- **Finding**: none
- **Fix direction**: none

### SC4 — sphinx-build console output, drift warning: when any `.typ` file in a used template bundle contains `@preview/<one of the five>:<version>` with a version different from that package's version in the effective `deps.typ` (the user's file when `typst_dependencies` is set, else the defaults), the build prints one warning per (file, package) naming the file, the package, the template's version and the `deps.typ` version, and still exits 0; with matching versions, or no such import, no warning is printed.

- **Verdict**: met
- **Surface**: sphinx-build console output
- **Check**: Walkthrough in the sidecar: copy `examples/basic` to `$d/q`, copy `typsphinx/templates/base.typ` to `$d/q/_tpl/base.typ`, append `#import "@preview/gentle-clues:1.2.0": *` and `// #import "@preview/codly:1.0.0": *`, set `typst_template = "_tpl/base.typ"`; `LC_ALL=C uv run sphinx-build -E -b typst $d/q $d/qout 2> err.txt`; then pin 1.3.1 and rebuild; held-out tests in `tests/test_template_dependency_drift_gate.py`
- **Observed**: success state: rc=0, exactly one line `WARNING: template dependency drift: '_template/typst/base.typ' pins @preview/gentle-clues:1.2.0, but _typsphinx/deps.typ has @preview/gentle-clues:1.3.1`, no line for the commented codly pin, `build succeeded, 2 warnings.`; copied bundle file byte-identical (`cmp` rc=0). empty state: with 1.3.1, rc=0 and `grep -c 'template dependency drift'` = 0. Held-out E7: `TestE7Adjacency::test_other_package_and_other_namespace_are_ignored` PASSED. E8: `TestE8Ordering::test_one_warning_per_file_and_package_in_sorted_order` PASSED. E9: `TestSC4OverrideMode::test_e9_package_missing_from_user_deps_is_not_compared` PASSED. E10 (C1): `TestE10Comments::test_pins_inside_comments_do_not_warn` and `test_url_string_does_not_hide_a_real_pin` PASSED, and the commented codly pin above did not warn. N2: drift never fails the build (rc=0 observed).
- **Reference**: typsphinx/builder.py `_warn_template_dependency_drift`; tests/test_template_dependency_drift_gate.py; .project/review/wave-2.cycle1.md (T003)
- **Finding**: none
- **Fix direction**: none

### SC5 — In-repo templates: `grep -rnE '@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):' docs/source/_typst/ examples/ tests/fixtures/admonition_greyscale_probe/_templates/ tests/fixtures/typst_lang_gate/` prints nothing; those templates either import nothing from the five or import names from `/_typsphinx/deps.typ`; the docs `typstpdf` build and the examples still build.

- **Verdict**: met
- **Check**: `grep -rnE '@preview/(codly|codly-languages|mitex|gentle-clues|diagraph):' docs/source/_typst/ examples/ tests/fixtures/admonition_greyscale_probe/_templates/ tests/fixtures/typst_lang_gate/`; `grep -rn '_typsphinx/deps.typ'` over the same paths; `-b typstpdf` builds of docs/source, examples/basic, examples/advanced (see SC2)
- **Observed**: first grep prints nothing (rc=1); the five templates (`docs/source/_typst/custom_template.typ:43`, `examples/advanced/_typst/custom.typ:12`, `admonition_greyscale_probe/_templates/minimal.typ:18`, `typst_lang_gate/custom_template_lang/_templates/custom.typ:15`, `typst_lang_gate/srcdir_shadow_lang/_typst/base.typ:20`) import `#import "/_typsphinx/deps.typ": *`; docs -> `typsphinx.pdf`, basic -> `basic-example.pdf`, advanced -> `advanced-example.pdf`, all rc=0. `tests/test_preview_version_sync.py` no-pin gate passed in the sidecar. E11 and N6 dismissed.
- **Reference**: tests/test_preview_version_sync.py; .project/review/wave-2.cycle1.md (T004)
- **Finding**: none
- **Fix direction**: none

### SC6 — Documentation surface: the configuration page documents `typst_dependencies` (path rule, single global file, verbatim copy, default when unset); a page lists the public `deps.typ` contract — the path `/_typsphinx/deps.typ`, every exported name (`codly`, `codly-init`, `codly-languages`, `mi`, `mitex`, `render`, the gentle-clues admonition functions the translator emits, `typsphinx-init`) — and states that output with a replaced `deps.typ` is not guaranteed because the translator targets the default versions' APIs; the templates page tells template authors to take package names from `/_typsphinx/deps.typ` rather than pinning versions; CHANGELOG `[Unreleased]` records the change; CLAUDE.md's `@preview` version-sync section describes the new single source.

- **Verdict**: met
- **Surface**: typsphinx documentation (configuration and templates pages)
- **Check**: Walkthrough in the sidecar: `uv sync --extra dev --extra docs`; `LC_ALL=C uv run sphinx-build -E -b html docs/source $d/html`; read the rendered text of `user_guide/configuration.html` and `user_guide/templates.html`; read CHANGELOG.md `## [Unreleased]` and CLAUDE.md `### The @preview version-sync hazard`
- **Observed**: HTML build rc=0, no Sphinx warnings (error state absent). configuration.html "Typst Dependencies": path rule (srcdir-relative or absolute, resolved like `typst_template`), "One global file", "Verbatim copy ... byte-identical", "Default when unset ... None", "Build stop" with `typst_dependencies:` prefix, and four `typst_dependencies:` rows in "When the Build Stops". templates.html "Package Dependencies (deps.typ)": path `/_typsphinx/deps.typ`, public-contract statement, table listing `codly`, `codly-init`, `codly-languages`, `mi`, `mitex`, `abstract`, `danger`, `error`, `info`, `memo`, `notify`, `task`, `tip`, `warning`, `render`, and `typsphinx-init` (all sixteen); "Take package names from deps.typ, do not pin versions" with `#import "/_typsphinx/deps.typ": info, codly`; drift-warning sample. N4 (judgment): both pages say "Only the default package versions are supported", output with a replaced `deps.typ` "is not guaranteed to compile or to render correctly", "a replaced file is used at your own risk"; CHANGELOG repeats "not guaranteed"; no text claims any other version works, so no promise of correct output is made. CHANGELOG `[Unreleased]` has Added (deps.typ, `typst_dependencies`, drift warning) and Changed (single source, in-repo templates, compile root). CLAUDE.md section names `DEFAULT_PACKAGES` in `typsphinx/typst_deps.py` as the single source; no "three places" wording remains. `tests/test_deps_contract_docs_gate.py` passed in the sidecar.
- **Reference**: docs/source/user_guide/configuration.rst; docs/source/user_guide/templates.rst; CHANGELOG.md; CLAUDE.md:64-66; .project/review/wave-2.cycle1.md (T005)
- **Finding**: none
- **Fix direction**: none

### SC7 — On the final HEAD, `LC_ALL=C uv run pytest tests/` reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean.

- **Verdict**: met
- **Check**: recorded project Verify (not re-run): `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/`; plus, in the docs-extra sidecar, `LC_ALL=C uv run pytest tests/test_bibliography_docs_gate.py tests/test_changelog_page_gate.py tests/test_corpus_gate.py tests/test_graphviz_docs_gate.py -rs` (the four files whose tests skipped under `--extra dev`)
- **Observed**: ledger at 92714623: exit 0, `1808 passed, 18 skipped`, 0 failed; black `394 files would be left unchanged.`; ruff `All checks passed!`; mypy `Success: no issues found in 10 source files`. With `--extra docs` the skipped files ran: `48 passed, 1 skipped` (the one skip is env-gated `TYPSPHINX_CORPUS_REPORT=1`), 0 failed. final-gap-1 = pass. E13 and N7 dismissed.
- **Reference**: .project/build/verify-ledger.jsonl (last line, commit 92714623); .project/review/final-gap-1.md
- **Finding**: none
- **Fix direction**: none
