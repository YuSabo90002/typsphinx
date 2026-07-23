Chapter One
===========

A second, NON-master document. Its only job is to be written.

This file exists because of code-review finding CR-01 (Phase 22.3). It is
deliberately **not** listed in ``conf.py``'s ``typst_documents``, so writing it
forces ``TypstWriter._is_master_document("chapter1")`` to scan the whole
``typst_documents`` list without matching -- which means the loop reaches the
malformed ``()`` entry at the end of that list.

Before CR-01 was fixed, that unguarded ``doc_tuple[0]`` raised
``IndexError: tuple index out of range`` during the **write** phase, aborting
``sphinx-build`` with a raw traceback before ``TypstPDFBuilder.finish()`` ever
ran -- so no PDF was produced for ANY master, including the valid one. The
single-document version of this fixture could not catch that: ``index`` is
listed first in ``typst_documents``, so ``_is_master_document("index")``
returned on the first iteration and never reached the malformed entry.

Do not add this document to ``typst_documents``, and do not remove it from
``index.rst``'s toctree -- either change silently stops exercising the
regression.
