# CR-01: real-sphinx-build reproduction of an EXPLICIT typst_documents entry
# colliding with the reserved `_template.typ` infrastructure file. `project`
# is deliberately neutral (non-colliding) so the only source of the
# collision is the explicit entry naming "_template.typ" as the master's
# target.
#
# Load-bearing property -- do NOT touch, or this fixture silently stops
# exercising CR-01's explicit-template half:
#   - The typst_documents target name below must remain "_template.typ".

project = "Explicit Template Collision Gate"
author = "Test Author"
release = "1.0.0"
copyright = "2026, Test Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "_template.typ", project, author),
]
