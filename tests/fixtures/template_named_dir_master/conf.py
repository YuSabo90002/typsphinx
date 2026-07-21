# Sphinx configuration for the template-named-dir-master fixture
# (Phase 22.1, gap G-22.1-4 -- CR-01 closure).
#
# Reproduces a project whose master documents live inside a source
# subdirectory literally named `_template`, colliding with the reserved
# `_template.typ` basename that `_write_template_file()` (builder.py)
# unconditionally writes at the outdir root. This is a realistic layout --
# an author holding custom Typst partials in a `_template/` directory,
# mirroring the tool's own reserved naming.
#
# Pre-fix, TypstWriter.translate() computed the template import by
# relativizing the master's docname against a synthetic "_template" sentinel
# target docname. When the master's own directory portion was itself
# literally "_template", the sentinel collided with a real path component
# and produced a malformed, stem-less reference (e.g. "#import "..typ""
# at depth 1, "#import "../.typ"" at depth 2). The depth-based fix has no
# such string dependence.

project = "Template Named Dir Master"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# The depth-1 master is the project root, keeping nothing else at the
# outdir root that could mask the condition (mirrors
# tests/fixtures/nested_master_render_gate/conf.py's reasoning).
root_doc = "_template/index"

# Both masters share a target basename equal to their own docname basename
# (D-07 reasoning, mirrored from the sibling PDF-02 fixture): the Phase 22
# target-name rename must NOT be exercised here. The two entries live in
# different directories, so their outputs do not collide.
typst_documents = [
    ("_template/index", "index", "Template Named Dir Master", "Test Author"),
    (
        "_template/sub/index",
        "index",
        "Template Named Dir Master (nested)",
        "Test Author",
    ),
]
