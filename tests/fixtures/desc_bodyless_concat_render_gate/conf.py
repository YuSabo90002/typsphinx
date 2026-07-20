# Sphinx configuration for the desc-bodyless-concat render-gate fixture
# (Phase 19, GATE-01, FID-06).
#
# Minimal self-contained project used by
# tests/test_desc_bodyless_concat_render_gate.py to prove the translator
# emits a real parbreak() between back-to-back body-less confval `desc`
# siblings. This is the fast, offline reproduction of the v0.6.1-audit
# finding F15: a confval directive with only :type:/:default: fields (no
# body paragraph) renders entirely inline (no par() anywhere), so consecutive
# such desc siblings concatenate with zero separation -- mirroring
# usage/extensions/coverage.rst's four back-to-back confvals, which merge
# into one blob: "coverage_c_pathType:...Default:()coverage_c_regexesType:...".
#
# Fix: depart_desc now calls self._emit_forced_break("parbreak()")
# unconditionally, replacing the old cosmetic-only self.body.append("\n\n").

project = "Desc Bodyless Concat Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF.
typst_documents = [
    ("index", "index", "Desc Bodyless Concat Render Gate", "Test Author"),
]
