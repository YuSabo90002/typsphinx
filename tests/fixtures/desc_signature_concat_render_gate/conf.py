"""Sphinx config for the desc-signature concat/newline render-gate fixture.

Reproduces GATE-02 corpus fatal #9 offline: a C-domain function signature whose
FIRST parameter leads with a cross-referenced type (``MyType *obj``). The type
xref must RESOLVE to a link so ``visit_reference`` fires inside the
``in_desc_parameter`` concat context. Same-document C targets resolve to a
``refid`` whose Typst label is never emitted (a separate, out-of-scope gap), so
this fixture routes the type through a tiny OFFLINE intersphinx inventory
instead: the xref resolves to an EXTERNAL URL (``link("https://.../MyType",
...)``), which needs no label and compiles cleanly -- isolating the concat bug.

The inventory is generated into the system temp dir (never committed alongside
the fixture) and referenced by absolute path, so the fixture stays text-only and
fully offline.
"""

import os
import tempfile
import zlib

# --- Generate a minimal offline intersphinx inventory (v2 format) ----------
# One c:type entry (``MyType``) resolving to an external URL. Written to the
# temp dir so no binary artifact lands in the repo.
_inv_path = os.path.join(
    tempfile.gettempdir(), "typsphinx_desc_signature_concat_objects.inv"
)
_inv_lines = b"MyType c:type 1 api.html#$ MyType\n"
_inv_header = (
    b"# Sphinx inventory version 2\n"
    b"# Project: extc\n"
    b"# Version: 1.0\n"
    b"# The remainder of this file is compressed using zlib.\n"
)
with open(_inv_path, "wb") as _f:
    _f.write(_inv_header + zlib.compress(_inv_lines))

project = "Desc Signature Concat Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["sphinx.ext.intersphinx", "typsphinx"]

# Absolute local path -> intersphinx reads it offline (no network).
intersphinx_mapping = {"extc": ("https://example.com/", _inv_path)}

typst_documents = [
    ("index", "index", "Desc Signature Concat Render Gate", "typsphinx tests"),
]
