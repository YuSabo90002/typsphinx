# typst_dependencies override: deps/my-deps.typ (srcdir-relative) is copied
# byte-identical to <outdir>/_typsphinx/deps.typ in place of the generated
# default. It pins gentle-clues 1.3.0 instead of the default 1.3.1.
project = "Deps Override"
author = "Test Author"
extensions = ["typsphinx"]
typst_dependencies = "deps/my-deps.typ"
