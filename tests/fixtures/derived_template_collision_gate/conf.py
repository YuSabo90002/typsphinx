# D-01 (Phase 47 plan 09, replacing CR-01): real-sphinx-build reproduction
# of the zero-configuration RESERVED-TEMPLATE clobber. `project =
# "_Template"` slugifies (make_filename_from_project preserves underscores)
# to the stem "_template", IDENTICAL to the reserved `_template.typ`
# basename `_write_template_file()` writes at the outdir root before any
# document is written. Since the content/wrapper split, this now FAILS the
# build with a single pre-write ExtensionError (D-01/D-02/D-03), and NO
# `.typ` file -- including `_template.typ` itself -- is ever written.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising CR-01's template-clobber half:
#   - NO `typst_documents` line: the derived default (CONF-08) must be the
#     thing that produces the colliding target name.
#   - `project` must remain exactly "_Template".

project = "_Template"
author = "Test Author"
release = "1.0.0"
copyright = "2026, Test Author"

extensions = ["typsphinx"]

# typst_documents intentionally left unset -- the derived default must
# resolve to [('index', '_template.typ', project, author, 'typst')], which
# collides with the reserved _template.typ infrastructure file.
