# Sphinx configuration for the nested-master render-gate fixture
# (Phase 22.1, GATE-01 regression -- PDF-02).
#
# Minimal self-contained project used by
# tests/test_nested_master_render_gate.py to prove `-b typstpdf` compiles a
# master that sits at a NESTED docname (`api/index`), not just at the outdir
# root. This is the fast, offline reproduction of the compile-root
# divergence that Phase 22.1 fixes:
#
# Root cause: TypstPDFBuilder.finish() used to read a master's `.typ` into a
# string and hand it to compile_typst_to_pdf(content, root_dir=self.outdir),
# which wrote that string to a NamedTemporaryFile(dir=root_dir) -- i.e. at
# the OUTDIR ROOT -- and compiled *that* file. Typst resolves every relative
# path (#include(), image()) against the file being compiled, while the
# translator emits those paths docname-relative. The two bases coincided
# only when the master sat at the outdir root, so a master at `api/index`
# emitted `include("usage.typ")` (sibling, relative to `api/`) that the
# temp copy at the outdir root could never resolve to `outdir/usage.typ`.
#
# Fix: compile_typst_file_to_pdf() now compiles the master's own `.typ` at
# its real, docname-derived location (`outdir/api/index.typ`), so the two
# bases are structurally identical.

project = "Nested Master Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# Making the nested document the project's root document keeps this fixture
# to a single master with nothing at the outdir root at all, so nothing in
# the project could accidentally mask the nested-master condition.
root_doc = "api/index"

# Phase 47 (OUT-01): the target used to equal the docname's basename
# ("index") on purpose (D-07), to keep the Phase 22 target-name rename out
# of this gate's failure surface. Under OUT-01 a bare target still resolves
# at the outdir root regardless of its literal string -- "index" itself
# does not collide with anything in THIS fixture (there is no root-level
# "index" docname; the only docname is the NESTED "api/index", whose
# content file is unconditionally at "api/index.typ", never at the outdir
# root). The rename to "nested-master.typ" below is not a collision fix
# for this specific fixture -- it is the general fixture de-collision
# convention (47-EXPECTED-STRUCTURE.md): a target string that reads as an
# "index" identity invites exactly the misreading this comment forestalls.
# What is load-bearing about this fixture is unchanged: the DOCNAME is
# nested ("api/index") while the TARGET is a bare name with no path
# component, so the WRAPPER resolves at the outdir root -- one directory
# level away from its own entry's CONTENT file (COMP-01, always at
# "api/index.typ") and from the sibling include/image references that
# live inside that content file's own body.
typst_documents = [
    ("api/index", "nested-master.typ", "Nested Master Render Gate", "Test Author"),
]
