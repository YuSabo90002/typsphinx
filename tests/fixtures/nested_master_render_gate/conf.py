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

# Target name equals the docname's basename ON PURPOSE (D-07): the Phase 22
# target-name rename must NOT be exercised here, so that when this gate goes
# red the cause is unambiguously PDF-02, not a target-name interaction.
typst_documents = [
    ("api/index", "index", "Nested Master Render Gate", "Test Author"),
]
