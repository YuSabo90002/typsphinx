# Phase 59 — Windows URI Evidence

This file accumulates the real, recorded runs that prove Phase 59's product changes are neither a
regression nor a tautology. Every command output below is pasted verbatim from a live run in this
worktree; nothing is reconstructed, paraphrased, or asserted from memory.

## Phase base SHA

`git rev-parse HEAD` — this worktree's HEAD before any edit to `typsphinx/builder.py`:

```
PHASE_BASE_SHA=ec6bd3a4714a578379ee45e02295abc31fdd8fe3
```

## PATH-01

### RED (pre-fix, direct call)

Recorded at `PHASE_BASE_SHA` (`ec6bd3a4714a578379ee45e02295abc31fdd8fe3`), before any edit to
`typsphinx/builder.py`. Command:

```
uv run pytest tests/test_path_shape_predicate_gate.py -k escapes_outdir_direct
```

Whole output verbatim (run without `-x` to capture both failures in one transcript; the plan's own
`-x`-suffixed verify command also exits non-zero on this tree, stopping at the first of the two):

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a370176102829d43d/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a370176102829d43d
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 2 items

tests/test_path_shape_predicate_gate.py::TestEscapesOutdirDirectCall::test_escapes_outdir_direct_driveless_absolute_is_true FAILED [ 50%]
tests/test_path_shape_predicate_gate.py::TestEscapesOutdirDirectCall::test_escapes_outdir_direct_unc_is_true FAILED [100%]

=================================== FAILURES ===================================
_ TestEscapesOutdirDirectCall.test_escapes_outdir_direct_driveless_absolute_is_true _

self = <test_path_shape_predicate_gate.TestEscapesOutdirDirectCall object at 0x79f63fb55d10>

    def test_escapes_outdir_direct_driveless_absolute_is_true(self):
        """A driveless-absolute Windows stem -- one leading backslash, no
        drive letter -- must be classified as escaping outdir."""
>       assert _escapes_outdir(r"\manuals\guide") is True
E       AssertionError: assert False is True
E        +  where False = _escapes_outdir('\\manuals\\guide')

tests/test_path_shape_predicate_gate.py:29: AssertionError
______ TestEscapesOutdirDirectCall.test_escapes_outdir_direct_unc_is_true ______

self = <test_path_shape_predicate_gate.TestEscapesOutdirDirectCall object at 0x79f63fb56350>

    def test_escapes_outdir_direct_unc_is_true(self):
        """A UNC-shaped Windows stem -- two leading backslashes, a server
        name, a share name -- must be classified as escaping outdir."""
>       assert _escapes_outdir(r"\\srv\share\g") is True
E       AssertionError: assert False is True
E        +  where False = _escapes_outdir('\\\\srv\\share\\g')

tests/test_path_shape_predicate_gate.py:34: AssertionError
=========================== short test summary info ============================
FAILED tests/test_path_shape_predicate_gate.py::TestEscapesOutdirDirectCall::test_escapes_outdir_direct_driveless_absolute_is_true
FAILED tests/test_path_shape_predicate_gate.py::TestEscapesOutdirDirectCall::test_escapes_outdir_direct_unc_is_true
============================== 2 failed in 0.03s ===============================
```

`2 failed`, zero skipped. Both failures are `assert False is True` for the two shapes PATH-01
names: `_escapes_outdir(r"\manuals\guide")` and `_escapes_outdir(r"\\srv\share\g")` both return
`False` on the unfixed tree. `typsphinx/builder.py` is untouched at this point — confirmed by
`git diff --stat -- typsphinx/builder.py` below.

```
$ git diff --stat -- typsphinx/builder.py
(empty)
```

### Characterization: byte-identical at both call sites

D-09/D-10: `TestEscapesOutdirCallSiteCharacterization` runs THROUGH both production call sites
(`_resolve_target_stem()` and `_track_image()`), parametrized over the five documented shapes
(driveless-absolute, unc, drive-qualified, posix-absolute, ordinary-relative). Command, run
identically against both trees:

```
uv run pytest tests/test_path_shape_predicate_gate.py -k characterization -q
```

**Pre-fix tree.** `git checkout ec6bd3a4714a578379ee45e02295abc31fdd8fe3 -- typsphinx/builder.py`
(restoring the pre-fix `_escapes_outdir()` while keeping the new tests), then the command above —
whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a370176102829d43d
configfile: pyproject.toml
plugins: cov-7.1.0
collected 14 items / 2 deselected / 12 selected

tests/test_path_shape_predicate_gate.py ............                     [100%]

======================= 12 passed, 2 deselected in 0.27s =======================
```

**Post-fix tree.** `git checkout HEAD -- typsphinx/builder.py` (restoring the fixed predicate;
`git diff --stat -- typsphinx/builder.py` confirmed empty immediately after), then the identical
command — whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a370176102829d43d
configfile: pyproject.toml
plugins: cov-7.1.0
collected 14 items / 2 deselected / 12 selected

tests/test_path_shape_predicate_gate.py ............                     [100%]

======================= 12 passed, 2 deselected in 0.21s =======================
```

**The two runs are byte-identical** in every substantive respect: same collection count (14
collected / 2 deselected / 12 selected), same per-test dot pattern (`............`, all 12 pass),
same summary shape (`12 passed, 2 deselected`). The only differing bytes are the wall-clock timing
figures (`0.27s` vs `0.21s`), which is expected run-to-run non-determinism, not a behavioral
difference — no test result (pass/fail) differs between the two trees. This proves `_resolve_target_stem()`
and `_track_image()` classify all five documented shapes identically before and after PATH-01's
fix, exactly as `_RESOLVE_TARGET_STEM_EXPECTED`'s comment and the call sites' own pre-normalization
(`_resolve_target_stem`) / always-carries-`".."` (`_track_image`'s `relpath()` result) predict.

`git status --porcelain typsphinx/builder.py` after the restore, confirming the temporary checkout
left no trace:

```
(empty)
```

## IMG-04 / IMG-06

### RED (pre-fix)

Recorded at `PHASE_BASE_SHA` (`34db72b6567e373a8628c7388efd53cfc981692b`, this plan's own base
commit -- plan 59-01 already merged, `typsphinx/builder.py` still carries the pre-fix
`_track_image()` escape-branch key construction). Command:

```
uv run pytest tests/test_track_image_key_construction.py tests/test_copy_image_files_name_too_long.py -q
```

`git diff --stat -- typsphinx/builder.py` at this point: empty (confirmed above the run; the
product file is untouched by this task).

Whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-add2e5170089418aa
configfile: pyproject.toml
plugins: cov-7.1.0
collected 3 items

tests/test_track_image_key_construction.py FF                            [ 66%]
tests/test_copy_image_files_name_too_long.py F                           [100%]

=================================== FAILURES ===================================
_ TestRelocationKeyNoBackslash.test_relocation_key_no_backslash_for_windows_shaped_uri _

self = <test_track_image_key_construction.TestRelocationKeyNoBackslash object at 0x749441fa5d10>
temp_sphinx_app = <SphinxTestApp buildername='html'>
caplog = <_pytest.logging.LogCaptureFixture object at 0x749440801400>

    def test_relocation_key_no_backslash_for_windows_shaped_uri(
        self, temp_sphinx_app, caplog
    ):
        """A Windows-shaped absolute URI whose basename carries both a
        backslash-delimited directory structure and a literal double
        quote must relocate to a key containing no backslash at all."""
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.init()

        # Raw string: exactly one backslash per Windows path separator,
        # plus one literal double quote in the basename (the D-01 shape
        # this phase's IMG-07 gate later reuses).
        uri = r"C:\Users\runner\assets\sub\we\"ird.png"
        doc = _build_single_image_document(uri)

        with caplog.at_level("WARNING"):
            builder.post_process_images(doc)

        img = doc[0]
        key = img["uri"]

        assert key.startswith(f"{RESERVED_IMAGE_NAMESPACE}/"), (
            f"expected the escape branch to fire and relocate under "
            f"{RESERVED_IMAGE_NAMESPACE!r}, got key {key!r}"
        )
>       assert "\\" not in key, (
            f"relocation key must contain no backslash for a "
            f"Windows-shaped URI, got key {key!r}"
        )
E       AssertionError: relocation key must contain no backslash for a Windows-shaped URI, got key '_typst_converted/ffe13a61-C:\\Users\\runner\\assets\\sub\\we\\"ird.png'
E       assert '\\' not in '_typst_conv...we\\"ird.png'
E
E         '\\' is contained here:
E           _typst_converted/ffe13a61-C:\Users\runner\assets\sub\we\"ird.png
E         ?                             +

tests/test_track_image_key_construction.py:87: AssertionError
------------------------------ Captured log call -------------------------------
WARNING  sphinx.typsphinx.builder:logging.py:138 WARNING: could not rehome image URI 'C:\\Users\\runner\\assets\\sub\\we\\"ird.png' relative to the doctree directory -- relocated to '_typst_converted/ffe13a61-C:\\Users\\runner\\assets\\sub\\we\\"ird.png'
_ TestRelocationKeyLengthBound.test_relocation_key_length_bound_through_track_image _

self = <test_track_image_key_construction.TestRelocationKeyLengthBound object at 0x749441fa6350>
temp_sphinx_app = <SphinxTestApp buildername='html'>
tmp_path = PosixPath('/tmp/pytest-of-yuta/pytest-1635/test_relocation_key_length_bou0')
caplog = <_pytest.logging.LogCaptureFixture object at 0x749440676710>

    def test_relocation_key_length_bound_through_track_image(
        self, temp_sphinx_app, tmp_path, caplog
    ):
        """A 250-character ASCII basename, rehomed through the real
        escape branch, must produce a final path component of at most
        255 UTF-8 bytes.

        Pre-fix this is 263 bytes (9 bytes of ``{digest}-`` plus the
        254-byte basename `"x" * 250 + ".png"`) -- D-06's measured
        "bounding the basename alone still fails" case; this gate proves
        the bound applies to the WHOLE final component, not merely
        caps at 255-minus-nothing.
        """
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.init()

        long_basename = "x" * 250 + ".png"
        # Outside doctreedir (builddir/.doctrees) by construction --
        # tmp_path/"outside"/<basename> never lives under
        # tmp_path/"build"/.doctrees, so the escape branch always fires.
        uri = os.path.join(str(tmp_path), "outside", long_basename)
        doc = _build_single_image_document(uri)

        with caplog.at_level("WARNING"):
            builder.post_process_images(doc)

        img = doc[0]
        final_component = img["uri"].rsplit("/", 1)[-1]
        byte_length = len(final_component.encode("utf-8"))

>       assert byte_length <= 255, (
            f"relocation key's final path component must be at most 255 "
            f"UTF-8 bytes, got {byte_length} bytes: {final_component!r}"
        )
E       AssertionError: relocation key's final path component must be at most 255 UTF-8 bytes, got 263 bytes: 'bfd33c49-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.png'
E       assert 263 <= 255

tests/test_track_image_key_construction.py:129: AssertionError
------------------------------ Captured log call -------------------------------
WARNING  sphinx.typsphinx.builder:logging.py:138 WARNING: could not rehome image URI '/tmp/pytest-of-yuta/pytest-1635/test_relocation_key_length_bou0/outside/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.png' relative to the doctree directory -- relocated to '_typst_converted/bfd33c49-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.png'
_ TestCopyImageFilesNameTooLong.test_copy_image_files_length_bound_no_name_too_long_warning _

self = <test_copy_image_files_name_too_long.TestCopyImageFilesNameTooLong object at 0x749441fa6490>
temp_sphinx_app = <SphinxTestApp buildername='html'>
tmp_path = PosixPath('/tmp/pytest-of-yuta/pytest-1635/test_copy_image_files_length_b0')
caplog = <_pytest.logging.LogCaptureFixture object at 0x7494406b9810>

    def test_copy_image_files_length_bound_no_name_too_long_warning(
        self, temp_sphinx_app, tmp_path, caplog
    ):
        long_basename = "x" * 250 + ".png"

        # In-body filesystem probe (Pitfall 1) -- never a collection-time
        # marker decorator.
        probe_dir = tmp_path / "probe"
        try:
            probe_dir.mkdir(parents=True, exist_ok=True)
            probe_path = probe_dir / long_basename
            probe_path.write_bytes(b"probe")
            probe_path.unlink()
        except OSError as e:
            pytest.skip(
                f"filesystem cannot hold a {len(long_basename)}-byte " f"basename: {e}"
            )

        # Real long-basename file, outside doctreedir so the escape
        # branch fires, with valid PNG bytes copied from the existing
        # render-gate fixture (never a synthetic/empty file).
        source_dir = tmp_path / "outside"
        source_dir.mkdir(parents=True, exist_ok=True)
        source_path = source_dir / long_basename
        shutil.copy2(_FIXTURE_PNG, source_path)

        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.init()

        doc = _build_single_image_document(str(source_path))

        with caplog.at_level("WARNING"):
            builder.post_process_images(doc)
            builder.copy_image_files()

        img = doc[0]

        warning_messages = [
            r.getMessage() for r in caplog.records if r.levelname == "WARNING"
        ]
        # Substring, not a strict prefix check: sphinx's own logging setup
        # (installed on temp_sphinx_app's real Sphinx application) prepends
        # a "WARNING: " translator prefix onto WARNING-level messages
        # before caplog observes them, so the literal text always begins
        # with that prefix rather than with "Failed to copy image" itself.
>       assert not any(
            "Failed to copy image" in m for m in warning_messages
        ), f"unexpected copy failure warning(s): {warning_messages!r}"
E       AssertionError: unexpected copy failure warning(s): ["WARNING: could not rehome image URI '/tmp/pytest-of-yuta/pytest-1635/test_copy_image_files_length_b0/outside/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.png' relative to the doctree directory -- relocated to '_typst_converted/b2e8281c-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.png'", "WARNING: Failed to copy image _typst_converted/b2e8281c-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.png: [Errno 36] File name too long: '/tmp/pytest-of-yuta/pytest-1635/test_copy_image_files_length_b0/build/html/_typst_converted/b2e8281c-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.png'"]
E       assert not True
E        +  where True = any(<generator object TestCopyImageFilesNameTooLong.test_copy_image_files_length_bound_no_name_too_long_warning.<locals>.<genexpr> at 0x74944085e810>)

tests/test_copy_image_files_name_too_long.py:104: AssertionError
------------------------------ Captured log call -------------------------------
WARNING  sphinx.typsphinx.builder:logging.py:138 WARNING: could not rehome image URI '/tmp/pytest-of-yuta/pytest-1635/test_copy_image_files_length_b0/outside/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.png' relative to the doctree directory -- relocated to '_typst_converted/b2e8281c-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.png'
INFO     sphinx.typsphinx.builder:logging.py:138 Copying 1 image file(s)...
WARNING  sphinx.typsphinx.builder:logging.py:138 WARNING: Failed to copy image _typst_converted/b2e8281c-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.png: [Errno 36] File name too long: '/tmp/pytest-of-yuta/pytest-1635/test_copy_image_files_length_b0/build/html/_typst_converted/b2e8281c-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.png'
=========================== short test summary info ============================
FAILED tests/test_track_image_key_construction.py::TestRelocationKeyNoBackslash::test_relocation_key_no_backslash_for_windows_shaped_uri
FAILED tests/test_track_image_key_construction.py::TestRelocationKeyLengthBound::test_relocation_key_length_bound_through_track_image
FAILED tests/test_copy_image_files_name_too_long.py::TestCopyImageFilesNameTooLong::test_copy_image_files_length_bound_no_name_too_long_warning
============================== 3 failed in 0.16s ===============================
```

`3 failed`, zero skipped. IMG-04's failure names the offending key verbatim:
`_typst_converted/ffe13a61-C:\Users\runner\assets\sub\we\"ird.png` (one literal backslash
surviving from the raw, un-normalized `path.basename(resolved_uri)` call). IMG-06's failure
shows `263` bytes measured for the 250-ASCII-character basename (9-byte `{digest}-` prefix plus
the 254-byte basename), matching D-06's predicted pre-fix number exactly. The integration gate's
own transcript carries Typst's platform-native refusal verbatim:
`Failed to copy image _typst_converted/b2e8281c-{254 x's}.png: [Errno 36] File name too long:
'{outdir}/_typst_converted/b2e8281c-{254 x's}.png'` -- the pre-fix `copy_image_files()` swallow
this fix closes.

### GREEN (post-fix)

Recorded after `_bound_relocation_component()`/`_build_relocation_key()` were added and
`_track_image()`'s escape branch was wired to call `_build_relocation_key(resolved_uri)`. Same
command as the RED run above, plus the task 3 pure-string property gates (11 tests total now
collected, up from 3):

```
uv run pytest tests/test_track_image_key_construction.py tests/test_copy_image_files_name_too_long.py -q
```

Whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-add2e5170089418aa
configfile: pyproject.toml
plugins: cov-7.1.0
collected 11 items

tests/test_track_image_key_construction.py ..........                    [ 90%]
tests/test_copy_image_files_name_too_long.py .                           [100%]

============================== 11 passed in 0.15s ==============================
```

`11 passed`, zero failed, zero skipped. Full suite also re-confirmed green: `uv run pytest -q` ->
`1462 passed, 5 skipped` (up from 1454 passed pre-task-3, the +8 new pure-string property tests
this task added). `uv run black --check .` and `uv run mypy typsphinx/` both clean.

**Before/after pair, measured directly against the post-fix helpers:**

- IMG-04's Windows-shaped URI (`r'C:\Users\runner\assets\sub\we\"ird.png'`) now produces key
  `_typst_converted/95a448fa-we"ird.png` -- no backslash (`'\\' in key` is `False`), versus the
  pre-fix `_typst_converted/ffe13a61-C:\Users\runner\assets\sub\we\"ird.png` recorded above.
- IMG-06's 250-ASCII-character basename now produces a final path component of exactly `255`
  UTF-8 bytes (`30232faf-{242 x's}.png`), versus the pre-fix `263` bytes recorded above -- the
  9-byte `{digest}-` prefix is accounted for and the stem is truncated by 8 bytes (250 -> 242) to
  land exactly at the limit.

## IMG-05

### RED (pre-fix)

Recorded at `b1c84fef9a89b69e11661a1a4bd2188e7b9d2587` (this plan's own base commit -- plan
59-02 already merged, `typsphinx/translator.py` still carries the pre-fix `visit_image()`
interpolating `adjusted_uri` directly, unescaped). Command:

```
uv run pytest tests/test_image_literal_escaping_gate.py -q
```

`git diff --stat -- typsphinx/translator.py` at this point: empty (confirmed above the run; the
product file is untouched by this task).

Whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7641101195cd2619
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests/test_image_literal_escaping_gate.py F                              [100%]

=================================== FAILURES ===================================
_ TestImageLiteralEscaping.test_image_literal_escaping_quote_is_escaped_in_emitted_typ _

self = <test_image_literal_escaping_gate.TestImageLiteralEscaping object at 0x7fc6a3251f90>
tmp_path = PosixPath('/tmp/pytest-of-yuta/pytest-1646/test_image_literal_escaping_qu0')

    def test_image_literal_escaping_quote_is_escaped_in_emitted_typ(self, tmp_path):
        """A relative image URI whose basename contains a literal double
        quote must emit an ESCAPED quote inside the ``image("...")``
        literal, never a raw one.

        Two properties of the chosen URI are load-bearing:

        1. It is RELATIVE (``images/we"ird.png``), so
           ``_is_absolute_image_uri()`` is False and the node never
           reaches the escape branch inside
           ``typsphinx/builder.py::_track_image()`` that plan 59-02
           already rewrote -- this test therefore measures
           ``visit_image()`` alone, independent of every other plan in
           this phase.
        2. No file named ``we"ird.png`` is ever created on disk, so this
           gate runs on every CI lane including ``windows-latest``, where
           a double quote is an illegal filename character.
           ``copy_image_files()`` logs ``Image file not found`` and the
           build continues -- that warning is expected and is never
           asserted against below.
        """
        srcdir = tmp_path / "source"
        _make_source_tree(srcdir)
        outdir = tmp_path / "build"

        result = _run_sphinx_build_typst(srcdir, outdir)

        assert result.returncode == 0, (
            f"Sphinx build failed:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        content_typ = outdir / "index.typ"
        assert content_typ.exists(), "index.typ (the content document) was not generated"
        emitted_text = content_typ.read_text()

        raw_uri = 'images/we"ird.png'
        escaped_fragment = f'image("{escape_typst_string(raw_uri)}"'
        raw_fragment = f'image("{raw_uri}"'

>       assert escaped_fragment in emitted_text, (
            f"Expected the escaped literal {escaped_fragment!r} in the "
            f"emitted .typ, got:\n{emitted_text}"
        )
E       AssertionError: Expected the escaped literal 'image("images/we\\"ird.png"' in the emitted .typ, got:
E         // Essential imports for included document
E         #import "@preview/codly:1.3.0": *
E         #import "@preview/codly-languages:0.1.10": *
E         #import "@preview/mitex:0.2.7": mi, mitex
E         #import "@preview/gentle-clues:1.3.1": *
E         
E         // Initialize codly
E         #show: codly-init.with()
E         #codly(languages: codly-languages)
E         
E         #{
E         [#metadata(none) <index:__tsx-doc__>]
E         [#heading(depth: 1, {text("Test Document")}) <index:test-document>]
E         
E         image("images/we"ird.png")
E         
E         
E         }
E         
E       assert 'image("images/we\\"ird.png"' in '// Essential imports for included document\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1....sx-doc__>]\n[#heading(depth: 1, {text("Test Document")}) <index:test-document>]\n\nimage("images/we"ird.png")\n\n\n}\n'

tests/test_image_literal_escaping_gate.py:161: AssertionError
=========================== short test summary info ============================
FAILED tests/test_image_literal_escaping_gate.py::TestImageLiteralEscaping::test_image_literal_escaping_quote_is_escaped_in_emitted_typ
============================== 1 failed in 0.31s ===============================
```

`1 failed`, zero skipped. The pre-fix `visit_image()` emits the literal `image("images/we"ird.png")`
verbatim -- the raw, unescaped double quote sits inside the Typst string literal exactly where
IMG-05 says it must not. `typsphinx/translator.py` is untouched at this point.

### GREEN (post-fix)

Recorded after `visit_image()` was changed to bind `escaped_uri = escape_typst_string(adjusted_uri)`
immediately after the `_compute_relative_image_path()` call, and to interpolate `escaped_uri`
(instead of `adjusted_uri`) at both the in-figure and standalone `add_text` sites. Same command as
the RED run above:

```
uv run pytest tests/test_image_literal_escaping_gate.py -q
```

Whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7641101195cd2619
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests/test_image_literal_escaping_gate.py .                              [100%]

============================== 1 passed in 0.24s ===============================
```

`1 passed`, zero failed, zero skipped. Full suite also re-confirmed green:
`uv run pytest -q` -> `1463 passed, 5 skipped` -- identical skip count to plan 59-02's post-fix
baseline, and only +1 over that baseline's `1462 passed` (this plan's own new gate test), meaning
zero pre-existing test assertions changed anywhere in the suite. `uv run black --check .` and
`uv run mypy typsphinx/` both clean.

**Before/after pair, measured directly against a real build (same fixture shape as the gate, run
standalone to capture the full emitted content document):**

Pre-fix (from the RED transcript above), the emitted content document `index.typ` contained:

```
image("images/we"ird.png")
```

Post-fix, the identical build now emits:

```
image("images/we\"ird.png")
```

with a `WARNING: Image file not found: .../images/we"ird.png` build warning still present in both
runs (expected -- no file with that name is ever created; the warning is about the copy step, not
the escaping this gate measures). The literal double quote inside the string is now preceded by a
backslash, matching `escape_typst_string()`'s documented quote-escaping rule, and the emitted text
contains no raw `we"ird.png` fragment anywhere.

## IMG-07 four-combination table

D-01's measured four-combination table (`59-CONTEXT.md`), reproduced here as the concrete design
target the compile gate built by this plan (`tests/test_windows_image_uri_render_gate.py`) proves
against. Raw basename: `sub\we"ird.png` -- normalized basename: `we"ird.png`.

| tree        | emitted `image(...)` literal               | Typst refusal                       |
|-------------|---------------------------------------------|---------------------------------------|
| unfixed     | `..._typst_converted/{d}-sub\we"ird.png`     | `path must not contain a backslash`   |
| IMG-04 only | `..._typst_converted/{d}-we"ird.png`         | `unclosed delimiter`                  |
| IMG-05 only | `..._typst_converted/{d}-sub\\we\"ird.png`   | `path must not contain a backslash`   |
| both        | `..._typst_converted/{d}-we\"ird.png`        | **compiles**                          |

A backslash-only fixture would already be green with IMG-04 (key normalization) alone and could
not prove SC#2's "neither alone would have closed it" -- the literal double quote in the basename
is what keeps IMG-05 (escaping) load-bearing too.

### RED (pre-fix, all four tree combinations) -- MEASURED (plan 59-05)

IMG-07 has no same-tree pre-fix RED by construction (D-05: the gate is coupled to BOTH the IMG-04
and IMG-05 fixes, and both are already merged onto this worktree by the time this plan's wave runs).
Plan 59-05 reconstructs all four tree combinations via
`git checkout $PHASE_BASE_SHA -- typsphinx/{builder,translator}.py`
(`PHASE_BASE_SHA=ec6bd3a4714a578379ee45e02295abc31fdd8fe3`, the value recorded at the top of this
file), running `git checkout HEAD -- typsphinx/builder.py typsphinx/translator.py` and confirming
`git status --porcelain typsphinx/` empty after EVERY combination before moving to the next.

For each combination, two measurements were taken: (1) `uv run pytest
tests/test_windows_image_uri_render_gate.py -q`, whole output; (2) a direct standalone
`python -m sphinx -b typstpdf tests/fixtures/windows_shaped_image_uri_gate <fresh temp dir>` with
`TYPSPHINX_WIN_URI_MODE=file`, capturing Typst's own error text and the emitted `image(...)` literal
independent of pytest's own output capture.

**MEASURED outcome table** (compare against the design-target table above, reproduced from
`59-CONTEXT.md` D-01):

| tree | emitted `image(...)` literal (measured) | Typst outcome (measured) | matches design target? |
|------|-------------------------------------------|---------------------------|--------------------------|
| (A) unfixed | `..._typst_converted/{d}-sub\we"ird.png` | `TypstError: unclosed delimiter` | **NO -- DIVERGENT** (target predicted `path must not contain a backslash`) |
| (B) key normalization only | `..._typst_converted/{d}-we"ird.png` | `TypstError: unclosed delimiter` | yes |
| (C) escaping only | `..._typst_converted/{d}-sub\\we\"ird.png` | `TypstError: path must not contain a backslash` | yes |
| (D) both | `..._typst_converted/{d}-we\"ird.png` | **compiles** (`master.pdf`, 29419 bytes, `%PDF` magic) | yes |

**SC#2 conclusion, unaffected by the divergence:** all three of A, B, C fail to compile and only D
compiles, so neither half alone closes the compile failure -- the conjunction is still genuinely
necessary on this fixture, regardless of which exact `TypstError` text fires on the unfixed tree.

**DIVERGENCE -- HALT condition (plan `59-05-PLAN.md` Task 1 instruction):** row (A)'s measured Typst
refusal is `unclosed delimiter`, not the `path must not contain a backslash` that `59-CONTEXT.md`
D-01 predicted for the unfixed tree. The plan's own instruction is explicit: "If any combination's
measured outcome differs from the expectation above, do NOT edit the expectation to match -- record
the measurement, mark the row DIVERGENT, and HALT for the owner." This section records the
measurement as directed and does not alter the prediction above it. A plausible explanation (not
asserted as fact, since the plan forbids resolving this without the owner): D-01's `59-CONTEXT.md`
table was inferred from four ISOLATED single-defect hand-compiled runs (`image("dir\logo.png")`,
`image("dir\\logo.png")`, `image("we"ird.png")`, `image("we\"ird.png")`) -- never from a single
literal carrying BOTH the raw backslash and the raw unescaped double quote simultaneously, which is
what the real "unfixed" tree's `_track_image()` + `visit_image()` pipeline actually emits. When both
defects are present in one string, the unescaped `"` terminates the Typst string literal early
(parse-level failure), so `ird.png")` becomes trailing unparsed tokens -- a parse-time
`unclosed delimiter` -- before Typst's semantic-level backslash-in-path check would ever run. This
is a hypothesis about the *design document's* prediction, not a claim about the product code, and
not resolved by this plan per its own instruction.

#### (A) unfixed -- verbatim transcripts

`uv run pytest tests/test_windows_image_uri_render_gate.py -q` (2 failed):

```
tests/test_windows_image_uri_render_gate.py FF                           [100%]

=================================== FAILURES ===================================
_ TestWindowsShapedImageUriStringShape.test_string_shape_emitted_image_literal_is_escaped_and_separator_free _
...
E       AssertionError: No image("...") literal found in the emitted .typ:
...
E         image("_typst_converted/95a448fa-C:\Users\runner\assets\sub\we"ird.png")
...
_ TestWindowsShapedImageUriCompileGate.test_compile_windows_shaped_absolute_image_uri_produces_pdf _
...
E       AssertionError: sphinx-build -b typstpdf failed:
...
E         stderr: WARNING: could not rehome image URI '.../sub\\we"ird.png' relative to the doctree directory -- relocated to '_typst_converted/467636ee-sub\\we"ird.png'
E         Typst compilation failed at .../build/master.typ: TypstError: unclosed delimiter
E         ERROR: Failed to compile .../build/master.typ: Typst compilation failed: TypstError: unclosed delimiter
E         Location: .../build/master.typ
E         Details: unclosed delimiter
...
=========================== short test summary info ============================
FAILED tests/test_windows_image_uri_render_gate.py::TestWindowsShapedImageUriStringShape::test_string_shape_emitted_image_literal_is_escaped_and_separator_free
FAILED tests/test_windows_image_uri_render_gate.py::TestWindowsShapedImageUriCompileGate::test_compile_windows_shaped_absolute_image_uri_produces_pdf
============================== 2 failed in 0.62s ===============================
```

Direct standalone build (`TYPSPHINX_WIN_URI_MODE=file python -m sphinx -b typstpdf
tests/fixtures/windows_shaped_image_uri_gate <tmp>`), exit code 2, stderr verbatim (trimmed to the
load-bearing lines; the full traceback is the same Sphinx `ExtensionError` shape as every other
combination below):

```
WARNING: could not rehome image URI '.../sub\\we"ird.png' relative to the doctree directory -- relocated to '_typst_converted/a6bf4142-sub\\we"ird.png'
Typst compilation failed at .../master.typ: TypstError: unclosed delimiter
ERROR: Failed to compile .../master.typ: Typst compilation failed: TypstError: unclosed delimiter
Location: .../master.typ
Details: unclosed delimiter
```

Emitted `image(...)` literal, read from `index.typ` of the direct build:

```
image("_typst_converted/a6bf4142-sub\we"ird.png")
```

`git status --porcelain typsphinx/` after restore: empty (confirmed before moving to combination B).

#### (B) key normalization only -- verbatim transcripts

`uv run pytest tests/test_windows_image_uri_render_gate.py -q` (2 failed) -- key difference from (A):
the literal now carries no separator backslash (only the raw quote survives), and the error text is
IDENTICAL to (A)'s (`unclosed delimiter`), because the parse-level failure fires regardless of
whether a backslash is also present:

```
E         image("_typst_converted/95a448fa-we"ird.png")
...
E         stderr: WARNING: could not rehome image URI '.../sub\\we"ird.png' relative to the doctree directory -- relocated to '_typst_converted/d110e5f2-we"ird.png'
E         Typst compilation failed at .../master.typ: TypstError: unclosed delimiter
E         ERROR: Failed to compile .../master.typ: Typst compilation failed: TypstError: unclosed delimiter
E         Location: .../master.typ
E         Details: unclosed delimiter
...
============================== 2 failed in 0.63s ===============================
```

Direct standalone build, exit code 2, stderr verbatim (trimmed):

```
Typst compilation failed at .../master.typ: TypstError: unclosed delimiter
ERROR: Failed to compile .../master.typ: Typst compilation failed: TypstError: unclosed delimiter
Details: unclosed delimiter
```

Emitted `image(...)` literal, read from `index.typ` of the direct build:

```
image("_typst_converted/8bcb3de9-we"ird.png")
```

`git status --porcelain typsphinx/` after restore: empty (confirmed before moving to combination C).
This combination MATCHES the design-target table's prediction.

#### (C) escaping only -- verbatim transcripts

`uv run pytest tests/test_windows_image_uri_render_gate.py -q` (2 failed) -- the string-shape gate's
own assertion fires first this time (a stray, non-quote-following backslash is found, because the
separator backslashes are still present and merely doubled by escaping):

```
E       AssertionError: Found a backslash NOT immediately followed by a double quote (a raw separator backslash, or a doubled escape from escaping without key normalization) in literal '_typst_converted/95a448fa-C:\\\\Users\\\\runner\\\\assets\\\\sub\\\\we\\"ird.png'
...
E         stderr: WARNING: could not rehome image URI '.../sub\\we"ird.png' relative to the doctree directory -- relocated to '_typst_converted/d43b9008-sub\\we"ird.png'
E         Typst compilation failed at .../master.typ: TypstError: path must not contain a backslash
E         ERROR: Failed to compile .../master.typ: Typst compilation failed: TypstError: path must not contain a backslash
E         Location: .../master.typ
E         Details: path must not contain a backslash
...
============================== 2 failed in 0.54s ===============================
```

Direct standalone build, exit code 2, stderr verbatim (trimmed):

```
Typst compilation failed at .../master.typ: TypstError: path must not contain a backslash
ERROR: Failed to compile .../master.typ: Typst compilation failed: TypstError: path must not contain a backslash
Details: path must not contain a backslash
```

Emitted `image(...)` literal, read from `index.typ` of the direct build:

```
image("_typst_converted/b90ae4ad-sub\\we\"ird.png")
```

`git status --porcelain typsphinx/` after restore: empty (confirmed before moving to combination D).
This combination MATCHES the design-target table's prediction.

#### (D) both -- verbatim transcripts

`uv run pytest tests/test_windows_image_uri_render_gate.py -q`:

```
tests/test_windows_image_uri_render_gate.py ..                           [100%]

============================== 2 passed in 0.54s ===============================
```

Direct standalone build, exit code 0. Emitted `image(...)` literal:

```
image("_typst_converted/33ea9149-we\"ird.png")
```

`master.pdf`: 29419 bytes, first four bytes `%PDF` -- a real, valid PDF. This combination MATCHES the
design-target table's prediction (confirming plan 59-04's own recorded GREEN transcript above).

`git status --porcelain typsphinx/` after restore: empty. `git status --porcelain typsphinx/` was
also re-confirmed empty immediately before this task's own commit below.

### HALT -- owner decision required

Per this task's own instruction, execution HALTS here rather than proceeding to Task 2 (SC#5
measurement) and Task 3 (CI dispatch) in this same plan run. The core SC#2 claim
("neither alone would have closed it") is proven true by the measurements above regardless of the
divergence -- three of four trees fail to compile and only the tree carrying both fixes compiles.
What is NOT resolved is whether `59-CONTEXT.md` D-01's table should be corrected in place (its
"unfixed" row's predicted error text was inferred from isolated single-defect probes, not measured
against the actual combined-defect literal this fixture emits) or whether some other explanation
applies. This plan's own acceptance criteria for Task 1 literally require the string
`path must not contain a backslash` to appear for combination A, which the real measurement does not
support -- committing that criterion as satisfied would misrepresent what was measured. The owner
should review this section and instruct either: (a) amend `59-CONTEXT.md` D-01 in place with this
measurement (the project's own established pattern for a locked decision falsified by measurement,
see STATE.md "[Phase 56] D-03 was AMENDED..." and the MEMORY.md entry "locked decisions can be
falsified by research"), after which this plan's Task 1 acceptance criteria should be read against
the corrected table; or (b) some other resolution. Tasks 2 and 3 of this plan are unexecuted pending
that decision.

**Resolved 2026-08-29:** the owner approved option (a) above. `59-CONTEXT.md` now carries
`D-01a: AMENDED` (commit `ab7a42ae`), independently re-measured by the orchestrator before approval.
This plan's Tasks 2 and 3 resumed under `## SC#5 acceptance` below.

### GREEN (post-fix, both halves present)

Recorded in this worktree with both IMG-04 (`typsphinx/builder.py`, plan 59-02) and IMG-05
(`typsphinx/translator.py`, plan 59-03) already merged. Command:

```
uv run pytest tests/test_windows_image_uri_render_gate.py -k compile -v
```

Whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7c21024584698d3/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7c21024584698d3
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 2 items / 1 deselected / 1 selected

tests/test_windows_image_uri_render_gate.py::TestWindowsShapedImageUriCompileGate::test_compile_windows_shaped_absolute_image_uri_produces_pdf PASSED [100%]

======================= 1 passed, 1 deselected in 0.33s ========================
```

`1 passed`, **`0 skipped`** -- the probe-and-skip in `TestWindowsShapedImageUriCompileGate` did NOT
fire on this worktree's filesystem (ext4), and the `TYPST_AVAILABLE` guard was satisfied (the
worktree venv's `typst-py 0.15.0` imported cleanly). A `skipped` line here would mean the worktree
venv lacks `typst` or the filesystem rejected the probe, and either reads as a pass in a summary
line while proving nothing (`59-CONTEXT.md` Specific Idea #4) -- neither happened.

Both gates in the module also pass together, `2 passed, 0 skipped`:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab7c21024584698d3
configfile: pyproject.toml
plugins: cov-7.1.0
collected 2 items

tests/test_windows_image_uri_render_gate.py ..                           [100%]

============================== 2 passed in 0.55s ===============================
```

**Measured emitted literal** (standalone `-b typstpdf` build of the fixture in `"file"` mode,
`TYPSPHINX_WIN_URI_MODE=file`, run separately from pytest to capture the full content document):

```
image("_typst_converted/d0092ecb-we\"ird.png")
```

No raw backslash survives (the `we"ird.png` basename carries no directory separator at all after
normalization), and the literal double quote is escaped (`\"`) -- both of D-04's properties, and
this is the exact "both" row of the table above.

**Resolved name of the copied destination file**, asserted present BEFORE the compile result
(`59-CONTEXT.md` Specific Idea #3 -- a green compile is not evidence unless the source file
existed):

```
$ ls _typst_converted/
d0092ecb-we"ird.png
```

**`master.pdf`**: 29419 bytes, first four bytes `b'%PDF'` -- a real, non-empty, valid PDF produced
by a real `typst.compile()` call through `TypstPDFBuilder.finish()`.

**Deviation recorded during this plan**: the fixture's `_rehome_to_real_file()` originally called
`self.env.doctreedir.rstrip(os.sep)` directly, which Sphinx 9.1 flags with
`RemovedInSphinx10Warning` (a `DeprecationWarning` subclass) -- "Sphinx 10 will drop support for
representing paths as strings. Use `pathlib.Path` or `os.fspath` instead." Fixed by wrapping with
`os.fspath(self.env.doctreedir)` before calling `.rstrip()`. Confirmed by a standalone `-b typstpdf`
build before and after: the warning line was present pre-fix and absent post-fix, with the build's
warning count dropping from 2 to 1 (only the expected rehome warning remains). This did not affect
any assertion (the warning fires inside a subprocess pytest's `filterwarnings` cannot see), but is
fixed as a correctness matter per CLAUDE.md's project conventions.

## SC#5 acceptance

**Owner disposition on the D-01 divergence recorded above:** the halt this section's placeholder was
waiting on is CLOSED. The owner reviewed the measured divergence recorded in `### HALT — owner
decision required` above and approved amending `59-CONTEXT.md` D-01 in place — recorded as
`D-01a: AMENDED` (committed `ab7a42ae`), which the orchestrator independently re-measured against
`typst.compile()` directly on the four literal shapes before approving, on 2026-08-29. SC#2's core
claim is unaffected by the amendment (A, B, C all fail to compile and only D compiles — see the
measured table and its conclusion above). Tasks 2 and 3 below resume per that approval.

### Zero test edits (measured)

`git diff --name-status $PHASE_BASE_SHA..HEAD -- tests/` (`PHASE_BASE_SHA=ec6bd3a4714a578379ee45e02295abc31fdd8fe3`),
whole output verbatim:

```
A	tests/fixtures/windows_shaped_image_uri_gate/_static/converted_stand_in.png
A	tests/fixtures/windows_shaped_image_uri_gate/conf.py
A	tests/fixtures/windows_shaped_image_uri_gate/index.rst
A	tests/test_copy_image_files_name_too_long.py
A	tests/test_image_literal_escaping_gate.py
A	tests/test_path_shape_predicate_gate.py
A	tests/test_track_image_key_construction.py
A	tests/test_windows_image_uri_render_gate.py
```

Every line begins with `A` (added). No `M` and no `D` line anywhere under `tests/` — zero
cross-check against `58-REPR-CENSUS.md` is needed because there is no modified or deleted path to
cross-check; all eight paths are new files this phase introduced.

`git diff --numstat $PHASE_BASE_SHA..HEAD -- tests/`, whole output verbatim (added-lines-only shape
confirmed numerically as well as by status; the binary PNG fixture reports `-\t-` per git's own
convention for binary files, not a deletion):

```
-	-	tests/fixtures/windows_shaped_image_uri_gate/_static/converted_stand_in.png
154	0	tests/fixtures/windows_shaped_image_uri_gate/conf.py
10	0	tests/fixtures/windows_shaped_image_uri_gate/index.rst
112	0	tests/test_copy_image_files_name_too_long.py
170	0	tests/test_image_literal_escaping_gate.py
170	0	tests/test_path_shape_predicate_gate.py
260	0	tests/test_track_image_key_construction.py
288	0	tests/test_windows_image_uri_render_gate.py
```

None of the eight new paths appear anywhere in `58-REPR-CENSUS.md`'s pass-criterion table or its
third bucket (`TestWindowsPathEscapingRegressionGuard` in
`tests/test_templates_path_collision_gate.py`, untouched by this phase) — the census's nine
enumerated sites are unaffected by this phase's diff.

### Final local gate (phase tip)

`uv run pytest -q`, verbatim tail:

```
tests/test_xref_compile_time_guard_render_gate.py ......                 [ 99%]
tests/test_xref_orphan_degrade_render_gate.py .                          [ 99%]
tests/test_xref_whole_document_guard_render_gate.py ........             [100%]

================= 1465 passed, 5 skipped in 120.51s (0:02:00) ==================
```

`uv run black --check .`, verbatim tail:

```
All done! ✨ 🍰 ✨
348 files would be left unchanged.
```

`uv run mypy typsphinx/`, verbatim tail:

```
Success: no issues found in 8 source files
```

`ruff check .` is **DEFERRED TO CI** — per `59-VALIDATION.md` § "Sampling Rate": "`ruff check .` is
deferred to CI — it is not runnable on this NixOS dev machine, and CI is the lint authority."

### Post-merge gate (orchestrator, milestone branch `gsd/v0.9.1-windows-path-correctness`)

The section above was measured inside plan 59-05's isolated worktree. The authoritative measurement
is the merged milestone branch, re-run by the orchestrator at tip `2deeae1a` (all five waves merged
plus the UP012 fix):

```
================= 1469 passed, 1 skipped in 125.62s (0:02:05) ==================
```

`uv run black --check .` → 348 files unchanged. `uv run mypy typsphinx/` → *Success: no issues found
in 8 source files*.

**On the 5-vs-1 skip difference:** the worktree run reports 5 skipped, the merged main tree 1. The
merged tree's single skip is identified verbatim as
`tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set
TYPSPHINX_CORPUS_REPORT=1 to run it`, a pre-existing env-gated corpus check unrelated to this phase.
The four additional skips seen in the worktree are an artifact of the freshly-provisioned worktree
venv, not of this phase's code; the per-module census below independently confirms `0 skipped` for
all five of this phase's own new gate modules in both environments, which is the property that
actually matters here.

**Correction to the `ruff` DEFERRED note above:** ruff is *not* universally unrunnable on this dev
machine. The orchestrator's main `.venv` carries a working ruff wheel (0.15.20, the same version CI
resolves) and ran `ruff check .` to *All checks passed!* after the UP012 fix. What is unrunnable is
ruff inside a **freshly `uv sync`-ed worktree venv**, whose wheel's generic-linux ELF cannot exec
under NixOS — which is precisely the environment every plan in this phase executed in, so the
DEFERRED note was correct as written from there. CI remains the declared lint authority, and Run 1
below is the demonstration of why: no worktree executor in this phase could have caught UP012.

### Per-module skip census (five new gate modules)

Each of the five new gate modules run standalone with `-q`, on this dev machine, immediately after
the full-suite run above:

| Module | Command | Result |
|---|---|---|
| `tests/test_path_shape_predicate_gate.py` | `uv run pytest tests/test_path_shape_predicate_gate.py -q` | `14 passed in 0.19s` — **0 skipped** |
| `tests/test_track_image_key_construction.py` | `uv run pytest tests/test_track_image_key_construction.py -q` | `10 passed in 0.12s` — **0 skipped** |
| `tests/test_copy_image_files_name_too_long.py` | `uv run pytest tests/test_copy_image_files_name_too_long.py -q` | `1 passed in 0.18s` — **0 skipped** |
| `tests/test_image_literal_escaping_gate.py` | `uv run pytest tests/test_image_literal_escaping_gate.py -q` | `1 passed in 0.23s` — **0 skipped** |
| `tests/test_windows_image_uri_render_gate.py` | `uv run pytest tests/test_windows_image_uri_render_gate.py -q` | `2 passed in 0.53s` — **0 skipped** |

All five report `0 skipped`. `typst` is a core dependency (`pyproject.toml:29`), so this confirms
the worktree venv is correctly provisioned rather than merely reporting a pass that hides an
unprovisioned environment (T-59-06).

The full suite's `5 skipped` are pre-existing skips outside these five modules (unrelated to this
phase — the same baseline count Phase 58's own evidence recorded); none of the five new gate modules
contributes to that count.

### RED-first ledger

| Requirement | Evidence section holding its recorded failure | Mechanism |
|---|---|---|
| PATH-01 | `59-WINDOWS-URI-EVIDENCE.md` § "PATH-01" § "RED (pre-fix, direct call)" | Recorded RED on the unfixed tree (`PHASE_BASE_SHA`) before `_escapes_outdir()`'s fix landed, in the same plan (59-01). |
| IMG-04 | `59-WINDOWS-URI-EVIDENCE.md` § "IMG-04 / IMG-06" § "RED (pre-fix)" | Recorded RED on the unfixed tree before `_track_image()`'s escape-branch key-normalization fix landed, in the same plan (59-02). |
| IMG-06 | `59-WINDOWS-URI-EVIDENCE.md` § "IMG-04 / IMG-06" § "RED (pre-fix)" | Recorded RED on the unfixed tree (the `263`-byte pre-fix measurement and the swallowed `[Errno 36]` warning) before the 255-byte bound landed, in the same plan (59-02). |
| IMG-05 | `59-WINDOWS-URI-EVIDENCE.md` § "IMG-05" § "RED (pre-fix)" | Recorded RED on the unfixed tree before `visit_image()`'s `escape_typst_string()` routing landed, in the same plan (59-03). |
| IMG-07 | `59-WINDOWS-URI-EVIDENCE.md` § "IMG-07 four-combination table" § "RED (pre-fix, all four tree combinations) -- MEASURED (plan 59-05)" | IMG-07's RED is the four-combination two-tree reconstruction in this plan's Task 1, because ROADMAP constraint 5 forces its gate into the wave after both fixes and a same-tree pre-fix RED is therefore impossible for it — the RED-then-green record here substitutes the reconstructed unfixed/partial/both trees for a same-tree pre-fix run. |

### 3-OS CI dispatch

**MEASURED — dispatched fresh on this phase's own post-fix tip by the orchestrator on the milestone
branch `gsd/v0.9.1-windows-path-correctness` after all five waves were merged.** Two runs were
dispatched: the first found a real, CI-only defect; the second is the acceptance run.

#### Run 1 — `36874e0e` — FAILURE (lint only), and what it caught

- Run URL: https://github.com/YuSabo90002/typsphinx/actions/runs/33211569732
- Dispatched head SHA: `36874e0ee77560cf11b4807e892c095ee2d06e28`
- Local tip SHA at dispatch: `36874e0ee77560cf11b4807e892c095ee2d06e28` (equal)

| job | conclusion |
|---|---|
| Test Python 3.12 on ubuntu-latest | success |
| Test Python 3.13 on ubuntu-latest | success |
| **Test Python 3.12 on windows-latest** | **success** |
| **Test Python 3.13 on windows-latest** | **success** |
| Test Python 3.12 on macos-latest | success |
| Test Python 3.13 on macos-latest | success |
| Lint and Format Check | **failure** |
| Type Check | success |
| Code Coverage | success |
| Build Package | success |
| Integration Test - basic | success |
| Integration Test - advanced | success |

Every matrix test job passed, including both `windows-latest` jobs. The single failure was
`ruff check .` inside `tox -e lint`:

```
UP012 [*] Unnecessary UTF-8 `encoding` argument to `encode`
   --> tests/test_track_image_key_construction.py:214:34
    |
214 |         prefix_byte_length = len(f"{digest}-".encode("utf-8"))
    |                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Found 1 error.
```

`black --check .` passed (348 files unchanged) and `Type Check` passed in the same run; only ruff
failed. This is exactly the defect class `59-VALIDATION.md` predicted when it recorded `ruff check .`
as DEFERRED TO CI: ruff is not runnable under the worktree-provisioned venv on this NixOS dev
machine, so CI is this project's lint authority and is the only place this could surface. Note that
UP012 fired on line 214 alone and not on the module's ten other `.encode("utf-8")` calls, because
only line 214 applies it to a **string literal** (an f-string); the rest apply it to variables,
which UP012 does not flag.

**Fix:** `2deeae1a` — `fix(59): drop redundant utf-8 arg tripping ruff UP012 in the IMG-06 gate`,
changing that one expression to `f"{digest}-".encode()`. `.encode()` already defaults to UTF-8, so
the semantics are unchanged, and the line now matches its own docstring one line above
(`255 - len(f"{digest}-".encode())`). Re-measured locally after the fix: `ruff check .` → *All
checks passed!*, `black --check .` → 348 files unchanged, `mypy typsphinx/` → *Success: no issues
found in 8 source files*, `pytest tests/test_track_image_key_construction.py -q` → 10 passed.

**SC#5 is unaffected by this fix.** The edited file is one this phase *added*, so the zero-test-edit
measurement is unchanged — re-run after the fix commit,
`git diff --name-status $PHASE_BASE_SHA..HEAD -- tests/` still yields zero non-`A` lines.

#### Run 2 — `2deeae1a` — SUCCESS (superseded by Run 3)

- Run URL: https://github.com/YuSabo90002/typsphinx/actions/runs/33212148974
- Dispatched head SHA: `2deeae1a55680fbf8523dcc9e566ad1f7e8abe6f`
- Local tip SHA at dispatch: `2deeae1a55680fbf8523dcc9e566ad1f7e8abe6f` (equal)
- Run conclusion: **success**

| job | conclusion |
|---|---|
| Test Python 3.12 on ubuntu-latest | success |
| Test Python 3.13 on ubuntu-latest | success |
| **Test Python 3.12 on windows-latest** | **success** |
| **Test Python 3.13 on windows-latest** | **success** |
| Test Python 3.12 on macos-latest | success |
| Test Python 3.13 on macos-latest | success |
| Lint and Format Check | success |
| Type Check | success |
| Code Coverage | success |
| Build Package | success |
| Integration Test - basic | success |
| Integration Test - advanced | success |

Both `windows-latest` jobs — the acceptance bar this phase names — concluded successfully on a run
whose head SHA is this phase's own post-fix tip, newer than every one of the phase's commits. No
earlier run is cited anywhere in this section.

#### Run 3 — `924f21d8` — SUCCESS (the acceptance run)

Run 2 was green, but the phase's own code review (`59-REVIEW.md`, CR-01) then found a real defect in
`_bound_relocation_component()` that Run 2 could not have caught, because no test exercised it. The
owner approved fixing it inside this phase rather than deferring it, so the acceptance bar moved to a
third run dispatched on the post-fix tip.

- Run URL: https://github.com/YuSabo90002/typsphinx/actions/runs/33214830110
- Dispatched head SHA: `924f21d818f32c79d2bcb4e3d2287e8b969c6899`
- Local tip SHA at dispatch: `924f21d818f32c79d2bcb4e3d2287e8b969c6899` (equal)
- Run conclusion: **success** — all 12 jobs

| job | conclusion |
|---|---|
| Test Python 3.12 on ubuntu-latest | success |
| Test Python 3.13 on ubuntu-latest | success |
| **Test Python 3.12 on windows-latest** | **success** |
| **Test Python 3.13 on windows-latest** | **success** |
| Test Python 3.12 on macos-latest | success |
| Test Python 3.13 on macos-latest | success |
| Lint and Format Check | success |
| Type Check | success |
| Code Coverage | success |
| Build Package | success |
| Integration Test - basic | success |
| Integration Test - advanced | success |

**What CR-01 was.** `_bound_relocation_component()` documents D-07's precedence as digest whole, then
at least one byte of stem, then extension. Reserving one *byte* is only equivalent to reserving one
*character* for ASCII: when the stem's first character is multi-byte and `stem_budget` was smaller
than it, the UTF-8 boundary walk-back had no valid non-empty prefix and landed on `b""`, dropping the
whole stem while the lower-priority extension kept its allotment — inverting the documented
precedence. Reproduced independently by the orchestrator before acting:

```
_bound_relocation_component("a1b2c3d4", "図" + "." + "e"*244)
  pre-fix  -> 'a1b2c3d4-.eeee…'   254 bytes, stem EMPTY
  ASCII sibling "a" + "." + "e"*244
           -> 'a1b2c3d4-a.eee…'   255 bytes, stem 'a' survives
```

The ASCII sibling is what hid it: an ASCII stem fits the one reserved byte, so only a multi-byte
leading character exposes the defect, and no test combined that with a tight `stem_budget`.

**Fix** — `924f21d8`: the reserved unit became one *character*, with the shortfall borrowed back from
the extension whenever the total budget can hold it; the duplicated `stem_budget` formula (WR-01) was
hoisted to a single computation; and the boundary walk-back was extracted to `_decode_to_boundary()`.
Two regression gates were added to `tests/test_track_image_key_construction.py`, and both were proven
RED against the pre-fix tree before the fix was committed:

```
FAILED …::test_length_bound_multibyte_leading_stem_survives_tight_budget
FAILED …::test_length_bound_multibyte_stem_kept_when_extension_exceeds_budget
========================= 2 failed, 10 passed in 0.14s =========================
```

Post-fix: 12 passed in that module; full suite `1471 passed, 1 skipped`; `black --check .`,
`ruff check .` and `mypy typsphinx/` all clean.

**SC#5 remains intact.** `tests/test_track_image_key_construction.py` is a file this phase *added*,
so `git diff --name-status $PHASE_BASE_SHA..HEAD -- tests/` still yields zero non-`A` lines after
this commit — re-measured.

