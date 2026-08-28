"""
IMG-06(b): `copy_image_files()` swallows the `OSError` a too-long
relocation-key final component raises (`builder.py:1988-1992`'s
``except Exception as e: logger.warning(...)``), so the fix must be
proven at the integration level -- through a real
`sphinx-build`-constructed doctree and a real filesystem copy attempt --
because `pytest.raises(OSError)` cannot observe an exception the product
code itself catches and logs.

Uses `caplog`, never a `warnings`-module interception helper: this is a
`sphinx.util.logging` call, not `warnings.warn()` (59-RESEARCH.md
Pitfall 4).

The filesystem probe that decides whether this host can even construct
the long-basename fixture runs INSIDE the test body (an in-body
`except OSError: pytest.skip(...)`), never as a collection-time marker
decorator that references a fixture -- such decorators are evaluated
before `tmp_path` exists (59-RESEARCH.md Pitfall 1).
"""

import shutil
from pathlib import Path

import pytest
from docutils import nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter

from typsphinx.builder import TypstBuilder

_FIXTURE_PNG = (
    Path(__file__).parent
    / "fixtures"
    / "absolute_image_render_gate"
    / "_static"
    / "converted_stand_in.png"
)


def _build_single_image_document(uri: str) -> nodes.document:
    """A minimal one-image doctree, following `tests/test_builder.py`'s
    `Reporter`/`states.Struct` document setup."""
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    img = nodes.image(uri=uri, candidates={"*": uri})
    doc += img
    return doc


class TestCopyImageFilesNameTooLong:
    """IMG-06(b)'s integration gate: a long-basename absolute image URI,
    driven through the real escape branch and a real `copy_image_files()`
    call, must copy successfully with no `Failed to copy image` warning."""

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
        assert not any(
            "Failed to copy image" in m for m in warning_messages
        ), f"unexpected copy failure warning(s): {warning_messages!r}"

        dest_path = Path(builder.outdir) / img["uri"]
        assert dest_path.exists(), (
            f"expected destination file to exist at {dest_path}, "
            f"warnings were: {warning_messages!r}"
        )
