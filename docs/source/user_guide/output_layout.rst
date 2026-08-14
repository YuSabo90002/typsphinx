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

This configuration writes three files, all at the output directory's root:
``manual.typ``, the wrapper for the ``index`` docname's target ``manual``;
``index.typ``, the content file for the ``index`` docname itself; and
``_template.typ``, which holds the template the wrapper imports. The
wrapper will not compile without it.

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

Targets that are refused
~~~~~~~~~~~~~~~~~~~~~~~~~

Not every path-bearing target is accepted. Three target shapes are refused:
a target with a ``..`` path segment (parent-directory traversal), an
absolute target, and a drive-qualified target such as a Windows drive
prefix (for example ``C:manual``). The drive-qualified check is a pure
string-shape test, so a Windows-shaped target is refused identically on
Linux and macOS -- it does not depend on which platform the build runs on.

A refused target does not stop the build. The build emits a warning, falls
back to the target's own basename, and writes the wrapper at the output
directory's root exactly as a bare target would; the build still succeeds.
For example, a target of ``"../escape"`` falls back to ``escape``, and a
target of ``"/abs/manual"`` or ``"C:manual"`` both fall back to ``manual``.

.. code-block:: text

   WARNING: a path is not supported in a typst_documents target name: '../escape' -- using 'escape' instead

The other two refused shapes emit the same warning, naming their own
target and fallback: ``/abs/manual`` falls back to ``manual``, and
``C:manual`` falls back to ``manual`` as well.

Targets That Stop the Build
-----------------------------

A path-shape refusal (above) still succeeds, with a fallback. A different
kind of target problem does not: when the output path a target resolves to
is already claimed by something else, the build raises an error instead of
falling back, and stops before writing anything.

A path can be claimed by any of three things: the reserved ``_template.typ``
file typsphinx writes for its own use, any document's own content file
(named after its docname, and written for every document whether or not it
appears in ``typst_documents``), or any other entry's own wrapper.

.. code-block:: python

   typst_documents = [
       ("index", "index.typ", "Title", "Author", "typst"),
   ]

This exact configuration built successfully in v0.7.x, and now stops the
build: the ``index`` entry's target, ``index.typ``, resolves onto the
``index`` document's own content file -- the same path two different things
now claim.

.. code-block:: text

   ExtensionError: typst: 1 output path collision(s): 'index.typ': the content file for docname 'index' and typst_documents entry 0 (docname 'index', target 'index.typ') both resolve to the same output path 'index.typ'

This check runs before any file is written, so a build that fails this way
leaves no ``.typ`` files behind at all -- not even ``_template.typ``. The
fix is to choose a target that is not any document's own name.

Documents Shared by Several Masters
------------------------------------

A document reached from more than one master appears in EVERY one of those
masters' outputs. It appears exactly once in each. It appears at that
master's own position in its own table of contents -- and because that
position differs per master, the document's heading level differs per
master too: the same shared chapter can be a second-level heading in one
master's output and a third-level heading in another's. This is the
intended behaviour, and no configuration is needed to get it.

This implies a file-count rule worth stating plainly, since it is what you
will actually observe when you build: a build writes one wrapper per
``typst_documents`` entry, one content file for every document in the
project, and -- unless you configure a Typst Universe package with
``typst_package`` and no ``typst_template`` -- the reserved
``_template.typ``. A three-master project over six documents therefore
writes ten ``.typ`` files; on the ``typst_package`` route it writes nine,
because the wrapper imports the package directly instead.

See Also
--------

- :doc:`configuration` - Configuration options
- :doc:`builders` - Understanding the typst and typstpdf builders
- :doc:`/changelog` - What changed from v0.7.x to v0.8.0
