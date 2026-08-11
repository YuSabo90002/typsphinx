"""Sphinx config for the DOC-12 changelog-page regression gate.

Mirrors the real published page's mechanism (docs/source/changelog.rst) at a
minimal scale: a single ``changelog.rst`` document that ``.. include::``s the
repository-root ``CHANGELOG.md`` via myst-parser's ``:parser:`` option.

WHY THIS FIXTURE'S INCLUDE PATH POINTS OUTSIDE THE FIXTURE DIRECTORY: from
this fixture's depth (``tests/fixtures/changelog_include_gate/``), the
relative path to the real repository-root ``CHANGELOG.md`` is
``../../../CHANGELOG.md``. This is deliberate -- the fixture must read the
REAL changelog so its content assertions (every release version string
present, zero changelog-attributable build warnings) are genuine, not
synthetic. Do NOT copy ``CHANGELOG.md`` into this fixture tree: a local copy
would drift from the real file silently and this gate would stop proving
anything about the published page.
"""

project = "Changelog Include Gate"
author = "Test Author"
release = "1.0.0"
copyright = "2026, Test Author"

extensions = [
    "myst_parser",
    "typsphinx",
]

# index must be a master document so TypstPDFBuilder.finish() actually
# compiles it to PDF -- the only build path this gate's PDF assertions need.
typst_documents = [
    ("index", "index", "Changelog Include Gate", "Test Author"),
]
