Target Label Render Gate
========================

This fixture reproduces the corpus fatal where two consecutive target nodes
emitted ``label("id1")label("id2")`` -- adjacent bare labels with no separator,
a Typst syntax error.

The two anonymous hyperlink targets below (``__ https://...``) create two
adjacent ``target`` nodes with auto-generated ids, exactly like the two that
close the ``.. tip::`` block in Sphinx's own ``usage/installation.rst``:

For local development, use `venv`__ or `conda`__ environments to keep separate
versions per project.

__ https://docs.python.org/3/library/venv.html
__ https://conda.io/projects/conda/en/latest/user-guide/getting-started.html

A paragraph immediately after the two anonymous targets, reproducing the
``]par(`` adjacency (an anchor directly followed by the next paragraph) that
also requires a separator.
