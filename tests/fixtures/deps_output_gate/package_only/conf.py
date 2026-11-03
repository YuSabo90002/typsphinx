# typst_package-only route: no custom template, so the wrapper imports the
# package's template function and no bundled template. Built with -b typst
# only (the package is never compiled here).
project = "Deps Package Only"
author = "Test Author"
extensions = ["typsphinx"]
typst_documents = [("index", "paper.typ", "Deps Package Only", "Test Author")]
typst_package = "@preview/charged-ieee:0.1.4"
typst_template_function = "ieee"
