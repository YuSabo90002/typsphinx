# Phase 60 Plan 03 — MSG-04 Evidence

## Plan base SHA

```
1118199a577533f598a799b51d08b7bc3e9bcc49
```

## Discovery grep

Command: `grep -n "!r" typsphinx/writer.py`

```
154:            f"{entry[0]!r} is not a str: {value!r} -- "
155:            f"falling back to {default!r}"
511:            f"Rendering wrapper for docname {docname!r} at "
512:            f"wrapper_relative_dir={wrapper_relative_dir!r}, "
513:            f"include_path={include_path!r}, template_file={template_file!r}"
```

Classification (D-05's role rule — "does the reader read this as a location on a
filesystem, or as a name in a namespace?"):

- `:154` `entry[0]!r` — identifier-valued (the entry's docname, `_entry_element_value`'s
  first positional arg). Stays unrouted (D-07).
- `:154` `value!r` — the non-`str` `typst_documents` element itself (a title/author
  value resolved from that specific entry), not a filesystem location. Stays unrouted
  (D-07).
- `:155` `default!r` — the fallback value, `config.project` or `config.author` depending
  on the caller. Title/author-valued, not path-valued. Stays unrouted (D-07).
- `:511` `docname!r` — identifier-valued (the same `entry[0]` read positionally into
  `docname` a few lines above). Stays unrouted (D-07). MSG-04 explicitly names this as
  the one value on the routed line that stays `!r`.
- `:512` `wrapper_relative_dir!r` — the wrapper's own resolved output directory,
  relative to the outdir root. Path-valued. Routes through `quote_path()`.
- `:513` `include_path!r` — `compute_content_include_path()`'s return value, itself a
  `posixpath.relpath` between two output-relative paths. Path-valued. Routes.
- `:513` `template_file!r` — either `None` (package-alone path, `:503-504`) or
  `compute_template_import_path()`'s root-absolute import path (`:507-509`). Path-valued
  (or the `None` D-03 handles). Routes.

This module has no `%r` occurrence (checked: `grep -n '%r' typsphinx/writer.py` returns
nothing) and no hardcoded-delimiter interpolation (checked: no `f"'{...}'"` or
`f"\"{...}\""` pattern present in the module).

## RED — wrapper-render debug log

Command: `uv run pytest tests/test_writer_path_quoting_gate.py -q` (plan base SHA
`1118199a577533f598a799b51d08b7bc3e9bcc49`, before `typsphinx/writer.py` was edited).

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a82773657d1290632
configfile: pyproject.toml
plugins: cov-7.1.0
collected 2 items

tests/test_writer_path_quoting_gate.py F.                                [100%]

=================================== FAILURES ===================================
_ TestWrapperDebugLogPathQuoting.test_wrapper_debug_log_has_no_doubled_separator_for_windows_shaped_paths _

self = <test_writer_path_quoting_gate.TestWrapperDebugLogPathQuoting object at 0x7ba486651f90>
temp_sphinx_app = <SphinxTestApp buildername='html'>
caplog = <_pytest.logging.LogCaptureFixture object at 0x7ba484ed9550>

    def test_wrapper_debug_log_has_no_doubled_separator_for_windows_shaped_paths(
        self, temp_sphinx_app, caplog
    ):
        """Pre-fix, this record carries eleven doubled runs (three `!r`
        conversions each doubling every backslash in a Windows-shaped
        value)."""
        app = temp_sphinx_app
        writer = TypstWriter(app.builder)
        doctree = _build_single_section_document()

        wrapper_relative_dir = "C:\\Users\\runner\\out\\sub"
        content_relative_path = "C:\\Users\\runner\\out\\sub\\index.typ"

        with caplog.at_level("DEBUG"):
            writer.render_wrapper(
                ("index", "manual.typ", "T", "A"),
                doctree,
                wrapper_relative_dir,
                content_relative_path,
            )

        debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
        wrapper_records = [
            r
            for r in debug_records
            if r.getMessage().startswith("Rendering wrapper for docname")
        ]
        assert len(wrapper_records) == 1, (
            f"Expected exactly one wrapper-render debug record, found "
            f"{len(wrapper_records)}: {[r.getMessage() for r in debug_records]}"
        )
        message = wrapper_records[0].getMessage()

>       _assert_no_doubled_separator(message)

tests/test_writer_path_quoting_gate.py:87:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

message = "Rendering wrapper for docname 'index' at wrapper_relative_dir='C:\\\\Users\\\\runner\\\\out\\\\sub', include_path='../C:\\\\Users\\\\runner\\\\out\\\\sub\\\\index.typ', template_file='/_template/typst/base.typ'"

    def _assert_no_doubled_separator(message: str) -> None:
        """Re-derives the guard predicate locally, importing nothing from
        the sibling `builder.py` wiring plan's own collision-gate test
        module (that module's shared-class extension is its exclusive
        privilege, D-11). No run of consecutive backslashes longer than 1
        may appear -- that is what `repr()` escaping would produce and what
        this guard exists to catch."""
        doubled = re.findall(r"\\\\+", message)
>       assert not doubled, (
            f"Expected every backslash run to be a single unescaped "
            f"separator, found a doubled/escaped run in:\n{message!r}"
        )
E       AssertionError: Expected every backslash run to be a single unescaped separator, found a doubled/escaped run in:
E         "Rendering wrapper for docname 'index' at wrapper_relative_dir='C:\\\\Users\\\\runner\\\\out\\\\sub', include_path='../C:\\\\Users\\\\runner\\\\out\\\\sub\\\\index.typ', template_file='/_template/typst/base.typ'"
E       assert not ['\\\\', '\\\\', '\\\\', '\\\\', '\\\\', '\\\\', ...]

tests/test_writer_path_quoting_gate.py:31: AssertionError
------------------------------ Captured log call -------------------------------
DEBUG    sphinx.typsphinx.writer:logging.py:138 Rendering wrapper for docname 'index' at wrapper_relative_dir='C:\\Users\\runner\\out\\sub', include_path='../C:\\Users\\runner\\out\\sub\\index.typ', template_file='/_template/typst/base.typ'
=========================== short test summary info ============================
FAILED tests/test_writer_path_quoting_gate.py::TestWrapperDebugLogPathQuoting::test_wrapper_debug_log_has_no_doubled_separator_for_windows_shaped_paths
========================= 1 failed, 1 passed in 0.14s ==========================
```

**Measured count correction:** the plan's own `must_haves.truths` cites "eleven doubled runs"
as the pre-fix count; re-deriving `re.findall(r"\\\\+", message)` directly against the
captured message string above (`Rendering wrapper for docname 'index' at
wrapper_relative_dir='C:\\Users\\runner\\out\\sub', include_path='../C:\\Users\\runner\\out\\sub\\index.typ',
template_file='/_template/typst/base.typ'`) returns **9** doubled runs (4 in
`wrapper_relative_dir`'s four separators, 5 in `include_path`'s five separators;
`template_file` here resolves to the bundled default template's forward-slash-only
import path, contributing zero). Recorded as measured rather than restated, per this
plan's own instruction to re-measure rather than trust a stale coordinate; the RED
verdict itself (doubled runs present, test fails) is unaffected by the exact count.

## None pin (two-tree)

### Pre-fix half

Command: `uv run pytest tests/test_writer_path_quoting_gate.py -q -k template_file_none`
(plan base SHA `1118199a577533f598a799b51d08b7bc3e9bcc49`, before `typsphinx/writer.py`
was edited).

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a82773657d1290632
configfile: pyproject.toml
plugins: cov-7.1.0
collected 2 items / 1 deselected / 1 selected

tests/test_writer_path_quoting_gate.py .                                 [100%]

======================= 1 passed, 1 deselected in 0.11s ========================
```

This method is GREEN before any product edit, confirming D-03's contract already holds
today via plain `!r` conversion on `None` (`repr(None) == "None"`) -- `quote_path(None)`
must reproduce this exactly, per D-03.

### Post-fix half

Command: `uv run pytest tests/test_writer_path_quoting_gate.py -q -k template_file_none -s`
(after `typsphinx/writer.py` was edited to route through `quote_path()`).

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a82773657d1290632
configfile: pyproject.toml
plugins: cov-7.1.0
collected 2 items / 1 deselected / 1 selected

tests/test_writer_path_quoting_gate.py .

======================= 1 passed, 1 deselected in 0.11s ========================
```

**Emitted debug line, pre-fix:**
```
Rendering wrapper for docname 'index' at wrapper_relative_dir='', include_path='index.typ', template_file=None
```

**Emitted debug line, post-fix:**
```
Rendering wrapper for docname 'index' at wrapper_relative_dir='', include_path='index.typ', template_file=None
```

**These two debug lines are byte-identical.** D-03's `None` contract holds: the
package-alone build path's `template_file = None` renders to the bare four-character word
`None` unchanged before and after routing through `quote_path()`, and the empty
`wrapper_relative_dir` renders as two apostrophes unchanged either way.

**Measurement method:** `git checkout 1118199a577533f598a799b51d08b7bc3e9bcc49 --
typsphinx/writer.py` restored the pre-fix module while keeping the new test in place
(a temporary local `print()` of the extracted `caplog` message was used to surface the
line to stdout, since Sphinx's own logging setup does not propagate `DEBUG` records to
a plain `basicConfig` handler outside `caplog`'s own capture mechanism; the print was
removed immediately after both halves were captured and confirmed by `git diff --stat --
tests/test_writer_path_quoting_gate.py` showing no diff against the committed test file).
The post-fix half was restored via a pre-saved copy of the edited `typsphinx/writer.py`
(not `git checkout HEAD`, since `HEAD` at measurement time predates this task's own
not-yet-committed fix and is therefore identical to the plan base SHA for this file).

## GREEN

Command: `uv run pytest tests/test_writer_path_quoting_gate.py -q`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a82773657d1290632
configfile: pyproject.toml
plugins: cov-7.1.0
collected 2 items

tests/test_writer_path_quoting_gate.py ..                                [100%]

============================== 2 passed in 0.12s ===============================
```

Command: `uv run pytest -q` (full suite)

```
================= 1496 passed, 5 skipped in 123.60s (0:02:03) ==================
```

Command: `uv run black --check .`

```
All done! ✨ 🍰 ✨
351 files would be left unchanged.
```

Command: `uv run mypy typsphinx/`

```
Success: no issues found in 9 source files
```

Command: `uv run pytest tests/test_repr_census_guard.py -q`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a82773657d1290632
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests/test_repr_census_guard.py ....                                     [100%]

============================== 4 passed in 0.61s ===============================
```

The `typsphinx/writer.py` diff (task 2's whole change):

```diff
diff --git a/typsphinx/writer.py b/typsphinx/writer.py
index 4f0dcebe..2e4f6269 100644
--- a/typsphinx/writer.py
+++ b/typsphinx/writer.py
@@ -12,6 +12,7 @@ from typing import Any, Tuple
 from docutils import writers
 from sphinx.util import logging
 
+from typsphinx.pathfmt import quote_path
 from typsphinx.template_engine import (
     TEMPLATE_SEARCH_SUBDIR,
     TemplateEngine,
@@ -509,7 +510,8 @@ class TypstWriter(writers.Writer):
             )
         logger.debug(
             f"Rendering wrapper for docname {docname!r} at "
-            f"wrapper_relative_dir={wrapper_relative_dir!r}, "
-            f"include_path={include_path!r}, template_file={template_file!r}"
+            f"wrapper_relative_dir={quote_path(wrapper_relative_dir)}, "
+            f"include_path={quote_path(include_path)}, "
+            f"template_file={quote_path(template_file)}"
         )
         return template_engine.render(params, body, template_file=template_file)
```

No conditional was added for the `None` case (`grep -c 'if template_file is None'
typsphinx/writer.py` returns `0`) -- `quote_path(None)` itself returns the bare string
`"None"` per D-03, keeping this a straight three-value substitution. `docname` on the
same line is untouched (`grep -cE '\{docname!r\}' typsphinx/writer.py` returns `1`).

## D-07 confirmation

## Known gate gaps
