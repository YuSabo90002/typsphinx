:orphan:

Orphan Whole-Document Target
=============================

ORPHAN_BODY_MARKER_TEXT

This document is marked orphan, so Sphinx excludes it from every toctree.
The compiled master never runs ``#include()`` on it, so a whole-document
reference to it must degrade to plain text rather than dangle post-fix.
