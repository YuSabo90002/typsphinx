# Sphinx configuration for the two_key_selection_gate fixture (Phase 54,
# TPL-02, OUT-06).
#
# Declares TWO registry keys via typst_document_templates and three
# typst_documents entries. The first two entries deliberately share the
# key "report" at two DIFFERENT wrapper depths -- the root ("master") and
# nested inside "manuals/" ("manuals/guide") -- because that pair is
# OUT-06's entire proof: a root-absolute `#import` path means both
# wrappers, regardless of nesting depth, import the IDENTICAL bundled
# template path. The third entry uses the distinct "memo" key so
# per-document template SELECTION (TPL-02) is exercised in the same
# build, not merely declared.
#
# Both template bundles live under `_typst/<key>/` rather than at srcdir
# root -- same D-14 bundle-directory invariant the OUT-05 fixture carries:
# a resolved template's PARENT directory is what gets copied wholesale to
# `<outdir>/_template/<key>/`, so each bundle must be a genuine directory,
# never srcdir itself.

project = "Two Key Selection Gate"
author = "Report Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

typst_document_templates = {
    "report": {"template": "_typst/report/base.typ"},
    "memo": {"template": "_typst/memo/base.typ"},
}

typst_documents = [
    ("index", "master", "Report Root", "Report Author", "report"),
    ("guide/index", "manuals/guide", "Report Nested", "Report Author", "report"),
    ("memo/index", "memos/memo", "Memo Master", "Memo Author", "memo"),
]
