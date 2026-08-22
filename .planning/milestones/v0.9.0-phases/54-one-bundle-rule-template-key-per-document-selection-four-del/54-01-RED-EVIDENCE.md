# Phase 54 Plan 01 — RED Evidence

Recorded against commit `a49b03d85b372dc4a393ec404df5fff037118bc2` (the pre-relocation tree —
Phase 54's production code, `typsphinx/*.py`, is untouched by this plan).

Each section below records one real `sphinx-build` (or `sphinx-build -b typst`/`-b typstpdf`)
compile against the tree at that commit, showing the real behaviour BEFORE the per-key bundle
relocation lands (in `54-04`). The built-in template is not used as evidence anywhere below (SC#3);
every fixture is a genuinely new user/registry-keyed template.

## OUT-05

**Fixture:** `tests/fixtures/user_template_relative_asset_gate/` — a USER-supplied template
(`_typst/branded.typ`) whose body calls `#image("logo.png", width: 24pt)` on a same-directory
asset (`_typst/logo.png`).

**Command:**

```
uv run pytest tests/test_user_template_relative_asset_gate.py -x
```

**Result:** `1 failed in 0.32s` (stopped at the first failure under `-x`; the full unfiltered run
is 4 failed / 0 errors — see the acceptance-criteria measurement below).

**Verbatim tail:**

```
E             Compiling 1 master document(s) to PDF...
E
E         Loaded Extensions
E         =================
E
E         * sphinx.ext.mathjax (9.1.0)
E         * alabaster (1.0.0)
E         * sphinxcontrib.applehelp (2.0.0)
E         * sphinxcontrib.devhelp (2.0.0)
E         * sphinxcontrib.htmlhelp (2.1.0)
E         * sphinxcontrib.serializinghtml (2.0.0)
E         * sphinxcontrib.qthelp (2.0.0)
E         * typsphinx (0.8.0)
E
E         Traceback
E         =========
E
E               File ".../typsphinx/builder.py", line 1677, in finish
E                 raise ExtensionError(
E                     f"typstpdf: {len(failures)} master document(s) failed: {summary}"
E                 )
E             sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation failed: TypstError: file not found (searched at /tmp/pytest-of-yuta/pytest-1297/user_template_relative_asset_gate_build0/logo.png)
E             Location: /tmp/pytest-of-yuta/pytest-1297/user_template_relative_asset_gate_build0/master.typ
E             Details: file not found (searched at /tmp/pytest-of-yuta/pytest-1297/user_template_relative_asset_gate_build0/logo.png)
E
E
E         The full traceback has been saved in:
E         /tmp/sphinx-err-hhepqmc4.log
E
E       assert 2 == 0
E        +  where 2 = CompletedProcess(args=[..., '-m', 'sphinx', '-b', 'typstpdf', ...],
E             returncode=2, stdout='...preparing documents... Template written to
E             /tmp/pytest-of-yuta/pytest-1297/user_template_relative_asset_gate_build0/_template.typ
E             \ndone\nwriting output... [index] done\ntypst: wrote 1 wrapper file(s) -- compile
E             these: master.typ\nCopying template assets...\nCopied 1 template asset(s) from
E             _typst/\nCompiling 1 master document(s) to PDF...\n', stderr='Typst compilation
E             failed at .../master.typ: TypstError: file not found (searched at
E             .../logo.png)...').returncode

tests/test_user_template_relative_asset_gate.py:102: AssertionError
=========================== short test summary info ============================
FAILED tests/test_user_template_relative_asset_gate.py::TestUserTemplateRelativeAssetGate::test_build_succeeds
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
============================== 1 failed in 0.32s ===============================
```

**Full run (no `-x`), confirming zero errors:** `4 failed in 0.83s` — `test_build_succeeds`,
`test_pdf_is_valid`, `test_asset_reached_the_bundle_destination`, and
`test_wrapper_imports_the_bundled_template` all FAIL; zero ERRORS (no verification failure leaked
into the class-scoped `build` fixture).

**Why it is RED on this tree:** today `_write_template_file()` writes the template body verbatim
to a single file at the OUTDIR ROOT (`_template.typ`, stdout: "Template written to
.../\_template.typ"), while `copy_template_assets()`/`_copy_template_directory()` copies the
bundle's non-`.typ` files to a SOURCE-relative destination (stdout: "Copied 1 template asset(s)
from `_typst/`", i.e. `<outdir>/_typst/logo.png`). The template file and its relative asset land
in two different directories, so `#image("logo.png")` — resolved relative to the compiled file's
own location, `<outdir>/_template.typ` — has nothing to resolve against; Typst reports
`file not found (searched at <outdir>/logo.png)`. There is no per-key bundle directory at all on
this tree, which is exactly what `54-04`'s relocation introduces.

## TPL-02 / OUT-06

**Fixture:** `tests/fixtures/two_key_selection_gate/` — two `typst_document_templates` registry
keys (`"report"`, `"memo"`), with the `"report"` key selected by two `typst_documents` entries at
two different wrapper nesting depths (root `master` and nested `manuals/guide`).

**Command:**

```
uv run pytest tests/test_two_key_selection_gate.py tests/test_bundle_copy_exclusion_manifest_gate.py
```

**Result:** `5 failed, 5 passed in 0.74s` — zero errors.

**Two_key_selection_gate failures (verbatim assertions):**

```
FAILED tests/test_two_key_selection_gate.py::TestTwoKeySelectionGate::test_both_report_wrappers_emit_an_identical_import_string
  AssertionError: the two 'report'-keyed wrappers do not emit an identical root-absolute import string:
  master: '_template.typ'
  guide: '../_template.typ'
  assert '_template.typ' == '../_template.typ'

FAILED tests/test_two_key_selection_gate.py::TestTwoKeySelectionGate::test_memo_wrapper_imports_its_own_key
  AssertionError: memo wrapper does not import its own key's bundle: '../_template.typ'
  assert '../_template.typ' == '/_template/memo/base.typ'

FAILED tests/test_two_key_selection_gate.py::TestTwoKeySelectionGate::test_both_bundles_are_published
  AssertionError: the 'report' bundle was not published to <outdir>/_template/report/base.typ
  assert False
   +  where False = exists()
```

`test_build_succeeds`, `test_three_pdfs_produced`, and
`test_the_two_templates_produce_different_pdfs` all PASS today — the build succeeds and produces
three distinct PDFs, because `render_wrapper()` already threads `template_entry` per document
(Phase 53); what fails is specifically OUT-06's root-absolute, depth-independent import contract.

**Why it is RED on this tree:** the writer still computes the template import path with
`compute_template_import_path_for_dir()`, a DEPTH-COUNTED `"../"` relative path
(`writer.py:69-106`) rather than a root-absolute `/_template/<key>/<file>.typ` string — the root
wrapper gets `_template.typ` and the nested wrapper gets `../_template.typ`, two DIFFERENT
strings for the SAME registry key, and both point at the single shared `_template.typ` written at
the outdir root rather than a per-key bundle. No per-key bundle directory (`_template/report/`,
`_template/memo/`) exists on this tree at all.

## BLD-06 / OUT-04

**Fixture:** `tests/fixtures/bundle_exclusion_manifest_gate/` — one registry key (`"styled"`)
whose bundle carries a nested non-`.typ` asset (`_typst/styled/assets/note.txt`); the test module
injects the four D-04 excluded kinds (`.git/config`, `.DS_Store`, `Thumbs.db`, `notes.txt~`) into
a fresh copy of the fixture at runtime.

**Command:** (same combined run as TPL-02/OUT-06 above)

**Verbatim failures:**

```
FAILED tests/test_bundle_copy_exclusion_manifest_gate.py::TestBundleCopyExclusionManifestGate::test_bundle_manifest_is_exactly_the_expected_set
  AssertionError: the 'styled' bundle was not published to
  /tmp/pytest-of-yuta/pytest-1302/bundle_exclusion_manifest_gate_build0/_template/styled:
    stdout: ...preparing documents... Template written to
    /tmp/pytest-of-yuta/pytest-1302/bundle_exclusion_manifest_gate_build0/_template.typ
    done
    writing output... [index] done
    typst: wrote 1 wrapper file(s) -- compile these: master.typ
    build succeeded.
  assert False
   +  where False = exists()
   +    where exists = PosixPath('.../bundle_exclusion_manifest_gate_build0/_template/styled').exists

FAILED tests/test_bundle_copy_exclusion_manifest_gate.py::TestBundleCopyExclusionManifestGate::test_rerun_leaves_a_removed_source_file_in_place
  AssertionError: note.txt was not published by the first build at
  .../bundle_exclusion_manifest_gate_build0/_template/styled/assets/note.txt
  assert False
   +  where False = exists()
```

`test_build_succeeds` and `test_each_excluded_kind_is_named_in_the_expected_set_comment` PASS
(the plain `-b typst` build succeeds today, and the module's own text does enumerate the four D-04
literals) — what fails is specifically the manifest-diff claim, because there is no
`<outdir>/_template/styled/` bundle directory to diff against at all.

**Why it is RED on this tree:** `_template/<key>/` does not exist as a destination shape today —
`copy_template_assets()`/`_copy_template_directory()` copies non-`.typ` bundle files to a
SOURCE-relative destination under `<outdir>/_typst/styled/...`, never under a `_template/`
prefix, so both the manifest-equality assertion and the incremental-rebuild
(`test_rerun_leaves_a_removed_source_file_in_place`) assertion fail on the same missing
directory.

## Handover

All three modules above are marked `@pytest.mark.xfail(strict=False, reason="Phase 54: green
only once the per-key bundle relocation lands in 54-04; RED recorded in
54-01-RED-EVIDENCE.md")` as of this plan's Task 3, so the full suite (`uv run pytest tests/ -q`)
stays green at this phase boundary (ROADMAP binding constraint #2) while the real RED evidence
above remains on record (constraint #6). `strict=False` is deliberate: once `54-04` lands the
bundle relocation but before its own task removes these markers, the tests XPASS, and a strict
marker would turn that XPASS into a failure — inverting the gate exactly when it starts working.

**`54-04` Task 3 removes the `xfail` marker from each of the three modules below and proves the
suite green for real:**

- `tests/test_user_template_relative_asset_gate.py`
- `tests/test_two_key_selection_gate.py`
- `tests/test_bundle_copy_exclusion_manifest_gate.py`
