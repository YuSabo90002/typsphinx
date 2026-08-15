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
