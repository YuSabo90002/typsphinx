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
#
# Phase 47 (OUT-01/BLD-02, 47-EXPECTED-STRUCTURE.md's fixture de-collision
# rule): both entries used to target the identity basename "index" (equal
# to their own docname's basename), which the pre-Phase-47
# `_directory_preserving_relpath()` force-relocated into each docname's own
# directory so the two outputs never collided. OUT-01 reverses that
# forcing -- a bare target (no path separator) now resolves at the OUTDIR
# ROOT, unconditionally -- so both entries' "index" targets would resolve
# to the SAME physical path (`outdir/index.typ`), a BLD-02 duplicate-target
# collision. The two distinct targets below (`template-dir-master.typ`,
# `template-dir-sub.typ`) are therefore load-bearing, not merely a rename:
# two entries resolving to one path is a build error under D-02/D-03.

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

# CONF-09 (Phase 44.2, SC#3): the second entry's author deliberately
# diverges from the first ("Test Author (nested)" vs "Test Author") so a
# per-master author leak is detectable -- both entries' titles already
# diverge (the title half of the leak was already detectable before this
# phase), but until now both entries shared the SAME author, so an author
# leak between the two masters was undetectable.
#
# Both targets are bare (no path separator), so both WRAPPERS resolve at
# the outdir root under OUT-01 -- this fixture's own purpose (docnames
# living inside a directory literally named `_template`) is carried
# entirely by the unconditional, docname-derived CONTENT files (COMP-01),
# which still land inside `_template/` regardless of where either entry's
# wrapper resolves.
typst_documents = [
    (
        "_template/index",
        "template-dir-master.typ",
        "Template Named Dir Master",
        "Test Author",
    ),
    (
        "_template/sub/index",
        "template-dir-sub.typ",
        "Template Named Dir Master (nested)",
        "Test Author (nested)",
    ),
]
