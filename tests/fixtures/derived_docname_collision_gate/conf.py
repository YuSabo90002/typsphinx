# CR-01: real-sphinx-build reproduction of the zero-configuration docname
# collision. `project = "Chapter 1"` slugifies (make_filename_from_project)
# to the stem "chapter1", which is IDENTICAL to the docname of the real
# `chapter1.rst` this project toctree-includes -- an ordinary "project named
# after its first chapter" docs layout.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising CR-01:
#   - NO `typst_documents` line: the derived default (CONF-08) must be the
#     thing that produces the colliding target name.
#   - `project` must remain exactly "Chapter 1" (renaming it changes the
#     derived stem and the collision disappears).
#   - `chapter1.rst` must keep its filename (renaming it changes the docname
#     and the collision disappears).

project = "Chapter 1"
author = "Test Author"
release = "1.0.0"
copyright = "2026, Test Author"

extensions = ["typsphinx"]

# typst_documents intentionally left unset -- the derived default must
# resolve to [('index', 'chapter1.typ', project, author, 'typst')], which
# collides with the real chapter1.rst document's own output path.
