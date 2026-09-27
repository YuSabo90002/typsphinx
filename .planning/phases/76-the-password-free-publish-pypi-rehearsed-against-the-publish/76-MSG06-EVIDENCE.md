# Phase 76 — MSG-06 Evidence

## Provisioning and base

MSG06_BASE_SHA = e3c169d4e7b52d828f6ebe2b04e55513df49ddfc

Recorded via `git rev-parse HEAD` before any edit, inside the worktree
(`test -f .git` confirmed true first).

SCRATCH_76_02 = /tmp/p7602.CEbXSs

Created via `mktemp -d -t p7602.XXXXXX`.

PYVENV_HOME = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin

PYVENV_VERSION_INFO = 3.14

Both read from `.venv/pyvenv.cfg` after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`
provisioned this worktree's own venv (fresh worktree venv uses uv-managed CPython 3.14,
not the main checkout's nixpkgs interpreter — expected per CLAUDE.md/MEMORY.md).

## Discovery grep

Command: `awk '/def _compute_relative_include_path\(/{p=1} /def _sanitize_label\(/{p=0} p' typsphinx/translator.py | grep -cE "'\{[a-zA-Z_.]+\}'"`

```
2
```

MSG06_DISCOVERY_REGION_HITS = 2

Command: `grep -nE "'\{[a-zA-Z_.]+\}'" typsphinx/translator.py`

```
5121:                f"up_path='{up_path}', down_path='{down_path}', "
5226:                f"up_path='{up_path}', down_path='{down_path}', "
5446:            logger.warning(f"Could not parse length value '{value}'; dropping.")
5461:            f"Unsupported length unit '{unit}' in '{value}'; "
```

MSG06_DISCOVERY_FILE_WIDE_HITS = 4

MSG06_DISCOVERY_SITE_LINES = 5121,5226

The two out-of-region hits at `:5446` and `:5461` are the length-value warnings inside
the length-parsing helper (well past `_sanitize_label`'s definition line 5233 in file
order, but the more precise anchor is that they lie outside the
`_compute_relative_include_path`..`_sanitize_label` region entirely) — they are not
filesystem path fragments and are out of scope for this plan (they classify as
identifier/value-valued length strings, not paths).

## RED — pre-fix tree

MSG06_RED_TEST_COMMIT = 68065948277abd93488f9686e6d656cf183fe209

Recorded via `git rev-parse HEAD` after the test-only commit
(`test(76-02): add failing MSG-06 gate for translator cross-directory debug logs`).

Command: `LC_ALL=C uv run pytest tests/test_translator_path_quoting_gate.py -q -p no:cacheprovider` (plan base SHA `e3c169d4e7b52d828f6ebe2b04e55513df49ddfc`, before `typsphinx/translator.py` was edited)

```
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7bd46f0b3a1d6917
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests/test_translator_path_quoting_gate.py F.F.                          [100%]

=================================== FAILURES ===================================
_ TestIncludePathDebugLogQuoting.test_apostrophe_in_down_path_does_not_close_the_quote_early _

self = <test_translator_path_quoting_gate.TestIncludePathDebugLogQuoting object at 0x7f5cc591c550>
mock_document = <document: >
mock_builder = <test_translator_path_quoting_gate.mock_builder.<locals>.MockBuilder object at 0x7f5cc57be7b0>
caplog = <_pytest.logging.LogCaptureFixture object at 0x7f5cc57bea50>

    def test_apostrophe_in_down_path_does_not_close_the_quote_early(
        self, mock_document, mock_builder, caplog
    ):
        translator = TypstTranslator(mock_document, mock_builder)

        with caplog.at_level("DEBUG"):
            result = translator._compute_relative_include_path(
                "chapter2/o'brien", "chapter1/doc1"
            )

        assert result == "../chapter2/o'brien"
        message = _single_cross_directory_message(caplog)
>       assert message == (
            "Cross-directory path calculation: up_count=1, up_path='../', "
            "down_path=\"chapter2/o'brien\", result: ../chapter2/o'brien"
        )
E       assert "Cross-direct...pter2/o'brien" == "Cross-direct...pter2/o'brien"
E
E         Skipping 61 identical leading characters in diff, use -v to show
E         - down_path="chapter2/o'brien", result: ../chapter2/o'brien
E         ?           ^                ^
E         + down_path='chapter2/o'brien', result: ../chapter2/o'brien
E         ?           ^                ^

tests/test_translator_path_quoting_gate.py:95: AssertionError
------------------------------ Captured log call -------------------------------
DEBUG    sphinx.typsphinx.translator:logging.py:138 Computing relative include path: target=chapter2/o'brien, current=chapter1/doc1
DEBUG    sphinx.typsphinx.translator:logging.py:138 Path components: current_dir=chapter1, target_path=chapter2/o'brien
DEBUG    sphinx.typsphinx.translator:logging.py:138 Cross-directory reference detected, calculating via common parent
DEBUG    sphinx.typsphinx.translator:logging.py:138 Common parent depth: 0, current_parts=('chapter1',), target_parts=('chapter2', "o'brien")
DEBUG    sphinx.typsphinx.translator:logging.py:138 Cross-directory path calculation: up_count=1, up_path='../', down_path='chapter2/o'brien', result: ../chapter2/o'brien
_ TestImagePathDebugLogQuoting.test_apostrophe_in_down_path_does_not_close_the_quote_early _

self = <test_translator_path_quoting_gate.TestImagePathDebugLogQuoting object at 0x7f5cc56d0050>
mock_document = <document: >
mock_builder = <test_translator_path_quoting_gate.mock_builder.<locals>.MockBuilder object at 0x7f5cc5698050>
caplog = <_pytest.logging.LogCaptureFixture object at 0x7f5cc56d0b90>

    def test_apostrophe_in_down_path_does_not_close_the_quote_early(
        self, mock_document, mock_builder, caplog
    ):
        translator = TypstTranslator(mock_document, mock_builder)

        with caplog.at_level("DEBUG"):
            result = translator._compute_relative_image_path(
                "images/o'brien.png", "chapter1/doc1"
            )

        assert result == "../images/o'brien.png"
        message = _single_cross_directory_message(caplog)
>       assert message == (
            "Cross-directory path calculation: up_count=1, up_path='../', "
            "down_path=\"images/o'brien.png\", result: ../images/o'brien.png"
        )
E       assert "Cross-direct...s/o'brien.png" == "Cross-direct...s/o'brien.png"
E
E         Skipping 61 identical leading characters in diff, use -v to show
E         - down_path="images/o'brien.png", result: ../images/o'brien.png
E         ?           ^                  ^
E         + down_path='images/o'brien.png', result: ../images/o'brien.png
E         ?           ^                  ^

tests/test_translator_path_quoting_gate.py:134: AssertionError
------------------------------ Captured log call -------------------------------
DEBUG    sphinx.typsphinx.translator:logging.py:138 Computing relative image path: uri=images/o'brien.png, current=chapter1/doc1
DEBUG    sphinx.typsphinx.translator:logging.py:138 Path components: current_dir=chapter1, image_path=images/o'brien.png
DEBUG    sphinx.typsphinx.translator:logging.py:138 Cross-directory reference detected, calculating via common parent
DEBUG    sphinx.typsphinx.translator:logging.py:138 Common parent depth: 0, current_parts=('chapter1',), image_parts=('images', "o'brien.png")
DEBUG    sphinx.typsphinx.translator:logging.py:138 Cross-directory path calculation: up_count=1, up_path='../', down_path='images/o'brien.png', result: ../images/o'brien.png
=========================== short test summary info ============================
FAILED tests/test_translator_path_quoting_gate.py::TestIncludePathDebugLogQuoting::test_apostrophe_in_down_path_does_not_close_the_quote_early
FAILED tests/test_translator_path_quoting_gate.py::TestImagePathDebugLogQuoting::test_apostrophe_in_down_path_does_not_close_the_quote_early
========================= 2 failed, 2 passed in 0.05s ==========================
```

MSG06_RED_FAILED = 2

MSG06_RED_PASSED = 2

Extracted with `grep -oE '[0-9]+ (passed|failed)'` against the saved transcript
(`$SCRATCH_76_02/p7602_red.txt`). The two failures are exactly the two apostrophe
tests (`TestIncludePathDebugLogQuoting` and `TestImagePathDebugLogQuoting`, both
`test_apostrophe_in_down_path_does_not_close_the_quote_early`), and each
`AssertionError` shows the pre-fix, early-closing actual message
(`down_path='chapter2/o'brien', result: …` and
`down_path='images/o'brien.png', result: …`). The two empty-`down_path` pins
passed as expected (byte-identity, unaffected by the fix either way).

## Include-path site routed

In `typsphinx/translator.py`: added `from typsphinx.pathfmt import quote_path` in a
separate first-party import block after `from sphinx.util.docutils import
SphinxTranslator` (matching `writer.py`'s own placement). In
`_compute_relative_include_path()` only, the cross-directory f-string line now reads
`f"up_path={quote_path(up_path)}, down_path={quote_path(down_path)}, "` — the
hardcoded apostrophes around both values are removed; the `up_count=` and `result:`
fragments and every other log line in the file are untouched. The image-path site is
left for Task 2.

Command: `LC_ALL=C uv run pytest "tests/test_translator_path_quoting_gate.py::TestIncludePathDebugLogQuoting" -q -p no:cacheprovider`

```
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7bd46f0b3a1d6917
configfile: pyproject.toml
plugins: cov-7.1.0
collected 2 items

tests/test_translator_path_quoting_gate.py ..                            [100%]

============================== 2 passed in 0.04s ===============================
```

MSG06_INCLUDE_NODE_PASSED = 2

`grep -cx 'from typsphinx.pathfmt import quote_path' typsphinx/translator.py` returns
`1`. `uv run black --check typsphinx/translator.py` and `uv run ruff check
typsphinx/translator.py` both exit 0.

<!-- gsd:write-continue -->
