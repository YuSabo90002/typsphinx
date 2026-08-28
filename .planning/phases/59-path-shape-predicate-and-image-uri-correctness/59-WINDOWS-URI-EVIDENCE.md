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

### RED (pre-fix, all four tree combinations)

Not recorded in this plan -- IMG-07 has no same-tree pre-fix RED by construction (D-05: the gate is
coupled to BOTH the IMG-04 and IMG-05 fixes, and both are already merged onto this worktree by the
time this plan's wave (wave 4) runs). **Plan 59-05** reconstructs all four tree combinations via
`git checkout $PHASE_BASE_SHA -- typsphinx/{builder,translator}.py` and re-runs this exact gate
against each reconstructed tree -- the direct proof of SC#2's "neither alone would have closed it".

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

(filled by plan 59-05)
