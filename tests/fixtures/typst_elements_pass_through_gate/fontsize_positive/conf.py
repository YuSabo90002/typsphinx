# Sphinx configuration for the GATE-01 `typst_elements` fontsize positive
# gate (Phase 26, CONF-04, SC#2).
#
# SEPARATE from the papersize fixture (SC#1/SC#2 explicitly require
# separate proofs -- a combined papersize+fontsize case would hide a
# per-key emission-type bug). This fixture proves `fontsize` reaches the
# `#show: project.with(...)` region as an UNQUOTED Typst length (D-02),
# via the `RawTypst` marker recognized by `_format_typst_value()` --
# NEVER as a quoted string (the "double-formatting trap", Pitfall 1).
#
# Uses the DEFAULT (unset `typst_package`/`typst_template`) template path,
# since `fontsize` is a parameter of `templates/base.typ`'s own
# `project()` function (the byte-frozen receiving contract, SC#5).

project = "Typst Elements Fontsize Positive Gate"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "index", project, author),
]

typst_elements = {
    "fontsize": "20pt",
}
