# Phase 60 Plan 02 — MSG-03 Evidence

## Plan base SHA

```
1118199a577533f598a799b51d08b7bc3e9bcc49
```

## Discovery grep

All four commands run against the live worktree at the plan base SHA (before any edit).

### `grep -n "\!r" typsphinx/builder.py`

```
523:        f"typst_document_templates: registry key {key!r}'s "
540:    back to ``!r`` (57-11-PLAN.md task 2).
546:            ``!r``, so a Windows backslash is not doubled by
557:        f"registry key {key!r}'s resolved template "
586:            quoted with explicit ``'...'``, never ``!r``).
592:        f"registry key {existing_key!r} and registry key "
593:        f"{key!r} both resolve to the same bundle "
884:                        f"{docname!r} after removing an unsupported path -- "
885:                        f"falling back to {docname!r}"
890:                    f"name: {target!r} -- using {fallback!r} instead"
905:                    f"{docname!r} -- falling back to {docname!r}"
918:                f"{docname!r} -- falling back to {docname!r}"
1135:                        f"the same output path {relpath!r}",
1151:            _claim(content_relpath, f"the content file for docname {docname!r}")
1156:                        f"the content file for docname {docname!r} would "
1157:                        f"be written to {content_relpath!r}, whose first "
1158:                        f"path segment is {TEMPLATE_OUTPUT_DIR!r} -- that "
1181:                    f"typst_documents entry {index} ({entry!r}) produces "
1191:                f"typst_documents entry {index} (docname {docname!r}, "
1192:                f"target {target!r})",
1199:                        f"{docname!r}, target {target!r}) would write its "
1200:                        f"wrapper to {wrapper_relpath!r}, whose first path "
1201:                        f"segment is {TEMPLATE_OUTPUT_DIR!r} -- that "
1208:                f"{relpath!r}: {message}" for relpath, message in failures
1470:                        f"registry key {declared_key!r} differs from "
1471:                        f"the built-in {RESERVED_REGISTRY_KEY!r} "
1479:                        f"{declared_key!r} to something that does not "
1565:            summary = "; ".join(f"{key!r}: {message}" for key, message in failures)
1943:                    f"could not rehome image URI {resolved_uri!r} relative "
1944:                    f"to the doctree directory -- relocated to {key!r}"
2224:                    logger.debug(f"Copied bundle file for {key!r}: {rel_path}")
2231:                            f"resolved template for registry key {key!r} "
2232:                            f"from {src_file!r} to {dest_file!r}: {e}"
2241:                f"registry key {key!r} ({template_filename!r}) was never "
2242:                f"copied from {src_dir!r} to {dest_dir!r} -- a wrapper "
2410:            summary = "; ".join(f"{key!r}: {message}" for key, message in failures)
2538:                logger.warning(f"Malformed typst_documents entry: {doc_tuple!r}")
2551:                    f"{docname!r} -- expected a str"
2566:                    f"typst_documents entry {doc_tuple!r} has no target "
2583:                        f"Master document {docname!r} is not a known Sphinx document"
```

### `grep -n "repr(" typsphinx/builder.py`

```
547:            ``repr()``).
1095:        ``repr()`` and stating it produces no wrapper file -- this is the
2539:                failures.append((repr(doc_tuple), "malformed typst_documents entry"))
2554:                failures.append((repr(docname), message))
```

### `grep -n "%r" typsphinx/builder.py`

```
(no output -- no %-style repr formatting anywhere in this module)
```

### `grep -noE "'\{[a-zA-Z_.]+\}'" typsphinx/builder.py`

```
524:'{resolved_path}'
526:'{srcdir}'
558:'{bundle_dir}'
560:'{raw_tp_entry}'
561:'{resolved_tp_entry}'
594:'{dest_dir}'
```

This fourth grep is the one that finds the three 57-11 message builders' hardcoded-delimiter
sites (`_conf17_violation_message`, `_templates_path_collision_message`,
`_bundle_destination_collision_message`) — they carry D-12's delimiter-selection defect without
using `!r` at all, so the first three greps miss them entirely; only this pattern catches them.

**Cross-check against D-06's line list:** the measured lines above match D-06's enumeration
(`:890`, `:1135`/`:1208`, `:1156-1158`, `:1199-1201`, `:1943-1944`, `:2231-2232`, `:2241-2242`,
`:524-526`, `:557-562`, `:594`) at the SAME line numbers as the CONTEXT — this worktree's tree is
at the same commit the CONTEXT was measured against (Phase 59 already merged, nothing shifted
since). The two AMENDED sites (`:1192`, `:1199`) are present in the `!r` grep as expected.

## RED — three 57-11 builders (single-quote half)

Command: `uv run pytest tests/test_templates_path_collision_gate.py -q -k disambiguates_embedded_single_quote`

Plan base SHA: `1118199a577533f598a799b51d08b7bc3e9bcc49`

These three tests target the SINGLE-QUOTE half of the D-01 delimiter rule (D-12) — the backslash
half of these three 57-11 message builders has been green since Phase 57, so a backslash-only
assertion here would be tautologically green. `SINGLE_QUOTE_SHAPED_PATH =
"/home/O'Brien's Projects/_templates/nested"` is wrapped in hardcoded apostrophes at all three
sites pre-fix, so the apostrophe inside the value closes the delimiter early — the
double-quote-delimited form the test asserts for is never produced.

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a976975ecfffc99dc
configfile: pyproject.toml
plugins: cov-7.1.0
collected 19 items / 16 deselected / 3 selected

tests/test_templates_path_collision_gate.py FFF                          [100%]

=================================== FAILURES ===================================
_ TestWindowsPathEscapingRegressionGuard.test_conf17_violation_message_disambiguates_embedded_single_quote _

self = <test_templates_path_collision_gate.TestWindowsPathEscapingRegressionGuard object at 0x7beb86093e30>

    def test_conf17_violation_message_disambiguates_embedded_single_quote(self):
        ...
        message = _conf17_violation_message(
            "mykey", self.SINGLE_QUOTE_SHAPED_PATH, "/srcdir"
        )
>       assert f'"{self.SINGLE_QUOTE_SHAPED_PATH}"' in message
E       assert '"/home/O\'Brien\'s Projects/_templates/nested"' in "typst_document_templates: registry key 'mykey''s resolved template '/home/O'Brien's Projects/_templates/nested' has a...hat is srcdir itself, or an ancestor of srcdir ('/srcdir') -- put the template in its own subdirectory (CONF-17, A-01)"

tests/test_templates_path_collision_gate.py:514: AssertionError
_ TestWindowsPathEscapingRegressionGuard.test_templates_path_collision_message_disambiguates_embedded_single_quote _

self = <test_templates_path_collision_gate.TestWindowsPathEscapingRegressionGuard object at 0x7beb86069370>

    def test_templates_path_collision_message_disambiguates_embedded_single_quote(
        self,
    ):
        ...
        message = _templates_path_collision_message(
            "mykey",
            self.SINGLE_QUOTE_SHAPED_PATH,
            "_templates",
            "/srcdir/_templates",
        )
>       assert f'"{self.SINGLE_QUOTE_SHAPED_PATH}"' in message
E       assert '"/home/O\'Brien\'s Projects/_templates/nested"' in "registry key 'mykey''s resolved template bundle directory '/home/O'Brien's Projects/_templates/nested' collides with ... is not on templates_path (this repository uses _typst/) and update typst_template / typst_document_templates to match"

tests/test_templates_path_collision_gate.py:529: AssertionError
_ TestWindowsPathEscapingRegressionGuard.test_bundle_destination_collision_message_disambiguates_embedded_single_quote _

self = <test_templates_path_collision_gate.TestWindowsPathEscapingRegressionGuard object at 0x7beb86069260>

    def test_bundle_destination_collision_message_disambiguates_embedded_single_quote(
        self,
    ):
        ...
        message = _bundle_destination_collision_message(
            "alpha", "beta", self.SINGLE_QUOTE_SHAPED_PATH
        )
>       assert f'"{self.SINGLE_QUOTE_SHAPED_PATH}"' in message
E       assert '"/home/O\'Brien\'s Projects/_templates/nested"' in "registry key 'alpha' and registry key 'beta' both resolve to the same bundle destination '/home/O'Brien's Projects/_templates/nested'"

tests/test_templates_path_collision_gate.py:541: AssertionError
=========================== short test summary info ============================
FAILED tests/test_templates_path_collision_gate.py::TestWindowsPathEscapingRegressionGuard::test_conf17_violation_message_disambiguates_embedded_single_quote
FAILED tests/test_templates_path_collision_gate.py::TestWindowsPathEscapingRegressionGuard::test_templates_path_collision_message_disambiguates_embedded_single_quote
FAILED tests/test_templates_path_collision_gate.py::TestWindowsPathEscapingRegressionGuard::test_bundle_destination_collision_message_disambiguates_embedded_single_quote
======================= 3 failed, 16 deselected in 0.04s =======================
```

Exactly 3 failures, all in the newly-added single-quote methods; the 16 pre-existing methods
(deselected by the `-k` filter, not run) are untouched by this transcript.

## RED — _resolve_target_stem

Command: `uv run pytest tests/test_builder_path_quoting_gate.py -q -k TestResolveTargetStemPathQuoting`

`builder._resolve_target_stem("index", "C:\\Users\\runner\\escape.typ")` — the raw target has
three single backslashes; pre-fix `{target!r}` interpolation doubles all three.

```
_ TestResolveTargetStemPathQuoting.test_path_refusal_warning_has_no_doubled_separator _

self = <test_builder_path_quoting_gate.TestResolveTargetStemPathQuoting object at 0x79895004df90>
temp_sphinx_app = <SphinxTestApp buildername='html'>
caplog = <_pytest.logging.LogCaptureFixture object at 0x79894e8917f0>

    def test_path_refusal_warning_has_no_doubled_separator(
        self, temp_sphinx_app, caplog
    ):
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        target = "C:\\Users\\runner\\escape.typ"

        with caplog.at_level("WARNING"):
            builder._resolve_target_stem("index", target)

        warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
        assert warning_records, "expected the path-refusal warning to fire"
        message = warning_records[0].getMessage()
        assert "a path is not supported in a typst_documents target" in message
>       _assert_no_doubled_separator(message)

tests/test_builder_path_quoting_gate.py:90:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

message = "WARNING: a path is not supported in a typst_documents target name: 'C:\\\\Users\\\\runner\\\\escape.typ' -- using 'escape' instead"

E       AssertionError: Expected every backslash run to be a single unescaped separator, found a doubled/escaped run in:
E         "WARNING: a path is not supported in a typst_documents target name: 'C:\\\\Users\\\\runner\\\\escape.typ' -- using 'escape' instead"
E       assert not ['\\\\', '\\\\', '\\\\']

tests/test_builder_path_quoting_gate.py:46: AssertionError
------------------------------ Captured log call -------------------------------
WARNING  sphinx.typsphinx.builder:logging.py:138 WARNING: a path is not supported in a typst_documents target name: 'C:\\Users\\runner\\escape.typ' -- using 'escape' instead
```

Three doubled runs recorded, matching the truths-table's "Pre-fix this message carries three
doubled runs" claim exactly.

## RED — _track_image rehome warning

Command: `uv run pytest tests/test_builder_path_quoting_gate.py -q -k TestTrackImageRehomeWarningPathQuoting`

`builder.post_process_images(doc)` driven with `uri = "C:\\Users\\runner\\assets\\sub\\image.png"`
(five single-backslash separators in the raw value: `C:`|`Users`|`runner`|`assets`|`sub`|`image.png`);
pre-fix `{resolved_uri!r}` doubles all five.

```
_ TestTrackImageRehomeWarningPathQuoting.test_rehome_warning_has_no_doubled_separator _

self = <test_builder_path_quoting_gate.TestTrackImageRehomeWarningPathQuoting object at 0x79895004e5d0>
temp_sphinx_app = <SphinxTestApp buildername='html'>
caplog = <_pytest.logging.LogCaptureFixture object at 0x79894e903110>

    def test_rehome_warning_has_no_doubled_separator(self, temp_sphinx_app, caplog):
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.init()
        uri = "C:\\Users\\runner\\assets\\sub\\image.png"
        doc = _build_single_image_document(uri)

        with caplog.at_level("WARNING"):
            builder.post_process_images(doc)

        warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
        assert warning_records, "expected the rehome warning to fire"
        message = warning_records[0].getMessage()
        assert "could not rehome image URI" in message
>       _assert_no_doubled_separator(message)

tests/test_builder_path_quoting_gate.py:120:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

message = "WARNING: could not rehome image URI 'C:\\\\Users\\\\runner\\\\assets\\\\sub\\\\image.png' relative to the doctree directory -- relocated to '_typst_converted/342fa359-image.png'"

E       AssertionError: Expected every backslash run to be a single unescaped separator, found a doubled/escaped run in:
E         "WARNING: could not rehome image URI 'C:\\\\Users\\\\runner\\\\assets\\\\sub\\\\image.png' relative to the doctree directory -- relocated to '_typst_converted/342fa359-image.png'"
E       assert not ['\\\\', '\\\\', '\\\\', '\\\\', '\\\\']

tests/test_builder_path_quoting_gate.py:46: AssertionError
------------------------------ Captured log call -------------------------------
WARNING  sphinx.typsphinx.builder:logging.py:138 WARNING: could not rehome image URI 'C:\\Users\\runner\\assets\\sub\\image.png' relative to the doctree directory -- relocated to '_typst_converted/342fa359-image.png'
```

The relocation key (`_typst_converted/342fa359-image.png`) is asserted NOT on its digest/suffix
(Phase 59 owns that value) — this gate stays green across it.

## RED — _validate_output_path_collisions

Command: `uv run pytest tests/test_builder_path_quoting_gate.py -q -k TestOutputPathCollisionMessagePathQuoting`

Two branches, both driven via `types.SimpleNamespace(found_docs=...)` + `builder.config.typst_documents`,
per `tests/test_builder_output_stem.py`'s established pattern.

**(a) Collision branch** — `found_docs={"index", "chapter1"}`,
`typst_documents = [("index", r"manuals\guide.typ", "T", "A"), ("chapter1", r"manuals\guide.typ", "T", "A")]`
(both entries resolve to the same wrapper path `manuals/guide.typ`):

```
_ TestOutputPathCollisionMessagePathQuoting.test_collision_branch_message_has_no_doubled_separator _

    def test_collision_branch_message_has_no_doubled_separator(
        self, temp_sphinx_app
    ):
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.env = types.SimpleNamespace(found_docs={"index", "chapter1"})
        builder.config.typst_documents = [
            ("index", r"manuals\guide.typ", "T", "A"),
            ("chapter1", r"manuals\guide.typ", "T", "A"),
        ]

        with pytest.raises(ExtensionError) as excinfo:
            builder._validate_output_path_collisions()

>       _assert_no_doubled_separator(str(excinfo.value))

message = "typst: 1 output path collision(s): 'manuals/guide.typ': typst_documents entry 0 (docname 'index', target 'manuals\\\\guide.typ') and typst_documents entry 1 (docname 'chapter1', target 'manuals\\\\guide.typ') both resolve to the same output path 'manuals/guide.typ'"

E       AssertionError: Expected every backslash run to be a single unescaped separator, found a doubled/escaped run in:
E         "typst: 1 output path collision(s): 'manuals/guide.typ': typst_documents entry 0 (docname 'index', target 'manuals\\\\guide.typ') and typst_documents entry 1 (docname 'chapter1', target 'manuals\\\\guide.typ') both resolve to the same output path 'manuals/guide.typ'"
E       assert not ['\\\\', '\\\\']

tests/test_builder_path_quoting_gate.py:46: AssertionError
```

This is the amended `:1192` site (`f"typst_documents entry {index} (docname {docname!r}, target {target!r})"`)
— exactly the site D-06's AMENDED block folds in.

**(b) Reserved-directory branch** — `found_docs={"index"}`,
`typst_documents = [("index", r"_template\x.typ", "T", "A")]` (the wrapper would land under the
reserved `_template/` output directory):

```
_ TestOutputPathCollisionMessagePathQuoting.test_reserved_directory_branch_message_has_no_doubled_separator _

    def test_reserved_directory_branch_message_has_no_doubled_separator(
        self, temp_sphinx_app
    ):
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.env = types.SimpleNamespace(found_docs={"index"})
        builder.config.typst_documents = [
            ("index", r"_template\x.typ", "T", "A"),
        ]

        with pytest.raises(ExtensionError) as excinfo:
            builder._validate_output_path_collisions()

>       _assert_no_doubled_separator(str(excinfo.value))

message = "typst: 1 output path collision(s): '_template/x.typ': typst_documents entry 0 (docname 'index', target '_template\\\\x.typ') would write its wrapper to '_template/x.typ', whose first path segment is '_template' -- that directory is reserved for template bundles"

E       AssertionError: Expected every backslash run to be a single unescaped separator, found a doubled/escaped run in:
E         "typst: 1 output path collision(s): '_template/x.typ': typst_documents entry 0 (docname 'index', target '_template\\\\x.typ') would write its wrapper to '_template/x.typ', whose first path segment is '_template' -- that directory is reserved for template bundles"
E       assert not ['\\\\']

tests/test_builder_path_quoting_gate.py:46: AssertionError
```

This is the amended `:1199` site (`f"{docname!r}, target {target!r}) would write its "`) — the
second amended site, and a MIXED f-string (`docname!r` stays `!r`, `target` routes) per the
AMENDED block's own note.

## RED — _copy_bundle_directory

Command: `uv run pytest tests/test_builder_path_quoting_gate.py -q -k TestBundleCopyMessagePathQuoting`

`builder._copy_bundle_directory(r"C:\Users\runner\project\_typst", r"C:\out\_template\mykey", "mykey", "base.typ")`
called directly; `src_dir` does not exist on this POSIX host, so `os.walk()` yields nothing, the
template is never copied, and the never-copied `ExtensionError` fires with both Windows-shaped
directory values in it.

```
_ TestBundleCopyMessagePathQuoting.test_never_copied_message_has_no_doubled_separator _

    def test_never_copied_message_has_no_doubled_separator(self, temp_sphinx_app):
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)

        with pytest.raises(ExtensionError) as excinfo:
            builder._copy_bundle_directory(
                r"C:\Users\runner\project\_typst",
                r"C:\out\_template\mykey",
                "mykey",
                "base.typ",
            )

>       _assert_no_doubled_separator(str(excinfo.value))

message = "typst_document_templates: the resolved template for registry key 'mykey' ('base.typ') was never copied from 'C:\\\\Users\\\\runner\\\\project\\\\_typst' to 'C:\\\\out\\\\_template\\\\mykey' -- a wrapper naming this key would import a file that does not exist"

E       AssertionError: Expected every backslash run to be a single unescaped separator, found a doubled/escaped run in:
E         "typst_document_templates: the resolved template for registry key 'mykey' ('base.typ') was never copied from 'C:\\\\Users\\\\runner\\\\project\\\\_typst' to 'C:\\\\out\\\\_template\\\\mykey' -- a wrapper naming this key would import a file that does not exist"
E       assert not ['\\\\', '\\\\', '\\\\', '\\\\', '\\\\', '\\\\', ...]

tests/test_builder_path_quoting_gate.py:46: AssertionError
```

Seven doubled runs total (four separators in `src_dir`, three in `dest_dir`) — matches
`template_filename` staying `!r`-quoted (`'base.typ'`, no separator, unaffected either way) and
`key` staying `!r`-quoted (`'mykey'`, an identifier, by design left unrouted).

## Non-str target characterization

### Pre-fix half (recorded now, task 1)

Command: `uv run pytest tests/test_builder_path_quoting_gate.py -q -k identifier_quoting_control`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a976975ecfffc99dc
configfile: pyproject.toml
plugins: cov-7.1.0
collected 7 items / 5 deselected / 2 selected

tests/test_builder_path_quoting_gate.py ..                               [100%]

======================= 2 passed, 5 deselected in 0.12s ========================
```

`TestBuilderIdentifierQuotingControl`'s two methods (`None` target, `123` target) are already
GREEN against the unfixed tree, because today's unconditional `!r` interpolation never raises
`TypeError` — this is the pre-fix half of the two-tree pin. Task 2 must reproduce this identical
result AFTER the `target_text` narrowing lands (the second half, below in `## GREEN`), proving the
narrowing did not change this control's observable behavior.

## GREEN

(filled below)

## Known gate gaps

(filled below)
