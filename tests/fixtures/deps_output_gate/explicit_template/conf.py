# Explicit-template route: a user template that imports nothing from the
# five packages.
project = "Deps Explicit Template"
author = "Test Author"
extensions = ["typsphinx"]
typst_documents = [("index", "manual.typ", "Deps Explicit Template", "Test Author")]
typst_template = "_typst/custom.typ"
