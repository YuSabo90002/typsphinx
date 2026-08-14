Output Layout
=============

This page explains the shape of the files a build actually writes to disk:
which files exist, which one you compile, and what happens if you compile
the other one.

Wrapper and Content Files
--------------------------

A build writes two kinds of ``.typ`` file.

One **wrapper** file is written per ``typst_documents`` entry, at that
entry's own target path. The wrapper carries the template application (the
title, author, and document-level styling) and one ``#include()`` of its
own content file.

One **content** file is written per docname, named after the docname. The
content file carries the document's body and no template application.
Every docname gets a content file unconditionally, whether or not that
docname appears in ``typst_documents`` -- a document reached only through a
toctree still gets its own content file, so it can be included by whichever
wrapper's chain of ``#include()`` calls eventually reaches it.

.. code-block:: python

   typst_documents = [
       ("index", "manual", "Title", "Author", "typst"),
   ]

This configuration writes two files: ``manual.typ`` at the output
directory's root -- the wrapper for the ``index`` docname's target
``manual`` -- and ``index.typ``, also at the output directory's root -- the
content file for the ``index`` docname itself.

Which File to Compile
~~~~~~~~~~~~~~~~~~~~~~

The wrapper is the file to compile. If you build with the ``typst``
builder, you don't need to work out which file that is by hand: the
builder's own log line names every wrapper file it wrote, for example
``typst: wrote 1 wrapper file(s) -- compile these: manual.typ``. Read the
wrapper names off that line.

Compiling a content file directly, on its own, also succeeds. It produces
only that document's own body: the documents it would otherwise have
pulled in are absent from the output, with no error and no warning at any
layer, because nothing published the wrapper's include set for a guarded
``#include()`` to read. This is normal, well-defined behaviour, not a
limitation -- a content file compiled on its own is simply a document with
no children rendered.

Where the Wrapper Is Written
------------------------------

A ``typst_documents`` entry's target controls exactly where its wrapper is
written. Two shapes are worth naming separately.

A bare target
~~~~~~~~~~~~~

A target with no path component -- like ``"manual"`` above -- writes the
wrapper at the output directory's own root, under that stem. This is the
example already shown in `Wrapper and Content Files`_: the wrapper lands at
``manual.typ``, directly under the output directory.

A path in the target
~~~~~~~~~~~~~~~~~~~~~

A target may also carry a path component, and that path is accepted and
honoured relative to the output directory.

.. code-block:: python

   typst_documents = [
       ("index", "manuals/guide.typ", "Title", "Author", "typst"),
   ]

This configuration writes the wrapper at ``manuals/guide.typ``, relative to
the output directory -- the path component is accepted and used exactly as
given. The content file is unaffected by where the wrapper landed: it still
writes to ``index.typ``, at the output directory's root, because a content
file's location is derived from its docname alone, never from any
``typst_documents`` target.
